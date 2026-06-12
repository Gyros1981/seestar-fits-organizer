"""Unit tests for UI filedialog starting directories."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from ui.main_window import SeestarApp
from ui.settings_window import SettingsWindow
from ui.analysis_window import AnalysisWindow


class TestUIDialogs:
    """Test cases for UI dialog initialdir logic."""

    @pytest.mark.parametrize(
        "method_name, dir_attr, setting_setter",
        [
            ("select_seestar_dir", "seestar_dir", "set_seestar_dir"),
            ("select_raw_dir", "raw_dir", "set_raw_dir"),
            ("select_projects_dir", "projects_dir", "set_projects_dir"),
            ("select_analyze_projects_dir", "analyze_projects_dir", "set_projects_dir"),
            ("select_ps_source_dir", "ps_source_dir", None),
            ("select_ps_target_dir", "ps_target_dir", None),
        ]
    )
    def test_main_window_dirs_default_to_home(self, method_name, dir_attr, setting_setter):
        """Test that directory selection dialogs default to home directory if field is not set."""
        # Create a mock self for SeestarApp
        self_mock = MagicMock(spec=SeestarApp)
        setattr(self_mock, dir_attr, None)
        self_mock.settings = MagicMock()

        # Mock labels to avoid configure errors
        label_attr = dir_attr.replace("_dir", "_path_label")
        setattr(self_mock, label_attr, MagicMock())

        with patch("ui.main_window.filedialog.askdirectory") as mock_askdirectory:
            mock_askdirectory.return_value = ""

            # Call the method on our mock self
            method = getattr(SeestarApp, method_name)
            method(self_mock)

            # Verify askdirectory was called with initialdir set to user's home directory
            mock_askdirectory.assert_called_once()
            kwargs = mock_askdirectory.call_args[1]
            assert kwargs["initialdir"] == str(Path.home())

    @pytest.mark.parametrize(
        "method_name, dir_attr, setting_setter",
        [
            ("select_seestar_dir", "seestar_dir", "set_seestar_dir"),
            ("select_raw_dir", "raw_dir", "set_raw_dir"),
            ("select_projects_dir", "projects_dir", "set_projects_dir"),
            ("select_analyze_projects_dir", "analyze_projects_dir", "set_projects_dir"),
            ("select_ps_source_dir", "ps_source_dir", None),
            ("select_ps_target_dir", "ps_target_dir", None),
        ]
    )
    def test_main_window_dirs_use_existing(self, temp_dir, method_name, dir_attr, setting_setter):
        """Test that directory selection dialogs start in the existing directory if set."""
        self_mock = MagicMock(spec=SeestarApp)
        setattr(self_mock, dir_attr, temp_dir)
        self_mock.settings = MagicMock()

        # Mock labels
        label_attr = dir_attr.replace("_dir", "_path_label")
        setattr(self_mock, label_attr, MagicMock())

        with patch("ui.main_window.filedialog.askdirectory") as mock_askdirectory:
            mock_askdirectory.return_value = str(temp_dir)

            method = getattr(SeestarApp, method_name)
            method(self_mock)

            mock_askdirectory.assert_called_once()
            kwargs = mock_askdirectory.call_args[1]
            assert kwargs["initialdir"] == str(temp_dir)

    def test_browse_fits_directory_default_to_home(self):
        """Test browse_fits_directory defaults to user's home directory when current_fits_directory is not set."""
        self_mock = MagicMock(spec=SeestarApp)
        self_mock.current_fits_directory = None

        with patch("ui.main_window.filedialog.askdirectory") as mock_askdirectory:
            mock_askdirectory.return_value = ""

            SeestarApp.browse_fits_directory(self_mock)

            mock_askdirectory.assert_called_once()
            kwargs = mock_askdirectory.call_args[1]
            assert kwargs["initialdir"] == str(Path.home())

    def test_browse_fits_directory_use_existing(self, temp_dir):
        """Test browse_fits_directory starts in current_fits_directory if set and exists."""
        self_mock = MagicMock(spec=SeestarApp)
        self_mock.current_fits_directory = str(temp_dir)

        with patch("ui.main_window.filedialog.askdirectory") as mock_askdirectory:
            mock_askdirectory.return_value = ""

            SeestarApp.browse_fits_directory(self_mock)

            mock_askdirectory.assert_called_once()
            kwargs = mock_askdirectory.call_args[1]
            assert kwargs["initialdir"] == str(temp_dir)

    def test_settings_window_import_tags(self):
        """Test import_tags in SettingsWindow starts in user's home directory."""
        self_mock = MagicMock(spec=SettingsWindow)
        self_mock.location_tags = MagicMock()

        with patch("ui.settings_window.filedialog.askopenfilename") as mock_askopenfilename:
            mock_askopenfilename.return_value = ""

            SettingsWindow.import_tags(self_mock)

            mock_askopenfilename.assert_called_once()
            kwargs = mock_askopenfilename.call_args[1]
            assert kwargs["initialdir"] == str(Path.home())

    def test_settings_window_export_tags(self):
        """Test export_tags in SettingsWindow starts in user's home directory."""
        self_mock = MagicMock(spec=SettingsWindow)
        self_mock.location_tags = MagicMock()

        with patch("ui.settings_window.filedialog.asksaveasfilename") as mock_asksaveasfilename:
            mock_asksaveasfilename.return_value = ""

            SettingsWindow.export_tags(self_mock)

            mock_asksaveasfilename.assert_called_once()
            kwargs = mock_asksaveasfilename.call_args[1]
            assert kwargs["initialdir"] == str(Path.home())

    def test_analysis_window_export_to_csv(self):
        """Test export_to_csv in AnalysisWindow starts in user's home directory."""
        self_mock = MagicMock(spec=AnalysisWindow)

        with patch("ui.analysis_window.filedialog.asksaveasfilename") as mock_asksaveasfilename:
            mock_asksaveasfilename.return_value = ""

            AnalysisWindow.export_to_csv(self_mock)

            mock_asksaveasfilename.assert_called_once()
            kwargs = mock_asksaveasfilename.call_args[1]
            assert kwargs["initialdir"] == str(Path.home())
