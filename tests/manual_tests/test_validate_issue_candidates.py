import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/authoring-pack/validate_issue_candidates.py"
REVIEW_SCRIPT = REPO_ROOT / "scripts/authoring-pack/review_chatgpt_authoring_pack.py"
FIXTURE_SOURCE = "scripts/authoring-pack/README.md"


def run_validate(
    review_report: Path,
    pack_tree: Path,
    output_dir: Path,
    *extra: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--review-report",
            str(review_report),
            "--pack-tree",
            str(pack_tree),
            "--expected-parent-epic",
            "epic-00283",
            "--expected-requirement",
            "E-RQ-011",
            "--expected-acceptance",
            "E-AC-007",
            "--expected-acceptance",
            "E-AC-011",
            "--output-dir",
            str(output_dir),
            *extra,
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_review(pack_tree: Path, preflight: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(REVIEW_SCRIPT),
            "--input",
            str(pack_tree),
            "--preflight",
            str(preflight),
            "--output-dir",
            str(output_dir),
            "--input-kind",
            "tree",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def preflight_data(*, source_sha: str | None = None) -> dict:
    source_sha = source_sha or sha256(REPO_ROOT / FIXTURE_SOURCE)
    return {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "status": "pass",
        "repository": {
            "full_name": "chemitaro/spec-dock",
            "requested_ref": "iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack",
            "observed_ref": "iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack",
        },
        "safe_output_constraints": {
            "expected_zip_root": "specdock-authoring-pack/",
            "forbidden_claims": [
                "spec-reviewer passed",
                "reviewer pass",
                "adoption_status: adopted",
                ".assurance.json updated",
                "pull request created",
                "implementation complete",
                "canonical overwrite",
                "authority: canonical",
            ],
        },
        "sources": [
            {
                "path": FIXTURE_SOURCE,
                "sha256": source_sha,
                "role": "readme",
            }
        ],
        "stale_if": [
            {
                "kind": "source_hash_changed",
                "source_paths": [FIXTURE_SOURCE],
            }
        ],
    }


def write_preflight(path: Path) -> Path:
    return write_json(path, preflight_data())


def pack_digest(pack_root: Path) -> dict:
    files: dict[str, str] = {}
    for path in sorted(pack_root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(pack_root).as_posix()
        files[f"specdock-authoring-pack/{relative}"] = path.read_text(encoding="utf-8")
    digest = hashlib.sha256()
    for rel_path in sorted(files):
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files[rel_path].encode("utf-8"))
        digest.update(b"\0")
    return {
        "algorithm": "sha256",
        "content_sha256": digest.hexdigest(),
        "file_count": len(files),
    }


def write_review_report(path: Path, pack_root: Path, *, status: str = "pass") -> Path:
    payload = {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "status": status,
        "generated_at": "2026-07-07T00:00:00Z",
        "input_kind": "tree",
        "trace": {
            "issue_id": "iss-00288",
            "parent_epic": "epic-00283",
        },
        "sources": [],
    }
    if status == "pass":
        payload["pack_digest"] = pack_digest(pack_root)
    return write_json(path, payload)


def boundary() -> dict:
    return {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
    }


def parent_trace(**overrides: object) -> dict:
    trace: dict[str, object] = {
        "epic_id": "epic-00283",
        "requirements": ["E-RQ-011"],
        "acceptance": ["E-AC-007", "E-AC-011"],
    }
    trace.update(overrides)
    return trace


def candidate_payload(candidate_id: str, title: str, **overrides: object) -> dict:
    payload: dict[str, object] = {
        **boundary(),
        "schema_version": "1",
        "candidate_id": candidate_id,
        "title": title,
        "parent_trace": parent_trace(),
        "scope": [f"{title} scope"],
        "non_scope": ["direct canonical document mutation", "review gate substitution"],
        "dependencies": ["iss-00284", "iss-00285"],
        "boundary_metadata": {
            "canonical_written": False,
            "assurance_mutated": False,
            "review_gate_claimed": False,
            "selected_skeleton_fill": False,
            "profile_specific_template_body": False,
        },
        "files": {
            "requirement": "draft-requirement.md",
            "design_brief": "draft-design-brief.md",
            "plan_brief": "draft-plan-brief.md",
            "profile": "profile.json",
        },
    }
    payload.update(overrides)
    return payload


def profile_payload(candidate_id: str, **overrides: object) -> dict:
    payload: dict[str, object] = {
        **boundary(),
        "schema_version": "1",
        "candidate_id": candidate_id,
        "profile_recommendation": {
            "profile": "standard",
            "rationale": "candidate-only recommendation",
            "advisory_only": True,
            "ignored_for_authority": True,
        },
        "authorized_profile": None,
        "profile_authority": "local_assurance_only",
        "assurance_mutated": False,
    }
    payload.update(overrides)
    return payload


def write_candidate(
    pack_root: Path,
    candidate_id: str,
    *,
    title: str | None = None,
    candidate: dict | None = None,
    profile: dict | None = None,
    draft_text: str = "候補の境界を説明するドラフトです。",
) -> None:
    title = title or candidate_id
    candidate_dir = pack_root / "candidates/issues" / candidate_id
    write_json(candidate_dir / "candidate.json", candidate or candidate_payload(candidate_id, title))
    write_json(candidate_dir / "profile.json", profile or profile_payload(candidate_id))
    (candidate_dir / "draft-requirement.md").write_text(f"# Requirement\n\n{draft_text}\n", encoding="utf-8")
    (candidate_dir / "draft-design-brief.md").write_text(f"# Design brief\n\n{draft_text}\n", encoding="utf-8")
    (candidate_dir / "draft-plan-brief.md").write_text(f"# Plan brief\n\n{draft_text}\n", encoding="utf-8")


def write_pack_tree(root: Path, *, candidates: list[dict] | None = None) -> Path:
    pack_root = root / "specdock-authoring-pack"
    source_sha = sha256(REPO_ROOT / FIXTURE_SOURCE)
    write_json(
        pack_root / "manifest.json",
        {
            **boundary(),
            "pack_id": "pack-iss-00288",
            "expected_zip_root": "specdock-authoring-pack/",
            "schema_version": "1",
        },
    )
    write_json(
        pack_root / "provenance.json",
        {
            "authority": "evidence_only",
            "repository": {
                "full_name": "chemitaro/spec-dock",
                "requested_ref": "iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack",
            },
            "source": "chatgpt_zip_authoring_pack",
        },
    )
    write_json(
        pack_root / "source-manifest.json",
        {
            "sources": [
                {
                    "path": FIXTURE_SOURCE,
                    "sha256": source_sha,
                    "role": "readme",
                }
            ]
        },
    )
    write_json(
        pack_root / "stale-if.json",
        {
            "stale_if": [
                {
                    "kind": "source_hash_changed",
                    "source_paths": [FIXTURE_SOURCE],
                }
            ]
        },
    )
    write_json(
        pack_root / "adoption/adoption-map.json",
        {
            "items": [
                {
                    "source_path": "candidates/issues/index.json",
                    "target": "evidence-only",
                    "adoption_status": "unreviewed",
                    "required_local_validation": ["local-candidate-validation"],
                }
            ]
        },
    )
    candidates = candidates or [
        {"candidate_id": "issue-candidate-001", "title": "First candidate"},
        {"candidate_id": "issue-candidate-002", "title": "Second candidate"},
    ]
    refs = []
    for item in candidates:
        candidate_id = item["candidate_id"]
        refs.append({
            "candidate_id": candidate_id,
            "path": f"candidates/issues/{candidate_id}/candidate.json",
        })
        write_candidate(
            pack_root,
            candidate_id,
            title=item.get("title"),
            candidate=item.get("candidate"),
            profile=item.get("profile"),
            draft_text=item.get("draft_text", "候補の境界を説明するドラフトです。"),
        )
    write_json(
        pack_root / "candidates/issues/index.json",
        {
            **boundary(),
            "schema_version": "1",
            "parent_trace": parent_trace(),
            "candidates": refs,
        },
    )
    return pack_root


def assert_no_leak(result: subprocess.CompletedProcess[str], output_dir: Path, *payloads: str) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    for name in (
        "issue-candidate-validation-report.json",
        "issue-candidate-comparison-summary.md",
        "issue-candidate-validation-summary.md",
    ):
        path = output_dir / name
        if path.exists():
            combined += "\n" + path.read_text(encoding="utf-8")
    for payload in payloads:
        assert payload not in combined
    assert "/Users/" not in combined
    assert "/home/" not in combined
    assert "/Volumes/" not in combined
    assert "/private/" not in combined


def test_valid_issue_candidates_pack_writes_report_and_comparison_summary(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    output_dir = tmp_path / "validation"
    protected_dir = tmp_path / "issue"
    protected_docs = []
    for name in ("requirement.md", "design.md", "plan.md", "report.md", ".assurance.json"):
        path = protected_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name} before\n", encoding="utf-8")
        protected_docs.append(path)
    before = {path: path.read_bytes() for path in protected_docs}

    result = run_validate(review_report, pack_root, output_dir)

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "issue-candidate-validation-report.json")
    comparison = read_json(output_dir / "issue-candidate-comparison-summary.json")
    assert report["status"] == "pass"
    assert report["authority"] == "evidence_only"
    assert report["adoption_status"] == "unreviewed"
    assert report["adoption"]["canonical_written"] is False
    assert report["adoption"]["assurance_mutated"] is False
    assert report["adoption"]["reviewer_pass_claimed"] is False
    assert comparison["candidate_count"] == 2
    assert comparison["adoption_eligible_count"] == 2
    assert comparison["dependency_index"]["iss-00284"] == ["issue-candidate-001", "issue-candidate-002"]
    assert (output_dir / ".specdock-issue-candidates-validation").exists()
    for path, original in before.items():
        assert path.read_bytes() == original


def test_valid_candidate_pack_passes_generic_review_before_candidate_validation(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_dir = tmp_path / "review"

    review = run_review(pack_root, write_preflight(tmp_path / "preflight.json"), review_dir)

    assert review.returncode == 0, review.stderr
    review_report = review_dir / "validation-report.json"
    assert read_json(review_report)["status"] == "pass"

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 0, result.stderr
    assert read_json(tmp_path / "validation/issue-candidate-validation-report.json")["status"] == "pass"


def test_review_report_not_pass_propagates_status_without_candidate_validation(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root, status="rejected")

    result = run_validate(review_report, tmp_path / "missing-pack", tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "review report status is not pass: rejected" in report["errors"]
    assert "pack tree could not be observed" not in report["errors"]


def test_pack_digest_mismatch_is_stale(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    (pack_root / "candidates/issues/issue-candidate-001/draft-requirement.md").write_text(
        "# changed\n", encoding="utf-8"
    )

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 3
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "stale"
    assert "pack tree digest does not match review report" in report["errors"]


def test_missing_parent_trace_is_blocked(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    index = read_json(pack_root / "candidates/issues/index.json")
    del index["parent_trace"]
    write_json(pack_root / "candidates/issues/index.json", index)
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 2
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "blocked"
    assert "parent_trace is required" in report["errors"]


def test_missing_boundary_metadata_is_blocked(tmp_path) -> None:
    candidate = candidate_payload("issue-candidate-001", "Missing boundary")
    del candidate["boundary_metadata"]["canonical_written"]
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "candidate": candidate}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 2
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "blocked"
    assert "issue-candidate.boundary_metadata.canonical_written is required" in report["errors"]


def test_boundary_metadata_extra_key_is_rejected(tmp_path) -> None:
    candidate = candidate_payload("issue-candidate-001", "Extra boundary")
    candidate["boundary_metadata"]["unexpected_boundary"] = False
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "candidate": candidate}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "issue-candidate.boundary_metadata.unexpected_boundary is not allowed" in report["errors"]


@pytest.mark.parametrize(
    "update",
    [
        {"authority": "canonical"},
        {"adoption_status": "adopted"},
    ],
)
def test_unsafe_boundary_value_is_rejected(tmp_path, update: dict) -> None:
    candidate = candidate_payload("issue-candidate-001", "Unsafe boundary")
    candidate.update(update)
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "candidate": candidate}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"


def test_authorized_profile_claim_is_rejected(tmp_path) -> None:
    profile = profile_payload("issue-candidate-001", authorized_profile="standard")
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "profile": profile}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "candidate metadata must not claim authorized_profile" in report["errors"]


def test_profile_recommendation_must_be_advisory_only(tmp_path) -> None:
    profile = profile_payload("issue-candidate-001")
    profile["profile_recommendation"]["advisory_only"] = False
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "profile": profile}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "issue-candidate-profile.profile_recommendation must be advisory-only" in report["errors"]


