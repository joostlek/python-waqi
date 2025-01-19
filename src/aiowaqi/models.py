"""Asynchronous Python client for the WAQI API."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from aiowaqi import converters
from aiowaqi.util import to_nullable_enum


class Pollutant(StrEnum):
    """Enum of pollutants."""

    CARBON_MONOXIDE = "co"
    NITROGEN_DIOXIDE = "no2"
    OZONE = "o3"
    SULFUR_DIOXIDE = "so2"
    PM10 = "pm10"
    PM25 = "pm25"
    NEPHELOMETRY = "neph"


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
    carbon_monoxide_concentration: float | None
    humidity: float | None
    nephelometry: float | None
    nitrogen_dioxide: float | None
    nitrogen_dioxide_concentration: int | None
    ozone: float | None
    ozone_concentration: int | None
    pressure: float | None
    sulfur_dioxide: float | None
    pm10: float | None
    pm10_concentration: int | None
    pm25: float | None
    pm25_concentration: float | None
    temperature: float | None

    @classmethod
    def from_dict(cls, air_quality: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        pm25 = air_quality.get("pm25", {}).get("v")
        pm10 = air_quality.get("pm10", {}).get("v")
        co = air_quality.get("co", {}).get("v")
        o3 = air_quality.get("o3", {}).get("v")
        no2 = air_quality.get("no2", {}).get("v")

        co_concentration = converters.aqi_to_co(co) if co is not None else None
        o3_concentration = converters.aqi_to_o3_8h(o3) if o3 is not None else None
        no2_concentration = converters.aqi_to_no2(no2) if no2 is not None else None
        pm10_concentration = converters.aqi_to_pm10(pm10) if pm10 is not None else None
        pm25_concentration = converters.aqi_to_pm25(pm25) if pm25 is not None else None

        return cls(
            carbon_monoxide=co,
            humidity=air_quality.get("h", {}).get("v"),
            nephelometry=air_quality.get("neph", {}).get("v"),
            nitrogen_dioxide=no2,
            ozone=o3,
            pressure=air_quality.get("p", {}).get("v"),
            sulfur_dioxide=air_quality.get("so2", {}).get("v"),
            pm10=pm10,
            pm25=pm25,
            temperature=air_quality.get("t", {}).get("v"),
            carbon_monoxide_concentration=co_concentration,
            ozone_concentration=o3_concentration,
            nitrogen_dioxide_concentration=no2_concentration,
            pm10_concentration=pm10_concentration,
            pm25_concentration=pm25_concentration,
        )


@dataclass(slots=True)
class WAQIAirQuality:
    """Represents the air quality data from WAQI."""

    air_quality_index: int | None
    station_id: int
    attributions: list[Attribution]
    city: City
    extended_air_quality: WAQIExtendedAirQuality
    dominant_pollutant: Pollutant | None
    measured_at: datetime | None

    @classmethod
    def from_dict(cls, air_quality: dict[str, Any]) -> Self:
        """Initialize from a dict."""
        aqi = None
        with suppress(ValueError):
            aqi = int(air_quality["aqi"])

        dominant_pollutant = air_quality["dominentpol"]
        if dominant_pollutant == "":
            dominant_pollutant = None
        else:
            dominant_pollutant = to_nullable_enum(Pollutant, air_quality["dominentpol"])

        measured_at: datetime | None = None
        if "iso" in air_quality["time"]:
            measured_at = datetime.fromisoformat(air_quality["time"]["iso"])

        return cls(
            air_quality_index=aqi,
            station_id=air_quality["idx"],
            attributions=[
                Attribution.from_dict(attribution)
                for attribution in air_quality["attributions"]
            ],
            city=City.from_dict(air_quality["city"]),
            extended_air_quality=WAQIExtendedAirQuality.from_dict(air_quality["iaqi"]),
            dominant_pollutant=dominant_pollutant,
            measured_at=measured_at,
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
