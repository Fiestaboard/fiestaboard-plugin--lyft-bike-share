# Lyft Bike Share Plugin

![Lyft Bike Share Display](./docs/board-display.png)

Display Lyft bike share availability with electric and classic bike counts.

**→ [Setup Guide](./docs/SETUP.md)** - Configuration and station setup

## Overview

The Lyft Bike Share plugin fetches real-time bike availability from any Lyft-operated GBFS feed, showing electric and classic bike counts at your selected stations.

### Supported Systems

| System | City | GBFS Feed URL |
|--------|------|---------------|
| **Bay Wheels** | San Francisco Bay Area | `https://gbfs.baywheels.com/gbfs/en` |
| **CitiBike** | New York City / Jersey City | `https://gbfs.citibikenyc.com/gbfs/en` |
| **Capital Bikeshare** | Washington DC / Northern Virginia | `https://gbfs.capitalbikeshare.com/gbfs/en` |
| **Biketown** | Portland, OR | `https://gbfs.biketownpdx.com/gbfs/en` |
| **Divvy** | Chicago, IL | `https://gbfs.divvybikes.com/gbfs/en` |

## Features

- Electric and classic bike counts
- Multiple station monitoring
- Color-coded availability status
- Aggregate statistics
- No API key required!
- Works with any Lyft-operated bike share system

## Template Variables

### Primary Station (First)

```
{{lyft_bike_share.electric_bikes}}      # Electric bikes available
{{lyft_bike_share.classic_bikes}}       # Classic bikes available
{{lyft_bike_share.num_bikes_available}} # Total bikes
{{lyft_bike_share.station_name}}        # Station name
{{lyft_bike_share.is_renting}}          # "Yes" or "No"
{{lyft_bike_share.status_color}}        # Color tile
```

### Aggregate Stats

```
{{lyft_bike_share.total_electric}}      # Total e-bikes across all stations
{{lyft_bike_share.total_classic}}       # Total classic bikes
{{lyft_bike_share.total_bikes}}         # Total all bikes
{{lyft_bike_share.station_count}}       # Number of tracked stations
```

### Best Station

```
{{lyft_bike_share.best_station_name}}     # Name of station with most e-bikes
{{lyft_bike_share.best_station_electric}} # E-bike count at best station
```

### Individual Stations (Array)

```
{{lyft_bike_share.stations.0.station_name}}    # First station name
{{lyft_bike_share.stations.0.electric_bikes}}  # First station e-bikes
{{lyft_bike_share.stations.0.classic_bikes}}   # First station classic
{{lyft_bike_share.stations.0.status_color}}    # First station color

{{lyft_bike_share.stations.1.station_name}}    # Second station name
{{lyft_bike_share.stations.1.electric_bikes}}  # Second station e-bikes
```

## Example Templates

### Single Station

```
{center}BIKE SHARE
{{lyft_bike_share.station_name}}
Electric: {{lyft_bike_share.electric_bikes}}
Classic: {{lyft_bike_share.classic_bikes}}
```

### Multiple Stations

```
{center}BIKES NEARBY
{{lyft_bike_share.stations.0.station_name}}: {{lyft_bike_share.stations.0.electric_bikes}}E
{{lyft_bike_share.stations.1.station_name}}: {{lyft_bike_share.stations.1.electric_bikes}}E
{{lyft_bike_share.stations.2.station_name}}: {{lyft_bike_share.stations.2.electric_bikes}}E
TOTAL: {{lyft_bike_share.total_electric}}E
```

### With Color

```
{center}BIKE SHARE
{{lyft_bike_share.stations.0.status_color}} {{lyft_bike_share.stations.0.station_name}}
E:{{lyft_bike_share.stations.0.electric_bikes}} C:{{lyft_bike_share.stations.0.classic_bikes}}
```

## Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| enabled | boolean | false | Enable/disable the plugin |
| gbfs_base_url | string | `https://gbfs.baywheels.com/gbfs/en` | GBFS feed URL for your local system |
| station_ids | array | - | Station IDs to monitor |
| refresh_seconds | integer | 60 | Update interval |

## Choosing Stations

`station_ids` is a searchable picker in the settings form, not a field you type
GBFS IDs into. Set the **GBFS Feed URL** first, then open **Stations** and start
typing a station name — the list comes live from your system's
`station_information.json`, grouped by region, with the station code and dock
capacity shown next to each name.

- Search runs against the whole catalog upstream, so typing narrows all 600+
  Bay Wheels stations rather than just the first page.
- Pick as many stations as you like and drag them into order. Order matters:
  the first station is the one `{{lyft_bike_share.station_name}}` and the other
  single-station variables report on.
- Changing the GBFS Feed URL rebuilds the list for the new system.
- A station ID you already know can still be typed in by hand, so
  configurations written before the picker existed keep working unchanged —
  `station_ids` is still a plain array of GBFS station ID strings.

If the picker shows a hint instead of a list, the feed URL is blank or the GBFS
feed could not be reached; check the URL and try again.

## Color Indicators

- **Green**: > 5 electric bikes
- **Yellow**: 2-5 electric bikes
- **Red**: < 2 electric bikes

## Author

FiestaBoard Team
