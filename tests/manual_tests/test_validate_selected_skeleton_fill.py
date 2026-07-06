import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/authoring-pack/validate_selected_skeleton_fill.py"

TEMPLATE_SHA = "a" * 64
SKELETON_SHA = "b" * 64
INVENTORY_SHA = "c" * 64


def run_validate(
    review_report: Path,
    pack_tree: Path,
    assurance: Path,
    selected_skeleton: Path,
    output_dir: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--review-report",
            str(review_report),
            "--pack-tree",
            str(pack_tree),
            "--assurance",
            str(assurance),
            "--selected-skeleton",
            str(selected_skeleton),
            "--output-dir",
            str(output_dir),
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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pack_digest(pack_root: Path) -> dict:
    files: dict[str, str] = {}
    for path in sorted(pack_root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(pack_root).as_posix()
        files[f"specdock-authoring-pack/{relative}"] = path.read_text(encoding="utf-8")
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files[path].encode("utf-8"))
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
        "generated_at": "2026-07-06T00:00:00Z",
        "input_kind": "tree",
        "trace": {
            "issue_id": "iss-00287",
            "parent_epic": "epic-00283",
        },
        "sources": [],
    }
    if status == "pass":
        payload["pack_digest"] = pack_digest(pack_root)
    return write_json(path, payload)


def write_assurance(path: Path, *, profile: str = "standard") -> Path:
    return write_json(
        path,
        {
            "status": "provisional",
            "classification": {
                "authorized_profile": profile,
            },
        },
    )


def write_canonical_docs(root: Path) -> list[Path]:
    docs = []
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        path = root / name
        path.write_text(f"# {name}\n\ncanonical content\n", encoding="utf-8")
        docs.append(path)
    return docs


def write_selected_skeleton(path: Path, *, profile: str = "standard", **overrides: object) -> Path:
    payload = {
        "authority": "local_assurance",
        "issue_id": "iss-00287",
        "authorized_profile": profile,
        "template_sha256": TEMPLATE_SHA,
        "skeleton_sha256": SKELETON_SHA,
        "section_inventory_sha256": INVENTORY_SHA,
        "section_inventory": [
            {
                "section_id": "purpose",
                "heading": "## Purpose",
                "required": True,
                "fillable": True,
                "order": 10,
            },
            {
                "section_id": "notes",
                "heading": "## Notes",
                "required": False,
                "fillable": True,
                "order": 20,
            },
        ],
        "allowed_section_ids": ["purpose", "notes"],
        "required_section_ids": ["purpose"],
    }
    payload.update(overrides)
    return write_json(path, payload)


def candidate_payload(**overrides: object) -> dict:
    body = "選択済みスケルトンに沿った候補本文です。"
    payload = {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "schema_version": "1",
        "issue_id": "iss-00287",
        "target": {
            "profile": "standard",
            "template_sha256": TEMPLATE_SHA,
            "skeleton_sha256": SKELETON_SHA,
            "section_inventory_sha256": INVENTORY_SHA,
        },
        "profile_suggestion": {
            "profile": "strict",
            "advisory_only": True,
            "rationale": "safety-sensitive validator",
        },
        "section_fills": [
            {
                "section_id": "purpose",
                "body": body,
                "body_sha256": sha256_text(body),
            }
        ],
    }
    payload.update(overrides)
    return payload


def write_pack_tree(root: Path, payload: dict | None = None) -> Path:
    pack_root = root / "specdock-authoring-pack"
    write_json(pack_root / "selected-skeleton-fill/section-fills.json", payload or candidate_payload())
    return pack_root


def assert_no_leak(result: subprocess.CompletedProcess[str], output_dir: Path, *payloads: str) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    report_path = output_dir / "selected-skeleton-fill-validation-report.json"
    summary_path = output_dir / "selected-skeleton-fill-validation-summary.md"
    if report_path.exists():
        combined += "\n" + report_path.read_text(encoding="utf-8")
    if summary_path.exists():
        combined += "\n" + summary_path.read_text(encoding="utf-8")
    for payload in payloads:
        assert payload not in combined
    assert "/Users/" not in combined
    assert "/home/" not in combined
    assert "/Volumes/" not in combined
    assert "/private/" not in combined


