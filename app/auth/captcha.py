"""Verifica anti-bot in registrazione via Cloudflare Turnstile.

Se TURNSTILE_SITE_KEY/TURNSTILE_SECRET_KEY non sono configurate (vedi
config.py), il widget non viene mostrato in register.html e la verifica è
saltata — comodo in locale/staging finché non si creano le chiavi su
Cloudflare (dash.cloudflare.com/?to=/:account/turnstile).
"""
import requests
from flask import current_app

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Nome del campo che il widget Turnstile inietta nel form al render lato client.
FIELD_NAME = "cf-turnstile-response"


def configured():
    return bool(
        current_app.config.get("TURNSTILE_SITE_KEY") and current_app.config.get("TURNSTILE_SECRET_KEY")
    )


def verify(token, remote_ip=None):
    """True se il token del widget è valido. Se il captcha non è configurato
    non blocca (vedi `configured`); se invece è configurato ma la richiesta a
    Cloudflare fallisce o va in timeout, fallisce chiuso (rifiuta) per non
    lasciare la registrazione senza protezione."""
    if not configured():
        return True
    if not token:
        return False

    payload = {"secret": current_app.config["TURNSTILE_SECRET_KEY"], "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        resp = requests.post(SITEVERIFY_URL, data=payload, timeout=5)
        resp.raise_for_status()
        return bool(resp.json().get("success"))
    except requests.RequestException:
        current_app.logger.warning("Turnstile siteverify request failed", exc_info=True)
        return False
