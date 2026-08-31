"""spec-dock installer CLI (uvx entrypoint).

This module is intentionally minimal:
- `spec-dock init` scaffolds `spec-dock/` into a target repository
- `spec-dock update` refreshes managed assets (docs/templates/scripts/skill)

Day-to-day operations (creating nodes, switching active issue, syncing state, etc.)
are handled by the repo-local runtime script installed at:
  `spec-dock/scripts/spec-dock`
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager, suppress
import hashlib
from importlib.resources import as_file, files
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, NoReturn, cast

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows has no POSIX flock module.
    fcntl = None  # type: ignore[assignment]

from spec_dock import __version__
from spec_dock.managed_distribution import (
    DistributionAdmission,
    DistributionAsset,
    DistributionIdentity,
    DistributionOperation,
    DistributionProcessError,
    DistributionProcessResult,
    DistributionRootIdentity,
    RecognizedDistributionIntent,
    _render_context_pack,
    admit_distribution_operation,
    build_distribution_plan,
    execute_deprovision_distribution,
    execute_explicit_spec_history_purge_distribution,
    execute_fresh_distribution,
    execute_recognized_distribution,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_SPEC_DOCK_DIRNAME = "spec-dock"
_LEGACY_SPEC_DOCK_DIRNAME = ".spec-dock"
_MANAGED_DIRS = ("docs", "templates", "scripts", "system")
_MANAGED_SCAFFOLD_ROOTS = tuple(Path(_SPEC_DOCK_DIRNAME) / name for name in _MANAGED_DIRS)
# Keep managed skill installation aligned with the shipped Target catalog.
_MANAGED_SKILL_NAMES = (
    "spec-dock",
    "spec-dock-grill-with-docs",
)
_MANAGED_OBSOLETE_EXACT_PATH_PREFIXES = (
    ".agents/skills/",
    ".agents/host-adapters/",
    ".codex/agents/",
    ".github/agents/",
    ".github/workflows/",
)
_DISTRIBUTION_RETRY_MARKER_REL = Path("spec-dock/.distribution-retry.json")
_DISTRIBUTION_CWD_LOCK = threading.RLock()

_FreshDistributionIntent = Literal["fresh", "update", "init-force"]


@contextmanager
def _exclusive_distribution_operation(target_root: Path) -> Iterator[DistributionRootIdentity]:
    """Serialize installer mutations for one repository root without a lock file."""

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    if fcntl is None or not nofollow or not directory:
        raise RuntimeError("platform lacks required no-follow operation lock support")
    fd = os.open(target_root, os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0))
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        locked = os.fstat(fd)
        try:
            visible = os.lstat(target_root)
        except OSError as exc:
            raise RuntimeError("distribution target root changed while acquiring operation lock") from exc
        if (
            stat.S_ISLNK(visible.st_mode)
            or not stat.S_ISDIR(visible.st_mode)
            or not stat.S_ISDIR(locked.st_mode)
            or (visible.st_dev, visible.st_ino) != (locked.st_dev, locked.st_ino)
        ):
            raise RuntimeError("distribution target root changed while acquiring operation lock")
        yield DistributionRootIdentity(device=locked.st_dev, inode=locked.st_ino)
    finally:
        with suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


@contextmanager
def _assets_dir() -> Iterator[Path]:
    """Yield the package assets directory as a real filesystem path."""
    assets = files("spec_dock") / "assets"
    with as_file(assets) as p:
        yield Path(p)


def _tool_version() -> str:
    """Return the installed package version (fallback to pyproject in dev)."""
    if __version__ and __version__ != "0.0.0+unknown":
        return __version__

    # Fallback for dev usage when `spec-dock` isn't installed as a package.
    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return __version__

    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    return match.group(1) if match else __version__


def _admit_distribution_cli(target_root: Path, *, operation: DistributionOperation) -> DistributionAdmission:
    """Run version/marker admission before any installer mutation."""
    with _assets_dir() as assets_dir:
        return admit_distribution_operation(
            target_root,
            operation=operation,
            package_version=_tool_version(),
            manifest_path=assets_dir / "managed_distribution.json",
        )


def _specdock_dir(target_root: Path) -> Path:
    """Return the `spec-dock/` path under the target root."""
    return target_root / _SPEC_DOCK_DIRNAME


def _require_specdock(target_root: Path) -> Path:
    """Ensure `spec-dock/` exists under `target_root` and return it."""
    specdock_dir = _specdock_dir(target_root)
    if not specdock_dir.exists():
        legacy = target_root / _LEGACY_SPEC_DOCK_DIRNAME
        if legacy.exists():
            raise RuntimeError(
                f"'{_SPEC_DOCK_DIRNAME}' not found. "
                f"Legacy '{_LEGACY_SPEC_DOCK_DIRNAME}' exists with an incompatible format. "
                f"Run 'spec-dock init' to install a new '{_SPEC_DOCK_DIRNAME}' workspace, migrate manually, "
                f"and remove '{_LEGACY_SPEC_DOCK_DIRNAME}' manually when ready."
            )
        raise RuntimeError(f"'{_SPEC_DOCK_DIRNAME}' not found. Run 'spec-dock init' first.")
    return specdock_dir


class _ManagedPathIdentity(NamedTuple):
    """No-follow identity captured for one managed scaffold boundary."""

    device: int
    inode: int
    ctime_ns: int


def _managed_path_identity(path: Path) -> _ManagedPathIdentity:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise RuntimeError(f"managed scaffold target cannot be inspected safely: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_nlink < 1:
        raise RuntimeError(f"managed scaffold target is not a safe directory: {path}")
    return _ManagedPathIdentity(info.st_dev, info.st_ino, info.st_ctime_ns)


def _managed_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if not isinstance(nofollow, int) or not isinstance(directory, int):
        raise RuntimeError("managed scaffold no-follow support is unavailable")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _active_placeholder_dir(specdock_dir: Path, layer: str) -> Path:
    """Return placeholder directory for a layer or raise if missing."""
    path = specdock_dir / "system" / "active-none" / layer
    if not path.is_dir():
        raise RuntimeError(f"Missing placeholder directory: {path}")
    return path


def _normalize_active_manifest_entry_id(entry: object) -> str | None:
    if not isinstance(entry, dict):
        return None
    raw_id = entry.get("id")
    if not isinstance(raw_id, str):
        return None
    normalized = raw_id.strip()
    return normalized or None


def _normalize_active_manifest_entry_path(entry: object) -> str | None:
    if not isinstance(entry, dict):
        return None
    raw_path = entry.get("path")
    if not isinstance(raw_path, str):
        return None
    normalized = raw_path.strip()
    return normalized or None


def _normalize_active_manifest_entries(
    current: object,
) -> dict[str, tuple[str | None, str | None]] | None:
    if not isinstance(current, dict):
        return None

    if all(key in current and current[key] is None for key in ("initiative", "epic", "issue")):
        return {
            "initiative": (None, None),
            "epic": (None, None),
            "issue": (None, None),
        }

    out: dict[str, tuple[str | None, str | None]] = {}
    for layer in ("initiative", "epic", "issue"):
        entry = current.get(layer)
        out[layer] = (
            _normalize_active_manifest_entry_id(entry),
            _normalize_active_manifest_entry_path(entry),
        )
    if all(out[layer][0] is None for layer in ("initiative", "epic", "issue")):
        return None
    return out


def _normalize_active_manifest_ids(current: object) -> tuple[str | None, str | None, str | None] | None:
    entries = _normalize_active_manifest_entries(current)
    if entries is None:
        return None
    return (entries["initiative"][0], entries["epic"][0], entries["issue"][0])


def _load_persisted_active_ids(specdock_dir: Path) -> tuple[str | None, str | None, str | None]:
    entries = _load_persisted_active_entries(specdock_dir)
    return (entries["initiative"][0], entries["epic"][0], entries["issue"][0])


def _load_persisted_active_entries(specdock_dir: Path) -> dict[str, tuple[str | None, str | None]]:
    candidates = (
        specdock_dir / ".agent" / "active.json",
        specdock_dir / ".work" / "active.json",
        specdock_dir / ".work" / "current.json",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            loaded: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        normalized = _normalize_active_manifest_entries(loaded)
        if normalized is not None:
            return normalized
    return {
        "initiative": (None, None),
        "epic": (None, None),
        "issue": (None, None),
    }


def _resolve_manifest_target_dir(
    specdock_dir: Path,
    layer: str,
    *,
    expected_id: str | None,
    persisted_path: str | None,
) -> Path | None:
    if expected_id is None:
        return None

    lexical_repo_root = specdock_dir.parent
    repo_root = lexical_repo_root.resolve()
    candidates: list[Path] = []

    if persisted_path is not None:
        candidate = Path(persisted_path)
        if not candidate.is_absolute():
            candidate = lexical_repo_root / candidate
        candidates.append(candidate)

    # Fallback: persisted path can be missing/corrupt; recover by id if possible.
    initiatives_root = specdock_dir / "initiatives"
    for meta_path in _iter_manifest_meta_paths(initiatives_root):
        try:
            loaded = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(loaded, dict):
            continue
        if str(loaded.get("id", "")).strip() != expected_id:
            continue
        candidates.append(meta_path.parent)
        break

    for candidate in candidates:
        if _has_lexical_workbench_component(candidate, lexical_repo_root):
            continue
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(repo_root)
        except ValueError:
            continue
        if ".workbench" in relative.parts:
            continue
        if not resolved.is_dir():
            continue
        meta_path = resolved / ".meta.json"
        if not meta_path.is_file():
            continue
        try:
            loaded = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(loaded, dict):
            continue
        if str(loaded.get("id", "")).strip() != expected_id:
            continue
        if str(loaded.get("type", "")).strip() != layer:
            continue
        return resolved
    return None


def _iter_manifest_meta_paths(initiatives_root: Path) -> list[Path]:
    matches: list[Path] = []
    for current_root, child_dirnames, filenames in os.walk(initiatives_root, topdown=True):
        child_dirnames[:] = sorted(name for name in child_dirnames if name != ".workbench")
        if ".meta.json" in filenames:
            matches.append(Path(current_root) / ".meta.json")
    return sorted(matches, key=lambda path: path.as_posix())


def _has_lexical_workbench_component(path: Path, repo_root: Path) -> bool:
    absolute = path.absolute()
    for root in (repo_root.absolute(), repo_root.resolve()):
        try:
            relative = absolute.relative_to(root)
        except ValueError:
            continue
        if ".workbench" in relative.parts:
            return True
    return False


def _resolve_persisted_path_dir(
    specdock_dir: Path,
    *,
    layer: str,
    expected_id: str | None,
    persisted_path: str | None,
) -> Path | None:
    if persisted_path is None:
        return None
    candidate = Path(persisted_path)
    lexical_repo_root = specdock_dir.parent
    repo_root = lexical_repo_root.resolve()
    if not candidate.is_absolute():
        candidate = lexical_repo_root / candidate
    if _has_lexical_workbench_component(candidate, lexical_repo_root):
        return None
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(repo_root)
    except ValueError:
        return None
    if ".workbench" in relative.parts:
        return None
    if not resolved.is_dir():
        return None
    expected_prefix = {
        "initiative": "init-",
        "epic": "epic-",
        "issue": "iss-",
    }.get(layer)
    if expected_prefix is not None and not resolved.name.startswith(expected_prefix):
        return None
    if expected_id is None:
        return None
    meta_path = resolved / ".meta.json"
    if not meta_path.is_file():
        return None
    try:
        loaded = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    if str(loaded.get("id", "")).strip() != expected_id:
        return None
    if str(loaded.get("type", "")).strip() != layer:
        return None
    return resolved


def _resolve_existing_active_entrypoint(
    specdock_dir: Path,
    *,
    active_dir: Path,
    layer: str,
) -> tuple[Path, str | None] | None:
    repo_root = specdock_dir.parent.resolve()
    placeholder = _active_placeholder_dir(specdock_dir, layer).resolve()
    link = active_dir / layer
    pathfile = active_dir / f"{layer}.path"
    candidates: list[Path] = []

    if link.exists() or link.is_symlink():
        with suppress(OSError):
            if link.is_symlink():
                target = link.readlink()
                candidates.append(target if target.is_absolute() else link.parent / target)
            else:
                candidates.append(link)

    if pathfile.is_file():
        try:
            rel_target = pathfile.read_text(encoding="utf-8").strip()
        except OSError:
            rel_target = ""
        if rel_target:
            candidates.append(active_dir / rel_target)

    placeholder_candidate: tuple[Path, str | None] | None = None
    for lexical_candidate in candidates:
        if _has_lexical_workbench_component(lexical_candidate, specdock_dir.parent):
            continue
        candidate = lexical_candidate.resolve()
        try:
            relative = candidate.relative_to(repo_root)
        except ValueError:
            continue
        if ".workbench" in relative.parts:
            continue
        if not candidate.is_dir():
            continue
        if candidate == placeholder:
            if placeholder_candidate is None:
                placeholder_candidate = (candidate, None)
            continue
        meta_path = candidate / ".meta.json"
        if not meta_path.is_file():
            continue
        try:
            loaded = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(loaded, dict):
            continue
        layer_value = str(loaded.get("type", loaded.get("kind", ""))).strip()
        if layer_value != layer:
            continue
        entry_id = str(loaded.get("id", "")).strip()
        if not entry_id:
            continue
        return (candidate, entry_id)
    return placeholder_candidate


def _render_default_context_pack() -> str:
    return _render_context_pack(initiative_id=None, epic_id=None, issue_id=None)


def _generated_regular_distribution_asset(
    path: str,
    content: bytes,
    *,
    refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
) -> DistributionAsset:
    return DistributionAsset(
        path=path,
        identity=DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=0o644,
        ),
        generated_content=content,
        refreshable_existing_identities=refreshable_existing_identities,
    )


def _generated_symlink_distribution_asset(
    path: str,
    target: str,
    *,
    refreshable_existing_identities: tuple[DistributionIdentity, ...] | None = None,
) -> DistributionAsset:
    return DistributionAsset(
        path=path,
        identity=DistributionIdentity(kind="symlink", target=target),
        refreshable_existing_identities=refreshable_existing_identities,
    )


def _active_symlink_creation_supported() -> bool:
    return hasattr(os, "symlink") and os.symlink in os.supports_dir_fd


class _PreservedReadBinding(NamedTuple):
    """No-follow identity captured for one preserved-state read boundary."""

    device: int
    inode: int
    mode: int
    link_count: int
    size: int
    mtime_ns: int
    ctime_ns: int
    link_target: str | None = None


class _PreservedDirectoryInventory(NamedTuple):
    """Resolver-visible children captured from one held directory descriptor."""

    selection: str
    allowed_names: frozenset[str]
    children: dict[str, _PreservedReadBinding]


def _preserved_read_binding(info: os.stat_result, *, link_target: str | None = None) -> _PreservedReadBinding:
    return _PreservedReadBinding(
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_nlink,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        link_target,
    )


def _open_preserved_parent_at(root_fd: int, relative_path: Path) -> tuple[int, ...]:
    """Open one repository-relative parent chain without following links."""

    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise RuntimeError("preserved state path escapes the bound repository")
    opened: list[int] = [os.dup(root_fd)]
    try:
        for component in relative_path.parent.parts:
            if component in ("", "."):
                continue
            child_fd = os.open(component, _managed_directory_flags(), dir_fd=opened[-1])
            child = os.fstat(child_fd)
            visible = os.stat(component, dir_fd=opened[-1], follow_symlinks=False)
            if (
                stat.S_ISLNK(visible.st_mode)
                or not stat.S_ISDIR(visible.st_mode)
                or not stat.S_ISDIR(child.st_mode)
                or (visible.st_dev, visible.st_ino) != (child.st_dev, child.st_ino)
            ):
                os.close(child_fd)
                raise RuntimeError("preserved state directory identity changed")
            opened.append(child_fd)
        return tuple(opened)
    except (OSError, RuntimeError) as exc:
        for fd in reversed(opened):
            with suppress(OSError):
                os.close(fd)
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError("preserved state directory cannot be opened safely") from exc


def _stat_preserved_path_at(root_fd: int, relative_path: Path) -> tuple[os.stat_result | None, str | None]:
    """Stat one preserved path through a no-follow repository-relative parent chain."""

    parent_chain = _open_preserved_parent_at(root_fd, relative_path)
    try:
        try:
            info = os.stat(relative_path.name, dir_fd=parent_chain[-1], follow_symlinks=False)
        except FileNotFoundError:
            return None, None
        link_target = os.readlink(relative_path.name, dir_fd=parent_chain[-1]) if stat.S_ISLNK(info.st_mode) else None
        return info, link_target
    except OSError as exc:
        raise RuntimeError("preserved state path cannot be inspected safely") from exc
    finally:
        for fd in reversed(parent_chain):
            with suppress(OSError):
                os.close(fd)


def _read_preserved_regular_at(
    root_fd: int,
    relative_path: Path,
    bindings: dict[Path, _PreservedReadBinding | None],
    *,
    binding_path: Path | None = None,
) -> tuple[bytes, int, _PreservedReadBinding] | None:
    """Read one single-link regular file from a held parent descriptor."""

    binding_key = binding_path or relative_path
    parent_chain = _open_preserved_parent_at(root_fd, relative_path)
    file_fd: int | None = None
    try:
        parent_fd = parent_chain[-1]
        try:
            visible = os.stat(relative_path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            bindings[binding_key] = None
            return None
        if stat.S_ISLNK(visible.st_mode) or not stat.S_ISREG(visible.st_mode) or visible.st_nlink != 1:
            raise RuntimeError(f"preserved state file is not a safe regular file: {relative_path.as_posix()}")
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int):
            raise RuntimeError("preserved state no-follow support is unavailable")
        file_fd = os.open(
            relative_path.name,
            os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(file_fd)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or (opened.st_dev, opened.st_ino, opened.st_ctime_ns)
            != (visible.st_dev, visible.st_ino, visible.st_ctime_ns)
        ):
            raise RuntimeError("preserved state file identity changed")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_fd, 1024 * 64)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_fd)
        current = os.stat(relative_path.name, dir_fd=parent_fd, follow_symlinks=False)
        expected = _preserved_read_binding(opened)
        if _preserved_read_binding(after) != expected or _preserved_read_binding(current) != expected:
            raise RuntimeError("preserved state file identity changed")
        bindings[binding_key] = expected
        return b"".join(chunks), stat.S_IMODE(opened.st_mode), expected
    except OSError as exc:
        raise RuntimeError("preserved state file cannot be read safely") from exc
    finally:
        if file_fd is not None:
            with suppress(OSError):
                os.close(file_fd)
        for fd in reversed(parent_chain):
            with suppress(OSError):
                os.close(fd)


def _capture_preserved_directory_at(
    root_fd: int,
    relative_path: Path,
    bindings: dict[Path, _PreservedReadBinding | None],
    *,
    required: bool,
    binding_path: Path | None = None,
) -> int | None:
    """Open and bind one directory that is part of the preserved read set."""

    binding_key = binding_path or relative_path
    parent_chain = _open_preserved_parent_at(root_fd, relative_path)
    try:
        parent_fd = parent_chain[-1]
        try:
            visible = os.stat(relative_path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            bindings[binding_key] = None
            if required:
                raise RuntimeError(f"missing preserved state directory: {relative_path.as_posix()}") from None
            return None
        if stat.S_ISLNK(visible.st_mode) or not stat.S_ISDIR(visible.st_mode):
            raise RuntimeError(f"preserved state boundary is not a safe directory: {relative_path.as_posix()}")
        directory_fd = os.open(relative_path.name, _managed_directory_flags(), dir_fd=parent_fd)
        opened = os.fstat(directory_fd)
        if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino, opened.st_ctime_ns) != (
            visible.st_dev,
            visible.st_ino,
            visible.st_ctime_ns,
        ):
            os.close(directory_fd)
            raise RuntimeError("preserved state directory identity changed")
        bindings[binding_key] = _preserved_read_binding(opened)
        return directory_fd
    except OSError as exc:
        raise RuntimeError("preserved state directory cannot be opened safely") from exc
    finally:
        for fd in reversed(parent_chain):
            with suppress(OSError):
                os.close(fd)


def _preserved_inventory_entry_selected(
    name: str,
    info: os.stat_result,
    *,
    selection: str,
    allowed_names: frozenset[str],
) -> bool:
    if selection == "all":
        return True
    if selection == "allowed":
        return name in allowed_names
    if selection == "initiative":
        if name == ".workbench":
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise RuntimeError("preserved initiative workbench boundary is unsafe")
            return True
        if not (stat.S_ISLNK(info.st_mode) or stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
            raise RuntimeError("preserved initiative traversal contains an unsafe entry")
        return stat.S_ISLNK(info.st_mode) or name == ".meta.json" or stat.S_ISDIR(info.st_mode)
    raise RuntimeError("unknown preserved directory inventory selection")


def _capture_preserved_directory_inventory(
    directory_fd: int,
    relative_path: Path,
    inventories: dict[Path, _PreservedDirectoryInventory],
    *,
    selection: str,
    allowed_names: frozenset[str] = frozenset(),
) -> None:
    """Capture the resolver-visible child set without reopening its directory."""

    before = os.fstat(directory_fd)
    captured: dict[str, _PreservedReadBinding] = {}
    try:
        names = sorted(os.listdir(directory_fd))
        for name in names:
            info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            if not _preserved_inventory_entry_selected(
                name,
                info,
                selection=selection,
                allowed_names=allowed_names,
            ):
                continue
            link_target = os.readlink(name, dir_fd=directory_fd) if stat.S_ISLNK(info.st_mode) else None
            captured[name] = _preserved_read_binding(info, link_target=link_target)
        after = os.fstat(directory_fd)
        if (after.st_dev, after.st_ino, after.st_ctime_ns) != (before.st_dev, before.st_ino, before.st_ctime_ns):
            raise RuntimeError("preserved state directory inventory changed during capture")
    except OSError as exc:
        raise RuntimeError("preserved state directory inventory cannot be captured safely") from exc
    inventories[relative_path] = _PreservedDirectoryInventory(selection, allowed_names, captured)


def _snapshot_active_manifest(
    content: bytes,
    *,
    visible_root: Path,
    initiative_aliases: frozenset[Path],
) -> bytes:
    """Map absolute in-repository manifest paths into the private snapshot root."""

    try:
        loaded: Any = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return content
    if not isinstance(loaded, dict):
        return content
    changed = False
    for layer in ("initiative", "epic", "issue"):
        entry = loaded.get(layer)
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        raw_path = Path(entry["path"])
        if raw_path.is_absolute():
            try:
                relative = raw_path.relative_to(visible_root)
            except ValueError:
                try:
                    specdock_index = raw_path.parts.index("spec-dock")
                    lexical_root = Path(*raw_path.parts[:specdock_index])
                    same_root = lexical_root.samefile(visible_root)
                except (OSError, ValueError):
                    same_root = False
                if not same_root:
                    entry["path"] = "__preserved-state-outside-repository__"
                    changed = True
                    continue
                relative = Path(*raw_path.parts[specdock_index:])
            entry["path"] = relative.as_posix()
            changed = True
        else:
            relative = raw_path
        normalized_parts: list[str] = []
        for component in relative.parts:
            if component in ("", "."):
                continue
            if component == "..":
                if normalized_parts:
                    normalized_parts.pop()
                continue
            normalized_parts.append(component)
            if Path(*normalized_parts) in initiative_aliases:
                raise RuntimeError("persisted active path traverses an initiative symlink")
        normalized = Path(*normalized_parts)
        if any(normalized == alias or alias in normalized.parents for alias in initiative_aliases):
            raise RuntimeError("persisted active path traverses an initiative symlink")
    if not changed:
        return content
    return (json.dumps(loaded, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _preserved_active_target_is_within_specdock(raw_target: str) -> bool:
    """Validate an active target lexically without resolving filesystem entries."""

    if (
        not raw_target
        or "\\" in raw_target
        or Path(raw_target).is_absolute()
        or any(ord(character) < 0x20 for character in raw_target)
    ):
        return False
    parts = ["spec-dock", "active"]
    for component in Path(raw_target).parts:
        if component in ("", "."):
            continue
        if component == "..":
            if not parts:
                return False
            parts.pop()
            continue
        parts.append(component)
    return bool(parts) and parts[0] == "spec-dock"


def _snapshot_initiative_metadata(
    source_fd: int,
    destination: Path,
    relative_root: Path,
    bindings: dict[Path, _PreservedReadBinding | None],
    inventories: dict[Path, _PreservedDirectoryInventory],
) -> None:
    """Copy only metadata that the active-state resolver reads from initiatives."""

    _capture_preserved_directory_inventory(
        source_fd,
        relative_root,
        inventories,
        selection="initiative",
    )
    for name in sorted(os.listdir(source_fd)):
        if name == ".workbench":
            continue
        info = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
        relative_path = relative_root / name
        if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
            child_fd = os.open(name, _managed_directory_flags(), dir_fd=source_fd)
            try:
                opened = os.fstat(child_fd)
                if (opened.st_dev, opened.st_ino, opened.st_ctime_ns) != (
                    info.st_dev,
                    info.st_ino,
                    info.st_ctime_ns,
                ):
                    raise RuntimeError("preserved initiative directory identity changed")
                bindings[relative_path] = _preserved_read_binding(opened)
                child_destination = destination / name
                child_destination.mkdir()
                _snapshot_initiative_metadata(
                    child_fd,
                    child_destination,
                    relative_path,
                    bindings,
                    inventories,
                )
            finally:
                os.close(child_fd)
            continue
        if name != ".meta.json":
            continue
        captured = _read_preserved_regular_at(
            source_fd,
            Path(name),
            bindings,
            binding_path=relative_path,
        )
        if captured is None:
            raise RuntimeError("preserved initiative metadata disappeared")
        content, mode, _binding = captured
        target = destination / name
        target.write_bytes(content)
        target.chmod(mode)


def _revalidate_preserved_read_bindings(
    root_fd: int,
    bindings: dict[Path, _PreservedReadBinding | None],
    inventories: dict[Path, _PreservedDirectoryInventory],
    *,
    allow_directory_metadata_changes: bool = False,
) -> None:
    """Reject any preserved input that appeared, vanished, or rebound before service entry."""

    for relative_path, expected in bindings.items():
        current, link_target = _stat_preserved_path_at(root_fd, relative_path)
        if expected is None:
            if current is not None:
                raise RuntimeError("preserved state path appeared after capture")
            continue
        if allow_directory_metadata_changes and stat.S_ISDIR(expected.mode):
            if (
                current is None
                or not stat.S_ISDIR(current.st_mode)
                or (current.st_dev, current.st_ino) != (expected.device, expected.inode)
            ):
                raise RuntimeError("preserved state path identity changed after capture")
            continue
        if current is None or _preserved_read_binding(current, link_target=link_target) != expected:
            raise RuntimeError("preserved state path identity changed after capture")

    for relative_path, inventory in inventories.items():
        parent_chain = _open_preserved_parent_at(root_fd, relative_path / "__inventory__")
        try:
            directory_fd = parent_chain[-1]
            before = os.fstat(directory_fd)
            current_children: dict[str, _PreservedReadBinding] = {}
            for name in sorted(os.listdir(directory_fd)):  # noqa: PTH208
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if not _preserved_inventory_entry_selected(
                    name,
                    info,
                    selection=inventory.selection,
                    allowed_names=inventory.allowed_names,
                ):
                    continue
                link_target = os.readlink(name, dir_fd=directory_fd) if stat.S_ISLNK(info.st_mode) else None
                current_children[name] = _preserved_read_binding(info, link_target=link_target)
            after = os.fstat(directory_fd)
            if (after.st_dev, after.st_ino, after.st_ctime_ns) != (before.st_dev, before.st_ino, before.st_ctime_ns):
                raise RuntimeError("preserved state directory inventory changed during revalidation")
            if current_children.keys() != inventory.children.keys():
                raise RuntimeError("preserved state directory children changed after capture")
            for name, expected_child in inventory.children.items():
                current_child = current_children[name]
                if inventory.selection == "initiative" and name == ".workbench":
                    if not stat.S_ISDIR(current_child.mode) or (current_child.device, current_child.inode) != (
                        expected_child.device,
                        expected_child.inode,
                    ):
                        raise RuntimeError("preserved initiative workbench boundary changed after capture")
                    continue
                if current_child != expected_child:
                    raise RuntimeError("preserved state directory child identity changed after capture")
        except OSError as exc:
            raise RuntimeError("preserved state directory inventory cannot be revalidated safely") from exc
        finally:
            for fd in reversed(parent_chain):
                with suppress(OSError):
                    os.close(fd)


@contextmanager
def _recognized_preserved_state_snapshot(
    bound_root: Path,
    *,
    visible_root: Path,
) -> Iterator[tuple[Path, Callable[[], None], Callable[[], None]]]:
    """Yield a descriptor-captured snapshot for recognized pre-service reads."""

    # `_bound_distribution_root` has already fchdir-bound this lexical path to
    # the opened repository.  Do not reopen `visible_root`: it may be rebound
    # by an attacker while the held repository remains the mutation authority.
    root_fd = os.open(bound_root, _managed_directory_flags())
    bindings: dict[Path, _PreservedReadBinding | None] = {}
    inventories: dict[Path, _PreservedDirectoryInventory] = {}
    try:
        specdock_fd = _capture_preserved_directory_at(root_fd, Path("spec-dock"), bindings, required=True)
        assert specdock_fd is not None
        try:
            _capture_preserved_directory_inventory(
                specdock_fd,
                Path("spec-dock"),
                inventories,
                selection="allowed",
                allowed_names=frozenset({".agent", ".work", "active", "initiatives", "system"}),
            )
            with tempfile.TemporaryDirectory(prefix="spec-dock-preserved-") as tmp:
                snapshot_root = Path(tmp) / "repo"
                snapshot_specdock = snapshot_root / "spec-dock"
                snapshot_specdock.mkdir(parents=True)
                snapshot_root = snapshot_root.resolve()
                snapshot_specdock = snapshot_root / "spec-dock"

                placeholder_root = snapshot_specdock / "system" / "active-none"
                for layer in ("initiative", "epic", "issue"):
                    (placeholder_root / layer).mkdir(parents=True, exist_ok=True)

                system_rel = Path("spec-dock/system")
                system_fd = _capture_preserved_directory_at(
                    specdock_fd,
                    Path("system"),
                    bindings,
                    required=False,
                    binding_path=system_rel,
                )
                if system_fd is not None:
                    try:
                        _capture_preserved_directory_inventory(
                            system_fd,
                            system_rel,
                            inventories,
                            selection="allowed",
                            allowed_names=frozenset({"active-none"}),
                        )
                        active_none_rel = system_rel / "active-none"
                        active_none_fd = _capture_preserved_directory_at(
                            system_fd,
                            Path("active-none"),
                            bindings,
                            required=False,
                            binding_path=active_none_rel,
                        )
                        if active_none_fd is not None:
                            try:
                                _capture_preserved_directory_inventory(
                                    active_none_fd,
                                    active_none_rel,
                                    inventories,
                                    selection="allowed",
                                    allowed_names=frozenset({"initiative", "epic", "issue"}),
                                )
                                for layer in ("initiative", "epic", "issue"):
                                    layer_fd = _capture_preserved_directory_at(
                                        active_none_fd,
                                        Path(layer),
                                        bindings,
                                        required=False,
                                        binding_path=active_none_rel / layer,
                                    )
                                    if layer_fd is not None:
                                        try:
                                            _capture_preserved_directory_inventory(
                                                layer_fd,
                                                active_none_rel / layer,
                                                inventories,
                                                selection="all",
                                            )
                                        finally:
                                            os.close(layer_fd)
                            finally:
                                os.close(active_none_fd)
                    finally:
                        os.close(system_fd)

                initiatives_rel = Path("spec-dock/initiatives")
                initiatives_fd = _capture_preserved_directory_at(
                    specdock_fd,
                    Path("initiatives"),
                    bindings,
                    required=False,
                    binding_path=initiatives_rel,
                )
                snapshot_initiatives = snapshot_root / initiatives_rel
                snapshot_initiatives.mkdir()
                if initiatives_fd is not None:
                    try:
                        _snapshot_initiative_metadata(
                            initiatives_fd,
                            snapshot_initiatives,
                            initiatives_rel,
                            bindings,
                            inventories,
                        )
                    finally:
                        os.close(initiatives_fd)

                initiative_aliases = frozenset(
                    relative_path / name
                    for relative_path, inventory in inventories.items()
                    if inventory.selection == "initiative"
                    for name, child in inventory.children.items()
                    if stat.S_ISLNK(child.mode)
                )

                for directory_name, file_names in (
                    (".agent", ("active.json",)),
                    (".work", ("active.json", "current.json")),
                ):
                    directory_rel = Path("spec-dock") / directory_name
                    directory_fd = _capture_preserved_directory_at(
                        specdock_fd,
                        Path(directory_name),
                        bindings,
                        required=False,
                        binding_path=directory_rel,
                    )
                    snapshot_directory = snapshot_root / directory_rel
                    snapshot_directory.mkdir()
                    if directory_fd is None:
                        continue
                    try:
                        _capture_preserved_directory_inventory(
                            directory_fd,
                            directory_rel,
                            inventories,
                            selection="allowed",
                            allowed_names=frozenset(file_names),
                        )
                        for file_name in file_names:
                            file_rel = directory_rel / file_name
                            captured = _read_preserved_regular_at(
                                directory_fd,
                                Path(file_name),
                                bindings,
                                binding_path=file_rel,
                            )
                            if captured is None:
                                continue
                            content, mode, _binding = captured
                            target = snapshot_root / file_rel
                            target.write_bytes(
                                _snapshot_active_manifest(
                                    content,
                                    visible_root=visible_root,
                                    initiative_aliases=initiative_aliases,
                                )
                            )
                            target.chmod(mode)
                    finally:
                        os.close(directory_fd)

                active_rel = Path("spec-dock/active")
                active_fd = _capture_preserved_directory_at(
                    specdock_fd,
                    Path("active"),
                    bindings,
                    required=False,
                    binding_path=active_rel,
                )
                snapshot_active = snapshot_root / active_rel
                snapshot_active.mkdir()
                active_names = (
                    "initiative",
                    "epic",
                    "issue",
                    "initiative.path",
                    "epic.path",
                    "issue.path",
                    "context-pack.md",
                )
                if active_fd is not None:
                    try:
                        _capture_preserved_directory_inventory(
                            active_fd,
                            active_rel,
                            inventories,
                            selection="allowed",
                            allowed_names=frozenset(active_names),
                        )
                        active_entries = set(os.listdir(active_fd))  # noqa: PTH208
                        for name in active_names:
                            path_rel = active_rel / name
                            info = (
                                os.stat(name, dir_fd=active_fd, follow_symlinks=False)
                                if name in active_entries
                                else None
                            )
                            if info is None:
                                bindings[path_rel] = None
                                continue
                            if stat.S_ISLNK(info.st_mode):
                                link_target = os.readlink(name, dir_fd=active_fd)
                                if not _preserved_active_target_is_within_specdock(link_target):
                                    raise RuntimeError(
                                        "preserved active entrypoint has a symlink target outside spec-dock"
                                    )
                                current = os.stat(name, dir_fd=active_fd, follow_symlinks=False)
                                if (
                                    not stat.S_ISLNK(current.st_mode)
                                    or (current.st_dev, current.st_ino, current.st_ctime_ns)
                                    != (info.st_dev, info.st_ino, info.st_ctime_ns)
                                    or os.readlink(name, dir_fd=active_fd) != link_target
                                ):
                                    raise RuntimeError("preserved active entrypoint identity changed")
                                bindings[path_rel] = _preserved_read_binding(current, link_target=link_target)
                                (snapshot_active / name).symlink_to(link_target)
                                continue
                            if stat.S_ISDIR(info.st_mode):
                                bindings[path_rel] = _preserved_read_binding(info)
                                (snapshot_active / name).mkdir()
                                continue
                            if name in {"initiative", "epic", "issue"}:
                                raise RuntimeError("preserved active entrypoint is not a safe link or directory")
                            captured = _read_preserved_regular_at(
                                active_fd,
                                Path(name),
                                bindings,
                                binding_path=path_rel,
                            )
                            if captured is None:
                                raise RuntimeError("preserved active state disappeared")
                            content, mode, _binding = captured
                            if name.endswith(".path"):
                                try:
                                    pathfile_target = content.decode("utf-8").strip()
                                except UnicodeDecodeError as exc:
                                    raise RuntimeError("preserved active pathfile is not valid UTF-8") from exc
                                if not _preserved_active_target_is_within_specdock(pathfile_target):
                                    raise RuntimeError("preserved active pathfile target escapes spec-dock")
                            target = snapshot_active / name
                            target.write_bytes(content)
                            target.chmod(mode)
                    finally:
                        os.close(active_fd)

                def revalidate_preserved_state_before_service() -> None:
                    _revalidate_preserved_read_bindings(root_fd, bindings, inventories)

                def revalidate_preserved_state_during_service() -> None:
                    _revalidate_preserved_read_bindings(
                        root_fd,
                        bindings,
                        inventories,
                        allow_directory_metadata_changes=True,
                    )

                yield (
                    snapshot_specdock,
                    revalidate_preserved_state_before_service,
                    revalidate_preserved_state_during_service,
                )
        finally:
            os.close(specdock_fd)
    finally:
        os.close(root_fd)


def _active_fallback_existing_state_is_refreshable(
    specdock_dir: Path,
    *,
    active_dir: Path,
    layer: str,
    existing: tuple[Path, str | None] | None,
) -> bool:
    """Return whether an existing fallback pointer has managed-state evidence."""

    allowed_targets = {(specdock_dir / "system" / "active-none" / layer).resolve()}
    if existing is not None:
        allowed_targets.add(existing[0].resolve())

    def points_to_validated_active_target(pointer: Path, raw_target: str) -> bool:
        candidate = Path(raw_target)
        if not candidate.is_absolute():
            candidate = pointer.parent / candidate
        try:
            resolved = candidate.resolve()
        except OSError:
            return False
        return resolved in allowed_targets

    link = active_dir / layer
    pathfile = active_dir / f"{layer}.path"
    if link.is_symlink():
        try:
            return points_to_validated_active_target(link, link.readlink().as_posix())
        except OSError:
            return False
    if link.exists():
        return False
    if pathfile.is_file() and not pathfile.is_symlink():
        try:
            return points_to_validated_active_target(pathfile, pathfile.read_text(encoding="utf-8").strip())
        except OSError:
            return False
    return not pathfile.exists() and not pathfile.is_symlink()


def _active_fallback_refresh_identities(path: Path, *, allowed: bool) -> tuple[DistributionIdentity, ...]:
    """Bind generated refresh authority to the exact observed pointer identity."""

    if not allowed or (not path.exists() and not path.is_symlink()):
        return ()
    if path.is_symlink():
        try:
            return (DistributionIdentity(kind="symlink", target=path.readlink().as_posix()),)
        except OSError:
            return ()
    if not path.is_file():
        return ()
    try:
        before = path.stat(follow_symlinks=False)
        content = path.read_bytes()
        after = path.stat(follow_symlinks=False)
    except OSError:
        return ()
    if (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_nlink,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    ) != (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_nlink,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ) or after.st_nlink != 1:
        return ()
    return (
        DistributionIdentity(
            kind="regular",
            sha256=hashlib.sha256(content).hexdigest(),
            mode=stat.S_IMODE(after.st_mode),
        ),
    )


def _active_fallback_distribution_assets(specdock_dir: Path) -> tuple[DistributionAsset, ...]:
    """Describe active fallback state without mutating the recognized workspace."""

    active_dir = specdock_dir / "active"
    persisted = _load_persisted_active_entries(specdock_dir)
    assets: list[DistributionAsset] = []
    resolved_ids: dict[str, str | None] = {"initiative": None, "epic": None, "issue": None}
    for layer in ("initiative", "epic", "issue"):
        link = active_dir / layer
        pathfile = active_dir / f"{layer}.path"
        persisted_id, persisted_path = persisted[layer]
        try:
            existing = _resolve_existing_active_entrypoint(
                specdock_dir,
                active_dir=active_dir,
                layer=layer,
            )
        except RuntimeError:
            existing = None
        allow_existing_refresh = _active_fallback_existing_state_is_refreshable(
            specdock_dir,
            active_dir=active_dir,
            layer=layer,
            existing=existing,
        )
        if existing is not None and existing[1] is not None:
            desired_target, desired_id = existing
        else:
            resolved_target = _resolve_manifest_target_dir(
                specdock_dir,
                layer,
                expected_id=persisted_id,
                persisted_path=persisted_path,
            )
            if resolved_target is None:
                resolved_target = _resolve_persisted_path_dir(
                    specdock_dir,
                    layer=layer,
                    expected_id=persisted_id,
                    persisted_path=persisted_path,
                )
            desired_id = persisted_id if resolved_target is not None else None
            desired_target = resolved_target or specdock_dir / "system" / "active-none" / layer
        resolved_ids[layer] = desired_id
        desired_resolved = desired_target.resolve()

        current_link_target: str | None = None
        if link.is_symlink():
            with suppress(OSError, UnicodeDecodeError):
                raw_target = link.readlink()
                candidate = raw_target if raw_target.is_absolute() else link.parent / raw_target
                if candidate.resolve() == desired_resolved:
                    current_link_target = raw_target.as_posix()
        if current_link_target is not None:
            assets.append(
                _generated_symlink_distribution_asset(
                    f"spec-dock/active/{layer}",
                    current_link_target,
                    refreshable_existing_identities=_active_fallback_refresh_identities(
                        link,
                        allowed=allow_existing_refresh,
                    ),
                )
            )
            continue

        if (
            existing is not None
            and not link.exists()
            and not link.is_symlink()
            and pathfile.is_file()
            and not pathfile.is_symlink()
        ):
            with suppress(OSError):
                content = pathfile.read_bytes()
                if (active_dir / content.decode("utf-8").strip()).resolve() == desired_resolved:
                    assets.append(
                        _generated_regular_distribution_asset(
                            f"spec-dock/active/{layer}.path",
                            content,
                            refreshable_existing_identities=_active_fallback_refresh_identities(
                                pathfile,
                                allowed=allow_existing_refresh,
                            ),
                        )
                    )
                    continue

        if not _active_symlink_creation_supported():
            assets.append(
                _generated_regular_distribution_asset(
                    f"spec-dock/active/{layer}.path",
                    (os.path.relpath(desired_target, start=active_dir) + "\n").encode("utf-8"),
                    refreshable_existing_identities=_active_fallback_refresh_identities(
                        pathfile,
                        allowed=allow_existing_refresh,
                    ),
                )
            )
            continue

        assets.append(
            _generated_symlink_distribution_asset(
                f"spec-dock/active/{layer}",
                os.path.relpath(desired_target, start=active_dir),
                refreshable_existing_identities=_active_fallback_refresh_identities(
                    link,
                    allowed=allow_existing_refresh,
                ),
            )
        )

    context_pack = _render_context_pack(
        initiative_id=resolved_ids["initiative"],
        epic_id=resolved_ids["epic"],
        issue_id=resolved_ids["issue"],
    ).encode("utf-8")
    context_pack_path = active_dir / "context-pack.md"
    assets.append(
        _generated_regular_distribution_asset(
            "spec-dock/active/context-pack.md",
            context_pack,
            refreshable_existing_identities=_active_fallback_refresh_identities(
                context_pack_path,
                allowed=context_pack_path.is_file() and not context_pack_path.is_symlink(),
            ),
        )
    )
    return tuple(assets)


def _distribution_root_identity(target_root: Path) -> DistributionRootIdentity:
    """Return the no-follow identity of a real target root directory."""
    try:
        info = os.lstat(target_root)
    except OSError as exc:
        raise RuntimeError("distribution target root cannot be inspected safely") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise RuntimeError("distribution target root is not a real directory")
    return DistributionRootIdentity(device=info.st_dev, inode=info.st_ino)


def _assert_distribution_root_identity(
    target_root: Path,
    expected: DistributionRootIdentity,
) -> None:
    """Fail closed when a distribution retry is rebound to another root."""
    if _distribution_root_identity(target_root) != expected:
        raise RuntimeError("distribution target root identity changed")


@contextmanager
def _bound_distribution_root(
    target_root: Path,
    expected: DistributionRootIdentity | None = None,
) -> Iterator[tuple[Path, Path, DistributionRootIdentity]]:
    """Bind pathname operations to one opened repository-root directory.

    The visible root path is still checked before yielding and callers keep
    checking it around phase boundaries.  Actual scaffold/marker operations
    run with the opened directory as the process cwd, so a later rename and
    replacement of the visible root cannot redirect those relative writes to
    the replacement repository.
    """
    # ``cwd`` is process-global, so per-repository flock protection is not
    # sufficient when two installer operations target different roots in the
    # same process.  Serialize the complete absolute-path/bind/restore window.
    with _DISTRIBUTION_CWD_LOCK:
        identity_path = Path(target_root).absolute()
        bound_identity = expected or _distribution_root_identity(identity_path)
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int) or not hasattr(os, "fchdir"):
            raise RuntimeError("root-bound distribution operations are unavailable")
        root_flags = os.O_RDONLY | nofollow | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
        try:
            root_fd = os.open(identity_path, root_flags)
        except OSError as exc:
            raise RuntimeError("distribution target root cannot be opened safely") from exc
        cwd_fd: int | None = None
        try:
            root_stat = os.fstat(root_fd)
            if not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_nlink < 1:
                raise RuntimeError("distribution target root is not a real directory")
            if (root_stat.st_dev, root_stat.st_ino) != (
                bound_identity.device,
                bound_identity.inode,
            ):
                raise RuntimeError("distribution target root identity changed")
            cwd_fd = os.open(".", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
            os.fchdir(root_fd)
            _assert_distribution_root_identity(identity_path, bound_identity)
            yield Path(), identity_path, bound_identity
        finally:
            if cwd_fd is not None:
                with suppress(OSError):
                    os.fchdir(cwd_fd)
                with suppress(OSError):
                    os.close(cwd_fd)
            with suppress(OSError):
                os.close(root_fd)


def _distribution_retry_marker_path(target_root: Path) -> Path:
    return target_root / _DISTRIBUTION_RETRY_MARKER_REL


def _distribution_retry_marker_present(target_root: Path) -> bool:
    """Detect a published retry marker without following its final path."""
    try:
        os.lstat(_distribution_retry_marker_path(target_root))
    except FileNotFoundError:
        return False
    except OSError:
        # An unreadable or unsafe marker must still be treated as partial state;
        # the admission path will fail closed on the next invocation.
        return True
    return True


def _preflight_fresh_spec_dock_assets(assets_dir: Path) -> None:
    """Validate the Fresh scaffold sources before the first target write."""
    src_spec_dock = assets_dir / "spec_dock"
    if not src_spec_dock.is_dir() or src_spec_dock.is_symlink():
        raise RuntimeError("Missing asset directory: spec_dock")

    src_gitignore = src_spec_dock / ".gitignore"
    if not src_gitignore.is_file() or src_gitignore.is_symlink():
        raise RuntimeError("Missing asset file: spec_dock/.gitignore")

    for name in _MANAGED_DIRS:
        source = src_spec_dock / name
        if not source.is_dir() or source.is_symlink():
            raise RuntimeError(f"Invalid asset directory: spec_dock/{name}")

    runtime_script = src_spec_dock / "scripts" / "spec-dock"
    try:
        runtime_info = os.lstat(runtime_script)
    except FileNotFoundError as exc:
        raise RuntimeError("Missing asset file: spec_dock/scripts/spec-dock") from exc
    except OSError as exc:
        raise RuntimeError("Cannot inspect asset file: spec_dock/scripts/spec-dock") from exc
    if (
        stat.S_ISLNK(runtime_info.st_mode)
        or not stat.S_ISREG(runtime_info.st_mode)
        or runtime_info.st_nlink != 1
        or (stat.S_IMODE(runtime_info.st_mode) & 0o111) == 0
    ):
        raise RuntimeError("Invalid asset file: spec_dock/scripts/spec-dock")

    root_workbench_readme = src_spec_dock / "templates" / "root" / ".workbench" / "README.md"
    if not root_workbench_readme.is_file() or root_workbench_readme.is_symlink():
        raise RuntimeError("Missing asset file: spec_dock/templates/root/.workbench/README.md")


def _shell_join(argv: list[str]) -> str:
    """Serialize an argv vector for a copy/paste-safe retry command."""
    if os.name == "nt":
        return subprocess.list2cmdline(argv)
    return shlex.join(argv)


def _safe_retry_target_label(target_root: Path) -> str | None:
    """Return a caller-CWD-relative target or None when it cannot be represented."""
    try:
        label = os.path.relpath(target_root, Path.cwd())
    except (OSError, ValueError):
        return None
    if not label:
        label = "."
    if "\x00" in label or any(ord(char) < 0x20 for char in label):
        return None
    if os.name != "nt":
        label = Path(label).as_posix()
    if not label or Path(label).is_absolute():
        return None
    return label


def _require_retry_target_label(target_root: Path) -> str:
    label = _safe_retry_target_label(target_root)
    if label is None:
        raise RuntimeError("retry target cannot be represented safely from the current working directory")
    return label


def _distribution_retry_command(operation: DistributionOperation, *, target_label: str = ".") -> str:
    argv = ["spec-dock"]
    if operation == "fresh":
        argv.append("init")
    elif operation == "init-force":
        argv.extend(("init", "--force"))
    else:
        argv.append("update")
    if target_label.startswith("-"):
        argv.append("--")
    argv.append(target_label)
    return _shell_join(argv)


def _safe_distribution_failure_target(exc: BaseException, phase: str) -> str:
    """Return a repository-relative diagnostic target without leaking host paths."""
    match = re.search(r"for '([^']+)'", str(exc))
    if match:
        candidate = match.group(1)
        try:
            relative = Path(candidate)
            if (
                not relative.is_absolute()
                and "\\" not in candidate
                and ".." not in relative.parts
                and relative.as_posix() == candidate
            ):
                return candidate
        except (OSError, ValueError):
            pass
    return {
        "preflight": "distribution",
        "distribution-apply": "distribution",
        "managed-scaffold-refresh": "spec-dock",
        "current-external-materialize": "distribution",
        "obsolete-prune": "distribution",
        "scaffold-refresh": "spec-dock",
        "post-verify": "distribution",
        "version-write": "spec-dock/spec-dock.version",
        "marker-finalization": "spec-dock/.distribution-retry.json",
    }.get(phase, "spec-dock/.distribution-retry.json")


def _raise_distribution_partial_failure(
    exc: BaseException,
    *,
    target_root: Path,
    operation: DistributionOperation,
    phase: str,
    last_completed_phase: str,
    applied_paths: tuple[str, ...] = (),
    pending_paths: tuple[str, ...] = (),
) -> NoReturn:
    target = _safe_distribution_failure_target(exc, phase)
    target_label = _safe_retry_target_label(target_root)
    retry = (
        _distribution_retry_command(operation, target_label=target_label) if target_label is not None else "unavailable"
    )
    raise RuntimeError(
        f"distribution partial failure during {phase}; "
        f"target={target}; last_completed_phase={last_completed_phase}; "
        f"applied_paths={json.dumps(applied_paths, separators=(',', ':'))}; "
        f"pending_paths={json.dumps(pending_paths, separators=(',', ':'))}; "
        f"retry={retry}"
    ) from None


def _install_fresh_distribution(
    target_root: Path,
    *,
    requested_operation: _FreshDistributionIntent = "fresh",
) -> None:
    with _exclusive_distribution_operation(target_root) as locked_root_identity:
        admission = _admit_distribution_cli(target_root, operation=requested_operation)
        if admission.status not in {"fresh", "retry"} or (admission.intent != "fresh"):
            raise RuntimeError("Fresh distribution target changed during operation admission")
        _execute_fresh_distribution_unlocked(
            target_root,
            requested_operation=requested_operation,
            retry_marker=admission if admission.status == "retry" else None,
            expected_root_identity=locked_root_identity,
        )


def _prepare_fresh_workspace_boundary(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity,
) -> _ManagedPathIdentity | None:
    """Create the journal parent only when the fresh workspace is absent."""

    created_identity: _ManagedPathIdentity | None = None
    with _bound_distribution_root(target_root, expected_root_identity) as (
        bound_root,
        visible_root,
        bound_identity,
    ):
        specdock_dir = _specdock_dir(bound_root)
        try:
            info = os.lstat(specdock_dir)
        except FileNotFoundError:
            nofollow = getattr(os, "O_NOFOLLOW", None)
            directory = getattr(os, "O_DIRECTORY", None)
            if not isinstance(nofollow, int) or not isinstance(directory, int):
                raise RuntimeError("fresh workspace bootstrap requires no-follow directory support") from None
            parent_fd = os.open(
                ".",
                os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0),
            )
            try:
                try:
                    os.mkdir(specdock_dir.name, dir_fd=parent_fd)
                except FileExistsError as exc:
                    raise RuntimeError("Fresh distribution workspace appeared during bootstrap") from exc
                created_identity = _managed_path_identity(specdock_dir)
                os.fsync(parent_fd)
            except Exception:
                if created_identity is not None:
                    with suppress(OSError, RuntimeError):
                        _remove_empty_managed_directory(
                            target_root,
                            Path(_SPEC_DOCK_DIRNAME),
                            expected_identity=created_identity,
                            expected_root_identity=bound_identity,
                        )
                    created_identity = None
                raise
            finally:
                os.close(parent_fd)
            _assert_distribution_root_identity(visible_root, bound_identity)
            return created_identity
        except OSError as exc:
            raise RuntimeError("fresh workspace cannot be inspected safely") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_nlink < 1:
            raise RuntimeError("fresh workspace must be a real directory")
        _assert_distribution_root_identity(visible_root, bound_identity)
    return None


def _execute_fresh_distribution_unlocked(
    target_root: Path,
    *,
    requested_operation: _FreshDistributionIntent = "fresh",
    retry_marker: DistributionAdmission | None = None,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> None:
    """Run a fresh request through the shared journaled distribution service."""

    if requested_operation not in {"fresh", "update", "init-force"}:
        raise RuntimeError(f"unsupported fresh requested operation: {requested_operation}")
    _require_retry_target_label(target_root)
    root_identity = expected_root_identity or _distribution_root_identity(target_root)
    _assert_distribution_root_identity(target_root, root_identity)

    with _assets_dir() as packaged_assets_dir:
        assets_dir = packaged_assets_dir.resolve()
        _preflight_fresh_spec_dock_assets(assets_dir)
        preflight_plan = build_distribution_plan(
            assets_dir / "install_root",
            manifest_path=assets_dir / "managed_distribution.json",
            scaffold_root=assets_dir / "spec_dock",
            target_root=target_root,
            operation="fresh",
        )
        if preflight_plan.blocked:
            reasons = ", ".join(
                f"{action.path}: {action.reason}" for action in preflight_plan.actions if action.blocked
            )
            raise RuntimeError(f"distribution preflight blocked: {reasons}")

        created_workspace = _prepare_fresh_workspace_boundary(
            target_root,
            expected_root_identity=root_identity,
        )
        try:
            with _bound_distribution_root(target_root, root_identity) as (
                bound_root,
                visible_root,
                bound_identity,
            ):
                generated_assets = _active_fallback_distribution_assets(_specdock_dir(bound_root))
                result = execute_fresh_distribution(
                    assets_dir / "install_root",
                    manifest_path=assets_dir / "managed_distribution.json",
                    scaffold_root=assets_dir / "spec_dock",
                    target_root=bound_root,
                    package_version=_tool_version(),
                    legacy_marker=retry_marker.marker if retry_marker is not None else None,
                    generated_assets=generated_assets,
                    root_identity_path=visible_root,
                    created_workspace_identity=(
                        (created_workspace.device, created_workspace.inode) if created_workspace is not None else None
                    ),
                )
                if result.status != "recovery_required":
                    _assert_distribution_root_identity(visible_root, bound_identity)
        except Exception:
            if created_workspace is not None and not (
                _distribution_retry_marker_present(target_root)
                or os.path.lexists(target_root / "spec-dock/.distribution-journal.json")
            ):
                with suppress(OSError, RuntimeError):
                    _remove_empty_managed_directory(
                        target_root,
                        Path(_SPEC_DOCK_DIRNAME),
                        expected_identity=created_workspace,
                        expected_root_identity=root_identity,
                    )
            raise

    if result.status == "blocked":
        if created_workspace is not None:
            with suppress(OSError, RuntimeError):
                _remove_empty_managed_directory(
                    target_root,
                    Path(_SPEC_DOCK_DIRNAME),
                    expected_identity=created_workspace,
                    expected_root_identity=root_identity,
                )
        raise RuntimeError(f"distribution preflight blocked: {result.reason}")
    if result.status == "recovery_required":
        target_label = _require_retry_target_label(target_root)
        retry_operation: DistributionOperation = requested_operation
        if (
            retry_marker is not None
            and retry_marker.marker is not None
            and retry_marker.marker.purpose == "distribution-rerun"
        ):
            retry_operation = "fresh"
        retry = _distribution_retry_command(retry_operation, target_label=target_label)
        raise RuntimeError(
            "distribution partial failure during fresh provisioning; "
            "target=spec-dock/.distribution-journal.json; "
            f"applied_paths={json.dumps(result.applied_paths, separators=(',', ':'))}; "
            f"pending_paths={json.dumps(result.pending_paths, separators=(',', ':'))}; "
            f"retry={retry}; reason={result.reason}"
        )


def _install_recognized_distribution_unlocked(
    target_root: Path,
    *,
    operation: DistributionOperation,
    retry_marker: DistributionAdmission | None = None,
    expected_root_identity: DistributionRootIdentity | None = None,
    version_identity: DistributionIdentity | None = None,
) -> None:
    """Execute recognized intents through the unified journaled service."""
    if operation not in {"update", "init-force"}:
        raise RuntimeError(f"unsupported recognized distribution operation: {operation}")
    recognized_operation: RecognizedDistributionIntent = "update" if operation == "update" else "init-force"
    with _assets_dir() as packaged_assets_dir:
        assets_dir = packaged_assets_dir.resolve()
        with _bound_distribution_root(target_root, expected_root_identity) as (
            bound_root,
            visible_root,
            bound_identity,
        ):
            with _recognized_preserved_state_snapshot(bound_root, visible_root=visible_root) as (
                snapshot_specdock,
                revalidate_preserved,
                revalidate_preserved_during_service,
            ):
                generated_assets = _active_fallback_distribution_assets(snapshot_specdock)
                revalidate_preserved()
                result = execute_recognized_distribution(
                    assets_dir / "install_root",
                    manifest_path=assets_dir / "managed_distribution.json",
                    scaffold_root=assets_dir / "spec_dock",
                    target_root=bound_root,
                    intent=recognized_operation,
                    package_version=_tool_version(),
                    legacy_marker=retry_marker.marker if retry_marker is not None else None,
                    generated_assets=generated_assets,
                    version_refreshable_existing_identities=(version_identity,) if version_identity is not None else (),
                    root_identity_path=visible_root,
                    preserved_state_validator=revalidate_preserved_during_service,
                )
            if result.status != "recovery_required":
                _assert_distribution_root_identity(visible_root, bound_identity)
    if result.status == "blocked":
        raise RuntimeError(f"distribution preflight blocked: {result.reason}")
    if result.status == "recovery_required":
        target_label = _require_retry_target_label(target_root)
        retry = _distribution_retry_command(operation, target_label=target_label)
        raise RuntimeError(
            "distribution partial failure during reconciliation; "
            "target=spec-dock/.distribution-journal.json; "
            f"applied_paths={json.dumps(result.applied_paths, separators=(',', ':'))}; "
            f"pending_paths={json.dumps(result.pending_paths, separators=(',', ':'))}; "
            f"retry={retry}; reason={result.reason}"
        )


def _install_recognized_distribution(
    target_root: Path,
    *,
    operation: DistributionOperation,
) -> None:
    with _exclusive_distribution_operation(target_root) as locked_root_identity:
        admission = _admit_distribution_cli(target_root, operation=operation)
        if operation in {"update", "init-force"} and (
            admission.status == "fresh" or (admission.status == "retry" and admission.intent == "fresh")
        ):
            fresh_operation = cast("_FreshDistributionIntent", operation)
            _execute_fresh_distribution_unlocked(
                target_root,
                requested_operation=fresh_operation,
                retry_marker=admission if admission.status == "retry" else None,
                expected_root_identity=locked_root_identity,
            )
            return
        if admission.status not in {"recognized", "retry", "uninstall-retry"}:
            raise RuntimeError("recognized distribution target changed during operation admission")
        _install_recognized_distribution_unlocked(
            target_root,
            operation=operation,
            retry_marker=admission if admission.status == "retry" else None,
            expected_root_identity=locked_root_identity,
            version_identity=admission.version_identity,
        )


def _managed_skill_names() -> tuple[str, ...]:
    """Return the managed bundled skill set."""
    return _MANAGED_SKILL_NAMES


def _is_within_managed_obsolete_exact_path_prefixes(path: Path) -> bool:
    rel_posix = path.as_posix()
    return any(rel_posix.startswith(prefix) for prefix in _MANAGED_OBSOLETE_EXACT_PATH_PREFIXES)


def _is_path_prefix(prefix: Path, candidate: Path) -> bool:
    prefix_parts = prefix.parts
    candidate_parts = candidate.parts
    return len(prefix_parts) < len(candidate_parts) and candidate_parts[: len(prefix_parts)] == prefix_parts


def _managed_obsolete_cleanup_boundary(rel_path: Path) -> Path | None:
    for prefix in _MANAGED_OBSOLETE_EXACT_PATH_PREFIXES:
        boundary = Path(prefix.rstrip("/"))
        if boundary.parts == rel_path.parts[: len(boundary.parts)]:
            return boundary
    return None


def _parent_dirs_for(rel_path: Path) -> tuple[Path, ...]:
    parents: list[Path] = []
    current = rel_path.parent
    while current.parts not in {(), (".",)}:
        parents.append(current)
        current = current.parent
    return tuple(parents)


def _prune_empty_obsolete_parent_dirs(
    target_root: Path,
    obsolete_rel: Path,
    *,
    protected_rel_dirs: set[Path],
) -> None:
    boundary = _managed_obsolete_cleanup_boundary(obsolete_rel)
    if boundary is None:
        return

    current = obsolete_rel.parent
    while len(boundary.parts) < len(current.parts):
        if current in protected_rel_dirs:
            return
        target_path = target_root / current
        if not target_path.exists() or not target_path.is_dir() or target_path.is_symlink():
            return
        try:
            target_path.rmdir()
        except OSError:
            return
        current = current.parent


def _uninstall_specs_mode(ns: argparse.Namespace) -> str | None:
    if getattr(ns, "keep_specs", False):
        return "keep"
    if getattr(ns, "remove_specs", False):
        return "remove"
    return None


def _is_safe_managed_removal_rel_path(rel_path: Path) -> bool:
    """Allow only installer-owned roots for rollback cleanup."""
    return rel_path == Path(_SPEC_DOCK_DIRNAME) or rel_path in _MANAGED_SCAFFOLD_ROOTS


def _managed_removal_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if not isinstance(nofollow, int) or not isinstance(directory, int):
        raise RuntimeError("platform lacks required no-follow directory support for uninstall")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _assert_managed_removal_visible_chain(
    target_root: Path,
    rel_path: Path,
    fds: tuple[int, ...],
) -> None:
    parts = rel_path.parts
    for index, fd in enumerate(fds):
        visible = target_root.joinpath(*parts[:index]) if index else target_root
        try:
            visible_stat = os.lstat(visible)
            held_stat = os.fstat(fd)
        except OSError as exc:
            raise RuntimeError("managed scaffold target path changed during safe operation") from exc
        if (
            stat.S_ISLNK(visible_stat.st_mode)
            or visible_stat.st_dev != held_stat.st_dev
            or visible_stat.st_ino != held_stat.st_ino
            or not stat.S_ISDIR(held_stat.st_mode)
        ):
            raise RuntimeError("managed scaffold target path changed during safe operation")


@contextmanager
def _open_managed_removal_parent_chain(
    target_root: Path,
    rel_path: Path,
    *,
    create_missing: bool = False,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> Iterator[tuple[int, ...]]:
    """Open an managed scaffold target's parent chain without following symlinks."""

    if not _is_safe_managed_removal_rel_path(rel_path):
        raise RuntimeError("unsafe uninstall path outside managed boundaries")
    flags = _managed_removal_directory_flags()
    fds: list[int] = []
    try:
        root_fd = os.open(target_root, flags)
        fds.append(root_fd)
        root_stat = os.fstat(root_fd)
        if not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_nlink < 1:
            raise RuntimeError("managed scaffold target root is not a real directory")
        if expected_root_identity is not None and (
            root_stat.st_dev,
            root_stat.st_ino,
        ) != (
            expected_root_identity.device,
            expected_root_identity.inode,
        ):
            raise RuntimeError("distribution target root identity changed")

        for component in rel_path.parts[:-1]:
            try:
                next_fd = os.open(component, flags, dir_fd=fds[-1])
            except FileNotFoundError:
                if not create_missing:
                    raise RuntimeError(
                        f"managed scaffold target parent is missing for '{rel_path.as_posix()}'"
                    ) from None
                os.mkdir(component, dir_fd=fds[-1])
                next_fd = os.open(component, flags, dir_fd=fds[-1])
            except OSError as exc:
                raise RuntimeError(f"managed scaffold target parent is unsafe for '{rel_path.as_posix()}'") from exc
            fds.append(next_fd)
        chain = tuple(fds)
        _assert_managed_removal_visible_chain(target_root, rel_path, chain)
        yield chain
    except FileExistsError:
        raise RuntimeError(f"managed scaffold target parent changed for '{rel_path.as_posix()}'") from None
    except OSError as exc:
        raise RuntimeError("managed scaffold target cannot be opened safely") from exc
    finally:
        for fd in reversed(fds):
            with suppress(OSError):
                os.close(fd)


