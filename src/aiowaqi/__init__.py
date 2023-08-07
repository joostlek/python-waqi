"""Asynchronous Python client for the WAQI API."""

from .exceptions import (
    WAQIAuthenticationError,
    WAQIConnectionError,
    WAQIError,
    WAQIUnknownCityError,
    WAQIUnknownStationError,
)
from .models import (
    Attribution,
    City,
    Coordinates,
    Location,
    WAQIAirQuality,
    WAQIExtendedAirQuality,
    WAQISearchResult,
)
from .waqi import WAQIClient

__all__ = [
    "WAQIError",
    "WAQIUnknownStationError",
    "WAQIUnknownCityError",
    "Location",
    "WAQISearchResult",
    "WAQIAuthenticationError",
    "WAQIClient",
    "WAQIConnectionError",
    "Attribution",
    "City",
    "Coordinates",
    "WAQIExtendedAirQuality",
    "WAQIAirQuality",
]
