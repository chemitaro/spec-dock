"""Current public diagnosis treats legacy files as explicit readonly evidence."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_issue413_workspace_validate import commit_fixture

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("invalid", [False, True])
def test_ci_validation_reads_committed_schema_without_installing_or_writing_state(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    invalid: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    if invalid:
        workspace.write_text('{"schema_version":2}\n', encoding="utf-8")
        commit_fixture(root)
    before = tree_digest(root)
    assert main(["--project", str(root), "workspace", "validate", "--ci", "--json"]) == (7 if invalid else 0)
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["valid"] is not invalid and data["snapshot_source"] == "HEAD"
    assert [item["code"] for item in data["findings"]] == (["WORKSPACE_DECLARATION_INVALID"] if invalid else [])
    assert result["effects"] == [] and tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()


def test_old_control_and_generation_are_not_authority_and_legacy_diagnosis_redacts_bodies(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    control = root / ".git/spec-dock/control/control.json"
    control.parent.mkdir(parents=True)
    control.write_bytes(b"private-body-secret\n{broken")
    generation = root / "spec-dock/.agent/generation.json"
    generation.parent.mkdir()
    generation.write_bytes(b"private-generation-secret\n{broken")
    before = tree_digest(root)
    command = ["--project", str(root), "workspace", "doctor", "--json"]
    assert main(command) == 0
    ordinary = capsys.readouterr()
    assert json.loads(ordinary.out)["effects"] == []
    assert "private-body-secret" not in ordinary.out + ordinary.err
    assert "private-generation-secret" not in ordinary.out + ordinary.err
    assert main([*command, "--legacy"]) == 7
    output = capsys.readouterr()
    result = json.loads(output.out)
    entry = next(item["details"] for item in result["data"]["findings"] if item["details"].get("path") == str(control))
    assert entry["classification"] == "invalid_json" and result["effects"] == []
    assert "private-body-secret" not in output.out + output.err
    assert "private-generation-secret" not in output.out + output.err
    assert tree_digest(root) == before


def test_dependency_and_artifact_faults_are_both_readonly_findings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    payload["depends_on"] = ["iss-99999"]
    metadata.write_text(json.dumps(payload), encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "private.txt"
    secret.write_bytes(b"private-artifact-secret")
    (root / "spec-dock/artifacts").symlink_to(outside, target_is_directory=True)
    before = tree_digest(root)
    for leaf in ("validate", "doctor"):
        assert main(["--project", str(root), "workspace", leaf, "--json"]) == 7
        output = capsys.readouterr()
        result = json.loads(output.out)
        findings = result["data"]["result"]["findings"] if leaf == "validate" else result["data"]["findings"]
        assert {item["code"] for item in findings} >= {"DEPENDENCY_INVALID", "ARTIFACT_INVALID"}
        assert result["effects"] == [] and "private-artifact-secret" not in output.out + output.err
        assert tree_digest(root) == before and secret.read_bytes() == b"private-artifact-secret"
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()
