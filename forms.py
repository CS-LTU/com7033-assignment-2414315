#!/bin/bash
# cleanup.sh - Resets the project completely

echo "[Cleanup] Stopping and removing MongoDB container (if running)..."
sudo docker stop stroke_mongo 2>/dev/null
sudo docker rm stroke_mongo 2>/dev/null

echo "[Cleanup] Removing virtual environments..."
rm -rf .venv venv

echo "[Cleanup] Removing SQLite database..."
rm -f instance/users.db
rm -f users.db

echo "[Cleanup] Removing Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache

echo "✅ Cleanup complete!"
