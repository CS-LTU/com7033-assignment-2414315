"""
tests/conftest.py
Shared pytest fixtures.
"""

import pytest
from unittest.mock import MagicMock
from stroke_app import create_app
from stroke_app.models.db_sqlite import init_sqlite_db


@pytest.fixture(scope="session")
def app():
    """Test app with in-memory SQLite and CSRF disabled."""
    test_app = create_app({
        "TESTING":          True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY":       "test-secret",
        "SQLITE_DB_PATH":   ":memory:",
        "MONGO_URI":        "mongodb://localhost:27017/",
        "MONGO_DB_NAME":    "stroke_test_db",
    })
    # Force SQLite table creation for in-memory DB
    with test_app.app_context():
        init_sqlite_db(test_app)
    return test_app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture
def mock_mongo(monkeypatch):
    """Replace MongoDB collection with MagicMock."""
    mock_col = MagicMock()
    monkeypatch.setattr(
        "stroke_app.models.patient.get_patients_collection",
        lambda: mock_col,
    )
    return mock_col


@pytest.fixture(scope="session")
def auth_client(app, client):
    """Test client pre-logged-in as testdoctor."""
    with app.app_context():
        from stroke_app.models.user import User
        try:
            User.create("testdoctor", "testdoctor@hospital.com", "Test@1234!")
        except ValueError:
            pass  # already exists

    client.post("/auth/login", data={
        "username": "testdoctor",
        "password": "Test@1234!",
    }, follow_redirects=True)
    return client
