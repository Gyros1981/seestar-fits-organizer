"""
Mac Build Script for Seestar FITS Organizer

This script creates a macOS .app bundle using PyInstaller.
Run this on a Mac with Python and PyInstaller installed.

Usage:
    python scripts/build_mac.py

Output:
    dist/SeestarFITSOrganizer.app

Requirements:
    - macOS 10.14 or later
    - Python 3.9+
    - PyInstaller: pip install pyinstaller
    - All app dependencies installed
"""

import subprocess
import sys
import shutil
from pathlib import Path


def build_mac_app():
    """Build the macOS .app bundle."""
    
    print("=" * 60)
    print("Building Seestar FITS Organizer for macOS")
    print("=" * 60)
    
    # Clean previous builds
    print("\n1. Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"   Removed {folder}/")
    
    # PyInstaller command
    print("\n2. Running PyInstaller...")
    
    cmd = [
        'pyinstaller',
        '--name', 'SeestarFITSOrganizer',
        '--windowed',  # No console window
        '--onefile',   # Single executable (can use --onedir instead)
        '--clean',
        '--noconfirm',
        
        # macOS specific options
        '--osx-bundle-identifier', 'com.guyronen.seestar-fits-organizer',
        
        # Icon (optional - create an .icns file)
        # '--icon', 'assets/icon.icns',
        
        # Add data files
        '--add-data', 'core:core',
        '--add-data', 'ui:ui',
        '--add-data', 'docs:docs',
        
        # Hidden imports (ensure these get included)
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._imagingtk',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'astropy',
        '--hidden-import', 'numpy',
        
        # Main script
        'main.py'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    
    print("   ✓ PyInstaller completed")
    
    # Post-build steps
    print("\n3. Post-build configuration...")
    
    app_path = Path('dist/SeestarFITSOrganizer.app')
    
    if not app_path.exists():
        print(f"❌ Expected app not found at {app_path}")
        sys.exit(1)
    
    print(f"   ✓ App bundle created: {app_path}")
    
    # Print info about the app
    print("\n4. Build complete!")
    print("=" * 60)
    print(f"Output: {app_path.absolute()}")
    print("\nTo test:")
    print(f"  open {app_path}")
    print("\nTo distribute:")
    print("  - Zip the .app folder")
    print("  - Or create a DMG for professional distribution")
    print("=" * 60)
    
    return app_path


def create_dmg(app_path: Path):
    """
    Create a DMG for distribution (optional).
    Requires create-dmg to be installed:
        brew install create-dmg
    """
    print("\n5. Creating DMG...")
    
    dmg_path = app_path.parent / "SeestarFITSOrganizer.dmg"
    
    cmd = [
        'create-dmg',
        '--volname', 'Seestar FITS Organizer',
        '--window-pos', '200', '120',
        '--window-size', '600', '400',
        '--icon-size', '100',
        '--app-drop-link', '450', '185',
        str(dmg_path),
        str(app_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✓ DMG created: {dmg_path}")
    else:
        print("   ⚠️ DMG creation failed (create-dmg may not be installed)")
        print("   App bundle is still available at:", app_path)


if __name__ == '__main__':
    try:
        app = build_mac_app()
        
        # Optionally create DMG
        # create_dmg(app)
        
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
