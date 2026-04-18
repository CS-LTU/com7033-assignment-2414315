"""
tests/test_patient_routes.py

Integration tests for patient CRUD routes.
All tests use auth_client (logged-in) and mock_mongo.
"""

import pytest
from bson import ObjectId
from unittest.mock import MagicMock


SAMPLE = {
    "_id":               str(ObjectId()),
    "gender":            "Male",
    "age":               67.0,
    "hypertension":      0,
    "heart_disease":     1,
    "ever_married":      "Yes",
    "work_type":         "Private",
    "Residence_type":    "Urban",
    "avg_glucose_level": 228.69,
    "bmi":               36.6,
    "smoking_status":    "formerly smoked",
    "stroke":            1,
}


class TestListRoute:

    def test_list_page_loads(self, auth_client, mock_mongo):
        mock_mongo.count_documents.return_value = 0
        mock_mongo.find.return_value = iter([])
        r = auth_client.get("/patients/")
        assert r.status_code == 200
        assert b"Patient" in r.data

    def test_list_unauthenticated_redirects(self, client):
        r = client.get("/patients/", follow_redirects=False)
        assert r.status_code == 302


class TestAddRoute:

    def test_add_page_loads(self, auth_client):
        r = auth_client.get("/patients/add")
        assert r.status_code == 200
        assert b"Add Patient" in r.data

    def test_add_valid_post_redirects(self, auth_client, mock_mongo):
        mock_mongo.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        r = auth_client.post("/patients/add", data={
            "gender":            "Female",
            "age":               "61",
            "hypertension":      "0",
            "heart_disease":     "0",
            "ever_married":      "Yes",
            "work_type":         "Self-employed",
            "Residence_type":    "Rural",
            "avg_glucose_level": "202.21",
            "bmi":               "",           # blank BMI — valid
            "smoking_status":    "never smoked",
            "stroke":            "1",
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_add_invalid_age_stays_on_form(self, auth_client):
        r = auth_client.post("/patients/add", data={
            "gender":            "Male",
            "age":               "999",        # invalid
            "hypertension":      "0",
            "heart_disease":     "0",
            "ever_married":      "No",
            "work_type":         "Private",
            "Residence_type":    "Rural",
            "avg_glucose_level": "80",
            "bmi":               "22",
            "smoking_status":    "never smoked",
            "stroke":            "0",
        }, follow_redirects=True)
        assert b"Add Patient" in r.data or b"between" in r.data.lower()

    def test_add_heart_disease_field_present(self, auth_client):
        """Heart disease field must appear in the add form."""
        r = auth_client.get("/patients/add")
        assert b"heart_disease" in r.data or b"Heart Disease" in r.data


class TestViewRoute:

    def test_view_existing_patient(self, auth_client, mock_mongo):
        oid = ObjectId()
        mock_mongo.find_one.return_value = {**SAMPLE, "_id": oid}
        r = auth_client.get(f"/patients/{oid}")
        assert r.status_code == 200

    def test_view_missing_patient_redirects(self, auth_client, mock_mongo):
        mock_mongo.find_one.return_value = None
        r = auth_client.get(f"/patients/{ObjectId()}", follow_redirects=True)
        assert b"not found" in r.data.lower()


class TestDeleteRoute:

    def test_delete_post_redirects(self, auth_client, mock_mongo):
        mock_mongo.delete_one.return_value = MagicMock(deleted_count=1)
        r = auth_client.post(f"/patients/{ObjectId()}/delete",
                             follow_redirects=True)
        assert r.status_code == 200

    def test_delete_via_get_not_allowed(self, auth_client):
        """GET on delete endpoint must return 405 Method Not Allowed."""
        r = auth_client.get(f"/patients/{ObjectId()}/delete")
        assert r.status_code == 405


class TestAPIRoute:

    def test_api_returns_json(self, auth_client, mock_mongo):
        oid = ObjectId()
        mock_mongo.find_one.return_value = {**SAMPLE, "_id": oid}
        r = auth_client.get(f"/patients/api/{oid}")
        assert r.status_code == 200
        assert r.content_type == "application/json"
        data = r.get_json()
        assert "gender" in data

    def test_api_missing_returns_404_json(self, auth_client, mock_mongo):
        mock_mongo.find_one.return_value = None
        r = auth_client.get(f"/patients/api/{ObjectId()}")
        assert r.status_code == 404
        assert "error" in r.get_json()
