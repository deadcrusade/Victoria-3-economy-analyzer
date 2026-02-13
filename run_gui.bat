@echo off
REM Victoria 3 Economic Analyzer - GUI Launcher
REM Double-click this file to start the GUI application

echo ========================================
echo Victoria 3 Economic Analyzer - GUI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install requirements if needed
if exist requirements.txt (
    echo Checking dependencies...
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Warning: Could not install dependencies
        echo Continuing anyway...
    )
)

echo Starting GUI application...
echo.

REM Launch GUI
python gui.py

REM If GUI exits with error
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    pause
)
