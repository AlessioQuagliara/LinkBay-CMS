"""Applica gli eventi webhook `transaction.*` di Paddle — crea/aggiorna la
riga di audit in PaddleTransaction e, SOLO per gli acquisti di crediti AI,
accredita il ledger reale (app/entitlements/ai_credits.py::grant_credits).
Per gli abbonamenti, `transaction.completed`
resta solo audit: l'accesso è concesso dagli eventi `subscription.*` (vedi
app/billing/paddle_subscriptions.py), mai da qui — un `transaction.completed`
può arrivare per il primo pagamento di un abbonamento, ma seguirlo per
concedere accesso duplicherebbe una decisione che spetta solo al ciclo di
vita della subscription."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.billing.paddle_products import PADDLE_CREDIT_PACKAGES, reverse_lookup_credit_package
from app.entitlements.ai_credits import grant_credits
from app.entitlements.service import get_plan_limits
from app.extensions import db
from app.models import PaddleTransaction, User


@dataclass(frozen=True)
class TransactionApplyResult:
    outcome: str  # "completed" | "already_completed" | "ignored_no_user" | "ignored_ineligible" | "failed_recorded"
    reason: str | None = None
    user_id: int | None = None
    credits_granted: int | None = None


def _resolve_user(data: dict) -> User | None:
    custom_data = data.get("custom_data") or {}
    local_user_id = custom_data.get("local_user_id")
    if local_user_id is None:
        return None
    try:
        return db.session.get(User, int(local_user_id))
    except (TypeError, ValueError):
        return None


def _get_or_create_row(*, transaction_id: str, environment: str) -> PaddleTransaction:
    row = PaddleTransaction.query.filter_by(paddle_transaction_id=transaction_id).first()
    if row is None:
        row = PaddleTransaction(
            paddle_transaction_id=transaction_id, environment=environment, purchase_type="unknown", status="pending"
        )
        db.session.add(row)
    return row


def apply_transaction_completed(
    *, data: dict, environment: str, completing_event_id: str | None
) -> TransactionApplyResult:
    transaction_id = data.get("id")
    if not transaction_id:
        return TransactionApplyResult(outcome="ignored_no_user", reason="transazione senza id")

    row = _get_or_create_row(transaction_id=transaction_id, environment=environment)

    # Difesa in profondità, oltre all'idempotenza a livello di event_id in
    # PaddleWebhookEvent (vedi app/webhooks/routes.py) — se questa riga è
    # già "completed", non rifare mai l'accredito.
    if row.status == "completed":
        return TransactionApplyResult(
            outcome="already_completed", user_id=row.user_id, credits_granted=row.credits_granted
        )

    custom_data = data.get("custom_data") or {}
    purchase_type = custom_data.get("purchase_type")
    internal_plan_key = custom_data.get("internal_plan_key")
    subscription_id = data.get("subscription_id")
    customer_id = data.get("customer_id")

    items = data.get("items") or []
    price_id = (items[0].get("price") or {}).get("id") if items else None
    totals = data.get("details", {}).get("totals", {}) if isinstance(data.get("details"), dict) else {}

    row.paddle_subscription_id = subscription_id
    row.paddle_customer_id = customer_id
    row.paddle_price_id = price_id
    row.purchase_type = purchase_type or ("subscription" if subscription_id else "unknown")
    row.internal_plan_key = internal_plan_key
    row.amount = totals.get("total")
    row.currency = data.get("currency_code")
    row.correlation_id = custom_data.get("correlation_id")
    row.completing_event_id = completing_event_id

    user = _resolve_user(data)
    if user is not None:
        row.user_id = user.id

    if row.purchase_type == "subscription":
        # Audit-only: l'accesso lo decide subscription.* (vedi docstring del
        # modulo). Marchiamo comunque "completed" così un secondo
        # transaction.completed per lo stesso id resta idempotente.
        row.status = "completed"
        row.completed_at = datetime.now(timezone.utc)
        db.session.add(row)
        return TransactionApplyResult(outcome="completed", user_id=row.user_id)

    if row.purchase_type == "ai_credits":
        if user is None:
            row.status = "ignored"
            db.session.add(row)
            return TransactionApplyResult(outcome="ignored_no_user", reason="local_user_id non risolvibile")

        package_key = internal_plan_key or (reverse_lookup_credit_package(price_id) if price_id else None)
        entry = PADDLE_CREDIT_PACKAGES.get(package_key) if package_key else None
        if entry is None:
            row.status = "ignored"
            db.session.add(row)
            return TransactionApplyResult(
                outcome="ignored_no_user", reason=f"pacchetto crediti sconosciuto: {package_key!r}", user_id=user.id
            )

        if not get_plan_limits(user).ai_credit_topups_allowed:
            # Non dovrebbe succedere (il checkout già filtra lato server —
            # vedi app/billing/paddle_routes.py), ma se il piano dell'utente
            # è cambiato tra checkout e pagamento, non accreditiamo comunque
            # in silenzio: audit "ignored", riconciliabile a mano.
            row.status = "ignored"
            db.session.add(row)
            return TransactionApplyResult(
                outcome="ignored_ineligible", reason="piano utente non più eleggibile ai top-up", user_id=user.id
            )

        credits = entry["credits"]
        grant_credits(
            user,
            credits,
            type="grant_purchase",
            product_key=package_key,
            payment_reference=transaction_id,
            payment_source="paddle",
        )
        row.credits_granted = credits
        row.status = "completed"
        row.completed_at = datetime.now(timezone.utc)
        db.session.add(row)
        return TransactionApplyResult(outcome="completed", user_id=user.id, credits_granted=credits)

    # purchase_type sconosciuto/assente (custom_data mancante o corrotto) —
    # tracciato per riconciliazione admin, nessun side effect.
    row.status = "ignored"
    db.session.add(row)
    return TransactionApplyResult(outcome="ignored_no_user", reason=f"purchase_type sconosciuto: {purchase_type!r}")


def apply_transaction_payment_failed(*, data: dict, environment: str, completing_event_id: str | None) -> TransactionApplyResult:
    transaction_id = data.get("id")
    if not transaction_id:
        return TransactionApplyResult(outcome="ignored_no_user", reason="transazione senza id")

    row = _get_or_create_row(transaction_id=transaction_id, environment=environment)
    if row.status == "completed":
        # Non dovrebbe mai succedere (un pagamento non può fallire dopo
        # essere già completato) — se capita, non tocchiamo un accredito già
        # avvenuto: solo audit.
        return TransactionApplyResult(outcome="already_completed", user_id=row.user_id)

    user = _resolve_user(data)
    if user is not None:
        row.user_id = user.id
    row.status = "failed"
    row.completing_event_id = completing_event_id
    db.session.add(row)
    return TransactionApplyResult(outcome="failed_recorded", user_id=row.user_id)
