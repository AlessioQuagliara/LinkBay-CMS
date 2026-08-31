"""Riscatto codici AppSumo multi-tier (app/billing/routes.py::redeem) e
migrazione controllata AppSumo->abbonamento (checkout() bloccato senza
appsumo_migration_unlocked)."""
from app.extensions import db
from app.models import AppSumoCode


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _make_code(db_session, code="TESTCODE1", tier=2):
    row = AppSumoCode(code=code, tier=tier)
    db_session.add(row)
    db_session.commit()
    return row


def test_redeem_sets_plan_type_from_code_tier(client, db_session, make_user):
    user = make_user(plan_type="trial", subscription_status="trialing")
    _make_code(db_session, "TIER2CODE", tier=2)
    _login(client, user)

    res = client.post("/billing/redeem", data={"code": "tier2code"}, follow_redirects=False)
    assert res.status_code == 302

    db_session.refresh(user)
    assert user.subscription_status == "lifetime"
    assert user.plan_type == "appsumo_tier2"


def test_redeem_rejects_code_without_tier(client, db_session, make_user):
    user = make_user(plan_type="trial")
    _make_code(db_session, "NOTIER", tier=None)
    _login(client, user)

    res = client.post("/billing/redeem", data={"code": "NOTIER"}, follow_redirects=True)
    assert res.status_code == 200

    db_session.refresh(user)
    # Non riscattato: né lo stato né il plan_type devono essere cambiati.
    assert user.subscription_status == "trialing"
    assert user.plan_type == "trial"
    code = AppSumoCode.query.filter_by(code="NOTIER").first()
    assert code.is_redeemed is False


def test_redeem_rejects_already_redeemed_code(client, db_session, make_user):
    owner = make_user(email="owner@example.com")
    code = _make_code(db_session, "USEDCODE", tier=1)
    code.redeemed_by_user_id = owner.id
    from datetime import datetime, timezone
    code.redeemed_at = datetime.now(timezone.utc)
    db_session.commit()

    other = make_user(email="other@example.com", plan_type="trial")
    _login(client, other)
    client.post("/billing/redeem", data={"code": "USEDCODE"}, follow_redirects=True)

    db_session.refresh(other)
    assert other.plan_type == "trial"  # non toccato


def test_redeem_rejects_unknown_code(client, db_session, make_user):
    user = make_user(plan_type="trial")
    _login(client, user)
    client.post("/billing/redeem", data={"code": "DOESNOTEXIST"}, follow_redirects=True)
    db_session.refresh(user)
    assert user.plan_type == "trial"


# --- migrazione controllata AppSumo -> abbonamento ------------------------


def test_checkout_blocked_for_appsumo_user_without_migration_unlock(client, db_session, make_user):
    user = make_user(
        plan_type="appsumo_tier1", subscription_status="lifetime",
        appsumo_migration_unlocked=False,
    )
    _login(client, user)
    res = client.post("/billing/checkout", data={"product_key": "pro_monthly"}, follow_redirects=False)
    # Redirect a billing.subscription, NON a Lemon Squeezy (nessuna chiamata HTTP esterna).
    assert res.status_code == 302
    assert "/billing/subscription" in res.headers["Location"]


def test_checkout_allowed_for_appsumo_user_with_migration_unlocked(client, db_session, make_user, monkeypatch):
    user = make_user(
        plan_type="appsumo_tier1", subscription_status="lifetime",
        appsumo_migration_unlocked=True,
    )
    _login(client, user)

    monkeypatch.setattr(
        "app.billing.routes.ls.create_checkout_url",
        lambda user, product_key: "https://checkout.lemonsqueezy.com/fake",
    )
    res = client.post("/billing/checkout", data={"product_key": "pro_monthly"}, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"] == "https://checkout.lemonsqueezy.com/fake"


def test_checkout_credits_never_blocked_for_appsumo_user(client, db_session, make_user, monkeypatch):
    # I pacchetti crediti sono l'upsell naturale per gli utenti AppSumo — mai
    # bloccati dalla guardia di migrazione (quella riguarda solo i piani Pro).
    user = make_user(
        plan_type="appsumo_tier1", subscription_status="lifetime",
        appsumo_migration_unlocked=False,
    )
    _login(client, user)
    monkeypatch.setattr(
        "app.billing.routes.ls.create_checkout_url",
        lambda user, product_key: "https://checkout.lemonsqueezy.com/fake-credits",
    )
    res = client.post("/billing/checkout", data={"product_key": "credits_500"}, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"] == "https://checkout.lemonsqueezy.com/fake-credits"


def test_checkout_not_blocked_for_subscription_user(client, db_session, make_user, monkeypatch):
    user = make_user(plan_type="subscription_monthly", subscription_status="active")
    _login(client, user)
    monkeypatch.setattr(
        "app.billing.routes.ls.create_checkout_url",
        lambda user, product_key: "https://checkout.lemonsqueezy.com/fake",
    )
    res = client.post("/billing/checkout", data={"product_key": "pro_annual"}, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["Location"] == "https://checkout.lemonsqueezy.com/fake"
