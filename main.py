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
from ui import DisclaimerWindow, FolderSelectionWindow, SettingsWindow, AnalysisWindow

logger = logging.getLogger(__name__)


class SeestarApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Seestar FITS Organizer")
        self.geometry("1000x700")
        
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
        
        self.scan_button.configure(state=state)
        self.analyze_button.configure(state=state)
        self.settings_button.configure(state=state)
        self.seestar_button.configure(state=state)
        self.raw_button.configure(state=state)
        self.projects_button.configure(state=state)
        self.analyze_projects_button.configure(state=state)
    
    def setup_ui(self):
        """Setup the user interface."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container - horizontal split
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
        
        self.settings_button = ctk.CTkButton(
            title_frame,
            text="⚙️",
            font=ctk.CTkFont(size=20),
            width=40,
            height=40,
            command=self.open_settings
        )
        self.settings_button.pack(side="right")
        
        # Content frame - horizontal split: left (controls) and right (console)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Controls
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Scan & Build Projects Section
        scan_build_frame = ctk.CTkFrame(left_panel)
        scan_build_frame.pack(fill="x", pady=(0, 20))
        
        scan_build_label = ctk.CTkLabel(scan_build_frame, text="Scan & Build Projects", font=ctk.CTkFont(size=16, weight="bold"))
        scan_build_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Workflow Selection
        workflow_label = ctk.CTkLabel(scan_build_frame, text="Select Workflow:", font=ctk.CTkFont(weight="bold"))
        workflow_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        workflow_button_frame = ctk.CTkFrame(scan_build_frame, fg_color="transparent")
        workflow_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.direct_radio = ctk.CTkRadioButton(
            workflow_button_frame,
            text="Direct (Seestar → Projects)",
            variable=self.workflow_var,
            value="direct",
            command=self.toggle_workflow
        )
        self.direct_radio.pack(side="left", padx=(0, 20))
        
        self.intermediate_radio = ctk.CTkRadioButton(
            workflow_button_frame,
            text="Intermediate (Seestar → Raw → Projects)",
            variable=self.workflow_var,
            value="intermediate",
            command=self.toggle_workflow
        )
        self.intermediate_radio.pack(side="left")
        self.direct_radio.select()
        
        # Workflow explanation
        self.workflow_explanation = ctk.CTkLabel(
            scan_build_frame,
            text="Direct: Copy directly from Seestar device to project folders (skips intermediate Raw directory).",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=900
        )
        self.workflow_explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Seestar Device Directory (common to both workflows)
        seestar_label = ctk.CTkLabel(scan_build_frame, text="Seestar MyWork Directory:", font=ctk.CTkFont(weight="bold"))
        seestar_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        seestar_button_frame = ctk.CTkFrame(scan_build_frame, fg_color="transparent")
        seestar_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.seestar_path_label = ctk.CTkLabel(seestar_button_frame, text="Not selected", text_color="gray")
        self.seestar_path_label.pack(side="left", padx=(0, 10))
        
        self.seestar_button = ctk.CTkButton(seestar_button_frame, text="🌌 Browse", command=self.select_seestar_dir, width=100)
        self.seestar_button.pack(side="right")
        
        # Raw Directory Section - Created but NOT packed (shown only in intermediate mode)
        self.raw_section_frame = ctk.CTkFrame(scan_build_frame, fg_color="transparent")
        
        raw_label = ctk.CTkLabel(self.raw_section_frame, text="Raw Directory (Intermediate):", font=ctk.CTkFont(weight="bold"))
        raw_label.pack(anchor="w", pady=(10, 0))
        
        raw_button_frame = ctk.CTkFrame(self.raw_section_frame, fg_color="transparent")
        raw_button_frame.pack(fill="x", pady=(5, 10))
        
        self.raw_path_label = ctk.CTkLabel(raw_button_frame, text="Not selected", text_color="gray")
        self.raw_path_label.pack(side="left", padx=(0, 10))
        
        self.raw_button = ctk.CTkButton(raw_button_frame, text="🌌 Browse", command=self.select_raw_dir, width=100)
        self.raw_button.pack(side="right")
        
        # Projects Directory (for scan & build) - This gets packed AFTER Seestar and Raw
        self.projects_label = ctk.CTkLabel(scan_build_frame, text="Projects Directory:", font=ctk.CTkFont(weight="bold"))
        self.projects_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        projects_button_frame = ctk.CTkFrame(scan_build_frame, fg_color="transparent")
        projects_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.projects_path_label = ctk.CTkLabel(projects_button_frame, text="Not selected", text_color="gray")
        self.projects_path_label.pack(side="left", padx=(0, 10))
        
        self.projects_button = ctk.CTkButton(projects_button_frame, text="🌌 Browse", command=self.select_projects_dir, width=100)
        self.projects_button.pack(side="right")
        
        # Scan & Build Button
        self.scan_button = ctk.CTkButton(
            scan_build_frame, 
            text="🔭 Scan & Build Projects",
            command=self.start_scan,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.scan_button.pack(fill="x", padx=10, pady=(10, 10))
        
        # Analyze Projects Section
        analyze_frame = ctk.CTkFrame(left_panel)
        analyze_frame.pack(fill="x", pady=(0, 20))
        
        analyze_label = ctk.CTkLabel(analyze_frame, text="Analyze Existing Projects", font=ctk.CTkFont(size=16, weight="bold"))
        analyze_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Projects Directory (for analysis)
        analyze_projects_label = ctk.CTkLabel(analyze_frame, text="Projects Directory:", font=ctk.CTkFont(weight="bold"))
        analyze_projects_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        analyze_projects_button_frame = ctk.CTkFrame(analyze_frame, fg_color="transparent")
        analyze_projects_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.analyze_projects_path_label = ctk.CTkLabel(analyze_projects_button_frame, text="Not selected", text_color="gray")
        self.analyze_projects_path_label.pack(side="left", padx=(0, 10))
        
        self.analyze_projects_button = ctk.CTkButton(analyze_projects_button_frame, text="🌌 Browse", command=self.select_analyze_projects_dir, width=100)
        self.analyze_projects_button.pack(side="right")
        
        # Analyze Button
        self.analyze_button = ctk.CTkButton(
            analyze_frame,
            text="🪐 Analyze Existing Projects",
            command=self.start_analysis,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyze_button.pack(fill="x", padx=10, pady=(0, 10))
        
        # Progress Frame
        progress_frame = ctk.CTkFrame(left_panel)
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready", text_color="gray")
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Right panel - Console Output
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        console_label = ctk.CTkLabel(right_panel, text="Console Output", font=ctk.CTkFont(size=14, weight="bold"))
        console_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.console_text = ctk.CTkTextbox(right_panel)
        self.console_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.console_text.configure(state="disabled")
        
        # Redirect logging to console
        self.setup_console_logging()
    
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
    
    def show_analysis_window(self, results):
        """Show analysis results in a new window."""
        location_tags = LocationTags()
        AnalysisWindow(self, results, self.settings, location_tags)
    
    def open_settings(self):
        """Open the settings dialog."""
        location_tags = LocationTags()
        SettingsWindow(self, self.settings, location_tags)
    
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
