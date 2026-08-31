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

    # Tier 1/2/3 del deal AppSumo (vedi piano multi-tier) — nullable perché i
    # codici importati prima dell'introduzione dei tier multipli non hanno un
    # valore recuperabile via query; vanno corretti a mano incrociando
    # l'export vendite di AppSumo. La redenzione (app/billing/routes.py)
    # rifiuta un codice con tier NULL.
    tier = db.Column(db.Integer, nullable=True)

    redeemed_by = db.relationship("User")

    @property
    def is_redeemed(self):
        return self.redeemed_at is not None
