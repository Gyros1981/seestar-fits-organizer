"""
UI Theme / UX Constants

Central palette and widget-style presets for the Seestar FITS Organizer.
Import these names instead of hardcoding hex values so colors stay consistent
across every window and dialog. Tune a color here once and it updates app-wide.

Usage:
    from ui import theme
    ctk.CTkButton(parent, text="Go", **theme.BTN_PRIMARY)
    ctk.CTkLabel(parent, text="hint", text_color=theme.TEXT_FAINT)
"""

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

# Primary accent (orange) - main action buttons, menu bar, section headers.
ACCENT = "#E67E22"            # base orange
ACCENT_HOVER = "#D35400"      # darker orange for hover / pressed / separators

# Secondary (blue) - directory "Browse" buttons.
SECONDARY = "#3498db"
SECONDARY_HOVER = "#2980b9"

# Danger (red) - destructive actions (e.g. Delete Selected).
DANGER = "#C0392B"
DANGER_HOVER = "#A93226"

# Neutral (gray) - low-emphasis buttons (Cancel, Reset to Defaults).
NEUTRAL = "#7F8C8D"
NEUTRAL_HOVER = "#616A6B"

# Info (blue) - settings Save button.
INFO = "#1E90FF"
INFO_HOVER = "#4169E1"

# Surfaces / structural grays.
SURFACE_DARK = "#2B2B2B"      # listbox background
SEPARATOR_GRAY = "#3a3a3a"    # resizable separator / console toggle button
SEPARATOR_HOVER = "#555555"   # separator/console toggle hover
TOOLTIP_BG = "#2C3E50"        # tooltip background
SELECT_BG = "#1E90FF"         # listbox selection highlight

# Text colors.
TEXT_ON_ACCENT = "black"      # dark text used on orange/light buttons
TEXT_PRIMARY = "white"        # default light text
TEXT_LIGHT = "#E0E0E0"        # near-white (status text)
TEXT_MUTED = "#B0B0B0"        # secondary / description text
TEXT_DIM = "#A0A0A0"          # small section labels
TEXT_FAINT = "#808080"        # hints / placeholders

# ---------------------------------------------------------------------------
# Button style presets
# Spread into a CTkButton call, e.g. ctk.CTkButton(parent, **theme.BTN_PRIMARY)
# ---------------------------------------------------------------------------

# Primary orange action button (dark text for contrast).
BTN_PRIMARY = {
    "fg_color": ACCENT,
    "hover_color": ACCENT_HOVER,
    "text_color": TEXT_ON_ACCENT,
}

# Secondary blue button (e.g. directory browse).
BTN_SECONDARY = {
    "fg_color": SECONDARY,
    "hover_color": SECONDARY_HOVER,
}

# Destructive red button.
BTN_DANGER = {
    "fg_color": DANGER,
    "hover_color": DANGER_HOVER,
    "text_color": TEXT_PRIMARY,
}

# Low-emphasis neutral button.
BTN_NEUTRAL = {
    "fg_color": NEUTRAL,
    "hover_color": NEUTRAL_HOVER,
}
