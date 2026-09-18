"""Applica gli eventi webhook `subscription.*` di Paddle allo stato locale
dell'utente — l'UNICA fonte autorevole che concede/estende l'accesso per un
utente Paddle (mai il callback client-side del checkout, vedi
app/webhooks/routes.py e docs/paddle-billing.md).

Ogni funzione qui è pensata per essere chiamata con lo stesso `data` grezzo
più volte (retry Paddle, eventi duplicati) e in un ordine non garantito
(fuori sequenza) — vedi `_is_stale` per la guardia anti-out-of-order. Non fa
mai il commit da sola: il chiamante (app/webhooks/routes.py) decide quando
committare, per poter scrivere nella stessa transazione anche la riga di
audit in PaddleWebhookEvent (vedi la nota su commit/rollback lì)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.billing.paddle_products import reverse_lookup_plan
from app.extensions import db
from app.models import User

# Stati Paddle che mappano 1:1 a subscription_status locale — stesso
# vocabolario dell'API Paddle, nessuna traduzione necessaria.
PADDLE_TO_LOCAL_STATUS = {
    "active": "active",
    "trialing": "trialing",
    "past_due": "past_due",
    "paused": "paused",
    "canceled": "canceled",
}


@dataclass(frozen=True)
class SubscriptionApplyResult:
    outcome: str  # "applied" | "ignored_stale" | "ignored_no_user" | "ignored_lifetime_protected"
    reason: str | None = None
    user_id: int | None = None


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # Paddle usa ISO 8601 con "Z" — datetime.fromisoformat non lo accetta
        # direttamente prima di Python 3.11 in tutte le forme, normalizziamo.
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _resolve_user(data: dict) -> User | None:
    """Risolve l'utente locale nell'ordine di affidabilità decrescente:
    1) custom_data.local_user_id (impostato da noi alla creazione del
       checkout — vedi app/billing/paddle_routes.py — e riecheggiato da
       Paddle su ogni evento della subscription/transazione risultante);
    2) un utente già collegato a questo stesso subscription_id (eventi
       successivi al primo, quando magari custom_data non viene più
       riecheggiato in una vista aggiornata);
    3) un utente già collegato a questo stesso customer_id, come ultima
       risorsa (un customer può avere più subscription nel tempo, ma non
       contemporaneamente per come questo prodotto vende oggi un solo piano
       Pro per utente).

    Non crea mai un utente: se nessuna delle tre risoluzioni trova una riga
    esistente, l'evento è "ignored_no_user" — riconciliabile a mano da un
    admin (vedi app/billing/paddle_reconciliation.py e Fase 7)."""
    custom_data = data.get("custom_data") or {}
    local_user_id = custom_data.get("local_user_id")
    if local_user_id is not None:
        try:
            user = db.session.get(User, int(local_user_id))
        except (TypeError, ValueError):
            user = None
        if user is not None:
            return user

    subscription_id = data.get("id")
    if subscription_id:
        user = User.query.filter_by(paddle_subscription_id=subscription_id).first()
        if user is not None:
            return user

    customer_id = data.get("customer_id")
    if customer_id:
        user = User.query.filter_by(paddle_customer_id=customer_id).first()
        if user is not None:
            return user

    return None


def _is_stale(user: User, event_occurred_at: datetime | None) -> bool:
    """Un evento è considerato superato se abbiamo già applicato un evento
    più recente per questo stesso utente (last_paddle_sync_at) — protegge
    dal caso "subscription.updated vecchio arriva dopo uno più nuovo" per
    consegne fuori ordine. Se non abbiamo un occurred_at (payload
    incompleto) o non abbiamo ancora mai sincronizzato questo utente, non è
    mai considerato stale: si applica per difetto."""
    if event_occurred_at is None or user.last_paddle_sync_at is None:
        return False
    last_sync = user.last_paddle_sync_at
    if last_sync.tzinfo is None:
        last_sync = last_sync.replace(tzinfo=timezone.utc)
    return event_occurred_at <= last_sync


def apply_subscription_event(
    *, event_type: str, data: dict, environment: str, event_occurred_at: datetime | None
) -> SubscriptionApplyResult:
    user = _resolve_user(data)
    if user is None:
        return SubscriptionApplyResult(outcome="ignored_no_user", reason="local_user_id non risolvibile")

    # Un account AppSumo lifetime non viene mai declassato/sovrascritto da un
    # altro flusso di pagamento, qualunque cosa dica l'evento in arrivo.
    if user.subscription_status == "lifetime":
        return SubscriptionApplyResult(
            outcome="ignored_lifetime_protected",
            reason="utente su piano AppSumo lifetime, non toccato da eventi Paddle",
            user_id=user.id,
        )

    if _is_stale(user, event_occurred_at):
        return SubscriptionApplyResult(outcome="ignored_stale", reason="evento più vecchio dell'ultimo sync", user_id=user.id)

    paddle_status = data.get("status")
    local_status = PADDLE_TO_LOCAL_STATUS.get(paddle_status)
    if local_status is None:
        return SubscriptionApplyResult(
            outcome="ignored_no_user", reason=f"status Paddle sconosciuto: {paddle_status!r}", user_id=user.id
        )

    period = data.get("current_billing_period") or {}
    period_ends_at = _parse_dt(period.get("ends_at"))

    scheduled_change = data.get("scheduled_change") or {}
    cancel_at_period_end = scheduled_change.get("action") == "cancel"

    items = data.get("items") or []
    price_id = None
    if items:
        price_id = (items[0].get("price") or {}).get("id")
    internal_plan_key = reverse_lookup_plan(price_id) if price_id else None

    now = datetime.now(timezone.utc)

    user.subscription_status = local_status
    user.subscription_source = "paddle"
    user.paddle_customer_id = data.get("customer_id") or user.paddle_customer_id
    user.paddle_subscription_id = data.get("id") or user.paddle_subscription_id
    user.paddle_environment = environment
    if price_id:
        user.paddle_price_id = price_id
    if internal_plan_key:
        # Solo se riconosciamo il price_id: un price creato a mano nel
        # dashboard Paddle e non registrato nella whitelist (vedi
        # app/billing/paddle_products.py) non deve mai far scattare un
        # plan_type "a caso" — meglio lasciare quello attuale e rendere il
        # caso visibile in admin via paddle_price_id.
        user.plan_type = internal_plan_key
    user.current_period_ends_at = period_ends_at
    user.cancel_at_period_end = cancel_at_period_end
    # subscription_expires_at è il fallback di accesso (vedi
    # app/entitlements/service.py::has_active_entitlement e il commento sul
    # campo in app/models/user.py) — per Paddle è sempre lo specchio del
    # periodo di fatturazione corrente. Se l'evento non porta un
    # current_billing_period (es. un `canceled` a fine vita, dopo che
    # l'ultimo periodo è già scaduto), NON lo azzeriamo mai a None — None
    # per un utente Paddle significherebbe "non ancora sincronizzato", non
    # "nessuna scadenza": manteniamo l'ultimo valore noto, così l'accesso
    # resta comunque bloccato dalla data già registrata invece di essere
    # riletto come "illimitato".
    if period_ends_at is not None:
        user.subscription_expires_at = period_ends_at
    elif user.subscription_expires_at is None:
        # Primissimo evento per questo utente e già senza periodo (raro, ma
        # possibile per un `canceled` immediato) — meglio essere
        # conservativi e non concedere accesso piuttosto che lasciare NULL,
        # che has_active_entitlement tratterebbe comunque come "nessun
        # accesso": scriviamo `now` solo per rendere il dato ispezionabile
        # in admin senza cambiare il risultato di has_active_entitlement.
        user.subscription_expires_at = now

    # IMPORTANTE: qui memorizziamo l'occurred_at DELL'EVENTO (tempo Paddle),
    # non l'ora reale di processing — è quello che _is_stale confronta con
    # l'occurred_at del PROSSIMO evento in arrivo per decidere se è più
    # vecchio dell'ultimo applicato. Usare invece l'ora di wall-clock qui
    # marcherebbe come "stale" quasi ogni evento successivo (un occurred_at
    # storico sarà quasi sempre <= all'ora di processing reale, che avanza
    # comunque nel frattempo) — un bug di design, non solo un dettaglio.
    # Per la riconciliazione (event_occurred_at None, vedi
    # app/billing/paddle_reconciliation.py) non abbiamo un occurred_at da
    # confrontare: usiamo `now` solo in quel caso, dove serve comunque per
    # capire "quando abbiamo sincronizzato l'ultima volta" a scopo audit.
    user.last_paddle_sync_at = event_occurred_at if event_occurred_at is not None else now

    return SubscriptionApplyResult(outcome="applied", user_id=user.id)
