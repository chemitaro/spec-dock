import shlex
import tempfile
from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class UninstallCommandTests(CliRuntimeHarness):
    def test_uninstall_help_describes_upstream_no_cache_and_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            p = self._run_runtime_capture(target, ["uninstall", "--help"])

            self.assertEqual(p.returncode, 0, msg=f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
            self.assertIn("uninstall", p.stdout)
            self.assertIn("uvx --no-cache", p.stdout)
            self.assertIn("git+https://github.com/chemitaro/spec-dock", p.stdout)
            self.assertIn("current working directory", p.stdout)

    def test_uninstall_runs_uvx_no_cache_with_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            p = self._run_runtime_capture(target, ["uninstall"], env={"PATH": str(bin_dir)})

            self.assertEqual(p.returncode, 0, msg=f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
            self.assertEqual(
                args_log.read_text(encoding="utf-8").splitlines(),
                [
                    "--no-cache",
                    "--from",
                    "git+https://github.com/chemitaro/spec-dock",
                    "spec-dock",
                    "uninstall",
                    str(target.resolve()),
                ],
            )

    def test_uninstall_passes_explicit_target_to_installer_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            managed = root / "managed"
            explicit_target = root / "target-project"
            managed.mkdir()
            explicit_target.mkdir()
            self.assertEqual(main(["init", str(managed)]), 0)
            bin_dir = root / ".test-bin"
            args_log = root / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            p = self._run_runtime_capture(managed, ["uninstall", "../target-project"], env={"PATH": str(bin_dir)})

            self.assertEqual(p.returncode, 0, msg=f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
            self.assertEqual(args_log.read_text(encoding="utf-8").splitlines()[-1], str(explicit_target.resolve()))

    def test_uninstall_forwards_apply_keep_specs_and_propagates_failure_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log, stdout="stub stdout", stderr="stub stderr", exit_code=7)

            p = self._run_runtime_capture(
                target,
                ["uninstall", "--apply", "--keep-specs"],
                env={"PATH": str(bin_dir)},
            )

            self.assertEqual(p.returncode, 7)
            self.assertIn("stub stdout", p.stdout)
            self.assertIn("stub stderr", p.stderr)
            self.assertEqual(
                args_log.read_text(encoding="utf-8").splitlines()[-3:],
                [str(target.resolve()), "--apply", "--keep-specs"],
            )

    def test_uninstall_forwards_remove_specs_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            p = self._run_runtime_capture(target, ["uninstall", "--remove-specs"], env={"PATH": str(bin_dir)})

            self.assertEqual(p.returncode, 0, msg=f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
            self.assertEqual(
                args_log.read_text(encoding="utf-8").splitlines()[-2:],
                [str(target.resolve()), "--remove-specs"],
            )

    def test_uninstall_forwards_json_and_preserves_json_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            json_stdout = '{"schema_version":1,"status":"completed"}'
            self._make_uvx_stub(bin_dir, args_log=args_log, stdout=json_stdout)

            p = self._run_runtime_capture(
                target,
                ["uninstall", "--json", "--apply", "--keep-specs"],
                env={"PATH": str(bin_dir)},
            )

            self.assertEqual(p.returncode, 0, msg=f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
            self.assertEqual(p.stdout, json_stdout + "\n")
            self.assertEqual(
                args_log.read_text(encoding="utf-8").splitlines()[-4:],
                [str(target.resolve()), "--apply", "--keep-specs", "--json"],
            )

    def test_uninstall_missing_uvx_fails_with_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            empty_bin = target / ".empty-bin"
            empty_bin.mkdir()

            p = self._run_runtime_capture(target, ["uninstall"], env={"PATH": str(empty_bin)})

            self.assertEqual(p.returncode, 127)
            self.assertIn("uvx could not be executed", p.stderr)
            self.assertIn("PATH", p.stderr)

    def test_uninstall_rejects_source_and_cache_overrides_without_invoking_uvx(self) -> None:
        cases = (
            (["uninstall", "--from", "git+https://example.invalid/spec-dock"], "--from"),
            (["uninstall", "--cache-dir", ".uv-cache"], "--cache-dir"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            bin_dir = target / ".test-bin"
            args_log = target / "uvx-args.txt"
            self._make_uvx_stub(bin_dir, args_log=args_log)

            for args, rejected_option in cases:
                with self.subTest(args=args):
                    args_log.unlink(missing_ok=True)

                    p = self._run_runtime_capture(target, args, env={"PATH": str(bin_dir)})

                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn(f"unrecognized arguments: {rejected_option}", p.stderr)
                    self.assertFalse(args_log.exists(), "uvx must not be invoked for rejected options")

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
