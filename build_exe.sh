#!/bin/bash
# Build Standalone Executable for Victoria 3 Economic Analyzer
# This creates a single executable file with everything bundled

echo "========================================"
echo "Victoria 3 Economic Analyzer - Builder"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "Step 1: Installing PyInstaller..."
pip3 install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Could not install PyInstaller"
    exit 1
fi

echo ""
echo "Step 2: Building standalone executable..."
echo "This may take a few minutes..."
echo ""

# Build the executable
pyinstaller --clean --onefile --windowed --name "Vic3_Analyzer" \
    --add-data "docs:docs" \
    --add-data "vendor:vendor" \
    --hidden-import=matplotlib \
    --hidden-import=numpy \
    --hidden-import=PIL \
    --hidden-import=watchdog \
    --hidden-import=watchdog.observers.inotify \
    gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "The executable is in: dist/Vic3_Analyzer"
echo ""
echo "File size: ~50-100 MB (includes Python + dependencies)"
echo ""
echo "You can now distribute this executable!"
echo "No Python installation needed on target computers."
echo ""

# Optional: Copy to releases folder
mkdir -p releases
cp "dist/Vic3_Analyzer" "releases/Vic3_Analyzer" 2>/dev/null
echo "Also copied to: releases/Vic3_Analyzer"
echo ""

echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Test the executable: Run dist/Vic3_Analyzer"
echo "2. Distribute: Share releases/Vic3_Analyzer with your team"
echo "3. Users just run it - no installation needed!"
echo ""
