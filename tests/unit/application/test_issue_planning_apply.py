from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path, PurePath
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application import issue_planning  # noqa: E402
from spec_dock_runtime.application.ports import (  # noqa: E402
    IssuePlanningCandidateArchiveRejected,
    IssuePlanningDependencies,
)
from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    GitBoundOperationBindingV1,
    IssueCandidateIdentity,
    OnboardingCompanionBindingV1,
    PlanningHumanDecisionV1,
    PlanningReviewFinding,
    PlanningReviewResult,
    ReviewedPlanningIdentity,
)

HEAD = "a" * 40
ZIP_SHA = "b" * 64
SOURCE_HASH = "c" * 64
COMPANION_PATH = "artifacts/20260729t000000z-guide-new-member.md"
COMPANION_BYTES = b"onboarding companion\n"
COMPANION_SHA = hashlib.sha256(COMPANION_BYTES).hexdigest()


@dataclass(frozen=True)
class _StoredMetaRecord:
    kind: str
    id: str
    title: str
    slug: str
    path: str
    parent_id: str | None
    initiative_id: str | None
    epic_id: str | None
    github_issue_number: int | None
    meta_path: str


@dataclass(frozen=True)
class _VerifiedIssueCandidate:
    identity: IssueCandidateIdentity
    files: dict[str, bytes]
    source_baseline: dict[str, object]
    zip_bytes: bytes
    onboarding_companion: OnboardingCompanionBindingV1


@dataclass(frozen=True)
class _PlanningApplyExecution:
    status: str
    reason: str
    operation_id: str
    decision_artifact_path: str | None = None
    local_commit: str | None = None
    local_tree: str | None = None
    remote_commit: str | None = None
    details: tuple[str, ...] = ()

    def to_output(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "decision_artifact_path": self.decision_artifact_path,
            "local_commit": self.local_commit,
            "local_tree": self.local_tree,
            "remote_commit": self.remote_commit,
        }


class _FakeClock:
    def now_iso(self) -> str:
        return "2026-07-28T12:00:00+00:00"

    def today(self) -> str:
        return "2026-07-28"


