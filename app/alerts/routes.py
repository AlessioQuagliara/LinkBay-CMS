"""API JSON per la lista delle pagine in discesa (page_alerts).

Un blueprint per una responsabilità (README): qui vivono solo le API che
alimentano /dashboard/declining. Ogni query è sempre filtrata per
current_user.id — un utente non può vedere né toccare gli alert di un altro.
"""
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.gsc.gsc import get_user_gsc_service
from app.gsc.insights import page_query_losses
from app.gsc.page_history import get_page_series
from app.gsc.repository import credentials_to_dict, save_gsc_credentials
from app.models import PageAlert

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")

VALID_STATUSES = {"new", "acknowledged", "done", "recovered"}


def _alert_to_dict(a: PageAlert) -> dict:
    return {
        "id": a.id,
        "site_url": a.site_url,
        "url": a.url,
        "window_end": a.window_end.isoformat() if a.window_end else None,
        "best_month_clicks": a.best_month_clicks,
        "click_loss_abs": a.click_loss_abs,
        "click_loss_pct": a.click_loss_pct,
        "position_before": a.position_before,
        "position_after": a.position_after,
        "impressions_trend_pct": a.impressions_trend_pct,
        "site_relative_drop_pct": a.site_relative_drop_pct,
        "yoy_confirmed": a.yoy_confirmed,
        "priority_score": a.priority_score,
        "reason_text": a.reason_text,
        "status": a.status,
    }


@alerts_bp.route("/api/list")
@login_required
def api_list():
    """Alert del sito, per stato, ordinati per priorità decrescente."""
    site = request.args.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400

    status = request.args.get("status", "new")
    query = PageAlert.query.filter_by(user_id=current_user.id, site_url=site)
    if status != "all":
        query = query.filter_by(status=status)

    alerts = query.order_by(PageAlert.priority_score.desc()).all()
    return jsonify({"alerts": [_alert_to_dict(a) for a in alerts]})


@alerts_bp.route("/api/trend")
@login_required
def api_trend():
    """Serie mensile (6 mesi) di una pagina, per la sparkline nella riga espansa."""
    site = request.args.get("site")
    page = request.args.get("page")
    if not site:
        return jsonify({"error": "missing_site"}), 400
    if not page:
        return jsonify({"error": "missing_page"}), 400

    series = get_page_series(current_user.id, site, page, months=6)
    return jsonify({"series": [dict(r, month=r["month"].isoformat()) for r in series]})


@alerts_bp.route("/api/query-losses")
@login_required
def api_query_losses():
    """Query che hanno perso più click per una singola pagina già segnalata.

    Riservata alle pagine presenti in page_alerts: non è un esploratore di
    query per URL arbitrarie. Il controllo sull'alert precede volutamente la
    chiamata a Google, così una pagina non segnalata ritorna 404 senza
    consumare quota API."""
    site = request.args.get("site")
    page = request.args.get("page")
    if not site:
        return jsonify({"error": "missing_site"}), 400
    if not page:
        return jsonify({"error": "missing_page"}), 400

    try:
        days = int(request.args.get("days", 90))
    except (TypeError, ValueError):
        days = 90

    # Prima barriera: deve esistere un alert dell'utente per questa pagina.
    # Nessuna query a Google finché non è verificato (mantiene i costi bassi).
    alert = PageAlert.query.filter_by(
        user_id=current_user.id, site_url=site, url=page
    ).first()
    if alert is None:
        return jsonify({"error": "not_an_alert"}), 404

    service, credentials = get_user_gsc_service(current_user.id)
    if service is None:
        return jsonify({"error": "not_connected"}), 401

    try:
        queries = page_query_losses(service, site, page, days=days)
    except Exception:
        current_app.logger.exception("query-losses failed for %s / %s", site, page)
        return jsonify({"error": "query_failed"}), 502

    # Refresh trasparente del token: ri-salviamo le credenziali dopo la chiamata.
    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    return jsonify({"queries": queries})


@alerts_bp.route("/api/status", methods=["POST"])
@login_required
def api_status():
    """Aggiorna lo stato di un alert. Solo se appartiene all'utente loggato."""
    status = request.form.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error": "invalid_status"}), 400

    raw_id = request.form.get("id")
    if not raw_id:
        return jsonify({"error": "missing_id"}), 400
    try:
        alert_id = int(raw_id)
    except (TypeError, ValueError):
        return jsonify({"error": "not_found"}), 404

    # La verifica user_id nella query è la barriera: un id di un altro utente
    # semplicemente non viene trovato -> 404, non 403 (non riveliamo l'esistenza).
    alert = PageAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if alert is None:
        return jsonify({"error": "not_found"}), 404

    if status == "done" and alert.status != "done":
        # Riparte il conto alla rovescia del recovery-check a 30/60gg (vedi
        # app/rules/recovery.py) — un "done" ripetuto non eredita i checkpoint
        # di un giro precedente.
        alert.done_at = datetime.now(timezone.utc)
        alert.checked_30d_at = None
        alert.checked_60d_at = None

    alert.status = status
    db.session.commit()
    return jsonify({"alert": _alert_to_dict(alert)})
