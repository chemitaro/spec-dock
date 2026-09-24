"""Read installed tooling and all registered worktree versions without mutation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spec_dock_runtime.infra.control_store import load_control
from spec_dock_runtime.infra.git_cli import worktree_list


@dataclass(frozen=True)
class InstalledWorktree:
    id: str
    root: str
    version: str | None
    schema_version: int
    writer_protocol: str
    engine_digest: str
    active: bool


@dataclass(frozen=True)
class InstallationView:
    target: str
    engine_version: str
    engine_digest: str
    source_repository: str
    control_mode: str
    control_epoch: int
    worktrees: tuple[InstalledWorktree, ...]


@dataclass(frozen=True)
class InstallationGroup:
    common_dir: str
    control_epoch: int
    mode: str
    worktrees: tuple[InstalledWorktree, ...]


def _installed_version(root: Path) -> str | None:
    version_path = root / "spec-dock/spec-dock.version"
    if any(path.is_symlink() for path in (root, root / "spec-dock", version_path)):
        raise ValueError("installed version record is a symlink")
    try:
        value = version_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    if not value or "\n" in value or "\r" in value:
        raise ValueError("installed version record is invalid")
    return value


def show_installation(
    *, repo_root: Path, common_dir: Path, engine_version: str, engine_digest: str, target: Path | None = None
) -> InstallationView:
    """Report the fixed source and bound worktree installation inventory."""
    control = load_control(common_dir)
    if control is None:
        raise ValueError("repository worktree control is unavailable")
    requested = repo_root if target is None else target
    if not requested.is_absolute() or requested.is_symlink() or not requested.is_dir():
        raise ValueError("installation target is not a real directory")
    observed = requested.resolve(strict=True)
    roots = {Path(item.root).resolve(strict=False) for item in control.worktrees}
    if observed not in roots:
        raise ValueError("installation target is not registered in this repository")
    worktrees: list[InstalledWorktree] = []
    for item in control.worktrees:
        root = Path(item.root)
        version = _installed_version(root) if root.is_dir() and not root.is_symlink() else None
        worktrees.append(
            InstalledWorktree(
                item.id,
                item.root,
                version,
                item.schema_version,
                item.writer_protocol,
                item.engine_digest,
                item.active,
            )
        )
    return InstallationView(
        str(observed),
        engine_version,
        engine_digest,
        "chemitaro/spec-dock",
        control.mode,
        control.epoch,
        tuple(worktrees),
    )


def inspect_installation_group(*, repo_root: Path, common_dir: Path) -> InstallationGroup:
    """Fix a complete, registered Git worktree inventory before a shared update."""
    control = load_control(common_dir)
    if control is None or control.mode not in {"ready", "maintenance"}:
        raise ValueError("installation group requires ready or maintenance control")
    registered: dict[Path, InstalledWorktree] = {}
    for item in control.worktrees:
        if not item.active:
            continue
        root = Path(item.root)
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ValueError("registered installation worktree is unavailable")
        canonical = root.resolve(strict=True)
        if canonical != root or canonical in registered:
            raise ValueError("registered installation worktree identity changed")
        registered[canonical] = InstalledWorktree(
            item.id,
            item.root,
            _installed_version(root),
            item.schema_version,
            item.writer_protocol,
            item.engine_digest,
            True,
        )
    records = worktree_list(repo_root)
    observed: set[Path] = set()
    for record in records:
        if record.bare or record.path.is_symlink() or not record.path.is_dir():
            raise ValueError("Git worktree inventory contains an unavailable worktree")
        canonical = record.path.resolve(strict=True)
        if canonical not in registered or canonical in observed:
            raise ValueError("Git worktree inventory differs from registered installation targets")
        observed.add(canonical)
    if observed != set(registered) or repo_root.resolve(strict=True) not in observed:
        raise ValueError("installation group is incomplete")
    return InstallationGroup(
        str(common_dir),
        control.epoch,
        control.mode,
        tuple(sorted(registered.values(), key=lambda item: item.id)),
    )
