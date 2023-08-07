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
