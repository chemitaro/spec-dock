from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast
import zipfile

import pytest

if TYPE_CHECKING:
    from spec_dock_runtime.application.issue_planning_prompt import (
        SynthesizedPlanningPrompt,
    )

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application.issue_planning import resolve_existing_issue_target  # noqa: E402
from spec_dock_runtime.application.ports import (  # noqa: E402
    IssuePlanningCandidateArchiveRejected,
    IssuePlanningCandidateCollision,
    IssuePlanningCandidatePublicationFailed,
    IssuePlanningDependencies,
)
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    FetchSummary,
    FreshnessEvidence,
    PreflightResult,
    RepositorySnapshot,
)
from spec_dock_runtime.domain.authoring_pack.source_manifest import (  # noqa: E402
    build_source_manifest,
    empty_source_manifest,
)
from spec_dock_runtime.domain.issue_planning_candidate import (  # noqa: E402
    CandidateMaterial,
    derive_candidate_identity,
)
from spec_dock_runtime.domain.issue_planning_contracts import (  # noqa: E402
    IssueCandidateIdentity,
    OnboardingCompanionBindingV1,
    OracleAuthoringZipSnapshot,
    PlanningPublicationSourceStale,
    ReviewedPlanningIdentity,
)


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
class _DirectDependencyResolution:
    raw_ref: str
    resolved_node_id: str


@dataclass(frozen=True)
class _VerifiedIssueCandidate:
    identity: IssueCandidateIdentity
    files: dict[str, bytes]
    source_baseline: dict[str, object]
    zip_bytes: bytes
    onboarding_companion: OnboardingCompanionBindingV1


def _review_identity_from_prompt(synthesized: object, contracts: object, *, expected_paths=None):
    prompt = synthesized.prompt
    identity_body = prompt.split("## Reviewed identity\n\n", 1)[1].split(
        "\n\n## Reviewed identity SHA-256", 1
    )[0]
    digest = prompt.split("## Reviewed identity SHA-256\n\n", 1)[1].split("\n\n", 1)[0]
    identity = contracts.ReviewedPlanningIdentity.from_dict(
        json.loads(identity_body),
        expected_canonical_target_paths=expected_paths,
    )
    assert digest == identity.sha256
    return identity, digest


@dataclass(frozen=True)
class _PublishedCandidate:
    identity: IssueCandidateIdentity
    zip_byte_count: int
    candidate_path: Path
    onboarding_companion: OnboardingCompanionBindingV1


@dataclass(frozen=True)
class _PublishedPlanningReview:
    review_result_file: str
    review_summary_file: str
    review_result_sha256: str


class _FakeClock:
    def now_iso(self) -> str:
        return "2026-07-28T12:00:00+00:00"

    def today(self) -> str:
        return "2026-07-28"


class _FakeIssuePlanningGateway:
    def __init__(self, *, publication_supported: bool = True) -> None:
        self._candidates: dict[Path, _VerifiedIssueCandidate] = {}
        self._descriptor_roots: dict[int, Path] = {}
        self._publication_supported = publication_supported

    def validate_candidate_output_directory(self, output_dir: Path, repo_root: Path) -> Path:
        output = output_dir.resolve(strict=True)
        repository = repo_root.resolve(strict=True)
        if not output.is_dir() or output == repository or output.is_relative_to(repository):
            raise ValueError("candidate output is unsafe")
        return output

    def load_validated_issue_authoring_payload(
        self,
        snapshot: object,
        *,
        expected_companion_path: str,
        repo_root: Path,
    ) -> SimpleNamespace:
        del repo_root
        authoring_snapshot = cast("OracleAuthoringZipSnapshot", snapshot)
        zip_bytes = authoring_snapshot.zip_bytes
        internal_root = authoring_snapshot.internal_root
        try:
            if len(zip_bytes) < 22 or zip_bytes[-22:-18] != b"PK\x05\x06":
                raise ValueError("authoring archive has trailing or missing data")
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
                expected_names = {
                    f"{internal_root}/{name}"
                    for name in (
                        "requirement.md",
                        "design.md",
                        "plan.md",
                        expected_companion_path,
                    )
                }
                if set(archive.namelist()) != expected_names:
                    raise ValueError("authoring archive inventory mismatch")
                documents = {
                    name: archive.read(f"{internal_root}/{name}") for name in ("requirement.md", "design.md", "plan.md")
                }
                companion = archive.read(f"{internal_root}/{expected_companion_path}")
        except (KeyError, ValueError, zipfile.BadZipFile) as error:
            raise IssuePlanningCandidateArchiveRejected(("authoring_archive_rejected",)) from error
        return SimpleNamespace(
            documents=documents,
            onboarding_companion_path=expected_companion_path,
            onboarding_companion_bytes=companion,
            zip_sha256=hashlib.sha256(zip_bytes).hexdigest(),
            zip_size_bytes=len(zip_bytes),
        )

    def build_and_publish_candidate(
        self,
        *,
        output_guard: Path,
        repo_root: Path,
        material: object,
        publication_guard: object,
    ) -> _PublishedCandidate:
        del repo_root, publication_guard
        candidate_material = cast("CandidateMaterial", material)
        if not self._publication_supported:
            raise IssuePlanningCandidatePublicationFailed("publication unsupported")
        final = output_guard / candidate_material.logical_filename
        if final.exists():
            raise IssuePlanningCandidateCollision(final.name)
        output = io.BytesIO()
        internal_root = candidate_material.internal_root
        files = dict(candidate_material.files)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for relative_path in sorted(files, key=lambda value: value.encode()):
                archive.writestr(f"{internal_root}/{relative_path}", files[relative_path])
        zip_bytes = output.getvalue()
        final.write_bytes(zip_bytes)
        identity = derive_candidate_identity(
            candidate_material,
            zip_bytes,
            observed_transport_filename=final.name,
        )
        companion = OnboardingCompanionBindingV1(
            path=candidate_material.onboarding_companion_path,
            sha256=hashlib.sha256(files[candidate_material.onboarding_companion_path]).hexdigest(),
        )
        source_baseline = json.loads(files["SOURCE-BASELINE.json"].decode("utf-8"))
        self._candidates[final.resolve()] = _VerifiedIssueCandidate(
            identity=identity,
            files=files,
            source_baseline=source_baseline,
            zip_bytes=zip_bytes,
            onboarding_companion=companion,
        )
        return _PublishedCandidate(identity, len(zip_bytes), final, companion)

    def load_verified_issue_candidate(self, candidate_path: Path, repo_root: Path) -> _VerifiedIssueCandidate:
        del repo_root
        path = candidate_path.resolve(strict=True)
        try:
            candidate = self._candidates[path]
        except KeyError as error:
            raise IssuePlanningCandidateArchiveRejected(("unregistered_candidate",)) from error
        current_bytes = path.read_bytes()
        if current_bytes == candidate.zip_bytes:
            return candidate
        return _VerifiedIssueCandidate(
            identity=candidate.identity,
            files=candidate.files,
            source_baseline=candidate.source_baseline,
            zip_bytes=current_bytes,
            onboarding_companion=candidate.onboarding_companion,
        )

    def open_safe_directory_descriptor(self, path: Path) -> int:
        descriptor = os.open(path, os.O_RDONLY)
        self._descriptor_roots[descriptor] = path
        return descriptor

    def read_bounded_regular_file_at(
        self,
        root_descriptor: int,
        relative_path: str,
        *,
        max_bytes: int,
    ) -> bytes:
        data = (self._descriptor_roots[root_descriptor] / relative_path).read_bytes()
        if len(data) > max_bytes:
            raise ValueError("bounded input exceeded")
        return data

    def read_bounded_regular_file(self, path: Path, *, max_bytes: int) -> bytes:
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path.anchor, directory_flags)
        try:
            for part in path.parent.parts[1:]:
                next_descriptor = os.open(part, directory_flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = next_descriptor
            file_descriptor = os.open(
                path.name,
                os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=descriptor,
            )
            try:
                if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
                    raise ValueError("bounded input must be a regular file")
                return self._read_descriptor(file_descriptor, max_bytes=max_bytes)
            finally:
                os.close(file_descriptor)
        except OSError as error:
            raise ValueError("bounded input is unsafe") from error
        finally:
            os.close(descriptor)

    @staticmethod
    def _read_descriptor(descriptor: int, *, max_bytes: int) -> bytes:
        chunks: list[bytes] = []
        size = 0
        while True:
            chunk = os.read(descriptor, min(64 * 1024, max_bytes + 1 - size))
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            size += len(chunk)
            if size > max_bytes:
                raise ValueError("bounded input exceeded")

    def read_external_review_result(
        self,
        path: Path,
        *,
        repo_root: Path,
        expected_sha256: str,
    ) -> bytes:
        del repo_root
        data = self.read_bounded_regular_file(path, max_bytes=1024 * 1024)
        if hashlib.sha256(data).hexdigest() != expected_sha256:
            raise ValueError("review digest mismatch")
        return data

    def publish_planning_review_evidence(
        self,
        *,
        output_dir: Path,
        repo_root: Path,
        reviewed_identity_sha256: str,
        review_result_bytes: bytes,
        summary_bytes: bytes,
        operation_time: datetime,
        publication_guard: object,
    ) -> _PublishedPlanningReview:
        del repo_root, publication_guard
        timestamp = operation_time.astimezone(timezone.utc).strftime("%Y%m%dt%H%M%Sz")
        result_name = f"{timestamp}-planning-review-result.json"
        summary_name = f"{timestamp}-planning-review-summary.md"
        result_path = output_dir / result_name
        summary_path = output_dir / summary_name
        if result_path.exists() or summary_path.exists():
            raise FileExistsError(result_name)
        result_path.write_bytes(review_result_bytes)
        summary_path.write_bytes(summary_bytes)
        return _PublishedPlanningReview(
            review_result_file=result_name,
            review_summary_file=summary_name,
            review_result_sha256=hashlib.sha256(review_result_bytes).hexdigest(),
        )

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"unexpected Issue Planning gateway call: {name}")


