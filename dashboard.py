"""
routes/dashboard.py  –  Dashboard Blueprint
Shows aggregated statistics pulled from MongoDB.
"""

import logging
from flask import Blueprint, render_template, flash
from flask_login import login_required
from ..models.patient import Patient

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    try:
        stats = Patient.get_statistics()
    except Exception as exc:
        logger.error("Dashboard stats error: %s", exc)
        flash("Could not load statistics. Is MongoDB running?", "warning")
        stats = {
            "total": 0, "stroke_count": 0, "stroke_pct": 0,
            "hypertension_count": 0, "heart_disease_count": 0,
            "avg_age": 0, "avg_bmi": 0, "avg_glucose": 0,
            "gender_counts": {}, "smoking_counts": {},
        }
    return render_template("dashboard/index.html", stats=stats, title="Dashboard")
