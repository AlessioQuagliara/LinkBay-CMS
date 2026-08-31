from datetime import datetime, timezone

from app.extensions import db


class AiCreditTransaction(db.Model):
    """Registro di ogni movimento di crediti AI — fonte di verità per
    l'audit; `User.ai_credit_balance` è una copia denormalizzata per letture
    veloci, aggiornata sempre in coppia con un inserimento qui (mai scritta
    altrove, vedi app/entitlements/ai_credits.py)."""

    __tablename__ = "ai_credit_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # "grant_purchase" (pacchetto acquistato) | "grant_monthly_quota" (quota
    # mensile inclusa nel piano) | "consume" (run AI) | "adjustment" (storno
    # manuale/rimborso).
    type = db.Column(db.String(20), nullable=False)

    # Positivo per un accredito, negativo per un consumo/storno.
    amount = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)

    # Valorizzato solo per le transazioni "grant_purchase" — permette di
    # risalire dall'ordine Lemon Squeezy alla transazione in caso di
    # order_refunded (vedi app/billing/routes.py::webhook).
    ls_order_id = db.Column(db.String(255), nullable=True, index=True)
    site_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User")

    def __repr__(self):
        return f"<AiCreditTransaction user_id={self.user_id} type={self.type} amount={self.amount}>"
