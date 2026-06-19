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
import json
import os
import re
import shutil
import sys
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Iterator, NamedTuple

from spec_dock import __version__

_SPEC_DOCK_DIRNAME = "spec-dock"
_LEGACY_SPEC_DOCK_DIRNAME = ".spec-dock"
_MANAGED_DIRS = ("docs", "templates", "scripts", "system")
# Keep managed skill installation aligned with docs README entrypoints.
_MANAGED_SKILL_NAMES = (
    "spec-dock-hub",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-epic-execution",
    "spec-dock-issue-planning",
    "spec-dock-issue-execution",
    "spec-dock-clarification",
    "spec-dock-adr-facilitation",
    "spec-dock-codex-adapter",
    "spec-dock-copilot-adapter",
    "git-commit-conventional-ja",
    "github-pr-observation",
    "github-pr-creator",
    "github-pr-merge-preparer",
)
_LEGACY_MANAGED_SKILL_NAMES = (
    "spec-driven-tdd-workflow",
    "spec-dock-system-architect",
    "spec-dock-implementation-planner",
)
_DEFAULT_SPEC_DOCK_GITIGNORE = (
    "# spec-dock runtime (generated)\n"
    "# v2 generated state for agents (SSOT + derived views)\n"
    ".agent/\n"
    "# legacy v2 name (kept ignored for safe upgrades)\n"
    ".work/\n"
    "active/\n"
)
_MANAGED_NATIVE_SHIM_PREFIXES = (".codex/agents/", ".github/agents/")
_MANAGED_OBSOLETE_EXACT_PATH_PREFIXES = (
    ".agents/skills/",
    ".agents/host-adapters/",
    ".codex/agents/",
    ".github/agents/",
    ".github/workflows/",
)
_UNINSTALL_CLEANUP_BOUNDARY_ROOTS = (Path(".agents"), Path(".codex"), Path(".github"), Path("spec-dock"))
_UNINSTALL_RETRY_MARKER_REL = Path("spec-dock/.uninstall-retry.json")
_REQUIRED_MANAGED_NATIVE_SHIM_HOSTS = ("codex", "copilot")
_HOST_ADAPTER_META_ASSET_REL = Path("install_root") / ".agents" / "host-adapters" / "meta.json"
_REQUIRED_MANAGED_NATIVE_SHIM_OWNER = "spec-dock"
_REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_ENTRY_FILES = {
    "codex": Path(".agents/skills/spec-dock-codex-adapter/SKILL.md"),
    "copilot": Path(".agents/skills/spec-dock-copilot-adapter/SKILL.md"),
}
_REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_TARGET_FILES = {
    "codex": Path(".codex/agents/spec-manager.toml"),
    "copilot": Path(".github/agents/orchestrator.agent.md"),
}
_REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_DELEGATES_TO = {
    "codex": Path(".agents/skills/spec-dock-codex-adapter/SKILL.md"),
    "copilot": Path(".agents/skills/spec-dock-copilot-adapter/SKILL.md"),
}


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


def _is_generated_python_cache_path(path: Path) -> bool:
    return "__pycache__" in path.parts or path.name.endswith(".pyc")


def _ignore_generated_python_caches(_dir: str, names: list[str]) -> set[str]:
    return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}


