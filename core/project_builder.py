"""
Project Builder Module
Creates project folder structure and copies FITS files.
"""

from pathlib import Path
from typing import List, Dict, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
from .fits_metadata import FitsMetadata
from .frame_classifier import FrameClassifier, FrameType
from .utils import safe_copy

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
        # Files that failed to copy: list of (source_path, error_message)
        self.copy_errors: List[Tuple[Path, str]] = []
    
    def scan_raw_folders(self) -> List[Path]:
        """Scan for *_sub or *_subs folders in raw directory."""
        folders = []
        for item in self.raw_dir.iterdir():
            if item.is_dir() and (item.name.endswith('_subs') or item.name.endswith('_sub')):
                folders.append(item)
        return folders
    
    def count_files_to_copy(self, folders: List[Path], selected_file_types=None) -> int:
        """Count total FITS files to copy across multiple folders.
        
        Args:
            folders: List of source folders to count files in
            selected_file_types: Optional set of file extensions to count (e.g., {'.fits', '.FIT'}).
                                If None, counts all FITS files.
            
        Returns:
            Total number of FITS files found
        """
        total = 0
        for folder in folders:
            if selected_file_types:
                # Count only selected file types
                for ext in selected_file_types:
                    total += len(list(folder.glob(f'*{ext}')))
            else:
                # Count all FITS files (default behavior)
                fits_files = list(folder.glob('*.fits')) + list(folder.glob('*.FIT'))
                total += len(fits_files)
        return total
    
    def build_project(self, source_folder: Path, progress_callback=None, global_progress=None, selected_file_types=None, cancel_check=None) -> Project:
        """Build a project from a source folder.
        
        Args:
            source_folder: Path to folder containing FITS files
            progress_callback: Optional callback(current, total, message) for project-level progress
            global_progress: Optional dict with 'current' and 'total' for cross-project progress tracking
            selected_file_types: Optional set of file extensions to copy (e.g., {'.fits', '.FIT'}).
                                If None, copies all FITS files.
            cancel_check: Optional callable returning True to abort copying early.
        """
        # Extract project name from folder name
        # m3_subs or m3_sub -> M3_Project
        folder_name = source_folder.name
        object_name = folder_name.replace('_subs', '').replace('_sub', '').replace('_', ' ').title()
        # Uppercase common catalog prefixes that .title() gets wrong (e.g. Ngc -> NGC, Ic -> IC)
        for prefix in ('Ngc', 'Ic', 'Ugc', 'Pgc', 'Mcg', 'Arp'):
            if object_name.upper().startswith(prefix.upper()):
                object_name = prefix.upper() + object_name[len(prefix):]
                break
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
        
        # Process FITS files based on selected file types
        if selected_file_types:
            # Get only selected file types
            fits_files = []
            for ext in selected_file_types:
                fits_files.extend(list(source_folder.glob(f'*{ext}')))
        else:
            # Get all FITS files (default behavior)
            fits_files = list(source_folder.glob('*.fits')) + list(source_folder.glob('*.FIT'))
        total_files = len(fits_files)
        
        # Batch metadata extraction in parallel
        def extract_metadata_and_classify(fits_path):
            """Extract metadata and classify a single FITS file."""
            try:
                frame = FitsFile(fits_path)
                return (fits_path, frame, None)
            except Exception as e:
                return (fits_path, None, str(e))
        
        # Extract metadata in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            metadata_futures = []
            for fits_path in fits_files:
                metadata_futures.append(executor.submit(extract_metadata_and_classify, fits_path))
            
            # Collect results
            processed_files = []
            for future in metadata_futures:
                fits_path, frame, error = future.result()
                if error:
                    logger.warning(f"Failed to process {fits_path}: {error}")
                    continue
                processed_files.append((fits_path, frame))
        
        # Now copy files based on classification (this is sequential but metadata is already extracted)
        for i, (fits_path, frame) in enumerate(processed_files):
            # Stop early if the user requested cancellation
            if cancel_check and cancel_check():
                logger.info(f"Build cancelled by user during {source_folder.name}")
                break
            # Update project-level progress
            if progress_callback:
                progress_callback(i + 1, total_files, f"Processing {fits_path.name}")
            
            # Update global progress if provided
            if global_progress is not None:
                global_progress['current'] += 1
                current = global_progress['current']
                total = global_progress['total']
                pct = current / total if total > 0 else 0
                global_progress['callback'](current, total, pct, f"Copying {fits_path.name}")
            
            project.add_frame(frame)
            
            # Copy FITS file to appropriate subfolder based on frame type
            if frame.frame_type == 'LIGHT':
                dest_folder = project_folder / 'lights'
            elif frame.frame_type == 'DARK':
                dest_folder = project_folder / 'darks'
            elif frame.frame_type == 'FLAT':
                dest_folder = project_folder / 'flats'
            elif frame.frame_type == 'BIAS':
                dest_folder = project_folder / 'biases'
            else:
                # UNKNOWN or other types go to lights
                dest_folder = project_folder / 'lights'
            
            dest_file = dest_folder / fits_path.name
            
            # Copy the file, but never let a single bad file abort the batch.
            try:
                if dest_file.exists():
                    logger.info(f"Skipping existing file: {fits_path.name}")
                else:
                    safe_copy(fits_path, dest_file)
                    logger.info(f"Copied: {fits_path.name} to {dest_folder.name}")
            except Exception as copy_err:
                self.copy_errors.append((fits_path, str(copy_err)))
                logger.error(f"Failed to copy {fits_path}: {copy_err}")
        
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
