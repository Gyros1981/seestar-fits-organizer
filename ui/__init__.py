"""
UI Components Package for Seestar FITS Organizer.

This package contains all UI windows and dialogs used by the application.
"""

from .disclaimer_window import DisclaimerWindow
from .folder_selection_dialog import FolderSelectionWindow
from .analysis_window import AnalysisWindow
from .preview_window import PreviewWindow
from .file_type_selection_dialog import FileTypeSelectionDialog, detect_file_types_in_directories
from .main_window import SeestarApp

__all__ = [
    'DisclaimerWindow',
    'FolderSelectionWindow',
    'AnalysisWindow',
    'PreviewWindow',
    'FileTypeSelectionDialog',
    'detect_file_types_in_directories',
    'SeestarApp'
]
