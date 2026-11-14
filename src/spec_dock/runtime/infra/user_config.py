"""The user's SpecDock settings file `$XDG_CONFIG_HOME/spec-dock/config.json` (epic-00547 D-10) and a catalog's
`dashboard.json` (iss-00552 D-02).

SpecDock only reads them and never creates them. The file holds the `todo` and `dashboard` sections.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.dashboard_visibility import (
    REPOSITORY_FILE,
    RepositoryDashboard,
    UserDashboard,
    parse_repository_dashboard,
    parse_user_dashboard,
)
from spec_dock.runtime.domain.orca_web import OrcaWebSettings, parse_orca_web
from spec_dock.runtime.domain.todo_settings import Layer, parse_layer
from spec_dock.runtime.infra.github_structure import GithubRepository

if TYPE_CHECKING:
    from collections.abc import Mapping


def user_config_path(environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    base = env.get("XDG_CONFIG_HOME", "")
    if base and Path(base).is_absolute():
        root = Path(base)
    else:
        home = env.get("HOME")
        root = (Path(home) if home else Path.home()) / ".config"
    return root / "spec-dock" / "config.json"


def read_optional(path: Path) -> tuple[bytes | None, str | None]:
    """(bytes, None), (None, None) when absent, or (None, reason) when it cannot be read."""
    try:
        return path.read_bytes(), None
    except FileNotFoundError:
        return None, None
    except IsADirectoryError:
        return None, "is a directory"
    except OSError as error:
        return None, f"cannot be read: {error.strerror or error}"


def read_user_todo_settings(environ: Mapping[str, str] | None = None) -> Layer:
    path = user_config_path(environ)
    payload, error = read_optional(path)
    return parse_layer("user", str(path), payload, read_error=error)


def repository_key(value: str) -> str:
    return GithubRepository.parse(value).key


def read_user_dashboard(path: Path | None = None) -> UserDashboard:
    """The `dashboard` section of the user's settings file (`path` defaults to `user_config_path()`)."""
    target = path if path is not None else user_config_path()
    payload, error = read_optional(target)
    return parse_user_dashboard(str(target), payload, key_of=repository_key, read_error=error)


def read_repository_dashboard(catalog: Path) -> RepositoryDashboard:
    """A catalog's `dashboard.json`; a link there is refused like a broken file."""
    path = catalog / REPOSITORY_FILE
    if path.is_symlink():
        return parse_repository_dashboard(str(path), None, read_error="is a symbolic link")
    payload, error = read_optional(path)
    return parse_repository_dashboard(str(path), payload, read_error=error)


def read_user_orca_web(path: Path | None = None) -> OrcaWebSettings:
    """Read the independent orca_web section, using the same optional-file boundary."""
    target = path if path is not None else user_config_path()
    payload, error = read_optional(target)
    return parse_orca_web(payload, read_error=error)
