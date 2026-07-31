from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
from types import SimpleNamespace

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.ports import IssuePlanningDependencies  # noqa: E402
from spec_dock_runtime.cli.bootstrap import _Clock, _IssuePlanningGateway  # noqa: E402

PLANNING_DEPENDENCIES = IssuePlanningDependencies(clock=_Clock(), gateway=_IssuePlanningGateway())


def _module():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_apply",
        fromlist=["execute_planning_apply_transaction"],
    )


@pytest.fixture
def _bind_local_publication_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()

    def capture(operation, repo_root: Path):
        endpoint = _git(repo_root, "remote", "get-url", "--push", "origin")
        return module._PublicationAuthority(
            repository=operation.repository.lower(),
            push_endpoint=endpoint,
        )

    monkeypatch.setattr(module, "_capture_publication_authority", capture)


pytestmark = pytest.mark.usefixtures("_bind_local_publication_authority")


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
    issue = repo / "spec-dock" / "initiatives" / "init-one" / "epics" / "epic-one" / "issues" / "iss-one"
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
        fromlist=[
            "GitBoundOperationBindingV1",
            "OnboardingCompanionBindingV1",
            "ReviewedPlanningIdentity",
            "IssueCandidateIdentity",
        ],
    )
    companion = b"onboarding companion\n"
    companion_relative = "artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"
    companion_target = (Path(targets[0]).parent / companion_relative).as_posix()
    companion_binding = contracts.OnboardingCompanionBindingV1(
        path=companion_relative,
        sha256=hashlib.sha256(companion).hexdigest(),
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
        operation_binding = contracts.GitBoundOperationBindingV1.create(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=head,
            candidate_identity=candidate,
            onboarding_companion=companion_binding,
        )
        identity = contracts.ReviewedPlanningIdentity(
            mode=mode,
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=head,
            canonical_target_paths=targets,
            git_bound_operation_binding=operation_binding,
            expected_canonical_target_paths=targets,
        )
    blobs = {path: _git(repo, "rev-parse", f"{head}:{path}") for path in targets}
    issue_dir = Path(targets[0]).parent
    artifact = issue_dir / ("artifacts/20260728t000000z-planning-human-decision-placeholder.json")
    replacements = {}
    if mode == "archive-candidate" and decision == "approved":
        replacements = {Path(path).name: f"new {Path(path).name}\n".encode() for path in targets}
    human_decision_bytes = f'{{"decision":"{decision}"}}'.encode()
    return module.PlanningApplyOperation.create(
        issue_id="iss-00003",
        mode=mode,
        repository="owner/repo",
        branch="feature/issue",
        expected_head=head,
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        review_result_sha256="c" * 64,
        human_decision_sha256=hashlib.sha256(human_decision_bytes).hexdigest(),
        decision=decision,
        canonical_target_paths=targets,
        pre_apply_target_blob_oids=blobs,
        candidate_identity=candidate,
        git_bound_operation_binding_sha256=(
            None if mode == "archive-candidate" else identity.git_bound_operation_binding.binding_sha256
        ),
        companion_target_path=companion_target,
        companion_sha256=companion_binding.sha256,
        decision_artifact_path=artifact.as_posix(),
        human_decision_bytes=human_decision_bytes,
        replacement_documents=replacements,
        replacement_companion=companion if decision == "approved" else None,
        pre_apply_document_bytes={Path(path).name: (repo / path).read_bytes() for path in targets},
    )


def _output_guard(module, output: Path):
    opened = output.stat()
    return module.OutputDirectoryGuard(
        path=output.resolve(),
        device=opened.st_dev,
        inode=opened.st_ino,
    )


def _validation_ok():
    return SimpleNamespace(report=SimpleNamespace(errors=[]))


def _sync_ok():
    return SimpleNamespace(
        artifact_failure=None,
        state=SimpleNamespace(deps_preflight_error=None),
        write_result=None,
        active_update=None,
    )


def _install_hook(repo: Path, name: str, body: str) -> None:
    hook = repo / ".git" / "hooks" / name
    hook.write_text(f"#!/bin/sh\nset -eu\n{body}\n")
    hook.chmod(0o755)


def test_output_replacement_before_fd_capture_is_rejected_without_evidence(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    guard = _output_guard(module, output)
    original = tmp_path / "original-output"
    redirected = repo / "redirected"
    redirected.mkdir()
    output.rename(original)
    output.symlink_to(redirected, target_is_directory=True)
    operation = _operation(repo, head, targets)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_guard=guard,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("rejected", "apply_output_rejected")
    assert list(redirected.iterdir()) == []
    assert list(original.iterdir()) == []
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_output_replacement_after_fd_capture_keeps_evidence_in_original(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, _origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    guard = _output_guard(module, output)
    original = tmp_path / "original-output"
    redirected = repo / "redirected"
    redirected.mkdir()
    operation = _operation(repo, head, targets)

    def replace(checkpoint: str) -> None:
        if checkpoint == "after_output_capture":
            output.rename(original)
            output.symlink_to(redirected, target_is_directory=True)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_guard=guard,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=replace,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert list(redirected.iterdir()) == []
    evidence = original / f"planning-apply-{operation.operation_id}"
    assert (evidence / "operation.json").is_file()
    assert (evidence / "state.json").is_file()
    assert len(list((evidence / "attempts").iterdir())) == 1
    assert (evidence / "commit.json").is_file()
    assert (evidence / "publication.json").is_file()
    assert not (evidence / "transaction").exists()


@pytest.mark.parametrize("race", ["delete", "rewind"])
def test_first_publication_remote_delete_or_rewind_is_blocked_by_cas(
    tmp_path: Path,
    race: str,
) -> None:
    module = _module()
    repo, origin, _head, targets = _repository(tmp_path)
    (repo / "second").write_text("second\n")
    _git(repo, "add", "--", "second")
    _git(repo, "commit", "-qm", "second")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    rewind = _git(repo, "rev-parse", f"{head}^")
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def race_remote(checkpoint: str) -> None:
        if checkpoint != "before_push":
            return
        if race == "delete":
            _git(origin, "update-ref", "-d", "refs/heads/feature/issue", head)
        else:
            _git(origin, "update-ref", "refs/heads/feature/issue", rewind, head)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=race_remote,
    )

    assert (result.status, result.reason) == (
        "blocked_remote_diverged",
        "remote_diverged",
    )
    remote = _git(origin, "rev-parse", "--verify", "refs/heads/feature/issue", check=False)
    assert remote == ("" if race == "delete" else rewind)
    evidence = output / f"planning-apply-{operation.operation_id}"
    assert (evidence / "commit.json").is_file()
    assert not (evidence / "publication.json").exists()


@pytest.mark.parametrize("race", ["delete", "rewind"])
def test_resume_publication_remote_delete_or_rewind_is_blocked_by_cas(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    race: str,
) -> None:
    module = _module()
    repo, origin, _head, targets = _repository(tmp_path)
    (repo / "second").write_text("second\n")
    _git(repo, "add", "--", "second")
    _git(repo, "commit", "-qm", "second")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    rewind = _git(repo, "rev-parse", f"{head}^")
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    real_push = module._push_operation_commit_cas
    fail_once = [True]

    def fail_first(**kwargs):
        if fail_once[0]:
            fail_once[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"injected")
        return real_push(**kwargs)

    monkeypatch.setattr(module, "_push_operation_commit_cas", fail_first)
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")

    def race_remote(checkpoint: str) -> None:
        if checkpoint != "before_push":
            return
        if race == "delete":
            _git(origin, "update-ref", "-d", "refs/heads/feature/issue", head)
        else:
            _git(origin, "update-ref", "refs/heads/feature/issue", rewind, head)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
        fault_hook=race_remote,
    )

    assert (result.status, result.reason) == (
        "blocked_remote_diverged",
        "remote_diverged",
    )
    remote = _git(origin, "rev-parse", "--verify", "refs/heads/feature/issue", check=False)
    assert remote == ("" if race == "delete" else rewind)
    evidence = output / f"planning-apply-{operation.operation_id}"
    assert (evidence / "commit.json").is_file()
    assert not (evidence / "publication.json").exists()


def test_resume_publication_remote_deleted_before_resume_is_blocked_without_push(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, _head, targets = _repository(tmp_path)
    (repo / "second").write_text("second\n")
    _git(repo, "add", "--", "second")
    _git(repo, "commit", "-qm", "second")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: module.GitCommandResult(returncode=1, stdout=b"", stderr=b"injected"),
    )
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    local_commit = _git(repo, "rev-parse", "HEAD")
    commit_count = _git(repo, "rev-list", "--count", "HEAD")
    evidence = output / f"planning-apply-{operation.operation_id}"
    commit_evidence = (evidence / "commit.json").read_bytes()
    state_evidence = (evidence / "state.json").read_bytes()
    _git(origin, "update-ref", "-d", "refs/heads/feature/issue", head)

    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: pytest.fail("deleted remote must stop before push"),
    )
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
    )

    assert (result.status, result.reason) == (
        "blocked_remote_diverged",
        "remote_diverged",
    )
    assert _git(origin, "rev-parse", "--verify", "refs/heads/feature/issue", check=False) == ""
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(repo, "rev-list", "--count", "HEAD") == commit_count
    assert (evidence / "commit.json").read_bytes() == commit_evidence
    assert (evidence / "state.json").read_bytes() == state_evidence
    assert not (evidence / "publication.json").exists()


