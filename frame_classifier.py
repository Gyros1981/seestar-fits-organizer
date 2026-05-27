"""
Frame Classification Module
Classifies FITS files as LIGHT, DARK, FLAT, or BIAS.
"""

from pathlib import Path
from typing import Literal
from fits_metadata import FitsMetadata
import logging

logger = logging.getLogger(__name__)

FrameType = Literal['LIGHT', 'DARK', 'FLAT', 'BIAS', 'UNKNOWN']


class FrameClassifier:
    """Classifies FITS frames based on metadata and filename."""
    
    @staticmethod
    def classify(metadata: FitsMetadata) -> FrameType:
        """
        Classify a FITS file based on metadata priority:
        1. IMAGETYP header (preferred)
        2. Filename keywords
        3. Exposure heuristics (fallback)
        """
        # Priority 1: IMAGETYP header
        if metadata.imagetyp:
            imagetyp = metadata.imagetyp.upper()
            if 'LIGHT' in imagetyp:
                return 'LIGHT'
            elif 'DARK' in imagetyp:
                return 'DARK'
            elif 'FLAT' in imagetyp:
                return 'FLAT'
            elif 'BIAS' in imagetyp or 'ZERO' in imagetyp:
                return 'BIAS'
        
        # Priority 2: Filename keywords
        filename = metadata.filepath.name.upper()
        if 'LIGHT' in filename or 'SUB' in filename:
            return 'LIGHT'
        elif 'DARK' in filename:
            return 'DARK'
        elif 'FLAT' in filename:
            return 'FLAT'
        elif 'BIAS' in filename or 'ZERO' in filename:
            return 'BIAS'
        
        # Priority 3: Exposure heuristics
        # Very short exposures (<= 0.01 sec) are typically BIAS
        # Short exposures (0.01 - 5 sec) are typically FLATS
        # Longer exposures are typically LIGHT or DARK
        if metadata.exptime is not None:
            if metadata.exptime <= 0.01:
                return 'BIAS'
            elif metadata.exptime <= 5.0:
                return 'FLAT'
            else:
                # Can't distinguish LIGHT from DARK without more context
                # Default to LIGHT as it's most common
                return 'LIGHT'
        
        logger.warning(f"Could not classify {metadata.filepath}, defaulting to UNKNOWN")
        return 'UNKNOWN'
