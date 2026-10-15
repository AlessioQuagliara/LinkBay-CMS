"""Webhook Paddle (app/webhooks/routes.py) — firma su raw body, idempotenza
per event_id, tolleranza replay, eventi fuori ordine, transizioni di stato,
fallback di scadenza, protezione AppSumo lifetime, accredito crediti one-time.
Nessuna chiamata di rete reale: il webhook non chiama mai Paddle, solo
verifica una firma locale con PADDLE_WEBHOOK_SECRET (vedi conftest.py)."""
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone

import pytest

from app.models import AiCreditTransaction, PaddleTransaction, PaddleWebhookEvent

WEBHOOK_SECRET = "test-paddle-webhook-secret"


def _sign(raw_body: bytes, *, ts: int | None = None, secret: str = WEBHOOK_SECRET) -> str:
    ts = ts if ts is not None else int(time.time())
    signed_payload = f"{ts}:".encode() + raw_body
    h1 = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"ts={ts};h1={h1}"


def _post(client, payload: dict, *, ts: int | None = None, secret: str = WEBHOOK_SECRET, header: str | None = "auto"):
    raw = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if header == "auto":
        headers["Paddle-Signature"] = _sign(raw, ts=ts, secret=secret)
    elif header is not None:
        headers["Paddle-Signature"] = header
    return client.post("/webhooks/paddle", data=raw, headers=headers)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _subscription_payload(*, event_id, event_type, user_id, subscription_id="sub_1", customer_id="ctm_1",
                           status="active", price_id="pri_test_1m", period_ends_in_days=30,
                           occurred_at=None, scheduled_change=None):
    occurred_at = occurred_at or datetime.now(timezone.utc)
    return {
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": _iso(occurred_at),
        "data": {
            "id": subscription_id,
            "status": status,
            "customer_id": customer_id,
            "current_billing_period": {
                "starts_at": _iso(occurred_at),
                "ends_at": _iso(occurred_at + timedelta(days=period_ends_in_days)) if period_ends_in_days is not None else None,
            } if period_ends_in_days is not None else None,
            "items": [{"price": {"id": price_id}}],
            "scheduled_change": scheduled_change,
            "custom_data": {"local_user_id": user_id, "purchase_type": "subscription", "internal_plan_key": "paddle_1m"},
        },
    }


def _transaction_completed_payload(*, event_id, user_id, transaction_id="txn_1", purchase_type="ai_credits",
                                    internal_plan_key="ai_topup_starter", price_id="pri_test_topup_starter"):
    return {
        "event_id": event_id,
        "event_type": "transaction.completed",
        "occurred_at": _iso(datetime.now(timezone.utc)),
        "data": {
            "id": transaction_id,
            "customer_id": "ctm_1",
            "subscription_id": None,
            "currency_code": "EUR",
            "items": [{"price": {"id": price_id}}],
            "details": {"totals": {"total": "700"}},
            "custom_data": {
                "local_user_id": user_id, "purchase_type": purchase_type, "internal_plan_key": internal_plan_key,
                "correlation_id": "corr-1",
            },
        },
    }


# --- verifica firma ---------------------------------------------------------


def test_webhook_rejects_missing_signature(client, db_session):
    res = _post(client, {"event_id": "evt_x", "event_type": "subscription.created", "data": {}}, header=None)
    assert res.status_code == 400
    assert PaddleWebhookEvent.query.count() == 0


def test_webhook_rejects_invalid_signature(client, db_session):
    res = _post(client, {"event_id": "evt_x", "event_type": "subscription.created", "data": {}}, header="ts=123;h1=deadbeef")
    assert res.status_code == 400
    assert PaddleWebhookEvent.query.count() == 0


def test_webhook_rejects_wrong_secret(client, db_session):
    res = _post(client, {"event_id": "evt_x", "event_type": "subscription.created", "data": {}}, secret="wrong-secret")
    assert res.status_code == 400
    assert PaddleWebhookEvent.query.count() == 0


