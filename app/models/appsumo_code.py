from datetime import datetime, timezone

from app.extensions import db


class AppSumoCode(db.Model):
    """Codice di riscatto per l'offerta lifetime su AppSumo. I codici si
    caricano in blocco con `flask import-appsumo-codes <file>` (un codice per
    riga); l'utente li riscatta da /billing/redeem, che porta
    User.subscription_status a "lifetime" (vedi app/billing/routes.py)."""

    __tablename__ = "appsumo_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    redeemed_at = db.Column(db.DateTime(timezone=True))
    redeemed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    redeemed_by = db.relationship("User")

    @property
    def is_redeemed(self):
        return self.redeemed_at is not None
