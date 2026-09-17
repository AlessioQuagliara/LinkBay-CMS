"""Checkout server-driven per Paddle Billing — estende `billing_bp` (import
in fondo a app/billing/routes.py) invece di un blueprint separato, stesso
url_prefix "/billing" delle route Revolut/AppSumo già esistenti lì.

Ogni route qui costruisce la transazione Paddle SOLO da una whitelist
server-side (app/billing/paddle_products.py) — il client sceglie al massimo
una chiave interna ("plan" o "credit_package"), mai un price_id, un importo
o una valuta. L'accesso/i crediti non vengono MAI concessi da queste route:
solo il webhook verificato (app/webhooks/routes.py) può farlo — qui si crea
solo la transazione e si reindirizza a Paddle."""
from __future__ import annotations

import secrets

from flask import current_app, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app.billing.paddle_client import (
    PaddleAPIError,
    PaddleConfigError,
    create_customer_portal_session,
    create_transaction,
    get_environment,
)
from app.billing.paddle_products import PADDLE_CREDIT_PACKAGES, PADDLE_SUBSCRIPTION_PLANS, resolve_price_id
from app.billing.routes import billing_bp
from app.entitlements.service import get_plan_limits, has_active_entitlement
from app.extensions import db
from app.models import PaddleTransaction


def _param(name: str) -> str | None:
    # Il frontend usa Common.postForm (form-encoded, stesso pattern già in
    # uso in tutta la dashboard — vedi app/static/js/common.js): supportiamo
    # anche un body JSON per chi chiama l'API direttamente, senza inventare
    # un secondo contratto — stessa chiave, stesso significato.
    value = request.form.get(name)
    if value:
        return value
    json_body = request.get_json(silent=True) or {}
    value = json_body.get(name)
    return value.strip() if isinstance(value, str) else value


def _success_url() -> str:
    return current_app.config.get("PADDLE_SUCCESS_URL") or url_for("billing.paddle_pending", _external=True)


@billing_bp.route("/checkout/subscription", methods=["POST"])
@login_required
def paddle_checkout_subscription():
    plan = _param("plan")
    if plan not in PADDLE_SUBSCRIPTION_PLANS:
        return jsonify(error="invalid_plan"), 400

    if current_user.subscription_status == "lifetime":
        return jsonify(error="lifetime_account", message="This account is on an AppSumo lifetime plan."), 409

    if (
        current_user.subscription_source == "paddle"
        and current_user.paddle_subscription_id
        and current_user.subscription_status in ("active", "trialing", "past_due")
    ):
        return jsonify(
            error="already_subscribed",
            message="You already have an active Paddle subscription — use the customer portal to change it.",
        ), 409

    price_id = resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, plan)
    if not price_id:
        return jsonify(error="not_configured", message="This plan isn't available yet."), 503

    correlation_id = secrets.token_urlsafe(16)
    custom_data = {
        "local_user_id": current_user.id,
        "purchase_type": "subscription",
        "internal_plan_key": plan,
        "correlation_id": correlation_id,
        "environment": get_environment(),
    }

    try:
        response = create_transaction(
            items=[{"price_id": price_id, "quantity": 1}],
            custom_data=custom_data,
            customer_email=current_user.email,
            success_url=_success_url(),
        )
    except PaddleConfigError:
        current_app.logger.error("Checkout Paddle non disponibile: configurazione mancante.")
        return jsonify(error="not_configured"), 503
    except PaddleAPIError:
        current_app.logger.exception("Creazione transazione Paddle (subscription) fallita per user %s.", current_user.id)
        return jsonify(error="paddle_unavailable"), 502

    tx_data = response.get("data") or response
    transaction_id = tx_data.get("id")
    checkout_url = (tx_data.get("checkout") or {}).get("url")
    if not transaction_id or not checkout_url:
        current_app.logger.error("Risposta Paddle senza transaction id/checkout url per user %s.", current_user.id)
        return jsonify(error="paddle_unavailable"), 502

    db.session.add(
        PaddleTransaction(
            environment=get_environment(),
            paddle_transaction_id=transaction_id,
            user_id=current_user.id,
            purchase_type="subscription",
            internal_plan_key=plan,
            paddle_price_id=price_id,
            correlation_id=correlation_id,
            status="pending",
        )
    )
    db.session.commit()

    return jsonify(checkout_url=checkout_url, transaction_id=transaction_id), 201


