"""Tests for the WAQI Library."""
from __future__ import annotations

import asyncio
from dataclasses import asdict

import aiohttp
from aiohttp.web_request import BaseRequest
from aresponses import Response, ResponsesMockServer
import pytest
from syrupy import SnapshotAssertion

from aiowaqi import (
    WAQIAirQuality,
    WAQIAuthenticationError,
    WAQIClient,
    WAQIConnectionError,
    WAQIError,
    WAQISearchResult,
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
        assert asdict(response) == snapshot
        await waqi.close()


async def test_new_dominant_pol(
    aresponses: ResponsesMockServer,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test retrieving new dominant pol."""
    aresponses.add(
        WAQI_URL,
        "/feed/maarssen?token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("city_feed_new_dominant_pol.json"),
        ),
        match_querystring=True,
    )
    async with aiohttp.ClientSession() as session:
        waqi = WAQIClient(session=session)
        waqi.authenticate("test")
        await waqi.get_by_city("maarssen")
        assert (
            "h is an unsupported value for <enum 'Pollutant'>,"
            " please report this at https://github.com/joostlek/python-waqi/issues"
            in caplog.text
        )
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
        response: list[WAQISearchResult] = await waqi.search(keyword)
        res = [asdict(wsr) for wsr in response]
        assert res == snapshot


@pytest.mark.parametrize(
    "identifier",
    [
        "@6337",
        "@372382",
        "A123946",
        "klundert",
        "failing_klundert",
    ],
)
async def test_get_by_identifier(
    aresponses: ResponsesMockServer,
    identifier: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting stations by identifier."""
    aresponses.add(
        WAQI_URL,
        f"/feed/{identifier}?token=test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"identifier_{identifier}.json"),
        ),
        match_querystring=True,
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        response = await waqi.get_by_identifier(identifier)
        assert asdict(response) == snapshot


@pytest.mark.parametrize(
    "identifier",
    [
        "unknown",
        "@123946",
    ],
)
async def test_get_unknown_station_by_identifier(
    aresponses: ResponsesMockServer,
    identifier: str,
) -> None:
    """Test getting unknown station by identifier."""
    aresponses.add(
        WAQI_URL,
        f"/feed/{identifier}",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture(f"identifier_{identifier}.json"),
        ),
    )
    async with WAQIClient() as waqi:
        waqi.authenticate("test")
        with pytest.raises(WAQIUnknownStationError):
            await waqi.get_by_identifier(identifier)


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
        assert asdict(response) == snapshot


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
        assert asdict(response) == snapshot
