"""Tests for the Lyft Bike Share ``stations`` remote-options provider.

The plugin declares ``"ui:widget": "remote-options"`` on ``station_ids`` so the
settings form can offer a searchable station picker instead of asking the user
to hand-type opaque GBFS station IDs.
"""

import json
from pathlib import Path

import pytest
import requests
from unittest.mock import Mock, patch

from src.plugins.base import OptionsRequest, OptionsUnavailable


STATION_INFORMATION_URL = "https://gbfs.baywheels.com/gbfs/en/station_information.json"
SYSTEM_REGIONS_URL = "https://gbfs.baywheels.com/gbfs/en/system_regions.json"

CATALOG = {
    "data": {
        "stations": [
            {
                "station_id": "sf-1",
                "name": "Market St at 10th St",
                "short_name": "SF-G30",
                "region_id": "3",
                "capacity": 27,
                "lat": 37.77,
                "lon": -122.41,
            },
            {
                "station_id": "oak-2",
                "name": "Broadway at 14th St",
                "short_name": "OK-L4",
                "region_id": "12",
                "capacity": 15,
                "lat": 37.80,
                "lon": -122.27,
            },
            {
                "station_id": "sj-3",
                "name": "Kerley Dr at Rosemary St",
                "short_name": "SJ-F10",
                "region_id": "5",
                "capacity": 11,
                "lat": 37.36,
                "lon": -121.90,
            },
        ]
    }
}

REGIONS = {
    "data": {
        "regions": [
            {"region_id": "3", "name": "San Francisco"},
            {"region_id": "5", "name": "San Jose"},
            {"region_id": "12", "name": "Oakland"},
        ]
    }
}


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.json"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text())


def _feed(station_information=None, system_regions=None):
    """Return a ``requests.get`` side effect serving the two GBFS endpoints."""
    payloads = {
        STATION_INFORMATION_URL: CATALOG if station_information is None else station_information,
        SYSTEM_REGIONS_URL: REGIONS if system_regions is None else system_regions,
    }

    def _get(url, **kwargs):
        if url not in payloads:
            raise AssertionError(f"Unexpected URL fetched: {url}")
        response = Mock()
        response.json.return_value = payloads[url]
        response.raise_for_status.return_value = None
        return response

    return _get


@pytest.fixture(autouse=True)
def clear_module_caches():
    """Module-level GBFS caches must not leak between tests."""
    import plugins.lyft_bike_share as module

    for name in ("_station_info_cache", "_station_info_cache_time", "_region_name_cache", "_region_name_cache_time"):
        setattr(module, name, {})
    yield
    for name in ("_station_info_cache", "_station_info_cache_time", "_region_name_cache", "_region_name_cache_time"):
        setattr(module, name, {})


@pytest.fixture
def plugin():
    from plugins.lyft_bike_share import LyftBikeSharePlugin

    manifest = {"id": "lyft_bike_share", "name": "Lyft Bike Share", "version": "2.1.0"}
    instance = LyftBikeSharePlugin(manifest)
    instance._config = {"gbfs_base_url": "https://gbfs.baywheels.com/gbfs/en"}
    return instance


class TestStationsProvider:
    """The ``stations`` provider browses the whole GBFS catalog."""

    def test_returns_whole_catalog_not_just_configured_stations(self, plugin):
        # The user has already picked one station; the picker must still offer
        # every station in the system so they can pick a different one.
        plugin._config["station_ids"] = ["sj-3"]

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        values = [option.value for option in result.options]
        assert values == ["sf-1", "oak-2", "sj-3"]

    def test_label_is_the_station_name(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert [option.label for option in result.options] == [
            "Market St at 10th St",
            "Broadway at 14th St",
            "Kerley Dr at Rosemary St",
        ]

    def test_preview_shows_dock_capacity(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert [option.preview for option in result.options] == ["27 docks", "15 docks", "11 docks"]

    def test_description_names_the_region_and_the_station_code(self, plugin):
        # 636 Bay Wheels stations share a namespace across five cities, so the
        # region is what tells "Broadway at 14th" in Oakland from any other.
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert [option.description for option in result.options] == [
            "San Francisco · SF-G30",
            "Oakland · OK-L4",
            "San Jose · SJ-F10",
        ]

    def test_options_are_grouped_by_region(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert [option.group for option in result.options] == ["San Francisco", "Oakland", "San Jose"]


class TestStationsProviderDegradesGracefully:
    """Optional feed data must never take the picker down with it."""

    def test_unreachable_region_feed_still_yields_stations(self, plugin):
        def _get(url, **kwargs):
            if url.endswith("system_regions.json"):
                raise requests.Timeout("regions timed out")
            return _feed()(url, **kwargs)

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_get):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert [option.value for option in result.options] == ["sf-1", "oak-2", "sj-3"]
        assert [option.group for option in result.options] == [None, None, None]
        assert result.options[0].description == "SF-G30"

    def test_street_address_is_preferred_over_the_station_code(self, plugin):
        catalog = {
            "data": {
                "stations": [
                    {
                        "station_id": "sf-1",
                        "name": "Market St at 10th St",
                        "short_name": "SF-G30",
                        "address": "1096 Market St",
                        "region_id": "3",
                        "capacity": 27,
                    }
                ]
            }
        }

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed(station_information=catalog)):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert result.options[0].description == "San Francisco · 1096 Market St"

    def test_station_without_capacity_has_no_preview(self, plugin):
        catalog = {"data": {"stations": [{"station_id": "sf-1", "name": "Market St at 10th St"}]}}

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed(station_information=catalog)):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        assert result.options[0].preview is None
        assert result.options[0].description is None


