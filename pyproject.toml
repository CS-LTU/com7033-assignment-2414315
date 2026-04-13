"""
models/user.py

User model for authentication.
Integrates with Flask-Login.
Passwords stored as Werkzeug pbkdf2:sha256 hashes — never plaintext.
"""

import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_sqlite import get_connection

logger = logging.getLogger(__name__)


class User(UserMixin):
    """Represents a hospital user (doctor/admin) stored in SQLite."""

    def __init__(self, id, username, email, password, role="doctor", created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password   # Hashed value from DB
        self.role = role
        self.created_at = created_at

    def get_id(self) -> str:
        """Required by Flask-Login — return user ID as string."""
        return str(self.id)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    # ── Password helpers ─────────────────────────────────────────────────────

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hash plaintext password. Uses pbkdf2:sha256 with 16-byte salt."""
        return generate_password_hash(plain, method="pbkdf2:sha256", salt_length=16)

    def verify_password(self, plain: str) -> bool:
        """Check plaintext password against stored hash."""
        return check_password_hash(self.password, plain)

    # ── CRUD ─────────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, username: str, email: str, password: str,
               role: str = "doctor") -> "User":
        """
        Insert new user with hashed password into SQLite.
        Raises ValueError if username or email already exists.
        """
        hashed = cls.hash_password(password)
        with get_connection() as conn:
            try:
                cur = conn.execute(
                    "INSERT INTO users (username,email,password,role) VALUES (?,?,?,?)",
                    (username.strip(), email.strip().lower(), hashed, role),
                )
                conn.commit()
                logger.info("User created: %s", username)
                return cls(cur.lastrowid, username, email, hashed, role)
            except Exception as exc:
                logger.warning("User creation failed for %s: %s", username, exc)
                raise ValueError("Username or email already exists.") from exc

    @classmethod
    def get_by_id(cls, user_id: int) -> "User | None":
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id=?", (user_id,)
            ).fetchone()
        return cls(**dict(row)) if row else None

    @classmethod
    def get_by_username(cls, username: str) -> "User | None":
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username=?", (username.strip(),)
            ).fetchone()
        return cls(**dict(row)) if row else None

    def __repr__(self):
        return f"<User {self.id} {self.username} [{self.role}]>"
