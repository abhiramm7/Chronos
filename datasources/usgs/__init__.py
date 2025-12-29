"""USGS data fetching module for hydrological time series data.

This module provides a simplified API with 3 main functions:
1. normalize_site_id() - Clean up site ID format
2. get_gauge_fields() - Get available fields for a gauge
3. get_gauge_data() - Fetch time series data
"""

# Simplified Functional Interface
from .fetch_data_functional import (
    normalize_site_id,
    get_gauge_fields,
    get_gauge_data,
    PARAMETER_CODES,
)

__all__ = [
    'normalize_site_id',
    'get_gauge_fields',
    'get_gauge_data',
    'PARAMETER_CODES',
]

