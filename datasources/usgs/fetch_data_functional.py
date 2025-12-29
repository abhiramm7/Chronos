"""
USGS Data Fetcher - Functional Programming Implementation

This module provides functional programming interface to query USGS Water Services API for:
- Streamflow (discharge)
- Precipitation (rainfall)
- Temperature

Example:
    >>> from datasources.usgs import fetch_streamflow, create_site_config
    >>> config = create_site_config("01651827")
    >>> data = fetch_streamflow(config, start_date="2020-01-01", end_date="2020-12-31")
    >>> print(data.head())
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
import warnings
from functools import reduce
from dataclasses import dataclass


# Constants
PARAMETER_CODES = {
    'streamflow': '00060',      # Discharge, cubic feet per second
    'gage_height': '00065',     # Gage height, feet
    'temperature': '00010',     # Temperature, water, degrees Celsius
    'precipitation': '00045',   # Precipitation, total, inches
    'air_temp': '00020',        # Temperature, air, degrees Celsius
}

BASE_URL = "https://waterservices.usgs.gov/nwis/iv/"
DV_URL = "https://waterservices.usgs.gov/nwis/dv/"
SITE_URL = "https://waterservices.usgs.gov/nwis/site/"


# Data structures (immutable)
@dataclass(frozen=True)
class SiteConfig:
    """Immutable site configuration"""
    site_id: str
    base_url: str = BASE_URL
    dv_url: str = DV_URL
    site_url: str = SITE_URL


@dataclass(frozen=True)
class SiteInfo:
    """Immutable site information"""
    site_id: str
    name: str
    latitude: float
    longitude: float
    state_code: str
    drainage_area: Optional[str] = None


@dataclass(frozen=True)
class NearbySite:
    """Immutable nearby site information"""
    site_id: str
    name: str
    latitude: float
    longitude: float
    distance_miles: float


# Pure utility functions
def normalize_site_id(site_id: str) -> str:
    """
    Normalize site ID by removing USGS prefix and whitespace.

    Args:
        site_id: Raw site identifier

    Returns:
        Normalized site ID
    """
    cleaned = site_id.strip()

    if cleaned.upper().startswith('USGS-'):
        return cleaned[5:].strip()
    elif cleaned.upper().startswith('USGS'):
        return cleaned[4:].strip()

    return cleaned


def create_site_config(site_id: str, validate: bool = False) -> SiteConfig:
    """
    Create an immutable site configuration.

    Args:
        site_id: USGS site identifier (accepts multiple formats)
        validate: If True, validate site exists (has side effects - prints)

    Returns:
        SiteConfig instance
    """
    normalized_id = normalize_site_id(site_id)
    config = SiteConfig(site_id=normalized_id)

    if validate:
        validate_and_display_site(config)

    return config


# HTTP request functions (impure - I/O operations)
def fetch_json_from_usgs(url: str, params: Dict) -> Optional[Dict]:
    """
    Fetch JSON data from USGS API.

    Args:
        url: API endpoint URL
        params: Query parameters

    Returns:
        JSON response as dict, or None on error
    """
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def fetch_rdb_from_usgs(url: str, params: Optional[Dict] = None) -> Optional[str]:
    """
    Fetch RDB (tab-delimited) data from USGS API.

    Args:
        url: API endpoint URL
        params: Query parameters (optional)

    Returns:
        RDB response as string, or None on error
    """
    try:
        response = requests.get(url, params=params or {}, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


# Data parsing functions (pure)
def parse_time_series_json(data: Dict, parameter_code: str) -> Optional[List[Dict]]:
    """
    Parse time series data from USGS JSON response.

    Args:
        data: JSON response from USGS
        parameter_code: Parameter code being fetched

    Returns:
        List of value dictionaries, or None if no data
    """
    if not data or 'value' not in data or 'timeSeries' not in data['value']:
        warnings.warn(f"No data found for parameter {parameter_code}")
        return None

    time_series = data['value']['timeSeries']

    if len(time_series) == 0:
        warnings.warn(f"No time series data for parameter {parameter_code}")
        return None

    values_list = time_series[0]['values'][0]['value']

    if len(values_list) == 0:
        warnings.warn(f"Empty values list for parameter {parameter_code}")
        return None

    variable_name = time_series[0]['variable']['variableName']

    return {'values': values_list, 'variable_name': variable_name}


def create_dataframe_from_values(parsed_data: Optional[Dict]) -> pd.DataFrame:
    """
    Create a DataFrame from parsed USGS values.

    Args:
        parsed_data: Parsed time series data with 'values' and 'variable_name'

    Returns:
        DataFrame with datetime index
    """
    if not parsed_data:
        return pd.DataFrame()

    df = pd.DataFrame(parsed_data['values'])
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.set_index('dateTime')

    return df[['value']].rename(columns={'value': parsed_data['variable_name']})


def parse_rdb_site_info(rdb_text: str, site_id: str) -> Optional[Dict]:
    """
    Parse site information from RDB format.

    Args:
        rdb_text: RDB formatted text
        site_id: Site ID being queried

    Returns:
        Dictionary of site information
    """
    if not rdb_text:
        return None

    lines = rdb_text.split('\n')

    for i, line in enumerate(lines):
        if line.startswith('agency_cd'):
            header = line.split('\t')
            if i + 2 < len(lines):
                data = lines[i + 2].split('\t')
                return dict(zip(header, data))

    return None


def parse_rdb_sites_list(rdb_text: str) -> List[Dict]:
    """
    Parse list of sites from RDB format.

    Args:
        rdb_text: RDB formatted text

    Returns:
        List of site dictionaries
    """
    if not rdb_text:
        return []

    lines = rdb_text.split('\n')

    # Find header
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith('agency_cd\t'):
            header_idx = i
            break

    if header_idx is None:
        return []

    header = lines[header_idx].split('\t')

    # Parse data lines (skip format line)
    sites = []
    for line in lines[header_idx + 2:]:
        if not line or line.startswith('#'):
            continue

        parts = line.split('\t')
        if len(parts) >= len(header):
            sites.append(dict(zip(header, parts)))

    return sites


# Calculation functions (pure)
def calculate_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate approximate distance between two points in miles.

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in miles (approximate)
    """
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 69.0


