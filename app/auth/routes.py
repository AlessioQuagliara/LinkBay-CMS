from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("There is already an account with this email address.", "error")
        else:
            user = User(name=form.name.data.strip(), email=email)
            user.set_password(form.password.data)
            db.session.add(user)

            db.session.commit()
            login_user(user)
            flash("Account created. Welcome!", "success")
            return redirect(url_for("dashboard.overview"))

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
            login_user(user)
            flash(f"Welcome, {user.name}.", "success")
            return redirect(url_for("dashboard.overview"))
        flash("Incorrect email or password.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You went out.", "success")
    return redirect(url_for("auth.login"))
