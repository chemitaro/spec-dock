from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
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


def _blob_oid(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _module():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_apply",
        fromlist=["PlanningApplyOperation"],
    )


def test_reference_transaction_payloads_are_byte_exact_and_closed() -> None:
    module = _module()
    branch = f"{HEAD} {'b' * 40} refs/heads/feature/issue"
    head = f"{HEAD} {'b' * 40} HEAD"
    allowed = module._reference_transaction_payloads(branch, head)

    assert allowed == (
        f"{branch}\n".encode("ascii"),
        f"{head}\n{branch}\n".encode("ascii"),
        f"{branch}\n{head}\n".encode("ascii"),
    )
    for payload in allowed:
        assert module._reference_transaction_payload_is_expected(
            payload,
            expected_branch_update=branch,
            expected_head_update=head,
        )

    rejected = (
        branch.encode("ascii"),
        f"{branch}\r\n".encode("ascii"),
        f"\n{branch}\n".encode("ascii"),
        f"{branch}\n\n".encode("ascii"),
        f"{branch}\n{branch}\n".encode("ascii"),
        f"{branch}\n{head}\n{branch}\n".encode("ascii"),
        f"{HEAD} {'c' * 40} refs/heads/feature/issue\n".encode("ascii"),
        f"{branch} extra\n".encode("ascii"),
    )
    for payload in rejected:
        assert not module._reference_transaction_payload_is_expected(
            payload,
            expected_branch_update=branch,
            expected_head_update=head,
        )


def test_reference_transaction_payloads_fail_closed_for_non_ascii_records() -> None:
    module = _module()
    assert module._reference_transaction_payloads("refs/heads/é", "HEAD") == ()
    assert not module._reference_transaction_payload_is_expected(
        b"refs/heads/\xff\n",
        expected_branch_update="refs/heads/é",
        expected_head_update="HEAD",
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
    pre_apply_document_bytes = {
        "design.md": b"old design\n",
        "plan.md": b"old plan\n",
        "requirement.md": b"old requirement\n",
    }
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
            "spec-dock/initiatives/i/epics/e/issues/x/design.md": _blob_oid(pre_apply_document_bytes["design.md"]),
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md": _blob_oid(pre_apply_document_bytes["plan.md"]),
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md": _blob_oid(
                pre_apply_document_bytes["requirement.md"]
            ),
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
        "pre_apply_document_bytes": pre_apply_document_bytes,
    }
    values.update(changes)
    return module.PlanningApplyOperation.create(**values)


def _workspace_intent_fixture(tmp_path: Path):
    module = _module()
    operation = _operation()
    repo = tmp_path / "repo"
    relative = operation.canonical_target_paths[0]
    target = repo / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(b"before\n")
    target.chmod(0o640)
    guard = module._RepositoryTargetGuard.capture(repo, (relative,))
    output = tmp_path / "output"
    output.mkdir()
    handle = module.record_planning_apply_operation(operation, output_dir=output)
    module._mkdir_private_at(handle, "transaction")
    module._write_private_no_replace_at(
        handle,
        "transaction/mutation-ledger.json",
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "workspace_intent": None,
            "entries": [],
        }),
    )
    return module, operation, repo, relative, target, guard, handle


def _absent_workspace_intent_fixture(tmp_path: Path):
    module = _module()
    operation = _operation()
    repo = tmp_path / "repo"
    relative = operation.decision_artifact_path
    target = repo / relative
    target.parent.mkdir(parents=True)
    guard = module._RepositoryTargetGuard.capture(repo, (relative,))
    output = tmp_path / "output"
    output.mkdir()
    handle = module.record_planning_apply_operation(operation, output_dir=output)
    module._mkdir_private_at(handle, "transaction")
    module._write_private_no_replace_at(
        handle,
        "transaction/mutation-ledger.json",
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "workspace_intent": None,
            "entries": [],
        }),
    )
    outer = guard.compare_replace(
        relative,
        expected=guard.snapshot(relative),
        replacement=operation.human_decision_bytes,
        mode=0o600,
    )
    assert outer is not None
    mutations = [outer]
    module._persist_target_mutations(handle, operation, mutations)
    return module, operation, relative, target, guard, handle, outer, mutations


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


def test_operation_rejects_incoherent_canonical_preimage_evidence() -> None:
    with pytest.raises(ValueError, match="planning apply preimage evidence mismatch"):
        _operation(
            pre_apply_target_blob_oids={
                "spec-dock/initiatives/i/epics/e/issues/x/design.md": "1" * 40,
                "spec-dock/initiatives/i/epics/e/issues/x/plan.md": "2" * 40,
                "spec-dock/initiatives/i/epics/e/issues/x/requirement.md": "3" * 40,
            }
        )


def test_expected_staged_blob_oids_are_derived_only_from_operation_authority() -> None:
    module = _module()
    approved = _operation()
    approved_expected = module._expected_staged_blob_oids(
        approved,
        expected_companion_oid=None,
    )
    for relative in approved.canonical_target_paths:
        assert approved_expected[relative] == _blob_oid(approved.replacement_documents[Path(relative).name])
    assert approved_expected[approved.companion_target_path] == _blob_oid(COMPANION)
    assert approved_expected[approved.decision_artifact_path] == _blob_oid(approved.human_decision_bytes)

    existing_companion_oid = "f" * 40
    rejected = module.dataclass_replace(
        approved,
        decision="rejected",
        replacement_companion=None,
    )
    rejected_expected = module._expected_staged_blob_oids(
        rejected,
        expected_companion_oid=existing_companion_oid,
    )
    for relative in rejected.canonical_target_paths:
        assert rejected_expected[relative] == rejected.pre_apply_target_blob_oids[relative]
    assert rejected_expected[rejected.companion_target_path] == existing_companion_oid
    assert rejected_expected[rejected.decision_artifact_path] == _blob_oid(rejected.human_decision_bytes)
    assert (
        module._expected_staged_blob_oids(
            rejected,
            expected_companion_oid=None,
        )[rejected.companion_target_path]
        is None
    )


def test_tree_blob_oids_reads_one_closed_tree_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    tree = "d" * 40
    oid = "e" * 40
    relatives = ("b.md", "a.md")
    observed: list[tuple[str, ...]] = []

    def run_git(_repo: Path, argv: tuple[str, ...], *, check: bool = False):
        assert check is False
        observed.append(argv)
        return module.GitCommandResult(
            returncode=0,
            stdout=f"100644 blob {oid}\ta.md\0".encode(),
            stderr=b"",
        )

    monkeypatch.setattr(module, "_run_git", run_git)

    assert module._tree_blob_oids(tmp_path, tree, relatives) == {
        "b.md": None,
        "a.md": oid,
    }
    assert observed == [
        ("ls-tree", "-r", "-z", tree, "--", "a.md", "b.md"),
    ]


@pytest.mark.parametrize(
    ("returncode", "stdout"),
    [
        (1, b""),
        (0, b"100644 blob " + b"e" * 40 + b"\ta.md"),
        (0, b"malformed\0"),
        (0, b"100644 blob " + b"e" * 40 + b"\ta-\xff.md\0"),
        (
            0,
            b"100644 blob " + b"e" * 40 + b"\ta.md\0" + b"100644 blob " + b"e" * 40 + b"\ta.md\0",
        ),
        (0, b"100644 blob " + b"e" * 40 + b"\tunexpected.md\0"),
        (0, b"040000 tree " + b"e" * 40 + b"\ta.md\0"),
        (0, b"100644 blob invalid\ta.md\0"),
    ],
)
def test_tree_blob_oids_fails_closed_for_unprovable_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    returncode: int,
    stdout: bytes,
) -> None:
    module = _module()
    monkeypatch.setattr(
        module,
        "_run_git",
        lambda _repo, _argv: module.GitCommandResult(
            returncode=returncode,
            stdout=stdout,
            stderr=b"",
        ),
    )

    assert module._tree_blob_oids(tmp_path, "d" * 40, ("a.md", "b.md")) is None


