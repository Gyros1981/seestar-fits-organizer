@echo off
echo Building Seestar FITS Organizer executable...
pyinstaller "Seestar FITS Organizer.spec" --clean --noconfirm
echo.
echo Build complete! Executable is in the 'dist' folder.
pause
