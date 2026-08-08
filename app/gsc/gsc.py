"""Collegamento OAuth2 a Google Search Console, per utente.

Adattato dalla bozza originale: qui l'account collegato è lo `User` loggato
(Flask-Login), non un "tenant" — questo progetto ha un solo modello,
`User` (vedi README). Le credenziali sono salvate cifrate in DB via
app/gsc/repository.py, non in sessione e non su file.
"""
import os
from datetime import date, timedelta

from flask import Blueprint, current_app, flash, jsonify, redirect, request, session, url_for
from flask_login import current_user, login_required
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from app.gsc.history import get_site_series, sync_site_daily
from app.gsc.insights import build_insights
from app.gsc.repository import (
    credentials_to_dict,
    delete_gsc_credentials,
    load_gsc_credentials,
    save_gsc_credentials,
)

gsc_bp = Blueprint("gsc", __name__, url_prefix="/gsc")

API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"

# Google richiede HTTPS per i redirect URI, tranne quando questa variabile è
# impostata — necessaria in locale, dove si gira su http://localhost.
if os.environ.get("APP_BASE_URL", "http://localhost:3000").startswith("http://"):
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")


def _redirect_uri():
    # GOOGLE_REDIRECT_URI ha priorità se impostata (utile dietro proxy, dove
    # url_for(_external=True) può dedurre schema/host sbagliati). Deve
    # risultare identico tra /authorize e /callback: usa sempre questo helper
    # in entrambe le route, mai url_for(...) diretto.
    return current_app.config.get("GOOGLE_REDIRECT_URI") or url_for("gsc.callback", _external=True)


def _client_config():
    return {
        "web": {
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [_redirect_uri()],
        }
    }


def _credentials_from_dict(creds: dict) -> google.oauth2.credentials.Credentials:
    credentials = google.oauth2.credentials.Credentials(
        token=creds["token"],
        refresh_token=creds.get("refresh_token"),
        token_uri=creds["token_uri"],
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        scopes=creds["scopes"],
    )
    if creds.get("expiry"):
        credentials.expiry = creds["expiry"]
    return credentials


def _build_service(credentials):
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def get_user_gsc_service(user_id):
    """(service, credentials) per l'utente, o (None, None) se non collegato.
    Riutilizzabile fuori dalle route (es. AI Analyzer). Dopo l'uso il chiamante
    deve ripersistere le credenziali con save_gsc_credentials, perché la
    libreria può averle aggiornate con un refresh trasparente."""
    creds = load_gsc_credentials(user_id)
    if not creds:
        return None, None
    credentials = _credentials_from_dict(creds)
    return _build_service(credentials), credentials


@gsc_bp.route("/authorize")
@login_required
def authorize():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("Google Search Console is not configured on this server yet (missing GOOGLE_CLIENT_ID/SECRET).", "error")
        return redirect(url_for("dashboard.connect"))

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        _client_config(), scopes=current_app.config["GSC_SCOPES"]
    )
    flow.redirect_uri = _redirect_uri()

    authorization_url, state = flow.authorization_url(
        access_type="offline",  # richiesto per ottenere un refresh_token
        include_granted_scopes="true",
        prompt="consent",  # forza il re-consenso, altrimenti Google a volte non rimanda il refresh_token
    )

    # PKCE: authorization_url() ha appena generato flow.code_verifier e lo ha
    # usato per calcolare il code_challenge mandato a Google. Va salvato ora,
    # altrimenti /callback (che ricrea un Flow nuovo) non potrà rimandarlo a
    # Google in fase di token exchange -> invalid_grant: Missing code verifier.
    session["gsc_oauth_state"] = state
    session["gsc_code_verifier"] = flow.code_verifier
    return redirect(authorization_url)


