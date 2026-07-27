from flask_admin.contrib.sqla import ModelView

from app.extensions import AdminAuthMixin


class SecureModelView(AdminAuthMixin, ModelView):
    """Base per le viste Flask-Admin: dentro solo al team (`User.is_admin`)."""


class UserAdminView(SecureModelView):
    # La password non è nel form: gli utenti si creano da /auth/register.
    column_list = ("id", "name", "email", "is_admin", "created_at")
    form_columns = ("name", "email", "is_admin")
    column_searchable_list = ("name", "email")
    column_default_sort = ("created_at", True)
