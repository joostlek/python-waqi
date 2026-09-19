"""Tests for the WAQI Library."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from aiointercept import CallbackResult, aiointercept
import pytest

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

if TYPE_CHECKING:
    from yarl import URL

    from syrupy import SnapshotAssertion

WAQI_URL = "https://api.waqi.info"


@pytest.mark.parametrize(
    "city",
    [
        "utrecht",
        "maarssen",
        "klundert",
        "olivias",
        "failing_klundert",
    ],
)
async def test_by_city(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    city: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving air quality by city."""
    responses.get(
        f"{WAQI_URL}/feed/{city}?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture(f"city_feed_{city}.json"),
    )
    response: WAQIAirQuality = await authenticated_client.get_by_city(city)
    assert response == snapshot


async def test_new_dominant_pol(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test retrieving new dominant pol."""
    responses.get(
        f"{WAQI_URL}/feed/maarssen?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("city_feed_new_dominant_pol.json"),
    )
    await authenticated_client.get_by_city("maarssen")
    assert (
        "'h' is an unsupported value for <enum 'Pollutant'>,"
        " please report this at https://github.com/joostlek/python-waqi/issues"
        in caplog.text
    )


async def test_unknown_dominant_pol(
    responses: aiointercept,
    authenticated_client: WAQIClient,
) -> None:
    """Test retrieving unknown dominant pol."""
    responses.get(
        f"{WAQI_URL}/feed/maarssen?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("city_feed_unknown_dominant_pol.json"),
    )
    air_quality = await authenticated_client.get_by_city("maarssen")
    assert air_quality.dominant_pollutant is None


async def test_own_session(
    responses: aiointercept,
) -> None:
    """Test creating own session."""
    responses.get(
        f"{WAQI_URL}/feed/utrecht?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("city_feed_utrecht.json"),
    )
    async with WAQIClient() as waqi:
        assert waqi.session is None
        waqi.authenticate("test")
        await waqi.get_by_city("utrecht")
        assert waqi.session is not None


async def test_unexpected_server_response(
    authenticated_client: WAQIClient,
    responses: aiointercept,
) -> None:
    """Test handling unexpected response."""
    responses.get(
        f"{WAQI_URL}/feed/utrecht?token=test",
        status=200,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(WAQIError):
        assert await authenticated_client.get_by_city("utrecht")


async def test_unknown_city(
    authenticated_client: WAQIClient,
    responses: aiointercept,
) -> None:
    """Test unknown city."""
    responses.get(
        f"{WAQI_URL}/feed/unknown?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("city_feed_unknown.json"),
    )
    with pytest.raises(WAQIError):
        assert await authenticated_client.get_by_city("unknown")


async def test_unauthenticated(
    authenticated_client: WAQIClient,
    responses: aiointercept,
) -> None:
    """Test unauthenticated."""
    responses.get(
        f"{WAQI_URL}/feed/utrecht?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("unauthenticated.json"),
    )
    with pytest.raises(WAQIAuthenticationError):
        assert await authenticated_client.get_by_city("utrecht")


async def test_timeout(responses: aiointercept) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_url: URL, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.get(
        f"{WAQI_URL}/feed/utrecht?token=test",
        callback=response_handler,
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
    authenticated_client: WAQIClient,
    responses: aiointercept,
    keyword: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test searching stations."""
    responses.get(
        f"{WAQI_URL}/search/?keyword={keyword}&token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture(f"search_{keyword}.json"),
    )
    response: list[WAQISearchResult] = await authenticated_client.search(keyword)
    assert response == snapshot


@pytest.mark.parametrize(
    "name",
    [
        "klundert",
        "failing_klundert",
    ],
)
async def test_get_by_name(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    name: str,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting stations by name."""
    responses.get(
        f"{WAQI_URL}/feed/{name}?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture(f"name_feed_{name}.json"),
    )
    response = await authenticated_client.get_by_name(name)
    assert response == snapshot


async def test_get_unknown_by_name(
    authenticated_client: WAQIClient,
    responses: aiointercept,
) -> None:
    """Test getting unknown station by name."""
    responses.get(
        f"{WAQI_URL}/feed/unknown?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("name_feed_unknown.json"),
    )
    with pytest.raises(WAQIUnknownStationError):
        await authenticated_client.get_by_name("unknown")


@pytest.mark.parametrize(
    "station_number",
    [
        6337,
        372382,
        10142,
        10002,
    ],
)
async def test_get_by_station_number(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    station_number: int,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting stations by station_number."""
    responses.get(
        f"{WAQI_URL}/feed/@{station_number}?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture(f"station_number_feed_{station_number}.json"),
    )
    response = await authenticated_client.get_by_station_number(station_number)
    assert response == snapshot


@pytest.mark.parametrize(
    "identifier",
    [
        "unknown",
        "@123946",
        "A10142",
    ],
)
async def test_get_unknown_by_station_number(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    identifier: str,
) -> None:
    """Test getting unknown station by station_number."""
    responses.get(
        f"{WAQI_URL}/feed/@0?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture(f"station_number_feed_{identifier}.json"),
    )
    with pytest.raises(WAQIUnknownStationError):
        await authenticated_client.get_by_station_number(0)


async def test_get_by_coordinates(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting measuring station via coordinates."""
    responses.get(
        f"{WAQI_URL}/feed/geo:52.105031;5.124464?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("coordinates.json"),
    )
    response = await authenticated_client.get_by_coordinates(52.105031, 5.124464)
    assert response == snapshot


async def test_get_by_ip(
    authenticated_client: WAQIClient,
    responses: aiointercept,
    snapshot: SnapshotAssertion,
) -> None:
    """Test getting measuring station via ip."""
    responses.get(
        f"{WAQI_URL}/feed/here?token=test",
        status=200,
        headers={"Content-Type": "application/json"},
        body=load_fixture("here.json"),
    )
    response = await authenticated_client.get_by_ip()
    assert response == snapshot