PLANNING_DEPENDENCIES = IssuePlanningDependencies(clock=_FakeClock(), gateway=_FakeIssuePlanningGateway())


def test_application_issue_planning_unit_tests_use_application_owned_test_doubles_only() -> None:
    forbidden = (
        "spec_dock_runtime.cli." + "bootstrap",
        "spec_dock_runtime." + "infra.",
    )
    for path in (
        Path(__file__),
        Path(__file__).with_name("test_issue_planning_apply.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert all(token not in source for token in forbidden), path


def _record(path: Path, *, node_id: str = "iss-00003", kind: str = "issue") -> _StoredMetaRecord:
    return _StoredMetaRecord(
        kind=kind,
        id=node_id,
        title="Issue",
        slug="issue",
        path=path.as_posix(),
        parent_id="epic-00002",
        initiative_id="init-00001",
        epic_id="epic-00002",
        github_issue_number=3,
        meta_path=(path / ".meta.json").as_posix(),
    )


def _issue_tree(repo_root: Path) -> Path:
    issue_dir = repo_root / "spec-dock" / "initiatives" / "init-one" / "epics" / "epic-one" / "issues" / "iss-one"
    issue_dir.mkdir(parents=True)
    for filename in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / filename).write_text(filename, encoding="utf-8")
    return issue_dir


def _planning_document(filename: str, *, issue_id: str = "iss-00003") -> bytes:
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
        f'ID: "{issue_id}"\n'
        'タイトル: "Issue"\n'
        '状態: "approved"\n'
        '作成者: "Author"\n'
        '最終更新: "2026-07-27"\n'
        f"{dependency}"
        '親: ["epic-00002", "init-00001"]\n'
        "---\n\n"
        f"# {issue_id} Issue\n\n"
        "## Section\n\n"
        "Substantive content.\n"
    ).encode()


def _planning_tree(repo_root: Path) -> Path:
    issue_dir = _issue_tree(repo_root)
    for filename in ("requirement.md", "design.md", "plan.md"):
        (issue_dir / filename).write_bytes(_planning_document(filename))
    return issue_dir


DEFAULT_COMPANION_PATH = "artifacts/20260728t120000z-guide-new-member-chatgpt-first-issue-planning.md"


def _onboarding_companion() -> bytes:
    diagrams = (
        "system context",
        "responsibility boundary",
        "planning sequence",
        "implementation roadmap",
    )
    blocks = "\n\n".join(
        f"```plantuml\n@startuml\ntitle {title}\nactor Human\ncomponent SpecDock\nHuman --> SpecDock\n@enduml\n```"
        for title in diagrams
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
        f"{blocks}\n"
    ).encode()


def _planner_payload(
    *,
    companion_path: str = DEFAULT_COMPANION_PATH,
    documents: dict[str, bytes] | None = None,
    companion: bytes | None = None,
) -> bytes:
    root = "issue-planning-authoring"
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        payloads = {
            filename: (documents or {}).get(filename, _planning_document(filename))
            for filename in ("requirement.md", "design.md", "plan.md")
        }
        payloads[companion_path] = companion if companion is not None else _onboarding_companion()
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


def _successful_transport(
    payload: bytes | None = None,
    *,
    source_manifest_hash: str | None = None,
    companion_path: str = DEFAULT_COMPANION_PATH,
):
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult", "PlanningSourceEvidence"],
    )
    value = payload or _planner_payload(companion_path=companion_path)
    evidence = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash=(source_manifest_hash or empty_source_manifest().source_manifest_hash),
        snapshot_id="b" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    authoring = contracts.OracleAuthoringZipSnapshot(
        expected_logical_filename="issue-planning-authoring.zip",
        observed_transport_filename="issue-planning-authoring.zip",
        internal_root="issue-planning-authoring",
        size_bytes=len(value),
        sha256=hashlib.sha256(value).hexdigest(),
        zip_bytes=value,
    )
    return contracts.PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=evidence,
        response_bytes=len(value),
        response_sha256=hashlib.sha256(value).hexdigest(),
        authoring_zip=authoring,
    )


def _successful_review_transport(payload: bytes, *, source_manifest_hash: str = "b" * 64):
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["OracleReviewJsonPayload", "PlanningInvocationResult", "PlanningSourceEvidence"],
    )
    evidence = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash=source_manifest_hash,
        snapshot_id="c" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    review = contracts.OracleReviewJsonPayload(
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        json_bytes=payload,
    )
    return contracts.PlanningInvocationResult(
        status="pass",
        reason="transport_received",
        source_evidence=evidence,
        response_bytes=len(payload),
        response_sha256=review.sha256,
        review_json=review,
    )


