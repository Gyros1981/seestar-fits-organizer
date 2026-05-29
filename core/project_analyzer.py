"""
Project Analyzer Module
Analyzes existing projects and generates aggregate statistics.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging
from .fits_metadata import FitsMetadata
from .frame_classifier import FrameClassifier

logger = logging.getLogger(__name__)


class ProjectAnalysis:
    """Analysis results for a single project."""
    
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.total_files = 0
        self.total_size = 0
        self.lights = 0
        self.darks = 0
        self.flats = 0
        self.bias = 0
        self.integration_seconds = 0.0
        self.session_start = None
        self.session_end = None
        self.objects = set()
        self.filters = set()
        self.exposures = set()
        # Track frame counts by exposure time
        self.lights_by_exposure = {}  # {exposure_time: count}
        self.darks_by_exposure = {}  # {exposure_time: count}
        # Capture location (site)
        self.site = None
        self.longitude = None
        self.latitude = None
        # Sessions (grouped by time gaps, per object)
        self.sessions = []  # List of (object, start, end, lights, integration_seconds, exposures, lights_by_exposure) tuples
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'path': str(self.path),
            'total_files': self.total_files,
            'total_size_mb': self.total_size / (1024 * 1024),
            'lights': self.lights,
            'darks': self.darks,
            'flats': self.flats,
            'bias': self.bias,
            'integration_seconds': self.integration_seconds,
            'session_start': self.session_start,
            'session_end': self.session_end,
            'objects': sorted(list(self.objects)),
            'filters': sorted(list(self.filters)),
            'exposures': sorted(list(self.exposures)),
            'lights_by_exposure': dict(sorted(self.lights_by_exposure.items())),
            'darks_by_exposure': dict(sorted(self.darks_by_exposure.items())),
            'site': self.site,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'sessions': self.sessions
        }


class AggregateAnalysis:
    """Aggregate analysis across all projects."""
    
    def __init__(self):
        self.total_projects = 0
        self.total_files = 0
        self.total_size = 0
        self.total_lights = 0
        self.total_darks = 0
        self.total_flats = 0
        self.total_bias = 0
        self.total_integration_seconds = 0.0
        self.unique_objects = set()
        self.unique_filters = set()
        self.nights_captured = set()
        self.projects: List[ProjectAnalysis] = []
    
    def add_project(self, project: ProjectAnalysis) -> None:
        """Add a project analysis to aggregate."""
        self.projects.append(project)
        self.total_projects += 1
        self.total_files += project.total_files
        self.total_size += project.total_size
        self.total_lights += project.lights
        self.total_darks += project.darks
        self.total_flats += project.flats
        self.total_bias += project.bias
        self.total_integration_seconds += project.integration_seconds
        self.unique_objects.update(project.objects)
        self.unique_filters.update(project.filters)
        
        # Track unique nights (by date)
        if project.session_start:
            try:
                date = datetime.fromisoformat(project.session_start).date()
                self.nights_captured.add(date)
            except:
                pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_projects': self.total_projects,
            'total_files': self.total_files,
            'total_size_gb': self.total_size / (1024 * 1024 * 1024),
            'total_lights': self.total_lights,
            'total_darks': self.total_darks,
            'total_flats': self.total_flats,
            'total_bias': self.total_bias,
            'total_integration_seconds': self.total_integration_seconds,
            'total_integration_hours': self.total_integration_seconds / 3600,
            'unique_objects': sorted(list(self.unique_objects)),
            'unique_filters': sorted(list(self.unique_filters)),
            'nights_captured': len(self.nights_captured),
            'projects': [p.to_dict() for p in self.projects]
        }


class ProjectAnalyzer:
    """Analyzes existing projects in a directory."""
    
    def __init__(self, projects_dir: Path):
        self.projects_dir = projects_dir
    
    def analyze_all(self) -> AggregateAnalysis:
        """Analyze all projects in the projects directory."""
        aggregate = AggregateAnalysis()
        
        logger.info(f"Analyzing projects directory: {self.projects_dir}")
        
        # Find all project folders (ending with _Project)
        project_folders = []
        for item in self.projects_dir.iterdir():
            if item.is_dir() and item.name.endswith('_Project'):
                project_folders.append(item)
        
        logger.info(f"Found {len(project_folders)} projects to analyze")
        
        if not project_folders:
            logger.warning(f"No _Project folders found in {self.projects_dir}")
            return aggregate
        
        for folder in project_folders:
            try:
                project_analysis = self.analyze_project(folder)
                aggregate.add_project(project_analysis)
                logger.info(f"Analyzed {folder.name}: {project_analysis.total_files} files")
            except Exception as e:
                logger.error(f"Failed to analyze {folder}: {e}")
        
        return aggregate
    
    def analyze_project(self, project_path: Path) -> ProjectAnalysis:
        """Analyze a single project."""
        analysis = ProjectAnalysis(project_path.name, project_path)
        
        # Analyze lights folder (where all FITS files are stored)
        lights_folder = project_path / 'lights'
        if lights_folder.exists():
            fits_files = list(lights_folder.glob('*.fits')) + list(lights_folder.glob('*.FIT'))
            
            # Collect timestamps per object for session grouping
            object_timestamps = {}  # {object: [timestamps]}
            object_session_data = {}  # {object: [(timestamp, exptime, is_light)]}
            object_coords = {}  # {object: (ra, dec)} - RA/DEC per object
            
            for fits_path in fits_files:
                try:
                    metadata = FitsMetadata(fits_path)
                    frame_type = FrameClassifier.classify(metadata)
                    
                    analysis.total_files += 1
                    analysis.total_size += fits_path.stat().st_size
                    
                    if frame_type == 'LIGHT':
                        analysis.lights += 1
                        if metadata.exptime:
                            analysis.integration_seconds += metadata.exptime
                            analysis.exposures.add(metadata.exptime)
                            # Track lights by exposure
                            if metadata.exptime not in analysis.lights_by_exposure:
                                analysis.lights_by_exposure[metadata.exptime] = 0
                            analysis.lights_by_exposure[metadata.exptime] += 1
                    elif frame_type == 'DARK':
                        analysis.darks += 1
                        if metadata.exptime:
                            # Track darks by exposure
                            if metadata.exptime not in analysis.darks_by_exposure:
                                analysis.darks_by_exposure[metadata.exptime] = 0
                            analysis.darks_by_exposure[metadata.exptime] += 1
                    elif frame_type == 'FLAT':
                        analysis.flats += 1
                    elif frame_type == 'BIAS':
                        analysis.bias += 1
                    
                    # Capture site location from first frame
                    if analysis.site is None and metadata.site:
                        analysis.site = metadata.site
                    if analysis.longitude is None and metadata.longitude:
                        analysis.longitude = metadata.longitude
                    if analysis.latitude is None and metadata.latitude:
                        analysis.latitude = metadata.latitude
                    
                    if metadata.object:
                        analysis.objects.add(metadata.object)
                        # Capture RA/DEC for this object (use first frame with coordinates)
                        if metadata.object not in object_coords:
                            if metadata.ra and metadata.dec:
                                object_coords[metadata.object] = (metadata.ra, metadata.dec)
                        # Collect timestamps per object with session data
                        if metadata.date_obs:
                            if metadata.object not in object_timestamps:
                                object_timestamps[metadata.object] = []
                            object_timestamps[metadata.object].append(metadata.date_obs)
                            
                            if metadata.object not in object_session_data:
                                object_session_data[metadata.object] = []
                            object_session_data[metadata.object].append((metadata.date_obs, metadata.exptime, frame_type == 'LIGHT'))
                    if metadata.filter:
                        analysis.filters.add(metadata.filter)
                            
                except Exception as e:
                    logger.warning(f"Failed to analyze {fits_path}: {e}")
            
            # Group timestamps into sessions per object (gap > 2 hours = new session)
            from datetime import datetime, timedelta
            gap_threshold = timedelta(hours=2)
            
            for obj_name, timestamps in object_timestamps.items():
                timestamps.sort()
                
                current_session_start = timestamps[0]
                current_session_end = timestamps[0]
                current_session_lights = 0
                current_session_integration = 0.0
                current_session_exposures = set()
                current_session_lights_by_exposure = {}
                
                # Get all data for this object
                obj_data = object_session_data.get(obj_name, [])
                obj_data_dict = {ts: (exptime, is_light) for ts, exptime, is_light in obj_data}
                
                # Get RA/DEC for this object
                ra, dec = object_coords.get(obj_name, (None, None))
                
                for ts in timestamps[1:]:
                    dt = datetime.fromisoformat(ts)
                    prev_dt = datetime.fromisoformat(current_session_end)
                    
                    if dt - prev_dt > gap_threshold:
                        # End current session
                        analysis.sessions.append((obj_name, ra, dec, current_session_start, current_session_end, 
                                                  current_session_lights, current_session_integration, 
                                                  sorted(list(current_session_exposures)),
                                                  dict(sorted(current_session_lights_by_exposure.items()))))
                        # Start new session
                        current_session_start = ts
                        current_session_end = ts
                        current_session_lights = 0
                        current_session_integration = 0.0
                        current_session_exposures = set()
                        current_session_lights_by_exposure = {}
                    else:
                        # Extend current session
                        current_session_end = ts
                    
                    # Add session data
                    if ts in obj_data_dict:
                        exptime, is_light = obj_data_dict[ts]
                        if is_light:
                            current_session_lights += 1
                            if exptime:
                                current_session_integration += exptime
                                current_session_exposures.add(exptime)
                                # Track lights by exposure
                                if exptime not in current_session_lights_by_exposure:
                                    current_session_lights_by_exposure[exptime] = 0
                                current_session_lights_by_exposure[exptime] += 1
                
                # Add final session for this object
                analysis.sessions.append((obj_name, ra, dec, current_session_start, current_session_end,
                                          current_session_lights, current_session_integration,
                                          sorted(list(current_session_exposures)),
                                          dict(sorted(current_session_lights_by_exposure.items()))))
            
            # Set overall start/end for backward compatibility
            all_timestamps = []
            for ts_list in object_timestamps.values():
                all_timestamps.extend(ts_list)
            if all_timestamps:
                all_timestamps.sort()
                analysis.session_start = all_timestamps[0]
                analysis.session_end = all_timestamps[-1]
        
        return analysis
