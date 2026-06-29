from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.domain.artifact_composer import (
    ArtifactKind,
    ProfileSectionManifest,
    load_profile_section_manifest,
)

if TYPE_CHECKING:
    from spec_dock_runtime.infra.assurance_store import ResolvedIssueTarget

ArtifactSelection = Literal["design", "plan", "report", "all"]

_ARTIFACT_KINDS: tuple[ArtifactKind, ...] = ("design", "plan", "report")


@dataclass(frozen=True)
class IssueArtifact:
    artifact: ArtifactKind
    path: Path
    repo_relative_path: str
    text: str


class ArtifactStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.specdock_dir = self.repo_root / "spec-dock"

    def artifact_kinds(self, selection: ArtifactSelection) -> tuple[ArtifactKind, ...]:
        if selection == "all":
            return _ARTIFACT_KINDS
        if selection not in _ARTIFACT_KINDS:
            raise ValueError(f"Unsupported artifact selection: {selection}")
        return (selection,)

    def read_artifact(self, target: ResolvedIssueTarget, artifact: ArtifactKind) -> IssueArtifact:
        path = target.issue_dir / f"{artifact}.md"
        if not path.is_file():
            raise FileNotFoundError(f"Planning artifact not found: {path}")
        self._validate_artifact_path(target, path)
        return IssueArtifact(
            artifact=artifact,
            path=path,
            repo_relative_path=path.relative_to(self.repo_root).as_posix(),
            text=path.read_text(encoding="utf-8"),
        )

    def write_artifact(self, artifact: IssueArtifact, text: str) -> None:
        self.ensure_artifact_writable(artifact)
        artifact.path.write_text(text, encoding="utf-8")

    def ensure_artifact_writable(self, artifact: IssueArtifact) -> None:
        if artifact.path.is_symlink():
            raise RuntimeError(f"Refusing to write symlinked planning artifact: {artifact.repo_relative_path}")
        if artifact.path.exists() and not artifact.path.is_file():
            raise RuntimeError(f"Refusing to write non-file planning artifact: {artifact.repo_relative_path}")
        resolved = artifact.path.resolve()
        if not _is_relative_to(resolved, self.repo_root):
            raise RuntimeError(f"Refusing to write artifact outside repository: {artifact.repo_relative_path}")

    def load_profile_section_manifest(self) -> ProfileSectionManifest:
        path = self.specdock_dir / "templates" / "assurance" / "profile-sections.json"
        return load_profile_section_manifest(path.read_text(encoding="utf-8"))

    def _validate_artifact_path(self, target: ResolvedIssueTarget, path: Path) -> None:
        if path.is_symlink():
            raise RuntimeError(f"Refusing to use symlinked planning artifact: {path.relative_to(self.repo_root)}")
        resolved = path.resolve()
        if not _is_relative_to(resolved, target.issue_dir.resolve()):
            raise RuntimeError(f"Planning artifact is outside target issue: {path.relative_to(self.repo_root)}")
        if not _is_relative_to(resolved, self.repo_root):
            raise RuntimeError(f"Planning artifact is outside repository: {path.relative_to(self.repo_root)}")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
