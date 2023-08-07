"""Tests for the WAQI Library."""

import aiohttp
import pytest
from aresponses import ResponsesMockServer
from syrupy import SnapshotAssertion

from aiowaqi import WAQIAirQuality, WAQIClient

from . import load_fixture

WAQI_URL = "api.waqi.info"


@pytest.mark.parametrize(
    "city",
    [
        "utrecht",
        "maarssen",
        "klundert",
        "failing_klundert",
    ],
)
async def test_states(
    aresponses: ResponsesMockServer,
    city: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving states."""
    aresponses.add(
        WAQI_URL,
        f"/feed/{city}",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"city_feed_{city}.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        waqi = WAQIClient(session=session)
        response: WAQIAirQuality = await waqi.get_by_city(city)
        assert response == snapshot
        await waqi.close()
