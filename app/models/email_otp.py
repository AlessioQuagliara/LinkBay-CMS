from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class EmailOtp(db.Model):
    """Codice OTP monouso inviato via email per verificare login e
    registrazione. Il codice in chiaro non viene mai salvato: teniamo solo il
    suo hash, esattamente come per le password. C'è al più un OTP attivo per
    (utente, scopo): quando se ne emette uno nuovo, i precedenti vengono
    rimossi (vedi app/auth/otp.py)."""

    __tablename__ = "email_otps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # "login" o "register": lo scopo per cui il codice è stato emesso.
    purpose = db.Column(db.String(20), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    consumed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User")

    def set_code(self, code):
        self.code_hash = generate_password_hash(code)

    def check_code(self, code):
        return check_password_hash(self.code_hash, code)

    def _aware(self, dt):
        # I timestamp letti da SQLite tornano naive: li normalizziamo a UTC per
        # poterli confrontare con datetime.now(timezone.utc). Su Postgres sono
        # già timezone-aware e questa resta una no-op.
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def is_expired(self):
        return datetime.now(timezone.utc) > self._aware(self.expires_at)

    @property
    def consumed(self):
        return self.consumed_at is not None
