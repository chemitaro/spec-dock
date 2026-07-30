import os
from pathlib import Path
import sys
import threading
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


def test_existing_artifacts_rules_creation_is_bound_to_opened_directory(
    tmp_path,
    monkeypatch,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    artifacts_dir = tmp_path / "spec-dock" / "artifacts"
    artifacts_dir.mkdir()
    displaced_artifacts = tmp_path / "displaced-artifacts"
    publisher_calls = 0
    original_symlink = os.symlink

    def replace_visible_artifacts_before_rules_create(
        source_value,
        destination_value,
        target_is_directory=False,
        *,
        dir_fd=None,
    ):
        if Path(destination_value).name == "rules.md":
            artifacts_dir.rename(displaced_artifacts)
            artifacts_dir.mkdir()
        return original_symlink(
            source_value,
            destination_value,
            target_is_directory=target_is_directory,
            dir_fd=dir_fd,
        )

    class _UnexpectedPublisher:
        def publish_explicit_file(self, _request):
            nonlocal publisher_calls
            publisher_calls += 1
            raise AssertionError("publisher must not run after artifacts replacement")

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_artifact_publisher": _UnexpectedPublisher(),
    })
    monkeypatch.setattr(os, "symlink", replace_visible_artifacts_before_rules_create)
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "artifact_setup_failed"
    assert captured.value.publication_state == "not_committed"
    assert publisher_calls == 0
    assert not os.path.lexists(artifacts_dir / "rules.md")
    assert not os.path.lexists(displaced_artifacts / "rules.md")
    assert source.read_bytes() == b"source"


def test_undecodable_source_basename_is_content_free_stable_failure(tmp_path) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    close_calls = 0

    class _Lease:
        source_visibility = "basename_only"
        source_display = "must-not-be-rendered"

        def close(self):
            nonlocal close_calls
            close_calls += 1

    class _Guard:
        def guard_explicit_file_source(self, _request):
            return _Lease()

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_source_guard": _Guard(),
    })
    undecodable = os.fsdecode(b"invalid-\xff.bin")

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path(undecodable),
            ),
            configured,
        )

    assert captured.value.code == "artifact_allocation_failed"
    assert captured.value.committed is False
    assert captured.value.publication_state == "not_committed"
    assert captured.value.cleanup_state == "not_created"
    assert captured.value.retry_disposition == "safe_after_remediation"
    assert "private body sentinel" not in str(captured.value)
    assert not (tmp_path / "spec-dock" / "artifacts").exists()
    assert close_calls == 1


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
            "_create_bound_fresh_artifacts_setup",
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


def test_noncooperative_destination_race_rescans_and_preserves_cleanup_state(
    tmp_path,
    monkeypatch,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"new body")
    configured = _ports(tmp_path)
    close_calls = 0

    class _Lease:
        source_visibility = "repo_relative"
        source_display = "source.bin"

        def close(self):
            nonlocal close_calls
            close_calls += 1

    lease = _Lease()

    class _Guard:
        def guard_explicit_file_source(self, _request):
            return lease

    class _RacingPublisher:
        calls = 0

        def publish_explicit_file(self, request):
            self.calls += 1
            request.destination_path.parent.mkdir(parents=True, exist_ok=True)
            if self.calls == 1:
                request.destination_path.write_bytes(b"noncooperative sentinel")
                raise contracts.BinaryArtifactPublishError(
                    code="destination_exists",
                    cleanup_state="retained",
                )
            request.destination_path.write_bytes(b"new body")
            return contracts.ExplicitFileArtifactPublishResult(
                source_visibility="repo_relative",
                source_display="source.bin",
                destination_path=request.destination_path,
                committed=True,
                cleanup_state="removed",
            )

    publisher = _RacingPublisher()
    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_source_guard": _Guard(),
        "explicit_file_artifact_publisher": publisher,
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

    artifacts_dir = tmp_path / "spec-dock" / "artifacts"
    assert (artifacts_dir / "20260730t010203z--source.bin").read_bytes() == b"noncooperative sentinel"
    assert (artifacts_dir / "20260730t010203z-01--source.bin").read_bytes() == b"new body"
    assert result.artifact_id == "20260730t010203z-01--source.bin"
    assert result.cleanup_state == "retained"
    assert result.publication_state == "committed_with_warning"
    assert result.warning_codes == ("temp_cleanup_retained",)
    assert close_calls == 1


