"""Unit tests for ProjectAnalyzer raw-frame filtering."""

import numpy as np
import pytest
from astropy.io import fits

from core.project_analyzer import ProjectAnalyzer, is_raw_seestar_frame


class TestIsRawSeestarFrame:
    """The filename filter that separates raw subs from processed outputs."""

    def test_accepts_raw_light_frame(self):
        assert is_raw_seestar_frame("Light_M 51_10.0s_IRCUT_20260510-212700.fit")

    def test_accepts_calibration_frames(self):
        assert is_raw_seestar_frame("Dark_10.0s_20260510-212700.fit")
        assert is_raw_seestar_frame("Flat_IRCUT_20260510.fit")
        assert is_raw_seestar_frame("Bias_20260510.fits")

    def test_is_case_insensitive(self):
        assert is_raw_seestar_frame("light_m51.fit")
        assert is_raw_seestar_frame("LIGHT_M51.FIT")

    def test_rejects_stacked_master(self):
        assert not is_raw_seestar_frame("M_51_1106x30sec_T16degC_2026-06-06.fit")

    def test_rejects_star_layer(self):
        assert not is_raw_seestar_frame("stars_M_51_1106x30sec_T16degC_2026-06-06.fit")

    def test_rejects_non_fits(self):
        assert not is_raw_seestar_frame("Light_M51.jpg")


def _write_light(path, exptime=10.0, obj="M 51"):
    """Write a minimal FITS light frame to path."""
    hdu = fits.PrimaryHDU(np.zeros((4, 4), dtype=np.uint16))
    hdu.header['EXPTIME'] = exptime
    hdu.header['OBJECT'] = obj
    hdu.header['IMAGETYP'] = 'LIGHT'
    hdu.header['DATE-OBS'] = '2026-05-10T21:27:00'
    hdu.writeto(path, overwrite=True)


class TestAnalyzeProjectSkipsProcessed:
    """analyze_project must ignore processed/stacked FITS outputs."""

    def test_processed_files_are_not_counted(self, temp_dir):
        project = temp_dir / "M 51_Project"
        lights = project / "Lights"
        processed = project / "Processed July"
        lights.mkdir(parents=True)
        processed.mkdir(parents=True)

        # 3 raw light subs
        for i in range(3):
            _write_light(lights / f"Light_M 51_10.0s_IRCUT_2026051{i}-212700.fit")

        # Processed outputs that should be ignored
        _write_light(processed / "M_51_1106x30sec_T16degC_2026-06-06.fit", exptime=33180.0)
        _write_light(processed / "stars_M_51_1106x30sec_T16degC_2026-06-06.fit", exptime=33180.0)

        analyzer = ProjectAnalyzer(temp_dir, session_gap_hours=2.0)
        analysis = analyzer.analyze_project(project)

        assert analysis.lights == 3
        assert analysis.total_files == 3
        assert analysis.integration_seconds == 30.0

    def test_works_without_light_subfolder(self, temp_dir):
        """Users who dump raw subs directly in the project folder still work."""
        project = temp_dir / "M 51_Project"
        project.mkdir(parents=True)

        for i in range(2):
            _write_light(project / f"Light_M 51_10.0s_IRCUT_2026051{i}-212700.fit")
        _write_light(project / "stars_M_51_stacked.fit", exptime=99999.0)

        analyzer = ProjectAnalyzer(temp_dir, session_gap_hours=2.0)
        analysis = analyzer.analyze_project(project)

        assert analysis.lights == 2
        assert analysis.total_files == 2
        assert analysis.integration_seconds == 20.0
