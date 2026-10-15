import hashlib
from datetime import datetime, timezone

from app.extensions import db
from app.utils import aware


class PasswordResetToken(db.Model):
    """Token monouso per il recupero password, inviato come link via email.

    A differenza di EmailOtp (codice a 6 cifre digitato a mano, hashato con
    werkzeug/bcrypt perché a bassa entropia), qui il token è una stringa
    casuale ad alta entropia (32 byte, `secrets.token_urlsafe`) e serve a
    fare lookup diretto in DB: usiamo perciò uno SHA-256 deterministico
    (niente salt) invece dell'hash lento, altrimenti il lookup per token
    sarebbe impossibile (l'hash salato di werkzeug cambia ad ogni chiamata).
    L'entropia del token rende comunque il lookup sicuro contro brute-force.
    """

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    consumed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User")

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


    def is_expired(self):
        return datetime.now(timezone.utc) > aware(self.expires_at)
