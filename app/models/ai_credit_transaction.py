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

    # Azione AI che ha consumato i crediti — solo per type == "consume":
    # "ai_analysis" | "audit_presentation" (gli unici due punti che oggi
    # chiamano consume_credits, vedi app/jobs/tasks.py). NULL per le righe
    # precedenti a questa colonna e per ogni altro type: non un'etichetta
    # inventata, riflette esattamente cosa il codice sa davvero al momento
    # del consumo (vedi app/entitlements/service.py::get_ai_credit_overview
    # e la tabella storico in app/templates/billing/credits.html).
    action = db.Column(db.String(30), nullable=True)

    # Legacy Lemon Squeezy (integrazione dismessa — vedi
    # app/billing/paddle_products.py per il flusso attuale). Valorizzato solo
    # per le vecchie transazioni "grant_purchase"/"adjustment"; nessun codice
    # nuovo lo scrive più, mantenuto nullable e silenzioso per l'audit
    # storico (mai riusato dai flussi successivi, vedi payment_source).
    ls_order_id = db.Column(db.String(255), nullable=True, index=True)
    site_url = db.Column(db.String(500), nullable=True)

    # --- Top-up a pagamento (Paddle, e storicamente Revolut manuale) -------

    # Saldo prima dell'accredito — solo per le transazioni "grant_purchase"
    # a pagamento: balance_after da solo non distingue "quanto è cambiato" a
    # colpo d'occhio nell'audit. Non retroattivo sullo storico Lemon Squeezy
    # (resta NULL lì, ricostruibile comunque da amount/balance_after in
    # sequenza se mai servisse).
    balance_before = db.Column(db.Integer, nullable=True)

    # Chiave stabile del pacchetto (vedi
    # app/billing/paddle_products.py::PADDLE_CREDIT_PACKAGES) — distinta dal
    # vecchio "credits_<amount>" di Lemon Squeezy, mai riusata per non
    # confondere i due flussi in report/audit.
    product_key = db.Column(db.String(50), nullable=True)

    # Riferimento pagamento (paddle_transaction_id per Paddle, o storicamente
    # il riferimento inserito a mano dall'admin per il canale Revolut
    # dismesso) — univoco fra TUTTI i top-up (qualunque utente): è il perno
    # dell'idempotenza (vedi app/billing/paddle_transactions.py).
    payment_reference = db.Column(db.String(255), nullable=True, unique=True)
    # "paddle" | "revolut_manual" (canale dismesso, valore storico) |
    # "legacy_lemonsqueezy" (mai backfillato sullo storico: resta NULL per le
    # righe precedenti a questa migrazione).
    payment_source = db.Column(db.String(30), nullable=True)

    approved_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_note = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User", foreign_keys=[user_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_user_id])

    def __repr__(self):
        return f"<AiCreditTransaction user_id={self.user_id} type={self.type} amount={self.amount}>"
