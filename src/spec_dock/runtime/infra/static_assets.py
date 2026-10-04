"""Explicit package resource inventory for single-worktree static installation."""

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


@dataclass(frozen=True)
class StaticAsset:
    path: str
    payload: bytes
    sha256: str
    mode: int
    init_only: bool
    known_old_sha256: tuple[str, ...]


@dataclass(frozen=True)
class RetiredStaticAsset:
    path: str
    known_old_sha256: tuple[str, ...]


def package_static_assets() -> tuple[StaticAsset, ...]:
    root = files("spec_dock").joinpath("assets")
    inventory = json.loads(root.joinpath("static-inventory.json").read_bytes())
    if inventory.get("schema_version") != "specdock.static-inventory/v1":
        raise ValueError("package static inventory is invalid")
    assets: list[StaticAsset] = []
    for entry in inventory["files"]:
        path = entry["path"]
        relative = _relative_path(path)
        if (
            not (
                path
                in (
                    "spec-dock/workspace.json",
                    "spec-dock/.gitignore",
                    "spec-dock/scripts/README.md",
                    "spec-dock/scripts/spec-dock",
                )
                or path.startswith((
                    "spec-dock/docs/",
                    "spec-dock/templates/",
                    "spec-dock/system/",
                ))
                or path.startswith((".agents/skills/spec-dock/", ".agents/skills/spec-dock-grill-with-docs/"))
            )
            or path != relative.as_posix()
        ):
            raise ValueError("package static inventory contains an unsafe target")
        source = _resource(root, entry["source"])
        payload = source.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != entry["sha256"] or entry["mode"] not in (0o644, 0o755):
            raise ValueError("package static resource does not match its inventory")
        assets.append(
            StaticAsset(
                path, payload, digest, entry["mode"], bool(entry["init_only"]), tuple(entry["known_old_sha256"])
            )
        )
    paths = tuple(asset.path for asset in assets)
    if len(paths) != len(set(paths)) or paths != tuple(sorted(paths)):
        raise ValueError("package static inventory paths must be unique and ordered")
    return tuple(assets)


def _relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise ValueError("package static path must be a string")
    relative = PurePosixPath(value)
    if (
        not value
        or relative.is_absolute()
        or ".." in relative.parts
        or "\\" in value
        or ":" in value
        or value != relative.as_posix()
    ):
        raise ValueError("package static path is invalid")
    return relative


def package_retired_assets() -> tuple[RetiredStaticAsset, ...]:
    root = files("spec_dock").joinpath("assets")
    inventory = json.loads(root.joinpath("static-inventory.json").read_bytes())
    if inventory.get("schema_version") != "specdock.static-inventory/v1":
        raise ValueError("package static inventory is invalid")
    result: list[RetiredStaticAsset] = []
    current = {entry["path"] for entry in inventory["files"]}
    for entry in inventory.get("retired", []):
        path = entry["path"]
        _relative_path(path)
        if path in current or not (
            path == "spec-dock/spec-dock.version"
            or (path.startswith("spec-dock/scripts/spec_dock_runtime/") and path.endswith(".py"))
        ):
            raise ValueError("retired static inventory contains an unsafe target")
        hashes = entry["known_old_sha256"]
        if (
            not isinstance(hashes, list)
            or not hashes
            or any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in hashes)
        ):
            raise ValueError("retired static inventory hashes are invalid")
        result.append(RetiredStaticAsset(path, tuple(hashes)))
    paths = tuple(entry.path for entry in result)
    if paths != tuple(sorted(set(paths))):
        raise ValueError("retired static inventory paths must be unique and ordered")
    return tuple(result)


def _resource(root: Traversable, source: str) -> Traversable:
    for part in _relative_path(source).parts:
        root = root.joinpath(part)
    return root
