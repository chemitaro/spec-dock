"""Infrastructure adapters needed by current Artifact mutations."""

from dataclasses import dataclass
from pathlib import Path

from spec_dock_runtime.application.ports import Ports
from spec_dock_runtime.infra import clock, fs_repo, template_scaffolder
from spec_dock_runtime.infra.binary_artifact_publisher import FilesystemBinaryArtifactPublisher


@dataclass(frozen=True)
class _NodeReader:
    specdock_dir: Path

    def load_node_records(self):
        return fs_repo.load_node_records(self.specdock_dir)


@dataclass(frozen=True)
class _TemplateScaffolder:
    def render_text(self, text: str, replacements: dict[str, str]) -> str:
        return template_scaffolder.render_text(text, replacements)

    def load_template_text(self, src_path: Path) -> str:
        return template_scaffolder.load_template_text(src_path)

    def copy_scaffolded_tree(self, src_dir: Path, dest_dir: Path, replacements: dict[str, str]):
        return template_scaffolder.copy_scaffolded_tree(src_dir, dest_dir, replacements)

    def copy_scaffolded_tree_at(self, src_dir: Path, dest_dir: Path, dest_dir_fd: int, replacements: dict[str, str]):
        return template_scaffolder.copy_scaffolded_tree_at(src_dir, dest_dir, dest_dir_fd, replacements)

    def write_text(self, dest_path: Path, text: str) -> None:
        template_scaffolder.write_text(dest_path, text)


@dataclass(frozen=True)
class _Clock:
    def now_iso(self) -> str:
        return clock.now_iso()

    def today(self) -> str:
        return clock.today()


def artifact_ports(repo_root: Path) -> Ports:
    specdock_dir = repo_root / "spec-dock"
    publisher = FilesystemBinaryArtifactPublisher()
    return Ports(
        node_reader=_NodeReader(specdock_dir),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        template_scaffolder=_TemplateScaffolder(),
        clock=_Clock(),
        explicit_file_source_guard=publisher,
        explicit_file_artifact_publisher=publisher,
    )
