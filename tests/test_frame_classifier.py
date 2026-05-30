"""Unit tests for FrameClassifier."""

import pytest
from pathlib import Path
from core import FrameClassifier, FitsMetadata


class MockFitsMetadata:
    """Mock FitsMetadata for testing without file I/O."""
    
    def __init__(self, filepath: Path, exptime=None, imagetyp=None, 
                 object_name=None, filter_name=None, gain=None, 
                 ccd_temp=None, ra=None, dec=None, focal_length=None,
                 binning=None):
        self.filepath = filepath
        self.exptime = exptime
        self.imagetyp = imagetyp
        self.object = object_name
        self.filter = filter_name
        self.gain = gain
        self.temp = ccd_temp
        self.ra = ra
        self.dec = dec
        self.focallen = focal_length
        self.xbinning = binning[0] if binning else None
        self.ybinning = binning[1] if binning else None


class TestFrameClassifier:
    """Test cases for FrameClassifier."""
    
    def test_classify_from_imagetyp_light(self):
        """Test classification from IMAGETYP header."""
        metadata = MockFitsMetadata(
            filepath=Path("test.fits"),
            exptime=10.0,
            imagetyp="LIGHT",
            object_name="M42"
        )
        result = FrameClassifier.classify(metadata)
        assert result == "LIGHT"
    
    def test_classify_from_imagetyp_dark(self):
        """Test classification of DARK frame."""
        metadata = MockFitsMetadata(
            filepath=Path("dark_10s.fits"),
            exptime=10.0,
            imagetyp="DARK"
        )
        result = FrameClassifier.classify(metadata)
        assert result == "DARK"
    
    def test_classify_from_imagetyp_flat(self):
        """Test classification of FLAT frame."""
        metadata = MockFitsMetadata(
            filepath=Path("flat.fits"),
            exptime=1.0,
            imagetyp="FLAT"
        )
        result = FrameClassifier.classify(metadata)
        assert result == "FLAT"
    
    def test_classify_from_imagetyp_bias(self):
        """Test classification of BIAS frame."""
        metadata = MockFitsMetadata(
            filepath=Path("bias.fits"),
            exptime=0.001,
            imagetyp="BIAS"
        )
        result = FrameClassifier.classify(metadata)
        assert result == "BIAS"
    
    def test_classify_from_filename_light(self):
        """Test classification from filename when IMAGETYP missing."""
        metadata = MockFitsMetadata(
            filepath=Path("light_m42_sub_001.fits"),
            exptime=10.0,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "LIGHT"
    
    def test_classify_from_filename_dark(self):
        """Test classification from DARK in filename."""
        metadata = MockFitsMetadata(
            filepath=Path("dark_30s_001.fits"),
            exptime=30.0,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "DARK"
    
    def test_classify_from_exposure_bias(self):
        """Test BIAS detection from very short exposure."""
        metadata = MockFitsMetadata(
            filepath=Path("unknown.fits"),
            exptime=0.001,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "BIAS"
    
    def test_classify_from_exposure_flat(self):
        """Test FLAT detection from short exposure."""
        metadata = MockFitsMetadata(
            filepath=Path("unknown.fits"),
            exptime=2.0,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "FLAT"
    
    def test_classify_from_exposure_light(self):
        """Test LIGHT detection from long exposure."""
        metadata = MockFitsMetadata(
            filepath=Path("unknown.fits"),
            exptime=300.0,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "LIGHT"
    
    def test_classify_unknown(self):
        """Test classification when nothing matches."""
        metadata = MockFitsMetadata(
            filepath=Path("unknown.xyz"),
            exptime=None,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "UNKNOWN"
    
    def test_imagetyp_priority_over_filename(self):
        """Test that IMAGETYP takes priority over filename."""
        # File has "dark" in name but is marked as LIGHT
        metadata = MockFitsMetadata(
            filepath=Path("dark_frame.fits"),
            exptime=10.0,
            imagetyp="LIGHT"
        )
        result = FrameClassifier.classify(metadata)
        assert result == "LIGHT"
    
    def test_filename_priority_over_exposure(self):
        """Test that filename takes priority over exposure heuristics."""
        # Short exposure but filename says DARK
        metadata = MockFitsMetadata(
            filepath=Path("dark_001.fits"),
            exptime=0.005,
            imagetyp=None
        )
        result = FrameClassifier.classify(metadata)
        assert result == "DARK"
