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
    # "trialing" | "active" | "canceled" | "lifetime". "active"/"canceled"
    # sono aggiornati dai webhook Lemon Squeezy (app/billing/routes.py).
    # "lifetime" è impostato una tantum al riscatto di un codice AppSumo
    # (app/models/appsumo_code.py) e non scade mai. Niente stato "past_due":
    # qualunque cosa diversa da "active"/"lifetime" durante l'abbonamento
    # viene trattata come non pagante (blocco netto).
    subscription_status = db.Column(db.String(20), nullable=False, default="trialing")
    ls_customer_id = db.Column(db.String(255))
    ls_subscription_id = db.Column(db.String(255))

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
        if self.subscription_status in ("active", "lifetime"):
            return True
        if self.subscription_status == "trialing" and self.trial_ends_at:
            return datetime.now(timezone.utc) < self._aware(self.trial_ends_at)
        return False

    @property
    def trial_days_left(self):
        if self.subscription_status != "trialing" or not self.trial_ends_at:
            return 0
        delta = self._aware(self.trial_ends_at) - datetime.now(timezone.utc)
        return max(0, delta.days + (1 if delta.seconds else 0))

    def __repr__(self):
        return f"<User {self.email}>"
