"""USGS data fetching module for hydrological time series data.

This module provides two interfaces:
1. Object-Oriented: USGSDataFetcher class
2. Functional: Pure functions with immutable data structures
"""

# Object-Oriented Interface
from .fetch_data import USGSDataFetcher

# Functional Interface
from .fetch_data_functional import (
    # Configuration
    create_site_config,
    SiteConfig,
    SiteInfo,
    NearbySite,

    # Data fetching
    fetch_streamflow,
    fetch_precipitation,
    fetch_temperature,
    fetch_all_data,

    # Site information
    get_site_info,
    check_data_availability,
    find_nearest_sites_with_precipitation,

    # Display functions
    display_data_sources,
    validate_and_display_site,

    # Constants
    PARAMETER_CODES,
)

__all__ = [
    # OOP Interface
    'USGSDataFetcher',

    # Functional Interface - Configuration
    'create_site_config',
    'SiteConfig',
    'SiteInfo',
    'NearbySite',

    # Functional Interface - Data fetching
    'fetch_streamflow',
    'fetch_precipitation',
    'fetch_temperature',
    'fetch_all_data',

    # Functional Interface - Site information
    'get_site_info',
    'check_data_availability',
    'find_nearest_sites_with_precipitation',

    # Functional Interface - Display
    'display_data_sources',
    'validate_and_display_site',

    # Constants
    'PARAMETER_CODES',
]

