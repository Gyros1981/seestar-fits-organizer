#!/bin/bash

# Bash strict mode (exit on error, unset variables, pipe failures)
set -euo pipefail

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run PyInstaller build
echo "Building Seestar FITS Organizer..."
pyinstaller --noconfirm --onefile --windowed --name "Seestar FITS Organizer" --add-data "TERMS_OF_SERVICE.md:." --add-data "DISCLAIMER.md:." main.py

echo "Build complete! Executable is in the 'dist' folder."