class _FakeIssuePlanningGateway:
    def validate_candidate_output_directory(self, output_dir: Path, repo_root: Path) -> Path:
        output = output_dir.resolve(strict=True)
        repository = repo_root.resolve(strict=True)
        if not output.is_dir() or output == repository or output.is_relative_to(repository):
            raise ValueError("candidate output is unsafe")
        return output

    def read_bounded_regular_file(self, path: Path, *, max_bytes: int) -> bytes:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            data = os.read(descriptor, max_bytes + 1)
        finally:
            os.close(descriptor)
        if len(data) > max_bytes:
            raise ValueError("bounded input exceeded")
        return data

    def load_verified_issue_candidate(self, candidate_path: Path, repo_root: Path) -> _VerifiedIssueCandidate:
        raise AssertionError(f"unexpected Candidate load: {candidate_path} from {repo_root}")

    def load_expected_planning_targets(
        self,
        repo_root: Path,
        expected_head: str,
        canonical_target_paths: tuple[str, str, str],
    ) -> object:
        raise AssertionError(f"unexpected target load: {repo_root} {expected_head} {canonical_target_paths}")

    def planning_apply_resume_available(self, operation: object, *, output_dir: Path) -> bool:
        raise AssertionError(f"unexpected resume probe: {operation} in {output_dir}")

    def create_planning_apply_operation(self, **kwargs: object) -> SimpleNamespace:
        operation_id = hashlib.sha256(
            json.dumps(
                {
                    "issue_id": kwargs["issue_id"],
                    "mode": kwargs["mode"],
                    "reviewed_identity_sha256": kwargs["reviewed_identity_sha256"],
                    "human_decision_sha256": kwargs["human_decision_sha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        return SimpleNamespace(operation_id=operation_id, **kwargs)

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"unexpected Issue Planning gateway call: {name}")


PLANNING_DEPENDENCIES = IssuePlanningDependencies(clock=_FakeClock(), gateway=_FakeIssuePlanningGateway())


def _issue_tree(repo: Path) -> tuple[Path, _StoredMetaRecord]:
    issue_dir = repo / "spec-dock" / "initiatives" / "init-one" / "epics" / "epic-one" / "issues" / "iss-one"
    issue_dir.mkdir(parents=True)
    for name in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / name).write_bytes(f"old {name}\n".encode())
    return issue_dir, _StoredMetaRecord(
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


def _candidate_identity(**changes: object) -> IssueCandidateIdentity:
    values: dict[str, object] = {
        "issue_id": "iss-00003",
        "candidate_id": "cand-1",
        "version": 1,
        "logical_filename": "iss-00003-planning-candidate-v1.zip",
        "observed_transport_filename": "iss-00003-planning-candidate-v1.zip",
        "internal_root": "iss-00003-planning-candidate-v1",
        "source_repository": "owner/repo",
        "source_branch": "feature/issue",
        "source_head": HEAD,
        "zip_sha256": ZIP_SHA,
    }
    values.update(changes)
    return IssueCandidateIdentity(**values)  # type: ignore[arg-type]


def _identity(
    mode: str,
    *,
    target_paths: tuple[str, str, str] | None = None,
    candidate: IssueCandidateIdentity | None = None,
    source_head: str = HEAD,
) -> ReviewedPlanningIdentity:
    if mode == "archive-candidate":
        return ReviewedPlanningIdentity(
            mode="archive-candidate",
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=source_head,
            candidate_identity=candidate or _candidate_identity(source_head=source_head),
        )
    assert target_paths is not None
    candidate_identity = candidate or _candidate_identity(source_head=source_head)
    companion = OnboardingCompanionBindingV1(
        path=COMPANION_PATH,
        sha256=COMPANION_SHA,
    )
    return ReviewedPlanningIdentity(
        mode="git-bound",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head=source_head,
        canonical_target_paths=target_paths,
        git_bound_operation_binding=GitBoundOperationBindingV1.create(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=source_head,
            candidate_identity=candidate_identity,
            onboarding_companion=companion,
        ),
        expected_canonical_target_paths=target_paths,
    )


def _evidence_files(
    root: Path,
    identity: ReviewedPlanningIdentity,
    *,
    verdict: str = "pass",
    decision: str = "approved",
) -> tuple[Path, Path]:
    findings: tuple[PlanningReviewFinding, ...] = ()
    if verdict == "fail":
        findings = (
            PlanningReviewFinding(
                id="P1-1",
                severity="p1",
                exact_location="plan.md",
                violated_requirement_or_contradiction="missing proof",
                concrete_impact="unsafe apply",
            ),
        )
    review = PlanningReviewResult(
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        verdict=verdict,  # type: ignore[arg-type]
        findings=findings,
    )
    review_bytes = json.dumps(
        review.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    human = PlanningHumanDecisionV1(
        schema_version=1,
        issue_id="iss-00003",
        reviewed_identity=identity,
        reviewed_identity_sha256=identity.sha256,
        review_result_sha256=hashlib.sha256(review_bytes).hexdigest(),
        decision=decision,  # type: ignore[arg-type]
        plan_adoption=decision == "approved",
        implementation_start=decision == "approved",
        decided_at="2026-07-28T00:00:00Z",
    )
    human_bytes = json.dumps(
        human.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    review_path = root / "review.json"
    human_path = root / "human.json"
    review_path.write_bytes(review_bytes)
    human_path.write_bytes(human_bytes)
    return review_path, human_path


def _preflight(
    *,
    status: str = "pass",
    head: str = HEAD,
    source_hash: str = SOURCE_HASH,
    blockers: tuple[str, ...] | None = None,
):
    return SimpleNamespace(
        status=status,
        local_head=head,
        remote_head=head,
        blockers=blockers if blockers is not None else (() if status == "pass" else ("source_hash_mismatch",)),
        repository=SimpleNamespace(
            normalized_origin="https://github.com/owner/repo.git",
            branch="feature/issue",
            upstream="origin/feature/issue",
            source_manifest=SimpleNamespace(source_manifest_hash=source_hash),
        ),
        source_manifest=SimpleNamespace(source_manifest_hash=source_hash),
    )


def _verified_candidate(identity: IssueCandidateIdentity | None = None) -> _VerifiedIssueCandidate:
    return _VerifiedIssueCandidate(
        identity=identity or _candidate_identity(),
        files={
            "requirement.md": b"new requirement\n",
            "design.md": b"new design\n",
            "plan.md": b"new plan\n",
            COMPANION_PATH: COMPANION_BYTES,
        },
        source_baseline={
            "source_manifest_hash": SOURCE_HASH,
            "canonical_issue_paths": [],
            "relevant_paths": [],
        },
        zip_bytes=b"zip",
        onboarding_companion=OnboardingCompanionBindingV1(
            path=COMPANION_PATH,
            sha256=COMPANION_SHA,
        ),
    )


def _request(
    output: Path,
    review: Path,
    human: Path,
    *,
    mode: str = "archive-candidate",
    **changes: object,
) -> issue_planning.PlanningApplyRequest:
    values: dict[str, object] = {
        "issue_id": "iss-00003",
        "mode": mode,
        "review_result_path": review,
        "human_decision_path": human,
        "expected_head": HEAD,
        "output_dir": output,
        "candidate_path": output / "iss-00003-planning-candidate-v1.zip",
        "logical_filename": "iss-00003-planning-candidate-v1.zip" if mode == "archive-candidate" else None,
        "zip_sha256": ZIP_SHA if mode == "archive-candidate" else None,
        "reviewed_head": HEAD if mode == "git-bound" else None,
    }
    values.update(changes)
    return issue_planning.PlanningApplyRequest(**values)  # type: ignore[arg-type]


def _run(
    tmp_path: Path,
    *,
    mode: str = "archive-candidate",
    verdict: str = "pass",
    decision: str = "approved",
    request_changes: dict[str, object] | None = None,
    identity: ReviewedPlanningIdentity | None = None,
    candidate: _VerifiedIssueCandidate | None = None,
    candidate_after_preflight: _VerifiedIssueCandidate | None = None,
    candidate_error: IssuePlanningCandidateArchiveRejected | None = None,
    preflight: object | None = None,
    execution: tuple[str, str] = ("ready", "adoption_published"),
    dependencies: IssuePlanningDependencies | None = None,
    resume_probe: Callable[..., bool] | None = None,
    transaction_runner_override: Callable[..., _PlanningApplyExecution] | None = None,
):
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _issue_dir, record = _issue_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    target = issue_planning.resolve_existing_issue_target("iss-00003", [record], repo)
    default_candidate = _verified_candidate()
    reviewed = identity or _identity(
        mode,
        target_paths=target.canonical_issue_paths,
        candidate=default_candidate.identity,
    )
    review_path, human_path = _evidence_files(
        output,
        reviewed,
        verdict=verdict,
        decision=decision,
    )
    request = _request(
        output,
        review_path,
        human_path,
        mode=mode,
        **(request_changes or {}),
    )
    calls: list[object] = []
    current_candidate = [candidate or default_candidate]

    def transaction_runner(operation, **kwargs):
        calls.append(operation)
        if transaction_runner_override is not None:
            return transaction_runner_override(operation, **kwargs)
        return _PlanningApplyExecution(
            status=execution[0],
            reason=execution[1],
            operation_id=operation.operation_id,
        )

    def expected_target_loader(root, _expected_head, canonical_paths):
        documents = {PurePath(path).name: (root / path).read_bytes() for path in canonical_paths}
        return SimpleNamespace(
            documents=documents,
            blob_oids={
                path: hashlib.sha1(
                    b"blob "
                    + str(len(documents[PurePath(path).name])).encode("ascii")
                    + b"\0"
                    + documents[PurePath(path).name]
                ).hexdigest()
                for path in canonical_paths
            },
        )

    def run_preflight(_request):
        if candidate_after_preflight is not None:
            current_candidate[0] = candidate_after_preflight
        return preflight or _preflight()

    def load_candidate(_path: Path, _root: Path) -> _VerifiedIssueCandidate:
        if candidate_error is not None:
            raise candidate_error
        return current_candidate[0]

    result = issue_planning.run_issue_planning_apply(
        dependencies=dependencies or PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: SimpleNamespace(report=SimpleNamespace(errors=[])),
        sync_runner=lambda: SimpleNamespace(
            artifact_failure=None,
            state=SimpleNamespace(deps_preflight_error=None),
        ),
        preflight_runner=run_preflight,
        candidate_loader=load_candidate,
        expected_target_loader=expected_target_loader,
        resume_probe=resume_probe or (lambda _operation, **_kwargs: False),
        transaction_runner=transaction_runner,
    )
    return result, calls, request, record


def test_apply_propagates_validated_output_guard_by_identity(tmp_path: Path) -> None:
    opaque_guard = object()
    resume_guards: list[object] = []
    transaction_guards: list[object] = []

    class _OpaqueGuardGateway(_FakeIssuePlanningGateway):
        def validate_candidate_output_directory(self, output_dir: Path, repo_root: Path) -> Path:
            super().validate_candidate_output_directory(output_dir, repo_root)
            return opaque_guard  # type: ignore[return-value]

    def resume_probe(_operation: object, *, output_guard: object) -> bool:
        resume_guards.append(output_guard)
        return False

    def transaction_runner(operation: object, *, output_guard: object, **_kwargs: object) -> _PlanningApplyExecution:
        transaction_guards.append(output_guard)
        return _PlanningApplyExecution(
            status="ready",
            reason="adoption_published",
            operation_id=operation.operation_id,  # type: ignore[attr-defined]
        )

    result, calls, _, _ = _run(
        tmp_path,
        dependencies=IssuePlanningDependencies(
            clock=_FakeClock(),
            gateway=_OpaqueGuardGateway(),
        ),
        resume_probe=resume_probe,
        transaction_runner_override=transaction_runner,
    )

    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert len(calls) == 1
    assert len(resume_guards) == 1
    assert len(transaction_guards) == 1
    assert resume_guards[0] is opaque_guard
    assert transaction_guards[0] is opaque_guard
    assert resume_guards[0] is transaction_guards[0]


def test_archive_apply_preserves_candidate_archive_findings_in_result_details(
    tmp_path: Path,
) -> None:
    findings = ("unsafe_entry_symlink", "checksum_mismatch")
    result, calls, _, _ = _run(
        tmp_path,
        candidate_error=IssuePlanningCandidateArchiveRejected(findings),
    )

    assert (result.status, result.reason) == ("rejected", "archive_rejected")
    assert result.details == findings
    assert calls == []


def _assert_not_ready(result, expected: tuple[str, str]) -> None:
    assert (result.status, result.reason) == expected
    assert result.is_ready is False
    assert (result.status, result.reason) != ("ready", "adoption_published")


def test_pa_nf_01_archive_review_only_is_blocked(tmp_path: Path) -> None:
    result, _, request, record = _run(tmp_path)
    request.human_decision_path.unlink()
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("blocked", "human_decision_unavailable"))


def test_pa_nf_02_git_bound_review_only_is_blocked(tmp_path: Path) -> None:
    result, _, request, record = _run(tmp_path, mode="git-bound")
    request.human_decision_path.unlink()
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("blocked", "human_decision_unavailable"))


def test_pa_nf_03_human_decision_only_is_blocked(tmp_path: Path) -> None:
    _, _, request, record = _run(tmp_path)
    request.review_result_path.unlink()
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("blocked", "review_result_unavailable"))


def test_pa_nf_04_parity_only_is_blocked(tmp_path: Path) -> None:
    _, _, request, record = _run(tmp_path)
    request.review_result_path.unlink()
    request.human_decision_path.unlink()
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("blocked", "review_result_unavailable"))


@pytest.mark.parametrize(
    ("name", "changes"),
    [
        ("filename", {"logical_filename": "wrong.zip"}),
        ("sha", {"zip_sha256": "d" * 64}),
    ],
)
def test_pa_nf_05_wrong_candidate_identity_is_rejected(
    tmp_path: Path,
    name: str,
    changes: dict[str, object],
) -> None:
    result, calls, _, _ = _run(tmp_path, request_changes=changes)
    _assert_not_ready(result, ("rejected", "candidate_identity_rejected"))
    assert calls == [], name


@pytest.mark.parametrize("kind", ["head", "paths"])
def test_pa_nf_06_wrong_review_identity_is_rejected(tmp_path: Path, kind: str) -> None:
    repo = tmp_path / "seed"
    repo.mkdir()
    _issue_dir, record = _issue_tree(repo)
    paths = issue_planning.resolve_existing_issue_target("iss-00003", [record], repo).canonical_issue_paths
    changes: dict[str, object] = {}
    if kind == "head":
        identity = _identity("git-bound", target_paths=paths, source_head="d" * 40)
        changes["reviewed_head"] = "d" * 40
    else:
        wrong_paths = tuple(path.replace("/iss-one/", "/iss-other/") for path in paths)
        identity = ReviewedPlanningIdentity(
            mode="git-bound",
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head=HEAD,
            canonical_target_paths=wrong_paths,  # type: ignore[arg-type]
            git_bound_operation_binding=GitBoundOperationBindingV1.create(
                issue_id="iss-00003",
                repository="owner/repo",
                branch="feature/issue",
                source_head=HEAD,
                candidate_identity=_candidate_identity(),
                onboarding_companion=OnboardingCompanionBindingV1(
                    path=COMPANION_PATH,
                    sha256=COMPANION_SHA,
                ),
            ),
            expected_canonical_target_paths=wrong_paths,  # type: ignore[arg-type]
        )
    result, calls, _, _ = _run(
        tmp_path / "case",
        mode="git-bound",
        identity=identity,
        request_changes=changes,
    )
    _assert_not_ready(result, ("rejected", "review_result_rejected" if kind == "paths" else "review_identity_rejected"))
    assert calls == []


@pytest.mark.parametrize("kind", ["source", "candidate", "target"])
def test_pa_nf_07_apply_target_drift_is_stale(tmp_path: Path, kind: str) -> None:
    mode: str = "archive-candidate"
    preflight: object | None = None
    candidate: _VerifiedIssueCandidate | None = None
    if kind == "source":
        preflight = _preflight(head="d" * 40)
    elif kind == "candidate":
        candidate = _verified_candidate(_candidate_identity(zip_sha256="d" * 64))
    else:
        mode = "git-bound"
        preflight = _preflight(head="d" * 40)
    result, calls, _, _ = _run(
        tmp_path,
        mode=mode,
        preflight=preflight,
        candidate=candidate,
    )
    _assert_not_ready(result, ("stale", "apply_target_changed"))
    assert calls == []


def _assert_execution_outcome(
    tmp_path: Path,
    execution: tuple[str, str],
) -> None:
    result, calls, _, _ = _run(tmp_path, execution=execution)
    _assert_not_ready(result, execution)
    assert len(calls) == 1


def test_pa_nf_08_semantic_mutation_rolls_back(tmp_path: Path) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("rolled_back", "adoption_semantic_mutation"),
    )