def test_resolve_existing_issue_returns_parents_and_exact_three_paths(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    result = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    assert result.issue_id == "iss-00003"
    assert result.parent_epic_id == "epic-00002"
    assert result.parent_initiative_id == "init-00001"
    assert tuple(Path(path).name for path in result.canonical_issue_paths) == (
        "design.md",
        "plan.md",
        "requirement.md",
    )


def test_git_bound_identity_accepts_exact_resolver_tuple(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=[
            "GitBoundOperationBindingV1",
            "IssueCandidateIdentity",
            "OnboardingCompanionBindingV1",
        ],
    )
    candidate = contracts.IssueCandidateIdentity(
        issue_id=target.issue_id,
        candidate_id="iss-00003-v1",
        version=1,
        logical_filename="candidate.zip",
        observed_transport_filename="candidate.zip",
        internal_root="candidate",
        source_repository="owner/repo",
        source_branch="feature/issue",
        source_head="a" * 40,
        zip_sha256="b" * 64,
    )
    binding = contracts.GitBoundOperationBindingV1.create(
        issue_id=target.issue_id,
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        candidate_identity=candidate,
        onboarding_companion=contracts.OnboardingCompanionBindingV1(
            path=DEFAULT_COMPANION_PATH,
            sha256="c" * 64,
        ),
    )
    identity = ReviewedPlanningIdentity(
        mode="git-bound",
        issue_id=target.issue_id,
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        canonical_target_paths=target.canonical_issue_paths,
        git_bound_operation_binding=binding,
        expected_canonical_target_paths=target.canonical_issue_paths,
    )
    identity.validate_canonical_target_paths(target.canonical_issue_paths)


@pytest.mark.parametrize("target", ["iss-99999", "init-00001", "epic-00002", "build payment flow"])
def test_resolve_existing_issue_rejects_unknown_parent_and_seed_targets(tmp_path: Path, target: str) -> None:
    issue_dir = _issue_tree(tmp_path)
    records = [
        _record(issue_dir),
        _record(issue_dir.parent.parent.parent, node_id="epic-00002", kind="epic"),
        _record(issue_dir.parent.parent.parent.parent.parent, node_id="init-00001", kind="initiative"),
    ]
    with pytest.raises(ValueError, match="existing Issue"):
        resolve_existing_issue_target(target, records, tmp_path)


def test_resolve_existing_issue_rejects_non_issue_record_with_issue_shaped_id(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    with pytest.raises(ValueError, match="existing Issue required"):
        resolve_existing_issue_target(
            "iss-00003",
            [_record(issue_dir, kind="epic")],
            tmp_path,
        )


def test_resolve_existing_issue_rejects_outside_and_dotdot_paths(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    for filename in ("requirement.md", "design.md", "plan.md"):
        (outside / filename).write_text(filename, encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        resolve_existing_issue_target("iss-00003", [_record(outside)], tmp_path)

    _issue_tree(tmp_path)
    dotdot_path = Path("spec-dock/initiatives/init-one/../init-one/epics/epic-one/issues/iss-one")
    with pytest.raises(ValueError, match=r"safe|dot|canonical"):
        resolve_existing_issue_target("iss-00003", [_record(dotdot_path)], tmp_path)


def test_resolve_existing_issue_rejects_symlinked_issue_or_document(tmp_path: Path) -> None:
    real_issue = _issue_tree(tmp_path)
    linked_issue = real_issue.parent / "iss-linked"
    linked_issue.symlink_to(real_issue, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        resolve_existing_issue_target("iss-00003", [_record(linked_issue)], tmp_path)

    (real_issue / "plan.md").unlink()
    (real_issue / "plan.md").symlink_to(real_issue / "design.md")
    with pytest.raises(ValueError, match="incomplete"):
        resolve_existing_issue_target("iss-00003", [_record(real_issue)], tmp_path)


def test_resolve_existing_issue_rejects_missing_canonical_document(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    (issue_dir / "plan.md").unlink()
    with pytest.raises(ValueError, match="incomplete"):
        resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)


@pytest.mark.parametrize(
    "blockers",
    [
        ("dirty_tracked",),
        ("staged_changes",),
        ("untracked_files",),
        ("detached_head",),
        ("remote_branch_missing",),
        ("origin_fetch_failed",),
        ("ahead_of_remote",),
        ("behind_remote",),
        ("diverged_from_remote",),
        ("concurrent_repo_change",),
    ],
)
def test_transport_short_circuits_backend_for_git_preflight_failures(
    tmp_path: Path,
    blockers: tuple[str, ...],
) -> None:
    issue_dir = _issue_tree(tmp_path)
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(blockers=blockers),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: (backend_calls.append(kwargs) or _successful_transport()),
    )
    assert (result.status, result.reason) == ("blocked", "git_preflight_blocked")
    assert result.details == blockers
    assert backend_calls == []


def test_transport_rejects_wrong_upstream_branch_before_backend(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(upstream="origin/other"),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: (backend_calls.append(kwargs) or _successful_transport()),
    )
    assert (result.status, result.reason) == ("blocked", "upstream_branch_mismatch")
    assert backend_calls == []


def test_transport_rejects_non_github_origin_without_leaking_error(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    run = module.run_issue_planning_transport
    private_url = "/Users/alice/private/repository"

    def reject_slug(root: Path) -> str:
        raise RuntimeError(f"origin is not GitHub: {private_url}")

    result = run(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(),
        repo_slug_resolver=reject_slug,
        prompt_synthesizer=lambda **kwargs: object(),
        backend_invoker=lambda **kwargs: pytest.fail("backend must not run"),
    )
    assert (result.status, result.reason) == ("blocked", "github_upstream_required")
    assert private_url not in repr(result)
    assert private_url not in str(result.to_dict())


def test_preflight_failure_redacts_unsafe_blocker_path_and_secret(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    private_value = "/Users/alice/private/token=abc123secret"
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(
            blockers=(f"unsafe_source_path:absolute-outside-repo:{private_value}",)
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("backend must not run"),
    )
    assert result.details == ("unsafe_source_path",)
    assert private_value not in repr(result)
    assert private_value not in str(result.to_dict())


def test_transport_rejects_source_mutation_after_preflight_before_backend(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    source_paths = tuple(
        sorted(
            (
                (issue_dir / "design.md").relative_to(tmp_path).as_posix(),
                (issue_dir / "plan.md").relative_to(tmp_path).as_posix(),
                (issue_dir / "requirement.md").relative_to(tmp_path).as_posix(),
            ),
            key=lambda value: value.encode("utf-8"),
        )
    )
    manifest = build_source_manifest(tmp_path, source_paths)
    backend_calls: list[object] = []

    def mutate_then_synthesize(**kwargs):
        (issue_dir / "plan.md").write_text("mutated after preflight", encoding="utf-8")
        from spec_dock_runtime.application.issue_planning_prompt import (
            synthesize_issue_planning_prompt,
        )

        return synthesize_issue_planning_prompt(**kwargs)

    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
        repo_slug_resolver=lambda root: "owner/repo",
        prompt_synthesizer=mutate_then_synthesize,
        backend_invoker=lambda **kwargs: (backend_calls.append(kwargs) or _successful_transport()),
        onboarding_companion_path=("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"),
    )
    assert (result.status, result.reason) == ("pass", "transport_received")
    assert len(backend_calls) == 1


def test_transport_sensitive_git_identity_rejection_does_not_leak_source_evidence(
    tmp_path: Path,
) -> None:
    issue_dir = _issue_tree(tmp_path)
    secret_branch = "token=abc123secret"
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(
            branch=secret_branch,
            upstream=f"origin/{secret_branch}",
        ),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: (backend_calls.append(kwargs) or _successful_transport()),
        onboarding_companion_path=("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"),
    )
    assert (result.status, result.reason) == ("rejected", "sensitive_input_rejected")
    assert result.source_evidence is None
    assert result.details == ()
    assert backend_calls == []
    assert secret_branch not in repr(result)
    assert secret_branch not in str(result.to_dict())


def test_transport_with_transcript_marker_mentions_reaches_backend_once(tmp_path: Path) -> None:
    issue_dir = _issue_tree(tmp_path)
    marker_content = {
        "design.md": "# Raw transcript vocabulary\n\nThe term raw transcript names an evidence class.\n",
        "plan.md": "- ChatGPT transcript、credential、private absolute pathを保存しない。\n",
        "requirement.md": "The runtime must not persist a browser transcript.\n",
    }
    for filename, content in marker_content.items():
        (issue_dir / filename).write_text(content, encoding="utf-8")
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    manifest = build_source_manifest(tmp_path, target.canonical_issue_paths)
    backend_result = _successful_transport()
    backend_calls: list[dict[str, Any]] = []

    def backend(**kwargs):
        backend_calls.append(kwargs)
        return backend_result

    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )
    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=backend,
        onboarding_companion_path=("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"),
    )

    assert result is backend_result
    assert result.reason != "sensitive_input_rejected"
    assert len(backend_calls) == 1
    synthesized = backend_calls[0]["synthesized"]
    assert synthesized.attachment_paths[1:] == tuple(tmp_path / path for path in target.canonical_issue_paths)


def test_transport_with_structured_transcript_stops_before_backend_without_leakage(
    tmp_path: Path,
) -> None:
    issue_dir = _issue_tree(tmp_path)
    transcript = "# Oracle Browser Transcript\n## Prompt\nprivate requirement body\n## Answer\nprivate response body\n"
    (issue_dir / "requirement.md").write_text(transcript, encoding="utf-8")
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], tmp_path)
    manifest = build_source_manifest(tmp_path, target.canonical_issue_paths)
    backend_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_transport"],
    )

    result = module.run_issue_planning_transport(
        issue="iss-00003",
        records=[_record(issue_dir)],
        repo_root=tmp_path,
        role="planner",
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: (backend_calls.append(kwargs) or _successful_transport()),
        onboarding_companion_path=("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"),
    )

    assert (result.status, result.reason) == ("pass", "transport_received")
    assert len(backend_calls) == 1
    synthesized = backend_calls[0]["synthesized"]
    assert synthesized.attachment_paths[1:] == tuple(tmp_path / path for path in target.canonical_issue_paths)
    assert "private requirement body" not in synthesized.prompt
    assert "private response body" not in str(result.to_dict())


def test_current_front_matter_inconsistency_short_circuits_backend(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    (issue_dir / "plan.md").write_bytes(_planning_document("plan.md", issue_id="iss-99999"))
    output = tmp_path / "output"
    output.mkdir()
    backend_calls: list[object] = []
    result = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    ).run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=__import__(
            "spec_dock_runtime.application.issue_planning",
            fromlist=["PlanningCreateRequest"],
        ).PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("rejected", "planning_context_rejected")
    assert backend_calls == []


def test_context_manifest_is_bounded_and_loaded_outside_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = tmp_path / "context.json"
    manifest.write_text(
        '{"relevant_source_paths":["src/example.py"],"operator_context":["preserve approved scope"]}\n',
        encoding="utf-8",
    )
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_load_planning_context_manifest"],
    )

    assert module._load_planning_context_manifest(
        manifest,
        repo_root=repo,
        gateway=PLANNING_DEPENDENCIES.gateway,
    ) == (("src/example.py",), ("preserve approved scope",))


def test_context_manifest_rejects_unknown_keys_without_backend_work(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest = tmp_path / "context.json"
    manifest.write_text(
        '{"relevant_source_paths":[],"operator_context":[],"unexpected":true}\n',
        encoding="utf-8",
    )
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_load_planning_context_manifest"],
    )

    with pytest.raises(ValueError, match="schema"):
        module._load_planning_context_manifest(
            manifest,
            repo_root=repo,
            gateway=PLANNING_DEPENDENCIES.gateway,
        )


def test_create_rejects_deeply_nested_context_manifest_without_backend_work(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    manifest = tmp_path / "context.json"
    nested = "[" * 10000 + "0" + "]" * 10000
    manifest.write_text(
        '{"relevant_source_paths":' + nested + ',"operator_context":[]}',
        encoding="utf-8",
    )
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["PlanningCreateRequest", "run_issue_planning_create"],
    )
    backend_calls: list[object] = []
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output, manifest),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
    )

    assert (result.status, result.reason) == ("rejected", "planning_context_rejected")
    assert backend_calls == []


def test_invalid_issue_id_rejections_keep_structured_result_contract(tmp_path: Path) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=[
            "PlanningApplyRequest",
            "PlanningCreateRequest",
            "PlanningReviewRequest",
            "run_issue_planning_apply",
            "run_issue_planning_create",
            "run_issue_planning_review",
        ],
    )

    def no_backend(**kwargs):
        pytest.fail("invalid Issue ID must short-circuit before backend work")

    create = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("nope", tmp_path),
        records=[],
        repo_root=tmp_path,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=no_backend,
    )
    review = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            "nope",
            "git-bound",
            tmp_path,
            candidate_path=tmp_path / "candidate.zip",
            reviewed_head="a" * 40,
        ),
        records=[],
        repo_root=tmp_path,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=no_backend,
    )
    apply = module.run_issue_planning_apply(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningApplyRequest(
            issue_id="nope",
            mode="git-bound",
            review_result_path=tmp_path / "review.json",
            human_decision_path=tmp_path / "decision.json",
            expected_head="a" * 40,
            output_dir=tmp_path,
            candidate_path=tmp_path / "candidate.zip",
            reviewed_head="a" * 40,
        ),
        records=[],
        repo_root=tmp_path,
        repo_slug_resolver=lambda _root: "owner/repo",
        candidate_loader=lambda *_args: pytest.fail("invalid Issue ID must short-circuit before candidate work"),
        expected_target_loader=lambda *_args: pytest.fail("invalid Issue ID must short-circuit before target work"),
        resume_probe=lambda *_args, **_kwargs: pytest.fail("invalid Issue ID must short-circuit before resume work"),
        validation_runner=lambda: None,
        sync_runner=lambda: None,
        transaction_runner=no_backend,
    )

    assert [(result.status, result.reason, result.issue_id) for result in (create, review, apply)] == [
        ("rejected", "planning_context_rejected", "iss-00000"),
        ("rejected", "review_request_rejected", "iss-00000"),
        ("rejected", "apply_request_rejected", "iss-00000"),
    ]
    assert all(result.to_dict()["issue_id"] == "iss-00000" for result in (create, review, apply))


