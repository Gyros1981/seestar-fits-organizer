"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_fits_header():
    """Return a sample FITS header dictionary."""
    return {
        'SIMPLE': True,
        'BITPIX': 16,
        'NAXIS': 2,
        'NAXIS1': 1024,
        'NAXIS2': 1024,
        'EXPTIME': 10.0,
        'DATE-OBS': '2024-01-15T20:30:00',
        'OBJECT': 'M42',
        'IMAGETYP': 'LIGHT',
        'FILTER': 'Ha',
        'GAIN': 100,
        'CCD-TEMP': -10.0,
        'XBINNING': 1,
        'YBINNING': 1,
        'RA': 83.8221,
        'DEC': -5.3911,
        'FOCALLEN': 250.0,
    }
