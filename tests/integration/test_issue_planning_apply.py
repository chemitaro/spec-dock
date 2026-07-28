from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _module():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_apply",
        fromlist=["execute_planning_apply_transaction"],
    )


def _git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", repo.as_posix(), *args],
        check=check,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, Path, str, tuple[str, str, str]]:
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", "-q", origin.as_posix()], check=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Tester")
    _git(repo, "config", "user.email", "tester@example.com")
    _git(repo, "remote", "add", "origin", origin.as_posix())
    issue = (
        repo
        / "spec-dock"
        / "initiatives"
        / "init-one"
        / "epics"
        / "epic-one"
        / "issues"
        / "iss-one"
    )
    (issue / "artifacts").mkdir(parents=True)
    relative: list[str] = []
    for name in ("design.md", "plan.md", "requirement.md"):
        path = issue / name
        path.write_bytes(f"old {name}\n".encode())
        relative.append(path.relative_to(repo).as_posix())
    (repo / ".gitignore").write_text("spec-dock/dashboard.md\n")
    _git(repo, "add", "--", ".gitignore", *relative)
    _git(repo, "commit", "-qm", "initial")
    _git(repo, "branch", "-M", "feature/issue")
    _git(repo, "push", "-qu", "origin", "feature/issue")
    return repo, origin, _git(repo, "rev-parse", "HEAD"), tuple(sorted(relative))  # type: ignore[return-value]


def _operation(
    repo: Path,
    head: str,
    targets: tuple[str, str, str],
    *,
    mode: str = "archive-candidate",
    decision: str = "approved",
):
    module = _module()
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["ReviewedPlanningIdentity", "IssueCandidateIdentity"],
    )
    candidate = contracts.IssueCandidateIdentity(
        issue_id="iss-00003",
        candidate_id="cand-1",
        version=1,
        logical_filename="candidate.zip",
        observed_transport_filename="candidate.zip",
        internal_root="candidate",
        source_repository="owner/repo",
        source_branch="feature/issue",
        source_head=head,
        zip_sha256="b" * 64,
    )
    if mode == "archive-candidate":
        identity = contracts.ReviewedPlanningIdentity(
            mode=mode,
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=head,
            candidate_identity=candidate,
        )
    else:
        identity = contracts.ReviewedPlanningIdentity(
            mode=mode,
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=head,
            canonical_target_paths=targets,
            expected_canonical_target_paths=targets,
        )
    blobs = {path: _git(repo, "rev-parse", f"{head}:{path}") for path in targets}
    issue_dir = Path(targets[0]).parent
    artifact = issue_dir / (
        "artifacts/20260728t000000z-planning-human-decision-placeholder.json"
    )
    replacements = {}
    if mode == "archive-candidate" and decision == "approved":
        replacements = {
            Path(path).name: f"new {Path(path).name}\n".encode()
            for path in targets
        }
    return module.PlanningApplyOperation.create(
        issue_id="iss-00003",
        mode=mode,
        repository="owner/repo",
        branch="feature/issue",
        expected_head=head,
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        review_result_sha256="c" * 64,
        human_decision_sha256="d" * 64,
        decision=decision,
        canonical_target_paths=targets,
        pre_apply_target_blob_oids=blobs,
        candidate_identity=candidate if mode == "archive-candidate" else None,
        decision_artifact_path=artifact.as_posix(),
        human_decision_bytes=f'{{"decision":"{decision}"}}'.encode(),
        replacement_documents=replacements,
        pre_apply_document_bytes={
            Path(path).name: (repo / path).read_bytes() for path in targets
        },
    )


