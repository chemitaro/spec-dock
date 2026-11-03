"""The package files the dashboard server hands out: its screens, the design system and the diagram parts.

The screens live in `spec_dock/assets/dashboard/` (in the wheel through `assets/**/*`; not a static asset of
`static-inventory.json`). The design system is the shipped `spec_dock/assets/spec_dock/design-system/`, and the
diagram parts come through `diagram_vendor` with their manifest's content type (Epic D-07, R-24).
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
import mimetypes
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.infra.diagram_vendor import diagram_vendor_files, read_diagram_vendor_file

if TYPE_CHECKING:
    from collections.abc import Sequence
    from importlib.resources.abc import Traversable

_TYPES: Final = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".cue": "text/plain; charset=utf-8",
    ".py": "text/plain; charset=utf-8",
}


@dataclass(frozen=True)
class AssetFile:
    body: bytes
    content_type: str


def content_type(name: str) -> str:
    lower = name.lower()
    for suffix, value in _TYPES.items():
        if lower.endswith(suffix):
            return value
    guessed, _ = mimetypes.guess_type(lower)
    return guessed or "application/octet-stream"


def _read(root: Traversable, parts: Sequence[str]) -> AssetFile | None:
    resource = root
    for part in parts:
        resource = resource.joinpath(part)
    try:
        if not resource.is_file():
            return None
        return AssetFile(resource.read_bytes(), content_type(parts[-1]))
    except OSError:
        return None


def screen_asset(parts: Sequence[str]) -> AssetFile | None:
    """A file of the screens; `parts` are checked path segments (no '', '.', '..')."""
    return _read(files("spec_dock").joinpath("assets").joinpath("dashboard"), parts) if parts else None


def design_system_asset(parts: Sequence[str]) -> AssetFile | None:
    root = files("spec_dock").joinpath("assets").joinpath("spec_dock").joinpath("design-system")
    return _read(root, parts) if parts else None


def vendor_asset(parts: Sequence[str]) -> AssetFile | None:
    path = "/".join(parts)
    body = read_diagram_vendor_file(path)
    if body is None:
        return None
    entry = next(item for item in diagram_vendor_files() if item.path == path)
    return AssetFile(body, entry.content_type)
