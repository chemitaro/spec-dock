import contextlib
import io
import sys
import tempfile
import time
import unittest
from pathlib import Path


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime import app as runtime_app
        from spec_dock_runtime.application import contracts as app_contracts
        from spec_dock_runtime.application import doctor as app_doctor
        from spec_dock_runtime.application import ports as app_ports
        from spec_dock_runtime.infra import contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return runtime_app, app_contracts, app_doctor, app_ports, infra_contracts


def _record(
    infra_contracts,
    *,
    kind: str,
    node_id: str,
    title: str,
    path: Path,
    parent_id: str | None,
    initiative_id: str | None,
    epic_id: str | None,
):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=None,
        meta_path=(path / ".meta.json").as_posix(),
    )


def _write_required_docs(node_dir: Path) -> None:
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (node_dir / name).write_text(f"{name}\n", encoding="utf-8")


def _build_valid_records(infra_contracts, *, specdock_dir: Path):
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
    _write_required_docs(init_dir)
    _write_required_docs(epic_dir)
    _write_required_docs(issue_dir)
    return (
        [
            _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth Platform",
                path=init_dir,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
            ),
            _record(
                infra_contracts,
                kind="epic",
                node_id="epic-local-00001",
                title="JWT Auth",
                path=epic_dir,
                parent_id="init-local-00001",
                initiative_id="init-local-00001",
                epic_id=None,
            ),
            _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Add Refresh Token",
                path=issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
            ),
        ],
        issue_dir,
    )


class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)

    def load_node_records(self):
        return list(self._records)


class _FailingNodeReader:
    def __init__(self, message: str):
        self._message = message

    def load_node_records(self):
        raise RuntimeError(self._message)


class _StubActiveStateStore:
    def __init__(self, load_result):
        self._load_result = load_result

    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return self._load_result