def test_pa_nf_09_candidate_parity_failure_rolls_back(tmp_path: Path) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("rolled_back", "candidate_parity_failed"),
    )


def test_pa_nf_10a_validation_failure_rolls_back(tmp_path: Path) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("rolled_back", "specdock_validation_failed"),
    )


def test_pa_nf_10a_sync_failure_rolls_back(tmp_path: Path) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("rolled_back", "specdock_sync_failed"),
    )


def test_pa_nf_10b_push_failure_is_publication_pending(tmp_path: Path) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("publication_pending", "push_failed"),
    )


def test_pa_nf_10b_remote_parity_failure_is_publication_pending(
    tmp_path: Path,
) -> None:
    _assert_execution_outcome(
        tmp_path,
        ("publication_pending", "remote_parity_unconfirmed"),
    )


def test_approval_requires_review_pass(tmp_path: Path) -> None:
    result, calls, _, _ = _run(tmp_path, verdict="fail")
    _assert_not_ready(result, ("blocked", "review_not_passed"))
    assert calls == []


@pytest.mark.parametrize("mode", ["archive-candidate", "git-bound"])
def test_rejection_selects_decision_only_lane(tmp_path: Path, mode: str) -> None:
    result, calls, _, _ = _run(
        tmp_path,
        mode=mode,
        decision="rejected",
        execution=("rejected", "plan_rejected"),
    )
    _assert_not_ready(result, ("rejected", "plan_rejected"))
    assert len(calls) == 1
    assert calls[0].replacement_documents == {}