def _sync_tree(src: Path, dest: Path) -> None:
    """Replace `dest` directory with a full copy of `src`."""
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

    repo_root = specdock_dir.parent.resolve()
    candidates: list[Path] = []

    if persisted_path is not None:
        candidate = Path(persisted_path)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        candidates.append(candidate)

    # Fallback: persisted path can be missing/corrupt; recover by id if possible.
    initiatives_root = specdock_dir / "initiatives"
    for meta_path in sorted(initiatives_root.rglob(".meta.json"), key=lambda p: p.as_posix()):
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
        resolved = candidate.resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
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
    repo_root = specdock_dir.parent.resolve()
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
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
        try:
            candidates.append(link.resolve())
        except OSError:
            pass

    if pathfile.is_file():
        try:
            rel_target = pathfile.read_text(encoding="utf-8").strip()
        except OSError:
            rel_target = ""
        if rel_target:
            candidates.append((active_dir / rel_target).resolve())

    placeholder_candidate: tuple[Path, str | None] | None = None
    for candidate in candidates:
        try:
            candidate.relative_to(repo_root)
        except ValueError:
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
            if link.is_symlink() and resolved_link_target != existing_target:
                force_rebuild = True
            elif link.exists() and not link.is_symlink() and resolved_link_target != existing_target:
                force_rebuild = True
            desired_target = existing_target
            if not force_rebuild:
                continue
        else:
            desired_target = _resolve_manifest_target_dir(
                specdock_dir,
                layer,
                expected_id=persisted_id,
                persisted_path=persisted_path,
            )
            if desired_target is None:
                desired_target = _resolve_persisted_path_dir(
                    specdock_dir,
                    layer=layer,
                    expected_id=persisted_id,
                    persisted_path=persisted_path,
                )
            if desired_target is None:
                desired_target = _active_placeholder_dir(specdock_dir, layer)

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
                    try:
                        shutil.rmtree(link)
                    except OSError:
                        pass
            if link.exists() or link.is_symlink():
                continue
            if pathfile.exists():
                try:
                    pathfile.unlink()
                except OSError:
                    pass
            if pathfile.exists():
                continue

        # If `.path` exists but does not resolve to a valid active entrypoint,
        # treat it as stale so recovery can rebuild from persisted state/placeholder.
        elif pathfile.exists():
            try:
                pathfile.unlink()
            except OSError:
                pass

        if link.exists() or link.is_symlink() or pathfile.exists():
            continue

        rel_target = os.path.relpath(desired_target, start=active_dir)
        try:
            os.symlink(rel_target, link)
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
        os.symlink(target, dest)
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

    # Defensive: node templates should not generate nested README.md files.
    # These can reappear if a local clone has stale `build/` artifacts that get packaged.
    for p in templates_dir.rglob("README.md"):
        if p == templates_dir / "README.md":
            continue
        p.unlink(missing_ok=True)

    # Legacy node templates used per-scope `adrs/` and `artifacts/`; prune them.
    for legacy_dir in ("adrs", "artifacts"):
        for d in sorted(templates_dir.rglob(legacy_dir), key=lambda x: len(str(x)), reverse=True):
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

    # v1 installed a workflow that moved `current/` -> `completed/` on issue close.
    legacy_workflow = specdock_dir.parent / ".github" / "workflows" / "spec-dock-close.yml"
    legacy_workflow.unlink(missing_ok=True)

    # v1 created root-level symlinks as shortcuts. v2 uses `spec-dock/active/`,
    # so these are always safe to remove when they are symlinks (never delete real dirs).
    for name in ("current-initiative", "current-epic", "current-issue"):
        p = specdock_dir / name
        if p.is_symlink():
            p.unlink(missing_ok=True)

    # v2 used a `.path` fallback briefly during development; prune if present.
    for name in ("current-initiative.path", "current-epic.path", "current-issue.path"):
        (specdock_dir / name).unlink(missing_ok=True)


def _install_spec_dock(target_root: Path, *, force: bool) -> None:
    """Install/update `spec-dock/` scaffold into the target repository."""
    specdock_dir = _specdock_dir(target_root)
    if specdock_dir.exists() and not force:
        raise RuntimeError(
            f"'{_SPEC_DOCK_DIRNAME}' already exists. Use 'spec-dock update' or re-run with '--force'."
        )

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"
        if not src_spec_dock.is_dir():
            raise RuntimeError(f"Missing asset directory: {src_spec_dock}")

        # Preflight all managed scaffold directories before any write.
        managed_scaffold_sync_plan: list[tuple[Path, Path]] = []
        for name in _MANAGED_DIRS:
            src = src_spec_dock / name
            if not src.exists():
                raise RuntimeError(f"Missing asset directory: {src}")
            if not src.is_dir():
                raise RuntimeError(f"Invalid asset directory: {src}")
            managed_scaffold_sync_plan.append((src, specdock_dir / name))

        specdock_dir.mkdir(parents=True, exist_ok=True)

        # Managed directories are owned by the installer and can be replaced on update.
        # The actual spec tree (`spec-dock/initiatives/**`) must be persistent and is
        # never removed by this installer.
        for src, dest in managed_scaffold_sync_plan:
            if dest.exists() or force:
                _sync_tree(src, dest)
            else:
                shutil.copytree(src, dest, ignore=_ignore_generated_python_caches)

        src_gitignore = src_spec_dock / ".gitignore"
        if src_gitignore.exists():
            _copy_file(src_gitignore, specdock_dir / ".gitignore")
        else:
            # Fallback: dotfiles may be missing in some packaged builds if glob patterns
            # exclude them. Keep `spec-dock/active/` and `spec-dock/.agent/` out of git.
            (specdock_dir / ".gitignore").write_text(_DEFAULT_SPEC_DOCK_GITIGNORE, encoding="utf-8")

        # Spec tree root + generated directories.
        (specdock_dir / "initiatives").mkdir(parents=True, exist_ok=True)
        (specdock_dir / "active").mkdir(parents=True, exist_ok=True)
        (specdock_dir / ".agent").mkdir(parents=True, exist_ok=True)

        _prune_legacy_scaffold(specdock_dir)

        # Ensure runtime script is executable (best-effort).
        runtime_script = specdock_dir / "scripts" / "spec-dock"
        if runtime_script.exists():
            _make_executable(runtime_script)

        # Best-effort: placeholders are not user-authored specs; discourage edits.
        _make_readonly_tree(specdock_dir / "system" / "active-none")

        # Ensure active fallback entrypoints exist before runtime `active clear/set`.
        _ensure_active_fallback_entrypoints(specdock_dir)

        (specdock_dir / "spec-dock.version").write_text(f"{_tool_version()}\n", encoding="utf-8")

        # Best-effort: provide `./spec` at repo root for convenience.
        _install_repo_root_shortcut(target_root)