def _assert_managed_removal_directory_binding(target_root: Path, rel_path: Path, directory_fd: int) -> None:
    """Require a held directory descriptor to remain at its repository path."""
    try:
        visible = os.lstat(target_root / rel_path)
        held = os.fstat(directory_fd)
    except OSError as exc:
        raise RuntimeError("managed scaffold target path changed during safe operation") from exc
    if (
        stat.S_ISLNK(visible.st_mode)
        or not stat.S_ISDIR(visible.st_mode)
        or not stat.S_ISDIR(held.st_mode)
        or visible.st_dev != held.st_dev
        or visible.st_ino != held.st_ino
    ):
        raise RuntimeError("managed scaffold target path changed during safe operation")


def _assert_managed_removal_tree_entry_identity(
    directory_fd: int,
    name: str,
    expected: os.stat_result,
) -> None:
    """Reject a recursive entry that was replaced after it was observed."""
    try:
        current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except OSError as exc:
        raise RuntimeError("managed scaffold target changed during safe operation") from exc
    identity_matches = (
        current.st_dev,
        current.st_ino,
        current.st_mode,
    ) == (
        expected.st_dev,
        expected.st_ino,
        expected.st_mode,
    )
    if not stat.S_ISDIR(expected.st_mode):
        identity_matches = identity_matches and current.st_ctime_ns == expected.st_ctime_ns
    if not identity_matches:
        raise RuntimeError("managed scaffold target changed during safe operation")


