"""
Example: Using USGS Functional API for Anacostia River

This example demonstrates the functional programming interface for fetching
USGS hydrological data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datasources.usgs.fetch_data_functional import (
    create_site_config,
    fetch_streamflow,
    fetch_precipitation,
    get_site_info,
    check_data_availability,
    find_nearest_sites_with_precipitation
)
import numpy as np
from datetime import datetime, timedelta


def main():
    """Main example function demonstrating functional API."""

    print("=" * 60)
    print("USGS FUNCTIONAL API - ANACOSTIA RIVER EXAMPLE")
    print("=" * 60)

    # 1. Create site configuration (immutable)
    print("\n1. Creating site configuration...")
    config = create_site_config("USGS-01651827", validate=True)
    print(f"   Site ID: {config.site_id}")

    # 2. Get site information (pure function, returns immutable data)
    print("\n2. Getting site information...")
    site_info = get_site_info(config)
    if site_info:
        print(f"   Name: {site_info.name}")
        print(f"   Location: ({site_info.latitude}, {site_info.longitude})")
        print(f"   State: {site_info.state_code}")

    # 3. Check data availability (pure function)
    print("\n3. Checking data availability...")
    availability = check_data_availability(config)
    for param, available in availability.items():
        status = "✓" if available else "✗"
        print(f"   {status} {param}")

    # 4. Fetch streamflow data (composition of pure and impure functions)
    print("\n4. Fetching streamflow data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    streamflow = fetch_streamflow(
        config,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        daily=False
    )

    if not streamflow.empty:
        print(f"   Retrieved {len(streamflow)} data points")
        print(f"   Mean: {streamflow['streamflow_cfs'].mean():.2f} cfs")
        print(f"\n   Sample data:")
        print(streamflow.head())

    # 5. Find nearby precipitation sites (pure + impure composition)
    print("\n5. Finding nearby precipitation sites...")
    nearby = find_nearest_sites_with_precipitation(config, max_distance_miles=25, max_results=3)

    if nearby:
        print(f"   Found {len(nearby)} sites:")
        for site in nearby:
            print(f"   - {site.site_id}: {site.name} ({site.distance_miles} miles)")

        # 6. Fetch precipitation from nearest site (function composition)
        print(f"\n6. Fetching precipitation from nearest site...")
        precip_config = create_site_config(nearby[0].site_id, validate=False)

        precipitation = fetch_precipitation(
            precip_config,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            daily=False
        )

        if not precipitation.empty:
            print(f"   Retrieved {len(precipitation)} data points")
            print(f"   Total precipitation: {precipitation['precipitation_inches'].sum():.2f} inches")
            print(f"\n   Sample data:")
            print(precipitation.head())

    # 7. Functional data transformation pipeline
    print("\n7. Functional data transformation pipeline...")
    if not streamflow.empty:
        # Resample to hourly
        hourly = streamflow.resample('1h').mean()

        # Apply transformation (pure function)
        hourly['log_streamflow'] = hourly['streamflow_cfs'].apply(lambda x: np.log1p(x) if x > 0 else 0)

        print(f"   Resampled to hourly: {len(hourly)} points")
        print(f"   Applied log transform")
        print(f"\n   Transformed data:")
        print(hourly.head())

        # Save result
        output_file = f"anacostia_functional_{start_date.strftime('%Y%m%d')}.csv"
        hourly.to_csv(output_file)
        print(f"\n   Saved to: {output_file}")

    print("\n" + "=" * 60)
    print("FUNCTIONAL API DEMONSTRATION COMPLETE")
    print("=" * 60)


def demonstrate_functional_composition():
    """Demonstrate pure functional composition patterns."""

    print("\n" + "=" * 60)
    print("FUNCTIONAL COMPOSITION PATTERNS")
    print("=" * 60)

    from functools import partial

    # Create multiple site configurations
    site_ids = ["01651827", "01652500"]

    # Map: Transform site IDs to configs (pure)
    configs = list(map(create_site_config, site_ids))
    print(f"\n1. Mapped {len(site_ids)} site IDs to configs")

    # Map: Get site info for each (impure but functional)
    site_infos = list(map(get_site_info, configs))
    valid_sites = [s for s in site_infos if s is not None]
    print(f"2. Retrieved info for {len(valid_sites)} sites")

    # Filter: Get sites with precipitation
    has_precip = lambda config: check_data_availability(config).get('precipitation', False)
    configs_with_precip = list(filter(has_precip, configs))
    print(f"3. Filtered to {len(configs_with_precip)} sites with precipitation")

    # Partial application: Create specialized fetch function
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)

    fetch_recent_streamflow = partial(
        fetch_streamflow,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        daily=False
    )

    # Map: Fetch data from all configs
    streamflow_data = list(map(fetch_recent_streamflow, configs))
    print(f"4. Fetched streamflow from {len(streamflow_data)} sites")

    # Reduce: Combine dataframes (if needed)
    non_empty = [df for df in streamflow_data if not df.empty]
    if non_empty:
        print(f"5. Combined {len(non_empty)} non-empty datasets")

    print("\nFunctional patterns demonstrated:")
    print("  ✓ Map (transform collections)")
    print("  ✓ Filter (select elements)")
    print("  ✓ Partial application (specialize functions)")
    print("  ✓ Function composition")


if __name__ == "__main__":
    main()
    demonstrate_functional_composition()