def test_valid_fill_passes_with_advisory_profile_suggestion_and_no_mutation(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")
    assurance_before = assurance.read_bytes()
    skeleton_before = selected_skeleton.read_bytes()
    canonical_docs = write_canonical_docs(tmp_path / "issue")
    canonical_before = {path: path.read_bytes() for path in canonical_docs}
    output_dir = tmp_path / "validation"

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, output_dir)

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "selected-skeleton-fill-validation-report.json")
    assert report["status"] == "pass"
    assert report["authority"] == "evidence_only"
    assert report["adoption_status"] == "unreviewed"
    assert report["profile_validation"]["local_authorized_profile"] == "standard"
    assert report["profile_validation"]["profile_suggestion_used_for_authority"] is False
    assert report["candidate"]["profile_suggestion"]["profile"] == "strict"
    assert "profile_suggestion differs" in " ".join(report["warnings"])
    assert report["section_inventory_validation"]["eligible_section_ids"] == ["purpose"]
    assert report["section_inventory_validation"]["missing_optional_section_ids"] == ["notes"]
    assert report["adoption"]["overall_adoption_eligible"] is True
    assert report["adoption"]["canonical_written"] is False
    assert report["adoption"]["assurance_mutated"] is False
    assert assurance.read_bytes() == assurance_before
    assert selected_skeleton.read_bytes() == skeleton_before
    for path, before in canonical_before.items():
        assert path.read_bytes() == before


@pytest.mark.parametrize(
    ("target_update", "expected_error"),
    [
        ({"profile": "strict"}, "candidate target.profile does not match local authorized_profile"),
        ({"template_sha256": "d" * 64}, "candidate target.template_sha256 does not match selected skeleton"),
        ({"skeleton_sha256": "e" * 64}, "candidate target.skeleton_sha256 does not match selected skeleton"),
        (
            {"section_inventory_sha256": "f" * 64},
            "candidate target.section_inventory_sha256 does not match selected skeleton",
        ),
    ],
)
def test_target_profile_or_hash_mismatch_is_stale(
    tmp_path,
    target_update: dict,
    expected_error: str,
) -> None:
    payload = candidate_payload()
    payload["target"].update(target_update)
    pack_root = write_pack_tree(tmp_path / "pack", payload)
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 3
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "stale"
    assert expected_error in report["errors"]
    assert report["adoption"]["overall_adoption_eligible"] is False


