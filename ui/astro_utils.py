"""
Astro Utilities Module

Coordinate conversion helpers and constellation lookup used across the UI.
"""

import logging

logger = logging.getLogger(__name__)


def format_duration(seconds) -> str:
    try:
        total_seconds = max(0, int(seconds or 0))
    except (ValueError, TypeError):
        total_seconds = 0
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _deg_to_hms(ra_deg: float) -> str:
    """Convert RA from decimal degrees to HH:MM:SS.ss format."""
    if ra_deg is None:
        return 'N/A'
    try:
        ra_hours = ra_deg / 15.0
        hours = int(ra_hours)
        minutes_float = (ra_hours - hours) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"
    except (ValueError, TypeError):
        return str(ra_deg)


def _deg_to_dms(dec_deg: float) -> str:
    """Convert DEC from decimal degrees to ±DD:MM:SS.ss format."""
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


def format_ra_dec(ra, dec, format_type: str = 'degrees') -> tuple:
    """Format RA and DEC values according to the specified format.

    Args:
        ra: Right Ascension (decimal degrees string or float, or None)
        dec: Declination (decimal degrees string or float, or None)
        format_type: 'degrees' or 'hms'

    Returns:
        (ra_str, dec_str) tuple
    """
    if ra is None or dec is None:
        return 'N/A', 'N/A'

    try:
        ra_float = float(ra)
        dec_float = float(dec)
    except (ValueError, TypeError):
        return str(ra), str(dec)

    if format_type == 'hms':
        return _deg_to_hms(ra_float), _deg_to_dms(dec_float)

    return f"{ra_float:.4f}°", f"{dec_float:.4f}°"


def get_constellation(ra, dec) -> str:
    """Return the constellation name for given RA/DEC (decimal degrees).

    Returns 'Unknown' if coordinates are missing or astropy is unavailable.
    """
    try:
        ra_float = float(ra) if ra is not None else None
        dec_float = float(dec) if dec is not None else None

        if ra_float is None or dec_float is None:
            return 'Unknown'

        from astropy.coordinates import SkyCoord
        import astropy.units as u

        coord = SkyCoord(ra=ra_float * u.degree, dec=dec_float * u.degree, frame='icrs')
        return coord.get_constellation()
    except Exception as e:
        logger.debug(f"Could not determine constellation: {e}")
        return 'Unknown'
