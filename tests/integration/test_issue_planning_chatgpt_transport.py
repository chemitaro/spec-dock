import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import cast
import zipfile

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application import issue_planning  # noqa: E402
from spec_dock_runtime.application.authoring_pack.github_sync_preflight import (  # noqa: E402
    run_github_sync_preflight,
)
from spec_dock_runtime.application.ports import IssuePlanningDependencies  # noqa: E402
from spec_dock_runtime.cli.bootstrap import _Clock, _IssuePlanningGateway  # noqa: E402
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    FetchSummary,
    FreshnessEvidence,
    GitProcessOutcome,
    PreflightResult,
    RepositorySnapshot,
)
from spec_dock_runtime.domain.authoring_pack.source_manifest import (  # noqa: E402
    build_source_manifest,
    empty_source_manifest,
)
from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    OracleAuthoringZipSnapshot,
    OracleReviewJsonPayload,
    PlanningInvocationResult,
    PlanningSourceEvidence,
)
from spec_dock_runtime.infra.contracts import DirectDependencyResolution, StoredMetaRecord  # noqa: E402
from spec_dock_runtime.infra.issue_planning_chatgpt import (  # noqa: E402
    resolve_issue_planning_github_repository,
)

DEFAULT_COMPANION_PATH = "artifacts/20260728t120000z-guide-new-member-chatgpt-first-issue-planning.md"
PLANNING_DEPENDENCIES = IssuePlanningDependencies(clock=_Clock(), gateway=_IssuePlanningGateway())


def test_synced_source_to_transport_tracer_preserves_identity_and_is_not_lifecycle_success(
    tmp_path: Path,
) -> None:
    issue_dir = tmp_path / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    for name in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / name).write_text(name, encoding="utf-8")
    record = StoredMetaRecord(
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
    invoked: list[object] = []

    def backend(**kwargs: object) -> PlanningInvocationResult:
        invoked.append(kwargs)
        return _transport_result(
            source_evidence=cast("PlanningSourceEvidence", kwargs["source_evidence"]),
        )

    run = issue_planning.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[record],
        repo_root=tmp_path,
        role="planner",
        dependency_loader=lambda issue_id: [
            DirectDependencyResolution(raw_ref="iss-00001", resolved_node_id="iss-00001")
        ],
        preflight_runner=lambda request: _preflight(
            source_manifest=build_source_manifest(tmp_path, request.source_paths)
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=backend,
        onboarding_companion_path=DEFAULT_COMPANION_PATH,
    )
    assert len(invoked) == 1
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.source_evidence.repository == "owner/repo"
    assert result.source_evidence.local_head == "a" * 40
    assert result.reason not in {
        "candidate_created",
        "candidate_revised",
        "review_completed",
        "adoption_published",
    }


def test_real_preflight_clean_synced_github_branch_invokes_backend_once(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "checkout", "-b", "feature/issue")
    issue_dir = tmp_path / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    for name in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / name).write_text(name, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture")
    head = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "remote", "add", "origin", "git@github.com:owner/repo.git")
    _git(tmp_path, "update-ref", "refs/remotes/origin/feature/issue", head)
    _git(tmp_path, "branch", "--set-upstream-to", "origin/feature/issue")
    record = StoredMetaRecord(
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
    backend_calls: list[object] = []

    def backend(**kwargs: object) -> PlanningInvocationResult:
        backend_calls.append(kwargs)
        return _transport_result(
            source_evidence=cast("PlanningSourceEvidence", kwargs["source_evidence"]),
        )

    result = issue_planning.run_issue_planning_transport(
        issue="iss-00003",
        records=[record],
        repo_root=tmp_path,
        role="planner",
        repo_slug_resolver=resolve_issue_planning_github_repository,
        backend_invoker=backend,
        preflight_runner=lambda request: run_github_sync_preflight(
            request,
            fetch_executor=lambda fetch_request: GitProcessOutcome(
                return_code=0,
                termination="exited",
                stdout=b"",
                stderr=b"",
                duration_ms=1,
            ),
        ),
        onboarding_companion_path=DEFAULT_COMPANION_PATH,
    )
    assert len(backend_calls) == 1
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert result.source_evidence.local_head == head
    assert result.source_evidence.remote_head == head


def test_fake_transport_to_candidate_preserves_source_and_payload_binding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    record = _record(issue_dir)
    payload = _authoring_zip(documents)
    result = issue_planning.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=payload),
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "candidate_created")
    candidate = output / result.output["candidate_identity"]["logical_filename"]
    with zipfile.ZipFile(candidate) as archive:
        root = result.output["candidate_identity"]["internal_root"]
        baseline = json.loads(archive.read(f"{root}/SOURCE-BASELINE.json"))
    assert baseline["source_repository"] == "owner/repo"
    assert baseline["source_head"] == "a" * 40
    assert baseline["planner_payload_sha256"] == hashlib.sha256(payload).hexdigest()
    assert baseline["planner_payload_size"] == len(payload)


