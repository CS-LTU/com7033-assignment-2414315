@echo off
if not exist .env (
    echo [Setup] Creating .env file from .env.example...
    copy .env.example .env >nul
)
echo [Setup] Preparing Python environment with uv...
uv sync

echo [Setup] Starting MongoDB container...
docker run -d -p 27017:27017 --name stroke_mongo mongo:4.4 >nul 2>&1
if errorlevel 1 docker start stroke_mongo

echo [Setup] Waiting for MongoDB to initialise...
timeout /t 3 /nobreak >nul

echo [Setup] Importing datasets...
uv run python import_dataset.py --clear

echo ===================================
echo [Success] Setup complete! You can now run 'run.bat' to start the application.
echo ===================================
pause
