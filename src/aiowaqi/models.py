"""Asynchronous Python client for the WAQI API."""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

try:
    from pydantic.v1 import BaseModel, Field, validator
except ImportError:  # pragma: no cover
    from pydantic import (  # type: ignore[assignment] # pragma: no cover
        BaseModel,
        Field,
        validator,
    )


class Pollutant(StrEnum):
    """Enum of pollutants."""

    CARBON_MONOXIDE = "co"
    NITROGEN_DIOXIDE = "no2"
    OZONE = "o3"
    SULFUR_DIOXIDE = "so2"
    PM10 = "pm10"
    PM25 = "pm25"


class Attribution(BaseModel):
    """Represents an attribution."""

    url: str = Field(...)
    name: str = Field(...)
    logo: str | None = Field(None)

    @validator(
        "name",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Strip name off attribution name."""
        return value.strip()


@dataclass
class Coordinates:
    """Represents coordinates."""

    latitude: float
    longitude: float


class Location(BaseModel):
    """Represents a location object."""

    external_url: str = Field(..., alias="url")
    name: str = Field(...)
    coordinates: Coordinates = Field(..., alias="geo")

    @validator(
        "coordinates",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def parse_coordinates(cls, value: list[float]) -> Coordinates:
        """Parse coordinates to object."""
        return Coordinates(
            latitude=value[0],
            longitude=value[1],
        )


class City(Location):
    """Represents a city object."""

    location: str | None = Field(...)

    @validator(
        "location",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def parse_location(cls, value: str) -> str | None:
        """Parse location to object."""
        if not value:
            return None
        return value


class Station(Location):
    """Represents a station object."""


class WAQIExtendedAirQuality(BaseModel):
    """Represents extended air quality data."""

    carbon_monoxide: float | None = Field(None, alias="co")
    humidity: float | None = Field(None, alias="h")
    nitrogen_dioxide: float | None = Field(None, alias="no2")
    ozone: float | None = Field(None, alias="o3")
    pressure: float | None = Field(None, alias="p")
    sulfur_dioxide: float | None = Field(None, alias="so2")
    pm10: float | None = Field(None)
    pm25: float | None = Field(None)
    temperature: float | None = Field(None, alias="t")

    @validator(
        "carbon_monoxide",
        "humidity",
        "nitrogen_dioxide",
        "ozone",
        "pressure",
        "sulfur_dioxide",
        "pm10",
        "pm25",
        "temperature",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def get_value(cls, value: dict[str, float]) -> float:
        """Get extra air quality value."""
        return value["v"]


class WAQIAirQuality(BaseModel):
    """Represents the air quality data from WAQI."""

    air_quality_index: int | None = Field(None, alias="aqi")
    station_id: int = Field(..., alias="idx")
    attributions: list[Attribution] = Field([])
    city: City = Field(...)
    extended_air_quality: WAQIExtendedAirQuality = Field(..., alias="iaqi")
    dominant_pollutant: Pollutant = Field(..., alias="dominentpol")
    measured_at: datetime = Field(..., alias="time")

    @validator(
        "air_quality_index",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def get_value(cls, value: int | str) -> int | None:
        """Handle invalid string."""
        with suppress(ValueError):
            return int(value)
        return None

    @validator(
        "measured_at",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def get_datetime(cls, value: dict[str, Any]) -> datetime:
        """Get measuring date."""
        return datetime.fromisoformat(value["iso"])


class WAQISearchResult(BaseModel):
    """Represents a search result from the WAQI api."""

    air_quality_index: int | None = Field(None, alias="aqi")
    station_id: int = Field(..., alias="uid")
    station: Station = Field(...)

    @validator(
        "air_quality_index",
        pre=True,
        allow_reuse=True,
    )
    @classmethod
    def get_value(cls, value: int | str) -> int | None:
        """Handle invalid string."""
        with suppress(ValueError):
            return int(value)
        return None


City.update_forward_refs()
WAQIExtendedAirQuality.update_forward_refs()