def filter_sites_by_distance(
    sites: List[Dict],
    center_lat: float,
    center_lon: float,
    max_distance: float,
    exclude_site_id: str
) -> List[NearbySite]:
    """
    Filter sites by distance from a center point.

    Args:
        sites: List of site dictionaries
        center_lat, center_lon: Center point coordinates
        max_distance: Maximum distance in miles
        exclude_site_id: Site ID to exclude from results

    Returns:
        List of NearbySite objects within distance, sorted by distance
    """
    nearby = []

    for site in sites:
        try:
            site_id = site.get('site_no', '')

            if site_id == exclude_site_id:
                continue

            site_lat = float(site.get('dec_lat_va', 0))
            site_lon = float(site.get('dec_long_va', 0))

            distance = calculate_distance_miles(center_lat, center_lon, site_lat, site_lon)

            if distance <= max_distance:
                nearby.append(NearbySite(
                    site_id=site_id,
                    name=site.get('station_nm', 'Unknown'),
                    latitude=site_lat,
                    longitude=site_lon,
                    distance_miles=round(distance, 2)
                ))
        except (ValueError, TypeError):
            continue

    return sorted(nearby, key=lambda x: x.distance_miles)


# Main data fetching functions (compose pure and impure functions)
def fetch_instantaneous_values(
    config: SiteConfig,
    parameter_code: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch instantaneous values from USGS.

    Args:
        config: Site configuration
        parameter_code: USGS parameter code
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'

    Returns:
        DataFrame with datetime index and parameter values
    """
    params = {
        'format': 'json',
        'sites': config.site_id,
        'startDT': start_date,
        'endDT': end_date,
        'parameterCd': parameter_code,
        'siteStatus': 'all'
    }

    data = fetch_json_from_usgs(config.base_url, params)
    parsed = parse_time_series_json(data, parameter_code)
    return create_dataframe_from_values(parsed)


def fetch_daily_values(
    config: SiteConfig,
    parameter_code: str,
    start_date: str,
    end_date: str,
    stat_code: str = "00003"
) -> pd.DataFrame:
    """
    Fetch daily values from USGS.

    Args:
        config: Site configuration
        parameter_code: USGS parameter code
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        stat_code: Statistic code (00003=mean, 00001=max, 00002=min)

    Returns:
        DataFrame with datetime index and daily parameter values
    """
    params = {
        'format': 'json',
        'sites': config.site_id,
        'startDT': start_date,
        'endDT': end_date,
        'parameterCd': parameter_code,
        'statCd': stat_code,
        'siteStatus': 'all'
    }

    data = fetch_json_from_usgs(config.dv_url, params)
    parsed = parse_time_series_json(data, parameter_code)
    return create_dataframe_from_values(parsed)


# Public API functions
def fetch_streamflow(
    config: SiteConfig,
    start_date: str,
    end_date: str,
    daily: bool = True
) -> pd.DataFrame:
    """
    Fetch streamflow (discharge) data.

    Args:
        config: Site configuration
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        daily: If True, fetch daily values; if False, fetch instantaneous values

    Returns:
        DataFrame with streamflow data
    """
    param_code = PARAMETER_CODES['streamflow']

    df = (fetch_daily_values(config, param_code, start_date, end_date) if daily
          else fetch_instantaneous_values(config, param_code, start_date, end_date))

    if not df.empty:
        df.columns = ['streamflow_cfs']

    return df


def fetch_precipitation(
    config: SiteConfig,
    start_date: str,
    end_date: str,
    daily: bool = True
) -> pd.DataFrame:
    """
    Fetch precipitation data.

    Args:
        config: Site configuration
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        daily: If True, fetch daily values; if False, fetch instantaneous values

    Returns:
        DataFrame with precipitation data
    """
    param_code = PARAMETER_CODES['precipitation']

    df = (fetch_daily_values(config, param_code, start_date, end_date) if daily
          else fetch_instantaneous_values(config, param_code, start_date, end_date))

    if not df.empty:
        df.columns = ['precipitation_inches']

    return df


def fetch_temperature(
    config: SiteConfig,
    start_date: str,
    end_date: str,
    daily: bool = True,
    air_temp: bool = False
) -> pd.DataFrame:
    """
    Fetch temperature data.

    Args:
        config: Site configuration
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        daily: If True, fetch daily values; if False, fetch instantaneous values
        air_temp: If True, fetch air temperature; if False, fetch water temperature

    Returns:
        DataFrame with temperature data
    """
    param_code = PARAMETER_CODES['air_temp'] if air_temp else PARAMETER_CODES['temperature']

    df = (fetch_daily_values(config, param_code, start_date, end_date) if daily
          else fetch_instantaneous_values(config, param_code, start_date, end_date))

    if not df.empty:
        col_name = 'air_temp_celsius' if air_temp else 'water_temp_celsius'
        df.columns = [col_name]

    return df


def fetch_all_data(
    config: SiteConfig,
    start_date: str,
    end_date: str,
    daily: bool = True,
    include_air_temp: bool = True
) -> pd.DataFrame:
    """
    Fetch all available data (streamflow, precipitation, temperature).

    Args:
        config: Site configuration
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        daily: If True, fetch daily values; if False, fetch instantaneous values
        include_air_temp: If True, also fetch air temperature

    Returns:
        DataFrame with all available data merged on datetime index
    """
    print(f"Fetching data for USGS site {config.site_id}")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 60)

    # Fetch all data types
    fetch_ops = [
        ("streamflow", lambda: fetch_streamflow(config, start_date, end_date, daily)),
        ("precipitation", lambda: fetch_precipitation(config, start_date, end_date, daily)),
        ("water_temp", lambda: fetch_temperature(config, start_date, end_date, daily, False)),
    ]

    if include_air_temp:
        fetch_ops.append(("air_temp", lambda: fetch_temperature(config, start_date, end_date, daily, True)))

    # Execute fetches and filter non-empty results
    results = []
    for name, fetch_fn in fetch_ops:
        print(f"Fetching {name} data...")
        df = fetch_fn()
        if not df.empty:
            results.append(df)

    if not results:
        print("\nNo data available for the specified period.")
        return pd.DataFrame()

    # Merge all dataframes using reduce
    merged = reduce(lambda left, right: left.join(right, how='outer'), results)

    print("-" * 60)
    print(f"Data fetched successfully!")
    print(f"Total records: {len(merged)}")
    print(f"Columns: {list(merged.columns)}")
    print(f"\nData summary:")
    print(merged.describe())

    return merged


def get_site_info(config: SiteConfig) -> Optional[SiteInfo]:
    """
    Get information about the USGS site.

    Args:
        config: Site configuration

    Returns:
        SiteInfo object, or None if site not found
    """
    url = f"{config.site_url}?format=rdb&sites={config.site_id}&siteOutput=expanded"
    rdb_text = fetch_rdb_from_usgs(url)

    if not rdb_text:
        return None

    site_data = parse_rdb_site_info(rdb_text, config.site_id)

    if not site_data:
        return None

    try:
        return SiteInfo(
            site_id=site_data.get('site_no', config.site_id),
            name=site_data.get('station_nm', 'Unknown'),
            latitude=float(site_data.get('dec_lat_va', 0)),
            longitude=float(site_data.get('dec_long_va', 0)),
            state_code=site_data.get('state_cd', ''),
            drainage_area=site_data.get('drain_area_va')
        )
    except (ValueError, TypeError):
        return None


def check_data_availability(config: SiteConfig) -> Dict[str, bool]:
    """
    Check which parameters are available for this site.

    Args:
        config: Site configuration

    Returns:
        Dictionary mapping parameter names to availability status
    """
    url = f"{config.site_url}?format=rdb&sites={config.site_id}&seriesCatalogOutput=true"
    rdb_text = fetch_rdb_from_usgs(url)

    if not rdb_text:
        return {name: False for name in PARAMETER_CODES.keys()}

    # Extract available parameter codes
    available_params = set()
    for line in rdb_text.split('\n'):
        if '\t' in line and not line.startswith('#'):
            parts = line.split('\t')
            for part in parts:
                if part in PARAMETER_CODES.values():
                    available_params.add(part)

    # Map back to parameter names
    return {name: code in available_params for name, code in PARAMETER_CODES.items()}


def find_nearest_sites_with_precipitation(
    config: SiteConfig,
    max_distance_miles: float = 50.0,
    max_results: int = 5
) -> List[NearbySite]:
    """
    Find nearby sites with precipitation data.

    Args:
        config: Site configuration
        max_distance_miles: Maximum search radius in miles
        max_results: Maximum number of results to return

    Returns:
        List of NearbySite objects, sorted by distance
    """
    site_info = get_site_info(config)

    if not site_info:
        print("Could not get location for current site")
        return []

    # Determine states to search
    state_code = site_info.state_code
    search_states = ['DC', 'MD', 'VA'] if state_code == '11' else [state_code] if state_code else ['DC', 'MD', 'VA']

    precip_code = PARAMETER_CODES['precipitation']

    # Fetch sites from all states and combine
    all_sites = []
    for state in search_states:
        params = {
            'format': 'rdb',
            'stateCd': state,
            'parameterCd': precip_code,
            'siteOutput': 'expanded',
            'siteStatus': 'active'
        }

        rdb_text = fetch_rdb_from_usgs(config.site_url, params)
        if rdb_text:
            all_sites.extend(parse_rdb_sites_list(rdb_text))

    # Filter by distance
    nearby = filter_sites_by_distance(
        all_sites,
        site_info.latitude,
        site_info.longitude,
        max_distance_miles,
        config.site_id
    )

    return nearby[:max_results]


# Display functions (impure - side effects)
def display_data_sources(config: SiteConfig) -> None:
    """
    Display available data sources for this site.
    If precipitation is not available, suggest nearby sites.

    Args:
        config: Site configuration
    """
    availability = check_data_availability(config)

    print("\nData Source Availability:")
    print("-" * 60)

    available_params = []
    unavailable_params = []

    for param_name, is_available in availability.items():
        if is_available:
            print(f"✓ {param_name.replace('_', ' ').title()}: Available")
            available_params.append(param_name)
        else:
            print(f"✗ {param_name.replace('_', ' ').title()}: Not Available")
            unavailable_params.append(param_name)

    # Special handling for precipitation
    if 'precipitation' in unavailable_params:
        print("\n⚠ Precipitation data not available at this site.")
        print("  Searching for nearby sites with precipitation...")

        nearby_sites = find_nearest_sites_with_precipitation(config, 50.0, 3)

        if nearby_sites:
            print(f"\n  Found {len(nearby_sites)} nearby site(s) with precipitation:")
            print("  " + "-" * 56)
            for i, site in enumerate(nearby_sites, 1):
                print(f"  {i}. Site ID: {site.site_id}")
                print(f"     Name: {site.name}")
                print(f"     Distance: {site.distance_miles} miles")
                print(f"     Coordinates: {site.latitude:.4f}, {site.longitude:.4f}")
                if i < len(nearby_sites):
                    print()

            print(f"\n  Suggestion: Use create_site_config('{nearby_sites[0].site_id}') to fetch precipitation")
            print("              data from the nearest site.")
        else:
            print("  No nearby sites with precipitation found within 50 miles.")

    print("-" * 60)

    if not available_params:
        print("\n⚠ WARNING: No data parameters available for this site!")
    else:
        print(f"\n✓ {len(available_params)} data parameter(s) available for analysis")


def validate_and_display_site(config: SiteConfig) -> None:
    """
    Validate site and display information.

    Args:
        config: Site configuration
    """
    print(f"\nValidating USGS site: {config.site_id}")
    print("-" * 60)

    site_info = get_site_info(config)

    if not site_info:
        print(f"⚠ WARNING: Could not find site {config.site_id}")
        print("Please verify the site ID at: https://waterdata.usgs.gov/nwis")
        return

    print(f"✓ Site found: {site_info.name}")
    print(f"  Location: {site_info.latitude}, {site_info.longitude}")

    print("\nChecking data availability...")
    display_data_sources(config)

