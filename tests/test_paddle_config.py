"""Selezione sandbox/production (app/billing/paddle_client.py) — PADDLE_ENVIRONMENT
è l'UNICA leva che deve decidere il base URL e la risoluzione dei price ID,
nessun'altra condizione (host, DEBUG, ecc.)."""
import pytest

from app.billing.paddle_client import (
    PRODUCTION_BASE_URL,
    SANDBOX_BASE_URL,
    PaddleConfigError,
    base_url,
    get_environment,
)
from app.billing.paddle_products import PADDLE_SUBSCRIPTION_PLANS, resolve_price_id


def test_default_environment_is_sandbox(app):
    with app.test_request_context():
        assert get_environment() == "sandbox"
        assert base_url() == SANDBOX_BASE_URL


def test_production_environment_switches_base_url(app, monkeypatch):
    monkeypatch.setitem(app.config, "PADDLE_ENVIRONMENT", "production")
    with app.test_request_context():
        assert get_environment() == "production"
        assert base_url() == PRODUCTION_BASE_URL


def test_invalid_environment_value_raises(app, monkeypatch):
    monkeypatch.setitem(app.config, "PADDLE_ENVIRONMENT", "staging")
    with app.test_request_context():
        with pytest.raises(PaddleConfigError):
            get_environment()


def test_environment_is_case_insensitive(app, monkeypatch):
    monkeypatch.setitem(app.config, "PADDLE_ENVIRONMENT", "SANDBOX")
    with app.test_request_context():
        assert get_environment() == "sandbox"


def test_sandbox_resolves_sandbox_price_ids(app):
    with app.test_request_context():
        assert resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, "paddle_1m") == "pri_test_1m"


def test_production_price_ids_not_configured_in_tests(app, monkeypatch):
    # Sentinella: nei test l'environment production non ha MAI price ID
    # configurati, quindi resolve_price_id deve tornare None — se un giorno
    # qualcuno aggiunge per sbaglio dei valori production a TestConfig, e
    # magari sbaglia a settare l'environment nel codice applicativo, questo
    # test lo scopre subito invece di lasciare un test sandbox "passare per
    # caso" contro dati production.
    monkeypatch.setitem(app.config, "PADDLE_ENVIRONMENT", "production")
    with app.test_request_context():
        assert resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, "paddle_1m") is None


def test_sandbox_and_production_price_ids_never_mixed(app, monkeypatch):
    monkeypatch.setitem(app.config, "PADDLE_PRODUCTION_PRICE_ID_1M", "pri_prod_1m")
    with app.test_request_context():
        assert resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, "paddle_1m") == "pri_test_1m"
    monkeypatch.setitem(app.config, "PADDLE_ENVIRONMENT", "production")
    with app.test_request_context():
        assert resolve_price_id(PADDLE_SUBSCRIPTION_PLANS, "paddle_1m") == "pri_prod_1m"
