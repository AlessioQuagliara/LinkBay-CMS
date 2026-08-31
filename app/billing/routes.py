"""Route billing: pagina di upgrade, stato abbonamento, Lemon Squeezy
Checkout (piani Pro + pacchetti crediti AI), webhook, customer portal, e
riscatto codici AppSumo (lifetime, multi-tier).

Restano sempre raggiungibili (vedi app/billing/access.py: "billing" non è tra
i blueprint gated) — è la via d'uscita per chi ha finito il trial."""
from datetime import datetime, timedelta, timezone

import requests
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.billing import lemonsqueezy_client as ls
from app.billing.products import PRODUCT_CATALOG, product_key_for_variant
from app.entitlements.ai_credits import adjust_credits, grant_credits
from app.entitlements.limits import PLAN_LIMITS
from app.entitlements.service import get_plan_limits
from app.extensions import csrf, db
from app.models import AiCreditTransaction, AppSumoCode, User

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")

# Periodo di grazia dopo un pagamento fallito (subscription_payment_failed)
# prima che l'accesso venga bloccato — vedi User.has_active_access.
GRACE_PERIOD_DAYS = 7


def _price_label(product_key="pro_monthly"):
    # Valutata a request-time (non a import-time) così viene tradotta nella
    # lingua corrente invece di restare fissa in inglese.
    return {
        "pro_monthly": _("€79/month"),
        "pro_annual": _("€790/year"),
    }.get(product_key, _("€79/month"))


@billing_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template(
        "billing/upgrade.html",
        price_label=_price_label("pro_monthly"),
        price_label_annual=_price_label("pro_annual"),
    )


@billing_bp.route("/subscription")
@login_required
def subscription():
    product_key = "pro_annual" if current_user.billing_interval == "annual" else "pro_monthly"
    return render_template(
        "billing/subscription.html",
        price_label=_price_label(product_key),
        limits=get_plan_limits(current_user),
    )


@billing_bp.route("/credits")
@login_required
def credits():
    from app.entitlements.limits import AI_CREDIT_PACKS

    # Pacchetti one-time riservati ai piani AppSumo (la scheda tecnica li
    # esclude esplicitamente per Pro: la quota mensile inclusa è già
    # generosa) — un utente Pro che arriva qui viene rimandato al suo piano
    # invece di vedere un carrello che non può usare.
    if not get_plan_limits(current_user).ai_credit_topups_allowed:
        flash(_("Your plan already includes a generous monthly AI quota — extra credit packs aren't needed."), "info")
        return redirect(url_for("billing.subscription"))

    packs = [
        {"product_key": f"credits_{amount}", "amount": amount, "price": price}
        for amount, price in sorted(AI_CREDIT_PACKS.items())
    ]
    return render_template("billing/credits.html", packs=packs)


def _is_appsumo(user) -> bool:
    return bool(user.plan_type) and user.plan_type.startswith("appsumo")


@billing_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    product_key = request.form.get("product_key", "pro_monthly")
    if product_key not in PRODUCT_CATALOG:
        flash(_("We couldn't start checkout. Please try again shortly."), "error")
        return redirect(url_for("billing.upgrade"))

    # Un utente AppSumo non passa a un piano Pro da qui: è una migrazione
    # controllata (vedi User.appsumo_migration_unlocked, sbloccabile solo dal
    # supporto via Flask-Admin) — nessuna chiamata a Lemon Squeezy in questo
    # caso, blocco netto con spiegazione. I pacchetti crediti restano invece
    # sempre acquistabili da un utente AppSumo (è il loro upsell naturale).
    kind = PRODUCT_CATALOG[product_key]["kind"]
    if kind == "plan" and _is_appsumo(current_user) and not current_user.appsumo_migration_unlocked:
        flash(_("AppSumo lifetime accounts can't switch to a monthly/annual plan directly. Contact support to migrate your account."), "error")
        return redirect(url_for("billing.subscription"))
    if kind == "credits" and not get_plan_limits(current_user).ai_credit_topups_allowed:
        flash(_("Your plan already includes a generous monthly AI quota — extra credit packs aren't needed."), "info")
        return redirect(url_for("billing.subscription"))

    try:
        url = ls.create_checkout_url(current_user, product_key)
    except (requests.RequestException, ValueError):
        current_app.logger.exception("Creazione Lemon Squeezy checkout fallita per user %s", current_user.id)
        flash(_("We couldn't start checkout. Please try again shortly."), "error")
        return redirect(url_for("billing.upgrade"))
    return redirect(url)


