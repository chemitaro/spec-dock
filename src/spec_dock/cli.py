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
from typing import Any, Iterator

from spec_dock import __version__

_SPEC_DOCK_DIRNAME = "spec-dock"
_LEGACY_SPEC_DOCK_DIRNAME = ".spec-dock"
_MANAGED_DIRS = ("docs", "templates", "scripts", "system")
_MANAGED_SKILL_NAMES = (
    "spec-driven-tdd-workflow",
    "spec-dock-initiative-planning",
    "spec-dock-epic-planning",
    "spec-dock-issue-execution",
    "spec-dock-adr-facilitation",
)
_LEGACY_MANAGED_SKILL_NAMES = ("spec-driven-tdd-workflow",)
_DEFAULT_SPEC_DOCK_GITIGNORE = (
    "# spec-dock runtime (generated)\n"
    "# v2 generated state for agents (SSOT + derived views)\n"
    ".agent/\n"
    "# legacy v2 name (kept ignored for safe upgrades)\n"
    ".work/\n"
    "active/\n"
)


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
                f"'{_SPEC_DOCK_DIRNAME}' not found, but legacy '{_LEGACY_SPEC_DOCK_DIRNAME}' exists. "
                f"Please rename it: mv {_LEGACY_SPEC_DOCK_DIRNAME} {_SPEC_DOCK_DIRNAME}"
            )
        raise RuntimeError(f"'{_SPEC_DOCK_DIRNAME}' not found. Run 'spec-dock init' first.")
    return specdock_dir


def _copy_file(src: Path, dest: Path) -> None:
    """Copy a file while creating parent directories."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _sync_tree(src: Path, dest: Path) -> None:
    """Replace `dest` directory with a full copy of `src`."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


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
    lines.append("- index: `spec-dock/.agent/index.json`")
    lines.append("- tree: `spec-dock/.agent/tree.json`")
    lines.append("")
    lines.append("## Read order")
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
    lines.append("- state (local): `./spec-dock/scripts/spec-dock sync`")
    lines.append("- state (github): `./spec-dock/scripts/spec-dock sync --github`")
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
    legacy_specdock_dir = target_root / _LEGACY_SPEC_DOCK_DIRNAME
    if legacy_specdock_dir.exists() and legacy_specdock_dir.is_dir() and not specdock_dir.exists():
        raise RuntimeError(
            f"legacy '{_LEGACY_SPEC_DOCK_DIRNAME}' exists. Please rename it before installing: "
            f"mv {_LEGACY_SPEC_DOCK_DIRNAME} {_SPEC_DOCK_DIRNAME}"
        )
    if specdock_dir.exists() and not force:
        raise RuntimeError(
            f"'{_SPEC_DOCK_DIRNAME}' already exists. Use 'spec-dock update' or re-run with '--force'."
        )

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"
        specdock_dir.mkdir(parents=True, exist_ok=True)

        # Managed directories are owned by the installer and can be replaced on update.
        # The actual spec tree (`spec-dock/initiatives/**`) must be persistent and is
        # never removed by this installer.
        for name in _MANAGED_DIRS:
            src = src_spec_dock / name
            dest = specdock_dir / name
            if not src.exists():
                raise RuntimeError(f"Missing asset directory: {src}")
            _sync_tree(src, dest) if (dest.exists() or force) else shutil.copytree(src, dest)

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


def _install_skill(target_root: Path) -> None:
    """Install/update managed agent skills into `.agents/skills/`.

    Notes:
    - Codex CLI discovers repository skills by scanning for `.agents/skills/`.
    - Other agents may adopt the same convention (Agent Skills open standard).
    """
    with _assets_dir() as assets_dir:
        skills_root = target_root / ".agents" / "skills"
        managed_skill_names = _managed_skill_names()

        # 1) Copy/update target managed skills.
        for skill_name in managed_skill_names:
            src_skill = assets_dir / "codex_skills" / skill_name / "SKILL.md"
            if not src_skill.exists():
                raise RuntimeError(f"Missing asset file: {src_skill}")

            dest_skill = skills_root / skill_name / "SKILL.md"
            _copy_file(src_skill, dest_skill)

        # 2) Verify target managed skills were all installed before pruning.
        missing_skills = [
            skill_name
            for skill_name in managed_skill_names
            if not (skills_root / skill_name / "SKILL.md").is_file()
        ]
        if missing_skills:
            joined = ", ".join(sorted(missing_skills))
            raise RuntimeError(f"managed skill sync incomplete (missing SKILL.md): {joined}")

        # 3) Prune obsolete managed skills only; preserve unknown custom dirs.
        managed_ownership = set(_managed_skill_ownership_names())
        target_managed = set(managed_skill_names)
        for skill_dir in skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name not in managed_ownership:
                continue
            if skill_dir.name in target_managed:
                continue
            shutil.rmtree(skill_dir, ignore_errors=True)


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

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Installer entrypoint. Returns a process exit code (0=success)."""
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    target_root = Path(getattr(ns, "path", ".")).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        print(f"error: target path is not a directory: {target_root}", file=sys.stderr)
        return 2

    try:
        if ns.command == "init":
            _install_spec_dock(target_root, force=bool(ns.force))
            _install_skill(target_root)
        elif ns.command == "update":
            _require_specdock(target_root)
            _install_spec_dock(target_root, force=True)
            _install_skill(target_root)
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