def test_typed_authoring_zip_rejects_stale_source_before_candidate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    result = issue_planning.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=_authoring_zip(documents)),
        preflight_runner=lambda request: _preflight(source_manifest=build_source_manifest(repo, request.source_paths)),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("stale", "planning_source_stale")
    assert list(output.iterdir()) == []


def test_authoring_zip_extra_entry_leaves_final_zero(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    output = tmp_path / "output"
    output.mkdir()
    payload = _authoring_zip(
        documents,
        extra_entries={"fourth.md": b"fourth document"},
    )
    result = issue_planning.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=payload),
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("rejected", "archive_rejected")
    assert list(output.iterdir()) == []


def test_semantic_revise_to_fresh_review_chain(tmp_path: Path) -> None:
    _run_revision_to_fresh_review_chain(tmp_path, lane="semantic")


def test_mechanical_revise_to_fresh_review_chain(tmp_path: Path) -> None:
    _run_revision_to_fresh_review_chain(tmp_path, lane="mechanical")


def _run_revision_to_fresh_review_chain(tmp_path: Path, *, lane: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = repo / "spec-dock/initiatives/i/epics/e/issues/x"
    issue_dir.mkdir(parents=True)
    documents = {name: _planning_document(name) for name in ("requirement.md", "design.md", "plan.md")}
    for name, content in documents.items():
        (issue_dir / name).write_bytes(content)
    candidates = tmp_path / "candidates"
    revised = tmp_path / "revised"
    reviews = tmp_path / "reviews"
    candidates.mkdir()
    revised.mkdir()
    reviews.mkdir()
    record = _record(issue_dir)
    created = issue_planning.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningCreateRequest("iss-00003", candidates),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _transport_result(payload=_authoring_zip(documents)),
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    reviewer_identities: list[object] = []

    def review_transport(**kwargs):
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=issue_planning.resolve_existing_issue_target(
                "iss-00003",
                [record],
                repo,
            ).canonical_issue_paths,
            relevant_source_paths=(),
            operator_context=(),
        )
        synthesized = kwargs["prompt_synthesizer"](
            role="reviewer",
            context=context,
            repo_root=repo,
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )
        identity = contracts.ReviewedPlanningIdentity.from_json_bytes(
            next(item.content for item in synthesized.exact_attachments if item.name == "reviewed-identity.json")
        )
        reviewer_identities.append(identity)
        findings = (
            (
                contracts.PlanningReviewFinding(
                    id="F-1",
                    severity="p1",
                    exact_location="plan.md",
                    violated_requirement_or_contradiction="missing executable wording",
                    concrete_impact="implementation blocked",
                ),
            )
            if len(reviewer_identities) == 1
            else ()
        )
        result = contracts.PlanningReviewResult(
            reviewed_identity=identity,
            reviewed_identity_sha256=identity.sha256,
            verdict="fail" if findings else "pass",
            findings=findings,
        )
        payload = json.dumps(
            result.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        return _review_transport_result(payload=payload)

    first_identity = contracts.IssueCandidateIdentity.from_dict(created.output["candidate_identity"])
    first_review = issue_planning.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="archive-candidate",
            output_dir=reviews,
            candidate_path=candidates / first_identity.logical_filename,
        ),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=review_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T13:00:00+00:00",
    )
    assert first_review.output["verdict"] == "fail"
    review_path = reviews / first_review.output["review_result_file"]
    if lane == "semantic":
        request_value = {
            "schema_version": 1,
            "lane": "semantic",
            "candidate_identity": first_identity.to_dict(),
            "preserve_assumptions": ["scope"],
            "finding_ids": ["F-1"],
            "review_result_sha256": first_review.output["review_result_sha256"],
        }
    else:
        request_value = {
            "schema_version": 1,
            "lane": "mechanical",
            "candidate_identity": first_identity.to_dict(),
            "preserve_assumptions": ["scope"],
            "target_file": "plan.md",
            "old_text": "Substantive",
            "new_text": "Executable",
            "meaning_invariant": "same scope",
            "diff_budget": len(b"Substantive") + len(b"Executable"),
        }
    request_path = tmp_path / f"{lane}.json"
    request_path.write_text(
        json.dumps(request_value, separators=(",", ":")),
        encoding="utf-8",
    )

    def semantic_transport(**kwargs):
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=issue_planning.resolve_existing_issue_target(
                "iss-00003",
                [record],
                repo,
            ).canonical_issue_paths,
            relevant_source_paths=(),
            operator_context=(),
        )
        kwargs["prompt_synthesizer"](
            role="planner",
            context=context,
            repo_root=repo,
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )
        return _transport_result(
            payload=_authoring_zip(
                documents,
                companion_path=kwargs["onboarding_companion_path"],
            )
        )

    revision = issue_planning.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningReviseRequest(
            candidates / first_identity.logical_filename,
            request_path,
            revised,
        ),
        review_evidence=issue_planning.PlanningRevisionEvidenceInput(
            review_path,
            first_review.output["review_result_sha256"],
        ),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=semantic_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T14:00:00+00:00",
    )
    assert (revision.status, revision.reason) == ("ok", "candidate_revised")
    second_identity = contracts.IssueCandidateIdentity.from_dict(revision.output["candidate_identity"])
    second_review = issue_planning.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=issue_planning.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="archive-candidate",
            output_dir=reviews,
            candidate_path=revised / second_identity.logical_filename,
        ),
        records=[record],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=review_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T15:00:00+00:00",
    )
    assert second_review.output["verdict"] == "pass"
    assert len(reviewer_identities) == 2
    assert reviewer_identities[0] != reviewer_identities[1]
    assert first_identity.zip_sha256 != second_identity.zip_sha256