def _remove_managed_tree_fd(
    target_root: Path,
    rel_path: Path,
    directory_fd: int,
    visible_fds: tuple[int, ...],
) -> None:
    """Remove an installer-owned tree while preserving repository binding."""
    _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
    _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)

    for name in os.listdir(directory_fd):
        _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
        _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISLNK(entry.st_mode):
            raise RuntimeError("refusing to remove symlink inside managed scaffold target")
        if stat.S_ISDIR(entry.st_mode):
            child_rel_path = rel_path / name
            child_fd = os.open(name, _managed_removal_directory_flags(), dir_fd=directory_fd)
            try:
                _remove_managed_tree_fd(
                    target_root,
                    child_rel_path,
                    child_fd,
                    (*visible_fds, child_fd),
                )
                _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
                _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
                _assert_managed_removal_directory_binding(target_root, child_rel_path, child_fd)
                _assert_managed_removal_tree_entry_identity(directory_fd, name, entry)
                os.rmdir(name, dir_fd=directory_fd)
            finally:
                os.close(child_fd)
            continue
        if stat.S_ISREG(entry.st_mode) and entry.st_nlink != 1:
            raise RuntimeError("refusing to remove hard-linked managed scaffold target")
        if not stat.S_ISREG(entry.st_mode):
            raise RuntimeError("refusing to remove unsafe entry inside managed scaffold target")
        _assert_managed_removal_tree_entry_identity(directory_fd, name, entry)
        _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
        _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
        os.unlink(name, dir_fd=directory_fd)


