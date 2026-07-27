from app.admin.views import UserAdminView
from app.extensions import admin, db
from app.models import User


def init_admin():
    """Registra le viste CRUD di Flask-Admin. Chiamata da create_app()."""
    admin.add_view(UserAdminView(User, db.session, name="Users"))
