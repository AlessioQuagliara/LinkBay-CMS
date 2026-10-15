"""Harness per i test di sicurezza (audit 2026-10-15).

Isolamento:
- DB SQLite in memoria, utenti/credenziali fittizi, nessun .env letto
  (eseguire con PYTHON_DOTENV_DISABLED=1, vedi REPORT.md);
- rete in uscita bloccata a livello di socket (solo loopback/unix);
- Redis sostituito da fakeredis; email/OAuth/AI sostituiti da stub.

A differenza di tests/conftest.py qui CSRF e rate limit restano ATTIVI:
sono proprio i controlli da verificare.
"""
import re
import socket
from datetime import datetime, timedelta, timezone

import fakeredis
import pytest
from cryptography.fernet import Fernet
from sqlalchemy.pool import StaticPool

from config import Config

_real_connect = socket.socket.connect


def _guarded_connect(self, address):
    host = address[0] if isinstance(address, tuple) else address
    if isinstance(host, str) and (host.startswith("/") or host in ("127.0.0.1", "::1", "localhost")):
        return _real_connect(self, address)
    raise RuntimeError(f"Connessione di rete bloccata dalla suite di sicurezza: {address!r}")


socket.socket.connect = _guarded_connect


class SecConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
    SECRET_KEY = "security-test-secret"
    TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode()
    APP_BASE_URL = "http://localhost:3000"
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    REDIS_URL = "redis://fake-redis-not-used:6379/0"
    RESEND_API = None
    DEEPSEEK_API = None
    TURNSTILE_SITE_KEY = None
    TURNSTILE_SECRET_KEY = None
    GOOGLE_CLIENT_ID = "fake-client-id"
    GOOGLE_CLIENT_SECRET = "fake-client-secret"
    GOOGLE_REDIRECT_URI = "http://localhost:3000/gsc/callback"
    PADDLE_API_KEY = "fake"
    PADDLE_WEBHOOK_SECRET = "fake"


@pytest.fixture(scope="session")
def app():
    from app import create_app
    from app.extensions import db

    application = create_app(SecConfig)
    # Le richieste del test client girano dentro l'app context della fixture,
    # quindi `g` (dove Flask-Login mette l'utente) sopravvivrebbe tra richieste
    # e tra client diversi (stesso per il token CSRF di Flask-WTF). In
    # produzione ogni richiesta ha il suo app context: qui lo si ripristina
    # svuotando `g` prima di ogni richiesta.
    from flask import g

    def _fresh_login_cache():
        for key in list(g):
            g.pop(key, None)

    application.before_request_funcs.setdefault(None, []).insert(0, _fresh_login_cache)
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture(autouse=True)
def db_session(app):
    from app.extensions import db, limiter

    with app.app_context():
        limiter.reset()
        yield db.session
        db.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    from app.jobs import concurrency, queue

    r = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(queue, "get_redis", lambda: r)
    monkeypatch.setattr(concurrency, "get_redis", lambda: r)
    return r


@pytest.fixture(autouse=True)
def sent_emails(monkeypatch):
    """Nessuna email reale: registra soltanto le chiamate."""
    sent = []

    def fake_send(to, subject, html, text=None, **kw):
        sent.append({"to": to, "subject": subject})
        return True

    monkeypatch.setattr("app.auth.otp.send_email", fake_send)
    monkeypatch.setattr("app.auth.password_reset.send_email", fake_send)
    return sent


@pytest.fixture()
def make_user(db_session):
    from app.models import User

    counter = {"n": 0}

    def _make(email=None, password="Passw0rd!secure", **kw):
        counter["n"] += 1
        user = User(
            name=kw.pop("name", f"User {counter['n']}"),
            email=email or f"user{counter['n']}@example.com",
            plan_type=kw.pop("plan_type", "appsumo_tier1"),
            subscription_status=kw.pop("subscription_status", "lifetime"),
            email_verified=True,
            trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7),
            **kw,
        )
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        return user

    return _make


def echo_result(**kw):
    """Funzione importabile per creare job RQ finti (eseguiti in-process)."""
    return kw


def login(client, user):
    """Sessione autenticata senza passare dall'OTP (il flusso OTP ha test dedicati)."""
    with client.session_transaction() as s:
        s["_user_id"] = str(user.id)
        s["_fresh"] = True


_TOKEN_RES = [
    re.compile(r'name="csrf-token" content="([^"]+)"'),
    re.compile(r'name="(?:[\w-]+-)?csrf_token"[^>]*value="([^"]+)"'),
    re.compile(r'value="([^"]+)"[^>]*name="(?:[\w-]+-)?csrf_token"'),
]


def csrf_token(client, path="/dashboard/sites"):
    html = client.get(path).get_data(as_text=True)
    for rx in _TOKEN_RES:
        m = rx.search(html)
        if m:
            return m.group(1)
    raise AssertionError(f"CSRF token non trovato in {path}")


@pytest.fixture()
def two_users(make_user, db_session):
    """A e B con risorse distinte su siti distinti."""
    from datetime import date

    from app.models import AuditPresentation, GscPageMonthly, MonitoredSite, PageAlert

    a = make_user(email="alice@example.com")
    b = make_user(email="bob@example.com")
    res = {"A": a, "B": b, "site_a": "https://alice.example/", "site_b": "https://bob.example/"}
    for user, site in ((a, res["site_a"]), (b, res["site_b"])):
        db_session.add(MonitoredSite(user_id=user.id, site_url=site))
        db_session.add(GscPageMonthly(user_id=user.id, site_url=site, page_url=site + "secret-page",
                                      month=date(2026, 9, 1), clicks=42, impressions=100))
        alert = PageAlert(user_id=user.id, site_url=site, url=site + "secret-page",
                          window_end=date(2026, 9, 30), priority_score=10, status="new",
                          reason_text=f"reason-of-{user.email}")
        db_session.add(alert)
        pres = AuditPresentation(user_id=user.id, site_url=site, title=f"audit-of-{user.email}",
                                 markdown=f"# audit-of-{user.email}\n\n- line")
        db_session.add(pres)
        db_session.commit()
        res[f"alert_{'a' if user is a else 'b'}"] = alert.id
        res[f"pres_{'a' if user is a else 'b'}"] = pres.id
    return res
