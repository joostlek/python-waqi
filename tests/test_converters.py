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
    assert aqi_to_pm25(75) == 23.8
    assert aqi_to_pm25(150) == 55.5
    assert aqi_to_pm25(300) == 250.5
    assert aqi_to_pm25(400) == 350.5
    assert aqi_to_pm25(500) == 500.5


def test_pm10_conversion() -> None:
    """Test PM10 AQI to concentration conversion."""
    assert aqi_to_pm10(0) == 0
    assert aqi_to_pm10(75) == 105
    assert aqi_to_pm10(150) == 255
    assert aqi_to_pm10(155) == 265
    assert aqi_to_pm10(300) == 425
    assert aqi_to_pm10(400) == 505
    assert aqi_to_pm10(500) == 605


def test_co_conversion() -> None:
    """Test CO AQI to concentration conversion."""
    assert aqi_to_co(0) == 0.0
    assert aqi_to_co(75) == 7.0
    assert aqi_to_co(150) == 12.5
    assert aqi_to_co(175) == 14.0
    assert aqi_to_co(300) == 30.5
    assert aqi_to_co(400) == 40.5
    assert aqi_to_co(500) == 50.5


def test_o3_8h_conversion() -> None:
    """Test 8-hour Ozone AQI to concentration conversion."""
    assert aqi_to_o3_8h(0) == 0
    assert aqi_to_o3_8h(66) == 0.065
    assert aqi_to_o3_8h(123) == 0.085
    assert aqi_to_o3_8h(172) == 0.105
    assert aqi_to_o3_8h(240) == 0.220
    assert aqi_to_o3_8h(300) == 0.375

    with pytest.raises(ValueError, match="For AQI > 300, use 1-hour Ozone values"):
        aqi_to_o3_8h(301)


def test_o3_1h_conversion() -> None:
    """Test 1-hour Ozone AQI to concentration conversion."""
    with pytest.raises(ValueError, match="For AQI <= 100, use 8-hour Ozone values"):
        aqi_to_o3_1h(75)

    assert aqi_to_o3_1h(125) == 0.145
    assert aqi_to_o3_1h(175) == 0.185
    assert aqi_to_o3_1h(250) == 0.305
    assert aqi_to_o3_1h(400) == 0.505
    assert aqi_to_o3_1h(500) == 0.605


def test_no2_conversion() -> None:
    """Test NO2 AQI to concentration conversion."""
    assert aqi_to_no2(0) == 0
    assert aqi_to_no2(40) == 0.043
    assert aqi_to_no2(55) == 0.059
    assert aqi_to_no2(120) == 0.205
    assert aqi_to_no2(175) == 0.506
    assert aqi_to_no2(250) == 0.95
    assert aqi_to_no2(350) == 1.45
    assert aqi_to_no2(450) == 1.849
    assert aqi_to_no2(500) == 2.049


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
        aqi_to_o3_8h(400)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_o3_1h(aqi)
    with pytest.raises(ValueError, match="AQI out of range"):
        aqi_to_no2(aqi)
