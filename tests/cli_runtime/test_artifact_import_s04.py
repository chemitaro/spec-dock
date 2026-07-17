from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import tempfile
import threading

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import import_artifact
        from spec_dock_runtime.application.contracts import (
            ArtifactImportError,
            ArtifactImportRequest,
            CreateArtifactDocRequest,
        )
        from spec_dock_runtime.application.ports import Ports
        from spec_dock_runtime.cli import bootstrap
        from spec_dock_runtime.infra.binary_artifact_publisher import (
            FilesystemBinaryArtifactPublisher,
        )
    finally:
        sys.path.pop(0)
    return (
        import_artifact,
        ArtifactImportError,
        ArtifactImportRequest,
        CreateArtifactDocRequest,
        Ports,
        bootstrap,
        FilesystemBinaryArtifactPublisher,
    )


class _FixedClock:
    def now_iso(self) -> str:
        return "2026-07-14T01:02:03Z"

    def today(self) -> str:
        return "2026-07-14"


class TestArtifactImportS04(CliRuntimeHarness):
    def _prepare_target(self, target: Path) -> Path:
        assert main(["init", str(target)]) == 0
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=301,
            epic_issue_number=312,
            issue_issue_number=317,
            initiative_title="Architecture",
            epic_title="Workbench",
            issue_title="Raw import",
        )
        [issue_dir] = list((target / "spec-dock" / "initiatives").rglob("iss-00317-raw-import"))
        return issue_dir

    def _request(self, contracts, source: Path, *, slug: str = "collision"):
        return contracts(
            import_kind="chatgpt-output",
            scope_node_id="317",
            scope_kind="issue",
            source_path=source,
            title="Collision",
            slug=slug,
        )

    def _ports(self, target: Path, publisher, Ports, bootstrap):
        specdock_dir = target / "spec-dock"
        return Ports(
            node_reader=bootstrap._NodeReader(specdock_dir=specdock_dir),
            repo_root=target,
            specdock_dir=specdock_dir,
            clock=_FixedClock(),
            workbench_source_guard=publisher,
            binary_artifact_publisher=publisher,
        )

    @pytest.mark.parametrize("peer_kind", ["import", "new"])
    def test_tc317_s04_01_shared_lock_allocates_distinct_slots_without_deadlock(self, monkeypatch, peer_kind) -> None:
        (
            import_module,
            _ArtifactImportError,
            ArtifactImportRequest,
            CreateArtifactDocRequest,
            _Ports,
            bootstrap,
            _Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            workbench = target / "spec-dock" / ".workbench"
            workbench.mkdir(parents=True, exist_ok=True)
            source_a = workbench / "a.md"
            source_b = workbench / "b.md"
            source_a.write_bytes(b"import a")
            source_b.write_bytes(b"import b")
            sentinel = issue_dir / "artifacts" / "sentinel.md"
            sentinel.write_bytes(b"sentinel bytes")

            monkeypatch.setattr(bootstrap.infra_clock, "now_iso", _FixedClock().now_iso)
            context = bootstrap.build_runtime(target / "spec-dock", repo_root=target)
            barrier = threading.Barrier(2)
            original_import_acquire = import_module._acquire_create_lock

            def acquire_after_barrier(specdock_dir):
                barrier.wait(timeout=5)
                return original_import_acquire(specdock_dir)

            monkeypatch.setattr(import_module, "_acquire_create_lock", acquire_after_barrier)
            if peer_kind == "new":
                create_module = sys.modules["spec_dock_runtime.application.create_artifact_doc"]
                original_create_acquire = create_module._acquire_create_lock

                def create_acquire_after_barrier(specdock_dir):
                    barrier.wait(timeout=5)
                    return original_create_acquire(specdock_dir)

                monkeypatch.setattr(create_module, "_acquire_create_lock", create_acquire_after_barrier)

            import_a = ArtifactImportRequest(
                import_kind="chatgpt-output",
                scope_node_id="317",
                scope_kind="issue",
                source_path=source_a,
                title="Collision",
                slug="collision",
            )
            if peer_kind == "import":

                def peer():
                    return context.use_cases.import_artifact(replace(import_a, source_path=source_b))

            else:

                def peer():
                    return context.use_cases.create_artifact_doc(
                        CreateArtifactDocRequest(
                            artifact_type="blank",
                            scope_node_id="317",
                            scope_kind="issue",
                            title="Collision",
                            slug="chatgpt-output-collision",
                        )
                    )

            with ThreadPoolExecutor(max_workers=2) as executor:
                first = executor.submit(context.use_cases.import_artifact, import_a)
                second = executor.submit(peer)
                results = [first.result(timeout=10), second.result(timeout=10)]

            names = sorted(
                (result.destination_path.name if hasattr(result, "destination_path") else result.path.name)
                for result in results
            )
            assert names == [
                "20260714t010203z-01-chatgpt-output-collision.md",
                "20260714t010203z-chatgpt-output-collision.md",
            ]
            assert sentinel.read_bytes() == b"sentinel bytes"

    def test_tc317_s04_02_exact_path_eexist_rescans_then_uses_next_slot(self) -> None:
        (
            import_module,
            _ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"source bytes"
            source.write_bytes(source_body)
            collisions: list[Path] = []

            def external_writer(point):
                if point != "before_publication" or collisions:
                    return
                destination = issue_dir / "artifacts" / "20260714t010203z-chatgpt-output-collision.md"
                destination.write_bytes(b"external sentinel")
                collisions.append(destination)

            publisher = Publisher(fault_injector=external_writer)
            ports = self._ports(target, publisher, Ports, bootstrap)
            result = import_module.import_artifact(self._request(ArtifactImportRequest, source), ports)

            assert result.destination_path.name == ("20260714t010203z-01-chatgpt-output-collision.md")
            assert collisions[0].read_bytes() == b"external sentinel"
            assert (target / result.destination_path).read_bytes() == source_body
            assert source.read_bytes() == source_body

    def test_tc317_s04_02_retry_preserves_retained_owned_temp_state(self) -> None:
        (
            import_module,
            _ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(b"source bytes")
            first_attempt = True

            def retain_first_collision(point):
                nonlocal first_attempt
                if not first_attempt:
                    return
                if point == "before_publication":
                    destination = issue_dir / "artifacts" / "20260714t010203z-chatgpt-output-collision.md"
                    destination.write_bytes(b"external sentinel")
                elif point == "cleanup":
                    first_attempt = False
                    raise OSError("raw cleanup fault")

            publisher = Publisher(fault_injector=retain_first_collision)
            ports = self._ports(target, publisher, Ports, bootstrap)
            result = import_module.import_artifact(self._request(ArtifactImportRequest, source), ports)

            assert result.committed is True
            assert result.cleanup_state == "retained"
            assert result.warning_codes == ("temp_cleanup_retained",)
            assert len(list((issue_dir / "artifacts").glob(".spec-dock-import-*"))) == 1
            assert (
                issue_dir / "artifacts" / "20260714t010203z-chatgpt-output-collision.md"
            ).read_bytes() == b"external sentinel"

    def test_tc317_s04_02_retry_exhaustion_is_bounded_and_preserves_source(self) -> None:
        (
            import_module,
            ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"source bytes"
            source.write_bytes(source_body)
            attempts = 0
            source_guard = Publisher()

            class AlwaysCollidingPublisher:
                def guard_source(self, request):
                    return source_guard.guard_source(request)

                def publish(self, request):
                    nonlocal attempts
                    attempts += 1
                    raise sys.modules["spec_dock_runtime.application.contracts"].BinaryArtifactPublishError(
                        code="destination_exists", cleanup_state="removed"
                    )

            publisher = AlwaysCollidingPublisher()
            ports = self._ports(target, publisher, Ports, bootstrap)
            with pytest.raises(ArtifactImportError) as captured:
                import_module.import_artifact(self._request(ArtifactImportRequest, source), ports)

            assert captured.value.code == "artifact_publication_retry_exhausted"
            assert captured.value.committed is False
            assert captured.value.cleanup_state == "removed"
            assert attempts == 100
            assert source.read_bytes() == source_body

    def test_tc317_s04_02_suffix_exhaustion_does_not_publish_or_mutate(self) -> None:
        (
            import_module,
            ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"source bytes"
            source.write_bytes(source_body)
            artifacts_dir = issue_dir / "artifacts"
            occupied = {}
            for suffix in (None, *range(1, 100)):
                suffix_part = "" if suffix is None else f"-{suffix:02d}"
                path = artifacts_dir / (f"20260714t010203z{suffix_part}-chatgpt-output-collision.md")
                body = f"occupied {suffix}".encode()
                path.write_bytes(body)
                occupied[path] = body
            source_guard = Publisher()

            class UnexpectedPublisher:
                def guard_source(self, request):
                    return source_guard.guard_source(request)

                def publish(self, request):
                    raise AssertionError("publisher must not run after suffix exhaustion")

            publisher = UnexpectedPublisher()
            ports = self._ports(target, publisher, Ports, bootstrap)
            with pytest.raises(ArtifactImportError) as captured:
                import_module.import_artifact(self._request(ArtifactImportRequest, source), ports)

            assert captured.value.code == "artifact_allocation_failed"
            assert captured.value.committed is False
            assert captured.value.cleanup_state == "not_created"
            assert source.read_bytes() == source_body
            assert all(path.read_bytes() == body for path, body in occupied.items())

    @pytest.mark.parametrize("mutation", ["same-size", "replace", "unlink"])
    def test_tc317_s04_03_full_import_detects_source_change_before_publish(self, mutation) -> None:
        (
            import_module,
            ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            original = b"original bytes"
            source.write_bytes(original)
            displaced = source.with_name("displaced.md")

            def mutate_after_stage():
                if mutation == "same-size":
                    source.write_bytes(b"mutated! bytes")
                elif mutation == "replace":
                    source.rename(displaced)
                    source.write_bytes(original)
                else:
                    source.unlink()

            publisher = Publisher(stage_barrier=mutate_after_stage)
            ports = self._ports(target, publisher, Ports, bootstrap)
            with pytest.raises(ArtifactImportError) as captured:
                import_module.import_artifact(self._request(ArtifactImportRequest, source, slug=mutation), ports)

            assert captured.value.code == "source_changed"
            assert captured.value.committed is False
            assert captured.value.cleanup_state == "removed"
            assert not list((issue_dir / "artifacts").glob("*-chatgpt-output-" + mutation + ".md"))
            assert not list((issue_dir / "artifacts").glob(".spec-dock-import-*"))
            if mutation == "same-size":
                assert source.read_bytes() == b"mutated! bytes"
            elif mutation == "replace":
                assert source.read_bytes() == displaced.read_bytes() == original
            else:
                assert not source.exists()

    def test_tc317_s04_03_full_import_classifies_staged_hash_mismatch(self, monkeypatch) -> None:
        (
            import_module,
            ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"source bytes"
            source.write_bytes(source_body)
            publisher = Publisher()
            original_hash = publisher._hash_descriptor
            calls = 0

            def mismatch_first_hash(descriptor):
                nonlocal calls
                calls += 1
                digest, count = original_hash(descriptor)
                return ("0" * 64, count) if calls == 1 else (digest, count)

            monkeypatch.setattr(publisher, "_hash_descriptor", mismatch_first_hash)
            ports = self._ports(target, publisher, Ports, bootstrap)
            with pytest.raises(ArtifactImportError) as captured:
                import_module.import_artifact(
                    self._request(ArtifactImportRequest, source, slug="hash-mismatch"),
                    ports,
                )

            assert captured.value.code == "hash_mismatch"
            assert captured.value.committed is False
            assert captured.value.cleanup_state == "removed"
            assert source.read_bytes() == source_body
            assert not list((issue_dir / "artifacts").glob("*-chatgpt-output-hash-mismatch.md"))
            assert not list((issue_dir / "artifacts").glob(".spec-dock-import-*"))

    @pytest.mark.parametrize(
        ("fault", "expected_code", "expected_cleanup"),
        [
            ("temp_create", "temp_create_failed", "not_created"),
            ("write", "copy_failed", "removed"),
            ("hash", "hash_failed", "removed"),
            ("file_fsync", "file_fsync_failed", "removed"),
            ("publication_unsupported", "publication_unsupported", "removed"),
            ("write+cleanup", "copy_failed", "retained"),
        ],
    )
    def test_tc317_s04_03_full_import_prepublish_faults_are_uncommitted(
        self, fault, expected_code, expected_cleanup
    ) -> None:
        (
            import_module,
            ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"secret source bytes"
            source.write_bytes(source_body)
            before = sorted(path.name for path in (issue_dir / "artifacts").iterdir() if path.suffix == ".md")

            def inject(point):
                if point == fault or (fault == "write+cleanup" and point in {"write", "cleanup"}):
                    raise OSError("raw secret fault")

            publisher = Publisher(fault_injector=inject)
            ports = self._ports(target, publisher, Ports, bootstrap)
            with pytest.raises(ArtifactImportError) as captured:
                import_module.import_artifact(
                    self._request(
                        ArtifactImportRequest,
                        source,
                        slug=fault.replace("+", "-").replace("_", "-"),
                    ),
                    ports,
                )

            error = captured.value
            assert (error.code, error.committed, error.cleanup_state) == (
                expected_code,
                False,
                expected_cleanup,
            )
            assert "secret" not in str(error)
            assert source.read_bytes() == source_body
            formal = [path.name for path in (issue_dir / "artifacts").iterdir() if path.suffix == ".md"]
            assert sorted(formal) == before
            leftovers = list((issue_dir / "artifacts").glob(".spec-dock-import-*"))
            assert (len(leftovers) == 1) is (expected_cleanup == "retained")

    @pytest.mark.parametrize(
        ("fault", "warning", "cleanup"),
        [
            ("directory_fsync", "directory_fsync_failed", "removed"),
            ("cleanup", "temp_cleanup_retained", "retained"),
            ("post_confirmation", "destination_read_failed", "removed"),
        ],
    )
    def test_tc317_s04_04_postpublish_faults_return_committed_warning(self, fault, warning, cleanup) -> None:
        (
            import_module,
            _ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            body = b"post publish bytes"
            source.write_bytes(body)

            def inject(point):
                if point == fault:
                    raise OSError("raw secret fault")

            publisher = Publisher(fault_injector=inject)
            ports = self._ports(target, publisher, Ports, bootstrap)
            result = import_module.import_artifact(
                self._request(ArtifactImportRequest, source, slug=fault.replace("_", "-")),
                ports,
            )

            assert result.committed is True
            assert result.warning_codes == (warning,)
            assert result.cleanup_state == cleanup
            assert result.sha256 == hashlib.sha256(body).hexdigest()
            assert result.byte_count == len(body)
            assert (target / result.destination_path).read_bytes() == body
            assert source.read_bytes() == body

    def test_tc317_s04_04_lock_release_fault_preserves_committed_result(self, monkeypatch) -> None:
        (
            import_module,
            _ArtifactImportError,
            ArtifactImportRequest,
            _CreateArtifactDocRequest,
            Ports,
            bootstrap,
            Publisher,
        ) = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "source.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            body = b"release fault bytes"
            source.write_bytes(body)
            publisher = Publisher()
            ports = self._ports(target, publisher, Ports, bootstrap)

            def release_fault(*args, **kwargs):
                raise OSError("raw secret release fault")

            monkeypatch.setattr(import_module, "_release_create_lock", release_fault)
            result = import_module.import_artifact(self._request(ArtifactImportRequest, source, slug="release"), ports)

            assert result.committed is True
            assert result.warning_codes == ("create_lock_release_failed",)
            assert result.sha256 == hashlib.sha256(body).hexdigest()
            assert result.byte_count == len(body)
            assert (target / result.destination_path).read_bytes() == body
            assert source.read_bytes() == body
