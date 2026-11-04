"""The settings of human tasks in three layers: defaults < user < repository (epic-00547 D-10).

Each key is decided on its own: the last layer that is `ok` and has the key wins. A layer whose file cannot be
read or has the wrong shape is skipped whole and reported (`TODO_SETTINGS_INVALID`); no command stops for it.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.todo_model import relative

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

USER_SCHEMA: Final = "specdock.config/v1"
REPOSITORY_SCHEMA: Final = "specdock.todo-settings/v1"
DEFAULTS: Final[dict[str, object]] = {"parent_limit": 20, "subtask_limit": 30, "default_due": "4h"}
LIMIT_RANGE: Final = (1, 10000)

LayerName = Literal["user", "repository"]
LayerState = Literal["missing", "ok", "invalid", "not_applicable"]


@dataclass(frozen=True)
class Layer:
    layer: LayerName
    path: str | None
    state: LayerState
    reason: str | None
    values: Mapping[str, object]

    def to_json(self) -> dict[str, object]:
        return {"layer": self.layer, "path": self.path, "state": self.state, "reason": self.reason}


@dataclass(frozen=True)
class Effective:
    values: Mapping[str, tuple[object, str]]  # key -> (value, source: default|user|repository)
    layers: tuple[Layer, ...]

    def value(self, key: str) -> object:
        return self.values[key][0]

    def source(self, key: str) -> str:
        return self.values[key][1]

    def to_json(self) -> dict[str, object]:
        return {
            "values": {key: {"value": value, "source": source} for key, (value, source) in self.values.items()},
            "layers": [layer.to_json() for layer in self.layers],
        }


def check_values(values: Mapping[str, object]) -> str | None:
    """Why the known keys have wrong values, or None; unknown keys are ignored."""
    low, high = LIMIT_RANGE
    for key in ("parent_limit", "subtask_limit"):
        if key in values:
            value = values[key]
            if type(value) is not int or not low <= value <= high:
                return f"{key} must be an integer from {low} to {high}"
    if "default_due" in values:
        value = values["default_due"]
        if not isinstance(value, str) or relative(value) is None:
            return "default_due must be like 30m, 4h or 2d and at most 30d"
    return None


def parse_layer(layer: LayerName, path: str, payload: bytes | None, *, read_error: str | None = None) -> Layer:
    """One layer from its file bytes (None when the file does not exist)."""
    if read_error is not None:
        return Layer(layer, path, "invalid", read_error, {})
    if payload is None:
        return Layer(layer, path, "missing", None, {})
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        return Layer(layer, path, "invalid", f"not JSON: {error}", {})
    schema = USER_SCHEMA if layer == "user" else REPOSITORY_SCHEMA
    if not isinstance(document, dict) or document.get("schema") != schema:
        return Layer(layer, path, "invalid", f"schema must be {schema}", {})
    if layer == "user":
        section = document.get("todo", {})
        if not isinstance(section, dict):
            return Layer(layer, path, "invalid", "todo must be an object", {})
    else:
        section = {key: value for key, value in document.items() if key != "schema"}
    reason = check_values(section)
    if reason is not None:
        return Layer(layer, path, "invalid", reason, {})
    return Layer(layer, path, "ok", None, {key: section[key] for key in DEFAULTS if key in section})


def resolve(layers: Sequence[Layer]) -> Effective:
    values: dict[str, tuple[object, str]] = {key: (value, "default") for key, value in DEFAULTS.items()}
    for layer in layers:
        if layer.state != "ok":
            continue
        for key, value in layer.values.items():
            values[key] = (value, layer.layer)
    return Effective(values, tuple(layers))
