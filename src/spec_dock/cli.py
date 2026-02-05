"""spec-dock installer CLI (uvx entrypoint).

This module is intentionally minimal:
- `spec-dock init` scaffolds `.spec-dock/` into a target repository
- `spec-dock update` refreshes managed assets (docs/templates/scripts/skill)

Day-to-day operations (creating nodes, switching active issue, syncing state, etc.)
are handled by the repo-local runtime script installed at:
  `.spec-dock/scripts/spec-dock`
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator

from spec_dock import __version__

_SPEC_DOCK_DIRNAME = ".spec-dock"
_MANAGED_DIRS = ("docs", "templates", "scripts")


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

    match = re.search(r'(?m)^version\\s*=\\s*"([^"]+)"\\s*$', text)
    return match.group(1) if match else __version__


def _specdock_dir(target_root: Path) -> Path:
    """Return the `.spec-dock/` path under the target root."""
    return target_root / _SPEC_DOCK_DIRNAME


def _require_specdock(target_root: Path) -> Path:
    """Ensure `.spec-dock/` exists under `target_root` and return it."""
    specdock_dir = _specdock_dir(target_root)
    if not specdock_dir.exists():
        raise RuntimeError("'.spec-dock' not found. Run 'spec-dock init' first.")
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


def _install_spec_dock(target_root: Path, *, force: bool) -> None:
    """Install/update `.spec-dock/` scaffold into the target repository."""
    specdock_dir = _specdock_dir(target_root)
    if specdock_dir.exists() and not force:
        raise RuntimeError("'.spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'.")

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"
        specdock_dir.mkdir(parents=True, exist_ok=True)

        # Managed directories are owned by the installer and can be replaced on update.
        # The actual spec tree (`.spec-dock/initiatives/**`) must be persistent and is
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

        # Spec tree root + generated directories.
        (specdock_dir / "initiatives").mkdir(parents=True, exist_ok=True)
        (specdock_dir / "active").mkdir(parents=True, exist_ok=True)
        (specdock_dir / ".work").mkdir(parents=True, exist_ok=True)

        # Ensure runtime script is executable (best-effort).
        runtime_script = specdock_dir / "scripts" / "spec-dock"
        if runtime_script.exists():
            _make_executable(runtime_script)

        (specdock_dir / "spec-dock.version").write_text(f"{_tool_version()}\n", encoding="utf-8")


def _install_skill(target_root: Path, *, force: bool) -> None:
    """Install/update the bundled Codex skill into `.codex/skills/`."""
    with _assets_dir() as assets_dir:
        src_skill = assets_dir / "codex_skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        if not src_skill.exists():
            raise RuntimeError(f"Missing asset file: {src_skill}")

        dest_skill = target_root / ".codex" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        if dest_skill.exists() and not force:
            print(
                f"spec-dock: skill already exists (skipped): {dest_skill} (use --force to overwrite)",
                file=sys.stderr,
            )
            return
        _copy_file(src_skill, dest_skill)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments (installer commands only)."""
    parser = argparse.ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_init_update_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
        p.add_argument("--no-skill", action="store_true", help="Do not install the Codex skill into '.codex/skills/'")

    p_init = sub.add_parser("init", help="Scaffold .spec-dock into a project")
    add_init_update_common(p_init)
    p_init.add_argument("--force", action="store_true", help="Overwrite managed files if '.spec-dock' already exists")

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
            if not ns.no_skill:
                _install_skill(target_root, force=bool(ns.force))
        elif ns.command == "update":
            _require_specdock(target_root)
            _install_spec_dock(target_root, force=True)
            if not ns.no_skill:
                _install_skill(target_root, force=True)
        else:
            raise RuntimeError(f"Unknown command: {ns.command}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"spec-dock: ok ({ns.command}) -> {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
