from flask_admin.contrib.sqla import ModelView

from app.extensions import AdminAuthMixin


class SecureModelView(AdminAuthMixin, ModelView):
    """Base per le viste Flask-Admin: dentro solo al team (`User.is_admin`)."""


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
    )
    # white_label_enabled è editabile solo da
    # qui (nessun bottone self-service nell'app) — vedi
    # app/billing/routes.py::redeem(). heavy_user_flag NON è nella form: è
    # calcolato dal job settimanale flask flag-heavy-users, non va corretto a
    # mano (si autocorregge al giro successivo).
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
        "name", "email", "is_admin", "plan_type", "white_label_enabled",
        "paddle_customer_id", "paddle_subscription_id",
    )
    column_searchable_list = ("name", "email", "paddle_customer_id", "paddle_subscription_id")
    column_filters = ("plan_type", "subscription_status", "subscription_source", "heavy_user_flag")
    column_default_sort = ("created_at", True)


class AiCreditTransactionAdminView(SecureModelView):
    """Sola lettura: il ledger crediti si scrive solo tramite
    app/entitlements/ai_credits.py (consumo AI, job mensile, acquisto
    Paddle) — mai a mano, altrimenti balance_after perde di significato.
    ls_order_id resta per l'audit storico Lemon Squeezy; payment_reference/
    payment_source coprono acquisti storici (incluso il canale Revolut
    dismesso) — le due coppie di colonne non si sovrappongono mai sulla
    stessa riga."""
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