def test_create_maps_s02_nonpass_without_candidate_work(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult"],
    )
    publisher_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: contracts.PlanningInvocationResult(
            status="blocked",
            reason="backend_timeout",
        ),
        publisher=lambda **kwargs: publisher_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("blocked", "backend_timeout")
    assert publisher_calls == []


def test_create_forwards_context_manifest_values_to_transport(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    manifest = tmp_path / "context.json"
    manifest.write_text(
        '{"relevant_source_paths":["src/example.py"],"operator_context":["preserve approved scope"]}\n',
        encoding="utf-8",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningInvocationResult"],
    )
    captured: dict[str, object] = {}
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )

    def transport(**kwargs):
        captured.update(kwargs)
        return contracts.PlanningInvocationResult(status="blocked", reason="backend_timeout")

    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output, manifest),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=transport,
    )

    assert (result.status, result.reason) == ("blocked", "backend_timeout")
    assert captured["relevant_source_paths"] == ("src/example.py",)
    assert captured["operator_context"] == ("preserve approved scope",)


def test_create_rejects_post_oracle_source_drift_before_publication(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
    manifest = build_source_manifest(repo, target.canonical_issue_paths)
    preflights = iter((
        _preflight(source_manifest=manifest),
        _preflight(
            branch="feature/other",
            upstream="origin/feature/other",
            source_manifest=manifest,
        ),
    ))
    publisher_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )

    def backend(**kwargs):
        assert kwargs["synthesized"].role == "planner"
        return _successful_transport(
            source_manifest_hash=manifest.source_manifest_hash,
        )

    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=backend,
        preflight_runner=lambda _request: next(preflights),
        publisher=lambda **kwargs: publisher_calls.append(kwargs),
        clock=lambda: "2026-07-29T04:46:00+00:00",
    )

    assert (result.status, result.reason) == ("stale", "planning_source_stale")
    assert publisher_calls == []
    assert list(output.iterdir()) == []


def test_create_publication_guard_maps_source_drift_to_stale(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
    before = build_source_manifest(repo, target.canonical_issue_paths)
    changed = issue_dir / "plan.md"
    changed.write_bytes(changed.read_bytes() + b"changed\n")
    after = build_source_manifest(repo, target.canonical_issue_paths)
    preflights = iter((_preflight(source_manifest=before), _preflight(source_manifest=after)))
    publisher_calls: list[object] = []
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )

    def publisher(**kwargs):
        publisher_calls.append(kwargs)
        assert kwargs["publication_guard"]() is False
        raise PlanningPublicationSourceStale("source changed")

    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(
            source_manifest_hash=before.source_manifest_hash,
        ),
        preflight_runner=lambda _request: next(preflights),
        publisher=publisher,
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )

    assert (result.status, result.reason) == ("stale", "planning_source_stale")
    assert len(publisher_calls) == 1
    assert list(output.iterdir()) == []


def test_onboarding_companion_path_uses_one_utc_operation_instant() -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_resolve_onboarding_companion_path"],
    )
    assert module._resolve_onboarding_companion_path(
        datetime(
            2026,
            7,
            29,
            13,
            46,
            tzinfo=timezone(offset=timedelta(hours=9)),
        )
    ) == ("artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md")


def test_create_rejects_transient_payload_digest_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    transport = _successful_transport()
    object.__setattr__(transport, "response_sha256", "d" * 64)
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: transport,
    )
    assert (result.status, result.reason) == ("rejected", "planner_response_rejected")
    assert list(output.iterdir()) == []


def test_create_returns_ok_candidate_created_only_after_atomic_publication(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc).isoformat(),
    )
    assert (result.status, result.reason) == ("ok", "candidate_created")
    identity = result.output["candidate_identity"]
    final = output / identity["logical_filename"]
    assert final.is_file()
    assert hashlib.sha256(final.read_bytes()).hexdigest() == identity["zip_sha256"]


def test_create_success_output_has_only_safe_keys(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert set(result.output) == {
        "candidate_identity",
        "candidate_path",
        "git_bound_operation_binding_sha256",
        "zip_byte_count",
    }
    assert result.output["candidate_path"] == str(output / result.output["candidate_identity"]["logical_filename"])
    assert _onboarding_companion().decode() not in str(result.to_dict())


def test_unsupported_atomic_publication_leaves_final_absent(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    dependencies = IssuePlanningDependencies(
        clock=_FakeClock(),
        gateway=_FakeIssuePlanningGateway(publication_supported=False),
    )
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=dependencies,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    assert (result.status, result.reason) == ("blocked", "candidate_publication_failed")
    assert list(output.iterdir()) == []


def test_atomic_publication_collision_preserves_existing_candidate_bytes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    arguments = {
        "request": module.PlanningCreateRequest("iss-00003", output),
        "records": [_record(issue_dir)],
        "repo_root": repo,
        "repo_slug_resolver": lambda root: "owner/repo",
        "backend_invoker": lambda **kwargs: None,
        "transport_runner": lambda **kwargs: _successful_transport(),
        "preflight_runner": lambda _request: _preflight(),
        "clock": lambda: "2026-07-28T12:00:00+00:00",
    }
    first = module.run_issue_planning_create(dependencies=PLANNING_DEPENDENCIES, **arguments)
    candidate = output / first.output["candidate_identity"]["logical_filename"]
    before = candidate.read_bytes()
    second = module.run_issue_planning_create(dependencies=PLANNING_DEPENDENCIES, **arguments)
    assert (second.status, second.reason) == ("rejected", "output_collision")
    assert candidate.read_bytes() == before
    assert len(list(output.iterdir())) == 1


def test_create_uses_one_dependency_snapshot_for_transport_and_source_baseline(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "output"
    output.mkdir()
    loader_calls: list[str] = []
    transport_dependencies: list[str] = []

    def changing_loader(issue_id: str) -> list[_DirectDependencyResolution]:
        loader_calls.append(issue_id)
        resolved = "iss-00001" if len(loader_calls) == 1 else "iss-00002"
        return [_DirectDependencyResolution(raw_ref=resolved, resolved_node_id=resolved)]

    def transport_runner(**kwargs):
        dependencies = kwargs["dependency_loader"]("iss-00003")
        transport_dependencies.extend(item.resolved_node_id for item in dependencies)
        return _successful_transport()

    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_create"],
    )
    result = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        dependency_loader=changing_loader,
        transport_runner=transport_runner,
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    candidate = output / result.output["candidate_identity"]["logical_filename"]
    internal_root = result.output["candidate_identity"]["internal_root"]
    with zipfile.ZipFile(candidate) as archive:
        baseline = json.loads(archive.read(f"{internal_root}/SOURCE-BASELINE.json"))
    assert loader_calls == ["iss-00003"]
    assert baseline["dependency_ids"] == transport_dependencies == ["iss-00001"]


def test_archive_review_accepts_exact_identity_and_publishes_external_evidence(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidate_output = tmp_path / "candidates"
    review_output = tmp_path / "reviews"
    candidate_output.mkdir()
    review_output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_review"],
    )
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidate_output),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    candidate = candidate_output / created.output["candidate_identity"]["logical_filename"]
    calls: list[SynthesizedPlanningPrompt] = []
    mutate_candidate = [False]

    def review_transport(**kwargs):
        contracts = __import__(
            "spec_dock_runtime.domain.issue_planning_contracts",
            fromlist=["PlanningContext"],
        )
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=resolve_existing_issue_target(
                "iss-00003",
                [_record(issue_dir)],
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
        calls.append(synthesized)
        if mutate_candidate[0]:
            candidate.write_bytes(b"changed after Reviewer invocation")
        identity, supplied_identity_digest = _review_identity_from_prompt(synthesized, contracts)
        review = contracts.PlanningReviewResult(
            reviewed_identity=identity,
            reviewed_identity_sha256=supplied_identity_digest,
            verdict="pass",
            findings=(),
        )
        payload = json.dumps(
            review.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        preflight = _preflight()
        assert preflight.repository is not None
        evidence = contracts.PlanningSourceEvidence(
            repository="owner/repo",
            branch="feature/issue",
            upstream="origin/feature/issue",
            local_head="a" * 40,
            remote_head="a" * 40,
            source_manifest_hash=preflight.repository.source_manifest.source_manifest_hash,
            snapshot_id="b" * 64,
            remote_head_disposition="fetched_remote_tracking_ref",
        )
        return _successful_review_transport(
            payload,
            source_manifest_hash=evidence.source_manifest_hash,
        )

    result = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="archive-candidate",
            output_dir=review_output,
            candidate_path=candidate,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=review_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T13:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "review_completed")
    assert result.output["verdict"] == "pass"
    assert (review_output / result.output["review_result_file"]).is_file()
    assert len(calls) == 1
    assert calls[0].attachment_paths[1] == candidate
    assert all("reviewed-identity" not in str(path) for path in calls[0].attachment_paths)
    before_directories = tuple(review_output.iterdir())
    mutate_candidate[0] = True
    stale = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="archive-candidate",
            output_dir=review_output,
            candidate_path=candidate,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=review_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T13:01:00+00:00",
    )
    assert (stale.status, stale.reason) == ("stale", "review_target_changed")
    assert tuple(review_output.iterdir()) == before_directories
    assert len(calls) == 2


def test_git_bound_review_has_exact_three_documents_and_companion_targets(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    candidates.mkdir()
    output = tmp_path / "reviews"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_review"],
    )
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    candidate = candidates / created.output["candidate_identity"]["logical_filename"]
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
    captured: list[Path] = []

    def transport(**kwargs):
        contracts = __import__(
            "spec_dock_runtime.domain.issue_planning_contracts",
            fromlist=["PlanningContext"],
        )
        target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=target.canonical_issue_paths,
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
        captured.extend(synthesized.attachment_paths)
        identity, _digest = _review_identity_from_prompt(
            synthesized,
            contracts,
            expected_paths=target.canonical_issue_paths,
        )
        review = contracts.PlanningReviewResult(
            reviewed_identity=identity,
            reviewed_identity_sha256=identity.sha256,
            verdict="pass",
            findings=(),
        )
        payload = json.dumps(review.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        snapshot = _preflight()
        assert snapshot.repository is not None
        evidence = contracts.PlanningSourceEvidence(
            repository="owner/repo",
            branch="feature/issue",
            upstream="origin/feature/issue",
            local_head="a" * 40,
            remote_head="a" * 40,
            source_manifest_hash=snapshot.repository.source_manifest.source_manifest_hash,
            snapshot_id="b" * 64,
            remote_head_disposition="fetched_remote_tracking_ref",
        )
        return _successful_review_transport(
            payload,
            source_manifest_hash=evidence.source_manifest_hash,
        )

    result = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="git-bound",
            output_dir=output,
            candidate_path=candidate,
            reviewed_head="a" * 40,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T14:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "review_completed")
    assert captured[1:] == [candidate, *(repo / path for path in target.canonical_issue_paths)]
    before_directories = tuple(output.iterdir())
    stale = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="git-bound",
            output_dir=output,
            candidate_path=candidate,
            reviewed_head="a" * 40,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=transport,
        preflight_runner=lambda request: _preflight(blockers=("dirty_tracked",)),
        clock=lambda: "2026-07-28T14:01:00+00:00",
    )
    assert (stale.status, stale.reason) == ("stale", "review_target_changed")
    assert tuple(output.iterdir()) == before_directories


