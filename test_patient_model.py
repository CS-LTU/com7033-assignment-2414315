"""
tests/test_auth_routes.py

Integration tests for authentication routes.
"""

import pytest


class TestRegistration:

    def test_register_page_loads(self, client):
        r = client.get("/auth/register")
        assert r.status_code == 200
        assert b"Create Account" in r.data

    def test_register_success_redirects_to_login(self, client, app):
        r = client.post("/auth/register", data={
            "username":         "newdoc",
            "email":            "newdoc@h.com",
            "password":         "Secure@99!",
            "confirm_password": "Secure@99!",
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b"Sign In" in r.data or b"sign in" in r.data.lower()

    def test_register_duplicate_username(self, client, app):
        with app.app_context():
            from stroke_app.models.user import User
            try: User.create("existing", "existing@h.com", "Secure@99!")
            except ValueError: pass

        r = client.post("/auth/register", data={
            "username":         "existing",
            "email":            "other@h.com",
            "password":         "Secure@99!",
            "confirm_password": "Secure@99!",
        }, follow_redirects=True)
        assert b"already exists" in r.data.lower()

    def test_register_password_mismatch(self, client):
        r = client.post("/auth/register", data={
            "username":         "mismatch",
            "email":            "mm@h.com",
            "password":         "Secure@99!",
            "confirm_password": "Different@1!",
        }, follow_redirects=True)
        assert b"match" in r.data.lower()

    def test_register_weak_password_rejected(self, client):
        r = client.post("/auth/register", data={
            "username":         "weakpwd",
            "email":            "weak@h.com",
            "password":         "password1",   # no uppercase or special char
            "confirm_password": "password1",
        }, follow_redirects=True)
        # Should stay on register page, not redirect to login
        assert b"Create Account" in r.data or b"uppercase" in r.data.lower()


class TestLogin:

    def test_login_page_loads(self, client):
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert b"Sign In" in r.data

    def test_login_success_redirects_to_dashboard(self, client, app):
        with app.app_context():
            from stroke_app.models.user import User
            try: User.create("logintest", "lt@h.com", "Login@123!")
            except ValueError: pass

        r = client.post("/auth/login", data={
            "username": "logintest",
            "password": "Login@123!",
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b"Dashboard" in r.data

    def test_login_wrong_password_generic_error(self, client, app):
        with app.app_context():
            from stroke_app.models.user import User
            try: User.create("wrongpwd", "wp@h.com", "Correct@1!")
            except ValueError: pass

        r = client.post("/auth/login", data={
            "username": "wrongpwd",
            "password": "WrongPass@1!",
        }, follow_redirects=True)
        assert b"Invalid username or password" in r.data

    def test_login_nonexistent_user_generic_error(self, client):
        r = client.post("/auth/login", data={
            "username": "ghost",
            "password": "Ghost@123!",
        }, follow_redirects=True)
        assert b"Invalid username or password" in r.data


class TestLogout:

    def test_logout_redirects_to_login(self, auth_client):
        r = auth_client.get("/auth/logout", follow_redirects=True)
        assert b"Sign In" in r.data or b"signed out" in r.data.lower()


class TestProtectedRoutes:

    def test_dashboard_redirects_unauthenticated(self, client):
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code == 302
        assert "/auth/login" in r.headers["Location"]

    def test_patients_redirects_unauthenticated(self, client):
        r = client.get("/patients/", follow_redirects=False)
        assert r.status_code == 302
        assert "/auth/login" in r.headers["Location"]

    def test_add_patient_redirects_unauthenticated(self, client):
        r = client.get("/patients/add", follow_redirects=False)
        assert r.status_code == 302
