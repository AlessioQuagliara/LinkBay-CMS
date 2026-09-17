"""Route billing: pagina di upgrade (piani Pro via Revolut, link di
pagamento manuali), stato abbonamento, pacchetti crediti AI (idem, vendita
una tantum) e riscatto codici AppSumo (lifetime, multi-tier — invariato).

Nessun pagamento passa più da qui: ogni CTA in /billing/upgrade e
/billing/credits è un link statico verso un Revolut Business Payment Link
(catalogo in app/billing/revolut_products.py), aperto in una nuova scheda.
Nessun checkout interno, nessun webhook: dopo la notifica di pagamento via
email, un admin attiva/estende il piano o accredita il top-up da Flask-Admin
(vedi app/billing/revolut_manual_activation.py e
app/billing/revolut_ai_topup.py).

Restano sempre raggiungibili (vedi app/billing/access.py: "billing" non è tra
i blueprint gated) — è la via d'uscita per chi ha finito il trial."""
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.billing.paddle_products import paddle_credit_packages, paddle_pro_plans
from app.billing.revolut_products import ai_topup_packages, revolut_pro_plans
from app.entitlements.service import get_ai_credit_overview, get_plan_limits
from app.extensions import db
from app.models import AiCreditTransaction, AppSumoCode

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")

CREDITS_PAGE_SIZE = 20


@billing_bp.route("/upgrade")
@login_required
def upgrade():
    # Stessa durata (1/3/12 mesi), due processori — costruiamo un'unica
    # lista di card con entrambe le opzioni di pagamento invece di far
    # ricostruire l'abbinamento al template. Entrambe le funzioni sorgente
    # iterano lo stesso ordine di durata (1m, 3m, 12m), quindi lo zip
    # allinea correttamente per indice senza bisogno di una chiave comune.
    plans = [
        {**revolut_plan, "paddle": paddle_plan}
        for revolut_plan, paddle_plan in zip(revolut_pro_plans(), paddle_pro_plans())
    ]
    return render_template("billing/upgrade.html", plans=plans)


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
    # Piani ai_mode != "credit" (oggi solo trial, cooldown-based) non hanno
    # alcun ledger da mostrare: via diretta invece di una pagina vuota. I
    # pacchetti di acquisto restano riservati agli AppSumo (vedi
    # ai_credit_topups_allowed nel template) — un piano Pro/Revolut arriva
    # comunque qui per vedere saldo/storico, solo senza le card di acquisto.
    if get_plan_limits(current_user).ai_mode != "credit":
        flash(_("Your plan doesn't use AI credits."), "info")
        return redirect(url_for("billing.subscription"))

    page = request.args.get("page", 1, type=int)
    transactions = (
        AiCreditTransaction.query.filter_by(user_id=current_user.id)
        .order_by(AiCreditTransaction.created_at.desc())
        .paginate(page=page, per_page=CREDITS_PAGE_SIZE, error_out=False)
    )

    # Stesso abbinamento per indice di upgrade() sopra: stesso ordine
    # (starter, growth, scale) in entrambe le funzioni sorgente.
    packs = [
        {**revolut_pack, "paddle": paddle_pack}
        for revolut_pack, paddle_pack in zip(ai_topup_packages(), paddle_credit_packages())
    ]

    return render_template(
        "billing/credits.html",
        packs=packs,
        ai_credits=get_ai_credit_overview(current_user),
        transactions=transactions,
    )


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


# Import in fondo al modulo (non in cima): app/billing/paddle_routes.py importa
# `billing_bp` da QUESTO stesso modulo per aggiungere le route di checkout
# Paddle allo stesso blueprint — un import in cima creerebbe un ciclo
# (paddle_routes non sarebbe ancora eseguibile prima che billing_bp esista).
# Side-effect import: registra le route via i decoratori @billing_bp.route,
# non serve altro dal modulo.
from app.billing import paddle_routes  # noqa: E402,F401