def _remove_managed_bound_directory_tree(
    target_root: Path,
    rel_path: Path,
    *,
    expected_identity: _ManagedPathIdentity,
    expected_root_identity: DistributionRootIdentity | None,
) -> None:
    """Remove one already-authorized directory through held no-follow descriptors."""
    with _open_managed_removal_parent_chain(
        target_root,
        rel_path,
        expected_root_identity=expected_root_identity,
    ) as fds:
        parent_fd = fds[-1]
        try:
            visible = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
        except OSError as exc:
            raise RuntimeError("managed scaffold target changed during safe replacement") from exc
        if (
            stat.S_ISLNK(visible.st_mode)
            or not stat.S_ISDIR(visible.st_mode)
            or (visible.st_dev, visible.st_ino, visible.st_ctime_ns)
            != (expected_identity.device, expected_identity.inode, expected_identity.ctime_ns)
        ):
            raise RuntimeError("managed scaffold target identity changed")

        directory_fd = os.open(rel_path.name, _managed_removal_directory_flags(), dir_fd=parent_fd)
        try:
            held = os.fstat(directory_fd)
            if not stat.S_ISDIR(held.st_mode) or (held.st_dev, held.st_ino, held.st_ctime_ns) != (
                expected_identity.device,
                expected_identity.inode,
                expected_identity.ctime_ns,
            ):
                raise RuntimeError("managed scaffold target identity changed")
            visible_fds = (*fds, directory_fd)
            _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
            _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
            _remove_managed_tree_fd(target_root, rel_path, directory_fd, visible_fds)
            _assert_managed_removal_visible_chain(target_root, rel_path, fds)
            _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
            _assert_managed_removal_tree_entry_identity(parent_fd, rel_path.name, visible)
            os.rmdir(rel_path.name, dir_fd=parent_fd)
        finally:
            os.close(directory_fd)