def test_selected_skeleton_fill_path_is_rejected_in_candidate_pack(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    write_json(pack_root / "selected-skeleton-fill/section-fills.json", {"section_fills": []})
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "candidate pack contains profile-specific or selected-skeleton output path" in report["errors"]


def test_profile_specific_template_body_or_all_profile_variants_are_rejected(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    (pack_root / "all-profiles").mkdir()
    (pack_root / "all-profiles/strict.md").write_text("strict body\n", encoding="utf-8")
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"


def test_profiles_path_segment_is_rejected(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    (pack_root / "candidates/issues/issue-candidate-001/profiles/standard").mkdir(parents=True)
    (pack_root / "candidates/issues/issue-candidate-001/profiles/standard/design.md").write_text(
        "profile-specific body\n",
        encoding="utf-8",
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"


def test_profile_specific_metadata_key_is_rejected(tmp_path) -> None:
    candidate = candidate_payload(
        "issue-candidate-001",
        "Profile metadata",
        template_sha256="a" * 64,
    )
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "candidate": candidate}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert "candidate metadata contains selected-skeleton or profile-specific template keys" in report["errors"]


def test_missing_candidate_scope_dependency_or_non_scope_is_fail(tmp_path) -> None:
    candidate = candidate_payload("issue-candidate-001", "Missing scope")
    del candidate["scope"]
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[{"candidate_id": "issue-candidate-001", "candidate": candidate}],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 1
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "fail"
    assert "issue-candidate.scope must be a string array" in report["errors"]


def test_duplicate_candidate_scope_is_reported_not_silently_passed(tmp_path) -> None:
    first = candidate_payload("issue-candidate-001", "Same title", scope=["same scope"])
    second = candidate_payload("issue-candidate-002", "Same title", scope=["same scope"])
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[
            {"candidate_id": "issue-candidate-001", "candidate": first},
            {"candidate_id": "issue-candidate-002", "candidate": second},
        ],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 0, result.stderr
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    comparison = report["comparison"]
    assert report["status"] == "pass"
    assert comparison["duplicate_title_groups"]
    assert comparison["duplicate_scope_groups"]
    assert "duplicate candidate titles detected" in report["warnings"]


def test_output_directory_ownership_guard_and_redaction(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    output_dir = tmp_path / "validation"

    first = run_validate(review_report, pack_root, output_dir)

    assert first.returncode == 0
    assert (output_dir / ".specdock-issue-candidates-validation").exists()

    (output_dir / "old.txt").write_text("old", encoding="utf-8")
    second = run_validate(review_report, pack_root, output_dir)

    assert second.returncode == 0
    assert not (output_dir / "old.txt").exists()

    unowned = tmp_path / "unowned"
    unowned.mkdir()
    (unowned / "user.txt").write_text("keep", encoding="utf-8")
    blocked = run_validate(review_report, pack_root, unowned)

    assert blocked.returncode == 2
    assert (unowned / "user.txt").read_text(encoding="utf-8") == "keep"
    assert not (unowned / "issue-candidate-validation-report.json").exists()

    unsafe_output = tmp_path / "token raw transcript validation"
    unsafe = run_validate(review_report, pack_root, unsafe_output)

    assert unsafe.returncode == 2
    assert not (unsafe_output / "issue-candidate-validation-report.json").exists()
    assert_no_leak(unsafe, unsafe_output, "token raw transcript")


def test_forbidden_authority_claim_in_markdown_is_rejected_without_echo(tmp_path) -> None:
    unsafe_claim = "spec-reviewer passed"
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidates=[
            {
                "candidate_id": "issue-candidate-001",
                "draft_text": f"This candidate says {unsafe_claim}.",
            }
        ],
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)

    result = run_validate(review_report, pack_root, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/issue-candidate-validation-report.json")
    assert report["status"] == "rejected"
    assert_no_leak(result, tmp_path / "validation", unsafe_claim)
