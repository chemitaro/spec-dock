import contextlib
import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

import pytest

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    main,
)

_S06_HISTORICAL_POSITIVE_FILENAMES = (
    ("artifacts", "20260810t010101z-pr-repair-batch-review-fix.md"),
    ("artifacts", "20260810t010102z-draft-requirement-requirement.md"),
    ("artifacts", "20260810t010103z-draft-design-design.md"),
    ("artifacts", "20260810t010104z-draft-plan-plan.md"),
    ("artifacts", "20260810t010105z-scratch-capture.md"),
    ("artifacts", "20260810t010106z-note-handoff.md"),
    ("artifacts", "001-adr-token-rotation.md"),
    ("artifacts", "002-disc-api-options.md"),
    ("artifacts", "003-note-kickoff-memo.md"),
    ("artifacts", "20260810t010107z--Report FINAL.PDF"),
    ("artifacts", "20260810t010108z-07--opaque.md"),
    ("artifacts", "20260810t010109z-notes.md"),
    ("artifacts", "20260810t010110z-research-research.md"),
    ("artifacts", "20260810t010111z-interview-hearing.md"),
    ("artifacts", "20260810t010112z-disc-options.md"),
    ("artifacts", "20260810t010113z-decision-candidate-choice.md"),
    ("artifacts", "20260810t010114z-adr-decision.md"),
    ("discussions", "20260810t010115z-disc-legacy.md"),
    ("discussions", "20260810t010116z-01-note-legacy.md"),
    ("discussions", "001-adr-legacy.md"),
    ("discussions", "002-disc-legacy.md"),
    ("discussions", "003-research-legacy.md"),
    ("discussions", "004-note-legacy.md"),
)

_S06_MALFORMED_ARTIFACT_FILENAMES = (
    "20260810t010101z-analysis-unknown.md",
    "20260810T010101z-adr-upper-t.md",
    "20260810t01010z-adr-short-time.md",
    "20261340t256199z-adr-impossible-time.md",
    "20260810t010101z-00-note-bad-slot.md",
    "001-scratch-not-in-sequential-catalog.md",
)


def _path_sha256_snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*"), key=lambda candidate: candidate.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("symlink", path.readlink().as_posix())
        elif path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_dir():
            snapshot[relative] = ("dir", "")
    return snapshot


def _raw_directory_entries(root: Path) -> tuple[bytes, ...]:
    with os.scandir(os.fsencode(root)) as entries:
        return tuple(sorted(os.fsencode(entry.name) for entry in entries))


def _s06_issue_dir(target: Path) -> Path:
    return (
        target
        / "spec-dock"
        / "initiatives"
        / "init-00001-auth-platform"
        / "epics"
        / "epic-00002-jwt-auth"
        / "issues"
        / "iss-00003-add-refresh-token"
    )