@billing_bp.route("/success")
@login_required
def success():
    return render_template("billing/success.html")


@billing_bp.route("/portal")
@login_required
def portal():
    if not current_user.ls_subscription_id:
        return redirect(url_for("billing.upgrade"))
    try:
        url = ls.get_customer_portal_url(current_user.ls_subscription_id)
    except requests.RequestException:
        current_app.logger.exception("Recupero Lemon Squeezy customer portal fallito per user %s", current_user.id)
        flash(_("We couldn't open subscription management. Please try again shortly."), "error")
        return redirect(url_for("billing.upgrade"))
    return redirect(url)


@billing_bp.route("/redeem", methods=["GET", "POST"])
@login_required
def redeem():
    if request.method == "POST":
        raw_code = (request.form.get("code") or "").strip().upper()
        code = AppSumoCode.query.filter_by(code=raw_code).first()
        if not code:
            flash(_("Invalid code."), "error")
        elif code.is_redeemed:
            flash(_("This code has already been used."), "error")
        elif code.tier is None:
            # Dato storico incompleto (codice importato prima dei tier
            # multipli, mai corretto a mano) — non redimibile finché
            # qualcuno non gli assegna un tier, vedi flask import-appsumo-codes.
            current_app.logger.warning("Tentativo di riscatto codice AppSumo senza tier: %s", raw_code)
            flash(_("This code isn't ready yet. Please contact support."), "error")
        else:
            code.redeemed_at = datetime.now(timezone.utc)
            code.redeemed_by_user_id = current_user.id
            current_user.subscription_status = "lifetime"
            current_user.plan_type = f"appsumo_tier{code.tier}"
            db.session.commit()
            flash(_("Code redeemed: your account is now lifetime."), "success")
            return redirect(url_for("dashboard.overview"))
    return render_template("billing/redeem.html")


@billing_bp.route("/webhook", methods=["POST"])
@csrf.exempt
def webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Signature", "")
    if not ls.verify_webhook_signature(payload, signature):
        current_app.logger.warning("Webhook Lemon Squeezy con firma non valida.")
        return "", 400

    event = request.get_json(silent=True) or {}
    meta = event.get("meta") or {}
    event_name = meta.get("event_name")
    data = event.get("data") or {}
    custom_data = meta.get("custom_data") or {}

    if event_name == "subscription_created":
        _activate_subscription(data, custom_data)
    elif event_name in ("subscription_updated", "subscription_resumed"):
        _sync_subscription_status(data)
    elif event_name in ("subscription_cancelled", "subscription_expired"):
        _cancel_subscription(data)
    elif event_name == "subscription_payment_success":
        _handle_payment_success(data)
    elif event_name == "subscription_payment_failed":
        _handle_payment_failed(data)
    elif event_name == "subscription_plan_changed":
        _handle_plan_changed(data)
    elif event_name == "order_created":
        _handle_order_created(data, custom_data)
    elif event_name == "order_refunded":
        _handle_order_refunded(data)
    else:
        current_app.logger.info("Webhook Lemon Squeezy ignorato: %s", event_name)

    return "", 200


def _map_status(ls_status):
    if ls_status in ("active", "on_trial"):
        return "active"
    if ls_status in ("past_due", "unpaid", "paused"):
        return "past_due"
    return "canceled"


def _apply_plan_from_variant(user, variant_id):
    """Deriva plan_type/billing_interval dalla variante Lemon Squeezy —
    dual-write accanto a subscription_status, mai in sostituzione: se il
    variant_id non è (ancora) mappato in PRODUCT_CATALOG (es. store
    configurato solo in parte), lascia il plan_type esistente invariato
    invece di azzerarlo per errore."""
    product_key = product_key_for_variant(variant_id)
    if not product_key:
        current_app.logger.warning("Variant Lemon Squeezy %s non mappato in PRODUCT_CATALOG.", variant_id)
        return
    entry = PRODUCT_CATALOG.get(product_key)
    if not entry or entry["kind"] != "plan":
        return
    user.plan_type = entry["plan_type"]
    user.billing_interval = entry["billing_interval"]


