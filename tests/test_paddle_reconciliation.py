"""Riconciliazione admin (app/billing/paddle_reconciliation.py) — fallback
per webhook persi: dry-run non scrive nulla, apply scrive, tocca solo
l'environment richiesto e mai utenti AppSumo/legacy (incluso il canale
Revolut dismesso)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.billing.paddle_client import PaddleAPIError
from app.billing.paddle_reconciliation import reconcile_paddle_users


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _fake_subscription_response(*, subscription_id, customer_id, status, price_id, ends_in_days, user_id):
    now = datetime.now(timezone.utc)
    return {
        "data": {
            "id": subscription_id,
            "status": status,
            "customer_id": customer_id,
            "current_billing_period": {"starts_at": _iso(now), "ends_at": _iso(now + timedelta(days=ends_in_days))},
            "items": [{"price": {"id": price_id}}],
            "scheduled_change": None,
            "custom_data": {"local_user_id": user_id, "purchase_type": "subscription", "internal_plan_key": "paddle_1m"},
        }
    }


@pytest.fixture()
def paddle_user(db_session, make_user):
    return make_user(
        plan_type="paddle_1m", subscription_status="past_due", subscription_source="paddle",
        paddle_environment="sandbox", paddle_subscription_id="sub_reconcile_1", paddle_customer_id="ctm_reconcile_1",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )


def test_dry_run_does_not_persist_changes(app, db_session, paddle_user, monkeypatch):
    import app.billing.paddle_reconciliation as recon

    monkeypatch.setattr(
        recon, "get_subscription",
        lambda sub_id: _fake_subscription_response(
            subscription_id=sub_id, customer_id="ctm_reconcile_1", status="active",
            price_id="pri_test_1m", ends_in_days=30, user_id=paddle_user.id,
        ),
    )

    with app.test_request_context():
        report = reconcile_paddle_users(environment="sandbox", dry_run=True)

    assert report.dry_run is True
    assert report.checked == 1
    assert report.changed == 1
    assert report.rows[0].after_status == "active"

    # Il DB non deve riflettere il cambiamento: dry-run.
    db_session.refresh(paddle_user)
    assert paddle_user.subscription_status == "past_due"


def test_apply_persists_changes(app, db_session, paddle_user, monkeypatch):
    import app.billing.paddle_reconciliation as recon

    monkeypatch.setattr(
        recon, "get_subscription",
        lambda sub_id: _fake_subscription_response(
            subscription_id=sub_id, customer_id="ctm_reconcile_1", status="active",
            price_id="pri_test_1m", ends_in_days=30, user_id=paddle_user.id,
        ),
    )

    with app.test_request_context():
        report = reconcile_paddle_users(environment="sandbox", dry_run=False)

    assert report.dry_run is False
    assert report.changed == 1

    db_session.refresh(paddle_user)
    assert paddle_user.subscription_status == "active"
    assert paddle_user.subscription_expires_at is not None


def test_reconcile_only_touches_requested_environment(app, db_session, paddle_user, monkeypatch):
    import app.billing.paddle_reconciliation as recon

    calls = []
    monkeypatch.setattr(recon, "get_subscription", lambda sub_id: calls.append(sub_id) or _fake_subscription_response(
        subscription_id=sub_id, customer_id="ctm_reconcile_1", status="active",
        price_id="pri_test_1m", ends_in_days=30, user_id=paddle_user.id,
    ))

    with app.test_request_context():
        report = reconcile_paddle_users(environment="production", dry_run=True)

    assert report.checked == 0
    assert calls == []  # l'utente è sandbox: mai interrogato per una riconciliazione production


def test_reconcile_never_touches_revolut_or_appsumo_users(app, db_session, make_user, monkeypatch):
    import app.billing.paddle_reconciliation as recon

    revolut_user = make_user(plan_type="revolut_1m", subscription_status="active", subscription_source="revolut_manual")
    appsumo_user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")

    calls = []
    monkeypatch.setattr(recon, "get_subscription", lambda sub_id: calls.append(sub_id))

    with app.test_request_context():
        report = reconcile_paddle_users(environment="sandbox", dry_run=True)

    assert report.checked == 0
    assert calls == []
    db_session.refresh(revolut_user)
    db_session.refresh(appsumo_user)
    assert revolut_user.subscription_status == "active"
    assert appsumo_user.subscription_status == "lifetime"


def test_reconcile_records_api_error_without_crashing(app, db_session, paddle_user, monkeypatch):
    import app.billing.paddle_reconciliation as recon

    def _boom(sub_id):
        raise PaddleAPIError("Paddle GET /subscriptions/... -> 500: boom")

    monkeypatch.setattr(recon, "get_subscription", _boom)

    with app.test_request_context():
        report = reconcile_paddle_users(environment="sandbox", dry_run=True)

    assert report.checked == 1
    assert report.changed == 0
    assert report.rows[0].outcome == "api_error"
