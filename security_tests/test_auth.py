"""A. Autenticazione e sessioni (login + OTP email, reset password, logout)."""
from datetime import datetime, timedelta, timezone

import pytest

from security_tests.conftest import csrf_token, login

PASSWORD = "Passw0rd!secure"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    # Codice deterministico così un "codice sbagliato" è sbagliato con certezza.
    monkeypatch.setattr("app.auth.otp._generate_code", lambda: "123456")


def _login(client, email, password=PASSWORD):
    tok = csrf_token(client, "/auth/login")
    return client.post("/auth/login", data={"csrf_token": tok, "email": email, "password": password})


def _verify(client, code):
    tok = csrf_token(client, "/auth/verify")
    return client.post("/auth/verify", data={"csrf_token": tok, "code": code})


def _otp_attempts(db_session, user):
    from app.models import EmailOtp

    db_session.expire_all()
    return EmailOtp.query.filter_by(user_id=user.id, purpose="login").one().attempts


def test_otp_not_reissued_on_login_during_cooldown(client, make_user, db_session, sent_emails):
    u = make_user(password=PASSWORD)
    assert _login(client, u.email).status_code == 302
    for _ in range(5):
        _verify(client, "000001")
    assert _otp_attempts(db_session, u) == 5
    # Rifare il login non deve emettere un codice nuovo (contatore azzerato).
    assert _login(client, u.email).status_code == 302
    assert _otp_attempts(db_session, u) == 5
    assert "Too many attempts" in _verify(client, "123456").get_data(as_text=True)
    assert len(sent_emails) == 1


def test_otp_reissued_on_login_after_cooldown(client, make_user, db_session, sent_emails):
    from app.models import EmailOtp

    u = make_user(password=PASSWORD)
    _login(client, u.email)
    otp = EmailOtp.query.filter_by(user_id=u.id).one()
    otp.created_at = datetime.now(timezone.utc) - timedelta(seconds=120)
    db_session.commit()
    _login(client, u.email)
    assert len(sent_emails) == 2
    r = _verify(client, "123456")
    assert r.status_code == 302 and "/dashboard" in r.headers["Location"]


def test_login_is_rate_limited(client, make_user):
    u = make_user(password=PASSWORD)
    codes = [_login(client, u.email, "wrong-password").status_code for _ in range(15)]
    assert 429 in codes


def test_otp_verify_is_rate_limited(client, make_user):
    u = make_user(password=PASSWORD)
    _login(client, u.email)
    codes = [_verify(client, "000001").status_code for _ in range(15)]
    assert 429 in codes


def test_register_is_rate_limited_control(client):
    # Il limite 5/min vale per GET+POST su /auth/register.
    codes = [client.get("/auth/register").status_code for _ in range(7)]
    assert 429 in codes


def test_otp_resend_respects_cooldown_control(client, make_user, sent_emails):
    u = make_user(password=PASSWORD)
    _login(client, u.email)
    tok = csrf_token(client, "/auth/verify")
    client.post("/auth/verify/resend", data={"csrf_token": tok})
    assert len(sent_emails) == 1  # il resend esplicito è bloccato dal cooldown


def test_otp_expired_code_rejected(client, make_user, db_session):
    from app.models import EmailOtp

    u = make_user(password=PASSWORD)
    _login(client, u.email)
    otp = EmailOtp.query.filter_by(user_id=u.id).one()
    otp.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    r = _verify(client, "123456")
    assert r.status_code == 200 and "expired" in r.get_data(as_text=True)


def test_otp_code_not_reusable(client, make_user):
    u = make_user(password=PASSWORD)
    _login(client, u.email)
    assert _verify(client, "123456").status_code == 302
    client.get("/auth/logout")
    # Riprova lo stesso codice con una sessione "pending" forgiata.
    with client.session_transaction() as s:
        s["otp_pending_user_id"] = u.id
        s["otp_pending_purpose"] = "login"
    r = _verify(client, "123456")
    assert r.status_code == 200 and "No active code" in r.get_data(as_text=True)


def test_login_error_message_does_not_enumerate(client, make_user):
    u = make_user(password=PASSWORD)
    a = _login(client, u.email, "wrong").get_data(as_text=True)
    b = _login(client, "nobody@example.com", "wrong").get_data(as_text=True)
    assert "Incorrect email or password" in a and "Incorrect email or password" in b


def test_FINDING_register_enumerates_existing_email(client, make_user):
    u = make_user()
    tok = csrf_token(client, "/auth/register")
    r = client.post("/auth/register", data={
        "csrf_token": tok, "name": "x", "email": u.email,
        "password": PASSWORD, "confirm_password": PASSWORD,
    })
    assert "already an account" in r.get_data(as_text=True)


def test_forgot_password_does_not_enumerate(client, make_user):
    u = make_user()
    msgs = []
    for email in (u.email, "nobody@example.com"):
        tok = csrf_token(client, "/auth/forgot-password")
        r = client.post("/auth/forgot-password", data={"csrf_token": tok, "email": email},
                        follow_redirects=True)
        msgs.append("If an account exists" in r.get_data(as_text=True))
    assert msgs == [True, True]


# --- Reset password ----------------------------------------------------------

def _issue_reset(app, user):
    from app.auth.password_reset import request_reset

    with app.test_request_context():
        sent, token = request_reset(user)
    assert sent and token
    return token


def _do_reset(client, token, new="N3w-Passw0rd!x"):
    tok = csrf_token(client, f"/auth/reset-password/{token}")
    return client.post(f"/auth/reset-password/{token}",
                       data={"csrf_token": tok, "password": new, "confirm_password": new})


def test_reset_token_single_use(app, client, make_user):
    u = make_user()
    token = _issue_reset(app, u)
    assert _do_reset(client, token).status_code == 302
    r = client.get(f"/auth/reset-password/{token}")
    assert r.status_code == 302 and "forgot-password" in r.headers["Location"]


def test_reset_token_expires(app, client, make_user, db_session):
    from app.models import PasswordResetToken

    u = make_user()
    token = _issue_reset(app, u)
    rec = PasswordResetToken.query.filter_by(user_id=u.id).one()
    rec.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    assert client.get(f"/auth/reset-password/{token}").status_code == 302


def test_reset_token_stored_hashed(app, make_user):
    from app.models import PasswordResetToken

    u = make_user()
    token = _issue_reset(app, u)
    assert PasswordResetToken.query.filter_by(user_id=u.id).one().token_hash != token


def test_FINDING_password_reset_does_not_invalidate_existing_sessions(app, make_user):
    u = make_user()
    attacker = app.test_client()
    login(attacker, u)  # sessione già rubata/aperta
    assert attacker.get("/settings/").status_code == 200
    token = _issue_reset(app, u)
    victim = app.test_client()
    r = victim.get(f"/auth/reset-password/{token}")
    assert r.status_code == 200, (r.status_code, r.headers.get("Location"))
    assert _do_reset(victim, token).status_code == 302
    assert attacker.get("/settings/").status_code == 200  # ancora dentro


def test_FINDING_logout_via_get(client, make_user):
    u = make_user()
    login(client, u)
    client.get("/auth/logout")
    assert client.get("/settings/").status_code == 302  # sloggato con una semplice GET (CSRF logout)
