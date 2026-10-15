"""D/E/F. Redirect, header HTTP, rate limit dietro proxy, limiti di piano, SECRET_KEY."""
import os
import subprocess
import sys
from pathlib import Path

from rq import Queue

from security_tests.conftest import csrf_token, login

REPO = Path(__file__).resolve().parents[1]


def test_FINDING_open_redirect_via_referer(client):
    r = client.get("/lang/en", headers={"Referer": "https://evil.example/phish"})
    assert r.status_code == 302 and r.headers["Location"] == "https://evil.example/phish"


def test_FINDING_no_security_headers(client):
    r = client.get("/")
    missing = [h for h in ("Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options",
                           "Strict-Transport-Security", "Referrer-Policy") if h not in r.headers]
    assert missing == ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options",
                       "Strict-Transport-Security", "Referrer-Policy"]


def test_session_cookie_flags_follow_https_base_url():
    code = (
        "import os; os.environ['APP_BASE_URL']='https://app.example'; "
        "from config import Config as C; "
        "print(C.SESSION_COOKIE_SECURE, C.SESSION_COOKIE_HTTPONLY, C.SESSION_COOKIE_SAMESITE)"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True,
                         env={"PATH": os.environ["PATH"], "PYTHON_DOTENV_DISABLED": "1"}, check=True)
    assert out.stdout.split() == ["True", "True", "Lax"]


def test_404_does_not_leak_traceback(client):
    body = client.get("/does-not-exist").get_data(as_text=True)
    assert "Traceback" not in body and "werkzeug" not in body.lower()


def test_FINDING_chat_rate_limit_keyed_on_forwarded_for(client, monkeypatch):
    """Il limite 8/min di /chat/ask usa l'IP risolto da ProxyFix (ultimo hop di
    X-Forwarded-For). Se l'app è raggiungibile senza un proxy che riscrive
    l'header, ruotarlo azzera il limite (ogni chiamata = costo DeepSeek)."""
    calls = []
    monkeypatch.setattr("app.chat.routes.chat_reply", lambda *a: calls.append(1) or "ok")
    same_ip = [client.post("/chat/ask", json={"message": "hi"},
                           headers={"X-Forwarded-For": "203.0.113.1"}).status_code for _ in range(10)]
    assert 429 in same_ip  # controllo: con IP fisso il limite scatta
    rotated = [client.post("/chat/ask", json={"message": "hi"},
                           headers={"X-Forwarded-For": f"203.0.113.{i + 10}"}).status_code for i in range(20)]
    assert 429 not in rotated


def test_FINDING_monitored_site_not_verified_against_gsc(client, make_user, monkeypatch, db_session):
    from app.models import MonitoredSite

    u = make_user()
    login(client, u)
    monkeypatch.setattr("app.gsc.gsc.get_user_gsc_service", lambda uid: (None, None))
    tok = csrf_token(client)
    r = client.post("/gsc/api/monitored-site", data={"site": "https://not-my-property.example/"},
                    headers={"X-CSRFToken": tok})
    assert r.status_code == 200
    assert MonitoredSite.query.filter_by(user_id=u.id, site_url="https://not-my-property.example/").count() == 1


def test_FINDING_insights_enqueues_scan_for_site_beyond_plan_limit(client, make_user, monkeypatch,
                                                                    db_session, fake_redis):
    from app.entitlements.service import get_plan_limits
    from app.models import MonitoredSite

    u = make_user(plan_type="appsumo_tier1")
    limit = get_plan_limits(u).site_limit
    for i in range(limit):
        db_session.add(MonitoredSite(user_id=u.id, site_url=f"https://s{i}.example/"))
    db_session.commit()
    login(client, u)
    tok = csrf_token(client)
    extra = "https://extra.example/"
    # controllo: l'aggiunta esplicita è bloccata dal limite
    assert client.post("/gsc/api/monitored-site", data={"site": extra},
                       headers={"X-CSRFToken": tok}).status_code == 403

    monkeypatch.setattr("app.gsc.gsc.get_user_gsc_service", lambda uid: (object(), object()))
    monkeypatch.setattr("app.gsc.gsc.build_insights", lambda *a, **k: {"pages": []})
    monkeypatch.setattr("app.gsc.gsc.get_site_series", lambda *a: [])
    monkeypatch.setattr("app.gsc.gsc.save_gsc_credentials", lambda *a: None)
    monkeypatch.setattr("app.gsc.gsc.credentials_to_dict", lambda c: {})
    r = client.get(f"/gsc/api/insights?site={extra}")
    assert r.status_code == 200 and r.get_json()["stale"] is True
    jobs = [j for name in ("high", "default", "low") for j in Queue(name, connection=fake_redis).jobs]
    assert any(j.args == (u.id, extra) for j in jobs)


import pytest


@pytest.mark.parametrize("value", [None, "", "dev-secret-key-change-me", "dev-secret-change-me"])
def test_app_refuses_to_start_with_missing_or_public_secret_key(value):
    env = {"PATH": os.environ["PATH"], "PYTHON_DOTENV_DISABLED": "1"}
    if value is not None:
        env["SECRET_KEY"] = value
    script = (
        "from config import Config\n"
        "class C(Config):\n"
        "    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'\n"
        "    RATELIMIT_ENABLED = False\n"
        "from app import create_app\n"
        "try:\n"
        "    create_app(C)\n"
        "except RuntimeError as e:\n"
        "    print('REFUSED', 'SECRET_KEY' in str(e))\n"
        "else:\n"
        "    print('STARTED')\n"
    )
    out = subprocess.run([sys.executable, "-c", script], cwd=REPO, capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr[-2000:]
    assert out.stdout.strip().splitlines()[-1] == "REFUSED True"


def test_app_starts_with_real_secret_key():
    env = {"PATH": os.environ["PATH"], "PYTHON_DOTENV_DISABLED": "1", "SECRET_KEY": "a" * 64}
    script = (
        "from config import Config\n"
        "class C(Config):\n"
        "    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'\n"
        "    RATELIMIT_ENABLED = False\n"
        "from app import create_app\n"
        "create_app(C); print('STARTED')\n"
    )
    out = subprocess.run([sys.executable, "-c", script], cwd=REPO, capture_output=True, text=True, env=env)
    assert out.stdout.strip().splitlines()[-1] == "STARTED", out.stderr[-2000:]


def test_prod_compose_does_not_publish_postgres_nor_hardcode_password():
    text = (REPO / "compose.prod.yml").read_text()
    db_block = text.split("\n  db:")[1].split("\n  web:")[0]
    assert "5432:5432" not in db_block and "ports:" not in db_block
    assert "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?" in db_block
    assert "linkbay:linkbay@" not in text
