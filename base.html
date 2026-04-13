#!/bin/bash
# setup.sh - Initialises the project

if [ ! -f .env ]; then
    echo "[Setup] Creating .env file from .env.example..."
    cp .env.example .env
fi

echo "[Setup] Preparing Python environment with uv..."
uv sync

echo "[Setup] Ensuring Docker is running..."
sudo systemctl start docker

echo "[Setup] Starting MongoDB container..."
sudo docker run -d -p 27017:27017 --name stroke_mongo mongo:4.4 2>/dev/null || sudo docker start stroke_mongo

echo "[Setup] Waiting for MongoDB to initialise..."
sleep 3

echo "[Setup] Importing datasets..."
uv run python import_dataset.py --clear

echo "✅ Setup complete! You can now run './run.sh' to start the application."
