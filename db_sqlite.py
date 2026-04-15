"""
models/db_sqlite.py

SQLite connection layer for user authentication.
All queries use parameterised statements — never string interpolation.
This prevents SQL injection attacks.
"""

import sqlite3
import contextlib
import logging

logger = logging.getLogger(__name__)
_DB_PATH: str = ""


def init_sqlite_db(app) -> None:
    """Create users table on first run. Called once at app startup."""
    global _DB_PATH
    _DB_PATH = app.config["SQLITE_DB_PATH"]
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                email      TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,
                role       TEXT    NOT NULL DEFAULT 'doctor',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("SQLite initialised at %s", _DB_PATH)


@contextlib.contextmanager
def get_connection():
    """
    Context manager yielding a sqlite3 connection.
    Rows are accessible by column name via Row factory.
    Auto-closes on exit.
    """
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.Error as exc:
        logger.error("SQLite error: %s", exc)
        conn.rollback()
        raise
    finally:
        conn.close()