def _managed_skill_names() -> tuple[str, ...]:
    """Return the managed bundled skill set."""
    return _MANAGED_SKILL_NAMES


def _managed_skill_ownership_names() -> tuple[str, ...]:
    """Return skill directory names owned by the installer for pruning decisions."""
    return tuple(dict.fromkeys((*_managed_skill_names(), *_LEGACY_MANAGED_SKILL_NAMES)))


def _is_within_managed_native_shim_prefixes(path: Path) -> bool:
    rel_posix = path.as_posix()
    return any(rel_posix.startswith(prefix) for prefix in _MANAGED_NATIVE_SHIM_PREFIXES)


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


class _UninstallAction(NamedTuple):
    rel_path: str
    category: str
    status: str
    reason: str
    error: str | None = None


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
            "target contains symlinked SpecDock uninstall retry marker: "
            f"{_UNINSTALL_RETRY_MARKER_REL.as_posix()}"
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
            "target contains symlinked SpecDock uninstall retry marker: "
            f"{_UNINSTALL_RETRY_MARKER_REL.as_posix()}"
        )


def _write_uninstall_retry_marker(target_root: Path) -> None:
    marker = target_root / _UNINSTALL_RETRY_MARKER_REL
    _reject_symlinked_uninstall_retry_marker(target_root)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(_uninstall_retry_marker_payload(), sort_keys=True) + "\n", encoding="utf-8")


def _symlinked_uninstall_boundary_root(target_root: Path) -> Path | None:
    for boundary_root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS:
        if (target_root / boundary_root).is_symlink():
            return boundary_root
    return None


