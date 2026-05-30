# Workflow: Planetary & Scenery Import

## Purpose
Copy media files (videos and photos) from your Seestar for:
- **Planetary** imaging (Jupiter, Saturn, Mars, etc.)
- **Solar** imaging (with solar filter)
- **Lunar** imaging (Moon)
- **Scenery** photos and videos

These are non-FITS media files organized into specific folder structures.

---

## Step 1: Access the Workflow

**[SCREENSHOT: Import menu dropdown]**

**[ARROW: Point to "Planetary & Scenery (Media Files)" option]**

1. Select **"Planetary & Scenery (Media Files)"** from Import menu

---

## Step 2: Planetary & Scenery View

**[SCREENSHOT: Planetary & Scenery view with title and explanation]**

The view shows:
- **Explanation**: Description of what this workflow handles
- **Source Directory**: Where your Seestar exports media
- **Destination Directory**: Where organized media goes
- **Action Button**: To start copying

**[ARROW: Point to explanation text]** Read this for important details.

---

## Step 3: Select Directories

### Select Source Directory

**[SCREENSHOT: Source directory selection area]**

**[ARROW: Point to Browse button]**

1. Click **Browse** and select Seestar export folder

This folder should contain subfolders like:
- `Planetary_video`
- `Planetary_photo`
- `Solar_video`
- `Solar_photo`
- `Lunar_video`
- `Lunar_photo`
- `Scenery_video`
- `Scenery_photo`

**[SCREENSHOT: Example Seestar export folder showing these subfolders]**

**[ARROW: Point to each recognized folder type]** App looks for these specific names.

### Select Destination Directory

**[SCREENSHOT: Destination selection area]**

**[ARROW: Point to Browse button for destination]**

2. Click **Browse** and select where organized media should go

**[SCREENSHOT: Both directories selected]**

---

## Step 4: Copy Media

**[SCREENSHOT: Ready to copy - both paths selected, action button visible]**

**[ARROW: Point to orange "Copy Planetary & Scenery Files" button]**

1. Click **Copy Planetary & Scenery Files** button

**[SCREENSHOT: Copy in progress showing progress bar and file counts]**

The app will:
- Scan for media folders
- Copy videos to `*_video` folders
- Copy photos to `*_photo` folders
- Show progress for each category

**[ARROW: Point to progress section]** Shows files being copied per category.

**[SCREENSHOT: Completion with summary of copied files]**

---

## Expected Output Structure

```
Destination/
  Planetary_video/
    *.mp4, *.mov files
  Planetary_photo/
    *.jpg, *.png files
  Solar_video/
  Solar_photo/
  Lunar_video/
  Lunar_photo/
  Scenery_video/
  Scenery_photo/
```

**[SCREENSHOT: File explorer showing this folder structure]**

**[ARROW: Point to video folder]** Video files organized here.

**[ARROW: Point to photo folder]** Photo files organized here.

---

## Supported File Types

| Category | Videos | Photos |
|----------|--------|--------|
| Planetary | .mp4, .mov, .avi | .jpg, .jpeg, .png |
| Solar | .mp4, .mov, .avi | .jpg, .jpeg, .png |
| Lunar | .mp4, .mov, .avi | .jpg, .jpeg, .png |
| Scenery | .mp4, .mov, .avi | .jpg, .jpeg, .png |

**[SCREENSHOT: Files of various types in source folder]**

---

## Tips

- Source files are **never deleted**
- Only copies are made to destination
- Folder structure is created automatically
- Existing files in destination are preserved

---

## Common Issues

**Issue**: No media files found
- Verify folder names match exactly: `Planetary_video`, `Planetary_photo`, etc.
- Check file extensions are supported

**Issue**: Wrong file types copied
- Ensure videos are in `*_video` folders
- Ensure photos are in `*_photo` folders
