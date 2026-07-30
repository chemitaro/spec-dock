import json
from pathlib import Path
import subprocess
import sys
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestArtifactImportFile(CliRuntimeHarness):
    def _write_runtime_clock(self, target: Path) -> None:
        runtime_clock = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "clock.py"
        runtime_clock.write_text(
            (
                "from __future__ import annotations\n\n"
                "def now_iso() -> str:\n    return '2026-07-30T01:02:03+00:00'\n\n"
                "def today() -> str:\n    return '2026-07-30'\n"
            ),
            encoding="utf-8",
        )

    def test_help_has_only_generic_file_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            completed = self._run_runtime_capture(target, ["artifact", "import", "file", "--help"])
            assert completed.returncode == 0
            for required in ("--file", "--root", "--initiative", "--epic", "--issue", "--json"):
                assert required in completed.stdout
            for forbidden in ("--title", "--slug", "--mime", "--encoding", "--move", "--overwrite"):
                assert forbidden not in completed.stdout

    def test_zero_or_multiple_target_is_parser_error_without_source_or_setup_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            source = target / "source.bin"
            body = b"parser must reject before runtime dispatch"
            source.write_bytes(body)
            commands = (
                ["artifact", "import", "file", "--file", source.name],
                [
                    "artifact",
                    "import",
                    "file",
                    "--root",
                    "--issue",
                    "345",
                    "--file",
                    source.name,
                ],
            )

            for command in commands:
                completed = self._run_runtime_capture(target, command)
                assert completed.returncode == 2
                assert source.read_bytes() == body
                assert not (target / "spec-dock" / "artifacts").exists()

    def test_missing_or_kind_mismatched_target_is_rejected_without_setup_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=301,
                epic_issue_number=312,
                issue_issue_number=345,
            )
            source = target / "source.bin"
            body = b"target guard must precede source open"
            source.write_bytes(body)
            specdock_dir = target / "spec-dock"

            def setup_snapshot() -> tuple[tuple[str, str], ...]:
                snapshot = []
                for path in specdock_dir.rglob("*"):
                    if "artifacts" not in path.parts:
                        continue
                    relative = path.relative_to(specdock_dir).as_posix()
                    if path.is_symlink():
                        snapshot.append((relative, f"symlink:{path.readlink()}"))
                    elif path.is_dir():
                        snapshot.append((relative, "directory"))
                    else:
                        snapshot.append((relative, f"file:{path.read_bytes()!r}"))
                return tuple(sorted(snapshot))

            before = setup_snapshot()
            commands = (
                ["artifact", "import", "file", "--issue", "999", "--file", source.name, "--json"],
                [
                    "artifact",
                    "import",
                    "file",
                    "--issue",
                    "init-00301",
                    "--file",
                    source.name,
                    "--json",
                ],
            )
            for command in commands:
                completed = self._run_runtime_capture(target, command)
                assert completed.returncode == 1
                assert json.loads(completed.stdout)["code"] == "target_invalid"
                assert source.read_bytes() == body
                assert setup_snapshot() == before

    def test_root_initiative_epic_issue_target_matrix_preserves_opaque_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            self._create_same_repo_linked_hierarchy(
                target,
                initiative_issue_number=301,
                epic_issue_number=312,
                issue_issue_number=345,
                initiative_title="Architecture",
                epic_title="Explicit import",
                issue_title="Generic file",
            )
            self._write_runtime_clock(target)
            specdock_dir = target / "spec-dock"
            meta_before = {
                path.relative_to(specdock_dir).as_posix(): path.read_bytes()
                for path in specdock_dir.rglob(".meta.json")
            }
            deps_path = specdock_dir / ".agent" / "deps-issues.json"
            deps_before = json.loads(deps_path.read_text(encoding="utf-8"))

            targets = (
                ("root", None, "root"),
                ("initiative", "301", "init-00301"),
                ("epic", "312", "epic-00312"),
                ("issue", "345", "iss-00345"),
            )
            for index, (kind, value, expected_id) in enumerate(targets):
                source = target / f"opaque-{index}.bin"
                body = b"\x00\xffopaque-" + bytes([index])
                source.write_bytes(body)
                command = ["artifact", "import", "file", f"--{kind}"]
                if value is not None:
                    command.append(value)
                command.extend(["--file", source.name, "--json"])
                completed = self._run_runtime_capture(target, command)
                assert completed.returncode == 0, completed.stdout + completed.stderr
                payload = json.loads(completed.stdout)
                assert payload["target_kind"] == kind
                assert payload["target_id"] == expected_id
                assert payload["artifact_id"] == f"20260730t010203z--{source.name}"
                assert payload["canonical"] is False
                assert "sha256" not in payload
                assert "byte_count" not in payload
                destination = target / payload["destination"]
                assert destination.read_bytes() == body
                assert source.read_bytes() == body
                if kind == "root":
                    meta_after = {
                        path.relative_to(specdock_dir).as_posix(): path.read_bytes()
                        for path in specdock_dir.rglob(".meta.json")
                    }
                    deps_after = json.loads(deps_path.read_text(encoding="utf-8"))
                    assert len(meta_after) == len(meta_before)
                    assert meta_after == meta_before
                    assert deps_after == deps_before

            assert not (target / "spec-dock" / ".meta.json").exists()

    def test_external_relative_source_from_nested_cwd_is_basename_only_and_content_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "repo"
            target.mkdir()
            assert main(["init", str(target)]) == 0
            self._write_runtime_clock(target)
            private_parent = base / "private-parent-sentinel"
            private_parent.mkdir()
            source = private_parent / "visible.bin"
            body = b"body-hash-count-sentinel\x00\xff"
            source.write_bytes(body)
            nested_cwd = target / "nested" / "cwd"
            nested_cwd.mkdir(parents=True)
            script = target / "spec-dock" / "scripts" / "spec-dock"
            env = self._runtime_env(target, None)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "artifact",
                    "import",
                    "file",
                    "--root",
                    "--file",
                    "../private-parent-sentinel/visible.bin",
                    "--json",
                ],
                cwd=nested_cwd,
                env=env,
                capture_output=True,
                text=True,
            )

            assert completed.returncode == 0, completed.stdout + completed.stderr
            payload = json.loads(completed.stdout)
            assert payload["source_visibility"] == "basename_only"
            assert payload["source"] == "visible.bin"
            assert private_parent.name not in completed.stdout
            assert "body-hash-count-sentinel" not in completed.stdout
            assert "sha256" not in completed.stdout.lower()
            assert "byte_count" not in completed.stdout.lower()
            assert (target / payload["destination"]).read_bytes() == body
            assert source.read_bytes() == body
