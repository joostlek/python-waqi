"""Fixtures for the aiowaqi package."""

from typing import AsyncGenerator

import aiohttp
import pytest

from aiowaqi import WAQIClient
from syrupy import SnapshotAssertion

from .syrupy import WAQISnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the WAQI extension."""
    return snapshot.use_extension(WAQISnapshotExtension)


@pytest.fixture(name="waqi_client")
async def client() -> AsyncGenerator[WAQIClient, None]:
    """Return a WAQI client."""
    async with aiohttp.ClientSession() as session, WAQIClient(
        session=session,
    ) as waqi_client:
        yield waqi_client


@pytest.fixture(name="authenticated_client")
async def authenticated_client(
    waqi_client: WAQIClient,
) -> WAQIClient:
    """Return an authenticated WAQI client."""
    waqi_client.authenticate("test")
    return waqi_client
