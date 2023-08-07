"""Tests for the WAQI Library."""
import asyncio

import aiohttp
import pytest
from aiohttp import BasicAuth, ClientError
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer
from syrupy import SnapshotAssertion
from src.aiowaqi import WAQIClient, WAQIAirQuality
from . import load_fixture

WAQI_URL = "api.waqi.info"


@pytest.mark.parametrize(
    "city",
    [
        "utrecht",
        "maarssen",
        "klundert",
        "failing_klundert",
    ]
)
async def test_states(
    aresponses: ResponsesMockServer,
        city: str,
    snapshot: SnapshotAssertion
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
