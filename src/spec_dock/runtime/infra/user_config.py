"""The user's SpecDock settings file `$XDG_CONFIG_HOME/spec-dock/config.json` (epic-00547 D-10).

SpecDock only reads it and never creates it. Other features may add sections next to `todo` later.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.todo_settings import Layer, parse_layer

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
