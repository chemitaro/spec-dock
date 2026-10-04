"""Read-only project admission without an engine pin, control or registry."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock.runtime.domain.writer_admission import require_workspace_write
from spec_dock.runtime.infra.git_process import run_git
from spec_dock.runtime.infra.identity import DirectoryIdentity
from spec_dock.runtime.infra.json_store import read_guarded_json

if TYPE_CHECKING:
    from spec_dock.runtime.domain.work_target import PhysicalIdentity

NEW_WRITER_PROTOCOL = "specdock.worktree-writer/v1"
OLD_WRITER_PROTOCOL = "specdock.writer/v1"


@dataclass(frozen=True)
class GitContext:
    root: Path
    common_dir: Path
    clone_identity: PhysicalIdentity
    worktree_identity: PhysicalIdentity
    head: str | None
    branch: str | None


@dataclass(frozen=True)
class ProjectContext(GitContext):
    workspace: dict[str, object]

    def require_writer(self) -> None:
        if self.workspace.get("writer_protocol") != NEW_WRITER_PROTOCOL:
            raise ValueError("workspace requires explicit migration to specdock.worktree-writer/v1")
        require_workspace_write(self.workspace)


def physical_identity(path: Path) -> PhysicalIdentity:
    with DirectoryIdentity(path) as opened:
        return opened.identity


def resolve_context(project: str | None, cwd: Path, *, timeout: float = 30) -> ProjectContext:
    root, common = _resolve_git_paths(project, cwd, timeout=timeout)
    workspace = read_workspace_declaration(root / "spec-dock/workspace.json")
    git = _read_git_context(root, common, timeout=timeout)
    return ProjectContext(
        git.root, git.common_dir, git.clone_identity, git.worktree_identity, git.head, git.branch, workspace
    )


def resolve_git_context(project: str | None, cwd: Path, *, timeout: float = 30) -> GitContext:
    """Admit read-only raw diagnosis without interpreting the workspace declaration."""
    root, common = _resolve_git_paths(project, cwd, timeout=timeout)
    return _read_git_context(root, common, timeout=timeout)


def _resolve_git_paths(project: str | None, cwd: Path, *, timeout: float) -> tuple[Path, Path]:
    candidate = Path(project).expanduser() if project else cwd
    if not candidate.is_absolute():
        candidate = cwd / candidate
    candidate = candidate.resolve(strict=True)
    root_text = _git(candidate, "rev-parse", "--show-toplevel", timeout=timeout)
    root = Path(root_text.removesuffix("\n")).resolve(strict=True)
    if project and candidate != root:
        raise ValueError("--project must name the exact Git worktree root")
    common_text = _git(root, "rev-parse", "--git-common-dir", timeout=timeout).removesuffix("\n")
    common_path = Path(common_text)
    common = (common_path if common_path.is_absolute() else root / common_path).resolve(strict=True)
    return root, common


def _read_git_context(root: Path, common: Path, *, timeout: float) -> GitContext:
    head = (
        _git(root, "rev-parse", "--verify", "--quiet", "HEAD", allow_missing=True, timeout=timeout).removesuffix("\n")
        or None
    )
    branch = (
        _git(root, "symbolic-ref", "--quiet", "--short", "HEAD", allow_missing=True, timeout=timeout).removesuffix("\n")
        or None
    )
    return GitContext(root, common, physical_identity(common), physical_identity(root), head, branch)


def read_workspace_declaration(path: Path) -> dict[str, object]:
    loaded = read_guarded_json(path)
    if loaded is None or not isinstance(loaded[0], dict):
        raise ValueError("workspace declaration is missing or invalid")
    workspace = loaded[0]
    if type(workspace.get("schema_version")) is not int or workspace.get("schema_version") != 3:
        raise ValueError("workspace requires known schema 3")
    if workspace.get("writer_protocol") not in (NEW_WRITER_PROTOCOL, OLD_WRITER_PROTOCOL):
        raise ValueError("workspace writer protocol is unknown")
    return workspace


def _git(root: Path, *args: str, allow_missing: bool = False, timeout: float = 30) -> str:
    return os.fsdecode(run_git(root, *args, missing_ok=allow_missing, timeout=timeout))
