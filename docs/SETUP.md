# Lyft Bike Share Setup Guide

The Lyft Bike Share plugin lets you track real-time bike availability at stations on any Lyft-operated bike share system. A searchable station picker, fed live from your system's GBFS feed, makes it easy to find and monitor the stations you care about.

## Supported Systems

This plugin works with all Lyft-operated bike share systems:

| System | City / Region | GBFS Feed URL |
|--------|---------------|---------------|
| **Bay Wheels** | San Francisco Bay Area | `https://gbfs.baywheels.com/gbfs/en` |
| **CitiBike** | New York City / Jersey City | `https://gbfs.citibikenyc.com/gbfs/en` |
| **Capital Bikeshare** | Washington DC / Northern Virginia | `https://gbfs.capitalbikeshare.com/gbfs/en` |
| **Biketown** | Portland, OR | `https://gbfs.biketownpdx.com/gbfs/en` |
| **Divvy** | Chicago, IL | `https://gbfs.divvybikes.com/gbfs/en` |

## Overview

**What it does:**
- Displays real-time bike availability (electric and classic bikes)
- Tracks multiple stations simultaneously (up to 4)
- Shows dock availability for bike returns
- Provides a searchable station picker fed live from the GBFS feed
- No API key required (uses public GBFS feed)

**Use Cases:**
- Check bike availability before leaving home/work
- Monitor stations near multiple locations (home, office, gym, etc.)
- Track both electric and classic bike availability
- Ensure dock availability for bike returns

## Prerequisites

- ✅ No API key required
- ✅ A Lyft bike share system in your area (see supported systems above)
- ✅ Web UI access for the station picker

## Quick Setup

### 1. Enable Lyft Bike Share

Via Web UI (Recommended):
1. Go to the **Integrations** page
2. Find **Lyft Bike Share** section
3. Toggle the **Lyft Bike Share** plugin on
4. Click **Save Changes**

Via Environment Variables:
```bash
# Add to .env
LYFT_BIKESHARE_ENABLED=true
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.citibikenyc.com/gbfs/en  # Set to your system
LYFT_BIKESHARE_REFRESH_SECONDS=60  # Optional: refresh interval (default: 60)
```

### 2. Select Your Bike Share System

Set the **GBFS Feed URL** to match the system in your city:

```bash
# Bay Wheels (San Francisco Bay Area)
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.baywheels.com/gbfs/en

# CitiBike (New York City)
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.citibikenyc.com/gbfs/en

# Capital Bikeshare (Washington DC)
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.capitalbikeshare.com/gbfs/en

# Biketown (Portland, OR)
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.biketownpdx.com/gbfs/en

# Divvy (Chicago, IL)
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.divvybikes.com/gbfs/en
```

### 3. Pick Your Stations

**Stations** is a searchable picker, not a box you type GBFS IDs into. It reads
your system's live `station_information.json`, so it always offers exactly the
stations your feed publishes.

1. Go to the **Lyft Bike Share** plugin on the **Integrations** page
2. Make sure the **GBFS Feed URL** is set for your city — it decides which
   catalog the picker offers
3. Open **Stations** and start typing a station name

   ```
   Type: "market"
   → Market St at 10th St     San Francisco · SF-G30     27 docks
     Market St at Beale St    San Francisco · SF-D22     19 docks
   ```

   Each option shows the station name, its region and station code, and how
   many docks it has. Options are grouped by region, so it is obvious whether
   "Broadway at 14th" is the one in Oakland or the one elsewhere.

4. **Select as many stations as you want.** Search runs upstream, so typing
   narrows the whole catalog rather than just the visible page.
5. **Drag them into order.** The first station is the one the single-station
   variables (`station_name`, `electric_bikes`, …) report on; the rest are
   available through `stations.1`, `stations.2`, and so on.
6. **Save** your configuration

Already know an ID? You can still type one in — `station_ids` is stored as a
plain array of GBFS station ID strings exactly as it always was, so existing
configurations keep working untouched.

If the picker shows a hint instead of a list, either the GBFS Feed URL is blank
or the feed could not be reached; see Troubleshooting below.

