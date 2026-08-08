from flask import Blueprint, render_template
from flask_login import current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def overview():
    return render_template("dashboard/overview.html")


@dashboard_bp.route("/insights")
@login_required
def insights():
    return render_template("dashboard/insights.html", connection=current_user.gsc_connection)


@dashboard_bp.route("/connect")
@login_required
def connect():
    return render_template("dashboard/connect.html", connection=current_user.gsc_connection)
