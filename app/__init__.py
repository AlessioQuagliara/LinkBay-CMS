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
    _register_access_gate(app)
    _register_cli(app)
    _register_error_handlers(app)
    # NB: la creazione delle tabelle NON avviene più qui. Con gunicorn ogni
    # worker importa run:app e chiamerebbe create_all() in parallelo → race su
    # pg_type (UniqueViolation). Ora è fatta una volta sola: nel master via
    # l'hook on_starting di gunicorn.conf.py in prod, e nel blocco __main__ di
    # run.py per il dev server. Vedi gunicorn.conf.py per il perché.

    return app


def _register_error_handlers(app):
    from app.errors import register_error_handlers

    register_error_handlers(app)


def _register_extensions(app):
    from flask_babel import lazy_gettext as _l

    from app.extensions import admin, csrf, db, login_manager

    db.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = _l("Please sign in to continue.")
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.admin import init_admin

    init_admin()

    from app.i18n import init_babel

    init_babel(app)


def _register_blueprints(app):
    from app.ai.routes import ai_bp
    from app.alerts.routes import alerts_bp
    from app.auth.routes import auth_bp
    from app.billing.routes import billing_bp
    from app.dashboard.routes import dashboard_bp
    from app.gsc.gsc import gsc_bp
    from app.main.routes import main_bp
    from app.settings.routes import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gsc_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(settings_bp)


