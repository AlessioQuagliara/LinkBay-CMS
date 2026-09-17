"""Checkout server-driven Paddle (app/billing/paddle_routes.py) — whitelist
server-side di piano/pacchetto, custom_data corretto, nessuna chiamata di
rete reale (monkeypatch di requests.request dentro app.billing.paddle_client)."""
import json

import pytest

from app.models import PaddleTransaction


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


class _FakeResponse:
    def __init__(self, status_code=200, json_body=None):
        self.status_code = status_code
        self._json = json_body or {}
        self.content = b"{}" if json_body is None else json.dumps(json_body).encode()
        self.text = self.content.decode()

    def json(self):
        return self._json


@pytest.fixture()
def fake_paddle_transaction(monkeypatch):
    """Intercetta ogni chiamata HTTP di app.billing.paddle_client verso
    Paddle e simula una risposta di POST /transactions riuscita — cattura
    anche il payload inviato, per poter asserire su items/custom_data senza
    fidarsi di cosa il modulo dice di aver mandato."""
    calls = []

    def _fake_request(method, url, headers=None, json=None, timeout=None):
        calls.append({"method": method, "url": url, "headers": headers, "json": json})
        return _FakeResponse(
            200,
            {
                "data": {
                    "id": "txn_fake_123",
                    "checkout": {"url": "https://sandbox-checkout.paddle.com/txn_fake_123"},
                }
            },
        )

    import app.billing.paddle_client as paddle_client

    monkeypatch.setattr(paddle_client.requests, "request", _fake_request)
    return calls


# --- autenticazione ----------------------------------------------------


def test_checkout_subscription_requires_login(client):
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_1m"})
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]


def test_checkout_credits_requires_login(client):
    res = client.post("/billing/checkout/credits", data={"credit_package": "ai_topup_starter"})
    assert res.status_code == 302


# --- whitelist server-side -----------------------------------------------


def test_checkout_subscription_rejects_unknown_plan(client, db_session, make_user):
    user = make_user(plan_type="trial")
    _login(client, user)
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_99y"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_plan"


