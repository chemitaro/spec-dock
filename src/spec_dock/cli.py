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
import shutil
import stat
import sys
import tempfile
from typing import TYPE_CHECKING, Any, NamedTuple, NoReturn

from spec_dock import __version__
from spec_dock.managed_distribution import (
    DistributionAdmission,
    DistributionOperation,
    DistributionRootIdentity,
    DistributionStageOwnership,
    _rename_distribution_no_replace,
    admit_distribution_operation,
    apply_distribution_plan,
    build_distribution_plan,
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
_COLLISION_AWARE_ADDITIVE_SKILL_NAMES = frozenset({
    "spec-dock",
    "spec-dock-grill-with-docs",
})
_MANAGED_OBSOLETE_EXACT_PATH_PREFIXES = (
    ".agents/skills/",
    ".agents/host-adapters/",
    ".codex/agents/",
    ".github/agents/",
    ".github/workflows/",
)
_UNINSTALL_CLEANUP_BOUNDARY_ROOTS = (Path(".agents"), Path(".codex"), Path(".github"), Path("spec-dock"))
_UNINSTALL_RETRY_MARKER_REL = Path("spec-dock/.uninstall-retry.json")
_DISTRIBUTION_RETRY_MARKER_REL = Path("spec-dock/.distribution-retry.json")
_DISTRIBUTION_RETRY_MARKER_PAYLOAD_VERSION = 1
_DISTRIBUTION_RETRY_MARKER_PURPOSE = "distribution-rerun"


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


def _copy_file(src: Path, dest: Path) -> None:
    """Copy a file while creating parent directories."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _assert_root_workbench_parent_safe(specdock_dir: Path) -> None:
    """Reject a Fresh root Workbench parent that can redirect writes."""
    workbench_dir = specdock_dir / ".workbench"
    try:
        parent_info = os.lstat(workbench_dir)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise RuntimeError("managed root Workbench boundary cannot be inspected safely") from exc
    if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode) or parent_info.st_nlink < 1:
        raise RuntimeError("managed root Workbench boundary is not a safe directory")


def _assert_root_workbench_seed_target_safe(specdock_dir: Path) -> None:
    """Reject symlinked or pre-existing Fresh root Workbench seed boundaries."""
    _assert_root_workbench_parent_safe(specdock_dir)
    workbench_dir = specdock_dir / ".workbench"
    target = workbench_dir / "README.md"
    try:
        target_info = os.lstat(target)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise RuntimeError("managed root Workbench seed target cannot be inspected safely") from exc
    if stat.S_ISLNK(target_info.st_mode) or not stat.S_ISREG(target_info.st_mode) or target_info.st_nlink != 1:
        raise RuntimeError("managed root Workbench seed target is not a safe regular file")
    raise RuntimeError("managed root Workbench seed target already exists; preserve-and-block")


def _is_generated_python_cache_path(path: Path) -> bool:
    return "__pycache__" in path.parts or path.name.endswith(".pyc")


def _ignore_generated_python_caches(_dir: str, names: list[str]) -> set[str]:
    return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}


class _ManagedPathIdentity(NamedTuple):
    """No-follow identity captured for one managed scaffold boundary."""

    device: int
    inode: int
    ctime_ns: int


class _ManagedFileIdentity(NamedTuple):
    """No-follow identity and content digest for one managed scaffold file."""

    device: int
    inode: int
    ctime_ns: int
    link_count: int
    mode: int
    sha256: str


def _managed_path_identity(path: Path) -> _ManagedPathIdentity:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise RuntimeError(f"managed scaffold target cannot be inspected safely: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_nlink < 1:
        raise RuntimeError(f"managed scaffold target is not a safe directory: {path}")
    return _ManagedPathIdentity(info.st_dev, info.st_ino, info.st_ctime_ns)


def _managed_file_identity(path: Path) -> _ManagedFileIdentity | None:
    """Capture one regular file without following the final path component."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RuntimeError("managed scaffold file cannot be inspected safely") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise RuntimeError("managed scaffold file is not a safe regular file")

    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise RuntimeError("managed scaffold file no-follow support is unavailable")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0))
    except OSError as exc:
        raise RuntimeError("managed scaffold file cannot be opened safely") from exc
    try:
        opened = os.fstat(fd)
        if (
            opened.st_dev != info.st_dev
            or opened.st_ino != info.st_ino
            or opened.st_ctime_ns != info.st_ctime_ns
            or opened.st_nlink != 1
            or not stat.S_ISREG(opened.st_mode)
        ):
            raise RuntimeError("managed scaffold file identity changed")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 64)
            if not chunk:
                break
            digest.update(chunk)
        return _ManagedFileIdentity(
            opened.st_dev,
            opened.st_ino,
            opened.st_ctime_ns,
            opened.st_nlink,
            stat.S_IMODE(opened.st_mode),
            digest.hexdigest(),
        )
    except OSError as exc:
        raise RuntimeError("managed scaffold file cannot be read safely") from exc
    finally:
        os.close(fd)


def _root_workbench_seed_decision(specdock_dir: Path, source: Path) -> bool:
    """Classify the Fresh root Workbench seed without following user paths."""
    _assert_root_workbench_parent_safe(specdock_dir)
    target = specdock_dir / ".workbench" / "README.md"
    target_identity = _managed_file_identity(target)
    if target_identity is None:
        return True

    try:
        source_info = os.lstat(source)
    except OSError as exc:
        raise RuntimeError("managed root Workbench seed source cannot be inspected safely") from exc
    if stat.S_ISLNK(source_info.st_mode) or not stat.S_ISREG(source_info.st_mode) or source_info.st_nlink != 1:
        raise RuntimeError("managed root Workbench seed source is not a safe regular file")
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target_identity.sha256 != source_digest or target_identity.mode != stat.S_IMODE(source_info.st_mode):
        raise RuntimeError("managed root Workbench seed target has unknown content; preserve-and-block")
    return False


def _assert_managed_file_identity(path: Path, expected: _ManagedFileIdentity | None) -> None:
    """Reject a managed file that appeared or changed after preflight."""
    if _managed_file_identity(path) != expected:
        raise RuntimeError("managed scaffold file identity changed")


def _assert_managed_path_identity(path: Path, expected: _ManagedPathIdentity | None) -> None:
    """Reject a managed scaffold boundary that changed after preflight."""
    if expected is None:
        if os.path.lexists(path):
            raise RuntimeError(f"managed scaffold target appeared after preflight: {path}")
        return
    current = _managed_path_identity(path)
    if (current.device, current.inode) != (expected.device, expected.inode):
        raise RuntimeError(f"managed scaffold target identity changed: {path}")


def _sync_tree(
    src: Path,
    dest: Path,
    *,
    expected_identity: _ManagedPathIdentity | None = None,
    identity_checked: bool = False,
) -> None:
    """Replace `dest` directory with a full copy of `src`."""
    if expected_identity is not None or identity_checked:
        _assert_managed_path_identity(dest, expected_identity)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=_ignore_generated_python_caches)


