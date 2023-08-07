"""Tests for the WAQI Library."""
import asyncio

import aiohttp
import pytest
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer
from syrupy import SnapshotAssertion

from aiowaqi import (
    WAQIAirQuality,
    WAQIAuthenticationError,
    WAQIClient,
    WAQIConnectionError,
    WAQIError,
    WAQIUnknownStationError,
)

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
async def test_by_city(
    aresponses: ResponsesMockServer,
    city: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving air quality by city."""
    aresponses.add(
        WAQI_URL,
        f"/feed/{city}?token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"city_feed_{city}.json"),
        ),
        match_querystring=True,
    )
    async with aiohttp.ClientSession() as session:
        waqi = WAQIClient(session=session)
        waqi.authenticate("test")
        response: WAQIAirQuality = await waqi.get_by_city(city)
        assert response == snapshot
        await waqi.close()


async def test_own_session(
    aresponses: ResponsesMockServer,
) -> None:
    """Test creating own session."""
    aresponses.add(
        WAQI_URL,
        "/feed/utrecht",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("city_feed_utrecht.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        await waqi.get_by_city("utrecht")
        assert waqi.session is not None


async def test_unexpected_server_response(
    aresponses: ResponsesMockServer,
) -> None:
    """Test handling unexpected response."""
    aresponses.add(
        WAQI_URL,
        "/feed/utrecht",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "plain/text"},
            text="Yes",
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIError):
            assert await waqi.get_by_city("utrecht")


async def test_unknown_city(
    aresponses: ResponsesMockServer,
) -> None:
    """Test unknown city."""
    aresponses.add(
        WAQI_URL,
        "/feed/unknown",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("city_feed_unknown.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIError):
            assert await waqi.get_by_city("unknown")


async def test_unauthenticated(
    aresponses: ResponsesMockServer,
) -> None:
    """Test unauthenticated."""
    aresponses.add(
        WAQI_URL,
        "/feed/utrecht",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("unauthenticated.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIAuthenticationError):
            assert await waqi.get_by_city("utrecht")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: BaseRequest) -> Response:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(
        WAQI_URL,
        "/feed/utrecht",
        "GET",
        response_handler,
    )
    async with aiohttp.ClientSession() as session:
        waqi = WAQIClient(session=session, request_timeout=1)
        waqi.authenticate("test")
        with pytest.raises(WAQIConnectionError):
            assert await waqi.get_by_city("utrecht")
        await waqi.close()


@pytest.mark.parametrize(
    "keyword",
    [
        "klundert",
        "failing_klundert",
        "unknown",
    ],
)
async def test_search(
    aresponses: ResponsesMockServer,
    keyword: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test searching stations."""
    aresponses.add(
        WAQI_URL,
        f"/search/?keyword={keyword}&token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"search_{keyword}.json"),
        ),
        match_querystring=True,
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.search(keyword)
        assert response == snapshot


@pytest.mark.parametrize(
    "name",
    [
        "klundert",
        "failing_klundert",
    ],
)
async def test_get_by_name(
    aresponses: ResponsesMockServer,
    name: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting stations by name."""
    aresponses.add(
        WAQI_URL,
        f"/feed/{name}?token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"name_feed_{name}.json"),
        ),
        match_querystring=True,
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.get_by_name(name)
        assert response == snapshot


async def test_get_unknown_by_name(
    aresponses: ResponsesMockServer,
) -> None:
    """Test getting unknown station by name."""
    aresponses.add(
        WAQI_URL,
        "/feed/unknown",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("name_feed_unknown.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIUnknownStationError):
            await waqi.get_by_name("unknown")


@pytest.mark.parametrize(
    "station_number",
    [
        6337,
    ],
)
async def test_get_by_station_number(
    aresponses: ResponsesMockServer,
    station_number: int,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting stations by station_number."""
    aresponses.add(
        WAQI_URL,
        f"/feed/@{station_number}?token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"station_number_feed_{station_number}.json"),
        ),
        match_querystring=True,
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.get_by_station_number(station_number)
        assert response == snapshot


async def test_get_unknown_by_station_number(
    aresponses: ResponsesMockServer,
) -> None:
    """Test getting unknown station by station_number."""
    aresponses.add(
        WAQI_URL,
        "/feed/@0",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("station_number_feed_unknown.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIUnknownStationError):
            await waqi.get_by_station_number(0)


async def test_get_by_coordinates(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting measuring station via coordinates."""
    aresponses.add(
        WAQI_URL,
        "/feed/geo:52.105031;5.124464",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("coordinates.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.get_by_coordinates(52.105031, 5.124464)
        assert response == snapshot


async def test_get_by_ip(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting measuring station via ip."""
    aresponses.add(
        WAQI_URL,
        "/feed/here",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("here.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.get_by_ip()
        assert response == snapshot
