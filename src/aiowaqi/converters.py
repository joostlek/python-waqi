"""Conversion functions for AQI values."""


def inv_linear(
    aqi_high: float,
    aqi_low: float,
    conc_high: float,
    conc_low: float,
    aqi: float,
) -> float:
    """Calculate concentration value using linear interpolation.

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


def to_int(value: float) -> int:
    """Round a float to an integer (forces casting to int)."""
    return int(round(value, 0))


def aqi_to_pm25(aqi: float) -> float:
    """Convert AQI to PM2.5 concentration (μg/m3)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    precision = 1

    if 0 <= aqi <= 50:
        return round(inv_linear(50, 0, 9.0, 0, aqi), precision)
    if 51 <= aqi <= 100:
        return round(inv_linear(100, 51, 35.4, 9.1, aqi), precision)
    if 101 <= aqi <= 150:
        return round(inv_linear(150, 101, 55.4, 35.5, aqi), precision)
    if 151 <= aqi <= 200:
        return round(inv_linear(200, 151, 125.4, 55.5, aqi), precision)
    if 201 <= aqi <= 300:
        return round(inv_linear(300, 201, 225.4, 125.5, aqi), precision)
    if 301 <= aqi <= 500 or aqi > 500:
        return round(inv_linear(500, 301, 325.4, 225.5, aqi), precision)

    msg = "AQI out of range"
    raise ValueError(msg)


def aqi_to_pm10(aqi: float) -> int:
    """Convert AQI to PM10 concentration (μg/m3)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if 0 <= aqi <= 50:
        return to_int(inv_linear(50, 0, 54, 0, aqi))
    if 51 <= aqi <= 100:
        return to_int(inv_linear(100, 51, 154, 55, aqi))
    if 101 <= aqi <= 150:
        return to_int(inv_linear(150, 101, 254, 155, aqi))
    if 151 <= aqi <= 200:
        return to_int(inv_linear(200, 151, 354, 255, aqi))
    if 201 <= aqi <= 300:
        return to_int(inv_linear(300, 201, 424, 355, aqi))
    if 301 <= aqi <= 500 or aqi > 500:
        return to_int(inv_linear(500, 301, 604, 425, aqi))

    msg = "AQI out of range"
    raise ValueError(msg)


def aqi_to_co(aqi: float) -> float:
    """Convert AQI to CO concentration (ppm)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    precision = 1

    if 0 <= aqi <= 50:
        return round(inv_linear(50, 0, 4.4, 0, aqi), precision)
    if 51 <= aqi <= 100:
        return round(inv_linear(100, 51, 9.4, 4.5, aqi), precision)
    if 101 <= aqi <= 150:
        return round(inv_linear(150, 101, 12.4, 9.5, aqi), precision)
    if 151 <= aqi <= 200:
        return round(inv_linear(200, 151, 15.4, 12.5, aqi), precision)
    if 201 <= aqi <= 300:
        return round(inv_linear(300, 201, 30.4, 15.5, aqi), precision)
    if 301 <= aqi <= 500 or aqi > 500:
        return round(inv_linear(500, 301, 50.4, 30.5, aqi), precision)

    msg = "AQI out of range"
    raise ValueError(msg)


def aqi_to_o3_8h(aqi: float) -> int:
    """Convert AQI to 8-hour Ozone concentration (ppb)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if 0 <= aqi <= 50:
        return to_int(inv_linear(50, 0, 54, 0, aqi))
    if 51 <= aqi <= 100:
        return to_int(inv_linear(100, 51, 70, 55, aqi))
    if 101 <= aqi <= 150:
        return to_int(inv_linear(150, 101, 85, 71, aqi))
    if 151 <= aqi <= 200:
        return to_int(inv_linear(200, 151, 105, 86, aqi))
    if 201 <= aqi <= 300:
        return to_int(inv_linear(300, 201, 200, 106, aqi))

    msg = "For AQI > 300, use 1-hour Ozone values"
    raise ValueError(msg)


def aqi_to_o3_1h(aqi: float) -> int:
    """Convert AQI to 1-hour Ozone concentration (ppb)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if aqi <= 100:
        msg = "For AQI <= 100, use 8-hour Ozone values"
        raise ValueError(msg)
    if 101 <= aqi <= 150:
        return to_int(inv_linear(150, 101, 164, 125, aqi))
    if 151 <= aqi <= 200:
        return to_int(inv_linear(200, 151, 204, 165, aqi))
    if 201 <= aqi <= 300:
        return to_int(inv_linear(300, 201, 404, 205, aqi))
    if aqi > 300:
        return to_int(inv_linear(500, 301, 604, 404, aqi))

    msg = "AQI out of range"
    raise ValueError(msg)


def aqi_to_no2(aqi: float) -> int:
    """Convert AQI to NO2 concentration (ppb)."""
    if not isinstance(aqi, (int | float)) or aqi < 0:
        msg = "AQI must be a non-negative number"
        raise ValueError(msg)

    if 0 <= aqi <= 50:
        return to_int(inv_linear(50, 0, 53, 0, aqi))
    if 51 <= aqi <= 100:
        return to_int(inv_linear(100, 51, 100, 54, aqi))
    if 101 <= aqi <= 150:
        return to_int(inv_linear(150, 101, 360, 101, aqi))
    if 151 <= aqi <= 200:
        return to_int(inv_linear(200, 151, 649, 361, aqi))
    if 201 <= aqi <= 300:
        return to_int(inv_linear(300, 201, 1249, 650, aqi))
    if aqi > 300:
        return to_int(inv_linear(500, 301, 2049, 1250, aqi))

    msg = "AQI out of range"
    raise ValueError(msg)
