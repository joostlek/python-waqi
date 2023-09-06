"""Asynchronous Python client for the WAQI API."""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from aiowaqi.util import to_enum


class Pollutant(StrEnum):
    """Enum of pollutants."""

    UNKNOWN = "unknown"
    CARBON_MONOXIDE = "co"
    NITROGEN_DIOXIDE = "no2"
    OZONE = "o3"
    SULFUR_DIOXIDE = "so2"
    PM10 = "pm10"
    PM25 = "pm25"


@dataclass(slots=True)
class Attribution:
    """Represents an attribution."""

    url: str
    name: str
    logo: str | None

    @classmethod
    def from_dict(cls, attribution: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        return cls(
            url=attribution["url"],
            name=attribution["name"].strip(),
            logo=attribution.get("logo"),
        )


@dataclass(slots=True)
class Coordinates:
    """Represents coordinates."""

    latitude: float
    longitude: float


@dataclass(slots=True)
class Location:
    """Represents a location object."""

    external_url: str
    name: str
    coordinates: Coordinates

    @classmethod
    def from_dict(cls, location: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        return cls(
            external_url=location["url"],
            name=location["name"],
            coordinates=Coordinates(
                latitude=location["geo"][0],
                longitude=location["geo"][1],
            ),
        )


@dataclass(slots=True)
class City(Location):
    """Represents a city object."""

    location: str | None

    @classmethod
    def from_dict(cls, location: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        loc = location["location"]
        if not loc:
            loc = None
        return cls(
            external_url=location["url"],
            name=location["name"],
            coordinates=Coordinates(
                latitude=location["geo"][0],
                longitude=location["geo"][1],
            ),
            location=loc,
        )


@dataclass(slots=True)
class Station(Location):
    """Represents a station object."""


@dataclass(slots=True)
class WAQIExtendedAirQuality:
    """Represents extended air quality data."""

    carbon_monoxide: float | None
    humidity: float | None
    nitrogen_dioxide: float | None
    ozone: float | None
    pressure: float | None
    sulfur_dioxide: float | None
    pm10: float | None
    pm25: float | None
    temperature: float | None

    @classmethod
    def from_dict(cls, air_quality: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        return cls(
            carbon_monoxide=air_quality.get("co", {}).get("v"),
            humidity=air_quality.get("h", {}).get("v"),
            nitrogen_dioxide=air_quality.get("no2", {}).get("v"),
            ozone=air_quality.get("o3", {}).get("v"),
            pressure=air_quality.get("p", {}).get("v"),
            sulfur_dioxide=air_quality.get("so2", {}).get("v"),
            pm10=air_quality.get("pm10", {}).get("v"),
            pm25=air_quality.get("pm25", {}).get("v"),
            temperature=air_quality.get("t", {}).get("v"),
        )


@dataclass(slots=True)
class WAQIAirQuality:
    """Represents the air quality data from WAQI."""

    air_quality_index: int | None
    station_id: int
    attributions: list[Attribution]
    city: City
    extended_air_quality: WAQIExtendedAirQuality
    dominant_pollutant: Pollutant
    measured_at: datetime

    @classmethod
    def from_dict(cls, air_quality: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        aqi = None
        with suppress(ValueError):
            aqi = int(air_quality["aqi"])

        return cls(
            air_quality_index=aqi,
            station_id=air_quality["idx"],
            attributions=[
                Attribution.from_dict(attribution)
                for attribution in air_quality["attributions"]
            ],
            city=City.from_dict(air_quality["city"]),
            extended_air_quality=WAQIExtendedAirQuality.from_dict(air_quality["iaqi"]),
            dominant_pollutant=to_enum(
                Pollutant,
                air_quality["dominentpol"],
                Pollutant.UNKNOWN,
            ),
            measured_at=datetime.fromisoformat(air_quality["time"]["iso"]),
        )


@dataclass(slots=True)
class WAQISearchResult:
    """Represents a search result from the WAQI api."""

    air_quality_index: int | None
    station_id: int
    station: Station

    @classmethod
    def from_dict(cls, result: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        aqi = None
        with suppress(ValueError):
            aqi = int(result["aqi"])

        return cls(
            air_quality_index=aqi,
            station_id=result["uid"],
            station=Station.from_dict(result["station"]),
        )
