@echo off
echo Building Seestar FITS Organizer executable...
pyinstaller --onefile --windowed --name "Seestar FITS Organizer" --icon="icon.ico" --add-data "TERMS_OF_SERVICE.md;." --add-data "DISCLAIMER.md;." main.py
echo.
echo Build complete! Executable is in the 'dist' folder.
pause
