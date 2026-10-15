import pytest

from app.entitlements.limits import PLAN_LIMITS
from app.entitlements.service import (
    _level_for_ratio,
    check_ai_credits,
    check_site_limit,
    get_plan_limits,
    get_usage_summary,
    record_usage,
)
from app.gsc.sites import add_monitored_site


def test_plan_limits_covers_every_plan_type_used_in_the_codebase():
    # Valori usati altrove nel codice (redeem, checkout, webhook):
    # ognuno deve avere una entry in PLAN_LIMITS, altrimenti get_plan_limits
    # ricadrebbe silenziosamente su "trial" per un utente pagante.
    expected = {
        "trial",
        "appsumo_tier1",
        "appsumo_tier2",
        "appsumo_tier3",
        "subscription_monthly",
        "subscription_annual",
    }
    assert expected.issubset(PLAN_LIMITS.keys())


def test_get_plan_limits_falls_back_to_trial_for_none(db_session, make_user):
    user = make_user(plan_type=None)
    limits = get_plan_limits(user)
    assert limits is PLAN_LIMITS["trial"]


def test_get_plan_limits_falls_back_to_trial_for_unknown_value(db_session, make_user):
    user = make_user(plan_type="some_future_plan_not_yet_defined")
    limits = get_plan_limits(user)
    assert limits is PLAN_LIMITS["trial"]


@pytest.mark.parametrize(
    "used,limit,expected",
    [
        (0, 10, "ok"),
        (7, 10, "ok"),
        (8, 10, "warn_80"),
        (9, 10, "warn_80"),
        (9.5, 10, "warn_95"),  # confine 95%
        (10, 10, "blocked"),
        (11, 10, "blocked"),
        (5, -1, "ok"),  # -1 = illimitato, mai in warning/blocked
        (0, 0, "blocked"),  # limite 0 = feature non disponibile
    ],
)
def test_level_for_ratio_thresholds(used, limit, expected):
    assert _level_for_ratio(used, limit) == expected


def test_check_site_limit_blocks_at_tier1_cap(app, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1")  # site_limit=3 dalla richiesta
    with app.test_request_context():
        for i in range(3):
            add_monitored_site(user.id, f"https://site-{i}.example.com/")
        result = check_site_limit(user)
        assert result.allowed is False
        assert result.level == "blocked"
        assert result.upsell is not None


def test_check_site_limit_allows_under_cap(app, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1")
    with app.test_request_context():
        add_monitored_site(user.id, "https://site-0.example.com/")
        result = check_site_limit(user)
        assert result.allowed is True


def test_appsumo_upsell_is_ai_credits_not_subscription(app, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1")
    with app.test_request_context():
        for i in range(3):
            add_monitored_site(user.id, f"https://site-{i}.example.com/")
        result = check_site_limit(user)
        assert result.upsell["type"] == "ai_credits"


def test_subscription_upsell_is_subscription_upgrade(app, db_session, make_user):
    # trial/subscription_* hanno limiti troppo alti (100 siti) per triggerarli
    # aggiungendone davvero — _upsell_for è pura funzione di plan_type, va
    # bene testarla direttamente invece di forzare un limite reale.
    from app.entitlements.service import _upsell_for

    user = make_user(plan_type="trial")
    with app.test_request_context():
        upsell = _upsell_for(user)
        assert upsell["type"] == "subscription_upgrade"


def test_check_ai_credits_noop_for_cooldown_plans(db_session, make_user):
    # trial è l'unico piano ai_mode="cooldown": check_ai_credits non deve mai
    # bloccare, quel freno resta gestito dal cooldown esistente in app/ai/.
    user = make_user(plan_type="trial", ai_credit_balance=0)
    result = check_ai_credits(user)
    assert result.allowed is True


def test_check_ai_credits_blocks_at_zero_with_topup_upsell_for_appsumo(app, db_session, make_user):
    # AppSumo (ai_credit_topups_allowed=True): out-of-credits offre l'upsell
    # verso i pacchetti extra.
    user = make_user(plan_type="appsumo_tier1", ai_credit_balance=0)
    with app.test_request_context():
        result = check_ai_credits(user)
        assert result.allowed is False
        assert result.upsell["type"] == "ai_credits"


def test_check_ai_credits_blocks_at_zero_without_upsell_for_pro(app, db_session, make_user):
    # Pro (ai_credit_topups_allowed=False): la quota mensile è già generosa,
    # niente pacchetti extra da vendere — nessun upsell, si aspetta il rinnovo.
    user = make_user(plan_type="subscription_monthly", ai_credit_balance=0)
    with app.test_request_context():
        result = check_ai_credits(user)
        assert result.allowed is False
        assert result.upsell is None


def test_check_ai_credits_allows_when_balance_covers_cost(db_session, make_user):
    user = make_user(plan_type="subscription_monthly", ai_credit_balance=5)
    result = check_ai_credits(user, cost=1)
    assert result.allowed is True


def test_get_usage_summary_reflects_sites_and_credits(db_session, make_user):
    user = make_user(plan_type="appsumo_tier2", ai_credit_balance=42)
    add_monitored_site(user.id, "https://a.example.com/")
    add_monitored_site(user.id, "https://b.example.com/")

    summary = get_usage_summary(user)
    assert summary.sites_used == 2
    assert summary.sites_limit == 10  # appsumo_tier2 dalla richiesta
    assert summary.ai_credits_balance == 42


def test_record_usage_writes_log_entry(db_session, make_user):
    user = make_user()
    entry = record_usage(user, "site_added", site_url="https://example.com/")
    assert entry.id is not None
    assert entry.action == "site_added"
    assert entry.counted_against_limit is True
