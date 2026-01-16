@echo off
cd /d "%~dp0"

if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "src\main.py"
) else (
    echo Virtual environment not found. Attempting to use system Python...
    start "" pythonw "src\main.py"
)
