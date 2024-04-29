"""Asynchronous Python client for the WAQI API."""

from __future__ import annotations

from typing import Any, TypeVar

from .const import LOGGER

_EnumT = TypeVar("_EnumT")


def to_nullable_enum(
    enum_class: type[_EnumT],
    value: Any,
) -> _EnumT | None:
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