class TestRuntimeDoctorS04(unittest.TestCase):
    def test_doctor_detects_missing_artifact(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            (issue_dir / "plan.md").unlink(missing_ok=False)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "missing_artifact")
            self.assertIn("plan.md", result.findings[0].message)
            self.assertTrue(result.findings[0].guidance)

    def test_doctor_detects_duplicate_discussion_sequence(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            discussions_dir = issue_dir / "discussions"
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "duplicate_seq")
            self.assertIn("Duplicate discussion sequence detected", result.findings[0].message)
            self.assertTrue(result.findings[0].guidance)
            self.assertTrue(any("discussions" in line for line in result.findings[0].guidance))
            self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_duplicate_id(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            second_issue_dir = issue_dir.parent / "iss-local-1-add-refresh-token-alias"
            _write_required_docs(second_issue_dir)
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-1",
                    title="Add Refresh Token Alias",
                    path=second_issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                )
            )

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "duplicate_id")
            self.assertIn("Duplicate numeric id detected", result.findings[0].message)
            self.assertTrue(result.findings[0].guidance)
            self.assertTrue(any(".meta.json" in line for line in result.findings[0].guidance))
            self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_exact_duplicate_id_message(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            duplicate_issue_dir = issue_dir.parent / "iss-local-00001-add-refresh-token-duplicate"
            _write_required_docs(duplicate_issue_dir)
            records.append(
                _record(
                    infra_contracts,
                    kind="issue",
                    node_id="iss-local-00001",
                    title="Add Refresh Token Duplicate",
                    path=duplicate_issue_dir,
                    parent_id="epic-local-00001",
                    initiative_id="init-local-00001",
                    epic_id="epic-local-00001",
                )
            )

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "duplicate_id")
            self.assertIn("Duplicate id detected", result.findings[0].message)
            self.assertNotIn("Duplicate numeric id detected", result.findings[0].message)
            self.assertTrue(result.findings[0].guidance)

    def test_doctor_detects_broken_meta_when_reader_fails(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader("Invalid .meta.json (expected object): /repo/spec-dock/x/.meta.json"),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )

        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
        self.assertFalse(result.ok)
        self.assertEqual(result.findings[0].code, "broken_meta")
        self.assertIn("Invalid .meta.json", result.findings[0].message)
        self.assertTrue(result.findings[0].guidance)
        self.assertTrue(any(".meta.json" in line for line in result.findings[0].guidance))
        self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_broken_meta_when_reader_reports_invalid_json_for_meta(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Invalid JSON: /repo/spec-dock/initiatives/init-local-00001-alpha/.meta.json: Expecting value"
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )

        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
        self.assertFalse(result.ok)
        self.assertEqual(result.findings[0].code, "broken_meta")
        self.assertIn("Invalid JSON:", result.findings[0].message)

    def test_doctor_detects_broken_meta_when_required_field_is_missing(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            initiative_path = Path(records[0].path)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="",
                path=initiative_path,
                parent_id=None,
                initiative_id=None,
                epic_id=None,
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "broken_meta")
            self.assertIn("Missing title in .meta.json", result.findings[0].message)

    def test_doctor_skips_stale_active_pointer_id_check_when_graph_is_unavailable(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            del records
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path=issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_FailingNodeReader(f"Invalid .meta.json (expected object): {issue_dir / '.meta.json'}"),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            codes = [finding.code for finding in result.findings]
            self.assertIn("broken_meta", codes)
            self.assertNotIn("stale_active_pointer", codes)

    def test_doctor_detects_stale_active_pointer(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=infra_contracts.ActiveManifestEntry(
                        id="init-local-00001",
                        path="spec-dock/initiatives/init-local-00001-auth-platform",
                    ),
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-99999",
                        path="spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-00001-jwt-auth/issues/iss-local-99999-missing",
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            self.assertIn("stale_active_pointer", codes)
            stale_finding = next((finding for finding in result.findings if finding.code == "stale_active_pointer"), None)
            self.assertIsNotNone(stale_finding)
            if stale_finding is None:
                self.fail("stale_active_pointer finding was not returned")
            self.assertTrue(stale_finding.guidance)
            self.assertTrue(any("active clear" in line for line in stale_finding.guidance))
            self.assertTrue(any("active set <target>" in line for line in stale_finding.guidance))

    def test_doctor_detects_stale_active_pointer_for_absolute_path_outside_repo(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            outside_issue_dir = Path(outside_tmp) / "iss-local-00001-outside"
            _write_required_docs(outside_issue_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path=outside_issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            self.assertIn("stale_active_pointer", codes)
            stale_finding = next((finding for finding in result.findings if finding.code == "stale_active_pointer"), None)
            self.assertIsNotNone(stale_finding)
            if stale_finding is None:
                self.fail("stale_active_pointer finding was not returned")
            self.assertIn("issue.path", stale_finding.message)

    def test_doctor_detects_stale_active_pointer_when_manifest_path_points_to_file(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            readme_path = specdock_dir / "README.md"
            readme_path.write_text("not a node directory\n", encoding="utf-8")

            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-00001",
                        path="spec-dock/README.md",
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            self.assertIn("stale_active_pointer", codes)
            stale_finding = next((finding for finding in result.findings if finding.code == "stale_active_pointer"), None)
            self.assertIsNotNone(stale_finding)
            if stale_finding is None:
                self.fail("stale_active_pointer finding was not returned")
            self.assertIn("issue.path is not a directory", stale_finding.message)

    def test_doctor_detects_stale_active_pointer_id_mismatch_when_graph_ids_are_empty(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            existing_issue_dir = specdock_dir / "issues" / "iss-local-99999-existing"
            _write_required_docs(existing_issue_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-local-99999",
                        path=existing_issue_dir.as_posix(),
                    ),
                ),
                source="agent.active",
                warnings=[],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader([]),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            codes = [finding.code for finding in result.findings]
            self.assertIn("stale_active_pointer", codes)
            stale_finding = next((finding for finding in result.findings if finding.code == "stale_active_pointer"), None)
            self.assertIsNotNone(stale_finding)
            if stale_finding is None:
                self.fail("stale_active_pointer finding was not returned")
            self.assertIn("issue.id=iss-local-99999 is not found in current graph", stale_finding.message)

    def test_doctor_reports_stale_active_pointer_when_manifest_is_invalid_and_missing(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            load_result = infra_contracts.ActiveManifestLoadResult(
                manifest=None,
                source="none",
                warnings=["active_manifest_invalid_shape:agent.active"],
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                active_state_store=_StubActiveStateStore(load_result),
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            codes = [finding.code for finding in result.findings]
            self.assertIn("stale_active_pointer", codes)
            stale_finding = next((finding for finding in result.findings if finding.code == "stale_active_pointer"), None)
            self.assertIsNotNone(stale_finding)
            if stale_finding is None:
                self.fail("stale_active_pointer finding was not returned")
            self.assertIn("active_manifest_invalid_shape:agent.active", stale_finding.message)
            self.assertTrue(any("active clear" in line for line in stale_finding.guidance))
            self.assertTrue(any("active set <target>" in line for line in stale_finding.guidance))
            self.assertIn("active_manifest_invalid_shape:agent.active", result.warnings)

    def test_doctor_detects_stale_create_lock(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=abc",
                        "pid=1234",
                        "user=tester",
                        "created_unix=0",
                        "created_iso=2026-03-01",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            self.assertIsNotNone(finding)
            if finding is None:
                self.fail("stale_create_lock finding was not returned")
            self.assertIn("stale=true", finding.message)
            self.assertIn(str(lock_path), finding.message)
            self.assertTrue(any("create 実行中プロセス" in line for line in finding.guidance))
            self.assertTrue(any(str(lock_path) in line for line in finding.guidance))

    def test_doctor_detects_invalid_create_lock_metadata(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text("pid=1234\n", encoding="utf-8")
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            self.assertIsNotNone(finding)
            if finding is None:
                self.fail("stale_create_lock finding was not returned")
            self.assertIn("metadata=missing_fields", finding.message)
            self.assertIn(str(lock_path), finding.message)

    def test_doctor_detects_non_stale_create_lock_contention(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=running",
                        "pid=5678",
                        "user=tester",
                        f"created_unix={time.time():.6f}",
                        "created_iso=2026-03-18",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )

            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
            self.assertFalse(result.ok)
            finding = next((item for item in result.findings if item.code == "stale_create_lock"), None)
            self.assertIsNotNone(finding)
            if finding is None:
                self.fail("stale_create_lock finding was not returned")
            self.assertIn("stale=false", finding.message)
            self.assertIn("contention=true", finding.message)
            self.assertTrue(any("create 実行中" in line for line in finding.guidance))
            self.assertTrue(any("削除" in line for line in finding.guidance))

    def test_main_doctor_delegates_to_use_case(self) -> None:
        runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_doctor = cli_bootstrap.application_doctor
        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        cli_bootstrap.application_doctor = lambda _req, _ports: app_contracts.DoctorResult(
            ok=False,
            findings=[
                app_contracts.DoctorFinding(
                    code="missing_artifact",
                    message="Missing required artifact: kind=issue id=iss-local-00001 artifact=.../plan.md",
                    guidance=["復元してください。"],
                )
            ],
            warnings=[],
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["doctor"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_doctor = original_application_doctor

        stderr_text = stderr.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("spec-dock: doctor: findings=1", stderr_text)
        self.assertIn("[missing_artifact]", stderr_text)
        self.assertIn("  -> 復元してください。", stderr_text)


if __name__ == "__main__":
    unittest.main()
