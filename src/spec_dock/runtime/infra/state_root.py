"""The per-user SpecDock state root, outside every repository and catalog."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


def resolve_state_root(environ: Mapping[str, str] | None = None, *, override: Path | None = None) -> Path:
    """Return ${XDG_STATE_HOME:-$HOME/.local/state}/spec-dock, or an explicit absolute root.

    `canonical link` records the computed root for the periodic job, whose environment usually lacks
    XDG_STATE_HOME; passing that recorded value back as `override` must give the same root.
    """
    if override is not None:
        if not override.is_absolute():
            raise ValueError("the state root must be an absolute path")
        return override
    values = os.environ if environ is None else environ
    configured = values.get("XDG_STATE_HOME", "")
    if configured and Path(configured).is_absolute():
        return Path(configured) / "spec-dock"
    home = values.get("HOME") or str(Path.home())
    return Path(home) / ".local" / "state" / "spec-dock"