class TestCliValidate(CliRuntimeHarness):
    @pytest.mark.skipif(os.name != "posix", reason="raw non-UTF-8 filename fixture requires POSIX bytes paths")
    def test_validate_and_doctor_diagnose_raw_non_utf8_generic_basename_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            artifacts_dir = _s06_issue_dir(target) / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            raw_filename = b"20260810t010101z--invalid-\xff.bin"
            artifacts_fd = os.open(artifacts_dir, os.O_RDONLY)
            try:
                sentinel_filename = b"raw-filename-capability-sentinel"
                sentinel_fd = os.open(
                    sentinel_filename,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                    dir_fd=artifacts_fd,
                )
                os.close(sentinel_fd)
                os.unlink(sentinel_filename, dir_fd=artifacts_fd)
                try:
                    raw_fd = os.open(
                        raw_filename,
                        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                        0o600,
                        dir_fd=artifacts_fd,
                    )
                except OSError as exc:
                    if exc.errno in (errno.EILSEQ, errno.EPERM):
                        errno_name = errno.errorcode[exc.errno]
                        pytest.skip(
                            "filesystem rejects raw non-UTF-8 filename bytes after normal sentinel creation: "
                            f"errno={errno_name}"
                        )
                    raise
                try:
                    os.write(raw_fd, b"raw non-utf8 artifact\n")
                finally:
                    os.close(raw_fd)
                before_entries = _raw_directory_entries(artifacts_dir)
                read_fd = os.open(raw_filename, os.O_RDONLY, dir_fd=artifacts_fd)
                try:
                    before_content = os.read(read_fd, 4096)
                finally:
                    os.close(read_fd)
            finally:
                os.close(artifacts_fd)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode != 0, validated.stdout + validated.stderr
            assert "Malformed artifact filename" in validated.stderr
            assert "Traceback" not in validated.stderr
            assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
            assert "[malformed_artifact]" in diagnosed.stderr
            assert "Traceback" not in diagnosed.stderr
            artifacts_fd = os.open(artifacts_dir, os.O_RDONLY)
            try:
                assert _raw_directory_entries(artifacts_dir) == before_entries
                read_fd = os.open(raw_filename, os.O_RDONLY, dir_fd=artifacts_fd)
                try:
                    assert os.read(read_fd, 4096) == before_content
                finally:
                    os.close(read_fd)
            finally:
                os.close(artifacts_fd)

    @pytest.mark.parametrize(
        "malformed_name",
        (
            None,
            "20260810t010101z-analysis-direct-control.md",
            "20260230t120000z--capture.html",
        ),
    )
    def test_validate_and_doctor_preserve_timestamp_intent_authoring_pack_directory_without_accept_all(
        self,
        malformed_name: str | None,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            artifacts_dir = _s06_issue_dir(target) / "artifacts"
            authoring_pack = artifacts_dir / "20260707t164532z-chatgpt-final-authoring-pack"
            (authoring_pack / "epic").mkdir(parents=True)
            (authoring_pack / "issues" / "01-slice").mkdir(parents=True)
            (authoring_pack / "README.md").write_bytes(b"authoring pack\n")
            (authoring_pack / "manifest.json").write_bytes(b'{"kind":"authoring-pack"}\n')
            (authoring_pack / "epic" / "requirement.md").write_bytes(b"# Requirement\n")
            (authoring_pack / "issues" / "01-slice" / "plan.md").write_bytes(b"# Plan\n")
            attachment = artifacts_dir / "20260807t155105z-disc-new-member-onboarding-guide.html"
            attachment.write_bytes(b"<html><body>out-of-band attachment</body></html>\n")
            generic_html = artifacts_dir / "20260807t155106z--new-member-onboarding-guide.html"
            generic_html.write_bytes(b"<html><body>generic import</body></html>\n")
            if malformed_name is not None:
                (artifacts_dir / malformed_name).write_bytes(b"direct malformed control\n")
            before = _path_sha256_snapshot(target)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            if malformed_name is not None:
                assert validated.returncode != 0, validated.stdout + validated.stderr
                assert "Malformed artifact filename" in validated.stderr
                assert malformed_name in validated.stderr
                assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
                assert "[malformed_artifact]" in diagnosed.stderr
                assert malformed_name in diagnosed.stderr
            else:
                assert validated.returncode == 0, validated.stdout + validated.stderr
                assert diagnosed.returncode == 0, diagnosed.stdout + diagnosed.stderr
            assert _path_sha256_snapshot(target) == before

    @pytest.mark.parametrize(("surface", "filename"), _S06_HISTORICAL_POSITIVE_FILENAMES)
    def test_validate_and_doctor_preserve_explicit_historical_catalog(
        self,
        surface: str,
        filename: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = _s06_issue_dir(target)
            destination_dir = issue_dir / surface
            destination_dir.mkdir(parents=True, exist_ok=True)
            (destination_dir / filename).write_bytes(f"historical:{surface}:{filename}\n".encode())
            before = _path_sha256_snapshot(target)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode == 0, validated.stdout + validated.stderr
            assert diagnosed.returncode == 0, diagnosed.stdout + diagnosed.stderr
            assert _path_sha256_snapshot(target) == before

    @pytest.mark.parametrize("filename", _S06_MALFORMED_ARTIFACT_FILENAMES)
    def test_validate_and_doctor_diagnose_only_explicit_malformed_artifact_controls_without_mutation(
        self,
        filename: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            artifacts_dir = _s06_issue_dir(target) / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / filename).write_bytes(b"malformed historical control\n")
            before = _path_sha256_snapshot(target)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode != 0, validated.stdout + validated.stderr
            assert "Malformed artifact filename" in validated.stderr
            assert filename in validated.stderr
            assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
            assert "[malformed_artifact]" in diagnosed.stderr
            assert filename in diagnosed.stderr
            assert _path_sha256_snapshot(target) == before

    @pytest.mark.parametrize(
        ("filenames", "expected"),
        (
            (
                ("20260810t010101z-note-first.md", "20260810t010101z-note-second.md"),
                "Duplicate artifact id detected",
            ),
            (
                ("20260810t010101z-scratch-first.md", "20260810t010101z-draft-plan-second.md"),
                "Duplicate artifact timestamp slot detected",
            ),
            (
                ("001-adr-first.md", "001-adr-second.md"),
                "Duplicate artifact id detected",
            ),
        ),
    )
    def test_validate_and_doctor_preserve_duplicate_artifacts_while_reporting_actionable_diagnostic(
        self,
        filenames: tuple[str, str],
        expected: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            artifacts_dir = _s06_issue_dir(target) / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            for filename in filenames:
                (artifacts_dir / filename).write_bytes(filename.encode())
            before = _path_sha256_snapshot(target)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode != 0, validated.stdout + validated.stderr
            assert expected in validated.stderr
            assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
            assert "[duplicate_artifact]" in diagnosed.stderr
            assert expected in diagnosed.stderr
            assert _path_sha256_snapshot(target) == before

    @pytest.mark.parametrize(
        "unsafe_kind",
        (
            "artifact-file-symlink",
            "artifacts-directory-symlink",
            "dangling-artifacts-directory-symlink",
        ),
    )
    def test_validate_and_doctor_preserve_unsafe_artifact_paths_while_reporting_actionable_diagnostic(
        self,
        unsafe_kind: str,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = _s06_issue_dir(target)
            artifacts_dir = issue_dir / "artifacts"
            external = target / "external-artifacts"
            if unsafe_kind != "dangling-artifacts-directory-symlink":
                external.mkdir()
            external_file = external / "outside.md"
            if external.exists():
                external_file.write_bytes(b"external artifact\n")
            if unsafe_kind == "artifact-file-symlink":
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                (artifacts_dir / "20260810t010101z-note-external.md").symlink_to(external_file)
            else:
                shutil.rmtree(artifacts_dir)
                artifacts_dir.symlink_to(external, target_is_directory=True)
            if unsafe_kind == "dangling-artifacts-directory-symlink":
                assert artifacts_dir.is_symlink()
                assert artifacts_dir.readlink() == external
                assert not external.exists()
            before = _path_sha256_snapshot(target)

            validated = self._run_runtime_capture(target, ["validate"])
            diagnosed = self._run_runtime_capture(target, ["doctor"])

            assert validated.returncode != 0, validated.stdout + validated.stderr
            assert "Unsafe artifact" in validated.stderr
            assert diagnosed.returncode != 0, diagnosed.stdout + diagnosed.stderr
            assert "[unsafe_artifact]" in diagnosed.stderr
            assert "Unsafe artifact" in diagnosed.stderr
            assert _path_sha256_snapshot(target) == before
            if unsafe_kind == "dangling-artifacts-directory-symlink":
                assert artifacts_dir.is_symlink()
                assert artifacts_dir.readlink() == external
                assert not external.exists()

    def test_validate_rejects_missing_or_invalid_required_meta_identity_fields(self) -> None:
        cases = (
            ("type", None, "field=type"),
            ("type", "", "field=type"),
            ("type", "   ", "field=type"),
            ("type", 123, "field=type"),
            ("id", None, "field=id"),
            ("id", "", "field=id"),
            ("id", "   ", "field=id"),
            ("id", 123, "field=id"),
        )

        for field, value, expected in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0

                self._create_same_repo_linked_hierarchy(target)

                issue_meta = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                    / ".meta.json"
                )
                meta = json.loads(issue_meta.read_text(encoding="utf-8"))
                if value is None:
                    meta.pop(field, None)
                else:
                    meta[field] = value
                self._write_json_force(issue_meta, meta)

                p = self._run_runtime_capture(target, ["validate"])
                assert p.returncode != 0, p.stdout + p.stderr
                assert "Invalid .meta.json" in p.stderr
                assert expected in p.stderr
                assert str(issue_meta) in p.stderr

    def test_validate_detects_broken_parent_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    def test_validate_detects_issue_initiative_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["new", "initiative", "--title", "Payments platform", "--github-issue", "4"])

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["initiative_id"] = "init-00004"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["validate"])

    @pytest.mark.skip(
        reason="S04: covered by TestRuntimeDomainS03.test_validate_graph_rejects_local_only_initiative_under_github_mandatory_contract"
    )
    def test_validate_rejects_local_only_initiative_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            init_meta = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            meta = json.loads(init_meta.read_text(encoding="utf-8"))
            meta.pop("github", None)
            self._write_json_force(init_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "initiative missing github.issue_number" in p.stderr

    @pytest.mark.skip(
        reason="S04: covered by TestValidateApplication.test_validate_graph_reports_linkage_and_parent_diagnostics_without_cli"
    )
    def test_validate_rejects_legacy_unscoped_issue_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3}
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "legacy unscoped github linkage" in p.stderr

    @pytest.mark.skip(
        reason="S04: covered by TestRuntimeSyncS07.test_sync_fails_preflight_for_malformed_partial_repo_scope_linkage"
    )
    def test_sync_fails_preflight_on_partially_scoped_issue_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3, "repo_owner": "example"}
            self._write_json_force(issue_meta, meta)

            for args in (
                ["sync", "--no-github", "--no-update-active"],
                ["sync", "--no-github", "--no-update-active", "--force"],
            ):
                p = self._run_runtime_capture(target, args)
                assert p.returncode != 0, p.stdout + p.stderr
                assert "Invalid github.repo_owner/repo_name" in p.stderr
                assert "both fields are required" in p.stderr
                assert "deps_preflight_failed" not in p.stderr

    @pytest.mark.skip(
        reason="S04: covered by TestRuntimeDomainS03.test_validate_graph_rejects_partially_scoped_issue_linkage"
    )
    def test_validate_rejects_blank_string_repo_scope_in_meta_loader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["github"] = {"issue_number": 3, "repo_owner": "   ", "repo_name": "repo"}
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Invalid github.repo_owner/repo_name" in p.stderr
            assert "empty value is not allowed" in p.stderr
            assert "legacy unscoped github linkage" not in p.stderr

    def test_validate_reports_invalid_meta_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            self._write_text_force(issue_meta, "[]\n")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0
            assert "Invalid .meta.json" in p.stderr
            assert str(issue_meta) in p.stderr

    def test_validate_detects_duplicate_github_issue_numbers_with_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            init_meta = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1}
            self._write_json_force(issue_meta, issue_data)
            shutil.rmtree(target / ".git", ignore_errors=True)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Duplicate github.linkage detected" in p.stderr
            assert "github.issue_number=1" in p.stderr
            assert "repo=(current-or-unknown)" in p.stderr
            assert "initiative:init-00001" in p.stderr
            assert "issue:iss-00003" in p.stderr
            assert "spec-dock/initiatives/init-00001-auth-platform/.meta.json" in p.stderr
            assert (
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json"
                in p.stderr
            )
            assert "Fix github linkage" in p.stderr

    def test_validate_rejects_same_issue_number_when_repo_linkage_is_mixed_and_current_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            init_meta = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(issue_meta, issue_data)
            shutil.rmtree(target / ".git", ignore_errors=True)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Ambiguous github.linkage scope detected" in p.stderr
            assert "fail-closed" in p.stderr
            assert "github.issue_number=1" in p.stderr

    def test_validate_allows_same_issue_number_when_current_repo_is_resolved(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            init_meta = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )

            init_data = json.loads(init_meta.read_text(encoding="utf-8"))
            init_data["github"] = {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"}
            self._write_json_force(init_meta, init_data)

            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["github"] = {"issue_number": 1, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(issue_meta, issue_data)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok" in p.stdout

    def test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "001-disc-second.md").write_text("second\n", encoding="utf-8")
            (discussions_dir / "002-note-legacy-note.md").write_text("legacy note\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-note-current.md").write_text("current\n", encoding="utf-8")
            (discussions_dir / "20260329t123457z-scratch-capture.md").write_text("scratch\n", encoding="utf-8")
            (discussions_dir / "20260329t123458z-interview-hearing.md").write_text("interview\n", encoding="utf-8")
            (discussions_dir / "20260329t123459z-pr-repair-batch-review-fix.md").write_text(
                "batch\n",
                encoding="utf-8",
            )
            (discussions_dir / "20260329todo.md").write_text("ignore me\n", encoding="utf-8")
            (discussions_dir / "rules.md").write_text("notes\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok" in p.stdout

    def test_validate_rejects_malformed_discussion_doc_candidates(self) -> None:
        cases = (
            "20260329t123456z.md",
            "20260329t123456z--adr-kickoff.md",
            "20260329t123456z-1-adr-kickoff.md",
            "20260329t123456z-0a-adr-kickoff.md",
            "20260329t123456z-ADR-kickoff.md",
            "20260329t123456z-01-NOTE-memo.md",
            "20260329t123456z-01-SCRATCH-memo.md",
            "20260329t123456z-bogus-kickoff.md",
            "20260329T123456z-adr-upper-t.md",
            "20260329t123456Z-adr-upper-z.md",
            "20260329t123456z-00-adr-bad-suffix.md",
            "20260329t123456z-100-adr-too-wide.md",
            "20260329t123456z-adr.md",
            "20260329t123456z_adr-kickoff.md",
            "20260329t123456z01-adr-kickoff.md",
            "20260329-adr-kickoff.md",
            "20260329-99-adr-kickoff.md",
            "20260329t-adr-kickoff.md",
            "20260329tt123456z-adr-kickoff.md",
            "20260329x123456z-adr-kickoff.md",
            "20260329x-adr-kickoff.md",
            "20260329t123456zz-adr-kickoff.md",
            "20260329t1234z-adr-kickoff.md",
            "20260329t12345z-adr-kickoff.md",
            "20260329123456z-adr-kickoff.md",
            "20260329123456z-99-adr-kickoff.md",
            "001-adr.md",
            "001_adr-kickoff.md",
            "001-bogus-kickoff.md",
            "foo-adr-kickoff.md",
            "foo-scratch-capture.md",
            "bogus-01-adr-kickoff.md",
            "adr-kickoff.md",
            "draft-requirement-kickoff.md",
            "draft-design-kickoff.md",
            "draft-plan-kickoff.md",
            "pr-repair-batch.md",
            "pr-repair-batch-kickoff.md",
            "20260329t123456z-pr-repair-batch.md",
            "20260329t123456z-PR-repair-batch-kickoff.md",
            "20260329t123456z-pr-repair-batch_.md",
            "interview_kickoff.md",
            "adr_kickoff.md",
        )
        for name in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0

                self._create_same_repo_linked_hierarchy(target)

                discussions_dir = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                    / "discussions"
                )
                discussions_dir.mkdir(parents=True, exist_ok=True)
                (discussions_dir / name).write_text("bad\n", encoding="utf-8")
                (discussions_dir / "rules.md").write_text("allowed\n", encoding="utf-8")

                p = self._run_runtime_capture(target, ["validate"])
                assert p.returncode != 0, p.stdout + p.stderr
                assert "Malformed discussion document filename" in p.stderr
                assert name in p.stderr
                assert "rules.md" not in p.stderr

    def test_validate_accepts_mixed_same_timestamp_unsuffixed_and_suffixed_slots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-adr-kickoff.md").write_text("kickoff\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-01-disc-options.md").write_text("options\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-99-research-spike.md").write_text("spike\n", encoding="utf-8")
            (discussions_dir / "20260329t123457z-interview-hearing.md").write_text("hearing\n", encoding="utf-8")
            (discussions_dir / "20260329t123458z-scratch-capture.md").write_text("capture\n", encoding="utf-8")
            (discussions_dir / "20260329t123459z-draft-requirement-req.md").write_text("req\n", encoding="utf-8")
            (discussions_dir / "20260329t123500z-01-draft-design-design.md").write_text("design\n", encoding="utf-8")
            (discussions_dir / "20260329t123501z-99-draft-plan-plan.md").write_text("plan\n", encoding="utf-8")
            (discussions_dir / "20260329t123502z-pr-repair-batch-review-fix.md").write_text(
                "batch\n",
                encoding="utf-8",
            )
            (discussions_dir / "20260329t123502z-01-pr-repair-batch-review-follow-up.md").write_text(
                "batch suffix\n",
                encoding="utf-8",
            )

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok" in p.stdout

    def test_validate_accepts_high_end_discussion_timestamp_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-99-adr-tail.md").write_text("tail\n", encoding="utf-8")
            (discussions_dir / "20260329t123457z-note-next.md").write_text("next\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok" in p.stdout

    def test_validate_accepts_research_discussion_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-research-spike.md").write_text("spike\n", encoding="utf-8")
            (discussions_dir / "001-research-legacy-spike.md").write_text("legacy\n", encoding="utf-8")
            (discussions_dir / "rules.md").write_text("notes\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "spec-dock: ok" in p.stdout

    def test_validate_accepts_old_new_and_mixed_document_surfaces(self) -> None:
        cases = ("old-only", "new-only", "mixed")
        for case in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)
                issue_dir = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                )
                for artifacts_dir in (target / "spec-dock" / "initiatives").rglob("artifacts"):
                    shutil.rmtree(artifacts_dir)
                for discussions_dir in (target / "spec-dock" / "initiatives").rglob("discussions"):
                    shutil.rmtree(discussions_dir)

                if case in {"old-only", "mixed"}:
                    discussions_dir = issue_dir / "discussions"
                    discussions_dir.mkdir(parents=True, exist_ok=True)
                    (discussions_dir / "20260329t123456z-adr-legacy-decision.md").write_text(
                        "legacy adr\n",
                        encoding="utf-8",
                    )
                if case in {"new-only", "mixed"}:
                    artifacts_dir = issue_dir / "artifacts"
                    artifacts_dir.mkdir(parents=True, exist_ok=True)
                    (artifacts_dir / "20260701t010101z-adr-future-decision.md").write_text(
                        "future adr\n",
                        encoding="utf-8",
                    )

                p = self._run_runtime_capture(target, ["validate"])
                assert p.returncode == 0, p.stdout + p.stderr
                assert "spec-dock: ok" in p.stdout

    def test_validate_rejects_malformed_artifact_filename_with_artifact_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            artifacts_dir = issue_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "20260701t010101z-ADR-future-decision.md").write_text("bad\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Malformed artifact filename" in p.stderr
            assert "20260701t010101z-ADR-future-decision.md" in p.stderr
            assert "Malformed discussion document filename" not in p.stderr

    def test_validate_rejects_symlinked_artifact_file_with_artifact_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            artifacts_dir = issue_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            external = target / "external-artifact.md"
            external.write_text("external\n", encoding="utf-8")
            (artifacts_dir / "20260701t010101z-adr-external-decision.md").symlink_to(external)

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Unsafe artifact file" in p.stderr
            assert "20260701t010101z-adr-external-decision.md" in p.stderr

    def test_validate_rejects_duplicate_artifact_id_with_artifact_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)
            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            artifacts_dir = issue_dir / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            (artifacts_dir / "20260701t010101z-adr-first.md").write_text("first\n", encoding="utf-8")
            (artifacts_dir / "20260701t010101z-adr-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Duplicate artifact id detected" in p.stderr
            assert "id=20260701t010101z-adr" in p.stderr
            assert "Duplicate discussion" not in p.stderr

    def test_validate_legacy_delegated_authority_metadata_is_content_invariant(self) -> None:
        cases = (
            (
                "proposed delegated draft",
                "---\n"
                "status: draft\n"
                "authority: proposed\n"
                "grants: [review_input, planning_input]\n"
                "owner_role: main-orchestrator\n"
                "draft_author_role: system-architect\n"
                "approval: pending-main-promotion\n"
                "source_revision: rev-1\n"
                "approved_revision: rev-1\n"
                "approved_hash: hash-1\n"
                "manifest_hash: manifest-hash\n"
                "permission_profile_name: spec-dock-da\n"
                "permission_profile_hash: profile-hash\n"
                "write_session_invocation_hash: session-hash\n"
                "probe_run_id: probe-1\n"
                "positive_probe_result: pass\n"
                "---\n# Design\n",
                "authority_not_approved",
            ),
            (
                "approved authority with draft status",
                "---\n"
                "status: draft\n"
                "authority: approved\n"
                "grants: [implementation_start]\n"
                "owner_role: main-orchestrator\n"
                "draft_author_role: system-architect\n"
                "approval: fresh-reviewer-pass\n"
                "source_revision: rev-1\n"
                "approved_revision: rev-1\n"
                "approved_hash: hash-1\n"
                "manifest_hash: manifest-hash\n"
                "permission_profile_name: spec-dock-da\n"
                "permission_profile_hash: profile-hash\n"
                "write_session_invocation_hash: session-hash\n"
                "probe_run_id: probe-1\n"
                "positive_probe_result: pass\n"
                "---\n# Design\n",
                "status_not_approved",
            ),
            (
                "missing delegated metadata",
                "---\nauthority: approved\nmanifest_hash: manifest-hash\n---\n# Design\n",
                "incomplete_draft_metadata",
            ),
        )
        for _label, artifact_text, expected_reason in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)
                issue_dir = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                )
                (issue_dir / "design.md").write_text(artifact_text, encoding="utf-8")

                p = self._run_runtime_capture(target, ["validate"])

                assert p.returncode == 0, f"{expected_reason}: {p.stdout}{p.stderr}"
                assert "spec-dock: ok (validate)" in p.stdout
                assert "Delegated draft authority" not in p.stderr

    def test_validate_legacy_evidence_adoption_ledger_is_content_invariant(self) -> None:
        cases = (
            ("blocked", "EAL-021", "blocked", "EAL-021"),
            ("stale", "EAL-022", "stale", "EAL-022"),
            ("`blocked`", "`EAL-023`", "blocked", "EAL-023"),
        )
        for status, entry_id, expected_status, expected_entry_id in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0
                self._create_same_repo_linked_hierarchy(target)
                issue_dir = (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-00001-auth-platform"
                    / "epics"
                    / "epic-00002-jwt-auth"
                    / "issues"
                    / "iss-00003-add-refresh-token"
                )
                (issue_dir / "report.md").write_text(
                    "\n".join([
                        "# Report",
                        "",
                        "## Evidence Adoption Ledger",
                        "",
                        "| ID | adoption_status | target_artifact | next_action |",
                        "|---|---|---|---|",
                        f"| {entry_id} | {status} | design.md | resolve reviewer evidence |",
                        "",
                    ]),
                    encoding="utf-8",
                )

                p = self._run_runtime_capture(target, ["validate"])

                assert p.returncode == 0, f"{expected_status}/{expected_entry_id}: {p.stdout}{p.stderr}"
                assert "spec-dock: ok (validate)" in p.stdout
                assert "Evidence Adoption Ledger incomplete/blocked" not in p.stderr

    def test_validate_rejects_legacy_sequence_for_new_discussion_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "001-scratch-legacy-capture.md").write_text("legacy\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Malformed discussion document filename" in p.stderr
            assert "001-scratch-legacy-capture.md" in p.stderr

    def test_validate_detects_duplicate_discussion_timestamp_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-disc-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Duplicate discussion timestamp slot detected" in p.stderr
            assert "slot=20260329t123456z" in p.stderr
            assert "20260329t123456z-adr-first.md" in p.stderr
            assert "20260329t123456z-disc-second.md" in p.stderr

    def test_validate_detects_duplicate_discussion_timestamp_suffix_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            discussions_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / "discussions"
            )
            discussions_dir.mkdir(parents=True, exist_ok=True)
            (discussions_dir / "20260329t123456z-01-adr-first.md").write_text("first\n", encoding="utf-8")
            (discussions_dir / "20260329t123456z-01-note-second.md").write_text("second\n", encoding="utf-8")

            p = self._run_runtime_capture(target, ["validate"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "Duplicate discussion timestamp suffix detected" in p.stderr
            assert "slot=20260329t123456z-01" in p.stderr
            assert "20260329t123456z-01-adr-first.md" in p.stderr
            assert "20260329t123456z-01-note-second.md" in p.stderr

    @pytest.mark.skip(
        reason="S04: covered by TestValidateApplication.test_validate_tree_reports_missing_required_artifact_docs_without_cli"
    )
    def test_validate_detects_missing_required_artifact_docs_for_each_node_kind(self) -> None:
        artifact_names = ("requirement.md", "design.md", "plan.md", "report.md")
        node_roots = {
            "initiative": (
                Path("spec-dock/initiatives/init-00001-auth-platform"),
                "kind=initiative id=init-00001",
            ),
            "epic": (
                Path("spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth"),
                "kind=epic id=epic-00002",
            ),
            "issue": (
                Path(
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token"
                ),
                "kind=issue id=iss-00003",
            ),
        }
        cases = [
            (kind, artifact_name, node_root / artifact_name, expected)
            for kind, (node_root, expected) in node_roots.items()
            for artifact_name in artifact_names
        ]
        for _name, _artifact_name, artifact_rel_path, expected in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0

                self._create_same_repo_linked_hierarchy(target)

                artifact_path = target / artifact_rel_path
                artifact_path.unlink(missing_ok=False)

                p = self._run_runtime_capture(target, ["validate"])
                assert p.returncode != 0, p.stdout + p.stderr
                assert "Missing required artifact" in p.stderr
                assert expected in p.stderr
                assert artifact_rel_path.as_posix() in p.stderr

    @pytest.mark.skip(
        reason="S04: covered by TestValidateApplication.test_validate_tree_reports_missing_required_meta_without_cli"
    )
    def test_validate_detects_missing_required_meta_for_each_node_kind(self) -> None:
        cases = [
            (
                "initiative",
                Path("spec-dock/initiatives/init-00001-auth-platform/.meta.json"),
                "kind=initiative id=init-00001",
            ),
            (
                "epic",
                Path("spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/.meta.json"),
                "kind=epic id=epic-00002",
            ),
            (
                "issue",
                Path(
                    "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json"
                ),
                "kind=issue id=iss-00003",
            ),
        ]
        for _kind, meta_rel_path, expected in cases:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                assert main(["init", str(target)]) == 0

                self._create_same_repo_linked_hierarchy(target)

                meta_path = target / meta_rel_path
                meta_path.unlink(missing_ok=False)

                p = self._run_runtime_capture(target, ["validate"])
                assert p.returncode != 0, p.stdout + p.stderr
                assert "Missing required artifact" in p.stderr
                assert expected in p.stderr
                assert meta_rel_path.as_posix() in p.stderr

    def test_doctor_detects_missing_required_meta_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            meta_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/.meta.json"
            )
            (target / meta_rel_path).unlink(missing_ok=False)

            p = self._run_runtime_capture(target, ["doctor"])
            assert p.returncode != 0, p.stdout + p.stderr
            assert "spec-dock: doctor: findings=1" in p.stderr
            assert "[missing_artifact]" in p.stderr
            assert meta_rel_path.as_posix() in p.stderr

    def test_validate_sync_and_doctor_classify_missing_meta_with_create_lock_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            (issue_dir / ".meta.json").unlink(missing_ok=False)

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join([
                    "token=active",
                    "pid=1234",
                    "user=tester",
                    f"created_unix={time.time():.6f}",
                    "created_iso=2026-03-23",
                ])
                + "\n",
                encoding="utf-8",
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0, p_validate.stdout + p_validate.stderr
            assert "Create in-progress state detected" in p_validate.stderr
            assert ".meta.json" in p_validate.stderr
            assert "Missing required artifact" not in p_validate.stderr

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_sync.returncode != 0, p_sync.stdout + p_sync.stderr
            assert "Create in-progress state detected" in p_sync.stderr
            assert "Missing required artifact" not in p_sync.stderr

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            assert p_doctor.returncode != 0, p_doctor.stdout + p_doctor.stderr
            assert "[stale_create_lock]" in p_doctor.stderr
            assert "Create in-progress state detected" in p_doctor.stderr
            assert "[missing_artifact]" not in p_doctor.stderr

    def test_validate_sync_and_doctor_classify_missing_meta_with_stale_create_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            (issue_dir / ".meta.json").unlink(missing_ok=False)

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join([
                    "token=stale",
                    "pid=4321",
                    "user=tester",
                    "created_unix=0",
                    "created_iso=1970-01-01",
                ])
                + "\n",
                encoding="utf-8",
            )

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0, p_validate.stdout + p_validate.stderr
            assert "Stale create-lock state detected" in p_validate.stderr
            assert ".meta.json" in p_validate.stderr
            assert "Missing required artifact" not in p_validate.stderr

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_sync.returncode != 0, p_sync.stdout + p_sync.stderr
            assert "Stale create-lock state detected" in p_sync.stderr
            assert "Missing required artifact" not in p_sync.stderr

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            assert p_doctor.returncode != 0, p_doctor.stdout + p_doctor.stderr
            assert "[stale_create_lock]" in p_doctor.stderr
            assert "Stale create-lock state detected" in p_doctor.stderr
            assert "[missing_artifact]" not in p_doctor.stderr

    def test_validate_sync_and_doctor_detect_missing_required_plan_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            missing_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/plan.md"
            )
            (target / missing_rel_path).unlink(missing_ok=False)

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0, p_validate.stdout + p_validate.stderr
            assert "Missing required artifact" in p_validate.stderr
            assert missing_rel_path.as_posix() in p_validate.stderr

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_sync.returncode != 0, p_sync.stdout + p_sync.stderr
            assert "preflight validate failed" in p_sync.stderr
            assert "Missing required artifact" in p_sync.stderr
            assert missing_rel_path.as_posix() in p_sync.stderr

            p_doctor = self._run_runtime_capture(target, ["doctor"])
            assert p_doctor.returncode != 0, p_doctor.stdout + p_doctor.stderr
            assert "[missing_artifact]" in p_doctor.stderr
            assert missing_rel_path.as_posix() in p_doctor.stderr

    def test_issue_71_runtime_bundle_missing_required_artifact_fail_fast(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            missing_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/plan.md"
            )
            (target / missing_rel_path).unlink(missing_ok=False)

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0, p_validate.stdout + p_validate.stderr
            assert "Missing required artifact" in p_validate.stderr
            assert missing_rel_path.as_posix() in p_validate.stderr

            p_sync = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            assert p_sync.returncode != 0, p_sync.stdout + p_sync.stderr
            assert "preflight validate failed" in p_sync.stderr
            assert "Missing required artifact" in p_sync.stderr
            assert missing_rel_path.as_posix() in p_sync.stderr

    def test_sync_force_continues_when_required_plan_artifact_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)
            self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])

            agent_dir = target / "spec-dock" / ".agent"
            missing_rel_path = Path(
                "spec-dock/initiatives/init-00001-auth-platform/epics/epic-00002-jwt-auth/issues/iss-00003-add-refresh-token/plan.md"
            )
            (target / missing_rel_path).unlink(missing_ok=False)

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "preflight validate failed" in p.stderr
            assert "deps_preflight_failed" in p.stderr
            assert missing_rel_path.as_posix() in p.stderr

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert not index["deps"]["valid"]
            assert "preflight validate failed" in str(index["deps"]["error"])
            assert "deps_preflight_failed" in index["warnings"]

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            assert not tree["deps"]["valid"]
            assert "preflight validate failed" in str(tree["deps"]["error"])

    def test_sync_fails_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            self._run_runtime_expect_fail(target, ["sync", "--no-github", "--no-update-active"])

    def test_sync_force_continues_when_tree_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            self._run_runtime(target, ["sync", "--no-github", "--no-update-active"])
            agent_dir = target / "spec-dock" / ".agent"
            baseline_index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert baseline_index["deps"]["valid"]
            assert baseline_index["deps"]["issue_edges"] == []
            assert baseline_index["deps"]["error"] is None

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["parent_id"] = "epic-99999"
            self._write_json_force(issue_meta, meta)

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "preflight validate failed" in p.stderr
            assert "deps_preflight_failed" in p.stderr
            assert (agent_dir / "index.json").is_file()
            assert (agent_dir / "tree.json").is_file()

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert not index["deps"]["valid"]
            assert index["deps"]["issue_edges"] == []
            assert "preflight validate failed" in str(index["deps"]["error"])
            assert "deps_preflight_failed" in index["warnings"]
            assert index["nodes"]["iss-00003"]["deps"] is None

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            assert not tree["deps"]["valid"]
            assert "preflight validate failed" in str(tree["deps"]["error"])

            deps_issues = json.loads((agent_dir / "deps-issues.json").read_text(encoding="utf-8"))
            assert not deps_issues["deps"]["valid"]
            assert "preflight validate failed" in str(deps_issues["deps"]["error"])
            assert deps_issues["nodes"] == {}
            assert deps_issues["edges"] == []

            tree_puml = (target / "spec-dock" / "tree.puml").read_text(encoding="utf-8")
            assert "deps_preflight_failed" in tree_puml
            assert "deps.valid=false" in tree_puml
            assert "--force" in tree_puml
            dashboard = (target / "spec-dock" / "dashboard.md").read_text(encoding="utf-8")
            assert "DEPS_DISABLED" in dashboard
            assert "deps_preflight_failed" in dashboard
            assert "deps.valid=false" in dashboard

            # Legacy v1 deps artifacts must always be removed.
            assert not (agent_dir / "deps.json").exists()
            assert not (agent_dir / "deps.puml").exists()
            assert not (agent_dir / "deps.todo.puml").exists()

    def test_sync_force_continues_when_meta_id_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta = json.loads(issue_meta.read_text(encoding="utf-8"))
            meta["id"] = "broken-id"
            self._write_json_force(issue_meta, meta)

            agent_dir = target / "spec-dock" / ".agent"
            (agent_dir / "index.json").unlink(missing_ok=True)
            (agent_dir / "tree.json").unlink(missing_ok=True)
            (agent_dir / "index-all.json").unlink(missing_ok=True)
            (agent_dir / "tree-all.json").unlink(missing_ok=True)

            p = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            assert p.returncode == 0, p.stdout + p.stderr
            assert "preflight validate failed" in p.stderr
            assert "deps_preflight_failed" in p.stderr
            assert (agent_dir / "index.json").is_file()
            assert (agent_dir / "tree.json").is_file()
            assert (agent_dir / "index-all.json").is_file()
            assert (agent_dir / "tree-all.json").is_file()

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            assert not index["deps"]["valid"]
            assert "deps_preflight_failed" in index["warnings"]
            assert index["deps"]["issue_edges"] == []

    def test_sync_and_validate_do_not_backfill_or_relock_existing_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            init_meta_path = target / "spec-dock" / "initiatives" / "init-00001-auth-platform" / ".meta.json"
            epic_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / ".meta.json"
            )
            issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            meta_paths = [init_meta_path, epic_meta_path, issue_meta_path]

            before_texts: dict[Path, str] = {}
            before_modes: dict[Path, int] = {}

            for meta_path in meta_paths:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                meta.pop("_spec_dock", None)
                self._write_json_force(meta_path, meta)
                if os.name == "posix":
                    with contextlib.suppress(OSError):
                        meta_path.chmod(meta_path.stat().st_mode | 0o200)

                before_text = meta_path.read_text(encoding="utf-8")
                before_texts[meta_path] = before_text
                assert "_spec_dock" not in json.loads(before_text)
                if os.name == "posix":
                    before_modes[meta_path] = meta_path.stat().st_mode

            self._run_runtime(target, ["validate"])
            self._run_runtime(target, ["sync"])

            for meta_path in meta_paths:
                after_text = meta_path.read_text(encoding="utf-8")
                assert after_text == before_texts[meta_path]
                assert "_spec_dock" not in json.loads(after_text)
                if os.name == "posix":
                    after_mode = meta_path.stat().st_mode
                    assert after_mode == before_modes[meta_path]
                    assert after_mode & 0o222 == before_modes[meta_path] & 0o222

    def test_sync_github_keeps_already_normalized_current_repo_linkage_no_origin_continuity(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Foreign issue", "--github-issue", "124"]
            )

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )
            foreign_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00124-foreign-issue"
                / ".meta.json"
            )

            # already-normalized current linkage + explicit foreign same-number overlap.
            current_meta_before = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            assert current_meta_before["github"]["issue_number"] == 123
            assert current_meta_before["github"]["repo_owner"] == "current"
            assert current_meta_before["github"]["repo_name"] == "repo"
            foreign_meta = json.loads(foreign_issue_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_issue_meta_path, foreign_meta)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_result.returncode == 0, sync_result.stdout + sync_result.stderr

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            assert current_meta_after["github"]["issue_number"] == 123
            assert current_meta_after["github"]["repo_owner"] == "current"
            assert current_meta_after["github"]["repo_name"] == "repo"

            # no-origin continuity for already-normalized metadata.
            shutil.rmtree(target / ".git", ignore_errors=True)

            sync_after_no_origin = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_after_no_origin.returncode == 0, sync_after_no_origin.stdout + sync_after_no_origin.stderr

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, validate_result.stdout + validate_result.stderr

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            assert doctor_result.returncode == 0, doctor_result.stdout + doctor_result.stderr

            deps_by_url = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/current/repo/issues/123", "--json"],
            )
            assert deps_by_url.returncode in (0, 3), deps_by_url.stdout + deps_by_url.stderr
            assert '"target": "iss-00123"' in deps_by_url.stdout

            deps_by_id = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-00123", "--json"])
            assert deps_by_id.returncode in (0, 3), deps_by_id.stdout + deps_by_id.stderr
            assert '"target": "iss-00123"' in deps_by_id.stdout

            active_by_url = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/current/repo/issues/123"],
            )
            assert active_by_url.returncode == 0, active_by_url.stdout + active_by_url.stderr

            active_by_id = self._run_runtime_capture(target, ["active", "set", "--id", "iss-00123"])
            assert active_by_id.returncode == 0, active_by_id.stdout + active_by_id.stderr

            ambiguous_number = self._run_runtime_capture(target, ["deps", "check", "123"])
            assert ambiguous_number.returncode != 0, ambiguous_number.stdout + ambiguous_number.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous_number.stderr

            ambiguous_flag = self._run_runtime_capture(target, ["deps", "check", "--github-issue", "123"])
            assert ambiguous_flag.returncode != 0, ambiguous_flag.stdout + ambiguous_flag.stderr
            assert "Ambiguous github.issue_number=123" in ambiguous_flag.stderr

    def test_sync_github_keeps_readonly_lone_unscoped_meta_without_backfill(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"]
            )

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )

            current_meta = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_issue_meta_path, current_meta)
            current_issue_meta_path.chmod(current_issue_meta_path.stat().st_mode & ~0o222)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_result.returncode == 0, sync_result.stdout + sync_result.stderr

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            assert current_meta_after["github"]["issue_number"] == 123
            assert "repo_owner" not in current_meta_after["github"]
            assert "repo_name" not in current_meta_after["github"]
            assert current_issue_meta_path.stat().st_mode & 0o222 == 0

    def test_sync_github_no_backfill_path_does_not_emit_readonly_lock_warning(self) -> None:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            self._run_runtime(target, ["new", "initiative", "--title", "Auth platform", "--github-issue", "1"])
            self._run_runtime(
                target, ["new", "epic", "--initiative", "1", "--title", "JWT auth", "--github-issue", "2"]
            )
            self._run_runtime(
                target, ["new", "issue", "--epic", "2", "--title", "Current issue", "--github-issue", "123"]
            )

            current_issue_meta_path = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00123-current-issue"
                / ".meta.json"
            )

            current_meta = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_issue_meta_path, current_meta)
            current_issue_meta_path.chmod(current_issue_meta_path.stat().st_mode & ~0o222)

            runtime_fs_repo = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _try_make_readonly(path):\n"
                + '    return False, "simulated-relock-failure"\n',
                encoding="utf-8",
            )

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            assert sync_result.returncode == 0, sync_result.stdout + sync_result.stderr
            assert "readonly_lock_failed" not in sync_result.stderr
            assert "simulated-relock-failure" not in sync_result.stderr

            current_meta_after = json.loads(current_issue_meta_path.read_text(encoding="utf-8"))
            assert current_meta_after["github"]["issue_number"] == 123
            assert "repo_owner" not in current_meta_after["github"]
            assert "repo_name" not in current_meta_after["github"]

    def test_validate_and_sync_fail_fast_on_legacy_meta_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"
            assert dot_meta_path.is_file()

            meta = json.loads(dot_meta_path.read_text(encoding="utf-8"))
            meta.pop("_spec_dock", None)
            self._write_json_force(dot_meta_path, meta)
            if os.name == "posix":
                dot_meta_path.chmod(dot_meta_path.stat().st_mode | 0o200)

            before_text = dot_meta_path.read_text(encoding="utf-8")
            dot_meta_path.rename(legacy_meta_path)
            assert not dot_meta_path.exists()
            assert legacy_meta_path.is_file()

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0
            assert "Unsupported legacy meta.json detected" in p_validate.stderr
            assert str(legacy_meta_path) in p_validate.stderr
            assert not dot_meta_path.exists()
            assert legacy_meta_path.is_file()
            assert legacy_meta_path.read_text(encoding="utf-8") == before_text

            p_sync = self._run_runtime_capture(target, ["sync"])
            assert p_sync.returncode != 0
            assert "Unsupported legacy meta.json detected" in p_sync.stderr
            assert str(legacy_meta_path) in p_sync.stderr
            assert not dot_meta_path.exists()
            assert legacy_meta_path.is_file()
            assert legacy_meta_path.read_text(encoding="utf-8") == before_text

    def test_validate_and_sync_fail_fast_when_dot_meta_and_legacy_coexist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"

            before_text = dot_meta_path.read_text(encoding="utf-8")
            legacy_meta_path.write_text("{ invalid legacy json\n", encoding="utf-8")

            p_validate = self._run_runtime_capture(target, ["validate"])
            assert p_validate.returncode != 0, p_validate.stdout + p_validate.stderr
            assert "Unsupported legacy meta.json detected" in p_validate.stderr
            assert str(legacy_meta_path) in p_validate.stderr

            assert dot_meta_path.read_text(encoding="utf-8") == before_text
            assert legacy_meta_path.is_file()

            p_sync = self._run_runtime_capture(target, ["sync"])
            assert p_sync.returncode != 0, p_sync.stdout + p_sync.stderr
            assert "Unsupported legacy meta.json detected" in p_sync.stderr
            assert str(legacy_meta_path) in p_sync.stderr

            assert dot_meta_path.read_text(encoding="utf-8") == before_text
            assert legacy_meta_path.is_file()

    def test_sync_clause3_legacy_meta_json_fail_fast_no_auto_repair_or_agent_write_even_with_force(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            self._create_same_repo_linked_hierarchy(target)
            self._remove_generated_sync_artifacts(target)

            issue_dir = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
            )
            dot_meta_path = issue_dir / ".meta.json"
            legacy_meta_path = issue_dir / "meta.json"
            before_text = dot_meta_path.read_text(encoding="utf-8")
            dot_meta_path.rename(legacy_meta_path)

            active_dir = target / "spec-dock" / "active"
            context_pack_path = active_dir / "context-pack.md"
            assert context_pack_path.is_file(), context_pack_path.as_posix()
            assert not context_pack_path.is_symlink(), context_pack_path.as_posix()
            before_context_pack_text = context_pack_path.read_text(encoding="utf-8")

            def _snapshot_active_pointer(name: str) -> tuple[str, str]:
                active_link_path = active_dir / name
                active_path_file = active_dir / f"{name}.path"
                if active_link_path.is_symlink():
                    assert not active_path_file.exists(), active_path_file.as_posix()
                    return ("symlink", str(active_link_path.readlink()))
                assert not active_link_path.exists(), active_link_path.as_posix()
                assert active_path_file.is_file(), active_path_file.as_posix()
                return ("path", active_path_file.read_text(encoding="utf-8").strip())

            before_active_pointers = {name: _snapshot_active_pointer(name) for name in ("initiative", "epic", "issue")}

            agent_active_path = target / "spec-dock" / ".agent" / "active.json"
            assert not agent_active_path.exists(), agent_active_path.as_posix()

            generated_agent_paths = [
                target / "spec-dock" / ".agent" / "index.json",
                target / "spec-dock" / ".agent" / "tree.json",
                target / "spec-dock" / ".agent" / "index-all.json",
                target / "spec-dock" / ".agent" / "tree-all.json",
                target / "spec-dock" / ".agent" / "deps-issues.json",
            ]
            generated_top_level_paths = [
                target / "spec-dock" / "tree-all.puml",
                target / "spec-dock" / "tree.puml",
                target / "spec-dock" / "deps-issues.puml",
                target / "spec-dock" / "dashboard.md",
            ]
            for generated_path in generated_agent_paths:
                assert not generated_path.exists(), generated_path.as_posix()
            for generated_path in generated_top_level_paths:
                assert not generated_path.exists(), generated_path.as_posix()

            for args in (["sync"], ["sync", "--no-github", "--force"]):
                result = self._run_runtime_capture(target, args)
                assert result.returncode != 0, result.stdout + result.stderr
                assert "Unsupported legacy meta.json detected" in result.stderr
                assert str(legacy_meta_path) in result.stderr
                assert not dot_meta_path.exists()
                assert legacy_meta_path.is_file()
                assert legacy_meta_path.read_text(encoding="utf-8") == before_text
                assert context_pack_path.is_file(), context_pack_path.as_posix()
                assert not context_pack_path.is_symlink(), context_pack_path.as_posix()
                assert context_pack_path.read_text(encoding="utf-8") == before_context_pack_text
                for name, before_active_pointer in before_active_pointers.items():
                    assert _snapshot_active_pointer(name) == before_active_pointer
                assert not agent_active_path.exists(), agent_active_path.as_posix()
                for generated_path in generated_agent_paths:
                    assert not generated_path.exists(), generated_path.as_posix()
            for generated_path in generated_top_level_paths:
                assert not generated_path.exists(), generated_path.as_posix()

            assert legacy_meta_path.is_file()

    def test_issue_78_validate_ignores_legacy_hidden_workspace_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            legacy_dir = target / ".spec-dock" / "initiatives"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            (legacy_dir / "legacy-only.txt").write_text("legacy fixture\n", encoding="utf-8")

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode == 0, validate_result.stdout + validate_result.stderr
            assert "spec-dock: ok" in validate_result.stdout

    def test_issue_78_validate_does_not_fallback_to_legacy_when_current_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(target)

            issue_meta = (
                target
                / "spec-dock"
                / "initiatives"
                / "init-00001-auth-platform"
                / "epics"
                / "epic-00002-jwt-auth"
                / "issues"
                / "iss-00003-add-refresh-token"
                / ".meta.json"
            )
            issue_data = json.loads(issue_meta.read_text(encoding="utf-8"))
            issue_data["parent_id"] = "epic-99999-invalid"
            self._write_json_force(issue_meta, issue_data)

            legacy_dir = target / ".spec-dock" / "initiatives"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            (legacy_dir / "valid-looking.txt").write_text("legacy should be ignored\n", encoding="utf-8")

            validate_result = self._run_runtime_capture(target, ["validate"])
            assert validate_result.returncode != 0, validate_result.stdout + validate_result.stderr
            assert "issue parent_id mismatch" in validate_result.stderr
