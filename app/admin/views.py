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
        "ai_credit_balance", "heavy_user_flag", "created_at",
    )
    # appsumo_migration_unlocked e white_label_enabled sono editabili solo da
    # qui (nessun bottone self-service nell'app) — vedi
    # app/billing/routes.py::checkout(). heavy_user_flag NON è nella form:
    # è calcolato dal job settimanale flask flag-heavy-users, non va
    # corretto a mano (si autocorregge al giro successivo).
    form_columns = ("name", "email", "is_admin", "plan_type", "appsumo_migration_unlocked", "white_label_enabled")
    column_searchable_list = ("name", "email")
    column_filters = ("plan_type", "subscription_status", "heavy_user_flag")
    column_default_sort = ("created_at", True)


class AiCreditTransactionAdminView(SecureModelView):
    """Sola lettura: il ledger crediti si scrive solo tramite
    app/entitlements/ai_credits.py (webhook Lemon Squeezy, consumo AI, job
    mensile) — mai a mano, altrimenti balance_after perde di significato."""
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
