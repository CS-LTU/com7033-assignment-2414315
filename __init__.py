"""
stroke_app/__init__.py

Application factory for StrokeGuard.
COM7033 – Secure Software Development, Leeds Trinity University.

Security features initialised here:
  - CSRF protection (Flask-WTF)
  - Session management (Flask-Login, strong protection)
  - Secure cookie flags
  - Rotating file error logging
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_override: dict = None) -> Flask:
    """
    Application factory.
    Creates, configures, and returns a Flask app instance.
    Accepts optional config_override dict for testing.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-in-prod"),
        SQLITE_DB_PATH=os.path.join(
            app.instance_path,
            os.environ.get("SQLITE_DB_PATH", "users.db")
        ),
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
        MONGO_DB_NAME=os.environ.get("MONGO_DB_NAME", "stroke_prediction_db"),
        # CSRF
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=3600,
        # Secure session cookies
        SESSION_COOKIE_HTTPONLY=True,       # JS cannot read the cookie
        SESSION_COOKIE_SAMESITE="Lax",      # CSRF mitigation
        SESSION_COOKIE_SECURE=False,        # Set True when HTTPS is used
        PERMANENT_SESSION_LIFETIME=int(
            os.environ.get("PERMANENT_SESSION_LIFETIME", 1800)
        ),
    )

    if config_override:
        app.config.update(config_override)

    # Ensure instance folder exists (holds SQLite DB + logs)
    os.makedirs(app.instance_path, exist_ok=True)

    # ── Extensions ───────────────────────────────────────────────────────────
    csrf.init_app(app)
    _init_login_manager(app)
    _init_logging(app)

    # ── Databases ────────────────────────────────────────────────────────────
    from .models.db_sqlite import init_sqlite_db
    with app.app_context():
        init_sqlite_db(app)

    # ── Blueprints ───────────────────────────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.patients import patients_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(dashboard_bp)

    # ── MongoDB teardown ─────────────────────────────────────────────────────
    from .models.db_mongo import close_mongo_connection
    app.teardown_appcontext(close_mongo_connection)

    # ── Error handlers ───────────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error("500 error: %s", e)
        return render_template("errors/500.html"), 500

    app.logger.info("StrokeGuard started.")
    return app


def _init_login_manager(app: Flask) -> None:
    """Configure Flask-Login."""
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.session_protection = "strong"  # Regenerates session on IP change

    @login_manager.user_loader
    def load_user(user_id: str):
        from .models.user import User
        return User.get_by_id(int(user_id))


def _init_logging(app: Flask) -> None:
    """Set up rotating file log in instance/logs/."""
    logs_dir = os.path.join(app.instance_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    handler = RotatingFileHandler(
        os.path.join(logs_dir, "stroke_app.log"),
        maxBytes=1_048_576,
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s"
    ))
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.WARNING)
