"""Webhook Lemon Squeezy (app/billing/routes.py::webhook). Priorità alta sul
confine past_due/grace period (subscription_payment_failed): è la modifica a
più alto rischio del piano multi-tier, tocca direttamente il gate di accesso
pagante (User.has_active_access)."""
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import pytest

from app.models import AiCreditTransaction

WEBHOOK_SECRET = "test-webhook-secret"  # deve combaciare con TestConfig


def _sign(payload_bytes: bytes) -> str:
    return hmac.new(WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()


def _post_webhook(client, event_name, data, custom_data=None):
    body = {
        "meta": {"event_name": event_name, "custom_data": custom_data or {}},
        "data": data,
    }
    payload = json.dumps(body).encode()
    return client.post(
        "/billing/webhook",
        data=payload,
        headers={"Content-Type": "application/json", "X-Signature": _sign(payload)},
    )


def _subscription_data(sub_id, status, variant_id, customer_id=999):
    return {
        "id": str(sub_id),
        "attributes": {"status": status, "variant_id": variant_id, "customer_id": customer_id},
    }


# --- firma --------------------------------------------------------------


def test_webhook_rejects_invalid_signature(client):
    body = json.dumps({"meta": {"event_name": "subscription_created"}, "data": {}}).encode()
    res = client.post(
        "/billing/webhook",
        data=body,
        headers={"Content-Type": "application/json", "X-Signature": "not-the-real-signature"},
    )
    assert res.status_code == 400


# --- subscription_created / plan_type dal variant -----------------------


def test_subscription_created_sets_plan_type_from_variant(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    res = _post_webhook(
        client, "subscription_created",
        _subscription_data("sub_1", "active", "1001"),  # pro_monthly nel TestConfig
        custom_data={"user_id": str(user.id)},
    )
    assert res.status_code == 200
    db_session.refresh(user)
    assert user.subscription_status == "active"
    assert user.plan_type == "subscription_monthly"
    assert user.billing_interval == "monthly"
    assert user.ls_subscription_id == "sub_1"


def test_subscription_created_pro_annual(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    _post_webhook(
        client, "subscription_created",
        _subscription_data("sub_2", "active", "1002"),  # pro_annual
        custom_data={"user_id": str(user.id)},
    )
    db_session.refresh(user)
    assert user.plan_type == "subscription_annual"
    assert user.billing_interval == "annual"


def test_subscription_created_missing_user_id_does_not_crash(client):
    res = _post_webhook(client, "subscription_created", _subscription_data("sub_x", "active", "1001"))
    assert res.status_code == 200  # ignorato silenziosamente, non un errore verso Lemon Squeezy


# --- past_due / grace period (priorità alta) -----------------------------


def test_subscription_payment_failed_sets_past_due_with_grace_period(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ls_subscription_id="sub_3")
    res = _post_webhook(client, "subscription_payment_failed", {"id": "sub_3", "attributes": {}})
    assert res.status_code == 200
    db_session.refresh(user)
    assert user.subscription_status == "past_due"
    assert user.grace_period_ends_at is not None


def test_has_active_access_true_during_grace_period(db_session, make_user):
    user = make_user(
        plan_type="subscription_monthly", subscription_status="past_due",
        grace_period_ends_at=datetime.now(timezone.utc) + timedelta(days=3),
    )
    assert user.has_active_access is True


def test_has_active_access_false_after_grace_period_expires(db_session, make_user):
    user = make_user(
        plan_type="subscription_monthly", subscription_status="past_due",
        grace_period_ends_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    assert user.has_active_access is False


def test_has_active_access_unchanged_for_pre_existing_statuses(db_session, make_user):
    # Regressione esplicita: il gate per gli stati già esistenti prima di
    # questa fase non deve cambiare comportamento.
    trialing_ok = make_user(subscription_status="trialing", trial_ends_at=datetime.now(timezone.utc) + timedelta(days=1))
    trialing_expired = make_user(subscription_status="trialing", trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1))
    active = make_user(subscription_status="active")
    lifetime = make_user(subscription_status="lifetime")
    canceled = make_user(subscription_status="canceled")

    assert trialing_ok.has_active_access is True
    assert trialing_expired.has_active_access is False
    assert active.has_active_access is True
    assert lifetime.has_active_access is True
    assert canceled.has_active_access is False


def test_subscription_payment_success_clears_past_due(client, db_session, make_user):
    user = make_user(
        plan_type="subscription_monthly", subscription_status="past_due", ls_subscription_id="sub_4",
        grace_period_ends_at=datetime.now(timezone.utc) + timedelta(days=2),
    )
    res = _post_webhook(client, "subscription_payment_success", {"id": "sub_4", "attributes": {}})
    assert res.status_code == 200
    db_session.refresh(user)
    assert user.subscription_status == "active"
    assert user.grace_period_ends_at is None


def test_subscription_payment_success_grants_monthly_ai_quota_for_credit_plan(client, db_session, make_user):
    user = make_user(
        plan_type="subscription_monthly", subscription_status="active", ls_subscription_id="sub_5",
        ai_credit_balance=0,
    )
    _post_webhook(client, "subscription_payment_success", {"id": "sub_5", "attributes": {}})
    db_session.refresh(user)
    assert user.ai_credit_balance == 5000  # PLAN_LIMITS["subscription_monthly"].ai_credit_grant


def test_subscription_cancelled_sets_canceled(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", subscription_status="active", ls_subscription_id="sub_6")
    _post_webhook(client, "subscription_cancelled", {"id": "sub_6", "attributes": {}})
    db_session.refresh(user)
    assert user.subscription_status == "canceled"


def test_subscription_plan_changed_updates_plan_type(client, db_session, make_user):
    user = make_user(
        plan_type="subscription_monthly", billing_interval="monthly",
        subscription_status="active", ls_subscription_id="sub_7",
    )
    _post_webhook(client, "subscription_plan_changed", {"id": "sub_7", "attributes": {"variant_id": "1002"}})
    db_session.refresh(user)
    assert user.plan_type == "subscription_annual"
    assert user.billing_interval == "annual"


# --- crediti AI one-time (order_created / order_refunded) ----------------


def test_order_created_grants_credits(client, db_session, make_user):
    user = make_user(plan_type="subscription_monthly", ai_credit_balance=0)
    res = _post_webhook(
        client, "order_created", {"id": "order_1", "attributes": {}},
        custom_data={"user_id": str(user.id), "product_key": "credits_500"},
    )
    assert res.status_code == 200
    db_session.refresh(user)
    assert user.ai_credit_balance == 500
    tx = AiCreditTransaction.query.filter_by(ls_order_id="order_1").first()
    assert tx is not None
    assert tx.type == "grant_purchase"
    assert tx.amount == 500


def test_order_created_is_idempotent(client, db_session, make_user):
    user = make_user(ai_credit_balance=0)
    for _ in range(2):
        _post_webhook(
            client, "order_created", {"id": "order_2", "attributes": {}},
            custom_data={"user_id": str(user.id), "product_key": "credits_1500"},
        )
    db_session.refresh(user)
    assert user.ai_credit_balance == 1500  # non 3000: il secondo webhook non doppio-accredita


def test_order_created_ignores_plan_products(client, db_session, make_user):
    # product_key di tipo "plan" non deve mai passare da order_created
    # (i piani sono ricorrenti, gestiti da subscription_created) — un evento
    # simile non dovrebbe arrivare da Lemon Squeezy, ma se arrivasse va
    # ignorato, non deve accreditare crediti a caso.
    user = make_user(ai_credit_balance=0)
    _post_webhook(
        client, "order_created", {"id": "order_3", "attributes": {}},
        custom_data={"user_id": str(user.id), "product_key": "pro_monthly"},
    )
    db_session.refresh(user)
    assert user.ai_credit_balance == 0


def test_order_refunded_claws_back_credits(client, db_session, make_user):
    user = make_user(ai_credit_balance=0)
    _post_webhook(
        client, "order_created", {"id": "order_4", "attributes": {}},
        custom_data={"user_id": str(user.id), "product_key": "credits_500"},
    )
    db_session.refresh(user)
    assert user.ai_credit_balance == 500

    _post_webhook(client, "order_refunded", {"id": "order_4", "attributes": {}})
    db_session.refresh(user)
    assert user.ai_credit_balance == 0
    adjustment = AiCreditTransaction.query.filter_by(ls_order_id="order_4", type="adjustment").first()
    assert adjustment is not None
    assert adjustment.amount == -500


def test_order_refunded_unknown_order_is_a_noop(client):
    res = _post_webhook(client, "order_refunded", {"id": "does-not-exist", "attributes": {}})
    assert res.status_code == 200
