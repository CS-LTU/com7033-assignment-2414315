# StrokeGuard Setup Guide (Linux)

I've reviewed the codebase and identified a few startup problems that would prevent the application from running on your Linux machine. I've already fixed the code, but you will need to follow these steps to get everything up and running.

## 🚨 Startup Problems Addressed
1. **Import Error in `run.py`**: The main entry point was failing with a `ModuleNotFoundError` because it was placed inside the package. **I have fixed this securely** within the script so it resolves paths correctly.
2. **Incompatible Virtual Environment**: The `/venv` folder included in your download was created on a Windows machine. It won't work on your Linux system.
3. **Missing MongoDB Engine**: The application requires MongoDB to be running to store patient data, which isn't currently installed/active in your standard environment.

---

## The `uv` Automation Track

To make setting up easier, the application has been initialized with `uv` and includes simple automation scripts available for both Linux/macOS (`.sh`) and Windows (`.bat`).

> **Windows Users:** You can simply double-click the `.bat` files in your File Explorer!

### 1. Setup Everything
From the directory containing this file, run the setup script. It will synchronize all Python dependencies with `uv`, boot up the MongoDB container using Docker Desktop, and import the CSV data.

**Linux/macOS:**
```bash
./setup.sh
```
**Windows:**
```cmd
setup.bat
```

### 2. Run the App
Once setup completes, start the local Flask server:

**Linux/macOS:**
```bash
./run.sh
```
**Windows:**
```cmd
run.bat
```

The app will now be running correctly. You can access it in your browser at `http://127.0.0.1:5000`. You can begin by clicking **Register** to create a test doctor account!

### 3. Teardown
If you ever want to perform a deep clean, drop the MongoDB database container, destroy the `.venv`, or clear all caches:

**Linux/macOS:**
```bash
./cleanup.sh
```
**Windows:**
```cmd
cleanup.bat
```
