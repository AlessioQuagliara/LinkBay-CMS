"""Ledger crediti AI (app/entitlements/ai_credits.py) e riconciliazione
cooldown/crediti (app/ai/service.py, app/jobs/tasks.py::run_ai_analysis_job)."""
from datetime import datetime, timezone

import pytest

from app.entitlements.ai_credits import consume_credits, grant_credits
from app.models import AiCreditTransaction, AiAnalyzerConfig


def test_grant_credits_updates_balance_and_ledger(db_session, make_user):
    user = make_user(ai_credit_balance=0)
    tx = grant_credits(user, 500, type="grant_purchase")
    assert user.ai_credit_balance == 500
    assert tx.amount == 500
    assert tx.balance_after == 500
    assert tx.type == "grant_purchase"


def test_grant_credits_rejects_non_positive_amount(db_session, make_user):
    user = make_user()
    with pytest.raises(ValueError):
        grant_credits(user, 0, type="grant_purchase")
    with pytest.raises(ValueError):
        grant_credits(user, -10, type="grant_purchase")


def test_consume_credits_deducts_balance(db_session, make_user):
    user = make_user(ai_credit_balance=10)
    tx = consume_credits(user, 3, site_url="https://example.com/")
    assert user.ai_credit_balance == 7
    assert tx.amount == -3
    assert tx.balance_after == 7
    assert tx.type == "consume"


def test_consume_credits_returns_none_when_insufficient(db_session, make_user):
    user = make_user(ai_credit_balance=2)
    result = consume_credits(user, 5)
    assert result is None
    assert user.ai_credit_balance == 2  # invariato


def test_ledger_records_every_transaction(db_session, make_user):
    user = make_user(ai_credit_balance=0)
    grant_credits(user, 500, type="grant_purchase")
    consume_credits(user, 1)
    consume_credits(user, 1)
    count = AiCreditTransaction.query.filter_by(user_id=user.id).count()
    assert count == 3


# --- riconciliazione cooldown/crediti -------------------------------------


def test_cooldown_disabled_for_credit_mode_plans():
    from app.ai.service import _cooldown_remaining
    from app.entitlements.limits import PLAN_LIMITS

    cfg = AiAnalyzerConfig(user_id=1, site_url="https://example.com/", enabled=True)
    cfg.last_run_at = datetime.now(timezone.utc).replace(tzinfo=None)  # run appena fatto

    cooldown_limits = PLAN_LIMITS["trial"]
    credit_limits = PLAN_LIMITS["subscription_monthly"]

    assert _cooldown_remaining(cfg, cooldown_limits) > 0  # invariato: cooldown reale
    assert _cooldown_remaining(cfg, credit_limits) == 0   # crediti: nessun cooldown


def test_cooldown_remaining_unchanged_without_limits_arg():
    # Compatibilità: il parametro limits è opzionale, il comportamento
    # pre-esistente (nessun piano passato) non deve cambiare.
    from app.ai.service import _cooldown_remaining

    cfg = AiAnalyzerConfig(user_id=1, site_url="https://example.com/", enabled=True)
    cfg.last_run_at = datetime.now(timezone.utc).replace(tzinfo=None)
    assert _cooldown_remaining(cfg) > 0


def test_analyze_route_blocks_credit_plan_at_zero_balance(app, client, db_session, make_user):
    from tests.test_appsumo_redeem import _login

    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=0)
    _login(client, user)

    res = client.post("/ai/toggle", data={"site": "https://example.com/", "enabled": "true"})
    assert res.status_code == 200

    res = client.post("/ai/analyze", data={"site": "https://example.com/"})
    assert res.status_code == 402
    data = res.get_json()
    assert data["error"] == "insufficient_credits"
    assert data["upsell"] is None  # Pro: niente pacchetti extra, si aspetta il rinnovo mensile


def test_analyze_route_queues_for_credit_plan_with_balance(app, client, db_session, make_user, monkeypatch):
    from tests.test_appsumo_redeem import _login

    user = make_user(plan_type="subscription_monthly", subscription_status="active", ai_credit_balance=10)
    _login(client, user)
    client.post("/ai/toggle", data={"site": "https://example.com/", "enabled": "true"})

    captured = {}

    class FakeJob:
        id = "fake-job-id"

    class FakeQueue:
        def enqueue(self, fn, *args, **kwargs):
            captured["fn"] = fn
            captured["args"] = args
            return FakeJob()

    monkeypatch.setattr("app.ai.routes.get_queue", lambda name: FakeQueue())

    res = client.post("/ai/analyze", data={"site": "https://example.com/"})
    assert res.status_code == 200
    assert res.get_json() == {"status": "queued", "job_id": "fake-job-id"}
    assert captured["args"] == (user.id, "https://example.com/")


def test_run_ai_analysis_job_consumes_credit_only_for_credit_mode(app, db_session, make_user, monkeypatch):
    from app.jobs.tasks import run_ai_analysis_job

    monkeypatch.setattr("app.jobs.tasks.get_worker_app", lambda: app)

    user = make_user(plan_type="subscription_monthly", ai_credit_balance=5)
    # Nessun GscConnection: il job esce presto con "not_connected", NON deve
    # consumare crediti (si consuma solo a run riuscita).
    result = run_ai_analysis_job(user.id, "https://example.com/")
    assert result == {"ok": False, "error": "not_connected"}
    db_session.refresh(user)
    assert user.ai_credit_balance == 5  # invariato
