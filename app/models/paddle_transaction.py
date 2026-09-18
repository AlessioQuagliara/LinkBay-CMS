from datetime import datetime, timezone

from app.extensions import db


class PaddleTransaction(db.Model):
    """Ledger di riconciliazione locale per ogni transazione Paddle, creata
    lato server al momento del checkout (status "pending") e chiusa dal
    webhook `transaction.completed`/`transaction.payment_failed` (vedi
    app/billing/paddle_transactions.py). `paddle_transaction_id` è UNIQUE —
    impedisce un doppio accredito se lo stesso evento arriva più volte.

    Per gli acquisti di crediti AI, questa tabella è un audit trail
    *aggiuntivo*: l'accredito vero passa comunque da
    app/entitlements/ai_credits.py::grant_credits, che scrive anche in
    AiCreditTransaction (payment_source="paddle", payment_reference=
    paddle_transaction_id) — stessa fonte di verità già usata dalla UI
    (/billing/credits), non duplicata. Per gli abbonamenti, l'accesso è
    invece guidato dagli eventi
    `subscription.*` (vedi app/models/user.py) — qui la riga resta solo
    audit/correlazione, non un secondo punto di scrittura dell'entitlement."""

    __tablename__ = "paddle_transactions"

    id = db.Column(db.Integer, primary_key=True)

    provider = db.Column(db.String(20), nullable=False, default="paddle")
    environment = db.Column(db.String(10), nullable=False)  # "sandbox" | "production"

    paddle_transaction_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    paddle_subscription_id = db.Column(db.String(255), nullable=True, index=True)
    paddle_customer_id = db.Column(db.String(255), nullable=True, index=True)

    # Nullable: una transazione può arrivare via webhook con un
    # custom_data.local_user_id non risolvibile (utente cancellato,
    # payload corrotto/legacy) — resta comunque tracciata per la
    # riconciliazione admin invece di essere scartata silenziosamente.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    # "subscription" | "ai_credits".
    purchase_type = db.Column(db.String(20), nullable=False)
    # "paddle_1m"/"paddle_3m"/"paddle_12m" (subscription) o
    # "ai_topup_starter"/"ai_topup_growth"/"ai_topup_scale" (ai_credits) —
    # vedi app/billing/paddle_products.py. Nullable: un price_id non
    # riconosciuto (fuori whitelist) non impedisce di tracciare la riga.
    internal_plan_key = db.Column(db.String(50), nullable=True)
    paddle_price_id = db.Column(db.String(255), nullable=True)

    amount = db.Column(db.String(20), nullable=True)  # importo grezzo Paddle (stringa, come nell'API), solo audit
    currency = db.Column(db.String(10), nullable=True)

    # "pending" (transazione creata dal checkout, in attesa di pagamento) |
    # "completed" | "failed" | "ignored" (custom_data/user non risolvibile).
    status = db.Column(db.String(20), nullable=False, default="pending")

    credits_granted = db.Column(db.Integer, nullable=True)  # solo per purchase_type == "ai_credits"

    # Correlazione checkout -> webhook, generata lato server al momento della
    # creazione (vedi app/billing/paddle_routes.py) e rispedita a Paddle in
    # custom_data — utile per il debug quando un event_id non basta a
    # ricostruire "quale richiesta ha originato questo".
    correlation_id = db.Column(db.String(64), nullable=True, index=True)

    # Riferimento minimizzato all'evento che ha chiuso la transazione (id
    # dell'evento in paddle_webhook_events, non il payload) — mai dati
    # personali o secret qui.
    completing_event_id = db.Column(db.String(255), nullable=True)

    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User")

    def __repr__(self):
        return f"<PaddleTransaction {self.paddle_transaction_id} status={self.status}>"
