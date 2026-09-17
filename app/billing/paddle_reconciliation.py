"""Riconciliazione amministrativa per gli utenti Paddle — il fallback
operativo per un webhook perso o uno stato locale incoerente (vedi Fase 6 e
docs/paddle-billing.md). Interroga l'API Paddle per lo stato REALE di ogni
subscription collegata e lo riapplica con la STESSA funzione già usata dal
webhook (app/billing/paddle_subscriptions.py::apply_subscription_event) —
nessuna logica di sincronizzazione duplicata, quindi nessun rischio che
riconciliazione e webhook divergano su cosa significa "un evento valido".

Tocca SOLO utenti con subscription_source == "paddle" e paddle_environment
== l'environment richiesto — mai un utente Revolut/AppSumo/legacy (Fase 7:
"non modifica automaticamente record legacy"), e mai un utente Paddle
dell'altro environment (mai mescolare sandbox e production)."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.billing.paddle_client import PaddleAPIError, get_subscription
from app.billing.paddle_subscriptions import apply_subscription_event
from app.extensions import db
from app.models import User


@dataclass(frozen=True)
class ReconciliationRow:
    user_id: int
    email: str
    paddle_subscription_id: str
    outcome: str  # stesso vocabolario di SubscriptionApplyResult.outcome, + "api_error"
    before_status: str | None
    after_status: str | None
    before_expires_at: str | None
    after_expires_at: str | None
    reason: str | None = None


@dataclass(frozen=True)
class ReconciliationReport:
    environment: str
    dry_run: bool
    checked: int
    changed: int
    rows: list[ReconciliationRow] = field(default_factory=list)


def _iso(dt):
    return dt.isoformat() if dt else None


def reconcile_paddle_users(*, environment: str, dry_run: bool = True, user_id: int | None = None) -> ReconciliationReport:
    query = User.query.filter(
        User.subscription_source == "paddle",
        User.paddle_environment == environment,
        User.paddle_subscription_id.isnot(None),
    )
    if user_id is not None:
        query = query.filter(User.id == user_id)

    users = query.all()
    rows: list[ReconciliationRow] = []
    changed = 0

    for user in users:
        before_status = user.subscription_status
        before_expires_at = _iso(user.subscription_expires_at)

        try:
            response = get_subscription(user.paddle_subscription_id)
        except PaddleAPIError as exc:
            rows.append(
                ReconciliationRow(
                    user_id=user.id, email=user.email, paddle_subscription_id=user.paddle_subscription_id,
                    outcome="api_error", before_status=before_status, after_status=before_status,
                    before_expires_at=before_expires_at, after_expires_at=before_expires_at, reason=str(exc),
                )
            )
            continue

        data = response.get("data") or response

        # event_occurred_at=None disabilita la guardia anti-out-of-order
        # (_is_stale) di proposito: uno stato appena letto dall'API è per
        # definizione il più recente disponibile, non un evento storico da
        # confrontare con last_paddle_sync_at.
        result = apply_subscription_event(
            event_type="subscription.updated", data=data, environment=environment, event_occurred_at=None
        )

        after_status = user.subscription_status
        after_expires_at = _iso(user.subscription_expires_at)
        row_changed = result.outcome == "applied" and (
            after_status != before_status or after_expires_at != before_expires_at
        )
        if row_changed:
            changed += 1

        rows.append(
            ReconciliationRow(
                user_id=user.id, email=user.email, paddle_subscription_id=user.paddle_subscription_id,
                outcome=result.outcome, before_status=before_status, after_status=after_status,
                before_expires_at=before_expires_at, after_expires_at=after_expires_at, reason=result.reason,
            )
        )

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    return ReconciliationReport(environment=environment, dry_run=dry_run, checked=len(users), changed=changed, rows=rows)
