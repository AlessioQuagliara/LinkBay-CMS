from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, redirect, render_template, session, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import otp as otp_service
from app.auth import password_reset as password_reset_service
from app.auth.forms import ForgotPasswordForm, LoginForm, OtpForm, RegisterForm, ResetPasswordForm
from app.entitlements.limits import TRIAL_DAYS
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Chiavi con cui teniamo in sessione lo stato "credenziali ok, manca l'OTP".
# La sessione Flask è un cookie firmato: l'utente non può manometterlo, e qui
# non c'è ancora un login effettivo (login_user avviene solo dopo l'OTP).
_PENDING_USER = "otp_pending_user_id"
_PENDING_PURPOSE = "otp_pending_purpose"
_PENDING_EMAIL = "otp_pending_email"


def _start_otp_flow(user, purpose):
    """Salva lo stato pendente in sessione, emette e invia il codice, poi
    manda l'utente alla pagina di verifica."""
    session[_PENDING_USER] = user.id
    session[_PENDING_PURPOSE] = purpose
    session[_PENDING_EMAIL] = user.email

    sent, code = otp_service.issue_code(user, purpose)
    _flash_code_status(sent, code)
    return redirect(url_for("auth.verify"))


def _flash_code_status(sent, code):
    if sent:
        flash(_("We've emailed you a 6-digit verification code."), "success")
    elif otp_service.dev_fallback_enabled():
        # Solo in sviluppo senza Resend: mostriamo il codice per poter testare.
        flash(_("Dev mode (email not configured): your code is %(code)s.", code=code), "info")
    else:
        flash(_("We couldn't send the email right now. Please try again."), "error")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash(_("There is already an account with this email address."), "error")
        else:
            user = User(name=form.name.data.strip(), email=email)
            user.set_password(form.password.data)
            user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=TRIAL_DAYS)
            user.plan_type = "trial"
            db.session.add(user)
            db.session.commit()
            # Niente login immediato: prima l'utente conferma l'email con l'OTP.
            return _start_otp_flow(user, otp_service.PURPOSE_REGISTER)

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            # Password corretta: secondo fattore via email prima di entrare.
            return _start_otp_flow(user, otp_service.PURPOSE_LOGIN)
        flash(_("Incorrect email or password."), "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        sent, token = (False, None)
        if user:
            sent, token = password_reset_service.request_reset(user)

        # Messaggio sempre identico, esista o meno l'account: non deve
        # trapelare quali email sono registrate.
        flash(
            _("If an account exists for that email, we've sent a password reset link."),
            "success",
        )
        if token and not sent and password_reset_service.dev_fallback_enabled():
            link = url_for("auth.reset_password", token=token, _external=True)
            flash(_("Dev mode (email not configured): %(link)s", link=link), "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    record = password_reset_service.find_valid_token(token)
    if record is None:
        flash(_("This password reset link is invalid or has expired."), "error")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        password_reset_service.consume(record, form.password.data)
        flash(_("Your password has been reset. You can now sign in."), "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form, token=token)


@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    user_id = session.get(_PENDING_USER)
    purpose = session.get(_PENDING_PURPOSE)
    if not user_id or not purpose:
        flash(_("Start by signing in."), "info")
        return redirect(url_for("auth.login"))

    form = OtpForm()
    if form.validate_on_submit():
        ok, error = otp_service.verify_code(user_id, purpose, form.code.data)
        if ok:
            user = db.session.get(User, user_id)
            if user is None:
                _clear_pending()
                flash(_("Something went wrong. Please sign in again."), "error")
                return redirect(url_for("auth.login"))
            if not user.email_verified:
                user.email_verified = True
                db.session.commit()
            login_user(user)
            _clear_pending()
            flash(_("Welcome, %(name)s.", name=user.name), "success")
            return redirect(url_for("dashboard.overview"))
        flash(error, "error")

    _can_resend, cooldown_left = otp_service.can_resend(user_id, purpose)
    return render_template(
        "auth/verify.html",
        form=form,
        email=session.get(_PENDING_EMAIL),
        purpose=purpose,
        cooldown_left=cooldown_left,
    )


@auth_bp.route("/verify/resend", methods=["POST"])
def resend():
    user_id = session.get(_PENDING_USER)
    purpose = session.get(_PENDING_PURPOSE)
    if not user_id or not purpose:
        return redirect(url_for("auth.login"))

    allowed, remaining = otp_service.can_resend(user_id, purpose)
    if not allowed:
        flash(_("Please wait %(seconds)ss before requesting a new code.", seconds=remaining), "error")
        return redirect(url_for("auth.verify"))

    user = db.session.get(User, user_id)
    if user is None:
        _clear_pending()
        return redirect(url_for("auth.login"))

    sent, code = otp_service.issue_code(user, purpose)
    _flash_code_status(sent, code)
    return redirect(url_for("auth.verify"))


@auth_bp.route("/verify/cancel")
def cancel_verify():
    _clear_pending()
    return redirect(url_for("auth.login"))


def _clear_pending():
    session.pop(_PENDING_USER, None)
    session.pop(_PENDING_PURPOSE, None)
    session.pop(_PENDING_EMAIL, None)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("You've been logged out."), "success")
    return redirect(url_for("auth.login"))
