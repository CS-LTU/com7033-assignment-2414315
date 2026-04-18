"""
models/patient.py

Patient model for MongoDB.
Field values match the actual Kaggle Stroke Prediction Dataset exactly:
  - work_type uses lowercase 'children' (as in the CSV)
  - bmi may be None (was 'N/A' in CSV — stored as null in MongoDB)
  - heart_disease field included (present in dataset)
"""

import logging
from bson import ObjectId
from bson.errors import InvalidId
from .db_mongo import get_patients_collection

logger = logging.getLogger(__name__)

# ── Valid categorical values (exactly as in dataset) ────────────────────────
VALID_GENDERS          = {"Male", "Female", "Other"}
VALID_WORK_TYPES       = {"children", "Govt_job", "Never_worked", "Private", "Self-employed"}
VALID_RESIDENCE_TYPES  = {"Rural", "Urban"}
VALID_SMOKING_STATUSES = {"formerly smoked", "never smoked", "smokes", "Unknown"}
VALID_EVER_MARRIED     = {"Yes", "No"}


class Patient:
    """Patient record stored in MongoDB."""

    @staticmethod
    def validate(data: dict) -> dict:
        """
        Validate and coerce all patient fields.
        Returns cleaned dict or raises ValueError with detail.
        """
        errors = []

        # Gender
        if data.get("gender") not in VALID_GENDERS:
            errors.append(f"Gender must be one of {sorted(VALID_GENDERS)}.")

        # Age
        try:
            age = float(data.get("age", -1))
            if not (0 <= age <= 120):
                errors.append("Age must be between 0 and 120.")
            data["age"] = age
        except (ValueError, TypeError):
            errors.append("Age must be a valid number.")

        # Hypertension
        if str(data.get("hypertension", "")) not in {"0", "1"}:
            errors.append("Hypertension must be 0 or 1.")
        else:
            data["hypertension"] = int(data["hypertension"])

        # Heart disease
        if str(data.get("heart_disease", "")) not in {"0", "1"}:
            errors.append("Heart disease must be 0 or 1.")
        else:
            data["heart_disease"] = int(data["heart_disease"])

        # Ever married
        if data.get("ever_married") not in VALID_EVER_MARRIED:
            errors.append("ever_married must be 'Yes' or 'No'.")

        # Work type
        if data.get("work_type") not in VALID_WORK_TYPES:
            errors.append(f"work_type must be one of {sorted(VALID_WORK_TYPES)}.")

        # Residence type
        if data.get("Residence_type") not in VALID_RESIDENCE_TYPES:
            errors.append("Residence_type must be 'Rural' or 'Urban'.")

        # Average glucose level
        try:
            glucose = float(data.get("avg_glucose_level", -1))
            if not (0 <= glucose <= 600):
                errors.append("avg_glucose_level must be between 0 and 600.")
            data["avg_glucose_level"] = round(glucose, 2)
        except (ValueError, TypeError):
            errors.append("avg_glucose_level must be a valid number.")

        # BMI — allowed to be blank/None (was N/A in dataset)
        bmi_raw = data.get("bmi", "")
        if bmi_raw in (None, "", "N/A", "n/a"):
            data["bmi"] = None
        else:
            try:
                bmi = float(bmi_raw)
                if not (5 <= bmi <= 100):
                    errors.append("BMI must be between 5 and 100.")
                data["bmi"] = round(bmi, 2)
            except (ValueError, TypeError):
                errors.append("BMI must be a valid number or left blank.")

        # Smoking status
        if data.get("smoking_status") not in VALID_SMOKING_STATUSES:
            errors.append(f"smoking_status must be one of {sorted(VALID_SMOKING_STATUSES)}.")

        # Stroke outcome
        if str(data.get("stroke", "")) not in {"0", "1"}:
            errors.append("Stroke must be 0 or 1.")
        else:
            data["stroke"] = int(data["stroke"])

        if errors:
            raise ValueError(" | ".join(errors))

        return data

    # ── CRUD ─────────────────────────────────────────────────────────────────

    @staticmethod
    def create(data: dict) -> str:
        """Validate then insert patient. Returns string ObjectId."""
        clean = Patient.validate(data)
        col = get_patients_collection()
        result = col.insert_one(clean)
        logger.info("Patient created: %s", result.inserted_id)
        return str(result.inserted_id)

    @staticmethod
    def get_all(page: int = 1, per_page: int = 20,
                filters: dict = None) -> tuple:
        """Return (list_of_patients, total_count) with pagination."""
        col = get_patients_collection()
        query = filters or {}
        total = col.count_documents(query)
        cursor = col.find(query).sort("_id", -1).skip((page - 1) * per_page).limit(per_page)
        patients = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            patients.append(doc)
        return patients, total

    @staticmethod
    def get_by_id(patient_id: str) -> dict | None:
        """Fetch single patient by MongoDB ObjectId string."""
        try:
            oid = ObjectId(patient_id)
        except (InvalidId, TypeError):
            return None
        col = get_patients_collection()
        doc = col.find_one({"_id": oid})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def update(patient_id: str, data: dict) -> bool:
        """Validate then update patient. Returns True if modified."""
        try:
            oid = ObjectId(patient_id)
        except (InvalidId, TypeError):
            return False
        clean = Patient.validate(data)
        col = get_patients_collection()
        result = col.update_one({"_id": oid}, {"$set": clean})
        logger.info("Patient %s updated", patient_id)
        return result.modified_count > 0

    @staticmethod
    def delete(patient_id: str) -> bool:
        """Delete patient. Returns True if deleted."""
        try:
            oid = ObjectId(patient_id)
        except (InvalidId, TypeError):
            return False
        col = get_patients_collection()
        result = col.delete_one({"_id": oid})
        logger.info("Patient %s deleted", patient_id)
        return result.deleted_count > 0

    @staticmethod
    def get_statistics() -> dict:
        """Aggregate dashboard statistics using MongoDB pipeline."""
        col = get_patients_collection()
        total = col.count_documents({})
        if total == 0:
            return {
                "total": 0, "stroke_count": 0, "stroke_pct": 0,
                "hypertension_count": 0, "heart_disease_count": 0,
                "avg_age": 0, "avg_bmi": 0, "avg_glucose": 0,
                "gender_counts": {}, "smoking_counts": {},
            }

        stroke_count      = col.count_documents({"stroke": 1})
        hypertension_count = col.count_documents({"hypertension": 1})
        heart_disease_count = col.count_documents({"heart_disease": 1})

        # Numeric averages
        agg = list(col.aggregate([{"$group": {
            "_id": None,
            "avg_age":     {"$avg": "$age"},
            "avg_bmi":     {"$avg": {"$ifNull": ["$bmi", None]}},
            "avg_glucose": {"$avg": "$avg_glucose_level"},
        }}]))

        # Gender breakdown
        gender_agg = col.aggregate([
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ])
        gender_counts = {d["_id"]: d["count"] for d in gender_agg}

        # Smoking breakdown
        smoke_agg = col.aggregate([
            {"$group": {"_id": "$smoking_status", "count": {"$sum": 1}}}
        ])
        smoking_counts = {d["_id"]: d["count"] for d in smoke_agg}

        a = agg[0] if agg else {}
        return {
            "total":               total,
            "stroke_count":        stroke_count,
            "stroke_pct":          round(stroke_count / total * 100, 1),
            "hypertension_count":  hypertension_count,
            "heart_disease_count": heart_disease_count,
            "avg_age":             round(a.get("avg_age") or 0, 1),
            "avg_bmi":             round(a.get("avg_bmi") or 0, 1),
            "avg_glucose":         round(a.get("avg_glucose") or 0, 1),
            "gender_counts":       gender_counts,
            "smoking_counts":      smoking_counts,
        }
