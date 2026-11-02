"""`workspace doctor` on a canonical (schema-4) checkout and on an unreadable declaration (iss-00440, G4).

Replaces tests/cli_runtime/test_issue413_workspace_doctor.py, tests/cli_runtime/test_workspace_doctor_vnext.py and
the doctor part of tests/cli_runtime/test_workspace_diagnostics_commands_vnext.py, which ran on a schema-3 workspace.
A readable schema-4 declaration routes `doctor` and `doctor --raw` to the canonical diagnosis; a declaration that
cannot be admitted (unknown schema, ambiguous JSON) keeps the raw observation. `--legacy` still inspects the
retired records under `.git/spec-dock/control` and `spec-dock/.agent` without executing, replaying or echoing them.
"""

from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_repo import configure, git, isolate_user_state
from tests.support.canonical_scopes import CanonicalWorld

if TYPE_CHECKING:
    from pathlib import Path

SECRET = "private-body-secret"


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "Plan")
    return world


def unreadable_declaration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: bytes = b'{"schema_version":99}'
) -> Path:
    """A committed repository whose declaration cannot be admitted, so `doctor --raw` only observes the file."""
    isolate_user_state(monkeypatch, tmp_path)
    root = tmp_path / "consumer"
    root.mkdir()
    git(root, "init", "-q", "--initial-branch=main")
    configure(root)
    declaration = root / "spec-dock/workspace.json"
    declaration.parent.mkdir()
    declaration.write_bytes(payload)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "fixture")
    return root.resolve()


def doctor(root: Path, capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any], str]:
    code = main(["--project", str(root), "workspace", "doctor", *arguments, "--json"])
    output = capsys.readouterr()
    return code, json.loads(output.out), output.out + output.err


def finding_for(result: dict[str, Any], path: Path) -> dict[str, Any]:
    return next(item["details"] for item in result["data"]["findings"] if item["details"].get("path") == str(path))


def untouched(root: Path) -> tuple[str, str]:
    return tree_digest(root), git(root, "status", "--porcelain", "--ignored")