@pytest.mark.parametrize(
    ("transient_bytes", "expected_reason"),
    [
        (b"transient canonical target bytes", "review_target_changed"),
        (b"token=abc123secret", "sensitive_input_rejected"),
    ],
)
def test_git_bound_review_rejects_transient_exact_target_bytes_before_backend(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    transient_bytes: bytes,
    expected_reason: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    candidates.mkdir()
    output = tmp_path / "reviews"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_review"],
    )
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda _root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    candidate = candidates / created.output["candidate_identity"]["logical_filename"]
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
    manifest = build_source_manifest(repo, target.canonical_issue_paths)
    transient_target = repo / target.canonical_issue_paths[0]
    original_read_bytes = Path.read_bytes
    transient_reads = [0]
    original_open = os.open
    backend_calls: list[object] = []
    leaked_target_bytes: list[bytes] = []

    def transient_read(path: Path) -> bytes:
        if path == transient_target and transient_reads[0] == 0:
            transient_reads[0] += 1
            return transient_bytes
        return original_read_bytes(path)

    def transient_open(path, flags, *args, **kwargs):
        if path == transient_target.name and kwargs.get("dir_fd") is not None and transient_reads[0] == 0:
            transient_reads[0] += 1
            backup = transient_target.with_suffix(".original")
            transient_target.rename(backup)
            transient_target.write_bytes(transient_bytes)
            descriptor = original_open(path, flags, *args, **kwargs)
            transient_target.unlink()
            backup.rename(transient_target)
            return descriptor
        return original_open(path, flags, *args, **kwargs)

    def backend(**kwargs):
        backend_calls.append(kwargs)
        synthesized = kwargs["synthesized"]
        contracts = __import__(
            "spec_dock_runtime.domain.issue_planning_contracts",
            fromlist=["PlanningReviewResult"],
        )
        identity, _digest = _review_identity_from_prompt(
            synthesized,
            contracts,
            expected_paths=target.canonical_issue_paths,
        )
        review = contracts.PlanningReviewResult(
            reviewed_identity=identity,
            reviewed_identity_sha256=identity.sha256,
            verdict="pass",
            findings=(),
        )
        payload = json.dumps(review.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        return _successful_review_transport(
            payload,
            source_manifest_hash=manifest.source_manifest_hash,
        )

    monkeypatch.setattr(Path, "read_bytes", transient_read)
    monkeypatch.setattr(os, "open", transient_open)
    result = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="git-bound",
            output_dir=output,
            candidate_path=candidate,
            reviewed_head="a" * 40,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=backend,
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
        clock=lambda: "2026-07-28T14:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "review_completed")
    assert len(backend_calls) == 1
    assert leaked_target_bytes == []
    assert len(tuple(output.iterdir())) == 2
    assert transient_target.exists()
    assert transient_bytes.decode("utf-8") not in repr(result)


@pytest.mark.parametrize("swap_kind", ["fifo", "symlink"])
def test_git_bound_review_target_swap_is_nonblocking_and_rejected_before_backend(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap_kind: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "reviews"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_review"],
    )
    target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
    manifest = build_source_manifest(repo, target.canonical_issue_paths)
    target_path = repo / target.canonical_issue_paths[0]
    sensitive_target = repo / "sensitive.md"
    sensitive_target.write_text("token=abc123secret", encoding="utf-8")
    original_open = os.open
    original_read_bytes = Path.read_bytes
    swapped = [False]
    backend_calls: list[object] = []

    def swap_target() -> None:
        if swapped[0]:
            return
        swapped[0] = True
        target_path.unlink()
        if swap_kind == "fifo":
            os.mkfifo(target_path)
        else:
            target_path.symlink_to(sensitive_target)

    def swap_during_open(path, flags, *args, **kwargs):
        if path == target_path.name and kwargs.get("dir_fd") is not None and not swapped[0]:
            swap_target()
            if swap_kind == "fifo":
                assert flags & os.O_NONBLOCK
        return original_open(path, flags, *args, **kwargs)

    def reject_blocking_pathname_read(path: Path) -> bytes:
        if path == target_path:
            swap_target()
            raise AssertionError("git-bound target used blocking pathname read")
        return original_read_bytes(path)

    def backend(**kwargs):
        backend_calls.append(kwargs)
        pytest.fail("unsafe target reached backend")

    monkeypatch.setattr(os, "open", swap_during_open)
    monkeypatch.setattr(Path, "read_bytes", reject_blocking_pathname_read)
    result = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="git-bound",
            output_dir=output,
            reviewed_head="a" * 40,
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=backend,
        preflight_runner=lambda request: _preflight(source_manifest=manifest),
    )
    assert result.status in {"rejected", "stale"}
    assert backend_calls == []
    assert list(output.iterdir()) == []


def test_mechanical_revision_requires_blocking_review_and_publishes_v2(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    revised = tmp_path / "revised"
    candidates.mkdir()
    revised.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_revise"],
    )
    snapshot = _preflight()
    assert snapshot.repository is not None
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=lambda **kwargs: _successful_transport(
            source_manifest_hash=snapshot.repository.source_manifest.source_manifest_hash
        ),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    identity = contracts.IssueCandidateIdentity.from_dict(created.output["candidate_identity"])
    reviewed_identity = contracts.ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        candidate_identity=identity,
    )
    finding = contracts.PlanningReviewFinding(
        id="F-1",
        severity="p1",
        exact_location="plan.md",
        violated_requirement_or_contradiction="missing exact wording",
        concrete_impact="cannot execute",
    )
    review = contracts.PlanningReviewResult(
        reviewed_identity=reviewed_identity,
        reviewed_identity_sha256=reviewed_identity.sha256,
        verdict="fail",
        findings=(finding,),
    )
    review_bytes = json.dumps(
        review.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    review_path = tmp_path / "review.json"
    review_path.write_bytes(review_bytes)
    request_path = tmp_path / "mechanical.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "lane": "mechanical",
                "candidate_identity": identity.to_dict(),
                "preserve_assumptions": ["scope"],
                "target_file": "plan.md",
                "old_text": "Substantive",
                "new_text": "Executable",
                "meaning_invariant": "same scope",
                "diff_budget": len(b"Substantive") + len(b"Executable"),
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    backend_calls: list[object] = []
    candidate_path = candidates / identity.logical_filename
    old_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(candidate_path, request_path, revised),
        review_evidence=module.PlanningRevisionEvidenceInput(
            review_path,
            hashlib.sha256(review_bytes).hexdigest(),
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T15:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "candidate_revised")
    assert result.output["candidate_identity"]["version"] == 2
    assert backend_calls == []
    assert hashlib.sha256(candidate_path.read_bytes()).hexdigest() == old_sha


def test_p2_only_review_blocks_revision_without_backend_or_candidate(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    revised = tmp_path / "revised"
    candidates.mkdir()
    revised.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_revise"],
    )
    snapshot = _preflight()
    assert snapshot.repository is not None
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(
            source_manifest_hash=snapshot.repository.source_manifest.source_manifest_hash
        ),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    identity = contracts.IssueCandidateIdentity.from_dict(created.output["candidate_identity"])
    reviewed_identity = contracts.ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        candidate_identity=identity,
    )
    review = contracts.PlanningReviewResult(
        reviewed_identity=reviewed_identity,
        reviewed_identity_sha256=reviewed_identity.sha256,
        verdict="pass",
        findings=(
            contracts.PlanningReviewFinding(
                id="F-2",
                severity="p2",
                exact_location="plan.md",
                violated_requirement_or_contradiction="observation",
                concrete_impact="non-blocking",
            ),
        ),
    )
    review_bytes = json.dumps(review.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    review_path = tmp_path / "review.json"
    review_path.write_bytes(review_bytes)
    request_path = tmp_path / "mechanical.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "lane": "mechanical",
                "candidate_identity": identity.to_dict(),
                "preserve_assumptions": [],
                "target_file": "plan.md",
                "old_text": "Substantive",
                "new_text": "Executable",
                "meaning_invariant": "same scope",
                "diff_budget": 100,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    backend_calls: list[object] = []
    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            candidates / identity.logical_filename,
            request_path,
            revised,
        ),
        review_evidence=module.PlanningRevisionEvidenceInput(
            review_path,
            hashlib.sha256(review_bytes).hexdigest(),
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: backend_calls.append(kwargs),
        preflight_runner=lambda request: _preflight(),
    )
    assert (result.status, result.reason) == ("blocked", "revision_not_required")
    assert backend_calls == []
    assert list(revised.iterdir()) == []


