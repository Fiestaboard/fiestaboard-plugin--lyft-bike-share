"""Lyft Bike Share plugin for FiestaBoard.

Displays bike share availability from any Lyft-operated GBFS feed.
Supports Bay Wheels (SF), CitiBike (NYC), Capital Bikeshare (DC),
Biketown (Portland), Divvy (Chicago), and other Lyft bike share systems.
"""

from typing import Any, Dict, List, Optional
import logging
import requests
import time

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

DEFAULT_GBFS_BASE_URL = "https://gbfs.baywheels.com/gbfs/en"

# Cache for station information (keyed by base URL)
_station_info_cache: Dict[str, Dict] = {}
_station_info_cache_time: Dict[str, float] = {}
STATION_INFO_CACHE_TTL = 24 * 60 * 60


class LyftBikeSharePlugin(PluginBase):
    """Lyft Bike Share plugin.

    Fetches bike availability from any Lyft-operated GBFS feed.
    Supports Bay Wheels, CitiBike, Capital Bikeshare, Biketown, Divvy, and more.
    """

    def __init__(self, manifest: Dict[str, Any]):
        """Initialize the Lyft Bike Share plugin."""
        super().__init__(manifest)
        self._cache: Optional[Dict[str, Any]] = None

    @property
    def plugin_id(self) -> str:
        return "lyft_bike_share"

    def _gbfs_base_url(self) -> str:
        """Return the configured GBFS base URL."""
        return self.config.get("gbfs_base_url", DEFAULT_GBFS_BASE_URL).rstrip("/")

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate Lyft Bike Share configuration."""
        errors = []

        station_ids = config.get("station_ids", [])
        if not station_ids:
            errors.append("At least one station ID is required")

        return errors

    def _get_station_information(self) -> Optional[Dict]:
        """Fetch and cache station information for the configured GBFS feed."""
        global _station_info_cache, _station_info_cache_time

        base_url = self._gbfs_base_url()
        station_information_url = f"{base_url}/station_information.json"
        current_time = time.time()

        cached = _station_info_cache.get(base_url)
        cached_time = _station_info_cache_time.get(base_url, 0)
        if cached and (current_time - cached_time) < STATION_INFO_CACHE_TTL:
            return cached

        try:
            response = requests.get(station_information_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            stations = data.get("data", {}).get("stations", [])
            station_map = {}
            for station in stations:
                station_id = station.get("station_id")
                if station_id:
                    station_map[station_id] = {
                        "station_id": station_id,
                        "name": station.get("name", station_id),
                        "lat": station.get("lat"),
                        "lon": station.get("lon"),
                    }

            _station_info_cache[base_url] = station_map
            _station_info_cache_time[base_url] = current_time
            return station_map

        except Exception as e:
            logger.error(f"Failed to fetch station information: {e}")
            return _station_info_cache.get(base_url)

    def _get_status_color(self, electric_bikes: int) -> str:
        """Get color based on electric bike count."""
        if electric_bikes < 2:
            return "{63}"  # red
        elif electric_bikes > 5:
            return "{66}"  # green
        else:
            return "{65}"  # yellow

    def fetch_data(self) -> PluginResult:
        """Fetch Lyft Bike Share station data."""
        station_ids = self.config.get("station_ids", [])
        if not station_ids:
            return PluginResult(
                available=False,
                error="No station IDs configured"
            )

        base_url = self._gbfs_base_url()
        station_status_url = f"{base_url}/station_status.json"

        try:
            response = requests.get(station_status_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            stations_map = {}
            for station in data.get("data", {}).get("stations", []):
                station_id = station.get("station_id")
                if station_id:
                    stations_map[station_id] = station

            station_info = self._get_station_information() or {}
            stations_data = []

            for station_id in station_ids:
                if station_id not in stations_map:
                    continue

                station = stations_map[station_id]
                num_bikes = station.get("num_bikes_available", 0)

                # Get electric bikes
                electric_bikes = station.get("num_ebikes_available", 0)
                classic_bikes = num_bikes - electric_bikes

                # Get station name
                station_name = station_id
                if station_id in station_info:
                    station_name = station_info[station_id].get("name", station_id)

                # Truncate name for display
                if len(station_name) > 10:
                    station_name = station_name[:10]

                stations_data.append({
                    "station_id": station_id,
                    "station_name": station_name,
                    "num_bikes_available": num_bikes,
                    "electric_bikes": electric_bikes,
                    "classic_bikes": classic_bikes,
                    "is_renting": "Yes" if station.get("is_renting", 1) == 1 else "No",
                    "status_color": self._get_status_color(electric_bikes),
                })

            if not stations_data:
                return PluginResult(
                    available=False,
                    error="No valid stations found"
                )

            # Calculate aggregates
            total_electric = sum(s["electric_bikes"] for s in stations_data)
            total_classic = sum(s["classic_bikes"] for s in stations_data)
            total_bikes = sum(s["num_bikes_available"] for s in stations_data)

            # Find best station
            best = max(stations_data, key=lambda s: s["electric_bikes"])

            # Primary station data (first one)
            primary = stations_data[0]

            result_data = {
                # Primary station
                "electric_bikes": primary["electric_bikes"],
                "classic_bikes": primary["classic_bikes"],
                "num_bikes_available": primary["num_bikes_available"],
                "is_renting": primary["is_renting"],
                "station_name": primary["station_name"],
                "status_color": primary["status_color"],
                # Aggregates
                "total_electric": total_electric,
                "total_classic": total_classic,
                "total_bikes": total_bikes,
                "station_count": len(stations_data),
                # Best station
                "best_station_name": best["station_name"],
                "best_station_electric": best["electric_bikes"],
                "best_station_id": best["station_id"],
                # Array
                "stations": stations_data,
            }

            self._cache = result_data
            return PluginResult(available=True, data=result_data)

        except Exception as e:
            logger.exception("Error fetching Lyft Bike Share data")
            return PluginResult(available=False, error=str(e))

    def get_formatted_display(self) -> Optional[List[str]]:
        """Return default formatted display."""
        if not self._cache:
            result = self.fetch_data()
            if not result.available:
                return None

        data = self._cache
        if not data:
            return None

        stations = data.get("stations", [])
        lines = ["BIKE SHARE".center(22), ""]

        for station in stations[:4]:
            line = f"{station['station_name']}: {station['electric_bikes']}E {station['classic_bikes']}C"
            lines.append(line[:22])

        while len(lines) < 6:
            lines.append("")

        return lines[:6]


# Export the plugin class
Plugin = LyftBikeSharePlugin

