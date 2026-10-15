"""Collegamento OAuth2 a Google Search Console, per utente.

Adattato dalla bozza originale: qui l'account collegato è lo `User` loggato
(Flask-Login), non un "tenant" — questo progetto ha un solo modello,
`User` (vedi README). Le credenziali sono salvate cifrate in DB via
app/gsc/repository.py, non in sessione e non su file.
"""
import os
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, flash, jsonify, redirect, request, session, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from app.entitlements.service import check_site_limit, get_plan_limits, record_usage
from app.gsc.history import get_site_series, sync_site_daily
from app.gsc.insights import build_insights
from app.gsc.page_history import sync_page_monthly
from app.gsc.repository import (
    credentials_to_dict,
    delete_gsc_credentials,
    load_gsc_credentials,
    save_gsc_credentials,
)
from app.gsc.sites import (
    add_monitored_site,
    deactivate_monitored_site,
    get_monitored_site_row,
    list_monitored_sites,
    touch_last_synced,
)
from app.jobs.concurrency import acquire_scan_slot
from app.jobs.queue import get_queue, queue_name_for_user
from app.jobs.tasks import run_gsc_scan_job
from app.utils import aware


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
        flash(_("Google Search Console is not configured on this server yet (missing GOOGLE_CLIENT_ID/SECRET)."), "error")
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
        flash(_("Could not verify the connection request. Please try connecting again."), "error")
        return redirect(url_for("dashboard.connect"))

    if code_verifier is None:
        flash(_("The connection request expired. Please try connecting again."), "error")
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
        flash(_("Google didn't confirm the connection. Please try again."), "error")
        return redirect(url_for("dashboard.connect"))

    save_gsc_credentials(current_user.id, credentials_to_dict(flow.credentials))

    flash(_("Google Search Console connected."), "success")
    return redirect(url_for("dashboard.connect"))


@gsc_bp.route("/disconnect", methods=["POST"])
@login_required
def disconnect():
    delete_gsc_credentials(current_user.id)
    flash(_("Google Search Console disconnected."), "success")
    return redirect(url_for("dashboard.connect"))


@gsc_bp.route("/api/sites")
@login_required
def api_sites():
    """Elenco JSON dei siti verificati, per popolare il selettore in dashboard."""
    service, credentials = get_user_gsc_service(current_user.id)
    if service is None:
        return jsonify({"error": "not_connected"}), 401

    site_list = service.sites().list().execute()
    sites = [
        {"siteUrl": s["siteUrl"], "permissionLevel": s["permissionLevel"]}
        for s in site_list.get("siteEntry", [])
        if s["permissionLevel"] != "siteUnverifiedUser"
    ]

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    monitored = list_monitored_sites(current_user.id)
    return jsonify({
        "sites": sites,
        "monitored_site_urls": [row.site_url for row in monitored],
    })


@gsc_bp.route("/api/monitored-sites")
@login_required
def api_monitored_sites():
    """Elenco dei soli siti scelti dall'utente per il monitoraggio (a
    differenza di /api/sites, che elenca tutte le proprietà verificate su
    Google)."""
    rows = list_monitored_sites(current_user.id)
    return jsonify({"sites": [row.site_url for row in rows]})


@gsc_bp.route("/api/monitored-site", methods=["POST"])
@login_required
def api_monitored_site():
    """Aggiunge un sito al monitoraggio dell'utente e avvia subito il
    backfill dello storico (giornaliero + mensile per pagina), invece di
    aspettare la prima visita a Insights o il cron settimanale. È il momento
    giusto per farlo: prima di aggiungere il sito non sappiamo ancora quale
    storico backfillare.

    Il limite di siti del piano (app/entitlements) è bloccante: un sito già
    attivo per l'utente non conta come "nuovo" (idempotente), quindi
    ri-aggiungere lo stesso sito non fa scattare il limite per errore."""
    site = request.form.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400

    already_active = any(row.site_url == site for row in list_monitored_sites(current_user.id))
    if not already_active:
        check = check_site_limit(current_user)
        if not check.allowed:
            return jsonify({"error": "site_limit_reached", "message": check.message, "upsell": check.upsell}), 403

    add_monitored_site(current_user.id, site)
    if not already_active:
        record_usage(current_user, "site_added", site_url=site)

    try:
        service, credentials = get_user_gsc_service(current_user.id)
        if service is not None:
            sync_site_daily(service, current_user.id, site, days=28)
            sync_page_monthly(service, current_user.id, site)
            save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
            touch_last_synced(current_user.id, site)
    except Exception:
        # Non bloccare l'aggiunta del sito se il backfill fallisce: il cron
        # notturno/settimanale (flask sync-full-history / run-decay-rules)
        # recupera comunque lo storico più avanti.
        current_app.logger.exception("Backfill iniziale fallito per %s (user %s)", site, current_user.id)

    return jsonify({"monitored_site_url": site})