def _remove_empty_managed_directory(
    target_root: Path,
    rel_path: Path,
    *,
    expected_identity: _ManagedPathIdentity,
    expected_root_identity: DistributionRootIdentity | None,
) -> None:
    """Remove an empty directory only while its captured identity remains bound."""
    with _open_managed_removal_parent_chain(
        target_root,
        rel_path,
        expected_root_identity=expected_root_identity,
    ) as fds:
        parent_fd = fds[-1]
        try:
            visible = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
        except OSError as exc:
            raise RuntimeError("empty directory target changed during safe cleanup") from exc
        if (
            stat.S_ISLNK(visible.st_mode)
            or not stat.S_ISDIR(visible.st_mode)
            or (visible.st_dev, visible.st_ino, visible.st_ctime_ns)
            != (expected_identity.device, expected_identity.inode, expected_identity.ctime_ns)
        ):
            raise RuntimeError("empty directory target identity changed during safe cleanup")

        directory_fd = os.open(rel_path.name, _managed_removal_directory_flags(), dir_fd=parent_fd)
        try:
            held = os.fstat(directory_fd)
            if not stat.S_ISDIR(held.st_mode) or (held.st_dev, held.st_ino, held.st_ctime_ns) != (
                expected_identity.device,
                expected_identity.inode,
                expected_identity.ctime_ns,
            ):
                raise RuntimeError("empty directory target identity changed during safe cleanup")
            visible_fds = (*fds, directory_fd)
            _assert_managed_removal_visible_chain(target_root, rel_path, visible_fds)
            _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
            with os.scandir(directory_fd) as entries:
                if next(entries, None) is not None:
                    raise RuntimeError("empty directory target is no longer empty")
            _assert_managed_removal_visible_chain(target_root, rel_path, fds)
            _assert_managed_removal_directory_binding(target_root, rel_path, directory_fd)
            _assert_managed_removal_tree_entry_identity(parent_fd, rel_path.name, visible)
            current = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino, current.st_ctime_ns) != (
                expected_identity.device,
                expected_identity.inode,
                expected_identity.ctime_ns,
            ):
                raise RuntimeError("empty directory target identity changed during safe cleanup")
            os.rmdir(rel_path.name, dir_fd=parent_fd)
            _assert_managed_removal_visible_chain(target_root, rel_path, fds)
        finally:
            os.close(directory_fd)


