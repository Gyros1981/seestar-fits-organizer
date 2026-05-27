"""
Seestar Astronomy Helper App - Main Application
Windows desktop application for processing astrophotography data.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from project_builder import ProjectBuilder
from location_tags import LocationTags
from app_settings import AppSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeestarApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Seestar FITS Organizer")
        self.geometry("1000x700")
        
        self.seestar_dir = None
        self.raw_dir = None
        self.projects_dir = None
        self.projects = []
        
        # Initialize settings
        self.settings = AppSettings()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title with settings button
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Seestar FITS Organizer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        settings_button = ctk.CTkButton(
            title_frame,
            text="⚙️",
            font=ctk.CTkFont(size=20),
            width=40,
            height=40,
            command=self.open_settings
        )
        settings_button.pack(side="right")
        
        # Folder Selection Frame
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill="x", pady=(0, 20))
        
        # Seestar Device Directory
        seestar_label = ctk.CTkLabel(folder_frame, text="Seestar Device Location:", font=ctk.CTkFont(weight="bold"))
        seestar_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        seestar_button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        seestar_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.seestar_path_label = ctk.CTkLabel(seestar_button_frame, text="Not selected", text_color="gray")
        self.seestar_path_label.pack(side="left", padx=(0, 10))
        
        seestar_button = ctk.CTkButton(seestar_button_frame, text="🌌 Browse", command=self.select_seestar_dir, width=100)
        seestar_button.pack(side="right")
        
        # Raw Directory (Target for copy)
        raw_label = ctk.CTkLabel(folder_frame, text="Raw Directory (Target):", font=ctk.CTkFont(weight="bold"))
        raw_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        raw_button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        raw_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.raw_path_label = ctk.CTkLabel(raw_button_frame, text="Not selected", text_color="gray")
        self.raw_path_label.pack(side="left", padx=(0, 10))
        
        raw_button = ctk.CTkButton(raw_button_frame, text="🌌 Browse", command=self.select_raw_dir, width=100)
        raw_button.pack(side="right")
        
        # Projects Directory
        projects_label = ctk.CTkLabel(folder_frame, text="Projects Directory:", font=ctk.CTkFont(weight="bold"))
        projects_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        projects_button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        projects_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.projects_path_label = ctk.CTkLabel(projects_button_frame, text="Not selected", text_color="gray")
        self.projects_path_label.pack(side="left", padx=(0, 10))
        
        projects_button = ctk.CTkButton(projects_button_frame, text="🌌 Browse", command=self.select_projects_dir, width=100)
        projects_button.pack(side="right")
        
        # Action Buttons
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(0, 20))
        
        self.scan_button = ctk.CTkButton(
            action_frame, 
            text="� Scan & Build Projects",
            command=self.start_scan,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.scan_button.pack(fill="x", padx=10, pady=(10, 5))
        
        self.analyze_button = ctk.CTkButton(
            action_frame,
            text="🪐 Analyze Existing Projects",
            command=self.start_analysis,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyze_button.pack(fill="x", padx=10, pady=(5, 10))
        
        # Progress Frame
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready", text_color="gray")
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Console Output Frame
        console_frame = ctk.CTkFrame(main_frame)
        console_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        console_label = ctk.CTkLabel(console_frame, text="Console Output", font=ctk.CTkFont(size=14, weight="bold"))
        console_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.console_text = ctk.CTkTextbox(console_frame, height=150)
        self.console_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.console_text.configure(state="disabled")
        
        # Redirect logging to console
        self.setup_console_logging()
    
    def setup_console_logging(self):
        """Setup custom logging handler to redirect output to console."""
        import logging
        
        class ConsoleHandler(logging.Handler):
            def __init__(self, textbox):
                super().__init__()
                self.textbox = textbox
            
            def emit(self, record):
                msg = self.format(record)
                self.textbox.configure(state="normal")
                self.textbox.insert("end", msg + "\n")
                self.textbox.see("end")
                self.textbox.configure(state="disabled")
        
        console_handler = ConsoleHandler(self.console_text)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        console_handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(console_handler)
    
    def select_seestar_dir(self):
        """Select Seestar device directory."""
        directory = filedialog.askdirectory(title="Select Seestar Device Location")
        if directory:
            self.seestar_dir = Path(directory)
            self.seestar_path_label.configure(text=str(self.seestar_dir), text_color="white")
            logger.info(f"Selected Seestar directory: {self.seestar_dir}")
    
    def select_raw_dir(self):
        """Select raw directory (target for copy)."""
        directory = filedialog.askdirectory(title="Select Raw Directory (Target)")
        if directory:
            self.raw_dir = Path(directory)
            self.raw_path_label.configure(text=str(self.raw_dir), text_color="white")
            logger.info(f"Selected raw directory: {self.raw_dir}")
    
    def select_projects_dir(self):
        """Select projects directory."""
        directory = filedialog.askdirectory(title="Select Projects Directory")
        if directory:
            self.projects_dir = Path(directory)
            self.projects_path_label.configure(text=str(self.projects_dir), text_color="white")
            logger.info(f"Selected projects directory: {self.projects_dir}")
    
    def start_scan(self):
        """Start scanning and building projects in a separate thread."""
        if not self.seestar_dir or not self.raw_dir or not self.projects_dir:
            messagebox.showerror("Error", "Please select all three directories (Seestar, Raw, Projects)")
            return
        
        self.scan_button.configure(state="disabled")
        self.progress_label.configure(text="Starting scan...")
        
        thread = threading.Thread(target=self.scan_and_build)
        thread.daemon = True
        thread.start()
    
    def start_analysis(self):
        """Start analysis of existing projects."""
        if not self.projects_dir:
            messagebox.showerror("Error", "Please select Projects directory")
            return
        
        self.analyze_button.configure(state="disabled")
        self.progress_label.configure(text="Analyzing projects...")
        
        thread = threading.Thread(target=self.analyze_projects)
        thread.daemon = True
        thread.start()
    
    def scan_and_build(self):
        """Scan and build projects."""
        try:
            # Step 1: Copy from Seestar to Raw directory
            self.after(0, lambda: self.progress_label.configure(text="Copying from Seestar to Raw..."))
            self.copy_seestar_to_raw()
            
            # Step 2: Build projects from Raw to Projects
            self.after(0, lambda: self.progress_label.configure(text="Building projects..."))
            builder = ProjectBuilder(self.raw_dir, self.projects_dir)
            
            folders = builder.scan_raw_folders()
            total_projects = len(folders)
            
            if total_projects == 0:
                self.after(0, lambda: self.progress_label.configure(text="No *_subs folders found in Raw"))
                self.after(0, lambda: self.scan_button.configure(state="normal"))
                return
            
            self.projects = []
            
            for i, folder in enumerate(folders):
                self.after(0, lambda idx=i, total=total_projects, fld=folder: 
                          self.progress_label.configure(text=f"Processing {fld.name} ({idx+1}/{total})"))
                
                project = builder.build_project(folder)
                self.projects.append(project)
            
            self.after(0, lambda: self.progress_label.configure(text=f"Completed! Built {len(self.projects)} projects"))
            
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to scan: {str(e)}"))
        
        finally:
            self.after(0, lambda: self.scan_button.configure(state="normal"))
    
    def copy_seestar_to_raw(self):
        """Copy <NAME>_sub folders from Seestar to Raw directory."""
        from shutil import copy2
        import os
        
        # Find all *_sub or *_subs folders in Seestar directory
        subs_folders = []
        for item in self.seestar_dir.iterdir():
            if item.is_dir() and (item.name.endswith('_subs') or item.name.endswith('_sub')):
                subs_folders.append(item)
        
        if not subs_folders:
            logger.warning(f"No *_subs folders found in Seestar directory: {self.seestar_dir}")
            return
        
        # Copy each folder to Raw directory
        for folder in subs_folders:
            dest = self.raw_dir / folder.name
            logger.info(f"Processing {folder} to {dest}")
            
            # Create destination folder if it doesn't exist
            dest.mkdir(parents=True, exist_ok=True)
            
            # Copy files individually, skipping existing ones
            files_copied = 0
            files_skipped = 0
            
            for item in folder.iterdir():
                dest_file = dest / item.name
                
                if item.is_file():
                    if dest_file.exists():
                        logger.info(f"Skipping existing file: {item.name}")
                        files_skipped += 1
                    else:
                        try:
                            copy2(item, dest_file)
                            logger.info(f"Copied: {item.name}")
                            files_copied += 1
                        except Exception as e:
                            logger.error(f"Failed to copy {item.name}: {e}")
            
            logger.info(f"Folder {folder.name}: {files_copied} files copied, {files_skipped} files skipped")
    
    def analyze_projects(self):
        """Analyze existing projects and show results."""
        try:
            from project_analyzer import ProjectAnalyzer
            
            analyzer = ProjectAnalyzer(self.projects_dir)
            results = analyzer.analyze_all()
            
            logger.info(f"Analysis complete. Total projects: {results.total_projects}")
            
            # Convert to dictionary for the window
            results_dict = results.to_dict()
            
            self.after(0, lambda: self.show_analysis_window(results_dict))
            self.after(0, lambda: self.progress_label.configure(text="Analysis complete"))
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during analysis: {error_msg}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to analyze: {error_msg}"))
        
        finally:
            self.after(0, lambda: self.analyze_button.configure(state="normal"))
    
    def show_analysis_window(self, results):
        """Show analysis results in a new window."""
        AnalysisWindow(self, results)


    def open_settings(self):
        """Open the settings dialog."""
        # Create a LocationTags instance for import/export
        location_tags = LocationTags()
        SettingsWindow(self, self.settings, location_tags)


class SettingsWindow(ctk.CTkToplevel):
    """Window for application settings."""
    
    def __init__(self, parent, settings, location_tags):
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
        from tkinter import filedialog
        import json
        
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
                            self.location_tags.set_tag(lat, value['name'], value.get('notes', ''))
                        except (ValueError, KeyError):
                            continue
                    messagebox.showinfo("Success", f"Imported {len(data)} location tags")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import tags: {str(e)}")
    
    def export_tags(self):
        """Export location tags to a JSON file."""
        from tkinter import filedialog
        import json
        
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


class AnalysisWindow(ctk.CTkToplevel):
    """Window for displaying project analysis results."""
    
    def __init__(self, parent, results):
        super().__init__(parent)
        
        self.title("Seestar FITS Organizer - Analysis")
        self.geometry("1400x900")
        
        self.results = results
        self.settings = parent.settings
        
        # Initialize location tags storage
        self.location_tags = LocationTags()
        
        self.setup_ui()
        
        # Bring window to front
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
    
    def setup_ui(self):
        """Setup the analysis window UI."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Seestar FITS Organizer - Analysis",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Check if no projects found
        if self.results['total_projects'] == 0:
            no_data_label = ctk.CTkLabel(
                main_frame,
                text="No projects found in the selected directory.\nMake sure you have folders ending with '_Project'.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return
        
        # Projects List Frame (left side)
        projects_frame = ctk.CTkFrame(main_frame)
        projects_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        projects_label = ctk.CTkLabel(projects_frame, text="Projects", font=ctk.CTkFont(size=18, weight="bold"))
        projects_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Search entry
        search_frame = ctk.CTkFrame(projects_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        search_label = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=16))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search projects...",
            height=32
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Scrollable frame for project list
        self.scroll_frame = ctk.CTkScrollableFrame(projects_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store original projects for filtering
        self.all_projects = self.results['projects'].copy()
        
        # Add aggregate statistics button at the top
        agg_button = ctk.CTkButton(
            self.scroll_frame,
            text="📊 Aggregate Statistics",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#2E8B57",  # Sea green color to differentiate
            hover_color="#3CB371",
            command=lambda: self.show_aggregate_stats()
        )
        agg_button.pack(fill="x", pady=(0, 10))
        
        # Separator line
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(0, 10))
        
        # Add project buttons
        self.project_buttons = []
        for project in self.all_projects:
            button = self.create_project_button(self.scroll_frame, project)
            self.project_buttons.append((button, project))
        
        # Project Details Frame (right side)
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.details_label = ctk.CTkLabel(details_frame, text="Project Details", font=ctk.CTkFont(size=18, weight="bold"))
        self.details_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.details_scroll = ctk.CTkScrollableFrame(details_frame)
        self.details_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial message
        self.no_selection_label = ctk.CTkLabel(
            self.details_scroll,
            text="Click on a project to view details",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.no_selection_label.pack(pady=50)
    
    def create_aggregate_stats(self, parent):
        """Create aggregate statistics display."""
        stats = self.results
        
        # Create grid of stats
        stats_data = [
            ("Total Projects", stats['total_projects']),
            ("Total Files", stats['total_files']),
            ("Total Size", f"{stats['total_size_gb']:.2f} GB"),
            ("Total Lights", stats['total_lights']),
            ("Total Darks", stats['total_darks']),
            ("Total Flats", stats['total_flats']),
            ("Total Bias", stats['total_bias']),
            ("Nights Captured", stats['nights_captured']),
        ]
        
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = ctk.CTkFrame(grid_frame)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            grid_frame.grid_columnconfigure(col, weight=1)
            
            label_widget = ctk.CTkLabel(stat_frame, text=label, font=ctk.CTkFont(weight="bold"))
            label_widget.pack(anchor="w", padx=10, pady=(10, 2))
            
            value_widget = ctk.CTkTextbox(stat_frame, height=35)
            value_widget.pack(fill="x", padx=10, pady=(2, 10))
            value_widget.insert("1.0", str(value))
            value_widget.configure(state="disabled", font=ctk.CTkFont(size=16))
        
        # Integration time
        hours = int(stats['total_integration_hours'])
        minutes = int((stats['total_integration_hours'] % 1) * 60)
        time_frame = ctk.CTkFrame(parent)
        time_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        time_label = ctk.CTkLabel(time_frame, text="Total Integration Time", font=ctk.CTkFont(weight="bold"))
        time_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        time_value = ctk.CTkTextbox(time_frame, height=35)
        time_value.pack(fill="x", padx=10, pady=(2, 10))
        time_value.insert("1.0", f"{hours}h {minutes}m")
        time_value.configure(state="disabled", font=ctk.CTkFont(size=16))
        
        # Unique objects and filters
        unique_frame = ctk.CTkFrame(parent)
        unique_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        objects_text = f"Objects: {', '.join(stats['unique_objects'])}" if stats['unique_objects'] else "Objects: None"
        filters_text = f"Filters: {', '.join(stats['unique_filters'])}" if stats['unique_filters'] else "Filters: None"
        
        objects_textbox = ctk.CTkTextbox(unique_frame, height=30)
        objects_textbox.pack(fill="x", padx=10, pady=(5, 2))
        objects_textbox.insert("1.0", objects_text)
        objects_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        filters_textbox = ctk.CTkTextbox(unique_frame, height=30)
        filters_textbox.pack(fill="x", padx=10, pady=(2, 10))
        filters_textbox.insert("1.0", filters_text)
        filters_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # Capture Locations expandable section
        locations_frame = ctk.CTkFrame(parent)
        locations_frame.pack(fill="x", padx=10, pady=5)
        
        locations_button = ctk.CTkButton(
            locations_frame,
            text="▶ Capture Locations",
            font=ctk.CTkFont(weight="bold"),
            height=35,
            command=lambda: self.toggle_expandable_section(locations_button, locations_content)
        )
        locations_button.pack(fill="x", padx=10, pady=(10, 5))
        
        locations_content = ctk.CTkFrame(locations_frame)
        locations_content.pack(fill="x", padx=10, pady=(0, 10))
        locations_content.pack_forget()  # Initially collapsed
        
        # Collect locations with objects from all projects
        location_data = []  # [(site, lat, lon, objects_set)]
        for project in stats['projects']:
            site = project.get('site')
            lat = project.get('latitude')
            lon = project.get('longitude')
            objects = project.get('objects', set())
            if site or (lat and lon):
                location_data.append((site, lat, lon, objects))
        
        if location_data:
            # Group nearby locations (within 100 yards ≈ 0.0008 degrees)
            grouped_locations = []
            used_indices = set()
            
            # Use a very forgiving threshold to account for GPS drift and coordinate precision
            # Get threshold from settings (default: 0.005 degrees ≈ 600 yards)
            threshold = self.settings.get_location_threshold()
            
            for i, (site1, lat1, lon1, objects1) in enumerate(location_data):
                if i in used_indices:
                    continue
                
                # Start a new group
                group = [(site1, lat1, lon1, objects1)]
                used_indices.add(i)
                
                # Find nearby locations
                for j, (site2, lat2, lon2, objects2) in enumerate(location_data):
                    if j in used_indices:
                        continue
                    
                    # Calculate distance if both have coordinates
                    if lat1 and lon1 and lat2 and lon2:
                        try:
                            lat1_f = float(lat1)
                            lon1_f = float(lon1)
                            lat2_f = float(lat2)
                            lon2_f = float(lon2)
                            
                            # Simple Euclidean distance in degrees
                            distance = ((lat2_f - lat1_f) ** 2 + (lon2_f - lon1_f) ** 2) ** 0.5
                            
                            if distance < threshold:
                                group.append((site2, lat2, lon2, objects2))
                                used_indices.add(j)
                        except (ValueError, TypeError):
                            pass
                    elif site1 and site2 and site1 == site2:
                        # Same site name but no coordinates, group them
                        group.append((site2, lat2, lon2, objects2))
                        used_indices.add(j)
                
                grouped_locations.append(group)
            
            # Display grouped locations
            for idx, group in enumerate(grouped_locations, 1):
                # Calculate average lat/lon and collect all objects
                lats = [lat for _, lat, _, _ in group if lat]
                lons = [lon for _, _, lon, _ in group if lon]
                all_objects = set()
                for _, _, _, objects in group:
                    all_objects.update(objects)
                
                avg_lat = sum(float(l) for l in lats) / len(lats) if lats else None
                avg_lon = sum(float(l) for l in lons) / len(lons) if lons else None
                
                # Use the most common site name (for reference, but not displayed)
                sites = [site for site, _, _, _ in group if site]
                site_name = max(set(sites), key=sites.count) if sites else None
                
                # Create location card
                loc_card = ctk.CTkFrame(locations_content, fg_color="gray20")
                loc_card.pack(fill="x", padx=10, pady=5)
                
                # Header row: location number + project count
                header_frame = ctk.CTkFrame(loc_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                # Check for saved tag
                tag = self.location_tags.get_tag(str(avg_lat), str(avg_lon))
                if tag:
                    display_name = f"⭐ {tag['name']}"
                else:
                    display_name = f"⭐ Location {idx}"
                
                location_label = ctk.CTkLabel(
                    header_frame,
                    text=display_name,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                location_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    header_frame,
                    text=f"{len(group)} projects",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                count_label.pack(side="right")
                
                # Coordinates row
                if avg_lat and avg_lon:
                    coord_textbox = ctk.CTkTextbox(loc_card, height=25)
                    coord_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    coord_textbox.insert("1.0", f"Lat: {avg_lat:.6f}, Lon: {avg_lon:.6f}")
                    coord_textbox.configure(state="disabled", font=ctk.CTkFont(size=12))
                
                # Objects row
                if all_objects:
                    obj_textbox = ctk.CTkTextbox(loc_card, height=30)
                    obj_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    obj_textbox.insert("1.0", f"Objects: {', '.join(sorted(all_objects))}")
                    obj_textbox.configure(state="disabled", font=ctk.CTkFont(size=12))
                
                # Google Maps button
                if avg_lat and avg_lon:
                    maps_button = ctk.CTkButton(
                        loc_card,
                        text="🗺️ Open in Google Maps",
                        font=ctk.CTkFont(size=12),
                        height=32,
                        fg_color="#4285F4",
                        hover_color="#3367D6",
                        command=lambda l=avg_lat, ln=avg_lon: self.open_google_maps(str(l), str(ln))
                    )
                    maps_button.pack(fill="x", padx=10, pady=(0, 5))
                
                # Tag button
                if avg_lat and avg_lon:
                    tag_button_text = "✏️ Edit Tag" if tag else "➕ Add Tag"
                    tag_button = ctk.CTkButton(
                        loc_card,
                        text=tag_button_text,
                        font=ctk.CTkFont(size=12),
                        height=32,
                        fg_color="#FFA500",
                        hover_color="#FF8C00",
                        command=lambda l=avg_lat, ln=avg_lon: self.open_tag_dialog(str(l), str(ln))
                    )
                    tag_button.pack(fill="x", padx=10, pady=(5, 10))
        else:
            no_loc_label = ctk.CTkLabel(locations_content, text="No capture locations found", font=ctk.CTkFont(size=14))
            no_loc_label.pack(padx=10, pady=10)
    
    def create_project_button(self, parent, project):
        """Create a clickable button for a single project."""
        button = ctk.CTkButton(
            parent,
            text=project['name'],
            font=ctk.CTkFont(size=14),
            height=40,
            command=lambda: self.show_project_details(project)
        )
        button.pack(fill="x", pady=5)
        return button
    
    def on_search_change(self, event):
        """Handle search text change to filter projects."""
        search_text = self.search_entry.get().lower()
        
        # Clear current project buttons (except aggregate stats and separator)
        children = self.scroll_frame.winfo_children()
        # Keep first 2 children (aggregate button and separator)
        for i, widget in enumerate(children):
            if i >= 2:
                widget.destroy()
        
        # Filter projects
        filtered_projects = []
        for project in self.all_projects:
            # Search in project name
            if search_text in project['name'].lower():
                filtered_projects.append(project)
                continue
            
            # Search in objects
            objects = project.get('objects', set())
            if any(search_text in obj.lower() for obj in objects):
                filtered_projects.append(project)
                continue
            
            # Search in site/location
            site = project.get('site', '')
            if site and search_text in site.lower():
                filtered_projects.append(project)
                continue
        
        # Re-add project buttons
        for project in filtered_projects:
            self.create_project_button(self.scroll_frame, project)
    
    def show_aggregate_stats(self):
        """Show aggregate statistics in the details panel."""
        # Clear previous details
        for widget in self.details_scroll.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(
            self.details_scroll,
            text="Aggregate Statistics",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Create aggregate stats display
        self.create_aggregate_stats(self.details_scroll)
    
    def open_file_explorer(self, path: str):
        """Open the given path in the system's file explorer."""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
            logger.info(f"Opened file explorer: {path}")
        except Exception as e:
            logger.error(f"Failed to open file explorer: {e}")
            messagebox.showerror("Error", f"Failed to open file explorer: {str(e)}")
    
    def open_google_maps(self, lat: str, lon: str):
        """Open Google Maps centered on the given coordinates."""
        import webbrowser
        try:
            url = f"https://www.google.com/maps?q={lat},{lon}"
            webbrowser.open(url)
            logger.info(f"Opened Google Maps for location: {lat}, {lon}")
        except Exception as e:
            logger.error(f"Failed to open Google Maps: {e}")
            messagebox.showerror("Error", f"Failed to open Google Maps: {str(e)}")
    
    def open_tag_dialog(self, lat: str, lon: str):
        """Open dialog to add/edit location tag."""
        tag = self.location_tags.get_tag(lat, lon)
        
        # Create tag dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Location Tag")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Name field
        name_label = ctk.CTkLabel(dialog, text="Location Name:", font=ctk.CTkFont(weight="bold"))
        name_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="e.g., Backyard Observatory")
        name_entry.pack(fill="x", padx=20, pady=(0, 10))
        if tag:
            name_entry.insert(0, tag['name'])
        
        # Notes field
        notes_label = ctk.CTkLabel(dialog, text="Notes (optional):", font=ctk.CTkFont(weight="bold"))
        notes_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        notes_textbox = ctk.CTkTextbox(dialog, height=100)
        notes_textbox.pack(fill="x", padx=20, pady=(0, 10))
        if tag and tag.get('notes'):
            notes_textbox.insert("1.0", tag['notes'])
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        def save_tag():
            name = name_entry.get().strip()
            notes = notes_textbox.get("1.0", "end").strip()
            
            if not name:
                messagebox.showerror("Error", "Location name is required")
                return
            
            self.location_tags.set_tag(lat, lon, name, notes)
            messagebox.showinfo("Success", "Location tag saved!")
            dialog.destroy()
            # Refresh the aggregate statistics view
            self.show_aggregate_stats()
        
        def delete_tag():
            if tag:
                if messagebox.askyesno("Confirm", "Delete this location tag?"):
                    self.location_tags.delete_tag(lat, lon)
                    messagebox.showinfo("Success", "Location tag deleted!")
                    dialog.destroy()
                    # Refresh the aggregate statistics view
                    self.show_aggregate_stats()
            else:
                messagebox.showinfo("Info", "No tag to delete")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            fg_color="#2E8B57",
            hover_color="#3CB371",
            command=save_tag
        )
        save_button.pack(side="left", padx=(0, 5))
        
        if tag:
            delete_button = ctk.CTkButton(
                button_frame,
                text="Delete",
                fg_color="#DC143C",
                hover_color="#B22222",
                command=delete_tag
            )
            delete_button.pack(side="left", padx=(0, 5))
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side="right")
    
    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string to human-readable format using configured timezone."""
        try:
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromisoformat(datetime_str)
            
            # Get timezone from settings
            tz_setting = self.settings.get_timezone()
            
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            if tz_setting == "UTC":
                # Keep as UTC
                dt_final = dt
            elif tz_setting == "EST":
                # Convert to EST (UTC-5)
                est = timezone(timedelta(hours=-5))
                dt_final = dt.astimezone(est)
            elif tz_setting == "Local":
                # Convert to local timezone
                dt_final = dt.astimezone()
            else:
                # Default to PST (UTC-8)
                pst = timezone(timedelta(hours=-8))
                dt_final = dt.astimezone(pst)
            
            return dt_final.strftime("%Y-%m-%d %I:%M %p")
        except Exception:
            return datetime_str
    
    def show_project_details(self, project):
        """Show detailed information for a selected project."""
        # Update details label with project name
        self.details_label.configure(text=f"Project Details - {project['name']}")
        
        # Clear previous details
        for widget in self.details_scroll.winfo_children():
            widget.destroy()
        
        # Track expandable sections for accordion behavior
        self.expandable_sections = []
        
        # Project summary (collapsible)
        summary_frame = ctk.CTkFrame(self.details_scroll)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        summary_button = ctk.CTkButton(
            summary_frame,
            text="▶ Project Summary",
            font=ctk.CTkFont(weight="bold"),
            height=35,
            command=lambda: self.toggle_expandable_section(summary_button, summary_content)
        )
        summary_button.pack(fill="x", padx=10, pady=(10, 5))
        
        summary_content = ctk.CTkFrame(summary_frame)
        summary_content.pack(fill="x", padx=10, pady=(0, 10))
        summary_content.pack_forget()  # Initially collapsed
        
        # Track this section for accordion behavior
        self.expandable_sections.append((summary_button, summary_content))
        
        # Frame counts
        counts_label = ctk.CTkLabel(summary_content, text="Frame Counts", font=ctk.CTkFont(weight="bold"))
        counts_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        counts_text = (
            f"Lights: {project['lights']} | "
            f"Darks: {project['darks']} | "
            f"Flats: {project['flats']} | "
            f"Bias: {project['bias']}"
        )
        counts_value = ctk.CTkTextbox(summary_content, height=30)
        counts_value.pack(fill="x", padx=10, pady=(0, 5))
        counts_value.insert("1.0", counts_text)
        counts_value.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # Exposure breakdown for lights
        if project.get('lights_by_exposure'):
            lights_exp_label = ctk.CTkLabel(summary_content, text="Lights by Exposure:", font=ctk.CTkFont(weight="bold"))
            lights_exp_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            for exp, count in sorted(project['lights_by_exposure'].items()):
                exp_textbox = ctk.CTkTextbox(summary_content, height=25)
                exp_textbox.pack(fill="x", padx=10, pady=1)
                exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                exp_textbox.configure(state="disabled", font=ctk.CTkFont(size=12))
        
        # Exposure breakdown for darks
        if project.get('darks_by_exposure'):
            darks_exp_label = ctk.CTkLabel(summary_content, text="Darks by Exposure:", font=ctk.CTkFont(weight="bold"))
            darks_exp_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            for exp, count in sorted(project['darks_by_exposure'].items()):
                exp_textbox = ctk.CTkTextbox(summary_content, height=25)
                exp_textbox.pack(fill="x", padx=10, pady=1)
                exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                exp_textbox.configure(state="disabled", font=ctk.CTkFont(size=12))
        
        # Integration time
        time_label = ctk.CTkLabel(summary_content, text="Total Integration Time", font=ctk.CTkFont(weight="bold"))
        time_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        total_seconds = project['integration_seconds']
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        time_value = ctk.CTkTextbox(summary_content, height=30)
        time_value.pack(fill="x", padx=10, pady=(0, 10))
        time_value.insert("1.0", f"{hours}h {minutes}m {seconds}s")
        time_value.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # File statistics
        file_label = ctk.CTkLabel(summary_content, text="File Statistics", font=ctk.CTkFont(weight="bold"))
        file_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        file_text = f"{project['total_files']} files | {project['total_size_mb']:.2f} MB"
        file_value = ctk.CTkTextbox(summary_content, height=30)
        file_value.pack(fill="x", padx=10, pady=(0, 10))
        file_value.insert("1.0", file_text)
        file_value.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # Filters
        if project['filters']:
            filter_label = ctk.CTkLabel(summary_content, text="Filters", font=ctk.CTkFont(weight="bold"))
            filter_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            filter_textbox = ctk.CTkTextbox(summary_content, height=30)
            filter_textbox.pack(fill="x", padx=10, pady=(0, 10))
            filter_textbox.insert("1.0", ', '.join(project['filters']))
            filter_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # Exposures
        if project['exposures']:
            exp_label = ctk.CTkLabel(summary_content, text="Exposure Times", font=ctk.CTkFont(weight="bold"))
            exp_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            exp_text = ', '.join([f"{e}s" for e in project['exposures']])
            exp_textbox = ctk.CTkTextbox(summary_content, height=30)
            exp_textbox.pack(fill="x", padx=10, pady=(0, 10))
            exp_textbox.insert("1.0", exp_text)
            exp_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
        
        # Path
        path_label = ctk.CTkLabel(summary_content, text="Project Path", font=ctk.CTkFont(weight="bold"))
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        path_textbox = ctk.CTkTextbox(summary_content, height=30)
        path_textbox.pack(fill="x", padx=10, pady=(0, 5))
        path_textbox.insert("1.0", project['path'])
        path_textbox.configure(state="disabled", font=ctk.CTkFont(size=12), text_color="gray")
        
        # Open in File Explorer button
        open_button = ctk.CTkButton(
            summary_content,
            text="� Open in File Explorer",
            font=ctk.CTkFont(size=12),
            height=32,
            command=lambda: self.open_file_explorer(project['path'])
        )
        open_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Individual sessions expandable sections
        if project.get('sessions'):
            for idx, (obj, start, end, lights, integration, exposures, lights_by_exposure) in enumerate(project['sessions']):
                session_frame = ctk.CTkFrame(self.details_scroll)
                session_frame.pack(fill="x", padx=10, pady=5)
                
                session_content = ctk.CTkFrame(session_frame)
                session_content.pack(fill="x", padx=10, pady=(0, 10))
                session_content.pack_forget()  # Initially collapsed
                
                session_button_text = f"▶ {obj} - Session {idx + 1}: {self._format_datetime(start)}"
                session_button = ctk.CTkButton(
                    session_frame,
                    text=session_button_text,
                    font=ctk.CTkFont(size=12),
                    height=35
                )
                session_button.pack(fill="x", padx=10, pady=(10, 5))
                session_button.configure(command=lambda btn=session_button, content=session_content: self.toggle_expandable_section(btn, content))
                
                # Track this section for accordion behavior
                self.expandable_sections.append((session_button, session_content))
                
                # Session details - Capture Location section (first)
                if project.get('latitude') and project.get('longitude'):
                    location_label = ctk.CTkLabel(session_content, text="Capture Location:", font=ctk.CTkFont(weight="bold"))
                    location_label.pack(anchor="w", padx=10, pady=(5, 2))
                    
                    tag = self.location_tags.get_tag(str(project['latitude']), str(project['longitude']))
                    if tag:
                        location_textbox = ctk.CTkTextbox(session_content, height=25)
                        location_textbox.pack(fill="x", padx=10, pady=(0, 2))
                        location_textbox.insert("1.0", f"⭐ {tag['name']}")
                        location_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                    
                    # Site
                    if project.get('site'):
                        site_textbox = ctk.CTkTextbox(session_content, height=25)
                        site_textbox.pack(fill="x", padx=10, pady=2)
                        site_textbox.insert("1.0", f"Site: {project['site']}")
                        site_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                    
                    # Coordinates
                    coord_textbox = ctk.CTkTextbox(session_content, height=25)
                    coord_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    coord_textbox.insert("1.0", f"Lat: {project['latitude']}, Lon: {project['longitude']}")
                    coord_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                    
                    # Tag button
                    tag_button_text = "✏️ Edit Tag" if tag else "➕ Add Tag"
                    tag_button = ctk.CTkButton(
                        session_content,
                        text=tag_button_text,
                        font=ctk.CTkFont(size=12),
                        height=32,
                        fg_color="#FFA500",
                        hover_color="#FF8C00",
                        command=lambda l=project['latitude'], ln=project['longitude']: self.open_tag_dialog(str(l), str(ln))
                    )
                    tag_button.pack(fill="x", padx=10, pady=(0, 5))
                    
                    # Google Maps button
                    maps_button = ctk.CTkButton(
                        session_content,
                        text="🗺️ Open in Google Maps",
                        font=ctk.CTkFont(size=12),
                        height=32,
                        fg_color="#4285F4",
                        hover_color="#3367D6",
                        command=lambda l=project['latitude'], ln=project['longitude']: self.open_google_maps(str(l), str(ln))
                    )
                    maps_button.pack(fill="x", padx=10, pady=(0, 10))
                
                # Time section
                time_label = ctk.CTkLabel(session_content, text="Time:", font=ctk.CTkFont(weight="bold"))
                time_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                start_textbox = ctk.CTkTextbox(session_content, height=25)
                start_textbox.pack(fill="x", padx=10, pady=2)
                start_textbox.insert("1.0", f"Start: {self._format_datetime(start)}")
                start_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                
                end_textbox = ctk.CTkTextbox(session_content, height=25)
                end_textbox.pack(fill="x", padx=10, pady=(0, 5))
                end_textbox.insert("1.0", f"End: {self._format_datetime(end)}")
                end_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                
                # Captures section
                captures_label = ctk.CTkLabel(session_content, text="Captures:", font=ctk.CTkFont(weight="bold"))
                captures_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                lights_textbox = ctk.CTkTextbox(session_content, height=25)
                lights_textbox.pack(fill="x", padx=10, pady=2)
                lights_textbox.insert("1.0", f"Lights: {lights}")
                lights_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                
                if integration > 0:
                    hours = int(integration // 3600)
                    minutes = int((integration % 3600) // 60)
                    seconds = int(integration % 60)
                    integration_text = f"{hours}h {minutes}m {seconds}s"
                    
                    integration_textbox = ctk.CTkTextbox(session_content, height=25)
                    integration_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    integration_textbox.insert("1.0", f"Integration: {integration_text}")
                    integration_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
                
                # Exposure breakdown section
                if lights_by_exposure:
                    exp_label = ctk.CTkLabel(session_content, text="Exposure Breakdown:", font=ctk.CTkFont(weight="bold"))
                    exp_label.pack(anchor="w", padx=10, pady=(5, 2))
                    
                    for exp, count in sorted(lights_by_exposure.items()):
                        exp_textbox = ctk.CTkTextbox(session_content, height=25)
                        exp_textbox.pack(fill="x", padx=10, pady=1)
                        exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                        exp_textbox.configure(state="disabled", font=ctk.CTkFont(size=12))
                
                if exposures:
                    exp_text = ', '.join([f"{e}s" for e in exposures])
                    exp_textbox = ctk.CTkTextbox(session_content, height=25)
                    exp_textbox.pack(fill="x", padx=10, pady=(2, 10))
                    exp_textbox.insert("1.0", f"Exposures: {exp_text}")
                    exp_textbox.configure(state="disabled", font=ctk.CTkFont(size=14))
    
    def toggle_expandable_section(self, button, content_frame):
        """Toggle visibility of an expandable section with accordion behavior."""
        if content_frame.winfo_ismapped():
            # Collapse this section
            content_frame.pack_forget()
            button.configure(text=button.cget("text").replace("▼", "▶"))
        else:
            # Collapse all other sections first (if accordion behavior is enabled)
            if hasattr(self, 'expandable_sections'):
                for other_button, other_content in self.expandable_sections:
                    try:
                        if other_content.winfo_ismapped() and other_content != content_frame:
                            other_content.pack_forget()
                            other_button.configure(text=other_button.cget("text").replace("▼", "▶"))
                    except Exception:
                        # Widget might be invalid, skip it
                        pass
            
            # Expand this section
            content_frame.pack(fill="x")
            button.configure(text=button.cget("text").replace("▶", "▼"))


def main():
    """Main entry point."""
    app = SeestarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
