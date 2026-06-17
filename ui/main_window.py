"""
Main Window Module

Contains the main SeestarApp class for the Seestar FITS Organizer.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor

# Import core business logic
from core import AppSettings, LocationTags, ProjectBuilder, ProjectAnalyzer

# Import UI components
from ui import DisclaimerWindow, FolderSelectionWindow, AnalysisWindow, FileTypeSelectionDialog, detect_file_types_in_directories

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
        
        # Load saved directories and auto-populate UI
        self._load_saved_directories()
        
        # Set fullscreen/maximized window state
        self.state('zoomed')  # Windows maximized
        # Alternative: self.attributes('-fullscreen', True) for true fullscreen
        
        # Initialize workflow state (raw section is not packed by default for direct mode)
        pass  # raw_section_frame is not packed initially
    
    def show_disclaimer(self):
        """Show the disclaimer window."""
        DisclaimerWindow(self, self.settings)
    
    def _load_saved_directories(self):
        """Load saved directories from settings and auto-populate UI labels."""
        # Load Seestar directory
        seestar_dir = self.settings.get_seestar_dir()
        if seestar_dir and Path(seestar_dir).exists():
            self.seestar_dir = Path(seestar_dir)
            if hasattr(self, 'seestar_path_label'):
                self.seestar_path_label.configure(text=str(self.seestar_dir), text_color="white")
            logger.info(f"Loaded saved Seestar directory: {self.seestar_dir}")
        
        # Load Raw directory
        raw_dir = self.settings.get_raw_dir()
        if raw_dir and Path(raw_dir).exists():
            self.raw_dir = Path(raw_dir)
            if hasattr(self, 'raw_path_label'):
                self.raw_path_label.configure(text=str(self.raw_dir), text_color="white")
            logger.info(f"Loaded saved Raw directory: {self.raw_dir}")
        
        # Load Projects directory
        projects_dir = self.settings.get_projects_dir()
        if projects_dir and Path(projects_dir).exists():
            self.projects_dir = Path(projects_dir)
            if hasattr(self, 'projects_path_label'):
                self.projects_path_label.configure(text=str(self.projects_dir), text_color="white")
            logger.info(f"Loaded saved Projects directory: {self.projects_dir}")
            
            # Also load into analyze_projects_dir for reuse
            self.analyze_projects_dir = Path(projects_dir)
            if hasattr(self, 'analyze_projects_path_label'):
                self.analyze_projects_path_label.configure(text=str(self.analyze_projects_dir), text_color="white")
    
    def _create_menu_item(self, parent, text, font, command):
        """Create a traditional menu item button.
        
        Args:
            parent: Parent widget
            text: Button text
            font: Font to use
            command: Command to execute on click
            
        Returns:
            CTkButton configured as a menu item
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=font,
            height=28,
            fg_color="transparent",
            hover_color="#D35400",
            border_width=0,
            text_color="black",
            cursor="hand2",
            command=command
        )
    
    def _create_dropdown_menu_item(self, parent, text, command):
        """Create a traditional dropdown menu item (looks like text, not button).
        
        Args:
            parent: Parent widget
            text: Menu item text
            command: Command to execute on click
            
        Returns:
            CTkButton configured as a menu item with transparent styling
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=self.get_font(12),
            height=28,
            fg_color="#E67E22",
            hover_color="#D35400",
            border_width=0,
            text_color="black",
            anchor="w",
            cursor="hand2",
            command=command
        )
    
    def _create_menu_separator(self, parent):
        """Create a separator line between menu items.
        
        Args:
            parent: Parent widget
        """
        separator = ctk.CTkFrame(parent, height=1, fg_color="#D35400")
        separator.pack(fill="x", padx=5, pady=2)
    
    def get_font(self, size: int, weight: str = None):
        """Get a CTkFont with text scaling applied.
        
        Args:
            size: Base font size
            weight: Font weight (e.g., 'bold', 'normal')
            
        Returns:
            CTkFont with scaled size
        """
        scale = self.settings.get_text_scale()
        scaled_size = int(size * scale)
        if weight:
            return ctk.CTkFont(size=scaled_size, weight=weight)
        return ctk.CTkFont(size=scaled_size)
    
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
    
    def show_loading_spinner(self):
        """Show animated loading spinner."""
        self.loading_animation_running = True
        self.loading_label.pack(anchor="center", pady=(5, 0))
        self._animate_loading_spinner()
    
    def hide_loading_spinner(self):
        """Hide loading spinner."""
        self.loading_animation_running = False
        self.loading_label.pack_forget()
    
    def _animate_loading_spinner(self):
        """Animate the loading spinner with cycling dots."""
        if not self.loading_animation_running:
            return
        
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        current_dot = 0
        
        def update_spinner():
            if not self.loading_animation_running:
                return
            self.loading_label.configure(text=f"{dots[current_dot % len(dots)]} Processing...")
            self.after(100, lambda: self._update_spinner_frame((current_dot + 1) % len(dots)))
        
        self.after(0, update_spinner)
    
    def _update_spinner_frame(self, dot_index):
        """Update spinner frame."""
        if not self.loading_animation_running:
            return
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_label.configure(text=f"{dots[dot_index]} Processing...")
        self.after(100, lambda: self._update_spinner_frame((dot_index + 1) % len(dots)))
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget.
        
        Args:
            widget: The widget to add tooltip to
            text: The tooltip text
        """
        tooltip = ctk.CTkLabel(
            self,
            text=text,
            font=self.get_font(10),
            fg_color="#2C3E50",
            text_color="white",
            corner_radius=5,
            padx=8,
            pady=4
        )
        tooltip.place_forget()  # Hide initially
        tooltip_visible = [False]  # Use list to allow modification in nested function
        
        def show_tooltip(event):
            if not tooltip_visible[0]:
                x = event.x_root - self.winfo_rootx() + 15
                y = event.y_root - self.winfo_rooty() + 15
                tooltip.place(x=x, y=y)
                tooltip.lift()
                tooltip_visible[0] = True
        
        def hide_tooltip(event):
            tooltip.place_forget()
            tooltip_visible[0] = False
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def setup_ui(self):
        """Setup the user interface."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main container - no padding, tight layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)  # Content frame expands
        
        # Menu bar frame at top (fixed height)
        menu_bar = ctk.CTkFrame(main_frame, height=35, fg_color="#E67E22")
        menu_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        menu_bar.grid_propagate(False)  # Keep fixed height
        
        # Home Button (leftmost)
        home_btn = ctk.CTkButton(
            menu_bar,
            text="🏠",
            font=self.get_font(14),
            width=35,
            height=28,
            fg_color="transparent",
            hover_color="#D35400",
            border_width=0,
            text_color="black",
            command=lambda: (self.destroy_all_menus(), self.show_mode('welcome'))
        )
        home_btn.grid(row=0, column=0, padx=2, pady=2)
        self._create_tooltip(home_btn, "Return to Home")
        
        # Import Menu
        self.import_menu_btn = self._create_menu_item(
            menu_bar,
            text="Import ▼",
            font=self.get_font(13),
            command=self.show_import_menu
        )
        self.import_menu_btn.grid(row=0, column=1, padx=2, pady=2)
        self._create_tooltip(self.import_menu_btn, "Import from Seestar")
        
        # Tools Menu
        self.tools_menu_btn = self._create_menu_item(
            menu_bar,
            text="Tools ▼",
            font=self.get_font(13),
            command=self.show_tools_menu
        )
        self.tools_menu_btn.grid(row=0, column=2, padx=2, pady=2)
        self._create_tooltip(self.tools_menu_btn, "Tools and Analysis")
        
        # Help Menu
        self.help_menu_btn = self._create_menu_item(
            menu_bar,
            text="Help ▼",
            font=self.get_font(13),
            command=self.show_help_menu
        )
        self.help_menu_btn.grid(row=0, column=3, padx=2, pady=2)
        self._create_tooltip(self.help_menu_btn, "Help and Documentation")
        
        # Configure column 4 to expand (spacer)
        menu_bar.grid_columnconfigure(4, weight=1)
        
        # Settings Button (right side)
        settings_btn = ctk.CTkButton(
            menu_bar,
            text="⚙️",
            font=self.get_font(14),
            width=35,
            height=28,
            fg_color="transparent",
            hover_color="#D35400",
            border_width=0,
            text_color="black",
            command=lambda: (self.destroy_all_menus(), self.show_mode('settings'))
        )
        settings_btn.grid(row=0, column=5, padx=2, pady=2)
        self._create_tooltip(settings_btn, "Settings")
        
        # Initialize mode tracking
        self.current_mode = None  # None, 'scan_build', 'analyze', 'settings', or 'fits_viewer'
        
        # Content frame - main container for all views
        self.content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=0)  # Separator doesn't expand
        self.content_frame.grid_columnconfigure(2, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Normal mode panel (left side - for scan/build and analyze)
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 0))
        
        # Resizable separator with toggle button
        self.separator = ctk.CTkFrame(self.content_frame, width=12, fg_color="#3a3a3a", cursor="sb_h_double_arrow")
        self.separator.grid(row=0, column=1, sticky="ns")
        
        # Console toggle button on separator
        self.console_toggle_btn = ctk.CTkButton(
            self.separator,
            text="▶",
            width=24,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3a3a3a",
            hover_color="#555555",
            text_color="white",
            command=self.toggle_console
        )
        self.console_toggle_btn.place(relx=0.5, rely=0.5, anchor="center")
        self._create_tooltip(self.console_toggle_btn, "Toggle Console Panel")
        
        # Console state
        self.console_visible = True
        
        # Bind mouse events for dragging (on separator, not button)
        self.separator.bind("<Button-1>", self._start_resize)
        self.separator.bind("<B1-Motion>", self._on_resize)
        self.separator.bind("<ButtonRelease-1>", self._end_resize)
        
        self._resizing = False
        self._resize_start_x = 0
        self._resize_start_width = 0
        
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
            font=self.get_font(24, weight="bold")
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
            font=self.get_font(16),
            text_color="gray"
        )
        welcome_text.pack(pady=20)
        
        # Progress Frame (always visible at bottom of left panel)
        self.progress_frame = ctk.CTkFrame(self.left_panel)
        self.progress_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Ready", text_color="#E0E0E0")
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Progress bar for file operations
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)  # 0 to 1
        
        # Loading spinner label (hidden by default)
        self.loading_label = ctk.CTkLabel(self.progress_frame, text="", font=self.get_font(11))
        self.loading_label.pack(anchor="center", pady=(5, 0))
        self.loading_label.pack_forget()  # Hide initially
        self.loading_animation_running = False
        
        # Right panel - Console Output
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.grid(row=0, column=2, sticky="nsew")
        
        console_label = ctk.CTkLabel(self.right_panel, text="Console Output", font=self.get_font(14, weight="bold"))
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
            # Save to settings
            self.settings.set_seestar_dir(directory)
    
    def select_raw_dir(self):
        """Select raw directory (target for copy)."""
        directory = filedialog.askdirectory(title="Select Raw Directory (Target)")
        if directory:
            self.raw_dir = Path(directory)
            self.raw_path_label.configure(text=str(self.raw_dir), text_color="white")
            logger.info(f"Selected raw directory: {self.raw_dir}")
            # Save to settings
            self.settings.set_raw_dir(directory)
    
    def select_projects_dir(self):
        """Select projects directory."""
        directory = filedialog.askdirectory(title="Select Projects Directory")
        if directory:
            self.projects_dir = Path(directory)
            self.projects_path_label.configure(text=str(self.projects_dir), text_color="white")
            logger.info(f"Selected projects directory: {self.projects_dir}")
            # Save to settings
            self.settings.set_projects_dir(directory)
    
    def select_analyze_projects_dir(self):
        """Select projects directory for analysis."""
        directory = filedialog.askdirectory(title="Select Projects Directory for Analysis")
        if directory:
            self.analyze_projects_dir = Path(directory)
            self.analyze_projects_path_label.configure(text=str(self.analyze_projects_dir), text_color="white")
            logger.info(f"Selected analyze projects directory: {self.analyze_projects_dir}")
            # Also save to projects_dir setting for reuse
            self.settings.set_projects_dir(directory)
    
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
        self.show_loading_spinner()
        self.progress_label.configure(text="Scanning and building projects...")
        self.progress_bar.set(0)  # Reset progress bar
        
        thread = threading.Thread(target=self.scan_and_build)
        thread.daemon = True
        thread.start()
    
    def start_analysis(self):
        """Start analysis of existing projects."""
        if not self.analyze_projects_dir:
            messagebox.showerror("Error", "Please select Projects directory for analysis")
            return
        
        self.set_ui_state(False)
        self.show_loading_spinner()
        self.progress_label.configure(text="Analyzing projects...")
        self.progress_bar.set(0)  # Reset progress bar
        
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
        self.show_loading_spinner()
        self.progress_label.configure(text="Copying Planetary & Scenery media...")
        self.progress_bar.set(0)  # Reset progress bar
        
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
                    self.after(0, lambda: self.hide_loading_spinner())
                    return
                
                # Show folder selection dialog
                selected_folders = self._show_folder_selection_dialog(seestar_folders)
                
                if not selected_folders:
                    self.after(0, lambda: self.progress_label.configure(text="No folders selected. Cancelled."))
                    self.after(0, lambda: self.set_ui_state(True))
                    self.after(0, lambda: self.hide_loading_spinner())
                    return
                
                # Step 2: Detect file types and show selection dialog BEFORE copying
                self.after(0, lambda: self.progress_label.configure(text="Detecting file types..."))
                file_type_counts = detect_file_types_in_directories(selected_folders)
                
                selected_file_types = None
                if file_type_counts:
                    selected_file_types = self._show_file_type_selection_dialog(file_type_counts)
                    
                    # If user cancelled file type selection, cancel the entire operation
                    if selected_file_types is None:
                        self.after(0, lambda: self.progress_label.configure(text="File type selection cancelled."))
                        self.after(0, lambda: self.set_ui_state(True))
                        self.after(0, lambda: self.hide_loading_spinner())
                        return
                
                # Step 3: Copy selected folders from Seestar to Raw
                self.after(0, lambda: self.progress_label.configure(text=f"Copying {len(selected_folders)} folders to Raw..."))
                self.copy_seestar_to_raw(selected_folders, selected_file_types)
                
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
            selected_file_types = None
            if self.workflow_mode == "direct":
                self.after(0, lambda: self.progress_label.configure(text="Discovering folders..."))
                folders = builder.scan_raw_folders()
                total_folders = len(folders)
                
                if total_folders == 0:
                    self.after(0, lambda: self.progress_label.configure(text="No *_subs folders found in source"))
                    self.after(0, lambda: self.set_ui_state(True))
                    self.after(0, lambda: self.hide_loading_spinner())
                    return
                
                # Show folder selection dialog
                selected_folders = self._show_folder_selection_dialog(folders)
                
                if not selected_folders:
                    self.after(0, lambda: self.progress_label.configure(text="No folders selected. Cancelled."))
                    self.after(0, lambda: self.set_ui_state(True))
                    self.after(0, lambda: self.hide_loading_spinner())
                    return
                
                # Step 4: Detect file types and show selection dialog for direct mode
                self.after(0, lambda: self.progress_label.configure(text="Detecting file types..."))
                file_type_counts = detect_file_types_in_directories(selected_folders)
                
                if file_type_counts:
                    selected_file_types = self._show_file_type_selection_dialog(file_type_counts)
                
                build_folders = selected_folders
            else:
                # Intermediate workflow: use the folders we already selected and copied
                self.after(0, lambda: self.progress_label.configure(text="Discovering folders in Raw..."))
                # Verify the folders exist in Raw
                build_folders = [f for f in build_folders if f.exists()]
            
            # Step 1: Count total files to copy
            self.after(0, lambda: self.progress_label.configure(text="Counting files to copy..."))
            total_files = builder.count_files_to_copy(build_folders, selected_file_types)
            
            if total_files == 0:
                self.after(0, lambda: self.progress_label.configure(text="No FITS files found in selected folders"))
                self.after(0, lambda: self.set_ui_state(True))
                self.after(0, lambda: self.hide_loading_spinner())
                return
            
            self.after(0, lambda: self.progress_label.configure(text=f"Copying {total_files} files..."))
            
            # Set up global progress tracking
            global_progress = {
                'current': 0,
                'total': total_files,
                'callback': lambda cur, tot, pct, msg: self.after(0, lambda: self._update_copy_progress(cur, tot, pct, msg))
            }
            
            # Step 2: Process folders with progress bar
            self.projects = []
            
            for folder in build_folders:
                project = builder.build_project(folder, global_progress=global_progress, selected_file_types=selected_file_types)
                self.projects.append(project)
            
            self.after(0, lambda: self._update_copy_progress(total_files, total_files, 1.0, "Complete!"))
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
            self.after(0, lambda: self.hide_loading_spinner())
    
    def _update_copy_progress(self, current: int, total: int, percentage: float, message: str):
        """Update the progress bar and label during file copy operations.
        
        Args:
            current: Current file number being processed
            total: Total number of files to copy
            percentage: Progress as a float from 0.0 to 1.0
            message: Status message to display
        """
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"{message} ({current}/{total})")
        self.update_idletasks()  # Force UI update
    
    def copy_seestar_to_raw(self, folders=None, selected_file_types=None):
        """Copy <NAME>_sub folders from Seestar to Raw directory.
        
        Args:
            folders: Optional list of specific folders to copy. If None, copies all folders.
            selected_file_types: Optional set of file extensions to copy (e.g., {'.fits', '.FIT'}).
                               If None, copies all FITS files.
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
        if selected_file_types:
            logger.info(f"Filtering by file types: {selected_file_types}")
        
        def copy_single_file(fits_file, raw_folder):
            """Copy a single file and return (copied, skipped) status."""
            dest_file = raw_folder / fits_file.name
            
            if dest_file.exists():
                # Compare file sizes
                src_size = fits_file.stat().st_size
                dest_size = dest_file.stat().st_size
                
                if src_size == dest_size:
                    return (0, 1)  # skipped
            
            # Copy the file
            shutil.copy2(fits_file, dest_file)
            return (1, 0)  # copied
        
        for folder in folders:
            # Create corresponding folder in Raw
            raw_folder = self.raw_dir / folder.name
            raw_folder.mkdir(parents=True, exist_ok=True)
            
            # Get files based on selected file types
            if selected_file_types:
                # Copy only selected file types
                files_to_copy = []
                for ext in selected_file_types:
                    files_to_copy.extend(list(folder.glob(f'*{ext}')))
            else:
                # Copy all FITS files (default behavior)
                files_to_copy = list(folder.glob('*.fits')) + list(folder.glob('*.FIT'))
            
            files_copied = 0
            files_skipped = 0
            
            # Use ThreadPoolExecutor for parallel copying
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for fits_file in files_to_copy:
                    futures.append(executor.submit(copy_single_file, fits_file, raw_folder))
                
                for future in futures:
                    copied, skipped = future.result()
                    files_copied += copied
                    files_skipped += skipped
            
            logger.info(f"Folder {folder.name}: {files_copied} files copied, {files_skipped} files skipped")
    
    def analyze_projects(self):
        """Analyze existing projects and show results."""
        try:
            # Scan for project folders
            project_folders = []
            for item in self.analyze_projects_dir.iterdir():
                if item.is_dir() and item.name.endswith('_Project'):
                    project_folders.append(item)
            
            # Fallback: Look for any directory with FITS files
            if not project_folders:
                logger.info("No _Project folders found, scanning for directories with FITS files...")
                for item in self.analyze_projects_dir.iterdir():
                    if item.is_dir():
                        has_fits = False
                        for file in item.iterdir():
                            if file.is_file() and file.suffix.lower() in ('.fits', '.fit'):
                                has_fits = True
                                break
                            if file.is_dir() and file.name.lower() in ('lights', 'darks', 'flats', 'bias'):
                                for subfile in file.iterdir():
                                    if subfile.is_file() and subfile.suffix.lower() in ('.fits', '.fit'):
                                        has_fits = True
                                        break
                                if has_fits:
                                    break
                        if has_fits:
                            project_folders.append(item)
            
            if not project_folders:
                self.after(0, lambda: messagebox.showinfo("No Projects", "No project folders found in the selected directory."))
                return
            
            # Show folder selection dialog
            selected_folders = self._show_folder_selection_dialog(project_folders)
            
            if not selected_folders:
                self.after(0, lambda: self.progress_label.configure(text="Analysis cancelled."))
                self.after(0, lambda: self.set_ui_state(True))
                self.after(0, lambda: self.hide_loading_spinner())
                return
            
            analyzer = ProjectAnalyzer(self.analyze_projects_dir)
            
            # Set up progress callback
            def progress_callback(current, total, percentage, message):
                self.after(0, lambda: self.progress_bar.set(percentage))
                self.after(0, lambda: self.progress_label.configure(text=f"{message} ({current}/{total})"))
            
            results = analyzer.analyze_all(progress_callback=progress_callback, specific_folders=selected_folders)
            
            # Update UI on main thread
            self.after(0, lambda: self.progress_bar.set(1.0))  # Complete progress bar
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
            self.after(0, lambda: self.hide_loading_spinner())
    
    def reset_progress(self):
        """Reset progress bar to 0."""
        self.progress_bar.set(0)
    
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
            
            def copy_single_media_file(item, target_folder):
                """Copy a single media file and return (copied, skipped) status."""
                dest_file = target_folder / item.name
                
                if dest_file.exists():
                    # Compare sizes
                    if item.stat().st_size == dest_file.stat().st_size:
                        return (0, 1)  # skipped
                
                shutil.copy2(item, dest_file)
                return (1, 0)  # copied
            
            for folder_name in media_folders:
                source_folder = self.ps_source_dir / folder_name
                if not source_folder.exists():
                    continue
                
                # Create target folder
                target_folder = self.ps_target_dir / folder_name
                target_folder.mkdir(parents=True, exist_ok=True)
                
                # Collect all files
                files_to_copy = []
                for item in source_folder.iterdir():
                    if item.is_file():
                        files_to_copy.append(item)
                
                total_files += len(files_to_copy)
                
                # Use ThreadPoolExecutor for parallel copying
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    for item in files_to_copy:
                        futures.append(executor.submit(copy_single_media_file, item, target_folder))
                    
                    for future in futures:
                        copied, skipped = future.result()
                        copied_files += copied
                        skipped_files += skipped
                
                self.after(0, lambda f=folder_name, c=copied_files, s=skipped_files: 
                    self.progress_label.configure(
                        text=f"Copied {f}: {c} new, {s} skipped"
                    ))
            
            # Show completion
            self.after(0, lambda: self.progress_bar.set(1.0))  # Complete progress bar
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
            self.after(0, lambda: self.hide_loading_spinner())
    
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
        self.scan_build_title = ctk.CTkLabel(self.scan_build_frame, text="Direct Copy", font=self.get_font(16, weight="bold"))
        self.scan_build_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Dynamic explanation (updated based on workflow mode)
        self.scan_build_explanation = ctk.CTkLabel(
            self.scan_build_frame,
            text="Copy FITS files directly from Seestar device to project folders. This mode skips the intermediate Raw directory.",
            font=self.get_font(13),
            text_color="#B0B0B0",
            wraplength=900,
            justify="left"
        )
        self.scan_build_explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Seestar Device Directory
        seestar_label = ctk.CTkLabel(self.scan_build_frame, text="Seestar MyWork Directory:", font=self.get_font(13, weight="bold"))
        seestar_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        seestar_button_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        seestar_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.seestar_path_label = ctk.CTkLabel(seestar_button_frame, text="Not selected", text_color="#B0B0B0")
        self.seestar_path_label.pack(side="left", padx=(0, 10))
        
        self.seestar_button = ctk.CTkButton(seestar_button_frame, text="🌌 Browse", command=self.select_seestar_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.seestar_button.pack(side="right")
        
        # Raw Directory Section (hidden initially)
        self.raw_section_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        
        raw_label = ctk.CTkLabel(self.raw_section_frame, text="Raw Directory (Intermediate):", font=self.get_font(13, weight="bold"))
        raw_label.pack(anchor="w", pady=(10, 0))
        
        raw_button_frame = ctk.CTkFrame(self.raw_section_frame, fg_color="transparent")
        raw_button_frame.pack(fill="x", pady=(5, 10))
        
        self.raw_path_label = ctk.CTkLabel(raw_button_frame, text="Not selected", text_color="#B0B0B0")
        self.raw_path_label.pack(side="left", padx=(0, 10))
        
        self.raw_button = ctk.CTkButton(raw_button_frame, text="🌌 Browse", command=self.select_raw_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.raw_button.pack(side="right")
        
        # Projects Directory
        self.projects_label = ctk.CTkLabel(self.scan_build_frame, text="Projects Directory:", font=self.get_font(13, weight="bold"))
        self.projects_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        projects_button_frame = ctk.CTkFrame(self.scan_build_frame, fg_color="transparent")
        projects_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.projects_path_label = ctk.CTkLabel(projects_button_frame, text="Not selected", text_color="#B0B0B0")
        self.projects_path_label.pack(side="left", padx=(0, 10))
        
        self.projects_button = ctk.CTkButton(projects_button_frame, text="🌌 Browse", command=self.select_projects_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.projects_button.pack(side="right")
        
        # Start Button
        self.scan_build_action_btn = ctk.CTkButton(
            self.scan_build_frame,
            text="🔭 Start Import",
            command=self.start_scan,
            height=40,
            font=self.get_font(14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.scan_build_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_analyze_frame(self):
        """Create Analyze mode frame (hidden initially)."""
        self.analyze_frame = ctk.CTkFrame(self.left_panel)
        
        analyze_label = ctk.CTkLabel(self.analyze_frame, text="Analyze Existing Projects", font=self.get_font(16, weight="bold"))
        analyze_label.pack(anchor="w", padx=10, pady=(10, 10))
        
        # Projects Directory (for analysis)
        analyze_projects_label = ctk.CTkLabel(self.analyze_frame, text="Projects Directory:", font=self.get_font(13, weight="bold"))
        analyze_projects_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        analyze_projects_button_frame = ctk.CTkFrame(self.analyze_frame, fg_color="transparent")
        analyze_projects_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.analyze_projects_path_label = ctk.CTkLabel(analyze_projects_button_frame, text="Not selected", text_color="#B0B0B0")
        self.analyze_projects_path_label.pack(side="left", padx=(0, 10))
        
        self.analyze_projects_button = ctk.CTkButton(analyze_projects_button_frame, text="🌌 Browse", command=self.select_analyze_projects_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.analyze_projects_button.pack(side="right")
        
        # Start Button
        self.analyze_action_btn = ctk.CTkButton(
            self.analyze_frame,
            text="🪐 Start Analysis",
            command=self.start_analysis,
            height=40,
            font=self.get_font(14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.analyze_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_planetary_scenery_frame(self):
        """Create Planetary & Scenery copy mode frame (hidden initially)."""
        self.planetary_scenery_frame = ctk.CTkFrame(self.left_panel)
        
        ps_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Copy Planetary & Scenery Media", font=self.get_font(16, weight="bold"))
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
            font=self.get_font(13),
            text_color="#B0B0B0",
            wraplength=900,
            justify="left"
        )
        explanation.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Source: Seestar MyWorks Directory
        source_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Seestar MyWorks Directory:", font=self.get_font(13, weight="bold"))
        source_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        source_button_frame = ctk.CTkFrame(self.planetary_scenery_frame, fg_color="transparent")
        source_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ps_source_path_label = ctk.CTkLabel(source_button_frame, text="Not selected", text_color="#B0B0B0")
        self.ps_source_path_label.pack(side="left", padx=(0, 10))
        
        self.ps_source_button = ctk.CTkButton(source_button_frame, text="🌌 Browse", command=self.select_ps_source_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.ps_source_button.pack(side="right")
        
        # Target: Destination Directory
        target_label = ctk.CTkLabel(self.planetary_scenery_frame, text="Target Directory:", font=self.get_font(13, weight="bold"))
        target_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        target_button_frame = ctk.CTkFrame(self.planetary_scenery_frame, fg_color="transparent")
        target_button_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.ps_target_path_label = ctk.CTkLabel(target_button_frame, text="Not selected", text_color="#B0B0B0")
        self.ps_target_path_label.pack(side="left", padx=(0, 10))
        
        self.ps_target_button = ctk.CTkButton(target_button_frame, text="🌌 Browse", command=self.select_ps_target_dir, width=100, fg_color="#3498db", hover_color="#2980b9")
        self.ps_target_button.pack(side="right")
        
        # Start Button
        self.ps_action_btn = ctk.CTkButton(
            self.planetary_scenery_frame,
            text="🌙 Copy Planetary & Scenery",
            command=self.start_planetary_scenery_copy,
            height=40,
            font=self.get_font(14, weight="bold"),
            fg_color="#E67E22",
            hover_color="#D35400"
        )
        self.ps_action_btn.pack(fill="x", padx=10, pady=(10, 10))
    
    def _create_fits_viewer_frame(self):
        """Create FITS Viewer mode frame (hidden initially)."""
        self.fits_viewer_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        title_label = ctk.CTkLabel(self.fits_viewer_frame, text="🖼️ FITS Viewer", font=self.get_font(16, weight="bold"))
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Directory selection frame
        dir_frame = ctk.CTkFrame(self.fits_viewer_frame)
        dir_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.fits_viewer_dir_label = ctk.CTkLabel(dir_frame, text="No directory selected", text_color="#B0B0B0")
        self.fits_viewer_dir_label.pack(side="left", padx=10, pady=10)
        
        browse_btn = ctk.CTkButton(dir_frame, text="📁 Browse", command=self.browse_fits_directory, width=100, fg_color="#3498db", hover_color="#2980b9")
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
        
        list_label = ctk.CTkLabel(left_panel, text="FITS Files", font=self.get_font(12, weight="bold"))
        list_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=5)
        
        self.mark_btn = ctk.CTkButton(action_frame, text="✓ Mark", command=self.toggle_mark_selected, width=80, font=self.get_font(11), fg_color="#27ae60", hover_color="#229954")
        self.mark_btn.pack(side="left", padx=2)
        
        self.clear_marks_btn = ctk.CTkButton(action_frame, text="⬜ Clear Marks", command=self.clear_all_marks, width=100, font=self.get_font(11), fg_color="#f39c12", hover_color="#e67e22")
        self.clear_marks_btn.pack(side="left", padx=2)
        
        self.delete_marked_btn = ctk.CTkButton(action_frame, text="🗑️ Delete Marked", command=self.delete_marked_fits, width=110, font=self.get_font(11), fg_color="#C0392B", hover_color="#A93226")
        self.delete_marked_btn.pack(side="right", padx=2)
        
        # Analysis button row
        analysis_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        analysis_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.analyze_all_btn = ctk.CTkButton(
            analysis_frame, 
            text="🔍 Analyze All", 
            command=self.analyze_all_fits,
            width=110, 
            font=self.get_font(11), 
            fg_color="#8E44AD", 
            hover_color="#7D3C98"
        )
        self.analyze_all_btn.pack(side="left", padx=2)
        self._create_tooltip(self.analyze_all_btn, "Analyze all images for streaks and star quality")
        
        # Sensitivity selector (7 levels)
        self.sensitivity_menu = ctk.CTkOptionMenu(
            analysis_frame,
            values=[
                "1 - Very Strict",
                "2 - Strict", 
                "3 - Moderately Strict",
                "4 - Balanced",
                "5 - Moderate",
                "6 - Lenient",
                "7 - Very Lenient"
            ],
            width=140,
            font=self.get_font(10),
            command=self._on_sensitivity_change
        )
        self.sensitivity_menu.pack(side="left", padx=(0, 2))
        self.sensitivity_menu.set("4 - Balanced")  # Default
        self._create_tooltip(self.sensitivity_menu, "Streak detection sensitivity: lower = fewer false positives")
        
        # Store current sensitivity value
        self.current_sensitivity = 0.5
        
        self.auto_mark_btn = ctk.CTkButton(
            analysis_frame, 
            text="⚠️ Auto-Mark Bad", 
            command=self.auto_mark_problematic,
            width=120, 
            font=self.get_font(11), 
            fg_color="#E74C3C", 
            hover_color="#C0392B"
        )
        self.auto_mark_btn.pack(side="left", padx=2)
        self.auto_mark_btn.configure(state="disabled")  # Enabled after analysis
        self._create_tooltip(self.auto_mark_btn, "Mark all problematic images for deletion")
        
        # Progress label for analysis
        self.analysis_progress_label = ctk.CTkLabel(analysis_frame, text="", font=self.get_font(10), text_color="#B0B0B0")
        self.analysis_progress_label.pack(side="right", padx=5)
        
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
        
        # Right panel - preview with zoom controls
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_columnconfigure(1, weight=0)
        right_panel.grid_rowconfigure(1, weight=1)
        
        preview_label = ctk.CTkLabel(right_panel, text="Preview", font=self.get_font(12, weight="bold"))
        preview_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        
        # Filename label (updates when file selected)
        self.fits_preview_filename = ctk.CTkLabel(right_panel, text="", font=self.get_font(11), text_color="#B0B0B0")
        self.fits_preview_filename.grid(row=0, column=0, sticky="w", padx=10, pady=(25, 5))
        
        # Preview image container
        preview_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        preview_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)
        
        self.fits_preview_label = ctk.CTkLabel(preview_container, text="Select a FITS file to preview", text_color="#B0B0B0")
        self.fits_preview_label.grid(row=0, column=0, sticky="nsew")
        
        # Zoom buttons on the right
        zoom_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        zoom_frame.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=10)
        
        self.zoom_in_btn = ctk.CTkButton(
            zoom_frame, 
            text="+", 
            width=30, 
            height=30,
            font=self.get_font(14, weight="bold"),
            command=self.zoom_fits_in,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.zoom_in_btn.pack(pady=(0, 5))
        self._create_tooltip(self.zoom_in_btn, "Zoom In")
        
        self.zoom_level_label = ctk.CTkLabel(
            zoom_frame, 
            text="100%", 
            font=self.get_font(10, weight="bold"), 
            width=40,
            cursor="hand2"
        )
        self.zoom_level_label.pack(pady=5)
        self.zoom_level_label.bind("<Button-1>", self._on_zoom_label_click)
        
        self.zoom_out_btn = ctk.CTkButton(
            zoom_frame, 
            text="−", 
            width=30, 
            height=30,
            font=self.get_font(14, weight="bold"),
            command=self.zoom_fits_out,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.zoom_out_btn.pack(pady=(5, 0))
        self._create_tooltip(self.zoom_out_btn, "Zoom Out")
        
        # Navigation buttons below the list
        nav_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        nav_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Previous",
            width=80,
            font=self.get_font(11),
            command=lambda: self.navigate_fits_files(-1),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.prev_btn.pack(side="left", padx=2)
        self._create_tooltip(self.prev_btn, "Previous Image")
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            width=80,
            font=self.get_font(11),
            command=lambda: self.navigate_fits_files(1),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.next_btn.pack(side="right", padx=2)
        self._create_tooltip(self.next_btn, "Next Image")
        
        # Status bar
        self.fits_status_label = ctk.CTkLabel(self.fits_viewer_frame, text="Ready", text_color="#E0E0E0")
        self.fits_status_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Bind keyboard navigation
        self.bind("<Up>", lambda e: self.navigate_fits_files(-1))
        self.bind("<Down>", lambda e: self.navigate_fits_files(1))
        
        # Initialize viewer state
        self.current_fits_directory = None
        self.fits_files = []
        self.selected_fits_index = -1
        self.marked_for_deletion = set()  # Set of indices marked for deletion
        self.fits_zoom_level = 1.0  # Zoom level (0.3 to 4.0)
        
        # Analysis results storage
        self.quality_reports = {}  # Dict mapping file index to QualityReport
        self.analysis_in_progress = False
    
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
        self.quality_reports = {}  # Clear analysis results
        self.fits_zoom_level = 1.0  # Reset zoom to 100%
        self._update_zoom_display()
        self.fits_preview_label.configure(text="Select a FITS file to preview", image=None)
        self.analysis_progress_label.configure(text="")
        self.auto_mark_btn.configure(state="disabled")
        
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
            self._update_nav_buttons()
        else:
            self.fits_status_label.configure(text="No FITS files found")
            self._update_nav_buttons()
    
    def refresh_fits_file_list(self):
        """Refresh the file list display with marked status and quality indicators."""
        # Clear listbox
        self.fits_file_listbox.delete(0, "end")
        
        # Add files with mark indicator and quality icons
        for i, file_path in enumerate(self.fits_files):
            # Build status indicators
            indicators = []
            
            # Mark status
            if i in self.marked_for_deletion:
                indicators.append("[✓]")
            else:
                indicators.append("[ ]")
            
            # Quality indicators from analysis
            if i in self.quality_reports:
                report = self.quality_reports[i]
                if report.has_streaks:
                    indicators.append("🛰️")
                if report.star_quality == 'poor':
                    indicators.append("⭐")
                elif report.star_quality == 'fair':
                    indicators.append("~")
            
            display_text = f"{' '.join(indicators)} {file_path.name}"
            self.fits_file_listbox.insert("end", display_text)
    
    
    def on_listbox_select(self, event):
        """Handle listbox selection change from mouse click."""
        selection = self.fits_file_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_fits_index = index
            file_path = self.fits_files[index]
            self.show_fits_preview(file_path)
            
            # Build status text with quality info if available
            status_text = f"Selected: {file_path.name}"
            if index in self.quality_reports:
                report = self.quality_reports[index]
                issues = []
                if report.has_streaks:
                    issues.append("🛰️ streaks")
                if report.star_quality == 'poor':
                    issues.append("⭐ poor stars")
                if issues:
                    status_text += f" | {' | '.join(issues)}"
                else:
                    status_text += " | ✓ good quality"
            
            self.fits_status_label.configure(text=status_text)
            self._update_nav_buttons()
    
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
            self._update_nav_buttons()
    
    def zoom_fits_in(self):
        """Zoom in on the FITS preview."""
        if self.fits_zoom_level < 2.5:
            self.fits_zoom_level = min(2.5, self.fits_zoom_level + 0.25)
            self._update_zoom_display()
            # Reload current image with new zoom
            if self.selected_fits_index >= 0 and self.fits_files:
                self.show_fits_preview(self.fits_files[self.selected_fits_index])
    
    def zoom_fits_out(self):
        """Zoom out on the FITS preview."""
        if self.fits_zoom_level > 0.3:
            self.fits_zoom_level = max(0.3, self.fits_zoom_level - 0.25)
            self._update_zoom_display()
            # Reload current image with new zoom
            if self.selected_fits_index >= 0 and self.fits_files:
                self.show_fits_preview(self.fits_files[self.selected_fits_index])
    
    def _update_zoom_display(self):
        """Update zoom level display and button states."""
        percentage = int(self.fits_zoom_level * 100)
        self.zoom_level_label.configure(text=f"{percentage}%")
        
        # Enable/disable buttons at limits
        if self.fits_zoom_level >= 2.5:
            self.zoom_in_btn.configure(state="disabled")
        else:
            self.zoom_in_btn.configure(state="normal")
        
        if self.fits_zoom_level <= 0.3:
            self.zoom_out_btn.configure(state="disabled")
        else:
            self.zoom_out_btn.configure(state="normal")
    
    def _on_zoom_label_click(self, event):
        """Handle click on zoom level label to allow manual zoom input."""
        self._show_zoom_input_dialog()
    
    def _show_zoom_input_dialog(self):
        """Show dialog for manual zoom percentage input."""
        import tkinter.simpledialog as simpledialog
        
        current_percent = int(self.fits_zoom_level * 100)
        
        # Create custom dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Set Zoom Level")
        dialog.geometry("250x150")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Label
        label = ctk.CTkLabel(dialog, text="Enter zoom percentage:", font=self.get_font(12))
        label.pack(pady=(20, 10))
        
        # Entry field
        entry = ctk.CTkEntry(dialog, font=self.get_font(12))
        entry.pack(padx=20, pady=5)
        entry.insert(0, str(current_percent))
        entry.select_range(0, "end")
        entry.focus()
        
        # Help text
        help_label = ctk.CTkLabel(dialog, text="Range: 30% - 250%", font=self.get_font(10), text_color="#B0B0B0")
        help_label.pack(pady=(0, 10))
        
        def apply_zoom():
            try:
                value = int(entry.get())
                # Clamp to valid range
                value = max(30, min(250, value))
                # Convert to scale factor
                self.fits_zoom_level = value / 100.0
                self._update_zoom_display()
                # Reload current image with new zoom
                if self.selected_fits_index >= 0 and self.fits_files:
                    self.show_fits_preview(self.fits_files[self.selected_fits_index])
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number (30-250)")
        
        def on_enter(event):
            apply_zoom()
        
        entry.bind("<Return>", on_enter)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=80, command=dialog.destroy, fg_color="#7F8C8D", hover_color="#616A6B")
        cancel_btn.pack(side="left", padx=5)
        
        ok_btn = ctk.CTkButton(btn_frame, text="OK", width=80, command=apply_zoom, fg_color="#E67E22", hover_color="#D35400")
        ok_btn.pack(side="left", padx=5)
    
    def _update_nav_buttons(self):
        """Update navigation button states based on current position."""
        if not self.fits_files:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            return
        
        # Disable prev button at first file
        if self.selected_fits_index <= 0:
            self.prev_btn.configure(state="disabled")
        else:
            self.prev_btn.configure(state="normal")
        
        # Disable next button at last file
        if self.selected_fits_index >= len(self.fits_files) - 1:
            self.next_btn.configure(state="disabled")
        else:
            self.next_btn.configure(state="normal")
    
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
                
                # Resize to fit preview area with zoom applied
                # Base max size 800x650, multiplied by zoom level
                base_width, base_height = 800, 650
                zoomed_width = int(base_width * self.fits_zoom_level)
                zoomed_height = int(base_height * self.fits_zoom_level)
                img.thumbnail((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
                
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
    
    def _on_sensitivity_change(self, choice):
        """Handle sensitivity level change from dropdown."""
        # Map choice to sensitivity value
        sensitivity_map = {
            "1 - Very Strict": 0.2,
            "2 - Strict": 0.3,
            "3 - Moderately Strict": 0.4,
            "4 - Balanced": 0.5,
            "5 - Moderate": 0.7,
            "6 - Lenient": 1.0,
            "7 - Very Lenient": 1.5
        }
        
        self.current_sensitivity = sensitivity_map.get(choice, 0.5)
        logger.info(f"Analysis sensitivity set to {choice} ({self.current_sensitivity})")
        
        # If we have cached reports, re-apply the new threshold
        if hasattr(self, 'quality_reports') and self.quality_reports:
            self._reapply_analysis_threshold()
    
    def _reapply_analysis_threshold(self):
        """Re-apply current sensitivity threshold to cached analysis results."""
        try:
            from core.image_quality import ImageQualityAnalyzer
            
            analyzer = ImageQualityAnalyzer(streak_sensitivity=self.current_sensitivity)
            
            # Re-apply threshold to all cached reports
            updated_count = 0
            for idx, report in self.quality_reports.items():
                if hasattr(report, 'raw_streak_ratio') and report.raw_streak_ratio > 0:
                    new_report = analyzer.reapply_threshold(report)
                    self.quality_reports[idx] = new_report
                    if new_report.is_problematic != report.is_problematic:
                        updated_count += 1
            
            # Refresh the file list display
            self.refresh_fits_file_list()
            
            # Update status
            status_msg = f"Re-applied threshold: {updated_count} files changed status"
            self.fits_status_label.configure(text=status_msg)
            logger.info(status_msg)
            
        except Exception as e:
            logger.error(f"Error re-applying threshold: {e}")
    
    def analyze_all_fits(self):
        """Run quality analysis on all FITS files in the current directory."""
        if not self.fits_files:
            messagebox.showinfo("No Files", "No FITS files to analyze. Please select a directory first.")
            return
        
        if self.analysis_in_progress:
            messagebox.showinfo("Analysis Running", "Analysis is already in progress.")
            return
        
        self.analysis_in_progress = True
        self.analyze_all_btn.configure(state="disabled")
        self.analysis_progress_label.configure(text="Starting analysis...")
        
        # Run analysis in background thread
        thread = threading.Thread(target=self._analyze_all_thread)
        thread.daemon = True
        thread.start()
    
    def _analyze_all_thread(self):
        """Background thread for analyzing all files."""
        try:
            from astropy.io import fits
            from core.image_quality import ImageQualityAnalyzer
            
            total = len(self.fits_files)
            logger.info(f"Starting analysis of {total} files...")
            
            # Use fast mode for batch analysis with selected sensitivity
            analyzer = ImageQualityAnalyzer(streak_sensitivity=self.current_sensitivity)
            logger.info("Analyzer initialized successfully (fast mode, strict sensitivity)")
            
            for i, file_path in enumerate(self.fits_files):
                try:
                    # Update progress every file
                    progress_text = f"Analyzing {i+1}/{total}..."
                    self.after(0, lambda t=progress_text: self._safe_update_progress(t))
                    
                    # Load FITS data
                    with fits.open(file_path) as hdul:
                        data = hdul[0].data
                        
                        if data is not None:
                            # Analyze in fast mode for speed
                            report = analyzer.analyze_image(data, file_path, fast_mode=True)
                            self.quality_reports[i] = report
                            
                            # Log progress every 10 files
                            if (i + 1) % 10 == 0:
                                logger.info(f"Analyzed {i+1}/{total} files")
                        else:
                            logger.warning(f"No data in {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
            
            logger.info(f"Analysis complete. Processed {len(self.quality_reports)} files.")
            # Analysis complete - update UI on main thread
            self.after(0, self._analysis_complete)
            
        except Exception as e:
            logger.error(f"Analysis thread error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.after(0, lambda: self._analysis_error(str(e)))
    
    def _safe_update_progress(self, text: str):
        """Safely update progress label from any thread."""
        try:
            if hasattr(self, 'analysis_progress_label') and self.analysis_progress_label.winfo_exists():
                self.analysis_progress_label.configure(text=text)
        except Exception as e:
            logger.debug(f"Failed to update progress: {e}")
    
    def _analysis_complete(self):
        """Called when analysis is complete."""
        self.analysis_in_progress = False
        self.analyze_all_btn.configure(state="normal")
        
        # Count issues
        problematic = sum(1 for r in self.quality_reports.values() if r.is_problematic)
        total = len(self.quality_reports)
        
        self.analysis_progress_label.configure(text=f"Done: {problematic}/{total} problematic")
        
        # Enable auto-mark button if there are problematic files
        if problematic > 0:
            self.auto_mark_btn.configure(state="normal")
        
        # Refresh list to show indicators
        self.refresh_fits_file_list()
        
        # Show summary dialog
        if problematic > 0:
            streaks = sum(1 for r in self.quality_reports.values() if r.has_streaks)
            poor_stars = sum(1 for r in self.quality_reports.values() if r.star_quality == 'poor')
            messagebox.showinfo(
                "Analysis Complete",
                f"Analyzed {total} images\n\n"
                f"Issues found:\n"
                f"  🛰️ {streaks} with satellite/airplane streaks\n"
                f"  ⭐ {poor_stars} with poor star quality\n\n"
                f"Use '⚠️ Auto-Mark Bad' to mark problematic images for deletion."
            )
        else:
            messagebox.showinfo("Analysis Complete", f"Analyzed {total} images. No issues found!")
    
    def _analysis_error(self, error_msg: str):
        """Called when analysis encounters an error."""
        self.analysis_in_progress = False
        self.analyze_all_btn.configure(state="normal")
        self.analysis_progress_label.configure(text="Analysis failed")
        messagebox.showerror("Analysis Error", f"Failed to analyze images:\n{error_msg}")
    
    def auto_mark_problematic(self):
        """Automatically mark all problematic images for deletion."""
        if not self.quality_reports:
            messagebox.showinfo("No Analysis", "Please run analysis first.")
            return
        
        marked = 0
        for i, report in self.quality_reports.items():
            if report.is_problematic:
                self.marked_for_deletion.add(i)
                marked += 1
        
        self.refresh_fits_file_list()
        self.fits_status_label.configure(text=f"Auto-marked {marked} problematic image(s) for deletion")
        
        if marked > 0:
            messagebox.showinfo(
                "Auto-Mark Complete",
                f"Marked {marked} problematic image(s) for deletion.\n\n"
                f"Click '🗑️ Delete Marked' to remove them, or use '✓ Mark' to unmark individual files."
            )
    
    def show_quality_details(self):
        """Show quality details for the currently selected image."""
        if self.selected_fits_index < 0:
            return
        
        if self.selected_fits_index not in self.quality_reports:
            return
        
        report = self.quality_reports[self.selected_fits_index]
        
        # Build details text
        details = f"Quality Report for: {report.file_path.name}\n\n"
        
        if report.has_streaks:
            details += f"🛰️ Streaks: {report.streak_count} detected (confidence: {report.streak_confidence:.1%})\n"
        else:
            details += "✓ No streaks detected\n"
        
        details += f"\n⭐ Star Quality: {report.star_quality.upper()}\n"
        details += f"   Average FWHM: {report.avg_fwhm:.2f} pixels\n"
        details += f"   Eccentricity: {report.avg_eccentricity:.2f}\n"
        
        if report.background_gradient > 0.3:
            details += f"\n⚠️ Uneven background (gradient: {report.background_gradient:.2f})\n"
        
        if report.issues:
            details += f"\nIssues:\n"
            for issue in report.issues:
                details += f"  • {issue}\n"
        
        if report.is_problematic:
            details += "\n⚠️ This image is flagged as problematic."
        else:
            details += "\n✓ This image looks good."
        
        # Show in dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Image Quality Details")
        dialog.geometry("400x400")
        dialog.transient(self)
        
        textbox = ctk.CTkTextbox(dialog, wrap="word")
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", details)
        textbox.configure(state="disabled")
        
        close_btn = ctk.CTkButton(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)

    def _create_settings_frame(self):
        """Create Settings mode frame (hidden initially)."""
        self.settings_frame = ctk.CTkFrame(self.content_frame)
        
        # Title
        settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=self.get_font(16, weight="bold"))
        settings_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Scrollable frame for settings content - fill all available space
        scroll_frame = ctk.CTkScrollableFrame(self.settings_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Location Settings Section
        location_frame = ctk.CTkFrame(scroll_frame)
        location_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        location_label = ctk.CTkLabel(location_frame, text="Location Settings", font=self.get_font(14, weight="bold"))
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
            font=self.get_font(10),
            text_color="gray"
        )
        threshold_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Timezone Settings Section
        timezone_frame = ctk.CTkFrame(scroll_frame)
        timezone_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        timezone_label = ctk.CTkLabel(timezone_frame, text="Timezone Settings", font=self.get_font(14, weight="bold"))
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
        
        coord_label = ctk.CTkLabel(coord_frame, text="Coordinate Format", font=self.get_font(14, weight="bold"))
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
            font=self.get_font(10),
            text_color="gray"
        )
        coord_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Disclaimer Section
        disclaimer_frame = ctk.CTkFrame(scroll_frame)
        disclaimer_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        disclaimer_label = ctk.CTkLabel(disclaimer_frame, text="Disclaimer", font=self.get_font(14, weight="bold"))
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
            font=self.get_font(10),
            text_color="gray"
        )
        disclaimer_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Text Scale Section
        text_scale_frame = ctk.CTkFrame(scroll_frame)
        text_scale_frame.pack(fill="x", padx=5, pady=(0, 15))
        
        text_scale_label = ctk.CTkLabel(text_scale_frame, text="Text Size", font=self.get_font(14, weight="bold"))
        text_scale_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        text_scale_menu_label = ctk.CTkLabel(text_scale_frame, text="UI Text Scale:")
        text_scale_menu_label.pack(anchor="w", padx=10, pady=(5, 2))
        
        self.settings_text_scale_menu = ctk.CTkOptionMenu(
            text_scale_frame,
            values=["Small (0.8x)", "Normal (1.0x)", "Large (1.2x)", "Extra Large (1.4x)"]
        )
        self.settings_text_scale_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Map text scale setting to menu value
        scale_setting = self.settings.get_text_scale()
        if scale_setting <= 0.85:
            self.settings_text_scale_menu.set("Small (0.8x)")
        elif scale_setting >= 1.35:
            self.settings_text_scale_menu.set("Extra Large (1.4x)")
        elif scale_setting >= 1.15:
            self.settings_text_scale_menu.set("Large (1.2x)")
        else:
            self.settings_text_scale_menu.set("Normal (1.0x)")
        
        text_scale_help = ctk.CTkLabel(
            text_scale_frame,
            text="Changes take effect after restarting the application",
            font=self.get_font(10),
            text_color="gray"
        )
        text_scale_help.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Button frame for Save and Reset
        button_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15), side="bottom")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Reset to Defaults button
        reset_button = ctk.CTkButton(
            button_frame,
            text="↺ Reset to Defaults",
            command=self.reset_settings_to_defaults,
            height=40,
            fg_color="#7F8C8D",
            hover_color="#616A6B",
            font=self.get_font(12)
        )
        reset_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self.save_main_settings,
            height=40,
            fg_color="#E67E22",
            hover_color="#D35400",
            font=self.get_font(14, weight="bold")
        )
        save_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")
    
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
            
            # Save text scale
            scale_value = self.settings_text_scale_menu.get()
            if "0.8" in scale_value:
                self.settings.set_text_scale(0.8)
            elif "1.2" in scale_value:
                self.settings.set_text_scale(1.2)
            elif "1.4" in scale_value:
                self.settings.set_text_scale(1.4)
            else:
                self.settings.set_text_scale(1.0)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            logger.info("Settings saved from main view")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings_to_defaults(self):
        """Reset all settings to default values with confirmation."""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\n\n"
            "This will:\n"
            "• Reset location threshold to 0.005°\n"
            "• Reset timezone to UTC\n"
            "• Reset coordinate format to Decimal Degrees\n"
            "• Reset text scale to Normal (1.0x)\n"
            "• Clear disclaimer acknowledgment\n\n"
            "Settings will be saved immediately.",
            icon='warning'
        )
        
        if result:
            try:
                # Reset settings in backend
                self.settings.reset_to_defaults()
                
                # Update UI to reflect defaults
                self.settings_threshold_entry.delete(0, "end")
                self.settings_threshold_entry.insert(0, "0.005")
                
                self.settings_timezone_menu.set("UTC")
                
                self.settings_coord_menu.set("Decimal Degrees")
                
                self.settings_text_scale_menu.set("Normal (1.0x)")
                
                messagebox.showinfo(
                    "Settings Reset",
                    "All settings have been reset to defaults.\n\n"
                    "Note: Text scale changes require restarting the application."
                )
                logger.info("Settings reset to defaults via UI")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
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
            # Hide normal mode panels, show settings in left panel only
            self.left_panel.grid_forget()
            self.fits_viewer_frame.grid_forget()
            # Keep separator visible
            self.separator.grid(row=0, column=1, sticky="ns")
            # Show/hide console based on state
            if self.console_visible:
                self.right_panel.grid(row=0, column=2, sticky="nsew")
            else:
                self.right_panel.grid_forget()
            self.settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
            self.progress_label.configure(text="Settings mode - configure app settings and click Save")
            
            # Refresh disclaimer switch state (may have changed via disclaimer dialog)
            if not self.settings.get_disclaimer_acknowledged():
                self.disclaimer_switch.select()
            else:
                self.disclaimer_switch.deselect()
        elif mode == 'fits_viewer':
            # Hide normal mode panels, show fits viewer in left panel only
            self.left_panel.grid_forget()
            self.settings_frame.grid_forget()
            # Keep separator visible
            self.separator.grid(row=0, column=1, sticky="ns")
            # Show/hide console based on state
            if self.console_visible:
                self.right_panel.grid(row=0, column=2, sticky="nsew")
            else:
                self.right_panel.grid_forget()
            self.fits_viewer_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
            self.progress_label.configure(text="FITS Viewer - browse and preview FITS files")
        else:
            # Hide settings and fits viewer, show normal layout
            self.settings_frame.grid_forget()
            self.fits_viewer_frame.grid_forget()
            # Ensure separator is visible
            self.separator.grid(row=0, column=1, sticky="ns")
            # Show/hide console based on state
            if self.console_visible:
                self.right_panel.grid(row=0, column=2, sticky="nsew")
                self.content_frame.grid_columnconfigure(2, weight=1)
            else:
                self.right_panel.grid_forget()
                self.content_frame.grid_columnconfigure(2, weight=0)
            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
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
    
    def _start_resize(self, event):
        """Start resizing the panels when separator is clicked."""
        self._resizing = True
        self._resize_start_x = event.x_root
        self._resize_start_width = self.left_panel.winfo_width()
    
    def _on_resize(self, event):
        """Handle panel resizing during drag."""
        if not self._resizing:
            return
        
        # Calculate the delta in pixels
        delta = event.x_root - self._resize_start_x
        
        # Calculate new width for left panel
        new_width = self._resize_start_width + delta
        
        # Set minimum and maximum widths (in pixels)
        min_width = 200
        max_width = self.content_frame.winfo_width() - 200 - self.separator.winfo_width()
        
        # Clamp the width
        new_width = max(min_width, min(new_width, max_width))
        
        # Calculate the new grid column weights based on the new width
        total_width = self.content_frame.winfo_width()
        if total_width > 0:
            separator_width = self.separator.winfo_width()
            left_weight = new_width / total_width
            right_weight = (total_width - new_width - separator_width) / total_width
            
            # Update grid column weights (must be integers)
            self.content_frame.grid_columnconfigure(0, weight=int(left_weight * 100))
            self.content_frame.grid_columnconfigure(2, weight=int(right_weight * 100))
    
    def _end_resize(self, event):
        """End resizing when mouse button is released."""
        self._resizing = False
    
    def toggle_console(self):
        """Toggle the visibility of the console panel."""
        if self.console_visible:
            # Hide console
            self.right_panel.grid_forget()
            self.content_frame.grid_columnconfigure(2, weight=0)
            self.console_toggle_btn.configure(text="◀")
            self.console_visible = False
            logger.info("Console collapsed")
        else:
            # Show console
            self.right_panel.grid(row=0, column=2, sticky="nsew")
            self.content_frame.grid_columnconfigure(2, weight=1)
            self.console_toggle_btn.configure(text="▶")
            self.console_visible = True
            logger.info("Console expanded")
    
    def _show_folder_selection_dialog(self, folders: list) -> list:
        """Show folder selection dialog and return selected folders.
        
        Args:
            folders: List of folder paths to show in dialog
            
        Returns:
            List of selected folders, or empty list if cancelled
        """
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
        
        return selected_folders
    
    def _show_file_type_selection_dialog(self, file_type_counts: dict) -> set:
        """Show file type selection dialog and return selected file types.
        
        Args:
            file_type_counts: Dictionary mapping file extensions to counts
            
        Returns:
            Set of selected file extensions, or None if cancelled
        """
        selected_file_types = None
        file_type_dialog_result = threading.Event()
        
        def show_file_type_dialog():
            nonlocal selected_file_types
            dialog = FileTypeSelectionDialog(self, file_type_counts)
            dialog.wait_window()
            if dialog.result == "process":
                selected_file_types = dialog.get_selected_types()
            file_type_dialog_result.set()
        
        # Show dialog on main thread and wait for result
        self.after(0, show_file_type_dialog)
        file_type_dialog_result.wait()
        
        return selected_file_types
    
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
        # Position directly under Import button
        btn_x = self.import_menu_btn.winfo_rootx()
        btn_y = self.import_menu_btn.winfo_rooty()
        btn_height = self.import_menu_btn.winfo_height()
        menu.geometry(f"220x110+{btn_x}+{btn_y + btn_height}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        menu.configure(fg_color="#E67E22")  # Match menu bar background
        
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
        
        self._create_dropdown_menu_item(menu, "Direct", direct_flow).pack(fill="x", padx=5, pady=2)
        self._create_menu_separator(menu)
        self._create_dropdown_menu_item(menu, "Intermediate", intermediate_flow).pack(fill="x", padx=5, pady=2)
        self._create_menu_separator(menu)
        self._create_dropdown_menu_item(menu, "Copy Planetary & Scenery", planetary_scenery_flow).pack(fill="x", padx=5, pady=2)
        
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
        # Position directly under Tools button
        btn_x = self.tools_menu_btn.winfo_rootx()
        btn_y = self.tools_menu_btn.winfo_rooty()
        btn_height = self.tools_menu_btn.winfo_height()
        menu.geometry(f"200x70+{btn_x}+{btn_y + btn_height}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        menu.configure(fg_color="#E67E22")  # Match menu bar background
        
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
        
        self._create_dropdown_menu_item(menu, "Analyze Projects", analyze_and_close).pack(fill="x", padx=5, pady=2)
        self._create_menu_separator(menu)
        self._create_dropdown_menu_item(menu, "FITS Viewer", fits_viewer_and_close).pack(fill="x", padx=5, pady=2)
        
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
        # Position directly under Help button
        btn_x = self.help_menu_btn.winfo_rootx()
        btn_y = self.help_menu_btn.winfo_rooty()
        btn_height = self.help_menu_btn.winfo_height()
        menu.geometry(f"200x70+{btn_x}+{btn_y + btn_height}")
        menu.overrideredirect(True)
        menu.transient(self)
        menu.lift()
        menu.configure(fg_color="#E67E22")  # Match menu bar background
        
        def close_menu():
            if hasattr(self, '_help_menu') and self._help_menu and self._help_menu.winfo_exists():
                self._help_menu.destroy()
            self._help_menu = None
        
        def open_docs():
            import webbrowser
            webbrowser.open("https://docs.google.com/document/d/1ZjtI4f97ZZ3ev8C_yMDOoG3-o8_H4E_rZu3ecQxJZy0/edit?tab=t.hewxpg77x81j")
            close_menu()
        
        def about_and_close():
            close_menu()
            self.lift()
            self.after(100, lambda: self.show_mode('about'))
        
        self._create_dropdown_menu_item(menu, "Documentation", open_docs).pack(fill="x", padx=5, pady=2)
        self._create_menu_separator(menu)
        self._create_dropdown_menu_item(menu, "About", about_and_close).pack(fill="x", padx=5, pady=2)
        
        menu.bind("<Escape>", lambda e: close_menu())
        menu.focus_set()
    
    def _create_about_frame(self):
        """Create About frame (hidden initially)."""
        self.about_frame = ctk.CTkFrame(self.left_panel)
        
        about_title = ctk.CTkLabel(self.about_frame, text="ℹ️ About", font=self.get_font(22, weight="bold"))
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
                 "Version: 1.4\n"
                 "Created by Guy Ronen",
            font=self.get_font(16),
            text_color="#B0B0B0",
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