def test_webhook_rejects_stale_timestamp(client, db_session):
    old_ts = int(time.time()) - 3600  # 1h fa, oltre la tolleranza di 5 minuti
    res = _post(client, {"event_id": "evt_x", "event_type": "subscription.created", "data": {}}, ts=old_ts)
    assert res.status_code == 400
    assert PaddleWebhookEvent.query.count() == 0


def test_webhook_rejects_malformed_payload_even_with_valid_signature(client, db_session):
    res = _post(client, {"foo": "bar"})  # firma valida ma senza event_id/event_type
    assert res.status_code == 400
    assert PaddleWebhookEvent.query.count() == 0


# --- idempotenza per event_id -----------------------------------------------


def test_webhook_duplicate_event_id_is_not_reprocessed(client, db_session, make_user):
    user = make_user(plan_type="trial")
    payload = _subscription_payload(event_id="evt_dup_1", event_type="subscription.created", user_id=user.id)

    res1 = _post(client, payload)
    assert res1.status_code == 200
    res2 = _post(client, payload)
    assert res2.status_code == 200
    assert res2.get_json()["status"] == "duplicate"

    assert PaddleWebhookEvent.query.filter_by(event_id="evt_dup_1").count() == 1


# --- applicazione subscription.* --------------------------------------------


