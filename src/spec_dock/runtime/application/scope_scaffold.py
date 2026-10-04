"""Scope template paths, replacements and guarded rule-link publication."""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pathlib import Path


def _scaffold_file_paths(template_dir: Path, dest_dir: Path) -> list[Path]:
    if not template_dir.exists() or not template_dir.is_dir():
        raise RuntimeError(f"Missing template directory: {template_dir}")
    files: list[Path] = []
    for src_path in sorted(template_dir.rglob("*"), key=lambda p: p.as_posix()):
        if src_path.is_file():
            files.append(dest_dir / src_path.relative_to(template_dir))
    return files


def _rules_source_paths(
    *,
    kind: Literal["initiative", "epic", "issue"],
    specdock_dir: Path,
) -> list[Path]:
    docs_rules_dir = specdock_dir / "docs" / "rules"
    if kind == "initiative":
        return [
            docs_rules_dir / "initiative" / "epics.md",
            docs_rules_dir / "initiative" / "artifacts.md",
        ]
    if kind == "epic":
        return [
            docs_rules_dir / "epic" / "issues.md",
            docs_rules_dir / "epic" / "artifacts.md",
        ]
    return [docs_rules_dir / "issue" / "artifacts.md"]


def _rules_scaffold_specs(
    *,
    kind: Literal["initiative", "epic", "issue"],
    dest_dir: Path,
    specdock_dir: Path,
) -> list[tuple[Path, Path]]:
    rules_source_paths = _rules_source_paths(kind=kind, specdock_dir=specdock_dir)
    if kind == "initiative":
        return [
            (dest_dir / "epics" / "rules.md", rules_source_paths[0]),
            (dest_dir / "artifacts" / "rules.md", rules_source_paths[1]),
        ]
    if kind == "epic":
        return [
            (dest_dir / "issues" / "rules.md", rules_source_paths[0]),
            (dest_dir / "artifacts" / "rules.md", rules_source_paths[1]),
        ]
    return [
        (dest_dir / "artifacts" / "rules.md", rules_source_paths[0]),
    ]


def _open_relative_directory_at(root_fd: int, parts: tuple[str, ...]) -> int:
    current_fd = os.dup(root_fd)
    try:
        for part in parts:
            with contextlib.suppress(FileExistsError):
                os.mkdir(part, dir_fd=current_fd)
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=current_fd,
            )
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except Exception:
        with contextlib.suppress(OSError):
            os.close(current_fd)
        raise


def _create_relative_symlink_at(
    node_fd: int,
    *,
    node_dir: Path,
    link_path: Path,
    target_path: Path,
) -> None:
    _validate_rules_symlink_preflight(link_path=link_path, target_path=target_path)
    relative_link_path = link_path.relative_to(node_dir)
    parent_fd = _open_relative_directory_at(node_fd, relative_link_path.parts[:-1])
    try:
        rel_target = os.path.relpath(target_path, start=link_path.parent)
        os.symlink(rel_target, relative_link_path.name, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _validate_parent_dir_preflight(parent_dir: Path) -> None:
    current = parent_dir
    while True:
        if os.path.lexists(current):
            if current.is_symlink():
                raise RuntimeError(f"Destination already exists: {current}")
            if not current.is_dir():
                raise RuntimeError(f"Destination already exists: {current}")
            return
        next_parent = current.parent
        if next_parent == current:
            return
        current = next_parent


def _validate_rules_symlink_preflight(*, link_path: Path, target_path: Path) -> None:
    if not target_path.exists() or not target_path.is_file():
        raise RuntimeError(f"Missing rules source: {target_path}")
    _validate_parent_dir_preflight(link_path.parent)
    if os.path.lexists(link_path):
        raise RuntimeError(f"Destination already exists: {link_path}")


def _precheck_pre_github_create_rules_sources(
    *,
    kind: Literal["initiative", "epic", "issue"],
    specdock_dir: Path,
) -> None:
    for target_path in _rules_source_paths(kind=kind, specdock_dir=specdock_dir):
        if not target_path.exists() or not target_path.is_file():
            raise RuntimeError(f"Missing rules source: {target_path}")


def _replacements(
    *,
    kind: Literal["initiative", "epic", "issue"],
    node_id: str,
    title: str,
    parent_id: str | None,
    initiative_id: str | None,
    github_issue_number: int | None,
    today: str,
) -> dict[str, str]:
    issue_ref = f"#{github_issue_number}" if github_issue_number is not None else ""
    common = {
        "<YOUR_NAME>": os.environ.get("USER", "<YOUR_NAME>"),
        "YYYY-MM-DD": today,
    }
    if kind == "initiative":
        return {
            "<INIT_ID>": node_id,
            "<INIT_TITLE>": title,
            "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
            **common,
        }
    if kind == "epic":
        assert parent_id is not None
        return {
            "<EPIC_ID>": node_id,
            "<EPIC_TITLE>": title,
            "<INIT_ID>": parent_id,
            "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
            **common,
        }
    assert parent_id is not None and initiative_id is not None
    return {
        "<ISS_ID>": node_id,
        "<ISS_TITLE>": title,
        "<FEATURE_ID>": node_id,
        "<FEATURE_NAME>": title,
        "<EPIC_ID>": parent_id,
        "<INIT_ID>": initiative_id,
        "<ISSUE_NUMBER_OR_URL>": issue_ref,
        "<GITHUB_ISSUE_NUMBER_OR_URL>": issue_ref,
        **common,
    }
