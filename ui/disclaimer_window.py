"""
Disclaimer Window Module

Displays the application disclaimer and Terms of Service on startup.
"""

import customtkinter as ctk
from pathlib import Path
import logging

from ui.theme import INFO, INFO_HOVER

logger = logging.getLogger(__name__)


class DisclaimerWindow(ctk.CTkToplevel):
    """
    Window for displaying the disclaimer on startup.
    
    Shows disclaimer text from DISCLAIMER.md and provides option
    to not show again on future launches.
    """
    
    def __init__(self, parent, settings):
        """
        Initialize the disclaimer window.
        
        Args:
            parent: Parent window
            settings: AppSettings instance
        """
        super().__init__(parent)
        
        self.settings = settings
        self.parent = parent
        
        self.title("Disclaimer")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def get_font(self, size: int, weight: str = None):
        """Get a CTkFont with text scaling applied."""
        scale = self.settings.get_text_scale()
        scaled_size = int(size * scale)
        if weight:
            return ctk.CTkFont(size=scaled_size, weight=weight)
        return ctk.CTkFont(size=scaled_size)
    
    def setup_ui(self):
        """Setup the disclaimer UI components."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ Disclaimer",
            font=self.get_font(24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Scrollable text area for disclaimer content
        disclaimer_text = ctk.CTkTextbox(main_frame, height=350)
        disclaimer_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Load disclaimer content from file
        try:
            disclaimer_path = Path(__file__).parent.parent / "DISCLAIMER.md"
            if disclaimer_path.exists():
                with open(disclaimer_path, 'r') as f:
                    content = f.read()
                    disclaimer_text.insert("1.0", content)
            else:
                disclaimer_text.insert("1.0", "Disclaimer file not found.")
        except Exception as e:
            logger.error(f"Failed to load disclaimer: {e}")
            disclaimer_text.insert("1.0", "Failed to load disclaimer content.")
        
        disclaimer_text.configure(state="disabled")
        
        # Checkbox for "Don't show this again"
        self.dont_show_again_var = ctk.BooleanVar(value=False)
        dont_show_again_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="Don't show this disclaimer again",
            variable=self.dont_show_again_var,
            font=self.get_font(12)
        )
        dont_show_again_checkbox.pack(anchor="w", padx=10, pady=(0, 15))
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 0))
        
        # View Terms of Service button
        tos_button = ctk.CTkButton(
            button_frame,
            text="📄 View Terms of Service",
            font=self.get_font(14),
            height=40,
            command=self.show_tos
        )
        tos_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Continue button
        continue_button = ctk.CTkButton(
            button_frame,
            text="Continue to App",
            font=self.get_font(14, weight="bold"),
            height=40,
            fg_color=INFO,
            hover_color=INFO_HOVER,
            command=self.continue_to_app
        )
        continue_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def show_tos(self):
        """Show the Terms of Service in a new window."""
        tos_window = ctk.CTkToplevel(self)
        tos_window.title("Terms of Service")
        tos_window.geometry("700x600")
        tos_window.transient(self)
        
        # Main container
        main_frame = ctk.CTkFrame(tos_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Terms of Service",
            font=self.get_font(24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Scrollable text area for TOS content
        tos_text = ctk.CTkTextbox(main_frame, height=400)
        tos_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Load TOS content from file
        try:
            tos_path = Path(__file__).parent.parent / "TERMS_OF_SERVICE.md"
            if tos_path.exists():
                with open(tos_path, 'r') as f:
                    content = f.read()
                    tos_text.insert("1.0", content)
            else:
                tos_text.insert("1.0", "Terms of Service file not found.")
        except Exception as e:
            logger.error(f"Failed to load TOS: {e}")
            tos_text.insert("1.0", "Failed to load Terms of Service content.")
        
        tos_text.configure(state="disabled")
        
        # Close button
        close_button = ctk.CTkButton(
            main_frame,
            text="Close",
            font=self.get_font(14),
            height=40,
            command=tos_window.destroy
        )
        close_button.pack(fill="x")
    
    def continue_to_app(self):
        """Continue to the main app after acknowledging disclaimer."""
        # Save the "don't show again" preference
        if self.dont_show_again_var.get():
            self.settings.set_disclaimer_acknowledged(True)
        
        self.destroy()
