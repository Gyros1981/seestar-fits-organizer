"""
Seestar FITS Organizer - Main Entry Point

A desktop application for organizing and analyzing astrophotography data
from Seestar telescopes. Provides tools for:
- Scanning and building projects from raw FITS data
- Analyzing existing projects with detailed statistics
- Managing location tags for capture sites
- Exporting analysis data to CSV

Usage:
    python main.py
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import logging
import shutil

# Import core business logic
from core import AppSettings, LocationTags, ProjectBuilder, ProjectAnalyzer

# Import UI components
from ui import DisclaimerWindow, FolderSelectionWindow, AnalysisWindow

logger = logging.getLogger(__name__)


class SeestarApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Seestar FITS Organizer")
        self.geometry("1200x800")
        
        # Directory paths
        self.seestar_dir = None
        self.raw_dir = None
        self.projects_dir = None
        self.analyze_projects_dir = None
        self.projects = []
        
        # Workflow configuration
        self.workflow_mode = "direct"  # "direct" or "intermediate"
        self.workflow_var = ctk.StringVar(value="direct")
        
        # Initialize settings
        self.settings = AppSettings()
        logger.info(f"Settings loaded from: {self.settings.storage_path}")
        logger.info(f"Settings: threshold={self.settings.get_location_threshold()}, "
                   f"timezone={self.settings.get_timezone()}, "
                   f"coord_format={self.settings.get_coordinate_format()}, "
                   f"disclaimer_ack={self.settings.get_disclaimer_acknowledged()}")
        
        # Show disclaimer if not acknowledged
        if not self.settings.get_disclaimer_acknowledged():
            self.show_disclaimer()
        
        self.setup_ui()
        
        # Set fullscreen/maximized window state
        self.state('zoomed')  # Windows maximized
        # Alternative: self.attributes('-fullscreen', True) for true fullscreen
        
        # Initialize workflow state (raw section is not packed by default for direct mode)
        pass  # raw_section_frame is not packed initially
    
    def show_disclaimer(self):
        """Show the disclaimer window."""
        DisclaimerWindow(self, self.settings)
    
    def set_ui_state(self, enabled: bool):
        """Enable or disable all UI buttons during processing."""
        state = "normal" if enabled else "disabled"
        
        # Directory browse buttons
        if hasattr(self, 'seestar_button'):
            self.seestar_button.configure(state=state)
        if hasattr(self, 'raw_button'):
            self.raw_button.configure(state=state)
        if hasattr(self, 'projects_button'):
            self.projects_button.configure(state=state)
        if hasattr(self, 'analyze_projects_button'):
            self.analyze_projects_button.configure(state=state)
        
        # Mode action buttons
        if hasattr(self, 'scan_build_action_btn'):
            self.scan_build_action_btn.configure(state=state)
        if hasattr(self, 'analyze_action_btn'):
            self.analyze_action_btn.configure(state=state)
    
    def setup_ui(self):
        """Setup the user interface."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container - no padding, tight layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Menu buttons packed directly into main_frame (no menu_frame wrapper)
        # Import Menu (for transferring files from Seestar)
        import_menu_btn = ctk.CTkButton(
            main_frame,
            text="� Import",
            font=ctk.CTkFont(size=12),
            width=80,
            command=self.show_import_menu
        )
        import_menu_btn.pack(side="top", anchor="w", padx=10, pady=(5, 0))
        
        # Tools Menu
        tools_menu_btn = ctk.CTkButton(
            main_frame,
            text="🔧 Tools",
            font=ctk.CTkFont(size=12),
            width=80,
            command=self.show_tools_menu
        )
        tools_menu_btn.place(x=100, y=5)
        
        # Settings Button (direct)
        settings_btn = ctk.CTkButton(
            main_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=12),
            width=100,
            command=lambda: self.show_mode('settings')
        )
        settings_btn.place(x=190, y=5)
        
        # Help Menu
        help_menu_btn = ctk.CTkButton(
            main_frame,
            text="❓ Help",
            font=ctk.CTkFont(size=12),
            width=80,
            command=self.show_help_menu
        )
        help_menu_btn.place(x=300, y=5)
        
        # Exit Button (right-aligned)
        exit_btn = ctk.CTkButton(
            main_frame,
            text="❌ Exit",
            font=ctk.CTkFont(size=12),
            width=80,
            fg_color="#C0392B",
            hover_color="#A93226",
            command=self.quit
        )
        exit_btn.place(relx=1.0, x=-90, y=5)
        
        # Initialize mode tracking
        self.current_mode = None  # None, 'scan_build', 'analyze', 'settings', or 'fits_viewer'
        
        # Content frame - main container for all views
        self.content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Normal mode panel (left side - for scan/build and analyze)
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Create mode frames (hidden initially)
        self._create_scan_build_frame()
        self._create_analyze_frame()
        self._create_planetary_scenery_frame()
        
        # Default/Welcome frame
        self.welcome_frame = ctk.CTkFrame(self.left_panel)
        self.welcome_frame.pack(fill="both", expand=True)
        
        welcome_title = ctk.CTkLabel(
            self.welcome_frame,
            text="Welcome to Seestar FITS Organizer",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_title.pack(pady=(50, 20))
        
        welcome_text = ctk.CTkLabel(
            self.welcome_frame,
            text="Select a mode from the menu above to get started:\n\n"
                 "📥 Import → 🔭 Direct (from Seestar)\n"
                 "📥 Import → 📁 Intermediate (via Raw)\n"
                 "📥 Import → 🌙 Copy Planetary & Scenery\n"
                 "🔧 Tools → 🪐 Analyze Projects\n"
                 "🔧 Tools → 🖼️ FITS Viewer\n"
                 "⚙️ Settings → Configure app settings",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        welcome_text.pack(pady=20)
        
        # Progress Frame (always visible at bottom of left panel)
        self.progress_frame = ctk.CTkFrame(self.left_panel)
        self.progress_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Ready", text_color="gray")
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Right panel - Console Output
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        console_label = ctk.CTkLabel(self.right_panel, text="Console Output", font=ctk.CTkFont(size=14, weight="bold"))
        console_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.console_text = ctk.CTkTextbox(self.right_panel)
        self.console_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.console_text.configure(state="disabled")
        
        # Settings frame - full width (spans both columns)
        self._create_settings_frame()
        
        # FITS Viewer frame
        self._create_fits_viewer_frame()
        
        # About frame
        self._create_about_frame()
        
        # Redirect logging to console
        self.setup_console_logging()
        
        # Bind click to close menus when clicking outside them
        self.bind("<Button-1>", self.close_menus_on_click)
    
    def setup_console_logging(self):
        """Setup custom logging handler to redirect output to console."""
        
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
        directory = filedialog.askdirectory(title="Select Seestar MyWork Directory")
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
    
    def select_analyze_projects_dir(self):
        """Select projects directory for analysis."""
        directory = filedialog.askdirectory(title="Select Projects Directory for Analysis")
        if directory:
            self.analyze_projects_dir = Path(directory)
            self.analyze_projects_path_label.configure(text=str(self.analyze_projects_dir), text_color="white")
            logger.info(f"Selected analyze projects directory: {self.analyze_projects_dir}")
    
    def select_ps_source_dir(self):
        """Select Seestar MyWorks directory for Planetary & Scenery copy."""
        directory = filedialog.askdirectory(title="Select Seestar MyWorks Directory")
        if directory:
            self.ps_source_dir = Path(directory)
            self.ps_source_path_label.configure(text=str(self.ps_source_dir), text_color="white")
            logger.info(f"Selected Planetary & Scenery source: {self.ps_source_dir}")
    
    def select_ps_target_dir(self):
        """Select target directory for Planetary & Scenery copy."""
        directory = filedialog.askdirectory(title="Select Target Directory for Planetary & Scenery")
        if directory:
            self.ps_target_dir = Path(directory)
            self.ps_target_path_label.configure(text=str(self.ps_target_dir), text_color="white")
            logger.info(f"Selected Planetary & Scenery target: {self.ps_target_dir}")
    
    def start_scan(self):
        """Start scanning and building projects in a separate thread."""
        # Validate directories based on workflow mode
        if self.workflow_mode == "direct":
            if not self.seestar_dir:
                messagebox.showerror("Error", "Please select Seestar directory")
                return
            if not self.projects_dir:
                messagebox.showerror("Error", "Please select Projects directory")
                return
        else:  # intermediate workflow
            if not self.seestar_dir:
                messagebox.showerror("Error", "Please select Seestar directory")
                return
            if not self.raw_dir:
                messagebox.showerror("Error", "Please select Raw directory")
                return
            if not self.projects_dir:
                messagebox.showerror("Error", "Please select Projects directory")
                return
        
        self.set_ui_state(False)
        self.progress_label.configure(text="Scanning and building projects...")
        
        thread = threading.Thread(target=self.scan_and_build)
        thread.daemon = True
        thread.start()
    
    def start_analysis(self):
        """Start analysis of existing projects."""
        if not self.analyze_projects_dir:
            messagebox.showerror("Error", "Please select Projects directory for analysis")
            return
        
        self.set_ui_state(False)
        self.progress_label.configure(text="Analyzing projects...")
        
        thread = threading.Thread(target=self.analyze_projects)
        thread.daemon = True
        thread.start()
    
    def start_planetary_scenery_copy(self):
        """Start copying Planetary & Scenery media in a separate thread."""
        if not hasattr(self, 'ps_source_dir') or not self.ps_source_dir:
            messagebox.showerror("Error", "Please select Seestar MyWorks directory")
            return
        if not hasattr(self, 'ps_target_dir') or not self.ps_target_dir:
            messagebox.showerror("Error", "Please select target directory")
            return
        
        self.set_ui_state(False)
        self.progress_label.configure(text="Copying Planetary & Scenery media...")
        
        thread = threading.Thread(target=self.copy_planetary_scenery)
        thread.daemon = True
        thread.start()
    
    def scan_and_build(self):
        """Scan and build projects."""
        try:
            source_dir = self.raw_dir  # Default to raw_dir for intermediate workflow
            
            if self.workflow_mode == "intermediate":
                # Step 1: Discover folders in Seestar and ask which to copy
                self.after(0, lambda: self.progress_label.configure(text="Discovering folders in Seestar..."))
                
                # Scan for folders in Seestar directory
                seestar_folders = []
                for item in self.seestar_dir.iterdir():
                    if item.is_dir() and (item.name.endswith('_subs') or item.name.endswith('_sub')):
                        seestar_folders.append(item)
                
                if not seestar_folders:
                    self.after(0, lambda: self.progress_label.configure(text="No *_subs folders found in Seestar"))
                    self.after(0, lambda: self.set_ui_state(True))
                    return
                
                # Show folder selection dialog for copying (thread-safe)
                selected_folders = []
                dialog_result = threading.Event()
                
                def show_folder_dialog():
                    nonlocal selected_folders
                    dialog = FolderSelectionWindow(self, seestar_folders)
                    dialog.wait_window()
                    if dialog.result == "process":
                        selected_folders = dialog.get_selected_folders()
                    dialog_result.set()
                
                # Show dialog on main thread and wait for result
                self.after(0, show_folder_dialog)
                dialog_result.wait()
                
                if not selected_folders:
                    self.after(0, lambda: self.progress_label.configure(text="No folders selected. Cancelled."))
                    self.after(0, lambda: self.set_ui_state(True))
                    return
                
                # Step 2: Copy selected folders from Seestar to Raw
                self.after(0, lambda: self.progress_label.configure(text=f"Copying {len(selected_folders)} folders to Raw..."))
                self.copy_seestar_to_raw(selected_folders)
                
                # For intermediate workflow, use the same selected folders (now in Raw) without asking again
                # Convert Seestar folder paths to Raw folder paths
                raw_folders = [self.raw_dir / folder.name for folder in selected_folders]
                build_folders = raw_folders
                source_dir = self.raw_dir
            else:
                # Direct workflow: use Seestar directory as source
                source_dir = self.seestar_dir
                self.after(0, lambda: self.progress_label.configure(text="Building projects from Seestar..."))
            
            # Step 3: Build projects from source to Projects
            builder = ProjectBuilder(source_dir, self.projects_dir)
            
            # For direct workflow, show folder selection; for intermediate, use already-selected folders
            if self.workflow_mode == "direct":
                self.after(0, lambda: self.progress_label.configure(text="Discovering folders..."))
                folders = builder.scan_raw_folders()
                total_folders = len(folders)
                
                if total_folders == 0:
                    self.after(0, lambda: self.progress_label.configure(text="No *_subs folders found in source"))
                    self.after(0, lambda: self.set_ui_state(True))
                    return
                
                # Show folder selection dialog (thread-safe)
                selected_folders = []
                dialog_result = threading.Event()
                
                def show_folder_dialog():
                    nonlocal selected_folders
                    dialog = FolderSelectionWindow(self, folders)
                    dialog.wait_window()
                    if dialog.result == "process":
                        selected_folders = dialog.get_selected_folders()
                    dialog_result.set()
                
                # Show dialog on main thread and wait for result
                self.after(0, show_folder_dialog)
                dialog_result.wait()
                
                if not selected_folders:
                    self.after(0, lambda: self.progress_label.configure(text="No folders selected. Cancelled."))
                    self.after(0, lambda: self.set_ui_state(True))
                    return
                
                build_folders = selected_folders
            else:
                # Intermediate workflow: use the folders we already selected and copied
                self.after(0, lambda: self.progress_label.configure(text="Discovering folders in Raw..."))
                # Verify the folders exist in Raw
                build_folders = [f for f in build_folders if f.exists()]
            
            # Process only selected folders
            self.after(0, lambda: self.progress_label.configure(text=f"Building {len(selected_folders)} projects..."))
            self.projects = []
            
            for i, folder in enumerate(selected_folders):
                self.after(0, lambda idx=i, total=len(selected_folders), fld=folder: 
                          self.progress_label.configure(text=f"Processing {fld.name} ({idx+1}/{total})"))
                
                project = builder.build_project(folder)
                self.projects.append(project)
            
            self.after(0, lambda: self.progress_label.configure(text=f"Completed! Built {len(self.projects)} projects"))
            
            # Show completion dialog
            self.after(0, lambda: messagebox.showinfo(
                "Processing Complete",
                f"Successfully built {len(self.projects)} project(s):\n\n" +
                "\n".join([f"  • {p.name}" for p in self.projects])
            ))
            
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to scan: {str(e)}"))
        
        finally:
            self.after(0, lambda: self.set_ui_state(True))
    
    def copy_seestar_to_raw(self, folders=None):
        """Copy <NAME>_sub folders from Seestar to Raw directory.
        
        Args:
            folders: Optional list of specific folders to copy. If None, copies all folders.
        """
        if not self.seestar_dir or not self.raw_dir:
            return
        
        # If no specific folders provided, scan for all folders
        if folders is None:
            folders = []
            for item in self.seestar_dir.iterdir():
                if item.is_dir() and (item.name.endswith('_subs') or item.name.endswith('_sub')):
                    folders.append(item)
        
        logger.info(f"Copying {len(folders)} folders from Seestar to Raw")
        
        for folder in folders:
            # Create corresponding folder in Raw
            raw_folder = self.raw_dir / folder.name
            raw_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy all FITS files
            fits_files = list(folder.glob('*.fits')) + list(folder.glob('*.FIT'))
            
            files_copied = 0
            files_skipped = 0
            
            for fits_file in fits_files:
                dest_file = raw_folder / fits_file.name
                
                if dest_file.exists():
                    # Compare file sizes
                    src_size = fits_file.stat().st_size
                    dest_size = dest_file.stat().st_size
                    
                    if src_size == dest_size:
                        files_skipped += 1
                        continue
                
                # Copy the file
                shutil.copy2(fits_file, dest_file)
                files_copied += 1
            
            logger.info(f"Folder {folder.name}: {files_copied} files copied, {files_skipped} files skipped")
    
    def analyze_projects(self):
        """Analyze existing projects and show results."""
        try:
            analyzer = ProjectAnalyzer(self.analyze_projects_dir)
            results = analyzer.analyze_all()
            
            # Update UI on main thread
            self.after(0, lambda: self.progress_label.configure(
                text=f"Analysis complete: {results.total_projects} projects, {results.total_lights} lights"
            ))
            
            # Show results window on main thread
            self.after(0, lambda: self.show_analysis_window(results.to_dict()))
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            self.after(0, lambda: self.progress_label.configure(text=f"Error: {str(e)}"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to analyze projects: {str(e)}"))
        
        finally:
            self.after(0, lambda: self.set_ui_state(True))
    
    def copy_planetary_scenery(self):
        """Copy Planetary & Scenery media from Seestar to target."""
        try:
            # Media folders to look for
            media_folders = [
                'Planetary_video', 'Planetary_photo',
                'Solar_video', 'Solar_photo',
                'Scenery_video', 'Scenery_photo',
                'Lunar_video', 'Lunar_photo'
            ]
            
            total_files = 0
            copied_files = 0
            skipped_files = 0
            
            for folder_name in media_folders:
                source_folder = self.ps_source_dir / folder_name
                if not source_folder.exists():
                    continue
                
                # Create target folder
                target_folder = self.ps_target_dir / folder_name
                target_folder.mkdir(parents=True, exist_ok=True)
                
                # Copy all files (images and videos)
                for item in source_folder.iterdir():
                    if item.is_file():
                        total_files += 1
                        dest_file = target_folder / item.name
                        
                        if dest_file.exists():
                            # Compare sizes
                            if item.stat().st_size == dest_file.stat().st_size:
                                skipped_files += 1
                                continue
                        
                        shutil.copy2(item, dest_file)
                        copied_files += 1
                
                self.after(0, lambda f=folder_name, c=copied_files, s=skipped_files: 
                    self.progress_label.configure(
                        text=f"Copied {f}: {c} new, {s} skipped"
                    ))
            
            # Show completion
            self.after(0, lambda: self.progress_label.configure(
                text=f"✓ Copied {copied_files} files, skipped {skipped_files}"
            ))
            
            self.after(0, lambda: messagebox.showinfo(
                "Copy Complete",
                f"Planetary & Scenery copy complete!\n"
                f"Copied: {copied_files} files\n"
                f"Skipped (already exist): {skipped_files} files"
            ))
            
        except Exception as e:
            logger.error(f"Error copying Planetary & Scenery: {e}")
            self.after(0, lambda: self.progress_label.configure(text=f"Error: {str(e)}"))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to copy media: {str(e)}"))
        
        finally:
            self.after(0, lambda: self.set_ui_state(True))
    
    def show_analysis_window(self, results):
        """Show analysis results in a new window."""
        location_tags = LocationTags()
        AnalysisWindow(self, results, self.settings, location_tags)
    
    def _create_scan_build_frame(self):
        """Create Scan & Build mode frame (hidden initially)."""
        self.scan_build_frame = ctk.CTkFrame(self.left_panel)
        
        # Store references to frame widgets
        self.scan_build_widgets = {}
        
        # Dynamic title (updated based on workflow mode)
        self.scan_build_title = ctk.CTkLabel(self.scan_build_frame, text="Direct Copy", font=ctk.CTkFont(size=16, weight="bold"))
        self.scan_build_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Dynamic explanation (updated based on workflow mode)
        self.scan_build_explanation = ctk.CTkLabel(
            self.scan_build_frame,
            text="Copy FITS files directly from Seestar device to project folders. This mode skips the intermediate Raw directory.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=900,
            justify="left"
        )
        self.scan_build_explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Seestar Device Directory
        seestar_label = ctk.CTkLabel(self.scan_build_frame, text="Seestar MyWork Directory:", font=ctk.CTkFont(weight="bold"))
        seestar_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        seestar_button_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        seestar_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.seestar_path_label = ctk.CTkLabel(seestar_button_frame, text="Not selected", text_color="gray")
        self.seestar_path_label.pack(side="left", padx=(0, 10))
        
        self.seestar_button = ctk.CTkButton(seestar_button_frame, text="🌌 Browse", command=self.select_seestar_dir, width=100)
        self.seestar_button.pack(side="right")
        
        # Raw Directory Section (hidden initially)
        self.raw_section_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        
        raw_label = ctk.CTkLabel(self.raw_section_frame, text="Raw Directory (Intermediate):", font=ctk.CTkFont(weight="bold"))
        raw_label.pack(anchor="w", pady=(10, 0))
        
        raw_button_frame = ctk.CTkFrame(self.raw_section_frame, fg_color="transparent")
        raw_button_frame.pack(fill="x", pady=(5, 10))
        
        self.raw_path_label = ctk.CTkLabel(raw_button_frame, text="Not selected", text_color="gray")
        self.raw_path_label.pack(side="left", padx=(0, 10))
        
        self.raw_button = ctk.CTkButton(raw_button_frame, text="🌌 Browse", command=self.select_raw_dir, width=100)
        self.raw_button.pack(side="right")
        
        # Projects Directory
        self.projects_label = ctk.CTkLabel(self.scan_build_frame, text="Projects Directory:", font=ctk.CTkFont(weight="bold"))
        self.projects_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        projects_button_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        projects_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.projects_path_label = ctk.CTkLabel(projects_button_frame, text="Not selected", text_color="gray")
        self.projects_path_label.pack(side="left", padx=(0, 10))
        
        self.projects_button = ctk.CTkButton(projects_button_frame, text="🌌 Browse", command=self.select_projects_dir, width=100)
        self.projects_button.pack(side="right")
        
        # Start Button
        self.scan_build_action_btn = ctk.CTkButton(
            self.scan_build_frame,
            text="🔭 Start Import",
            command=self.start_scan,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.scan_build_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_analyze_frame(self):
        """Create Analyze mode frame (hidden initially)."""
        self.analyze_frame = ctk.CTkFrame(self.left_panel)
        
        analyze_label = ctk.CTkLabel(self.analyze_frame, text="Analyze Existing Projects", font=ctk.CTkFont(size=16, weight="bold"))
        analyze_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Projects Directory (for analysis)
        analyze_projects_label = ctk.CTkLabel(self.analyze_frame, text="Projects Directory:", font=ctk.CTkFont(weight="bold"))
        analyze_projects_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        analyze_projects_button_frame = ctk.CTkFrame(self.analyze_frame, fg_color="transparent")
        analyze_projects_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.analyze_projects_path_label = ctk.CTkLabel(analyze_projects_button_frame, text="Not selected", text_color="gray")
        self.analyze_projects_path_label.pack(side="left", padx=(0, 10))
        
        self.analyze_projects_button = ctk.CTkButton(analyze_projects_button_frame, text="🌌 Browse", command=self.select_analyze_projects_dir, width=100)
        self.analyze_projects_button.pack(side="right")
        
        # Start Button
        self.analyze_action_btn = ctk.CTkButton(
            self.analyze_frame,
            text="🪐 Start Analysis",
            command=self.start_analysis,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.analyze_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_planetary_scenery_frame(self):
        """Create Planetary & Scenery copy mode frame (hidden initially)."""
        self.planetary_scenery_frame = ctk.CTkFrame(self.left_panel)
        
        ps_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Copy Planetary & Scenery Media", font=ctk.CTkFont(size=16, weight="bold"))
        ps_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        explanation = ctk.CTkLabel(
            self.planetary_scenery_frame,
            text="Copy Solar, Lunar, Planetary, and Scenery images and videos from Seestar MyWorks to a target directory. "
                 "This mode handles the non-FITS media files that are not part of the deep sky astrophotography workflow.\n\n"
                 "The following folders will be copied if they exist:\n"
                 "• Planetary_video, Planetary_photo\n"
                 "• Solar_video, Solar_photo\n"
                 "• Lunar_video, Lunar_photo\n"
                 "• Scenery_video, Scenery_photo\n\n"
                 "Files are only copied if they don't already exist at the destination (matching file size).",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=900,
            justify="left"
        )
        explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Source: Seestar MyWorks Directory
        source_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Seestar MyWorks Directory:", font=ctk.CTkFont(weight="bold"))
        source_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        source_button_frame = ctk.CTkFrame(self.planetary_scenery_frame, fg_color="transparent")
        source_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ps_source_path_label = ctk.CTkLabel(source_button_frame, text="Not selected", text_color="gray")
        self.ps_source_path_label.pack(side="left", padx=(0, 10))
        
        self.ps_source_button = ctk.CTkButton(source_button_frame, text="🌌 Browse", command=self.select_ps_source_dir, width=100)
        self.ps_source_button.pack(side="right")
        
        # Target: Destination Directory
        target_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Target Directory:", font=ctk.CTkFont(weight="bold"))
        target_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        target_button_frame = ctk.CTkFrame(self.planetary_scenery_frame, fg_color="transparent")
        target_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ps_target_path_label = ctk.CTkLabel(target_button_frame, text="Not selected", text_color="gray")
        self.ps_target_path_label.pack(side="left", padx=(0, 10))
        
        self.ps_target_button = ctk.CTkButton(target_button_frame, text="🌌 Browse", command=self.select_ps_target_dir, width=100)
        self.ps_target_button.pack(side="right")
        
        # Start Button
        self.ps_action_btn = ctk.CTkButton(
            self.planetary_scenery_frame,
            text="🌙 Copy Planetary & Scenery",
            command=self.start_planetary_scenery_copy,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.ps_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_fits_viewer_frame(self):
        """Create FITS Viewer mode frame (hidden initially)."""
        self.fits_viewer_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title_label = ctk.CTkLabel(self.fits_viewer_frame, text="🖼️ FITS Viewer", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Directory selection frame
        dir_frame = ctk.CTkFrame(self.fits_viewer_frame)
        dir_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.fits_viewer_dir_label = ctk.CTkLabel(dir_frame, text="No directory selected", text_color="gray")
        self.fits_viewer_dir_label.pack(side="left", padx=10, pady=10)
        
        browse_btn = ctk.CTkButton(dir_frame, text="📁 Browse", command=self.browse_fits_directory, width=100)
        browse_btn.pack(side="right", padx=10, pady=10)
        
        # Main content - split view
        content_frame = ctk.CTkFrame(self.fits_viewer_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - file list
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        list_label = ctk.CTkLabel(left_panel, text="FITS Files", font=ctk.CTkFont(size=12, weight="bold"))
        list_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=5)
        
        self.mark_btn = ctk.CTkButton(action_frame, text="✓ Mark", command=self.toggle_mark_selected, width=80, font=ctk.CTkFont(size=11))
        self.mark_btn.pack(side="left", padx=2)
        
        self.clear_marks_btn = ctk.CTkButton(action_frame, text="⬜ Clear Marks", command=self.clear_all_marks, width=100, font=ctk.CTkFont(size=11))
        self.clear_marks_btn.pack(side="left", padx=2)
        
        self.delete_marked_btn = ctk.CTkButton(action_frame, text="🗑️ Delete Marked", command=self.delete_marked_fits, width=110, font=ctk.CTkFont(size=11), fg_color="#C0392B", hover_color="#A93226")
        self.delete_marked_btn.pack(side="right", padx=2)
        
        # File list using tk.Listbox for performance
        import tkinter as tk
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.fits_file_listbox = tk.Listbox(
            list_frame,
            selectmode="single",
            font=("Segoe UI", 11),
            bg="#2B2B2B",
            fg="white",
            selectbackground="#1E90FF",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"  # No underline on active item
        )
        self.fits_file_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.fits_file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.fits_file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.fits_file_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Right panel - preview
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        preview_label = ctk.CTkLabel(right_panel, text="Preview", font=ctk.CTkFont(size=12, weight="bold"))
        preview_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Filename label (updates when file selected)
        self.fits_preview_filename = ctk.CTkLabel(right_panel, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.fits_preview_filename.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.fits_preview_label = ctk.CTkLabel(right_panel, text="Select a FITS file to preview", text_color="gray")
        self.fits_preview_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status bar
        self.fits_status_label = ctk.CTkLabel(self.fits_viewer_frame, text="Ready", text_color="gray")
        self.fits_status_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Bind keyboard navigation
        self.bind("<Up>", lambda e: self.navigate_fits_files(-1))
        self.bind("<Down>", lambda e: self.navigate_fits_files(1))
        
        # Initialize viewer state
        self.current_fits_directory = None
        self.fits_files = []
        self.selected_fits_index = -1
        self.marked_for_deletion = set()  # Set of indices marked for deletion
    
    def browse_fits_directory(self):
        """Browse for a directory containing FITS files."""
        directory = filedialog.askdirectory(title="Select Directory with FITS Files")
        if directory:
            self.load_fits_directory(directory)
    
    def load_fits_directory(self, directory):
        """Load FITS files from a directory."""
        # Clear UI state first
        self.selected_fits_index = -1
        self.marked_for_deletion = set()
        self.fits_preview_label.configure(text="Select a FITS file to preview", image=None)
        
        self.current_fits_directory = directory
        self.fits_viewer_dir_label.configure(text=directory)
        
        # Find all FITS files
        path = Path(directory)
        self.fits_files = sorted([f for f in path.iterdir() if f.is_file() and f.suffix.lower() in ['.fits', '.fit']])
        
        self.refresh_fits_file_list()
        
        # Auto-select and preview first file if any exist
        if self.fits_files:
            self.selected_fits_index = 0
            self.fits_file_listbox.selection_set(0)
            self.show_fits_preview(self.fits_files[0])
            self.fits_status_label.configure(text=f"{len(self.fits_files)} FITS files found - Showing {self.fits_files[0].name}")
        else:
            self.fits_status_label.configure(text="No FITS files found")
    
    def refresh_fits_file_list(self):
        """Refresh the file list display with marked status."""
        # Clear listbox
        self.fits_file_listbox.delete(0, "end")
        
        # Add files with mark indicator
        for i, file_path in enumerate(self.fits_files):
            if i in self.marked_for_deletion:
                display_text = f"[✓] {file_path.name}"
            else:
                display_text = f"[ ] {file_path.name}"
            self.fits_file_listbox.insert("end", display_text)
    
    
    def on_listbox_select(self, event):
        """Handle listbox selection change from mouse click."""
        selection = self.fits_file_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_fits_index = index
            file_path = self.fits_files[index]
            self.show_fits_preview(file_path)
            self.fits_status_label.configure(text=f"Selected: {file_path.name}")
    
    def navigate_fits_files(self, direction):
        """Navigate through FITS files with keyboard."""
        if not self.fits_files:
            return
        
        # Calculate new index from current selection
        current = self.selected_fits_index
        if current < 0:
            current = 0
            
        new_index = current + direction
        new_index = max(0, min(new_index, len(self.fits_files) - 1))
        
        if new_index != self.selected_fits_index:
            self.selected_fits_index = new_index
            self.fits_file_listbox.selection_clear(0, "end")
            self.fits_file_listbox.selection_set(new_index)
            self.fits_file_listbox.see(new_index)
            file_path = self.fits_files[new_index]
            self.show_fits_preview(file_path)
            self.fits_status_label.configure(text=f"Selected: {file_path.name}")
    
    def toggle_mark_selected(self):
        """Toggle mark for deletion on currently selected file."""
        selection = self.fits_file_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a file first to mark/unmark it.")
            return
        
        index = selection[0]
        if index in self.marked_for_deletion:
            self.marked_for_deletion.remove(index)
            self.fits_status_label.configure(text=f"Unmarked: {self.fits_files[index].name}")
        else:
            self.marked_for_deletion.add(index)
            self.fits_status_label.configure(text=f"Marked for deletion: {self.fits_files[index].name}")
        
        self.refresh_fits_file_list()
    
    def clear_all_marks(self):
        """Clear all deletion marks."""
        self.marked_for_deletion.clear()
        self.refresh_fits_file_list()
        self.fits_status_label.configure(text="All marks cleared")
    
    def delete_marked_fits(self):
        """Delete all marked FITS files."""
        if not self.marked_for_deletion:
            messagebox.showwarning("No Files Marked", "No files marked for deletion. Use 'Mark' button to mark files.")
            return
        
        marked_indices = sorted(self.marked_for_deletion)
        count = len(marked_indices)
        
        # Show list of files to be deleted
        if count <= 5:
            file_list = "\n".join([f"  - {self.fits_files[i].name}" for i in marked_indices])
        else:
            file_list = "\n".join([f"  - {self.fits_files[i].name}" for i in marked_indices[:5]])
            file_list += f"\n  ... and {count - 5} more files"
        
        msg = f"Delete {count} marked file(s)?\n\n{file_list}"
        
        if not messagebox.askyesno("Confirm Delete", msg + "\n\nThis action cannot be undone!"):
            return
        
        # Delete files
        deleted = 0
        failed = 0
        # Delete in reverse order to maintain index validity
        for i in reversed(marked_indices):
            try:
                file_path = self.fits_files[i]
                file_path.unlink()
                deleted += 1
            except Exception as e:
                logger.error(f"Failed to delete {self.fits_files[i]}: {e}")
                failed += 1
        
        # Reload directory
        self.load_fits_directory(self.current_fits_directory)
        
        # Show result
        if failed == 0:
            self.fits_status_label.configure(text=f"✓ Deleted {deleted} file(s)")
        else:
            self.fits_status_label.configure(text=f"Deleted {deleted}, failed {failed}")
    
    def show_fits_preview(self, file_path):
        """Show preview of a FITS file."""
        # Clear any existing image from label first, then clear our reference
        if hasattr(self, 'fits_preview_label') and self.fits_preview_label.winfo_exists():
            try:
                # Access internal _label to safely clear image
                self.fits_preview_label._label.configure(image='')
            except:
                pass
        self._current_fits_image = None
        
        try:
            # Update filename label
            if hasattr(self, 'fits_preview_filename') and self.fits_preview_filename.winfo_exists():
                self.fits_preview_filename.configure(text=file_path.name)
            
            from astropy.io import fits
            from PIL import Image
            import numpy as np
            
            # Load FITS data
            with fits.open(file_path) as hdul:
                data = hdul[0].data
                
                if data is None:
                    if hasattr(self, 'fits_preview_label') and self.fits_preview_label.winfo_exists():
                        self.fits_preview_label.configure(text="No image data")
                    return
                
                # Normalize for display
                if data.ndim == 2:
                    # Single channel image
                    norm_data = self._normalize_for_display(data)
                    img = Image.fromarray((norm_data * 255).astype(np.uint8))
                elif data.ndim == 3:
                    # Multi-channel, use first channel
                    norm_data = self._normalize_for_display(data[0])
                    img = Image.fromarray((norm_data * 255).astype(np.uint8))
                else:
                    if hasattr(self, 'fits_preview_label') and self.fits_preview_label.winfo_exists():
                        self.fits_preview_label.configure(text="Unsupported image format")
                    return
                
                # Resize to fit preview area (max 800x650)
                img.thumbnail((800, 650), Image.Resampling.LANCZOS)
                
                # Convert to CTkImage
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                
                # Keep reference to prevent garbage collection
                self._current_fits_image = ctk_img
                
                if hasattr(self, 'fits_preview_label') and self.fits_preview_label.winfo_exists():
                    self.fits_preview_label.configure(text="", image=ctk_img)
                
        except Exception as e:
            logger.error(f"Error loading FITS preview: {e}")
            if hasattr(self, 'fits_preview_label') and self.fits_preview_label.winfo_exists():
                self.fits_preview_label.configure(text=f"Error loading preview:\n{str(e)[:100]}")
    
    def _normalize_for_display(self, data):
        """Normalize image data for display."""
        import numpy as np
        
        # Remove NaN and Inf
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
        
        # Use percentiles for better contrast
        vmin = np.percentile(data, 1)
        vmax = np.percentile(data, 99)
        
        if vmax > vmin:
            normalized = (data - vmin) / (vmax - vmin)
        else:
            normalized = np.zeros_like(data)
        
        return np.clip(normalized, 0, 1)

    def _create_settings_frame(self):
        """Create Settings mode frame (hidden initially)."""
        self.settings_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=16, weight="bold"))
        settings_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Scrollable frame for settings content - fill all available space
        scroll_frame = ctk.CTkScrollableFrame(self.settings_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Location Settings Section
        location_frame = ctk.CTkFrame(scroll_frame)
        location_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        location_label = ctk.CTkLabel(location_frame, text="Location Settings", font=ctk.CTkFont(size=14, weight="bold"))
        location_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Location grouping threshold
        threshold_label = ctk.CTkLabel(location_frame, text="Location Grouping Threshold (degrees):")
        threshold_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.settings_threshold_entry = ctk.CTkEntry(location_frame)
        self.settings_threshold_entry.pack(fill="x", padx=10, pady=(0, 5))
        self.settings_threshold_entry.insert("0", str(self.settings.get_location_threshold()))
        
        threshold_help = ctk.CTkLabel(
            location_frame,
            text="Locations within this distance will be grouped together (default: 0.005 ≈ 600 yards)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        threshold_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Timezone Settings Section
        timezone_frame = ctk.CTkFrame(scroll_frame)
        timezone_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        timezone_label = ctk.CTkLabel(timezone_frame, text="Timezone Settings", font=ctk.CTkFont(size=14, weight="bold"))
        timezone_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        tz_label = ctk.CTkLabel(timezone_frame, text="Display Timezone:")
        tz_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.settings_timezone_menu = ctk.CTkOptionMenu(
            timezone_frame,
            values=["UTC", "PST (UTC-8)", "EST (UTC-5)", "Local"]
        )
        self.settings_timezone_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Map timezone setting to menu value
        tz_setting = self.settings.get_timezone()
        logger.info(f"Loading timezone setting: {tz_setting}")
        if tz_setting == "UTC":
            self.settings_timezone_menu.set("UTC")
        elif tz_setting == "EST":
            self.settings_timezone_menu.set("EST (UTC-5)")
        elif tz_setting == "Local":
            self.settings_timezone_menu.set("Local")
        else:
            self.settings_timezone_menu.set("PST (UTC-8)")
        logger.info(f"Timezone menu set to: {self.settings_timezone_menu.get()}")
        
        # Coordinate Format Section
        coord_frame = ctk.CTkFrame(scroll_frame)
        coord_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        coord_label = ctk.CTkLabel(coord_frame, text="Coordinate Format", font=ctk.CTkFont(size=14, weight="bold"))
        coord_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        coord_menu_label = ctk.CTkLabel(coord_frame, text="RA/DEC Display Format:")
        coord_menu_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.settings_coord_menu = ctk.CTkOptionMenu(
            coord_frame,
            values=["Decimal Degrees", "Hours/Minutes/Seconds (RA) + DMS (DEC)"]
        )
        self.settings_coord_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Map coordinate format setting to menu value
        coord_setting = self.settings.get_coordinate_format()
        if coord_setting == "hms":
            self.settings_coord_menu.set("Hours/Minutes/Seconds (RA) + DMS (DEC)")
        else:
            self.settings_coord_menu.set("Decimal Degrees")
        
        coord_help = ctk.CTkLabel(
            coord_frame,
            text="'Hours/Minutes/Seconds' shows RA as HH:MM:SS and DEC as DD:MM:SS",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        coord_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Disclaimer Section
        disclaimer_frame = ctk.CTkFrame(scroll_frame)
        disclaimer_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        disclaimer_label = ctk.CTkLabel(disclaimer_frame, text="Disclaimer", font=ctk.CTkFont(size=14, weight="bold"))
        disclaimer_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Toggle switch for showing disclaimer on startup
        self.disclaimer_switch = ctk.CTkSwitch(
            disclaimer_frame,
            text="Show disclaimer on startup",
            command=self.toggle_disclaimer
        )
        self.disclaimer_switch.pack(anchor="w", padx=10, pady=(5, 5))
        
        # Set initial state based on current setting
        if not self.settings.get_disclaimer_acknowledged():
            self.disclaimer_switch.select()
        
        disclaimer_help = ctk.CTkLabel(
            disclaimer_frame,
            text="Toggle ON to show the disclaimer window on next startup",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        disclaimer_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Save button at bottom
        save_button = ctk.CTkButton(
            self.settings_frame,
            text="💾 Save Settings",
            command=self.save_main_settings,
            height=40,
            fg_color="#E67E22",
            hover_color="#D35400",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_button.pack(fill="x", padx=20, pady=(10, 15), side="bottom")
    
    def save_main_settings(self):
        """Save settings from main view."""
        try:
            # Save location threshold
            threshold = float(self.settings_threshold_entry.get())
            self.settings.set_location_threshold(threshold)
            
            # Save timezone
            tz_value = self.settings_timezone_menu.get()
            logger.info(f"Saving timezone from menu value: {tz_value}")
            if tz_value.startswith("UTC"):
                self.settings.set_timezone("UTC")
            elif tz_value.startswith("EST"):
                self.settings.set_timezone("EST")
            elif tz_value.startswith("Local"):
                self.settings.set_timezone("Local")
            else:
                self.settings.set_timezone("PST")
            logger.info(f"Timezone saved as: {self.settings.get_timezone()}")
            
            # Save coordinate format
            coord_value = self.settings_coord_menu.get()
            if "Hours/Minutes/Seconds" in coord_value:
                self.settings.set_coordinate_format("hms")
            else:
                self.settings.set_coordinate_format("degrees")
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            logger.info("Settings saved from main view")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def toggle_disclaimer(self):
        """Toggle the disclaimer acknowledgment based on switch state."""
        # Switch is ON (not acknowledged = show on startup)
        if self.disclaimer_switch.get():
            self.settings.set_disclaimer_acknowledged(False)
        # Switch is OFF (acknowledged = don't show)
        else:
            self.settings.set_disclaimer_acknowledged(True)
    
    def show_mode(self, mode):
        """Switch to specified mode view."""
        self.current_mode = mode
        
        if mode == 'settings':
            # Hide normal mode panels, show settings full width
            self.left_panel.grid_forget()
            self.right_panel.grid_forget()
            self.fits_viewer_frame.grid_forget()
            self.settings_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
            self.progress_label.configure(text="Settings mode - configure app settings and click Save")
            
            # Refresh disclaimer switch state (may have changed via disclaimer dialog)
            if not self.settings.get_disclaimer_acknowledged():
                self.disclaimer_switch.select()
            else:
                self.disclaimer_switch.deselect()
        elif mode == 'fits_viewer':
            # Hide normal mode panels, show fits viewer full width
            self.left_panel.grid_forget()
            self.right_panel.grid_forget()
            self.settings_frame.grid_forget()
            self.fits_viewer_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
            self.progress_label.configure(text="FITS Viewer - browse and preview FITS files")
        else:
            # Hide settings and fits viewer, show normal layout
            self.settings_frame.grid_forget()
            self.fits_viewer_frame.grid_forget()
            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.right_panel.grid(row=0, column=1, sticky="nsew")
            
            # Hide all content frames in left panel
            self.welcome_frame.pack_forget()
            self.scan_build_frame.pack_forget()
            self.analyze_frame.pack_forget()
            self.about_frame.pack_forget()
            self.planetary_scenery_frame.pack_forget()
            
            if mode == 'scan_build':
                self.scan_build_frame.pack(fill="both", expand=True)
                # Show/hide raw section and update title/explanation based on workflow mode
                if self.workflow_mode == "direct":
                    self.scan_build_title.configure(text="Direct Copy")
                    self.scan_build_explanation.configure(
                        text="Copy FITS files directly from Seestar device to project folders. "
                             "This mode skips the intermediate Raw directory and is fastest for typical use.\n\n"
                             "For each source folder ending in '_sub' or '_subs', a '_Project' folder will be created "
                             "with lights/, darks/, biases/, and flats/ subdirectories. All FITS files will be "
                             "classified and copied to the appropriate folder (typically lights/)."
                    )
                    self.raw_section_frame.pack_forget()
                    self.progress_label.configure(text="Direct mode: Seestar → Projects")
                else:
                    self.scan_build_title.configure(text="Intermediate Copy")
                    self.scan_build_explanation.configure(
                        text="Copy FITS files from Seestar to Raw directory first, then build projects. "
                             "This mode preserves the original files and allows for more flexible project management.\n\n"
                             "For each source folder ending in '_sub' or '_subs', a '_Project' folder will be created "
                             "with lights/, darks/, biases/, and flats/ subdirectories. All FITS files will be "
                             "classified and copied to the appropriate folder (typically lights/)."
                    )
                    self.raw_section_frame.pack(fill="x", padx=10, pady=(0, 0), before=self.projects_label)
                    self.progress_label.configure(text="Intermediate mode: Seestar → Raw → Projects")
            elif mode == 'analyze':
                self.analyze_frame.pack(fill="both", expand=True)
                self.progress_label.configure(text="Analysis mode - select projects directory and click Start")
            elif mode == 'planetary_scenery':
                self.planetary_scenery_frame.pack(fill="both", expand=True)
                self.progress_label.configure(text="Copy Planetary & Scenery - select directories and click Start")
            elif mode == 'about':
                self.about_frame.pack(fill="both", expand=True)
                self.progress_label.configure(text="About - Seestar FITS Organizer")
            else:
                self.welcome_frame.pack(fill="both", expand=True)
                self.progress_label.configure(text="Ready")
    
    def destroy_all_menus(self):
        """Destroy all open menus."""
        for attr in ['_import_menu', '_tools_menu', '_help_menu']:
            if hasattr(self, attr):
                menu = getattr(self, attr)
                if menu and menu.winfo_exists():
                    menu.destroy()
                setattr(self, attr, None)
    
    def close_menus_on_click(self, event):
        """Close all menus when clicking outside them."""
        # Only close if not clicking on menu buttons (let button handlers manage that)
        widget = event.widget
        widget_class = widget.winfo_class()
        # Don't close if clicking on a button
        if widget_class == 'Button' or 'button' in str(widget).lower():
            return
        
        for attr in ['_import_menu', '_tools_menu', '_help_menu']:
            if hasattr(self, attr):
                menu = getattr(self, attr)
                if menu and menu.winfo_exists():
                    menu.destroy()
                    setattr(self, attr, None)
    
    def show_import_menu(self):
        """Show Import menu dropdown."""
        # Destroy existing menu if open
        if hasattr(self, '_import_menu') and self._import_menu and self._import_menu.winfo_exists():
            self._import_menu.destroy()
            self._import_menu = None
            return
        
        # Close any other open menus
        self.destroy_all_menus()
        
        self._import_menu = ctk.CTkToplevel(self)
        menu = self._import_menu
        # Position below Import button (y + 40 to be below the button)
        menu.geometry(f"200x130+{self.winfo_x() + 20}+{self.winfo_y() + 45}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        
        def close_menu():
            if hasattr(self, '_import_menu') and self._import_menu and self._import_menu.winfo_exists():
                self._import_menu.destroy()
            self._import_menu = None
        
        def direct_flow():
            close_menu()
            self.workflow_mode = "direct"
            self.lift()
            self.after(100, lambda: self.show_mode('scan_build'))
        
        def intermediate_flow():
            close_menu()
            self.workflow_mode = "intermediate"
            self.lift()
            self.after(100, lambda: self.show_mode('scan_build'))
        
        def planetary_scenery_flow():
            close_menu()
            self.lift()
            self.after(100, lambda: self.show_mode('planetary_scenery'))
        
        ctk.CTkButton(menu, text="� Direct", 
                     command=direct_flow).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(menu, text="📁 Intermediate", 
                     command=intermediate_flow).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(menu, text="🌙 Copy Planetary & Scenery", 
                     command=planetary_scenery_flow).pack(fill="x", padx=10, pady=2)
        
        # Close on Escape
        menu.bind("<Escape>", lambda e: close_menu())
        menu.focus_set()
    
    def show_tools_menu(self):
        """Show Tools menu dropdown."""
        if hasattr(self, '_tools_menu') and self._tools_menu and self._tools_menu.winfo_exists():
            self._tools_menu.destroy()
            self._tools_menu = None
            return
        
        self.destroy_all_menus()
        
        self._tools_menu = ctk.CTkToplevel(self)
        menu = self._tools_menu
        # Position below Tools button (y + 40 to be below the button)
        menu.geometry(f"200x90+{self.winfo_x() + 110}+{self.winfo_y() + 45}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        
        def close_menu():
            if hasattr(self, '_tools_menu') and self._tools_menu and self._tools_menu.winfo_exists():
                self._tools_menu.destroy()
            self._tools_menu = None
        
        def fits_viewer_and_close():
            close_menu()
            self.lift()
            self.after(100, lambda: self.show_mode('fits_viewer'))
        
        def analyze_and_close():
            close_menu()
            self.lift()
            self.after(100, lambda: self.show_mode('analyze'))
        
        ctk.CTkButton(menu, text="🪐 Analyze Projects",
                     command=analyze_and_close).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(menu, text="🖼️ FITS Viewer",
                     command=fits_viewer_and_close).pack(fill="x", padx=10, pady=5)
        
        menu.bind("<Escape>", lambda e: close_menu())
        menu.focus_set()
    
    def show_help_menu(self):
        """Show Help menu dropdown."""
        if hasattr(self, '_help_menu') and self._help_menu and self._help_menu.winfo_exists():
            self._help_menu.destroy()
            self._help_menu = None
            return
        
        self.destroy_all_menus()
        
        self._help_menu = ctk.CTkToplevel(self)
        menu = self._help_menu
        # Position below Help button (y + 40 to be below the button)
        menu.geometry(f"150x60+{self.winfo_x() + 310}+{self.winfo_y() + 45}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        
        def close_menu():
            if hasattr(self, '_help_menu') and self._help_menu and self._help_menu.winfo_exists():
                self._help_menu.destroy()
            self._help_menu = None
        
        def about_and_close():
            close_menu()
            self.lift()
            self.after(100, lambda: self.show_mode('about'))
        
        ctk.CTkButton(menu, text="ℹ️ About", 
                     command=about_and_close).pack(fill="x", padx=10, pady=5)
        
        menu.bind("<Escape>", lambda e: close_menu())
        menu.focus_set()
    
    def _create_about_frame(self):
        """Create About frame (hidden initially)."""
        self.about_frame = ctk.CTkFrame(self.left_panel)
        
        about_title = ctk.CTkLabel(self.about_frame, text="ℹ️ About", font=ctk.CTkFont(size=16, weight="bold"))
        about_title.pack(anchor="w", padx=10, pady=(20, 10))
        
        about_text = ctk.CTkLabel(
            self.about_frame,
            text="Seestar FITS Organizer\n\n"
                 "A tool for organizing astrophotography data from Seestar telescopes.\n\n"
                 "Features:\n"
                 "• Direct Import - Copy FITS files directly from Seestar to organized projects\n"
                 "• Intermediate Import - Copy to Raw folder first, then build projects\n"
                 "• Planetary & Scenery Import - Copy Solar, Lunar, Planetary, and Scenery media\n"
                 "• Project Analysis - View integration time, frame counts, and session details\n"
                 "• FITS Viewer - Browse and preview FITS files with arrow key navigation\n\n"
                 "Version: 1.3.2\n"
                 "Created by Guy Ronen",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=900,
            justify="left"
        )
        about_text.pack(anchor="w", padx=10, pady=10)
    
    def show_about(self):
        """Show about view (legacy method, now uses show_mode)."""
        self.show_mode('about')
    
    def toggle_workflow(self):
        """Toggle between direct and intermediate workflow."""
        if self.workflow_var.get() == "direct":
            self.workflow_mode = "direct"
            self.workflow_explanation.configure(
                text="Direct: Copy directly from Seestar device to project folders (skips intermediate Raw directory)."
            )
            # Hide raw directory selection
            self.raw_section_frame.pack_forget()
        else:
            self.workflow_mode = "intermediate"
            self.workflow_explanation.configure(
                text="Intermediate: First copy to Raw directory, then build projects from Raw."
            )
            # Show raw directory section BEFORE projects directory
            self.raw_section_frame.pack(fill="x", padx=10, pady=(0, 0), before=self.projects_label)


def main():
    """Main entry point."""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    app = SeestarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