### 4. Create a Page to Display Bike Share Data

1. Go to **Pages** and click **New**
2. Choose **Template** page type
3. Add your template using Lyft Bike Share variables:

**Example Template:**
```
{center}BIKE SHARE
{lyft_bike_share.stations.0.station_name}
E-Bikes: {lyft_bike_share.stations.0.electric_bikes}
Classic: {lyft_bike_share.stations.0.classic_bikes}

{lyft_bike_share.stations.1.station_name}
E-Bikes: {lyft_bike_share.stations.1.electric_bikes}
Classic: {lyft_bike_share.stations.1.classic_bikes}
```

4. **Save** and **Set as Active**

## Template Variables

### Station-Specific Variables

Access individual stations using index (0-3):

```
{lyft_bike_share.stations.0.station_name}       # Station name (e.g., "19th St BART")
{lyft_bike_share.stations.0.electric_bikes}    # Number of electric bikes available
{lyft_bike_share.stations.0.classic_bikes}     # Number of classic bikes available
{lyft_bike_share.stations.0.num_bikes_available} # Total bikes available
{lyft_bike_share.stations.0.is_renting}        # "Yes" or "No"
```

### Aggregate Variables

Total across all configured stations:

```
{lyft_bike_share.total_electric}    # Total electric bikes across all stations
{lyft_bike_share.total_classic}     # Total classic bikes across all stations
{lyft_bike_share.total_bikes}       # Total bikes across all stations
```

### Station Count

```
{lyft_bike_share.station_count}     # Number of configured stations
```

## Example Templates

![Lyft Bike Share Display](./board-display.png)

### Simple Single Station

```
{center}BIKE SHARE
19th & Telegraph
E-Bikes: {lyft_bike_share.stations.0.electric_bikes}
Classic: {lyft_bike_share.stations.0.classic_bikes}
```

### Multiple Stations Compact

```
{center}BIKE SHARE
HOME: {lyft_bike_share.stations.0.electric_bikes}E {lyft_bike_share.stations.0.classic_bikes}C
WORK: {lyft_bike_share.stations.1.electric_bikes}E {lyft_bike_share.stations.1.classic_bikes}C
GYM:  {lyft_bike_share.stations.2.electric_bikes}E {lyft_bike_share.stations.2.classic_bikes}C
```

### Aggregate Summary

```
{center}BIKE SHARE TOTAL
{lyft_bike_share.station_count} Stations Monitored
E-Bikes: {lyft_bike_share.total_electric}
Classic: {lyft_bike_share.total_classic}
Bikes: {lyft_bike_share.total_bikes}
```

### With Station Names

```
{center}BIKE AVAILABILITY
{lyft_bike_share.stations.0.station_name}
E:{lyft_bike_share.stations.0.electric_bikes} C:{lyft_bike_share.stations.0.classic_bikes}

{lyft_bike_share.stations.1.station_name}
E:{lyft_bike_share.stations.1.electric_bikes} C:{lyft_bike_share.stations.1.classic_bikes}
```

## Configuration Reference

### Environment Variables

```bash
# Enable Lyft Bike Share
LYFT_BIKESHARE_ENABLED=true

# GBFS feed URL for your local system
LYFT_BIKESHARE_GBFS_BASE_URL=https://gbfs.baywheels.com/gbfs/en

# Refresh interval (seconds)
LYFT_BIKESHARE_REFRESH_SECONDS=60  # Default: 60 (1 minute)
```

### config.json Format

```json
{
  "features": {
    "lyft_bike_share": {
      "enabled": true,
      "gbfs_base_url": "https://gbfs.citibikenyc.com/gbfs/en",
      "refresh_seconds": 60,
      "station_ids": [
        "6926.07",
        "5430.08",
        "6140.02"
      ]
    }
  }
}
```

## Tips and Best Practices

### Choosing Stations

1. **Monitor key locations**: Home, work, gym, etc.
2. **Include backup options**: Stations close together for alternatives
3. **Check capacity**: Higher capacity stations = more reliable availability
4. **Consider routes**: Stations along your common routes

