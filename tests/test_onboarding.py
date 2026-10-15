"""Checklist onboarding in Overview (app/templates/partials/onboarding_steps.html,
stato calcolato in app/dashboard/routes.py::overview): il prossimo passo segue
i dati reali dell'utente e la checklist sparisce a percorso completato."""
from app.models import AuditPresentation, GscConnection, MonitoredSite


def _login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True


def test_new_user_is_sent_to_connect_google(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    _login(client, user)
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "onboarding-title" in body
    assert 'class="btn btn-primary shrink-0" href="/dashboard/connect"' in body


def test_connected_user_without_sites_is_sent_to_sites(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    db_session.add(GscConnection(user_id=user.id, access_token="x", token_uri="x", scopes="x"))
    db_session.commit()
    _login(client, user)
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'class="btn btn-primary shrink-0" href="/dashboard/sites"' in body


def test_checklist_disappears_when_flow_is_complete(client, db_session, make_user):
    user = make_user(plan_type="appsumo_tier1", subscription_status="lifetime")
    db_session.add_all([
        GscConnection(user_id=user.id, access_token="x", token_uri="x", scopes="x"),
        MonitoredSite(user_id=user.id, site_url="https://example.com/", is_active=True),
        AuditPresentation(user_id=user.id, site_url="https://example.com/", title="t", markdown="m"),
    ])
    db_session.commit()
    _login(client, user)
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "onboarding-title" not in body
