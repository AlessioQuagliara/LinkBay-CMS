"""Accredito manuale top-up crediti AI via Revolut
(app/billing/revolut_ai_topup.py + app/admin/views.py::RevolutAiTopupView) —
vendita UNA TANTUM, distinta dagli abbonamenti Pro (vedi
tests/test_revolut_activation.py). Nessun test qui deve mai osservare un
cambiamento di plan_type/subscription_status/subscription_expires_at: se
succede, è un bug (un top-up ha toccato lo stato dell'abbonamento).

Convenzione: un solo login per test (mai un GET anonimo intercalato con un
login via session_transaction nello stesso test) — mescolarli rompe la
sessione nel test client di Werkzeug indipendentemente dal codice applicativo
(riprodotto anche su main.index, invariato da questa migrazione)."""
import pytest

from app.billing.revolut_ai_topup import RevolutAiTopupError, credit_revolut_ai_topup
from app.billing.revolut_products import AI_TOPUP_CATALOG
from app.models import AiCreditTransaction


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def _topup_url(user_id):
    return f"/admin/revolut-ai-topup/{user_id}"


# --- autorizzazione ----------------------------------------------------


def test_non_admin_cannot_reach_topup_route(client, db_session, make_user):
    non_admin = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", is_admin=False)
    target = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="target@example.com")
    _login(client, non_admin)

    res = client.get(_topup_url(target.id), follow_redirects=False)
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]

    db_session.refresh(target)
    assert target.ai_credit_balance == 0


def test_admin_can_reach_and_submit_topup_route(client, db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin@example.com")
    target = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="target@example.com")
    _login(client, admin)

    res = client.get(_topup_url(target.id))
    assert res.status_code == 200

    res = client.post(
        _topup_url(target.id),
        data={"product_key": "ai_topup_starter", "payment_reference": "REF-A1", "note": ""},
        follow_redirects=False,
    )
    assert res.status_code == 302
    db_session.refresh(target)
    assert target.ai_credit_balance == 50


# --- eleggibilità --------------------------------------------------------