def _preflight(*, source_manifest=None) -> PreflightResult:
    manifest = source_manifest or empty_source_manifest()
    repository = RepositorySnapshot(
        normalized_origin="github.com/owner/repo",
        branch="feature/issue",
        local_head="a" * 40,
        upstream="origin/feature/issue",
        effective_ref="feature/issue",
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        worktree_state=(),
        source_manifest=manifest,
        snapshot_id="b" * 64,
    )
    return PreflightResult(
        status="pass",
        evidence_mode="github-synced",
        sync_state="synced",
        github_sync="verified",
        requested_ref="feature/issue",
        effective_ref="feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest=manifest,
        source_hash_mismatch_checked=False,
        fetch=FetchSummary(status="success"),
        freshness=FreshnessEvidence(
            snapshot_id="b" * 64,
            final_guard_snapshot_id="b" * 64,
            concurrent_change_check="stable",
            remote_head_disposition="fetched_remote_tracking_ref",
        ),
        repository=repository,
    )


def _transport_result(
    *,
    source_evidence: PlanningSourceEvidence | None = None,
    payload: bytes = b"body",
) -> PlanningInvocationResult:
    evidence = source_evidence or PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash=empty_source_manifest().source_manifest_hash,
        snapshot_id="b" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    authoring_zip = OracleAuthoringZipSnapshot(
        expected_logical_filename="iss-00003-issue-planning-documents.zip",
        observed_transport_filename="iss-00003-issue-planning-documents.zip",
        internal_root="iss-00003-issue-planning-documents",
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        zip_bytes=payload,
    )
    return PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=evidence,
        response_bytes=len(payload),
        response_sha256=authoring_zip.sha256,
        authoring_zip=authoring_zip,
    )


