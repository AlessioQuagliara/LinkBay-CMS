from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    _register_extensions(app)
    _register_blueprints(app)
    _register_cli(app)
    _ensure_tables(app)

    return app


def _register_extensions(app):
    from app.extensions import admin, csrf, db, login_manager

    db.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Effettua l'accesso per continuare."
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.admin import init_admin

    init_admin()


def _register_blueprints(app):
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.gsc.gsc import gsc_bp
    from app.main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gsc_bp)


def _register_cli(app):
    import click

    from app.extensions import db

    @app.cli.command("init-db")
    def init_db():
        """Crea le tabelle nel database configurato (DATABASE_URL)."""
        db.create_all()
        print("Tabelle create.")

    @app.cli.command("make-admin")
    @click.argument("email")
    def make_admin(email):
        """Dà accesso a Flask-Admin a un utente già registrato (via email)."""
        from app.models import User

        user = User.query.filter_by(email=email.lower().strip()).first()
        if not user:
            print(f"Nessun utente con email {email}.")
            return
        user.is_admin = True
        db.session.commit()
        print(f"{user.email} ora può accedere a /admin/.")


def _ensure_tables(app):
    """Crea le tabelle mancanti all'avvio, così non serve ricordarsi di
    lanciare `flask init-db` a mano (es. dopo un `docker compose up` da zero).
    Non tocca le tabelle già esistenti: è lo stesso `db.create_all()` di
    `init-db`, solo eseguito automaticamente. Vedi README per quando invece
    servono migration vere."""
    from app.extensions import db

    with app.app_context():
        db.create_all()
