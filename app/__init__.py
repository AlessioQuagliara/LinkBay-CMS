from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config


def create_app(config_class=Config):
    from app.billing.access import init_access_gate
    from app.errors import register_error_handlers

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
    init_access_gate(app)
    _register_cli(app)
    register_error_handlers(app)
    _register_context_processors(app)
    # NB: la creazione delle tabelle NON avviene più qui. Con gunicorn ogni
    # worker importa run:app e chiamerebbe create_all() in parallelo → race su
    # pg_type (UniqueViolation). Ora è fatta una volta sola: nel master via
    # l'hook on_starting di gunicorn.conf.py in prod, e nel blocco __main__ di
    # run.py per il dev server. Vedi gunicorn.conf.py per il perché.

    return app


def _register_context_processors(app):
    @app.context_processor
    def inject_ai_credit_flags():
        # dashboard/layout.html è condiviso da più blueprint (dashboard,
        # billing): un context processor globale invece che scoped a un
        # singolo blueprint, così il link "AI Credits" in sidebar compare per
        # ogni pagina che estende quel layout, non solo per le route di
        # dashboard_bp. Nessuna query aggiuntiva: get_plan_limits legge da
        # PLAN_LIMITS, non dal DB.
        #
        # Due flag distinti: "ai_credit_topups_allowed" governa la CTA di
        # acquisto (solo AppSumo, business rule invariata), mentre
        # "ai_credit_ledger_visible" governa la visibilità del link stesso —
        # più ampio: qualunque piano ai_mode=="credit" (AppSumo + Pro)
        # ha un saldo/storico da vedere in /billing/credits, anche se non può
        # comprare top-up. Il trial (ai_mode=="cooldown") non ha un ledger.
        from flask_login import current_user

        if not current_user.is_authenticated:
            return {"ai_credit_topups_allowed": False, "ai_credit_ledger_visible": False}
        from app.entitlements.service import get_plan_limits

        limits = get_plan_limits(current_user)
        return {
            "ai_credit_topups_allowed": limits.ai_credit_topups_allowed,
            "ai_credit_ledger_visible": limits.ai_mode == "credit",
        }


def _register_extensions(app):
    from flask_babel import lazy_gettext as _l

    from app.extensions import admin, csrf, db, limiter, login_manager

    db.init_app(app)
    csrf.init_app(app)
    admin.init_app(app)
    limiter.init_app(app)

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
    from app.billing.access import GATED_BLUEPRINTS, init_rate_limits
    from app.billing.routes import billing_bp
    from app.audits.routes import audits_bp
    from app.chat.routes import chat_bp
    from app.dashboard.routes import dashboard_bp
    from app.exports.routes import exports_bp
    from app.gsc.gsc import gsc_bp
    from app.main.routes import main_bp
    from app.settings.routes import settings_bp
    from app.webhooks.routes import webhooks_bp

    blueprints = [
        main_bp, auth_bp, billing_bp, dashboard_bp, gsc_bp, ai_bp, alerts_bp,
        settings_bp, exports_bp, chat_bp, audits_bp, webhooks_bp,
    ]
    # Rate limit per piano solo sui blueprint a pagamento, prima della registrazione.
    init_rate_limits([bp for bp in blueprints if bp.name in GATED_BLUEPRINTS])
    for bp in blueprints:
        app.register_blueprint(bp)


