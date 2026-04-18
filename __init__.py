"""
tests/test_user_model.py

Unit tests for the User model:
  - Account creation
  - Duplicate prevention
  - Password hashing (never stores plaintext)
  - Password verification
  - DB lookups
"""

import pytest
from stroke_app.models.user import User


class TestUserCreation:

    def test_create_returns_user_object(self, app):
        with app.app_context():
            u = User.create("dr_jones", "jones@h.com", "Secure@99!")
            assert u.id is not None
            assert u.username == "dr_jones"
            assert u.role == "doctor"

    def test_duplicate_username_raises(self, app):
        with app.app_context():
            User.create("dup_name", "dup1@h.com", "Secure@99!")
            with pytest.raises(ValueError, match="already exists"):
                User.create("dup_name", "dup2@h.com", "Secure@99!")

    def test_duplicate_email_raises(self, app):
        with app.app_context():
            User.create("user_aa", "shared@h.com", "Secure@99!")
            with pytest.raises(ValueError):
                User.create("user_bb", "shared@h.com", "Secure@99!")


class TestPasswordSecurity:

    def test_password_is_hashed(self, app):
        """Stored password must never equal the plaintext input."""
        with app.app_context():
            u = User.create("hashcheck", "hc@h.com", "Secure@99!")
            assert u.password != "Secure@99!"
            assert len(u.password) > 30        # hash is always long

    def test_hash_uses_pbkdf2(self, app):
        """Hash string should start with the pbkdf2 identifier."""
        with app.app_context():
            u = User.create("pbkdf2check", "pbkdf2@h.com", "Secure@99!")
            assert u.password.startswith("pbkdf2:sha256")

    def test_correct_password_verified(self, app):
        with app.app_context():
            u = User.create("verifyok", "vok@h.com", "Correct@1!")
            assert u.verify_password("Correct@1!") is True

    def test_wrong_password_rejected(self, app):
        with app.app_context():
            u = User.create("verifybad", "vbad@h.com", "Correct@1!")
            assert u.verify_password("Wrong@1!") is False

    def test_empty_password_rejected(self, app):
        with app.app_context():
            u = User.create("emptytest", "emp@h.com", "Correct@1!")
            assert u.verify_password("") is False


class TestUserLookups:

    def test_get_by_id(self, app):
        with app.app_context():
            u = User.create("bylookup", "bylookup@h.com", "Secure@99!")
            found = User.get_by_id(u.id)
            assert found is not None
            assert found.username == "bylookup"

    def test_get_by_username(self, app):
        with app.app_context():
            User.create("CaseUser", "caseuser@h.com", "Secure@99!")
            # SQLite COLLATE NOCASE — any case should work
            assert User.get_by_username("CaseUser") is not None
            assert User.get_by_username("caseuser") is not None

    def test_get_by_nonexistent_id_returns_none(self, app):
        with app.app_context():
            assert User.get_by_id(999999) is None

    def test_get_by_nonexistent_username_returns_none(self, app):
        with app.app_context():
            assert User.get_by_username("nobody_xyz") is None
