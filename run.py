"""
routes/patients.py  –  Patients Blueprint
Full CRUD for patient records in MongoDB.
All writes require login + CSRF-protected form submission.
"""

import logging
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify)
from flask_login import login_required, current_user
from ..forms import PatientForm, PatientSearchForm
from ..models.patient import Patient

logger = logging.getLogger(__name__)
patients_bp = Blueprint("patients", __name__, url_prefix="/patients")
PER_PAGE = 15


# ── List ──────────────────────────────────────────────────────────────────────

@patients_bp.route("/", methods=["GET"])
@login_required
def list_patients():
    search_form = PatientSearchForm(request.args, meta={"csrf": False})
    page = request.args.get("page", 1, type=int)

    filters = {}
    if request.args.get("gender"):
        filters["gender"] = request.args.get("gender")
    stroke_val = request.args.get("stroke", "")
    if stroke_val in ("0", "1"):
        filters["stroke"] = int(stroke_val)

    try:
        patients, total = Patient.get_all(page=page, per_page=PER_PAGE, filters=filters)
    except Exception as exc:
        logger.error("Patient list error: %s", exc)
        flash("Cannot reach MongoDB. Is mongod running?", "danger")
        patients, total = [], 0

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    return render_template("patients/list.html",
                           patients=patients, page=page,
                           total_pages=total_pages, total=total,
                           search_form=search_form, title="Patients")


# ── Create ────────────────────────────────────────────────────────────────────

@patients_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        data = _form_to_dict(form)
        try:
            pid = Patient.create(data)
            flash(f"Patient added (ID: {pid[:8]}…).", "success")
            logger.info("%s added patient %s", current_user.username, pid)
            return redirect(url_for("patients.list_patients"))
        except Exception as exc:
            flash(f"Error: {exc}", "danger")
    return render_template("patients/form.html", form=form,
                           title="Add Patient", action="Add", patient_id=None)


# ── Read ──────────────────────────────────────────────────────────────────────

@patients_bp.route("/<patient_id>")
@login_required
def view_patient(patient_id):
    patient = Patient.get_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients.list_patients"))
    return render_template("patients/detail.html", patient=patient, title="Patient Detail")


# ── Update ────────────────────────────────────────────────────────────────────

@patients_bp.route("/<patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = Patient.get_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients.list_patients"))

    form = PatientForm(data=patient)
    if form.validate_on_submit():
        try:
            Patient.update(patient_id, _form_to_dict(form))
            flash("Record updated.", "success")
            logger.info("%s updated patient %s", current_user.username, patient_id)
            return redirect(url_for("patients.view_patient", patient_id=patient_id))
        except Exception as exc:
            flash(f"Update error: {exc}", "danger")

    return render_template("patients/form.html", form=form,
                           title="Edit Patient", action="Update",
                           patient_id=patient_id)


# ── Delete ────────────────────────────────────────────────────────────────────

@patients_bp.route("/<patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """POST-only (CSRF protected) delete endpoint."""
    if Patient.delete(patient_id):
        flash("Patient record deleted.", "success")
        logger.info("%s deleted patient %s", current_user.username, patient_id)
    else:
        flash("Patient not found.", "warning")
    return redirect(url_for("patients.list_patients"))


# ── JSON API ──────────────────────────────────────────────────────────────────

@patients_bp.route("/api/<patient_id>")
@login_required
def api_patient(patient_id):
    """REST-style JSON endpoint for a single patient record."""
    patient = Patient.get_by_id(patient_id)
    if not patient:
        return jsonify({"error": "Not found"}), 404
    return jsonify(patient)


# ── Helper ────────────────────────────────────────────────────────────────────

def _form_to_dict(form: PatientForm) -> dict:
    """Extract patient fields from a validated PatientForm."""
    return {
        "gender":            form.gender.data,
        "age":               form.age.data,
        "hypertension":      form.hypertension.data,
        "heart_disease":     form.heart_disease.data,
        "ever_married":      form.ever_married.data,
        "work_type":         form.work_type.data,
        "Residence_type":    form.Residence_type.data,
        "avg_glucose_level": form.avg_glucose_level.data,
        "bmi":               form.bmi.data,
        "smoking_status":    form.smoking_status.data,
        "stroke":            form.stroke.data,
    }