def test_raw_legacy_doctor_reports_safe_file_information_even_for_unknown_workspace_schema(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = unreadable_declaration(
        tmp_path,
        monkeypatch,
        json.dumps({"schema_version": 99, "writer_protocol": "unknown", "private": "workspace-secret"}).encode(),
    )
    workspace = root / "spec-dock/workspace.json"
    control = root / ".git/spec-dock/control/control.json"
    control.parent.mkdir(parents=True)
    payload = b'{"schema_version":99,"private":"legacy-unlabelled-secret"}'
    control.write_bytes(payload)
    before = workspace.read_bytes()
    code, result, text = doctor(root, capsys, "--raw", "--legacy")
    assert code == 7
    assert result["data"]["kind"] == "diagnostic" and result["effects"] == []
    observed = finding_for(result, control)
    assert observed["entry_type"] == "regular" and observed["bytes"] == len(payload)
    assert "legacy-unlabelled-secret" not in text and "workspace-secret" not in text
    assert control.read_bytes() == payload and workspace.read_bytes() == before
    assert not (root / "spec-dock/.agent").exists()


def test_legacy_doctor_reports_pending_remote_effects_without_resuming_or_executing_old_engine(
    world: CanonicalWorld, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    control = world.main / ".git/spec-dock/control"
    control.mkdir(parents=True)
    trap = tmp_path / "old-engine"
    marker = tmp_path / "must-not-execute"
    trap.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    trap.chmod(0o755)
    (control / "engine.json").write_text(json.dumps({"schema_version": 1, "executable": str(trap)}), encoding="utf-8")
    journal = control / "operations" / ("a" * 32) / "journal.json"
    journal.parent.mkdir(parents=True)
    payload = json.dumps({
        "operation_id": "a" * 32,
        "command": "scope create issue",
        "effect_plan": ["remote"],
        "request_fingerprint": "historical",
        "phase": "remote-intent",
        "engine_digest": "old",
        "writer_epoch": 1,
        "terminal_status": "pending",
        "sequence": 0,
        "backup_refs": [],
        "fixed_targets": [],
        "before_revisions": [],
        "effects": [{"id": "remote", "kind": "remote", "target": SECRET, "status": "intent"}],
    }).encode()
    journal.write_bytes(payload)
    # The canonical diagnosis reads the GitHub structure through gh, so the fake GitHub replaces the trap gh:
    # the old journal's remote effect must not be replayed as a GitHub write.
    code, result, text = doctor(world.main, capsys, "--legacy")
    assert code == 7 and result["effects"] == []
    assert finding_for(result, journal)["classification"] == "remote_effects_unverified"
    assert SECRET not in text
    assert journal.read_bytes() == payload and not marker.exists()
    assert world.fake().writes() == []
    assert not (world.main / "spec-dock/.agent").exists()


PROBE_ARGUMENTS = [
    ["--github-repo", "example/repo"],
    ["--github-extended"],
    ["--github-repo", "example/repo", "--github-pr", "0", "--github-head-sha", "a" * 40],
    ["--github-repo", "example/repo", "--github-pr", "one", "--github-head-sha", "a" * 40],
    ["--github-repo", "-host/repo", "--github-pr", "1", "--github-head-sha", "a" * 40],
    ["--github-repo", "example/repo", "--github-pr", "1", "--github-head-sha", "not-an-oid"],
    ["--github-repo", "example/repo", "--github-pr", "1", "--github-head-sha", "a" * 40, "--offline"],
]


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize("arguments", PROBE_ARGUMENTS)
def test_doctor_refuses_incomplete_or_invalid_fixed_github_probe_before_any_probe(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    raw: bool,
) -> None:
    # raw: an unreadable declaration takes the raw observation; otherwise the canonical diagnosis checks the request.
    root = (
        unreadable_declaration(tmp_path, monkeypatch)
        if raw
        else CanonicalWorld.create(tmp_path, monkeypatch, capsys).main
    )

    def unexpected_probe(*_args: object, **_kwargs: object) -> object:
        pytest.fail("invalid diagnosis must not probe GitHub")

    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_capability_cli.GitHubCapabilityCliGateway.probe", unexpected_probe
    )
    code, result, _ = doctor(root, capsys, *(["--raw"] if raw else []), *arguments)
    assert code in (2, 3)
    assert result["effects"] == []


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize(
    "fault,classification",
    [
        ("malformed", "invalid_json"),
        ("encoding", "invalid_json"),
        ("unknown", "unknown_schema"),
        ("boolean", "unknown_schema"),
        ("too_large", "too_large"),
        ("symlink", "unsafe_file"),
        ("directory", "unsafe_file"),
        ("hardlink", "unsafe_file"),
        ("fifo", "unsafe_file"),
    ],
)
def test_legacy_doctor_preserves_unsafe_and_unknown_records_and_omits_bodies(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    raw: bool,
    fault: str,
    classification: str,
) -> None:
    root = (
        unreadable_declaration(tmp_path, monkeypatch)
        if raw
        else CanonicalWorld.create(tmp_path, monkeypatch, capsys).main
    )
    target = root / ".git/spec-dock/control/control.json"
    target.parent.mkdir(parents=True)
    outside = tmp_path / "private.json"
    outside.write_bytes(b'{"schema_version":3,"private":"do-not-disclose"}')
    if fault == "symlink":
        target.symlink_to(outside)
    elif fault == "directory":
        target.mkdir()
    elif fault == "hardlink":
        os.link(outside, target)
    elif fault == "fifo":
        os.mkfifo(target)
    else:
        target.write_bytes(
            {
                "malformed": b'{"private":"do-not-disclose",bad}',
                "encoding": b"\xffdo-not-disclose",
                "unknown": b'{"schema_version":99,"private":"do-not-disclose"}',
                "boolean": b'{"schema_version":true}',
                "too_large": b"do-not-disclose" * 70000,
            }[fault]
        )
    before = target.lstat()
    code, result, text = doctor(root, capsys, *(["--raw"] if raw else []), "--legacy")
    assert code == 7
    assert finding_for(result, target)["classification"] == classification and result["effects"] == []
    after = target.lstat()
    assert (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns) == (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_size,
        before.st_mtime_ns,
    )
    assert "do-not-disclose" not in text
    assert outside.read_bytes() == b'{"schema_version":3,"private":"do-not-disclose"}'


@pytest.mark.parametrize(
    "declaration",
    [
        b'{"schema_version":99,"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}',
        b'{"schema_version":3,"schema_version":99,"writer_protocol":"specdock.worktree-writer/v1"}',
    ],
)
def test_raw_doctor_refuses_ambiguous_json_before_calling_it_a_known_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, declaration: bytes
) -> None:
    # A duplicate schema key is observed raw (invalid_json), not stopped as schema 3, whichever value comes last.
    root = unreadable_declaration(tmp_path, monkeypatch, declaration)
    code, result, _ = doctor(root, capsys, "--raw")
    assert code == 7
    assert result["data"]["findings"][0]["details"]["classification"] == "invalid_json"
    assert (root / "spec-dock/workspace.json").read_bytes() == declaration and result["effects"] == []


