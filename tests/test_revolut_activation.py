"""Attivazione manuale Revolut (app/billing/revolut_manual_activation.py +
app/admin/views.py::RevolutActivationView) — sostituisce il flusso Lemon
Squeezy (checkout/webhook, rimossi). Copre sia il service in isolamento sia
l'endpoint Flask-Admin end-to-end (autorizzazione, CSRF già disabilitato nei
test — vedi TestConfig)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.billing.revolut_manual_activation import RevolutActivationError, activate_revolut_subscription


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _activate_url(user_id):
    return f"/admin/revolut-activation/{user_id}"


# --- autorizzazione --------------------------------------------------------


def test_non_admin_cannot_reach_activation_route(client, db_session, make_user):
    # AdminAuthMixin.is_accessible() intercetta prima ancora che activate()
    # giri: un non-admin viene rediretto (inaccessible_callback), non vede
    # mai il form né tantomeno può sottomettere l'azione.
    non_admin = make_user(plan_type="trial", is_admin=False)
    target = make_user(plan_type="trial")
    _login(client, non_admin)

    res = client.get(_activate_url(target.id), follow_redirects=False)
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]

    res = client.post(_activate_url(target.id), data={"plan": "revolut_1m"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]

    db_session.refresh(target)
    assert target.subscription_status == "trialing"  # non toccato


def test_anonymous_cannot_reach_activation_route(client, db_session, make_user):
    target = make_user(plan_type="trial")
    res = client.get(_activate_url(target.id), follow_redirects=False)
    # AdminAuthMixin.inaccessible_callback -> redirect al login, non 200.
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]


def test_admin_can_reach_and_submit_activation_route(client, db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True)
    target = make_user(plan_type="trial", subscription_status="trialing")
    _login(client, admin)

    res = client.get(_activate_url(target.id))
    assert res.status_code == 200

    res = client.post(
        _activate_url(target.id),
        data={"plan": "revolut_1m", "payment_reference": "", "note": ""},
        follow_redirects=False,
    )
    assert res.status_code == 302
    db_session.refresh(target)
    assert target.subscription_status == "active"
    assert target.plan_type == "revolut_1m"
    assert target.subscription_source == "revolut_manual"
    assert target.subscription_activated_by_id == admin.id


# --- durata per piano (service, isolato) ------------------------------------


@pytest.mark.parametrize(
    "plan,days",
    [("revolut_1m", 30), ("revolut_3m", 90), ("revolut_12m", 365)],
)
def test_each_plan_extends_by_its_fixed_duration(db_session, make_user, plan, days):
    admin = make_user(plan_type="trial", is_admin=True, email="admin1@example.com")
    user = make_user(plan_type="trial", subscription_status="trialing", email=f"user-{plan}@example.com")

    before = datetime.now(timezone.utc)
    result = activate_revolut_subscription(user=user, plan=plan, admin=admin)
    after = datetime.now(timezone.utc)

    assert result.plan == plan
    # Tolleranza di qualche secondo per il tempo di esecuzione del test.
    assert before + timedelta(days=days) <= result.new_expiry <= after + timedelta(days=days)


def test_invalid_plan_is_rejected_server_side(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin2@example.com")
    user = make_user(plan_type="trial", email="target2@example.com")

    with pytest.raises(RevolutActivationError):
        activate_revolut_subscription(user=user, plan="revolut_6m", admin=admin)

    db_session.refresh(user)
    assert user.subscription_status == "trialing"  # non toccato


# --- estensione da scadenza futura vs now() ---------------------------------


def test_active_user_with_future_expiry_is_extended_from_that_date(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin3@example.com")
    future_expiry = datetime.now(timezone.utc) + timedelta(days=10)
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=future_expiry, email="target3@example.com",
    )

    result = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin)

    expected = future_expiry + timedelta(days=30)
    assert abs((result.new_expiry - expected).total_seconds()) < 2
    assert result.previous_expiry is not None


def test_expired_user_is_extended_from_now(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin4@example.com")
    past_expiry = datetime.now(timezone.utc) - timedelta(days=5)
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=past_expiry, email="target4@example.com",
    )

    before = datetime.now(timezone.utc)
    result = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin)
    after = datetime.now(timezone.utc)

    assert before + timedelta(days=30) <= result.new_expiry <= after + timedelta(days=30)


def test_user_with_no_prior_expiry_is_extended_from_now(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin5@example.com")
    user = make_user(plan_type="trial", subscription_status="trialing", email="target5@example.com")

    before = datetime.now(timezone.utc)
    result = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin)
    after = datetime.now(timezone.utc)

    assert before + timedelta(days=30) <= result.new_expiry <= after + timedelta(days=30)
    assert result.previous_expiry is None


# --- idempotenza per riferimento pagamento ----------------------------------


def test_same_payment_reference_does_not_extend_twice(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin6@example.com")
    user = make_user(plan_type="trial", subscription_status="trialing", email="target6@example.com")

    first = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin, payment_reference="REV-100")
    assert first.already_processed is False

    second = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin, payment_reference="REV-100")
    assert second.already_processed is True
    assert second.new_expiry == first.new_expiry  # non esteso una seconda volta


def test_double_submit_same_reference_sends_email_once(db_session, make_user, monkeypatch):
    admin = make_user(plan_type="trial", is_admin=True, email="admin7@example.com")
    user = make_user(plan_type="trial", subscription_status="trialing", email="target7@example.com")

    calls = []
    monkeypatch.setattr(
        "app.billing.revolut_manual_activation.send_revolut_subscription_activated_email",
        lambda user, **kw: calls.append(user.id) or True,
    )

    activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin, payment_reference="REV-200")
    activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin, payment_reference="REV-200")

    assert len(calls) == 1


def test_reusing_reference_for_a_different_user_is_rejected(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin8@example.com")
    user_a = make_user(plan_type="trial", email="target8a@example.com")
    user_b = make_user(plan_type="trial", email="target8b@example.com")

    activate_revolut_subscription(user=user_a, plan="revolut_1m", admin=admin, payment_reference="REV-SHARED")

    with pytest.raises(RevolutActivationError):
        activate_revolut_subscription(user=user_b, plan="revolut_1m", admin=admin, payment_reference="REV-SHARED")

    db_session.refresh(user_b)
    assert user_b.subscription_status == "trialing"  # non toccato


# --- email che fallisce non deve annullare l'attivazione --------------------


def test_email_failure_does_not_roll_back_activation(db_session, make_user, monkeypatch):
    admin = make_user(plan_type="trial", is_admin=True, email="admin9@example.com")
    user = make_user(plan_type="trial", subscription_status="trialing", email="target9@example.com")

    def _boom(user, **kwargs):
        raise RuntimeError("Resend is down")

    monkeypatch.setattr(
        "app.billing.revolut_manual_activation.send_revolut_subscription_activated_email", _boom
    )

    result = activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin)
    assert result.outcome == "activated"
    assert result.email_sent is False

    db_session.refresh(user)
    assert user.subscription_status == "active"  # non annullato dal fallimento email


# --- AppSumo lifetime non toccato -------------------------------------------


def test_appsumo_lifetime_user_is_rejected_by_service(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin10@example.com")
    user = make_user(plan_type="appsumo_tier2", subscription_status="lifetime", email="target10@example.com")

    with pytest.raises(RevolutActivationError):
        activate_revolut_subscription(user=user, plan="revolut_1m", admin=admin)

    db_session.refresh(user)
    assert user.subscription_status == "lifetime"
    assert user.plan_type == "appsumo_tier2"


def test_appsumo_lifetime_user_is_blocked_at_the_admin_route(client, db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin11@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="target11@example.com")
    _login(client, admin)

    res = client.get(_activate_url(user.id), follow_redirects=False)
    assert res.status_code == 302  # redirect alla lista utenti, nessun form mostrato

    db_session.refresh(user)
    assert user.subscription_status == "lifetime"
    assert user.plan_type == "appsumo_tier1"


# --- has_active_access rispetta subscription_expires_at ---------------------


def test_active_revolut_user_has_access_before_expiry(db_session, make_user):
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    assert user.has_active_access is True


def test_active_revolut_user_loses_access_after_expiry(db_session, make_user):
    user = make_user(
        plan_type="revolut_1m", subscription_status="active",
        subscription_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    assert user.has_active_access is False


def test_active_user_without_expiry_keeps_access(db_session, make_user):
    # Legacy Lemon Squeezy: subscription_status "active" senza mai aver avuto
    # una subscription_expires_at — non deve rompersi con questa migrazione.
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    assert user.subscription_expires_at is None
    assert user.has_active_access is True


def test_lifetime_appsumo_user_never_expires(db_session, make_user):
    user = make_user(plan_type="appsumo_tier3", subscription_status="lifetime")
    assert user.has_active_access is True


# --- CTA disabilitata quando il link Revolut non è configurato --------------


def test_upgrade_page_shows_working_cta_when_links_configured(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    _login(client, user)
    res = client.get("/billing/upgrade")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert "https://pay.revolut.com/test-1m" in body
    assert "https://pay.revolut.com/test-3m" in body
    assert "https://pay.revolut.com/test-12m" in body
    assert 'rel="noopener noreferrer"' in body
    assert 'target="_blank"' in body


def test_upgrade_page_disables_cta_when_link_not_configured(client, app, db_session, make_user, monkeypatch):
    user = make_user(plan_type="trial", subscription_status="trialing")
    _login(client, user)
    monkeypatch.setitem(app.config, "REVOLUT_PAYMENT_LINK_1M", None)

    res = client.get("/billing/upgrade")
    body = res.get_data(as_text=True)
    assert "https://pay.revolut.com/test-1m" not in body
    assert "https://pay.revolut.com/test-3m" in body  # gli altri due restano attivi