def _make_executable(path: Path) -> None:
    """Best-effort: add executable bits to a file."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode | 0o111)
    except OSError:
        # Best-effort only.
        return


def _make_readonly_tree(path: Path) -> None:
    """Best-effort: remove write bits from files under `path`.

    Notes:
    - This is best-effort only; permissions vary by OS/FS.
    - On Windows, making files read-only can interfere with later removal on update,
      so we skip it there.
    """
    if os.name == "nt":
        return
    if not path.exists():
        return

    for p in path.rglob("*"):
        if not p.is_file():
            continue
        try:
            mode = p.stat().st_mode
            p.chmod(mode & ~0o222)
        except OSError:
            # Best-effort only.
            continue


def _active_placeholder_dir(specdock_dir: Path, layer: str) -> Path:
    """Return placeholder directory for a layer or raise if missing."""
    path = specdock_dir / "system" / "active-none" / layer
    if not path.is_dir():
        raise RuntimeError(f"Missing placeholder directory: {path}")
    return path


def _write_active_pathfile(active_dir: Path, name: str, target: Path) -> None:
    """Write `active/<name>.path` as symlink fallback."""
    rel_target = os.path.relpath(target, start=active_dir)
    (active_dir / f"{name}.path").write_text(rel_target + "\n", encoding="utf-8")


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


def _render_context_pack(*, initiative_id: str | None, epic_id: str | None, issue_id: str | None) -> str:
    """Render context-pack content used before runtime active commands run."""
    has_init = initiative_id is not None
    has_epic = epic_id is not None
    has_issue = issue_id is not None
    init_value = initiative_id if has_init else "(none)"
    epic_value = epic_id if has_epic else "(none)"
    issue_value = issue_id if has_issue else "(none)"
    lines: list[str] = []
    lines.append("# Context Pack (generated)")
    lines.append("")
    lines.append("## Active")
    lines.append(f"- initiative: {init_value}")
    lines.append(f"- epic: {epic_value}")
    lines.append(f"- issue: {issue_value}")
    lines.append("")
    lines.append("## Generated state")
    lines.append("- entry: `spec-dock/.agent/active.json`")
    lines.append("- default working set: `spec-dock/.agent/index.json`")
    lines.append("- default dependency view: `spec-dock/.agent/deps-issues.json`")
    lines.append("- escalation only: `spec-dock/.agent/index-all.json`")
    lines.append("- human-oriented tree: `spec-dock/.agent/tree.json`")
    lines.append("")
    lines.append("## Read order")
    lines.append("- Start with `spec-dock/.agent/active.json`.")
    lines.append("- For normal work, read `spec-dock/.agent/index.json` and `spec-dock/.agent/deps-issues.json`.")
    lines.append("- Read `spec-dock/.agent/index-all.json` only when full-history context is needed.")
    lines.append(
        "- `spec-dock/active/context-pack.md` is human guidance that mirrors this contract; it is not the sole source of truth."
    )
    lines.append("- Then follow the active documents:")
    if has_init:
        lines.append("- `spec-dock/active/initiative/requirement.md`")
        lines.append("- `spec-dock/active/initiative/design.md`")
        lines.append("- `spec-dock/active/initiative/plan.md`")
    else:
        lines.append("- `spec-dock/active/initiative/README.md`")
    if has_epic:
        lines.append("- `spec-dock/active/epic/requirement.md`")
        lines.append("- `spec-dock/active/epic/design.md`")
        lines.append("- `spec-dock/active/epic/plan.md`")
    else:
        lines.append("- `spec-dock/active/epic/README.md`")
    if has_issue:
        lines.append("- `spec-dock/active/issue/requirement.md`")
        lines.append("- `spec-dock/active/issue/design.md`")
        lines.append("- `spec-dock/active/issue/plan.md`")
        lines.append("- `spec-dock/active/issue/report.md`")
    else:
        lines.append("- `spec-dock/active/issue/README.md`")
    lines.append("")
    lines.append("## Commands")
    lines.append("- state (github default): `./spec-dock/scripts/spec-dock sync`")
    lines.append("- state (cache/local opt-out): `./spec-dock/scripts/spec-dock sync --no-github`")
    lines.append("- validate: `./spec-dock/scripts/spec-dock validate`")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_default_context_pack() -> str:
    return _render_context_pack(initiative_id=None, epic_id=None, issue_id=None)


def _ensure_active_fallback_entrypoints(specdock_dir: Path) -> None:
    """Ensure `spec-dock/active/*` fallback entrypoints exist after init/update."""
    active_dir = specdock_dir / "active"
    active_dir.mkdir(parents=True, exist_ok=True)
    persisted = _load_persisted_active_entries(specdock_dir)

    for layer in ("initiative", "epic", "issue"):
        link = active_dir / layer
        pathfile = active_dir / f"{layer}.path"
        desired_target: Path
        # Repair stale symlinks so update can restore fallback pointers.
        if link.is_symlink() and not link.exists():
            link.unlink(missing_ok=True)

        persisted_id, persisted_path = persisted[layer]
        existing_entrypoint = _resolve_existing_active_entrypoint(
            specdock_dir,
            active_dir=active_dir,
            layer=layer,
        )
        force_rebuild = False
        if existing_entrypoint is not None and existing_entrypoint[1] is not None:
            existing_target, _existing_id = existing_entrypoint
            resolved_link_target: Path | None = None
            if link.exists() or link.is_symlink():
                try:
                    resolved_link_target = link.resolve()
                except OSError:
                    resolved_link_target = None
            # Keep healthy real entrypoints as highest priority, but if the
            # user-visible pointer disagrees (e.g. placeholder link + real
            # `.path`), normalize the pointer to the same real target.
            if (link.is_symlink() and resolved_link_target != existing_target) or (
                link.exists() and not link.is_symlink() and resolved_link_target != existing_target
            ):
                force_rebuild = True
            desired_target = existing_target
            if not force_rebuild:
                continue
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
            desired_target = (
                resolved_target if resolved_target is not None else _active_placeholder_dir(specdock_dir, layer)
            )

        if existing_entrypoint is not None:
            existing_target, _existing_id = existing_entrypoint
            should_rebuild = force_rebuild or existing_target != desired_target.resolve()
            # Placeholder is already the desired fallback target.
            if not should_rebuild:
                continue

            # Placeholder entrypoint exists but persisted target resolved to real node.
            # For managed pointer conflicts, clear `active/<layer>` first. If that
            # fails, keep `.path` untouched so we do not lose the valid target hint.
            if link.exists() or link.is_symlink():
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    with suppress(OSError):
                        shutil.rmtree(link)
            if link.exists() or link.is_symlink():
                continue
            if pathfile.exists():
                with suppress(OSError):
                    pathfile.unlink()
            if pathfile.exists():
                continue

        # If `.path` exists but does not resolve to a valid active entrypoint,
        # treat it as stale so recovery can rebuild from persisted state/placeholder.
        else:
            if link.is_symlink():
                with suppress(OSError):
                    link.unlink()
            if pathfile.exists():
                with suppress(OSError):
                    pathfile.unlink()

        if link.exists() or link.is_symlink() or pathfile.exists():
            continue

        rel_target = os.path.relpath(desired_target, start=active_dir)
        try:
            Path(link).symlink_to(rel_target)
        except OSError:
            _write_active_pathfile(active_dir, layer, desired_target)

    # Context pack must come from currently-resolved active entrypoints only.
    resolved_ids: dict[str, str | None] = {"initiative": None, "epic": None, "issue": None}
    for layer in ("initiative", "epic", "issue"):
        existing_entrypoint = _resolve_existing_active_entrypoint(
            specdock_dir,
            active_dir=active_dir,
            layer=layer,
        )
        if existing_entrypoint is not None:
            resolved_ids[layer] = existing_entrypoint[1]

    context_pack_path = active_dir / "context-pack.md"
    desired_context_pack = _render_context_pack(
        initiative_id=resolved_ids["initiative"],
        epic_id=resolved_ids["epic"],
        issue_id=resolved_ids["issue"],
    )
    current_context_pack: str | None = None
    if context_pack_path.exists():
        try:
            current_context_pack = context_pack_path.read_text(encoding="utf-8")
        except OSError:
            current_context_pack = None
    if current_context_pack != desired_context_pack:
        context_pack_path.write_text(desired_context_pack, encoding="utf-8")


def _install_repo_root_shortcut(target_root: Path) -> None:
    """Best-effort: create a repo-root `./spec` shortcut to the runtime script.

    This intentionally does not overwrite existing files (safety-first).
    """
    dest = target_root / "spec"
    if dest.exists() or dest.is_symlink():
        print(f"spec-dock: (warn) repo-root shortcut already exists (skipped): {dest}", file=sys.stderr)
        return

    target = f"{_SPEC_DOCK_DIRNAME}/scripts/spec-dock"
    try:
        Path(dest).symlink_to(target)
    except OSError as e:
        print(f"spec-dock: (warn) failed to create repo-root shortcut symlink: {dest}: {e}", file=sys.stderr)


def _prune_legacy_scaffold(specdock_dir: Path) -> None:
    """Remove known legacy (v1) artifacts from generated scaffolding.

    Why this exists:
    - Some local clones may contain a stale `build/` directory from older versions.
    - When building a wheel, setuptools can accidentally carry those stale files into the package.
    - This makes `spec-dock init/update` resilient by removing legacy artifacts after copying.

    Scope:
    - Only touches generated scaffolding files (legacy scripts/templates/workflow/symlinks).
    - Never deletes user-authored specs under `spec-dock/initiatives/**`.
    """
    scripts_dir = specdock_dir / "scripts"
    for p in scripts_dir.glob("spec-dock-close*.sh"):
        p.unlink(missing_ok=True)

    templates_dir = specdock_dir / "templates"

    preserved_readmes = {
        Path("README.md"),
        Path("root/.workbench/README.md"),
        Path("initiative/.workbench/README.md"),
        Path("epic/.workbench/README.md"),
        Path("issue/.workbench/README.md"),
    }

    # Defensive: node templates should not generate unrecognized nested README.md files.
    # These can reappear if a local clone has stale `build/` artifacts that get packaged.
    for p in templates_dir.rglob("README.md"):
        if p.relative_to(templates_dir) in preserved_readmes:
            continue
        p.unlink(missing_ok=True)

    # Legacy node templates used per-scope `adrs/` and `artifacts/`; prune only those nested scopes.
    for scope in ("initiative", "epic", "issue"):
        for legacy_dir in ("adrs", "artifacts"):
            d = templates_dir / scope / legacy_dir
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)

    # v1 used top-level templates/*.md; v2 uses templates/{initiative,epic,issue}/.
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (templates_dir / name).unlink(missing_ok=True)

    # v1-era package contamination can leak template-scoped deps.json files.
    for scope in ("initiative", "epic", "issue"):
        (templates_dir / scope / "deps.json").unlink(missing_ok=True)

    # v1 used nested `current/` and `completed/` directories under templates.
    for dirname in ("current", "completed"):
        for d in sorted(templates_dir.rglob(dirname), key=lambda x: len(str(x)), reverse=True):
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)

    # v1 created root-level symlinks as shortcuts. v2 uses `spec-dock/active/`,
    # so these are always safe to remove when they are symlinks (never delete real dirs).
    for name in ("current-initiative", "current-epic", "current-issue"):
        p = specdock_dir / name
        if p.is_symlink():
            p.unlink(missing_ok=True)

    # v2 used a `.path` fallback briefly during development; prune if present.
    for name in ("current-initiative.path", "current-epic.path", "current-issue.path"):
        (specdock_dir / name).unlink(missing_ok=True)


def _retry_unpublished_atomic_regular_file(
    temporary: Path,
    destination: Path,
    payload: bytes,
    *,
    mode: int,
    expected_identity: tuple[int, int],
) -> tuple[bool, bool]:
    """Retry one failed no-replace publication while retaining temp ownership."""
    parent = temporary.parent
    try:
        parent_info = os.lstat(parent)
        if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
            return False, False
        nofollow = getattr(os, "O_NOFOLLOW", None)
        if not isinstance(nofollow, int):
            return False, False
        parent_fd = os.open(
            parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow | getattr(os, "O_CLOEXEC", 0),
        )
    except OSError:
        return False, False
    fd: int | None = None
    try:
        parent_current = os.fstat(parent_fd)
        if (
            stat.S_ISLNK(parent_current.st_mode)
            or not stat.S_ISDIR(parent_current.st_mode)
            or (parent_current.st_dev, parent_current.st_ino) != (parent_info.st_dev, parent_info.st_ino)
        ):
            return False, False
        temporary_info = os.stat(temporary.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            stat.S_ISLNK(temporary_info.st_mode)
            or not stat.S_ISREG(temporary_info.st_mode)
            or temporary_info.st_nlink != 1
            or (temporary_info.st_dev, temporary_info.st_ino) != expected_identity
        ):
            return False, False
        try:
            os.stat(destination.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        except OSError:
            return False, False
        else:
            return False, False

        # Open without truncation so a race replacement is only inspected by
        # fstat; truncate the held descriptor only after its identity matches.
        flags = os.O_WRONLY | nofollow | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(temporary.name, flags, dir_fd=parent_fd)
        current = os.fstat(fd)
        if (
            stat.S_ISLNK(current.st_mode)
            or not stat.S_ISREG(current.st_mode)
            or current.st_nlink != 1
            or (current.st_dev, current.st_ino) != expected_identity
        ):
            return False, False
        os.ftruncate(fd, 0)
        os.fchmod(fd, mode)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                return False, False
            view = view[written:]
        os.fsync(fd)
        os.close(fd)
        fd = None

        try:
            os.stat(destination.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        except OSError:
            return False, False
        else:
            return False, False
        _rename_distribution_no_replace(parent_fd, temporary.name, parent_fd, destination.name)
        return True, True
    except OSError:
        return False, False
    finally:
        if fd is not None:
            with suppress(OSError):
                os.close(fd)
        with suppress(OSError):
            os.close(parent_fd)


def _publish_new_atomic_regular_file(temporary: Path, destination: Path) -> None:
    """Move a new regular file into place without replacing a race winner."""
    parent = temporary.parent
    try:
        parent_info = os.lstat(parent)
    except OSError as exc:
        raise RuntimeError("managed file parent cannot be inspected safely") from exc
    if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
        raise RuntimeError("managed file parent must be a real directory")
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise RuntimeError("managed file parent cannot be opened safely")
    try:
        parent_fd = os.open(
            parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow | getattr(os, "O_CLOEXEC", 0),
        )
    except OSError as exc:
        raise RuntimeError("managed file parent cannot be opened safely") from exc
    try:
        current_parent = os.fstat(parent_fd)
        if (
            stat.S_ISLNK(current_parent.st_mode)
            or not stat.S_ISDIR(current_parent.st_mode)
            or (current_parent.st_dev, current_parent.st_ino) != (parent_info.st_dev, parent_info.st_ino)
        ):
            raise RuntimeError("managed file parent identity changed")
        _rename_distribution_no_replace(parent_fd, temporary.name, parent_fd, destination.name)
    finally:
        with suppress(OSError):
            os.close(parent_fd)


def _write_atomic_regular_file(
    path: Path,
    payload: bytes,
    *,
    mode: int,
    expected_identity: _ManagedFileIdentity | None = None,
    identity_checked: bool = False,
) -> None:
    """Write one managed regular file without following a destination link."""
    parent = path.parent
    try:
        parent_info = os.lstat(parent)
    except OSError as exc:
        raise RuntimeError("managed file parent cannot be inspected safely") from exc
    if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
        raise RuntimeError("managed file parent must be a real directory")

    existing: os.stat_result | None
    try:
        existing = os.lstat(path)
    except FileNotFoundError:
        existing = None
    except OSError as exc:
        raise RuntimeError("managed file cannot be inspected safely") from exc
    if existing is not None and (
        stat.S_ISLNK(existing.st_mode) or not stat.S_ISREG(existing.st_mode) or existing.st_nlink != 1
    ):
        raise RuntimeError("managed file destination is not a safe regular file")
    if identity_checked:
        _assert_managed_file_identity(path, expected_identity)

    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=parent)
    temporary = Path(temporary_name)
    # `mkstemp` returns an absolute pathname even when `parent` is relative.
    # Keep the staging reference relative while a root-bound caller holds the
    # opened directory, otherwise a root rename would make the absolute name
    # point at the now-empty original pathname.
    temporary_ref = parent / temporary.name if not parent.is_absolute() else temporary
    temporary_info = os.lstat(temporary_ref)
    temporary_identity = (temporary_info.st_dev, temporary_info.st_ino)
    closed = False
    try:
        os.fchmod(fd, mode)
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise RuntimeError("managed file write made no progress")
            view = view[written:]
        os.fsync(fd)
        os.close(fd)
        closed = True

        if existing is not None:
            if identity_checked:
                _assert_managed_file_identity(path, expected_identity)
            current = os.lstat(path)
            if (
                stat.S_ISLNK(current.st_mode)
                or not stat.S_ISREG(current.st_mode)
                or current.st_nlink != 1
                or current.st_dev != existing.st_dev
                or current.st_ino != existing.st_ino
            ):
                raise RuntimeError("managed file destination identity changed")
            temporary_ref.replace(path)
        else:
            # A destination that was absent during preflight must not be
            # replaced if another actor creates it before publication.
            _publish_new_atomic_regular_file(temporary_ref, path)
        temporary = None  # type: ignore[assignment]
    except Exception as exc:
        if not closed:
            with suppress(OSError):
                os.close(fd)
            closed = True
        if existing is None and temporary is not None:
            published, removed = _retry_unpublished_atomic_regular_file(
                temporary_ref,
                path,
                payload,
                mode=mode,
                expected_identity=temporary_identity,
            )
            if published and removed:
                temporary = None  # type: ignore[assignment]
        if isinstance(exc, OSError):
            raise RuntimeError("managed file write failed") from exc
        raise
    finally:
        if not closed:
            with suppress(OSError):
                os.close(fd)
        if temporary is not None:
            with suppress(OSError):
                temporary_ref.unlink()


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


def _write_spec_dock_version(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
    root_identity_path: Path | None = None,
) -> None:
    """Publish the generated version marker after post-verification."""
    identity_path = root_identity_path or target_root
    with _bound_distribution_root(identity_path, expected_root_identity) as (bound_root, visible_root, bound_identity):
        path = _specdock_dir(bound_root) / "spec-dock.version"
        mode = 0o644
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            info = None
        except OSError as exc:
            raise RuntimeError("version marker cannot be inspected safely") from exc
        if info is not None:
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise RuntimeError("version marker is not a safe regular file")
            mode = stat.S_IMODE(info.st_mode)
        _write_atomic_regular_file(path, f"{_tool_version()}\n".encode(), mode=mode)
        _assert_distribution_root_identity(visible_root, bound_identity)


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


def _write_distribution_retry_marker(
    target_root: Path,
    *,
    operation: DistributionOperation,
    last_completed_phase: str,
    expected_root_identity: DistributionRootIdentity,
    stage_ownership: tuple[DistributionStageOwnership, ...] = (),
) -> None:
    """Create or atomically advance the init/update forward-retry marker."""
    with _bound_distribution_root(target_root, expected_root_identity) as (bound_root, visible_root, bound_identity):
        marker = _distribution_retry_marker_path(bound_root)
        try:
            root_info = os.lstat(bound_root)
            parent_info = os.lstat(marker.parent)
        except OSError as exc:
            raise RuntimeError("distribution retry marker parent cannot be inspected safely") from exc
        if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
            raise RuntimeError("distribution retry marker target root is unsafe")
        if stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode):
            raise RuntimeError("distribution retry marker parent is unsafe")

        payload = {
            "schema_version": _DISTRIBUTION_RETRY_MARKER_PAYLOAD_VERSION,
            "operation": operation,
            "package_version": _tool_version(),
            "target_root": {
                "device": bound_identity.device,
                "inode": bound_identity.inode,
            },
            "last_completed_phase": last_completed_phase,
            "purpose": _DISTRIBUTION_RETRY_MARKER_PURPOSE,
            "stage_ownership": [
                {
                    "path": item.path,
                    "stage_name": item.stage_name,
                    "device": item.device,
                    "inode": item.inode,
                    "ctime_ns": item.ctime_ns,
                    "file_type": item.file_type,
                }
                for item in stage_ownership
            ],
        }
        marker_bytes = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        _write_atomic_regular_file(marker, marker_bytes, mode=0o600)
        _assert_distribution_root_identity(visible_root, bound_identity)


def _remove_distribution_retry_marker(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> None:
    """Remove the init/update marker only when it is a safe regular file."""
    with _bound_distribution_root(target_root, expected_root_identity) as (bound_root, visible_root, bound_identity):
        marker = _distribution_retry_marker_path(bound_root)
        try:
            info = os.lstat(marker)
        except FileNotFoundError:
            return
        except OSError as exc:
            raise RuntimeError("distribution retry marker cannot be inspected safely") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise RuntimeError("distribution retry marker is not a safe regular file")
        _assert_distribution_root_identity(visible_root, bound_identity)
        try:
            marker.unlink()
        except OSError as exc:
            raise RuntimeError("distribution retry marker could not be removed") from exc
        _assert_distribution_root_identity(visible_root, bound_identity)


def _install_spec_dock_bound(
    target_root: Path,
    *,
    force: bool,
    install_root_shortcut: bool = True,
    write_version: bool = True,
    expected_root_identity: DistributionRootIdentity | None = None,
    root_identity_path: Path | None = None,
    expected_managed_scaffold_identities: dict[Path, _ManagedPathIdentity | None] | None = None,
    expected_managed_gitignore_identity: _ManagedFileIdentity | None = None,
    managed_gitignore_identity_checked: bool = False,
    seed_root_workbench: bool | None = None,
) -> None:
    """Install/update `spec-dock/` scaffold into the target repository."""
    identity_path = root_identity_path or target_root

    def guard_root() -> None:
        if expected_root_identity is not None:
            _assert_distribution_root_identity(identity_path, expected_root_identity)

    guard_root()
    specdock_dir = _specdock_dir(target_root)
    fresh_specdock = not os.path.lexists(specdock_dir)
    should_seed_root_workbench = fresh_specdock if seed_root_workbench is None else seed_root_workbench
    if specdock_dir.exists() and not force:
        raise RuntimeError(f"'{_SPEC_DOCK_DIRNAME}' already exists. Use 'spec-dock update' or re-run with '--force'.")

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"
        if not src_spec_dock.is_dir():
            raise RuntimeError("Missing asset directory: spec_dock")

        # `.gitignore` is a required shipped asset.  Do not fall back to an
        # embedded copy: a package that omits it is incomplete and must fail
        # before creating or replacing any consumer state.
        src_gitignore = src_spec_dock / ".gitignore"
        if not src_gitignore.is_file() or src_gitignore.is_symlink():
            raise RuntimeError("Missing asset file: spec_dock/.gitignore")

        # Preflight all managed scaffold directories before any write.
        managed_scaffold_sync_plan: list[tuple[Path, Path]] = []
        for name in _MANAGED_DIRS:
            src = src_spec_dock / name
            if not src.exists():
                raise RuntimeError(f"Missing asset directory: spec_dock/{name}")
            if not src.is_dir():
                raise RuntimeError(f"Invalid asset directory: spec_dock/{name}")
            managed_scaffold_sync_plan.append((src, specdock_dir / name))

        root_workbench_readme: Path | None = None
        if seed_root_workbench is not None:
            _assert_root_workbench_parent_safe(specdock_dir)
            if seed_root_workbench:
                root_workbench_readme = src_spec_dock / "templates" / "root" / ".workbench" / "README.md"
                if not root_workbench_readme.is_file() or root_workbench_readme.is_symlink():
                    raise RuntimeError("Missing asset file: spec_dock/templates/root/.workbench/README.md")

        guard_root()
        if expected_managed_scaffold_identities is not None:
            _assert_managed_path_identity(
                specdock_dir,
                expected_managed_scaffold_identities[specdock_dir],
            )
        specdock_dir.mkdir(parents=True, exist_ok=True)
        guard_root()

        # Managed directories are owned by the installer and can be replaced on update.
        # The actual spec tree (`spec-dock/initiatives/**`) must be persistent and is
        # never removed by this installer.
        for src, dest in managed_scaffold_sync_plan:
            guard_root()
            if expected_managed_scaffold_identities is not None:
                _assert_managed_path_identity(
                    dest,
                    expected_managed_scaffold_identities[dest],
                )
            if dest.exists() or force:
                _sync_tree(
                    src,
                    dest,
                    expected_identity=(
                        expected_managed_scaffold_identities.get(dest)
                        if expected_managed_scaffold_identities is not None
                        else None
                    ),
                    identity_checked=expected_managed_scaffold_identities is not None,
                )
            else:
                shutil.copytree(src, dest, ignore=_ignore_generated_python_caches)
            guard_root()

        guard_root()
        gitignore_mode = stat.S_IMODE(src_gitignore.stat().st_mode)
        _write_atomic_regular_file(
            specdock_dir / ".gitignore",
            src_gitignore.read_bytes(),
            mode=gitignore_mode,
            expected_identity=expected_managed_gitignore_identity,
            identity_checked=managed_gitignore_identity_checked,
        )
        guard_root()

        if should_seed_root_workbench:
            _assert_root_workbench_seed_target_safe(specdock_dir)
            assert root_workbench_readme is not None
            guard_root()
            workbench_seed_target = specdock_dir / ".workbench" / "README.md"
            workbench_seed_target.parent.mkdir(parents=True, exist_ok=True)
            source_info = os.lstat(root_workbench_readme)
            _write_atomic_regular_file(
                workbench_seed_target,
                root_workbench_readme.read_bytes(),
                mode=stat.S_IMODE(source_info.st_mode),
            )
            guard_root()

        # Spec tree root + generated directories.
        guard_root()
        (specdock_dir / "initiatives").mkdir(parents=True, exist_ok=True)
        guard_root()
        (specdock_dir / "active").mkdir(parents=True, exist_ok=True)
        guard_root()
        (specdock_dir / ".agent").mkdir(parents=True, exist_ok=True)
        guard_root()

        guard_root()
        _prune_legacy_scaffold(specdock_dir)
        guard_root()

        # Ensure runtime scripts are executable (best-effort).
        for runtime_name in ("spec-dock",):
            runtime_script = specdock_dir / "scripts" / runtime_name
            if runtime_script.exists():
                guard_root()
                _make_executable(runtime_script)
                guard_root()

        # Best-effort: placeholders are not user-authored specs; discourage edits.
        guard_root()
        _make_readonly_tree(specdock_dir / "system" / "active-none")
        guard_root()

        # Ensure active fallback entrypoints exist before runtime `active clear/set`.
        guard_root()
        _ensure_active_fallback_entrypoints(specdock_dir)
        guard_root()

        if write_version:
            _write_spec_dock_version(
                target_root,
                expected_root_identity=expected_root_identity,
                root_identity_path=identity_path,
            )

        # Best-effort: provide `./spec` at repo root for convenience.
        if install_root_shortcut:
            guard_root()
            _install_repo_root_shortcut(target_root)
            guard_root()


def _install_spec_dock(
    target_root: Path,
    *,
    force: bool,
    install_root_shortcut: bool = True,
    write_version: bool = True,
    expected_root_identity: DistributionRootIdentity | None = None,
    expected_managed_scaffold_identities: dict[Path, _ManagedPathIdentity | None] | None = None,
    expected_managed_gitignore_identity: _ManagedFileIdentity | None = None,
    managed_gitignore_identity_checked: bool = False,
    seed_root_workbench: bool | None = None,
) -> None:
    """Install/update scaffold while binding all writes to the opened root."""
    with _bound_distribution_root(target_root, expected_root_identity) as (
        bound_root,
        visible_root,
        bound_identity,
    ):
        _install_spec_dock_bound(
            bound_root,
            force=force,
            install_root_shortcut=install_root_shortcut,
            write_version=write_version,
            expected_root_identity=bound_identity,
            root_identity_path=visible_root,
            expected_managed_scaffold_identities=expected_managed_scaffold_identities,
            expected_managed_gitignore_identity=expected_managed_gitignore_identity,
            managed_gitignore_identity_checked=managed_gitignore_identity_checked,
            seed_root_workbench=seed_root_workbench,
        )


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


def _preflight_managed_scaffold_target_paths(
    target_root: Path,
    *,
    expected_gitignore_bytes: bytes,
) -> tuple[dict[Path, _ManagedPathIdentity | None], _ManagedFileIdentity | None]:
    """Reject unsafe existing scaffold targets before a recognized update.

    The scaffold refresh replaces the four provider-managed directories and
    rewrites a small set of marker files.  Every existing target must therefore
    be a real directory or a single-link regular file; a symlink, hard link, or
    non-directory at any mutation boundary is a preserve-and-block collision.
    """

    specdock_dir = _specdock_dir(target_root)
    identities: dict[Path, _ManagedPathIdentity | None] = {}

    def require_directory(path: Path, *, label: str) -> None:
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            return
        except OSError as exc:
            raise RuntimeError(f"cannot inspect managed scaffold target '{label}' safely") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_nlink < 1:
            raise RuntimeError(f"managed scaffold target '{label}' is not a safe directory")

    def require_regular_file(path: Path, *, label: str) -> None:
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            return
        except OSError as exc:
            raise RuntimeError(f"cannot inspect managed scaffold target '{label}' safely") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise RuntimeError(f"managed scaffold target '{label}' is not a safe regular file")

    require_directory(specdock_dir, label="spec-dock")
    identities[specdock_dir] = _managed_path_identity(specdock_dir) if os.path.lexists(specdock_dir) else None
    for name in _MANAGED_DIRS:
        managed_dir = specdock_dir / name
        require_directory(managed_dir, label=f"spec-dock/{name}")
        identities[managed_dir] = _managed_path_identity(managed_dir) if os.path.lexists(managed_dir) else None
        if not managed_dir.exists():
            continue
        # `_sync_tree` removes and recreates this whole directory.  Refuse any
        # nested symlink so a managed refresh cannot silently delete a user link
        # or traverse a replacement path during the pathname-based copy helper.
        for current_root, dir_names, file_names in os.walk(managed_dir, topdown=True, followlinks=False):
            current = Path(current_root)
            unsafe_dirs = [name for name in dir_names if (current / name).is_symlink()]
            unsafe_files = [name for name in file_names if (current / name).is_symlink()]
            if unsafe_dirs or unsafe_files:
                first_entry = (unsafe_dirs or unsafe_files)[0]
                unsafe_path = (current / first_entry).relative_to(specdock_dir).as_posix()
                raise RuntimeError(f"managed scaffold target contains symlinked entry: spec-dock/{unsafe_path}")

    gitignore_path = specdock_dir / ".gitignore"
    require_regular_file(gitignore_path, label="spec-dock/.gitignore")
    gitignore_identity = _managed_file_identity(gitignore_path)
    if (
        gitignore_identity is not None
        and gitignore_identity.sha256 != hashlib.sha256(expected_gitignore_bytes).hexdigest()
    ):
        raise RuntimeError("managed scaffold target 'spec-dock/.gitignore' has unknown content; preserve-and-block")
    require_regular_file(specdock_dir / "spec-dock.version", label="spec-dock/spec-dock.version")

    # These directories hold persistent or generated state and are only
    # created/updated through known child paths.  Their top-level boundary must
    # not be a link or a replacement file.
    for name in ("initiatives", "active", ".agent"):
        require_directory(specdock_dir / name, label=f"spec-dock/{name}")
    require_regular_file(specdock_dir / "active" / "context-pack.md", label="spec-dock/active/context-pack.md")
    require_regular_file(specdock_dir / ".agent" / "active.json", label="spec-dock/.agent/active.json")

    return identities, gitignore_identity


def _distribution_retry_command(operation: DistributionOperation) -> str:
    if operation == "fresh":
        return "spec-dock init ."
    if operation == "init-force":
        return "spec-dock init --force ."
    return "spec-dock update ."


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
        "scaffold-refresh": "spec-dock",
        "post-verify": "distribution",
        "version-write": "spec-dock/spec-dock.version",
        "marker-finalization": "spec-dock/.distribution-retry.json",
    }.get(phase, "spec-dock/.distribution-retry.json")


def _raise_distribution_partial_failure(
    exc: BaseException,
    *,
    operation: DistributionOperation,
    phase: str,
    last_completed_phase: str,
) -> NoReturn:
    target = _safe_distribution_failure_target(exc, phase)
    retry = _distribution_retry_command(operation)
    raise RuntimeError(
        f"distribution partial failure during {phase}; "
        f"target={target}; last_completed_phase={last_completed_phase}; "
        f"retry={retry}"
    ) from None


def _install_fresh_distribution(target_root: Path) -> None:
    """Apply one validated Fresh distribution with forward-retry recovery."""
    phase = "preflight"
    marker_started = False
    last_completed_phase = "not-started"
    root_identity = _distribution_root_identity(target_root)
    fresh_workspace_created = False
    stage_ownership: list[DistributionStageOwnership] = []
    with _assets_dir() as assets_dir:
        try:
            _preflight_fresh_spec_dock_assets(assets_dir)
            plan = build_distribution_plan(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                operation="fresh",
            )
            if plan.blocked:
                reasons = ", ".join(f"{action.path}: {action.reason}" for action in plan.actions if action.blocked)
                raise RuntimeError(f"distribution preflight blocked: {reasons}")

            _assert_distribution_root_identity(target_root, root_identity)
            specdock_dir = _specdock_dir(target_root)
            if not os.path.lexists(specdock_dir):
                # Create the first workspace boundary relative to the held
                # root directory.  A concurrent pathname replacement must
                # not redirect this mutation to an unrelated visible root.
                with _bound_distribution_root(target_root, root_identity) as (
                    bound_root,
                    _visible_root,
                    _bound_identity,
                ):
                    try:
                        _specdock_dir(bound_root).mkdir()
                    except FileExistsError as exc:
                        raise RuntimeError("Fresh distribution workspace appeared during preflight") from exc
                fresh_workspace_created = True
            _write_distribution_retry_marker(
                target_root,
                operation="fresh",
                last_completed_phase="preflight-complete",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            marker_started = True
            last_completed_phase = "preflight-complete"

            def record_stage_ownership(record: DistributionStageOwnership) -> None:
                stage_ownership.append(record)
                _write_distribution_retry_marker(
                    target_root,
                    operation="fresh",
                    last_completed_phase=last_completed_phase,
                    expected_root_identity=root_identity,
                    stage_ownership=tuple(stage_ownership),
                )

            # Creating the marker's `spec-dock/` parent is itself a target-root
            # mutation and therefore updates the root ctime.  Rebuild the
            # read-only plan after that first mutation so apply-time snapshots
            # remain bound to the current root identity.
            plan = build_distribution_plan(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                operation="fresh",
            )
            if plan.blocked:
                reasons = ", ".join(f"{action.path}: {action.reason}" for action in plan.actions if action.blocked)
                raise RuntimeError(f"distribution preflight blocked after marker: {reasons}")

            phase = "distribution-apply"
            _assert_distribution_root_identity(target_root, root_identity)
            apply_distribution_plan(plan, stage_ownership_recorder=record_stage_ownership)
            _write_distribution_retry_marker(
                target_root,
                operation="fresh",
                last_completed_phase="distribution-applied",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "distribution-applied"

            phase = "scaffold-refresh"
            _assert_distribution_root_identity(target_root, root_identity)
            _install_spec_dock(
                target_root,
                force=True,
                install_root_shortcut=False,
                write_version=False,
                expected_root_identity=root_identity,
                seed_root_workbench=_root_workbench_seed_decision(
                    specdock_dir,
                    assets_dir / "spec_dock" / "templates" / "root" / ".workbench" / "README.md",
                ),
            )
            _write_distribution_retry_marker(
                target_root,
                operation="fresh",
                last_completed_phase="scaffold-refreshed",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "scaffold-refreshed"

            phase = "post-verify"
            _assert_distribution_root_identity(target_root, root_identity)
            post_plan = build_distribution_plan(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                operation="fresh",
            )
            if post_plan.blocked:
                reasons = ", ".join(f"{action.path}: {action.reason}" for action in post_plan.actions if action.blocked)
                raise RuntimeError(f"distribution post-verify blocked: {reasons}")
            non_adopted = [action.path for action in post_plan.actions if action.action != "adopt"]
            if non_adopted:
                joined = ", ".join(non_adopted)
                raise RuntimeError(f"distribution post-verify incomplete: {joined}")
            _write_distribution_retry_marker(
                target_root,
                operation="fresh",
                last_completed_phase="post-verified",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "post-verified"

            phase = "version-write"
            _write_spec_dock_version(target_root, expected_root_identity=root_identity)
            _write_distribution_retry_marker(
                target_root,
                operation="fresh",
                last_completed_phase="version-written",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "version-written"
            phase = "marker-finalization"
            _remove_distribution_retry_marker(target_root, expected_root_identity=root_identity)
            last_completed_phase = "marker-finalized"
        except Exception as exc:
            if _distribution_retry_marker_present(target_root):
                marker_started = True
            if marker_started:
                _raise_distribution_partial_failure(
                    exc,
                    operation="fresh",
                    phase=phase,
                    last_completed_phase=last_completed_phase,
                )
            if fresh_workspace_created:
                with suppress(OSError):
                    _assert_distribution_root_identity(target_root, root_identity)
                    _specdock_dir(target_root).rmdir()
            raise


def _install_recognized_distribution(
    target_root: Path,
    *,
    operation: DistributionOperation,
    retry_marker: DistributionAdmission | None = None,
) -> None:
    """Apply a recognized distribution with same-package forward recovery."""
    phase = "preflight"
    marker_started = False
    last_completed_phase = "not-started"
    root_identity = _distribution_root_identity(target_root)
    retry_recovery = _distribution_retry_marker_present(target_root)
    stage_ownership: list[DistributionStageOwnership] = list(
        retry_marker.marker.stage_ownership if retry_marker is not None and retry_marker.marker is not None else ()
    )
    with _assets_dir() as assets_dir:
        try:
            # Recognized updates may mutate external distribution files before
            # the scaffold refresh. Validate the complete scaffold source
            # catalog before publishing the retry marker or touching targets.
            _preflight_fresh_spec_dock_assets(assets_dir)
            src_gitignore = assets_dir / "spec_dock" / ".gitignore"
            if not src_gitignore.is_file() or src_gitignore.is_symlink():
                raise RuntimeError("Missing asset file: spec_dock/.gitignore")
            expected_gitignore_bytes = src_gitignore.read_bytes()
            plan = build_distribution_plan(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                operation=operation,
            )
            if plan.blocked:
                reasons = ", ".join(f"{action.path}: {action.reason}" for action in plan.actions if action.blocked)
                raise RuntimeError(f"distribution preflight blocked: {reasons}")

            _assert_distribution_root_identity(target_root, root_identity)
            absolute_scaffold_identities, gitignore_identity = _preflight_managed_scaffold_target_paths(
                target_root,
                expected_gitignore_bytes=expected_gitignore_bytes,
            )
            managed_scaffold_identities = {
                path.relative_to(target_root): identity for path, identity in absolute_scaffold_identities.items()
            }
            _write_distribution_retry_marker(
                target_root,
                operation=operation,
                last_completed_phase="preflight-complete",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            marker_started = True
            last_completed_phase = "preflight-complete"

            def record_stage_ownership(record: DistributionStageOwnership) -> None:
                existing = next(
                    (
                        item
                        for item in stage_ownership
                        if item.path == record.path and item.stage_name == record.stage_name
                    ),
                    None,
                )
                if existing is not None:
                    stage_ownership.remove(existing)
                stage_ownership.append(record)
                _write_distribution_retry_marker(
                    target_root,
                    operation=operation,
                    last_completed_phase=last_completed_phase,
                    expected_root_identity=root_identity,
                    stage_ownership=tuple(stage_ownership),
                )

            phase = "distribution-apply"
            _assert_distribution_root_identity(target_root, root_identity)
            apply_distribution_plan(
                plan,
                allow_stale_stage_cleanup=retry_recovery,
                stage_ownership=tuple(stage_ownership),
                stage_ownership_recorder=record_stage_ownership,
            )
            _write_distribution_retry_marker(
                target_root,
                operation=operation,
                last_completed_phase="distribution-applied",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "distribution-applied"

            phase = "scaffold-refresh"
            _assert_distribution_root_identity(target_root, root_identity)
            _install_spec_dock(
                target_root,
                force=True,
                write_version=False,
                expected_root_identity=root_identity,
                expected_managed_scaffold_identities=managed_scaffold_identities,
                expected_managed_gitignore_identity=gitignore_identity,
                managed_gitignore_identity_checked=True,
                seed_root_workbench=(
                    _root_workbench_seed_decision(
                        _specdock_dir(target_root),
                        assets_dir / "spec_dock" / "templates" / "root" / ".workbench" / "README.md",
                    )
                    if operation == "fresh"
                    else None
                ),
            )
            _write_distribution_retry_marker(
                target_root,
                operation=operation,
                last_completed_phase="scaffold-refreshed",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "scaffold-refreshed"

            phase = "post-verify"
            _assert_distribution_root_identity(target_root, root_identity)
            post_plan = build_distribution_plan(
                assets_dir / "install_root",
                manifest_path=assets_dir / "managed_distribution.json",
                scaffold_root=assets_dir / "spec_dock",
                target_root=target_root,
                operation=operation,
            )
            if post_plan.blocked:
                raise RuntimeError("distribution post-verify blocked")
            if any(action.action != "adopt" for action in post_plan.actions):
                raise RuntimeError("distribution post-verify incomplete")
            _write_distribution_retry_marker(
                target_root,
                operation=operation,
                last_completed_phase="post-verified",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "post-verified"

            phase = "version-write"
            _write_spec_dock_version(
                target_root,
                expected_root_identity=root_identity,
            )
            _write_distribution_retry_marker(
                target_root,
                operation=operation,
                last_completed_phase="version-written",
                expected_root_identity=root_identity,
                stage_ownership=tuple(stage_ownership),
            )
            last_completed_phase = "version-written"
            phase = "marker-finalization"
            _remove_distribution_retry_marker(
                target_root,
                expected_root_identity=root_identity,
            )
            last_completed_phase = "marker-finalized"
        except Exception as exc:
            if _distribution_retry_marker_present(target_root):
                marker_started = True
            if marker_started:
                _raise_distribution_partial_failure(
                    exc,
                    operation=operation,
                    phase=phase,
                    last_completed_phase=last_completed_phase,
                )
            raise exc


def _managed_skill_names() -> tuple[str, ...]:
    """Return the managed bundled skill set."""
    return _MANAGED_SKILL_NAMES


def _managed_skill_ownership_names() -> tuple[str, ...]:
    """Return skill directory names owned by the installer for pruning decisions."""
    return _managed_skill_names()


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


class _ManagedCurrentFileMapping(NamedTuple):
    source_asset_rel: Path
    target_rel: Path


class _ManagedSkillInstallPlan(NamedTuple):
    current_file_mappings: tuple[_ManagedCurrentFileMapping, ...]
    bootstrap_only_rel_paths: tuple[Path, ...]
    obsolete_exact_rel_paths: tuple[Path, ...]


class _UninstallTargetIdentity(NamedTuple):
    """No-follow identity captured before an uninstall mutation."""

    kind: str
    device: int
    inode: int
    ctime_ns: int
    size: int = 0
    sha256: str | None = None
    link_target: str | None = None


class _UninstallAction(NamedTuple):
    rel_path: str
    category: str
    status: str
    reason: str
    error: str | None = None
    expected_identity: _UninstallTargetIdentity | None = None
    expected_absent: bool = False


def _uninstall_specs_mode(ns: argparse.Namespace) -> str | None:
    if getattr(ns, "keep_specs", False):
        return "keep"
    if getattr(ns, "remove_specs", False):
        return "remove"
    return None


def _require_managed_specdock_for_uninstall(target_root: Path) -> Path:
    try:
        specdock_dir = _require_specdock(target_root)
    except RuntimeError as e:
        raise RuntimeError(f"target is not a managed SpecDock repo: {e}") from e

    version_file = specdock_dir / "spec-dock.version"
    if not version_file.is_file() and not _has_valid_uninstall_retry_marker(specdock_dir):
        raise RuntimeError(
            "target is not a managed SpecDock repo: missing managed "
            "'spec-dock/spec-dock.version' state or SpecDock uninstall retry marker"
        )
    return specdock_dir


def _uninstall_retry_marker_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "managed_by": "spec-dock",
        "purpose": "uninstall-rerun",
    }


def _has_valid_uninstall_retry_marker(specdock_dir: Path) -> bool:
    marker = specdock_dir / _UNINSTALL_RETRY_MARKER_REL.relative_to("spec-dock")
    if marker.is_symlink():
        raise RuntimeError(
            f"target contains symlinked SpecDock uninstall retry marker: {_UNINSTALL_RETRY_MARKER_REL.as_posix()}"
        )
    if not marker.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return payload == _uninstall_retry_marker_payload()


def _reject_symlinked_uninstall_retry_marker(target_root: Path) -> None:
    marker = target_root / _UNINSTALL_RETRY_MARKER_REL
    if marker.is_symlink():
        raise RuntimeError(
            f"target contains symlinked SpecDock uninstall retry marker: {_UNINSTALL_RETRY_MARKER_REL.as_posix()}"
        )


def _uninstall_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if not isinstance(nofollow, int) or not isinstance(directory, int):
        raise RuntimeError("platform lacks required no-follow directory support for uninstall")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _assert_uninstall_visible_chain(
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
            raise RuntimeError("uninstall target path changed during safe operation") from exc
        if (
            stat.S_ISLNK(visible_stat.st_mode)
            or visible_stat.st_dev != held_stat.st_dev
            or visible_stat.st_ino != held_stat.st_ino
            or not stat.S_ISDIR(held_stat.st_mode)
        ):
            raise RuntimeError("uninstall target path changed during safe operation")


@contextmanager
def _open_uninstall_parent_chain(
    target_root: Path,
    rel_path: Path,
    *,
    create_missing: bool = False,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> Iterator[tuple[int, ...]]:
    """Open an uninstall target's parent chain without following symlinks."""

    if not _is_safe_uninstall_rel_path(rel_path):
        raise RuntimeError("unsafe uninstall path outside managed boundaries")
    flags = _uninstall_directory_flags()
    fds: list[int] = []
    try:
        root_fd = os.open(target_root, flags)
        fds.append(root_fd)
        root_stat = os.fstat(root_fd)
        if not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_nlink < 1:
            raise RuntimeError("uninstall target root is not a real directory")
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
                    raise RuntimeError(f"uninstall target parent is missing for '{rel_path.as_posix()}'") from None
                os.mkdir(component, dir_fd=fds[-1])
                next_fd = os.open(component, flags, dir_fd=fds[-1])
            except OSError as exc:
                raise RuntimeError(f"uninstall target parent is unsafe for '{rel_path.as_posix()}'") from exc
            fds.append(next_fd)
        chain = tuple(fds)
        _assert_uninstall_visible_chain(target_root, rel_path, chain)
        yield chain
    except FileExistsError:
        raise RuntimeError(f"uninstall target parent changed for '{rel_path.as_posix()}'") from None
    except OSError as exc:
        raise RuntimeError("uninstall target cannot be opened safely") from exc
    finally:
        for fd in reversed(fds):
            with suppress(OSError):
                os.close(fd)