### Refresh Interval

- **60 seconds** (default): Good balance for most uses
- **30 seconds**: If you need very fresh data before leaving
- **120 seconds**: To reduce API calls (data still very current)

### Station Names

When configuring manually, use short names that fit on the display:
- ✅ "19TH", "WORK", "GYM", "HOME"
- ❌ "19th Street BART Station" (too long)

## Troubleshooting

### Station Picker Shows a Hint Instead of a List

**Problem:** The **Stations** field says it cannot load stations

**Solutions:**
1. **Set the GBFS Feed URL**: The picker cannot offer a catalog until it knows
   which system to read
2. **Verify GBFS Feed URL**: Confirm the URL matches your local system (see supported systems table above)
3. **Verify feed directly**: Open your system's `station_information.json` URL in a browser
4. **Search again**: Typing filters on station name only, so a street address or
   station code will not match

### Station Shows Zero Bikes

**Problem:** Station always shows 0 bikes/docks

**Solutions:**
1. **Check station status**: Station might be temporarily closed
2. **Verify station ID**: Re-select the station in the **Stations** picker
3. **Check GBFS status feed**: Station might be disabled for maintenance

### Data Not Updating

**Problem:** Bike counts seem stale

**Solutions:**
1. **Check refresh interval**: Verify `LYFT_BIKESHARE_REFRESH_SECONDS` is set
2. **Check logs**: Look for GBFS API errors
3. **Restart service**: Docker containers might need restart
4. **Test GBFS directly**:
   ```bash
   curl https://gbfs.citibikenyc.com/gbfs/en/station_status.json
   ```

### Station Names Too Long

**Problem:** Station names overflow on display

**Solutions:**
1. **Use truncate filter**: `{lyft_bike_share.stations.0.station_name|truncate:22}`
2. **Use abbreviations**: "BART" instead of "BART Station"

## Data Source

All Lyft bike share systems use the **GBFS (General Bikeshare Feed Specification)** standard:

- **Station Info**: `{gbfs_base_url}/station_information.json`
- **Station Status**: `{gbfs_base_url}/station_status.json`
- **Update Frequency**: Real-time (updates every 10-30 seconds at source)

## Advanced Usage

### Combining with Other Features

```
{center}MORNING COMMUTE
Muni: {muni.stops.0.formatted}
Bikes: {lyft_bike_share.stations.0.electric_bikes}E
Traffic: {traffic.routes.0.duration_minutes}m
```

### Multiple Station Comparisons

```
{center}WHICH STATION?
Near: {lyft_bike_share.stations.0.electric_bikes}E {lyft_bike_share.stations.0.classic_bikes}C
Alt:  {lyft_bike_share.stations.1.electric_bikes}E {lyft_bike_share.stations.1.classic_bikes}C
Best: {lyft_bike_share.stations.2.electric_bikes}E {lyft_bike_share.stations.2.classic_bikes}C
```

## API Reference

### REST API Endpoints

```bash
# List all stations for configured system
GET /lyft_bike_share/stations

# Find stations near location
GET /lyft_bike_share/stations/nearby?lat=40.7128&lng=-74.0060&radius=2.0

# Search stations by address
GET /lyft_bike_share/stations/search?address=123+Market+St&radius=2.0
```

## Related Features

- **Transit**: Track transit arrivals alongside bike availability
- **Traffic**: Compare bike vs. drive times
- **Weather**: Check weather before biking

## Resources

- [GBFS Specification](https://github.com/MobilityData/gbfs)
- [Bay Wheels](https://www.baywheels.com/)
- [CitiBike](https://citibikenyc.com/)
- [Capital Bikeshare](https://www.capitalbikeshare.com/)
- [Biketown](https://www.biketownpdx.com/)
- [Divvy](https://divvybikes.com/)

---

**Next Steps:**
1. Enable Lyft Bike Share in Settings
2. Set the GBFS Feed URL for your city's system
3. Use the **Stations** picker to add your favorite stations
4. Create a page with bike availability
5. Set as active page or combine with other transit data
