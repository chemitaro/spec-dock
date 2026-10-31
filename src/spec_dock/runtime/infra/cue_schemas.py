"""Locate the CUE spec type versions shipped inside the package (contract K6 of epic-00425)."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
import re

_SCHEMA = re.compile(r"specdock/(v[1-9][0-9]*)")


def _root() -> Path:
    return Path(str(files("spec_dock").joinpath("cue")))


def schema_directory(schema: object) -> Path | None:
    """The package directory holding the type named by a `schema` value such as "specdock/v1"."""
    if not isinstance(schema, str):
        return None
    match = _SCHEMA.fullmatch(schema)
    if match is None:
        return None
    directory = _root() / match.group(1)
    return directory if directory.is_dir() else None


def shipped_schemas() -> tuple[str, ...]:
    """Every type version the package ships, in version order."""
    root = _root()
    if not root.is_dir():
        return ()
    names = [f"specdock/{entry.name}" for entry in root.iterdir() if entry.is_dir()]
    return tuple(sorted((name for name in names if schema_directory(name) is not None), key=_number))


def _number(schema: str) -> int:
    return int(schema.rsplit("/v", 1)[1])