def _assert_uninstall_directory_binding(target_root: Path, rel_path: Path, directory_fd: int) -> None:
    """Require a held directory descriptor to remain at its repository path."""
    try:
        visible = os.lstat(target_root / rel_path)
        held = os.fstat(directory_fd)
    except OSError as exc:
        raise RuntimeError("uninstall target path changed during safe operation") from exc
    if (
        stat.S_ISLNK(visible.st_mode)
        or not stat.S_ISDIR(visible.st_mode)
        or not stat.S_ISDIR(held.st_mode)
        or visible.st_dev != held.st_dev
        or visible.st_ino != held.st_ino
    ):
        raise RuntimeError("uninstall target path changed during safe operation")


def _assert_uninstall_tree_entry_identity(
    directory_fd: int,
    name: str,
    expected: os.stat_result,
) -> None:
    """Reject a recursive entry that was replaced after it was observed."""
    try:
        current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except OSError as exc:
        raise RuntimeError("uninstall target changed during safe operation") from exc
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
        raise RuntimeError("uninstall target changed during safe operation")


def _remove_uninstall_tree_fd(
    target_root: Path,
    rel_path: Path,
    directory_fd: int,
    visible_fds: tuple[int, ...],
) -> None:
    """Remove an installer-owned tree while preserving repository binding."""
    _assert_uninstall_visible_chain(target_root, rel_path, visible_fds)
    _assert_uninstall_directory_binding(target_root, rel_path, directory_fd)

    for name in os.listdir(directory_fd):
        _assert_uninstall_visible_chain(target_root, rel_path, visible_fds)
        _assert_uninstall_directory_binding(target_root, rel_path, directory_fd)
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISLNK(entry.st_mode):
            raise RuntimeError("refusing to remove symlink inside uninstall target")
        if stat.S_ISDIR(entry.st_mode):
            child_rel_path = rel_path / name
            child_fd = os.open(name, _uninstall_directory_flags(), dir_fd=directory_fd)
            try:
                _remove_uninstall_tree_fd(
                    target_root,
                    child_rel_path,
                    child_fd,
                    (*visible_fds, child_fd),
                )
                _assert_uninstall_visible_chain(target_root, rel_path, visible_fds)
                _assert_uninstall_directory_binding(target_root, rel_path, directory_fd)
                _assert_uninstall_directory_binding(target_root, child_rel_path, child_fd)
                _assert_uninstall_tree_entry_identity(directory_fd, name, entry)
                os.rmdir(name, dir_fd=directory_fd)
            finally:
                os.close(child_fd)
            continue
        if stat.S_ISREG(entry.st_mode) and entry.st_nlink != 1:
            raise RuntimeError("refusing to remove hard-linked uninstall target")
        if not stat.S_ISREG(entry.st_mode):
            raise RuntimeError("refusing to remove unsafe entry inside uninstall target")
        _assert_uninstall_tree_entry_identity(directory_fd, name, entry)
        _assert_uninstall_visible_chain(target_root, rel_path, visible_fds)
        _assert_uninstall_directory_binding(target_root, rel_path, directory_fd)
        os.unlink(name, dir_fd=directory_fd)


