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
