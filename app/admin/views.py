from flask import abort, flash, redirect, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import SelectField, StringField, TextAreaField
from wtforms.validators import Length, Optional

from app.billing.revolut_manual_activation import (
    REVOLUT_PLAN_DAYS,
    RevolutActivationError,
    activate_revolut_subscription,
)
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
        "ai_credit_balance", "heavy_user_flag", "created_at", "revolut_action",
    )
    # appsumo_migration_unlocked e white_label_enabled sono editabili solo da
    # qui (nessun bottone self-service nell'app) — vedi
    # app/billing/routes.py::redeem(). L'attivazione Revolut NON è nella form
    # (vedi colonna virtuale "revolut_action" sotto): serve un calcolo
    # server-side della nuova scadenza che una semplice form CRUD non fa,
    # quindi vive nella sua view dedicata (RevolutActivationView).
    # heavy_user_flag NON è nella form: è calcolato dal job settimanale
    # flask flag-heavy-users, non va corretto a mano (si autocorregge al
    # giro successivo).
    form_columns = ("name", "email", "is_admin", "plan_type", "appsumo_migration_unlocked", "white_label_enabled")
    column_searchable_list = ("name", "email")
    column_filters = ("plan_type", "subscription_status", "subscription_source", "heavy_user_flag")
    column_default_sort = ("created_at", True)
    column_formatters = {"revolut_action": _format_revolut_action}


class AiCreditTransactionAdminView(SecureModelView):
    """Sola lettura: il ledger crediti si scrive solo tramite
    app/entitlements/ai_credits.py (consumo AI, job mensile — l'acquisto
    one-time via Lemon Squeezy è stato rimosso, vedi
    app/templates/billing/credits.html) — mai a mano, altrimenti
    balance_after perde di significato."""
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ("id", "user", "type", "amount", "balance_after", "ls_order_id", "site_url", "created_at")
    column_searchable_list = ("ls_order_id",)
    column_filters = ("type",)
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
