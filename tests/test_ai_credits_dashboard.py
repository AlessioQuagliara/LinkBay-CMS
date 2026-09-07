"""Dashboard "Crediti AI" (app/templates/partials/ai_credits_card.html,
app/entitlements/service.py::get_ai_credit_overview) e storico
/billing/credits (app/billing/routes.py::credits) — saldo/piano/consumo
calcolati SOLO server-side dal ledger reale, mai da input del client.

Convenzione: un solo login per test, mai un GET anonimo intercalato con
session_transaction nello stesso test (vedi tests/test_revolut_ai_topup.py
per la spiegazione — è un artefatto del test client di Werkzeug, non
dell'app)."""
from datetime import datetime, timedelta, timezone

from app.entitlements.service import get_ai_credit_overview
from app.models import AiCreditTransaction


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


# --- get_ai_credit_overview (fonte di verità server-side) -------------------


def test_overview_balance_matches_user_field(db_session, make_user):
    user = make_user(plan_type="appsumo_tier2", subscription_status="lifetime", ai_credit_balance=42)
    overview = get_ai_credit_overview(user)
    assert overview.balance == 42
    assert overview.plan_name == "AppSumo Tier 2"


def test_overview_hides_monthly_quota_for_cooldown_plan(db_session, make_user):
    # Trial è ai_mode == "cooldown": nessuna quota mensile da promettere.
    user = make_user(plan_type="trial", subscription_status="trialing")
    overview = get_ai_credit_overview(user)
    assert overview.ai_mode == "cooldown"
    assert overview.monthly_quota == 0
    assert overview.next_monthly_grant_at is None


def test_overview_shows_monthly_quota_for_credit_plan(db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    overview = get_ai_credit_overview(user)
    assert overview.ai_mode == "credit"
    assert overview.monthly_quota == 10  # PLAN_LIMITS["appsumo_tier1"].ai_credit_grant


def test_overview_next_grant_only_when_active_and_credit_mode(db_session, make_user):
    active = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="a@example.com")
    assert get_ai_credit_overview(active).next_monthly_grant_at is not None

    expired = make_user(
        plan_type="revolut_1m", subscription_status="active", email="b@example.com",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    assert get_ai_credit_overview(expired).has_active_access is False
    assert get_ai_credit_overview(expired).next_monthly_grant_at is None


def test_overview_consumed_this_month_from_ledger(db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", ai_credit_balance=8)
    now = datetime.now(timezone.utc)
    db_session.add(AiCreditTransaction(
        user_id=user.id, type="consume", action="ai_analysis", amount=-2,
        balance_before=10, balance_after=8, created_at=now,
    ))
    db_session.commit()

    overview = get_ai_credit_overview(user)
    assert overview.consumed_this_month == 2


def test_overview_purchased_total_from_ledger(db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", ai_credit_balance=150)
    db_session.add(AiCreditTransaction(
        user_id=user.id, type="grant_purchase", amount=150, balance_before=0, balance_after=150,
        payment_source="revolut_manual", product_key="ai_topup_growth",
    ))
    db_session.commit()

    overview = get_ai_credit_overview(user)
    assert overview.purchased_total == 150


# --- dashboard overview card (rendering, non calcolo client-side) ----------


def test_overview_page_shows_balance_and_plan(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", ai_credit_balance=42)
    _login(client, user)
    res = client.get("/dashboard/")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "42 credits available" in body
    assert "AppSumo Tier 1" in body


def test_overview_page_does_not_show_monthly_quota_for_trial(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing", trial_ends_at=datetime.now(timezone.utc) + timedelta(days=5))
    _login(client, user)
    res = client.get("/dashboard/")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "Included monthly quota" not in body


def test_credits_page_shows_upgrade_message_for_inactive_plan(client, db_session, make_user):
    # Un piano scaduto viene bloccato dal gate globale su /dashboard/ (vedi
    # app/billing/access.py — "dashboard" è tra i blueprint gated), ma
    # /billing/credits resta sempre raggiungibile: è lì che si vede
    # davvero il ramo "piano non attivo" della card.
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    _login(client, user)
    res = client.get("/billing/credits")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "aren&#39;t available right now" in body or "aren't available right now" in body


# --- /billing/credits: login, isolamento, paginazione, dati sensibili ------


def test_credits_page_requires_login(client, db_session, make_user):
    res = client.get("/billing/credits", follow_redirects=False)
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]


def test_credits_page_shows_only_own_transactions(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="owner@example.com")
    other = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="other@example.com")

    db_session.add(AiCreditTransaction(
        user_id=user.id, type="grant_monthly_quota", amount=10, balance_before=0, balance_after=10,
    ))
    db_session.add(AiCreditTransaction(
        user_id=other.id, type="grant_monthly_quota", amount=999, balance_before=0, balance_after=999,
    ))
    db_session.commit()

    _login(client, user)
    res = client.get("/billing/credits")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "999" not in body


def test_credits_page_pagination(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", ai_credit_balance=25)
    for i in range(25):
        db_session.add(AiCreditTransaction(
            user_id=user.id, type="consume", action="ai_analysis", amount=-1,
            balance_before=25 - i, balance_after=24 - i,
        ))
    db_session.commit()

    _login(client, user)
    res = client.get("/billing/credits")
    assert res.status_code == 200
    assert "Page 1 of 2" in res.get_data(as_text=True)

    res2 = client.get("/billing/credits?page=2")
    assert res2.status_code == 200
    assert "Page 2 of 2" in res2.get_data(as_text=True)


def test_credits_page_hides_sensitive_admin_data(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="sensitive@example.com")
    admin = make_user(plan_type="trial", is_admin=True, email="secretadmin@example.com")
    db_session.add(AiCreditTransaction(
        user_id=user.id, type="grant_purchase", amount=150, balance_before=0, balance_after=150,
        payment_source="revolut_manual", product_key="ai_topup_growth",
        payment_reference="REV-SECRET-REF-12345", admin_note="Called customer, verified via phone.",
        approved_by_user_id=admin.id, ls_order_id="ls_legacy_999",
    ))
    db_session.commit()

    _login(client, user)
    res = client.get("/billing/credits")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "REV-SECRET-REF-12345" not in body
    assert "Called customer, verified via phone." not in body
    assert "secretadmin@example.com" not in body
    assert "ls_legacy_999" not in body


def test_credits_page_trial_user_redirected_no_ledger(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    _login(client, user)
    res = client.get("/billing/credits", follow_redirects=False)
    assert res.status_code == 302


# --- CTA acquisto: eleggibilità + link configurato/assente ------------------


def test_buy_cta_shown_for_eligible_appsumo_user(client, app, db_session, make_user, monkeypatch):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_50", "https://pay.revolut.com/test-topup-50")

    res = client.get("/billing/credits")
    body = res.get_data(as_text=True)
    assert "Pay with Revolut" in body
    assert "https://pay.revolut.com/test-topup-50" in body
    assert 'target="_blank"' in body
    assert 'rel="noopener noreferrer"' in body


def test_buy_cta_hidden_for_ineligible_pro_user(client, db_session, make_user):
    user = make_user(plan_type="revolut_1m", subscription_status="active")
    _login(client, user)
    res = client.get("/billing/credits")
    body = res.get_data(as_text=True)
    assert "Pay with Revolut" not in body


def test_buy_cta_disabled_when_link_not_configured(client, app, db_session, make_user, monkeypatch):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_50", None)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_150", None)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_500", None)

    res = client.get("/billing/credits")
    body = res.get_data(as_text=True)
    assert "Payment link not configured yet" in body
    assert "Pay with Revolut" not in body
