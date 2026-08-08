"""Route AI Analyzer (JSON). CSRF: le POST richiedono l'header X-CSRFToken
(Flask-WTF), che il frontend legge dal <meta name="csrf-token">."""
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.ai.deepseek import DeepSeekError
from app.ai.service import (
    _cooldown_remaining,
    analyze_site,
    get_or_create_config,
    get_status,
    set_enabled,
)
from app.gsc.gsc import get_user_gsc_service
from app.gsc.insights import build_insights
from app.gsc.repository import credentials_to_dict, save_gsc_credentials

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.route("/status")
@login_required
def status():
    site = request.args.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400
    return jsonify(get_status(current_user.id, site))


@ai_bp.route("/toggle", methods=["POST"])
@login_required
def toggle():
    site = request.form.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400
    enabled = request.form.get("enabled") == "true"
    set_enabled(current_user.id, site, enabled)
    return jsonify(get_status(current_user.id, site))


@ai_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    site = request.form.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400

    cfg = get_or_create_config(current_user.id, site)
    if not cfg.enabled:
        return jsonify({"error": "disabled"}), 400

    remaining = _cooldown_remaining(cfg)
    if remaining > 0:
        return jsonify({"error": "cooldown", "days_left": remaining}), 429

    service, credentials = get_user_gsc_service(current_user.id)
    if service is None:
        return jsonify({"error": "not_connected"}), 401

    try:
        data = build_insights(service, site, days=28)
        analyze_site(current_user.id, site, data["pages"])
    except DeepSeekError as e:
        current_app.logger.warning("DeepSeek analyze failed: %s", e)
        return jsonify({"error": "ai_failed", "message": str(e)}), 502
    except Exception:
        current_app.logger.exception("AI analyze failed for %s", site)
        return jsonify({"error": "query_failed"}), 502

    save_gsc_credentials(current_user.id, credentials_to_dict(credentials))
    return jsonify(get_status(current_user.id, site))