@gsc_bp.route("/api/monitored-site/remove", methods=["POST"])
@login_required
def api_monitored_site_remove():
    """Disattiva un sito dal monitoraggio (non cancella lo storico raccolto:
    vedi app/models/monitored_site.py)."""
    site = request.form.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400
    removed = deactivate_monitored_site(current_user.id, site)
    if not removed:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"removed": site})


ALLOWED_PERIODS = {7, 28, 90}


def _maybe_queue_background_scan(user, site_url) -> bool:
    """Se il sito non è mai stato sincronizzato o l'ultimo sync è più
    vecchio del refresh_interval del piano, mette in coda un aggiornamento
    di GscSiteDaily/GscPageMonthly/PageAlert in background invece di farlo
    dentro la request (comportamento precedente). Ritorna True se i dati di
    storico mostrati potrebbero essere indietro rispetto a Search Console —
    la UI può usare questo flag per mostrare "aggiornamento in corso"
    (cablaggio lato frontend rimandato a una fase successiva).

    Nota: NON elimina le chiamate GSC live che build_insights() fa comunque
    per il periodo corrente (overview/pagine/query) — quelle leggono
    direttamente dall'API per il range richiesto (7/28/90gg) e non hanno
    un equivalente pre-aggregato in DB oggi (solo storico giornaliero di
    sito e mensile per pagina, non giornaliero per pagina). Qui si accoda
    solo il refresh dello storico persistito, che prima girava sincrono e
    ripetuto ad ogni apertura della pagina indipendentemente dal piano."""
    row = get_monitored_site_row(user.id, site_url)
    limits = get_plan_limits(user)
    last_synced = aware(row.last_synced_at) if row else None
    stale = last_synced is None or (
        datetime.now(timezone.utc) - last_synced >= timedelta(days=limits.refresh_days)
    )
    if not stale:
        return False

    # Silenzioso se non c'è uno slot di concorrenza libero: è un refresh
    # passivo (non un click esplicito dell'utente), non deve mostrare un
    # errore — semplicemente non accoda un altro job finché quello in corso
    # non libera lo slot.
    if acquire_scan_slot(user.id, limits.concurrent_scans):
        try:
            get_queue(queue_name_for_user(user)).enqueue(
                run_gsc_scan_job, user.id, site_url, job_timeout=300
            )
        except Exception:
            current_app.logger.exception(
                "Impossibile accodare lo scan in background per %s (user %s)", site_url, user.id
            )
            from app.jobs.concurrency import release_scan_slot

            release_scan_slot(user.id)
    return True


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

    service, credentials = get_user_gsc_service(current_user.id)
    if service is None:
        return jsonify({"error": "not_connected"}), 401

    try:
        data = build_insights(service, site_url, days=days)
        data["series"] = get_site_series(current_user.id, site_url, days)
    except Exception:
        current_app.logger.exception("GSC insights failed for %s", site_url)
        return jsonify({"error": "query_failed"}), 502

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    # Lo storico persistito (grafico, declining pages) si aggiorna in
    # background quando è più vecchio del refresh_interval del piano, non
    # più in sincrono ad ogni apertura di questa pagina (vedi Fase 2 del
    # piano multi-tier).
    data["stale"] = _maybe_queue_background_scan(current_user, site_url)
    return jsonify(data)
