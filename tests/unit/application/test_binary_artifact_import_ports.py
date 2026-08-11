from pathlib import Path
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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


def test_explicit_file_guard_and_publisher_use_separate_narrow_ports(tmp_path):
    contracts, ports, publisher_type = _runtime_modules()
    publisher = publisher_type()
    source = tmp_path / "opaque.bin"
    source.write_bytes(b"\x00\xffopaque")
    destination_dir = tmp_path / "spec-dock" / "artifacts"
    destination_dir.mkdir(parents=True)
    guarded = publisher.guard_explicit_file_source(
        contracts.ExplicitFileSourcePreflightRequest(
            repo_root=tmp_path,
            source_path=Path("opaque.bin"),
        )
    )
    wired = ports.Ports(
        node_reader=_NodeReader(),
        repo_root=tmp_path,
        explicit_file_source_guard=publisher,
        explicit_file_artifact_publisher=publisher,
    )

    try:
        result = wired.explicit_file_artifact_publisher.publish_explicit_file(
            contracts.ExplicitFileArtifactPublishRequest(
                repo_root=tmp_path,
                guarded_source=guarded,
                destination_path=destination_dir / "20260730t010203z--opaque.bin",
            )
        )
    finally:
        guarded.close()

    assert wired.explicit_file_source_guard is publisher
    assert result.committed is True
    assert result.source_visibility == "repo_relative"
    assert result.source_display == "opaque.bin"
    assert result.destination_path.read_bytes() == b"\x00\xffopaque"
    assert not hasattr(result, "destination_sha256")
    assert not hasattr(result, "destination_byte_count")


def test_explicit_source_lease_close_failure_is_no_throw_and_idempotent(tmp_path, monkeypatch):
    contracts, _ports, publisher_type = _runtime_modules()
    source = tmp_path / "opaque.bin"
    source.write_bytes(b"opaque")
    guarded = publisher_type().guard_explicit_file_source(
        contracts.ExplicitFileSourcePreflightRequest(
            repo_root=tmp_path,
            source_path=source,
        )
    )
    descriptor = guarded._descriptor
    original_close = contracts.os.close
    calls = 0

    def fail_selected_close(fd):
        nonlocal calls
        if fd == descriptor:
            calls += 1
            original_close(fd)
            raise OSError("close sentinel")
        return original_close(fd)

    monkeypatch.setattr(contracts.os, "close", fail_selected_close)

    guarded.close()
    guarded.close()

    assert calls == 1
    assert guarded._closed is True
    with pytest.raises(RuntimeError):
        guarded.__enter__()
