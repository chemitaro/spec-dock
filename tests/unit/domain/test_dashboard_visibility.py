"""Which repositories the dashboard shows: the settings' three layers and the hidden marks (iss-00552 D-01)."""

from __future__ import annotations

import json

import pytest

from spec_dock.runtime.domain.dashboard_visibility import (
    RepositoryDashboard,
    UserDashboard,
    Visibility,
    parse_repository_dashboard,
    parse_user_dashboard,
    resolve_config,
)

KEY = "github.com/o/r"


def key_of(value: str) -> str:
    """The repository key the way the CLI writes it: owner/name or github.com/owner/name, any case."""
    parts = value.lower().split("/")
    if len(parts) == 3 and parts[0] == "github.com":
        parts = parts[1:]
    if len(parts) != 2 or not all(part.replace("-", "").isalnum() for part in parts):
        raise ValueError(value)
    return "github.com/" + "/".join(parts)


def user(document: object) -> UserDashboard:
    return parse_user_dashboard("/u/config.json", json.dumps(document).encode(), key_of=key_of)


def repo(document: object, path: str = "/c/dashboard.json") -> RepositoryDashboard:
    return parse_repository_dashboard(path, json.dumps(document).encode())


MISSING_USER = parse_user_dashboard("/u/config.json", None, key_of=lambda value: value)
MISSING_REPO = parse_repository_dashboard("/c/dashboard.json", None)


def test_nothing_written_shows_by_default() -> None:
    config = resolve_config(MISSING_USER, (MISSING_REPO,), KEY)
    assert (config.visible, config.source, config.problems) == (True, "default", ())


def test_the_user_default_and_the_per_repository_value() -> None:
    hide_all = user({"schema": "specdock.config/v1", "dashboard": {"visible": False}})
    assert (resolve_config(hide_all, (), KEY).visible, resolve_config(hide_all, (), KEY).source) == (False, "user")
    allow = user({
        "schema": "specdock.config/v1",
        "dashboard": {"visible": False, "repositories": {"O/R": {"visible": True}}},
    })
    assert (resolve_config(allow, (), KEY).visible, resolve_config(allow, (), KEY).source) == (True, "user")
    assert resolve_config(allow, (), "github.com/o/s").visible is False


def test_a_todo_only_file_leaves_the_dashboard_alone() -> None:
    layer = user({"schema": "specdock.config/v1", "todo": {"parent_limit": "many"}})
    assert resolve_config(layer, (), KEY).source == "default"


def test_the_repository_layer_wins_both_ways() -> None:
    hide_all = user({"schema": "specdock.config/v1", "dashboard": {"visible": False}})
    shown = resolve_config(hide_all, (repo({"schema": "specdock.dashboard-settings/v1", "visible": True}),), KEY)
    assert (shown.visible, shown.source) == (True, "repository")
    show_all = user({"schema": "specdock.config/v1", "dashboard": {"visible": True}})
    hidden = resolve_config(show_all, (repo({"schema": "specdock.dashboard-settings/v1", "visible": False}),), KEY)
    assert (hidden.visible, hidden.source) == (False, "repository")
    without = resolve_config(show_all, (repo({"schema": "specdock.dashboard-settings/v1"}),), KEY)
    assert without.source == "user"


@pytest.mark.parametrize(
    "payload",
    [
        b"{broken",
        b"\xff",
        json.dumps({"schema": "specdock.config/v2"}).encode(),
        json.dumps([1]).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": []}).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": {"visible": "no"}}).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": {"repositories": []}}).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": {"repositories": {"o/r": True}}}).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": {"repositories": {"o/r": {"visible": 1}}}}).encode(),
        json.dumps({"schema": "specdock.config/v1", "dashboard": {"repositories": {"not a repo": {}}}}).encode(),
        json.dumps({
            "schema": "specdock.config/v1",
            "dashboard": {"repositories": {"o/r": {"visible": True}, "github.com/O/R": {"visible": False}}},
        }).encode(),
    ],
)
def test_a_broken_user_file_hides_everything(payload: bytes) -> None:
    layer = parse_user_dashboard("/u/config.json", payload, key_of=key_of)
    config = resolve_config(layer, (MISSING_REPO,), KEY)
    assert (config.visible, config.source) == (False, "invalid")
    assert [(item.layer, item.path) for item in config.problems] == [("user", "/u/config.json")]
    assert config.problems[0].reason


def test_an_unreadable_user_file_hides_everything() -> None:
    layer = parse_user_dashboard("/u/config.json", None, key_of=key_of, read_error="is a directory")
    config = resolve_config(layer, (), KEY)
    assert (config.visible, config.source, config.problems[0].reason) == (False, "invalid", "is a directory")


@pytest.mark.parametrize(
    "payload",
    [
        b"{broken",
        json.dumps({"schema": "specdock.config/v1", "visible": True}).encode(),
        json.dumps({"schema": "specdock.dashboard-settings/v1", "visible": "yes"}).encode(),
    ],
)
def test_a_broken_repository_file_hides_that_repository(payload: bytes) -> None:
    layer = parse_repository_dashboard("/c/dashboard.json", payload)
    config = resolve_config(MISSING_USER, (layer,), KEY)
    assert (config.visible, config.source) == (False, "invalid")
    assert [(item.layer, item.path) for item in config.problems] == [("repository", "/c/dashboard.json")]


@pytest.mark.parametrize(
    ("first", "second"),
    [
        (
            {"schema": "specdock.dashboard-settings/v1", "visible": True},
            {"schema": "specdock.dashboard-settings/v1", "visible": False},
        ),
        ({"schema": "specdock.dashboard-settings/v1", "visible": True}, None),
        ({"schema": "specdock.dashboard-settings/v1", "visible": False}, {"schema": "specdock.dashboard-settings/v1"}),
    ],
)
def test_clones_that_disagree_hide_the_repository(first: object, second: object) -> None:
    layers = (
        repo(first, "/a/dashboard.json"),
        repo(second, "/b/dashboard.json")
        if second is not None
        else parse_repository_dashboard("/b/dashboard.json", None),
    )
    config = resolve_config(MISSING_USER, layers, KEY)
    assert (config.visible, config.source) == (False, "invalid")
    assert config.problems[0].layer == "repository"
    assert config.problems[0].path == "/a/dashboard.json, /b/dashboard.json"
    assert "disagree" in config.problems[0].reason


def test_clones_that_agree_keep_the_value() -> None:
    value = {"schema": "specdock.dashboard-settings/v1", "visible": False}
    config = resolve_config(MISSING_USER, (repo(value, "/a/dashboard.json"), repo(value, "/b/dashboard.json")), KEY)
    assert (config.visible, config.source, config.problems) == (False, "repository", ())
    assert resolve_config(MISSING_USER, (MISSING_REPO, MISSING_REPO), KEY).source == "default"


def test_the_mark_always_hides_and_hidden_by_names_every_reason() -> None:
    shown = resolve_config(MISSING_USER, (), KEY)
    hidden_user = resolve_config(user({"schema": "specdock.config/v1", "dashboard": {"visible": False}}), (), KEY)
    assert Visibility(False, shown).hidden is False and Visibility(False, shown).hidden_by == ()
    assert Visibility(True, shown).hidden is True and Visibility(True, shown).hidden_by == ("mark",)
    assert Visibility(False, hidden_user).hidden_by == ("user",)
    assert Visibility(True, hidden_user).hidden_by == ("mark", "user")
    assert Visibility(True, hidden_user).to_json() == {
        "hidden": True,
        "mark": True,
        "config": {"visible": False, "source": "user"},
        "hidden_by": ["mark", "user"],
    }
