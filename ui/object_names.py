"""
Object Names Module

Provides common name lookups for astronomical objects, backed by a local
dictionary and a SIMBAD-queried cache.  Also stores verbose object types
fetched from SIMBAD so the UI can display them when no common name exists.
"""

import json
import logging
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache file locations
# ---------------------------------------------------------------------------
COMMON_NAMES_CACHE_FILE = Path.home() / '.seestar_fits_organizer' / 'common_names_cache.json'
OBJECT_TYPES_CACHE_FILE  = Path.home() / '.seestar_fits_organizer' / 'object_types_cache.json'

# ---------------------------------------------------------------------------
# Built-in common names dictionary
# ---------------------------------------------------------------------------
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
    'M81': "Bode's Galaxy",
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
    'M94': "Cat's Eye Galaxy",
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
    'NGC6974': 'Veil Nebula',
    'NGC6979': 'Veil Nebula',
    'NGC6960-6992': 'Veil Nebula Complex',
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
    'NGC6523': 'Lagoon Nebula',
    'NGC6611': 'Eagle Nebula',
    'NGC6720': 'Ring Nebula',
    'NGC1952': 'Crab Nebula',
    'NGC7293': 'Helix Nebula',
    'NGC3372': 'Eta Carinae Nebula',
    'NGC2261': "Hubble's Variable Nebula",
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
    'NGC7662': 'Blue Snowball Nebula',
    'NGC6210': 'Turtle Nebula',
    'NGC891': 'Silver Sliver Galaxy',
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
    'NGC5904': 'M5',
    'NGC6205': 'Hercules Globular Cluster',
    'NGC6341': 'M92',
    'NGC7078': 'M15',
    'NGC7099': 'M30',
    'NGC205': 'M110',
    'NGC221': 'M32',
    'NGC224': 'Andromeda Galaxy',
    'NGC598': 'Triangulum Galaxy',
    'NGC3031': "Bode's Galaxy",
    'NGC3034': 'Cigar Galaxy',
    'NGC4594': 'Sombrero Galaxy',
    'NGC5457': 'Pinwheel Galaxy',
    'NGC5194': 'Whirlpool Galaxy',
    'NGC5195': 'Whirlpool Companion',
    'NGC6543': "Cat's Eye Nebula",
    # Additional popular NGC targets for Seestar
    'NGC6946': 'Fireworks Galaxy',
    'NGC2403': 'Caldwell 7',
    'NGC7331': 'Deer Lick Galaxy',
    'NGC7317': "Stephan's Quintet",
    'NGC7318': "Stephan's Quintet",
    'NGC7319': "Stephan's Quintet",
    'NGC7320': "Stephan's Quintet",
    'NGC7320C': "Stephan's Quintet",
    'NGC4038': 'Antennae Galaxies',
    'NGC4039': 'Antennae Galaxies',
    'NGC4889': 'Coma Galaxy Cluster',
    'NGC4874': 'Coma Galaxy Cluster',
    'NGC4649': 'M60',
    'NGC4621': 'M59',
    'NGC4552': 'M89',
    'NGC4548': 'M91',
    'NGC4501': 'M88',
    'NGC4486': 'Virgo A',
    'NGC4472': 'M49',
    'NGC4303': 'M61',
    'NGC4254': 'M99',
    'NGC4321': 'M100',
    'NGC4258': 'M106',
    'NGC4051': 'Seyfert Galaxy',
    'NGC3628': 'Hamburger Galaxy',
    'NGC3627': 'M66',
    'NGC3623': 'M65',
    'NGC2903': 'Leo I Galaxy',
    'NGC2841': "Tiger's Eye Galaxy",
    'NGC2683': 'UFO Galaxy',
    'NGC1300': 'Barred Spiral Galaxy',
    'NGC1232': 'Grand Design Spiral',
    'NGC1055': None,
    'NGC1023': None,
    'NGC772': 'Arp 78',
    'NGC925': None,
    'NGC7479': 'Propeller Galaxy',
    'NGC7814': 'Little Sombrero Galaxy',
    'NGC7789': "Caroline's Rose",
    'NGC7762': None,
    'NGC7380': 'Wizard Nebula',
    'NGC7023': 'Iris Nebula',
    'NGC6888': 'Crescent Nebula',
    'NGC6871': None,
    'NGC6826': 'Blinking Planetary Nebula',
    'NGC6819': 'Foxhead Cluster',
    'NGC6818': 'Little Gem Nebula',
    'NGC6811': None,
    'NGC6781': 'Snowglobe Nebula',
    'NGC6752': 'Pavo Globular',
    'NGC6744': None,
    'NGC6723': None,
    'NGC6712': None,
    'NGC6709': None,
    'NGC6705': 'Wild Duck Cluster',
    'NGC6694': 'M26',
    'NGC6681': 'M70',
    'NGC6656': 'M22',
    'NGC6626': 'M28',
    'NGC6618': 'Omega Nebula',
    'NGC6603': 'M24',
    'NGC6530': 'Lagoon Cluster',
    'NGC6522': None,
    'NGC6520': None,
    'NGC6494': 'M23',
    'NGC6475': 'M7',
    'NGC6405': 'M6',
    'NGC6404': None,
    'NGC6352': None,
    'NGC6333': 'M9',
    'NGC6218': 'M12',
    'NGC6171': 'M107',
    'NGC6093': 'M80',
    'NGC6121': 'M4',
    'NGC6101': None,
    'NGC6087': None,
    'NGC6067': None,
    'NGC6025': None,
    'NGC5986': None,
    'NGC5897': None,
    'NGC5866': 'Spindle Galaxy',
    'NGC5813': None,
    'NGC5746': None,
    'NGC5689': None,
    'NGC5676': None,
    'NGC5566': None,
    'NGC5548': None,
    'NGC5506': None,
    'NGC5474': None,
    'NGC5466': None,
    'NGC5364': None,
    'NGC5363': None,
    'NGC5353': None,
    'NGC5350': None,
    'NGC5322': None,
    'NGC5248': None,
    'NGC5236': 'Southern Pinwheel Galaxy',
    'NGC5128': 'Centaurus A',
    'NGC4945': None,
    'NGC4833': None,
    'NGC4755': 'Jewel Box Cluster',
    'NGC4736': 'M94',
    'NGC4631': 'Whale Galaxy',
    'NGC4627': None,
    'NGC4565': 'Needle Galaxy',
    'NGC4559': None,
    'NGC4449': None,
    'NGC4395': None,
    'NGC4244': 'Silver Needle Galaxy',
    'NGC4236': None,
    'NGC4216': None,
    'NGC4214': None,
    'NGC4203': None,
    'NGC4192': 'M98',
    'NGC4147': None,
    'NGC4125': None,
    'NGC4088': None,
    'NGC4013': None,
    'NGC3992': 'M109',
    'NGC3982': None,
    'NGC3953': None,
    'NGC3938': None,
    'NGC3893': None,
    'NGC3877': None,
    'NGC3729': None,
    'NGC3718': 'Warped Galaxy',
    'NGC3675': None,
    'NGC3556': 'M108',
    'NGC3521': None,
    'NGC3516': None,
    'NGC3486': None,
    'NGC3414': None,
    'NGC3384': None,
    'NGC3379': 'M105',
    'NGC3351': 'M95',
    'NGC3344': None,
    'NGC3310': 'Bow-Tie Galaxy',
    'NGC3227': None,
    'NGC3190': None,
    'NGC3185': None,
    'NGC3184': 'Little Pinwheel Galaxy',
    'NGC3147': None,
    'NGC3115': 'Spindle Galaxy',
    'NGC3077': None,
    'NGC2976': None,
    'NGC2974': None,
    'NGC2859': None,
    'NGC2775': None,
    'NGC2768': None,
    'NGC2742': None,
    'NGC2736': 'Pencil Nebula',
    'NGC2359': "Thor's Helmet",
    'NGC2346': 'Butterfly Nebula',
    'NGC2343': None,
    'NGC2301': None,
    'NGC2281': None,
    'NGC2232': None,
    'NGC2194': None,
    'NGC2175': 'Monkey Head Nebula',
    'NGC2169': '37 Cluster',
    'NGC2158': None,
    'NGC2129': None,
    'NGC2112': None,
    'NGC2099': 'M37',
    'NGC2068': 'M78',
    'NGC2067': None,
    'NGC2063': None,
    'NGC2022': None,
    'NGC2023': None,
    'NGC1977': 'Running Man Nebula',
    'NGC1975': 'Running Man Nebula',
    'NGC1973': 'Running Man Nebula',
    'NGC1931': None,
    'NGC1907': None,
    'NGC1893': None,
    'NGC1857': None,
    'NGC1851': None,
    'NGC1817': None,
    'NGC1807': None,
    'NGC1788': None,
    'NGC1746': None,
    'NGC1647': None,
    'NGC1637': None,
    'NGC1624': None,
    'NGC1579': 'Northern Trifid',
    'NGC1528': None,
    'NGC1514': 'Crystal Ball Nebula',
    'NGC1502': None,
    'NGC1491': 'Fossil Footprint Nebula',
    'NGC1432': 'Maia Nebula',
    'NGC1333': None,
    'NGC1316': 'Fornax A',
    'NGC1291': None,
    'NGC1275': 'Perseus A',
    'NGC1068': 'M77',
    'NGC1049': None,
    'NGC1022': None,
    # IC objects (popular)
    'IC434': 'Horsehead Nebula',
    'IC4603': 'Rho Ophiuchi',
    'IC4604': 'Rho Ophiuchi',
    'IC4605': 'Rho Ophiuchi',
    'IC4592': 'Blue Horsehead Nebula',
    'IC1318': 'Gamma Cygni Nebula',
    'IC1805': 'Heart Nebula',
    'IC1848': 'Soul Nebula',
    'IC405': 'Flaming Star Nebula',
    'IC410': 'Tadpoles Nebula',
    'IC2177': 'Seagull Nebula',
    'IC1396': 'Elephant Trunk Nebula',
    'IC5070': 'Pelican Nebula',
    'IC5067': 'Pelican Nebula',
    'IC5146': 'Cocoon Nebula',
    'IC2118': 'Witch Head Nebula',
    'IC2944': 'Running Chicken Nebula',
    'IC2948': 'Running Chicken Nebula',
    'IC4628': 'Prawn Nebula',
    'IC4701': None,
    'IC1274': None,
    'IC1287': None,
    'IC1297': None,
    'IC2602': 'Southern Pleiades',
    'IC2391': 'Omicron Velorum Cluster',
    'IC2395': None,
    'IC2488': None,
    'IC4665': None,
    'IC4756': None,
    'IC5152': None,
    'IC10': 'Local Group Starburst Galaxy',
    'IC342': 'Hidden Galaxy',
    'IC1101': 'Largest Known Galaxy',
    'IC1613': None,
    'IC2574': "Coddington's Nebula",
    'IC3583': None,
    'IC4296': None,
    'IC4499': None,
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