@billing_bp.route("/checkout/credits", methods=["POST"])
@login_required
def paddle_checkout_credits():
    credit_package = _param("credit_package")
    if credit_package not in PADDLE_CREDIT_PACKAGES:
        return jsonify(error="invalid_package"), 400

    if not get_plan_limits(current_user).ai_credit_topups_allowed:
        return jsonify(error="not_eligible", message="Your plan isn't eligible for AI credit top-ups."), 403

    price_id = resolve_price_id(PADDLE_CREDIT_PACKAGES, credit_package)
    if not price_id:
        return jsonify(error="not_configured", message="This package isn't available yet."), 503

    correlation_id = secrets.token_urlsafe(16)
    custom_data = {
        "local_user_id": current_user.id,
        "purchase_type": "ai_credits",
        "internal_plan_key": credit_package,
        "correlation_id": correlation_id,
        "environment": get_environment(),
    }

    try:
        response = create_transaction(
            items=[{"price_id": price_id, "quantity": 1}],
            custom_data=custom_data,
            customer_email=current_user.email,
            success_url=_success_url(),
        )
    except PaddleConfigError:
        current_app.logger.error("Checkout Paddle non disponibile: configurazione mancante.")
        return jsonify(error="not_configured"), 503
    except PaddleAPIError:
        current_app.logger.exception("Creazione transazione Paddle (credits) fallita per user %s.", current_user.id)
        return jsonify(error="paddle_unavailable"), 502

    tx_data = response.get("data") or response
    transaction_id = tx_data.get("id")
    checkout_url = (tx_data.get("checkout") or {}).get("url")
    if not transaction_id or not checkout_url:
        current_app.logger.error("Risposta Paddle senza transaction id/checkout url per user %s.", current_user.id)
        return jsonify(error="paddle_unavailable"), 502

    db.session.add(
        PaddleTransaction(
            environment=get_environment(),
            paddle_transaction_id=transaction_id,
            user_id=current_user.id,
            purchase_type="ai_credits",
            internal_plan_key=credit_package,
            paddle_price_id=price_id,
            correlation_id=correlation_id,
            status="pending",
        )
    )
    db.session.commit()

    return jsonify(checkout_url=checkout_url, transaction_id=transaction_id), 201


@billing_bp.route("/status")
@login_required
def paddle_status():
    """Stato di billing dell'utente, letto SOLO dal DB locale (mai da una
    chiamata sincrona a Paddle) — usato dalla pagina "pagamento in
    elaborazione" (paddle_pending, sotto) per fare polling finché il webhook
    non ha applicato lo stato, invece di fidarsi del ritorno client-side dal
    checkout."""
    user = current_user

    def _iso(dt):
        return dt.isoformat() if dt else None

    return jsonify(
        subscription_status=user.subscription_status,
        plan_type=user.plan_type,
        billing_provider=user.subscription_source,
        current_period_ends_at=_iso(user.current_period_ends_at),
        access_expires_at=_iso(user.subscription_expires_at),
        cancel_at_period_end=bool(user.cancel_at_period_end),
        has_active_access=has_active_entitlement(user),
        last_paddle_sync_at=_iso(user.last_paddle_sync_at),
    )


@billing_bp.route("/customer-portal", methods=["POST"])
@login_required
def paddle_customer_portal():
    if not current_user.paddle_customer_id:
        return jsonify(error="no_paddle_customer", message="No Paddle subscription linked to this account yet."), 404

    try:
        response = create_customer_portal_session(current_user.paddle_customer_id)
    except PaddleConfigError:
        return jsonify(error="not_configured"), 503
    except PaddleAPIError:
        current_app.logger.exception("Creazione customer portal session fallita per user %s.", current_user.id)
        return jsonify(error="paddle_unavailable"), 502

    urls = ((response.get("data") or {}).get("urls") or {}).get("general") or {}
    portal_url = urls.get("overview")
    if not portal_url:
        return jsonify(error="paddle_unavailable"), 502

    return jsonify(portal_url=portal_url)


@billing_bp.route("/paddle/pending")
@login_required
def paddle_pending():
    """Pagina di ritorno dopo il checkout Paddle (PADDLE_SUCCESS_URL di
    default punta qui) — NON legge mai `checkout.completed` come prova di
    pagamento: mostra uno stato "in elaborazione" e fa polling su
    /billing/status finché il webhook non ha confermato (vedi
    app/static/js/paddle-checkout.js)."""
    return render_template("billing/paddle_pending.html")
