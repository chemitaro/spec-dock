from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    IssueCandidateIdentity,
    ReviewedPlanningIdentity,
)

HEAD = "a" * 40
COMPANION = b"onboarding companion\n"
COMPANION_SHA = hashlib.sha256(COMPANION).hexdigest()
COMPANION_TARGET = (
    "spec-dock/initiatives/i/epics/e/issues/x/artifacts/"
    "20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"
)


def _module():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_apply",
        fromlist=["PlanningApplyOperation"],
    )


def _identity() -> ReviewedPlanningIdentity:
    candidate = IssueCandidateIdentity(
        issue_id="iss-00003",
        candidate_id="cand-1",
        version=1,
        logical_filename="candidate.zip",
        observed_transport_filename="candidate.zip",
        internal_root="candidate",
        source_repository="owner/repo",
        source_branch="feature/issue",
        source_head=HEAD,
        zip_sha256="b" * 64,
    )
    return ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head=HEAD,
        candidate_identity=candidate,
    )


def _operation(**changes: object):
    module = _module()
    identity = _identity()
    human_decision_bytes = b'{"decision":"approved"}'
    values: dict[str, object] = {
        "issue_id": "iss-00003",
        "mode": "archive-candidate",
        "repository": "owner/repo",
        "branch": "feature/issue",
        "expected_head": HEAD,
        "reviewed_identity": identity,
        "reviewed_identity_sha256": identity.sha256,
        "review_result_sha256": "c" * 64,
        "human_decision_sha256": hashlib.sha256(human_decision_bytes).hexdigest(),
        "decision": "approved",
        "canonical_target_paths": (
            "spec-dock/initiatives/i/epics/e/issues/x/design.md",
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md",
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md",
        ),
        "pre_apply_target_blob_oids": {
            "spec-dock/initiatives/i/epics/e/issues/x/design.md": "1" * 40,
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md": "2" * 40,
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md": "3" * 40,
        },
        "candidate_identity": identity.candidate_identity,
        "git_bound_operation_binding_sha256": None,
        "companion_target_path": COMPANION_TARGET,
        "companion_sha256": COMPANION_SHA,
        "decision_artifact_path": (
            "spec-dock/initiatives/i/epics/e/issues/x/artifacts/"
            "20260728t000000z-planning-human-decision-placeholder.json"
        ),
        "human_decision_bytes": human_decision_bytes,
        "replacement_documents": {
            "design.md": b"new design\n",
            "plan.md": b"new plan\n",
            "requirement.md": b"new requirement\n",
        },
        "replacement_companion": COMPANION,
        "pre_apply_document_bytes": {
            "design.md": b"old design\n",
            "plan.md": b"old plan\n",
            "requirement.md": b"old requirement\n",
        },
    }
    values.update(changes)
    return module.PlanningApplyOperation.create(**values)


def test_operation_identity_is_canonical_and_excludes_private_bytes() -> None:
    first = _operation()
    second = _operation(
        replacement_documents={
            "requirement.md": b"different secret bytes",
            "plan.md": b"different plan",
            "design.md": b"different design",
        }
    )
    assert first.operation_id == second.operation_id
    assert len(first.operation_id) == 64
    payload = first.operation_core_bytes
    assert payload.endswith(b"\n")
    assert b"human_decision_bytes" not in payload
    assert b"replacement_documents" not in payload
    assert b"onboarding companion" not in payload
    assert b'"replacement_companion_present":true' in payload
    assert hashlib.sha256(payload).hexdigest() == first.operation_id


def test_decision_artifact_path_is_deterministic_from_operation_id() -> None:
    operation = _operation()
    assert operation.decision_artifact_path.endswith(
        f"-planning-human-decision-{operation.operation_id[:16]}.json"
    )
    assert not Path(operation.decision_artifact_path).is_absolute()


