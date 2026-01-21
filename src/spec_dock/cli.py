from __future__ import annotations

import argparse
import shutil
import sys
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator


@contextmanager
def _assets_dir() -> Iterator[Path]:
    assets = files("spec_dock") / "assets"
    with as_file(assets) as p:
        yield Path(p)


def _sync_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _install_spec_dock(
    target_root: Path,
    *,
    force: bool,
    reset_current: bool,
) -> None:
    specdock_dir = target_root / ".spec-dock"
    if specdock_dir.exists() and not force:
        raise RuntimeError(
            "'.spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'."
        )

    with _assets_dir() as assets_dir:
        src_spec_dock = assets_dir / "spec_dock"

        specdock_dir.mkdir(parents=True, exist_ok=True)

        for name in ("docs", "templates", "scripts"):
            src = src_spec_dock / name
            dest = specdock_dir / name
            if not src.exists():
                raise RuntimeError(f"Missing asset directory: {src}")
            _sync_tree(src, dest) if (dest.exists() or force) else shutil.copytree(src, dest)

        # Ensure empty directories exist.
        (specdock_dir / "completed").mkdir(parents=True, exist_ok=True)

        current_dir = specdock_dir / "current"
        if reset_current or not current_dir.exists():
            if current_dir.exists():
                shutil.rmtree(current_dir)
            shutil.copytree(specdock_dir / "templates", current_dir)


def _install_skill(target_root: Path, *, force: bool) -> None:
    with _assets_dir() as assets_dir:
        src_skill = assets_dir / "codex_skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        if not src_skill.exists():
            raise RuntimeError(f"Missing asset file: {src_skill}")

        dest_skill = (
            target_root / ".codex" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md"
        )
        if dest_skill.exists() and not force:
            print(
                f"spec-dock: skill already exists (skipped): {dest_skill} (use --force to overwrite)",
                file=sys.stderr,
            )
            return
        _copy_file(src_skill, dest_skill)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="spec-dock")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "path",
            nargs="?",
            default=".",
            help="Target project path (default: current directory)",
        )
        p.add_argument(
            "--reset-current",
            action="store_true",
            help="Reset '.spec-dock/current' from templates",
        )
        p.add_argument(
            "--no-skill",
            action="store_true",
            help="Do not install the Codex skill into '.codex/skills/'",
        )

    p_init = sub.add_parser("init", help="Scaffold .spec-dock into a project")
    add_common(p_init)
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite managed files if '.spec-dock' already exists",
    )

    p_update = sub.add_parser(
        "update",
        help="Update managed files (docs/templates/scripts/skill) in an existing project",
    )
    add_common(p_update)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    target_root = Path(ns.path).expanduser().resolve()
    if not target_root.exists() or not target_root.is_dir():
        print(f"error: target path is not a directory: {target_root}", file=sys.stderr)
        return 2

    try:
        if ns.command == "init":
            _install_spec_dock(target_root, force=bool(ns.force), reset_current=ns.reset_current)
            if not ns.no_skill:
                _install_skill(target_root, force=bool(ns.force))
        elif ns.command == "update":
            # Update is effectively a managed overwrite.
            _install_spec_dock(target_root, force=True, reset_current=ns.reset_current)
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
