"""Conversion functions for AQI values."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class PollutantInfo:
    """Data structure for pollutant information."""

    unit: str
    name: str
    range: Sequence[int | None]
    scale: Sequence[float]


# AQI breakpoints and scales for different pollutants
POLLUTANT_DATA = {
    "pm25": PollutantInfo(
        unit="μg/m³",
        name="PM2.5",
        range=[0, 50, 100, 150, 200, 300, 400, 500],
        scale=[0, 12, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5],
    ),
    "pm10": PollutantInfo(
        unit="μg/m³",
        name="PM10",
        range=[0, 50, 100, 150, 200, 300, 400, 500],
        scale=[0, 55, 155, 255, 355, 425, 505, 605],
    ),
    "o3_1h": PollutantInfo(
        unit="ppb",
        name="O3 (1 hour average)",
        range=[None, 100, 150, 200, 300, 400, 500],
        scale=[0, 0.125, 0.165, 0.205, 0.405, 0.505, 0.605],
    ),
    "o3_8h": PollutantInfo(
        unit="ppb",
        name="O3 (8 hours average)",
        range=[0, 50, 100, 150, 200, 300, None],
        scale=[0, 0.06, 0.076, 0.096, 0.116, 0.375],
    ),
    "no2": PollutantInfo(
        unit="ppb",
        name="NO2",
        range=[0, 50, 100, 150, 200, 300, 400, 500],
        scale=[0, 0.054, 0.101, 0.361, 0.65, 1.25, 1.65, 2.049],
    ),
    "co": PollutantInfo(
        unit="ppm",
        name="CO",
        range=[0, 50, 100, 150, 200, 300, 400, 500],
        scale=[0, 4.5, 9.5, 12.5, 15.5, 30.5, 40.5, 50.5],
    ),
}


def inv_linear(
    aqi_high: float,
    aqi_low: float,
    conc_high: float,
    conc_low: float,
    aqi: float,
) -> float:
    """Calculate concentration value using linear interpolation.

    Inverted var l = o[s] + (t - i[s]) * (o[s + 1] - o[s]) / (i[s + 1] - i[s]);
    defined in https://aqicn.org/air-cache/calculator/dist/calculator.js

    Args:
        aqi_high: Upper AQI breakpoint
        aqi_low: Lower AQI breakpoint
        conc_high: Upper concentration breakpoint
        conc_low: Lower concentration breakpoint
        aqi: Input AQI value

    Returns:
        Calculated concentration value

    """
    return ((aqi - aqi_low) / (aqi_high - aqi_low)) * (conc_high - conc_low) + conc_low


def _convert_aqi_to_concentration(
    aqi: float, pollutant: str, precision: int = 1
) -> float:
    """Convert AQI to concentration."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    data = POLLUTANT_DATA[pollutant]
    ranges = data.range
    scales = data.scale

    for i in range(len(ranges) - 1):
        range_low, range_high = ranges[i], ranges[i + 1]
        scale_low, scale_high = scales[i], scales[i + 1]

        if range_low is None or range_high is None:
            continue

        if range_low <= aqi <= range_high:
            return round(
                inv_linear(range_high, range_low, scale_high, scale_low, aqi), precision
            )

    msg = "AQI out of range"
    raise ValueError(msg)


def aqi_to_pm25(aqi: float) -> float:
    """Convert AQI to PM2.5 concentration (μg/m3)."""
    return _convert_aqi_to_concentration(aqi, "pm25")


def aqi_to_pm10(aqi: float) -> int:
    """Convert AQI to PM10 concentration (μg/m3)."""
    return int(_convert_aqi_to_concentration(aqi, "pm10", 0))


def aqi_to_co(aqi: float) -> float:
    """Convert AQI to CO concentration (ppm)."""
    return _convert_aqi_to_concentration(aqi, "co")


def aqi_to_o3_8h(aqi: float) -> float:
    """Convert AQI to 8-hour Ozone concentration (ppb)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if aqi > 300:
        msg = "For AQI > 300, use 1-hour Ozone values"
        raise ValueError(msg)
    return _convert_aqi_to_concentration(aqi, "o3_8h", 3)


def aqi_to_o3_1h(aqi: float) -> float:
    """Convert AQI to 1-hour Ozone concentration (ppb)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if aqi <= 100:
        msg = "For AQI <= 100, use 8-hour Ozone values"
        raise ValueError(msg)

    return _convert_aqi_to_concentration(aqi, "o3_1h", 3)


def aqi_to_no2(aqi: float) -> float:
    """Convert AQI to NO2 concentration (ppb)."""
    return _convert_aqi_to_concentration(aqi, "no2", 3)
