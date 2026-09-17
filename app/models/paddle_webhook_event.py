from datetime import datetime, timezone

from app.extensions import db


class PaddleWebhookEvent(db.Model):
    """Audit + idempotenza per ogni evento webhook Paddle ricevuto.
    `event_id` (l'id che Paddle assegna all'evento, non alla risorsa) è
    UNIQUE: è la difesa primaria contro il doppio processing di una consegna
    duplicata/ritentata (vedi app/webhooks/routes.py).

    Una riga viene scritta SOLO dopo che la firma è stata verificata — un
    webhook con firma invalida non lascia traccia qui (vedi
    app/billing/paddle_client.py::verify_webhook_signature). Non contiene mai
    il payload completo: solo identificatori per il cross-reference e un
    hash per rilevare un eventuale replay con corpo alterato ma stesso
    event_id (che comunque la firma già impedirebbe — difesa in profondità)."""

    __tablename__ = "paddle_webhook_events"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    environment = db.Column(db.String(10), nullable=False)  # "sandbox" | "production"

    # Quando Paddle dice che l'evento è avvenuto (`occurred_at` nel payload)
    # vs quando lo abbiamo processato qui — utile per misurare il ritardo di
    # consegna e per il confronto anti-out-of-order (vedi
    # app/billing/paddle_subscriptions.py).
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=True)
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # "processed" (side effect applicati con successo) | "ignored" (evento
    # valido ma non applicabile — es. custom_data invalido, price_id
    # sconosciuto, utente AppSumo lifetime protetto) | "failed" (errore
    # imprevisto — riga MAI scritta in questo caso: vedi la nota su
    # commit/rollback in app/webhooks/routes.py, "failed" resta qui solo per
    # completezza di enum, non è mai il valore committato).
    status = db.Column(db.String(20), nullable=False)

    paddle_customer_id = db.Column(db.String(255), nullable=True, index=True)
    paddle_subscription_id = db.Column(db.String(255), nullable=True, index=True)
    paddle_transaction_id = db.Column(db.String(255), nullable=True, index=True)

    payload_hash = db.Column(db.String(64), nullable=True)  # sha256 hex del raw body
    error_message = db.Column(db.Text, nullable=True)  # sanitizzato, mai un secret

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<PaddleWebhookEvent {self.event_type} id={self.event_id} status={self.status}>"
