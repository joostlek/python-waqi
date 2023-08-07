"""Asynchronous Python client for the WAQI API."""
import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import Any, cast

import async_timeout
from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .models import WAQIAirQuality
from .exceptions import WAQIConnectionError, WAQIError, WAQIAuthenticationError, WAQIUnknownCityError


@dataclass
class WAQIClient:
    """Main class for handling connections with WAQI."""

    session: ClientSession | None = None
    request_timeout: int = 10
    api_host: str = "api.waqi.info"
    _token: str | None = None
    _close_session: bool = False

    def authenticate(self, token: str) -> None:
        """Authenticate the user with a token"""
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
        version = "2.0.0"
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

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url.with_query(data),
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
        if response_data["status"] == "error":
            if response_data == "Invalid key":
                raise WAQIAuthenticationError()
        return response_data

    async def get_by_city(self, city: str) -> WAQIAirQuality:
        """Get air quality information for a given city."""
        response = await self._request(f"feed/{city}")
        if response["status"] == "error":
            if response["data"] == "Unknown station":
                raise WAQIUnknownCityError(f"Could not find city {city}")
        return WAQIAirQuality.parse_obj(response["data"])


    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> "WAQIClient":
        """Async enter.

        Returns
        -------
            The WAQIClient object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()