def test_ready_is_returned_only_from_terminal_transaction_result(tmp_path: Path) -> None:
    result, calls, _, _ = _run(tmp_path)
    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert result.is_ready is True
    assert len(calls) == 1


def test_archive_review_skip_requires_all_canonical_proofs(tmp_path: Path) -> None:
    result, calls, _, _ = _run(tmp_path)
    assert (result.status, result.reason) == ("ready", "adoption_published")
    assert len(calls) == 1


def test_archive_review_skip_rejects_source_manifest_drift(tmp_path: Path) -> None:
    result, calls, _, _ = _run(
        tmp_path,
        preflight=_preflight(
            status="stale",
            blockers=("source_hash_mismatch",),
        ),
    )
    _assert_not_ready(result, ("stale", "fresh_review_required"))
    assert calls == []


def test_archive_review_skip_rejects_candidate_external_diff(tmp_path: Path) -> None:
    result, calls, _, _ = _run(
        tmp_path,
        preflight=_preflight(
            status="blocked",
            blockers=("dirty_tracked",),
        ),
    )
    _assert_not_ready(result, ("stale", "fresh_review_required"))
    assert calls == []


def test_archive_review_skip_rejects_candidate_identity_drift(
    tmp_path: Path,
) -> None:
    result, calls, _, _ = _run(
        tmp_path,
        candidate=_verified_candidate(_candidate_identity(zip_sha256="d" * 64)),
    )
    _assert_not_ready(result, ("stale", "apply_target_changed"))
    assert calls == []