def test_semantic_revision_uses_exact_review_and_complete_replacement(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    revised = tmp_path / "revised"
    candidates.mkdir()
    revised.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_revise"],
    )
    snapshot = _preflight()
    assert snapshot.repository is not None
    source_hash = snapshot.repository.source_manifest.source_manifest_hash
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(source_manifest_hash=source_hash),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    identity = contracts.IssueCandidateIdentity.from_dict(created.output["candidate_identity"])
    reviewed_identity = contracts.ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        candidate_identity=identity,
    )
    review = contracts.PlanningReviewResult(
        reviewed_identity=reviewed_identity,
        reviewed_identity_sha256=reviewed_identity.sha256,
        verdict="fail",
        findings=(
            contracts.PlanningReviewFinding(
                id="F-1",
                severity="p1",
                exact_location="design.md",
                violated_requirement_or_contradiction="missing behavior",
                concrete_impact="implementation blocked",
            ),
        ),
    )
    review_bytes = json.dumps(review.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    review_sha = hashlib.sha256(review_bytes).hexdigest()
    review_path = tmp_path / "review.json"
    review_path.write_bytes(review_bytes)
    request_path = tmp_path / "semantic.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "lane": "semantic",
                "candidate_identity": identity.to_dict(),
                "preserve_assumptions": ["keep scope"],
                "finding_ids": ["F-1"],
                "review_result_sha256": review_sha,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    calls: list[SynthesizedPlanningPrompt] = []

    def semantic_transport(**kwargs):
        target = resolve_existing_issue_target("iss-00003", [_record(issue_dir)], repo)
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=(),
            operator_context=(),
        )
        synthesized = kwargs["prompt_synthesizer"](
            role="planner",
            context=context,
            repo_root=repo,
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )
        calls.append(synthesized)
        return _successful_transport(
            _planner_payload(
                companion_path=("artifacts/20260728t160000z-guide-new-member-chatgpt-first-issue-planning.md")
            ),
            source_manifest_hash=source_hash,
        )

    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            candidates / identity.logical_filename,
            request_path,
            revised,
        ),
        review_evidence=module.PlanningRevisionEvidenceInput(review_path, review_sha),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=semantic_transport,
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T16:00:00+00:00",
    )
    assert (result.status, result.reason) == ("ok", "candidate_revised")
    assert result.output["candidate_identity"]["version"] == 2
    assert len(calls) == 1
    assert calls[0].attachment_paths[1:4] == (
        candidates / identity.logical_filename,
        review_path,
        request_path,
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_identity",
        "wrong_attachment_digest",
        "verdict_mismatch",
        "authority_output",
        "secret_finding",
        "private_path_finding",
    ],
)
def test_review_rejects_malformed_wrong_identity_digest_verdict_and_authority_output(
    tmp_path: Path,
    mutation: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    output = tmp_path / "reviews"
    output.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_review"],
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    identity = contracts.IssueCandidateIdentity(
        issue_id="iss-00003",
        candidate_id="iss-00003-v1-token",
        version=1,
        logical_filename="candidate.zip",
        observed_transport_filename="candidate.zip",
        internal_root="candidate",
        source_repository="owner/repo",
        source_branch="feature/issue",
        source_head="a" * 40,
        zip_sha256="d" * 64,
    )
    candidate = _VerifiedIssueCandidate(
        identity=identity,
        files={DEFAULT_COMPANION_PATH: _onboarding_companion()},
        source_baseline={},
        zip_bytes=b"candidate",
        onboarding_companion=contracts.OnboardingCompanionBindingV1(
            path=DEFAULT_COMPANION_PATH,
            sha256=hashlib.sha256(_onboarding_companion()).hexdigest(),
        ),
    )
    publisher_calls: list[object] = []

    def transport(**kwargs):
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=resolve_existing_issue_target(
                "iss-00003",
                [_record(issue_dir)],
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
        runtime_identity, supplied_identity_digest = _review_identity_from_prompt(synthesized, contracts)
        finding = {
            "id": "F-1",
            "severity": "p1",
            "exact_location": "plan.md",
            "violated_requirement_or_contradiction": "violation",
            "concrete_impact": "impact",
        }
        value = {
            "reviewed_identity": runtime_identity.to_dict(),
            "reviewed_identity_sha256": supplied_identity_digest,
            "verdict": "fail",
            "findings": [finding],
        }
        if mutation == "wrong_identity":
            value["reviewed_identity"] = {
                **runtime_identity.to_dict(),
                "candidate_identity": {
                    **identity.to_dict(),
                    "candidate_id": "iss-00003-v1-other",
                },
            }
            other = contracts.ReviewedPlanningIdentity.from_dict(value["reviewed_identity"])
            value["reviewed_identity_sha256"] = other.sha256
        else:
            if mutation == "wrong_attachment_digest":
                value["reviewed_identity_sha256"] = "e" * 64
            elif mutation == "verdict_mismatch":
                value["verdict"] = "pass"
            elif mutation == "authority_output":
                value["patch"] = "forbidden"
            elif mutation == "secret_finding":
                value["findings"][0]["concrete_impact"] = "token=abc123secret"
            else:
                value["findings"][0]["exact_location"] = "/Users/alice/private/spec.md"
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        evidence = contracts.PlanningSourceEvidence(
            repository="owner/repo",
            branch="feature/issue",
            upstream="origin/feature/issue",
            local_head="a" * 40,
            remote_head="a" * 40,
            source_manifest_hash="b" * 64,
            snapshot_id="c" * 64,
            remote_head_disposition="fetched_remote_tracking_ref",
        )
        return _successful_review_transport(
            payload,
            source_manifest_hash=evidence.source_manifest_hash,
        )

    result = module.run_issue_planning_review(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviewRequest(
            issue_id="iss-00003",
            mode="archive-candidate",
            output_dir=output,
            candidate_path=tmp_path / "candidate.zip",
        ),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=transport,
        candidate_loader=lambda path, root: candidate,
        publisher=lambda **kwargs: publisher_calls.append(kwargs),
    )
    assert (result.status, result.reason) == ("rejected", "review_result_rejected")
    assert publisher_calls == []
    assert list(output.iterdir()) == []
    assert "abc123secret" not in repr(result)
    assert "/Users/alice" not in repr(result)


def _semantic_revision_setup(tmp_path: Path) -> dict[str, Any]:
    repo = tmp_path / "repo"
    repo.mkdir()
    issue_dir = _planning_tree(repo)
    candidates = tmp_path / "candidates"
    revised = tmp_path / "revised"
    candidates.mkdir()
    revised.mkdir()
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["run_issue_planning_revise"],
    )
    snapshot = _preflight()
    assert snapshot.repository is not None
    source_hash = snapshot.repository.source_manifest.source_manifest_hash
    created = module.run_issue_planning_create(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningCreateRequest("iss-00003", candidates),
        records=[_record(issue_dir)],
        repo_root=repo,
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(source_manifest_hash=source_hash),
        preflight_runner=lambda _request: _preflight(),
        clock=lambda: "2026-07-28T12:00:00+00:00",
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["IssueCandidateIdentity"],
    )
    identity = contracts.IssueCandidateIdentity.from_dict(created.output["candidate_identity"])
    reviewed_identity = contracts.ReviewedPlanningIdentity(
        mode="archive-candidate",
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        candidate_identity=identity,
    )
    review = contracts.PlanningReviewResult(
        reviewed_identity=reviewed_identity,
        reviewed_identity_sha256=reviewed_identity.sha256,
        verdict="fail",
        findings=(
            contracts.PlanningReviewFinding(
                id="F-1",
                severity="p1",
                exact_location="design.md",
                violated_requirement_or_contradiction="missing behavior",
                concrete_impact="implementation blocked",
            ),
        ),
    )
    review_bytes = json.dumps(review.to_dict(), sort_keys=True, separators=(",", ":")).encode()
    review_sha = hashlib.sha256(review_bytes).hexdigest()
    review_path = tmp_path / "review.json"
    review_path.write_bytes(review_bytes)
    request_path = tmp_path / "semantic.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "lane": "semantic",
                "candidate_identity": identity.to_dict(),
                "preserve_assumptions": ["keep scope"],
                "finding_ids": ["F-1"],
                "review_result_sha256": review_sha,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    return {
        "repo": repo,
        "issue_dir": issue_dir,
        "candidates": candidates,
        "revised": revised,
        "module": module,
        "contracts": contracts,
        "identity": identity,
        "review_path": review_path,
        "review_sha": review_sha,
        "request_path": request_path,
        "source_hash": source_hash,
    }


def test_revision_without_explicit_evidence_uses_exact_review_sibling(
    tmp_path: Path,
) -> None:
    setup = _semantic_revision_setup(tmp_path)
    request_path = setup["request_path"]
    sibling_request = request_path.with_name("planning-revision-request.json")
    request_path.rename(sibling_request)
    review_path = setup["review_path"]
    sibling_review = sibling_request.with_name("planning-review-result.json")
    review_path.rename(sibling_review)
    module = setup["module"]
    identity = setup["identity"]

    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            setup["candidates"] / identity.logical_filename,
            sibling_request,
            setup["revised"],
        ),
        records=[_record(setup["issue_dir"])],
        repo_root=setup["repo"],
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: _successful_transport(
            source_manifest_hash=setup["source_hash"],
            companion_path=("artifacts/20260728t121000z-guide-new-member-chatgpt-first-issue-planning.md"),
        ),
        preflight_runner=lambda request: _preflight(),
        clock=lambda: "2026-07-28T12:10:00+00:00",
    )

    assert (result.status, result.reason) == ("ok", "candidate_revised")


