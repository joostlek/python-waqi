"""Test the converters module."""

import pytest

from aiowaqi.converters import (
    aqi_to_co,
    aqi_to_no2,
    aqi_to_o3_1h,
    aqi_to_o3_8h,
    aqi_to_pm10,
    aqi_to_pm25,
    inv_linear,
)


def test_invalid_aqi_values() -> None:
    """Test that invalid AQI values raise exceptions."""
    with pytest.raises(ValueError, match="AQI must be a non-negative number"):
        aqi_to_pm25(-1)

    with pytest.raises(ValueError, match="AQI must be a non-negative number"):
        aqi_to_pm25("not a number")  # type: ignore[arg-type]


def test_pm25_conversion() -> None:
    """Test PM2.5 AQI to concentration conversion."""
    assert aqi_to_pm25(0) == 0.0
    assert aqi_to_pm25(75) == 22.0
    assert aqi_to_pm25(150) == 55.4
    assert aqi_to_pm25(300) == 225.4
    assert aqi_to_pm25(400) == 275.2
    assert aqi_to_pm25(501) == 325.9


def test_pm10_conversion() -> None:
    """Test PM10 AQI to concentration conversion."""
    assert aqi_to_pm10(0) == 0
    assert aqi_to_pm10(75) == 103
    assert aqi_to_pm10(150) == 254
    assert aqi_to_pm10(155) == 263
    assert aqi_to_pm10(300) == 424
    assert aqi_to_pm10(400) == 514
    assert aqi_to_pm10(501) == 605


def test_co_conversion() -> None:
    """Test CO AQI to concentration conversion."""
    assert aqi_to_co(0) == 0.0
    assert aqi_to_co(75) == 6.9
    assert aqi_to_co(150) == 12.4
    assert aqi_to_co(175) == 13.9
    assert aqi_to_co(300) == 30.4
    assert aqi_to_co(400) == 40.4
    assert aqi_to_co(501) == 50.5


def test_o3_8h_conversion() -> None:
    """Test 8-hour Ozone AQI to concentration conversion."""
    assert aqi_to_o3_8h(0) == 0
    assert aqi_to_o3_8h(75) == 62
    assert aqi_to_o3_8h(150) == 85
    assert aqi_to_o3_8h(180) == 97
    assert aqi_to_o3_8h(250) == 153

    with pytest.raises(ValueError, match="For AQI > 300, use 1-hour Ozone values"):
        aqi_to_o3_8h(301)


def test_o3_1h_conversion() -> None:
    """Test 1-hour Ozone AQI to concentration conversion."""
    with pytest.raises(ValueError, match="For AQI <= 100, use 8-hour Ozone values"):
        aqi_to_o3_1h(75)

    assert aqi_to_o3_1h(125) == 144
    assert aqi_to_o3_1h(175) == 184
    assert aqi_to_o3_1h(250) == 303
    assert aqi_to_o3_1h(400) == 503
    assert aqi_to_o3_1h(501) == 605


def test_no2_conversion() -> None:
    """Test NO2 AQI to concentration conversion."""
    assert aqi_to_no2(0) == 0
    assert aqi_to_no2(75) == 77
    assert aqi_to_no2(150) == 360
    assert aqi_to_no2(180) == 531
    assert aqi_to_no2(300) == 1249
    assert aqi_to_no2(400) == 1647
    assert aqi_to_no2(501) == 2053


def test_invalid_ranges() -> None:
    """Test invalid AQI ranges."""
    for converter in [
        aqi_to_pm25,
        aqi_to_pm10,
        aqi_to_co,
        aqi_to_o3_8h,
        aqi_to_o3_1h,
        aqi_to_no2,
    ]:
        with pytest.raises(ValueError, match="AQI must be a non-negative number"):
            converter(-1)
        with pytest.raises(ValueError, match="AQI must be a non-negative number"):
            converter("invalid")  # type: ignore[arg-type]


def test_edge_cases() -> None:
    """Test edge cases and error conditions."""
    # Test inv_linear function directly
    assert inv_linear(100, 0, 100, 0, 50) == 50
    assert inv_linear(100, 0, 100, 0, 50) == 50.0

    aqi = float("nan")

    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_pm25(aqi)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_pm10(aqi)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_co(aqi)
    with pytest.raises(ValueError, match="For AQI > 300, use 1-hour Ozone values"):
        aqi_to_o3_8h(aqi)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_o3_1h(aqi)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_no2(aqi)
