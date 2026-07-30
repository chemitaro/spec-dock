from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import contracts, import_file_artifact, ports
        from spec_dock_runtime.infra.binary_artifact_publisher import FilesystemBinaryArtifactPublisher
    finally:
        sys.path.pop(0)
    return contracts, import_file_artifact, ports, FilesystemBinaryArtifactPublisher


class _NodeReader:
    def load_node_records(self):
        return []


class _Clock:
    def now_iso(self) -> str:
        return "2026-07-30T01:02:03+00:00"

    def today(self) -> str:
        return "2026-07-30"


def _ports(tmp_path):
    _contracts, _module, ports, publisher_type = _runtime_modules()
    specdock_dir = tmp_path / "spec-dock"
    rules_source = specdock_dir / "docs" / "rules" / "root" / "artifacts.md"
    rules_source.parent.mkdir(parents=True)
    rules_source.write_text("# Root artifacts\n", encoding="utf-8")
    publisher = publisher_type()
    return ports.Ports(
        node_reader=_NodeReader(),
        repo_root=tmp_path,
        specdock_dir=specdock_dir,
        clock=_Clock(),
        explicit_file_source_guard=publisher,
        explicit_file_artifact_publisher=publisher,
    )


def test_root_import_commits_opaque_bytes_after_source_guard(tmp_path) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "evidence" / "Report FINAL.PDF"
    source.parent.mkdir()
    body = b"%PDF-\xff\x00opaque"
    source.write_bytes(body)

    result = module.import_file_artifact(
        contracts.FileArtifactImportRequest(
            target_kind="root",
            target_value=None,
            source_path=Path("evidence/Report FINAL.PDF"),
        ),
        _ports(tmp_path),
    )

    destination = tmp_path / result.destination
    assert result.artifact_id == "20260730t010203z--Report FINAL.PDF"
    assert result.target_kind == "root"
    assert result.target_id == "root"
    assert result.canonical is False
    assert source.read_bytes() == body
    assert destination.read_bytes() == body
    assert not (tmp_path / "spec-dock" / ".meta.json").exists()
    rules_link = tmp_path / "spec-dock" / "artifacts" / "rules.md"
    assert rules_link.is_symlink()
    assert rules_link.resolve() == tmp_path / "spec-dock" / "docs" / "rules" / "root" / "artifacts.md"


def test_source_guard_failure_precedes_root_artifact_setup(tmp_path) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("missing.bin"),
            ),
            configured,
        )

    assert captured.value.code == "source_ineligible"
    assert not (tmp_path / "spec-dock" / "artifacts").exists()


