"""Help and completion come from the same catalog without repository access."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.catalog import HELP_PRECONDITIONS, HELP_SPECS, LEAF_PATHS
from spec_dock.runtime.cli.options import parse_vnext_output
from spec_dock.runtime.cli.vnext_runtime import run_vnext

if TYPE_CHECKING:
    from pathlib import Path


def _run(tmp_path: Path, *args: str):
    return run_vnext(args, invocation_cwd=tmp_path, engine_digest="test-engine", engine_version="0.2.4")


def test_help_uses_catalog_and_does_not_require_project(tmp_path: Path) -> None:
    root = _run(tmp_path, "help")
    assert root.exit_code == 0
    assert "scope" in root.stdout and "installation" in root.stdout
    leaf = _run(tmp_path, "help", "work", "start", "--json")
    assert leaf.exit_code == 0
    assert "--switch-active" in json.loads(leaf.stdout)["data"]["help"]
    missing = _run(tmp_path, "help", "unknown", "--json")
    assert missing.exit_code == 3


def test_each_leaf_has_specific_preconditions_and_example(tmp_path: Path) -> None:
    assert set(HELP_PRECONDITIONS) == set(LEAF_PATHS)
    for leaf in LEAF_PATHS:
        output = _run(tmp_path, "help", *leaf.split(), "--json")
        assert output.exit_code == 0, leaf
        content = json.loads(output.stdout)["data"]["help"]
        assert HELP_PRECONDITIONS[leaf] in content
        assert "Resolve the target in the selected project" not in content
        assert f"spec-dock {leaf}" in content
        words = shlex.split(HELP_SPECS[leaf].examples)
        assert words[0] == "spec-dock"
        parsed = parse_vnext_output(words[1:], engine_version="0.2.4", engine_digest="test-engine")
        assert parsed.namespace is not None, (leaf, parsed.stderr)


def test_help_explains_supported_finish_and_migration_modes(tmp_path: Path) -> None:
    finish = json.loads(_run(tmp_path, "help", "work", "finish", "--json").stdout)["data"]["help"]
    assert "outside the active chain" in finish
    assert "An active Scope must resolve" not in finish

    migrate = json.loads(_run(tmp_path, "help", "workspace", "migrate", "--json").stdout)["data"]["help"]
    assert "--dry-run" in migrate
    assert "without --mapping-file" in migrate
    assert "Applying a migration requires" in migrate


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


def _native_completion(script: str, shell: str, words: list[str]) -> set[str]:
    executable = shutil.which(shell)
    if executable is None:
        pytest.skip(f"native {shell} is unavailable")
    quoted = shlex.join(words)
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
