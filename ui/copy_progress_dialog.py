"""
Copy Progress Dialog Module

A modal, Windows Explorer-style progress dialog shown while FITS files are
copied. Displays the current phase, the file being copied, an overall progress
bar, a running count, and a Cancel button for cooperative cancellation.
"""

import customtkinter as ctk

from ui.theme import BTN_NEUTRAL, TEXT_MUTED, ACCENT, ACCENT_HOVER


class CopyProgressWindow(ctk.CTkToplevel):
    """Modal progress window for file copy operations.

    The dialog is created on the main (UI) thread. A background worker updates
    it exclusively via ``parent.after(0, ...)`` so all widget access stays on
    the UI thread. Cancellation is cooperative: pressing Cancel sets a flag the
    worker polls via :meth:`is_cancelled`.
    """

    def __init__(self, parent, title="Copying Files", settings=None):
        super().__init__(parent)

        self.parent = parent
        self.settings = settings
        self._cancelled = False

        self.title(title)
        self.geometry("480x210")
        self.resizable(False, False)
        self.transient(parent)

        # Keep the dialog above the main window and grab focus like Explorer.
        self.grab_set()

        # Treat the window-close button as a cancel request.
        self.protocol("WM_DELETE_WINDOW", self.request_cancel)

        self._build_ui()
        self._center_on_parent(parent)

    def get_font(self, size: int, weight: str = None):
        """Return a CTkFont with the app's text scaling applied."""
        if self.settings:
            try:
                size = int(size * self.settings.get_text_scale())
            except Exception:
                pass
        if weight:
            return ctk.CTkFont(size=size, weight=weight)
        return ctk.CTkFont(size=size)

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=18)

        # Phase / heading (e.g. "Copying to Raw", "Building projects")
        self.phase_label = ctk.CTkLabel(
            container,
            text="Preparing to copy...",
            font=self.get_font(15, weight="bold"),
            anchor="w",
        )
        self.phase_label.pack(fill="x")

        # Current file name being copied
        self.file_label = ctk.CTkLabel(
            container,
            text="",
            font=self.get_font(12),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.file_label.pack(fill="x", pady=(4, 12))

        # Determinate progress bar
        self.progress_bar = ctk.CTkProgressBar(container, height=18)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # Count + percentage row
        stats_row = ctk.CTkFrame(container, fg_color="transparent")
        stats_row.pack(fill="x", pady=(6, 14))

        self.count_label = ctk.CTkLabel(
            stats_row, text="0 of 0", font=self.get_font(11), text_color=TEXT_MUTED
        )
        self.count_label.pack(side="left")

        self.percent_label = ctk.CTkLabel(
            stats_row, text="0%", font=self.get_font(11, weight="bold")
        )
        self.percent_label.pack(side="right")

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            container, text="Cancel", width=110, height=32,
            command=self.request_cancel, **BTN_NEUTRAL,
        )
        self.cancel_btn.pack(side="right")

    def _center_on_parent(self, parent):
        """Position the dialog centered over the parent window."""
        try:
            self.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Worker-facing API (always call via parent.after on the UI thread)
    # ------------------------------------------------------------------
    def set_phase(self, text: str):
        """Update the heading describing the current copy phase."""
        if self.winfo_exists():
            self.phase_label.configure(text=text)

    def update_progress(self, current: int, total: int, percentage: float,
                        filename: str = ""):
        """Update the progress bar, counter, percentage, and current file."""
        if not self.winfo_exists():
            return
        self.progress_bar.set(max(0.0, min(1.0, percentage)))
        self.count_label.configure(text=f"{current} of {total} files")
        self.percent_label.configure(text=f"{int(percentage * 100)}%")
        if filename:
            self.file_label.configure(text=filename)

    def request_cancel(self):
        """Flag cancellation and reflect it in the UI (worker stops shortly)."""
        self._cancelled = True
        if self.winfo_exists():
            self.phase_label.configure(text="Cancelling...")
            self.cancel_btn.configure(state="disabled", text="Cancelling...")

    def is_cancelled(self) -> bool:
        """Return True once the user has requested cancellation."""
        return self._cancelled

    def close(self):
        """Release the grab and destroy the dialog."""
        try:
            self.grab_release()
        except Exception:
            pass
        if self.winfo_exists():
            self.destroy()
