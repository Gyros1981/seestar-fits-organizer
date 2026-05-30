# Workflow: Direct Copy (Raw → Projects)

## Purpose
Directly copy FITS files from your Seestar's Raw export folders into organized Projects with automatic classification (lights, darks, flats, biases).

---

## Step 1: Access the Workflow

**[SCREENSHOT: Application with menu bar visible]**

1. Click **📥 Import** menu button

**[SCREENSHOT: Import dropdown menu showing 3 options]**

2. Select **"Direct Copy (Raw → Projects)"**

**[ARROW: Point to "Direct Copy" option in dropdown]**

---

## Step 2: Direct Copy View

**[SCREENSHOT: Direct Copy view showing title, explanation text, and directory selection areas]**

The view shows:
- **Header**: "Direct Copy" 
- **Explanation**: "Copy FITS files directly from Raw folders to Projects..."
- **Raw Directory**: Select your Seestar export folder
- **Projects Directory**: Where organized projects will be created

---

## Step 3: Select Directories

### Select Raw Directory

**[SCREENSHOT: Direct Copy view with focus on Raw Directory section]**

**[ARROW: Point to "📁 Browse" button next to Raw Directory]**

1. Click **Browse** button next to "Raw Directory"

**[SCREENSHOT: File browser dialog opened to Seestar export folder]**

2. Navigate to your Seestar export folder (contains folders like `m3_subs`, `m27_subs`)

**[ARROW: Point to folder containing _subs folders]**

3. Click **Select Folder**

**[SCREENSHOT: Returned to Direct Copy view with path now showing in Raw Directory label]**

**[ARROW: Point to path text now displayed]** Path now shows selected location.

### Select Projects Directory

**[SCREENSHOT: Direct Copy view with focus on Projects Directory section]**

**[ARROW: Point to "📁 Browse" button next to Projects Directory]**

4. Click **Browse** button next to "Projects Directory"

**[SCREENSHOT: File browser dialog for selecting Projects folder]**

5. Navigate to where you want organized projects stored

**[ARROW: Point to destination folder]**

6. Click **Select Folder**

**[SCREENSHOT: Both directories now selected, Start Scan button active/enabled]**

---

## Step 4: Scan & Build

**[SCREENSHOT: Both directories selected, Start Scan button ready]**

**[ARROW: Point to orange "Start Scan & Build Projects" button]**

1. Click **Start Scan & Build Projects** button

**[SCREENSHOT: Scan in progress - showing progress bar and console output]**

The app will:
- Scan all `*_subs` folders in Raw directory
- Parse FITS metadata
- Classify files (LIGHT, DARK, FLAT, BIAS)
- Create project structure
- Copy files to correct folders

**[ARROW: Point to progress indicators]** Shows current operation and progress.

**[SCREENSHOT: Completion state - showing summary and success message]**

**[ARROW: Point to summary statistics]** Shows frame counts per project.

---

## Step 5: Verify Results

**[SCREENSHOT: File explorer showing created project folder structure]**

Projects are created as:
```
Projects/
  M3_Project/
    lights/
    darks/
    biases/
    flats/
  M27_Project/
    lights/
    ...
```

**[ARROW: Point to lights folder]** Contains all light frames.

**[ARROW: Point to darks folder]** Contains matching dark frames.

---

## Tips

- Original Raw files are **never modified or deleted**
- Only copies are made to Projects folder
- Each `*_subs` folder becomes a separate project
- Integration time is calculated from FITS metadata

---

## Common Issues

**Issue**: No files found
- Ensure Raw folder contains subfolders ending in `_subs`
- Verify files have `.fits` or `.fit` extension

**Issue**: Files not classified correctly
- Check that FITS files have proper `IMAGETYP` header
- Files without headers use filename heuristics
