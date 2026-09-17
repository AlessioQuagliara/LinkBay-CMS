from flask import abort, flash, redirect, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.billing.revolut_ai_topup import RevolutAiTopupError, credit_revolut_ai_topup
from app.billing.revolut_manual_activation import (
    REVOLUT_PLAN_DAYS,
    RevolutActivationError,
    activate_revolut_subscription,
)
from app.billing.revolut_products import AI_TOPUP_CATALOG
from app.entitlements.service import get_plan_limits
from app.extensions import AdminAuthMixin, db
from app.models import User


class SecureModelView(AdminAuthMixin, ModelView):
    """Base per le viste Flask-Admin: dentro solo al team (`User.is_admin`)."""


def _format_revolut_action(view, context, model, name):
    """Colonna virtuale (non un campo del modello) in UserAdminView: un
    link verso il form "Attiva abbonamento Revolut" per l'utente della riga,
    o un badge inerte per gli account AppSumo lifetime (l'attivazione
    Revolut è bloccata anche server-side dal service, questo è solo per non
    mostrare un'azione che fallirebbe sempre)."""
    if model.subscription_status == "lifetime":
        return Markup('<span class="badge badge-secondary">AppSumo lifetime</span>')
    return Markup(
        '<a class="btn btn-xs btn-primary" href="{url}">Activate Revolut plan</a>'
    ).format(url=url_for("revolut-activation.activate", user_id=model.id))


def _format_ai_topup_action(view, context, model, name):
    """Colonna virtuale gemella di _format_revolut_action, per il secondo
    flusso Revolut (top-up crediti AI — vendita una tantum, non tocca il
    piano). Visibile solo per gli utenti eleggibili (stessa regola di
    /billing/credits: get_plan_limits(user).ai_credit_topups_allowed, oggi
    solo i tier AppSumo) — un link che fallirebbe sempre non serve a
    nessuno."""
    if not get_plan_limits(model).ai_credit_topups_allowed:
        return Markup('<span class="text-muted">Not eligible</span>')
    return Markup(
        '<a class="btn btn-xs btn-outline-primary" href="{url}">Credit AI top-up</a>'
    ).format(url=url_for("revolut-ai-topup.credit", user_id=model.id))


class UserAdminView(SecureModelView):
    # Niente "Create" qui: User.password_hash è NOT NULL e questo form non
    # raccoglie una password, quindi un insert fallirebbe sempre con un
    # integrity error. Gli utenti si creano solo da /auth/register; qui si
    # gestiscono solo anagrafica, il flag is_admin, e gli escape hatch del
    # sistema di licensing (migrazione AppSumo→Pro, white label).
    can_create = False
    column_list = (
        "id", "name", "email", "is_admin", "plan_type", "subscription_status",
        "subscription_expires_at", "subscription_source",
        "paddle_customer_id", "paddle_subscription_id", "cancel_at_period_end",
        "ai_credit_balance", "heavy_user_flag", "created_at",
        "revolut_action", "ai_topup_action",
    )
    # appsumo_migration_unlocked e white_label_enabled sono editabili solo da
    # qui (nessun bottone self-service nell'app) — vedi
    # app/billing/routes.py::redeem(). Le due azioni Revolut (attivazione
    # abbonamento, top-up crediti AI) NON sono nella form (vedi colonne
    # virtuali "revolut_action"/"ai_topup_action" sotto): richiedono un
    # calcolo/validazione server-side che una form CRUD generica non fa,
    # quindi vivono in view dedicate (RevolutActivationView,
    # RevolutAiTopupView). heavy_user_flag NON è nella form: è calcolato dal
    # job settimanale flask flag-heavy-users, non va corretto a mano (si
    # autocorregge al giro successivo).
    #
    # paddle_customer_id/paddle_subscription_id SONO editabili qui — a
    # differenza degli altri campi Paddle (scritti solo dal webhook, vedi
    # app/billing/paddle_subscriptions.py), questi due sono l'escape hatch
    # per l'associazione manuale richiesta dalla Fase 7 del piano di
    # migrazione: un admin può collegare a mano un customer/subscription
    # Paddle già esistente a un utente locale (es. per correggere un
    # custom_data perso) prima che arrivi/venga riconciliato il prossimo
    # evento — vedi anche `flask paddle-reconcile`.
    form_columns = (
        "name", "email", "is_admin", "plan_type", "appsumo_migration_unlocked", "white_label_enabled",
        "paddle_customer_id", "paddle_subscription_id",
    )
    column_searchable_list = ("name", "email", "paddle_customer_id", "paddle_subscription_id")
    column_filters = ("plan_type", "subscription_status", "subscription_source", "heavy_user_flag")
    column_default_sort = ("created_at", True)
    column_formatters = {
        "revolut_action": _format_revolut_action,
        "ai_topup_action": _format_ai_topup_action,
    }


