@echo off
REM Victoria 3 Economic Analyzer - Quick Launch Script for Windows
REM 
REM Instructions:
REM 1. Edit the SAVE_DIR path below to match your Victoria 3 save location
REM 2. Double-click this file to run the analyzer

REM ===== CONFIGURATION =====
REM Edit this line to point to your save games folder
SET SAVE_DIR=C:\Users\%USERNAME%\Documents\Paradox Interactive\Victoria 3\save games

REM Check interval in seconds (how often to check for new saves)
SET INTERVAL=60

REM =========================

echo ========================================
echo Victoria 3 Economic Analyzer
echo ========================================
echo.
echo Save Directory: %SAVE_DIR%
echo Check Interval: %INTERVAL% seconds
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if save directory exists
if not exist "%SAVE_DIR%" (
    echo ERROR: Save directory not found: %SAVE_DIR%
    echo.
    echo Please edit this batch file and set SAVE_DIR to your save location.
    echo Right-click this file and select "Edit" to change the path.
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    echo Make sure this batch file is in the vic3_analyzer folder
    pause
    exit /b 1
)

echo Checking dependencies...
pip install -q -r requirements.txt

echo.
echo Starting analyzer...
echo Press Ctrl+C to stop monitoring and generate visualizations
echo.
echo ========================================
echo.

REM Run the analyzer in interactive mode
python main.py "%SAVE_DIR%"

pause
