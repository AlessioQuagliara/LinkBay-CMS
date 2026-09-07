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
    # "trialing" | "active" | "past_due" | "canceled" | "lifetime".
    # "active" è impostato dall'attivazione manuale Revolut (vedi
    # app/billing/revolut_manual_activation.py — scadenza in
    # subscription_expires_at, non più webhook-driven). "lifetime" è
    # impostato una tantum al riscatto di un codice AppSumo (vedi
    # app/models/appsumo_code.py) e non scade mai. "past_due"/"canceled" sono
    # stati legacy Lemon Squeezy: nessun codice nuovo li assegna più (il
    # webhook che li scriveva è stato rimosso), ma restano gestiti da
    # has_active_access per non rompere gli utenti che li avevano già.
    subscription_status = db.Column(db.String(20), nullable=False, default="trialing")

    # Legacy Lemon Squeezy (dismesso dal flusso commerciale — vedi
    # app/billing/revolut_manual_activation.py per il flusso attuale).
    # Colonne mantenute nullable e silenti per non perdere l'audit storico di
    # chi ha pagato via Lemon Squeezy; nessun codice le scrive più.
    ls_customer_id = db.Column(db.String(255))
    ls_subscription_id = db.Column(db.String(255))

    # Scadenza dell'abbonamento — unica per tutti i piani "active" a termine
    # (oggi solo Revolut manuale). NULL = nessuna scadenza nota, che copre sia
    # i piani lifetime/legacy sia un utente non ancora attivato: vedi
    # has_active_access, che in quel caso non blocca (comportamento
    # preesistente per gli abbonamenti Lemon Squeezy legacy, mai spento qui).
    subscription_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Provenienza dell'ultima attivazione: "revolut_manual" | "appsumo" |
    # "legacy_lemonsqueezy". Solo informativo/audit — NON è letto da
    # has_active_access (quello resta guidato da subscription_status +
    # subscription_expires_at). Mai backfillato per gli utenti storici: resta
    # NULL finché non ricevono una prima attivazione tracciata da qui.
    subscription_source = db.Column(db.String(30), nullable=True)

    # Audit minimo dell'ultima attivazione manuale Revolut (vedi
    # app/billing/revolut_manual_activation.py). activated_by è nullable: un
    # utente non ancora attivato manualmente non ha né data né admin.
    subscription_activated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    subscription_activated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Riferimento pagamento Revolut (facoltativo, inserito a mano
    # dall'admin) — univoco quando valorizzato: usato per rendere idempotente
    # una doppia sottomissione dello stesso pagamento (vedi
    # revolut_manual_activation.activate_revolut_subscription). Non è uno
    # storico completo: una riattivazione successiva sovrascrive il valore
    # precedente, vedi il modulo del service per il compromesso accettato.
    subscription_activation_reference = db.Column(db.String(255), nullable=True, unique=True)

    subscription_activated_by = db.relationship("User", remote_side=[id])

    # Piano/tier per i limiti tecnici (app/entitlements/) — ORTOGONALE a
    # subscription_status: quest'ultimo risponde "ha accesso ora?" (gate
    # binario usato da app/billing/access.py, invariato), plan_type risponde
    # "quali limiti si applicano?". Valori: "trial" | "subscription_monthly"
    # | "subscription_annual" (legacy Lemon Squeezy, non più assegnabili a
    # utenti nuovi) | "revolut_1m" | "revolut_3m" | "revolut_12m" (vedi
    # app/billing/revolut_manual_activation.py) | "appsumo_tier1" |
    # "appsumo_tier2" | "appsumo_tier3". NULL per utenti non ancora migrati —
    # vedi `flask backfill-plan-type` e
    # app/entitlements/service.py::get_plan_limits (fallback sicuro a "trial"
    # se NULL).
    plan_type = db.Column(db.String(30), nullable=True)
    billing_interval = db.Column(db.String(10), nullable=True)  # "monthly" | "annual" | None

    # Periodo di grazia dopo un pagamento fallito (subscription_payment_failed,
    # vedi app/billing/routes.py::webhook) prima di revocare l'accesso.
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
            # (oggi solo Revolut manuale, vedi
            # app/billing/revolut_manual_activation.py). NULL copre gli
            # abbonamenti "active" legacy Lemon Squeezy, mai spenti da questa
            # migrazione: restano attivi finché non li tocca un admin, invece
            # di essere bloccati di colpo per l'assenza di un dato che non
            # avevano mai avuto.
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
