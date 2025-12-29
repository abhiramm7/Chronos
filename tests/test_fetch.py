#!/usr/bin/env python3
"""Test script for the simplified USGS data API"""

from datasources.usgs import (
    normalize_site_id,
    get_gauge_fields,
    get_gauge_data,
    PARAMETER_CODES
)

print("=" * 70)
print("Testing USGS Data Fetcher - Simplified API")
print("=" * 70)

# Test 1: Normalize site ID
print("\n1. Testing normalize_site_id()")
print("-" * 70)
site_id = normalize_site_id('USGS-01651000')
print(f"Normalized site ID: {site_id}")

# Test 2: Get gauge fields (requires network)
print("\n2. Testing get_gauge_fields()")
print("-" * 70)
try:
    fields = get_gauge_fields(site_id)
    print(f"Site Name: {fields['site_name']}")
    print(f"Location: ({fields['latitude']}, {fields['longitude']})")
    print(f"State: {fields['state']}")
    print(f"Available parameters: {list(fields['available_parameters'].keys())}")
except Exception as e:
    print(f"Error: {e}")
    print("(This may be a network or USGS API issue)")

# Test 3: Get gauge data (requires network)
print("\n3. Testing get_gauge_data()")
print("-" * 70)
try:
    df = get_gauge_data(
        site_id=site_id,
        start_date='2024-01-01',
        end_date='2024-01-31',
        parameters=['streamflow'],
        daily=True
    )

    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    if not df.empty:
        print("\nSuccess! Data retrieved:")
        print(df.head(10))
        print(f"\nBasic statistics:")
        print(df.describe())
    else:
        print("\nNo data returned (may not be available for this period)")

except Exception as e:
    print(f"Error: {e}")
    print("(This may be a network or USGS API issue)")

print("\n" + "=" * 70)
print("Test complete")
print("=" * 70)

