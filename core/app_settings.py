"""
Application Settings Module
Manages application-wide settings.
"""

import json
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppSettings:
    """Manages application settings stored in a local JSON file."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize application settings storage.
        
        Args:
            storage_path: Path to the JSON file for storing settings. Defaults to app_settings.json in the executable directory.
        """
        if storage_path is None:
            # Try to use the directory of the executable (if bundled) or the script
            try:
                # If running as a PyInstaller bundle
                import sys
                if getattr(sys, 'frozen', False):
                    # Running as bundled executable
                    storage_path = Path(sys.executable).parent / "app_settings.json"
                else:
                    # Running as script
                    storage_path = Path(__file__).parent / "app_settings.json"
            except Exception:
                # Fallback to current directory
                storage_path = Path.cwd() / "app_settings.json"
        
        self.storage_path = storage_path
        
        # Default settings
        self.settings: Dict = {
            'location_threshold': 0.005,  # degrees
            'timezone': 'UTC',  # UTC, PST, EST, or Local
            'disclaimer_acknowledged': False,  # Whether user has acknowledged the disclaimer
            'coordinate_format': 'degrees',  # 'degrees' or 'hms' (hours/minutes/seconds)
            'text_scale': 1.0,  # UI text scale factor (0.8 to 1.4)
        }
        
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    self.settings.update(loaded_settings)
                logger.info(f"Loaded settings from {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            # Keep defaults (already set in __init__)
    
    def _save_settings(self):
        """Save settings to storage file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved settings to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self._save_settings()
    
    def get_location_threshold(self) -> float:
        """Get the location grouping threshold in degrees."""
        return self.settings.get('location_threshold', 0.005)
    
    def set_location_threshold(self, threshold: float):
        """Set the location grouping threshold.
        
        Args:
            threshold: Threshold in degrees
        """
        self.settings['location_threshold'] = threshold
        self._save_settings()
    
    def get_timezone(self) -> str:
        """Get the timezone setting."""
        return self.settings.get('timezone', 'PST')
    
    def set_timezone(self, timezone: str):
        """Set the timezone.
        
        Args:
            timezone: Timezone string (UTC, PST, EST, or Local)
        """
        self.settings['timezone'] = timezone
        self._save_settings()
    
    def get_disclaimer_acknowledged(self) -> bool:
        """Get whether the disclaimer has been acknowledged."""
        return self.settings.get('disclaimer_acknowledged', False)
    
    def set_disclaimer_acknowledged(self, acknowledged: bool):
        """Set whether the disclaimer has been acknowledged.
        
        Args:
            acknowledged: True if acknowledged, False otherwise
        """
        self.settings['disclaimer_acknowledged'] = acknowledged
        self._save_settings()
    
    def get_coordinate_format(self) -> str:
        """Get the coordinate format setting."""
        return self.settings.get('coordinate_format', 'degrees')
    
    def set_coordinate_format(self, format_type: str):
        """Set the coordinate format.
        
        Args:
            format_type: 'degrees' or 'hms' (hours/minutes/seconds for RA, deg/min/sec for DEC)
        """
        if format_type in ['degrees', 'hms']:
            self.settings['coordinate_format'] = format_type
            self._save_settings()
    
    def get_text_scale(self) -> float:
        """Get the UI text scale factor."""
        return self.settings.get('text_scale', 1.0)
    
    def set_text_scale(self, scale: float):
        """Set the UI text scale factor.
        
        Args:
            scale: Scale factor between 0.8 and 1.4
        """
        # Clamp to valid range
        scale = max(0.8, min(1.4, scale))
        self.settings['text_scale'] = scale
        self._save_settings()