def _activate_subscription(data, custom_data):
    user_id = custom_data.get("user_id")
    if not user_id:
        current_app.logger.warning("subscription_created senza user_id in custom_data.")
        return
    user = db.session.get(User, int(user_id))
    if not user:
        current_app.logger.warning("subscription_created per user_id %s inesistente.", user_id)
        return
    attrs = data.get("attributes", {})
    user.ls_customer_id = str(attrs.get("customer_id"))
    user.ls_subscription_id = str(data.get("id"))
    user.subscription_status = _map_status(attrs.get("status"))
    user.grace_period_ends_at = None
    _apply_plan_from_variant(user, attrs.get("variant_id"))
    db.session.commit()


def _sync_subscription_status(data):
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    attrs = data.get("attributes", {})
    user.subscription_status = _map_status(attrs.get("status"))
    if user.subscription_status == "active":
        user.grace_period_ends_at = None
    _apply_plan_from_variant(user, attrs.get("variant_id"))
    db.session.commit()


def _cancel_subscription(data):
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    user.subscription_status = "canceled"
    user.grace_period_ends_at = None
    db.session.commit()


def _handle_payment_success(data):
    """Rinnovo riuscito: chiude un eventuale periodo di grazia in corso e
    accredita la quota AI mensile del piano (per i piani ai_mode=="credit";
    i piani a cooldown non hanno una quota da accreditare)."""
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    user.subscription_status = "active"
    user.grace_period_ends_at = None
    db.session.commit()

    limits = PLAN_LIMITS.get(user.plan_type)
    if limits and limits.ai_mode == "credit" and limits.ai_credit_grant > 0:
        grant_credits(user, limits.ai_credit_grant, type="grant_monthly_quota")


def _handle_payment_failed(data):
    """Pagamento fallito: NON blocca subito — periodo di grazia di
    GRACE_PERIOD_DAYS prima che has_active_access torni False (vedi
    app/models/user.py). È la modifica a più alto rischio del piano
    multi-tier: tocca direttamente il gate di accesso pagante."""
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    user.subscription_status = "past_due"
    user.grace_period_ends_at = datetime.now(timezone.utc) + timedelta(days=GRACE_PERIOD_DAYS)
    db.session.commit()


def _handle_plan_changed(data):
    """Cambio variante su un abbonamento esistente (es. mensile -> annuale) —
    stesso ls_subscription_id, variant_id diverso."""
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    attrs = data.get("attributes", {})
    _apply_plan_from_variant(user, attrs.get("variant_id"))
    db.session.commit()


def _handle_order_created(data, custom_data):
    """Acquisto one-time — oggi solo i pacchetti crediti AI passano da qui
    (i piani Pro sono ricorrenti, gestiti da subscription_created). Un
    order_created per un product_key sconosciuto o di tipo "plan" viene
    ignorato: non dovrebbe succedere dato come create_checkout_url imposta
    custom_data, ma non è motivo per far fallire il webhook."""
    user_id = custom_data.get("user_id")
    product_key = custom_data.get("product_key")
    if not user_id or not product_key:
        current_app.logger.warning("order_created senza user_id/product_key in custom_data.")
        return
    user = db.session.get(User, int(user_id))
    if not user:
        current_app.logger.warning("order_created per user_id %s inesistente.", user_id)
        return
    entry = PRODUCT_CATALOG.get(product_key)
    if not entry or entry["kind"] != "credits":
        return

    ls_order_id = str(data.get("id"))
    # Idempotenza: Lemon Squeezy può ri-consegnare lo stesso webhook più
    # volte (retry su timeout) — non accreditare due volte lo stesso ordine.
    already_granted = AiCreditTransaction.query.filter_by(
        ls_order_id=ls_order_id, type="grant_purchase"
    ).first()
    if already_granted:
        return

    grant_credits(user, entry["amount"], type="grant_purchase", ls_order_id=ls_order_id)


def _handle_order_refunded(data):
    """Storna i crediti di un ordine rimborsato. Se l'utente li ha già
    consumati parzialmente, il saldo può finire negativo — è un segnale per
    il supporto (vedi adjust_credits), non un caso bloccato: il rimborso va
    comunque registrato."""
    ls_order_id = str(data.get("id"))
    original = AiCreditTransaction.query.filter_by(
        ls_order_id=ls_order_id, type="grant_purchase"
    ).first()
    if not original:
        return
    already_refunded = AiCreditTransaction.query.filter_by(
        ls_order_id=ls_order_id, type="adjustment"
    ).first()
    if already_refunded:
        return

    user = db.session.get(User, original.user_id)
    if not user:
        return
    adjust_credits(user, -original.amount, ls_order_id=ls_order_id)
