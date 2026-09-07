"""Route billing: pagina di upgrade (piani Pro via Revolut, link di
pagamento manuali), stato abbonamento, pacchetti crediti AI (acquisto
temporaneamente sospeso, vedi app/templates/billing/credits.html) e riscatto
codici AppSumo (lifetime, multi-tier — invariato).

Il pagamento Pro non passa più da qui: ogni CTA in /billing/upgrade è un
link statico verso un Revolut Business Payment Link (config
REVOLUT_PAYMENT_LINK_1M/3M/12M), aperto in una nuova scheda. Nessun checkout
interno, nessun webhook: dopo la notifica di pagamento via email, un admin
attiva/estende il piano da Flask-Admin (vedi
app/billing/revolut_manual_activation.py).

Restano sempre raggiungibili (vedi app/billing/access.py: "billing" non è tra
i blueprint gated) — è la via d'uscita per chi ha finito il trial."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.entitlements.limits import REVOLUT_PLAN_PRICES, REVOLUT_PLAN_SAVINGS_LABEL
from app.entitlements.service import get_plan_limits
from app.extensions import db
from app.models import AppSumoCode

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _revolut_plans():
    """Le tre card mostrate in /billing/upgrade. `link` è None se la env var
    corrispondente non è configurata — il template disabilita la CTA invece
    di puntare a un placeholder (vedi Fase 6 del piano di migrazione)."""
    return [
        {
            "plan": "revolut_1m",
            "label": _("1 month"),
            "price": REVOLUT_PLAN_PRICES["revolut_1m"],
            "savings_label": REVOLUT_PLAN_SAVINGS_LABEL["revolut_1m"],
            "link": current_app.config.get("REVOLUT_PAYMENT_LINK_1M") or None,
        },
        {
            "plan": "revolut_3m",
            "label": _("3 months"),
            "price": REVOLUT_PLAN_PRICES["revolut_3m"],
            "savings_label": REVOLUT_PLAN_SAVINGS_LABEL["revolut_3m"],
            "link": current_app.config.get("REVOLUT_PAYMENT_LINK_3M") or None,
        },
        {
            "plan": "revolut_12m",
            "label": _("12 months"),
            "price": REVOLUT_PLAN_PRICES["revolut_12m"],
            "savings_label": REVOLUT_PLAN_SAVINGS_LABEL["revolut_12m"],
            "link": current_app.config.get("REVOLUT_PAYMENT_LINK_12M") or None,
        },
    ]


@billing_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("billing/upgrade.html", plans=_revolut_plans())


@billing_bp.route("/subscription")
@login_required
def subscription():
    limits = get_plan_limits(current_user)
    return render_template(
        "billing/subscription.html",
        limits=limits,
        plan_name=limits.name,
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
            from datetime import datetime, timezone

            code.redeemed_at = datetime.now(timezone.utc)
            code.redeemed_by_user_id = current_user.id
            current_user.subscription_status = "lifetime"
            current_user.plan_type = f"appsumo_tier{code.tier}"
            db.session.commit()
            flash(_("Code redeemed: your account is now lifetime."), "success")
            return redirect(url_for("dashboard.overview"))
    return render_template("billing/redeem.html")
