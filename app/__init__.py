from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Dietro Traefik l'app riceve richieste in HTTP dall'host interno
    # (web:3000), ma è servita pubblicamente su https://www.linkbay-cms.com.
    # Senza questo, request.scheme/host — e quindi url_for(_external=True) e il
    # redirect URI OAuth di Google Search Console — risulterebbero sbagliati
    # (http:// e host interno), ed è il motivo per cui il collegamento GSC
    # funzionava solo in locale. ProxyFix fa fidare Flask degli header
    # X-Forwarded-* impostati dal primo (e unico) proxy davanti all'app.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    _register_extensions(app)
    _register_blueprints(app)
    _register_cli(app)
    _register_error_handlers(app)
    _ensure_tables(app)

    return app


def _register_error_handlers(app):
    from app.errors import register_error_handlers

    register_error_handlers(app)


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
    from app.ai.routes import ai_bp
    from app.alerts.routes import alerts_bp
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.gsc.gsc import gsc_bp
    from app.main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gsc_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(alerts_bp)


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

    @app.cli.command("sync-page-history")
    @click.argument("email")
    def sync_page_history_cmd(email):
        """Sincronizza lo storico mensile per pagina del sito monitorato di
        un utente (per test manuale)."""
        from app.gsc.gsc import get_user_gsc_service
        from app.gsc.page_history import sync_page_monthly
        from app.gsc.repository import get_monitored_site
        from app.models import User

        user = User.query.filter_by(email=email.lower().strip()).first()
        if not user:
            print(f"Nessun utente con email {email}.")
            return

        site_url = get_monitored_site(user.id)
        if not site_url:
            print(f"{user.email} non ha ancora scelto un sito monitorato.")
            return

        service, _ = get_user_gsc_service(user.id)
        if service is None:
            print(f"{user.email} non è connesso a Google Search Console.")
            return

        try:
            written = sync_page_monthly(service, user.id, site_url)
        except Exception as exc:  # noqa: BLE001 — mostra l'errore GSC senza traceback
            print(f"Errore durante il sync GSC per {site_url}: {exc}")
            return

        print(f"{written} righe scritte/aggiornate in gsc_page_monthly per {site_url}.")

    @app.cli.command("run-decay-rules")
    def run_decay_rules_cmd():
        """Job settimanale: sincronizza lo storico e applica le regole di
        decadenza per ogni sito monitorato. Da schedulare con un cron di
        sistema (es. lunedì alle 4:00), non con un servizio separato."""
        from app.rules.service import run_weekly

        result = run_weekly()
        print(f"Processati {result['processed']} siti, "
              f"{len(result['errors'])} errori.")
        for err in result["errors"]:
            print(f"  - {err}")


def _ensure_tables(app):
    """Crea le tabelle mancanti all'avvio, così non serve ricordarsi di
    lanciare `flask init-db` a mano (es. dopo un `docker compose up` da zero).
    Non tocca le tabelle già esistenti: è lo stesso `db.create_all()` di
    `init-db`, solo eseguito automaticamente. Vedi README per quando invece
    servono migration vere."""
    from app.extensions import db

    with app.app_context():
        db.create_all()
        _ensure_columns(db)


def _ensure_columns(db):
    """Micro-migrazione idempotente: `db.create_all()` crea le tabelle mancanti
    ma NON aggiunge colonne nuove a tabelle già esistenti. Senza un tool di
    migration, aggiungiamo qui a mano le colonne introdotte dopo il primo
    deploy, solo se mancano. Aggiungere una riga per ogni nuova colonna."""
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    dialect = db.engine.dialect.name

    def has_column(table, column):
        try:
            return column in {c["name"] for c in inspector.get_columns(table)}
        except Exception:  # noqa: BLE001 — tabella non ancora esistente, ecc.
            return False

    # users.email_verified (introdotta con l'OTP email al login/registrazione).
    if has_column("users", "id") and not has_column("users", "email_verified"):
        default = "false" if dialect == "postgresql" else "0"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT {default}"
                )
            )

    # gsc_connections.monitored_site_url (sito scelto per il monitoraggio).
    if has_column("gsc_connections", "id") and not has_column("gsc_connections", "monitored_site_url"):
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE gsc_connections ADD COLUMN monitored_site_url VARCHAR(500)"
                )
            )
