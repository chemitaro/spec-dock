import json
from pathlib import Path
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliAssurance(CliRuntimeHarness):
    def test_assurance_classify_writes_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Add assurance")

            result = self._run_runtime_capture(
                target,
                ["assurance", "classify", "--stage", "requirement", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            contract_path = issue_dir / "assurance.json"
            assert contract_path.is_file()
            persisted = json.loads(contract_path.read_text(encoding="utf-8"))
            assert payload["operation"] == "classify"
            assert payload["ok"] is True
            assert payload["mode"] == "adaptive"
            assert payload["has_contract"] is True
            assert payload["classification"]["authorized_profile"] == "standard"
            assert payload["classification"]["complexity_tier"] == "normal"
            assert payload["classification"]["lite_candidate"] is False
            assert payload["classification"]["lite_authorized"] is False
            assert persisted == payload["contract"]
            assert persisted["issue_id"] == "iss-00301"
            assert persisted["stage"] == "requirement"
            assert persisted["mode"] == "adaptive"

    def test_assurance_classify_dry_run_does_not_write_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Preview assurance")

            result = self._run_runtime_capture(
                target,
                ["assurance", "classify", "--stage", "requirement", "--dry-run", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["operation"] == "classify"
            assert payload["ok"] is True
            assert payload["dry_run"] is True
            assert payload["has_contract"] is True
            assert payload["classification"]["authorized_profile"] == "standard"
            assert not (issue_dir / "assurance.json").exists()

    def test_assurance_show_and_verify_strict_legacy_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_assurance_fixture(target, issue_number=301, title="Legacy issue")

            for command in ("show", "verify"):
                result = self._run_runtime_capture(target, ["assurance", command, "--format", "json"])

                assert result.returncode == 0, result.stdout + result.stderr
                payload = json.loads(result.stdout)
                assert payload["operation"] == command
                assert payload["ok"] is True
                assert payload["status"] == "missing"
                assert payload["mode"] == "strict-legacy"
                assert payload["has_contract"] is False
                assert payload["classification"]["authorized_profile"] == "strict"

    def test_assurance_verify_invalid_contract_exits_one_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Invalid issue")
            (issue_dir / "assurance.json").write_text("{not-json\n", encoding="utf-8")

            result = self._run_runtime_capture(target, ["assurance", "verify", "--format", "json"])

            assert result.returncode == 1
            payload = json.loads(result.stdout)
            assert payload["operation"] == "verify"
            assert payload["ok"] is False
            assert payload["status"] == "invalid"
            assert payload["mode"] == "invalid"
            assert payload["reason"] == "invalid_json"
            assert payload["details"]

    def test_assurance_explicit_target_takes_precedence_over_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            active_issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Active issue")
            explicit_issue_dir = self._create_issue_under_existing_epic(
                target,
                issue_number=302,
                title="Explicit issue",
            )

            by_id = self._run_runtime_capture(
                target,
                ["assurance", "classify", "--stage", "requirement", "--issue", "iss-00302", "--format", "json"],
            )
            by_number = self._run_runtime_capture(
                target,
                ["assurance", "show", "--issue", "302", "--format", "json"],
            )
            by_path = self._run_runtime_capture(
                target,
                [
                    "assurance",
                    "show",
                    "--issue",
                    explicit_issue_dir.relative_to(target).as_posix(),
                    "--format",
                    "json",
                ],
            )

            assert by_id.returncode == 0, by_id.stdout + by_id.stderr
            assert by_number.returncode == 0, by_number.stdout + by_number.stderr
            assert by_path.returncode == 0, by_path.stdout + by_path.stderr
            assert not (active_issue_dir / "assurance.json").exists()
            assert (explicit_issue_dir / "assurance.json").is_file()
            assert json.loads(by_id.stdout)["issue_id"] == "iss-00302"
            assert json.loads(by_number.stdout)["issue_id"] == "iss-00302"
            assert json.loads(by_path.stdout)["issue_id"] == "iss-00302"

    def _create_assurance_fixture(self, target: Path, *, issue_number: int, title: str) -> Path:
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=101,
            epic_issue_number=201,
            issue_issue_number=issue_number,
            issue_title=title,
        )
        issue_id = f"iss-{issue_number:05d}"
        self._run_runtime(target, ["active", "set", "--id", issue_id])
        return self._find_issue_dir_by_id(target, issue_id)

    def _create_issue_under_existing_epic(self, target: Path, *, issue_number: int, title: str) -> Path:
        self._run_runtime(
            target,
            [
                "new",
                "issue",
                "--epic",
                "201",
                "--title",
                title,
                "--github-issue",
                str(issue_number),
            ],
        )
        return self._find_issue_dir_by_id(target, f"iss-{issue_number:05d}")

    def _find_issue_dir_by_id(self, target: Path, issue_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("type") == "issue" and payload.get("id") == issue_id:
                return meta_path.parent
        raise AssertionError(f"issue not found: {issue_id}")
