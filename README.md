# Seestar Astronomy Helper App

A Windows desktop application for processing astrophotography data from Seestar telescopes.

## Features

- **Ingest** raw FITS files from Seestar exports
- **Organize** files into structured astrophotography projects
- **Extract** metadata from FITS headers
- **Compute** integration time and capture statistics
- **Safe file operations** - only copies, never modifies or deletes source data

## Installation

1. Install Python 3.9 or later from [python.org](https://www.python.org/downloads/)

2. Navigate to the project directory:
   ```cmd
   cd "c:\Users\Guy\Seestar Processing"
   ```

3. Create a virtual environment (recommended):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```cmd
   python main.py
   ```

2. In the application:
   - Click **Browse** to select your **Raw Directory** (containing `*_subs` folders)
   - Click **Browse** to select your **Projects Directory** (where organized projects will be created)
   - Click **Scan & Build Projects** to process your data

3. View results in the **Project Dashboard** showing:
   - Frame counts (lights, darks, flats, bias)
   - Total integration time
   - File statistics

## Folder Structure

### Input (Raw Data)
```
Raw/
  m3_subs/
  m27_subs/
```

### Output (Projects)
```
Projects/
  M3_Project/
    lights/
    darks/
    biases/
    flats/
```

## Requirements

- Python 3.9+
- astropy (FITS file handling)
- customtkinter (modern UI)

## Core Rules

- **NEVER** deletes or modifies files in Raw/
- **ONLY** copies files into Projects/
- All processing is deterministic and repeatable
- FITS metadata is the primary source of truth
- Handles missing or partial metadata gracefully
