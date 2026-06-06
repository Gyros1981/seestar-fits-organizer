"""
Seestar FITS Organizer - Main Entry Point

A desktop application for organizing and analyzing astrophotography data
from Seestar telescopes. Provides tools for:
- Scanning and building projects from raw FITS data
- Analyzing existing projects with detailed statistics
- Managing location tags for capture sites
- Exporting analysis data to CSV

Usage:
    python main.py
"""

import logging

from core import setup_logging
from ui.main_window import SeestarApp


def main():
    """Main entry point."""
    # Configure root logger using centralized setup
    setup_logging(level=logging.INFO)
    
    app = SeestarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
