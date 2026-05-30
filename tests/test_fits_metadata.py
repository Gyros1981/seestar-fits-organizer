"""Unit tests for FitsMetadata extraction."""

import pytest
from pathlib import Path
from core import FitsMetadata


class TestFitsMetadata:
    """Test cases for FitsMetadata - requires actual FITS files."""
    
    def test_metadata_handles_missing_file(self):
        """Test that FitsMetadata handles missing file gracefully."""
        # FitsMetadata handles missing files gracefully (logs warning, creates empty metadata)
        metadata = FitsMetadata(Path("nonexistent.fits"))
        assert metadata.filepath == Path("nonexistent.fits")
        assert metadata.exptime is None
