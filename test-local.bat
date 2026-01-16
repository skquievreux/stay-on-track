@echo off
REM Local pre-commit test script
echo ========================================
echo Running local quality checks...
echo ========================================

echo.
echo [1/3] Running Pylint...
pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: Pylint found issues
    exit /b 1
)

echo.
echo [2/3] Testing PyInstaller build...
pyinstaller build.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo FAILED: PyInstaller build failed
    exit /b 1
)

echo.
echo [3/3] Checking if executable exists...
if not exist "dist\StayOnTrack\StayOnTrack.exe" (
    echo FAILED: Executable not found
    exit /b 1
)

echo.
echo ========================================
echo All checks passed! Safe to commit.
echo ========================================