class AiCreditTransactionAdminView(SecureModelView):
    """Sola lettura: il ledger crediti si scrive solo tramite
    app/entitlements/ai_credits.py (consumo AI, job mensile, top-up manuale
    Revolut — vedi app/billing/revolut_ai_topup.py) — mai a mano, altrimenti
    balance_after perde di significato. ls_order_id resta per l'audit storico
    Lemon Squeezy; payment_reference/payment_source coprono il flusso Revolut
    attuale — le due coppie di colonne non si sovrappongono mai sulla stessa
    riga."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = (
        "id", "user", "type", "product_key", "amount", "balance_before", "balance_after",
        "payment_reference", "payment_source", "approved_by", "ls_order_id", "site_url", "created_at",
    )
    column_searchable_list = ("ls_order_id", "payment_reference")
    column_filters = ("type", "payment_source", "product_key")
    column_default_sort = ("created_at", True)


class ResourceUsageLogAdminView(SecureModelView):
    """Sola lettura: audit trail scritto da app/entitlements/service.py::record_usage,
    mai a mano."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ("id", "user", "action", "site_url", "counted_against_limit", "credits_consumed", "created_at")
    column_filters = ("action", "counted_against_limit")
    column_default_sort = ("created_at", True)


class PaddleWebhookEventAdminView(SecureModelView):
    """Sola lettura: audit/idempotenza degli eventi webhook Paddle (vedi
    app/webhooks/routes.py) — mai scritta a mano. Prima fonte da consultare
    quando un utente segnala "ho pagato ma non vedo l'accesso attivo": un
    evento assente qui vuol dire che Paddle non ha (ancora) consegnato il
    webhook, un evento "ignored" vuol dire che è arrivato ma non è stato
    applicato (vedi error_message)."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = (
        "id", "event_type", "status", "environment", "event_id",
        "paddle_subscription_id", "paddle_transaction_id", "error_message", "occurred_at", "created_at",
    )
    column_searchable_list = ("event_id", "paddle_subscription_id", "paddle_transaction_id", "paddle_customer_id")
    column_filters = ("event_type", "status", "environment")
    column_default_sort = ("created_at", True)


class PaddleTransactionAdminView(SecureModelView):
    """Sola lettura: ledger di riconciliazione Paddle (vedi
    app/billing/paddle_transactions.py) — creata al checkout, chiusa dal
    webhook. Per gli acquisti di crediti AI l'accredito vero è comunque in
    AI Credit Ledger (AiCreditTransactionAdminView, payment_source="paddle")
    — questa vista è il lato "cosa ha detto Paddle", quella è il lato
    "cosa abbiamo effettivamente accreditato"."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = (
        "id", "user", "purchase_type", "internal_plan_key", "status", "environment",
        "credits_granted", "paddle_transaction_id", "paddle_subscription_id", "amount", "currency",
        "completed_at", "created_at",
    )
    column_searchable_list = ("paddle_transaction_id", "paddle_subscription_id", "paddle_customer_id", "correlation_id")
    column_filters = ("purchase_type", "status", "environment")
    column_default_sort = ("created_at", True)