def test_decision_artifact_path_is_deterministic_from_operation_id() -> None:
    operation = _operation()
    assert operation.decision_artifact_path.endswith(f"-planning-human-decision-{operation.operation_id[:16]}.json")
    assert not Path(operation.decision_artifact_path).is_absolute()


def test_operation_evidence_is_private_and_collision_is_rejected(tmp_path: Path) -> None:
    module = _module()
    operation = _operation()
    handle = module.record_planning_apply_operation(operation, output_dir=tmp_path)
    path = handle.logical_operation_path
    assert stat.S_IMODE(path.stat().st_mode) == 0o700
    manifest = path / "operation.json"
    assert stat.S_IMODE(manifest.stat().st_mode) == 0o600
    assert manifest.read_bytes() == operation.operation_core_bytes
    handle.close()
    resumed = module.record_planning_apply_operation(operation, output_dir=tmp_path)
    assert resumed.logical_operation_path == path
    resumed.close()
    manifest.chmod(0o600)
    manifest.write_bytes(b"{}\n")
    with pytest.raises(module.PlanningApplyOutputRejected):
        module.record_planning_apply_operation(operation, output_dir=tmp_path)


def test_load_operation_state_rejects_unknown_durable_state(tmp_path: Path) -> None:
    module = _module()
    operation = _operation()
    handle = module.record_planning_apply_operation(operation, output_dir=tmp_path)
    state_path = handle.logical_operation_path / "state.json"
    state_path.write_bytes(
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "state": "BOGUS",
        })
    )
    state_path.chmod(0o600)

    with pytest.raises(module.PlanningApplyRestoreMismatch, match="operation state is invalid"):
        module._load_operation_state(handle, operation)
    handle.close()


@pytest.mark.parametrize(
    "argv",
    [
        ("git", "push", "--force"),
        ("git", "push", "--force-with-lease"),
        ("git", "push", f"--force-with-lease=refs/heads/main:{HEAD}"),
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


def test_private_index_runner_rejects_update_ref(tmp_path: Path) -> None:
    module = _module()
    workspace = tmp_path / "private"
    workspace.mkdir(mode=0o700)

    with pytest.raises(module.PlanningApplyUnsafeGitCommand):
        module._run_git_with_private_index(
            tmp_path,
            workspace / "index",
            ("update-ref", "refs/heads/feature/issue", "c" * 40, HEAD),
        )


@pytest.mark.parametrize(
    ("config_returncode", "config_stdout", "expected_signed"),
    [
        (0, b"true\n", True),
        (0, b"false\n", False),
        (1, b"", False),
    ],
)
def test_verified_commit_preserves_repository_signing_intent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    config_returncode: int,
    config_stdout: bytes,
    expected_signed: bool,
) -> None:
    module = _module()
    operation = _operation()
    local_tree = "d" * 40
    local_commit = "c" * 40
    observed: list[tuple[str, ...]] = []

    def private_git(_repo: Path, _index: Path, argv: tuple[str, ...]):
        observed.append(argv)
        stdout = (
            f"{local_tree}\n".encode()
            if argv == ("write-tree",)
            else (f"{local_commit}\n".encode() if argv[0] == "commit-tree" else b"")
        )
        return module.GitCommandResult(returncode=0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(module, "_run_git_with_private_index", private_git)
    monkeypatch.setattr(
        module,
        "_run_git",
        lambda _repo, argv: module.GitCommandResult(
            returncode=config_returncode,
            stdout=config_stdout,
            stderr=b"",
        ),
    )
    monkeypatch.setattr(
        module,
        "_git_text",
        lambda _repo, *argv: local_tree if argv == ("write-tree",) else None,
    )
    monkeypatch.setattr(module, "_operation_commit_is_proven", lambda *_args, **_kwargs: True)

    result = module._create_verified_operation_commit(
        operation,
        repo_root=tmp_path,
        local_tree=local_tree,
        expected_paths={"decision.json"},
        subject="subject",
        fault_hook=None,
    )

    assert result == local_commit
    commit_tree_argv = next(argv for argv in observed if argv[0] == "commit-tree")
    assert (commit_tree_argv[-1] == "-S") is expected_signed


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (b"subject\n\nSpecDock-Planning-Operation: operation-1\n", True),
        (
            b"subject\n\nSpecDock-Planning-Operation: operation-1\nReviewed-by: Human\n",
            True,
        ),
        (b"subject\n\nNot-SpecDock-Planning-Operation: operation-1\n", False),
        (b"subject\n\nSpecDock-Planning-Operation-Extra: operation-1\n", False),
        (b"subject\n\nSpecDock-Planning-Operation: prefix-operation-1\n", False),
        (b"subject\n\nSpecDock-Planning-Operation: operation-1-suffix\n", False),
        (
            b"subject\n\nSpecDock-Planning-Operation: operation-1\nSpecDock-Planning-Operation: operation-1\n",
            False,
        ),
        (
            b"subject\n\nSpecDock-Planning-Operation: operation-1\nSpecDock-Planning-Operation: another\n",
            False,
        ),
        (
            b"subject\n\nSpecDock-Planning-Operation: operation-1\n\nnot a trailer\n",
            False,
        ),
    ],
)
def test_operation_trailer_proof_requires_one_exact_terminal_trailer(
    tmp_path: Path,
    message: bytes,
    expected: bool,
) -> None:
    module = _module()
    assert (
        module._operation_trailer_is_proven(
            tmp_path,
            message=message,
            operation_id="operation-1",
        )
        is expected
    )