def test_webhook_subscription_created_activates_user(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    payload = _subscription_payload(event_id="evt_created_1", event_type="subscription.created", user_id=user.id)

    res = _post(client, payload)
    assert res.status_code == 200

    db_session.refresh(user)
    assert user.subscription_status == "active"
    assert user.subscription_source == "paddle"
    assert user.plan_type == "paddle_1m"
    assert user.paddle_customer_id == "ctm_1"
    assert user.paddle_subscription_id == "sub_1"
    assert user.paddle_price_id == "pri_test_1m"
    assert user.subscription_expires_at is not None

    event_row = PaddleWebhookEvent.query.filter_by(event_id="evt_created_1").first()
    assert event_row.status == "processed"


def test_webhook_ignores_event_with_unresolvable_user(client, db_session):
    payload = _subscription_payload(event_id="evt_no_user", event_type="subscription.created", user_id=999999)
    res = _post(client, payload)
    assert res.status_code == 200  # ricevuto, ma non processato: non deve far ritentare Paddle

    event_row = PaddleWebhookEvent.query.filter_by(event_id="evt_no_user").first()
    assert event_row is not None
    assert event_row.status == "ignored"


def test_webhook_never_touches_appsumo_lifetime_user(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier2", subscription_status="lifetime")
    payload = _subscription_payload(event_id="evt_lifetime_1", event_type="subscription.created", user_id=user.id)

    res = _post(client, payload)
    assert res.status_code == 200

    db_session.refresh(user)
    assert user.subscription_status == "lifetime"
    assert user.plan_type == "appsumo_tier2"
    assert user.paddle_subscription_id is None

    event_row = PaddleWebhookEvent.query.filter_by(event_id="evt_lifetime_1").first()
    assert event_row.status == "ignored"


def test_webhook_active_to_past_due_to_active(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    base = datetime.now(timezone.utc)

    _post(client, _subscription_payload(
        event_id="evt_seq_1", event_type="subscription.created", user_id=user.id,
        status="active", occurred_at=base,
    ))
    db_session.refresh(user)
    assert user.subscription_status == "active"

    _post(client, _subscription_payload(
        event_id="evt_seq_2", event_type="subscription.past_due", user_id=user.id,
        status="past_due", occurred_at=base + timedelta(minutes=1),
    ))
    db_session.refresh(user)
    assert user.subscription_status == "past_due"
    # Nessuna grace period inventata: has_active_entitlement per Paddle
    # ammette "past_due" solo fino a subscription_expires_at, non oltre —
    # qui il periodo è ancora nel futuro quindi l'accesso resta valido.
    from app.entitlements.service import has_active_entitlement
    assert has_active_entitlement(user) is True

    _post(client, _subscription_payload(
        event_id="evt_seq_3", event_type="subscription.updated", user_id=user.id,
        status="active", occurred_at=base + timedelta(minutes=2),
    ))
    db_session.refresh(user)
    assert user.subscription_status == "active"


def test_webhook_out_of_order_event_is_ignored(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    base = datetime.now(timezone.utc)

    # Evento "recente" applicato per primo.
    _post(client, _subscription_payload(
        event_id="evt_order_new", event_type="subscription.updated", user_id=user.id,
        status="active", occurred_at=base + timedelta(minutes=5),
    ))
    db_session.refresh(user)
    assert user.subscription_status == "active"

    # Evento "vecchio" (occurred_at precedente) arriva DOPO — non deve
    # sovrascrivere lo stato più recente già applicato.
    res = _post(client, _subscription_payload(
        event_id="evt_order_old", event_type="subscription.past_due", user_id=user.id,
        status="past_due", occurred_at=base,
    ))
    assert res.status_code == 200
    db_session.refresh(user)
    assert user.subscription_status == "active"  # non declassato dall'evento vecchio

    event_row = PaddleWebhookEvent.query.filter_by(event_id="evt_order_old").first()
    assert event_row.status == "ignored"


def test_webhook_canceled_keeps_access_until_period_end(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    base = datetime.now(timezone.utc)

    _post(client, _subscription_payload(
        event_id="evt_cancel_1", event_type="subscription.created", user_id=user.id,
        status="active", occurred_at=base, period_ends_in_days=30,
    ))
    _post(client, _subscription_payload(
        event_id="evt_cancel_2", event_type="subscription.canceled", user_id=user.id,
        status="canceled", occurred_at=base + timedelta(minutes=1), period_ends_in_days=30,
        scheduled_change={"action": "cancel", "effective_at": _iso(base + timedelta(days=30))},
    ))

    db_session.refresh(user)
    assert user.subscription_status == "canceled"
    assert user.cancel_at_period_end is True

    from app.entitlements.service import has_active_entitlement
    assert has_active_entitlement(user) is False  # "canceled" non è tra gli stati che concedono accesso Paddle


def test_webhook_access_blocked_after_expiry(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    base = datetime.now(timezone.utc) - timedelta(days=40)

    _post(client, _subscription_payload(
        event_id="evt_expired_1", event_type="subscription.created", user_id=user.id,
        status="active", occurred_at=base, period_ends_in_days=30,  # scaduto 10gg fa
    ))

    db_session.refresh(user)
    assert user.subscription_status == "active"
    from app.entitlements.service import has_active_entitlement
    assert has_active_entitlement(user) is False  # scaduto, nessun accesso illimitato per un NULL mai avuto


def test_webhook_unknown_price_id_keeps_previous_plan_type(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    payload = _subscription_payload(
        event_id="evt_unknownprice_1", event_type="subscription.created", user_id=user.id,
        price_id="pri_not_in_whitelist",
    )
    res = _post(client, payload)
    assert res.status_code == 200

    db_session.refresh(user)
    # Lo stato/i campi "grezzi" Paddle si aggiornano comunque...
    assert user.subscription_status == "active"
    assert user.paddle_price_id == "pri_not_in_whitelist"
    # ...ma plan_type NON viene mai impostato a un valore inventato.
    assert user.plan_type == "trial"


# --- transaction.completed (crediti AI) -------------------------------------


def test_webhook_transaction_completed_grants_credits_once(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    payload = _transaction_completed_payload(event_id="evt_txn_1", user_id=user.id, transaction_id="txn_credits_1")

    res1 = _post(client, payload)
    assert res1.status_code == 200
    db_session.refresh(user)
    assert user.ai_credit_balance == 50

    # Stesso event_id ripetuto (retry Paddle) -> "duplicate", nessun secondo accredito.
    res2 = _post(client, payload)
    assert res2.status_code == 200
    assert res2.get_json()["status"] == "duplicate"

    db_session.refresh(user)
    assert user.ai_credit_balance == 50
    assert AiCreditTransaction.query.filter_by(user_id=user.id, payment_source="paddle").count() == 1

    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_credits_1").first()
    assert row.status == "completed"
    assert row.credits_granted == 50


def test_webhook_failed_final_commit_leaves_no_credits(client, db_session, make_user, monkeypatch):
    # L'accredito e la riga evento devono stare nella STESSA transazione: se il
    # commit finale fallisce, il retry di Paddle deve ripartire da zero.
    from app.extensions import db

    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    real_commit = db.session.commit

    def failing_commit():
        if any(isinstance(o, PaddleWebhookEvent) for o in db.session.new):
            raise RuntimeError("db down")
        real_commit()

    monkeypatch.setattr(db.session, "commit", failing_commit)
    payload = _transaction_completed_payload(event_id="evt_txn_fail", user_id=user.id, transaction_id="txn_fail")
    assert _post(client, payload).status_code == 500
    monkeypatch.undo()

    db_session.refresh(user)
    assert user.ai_credit_balance == 0
    assert AiCreditTransaction.query.filter_by(user_id=user.id).count() == 0


def test_webhook_transaction_completed_different_event_id_same_transaction_id_is_idempotent(client, db_session, make_user):
    # Simula due CONSEGNE diverse (event_id diverso) dello stesso
    # transaction.completed (può succedere con Paddle) — la difesa di
    # secondo livello sul transaction_id (PaddleTransaction.status ==
    # "completed") deve comunque impedire un doppio accredito.
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    payload1 = _transaction_completed_payload(event_id="evt_txn_a", user_id=user.id, transaction_id="txn_credits_2")
    payload2 = _transaction_completed_payload(event_id="evt_txn_b", user_id=user.id, transaction_id="txn_credits_2")

    _post(client, payload1)
    _post(client, payload2)

    db_session.refresh(user)
    assert user.ai_credit_balance == 50
    assert AiCreditTransaction.query.filter_by(user_id=user.id, payment_source="paddle").count() == 1


def test_webhook_transaction_completed_unknown_user_is_ignored_not_credited(client, db_session):
    payload = _transaction_completed_payload(event_id="evt_txn_nouser", user_id=999999, transaction_id="txn_nouser_1")
    res = _post(client, payload)
    assert res.status_code == 200

    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_nouser_1").first()
    assert row.status == "ignored"
    assert row.credits_granted is None


def test_webhook_subscription_transaction_completed_is_audit_only(client, db_session, make_user):
    # Un transaction.completed collegato a un abbonamento non deve MAI
    # accreditare crediti né toccare i campi subscription — quello lo fanno
    # solo gli eventi subscription.* (vedi test sopra).
    user = make_user(plan_type="trial", subscription_status="trialing")
    payload = _transaction_completed_payload(
        event_id="evt_txn_sub_1", user_id=user.id, transaction_id="txn_sub_1",
        purchase_type="subscription", internal_plan_key="paddle_1m", price_id="pri_test_1m",
    )
    res = _post(client, payload)
    assert res.status_code == 200

    db_session.refresh(user)
    assert user.subscription_status == "trialing"  # invariato: non è un evento subscription.*
    assert user.ai_credit_balance == 0

    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_sub_1").first()
    assert row.status == "completed"
    assert row.purchase_type == "subscription"


def test_webhook_transaction_payment_failed_records_no_credit(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    raw_payload = {
        "event_id": "evt_txn_failed_1",
        "event_type": "transaction.payment_failed",
        "occurred_at": _iso(datetime.now(timezone.utc)),
        "data": {
            "id": "txn_failed_1", "customer_id": "ctm_1",
            "custom_data": {"local_user_id": user.id, "purchase_type": "ai_credits", "internal_plan_key": "ai_topup_starter"},
        },
    }
    res = _post(client, raw_payload)
    assert res.status_code == 200

    db_session.refresh(user)
    assert user.ai_credit_balance == 0
    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_failed_1").first()
    assert row.status == "failed"


# --- eventi non gestiti ------------------------------------------------------


def test_webhook_unhandled_event_type_is_recorded_and_ignored(client, db_session):
    payload = {
        "event_id": "evt_unhandled_1", "event_type": "address.updated",
        "occurred_at": _iso(datetime.now(timezone.utc)), "data": {"id": "add_1"},
    }
    res = _post(client, payload)
    assert res.status_code == 200
    row = PaddleWebhookEvent.query.filter_by(event_id="evt_unhandled_1").first()
    assert row.status == "ignored"
