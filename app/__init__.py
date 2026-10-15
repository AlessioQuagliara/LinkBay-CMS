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
    _register_context_processors(app)
    # NB: la creazione delle tabelle NON avviene più qui. Con gunicorn ogni
    # worker importa run:app e chiamerebbe create_all() in parallelo → race su
    # pg_type (UniqueViolation). Ora è fatta una volta sola: nel master via
    # l'hook on_starting di gunicorn.conf.py in prod, e nel blocco __main__ di
    # run.py per il dev server. Vedi gunicorn.conf.py per il perché.

    return app


def _register_error_handlers(app):
    from app.errors import register_error_handlers

    register_error_handlers(app)


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
    from app.billing.access import init_rate_limits
    from app.billing.routes import billing_bp
    from app.audits.routes import audits_bp
    from app.chat.routes import chat_bp
    from app.dashboard.routes import dashboard_bp
    from app.exports.routes import exports_bp
    from app.gsc.gsc import gsc_bp
    from app.main.routes import main_bp
    from app.settings.routes import settings_bp
    from app.webhooks.routes import webhooks_bp

    # Rate limit per piano (vedi app/billing/access.py) — va applicato prima
    # della registrazione sull'app, idioma standard dei limiti a livello di
    # blueprint di Flask-Limiter.
    init_rate_limits([dashboard_bp, gsc_bp, ai_bp, alerts_bp, exports_bp, audits_bp])

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gsc_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(audits_bp)
    app.register_blueprint(webhooks_bp)


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

    @app.cli.command("backfill-monitored-sites")
    def backfill_monitored_sites_cmd():
        """Una tantum: copia GscConnection.monitored_site_url (singolare,
        deprecato) in una riga MonitoredSite per ogni utente. Idempotente —
        rilanciabile senza creare duplicati (add_monitored_site riattiva una
        riga esistente invece di duplicarla). Da lanciare una volta prima del
        deploy che introduce il multi-sito, così i job schedulati (che ora
        iterano MonitoredSite) continuano a coprire gli utenti già connessi."""
        from app.gsc.sites import add_monitored_site
        from app.models import GscConnection

        connections = GscConnection.query.filter(GscConnection.monitored_site_url.isnot(None)).all()

        added = 0
        for conn in connections:
            add_monitored_site(conn.user_id, conn.monitored_site_url)
            added += 1

        print(f"Backfill completato: {added} collegamenti utente→sito verificati/creati in monitored_sites.")

    @app.cli.command("backfill-plan-type")
    def backfill_plan_type_cmd():
        """Una tantum: deriva User.plan_type dal subscription_status esistente
        (che resta il gate di accesso invariato — vedi app/models/user.py).
        Idempotente: salta chi ha già plan_type valorizzato, rilanciabile
        senza effetti collaterali.

        ATTENZIONE azione fuori dal codice: "lifetime" diventa "appsumo_tier1"
        come pavimento provvisorio, perché AppSumoCode non ha mai avuto un
        campo tier prima di questa fase — non c'è modo di recuperare via
        query quali redenzioni storiche erano Tier 2/3. Vanno corrette a mano
        incrociando l'export vendite di AppSumo (email/codice → tier) prima
        del lancio dei limiti differenziati per tier."""
        from app.models import User

        mapping = {
            "trialing": "trial",
            "active": "subscription_monthly",
            "canceled": "subscription_monthly",
            "lifetime": "appsumo_tier1",
        }

        users = User.query.filter(User.plan_type.is_(None)).all()
        updated = 0
        for user in users:
            plan_type = mapping.get(user.subscription_status)
            if plan_type is None:
                continue
            user.plan_type = plan_type
            if plan_type in ("subscription_monthly",):
                user.billing_interval = "monthly"
            updated += 1
        db.session.commit()

        lifetime_count = sum(1 for u in users if u.subscription_status == "lifetime")
        print(f"plan_type impostato per {updated} utenti.")
        if lifetime_count:
            print(
                f"  {lifetime_count} utenti 'lifetime' impostati a appsumo_tier1 come "
                "pavimento provvisorio — correggi a mano i Tier 2/3 incrociando "
                "l'export vendite AppSumo prima di abilitare i limiti differenziati."
            )

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

    # users: piano/limiti tecnici (vedi app/entitlements/ e app/models/user.py).
    if has_column("users", "id") and not has_column("users", "plan_type"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN plan_type VARCHAR(30)"))
    if has_column("users", "id") and not has_column("users", "billing_interval"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN billing_interval VARCHAR(10)"))
    if has_column("users", "id") and not has_column("users", "grace_period_ends_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN grace_period_ends_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "ai_credit_balance"):
        with db.engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN ai_credit_balance INTEGER NOT NULL DEFAULT 0")
            )
    if has_column("users", "id") and not has_column("users", "heavy_user_flag"):
        default = "false" if dialect == "postgresql" else "0"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN heavy_user_flag BOOLEAN NOT NULL DEFAULT {default}"
                )
            )
    if has_column("users", "id") and not has_column("users", "heavy_user_flagged_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN heavy_user_flagged_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "white_label_enabled"):
        default = "false" if dialect == "postgresql" else "0"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN white_label_enabled BOOLEAN NOT NULL DEFAULT {default}"
                )
            )
    if has_column("users", "id") and not has_column("users", "appsumo_migration_unlocked"):
        default = "false" if dialect == "postgresql" else "0"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN appsumo_migration_unlocked BOOLEAN NOT NULL DEFAULT {default}"
                )
            )

    # users: colonne condivise da Paddle e dal (dismesso) canale Revolut
    # manuale — vedi app/models/user.py per il dettaglio campo per campo. Le
    # colonne ls_customer_id/ls_subscription_id restano dove sono, invariate,
    # per l'audit storico Lemon Squeezy.
    if has_column("users", "id") and not has_column("users", "subscription_expires_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "subscription_source"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN subscription_source VARCHAR(30)"))
    if has_column("users", "id") and not has_column("users", "subscription_activated_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN subscription_activated_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "subscription_activated_by_id"):
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN subscription_activated_by_id INTEGER "
                    "REFERENCES users(id)"
                )
            )
    if has_column("users", "id") and not has_column("users", "subscription_activation_reference"):
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN subscription_activation_reference VARCHAR(255)"
                )
            )
            # UNIQUE standard (non parziale): sia Postgres sia SQLite trattano
            # ogni NULL come distinto dagli altri, quindi più utenti senza
            # riferimento convivono senza violare il vincolo.
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_subscription_activation_reference "
                    "ON users (subscription_activation_reference)"
                )
            )

    # appsumo_codes.tier (1-3, vedi Fase 4 del piano multi-tier).
    if has_column("appsumo_codes", "id") and not has_column("appsumo_codes", "tier"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE appsumo_codes ADD COLUMN tier INTEGER"))

    # monitored_sites.last_synced_at — aggiunta qui e non solo via create_all()
    # perché la tabella nasce da create_all() ma questa colonna documenta il
    # significato "ultimo sync riuscito" fin dal principio; nessuna azione se
    # la tabella non esiste ancora (has_column ritorna False e basta).
    if has_column("monitored_sites", "id") and not has_column("monitored_sites", "last_synced_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE monitored_sites ADD COLUMN last_synced_at TIMESTAMPTZ"))

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

    # ai_credit_transactions: colonne per l'accredito dei top-up a pagamento
    # (Paddle, e storicamente Revolut manuale — vedi
    # app/models/ai_credit_transaction.py). ls_order_id/site_url restano dove
    # sono, invariate, per l'audit storico Lemon Squeezy.
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "balance_before"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN balance_before INTEGER"))
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "product_key"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN product_key VARCHAR(50)"))
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "payment_source"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN payment_source VARCHAR(30)"))
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "approved_by_user_id"):
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE ai_credit_transactions ADD COLUMN approved_by_user_id INTEGER "
                    "REFERENCES users(id)"
                )
            )
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "admin_note"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN admin_note TEXT"))
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "payment_reference"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN payment_reference VARCHAR(255)"))
            # UNIQUE standard (non parziale): più righe storiche senza
            # riferimento (NULL) convivono senza violare il vincolo — stessa
            # nota di ix_users_subscription_activation_reference sopra.
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_ai_credit_transactions_payment_reference "
                    "ON ai_credit_transactions (payment_reference)"
                )
            )
    # action (vedi app/entitlements/ai_credits.py::consume_credits e
    # app/models/ai_credit_transaction.py) — etichetta leggibile dello
    # storico crediti, popolata solo dai due punti reali che consumano
    # crediti (app/jobs/tasks.py).
    if has_column("ai_credit_transactions", "id") and not has_column("ai_credit_transactions", "action"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE ai_credit_transactions ADD COLUMN action VARCHAR(30)"))

    # audit_presentations.chart_data (vedi app/audits/charts.py) — JSON
    # serializzato come testo (stessa scelta di app/models/ai_credit_transaction.py
    # per admin_note ecc.: TEXT è portabile su Postgres e SQLite senza
    # ambiguità di tipo, la (de)serializzazione resta applicativa). NULL per
    # ogni presentazione generata prima di questa colonna — il rendering
    # mostra un fallback, non rigenera né consuma crediti.
    if has_column("audit_presentations", "id") and not has_column("audit_presentations", "chart_data"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE audit_presentations ADD COLUMN chart_data TEXT"))

    # users: integrazione Paddle Billing (vedi app/billing/paddle_client.py,
    # app/billing/paddle_subscriptions.py, docs/paddle-billing.md). Le
    # tabelle nuove (paddle_webhook_events, paddle_transactions) sono create
    # da db.create_all() sopra, non serve _ensure_columns per quelle — solo
    # per le colonne aggiunte a una tabella `users` già esistente.
    if has_column("users", "id") and not has_column("users", "paddle_customer_id"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN paddle_customer_id VARCHAR(255)"))
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_users_paddle_customer_id ON users (paddle_customer_id)")
            )
    if has_column("users", "id") and not has_column("users", "paddle_subscription_id"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN paddle_subscription_id VARCHAR(255)"))
            # UNIQUE standard (non parziale): stessa nota di
            # ix_users_subscription_activation_reference sopra — più utenti
            # senza subscription Paddle (NULL) convivono senza violare il
            # vincolo, su Postgres e SQLite.
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_paddle_subscription_id "
                    "ON users (paddle_subscription_id)"
                )
            )
    if has_column("users", "id") and not has_column("users", "paddle_price_id"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN paddle_price_id VARCHAR(255)"))
    if has_column("users", "id") and not has_column("users", "paddle_environment"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN paddle_environment VARCHAR(10)"))
    if has_column("users", "id") and not has_column("users", "current_period_ends_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN current_period_ends_at TIMESTAMPTZ"))
    if has_column("users", "id") and not has_column("users", "cancel_at_period_end"):
        default = "false" if dialect == "postgresql" else "0"
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN cancel_at_period_end BOOLEAN NOT NULL DEFAULT {default}"
                )
            )
    if has_column("users", "id") and not has_column("users", "last_paddle_sync_at"):
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_paddle_sync_at TIMESTAMPTZ"))