def _review_transport_result(payload: bytes) -> PlanningInvocationResult:
    review_json = OracleReviewJsonPayload(
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        json_bytes=payload,
    )
    return PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=_transport_result().source_evidence,
        response_bytes=len(payload),
        response_sha256=review_json.sha256,
        review_json=review_json,
    )


def _record(issue_dir: Path) -> StoredMetaRecord:
    return StoredMetaRecord(
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


def _planning_document(filename: str) -> bytes:
    kind = {
        "requirement.md": "要件定義書（Issue）",
        "design.md": "設計書（Issue）",
        "plan.md": "実装計画書（Issue）",
    }[filename]
    dependency = {
        "requirement.md": "",
        "design.md": '依存: ["requirement.md"]\n',
        "plan.md": '依存: ["requirement.md", "design.md"]\n',
    }[filename]
    return (
        "---\n"
        f"種別: {kind}\n"
        'ID: "iss-00003"\n'
        'タイトル: "Issue"\n'
        '状態: "approved"\n'
        '作成者: "Author"\n'
        '最終更新: "2026-07-27"\n'
        f"{dependency}"
        '親: ["epic-00002", "init-00001"]\n'
        "---\n\n"
        "# iss-00003 Issue\n\n"
        "## Section\n\n"
        "Substantive content.\n"
    ).encode()


def _authoring_zip(
    documents: dict[str, bytes],
    *,
    companion_path: str = DEFAULT_COMPANION_PATH,
    extra_entries: dict[str, bytes] | None = None,
) -> bytes:
    root = "iss-00003-issue-planning-documents"
    payloads = {
        **documents,
        companion_path: _onboarding_companion(),
        **(extra_entries or {}),
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for relative_path in sorted(payloads, key=lambda value: value.encode()):
            info = zipfile.ZipInfo(
                f"{root}/{relative_path}",
                date_time=(2026, 7, 28, 12, 0, 0),
            )
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, payloads[relative_path])
    return output.getvalue()


def _onboarding_companion() -> bytes:
    diagrams = "\n\n".join(
        f"```plantuml\n@startuml\ntitle {title}\nactor Human\ncomponent SpecDock\nHuman --> SpecDock\n@enduml\n```"
        for title in (
            "system context",
            "responsibility boundary",
            "planning sequence",
            "implementation roadmap",
        )
    )
    return (
        "# First-day onboarding guide\n\n"
        "This subordinate guide defers to requirement.md, design.md, and plan.md.\n\n"
        "## Initiative, Epic, and Issue lineage\n\n"
        "The planning target is init-00001, epic-00002, and iss-00003.\n\n"
        "## Purpose and scope\n\nPurpose and scope are bounded to onboarding.\n\n"
        "## System context\n\nThe system context identifies the actors.\n\n"
        "## Authority and responsibility boundary\n\n"
        "Authority and responsibility remain deterministic.\n\n"
        "## Current architecture and target architecture\n\n"
        "Current architecture and target architecture define the transition.\n\n"
        "## ChatGPT First planning lifecycle\n\n"
        "ChatGPT First governs the planning lifecycle.\n\n"
        "## Direct Oracle and reference-only chatgpt-use\n\n"
        "Oracle is direct and chatgpt-use is reference-only.\n\n"
        "## Candidate, Review, Human, and apply lifecycle\n\n"
        "Candidate creation, Review, Human decision, and apply are controlled.\n\n"
        "## Exact current branch gate\n\nThe exact current branch is required.\n\n"
        "## Implementation roadmap\n\nS01 through S07 are complete; S08 through S14 remain.\n\n"
        "## Provider authority and projection\n\nProvider authority precedes projection.\n\n"
        "## Failure modes\n\nFailure handling stops closed.\n\n"
        "## First-day checklist\n\nThe first-day checklist directs onboarding.\n\n"
        f"{diagrams}\n"
    ).encode()


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
