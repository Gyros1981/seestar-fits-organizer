"""
Analysis Window Module

Displays project analysis results with detailed statistics,
session breakdowns, location information, and export capabilities.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import csv
import subprocess
import platform
import webbrowser
import logging
import json
import os
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from .preview_window import PreviewWindow

# SIMBAD TAP service endpoint
SIMBAD_TAP_URL = "http://simbad.u-strasbg.fr/simbad/sim-tap/sync"

# Cache file for common names lookup
COMMON_NAMES_CACHE_FILE = Path.home() / '.seestar_fits_organizer' / 'common_names_cache.json'


def load_common_names_cache():
    """Load cached common names from file."""
    if COMMON_NAMES_CACHE_FILE.exists():
        try:
            with open(COMMON_NAMES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_common_names_cache(cache):
    """Save common names cache to file."""
    try:
        COMMON_NAMES_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMON_NAMES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not save common names cache: {e}")


def query_simbad_batch(object_names):
    """
    Query SIMBAD script service for common names of multiple objects.
    
    Uses the SIMBAD script service to get all identifiers, then extracts
    common names (those starting with 'NAME ').
    
    Args:
        object_names: List of object names to query (e.g., ['M51', 'NGC6960'])
        
    Returns:
        Dict mapping normalized object names to common names
    """
    if not object_names:
        return {}
    
    results = {}
    
    # Format object names for SIMBAD (add spaces after M/NGC/IC if needed)
    formatted_names = []
    for name in object_names:
        name_upper = name.upper()
        # Format: M51 -> 'M 51', NGC6960 -> 'NGC 6960'
        if name_upper.startswith('M') and len(name_upper) > 1 and name_upper[1:].isdigit():
            formatted_names.append(f"M {name_upper[1:]}")
        elif name_upper.startswith('NGC') and len(name_upper) > 3 and name_upper[3:].isdigit():
            formatted_names.append(f"NGC {name_upper[3:]}")
        elif name_upper.startswith('IC') and len(name_upper) > 2 and name_upper[2:].isdigit():
            formatted_names.append(f"IC {name_upper[2:]}")
        else:
            formatted_names.append(name_upper)
    
    # Query each object using SIMBAD script service
    # Note: We could do a batch query but individual queries are more reliable
    for obj_name in formatted_names:
        try:
            # SIMBAD script to get all identifiers
            script = f'format object "%IDLIST"\nquery id {obj_name}'
            encoded_script = quote(script, safe='')
            url = f"http://simbad.u-strasbg.fr/simbad/sim-script?script={encoded_script}"
            
            req = Request(url, headers={'User-Agent': 'SeestarFITSOrganizer/1.0'})
            
            with urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
            
            # Extract the data section
            if '::data::' in content:
                data_section = content.split('::data::')[1].strip()
                
                # Look for common names (identifiers starting with 'NAME ')
                common_names = []
                for line in data_section.split('\n'):
                    line = line.strip()
                    if line.startswith('NAME '):
                        # Extract the name after 'NAME '
                        common_name = line[5:].strip()
                        if common_name:
                            common_names.append(common_name)
                
                # Use the first common name found (usually the main one)
                if common_names:
                    # Normalize the object name for the key
                    normalized = obj_name.upper().replace(' ', '').replace('-', '')
                    results[normalized] = common_names[0]
                    logger.debug(f"Found common name for {obj_name}: {common_names[0]}")
            
        except Exception as e:
            logger.debug(f"Failed to query SIMBAD for {obj_name}: {e}")
            continue
    
    if results:
        logger.info(f"Retrieved {len(results)} common names from SIMBAD")
    
    return results

logger = logging.getLogger(__name__)


# Common names lookup for astronomical objects
# Maps catalog identifiers to common names
OBJECT_COMMON_NAMES = {
    # Messier objects
    'M1': 'Crab Nebula',
    'M2': None,
    'M3': None,
    'M4': None,
    'M5': None,
    'M6': 'Butterfly Cluster',
    'M7': 'Ptolemy Cluster',
    'M8': 'Lagoon Nebula',
    'M9': None,
    'M10': None,
    'M11': 'Wild Duck Cluster',
    'M12': None,
    'M13': 'Hercules Globular Cluster',
    'M14': None,
    'M15': None,
    'M16': 'Eagle Nebula',
    'M17': 'Omega Nebula',
    'M18': None,
    'M19': None,
    'M20': 'Trifid Nebula',
    'M21': None,
    'M22': None,
    'M23': None,
    'M24': 'Sagittarius Star Cloud',
    'M25': None,
    'M26': None,
    'M27': 'Dumbbell Nebula',
    'M28': None,
    'M29': None,
    'M30': None,
    'M31': 'Andromeda Galaxy',
    'M32': None,
    'M33': 'Triangulum Galaxy',
    'M34': None,
    'M35': None,
    'M36': 'Pinwheel Cluster',
    'M37': None,
    'M38': 'Starfish Cluster',
    'M39': None,
    'M40': None,
    'M41': None,
    'M42': 'Orion Nebula',
    'M43': None,
    'M44': 'Beehive Cluster',
    'M45': 'Pleiades',
    'M46': None,
    'M47': None,
    'M48': None,
    'M49': None,
    'M50': 'Heart-Shaped Cluster',
    'M51': 'Whirlpool Galaxy',
    'M52': None,
    'M53': None,
    'M54': None,
    'M55': None,
    'M56': None,
    'M57': 'Ring Nebula',
    'M58': None,
    'M59': None,
    'M60': None,
    'M61': None,
    'M62': None,
    'M63': 'Sunflower Galaxy',
    'M64': 'Black Eye Galaxy',
    'M65': 'Leo Triplet',
    'M66': 'Leo Triplet',
    'M67': None,
    'M68': None,
    'M69': None,
    'M70': None,
    'M71': None,
    'M72': None,
    'M73': None,
    'M74': 'Phantom Galaxy',
    'M75': None,
    'M76': 'Little Dumbbell Nebula',
    'M77': None,
    'M78': None,
    'M79': None,
    'M80': None,
    'M81': 'Bode\'s Galaxy',
    'M82': 'Cigar Galaxy',
    'M83': 'Southern Pinwheel Galaxy',
    'M84': None,
    'M85': None,
    'M86': None,
    'M87': 'Virgo A',
    'M88': None,
    'M89': None,
    'M90': None,
    'M91': None,
    'M92': None,
    'M93': None,
    'M94': 'Cat\'s Eye Galaxy',
    'M95': None,
    'M96': None,
    'M97': 'Owl Nebula',
    'M98': None,
    'M99': None,
    'M100': None,
    'M101': 'Pinwheel Galaxy',
    'M102': None,
    'M103': None,
    'M104': 'Sombrero Galaxy',
    'M105': None,
    'M106': None,
    'M107': None,
    'M108': None,
    'M109': None,
    'M110': None,
    # NGC objects (selected popular ones)
    'NGC6960': 'Western Veil Nebula',
    'NGC6992': 'Eastern Veil Nebula',
    'NGC6995': 'Eastern Veil Nebula',
    'NGC6974': None,
    'NGC6979': None,
    'NGC2024': 'Flame Nebula',
    'NGC2264': 'Christmas Tree Cluster',
    'NGC2237': 'Rosette Nebula',
    'NGC2238': 'Rosette Nebula',
    'NGC2239': 'Rosette Nebula',
    'NGC2244': 'Rosette Nebula',
    'NGC2246': 'Rosette Nebula',
    'NGC7000': 'North America Nebula',
    'NGC1976': 'Orion Nebula',
    'NGC6514': 'Trifid Nebula',
    'NGC6523': 'Trifid Nebula',
    'NGC6611': 'Eagle Nebula',
    'NGC6720': 'Ring Nebula',
    'NGC1952': 'Crab Nebula',
    'NGC7293': 'Helix Nebula',
    'NGC3372': 'Eta Carinae Nebula',
    'NGC2261': 'Hubble\'s Variable Nebula',
    'NGC2392': 'Eskimo Nebula',
    'NGC3587': 'Owl Nebula',
    'NGC6853': 'Dumbbell Nebula',
    'NGC6503': 'Little Dumbbell Nebula',
    'NGC1982': 'M43',
    'NGC2070': 'Tarantula Nebula',
    'NGC7635': 'Bubble Nebula',
    'NGC1499': 'California Nebula',
    'NGC1435': 'Merope Nebula',
    'NGC6857': None,
    'NGC7662': 'Blue Snowball',
    'NGC6210': None,
    'NGC891': None,
    'NGC457': 'Owl Cluster',
    'NGC663': None,
    'NGC869': 'Double Cluster',
    'NGC884': 'Double Cluster',
    'NGC6383': None,
    'NGC6397': None,
    'NGC6541': None,
    'NGC6752': None,
    'NGC362': None,
    'NGC104': '47 Tucanae',
    'NGC2071': None,
    'NGC5139': 'Omega Centauri',
    'NGC5904': None,
    'NGC6205': 'Hercules Globular Cluster',
    'NGC6341': None,
    'NGC7078': None,
    'NGC7099': None,
    'NGC205': None,
    'NGC221': None,
    'NGC224': 'Andromeda Galaxy',
    'NGC598': 'Triangulum Galaxy',
    'NGC3031': 'Bode\'s Galaxy',
    'NGC3034': 'Cigar Galaxy',
    'NGC4594': 'Sombrero Galaxy',
    'NGC5457': 'Pinwheel Galaxy',
    'NGC5194': 'Whirlpool Galaxy',
    'NGC5195': None,
    'NGC6543': 'Cat\'s Eye Nebula',
    'IC434': 'Horsehead Nebula',
    'IC4603': 'Rho Ophiuchi',
    'IC4604': 'Rho Ophiuchi',
    'IC4605': 'Rho Ophiuchi',
    'IC1318': 'Gamma Cygni Nebula',
    'IC1805': 'Heart Nebula',
    'IC1848': 'Soul Nebula',
    'IC405': 'Flaming Star Nebula',
    'IC2177': 'Seagull Nebula',
    'IC1396': 'Elephant Trunk Nebula',
    'IC5070': 'Pelican Nebula',
    'IC5067': 'Pelican Nebula',
    'IC5146': 'Cocoon Nebula',
    # Popular star/asterism names
    'ALNILAM': None,
    'ALNITAK': None,
    'MINTAKA': None,
    'BETELGEUSE': None,
    'RIGEL': None,
    'ALDEBARAN': None,
    'CAPPELLA': None,
    'SIRIUS': None,
    'VEGA': None,
    'ALTAIR': None,
    'DENEB': None,
    'POLARIS': 'North Star',
    'ANTARES': None,
    'SPICA': None,
    'REGULUS': None,
    'ARCTURUS': None,
    'ALPHARD': None,
}


# Global cache for common names (populated at export time)
_common_names_cache = {}
_common_names_cache_loaded = False


def _ensure_cache_loaded():
    """Ensure the common names cache is loaded."""
    global _common_names_cache, _common_names_cache_loaded
    if not _common_names_cache_loaded:
        _common_names_cache = load_common_names_cache()
        # Merge with built-in dictionary
        for key, value in OBJECT_COMMON_NAMES.items():
            if value and key not in _common_names_cache:
                _common_names_cache[key] = value
        _common_names_cache_loaded = True


def get_common_name(object_name: str) -> str:
    """Get the common name for an astronomical object.
    
    Uses local cache first, which is populated from SIMBAD API
    during CSV export for all unknown objects in one batch.
    
    Args:
        object_name: The catalog name (e.g., 'NGC6960', 'M51', 'M42')
        
    Returns:
        The common name if known, otherwise empty string
    """
    if not object_name:
        return ''
    
    # Normalize the object name (remove spaces, uppercase)
    normalized = object_name.upper().replace(' ', '').replace('-', '')
    
    # Ensure cache is loaded
    _ensure_cache_loaded()
    
    # Check cache first
    if normalized in _common_names_cache:
        name = _common_names_cache[normalized]
        return name if name else ''
    
    # Try with IC prefix variations
    if normalized.startswith('IC'):
        base = normalized[2:]
        try:
            num = int(base)
            ic_key = f"IC{num}"
            if ic_key in _common_names_cache:
                name = _common_names_cache[ic_key]
                return name if name else ''
        except ValueError:
            pass
    
    # Try with NGC prefix variations
    if normalized.startswith('NGC'):
        base = normalized[3:]
        try:
            num = int(base)
            ngc_key = f"NGC{num}"
            if ngc_key in _common_names_cache:
                name = _common_names_cache[ngc_key]
                return name if name else ''
        except ValueError:
            pass
    
    return ''


def lookup_common_names_batch(projects):
    """
    Collect all unique objects from projects and query SIMBAD in one batch.
    
    This minimizes API calls by doing a single batch query for all unknown objects.
    Results are cached for future use.
    
    Args:
        projects: List of project dictionaries
    """
    global _common_names_cache
    
    _ensure_cache_loaded()
    
    # Collect all unique objects that aren't in our cache yet
    unknown_objects = set()
    for project in projects:
        objects = project.get('objects', [])
        for obj in objects:
            if obj:
                normalized = obj.upper().replace(' ', '').replace('-', '')
                if normalized not in _common_names_cache:
                    unknown_objects.add(obj)
    
    if not unknown_objects:
        logger.info("All object common names found in cache, no API call needed")
        return
    
    logger.info(f"Querying SIMBAD for {len(unknown_objects)} unknown objects...")
    
    # Query SIMBAD in batch
    results = query_simbad_batch(list(unknown_objects))
    
    # Update cache with results
    if results:
        _common_names_cache.update(results)
        save_common_names_cache(_common_names_cache)
        logger.info(f"Cached {len(results)} common names from SIMBAD")
    else:
        logger.warning("SIMBAD query returned no results")


def _deg_to_hms(ra_deg: float) -> str:
    """Convert RA from decimal degrees to hours:minutes:seconds format."""
    if ra_deg is None:
        return 'N/A'
    try:
        ra_hours = ra_deg / 15.0  # Convert degrees to hours (360 deg = 24 hours)
        hours = int(ra_hours)
        minutes_float = (ra_hours - hours) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"
    except (ValueError, TypeError):
        return str(ra_deg)


def _deg_to_dms(dec_deg: float) -> str:
    """Convert DEC from decimal degrees to degrees:minutes:seconds format."""
    if dec_deg is None:
        return 'N/A'
    try:
        sign = '-' if dec_deg < 0 else '+'
        dec_abs = abs(dec_deg)
        degrees = int(dec_abs)
        minutes_float = (dec_abs - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return f"{sign}{degrees:02d}:{minutes:02d}:{seconds:05.2f}"
    except (ValueError, TypeError):
        return str(dec_deg)


def get_constellation(ra, dec) -> str:
    """Get constellation name from RA/DEC coordinates using astropy.
    
    Args:
        ra: Right Ascension in decimal degrees
        dec: Declination in decimal degrees
        
    Returns:
        Constellation name or 'Unknown' if cannot determine
    """
    try:
        ra_float = float(ra) if ra is not None else None
        dec_float = float(dec) if dec is not None else None
        
        if ra_float is None or dec_float is None:
            return 'Unknown'
        
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        
        coord = SkyCoord(ra=ra_float*u.degree, dec=dec_float*u.degree, frame='icrs')
        return coord.get_constellation()
    except Exception as e:
        logger.debug(f"Could not determine constellation: {e}")
        return 'Unknown'


def format_ra_dec(ra, dec, format_type: str = 'degrees') -> tuple:
    """Format RA and DEC values according to the specified format.
    
    Args:
        ra: Right Ascension in decimal degrees or None
        dec: Declination in decimal degrees or None
        format_type: 'degrees' or 'hms'
        
    Returns:
        Tuple of (ra_string, dec_string)
    """
    if format_type == 'hms':
        # Convert to float first if they're strings
        try:
            ra_float = float(ra) if ra is not None else None
        except (ValueError, TypeError):
            ra_float = None
        try:
            dec_float = float(dec) if dec is not None else None
        except (ValueError, TypeError):
            dec_float = None
        return _deg_to_hms(ra_float), _deg_to_dms(dec_float)
    else:
        # Decimal degrees format
        try:
            ra_val = f"{float(ra):.5f}" if ra is not None else 'N/A'
        except (ValueError, TypeError):
            ra_val = str(ra) if ra else 'N/A'
        try:
            dec_val = f"{float(dec):.5f}" if dec is not None else 'N/A'
        except (ValueError, TypeError):
            dec_val = str(dec) if dec else 'N/A'
        return ra_val, dec_val


class AnalysisWindow(ctk.CTkToplevel):
    """
    Window for displaying project analysis results.
    
    Shows aggregate statistics, project list with search/filter,
    detailed project information with sessions, location mapping,
    and CSV export functionality.
    """
    
    def __init__(self, parent, results, settings, location_tags):
        """
        Initialize the analysis window.
        
        Args:
            parent: Parent window (SeestarApp)
            results: Analysis results dictionary from ProjectAnalyzer
            settings: AppSettings instance for timezone configuration
            location_tags: LocationTags instance for location name management
        """
        super().__init__(parent)
        
        self.title("Seestar FITS Organizer - Analysis")
        self.geometry("1400x900")
        
        self.results = results
        self.settings = settings
        self.location_tags = location_tags
        self.current_project = None  # Track currently selected project for view refresh
        
        self.setup_ui()
        
        # Bring window to front
        self.lift()
        self.attributes('-topmost', True)
    
        self.after(100, lambda: self.attributes('-topmost', False))
    
    def get_font(self, size: int, weight: str = None):
        """Get a CTkFont with text scaling applied."""
        scale = self.settings.get_text_scale()
        scaled_size = int(size * scale)
        if weight:
            return ctk.CTkFont(size=scaled_size, weight=weight)
        return ctk.CTkFont(size=scaled_size)
    
    def export_to_csv(self):
        """Export analysis data to CSV file."""
        # Prompt for save location
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"seestar_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        # Query SIMBAD for all unknown objects in one batch before export
        # This minimizes API calls by doing a single query for all objects
        lookup_common_names_batch(self.results['projects'])
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write project summary section
                writer.writerow(['PROJECT SUMMARY'])

                # Collect all unique exposure times across all projects for column headers
                all_project_exposure_times = set()
                for project in self.results['projects']:
                    lights_by_exposure = project.get('lights_by_exposure', {})
                    all_project_exposure_times.update(lights_by_exposure.keys())
                sorted_project_exposures = sorted(all_project_exposure_times)

                # Build project summary headers with exposure breakdown columns
                project_base_headers = ['Project Name', 'Common Name (if known)', 'Total Lights (count)', 'Total Darks (count)', 'Total Flats (count)', 'Total Bias (count)',
                               'Total Integration Time (hrs)', 'Total Integration Time (sec)', 'Session Count']
                project_exposure_headers = [f'{int(exp)}s Exposures (count)' for exp in sorted_project_exposures]
                writer.writerow(project_base_headers + project_exposure_headers)

                for project in self.results['projects']:
                    project_name = project.get('name', 'Unknown')
                    # Get common name from first object in project
                    objects = project.get('objects', [])
                    common_name = ''
                    if objects:
                        common_name = get_common_name(objects[0])
                    total_lights = project.get('lights', 0)
                    total_darks = project.get('darks', 0)
                    total_flats = project.get('flats', 0)
                    total_bias = project.get('bias', 0)
                    total_integration_sec = project.get('integration_seconds', 0)
                    integration_hrs = total_integration_sec / 3600 if total_integration_sec else 0
                    session_count = len(project.get('sessions', []))

                    # Build base row
                    project_base_row = [
                        project_name, common_name, total_lights, total_darks, total_flats, total_bias,
                        f"{integration_hrs:.2f}", total_integration_sec, session_count
                    ]

                    # Add exposure counts for each exposure time column at project level
                    lights_by_exposure = project.get('lights_by_exposure', {})
                    project_exposure_counts = []
                    for exp in sorted_project_exposures:
                        count = lights_by_exposure.get(exp, 0)
                        project_exposure_counts.append(count)

                    writer.writerow(project_base_row + project_exposure_counts)
                
                writer.writerow([])  # Empty row separator
                
                # Write session details section
                writer.writerow(['SESSION DETAILS'])
                # Get coordinate format for header
                coord_format = self.settings.get_coordinate_format()
                ra_header = 'RA (HMS)' if coord_format == 'hms' else 'RA (deg)'
                dec_header = 'DEC (DMS)' if coord_format == 'hms' else 'DEC (deg)'

                # Collect all unique exposure times across all sessions for column headers
                all_exposure_times = set()
                for project in self.results['projects']:
                    for session in project.get('sessions', []):
                        lights_by_exposure = session[8] if len(session) > 8 else {}
                        all_exposure_times.update(lights_by_exposure.keys())
                sorted_exposure_times = sorted(all_exposure_times)

                # Build dynamic headers with parenthetical explanations
                base_headers = ['Project Name', 'Session Start (Local Time)', 'Session End (Local Time)', 'Session Duration (hrs)',
                               'Object Name', 'Common Name (if known)', ra_header, dec_header, 'Constellation',
                               'Shooting Location (Name)', 'Shooting Location (LAT in deg)', 'Shooting Location (LON in deg)',
                               'Total Lights (count)', 'Total Darks (count)', 'Total Flats (count)', 'Total Bias (count)',
                               'Total Integration Time (hrs)']

                # Add exposure breakdown columns
                exposure_headers = [f'{int(exp)}s Exposures (count)' for exp in sorted_exposure_times]
                writer.writerow(base_headers + exposure_headers)
                
                for project in self.results['projects']:
                    project_name = project.get('name', 'Unknown')
                    sessions = project.get('sessions', [])
                    
                    for session in sessions:
                        # Sessions are tuples: (obj_name, ra, dec, start, end, lights, integration_seconds, exposures, lights_by_exposure)
                        obj_name = session[0] if len(session) > 0 else 'N/A'
                        ra = session[1] if len(session) > 1 else None
                        dec = session[2] if len(session) > 2 else None
                        session_start = session[3] if len(session) > 3 else 'N/A'
                        session_end = session[4] if len(session) > 4 else 'N/A'
                        lights = session[5] if len(session) > 5 else 0
                        integration_sec = session[6] if len(session) > 6 else 0
                        exposures = session[7] if len(session) > 7 else []
                        lights_by_exposure = session[8] if len(session) > 8 else {}

                        # Get common name for this object
                        obj_common_name = get_common_name(obj_name)

                        # Calculate duration
                        duration_hrs = 0
                        if session_start != 'N/A' and session_end != 'N/A':
                            try:
                                start_dt = datetime.fromisoformat(session_start)
                                end_dt = datetime.fromisoformat(session_end)
                                duration_hrs = (end_dt - start_dt).total_seconds() / 3600
                            except:
                                pass

                        # Get location from project level
                        lat = project.get('latitude', 'N/A')
                        lon = project.get('longitude', 'N/A')

                        # Look up location tag
                        location_name = 'N/A'
                        if lat != 'N/A' and lon != 'N/A':
                            tag = self.location_tags.get_tag(lat, lon)
                            if tag and tag.get('name'):
                                location_name = tag['name']

                        integration_hrs = integration_sec / 3600 if integration_sec else 0

                        # Format dates
                        if session_start != 'N/A':
                            session_start = self._format_datetime(session_start)
                        if session_end != 'N/A':
                            session_end = self._format_datetime(session_end)

                        # Get coordinate format setting and format RA/DEC values
                        coord_format = self.settings.get_coordinate_format()
                        ra_val, dec_val = format_ra_dec(ra, dec, coord_format)

                        # Get constellation
                        constellation = get_constellation(ra, dec)

                        # Build base row data
                        base_row = [
                            project_name, session_start, session_end, f"{duration_hrs:.2f}",
                            obj_name, obj_common_name, ra_val, dec_val, constellation,
                            location_name, lat, lon,
                            lights, 0, 0, 0,  # darks, flats, bias are 0 for session-level
                            f"{integration_hrs:.2f}"
                        ]

                        # Add exposure counts for each exposure time column
                        exposure_counts = []
                        for exp in sorted_exposure_times:
                            count = lights_by_exposure.get(exp, 0)
                            exposure_counts.append(count)

                        writer.writerow(base_row + exposure_counts)
                
                writer.writerow([])  # Empty row separator
                
                # Write aggregate statistics
                writer.writerow(['AGGREGATE STATISTICS'])
                writer.writerow(['Total Projects (count)', self.results['total_projects']])
                writer.writerow(['Total Lights (count)', self.results['total_lights']])
                writer.writerow(['Total Darks (count)', self.results['total_darks']])
                writer.writerow(['Total Flats (count)', self.results['total_flats']])
                writer.writerow(['Total Bias (count)', self.results['total_bias']])
                writer.writerow(['Total Integration Time (hrs)', f"{self.results['total_integration_hours']:.2f}"])
                
                # Calculate total sessions from project data
                total_sessions = sum(len(project.get('sessions', [])) for project in self.results['projects'])
                writer.writerow(['Total Sessions (count)', total_sessions])
                
                # Write stored locations section
                writer.writerow([])  # Empty row separator
                writer.writerow(['STORED LOCATIONS'])
                writer.writerow(['Location Name', 'Latitude (deg)', 'Longitude (deg)', 'Notes'])
                
                # Collect all unique locations from location_tags
                all_tags = []
                try:
                    # Use get_all_tags() method to get all tags
                    tags_data = self.location_tags.get_all_tags()
                    for key, tag_info in tags_data.items():
                        # Key is in format "lat,lon"
                        try:
                            lat, lon = key.split(',')
                            all_tags.append({
                                'name': tag_info.get('name', 'Unnamed'),
                                'lat': lat,
                                'lon': lon,
                                'notes': tag_info.get('notes', '')
                            })
                        except ValueError:
                            # Skip invalid keys
                            continue
                    
                    # Sort by location name
                    all_tags.sort(key=lambda x: x['name'])
                    
                    for tag in all_tags:
                        writer.writerow([
                            tag['name'],
                            tag['lat'],
                            tag['lon'],
                            tag['notes']
                        ])
                except Exception as e:
                    logger.warning(f"Could not export stored locations: {e}")
                    writer.writerow(['Error loading stored locations', '', '', str(e)])
            
            messagebox.showinfo("Success", f"Analysis exported to:\n{file_path}")
            logger.info(f"Exported analysis to CSV: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
            logger.error(f"CSV export error: {e}")
    
    def setup_ui(self):
        """Setup the analysis window UI."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with title and export button
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Seestar FITS Organizer - Analysis",
            font=self.get_font(24, weight="bold")
        )
        title_label.pack(side="left")
        
        export_button = ctk.CTkButton(
            header_frame,
            text="📥 Export to CSV",
            font=self.get_font(14, weight="bold"),
            height=40,
            fg_color="#1E90FF",
            hover_color="#4169E1",
            command=self.export_to_csv
        )
        export_button.pack(side="right")
        
        # Check if no projects found
        if self.results['total_projects'] == 0:
            no_data_label = ctk.CTkLabel(
                main_frame,
                text="No projects found in the selected directory.\nMake sure you have folders ending with '_Project'.",
                font=self.get_font(14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return
        
        # Projects List Frame (left side)
        projects_frame = ctk.CTkFrame(main_frame)
        projects_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        projects_label = ctk.CTkLabel(projects_frame, text="Projects", font=self.get_font(18, weight="bold"))
        projects_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Search entry
        search_frame = ctk.CTkFrame(projects_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        search_label = ctk.CTkLabel(search_frame, text="🔍", font=self.get_font(16))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search projects...",
            height=32
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Scrollable frame for project list
        self.scroll_frame = ctk.CTkScrollableFrame(projects_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store original projects for filtering
        self.all_projects = self.results['projects'].copy()
        
        # Add aggregate statistics button at the top
        agg_button = ctk.CTkButton(
            self.scroll_frame,
            text="📊 Aggregate Statistics",
            font=self.get_font(14, weight="bold"),
            height=40,
            fg_color="#2E8B57",  # Sea green color to differentiate
            hover_color="#3CB371",
            command=lambda: self.show_aggregate_stats()
        )
        agg_button.pack(fill="x", pady=(0, 10))
        
        # Separator line
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=(0, 10))
        
        # Add project buttons
        self.project_buttons = []
        for project in self.all_projects:
            button = self.create_project_button(self.scroll_frame, project)
            self.project_buttons.append((button, project))
        
        # Project Details Frame (right side)
        details_frame = ctk.CTkFrame(main_frame)
        details_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.details_label = ctk.CTkLabel(details_frame, text="Project Details", font=self.get_font(18, weight="bold"))
        self.details_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.details_scroll = ctk.CTkScrollableFrame(details_frame)
        self.details_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial message
        self.no_selection_label = ctk.CTkLabel(
            self.details_scroll,
            text="Click on a project to view details",
            font=self.get_font(14),
            text_color="gray"
        )
        self.no_selection_label.pack(pady=50)
    
    def create_aggregate_stats(self, parent):
        """Create aggregate statistics display."""
        stats = self.results
        
        # Create grid of stats
        stats_data = [
            ("Total Projects", stats['total_projects']),
            ("Total Files", stats['total_files']),
            ("Total Size", f"{stats['total_size_gb']:.2f} GB"),
            ("Total Lights", stats['total_lights']),
            ("Total Darks", stats['total_darks']),
            ("Total Flats", stats['total_flats']),
            ("Total Bias", stats['total_bias']),
            ("Nights Captured", stats['nights_captured']),
        ]
        
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = ctk.CTkFrame(grid_frame)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            grid_frame.grid_columnconfigure(col, weight=1)
            
            label_widget = ctk.CTkLabel(stat_frame, text=label, font=self.get_font(12, weight="bold"))
            label_widget.pack(anchor="w", padx=10, pady=(10, 2))
            
            value_widget = ctk.CTkTextbox(stat_frame, height=35)
            value_widget.pack(fill="x", padx=10, pady=(2, 10))
            value_widget.insert("1.0", str(value))
            value_widget.configure(state="disabled", font=self.get_font(16))
        
        # Integration time
        hours = int(stats['total_integration_hours'])
        minutes = int((stats['total_integration_hours'] % 1) * 60)
        time_frame = ctk.CTkFrame(parent)
        time_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        time_label = ctk.CTkLabel(time_frame, text="Total Integration Time", font=self.get_font(12, weight="bold"))
        time_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        time_value = ctk.CTkTextbox(time_frame, height=35)
        time_value.pack(fill="x", padx=10, pady=(2, 10))
        time_value.insert("1.0", f"{hours}h {minutes}m")
        time_value.configure(state="disabled", font=self.get_font(16))
        
        # Unique objects and filters
        unique_frame = ctk.CTkFrame(parent)
        unique_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        objects_text = f"Objects: {', '.join(stats['unique_objects'])}" if stats['unique_objects'] else "Objects: None"
        filters_text = f"Filters: {', '.join(stats['unique_filters'])}" if stats['unique_filters'] else "Filters: None"
        
        objects_textbox = ctk.CTkTextbox(unique_frame, height=30)
        objects_textbox.pack(fill="x", padx=10, pady=(5, 2))
        objects_textbox.insert("1.0", objects_text)
        objects_textbox.configure(state="disabled", font=self.get_font(14))
        
        filters_textbox = ctk.CTkTextbox(unique_frame, height=30)
        filters_textbox.pack(fill="x", padx=10, pady=(2, 10))
        filters_textbox.insert("1.0", filters_text)
        filters_textbox.configure(state="disabled", font=self.get_font(14))
        
        # Capture Locations expandable section
        locations_frame = ctk.CTkFrame(parent)
        locations_frame.pack(fill="x", padx=10, pady=5)
        
        locations_button = ctk.CTkButton(
            locations_frame,
            text="▶ Capture Locations",
            font=self.get_font(12, weight="bold"),
            height=35,
            command=lambda: self.toggle_expandable_section(locations_button, locations_content)
        )
        locations_button.pack(fill="x", padx=10, pady=(10, 5))
        
        locations_content = ctk.CTkFrame(locations_frame)
        locations_content.pack(fill="x", padx=10, pady=(0, 10))
        locations_content.pack_forget()  # Initially collapsed
        
        # Collect locations with objects from all projects
        location_data = []  # [(site, lat, lon, objects_set)]
        for project in stats['projects']:
            site = project.get('site')
            lat = project.get('latitude')
            lon = project.get('longitude')
            objects = project.get('objects', set())
            if site or (lat and lon):
                location_data.append((site, lat, lon, objects))
        
        if location_data:
            # Group nearby locations (within threshold degrees)
            grouped_locations = []
            used_indices = set()
            
            # Get threshold from settings (default: 0.005 degrees ≈ 600 yards)
            threshold = self.settings.get_location_threshold()
            
            for i, (site1, lat1, lon1, objects1) in enumerate(location_data):
                if i in used_indices:
                    continue
                
                # Start a new group
                group = [(site1, lat1, lon1, objects1)]
                used_indices.add(i)
                
                # Find nearby locations
                for j, (site2, lat2, lon2, objects2) in enumerate(location_data):
                    if j in used_indices:
                        continue
                    
                    # Calculate distance if both have coordinates
                    if lat1 and lon1 and lat2 and lon2:
                        try:
                            lat1_f = float(lat1)
                            lon1_f = float(lon1)
                            lat2_f = float(lat2)
                            lon2_f = float(lon2)
                            
                            # Simple Euclidean distance in degrees
                            distance = ((lat2_f - lat1_f) ** 2 + (lon2_f - lon1_f) ** 2) ** 0.5
                            
                            if distance < threshold:
                                group.append((site2, lat2, lon2, objects2))
                                used_indices.add(j)
                        except (ValueError, TypeError):
                            pass
                    elif site1 and site2 and site1 == site2:
                        # Same site name but no coordinates, group them
                        group.append((site2, lat2, lon2, objects2))
                        used_indices.add(j)
                
                grouped_locations.append(group)
            
            # Display grouped locations
            for idx, group in enumerate(grouped_locations, 1):
                # Calculate average lat/lon and collect all objects
                lats = [lat for _, lat, _, _ in group if lat]
                lons = [lon for _, _, lon, _ in group if lon]
                all_objects = set()
                for _, _, _, objects in group:
                    all_objects.update(objects)
                
                avg_lat = sum(float(l) for l in lats) / len(lats) if lats else None
                avg_lon = sum(float(l) for l in lons) / len(lons) if lons else None
                
                # Create location card
                loc_card = ctk.CTkFrame(locations_content, fg_color="gray20")
                loc_card.pack(fill="x", padx=10, pady=5)
                
                # Header row: location number + project count
                header_frame = ctk.CTkFrame(loc_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                # Check for saved tag
                tag = self.location_tags.get_tag(str(avg_lat), str(avg_lon))
                if tag:
                    display_name = f"⭐ {tag['name']}"
                else:
                    display_name = f"⭐ Location {idx}"
                
                location_label = ctk.CTkLabel(
                    header_frame,
                    text=display_name,
                    font=self.get_font(14, weight="bold")
                )
                location_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    header_frame,
                    text=f"{len(group)} projects",
                    font=self.get_font(12),
                    text_color="gray"
                )
                count_label.pack(side="right")
                
                # Coordinates row
                if avg_lat and avg_lon:
                    coord_textbox = ctk.CTkTextbox(loc_card, height=25)
                    coord_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    coord_textbox.insert("1.0", f"Lat: {avg_lat:.6f}, Lon: {avg_lon:.6f}")
                    coord_textbox.configure(state="disabled", font=self.get_font(12))
                
                # Objects row
                if all_objects:
                    obj_textbox = ctk.CTkTextbox(loc_card, height=30)
                    obj_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    obj_textbox.insert("1.0", f"Objects: {', '.join(sorted(all_objects))}")
                    obj_textbox.configure(state="disabled", font=self.get_font(12))
                
                # Google Maps button
                if avg_lat and avg_lon:
                    maps_button = ctk.CTkButton(
                        loc_card,
                        text="🗺️ Open in Google Maps",
                        font=self.get_font(12),
                        height=32,
                        fg_color="#4285F4",
                        hover_color="#3367D6",
                        command=lambda l=avg_lat, ln=avg_lon: self.open_google_maps(str(l), str(ln))
                    )
                    maps_button.pack(fill="x", padx=10, pady=(0, 5))
                
                # Tag button
                if avg_lat and avg_lon:
                    tag_button_text = "✏️ Edit Tag" if tag else "➕ Add Tag"
                    tag_button = ctk.CTkButton(
                        loc_card,
                        text=tag_button_text,
                        font=self.get_font(12),
                        height=32,
                        fg_color="#FFA500",
                        hover_color="#FF8C00",
                        command=lambda l=avg_lat, ln=avg_lon: self.open_tag_dialog(str(l), str(ln))
                    )
                    tag_button.pack(fill="x", padx=10, pady=(5, 10))
        else:
            no_loc_label = ctk.CTkLabel(locations_content, text="No capture locations found", font=self.get_font(14))
            no_loc_label.pack(padx=10, pady=10)
    
    def create_project_button(self, parent, project):
        """Create a clickable button for a single project."""
        button = ctk.CTkButton(
            parent,
            text=project['name'],
            font=self.get_font(14),
            height=40,
            command=lambda: self.show_project_details(project)
        )
        button.pack(fill="x", pady=5)
        return button
    
    def on_search_change(self, event):
        """Handle search text change to filter projects."""
        search_text = self.search_entry.get().lower()
        
        # Clear current project buttons (except aggregate stats and separator)
        children = self.scroll_frame.winfo_children()
        # Keep first 2 children (aggregate button and separator)
        for i, widget in enumerate(children):
            if i >= 2:
                widget.destroy()
        
        # Filter projects
        filtered_projects = []
        for project in self.all_projects:
            # Search in project name
            if search_text in project['name'].lower():
                filtered_projects.append(project)
                continue
            
            # Search in objects
            objects = project.get('objects', set())
            if any(search_text in obj.lower() for obj in objects):
                filtered_projects.append(project)
                continue
            
            # Search in site/location
            site = project.get('site', '')
            if site and search_text in site.lower():
                filtered_projects.append(project)
                continue
        
        # Re-add project buttons
        for project in filtered_projects:
            self.create_project_button(self.scroll_frame, project)
    
    def show_aggregate_stats(self):
        """Show aggregate statistics in the details panel."""
        # Clear current project tracking
        self.current_project = None
        
        # Reset the details label to show no specific project
        self.details_label.configure(text="Aggregate Statistics")
        
        # Clear previous details
        for widget in self.details_scroll.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(
            self.details_scroll,
            text="Aggregate Statistics",
            font=self.get_font(20, weight="bold")
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Create aggregate stats display
        self.create_aggregate_stats(self.details_scroll)
    
    def open_file_explorer(self, path: str):
        """Open the given path in the system's file explorer."""
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
            logger.info(f"Opened file explorer: {path}")
        except Exception as e:
            logger.error(f"Failed to open file explorer: {e}")
            messagebox.showerror("Error", f"Failed to open file explorer: {str(e)}")
    
    def open_google_maps(self, lat: str, lon: str):
        """Open Google Maps centered on the given coordinates."""
        try:
            url = f"https://www.google.com/maps?q={lat},{lon}"
            webbrowser.open(url)
            logger.info(f"Opened Google Maps for location: {lat}, {lon}")
        except Exception as e:
            logger.error(f"Failed to open Google Maps: {e}")
            messagebox.showerror("Error", f"Failed to open Google Maps: {str(e)}")
    
    def open_sky_atlas(self, ra: str, dec: str, obj_name: str):
        """Open Aladin Lite sky atlas centered on the object's RA/DEC coordinates."""
        try:
            if ra and dec:
                # Aladin Lite expects RA and DEC in degrees
                # RA: 0-360 degrees, DEC: -90 to +90 degrees
                ra_degrees = float(ra)
                dec_degrees = float(dec)
                
                # Aladin Lite URL format with DSS colored survey
                # Seestar S50 FOV: 0.73° x 1°, using 1.2° to show full context
                url = f"https://aladin.u-strasbg.fr/AladinLite/?target={ra_degrees:.5f}%20{dec_degrees:.5f}&fov=1.2&survey=CDS%2FP%2FDSS2%2Fcolor"
                webbrowser.open(url)
                logger.info(f"Opened Aladin Lite for RA: {ra_degrees:.5f}°, DEC: {dec_degrees:.5f}°")
            elif obj_name and obj_name.strip():
                # Fallback to Telescopius with object name if no coordinates
                encoded_name = obj_name.replace(' ', '%20')
                url = f"https://telescopius.com/deepsky/objinfo/{encoded_name}"
                webbrowser.open(url)
                logger.info(f"Opened Telescopius for object: {obj_name}")
            else:
                messagebox.showwarning("No Coordinates", "No RA/DEC coordinates or object name available.")
        except Exception as e:
            logger.error(f"Failed to open sky atlas: {e}")
            messagebox.showerror("Error", f"Failed to open sky atlas: {str(e)}")
    
    def open_image_preview(self, project: dict, object_name: str):
        """Open image preview window for the first light frame of this object."""
        try:
            # Get project path
            project_path = Path(project['path'])
            fits_files = []
            
            # First try lights folder
            lights_folder = project_path / 'lights'
            if lights_folder.exists():
                fits_files = list(lights_folder.glob('*.fits')) + list(lights_folder.glob('*.FIT'))
            
            # If no lights folder or no files found, search entire project directory
            if not fits_files:
                for item in project_path.rglob('*.fits'):
                    fits_files.append(item)
                for item in project_path.rglob('*.FIT'):
                    fits_files.append(item)
            
            if not fits_files:
                messagebox.showwarning("No Images", "No FITS files found for this project.")
                return
            
            # Try to find a file matching the object name first
            image_file = None
            for fits_file in fits_files:
                if object_name.lower() in fits_file.name.lower():
                    image_file = fits_file
                    break
            
            # If no match, just take the first file
            if not image_file:
                image_file = fits_files[0]
            
            # Open preview window
            PreviewWindow(self, image_file)
            logger.info(f"Opened preview for {image_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to open image preview: {e}")
            messagebox.showerror("Error", f"Failed to open image preview: {str(e)}")
    
    def open_tag_dialog(self, lat: str, lon: str):
        """Open dialog to add/edit location tag."""
        tag = self.location_tags.get_tag(lat, lon)
        
        # Create tag dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Location Tag")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Name field
        name_label = ctk.CTkLabel(dialog, text="Location Name:", font=self.get_font(13, weight="bold"))
        name_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="e.g., Backyard Observatory")
        name_entry.pack(fill="x", padx=20, pady=(0, 10))
        if tag:
            name_entry.insert(0, tag['name'])
        
        # Notes field
        notes_label = ctk.CTkLabel(dialog, text="Notes (optional):", font=self.get_font(13, weight="bold"))
        notes_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        notes_textbox = ctk.CTkTextbox(dialog, height=100)
        notes_textbox.pack(fill="x", padx=20, pady=(0, 10))
        if tag and tag.get('notes'):
            notes_textbox.insert("1.0", tag['notes'])
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        def save_tag():
            name = name_entry.get().strip()
            notes = notes_textbox.get("1.0", "end").strip()
            
            if not name:
                messagebox.showerror("Error", "Location name is required")
                return
            
            self.location_tags.set_tag(lat, lon, name, notes)
            messagebox.showinfo("Success", "Location tag saved!")
            dialog.destroy()
            # Refresh the current view (project details or aggregate stats)
            if self.current_project:
                self.show_project_details(self.current_project)
            else:
                self.show_aggregate_stats()
        
        def delete_tag():
            if tag:
                if messagebox.askyesno("Confirm", "Delete this location tag?"):
                    self.location_tags.delete_tag(lat, lon)
                    messagebox.showinfo("Success", "Location tag deleted!")
                    dialog.destroy()
                    # Refresh the current view (project details or aggregate stats)
                    if self.current_project:
                        self.show_project_details(self.current_project)
                    else:
                        self.show_aggregate_stats()
            else:
                messagebox.showinfo("Info", "No tag to delete")
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            fg_color="#2E8B57",
            hover_color="#3CB371",
            command=save_tag
        )
        save_button.pack(side="left", padx=(0, 5))
        
        if tag:
            delete_button = ctk.CTkButton(
                button_frame,
                text="Delete",
                fg_color="#DC143C",
                hover_color="#B22222",
                command=delete_tag
            )
            delete_button.pack(side="left", padx=(0, 5))
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side="right")
    
    def _format_datetime(self, datetime_str: str) -> str:
        """Format datetime string to human-readable format using configured timezone."""
        try:
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromisoformat(datetime_str)
            
            # Get timezone from settings
            tz_setting = self.settings.get_timezone()
            
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            if tz_setting == "UTC":
                # Keep as UTC
                dt_final = dt
            elif tz_setting == "EST":
                # Convert to EST (UTC-5)
                est = timezone(timedelta(hours=-5))
                dt_final = dt.astimezone(est)
            elif tz_setting == "Local":
                # Convert to local timezone
                dt_final = dt.astimezone()
            else:
                # Default to PST (UTC-8)
                pst = timezone(timedelta(hours=-8))
                dt_final = dt.astimezone(pst)
            
            return dt_final.strftime("%Y-%m-%d %I:%M %p")
        except Exception:
            return datetime_str
    
    def show_project_details(self, project):
        """Show detailed information for a selected project."""
        # Track the current project for refresh after tag edits
        self.current_project = project
        
        # Update details label with project name
        self.details_label.configure(text=f"Project Details - {project['name']}")
        
        # Clear previous details
        for widget in self.details_scroll.winfo_children():
            widget.destroy()
        
        # Track expandable sections for accordion behavior
        self.expandable_sections = []
        
        # Project summary (collapsible)
        summary_frame = ctk.CTkFrame(self.details_scroll)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        summary_button = ctk.CTkButton(
            summary_frame,
            text="▶ Project Summary",
            font=self.get_font(12, weight="bold"),
            height=35,
            command=lambda: self.toggle_expandable_section(summary_button, summary_content)
        )
        summary_button.pack(fill="x", padx=10, pady=(10, 5))
        
        summary_content = ctk.CTkFrame(summary_frame)
        summary_content.pack(fill="x", padx=10, pady=(0, 10))
        summary_content.pack_forget()  # Initially collapsed
        
        # Track this section for accordion behavior
        self.expandable_sections.append((summary_button, summary_content))
        
        # Frame counts
        counts_label = ctk.CTkLabel(summary_content, text="Frame Counts", font=self.get_font(12, weight="bold"))
        counts_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        counts_text = (
            f"Lights: {project['lights']} | "
            f"Darks: {project['darks']} | "
            f"Flats: {project['flats']} | "
            f"Bias: {project['bias']}"
        )
        counts_value = ctk.CTkTextbox(summary_content, height=30)
        counts_value.pack(fill="x", padx=10, pady=(0, 5))
        counts_value.insert("1.0", counts_text)
        counts_value.configure(state="disabled", font=self.get_font(14))
        
        # Exposure breakdown for lights
        if project.get('lights_by_exposure'):
            lights_exp_label = ctk.CTkLabel(summary_content, text="Lights by Exposure:", font=self.get_font(12, weight="bold"))
            lights_exp_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            for exp, count in sorted(project['lights_by_exposure'].items()):
                exp_textbox = ctk.CTkTextbox(summary_content, height=25)
                exp_textbox.pack(fill="x", padx=10, pady=1)
                exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                exp_textbox.configure(state="disabled", font=self.get_font(12))
        
        # Exposure breakdown for darks
        if project.get('darks_by_exposure'):
            darks_exp_label = ctk.CTkLabel(summary_content, text="Darks by Exposure:", font=self.get_font(12, weight="bold"))
            darks_exp_label.pack(anchor="w", padx=10, pady=(5, 2))
            
            for exp, count in sorted(project['darks_by_exposure'].items()):
                exp_textbox = ctk.CTkTextbox(summary_content, height=25)
                exp_textbox.pack(fill="x", padx=10, pady=1)
                exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                exp_textbox.configure(state="disabled", font=self.get_font(12))
        
        # Integration time
        time_label = ctk.CTkLabel(summary_content, text="Total Integration Time", font=self.get_font(12, weight="bold"))
        time_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        total_seconds = project['integration_seconds']
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        time_value = ctk.CTkTextbox(summary_content, height=30)
        time_value.pack(fill="x", padx=10, pady=(0, 10))
        time_value.insert("1.0", f"{hours}h {minutes}m {seconds}s")
        time_value.configure(state="disabled", font=self.get_font(14))
        
        # File statistics
        file_label = ctk.CTkLabel(summary_content, text="File Statistics", font=self.get_font(12, weight="bold"))
        file_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        file_text = f"{project['total_files']} files | {project['total_size_mb']:.2f} MB"
        file_value = ctk.CTkTextbox(summary_content, height=30)
        file_value.pack(fill="x", padx=10, pady=(0, 10))
        file_value.insert("1.0", file_text)
        file_value.configure(state="disabled", font=self.get_font(14))
        
        # Filters
        if project['filters']:
            filter_label = ctk.CTkLabel(summary_content, text="Filters", font=self.get_font(12, weight="bold"))
            filter_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            filter_textbox = ctk.CTkTextbox(summary_content, height=30)
            filter_textbox.pack(fill="x", padx=10, pady=(0, 10))
            filter_textbox.insert("1.0", ', '.join(project['filters']))
            filter_textbox.configure(state="disabled", font=self.get_font(14))
        
        # Exposures
        if project['exposures']:
            exp_label = ctk.CTkLabel(summary_content, text="Exposure Times", font=self.get_font(12, weight="bold"))
            exp_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            exp_text = ', '.join([f"{e}s" for e in project['exposures']])
            exp_textbox = ctk.CTkTextbox(summary_content, height=30)
            exp_textbox.pack(fill="x", padx=10, pady=(0, 10))
            exp_textbox.insert("1.0", exp_text)
            exp_textbox.configure(state="disabled", font=self.get_font(14))
        
        # Path
        path_label = ctk.CTkLabel(summary_content, text="Project Path", font=self.get_font(12, weight="bold"))
        path_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        path_textbox = ctk.CTkTextbox(summary_content, height=30)
        path_textbox.pack(fill="x", padx=10, pady=(0, 5))
        path_textbox.insert("1.0", project['path'])
        path_textbox.configure(state="disabled", font=self.get_font(12), text_color="gray")
        
        # Open in File Explorer button
        open_button = ctk.CTkButton(
            summary_content,
            text="📂 Open in File Explorer",
            font=self.get_font(12),
            height=32,
            command=lambda: self.open_file_explorer(project['path'])
        )
        open_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Individual sessions expandable sections
        # Session tuple: (obj_name, ra, dec, start, end, lights, integration, exposures, lights_by_exposure)
        if project.get('sessions'):
            for idx, (obj, ra, dec, start, end, lights, integration, exposures, lights_by_exposure) in enumerate(project['sessions']):
                session_frame = ctk.CTkFrame(self.details_scroll)
                session_frame.pack(fill="x", padx=10, pady=5)
                
                session_content = ctk.CTkFrame(session_frame)
                session_content.pack(fill="x", padx=10, pady=(0, 10))
                session_content.pack_forget()  # Initially collapsed
                
                session_button_text = f"▶ {obj} - Session {idx + 1}: {self._format_datetime(start)}"
                session_button = ctk.CTkButton(
                    session_frame,
                    text=session_button_text,
                    font=self.get_font(12),
                    height=35
                )
                session_button.pack(fill="x", padx=10, pady=(10, 5))
                session_button.configure(command=lambda btn=session_button, content=session_content: self.toggle_expandable_section(btn, content))
                
                # Track this section for accordion behavior
                self.expandable_sections.append((session_button, session_content))
                
                # Session details - Capture Location section (first)
                if project.get('latitude') and project.get('longitude'):
                    location_label = ctk.CTkLabel(session_content, text="Capture Location:", font=self.get_font(12, weight="bold"))
                    location_label.pack(anchor="w", padx=10, pady=(5, 2))
                    
                    tag = self.location_tags.get_tag(str(project['latitude']), str(project['longitude']))
                    if tag:
                        location_textbox = ctk.CTkTextbox(session_content, height=25)
                        location_textbox.pack(fill="x", padx=10, pady=(0, 2))
                        location_textbox.insert("1.0", f"⭐ {tag['name']}")
                        location_textbox.configure(state="disabled", font=self.get_font(14))
                    
                    # Site
                    if project.get('site'):
                        site_textbox = ctk.CTkTextbox(session_content, height=25)
                        site_textbox.pack(fill="x", padx=10, pady=2)
                        site_textbox.insert("1.0", f"Site: {project['site']}")
                        site_textbox.configure(state="disabled", font=self.get_font(14))
                    
                    # Coordinates
                    coord_textbox = ctk.CTkTextbox(session_content, height=25)
                    coord_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    coord_textbox.insert("1.0", f"Lat: {project['latitude']}, Lon: {project['longitude']}")
                    coord_textbox.configure(state="disabled", font=self.get_font(14))
                    
                    # Tag button
                    tag_button_text = "✏️ Edit Tag" if tag else "➕ Add Tag"
                    tag_button = ctk.CTkButton(
                        session_content,
                        text=tag_button_text,
                        font=self.get_font(12),
                        height=32,
                        fg_color="#FFA500",
                        hover_color="#FF8C00",
                        command=lambda l=project['latitude'], ln=project['longitude']: self.open_tag_dialog(str(l), str(ln))
                    )
                    tag_button.pack(fill="x", padx=10, pady=(0, 5))
                    
                    # Google Maps button
                    maps_button = ctk.CTkButton(
                        session_content,
                        text="🗺️ Open in Google Maps",
                        font=self.get_font(12),
                        height=32,
                        fg_color="#4285F4",
                        hover_color="#3367D6",
                        command=lambda l=project['latitude'], ln=project['longitude']: self.open_google_maps(str(l), str(ln))
                    )
                    maps_button.pack(fill="x", padx=10, pady=(0, 10))
                
                # Object Information section
                object_info_label = ctk.CTkLabel(session_content, text="Object Information:", font=self.get_font(12, weight="bold"))
                object_info_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                # Object name
                obj_textbox = ctk.CTkTextbox(session_content, height=25)
                obj_textbox.pack(fill="x", padx=10, pady=2)
                obj_textbox.insert("1.0", f"Name: {obj}")
                obj_textbox.configure(state="disabled", font=self.get_font(14))
                
                # RA/DEC coordinates
                if ra or dec:
                    # Use coordinate format setting for display
                    coord_format = self.settings.get_coordinate_format()
                    ra_val, dec_val = format_ra_dec(ra, dec, coord_format)
                    coords_textbox = ctk.CTkTextbox(session_content, height=25)
                    coords_textbox.pack(fill="x", padx=10, pady=2)
                    coords_textbox.insert("1.0", f"RA: {ra_val}, DEC: {dec_val}")
                    coords_textbox.configure(state="disabled", font=self.get_font(14))
                    
                    # Constellation
                    constellation = get_constellation(ra, dec)
                    if constellation and constellation != 'Unknown':
                        const_textbox = ctk.CTkTextbox(session_content, height=25)
                        const_textbox.pack(fill="x", padx=10, pady=2)
                        const_textbox.insert("1.0", f"Constellation: {constellation}")
                        const_textbox.configure(state="disabled", font=self.get_font(14))
                    
                    # Sky Atlas button - Open Aladin Lite with object coordinates
                    sky_button = ctk.CTkButton(
                        session_content,
                        text="🔭 Open in Sky Atlas (Aladin)",
                        font=self.get_font(12),
                        height=32,
                        fg_color="#2E86AB",
                        hover_color="#1E5F7A",
                        command=lambda r=ra, d=dec, name=obj: self.open_sky_atlas(r, d, name)
                    )
                    sky_button.pack(fill="x", padx=10, pady=(0, 5))
                    
                    # Preview Image button
                    preview_button = ctk.CTkButton(
                        session_content,
                        text="🔍 Preview Image",
                        font=self.get_font(12),
                        height=32,
                        fg_color="#4A90A4",
                        hover_color="#3A7A8C",
                        command=lambda p=project, o=obj: self.open_image_preview(p, o)
                    )
                    preview_button.pack(fill="x", padx=10, pady=(0, 10))
                
                # Time section
                time_label = ctk.CTkLabel(session_content, text="Time:", font=self.get_font(12, weight="bold"))
                time_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                start_textbox = ctk.CTkTextbox(session_content, height=25)
                start_textbox.pack(fill="x", padx=10, pady=2)
                start_textbox.insert("1.0", f"Start: {self._format_datetime(start)}")
                start_textbox.configure(state="disabled", font=self.get_font(14))
                
                end_textbox = ctk.CTkTextbox(session_content, height=25)
                end_textbox.pack(fill="x", padx=10, pady=(0, 5))
                end_textbox.insert("1.0", f"End: {self._format_datetime(end)}")
                end_textbox.configure(state="disabled", font=self.get_font(14))
                
                # Captures section
                captures_label = ctk.CTkLabel(session_content, text="Captures:", font=self.get_font(12, weight="bold"))
                captures_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                lights_textbox = ctk.CTkTextbox(session_content, height=25)
                lights_textbox.pack(fill="x", padx=10, pady=2)
                lights_textbox.insert("1.0", f"Lights: {lights}")
                lights_textbox.configure(state="disabled", font=self.get_font(14))
                
                if integration > 0:
                    hours = int(integration // 3600)
                    minutes = int((integration % 3600) // 60)
                    seconds = int(integration % 60)
                    integration_text = f"{hours}h {minutes}m {seconds}s"
                    
                    integration_textbox = ctk.CTkTextbox(session_content, height=25)
                    integration_textbox.pack(fill="x", padx=10, pady=(0, 5))
                    integration_textbox.insert("1.0", f"Integration: {integration_text}")
                    integration_textbox.configure(state="disabled", font=self.get_font(14))
                
                # Exposure breakdown section
                if lights_by_exposure:
                    exp_label = ctk.CTkLabel(session_content, text="Exposure Breakdown:", font=self.get_font(12, weight="bold"))
                    exp_label.pack(anchor="w", padx=10, pady=(5, 2))
                    
                    for exp, count in sorted(lights_by_exposure.items()):
                        exp_textbox = ctk.CTkTextbox(session_content, height=25)
                        exp_textbox.pack(fill="x", padx=10, pady=1)
                        exp_textbox.insert("1.0", f"{exp}s: {count} frames")
                        exp_textbox.configure(state="disabled", font=self.get_font(12))
                
                if exposures:
                    exp_text = ', '.join([f"{e}s" for e in exposures])
                    exp_textbox = ctk.CTkTextbox(session_content, height=25)
                    exp_textbox.pack(fill="x", padx=10, pady=(2, 10))
                    exp_textbox.insert("1.0", f"Exposures: {exp_text}")
                    exp_textbox.configure(state="disabled", font=self.get_font(14))
    
    def toggle_expandable_section(self, button, content_frame):
        """Toggle visibility of an expandable section with accordion behavior."""
        if content_frame.winfo_ismapped():
            # Collapse this section
            content_frame.pack_forget()
            button.configure(text=button.cget("text").replace("▼", "▶"))
        else:
            # Collapse all other sections first (if accordion behavior is enabled)
            if hasattr(self, 'expandable_sections'):
                for other_button, other_content in self.expandable_sections:
                    try:
                        if other_content.winfo_ismapped() and other_content != content_frame:
                            other_content.pack_forget()
                            other_button.configure(text=other_button.cget("text").replace("▼", "▶"))
                    except Exception:
                        # Widget might be invalid, skip it
                        pass
            
            # Expand this section
            content_frame.pack(fill="x")
            button.configure(text=button.cget("text").replace("▶", "▼"))
