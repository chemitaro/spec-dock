"""Public CLI inventory for the coordinated vNext cutover."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spec_dock import __version__
from spec_dock.cli import main
from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.cli.legacy import LegacyCommandError
from spec_dock.runtime.cli.options import explicit_help, parse_vnext


def test_vnext_catalog_matches_approved_44_leaf_design() -> None:
    expected = {
        "scope create initiative",
        "scope create epic",
        "scope create issue",
        "scope import github initiative",
        "scope import github epic",
        "scope import github issue",
        "scope list",
        "scope show",
        "scope edit",
        "scope close",
        "scope reopen",
        "scope delete",
        "active show",
        "active set",
        "active clear",
        "work start",
        "work finish",
        "branch show",
        "branch create",
        "branch switch",
        "dependency list",
        "dependency check",
        "dependency add",
        "dependency remove",
        "artifact create",
        "artifact import file",
        "artifact list",
        "artifact show",
        "worktree create",
        "worktree list",
        "worktree show",
        "worktree remove",
        "worktree bootstrap",
        "workbench copy",
        "workspace sync",
        "workspace validate",
        "workspace doctor",
        "workspace migrate",
        "installation show",
        "installation init",
        "installation update",
        "installation uninstall",
        "help",
        "completion",
    }
    assert len(LEAF_PATHS) == 44
    assert set(LEAF_PATHS) == expected


def test_every_vnext_leaf_has_parseable_help() -> None:
    for path in LEAF_PATHS:
        try:
            parse_vnext([*path.split(), "--help"])
        except SystemExit as exc:
            assert exc.code == 0, path
        else:
            raise AssertionError(f"help did not exit: {path}")


def test_every_leaf_help_names_its_effects_and_recovery(capsys: pytest.CaptureFixture[str]) -> None:
    headings = (
        "Target:",
        "Reads:",
        "Writes:",
        "Does not:",
        "Preconditions:",
        "Confirmation:",
        "Recovery:",
        "JSON:",
        "Examples:",
    )
    for path in LEAF_PATHS:
        text = explicit_help(path.split())
        assert "Effects:" in text, path
        for heading in headings:
            assert heading in text, (path, heading)
        assert main([*path.split(), "--help", "--json"]) == 0
        output = capsys.readouterr()
        payload = json.loads(output.out)
        assert not output.err and payload["schema_version"] == "specdock.cli/v2"
        assert payload["data"]["kind"] == "utility" and payload["effects"] == []
        assert payload["data"]["text"] == text, path
    work_start = explicit_help(("work", "start"))
    assert "branch" in work_start and "checkout" in work_start
    assert "--resume" not in work_start
    assert "--allow-stale" not in work_start
    assert "spec-dock work start <scope-id> --base HEAD" in work_start


def test_help_examples_include_required_runtime_inputs_once() -> None:
    worktree_help = explicit_help(("worktree", "create"))
    worktree_example = worktree_help.split("Examples:\n", 1)[1].splitlines()[0]
    assert worktree_example.count("--base") == 1

    migration_help = explicit_help(("workspace", "migrate"))
    migration_example = migration_help.split("Examples:\n", 1)[1].splitlines()[0]
    for option in ("--to-schema", "--to-writer-protocol", "--backup-dir", "--confirm-old-writers-stopped"):
        assert migration_example.count(option) == 1
    assert "--mapping-file" not in migration_help


def test_repository_operator_guidance_uses_current_cli() -> None:
    guidance = (Path(__file__).resolve().parents[2] / "AGENTS.md").read_text(encoding="utf-8")
    for command in ("work start/finish", "scope create/import", "installation update", "workspace validate"):
        assert command in guidance
    for retired in ("issue start", "issue finish", "uninstall --apply", "spec-dock update ."):
        assert retired not in guidance


def test_common_options_are_accepted_before_or_after_leaf() -> None:
    first = parse_vnext(["--json", "scope", "show", "iss-00409"])
    last = parse_vnext(["scope", "show", "iss-00409", "--json"])
    assert first.command_path == last.command_path == "scope show"
    assert first.target == last.target == "iss-00409"
    assert first.json is last.json is True


def test_scope_create_requires_explicit_backend_parent_and_title() -> None:
    with pytest.raises(SystemExit) as missing:
        parse_vnext(["scope", "create", "epic", "--title", "Roadmap"])
    assert missing.value.code == 2
    result = parse_vnext([
        "scope",
        "create",
        "epic",
        "--backend",
        "github",
        "--parent",
        "init-local-00001",
        "--title",
        "Roadmap",
    ])
    assert result.backend == "github"
    assert result.parent == "init-local-00001"


def test_installation_rejects_the_retired_pin_and_journal_route(capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        main([
            "installation",
            "update",
            "--commit",
            "a" * 40,
            "--rollback",
            "b" * 32,
            "--json",
        ])
        == 2
    )
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert not output.err and payload["error"]["code"] == "ARGUMENT_RETIRED"
    assert payload["effects"] == []


def test_active_clear_requires_explicit_target_or_all() -> None:
    with pytest.raises(SystemExit) as missing:
        parse_vnext(["active", "clear"])
    assert missing.value.code == 2
    result = parse_vnext(["active", "clear", "--from", "@epic"])
    assert result.from_target == "@epic"


def test_double_dash_keeps_option_like_artifact_source_positional() -> None:
    result = parse_vnext(["artifact", "import", "file", "--scope", "@issue", "--", "--json"])
    assert result.path == "--json"
    assert result.json is False


def test_common_options_normalize_equal_duplicates_and_reject_conflicts() -> None:
    parsed = parse_vnext(["--project", "/tmp/project", "scope", "show", "iss-00409", "--project", "/tmp/project"])
    assert parsed.project == "/tmp/project"
    with pytest.raises(SystemExit) as conflict:
        parse_vnext(["--project", "/tmp/a", "scope", "show", "iss-00409", "--project", "/tmp/b"])
    assert conflict.value.code == 2


@pytest.mark.parametrize(
    ("legacy", "replacement"),
    [
        (["issue", "start", "iss-00409"], "work start"),
        (["delete", "iss-00409"], "scope delete"),
        (["deps", "check", "iss-00409"], "dependency check"),
    ],
)
def test_removed_legacy_roots_are_tombstones(legacy: list[str], replacement: str) -> None:
    with pytest.raises(LegacyCommandError) as removed:
        parse_vnext(legacy)
    assert removed.value.code == 2
    assert removed.value.error_code == "LEGACY_COMMAND_REMOVED"
    assert replacement in str(removed.value)


def test_approved_defaults_are_explicit_in_parsed_request() -> None:
    assert parse_vnext(["scope", "close", "iss-00409"]).reason == "completed"
    assert parse_vnext(["work", "start", "iss-00409"]).source == "github"
    assert parse_vnext(["dependency", "check", "iss-00409"]).source == "local"
    assert parse_vnext(["workspace", "sync"]).source == "local"


def test_read_only_leaf_rejects_confirmation_and_accepts_a_preview() -> None:
    with pytest.raises(SystemExit) as invalid:
        parse_vnext(["scope", "show", "iss-00409", "--yes"])
    assert invalid.value.code == 2
    assert parse_vnext(["scope", "show", "iss-00409", "--dry-run"]).dry_run is True


def test_common_numeric_timeout_rejects_negative_values() -> None:
    with pytest.raises(SystemExit) as invalid:
        parse_vnext(["work", "start", "iss-00409", "--lock-timeout", "-1"])
    assert invalid.value.code == 2


def test_common_timeouts_are_typed_finite_and_explicit() -> None:
    default = parse_vnext(["work", "start", "iss-00409", "--json"])
    assert default.lock_timeout == pytest.approx(5.0)
    assert default.timeout == pytest.approx(30.0)
    assert default.non_interactive is True
    assert parse_vnext(["worktree", "bootstrap", "/absolute/worktree"]).timeout == pytest.approx(300.0)
    assert parse_vnext(["work", "start", "iss-00409", "--lock-timeout", "1"]).lock_timeout == pytest.approx(1.0)
    for value in ("nan", "inf", "-inf"):
        with pytest.raises(SystemExit):
            parse_vnext(["work", "start", "iss-00409", "--lock-timeout", value])


@pytest.mark.parametrize(
    "path", ["workspace migrate", "installation init", "installation update", "installation uninstall"]
)
@pytest.mark.parametrize("flag", ["--resume", "--rollback"])
@pytest.mark.parametrize("value", ["0123456789abcdef0123456789abcdef", "bad"])
def test_old_recovery_routes_are_rejected_before_project_access(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], path: str, flag: str, value: str
) -> None:
    arguments = {
        "workspace migrate": ["--to-schema", "3", "--to-writer-protocol", "specdock.worktree-writer/v1"],
        "installation init": [str(tmp_path / "consumer")],
        "installation update": [],
        "installation uninstall": [],
    }[path]
    assert main(["--project", str(tmp_path / "missing"), *path.split(), *arguments, flag, value, "--json"]) == 2
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert not output.err and payload["schema_version"] == "specdock.cli/v2"
    assert payload["error"]["code"] == "ARGUMENT_RETIRED" and payload["effects"] == []
    assert tuple(tmp_path.iterdir()) == ()


def test_nonrecoverable_leaf_rejects_recovery_option() -> None:
    with pytest.raises(SystemExit):
        parse_vnext(["scope", "edit", "iss-00409", "--title", "New", "--resume", "0123456789abcdef0123456789abcdef"])


def test_help_option_before_leaf_opens_that_leaf(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as help_exit:
        parse_vnext(["--help", "scope", "close"])
    assert help_exit.value.code == 0
    assert "--reason" in capsys.readouterr().out


def test_same_name_legacy_arguments_and_abbreviations_are_rejected() -> None:
    for arguments in (
        ["active", "set", "--id", "iss-00409"],
        ["worktree", "create", "planning"],
        ["scope", "sho", "iss-00409"],
    ):
        with pytest.raises(SystemExit) as invalid:
            parse_vnext(arguments)
        assert invalid.value.code == 2


def test_json_usage_failure_is_one_envelope_on_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "scope", "show"]) == 2
    output = capsys.readouterr()
    assert output.err == ""
    payload = json.loads(output.out)
    assert payload["schema_version"] == "specdock.cli/v2"
    assert payload["status"] == "failed"
    assert payload["error"]["code"] == "USAGE_ERROR"


def test_json_help_is_an_envelope(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["scope", "close", "--help", "--json"]) == 0
    output = capsys.readouterr()
    assert output.err == ""
    payload = json.loads(output.out)
    assert payload["schema_version"] == "specdock.cli/v2" and payload["data"]["kind"] == "utility"
    assert payload["status"] == "succeeded"
    assert "--reason" in payload["data"]["text"]


def test_root_version_is_a_utility_and_installation_pins_are_retired(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "--version"]) == 0
    root = capsys.readouterr()
    assert not root.err and json.loads(root.out)["data"]["version"] == __version__
    assert main(["installation", "update", "--version", "0.2.4", "--json"]) == 2
    update = capsys.readouterr()
    assert not update.err and json.loads(update.out)["error"]["code"] == "ARGUMENT_RETIRED"