def _create_uninstall_retry_marker(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> None:
    payload = (json.dumps(_uninstall_retry_marker_payload(), sort_keys=True) + "\n").encode("utf-8")
    marker_rel = _UNINSTALL_RETRY_MARKER_REL
    with _open_uninstall_parent_chain(
        target_root,
        marker_rel,
        create_missing=False,
        expected_root_identity=expected_root_identity,
    ) as fds:
        parent_fd = fds[-1]
        _assert_uninstall_visible_chain(target_root, marker_rel, fds)
        try:
            marker_fd = os.open(
                marker_rel.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                0o600,
                dir_fd=parent_fd,
            )
        except FileExistsError:
            nofollow = getattr(os, "O_NOFOLLOW", None)
            if not isinstance(nofollow, int):
                raise RuntimeError("SpecDock uninstall retry marker no-follow support is unavailable") from None
            try:
                existing_fd = os.open(
                    marker_rel.name,
                    os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent_fd,
                )
            except OSError as exc:
                raise RuntimeError("SpecDock uninstall retry marker cannot be opened safely") from exc
            try:
                before = os.fstat(existing_fd)
                if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                    raise RuntimeError("SpecDock uninstall retry marker is not a safe regular file")
                existing_payload = _read_file_descriptor(existing_fd)
                after = os.fstat(existing_fd)
                if (
                    not stat.S_ISREG(after.st_mode)
                    or after.st_nlink != 1
                    or (after.st_dev, after.st_ino, after.st_ctime_ns, after.st_size)
                    != (before.st_dev, before.st_ino, before.st_ctime_ns, before.st_size)
                    or existing_payload != payload
                ):
                    raise RuntimeError("SpecDock uninstall retry marker is incomplete or invalid")
            finally:
                with suppress(OSError):
                    os.close(existing_fd)
            return
        marker_identity: tuple[int, int] | None = None
        completed = False
        try:
            created = os.fstat(marker_fd)
            if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
                raise RuntimeError("SpecDock uninstall retry marker is not a safe regular file")
            marker_identity = (created.st_dev, created.st_ino)
            _write_file_descriptor(marker_fd, payload)
            os.fsync(marker_fd)
            written = os.fstat(marker_fd)
            if (
                not stat.S_ISREG(written.st_mode)
                or written.st_nlink != 1
                or (written.st_dev, written.st_ino) != marker_identity
            ):
                raise RuntimeError("SpecDock uninstall retry marker is not a safe regular file")
            completed = True
        finally:
            with suppress(OSError):
                os.close(marker_fd)
            if not completed and marker_identity is not None:
                try:
                    current = os.stat(marker_rel.name, dir_fd=parent_fd, follow_symlinks=False)
                except OSError:
                    pass
                else:
                    if (
                        stat.S_ISREG(current.st_mode)
                        and current.st_nlink == 1
                        and (current.st_dev, current.st_ino) == marker_identity
                    ):
                        with suppress(OSError):
                            os.unlink(marker_rel.name, dir_fd=parent_fd)
        _assert_uninstall_visible_chain(target_root, marker_rel, fds)


def _write_uninstall_retry_marker(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> None:
    _create_uninstall_retry_marker(
        target_root,
        expected_root_identity=expected_root_identity,
    )


def _symlinked_uninstall_boundary_root(target_root: Path) -> Path | None:
    for boundary_root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS:
        if (target_root / boundary_root).is_symlink():
            return boundary_root
    return None


def _path_exists_for_uninstall(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _hash_uninstall_regular_fd(fd: int) -> tuple[str, os.stat_result]:
    """Hash one held regular-file descriptor and return its final stat."""
    before = os.fstat(fd)
    digest = hashlib.sha256()
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    after = os.fstat(fd)
    if (
        before.st_dev,
        before.st_ino,
        before.st_ctime_ns,
        before.st_size,
    ) != (
        after.st_dev,
        after.st_ino,
        after.st_ctime_ns,
        after.st_size,
    ):
        raise RuntimeError("uninstall target changed while capturing identity")
    return digest.hexdigest(), after


def _capture_uninstall_target_identity(target_root: Path, rel_path: Path) -> _UninstallTargetIdentity | None:
    """Capture a target identity through a no-follow parent descriptor chain."""
    if not _path_exists_for_uninstall(target_root / rel_path):
        return None
    with _open_uninstall_parent_chain(target_root, rel_path) as fds:
        parent_fd = fds[-1]
        try:
            info = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None
        if stat.S_ISLNK(info.st_mode):
            return _UninstallTargetIdentity(
                "symlink",
                info.st_dev,
                info.st_ino,
                info.st_ctime_ns,
                link_target=os.readlink(rel_path.name, dir_fd=parent_fd),
            )
        if stat.S_ISDIR(info.st_mode):
            return _UninstallTargetIdentity("directory", info.st_dev, info.st_ino, info.st_ctime_ns)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            return _UninstallTargetIdentity("unsafe", info.st_dev, info.st_ino, info.st_ctime_ns)
        fd = os.open(
            rel_path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            dir_fd=parent_fd,
        )
        try:
            digest, final_info = _hash_uninstall_regular_fd(fd)
        finally:
            os.close(fd)
        return _UninstallTargetIdentity(
            "regular",
            final_info.st_dev,
            final_info.st_ino,
            final_info.st_ctime_ns,
            size=final_info.st_size,
            sha256=digest,
        )


def _assert_uninstall_target_identity(
    parent_fd: int,
    name: str,
    info: os.stat_result,
    expected: _UninstallTargetIdentity,
) -> None:
    """Fail closed when a planned uninstall entry was replaced or rewritten."""
    if expected.kind == "symlink":
        if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent_fd) != expected.link_target:
            raise RuntimeError("uninstall target identity changed during safe operation")
        return
    if expected.kind == "directory":
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_dev != expected.device
            or info.st_ino != expected.inode
            or info.st_ctime_ns != expected.ctime_ns
        ):
            raise RuntimeError("uninstall target identity changed during safe operation")
        return
    if expected.kind != "regular" or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise RuntimeError("uninstall target identity changed during safe operation")
    if (
        info.st_dev != expected.device
        or info.st_ino != expected.inode
        or info.st_ctime_ns != expected.ctime_ns
        or info.st_size != expected.size
    ):
        raise RuntimeError("uninstall target identity changed during safe operation")
    fd = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        dir_fd=parent_fd,
    )
    try:
        digest, final_info = _hash_uninstall_regular_fd(fd)
    finally:
        os.close(fd)
    if (
        digest != expected.sha256
        or final_info.st_dev != expected.device
        or final_info.st_ino != expected.inode
        or final_info.st_ctime_ns != expected.ctime_ns
        or final_info.st_size != expected.size
    ):
        raise RuntimeError("uninstall target identity changed during safe operation")