def _remove_managed_scaffold_tree(
    target_root: Path,
    dest: Path,
    *,
    expected_identity: _ManagedPathIdentity,
    expected_root_identity: DistributionRootIdentity | None,
) -> None:
    """Remove one managed scaffold root through held no-follow descriptors."""
    try:
        rel_path = dest.absolute().relative_to(target_root.absolute())
    except ValueError as exc:
        raise RuntimeError("managed scaffold target is outside the distribution root") from exc
    if rel_path not in _MANAGED_SCAFFOLD_ROOTS:
        raise RuntimeError("managed scaffold replacement is outside the managed roots")
    _remove_managed_bound_directory_tree(
        target_root,
        rel_path,
        expected_identity=expected_identity,
        expected_root_identity=expected_root_identity,
    )


def _uninstall_retry_command(specs_mode: str | None, *, target_label: str = ".") -> str | None:
    if specs_mode not in {"keep", "remove"}:
        return None
    mode = "keep-specs" if specs_mode == "keep" else "remove-specs"
    argv = ["spec-dock", "uninstall", "--apply", f"--{mode}"]
    if target_label.startswith("-"):
        argv.append("--")
    argv.append(target_label)
    return _shell_join(argv)


def _validate_uninstall_process_result(
    result: DistributionProcessResult,
    *,
    specs_mode: str | None,
) -> None:
    """Validate the typed service result for the selected public authority."""

    accepted_pair = (result.intent == "deprovision" and specs_mode in {None, "keep"}) or (
        result.intent == "purge" and specs_mode == "remove"
    )
    if not accepted_pair or result.phase is None or result.last_completed_phase is None:
        raise RuntimeError("managed uninstall service returned an incomplete or mismatched typed result")
    if result.retry_policy == "same-keep-command" and result.intent == "purge":
        raise RuntimeError("managed uninstall service returned an invalid purge retry policy")
    if result.retry_policy == "same-remove-command" and result.intent == "deprovision":
        raise RuntimeError("managed uninstall service returned an invalid deprovision retry policy")
    if result.pending_paths != tuple(sorted(set(result.pending_paths), key=os.fsencode)):
        raise RuntimeError("managed uninstall service returned non-canonical pending paths")
    if result.failed_paths != tuple(sorted(set(result.failed_paths), key=os.fsencode)):
        raise RuntimeError("managed uninstall service returned non-canonical failed paths")
    if not set(result.pending_paths).issubset(result.failed_paths):
        raise RuntimeError("managed uninstall service returned pending paths without failure diagnostics")
    if result.status in {"planned", "completed"}:
        if result.errors or result.failed_paths or result.pending_paths:
            raise RuntimeError("managed uninstall success result contains failure state")
    elif not result.errors:
        raise RuntimeError("managed uninstall failure result is missing its operation error")


