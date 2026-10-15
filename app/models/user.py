from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    """Un cliente che si registra dalla landing e usa il software.
    Tutto lo storico dell'app va agganciato a questo modello (via user_id)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Diventa True dopo che l'utente ha inserito il codice OTP ricevuto via
    # email in fase di registrazione. Il login richiede comunque un OTP ogni
    # volta (2FA email), a prescindere da questo flag.
    email_verified = db.Column(db.Boolean, nullable=False, default=False)

    # Non è RBAC: un solo flag per distinguere il team (accesso a Flask-Admin)
    # dai clienti normali. Si imposta con `python3 -m flask make-admin <email>`.
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    # Lingua preferita ("en" | "it"), modificabile da Settings. Vedi
    # app/i18n.py::get_locale per come viene scelta a ogni richiesta.
    locale = db.Column(db.String(5), nullable=False, default="en")

    # Digest email del lunedì con le top declining pages, modificabile da
    # Settings. Inviata solo a chi ha has_active_access pagante (vedi
    # app/emails/digest.py) — questo flag decide solo l'opt-out personale.
    weekly_digest_enabled = db.Column(db.Boolean, nullable=False, default=True)

    # Trial di 14 giorni senza carta, impostato alla registrazione (vedi
    # app/auth/routes.py::register). Scaduto il trial senza un abbonamento
    # attivo, app/billing/access.py blocca l'accesso alla app.
    trial_ends_at = db.Column(db.DateTime(timezone=True))
    # "trialing" | "active" | "past_due" | "paused" | "canceled" | "lifetime".
    # "active" è impostato dal webhook Paddle
    # `subscription.activated`/`subscription.updated` per subscription_source
    # == "paddle" (vedi app/billing/paddle_subscriptions.py — scadenza in
    # subscription_expires_at), o storicamente dall'attivazione manuale
    # Revolut (canale dismesso, nessun codice la scrive più). "lifetime" è
    # impostato una tantum al riscatto di un codice AppSumo (vedi
    # app/models/appsumo_code.py) e non scade mai. "paused" è impostato dal
    # webhook Paddle `subscription.paused`. "past_due"/"canceled" sono sia
    # stati legacy Lemon Squeezy (nessun codice nuovo li assegna più per
    # quella fonte) sia stati Paddle reali per subscription_source ==
    # "paddle" — has_active_access/has_active_entitlement li interpretano
    # diversamente in base a subscription_source (vedi sotto e
    # app/entitlements/service.py::has_active_entitlement).
    subscription_status = db.Column(db.String(20), nullable=False, default="trialing")

    # Legacy Lemon Squeezy (dismesso dal flusso commerciale — vedi
    # app/billing/paddle_products.py per il flusso attuale). Colonne
    # mantenute nullable e silenti per non perdere l'audit storico di chi ha
    # pagato via Lemon Squeezy; nessun codice le scrive più.
    ls_customer_id = db.Column(db.String(255))
    ls_subscription_id = db.Column(db.String(255))

    # Scadenza dell'abbonamento — unica per tutti i piani "active"/"past_due"/
    # "paused" a termine, sia legacy Revolut manuale sia Paddle. Per Paddle è
    # lo specchio di subscription.current_billing_period.ends_at, riscritto a
    # ogni webhook subscription.* (vedi app/billing/paddle_subscriptions.py)
    # ed è il fallback locale usato quando Paddle non è raggiungibile (vedi
    # app/entitlements/service.py::has_active_entitlement). NULL = nessuna
    # scadenza nota: per i piani lifetime/legacy copre un utente non ancora
    # attivato (has_active_access non blocca, comportamento preesistente per
    # Lemon Squeezy legacy) — per subscription_source == "paddle" invece NULL
    # NON concede mai accesso (has_active_entitlement tratta i due casi in
    # modo diverso: Paddle imposta sempre questo campo a ogni sync riuscito,
    # NULL lì significa "mai sincronizzato", non "nessun limite").
    subscription_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Provenienza dell'ultima attivazione: "appsumo" | "paddle" |
    # "legacy_lemonsqueezy" | "revolut_manual" (canale dismesso, valore
    # storico). NON solo informativo/audit come prima
    # di Paddle: has_active_entitlement lo usa per decidere quale semantica
    # di scadenza applicare (vedi sopra) — has_active_access (il property
    # legacy, invariato) resta invece guidato solo da subscription_status +
    # subscription_expires_at, per non rompere i test/consumer esistenti.
    # Mai backfillato per gli utenti storici: resta NULL finché non ricevono
    # una prima attivazione tracciata da qui.
    subscription_source = db.Column(db.String(30), nullable=True)

    # Audit minimo dell'ultima attivazione manuale Revolut — canale dismesso,
    # colonne mantenute solo per l'audit storico di chi fu attivato così.
    # activated_by è nullable: un utente mai attivato manualmente non ha né
    # data né admin.
    subscription_activated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    subscription_activated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Riferimento pagamento del vecchio flusso Revolut manuale (canale
    # dismesso) — univoco quando valorizzato, manteneva idempotente una
    # doppia sottomissione dello stesso pagamento. Colonna mantenuta solo per
    # l'audit storico; nessun codice la scrive più.
    subscription_activation_reference = db.Column(db.String(255), nullable=True, unique=True)

    subscription_activated_by = db.relationship("User", remote_side=[id])

    # --- Paddle Billing (vedi app/billing/paddle_client.py,
    # app/billing/paddle_subscriptions.py, docs/paddle-billing.md) ----------
    # Scritti SOLO dal webhook verificato (mai dal callback client-side del
    # checkout) — vedi app/webhooks/routes.py. Tutti nullable: un utente che
    # non ha mai avviato un checkout Paddle non li ha.

    # Customer Paddle — stabile per utente, non cambia tra un abbonamento e
    # l'altro (utile per aprire la customer portal — vedi
    # app/billing/paddle_client.py::create_customer_portal_session).
    paddle_customer_id = db.Column(db.String(255), nullable=True, index=True)
    # Subscription Paddle corrente — UNIQUE: due utenti non possono mai
    # condividere lo stesso subscription_id (garanzia DB, non solo applicativa).
    paddle_subscription_id = db.Column(db.String(255), nullable=True, unique=True)
    # Price ID dell'ultimo evento subscription.* applicato — audit/debug, per
    # capire a colpo d'occhio quale piano Paddle sta pagando senza dover
    # risalire da plan_type (che è la chiave interna, non l'id Paddle).
    paddle_price_id = db.Column(db.String(255), nullable=True)
    # "sandbox" | "production" — dell'ULTIMO evento applicato. Mai letto per
    # decidere il comportamento del codice (quello lo decide solo
    # PADDLE_ENVIRONMENT, vedi app/billing/paddle_client.py): serve solo a
    # rendere ispezionabile da un admin se una riga è di test o reale, utile
    # in fase di migrazione sandbox -> production.
    paddle_environment = db.Column(db.String(10), nullable=True)
    # Specchio esatto di subscription.current_billing_period.ends_at
    # dell'ultimo evento applicato — a differenza di subscription_expires_at
    # (che è anche il fallback di accesso, vedi sopra) questo campo non è mai
    # riletto da has_active_entitlement: è solo il valore grezzo Paddle per
    # audit/riconciliazione, anche quando differisse per policy locale.
    current_period_ends_at = db.Column(db.DateTime(timezone=True), nullable=True)
    # True se l'utente ha già programmato la cancellazione a fine periodo
    # (subscription.scheduled_change.action == "cancel") — l'accesso resta
    # comunque valido fino a subscription_expires_at, questo flag è solo per
    # mostrare "si cancellerà il ..." nella UI (vedi billing.subscription).
    cancel_at_period_end = db.Column(db.Boolean, nullable=False, default=False)
    # Timestamp dell'ULTIMO EVENTO PADDLE applicato (il suo `occurred_at`,
    # tempo lato Paddle — non l'ora reale di processing sul nostro server),
    # o l'ora di wall-clock per una riconciliazione admin (che non ha un
    # occurred_at, vedi app/billing/paddle_reconciliation.py). Doppio ruolo,
    # entrambi in app/billing/paddle_subscriptions.py: (1) guardia
    # anti-out-of-order — un evento con occurred_at <= questo valore è
    # considerato superato e ignorato; (2) per capire a colpo d'occhio in
    # admin se un utente Paddle "non riceve più eventi da un po'"
    # (candidato a riconciliazione manuale).
    last_paddle_sync_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Piano/tier per i limiti tecnici (app/entitlements/) — ORTOGONALE a
    # subscription_status: quest'ultimo risponde "ha accesso ora?" (gate
    # binario usato da app/billing/access.py, invariato), plan_type risponde
    # "quali limiti si applicano?". Valori: "trial" | "subscription_monthly"
    # | "subscription_annual" (legacy Lemon Squeezy, non più assegnabili a
    # utenti nuovi) | "revolut_1m" | "revolut_3m" | "revolut_12m" (legacy,
    # canale Revolut dismesso, non più assegnabili a utenti nuovi) |
    # "paddle_1m" | "paddle_3m" | "paddle_12m" (stessi limiti/prezzi dei tre
    # piani legacy equivalenti, vedi app/billing/paddle_products.py) |
    # "appsumo_tier1" | "appsumo_tier2" |
    # "appsumo_tier3". NULL ricade su "trial" (vedi
    # app/entitlements/service.py::get_plan_limits).
    plan_type = db.Column(db.String(30), nullable=True)
    billing_interval = db.Column(db.String(10), nullable=True)  # "monthly" | "annual" | None

    # Periodo di grazia dopo un pagamento fallito — legacy Lemon Squeezy: era
    # scritto da un webhook subscription_payment_failed rimosso insieme al
    # resto dell'integrazione. Nessun codice nuovo lo scrive più: Paddle non
    # ha un equivalente qui — un `subscription.
    # past_due` Paddle NON estende l'accesso oltre subscription_expires_at
    # (nessuna policy di grace period definita per Paddle, vedi
    # app/billing/paddle_subscriptions.py e docs/paddle-billing.md). Resta
    # letto da has_active_access per non rompere gli utenti legacy che
    # l'avevano già valorizzato.
    grace_period_ends_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Saldo crediti AI denormalizzato (letture veloci) — il registro delle
    # transazioni è AiCreditTransaction, fonte di verità per l'audit; questo
    # campo va sempre aggiornato in coppia con un inserimento nel ledger, mai
    # scritto direttamente altrove (vedi app/entitlements/ai_credits.py).
    ai_credit_balance = db.Column(db.Integer, nullable=False, default=0)

    # Flag di monitoraggio costi infrastrutturali (utenti che consumano
    # molto più della norma) — calcolato periodicamente da un job, non
    # editabile dall'utente. Vedi app/entitlements/heavy_user.py.
    heavy_user_flag = db.Column(db.Boolean, nullable=False, default=False)
    heavy_user_flagged_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # White label sugli export PDF/CSV — onorato solo se il piano dell'utente
    # lo consente (PlanLimits.white_label); il toggle da solo non basta.
    white_label_enabled = db.Column(db.Boolean, nullable=False, default=False)

    # Escape hatch per la migrazione controllata AppSumo→abbonamento: un
    # utente appsumo_* non può auto-servirsi da /billing/checkout finché
    # questo flag non viene attivato a mano dal supporto (Flask-Admin), dopo
    # una conversazione — mai da un bottone self-service.
    appsumo_migration_unlocked = db.Column(db.Boolean, nullable=False, default=False)

    gsc_connection = db.relationship(
        "GscConnection", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def _aware(self, dt):
        # I timestamp letti da SQLite tornano naive: li normalizziamo a UTC per
        # poterli confrontare con datetime.now(timezone.utc). Su Postgres sono
        # già timezone-aware e questa resta una no-op. Stesso pattern di
        # EmailOtp._aware (app/models/email_otp.py).
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @property
    def has_active_access(self):
        # "lifetime" (AppSumo) non scade mai — invariato, nessuna dipendenza
        # da subscription_expires_at.
        if self.subscription_status == "lifetime":
            return True
        if self.subscription_status == "active":
            # subscription_expires_at guida la scadenza dei piani a termine
            # (oggi solo utenti storici del canale Revolut dismesso). NULL
            # copre gli abbonamenti "active" legacy Lemon Squeezy, mai spenti
            # da questa migrazione: restano attivi finché non li tocca un
            # admin, invece di essere bloccati di colpo per l'assenza di un
            # dato che non avevano mai avuto.
            expires_at = self._aware(self.subscription_expires_at)
            if expires_at is None:
                return True
            return datetime.now(timezone.utc) < expires_at
        if self.subscription_status == "trialing" and self.trial_ends_at:
            return datetime.now(timezone.utc) < self._aware(self.trial_ends_at)
        if self.subscription_status == "past_due" and self.grace_period_ends_at:
            return datetime.now(timezone.utc) < self._aware(self.grace_period_ends_at)
        return False

    @property
    def trial_days_left(self):
        if self.subscription_status != "trialing" or not self.trial_ends_at:
            return 0
        delta = self._aware(self.trial_ends_at) - datetime.now(timezone.utc)
        return max(0, delta.days + (1 if delta.seconds else 0))

    def __repr__(self):
        return f"<User {self.email}>"