@pytest.mark.parametrize(
    ("mode", "decision", "expected"),
    [
        ("archive-candidate", "approved", ("ready", "adoption_published")),
        ("git-bound", "approved", ("ready", "adoption_published")),
        ("archive-candidate", "rejected", ("rejected", "plan_rejected")),
        ("git-bound", "rejected", ("rejected", "plan_rejected")),
    ],
)
def test_apply_against_local_bare_remote(
    tmp_path: Path,
    mode: str,
    decision: str,
    expected: tuple[str, str],
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets, mode=mode, decision=decision)
    before = {path: (repo / path).read_bytes() for path in targets}
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
    )
    assert (result.status, result.reason) == expected
    local = _git(repo, "rev-parse", "HEAD")
    remote = _git(origin, "rev-parse", "refs/heads/feature/issue")
    assert local == remote
    assert _git(repo, "status", "--porcelain=v2") == ""
    artifact = repo / operation.decision_artifact_path
    assert artifact.read_bytes() == operation.human_decision_bytes
    if mode == "archive-candidate" and decision == "approved":
        assert any((repo / path).read_bytes() != before[path] for path in targets)
    else:
        assert {path: (repo / path).read_bytes() for path in targets} == before
    assert result.is_ready is (decision == "approved")


def test_precommit_failure_restores_documents_decision_and_raw_index(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    index_before = module.snapshot_git_index(repo)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_index_stage":
            raise RuntimeError("injected")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
        fault_hook=fault,
    )
    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_push_failure_keeps_local_commit_for_same_operation_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    real_run = module._run_git
    fail = [True]

    def run_git(repo_root: Path, argv: tuple[str, ...], *, check: bool = True):
        if argv and argv[0] == "push" and fail[0]:
            fail[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_run(repo_root, argv, check=check)

    monkeypatch.setattr(module, "_run_git", run_git)
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
    )
    local_commit = _git(repo, "rev-parse", "HEAD")
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    assert local_commit != head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    ready = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("retry must not validate or commit"),
        sync_runner=lambda: pytest.fail("retry must not sync or commit"),
    )
    assert (ready.status, ready.reason) == ("ready", "adoption_published")
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == local_commit


def test_after_commit_interruption_retry_publishes_same_commit(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def interrupt(checkpoint: str) -> None:
        if checkpoint == "after_commit":
            raise RuntimeError("process interrupted after commit")

    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: SimpleNamespace(
            report=SimpleNamespace(errors=[]),
        ),
        sync_runner=lambda: SimpleNamespace(
            artifact_failure=None,
            state=SimpleNamespace(deps_preflight_error=None),
            write_result=None,
            active_update=None,
        ),
        fault_hook=interrupt,
    )
    local_commit = _git(repo, "rev-parse", "HEAD")
    commit_count = _git(repo, "rev-list", "--count", "HEAD")
    assert (pending.status, pending.reason) == (
        "publication_pending",
        "remote_parity_unconfirmed",
    )
    assert local_commit != head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head

    ready = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("retry must not validate or commit"),
        sync_runner=lambda: pytest.fail("retry must not sync or commit"),
    )
    assert (ready.status, ready.reason) == ("ready", "adoption_published")
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(repo, "rev-list", "--count", "HEAD") == commit_count
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == local_commit


