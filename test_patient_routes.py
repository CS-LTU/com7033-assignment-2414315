"""
tests/test_patient_model.py

Unit tests for Patient model validation and mocked CRUD.
Uses real dataset field values (e.g. work_type='children').
"""

import pytest
from bson import ObjectId
from unittest.mock import MagicMock
from stroke_app.models.patient import Patient


@pytest.fixture
def valid_data():
    """A complete, valid patient record matching dataset values."""
    return {
        "gender":            "Female",
        "age":               "67",
        "hypertension":      "0",
        "heart_disease":     "1",
        "ever_married":      "Yes",
        "work_type":         "Private",
        "Residence_type":    "Urban",
        "avg_glucose_level": "228.69",
        "bmi":               "36.6",
        "smoking_status":    "formerly smoked",
        "stroke":            "1",
    }


class TestPatientValidation:

    def test_valid_data_passes(self, valid_data):
        result = Patient.validate(valid_data.copy())
        assert result["age"] == 67.0
        assert result["stroke"] == 1
        assert result["heart_disease"] == 1

    def test_bmi_na_stored_as_none(self, valid_data):
        """N/A BMI (as in dataset) should become None, not raise an error."""
        valid_data["bmi"] = "N/A"
        result = Patient.validate(valid_data)
        assert result["bmi"] is None

    def test_bmi_blank_stored_as_none(self, valid_data):
        valid_data["bmi"] = ""
        result = Patient.validate(valid_data)
        assert result["bmi"] is None

    def test_work_type_lowercase_children_valid(self, valid_data):
        """Dataset uses lowercase 'children' — must be accepted."""
        valid_data["work_type"] = "children"
        result = Patient.validate(valid_data)
        assert result["work_type"] == "children"

    def test_invalid_gender_raises(self, valid_data):
        valid_data["gender"] = "Unknown"
        with pytest.raises(ValueError, match="Gender"):
            Patient.validate(valid_data)

    def test_age_above_120_raises(self, valid_data):
        valid_data["age"] = "121"
        with pytest.raises(ValueError, match="Age"):
            Patient.validate(valid_data)

    def test_negative_age_raises(self, valid_data):
        valid_data["age"] = "-1"
        with pytest.raises(ValueError, match="Age"):
            Patient.validate(valid_data)

    def test_invalid_hypertension_raises(self, valid_data):
        valid_data["hypertension"] = "5"
        with pytest.raises(ValueError, match="Hypertension"):
            Patient.validate(valid_data)

    def test_invalid_heart_disease_raises(self, valid_data):
        valid_data["heart_disease"] = "yes"
        with pytest.raises(ValueError, match="Heart disease"):
            Patient.validate(valid_data)

    def test_invalid_work_type_raises(self, valid_data):
        valid_data["work_type"] = "Freelance"
        with pytest.raises(ValueError, match="work_type"):
            Patient.validate(valid_data)

    def test_invalid_smoking_status_raises(self, valid_data):
        valid_data["smoking_status"] = "casual"
        with pytest.raises(ValueError, match="smoking_status"):
            Patient.validate(valid_data)

    def test_glucose_out_of_range_raises(self, valid_data):
        valid_data["avg_glucose_level"] = "700"
        with pytest.raises(ValueError, match="glucose"):
            Patient.validate(valid_data)

    def test_multiple_errors_reported_together(self, valid_data):
        """All errors should be joined in a single ValueError."""
        valid_data["gender"] = "X"
        valid_data["age"] = "999"
        with pytest.raises(ValueError) as exc:
            Patient.validate(valid_data)
        assert "|" in str(exc.value)   # Multiple errors joined with |

    def test_numeric_values_coerced(self, valid_data):
        """String numbers must be coerced to float/int."""
        result = Patient.validate(valid_data)
        assert isinstance(result["age"], float)
        assert isinstance(result["hypertension"], int)
        assert isinstance(result["stroke"], int)


class TestPatientCRUD:

    def test_create_calls_insert_one(self, mock_mongo, valid_data):
        mock_mongo.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        pid = Patient.create(valid_data.copy())
        assert isinstance(pid, str)
        mock_mongo.insert_one.assert_called_once()

    def test_get_by_id_returns_dict(self, mock_mongo):
        oid = ObjectId()
        mock_mongo.find_one.return_value = {"_id": oid, "gender": "Male", "age": 45}
        result = Patient.get_by_id(str(oid))
        assert result["_id"] == str(oid)
        assert result["gender"] == "Male"

    def test_get_by_invalid_id_returns_none(self, mock_mongo):
        assert Patient.get_by_id("not-valid-id") is None

    def test_get_by_id_not_found_returns_none(self, mock_mongo):
        mock_mongo.find_one.return_value = None
        assert Patient.get_by_id(str(ObjectId())) is None

    def test_delete_returns_true(self, mock_mongo):
        mock_mongo.delete_one.return_value = MagicMock(deleted_count=1)
        assert Patient.delete(str(ObjectId())) is True

    def test_delete_not_found_returns_false(self, mock_mongo):
        mock_mongo.delete_one.return_value = MagicMock(deleted_count=0)
        assert Patient.delete(str(ObjectId())) is False

    def test_update_returns_true_on_change(self, mock_mongo, valid_data):
        mock_mongo.update_one.return_value = MagicMock(modified_count=1)
        assert Patient.update(str(ObjectId()), valid_data.copy()) is True

    def test_update_invalid_id_returns_false(self, mock_mongo, valid_data):
        assert Patient.update("bad-id", valid_data.copy()) is False
