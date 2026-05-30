# Workflow: Intermediate Copy (Raw → Processing → Projects)

## Purpose
Copy FITS files through an intermediate processing step. Use this when you need to:
- Manually review/cull frames before organizing
- Pre-process files in another tool
- Work with files from multiple nights before final organization

---

## Step 1: Access the Workflow

**[SCREENSHOT: Application with Import menu open]**

1. Click **📥 Import** menu button

**[SCREENSHOT: Import dropdown menu]**

**[ARROW: Point to "Intermediate Copy" option]**

2. Select **"Intermediate Copy (Raw → Processing → Projects)"**

---

## Step 2: Intermediate Copy View

**[SCREENSHOT: Intermediate Copy view showing 3 directory sections]**

The view shows three directory sections:
1. **Raw Directory** - Source Seestar exports
2. **Intermediate Directory** - Working/staging area
3. **Projects Directory** - Final organized location

**[ARROW: Point to Raw Directory section]** First, select source.

**[ARROW: Point to Intermediate Directory section]** Second, select staging area.

**[ARROW: Point to Projects Directory section]** Third, select final destination.

---

## Step 3: Select All Three Directories

### Select Raw Directory

**[SCREENSHOT: Focus on Raw Directory selection area]**

**[ARROW: Point to Browse button]**

1. Click **Browse** and select your Seestar export folder

### Select Intermediate Directory

**[SCREENSHOT: Focus on Intermediate Directory section]**

**[ARROW: Point to Browse button for Intermediate]**

2. Click **Browse** and select/create a staging folder

**[SCREENSHOT: Example: "Processing" or "Staging" folder selected]**

**[ARROW: Point to selected Intermediate path]** This is your working area.

### Select Projects Directory

**[SCREENSHOT: Focus on Projects Directory section]**

**[ARROW: Point to Browse button for Projects]**

3. Click **Browse** and select final Projects location

**[SCREENSHOT: All three directories selected]**

---

## Step 4: Start Transfer

**[SCREENSHOT: All 3 paths filled, Start Transfer button enabled]**

**[ARROW: Point to orange action button]**

1. Click **Start Scan & Transfer** button

**[SCREENSHOT: Transfer in progress]**

Process flow:
1. Scans Raw folder for `*_subs` directories
2. Copies files to Intermediate location
3. Organizes into Projects from Intermediate

**[ARROW: Point to progress bar]** Shows current stage.

**[ARROW: Point to console output]** Shows detailed operations.

**[SCREENSHOT: Completion with summary]**

---

## Workflow Differences from Direct Copy

| Feature | Direct Copy | Intermediate Copy |
|---------|-------------|-----------------|
| Stages | Raw → Projects | Raw → Intermediate → Projects |
| Use Case | Simple organization | Review/pre-processing needed |
| Speed | Faster | Slower (extra copy step) |

**[SCREENSHOT: Side-by-side comparison view (if possible) or just text table]**

---

## File Flow Diagram

```
Raw/m3_subs/*.fits
       ↓
Intermediate/m3_processing/
       ↓
Projects/M3_Project/
   ├── lights/
   ├── darks/
   ├── biases/
   └── flats/
```

**[SCREENSHOT: File explorer showing the 3-folder structure]**

---

## Tips

- Use Intermediate folder to temporarily store files
- Great for multi-night sessions before final organization
- Delete Intermediate folder contents after Projects are created to save space

---

## When to Use Intermediate vs Direct

**Use Intermediate when:**
- You want to review files before organizing
- Using external tools (Siril, PixInsight) before organization
- Combining data from multiple nights

**Use Direct when:**
- You trust the data and want quick organization
- You have a simple workflow
- You don't need intermediate processing
