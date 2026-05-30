# Quick Reference Card

**Seestar FITS Organizer v1.3.3**

---

## 🚀 Quick Start

### 1. Import Your Data (Choose One)

| Your Situation | Use This | Menu Path |
|----------------|----------|-----------|
| Quick organization | **Direct Copy** | Import → Direct Copy |
| Need review first | **Intermediate Copy** | Import → Intermediate Copy |
| Planetary/Solar/Lunar videos | **Planetary & Scenery** | Import → Planetary & Scenery |

### 2. Analyze Your Projects

- **🔧 Tools → Project Analyzer** - View stats, integration time, sessions
- **🔧 Tools → FITS Viewer** - Preview files, zoom, mark for deletion

### 3. Adjust Settings (Optional)

- **⚙️ Settings** - Timezone, coordinates, text size

---

## 📂 Folder Structure

### Input (Seestar Export)
```
Raw/
  m3_subs/          ← FITS files
  m27_subs/
  Planetary_video/  ← Media files
  Lunar_photo/
```

### Output (Organized)
```
Projects/
  M3_Project/
    lights/
    darks/
    biases/
    flats/
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| ↑ | Previous file (FITS Viewer) |
| ↓ | Next file (FITS Viewer) |

---

## 🔍 FITS Viewer Controls

| Control | Range | Purpose |
|---------|-------|---------|
| Zoom In | Up to 250% | Magnify image |
| Zoom Out | Down to 30% | Shrink image |
| Click % | 30-250% | Custom zoom input |
| Mark | Toggle | Mark for deletion |
| Delete Marked | - | Remove marked files |

---

## 📊 Project Analyzer Stats

| Stat | Meaning |
|------|---------|
| Lights | Image frames of your target |
| Darks | Dark frames for noise reduction |
| Flats | Flat frames for vignette correction |
| Biases | Bias frames for calibration |
| Integration | Total exposure time (lights only) |

---

## ⚙️ Settings Quick Guide

| Setting | Options | When to Change |
|---------|---------|----------------|
| Timezone | UTC, PST, EST, Local | Match your observing timezone |
| Coordinates | Decimal, HMS/DMS | Decimal for calculations, HMS for traditional |
| Text Scale | 0.8x, 1.0x, 1.2x, 1.4x | Larger for accessibility, smaller for small screens |
| Location Threshold | 0.001-0.1° | Larger = groups more distant sites together |

---

## ❓ Common Issues (30-Second Fixes)

| Problem | Solution |
|---------|----------|
| No files found | Check folder ends with `_subs` |
| Text too small/big | Settings → Text Scale → Save → Restart |
| Can't navigate images | Use ↑↓ arrows or Previous/Next buttons |
| Wrong file types | Check FITS files have `.fits` extension |
| Coordinates wrong | Switch format in Settings (Decimal vs HMS) |
| Times look wrong | Change Timezone in Settings |

---

## 🎯 Workflow Decision Tree

```
What do you want to do?
├── Organize deep-sky FITS
│   ├── Quick/simple workflow? → Direct Copy
│   └── Need to review first? → Intermediate Copy
├── Organize planetary/media files
│   └── Planetary & Scenery
├── Check my data
│   ├── Preview individual files? → FITS Viewer
│   └── See project statistics? → Project Analyzer
└── Change preferences
    └── Settings
```

---

## 📱 Menu Map

```
📥 Import
├── Direct Copy (Raw → Projects)
├── Intermediate Copy (Raw → Processing → Projects)
└── Planetary & Scenery (Media files)

🔧 Tools
├── FITS Viewer
└── Project Analyzer

⚙️ Settings
│   (All app settings)

❓ Help
├── About
└── Documentation

🏠 Home
│   (Return to landing page)

❌ Exit
    (Close application)
```

---

## 🔢 Version Info

- **App Version**: 1.3.3
- **Created by**: Guy Ronen
- **Settings File**: `core/app_settings.json`

---

## 📞 Support Resources

1. **Troubleshooting Guide** - See `07-troubleshooting.md`
2. **Full Documentation** - All `.md` files in this folder
3. **Logs** - Check `logs/` folder for error details

---

## 💡 Pro Tips

- **Restart after changing text scale** - It won't apply until restart
- **Original files are never touched** - Only copies are made
- **Use keyboard arrows in FITS Viewer** - Faster than clicking
- **Export to CSV** - Great for tracking your imaging sessions
- **Sky Atlas button** - Opens your target in online star chart

---

## 🖼️ Screenshot Guide

When reporting issues, include:
1. Full window screenshot
2. Menu that's open (if any)
3. Error message text
4. What you clicked before the issue

---

**Print this page and keep it handy!**