def test_candidate_issue_id_mismatch_is_stale(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack", candidate_payload(issue_id="iss-99999"))
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 3
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "stale"
    assert "candidate issue_id does not match selected skeleton issue_id" in report["errors"]


def test_selected_skeleton_profile_drift_is_stale(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json", profile="standard")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json", profile="strict")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 3
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "stale"
    assert "selected skeleton authorized_profile does not match assurance authorized_profile" in report["errors"]


def test_allowed_section_ids_must_be_subset_of_inventory(tmp_path) -> None:
    pack_root = write_pack_tree(
        tmp_path / "pack",
        candidate_payload(
            section_fills=[
                {"section_id": "purpose", "body": "ok"},
                {"section_id": "bogus", "body": "should not become eligible"},
            ]
        ),
    )
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(
        tmp_path / "selected-skeleton.json",
        allowed_section_ids=["purpose", "bogus"],
    )

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 1
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "fail"
    assert "selected-skeleton.allowed_section_ids must be a subset of section_inventory" in report["errors"]


def test_extra_section_is_rejected(tmp_path) -> None:
    payload = candidate_payload(
        section_fills=[
            {"section_id": "purpose", "body": "ok"},
            {"section_id": "outside", "body": "not allowed"},
        ]
    )
    pack_root = write_pack_tree(tmp_path / "pack", payload)
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "rejected"
    assert report["section_inventory_validation"]["extra_section_ids"] == ["outside"]


def test_missing_required_section_fails(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack", candidate_payload(section_fills=[]))
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 1
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "fail"
    assert report["section_inventory_validation"]["missing_section_ids"] == ["purpose"]


@pytest.mark.parametrize(
    "claim",
    [
        "spec-reviewer passed",
        "adoption_status: adopted",
        ".assurance.json updated",
        "canonical overwrite",
    ],
)
def test_unsafe_authority_claim_in_section_body_is_rejected(tmp_path, claim: str) -> None:
    payload = candidate_payload(
        section_fills=[
            {
                "section_id": "purpose",
                "body": f"This says {claim}.",
            }
        ]
    )
    pack_root = write_pack_tree(tmp_path / "pack", payload)
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "rejected"
    assert report["section_results"][0]["unsafe_claim_detected"] is True


def test_candidate_authorized_profile_field_is_rejected(tmp_path) -> None:
    payload = candidate_payload(authorized_profile="strict")
    pack_root = write_pack_tree(tmp_path / "pack", payload)
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "rejected"


def test_unsafe_authority_claim_in_candidate_metadata_is_rejected(tmp_path) -> None:
    payload = candidate_payload(
        profile_suggestion={
            "profile": "standard",
            "advisory_only": True,
            "rationale": "spec-reviewer passed",
        }
    )
    pack_root = write_pack_tree(tmp_path / "pack", payload)
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "rejected"
    assert "candidate fill metadata contains unsafe authority claim" in report["errors"]


def test_non_pass_review_input_does_not_validate(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root, status="rejected")
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(
        review_report, tmp_path / "missing-pack", assurance, selected_skeleton, tmp_path / "validation"
    )

    assert result.returncode == 4
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "rejected"
    assert report["adoption"]["overall_adoption_eligible"] is False
    assert "review report status is not pass: rejected" in report["errors"]
    assert "pack tree could not be observed" not in report["errors"]


def test_pack_digest_mismatch_is_stale(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    write_json(pack_root / "selected-skeleton-fill/section-fills.json", candidate_payload(section_fills=[]))
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")

    result = run_validate(review_report, pack_root, assurance, selected_skeleton, tmp_path / "validation")

    assert result.returncode == 3
    report = read_json(tmp_path / "validation/selected-skeleton-fill-validation-report.json")
    assert report["status"] == "stale"


def test_output_directory_ownership_guard_and_redaction(tmp_path) -> None:
    pack_root = write_pack_tree(tmp_path / "pack")
    review_report = write_review_report(tmp_path / "review.json", pack_root)
    assurance = write_assurance(tmp_path / "issue/.assurance.json")
    selected_skeleton = write_selected_skeleton(tmp_path / "selected-skeleton.json")
    output_dir = tmp_path / "validation"

    first = run_validate(review_report, pack_root, assurance, selected_skeleton, output_dir)

    assert first.returncode == 0
    assert (output_dir / ".specdock-selected-skeleton-fill-validation").exists()

    (output_dir / "old.txt").write_text("old", encoding="utf-8")
    second = run_validate(review_report, pack_root, assurance, selected_skeleton, output_dir)

    assert second.returncode == 0
    assert not (output_dir / "old.txt").exists()

    unowned = tmp_path / "unowned"
    unowned.mkdir()
    (unowned / "user.txt").write_text("keep", encoding="utf-8")
    blocked = run_validate(review_report, pack_root, assurance, selected_skeleton, unowned)

    assert blocked.returncode == 2
    assert (unowned / "user.txt").read_text(encoding="utf-8") == "keep"
    assert not (unowned / "selected-skeleton-fill-validation-report.json").exists()

    unsafe_output = tmp_path / "token raw transcript validation"
    unsafe = run_validate(review_report, pack_root, assurance, selected_skeleton, unsafe_output)

    assert unsafe.returncode == 2
    assert not (unsafe_output / "selected-skeleton-fill-validation-report.json").exists()
    assert_no_leak(unsafe, unsafe_output, "token raw transcript")
