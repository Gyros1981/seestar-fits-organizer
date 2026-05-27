"""
Project Builder Module
Creates project folder structure and copies FITS files.
"""

from pathlib import Path
from typing import List, Dict
from shutil import copy2
import logging
from fits_metadata import FitsMetadata
from frame_classifier import FrameClassifier, FrameType

logger = logging.getLogger(__name__)


class FitsFile:
    """Represents a FITS file with its classification."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.metadata = FitsMetadata(filepath)
        self.frame_type = FrameClassifier.classify(self.metadata)
    
    def to_dict(self) -> Dict:
        return {
            'path': str(self.filepath),
            'frameType': self.frame_type,
            'metadata': self.metadata.to_dict()
        }


class ProjectMetrics:
    """Metrics for a project."""
    
    def __init__(self):
        self.total_lights = 0
        self.total_darks = 0
        self.total_flats = 0
        self.total_bias = 0
        self.total_integration_seconds = 0.0
        self.session_start = None
        self.session_end = None
        self.total_file_count = 0
        self.total_disk_usage = 0
        self.exposure_values = set()
        self.dark_exposure_values = set()
    
    def to_dict(self) -> Dict:
        return {
            'totalLights': self.total_lights,
            'totalDarks': self.total_darks,
            'totalFlats': self.total_flats,
            'totalBias': self.total_bias,
            'totalIntegrationSeconds': self.total_integration_seconds,
            'sessionStart': self.session_start,
            'sessionEnd': self.session_end,
            'totalFileCount': self.total_file_count,
            'totalDiskUsage': self.total_disk_usage,
            'exposureValues': sorted(list(self.exposure_values)),
            'darkExposureValues': sorted(list(self.dark_exposure_values))
        }


class Project:
    """Represents an astrophotography project."""
    
    def __init__(self, name: str, source_folder: Path, output_folder: Path):
        self.name = name
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.frames: List[FitsFile] = []
        self.metrics = ProjectMetrics()
    
    def add_frame(self, frame: FitsFile) -> None:
        """Add a frame to the project."""
        self.frames.append(frame)
        
        # Update metrics
        self.metrics.total_file_count += 1
        self.metrics.total_disk_usage += frame.filepath.stat().st_size
        
        if frame.frame_type == 'LIGHT':
            self.metrics.total_lights += 1
            if frame.metadata.exptime:
                self.metrics.total_integration_seconds += frame.metadata.exptime
                self.metrics.exposure_values.add(frame.metadata.exptime)
        elif frame.frame_type == 'DARK':
            self.metrics.total_darks += 1
            if frame.metadata.exptime:
                self.metrics.dark_exposure_values.add(frame.metadata.exptime)
        elif frame.frame_type == 'FLAT':
            self.metrics.total_flats += 1
        elif frame.frame_type == 'BIAS':
            self.metrics.total_bias += 1
        
        # Update session timeline
        if frame.metadata.date_obs:
            if self.metrics.session_start is None or frame.metadata.date_obs < self.metrics.session_start:
                self.metrics.session_start = frame.metadata.date_obs
            if self.metrics.session_end is None or frame.metadata.date_obs > self.metrics.session_end:
                self.metrics.session_end = frame.metadata.date_obs
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'sourceFolder': str(self.source_folder),
            'outputFolder': str(self.output_folder),
            'frames': [f.to_dict() for f in self.frames],
            'metrics': self.metrics.to_dict()
        }


class ProjectBuilder:
    """Builds projects from raw FITS data."""
    
    def __init__(self, raw_dir: Path, projects_dir: Path):
        self.raw_dir = raw_dir
        self.projects_dir = projects_dir
        self.projects: List[Project] = []
    
    def scan_raw_folders(self) -> List[Path]:
        """Scan for *_sub or *_subs folders in raw directory."""
        folders = []
        for item in self.raw_dir.iterdir():
            if item.is_dir() and (item.name.endswith('_subs') or item.name.endswith('_sub')):
                folders.append(item)
        return folders
    
    def build_project(self, source_folder: Path, progress_callback=None) -> Project:
        """Build a project from a source folder."""
        # Extract project name from folder name
        # m3_subs or m3_sub -> M3_Project
        folder_name = source_folder.name
        object_name = folder_name.replace('_subs', '').replace('_sub', '').title()
        project_name = f"{object_name}_Project"
        
        # Create project folder
        project_folder = self.projects_dir / project_name
        project_folder.mkdir(parents=True, exist_ok=True)
        
        # Create subfolders
        subfolders = ['lights', 'darks', 'biases', 'flats']
        for subfolder in subfolders:
            (project_folder / subfolder).mkdir(exist_ok=True)
        
        # Create project object
        project = Project(project_name, source_folder, project_folder)
        
        # Process FITS files
        fits_files = list(source_folder.glob('*.fits')) + list(source_folder.glob('*.FIT'))
        total_files = len(fits_files)
        
        for i, fits_path in enumerate(fits_files):
            if progress_callback:
                progress_callback(i + 1, total_files, f"Processing {fits_path.name}")
            
            try:
                frame = FitsFile(fits_path)
                project.add_frame(frame)
                
                # Copy ALL FITS files to lights folder only
                dest_folder = project_folder / 'lights'
                dest_file = dest_folder / fits_path.name
                
                if dest_folder.exists():
                    # Skip if file already exists
                    if dest_file.exists():
                        logger.info(f"Skipping existing file: {fits_path.name}")
                    else:
                        copy2(fits_path, dest_file)
                        logger.info(f"Copied: {fits_path.name}")
                    
            except Exception as e:
                logger.warning(f"Failed to process {fits_path}: {e}")
        
        self.projects.append(project)
        return project
    
    def build_all_projects(self, progress_callback=None) -> List[Project]:
        """Build projects from all *_subs folders."""
        folders = self.scan_raw_folders()
        projects = []
        
        for i, folder in enumerate(folders):
            if progress_callback:
                progress_callback(i + 1, len(folders), f"Building project from {folder.name}")
            
            project = self.build_project(folder, progress_callback)
            projects.append(project)
        
        return projects
