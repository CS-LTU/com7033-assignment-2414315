@echo off
echo [Cleanup] Stopping and removing MongoDB container (if running)...
docker stop stroke_mongo >nul 2>&1
docker rm stroke_mongo >nul 2>&1

echo [Cleanup] Removing virtual environments...
if exist .venv rmdir /s /q .venv
if exist venv rmdir /s /q venv

echo [Cleanup] Removing SQLite database...
if exist instance\users.db del /q instance\users.db
if exist users.db del /q users.db

echo [Cleanup] Removing Python caches...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist .pytest_cache rmdir /s /q .pytest_cache

echo ===================================
echo [Success] Cleanup complete!
echo ===================================
pause