def test_ineligible_user_is_rejected_by_service(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin1@example.com")
    # Pro non è eleggibile ai top-up (quota mensile già inclusa) — stessa
    # regola già in uso per /billing/credits.
    user = make_user(plan_type="subscription_monthly", subscription_status="active", email="pro1@example.com")

    with pytest.raises(RevolutAiTopupError):
        credit_revolut_ai_topup(
            user=user, product_key="ai_topup_starter", payment_reference="REF-B1", admin=admin
        )
    db_session.refresh(user)
    assert user.ai_credit_balance == 0


def test_ineligible_user_is_blocked_at_the_admin_route(client, db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin2@example.com")
    user = make_user(plan_type="subscription_monthly", subscription_status="active", email="pro2@example.com")
    _login(client, admin)

    res = client.get(_topup_url(user.id), follow_redirects=False)
    assert res.status_code == 302  # redirect alla lista utenti, nessun form mostrato


# --- ogni pacchetto accredita esattamente i crediti definiti server-side --


@pytest.mark.parametrize("product_key", ["ai_topup_starter", "ai_topup_growth", "ai_topup_scale"])
def test_each_package_grants_its_exact_catalog_amount(db_session, make_user, product_key):
    admin = make_user(plan_type="trial", is_admin=True, email=f"admin-{product_key}@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email=f"user-{product_key}@example.com")

    result = credit_revolut_ai_topup(
        user=user, product_key=product_key, payment_reference=f"REF-{product_key}", admin=admin
    )

    expected_credits = AI_TOPUP_CATALOG[product_key]["credits"]
    assert result.credits_added == expected_credits
    db_session.refresh(user)
    assert user.ai_credit_balance == expected_credits


def test_invalid_package_is_rejected_server_side(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin3@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user3@example.com")

    with pytest.raises(RevolutAiTopupError):
        credit_revolut_ai_topup(user=user, product_key="ai_topup_mega", payment_reference="REF-C1", admin=admin)
    db_session.refresh(user)
    assert user.ai_credit_balance == 0


def test_client_supplied_credits_and_price_are_ignored(client, db_session, make_user):
    # Il form non ha nemmeno un campo credits/price — questo test dimostra
    # che anche se un client li invia comunque (form contraffatto), il
    # server li ignora: la quantità accreditata viene SEMPRE dal catalogo.
    admin = make_user(plan_type="trial", is_admin=True, email="admin4@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user4@example.com")
    _login(client, admin)

    res = client.post(
        _topup_url(user.id),
        data={
            "product_key": "ai_topup_starter",
            "payment_reference": "REF-D1",
            "credits": "999999",
            "price": "0.01",
            "amount": "999999",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    db_session.refresh(user)
    assert user.ai_credit_balance == 50  # non 999999


# --- ledger: una sola transazione, balance corretto -----------------------


def test_exactly_one_transaction_is_created_with_correct_balances(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin5@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user5@example.com", ai_credit_balance=20)

    credit_revolut_ai_topup(user=user, product_key="ai_topup_growth", payment_reference="REF-E1", admin=admin, note="test")

    txs = AiCreditTransaction.query.filter_by(user_id=user.id).all()
    assert len(txs) == 1
    tx = txs[0]
    assert tx.type == "grant_purchase"
    assert tx.amount == 150
    assert tx.balance_before == 20
    assert tx.balance_after == 170
    assert tx.payment_reference == "REF-E1"
    assert tx.payment_source == "revolut_manual"
    assert tx.product_key == "ai_topup_growth"
    assert tx.approved_by_user_id == admin.id
    assert tx.admin_note == "test"

    db_session.refresh(user)
    assert user.ai_credit_balance == 170


# --- idempotenza del riferimento pagamento ---------------------------------


def test_same_reference_same_user_does_not_grant_twice(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin6@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user6@example.com")

    first = credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="REF-F1", admin=admin)
    assert first.already_processed is False

    second = credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="REF-F1", admin=admin)
    assert second.already_processed is True
    assert second.balance_after == first.balance_after

    db_session.refresh(user)
    assert user.ai_credit_balance == 50  # non 100
    assert AiCreditTransaction.query.filter_by(user_id=user.id).count() == 1


def test_reference_cannot_be_reused_for_a_different_user(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin7@example.com")
    user_a = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user7a@example.com")
    user_b = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user7b@example.com")

    credit_revolut_ai_topup(user=user_a, product_key="ai_topup_starter", payment_reference="REF-SHARED", admin=admin)

    with pytest.raises(RevolutAiTopupError):
        credit_revolut_ai_topup(user=user_b, product_key="ai_topup_starter", payment_reference="REF-SHARED", admin=admin)

    db_session.refresh(user_b)
    assert user_b.ai_credit_balance == 0


def test_double_submit_via_http_grants_credit_only_once(client, db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin8@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user8@example.com")
    _login(client, admin)

    for _ in range(2):
        client.post(
            _topup_url(user.id),
            data={"product_key": "ai_topup_starter", "payment_reference": "REF-G1", "note": ""},
            follow_redirects=False,
        )

    db_session.refresh(user)
    assert user.ai_credit_balance == 50
    assert AiCreditTransaction.query.filter_by(user_id=user.id).count() == 1


def test_double_submit_sends_email_once(db_session, make_user, monkeypatch):
    admin = make_user(plan_type="trial", is_admin=True, email="admin9@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user9@example.com")

    calls = []
    monkeypatch.setattr(
        "app.billing.revolut_ai_topup.send_revolut_ai_topup_activated_email",
        lambda user, **kw: calls.append(user.id) or True,
    )

    credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="REF-H1", admin=admin)
    credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="REF-H1", admin=admin)

    assert len(calls) == 1


def test_missing_payment_reference_is_rejected(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin10@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user10@example.com")

    with pytest.raises(RevolutAiTopupError):
        credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="", admin=admin)
    db_session.refresh(user)
    assert user.ai_credit_balance == 0


# --- reference condivisa fra abbonamento e top-up (cross-flow) ------------


def test_reference_used_for_subscription_cannot_fund_a_topup(db_session, make_user):
    from app.billing.revolut_manual_activation import activate_revolut_subscription

    admin = make_user(plan_type="trial", is_admin=True, email="admin11@example.com")
    sub_user = make_user(plan_type="trial", subscription_status="trialing", email="subuser11@example.com")
    topup_user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="topupuser11@example.com")

    activate_revolut_subscription(user=sub_user, plan="revolut_1m", admin=admin, payment_reference="REF-CROSS-1")

    with pytest.raises(RevolutAiTopupError):
        credit_revolut_ai_topup(user=topup_user, product_key="ai_topup_starter", payment_reference="REF-CROSS-1", admin=admin)

    db_session.refresh(topup_user)
    assert topup_user.ai_credit_balance == 0


def test_reference_used_for_topup_cannot_fund_a_subscription(db_session, make_user):
    from app.billing.revolut_manual_activation import RevolutActivationError, activate_revolut_subscription

    admin = make_user(plan_type="trial", is_admin=True, email="admin12@example.com")
    topup_user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="topupuser12@example.com")
    sub_user = make_user(plan_type="trial", subscription_status="trialing", email="subuser12@example.com")

    credit_revolut_ai_topup(user=topup_user, product_key="ai_topup_starter", payment_reference="REF-CROSS-2", admin=admin)

    with pytest.raises(RevolutActivationError):
        activate_revolut_subscription(user=sub_user, plan="revolut_1m", admin=admin, payment_reference="REF-CROSS-2")

    db_session.refresh(sub_user)
    assert sub_user.subscription_status == "trialing"


# --- email che fallisce non deve annullare il credito ----------------------


def test_email_failure_does_not_revoke_the_credit(db_session, make_user, monkeypatch):
    admin = make_user(plan_type="trial", is_admin=True, email="admin13@example.com")
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime", email="user13@example.com")

    def _boom(user, **kwargs):
        raise RuntimeError("Resend is down")

    monkeypatch.setattr("app.billing.revolut_ai_topup.send_revolut_ai_topup_activated_email", _boom)

    result = credit_revolut_ai_topup(user=user, product_key="ai_topup_starter", payment_reference="REF-I1", admin=admin)
    assert result.outcome == "credited"
    assert result.email_sent is False

    db_session.refresh(user)
    assert user.ai_credit_balance == 50  # non annullato dal fallimento email


# --- un top-up non tocca MAI il piano/abbonamento ---------------------------


def test_topup_never_touches_subscription_fields(db_session, make_user):
    admin = make_user(plan_type="trial", is_admin=True, email="admin14@example.com")
    user = make_user(plan_type="appsumo_tier2", subscription_status="lifetime", email="user14@example.com")

    credit_revolut_ai_topup(user=user, product_key="ai_topup_scale", payment_reference="REF-J1", admin=admin)

    db_session.refresh(user)
    assert user.plan_type == "appsumo_tier2"  # invariato
    assert user.subscription_status == "lifetime"  # invariato, mai declassato
    assert user.subscription_expires_at is None  # mai impostato da un top-up
    assert user.subscription_source is None  # invariato (nessun collegamento al top-up)


# --- CTA disabilitata/abilitata in base alla configurazione -----------------


def test_credits_page_cta_disabled_without_link_config(client, app, db_session, make_user, monkeypatch):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_50", None)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_150", None)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_500", None)

    res = client.get("/billing/credits")
    body = res.get_data(as_text=True)
    assert "Payment link not configured yet" in body


def test_credits_page_cta_enabled_with_link_config(client, app, db_session, make_user, monkeypatch):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    monkeypatch.setitem(app.config, "REVOLUT_AI_TOPUP_LINK_50", "https://pay.revolut.com/topup-50")

    res = client.get("/billing/credits")
    body = res.get_data(as_text=True)
    assert "https://pay.revolut.com/topup-50" in body
    assert 'rel="noopener noreferrer"' in body
    assert 'target="_blank"' in body


# --- AppSumo continua a funzionare (regressione) ----------------------------


def test_appsumo_lifetime_status_unaffected_by_topup_feature(db_session, make_user):
    # Nessun collegamento fra i due flussi: un top-up non blocca né altera il
    # riscatto/l'accesso lifetime AppSumo (invariato, vedi tests/test_appsumo_redeem.py).
    user = make_user(plan_type="appsumo_tier3", subscription_status="lifetime")
    assert user.has_active_access is True
