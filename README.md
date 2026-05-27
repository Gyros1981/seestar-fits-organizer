# Seestar FITS Organizer

A Windows desktop application for processing astrophotography data from Seestar telescopes.

## Features

- **Ingest** raw FITS files from Seestar exports
- **Organize** files into structured astrophotography projects
- **Extract** metadata from FITS headers (exposure time, date, object, filter, coordinates, etc.)
- **Compute** integration time and capture statistics
- **Safe file operations** - only copies, never modifies or deletes source data
- **Analysis window** with search/filter for existing projects
- **Session-level breakdowns** with frame counts and exposure times
- **Capture location tracking** with custom tagging
- **Google Maps integration** for each location
- **Local tag storage** - your favorite spots persist across sessions

## Installation

### Option 1: Standalone Executable (Recommended for Sharing)

Download the pre-built executable from the [Releases](https://github.com/Gyros1981/seestar-fits-organizer/releases) section. No Python installation required - just run the `.exe` file.

### Option 2: Build from Source

#### Virtual Environment (Recommended but Optional)

A virtual environment keeps your project dependencies isolated from other Python projects on your system, preventing version conflicts. However, for a simple app like this, you can skip it if you prefer a simpler setup.

**With virtual environment:**
- Prevents conflicts with other projects
- Easier to reproduce the setup
- Cleaner system-wide Python

**Without virtual environment:**
- Simpler setup (fewer steps)
- Works fine for a single project
- Dependencies install globally

#### Quick Install

1. Clone the repository:
   ```cmd
   git clone https://github.com/Gyros1981/seestar-fits-organizer.git
   cd seestar-fits-organizer
   ```

2. Install Python 3.9 or later from [python.org](https://www.python.org/downloads/)

3. (Optional) Create a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

#### Building the Executable

To create a standalone `.exe` file for sharing:

1. Install PyInstaller (included in requirements.txt):
   ```cmd
   pip install pyinstaller
   ```

2. Run the build script:
   ```cmd
   build_exe.bat
   ```

Or manually:
   ```cmd
   pyinstaller --onefile --windowed --name "Seestar FITS Organizer" main.py
   ```

The executable will be created in the `dist` folder.

## Usage

1. Run the application:
   ```cmd
   python main.py
   ```

2. In the application:
   - Click **Browse** to select your **Seestar Directory** (original Seestar exports)
   - Click **Browse** to select your **Raw Directory** (containing `*_subs` folders)
   - Click **Browse** to select your **Projects Directory** (where organized projects will be created)
   - Click **Scan & Build Projects** to process your data

3. View results in the **Project Dashboard** showing:
   - Frame counts (lights, darks, flats, bias)
   - Total integration time
   - File statistics

4. Click **Analyze** to open the analysis window for existing projects:
   - Search/filter projects by name, object, or location
   - View detailed project metrics
   - Expand sessions to see capture details
   - Tag locations with custom names
   - Open locations in Google Maps

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
