from flask_admin.contrib.sqla import ModelView

from app.extensions import AdminAuthMixin


class SecureModelView(AdminAuthMixin, ModelView):
    """Base per le viste Flask-Admin: dentro solo al team (`User.is_admin`)."""


class UserAdminView(SecureModelView):
    # Niente "Create" qui: User.password_hash è NOT NULL e questo form non
    # raccoglie una password, quindi un insert fallirebbe sempre con un
    # integrity error. Gli utenti si creano solo da /auth/register; qui si
    # gestiscono solo anagrafica e il flag is_admin.
    can_create = False
    column_list = ("id", "name", "email", "is_admin", "created_at")
    form_columns = ("name", "email", "is_admin")
    column_searchable_list = ("name", "email")
    column_default_sort = ("created_at", True)