# ---------------------------------------------------------------------------
# Runtime caches (module-level singletons)
# ---------------------------------------------------------------------------
_common_names_cache: dict = {}
_common_names_cache_loaded: bool = False

_object_types_cache: dict = {}
_object_types_cache_loaded: bool = False


# ---------------------------------------------------------------------------
# Cache persistence helpers
# ---------------------------------------------------------------------------

def load_common_names_cache() -> dict:
    """Load cached common names from file."""
    if COMMON_NAMES_CACHE_FILE.exists():
        try:
            with open(COMMON_NAMES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_common_names_cache(cache: dict) -> None:
    """Save common names cache to file."""
    try:
        COMMON_NAMES_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMON_NAMES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not save common names cache: {e}")


def load_object_types_cache() -> dict:
    """Load cached object types from file."""
    if OBJECT_TYPES_CACHE_FILE.exists():
        try:
            with open(OBJECT_TYPES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_object_types_cache(cache: dict) -> None:
    """Save object types cache to file."""
    try:
        OBJECT_TYPES_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OBJECT_TYPES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not save object types cache: {e}")


def _ensure_cache_loaded() -> None:
    """Ensure both caches are loaded into memory."""
    global _common_names_cache, _common_names_cache_loaded
    global _object_types_cache, _object_types_cache_loaded
    if not _common_names_cache_loaded:
        _common_names_cache = load_common_names_cache()
        for key, value in OBJECT_COMMON_NAMES.items():
            if value and key not in _common_names_cache:
                _common_names_cache[key] = value
        _common_names_cache_loaded = True
    if not _object_types_cache_loaded:
        _object_types_cache = load_object_types_cache()
        _object_types_cache_loaded = True


# ---------------------------------------------------------------------------
# SIMBAD query
# ---------------------------------------------------------------------------

def query_simbad_batch(object_names: list) -> tuple:
    """
    Query the SIMBAD script service for common names and object types.

    Returns (names_results, types_results) where each is a dict keyed by
    the normalised object name (upper, no spaces/hyphens).
    """
    if not object_names:
        return {}, {}

    names_results = {}
    types_results = {}

    formatted_names = []
    for name in object_names:
        name_upper = name.upper()
        if name_upper.startswith('M') and len(name_upper) > 1 and name_upper[1:].isdigit():
            formatted_names.append(f"M {name_upper[1:]}")
        elif name_upper.startswith('NGC') and len(name_upper) > 3 and name_upper[3:].isdigit():
            formatted_names.append(f"NGC {name_upper[3:]}")
        elif name_upper.startswith('IC') and len(name_upper) > 2 and name_upper[2:].isdigit():
            formatted_names.append(f"IC {name_upper[2:]}")
        else:
            formatted_names.append(name_upper)

    for obj_name in formatted_names:
        try:
            script = f'format object "%IDLIST|%OTYPE(V)"\nquery id {obj_name}'
            encoded_script = quote(script, safe='')
            url = f"http://simbad.u-strasbg.fr/simbad/sim-script?script={encoded_script}"

            req = Request(url, headers={'User-Agent': 'SeestarFITSOrganizer/1.0'})

            with urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')

            if '::data::' in content:
                data_section = content.split('::data::')[1].strip()
                normalized = obj_name.upper().replace(' ', '').replace('-', '')

                lines = [l.strip() for l in data_section.split('\n') if l.strip()]

                obj_type = None
                for line in reversed(lines):
                    if '|' in line:
                        obj_type = line.split('|')[-1].strip()
                        break

                if obj_type:
                    types_results[normalized] = obj_type
                    logger.debug(f"Found object type for {obj_name}: {obj_type}")

                common_names = []
                for line in lines:
                    if line.startswith('NAME '):
                        common_name = line[5:].strip()
                        if '|' in common_name:
                            common_name = common_name.split('|')[0].strip()
                        if common_name:
                            common_names.append(common_name)

                if common_names:
                    names_results[normalized] = common_names[0]
                    logger.debug(f"Found common name for {obj_name}: {common_names[0]}")

        except Exception as e:
            logger.debug(f"Failed to query SIMBAD for {obj_name}: {e}")
            continue

    if names_results:
        logger.info(f"Retrieved {len(names_results)} common names from SIMBAD")
    if types_results:
        logger.info(f"Retrieved {len(types_results)} object types from SIMBAD")

    return names_results, types_results


# ---------------------------------------------------------------------------
# Public lookup API
# ---------------------------------------------------------------------------

def get_common_name(object_name: str) -> str:
    """Return the common name for an astronomical object, or empty string."""
    if not object_name:
        return ''

    normalized = object_name.upper().replace(' ', '').replace('-', '')
    _ensure_cache_loaded()

    if normalized in _common_names_cache:
        name = _common_names_cache[normalized]
        return name if name else ''

    if normalized.startswith('IC'):
        base = normalized[2:]
        try:
            ic_key = f"IC{int(base)}"
            if ic_key in _common_names_cache:
                name = _common_names_cache[ic_key]
                return name if name else ''
        except ValueError:
            pass

    if normalized.startswith('NGC'):
        base = normalized[3:]
        try:
            ngc_key = f"NGC{int(base)}"
            if ngc_key in _common_names_cache:
                name = _common_names_cache[ngc_key]
                return name if name else ''
        except ValueError:
            pass

    return ''


def get_object_type(object_name: str) -> str:
    """Return the SIMBAD verbose object type, or empty string if unknown."""
    if not object_name:
        return ''
    normalized = object_name.upper().replace(' ', '').replace('-', '')
    _ensure_cache_loaded()
    return _object_types_cache.get(normalized, '')


def get_display_label(object_name: str) -> str:
    """Return the best display label: common name, then object type, then ''."""
    common = get_common_name(object_name)
    if common:
        return common
    return get_object_type(object_name)


def lookup_common_names_batch(projects: list) -> None:
    """
    Query SIMBAD for any objects not yet in either cache.

    Mutates both module-level caches and persists them to disk.
    """
    global _common_names_cache, _object_types_cache

    _ensure_cache_loaded()

    unknown_objects = set()
    for project in projects:
        for obj in project.get('objects', []):
            if obj:
                normalized = obj.upper().replace(' ', '').replace('-', '')
                name_known = normalized in _common_names_cache and _common_names_cache[normalized]
                type_known = normalized in _object_types_cache
                if not name_known and not type_known:
                    unknown_objects.add(obj)

    if not unknown_objects:
        logger.info("All object names and types found in cache, no API call needed")
        return

    logger.info(f"Querying SIMBAD for {len(unknown_objects)} unknown objects...")
    names_results, types_results = query_simbad_batch(list(unknown_objects))

    if names_results:
        _common_names_cache.update(names_results)
        save_common_names_cache(_common_names_cache)
        logger.info(f"Cached {len(names_results)} common names from SIMBAD")
    else:
        logger.warning("SIMBAD query returned no common names")

    if types_results:
        _object_types_cache.update(types_results)
        save_object_types_cache(_object_types_cache)
        logger.info(f"Cached {len(types_results)} object types from SIMBAD")
