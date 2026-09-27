"""Workspace diagnostics are read-only and report stable finding codes."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
from typing import TYPE_CHECKING, cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application import workspace_diagnostics_vnext as diagnostics_module  # noqa: E402
from spec_dock_runtime.application.contracts import GitHubCapabilityDiagnostic  # noqa: E402
from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.application.workspace_diagnostics_vnext import doctor_workspace, validate_workspace  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402

if TYPE_CHECKING:
    from spec_dock_runtime.infra.github_capability_cli import GitHubCapabilityCliGateway


def _arguments(common: dict[str, object]) -> dict[str, object]:
    return {key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest")}


def test_empty_workspace_is_valid_unless_nodes_required(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    valid = validate_workspace(**_arguments(common))
    assert valid.node_count == 0 and valid.exit_code == 0
    assert [finding.code for finding in valid.findings] == ["generation_missing"]
    required = validate_workspace(**_arguments(common), require_nodes=True)
    assert required.exit_code == 7
    assert "nodes_required" in {finding.code for finding in required.findings}


def test_ci_validation_reads_fresh_checkout_without_control_or_active_state(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    control_directory = cast("Path", common["common_dir"]) / "spec-dock"
    shutil.rmtree(control_directory)
    before = (repo / "spec-dock/workspace.json").read_bytes()
    result = diagnostics_module.validate_checkout_for_ci(repo_root=repo, require_nodes=False)
    assert result.exit_code == 0
    assert result.node_count == 0
    assert result.findings == ()
    assert (repo / "spec-dock/workspace.json").read_bytes() == before
    assert not control_directory.exists()


def test_ci_validation_reports_invalid_committed_schema_without_installing(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    control_directory = cast("Path", common["common_dir"]) / "spec-dock"
    shutil.rmtree(control_directory)
    workspace = repo / "spec-dock/workspace.json"
    workspace.write_text('{"schema_version":2}\n', encoding="utf-8")
    result = diagnostics_module.validate_checkout_for_ci(repo_root=repo)
    assert result.exit_code == 7
    assert {finding.code for finding in result.findings} == {"workspace_schema_mismatch"}
    assert workspace.read_text(encoding="utf-8") == '{"schema_version":2}\n'
    assert not control_directory.exists()


def test_corrupt_control_and_generation_are_findings_without_exposing_content(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    control = cast("Path", common["common_dir"]) / "spec-dock" / "control" / "control.json"
    control.write_text("secret=should-not-appear\n{broken", encoding="utf-8")
    agent = repo / "spec-dock" / ".agent"
    agent.mkdir(exist_ok=True)
    (agent / "generation.json").write_text("secret=should-not-appear\n{broken", encoding="utf-8")
    result = doctor_workspace(**_arguments(common))
    assert result.exit_code == 7
    assert {item.code for item in result.findings} >= {"control_invalid", "generation_invalid"}
    assert "secret=should-not-appear" not in repr(result)


def test_doctor_github_probe_arguments_are_all_or_none(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    with pytest.raises(ValueError, match="requires"):
        doctor_workspace(**_arguments(common), github_repo="example/repo")
    with pytest.raises(ValueError, match="requires"):
        doctor_workspace(**_arguments(common), github_extended=True)
    with pytest.raises(ValueError, match="invalid"):
        doctor_workspace(**_arguments(common), github_repo="example/repo", github_pr=1, github_head_sha="not-a-sha")


def test_engine_mismatch_is_diagnosed_without_mutating_control(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    control = cast("Path", common["common_dir"]) / "spec-dock" / "control" / "control.json"
    before = control.read_bytes()
    result = doctor_workspace(
        repo_root=cast("Path", common["repo_root"]),
        common_dir=cast("Path", common["common_dir"]),
        worktree_id="main",
        engine_digest="other-engine",
    )
    assert result.exit_code == 7
    assert "engine_mismatch" in {item.code for item in result.findings}
    assert control.read_bytes() == before


def test_complete_github_probe_arguments_delegate_once(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    requests: list[object] = []

    class FakeProbe:
        def probe(self, request: object) -> list[object]:
            requests.append(request)
            return []

    result = doctor_workspace(
        **_arguments(common),
        github_repo="example/repo",
        github_pr=42,
        github_head_sha="a" * 40,
        capability_gateway=cast("GitHubCapabilityCliGateway", FakeProbe()),
    )
    assert result.exit_code == 0
    assert len(requests) == 1
    blocked = GitHubCapabilityDiagnostic(
        "github_auth_missing",
        "repo_metadata_read",
        "auth_missing",
        "unknown",
        "gh repo view",
        "blocking",
        "authentication unavailable",
        "configure access",
        True,
        None,
        "core",
    )

    class BlockedProbe:
        def probe(self, _request: object) -> list[GitHubCapabilityDiagnostic]:
            return [blocked]

    failed = doctor_workspace(
        **_arguments(common),
        github_repo="example/repo",
        github_pr=42,
        github_head_sha="a" * 40,
        capability_gateway=cast("GitHubCapabilityCliGateway", BlockedProbe()),
    )
    assert failed.exit_code == 7


def test_dependency_and_artifact_faults_are_read_only_findings(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    metadata_path = created.path / ".meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["depends_on"] = ["iss-local-99999"]
    metadata_path.chmod(0o600)
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    artifacts = repo / "spec-dock" / "artifacts"
    artifacts.symlink_to(tmp_path)
    before = metadata_path.read_bytes()
    result = validate_workspace(**_arguments(common))
    assert result.exit_code == 7
    assert {item.code for item in result.findings} >= {"dependency_invalid", "artifact_invalid"}
    assert metadata_path.read_bytes() == before
    assert artifacts.is_symlink()
