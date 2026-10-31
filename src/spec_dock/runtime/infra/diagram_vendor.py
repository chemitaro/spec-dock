"""Version-pinned diagram parts bundled in the package for local serving (iss-00475, Epic K5).

The files live under ``spec_dock/assets/vendor/`` and are not static installation assets: they are
served by a host (for example the dashboard server) below the URL that a page announces with
``<meta name="ds-vendor-base" content="URL">``. Each ``path`` maps directly below that URL.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from importlib.resources import files
import json
from pathlib import PurePosixPath
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable
    from pathlib import Path

DIAGRAM_VENDOR_META_NAME = "ds-vendor-base"
_SCHEMA_VERSION = "specdock.diagram-vendor/v1"
_DIGEST = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class DiagramVendorFile:
    path: str
    content_type: str
    sha256: str


class DiagramVendorError(ValueError):
    """The bundled diagram parts or their manifest do not match."""


def _vendor_root() -> Traversable | Path:
    return files("spec_dock").joinpath("assets").joinpath("vendor")


def _safe_path(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return None
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        return None
    return value if relative.as_posix() == value else None


def diagram_vendor_files() -> tuple[DiagramVendorFile, ...]:
    """Return the manifest entries after checking its shape; raise DiagramVendorError when broken."""
    try:
        manifest = json.loads(_vendor_root().joinpath("manifest.json").read_bytes())
        if manifest.get("schema_version") != _SCHEMA_VERSION:
            raise DiagramVendorError("diagram vendor manifest has an unknown schema")
        result = tuple(
            DiagramVendorFile(entry["path"], entry["content_type"], entry["sha256"]) for entry in manifest["files"]
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        if isinstance(error, DiagramVendorError):
            raise
        raise DiagramVendorError("diagram vendor manifest is unreadable") from error
    for item in result:
        if (
            _safe_path(item.path) is None
            or item.path == "manifest.json"
            or not isinstance(item.content_type, str)
            or not item.content_type
            or not isinstance(item.sha256, str)
            or _DIGEST.fullmatch(item.sha256) is None
        ):
            raise DiagramVendorError("diagram vendor manifest contains an invalid entry")
    paths = tuple(item.path for item in result)
    if paths != tuple(sorted(set(paths))):
        raise DiagramVendorError("diagram vendor manifest paths must be unique and ordered")
    return result


def read_diagram_vendor_file(path: str) -> bytes | None:
    """Return one listed part's bytes, None for any path outside the manifest, or raise on a digest mismatch."""
    if _safe_path(path) is None:
        return None
    entry = next((item for item in diagram_vendor_files() if item.path == path), None)
    if entry is None:
        return None
    resource = _vendor_root()
    for part in path.split("/"):
        resource = resource.joinpath(part)
    payload = resource.read_bytes()
    if hashlib.sha256(payload).hexdigest() != entry.sha256:
        raise DiagramVendorError(f"bundled diagram part does not match its manifest: {path}")
    return payload
