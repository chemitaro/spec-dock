"""Workspace diagnosis reads current evidence without creating or repairing control."""

from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_work_start import committed_workspace

if TYPE_CHECKING:
    from pathlib import Path


def test_doctor_inspects_a_workspace_without_common_control_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    before = {path.relative_to(root): path.read_bytes() for path in (root / "spec-dock").rglob("*") if path.is_file()}
    assert main(["--project", str(root), "workspace", "doctor", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["kind"] == "diagnostic" and result["effects"] == []
    assert isinstance(result["data"]["findings"], list) and isinstance(result["data"]["unverified"], list)
    assert {
        path.relative_to(root): path.read_bytes() for path in (root / "spec-dock").rglob("*") if path.is_file()
    } == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_raw_legacy_doctor_reports_safe_file_information_even_for_unknown_workspace_schema(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    workspace.write_text(
        json.dumps({"schema_version": 99, "writer_protocol": "unknown", "private": "workspace-secret"}),
        encoding="utf-8",
    )
    control = root / ".git/spec-dock/control/control.json"
    control.parent.mkdir(parents=True)
    payload = b'{"schema_version":99,"private":"legacy-unlabelled-secret"}'
    control.write_bytes(payload)
    before = workspace.read_bytes()
    assert main(["--project", str(root), "workspace", "doctor", "--raw", "--legacy", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["kind"] == "diagnostic" and result["effects"] == []
    details = [item["details"] for item in result["data"]["findings"]]
    observed = next(item for item in details if item.get("path") == str(control))
    assert observed["entry_type"] == "regular" and observed["bytes"] == len(payload)
    assert (
        "legacy-unlabelled-secret" not in output.out + output.err and "workspace-secret" not in output.out + output.err
    )
    assert control.read_bytes() == payload and workspace.read_bytes() == before
    assert not (root / "spec-dock/.agent").exists()


def test_legacy_doctor_reports_pending_remote_effects_without_resuming_or_executing_old_engine(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    control = root / ".git/spec-dock/control"
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
        "effects": [{"id": "remote", "kind": "remote", "target": "private-body-secret", "status": "intent"}],
    }).encode()
    journal.write_bytes(payload)
    gh = tmp_path / "gh"
    gh.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 91\n", encoding="utf-8")
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    assert main(["--project", str(root), "workspace", "doctor", "--legacy", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == []
    details = [finding["details"] for finding in result["data"]["findings"]]
    observed = next(item for item in details if item.get("path") == str(journal))
    assert observed["classification"] == "remote_effects_unverified"
    assert "private-body-secret" not in output.out + output.err
    assert journal.read_bytes() == payload and not marker.exists()
    assert not (root / "spec-dock/.agent").exists()


@pytest.mark.parametrize("raw", [False, True])
@pytest.mark.parametrize(
    "arguments",
    [
        ["--github-repo", "example/repo"],
        ["--github-extended"],
        ["--github-repo", "example/repo", "--github-pr", "0", "--github-head-sha", "a" * 40],
        ["--github-repo", "example/repo", "--github-pr", "one", "--github-head-sha", "a" * 40],
        ["--github-repo", "-host/repo", "--github-pr", "1", "--github-head-sha", "a" * 40],
        ["--github-repo", "example/repo", "--github-pr", "1", "--github-head-sha", "not-an-oid"],
        ["--github-repo", "example/repo", "--github-pr", "1", "--github-head-sha", "a" * 40, "--offline"],
    ],
)
def test_doctor_refuses_incomplete_or_invalid_fixed_github_probe_before_any_probe(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
    raw: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")

    def unexpected_probe(*_args: object, **_kwargs: object) -> object:
        pytest.fail("invalid diagnosis must not probe GitHub")

    monkeypatch.setattr(
        "spec_dock.runtime.infra.github_capability_cli.GitHubCapabilityCliGateway.probe", unexpected_probe
    )
    code = main(["--project", str(root), "workspace", "doctor", *(["--raw"] if raw else []), *arguments, "--json"])
    assert code in (2, 3)
    output = json.loads(capsys.readouterr().out)
    assert output["effects"] == []


@pytest.mark.parametrize("fault", ["invalid_json", "wrong_parent", "dependency_missing", "artifact_redirect"])
def test_doctor_reports_workspace_structure_faults_as_incomplete_diagnostics_without_repairs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    fault: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = next((root / "spec-dock").rglob(".meta.json"))
    if fault == "invalid_json":
        metadata.write_text('{"private-body-secret": invalid}', encoding="utf-8")
    elif fault == "artifact_redirect":
        (root / "spec-dock/artifacts").symlink_to(tmp_path)
    else:
        payload = json.loads(metadata.read_bytes())
        payload["parent_id" if fault == "wrong_parent" else "depends_on"] = (
            "epic-99999" if fault == "wrong_parent" else ["init-99999"]
        )
        metadata.write_text(json.dumps(payload), encoding="utf-8")
    before = metadata.read_bytes()
    assert main(["--project", str(root), "workspace", "doctor", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["findings"] and result["effects"] == []
    assert "private-body-secret" not in output.out + output.err
    assert metadata.read_bytes() == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


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
    raw: bool,
    fault: str,
    classification: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
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
    assert main(["--project", str(root), "workspace", "doctor", *(["--raw"] if raw else []), "--legacy", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    observed = next(
        item["details"] for item in result["data"]["findings"] if item["details"].get("path") == str(target)
    )
    assert observed["classification"] == classification and result["effects"] == []
    after = target.lstat()
    assert (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns) == (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_size,
        before.st_mtime_ns,
    )
    assert "do-not-disclose" not in output.out + output.err
    assert outside.read_bytes() == b'{"schema_version":3,"private":"do-not-disclose"}'


def test_raw_doctor_refuses_ambiguous_json_before_calling_it_a_known_workspace(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    before = b'{"schema_version":99,"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}'
    workspace.write_bytes(before)
    assert main(["--project", str(root), "workspace", "doctor", "--raw", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["findings"][0]["details"]["classification"] == "invalid_json"
    assert workspace.read_bytes() == before and result["effects"] == []


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
    root = committed_workspace(tmp_path / "consumer")
    gh = tmp_path / "gh"
    log = tmp_path / "requests.jsonl"
    gh.write_text(
        f"#!{sys.executable}\nimport json,sys,time\nmode={mode!r}\nwith open({str(log)!r},'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "if mode == 'timeout' and sys.argv[1:3] == ['repo','view']: time.sleep(4)\n"
        "if mode == 'denied': print('permission denied: private-body-secret', file=sys.stderr); sys.exit(1)\n"
        "if mode == 'malformed': print('private-body-secret{bad'); sys.exit(0)\n"
        "if sys.argv[1:3] == ['repo','view']: print(json.dumps({'nameWithOwner':'example/repo'}))\n"
        "elif sys.argv[1:3] == ['pr','view']: print(json.dumps({'number':42,'headRefOid':('b' if mode == 'mismatch' else 'a') * 40}))\n"
        "else: print('{}')\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "doctor",
            *(["--raw"] if raw else []),
            "--github-repo",
            "example/repo",
            "--github-pr",
            "42",
            "--github-head-sha",
            "a" * 40,
            "--timeout",
            "1",
            "--json",
        ])
        == expected_code
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["effects"] == [] and any(item["code"] == finding_code for item in result["data"]["findings"])
    assert "private-body-secret" not in output.out + output.err
    requests = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(requests) == 7 and all(request[0] in ("repo", "pr", "api") for request in requests)
    assert requests[0] == ["repo", "view", "example/repo", "--json", "nameWithOwner"]
    assert requests[1][:5] == ["pr", "view", "42", "--repo", "example/repo"]


@pytest.mark.parametrize("raw", [False, True])
def test_doctor_reads_retired_paths_only_when_legacy_is_explicit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    raw: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")

    def unexpected_read(*_args: object, **_kwargs: object) -> object:
        pytest.fail("ordinary diagnosis must not inspect old control")

    monkeypatch.setattr("spec_dock.runtime.application.direct_diagnostics.inspect_legacy_files", unexpected_read)
    assert main(["--project", str(root), "workspace", "doctor", *(["--raw"] if raw else []), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["effects"] == []


def test_legacy_active_is_preserved_but_never_automatically_adopted_after_writer_migration(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    active = root / "spec-dock/.agent/active.json"
    active.parent.mkdir()
    payload = b'{"schema_version":3,"worktree_id":"historical","revision":1,"focus_id":"init-00001","private":"private-body-secret"}'
    active.write_bytes(payload)
    workspace = root / "spec-dock/workspace.json"
    workspace.write_text('{"schema_version":3,"writer_protocol":"specdock.writer/v1"}', encoding="utf-8")
    assert main(["--project", str(root), "workspace", "doctor", "--legacy", "--json"]) == 7
    before = json.loads(capsys.readouterr().out)
    assert any(item["code"] == "DIRECT_SELECTION_UNVERIFIED" for item in before["data"]["findings"])
    workspace.write_text('{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}', encoding="utf-8")
    assert main(["--project", str(root), "workspace", "doctor", "--legacy", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert not any(item["code"] == "DIRECT_SELECTION_UNVERIFIED" for item in result["data"]["findings"])
    assert result["effects"] == [] and active.read_bytes() == payload and not (active.parent / "work-target").exists()
    assert "private-body-secret" not in output.out + output.err


@pytest.mark.parametrize("kind", ["engine", "control", "registry", "active", "journal", "missing_journal"])
def test_legacy_doctor_does_not_treat_known_schema_alone_as_a_readable_complete_record(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    kind: str,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    base = root / ".git/spec-dock/control"
    path = root / "spec-dock/.agent/active.json" if kind == "active" else base / f"{kind}.json"
    if kind in ("journal", "missing_journal"):
        path = base / "operations" / ("a" * 32) / "journal.json"
    path.parent.mkdir(parents=True)
    payload: dict[str, object] = {
        "schema_version": 1 if kind in ("engine", "registry") else 3,
        "private": "private-body-secret",
    }
    if kind == "journal":
        payload = {"terminal_status": "succeeded", "effects": [], "private": "private-body-secret"}
    if kind != "missing_journal":
        path.write_text(json.dumps(payload), encoding="utf-8")
    assert main(["--project", str(root), "workspace", "doctor", "--legacy", "--json"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    entry = next(item["details"] for item in result["data"]["findings"] if item["details"].get("path") == str(path))
    assert entry["classification"] == ("journal_missing" if kind == "missing_journal" else "invalid_record")
    assert result["effects"] == [] and "private-body-secret" not in output.out + output.err


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
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    kind: str,
    directory: str,
    filename: str | None,
    pending: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    operation_id = "a" * 32
    base = root / ".git/spec-dock/control" / directory
    path = base / operation_id / filename if filename else base / f"{operation_id}.json"
    path.parent.mkdir(parents=True)
    payload: dict[str, object] = {
        "operation_id": operation_id,
        "common_dir": str(root / ".git"),
        "control_epoch": 1,
        "engine_digest": "old",
        "targets": [],
        "phase": "committed",
        "private": "private-body-secret",
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
    assert main(["--project", str(root), "workspace", "doctor", "--legacy", "--json"]) == (7 if pending else 0)
    output = capsys.readouterr()
    result = json.loads(output.out)
    entry = next(item["details"] for item in result["data"]["findings"] if item["details"].get("path") == str(path))
    assert entry["classification"] == ("transition_effects_unverified" if pending else "legacy_header_observed")
    assert entry["record_kind"] == kind
    assert (
        result["effects"] == [] and path.read_bytes() == before and "private-body-secret" not in output.out + output.err
    )