def _probe_gh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str) -> Path:
    """A gh whose capability-probe calls follow `mode`; the fixed `gh api --hostname` shape goes to the fake GitHub."""
    log = tmp_path / "requests.jsonl"
    fake = next((tmp_path / "fake-gh-bin").glob("gh"), None)
    binary = tmp_path / "probe-bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        f"#!{sys.executable}\nimport json,os,sys,time\nmode={mode!r}\nfake={str(fake) if fake else None!r}\n"
        "if fake and sys.argv[1:3] == ['api','--hostname']: os.execv(fake, [fake, *sys.argv[1:]])\n"
        f"with open({str(log)!r},'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "if mode == 'timeout' and sys.argv[1:3] == ['repo','view']: time.sleep(4)\n"
        f"if mode == 'denied': print('permission denied: {SECRET}', file=sys.stderr); sys.exit(1)\n"
        f"if mode == 'malformed': print('{SECRET}{{bad'); sys.exit(0)\n"
        "if sys.argv[1:3] == ['repo','view']: print(json.dumps({'nameWithOwner':'example/repo'}))\n"
        "elif sys.argv[1:3] == ['pr','view']: print(json.dumps({'number':42,'headRefOid':('b' if mode == 'mismatch' else 'a') * 40}))\n"
        "else: print('{}')\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary) + os.pathsep + os.environ["PATH"])
    return log


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize(
    "mode,expected_code,finding_code",
    [
        ("match", 0, "github_capability_ok"),
        ("mismatch", 7, "github_probe_target_mismatch"),
        ("malformed", 7, "github_schema_unavailable"),
        ("denied", 7, "github_token_permission_denied"),
        ("timeout", 7, "github_transient_unknown"),
    ],
)
def test_doctor_native_github_probe_binds_repository_pr_and_head_and_redacts_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    raw: bool,
    mode: str,
    expected_code: int,
    finding_code: str,
) -> None:
    # raw: an unreadable declaration is always an incomplete diagnosis (exit 7), whatever the probe observes.
    root = (
        unreadable_declaration(tmp_path, monkeypatch)
        if raw
        else CanonicalWorld.create(tmp_path, monkeypatch, capsys).main
    )
    log = _probe_gh(tmp_path, monkeypatch, mode)
    code, result, text = doctor(
        root,
        capsys,
        *(["--raw"] if raw else []),
        "--github-repo",
        "example/repo",
        "--github-pr",
        "42",
        "--github-head-sha",
        "a" * 40,
        "--timeout",
        "1",
    )
    assert code == (7 if raw else expected_code)
    assert result["effects"] == [] and any(item["code"] == finding_code for item in result["data"]["findings"])
    assert SECRET not in text
    requests = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(requests) == 7 and all(request[0] in ("repo", "pr", "api") for request in requests)
    assert requests[0] == ["repo", "view", "example/repo", "--json", "nameWithOwner"]
    assert requests[1][:5] == ["pr", "view", "42", "--repo", "example/repo"]


@pytest.mark.parametrize("raw", [False, True])
def test_doctor_reads_retired_paths_only_when_legacy_is_explicit(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, raw: bool
) -> None:
    def unexpected_read(*_args: object, **_kwargs: object) -> object:
        pytest.fail("ordinary diagnosis must not inspect old control")

    monkeypatch.setattr("spec_dock.runtime.application.direct_diagnostics.inspect_legacy_files", unexpected_read)
    code, result, _ = doctor(world.main, capsys, *(["--raw"] if raw else []))
    assert code == 0, result
    assert result["effects"] == []


