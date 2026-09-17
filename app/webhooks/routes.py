"""Riceve i webhook Paddle (POST /webhooks/paddle) — l'unico punto che può
concedere/estendere accesso o accreditare crediti per un utente Paddle (mai
il callback client-side del checkout, vedi app/billing/paddle_routes.py).

Contratto di idempotenza/retry (vedi anche il modello PaddleWebhookEvent):
- firma invalida -> 400, NESSUN side effect, nessuna riga scritta;
- firma valida + event_id già visto -> 200 immediato, nessun reprocessing;
- firma valida + evento nuovo, processato (anche se l'esito applicativo è
  "ignored": custom_data invalido, utente non trovato, price_id sconosciuto
  — sono esiti di business legittimi, non errori tecnici) -> UNA sola
  transazione DB che scrive insieme la riga PaddleWebhookEvent e ogni
  effetto collaterale (User, AiCreditTransaction, PaddleTransaction), poi
  200;
- firma valida + eccezione imprevista (bug, DB down, ecc.) -> rollback
  completo (nessuna riga resta scritta, l'event_id NON risulta "già visto"),
  500 -> Paddle ritenterà più tardi e il retry riparte da zero, senza
  duplicati residui a bloccarlo."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from app.billing.paddle_client import get_environment, verify_webhook_signature
from app.billing.paddle_subscriptions import apply_subscription_event
from app.billing.paddle_transactions import apply_transaction_completed, apply_transaction_payment_failed
from app.extensions import csrf, db
from app.models import PaddleWebhookEvent

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/webhooks")
# Paddle non manda (e non può conoscere) un CSRF token di sessione — questo
# endpoint si autentica con la firma HMAC (verify_webhook_signature), non
# con i cookie di sessione: CSRFProtect globale (app/extensions.py) non si
# applica a una richiesta server-to-server senza cookie di sessione.
csrf.exempt(webhooks_bp)

SUBSCRIPTION_EVENT_TYPES = {
    "subscription.created",
    "subscription.updated",
    "subscription.activated",
    "subscription.past_due",
    "subscription.paused",
    "subscription.resumed",
    "subscription.canceled",
}


def _parse_occurred_at(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@webhooks_bp.route("/paddle", methods=["POST"])
def paddle_webhook():
    # cache=True (default): il raw body va letto UNA volta e riusato sia per
    # la verifica della firma sia dal successivo request.get_json() — con
    # cache=False lo stream WSGI risulterebbe già esaurito al secondo
    # accesso e get_json() vedrebbe un body vuoto.
    raw_body = request.get_data()
    signature_header = request.headers.get("Paddle-Signature")
    secret = current_app.config.get("PADDLE_WEBHOOK_SECRET")

    if not verify_webhook_signature(raw_body, signature_header, secret):
        current_app.logger.warning("Webhook Paddle rifiutato: firma mancante o non valida.")
        return jsonify(error="invalid_signature"), 400

    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:  # noqa: BLE001 — body non JSON valido nonostante firma corretta
        current_app.logger.warning("Webhook Paddle: firma valida ma body non è JSON valido.")
        return jsonify(error="invalid_json"), 400

    if not isinstance(payload, dict):
        return jsonify(error="malformed_payload"), 400

    event_id = payload.get("event_id")
    event_type = payload.get("event_type")
    data = payload.get("data") or {}
    occurred_at = _parse_occurred_at(payload.get("occurred_at"))

    if not event_id or not event_type:
        current_app.logger.warning("Webhook Paddle: payload firmato ma senza event_id/event_type.")
        return jsonify(error="malformed_payload"), 400

    existing = PaddleWebhookEvent.query.filter_by(event_id=event_id).first()
    if existing is not None:
        return jsonify(status="duplicate"), 200

    environment = get_environment()
    event_row = PaddleWebhookEvent(
        event_id=event_id,
        event_type=event_type,
        environment=environment,
        occurred_at=occurred_at,
        payload_hash=hashlib.sha256(raw_body).hexdigest(),
    )

    try:
        if event_type in SUBSCRIPTION_EVENT_TYPES:
            result = apply_subscription_event(
                event_type=event_type, data=data, environment=environment, event_occurred_at=occurred_at
            )
            event_row.paddle_subscription_id = data.get("id")
            event_row.paddle_customer_id = data.get("customer_id")
            event_row.status = "processed" if result.outcome == "applied" else "ignored"
            if result.outcome != "applied":
                event_row.error_message = result.reason

        elif event_type == "transaction.completed":
            result = apply_transaction_completed(data=data, environment=environment, completing_event_id=event_id)
            event_row.paddle_transaction_id = data.get("id")
            event_row.paddle_customer_id = data.get("customer_id")
            event_row.status = "processed" if result.outcome in ("completed", "already_completed") else "ignored"
            if event_row.status == "ignored":
                event_row.error_message = result.reason

        elif event_type == "transaction.payment_failed":
            result = apply_transaction_payment_failed(
                data=data, environment=environment, completing_event_id=event_id
            )
            event_row.paddle_transaction_id = data.get("id")
            event_row.paddle_customer_id = data.get("customer_id")
            event_row.status = "processed"

        else:
            # Tipo di evento non gestito da questo prodotto (es. address.*,
            # business.*, payout.*) — registrato per audit/idempotenza,
            # nessun side effect applicativo.
            event_row.status = "ignored"
            event_row.error_message = "event_type non gestito"

        event_row.processed_at = datetime.now(timezone.utc)
        db.session.add(event_row)
        db.session.commit()
    except Exception:
        # Rollback completo: NESSUNA riga resta scritta (vedi contratto nel
        # docstring del modulo) — un retry di Paddle riparte da zero.
        db.session.rollback()
        current_app.logger.exception(
            "Errore imprevisto processando il webhook Paddle %s (event_id=%s).", event_type, event_id
        )
        return jsonify(error="processing_failed"), 500

    return jsonify(status="ok"), 200
