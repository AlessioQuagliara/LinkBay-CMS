from app.admin.views import (
    AiCreditTransactionAdminView,
    ResourceUsageLogAdminView,
    RevolutActivationView,
    UserAdminView,
)
from app.extensions import admin, db
from app.models import AiCreditTransaction, ResourceUsageLog, User


def init_admin():
    """Registra le viste CRUD di Flask-Admin. Chiamata da create_app()."""
    admin.add_view(UserAdminView(User, db, name="Users"))
    admin.add_view(AiCreditTransactionAdminView(AiCreditTransaction, db, name="AI Credit Ledger"))
    admin.add_view(ResourceUsageLogAdminView(ResourceUsageLog, db, name="Usage Log"))
    # Non-CRUD: form dedicato "Attiva abbonamento Revolut", raggiungibile dal
    # link nella riga utente (vedi UserAdminView.column_formatters) — nascosta
    # dal menu (is_visible() -> False in RevolutActivationView).
    admin.add_view(
        RevolutActivationView(name="Revolut Activation", endpoint="revolut-activation")
    )
