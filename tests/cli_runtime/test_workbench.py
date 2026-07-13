import json
from pathlib import Path
import shutil
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestCliWorkbench(CliRuntimeHarness):
    @staticmethod
    def _assert_content_free_error(payload: dict[str, object], *, code: str, side: str | None) -> None:
        assert payload == {
            "status": "error",
            "command": "copy",
            "code": code,
            "side": side,
            "mutation_started": False,
            "experimental": True,
            "canonical": False,
            "disposable": True,
            "one_shot": True,
            "sync": False,
        }

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
            assert "experimental" in result.stdout.lower()
            assert "non-canonical" in result.stdout.lower()
            assert "disposable" in result.stdout.lower()
            assert "one-shot" in result.stdout.lower()
            assert "does not synchronize" in result.stdout.lower()

    @pytest.mark.parametrize("forbidden_option", ["--from", "--root", "--date", "--path"])
    def test_workbench_copy_rejects_unpublished_source_and_scope_routes(self, forbidden_option: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "repo"
            source.mkdir()
            assert main(["init", str(source)]) == 0

            result = self._run_runtime_capture(
                source,
                [
                    "workbench",
                    "copy",
                    "--scope",
                    "iss-00003",
                    "--to",
                    "target",
                    forbidden_option,
                    "must-not-be-accepted",
                ],
            )

            assert result.returncode != 0
            assert "unrecognized arguments" in result.stderr

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
            assert payload == {
                "status": "ok",
                "command": "copy",
                "scope": scope_id,
                "source_worktree": payload["source_worktree"],
                "target_worktree": payload["target_worktree"],
                "target_workbench_path": str(target_scope.resolve() / ".workbench"),
                "experimental": True,
                "canonical": False,
                "disposable": True,
                "one_shot": True,
                "sync": False,
            }
            assert secret_body.strip() not in json_result.stdout

    def test_workbench_copy_selector_failure_uses_content_free_workbench_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "repo"
            source.mkdir()
            assert main(["init", str(source)]) == 0
            self._create_same_repo_linked_hierarchy(source)
            secret_selector = "missing-secret-target-body"

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", "iss-00003", "--to", secret_selector, "--json"],
            )

            assert result.returncode == 1, result.stderr
            payload = json.loads(result.stdout)
            self._assert_content_free_error(payload, code="target_not_found", side="target")
            assert secret_selector not in result.stdout + result.stderr

    def test_workbench_copy_invalid_scope_uses_stable_content_free_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "repo"
            source.mkdir()
            assert main(["init", str(source)]) == 0
            self._create_same_repo_linked_hierarchy(source)

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", "init-local-00003", "--to", "missing", "--json"],
            )

            assert result.returncode == 1, result.stderr
            self._assert_content_free_error(json.loads(result.stdout), code="invalid_scope", side=None)

    def test_workbench_copy_reports_no_source_without_changing_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target, scope_id, _, target_scope = self._prepare_linked_worktrees(Path(tmp))
            sentinel = target_scope / ".workbench" / "sentinel.txt"
            sentinel.parent.mkdir()
            sentinel.write_text("target-only\n", encoding="utf-8")

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name, "--json"],
            )

            assert result.returncode == 1, result.stderr
            payload = json.loads(result.stdout)
            self._assert_content_free_error(payload, code="no_source", side="source")
            assert sentinel.read_text(encoding="utf-8") == "target-only\n"

    def test_workbench_copy_accepts_empty_source_workbench(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(Path(tmp))
            (source_scope / ".workbench").mkdir()

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert result.returncode == 0, result.stderr
            assert (target_scope / ".workbench").is_dir()
            assert list((target_scope / ".workbench").iterdir()) == []

    @pytest.mark.parametrize(
        ("side", "kind"), [("source", "file"), ("target", "file"), ("source", "symlink"), ("target", "symlink")]
    )
    def test_workbench_copy_rejects_malformed_roots_without_external_impact(self, side: str, kind: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(root)
            external = root / "external"
            external.mkdir()
            sentinel = external / "sentinel.txt"
            sentinel.write_text("outside\n", encoding="utf-8")
            malformed = (source_scope if side == "source" else target_scope) / ".workbench"
            if kind == "symlink":
                if not self._can_create_symlink(root):
                    pytest.skip("symlink not available")
                malformed.symlink_to(external, target_is_directory=True)
            else:
                malformed.write_text("not a directory\n", encoding="utf-8")
            if side == "target":
                source_workbench = source_scope / ".workbench"
                source_workbench.mkdir()
                (source_workbench / "analysis.txt").write_text("source\n", encoding="utf-8")

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name, "--json"],
            )

            assert result.returncode == 1, result.stderr
            payload = json.loads(result.stdout)
            assert payload["code"] == "invalid_workbench_root"
            assert payload["side"] == side
            assert payload["mutation_started"] is False
            assert sentinel.read_text(encoding="utf-8") == "outside\n"

    def test_workbench_copy_rejects_symlinked_target_specdock_before_external_read_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target, scope_id, source_scope, _ = self._prepare_linked_worktrees(root)
            if not self._can_create_symlink(root):
                pytest.skip("symlink creation is not available on this host")
            source_workbench = source_scope / ".workbench"
            source_workbench.mkdir()
            (source_workbench / "source.txt").write_text("source body\n", encoding="utf-8")
            external_specdock = root / "external-spec-dock"
            (target / "spec-dock").rename(external_specdock)
            sentinel = external_specdock / "external-sentinel.txt"
            sentinel.write_text("external sentinel\n", encoding="utf-8")
            (target / "spec-dock").symlink_to(external_specdock, target_is_directory=True)

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name, "--json"],
            )

            assert result.returncode == 1, result.stderr
            payload = json.loads(result.stdout)
            self._assert_content_free_error(payload, code="unsafe_path", side="target")
            assert sentinel.read_text(encoding="utf-8") == "external sentinel\n"
            assert not any(external_specdock.rglob("source.txt"))

    def test_copied_fake_metadata_adr_and_dependency_remain_opaque_to_runtime_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(Path(tmp))
            source_workbench = source_scope / ".workbench"
            opaque_payloads = {
                "fake-node/.meta.json": b"not valid node metadata\n",
                "decisions/adr-999.md": b"# fake ADR secret body\n",
                "dependency.yml": b"depends_on: [iss-99999]\n",
            }
            for relative, body in opaque_payloads.items():
                path = source_workbench / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)

            copy_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert copy_result.returncode == 0, copy_result.stderr
            assert {
                relative: (target_scope / ".workbench" / relative).read_bytes() for relative in opaque_payloads
            } == (opaque_payloads)
            validate_result = self._run_runtime_capture(target, ["validate"])
            sync_result = self._run_runtime_capture(target, ["sync"])
            deps_result = self._run_runtime_capture(target, ["deps", "check", "--id", scope_id, "--no-github"])
            assert validate_result.returncode == 0, validate_result.stderr
            assert sync_result.returncode == 0, sync_result.stderr
            assert deps_result.returncode == 0, deps_result.stderr
