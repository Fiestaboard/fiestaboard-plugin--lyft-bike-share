"""Board-geometry conformance for the Lyft Bike Share plugin.

Station names come from the GBFS feed and are shown in full (see
``TestConfiguredStations``/``test_fetch_data_long_station_name`` in
``test_plugin.py``), so this suite configures 30 stations with names of
varying length -- some short, some longer than a Flagship row -- to prove
``get_formatted_display`` reflows rather than truncates: full names on a wide
board, deliberately abbreviated ones on a Note, and more stations listed as
the board grows taller.

``requests.get`` is stubbed for the module's own URL, dispatching on the
feed base URL so both ``station_status.json`` and ``station_information.json``
resolve without touching the network.

``strict_growth=True``: this plugin renders a list of stations, so a taller
board (at fixed width) must show strictly more of them once a shorter board
was full.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.plugins.geometry_conformance import assert_board_conformance

import plugins.lyft_bike_share as lyft_module
from plugins.lyft_bike_share import LyftBikeSharePlugin

MANIFEST = json.loads((Path(__file__).parent.parent / "manifest.json").read_text())

BASE_URL = "https://gbfs.baywheels.com/gbfs/en"

# 30 stations -- enough to saturate every geometry in the standard matrix and
# the growth ladder (the tallest is a 24-row max array, which needs at most
# 22 station rows once the header and spacer are subtracted). Names vary in
# length, including several longer than a Flagship row (22 tiles), so a wide
# board exercises "show the full name" and a narrow one exercises "abbreviate
# deliberately".
STATION_IDS = [f"station-{i}" for i in range(30)]

STATION_NAMES = [
    "Market St at 10th St",
    "Embarcadero at Folsom",
    "Powell St BART Station",
    "Ferry Building",
    "Steuart St at Market St",
    "Duboce Ave at Noe St",
    "The Embarcadero at Sansome St",
    "18th St at Noe St",
    "Union Square (Powell St at Post St)",
    "Grove St",
]


def _station_name(index: int) -> str:
    return f"{STATION_NAMES[index % len(STATION_NAMES)]} #{index}"


def _fake_get(url: str, timeout: int = 10):
    """Stand in for ``requests.get`` against the two GBFS endpoints used."""
    response = Mock()
    response.raise_for_status.return_value = None

    if url == f"{BASE_URL}/station_status.json":
        response.json.return_value = {
            "data": {
                "stations": [
                    {
                        "station_id": station_id,
                        "num_bikes_available": 8,
                        "num_ebikes_available": 5,
                        "is_renting": 1,
                    }
                    for station_id in STATION_IDS
                ]
            }
        }
        return response

    if url == f"{BASE_URL}/station_information.json":
        response.json.return_value = {
            "data": {
                "stations": [
                    {
                        "station_id": station_id,
                        "name": _station_name(i),
                        "lat": 37.77,
                        "lon": -122.41,
                    }
                    for i, station_id in enumerate(STATION_IDS)
                ]
            }
        }
        return response

    raise AssertionError(f"unexpected GBFS URL in conformance test: {url}")


def make_plugin() -> LyftBikeSharePlugin:
    """Fresh, ready-to-render plugin with the GBFS network stubbed.

    Clears the plugin's module-level station/region caches first: they are
    keyed by base URL and shared across every instance and test in the
    process, so a stale entry from another test would otherwise leak in here.
    """
    lyft_module._station_info_cache.clear()
    lyft_module._station_info_cache_time.clear()
    lyft_module._region_name_cache.clear()
    lyft_module._region_name_cache_time.clear()

    plugin = LyftBikeSharePlugin(MANIFEST)
    plugin.config = {"gbfs_base_url": BASE_URL, "station_ids": STATION_IDS}
    return plugin


def test_renders_on_every_board_shape():
    with patch("plugins.lyft_bike_share.requests.get", side_effect=_fake_get):
        assert_board_conformance(
            make_plugin,
            manifest=MANIFEST,
            strict_growth=True,  # renders a list of stations
            require_note_array_preview=True,
        )
