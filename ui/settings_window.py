"""
Settings Window Module

Provides a dialog for configuring application settings including
location grouping threshold, timezone, and location tags management.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import logging

logger = logging.getLogger(__name__)


class SettingsWindow(ctk.CTkToplevel):
    """
    Window for application settings.
    
    Allows configuration of:
    - Location grouping threshold
    - Timezone display
    - Location tags import/export
    - Disclaimer reset
    """
    
    def __init__(self, parent, settings, location_tags):
        """
        Initialize the settings window.
        
        Args:
            parent: Parent window
            settings: AppSettings instance
            location_tags: LocationTags instance
        """
        super().__init__(parent)
        
        self.settings = settings
        self.parent = parent
        self.location_tags = location_tags
        
        self.title("Settings")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings UI."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Location Settings Section
        location_frame = ctk.CTkFrame(main_frame)
        location_frame.pack(fill="x", pady=(0, 15))
        
        location_label = ctk.CTkLabel(
            location_frame,
            text="Location Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        location_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Location grouping threshold
        threshold_label = ctk.CTkLabel(
            location_frame,
            text="Location Grouping Threshold (degrees):"
        )
        threshold_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.threshold_entry = ctk.CTkEntry(location_frame)
        self.threshold_entry.pack(fill="x", padx=10, pady=(0, 5))
        self.threshold_entry.insert("0", str(self.settings.get_location_threshold()))
        
        threshold_help = ctk.CTkLabel(
            location_frame,
            text="Locations within this distance will be grouped together (default: 0.005 ≈ 600 yards)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        threshold_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Timezone Settings Section
        timezone_frame = ctk.CTkFrame(main_frame)
        timezone_frame.pack(fill="x", pady=(0, 15))
        
        timezone_label = ctk.CTkLabel(
            timezone_frame,
            text="Timezone Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        timezone_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Timezone selection
        tz_label = ctk.CTkLabel(
            timezone_frame,
            text="Display Timezone:"
        )
        tz_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.timezone_menu = ctk.CTkOptionMenu(
            timezone_frame,
            values=["UTC", "PST (UTC-8)", "EST (UTC-5)", "Local"],
            command=None
        )
        self.timezone_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Map timezone setting to menu value
        tz_setting = self.settings.get_timezone()
        if tz_setting == "UTC":
            self.timezone_menu.set("UTC")
        elif tz_setting == "EST":
            self.timezone_menu.set("EST (UTC-5)")
        elif tz_setting == "Local":
            self.timezone_menu.set("Local")
        else:
            self.timezone_menu.set("PST (UTC-8)")
        
        # Location Tags Section
        tags_frame = ctk.CTkFrame(main_frame)
        tags_frame.pack(fill="x", pady=(0, 15))
        
        tags_label = ctk.CTkLabel(
            tags_frame,
            text="Location Tags",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tags_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Import/Export buttons
        button_frame = ctk.CTkFrame(tags_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        import_button = ctk.CTkButton(
            button_frame,
            text="📥 Import Tags",
            command=self.import_tags,
            height=35
        )
        import_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        export_button = ctk.CTkButton(
            button_frame,
            text="📤 Export Tags",
            command=self.export_tags,
            height=35
        )
        export_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Disclaimer Section
        disclaimer_frame = ctk.CTkFrame(main_frame)
        disclaimer_frame.pack(fill="x", pady=(0, 15))
        
        disclaimer_label = ctk.CTkLabel(
            disclaimer_frame,
            text="Disclaimer",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        disclaimer_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        reset_disclaimer_button = ctk.CTkButton(
            disclaimer_frame,
            text="🔄 Show Disclaimer on Startup",
            command=self.reset_disclaimer,
            height=35
        )
        reset_disclaimer_button.pack(fill="x", padx=10, pady=(0, 10))
        
        disclaimer_help = ctk.CTkLabel(
            disclaimer_frame,
            text="Click to show the disclaimer window again on next startup",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        disclaimer_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Save/Cancel buttons
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(20, 0))
        
        save_button = ctk.CTkButton(
            action_frame,
            text="Save",
            fg_color="#1E90FF",
            hover_color="#4169E1",
            command=self.save_settings,
            height=40
        )
        save_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        cancel_button = ctk.CTkButton(
            action_frame,
            text="Cancel",
            command=self.destroy,
            height=40
        )
        cancel_button.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def import_tags(self):
        """Import location tags from a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Import Location Tags",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Import tags to location_tags system
                    for key, value in data.items():
                        try:
                            lat, lon = key.split(',')
                            self.location_tags.set_tag(lat, lon, value['name'], value.get('notes', ''))
                        except (ValueError, KeyError):
                            continue
                    messagebox.showinfo("Success", f"Imported {len(data)} location tags")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import tags: {str(e)}")
    
    def export_tags(self):
        """Export location tags to a JSON file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Location Tags",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Export tags from location_tags system
                data = self.location_tags.get_all_tags()
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", f"Exported {len(data)} location tags to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export tags: {str(e)}")
    
    def reset_disclaimer(self):
        """Reset the disclaimer acknowledgment so it shows on next startup."""
        if messagebox.askyesno("Confirm", "Show the disclaimer window again on next startup?"):
            self.settings.set_disclaimer_acknowledged(False)
            messagebox.showinfo("Success", "Disclaimer will be shown on next startup.")
    
    def save_settings(self):
        """Save settings and close dialog."""
        try:
            # Save location threshold
            threshold = float(self.threshold_entry.get())
            self.settings.set_location_threshold(threshold)
            
            # Save timezone
            tz_value = self.timezone_menu.get()
            if "UTC" in tz_value:
                self.settings.set_timezone("UTC")
            elif "EST" in tz_value:
                self.settings.set_timezone("EST")
            elif "Local" in tz_value:
                self.settings.set_timezone("Local")
            else:
                self.settings.set_timezone("PST")
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid threshold value. Please enter a number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
