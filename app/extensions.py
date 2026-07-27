"""Istanze delle estensioni Flask, centralizzate per evitare import circolari.

Vengono create qui senza `app` e agganciate all'app con `.init_app(app)`
dentro `create_app()` (app/__init__.py). Qualunque modulo può importare
`db`, `login_manager`, `csrf` o `admin` da qui senza dipendere dalla factory.
"""
from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.theme import Bootstrap4Theme
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


class AdminAuthMixin:
    """Regola di accesso condivisa da tutte le viste di Flask-Admin:
    dentro solo al team (`User.is_admin`), mai ai clienti normali.
    Non è RBAC, è un solo flag booleano — si imposta con `flask make-admin
    <email>` (vedi README, sezione "Come continuare da solo senza AI")."""

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))


class SecureAdminIndexView(AdminAuthMixin, AdminIndexView):
    pass


admin = Admin(
    name="LinkBayCMS",
    theme=Bootstrap4Theme(swatch="flatly"),
    index_view=SecureAdminIndexView(),
)
