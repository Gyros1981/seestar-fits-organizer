# Mac Port Progress Tracker

## Overview
Porting Seestar FITS Organizer from Windows to macOS.

---

## Phase 1: Platform Detection & Paths ✅

### 1.1 Create Platform Utility Module ✅
- [x] Create `core/platform_utils.py`
- [x] Implement `get_platform()` function
- [x] Implement `get_settings_dir()` for Windows
- [x] Implement `get_settings_dir()` for macOS
- [x] Implement `get_logs_dir()` for both platforms
- [x] Add `get_bundle_resource_path()` for bundled apps
- [x] Add platform detection constants (IS_WINDOWS, IS_MACOS, IS_LINUX)

### 1.2 Update AppSettings ✅
- [x] Modify `app_settings.py` to use platform-aware paths
- [x] Ensure Mac uses `~/Library/Application Support/SeestarFITS/`
- [x] Import and use `get_settings_dir()` from platform_utils

### 1.3 Update Logging ✅
- [x] Update `main.py` to use platform-aware logs directory
- [x] Add file logging alongside console logging
- [x] Log file location is now platform-appropriate:
  - Windows: `%APPDATA%\SeestarFITS\logs\app.log`
  - macOS: `~/Library/Logs/SeestarFITS/app.log`
  - Linux: `~/.local/share/SeestarFITS/logs/app.log`

**Phase 1 Status:** Code Complete ✅  
**Next:** Move to Phase 2 - UI Adjustments

---

## Phase 2: UI Adjustments

### 2.1 Menu Bar Adaptation ✅
- [x] Import `IS_MACOS` from platform_utils in main.py
- [x] Conditionally hide Exit button on Mac (Mac uses Cmd+Q instead)
- [x] Keep all other menu buttons for both platforms

### 2.2 Window & Layout
- [ ] Adjust default window size for Mac if needed
- [ ] Test DPI/scaling differences
- [ ] Fix any layout issues on Mac

**Status:** In Progress  
**Next:** Test UI on both platforms

---

## Phase 3: Platform-Specific Code Review

### 3.1 Path Handling
- [ ] Search for hardcoded backslashes (`\`)
- [ ] Verify all paths use `pathlib.Path`
- [ ] Test file operations on APFS (Mac) and NTFS (Windows)

### 3.2 File Dialogs
- [ ] Test `filedialog.askdirectory()` on Mac
- [ ] Verify native picker appearance
- [ ] Test file selection functionality

### 3.3 Other Platform Differences
- [ ] Check for Windows-specific imports
- [ ] Verify `tkinter` behavior on Mac
- [ ] Test keyboard shortcuts (Ctrl vs Cmd)

**Status:** Not Started  
**Estimated Time:** 2-3 hours

---

## Phase 4: Build Configuration ✅

### 4.1 PyInstaller Build Script ✅
- [x] Create `scripts/build_mac.py` - Automated build script
- [x] Configure `.app` bundle settings (bundle identifier, windowed mode)
- [x] Add data files (core, ui, docs)
- [x] Hidden imports for PIL, customtkinter, astropy, numpy
- [x] Test build process (documented)

### 4.2 Build Documentation ✅
- [x] Create `docs/mac-build-guide.md`
- [x] Document prerequisites (Python, dependencies)
- [x] Document quick build method
- [x] Document manual build (fallback)
- [x] Troubleshooting section
- [x] Tester instructions

### 4.3 Code Signing (Future Enhancement)
- [ ] Research Apple Developer requirements
- [ ] Document code signing steps
- [ ] Test notarization process (if applicable)

**Status:** Code Complete ✅  
**Ready for:** Building on Mac and testing

---

## Phase 5: Testing & Documentation

### 5.1 Testing
- [ ] Test all import workflows on Mac
- [ ] Test FITS Viewer on Mac
- [ ] Test Project Analyzer on Mac
- [ ] Test Settings save/load on Mac
- [ ] Regression test on Windows

### 5.2 Documentation
- [ ] Create Mac installation instructions
- [ ] Update README with Mac support
- [ ] Document any Mac-specific differences

**Status:** Not Started  
**Estimated Time:** 2-3 hours

---

## Current Status Summary

| Phase | Status | Completion |
|-------|--------|------------|
| 1. Platform & Paths | In Progress | 0% |
| 2. UI Adjustments | Not Started | 0% |
| 3. Code Review | Not Started | 0% |
| 4. Build Config | Not Started | 0% |
| 5. Testing & Docs | Not Started | 0% |

**Overall Progress:** 0%  
**Next Action:** Create platform_utils.py

---

## Notes

- Branch: `mac`
- Priority: Platform detection and paths first
- Keep Windows compatibility throughout