class TestOptionsRunsInAThrowawaySandbox:
    """Core dispatches options on a throwaway instance with the stored config applied."""

    def test_reads_the_configured_systems_station_information_feed(self, plugin):
        plugin._config["gbfs_base_url"] = "https://gbfs.citibikenyc.com/gbfs/en/"
        calls = []

        def _get(url, **kwargs):
            calls.append(url)
            payload = CATALOG if url.endswith("station_information.json") else REGIONS
            response = Mock()
            response.json.return_value = payload
            response.raise_for_status.return_value = None
            return response

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_get):
            plugin.get_options(OptionsRequest(options_id="stations"))

        assert "https://gbfs.citibikenyc.com/gbfs/en/station_information.json" in calls

    def test_does_not_prime_the_plugins_board_data_cache(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            plugin.get_options(OptionsRequest(options_id="stations"))

        assert plugin._cache is None

    def test_does_not_write_back_to_the_stored_config(self, plugin):
        before = json.loads(json.dumps(plugin.config))

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            plugin.get_options(OptionsRequest(options_id="stations"))

        assert plugin.config == before

    def test_a_second_throwaway_instance_answers_from_the_module_cache(self, plugin):
        from plugins.lyft_bike_share import LyftBikeSharePlugin

        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()) as mock_get:
            plugin.get_options(OptionsRequest(options_id="stations"))
            first_call_count = mock_get.call_count

            sandbox = LyftBikeSharePlugin({"id": "lyft_bike_share", "name": "Lyft Bike Share", "version": "2.1.0"})
            sandbox._config = dict(plugin.config)
            result = sandbox.get_options(OptionsRequest(options_id="stations"))

            assert mock_get.call_count == first_call_count
        assert [option.value for option in result.options] == ["sf-1", "oak-2", "sj-3"]


class TestManifestDeclaresThePicker:
    """The manifest must ask core for the picker in the grammar core accepts."""

    def test_station_ids_uses_the_generic_remote_options_widget(self):
        schema = _manifest()["settings_schema"]["properties"]["station_ids"]

        assert schema["ui:widget"] == "remote-options"

    def test_no_field_still_asks_for_the_widget_core_never_implemented(self):
        assert "lyft-bikeshare-station-picker" not in MANIFEST_PATH.read_text()

    def test_ui_options_points_at_the_stations_provider(self):
        ui_options = _manifest()["settings_schema"]["properties"]["station_ids"]["ui:options"]

        assert ui_options["options_id"] == "stations"
        assert ui_options["multiple"] is True

    def test_ui_options_asks_for_server_side_search(self):
        # A 636-station catalog is only usable if typing narrows it upstream.
        ui_options = _manifest()["settings_schema"]["properties"]["station_ids"]["ui:options"]

        assert ui_options["server_search"] is True

    def test_ui_options_rebuilds_the_catalog_when_the_feed_url_changes(self):
        ui_options = _manifest()["settings_schema"]["properties"]["station_ids"]["ui:options"]

        assert ui_options["depends_on"] == ["gbfs_base_url"]

    def test_ui_annotations_pass_cores_validator(self):
        from src.plugins.manifest import validate_settings_schema_ui

        assert validate_settings_schema_ui(_manifest()["settings_schema"]) == []

    def test_core_dispatches_the_stations_provider_from_the_manifest(self):
        from src.plugins.manifest import collect_options_ids

        assert collect_options_ids(_manifest()["settings_schema"]) == {"stations"}

    def test_whole_manifest_still_validates(self):
        from src.plugins.manifest import validate_manifest

        is_valid, errors = validate_manifest(_manifest())
        assert is_valid, errors

    def test_fiestaboard_version_floor_is_the_release_that_accepts_the_full_grammar(self):
        # 8.24.2 shipped the ui:options keys used above (searchable,
        # server_search, reorderable, allow_custom, placeholder). Older cores
        # reject them, and load_manifest() returns None on any validation
        # error -- so an older core drops the plugin entirely.
        assert _manifest()["fiestaboard_version"] == ">=8.24.2"


