"""Fixture harness Flask/DB — il primo di questo repo (test_rules.py testa
app/rules/engine.py in isolamento puro, senza Flask/DB).

Gotcha da rispettare: `create_app()` registra le view di Flask-Admin sul
singleton globale `app.extensions.admin` (via app/admin/__init__.py::init_admin).
Chiamarlo due volte nello stesso processo fa esplodere Flask-Admin con "view
already registered" — lo stesso problema già documentato nel commento di
`init_db_schema()` in app/__init__.py. Per questo `app` è una fixture
session-scoped: create_app() gira esattamente una volta per l'intera sessione
di test, mai per singolo test.
"""
import secrets

import pytest
from cryptography.fernet import Fernet
from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import db as _db
from config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # StaticPool: una singola connessione condivisa per tutto il processo,
    # altrimenti ogni nuova connessione a "sqlite:///:memory:" vedrebbe un DB
    # vuoto diverso (SQLite in-memory non è condiviso tra connessioni per
    # default).
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    }
    SECRET_KEY = "test-secret-key"
    TOKEN_ENCRYPTION_KEY = Fernet.generate_key().decode()
    APP_BASE_URL = "http://localhost:3000"
    # Flask-Limiter usa Redis in dev/prod (vedi RATELIMIT_STORAGE_URI in
    # config.py) — nei test non c'è un Redis reale, e testare l'enforcement
    # del rate limit non è lo scopo di questa suite (la scelta del limite
    # per piano, _rate_limit_value, si testa come funzione pura). Disabilitato
    # invece di puntare a un fake storage: più semplice e altrettanto onesto.
    RATELIMIT_ENABLED = False
    # Provider esterni non configurati nei test: il codice applicativo gestisce
    # già "non configurato" senza eccezioni (vedi dev_fallback_enabled in
    # app/auth/otp.py, resend_configured in app/emails/__init__.py, ecc.).
    RESEND_API = None
    DEEPSEEK_API = None
    # Link Revolut di test — non reali, solo per verificare che le CTA in
    # /billing/upgrade si abilitino quando configurati (vedi
    # tests/test_revolut_activation.py per il caso "non configurato").
    REVOLUT_PAYMENT_LINK_1M = "https://pay.revolut.com/test-1m"
    REVOLUT_PAYMENT_LINK_3M = "https://pay.revolut.com/test-3m"
    REVOLUT_PAYMENT_LINK_12M = "https://pay.revolut.com/test-12m"


@pytest.fixture(scope="session")
def app():
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture()
def db_session(app):
    """Isolamento per-test: ogni test parte da schema pulito senza mai
    richiamare create_app() più di una volta (vedi docstring del modulo).

    Nota: il pattern SQLAlchemy "join a session into an external transaction"
    (SAVEPOINT + rollback) è quello da manuale, ma con la scoped_session di
    Flask-SQLAlchemy 3.x e SQLite in-memory è risultato fragile in pratica
    (ResourceClosedError non appena il codice applicativo, che chiama
    db.session.commit() liberamente, chiude la transazione esterna). Più
    semplice e altrettanto corretto per lo schema di questa app: svuotare
    tutte le tabelle dopo ogni test invece di fare rollback di una
    transazione. Più lento di un vero SAVEPOINT ma trascurabile per le
    dimensioni di questo DB di test."""
    with app.app_context():
        yield _db.session
        _db.session.remove()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(db_session):
    from app.models import User

    def _make(email=None, plan_type="trial", subscription_status="trialing", **kwargs):
        email = email or f"user-{secrets.token_hex(4)}@example.com"
        user = User(
            name=kwargs.pop("name", "Test User"),
            email=email,
            plan_type=plan_type,
            subscription_status=subscription_status,
            email_verified=True,
            **kwargs,
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        return user

    return _make
