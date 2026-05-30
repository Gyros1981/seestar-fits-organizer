# Tool: FITS Viewer

## Purpose
Browse, preview, and manage FITS files with keyboard navigation, zoom controls, and marking for deletion.

---

## Accessing FITS Viewer

**[SCREENSHOT: Tools menu dropdown showing FITS Viewer option]**

**[ARROW: Point to "FITS Viewer" in Tools menu]**

1. Click **🔧 Tools** menu
2. Select **"FITS Viewer"**

---

## FITS Viewer Layout

**[SCREENSHOT: Full FITS Viewer window with all components labeled]**

### Layout Overview:
- **Left Panel**: File list with navigation buttons
- **Right Panel**: Image preview with zoom controls
- **Top**: Directory selection and action buttons

**[ARROW: Point to left panel - file list]** Shows all FITS files in directory.

**[ARROW: Point to right panel - preview]** Shows selected image.

**[ARROW: Point to top action bar]** Browse, Mark, Clear, Delete controls.

---

## Step 1: Select Directory

**[SCREENSHOT: FITS Viewer with "No directory selected" label]**

**[ARROW: Point to "📁 Browse" button]**

1. Click **Browse** button

**[SCREENSHOT: File browser dialog]**

2. Navigate to folder containing FITS files

**[ARROW: Point to folder with .fits files]**

3. Select folder and click OK

**[SCREENSHOT: FITS Viewer loaded with file list populated]**

**[ARROW: Point to file list]** All FITS files now listed.

**[ARROW: Point to status bar]** Shows "X FITS files found".

---

## File List Panel (Left)

**[SCREENSHOT: Left panel showing file list with marked files]**

### Features:
- Files marked with `[ ]` = unmarked
- Files marked with `[✓]` = marked for deletion
- Click to select and preview

**[ARROW: Point to marked file with [✓]]** This file is marked for deletion.

**[ARROW: Point to unmarked file with [ ]]** This file is not marked.

---

## Navigation Buttons (Below File List)

**[SCREENSHOT: Navigation buttons below file list]**

**[ARROW: Point to "◀ Previous" button]** Go to previous file.

**[ARROW: Point to "Next ▶" button]** Go to next file.

Buttons auto-disable at first/last file.

**[SCREENSHOT: Previous button disabled at first file]**

**[ARROW: Point to disabled Previous button]** Grayed out - can't go back.

---

## Keyboard Navigation

**[SCREENSHOT: FITS Viewer with annotation showing keyboard shortcuts]**

- **↑ Up Arrow** = Previous file
- **↓ Down Arrow** = Next file

**[ARROW: Draw arrow from keyboard to file list]** Same as clicking Previous/Next.

---

## Preview Panel (Right)

**[SCREENSHOT: Preview panel showing FITS image]**

Shows selected FITS image with:
- Filename at top
- Scaled image
- Zoom controls on right edge

**[ARROW: Point to filename label]** Shows current file name.

**[ARROW: Point to image]** Auto-stretched for visibility.

---

## Zoom Controls (Right Edge)

**[SCREENSHOT: Zoom control buttons on right side]**

**[ARROW: Point to "+" button]** Zoom in (max 250%).

**[ARROW: Point to zoom percentage "100%"]** Click to enter custom zoom.

**[ARROW: Point to "−" button]** Zoom out (min 30%).

---

## Using Zoom

### Step-by-Step:

**[SCREENSHOT: Zoom at 100% - normal size]**

1. Click **+** to zoom in

**[SCREENSHOT: Zoom at 125% - image larger]**

2. Continue clicking **+** to increase zoom

**[SCREENSHOT: Zoom at 250% - maximum zoom, + button disabled]**

**[ARROW: Point to disabled + button]** Maximum zoom reached (250%).

3. Click **−** to zoom out

**[SCREENSHOT: Zoom at 30% - minimum zoom, − button disabled]**

**[ARROW: Point to disabled − button]** Minimum zoom reached (30%).

---

## Custom Zoom Input

**[SCREENSHOT: Clicking on zoom percentage label]**

1. Click on zoom percentage text (e.g., "100%")

**[SCREENSHOT: Zoom input dialog opened]**

**[ARROW: Point to text field]** Enter zoom percentage.

**[ARROW: Point to "Range: 30% - 250%" text]** Valid range.

2. Type desired percentage (e.g., 150)
3. Press **Enter** or click **OK**

**[SCREENSHOT: Image now at 150% zoom]**

---

## Marking Files for Deletion

### Mark Single File:

**[SCREENSHOT: File selected in list]**

**[ARROW: Point to "✓ Mark" button]**

1. Select file in list
2. Click **Mark** button

**[SCREENSHOT: Same file now showing [✓] in list]**

File is now marked for deletion.

### Clear All Marks:

**[ARROW: Point to "⬜ Clear Marks" button]**

Click to unmark all files.

### Delete Marked Files:

**[ARROW: Point to "🗑️ Delete Marked" button]**

**⚠️ WARNING: This permanently deletes files!**

**[SCREENSHOT: Confirmation dialog before deletion]**

1. Click **Delete Marked**
2. Confirm in dialog
3. Marked files are permanently removed

---

## Summary Controls

**[SCREENSHOT: Top control bar with all buttons labeled]**

| Button | Function |
|--------|----------|
| 📁 Browse | Select new directory |
| ✓ Mark | Mark selected file for deletion |
| ⬜ Clear Marks | Unmark all files |
| 🗑️ Delete Marked | Permanently delete marked files |

---

## Tips

- Zoom level resets when changing directories
- Marked files show `[✓]` in list
- Use keyboard arrows for quick browsing
- Images are auto-stretched for visibility

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑ | Previous file |
| ↓ | Next file |

---

## Zoom Limits

- **Minimum**: 30% (0.3x)
- **Maximum**: 250% (2.5x)
- **Step size**: 25% per button click
