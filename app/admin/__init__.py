from app.admin.views import (
    AiCreditTransactionAdminView,
    PaddleTransactionAdminView,
    PaddleWebhookEventAdminView,
    ResourceUsageLogAdminView,
    UserAdminView,
)
from app.extensions import admin, db
from app.models import AiCreditTransaction, PaddleTransaction, PaddleWebhookEvent, ResourceUsageLog, User


def init_admin():
    """Registra le viste CRUD di Flask-Admin. Chiamata da create_app()."""
    admin.add_view(UserAdminView(User, db, name="Users"))
    admin.add_view(AiCreditTransactionAdminView(AiCreditTransaction, db, name="AI Credit Ledger"))
    admin.add_view(ResourceUsageLogAdminView(ResourceUsageLog, db, name="Usage Log"))
    admin.add_view(PaddleWebhookEventAdminView(PaddleWebhookEvent, db, name="Paddle Webhook Events"))
    admin.add_view(PaddleTransactionAdminView(PaddleTransaction, db, name="Paddle Transactions"))