def test_cooperative_same_timestamp_imports_receive_distinct_slots(tmp_path) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    sources = []
    for index in range(3):
        source = tmp_path / f"source-{index}.bin"
        source.write_bytes(f"payload-{index}".encode())
        sources.append(source)
    barrier = threading.Barrier(len(sources))
    results = []
    errors = []

    def run(source: Path) -> None:
        try:
            barrier.wait(timeout=5)
            results.append(
                module.import_file_artifact(
                    contracts.FileArtifactImportRequest(
                        target_kind="root",
                        target_value=None,
                        source_path=source.relative_to(tmp_path),
                    ),
                    configured,
                )
            )
        except BaseException as error:
            errors.append(error)

    threads = [threading.Thread(target=run, args=(source,)) for source in sources]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors
    assert len(results) == len(sources)
    assert len({result.artifact_id.split("--", 1)[0] for result in results}) == len(sources)
    for result in results:
        source_name = result.artifact_id.split("--", 1)[1]
        assert (tmp_path / result.destination).read_bytes() == (tmp_path / source_name).read_bytes()


def test_shared_slot_exhaustion_is_not_committed_and_does_not_call_publisher(
    tmp_path,
    monkeypatch,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"source sentinel")
    artifacts_dir = tmp_path / "spec-dock" / "artifacts"
    artifacts_dir.mkdir()
    rules_source = tmp_path / "spec-dock" / "docs" / "rules" / "root" / "artifacts.md"
    (artifacts_dir / "rules.md").symlink_to(rules_source)
    timestamp = "20260730t010203z"
    (artifacts_dir / f"{timestamp}-adr-existing.md").write_bytes(b"standard")
    for suffix in range(1, 100):
        name = f"{timestamp}-{suffix:02d}-existing.md" if suffix % 2 else f"{timestamp}-{suffix:02d}--existing.bin"
        (artifacts_dir / name).write_bytes(str(suffix).encode())
    before = {
        path.name: (path.readlink() if path.is_symlink() else path.read_bytes()) for path in artifacts_dir.iterdir()
    }
    close_calls = 0

    class _Lease:
        source_visibility = "repo_relative"
        source_display = "source.bin"

        def close(self):
            nonlocal close_calls
            close_calls += 1

    class _Guard:
        def guard_explicit_file_source(self, _request):
            return _Lease()

    class _UnexpectedPublisher:
        def publish_explicit_file(self, _request):
            raise AssertionError("publisher must not run after slot exhaustion")

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_source_guard": _Guard(),
        "explicit_file_artifact_publisher": _UnexpectedPublisher(),
    })
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    after = {
        path.name: (path.readlink() if path.is_symlink() else path.read_bytes()) for path in artifacts_dir.iterdir()
    }
    assert captured.value.code == "artifact_slot_exhausted"
    assert captured.value.publication_state == "not_committed"
    assert captured.value.cleanup_state == "not_created"
    assert after == before
    assert source.read_bytes() == b"source sentinel"
    assert close_calls == 1


def test_noncooperative_race_exhaustion_keeps_retained_cleanup_and_closes_once(
    tmp_path,
    monkeypatch,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    close_calls = 0

    class _Lease:
        source_visibility = "repo_relative"
        source_display = "source.bin"

        def close(self):
            nonlocal close_calls
            close_calls += 1

    class _Guard:
        def guard_explicit_file_source(self, _request):
            return _Lease()

    class _AlwaysRacingPublisher:
        calls = 0

        def publish_explicit_file(self, request):
            self.calls += 1
            request.destination_path.write_bytes(f"sentinel-{self.calls}".encode())
            raise contracts.BinaryArtifactPublishError(
                code="destination_exists",
                cleanup_state="retained",
            )

    publisher = _AlwaysRacingPublisher()
    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_source_guard": _Guard(),
        "explicit_file_artifact_publisher": publisher,
    })
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "artifact_slot_exhausted"
    assert captured.value.cleanup_state == "retained"
    assert publisher.calls == 100
    assert close_calls == 1


@pytest.mark.parametrize("limits", [(OSError("unavailable"),), (255, 254)])
def test_fresh_target_name_max_failure_is_precommit_and_rolls_back_setup(
    tmp_path,
    monkeypatch,
    limits,
) -> None:
    contracts, module, _ports_module, _publisher_type = _runtime_modules()
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    configured = _ports(tmp_path)
    values = iter(limits)

    def name_max(_descriptor):
        value = next(values)
        if isinstance(value, BaseException):
            raise value
        return value

    monkeypatch.setattr(module, "_name_max_for_descriptor", name_max)
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.publication_state == "not_committed"
    assert captured.value.code in ("runtime_failed", "artifact_allocation_failed")
    assert not (tmp_path / "spec-dock" / "artifacts").exists()
    assert source.read_bytes() == b"source"


