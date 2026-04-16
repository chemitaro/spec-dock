import contextlib
import io
import json
import os
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


def _runtime_fs_repo():
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
        from spec_dock_runtime.infra import fs_repo as infra_fs_repo
    finally:
        sys.path.pop(0)
    return infra_fs_repo


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
    github_issue_number: int | None = None,
    github_repo_owner: str | None = None,
    github_repo_name: str | None = None,
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
        github_issue_number=github_issue_number,
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
        meta_path=(path / ".meta.json").as_posix(),
    )


def _write_required_docs(node_dir: Path) -> None:
    node_dir.mkdir(parents=True, exist_ok=True)
    (node_dir / ".meta.json").write_text("{}\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (node_dir / name).write_text(f"{name}\n", encoding="utf-8")


def _write_record_artifacts(record) -> None:
    node_dir = Path(record.path)
    node_dir.mkdir(parents=True, exist_ok=True)
    meta_payload = {
        "type": record.kind,
        "id": record.id,
        "title": record.title,
        "slug": record.slug,
    }
    if record.parent_id is not None:
        meta_payload["parent_id"] = record.parent_id
    if record.initiative_id is not None:
        meta_payload["initiative_id"] = record.initiative_id
    if record.epic_id is not None:
        meta_payload["epic_id"] = record.epic_id
    if record.github_issue_number is not None:
        meta_payload["github"] = {"issue_number": int(record.github_issue_number)}
        if record.github_repo_owner is not None and record.github_repo_name is not None:
            meta_payload["github"]["repo_owner"] = record.github_repo_owner
            meta_payload["github"]["repo_name"] = record.github_repo_name
    (node_dir / ".meta.json").write_text(json.dumps(meta_payload), encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (node_dir / name).write_text(f"{name}\n", encoding="utf-8")


def _build_valid_records(infra_contracts, *, specdock_dir: Path):
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"
    records = [
        _record(
            infra_contracts,
            kind="initiative",
            node_id="init-local-00001",
            title="Auth Platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            github_repo_owner="example",
            github_repo_name="repo",
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
            github_issue_number=102,
            github_repo_owner="example",
            github_repo_name="repo",
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
            github_issue_number=103,
            github_repo_owner="example",
            github_repo_name="repo",
        ),
    ]
    for record in records:
        _write_record_artifacts(record)
    return (records, issue_dir)


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


class _StubGitGateway:
    def __init__(self, origin_slug: str | None):
        self._origin_slug = origin_slug

    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return self._origin_slug


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
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Duplicate discussion sequence detected under /repo/spec-dock/x/discussions: seq=001 files=[001-adr-first.md, 001-disc-second.md]"
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )
        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

        self.assertFalse(result.ok)
        self.assertEqual(result.findings[0].code, "duplicate_seq")
        self.assertIn("Duplicate discussion sequence detected", result.findings[0].message)
        self.assertTrue(result.findings[0].guidance)
        self.assertTrue(any("重複している discussion markdown" in line for line in result.findings[0].guidance))
        self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_duplicate_discussion_timestamps(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        cases = (
            (
                "slot",
                (
                    "20260312t010203z-adr-first.md",
                    "20260312t010203z-disc-second.md",
                ),
                "Duplicate discussion timestamp slot detected",
            ),
            (
                "suffix",
                (
                    "20260312t010203z-01-adr-first.md",
                    "20260312t010203z-01-disc-second.md",
                ),
                "Duplicate discussion timestamp suffix detected",
            ),
        )

        for label, filenames, expected_message in cases:
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    specdock_dir = repo_root / "spec-dock"
                    records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
                    discussions_dir = issue_dir / "discussions"
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    for filename in filenames:
                        (discussions_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

                    ports = app_ports.Ports(
                        node_reader=_StubNodeReader(records),
                        repo_root=repo_root,
                        specdock_dir=specdock_dir,
                    )
                    result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

                    self.assertFalse(result.ok)
                    self.assertEqual(result.findings[0].code, "duplicate_seq")
                    self.assertIn(expected_message, result.findings[0].message)
                    self.assertTrue(result.findings[0].guidance)
                    self.assertTrue(any("重複している discussion markdown" in line for line in result.findings[0].guidance))
                    self.assertFalse(any("重複 sequence" in line for line in result.findings[0].guidance))
                    self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_malformed_discussion_doc_filename(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        ports = app_ports.Ports(
            node_reader=_FailingNodeReader(
                "Malformed discussion document filename under /repo/spec-dock/x/discussions: "
                "20260329x-adr-kickoff.md. Expected `<ts>-<kind>-<slug>.md`, "
                "`<ts>-<nn>-<kind>-<slug>.md`, or grandfathered `<nnn>-<kind>-<slug>.md`."
            ),
            repo_root=Path("/repo"),
            specdock_dir=Path("/repo/spec-dock"),
        )
        result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

        self.assertFalse(result.ok)
        self.assertEqual(result.findings[0].code, "malformed_discussion_doc")
        self.assertIn("Malformed discussion document filename", result.findings[0].message)
        self.assertTrue(result.findings[0].guidance)
        self.assertTrue(any("discussions 配下" in line for line in result.findings[0].guidance))
        self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_malformed_discussion_doc_filename_from_repo_backed_validation(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        infra_fs_repo = _runtime_fs_repo()

        class _RepoBackedNodeReader:
            def __init__(self, specdock_dir: Path):
                self._specdock_dir = specdock_dir

            def load_node_records(self):
                return infra_fs_repo.load_node_records(self._specdock_dir)

        cases = (
            "20260329x-adr-kickoff.md",
            "foo-adr-kickoff.md",
            "bogus-01-adr-kickoff.md",
        )
        for malformed_name in cases:
            with self.subTest(malformed_name=malformed_name):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root = Path(tmp)
                    specdock_dir = repo_root / "spec-dock"
                    _records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
                    discussions_dir = issue_dir / "discussions"
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    (discussions_dir / malformed_name).write_text("# malformed\n", encoding="utf-8")

                    ports = app_ports.Ports(
                        node_reader=_RepoBackedNodeReader(specdock_dir),
                        repo_root=repo_root,
                        specdock_dir=specdock_dir,
                    )
                    result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

                    self.assertFalse(result.ok)
                    self.assertEqual(result.findings[0].code, "malformed_discussion_doc")
                    self.assertIn("Malformed discussion document filename under", result.findings[0].message)
                    self.assertIn(malformed_name, result.findings[0].message)
                    self.assertIn("Expected `<ts>-<kind>-<slug>.md`", result.findings[0].message)
                    self.assertTrue(result.findings[0].guidance)
                    self.assertTrue(any("discussions 配下" in line for line in result.findings[0].guidance))
                    self.assertTrue(any("spec-dock/scripts/spec-dock validate" in line for line in result.findings[0].guidance))

    def test_doctor_detects_duplicate_id(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            second_issue_dir = issue_dir.parent / "iss-local-1-add-refresh-token-alias"
            second_issue_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-1",
                title="Add Refresh Token Alias",
                path=second_issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=104,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(second_issue_record)
            records.append(second_issue_record)

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
            duplicate_issue_record = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Add Refresh Token Duplicate",
                path=duplicate_issue_dir,
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=105,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(duplicate_issue_record)
            records.append(duplicate_issue_record)

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

    def test_doctor_detects_legacy_unscoped_github_linkage_when_current_repo_is_resolved(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            records[0] = _record(
                infra_contracts,
                kind="initiative",
                node_id="init-local-00001",
                title="Auth Platform",
                path=Path(records[0].path),
                parent_id=None,
                initiative_id=None,
                epic_id=None,
                github_issue_number=123,
            )
            _write_record_artifacts(records[0])
            records[2] = _record(
                infra_contracts,
                kind="issue",
                node_id="iss-local-00001",
                title="Add Refresh Token",
                path=Path(records[2].path),
                parent_id="epic-local-00001",
                initiative_id="init-local-00001",
                epic_id="epic-local-00001",
                github_issue_number=123,
                github_repo_owner="other",
                github_repo_name="repo",
            )
            _write_record_artifacts(records[2])

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
                git_gateway=_StubGitGateway("example/repo"),
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(result.findings[0].code, "broken_meta")
            self.assertIn("legacy unscoped github linkage", result.findings[0].message)

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
                github_issue_number=101,
                github_repo_owner="example",
                github_repo_name="repo",
            )
            _write_record_artifacts(records[0])
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

    def test_issue_78_doctor_reports_legacy_only_workspace_as_finding(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, _infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            legacy_dir = repo_root / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader([]),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertFalse(result.ok)
            self.assertEqual(len(result.findings), 1)
            finding = result.findings[0]
            self.assertEqual(finding.code, "legacy_only_workspace")
            self.assertIn(str(legacy_dir), finding.message)
            self.assertTrue(any("Do not rename '.spec-dock'" in line for line in finding.guidance))
            self.assertTrue(any("spec-dock init" in line for line in finding.guidance))
            self.assertTrue(any("migrate" in line.lower() for line in finding.guidance))

    def test_issue_78_doctor_reports_cleanup_pending_warning_for_valid_coexistence(self) -> None:
        _runtime_app, app_contracts, app_doctor, app_ports, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            records, _issue_dir = _build_valid_records(infra_contracts, specdock_dir=specdock_dir)
            legacy_dir = repo_root / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            ports = app_ports.Ports(
                node_reader=_StubNodeReader(records),
                repo_root=repo_root,
                specdock_dir=specdock_dir,
            )
            result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)

            self.assertTrue(result.ok)
            self.assertEqual(result.findings, [])
            self.assertIn("legacy_cleanup_pending", result.warnings)

    def test_issue_78_main_doctor_renders_cleanup_pending_warning_message(self) -> None:
        runtime_app, app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        from spec_dock_runtime.cli import bootstrap as cli_bootstrap

        original_find_specdock_dir = runtime_app._find_specdock_dir
        original_application_doctor = cli_bootstrap.application_doctor
        runtime_app._find_specdock_dir = lambda: Path("/repo/spec-dock")
        cli_bootstrap.application_doctor = lambda _req, _ports: app_contracts.DoctorResult(
            ok=True,
            findings=[],
            warnings=["legacy_cleanup_pending"],
        )
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = runtime_app.main(["doctor"])
        finally:
            runtime_app._find_specdock_dir = original_find_specdock_dir
            cli_bootstrap.application_doctor = original_application_doctor

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "spec-dock: ok (doctor) findings=0\n")
        stderr_text = stderr.getvalue()
        self.assertIn("spec-dock: (warn) legacy '.spec-dock/' is still present.", stderr_text)
        self.assertNotIn("legacy_cleanup_pending", stderr_text)

    def test_issue_78_main_doctor_reaches_legacy_only_workspace_guidance(self) -> None:
        runtime_app, _app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        original_cwd = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                (repo_root / ".spec-dock").mkdir(parents=True, exist_ok=True)
                os.chdir(repo_root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = runtime_app.main(["doctor"])
        finally:
            os.chdir(original_cwd)

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        stderr_text = stderr.getvalue()
        self.assertIn("spec-dock: doctor: findings=1", stderr_text)
        self.assertIn("[legacy_only_workspace]", stderr_text)
        self.assertIn("Do not rename '.spec-dock'", stderr_text)
        self.assertIn("spec-dock init", stderr_text)

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

    def test_issue_78_main_doctor_keeps_not_found_when_no_workspace_exists(self) -> None:
        runtime_app, _app_contracts, _app_doctor, _app_ports, _infra_contracts = _runtime_modules()
        original_cwd = Path.cwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                repo_root = Path(tmp)
                os.chdir(repo_root)
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exit_code = runtime_app.main(["doctor"])
        finally:
            os.chdir(original_cwd)

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("'spec-dock' not found. Run 'uvx ... spec-dock init' first.", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
