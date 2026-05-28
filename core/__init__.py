"""
Core Business Logic Package for Seestar FITS Organizer.

This package contains all business logic modules for processing
astrophotography data from Seestar telescopes.
"""

from .app_settings import AppSettings
from .location_tags import LocationTags
from .fits_metadata import FitsMetadata
from .frame_classifier import FrameClassifier, FrameType
from .project_builder import ProjectBuilder, Project, ProjectMetrics, FitsFile
from .project_analyzer import ProjectAnalyzer, ProjectAnalysis, AggregateAnalysis

__all__ = [
    'AppSettings',
    'LocationTags',
    'FitsMetadata',
    'FrameClassifier',
    'FrameType',
    'ProjectBuilder',
    'Project',
    'ProjectMetrics',
    'FitsFile',
    'ProjectAnalyzer',
    'ProjectAnalysis',
    'AggregateAnalysis'
]
