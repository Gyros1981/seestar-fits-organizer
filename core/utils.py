"""
Utility Functions Module

Contains common utility functions used across the application.
"""

import os
import sys
import shutil
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


def extended_path(path: Path) -> str:
    """Return a filesystem path string that bypasses the Windows MAX_PATH limit.

    Windows APIs reject paths longer than 260 characters unless they use the
    extended-length ``\\\\?\\`` prefix. Seestar object names contain spaces and
    long timestamped filenames, so nested Projects paths can exceed this limit
    and cause copies to fail. On non-Windows platforms the plain path is
    returned unchanged.

    Args:
        path: The path to normalize.

    Returns:
        A string path safe to pass to filesystem calls.
    """
    p = os.path.abspath(str(path))
    if os.name == 'nt' and not p.startswith('\\\\?\\'):
        if p.startswith('\\\\'):
            # UNC path: \\server\share -> \\?\UNC\server\share
            p = '\\\\?\\UNC\\' + p[2:]
        else:
            p = '\\\\?\\' + p
    return p


def safe_copy(src: Path, dst: Path) -> None:
    """Copy a single file preserving metadata, resilient to long paths.

    Uses :func:`extended_path` so copies do not fail on deeply nested Windows
    paths. Raises the underlying exception on failure so callers can record and
    report which file could not be copied without aborting the whole batch.

    Args:
        src: Source file path.
        dst: Destination file path.
    """
    shutil.copy2(extended_path(src), extended_path(dst))


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
