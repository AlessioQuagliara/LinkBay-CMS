"""Emissione e verifica dei codici OTP via email.

Regole (parametri in config.py):
  - codice numerico a 6 cifre, generato con `secrets` (CSPRNG);
  - un solo OTP attivo per (utente, scopo): emetterne uno nuovo cancella i
    precedenti;
  - scade dopo OTP_TTL_SECONDS;
  - al massimo OTP_MAX_ATTEMPTS tentativi di inserimento, poi va rigenerato;
  - nuovo invio non prima di OTP_RESEND_COOLDOWN secondi dall'ultimo.

Il codice in chiaro esiste solo il tempo di inviarlo per email: in DB si salva
solo l'hash (vedi EmailOtp).
"""
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app, render_template
from flask_babel import gettext as _

from app.emails import resend_configured, send_email
from app.extensions import db
from app.models import EmailOtp
from app.utils import aware

PURPOSE_LOGIN = "login"
PURPOSE_REGISTER = "register"


def _now():
    return datetime.now(timezone.utc)


def _generate_code():
    # 6 cifre, zero-padded: da "000000" a "999999".
    return f"{secrets.randbelow(1_000_000):06d}"


def can_resend(user_id, purpose):
    """True se è passato abbastanza tempo dall'ultimo invio per poterne
    richiedere un altro. Se non esiste un OTP attivo, si può inviare."""
    cooldown = current_app.config["OTP_RESEND_COOLDOWN"]
    latest = (
        EmailOtp.query.filter_by(user_id=user_id, purpose=purpose)
        .order_by(EmailOtp.created_at.desc())
        .first()
    )
    if latest is None:
        return True, 0
    elapsed = (_now() - aware(latest.created_at)).total_seconds()
    remaining = int(cooldown - elapsed)
    return remaining <= 0, max(remaining, 0)


def issue_code(user, purpose):
    """Genera un nuovo OTP per l'utente, invalida i precedenti dello stesso
    scopo, lo salva (hashato) e lo invia via email. Ritorna (sent, code) dove
    `sent` indica se l'email è partita e `code` è il codice in chiaro (serve
    solo al fallback in sviluppo, mai da mostrare in produzione)."""
    EmailOtp.query.filter_by(user_id=user.id, purpose=purpose).delete()

    code = _generate_code()
    ttl = current_app.config["OTP_TTL_SECONDS"]
    otp = EmailOtp(
        user_id=user.id,
        purpose=purpose,
        expires_at=_now() + timedelta(seconds=ttl),
    )
    otp.set_code(code)
    db.session.add(otp)
    db.session.commit()

    sent = _send_otp_email(user, code, purpose)
    return sent, code


def _send_otp_email(user, code, purpose):
    minutes = max(current_app.config["OTP_TTL_SECONDS"] // 60, 1)
    subject = f"{code} is your LinkBayCMS verification code"
    html = render_template(
        "emails/otp.html", name=user.name, code=code, minutes=minutes, purpose=purpose
    )
    text = (
        f"Your LinkBayCMS verification code is {code}. "
        f"It expires in {minutes} minutes. If you didn't request it, ignore this email."
    )
    return send_email(user.email, subject, html, text=text)


def verify_code(user_id, purpose, code):
    """Verifica il codice. Ritorna (ok, error). In caso di errore, `error` è un
    messaggio già pronto da mostrare all'utente."""
    otp = (
        EmailOtp.query.filter_by(user_id=user_id, purpose=purpose, consumed_at=None)
        .order_by(EmailOtp.created_at.desc())
        .first()
    )
    if otp is None:
        return False, _("No active code. Request a new one.")
    if otp.is_expired():
        return False, _("This code has expired. Request a new one.")

    max_attempts = current_app.config["OTP_MAX_ATTEMPTS"]
    if otp.attempts >= max_attempts:
        return False, _("Too many attempts. Request a new code.")

    if not otp.check_code((code or "").strip()):
        otp.attempts += 1
        db.session.commit()
        left = max_attempts - otp.attempts
        if left <= 0:
            return False, _("Too many attempts. Request a new code.")
        return False, _("Incorrect code. %(left)s attempt(s) left.", left=left)

    otp.consumed_at = _now()
    db.session.commit()
    return True, None


def dev_fallback_enabled():
    """In sviluppo, se Resend non è configurato, l'email non parte: permettiamo
    di mostrare il codice a schermo così il flusso è comunque testabile in
    locale. Mai attivo se Resend è configurato o fuori da debug."""
    return current_app.debug and not resend_configured()
