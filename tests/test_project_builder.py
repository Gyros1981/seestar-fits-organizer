"""Unit tests for ProjectBuilder."""

import pytest
from pathlib import Path
from core import ProjectBuilder, Project


class TestProjectBuilder:
    """Test cases for ProjectBuilder."""
    
    @pytest.fixture
    def builder(self, temp_dir):
        """Create a ProjectBuilder with temp directories."""
        raw_dir = temp_dir / "raw"
        projects_dir = temp_dir / "projects"
        raw_dir.mkdir()
        projects_dir.mkdir()
        return ProjectBuilder(raw_dir, projects_dir)
    
    def test_builder_initialization(self, builder):
        """Test ProjectBuilder initializes correctly."""
        assert builder.raw_dir.exists()
        assert builder.projects_dir.exists()
        assert builder.projects == []
    
    def test_scan_raw_folders_empty(self, builder):
        """Test scanning empty raw directory."""
        folders = builder.scan_raw_folders()
        assert folders == []
    
    def test_scan_raw_folders_with_subs(self, builder):
        """Test scanning raw directory with *_subs folders."""
        # Create test folders
        (builder.raw_dir / "m42_subs").mkdir()
        (builder.raw_dir / "m3_sub").mkdir()
        (builder.raw_dir / "regular_folder").mkdir()  # Should not match
        
        folders = builder.scan_raw_folders()
        
        assert len(folders) == 2
        assert any("m42_subs" in str(f) for f in folders)
        assert any("m3_sub" in str(f) for f in folders)

    def test_build_records_copy_error_without_aborting(self, builder, monkeypatch):
        """A single failing copy must be recorded, not abort the whole build."""
        import numpy as np
        from astropy.io import fits
        import core.project_builder as pb

        source = builder.raw_dir / "m13_subs"
        source.mkdir()
        for i in range(3):
            hdu = fits.PrimaryHDU(np.zeros((4, 4), dtype=np.uint16))
            hdu.header['EXPTIME'] = 10.0
            hdu.header['OBJECT'] = 'M13'
            hdu.header['IMAGETYP'] = 'LIGHT'
            hdu.writeto(source / f"Light_M13_{i}.fits", overwrite=True)

        # Make the 2nd copy fail, others succeed.
        real_safe_copy = pb.safe_copy
        calls = {'n': 0}

        def flaky_copy(src, dst):
            calls['n'] += 1
            if calls['n'] == 2:
                raise OSError("simulated disk error")
            return real_safe_copy(src, dst)

        monkeypatch.setattr(pb, 'safe_copy', flaky_copy)

        project = builder.build_project(source)

        # Build still completed and produced a project.
        assert project is not None
        # Exactly one failure recorded; the other two copied.
        assert len(builder.copy_errors) == 1
        assert "simulated disk error" in builder.copy_errors[0][1]
