"""Help and completion come from the same catalog without repository access."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
import io
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.catalog import HELP_PRECONDITIONS, HELP_SPECS, LEAF_PATHS
from spec_dock.runtime.cli.options import parse_vnext

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class _ConsoleOutput:
    exit_code: int
    stdout: str
    stderr: str


def _run(tmp_path: Path, *args: str) -> _ConsoleOutput:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(["--project", str(tmp_path / "missing"), *args])
    return _ConsoleOutput(code, stdout.getvalue(), stderr.getvalue())


def test_public_migration_help_does_not_advertise_retired_journal_options(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before = tuple(tmp_path.iterdir())
    assert main(["--project", str(tmp_path / "missing"), "help", "workspace", "migrate", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["kind"] == "utility" and result["effects"] == []
    text = result["data"]["text"]
    assert "--backup-dir" in text and "--confirm-old-writers-stopped" in text
    assert "--resume" not in text and "--rollback" not in text
    assert tuple(tmp_path.iterdir()) == before


def test_help_uses_catalog_and_does_not_require_project(tmp_path: Path) -> None:
    root = _run(tmp_path, "help")
    assert root.exit_code == 0
    assert "scope" in root.stdout and "installation" in root.stdout
    leaf = _run(tmp_path, "help", "work", "start", "--json")
    assert leaf.exit_code == 0
    assert "--switch-active" in json.loads(leaf.stdout)["data"]["text"]
    missing = _run(tmp_path, "help", "unknown", "--json")
    assert missing.exit_code == 2


def test_each_leaf_has_specific_preconditions_and_example(tmp_path: Path) -> None:
    assert set(HELP_PRECONDITIONS) == set(LEAF_PATHS)
    for leaf in LEAF_PATHS:
        output = _run(tmp_path, "help", *leaf.split(), "--json")
        assert output.exit_code == 0, leaf
        content = json.loads(output.stdout)["data"]["text"]
        syntax = content.split("\nTarget:\n", 1)[0]
        assert "--resume" not in syntax and "--rollback" not in syntax
        assert HELP_PRECONDITIONS[leaf] in content
        assert "Resolve the target in the selected project" not in content
        assert f"spec-dock {leaf}" in content
        words = shlex.split(HELP_SPECS[leaf].examples)
        assert words[0] == "spec-dock"
        parsed = parse_vnext(words[1:])
        assert parsed.command_path == leaf, leaf


def test_help_explains_supported_finish_and_migration_modes(tmp_path: Path) -> None:
    finish = json.loads(_run(tmp_path, "help", "work", "finish", "--json").stdout)["data"]["text"]
    assert "outside the active chain" in finish
    assert "An active Scope must resolve" not in finish
    assert "confirmed completed" in finish and "captured direct record" in finish
    assert "current branch" in finish and "no Start lock" in finish
    assert "selected subtree" not in finish and "canonical branch" not in finish and "derived state" not in finish

    migrate = json.loads(_run(tmp_path, "help", "workspace", "migrate", "--json").stdout)["data"]["text"]
    assert "--dry-run" in migrate
    assert "--to-writer-protocol" in migrate and "--confirm-old-writers-stopped" in migrate
    assert "--mapping-file" not in migrate and "--resume OPERATION_ID" not in migrate
    assert "restore verification" in migrate and "human operational confirmation" in migrate


def test_completions_include_every_catalog_leaf_without_writing_files(tmp_path: Path) -> None:
    before = tuple(tmp_path.iterdir())
    for shell in ("bash", "zsh", "fish"):
        output = _run(tmp_path, "completion", shell)
        assert output.exit_code == 0
        assert "spec-dock" in output.stdout
        for leaf in LEAF_PATHS:
            assert leaf.split()[0] in output.stdout
        executable = shutil.which(shell) if shell in ("bash", "zsh") else None
        if executable is not None:
            syntax = subprocess.run(
                [executable, "-n"], input=output.stdout, text=True, capture_output=True, check=False
            )
            assert syntax.returncode == 0, syntax.stderr
    assert tuple(tmp_path.iterdir()) == before


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_native_completion_keeps_leaf_options_after_scope_operands(
    capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    assert main(["completion", shell]) == 0
    script = capsys.readouterr().out
    choices = _native_completion(script, shell, ["spec-dock", "scope", "show", "gh:example/repo#1", ""])
    assert {"--expect-current", "--expect-backend", "--json"} <= choices


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_native_migration_completion_omits_retired_journal_options(
    capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    assert main(["completion", shell]) == 0
    script = capsys.readouterr().out
    choices = _native_completion(script, shell, ["spec-dock", "workspace", "migrate", ""])
    assert {"--to-schema", "--to-writer-protocol", "--backup-dir"} <= choices
    assert not {"--resume", "--rollback"} & choices


def _native_completion(script: str, shell: str, words: list[str]) -> set[str]:
    executable = shutil.which(shell)
    if executable is None:
        pytest.skip(f"native {shell} is unavailable")
    assert executable is not None
    quoted = shlex.join(words)
    if shell == "fish":
        line = shlex.join(words[:-1]) + " " + words[-1]
        with tempfile.TemporaryDirectory() as home:
            completed = subprocess.run(
                [executable, "--no-config"],
                input="set -g fish_complete_path\n" + script + "\ncomplete -C " + shlex.quote(line) + "\n",
                env=dict(os.environ, HOME=home, XDG_CONFIG_HOME=home, XDG_DATA_HOME=home, XDG_CACHE_HOME=home),
                cwd=home,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        assert completed.returncode == 0, completed.stderr
        return {line.split("\t", 1)[0] for line in completed.stdout.splitlines()}
    if shell == "bash":
        harness = (
            f"COMP_WORDS=({quoted})\nCOMP_CWORD={len(words) - 1}\n"
            "_spec_dock_complete\nprintf '%s\\n' \"${COMPREPLY[@]}\"\n"
        )
        setup = ""
    else:
        setup = "compdef() { :; }\ncompadd() { shift; printf '%s\\n' \"$@\"; }\n"
        harness = f"words=({quoted})\nCURRENT={len(words)}\n_spec_dock_complete\n"
    completed = subprocess.run(
        [executable, "-f"], input=setup + script + harness, text=True, capture_output=True, check=False, timeout=5
    )
    assert completed.returncode == 0, completed.stderr
    return set(completed.stdout.split())


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_native_completion_skips_common_option_values_before_the_command_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    before = tuple(tmp_path.iterdir())
    assert main(["--project", str(tmp_path / "not-a-repository"), "completion", shell]) == 0
    script = capsys.readouterr().out
    choices = _native_completion(script, shell, ["spec-dock", "--project", "/not a repository", "scope", ""])
    assert {"show", "create", "import", "list"} <= choices
    assert tuple(tmp_path.iterdir()) == before


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_native_completion_does_not_offer_command_options_for_a_required_leaf_value(
    capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    assert main(["completion", shell]) == 0
    script = capsys.readouterr().out
    choices = _native_completion(script, shell, ["spec-dock", "artifact", "create", "--scope", "@root", "--title", ""])
    assert choices == set()


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_native_completion_treats_words_after_double_dash_as_operands(
    capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    assert main(["completion", shell]) == 0
    script = capsys.readouterr().out
    choices = _native_completion(
        script, shell, ["spec-dock", "artifact", "import", "file", "--scope", "@root", "--", "--scope", ""]
    )
    assert {"--scope", "--json"} <= choices


@pytest.mark.parametrize("shell", ["bash", "zsh"])
@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["spec-dock", "--project=/not/git", "scope", ""], {"show", "create"}),
        (["spec-dock", "scope", "--timeout", "5", "show", "init-00001", "--json", ""], {"--color"}),
        (["spec-dock", "artifact", "import", "file", "/source with spaces", "--scope", "@root", ""], {"--scope"}),
        (
            ["spec-dock", "work", "start", "iss-00003", "--branch", "scope", "--base", "HEAD", "--switch-active", ""],
            {"--base"},
        ),
        (["spec-dock", "branch", "show", "@current", "--name=scope", ""], {"--name"}),
        (["spec-dock", "--project", ""], set()),
        (["spec-dock", "scop", ""], set()),
    ],
)
def test_native_completion_handles_inline_values_flags_and_command_depth(
    capsys: pytest.CaptureFixture[str], shell: str, words: list[str], expected: set[str]
) -> None:
    assert main(["completion", shell]) == 0
    choices = _native_completion(capsys.readouterr().out, shell, words)
    assert expected <= choices if expected else choices == set()


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_every_leaf_completion_matches_yes_and_lock_acceptance(tmp_path: Path, shell: str) -> None:
    import re

    readonly = {
        "scope list",
        "scope show",
        "active show",
        "branch show",
        "dependency list",
        "dependency check",
        "artifact list",
        "artifact show",
        "worktree list",
        "worktree show",
        "help",
        "completion",
        "workspace validate",
        "workspace sync",
        "workspace doctor",
        "installation show",
    }
    output = _run(tmp_path, "completion", shell)
    assert output.exit_code == 0
    assert len(LEAF_PATHS) == 44 and readonly <= set(LEAF_PATHS)
    for leaf in LEAF_PATHS:
        if shell == "fish":
            # Public registration lines belonging to this exact command path.
            lines = [line for line in output.stdout.splitlines() if f'__spec_dock_path_is "{leaf}"' in line]
            choices = set()
            for line in lines:
                words = shlex.split(line)
                if "-a" in words:
                    choices.update(words[words.index("-a") + 1].split())
                if "-l" in words:
                    choices.add("--" + words[words.index("-l") + 1])
                if "-s" in words:
                    choices.add("-" + words[words.index("-s") + 1])
        else:
            matched = re.search(r'"' + re.escape(leaf) + r'"\) choices="([^"]*)"', output.stdout)
            assert matched is not None, leaf
            choices = set(matched[1].split())
        assert {"--json", "--project", "--help"} <= choices, (shell, leaf)
        assert ("--yes" in choices) == (leaf not in readonly), (shell, leaf, choices)
        assert ("-y" in choices) == (leaf not in readonly), (shell, leaf, choices)
        assert ("--lock-timeout" in choices) == (leaf == "work start"), (shell, leaf, choices)


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
@pytest.mark.parametrize(
    "words,required,forbidden",
    [
        (["scope", "list", "--"], {"--json"}, {"--yes", "--lock-timeout"}),
        (["scope", "list", "-"], {"--json"}, {"--yes", "-y", "--lock-timeout"}),
        (["active", "show", "--"], {"--json"}, {"--yes", "--lock-timeout"}),
        (["work", "start", "iss-00003", "--"], {"--yes", "--lock-timeout", "--base"}, set()),
        (["scope", "create", "initiative", "--"], {"--yes", "--title"}, {"--lock-timeout"}),
        (["--project", "/not a repository", "scope", "list", "--"], {"--json"}, {"--yes", "--lock-timeout"}),
        (["--project=/not/git", "scope", "list", "--"], {"--json"}, {"--yes", "--lock-timeout"}),
    ],
)
def test_native_completion_only_offers_applicable_options(
    capsys: pytest.CaptureFixture[str], shell: str, words: list[str], required: set[str], forbidden: set[str]
) -> None:
    assert main(["completion", shell]) == 0
    choices = _native_completion(capsys.readouterr().out, shell, ["spec-dock", *words])
    assert required <= choices
    assert not forbidden & choices
