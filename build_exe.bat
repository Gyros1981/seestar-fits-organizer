@echo off
echo Building Seestar FITS Organizer executable...
pyinstaller --onefile --windowed --name "Seestar FITS Organizer" main.py
echo.
echo Build complete! Executable is in the 'dist' folder.
pause
