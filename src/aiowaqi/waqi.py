"""Asynchronous Python client for the WAQI API."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, cast

from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET
import async_timeout
from yarl import URL

from .exceptions import (
    WAQIAuthenticationError,
    WAQIConnectionError,
    WAQIError,
    WAQIUnknownCityError,
    WAQIUnknownStationError,
)
from .models import WAQIAirQuality, WAQISearchResult

if TYPE_CHECKING:
    from typing_extensions import Self


@dataclass
class WAQIClient:
    """Main class for handling connections with WAQI."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "api.waqi.info"
    _token: str | None = None
    _close_session: bool = False

    def authenticate(self, token: str) -> None:
        """Authenticate the user with a token."""
        self._token = token

    async def _request(
        self,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a request to WAQI.

        A generic method for sending/handling HTTP requests done against
        WAQI.

        Args:
        ----
            uri: the path to call.
            data: the query parameters to add.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the API.

        Raises:
        ------
            WAQIConnectionError: An error occurred while communicating with
                the WAQI API.
            WAQIError: Received an unexpected response from the WAQI API.
            WAQIAuthenticationError: Used token is invalid.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
        ).joinpath(uri)

        headers = {
            "User-Agent": f"WAQIAsync/{version}",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        if data is None:  # pragma: no cover
            data = {}
        data["token"] = self._token
        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    str(url.with_query(data)).replace("search", "search/"),
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the WAQI API"
            raise WAQIConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from the WAQI API"
            raise WAQIError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        response_data = cast(dict[str, Any], await response.json())
        if (
            response_data["status"] == "error"
            and response_data["data"] == "Invalid key"
        ):
            raise WAQIAuthenticationError
        return response_data

    async def get_by_city(self, city: str) -> WAQIAirQuality:
        """Get air quality information for a given city."""
        response = await self._request(f"feed/{city}")
        if response["status"] == "error" and response["data"] == "Unknown station":
            msg = f"Could not find city {city}"
            raise WAQIUnknownCityError(msg)
        return WAQIAirQuality.from_dict(response["data"])

    async def get_by_name(self, name: str) -> WAQIAirQuality:
        """Get air quality measuring station by name."""
        response = await self._request(f"feed/{name}")
        data = response["data"]
        if (
            response["status"] == "error"
            and data in ("Unknown station", "no such station")
        ) or (
            "status" in data
            and data["status"] == "error"
            and data["msg"] == "Unknown ID"
        ):
            msg = f"Could not find station {name}"
            raise WAQIUnknownStationError(msg)
        return WAQIAirQuality.from_dict(data)

    async def get_by_station_number(self, station_number: int) -> WAQIAirQuality:
        """Get air quality measuring station by station number."""
        return await self.get_by_name(f"@{station_number}")

    async def get_by_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> WAQIAirQuality:
        """Get nearest air quality measuring station by coordinates."""
        response = await self._request(f"feed/geo:{latitude};{longitude}")
        return WAQIAirQuality.from_dict(response["data"])

    async def get_by_ip(
        self,
    ) -> WAQIAirQuality:
        """Get the nearest air quality measuring station according to WAQI."""
        return await self.get_by_name("here")

    async def search(self, keyword: str) -> list[WAQISearchResult]:
        """Search for stations with a keyword."""
        response = await self._request("search/", data={"keyword": keyword})
        return [WAQISearchResult.from_dict(station) for station in response["data"]]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The WAQIClient object.
        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
