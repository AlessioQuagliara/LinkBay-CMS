"""C. OAuth Google Search Console — Google sostituito da un Flow finto (nessuna rete)."""
import pytest

from security_tests.conftest import login

PLAIN_ACCESS = "ya29.FAKE-ACCESS-TOKEN"
PLAIN_REFRESH = "1//FAKE-REFRESH-TOKEN"


class _Creds:
    token = PLAIN_ACCESS
    refresh_token = PLAIN_REFRESH
    token_uri = "https://oauth2.example.invalid/token"
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    expiry = None


class _FakeFlow:
    calls = []

    def __init__(self, scopes, state=None, code_verifier=None):
        self.scopes, self.state, self.code_verifier = scopes, state, code_verifier or "verifier-xyz"
        self.credentials = _Creds()
        self.redirect_uri = None

    @classmethod
    def from_client_config(cls, config, scopes, state=None, code_verifier=None):
        cls.calls.append({"scopes": scopes, "state": state, "code_verifier": code_verifier})
        return cls(scopes, state, code_verifier)

    def authorization_url(self, **kw):
        return "https://accounts.example.invalid/auth?state=STATE-123", "STATE-123"

    def fetch_token(self, authorization_response):
        _FakeFlow.calls.append({"fetch": authorization_response})


@pytest.fixture(autouse=True)
def fake_flow(monkeypatch):
    _FakeFlow.calls = []
    monkeypatch.setattr("app.gsc.gsc.google_auth_oauthlib.flow.Flow", _FakeFlow)
    return _FakeFlow


def _connections(user):
    from app.models import GscConnection

    return GscConnection.query.filter_by(user_id=user.id).all()


def test_authorize_requests_readonly_scope_and_binds_state(client, make_user, fake_flow):
    u = make_user()
    login(client, u)
    r = client.get("/gsc/authorize")
    assert r.status_code == 302
    assert fake_flow.calls[0]["scopes"] == ["https://www.googleapis.com/auth/webmasters.readonly"]
    with client.session_transaction() as s:
        assert s["gsc_oauth_state"] == "STATE-123"
        assert s["gsc_code_verifier"]


def test_callback_without_session_state_rejected(client, make_user):
    u = make_user()
    login(client, u)
    client.get("/gsc/callback?state=STATE-123&code=c")
    assert _connections(u) == []


def test_callback_wrong_state_rejected(client, make_user):
    u = make_user()
    login(client, u)
    client.get("/gsc/authorize")
    client.get("/gsc/callback?state=ATTACKER&code=c")
    assert _connections(u) == []


def test_state_of_user_a_not_usable_in_session_of_b(app, make_user):
    a, b = make_user(), make_user()
    ca, cb = app.test_client(), app.test_client()
    login(ca, a)
    login(cb, b)
    ca.get("/gsc/authorize")
    cb.get("/gsc/callback?state=STATE-123&code=code-of-a")  # B riusa lo state di A
    assert _connections(a) == [] and _connections(b) == []


def test_callback_success_encrypts_tokens_and_no_leak(client, make_user, caplog):
    u = make_user()
    login(client, u)
    client.get("/gsc/authorize")
    r = client.get("/gsc/callback?state=STATE-123&code=c", follow_redirects=True)
    html = r.get_data(as_text=True)
    [conn] = _connections(u)
    assert conn.access_token != PLAIN_ACCESS and PLAIN_ACCESS not in conn.access_token
    assert conn.refresh_token != PLAIN_REFRESH
    from app.gsc.crypto import decrypt

    assert decrypt(conn.refresh_token) == PLAIN_REFRESH
    assert PLAIN_ACCESS not in html and PLAIN_REFRESH not in html
    assert PLAIN_ACCESS not in caplog.text and PLAIN_REFRESH not in caplog.text


def test_callback_replay_rejected(client, make_user, fake_flow):
    u = make_user()
    login(client, u)
    client.get("/gsc/authorize")
    client.get("/gsc/callback?state=STATE-123&code=c")
    fetches_before = sum(1 for c in fake_flow.calls if "fetch" in c)
    client.get("/gsc/callback?state=STATE-123&code=c")
    assert sum(1 for c in fake_flow.calls if "fetch" in c) == fetches_before


def test_callback_anonymous_rejected(client):
    r = client.get("/gsc/callback?state=STATE-123&code=c")
    assert r.status_code == 302 and "/auth/login" in r.headers["Location"]


def test_api_sites_response_has_no_tokens(client, make_user, monkeypatch):
    u = make_user()
    login(client, u)

    class _Svc:
        def sites(self):
            return self

        def list(self):
            return self

        def execute(self):
            return {"siteEntry": [{"siteUrl": "https://mine.example/", "permissionLevel": "siteOwner"}]}

    monkeypatch.setattr("app.gsc.gsc.get_user_gsc_service", lambda uid: (_Svc(), _Creds()))
    monkeypatch.setattr("app.gsc.gsc.save_gsc_credentials", lambda *a: None)
    body = client.get("/gsc/api/sites").get_data(as_text=True)
    assert PLAIN_ACCESS not in body and PLAIN_REFRESH not in body