def test_revision_does_not_scan_for_review_evidence(tmp_path: Path) -> None:
    setup = _semantic_revision_setup(tmp_path)
    request_path = setup["request_path"]
    sibling_request = request_path.with_name("planning-revision-request.json")
    request_path.rename(sibling_request)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    setup["review_path"].rename(elsewhere / "planning-review-result.json")
    module = setup["module"]
    identity = setup["identity"]

    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            setup["candidates"] / identity.logical_filename,
            sibling_request,
            setup["revised"],
        ),
        records=[_record(setup["issue_dir"])],
        repo_root=setup["repo"],
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("backend must not run"),
        preflight_runner=lambda request: _preflight(),
    )

    assert (result.status, result.reason) == ("blocked", "revision_review_unavailable")


@pytest.mark.parametrize(
    ("field", "sensitive_value"),
    [
        ("concrete_impact", "credential token=abc123secret"),
        ("exact_location", "/Users/alice/private/spec.md"),
    ],
)
def test_semantic_revision_rejects_sensitive_external_review_before_backend(
    tmp_path: Path,
    field: str,
    sensitive_value: str,
) -> None:
    setup = _semantic_revision_setup(tmp_path)
    review_path = setup["review_path"]
    review_value = json.loads(review_path.read_text(encoding="utf-8"))
    review_value["findings"][0][field] = sensitive_value
    review_bytes = json.dumps(
        review_value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    review_path.write_bytes(review_bytes)
    review_sha = hashlib.sha256(review_bytes).hexdigest()
    request_path = setup["request_path"]
    request_value = json.loads(request_path.read_text(encoding="utf-8"))
    request_value["review_result_sha256"] = review_sha
    request_path.write_text(
        json.dumps(request_value, separators=(",", ":")),
        encoding="utf-8",
    )
    backend_calls: list[object] = []
    leaked_review_bytes: list[bytes] = []

    def transport(**kwargs):
        backend_calls.append(kwargs)
        target = resolve_existing_issue_target(
            "iss-00003",
            [_record(setup["issue_dir"])],
            setup["repo"],
        )
        contracts = setup["contracts"]
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=(),
            operator_context=(),
        )
        synthesized = kwargs["prompt_synthesizer"](
            role="planner",
            context=context,
            repo_root=setup["repo"],
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )
        assert review_path in synthesized.attachment_paths
        return contracts.PlanningInvocationResult(
            status="blocked",
            reason="backend_timeout",
        )

    module = setup["module"]
    identity = setup["identity"]
    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            setup["candidates"] / identity.logical_filename,
            request_path,
            setup["revised"],
        ),
        review_evidence=module.PlanningRevisionEvidenceInput(review_path, review_sha),
        records=[_record(setup["issue_dir"])],
        repo_root=setup["repo"],
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: pytest.fail("transport runner owns this fixture"),
        transport_runner=transport,
        preflight_runner=lambda request: _preflight(),
    )
    assert (result.status, result.reason) == ("rejected", "revision_evidence_mismatch")
    assert backend_calls == []
    assert leaked_review_bytes == []
    assert list(setup["revised"].iterdir()) == []
    assert sensitive_value not in repr(result)


@pytest.mark.parametrize("mutation", ["partial", "extra", "wrong_issue", "scope_escape"])
def test_semantic_partial_extra_wrong_issue_or_scope_escape_publishes_zero(
    tmp_path: Path,
    mutation: str,
) -> None:
    setup = _semantic_revision_setup(tmp_path)
    module = setup["module"]
    identity = setup["identity"]
    payload = _planner_payload()
    if mutation == "partial":
        source = zipfile.ZipFile(io.BytesIO(payload))
        output = io.BytesIO()
        with source, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
            for info in source.infolist():
                if not info.filename.endswith("/plan.md"):
                    archive.writestr(info, source.read(info.filename))
        payload = output.getvalue()
    elif mutation == "extra":
        payload += b"\nextra"
    elif mutation == "wrong_issue":
        payload = payload.replace(b"iss-00003", b"iss-99999")
    else:
        payload = payload.replace(b"epic-00002", b"epic-99999")

    def transport(**kwargs):
        contracts = setup["contracts"]
        target = resolve_existing_issue_target(
            "iss-00003",
            [_record(setup["issue_dir"])],
            setup["repo"],
        )
        context = contracts.PlanningContext(
            issue_id="iss-00003",
            repository="owner/repo",
            branch="feature/issue",
            source_head="a" * 40,
            parent_epic_id="epic-00002",
            parent_initiative_id="init-00001",
            dependency_summary=(),
            canonical_issue_paths=target.canonical_issue_paths,
            relevant_source_paths=(),
            operator_context=(),
        )
        kwargs["prompt_synthesizer"](
            role="planner",
            context=context,
            repo_root=setup["repo"],
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )
        return _successful_transport(
            payload,
            source_manifest_hash=setup["source_hash"],
        )

    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            setup["candidates"] / identity.logical_filename,
            setup["request_path"],
            setup["revised"],
        ),
        review_evidence=module.PlanningRevisionEvidenceInput(
            setup["review_path"],
            setup["review_sha"],
        ),
        records=[_record(setup["issue_dir"])],
        repo_root=setup["repo"],
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=transport,
        preflight_runner=lambda request: _preflight(),
    )
    assert (result.status, result.reason) == ("rejected", "planner_response_rejected")
    assert list(setup["revised"].iterdir()) == []


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("blocked", "backend_timeout"),
        ("blocked", "backend_nonzero"),
        ("rejected", "backend_response_malformed"),
    ],
)
def test_semantic_transport_nonpass_preserves_existing_reason(
    tmp_path: Path,
    status: str,
    reason: str,
) -> None:
    setup = _semantic_revision_setup(tmp_path)
    module = setup["module"]
    identity = setup["identity"]
    contracts = setup["contracts"]
    result = module.run_issue_planning_revise(
        dependencies=PLANNING_DEPENDENCIES,
        request=module.PlanningReviseRequest(
            setup["candidates"] / identity.logical_filename,
            setup["request_path"],
            setup["revised"],
        ),
        review_evidence=module.PlanningRevisionEvidenceInput(
            setup["review_path"],
            setup["review_sha"],
        ),
        records=[_record(setup["issue_dir"])],
        repo_root=setup["repo"],
        repo_slug_resolver=lambda root: "owner/repo",
        backend_invoker=lambda **kwargs: None,
        transport_runner=lambda **kwargs: contracts.PlanningInvocationResult(
            status=status,
            reason=reason,
        ),
        preflight_runner=lambda request: _preflight(),
    )
    assert (result.status, result.reason) == (status, reason)
    assert list(setup["revised"].iterdir()) == []


@pytest.mark.parametrize("swap_kind", ["fifo", "symlink"])
def test_revision_request_transient_swap_is_nonblocking_and_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    swap_kind: str,
) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_read_external_bounded_file"],
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    request_path = tmp_path / "revision.json"
    request_path.write_text("{}", encoding="utf-8")
    original_open = os.open
    swapped = [False]

    def swap_before_open(path, flags, *args, **kwargs):
        if (
            Path(path) == request_path or (path == request_path.name and kwargs.get("dir_fd") is not None)
        ) and not swapped[0]:
            swapped[0] = True
            request_path.unlink()
            if swap_kind == "fifo":
                os.mkfifo(request_path)
                assert flags & os.O_NONBLOCK
            else:
                request_path.symlink_to(repo)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", swap_before_open)
    with pytest.raises(ValueError):
        module._read_external_bounded_file(
            request_path,
            repo_root=repo,
            gateway=PLANNING_DEPENDENCIES.gateway,
        )
    assert swapped == [True]


def test_revision_request_rejects_oversize_without_pathname_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_read_external_bounded_file"],
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    request_path = tmp_path / "revision.json"
    limit = 1024 * 1024
    request_path.write_bytes(b"x" * (limit + 1))
    original_read_bytes = Path.read_bytes
    pathname_reads = [0]
    descriptor_read_requests: list[int] = []
    original_os_read = os.read

    def observe_pathname_read(path: Path) -> bytes:
        if path == request_path:
            pathname_reads[0] += 1
        return original_read_bytes(path)

    def observe_descriptor_read(descriptor: int, count: int) -> bytes:
        descriptor_read_requests.append(count)
        return original_os_read(descriptor, count)

    monkeypatch.setattr(Path, "read_bytes", observe_pathname_read)
    monkeypatch.setattr(os, "read", observe_descriptor_read)
    with pytest.raises(ValueError, match="bounded"):
        module._read_external_bounded_file(
            request_path,
            repo_root=repo,
            gateway=PLANNING_DEPENDENCIES.gateway,
        )
    assert pathname_reads == [0]
    assert sum(descriptor_read_requests) <= limit + 1