def test_legacy_active_is_preserved_but_never_automatically_adopted_after_writer_migration(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    active = world.main / "spec-dock/.agent/active.json"
    active.parent.mkdir()
    payload = (
        b'{"schema_version":3,"worktree_id":"historical","revision":1,"focus_id":"init-00001","private":"'
        + SECRET.encode()
        + b'"}'
    )
    active.write_bytes(payload)
    workspace = world.main / "spec-dock/workspace.json"
    original = workspace.read_bytes()
    workspace.write_text('{"schema_version":4,"writer_protocol":"specdock.writer/v1"}', encoding="utf-8")
    code, before, _ = doctor(world.main, capsys, "--legacy")
    assert code == 7
    assert any(item["code"] == "DIRECT_SELECTION_UNVERIFIED" for item in before["data"]["findings"])
    workspace.write_bytes(original)
    code, result, text = doctor(world.main, capsys, "--legacy")
    assert code == 0, result
    assert not any(item["code"] == "DIRECT_SELECTION_UNVERIFIED" for item in result["data"]["findings"])
    assert result["effects"] == [] and active.read_bytes() == payload and not (active.parent / "work-target").exists()
    assert SECRET not in text


@pytest.mark.parametrize("kind", ["engine", "control", "registry", "active", "journal", "missing_journal"])
def test_legacy_doctor_does_not_treat_known_schema_alone_as_a_readable_complete_record(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str], kind: str
) -> None:
    base = world.main / ".git/spec-dock/control"
    path = world.main / "spec-dock/.agent/active.json" if kind == "active" else base / f"{kind}.json"
    if kind in ("journal", "missing_journal"):
        path = base / "operations" / ("a" * 32) / "journal.json"
    path.parent.mkdir(parents=True)
    payload: dict[str, object] = {"schema_version": 1 if kind in ("engine", "registry") else 3, "private": SECRET}
    if kind == "journal":
        payload = {"terminal_status": "succeeded", "effects": [], "private": SECRET}
    if kind != "missing_journal":
        path.write_text(json.dumps(payload), encoding="utf-8")
    code, result, text = doctor(world.main, capsys, "--legacy")
    assert code == 7
    entry = finding_for(result, path)
    assert entry["classification"] == ("journal_missing" if kind == "missing_journal" else "invalid_record")
    assert result["effects"] == [] and SECRET not in text


@pytest.mark.parametrize(
    "kind,directory,filename",
    [
        ("migration", "migrations", "record.json"),
        ("installation", "installations", "group.json"),
        ("finalization", "finalizations", None),
        ("handover", "engine-handovers", None),
    ],
)
@pytest.mark.parametrize("pending", [True, False])
def test_legacy_doctor_classifies_old_migration_and_installation_records_without_replaying_them(
    world: CanonicalWorld,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    directory: str,
    filename: str | None,
    pending: bool,
) -> None:
    operation_id = "a" * 32
    base = world.main / ".git/spec-dock/control" / directory
    path = base / operation_id / filename if filename else base / f"{operation_id}.json"
    path.parent.mkdir(parents=True)
    payload: dict[str, object] = {
        "operation_id": operation_id,
        "common_dir": str(world.main / ".git"),
        "control_epoch": 1,
        "engine_digest": "old",
        "targets": [],
        "phase": "committed",
        "private": SECRET,
    }
    if kind == "migration":
        payload.update(
            repository_uid="historical",
            source_inventory_digest="historical",
            worktrees=[],
            files=[],
            completed_paths=[],
        )
    elif kind == "installation":
        payload["action"] = "update"
    elif kind == "handover":
        payload.update(
            source_update_id="b" * 32,
            prior_executable="/old/bin/spec-dock",
            prior_distribution_root="/old",
            prior_digest="old",
            next_executable="/new/bin/spec-dock",
            next_distribution_root="/new",
            next_digest="new",
        )
    if pending:
        payload["phase"] = "preparing" if kind == "installation" else "prepared"
    before = json.dumps(payload).encode()
    path.write_bytes(before)
    code, result, text = doctor(world.main, capsys, "--legacy")
    assert code == (7 if pending else 0), result
    entry = finding_for(result, path)
    assert entry["classification"] == ("transition_effects_unverified" if pending else "legacy_header_observed")
    assert entry["record_kind"] == kind
    assert result["effects"] == [] and path.read_bytes() == before and SECRET not in text


def test_old_control_and_generation_are_not_authority_and_legacy_diagnosis_redacts_bodies(
    world: CanonicalWorld, capsys: pytest.CaptureFixture[str]
) -> None:
    control = world.main / ".git/spec-dock/control/control.json"
    control.parent.mkdir(parents=True)
    control.write_bytes(SECRET.encode() + b"\n{broken")
    generation = world.main / "spec-dock/.agent/generation.json"
    generation.parent.mkdir()
    generation.write_bytes(b"private-generation-secret\n{broken")
    before = untouched(world.main)
    code, ordinary, text = doctor(world.main, capsys)
    assert code == 0, ordinary
    assert ordinary["effects"] == []
    assert SECRET not in text and "private-generation-secret" not in text
    code, result, text = doctor(world.main, capsys, "--legacy")
    assert code == 7
    assert finding_for(result, control)["classification"] == "invalid_json" and result["effects"] == []
    assert SECRET not in text and "private-generation-secret" not in text
    assert untouched(world.main) == before
    assert world.fake().writes() == []