def test_operation_branch_commit_proof_binds_symbolic_head_and_branch_ref(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    operation = _operation()
    local_commit = "c" * 40
    values = {
        ("symbolic-ref", "-q", "HEAD"): "refs/heads/feature/issue",
        ("rev-parse", "refs/heads/feature/issue"): local_commit,
        ("rev-parse", "HEAD"): local_commit,
    }
    monkeypatch.setattr(module, "_git_text", lambda _repo, *argv: values.get(argv))

    branch_lock = module._OperationBranchLock(
        path=tmp_path / "HEAD.lock",
        descriptor=-1,
        device=0,
        inode=0,
        mode=0o600,
        destination="refs/heads/feature/issue",
        expected_commit=local_commit,
        ref_process=object(),
        hook_root=tmp_path,
    )
    monkeypatch.setattr(branch_lock, "assert_held", lambda: None)
    assert module._operation_branch_commit_is_proven(
        operation,
        tmp_path,
        local_commit,
        branch_lock=branch_lock,
    )
    values["symbolic-ref", "-q", "HEAD"] = "refs/heads/alternate"
    assert not module._operation_branch_commit_is_proven(
        operation,
        tmp_path,
        local_commit,
        branch_lock=branch_lock,
    )


def test_operation_branch_commit_proof_rejects_unbound_lock_object(
    tmp_path: Path,
) -> None:
    module = _module()
    operation = _operation()
    with pytest.raises(module.PlanningApplyRestoreMismatch):
        module._operation_branch_commit_is_proven(
            operation,
            tmp_path,
            "c" * 40,
            branch_lock=object(),
        )


@pytest.mark.parametrize(
    ("umask", "expected_mode"),
    [(0o022, 0o644), (0o077, 0o600)],
)
def test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask(
    tmp_path: Path,
    umask: int,
    expected_mode: int,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", repo.as_posix(), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", repo.as_posix(), "config", "user.name", "Tester"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", repo.as_posix(), "config", "user.email", "tester@example.com"],
        check=True,
    )
    (repo / "initial.txt").write_text("initial\n", encoding="utf-8")
    subprocess.run(["git", "-C", repo.as_posix(), "add", "--", "initial.txt"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "commit", "-qm", "initial"], check=True)
    subprocess.run(["git", "-C", repo.as_posix(), "branch", "-M", "feature/issue"], check=True)
    local_commit = subprocess.run(
        ["git", "-C", repo.as_posix(), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    operation = SimpleNamespace(branch="feature/issue")
    previous_umask = os.umask(umask)
    try:
        with module._acquire_operation_branch_lock(repo, operation, local_commit) as branch_lock:
            assert branch_lock.mode == expected_mode
            assert stat.S_IMODE(branch_lock.path.stat().st_mode) == expected_mode
    finally:
        os.umask(previous_umask)

    assert not (repo / ".git" / "HEAD.lock").exists()
    assert not (repo / ".git" / "refs" / "heads" / "feature" / "issue.lock").exists()


class _FakeOperationRefStream:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def write(self, _data: bytes) -> int:
        self.events.append("write")
        return 6

    def flush(self) -> None:
        self.events.append("flush")

    def close(self) -> None:
        self.events.append("close")


class _FakeOperationRefProcess:
    def __init__(self, events: list[str], *, returncode: int = 0) -> None:
        self.events = events
        self.returncode = returncode
        self.stdin = _FakeOperationRefStream(events)
        self.stdout = None
        self.stderr = None
        self._status: int | None = None

    def poll(self) -> int | None:
        return self._status

    def wait(self, *, timeout: int) -> int:
        assert timeout == 5
        self.events.append("wait")
        self._status = self.returncode
        return self.returncode

    def kill(self) -> None:
        self.events.append("kill")
        self._status = -9


def _operation_branch_lock_fixture(
    tmp_path: Path,
    *,
    returncode: int = 0,
    mode: int = 0o600,
):
    module = _module()
    path = tmp_path / "HEAD.lock"
    path.write_bytes(b"owned\n")
    path.chmod(mode)
    descriptor = os.open(path, os.O_RDONLY)
    opened = os.fstat(descriptor)
    hook_root = tmp_path / "hooks"
    hook_root.mkdir()
    events: list[str] = []
    process = _FakeOperationRefProcess(events, returncode=returncode)
    lock = module._OperationBranchLock(
        path=path,
        descriptor=descriptor,
        device=opened.st_dev,
        inode=opened.st_ino,
        mode=mode,
        destination="refs/heads/feature/issue",
        expected_commit="c" * 40,
        ref_process=process,
        hook_root=hook_root,
    )
    return module, lock, path, events


@pytest.mark.parametrize("mode", [0o600, 0o644])
def test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: int,
) -> None:
    module, lock, path, events = _operation_branch_lock_fixture(tmp_path, mode=mode)
    real_remove = module._remove_captured_operation_head_lock

    def remove(*args):
        events.append("remove")
        return real_remove(*args)

    monkeypatch.setattr(module, "_remove_captured_operation_head_lock", remove)
    with lock:
        pass

    assert events.index("wait") < events.index("remove")
    assert not path.exists()


@pytest.mark.parametrize("mode", [0o600, 0o644])
def test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock(
    tmp_path: Path,
    mode: int,
) -> None:
    module, lock, path, _events = _operation_branch_lock_fixture(tmp_path, returncode=1, mode=mode)
    before = path.stat()

    with pytest.raises(module.PlanningApplyRestoreMismatch), lock:
        pass

    after = path.stat()
    assert path.read_bytes() == b"owned\n"
    assert (after.st_dev, after.st_ino, after.st_mode, after.st_uid) == (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_uid,
    )


def test_operation_branch_lock_mode_change_is_preserved_without_protocol_abort(
    tmp_path: Path,
) -> None:
    module, lock, path, events = _operation_branch_lock_fixture(tmp_path, mode=0o644)
    path.chmod(0o600)
    before = path.stat()

    with pytest.raises(module.PlanningApplyRestoreMismatch), lock:
        pass

    after = path.stat()
    assert (after.st_dev, after.st_ino, after.st_mode, after.st_uid) == (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_uid,
    )
    assert "write" not in events
    assert "kill" in events


def test_operation_branch_lock_mode_change_after_abort_is_preserved_without_fallback_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, lock, path, events = _operation_branch_lock_fixture(tmp_path, mode=0o644)
    real_abort = module._abort_operation_ref_transaction

    def abort_and_change(process) -> None:
        real_abort(process)
        path.chmod(0o600)

    monkeypatch.setattr(module, "_abort_operation_ref_transaction", abort_and_change)
    before = path.stat()
    with pytest.raises(module.PlanningApplyRestoreMismatch), lock:
        pass

    after = path.stat()
    assert path.exists()
    assert (after.st_dev, after.st_ino, after.st_uid) == (
        before.st_dev,
        before.st_ino,
        before.st_uid,
    )
    assert stat.S_IMODE(after.st_mode) == 0o600
    assert "write" in events


def test_operation_branch_lock_replaced_head_lock_is_preserved_without_protocol_abort(
    tmp_path: Path,
) -> None:
    module, lock, path, events = _operation_branch_lock_fixture(tmp_path)
    path.unlink()
    path.write_bytes(b"foreign\n")
    path.chmod(0o600)
    foreign = path.read_bytes()

    with pytest.raises(module.PlanningApplyRestoreMismatch), lock:
        pass

    assert path.read_bytes() == foreign
    assert "write" not in events
    assert "kill" in events


def test_operation_branch_lock_disappeared_head_lock_is_abandoned_without_unlink(
    tmp_path: Path,
) -> None:
    module, lock, path, events = _operation_branch_lock_fixture(tmp_path)
    path.unlink()

    with pytest.raises(module.PlanningApplyRestoreMismatch), lock:
        pass

    assert not path.exists()
    assert "write" not in events
    assert "kill" in events


def test_dedicated_push_uses_exact_expected_old_lease(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    local_commit = "c" * 40
    local_tree = "d" * 40
    observed: list[tuple[str, ...]] = []

    def git_text(_repo: Path, *argv: str) -> str | None:
        if argv == ("check-ref-format", "--branch", "feature/issue"):
            return "feature/issue"
        if argv == ("rev-parse", "HEAD"):
            return local_commit
        if argv == ("symbolic-ref", "-q", "HEAD"):
            return "refs/heads/feature/issue"
        if argv == ("rev-parse", "refs/heads/feature/issue"):
            return local_commit
        if argv == ("rev-parse", f"{local_commit}^"):
            return HEAD
        if argv == ("rev-parse", f"{local_commit}^{{tree}}"):
            return local_tree
        return None

    def run(argv, **_kwargs):
        observed.append(tuple(argv))
        return subprocess.CompletedProcess(argv, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(module, "_git_text", git_text)
    monkeypatch.setattr(module.subprocess, "run", run)
    operation = _operation()
    authority = module._PublicationAuthority(
        repository="owner/repo",
        push_endpoint="git@github.com:owner/repo.git",
    )
    branch_lock = module._OperationBranchLock(
        path=tmp_path / "HEAD.lock",
        descriptor=-1,
        device=0,
        inode=0,
        mode=0o600,
        destination="refs/heads/feature/issue",
        expected_commit=local_commit,
        ref_process=object(),
        hook_root=tmp_path,
    )
    monkeypatch.setattr(branch_lock, "assert_held", lambda: None)
    result = module._push_operation_commit_cas(
        operation,
        repo_root=tmp_path,
        authority=authority,
        expected_remote_head=HEAD,
        local_commit=local_commit,
        local_tree=local_tree,
        branch_lock=branch_lock,
    )

    assert result.returncode == 0
    assert observed == [
        (
            "git",
            "-C",
            tmp_path.as_posix(),
            "push",
            f"--force-with-lease=refs/heads/feature/issue:{HEAD}",
            "git@github.com:owner/repo.git",
            f"{local_commit}:refs/heads/feature/issue",
        )
    ]


def test_publication_authority_requires_reviewed_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    git_cli = __import__(
        "spec_dock_runtime.infra.git_cli",
        fromlist=["origin_github_publication_endpoint"],
    )
    monkeypatch.setattr(
        git_cli,
        "origin_github_publication_endpoint",
        lambda _repo: ("owner/repo", "https://github.com/owner/repo.git"),
    )
    authority = module._capture_publication_authority(_operation(), tmp_path)
    assert authority == module._PublicationAuthority(
        repository="owner/repo",
        push_endpoint="https://github.com/owner/repo.git",
    )

    monkeypatch.setattr(
        git_cli,
        "origin_github_publication_endpoint",
        lambda _repo: ("other/repo", "https://github.com/other/repo.git"),
    )
    with pytest.raises(module.PlanningApplyRestoreMismatch):
        module._capture_publication_authority(_operation(), tmp_path)


@pytest.mark.parametrize(
    ("fetch_url", "push_url", "expected"),
    [
        (
            "https://github.com/Owner/Repo.git",
            "https://github.com/Owner/Repo.git",
            ("owner/repo", "https://github.com/Owner/Repo.git"),
        ),
        (
            "git@github.com:Owner/Repo.git",
            "ssh://git@github.com/Owner/Repo.git",
            ("owner/repo", "ssh://git@github.com/Owner/Repo.git"),
        ),
    ],
)
def test_git_cli_captures_exact_github_push_endpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fetch_url: str,
    push_url: str,
    expected: tuple[str, str],
) -> None:
    git_cli = __import__(
        "spec_dock_runtime.infra.git_cli",
        fromlist=["origin_github_publication_endpoint"],
    )
    monkeypatch.setattr(
        git_cli,
        "_remote_get_url",
        lambda _repo, *, push: push_url if push else fetch_url,
    )

    assert git_cli.origin_github_publication_endpoint(tmp_path) == expected
    assert git_cli.origin_github_repo_slug(tmp_path) == expected[0]


@pytest.mark.parametrize(
    ("fetch_url", "push_url"),
    [
        ("https://github.com/owner/repo.git", "https://github.com/other/repo.git"),
        ("https://example.com/owner/repo.git", "https://example.com/owner/repo.git"),
        ("malformed", "malformed"),
        ("https://token:secret@github.com/owner/repo.git", "https://github.com/owner/repo.git"),
        ("https://github.com/owner/repo.git", "https://token:secret@github.com/owner/repo.git"),
    ],
)
def test_git_cli_rejects_unprovable_publication_endpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fetch_url: str,
    push_url: str,
) -> None:
    git_cli = __import__(
        "spec_dock_runtime.infra.git_cli",
        fromlist=["origin_github_publication_endpoint"],
    )
    monkeypatch.setattr(
        git_cli,
        "_remote_get_url",
        lambda _repo, *, push: push_url if push else fetch_url,
    )

    with pytest.raises(RuntimeError) as error:
        git_cli.origin_github_publication_endpoint(tmp_path)
    assert "token" not in str(error.value)
    assert "secret" not in str(error.value)


def test_cas_failure_with_unavailable_remote_preserves_push_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    monkeypatch.setattr(
        module,
        "_remote_head_observation",
        lambda _repo, _authority, _branch: ("unavailable", None),
    )

    result = module._cas_failure_result(
        _operation(),
        repo_root=tmp_path,
        authority=module._PublicationAuthority(
            repository="owner/repo",
            push_endpoint="git@github.com:owner/repo.git",
        ),
        local_commit="c" * 40,
        local_tree="d" * 40,
    )

    assert result is not None
    assert (result.status, result.reason) == ("publication_pending", "push_failed")


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


def test_dangling_symlink_destination_is_rejected_before_mutation_and_preserved(
    tmp_path: Path,
) -> None:
    module = _module()
    target = tmp_path / "companion.md"
    target.symlink_to("missing-destination.md")
    original_link = target.readlink()

    with pytest.raises(ValueError, match="regular non-symlink"):
        module.snapshot_regular_file(target)

    assert target.is_symlink()
    assert target.readlink() == original_link
    assert not (tmp_path / "missing-destination.md").exists()


def test_repository_target_parent_walk_rejects_symlink_component(tmp_path: Path) -> None:
    module = _module()
    repo = tmp_path / "repo"
    external = tmp_path / "external"
    repo.mkdir()
    (external / "nested").mkdir(parents=True)
    (repo / "linked").symlink_to(external, target_is_directory=True)

    with pytest.raises(ValueError, match="directory traversal rejected"):
        module._RepositoryTargetGuard.capture(
            repo,
            ("linked/nested/target.md",),
        )

    assert not (external / "nested" / "target.md").exists()


def test_descriptor_relative_atomic_write_survives_lexical_parent_replacement(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    parent = repo / "parent"
    parent.mkdir(parents=True)
    guard = module._RepositoryTargetGuard.capture(repo, ("parent/target.md",))
    captured = repo / "captured-parent"
    parent.rename(captured)
    parent.mkdir()
    try:
        mutation = guard.compare_replace(
            "parent/target.md",
            expected=module.FileSnapshot(
                existed=False,
                data=b"",
                mode=0,
                sha256=hashlib.sha256(b"").hexdigest(),
            ),
            replacement=b"captured\n",
            mode=0o644,
        )
    finally:
        guard.close()

    assert mutation is not None
    assert (captured / "target.md").read_bytes() == b"captured\n"
    assert not (parent / "target.md").exists()


@pytest.mark.parametrize(
    ("platform", "backend"),
    [
        ("linux", "_exchange_entries_linux_at"),
        ("darwin", "_exchange_entries_darwin_at"),
    ],
)
def test_atomic_exchange_dispatches_verified_descriptor_and_names(
    monkeypatch: pytest.MonkeyPatch,
    platform: str,
    backend: str,
) -> None:
    module = _module()
    observed: list[tuple[int, str, int, str]] = []
    monkeypatch.setattr(module.sys, "platform", platform)
    monkeypatch.setattr(
        module,
        backend,
        lambda source_fd, first, destination_fd, second: observed.append((source_fd, first, destination_fd, second)),
    )

    module._exchange_entries_at(17, ".staged", 23, "target.md")

    assert observed == [(17, ".staged", 23, "target.md")]


@pytest.mark.parametrize(
    ("backend_name", "symbol_name"),
    [
        ("_exchange_entries_linux_at", "renameat2"),
        ("_exchange_entries_darwin_at", "renameatx_np"),
    ],
)
def test_atomic_exchange_backends_pass_parent_descriptor_names_and_swap_flag(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
) -> None:
    module = _module()
    calls: list[tuple[object, ...]] = []

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *args):
            calls.append(args)
            return 0

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    getattr(module, backend_name)(17, ".staged", 23, "target.md")

    assert calls == [(17, b".staged", 23, b"target.md", 0x00000002)]


@pytest.mark.parametrize(
    ("backend_name", "symbol_name", "message"),
    [
        ("_exchange_entries_linux_at", "renameat2", "renameat2 is unavailable"),
        ("_exchange_entries_darwin_at", "renameatx_np", "renameatx_np is unavailable"),
    ],
)
def test_atomic_exchange_backends_fail_closed_when_native_symbol_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    message: str,
) -> None:
    module = _module()

    class FakeLibrary:
        pass

    library = FakeLibrary()
    assert not hasattr(library, symbol_name)
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    with pytest.raises(NotImplementedError, match=message):
        getattr(module, backend_name)(17, ".staged", 23, "target.md")


@pytest.mark.parametrize(
    ("backend_name", "symbol_name"),
    [
        ("_exchange_entries_linux_at", "renameat2"),
        ("_exchange_entries_darwin_at", "renameatx_np"),
    ],
)
def test_atomic_exchange_backends_preserve_native_errno(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
) -> None:
    module = _module()

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *_args):
            return -1

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)
    monkeypatch.setattr(module.ctypes, "get_errno", lambda: errno.EBUSY)

    with pytest.raises(OSError) as captured:
        getattr(module, backend_name)(17, ".staged", 23, "target.md")

    assert captured.value.errno == errno.EBUSY
    assert captured.value.filename == "target.md"


