# Seestar Astronomy Helper App — Agent Spec

## Overview
You are building a Windows desktop application that helps process astrophotography data from a Seestar telescope workflow.

The app:
- Ingests raw FITS files from Seestar exports
- Organizes them into structured astrophotography projects
- Extracts metadata from FITS headers
- Computes integration time and capture statistics
- Copies files safely (NO deletion or modification of source data)

This is a data organization + analytics tool, not an image processing tool.

---

## Core Folder Structure

### Input (Raw Data)
```
Raw/
  m3_subs/
  m27_subs/
```

Each folder represents a target object session group containing FITS files.

---

### Output (Projects)
```
Projects/
  M3_Project/
    lights/
    darks/
    biases/
    flats/
```

Mapping rule:
Raw/<object>_subs → Projects/<Object>_Project

Example:
m3_subs → M3_Project

---

## Core Rules (STRICT)

- NEVER delete or modify files in Raw/
- ONLY COPY files into Projects/
- All processing must be deterministic and repeatable
- FITS metadata is the primary source of truth
- System must handle missing or partial metadata gracefully
- Raw structure must remain unchanged

---

## FITS Metadata Extraction

Extract as much metadata as possible from each FITS file.

### Required fields (if available):
- EXPTIME (exposure time in seconds)
- DATE-OBS (capture timestamp)
- OBJECT
- IMAGETYP (LIGHT / DARK / FLAT / BIAS)
- FILTER
- GAIN / ISO
- CCD-TEMP or sensor temperature
- XBINNING / YBINNING

### Optional fields:
- RA / DEC
- FOCALLEN
- AIRMASS

If a field is missing:
- Do not fail
- Set value to null
- Log warning internally

---

## Frame Classification Logic

Each FITS file must be classified as:

- LIGHT
- DARK
- FLAT
- BIAS

Priority order:
1. IMAGETYP header (preferred)
2. Filename keywords
3. Exposure heuristics (fallback)

Never assume without checking metadata first.

---

## Project Generation Logic

For each folder in Raw/:

1. Create project folder:
```
Projects/<Name>_Project/
```

2. Create subfolders:
```
lights/
darks/
biases/
flats/
```

3. Copy FITS files into correct subfolder based on classification.

4. Generate project metrics summary.

---

## Metrics Per Project

### Frame counts
- total lights
- total darks
- total flats
- total biases

---

### Integration time

Total integration time = sum(EXPTIME of LIGHT frames)

Return:
- seconds
- formatted hours/minutes/seconds

---

### Capture timeline
From DATE-OBS:
- start time
- end time
- session duration

---

### Exposure validation
Detect and report:
- multiple exposure values in LIGHT frames
- mismatched dark exposures

---

### File stats
- total FITS file count
- total disk usage per project

---

## Data Model

### FITS File Record
```
FitsFile:
  path
  frameType
  metadata:
    exptime
    dateObs
    object
    filter
    gain
    temp
```

---

### Project Model
```
Project:
  name
  sourceFolder
  outputFolder
  frames[]
  metrics:
    totalLights
    totalDarks
    totalFlats
    totalBias
    totalIntegrationSeconds
    sessionStart
    sessionEnd
```

---

## Application Features

### 1. Folder Selection
- Select Raw directory
- Select Projects directory

### 2. Scan & Ingest
- Detect *_subs folders
- Parse FITS files
- Classify frames

### 3. Project Builder
- Create folder structure
- Copy files (safe copy only)
- Generate metrics

### 4. Dashboard
Show per project:
- integration time
- frame counts
- exposure breakdown
- timeline

---

## Performance Requirements

- Must handle large FITS datasets
- Must not block UI during operations
- Must show progress indicators

---

## Failure Handling

If:
- FITS file cannot be read → skip file
- metadata missing → continue with partial data
- folder invalid → skip folder

Never crash due to bad data.

---

## Future Extensions (DO NOT IMPLEMENT YET)

- image stacking integration (Siril, etc.)
- quality scoring (FWHM, SNR)
- database-backed projects
- cloud sync
- session auto-grouping across nights

---

## Agent Behavior Rules

- Prefer simplicity over abstraction
- Avoid hidden assumptions about FITS structure
- Never modify raw data
- Keep file operations explicit and traceable
- Favor readability over clever code