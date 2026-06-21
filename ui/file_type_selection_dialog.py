"""
File Type Selection Dialog Module

Provides a dialog for selecting which file types to copy from Seestar directories.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Dict, Set, List
import logging

from ui.theme import ACCENT, ACCENT_HOVER, SECONDARY, SECONDARY_HOVER, NEUTRAL, NEUTRAL_HOVER

logger = logging.getLogger(__name__)


class FileTypeSelectionDialog(ctk.CTkToplevel):
    """
    Dialog for selecting which file types to copy from Seestar directories.
    
    Shows all discovered file extensions and allows user to select which ones to copy.
    """
    
    def __init__(self, parent, file_type_counts: Dict[str, int]):
        """
        Initialize the file type selection dialog.
        
        Args:
            parent: Parent window
            file_type_counts: Dictionary mapping file extensions to their counts
                             e.g., {'.fits': 150, '.FIT': 20, '.png': 5}
        """
        super().__init__(parent)
        
        self.parent = parent
        self.file_type_counts = file_type_counts
        self.selected_types: Set[str] = set()
        self.result = None  # "process" or "cancel"
        
        self.title("Select File Types to Copy")
        self.geometry("500x500")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the file type selection UI."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Select File Types to Copy",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Select which file types you want to copy from Seestar:",
            font=ctk.CTkFont(size=12)
        )
        desc_label.pack(pady=(0, 15))
        
        # Scrollable frame for file type checkboxes
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=200)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create checkboxes for each file type
        self.checkboxes = {}
        for ext, count in sorted(self.file_type_counts.items()):
            checkbox = ctk.CTkCheckBox(
                scroll_frame,
                text=f"{ext} ({count} files)",
                command=lambda e=ext: self._toggle_type(e)
            )
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.checkboxes[ext] = checkbox
        
        # Select All button
        select_all_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        select_all_frame.pack(fill="x", pady=(0, 15))
        
        select_all_btn = ctk.CTkButton(
            select_all_frame,
            text="Select All",
            width=100,
            fg_color=SECONDARY,
            hover_color=SECONDARY_HOVER,
            command=self._select_all
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        deselect_all_btn = ctk.CTkButton(
            select_all_frame,
            text="Deselect All",
            width=120,
            fg_color=SECONDARY,
            hover_color=SECONDARY_HOVER,
            command=self._deselect_all
        )
        deselect_all_btn.pack(side="left", padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            fg_color=NEUTRAL,
            hover_color=NEUTRAL_HOVER,
            command=self._cancel
        )
        cancel_btn.pack(side="right", padx=5)
        
        process_btn = ctk.CTkButton(
            button_frame,
            text="Copy Selected",
            width=120,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=self._process
        )
        process_btn.pack(side="right", padx=5)
    
    def _toggle_type(self, ext: str):
        """Toggle selection of a file type."""
        if ext in self.selected_types:
            self.selected_types.remove(ext)
        else:
            self.selected_types.add(ext)
        logger.debug(f"Toggled {ext}: {ext in self.selected_types}")
    
    def _select_all(self):
        """Select all file types."""
        for ext in self.file_type_counts:
            self.selected_types.add(ext)
            self.checkboxes[ext].select()
        logger.debug(f"Selected all types: {self.selected_types}")
    
    def _deselect_all(self):
        """Deselect all file types."""
        self.selected_types.clear()
        for checkbox in self.checkboxes.values():
            checkbox.deselect()
        logger.debug("Deselected all types")
    
    def _process(self):
        """Process with selected file types."""
        if not self.selected_types:
            from tkinter import messagebox
            messagebox.showwarning("No Selection", "Please select at least one file type.")
            return
        
        self.result = "process"
        self.destroy()
    
    def _cancel(self):
        """Cancel the operation."""
        self.result = "cancel"
        self.destroy()
    
    def get_selected_types(self) -> Set[str]:
        """Get the set of selected file type extensions."""
        return self.selected_types.copy()


def detect_file_types_in_directories(directories: List[Path]) -> Dict[str, int]:
    """
    Detect all file types and their counts in the given directories.
    
    Args:
        directories: List of directory paths to scan
        
    Returns:
        Dictionary mapping file extensions to their counts
    """
    file_type_counts: Dict[str, int] = {}
    
    for directory in directories:
        if not directory.exists():
            continue
        
        for item in directory.iterdir():
            if item.is_file():
                ext = item.suffix
                if ext:
                    file_type_counts[ext] = file_type_counts.get(ext, 0) + 1
    
    return file_type_counts