def test_resume_publication_remote_observation_unavailable_stays_pending_without_push(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, _head, targets = _repository(tmp_path)
    (repo / "second").write_text("second\n")
    _git(repo, "add", "--", "second")
    _git(repo, "commit", "-qm", "second")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: module.GitCommandResult(returncode=1, stdout=b"", stderr=b"injected"),
    )
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    local_commit = _git(repo, "rev-parse", "HEAD")
    commit_count = _git(repo, "rev-list", "--count", "HEAD")
    remote_commit = _git(origin, "rev-parse", "refs/heads/feature/issue")
    evidence = output / f"planning-apply-{operation.operation_id}"
    commit_evidence = (evidence / "commit.json").read_bytes()
    state_evidence = (evidence / "state.json").read_bytes()

    monkeypatch.setattr(
        module,
        "_remote_head_observation",
        lambda _repo, _authority, _branch: ("unavailable", None),
    )
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: pytest.fail("unavailable remote must stop before push"),
    )
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
    )

    assert (result.status, result.reason) == (
        "publication_pending",
        "remote_parity_unconfirmed",
    )
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == remote_commit
    assert _git(repo, "rev-parse", "HEAD") == local_commit
    assert _git(repo, "rev-list", "--count", "HEAD") == commit_count
    assert (evidence / "commit.json").read_bytes() == commit_evidence
    assert (evidence / "state.json").read_bytes() == state_evidence
    assert not (evidence / "publication.json").exists()


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
    companion_path = repo / operation.companion_target_path
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
    if decision == "approved":
        assert companion_path.read_bytes() == operation.replacement_companion
    else:
        assert not companion_path.exists()
    assert result.is_ready is (decision == "approved")


def test_git_bound_apply_accepts_exact_existing_companion_as_noop(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, _, targets = _repository(tmp_path)
    companion_target = (
        Path(targets[0]).parent / "artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"
    )
    (repo / companion_target).write_bytes(b"onboarding companion\n")
    _git(repo, "add", "--", companion_target.as_posix())
    _git(repo, "commit", "-qm", "existing companion")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    operation = _operation(repo, head, targets, mode="git-bound")
    before = {path: (repo / path).read_bytes() for path in targets}
    output = tmp_path / "output"
    output.mkdir()

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
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert (repo / companion_target).read_bytes() == b"onboarding companion\n"
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == _git(repo, "rev-parse", "HEAD")


def test_archive_apply_rejects_canonical_edit_at_transaction_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    changed_target = repo / targets[0]
    concurrent_bytes = b"concurrent canonical edit\n"
    real_snapshot = module.snapshot_git_index

    def snapshot(repo_root: Path):
        changed_target.write_bytes(concurrent_bytes)
        return real_snapshot(repo_root)

    monkeypatch.setattr(module, "snapshot_git_index", snapshot)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert changed_target.read_bytes() == concurrent_bytes
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "transaction").exists()


def test_archive_apply_atomic_editor_swap_after_target_open_is_stale_and_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: module.snapshot_regular_file(repo / path) for path in targets}
    requirement_relative = next(path for path in targets if Path(path).name == "requirement.md")
    requirement = repo / requirement_relative
    editor_bytes = b"atomic editor replacement\n"
    editor_identity: list[tuple[int, int]] = []
    real_exchange = module._exchange_entries_at
    injected = [False]

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        if not injected[0] and second == "requirement.md":
            injected[0] = True
            editor = requirement.with_name("requirement.editor.tmp")
            editor.write_bytes(editor_bytes)
            editor.replace(requirement)
            observed = requirement.stat()
            editor_identity.append((observed.st_dev, observed.st_ino))
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    observed = requirement.stat()
    assert (observed.st_dev, observed.st_ino) == editor_identity[0]
    assert requirement.read_bytes() == editor_bytes
    for path, snapshot in before.items():
        if path != requirement_relative:
            assert module.snapshot_regular_file(repo / path) == snapshot
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert not tuple(repo.rglob(".spec-dock-apply-*"))
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "OPERATION_RECORDED"


def test_archive_apply_second_canonical_replacement_during_exchange_back_retains_recovery_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    requirement_relative = next(path for path in targets if Path(path).name == "requirement.md")
    requirement = repo / requirement_relative
    original_preimage = requirement.read_bytes()
    attachment_b = b"first concurrent canonical attachment\n"
    attachment_c = b"second concurrent canonical attachment\n"
    real_exchange = module._exchange_entries_at
    requirement_exchanges = [0]

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        if second == "requirement.md":
            requirement_exchanges[0] += 1
            replacement = requirement.with_name(f"requirement.editor.{requirement_exchanges[0]}.tmp")
            replacement.write_bytes(attachment_b if requirement_exchanges[0] == 1 else attachment_c)
            replacement.replace(requirement)
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("contended apply must not validate"),
        sync_runner=lambda: pytest.fail("contended apply must not sync"),
    )

    assert requirement_exchanges == [2]
    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert requirement.read_bytes() == attachment_b
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    transaction = operation_dir / "transaction"
    ledger = json.loads((transaction / "mutation-ledger.json").read_bytes())
    requirement_entry = next(entry for entry in ledger["entries"] if entry["path"] == requirement_relative)
    workspace = requirement.parent / requirement_entry["workspace_name"]
    assert (workspace / requirement_entry["staged_name"]).read_bytes() == attachment_c
    assert (
        requirement_entry["after_sha256"]
        == hashlib.sha256(operation.replacement_documents["requirement.md"]).hexdigest()
    )
    manifest = json.loads((transaction / "backup-manifest.json").read_bytes())
    requirement_backup = next(entry for entry in manifest["files"] if entry["path"] == requirement_relative)
    assert (transaction / "files" / requirement_backup["backup"]).read_bytes() == original_preimage
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (operation_dir / "commit.json").exists()
    assert not (operation_dir / "publication.json").exists()


def test_archive_apply_rejects_absent_companion_create_at_transaction_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    companion_path = repo / operation.companion_target_path
    concurrent_bytes = b"concurrent companion\n"
    real_snapshot = module.snapshot_git_index

    def snapshot(repo_root: Path):
        companion_path.write_bytes(concurrent_bytes)
        return real_snapshot(repo_root)

    monkeypatch.setattr(module, "snapshot_git_index", snapshot)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert companion_path.read_bytes() == concurrent_bytes
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "transaction").exists()


def test_archive_apply_rejects_tracked_companion_change_at_transaction_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, _, targets = _repository(tmp_path)
    companion_target = (
        Path(targets[0]).parent / "artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"
    )
    companion_path = repo / companion_target
    companion_path.write_bytes(b"onboarding companion\n")
    _git(repo, "add", "--", companion_target.as_posix())
    _git(repo, "commit", "-qm", "existing companion")
    _git(repo, "push", "-q", "origin", "feature/issue")
    head = _git(repo, "rev-parse", "HEAD")
    operation = _operation(repo, head, targets)
    output = tmp_path / "output"
    output.mkdir()
    concurrent_bytes = b"concurrent tracked companion edit\n"
    real_snapshot = module.snapshot_git_index

    def snapshot(repo_root: Path):
        companion_path.write_bytes(concurrent_bytes)
        return real_snapshot(repo_root)

    monkeypatch.setattr(module, "snapshot_git_index", snapshot)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert companion_path.read_bytes() == concurrent_bytes
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "transaction").exists()


