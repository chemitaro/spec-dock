import builtins
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import zipfile

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


def _lifecycle_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application.contracts import (
            CheckDepsRequest,
            SyncRequest,
            TargetRef,
            ValidateTreeRequest,
        )
        from spec_dock_runtime.application.set_active import build_context_pack_text
        from spec_dock_runtime.infra.active_store import load_active_manifest
    finally:
        sys.path.pop(0)
    return (
        CheckDepsRequest,
        SyncRequest,
        TargetRef,
        ValidateTreeRequest,
        build_context_pack_text,
        load_active_manifest,
    )


def _post_rollout_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.commands import artifact_import as artifact_import_commands
        from spec_dock_runtime.commands.artifact_import import ArtifactImportFileArgs
    finally:
        sys.path.pop(0)
    return artifact_import_commands, ArtifactImportFileArgs


def _file_import_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from importlib import import_module

        from spec_dock_runtime.application.contracts import FileArtifactImportRequest

        import_file_module = import_module("spec_dock_runtime.application.import_file_artifact")
        create_module = import_module("spec_dock_runtime.application.create_artifact_doc")
    finally:
        sys.path.pop(0)
    return FileArtifactImportRequest, import_file_module, create_module


def _artifact_domain_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain.artifacts import (
            ArtifactSlot,
            parse_artifact_filename,
            parse_generic_imported_artifact_filename,
            scan_artifact_slot_ledger,
        )
    finally:
        sys.path.pop(0)
    return ArtifactSlot, parse_artifact_filename, parse_generic_imported_artifact_filename, scan_artifact_slot_ledger


def _normalize_top_level_generated_at(content: bytes) -> bytes:
    """Normalize only a top-level generated_at value while preserving raw JSON bytes."""

    try:
        payload = json.loads(content)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return content
    if not isinstance(payload, dict) or not isinstance(payload.get("generated_at"), str):
        return content

    def consume_string(start: int) -> int:
        index = start + 1
        escaped = False
        while index < len(content):
            byte = content[index]
            if escaped:
                escaped = False
            elif byte == ord("\\"):
                escaped = True
            elif byte == ord('"'):
                return index + 1
            index += 1
        return len(content)

    depth = 0
    index = 0
    while index < len(content):
        byte = content[index]
        if byte == ord('"'):
            string_end = consume_string(index)
            if depth == 1 and json.loads(content[index:string_end]) == "generated_at":
                value_start = string_end
                while value_start < len(content) and content[value_start] in b" \t\r\n":
                    value_start += 1
                if value_start >= len(content) or content[value_start] != ord(":"):
                    return content
                value_start += 1
                while value_start < len(content) and content[value_start] in b" \t\r\n":
                    value_start += 1
                if value_start >= len(content) or content[value_start] != ord('"'):
                    return content
                value_end = consume_string(value_start)
                return content[:value_start] + b'"<generated_at>"' + content[value_end:]
            index = string_end
            continue
        if byte in (ord("{"), ord("[")):
            depth += 1
        elif byte in (ord("}"), ord("]")):
            depth -= 1
        index += 1
    return content


def test_tc_346_s04_projection_snapshot_preserves_raw_json_except_generated_at() -> None:
    raw = b'{\n  "nested": { "generated_at": "inner" },\n  "b": 2,\n  "generated_at" : "2026-07-14T01:02:03Z"\n}\n'
    normalized = _normalize_top_level_generated_at(raw)
    assert (
        normalized
        == b'{\n  "nested": { "generated_at": "inner" },\n  "b": 2,\n  "generated_at" : "<generated_at>"\n}\n'
    )
    reordered = (
        b'{\n  "generated_at" : "2026-07-14T01:02:03Z",\n  "nested": { "generated_at": "inner" },\n  "b": 2\n}\n'
    )
    assert _normalize_top_level_generated_at(reordered) != normalized


class _FixedClock:
    def now_iso(self) -> str:
        return "2026-07-14T01:02:03Z"

    def today(self) -> str:
        return "2026-07-14"


