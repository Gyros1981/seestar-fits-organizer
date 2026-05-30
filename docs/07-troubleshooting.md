# Troubleshooting Guide

## Common Issues and Solutions

---

## Import Issues

### Issue: "No files found" during scan

**[SCREENSHOT: Error or warning message "No FITS files found"]**

**[ARROW: Point to message]**

**Possible Causes:**
1. Wrong folder selected
2. Files don't have `.fits` or `.fit` extension
3. No `*_subs` folders present

**Solutions:**

**[SCREENSHOT: File explorer showing correct folder structure]**

1. Verify Raw directory contains subfolders ending in `_subs`
2. Check that FITS files have `.fits` or `.fit` extension (not `.txt`, `.jpg`, etc.)
3. Ensure files are in subfolders, not root of Raw directory

```
✅ Correct:
Raw/
  m3_subs/
    image001.fits
    image002.fits

❌ Incorrect:
Raw/
  image001.fits  ← Files in root won't be found
```

---

### Issue: Files not classified correctly

**[SCREENSHOT: Project showing all files in lights folder when some should be darks]**

**[ARROW: Point to wrong classification]**

**Cause:** Missing or incorrect `IMAGETYP` header in FITS files

**Solution:**

The app classifies in this priority:
1. `IMAGETYP` FITS header (preferred)
2. Filename keywords (e.g., `dark`, `flat`, `bias`)
3. Exposure heuristics (short exposures = bias, etc.)

**[SCREENSHOT: FITS header viewer showing IMAGETYP field]**

If Seestar didn't write proper headers, you may need to:
- Rename files to include type keywords
- Use external tool to fix headers
- Manually sort files after import

---

### Issue: Planetary & Scenery "No media files found"

**[SCREENSHOT: Planetary import showing no files found]**

**[ARROW: Point to message]**

**Cause:** Folder names don't match expected pattern

**Solution:**

Verify folder names match **exactly**:
- `Planetary_video` (not `Planetary videos` or `planetary_video`)
- `Planetary_photo`
- `Solar_video`
- `Solar_photo`
- `Lunar_video`
- `Lunar_photo`
- `Scenery_video`
- `Scenery_photo`

**[SCREENSHOT: File explorer showing correct folder names]**

**[ARROW: Point to each correctly named folder]**

Also check file extensions:
- Videos: `.mp4`, `.mov`, `.avi`
- Photos: `.jpg`, `.jpeg`, `.png`

---

## FITS Viewer Issues

### Issue: Images not displaying

**[SCREENSHOT: FITS Viewer showing "Error loading preview"]**

**[ARROW: Point to error message]**

**Possible Causes:**
1. Corrupt FITS file
2. Unsupported data format
3. Memory issue with very large files

**Solutions:**
1. Try different file to isolate issue
2. Check file opens in other FITS software
3. For very large files (50MB+), zoom out to reduce memory

**[SCREENSHOT: FITS Viewer at lower zoom showing large file]**

---

### Issue: Zoom buttons not working

**[SCREENSHOT: Zoom buttons at limits (disabled state)]**

**[ARROW: Point to disabled buttons]**

**Cause:** You've reached zoom limits

- **Min zoom**: 30% (0.3x)
- **Max zoom**: 250% (2.5x)

**Solution:**
Click the opposite direction or click percentage label to enter custom value.

---

### Issue: Navigation not working

**[SCREENSHOT: Previous/Next buttons disabled]**

**[ARROW: Point to disabled navigation buttons]**

**Cause:** 
- At first file (Previous disabled)
- At last file (Next disabled)
- No directory loaded

**Solution:**
Load a directory with multiple FITS files first.

---

## Project Analyzer Issues

### Issue: No projects found

**[SCREENSHOT: Analyzer showing "Select Projects Directory" with no projects]**

**[ARROW: Point to empty project list]**

**Causes:**
1. Wrong folder selected
2. Projects don't have proper structure
3. No `lights` folder in projects

**Solution:**

**[SCREENSHOT: Correct project folder structure]**

Verify structure:
```
Projects/
  M3_Project/
    lights/     ← Required folder
    darks/      ← Optional
    flats/      ← Optional
    biases/     ← Optional
```

**[ARROW: Point to lights folder]** This folder must exist.

---

### Issue: Integration time showing 0

**[SCREENSHOT: Project showing "Integration: 0s"]**

**[ARROW: Point to zero integration time]**

**Cause:** FITS files missing `EXPTIME` header

**Solution:**
Integration time is calculated from `EXPTIME` FITS header. If missing:
- Time shows as 0
- App continues normally
- Check files with FITS header viewer

---

### Issue: Coordinates not showing

**[SCREENSHOT: Project details with RA/DEC blank or "N/A"]**

**[ARROW: Point to missing coordinate fields]**

**Cause:** Missing `RA` and `DEC` FITS headers

**Solution:**
Coordinates are extracted from FITS metadata. Some Seestar exports may not include this. Use the object's name for identification instead.

---

## Settings Issues

### Issue: Text scale not applying immediately

**[SCREENSHOT: Settings showing Large selected but UI still normal size]**

**Cause:** Text scale requires app restart

**Solution:**
1. Save settings
2. Close application completely
3. Reopen application

**[SCREENSHOT: App at larger text scale after restart]**

---

### Issue: Timezone not saving

**[SCREENSHOT: Settings showing UTC but displaying times differently]**

**[ARROW: Point to timezone dropdown]**

**Solution:**
1. Ensure you click **Save Settings** button
2. Check `core/app_settings.json` was updated
3. Restart app if issues persist

---

### Issue: Settings file corrupt

**[SCREENSHOT: Error message about settings file]**

**Solution:**
Delete `core/app_settings.json` and restart app:
1. Close application
2. Navigate to `Seestar Processing/core/`
3. Delete `app_settings.json`
4. Restart application

Settings will reset to defaults.

---

## Performance Issues

### Issue: App slow with large folders

**[SCREENSHOT: App with progress bar showing slow operation]**

**Solution:**
- Wait for operations to complete (don't click multiple times)
- Close other applications to free memory
- For 1000+ files, consider working in smaller batches

---

### Issue: FITS Viewer slow with large images

**[SCREENSHOT: Large FITS file loading slowly]**

**Solution:**
- Large files (50MB+) take longer to load
- Use lower zoom to reduce memory usage
- Consider using external viewer for very large files

---

## Menu/Navigation Issues

### Issue: Menu buttons not visible

**[SCREENSHOT: App with missing menu bar]**

**Solution:**
Resize window to be wider (minimum ~900px recommended).

---

### Issue: Can't get back to home/landing page

**[SCREENSHOT: Any tool view with no obvious back button]**

**Solution:**
Click **🏠 Home** button in menu bar to return to landing page.

**[ARROW: Point to Home button]**

---

## General Solutions

### Restart Application
Many issues resolve with a restart:
1. Close app
2. Wait 5 seconds
3. Reopen

### Check Log Files
View detailed error information:
- Log file location: `logs/` folder
- Look for recent errors

### Update Application
Ensure you're using latest version:
- Check About dialog for version number
- Update if available

---

## Getting Help

If issues persist:
1. Check this troubleshooting guide
2. Review workflow documentation
3. Check logs for error details
4. Verify file/folder structure
5. Try with a small test set first
