"""Unit test diretti su app/billing/paddle_client.py: verifica firma
(HMAC su raw body, non su JSON riparsato) e propagazione degli errori senza
mai includere la API key nel messaggio."""
import hashlib
import hmac
import time

from app.billing.paddle_client import verify_webhook_signature

SECRET = "shh-webhook-secret"


def _sign(body: bytes, ts: int) -> str:
    h1 = hmac.new(SECRET.encode(), f"{ts}:".encode() + body, hashlib.sha256).hexdigest()
    return f"ts={ts};h1={h1}"


def test_verify_valid_signature():
    body = b'{"event_id":"evt_1"}'
    ts = int(time.time())
    assert verify_webhook_signature(body, _sign(body, ts), SECRET) is True


def test_verify_rejects_tampered_body():
    body = b'{"event_id":"evt_1"}'
    ts = int(time.time())
    sig = _sign(body, ts)
    tampered = b'{"event_id":"evt_2"}'
    assert verify_webhook_signature(tampered, sig, SECRET) is False


def test_verify_rejects_wrong_secret():
    body = b'{"event_id":"evt_1"}'
    ts = int(time.time())
    assert verify_webhook_signature(body, _sign(body, ts), "different-secret") is False


def test_verify_rejects_stale_timestamp():
    body = b'{"event_id":"evt_1"}'
    old_ts = int(time.time()) - 3600
    assert verify_webhook_signature(body, _sign(body, old_ts), SECRET) is False


def test_verify_rejects_future_timestamp_beyond_tolerance():
    body = b'{"event_id":"evt_1"}'
    future_ts = int(time.time()) + 3600
    assert verify_webhook_signature(body, _sign(body, future_ts), SECRET) is False


def test_verify_rejects_missing_header():
    assert verify_webhook_signature(b"{}", None, SECRET) is False


def test_verify_rejects_missing_secret():
    body = b'{"event_id":"evt_1"}'
    ts = int(time.time())
    assert verify_webhook_signature(body, _sign(body, ts), None) is False


def test_verify_rejects_malformed_header():
    assert verify_webhook_signature(b"{}", "not-a-valid-header", SECRET) is False


def test_verify_never_raises_on_garbage_input():
    # Un endpoint pubblico riceve di tutto — non deve mai sollevare, solo
    # tornare False.
    assert verify_webhook_signature(b"", "ts=abc;h1=xyz", SECRET) is False
    assert verify_webhook_signature(b"{}", "h1=onlyh1", SECRET) is False
    assert verify_webhook_signature(b"{}", "ts=123", SECRET) is False


def test_paddle_api_error_never_includes_the_api_key(app, monkeypatch):
    import app.billing.paddle_client as paddle_client

    def _fake_request(method, url, headers=None, json=None, timeout=None):
        class R:
            status_code = 401
            text = '{"error":{"detail":"Unauthorized"}}'
            content = text.encode()

            def json(self):
                return {}

        return R()

    monkeypatch.setattr(paddle_client.requests, "request", _fake_request)
    monkeypatch.setitem(app.config, "PADDLE_API_KEY", "super-secret-key-should-never-leak")

    with app.test_request_context():
        try:
            paddle_client.create_transaction(items=[], custom_data={})
        except paddle_client.PaddleAPIError as exc:
            assert "super-secret-key-should-never-leak" not in str(exc)
        else:
            raise AssertionError("expected PaddleAPIError")