def test_revision_request_parent_swap_never_redirects_into_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_read_external_bounded_file"],
    )
    repo = tmp_path / "repo"
    external = tmp_path / "external"
    repo.mkdir()
    external.mkdir()
    request_path = external / "revision.json"
    original_bytes = b"{}"
    redirected_bytes = b'{"token":"abc123secret"}'
    request_path.write_bytes(original_bytes)
    (repo / request_path.name).write_bytes(redirected_bytes)
    backup = tmp_path / "external-backup"
    original_open = os.open
    original_read_bytes = Path.read_bytes
    swapped = [False]

    def swap_parent() -> None:
        if swapped[0]:
            return
        swapped[0] = True
        external.rename(backup)
        external.symlink_to(repo, target_is_directory=True)

    def swap_during_open(path, flags, *args, **kwargs):
        if Path(path) == request_path and not swapped[0]:
            swap_parent()
            return original_open(path, flags, *args, **kwargs)
        if path == external.name and flags & getattr(os, "O_DIRECTORY", 0) and not swapped[0]:
            descriptor = original_open(path, flags, *args, **kwargs)
            swap_parent()
            return descriptor
        return original_open(path, flags, *args, **kwargs)

    def swap_during_pathname_read(path: Path) -> bytes:
        if path == request_path:
            swap_parent()
        return original_read_bytes(path)

    monkeypatch.setattr(os, "open", swap_during_open)
    monkeypatch.setattr(Path, "read_bytes", swap_during_pathname_read)
    data = module._read_external_bounded_file(
        request_path,
        repo_root=repo,
        gateway=PLANNING_DEPENDENCIES.gateway,
    )
    assert data == original_bytes
    assert redirected_bytes not in data
    assert swapped == [True]


def _preflight(
    *,
    blockers: tuple[str, ...] = (),
    branch: str = "feature/issue",
    upstream: str = "origin/feature/issue",
    source_manifest=None,
) -> PreflightResult:
    manifest = source_manifest or empty_source_manifest()
    repository = RepositorySnapshot(
        normalized_origin="github.com/owner/repo",
        branch=branch,
        local_head="a" * 40,
        upstream=upstream,
        effective_ref=branch,
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        worktree_state=blockers,
        source_manifest=manifest,
        snapshot_id="b" * 64,
    )
    return PreflightResult(
        status="blocked" if blockers else "pass",
        evidence_mode="github-synced",
        sync_state="blocked" if blockers else "synced",
        github_sync="failed" if blockers else "verified",
        requested_ref=branch,
        effective_ref=branch,
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest=manifest,
        source_hash_mismatch_checked=False,
        blockers=blockers,
        fetch=FetchSummary(status="failed" if "origin_fetch_failed" in blockers else "success"),
        freshness=FreshnessEvidence(
            snapshot_id="b" * 64,
            final_guard_snapshot_id="b" * 64,
            concurrent_change_check="changed" if "concurrent_repo_change" in blockers else "stable",
            remote_head_disposition="fetched_remote_tracking_ref",
        ),
        repository=repository,
    )


def _source_guard_probe(
    *,
    revision: bool,
    mutate_source: bool,
    preflight_error: BaseException | None = None,
) -> tuple[bool, list[str]]:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_review_publication_is_current", "_revision_publication_is_current"],
    )
    events: list[str] = []
    source_hash = ["a" * 64]
    target = SimpleNamespace(canonical_issue_paths=("requirement.md", "design.md", "plan.md"))
    evidence = SimpleNamespace(
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        source_manifest_hash="a" * 64,
    )
    candidate = SimpleNamespace(
        identity="candidate-identity",
        zip_bytes=b"candidate-zip",
        source_baseline={"relevant_paths": ()},
    )

    def candidate_loader(_path: Path, _repo_root: Path) -> SimpleNamespace:
        events.append("candidate_loader")
        if mutate_source:
            source_hash[0] = "b" * 64
        return candidate

    def preflight_runner(_request: object) -> PreflightResult:
        events.append("source_preflight")
        if preflight_error is not None:
            raise preflight_error
        return _preflight(source_manifest=SimpleNamespace(source_manifest_hash=source_hash[0]))

    if revision:
        result = module._revision_publication_is_current(
            candidate=candidate,
            current_candidate_loader=candidate_loader,
            candidate_path=Path("candidate.zip"),
            target=target,
            repo_root=Path("/repo"),
            source_evidence=evidence,
            preflight_runner=preflight_runner,
        )
    else:
        result = module._review_publication_is_current(
            target=target,
            relevant_source_paths=(),
            repo_root=Path("/repo"),
            evidence=evidence,
            preflight_runner=preflight_runner,
            candidate_path=Path("candidate.zip"),
            candidate=candidate,
            candidate_loader=candidate_loader,
        )
    return result, events


@pytest.mark.parametrize("revision", [False, True])
def test_publication_guard_rechecks_source_after_candidate_loader(revision: bool) -> None:
    result, events = _source_guard_probe(revision=revision, mutate_source=True)

    assert result is False
    assert events == ["candidate_loader", "source_preflight"]


@pytest.mark.parametrize("revision", [False, True])
def test_publication_guard_closes_source_preflight_exceptions(revision: bool) -> None:
    result, events = _source_guard_probe(
        revision=revision,
        mutate_source=False,
        preflight_error=RuntimeError("private preflight detail"),
    )

    assert result is False
    assert events == ["candidate_loader", "source_preflight"]


@pytest.mark.parametrize("revision", [False, True])
def test_publication_guard_validates_candidate_then_source_without_drift(revision: bool) -> None:
    result, events = _source_guard_probe(revision=revision, mutate_source=False)

    assert result is True
    assert events == ["candidate_loader", "source_preflight", "candidate_loader"]


@pytest.mark.parametrize("revision", [False, True])
@pytest.mark.parametrize("drift", ["identity", "zip"])
def test_publication_guard_rechecks_candidate_after_source_preflight(
    revision: bool,
    drift: str,
) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_review_publication_is_current", "_revision_publication_is_current"],
    )
    events: list[str] = []
    candidate = SimpleNamespace(
        identity="candidate-identity",
        zip_bytes=b"candidate-zip",
        source_baseline={"relevant_paths": ()},
    )
    replacement = SimpleNamespace(
        identity=("replacement-identity" if drift == "identity" else candidate.identity),
        zip_bytes=(b"replacement-zip" if drift == "zip" else candidate.zip_bytes),
        source_baseline={"relevant_paths": ()},
    )
    candidates = iter((candidate, replacement))

    def candidate_loader(_path: Path, _repo_root: Path) -> SimpleNamespace:
        events.append("candidate_loader")
        return next(candidates)

    def preflight_runner(_request: object) -> PreflightResult:
        events.append("source_preflight")
        return _preflight(source_manifest=SimpleNamespace(source_manifest_hash="a" * 64))

    target = SimpleNamespace(canonical_issue_paths=("requirement.md", "design.md", "plan.md"))
    evidence = SimpleNamespace(
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        source_manifest_hash="a" * 64,
    )
    if revision:
        result = module._revision_publication_is_current(
            candidate=candidate,
            current_candidate_loader=candidate_loader,
            candidate_path=Path("candidate.zip"),
            target=target,
            repo_root=Path("/repo"),
            source_evidence=evidence,
            preflight_runner=preflight_runner,
        )
    else:
        result = module._review_publication_is_current(
            target=target,
            relevant_source_paths=(),
            repo_root=Path("/repo"),
            evidence=evidence,
            preflight_runner=preflight_runner,
            candidate_path=Path("candidate.zip"),
            candidate=candidate,
            candidate_loader=candidate_loader,
        )

    assert result is False
    assert events == ["candidate_loader", "source_preflight", "candidate_loader"]


@pytest.mark.parametrize("revision", [False, True])
def test_publication_guard_revalidates_candidate_around_source_without_drift(revision: bool) -> None:
    module = __import__(
        "spec_dock_runtime.application.issue_planning",
        fromlist=["_review_publication_is_current", "_revision_publication_is_current"],
    )
    events: list[str] = []
    candidate = SimpleNamespace(
        identity="candidate-identity",
        zip_bytes=b"candidate-zip",
        source_baseline={"relevant_paths": ()},
    )

    def candidate_loader(_path: Path, _repo_root: Path) -> SimpleNamespace:
        events.append("candidate_loader")
        return candidate

    def preflight_runner(_request: object) -> PreflightResult:
        events.append("source_preflight")
        return _preflight(source_manifest=SimpleNamespace(source_manifest_hash="a" * 64))

    target = SimpleNamespace(canonical_issue_paths=("requirement.md", "design.md", "plan.md"))
    evidence = SimpleNamespace(
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        remote_head_disposition="fetched_remote_tracking_ref",
        source_manifest_hash="a" * 64,
    )
    if revision:
        result = module._revision_publication_is_current(
            candidate=candidate,
            current_candidate_loader=candidate_loader,
            candidate_path=Path("candidate.zip"),
            target=target,
            repo_root=Path("/repo"),
            source_evidence=evidence,
            preflight_runner=preflight_runner,
        )
    else:
        result = module._review_publication_is_current(
            target=target,
            relevant_source_paths=(),
            repo_root=Path("/repo"),
            evidence=evidence,
            preflight_runner=preflight_runner,
            candidate_path=Path("candidate.zip"),
            candidate=candidate,
            candidate_loader=candidate_loader,
        )

    assert result is True
    assert events == ["candidate_loader", "source_preflight", "candidate_loader"]