def _planned_uninstall_identity(
    target_root: Path,
    rel_path: Path,
) -> tuple[_UninstallTargetIdentity | None, bool]:
    identity = _capture_uninstall_target_identity(target_root, rel_path)
    return identity, identity is None


def _compare_uninstall_bytes(target_path: Path, expected: bytes) -> tuple[bool, str | None]:
    if target_path.is_symlink():
        return False, "comparison error: symlink requires manual review"
    if not target_path.is_file():
        return False, "comparison error: not a regular file; manual review required"
    try:
        actual = target_path.read_bytes()
    except OSError as e:
        return False, f"comparison error: {e}; manual review required"
    if actual == expected:
        return True, None
    return False, "content mismatch; manual review required"


def _add_exact_match_uninstall_action(
    actions: list[_UninstallAction],
    target_root: Path,
    rel_path: Path,
    *,
    category: str,
    expected: bytes,
    include_missing_removals: bool = False,
) -> None:
    identity, expected_absent = _planned_uninstall_identity(target_root, rel_path)
    if expected_absent:
        if include_missing_removals:
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category=category,
                    status="would_remove",
                    reason="current shipped asset exact match",
                    expected_absent=True,
                )
            )
        return

    expected_digest = hashlib.sha256(expected).hexdigest()
    if identity is not None and identity.kind == "regular" and identity.sha256 == expected_digest:
        actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category=category,
                status="would_remove",
                reason="current shipped asset exact match",
                expected_identity=identity,
            )
        )
    else:
        actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category=category,
                status="preserved",
                reason="content mismatch; manual review required",
            )
        )


def _uninstall_category_for_install_root_path(
    rel_path: Path,
    *,
    bootstrap_only_rel_paths: set[Path],
) -> str:
    if rel_path.parts[:2] == (".agents", "skills"):
        return "agent_skill"
    if rel_path.parts[:2] in {(".codex", "agents"), (".github", "agents")}:
        return "native_agent"
    if rel_path in bootstrap_only_rel_paths:
        return "bootstrap_only"
    if rel_path == Path(".agents/host-adapters/meta.json"):
        return "bootstrap_only"
    if rel_path.parts[:2] in {
        (".codex", "prompts"),
        (".codex", "rules"),
        (".github", "workflows"),
    } or rel_path == Path(".codex/AGENTS.md"):
        return "product_reusable"
    return "product_reusable"


def _is_delete_even_if_mismatch_uninstall_path(rel_path: Path) -> bool:
    return rel_path.parts[:2] in {
        (".agents", "skills"),
        (".codex", "agents"),
        (".github", "agents"),
    } or rel_path == Path("spec-dock/spec-dock.version")


def _iter_existing_files_or_symlinks(root: Path) -> tuple[Path, ...]:
    if not root.exists():
        return ()
    if root.is_symlink():
        return (root,)
    return tuple(
        sorted((path for path in root.rglob("*") if path.is_file() or path.is_symlink()), key=lambda p: p.as_posix())
    )


def _add_generated_state_uninstall_actions(
    actions: list[_UninstallAction],
    target_root: Path,
    known_rel_paths: set[Path],
) -> None:
    for rel_root in (Path("spec-dock/active"), Path("spec-dock/.agent")):
        for path in _iter_existing_files_or_symlinks(target_root / rel_root):
            rel_path = path.relative_to(target_root)
            known_rel_paths.add(rel_path)
            identity, expected_absent = _planned_uninstall_identity(target_root, rel_path)
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category="generated_state",
                    status="would_remove",
                    reason="SpecDock generated state",
                    expected_identity=identity,
                    expected_absent=expected_absent,
                )
            )


def _add_spec_history_uninstall_action(
    actions: list[_UninstallAction],
    target_root: Path,
    *,
    specs_mode: str | None,
    include_missing_removals: bool = False,
) -> None:
    spec_history_path = Path("spec-dock/initiatives")
    if not (target_root / spec_history_path).exists() and not (specs_mode == "remove" and include_missing_removals):
        return
    if specs_mode == "remove":
        identity, expected_absent = _planned_uninstall_identity(target_root, spec_history_path)
        actions.append(
            _UninstallAction(
                rel_path=spec_history_path.as_posix(),
                category="spec_history",
                status="would_remove",
                reason="explicit remove-specs mode",
                expected_identity=identity,
                expected_absent=expected_absent,
            )
        )
    else:
        reason = (
            "keep-specs mode" if specs_mode == "keep" else "dry-run preserves specs unless remove-specs is explicit"
        )
        actions.append(
            _UninstallAction(
                rel_path=spec_history_path.as_posix(),
                category="spec_history",
                status="preserved",
                reason=reason,
            )
        )


def _add_uninstall_retry_marker_action(
    actions: list[_UninstallAction], target_root: Path, known_rel_paths: set[Path]
) -> None:
    known_rel_paths.add(_UNINSTALL_RETRY_MARKER_REL)
    if not _path_exists_for_uninstall(target_root / _UNINSTALL_RETRY_MARKER_REL):
        return
    identity, expected_absent = _planned_uninstall_identity(target_root, _UNINSTALL_RETRY_MARKER_REL)
    actions.append(
        _UninstallAction(
            rel_path=_UNINSTALL_RETRY_MARKER_REL.as_posix(),
            category="generated_state",
            status="preserved",
            reason="SpecDock uninstall retry marker for idempotent rerun",
            expected_identity=identity,
            expected_absent=expected_absent,
        )
    )


def _add_shortcut_uninstall_action(actions: list[_UninstallAction], target_root: Path) -> None:
    shortcut = target_root / "spec"
    if not _path_exists_for_uninstall(shortcut):
        return
    if (
        shortcut.is_symlink() and os.readlink(shortcut) == f"{_SPEC_DOCK_DIRNAME}/scripts/spec-dock"  # noqa: PTH115 - raw exact target.
    ):
        identity, expected_absent = _planned_uninstall_identity(target_root, Path("spec"))
        actions.append(
            _UninstallAction(
                rel_path="spec",
                category="shortcut",
                status="would_remove",
                reason="repo-root shortcut targets spec-dock/scripts/spec-dock",
                expected_identity=identity,
                expected_absent=expected_absent,
            )
        )
    else:
        actions.append(
            _UninstallAction(
                rel_path="spec",
                category="shortcut",
                status="preserved",
                reason="not spec-dock shortcut; manual review required",
            )
        )


def _add_unknown_boundary_uninstall_actions(
    actions: list[_UninstallAction],
    target_root: Path,
    known_rel_paths: set[Path],
) -> None:
    for boundary_root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS:
        for path in _iter_existing_files_or_symlinks(target_root / boundary_root):
            rel_path = path.relative_to(target_root)
            if rel_path in known_rel_paths:
                continue
            if rel_path.parts[:2] == ("spec-dock", "initiatives"):
                continue
            if rel_path.parts[:2] in {("spec-dock", "active"), ("spec-dock", ".agent")}:
                continue
            if any(
                rel_path == managed_root or _is_path_prefix(managed_root, rel_path)
                for managed_root in _MANAGED_SCAFFOLD_ROOTS
            ):
                continue
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category="unmanaged",
                    status="preserved",
                    reason="unmanaged file under managed boundary root",
                )
            )


def _build_scaffold_uninstall_sources(assets_dir: Path) -> tuple[tuple[Path, bytes], ...]:
    src_spec_dock = assets_dir / "spec_dock"
    sources: list[tuple[Path, bytes]] = []
    for managed_dir in _MANAGED_DIRS:
        src_root = src_spec_dock / managed_dir
        if not src_root.is_dir():
            raise RuntimeError(f"Missing asset directory: spec_dock/{managed_dir}")
        for source_path in sorted(
            (
                path
                for path in src_root.rglob("*")
                if path.is_file() and not _is_generated_python_cache_path(path.relative_to(src_spec_dock))
            ),
            key=lambda p: p.as_posix(),
        ):
            rel_path = Path("spec-dock") / source_path.relative_to(src_spec_dock)
            sources.append((rel_path, source_path.read_bytes()))

    src_gitignore = src_spec_dock / ".gitignore"
    if not src_gitignore.is_file():
        raise RuntimeError("Missing asset file: spec_dock/.gitignore")
    sources.append((Path("spec-dock/.gitignore"), src_gitignore.read_bytes()))
    root_workbench_readme = src_spec_dock / "templates" / "root" / ".workbench" / "README.md"
    if not root_workbench_readme.is_file() or root_workbench_readme.is_symlink():
        raise RuntimeError("Missing asset file: spec_dock/templates/root/.workbench/README.md")
    sources.append((Path("spec-dock/.workbench/README.md"), root_workbench_readme.read_bytes()))
    sources.append((Path("spec-dock/spec-dock.version"), f"{_tool_version()}\n".encode()))
    return tuple(sources)


