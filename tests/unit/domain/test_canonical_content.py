"""The canonical branch's own files and its format version (contract C5)."""

from __future__ import annotations

import json

import pytest

from spec_dock.runtime.domain.canonical_content import (
    CANONICAL_FORMAT,
    CANONICAL_ROOT_FILES,
    FORMAT_FILE,
    format_writable,
    read_format,
)


def test_format_one_has_exactly_the_marker_ignore_rules_and_readme() -> None:
    assert set(CANONICAL_ROOT_FILES) == {".spec-dock-canonical.json", ".gitignore", "README.md"}
    assert FORMAT_FILE == ".spec-dock-canonical.json"
    assert json.loads(CANONICAL_ROOT_FILES[FORMAT_FILE]) == {"format": 1}
    assert CANONICAL_ROOT_FILES[FORMAT_FILE] == b'{"format": 1}\n'
    assert CANONICAL_ROOT_FILES[".gitignore"] == (
        b".runtime/\n**/.workbench/*\n!**/.workbench/README.md\n**/.workbench/README.md/**\n"
    )
    readme = CANONICAL_ROOT_FILES["README.md"].decode("utf-8")
    assert "spec-dock/canonical" in readme and "spec-dock/initiatives/" in readme
    assert CANONICAL_FORMAT == 1


@pytest.mark.parametrize(
    ("payload", "version"),
    [
        (b'{"format": 1}\n', 1),
        (b'{"format": 2, "extra": true}', 2),
        (None, None),
        (b"", None),
        (b"not json", None),
        (b'{"format": "1"}', None),
        (b'{"format": true}', None),
        (b"[1]", None),
        (b"\xff", None),
    ],
)
def test_the_format_is_an_integer_or_unknown(payload: bytes | None, version: int | None) -> None:
    assert read_format(payload) == version


@pytest.mark.parametrize(("version", "writable"), [(1, True), (2, False), (0, False), (None, False)])
def test_only_known_formats_are_writable(version: int | None, writable: bool) -> None:
    assert format_writable(version) is writable
