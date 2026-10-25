"""The one tool-setting line per tool and the read-only Claude Code check (Epic design ch. 9)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spec_dock.runtime.domain.canonical_tools import (
    CLAUDE_USER_SETTINGS_FILE,
    CODEX_CONFIG_FILE,
    CODEX_SECTION,
    claude_allows,
    claude_setting_line,
    codex_setting_line,
)

CATALOG = Path("/work/repo/spec-dock/.canonical")
HOME = Path("/home/me")
USER = HOME / ".claude/settings.json"
PROJECT = Path("/work/trees/feature/.claude/settings.local.json")


def test_each_tool_gets_exactly_one_line_with_the_catalog_path() -> None:
    assert codex_setting_line(CATALOG) == 'writable_roots = ["/work/repo/spec-dock/.canonical"]'
    assert claude_setting_line(CATALOG) == (
        '{ "permissions": { "additionalDirectories": ["/work/repo/spec-dock/.canonical"] } }'
    )
    assert json.loads(claude_setting_line(CATALOG)) == {"permissions": {"additionalDirectories": [str(CATALOG)]}}
    assert (CODEX_CONFIG_FILE, CODEX_SECTION, CLAUDE_USER_SETTINGS_FILE) == (
        "~/.codex/config.toml",
        "[sandbox_workspace_write]",
        "~/.claude/settings.json",
    )


def test_a_path_with_quotes_stays_one_valid_line() -> None:
    odd = Path('/work/"odd"/spec-dock/.canonical')
    assert codex_setting_line(odd) == 'writable_roots = ["/work/\\"odd\\"/spec-dock/.canonical"]'
    assert json.loads(claude_setting_line(odd))["permissions"]["additionalDirectories"] == [str(odd)]


@pytest.mark.parametrize(
    "directories",
    [
        [str(CATALOG)],
        ["/work/repo"],
        ["/work/repo/spec-dock/.canonical/"],
        ["~/other", "/work"],
    ],
)
def test_the_catalog_or_a_parent_allows_the_catalog(directories: list[str]) -> None:
    payloads = [(USER, {"permissions": {"additionalDirectories": directories}})]
    assert claude_allows(payloads, CATALOG, home=HOME) is True


def test_a_tilde_entry_expands_with_the_home_directory() -> None:
    payloads = [(USER, {"permissions": {"additionalDirectories": ["~/repo"]}})]
    assert claude_allows(payloads, Path("/home/me/repo/spec-dock/.canonical"), home=HOME) is True


def test_a_relative_entry_resolves_from_the_project_root_of_the_settings_file() -> None:
    payloads = [(PROJECT, {"permissions": {"additionalDirectories": ["../../repo"]}})]
    assert claude_allows(payloads, CATALOG, home=HOME) is True


def test_other_directories_or_no_settings_do_not_allow_the_catalog() -> None:
    assert claude_allows([], CATALOG, home=HOME) is False
    assert (
        claude_allows([(USER, {"permissions": {"additionalDirectories": ["/work/repo-other"]}})], CATALOG, home=HOME)
        is False
    )
    assert claude_allows([(USER, {"permissions": {"allow": ["Read"]}})], CATALOG, home=HOME) is False
    assert claude_allows([(USER, {})], CATALOG, home=HOME) is False


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "not an object",
        {"permissions": "x"},
        {"permissions": {"additionalDirectories": "/work"}},
        {"permissions": {"additionalDirectories": [1]}},
    ],
)
def test_an_unreadable_setting_without_another_match_cannot_be_judged(payload: object) -> None:
    assert claude_allows([(USER, payload)], CATALOG, home=HOME) is None
    allowed = (PROJECT, {"permissions": {"additionalDirectories": ["/work"]}})
    assert claude_allows([(USER, payload), allowed], CATALOG, home=HOME) is True


def test_a_tilde_entry_without_a_home_cannot_be_judged() -> None:
    assert claude_allows([(USER, {"permissions": {"additionalDirectories": ["~/repo"]}})], CATALOG, home=None) is None


def test_entries_are_compared_through_the_given_real_path_resolver() -> None:
    payloads = [(USER, {"permissions": {"additionalDirectories": ["/alias/repo"]}})]
    real = {Path("/alias/repo"): Path("/work/repo")}
    assert claude_allows(payloads, CATALOG, home=HOME, resolve=lambda path: real.get(path, path)) is True
    assert claude_allows(payloads, CATALOG, home=HOME) is False