def test_git_bound_apply_rejects_candidate_swap_during_final_preflight(
    tmp_path: Path,
) -> None:
    replacement = _verified_candidate(
        _candidate_identity(
            candidate_id="cand-2",
            version=2,
            logical_filename="iss-00003-planning-candidate-v2.zip",
            observed_transport_filename="iss-00003-planning-candidate-v2.zip",
            internal_root="iss-00003-planning-candidate-v2",
            zip_sha256="d" * 64,
        )
    )

    result, calls, _, _ = _run(
        tmp_path,
        mode="git-bound",
        candidate_after_preflight=replacement,
    )

    _assert_not_ready(result, ("rejected", "operation_binding_mismatch"))
    assert calls == []


@pytest.mark.parametrize("kind", ["symlink", "inside_repo", "oversize", "invalid_utf8"])
def test_unsafe_review_input_is_rejected_before_transaction(
    tmp_path: Path,
    kind: str,
) -> None:
    _, _, request, record = _run(tmp_path)
    source = request.review_result_path
    if kind == "symlink":
        alias = source.with_name("review-link.json")
        alias.symlink_to(source)
        request = replace(request, review_result_path=alias)
    elif kind == "inside_repo":
        inside = tmp_path / "repo" / "review.json"
        inside.write_bytes(source.read_bytes())
        request = replace(request, review_result_path=inside)
    elif kind == "oversize":
        source.write_bytes(b"x" * (1024 * 1024 + 1))
    else:
        source.write_bytes(b"\xff")
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("rejected", "review_result_rejected"))


@pytest.mark.parametrize("kind", ["symlink", "inside_repo", "oversize", "invalid_utf8"])
def test_unsafe_human_input_is_rejected_before_transaction(
    tmp_path: Path,
    kind: str,
) -> None:
    _, _, request, record = _run(tmp_path)
    source = request.human_decision_path
    if kind == "symlink":
        alias = source.with_name("human-link.json")
        alias.symlink_to(source)
        request = replace(request, human_decision_path=alias)
    elif kind == "inside_repo":
        inside = tmp_path / "repo" / "human.json"
        inside.write_bytes(source.read_bytes())
        request = replace(request, human_decision_path=inside)
    elif kind == "oversize":
        source.write_bytes(b"x" * (1024 * 1024 + 1))
    else:
        source.write_bytes(b"\xff")
    result = issue_planning.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=request,
        records=[record],
        repo_root=tmp_path / "repo",
        repo_slug_resolver=lambda _root: "owner/repo",
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=lambda *_args, **_kwargs: pytest.fail("must not mutate"),
    )
    _assert_not_ready(result, ("rejected", "human_decision_rejected"))
