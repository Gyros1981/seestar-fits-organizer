# Tool: Project Analyzer

## Purpose
View detailed statistics and metadata for your astrophotography projects including:
- Integration time calculations
- Frame counts (lights, darks, flats, biases)
- Exposure breakdown
- Session timeline
- Object information (RA/DEC, constellation)

---

## Accessing Project Analyzer

**[SCREENSHOT: Tools menu dropdown]**

**[ARROW: Point to "Project Analyzer" option]**

1. Click **🔧 Tools** menu
2. Select **"Project Analyzer"**

---

## Project Analyzer Layout

**[SCREENSHOT: Full Project Analyzer window with sections labeled]**

### Layout:
- **Top**: Search and export controls
- **Left Panel**: Project list
- **Right Panel**: Detailed information
  - Summary section
  - Sessions section (expandable)

**[ARROW: Point to search box]** Filter projects by name.

**[ARROW: Point to project list]** All discovered projects.

**[ARROW: Point to right panel details]** Shows project statistics.

---

## Step 1: Select Projects Directory

**[SCREENSHOT: Analyzer showing "Select Projects Directory" button]**

**[ARROW: Point to "📁 Select Projects Directory" button]**

1. Click **Select Projects Directory** button

**[SCREENSHOT: File browser dialog]**

2. Navigate to your Projects folder

**[ARROW: Point to Projects folder]**

3. Select folder and click OK

**[SCREENSHOT: Projects loaded with list of projects]**

Projects are automatically scanned and listed.

**[ARROW: Point to project count]** Shows number of projects found.

---

## Project List (Left Panel)

**[SCREENSHOT: Left panel showing multiple projects]**

Shows all projects with:
- Project name
- Object name (if extracted from metadata)

**[ARROW: Point to project name]** Click to view details.

**[ARROW: Point to object name]** Parsed from FITS headers.

---

## Search Function

**[SCREENSHOT: Search box with text entered]**

**[ARROW: Point to search field]**

1. Type in search box
2. Project list filters automatically

**[SCREENSHOT: Filtered list showing only matching projects]**

**[ARROW: Point to filtered results]** Only matching projects shown.

---

## Project Details (Right Panel)

**[SCREENSHOT: Right panel showing selected project details]**

### Summary Section:

**[ARROW: Point to object name]** Target object.

**[ARROW: Point to RA/DEC coordinates]** Right Ascension and Declination.

**[ARROW: Point to frame counts]** Lights, Darks, Flats, Biases.

**[ARROW: Point to integration time]** Total exposure time calculated.

**[ARROW: Point to filters used]** Filter wheel positions detected.

---

## Integration Time Display

**[SCREENSHOT: Project showing integration time breakdown]**

Shows in multiple formats:
- Hours / Minutes / Seconds (e.g., "2h 30m 0s")
- Total seconds

**[ARROW: Point to formatted time]** Human-readable format.

**[ARROW: Point to exposure breakdown]** Per-exposure-time counts.

---

## Sessions Section (Expandable)

**[SCREENSHOT: Sessions section collapsed with arrow]**

**[ARROW: Point to dropdown arrow / expand button]**

1. Click to expand Sessions section

**[SCREENSHOT: Sessions section expanded showing multiple sessions]**

Shows capture sessions grouped by time:
- Date/time range
- Number of lights in session
- Location (if coordinates available)
- Individual frame list

**[ARROW: Point to session header]** Date/time of session.

**[ARROW: Point to session details]** Lights count and duration.

---

## Session Details

**[SCREENSHOT: Expanded session showing individual frames]**

**[ARROW: Point to start/end time]** Session duration.

**[ARROW: Point to location info]** Capture site coordinates.

**[ARROW: Point to object info]** RA/DEC for this session.

**[ARROW: Point to individual captures list]** All frames in session.

---

## Sky Atlas Integration

**[SCREENSHOT: Session with "Open in Sky Atlas" button visible]**

**[ARROW: Point to "🌌 Open in Sky Atlas" button]**

Click to open Aladin Lite web viewer centered on object coordinates.

**[SCREENSHOT: Browser showing Aladin Lite with object centered]**

Opens in default web browser with DSS2 colored survey.

---

## Image Preview

**[SCREENSHOT: Session with "Preview Image" button]**

**[ARROW: Point to "🖼️ Preview Image" button]**

Click to preview first light frame from this session.

**[SCREENSHOT: Preview window showing FITS image]**

Shows auto-stretched FITS preview.

---

## Export to CSV

**[SCREENSHOT: Top bar showing "Export to CSV" button]**

**[ARROW: Point to "Export to CSV" button]**

1. Click **Export to CSV**

**[SCREENSHOT: Save dialog for CSV file]**

2. Choose save location
3. Click Save

**[SCREENSHOT: CSV file opened in Excel/spreadsheet]**

Exports all project data to spreadsheet format:
- Project names
- Object names
- Frame counts
- Integration times
- RA/DEC coordinates
- Dates

---

## Accordion Behavior

**[SCREENSHOT: Multiple sessions with one expanded]**

Click any session to expand/collapse it independently.

**[ARROW: Point to expanded session]** Currently viewing.

**[ARROW: Point to collapsed session]** Click to expand.

---

## Tips

- Projects are scanned recursively
- Metadata extracted from FITS headers
- Sessions auto-grouped by capture time gaps
- CSV export includes all project statistics
- Sky Atlas opens in external browser

---

## Data Sources

The analyzer reads:
- FITS headers (OBJECT, RA, DEC, DATE-OBS, EXPTIME, FILTER)
- File counts per folder type
- Timestamp for session grouping

**[SCREENSHOT: Example FITS metadata display]**

**[ARROW: Point to metadata fields]** Extracted from file headers.
