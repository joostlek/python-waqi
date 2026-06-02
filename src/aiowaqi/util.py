"""Asynchronous Python client for the WAQI API."""

from __future__ import annotations

from typing import Any

from .const import LOGGER


def to_nullable_enum[EnumT](
    enum_class: type[EnumT],
    value: Any,
) -> EnumT | None:
    """Convert a value to an enum and log if it doesn't exist."""
    try:
        return enum_class(value)  # type: ignore[call-arg]
    except ValueError:
        LOGGER.warning(
            "%r is an unsupported value for %s, please report this at https://github.com/joostlek/python-waqi/issues",
            value,
            str(enum_class),
        )
        return None
