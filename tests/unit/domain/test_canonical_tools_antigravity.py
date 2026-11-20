"""Pure decisions about which Antigravity settings cover a catalog."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spec_dock.runtime.domain.canonical_tools import antigravity_allows, antigravity_setting_line

CATALOG = Path("/repo/spec-dock/.canonical")


@pytest.mark.parametrize(
    ("allow", "configured"),
    [
        ([], False),
        (["read_file(/repo)", "write_file(/repo/spec-dock/.canonical)"], True),
        (["write_file(/repo)"], False),
        (["read_file(/repo)", "write_file(/repo-other)"], False),
        (["read_file(/repo)", "write_file(/repo/spec-dock/.canonical/child)"], False),
        (["read_file(/repo)", "write_file(~/repo)"], False),
        (["read_file(/repo)", "write_file(repo)"], False),
        (["read_file(/repo)", "write_file(/*)"], False),
        (["read_file(*)", "write_file(*)"], False),
        (["read_file()", "write_file"], False),
        (["read_file(/repo)", "command(/repo)"], False),
    ],
)
def test_both_actions_must_cover_the_catalog(allow: list[str], configured: bool) -> None:
    assert antigravity_allows({"permissions": {"allow": allow}}, CATALOG) is configured


def test_paths_are_normalized_and_aliases_are_resolved() -> None:
    payload = {
        "permissions": {
            "allow": ["read_file(/alias/unused/..)", "write_file(/repo)"],
            "deny": ["read_file(/other)"],
            "ask": ["write_file(/repo/spec-dock/.canonical/child)"],
        },
    }
    assert (
        antigravity_allows(payload, CATALOG, resolve=lambda path: Path("/repo") if path == Path("/alias") else path)
        is True
    )


@pytest.mark.parametrize(
    ("policy", "rule"),
    [
        ("deny", "read_file(*)"),
        ("ask", "write_file(/some/*)"),
        ("deny", "read_file(~/x)"),
        ("ask", "write_file(relative/path)"),
        ("deny", "read_file()"),
        ("ask", "write_file"),
        ("deny", "read_file(relative/path)"),
    ],
)
def test_deny_or_ask_with_an_ambiguous_file_target_is_unknown(policy: str, rule: str) -> None:
    payload = {"permissions": {"allow": ["read_file(/repo)", "write_file(/repo)"], policy: [rule]}}
    assert antigravity_allows(payload, CATALOG) is None


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {"permissions": False},
        {"permissions": {"allow": 42}},
        {"permissions": {"ask": "read_file(/repo)"}},
        {"permissions": {"deny": [None]}},
    ],
)
def test_invalid_settings_shape_is_unknown(payload: object) -> None:
    assert antigravity_allows(payload, CATALOG) is None


def test_setting_line_is_valid_json_with_unescaped_japanese_and_escaped_quotes() -> None:
    catalog = Path('/repo/仕様 "draft"')
    line = antigravity_setting_line(catalog)
    assert "仕様" in line
    assert json.loads(line) == {"permissions": {"allow": [f"read_file({catalog})", f"write_file({catalog})"]}}
