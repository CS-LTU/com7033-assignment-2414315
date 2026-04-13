"""
routes/auth.py  –  Authentication Blueprint
Handles: register, login, logout
Security: CSRF (Flask-WTF), password hashing, generic error msg,
          open-redirect prevention, session hardening.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm
from ..models.user import User

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            User.create(form.username.data, form.email.data, form.password.data)
            flash("Account created! Please sign in.", "success")
            logger.info("Registered: %s", form.username.data)
            return redirect(url_for("auth.login"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("auth/register.html", form=form, title="Register")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        # Generic message prevents username enumeration
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session.permanent = True
            logger.info("Login: %s", user.username)
            # Safe redirect — reject absolute URLs to prevent open-redirect
            next_page = request.args.get("next", "")
            if next_page and not next_page.startswith("/"):
                next_page = ""
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("Invalid username or password.", "danger")
            logger.warning("Failed login attempt: %s", form.username.data)

    return render_template("auth/login.html", form=form, title="Sign In")


@auth_bp.route("/logout")
@login_required
def logout():
    logger.info("Logout: %s", current_user.username)
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
