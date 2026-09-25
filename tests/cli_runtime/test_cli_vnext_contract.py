"""Public CLI inventory for the coordinated vNext cutover."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli.catalog import LEAF_PATHS, RECOVERY_LEAF_COMMANDS  # noqa: E402
from spec_dock_runtime.cli.legacy import LegacyCommandError  # noqa: E402
from spec_dock_runtime.cli.options import explicit_help, parse_vnext, parse_vnext_output  # noqa: E402
from spec_dock_runtime.cli.parser import build_parser  # noqa: E402
from spec_dock_runtime.cli.registry import build_registry  # noqa: E402

LEGACY_MANIFEST = Path(__file__).resolve().parents[1] / "fixtures/cli_redesign/legacy_manifest.json"


def _leaf_paths(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> set[str]:
    result: set[str] = set()
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child in action.choices.items():
            path = (*prefix, name)
            if child.get_default("command_key"):
                result.add(" ".join(path))
            else:
                result.update(_leaf_paths(child, path))
    return result


def test_legacy_28_leaf_inventory_is_frozen_before_cutover() -> None:
    manifest = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["source_commit"] == "eeb3e5965f0cb42de9a24081bfaea15e27fd4451"
    assert len(manifest["leaf_paths"]) == 28
    assert len(set(manifest["leaf_paths"])) == 28
    assert _leaf_paths(build_parser(build_registry())) == set(manifest["leaf_paths"])


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


def test_every_leaf_help_names_its_effects_and_recovery() -> None:
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
        parsed = parse_vnext_output([*path.split(), "--help", "--json"])
        assert parsed.exit_code == 0
        assert parsed.stdout
        assert json.loads(parsed.stdout)["data"]["help"] == text, path
    work_start = explicit_help(("work", "start"))
    assert "branch" in work_start and "checkout" in work_start
    assert "--resume" in work_start


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
        "local",
        "--parent",
        "init-local-00001",
        "--title",
        "Roadmap",
    ])
    assert result.backend == "local"
    assert result.parent == "init-local-00001"


def test_installation_rollback_accepts_matching_source_pin_for_verification() -> None:
    parsed = parse_vnext([
        "installation",
        "update",
        "--commit",
        "a" * 40,
        "--rollback",
        "b" * 32,
    ])
    assert parsed.commit == "a" * 40
    assert parsed.rollback == "b" * 32


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
    assert parse_vnext(["dependency", "check", "iss-00409"]).source == "cache"
    assert parse_vnext(["workspace", "sync"]).source == "cache"


def test_read_only_leaf_rejects_confirmation_and_dry_run_flags() -> None:
    for flag in ("--yes", "--dry-run"):
        with pytest.raises(SystemExit) as invalid:
            parse_vnext(["scope", "show", "iss-00409", flag])
        assert invalid.value.code == 2


def test_common_numeric_timeout_rejects_negative_values() -> None:
    with pytest.raises(SystemExit) as invalid:
        parse_vnext(["work", "start", "iss-00409", "--lock-timeout", "-1"])
    assert invalid.value.code == 2


def test_common_timeouts_are_typed_finite_and_explicit() -> None:
    default = parse_vnext(["work", "start", "iss-00409", "--json"])
    assert default.lock_timeout == pytest.approx(0.0)
    assert default.timeout == pytest.approx(30.0)
    assert default.non_interactive is True
    assert parse_vnext(["worktree", "bootstrap", "wt:one"]).timeout == pytest.approx(300.0)
    assert parse_vnext(["work", "start", "iss-00409", "--lock-timeout", "1"]).lock_timeout == pytest.approx(1.0)
    for value in ("nan", "inf", "-inf"):
        with pytest.raises(SystemExit):
            parse_vnext(["work", "start", "iss-00409", "--lock-timeout", value])


@pytest.mark.parametrize("path", sorted(RECOVERY_LEAF_COMMANDS))
def test_only_recoverable_leaves_accept_resume(path: str) -> None:
    args = {
        "scope create initiative": ["--backend", "local", "--title", "Plan"],
        "scope create epic": ["--backend", "local", "--parent", "init-00001", "--title", "Plan"],
        "scope create issue": ["--backend", "local", "--parent", "epic-00001", "--title", "Plan"],
        "scope import github initiative": ["gh:a/b#1", "--title", "Plan"],
        "scope import github epic": ["gh:a/b#1", "--parent", "init-00001", "--title", "Plan"],
        "scope import github issue": ["gh:a/b#1", "--parent", "epic-00001", "--title", "Plan"],
        "scope close": ["iss-00001"],
        "scope reopen": ["iss-00001"],
        "scope delete": ["iss-00001"],
        "work start": ["iss-00001"],
        "work finish": ["iss-00001"],
        "branch create": ["iss-00001", "--base", "main"],
        "workspace migrate": ["--to-schema", "3"],
        "installation init": ["/tmp/install"],
        "installation update": ["--version", "0.2.4"],
        "installation uninstall": [],
    }[path]
    operation_id = "0123456789abcdef0123456789abcdef"
    parsed = parse_vnext([*path.split(), *args, "--resume", operation_id])
    assert parsed.resume == operation_id
    with pytest.raises(SystemExit):
        parse_vnext([*path.split(), *args, "--resume", "bad"])
    if RECOVERY_LEAF_COMMANDS[path] in {
        "scope.delete",
        "workspace.migrate",
        "installation.init",
        "installation.update",
        "installation.uninstall",
    }:
        rollback_args = [] if path == "installation update" else args
        rolled = parse_vnext([*path.split(), *rollback_args, "--rollback", operation_id])
        assert rolled.rollback == operation_id
        with pytest.raises(SystemExit):
            parse_vnext([*path.split(), *rollback_args, "--resume", operation_id, "--rollback", operation_id])


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


def test_json_usage_failure_is_one_envelope_on_stdout() -> None:
    output = parse_vnext_output(["--json", "scope", "show"])
    assert output.namespace is None
    assert output.exit_code == 2
    assert output.stderr == ""
    payload = json.loads(output.stdout)
    assert payload["schema_version"] == "specdock.cli/v1"
    assert payload["status"] == "failed"
    assert payload["error"]["code"] == "USAGE_ERROR"


def test_json_help_is_an_envelope() -> None:
    output = parse_vnext_output(["scope", "close", "--help", "--json"])
    assert output.namespace is None
    assert output.exit_code == 0
    assert output.stderr == ""
    payload = json.loads(output.stdout)
    assert payload["status"] == "succeeded"
    assert "--reason" in payload["data"]["help"]


def test_root_version_is_distinct_from_installation_update_version() -> None:
    root = parse_vnext_output(["--json", "--version"], engine_version="0.2.4")
    assert root.exit_code == 0
    assert json.loads(root.stdout)["data"]["version"] == "0.2.4"
    update = parse_vnext(["installation", "update", "--version", "0.2.4"])
    assert update.command_path == "installation update"
    assert update.version == "0.2.4"
