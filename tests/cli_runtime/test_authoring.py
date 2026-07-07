from pathlib import Path
import tempfile

import pytest

from tests.cli_runtime.harness import CliRuntimeHarness, main


_DEFERRED_COMMANDS = (
    (["authoring", "preflight", "github-sync"], "authoring preflight github-sync", "iss-00298"),
    (["authoring", "pack", "prepare"], "authoring pack prepare", "iss-00299"),
    (["authoring", "backend", "invoke"], "authoring backend invoke", "iss-00300"),
    (["authoring", "pack", "review"], "authoring pack review", "iss-00301"),
    (["authoring", "pack", "stage"], "authoring pack stage", "iss-00301"),
    (
        ["authoring", "validate", "initiative-epic-candidates"],
        "authoring validate initiative-epic-candidates",
        "iss-00302",
    ),
    (
        ["authoring", "validate", "epic-issue-candidates"],
        "authoring validate epic-issue-candidates",
        "iss-00302",
    ),
    (
        ["authoring", "validate", "issue-draft-adoption"],
        "authoring validate issue-draft-adoption",
        "iss-00303",
    ),
    (
        ["authoring", "validate", "selected-skeleton-fill"],
        "authoring validate selected-skeleton-fill",
        "iss-00303",
    ),
    (["authoring", "approval", "check"], "authoring approval check", "iss-00305"),
)

_FORBIDDEN_AUTHORITY_CLAIMS = (
    "canonical docs",
    ".assurance.json",
    "authorized profile",
    "set-authorized-profile",
    "success",
    "adoption_status",
    "adopted",
    "reviewer pass",
    "execution-ready",
    "pr-ready",
    "merge-ready",
)


class TestAuthoringCli(CliRuntimeHarness):
    def test_authoring_help_exposes_deferred_command_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, ["authoring", "--help"])

            assert p.returncode == 0, p.stdout + p.stderr
            assert "Run deferred ChatGPT authoring helper commands" in p.stdout
            for expected in ("preflight", "pack", "backend", "validate", "approval"):
                assert expected in p.stdout
            for _args, command, _next_issue in _DEFERRED_COMMANDS:
                assert command in p.stdout

    @pytest.mark.parametrize(("args", "command", "next_issue"), _DEFERRED_COMMANDS)
    def test_authoring_deferred_commands_fail_closed_with_stable_diagnostics(
        self, args: list[str], command: str, next_issue: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            assert main(["init", str(target)]) == 0

            p = self._run_runtime_capture(target, args)

            assert p.returncode != 0, p.stdout + p.stderr
            assert f"spec-dock: deferred (authoring) command={command}" in p.stdout
            assert "status=deferred" in p.stdout
            assert "authority=evidence_only" in p.stdout
            assert f"next_issue={next_issue}" in p.stdout
            assert "reason=not_implemented_in_this_issue" in p.stdout

            output = (p.stdout + p.stderr).lower()
            for forbidden in _FORBIDDEN_AUTHORITY_CLAIMS:
                assert forbidden not in output
