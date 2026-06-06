import shlex
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestUpdateCommand(CliRuntimeHarness):
    def test_update_help_describes_upstream_no_cache_and_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["update", "--help"])

            assert p.returncode == 0, f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}"
            assert "update" in p.stdout
            assert "uvx --no-cache" in p.stdout
            assert "git+https://github.com/chemitaro/spec-dock" in p.stdout
            assert "current working directory" in p.stdout

    def test_update_runs_uvx_no_cache_with_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            p = self._run_runtime_capture(target, ["update"], env={"PATH": str(bin_dir)})

            assert p.returncode == 0, f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}"
            assert args_log.read_text(encoding="utf-8").splitlines() == [
                    "--no-cache",
                    "--from",
                    "git+https://github.com/chemitaro/spec-dock",
                    "spec-dock",
                    "update",
                    str(target.resolve()),
                ]

    def test_update_passes_explicit_target_to_installer_update(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            managed = root / "managed"
            explicit_target = root / "target-project"
            managed.mkdir()
            explicit_target.mkdir()
            assert main(["init", str(managed)]) == 0
            bin_dir = root / ".test-bin"
            args_log = root / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            p = self._run_runtime_capture(managed, ["update", "../target-project"], env={"PATH": str(bin_dir)})

            assert p.returncode == 0, f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}"
            assert args_log.read_text(encoding="utf-8").splitlines()[-1] == str(explicit_target.resolve())

    def test_update_propagates_subprocess_failure_output_and_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            bin_dir = target / ".test-bin"
            self._make_uvx_stub(bin_dir, stdout="stub stdout", stderr="stub stderr", exit_code=7)

            p = self._run_runtime_capture(target, ["update"], env={"PATH": str(bin_dir)})

            assert p.returncode == 7
            assert "stub stdout" in p.stdout
            assert "stub stderr" in p.stderr

    def test_update_missing_uvx_fails_with_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            empty_bin = target / ".empty-bin"
            empty_bin.mkdir()

            p = self._run_runtime_capture(target, ["update"], env={"PATH": str(empty_bin)})

            assert p.returncode != 0
            assert "uvx could not be executed" in p.stderr
            assert "PATH" in p.stderr

    def test_update_rejects_force_option(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["update", "--force"])

            assert p.returncode != 0
            assert "unrecognized arguments: --force" in p.stderr

    def test_update_rejects_source_and_cache_overrides_without_invoking_uvx(self) -> None:
        cases = (
            (["update", "--from", "git+https://example.invalid/spec-dock"], "--from"),
            (["update", "--cache-dir", ".uv-cache"], "--cache-dir"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            for args, rejected_option in cases:
                args_log.unlink(missing_ok=True)

                p = self._run_runtime_capture(target, args, env={"PATH": str(bin_dir)})

                assert p.returncode != 0
                assert f"unrecognized arguments: {rejected_option}" in p.stderr
                assert not args_log.exists(), "uvx must not be invoked for rejected options"

    def _make_uvx_stub(
        self,
        bin_dir: Path,
        *,
        args_log: Path | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
        exit_code: int = 0,
    ) -> None:
        bin_dir.mkdir(parents=True, exist_ok=True)
        lines = ["#!/bin/sh"]
        if args_log is not None:
            lines.append(f"printf '%s\\n' \"$@\" > {shlex.quote(str(args_log))}")
        if stdout is not None:
            lines.append(f"printf '%s\\n' {shlex.quote(stdout)}")
        if stderr is not None:
            lines.append(f"printf '%s\\n' {shlex.quote(stderr)} >&2")
        lines.append(f"exit {exit_code}")
        uvx_path = bin_dir / "uvx"
        uvx_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        uvx_path.chmod(0o755)
