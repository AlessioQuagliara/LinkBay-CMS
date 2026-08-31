"""Route AI Analyzer (JSON). CSRF: le POST richiedono l'header X-CSRFToken
(Flask-WTF), che il frontend legge dal <meta name="csrf-token">."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.ai.service import (
    AI_CREDIT_COST_PER_RUN,
    _cooldown_remaining,
    get_or_create_config,
    get_status,
    set_enabled,
)
from app.entitlements.service import check_ai_credits, get_plan_limits
from app.jobs.queue import get_queue, job_status_payload, queue_name_for_user
from app.jobs.tasks import run_ai_analysis_job

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
    """Accoda l'analisi invece di chiamare DeepSeek dentro la request (prima
    girava sincrona qui — vedi app/jobs/tasks.py::run_ai_analysis_job per la
    stessa logica spostata in background). Il frontend fa polling su
    GET /ai/analyze-status/<job_id> finché il job non è "finished"/"failed"."""
    site = request.form.get("site")
    if not site:
        return jsonify({"error": "missing_site"}), 400

    cfg = get_or_create_config(current_user.id, site)
    if not cfg.enabled:
        return jsonify({"error": "disabled"}), 400

    limits = get_plan_limits(current_user)
    if limits.ai_mode == "credit":
        # Piani Pro (e AppSumo Tier 3 per la quota mensile): freno a crediti,
        # non a tempo — vedi app/entitlements/ai_credits.py.
        check = check_ai_credits(current_user, cost=AI_CREDIT_COST_PER_RUN)
        if not check.allowed:
            return jsonify({"error": "insufficient_credits", "message": check.message, "upsell": check.upsell}), 402
    else:
        remaining = _cooldown_remaining(cfg, limits)
        if remaining > 0:
            return jsonify({"error": "cooldown", "days_left": remaining}), 429

    job = get_queue(queue_name_for_user(current_user)).enqueue(
        run_ai_analysis_job, current_user.id, site, job_timeout=180
    )
    return jsonify({"status": "queued", "job_id": job.id})


@ai_bp.route("/analyze-status/<job_id>")
@login_required
def analyze_status(job_id):
    """Polling per il job accodato da /ai/analyze. `job_result` è l'esito di
    business del job (vedi run_ai_analysis_job: {"ok": True} oppure
    {"ok": False, "error": ...}). Quando il job è concluso con successo,
    allega anche get_status() aggiornato così il frontend può ridisegnare
    punteggi/cooldown con una sola chiamata."""
    site = request.args.get("site")
    payload = job_status_payload(job_id)
    job_result = payload.get("job_result") or {}
    if payload["status"] == "finished" and job_result.get("ok") and site:
        payload["ai_status"] = get_status(current_user.id, site)
    return jsonify(payload)
