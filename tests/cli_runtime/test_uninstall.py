import json
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestUninstallCommand(CliRuntimeHarness):
    def test_removed_spec_purge_is_a_closed_wire_trap_before_target_observation(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        before = {
            path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
        }

        json_result = self._run_runtime_capture(
            target,
            ["uninstall", "--apply", "--remove-specs", "--json"],
            env={"PATH": ""},
        )

        expected = {
            "schema_version": 1,
            "target": str(target),
            "mode": "apply",
            "apply": True,
            "specs_mode": "remove",
            "status": "error",
            "code": "spec-history-purge-removed",
            "operation": None,
            "candidate_digest": None,
            "seed_policy": None,
            "mutation_started": False,
            "bootstrap_rolled_back": False,
            "phase": "request-validation",
            "last_completed_phase": "not-started",
            "retry_command": None,
            "continuation": {
                "next_action": "none",
                "next_command": None,
                "after_cleanup_action": "none",
                "after_cleanup_command": None,
            },
            "failed_paths": [],
            "pending_paths": [],
            "summary": {
                "planned": 0,
                "completed": 0,
                "preserved": 0,
                "pending": 0,
                "failed": 0,
                "warnings": 0,
            },
            "actions": [],
            "guidance": [
                "Use tooling-only uninstall without --remove-specs.",
                "Spec history and Workbench data remain consumer-owned.",
            ],
            "warnings": [],
            "errors": ["Spec history purge has been removed; uninstall is tooling-only."],
        }
        assert json_result.returncode == 2
        assert json_result.stderr == ""
        assert json.loads(json_result.stdout) == expected
        assert json_result.stdout == json.dumps(expected, ensure_ascii=False, separators=(",", ":")) + "\n"

        missing_target = tmp_path / "missing-target"
        text_result = self._run_runtime_capture(
            target,
            ["uninstall", str(missing_target), "--remove-specs"],
            env={"PATH": ""},
        )

        assert text_result.returncode == 2
        assert text_result.stderr == ""
        assert text_result.stdout == (
            f"spec-dock uninstall dry-run for {missing_target}\n"
            "status: error\n"
            "code: spec-history-purge-removed\n"
            "phase: request-validation\n"
            "last-completed-phase: not-started\n"
            "operation: none\n"
            "candidate-digest: none\n"
            "seed-policy: none\n"
            "mutation-started: false\n"
            "bootstrap-rolled-back: false\n"
            "next-action: none\n"
            "next-command: none\n"
            "after-cleanup-action: none\n"
            "after-cleanup-command: none\n"
            "summary: planned=0 completed=0 preserved=0 pending=0 failed=0 warnings=0\n"
            "guidance: Use tooling-only uninstall without --remove-specs.\n"
            "guidance: Spec history and Workbench data remain consumer-owned.\n"
            "error: Spec history purge has been removed; uninstall is tooling-only.\n"
        )
        assert not missing_target.exists()
        assert {
            path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()
        } == before

    def test_uninstall_help_describes_upstream_no_cache_and_default_target(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0

        result = self._run_runtime_capture(target, ["uninstall", "--help"])

        assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        assert "uninstall" in result.stdout
        assert "uvx --no-cache" in result.stdout
        assert "git+https://github.com/chemitaro/spec-dock" in result.stdout
        assert "current working directory" in result.stdout

    def test_uninstall_rejects_unsupported_options(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0

        for args, rejected_option in (
            (["uninstall", "--from", "git+https://example.invalid/spec-dock"], "--from"),
            (["uninstall", "--cache-dir", ".uv-cache"], "--cache-dir"),
        ):
            result = self._run_runtime_capture(target, args)
            assert result.returncode != 0
            assert f"unrecognized arguments: {rejected_option}" in result.stderr
