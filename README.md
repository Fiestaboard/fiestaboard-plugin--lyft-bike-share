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
{{lyft_bikeshare.electric_bikes}}      # Electric bikes available
{{lyft_bikeshare.classic_bikes}}       # Classic bikes available
{{lyft_bikeshare.num_bikes_available}} # Total bikes
{{lyft_bikeshare.station_name}}        # Station name
{{lyft_bikeshare.is_renting}}          # "Yes" or "No"
{{lyft_bikeshare.status_color}}        # Color tile
```

### Aggregate Stats

```
{{lyft_bikeshare.total_electric}}      # Total e-bikes across all stations
{{lyft_bikeshare.total_classic}}       # Total classic bikes
{{lyft_bikeshare.total_bikes}}         # Total all bikes
{{lyft_bikeshare.station_count}}       # Number of tracked stations
```

### Best Station

```
{{lyft_bikeshare.best_station_name}}     # Name of station with most e-bikes
{{lyft_bikeshare.best_station_electric}} # E-bike count at best station
```

### Individual Stations (Array)

```
{{lyft_bikeshare.stations.0.station_name}}    # First station name
{{lyft_bikeshare.stations.0.electric_bikes}}  # First station e-bikes
{{lyft_bikeshare.stations.0.classic_bikes}}   # First station classic
{{lyft_bikeshare.stations.0.status_color}}    # First station color

{{lyft_bikeshare.stations.1.station_name}}    # Second station name
{{lyft_bikeshare.stations.1.electric_bikes}}  # Second station e-bikes
```

## Example Templates

### Single Station

```
{center}BIKE SHARE
{{lyft_bikeshare.station_name}}
Electric: {{lyft_bikeshare.electric_bikes}}
Classic: {{lyft_bikeshare.classic_bikes}}
```

### Multiple Stations

```
{center}BIKES NEARBY
{{lyft_bikeshare.stations.0.station_name}}: {{lyft_bikeshare.stations.0.electric_bikes}}E
{{lyft_bikeshare.stations.1.station_name}}: {{lyft_bikeshare.stations.1.electric_bikes}}E
{{lyft_bikeshare.stations.2.station_name}}: {{lyft_bikeshare.stations.2.electric_bikes}}E
TOTAL: {{lyft_bikeshare.total_electric}}E
```

### With Color

```
{center}BIKE SHARE
{{lyft_bikeshare.stations.0.status_color}} {{lyft_bikeshare.stations.0.station_name}}
E:{{lyft_bikeshare.stations.0.electric_bikes}} C:{{lyft_bikeshare.stations.0.classic_bikes}}
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
