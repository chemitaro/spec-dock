"""Which repositories the dashboard shows (iss-00552 D-01).

The settings decide a value in the three layers of epic-00547 D-10: the default (shown) < the user's
`config.json` `dashboard` section (`visible`, then `repositories[<key>].visible`) < the repository's
catalog `dashboard.json`. A broken layer is not skipped: it hides (a wrong answer would show a repository on
the tailnet), and so do registered clones whose values disagree. The `dashboard hide` mark always hides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.domain.todo_settings import USER_SCHEMA

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

REPOSITORY_SCHEMA: Final = "specdock.dashboard-settings/v1"
REPOSITORY_FILE: Final = "dashboard.json"

LayerState = Literal["missing", "ok", "invalid"]
Source = Literal["default", "user", "repository", "invalid"]


@dataclass(frozen=True)
class ConfigProblem:
    layer: Literal["user", "repository"]
    path: str
    reason: str

    def to_json(self) -> dict[str, str]:
        return {"layer": self.layer, "path": self.path, "reason": self.reason}


@dataclass(frozen=True)
class UserDashboard:
    path: str
    state: LayerState
    reason: str | None = None
    visible: bool | None = None
    repositories: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class RepositoryDashboard:
    path: str
    state: LayerState
    reason: str | None = None
    visible: bool | None = None


@dataclass(frozen=True)
class ConfigVisibility:
    visible: bool
    source: Source
    problems: tuple[ConfigProblem, ...] = ()


@dataclass(frozen=True)
class Visibility:
    mark: bool
    config: ConfigVisibility

    @property
    def hidden(self) -> bool:
        return self.mark or not self.config.visible

    @property
    def hidden_by(self) -> tuple[str, ...]:
        reasons: list[str] = ["mark"] if self.mark else []
        if not self.config.visible:
            reasons.append(self.config.source)
        return tuple(reasons)

    def to_json(self) -> dict[str, object]:
        return {
            "hidden": self.hidden,
            "mark": self.mark,
            "config": {"visible": self.config.visible, "source": self.config.source},
            "hidden_by": list(self.hidden_by),
        }


def _document(payload: bytes) -> object:
    """The parsed JSON; raises ValueError with a reason."""
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"not JSON: {error}") from error


def _user_section(section: object, key_of: Callable[[str], str]) -> tuple[bool | None, dict[str, bool]]:
    """(visible, {key: visible}) from the `dashboard` section; raises ValueError with a reason."""
    if not isinstance(section, dict):
        raise ValueError("dashboard must be an object")
    visible = section.get("visible")
    if visible is not None and not isinstance(visible, bool):
        raise ValueError("dashboard.visible must be true or false")
    entries = section.get("repositories", {})
    if not isinstance(entries, dict):
        raise ValueError("dashboard.repositories must be an object")
    found: dict[str, bool] = {}
    for name, entry in entries.items():
        try:
            key = key_of(name)
        except ValueError:
            raise ValueError(f"dashboard.repositories: {name!r} is not owner/name or github.com/owner/name") from None
        if not isinstance(entry, dict):
            raise ValueError(f"dashboard.repositories.{name} must be an object")
        value = entry.get("visible")
        if value is None:
            continue
        if not isinstance(value, bool):
            raise ValueError(f"dashboard.repositories.{name}.visible must be true or false")
        if found.get(key, value) != value:
            raise ValueError(f"dashboard.repositories names {key} twice with different values")
        found[key] = value
    return visible, found


def parse_user_dashboard(
    path: str, payload: bytes | None, *, key_of: Callable[[str], str], read_error: str | None = None
) -> UserDashboard:
    """The user's `config.json` as the dashboard reads it (None payload: no file).

    `key_of` turns a written repository name into its `host/owner/name` key, raising ValueError when it is not one.
    """
    if read_error is not None:
        return UserDashboard(path, "invalid", read_error)
    if payload is None:
        return UserDashboard(path, "missing")
    try:
        document = _document(payload)
        if not isinstance(document, dict) or document.get("schema") != USER_SCHEMA:
            raise ValueError(f"schema must be {USER_SCHEMA}")
        if "dashboard" not in document:
            return UserDashboard(path, "ok")
        visible, repositories = _user_section(document["dashboard"], key_of)
    except ValueError as error:
        return UserDashboard(path, "invalid", str(error))
    return UserDashboard(path, "ok", None, visible, repositories)


def parse_repository_dashboard(
    path: str, payload: bytes | None, *, read_error: str | None = None
) -> RepositoryDashboard:
    """A catalog's `dashboard.json` (None payload: no file)."""
    if read_error is not None:
        return RepositoryDashboard(path, "invalid", read_error)
    if payload is None:
        return RepositoryDashboard(path, "missing")
    try:
        document = _document(payload)
        if not isinstance(document, dict) or document.get("schema") != REPOSITORY_SCHEMA:
            raise ValueError(f"schema must be {REPOSITORY_SCHEMA}")
        visible = document.get("visible")
        if visible is not None and not isinstance(visible, bool):
            raise ValueError("visible must be true or false")
    except ValueError as error:
        return RepositoryDashboard(path, "invalid", str(error))
    return RepositoryDashboard(path, "ok", None, visible)


def resolve_config(user: UserDashboard, repositories: Sequence[RepositoryDashboard], key: str) -> ConfigVisibility:
    """The settings' value for one repository; `repositories` holds one layer per registered clone."""
    problems = [ConfigProblem("user", user.path, user.reason or "")] if user.state == "invalid" else []
    problems += [
        ConfigProblem("repository", layer.path, layer.reason or "")
        for layer in repositories
        if layer.state == "invalid"
    ]
    if problems:
        return ConfigVisibility(False, "invalid", tuple(problems))
    values = {layer.visible for layer in repositories}
    if len(values) > 1:
        shown = ", ".join(
            "none" if value is None else str(value).lower() for value in (layer.visible for layer in repositories)
        )
        reason = f"clones disagree: {shown}"
        path = ", ".join(layer.path for layer in repositories)
        return ConfigVisibility(False, "invalid", (ConfigProblem("repository", path, reason),))
    visible, source = True, "default"
    if user.visible is not None:
        visible, source = user.visible, "user"
    if key in user.repositories:
        visible, source = user.repositories[key], "user"
    repository_value = next(iter(values), None)
    if repository_value is not None:
        visible, source = repository_value, "repository"
    return ConfigVisibility(visible, source)  # type: ignore[arg-type]