class RevolutActivationForm(FlaskForm):
    """Form server-side per "Attiva abbonamento Revolut" (vedi
    app/billing/revolut_manual_activation.py). Il client NON può inviare una
    scadenza: solo il piano (durata fissa) — la nuova scadenza è sempre
    calcolata dal service, mai accettata dal form."""

    plan = SelectField(
        "Plan",
        choices=[
            ("revolut_1m", "1 month (30 days)"),
            ("revolut_3m", "3 months (90 days)"),
            ("revolut_12m", "12 months (365 days)"),
        ],
        validators=[],
    )
    payment_reference = StringField(
        "Revolut payment reference (optional but recommended)",
        validators=[Optional(), Length(max=255)],
    )
    note = TextAreaField("Admin note (optional)", validators=[Optional(), Length(max=1000)])


class RevolutActivationView(AdminAuthMixin, BaseView):
    """View Flask-Admin dedicata (non un'azione bulk): serve un form con
    scelta del piano + riepilogo scadenza attuale/nuova, che le bulk actions
    di Flask-Admin non supportano bene. Riusa AdminAuthMixin — stessa regola
    di accesso (`User.is_admin`) di ogni altra vista qui, verificata
    server-side dentro `activate()`, non solo dal fatto che il link non
    compare per i non-admin."""

    def is_visible(self):
        # Raggiungibile solo dal link nella riga utente (UserAdminView), non
        # è una voce di menu a sé stante.
        return False

    @expose("/")
    def index(self):
        # Flask-Admin richiede una view di default su "/" per ogni BaseView;
        # non è mai il punto d'ingresso reale (si arriva solo da activate()
        # via il link nella riga utente), quindi si limita a rimandare alla
        # lista utenti.
        return redirect(url_for("user.index_view"))

    @expose("/<int:user_id>", methods=("GET", "POST"))
    def activate(self, user_id):
        # Difesa in profondità: is_accessible() (AdminAuthMixin) già blocca
        # l'intero blueprint Flask-Admin ai non-admin, ma un check esplicito
        # qui non fa mai male su un'azione che scrive stato di billing.
        if not (current_user.is_authenticated and current_user.is_admin):
            abort(403)

        user = db.session.get(User, user_id)
        if user is None:
            abort(404)

        if user.subscription_status == "lifetime":
            flash(
                f"{user.email} is on an AppSumo lifetime plan — it can't be replaced by a "
                "manual Revolut activation.",
                "error",
            )
            return redirect(url_for("user.index_view"))

        form = RevolutActivationForm()

        if form.validate_on_submit():
            try:
                result = activate_revolut_subscription(
                    user=user,
                    plan=form.plan.data,
                    admin=current_user,
                    payment_reference=form.payment_reference.data,
                    note=form.note.data,
                )
            except RevolutActivationError as exc:
                flash(str(exc), "error")
                return redirect(url_for("revolut-activation.activate", user_id=user.id))

            if result.already_processed:
                flash(
                    f"This payment reference was already processed for {user.email} — "
                    f"no changes made (current expiry: {result.new_expiry:%d %b %Y}).",
                    "info",
                )
            else:
                flash(
                    f"Revolut plan activated for {user.email}: {result.plan}, "
                    f"now expires {result.new_expiry:%d %b %Y}"
                    + ("" if result.email_sent else " (confirmation email not sent — see logs)."),
                    "success",
                )
            return redirect(url_for("user.edit_view", id=user.id))

        # Anteprima server-calcolata della nuova scadenza per ciascun piano —
        # stessa regola del service (estendi dalla scadenza futura, altrimenti
        # da now()) così il form non mostra mai un numero che il service
        # potrebbe poi calcolare diversamente. Solo informativa: il valore
        # autorevole resta quello ricalcolato da activate_revolut_subscription
        # al momento del submit, il client non può inviarne uno proprio.
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        current_expiry = user.subscription_expires_at
        if current_expiry is not None and current_expiry.tzinfo is None:
            current_expiry = current_expiry.replace(tzinfo=timezone.utc)
        base = current_expiry if (current_expiry and current_expiry > now) else now
        previews = {plan: base + timedelta(days=days) for plan, days in REVOLUT_PLAN_DAYS.items()}

        return self.render(
            "admin/revolut_activate.html",
            user=user,
            form=form,
            plan_days=REVOLUT_PLAN_DAYS,
            current_expiry=current_expiry,
            previews=previews,
        )


