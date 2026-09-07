"""Audit Presentation: genera (in coda, come /ai/analyze — chiamata DeepSeek
esterna, non sincrona in request) e serve la presentazione reveal.js.
Isolamento: ogni lettura filtra sempre su user_id, un 404 generico (mai 403)
se l'id non esiste o appartiene a un altro utente, per non confermarne
l'esistenza."""
import json

from flask import Blueprint, Response, abort, jsonify, render_template, request
from flask_login import current_user, login_required

from app.audits.charts import render_chart_sections
from app.audits.render import parse_markdown, slides_to_html
from app.entitlements.limits import AI_CREDIT_ACTION_COSTS
from app.entitlements.service import check_ai_credits
from app.gsc.sites import list_monitored_sites
from app.jobs.queue import get_queue, job_status_payload, queue_name_for_user
from app.jobs.tasks import run_audit_presentation_job
from app.models import AuditPresentation

audits_bp = Blueprint("audits", __name__, url_prefix="/dashboard/audits")

AUDIT_PRESENTATION_COST = AI_CREDIT_ACTION_COSTS["audit_presentation"]


def _safe_filename(site_url: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in site_url).strip("-") or "site"


@audits_bp.route("/")
@login_required
def index():
    presentations = (
        AuditPresentation.query.filter_by(user_id=current_user.id)
        .order_by(AuditPresentation.created_at.desc())
        .all()
    )
    sites = list_monitored_sites(current_user.id)
    return render_template(
        "dashboard/audits.html",
        presentations=presentations, sites=sites, cost=AUDIT_PRESENTATION_COST,
    )


@audits_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    site_url = request.form.get("site")
    if not site_url:
        return jsonify({"error": "missing_site"}), 400

    check = check_ai_credits(current_user, cost=AUDIT_PRESENTATION_COST)
    if not check.allowed:
        return jsonify({
            "error": "insufficient_credits", "message": check.message,
            "upsell": check.upsell, "cost": AUDIT_PRESENTATION_COST,
        }), 402

    job = get_queue(queue_name_for_user(current_user)).enqueue(
        run_audit_presentation_job, current_user.id, site_url, job_timeout=180,
    )
    return jsonify({"status": "queued", "job_id": job.id})


@audits_bp.route("/generate-status/<job_id>")
@login_required
def generate_status(job_id):
    payload = job_status_payload(job_id)
    job_result = payload.get("job_result") or {}
    if payload["status"] == "finished" and job_result.get("ok") and job_result.get("presentation_id"):
        presentation = AuditPresentation.query.filter_by(
            id=job_result["presentation_id"], user_id=current_user.id
        ).first()
        if presentation:
            payload["presentation_id"] = presentation.id
    return jsonify(payload)


def _get_owned_presentation(presentation_id: int) -> AuditPresentation:
    presentation = AuditPresentation.query.filter_by(
        id=presentation_id, user_id=current_user.id
    ).first()
    if presentation is None:
        abort(404)
    return presentation


def _render_presentation(presentation: AuditPresentation) -> str:
    slides = parse_markdown(presentation.markdown)

    # I grafici (vedi app/audits/charts.py) si inseriscono subito dopo la
    # slide del titolo, prima delle slide di dettaglio per pagina — mai
    # ricalcolati qui: solo il dict già salvato al momento della generazione
    # (None per le presentazioni create prima di questa colonna, gestito con
    # un fallback pulito da render_chart_sections, non un'eccezione).
    try:
        chart_data = json.loads(presentation.chart_data) if presentation.chart_data else None
    except (TypeError, ValueError):
        chart_data = None

    title_slides, rest_slides = slides[:1], slides[1:]
    slides_html = "\n".join([
        slides_to_html(title_slides),
        render_chart_sections(chart_data),
        slides_to_html(rest_slides),
    ])

    return render_template(
        "audits/present.html", presentation=presentation, slides_html=slides_html,
    )


@audits_bp.route("/<int:presentation_id>")
@login_required
def view(presentation_id):
    presentation = _get_owned_presentation(presentation_id)
    return _render_presentation(presentation)


@audits_bp.route("/<int:presentation_id>/download")
@login_required
def download(presentation_id):
    presentation = _get_owned_presentation(presentation_id)
    html = _render_presentation(presentation)
    filename = f"audit-{_safe_filename(presentation.site_url)}-{presentation.created_at.date().isoformat()}.html"
    return Response(
        html, mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
