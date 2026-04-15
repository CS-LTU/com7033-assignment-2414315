"""
models/db_mongo.py

MongoDB connection layer for patient records.
Uses Flask's application context (g) to reuse the client within a request.
"""

import logging
from flask import current_app, g
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


def get_mongo_db():
    """Return MongoDB database, reusing connection stored in Flask g."""
    if "mongo_client" not in g:
        try:
            g.mongo_client = MongoClient(
                current_app.config["MONGO_URI"],
                serverSelectionTimeoutMS=3000,
            )
            g.mongo_client.admin.command("ping")  # Verify connection
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.error("MongoDB connection failed: %s", exc)
            raise ConnectionError(
                "Cannot connect to MongoDB. Make sure mongod is running."
            ) from exc
    return g.mongo_client[current_app.config["MONGO_DB_NAME"]]


def get_patients_collection():
    """Convenience helper — returns the patients collection."""
    return get_mongo_db()["patients"]


def close_mongo_connection(exc=None) -> None:
    """Called on app context teardown to close the MongoDB client."""
    client = g.pop("mongo_client", None)
    if client is not None:
        client.close()
