"""Asynchronous Python client for the WAQI API."""

from .exceptions import WAQIAuthenticationError, WAQIConnectionError, WAQIError
from .models import (
    Attribution,
    City,
    Coordinates,
    WAQIAirQuality,
    WAQIExtendedAirQuality,
)
from .waqi import WAQIClient

__all__ = [
    "WAQIError",
    "WAQIAuthenticationError",
    "WAQIClient",
    "WAQIConnectionError",
    "Attribution",
    "City",
    "Coordinates",
    "WAQIExtendedAirQuality",
    "WAQIAirQuality",
]
