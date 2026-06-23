import json
from pathlib import Path
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliAssuranceCompose(CliRuntimeHarness):
    def test_assurance_compose_all_materializes_planning_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_classified_fixture(target)

            result = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["operation"] == "compose"
            assert payload["ok"] is True
            assert payload["status"] == "applied"
            assert payload["classification"]["authorized_profile"] == "standard"
            assert sorted(payload["changed_paths"]) == sorted(
                [
                    (issue_dir / "design.md").relative_to(target).as_posix(),
                    (issue_dir / "plan.md").relative_to(target).as_posix(),
                    (issue_dir / "report.md").relative_to(target).as_posix(),
                ]
            )
            for artifact in ("design", "plan", "report"):
                text = (issue_dir / f"{artifact}.md").read_text(encoding="utf-8")
                assert "spec-dock:managed-section begin" in text
                assert f"artifact\": \"{artifact}\"" not in text
                assert payload["artifacts"][artifact]["changed"] is True
                assert payload["artifacts"][artifact]["added_section_ids"]

    def test_assurance_compose_second_run_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_classified_fixture(target)

            first = self._run_runtime_capture(target, ["assurance", "compose", "--artifact", "all", "--format", "json"])
            second = self._run_runtime_capture(target, ["assurance", "compose", "--artifact", "all", "--format", "json"])

            assert first.returncode == 0, first.stdout + first.stderr
            assert second.returncode == 0, second.stdout + second.stderr
            payload = json.loads(second.stdout)
            assert payload["ok"] is True
            assert payload["status"] == "unchanged"
            assert payload["changed_paths"] == []

    def test_assurance_compose_missing_and_invalid_assurance_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            missing_issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Missing assurance")
            before_missing = self._artifact_texts(missing_issue_dir)

            missing = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--format", "json"],
            )

            assert missing.returncode == 1
            missing_payload = json.loads(missing.stdout)
            assert missing_payload["ok"] is False
            assert missing_payload["status"] == "invalid"
            assert missing_payload["reason"] == "missing_assurance_contract"
            assert "assurance classify --stage requirement" in " ".join(missing_payload["details"])
            assert self._artifact_texts(missing_issue_dir) == before_missing

            self._run_runtime(
                target,
                [
                    "new",
                    "issue",
                    "--epic",
                    "201",
                    "--title",
                    "Invalid assurance",
                    "--github-issue",
                    "302",
                ],
            )
            self._run_runtime(target, ["active", "set", "--id", "iss-00302"])
            invalid_issue_dir = self._find_issue_dir_by_id(target, "iss-00302")
            (invalid_issue_dir / "assurance.json").write_text("{not-json\n", encoding="utf-8")
            before_invalid = self._artifact_texts(invalid_issue_dir)

            invalid = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--format", "json"],
            )

            assert invalid.returncode == 1
            invalid_payload = json.loads(invalid.stdout)
            assert invalid_payload["ok"] is False
            assert invalid_payload["status"] == "invalid"
            assert invalid_payload["reason"] == "invalid_json"
            assert self._artifact_texts(invalid_issue_dir) == before_invalid

    def test_assurance_compose_marker_conflict_keeps_artifact_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_classified_fixture(target)
            design_path = issue_dir / "design.md"
            design_path.write_text(
                design_path.read_text(encoding="utf-8")
                + '\n<!-- spec-dock:managed-section begin id="standard.design.assurance-gates" -->\n',
                encoding="utf-8",
            )
            before = self._artifact_texts(issue_dir)

            result = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--format", "json"],
            )

            assert result.returncode == 1
            payload = json.loads(result.stdout)
            assert payload["ok"] is False
            assert payload["status"] == "invalid"
            assert payload["reason"] == "marker_conflict"
            assert payload["artifacts"]["design"]["errors"]
            assert self._artifact_texts(issue_dir) == before

    def test_assurance_compose_rejects_symlinked_artifact_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_classified_fixture(target)
            external = target / "external-design.md"
            external.write_text("# External\n", encoding="utf-8")
            design_path = issue_dir / "design.md"
            design_path.unlink()
            design_path.symlink_to(external)

            result = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--format", "json"],
            )

            assert result.returncode == 1
            assert "Refusing to use symlinked planning artifact" in result.stderr
            assert external.read_text(encoding="utf-8") == "# External\n"

    def test_assurance_compose_dry_run_does_not_write_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            issue_dir = self._create_classified_fixture(target)
            before = self._artifact_texts(issue_dir)

            result = self._run_runtime_capture(
                target,
                ["assurance", "compose", "--artifact", "all", "--dry-run", "--format", "json"],
            )

            assert result.returncode == 0, result.stdout + result.stderr
            payload = json.loads(result.stdout)
            assert payload["ok"] is True
            assert payload["status"] == "dry-run"
            assert payload["dry_run"] is True
            assert payload["changed_paths"]
            assert self._artifact_texts(issue_dir) == before

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

    def _create_classified_fixture(self, target: Path) -> Path:
        issue_dir = self._create_assurance_fixture(target, issue_number=301, title="Compose assurance")
        self._run_runtime(target, ["assurance", "classify", "--stage", "requirement", "--format", "json"])
        return issue_dir

    def _find_issue_dir_by_id(self, target: Path, issue_id: str) -> Path:
        for meta_path in sorted((target / "spec-dock" / "initiatives").glob("**/.meta.json")):
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if payload.get("type") == "issue" and payload.get("id") == issue_id:
                return meta_path.parent
        raise AssertionError(f"issue not found: {issue_id}")

    def _artifact_texts(self, issue_dir: Path) -> dict[str, str]:
        return {
            artifact: (issue_dir / f"{artifact}.md").read_text(encoding="utf-8")
            for artifact in ("design", "plan", "report")
        }
