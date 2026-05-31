"""
Platform Utility Module

Provides platform detection and platform-specific path handling.
Supports Windows, macOS, and Linux.
"""

import sys
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_platform() -> str:
    """
    Detect the current operating system.
    
    Returns:
        'windows', 'darwin' (macOS), or 'linux'
    """
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'darwin'
    else:
        return 'linux'


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform() == 'windows'


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform() == 'darwin'


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform() == 'linux'


def get_settings_dir(app_name: str = "SeestarFITS") -> Path:
    r"""
    Get the platform-appropriate directory for application settings.
    
    Args:
        app_name: Name of the application (used for folder naming)
        
    Returns:
        Path to settings directory
        
    Platform paths:
        - Windows: %APPDATA%\SeestarFITS\
        - macOS: ~/Library/Application Support/SeestarFITS/
        - Linux: ~/.config/SeestarFITS/
    """
    platform = get_platform()
    
    if platform == 'windows':
        # Windows: Use %APPDATA%
        app_data = Path.home() / "AppData" / "Roaming"
        settings_dir = app_data / app_name
    elif platform == 'darwin':
        # macOS: Use Application Support
        settings_dir = Path.home() / "Library" / "Application Support" / app_name
    else:
        # Linux: Use XDG config directory
        xdg_config = Path.home() / ".config"
        settings_dir = xdg_config / app_name
    
    # Create directory if it doesn't exist
    settings_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Settings directory: {settings_dir}")
    
    return settings_dir


def get_logs_dir(app_name: str = "SeestarFITS") -> Path:
    r"""
    Get the platform-appropriate directory for log files.
    
    Args:
        app_name: Name of the application
        
    Returns:
        Path to logs directory
        
    Platform paths:
        - Windows: %APPDATA%\SeestarFITS\logs\
        - macOS: ~/Library/Logs/SeestarFITS/
        - Linux: ~/.local/share/SeestarFITS/logs/
    """
    platform = get_platform()
    
    if platform == 'windows':
        app_data = Path.home() / "AppData" / "Roaming"
        logs_dir = app_data / app_name / "logs"
    elif platform == 'darwin':
        # macOS has a dedicated Logs folder
        logs_dir = Path.home() / "Library" / "Logs" / app_name
    else:
        # Linux: Use .local/share
        local_share = Path.home() / ".local" / "share"
        logs_dir = local_share / app_name / "logs"
    
    # Create directory if it doesn't exist
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Logs directory: {logs_dir}")
    
    return logs_dir


def get_temp_dir(app_name: str = "SeestarFITS") -> Path:
    """
    Get the platform-appropriate directory for temporary files.
    
    Args:
        app_name: Name of the application
        
    Returns:
        Path to temp directory
    """
    import tempfile
    
    platform = get_platform()
    
    if platform == 'windows':
        # Windows temp
        temp_dir = Path(tempfile.gettempdir()) / app_name
    elif platform == 'darwin':
        # macOS temp (Darwin uses standard temp)
        temp_dir = Path(tempfile.gettempdir()) / app_name
    else:
        # Linux temp
        temp_dir = Path(tempfile.gettempdir()) / app_name
    
    # Create directory if it doesn't exist
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    return temp_dir


def get_documents_dir() -> Path:
    """
    Get the user's Documents folder.
    
    Returns:
        Path to Documents directory
    """
    # This is a reasonable default for all platforms
    return Path.home() / "Documents"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for the current platform.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for the current platform
    """
    platform = get_platform()
    
    # Characters invalid on Windows
    if platform == 'windows':
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
    else:
        # macOS and Linux: mainly / is invalid
        filename = filename.replace('/', '_')
    
    return filename


def get_bundle_resource_path(relative_path: str) -> Optional[Path]:
    """
    Get path to a resource file when running in a bundled app.
    
    This handles both:
    - Running as script (development)
    - Running as PyInstaller bundle (.app on Mac, .exe on Windows)
    
    Args:
        relative_path: Path relative to bundle/resource root
        
    Returns:
        Path to resource, or None if not found
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        bundle_dir = Path(sys.executable).parent
        
        # On macOS, the bundle structure is different
        if is_macos():
            # In a .app bundle, executable is at:
            # MyApp.app/Contents/MacOS/MyApp
            # Resources should be at:
            # MyApp.app/Contents/Resources/
            if (bundle_dir.parent / "Resources").exists():
                resource_dir = bundle_dir.parent / "Resources"
            else:
                resource_dir = bundle_dir
        else:
            # Windows/Linux: resources next to executable
            resource_dir = bundle_dir
        
        resource_path = resource_dir / relative_path
        if resource_path.exists():
            return resource_path
        
        # Try _MEIPASS (PyInstaller temp extraction dir)
        if hasattr(sys, '_MEIPASS'):
            meipass_path = Path(sys._MEIPASS) / relative_path
            if meipass_path.exists():
                return meipass_path
    
    # Running as script - look relative to script location
    script_dir = Path(__file__).parent
    dev_path = script_dir / relative_path
    if dev_path.exists():
        return dev_path
    
    return None


# Convenience constants for quick checks
PLATFORM = get_platform()
IS_WINDOWS = is_windows()
IS_MACOS = is_macos()
IS_LINUX = is_linux()