def test_archive_apply_rechecks_canonical_after_operation_recorded(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    changed_target = repo / targets[0]
    concurrent_bytes = b"concurrent canonical edit after backup\n"

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            changed_target.write_bytes(concurrent_bytes)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert changed_target.read_bytes() == concurrent_bytes
    assert all((repo / path).read_bytes() == before[path] for path in targets[1:])
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "OPERATION_RECORDED"


def test_archive_apply_rechecks_absent_companion_after_operation_recorded(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    companion_path = repo / operation.companion_target_path
    concurrent_bytes = b"concurrent companion after backup\n"

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            companion_path.write_bytes(concurrent_bytes)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert companion_path.read_bytes() == concurrent_bytes
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "OPERATION_RECORDED"

    companion_path.unlink()
    retry = module.execute_planning_apply_transaction(
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
    )
    assert (retry.status, retry.reason) == ("ready", "adoption_published")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == _git(repo, "rev-parse", "HEAD")


def test_canonical_replace_uses_captured_parent_after_ancestor_symlink_swap(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    issue = repo / Path(targets[0]).parent
    issues = issue.parent
    captured_issues = issues.with_name(f"{issues.name}-captured")
    external_issues = tmp_path / "external-issues"
    external_issue = external_issues / issue.name
    (external_issue / "artifacts").mkdir(parents=True)
    external_sentinels = {name: f"external {name}\n".encode() for name in ("design.md", "plan.md", "requirement.md")}
    for name, data in external_sentinels.items():
        (external_issue / name).write_bytes(data)
    observed_external_requirement: list[bytes] = []

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_decision_write":
            issues.rename(captured_issues)
            issues.symlink_to(external_issues, target_is_directory=True)
        elif checkpoint == "after_requirement_replace":
            observed_external_requirement.append((external_issue / "requirement.md").read_bytes())
            raise RuntimeError("injected")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("swapped topology must not validate"),
        sync_runner=lambda: pytest.fail("swapped topology must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert observed_external_requirement == [external_sentinels["requirement.md"]]
    assert {name: (external_issue / name).read_bytes() for name in external_sentinels} == external_sentinels
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_rollback_uses_captured_parents_after_ancestor_symlink_swap(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    issue = repo / Path(targets[0]).parent
    issues = issue.parent
    captured_issues = issues.with_name(f"{issues.name}-captured")
    external_issues = tmp_path / "external-issues"
    external_issue = external_issues / issue.name
    (external_issue / "artifacts").mkdir(parents=True)
    external_sentinels = {name: f"external {name}\n".encode() for name in ("design.md", "plan.md", "requirement.md")}
    for name, data in external_sentinels.items():
        (external_issue / name).write_bytes(data)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_decision_write":
            issues.rename(captured_issues)
            issues.symlink_to(external_issues, target_is_directory=True)
            raise RuntimeError("injected")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("swapped topology must not validate"),
        sync_runner=lambda: pytest.fail("swapped topology must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert {name: (external_issue / name).read_bytes() for name in external_sentinels} == external_sentinels
    assert not (external_issue / Path(operation.decision_artifact_path).name).exists()
    assert not any(path.name.startswith(".") for path in external_issue.rglob("*"))
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_archive_apply_preserves_edit_injected_during_mutating_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    design = repo / next(path for path in targets if Path(path).name == "design.md")
    concurrent = b"concurrent design during mutating state\n"
    real_set_state = module._set_operation_state

    def set_state(handle, current_operation, state: str) -> None:
        real_set_state(handle, current_operation, state)
        if state == "MUTATING":
            design.write_bytes(concurrent)

    monkeypatch.setattr(module, "_set_operation_state", set_state)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("drifted apply must not validate"),
        sync_runner=lambda: pytest.fail("drifted apply must not sync"),
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert design.read_bytes() == concurrent
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "OPERATION_RECORDED"


def test_archive_apply_revalidates_each_canonical_replacement_boundary(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    requirement = repo / next(path for path in targets if Path(path).name == "requirement.md")
    design = repo / next(path for path in targets if Path(path).name == "design.md")
    requirement_before = requirement.read_bytes()
    concurrent = b"concurrent design after requirement replacement\n"

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_requirement_replace":
            design.write_bytes(concurrent)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("drifted apply must not validate"),
        sync_runner=lambda: pytest.fail("drifted apply must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert requirement.read_bytes() == requirement_before
    assert design.read_bytes() == concurrent
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_archive_apply_preserves_companion_created_after_canonical_replacements(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    companion = repo / operation.companion_target_path
    concurrent = b"concurrent companion after plan replacement\n"

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_plan_replace":
            companion.write_bytes(concurrent)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("drifted apply must not validate"),
        sync_runner=lambda: pytest.fail("drifted apply must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("stale", "apply_target_changed")
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert companion.read_bytes() == concurrent
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_apply_staged_name_replacement_before_exchange_preserves_repository_preimage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    requirement = repo / next(path for path in targets if Path(path).name == "requirement.md")
    preimage = requirement.read_bytes()
    unknown = b"unknown staged replacement\n"
    real_exchange = module._exchange_entries_at
    injected = [False]

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        if not injected[0] and second == "requirement.md":
            injected[0] = True
            module.os.rename(
                first,
                f"{first}.owned",
                src_dir_fd=source_fd,
                dst_dir_fd=source_fd,
            )
            descriptor = module.os.open(
                first,
                module.os.O_WRONLY | module.os.O_CREAT | module.os.O_EXCL,
                0o600,
                dir_fd=source_fd,
            )
            try:
                module.os.write(descriptor, unknown)
            finally:
                module.os.close(descriptor)
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("ambiguous exchange must not validate"),
        sync_runner=lambda: pytest.fail("ambiguous exchange must not sync"),
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    available = [path.read_bytes() for path in (repo / Path(targets[0]).parent).rglob("*") if path.is_file()]
    assert preimage in available
    assert unknown in available
    assert operation.replacement_documents["requirement.md"] in available
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert (output / f"planning-apply-{operation.operation_id}" / "transaction").is_dir()


def test_crash_after_compare_replace_before_outer_return_recovers_recorded_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    real_compare = module._RepositoryTargetGuard.compare_replace

    class ProcessCrash(BaseException):
        pass

    crashed = [False]

    def compare(self, relative: str, **kwargs):
        result = real_compare(self, relative, **kwargs)
        if not crashed[0] and Path(relative).name == "requirement.md" and result is not None:
            crashed[0] = True
            raise ProcessCrash
        return result

    monkeypatch.setattr(module._RepositoryTargetGuard, "compare_replace", compare)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
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
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_recovery_resolves_prepared_ledger_after_namespace_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}
    real_persist = module._persist_target_mutations

    class ProcessCrash(BaseException):
        pass

    crashed = [False]

    def crash_before_published_ledger(handle, current_operation, mutations, **kwargs) -> None:
        if (
            not crashed[0]
            and mutations
            and Path(mutations[-1].relative).name == "requirement.md"
            and mutations[-1].phase == "published"
        ):
            crashed[0] = True
            raise ProcessCrash
        real_persist(handle, current_operation, mutations, **kwargs)

    monkeypatch.setattr(
        module,
        "_persist_target_mutations",
        crash_before_published_ledger,
    )
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
        )
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    assert ledger["entries"][-1]["phase"] == "prepared"

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
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize("artifact", ["decision", "companion"])
def test_recovery_resolves_prepared_absent_artifact_after_namespace_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    artifact: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    selected_relative = operation.decision_artifact_path if artifact == "decision" else operation.companion_target_path
    selected = repo / selected_relative
    real_persist = module._persist_target_mutations

    class ProcessCrash(BaseException):
        pass

    crashed = [False]

    def crash_before_published_ledger(handle, current_operation, mutations, **kwargs) -> None:
        if (
            not crashed[0]
            and mutations
            and mutations[-1].relative == selected_relative
            and mutations[-1].phase == "published"
        ):
            crashed[0] = True
            raise ProcessCrash
        real_persist(handle, current_operation, mutations, **kwargs)

    monkeypatch.setattr(
        module,
        "_persist_target_mutations",
        crash_before_published_ledger,
    )
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    assert ledger["entries"][-1]["path"] == selected_relative
    assert ledger["entries"][-1]["phase"] == "prepared"
    assert selected.exists()

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
    assert not selected.exists()
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_recovery_resumes_existing_restore_after_reverse_exchange_before_workspace_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: module.snapshot_regular_file(repo / path) for path in targets}
    index_before = module.snapshot_git_index(repo)
    managed_before = module.snapshot_managed_sync_state(repo)
    real_exchange = module._exchange_entries_at
    armed = [False]
    crashed = [False]

    class ProcessCrash(BaseException):
        pass

    def crash_after_reverse_exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        real_exchange(source_fd, first, destination_fd, second)
        if armed[0] and not crashed[0]:
            crashed[0] = True
            raise ProcessCrash

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_index_stage":
            raise RuntimeError("begin rollback")
        if checkpoint == "during_restore":
            armed[0] = True

    monkeypatch.setattr(module, "_exchange_entries_at", crash_after_reverse_exchange)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: SimpleNamespace(report=SimpleNamespace(errors=[])),
            sync_runner=lambda: SimpleNamespace(
                artifact_failure=None,
                state=SimpleNamespace(deps_preflight_error=None),
                write_result=None,
                active_update=None,
            ),
            fault_hook=fault,
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    affected = ledger["entries"][-1]
    assert affected["phase"] == "rollback-prepared"
    workspace = repo / Path(affected["path"]).parent / affected["workspace_name"]
    assert workspace.is_dir()
    assert (repo / affected["path"]).read_bytes() == documents_before[affected["path"]].data
    assert (workspace / affected["staged_name"]).read_bytes() == operation.replacement_documents[
        Path(affected["path"]).name
    ]

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
    for path, before in documents_before.items():
        assert module.snapshot_regular_file(repo / path) == before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not tuple(repo.rglob(".spec-dock-apply-*"))
    assert not (operation_dir / "transaction").exists()
    state = json.loads((operation_dir / "state.json").read_bytes())
    assert state["state"] == "ROLLED_BACK"


def test_recovery_cleans_forward_workspace_crash_before_mutation_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: module.snapshot_regular_file(repo / path) for path in targets}
    targets_before = {
        **documents_before,
        operation.decision_artifact_path: module.snapshot_regular_file(repo / operation.decision_artifact_path),
        operation.companion_target_path: module.snapshot_regular_file(repo / operation.companion_target_path),
    }
    index_before = module.snapshot_git_index(repo)
    managed_before = module.snapshot_managed_sync_state(repo)
    real_persist = module._persist_target_mutations
    crashed = [False]

    class ProcessCrash(BaseException):
        pass

    def crash_before_prepared_handoff(handle, current_operation, mutations, **kwargs) -> None:
        if not crashed[0] and mutations and mutations[-1].phase == "prepared":
            crashed[0] = True
            raise ProcessCrash
        real_persist(handle, current_operation, mutations, **kwargs)

    monkeypatch.setattr(module, "_persist_target_mutations", crash_before_prepared_handoff)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    assert ledger["entries"] == []
    intent = ledger["workspace_intent"]
    assert intent["purpose"] == "forward"
    workspace = repo / Path(intent["path"]).parent / intent["workspace_name"]
    staged = workspace / intent["staged_name"]
    assert workspace.is_dir()
    staged_stat = staged.stat()
    assert (staged_stat.st_dev, staged_stat.st_ino) == (
        intent["staged_device"],
        intent["staged_inode"],
    )
    assert module.snapshot_regular_file(repo / intent["path"]) == targets_before[intent["path"]]

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
    for path, before in documents_before.items():
        assert module.snapshot_regular_file(repo / path) == before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not tuple(repo.rglob(".spec-dock-apply-*"))
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "ROLLED_BACK"


def test_recovery_cleans_existing_rollback_workspace_crash_before_reverse_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: module.snapshot_regular_file(repo / path) for path in targets}
    index_before = module.snapshot_git_index(repo)
    managed_before = module.snapshot_managed_sync_state(repo)
    real_persist = module._persist_target_mutations
    crashed = [False]

    class ProcessCrash(BaseException):
        pass

    def crash_before_reverse_handoff(handle, current_operation, mutations, **kwargs) -> None:
        if not crashed[0] and mutations and mutations[-1].phase == "rollback-prepared" and mutations[-1].before.existed:
            crashed[0] = True
            raise ProcessCrash
        real_persist(handle, current_operation, mutations, **kwargs)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_index_stage":
            raise RuntimeError("begin rollback")

    monkeypatch.setattr(module, "_persist_target_mutations", crash_before_reverse_handoff)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: SimpleNamespace(report=SimpleNamespace(errors=[])),
            sync_runner=lambda: SimpleNamespace(
                artifact_failure=None,
                state=SimpleNamespace(deps_preflight_error=None),
                write_result=None,
                active_update=None,
            ),
            fault_hook=fault,
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    outer = ledger["entries"][-1]
    assert outer["phase"] == "published"
    intent = ledger["workspace_intent"]
    assert intent["purpose"] == "rollback-existing"
    workspace = repo / Path(intent["path"]).parent / intent["workspace_name"]
    staged = workspace / intent["staged_name"]
    assert workspace.is_dir()
    staged_stat = staged.stat()
    assert (staged_stat.st_dev, staged_stat.st_ino) == (
        intent["staged_device"],
        intent["staged_inode"],
    )
    assert (repo / intent["path"]).read_bytes() == operation.replacement_documents[Path(intent["path"]).name]
    assert staged.read_bytes() == documents_before[intent["path"]].data

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
    for path, before in documents_before.items():
        assert module.snapshot_regular_file(repo / path) == before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not tuple(repo.rglob(".spec-dock-apply-*"))
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "ROLLED_BACK"


@pytest.mark.parametrize("artifact", ["decision", "companion"])
def test_recovery_cleans_absent_rollback_workspace_crash_before_phase_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    artifact: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: module.snapshot_regular_file(repo / path) for path in targets}
    index_before = module.snapshot_git_index(repo)
    managed_before = module.snapshot_managed_sync_state(repo)
    selected_relative = operation.decision_artifact_path if artifact == "decision" else operation.companion_target_path
    selected_bytes = operation.human_decision_bytes if artifact == "decision" else operation.replacement_companion
    assert selected_bytes is not None
    checkpoint = "after_decision_write" if artifact == "decision" else "after_companion_write"
    real_persist = module._persist_target_mutations
    crashed = [False]

    class ProcessCrash(BaseException):
        pass

    def crash_before_absent_handoff(handle, current_operation, mutations, **kwargs) -> None:
        if (
            not crashed[0]
            and mutations
            and mutations[-1].relative == selected_relative
            and mutations[-1].phase == "rollback-prepared"
            and not mutations[-1].before.existed
        ):
            crashed[0] = True
            raise ProcessCrash
        real_persist(handle, current_operation, mutations, **kwargs)

    def fault(observed: str) -> None:
        if observed == checkpoint:
            raise RuntimeError("begin rollback")

    monkeypatch.setattr(module, "_persist_target_mutations", crash_before_absent_handoff)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: SimpleNamespace(report=SimpleNamespace(errors=[])),
            sync_runner=lambda: SimpleNamespace(
                artifact_failure=None,
                state=SimpleNamespace(deps_preflight_error=None),
                write_result=None,
                active_update=None,
            ),
            fault_hook=fault,
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = json.loads((operation_dir / "transaction" / "mutation-ledger.json").read_bytes())
    outer = ledger["entries"][-1]
    assert outer["path"] == selected_relative
    assert outer["phase"] == "published"
    intent = ledger["workspace_intent"]
    assert intent["purpose"] == "rollback-absent"
    assert intent["staged_name"] == "quarantine"
    assert (intent["staged_device"], intent["staged_inode"]) == (
        outer["after_device"],
        outer["after_inode"],
    )
    workspace = repo / Path(intent["path"]).parent / intent["workspace_name"]
    assert workspace.is_dir()
    assert not tuple(workspace.iterdir())
    assert (repo / selected_relative).read_bytes() == selected_bytes

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
    for path, before in documents_before.items():
        assert module.snapshot_regular_file(repo / path) == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert not (repo / operation.companion_target_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not tuple(repo.rglob(".spec-dock-apply-*"))
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "ROLLED_BACK"


def test_recovery_retries_after_crash_between_target_restore_and_ledger_shrink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}

    class ProcessCrash(BaseException):
        pass

    def initial_crash(checkpoint: str) -> None:
        if checkpoint == "after_plan_replace":
            raise ProcessCrash

    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
            fault_hook=initial_crash,
        )

    real_restore = module._RepositoryTargetGuard.restore
    crash_once = [True]

    def restore_then_crash(self, mutation, **kwargs):
        result = real_restore(self, mutation, **kwargs)
        if crash_once[0]:
            crash_once[0] = False
            raise ProcessCrash
        return result

    monkeypatch.setattr(module._RepositoryTargetGuard, "restore", restore_then_crash)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("recovery must not validate"),
            sync_runner=lambda: pytest.fail("recovery must not sync"),
        )
    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("recovery must not validate"),
        sync_runner=lambda: pytest.fail("recovery must not sync"),
    )

    assert (recovered.status, recovered.reason) == (
        "rolled_back",
        "planning_commit_failed",
    )
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_recovery_resumes_from_durable_shortened_mutation_ledger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    before = {path: (repo / path).read_bytes() for path in targets}

    class ProcessCrash(BaseException):
        pass

    def initial_crash(checkpoint: str) -> None:
        if checkpoint == "after_plan_replace":
            raise ProcessCrash

    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
            fault_hook=initial_crash,
        )
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    ledger = operation_dir / "transaction" / "mutation-ledger.json"
    initial_count = len(json.loads(ledger.read_bytes())["entries"])
    real_persist = module._persist_target_mutations
    crash_once = [True]

    def persist_then_crash(handle, current_operation, mutations, **kwargs) -> None:
        real_persist(handle, current_operation, mutations, **kwargs)
        if crash_once[0] and len(mutations) == initial_count - 1:
            crash_once[0] = False
            raise ProcessCrash

    monkeypatch.setattr(module, "_persist_target_mutations", persist_then_crash)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("recovery must not validate"),
            sync_runner=lambda: pytest.fail("recovery must not sync"),
        )
    assert len(json.loads(ledger.read_bytes())["entries"]) == initial_count - 1
    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("recovery must not validate"),
        sync_runner=lambda: pytest.fail("recovery must not sync"),
    )

    assert (recovered.status, recovered.reason) == (
        "rolled_back",
        "planning_commit_failed",
    )
    assert {path: (repo / path).read_bytes() for path in targets} == before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_recovery_resumes_absent_restore_after_quarantine_rename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    class ProcessCrash(BaseException):
        pass

    def initial_crash(checkpoint: str) -> None:
        if checkpoint == "after_decision_write":
            raise RuntimeError("begin rollback")

    real_rename = module._rename_no_replace_at
    crash_once = [True]

    def rename_then_crash(
        source_fd: int,
        source_name: str,
        destination_fd: int,
        destination_name: str,
    ) -> None:
        real_rename(
            source_fd,
            source_name,
            destination_fd,
            destination_name,
        )
        if crash_once[0] and destination_name == "quarantine":
            crash_once[0] = False
            raise ProcessCrash

    monkeypatch.setattr(module, "_rename_no_replace_at", rename_then_crash)
    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("rollback must precede validation"),
            sync_runner=lambda: pytest.fail("rollback must precede sync"),
            fault_hook=initial_crash,
        )

    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("recovery must not validate"),
        sync_runner=lambda: pytest.fail("recovery must not sync"),
    )

    assert (recovered.status, recovered.reason) == (
        "rolled_back",
        "planning_commit_failed",
    )
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize("artifact", ["decision", "companion"])
def test_rollback_absent_artifact_race_preserves_concurrent_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    artifact: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    selected_relative = operation.decision_artifact_path if artifact == "decision" else operation.companion_target_path
    selected = repo / selected_relative
    expected = operation.human_decision_bytes if artifact == "decision" else operation.replacement_companion
    assert expected is not None
    sentinel = f"concurrent {artifact}\n".encode()
    aside = selected.with_name(f"{selected.name}.transaction-owned")
    armed = [False]
    real_snapshot = module._RepositoryTargetGuard.snapshot

    def snapshot(self, relative: str):
        observed = real_snapshot(self, relative)
        if armed[0] and relative == selected_relative and observed.existed and observed.data == expected:
            armed[0] = False
            selected.rename(aside)
            selected.write_bytes(sentinel)
        return observed

    def fault(checkpoint: str) -> None:
        trigger = "after_decision_write" if artifact == "decision" else "after_companion_write"
        if checkpoint == trigger:
            armed[0] = True
            raise RuntimeError("begin rollback")

    monkeypatch.setattr(module._RepositoryTargetGuard, "snapshot", snapshot)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("rollback race must not validate"),
        sync_runner=lambda: pytest.fail("rollback race must not sync"),
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert selected.read_bytes() == sentinel
    assert aside.read_bytes() == expected
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert (output / f"planning-apply-{operation.operation_id}" / "transaction").is_dir()


