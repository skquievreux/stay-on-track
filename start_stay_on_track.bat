@echo off
setlocal
cd /d "%~dp0"

echo [Stay On Track] Starting application...

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [Stay On Track] Activating virtual environment...
    call venv\Scripts\activate.bat
    python src\main.py
    if errorlevel 1 (
        echo.
        echo [ERROR] Application crashed. Press any key to exit.
        pause > nul
    )
) else (
    echo [Stay On Track] Virtual environment not found. 
    echo Attempting to run with Poetry...
    poetry run python src\main.py
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not start application. 
        echo Please ensure dependencies are installed (run: poetry install)
        pause
    )
)

endlocal
