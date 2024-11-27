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
    "Attribution",
    "City",
    "Coordinates",
    "Location",
    "WAQIAirQuality",
    "WAQIAuthenticationError",
    "WAQIClient",
    "WAQIConnectionError",
    "WAQIError",
    "WAQIExtendedAirQuality",
    "WAQISearchResult",
    "WAQIUnknownCityError",
    "WAQIUnknownStationError",
]
