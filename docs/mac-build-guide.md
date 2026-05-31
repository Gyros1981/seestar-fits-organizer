# Mac Build Guide

**How to build the Seestar FITS Organizer .app for macOS**

---

## Prerequisites

### You Need:
1. **A Mac computer** (macOS 10.14 or later)
2. **Python 3.9 or later** installed
3. **This source code** (the `mac` branch)

### Install Python Dependencies

Open Terminal and run:

```bash
cd /path/to/Seestar\ Processing

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller (for building the app)
pip install pyinstaller
```

---

## Quick Build (Simplest Method)

### Step 1: Run the Build Script

```bash
cd /path/to/Seestar\ Processing
python scripts/build_mac.py
```

This creates: `dist/SeestarFITSOrganizer.app`

### Step 2: Test the App

```bash
open dist/SeestarFITSOrganizer.app
```

### Step 3: Prepare for Distribution

**Option A: Zip (Easiest)**
```bash
cd dist
zip -r SeestarFITSOrganizer.zip SeestarFITSOrganizer.app
```

Send the `.zip` file to your tester.

**Option B: DMG (More Professional)**
```bash
# Install create-dmg (one time only)
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Seestar FITS Organizer" \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 450 185 \
  SeestarFITSOrganizer.dmg \
  dist/SeestarFITSOrganizer.app
```

---

## Manual Build (If Script Fails)

If the build script doesn't work, run PyInstaller directly:

```bash
pyinstaller \
  --name SeestarFITSOrganizer \
  --windowed \
  --onefile \
  --clean \
  --noconfirm \
  --osx-bundle-identifier com.guyronen.seestar-fits-organizer \
  --add-data "core:core" \
  --add-data "ui:ui" \
  --add-data "docs:docs" \
  --hidden-import PIL \
  --hidden-import customtkinter \
  --hidden-import astropy \
  --hidden-import numpy \
  main.py
```

---

## Troubleshooting Build Issues

### Issue: "Module not found" errors

**Solution:** Add missing modules to the build command:

```bash
pyinstaller ... --hidden-import MODULE_NAME main.py
```

### Issue: App won't open ("Unidentified Developer")

**This is expected!** macOS shows a security warning for apps not signed with an Apple Developer certificate.

**Tester Workaround:**
1. Right-click the .app
2. Select "Open"
3. Click "Open" in the security dialog

**OR in Terminal:**
```bash
xattr -cr /path/to/SeestarFITSOrganizer.app
open /path/to/SeestarFITSOrganizer.app
```

### Issue: Missing data files (docs, images not showing)

Check that `--add-data` paths are correct. The format is:
```
--add-data "source_path:destination_path"
```

On Mac, use colon `:` as separator (not semicolon `;` like Windows).

---

## For Your Tester

When you send the .app to someone:

### What to Send:
- `SeestarFITSOrganizer.app` folder (zipped)

### Instructions for Tester:

1. **Download and unzip** the file
2. **Right-click** the .app → **Open** (Don't double-click!)
3. **Click "Open"** in the security dialog
4. The app should launch

### What to Test:
1. ✅ App opens without crashing
2. ✅ Menu bar shows (🏠, 📥, 🔧, ⚙️, ❓)
3. ✅ Settings saves to right location (`~/Library/Application Support/SeestarFITS/`)
4. ✅ Logs created in `~/Library/Logs/SeestarFITS/`
5. ✅ Import workflows work
6. ✅ FITS Viewer works
7. ✅ Project Analyzer works

---

## Build Checklist

Before sending to tester:

- [ ] Build succeeds without errors
- [ ] App launches on your Mac
- [ ] All menu buttons visible and working
- [ ] Settings can be saved and loaded
- [ ] Can browse for directories
- [ ] No crash on basic operations

---

## Known Limitations

1. **No Code Signing**: Testers will see "Unidentified Developer" warning
   - They need to right-click → Open
   - Or run `xattr -cr` command

2. **No Notarization**: Apple may block on newer macOS versions
   - Workaround: Disable Gatekeeper for this app only

3. **Intel vs Apple Silicon**:
   - Build on Intel Mac = runs on Intel and Rosetta 2 (Apple Silicon)
   - Build on Apple Silicon = runs on Apple Silicon only
   - For universal build, more complex setup needed

---

## Code Signing (Advanced - Optional)

If you want to distribute without security warnings, you need:
1. Apple Developer account ($99/year)
2. Code signing certificate
3. Notarization through Apple

This is NOT required for testing with friends.

---

## Next Steps After Testing

Once your tester confirms everything works:

1. Merge `mac` branch to `main`
2. Create GitHub release with Mac download
3. Consider Apple Developer account for signed releases

---

**Questions?** Check the troubleshooting section or review PyInstaller docs:
https://pyinstaller.readthedocs.io/
