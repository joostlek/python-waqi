"""Asynchronous Python client for the WAQI API."""


class WAQIError(Exception):
    """Generic exception."""


class WAQIConnectionError(WAQIError):
    """WAQI connection exception."""


class WAQIUnknownCityError(WAQIError):
    """WAQI unknown city exception."""


class WAQIAuthenticationError(WAQIError):
    """WAQI authentication exception."""