def test_atomic_exchange_fails_closed_on_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    monkeypatch.setattr(module.sys, "platform", "unsupported")

    with pytest.raises(NotImplementedError, match="atomic exchange is unavailable"):
        module._exchange_entries_at(17, ".staged", 23, "target.md")


@pytest.mark.parametrize(
    ("backend_name", "symbol_name", "expected_flag"),
    [
        ("_rename_no_replace_linux_at", "renameat2", 0x00000001),
        ("_rename_no_replace_darwin_at", "renameatx_np", 0x00000004),
    ],
)
def test_no_replace_backends_pass_distinct_descriptors_names_and_flag(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    expected_flag: int,
) -> None:
    module = _module()
    calls: list[tuple[object, ...]] = []

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *args):
            calls.append(args)
            return 0

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    getattr(module, backend_name)(17, "source", 23, "destination")

    assert calls == [(17, b"source", 23, b"destination", expected_flag)]


@pytest.mark.parametrize(
    ("backend_name", "symbol_name", "message"),
    [
        ("_rename_no_replace_linux_at", "renameat2", "renameat2 is unavailable"),
        ("_rename_no_replace_darwin_at", "renameatx_np", "renameatx_np is unavailable"),
    ],
)
def test_no_replace_backends_fail_closed_when_native_symbol_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    message: str,
) -> None:
    module = _module()

    class FakeLibrary:
        pass

    library = FakeLibrary()
    assert not hasattr(library, symbol_name)
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    with pytest.raises(NotImplementedError, match=message):
        getattr(module, backend_name)(17, "source", 23, "destination")