def _managed_scaffold_tree_safety_issue(target_root: Path, rel_root: Path) -> str | None:
    """Return a preflight diagnostic for unsafe recursive scaffold entries."""
    root = target_root / rel_root
    for current, directories, file_names in os.walk(root, topdown=True, followlinks=False):
        for name in (*directories, *file_names):
            path = Path(current) / name
            try:
                info = os.lstat(path)
            except OSError:
                return f"managed scaffold entry cannot be inspected safely: {path.relative_to(target_root)}"
            if stat.S_ISLNK(info.st_mode):
                return f"managed scaffold tree contains symlink: {path.relative_to(target_root)}"
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                return f"managed scaffold tree contains unsafe entry: {path.relative_to(target_root)}"
    return None


def _add_managed_scaffold_uninstall_actions(
    actions: list[_UninstallAction],
    target_root: Path,
    known_rel_paths: set[Path],
) -> None:
    """Plan each managed scaffold tree as one safe recursive removal."""
    for rel_root in _MANAGED_SCAFFOLD_ROOTS:
        known_rel_paths.add(rel_root)
        if not _path_exists_for_uninstall(target_root / rel_root):
            continue
        identity, expected_absent = _planned_uninstall_identity(target_root, rel_root)
        if identity is None or identity.kind != "directory":
            actions.append(
                _UninstallAction(
                    rel_path=rel_root.as_posix(),
                    category="scaffold_managed",
                    status="preserved",
                    reason="managed scaffold root is not a safe real directory; manual review required",
                )
            )
            continue
        safety_issue = _managed_scaffold_tree_safety_issue(target_root, rel_root)
        if safety_issue is not None:
            actions.append(
                _UninstallAction(
                    rel_path=rel_root.as_posix(),
                    category="scaffold_managed",
                    status="preserved",
                    reason=f"{safety_issue}; manual review required",
                )
            )
            continue
        actions.append(
            _UninstallAction(
                rel_path=rel_root.as_posix(),
                category="scaffold_managed",
                status="would_remove",
                reason="SpecDock managed scaffold tree",
                expected_identity=identity,
                expected_absent=expected_absent,
            )
        )


def _append_distribution_uninstall_actions(
    actions: list[_UninstallAction],
    target_root: Path,
    *,
    plan,
    include_missing_removals: bool,
    known_rel_paths: set[Path],
) -> None:
    """Project the shared ownership classifier into the uninstall report."""
    obsolete_paths = {Path(item["path"]) for item in plan.manifest.obsolete_exact_files}
    current_paths = {Path(asset.path) for asset in plan.current_assets}
    for distribution_action in plan.actions:
        rel_path = Path(distribution_action.path)
        if rel_path == Path("spec"):
            # The shortcut has a dedicated renderer with a more specific
            # target-link diagnostic below.
            continue
        known_rel_paths.add(rel_path)
        target_exists = _path_exists_for_uninstall(target_root / rel_path)
        if not target_exists and not include_missing_removals:
            continue

        category = (
            "obsolete_managed"
            if rel_path in obsolete_paths
            else _uninstall_category_for_install_root_path(
                rel_path,
                bootstrap_only_rel_paths=set(),
            )
        )
        if distribution_action.action == "prune":
            identity, expected_absent = _planned_uninstall_identity(target_root, rel_path)
            if rel_path in obsolete_paths:
                reason = (
                    "known obsolete SpecDock-managed asset"
                    if target_exists
                    else "known obsolete SpecDock-managed asset already absent"
                )
            elif distribution_action.provenance == "historical":
                reason = (
                    "historical SpecDock-managed asset exact identity"
                    if target_exists
                    else "historical SpecDock-managed asset already absent"
                )
            else:
                reason = (
                    "current shipped asset exact identity" if target_exists else "current shipped asset already absent"
                )
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category=category,
                    status="would_remove",
                    reason=reason,
                    expected_identity=identity,
                    expected_absent=expected_absent,
                )
            )
            continue

        if distribution_action.blocked or distribution_action.action == "preserve":
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category=category,
                    status="preserved",
                    reason=(f"{distribution_action.reason}; {distribution_action.operator_action}"),
                )
            )
            continue

        # Uninstall classification should never create/adopt/upgrade a target;
        # fail closed in the report if a future classifier change violates it.
        actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category=category,
                status="preserved",
                reason="unexpected uninstall classification; manual review required",
            )
        )

    if include_missing_removals:
        for item in plan.manifest.obsolete_exact_files:
            rel_path = Path(item["path"])
            known_rel_paths.add(rel_path)
            if rel_path in current_paths or _path_exists_for_uninstall(target_root / rel_path):
                continue
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category="obsolete_managed",
                    status="would_remove",
                    reason="known obsolete SpecDock-managed asset already absent",
                    expected_absent=True,
                )
            )


def _build_uninstall_plan(
    target_root: Path,
    *,
    specs_mode: str | None,
    include_missing_removals: bool = False,
) -> tuple[_UninstallAction, ...]:
    """Build the S02 dry-run inventory and classification plan."""
    actions: list[_UninstallAction] = []
    known_rel_paths: set[Path] = set()

    with _assets_dir() as assets_dir:
        distribution_plan = build_distribution_plan(
            assets_dir / "install_root",
            manifest_path=assets_dir / "managed_distribution.json",
            scaffold_root=assets_dir / "spec_dock",
            target_root=target_root,
            operation="uninstall",
        )
        _append_distribution_uninstall_actions(
            actions,
            target_root,
            plan=distribution_plan,
            include_missing_removals=include_missing_removals,
            known_rel_paths=known_rel_paths,
        )

        _add_managed_scaffold_uninstall_actions(actions, target_root, known_rel_paths)

        for rel_path, expected in _build_scaffold_uninstall_sources(assets_dir):
            if any(
                rel_path == managed_root or _is_path_prefix(managed_root, rel_path)
                for managed_root in _MANAGED_SCAFFOLD_ROOTS
            ):
                continue
            known_rel_paths.add(rel_path)
            if _is_delete_even_if_mismatch_uninstall_path(rel_path):
                if _path_exists_for_uninstall(target_root / rel_path) or include_missing_removals:
                    identity, expected_absent = _planned_uninstall_identity(target_root, rel_path)
                    actions.append(
                        _UninstallAction(
                            rel_path=rel_path.as_posix(),
                            category="scaffold_managed",
                            status="would_remove",
                            reason="SpecDock managed state",
                            expected_identity=identity,
                            expected_absent=expected_absent,
                        )
                    )
                continue
            _add_exact_match_uninstall_action(
                actions,
                target_root,
                rel_path,
                category="scaffold_managed",
                expected=expected,
                include_missing_removals=include_missing_removals,
            )

    _add_generated_state_uninstall_actions(actions, target_root, known_rel_paths)
    _add_spec_history_uninstall_action(
        actions,
        target_root,
        specs_mode=specs_mode,
        include_missing_removals=include_missing_removals,
    )
    _add_uninstall_retry_marker_action(actions, target_root, known_rel_paths)
    _add_shortcut_uninstall_action(actions, target_root)
    known_rel_paths.add(Path("spec"))
    _add_unknown_boundary_uninstall_actions(actions, target_root, known_rel_paths)

    return tuple(sorted(actions, key=lambda action: action.rel_path))


def _summarize_uninstall_actions(actions: tuple[_UninstallAction, ...]) -> dict[str, int]:
    summary = {
        "would_remove": 0,
        "removed": 0,
        "already_removed": 0,
        "preserved": 0,
        "failed": 0,
        "empty_dir_removed": 0,
    }
    for action in actions:
        if action.status not in summary:
            summary[action.status] = 0
        summary[action.status] += 1
    return summary


def _is_safe_uninstall_rel_path(rel_path: Path) -> bool:
    if rel_path.is_absolute() or ".." in rel_path.parts or rel_path.parts in {(), (".",)}:
        return False
    if rel_path.parts[0] == ".git":
        return False
    return rel_path.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS} or rel_path == Path(
        "spec"
    )


def _remove_uninstall_path(
    target_root: Path,
    action: _UninstallAction,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> _UninstallAction:
    rel_path = Path(action.rel_path)
    if not _is_safe_uninstall_rel_path(rel_path):
        return action._replace(status="failed", error="unsafe uninstall path outside managed boundaries")
    # Cleanup actions are ordered deepest-first.  A previously removed parent
    # therefore makes later child entries idempotently absent; avoid treating
    # that expected state as a safety failure before opening the descriptor
    # chain.
    if not _path_exists_for_uninstall(target_root / rel_path):
        return action._replace(status="already_removed", error=None)
    try:
        with _open_uninstall_parent_chain(
            target_root,
            rel_path,
            expected_root_identity=expected_root_identity,
        ) as fds:
            parent_fd = fds[-1]
            _assert_uninstall_visible_chain(target_root, rel_path, fds)
            try:
                info = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                if action.expected_absent:
                    return action._replace(status="already_removed", error=None)
                if action.expected_identity is not None:
                    return action._replace(status="already_removed", error=None)
                return action._replace(status="already_removed", error=None)

            if action.expected_absent:
                return action._replace(
                    status="failed",
                    error="uninstall target appeared after preflight",
                )
            if action.expected_identity is None:
                return action._replace(
                    status="failed",
                    error="uninstall target identity was not captured during preflight",
                )
            try:
                _assert_uninstall_target_identity(
                    parent_fd,
                    rel_path.name,
                    info,
                    action.expected_identity,
                )
            except (OSError, RuntimeError) as exc:
                return action._replace(status="failed", error=str(exc))

            if stat.S_ISLNK(info.st_mode):
                # A managed file is never removed through a symlink.  The only
                # intentional symlink removals are the exact repo-root shortcut
                # and generated active pointers under the managed scaffold.
                is_generated_active_pointer = action.category == "generated_state" and rel_path.parts[:2] == (
                    "spec-dock",
                    "active",
                )
                if action.category != "shortcut" and not is_generated_active_pointer:
                    return action._replace(
                        status="failed",
                        error="unsafe uninstall target symlink requires manual review",
                    )
                if action.category == "shortcut":
                    try:
                        link_target = os.readlink(rel_path.name, dir_fd=parent_fd)
                    except OSError as exc:
                        return action._replace(status="failed", error=str(exc))
                    if link_target != f"{_SPEC_DOCK_DIRNAME}/scripts/spec-dock":
                        return action._replace(
                            status="failed",
                            error="unsafe uninstall shortcut target requires manual review",
                        )
                os.unlink(rel_path.name, dir_fd=parent_fd)
            elif stat.S_ISDIR(info.st_mode):
                if action.category not in {"spec_history", "scaffold_managed"}:
                    return action._replace(
                        status="failed",
                        error="unexpected uninstall directory requires manual review",
                    )
                directory_fd = os.open(rel_path.name, _uninstall_directory_flags(), dir_fd=parent_fd)
                try:
                    _remove_uninstall_tree_fd(target_root, rel_path, directory_fd, (*fds, directory_fd))
                finally:
                    os.close(directory_fd)
                os.rmdir(rel_path.name, dir_fd=parent_fd)
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    return action._replace(
                        status="failed",
                        error="refusing to remove hard-linked uninstall target",
                    )
                os.unlink(rel_path.name, dir_fd=parent_fd)
            else:
                return action._replace(
                    status="failed",
                    error="unsafe uninstall target type requires manual review",
                )
            _assert_uninstall_visible_chain(target_root, rel_path, fds)
    except (OSError, RuntimeError) as exc:
        return action._replace(status="failed", error=str(exc))
    return action._replace(status="removed", error=None)


def _is_uninstall_cleanup_boundary_path(rel_path: Path) -> bool:
    if rel_path.is_absolute() or ".." in rel_path.parts or rel_path.parts in {(), (".",)}:
        return False
    if rel_path.parts[0] == ".git":
        return False
    return rel_path.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS}


def _cleanup_empty_uninstall_dirs(
    target_root: Path,
    actions: tuple[_UninstallAction, ...],
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> tuple[_UninstallAction, ...]:
    cleanup_actions: list[_UninstallAction] = []
    candidates: set[Path] = set()

    # Cleanup is derived only from proven managed removals.  Scanning every
    # directory under a boundary would turn an unknown empty user directory
    # into an implicit deletion candidate.
    protected: set[Path] = set()
    for action in actions:
        rel_path = Path(action.rel_path)
        if action.status == "preserved":
            protected.add(rel_path)
            if rel_path.parts and rel_path.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS}:
                protected.update(rel_path.parents)
            continue
        if action.status != "removed" or rel_path == _UNINSTALL_RETRY_MARKER_REL:
            continue
        current = rel_path if action.category == "spec_history" else rel_path.parent
        while current.parts and current.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS}:
            candidates.add(current)
            current = current.parent

    for rel_path in sorted(candidates, key=lambda path: len(path.parts), reverse=True):
        if not _is_uninstall_cleanup_boundary_path(rel_path):
            continue
        if rel_path in protected:
            continue
        try:
            with _open_uninstall_parent_chain(
                target_root,
                rel_path,
                expected_root_identity=expected_root_identity,
            ) as fds:
                parent_fd = fds[-1]
                _assert_uninstall_visible_chain(target_root, rel_path, fds)
                try:
                    info = os.stat(rel_path.name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
                    continue
                os.rmdir(rel_path.name, dir_fd=parent_fd)
                _assert_uninstall_visible_chain(target_root, rel_path, fds)
        except (OSError, RuntimeError):
            continue
        cleanup_actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category="empty_dir",
                status="empty_dir_removed",
                reason="empty directory cleanup inside uninstall boundary",
            )
        )
    return tuple(cleanup_actions)


