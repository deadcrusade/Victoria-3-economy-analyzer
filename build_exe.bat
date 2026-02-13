@echo off
REM Build Standalone Executable for Victoria 3 Economic Analyzer
REM This creates a single .exe file with everything bundled

echo ========================================
echo Victoria 3 Economic Analyzer - Builder
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

echo Step 1: Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Could not install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Building standalone executable...
echo This may take a few minutes...
echo.

REM Build the executable
python -m PyInstaller --clean --onefile --windowed --name "Vic3_Analyzer" ^
    --icon=NONE ^
    --add-data "docs;docs" ^
    --hidden-import=matplotlib ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The executable is in: dist\Vic3_Analyzer.exe
echo.
echo File size: ~50-100 MB (includes Python + dependencies)
echo.
echo You can now distribute this .exe file!
echo No Python installation needed on target computers.
echo.

REM Optional: Copy to releases folder
if not exist "releases" mkdir releases
copy "dist\Vic3_Analyzer.exe" "releases\Vic3_Analyzer.exe" >nul 2>&1
echo Also copied to: releases\Vic3_Analyzer.exe
echo.

echo ========================================
echo Next Steps:
echo ========================================
echo 1. Test the .exe: Run dist\Vic3_Analyzer.exe
echo 2. Distribute: Share releases\Vic3_Analyzer.exe with your team
echo 3. Users just double-click - no installation needed!
echo.

pause