def _register_access_gate(app):
    from app.billing.access import init_access_gate

    init_access_gate(app)


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

    @app.cli.command("import-appsumo-codes")
    @click.argument("path", type=click.Path(exists=True))
    def import_appsumo_codes(path):
        """Carica in blocco i codici di riscatto AppSumo da un file di testo
        (un codice per riga). Ignora righe vuote e codici già presenti."""
        from app.models import AppSumoCode

        added = skipped = 0
        with open(path) as f:
            codes = {line.strip().upper() for line in f if line.strip()}

        existing = {
            c.code for c in AppSumoCode.query.filter(AppSumoCode.code.in_(codes)).all()
        }
        for code in codes:
            if code in existing:
                skipped += 1
                continue
            db.session.add(AppSumoCode(code=code))
            added += 1
        db.session.commit()
        print(f"{added} codici aggiunti, {skipped} già presenti (ignorati).")

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
        decadenza per ogni sito monitorato. Schedulato dal servizio "cron"
        (vedi compose.prod.yml e ./crontab)."""
        from app.rules.service import run_weekly

        result = run_weekly()
        print(f"Processati {result['processed']} siti, "
              f"{len(result['errors'])} errori.")
        for err in result["errors"]:
            print(f"  - {err}")

    @app.cli.command("sync-full-history")
    def sync_full_history_cmd():
        """Job giornaliero: rinfresca GscSiteDaily per ogni sito monitorato,
        anche per gli utenti che non aprono la dashboard (quel sync è
        altrimenti lazy, solo su visita a Insights). Schedulato dal servizio
        "cron" (vedi compose.prod.yml e ./crontab)."""
        from app.gsc.gsc import get_user_gsc_service
        from app.gsc.history import FRESH_DAYS, sync_site_daily
        from app.gsc.repository import credentials_to_dict, save_gsc_credentials
        from app.models import GscConnection

        connections = GscConnection.query.filter(GscConnection.monitored_site_url.isnot(None)).all()

        processed = 0
        errors = []
        for conn in connections:
            site_url = conn.monitored_site_url
            try:
                service, credentials = get_user_gsc_service(conn.user_id)
                if service is None:
                    errors.append(f"user {conn.user_id}: non connesso a GSC")
                    continue
                sync_site_daily(service, conn.user_id, site_url, days=FRESH_DAYS)
                save_gsc_credentials(conn.user_id, credentials_to_dict(credentials))
                processed += 1
            except Exception as exc:  # noqa: BLE001 — un utente non deve fermare il job
                db.session.rollback()
                errors.append(f"user {conn.user_id} ({site_url}): {exc}")

        print(f"Processati {processed} siti, {len(errors)} errori.")
        for err in errors:
            print(f"  - {err}")

    @app.cli.command("send-weekly-digest")
    def send_weekly_digest_cmd():
        """Digest email del lunedì con le top declining pages, solo per chi
        ha un abbonamento pagante e non ha disattivato l'opt-out in Settings.
        Schedulato dal servizio "cron" (vedi compose.prod.yml e ./crontab),
        dopo run-decay-rules così i dati sono freschi."""
        from app.emails.digest import send_weekly_digest_for_user
        from app.models import User

        users = User.query.filter(
            User.subscription_status.in_(("active", "lifetime")),
            User.weekly_digest_enabled.is_(True),
        ).all()

        sent = skipped = errors = 0
        for user in users:
            site_url = user.gsc_connection.monitored_site_url if user.gsc_connection else None
            if not site_url:
                skipped += 1
                continue
            try:
                result = send_weekly_digest_for_user(user, site_url)
                if result is None:
                    skipped += 1
                elif result:
                    sent += 1
                else:
                    print(f"  - user {user.id}: invio email fallito")
                    errors += 1
            except Exception as exc:  # noqa: BLE001 — un utente non deve fermare il job
                db.session.rollback()
                print(f"  - user {user.id}: {exc}")
                errors += 1

        print(f"Digest inviati: {sent}, saltati (nessun alert): {skipped}, errori: {errors}.")

    @app.cli.command("check-page-recovery")
    def check_page_recovery_cmd():
        """Recovery-check: pagine marcate "done" da 30 o 60 giorni, verifica
        se il traffico è tornato (vedi app/rules/recovery.py). Schedulato dal
        servizio "cron" (vedi compose.prod.yml e ./crontab)."""
        from app.rules.recovery import check_due_alerts

        result = check_due_alerts()
        print(
            f"Valutati {result['checked']} alert, {result['recovered']} recuperati, "
            f"{result['errors']} errori."
        )


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


def init_db_schema():
    """Crea le tabelle mancanti usando un'app minimale usa-e-getta (solo il DB).

    Serve all'hook on_starting di gunicorn (una volta sola nel master, prima del
    fork). NON usa create_app() di proposito: quello registra le view di
    Flask-Admin sul singleton globale `admin`, operazione non idempotente — se
    create_app girasse due volte nello stesso processo (master + poi il worker
    forkato) esploderebbe con "name 'user' is already registered". Qui inizia
    solo `db`, senza admin né blueprint."""
    from flask import Flask

    from config import Config

    import app.models  # noqa: F401 — importa i modelli per popolare db.metadata
    from app.extensions import db

    ddl_app = Flask("db_init")
    ddl_app.config.from_object(Config)
    db.init_app(ddl_app)
    with ddl_app.app_context():
        db.create_all()
        _ensure_columns(db)
        # App usa e getta: chiudiamo il pool così i worker (che reimportano
        # run:app dopo il fork) partono con connessioni proprie.
        db.engine.dispose()


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

    # users: trial 14gg + stato abbonamento Lemon Squeezy / AppSumo (vedi app/billing/).
    if has_column("users", "id") and not has_column("users", "trial_ends_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN trial_ends_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "subscription_status"):
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) NOT NULL DEFAULT 'trialing'"
                )
            )
    if has_column("users", "id") and not has_column("users", "ls_customer_id"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN ls_customer_id VARCHAR(255)"))
    if has_column("users", "id") and not has_column("users", "ls_subscription_id"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN ls_subscription_id VARCHAR(255)"))

    # users.locale (preferenza lingua, vedi app/i18n.py e app/settings/).
    if has_column("users", "id") and not has_column("users", "locale"):
        with db.engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN locale VARCHAR(5) NOT NULL DEFAULT 'en'")
            )

    # users.weekly_digest_enabled (opt-out digest lunedì, vedi app/emails/digest.py).
    if has_column("users", "id") and not has_column("users", "weekly_digest_enabled"):
        default = "true" if dialect == "postgresql" else "1"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN weekly_digest_enabled BOOLEAN NOT NULL DEFAULT {default}"
                )
            )

    # page_alerts: timestamp per il recovery-check a 30/60gg (vedi app/rules/recovery.py).
    if has_column("page_alerts", "id") and not has_column("page_alerts", "done_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE page_alerts ADD COLUMN done_at TIMESTAMPTZ"))
    if has_column("page_alerts", "id") and not has_column("page_alerts", "checked_30d_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE page_alerts ADD COLUMN checked_30d_at TIMESTAMPTZ"))
    if has_column("page_alerts", "id") and not has_column("page_alerts", "checked_60d_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE page_alerts ADD COLUMN checked_60d_at TIMESTAMPTZ"))
