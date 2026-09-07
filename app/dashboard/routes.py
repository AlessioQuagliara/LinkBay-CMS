from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.entitlements.service import (
    get_ai_credit_overview,
    get_plan_limits,
    get_usage_summary,
    levels_from_usage,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def overview():
    # Una sola query batch (get_usage_summary) invece di quattro: i livelli
    # di avviso si derivano dagli stessi numeri già calcolati, non da
    # check_site_limit/check_page_limit/check_export_limit (che rifarebbero
    # da capo le stesse query — corretto per un singolo controllo isolato,
    # ridondante quando servono tutte e tre le dimensioni insieme).
    usage = get_usage_summary(current_user)
    usage_levels = levels_from_usage(usage)
    return render_template(
        "dashboard/overview.html",
        connection=current_user.gsc_connection,
        usage=usage,
        usage_levels=usage_levels,
        plan_name=get_plan_limits(current_user).name,
        ai_credits=get_ai_credit_overview(current_user),
    )


@dashboard_bp.route("/sites")
@login_required
def sites():
    limits = get_plan_limits(current_user)
    return render_template(
        "dashboard/sites.html",
        connection=current_user.gsc_connection,
        site_limit=limits.site_limit,
    )


@dashboard_bp.route("/insights")
@login_required
def insights():
    return render_template("dashboard/insights.html", connection=current_user.gsc_connection)


@dashboard_bp.route("/declining")
@login_required
def declining():
    return render_template("dashboard/declining.html", connection=current_user.gsc_connection)


@dashboard_bp.route("/connect")
@login_required
def connect():
    return render_template("dashboard/connect.html", connection=current_user.gsc_connection)
