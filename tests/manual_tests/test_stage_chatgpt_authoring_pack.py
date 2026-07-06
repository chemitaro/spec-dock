import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/authoring-pack/stage_chatgpt_authoring_pack.py"
REVIEW_SCRIPT = REPO_ROOT / "scripts/authoring-pack/review_chatgpt_authoring_pack.py"
FIXTURE_SOURCE = "scripts/authoring-pack/README.md"


def run_stage(
    review_report: Path, pack_tree: Path, issue_dir: Path, output_dir: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--review-report",
            str(review_report),
            "--pack-tree",
            str(pack_tree),
            "--issue-dir",
            str(issue_dir),
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight_data(*, source_sha: str | None = None) -> dict:
    source_sha = source_sha or sha256(REPO_ROOT / FIXTURE_SOURCE)
    return {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "status": "pass",
        "repository": {
            "full_name": "chemitaro/spec-dock",
            "requested_ref": "iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering",
            "observed_ref": "iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering",
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
    path.write_text(json.dumps(preflight_data()), encoding="utf-8")
    return path


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


def write_pass_review_report(tmp_path: Path, pack_tree: Path) -> Path:
    review_dir = tmp_path / "review"
    result = run_review(pack_tree, write_preflight(tmp_path / "preflight.json"), review_dir)
    assert result.returncode == 0, result.stderr
    report_path = review_dir / "validation-report.json"
    report = read_json(report_path)
    assert report["status"] == "pass"
    assert report["pack_digest"]["content_sha256"]
    return report_path


def write_review_report(path: Path, *, status: str = "pass") -> Path:
    payload = {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "status": status,
        "generated_at": "2026-07-06T00:00:00Z",
        "input_kind": "zip",
        "trace": {
            "issue_id": "iss-00285",
            "parent_epic": "epic-00283",
            "requirements": ["E-RQ-004", "E-RQ-005"],
            "acceptance": ["E-AC-002", "E-AC-003", "E-AC-004"],
        },
        "sources": [],
    }
    if status == "pass":
        payload["pack_digest"] = {
            "algorithm": "sha256",
            "content_sha256": "0" * 64,
            "file_count": 1,
        }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def write_issue_dir(root: Path) -> Path:
    issue_dir = root / "issue"
    issue_dir.mkdir()
    (issue_dir / "requirement.md").write_text("# Requirement\n\nold requirement\n", encoding="utf-8")
    (issue_dir / "design.md").write_text("# Design\n\nold design\n", encoding="utf-8")
    (issue_dir / "plan.md").write_text("# Plan\n\nold plan\n", encoding="utf-8")
    (issue_dir / ".assurance.json").write_text('{"authorized_profile":"standard"}\n', encoding="utf-8")
    return issue_dir


def stage_item(source_path: str, target_path: str, **extra: object) -> dict:
    item = {
        "source_path": source_path,
        "target_path": target_path,
        "adoption_status": "unreviewed",
        "required_local_validation": ["local-diff-review", "canonical-rewrite", "fresh-spec-reviewer"],
        "rationale": "manual local review required",
    }
    item.update(extra)
    return item


def write_pack_tree(root: Path, *, items: list[dict], candidates: dict[str, str]) -> Path:
    pack_root = root / "specdock-authoring-pack"
    (pack_root / "adoption").mkdir(parents=True)
    source_manifest = {
        "sources": [
            {
                "path": FIXTURE_SOURCE,
                "sha256": sha256(REPO_ROOT / FIXTURE_SOURCE),
                "role": "readme",
            }
        ]
    }
    (pack_root / "manifest.json").write_text(
        json.dumps({
            "authority": "evidence_only",
            "adoption_status": "unreviewed",
            "bundle_generation_not_promotion": True,
            "pack_id": "pack-iss-00286",
            "expected_zip_root": "specdock-authoring-pack/",
            "schema_version": "1",
        }),
        encoding="utf-8",
    )
    (pack_root / "provenance.json").write_text(
        json.dumps({
            "authority": "evidence_only",
            "repository": {
                "full_name": "chemitaro/spec-dock",
                "requested_ref": "iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering",
            },
            "source": "chatgpt_zip_authoring_pack",
        }),
        encoding="utf-8",
    )
    (pack_root / "source-manifest.json").write_text(json.dumps(source_manifest), encoding="utf-8")
    (pack_root / "stale-if.json").write_text(
        json.dumps({
            "stale_if": [
                {
                    "kind": "source_hash_changed",
                    "source_paths": [FIXTURE_SOURCE],
                }
            ]
        }),
        encoding="utf-8",
    )
    (pack_root / "adoption/adoption-map.json").write_text(json.dumps({"items": items}), encoding="utf-8")
    for relative_path, text in candidates.items():
        path = pack_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return pack_root


def assert_no_stage_outputs(output_dir: Path) -> None:
    assert not (output_dir / "staged-artifacts").exists()
    assert not (output_dir / "dry-run-diff.json").exists()
    assert not (output_dir / "dry-run-diff.md").exists()
    assert not (output_dir / "adoption/eal-candidates.json").exists()


def assert_no_leak(result: subprocess.CompletedProcess[str], output_dir: Path, *payloads: str) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    for path in (output_dir / "staging-report.json", output_dir / "staging-summary.md"):
        if path.exists():
            combined += "\n" + path.read_text(encoding="utf-8")
    for payload in payloads:
        assert payload not in combined
    assert "/Users/" not in combined
    assert "/home/" not in combined
    assert "/Volumes/" not in combined
    assert "/private/" not in combined


def test_valid_pass_review_creates_stage_and_diff_without_canonical_overwrite(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    requirement_before = (issue_dir / "requirement.md").read_bytes()
    assurance_before = (issue_dir / ".assurance.json").read_bytes()
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/a/b/requirement.md", "requirement.md")],
        candidates={"drafts/a/b/requirement.md": "# Requirement\n\nnew requirement\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "staging-report.json")
    assert report["status"] == "pass"
    assert report["authority"] == "evidence_only"
    assert report["adoption_status"] == "unreviewed"
    assert report["bundle_generation_not_promotion"] is True
    assert report["trace"]["issue_id"] == "iss-00286"
    assert report["trace"]["requirements"] == ["E-RQ-006", "E-RQ-007"]
    assert report["trace"]["acceptance"] == ["E-AC-008", "E-AC-009"]
    assert report["items"][0]["target_path"] == "requirement.md"
    assert report["items"][0]["staged_artifact_path"] == "staged-artifacts/item-0001.md"
    assert (output_dir / "staged-artifacts/item-0001.md").read_text(encoding="utf-8").endswith("new requirement\n")
    assert (output_dir / "diffs/item-0001.diff").exists()
    assert read_json(output_dir / "dry-run-diff.json")["diffs"][0]["canonical_written"] is False
    assert (issue_dir / "requirement.md").read_bytes() == requirement_before
    assert (issue_dir / ".assurance.json").read_bytes() == assurance_before
    assert not (output_dir / "staged-artifacts/drafts/a/b/requirement.md").exists()


def test_pack_tree_digest_mismatch_is_stale_and_does_not_stage(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.md", "requirement.md")],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    (pack_tree / "drafts/requirement.md").write_text("# Requirement\n\nchanged after review\n", encoding="utf-8")
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 3
    assert read_json(output_dir / "staging-report.json")["status"] == "stale"
    assert_no_stage_outputs(output_dir)


def test_adoption_map_becomes_unreviewed_eal_candidates(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[
            stage_item("drafts/requirement.md", "requirement.md"),
            stage_item("drafts/design.md", "design.md"),
        ],
        candidates={
            "drafts/requirement.md": "# Requirement\n\nnew\n",
            "drafts/design.md": "# Design\n\nnew\n",
        },
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 0, result.stderr
    candidates = read_json(output_dir / "adoption/eal-candidates.json")
    assert candidates["status"] == "pass"
    assert [row["adoption_status"] for row in candidates["rows"]] == ["unreviewed", "unreviewed"]
    assert candidates["rows"][0]["candidate_id"] == "EAL-CAND-0001"
    assert candidates["rows"][0]["staged_artifact"] == "staged-artifacts/item-0001.md"
    assert candidates["rows"][0]["dry_run_diff"] == "diffs/item-0001.diff"
    assert "fresh-spec-reviewer" in candidates["rows"][0]["required_local_validation"]
    assert "adopted" not in json.dumps(candidates["rows"], ensure_ascii=False)


@pytest.mark.parametrize(
    ("item_update", "raw_payload"),
    [
        ({"target_path": "../requirement.md"}, "../requirement.md"),
        ({"target_path": "/tmp/requirement.md"}, "/tmp/requirement.md"),
        ({"target_path": ".assurance.json"}, ".assurance.json"),
        ({"target_path": "config/token.md"}, "config/token.md"),
        ({"target_path": "report.md"}, "report.md"),
        ({"write_mode": "direct"}, "direct"),
    ],
)
def test_unsafe_target_or_direct_write_is_rejected(
    tmp_path,
    item_update: dict[str, object],
    raw_payload: str,
) -> None:
    issue_dir = write_issue_dir(tmp_path)
    item = stage_item("drafts/requirement.md", "requirement.md")
    item.update(item_update)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[item],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 4
    assert read_json(output_dir / "staging-report.json")["status"] == "rejected"
    assert_no_stage_outputs(output_dir)
    assert_no_leak(result, output_dir, raw_payload)


@pytest.mark.parametrize(
    ("item_update", "expected_status", "expected_code"),
    [
        ({"adoption_status": "adopted"}, "rejected", 4),
        ({"authority": "canonical"}, "rejected", 4),
        ({"rationale": "reviewer pass"}, "rejected", 4),
    ],
)
def test_review_rejected_authority_claims_do_not_stage(
    tmp_path,
    item_update: dict[str, object],
    expected_status: str,
    expected_code: int,
) -> None:
    issue_dir = write_issue_dir(tmp_path)
    item = stage_item("drafts/requirement.md", "requirement.md")
    item.update(item_update)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[item],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_dir = tmp_path / "review"
    review_result = run_review(pack_tree, write_preflight(tmp_path / "preflight.json"), review_dir)
    assert review_result.returncode == expected_code
    review_report = review_dir / "validation-report.json"
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == expected_code
    assert read_json(output_dir / "staging-report.json")["status"] == expected_status
    assert_no_stage_outputs(output_dir)


@pytest.mark.parametrize(
    ("status", "code"),
    [
        ("fail", 1),
        ("blocked", 2),
        ("stale", 3),
        ("rejected", 4),
        ("deferred", 5),
    ],
)
def test_non_pass_review_input_does_not_stage(tmp_path, status: str, code: int) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.md", "requirement.md")],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_report = write_review_report(tmp_path / "validation-report.json", status=status)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == code
    assert read_json(output_dir / "staging-report.json")["status"] == status
    assert_no_stage_outputs(output_dir)


def test_diagnostics_redact_unsafe_paths_secrets_and_raw_transcripts(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    leaked_payload = "/Users/example/token raw transcript"
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.md", "requirement.md")],
        candidates={"drafts/requirement.md": f"# Requirement\n\n{leaked_payload}\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 4
    assert read_json(output_dir / "staging-report.json")["status"] == "rejected"
    assert_no_stage_outputs(output_dir)
    assert_no_leak(result, output_dir, leaked_payload, "/Users/example/token", "raw transcript")


def test_unsafe_output_directory_is_blocked_without_staging_or_leak(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.md", "requirement.md")],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    unsafe_output = tmp_path / "token raw transcript stage"

    result = run_stage(review_report, pack_tree, issue_dir, unsafe_output)

    assert result.returncode == 2
    assert_no_stage_outputs(unsafe_output)
    assert not (unsafe_output / "staging-report.json").exists()
    assert_no_leak(result, unsafe_output, "token raw transcript")


def test_non_markdown_source_is_rejected_without_staging(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.txt", "requirement.md")],
        candidates={"drafts/requirement.txt": "# Requirement\n\nnew\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    result = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert result.returncode == 4
    assert read_json(output_dir / "staging-report.json")["status"] == "rejected"
    assert_no_stage_outputs(output_dir)


def test_output_directory_ownership_and_cleanup_remains_safe(tmp_path) -> None:
    issue_dir = write_issue_dir(tmp_path)
    pack_tree = write_pack_tree(
        tmp_path / "pack",
        items=[stage_item("drafts/requirement.md", "requirement.md")],
        candidates={"drafts/requirement.md": "# Requirement\n\nnew\n"},
    )
    review_report = write_pass_review_report(tmp_path, pack_tree)
    output_dir = tmp_path / "stage"

    first = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert first.returncode == 0, first.stderr
    assert (output_dir / ".specdock-authoring-pack-stage").exists()

    (output_dir / "stale.txt").write_text("old", encoding="utf-8")
    (output_dir / "old-dir").mkdir()
    (output_dir / "old-dir/old.txt").write_text("old", encoding="utf-8")
    second = run_stage(review_report, pack_tree, issue_dir, output_dir)

    assert second.returncode == 0, second.stderr
    assert not (output_dir / "stale.txt").exists()
    assert not (output_dir / "old-dir").exists()

    unowned = tmp_path / "unowned"
    unowned.mkdir()
    (unowned / "user.txt").write_text("keep", encoding="utf-8")
    blocked = run_stage(review_report, pack_tree, issue_dir, unowned)

    assert blocked.returncode == 2
    assert (unowned / "user.txt").read_text(encoding="utf-8") == "keep"
    assert not (unowned / "staging-report.json").exists()

    fake_owned = tmp_path / "fake-owned"
    fake_owned.mkdir()
    (fake_owned / ".specdock-authoring-pack-stage").write_text("owned-by=someone-else\n", encoding="utf-8")
    (fake_owned / "user.txt").write_text("keep", encoding="utf-8")
    blocked_fake = run_stage(review_report, pack_tree, issue_dir, fake_owned)

    assert blocked_fake.returncode == 2
    assert (fake_owned / "user.txt").read_text(encoding="utf-8") == "keep"
