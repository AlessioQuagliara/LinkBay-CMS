"""Impostazioni account: nome, lingua, password. Resta fuori dal gate di
accesso (app/billing/access.py) — sempre raggiungibile, anche a trial scaduto."""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.entitlements.service import get_plan_limits
from app.extensions import db
from app.settings.forms import NotificationsForm, PasswordForm, ProfileForm, WhiteLabelForm

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    profile_form = ProfileForm(name=current_user.name, locale=current_user.locale, prefix="profile")
    notifications_form = NotificationsForm(
        weekly_digest_enabled=current_user.weekly_digest_enabled, prefix="notifications"
    )
    password_form = PasswordForm(prefix="password")
    white_label_form = WhiteLabelForm(
        white_label_enabled=current_user.white_label_enabled, prefix="white_label"
    )
    white_label_available = get_plan_limits(current_user).white_label

    if profile_form.submit.data and profile_form.validate_on_submit():
        current_user.name = profile_form.name.data.strip()
        current_user.locale = profile_form.locale.data
        db.session.commit()
        flash(_("Settings saved."), "success")
        return redirect(url_for("settings.index"))

    if notifications_form.submit.data and notifications_form.validate_on_submit():
        current_user.weekly_digest_enabled = notifications_form.weekly_digest_enabled.data
        db.session.commit()
        flash(_("Settings saved."), "success")
        return redirect(url_for("settings.index"))

    if password_form.submit.data and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash(_("Current password is incorrect."), "error")
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash(_("Password changed."), "success")
            return redirect(url_for("settings.index"))

    if white_label_form.submit.data and white_label_form.validate_on_submit():
        # Ricontrollo lato server anche qui (difesa in profondità): il form
        # nel template è già nascosto per un piano senza white label, ma un
        # POST diretto non deve comunque poter attivare il flag.
        if white_label_available:
            current_user.white_label_enabled = white_label_form.white_label_enabled.data
            db.session.commit()
            flash(_("Settings saved."), "success")
        return redirect(url_for("settings.index"))

    return render_template(
        "settings/index.html",
        profile_form=profile_form,
        notifications_form=notifications_form,
        password_form=password_form,
        white_label_form=white_label_form,
        white_label_available=white_label_available,
    )
