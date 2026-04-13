"""
run.py — Application entry point

Usage (development):
    python run.py

Usage (production with Gunicorn):
    gunicorn "stroke_app:create_app()" --bind 0.0.0.0:8000 --workers 4
"""
import sys
import os

# Add parent directory to sys.path so 'stroke_app' can be imported correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stroke_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
