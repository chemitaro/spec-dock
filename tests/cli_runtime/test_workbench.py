import hashlib
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

    def _prepare_linked_worktrees(
        self,
        root: Path,
        *,
        source_workbench_payloads: dict[str, bytes] | None = None,
        rename_target_scope: bool = True,
    ) -> tuple[Path, Path, str, Path, Path]:
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

        source_meta = next(
            path
            for path in (source / "spec-dock" / "initiatives").rglob(".meta.json")
            if json.loads(path.read_text(encoding="utf-8"))["type"] == "issue"
        )
        scope_id = json.loads(source_meta.read_text(encoding="utf-8"))["id"]
        source_scope = source_meta.parent
        for relative, body in (source_workbench_payloads or {}).items():
            payload_path = source_scope / ".workbench" / relative
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload_path.write_bytes(body)

        self._run_git(source, ["worktree", "add", "-b", "target", str(target)])

        target_meta = next(
            path
            for path in (target / "spec-dock" / "initiatives").rglob(".meta.json")
            if json.loads(path.read_text(encoding="utf-8"))["id"] == scope_id
        )
        target_scope = target_meta.parent
        if rename_target_scope:
            renamed_target_scope = target_scope.with_name(f"{scope_id}-target-side-renamed")
            target_scope.rename(renamed_target_scope)
            target_scope = renamed_target_scope

        return source, target, scope_id, source_scope, target_scope

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
            source_file.parent.mkdir(exist_ok=True)
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
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(Path(tmp))
            shutil.rmtree(source_scope / ".workbench")
            sentinel = target_scope / ".workbench" / "sentinel.txt"
            sentinel.parent.mkdir(exist_ok=True)
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
            source_workbench = source_scope / ".workbench"
            target_workbench = target_scope / ".workbench"
            (source_workbench / "README.md").unlink()
            shutil.rmtree(target_workbench)
            assert source_workbench.exists()
            assert source_workbench.is_dir()
            assert list(source_workbench.iterdir()) == []
            assert not target_workbench.exists()

            result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert result.returncode == 0, result.stderr
            assert target_workbench.is_dir()
            assert list(target_workbench.iterdir()) == []

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
            shutil.rmtree(malformed)
            if kind == "symlink":
                if not self._can_create_symlink(root):
                    pytest.skip("symlink not available")
                malformed.symlink_to(external, target_is_directory=True)
            else:
                malformed.write_text("not a directory\n", encoding="utf-8")
            if side == "target":
                source_workbench = source_scope / ".workbench"
                source_workbench.mkdir(exist_ok=True)
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

    def test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            opaque_payloads = {
                "fake-node/.meta.json": b"not valid node metadata\n",
                "legacy/meta.json": b"not valid legacy metadata\n",
                "decisions/adr-999.md": b"# fake ADR secret body\n",
                "notes.md": b"# ordinary Markdown notes\n",
                "dependency.yml": b"depends_on: [iss-99999]\n",
                "binary.bin": b"\x00\x01\x02\xff",
                "invalid-utf8.bin": b"\xff\xfe\x80",
            }
            source, target, scope_id, _, target_scope = self._prepare_linked_worktrees(
                Path(tmp),
                source_workbench_payloads=opaque_payloads,
                rename_target_scope=False,
            )

            def observe() -> tuple[tuple[int, int, int, int], tuple[tuple[str, str], ...], tuple[str, ...]]:
                validate_result = self._run_runtime_capture(target, ["validate"])
                sync_result = self._run_runtime_capture(target, ["sync"])
                deps_result = self._run_runtime_capture(target, ["deps", "check", "--id", scope_id, "--no-github"])
                active_result = self._run_runtime_capture(target, ["active", "set", "--id", scope_id, "--force"])
                active = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
                active_fields = tuple(
                    (key, active[key][field]) for key in ("initiative", "epic", "issue") for field in ("id", "path")
                )
                index_all = json.loads((target / "spec-dock" / ".agent" / "index-all.json").read_text(encoding="utf-8"))
                return (
                    (
                        validate_result.returncode,
                        sync_result.returncode,
                        deps_result.returncode,
                        active_result.returncode,
                    ),
                    active_fields,
                    tuple(sorted(index_all["nodes"])),
                )

            baseline = observe()

            copy_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert copy_result.returncode == 0, copy_result.stderr
            assert {
                relative: (target_scope / ".workbench" / relative).read_bytes() for relative in opaque_payloads
            } == (opaque_payloads)
            assert (target_scope / ".workbench" / "README.md").is_file()
            assert observe() == baseline

    def test_linked_worktree_checkout_and_manual_copy_preserve_identical_readme_and_move_only_ignored_payload(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payloads = {"notes/opaque.bin": b"\x00opaque\xff\n"}
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(
                Path(tmp),
                source_workbench_payloads=payloads,
                rename_target_scope=False,
            )
            source_workbench = source_scope / ".workbench"
            target_workbench = target_scope / ".workbench"
            target_readme = target_workbench / "README.md"
            source_payload = source_workbench / "notes" / "opaque.bin"
            target_payload = target_workbench / "notes" / "opaque.bin"

            def inventory(workbench: Path) -> dict[str, str]:
                return {
                    path.relative_to(workbench).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in workbench.rglob("*")
                    if path.is_file()
                }

            source_before = inventory(source_workbench)
            target_before = inventory(target_workbench)
            readme_rel = target_readme.relative_to(target).as_posix()
            source_payload_rel = source_payload.relative_to(source).as_posix()
            target_payload_rel = target_payload.relative_to(target).as_posix()

            assert set(source_before) == {"README.md", "notes/opaque.bin"}
            assert set(target_before) == {"README.md"}
            assert source_before["README.md"] == target_before["README.md"]
            assert not target_payload.exists()
            assert self._run_git(target, ["ls-files", "--error-unmatch", "--", readme_rel], check=False).returncode == 0
            assert self._run_git(source, ["check-ignore", "-q", "--", source_payload_rel], check=False).returncode == 0
            assert self._run_git(target, ["diff", "--quiet", "--", readme_rel], check=False).returncode == 0
            assert self._run_git(target, ["diff", "--cached", "--quiet", "--", readme_rel], check=False).returncode == 0

            copy_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert copy_result.returncode == 0, copy_result.stderr
            target_after = inventory(target_workbench)
            assert set(target_after) == {"README.md", "notes/opaque.bin"}
            assert target_after["README.md"] == target_before["README.md"] == source_before["README.md"]
            assert target_after["notes/opaque.bin"] == source_before["notes/opaque.bin"]
            assert self._run_git(target, ["check-ignore", "-q", "--", target_payload_rel], check=False).returncode == 0
            assert self._run_git(target, ["diff", "--quiet", "--", readme_rel], check=False).returncode == 0
            assert self._run_git(target, ["diff", "--cached", "--quiet", "--", readme_rel], check=False).returncode == 0

    def test_workbench_copy_preserves_opaque_source_wins_for_divergent_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target, scope_id, source_scope, target_scope = self._prepare_linked_worktrees(
                Path(tmp),
                rename_target_scope=False,
            )
            source_readme = source_scope / ".workbench" / "README.md"
            target_readme = target_scope / ".workbench" / "README.md"
            source_readme.write_bytes(b"# Source Workbench\n")
            target_readme.write_bytes(b"# Target Workbench\n")
            source_before = hashlib.sha256(source_readme.read_bytes()).hexdigest()
            target_before = hashlib.sha256(target_readme.read_bytes()).hexdigest()
            assert source_before != target_before

            copy_result = self._run_runtime_capture(
                source,
                ["workbench", "copy", "--scope", scope_id, "--to", target.name],
            )

            assert copy_result.returncode == 0, copy_result.stderr
            target_after = hashlib.sha256(target_readme.read_bytes()).hexdigest()
            assert target_after == source_before
            assert target_after != target_before
