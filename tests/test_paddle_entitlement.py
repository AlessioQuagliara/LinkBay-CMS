"""has_active_entitlement (app/entitlements/service.py) — la fonte
autorevole di accesso multi-provider. Il ramo Paddle è quello nuovo (NULL
non concede mai accesso illimitato); ogni altro provider deve comportarsi
ESATTAMENTE come User.has_active_access, invariato."""
from datetime import datetime, timedelta, timezone

from app.entitlements.service import has_active_entitlement


def test_appsumo_lifetime_always_entitled(db_session, make_user):
    user = make_user(plan_type="appsumo_tier3", subscription_status="lifetime")
    assert has_active_entitlement(user) is True


def test_revolut_active_before_expiry_entitled(db_session, make_user):
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert has_active_entitlement(user) is True


def test_revolut_active_after_expiry_not_entitled(db_session, make_user):
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    assert has_active_entitlement(user) is False


def test_legacy_active_without_expiry_stays_entitled(db_session, make_user):
    # Comportamento legacy Lemon Squeezy invariato: NULL == "mai spento".
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    assert user.subscription_expires_at is None
    assert has_active_entitlement(user) is True


def test_trial_within_window_entitled(db_session, make_user):
    user = make_user(
        plan_type="trial", subscription_status="trialing",
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert has_active_entitlement(user) is True


def test_trial_expired_not_entitled(db_session, make_user):
    user = make_user(
        plan_type="trial", subscription_status="trialing",
        trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    assert has_active_entitlement(user) is False


# --- ramo Paddle: qui il comportamento DIVERGE deliberatamente da
# has_active_access (vedi docstring della funzione) --------------------------


def test_paddle_active_before_expiry_entitled(db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="active", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert has_active_entitlement(user) is True


def test_paddle_active_without_expiry_is_never_entitled(db_session, make_user):
    # Qui sta la differenza cruciale con has_active_access: per un utente
    # Paddle, NULL significa "mai sincronizzato da un webhook", non "nessuna
    # scadenza nota" — non deve MAI concedere accesso illimitato.
    user = make_user(plan_type="paddle_1m", subscription_status="active", subscription_source="paddle")
    assert user.subscription_expires_at is None
    assert has_active_entitlement(user) is False
    # E per contrasto, has_active_access (il vecchio property, invariato)
    # avrebbe concesso accesso qui — la ragion d'essere di questa funzione.
    assert user.has_active_access is True


def test_paddle_trialing_before_expiry_entitled(db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="trialing", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert has_active_entitlement(user) is True


def test_paddle_past_due_before_expiry_entitled(db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="past_due", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    assert has_active_entitlement(user) is True


def test_paddle_paused_not_entitled(db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="paused", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=10),
    )
    assert has_active_entitlement(user) is False


def test_paddle_canceled_not_entitled(db_session, make_user):
    user = make_user(
        plan_type="paddle_1m", subscription_status="canceled", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=10),
    )
    assert has_active_entitlement(user) is False


def test_paddle_lifetime_still_wins_over_paddle_fields(db_session, make_user):
    # Un utente AppSumo lifetime non può mai perdere l'accesso per via di
    # campi Paddle residui/errati — lifetime prevale sempre (vedi anche
    # app/billing/paddle_subscriptions.py::apply_subscription_event, stessa
    # regola lato webhook).
    user = make_user(
        plan_type="appsumo_tier1", subscription_status="lifetime", subscription_source="paddle",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(days=100),
    )
    assert has_active_entitlement(user) is True