def _uninstall_exit_code_from_result(result: DistributionProcessResult) -> int:
    """Map the typed service status to the stable public uninstall exit code."""

    return {
        "planned": 0,
        "completed": 0,
        "blocked": 1,
        "recovery_required": 1,
        "error": 2,
    }[result.status]


def _summarize_uninstall_outcomes(result: DistributionProcessResult) -> dict[str, int]:
    summary = {
        "would_remove": 0,
        "removed": 0,
        "already_removed": 0,
        "preserved": 0,
        "failed": 0,
        "pending": 0,
        "empty_dir_removed": 0,
    }
    for outcome in result.action_outcomes:
        summary[outcome.status] += 1
    return summary


def _uninstall_guidance_from_result(
    result: DistributionProcessResult,
    *,
    apply: bool,
) -> list[str]:
    if result.retry_policy == "manual-recovery":
        primary = {
            "legacy-marker-unconvertible": (
                "manual recovery required: legacy installer state does not prove its root, specs mode, or checkpoint"
            ),
            "legacy-marker-invalid": (
                "manual recovery required: invalid legacy installer state does not prove its root, specs mode, or checkpoint"
            ),
            "dual-recovery-state": (
                "manual recovery required: conflicting legacy and schema-2 recovery states prove no single plan or checkpoint"
            ),
        }.get(
            result.reason or "",
            "manual recovery required: managed recovery evidence cannot prove one safe plan or checkpoint",
        )
    elif result.retry_policy == "same-remove-command" and result.intent == "purge" and apply:
        primary = "retry removal with installer CLI: spec-dock uninstall <target> --apply --remove-specs"
    elif result.retry_policy == "same-remove-command" and result.intent == "purge":
        primary = "dry-run only; pass --apply --remove-specs to mutate managed distribution artifacts"
    elif result.retry_policy == "same-keep-command" and apply:
        primary = "retry removal with installer CLI: spec-dock uninstall <target> --apply --keep-specs"
    elif result.retry_policy == "same-keep-command":
        primary = "dry-run only; pass --apply --keep-specs to mutate managed distribution artifacts"
    else:
        primary = "automatic uninstall retry is unavailable; inspect the managed distribution result"
    return [
        primary,
        "reinstall or refresh with installer CLI: spec-dock init <target> or spec-dock update <target>",
    ]


_UNINSTALL_PUBLIC_OPERATION_ERRORS = {
    "deprovision-preflight-failed": "Managed distribution deprovision preflight failed.",
    "purge-preflight-failed": "Managed distribution spec-history purge preflight failed.",
    "deprovision-target-not-directory": "target path is not a directory",
    "purge-target-not-directory": "target path is not a directory",
    "deprovision-specs-mode-required": (
        "uninstall --apply requires exactly one specs mode: --keep-specs or --remove-specs"
    ),
    "deprovision-retry-target-unrepresentable": (
        "retry target cannot be represented safely from the current working directory"
    ),
    "deprovision-root-binding-required": "Managed distribution deprovision requires a bound target root.",
    "deprovision-root-binding-mismatch": "Managed distribution deprovision target binding changed.",
    "purge-root-binding-required": "Managed distribution spec-history purge requires a bound target root.",
    "purge-root-binding-mismatch": "Managed distribution spec-history purge target binding changed.",
    "managed-workspace-evidence-missing": (
        "target is not a managed SpecDock repo: missing managed "
        "'spec-dock/spec-dock.version' state or exact managed distribution evidence"
    ),
    "deprovision-preflight-blocked": "Managed distribution deprovision is blocked by preserved state.",
    "deprovision-no-op-postcondition-changed": "Managed distribution deprovision is blocked by preserved state.",
    "purge-preflight-blocked": "Managed distribution spec-history purge is blocked by preserved state.",
    "purge-no-op-postcondition-changed": "Managed distribution spec-history purge is blocked by preserved state.",
    "deprovision-recovery-required": "Managed distribution deprovision recovery is required.",
    "deprovision-recovery-mismatch": "Managed distribution deprovision recovery evidence does not match.",
    "purge-recovery-required": "Managed distribution spec-history purge recovery is required.",
    "purge-recovery-mismatch": "Managed distribution spec-history purge recovery evidence does not match.",
    "legacy-marker-unconvertible": "Legacy uninstall recovery requires manual review.",
    "legacy-marker-invalid": "Legacy uninstall recovery evidence is invalid.",
    "dual-recovery-state": "Conflicting uninstall recovery evidence requires manual review.",
}
_UNINSTALL_GENERIC_OPERATION_ERROR = "Managed distribution deprovision failed."
_PURGE_GENERIC_OPERATION_ERROR = "Managed distribution spec-history purge failed."
_UNINSTALL_GENERIC_ACTION_ERROR = "Managed distribution deprovision action failed."
_PURGE_GENERIC_ACTION_ERROR = "Managed distribution spec-history purge action failed."


def _uninstall_public_operation_error(error: DistributionProcessError) -> str:
    if error.code.startswith("purge-"):
        return _UNINSTALL_PUBLIC_OPERATION_ERRORS.get(error.code, _PURGE_GENERIC_OPERATION_ERROR)
    return _UNINSTALL_PUBLIC_OPERATION_ERRORS.get(error.code, _UNINSTALL_GENERIC_OPERATION_ERROR)


def _uninstall_public_action_error(error: str | None, *, intent: str) -> str | None:
    if error is None:
        return None
    return _PURGE_GENERIC_ACTION_ERROR if intent == "purge" else _UNINSTALL_GENERIC_ACTION_ERROR