def test_operation_evidence_is_private_and_collision_is_rejected(tmp_path: Path) -> None:
    module = _module()
    operation = _operation()
    path = module.record_planning_apply_operation(operation, output_dir=tmp_path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o700
    manifest = path / "operation.json"
    assert stat.S_IMODE(manifest.stat().st_mode) == 0o600
    assert manifest.read_bytes() == operation.operation_core_bytes
    assert module.record_planning_apply_operation(operation, output_dir=tmp_path) == path
    manifest.chmod(0o600)
    manifest.write_bytes(b"{}\n")
    with pytest.raises(module.PlanningApplyOutputRejected):
        module.record_planning_apply_operation(operation, output_dir=tmp_path)


@pytest.mark.parametrize(
    "argv",
    [
        ("git", "push", "--force"),
        ("git", "push", "--force-with-lease"),
        ("git", "reset", "--hard"),
        ("git", "commit", "--amend"),
        ("git", "rebase", "main"),
        ("git", "update-ref", "refs/spec-dock/x", HEAD),
    ],
)
def test_prohibited_git_argv_is_rejected(argv: tuple[str, ...]) -> None:
    module = _module()
    with pytest.raises(module.PlanningApplyUnsafeGitCommand):
        module.validate_planning_git_argv(argv)


def test_exact_file_snapshot_restore_preserves_bytes_and_modes(tmp_path: Path) -> None:
    module = _module()
    target = tmp_path / "target"
    target.write_bytes(b"before")
    target.chmod(0o640)
    snapshot = module.snapshot_regular_file(target)
    target.write_bytes(b"after")
    target.chmod(0o600)
    module.restore_regular_file(target, snapshot)
    assert target.read_bytes() == b"before"
    assert stat.S_IMODE(target.stat().st_mode) == 0o640


def test_restore_mismatch_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()
    target = tmp_path / "target"
    target.write_bytes(b"before")
    snapshot = module.snapshot_regular_file(target)
    original = module._atomic_write_exact

    def corrupt(path: Path, data: bytes, *, mode: int) -> None:
        original(path, b"corrupt", mode=mode)

    monkeypatch.setattr(module, "_atomic_write_exact", corrupt)
    with pytest.raises(module.PlanningApplyRestoreMismatch):
        module.restore_regular_file(target, snapshot)


def test_absent_companion_snapshot_restores_exact_absence(tmp_path: Path) -> None:
    module = _module()
    target = tmp_path / "companion.md"
    snapshot = module.snapshot_regular_file(target)
    assert snapshot.existed is False
    target.write_bytes(COMPANION)
    module.restore_regular_file(target, snapshot)
    assert not target.exists()


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_unsafe_companion_destination_is_rejected_before_mutation(
    tmp_path: Path,
    kind: str,
) -> None:
    module = _module()
    target = tmp_path / "companion.md"
    if kind == "symlink":
        destination = tmp_path / "destination.md"
        destination.write_bytes(b"outside\n")
        target.symlink_to(destination)
    else:
        target.mkdir()
    with pytest.raises(ValueError, match="regular non-symlink"):
        module.snapshot_regular_file(target)


def test_git_index_snapshot_uses_raw_bytes(tmp_path: Path) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", repo.as_posix()], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "config", "user.name", "Tester"], check=True)
    subprocess.run(
        ["git", "-C", repo.as_posix(), "config", "user.email", "tester@example.com"],
        check=True,
    )
    tracked = repo / "tracked"
    tracked.write_text("one\n")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "--", "tracked"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "commit", "-qm", "initial"], check=True)
    snapshot = module.snapshot_git_index(repo)
    tracked.write_text("two\n")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "--", "tracked"], check=True)
    assert module.snapshot_git_index(repo).sha256 != snapshot.sha256
    module.restore_git_index(repo, snapshot)
    assert module.snapshot_git_index(repo) == snapshot


def test_execution_result_details_are_content_free() -> None:
    module = _module()
    execution = module.PlanningApplyExecution(
        status="publication_pending",
        reason="push_failed",
        operation_id="a" * 64,
        details=("push_failed",),
    )
    encoded = json.dumps(execution.to_output())
    assert "/Users/" not in encoded
    assert "stderr" not in encoded
