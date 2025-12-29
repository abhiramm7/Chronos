"""
USGS Water Data Fetcher - Simplified API

This module provides a clean interface to fetch data from USGS water gauges.

Main Functions:
    1. get_gauge_fields(site_id) - Get available data fields for a gauge
    2. get_gauge_data(site_id, start_date, end_date) - Get data for a gauge
    3. normalize_site_id(site_id) - Clean up site ID format
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
import warnings


# USGS API Endpoints
SITE_URL = "https://waterservices.usgs.gov/nwis/site/"
DV_URL = "https://waterservices.usgs.gov/nwis/dv/"

# Common USGS Parameter Codes
PARAMETER_CODES = {
    'streamflow': '00060',      # Discharge, cubic feet per second
    'gage_height': '00065',     # Gage height, feet
    'temperature': '00010',     # Temperature, water, degrees Celsius
    'precipitation': '00045',   # Precipitation, total, inches
    'air_temp': '00020',        # Temperature, air, degrees Celsius
}


def normalize_site_id(site_id: str) -> str:
    """
    Clean up USGS site ID by removing 'USGS' prefix and whitespace.

    Args:
        site_id: USGS site identifier (e.g., 'USGS-01646500', '01646500')

    Returns:
        Cleaned site ID (e.g., '01646500')

    Examples:
        >>> normalize_site_id('USGS-01646500')
        '01646500'
        >>> normalize_site_id('  01646500  ')
        '01646500'
    """
    cleaned = site_id.strip()

    if cleaned.upper().startswith('USGS-'):
        return cleaned[5:].strip()
    elif cleaned.upper().startswith('USGS'):
        return cleaned[4:].strip()

    return cleaned


def get_gauge_fields(site_id: str) -> Dict[str, Dict]:
    """
    Get available data fields/parameters for a USGS gauge.

    Args:
        site_id: USGS site identifier

    Returns:
        Dictionary with available fields and their metadata:
        {
            'site_id': str,
            'site_name': str,
            'latitude': float,
            'longitude': float,
            'state': str,
            'available_parameters': {
                'parameter_code': {
                    'name': str,
                    'description': str,
                    'unit': str
                },
                ...
            }
        }

    Examples:
        >>> fields = get_gauge_fields('01646500')
        >>> print(fields['site_name'])
        >>> print(fields['available_parameters'].keys())
    """
    site_id = normalize_site_id(site_id)

    # Get site info and available parameters
    url = f"{SITE_URL}?format=rdb&sites={site_id}&seriesCatalogOutput=true&siteOutput=expanded"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        rdb_text = response.text
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching gauge info for site {site_id}: {e}")

    # Parse RDB format
    lines = rdb_text.split('\n')

    # Find site info
    site_info = {}
    header_idx = None
    header = []

    for i, line in enumerate(lines):
        if line.startswith('agency_cd\t'):
            header_idx = i
            header = line.split('\t')
            if i + 2 < len(lines):
                data = lines[i + 2].split('\t')
                site_info = dict(zip(header, data))
            break

    if not site_info:
        raise ValueError(f"Site {site_id} not found in USGS database")

    # Parse available parameters
    available_params = {}
    if header_idx is not None and header:
        for line in lines:
            if line.startswith('#'):
                continue
            parts = line.split('\t')

            # Look for parameter codes in the data
            if len(parts) > 5 and 'parm_cd' in header:
                try:
                    parm_idx = header.index('parm_cd')
                    if parm_idx < len(parts):
                        param_code = parts[parm_idx]
                        if param_code and param_code.isdigit():
                            # Try to find parameter name
                            param_name = next(
                                (name for name, code in PARAMETER_CODES.items() if code == param_code),
                                f"parameter_{param_code}"
                            )
                            available_params[param_code] = {
                                'name': param_name,
                                'code': param_code
                            }
                except (ValueError, IndexError):
                    continue

    return {
        'site_id': site_info.get('site_no', site_id),
        'site_name': site_info.get('station_nm', 'Unknown'),
        'latitude': float(site_info.get('dec_lat_va', 0)),
        'longitude': float(site_info.get('dec_long_va', 0)),
        'state': site_info.get('state_cd', ''),
        'drainage_area': site_info.get('drain_area_va', 'N/A'),
        'available_parameters': available_params
    }


def get_gauge_data(
    site_id: str,
    start_date: str,
    end_date: str,
    parameters: Optional[List[str]] = None,
    daily: bool = True
) -> pd.DataFrame:
    """
    Get time series data from a USGS gauge.

    Args:
        site_id: USGS site identifier
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        parameters: List of parameter names or codes to fetch.
                   If None, fetches all available common parameters.
                   Examples: ['streamflow', 'precipitation', '00060']
        daily: If True, fetch daily averages. If False, fetch instantaneous values.

    Returns:
        DataFrame with datetime index and columns for each parameter

    Examples:
        >>> # Get all available data
        >>> df = get_gauge_data('01646500', '2023-01-01', '2023-12-31')
        >>>
        >>> # Get only streamflow
        >>> df = get_gauge_data('01646500', '2023-01-01', '2023-12-31',
        ...                     parameters=['streamflow'])
        >>>
        >>> # Get instantaneous values
        >>> df = get_gauge_data('01646500', '2023-01-01', '2023-01-07',
        ...                     daily=False)
    """
    site_id = normalize_site_id(site_id)

    # If no parameters specified, try common ones
    if parameters is None:
        parameters = list(PARAMETER_CODES.keys())

    # Convert parameter names to codes
    param_codes = []
    for param in parameters:
        if param in PARAMETER_CODES:
            param_codes.append(PARAMETER_CODES[param])
        elif param.isdigit():
            param_codes.append(param)
        else:
            warnings.warn(f"Unknown parameter: {param}")

    if not param_codes:
        raise ValueError("No valid parameters specified")

    # Fetch data for each parameter
    all_data = []

    for param_code in param_codes:
        df = _fetch_single_parameter(site_id, param_code, start_date, end_date, daily)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        warnings.warn(f"No data available for site {site_id} in the specified period")
        return pd.DataFrame()

    # Merge all parameters
    result = all_data[0]
    for df in all_data[1:]:
        result = result.join(df, how='outer')

    return result


def _fetch_single_parameter(
    site_id: str,
    parameter_code: str,
    start_date: str,
    end_date: str,
    daily: bool
) -> pd.DataFrame:
    """
    Internal function to fetch a single parameter.

    Args:
        site_id: USGS site identifier (already normalized)
        parameter_code: USGS parameter code
        start_date: Start date 'YYYY-MM-DD'
        end_date: End date 'YYYY-MM-DD'
        daily: Whether to fetch daily or instantaneous values

    Returns:
        DataFrame with the parameter data
    """
    url = DV_URL if daily else "https://waterservices.usgs.gov/nwis/iv/"

    params = {
        'format': 'json',
        'sites': site_id,
        'startDT': start_date,
        'endDT': end_date,
        'parameterCd': parameter_code,
        'siteStatus': 'all'
    }

    if daily:
        params['statCd'] = '00003'  # Mean value

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        warnings.warn(f"Error fetching parameter {parameter_code}: {e}")
        return pd.DataFrame()

    # Parse JSON response
    if not data or 'value' not in data or 'timeSeries' not in data['value']:
        return pd.DataFrame()

    time_series = data['value']['timeSeries']
    if len(time_series) == 0:
        return pd.DataFrame()

    values_list = time_series[0]['values'][0]['value']
    if len(values_list) == 0:
        return pd.DataFrame()

    variable_name = time_series[0]['variable']['variableName']

    # Create DataFrame
    df = pd.DataFrame(values_list)
    df['dateTime'] = pd.to_datetime(df['dateTime'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.set_index('dateTime')

    # Use friendly column name if possible
    param_name = next(
        (name for name, code in PARAMETER_CODES.items() if code == parameter_code),
        variable_name
    )

    return df[['value']].rename(columns={'value': param_name})