def _uninstall_payload_from_result(
    result: DistributionProcessResult,
    *,
    target_root: Path,
    apply: bool,
    specs_mode: str | None,
) -> dict[str, Any]:
    """Map one typed uninstall result without interpreting durable state."""

    _validate_uninstall_process_result(result, specs_mode=specs_mode)
    public_status = {
        "planned": "planned",
        "completed": "completed",
        "blocked": "blocked",
        "recovery_required": "partial_failure",
        "error": "error",
    }[result.status]
    safe_target_label = _safe_retry_target_label(target_root)
    sanitized_failure = public_status in {"blocked", "partial_failure"}
    retry_command = None
    retry_mode = "remove" if result.intent == "purge" else "keep"
    retry_policy = "same-remove-command" if result.intent == "purge" else "same-keep-command"
    retry_authority_selected = specs_mode == ("remove" if result.intent == "purge" else "keep")
    if (
        result.retry_policy == retry_policy
        and safe_target_label is not None
        and retry_authority_selected
        and (result.intent != "purge" or apply)
    ):
        retry_command = _uninstall_retry_command(retry_mode, target_label=safe_target_label)
    return {
        "schema_version": 1,
        "target": (safe_target_label or "unavailable") if sanitized_failure else str(target_root),
        "mode": "apply" if apply else "dry-run",
        "apply": apply,
        "specs_mode": specs_mode,
        "status": public_status,
        "phase": result.phase,
        "last_completed_phase": result.last_completed_phase,
        "retry_command": retry_command,
        "failed_paths": list(result.failed_paths),
        "pending_paths": list(result.pending_paths),
        "summary": _summarize_uninstall_outcomes(result),
        "actions": [
            {
                "path": outcome.path,
                "category": outcome.category,
                "status": outcome.status,
                "reason": outcome.reason,
                "error": _uninstall_public_action_error(outcome.error, intent=result.intent),
            }
            for outcome in result.action_outcomes
        ],
        "guidance": _uninstall_guidance_from_result(result, apply=apply),
        "errors": [_uninstall_public_operation_error(error) for error in result.errors],
    }


def _render_uninstall_text(payload: dict[str, Any]) -> str:
    noun = "result" if payload["apply"] else "plan"
    lines = [
        f"spec-dock: uninstall {noun} ({payload['mode']}) -> {payload['target']}",
        f"specs_mode: {payload['specs_mode'] or 'unspecified'}",
        f"status: {payload['status']}",
        f"phase: {payload['phase']}",
        f"last_completed_phase: {payload['last_completed_phase']}",
        f"retry_command: {payload['retry_command'] or 'unavailable'}",
        f"failed_paths: {', '.join(payload.get('failed_paths', [])) or 'none'}",
        "summary:",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"  {key}: {value}")
    lines.append("actions:")
    for action in payload["actions"]:
        line = f"  [{action['status']}] {action['path']} category={action['category']} reason={action['reason']}"
        if action.get("error"):
            line += f" error={action['error']}"
        lines.append(line)
    if payload.get("errors"):
        lines.append("errors:")
        for error in payload["errors"]:
            lines.append(f"  - {error}")
    lines.append("guidance:")
    for item in payload["guidance"]:
        lines.append(f"  - {item}")
    return "\n".join(lines)


def _deprovision_request_error_result(
    message: str,
    *,
    code: str = "deprovision-preflight-failed",
) -> DistributionProcessResult:
    return DistributionProcessResult(
        status="error",
        intent="deprovision",
        actions=(),
        phase="preflight",
        last_completed_phase="not-started",
        errors=(
            DistributionProcessError(
                code=code,
                message=message,
            ),
        ),
        retry_policy="same-keep-command",
    )


def _purge_request_error_result(
    message: str,
    *,
    code: str = "purge-preflight-failed",
) -> DistributionProcessResult:
    return DistributionProcessResult(
        status="error",
        intent="purge",
        actions=(),
        phase="preflight",
        last_completed_phase="not-started",
        errors=(
            DistributionProcessError(
                code=code,
                message=message,
            ),
        ),
        retry_policy="none",
    )


def _emit_uninstall_result(
    result: DistributionProcessResult,
    *,
    target_root: Path,
    apply: bool,
    specs_mode: str | None,
    json_requested: bool,
) -> int:
    payload = _uninstall_payload_from_result(
        result,
        target_root=target_root,
        apply=apply,
        specs_mode=specs_mode,
    )
    if json_requested:
        print(json.dumps(payload, sort_keys=True))
    elif result.status == "error":
        message = payload["errors"][0] if payload["errors"] else _UNINSTALL_GENERIC_OPERATION_ERROR
        print(f"error: {message}", file=sys.stderr)
    else:
        print(_render_uninstall_text(payload))
    return _uninstall_exit_code_from_result(result)


def _run_uninstall_deprovision(
    target_root: Path,
    ns: argparse.Namespace,
    *,
    specs_mode: str | None,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> int:
    """Adapt default/keep uninstall requests to the managed deprovision service."""

    if specs_mode not in {None, "keep"}:
        raise RuntimeError("deprovision route received non-keep specs authority")
    apply_requested = bool(ns.apply)
    json_requested = bool(ns.json)
    if not target_root.exists() or not target_root.is_dir():
        result = _deprovision_request_error_result(
            "target path is not a directory",
            code="deprovision-target-not-directory",
        )
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
        )
    if apply_requested and specs_mode is None:
        result = _deprovision_request_error_result(
            "uninstall --apply requires exactly one specs mode: --keep-specs or --remove-specs",
            code="deprovision-specs-mode-required",
        )
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=True,
            specs_mode=None,
            json_requested=json_requested,
        )
    try:
        _require_retry_target_label(target_root)
    except RuntimeError:
        result = _deprovision_request_error_result(
            "retry target cannot be represented safely from the current working directory",
            code="deprovision-retry-target-unrepresentable",
        )
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
        )
    try:
        with _assets_dir() as packaged_assets_dir:
            assets_dir = packaged_assets_dir.resolve()
            result = execute_deprovision_distribution(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                package_version=_tool_version(),
                apply=apply_requested,
                expected_root_identity=expected_root_identity,
            )
    except (OSError, RuntimeError):
        result = _deprovision_request_error_result("Managed distribution deprovision preflight failed.")
    return _emit_uninstall_result(
        result,
        target_root=target_root,
        apply=apply_requested,
        specs_mode=specs_mode,
        json_requested=json_requested,
    )


def _run_uninstall_explicit_spec_history_purge(
    target_root: Path,
    ns: argparse.Namespace,
    *,
    specs_mode: str,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> int:
    """Adapt explicit ``--remove-specs`` requests to the typed purge service."""

    if specs_mode != "remove":
        raise RuntimeError("explicit spec-history purge route requires remove authority")
    apply_requested = bool(ns.apply)
    json_requested = bool(ns.json)
    if not target_root.exists() or not target_root.is_dir():
        result = _purge_request_error_result(
            "target path is not a directory",
            code="purge-target-not-directory",
        )
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
        )
    try:
        _require_retry_target_label(target_root)
    except RuntimeError:
        result = _purge_request_error_result(
            "retry target cannot be represented safely from the current working directory",
        )
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
        )
    try:
        with _assets_dir() as packaged_assets_dir:
            assets_dir = packaged_assets_dir.resolve()
            result = execute_explicit_spec_history_purge_distribution(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                package_version=_tool_version(),
                apply=apply_requested,
                expected_root_identity=expected_root_identity,
            )
    except (OSError, RuntimeError):
        result = _purge_request_error_result("Managed distribution spec-history purge preflight failed.")
    return _emit_uninstall_result(
        result,
        target_root=target_root,
        apply=apply_requested,
        specs_mode=specs_mode,
        json_requested=json_requested,
    )


def _run_uninstall(target_root: Path, ns: argparse.Namespace) -> int:
    specs_mode = _uninstall_specs_mode(ns)
    apply_requested = bool(ns.apply)
    if specs_mode == "remove":
        if not apply_requested:
            return _run_uninstall_explicit_spec_history_purge(
                target_root,
                ns,
                specs_mode=specs_mode,
            )
        try:
            with _exclusive_distribution_operation(target_root) as locked_root_identity:
                return _run_uninstall_explicit_spec_history_purge(
                    target_root,
                    ns,
                    specs_mode=specs_mode,
                    expected_root_identity=locked_root_identity,
                )
        except (OSError, RuntimeError):
            result = _purge_request_error_result("Managed distribution spec-history purge preflight failed.")
            return _emit_uninstall_result(
                result,
                target_root=target_root,
                apply=True,
                specs_mode=specs_mode,
                json_requested=bool(ns.json),
            )

    if not apply_requested or specs_mode is None or not target_root.exists() or not target_root.is_dir():
        return _run_uninstall_deprovision(
            target_root,
            ns,
            specs_mode=specs_mode,
        )
    try:
        with _exclusive_distribution_operation(target_root) as locked_root_identity:
            return _run_uninstall_deprovision(
                target_root,
                ns,
                specs_mode=specs_mode,
                expected_root_identity=locked_root_identity,
            )
    except (OSError, RuntimeError):
        result = _deprovision_request_error_result("Managed distribution deprovision preflight failed.")
        return _emit_uninstall_result(
            result,
            target_root=target_root,
            apply=True,
            specs_mode=specs_mode,
            json_requested=bool(ns.json),
        )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments (installer commands only)."""
    parser = argparse.ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_init_update_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")

    p_init = sub.add_parser("init", help="Scaffold spec-dock into a project")
    add_init_update_common(p_init)
    p_init.add_argument("--force", action="store_true", help="Overwrite managed files if 'spec-dock' already exists")

    p_update = sub.add_parser(
        "update", help="Update managed files (docs/templates/scripts/skill) in an existing project"
    )
    add_init_update_common(p_update)

    p_uninstall = sub.add_parser("uninstall", help="Plan or remove managed spec-dock artifacts from a project")
    p_uninstall.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    p_uninstall.add_argument("--apply", action="store_true", help="Apply the uninstall plan")
    specs_group = p_uninstall.add_mutually_exclusive_group()
    specs_group.add_argument(
        "--keep-specs", action="store_true", help="Preserve spec history under spec-dock/initiatives"
    )
    specs_group.add_argument("--remove-specs", action="store_true", help="Include spec history in the uninstall plan")
    p_uninstall.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Installer entrypoint. Returns a process exit code (0=success)."""
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    target_root = Path(getattr(ns, "path", ".")).expanduser().resolve()
    if ns.command == "uninstall":
        return _run_uninstall(target_root, ns)

    if not target_root.exists() or not target_root.is_dir():
        print(f"error: target path is not a directory: {target_root}", file=sys.stderr)
        return 2

    try:
        if ns.command == "init":
            admission = _admit_distribution_cli(
                target_root,
                operation="init-force" if bool(ns.force) else "fresh",
            )
            if not ns.force:
                if admission.status in {"retry", "fresh"}:
                    _install_fresh_distribution(target_root, requested_operation="fresh")
                elif os.path.lexists(_specdock_dir(target_root)):
                    raise RuntimeError("'spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'.")
                else:
                    _install_fresh_distribution(target_root, requested_operation="fresh")
            else:
                if admission.status == "fresh" or (admission.status == "retry" and admission.intent == "fresh"):
                    _install_fresh_distribution(target_root, requested_operation="init-force")
                else:
                    _install_recognized_distribution(target_root, operation="init-force")
        elif ns.command == "update":
            admission = _admit_distribution_cli(target_root, operation="update")
            if admission.status == "fresh" or (admission.status == "retry" and admission.intent == "fresh"):
                _install_fresh_distribution(target_root, requested_operation="update")
            else:
                _install_recognized_distribution(target_root, operation="update")
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