class RevolutAiTopupForm(FlaskForm):
    """Form server-side per "Accredita top-up AI Revolut" (vedi
    app/billing/revolut_ai_topup.py). Il client sceglie solo il pacchetto
    (chiave whitelistata) — quantità e prezzo restano sola-lettura nel
    template, ricavati dal catalogo server-side, mai inviati come valore
    fidato dal form."""

    product_key = SelectField(
        "AI credit package",
        choices=[
            (key, f"{entry['label']} — {entry['credits']} credits (€{entry['price']})")
            for key, entry in AI_TOPUP_CATALOG.items()
        ],
        validators=[],
    )
    payment_reference = StringField(
        "Revolut payment reference",
        validators=[DataRequired(), Length(max=255)],
    )
    note = TextAreaField("Admin note (optional)", validators=[Optional(), Length(max=1000)])


class RevolutAiTopupView(AdminAuthMixin, BaseView):
    """View Flask-Admin dedicata per il secondo flusso Revolut: accredito di
    un pacchetto crediti AI (vendita una tantum, MAI un'attivazione/estensione
    di abbonamento — vedi app/billing/revolut_ai_topup.py). Stessa struttura
    di RevolutActivationView, azione distinta."""

    def is_visible(self):
        # Raggiungibile solo dal link nella riga utente (UserAdminView).
        return False

    @expose("/")
    def index(self):
        return redirect(url_for("user.index_view"))

    @expose("/<int:user_id>", methods=("GET", "POST"))
    def credit(self, user_id):
        # Difesa in profondità, stessa nota di RevolutActivationView.activate.
        if not (current_user.is_authenticated and current_user.is_admin):
            abort(403)

        user = db.session.get(User, user_id)
        if user is None:
            abort(404)

        if not get_plan_limits(user).ai_credit_topups_allowed:
            flash(f"{user.email}'s plan is not eligible for AI credit top-ups.", "error")
            return redirect(url_for("user.index_view"))

        form = RevolutAiTopupForm()

        if form.validate_on_submit():
            try:
                result = credit_revolut_ai_topup(
                    user=user,
                    product_key=form.product_key.data,
                    payment_reference=form.payment_reference.data,
                    admin=current_user,
                    note=form.note.data,
                )
            except RevolutAiTopupError as exc:
                flash(str(exc), "error")
                return redirect(url_for("revolut-ai-topup.credit", user_id=user.id))

            if result.already_processed:
                flash(
                    f"This payment reference was already processed for {user.email} — "
                    f"no changes made (current balance: {result.balance_after} credits).",
                    "info",
                )
            else:
                flash(
                    f"AI credit top-up applied for {user.email}: +{result.credits_added} credits "
                    f"(new balance: {result.balance_after})"
                    + ("" if result.email_sent else " (confirmation email not sent — see logs)."),
                    "success",
                )
            return redirect(url_for("user.edit_view", id=user.id))

        return self.render(
            "admin/revolut_ai_topup.html",
            user=user,
            form=form,
            catalog=AI_TOPUP_CATALOG,
            current_balance=user.ai_credit_balance,
        )