class TestPersistedShapeIsUnchanged:
    """Users already have station IDs stored; the picker must write the same shape."""

    STORED_CONFIG = {
        "enabled": True,
        "gbfs_base_url": "https://gbfs.baywheels.com/gbfs/en",
        "station_ids": ["sj-3", "sf-1"],
        "refresh_seconds": 60,
    }

    def test_existing_stored_config_still_validates(self, plugin):
        assert plugin.validate_config(dict(self.STORED_CONFIG)) == []

    def test_existing_stored_config_round_trips_through_json_unchanged(self, plugin):
        plugin._config = json.loads(json.dumps(self.STORED_CONFIG))

        assert plugin.config["station_ids"] == ["sj-3", "sf-1"]
        assert json.loads(json.dumps(plugin.config)) == self.STORED_CONFIG

    def test_picking_from_the_catalog_writes_the_same_shape_as_the_stored_ids(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations"))

        by_value = {option.value: option for option in result.options}
        picked = [value for value in ["sj-3", "sf-1"] if value in by_value]

        assert all(isinstance(option.value, str) for option in result.options)
        assert picked == self.STORED_CONFIG["station_ids"]

    def test_station_ids_stays_an_array_of_plain_strings_in_the_manifest(self):
        schema = _manifest()["settings_schema"]["properties"]["station_ids"]

        assert schema["type"] == "array"
        assert schema["items"] == {"type": "string"}

    def test_stored_ids_still_drive_fetch_data(self, plugin):
        plugin._config = json.loads(json.dumps(self.STORED_CONFIG))
        status = {
            "data": {
                "stations": [
                    {"station_id": "sj-3", "num_bikes_available": 4, "num_ebikes_available": 3, "is_renting": 1},
                    {"station_id": "sf-1", "num_bikes_available": 9, "num_ebikes_available": 6, "is_renting": 1},
                ]
            }
        }
        response = Mock()
        response.json.return_value = status
        response.raise_for_status.return_value = None

        with patch("plugins.lyft_bike_share.requests.get", return_value=response), patch.object(
            plugin, "_get_station_information", return_value={"sj-3": {"name": "Kerley Dr at Rosemary St"}}
        ):
            result = plugin.fetch_data()

        assert result.available
        assert result.data["station_count"] == 2
        assert result.data["station_name"] == "Kerley Dr at Rosemary St"


class TestOptionsFailureModes:
    """Setup-time failures are hints, not stack traces."""

    def test_unreachable_feed_raises_options_unavailable(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=requests.ConnectionError("no route")):
            with pytest.raises(OptionsUnavailable) as excinfo:
                plugin.get_options(OptionsRequest(options_id="stations"))

        assert "gbfs.baywheels.com" in str(excinfo.value)

    def test_feed_with_no_stations_raises_options_unavailable(self, plugin):
        with patch(
            "plugins.lyft_bike_share.requests.get",
            side_effect=_feed(station_information={"data": {"stations": []}}),
        ):
            with pytest.raises(OptionsUnavailable):
                plugin.get_options(OptionsRequest(options_id="stations"))

    def test_blank_feed_url_raises_options_unavailable(self, plugin):
        plugin._config["gbfs_base_url"] = "   "

        with patch("plugins.lyft_bike_share.requests.get") as mock_get:
            with pytest.raises(OptionsUnavailable) as excinfo:
                plugin.get_options(OptionsRequest(options_id="stations"))

        mock_get.assert_not_called()
        assert "GBFS" in str(excinfo.value)

    def test_a_query_that_matches_nothing_is_an_empty_result_not_an_error(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", query="nowhere at all"))

        assert result.options == []
        assert result.total == 0

    def test_unknown_options_id_raises_not_implemented_error(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            with pytest.raises(NotImplementedError) as excinfo:
                plugin.get_options(OptionsRequest(options_id="regions"))

        assert "regions" in str(excinfo.value)


class TestStationsSearch:
    """``request.query`` narrows the catalog server-side."""

    def test_query_matches_station_name_case_insensitively(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", query="BROADWAY"))

        assert [option.value for option in result.options] == ["oak-2"]

    def test_query_matches_a_substring_anywhere_in_the_name(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", query="at 1"))

        assert [option.value for option in result.options] == ["sf-1", "oak-2"]

    def test_total_counts_only_the_matching_stations(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", query="broadway"))

        assert result.total == 1
        assert result.has_more is False


class TestStationsPaging:
    """``request.limit`` caps the page; ``has_more``/``total``/``cursor`` describe the rest."""

    def test_limit_caps_the_page(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", limit=2))

        assert [option.value for option in result.options] == ["sf-1", "oak-2"]

    def test_limited_page_flags_more_and_still_totals_the_catalog(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", limit=2))

        assert result.has_more is True
        assert result.total == 3

    def test_a_page_that_fits_flags_no_more(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", limit=3))

        assert result.has_more is False
        assert result.cursor is None

    def test_cursor_continues_where_the_previous_page_stopped(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            first = plugin.get_options(OptionsRequest(options_id="stations", limit=2))
            second = plugin.get_options(
                OptionsRequest(options_id="stations", limit=2, cursor=first.cursor)
            )

        assert first.cursor is not None
        assert [option.value for option in second.options] == ["sj-3"]
        assert second.has_more is False

    def test_unusable_cursor_restarts_at_the_first_station(self, plugin):
        with patch("plugins.lyft_bike_share.requests.get", side_effect=_feed()):
            result = plugin.get_options(OptionsRequest(options_id="stations", cursor="not-a-number"))

        assert [option.value for option in result.options] == ["sf-1", "oak-2", "sj-3"]