@pytest.mark.parametrize(
    ("backend_name", "symbol_name"),
    [
        ("_rename_no_replace_linux_at", "renameat2"),
        ("_rename_no_replace_darwin_at", "renameatx_np"),
    ],
)
def test_no_replace_backends_preserve_eexist(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
) -> None:
    module = _module()

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *_args):
            return -1

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(module.ctypes, "CDLL", lambda *_args, **_kwargs: library)
    monkeypatch.setattr(module.ctypes, "get_errno", lambda: errno.EEXIST)

    with pytest.raises(FileExistsError) as captured:
        getattr(module, backend_name)(17, "source", 23, "destination")

    assert captured.value.errno == errno.EEXIST
    assert captured.value.filename == "destination"


def test_mutation_intent_is_durable_before_namespace_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, operation, _repo, relative, target, guard, handle = _workspace_intent_fixture(tmp_path)
    mutations: list[Any] = []
    observed_entries: list[dict[str, object]] = []
    real_exchange = module._exchange_entries_at

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        ledger = json.loads(
            module._read_private_file_at(
                handle,
                "transaction/mutation-ledger.json",
            )
        )
        observed_entries.extend(ledger["entries"])
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    try:
        module._apply_guarded_mutation(
            guard,
            handle,
            operation,
            mutations,
            relative=relative,
            expected=module.snapshot_regular_file(target),
            replacement=b"replacement\n",
            mode=0o644,
        )
    finally:
        guard.close()
        handle.close()

    assert len(observed_entries) == 1
    prepared = observed_entries[0]
    assert prepared["path"] == relative
    assert prepared["phase"] == "prepared"
    assert prepared["staged_name"] == "staged"
    assert isinstance(prepared["workspace_device"], int)
    assert isinstance(prepared["workspace_inode"], int)
    assert isinstance(prepared["staged_device"], int)
    assert isinstance(prepared["staged_inode"], int)


