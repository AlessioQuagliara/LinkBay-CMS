"""Emissione e verifica dei token di recupero password via email.

Stesso spirito di app/auth/otp.py, adattato a un flusso a link invece che a
codice digitato:
  - token casuale ad alta entropia (`secrets.token_urlsafe`), inviato come
    link `/auth/reset-password/<token>`;
  - un solo token attivo per utente: emetterne uno nuovo cancella i
    precedenti non consumati;
  - scade dopo PASSWORD_RESET_TTL_SECONDS;
  - un nuovo invio non è richiedibile prima di PASSWORD_RESET_RESEND_COOLDOWN
    secondi, per non permettere di floodare di email un indirizzo altrui.

Il token in chiaro esiste solo il tempo di inviarlo per email: in DB si salva
solo il suo hash (vedi PasswordResetToken).
"""
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app, render_template, url_for

from app.emails import send_email
from app.extensions import db
from app.models import PasswordResetToken
from app.utils import aware

def _now():
    return datetime.now(timezone.utc)


def _can_request(user_id):
    cooldown = current_app.config["PASSWORD_RESET_RESEND_COOLDOWN"]
    latest = (
        PasswordResetToken.query.filter_by(user_id=user_id)
        .order_by(PasswordResetToken.created_at.desc())
        .first()
    )
    if latest is None:
        return True
    return (_now() - aware(latest.created_at)).total_seconds() >= cooldown


def request_reset(user):
    """Emette un nuovo token per l'utente e invia l'email col link di reset.

    Ritorna (sent, token): `sent` indica se l'email è partita, `token` è il
    valore in chiaro (serve solo al fallback dev, mai da esporre in
    produzione). Se siamo ancora in cooldown dall'ultima richiesta per questo
    utente, non emette nulla e ritorna (False, None) — il chiamante mostra
    comunque il messaggio generico, per non far trapelare se l'email esiste
    né lo stato del cooldown."""
    if not _can_request(user.id):
        return False, None

    PasswordResetToken.query.filter_by(user_id=user.id, consumed_at=None).delete()

    token = secrets.token_urlsafe(32)
    ttl = current_app.config["PASSWORD_RESET_TTL_SECONDS"]
    record = PasswordResetToken(
        user_id=user.id,
        token_hash=PasswordResetToken.hash_token(token),
        expires_at=_now() + timedelta(seconds=ttl),
    )
    db.session.add(record)
    db.session.commit()

    sent = _send_reset_email(user, token, ttl)
    return sent, token


def _send_reset_email(user, token, ttl):
    link = url_for("auth.reset_password", token=token, _external=True)
    minutes = max(ttl // 60, 1)
    subject = "Reset your LinkBayCMS password"
    html = render_template(
        "emails/password_reset.html", name=user.name, link=link, minutes=minutes
    )
    text = (
        f"Reset your LinkBayCMS password: {link}\n"
        f"This link expires in {minutes} minutes. If you didn't request it, ignore this email."
    )
    return send_email(user.email, subject, html, text=text)


def find_valid_token(token):
    """Ritorna il PasswordResetToken valido (non scaduto, non consumato) per
    il token in chiaro, o None se non esiste/è scaduto/già usato."""
    if not token:
        return None
    record = PasswordResetToken.query.filter_by(
        token_hash=PasswordResetToken.hash_token(token), consumed_at=None
    ).first()
    if record is None or record.is_expired():
        return None
    return record


def consume(record, new_password):
    """Applica la nuova password e marca il token come usato. Invalida anche
    ogni altro token di reset pendente per lo stesso utente, per sicurezza."""
    user = record.user
    user.set_password(new_password)
    record.consumed_at = _now()
    PasswordResetToken.query.filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.id != record.id,
        PasswordResetToken.consumed_at.is_(None),
    ).delete()
    db.session.commit()
