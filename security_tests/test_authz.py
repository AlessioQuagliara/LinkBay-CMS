"""B. Autorizzazione e isolamento dati: A non deve vedere/toccare risorse di B.

Ogni test passa (verde) quando il controllo REGGE. I test marcati
`FINDING` invece passano quando il difetto è PRESENTE (documentano
l'evidenza; vanno invertiti come test di regressione dopo la fix).
"""
import pytest
from rq import Queue

from security_tests.conftest import csrf_token, echo_result, login


# --- Letture cross-utente ----------------------------------------------------

def test_alerts_list_does_not_leak_other_user(client, two_users):
    login(client, two_users["A"])
    r = client.get(f"/alerts/api/list?site={two_users['site_b']}&status=all")
    assert r.status_code == 200
    assert r.get_json()["alerts"] == []


def test_alerts_trend_does_not_leak_other_user(client, two_users):
    login(client, two_users["A"])
    site = two_users["site_b"]
    r = client.get(f"/alerts/api/trend?site={site}&page={site}secret-page")
    assert r.status_code == 200
    assert all(p["clicks"] == 0 for p in r.get_json()["series"])


def test_query_losses_requires_own_alert(client, two_users):
    login(client, two_users["A"])
    site = two_users["site_b"]
    r = client.get(f"/alerts/api/query-losses?site={site}&page={site}secret-page")
    assert r.status_code == 404


def test_audit_view_and_download_other_user_404(client, two_users):
    login(client, two_users["A"])
    pid = two_users["pres_b"]
    assert client.get(f"/dashboard/audits/{pid}").status_code == 404
    assert client.get(f"/dashboard/audits/{pid}/download").status_code == 404
    # controllo positivo: la propria è visibile
    assert client.get(f"/dashboard/audits/{two_users['pres_a']}").status_code == 200


def test_export_csv_other_user_site_has_no_rows(client, two_users):
    login(client, two_users["A"])
    r = client.get(f"/exports/declining.csv?site={two_users['site_b']}")
    assert r.status_code == 200
    assert "bob.example" not in r.get_data(as_text=True)


# --- Scritture cross-utente --------------------------------------------------

def test_alert_status_update_other_user_404(client, two_users, db_session):
    from app.models import PageAlert

    login(client, two_users["A"])
    tok = csrf_token(client)
    r = client.post("/alerts/api/status", data={"id": two_users["alert_b"], "status": "done"},
                    headers={"X-CSRFToken": tok})
    assert r.status_code == 404
    db_session.expire_all()
    assert db_session.get(PageAlert, two_users["alert_b"]).status == "new"


def test_remove_other_user_monitored_site_404(client, two_users, db_session):
    from app.models import MonitoredSite

    login(client, two_users["A"])
    tok = csrf_token(client)
    r = client.post("/gsc/api/monitored-site/remove", data={"site": two_users["site_b"]},
                    headers={"X-CSRFToken": tok})
    assert r.status_code == 404
    db_session.expire_all()
    row = MonitoredSite.query.filter_by(user_id=two_users["B"].id).one()
    assert row.is_active


# --- Job asincroni: ownership del job_id ------------------------------------

def _finished_job_of(user, fake_redis, payload):
    # Come le route reali (ai/routes.py, audits/routes.py): owner in job.meta.
    q = Queue("default", connection=fake_redis, is_async=False)
    job = q.enqueue(echo_result, meta={"user_id": user.id}, **payload)
    assert job.get_status() == "finished"
    return job.id


def test_ai_analyze_status_hides_other_users_job(client, two_users, fake_redis):
    job_id = _finished_job_of(two_users["B"], fake_redis, {"ok": False, "error": "ai_failed", "message": "msg-of-bob"})
    login(client, two_users["A"])
    assert client.get(f"/ai/analyze-status/{job_id}").get_json() == {"status": "not_found"}


def test_audit_generate_status_hides_other_users_job(client, two_users, fake_redis):
    job_id = _finished_job_of(two_users["B"], fake_redis, {"ok": True, "presentation_id": two_users["pres_b"]})
    login(client, two_users["A"])
    assert client.get(f"/dashboard/audits/generate-status/{job_id}").get_json() == {"status": "not_found"}


def test_job_status_owner_still_sees_own_result(client, two_users, fake_redis):
    job_id = _finished_job_of(two_users["A"], fake_redis, {"ok": True, "presentation_id": two_users["pres_a"]})
    login(client, two_users["A"])
    body = client.get(f"/dashboard/audits/generate-status/{job_id}").get_json()
    assert body["status"] == "finished" and body["presentation_id"] == two_users["pres_a"]


# --- Accesso anonimo ---------------------------------------------------------

ANON_GET = [
    "/dashboard/", "/dashboard/sites", "/dashboard/insights", "/dashboard/declining",
    "/alerts/api/list?site=x", "/alerts/api/trend?site=x&page=y", "/alerts/api/query-losses?site=x&page=y",
    "/gsc/api/sites", "/gsc/api/monitored-sites", "/gsc/api/insights?site=x", "/gsc/authorize",
    "/gsc/callback?state=x&code=y", "/ai/status?site=x", "/ai/analyze-status/abc",
    "/dashboard/audits/", "/dashboard/audits/1", "/dashboard/audits/1/download",
    "/dashboard/audits/generate-status/abc", "/exports/declining.csv?site=x", "/exports/declining.pdf?site=x",
    "/settings/", "/billing/credits", "/billing/redeem", "/billing/status",
]


@pytest.mark.parametrize("path", ANON_GET)
def test_anonymous_get_is_rejected(client, path):
    r = client.get(path)
    assert r.status_code in (302, 401), path
    if r.status_code == 302:
        assert "/auth/login" in r.headers["Location"], path


# --- CSRF --------------------------------------------------------------------

CSRF_POSTS = [
    "/alerts/api/status", "/gsc/api/monitored-site", "/gsc/api/monitored-site/remove", "/gsc/disconnect",
    "/ai/toggle", "/ai/analyze", "/dashboard/audits/generate", "/settings/", "/billing/redeem",
    "/billing/checkout/subscription", "/billing/checkout/credits", "/billing/customer-portal",
]


@pytest.mark.parametrize("path", CSRF_POSTS)
def test_state_changing_post_without_csrf_token_rejected(client, two_users, path):
    login(client, two_users["A"])
    r = client.post(path, data={"site": two_users["site_a"], "status": "done", "id": two_users["alert_a"]})
    assert r.status_code == 400, path


# --- Mass assignment ---------------------------------------------------------

def test_settings_ignores_privileged_fields(client, make_user, db_session):
    from app.models import User

    u = make_user(plan_type="trial", subscription_status="trialing")
    login(client, u)
    tok = csrf_token(client, "/settings/")
    r = client.post("/settings/", data={
        "csrf_token": tok, "profile-csrf_token": tok,
        "profile-name": "New Name", "profile-locale": "en", "profile-submit": "1",
        "is_admin": "1", "plan_type": "appsumo_tier3", "subscription_status": "lifetime",
        "ai_credit_balance": "99999", "white_label_enabled": "y",
    })
    assert r.status_code in (200, 302)
    db_session.expire_all()
    u = db_session.get(User, u.id)
    assert not u.is_admin
    assert u.plan_type == "trial"
    assert u.subscription_status == "trialing"
    assert (u.ai_credit_balance or 0) == 0
    assert not u.white_label_enabled
