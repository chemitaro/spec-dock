import json
from pathlib import Path
import shutil
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorkbench(CliRuntimeHarness):
    def _prepare_linked_worktrees(self, root: Path) -> tuple[Path, Path, str, Path, Path]:
        if shutil.which("git") is None:
            pytest.skip("git not available")

        source = root / "source"
        target = root / "target-renamed"
        source.mkdir()
        assert main(["init", str(source)]) == 0
        self._create_same_repo_linked_hierarchy(source)
        self._run_git(source, ["add", "-A"])
        self._run_git(
            source,
            ["-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "init"],
        )
        self._run_git(source, ["worktree", "add", "-b", "target", str(target)])

        source_meta = next(
            path
            for path in (source / "spec-dock" / "initiatives").rglob(".meta.json")
            if json.loads(path.read_text(encoding="utf-8"))["type"] == "issue"
        )
        scope_id = json.loads(source_meta.read_text(encoding="utf-8"))["id"]

        target_meta = next(
            path
            for path in (target / "spec-dock" / "initiatives").rglob(".meta.json")
            if json.loads(path.read_text(encoding="utf-8"))["id"] == scope_id
        )
        renamed_target_scope = target_meta.parent.with_name(f"{scope_id}-target-side-renamed")
        target_meta.parent.rename(renamed_target_scope)

        return source, target, scope_id, source_meta.parent, renamed_target_scope

    def test_workbench_copy_help_exposes_only_current_source_scope_and_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "repo"
            source.mkdir()
            assert main(["init", str(source)]) == 0

            result = self._run_runtime_capture(source, ["workbench", "copy", "--help"])

            assert result.returncode == 0, result.stderr
            assert "--scope" in result.stdout
            assert "--to" in result.stdout
            assert "--json" in result.stdout
            assert "--from" not in result.stdout

    def test_workbench_copy_uses_target_scope_record_and_keeps_output_content_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(Path(tmp))
            secret_body = "single-file-secret-body\n"
            source_file = source_scope / ".workbench" / "analysis.txt"
            source_file.parent.mkdir()
            source_file.write_text(secret_body, encoding="utf-8")

            text_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert text_result.returncode == 0, text_result.stderr
            assert (target_scope / ".workbench" / "analysis.txt").read_text(encoding="utf-8") == secret_body
            assert not (target / source_scope.relative_to(source) / ".workbench" / "analysis.txt").exists()
            combined_text = text_result.stdout + text_result.stderr
            assert "experimental" in combined_text
            assert "canonical=false" in combined_text
            assert "one_shot=true" in combined_text
            assert "sync=false" in combined_text
            assert secret_body.strip() not in combined_text

            json_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name, "--json"],
            )

            assert json_result.returncode == 0, json_result.stderr
            payload = json.loads(json_result.stdout)
            assert payload["status"] == "ok"
            assert payload["command"] == "copy"
            assert payload["experimental"] is True
            assert payload["canonical"] is False
            assert payload["one_shot"] is True
            assert payload["sync"] is False
            assert secret_body.strip() not in json_result.stdout
