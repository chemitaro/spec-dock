from pathlib import Path

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestUninstallCommand(CliRuntimeHarness):
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
