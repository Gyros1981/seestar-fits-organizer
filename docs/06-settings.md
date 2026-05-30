# Settings Reference

## Accessing Settings

**[SCREENSHOT: Main window with Settings button visible]**

**[ARROW: Point to "⚙️ Settings" button in menu bar]**

1. Click **Settings** button in menu bar

**[SCREENSHOT: Full Settings panel with all sections]**

---

## Location Settings

**[SCREENSHOT: Location Settings section]**

### Location Grouping Threshold

**[ARROW: Point to threshold input field]**

Controls how close locations must be to be grouped together in Project Analyzer.

- **Default**: 0.005 degrees (~600 yards)
- **Range**: 0.001 to 0.1 degrees
- **Purpose**: Capture sites within this distance are considered the same location

**[ARROW: Point to help text]** Shows default value meaning.

### How It Works:

```
Threshold = 0.005°

Site A (lat: 34.1234, lon: -118.5678)
Site B (lat: 34.1239, lon: -118.5672) ← Within 0.005° → Grouped together
Site C (lat: 34.2000, lon: -118.6000) ← Outside range → Separate location
```

**[SCREENSHOT: Map showing location grouping concept]**

---

## Timezone Settings

**[SCREENSHOT: Timezone Settings section]**

### Display Timezone

**[ARROW: Point to timezone dropdown menu]**

Select how times are displayed in Project Analyzer:

| Option | Description |
|--------|-------------|
| UTC | Universal Coordinated Time |
| PST (UTC-8) | Pacific Standard Time |
| EST (UTC-5) | Eastern Standard Time |
| Local | Your computer's local timezone |

**[SCREENSHOT: Dropdown showing all 4 options]**

### Example Time Display:

**[SCREENSHOT: Same session timestamp shown in different timezones]**

- UTC: 2024-01-15 08:30:00
- PST: 2024-01-15 00:30:00
- EST: 2024-01-15 03:30:00
- Local: (varies by user location)

---

## Coordinate Format

**[SCREENSHOT: Coordinate Format section]**

### RA/DEC Display Format

**[ARROW: Point to coordinate format dropdown]**

Choose how coordinates are displayed:

| Format | Example |
|--------|---------|
| Decimal Degrees | RA: 83.8221°, DEC: -5.3911° |
| Hours/Minutes/Seconds | RA: 05h 35m 17.3s, DEC: -05° 23' 28" |

**[SCREENSHOT: Side-by-side comparison of both formats]**

### Decimal Degrees
- Easier for calculations
- Used by many online tools

### HMS/DMS Format
- Traditional astronomy format
- Easier to communicate verbally
- Used in star atlases

---

## Text Scale

**[SCREENSHOT: Text Scale section]**

### UI Text Size

**[ARROW: Point to text scale dropdown]**

Adjust application-wide text size:

| Setting | Scale | Use Case |
|---------|-------|----------|
| Small (0.8x) | 80% | Small screens, more content visible |
| Normal (1.0x) | 100% | Default, balanced view |
| Large (1.2x) | 120% | Easier reading |
| Extra Large (1.4x) | 140% | Accessibility, large monitors |

**[SCREENSHOT: Same view shown at 0.8x, 1.0x, and 1.4x scales]**

### Changing Text Scale:

1. Select desired scale from dropdown
2. Click **Save Settings**
3. **Restart application** to apply changes

**⚠️ IMPORTANT**: Text scale requires app restart to take full effect.

---

## Saving Settings

**[SCREENSHOT: Bottom of Settings panel with Save button]**

**[ARROW: Point to "Save Settings" button]**

1. Adjust settings as needed
2. Click **Save Settings**

**[SCREENSHOT: Success message "Settings saved successfully!"]**

Settings are saved to `core/app_settings.json` file.

---

## Settings File Location

```
Seestar Processing/
  core/
    app_settings.json
```

**[SCREENSHOT: File explorer showing settings file location]**

**[ARROW: Point to app_settings.json file]** Can be manually edited if needed.

---

## Settings Persistence

All settings are automatically loaded on startup:
- Location threshold
- Timezone preference
- Coordinate format
- Text scale
- Disclaimer acknowledgment

**[SCREENSHOT: Settings panel showing previously saved values loaded]**

---

## Resetting to Defaults

To reset all settings:
1. Close application
2. Delete `core/app_settings.json`
3. Restart application

**[SCREENSHOT: Warning dialog about reset]**

⚠️ This cannot be undone!

---

## Recommended Settings by Use Case

### For Backyard Imaging (Single Location)
- Threshold: 0.005° (default)
- Timezone: Your local timezone
- Coordinates: HMS/DMS (traditional)

### For Remote/Travel Imaging (Multiple Sites)
- Threshold: 0.02° (larger area)
- Timezone: UTC (consistent)
- Coordinates: Decimal (easier comparison)

### For Accessibility
- Text Scale: Large or Extra Large
- Other settings: Personal preference

### For Small Laptops
- Text Scale: Small
- Threshold: 0.005° (default)
