"""
Utility Functions Module

Contains common utility functions used across the application.
"""

import sys
import logging
from pathlib import Path
from typing import Optional


def get_storage_path(filename: str) -> Path:
    """
    Get the appropriate storage path for a file.
    
    Detects if running as a PyInstaller bundle or as a script,
    and returns the appropriate directory path.
    
    Args:
        filename: The filename to use for the storage file
        
    Returns:
        Path to the storage file location
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as bundled executable
            return Path(sys.executable).parent / filename
        else:
            # Running as script
            return Path(__file__).parent / filename
    except Exception:
        # Fallback to current directory
        return Path.cwd() / filename


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