def test_precreated_permissive_operation_evidence_cannot_bypass_apply(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    operation_dir.mkdir(mode=0o777)
    operation_dir.chmod(0o777)
    attempts = operation_dir / "attempts"
    attempts.mkdir(mode=0o777)
    attempts.chmod(0o777)
    (operation_dir / "operation.json").write_bytes(operation.operation_core_bytes)
    (operation_dir / "state.json").write_text(
        '{"state":"COMMITTED"}\n',
        encoding="utf-8",
    )
    tree = _git(repo, "rev-parse", "HEAD^{tree}")
    (operation_dir / "commit.json").write_text(
        json.dumps(
            {
                "operation_id": operation.operation_id,
                "local_commit": head,
                "local_tree": tree,
                "decision": "approved",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    for evidence in operation_dir.glob("*.json"):
        evidence.chmod(0o644)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("forged resume must not validate"),
        sync_runner=lambda: pytest.fail("forged resume must not sync"),
    )
    assert (result.status, result.reason) == (
        "rejected",
        "apply_output_rejected",
    )
    assert result.is_ready is False
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize(
    ("failure", "expected_reason"),
    [
        ("validation", "specdock_validation_failed"),
        ("sync", "specdock_sync_failed"),
    ],
)
def test_validation_and_sync_failures_restore_exact_baseline(
    tmp_path: Path,
    failure: str,
    expected_reason: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    index_before = module.snapshot_git_index(repo)
    validation_errors = ["invalid"] if failure == "validation" else []
    sync_failure = object() if failure == "sync" else None
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type(
            "V",
            (),
            {"report": type("R", (), {"errors": validation_errors})()},
        )(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": sync_failure,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
    )
    assert (result.status, result.reason) == ("rolled_back", expected_reason)
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert module.snapshot_git_index(repo) == index_before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize(
    "checkpoint",
    [
        "after_decision_write",
        "after_requirement_replace",
        "after_design_replace",
        "after_plan_replace",
        "after_canonical_proof",
        "after_validation",
        "after_sync",
        "after_diff_proof",
        "before_commit",
    ],
)
def test_each_precommit_fault_checkpoint_rolls_back(
    tmp_path: Path,
    checkpoint: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}

    def fault(observed: str) -> None:
        if observed == checkpoint:
            raise RuntimeError("injected")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
        fault_hook=fault,
    )
    assert result.status == "rolled_back"
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_restore_failure_requires_recovery_and_retains_remote(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "during_restore":
            raise module.PlanningApplyRestoreMismatch("injected")
        if checkpoint == "after_index_stage":
            raise RuntimeError("begin rollback")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
        fault_hook=fault,
    )
    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_same_operation_retry_accepts_already_published_commit(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    kwargs = {
        "repo_root": repo,
        "output_dir": output,
        "validation_runner": lambda: type(
            "V", (), {"report": type("R", (), {"errors": []})()}
        )(),
        "sync_runner": lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
    }
    first = module.execute_planning_apply_transaction(operation, **kwargs)
    local_commit = _git(repo, "rev-parse", "HEAD")
    commit_count = _git(repo, "rev-list", "--count", "HEAD")
    second = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("published retry must not validate"),
        sync_runner=lambda: pytest.fail("published retry must not sync"),
    )
    assert (first.status, first.reason) == ("ready", "adoption_published")
    assert (second.status, second.reason) == ("ready", "adoption_published")
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(repo, "rev-list", "--count", "HEAD") == commit_count
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == local_commit


def test_retry_remote_divergence_is_blocked_without_force(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    real_run = module._run_git
    fail = [True]

    def run_git(repo_root: Path, argv: tuple[str, ...], *, check: bool = True):
        if argv and argv[0] == "push" and fail[0]:
            fail[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_run(repo_root, argv, check=check)

    monkeypatch.setattr(module, "_run_git", run_git)
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
        sync_runner=lambda: type(
            "S",
            (),
            {
                "artifact_failure": None,
                "state": type("State", (), {"deps_preflight_error": None})(),
            },
        )(),
    )
    assert pending.status == "publication_pending"
    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", "-q", "--branch", "feature/issue", origin.as_posix(), other.as_posix()],
        check=True,
    )
    _git(other, "config", "user.name", "Other")
    _git(other, "config", "user.email", "other@example.com")
    (other / "diverged").write_text("different\n")
    _git(other, "add", "--", "diverged")
    _git(other, "commit", "-qm", "diverge")
    _git(other, "push", "-q", "origin", "feature/issue")
    divergent = _git(origin, "rev-parse", "refs/heads/feature/issue")
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("diverged retry must not validate"),
        sync_runner=lambda: pytest.fail("diverged retry must not sync"),
    )
    assert (result.status, result.reason) == (
        "blocked_remote_diverged",
        "remote_diverged",
    )
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == divergent


def test_sync_failure_restores_managed_state_exactly(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    dashboard = repo / "spec-dock" / "dashboard.md"
    dashboard.write_bytes(b"old dashboard\n")
    operation = _operation(repo, head, targets)

    def sync():
        dashboard.write_bytes(b"partial new dashboard\n")
        return SimpleNamespace(
            artifact_failure=object(),
            state=SimpleNamespace(deps_preflight_error=None),
            write_result=None,
            active_update=None,
        )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: SimpleNamespace(
            report=SimpleNamespace(errors=[]),
        ),
        sync_runner=sync,
    )
    assert (result.status, result.reason) == (
        "rolled_back",
        "specdock_sync_failed",
    )
    assert dashboard.read_bytes() == b"old dashboard\n"
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_sync_scope_violation_rolls_back(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: SimpleNamespace(
            report=SimpleNamespace(errors=[]),
        ),
        sync_runner=lambda: SimpleNamespace(
            artifact_failure=None,
            state=SimpleNamespace(deps_preflight_error=None),
            write_result=SimpleNamespace(
                dashboard_md_path="spec-dock/not-declared.md",
            ),
            active_update=None,
        ),
    )
    assert (result.status, result.reason) == (
        "rolled_back",
        "specdock_sync_failed",
    )
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_recovery_required_retains_private_transaction_backup(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, _origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_index_stage":
            raise RuntimeError("rollback")
        if checkpoint == "during_restore":
            raise module.PlanningApplyRestoreMismatch("retain backup")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: SimpleNamespace(
            report=SimpleNamespace(errors=[]),
        ),
        sync_runner=lambda: SimpleNamespace(
            artifact_failure=None,
            state=SimpleNamespace(deps_preflight_error=None),
            write_result=None,
            active_update=None,
        ),
        fault_hook=fault,
    )
    assert (result.status, result.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    transaction = (
        output
        / f"planning-apply-{operation.operation_id}"
        / "transaction"
    )
    assert transaction.is_dir()
    assert transaction.stat().st_mode & 0o777 == 0o700
    assert (transaction / "git-index.bin").stat().st_mode & 0o777 == 0o600
    assert (transaction / "backup-manifest.json").stat().st_mode & 0o777 == 0o600


def test_post_commit_unexpected_worktree_change_requires_recovery(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_commit":
            (repo / "unexpected").write_text("hook mutation\n")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: SimpleNamespace(
            report=SimpleNamespace(errors=[]),
        ),
        sync_runner=lambda: SimpleNamespace(
            artifact_failure=None,
            state=SimpleNamespace(deps_preflight_error=None),
            write_result=None,
            active_update=None,
        ),
        fault_hook=fault,
    )
    assert (result.status, result.reason) == (
        "recovery_required",
        "post_commit_workspace_changed",
    )
    assert _git(repo, "rev-parse", "HEAD") != head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_application_retry_reaches_same_operation_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    app = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_apply"],
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningReviewResult", "PlanningHumanDecisionV1"],
    )
    infra_contracts = __import__(
        "spec_dock_runtime.infra.contracts",
        fromlist=["StoredMetaRecord"],
    )
    candidate_contracts = __import__(
        "spec_dock_runtime.infra.issue_planning_candidate",
        fromlist=["VerifiedIssueCandidate"],
    )
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    issue_dir = repo / Path(targets[0]).parent
    candidate_identity = _operation(repo, head, targets).candidate_identity
    assert candidate_identity is not None
    identity = contracts.ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head=head,
        candidate_identity=candidate_identity,
    )
    review = contracts.PlanningReviewResult(
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        verdict="pass",
        findings=(),
    )
    review_bytes = json.dumps(
        review.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    human = contracts.PlanningHumanDecisionV1(
        schema_version=1,
        issue_id="iss-00003",
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
        decision="approved",
        plan_adoption=True,
        implementation_start=True,
        decided_at="2026-07-28T00:00:00Z",
    )
    human_bytes = json.dumps(
        human.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    review_path = output / "review.json"
    human_path = output / "human.json"
    review_path.write_bytes(review_bytes)
    human_path.write_bytes(human_bytes)
    candidate = candidate_contracts.VerifiedIssueCandidate(
        identity=candidate_identity,
        files={
            "design.md": b"new design.md\n",
            "plan.md": b"new plan.md\n",
            "requirement.md": b"new requirement.md\n",
        },
        source_baseline={
            "canonical_issue_paths": list(targets),
            "relevant_paths": [],
            "source_manifest_hash": "c" * 64,
        },
        zip_bytes=b"candidate",
    )
    record = infra_contracts.StoredMetaRecord(
        kind="issue",
        id="iss-00003",
        title="Issue",
        slug="issue",
        path=issue_dir.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(issue_dir / ".meta.json").as_posix(),
    )
    request = app.PlanningApplyRequest(
        issue_id="iss-00003",
        mode="archive-candidate",
        review_result_path=review_path,
        human_decision_path=human_path,
        expected_head=head,
        output_dir=output,
        candidate_path=output / candidate_identity.observed_transport_filename,
        logical_filename=candidate_identity.logical_filename,
        zip_sha256=candidate_identity.zip_sha256,
    )
    real_run = module._run_git
    fail_push = [True]

    def run_git(repo_root: Path, argv: tuple[str, ...], *, check: bool = True):
        if argv and argv[0] == "push" and fail_push[0]:
            fail_push[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_run(repo_root, argv, check=check)

    monkeypatch.setattr(module, "_run_git", run_git)

    def preflight(_request):
        local = _git(repo, "rev-parse", "HEAD")
        remote = _git(origin, "rev-parse", "refs/heads/feature/issue")
        return SimpleNamespace(
            status="pass" if local == remote == head else "blocked",
            local_head=local,
            remote_head=remote,
            blockers=() if local == remote == head else ("ahead_of_remote",),
            source_manifest=SimpleNamespace(source_manifest_hash="c" * 64),
        )

    def apply_once():
        return app.run_issue_planning_apply(
            request=request,
            records=[record],
            repo_root=repo,
            repo_slug_resolver=lambda _root: "owner/repo",
            validation_runner=lambda: SimpleNamespace(
                report=SimpleNamespace(errors=[]),
            ),
            sync_runner=lambda: SimpleNamespace(
                artifact_failure=None,
                state=SimpleNamespace(deps_preflight_error=None),
                write_result=None,
                active_update=None,
            ),
            preflight_runner=preflight,
            candidate_loader=lambda _path, _root: candidate,
            transaction_runner=module.execute_planning_apply_transaction,
        )

    pending = apply_once()
    local_commit = _git(repo, "rev-parse", "HEAD")
    commit_count = _git(repo, "rev-list", "--count", "HEAD")
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    assert local_commit != head
    ready = apply_once()
    assert (ready.status, ready.reason) == ("ready", "adoption_published")
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(repo, "rev-list", "--count", "HEAD") == commit_count
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == local_commit


@pytest.mark.parametrize(
    "checkpoint",
    [
        "after_operation_recorded",
        "after_decision_write",
        "after_plan_replace",
        "after_index_stage",
    ],
)
def test_interrupted_precommit_transaction_retry_restores_durable_backup(
    tmp_path: Path,
    checkpoint: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: (repo / path).read_bytes() for path in targets}
    index_before = module.snapshot_git_index(repo)
    managed_before = module.snapshot_managed_sync_state(repo)

    class ProcessCrash(BaseException):
        pass

    def crash(observed: str) -> None:
        if observed == checkpoint:
            raise ProcessCrash

    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: SimpleNamespace(
                report=SimpleNamespace(errors=[]),
            ),
            sync_runner=lambda: SimpleNamespace(
                artifact_failure=None,
                state=SimpleNamespace(deps_preflight_error=None),
                write_result=None,
                active_update=None,
            ),
            fault_hook=crash,
        )
    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("recovery must precede validation"),
        sync_runner=lambda: pytest.fail("recovery must precede sync"),
    )
    assert (recovered.status, recovered.reason) == (
        "rolled_back",
        "planning_commit_failed",
    )
    assert {path: (repo / path).read_bytes() for path in targets} == documents_before
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
