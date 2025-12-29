"""
Example usage of the USGS data fetcher API

This demonstrates the 3 main functions:
1. normalize_site_id() - Clean up site IDs
2. get_gauge_fields() - Get available fields for a gauge
3. get_gauge_data() - Fetch time series data
"""

from datasources.usgs.fetch_data_functional import (
    normalize_site_id,
    get_gauge_fields,
    get_gauge_data
)


def main():
    # Example USGS site ID (Potomac River at Little Falls)
    site_id = 'USGS-01646500'

    # 1. Normalize the site ID (removes 'USGS' prefix)
    print("=" * 60)
    print("1. Normalizing site ID")
    print("=" * 60)
    clean_id = normalize_site_id(site_id)
    print(f"Original: {site_id}")
    print(f"Normalized: {clean_id}")
    print()

    # 2. Get available fields/parameters for the gauge
    print("=" * 60)
    print("2. Getting gauge fields and metadata")
    print("=" * 60)
    fields = get_gauge_fields(clean_id)
    print(f"Site ID: {fields['site_id']}")
    print(f"Site Name: {fields['site_name']}")
    print(f"Location: {fields['latitude']}, {fields['longitude']}")
    print(f"State: {fields['state']}")
    print(f"Drainage Area: {fields['drainage_area']}")
    print(f"\nAvailable Parameters:")
    for code, info in fields['available_parameters'].items():
        print(f"  - {info['name']} (code: {code})")
    print()

    # 3. Get actual time series data
    print("=" * 60)
    print("3. Fetching gauge data")
    print("=" * 60)

    # Fetch streamflow data for a specific period
    df = get_gauge_data(
        site_id=clean_id,
        start_date='2024-01-01',
        end_date='2024-01-31',
        parameters=['streamflow'],  # Can also use ['00060'] or None for all
        daily=True  # Set to False for instantaneous values
    )

    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nBasic statistics:")
    print(df.describe())
    print()

    # Example: Fetch multiple parameters
    print("=" * 60)
    print("4. Fetching multiple parameters")
    print("=" * 60)
    df_multi = get_gauge_data(
        site_id=clean_id,
        start_date='2024-01-01',
        end_date='2024-01-07',
        parameters=['streamflow', 'gage_height'],
        daily=True
    )
    print(f"Data shape: {df_multi.shape}")
    print(f"Columns: {list(df_multi.columns)}")
    print(df_multi.head())


if __name__ == '__main__':
    main()

