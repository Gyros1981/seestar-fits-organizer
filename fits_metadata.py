"""
FITS Metadata Extraction Module
Extracts metadata from FITS files for astrophotography processing.
"""

from astropy.io import fits
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FitsMetadata:
    """Container for FITS file metadata."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.exptime: Optional[float] = None
        self.date_obs: Optional[str] = None
        self.object: Optional[str] = None
        self.imagetyp: Optional[str] = None
        self.filter: Optional[str] = None
        self.gain: Optional[float] = None
        self.iso: Optional[int] = None
        self.temp: Optional[float] = None
        self.xbinning: Optional[int] = None
        self.ybinning: Optional[int] = None
        self.ra: Optional[str] = None
        self.dec: Optional[str] = None
        self.focallen: Optional[float] = None
        self.airmass: Optional[float] = None
        # Capture location (site)
        self.site: Optional[str] = None
        self.longitude: Optional[str] = None
        self.latitude: Optional[str] = None
        
        self._extract_metadata()
    
    def _extract_metadata(self) -> None:
        """Extract metadata from FITS header."""
        try:
            with fits.open(self.filepath) as hdul:
                header = hdul[0].header
                
                # Required fields
                self.exptime = self._get_float(header, 'EXPTIME')
                self.date_obs = self._get_str(header, 'DATE-OBS')
                self.object = self._get_str(header, 'OBJECT')
                self.imagetyp = self._get_str(header, 'IMAGETYP')
                self.filter = self._get_str(header, 'FILTER')
                self.gain = self._get_float(header, 'GAIN')
                self.iso = self._get_int(header, 'ISO')
                
                # Temperature - try multiple common header keys
                self.temp = (self._get_float(header, 'CCD-TEMP') or 
                           self._get_float(header, 'TEMP') or
                           self._get_float(header, 'SENSOR-TEMP'))
                
                self.xbinning = self._get_int(header, 'XBINNING')
                self.ybinning = self._get_int(header, 'YBINNING')
                
                # Optional fields
                self.ra = self._get_str(header, 'RA')
                self.dec = self._get_str(header, 'DEC')
                self.focallen = self._get_float(header, 'FOCALLEN')
                self.airmass = self._get_float(header, 'AIRMASS')
                
                # Capture location (site)
                self.site = (self._get_str(header, 'SITE') or
                           self._get_str(header, 'OBSERVAT') or
                           self._get_str(header, 'LOCATION') or
                           self._get_str(header, 'TELESCOP'))
                self.longitude = (self._get_str(header, 'SITELONG') or
                                 self._get_str(header, 'LONGITUD'))
                self.latitude = (self._get_str(header, 'SITELAT') or
                                self._get_str(header, 'LATITUDE'))
                
        except Exception as e:
            logger.warning(f"Failed to read FITS file {self.filepath}: {e}")
    
    def _get_str(self, header, key: str) -> Optional[str]:
        """Safely get string value from header."""
        try:
            value = header.get(key)
            if value is not None:
                return str(value).strip()
        except:
            pass
        return None
    
    def _get_float(self, header, key: str) -> Optional[float]:
        """Safely get float value from header."""
        try:
            value = header.get(key)
            if value is not None:
                return float(value)
        except:
            pass
        return None
    
    def _get_int(self, header, key: str) -> Optional[int]:
        """Safely get int value from header."""
        try:
            value = header.get(key)
            if value is not None:
                return int(value)
        except:
            pass
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'filepath': str(self.filepath),
            'exptime': self.exptime,
            'date_obs': self.date_obs,
            'object': self.object,
            'imagetyp': self.imagetyp,
            'filter': self.filter,
            'gain': self.gain,
            'iso': self.iso,
            'temp': self.temp,
            'xbinning': self.xbinning,
            'ybinning': self.ybinning,
            'ra': self.ra,
            'dec': self.dec,
            'focallen': self.focallen,
            'airmass': self.airmass,
            'site': self.site,
            'longitude': self.longitude,
            'latitude': self.latitude
        }