def test_checkout_credits_rejects_unknown_package(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    res = client.post("/billing/checkout/credits", data={"credit_package": "ai_topup_infinite"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_package"


def test_checkout_credits_rejects_ineligible_plan(client, db_session, make_user):
    # Pro (Revolut o Paddle) non è eleggibile ai top-up — stessa regola già
    # in vigore per Revolut (get_plan_limits(user).ai_credit_topups_allowed).
    user = make_user(plan_type="revolut_1m", subscription_status="active")
    _login(client, user)
    res = client.post("/billing/checkout/credits", data={"credit_package": "ai_topup_starter"})
    assert res.status_code == 403
    assert res.get_json()["error"] == "not_eligible"


def test_checkout_subscription_rejects_when_price_not_configured(client, app, db_session, make_user, monkeypatch):
    monkeypatch.setitem(app.config, "PADDLE_SANDBOX_PRICE_ID_1M", None)
    user = make_user(plan_type="trial")
    _login(client, user)
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_1m"})
    assert res.status_code == 503
    assert res.get_json()["error"] == "not_configured"


def test_checkout_subscription_rejects_lifetime_account(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_1m"})
    assert res.status_code == 409
    assert res.get_json()["error"] == "lifetime_account"


def test_checkout_subscription_rejects_when_already_subscribed(client, db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="active", subscription_source="paddle",
        paddle_subscription_id="sub_existing_1",
    )
    _login(client, user)
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_3m"})
    assert res.status_code == 409
    assert res.get_json()["error"] == "already_subscribed"


# --- creazione transazione: custom_data corretto, mai fidarsi del client ---


def test_checkout_subscription_builds_correct_custom_data(client, db_session, make_user, fake_paddle_transaction):
    user = make_user(plan_type="trial")
    _login(client, user)

    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_3m"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["checkout_url"] == "https://sandbox-checkout.paddle.com/txn_fake_123"
    assert body["transaction_id"] == "txn_fake_123"

    sent = fake_paddle_transaction[0]["json"]
    assert sent["items"] == [{"price_id": "pri_test_3m", "quantity": 1}]
    assert sent["custom_data"]["local_user_id"] == user.id
    assert sent["custom_data"]["purchase_type"] == "subscription"
    assert sent["custom_data"]["internal_plan_key"] == "paddle_3m"
    assert sent["custom_data"]["environment"] == "sandbox"
    assert "correlation_id" in sent["custom_data"]

    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_fake_123").first()
    assert row is not None
    assert row.user_id == user.id
    assert row.status == "pending"
    assert row.purchase_type == "subscription"
    assert row.internal_plan_key == "paddle_3m"


def test_checkout_credits_ignores_client_supplied_price_and_amount(client, db_session, make_user, fake_paddle_transaction):
    # Il client non ha nemmeno un campo price_id/amount nel form reale — qui
    # simuliamo un client "contraffatto" che li invia comunque: il server
    # deve ignorarli e risolvere SEMPRE il price_id dal catalogo whitelist.
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)

    res = client.post(
        "/billing/checkout/credits",
        data={
            "credit_package": "ai_topup_starter",
            "price_id": "pri_evil_free_credits",
            "amount": "0",
            "currency": "XXX",
        },
    )
    assert res.status_code == 201

    sent = fake_paddle_transaction[0]["json"]
    assert sent["items"] == [{"price_id": "pri_test_topup_starter", "quantity": 1}]

    row = PaddleTransaction.query.filter_by(paddle_transaction_id="txn_fake_123").first()
    assert row.paddle_price_id == "pri_test_topup_starter"
    assert row.purchase_type == "ai_credits"
    assert row.internal_plan_key == "ai_topup_starter"


def test_checkout_paddle_api_error_returns_502(client, db_session, make_user, monkeypatch):
    import app.billing.paddle_client as paddle_client

    def _boom(method, url, headers=None, json=None, timeout=None):
        return _FakeResponse(500, {"error": {"detail": "internal"}})

    monkeypatch.setattr(paddle_client.requests, "request", _boom)

    user = make_user(plan_type="trial")
    _login(client, user)
    res = client.post("/billing/checkout/subscription", data={"plan": "paddle_1m"})
    assert res.status_code == 502
    assert res.get_json()["error"] == "paddle_unavailable"


# --- /billing/status ---------------------------------------------------


def test_status_endpoint_reports_local_state_only(client, db_session, make_user):
    from datetime import datetime, timedelta, timezone

    expires = datetime.now(timezone.utc) + timedelta(days=10)
    user = make_user(
        plan_type="paddle_1m", subscription_status="active", subscription_source="paddle",
        subscription_expires_at=expires, paddle_subscription_id="sub_status_1",
    )
    _login(client, user)

    res = client.get("/billing/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["subscription_status"] == "active"
    assert body["billing_provider"] == "paddle"
    assert body["has_active_access"] is True


def test_status_requires_login(client):
    res = client.get("/billing/status", follow_redirects=False)
    assert res.status_code == 302


# --- /billing/customer-portal --------------------------------------------


def test_customer_portal_requires_paddle_customer(client, db_session, make_user):
    user = make_user(plan_type="trial")  # nessun paddle_customer_id
    _login(client, user)
    res = client.post("/billing/customer-portal")
    assert res.status_code == 404
    assert res.get_json()["error"] == "no_paddle_customer"


def test_customer_portal_returns_hosted_url(client, db_session, make_user, monkeypatch):
    import app.billing.paddle_client as paddle_client

    def _fake_request(method, url, headers=None, json=None, timeout=None):
        assert method == "POST"
        assert "/customers/ctm_portal_1/portal-sessions" in url
        return _FakeResponse(200, {"data": {"urls": {"general": {"overview": "https://customer-portal.paddle.com/xyz"}}}})

    monkeypatch.setattr(paddle_client.requests, "request", _fake_request)

    user = make_user(plan_type="paddle_1m", subscription_source="paddle", paddle_customer_id="ctm_portal_1")
    _login(client, user)
    res = client.post("/billing/customer-portal")
    assert res.status_code == 200
    assert res.get_json()["portal_url"] == "https://customer-portal.paddle.com/xyz"
