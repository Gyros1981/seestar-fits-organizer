"""
Folder Selection Dialog Module

Allows users to select which discovered folders to process.
"""

import customtkinter as ctk
from pathlib import Path
from typing import List

from ui.theme import INFO, INFO_HOVER


class FolderSelectionWindow(ctk.CTkToplevel):
    """
    Window for selecting which folders to process.
    
    Displays discovered folders with checkboxes, allowing users to
    select specific folders or use Select All/Deselect All options.
    """
    
    def __init__(self, parent, folders: List[Path], settings=None):
        """
        Initialize the folder selection window.
        
        Args:
            parent: Parent window
            folders: List of Path objects representing discovered folders
            settings: AppSettings instance for text scaling
        """
        super().__init__(parent)
        
        self.parent = parent
        self.folders = folders
        self.settings = settings
        self.selected_folders: List[Path] = []
        self.result = None
        
        self.title("Select Folders to Process")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def get_font(self, size: int, weight: str = None):
        """Get a CTkFont with text scaling applied."""
        if self.settings:
            scale = self.settings.get_text_scale()
            scaled_size = int(size * scale)
        else:
            scaled_size = size
        if weight:
            return ctk.CTkFont(size=scaled_size, weight=weight)
        return ctk.CTkFont(size=scaled_size)
    
    def setup_ui(self):
        """Setup the folder selection UI components."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📁 Select Folders to Process",
            font=self.get_font(20, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            main_frame,
            text=f"Found {len(self.folders)} folder(s). Select which ones to process:",
            font=self.get_font(12),
            text_color="gray"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Select All / Deselect All buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))
        
        select_all_btn = ctk.CTkButton(
            button_frame,
            text="Select All",
            command=self.select_all,
            width=100
        )
        select_all_btn.pack(side="left", padx=(0, 10))
        
        deselect_all_btn = ctk.CTkButton(
            button_frame,
            text="Deselect All",
            command=self.deselect_all,
            width=100
        )
        deselect_all_btn.pack(side="left")
        
        # Scrollable frame for checkboxes
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create checkbox for each folder (sorted alphabetically)
        self.checkbox_vars = {}
        for folder in sorted(self.folders, key=lambda x: x.name.lower()):
            var = ctk.BooleanVar(value=True)  # Default to selected
            self.checkbox_vars[folder] = var
            
            checkbox = ctk.CTkCheckBox(
                scroll_frame,
                text=folder.name,
                variable=var,
                font=self.get_font(12)
            )
            checkbox.pack(anchor="w", pady=2, padx=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            action_frame,
            text="Cancel",
            command=self.cancel,
            height=40
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        process_btn = ctk.CTkButton(
            action_frame,
            text="Process Selected",
            command=self.process,
            height=40,
            fg_color=INFO,
            hover_color=INFO_HOVER
        )
        process_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def select_all(self):
        """Select all folders."""
        for var in self.checkbox_vars.values():
            var.set(True)
    
    def deselect_all(self):
        """Deselect all folders."""
        for var in self.checkbox_vars.values():
            var.set(False)
    
    def process(self):
        """Process selected folders and close dialog."""
        self.selected_folders = [
            folder for folder, var in self.checkbox_vars.items()
            if var.get()
        ]
        self.result = "process"
        self.destroy()
    
    def cancel(self):
        """Cancel and close dialog."""
        self.result = "cancel"
        self.selected_folders = []
        self.destroy()
    
    def get_selected_folders(self) -> List[Path]:
        """Return the list of selected folders."""
        return self.selected_folders