def _apply_uninstall_plan(
    target_root: Path,
    actions: tuple[_UninstallAction, ...],
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> tuple[_UninstallAction, ...]:
    results: list[_UninstallAction] = []
    for action in actions:
        if action.status == "would_remove":
            results.append(
                _remove_uninstall_path(
                    target_root,
                    action,
                    expected_root_identity=expected_root_identity,
                )
            )
        else:
            results.append(action)
    results.extend(
        _cleanup_empty_uninstall_dirs(
            target_root,
            tuple(results),
            expected_root_identity=expected_root_identity,
        )
    )
    return tuple(sorted(results, key=lambda action: (action.rel_path, action.status)))


def _uninstall_apply_blockers(
    actions: tuple[_UninstallAction, ...],
    *,
    specs_mode: str,
) -> tuple[_UninstallAction, ...]:
    """Return preserved findings that must stop an uninstall before mutation.

    ``keep-specs`` and the legacy uninstall retry marker are intentional
    preserved state.  Every other preserved action represents an ownership,
    type, or boundary collision and therefore blocks the entire apply plan;
    executing unrelated ``would_remove`` actions would violate the shared
    classifier's fail-closed contract.
    """

    blockers: list[_UninstallAction] = []
    for action in actions:
        if action.status != "preserved":
            continue
        if action.category == "spec_history" and specs_mode == "keep":
            continue
        if action.rel_path == _UNINSTALL_RETRY_MARKER_REL.as_posix():
            continue
        blockers.append(action)
    return tuple(blockers)


def _ensure_uninstall_retry_marker_action(
    actions: tuple[_UninstallAction, ...],
) -> tuple[_UninstallAction, ...]:
    """Expose the marker as a managed action without scheduling early removal."""

    marker_path = _UNINSTALL_RETRY_MARKER_REL.as_posix()
    if any(action.rel_path == marker_path for action in actions):
        return actions
    return tuple(
        sorted(
            (
                *actions,
                _UninstallAction(
                    rel_path=marker_path,
                    category="generated_state",
                    status="preserved",
                    reason="SpecDock uninstall retry marker removed last after post-verify",
                ),
            ),
            key=lambda action: action.rel_path,
        )
    )


def _remove_uninstall_retry_marker(
    target_root: Path,
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
    expected_identity: _UninstallTargetIdentity | None = None,
) -> None:
    """Remove the legacy uninstall marker only after every other action passes."""
    marker_rel = _UNINSTALL_RETRY_MARKER_REL
    with _open_uninstall_parent_chain(
        target_root,
        marker_rel,
        expected_root_identity=expected_root_identity,
    ) as fds:
        parent_fd = fds[-1]
        _assert_uninstall_visible_chain(target_root, marker_rel, fds)
        try:
            info = os.stat(marker_rel.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise RuntimeError("SpecDock uninstall retry marker is not a safe regular file")
        if expected_identity is not None:
            _assert_uninstall_target_identity(parent_fd, marker_rel.name, info, expected_identity)
        os.unlink(marker_rel.name, dir_fd=parent_fd)
        _assert_uninstall_visible_chain(target_root, marker_rel, fds)


def _finalize_uninstall_retry_marker(
    target_root: Path,
    actions: tuple[_UninstallAction, ...],
    *,
    expected_root_identity: DistributionRootIdentity | None = None,
) -> tuple[_UninstallAction, ...]:
    """Remove the marker last and reflect that mutation in the result ledger."""

    marker_identity = _capture_uninstall_target_identity(target_root, _UNINSTALL_RETRY_MARKER_REL)
    if marker_identity is None:
        raise RuntimeError("SpecDock uninstall retry marker disappeared before finalization")
    _remove_uninstall_retry_marker(
        target_root,
        expected_root_identity=expected_root_identity,
        expected_identity=marker_identity,
    )
    marker_path = _UNINSTALL_RETRY_MARKER_REL.as_posix()
    finalized = [
        action._replace(
            status="removed",
            reason="SpecDock uninstall retry marker removed after post-verify",
            error=None,
        )
        if action.rel_path == marker_path
        else action
        for action in actions
    ]
    return tuple(sorted(finalized, key=lambda action: (action.rel_path, action.status)))


def _verify_uninstall_postcondition(
    target_root: Path,
    actions: tuple[_UninstallAction, ...],
    *,
    expected_root_identity: DistributionRootIdentity,
) -> None:
    """Verify every scheduled removal is absent before marker deletion."""

    _assert_distribution_root_identity(target_root, expected_root_identity)
    marker_path = _UNINSTALL_RETRY_MARKER_REL.as_posix()
    for action in actions:
        if action.status not in {"removed", "already_removed", "empty_dir_removed"}:
            continue
        if action.rel_path == marker_path:
            continue
        if _path_exists_for_uninstall(target_root / action.rel_path):
            raise RuntimeError(f"uninstall post-verify found residual managed path: {action.rel_path}")
    _assert_distribution_root_identity(target_root, expected_root_identity)


def _uninstall_payload(
    target_root: Path,
    *,
    apply: bool,
    specs_mode: str | None,
    actions: tuple[_UninstallAction, ...],
    status: str | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "target": str(target_root),
        "mode": "apply" if apply else "dry-run",
        "apply": apply,
        "specs_mode": specs_mode,
        "status": status or ("completed" if apply else "planned"),
        "summary": _summarize_uninstall_actions(actions),
        "actions": [
            {
                "path": action.rel_path,
                "category": action.category,
                "status": action.status,
                "reason": action.reason,
                "error": action.error,
            }
            for action in actions
        ],
        "guidance": [
            (
                "dry-run only; pass --apply with exactly one of --keep-specs or --remove-specs to mutate"
                if not apply
                else "retry removal with installer CLI: spec-dock uninstall <target> --apply --keep-specs or --remove-specs"
            ),
            "reinstall or refresh with installer CLI: spec-dock init <target> or spec-dock update <target>",
        ],
        "errors": errors or [],
    }


def _emit_uninstall_preflight_error(
    target_root: Path,
    *,
    apply: bool,
    specs_mode: str | None,
    json_requested: bool,
    message: str,
) -> int:
    if json_requested:
        payload = _uninstall_payload(
            target_root,
            apply=apply,
            specs_mode=specs_mode,
            actions=(),
            status="error",
            errors=[message],
        )
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"error: {message}", file=sys.stderr)
    return 2


def _render_uninstall_text(payload: dict[str, Any]) -> str:
    noun = "result" if payload["apply"] else "plan"
    lines = [
        f"spec-dock: uninstall {noun} ({payload['mode']}) -> {payload['target']}",
        f"specs_mode: {payload['specs_mode'] or 'unspecified'}",
        "summary:",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"  {key}: {value}")
    lines.append("actions:")
    for action in payload["actions"]:
        lines.append(f"  [{action['status']}] {action['path']} category={action['category']} reason={action['reason']}")
    lines.append("guidance:")
    for item in payload["guidance"]:
        lines.append(f"  - {item}")
    return "\n".join(lines)


def _run_uninstall(target_root: Path, ns: argparse.Namespace) -> int:
    specs_mode = _uninstall_specs_mode(ns)
    apply_requested = bool(ns.apply)
    json_requested = bool(ns.json)

    if not target_root.exists() or not target_root.is_dir():
        return _emit_uninstall_preflight_error(
            target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
            message=f"target path is not a directory: {target_root}",
        )

    if apply_requested and specs_mode is None:
        return _emit_uninstall_preflight_error(
            target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
            message=("uninstall --apply requires exactly one specs mode: --keep-specs or --remove-specs"),
        )

    try:
        uninstall_root_identity = _distribution_root_identity(target_root)
    except RuntimeError as e:
        return _emit_uninstall_preflight_error(
            target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
            message=str(e),
        )

    try:
        _admit_distribution_cli(target_root, operation="uninstall")
        if apply_requested:
            symlink_boundary = _symlinked_uninstall_boundary_root(target_root)
            if symlink_boundary is not None:
                return _emit_uninstall_preflight_error(
                    target_root,
                    apply=apply_requested,
                    specs_mode=specs_mode,
                    json_requested=json_requested,
                    message=(
                        f"target contains symlinked SpecDock uninstall boundary root: {symlink_boundary.as_posix()}"
                    ),
                )
            _reject_symlinked_uninstall_retry_marker(target_root)
        _require_managed_specdock_for_uninstall(target_root)
    except (OSError, RuntimeError) as e:
        return _emit_uninstall_preflight_error(
            target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
            message=str(e),
        )

    try:
        # The complete plan must be validated before the first apply mutation.
        # In particular, a preserved ownership collision blocks every unrelated
        # removal; do not create the retry marker until that gate passes.
        actions = _build_uninstall_plan(
            target_root,
            specs_mode=specs_mode,
            include_missing_removals=apply_requested,
        )
    except (OSError, RuntimeError) as e:
        return _emit_uninstall_preflight_error(
            target_root,
            apply=apply_requested,
            specs_mode=specs_mode,
            json_requested=json_requested,
            message=str(e),
        )
    if apply_requested:
        assert specs_mode is not None
        blockers = _uninstall_apply_blockers(actions, specs_mode=specs_mode)
        if blockers:
            payload = _uninstall_payload(
                target_root,
                apply=True,
                specs_mode=specs_mode,
                actions=actions,
                status="blocked",
                errors=[
                    "uninstall apply blocked before mutation: "
                    + "; ".join(f"{action.rel_path}: {action.reason}" for action in blockers)
                ],
            )
            if json_requested:
                print(json.dumps(payload, sort_keys=True))
            else:
                print(_render_uninstall_text(payload))
            return 1

        try:
            _write_uninstall_retry_marker(
                target_root,
                expected_root_identity=uninstall_root_identity,
            )
            actions = _ensure_uninstall_retry_marker_action(actions)
            actions = _apply_uninstall_plan(
                target_root,
                actions,
                expected_root_identity=uninstall_root_identity,
            )
        except (OSError, RuntimeError) as e:
            payload = _uninstall_payload(
                target_root,
                apply=True,
                specs_mode=specs_mode,
                actions=actions,
                status="partial_failure",
                errors=[str(e)],
            )
            if json_requested:
                print(json.dumps(payload, sort_keys=True))
            else:
                print(_render_uninstall_text(payload))
            return 1

    has_failures = any(action.status == "failed" for action in actions)
    if apply_requested and not has_failures:
        try:
            _verify_uninstall_postcondition(
                target_root,
                actions,
                expected_root_identity=uninstall_root_identity,
            )
            actions = _finalize_uninstall_retry_marker(
                target_root,
                actions,
                expected_root_identity=uninstall_root_identity,
            )
        except (OSError, RuntimeError) as e:
            payload = _uninstall_payload(
                target_root,
                apply=True,
                specs_mode=specs_mode,
                actions=actions,
                status="partial_failure",
                errors=[str(e)],
            )
            if json_requested:
                print(json.dumps(payload, sort_keys=True))
            else:
                print(_render_uninstall_text(payload))
            return 1

    payload = _uninstall_payload(
        target_root,
        apply=apply_requested,
        specs_mode=specs_mode,
        actions=actions,
        status="partial_failure" if has_failures else None,
    )
    if json_requested:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(_render_uninstall_text(payload))
    return 1 if has_failures else 0


def _iter_install_root_files(assets_dir: Path) -> tuple[Path, ...]:
    install_root = assets_dir / "install_root"
    if not install_root.is_dir():
        raise RuntimeError("Missing asset directory: install_root")
    return tuple(
        sorted(
            (
                candidate
                for candidate in install_root.rglob("*")
                if candidate.is_file() and not _is_generated_python_cache_path(candidate.relative_to(install_root))
            ),
            key=lambda candidate: candidate.relative_to(install_root).as_posix(),
        )
    )


def _build_current_managed_file_mappings(
    assets_dir: Path,
) -> tuple[tuple[_ManagedCurrentFileMapping, ...], dict[Path, Path]]:
    install_root = assets_dir / "install_root"
    mappings: list[_ManagedCurrentFileMapping] = []
    source_by_target: dict[Path, Path] = {}
    for source_path in _iter_install_root_files(assets_dir):
        target_rel = source_path.relative_to(install_root)
        source_asset_rel = Path("install_root") / target_rel
        existing_source = source_by_target.get(target_rel)
        if existing_source is not None and existing_source != source_asset_rel:
            raise RuntimeError(
                "duplicate current managed file mapping for target "
                f"'{target_rel.as_posix()}' from '{existing_source.as_posix()}' and "
                f"'{source_asset_rel.as_posix()}'"
            )
        source_by_target[target_rel] = source_asset_rel
        mappings.append(
            _ManagedCurrentFileMapping(
                source_asset_rel=source_asset_rel,
                target_rel=target_rel,
            )
        )
    return tuple(mappings), source_by_target


def _is_collision_aware_additive_skill_path(target_rel: Path) -> bool:
    parts = target_rel.parts
    return len(parts) >= 4 and parts[:2] == (".agents", "skills") and parts[2] in _COLLISION_AWARE_ADDITIVE_SKILL_NAMES


def _preflight_collision_aware_additive_skill_assets(
    target_root: Path,
    *,
    assets_dir: Path,
    mappings: tuple[_ManagedCurrentFileMapping, ...],
) -> None:
    for mapping in mappings:
        if not _is_collision_aware_additive_skill_path(mapping.target_rel):
            continue
        target_path = target_root / mapping.target_rel
        if not target_path.exists():
            if target_path.is_symlink():
                raise RuntimeError(
                    "target path conflict for additive skill asset "
                    f"'{mapping.target_rel.as_posix()}' (dangling symlink)"
                )
            continue
        if target_path.is_symlink() or not target_path.is_file():
            raise RuntimeError(
                "target path conflict for additive skill asset "
                f"'{mapping.target_rel.as_posix()}' (expected an ordinary file)"
            )
        source_path = assets_dir / mapping.source_asset_rel
        if target_path.read_bytes() != source_path.read_bytes():
            raise RuntimeError(
                "refusing to overwrite non-identical additive skill asset "
                f"'{mapping.target_rel.as_posix()}'; preserve or relocate the existing file first"
            )


def _additive_skill_directory_flags() -> int:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if not isinstance(nofollow, int) or not isinstance(directory, int):
        raise RuntimeError("platform lacks required no-follow directory support for additive skill assets")
    return os.O_RDONLY | nofollow | directory | getattr(os, "O_CLOEXEC", 0)


def _open_additive_skill_parent(target_root: Path, target_rel: Path, *, create_missing: bool) -> int:
    flags = _additive_skill_directory_flags()
    try:
        current_fd = os.open(target_root, flags)
    except OSError as exc:
        raise RuntimeError(f"cannot open additive skill target root without following symlinks: {exc}") from exc

    try:
        for component in target_rel.parts[:-1]:
            try:
                next_fd = os.open(component, flags, dir_fd=current_fd)
            except FileNotFoundError:
                if not create_missing:
                    raise RuntimeError(
                        f"missing additive skill parent component '{component}' for '{target_rel.as_posix()}'"
                    ) from None
                with suppress(FileExistsError):
                    os.mkdir(component, dir_fd=current_fd)
                try:
                    next_fd = os.open(component, flags, dir_fd=current_fd)
                except OSError as exc:
                    raise RuntimeError(
                        f"unsafe additive skill parent component '{component}' for '{target_rel.as_posix()}': {exc}"
                    ) from exc
            except OSError as exc:
                raise RuntimeError(
                    f"unsafe additive skill parent component '{component}' for '{target_rel.as_posix()}': {exc}"
                ) from exc
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def _read_file_descriptor(fd: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = os.read(fd, 1024 * 64)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _write_file_descriptor(
    fd: int,
    content: bytes,
    *,
    before_first_write: Callable[[], None] | None = None,
) -> None:
    if before_first_write is not None:
        before_first_write()
    view = memoryview(content)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            raise RuntimeError("additive skill asset write made no progress")
        written += count


def _require_additive_skill_parent_still_bound(
    *,
    target_root: Path,
    target_rel: Path,
    parent_fd: int,
) -> None:
    try:
        rebound_fd = _open_additive_skill_parent(target_root, target_rel, create_missing=False)
    except RuntimeError as exc:
        raise RuntimeError(
            f"additive skill parent moved outside the repository for '{target_rel.as_posix()}': {exc}"
        ) from exc
    try:
        opened = os.fstat(parent_fd)
        rebound = os.fstat(rebound_fd)
        if (opened.st_dev, opened.st_ino) != (rebound.st_dev, rebound.st_ino):
            raise RuntimeError(f"additive skill parent moved outside the repository for '{target_rel.as_posix()}'")
    finally:
        os.close(rebound_fd)


def _verify_existing_additive_skill_asset(
    *,
    source_bytes: bytes,
    target_root: Path,
    target_rel: Path,
) -> None:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise RuntimeError("platform lacks required no-follow file support for additive skill assets")
    parent_fd = _open_additive_skill_parent(target_root, target_rel, create_missing=False)
    file_fd: int | None = None
    try:
        try:
            file_fd = os.open(
                target_rel.name,
                os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent_fd,
            )
        except OSError as exc:
            raise RuntimeError(
                "target path conflict for additive skill asset "
                f"'{target_rel.as_posix()}' (symlink or unreadable entry): {exc}"
            ) from exc
        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(
                f"target path conflict for additive skill asset '{target_rel.as_posix()}' (expected an ordinary file)"
            )
        if _read_file_descriptor(file_fd) != source_bytes:
            raise RuntimeError(
                "refusing to overwrite non-identical additive skill asset "
                f"'{target_rel.as_posix()}'; preserve or relocate the existing file first"
            )
        observed = os.stat(target_rel.name, dir_fd=parent_fd, follow_symlinks=False)
        if (observed.st_dev, observed.st_ino) != (info.st_dev, info.st_ino):
            raise RuntimeError(f"target path changed while adopting additive skill asset '{target_rel.as_posix()}'")
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)


def _materialize_collision_aware_additive_skill_asset(
    *,
    source_path: Path,
    target_root: Path,
    target_rel: Path,
) -> None:
    source_bytes = source_path.read_bytes()
    source_mode = stat.S_IMODE(source_path.stat().st_mode)
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if not isinstance(nofollow, int):
        raise RuntimeError("platform lacks required no-follow file support for additive skill assets")

    parent_fd = _open_additive_skill_parent(target_root, target_rel, create_missing=True)
    file_fd: int | None = None
    try:
        _require_additive_skill_parent_still_bound(
            target_root=target_root,
            target_rel=target_rel,
            parent_fd=parent_fd,
        )
        try:
            file_fd = os.open(
                target_rel.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow | getattr(os, "O_CLOEXEC", 0),
                source_mode,
                dir_fd=parent_fd,
            )
        except FileExistsError:
            os.close(parent_fd)
            parent_fd = -1
            _verify_existing_additive_skill_asset(
                source_bytes=source_bytes,
                target_root=target_root,
                target_rel=target_rel,
            )
            return

        created = os.fstat(file_fd)
        if not stat.S_ISREG(created.st_mode) or created.st_nlink != 1:
            raise RuntimeError(f"new additive skill asset is not a safe ordinary file: '{target_rel.as_posix()}'")
        _write_file_descriptor(
            file_fd,
            source_bytes,
            before_first_write=lambda: _require_additive_skill_parent_still_bound(
                target_root=target_root,
                target_rel=target_rel,
                parent_fd=parent_fd,
            ),
        )
        os.fsync(file_fd)
        _require_additive_skill_parent_still_bound(
            target_root=target_root,
            target_rel=target_rel,
            parent_fd=parent_fd,
        )
        observed = os.stat(target_rel.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != (created.st_dev, created.st_ino)
        ):
            raise RuntimeError(f"target path changed while creating additive skill asset '{target_rel.as_posix()}'")
    except OSError as exc:
        raise RuntimeError(f"cannot safely materialize additive skill asset '{target_rel.as_posix()}': {exc}") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if parent_fd >= 0:
            os.close(parent_fd)


def _build_managed_skill_install_plan(assets_dir: Path) -> _ManagedSkillInstallPlan:
    managed_skill_names = _managed_skill_names()
    current_file_mappings, source_by_target = _build_current_managed_file_mappings(assets_dir)

    for skill_name in managed_skill_names:
        target_rel = Path(".agents") / "skills" / skill_name / "SKILL.md"
        source_rel = source_by_target.get(target_rel)
        if source_rel is None:
            raise RuntimeError(f"Missing asset file: install_root/{target_rel.as_posix()}")
        src_skill = assets_dir / source_rel
        if not src_skill.is_file():
            raise RuntimeError(f"Missing asset file: {source_rel.as_posix()}")

    return _ManagedSkillInstallPlan(
        current_file_mappings=current_file_mappings,
        bootstrap_only_rel_paths=(),
        obsolete_exact_rel_paths=(),
    )


def _preflight_target_path_conflicts(
    target_root: Path,
    *,
    current_target_rel_paths: tuple[Path, ...],
    obsolete_target_rel_paths: tuple[Path, ...],
    bootstrap_only_target_rel_paths: tuple[Path, ...] = (),
) -> None:
    bootstrap_only_target_rel_path_set = set(bootstrap_only_target_rel_paths)

    def _assert_exact_file_path_safe(
        target_rel: Path,
        *,
        path_kind: str,
        reject_exact_symlink: bool,
        allow_exact_file_symlink: bool = False,
    ) -> None:
        target_path = target_root / target_rel
        rel_posix = target_rel.as_posix()

        for parent in target_path.parents:
            if parent == target_root:
                break
            if parent.is_symlink():
                parent_rel = parent.relative_to(target_root).as_posix()
                raise RuntimeError(
                    "target directory/container conflict for "
                    f"{path_kind} '{rel_posix}' (symlink container: '{parent_rel}')"
                )
            if parent.exists() and not parent.is_dir():
                parent_rel = parent.relative_to(target_root).as_posix()
                raise RuntimeError(
                    "target directory/container conflict for "
                    f"{path_kind} '{rel_posix}' (non-directory container: '{parent_rel}')"
                )

        if target_path.is_symlink():
            if reject_exact_symlink:
                if allow_exact_file_symlink and target_path.exists() and target_path.is_file():
                    return
                raise RuntimeError(
                    f"target directory/container conflict for {path_kind} '{rel_posix}' (symlink at exact file path)"
                )
            return

        if target_path.exists() and target_path.is_dir():
            raise RuntimeError(
                "target directory/container conflict for "
                f"{path_kind} '{rel_posix}' (existing directory at exact file path)"
            )

    for current_rel in current_target_rel_paths:
        _assert_exact_file_path_safe(
            current_rel,
            path_kind="current managed path",
            reject_exact_symlink=True,
            allow_exact_file_symlink=current_rel in bootstrap_only_target_rel_path_set,
        )
    for obsolete_rel in obsolete_target_rel_paths:
        _assert_exact_file_path_safe(
            obsolete_rel,
            path_kind="obsolete managed path",
            reject_exact_symlink=False,
        )


def _preflight_managed_skill_install_plan(target_root: Path | None = None) -> _ManagedSkillInstallPlan:
    with _assets_dir() as assets_dir:
        plan = _build_managed_skill_install_plan(assets_dir)
        if target_root is not None:
            current_target_rel_paths = tuple(
                sorted(
                    {mapping.target_rel for mapping in plan.current_file_mappings},
                    key=lambda path: path.as_posix(),
                )
            )
            obsolete_target_rel_paths = tuple(
                sorted(
                    set(plan.obsolete_exact_rel_paths),
                    key=lambda path: path.as_posix(),
                )
            )
            _preflight_target_path_conflicts(
                target_root,
                current_target_rel_paths=current_target_rel_paths,
                obsolete_target_rel_paths=obsolete_target_rel_paths,
                bootstrap_only_target_rel_paths=plan.bootstrap_only_rel_paths,
            )
            _preflight_collision_aware_additive_skill_assets(
                target_root,
                assets_dir=assets_dir,
                mappings=plan.current_file_mappings,
            )

    return plan


def _apply_managed_skill_install_plan(
    target_root: Path,
    *,
    assets_dir: Path,
    plan: _ManagedSkillInstallPlan,
) -> None:
    current_sync_plan: list[tuple[Path, Path, Path]] = []
    bootstrap_only_target_rel_paths = set(plan.bootstrap_only_rel_paths)
    current_target_rel_paths = tuple(
        sorted(
            {mapping.target_rel for mapping in plan.current_file_mappings},
            key=lambda path: path.as_posix(),
        )
    )
    obsolete_target_rel_paths = tuple(
        sorted(
            set(plan.obsolete_exact_rel_paths),
            key=lambda path: path.as_posix(),
        )
    )

    _preflight_target_path_conflicts(
        target_root,
        current_target_rel_paths=current_target_rel_paths,
        obsolete_target_rel_paths=obsolete_target_rel_paths,
        bootstrap_only_target_rel_paths=plan.bootstrap_only_rel_paths,
    )
    _preflight_collision_aware_additive_skill_assets(
        target_root,
        assets_dir=assets_dir,
        mappings=plan.current_file_mappings,
    )

    for mapping in plan.current_file_mappings:
        source_path = assets_dir / mapping.source_asset_rel
        if not source_path.is_file():
            raise RuntimeError(f"Missing asset file: {mapping.source_asset_rel.as_posix()}")
        target_path = target_root / mapping.target_rel
        current_sync_plan.append((mapping.target_rel, source_path, target_path))

    for target_rel, source_path, target_path in current_sync_plan:
        if _is_collision_aware_additive_skill_path(target_rel):
            _materialize_collision_aware_additive_skill_asset(
                source_path=source_path,
                target_root=target_root,
                target_rel=target_rel,
            )
            continue
        if target_rel in bootstrap_only_target_rel_paths and target_path.exists():
            if target_path.is_file():
                _migrate_bootstrap_only_config_if_stale(target_rel, target_path)
                continue
            raise RuntimeError(
                "target directory/container conflict for current managed path "
                f"'{target_rel.as_posix()}' (non-file entry at exact file path)"
            )
        _copy_file(source_path, target_path)

    missing_current_targets: list[str] = []
    for target_rel, source_path, target_path in current_sync_plan:
        if _is_collision_aware_additive_skill_path(target_rel):
            _verify_existing_additive_skill_asset(
                source_bytes=source_path.read_bytes(),
                target_root=target_root,
                target_rel=target_rel,
            )
        elif not target_path.is_file():
            missing_current_targets.append(target_rel.as_posix())
    if missing_current_targets:
        joined = ", ".join(sorted(missing_current_targets))
        raise RuntimeError(f"managed current sync incomplete (missing target): {joined}")

    current_target_rel_path_set = {target_rel for target_rel, _src, _dest in current_sync_plan}
    protected_current_parent_dirs: set[Path] = set()
    for current_target_rel in current_target_rel_path_set:
        protected_current_parent_dirs.update(_parent_dirs_for(current_target_rel))
    for obsolete_rel in obsolete_target_rel_paths:
        if obsolete_rel in current_target_rel_path_set:
            continue
        obsolete_path = target_root / obsolete_rel
        if not obsolete_path.exists() and not obsolete_path.is_symlink():
            continue
        if obsolete_path.is_symlink() or obsolete_path.is_file():
            obsolete_path.unlink(missing_ok=True)
            _prune_empty_obsolete_parent_dirs(
                target_root,
                obsolete_rel,
                protected_rel_dirs=protected_current_parent_dirs,
            )
            continue
        if obsolete_path.is_dir():
            raise RuntimeError(
                "target directory/container conflict for obsolete managed path "
                f"'{obsolete_rel.as_posix()}' (existing directory at exact file path)"
            )
        raise RuntimeError(
            "target directory/container conflict for obsolete managed path "
            f"'{obsolete_rel.as_posix()}' (non-file entry at exact file path)"
        )


def _migrate_bootstrap_only_config_if_stale(target_rel: Path, target_path: Path) -> None:
    if target_rel.as_posix() != ".codex/config.toml":
        return
    if target_path.is_symlink():
        return
    try:
        target_text = target_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    migrated_text = target_text
    replacements = (
        (
            "PR 作成後の checks / statuses / Codex review 監視は pr-monitor",
            "PR 作成後の checks / statuses / Codex review 監視は "
            "`github-pr-observation` skill の "
            "`./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` direct invocation",
        ),
    )
    for old, new in replacements:
        migrated_text = migrated_text.replace(old, new)
    if migrated_text != target_text:
        target_path.write_text(migrated_text, encoding="utf-8")


def _install_skill(target_root: Path, *, plan: _ManagedSkillInstallPlan | None = None) -> None:
    """Install/update managed agent skills and host-native shims.

    Notes:
    - Codex CLI discovers repository skills by scanning for `.agents/skills/`.
    - Other agents may adopt the same convention (Agent Skills open standard).
    """
    with _assets_dir() as assets_dir:
        install_plan = plan if plan is not None else _build_managed_skill_install_plan(assets_dir)
        _apply_managed_skill_install_plan(
            target_root,
            assets_dir=assets_dir,
            plan=install_plan,
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
                if admission.status == "retry":
                    _install_recognized_distribution(target_root, operation="fresh", retry_marker=admission)
                elif os.path.lexists(_specdock_dir(target_root)):
                    raise RuntimeError("'spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'.")
                else:
                    _install_fresh_distribution(target_root)
            else:
                if admission.status == "fresh":
                    _install_fresh_distribution(target_root)
                else:
                    _install_recognized_distribution(target_root, operation="init-force", retry_marker=admission)
        elif ns.command == "update":
            admission = _admit_distribution_cli(target_root, operation="update")
            _install_recognized_distribution(target_root, operation="update", retry_marker=admission)
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