@pytest.mark.parametrize("replacement", ["target", "artifacts"])
def test_fresh_target_same_name_max_identity_replacement_fails_before_publisher(
    tmp_path,
    monkeypatch,
    replacement,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    specdock_dir = tmp_path / "spec-dock"
    displaced_specdock = tmp_path / "displaced-spec-dock"
    displaced_artifacts = tmp_path / "displaced-artifacts"
    original_create = module._create_bound_fresh_artifacts_setup
    publisher_calls = 0

    def replace_target_after_setup(**kwargs):
        opened = original_create(**kwargs)
        if replacement == "target":
            specdock_dir.rename(displaced_specdock)
            specdock_dir.mkdir()
            (specdock_dir / "artifacts").mkdir()
        else:
            (specdock_dir / "artifacts").rename(displaced_artifacts)
            (specdock_dir / "artifacts").mkdir()
        return opened

    class _UnexpectedPublisher:
        def publish_explicit_file(self, _request):
            nonlocal publisher_calls
            publisher_calls += 1
            raise AssertionError("publisher must not run for a replaced fresh target")

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_artifact_publisher": _UnexpectedPublisher(),
    })
    monkeypatch.setattr(module, "_create_bound_fresh_artifacts_setup", replace_target_after_setup)
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "artifact_setup_failed"
    assert captured.value.publication_state == "not_committed"
    assert publisher_calls == 0
    assert not list((specdock_dir / "artifacts").glob("*.bin"))
    displaced = displaced_specdock / "artifacts" if replacement == "target" else displaced_artifacts
    assert not list(displaced.glob("*.bin"))
    assert source.read_bytes() == b"source"


@pytest.mark.parametrize("race_point", ["during_create", "after_setup"])
@pytest.mark.parametrize("replacement_kind", ["wrong", "broken", "alternate"])
def test_fresh_rules_link_replacement_fails_closed_without_deleting_replacement(
    tmp_path,
    monkeypatch,
    race_point,
    replacement_kind,
) -> None:
    contracts, module, ports_module, _publisher_type = _runtime_modules()
    configured = _ports(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"source")
    artifacts_dir = tmp_path / "spec-dock" / "artifacts"
    rules_source = tmp_path / "spec-dock" / "docs" / "rules" / "root" / "artifacts.md"
    wrong_rules = tmp_path / "wrong-rules.md"
    if replacement_kind == "wrong":
        wrong_rules.write_text("# Wrong rules\n", encoding="utf-8")
    replacement_target = rules_source if replacement_kind == "alternate" else wrong_rules
    original_symlink = os.symlink
    original_create = module._create_bound_fresh_artifacts_setup
    publisher_calls = 0

    def replace_rules_link() -> None:
        rules_link = artifacts_dir / "rules.md"
        rules_link.unlink()
        original_symlink(replacement_target, rules_link)

    def replace_during_create(
        source_value,
        destination_value,
        target_is_directory=False,
        *,
        dir_fd=None,
    ):
        result = original_symlink(
            source_value,
            destination_value,
            target_is_directory=target_is_directory,
            dir_fd=dir_fd,
        )
        if Path(destination_value).name == "rules.md":
            replace_rules_link()
        return result

    def replace_after_setup(**kwargs):
        opened = original_create(**kwargs)
        replace_rules_link()
        return opened

    class _UnexpectedPublisher:
        def publish_explicit_file(self, _request):
            nonlocal publisher_calls
            publisher_calls += 1
            raise AssertionError("publisher must not run after rules.md replacement")

    configured = ports_module.Ports(**{
        **configured.__dict__,
        "explicit_file_artifact_publisher": _UnexpectedPublisher(),
    })
    if race_point == "during_create":
        monkeypatch.setattr(os, "symlink", replace_during_create)
    else:
        monkeypatch.setattr(module, "_create_bound_fresh_artifacts_setup", replace_after_setup)
    monkeypatch.setattr(module, "_acquire_create_lock", lambda _specdock_dir: (None, None))

    with pytest.raises(contracts.FileArtifactImportError) as captured:
        module.import_file_artifact(
            contracts.FileArtifactImportRequest(
                target_kind="root",
                target_value=None,
                source_path=Path("source.bin"),
            ),
            configured,
        )

    assert captured.value.code == "artifact_setup_failed"
    assert captured.value.publication_state == "not_committed"
    assert publisher_calls == 0
    assert (artifacts_dir / "rules.md").readlink() == replacement_target
    assert not list(artifacts_dir.glob("*.bin"))
    assert source.read_bytes() == b"source"
