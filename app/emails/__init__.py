"""Invio email transazionali tramite Resend.

Un solo punto di ingresso (`send_email`) che legge API key e mittente dalla
config dell'app, così il resto del codice non dipende dai dettagli di Resend.
Se la API key non è configurata, l'invio non solleva: logga un warning e
restituisce False, così il chiamante può decidere il fallback (in sviluppo, ad
esempio, mostrare comunque il codice OTP).
"""
import resend
from flask import current_app


def resend_configured():
    return bool(current_app.config.get("RESEND_API"))


def send_email(to, subject, html, text=None):
    """Invia un'email HTML (con eventuale fallback testuale) a `to`.

    Ritorna True se Resend ha accettato l'invio, False in caso di errore o
    configurazione mancante. Non solleva: l'invio email non deve mai far
    fallire il flusso di autenticazione con un 500.
    """
    api_key = current_app.config.get("RESEND_API")
    if not api_key:
        current_app.logger.warning("RESEND_API non configurata: email a %s non inviata.", to)
        return False

    resend.api_key = api_key
    params = {
        "from": current_app.config["RESEND_FROM"],
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "html": html,
    }
    if text:
        params["text"] = text

    try:
        resend.Emails.send(params)
        return True
    except Exception:  # noqa: BLE001 — qualunque errore di rete/API non deve propagarsi
        current_app.logger.exception("Invio email a %s fallito (Resend).", to)
        return False
