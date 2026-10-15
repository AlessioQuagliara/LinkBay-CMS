"""Export declining pages in CSV/PDF — gate sul limite export/mese del piano
(app/entitlements) e log su ResourceUsageLog per l'audit."""
from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_login import current_user, login_required

from app.entitlements.limits import PlanLimits
from app.entitlements.service import check_export_limit, get_plan_limits, record_usage
from app.exports.csv_export import build_declining_pages_csv
from app.exports.pdf_export import build_declining_pages_pdf
from app.utils import safe_filename

exports_bp = Blueprint("exports", __name__, url_prefix="/exports")


@exports_bp.route("/declining.csv")
@login_required
def declining_csv():
    site_url = request.args.get("site")
    if not site_url:
        return jsonify({"error": "missing_site"}), 400

    check = check_export_limit(current_user)
    if not check.allowed:
        return jsonify({"error": "export_limit_reached", "message": check.message, "upsell": check.upsell}), 403

    record_usage(current_user, "export_csv", site_url=site_url)
    filename = f"declining-pages-{safe_filename(site_url)}.csv"
    return Response(
        stream_with_context(build_declining_pages_csv(current_user.id, site_url)),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@exports_bp.route("/declining.pdf")
@login_required
def declining_pdf():
    site_url = request.args.get("site")
    if not site_url:
        return jsonify({"error": "missing_site"}), 400

    check = check_export_limit(current_user)
    if not check.allowed:
        return jsonify({"error": "export_limit_reached", "message": check.message, "upsell": check.upsell}), 403

    limits: PlanLimits = get_plan_limits(current_user)
    # White label onorato solo se il piano lo consente — controllo
    # server-side, il toggle da solo in Settings non basta (vedi
    # app/settings/routes.py).
    white_label = bool(limits.white_label and current_user.white_label_enabled)

    try:
        pdf_bytes = build_declining_pages_pdf(current_user, site_url, white_label)
    except Exception:
        from flask import current_app

        current_app.logger.exception("Export PDF fallito per %s (user %s)", site_url, current_user.id)
        return jsonify({"error": "export_failed"}), 502

    record_usage(current_user, "export_pdf", site_url=site_url)
    filename = f"declining-pages-{safe_filename(site_url)}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
