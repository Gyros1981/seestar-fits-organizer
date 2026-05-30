# Screenshot & Annotation Guide

**How to create professional screenshots for the user documentation**

---

## 📸 Taking Screenshots

### Window Preparation

1. **Resize window** to consistent size:
   - Recommended: 1280x720 or 1600x900
   - Keeps screenshots consistent across docs

2. **Clean desktop**:
   - Hide desktop icons (Right-click desktop → View → Show desktop icons)
   - Hide taskbar if possible (Auto-hide)
   - Close unrelated apps

3. **Reset to known state**:
   - Click 🏠 Home to return to landing page
   - Navigate fresh to the screen you need
   - Don't show "used" UI (pre-selected items, error states unless documenting errors)

---

## 🎨 Annotation Style

### Arrow Colors

| Color | Use For |
|-------|---------|
| **Red** | Buttons to click, interactive elements |
| **Yellow/Orange** | Text to read, important labels |
| **Green** | Success states, correct examples |
| **Blue** | Informational highlights |

### Annotation Types

**[ARROW: Point to X button]**
- Use straight arrows
- Point directly to button/element
- Keep arrow tip close to target
- Add text label if not obvious

**[CIRCLE: Highlight text field]**
- Use circles or rounded rectangles
- Draw around text/form fields
- Keep border visible but not too thick

**[NUMBER: Step sequence]**
- Use numbered callouts (1, 2, 3)
- Place in order of operations
- Connect with line to element

**[TEXT: Add explanation]**
- Brief caption near element
- Keep under 5 words if possible
- Match document font style

---

## 🛠️ Tools

### Option 1: Windows Snip & Sketch (Built-in)

**How to use:**
1. Press `Win + Shift + S`
2. Select window or draw area
3. Opens in Snip & Sketch
4. Click pen tool for basic arrows
5. Save as PNG

**Pros:** Already installed  
**Cons:** Basic annotations only

### Option 2: ShareX (Free)

**Download:** sharex.si  
**Best for:** Professional documentation

**Setup:**
1. Install ShareX
2. Hotkey settings: `Ctrl + Print Screen` for region capture
3. After capture → Open in image editor

**Annotations:**
- Arrows (multiple styles)
- Steps (numbered callouts)
- Text boxes
- Blur (hide sensitive info)
- Pixelate

**Recommended workflow:**
1. Take screenshot with ShareX
2. Auto-opens in editor
3. Add arrows/numbers
4. Save as PNG to docs/images/

### Option 3: Snagit (Paid - Best Quality)

**Download:** techsmith.com/snagit

**Best for:** Professional software documentation

**Features:**
- Simplified user interface captures
- Step tool (auto-numbered)
- Callouts with arrow + text
- Blur and spotlight effects
- GIF/video recording

---

## 📋 Screenshot Checklist

For each screenshot in the docs:

- [ ] Window sized consistently (1280x720)
- [ ] Clean background (no distractions)
- [ ] Fresh state (not "used")
- [ ] Clear focus on subject
- [ ] Annotations added
- [ ] Arrows point precisely
- [ ] Text labels are readable
- [ ] Saved as PNG (not JPG for UI)
- [ ] Filename describes content
- [ ] Stored in docs/images/

---

## 📝 Annotation Examples

### Example 1: Button to Click

**Screenshot:**
```
[ RED ARROW pointing to button ]
        ↓
   ┌──────────────┐
   │ 📁 Browse    │
   └──────────────┘
```

**Caption:** Click the Browse button to select folder

---

### Example 2: Multiple Steps

**Screenshot:**
```
    ①                    ②
    ↓                    ↓
┌──────────┐         ┌──────────┐
│ 📁 Raw   │   →     │ Projects │
│ Directory│         │ Directory│
└──────────┘         └──────────┘
```

**Caption:** First select Raw (1), then Projects (2)

---

### Example 3: Highlighting Text

**Screenshot:**
```
    ╔═══════════════════════════════════════╗
    ║  Direct Copy                          ║
    ║  Copy FITS files directly from...     ║
    ╚═══════════════════════════════════════╝
         [YELLOW HIGHLIGHT around text]
```

**Caption:** Read this explanation before proceeding

---

### Example 4: Comparison

**Screenshot:**
```
   CORRECT ✅              INCORRECT ❌
   ┌─────────┐            ┌─────────┐
   │m3_subs/ │            │   m3/   │
   │  ✓      │            │    ✗    │
   └─────────┘            └─────────┘
   [_subs suffix]        [missing suffix]
```

**Caption:** Folder name must end with `_subs`

---

## 🎯 Specific Screenshot Requirements

### Full Window Screenshots

Use for:
- Overview documentation
- Showing layout/context
- Menu demonstrations

**Settings:**
- Capture entire window
- Include title bar
- Include menu bar

### Detail Screenshots

Use for:
- Specific buttons/controls
- Error messages
- Dialog boxes

**Settings:**
- Capture just the relevant area
- Zoom in if needed (but not blurry)
- Annotations large and clear

### Before/After Pairs

Use for:
- Workflow steps
- State changes
- Results

**Settings:**
- Same window size/position
- Same zoom level
- Side-by-side in document

---

## 📁 File Naming Convention

Save screenshots with descriptive names:

```
direct-copy-view.png
fits-viewer-zoom-100.png
fits-viewer-zoom-250.png
project-analyzer-sessions.png
settings-timezone-dropdown.png
error-no-files-found.png
```

---

## 📂 Folder Structure

```
docs/
  00-overview.md
  01-import-direct.md
  ...
  images/              ← Store screenshots here
    overview/
      menu-bar.png
      welcome-page.png
    import/
      direct-copy-view.png
      browse-dialog.png
    fits-viewer/
      full-view.png
      zoom-controls.png
    ...
```

---

## ✨ Quality Tips

### Do:
- ✅ Use consistent window size
- ✅ Take screenshots in good lighting (avoid screen glare)
- ✅ Use PNG format (lossless)
- ✅ Keep annotations clean and minimal
- ✅ Test that arrows are visible after compression
- ✅ Use high contrast colors (red on dark backgrounds)

### Don't:
- ❌ Use JPG (compression artifacts on text)
- ❌ Capture personal information (blur if necessary)
- ❌ Make arrows too small or thin
- ❌ Over-annotate (keep it clean)
- ❌ Use light colors on light backgrounds
- ❌ Resize screenshots smaller (makes text unreadable)

---

## 🎬 Recording Workflow (for your notes)

**Before starting:**
1. Clean desktop
2. Set window size
3. Open app fresh

**For each screenshot:**
1. Navigate to required view
2. Reset to clean state if needed
3. Take screenshot
4. Annotate immediately
5. Save with descriptive name
6. Check quality (can you read text?)

**After finishing:**
1. Review all screenshots
2. Check for consistency
3. Copy to Google Docs
4. Delete [SCREENSHOT] placeholders
5. Resize in document if needed

---

## 📱 Mobile Device Screenshots

If documenting mobile companion apps:
- Use phone's built-in screenshot
- Transfer to computer
- Annotate same as desktop screenshots
- Keep aspect ratio (don't stretch)

---

## 🔍 Review Checklist

Before finalizing documentation:

- [ ] All [SCREENSHOT] markers replaced with actual images
- [ ] All [ARROW] annotations added to images
- [ ] Images clear at 100% zoom in document
- [ ] No personal/sensitive info visible
- [ ] Consistent style throughout
- [ ] All steps shown visually
- [ ] Error screenshots if relevant

---

**Remember: Good screenshots reduce support questions!**
