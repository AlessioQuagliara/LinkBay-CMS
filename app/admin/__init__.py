from app.admin.views import (
    AiCreditTransactionAdminView,
    ResourceUsageLogAdminView,
    RevolutActivationView,
    RevolutAiTopupView,
    UserAdminView,
)
from app.extensions import admin, db
from app.models import AiCreditTransaction, ResourceUsageLog, User


def init_admin():
    """Registra le viste CRUD di Flask-Admin. Chiamata da create_app()."""
    admin.add_view(UserAdminView(User, db, name="Users"))
    admin.add_view(AiCreditTransactionAdminView(AiCreditTransaction, db, name="AI Credit Ledger"))
    admin.add_view(ResourceUsageLogAdminView(ResourceUsageLog, db, name="Usage Log"))
    # Non-CRUD, nascoste dal menu (is_visible() -> False), raggiungibili solo
    # dai link nella riga utente (vedi UserAdminView.column_formatters):
    # "Attiva abbonamento Revolut" (piano Pro a termine) e "Accredita top-up
    # AI Revolut" (vendita una tantum, ledger crediti — mai il piano).
    admin.add_view(
        RevolutActivationView(name="Revolut Activation", endpoint="revolut-activation")
    )
    admin.add_view(
        RevolutAiTopupView(name="Revolut AI Top-up", endpoint="revolut-ai-topup")
    )
