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

## Finding Station IDs

Use the station search feature in the UI to find stations near you by address or coordinates.

## Color Indicators

- **Green**: > 5 electric bikes
- **Yellow**: 2-5 electric bikes
- **Red**: < 2 electric bikes

## Author

FiestaBoard Team
