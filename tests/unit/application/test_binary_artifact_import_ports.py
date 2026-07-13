from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import contracts, ports
        from spec_dock_runtime.infra.binary_artifact_publisher import FilesystemBinaryArtifactPublisher
    finally:
        sys.path.pop(0)
    return contracts, ports, FilesystemBinaryArtifactPublisher


class _NodeReader:
    def load_node_records(self):
        return []


def test_binary_artifact_publisher_adapter_satisfies_narrow_application_ports(tmp_path):
    contracts, ports, publisher_type = _runtime_modules()
    publisher = publisher_type()

    source_request = contracts.WorkbenchSourceGuardRequest(
        repo_root=tmp_path,
        specdock_dir=tmp_path / "spec-dock",
        scope_directories=(),
        source_path=Path("spec-dock/.workbench/source.md"),
    )
    publish_request = contracts.BinaryArtifactPublishRequest(
        source=source_request,
        destination_path=tmp_path / "spec-dock" / "artifacts" / "result.md",
    )
    wired = ports.Ports(
        node_reader=_NodeReader(),
        repo_root=tmp_path,
        workbench_source_guard=publisher,
        binary_artifact_publisher=publisher,
    )

    assert publish_request.source is source_request
    assert wired.workbench_source_guard is publisher
    assert wired.binary_artifact_publisher is publisher

