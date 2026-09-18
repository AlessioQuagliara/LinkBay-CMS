"""Riscatto codici AppSumo multi-tier (app/billing/routes.py::redeem) —
invariato dalla rimozione di Lemon Squeezy.

Nota: i test sulla migrazione controllata AppSumo->abbonamento
(appsumo_migration_unlocked bloccava un POST a /billing/checkout verso Lemon
Squeezy) sono stati rimossi insieme alla route stessa — /billing/checkout non
esiste più: il piano Pro si paga oggi via Paddle Billing (checkout
server-driven, vedi app/billing/paddle_routes.py), non più su un checkout
interno da gatekeepare. Il flag appsumo_migration_unlocked resta sul
modello/Flask-Admin ma non ha oggi alcun consumer applicativo (vedi
app/models/user.py)."""
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


def test_lemonsqueezy_checkout_and_webhook_routes_are_gone(client):
    # Regressione esplicita Fase 7: nessun endpoint Lemon Squeezy raggiungibile.
    assert client.post("/billing/checkout", data={"product_key": "pro_monthly"}).status_code == 404
    assert client.post("/billing/webhook", data=b"{}").status_code == 404
    assert client.get("/billing/portal").status_code == 404
    assert client.get("/billing/success").status_code == 404
