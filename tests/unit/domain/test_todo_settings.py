"""The three settings layers of human tasks (iss-00549 D-06)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.todo_settings import DEFAULTS, Layer, check_values, resolve
from spec_dock.runtime.infra.user_config import read_user_todo_settings, user_config_path

if TYPE_CHECKING:
    from pathlib import Path


def test_later_layers_win_key_by_key() -> None:
    effective = resolve((
        Layer("user", "/u", "ok", None, {"parent_limit": 5, "default_due": "1d"}),
        Layer("repository", "/r", "ok", None, {"parent_limit": 7}),
    ))
    assert effective.values["parent_limit"] == (7, "repository")
    assert effective.values["default_due"] == ("1d", "user")
    assert effective.values["subtask_limit"] == (DEFAULTS["subtask_limit"], "default")


def test_an_invalid_layer_is_skipped_whole() -> None:
    effective = resolve((Layer("user", "/u", "invalid", "bad", {"parent_limit": 5}),))
    assert effective.values["parent_limit"] == (20, "default")


def test_value_checks() -> None:
    assert check_values({"parent_limit": 1, "subtask_limit": 10000, "default_due": "30d", "other": "x"}) is None
    for bad in ({"parent_limit": 0}, {"parent_limit": True}, {"subtask_limit": 10001}, {"default_due": "31d"}):
        assert check_values(bad) is not None, bad


def test_user_config_path_follows_xdg_only_when_absolute(tmp_path: Path) -> None:
    assert user_config_path({"XDG_CONFIG_HOME": str(tmp_path), "HOME": "/h"}) == tmp_path / "spec-dock/config.json"
    assert user_config_path({"XDG_CONFIG_HOME": "rel", "HOME": "/h"}).as_posix() == "/h/.config/spec-dock/config.json"


def test_user_config_states(tmp_path: Path) -> None:
    env = {"XDG_CONFIG_HOME": str(tmp_path)}
    assert read_user_todo_settings(env).state == "missing"
    path = tmp_path / "spec-dock/config.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"schema": "specdock.config/v1", "todo": {"parent_limit": 3}, "other": {}}))
    layer = read_user_todo_settings(env)
    assert (layer.state, layer.values) == ("ok", {"parent_limit": 3})
    path.write_text(json.dumps({"schema": "specdock.config/v1"}))
    assert read_user_todo_settings(env).state == "ok"
    for payload in ("{", json.dumps({"schema": "x"}), json.dumps({"schema": "specdock.config/v1", "todo": []})):
        path.write_text(payload)
        layer = read_user_todo_settings(env)
        assert layer.state == "invalid" and layer.reason, payload
    path.write_text(json.dumps({"schema": "specdock.config/v1", "todo": {"subtask_limit": "many"}}))
    assert read_user_todo_settings(env).state == "invalid"
