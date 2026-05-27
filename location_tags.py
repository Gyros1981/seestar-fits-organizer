"""
Location Tags Storage Module
Manages local storage for location tags.
"""

import json
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationTags:
    """Manages location tags stored in a local JSON file."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize location tags storage.
        
        Args:
            storage_path: Path to the JSON file for storing tags. Defaults to location_tags.json in the same directory.
        """
        if storage_path is None:
            storage_path = Path(__file__).parent / "location_tags.json"
        
        self.storage_path = storage_path
        self.tags: Dict[str, Dict] = {}  # {(lat, lon): {name, notes, created_at}}
        self._load_tags()
    
    def _load_tags(self):
        """Load tags from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to tuples
                    self.tags = {}
                    for key, value in data.items():
                        # Parse key which should be "lat,lon" format
                        try:
                            lat, lon = key.split(',')
                            self.tags[f"{lat},{lon}"] = value
                        except ValueError:
                            logger.warning(f"Invalid tag key format: {key}")
                logger.info(f"Loaded {len(self.tags)} location tags")
        except Exception as e:
            logger.error(f"Failed to load location tags: {e}")
            self.tags = {}
    
    def _save_tags(self):
        """Save tags to storage file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.tags, f, indent=2)
            logger.info(f"Saved {len(self.tags)} location tags")
        except Exception as e:
            logger.error(f"Failed to save location tags: {e}")
    
    def get_tag(self, lat: str, lon: str) -> Optional[Dict]:
        """Get tag for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tag dictionary with 'name', 'notes', 'created_at' or None
        """
        key = f"{lat},{lon}"
        return self.tags.get(key)
    
    def set_tag(self, lat: str, lon: str, name: str, notes: str = ""):
        """Set tag for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            name: Custom name for the location
            notes: Optional notes about the location
        """
        from datetime import datetime
        
        key = f"{lat},{lon}"
        self.tags[key] = {
            'name': name,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        self._save_tags()
    
    def delete_tag(self, lat: str, lon: str):
        """Delete tag for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        key = f"{lat},{lon}"
        if key in self.tags:
            del self.tags[key]
            self._save_tags()
    
    def get_all_tags(self) -> Dict[str, Dict]:
        """Get all tags.
        
        Returns:
            Dictionary of all tags
        """
        return self.tags.copy()