class TestArtifactImportS04(CliRuntimeHarness):
    _PROJECTION_PATHS = (
        ".agent/index-all.json",
        ".agent/index.json",
        ".agent/tree-all.json",
        ".agent/tree.json",
        ".agent/deps-issues.json",
        "tree-all.puml",
        "tree.puml",
        "deps-issues.puml",
        "deps-raw.puml",
        "dashboard.md",
        "active/context-pack.md",
    )

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

    def _write_runtime_clock(self, target: Path) -> None:
        runtime_clock = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "clock.py"
        runtime_clock.write_text(
            (
                "from __future__ import annotations\n\n"
                "def now_iso() -> str:\n    return '2026-07-14T01:02:03+00:00'\n\n"
                "def today() -> str:\n    return '2026-07-14'\n"
            ),
            encoding="utf-8",
        )

    def _projection_snapshot(self, specdock_dir: Path) -> dict[str, bytes]:
        snapshot: dict[str, bytes] = {}
        for relative in self._PROJECTION_PATHS:
            path = specdock_dir / relative
            if not path.is_file():
                continue
            content = path.read_bytes()
            if path.suffix == ".json":
                content = _normalize_top_level_generated_at(content)
            snapshot[relative] = content
        return snapshot

    def _projection_digest(self, snapshot: dict[str, bytes]) -> str:
        digest = hashlib.sha256()
        for relative, content in snapshot.items():
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(content)
            digest.update(b"\0")
        return digest.hexdigest()

    def _adr_mirror_snapshot(self, specdock_dir: Path) -> tuple[tuple[str, str], ...]:
        adrs_dir = specdock_dir / "adrs"
        if not adrs_dir.is_dir():
            return ()
        return tuple(
            sorted(
                (
                    path.name,
                    f"symlink:{path.readlink()}" if path.is_symlink() else f"bytes:{path.read_bytes()!r}",
                )
                for path in adrs_dir.iterdir()
            )
        )

    def _strict_projection_snapshot(self, specdock_dir: Path) -> dict[str, bytes]:
        snapshot = self._projection_snapshot(specdock_dir)
        assert set(snapshot) == set(self._PROJECTION_PATHS)
        return snapshot

    def _prepare_opaque_import_consumer(self, target: Path) -> tuple[Path, tuple[Path, ...]]:
        assert main(["init", str(target)]) == 0
        self._write_runtime_clock(target)
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=301,
            epic_issue_number=312,
            issue_issue_number=317,
            initiative_title="Architecture",
            epic_title="Workbench",
            issue_title="Opaque lifecycle",
        )
        [issue_dir] = list((target / "spec-dock" / "initiatives").rglob("iss-00317-opaque-lifecycle"))
        baseline_adr = issue_dir / "artifacts" / "20260713t010203z-adr-baseline.md"
        baseline_adr.write_text(
            "\n".join((
                "---",
                "\u7a2e\u5225: ADR\uff08Architecture Decision Record\uff09",
                'ID: "20260713t010203z-adr"',
                'タイトル: "Baseline"',
                '状態: "accepted"',
                '作成者: "Tester"',
                '最終更新: "2026-07-13"',
                '親: ["iss-00317"]',
                'authority: "accepted"',
                "mirror_eligible: true",
                "---",
                "",
                "# Baseline",
                "",
            )),
            encoding="utf-8",
        )
        self._run_runtime(target, ["active", "set", "--id", "iss-00317"])
        self._run_runtime(target, ["validate"])
        self._run_runtime(target, ["sync", "--no-github"])

        sources_dir = target / "spec-dock" / ".workbench"
        sources_dir.mkdir(parents=True, exist_ok=True)
        binary = sources_dir / "opaque-binary.bin"
        binary.write_bytes(b"S04 binary body\x00\xff")
        archive = sources_dir / "opaque-archive.zip"
        with zipfile.ZipFile(archive, "w") as archive_file:
            archive_file.writestr("payload.txt", "S04 ZIP body sentinel")
        invalid_utf8 = sources_dir / "opaque-invalid.md"
        invalid_utf8.write_bytes(b"S04 invalid UTF-8\xff\xfe\x00")
        nul_bearing = sources_dir / "opaque-nul.md"
        nul_bearing.write_bytes(b"S04 NUL body\x00sentinel")
        adr_looking = sources_dir / "accepted-adr-looking.md"
        adr_looking.write_text(
            "\n".join((
                "---",
                "\u7a2e\u5225: ADR\uff08Architecture Decision Record\uff09",
                'ID: "s04-generic-adr-looking"',
                '\u89aa: ["iss-00317"]',
                'authority: "accepted"',
                "mirror_eligible: true",
                "---",
                "",
                "# This body remains opaque",
                "",
            )),
            encoding="utf-8",
        )
        return issue_dir, (binary, archive, invalid_utf8, nul_bearing, adr_looking)

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

    def test_tc_346_s04_003_generic_file_races_legacy_creator_without_overwrite(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (
            _import_module,
            _ArtifactImportError,
            _ArtifactImportRequest,
            CreateArtifactDocRequest,
            _Ports,
            bootstrap,
            _Publisher,
        ) = _runtime_modules()
        FileArtifactImportRequest, import_file_module, create_module = _file_import_modules()
        ArtifactSlot, parse_artifact_filename, parse_generic_imported_artifact_filename, scan_artifact_slot_ledger = (
            _artifact_domain_modules()
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            source = target / "spec-dock" / ".workbench" / "concurrent-generic.bin"
            source.parent.mkdir(parents=True, exist_ok=True)
            source_body = b"generic concurrent body\x00\xff"
            source.write_bytes(source_body)
            sentinel = issue_dir / "artifacts" / "20260714t010203z-99--sentinel.bin"
            sentinel.write_bytes(b"sentinel bytes")

            monkeypatch.setattr(bootstrap.infra_clock, "now_iso", _FixedClock().now_iso)
            context = bootstrap.build_runtime(target / "spec-dock", repo_root=target)
            barrier = threading.Barrier(2)
            original_import_acquire = import_file_module._acquire_create_lock
            original_create_acquire = create_module._acquire_create_lock

            def import_acquire_after_barrier(specdock_dir):
                barrier.wait(timeout=5)
                return original_import_acquire(specdock_dir)

            def create_acquire_after_barrier(specdock_dir):
                barrier.wait(timeout=5)
                return original_create_acquire(specdock_dir)

            monkeypatch.setattr(import_file_module, "_acquire_create_lock", import_acquire_after_barrier)
            monkeypatch.setattr(create_module, "_acquire_create_lock", create_acquire_after_barrier)
            generic_request = FileArtifactImportRequest(
                target_kind="issue",
                target_value="317",
                source_path=source,
            )
            legacy_request = CreateArtifactDocRequest(
                artifact_type="blank",
                scope_node_id="317",
                scope_kind="issue",
                title="Legacy concurrent notes",
                slug="legacy-concurrent-notes",
            )

            with ThreadPoolExecutor(max_workers=2) as executor:
                generic_future = executor.submit(context.use_cases.import_file_artifact, generic_request)
                legacy_future = executor.submit(context.use_cases.create_artifact_doc, legacy_request)
                generic_result = generic_future.result(timeout=10)
                legacy_result = legacy_future.result(timeout=10)

            generic_path = target / generic_result.destination
            legacy_path = target / legacy_result.path
            assert generic_path.is_file()
            assert legacy_path.is_file()
            assert generic_path != legacy_path
            assert generic_path.name.endswith("--concurrent-generic.bin")
            assert legacy_path.name.endswith("-legacy-concurrent-notes.md")
            assert generic_path.name != legacy_path.name
            assert generic_path.name.startswith("20260714t010203z")
            assert generic_path.read_bytes() == source_body
            assert legacy_path.read_bytes()
            assert source.read_bytes() == source_body
            assert sentinel.read_bytes() == b"sentinel bytes"

            generic_parsed = parse_generic_imported_artifact_filename(generic_path.name)
            legacy_parsed = parse_artifact_filename(legacy_path.name)
            assert generic_parsed is not None
            assert legacy_parsed is not None
            assert generic_parsed.original_basename == source.name
            assert legacy_parsed.artifact_type == "blank"
            fixed_timestamp = "20260714t010203z"
            expected_slots = {
                ArtifactSlot(fixed_timestamp, None),
                ArtifactSlot(fixed_timestamp, 1),
            }
            observed_slots = {
                ArtifactSlot(generic_parsed.timestamp, generic_parsed.suffix),
                ArtifactSlot(legacy_parsed.timestamp, legacy_parsed.suffix),
            }
            assert observed_slots == expected_slots
            duplicate_error, ledger = scan_artifact_slot_ledger(issue_dir / "artifacts")
            assert duplicate_error is None
            assert expected_slots <= ledger.used_slots
            assert {generic_parsed.artifact_id, legacy_parsed.artifact_id} <= ledger.artifact_ids

            # Keep the oracle sensitive to a missing suffix assignment without coupling it to winner order.
            with pytest.raises(AssertionError):
                assert {ArtifactSlot(fixed_timestamp, None)} == expected_slots

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

    def test_tc_346_s04_001_opaque_body_open_denial_matrix(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _issue_dir, sources = self._prepare_opaque_import_consumer(target)
            source_bodies = {source: source.read_bytes() for source in sources}
            target_specs = (
                ("root", None, sources[0]),
                ("initiative", "301", sources[1]),
                ("epic", "312", sources[2]),
                ("issue", "317", sources[3]),
                ("issue", "317", sources[4]),
            )
            destinations: list[Path] = []
            for target_kind, target_id, source in target_specs:
                command = ["artifact", "import", "file", f"--{target_kind}"]
                if target_id is not None:
                    command.append(target_id)
                command.extend(["--file", source.relative_to(target).as_posix(), "--json"])
                result = self._run_runtime_capture(target, command)
                assert result.returncode == 0, result.stdout + result.stderr
                payload = json.loads(result.stdout)
                assert payload["import_kind"] == "file"
                assert payload["storage_identity"] == "generic"
                assert payload["canonical"] is False
                assert "sha256" not in payload
                assert "byte_count" not in payload
                assert "mime" not in payload
                assert "encoding" not in payload
                destination = target / payload["destination"]
                assert destination.is_file()
                assert destination.name.split("--", 1)[0].startswith("202")
                destinations.append(destination)

            (
                CheckDepsRequest,
                SyncRequest,
                TargetRef,
                ValidateTreeRequest,
                build_context_pack_text,
                load_active_manifest,
            ) = _lifecycle_modules()
            (
                _import_module,
                _ArtifactImportError,
                _ArtifactImportRequest,
                _CreateArtifactDocRequest,
                _Ports,
                bootstrap,
                _Publisher,
            ) = _runtime_modules()
            specdock_dir = target / "spec-dock"
            context = bootstrap.build_runtime(specdock_dir, repo_root=target)
            generic_paths = {path.absolute() for path in destinations}

            def install_open_guard(guard: pytest.MonkeyPatch) -> list[Path]:
                opened: list[Path] = []

                def canonical(candidate: object) -> set[Path]:
                    if isinstance(candidate, int):
                        return set()
                    try:
                        path = Path(candidate)  # type: ignore[arg-type]
                    except (TypeError, ValueError):
                        return set()
                    return {path.absolute(), path.resolve()}

                def deny(candidate: object) -> None:
                    if generic_paths.intersection(canonical(candidate)):
                        path = Path(candidate)  # type: ignore[arg-type]
                        opened.append(path)
                        raise AssertionError(f"generic body must remain unopened: {path.name}")

                original_path_open = Path.open
                original_read_text = Path.read_text
                original_read_bytes = Path.read_bytes
                original_builtin_open = builtins.open
                original_io_open = io.open

                def guarded_path_open(path: Path, *args, **kwargs):
                    deny(path)
                    return original_path_open(path, *args, **kwargs)

                def guarded_read_text(path: Path, *args, **kwargs):
                    deny(path)
                    return original_read_text(path, *args, **kwargs)

                def guarded_read_bytes(path: Path, *args, **kwargs):
                    deny(path)
                    return original_read_bytes(path, *args, **kwargs)

                def guarded_builtin_open(file, *args, **kwargs):
                    deny(file)
                    return original_builtin_open(file, *args, **kwargs)

                def guarded_io_open(file, *args, **kwargs):
                    deny(file)
                    return original_io_open(file, *args, **kwargs)

                guard.setattr(Path, "open", guarded_path_open)
                guard.setattr(Path, "read_text", guarded_read_text)
                guard.setattr(Path, "read_bytes", guarded_read_bytes)
                guard.setattr(builtins, "open", guarded_builtin_open)
                guard.setattr(io, "open", guarded_io_open)
                return opened

            # First guard is an explicit sensitivity check. The measured guard
            # below is a fresh instance and therefore cannot inherit this read.
            with monkeypatch.context() as sensitivity_guard:
                sensitivity_opened = install_open_guard(sensitivity_guard)
                with pytest.raises(AssertionError, match="generic body must remain unopened"):
                    destinations[0].read_bytes()
                assert len(sensitivity_opened) == 1

            with monkeypatch.context() as lifecycle_guard:
                lifecycle_opened = install_open_guard(lifecycle_guard)
                validation = context.use_cases.validate_tree(ValidateTreeRequest())
                deps = context.use_cases.check_deps(
                    CheckDepsRequest(
                        target=TargetRef(kind="node_id", node_id="iss-00317", github_issue_number=None),
                        use_github=False,
                        issue_limit=10000,
                    )
                )
                sync_result = context.use_cases.sync(
                    SyncRequest(
                        force=False,
                        github_enabled=False,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    )
                )
                active = load_active_manifest(specdock_dir)
                assert active.manifest is not None
                context_pack = build_context_pack_text(active.manifest, repo_root=target)
                assert validation.report.errors == []
                assert deps.target.node_id == "iss-00317"
                assert sync_result.artifact_failure is None
                assert "# Context Pack (generated)" in context_pack
                assert lifecycle_opened == []

            adr_mirror = self._adr_mirror_snapshot(specdock_dir)
            assert len(adr_mirror) == 1
            assert adr_mirror[0][0] == "20260713t010203z-adr-baseline.md"
            assert all(destination.name not in {name for name, _target in adr_mirror} for destination in destinations)
            assert all(source.read_bytes() == source_bodies[source] for source in sources)
            assert all(
                destination.read_bytes() == source_bodies[source]
                for destination, source in zip(destinations, sources, strict=True)
            )

    def test_tc_346_s04_002_projection_and_context_equivalence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _issue_dir, sources = self._prepare_opaque_import_consumer(target)
            specdock_dir = target / "spec-dock"
            baseline_projection = self._strict_projection_snapshot(specdock_dir)
            baseline_mirror = self._adr_mirror_snapshot(specdock_dir)
            baseline_context = (specdock_dir / "active" / "context-pack.md").read_bytes()
            baseline_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-00317", "--no-github", "--json"],
            )
            assert baseline_deps.returncode == 0, baseline_deps.stdout + baseline_deps.stderr
            baseline_typed = tuple(
                sorted(
                    path.name
                    for path in specdock_dir.rglob("artifacts/*")
                    if path.suffix == ".md" and path.name != "rules.md" and "--" not in path.name
                )
            )

            target_specs = (
                ("root", None, sources[0]),
                ("initiative", "301", sources[1]),
                ("epic", "312", sources[2]),
                ("issue", "317", sources[3]),
                ("issue", "317", sources[4]),
            )
            imported: list[Path] = []
            for target_kind, target_id, source in target_specs:
                command = ["artifact", "import", "file", f"--{target_kind}"]
                if target_id is not None:
                    command.append(target_id)
                command.extend(["--file", source.relative_to(target).as_posix(), "--json"])
                result = self._run_runtime_capture(target, command)
                assert result.returncode == 0, result.stdout + result.stderr
                imported.append(target / json.loads(result.stdout)["destination"])

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync", "--no-github"])
            after_projection = self._strict_projection_snapshot(specdock_dir)
            after_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-00317", "--no-github", "--json"],
            )
            assert after_deps.returncode == 0, after_deps.stdout + after_deps.stderr
            assert after_projection == baseline_projection
            assert (specdock_dir / "active" / "context-pack.md").read_bytes() == baseline_context
            assert after_deps.stdout == baseline_deps.stdout
            assert self._adr_mirror_snapshot(specdock_dir) == baseline_mirror
            after_typed = tuple(
                sorted(
                    path.name
                    for path in specdock_dir.rglob("artifacts/*")
                    if path.suffix == ".md" and path.name != "rules.md" and "--" not in path.name
                )
            )
            assert after_typed == baseline_typed
            projection_text = b"\n".join(after_projection.values())
            assert all(path.name.encode() not in projection_text for path in imported)
            assert all(
                marker not in projection_text
                for marker in (
                    b"opaque-binary.bin",
                    b"opaque-archive.zip",
                    b"opaque-invalid.md",
                    b"opaque-nul.md",
                    b"accepted-adr-looking.md",
                    b"This body remains opaque",
                )
            )

    def test_tc_s04_001_002_003_generic_bodies_do_not_change_default_lifecycle_projections(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._write_runtime_clock(target)
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
            specdock_dir = target / "spec-dock"
            epic_dir = issue_dir.parents[1]
            initiative_dir = issue_dir.parents[3]
            accepted_adr = issue_dir / "artifacts" / "20260713t010203z-adr-baseline.md"
            accepted_adr.write_text(
                "\n".join((
                    "---",
                    "種別: ADR（Architecture Decision Record）",
                    'ID: "20260713t010203z-adr"',
                    'タイトル: "Baseline"',
                    '状態: "accepted"',
                    '作成者: "Tester"',
                    '最終更新: "2026-07-13"',
                    '親: ["iss-00317"]',
                    'authority: "accepted"',
                    "mirror_eligible: true",
                    "---",
                    "",
                    "# Baseline",
                    "",
                )),
                encoding="utf-8",
            )
            self._run_runtime(target, ["active", "set", "--id", "iss-00317"])
            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync", "--no-github"])
            baseline_projection = self._projection_snapshot(specdock_dir)
            baseline_digest = self._projection_digest(baseline_projection)
            baseline_mirror = self._adr_mirror_snapshot(specdock_dir)
            baseline_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-00317", "--no-github", "--json"],
            )
            assert baseline_deps.returncode == 0, baseline_deps.stdout + baseline_deps.stderr

            generic_paths: list[Path] = []
            invalid_payload = b"\xff\xfe\x00generic-invalid-utf8"
            for index, scope_dir in enumerate((specdock_dir, initiative_dir, epic_dir, issue_dir), start=1):
                artifacts_dir = scope_dir / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                generic = artifacts_dir / f"20260730t01020{index}z--opaque-{index}.md"
                generic.write_bytes(invalid_payload)
                generic_paths.append(generic)
            adr_looking_generic = issue_dir / "artifacts" / "20260730t010205z--accepted-adr-looking.md"
            adr_looking_generic.write_text(
                "\n".join((
                    "---",
                    "種別: ADR（Architecture Decision Record）",
                    'ID: "20260730t010205z-adr"',
                    '親: ["iss-00317"]',
                    'authority: "accepted"',
                    "mirror_eligible: true",
                    "---",
                    "",
                    "# Must remain opaque",
                    "",
                )),
                encoding="utf-8",
            )
            generic_paths.append(adr_looking_generic)

            (
                CheckDepsRequest,
                SyncRequest,
                TargetRef,
                ValidateTreeRequest,
                build_context_pack_text,
                load_active_manifest,
            ) = _lifecycle_modules()
            (
                _import_module,
                _ArtifactImportError,
                _ArtifactImportRequest,
                _CreateArtifactDocRequest,
                _Ports,
                bootstrap,
                _Publisher,
            ) = _runtime_modules()
            context = bootstrap.build_runtime(specdock_dir, repo_root=target)
            generic_path_set = set(generic_paths)
            original_open = Path.open
            original_read_text = Path.read_text
            original_read_bytes = Path.read_bytes
            opened_generic: list[Path] = []

            def deny_generic(path: Path) -> None:
                if path in generic_path_set:
                    opened_generic.append(path)
                    raise AssertionError(f"generic body must remain unopened: {path.name}")

            def guarded_open(path: Path, *args, **kwargs):
                deny_generic(path)
                return original_open(path, *args, **kwargs)

            def guarded_read_text(path: Path, *args, **kwargs):
                deny_generic(path)
                return original_read_text(path, *args, **kwargs)

            def guarded_read_bytes(path: Path):
                deny_generic(path)
                return original_read_bytes(path)

            with monkeypatch.context() as lifecycle_guard:
                lifecycle_guard.setattr(Path, "open", guarded_open)
                lifecycle_guard.setattr(Path, "read_text", guarded_read_text)
                lifecycle_guard.setattr(Path, "read_bytes", guarded_read_bytes)

                with pytest.raises(AssertionError, match="generic body must remain unopened"):
                    generic_paths[0].read_bytes()
                opened_generic.clear()

                validation = context.use_cases.validate_tree(ValidateTreeRequest())
                deps = context.use_cases.check_deps(
                    CheckDepsRequest(
                        target=TargetRef(kind="node_id", node_id="iss-00317", github_issue_number=None),
                        use_github=False,
                        issue_limit=10000,
                    )
                )
                sync_result = context.use_cases.sync(
                    SyncRequest(
                        force=False,
                        github_enabled=False,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    )
                )
                active = load_active_manifest(specdock_dir)
                assert active.manifest is not None
                context_pack = build_context_pack_text(active.manifest, repo_root=target)

                assert validation.report.errors == []
                assert deps.target.node_id == "iss-00317"
                assert sync_result.artifact_failure is None
                assert "# Context Pack (generated)" in context_pack
                assert opened_generic == []

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync", "--no-github"])
            after_projection = self._projection_snapshot(specdock_dir)
            after_digest = self._projection_digest(after_projection)
            after_mirror = self._adr_mirror_snapshot(specdock_dir)
            after_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-00317", "--no-github", "--json"],
            )

            assert after_deps.returncode == 0, after_deps.stdout + after_deps.stderr
            assert after_projection == baseline_projection
            assert after_digest == baseline_digest
            assert after_deps.stdout == baseline_deps.stdout
            assert after_mirror == baseline_mirror
            assert baseline_mirror == (("20260713t010203z-adr-baseline.md", baseline_mirror[0][1]),)
            assert all(path.name not in {name for name, _target in after_mirror} for path in generic_paths)
            assert all(path.read_bytes() == invalid_payload for path in generic_paths[:-1])
            assert b"Must remain opaque" in adr_looking_generic.read_bytes()

    def test_tc_s04_005_typed_and_blank_keep_legacy_names_while_generic_reserves_shared_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            self._write_runtime_clock(target)
            artifacts_dir = issue_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            existing = {
                artifacts_dir / "20260713t010201z-existing-notes.md": b"existing blank",
                artifacts_dir / "20260713t010202z-research-existing.md": b"existing typed",
                artifacts_dir / "20260714t010203z--opaque.bin": b"generic sentinel",
            }
            for path, body in existing.items():
                path.write_bytes(body)

            blank = self._run_runtime_capture(
                target,
                ["new", "artifact", "blank", "--issue", "iss-00317", "--title", "Working Notes"],
            )
            typed = self._run_runtime_capture(
                target,
                ["new", "artifact", "research", "--issue", "iss-00317", "--title", "Research Notes"],
            )

            assert blank.returncode == 0, blank.stdout + blank.stderr
            assert typed.returncode == 0, typed.stdout + typed.stderr
            assert "id=20260714t010203z-01 scope=iss-00317" in blank.stdout
            assert "id=20260714t010203z-02-research scope=iss-00317" in typed.stdout
            assert (artifacts_dir / "20260714t010203z-01-working-notes.md").is_file()
            assert (artifacts_dir / "20260714t010203z-02-research-research-notes.md").is_file()
            assert all(path.read_bytes() == body for path, body in existing.items())
            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync", "--no-github"])

    def test_tc_s99_002_post_rollout_write_disable_keeps_generic_compatibility_layer(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            self._write_runtime_clock(target)
            specdock_dir = target / "spec-dock"
            artifacts_dir = issue_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            timestamp = "20260714t010203z"
            grandfathered = {
                artifacts_dir / f"{timestamp}--grandfathered.bin": b"\xff\x00grandfathered-binary",
                artifacts_dir / f"{timestamp}-01--grandfathered.md": b"# Grandfathered Markdown\n",
                artifacts_dir / f"{timestamp}-02--adr-looking.md": (
                    b"---\nauthority: accepted\nmirror_eligible: true\n---\n\n# Must remain opaque\n"
                ),
            }
            existing_typed_and_blank = {
                artifacts_dir / f"{timestamp}-03-research-existing.md": b"existing typed",
                artifacts_dir / f"{timestamp}-04-existing-notes.md": b"existing blank",
            }
            for path, body in {**grandfathered, **existing_typed_and_blank}.items():
                path.write_bytes(body)
            before_names = {path.name for path in artifacts_dir.iterdir()}
            source = target / "new-generic.bin"
            source.write_bytes(b"must not be imported")

            (
                _import_module,
                _ArtifactImportError,
                _ArtifactImportRequest,
                CreateArtifactDocRequest,
                _Ports,
                bootstrap,
                _Publisher,
            ) = _runtime_modules()
            (
                _CheckDepsRequest,
                SyncRequest,
                _TargetRef,
                ValidateTreeRequest,
                _build_context_pack_text,
                _load_active_manifest,
            ) = _lifecycle_modules()
            artifact_import_commands, ArtifactImportFileArgs = _post_rollout_modules()
            monkeypatch.setattr(bootstrap.infra_clock, "now_iso", _FixedClock().now_iso)
            context = bootstrap.build_runtime(specdock_dir, repo_root=target)

            def disabled_import_file_artifact(_request):
                raise RuntimeError("post-rollout generic creation disabled")

            post_rollout_use_cases = replace(
                context.use_cases,
                import_file_artifact=disabled_import_file_artifact,
            )
            file_command = artifact_import_commands.command_specs()["artifact_import_file"]
            with pytest.raises(RuntimeError, match="artifact import file runtime contract violation"):
                file_command.run(
                    ArtifactImportFileArgs(
                        target_kind="issue",
                        target_value="iss-00317",
                        source_path=str(source),
                        json=False,
                    ),
                    post_rollout_use_cases,
                )
            assert {path.name for path in artifacts_dir.iterdir()} == before_names

            generic_path_set = set(grandfathered)
            original_open = Path.open
            original_read_text = Path.read_text
            original_read_bytes = Path.read_bytes
            opened_generic: list[Path] = []

            def deny_generic(path: Path) -> None:
                if path in generic_path_set:
                    opened_generic.append(path)
                    raise AssertionError(f"generic body must remain unopened: {path.name}")

            def guarded_open(path: Path, *args, **kwargs):
                deny_generic(path)
                return original_open(path, *args, **kwargs)

            def guarded_read_text(path: Path, *args, **kwargs):
                deny_generic(path)
                return original_read_text(path, *args, **kwargs)

            def guarded_read_bytes(path: Path):
                deny_generic(path)
                return original_read_bytes(path)

            with monkeypatch.context() as lifecycle_guard:
                lifecycle_guard.setattr(Path, "open", guarded_open)
                lifecycle_guard.setattr(Path, "read_text", guarded_read_text)
                lifecycle_guard.setattr(Path, "read_bytes", guarded_read_bytes)

                validation = post_rollout_use_cases.validate_tree(ValidateTreeRequest())
                sync_result = post_rollout_use_cases.sync(
                    SyncRequest(
                        force=False,
                        github_enabled=False,
                        issue_limit=10000,
                        update_active_from_branch=False,
                    )
                )
                blank = post_rollout_use_cases.create_artifact_doc(
                    CreateArtifactDocRequest(
                        artifact_type="blank",
                        scope_node_id="iss-00317",
                        scope_kind="issue",
                        title="Post Rollout Notes",
                        slug=None,
                    )
                )
                typed = post_rollout_use_cases.create_artifact_doc(
                    CreateArtifactDocRequest(
                        artifact_type="research",
                        scope_node_id="iss-00317",
                        scope_kind="issue",
                        title="Post Rollout Research",
                        slug=None,
                    )
                )

                assert validation.report.errors == []
                assert sync_result.artifact_failure is None
                assert blank.path.name == f"{timestamp}-05-post-rollout-notes.md"
                assert typed.path.name == f"{timestamp}-06-research-post-rollout-research.md"
                assert opened_generic == []

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync", "--no-github"])
            assert source.read_bytes() == b"must not be imported"
            assert {path.name for path in grandfathered} <= {path.name for path in artifacts_dir.iterdir()}
            assert all(path.read_bytes() == body for path, body in grandfathered.items())
            assert all(path.read_bytes() == body for path, body in existing_typed_and_blank.items())
            assert self._adr_mirror_snapshot(specdock_dir) == ()