def _path_exists_for_uninstall(path: Path) -> bool:
    return path.exists() or path.is_symlink()


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
    target_path = target_root / rel_path
    if not _path_exists_for_uninstall(target_path):
        if include_missing_removals:
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category=category,
                    status="would_remove",
                    reason="current shipped asset exact match",
                )
            )
        return

    is_match, preserve_reason = _compare_uninstall_bytes(target_path, expected)
    if is_match:
        actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category=category,
                status="would_remove",
                reason="current shipped asset exact match",
            )
        )
    else:
        actions.append(
            _UninstallAction(
                rel_path=rel_path.as_posix(),
                category=category,
                status="preserved",
                reason=preserve_reason or "manual review required",
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
    return tuple(sorted((path for path in root.rglob("*") if path.is_file() or path.is_symlink()), key=lambda p: p.as_posix()))


def _add_generated_state_uninstall_actions(
    actions: list[_UninstallAction],
    target_root: Path,
    known_rel_paths: set[Path],
) -> None:
    for rel_root in (Path("spec-dock/active"), Path("spec-dock/.agent")):
        for path in _iter_existing_files_or_symlinks(target_root / rel_root):
            rel_path = path.relative_to(target_root)
            known_rel_paths.add(rel_path)
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category="generated_state",
                    status="would_remove",
                    reason="SpecDock generated state",
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
        actions.append(
            _UninstallAction(
                rel_path=spec_history_path.as_posix(),
                category="spec_history",
                status="would_remove",
                reason="explicit remove-specs mode",
            )
        )
    else:
        reason = "keep-specs mode" if specs_mode == "keep" else "dry-run preserves specs unless remove-specs is explicit"
        actions.append(
            _UninstallAction(
                rel_path=spec_history_path.as_posix(),
                category="spec_history",
                status="preserved",
                reason=reason,
            )
        )


def _add_uninstall_retry_marker_action(actions: list[_UninstallAction], target_root: Path, known_rel_paths: set[Path]) -> None:
    known_rel_paths.add(_UNINSTALL_RETRY_MARKER_REL)
    if not _path_exists_for_uninstall(target_root / _UNINSTALL_RETRY_MARKER_REL):
        return
    actions.append(
        _UninstallAction(
            rel_path=_UNINSTALL_RETRY_MARKER_REL.as_posix(),
            category="generated_state",
            status="preserved",
            reason="SpecDock uninstall retry marker for idempotent rerun",
        )
    )


def _add_shortcut_uninstall_action(actions: list[_UninstallAction], target_root: Path) -> None:
    shortcut = target_root / "spec"
    if not _path_exists_for_uninstall(shortcut):
        return
    if shortcut.is_symlink() and os.readlink(shortcut) == f"{_SPEC_DOCK_DIRNAME}/scripts/spec-dock":
        actions.append(
            _UninstallAction(
                rel_path="spec",
                category="shortcut",
                status="would_remove",
                reason="repo-root shortcut targets spec-dock/scripts/spec-dock",
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
            raise RuntimeError(f"Missing asset directory: {src_root}")
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
    if src_gitignore.exists():
        gitignore_bytes = src_gitignore.read_bytes()
    else:
        gitignore_bytes = _DEFAULT_SPEC_DOCK_GITIGNORE.encode("utf-8")
    sources.append((Path("spec-dock/.gitignore"), gitignore_bytes))
    sources.append((Path("spec-dock/spec-dock.version"), f"{_tool_version()}\n".encode("utf-8")))
    return tuple(sources)


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
        install_plan = _build_managed_skill_install_plan(assets_dir)
        bootstrap_only_rel_paths = set(install_plan.bootstrap_only_rel_paths)
        for mapping in install_plan.current_file_mappings:
            rel_path = mapping.target_rel
            known_rel_paths.add(rel_path)
            target_path = target_root / rel_path
            if not _path_exists_for_uninstall(target_path):
                if include_missing_removals:
                    category = _uninstall_category_for_install_root_path(
                        rel_path,
                        bootstrap_only_rel_paths=bootstrap_only_rel_paths,
                    )
                    actions.append(
                        _UninstallAction(
                            rel_path=rel_path.as_posix(),
                            category=category,
                            status="would_remove",
                            reason=(
                                "known SpecDock-managed agent/skill asset"
                                if _is_delete_even_if_mismatch_uninstall_path(rel_path)
                                else "current shipped asset exact match"
                            ),
                        )
                    )
                continue
            category = _uninstall_category_for_install_root_path(
                rel_path,
                bootstrap_only_rel_paths=bootstrap_only_rel_paths,
            )
            if _is_delete_even_if_mismatch_uninstall_path(rel_path):
                actions.append(
                    _UninstallAction(
                        rel_path=rel_path.as_posix(),
                        category=category,
                        status="would_remove",
                        reason="known SpecDock-managed agent/skill asset",
                    )
                )
                continue
            _add_exact_match_uninstall_action(
                actions,
                target_root,
                rel_path,
                category=category,
                expected=(assets_dir / mapping.source_asset_rel).read_bytes(),
                include_missing_removals=include_missing_removals,
            )

        for rel_path in install_plan.obsolete_exact_rel_paths:
            known_rel_paths.add(rel_path)
            if not _path_exists_for_uninstall(target_root / rel_path):
                if include_missing_removals:
                    actions.append(
                        _UninstallAction(
                            rel_path=rel_path.as_posix(),
                            category="obsolete_managed",
                            status="would_remove",
                            reason="known obsolete SpecDock-managed asset",
                        )
                    )
                continue
            actions.append(
                _UninstallAction(
                    rel_path=rel_path.as_posix(),
                    category="obsolete_managed",
                    status="would_remove",
                    reason="known obsolete SpecDock-managed asset",
                )
            )

        for rel_path, expected in _build_scaffold_uninstall_sources(assets_dir):
            known_rel_paths.add(rel_path)
            if _is_delete_even_if_mismatch_uninstall_path(rel_path):
                if _path_exists_for_uninstall(target_root / rel_path) or include_missing_removals:
                    actions.append(
                        _UninstallAction(
                            rel_path=rel_path.as_posix(),
                            category="scaffold_managed",
                            status="would_remove",
                            reason="SpecDock managed state",
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
    return rel_path.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS} or rel_path == Path("spec")


def _has_symlink_uninstall_container(target_root: Path, rel_path: Path) -> bool:
    current = target_root
    last_index = len(rel_path.parts) - 1
    for index, part in enumerate(rel_path.parts):
        current = current / part
        if current.is_symlink():
            if index == last_index:
                return False
            return True
    return False


def _remove_uninstall_path(target_root: Path, action: _UninstallAction) -> _UninstallAction:
    rel_path = Path(action.rel_path)
    if not _is_safe_uninstall_rel_path(rel_path):
        return action._replace(status="failed", error="unsafe uninstall path outside managed boundaries")
    if _has_symlink_uninstall_container(target_root, rel_path):
        return action._replace(status="failed", error="unsafe uninstall path through symlink container")

    target_path = target_root / rel_path
    if not _path_exists_for_uninstall(target_path):
        return action._replace(status="already_removed", error=None)

    try:
        if target_path.is_dir() and not target_path.is_symlink():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
    except OSError as e:
        return action._replace(status="failed", error=str(e))
    return action._replace(status="removed", error=None)


def _is_uninstall_cleanup_boundary_path(rel_path: Path) -> bool:
    if rel_path.is_absolute() or ".." in rel_path.parts or rel_path.parts in {(), (".",)}:
        return False
    if rel_path.parts[0] == ".git":
        return False
    return rel_path.parts[0] in {root.parts[0] for root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS}


def _cleanup_empty_uninstall_dirs(target_root: Path) -> tuple[_UninstallAction, ...]:
    cleanup_actions: list[_UninstallAction] = []
    candidates: set[Path] = set()
    for boundary_root in _UNINSTALL_CLEANUP_BOUNDARY_ROOTS:
        root = target_root / boundary_root
        if not root.exists() or not root.is_dir() or root.is_symlink():
            continue
        candidates.add(boundary_root)
        for path in root.rglob("*"):
            if path.is_dir() and not path.is_symlink():
                candidates.add(path.relative_to(target_root))

    for rel_path in sorted(candidates, key=lambda path: len(path.parts), reverse=True):
        if not _is_uninstall_cleanup_boundary_path(rel_path):
            continue
        target_path = target_root / rel_path
        if not target_path.exists() or not target_path.is_dir() or target_path.is_symlink():
            continue
        try:
            target_path.rmdir()
        except OSError:
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


def _apply_uninstall_plan(target_root: Path, actions: tuple[_UninstallAction, ...]) -> tuple[_UninstallAction, ...]:
    results: list[_UninstallAction] = []
    for action in actions:
        if action.status == "would_remove":
            results.append(_remove_uninstall_path(target_root, action))
        else:
            results.append(action)
    results.extend(_cleanup_empty_uninstall_dirs(target_root))
    return tuple(sorted(results, key=lambda action: (action.rel_path, action.status)))


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
        lines.append(
            "  "
            f"[{action['status']}] {action['path']} "
            f"category={action['category']} reason={action['reason']}"
        )
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
            message=(
                "uninstall --apply requires exactly one specs mode: "
                "--keep-specs or --remove-specs"
            ),
        )

    try:
        if apply_requested:
            symlink_boundary = _symlinked_uninstall_boundary_root(target_root)
            if symlink_boundary is not None:
                return _emit_uninstall_preflight_error(
                    target_root,
                    apply=apply_requested,
                    specs_mode=specs_mode,
                    json_requested=json_requested,
                    message=(
                        "target contains symlinked SpecDock uninstall boundary root: "
                        f"{symlink_boundary.as_posix()}"
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
        if apply_requested:
            _write_uninstall_retry_marker(target_root)
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
        actions = _apply_uninstall_plan(target_root, actions)
    has_failures = any(action.status == "failed" for action in actions)
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
        raise RuntimeError(f"Missing asset directory: {install_root}")
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


def _build_obsolete_exact_rel_paths(
    *,
    manifest: dict[str, Any],
    host_adapter_meta_src: Path,
    current_target_paths: set[Path],
) -> tuple[Path, ...]:
    managed_assets = manifest.get("managed_assets")
    if not isinstance(managed_assets, dict):
        raise RuntimeError(f"invalid managed_assets contract: {host_adapter_meta_src}")

    obsolete_raw = managed_assets.get("obsolete_exact_file_paths")
    if not isinstance(obsolete_raw, list):
        raise RuntimeError(
            "invalid managed_assets.obsolete_exact_file_paths: "
            f"{host_adapter_meta_src}"
        )

    obsolete_rel_paths: list[Path] = []
    for obsolete in obsolete_raw:
        normalized_rel = _normalize_exact_file_path_from_manifest(
            obsolete,
            field_name="managed_assets.obsolete_exact_file_paths",
        )
        if not _is_within_managed_obsolete_exact_path_prefixes(normalized_rel):
            raise RuntimeError("invalid managed_assets.obsolete_exact_file_paths item")
        if normalized_rel in current_target_paths:
            raise RuntimeError(
                "managed_assets.obsolete_exact_file_paths overlaps current managed path "
                f"'{normalized_rel.as_posix()}'"
            )
        if any(_is_path_prefix(normalized_rel, current_path) for current_path in current_target_paths):
            raise RuntimeError(
                "invalid managed_assets.obsolete_exact_file_paths item "
                f"(must be exact file path): '{normalized_rel.as_posix()}'"
            )
        if any(normalized_rel == existing for existing in obsolete_rel_paths):
            raise RuntimeError(
                "duplicate managed_assets.obsolete_exact_file_paths item "
                f"'{normalized_rel.as_posix()}'"
            )
        for existing in obsolete_rel_paths:
            if _is_path_prefix(existing, normalized_rel) or _is_path_prefix(normalized_rel, existing):
                raise RuntimeError(
                    "overlapping managed_assets.obsolete_exact_file_paths items "
                    f"'{existing.as_posix()}' and '{normalized_rel.as_posix()}'"
                )
        obsolete_rel_paths.append(normalized_rel)

    return tuple(obsolete_rel_paths)


def _normalize_exact_file_path_from_manifest(value: object, *, field_name: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"invalid {field_name} item")
    value_norm = value.strip()
    value_rel = Path(value_norm)
    if re.match(r"^[A-Za-z]:", value_norm) or value_norm.startswith(("/", "\\")):
        raise RuntimeError(f"invalid {field_name} item")
    if "\\" in value_norm:
        raise RuntimeError(f"invalid {field_name} item")
    if value_rel.is_absolute() or ".." in value_rel.parts:
        raise RuntimeError(f"invalid {field_name} item")
    if value_norm.endswith("/"):
        raise RuntimeError(f"invalid {field_name} item (must be exact file path): '{value_norm}'")
    if any(token in value_norm for token in ("*", "?", "[", "]", "{", "}")):
        raise RuntimeError(f"invalid {field_name} item (must be exact file path): '{value_norm}'")

    normalized_parts = tuple(part for part in value_rel.parts if part not in ("", "."))
    if not normalized_parts:
        raise RuntimeError(f"invalid {field_name} item (must be exact file path): '{value_norm}'")
    normalized_rel = Path(*normalized_parts)
    if normalized_rel.as_posix() != value_norm:
        raise RuntimeError(f"invalid {field_name} item")
    if normalized_rel.suffix == "":
        raise RuntimeError(
            f"invalid {field_name} item (must be exact file path): '{normalized_rel.as_posix()}'"
        )
    return normalized_rel


def _build_bootstrap_only_rel_paths(
    *,
    manifest: dict[str, Any],
    host_adapter_meta_src: Path,
    current_target_paths: set[Path],
) -> tuple[Path, ...]:
    managed_assets = manifest.get("managed_assets")
    if not isinstance(managed_assets, dict):
        raise RuntimeError(f"invalid managed_assets contract: {host_adapter_meta_src}")

    bootstrap_raw = managed_assets.get("bootstrap_only_exact_file_paths")
    if not isinstance(bootstrap_raw, list):
        raise RuntimeError(
            "invalid managed_assets.bootstrap_only_exact_file_paths: "
            f"{host_adapter_meta_src}"
        )

    bootstrap_rel_paths: list[Path] = []
    for bootstrap in bootstrap_raw:
        normalized_rel = _normalize_exact_file_path_from_manifest(
            bootstrap,
            field_name="managed_assets.bootstrap_only_exact_file_paths",
        )
        if normalized_rel not in current_target_paths:
            raise RuntimeError(
                "managed_assets.bootstrap_only_exact_file_paths must reference current managed path "
                f"'{normalized_rel.as_posix()}'"
            )
        if any(normalized_rel == existing for existing in bootstrap_rel_paths):
            raise RuntimeError(
                "duplicate managed_assets.bootstrap_only_exact_file_paths item "
                f"'{normalized_rel.as_posix()}'"
            )
        for existing in bootstrap_rel_paths:
            if _is_path_prefix(existing, normalized_rel) or _is_path_prefix(normalized_rel, existing):
                raise RuntimeError(
                    "overlapping managed_assets.bootstrap_only_exact_file_paths items "
                    f"'{existing.as_posix()}' and '{normalized_rel.as_posix()}'"
                )
        bootstrap_rel_paths.append(normalized_rel)

    return tuple(bootstrap_rel_paths)


def _build_managed_skill_install_plan(assets_dir: Path) -> _ManagedSkillInstallPlan:
    managed_skill_names = _managed_skill_names()
    required_hosts = set(_REQUIRED_MANAGED_NATIVE_SHIM_HOSTS)
    current_file_mappings, source_by_target = _build_current_managed_file_mappings(assets_dir)
    current_target_paths = set(source_by_target.keys())

    for skill_name in managed_skill_names:
        target_rel = Path(".agents") / "skills" / skill_name / "SKILL.md"
        source_rel = source_by_target.get(target_rel)
        if source_rel is None:
            raise RuntimeError(f"Missing asset file: {assets_dir / 'install_root' / target_rel}")
        src_skill = assets_dir / source_rel
        if not src_skill.is_file():
            raise RuntimeError(f"Missing asset file: {src_skill}")

    host_adapter_meta_src = assets_dir / _HOST_ADAPTER_META_ASSET_REL
    if not host_adapter_meta_src.exists():
        raise RuntimeError(f"Missing asset file: {host_adapter_meta_src}")
    if host_adapter_meta_src.relative_to(assets_dir) not in {
        mapping.source_asset_rel for mapping in current_file_mappings
    }:
        raise RuntimeError(f"missing host adapter metadata from install_root inventory: {host_adapter_meta_src}")

    manifest = json.loads(host_adapter_meta_src.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise RuntimeError(f"invalid host adapter metadata shape: {host_adapter_meta_src}")
    targets = manifest.get("targets")
    if not isinstance(targets, dict):
        raise RuntimeError(f"invalid host adapter targets: {host_adapter_meta_src}")
    bootstrap_only_rel_paths = _build_bootstrap_only_rel_paths(
        manifest=manifest,
        host_adapter_meta_src=host_adapter_meta_src,
        current_target_paths=current_target_paths,
    )
    obsolete_exact_rel_paths = _build_obsolete_exact_rel_paths(
        manifest=manifest,
        host_adapter_meta_src=host_adapter_meta_src,
        current_target_paths=current_target_paths,
    )

    missing_required_hosts = sorted(required_hosts.difference(targets.keys()))
    if missing_required_hosts:
        joined = ", ".join(missing_required_hosts)
        raise RuntimeError(f"missing required managed native shim hosts: {joined}")

    native_target_file_owners: dict[Path, str] = {}
    for host_name, host_entry in targets.items():
        if not isinstance(host_entry, dict):
            raise RuntimeError(f"invalid host adapter target contract for host '{host_name}'")

        entry_file = host_entry.get("entry_file")
        if not isinstance(entry_file, str) or not entry_file.strip():
            raise RuntimeError(f"invalid host adapter entry_file for host '{host_name}'")
        entry_file_norm = entry_file.strip()
        entry_file_rel = Path(entry_file_norm)
        if re.match(r"^[A-Za-z]:", entry_file_norm) or entry_file_norm.startswith(("/", "\\")):
            raise RuntimeError(f"invalid host adapter entry_file path for host '{host_name}'")
        if entry_file_rel.is_absolute() or ".." in entry_file_rel.parts:
            raise RuntimeError(f"invalid host adapter entry_file path for host '{host_name}'")
        canonical_entry_file = _REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_ENTRY_FILES.get(host_name)
        if canonical_entry_file is not None and entry_file_rel != canonical_entry_file:
            raise RuntimeError(
                f"required host '{host_name}' must use canonical entry_file "
                f"'{canonical_entry_file.as_posix()}'"
            )

        native_shim = host_entry.get("native_shim")
        if host_name in required_hosts and native_shim is None:
            raise RuntimeError(f"missing required native_shim contract for host '{host_name}'")
        if native_shim is None:
            continue
        if not isinstance(native_shim, dict):
            raise RuntimeError(f"invalid native_shim contract for host '{host_name}'")
        managed_raw = native_shim.get("managed")
        if not isinstance(managed_raw, bool):
            raise RuntimeError(f"invalid native_shim.managed for host '{host_name}'")
        if host_name in required_hosts and not managed_raw:
            raise RuntimeError(f"required host '{host_name}' must define native_shim.managed=true")
        if not managed_raw:
            continue

        native_owner = native_shim.get("owner")
        if not isinstance(native_owner, str) or not native_owner.strip():
            raise RuntimeError(f"invalid native_shim.owner for host '{host_name}'")
        native_owner_norm = native_owner.strip()
        if host_name in required_hosts and native_owner_norm != _REQUIRED_MANAGED_NATIVE_SHIM_OWNER:
            raise RuntimeError(
                f"required host '{host_name}' must use native_shim.owner "
                f"'{_REQUIRED_MANAGED_NATIVE_SHIM_OWNER}'"
            )

        delegates_to = native_shim.get("delegates_to")
        if not isinstance(delegates_to, str) or not delegates_to.strip():
            raise RuntimeError(f"invalid native_shim.delegates_to for host '{host_name}'")
        delegates_to_norm = delegates_to.strip()
        delegates_to_rel = Path(delegates_to_norm)
        if re.match(r"^[A-Za-z]:", delegates_to_norm) or delegates_to_norm.startswith(("/", "\\")):
            raise RuntimeError(f"invalid native_shim.delegates_to path for host '{host_name}'")
        if delegates_to_rel.is_absolute() or ".." in delegates_to_rel.parts:
            raise RuntimeError(f"invalid native_shim.delegates_to path for host '{host_name}'")
        canonical_delegates_to = _REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_DELEGATES_TO.get(host_name)
        if canonical_delegates_to is not None and delegates_to_rel != canonical_delegates_to:
            raise RuntimeError(
                f"required host '{host_name}' must use canonical native_shim.delegates_to "
                f"'{canonical_delegates_to.as_posix()}'"
            )

        source_asset = native_shim.get("source_of_truth_asset")
        if not isinstance(source_asset, str) or not source_asset.strip():
            raise RuntimeError(f"invalid native_shim.source_of_truth_asset for host '{host_name}'")
        source_asset_norm = source_asset.strip()
        source_asset_rel = Path(source_asset_norm)
        if re.match(r"^[A-Za-z]:", source_asset_norm) or source_asset_norm.startswith(("/", "\\")):
            raise RuntimeError(f"invalid native_shim.source_of_truth_asset path for host '{host_name}'")
        if source_asset_rel.is_absolute() or ".." in source_asset_rel.parts:
            raise RuntimeError(f"invalid native_shim.source_of_truth_asset path for host '{host_name}'")
        if source_asset_rel.parts[:1] != ("install_root",):
            raise RuntimeError(f"invalid native_shim.source_of_truth_asset path for host '{host_name}'")
        source_path = assets_dir / source_asset_rel
        if not source_path.is_file():
            raise RuntimeError(f"Missing asset file: {source_path}")

        target_file = native_shim.get("target_file")
        if not isinstance(target_file, str) or not target_file.strip():
            raise RuntimeError(f"invalid native_shim.target_file for host '{host_name}'")
        target_norm = target_file.strip()
        target_rel = Path(target_norm)
        if re.match(r"^[A-Za-z]:", target_norm) or target_norm.startswith(("/", "\\")):
            raise RuntimeError(f"invalid native_shim.target_file path for host '{host_name}'")
        if target_rel.is_absolute() or ".." in target_rel.parts:
            raise RuntimeError(f"invalid native_shim.target_file path for host '{host_name}'")
        if not _is_within_managed_native_shim_prefixes(target_rel):
            raise RuntimeError(f"invalid native_shim.target_file path for host '{host_name}'")
        existing_owner = native_target_file_owners.get(target_rel)
        if existing_owner is not None and existing_owner != host_name:
            raise RuntimeError(
                "duplicate native_shim.target_file "
                f"'{target_rel.as_posix()}' for hosts '{existing_owner}' and '{host_name}'"
            )
        canonical_target = _REQUIRED_MANAGED_NATIVE_SHIM_CANONICAL_TARGET_FILES.get(host_name)
        if canonical_target is not None and target_rel != canonical_target:
            raise RuntimeError(
                f"required host '{host_name}' must use canonical native_shim.target_file "
                f"'{canonical_target.as_posix()}'"
            )
        native_target_file_owners[target_rel] = host_name

        inventory_source = source_by_target.get(target_rel)
        if inventory_source is None:
            raise RuntimeError(
                f"native_shim.target_file path for host '{host_name}' is not present in install_root inventory"
            )
        if inventory_source != source_asset_rel:
            raise RuntimeError(
                "native_shim.source_of_truth_asset does not match install_root inventory "
                f"for host '{host_name}'"
            )

    return _ManagedSkillInstallPlan(
        current_file_mappings=current_file_mappings,
        bootstrap_only_rel_paths=bootstrap_only_rel_paths,
        obsolete_exact_rel_paths=obsolete_exact_rel_paths,
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
                    "target directory/container conflict for "
                    f"{path_kind} '{rel_posix}' (symlink at exact file path)"
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

    for mapping in plan.current_file_mappings:
        source_path = assets_dir / mapping.source_asset_rel
        if not source_path.is_file():
            raise RuntimeError(f"Missing asset file: {source_path}")
        target_path = target_root / mapping.target_rel
        current_sync_plan.append((mapping.target_rel, source_path, target_path))

    for target_rel, source_path, target_path in current_sync_plan:
        if target_rel in bootstrap_only_target_rel_paths and target_path.exists():
            if target_path.is_file():
                _migrate_bootstrap_only_config_if_stale(target_rel, target_path)
                continue
            raise RuntimeError(
                "target directory/container conflict for current managed path "
                f"'{target_rel.as_posix()}' (non-file entry at exact file path)"
            )
        _copy_file(source_path, target_path)

    missing_current_targets = [
        target_rel.as_posix()
        for target_rel, _source_path, target_path in current_sync_plan
        if not target_path.is_file()
    ]
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

    p_update = sub.add_parser("update", help="Update managed files (docs/templates/scripts/skill) in an existing project")
    add_init_update_common(p_update)

    p_uninstall = sub.add_parser("uninstall", help="Plan or remove managed spec-dock artifacts from a project")
    p_uninstall.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    p_uninstall.add_argument("--apply", action="store_true", help="Apply the uninstall plan")
    specs_group = p_uninstall.add_mutually_exclusive_group()
    specs_group.add_argument("--keep-specs", action="store_true", help="Preserve spec history under spec-dock/initiatives")
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
            skill_install_plan = _preflight_managed_skill_install_plan(target_root)
            _install_spec_dock(target_root, force=bool(ns.force))
            _install_skill(target_root, plan=skill_install_plan)
        elif ns.command == "update":
            _require_specdock(target_root)
            skill_install_plan = _preflight_managed_skill_install_plan(target_root)
            _install_spec_dock(target_root, force=True)
            _install_skill(target_root, plan=skill_install_plan)
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
