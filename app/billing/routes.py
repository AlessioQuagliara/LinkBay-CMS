"""Route billing: pagina di upgrade, stato abbonamento, Lemon Squeezy
Checkout, webhook, customer portal, e riscatto codici AppSumo (lifetime).

Restano sempre raggiungibili (vedi app/billing/access.py: "billing" non è tra
i blueprint gated) — è la via d'uscita per chi ha finito il trial."""
from datetime import datetime, timezone

import requests
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.billing import lemonsqueezy_client as ls
from app.extensions import csrf, db
from app.models import AppSumoCode, User

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _price_label():
    # Valutata a request-time (non a import-time) così "/month" viene
    # tradotto nella lingua corrente invece di restare fissa in inglese.
    return _("€79/month")


@billing_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("billing/upgrade.html", price_label=_price_label())


@billing_bp.route("/subscription")
@login_required
def subscription():
    return render_template("billing/subscription.html", price_label=_price_label())


@billing_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    try:
        url = ls.create_checkout_url(current_user)
    except requests.RequestException:
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
        else:
            code.redeemed_at = datetime.now(timezone.utc)
            code.redeemed_by_user_id = current_user.id
            current_user.subscription_status = "lifetime"
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

    return "", 200


def _map_status(ls_status):
    return "active" if ls_status in ("active", "on_trial") else "canceled"


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
    db.session.commit()


def _sync_subscription_status(data):
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    user.subscription_status = _map_status(data.get("attributes", {}).get("status"))
    db.session.commit()


def _cancel_subscription(data):
    user = User.query.filter_by(ls_subscription_id=str(data.get("id"))).first()
    if not user:
        return
    user.subscription_status = "canceled"
    db.session.commit()