def test_backed_up_recovery_discards_without_overwriting_concurrent_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    companion_path = repo / operation.companion_target_path
    concurrent_bytes = b"concurrent companion during cleanup\n"
    real_remove = module._remove_transaction_backup
    fail_cleanup = [True]

    def remove(operation_dir: Path) -> None:
        if fail_cleanup[0]:
            fail_cleanup[0] = False
            raise OSError("injected cleanup interruption")
        real_remove(operation_dir)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            companion_path.write_bytes(concurrent_bytes)

    monkeypatch.setattr(module, "_remove_transaction_backup", remove)
    interrupted = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
        fault_hook=fault,
    )
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert (interrupted.status, interrupted.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    assert companion_path.read_bytes() == concurrent_bytes
    assert (operation_dir / "transaction").is_dir()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "BACKED_UP"

    monkeypatch.setattr(
        module,
        "_restore_transaction",
        lambda *_args, **_kwargs: pytest.fail("BACKED_UP recovery must not restore"),
    )
    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("BACKED_UP recovery must not validate"),
        sync_runner=lambda: pytest.fail("BACKED_UP recovery must not sync"),
    )

    assert (recovered.status, recovered.reason) == ("stale", "apply_target_changed")
    assert companion_path.read_bytes() == concurrent_bytes
    assert not (repo / operation.decision_artifact_path).exists()
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "OPERATION_RECORDED"
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_backed_up_no_drift_recovery_discards_without_restore(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
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

    def crash(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            raise ProcessCrash

    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
            fault_hook=crash,
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert (operation_dir / "transaction").is_dir()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "BACKED_UP"
    assert {path: (repo / path).read_bytes() for path in targets} == documents_before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head

    monkeypatch.setattr(
        module,
        "_restore_transaction",
        lambda *_args, **_kwargs: pytest.fail("BACKED_UP recovery must not restore"),
    )
    recovered = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("BACKED_UP recovery must not validate"),
        sync_runner=lambda: pytest.fail("BACKED_UP recovery must not sync"),
    )

    assert (recovered.status, recovered.reason) == (
        "rolled_back",
        "planning_commit_failed",
    )
    assert {path: (repo / path).read_bytes() for path in targets} == documents_before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "ROLLED_BACK"


@pytest.mark.parametrize(
    ("invalid_state", "invalid_evidence"),
    [
        ("BOGUS", None),
        ("OPERATION_RECORDED", None),
        ("COMMITTED", None),
        ("PUSHED", None),
        ("REMOTE_PARITY", None),
        ("ROLLED_BACK", None),
        ("BACKED_UP", "publication.json"),
    ],
)
def test_transaction_recovery_rejects_invalid_durable_state_without_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_state: str,
    invalid_evidence: str | None,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    documents_before = {path: (repo / path).read_bytes() for path in targets}

    class ProcessCrash(BaseException):
        pass

    def crash(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            raise ProcessCrash

    with pytest.raises(ProcessCrash):
        module.execute_planning_apply_transaction(
            operation,
            repo_root=repo,
            output_dir=output,
            validation_runner=lambda: pytest.fail("crash must precede validation"),
            sync_runner=lambda: pytest.fail("crash must precede sync"),
            fault_hook=crash,
        )

    operation_dir = output / f"planning-apply-{operation.operation_id}"
    state_path = operation_dir / "state.json"
    state_path.write_bytes(
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "state": invalid_state,
        })
    )
    state_path.chmod(0o600)
    invalid_state_bytes = state_path.read_bytes()
    if invalid_evidence is not None:
        evidence_path = operation_dir / invalid_evidence
        evidence_path.write_bytes(b"{}\n")
        evidence_path.chmod(0o600)

    def fail_if_called(*_args, **_kwargs):
        pytest.fail(f"invalid recovery evidence {invalid_state}/{invalid_evidence} must be retained")

    monkeypatch.setattr(module, "_load_transaction_backup", fail_if_called)
    monkeypatch.setattr(module, "_restore_transaction", fail_if_called)
    monkeypatch.setattr(module, "_discard_pre_mutation_backup", fail_if_called)
    monkeypatch.setattr(module, "_remove_transaction_backup", fail_if_called)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("invalid recovery must not validate"),
        sync_runner=lambda: pytest.fail("invalid recovery must not sync"),
    )

    assert (result.status, result.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    assert {path: (repo / path).read_bytes() for path in targets} == documents_before
    assert not (repo / operation.companion_target_path).exists()
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert (operation_dir / "transaction").is_dir()
    assert state_path.read_bytes() == invalid_state_bytes
    assert state_path.stat().st_mode & 0o777 == 0o600
    if invalid_evidence is not None:
        assert (operation_dir / invalid_evidence).read_bytes() == b"{}\n"


def test_backed_up_without_transaction_is_fail_closed_before_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    operation_dir = module.record_planning_apply_operation(operation, output_dir=output)
    companion_path = repo / operation.companion_target_path
    concurrent_bytes = b"concurrent companion before state failure\n"
    real_set_state = module._set_operation_state

    def set_state(operation_path: Path, current_operation, state: str) -> None:
        if state == "OPERATION_RECORDED":
            raise OSError("injected state write failure")
        real_set_state(operation_path, current_operation, state)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_operation_recorded":
            companion_path.write_bytes(concurrent_bytes)

    monkeypatch.setattr(module, "_set_operation_state", set_state)
    first = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("stale apply must not validate"),
        sync_runner=lambda: pytest.fail("stale apply must not sync"),
        fault_hook=fault,
    )
    state_path = operation_dir / "state.json"
    state_bytes = state_path.read_bytes()
    attempts_before = tuple((operation_dir / "attempts").iterdir())
    assert (first.status, first.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    assert not (operation_dir / "transaction").exists()
    assert json.loads(state_bytes)["state"] == "BACKED_UP"
    assert companion_path.read_bytes() == concurrent_bytes

    def fail_if_called(*_args, **_kwargs):
        pytest.fail("BACKED_UP without transaction must stop before normal flow")

    monkeypatch.setattr(module, "_record_operation_attempt", fail_if_called)
    monkeypatch.setattr(module, "_persist_transaction_backup", fail_if_called)
    monkeypatch.setattr(module, "_restore_transaction", fail_if_called)
    monkeypatch.setattr(module, "_discard_pre_mutation_backup", fail_if_called)
    monkeypatch.setattr(module, "_remove_transaction_backup", fail_if_called)
    monkeypatch.setattr(module, "_run_git", fail_if_called)
    second = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("invalid retry must not validate"),
        sync_runner=lambda: pytest.fail("invalid retry must not sync"),
    )

    assert (second.status, second.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    assert state_path.read_bytes() == state_bytes
    assert tuple((operation_dir / "attempts").iterdir()) == attempts_before
    assert companion_path.read_bytes() == concurrent_bytes
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize(
    ("invalid_state", "orphan_publication"),
    [
        ("BACKED_UP", False),
        ("MUTATING", False),
        ("VALIDATED", False),
        ("SYNCED", False),
        ("STAGED", False),
        ("COMMITTED", False),
        ("PUSHED", False),
        ("REMOTE_PARITY", False),
        ("BOGUS", False),
        ("OPERATION_RECORDED", True),
        ("ROLLED_BACK", True),
    ],
)
def test_no_transaction_state_matrix_stops_before_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid_state: str,
    orphan_publication: bool,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    operation_dir = module.record_planning_apply_operation(operation, output_dir=output)
    state_path = operation_dir / "state.json"
    state_path.write_bytes(
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "state": invalid_state,
        })
    )
    state_path.chmod(0o600)
    if orphan_publication:
        publication = operation_dir / "publication.json"
        publication.write_bytes(b"{}\n")
        publication.chmod(0o600)
    evidence_before = {path.name: path.read_bytes() for path in operation_dir.iterdir() if path.is_file()}

    def fail_if_called(*_args, **_kwargs):
        pytest.fail(f"invalid no-transaction state {invalid_state} must stop before attempt")

    monkeypatch.setattr(module, "_record_operation_attempt", fail_if_called)
    monkeypatch.setattr(module, "_persist_transaction_backup", fail_if_called)
    monkeypatch.setattr(module, "_restore_transaction", fail_if_called)
    monkeypatch.setattr(module, "_discard_pre_mutation_backup", fail_if_called)
    monkeypatch.setattr(module, "_remove_transaction_backup", fail_if_called)
    monkeypatch.setattr(module, "_run_git", fail_if_called)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("invalid state must not validate"),
        sync_runner=lambda: pytest.fail("invalid state must not sync"),
    )

    assert (result.status, result.reason) == (
        "recovery_required",
        "restore_mismatch",
    )
    assert not tuple((operation_dir / "attempts").iterdir())
    assert {path.name: path.read_bytes() for path in operation_dir.iterdir() if path.is_file()} == evidence_before
    assert not (operation_dir / "transaction").exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


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
    assert not (repo / operation.companion_target_path).exists()
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
    fail = [True]

    real_push = module._push_operation_commit_cas

    def push_cas(**kwargs):
        if fail[0]:
            fail[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_push(**kwargs)

    monkeypatch.setattr(module, "_push_operation_commit_cas", push_cas)
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
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert json.loads((operation_dir / "state.json").read_bytes())["state"] == "ROLLED_BACK"

    retry = module.execute_planning_apply_transaction(
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
    )
    assert (retry.status, retry.reason) == ("ready", "adoption_published")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == _git(repo, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    "selected_target",
    ["design.md", "plan.md", "requirement.md", "companion", "decision"],
)
def test_staged_tree_proof_rejects_atomic_target_replacement_after_diff_proof(
    tmp_path: Path,
    selected_target: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    target_relative = {
        **{Path(path).name: path for path in targets},
        "companion": operation.companion_target_path,
        "decision": operation.decision_artifact_path,
    }[selected_target]
    target = repo / target_relative
    unauthorized = f"unauthorized {selected_target} bytes\n".encode()

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_diff_proof":
            replacement = target.with_name(f".{target.name}.unauthorized")
            replacement.write_bytes(unauthorized)
            replacement.replace(target)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert target.read_bytes() == unauthorized
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    transaction = operation_dir / "transaction"
    ledger = json.loads((transaction / "mutation-ledger.json").read_bytes())
    selected_entry = next(entry for entry in ledger["entries"] if entry["path"] == target_relative)
    authorized = {
        **operation.replacement_documents,
        "companion": operation.replacement_companion,
        "decision": operation.human_decision_bytes,
    }[selected_target]
    assert authorized is not None
    assert selected_entry["after_sha256"] == hashlib.sha256(authorized).hexdigest()
    assert (transaction / "backup-manifest.json").is_file()
    assert not (operation_dir / "commit.json").exists()
    assert not (operation_dir / "publication.json").exists()


def test_staged_tree_proof_rejects_index_only_poison_before_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    index_before = module.snapshot_git_index(repo)
    worktree_before = {
        path: module.snapshot_regular_file(repo / path)
        for path in (
            *targets,
            operation.companion_target_path,
            operation.decision_artifact_path,
        )
    }
    poisoned_relative = next(path for path in targets if Path(path).name == "requirement.md")
    unauthorized = b"unauthorized index-only blob\n"
    real_run_git = module._run_git
    injected = [False]

    def run_git(repo_root: Path, argv: tuple[str, ...], *, check: bool = False):
        result = real_run_git(repo_root, argv, check=check)
        if not injected[0] and argv and argv[0] == "add" and result.returncode == 0:
            injected[0] = True
            hashed = subprocess.run(
                ["git", "-C", repo.as_posix(), "hash-object", "-w", "--stdin"],
                input=unauthorized,
                check=True,
                capture_output=True,
            )
            poisoned_oid = hashed.stdout.decode("ascii").strip()
            subprocess.run(
                [
                    "git",
                    "-C",
                    repo.as_posix(),
                    "update-index",
                    "--cacheinfo",
                    "100644",
                    poisoned_oid,
                    poisoned_relative,
                ],
                check=True,
                capture_output=True,
            )
        return result

    monkeypatch.setattr(module, "_run_git", run_git)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert injected == [True]
    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert module.snapshot_git_index(repo) == index_before
    for path, before in worktree_before.items():
        assert module.snapshot_regular_file(repo / path) == before
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "transaction").exists()
    assert not (operation_dir / "commit.json").exists()
    assert not (operation_dir / "publication.json").exists()


def test_late_real_index_poison_stops_before_local_commit(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    index_before = module.snapshot_git_index(repo)
    poisoned_relative = next(path for path in targets if Path(path).name == "requirement.md")

    def fault(checkpoint: str) -> None:
        if checkpoint != "after_index_stage":
            return
        poisoned_oid = (
            subprocess
            .run(
                ["git", "-C", repo.as_posix(), "hash-object", "-w", "--stdin"],
                input=b"unauthorized late index blob\n",
                check=True,
                capture_output=True,
            )
            .stdout.decode("ascii")
            .strip()
        )
        _git(
            repo,
            "update-index",
            "--cacheinfo",
            "100644",
            poisoned_oid,
            poisoned_relative,
        )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert module.snapshot_git_index(repo) == index_before
    operation_dir = output / f"planning-apply-{operation.operation_id}"
    assert not (operation_dir / "commit.json").exists()
    assert not (operation_dir / "publication.json").exists()


def test_final_real_index_race_installs_only_verified_tree(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    poisoned_relative = next(path for path in targets if Path(path).name == "requirement.md")

    def fault(checkpoint: str) -> None:
        if checkpoint != "after_final_index_proof":
            return
        poisoned_oid = (
            subprocess
            .run(
                ["git", "-C", repo.as_posix(), "hash-object", "-w", "--stdin"],
                input=b"unauthorized final-race index blob\n",
                check=True,
                capture_output=True,
            )
            .stdout.decode("ascii")
            .strip()
        )
        _git(
            repo,
            "update-index",
            "--cacheinfo",
            "100644",
            poisoned_oid,
            poisoned_relative,
        )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == (
        "recovery_required",
        "post_commit_workspace_changed",
    )
    assert result.local_commit is not None
    assert result.local_tree is not None
    assert _git(repo, "rev-parse", "HEAD") == result.local_commit
    assert _git(repo, "rev-parse", f"{result.local_commit}^") == head
    assert _git(repo, "rev-parse", f"{result.local_commit}^{{tree}}") == result.local_tree
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    for relative in operation.canonical_target_paths:
        expected = operation.replacement_documents[Path(relative).name]
        observed = subprocess.run(
            ["git", "-C", repo.as_posix(), "show", f"{result.local_commit}:{relative}"],
            check=True,
            capture_output=True,
        ).stdout
        assert observed == expected


def test_operation_commit_runs_hooks_once_in_order_with_private_index(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    hook_log = tmp_path / "hook.log"
    expected_tree = tmp_path / "expected-tree"
    for name in ("pre-commit", "prepare-commit-msg", "commit-msg", "post-commit"):
        body = (
            f"printf '%s\\n' {shlex.quote(name)} >> {shlex.quote(hook_log.as_posix())}\n"
            f"git write-tree >> {shlex.quote(expected_tree.as_posix())}"
            if name == "pre-commit"
            else f"printf '%s\\n' {shlex.quote(name)} >> {shlex.quote(hook_log.as_posix())}"
        )
        _install_hook(repo, name, body)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert hook_log.read_text().splitlines() == [
        "pre-commit",
        "prepare-commit-msg",
        "commit-msg",
        "post-commit",
    ]
    assert expected_tree.read_text().strip() == result.local_tree
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == result.local_commit


def test_rejecting_pre_commit_hook_rolls_back_before_commit(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    _install_hook(repo, "pre-commit", "exit 42")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "commit.json").exists()


def test_private_index_mutating_pre_commit_hook_is_rejected(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    poisoned_relative = next(path for path in targets if Path(path).name == "requirement.md")
    _install_hook(
        repo,
        "pre-commit",
        (
            "oid=$(printf 'unauthorized hook blob\\n' | git hash-object -w --stdin)\n"
            f'git update-index --cacheinfo 100644 "$oid" {shlex.quote(poisoned_relative)}'
        ),
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize(
    "replacement",
    [
        "Not-SpecDock-Planning-Operation: {operation_id}",
        "SpecDock-Planning-Operation-Extra: {operation_id}",
        "SpecDock-Planning-Operation: prefix-{operation_id}",
        "SpecDock-Planning-Operation: {operation_id}-suffix",
        ("SpecDock-Planning-Operation: {operation_id}\nSpecDock-Planning-Operation: {operation_id}"),
        "SpecDock-Planning-Operation: {operation_id}\n\nnot a trailer",
    ],
)
def test_commit_message_hook_cannot_forge_operation_trailer(
    tmp_path: Path,
    replacement: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    message = replacement.format(operation_id=operation.operation_id)
    _install_hook(
        repo,
        "commit-msg",
        f"printf '%s\\n' {shlex.quote(message)} > \"$1\"",
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("rolled_back", "planning_commit_failed")
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_commit_message_hook_may_append_unrelated_trailer(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    _install_hook(repo, "commit-msg", "printf 'Reviewed-by: Human\\n' >> \"$1\"")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    message = _git(repo, "show", "-s", "--format=%B", result.local_commit)
    assert message.count(f"SpecDock-Planning-Operation: {operation.operation_id}") == 1
    assert "Reviewed-by: Human" in message
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == result.local_commit


@pytest.mark.parametrize(
    "forged_message",
    [
        ("subject\n\nSpecDock-Planning-Operation: {operation_id}\nSpecDock-Planning-Operation: {operation_id}\n"),
        "subject\n\nSpecDock-Planning-Operation: {operation_id}\n\nnot a trailer\n",
    ],
)
def test_resume_rejects_commit_without_one_exact_operation_trailer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    forged_message: str,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: module.GitCommandResult(
            returncode=1,
            stdout=b"",
            stderr=b"injected",
        ),
    )
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    assert pending.local_commit is not None
    assert pending.local_tree is not None
    message_path = tmp_path / "forged-message"
    message_path.write_text(
        forged_message.format(operation_id=operation.operation_id),
        encoding="utf-8",
    )
    forged = _git(
        repo,
        "commit-tree",
        pending.local_tree,
        "-p",
        head,
        "-F",
        message_path.as_posix(),
    )
    _git(
        repo,
        "update-ref",
        "refs/heads/feature/issue",
        forged,
        pending.local_commit,
    )
    evidence = output / f"planning-apply-{operation.operation_id}"
    (evidence / "commit.json").write_bytes(
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "local_commit": forged,
            "local_tree": pending.local_tree,
            "decision": operation.decision,
        })
    )
    monkeypatch.setattr(
        module,
        "_remote_head_observation",
        lambda *_args: pytest.fail("invalid resume commit must not observe remote"),
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


def test_branch_switch_at_commit_install_is_rejected_without_advancing_either_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    original_install = module._install_operation_commit_cas

    def switch_then_install(*args, **kwargs):
        _git(repo, "checkout", "-qb", "alternate", head)
        return original_install(*args, **kwargs)

    monkeypatch.setattr(module, "_install_operation_commit_cas", switch_then_install)
    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(repo, "rev-parse", "refs/heads/feature/issue") == head
    assert _git(repo, "rev-parse", "refs/heads/alternate") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    evidence = output / f"planning-apply-{operation.operation_id}"
    assert not (evidence / "commit.json").exists()
    assert not (evidence / "publication.json").exists()


def test_branch_switch_before_push_blocks_publication(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "before_push":
            _git(repo, "checkout", "-qb", "alternate")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == (
        "publication_pending",
        "remote_parity_unconfirmed",
    )
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "publication.json").exists()


def test_resume_from_alternate_branch_at_local_commit_fails_before_push(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: module.GitCommandResult(
            returncode=1,
            stdout=b"",
            stderr=b"injected",
        ),
    )
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    assert pending.local_commit is not None
    _git(repo, "checkout", "-qb", "alternate", pending.local_commit)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: pytest.fail("alternate-branch resume must not push"),
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "publication.json").exists()


def test_branch_switch_after_push_prevents_terminal_ready(tmp_path: Path) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_push":
            _git(repo, "checkout", "-qb", "alternate")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == (
        "publication_pending",
        "remote_parity_unconfirmed",
    )
    assert result.local_commit is not None
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == result.local_commit
    assert not (output / f"planning-apply-{operation.operation_id}" / "publication.json").exists()


def test_captured_publication_endpoint_ignores_origin_retarget_before_push(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    secondary = tmp_path / "secondary.git"
    subprocess.run(["git", "init", "--bare", "-q", secondary.as_posix()], check=True)
    _git(
        repo,
        "push",
        "-q",
        secondary.as_posix(),
        f"{head}:refs/heads/feature/issue",
    )
    hook = origin / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o700)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "before_push":
            _git(repo, "remote", "set-url", "origin", secondary.as_posix())

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("publication_pending", "push_failed")
    assert _git(secondary, "rev-parse", "refs/heads/feature/issue") == head
    assert not (output / f"planning-apply-{operation.operation_id}" / "publication.json").exists()


def test_post_push_parity_uses_captured_endpoint_after_origin_retarget(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    secondary = tmp_path / "secondary.git"
    subprocess.run(["git", "init", "--bare", "-q", secondary.as_posix()], check=True)
    _git(
        repo,
        "push",
        "-q",
        secondary.as_posix(),
        f"{head}:refs/heads/feature/issue",
    )
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)

    def fault(checkpoint: str) -> None:
        if checkpoint == "after_push":
            _git(repo, "remote", "set-url", "origin", secondary.as_posix())

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
        fault_hook=fault,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert result.local_commit is not None
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == result.local_commit
    assert _git(secondary, "rev-parse", "refs/heads/feature/issue") == head


def test_resume_rejects_retargeted_origin_before_remote_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    secondary = tmp_path / "secondary.git"
    subprocess.run(["git", "init", "--bare", "-q", secondary.as_posix()], check=True)
    _git(
        repo,
        "push",
        "-q",
        secondary.as_posix(),
        f"{head}:refs/heads/feature/issue",
    )
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    primary_endpoint = origin.as_posix()

    def strict_capture(current_operation, repo_root: Path):
        endpoint = _git(repo_root, "remote", "get-url", "--push", "origin")
        if endpoint != primary_endpoint:
            raise module.PlanningApplyRestoreMismatch("retargeted")
        return module._PublicationAuthority(
            repository=current_operation.repository.lower(),
            push_endpoint=endpoint,
        )

    monkeypatch.setattr(module, "_capture_publication_authority", strict_capture)
    monkeypatch.setattr(
        module,
        "_push_operation_commit_cas",
        lambda **_kwargs: module.GitCommandResult(
            returncode=1,
            stdout=b"",
            stderr=b"injected",
        ),
    )
    pending = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )
    assert (pending.status, pending.reason) == ("publication_pending", "push_failed")
    _git(repo, "remote", "set-url", "origin", secondary.as_posix())
    monkeypatch.setattr(
        module,
        "_remote_head_observation",
        lambda *_args: pytest.fail("retargeted resume must not observe a remote"),
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=lambda: pytest.fail("resume must not validate"),
        sync_runner=lambda: pytest.fail("resume must not sync"),
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert _git(secondary, "rev-parse", "refs/heads/feature/issue") == head


def test_reference_transaction_hook_is_delegated_once_per_phase(tmp_path: Path) -> None:
    module = _module()
    repo, _origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    hook_log = tmp_path / "reference-hook.log"
    _install_hook(
        repo,
        "reference-transaction",
        f"printf '%s\\n' \"$1\" >> {shlex.quote(hook_log.as_posix())}\ncat >/dev/null",
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    phases = hook_log.read_text().splitlines()
    assert phases.count("prepared") == 1
    assert phases.count("committed") == 1


def test_prepared_reference_hook_cannot_switch_checked_out_branch(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, _origin, head, targets = _repository(tmp_path)
    _git(repo, "branch", "alternate", head)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    switch_result = tmp_path / "switch-result"
    _install_hook(
        repo,
        "reference-transaction",
        (
            'if [ "$1" = prepared ]; then\n'
            "  set +e\n"
            f"  git -C {shlex.quote(repo.as_posix())} symbolic-ref HEAD refs/heads/alternate\n"
            "  switch_status=$?\n"
            "  set -e\n"
            f"  printf '%s\\n' \"$switch_status\" > {shlex.quote(switch_result.as_posix())}\n"
            "fi\n"
            "cat >/dev/null"
        ),
    )

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert switch_result.read_text().strip() != "0"
    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert _git(repo, "symbolic-ref", "-q", "HEAD") == "refs/heads/feature/issue"


def test_existing_foreign_head_lock_aborts_install_without_ref_change(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    head_lock = repo / ".git" / "HEAD.lock"
    foreign_lock = b"foreign-git-operation\n"
    head_lock.write_bytes(foreign_lock)
    head_lock.chmod(0o600)

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == ("recovery_required", "restore_mismatch")
    assert _git(repo, "symbolic-ref", "-q", "HEAD") == "refs/heads/feature/issue"
    assert _git(repo, "rev-parse", "refs/heads/feature/issue") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
    assert head_lock.read_bytes() == foreign_lock
    evidence = output / f"planning-apply-{operation.operation_id}"
    assert not (evidence / "commit.json").exists()
    assert not (evidence / "publication.json").exists()


def test_post_commit_hook_workspace_mutation_preserves_recovery_gate(
    tmp_path: Path,
) -> None:
    module = _module()
    repo, origin, head, targets = _repository(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    operation = _operation(repo, head, targets)
    target = next(path for path in targets if Path(path).name == "requirement.md")
    _install_hook(repo, "post-commit", f"printf 'post hook mutation\\n' > {shlex.quote(target)}")

    result = module.execute_planning_apply_transaction(
        operation,
        repo_root=repo,
        output_dir=output,
        validation_runner=_validation_ok,
        sync_runner=_sync_ok,
    )

    assert (result.status, result.reason) == (
        "recovery_required",
        "post_commit_workspace_changed",
    )
    assert result.local_commit is not None
    assert _git(repo, "rev-parse", "HEAD") == result.local_commit
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head


@pytest.mark.parametrize(
    "checkpoint",
    [
        "after_decision_write",
        "after_requirement_replace",
        "after_design_replace",
        "after_plan_replace",
        "after_companion_write",
        "after_companion_parity",
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
    assert not (repo / operation.companion_target_path).exists()
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
        "validation_runner": lambda: type("V", (), {"report": type("R", (), {"errors": []})()})(),
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
    fail = [True]

    real_push = module._push_operation_commit_cas

    def push_cas(**kwargs):
        if fail[0]:
            fail[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_push(**kwargs)

    monkeypatch.setattr(module, "_push_operation_commit_cas", push_cas)
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
    transaction = output / f"planning-apply-{operation.operation_id}" / "transaction"
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
            ("artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"): b"onboarding companion\n",
        },
        source_baseline={
            "canonical_issue_paths": list(targets),
            "relevant_paths": [],
            "source_manifest_hash": "c" * 64,
        },
        zip_bytes=b"candidate",
        onboarding_companion=contracts.OnboardingCompanionBindingV1(
            path=("artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"),
            sha256=hashlib.sha256(b"onboarding companion\n").hexdigest(),
        ),
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
    fail_push = [True]

    real_push = module._push_operation_commit_cas

    def push_cas(**kwargs):
        if fail_push[0]:
            fail_push[0] = False
            return module.GitCommandResult(returncode=1, stdout=b"", stderr=b"hidden")
        return real_push(**kwargs)

    monkeypatch.setattr(module, "_push_operation_commit_cas", push_cas)

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
            dependencies=PLANNING_DEPENDENCIES,
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
        "after_decision_write",
        "after_plan_replace",
        "after_companion_write",
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
    assert not (repo / operation.companion_target_path).exists()
    assert module.snapshot_git_index(repo) == index_before
    assert module.snapshot_managed_sync_state(repo) == managed_before
    assert not (repo / operation.decision_artifact_path).exists()
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(origin, "rev-parse", "refs/heads/feature/issue") == head