def test_unknown_source_guard_fault_is_precommit_runtime_failed_without_private_detail(
    tmp_path,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    specdock_dir = tmp_path / "spec-dock"
    rules_source = specdock_dir / "docs" / "rules" / "root" / "artifacts.md"
    rules_source.parent.mkdir(parents=True)
    rules_source.write_text("# Root artifacts\n", encoding="utf-8")

    class _FaultingGuard:
        def guard_explicit_file_source(self, _request):
            raise ValueError("private-parent body hash count sentinel")

    configured = ports_module.Ports(
        node_reader=_NodeReader(),
        repo_root=tmp_path,
        specdock_dir=specdock_dir,
        clock=_Clock(),
        explicit_file_source_guard=_FaultingGuard(),
        explicit_file_artifact_publisher=SimpleNamespace(),
    )

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "runtime_failed"
    assert captured.value.publication_state == "not_committed"
    assert captured.value.retry_disposition == "safe_after_remediation"
    assert "private-parent" not in str(captured.value)
    assert not (specdock_dir / "artifacts").exists()


@pytest.mark.parametrize(
    ("target_value", "nodes"),
    [
        ("999", {}),
        (
            "init-00301",
            {
                "init-00301": SimpleNamespace(
                    id="init-00301",
                    kind="initiative",
                    path=Path("must-not-be-used"),
                )
            },
        ),
    ],
)
def test_missing_or_kind_mismatched_target_precedes_source_guard_and_setup(
    tmp_path,
    monkeypatch,
    target_value,
    nodes,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()

    class _UnexpectedSourceGuard:
        calls = 0

        def guard_explicit_file_source(self, _request):
            self.calls += 1
            raise AssertionError("source guard must not run for an invalid target")

    source_guard = _UnexpectedSourceGuard()
    specdock_dir = tmp_path / "spec-dock"
    specdock_dir.mkdir()
    source = tmp_path / "source.bin"
    body = b"target rejection must precede source open"
    source.write_bytes(body)
    monkeypatch.setattr(module, "load_graph", lambda _ports, validate=False: SimpleNamespace(nodes_by_id=nodes))
    configured = ports_module.Ports(
        node_reader=_NodeReader(),
        repo_root=tmp_path,
        specdock_dir=specdock_dir,
        clock=_Clock(),
        explicit_file_source_guard=source_guard,
        explicit_file_artifact_publisher=SimpleNamespace(),
    )

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="issue",
                target_value=target_value,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "target_invalid"
    assert source_guard.calls == 0
    assert source.read_bytes() == body
    assert list(specdock_dir.rglob("artifacts")) == []
    assert list(specdock_dir.rglob("rules.md")) == []


def test_generic_markdown_filename_is_not_a_malformed_typed_candidate(tmp_path) -> None:
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain.artifacts import (
            is_malformed_artifact_candidate,
            parse_artifact_filename,
            parse_generic_imported_artifact_filename,
        )
    finally:
        sys.path.pop(0)

    path = tmp_path / "20260730t010203z--opaque.md"
    path.write_bytes(b"\xff\x00not semantic markdown")

    assert parse_generic_imported_artifact_filename(path.name) is not None
    assert parse_artifact_filename(path.name) is None
    assert is_malformed_artifact_candidate(path) is False


@pytest.mark.parametrize(
    ("warning_codes", "expected_state"),
    [
        ((), "committed"),
        (("directory_fsync_failed",), "committed_with_warning"),
        (("temp_cleanup_retained",), "committed_with_warning"),
    ],
)
def test_publication_warning_maps_to_committed_retry_not_needed(
    tmp_path, monkeypatch, warning_codes, expected_state
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"body")
    configured = _ports(tmp_path)

    class _Publisher:
        def publish_explicit_file(self, request):
            request.destination_path.parent.mkdir(parents=True, exist_ok=True)
            request.destination_path.write_bytes(b"body")
            return contracts.ExplicitFileArtifactPublishResult(
                source_visibility="repo_relative",
                source_display="source.bin",
                destination_path=request.destination_path,
                committed=True,
                cleanup_state="retained" if warning_codes else "removed",
                warning_codes=warning_codes,
            )

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_artifact_publisher": _Publisher(),
    })
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    result = module.import_file_artifact(
        contracts.FileArtifactImportRequest(
            target_kind="root",
            target_value=None,
            source_path=Path("source.bin"),
        ),
        configured,
    )

    assert result.publication_state == expected_state
    assert result.committed is True
    assert result.retry_disposition == "not_needed"
    assert result.warning_codes == warning_codes


def test_create_lock_release_fault_after_commit_is_warning_and_not_retryable(tmp_path, monkeypatch) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"body")
    configured = _ports(tmp_path)
    monkeypatch.setattr(
        module,
        "_release_create_lock",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("private sentinel")),
    )

    result = module.import_file_artifact(
        contracts.FileArtifactImportRequest(
            target_kind="root",
            target_value=None,
            source_path=Path("source.bin"),
        ),
        configured,
    )

    assert result.publication_state == "committed_with_warning"
    assert result.committed is True
    assert result.retry_disposition == "not_needed"
    assert result.warning_codes == ("create_lock_release_failed",)
    assert (tmp_path / result.destination).read_bytes() == b"body"


@pytest.mark.parametrize("fault_location", ["create_lock", "artifact_setup"])
def test_known_precommit_os_faults_are_runtime_failed_and_safe_to_retry(
    tmp_path,
    monkeypatch,
    fault_location,
) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"body")
    configured = _ports(tmp_path)
    if fault_location == "create_lock":
        monkeypatch.setattr(
            module,
            "_acquire_create_lock",
            lambda _specdock_dir: (_ for _ in ()).throw(OSError("private lock sentinel")),
        )
    else:
        monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    if fault_location == "artifact_setup":
        monkeypatch.setattr(
            module,
            "_ensure_artifacts_setup_for_target",
            lambda **_kwargs: (_ for _ in ()).throw(OSError("private setup sentinel")),
        )

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "runtime_failed"
    assert captured.value.committed is False
    assert captured.value.publication_state == "not_committed"
    assert captured.value.retry_disposition == "safe_after_remediation"
    assert "private" not in str(captured.value)
    assert not list((tmp_path / "spec-dock").glob("artifacts/*.bin"))


def test_result_destination_is_validated_before_publisher_commit(tmp_path, monkeypatch) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"body")
    configured = _ports(tmp_path)
    calls = 0

    class _UnexpectedPublisher:
        def publish_explicit_file(self, _request):
            nonlocal calls
            calls += 1
            raise AssertionError("publisher must not run after invalid public destination")

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "repo_root": tmp_path / "other-root",
        "explicit_file_artifact_publisher": _UnexpectedPublisher(),
    })
    monkeypatch.setattr(module, "_resolve_specdock_dir", lambda _ports: tmp_path / "spec-dock")

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=source,
            ),
            configured,
        )

    assert captured.value.code == "result_path_invalid"
    assert calls == 0