def _register_cli(app):
    import click

    from app.extensions import db

    @app.cli.command("init-db")
    def init_db():
        """Crea le tabelle nel database configurato (DATABASE_URL)."""
        db.create_all()
        _ensure_columns(db)
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
    @click.option("--tier", type=click.IntRange(1, 3), required=True, help="Tier 1/2/3 di questo lotto di codici.")
    def import_appsumo_codes(path, tier):
        """Carica in blocco i codici di riscatto AppSumo da un file di testo
        (un codice per riga, tutti dello stesso tier — così AppSumo distribuisce
        i lotti). Ignora righe vuote e codici già presenti."""
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
            db.session.add(AppSumoCode(code=code, tier=tier))
            added += 1
        db.session.commit()
        print(f"{added} codici Tier {tier} aggiunti, {skipped} già presenti (ignorati).")

    @app.cli.command("sync-page-history")
    @click.argument("email")
    def sync_page_history_cmd(email):
        """Sincronizza lo storico mensile per pagina dei siti monitorati di
        un utente (per test manuale)."""
        from app.gsc.gsc import get_user_gsc_service
        from app.gsc.page_history import sync_page_monthly
        from app.gsc.sites import list_monitored_sites
        from app.models import User

        user = User.query.filter_by(email=email.lower().strip()).first()
        if not user:
            print(f"Nessun utente con email {email}.")
            return

        site_rows = list_monitored_sites(user.id)
        if not site_rows:
            print(f"{user.email} non ha ancora scelto un sito monitorato.")
            return

        service, _ = get_user_gsc_service(user.id)
        if service is None:
            print(f"{user.email} non è connesso a Google Search Console.")
            return

        for row in site_rows:
            try:
                written = sync_page_monthly(service, user.id, row.site_url)
            except Exception as exc:  # noqa: BLE001 — mostra l'errore GSC senza traceback
                print(f"Errore durante il sync GSC per {row.site_url}: {exc}")
                continue
            print(f"{written} righe scritte/aggiornate in gsc_page_monthly per {row.site_url}.")

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
        "cron" (vedi compose.prod.yml e ./crontab). Itera MonitoredSite: un
        utente con più siti viene processato una volta per sito."""
        from app.gsc.gsc import get_user_gsc_service
        from app.gsc.history import FRESH_DAYS, sync_site_daily
        from app.gsc.repository import credentials_to_dict, save_gsc_credentials
        from app.gsc.sites import touch_last_synced
        from app.models import MonitoredSite

        sites = MonitoredSite.query.filter_by(is_active=True).all()

        processed = 0
        errors = []
        for row in sites:
            try:
                service, credentials = get_user_gsc_service(row.user_id)
                if service is None:
                    errors.append(f"user {row.user_id}: non connesso a GSC")
                    continue
                sync_site_daily(service, row.user_id, row.site_url, days=FRESH_DAYS)
                save_gsc_credentials(row.user_id, credentials_to_dict(credentials))
                touch_last_synced(row.user_id, row.site_url)
                processed += 1
            except Exception as exc:  # noqa: BLE001 — un sito non deve fermare il job
                db.session.rollback()
                errors.append(f"user {row.user_id} ({row.site_url}): {exc}")

        print(f"Processati {processed} siti, {len(errors)} errori.")
        for err in errors:
            print(f"  - {err}")

    @app.cli.command("send-weekly-digest")
    def send_weekly_digest_cmd():
        """Digest email del lunedì con le top declining pages, solo per chi
        ha un abbonamento pagante e non ha disattivato l'opt-out in Settings.
        Schedulato dal servizio "cron" (vedi compose.prod.yml e ./crontab),
        dopo run-decay-rules così i dati sono freschi. Un utente con più siti
        (vedi MonitoredSite) riceve un'email per sito — un digest combinato
        multi-sito è un miglioramento UX rimandato a una fase successiva."""
        from app.emails.digest import send_weekly_digest_for_user
        from app.gsc.sites import list_monitored_sites
        from app.models import User

        from app.entitlements.service import has_active_entitlement

        # Lo status da solo non basta: un abbonamento "active" con scadenza
        # passata (webhook di fine periodo non ancora arrivato) non ha accesso.
        users = [
            u for u in User.query.filter(
                User.subscription_status.in_(("active", "lifetime")),
                User.weekly_digest_enabled.is_(True),
            ).all()
            if has_active_entitlement(u)
        ]

        sent = skipped = errors = 0
        for user in users:
            site_rows = list_monitored_sites(user.id)
            if not site_rows:
                skipped += 1
                continue
            for row in site_rows:
                try:
                    result = send_weekly_digest_for_user(user, row.site_url)
                    if result is None:
                        skipped += 1
                    elif result:
                        sent += 1
                    else:
                        print(f"  - user {user.id} ({row.site_url}): invio email fallito")
                        errors += 1
                except Exception as exc:  # noqa: BLE001 — un utente non deve fermare il job
                    db.session.rollback()
                    print(f"  - user {user.id} ({row.site_url}): {exc}")
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

    @app.cli.command("grant-monthly-ai-credits")
    def grant_monthly_ai_credits_cmd():
        """Accredita la quota AI mensile a ogni piano ai_mode=="credit" con
        accesso attivo (has_active_entitlement). Idempotente per mese."""
        from datetime import datetime, timezone

        from app.entitlements.ai_credits import grant_credits
        from app.entitlements.limits import PLAN_LIMITS
        from app.entitlements.service import has_active_entitlement
        from app.models import AiCreditTransaction, User

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        granted = skipped = 0
        for plan_type, limits in PLAN_LIMITS.items():
            if limits.ai_mode != "credit" or limits.ai_credit_grant <= 0:
                continue
            for user in User.query.filter_by(plan_type=plan_type).all():
                if not has_active_entitlement(user):
                    continue
                already_this_month = (
                    AiCreditTransaction.query.filter(
                        AiCreditTransaction.user_id == user.id,
                        AiCreditTransaction.type == "grant_monthly_quota",
                        AiCreditTransaction.created_at >= month_start,
                    ).first()
                    is not None
                )
                if already_this_month:
                    skipped += 1
                    continue
                grant_credits(user, limits.ai_credit_grant, type="grant_monthly_quota")
                db.session.commit()
                granted += 1

        print(f"Quota AI mensile accreditata a {granted} utenti, {skipped} già accreditati questo mese o senza accesso attivo.")

    @app.cli.command("flag-heavy-users")
    def flag_heavy_users_cmd():
        """Rivaluta il flag "heavy user" (monitoraggio costi infrastrutturali)
        per ogni utente con attività negli ultimi 30 giorni. Schedulato
        settimanalmente dal servizio "cron"."""
        from app.entitlements.heavy_user import flag_heavy_users

        result = flag_heavy_users()
        print(f"{len(result['flagged'])} utenti segnalati come heavy user, {len(result['unflagged'])} rimossi dal flag.")

    @app.cli.command("seed-demo-account")
    @click.option("--email", default="alessio@linkbay-cms.com", show_default=True,
                  help="Email dell'account demo (creato se non esiste, riusato se già presente).")
    @click.option("--password", default=None,
                  help="Password dell'account demo. Se omessa, ne viene generata una e stampata a schermo.")
    @click.option("--name", default="Alessio Demo", show_default=True, help="Nome visualizzato dell'account demo.")
    def seed_demo_account_cmd(email, password, name):
        """Crea/ripristina un account demo con siti e storico Search Console
        sintetici, alert generati dal vero rule engine e una audit
        presentation — per testare/registrare Pagine in calo e Audit senza
        toccare account reali. Ogni run azzera e rigenera SOLO i dati di
        questo indirizzo email (vedi app/demo/seed_account.py)."""
        import secrets

        from app.demo.seed_account import seed_demo_account

        generated_password = password or secrets.token_urlsafe(9)
        summary = seed_demo_account(email, generated_password, name=name)

        print(f"Account demo pronto: {summary['email']} (id {summary['user_id']})")
        if not password:
            print(f"Password generata: {generated_password}")
        for site in summary["sites"]:
            print(f"  - {site['site_url']}: {site['pages']} pagine, {site['alerts']} alert generati dal rule engine")
        if summary.get("audit_presentation"):
            ap = summary["audit_presentation"]
            print(f"Audit presentation creata: #{ap['id']} — {ap['title']}")
        elif summary.get("audit_presentation_error"):
            print(f"Audit presentation non generata ({summary['audit_presentation_error']}) "
                  "— riprova più tardi dal bottone Genera in /dashboard/audits.")

    @app.cli.command("paddle-sync-catalog")
    @click.option(
        "--environment", type=click.Choice(["sandbox", "production"]), required=True,
        help="Quale set di credenziali/price ID usare (vedi PADDLE_ENVIRONMENT in config.py).",
    )
    @click.option("--currency", default="EUR", show_default=True)
    @click.option(
        "--dry-run", is_flag=True, default=False,
        help="Non chiama l'API Paddle: stampa solo quali env var andrebbero valorizzate.",
    )
    def paddle_sync_catalog_cmd(environment, currency, dry_run):
        """Crea/recupera in Paddle un prodotto+price per ogni piano Pro e
        pacchetto crediti AI del catalogo whitelist (vedi
        app/billing/paddle_products.py) — idempotente, rilanciabile senza
        duplicare nulla (riusa un prodotto/price già esistente con lo stesso
        nome/importo). Stampa gli ID risultanti E il nome della env var in
        cui vanno incollati in .env — non li scrive mai lì da solo (vedi
        docs/paddle-billing.md, "Setup catalogo")."""
        from app.billing.paddle_catalog_sync import sync_catalog

        entries = sync_catalog(environment=environment, currency=currency, dry_run=dry_run)
        print(f"Catalogo Paddle ({environment}, dry_run={dry_run}):")
        for e in entries:
            marker = "creato" if e.created_price else ("prodotto nuovo" if e.created_product else "già esistente")
            print(f"  [{e.kind}] {e.internal_key}: {e.product_name}")
            print(f"      product_id={e.product_id}  price_id={e.price_id}  ({marker})")
            print(f"      -> imposta {e.price_env_var}={e.price_id} in .env")

    @app.cli.command("paddle-reconcile")
    @click.option(
        "--environment", type=click.Choice(["sandbox", "production"]), required=True,
        help="Riconcilia solo gli utenti Paddle di questo environment — mai mescolato con l'altro.",
    )
    @click.option(
        "--apply", "apply_changes", is_flag=True, default=False,
        help="Senza questo flag gira in dry-run: legge lo stato remoto e mostra le differenze, ma non scrive nulla.",
    )
    @click.option("--user-id", type=int, default=None, help="Limita la riconciliazione a un solo utente (per id).")
    def paddle_reconcile_cmd(environment, apply_changes, user_id):
        """Fallback operativo per webhook Paddle persi o stato locale
        incoerente (vedi Fase 6): rilegge da Paddle lo stato di ogni
        subscription collegata a un utente locale e lo riapplica con la
        stessa logica del webhook (app/billing/paddle_subscriptions.py).
        Tocca SOLO utenti subscription_source == "paddle" nell'environment
        indicato — mai un utente AppSumo/legacy, mai l'altro
        environment. Dry-run di default: passa --apply per scrivere
        davvero."""
        from app.billing.paddle_reconciliation import reconcile_paddle_users

        report = reconcile_paddle_users(environment=environment, dry_run=not apply_changes, user_id=user_id)
        print(
            f"Riconciliazione Paddle ({report.environment}, "
            f"{'DRY-RUN — nessuna scrittura' if report.dry_run else 'APPLICATA'}): "
            f"{report.checked} utenti controllati, {report.changed} con differenze."
        )
        for row in report.rows:
            if row.outcome == "api_error":
                print(f"  - user {row.user_id} ({row.email}): errore API Paddle — {row.reason}")
                continue
            changed = row.before_status != row.after_status or row.before_expires_at != row.after_expires_at
            marker = "MODIFICATO" if changed else "invariato"
            print(
                f"  - user {row.user_id} ({row.email}) sub={row.paddle_subscription_id}: "
                f"{row.before_status}/{row.before_expires_at} -> {row.after_status}/{row.after_expires_at} "
                f"[{marker}, outcome={row.outcome}]"
            )


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


# Colonne aggiunte dopo il primo deploy: (tabella, colonna, tipo DDL, SQL extra).
# {false}/{true} vengono resi per dialetto. Aggiungere una riga per ogni nuova colonna.
_ADDED_COLUMNS = [
    ("users", "email_verified", "BOOLEAN NOT NULL DEFAULT {false}", None),
    ("gsc_connections", "monitored_site_url", "VARCHAR(500)", None),
    ("users", "trial_ends_at", "TIMESTAMPTZ", None),
    ("users", "subscription_status", "VARCHAR(20) NOT NULL DEFAULT 'trialing'", None),
    ("users", "ls_customer_id", "VARCHAR(255)", None),
    ("users", "ls_subscription_id", "VARCHAR(255)", None),
    ("users", "locale", "VARCHAR(5) NOT NULL DEFAULT 'en'", None),
    ("users", "weekly_digest_enabled", "BOOLEAN NOT NULL DEFAULT {true}", None),
    ("users", "plan_type", "VARCHAR(30)", None),
    ("users", "billing_interval", "VARCHAR(10)", None),
    ("users", "grace_period_ends_at", "TIMESTAMPTZ", None),
    ("users", "ai_credit_balance", "INTEGER NOT NULL DEFAULT 0", None),
    ("users", "heavy_user_flag", "BOOLEAN NOT NULL DEFAULT {false}", None),
    ("users", "heavy_user_flagged_at", "TIMESTAMPTZ", None),
    ("users", "white_label_enabled", "BOOLEAN NOT NULL DEFAULT {false}", None),
    ("users", "appsumo_migration_unlocked", "BOOLEAN NOT NULL DEFAULT {false}", None),
    ("users", "subscription_expires_at", "TIMESTAMPTZ", None),
    ("users", "subscription_source", "VARCHAR(30)", None),
    ("users", "subscription_activated_at", "TIMESTAMPTZ", None),
    ("users", "subscription_activated_by_id", "INTEGER REFERENCES users(id)", None),
    # UNIQUE standard (non parziale): Postgres e SQLite trattano ogni NULL come
    # distinto, quindi più righe senza valore convivono senza violare il vincolo.
    ("users", "subscription_activation_reference", "VARCHAR(255)",
     "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_subscription_activation_reference "
     "ON users (subscription_activation_reference)"),
    ("appsumo_codes", "tier", "INTEGER", None),
    ("monitored_sites", "last_synced_at", "TIMESTAMPTZ", None),
    ("page_alerts", "done_at", "TIMESTAMPTZ", None),
    ("page_alerts", "checked_30d_at", "TIMESTAMPTZ", None),
    ("page_alerts", "checked_60d_at", "TIMESTAMPTZ", None),
    ("ai_credit_transactions", "balance_before", "INTEGER", None),
    ("ai_credit_transactions", "product_key", "VARCHAR(50)", None),
    ("ai_credit_transactions", "payment_source", "VARCHAR(30)", None),
    ("ai_credit_transactions", "approved_by_user_id", "INTEGER REFERENCES users(id)", None),
    ("ai_credit_transactions", "admin_note", "TEXT", None),
    ("ai_credit_transactions", "payment_reference", "VARCHAR(255)",
     "CREATE UNIQUE INDEX IF NOT EXISTS ix_ai_credit_transactions_payment_reference "
     "ON ai_credit_transactions (payment_reference)"),
    ("ai_credit_transactions", "action", "VARCHAR(30)", None),
    ("audit_presentations", "chart_data", "TEXT", None),
    ("users", "paddle_customer_id", "VARCHAR(255)",
     "CREATE INDEX IF NOT EXISTS ix_users_paddle_customer_id ON users (paddle_customer_id)"),
    ("users", "paddle_subscription_id", "VARCHAR(255)",
     "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_paddle_subscription_id ON users (paddle_subscription_id)"),
    ("users", "paddle_price_id", "VARCHAR(255)", None),
    ("users", "paddle_environment", "VARCHAR(10)", None),
    ("users", "current_period_ends_at", "TIMESTAMPTZ", None),
    ("users", "cancel_at_period_end", "BOOLEAN NOT NULL DEFAULT {false}", None),
    ("users", "last_paddle_sync_at", "TIMESTAMPTZ", None),
]


def _ensure_columns(db):
    """Micro-migrazione idempotente: `db.create_all()` crea le tabelle mancanti
    ma NON aggiunge colonne nuove a tabelle già esistenti. Senza un tool di
    migration, aggiunge qui le colonne di _ADDED_COLUMNS solo se mancano."""
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    pg = db.engine.dialect.name == "postgresql"
    bools = {"false": "false" if pg else "0", "true": "true" if pg else "1"}

    def has_column(table, column):
        try:
            return column in {c["name"] for c in inspector.get_columns(table)}
        except Exception:  # noqa: BLE001 — tabella non ancora esistente, ecc.
            return False

    for table, column, ddl, extra_sql in _ADDED_COLUMNS:
        if not has_column(table, "id") or has_column(table, column):
            continue
        with db.engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl.format(**bools)}"))
            if extra_sql:
                conn.execute(text(extra_sql))