@gsc_bp.route("/callback")
@login_required
def callback():
    state = session.pop("gsc_oauth_state", None)
    code_verifier = session.pop("gsc_code_verifier", None)

    if state is None or state != request.args.get("state"):
        flash("Could not verify the connection request. Please try connecting again.", "error")
        return redirect(url_for("dashboard.connect"))

    if code_verifier is None:
        flash("The connection request expired. Please try connecting again.", "error")
        return redirect(url_for("dashboard.connect"))

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            _client_config(),
            scopes=current_app.config["GSC_SCOPES"],
            state=state,
            code_verifier=code_verifier,  # riassocia il verifier al nuovo Flow, così fetch_token() lo invia a Google
        )
        flow.redirect_uri = _redirect_uri()
        flow.fetch_token(authorization_response=request.url)
    except Exception:
        current_app.logger.exception("GSC OAuth callback failed")
        flash("Google didn't confirm the connection. Please try again.", "error")
        return redirect(url_for("dashboard.connect"))

    save_gsc_credentials(current_user.id, credentials_to_dict(flow.credentials))

    flash("Google Search Console connected.", "success")
    return redirect(url_for("dashboard.connect"))


@gsc_bp.route("/disconnect", methods=["POST"])
@login_required
def disconnect():
    delete_gsc_credentials(current_user.id)
    flash("Google Search Console disconnected.", "success")
    return redirect(url_for("dashboard.connect"))


@gsc_bp.route("/sites")
@login_required
def sites():
    creds = load_gsc_credentials(current_user.id)
    if not creds:
        return redirect(url_for("gsc.authorize"))

    credentials = _credentials_from_dict(creds)
    service = _build_service(credentials)

    site_list = service.sites().list().execute()
    verified_sites = [
        s for s in site_list.get("siteEntry", [])
        if s["permissionLevel"] != "siteUnverifiedUser"
    ]

    # Il token potrebbe essere stato aggiornato automaticamente dalla libreria
    # (refresh trasparente): salva la versione aggiornata.
    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))

    return jsonify(verified_sites)


@gsc_bp.route("/api/sites")
@login_required
def api_sites():
    """Elenco JSON dei siti verificati, per popolare il selettore in dashboard."""
    creds = load_gsc_credentials(current_user.id)
    if not creds:
        return jsonify({"error": "not_connected"}), 401

    credentials = _credentials_from_dict(creds)
    service = _build_service(credentials)

    site_list = service.sites().list().execute()
    sites = [
        {"siteUrl": s["siteUrl"], "permissionLevel": s["permissionLevel"]}
        for s in site_list.get("siteEntry", [])
        if s["permissionLevel"] != "siteUnverifiedUser"
    ]

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    return jsonify({"sites": sites})


ALLOWED_PERIODS = {7, 28, 90}


@gsc_bp.route("/api/insights")
@login_required
def api_insights():
    """Dati aggregati (totali sito + delta, pagine con rating, query, serie
    storica) per la vista Insights. Querystring: ?site=<siteUrl>&days=7|28|90."""
    site_url = request.args.get("site")
    if not site_url:
        return jsonify({"error": "missing_site"}), 400

    try:
        days = int(request.args.get("days", 28))
    except (TypeError, ValueError):
        days = 28
    if days not in ALLOWED_PERIODS:
        days = 28

    creds = load_gsc_credentials(current_user.id)
    if not creds:
        return jsonify({"error": "not_connected"}), 401

    credentials = _credentials_from_dict(creds)
    service = _build_service(credentials)

    try:
        # Prima allinea lo storico su DB (backfill/refresh), poi calcola i
        # numeri del periodo live e rileggi la serie dal DB per il grafico.
        sync_site_daily(service, current_user.id, site_url, days)
        data = build_insights(service, site_url, days=days)
        data["series"] = get_site_series(current_user.id, site_url, days)
    except Exception:
        current_app.logger.exception("GSC insights failed for %s", site_url)
        return jsonify({"error": "query_failed"}), 502

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    return jsonify(data)


@gsc_bp.route("/analytics/<path:site_url>")
@login_required
def analytics(site_url):
    """Click, impressioni, CTR e posizione media per sito, ultimi 3 mesi."""
    creds = load_gsc_credentials(current_user.id)
    if not creds:
        return redirect(url_for("gsc.authorize"))

    credentials = _credentials_from_dict(creds)
    service = _build_service(credentials)

    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": ["query", "page"],
        "rowLimit": 100,
    }

    response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))

    return jsonify(response.get("rows", []))
