# About Seestar FITS Organizer

## What is Seestar FITS Organizer?

Seestar FITS Organizer is a Windows desktop application designed specifically for astrophotographers using the Seestar S50 smart telescope. It helps you organize, manage, and understand your astronomical imaging data with an intuitive, user-friendly interface.

---

## The Challenge

When you use your Seestar telescope, it generates a lot of data:

- **Deep-sky FITS files** from your nebula and galaxy imaging sessions
- **Planetary videos** of Jupiter, Saturn, Mars, and the Moon
- **Solar captures** with your solar filter
- **Scenery photos** from your imaging location
- **Calibration frames** (darks, flats, biases) for image processing

Over time, this data becomes scattered across folders, mixed together, and difficult to manage. Finding that perfect session from three months ago becomes a chore. Understanding your total integration time requires manual calculations. And preparing data for processing in tools like Siril or PixInsight means hours of manual file sorting.

---

## The Solution

Seestar FITS Organizer solves these problems by automatically:

### 1. Organizing Your Data

The app reads metadata directly from your FITS files and sorts them into clean, structured project folders:

```
M42_Project/
  lights/       <- All your light frames
  darks/        <- Matching dark frames
  flats/        <- Flat calibration frames
  biases/       <- Bias calibration frames
```

No manual sorting. No renaming files. Just point the app at your Seestar export folder and let it do the work.

### 2. Preserving Your Original Data

**Important:** The app never modifies or deletes your original files. It only copies them to the organized structure. Your source data remains untouched and safe.

### 3. Extracting Metadata

Every FITS file contains valuable information in its header:

- **EXPTIME** - How long each exposure was
- **DATE-OBS** - When you captured it
- **OBJECT** - What target you were imaging
- **RA/DEC** - Where in the sky you pointed
- **FILTER** - Which filter was used

The app extracts all of this automatically and uses it to:
- Calculate total integration time
- Group sessions by date and location
- Identify your imaging targets
- Show coordinates in your preferred format

### 4. Supporting Multiple Workflows

Whether you're a casual imager or a serious astrophotographer, the app adapts to your needs:

- **Direct Copy** for quick, simple organization
- **Intermediate Copy** when you want to review files first
- **Planetary & Scenery** for your non-deep-sky captures

---

## Key Features

### Smart Import Workflows

**Direct Copy (Raw → Projects)**
The fastest way to organize your data. Select your Seestar export folder, select your Projects folder, and click Start. The app handles everything else.

**Intermediate Copy (Raw → Processing → Projects)**
For when you want an extra step. Files are first copied to an intermediate folder where you can review, cull, or pre-process before final organization.

**Planetary & Scenery (Media Files)**
Seestar captures more than deep-sky objects. This workflow organizes your planetary videos, lunar photos, solar captures, and scenery shots into dedicated folders.

### FITS Viewer

Browse and preview your FITS files without opening a heavy image processing application:

- **Keyboard navigation** with arrow keys
- **Zoom controls** from 30% to 250%
- **Custom zoom input** for precise control
- **Mark for deletion** to clean up bad frames
- **Batch deletion** of marked files

The auto-stretch preview makes faint details visible without complex processing.

### Project Analyzer

Understand your imaging sessions at a glance:

- **Integration time calculation** - Total hours of exposure per project
- **Frame counts** - Lights, darks, flats, biases
- **Session grouping** - Automatic grouping by capture time
- **Location tagging** - Group by capture site
- **Filter breakdown** - See which filters you used
- **Sky atlas integration** - Open your target in Aladin Lite
- **CSV export** - Export all data to spreadsheet

### Flexible Settings

Customize the app to match your preferences:

- **Timezone display** - UTC, PST, EST, or Local time
- **Coordinate format** - Decimal degrees or traditional HMS/DMS
- **Text scale** - Small to Extra Large for accessibility
- **Location threshold** - Control how sites are grouped

---

## Who Is This For?

### Beginners

Just getting started with astrophotography? The app helps you:
- Understand what all those files mean
- Keep your data organized from day one
- Learn about calibration frames (darks, flats, biases)
- Track your progress over time

### Intermediate Imagers

Already comfortable with your Seestar? Use the app to:
- Quickly organize multiple nights of data
- Review and cull bad frames before processing
- Track your integration time across sessions
- Prepare clean datasets for stacking

### Advanced Users

Deep into astrophotography workflows? The app provides:
- Batch organization of large datasets
- Detailed metadata extraction
- Location-based session grouping
- CSV export for custom analysis

---

## Design Philosophy

### Safety First

Your data is irreplaceable. That's why the app:
- Never modifies source files
- Never deletes without explicit marking
- Creates copies, never moves originals
- Maintains your Raw folder exactly as exported

### Non-Destructive

Everything the app does can be undone or redone:
- Delete a project? Your source files remain.
- Reset settings? Just change them back.
- Wrong organization? Run the import again.

### Transparency

The app tells you what it's doing:
- Progress bars show scan status
- Console output explains each step
- File counts show what was found
- Errors are logged and displayed

### Accessibility

Astrophotography is for everyone:
- Adjustable text scale (0.8x to 1.4x)
- Keyboard navigation support
- Clear, simple interface
- No technical knowledge required

---

## What It Doesn't Do

Understanding the app's limitations helps set expectations:

### No Image Processing

The app organizes your data. It does not:
- Stack your images
- Calibrate your frames
- Process your data
- Generate final images

Use Siril, PixInsight, DeepSkyStacker, or your preferred processing software for that.

### No Automatic Quality Scoring

The app doesn't analyze image quality:
- No FWHM measurement
- No star detection
- No SNR calculation
- No automatic frame rejection

Use the FITS Viewer to visually inspect and mark frames manually.

### No Cloud Sync

The app works locally on your computer:
- No automatic cloud backup
- No multi-device synchronization
- No online storage

Your data stays on your machine, under your control.

---

## Getting Started

The fastest way to begin:

1. Export data from your Seestar
2. Open Seestar FITS Organizer
3. Click Import → Direct Copy
4. Select your Seestar export folder
5. Select where you want Projects created
6. Click Start Scan & Build Projects

Within minutes, you'll have organized projects ready for processing.

---

## About the Developer

Seestar FITS Organizer was created by Guy Ronen, an astrophotography enthusiast who wanted a simpler way to manage Seestar data. The app is built with feedback from the astrophotography community and continues to evolve based on user needs.

---

## Version Information

- **Current Version**: 1.3.3
- **Platform**: Windows
- **Requirements**: Windows 10 or later, Seestar S50 export data

---

## Next Steps

Ready to learn more? Explore the detailed guides:

1. **Import Workflows** - Step-by-step guides for each import type
2. **Tools Guide** - Deep dive into FITS Viewer and Project Analyzer
3. **Settings Reference** - Understand every option
4. **Troubleshooting** - Solve common issues

Or jump right in with the **Quick Reference Card** for the essentials at a glance.

---

*Happy imaging, and clear skies!*