def test_prepared_absent_publication_resolves_with_empty_workspace_slot(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    guard = module._RepositoryTargetGuard.capture(repo, ("artifact.md",))
    prepared: list[Any] = []

    class ProcessCrash(BaseException):
        pass

    try:
        with pytest.raises(ProcessCrash):
            guard.compare_replace(
                "artifact.md",
                expected=guard.snapshot("artifact.md"),
                replacement=b"published\n",
                mode=0o644,
                prepare=prepared.append,
                publish=lambda _mutation: (_ for _ in ()).throw(ProcessCrash),
            )

        assert len(prepared) == 1
        resolved = guard.resolve_prepared(prepared[0])

        assert resolved is not None
        assert resolved.phase == "published"
        assert guard.snapshot("artifact.md") == resolved.after
        guard.restore(resolved)
        assert not (repo / "artifact.md").exists()
    finally:
        guard.close()


def test_existing_restore_intent_is_durable_before_reverse_exchange(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    target.chmod(0o640)
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    operation = _operation()
    output = tmp_path / "output"
    output.mkdir()
    handle = module.record_planning_apply_operation(operation, output_dir=output)
    module._mkdir_private_at(handle, "transaction")
    module._write_private_no_replace_at(
        handle,
        "transaction/mutation-ledger.json",
        module._canonical_json_bytes({
            "operation_id": operation.operation_id,
            "workspace_intent": None,
            "entries": [],
        }),
    )
    outer = guard.compare_replace(
        "target.md",
        expected=guard.snapshot("target.md"),
        replacement=b"after\n",
        mode=0o600,
    )
    assert outer is not None
    mutations = [outer]
    module._persist_target_mutations(handle, operation, mutations)
    observed: dict[str, object] = {}
    real_exchange = module._exchange_entries_at

    class ProcessCrash(BaseException):
        pass

    def phase_update(updated) -> None:
        mutations[0] = updated
        module._persist_target_mutations(handle, operation, mutations)

    def crash_after_exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        ledger = json.loads(
            module._read_private_file_at(
                handle,
                "transaction/mutation-ledger.json",
            )
        )
        observed.update(ledger["entries"][0])
        observed["workspace_identity"] = (
            os.fstat(source_fd).st_dev,
            os.fstat(source_fd).st_ino,
        )
        staged = os.stat(first, dir_fd=source_fd, follow_symlinks=False)
        observed["staged_identity"] = (staged.st_dev, staged.st_ino)
        real_exchange(source_fd, first, destination_fd, second)
        raise ProcessCrash

    monkeypatch.setattr(module, "_exchange_entries_at", crash_after_exchange)
    try:
        with pytest.raises(ProcessCrash):
            guard.restore(outer, phase_update=phase_update)

        assert observed["phase"] == "rollback-prepared"
        assert (observed["workspace_device"], observed["workspace_inode"]) == observed["workspace_identity"]
        assert (observed["staged_device"], observed["staged_inode"]) == observed["staged_identity"]
        assert (observed["after_device"], observed["after_inode"]) == (
            outer.after_device,
            outer.after_inode,
        )
        assert observed["after_sha256"] == outer.after.sha256
        assert mutations[0].before == outer.before
        assert mutations[0].after == outer.after
        assert target.read_bytes() == b"before\n"
        workspace = repo / mutations[0].workspace_name
        assert (workspace / mutations[0].staged_name).read_bytes() == b"after\n"

        monkeypatch.setattr(module, "_exchange_entries_at", real_exchange)
        guard.restore(mutations[0], phase_update=phase_update)

        assert target.read_bytes() == b"before\n"
        assert stat.S_IMODE(target.stat().st_mode) == 0o640
        assert not workspace.exists()
    finally:
        guard.close()
        handle.close()


def test_existing_restore_resume_workspace_slot_swap_preserves_unknown_and_displaced_after(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    outer = guard.compare_replace(
        "target.md",
        expected=guard.snapshot("target.md"),
        replacement=b"after\n",
        mode=0o600,
    )
    assert outer is not None
    recorded: list[Any] = []
    real_exchange = module._exchange_entries_at

    class ProcessCrash(BaseException):
        pass

    def crash_after_exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        real_exchange(source_fd, first, destination_fd, second)
        raise ProcessCrash

    monkeypatch.setattr(module, "_exchange_entries_at", crash_after_exchange)
    try:
        with pytest.raises(ProcessCrash):
            guard.restore(outer, phase_update=lambda updated: recorded.append(updated))

        assert len(recorded) == 1
        rollback = recorded[0]
        workspace = repo / rollback.workspace_name
        displaced = workspace / "displaced-after"
        staged = workspace / rollback.staged_name
        staged.rename(displaced)
        staged.write_bytes(b"unknown\n")

        monkeypatch.setattr(module, "_exchange_entries_at", real_exchange)
        with pytest.raises(module.PlanningApplyRestoreMismatch):
            guard.restore(rollback)

        assert target.read_bytes() == b"before\n"
        assert staged.read_bytes() == b"unknown\n"
        assert displaced.read_bytes() == b"after\n"
        assert workspace.is_dir()
    finally:
        guard.close()


def test_workspace_ownership_intent_is_durable_before_forward_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, operation, _repo, relative, target, guard, handle = _workspace_intent_fixture(tmp_path)
    mutations: list[Any] = []
    observed: dict[str, Any] = {}
    real_mkdir = module.os.mkdir

    class ProcessCrash(BaseException):
        pass

    def crash_before_mkdir(path, mode=0o777, *, dir_fd=None) -> None:
        if isinstance(path, str) and path.startswith(".spec-dock-apply-"):
            ledger = json.loads(
                module._read_private_file_at(
                    handle,
                    "transaction/mutation-ledger.json",
                )
            )
            observed.update(ledger)
            observed["mkdir_name"] = path
            raise ProcessCrash
        real_mkdir(path, mode=mode, dir_fd=dir_fd)

    monkeypatch.setattr(module.os, "mkdir", crash_before_mkdir)
    try:
        with pytest.raises(ProcessCrash):
            module._apply_guarded_mutation(
                guard,
                handle,
                operation,
                mutations,
                relative=relative,
                expected=guard.snapshot(relative),
                replacement=b"after\n",
                mode=0o600,
            )

        intent = observed["workspace_intent"]
        assert observed["entries"] == []
        assert intent["path"] == relative
        assert intent["purpose"] == "forward"
        assert intent["workspace_name"] == observed["mkdir_name"]
        assert intent["workspace_device"] is None
        assert intent["workspace_inode"] is None
        assert intent["staged_device"] is None
        assert intent["staged_inode"] is None
        assert not tuple(target.parent.glob(".spec-dock-apply-*"))

        monkeypatch.setattr(module.os, "mkdir", real_mkdir)
        module._recover_workspace_intent(guard, handle, operation, mutations)
        ledger = json.loads(module._read_private_file_at(handle, "transaction/mutation-ledger.json"))
        assert ledger["workspace_intent"] is None
        assert target.read_bytes() == b"before\n"
    finally:
        guard.close()
        handle.close()


def test_existing_restore_workspace_intent_is_durable_before_reverse_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, operation, _repo, relative, target, guard, handle = _workspace_intent_fixture(tmp_path)
    outer = guard.compare_replace(
        relative,
        expected=guard.snapshot(relative),
        replacement=b"after\n",
        mode=0o600,
    )
    assert outer is not None
    mutations = [outer]
    module._persist_target_mutations(handle, operation, mutations)
    observed: dict[str, Any] = {}
    real_mkdir = module.os.mkdir

    class ProcessCrash(BaseException):
        pass

    def update_intent(intent) -> None:
        module._persist_workspace_intent(handle, operation, mutations, intent)

    def phase_update(updated) -> None:
        mutations[0] = updated
        module._persist_target_mutations(handle, operation, mutations)

    def crash_before_mkdir(path, mode=0o777, *, dir_fd=None) -> None:
        if isinstance(path, str) and path.startswith(".spec-dock-apply-"):
            ledger = json.loads(
                module._read_private_file_at(
                    handle,
                    "transaction/mutation-ledger.json",
                )
            )
            observed.update(ledger)
            observed["mkdir_name"] = path
            raise ProcessCrash
        real_mkdir(path, mode=mode, dir_fd=dir_fd)

    monkeypatch.setattr(module.os, "mkdir", crash_before_mkdir)
    try:
        with pytest.raises(ProcessCrash):
            guard.restore(
                outer,
                phase_update=phase_update,
                workspace_intent_update=update_intent,
            )

        assert len(observed["entries"]) == 1
        entry = observed["entries"][0]
        assert entry["phase"] == "published"
        assert (entry["after_device"], entry["after_inode"]) == (
            outer.after_device,
            outer.after_inode,
        )
        intent = observed["workspace_intent"]
        assert intent["path"] == relative
        assert intent["purpose"] == "rollback-existing"
        assert intent["workspace_name"] == observed["mkdir_name"]
        assert intent["workspace_device"] is None
        assert intent["staged_device"] is None

        monkeypatch.setattr(module.os, "mkdir", real_mkdir)
        module._recover_workspace_intent(guard, handle, operation, mutations)
        guard.restore(
            outer,
            phase_update=phase_update,
            workspace_intent_update=update_intent,
        )
        assert target.read_bytes() == b"before\n"
        assert stat.S_IMODE(target.stat().st_mode) == 0o640
        assert not tuple(target.parent.glob(".spec-dock-apply-*"))
    finally:
        guard.close()
        handle.close()


@pytest.mark.parametrize(
    "boundary",
    [
        "before_mkdir",
        "after_mkdir_before_workspace_binding",
        "after_workspace_and_staged_binding",
    ],
)
def test_workspace_intent_recovery_classifies_creation_boundaries(
    tmp_path: Path,
    boundary: str,
) -> None:
    module, operation, _repo, relative, target, guard, handle = _workspace_intent_fixture(tmp_path)
    name = ".spec-dock-apply-" + "1" * 32
    workspace = target.parent / name
    workspace_device = workspace_inode = staged_device = staged_inode = None
    if boundary != "before_mkdir":
        workspace.mkdir(mode=0o700)
    if boundary == "after_workspace_and_staged_binding":
        workspace_stat = workspace.stat()
        workspace_device, workspace_inode = workspace_stat.st_dev, workspace_stat.st_ino
        staged = workspace / "staged"
        staged.write_bytes(b"partial")
        staged_stat = staged.stat()
        staged_device, staged_inode = staged_stat.st_dev, staged_stat.st_ino
    intent = module._WorkspaceIntent(
        relative=relative,
        purpose="forward",
        workspace_name=name,
        workspace_device=workspace_device,
        workspace_inode=workspace_inode,
        staged_name="staged",
        staged_device=staged_device,
        staged_inode=staged_inode,
    )
    try:
        module._persist_workspace_intent(handle, operation, [], intent)
        module._recover_workspace_intent(guard, handle, operation, [])

        ledger = json.loads(module._read_private_file_at(handle, "transaction/mutation-ledger.json"))
        assert ledger["workspace_intent"] is None
        assert ledger["entries"] == []
        assert target.read_bytes() == b"before\n"
        assert not workspace.exists()
    finally:
        guard.close()
        handle.close()


@pytest.mark.parametrize(
    "ambiguity",
    ["unbound_unknown", "bound_wrong_inode", "bound_extra"],
)
def test_workspace_intent_recovery_preserves_ambiguous_nonempty_workspace(
    tmp_path: Path,
    ambiguity: str,
) -> None:
    module, operation, _repo, relative, target, guard, handle = _workspace_intent_fixture(tmp_path)
    name = ".spec-dock-apply-" + "2" * 32
    workspace = target.parent / name
    workspace.mkdir(mode=0o700)
    workspace_stat = workspace.stat()
    workspace_device = workspace_inode = staged_device = staged_inode = None
    if ambiguity == "unbound_unknown":
        (workspace / "unknown").write_bytes(b"sentinel")
    else:
        workspace_device, workspace_inode = workspace_stat.st_dev, workspace_stat.st_ino
        staged = workspace / "staged"
        staged.write_bytes(b"owned")
        staged_stat = staged.stat()
        staged_device, staged_inode = staged_stat.st_dev, staged_stat.st_ino
        if ambiguity == "bound_wrong_inode":
            staged.rename(workspace / "displaced")
            staged.write_bytes(b"unknown")
        else:
            (workspace / "extra").write_bytes(b"sentinel")
    intent = module._WorkspaceIntent(
        relative=relative,
        purpose="forward",
        workspace_name=name,
        workspace_device=workspace_device,
        workspace_inode=workspace_inode,
        staged_name="staged",
        staged_device=staged_device,
        staged_inode=staged_inode,
    )
    before = {path.name: path.read_bytes() for path in workspace.iterdir()}
    try:
        module._persist_workspace_intent(handle, operation, [], intent)
        ledger_before = module._read_private_file_at(handle, "transaction/mutation-ledger.json")
        with pytest.raises(module.PlanningApplyRestoreMismatch):
            module._recover_workspace_intent(guard, handle, operation, [])

        assert workspace.is_dir()
        assert {path.name: path.read_bytes() for path in workspace.iterdir()} == before
        assert module._read_private_file_at(handle, "transaction/mutation-ledger.json") == ledger_before
        assert target.read_bytes() == b"before\n"
    finally:
        guard.close()
        handle.close()


def test_absent_restore_workspace_intent_is_durable_before_rollback_mkdir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, operation, relative, target, guard, handle, outer, mutations = _absent_workspace_intent_fixture(tmp_path)
    observed: dict[str, Any] = {}
    real_mkdir = module.os.mkdir

    class ProcessCrash(BaseException):
        pass

    def update_intent(intent) -> None:
        module._persist_workspace_intent(handle, operation, mutations, intent)

    def phase_update(updated) -> None:
        mutations[0] = updated
        module._persist_target_mutations(handle, operation, mutations)

    def crash_before_mkdir(path, mode=0o777, *, dir_fd=None) -> None:
        if isinstance(path, str) and path.startswith(".spec-dock-apply-"):
            observed.update(
                json.loads(
                    module._read_private_file_at(
                        handle,
                        "transaction/mutation-ledger.json",
                    )
                )
            )
            observed["mkdir_name"] = path
            raise ProcessCrash
        real_mkdir(path, mode=mode, dir_fd=dir_fd)

    monkeypatch.setattr(module.os, "mkdir", crash_before_mkdir)
    try:
        with pytest.raises(ProcessCrash):
            guard.restore(
                outer,
                phase_update=phase_update,
                workspace_intent_update=update_intent,
            )

        assert len(observed["entries"]) == 1
        assert observed["entries"][0]["phase"] == "published"
        intent = observed["workspace_intent"]
        assert intent["purpose"] == "rollback-absent"
        assert intent["path"] == relative
        assert intent["workspace_name"] == observed["mkdir_name"]
        assert intent["staged_name"] == "quarantine"
        assert intent["workspace_device"] is None
        assert intent["workspace_inode"] is None
        assert intent["staged_device"] is None
        assert intent["staged_inode"] is None

        monkeypatch.setattr(module.os, "mkdir", real_mkdir)
        module._recover_workspace_intent(guard, handle, operation, mutations)
        assert mutations == [outer]
        assert target.read_bytes() == operation.human_decision_bytes
        assert not tuple(target.parent.glob(".spec-dock-apply-*"))
        guard.restore(
            outer,
            phase_update=phase_update,
            workspace_intent_update=update_intent,
        )
        assert not target.exists()
        assert not tuple(target.parent.glob(".spec-dock-apply-*"))
    finally:
        guard.close()
        handle.close()


@pytest.mark.parametrize(
    "boundary",
    [
        "before_mkdir",
        "after_mkdir_before_bind",
        "after_workspace_bind",
        "after_rollback_prepared_handoff",
    ],
)
def test_absent_restore_workspace_intent_recovery_classifies_boundaries(
    tmp_path: Path,
    boundary: str,
) -> None:
    module, operation, relative, target, guard, handle, outer, mutations = _absent_workspace_intent_fixture(tmp_path)
    name = ".spec-dock-apply-" + "3" * 32
    workspace = target.parent / name
    workspace_device = workspace_inode = staged_device = staged_inode = None
    if boundary != "before_mkdir":
        workspace.mkdir(mode=0o700)
    if boundary in {"after_workspace_bind", "after_rollback_prepared_handoff"}:
        opened = workspace.stat()
        workspace_device, workspace_inode = opened.st_dev, opened.st_ino
        staged_device, staged_inode = outer.after_device, outer.after_inode
    intent = module._WorkspaceIntent(
        relative=relative,
        purpose="rollback-absent",
        workspace_name=name,
        workspace_device=workspace_device,
        workspace_inode=workspace_inode,
        staged_name="quarantine",
        staged_device=staged_device,
        staged_inode=staged_inode,
    )
    if boundary == "after_rollback_prepared_handoff":
        mutations[0] = module.dataclass_replace(
            outer,
            phase="rollback-prepared",
            workspace_name=name,
            workspace_device=workspace_device,
            workspace_inode=workspace_inode,
            staged_name="quarantine",
            staged_device=outer.after_device,
            staged_inode=outer.after_inode,
        )
        module._persist_target_mutations(handle, operation, mutations)
    try:
        module._persist_workspace_intent(handle, operation, mutations, intent)
        module._recover_workspace_intent(guard, handle, operation, mutations)

        ledger = json.loads(module._read_private_file_at(handle, "transaction/mutation-ledger.json"))
        assert ledger["workspace_intent"] is None
        assert target.read_bytes() == operation.human_decision_bytes
        if boundary == "after_rollback_prepared_handoff":
            assert workspace.is_dir()
            guard.restore(mutations[0])
            assert not target.exists()
            assert not workspace.exists()
        else:
            assert mutations == [outer]
            assert not workspace.exists()
    finally:
        guard.close()
        handle.close()


@pytest.mark.parametrize(
    "ambiguity",
    [
        "unbound_unknown",
        "bound_quarantine",
        "bound_extra",
        "replaced_workspace",
    ],
)
def test_absent_restore_workspace_intent_preserves_ambiguous_nonempty_workspace(
    tmp_path: Path,
    ambiguity: str,
) -> None:
    module, operation, relative, target, guard, handle, outer, mutations = _absent_workspace_intent_fixture(tmp_path)
    name = ".spec-dock-apply-" + "4" * 32
    workspace = target.parent / name
    workspace.mkdir(mode=0o700)
    opened = workspace.stat()
    workspace_device = workspace_inode = staged_device = staged_inode = None
    if ambiguity == "unbound_unknown":
        (workspace / "unknown").write_bytes(b"sentinel")
    else:
        workspace_device, workspace_inode = opened.st_dev, opened.st_ino
        staged_device, staged_inode = outer.after_device, outer.after_inode
        if ambiguity == "bound_quarantine":
            os.link(target, workspace / "quarantine")
        elif ambiguity == "bound_extra":
            (workspace / "extra").write_bytes(b"sentinel")
        else:
            workspace.rename(target.parent / "displaced-workspace")
            workspace.mkdir(mode=0o700)
            (workspace / "unknown").write_bytes(b"replacement")
    intent = module._WorkspaceIntent(
        relative=relative,
        purpose="rollback-absent",
        workspace_name=name,
        workspace_device=workspace_device,
        workspace_inode=workspace_inode,
        staged_name="quarantine",
        staged_device=staged_device,
        staged_inode=staged_inode,
    )
    try:
        module._persist_workspace_intent(handle, operation, mutations, intent)
        assert module._load_workspace_intent(handle, operation) == intent
        ledger_before = module._read_private_file_at(handle, "transaction/mutation-ledger.json")
        target_before = target.read_bytes()
        with pytest.raises(module.PlanningApplyRestoreMismatch):
            module._recover_workspace_intent(guard, handle, operation, mutations)

        assert target.read_bytes() == target_before
        assert workspace.is_dir()
        assert module._read_private_file_at(handle, "transaction/mutation-ledger.json") == ledger_before
        assert mutations == [outer]
    finally:
        guard.close()
        handle.close()


def test_compare_replace_mismatch_exchanges_back_and_preserves_current_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    expected = module.snapshot_regular_file(target)
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    real_exchange = module._exchange_entries_at
    injected = [False]

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        if not injected[0]:
            injected[0] = True
            target.write_bytes(b"concurrent\n")
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    try:
        with pytest.raises(module._ApplyTargetDrift):
            guard.compare_replace(
                "target.md",
                expected=expected,
                replacement=b"replacement\n",
                mode=0o644,
            )
    finally:
        guard.close()

    assert target.read_bytes() == b"concurrent\n"
    assert not any(path.name.startswith(".target.md.") for path in repo.iterdir())


@pytest.mark.parametrize(
    "editor_bytes",
    [b"editor replacement\n", b"before\n"],
    ids=["byte-different", "byte-identical-distinct-inode"],
)
def test_compare_replace_atomic_editor_swap_after_open_restores_actual_attachment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    editor_bytes: bytes,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    expected = module.snapshot_regular_file(target)
    opened_inode = target.stat().st_ino
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    real_exchange = module._exchange_entries_at
    exchange_count = [0]
    editor_identity: list[tuple[int, int]] = []
    prepared: list[Any] = []
    discarded: list[Any] = []

    def exchange(source_fd: int, first: str, destination_fd: int, second: str) -> None:
        exchange_count[0] += 1
        if exchange_count[0] == 1:
            editor = repo / "editor.tmp"
            editor.write_bytes(editor_bytes)
            editor.replace(target)
            observed = target.stat()
            editor_identity.append((observed.st_dev, observed.st_ino))
            assert observed.st_ino != opened_inode
        real_exchange(source_fd, first, destination_fd, second)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    try:
        with pytest.raises(module._ApplyTargetDrift):
            guard.compare_replace(
                "target.md",
                expected=expected,
                replacement=b"transaction replacement\n",
                mode=0o644,
                prepare=prepared.append,
                discard=discarded.append,
            )
    finally:
        guard.close()

    observed = target.stat()
    assert exchange_count == [2]
    assert (observed.st_dev, observed.st_ino) == editor_identity[0]
    assert target.read_bytes() == editor_bytes
    assert discarded == prepared
    assert len(discarded) == 1
    assert not tuple(repo.glob(".spec-dock-apply-*"))


def test_compare_replace_staged_name_swap_before_exchange_preserves_unknown_and_preimage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"preimage\n")
    expected = module.snapshot_regular_file(target)
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    real_exchange = module._exchange_entries_at
    unknown = b"unknown staged replacement\n"
    owned_names: list[str] = []

    def exchange(*args) -> None:
        source_fd, source_name = args[:2]
        owned_name = f"{source_name}.owned"
        owned_names.append(owned_name)
        module.os.rename(
            source_name,
            owned_name,
            src_dir_fd=source_fd,
            dst_dir_fd=source_fd,
        )
        descriptor = module.os.open(
            source_name,
            module.os.O_WRONLY | module.os.O_CREAT | module.os.O_EXCL,
            0o600,
            dir_fd=source_fd,
        )
        try:
            module.os.write(descriptor, unknown)
        finally:
            module.os.close(descriptor)
        real_exchange(*args)

    monkeypatch.setattr(module, "_exchange_entries_at", exchange)
    try:
        with pytest.raises(module.PlanningApplyRestoreMismatch):
            guard.compare_replace(
                "target.md",
                expected=expected,
                replacement=b"replacement\n",
                mode=0o644,
            )
    finally:
        guard.close()

    available = [path.read_bytes() for path in repo.rglob("*") if path.is_file()]
    assert b"preimage\n" in available
    assert unknown in available
    assert b"replacement\n" in available
    assert owned_names


def test_reverse_compare_replace_does_not_overwrite_unknown_postmutation_bytes(
    tmp_path: Path,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    try:
        mutation = guard.compare_replace(
            "target.md",
            expected=module.snapshot_regular_file(target),
            replacement=b"replacement\n",
            mode=0o644,
        )
        assert mutation is not None
        unknown = repo / "unknown"
        unknown.write_bytes(b"unknown\n")
        unknown.replace(target)

        with pytest.raises(
            module.PlanningApplyRestoreMismatch,
            match="transaction-owned target changed",
        ):
            guard.restore(mutation)
    finally:
        guard.close()

    assert target.read_bytes() == b"unknown\n"


def test_target_restore_accepts_exact_already_restored_preimage(tmp_path: Path) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    target.write_bytes(b"before\n")
    target.chmod(0o640)
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    try:
        mutation = guard.compare_replace(
            "target.md",
            expected=module.snapshot_regular_file(target),
            replacement=b"replacement\n",
            mode=0o644,
        )
        assert mutation is not None
        guard.restore(mutation)
        guard.restore(mutation)
    finally:
        guard.close()

    assert target.read_bytes() == b"before\n"
    assert stat.S_IMODE(target.stat().st_mode) == 0o640


def test_target_restore_accepts_exact_already_restored_absence(tmp_path: Path) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    try:
        mutation = guard.compare_replace(
            "target.md",
            expected=module.snapshot_regular_file(target),
            replacement=b"replacement\n",
            mode=0o644,
        )
        assert mutation is not None
        guard.restore(mutation)
        guard.restore(mutation)
    finally:
        guard.close()

    assert not target.exists()


def test_absent_restore_post_verification_swap_preserves_unknown_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    try:
        mutation = guard.compare_replace(
            "target.md",
            expected=module.snapshot_regular_file(target),
            replacement=b"transaction-owned\n",
            mode=0o644,
        )
        assert mutation is not None
        real_snapshot = guard.snapshot
        swapped = [False]
        unknown = b"unknown concurrent bytes\n"

        def snapshot(relative: str):
            observed = real_snapshot(relative)
            if relative == "target.md" and observed == mutation.after and not swapped[0]:
                swapped[0] = True
                target.rename(repo / "transaction-owned-aside")
                target.write_bytes(unknown)
            return observed

        monkeypatch.setattr(guard, "snapshot", snapshot)
        with pytest.raises(module.PlanningApplyRestoreMismatch):
            guard.restore(mutation)
    finally:
        guard.close()

    assert target.read_bytes() == b"unknown concurrent bytes\n"
    assert (repo / "transaction-owned-aside").read_bytes() == b"transaction-owned\n"


def test_absent_restore_missing_native_primitive_preserves_owned_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "target.md"
    guard = module._RepositoryTargetGuard.capture(repo, ("target.md",))
    try:
        mutation = guard.compare_replace(
            "target.md",
            expected=module.snapshot_regular_file(target),
            replacement=b"transaction-owned\n",
            mode=0o644,
        )
        assert mutation is not None

        def unavailable(*_args) -> None:
            raise NotImplementedError("native primitive unavailable")

        monkeypatch.setattr(
            module,
            "_rename_no_replace_at",
            unavailable,
        )

        with pytest.raises(NotImplementedError, match="native primitive unavailable"):
            guard.restore(mutation)
    finally:
        guard.close()

    assert target.read_bytes() == b"transaction-owned\n"


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
