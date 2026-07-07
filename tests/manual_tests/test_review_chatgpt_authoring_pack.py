from collections.abc import Mapping
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/authoring-pack/review_chatgpt_authoring_pack.py"
FIXTURE_SOURCE = "scripts/authoring-pack/README.md"
ISSUE_DIR = (
    REPO_ROOT / "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/"
    "epic-00283-chatgpt-zip-authoring-pack-automation/issues/"
    "iss-00285-implement-safe-authoring-pack-review-and-schema-validation"
)
MODULE_SPEC = importlib.util.spec_from_file_location(
    "authoring_pack_review",
    REPO_ROOT / "scripts/authoring-pack/authoring_pack_review.py",
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
REVIEW_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(REVIEW_MODULE)


def run_review(input_path: Path, preflight: Path, output_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(input_path),
            "--preflight",
            str(preflight),
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight_data(*, source_sha: str | None = None, status: str = "pass") -> dict:
    source_sha = source_sha or sha256(REPO_ROOT / FIXTURE_SOURCE)
    return {
        "authority": "evidence_only",
        "adoption_status": "unreviewed",
        "bundle_generation_not_promotion": True,
        "status": status,
        "repository": {
            "full_name": "chemitaro/spec-dock",
            "requested_ref": "iss-00285-implement-safe-authoring-pack-review-and-schema-validation",
            "observed_ref": "iss-00285-implement-safe-authoring-pack-review-and-schema-validation",
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


def write_preflight(tmp_path: Path, data: dict | None = None) -> Path:
    path = tmp_path / "preflight.json"
    path.write_text(json.dumps(data or preflight_data()), encoding="utf-8")
    return path


def pack_files(*, source_sha: str | None = None, readme: str = "draft evidence\n") -> dict[str, str | bytes]:
    source_sha = source_sha or sha256(REPO_ROOT / FIXTURE_SOURCE)
    source_manifest = {
        "sources": [
            {
                "path": FIXTURE_SOURCE,
                "sha256": source_sha,
                "role": "readme",
            }
        ]
    }
    return {
        "specdock-authoring-pack/manifest.json": json.dumps({
            "authority": "evidence_only",
            "adoption_status": "unreviewed",
            "bundle_generation_not_promotion": True,
            "pack_id": "pack-iss-00285",
            "expected_zip_root": "specdock-authoring-pack/",
            "schema_version": "1",
        }),
        "specdock-authoring-pack/provenance.json": json.dumps({
            "authority": "evidence_only",
            "repository": {
                "full_name": "chemitaro/spec-dock",
                "requested_ref": "iss-00285-implement-safe-authoring-pack-review-and-schema-validation",
            },
            "source": "chatgpt_zip_authoring_pack",
        }),
        "specdock-authoring-pack/source-manifest.json": json.dumps(source_manifest),
        "specdock-authoring-pack/stale-if.json": json.dumps({
            "stale_if": [
                {
                    "kind": "source_hash_changed",
                    "source_paths": [FIXTURE_SOURCE],
                }
            ]
        }),
        "specdock-authoring-pack/adoption/adoption-map.json": json.dumps({
            "items": [
                {
                    "source_path": "README.md",
                    "target": "evidence-only",
                    "adoption_status": "unreviewed",
                    "required_local_validation": ["spec-reviewer"],
                }
            ]
        }),
        "specdock-authoring-pack/README.md": readme,
    }


def write_zip(path: Path, files: Mapping[str, str | bytes], *, modes: Mapping[str, int] | None = None) -> Path:
    modes = modes or {}
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in files.items():
            info = zipfile.ZipInfo(name)
            if name in modes:
                info.external_attr = modes[name] << 16
            data = payload if isinstance(payload, bytes) else payload.encode("utf-8")
            archive.writestr(info, data)
    return path


def mark_first_zip_entry_encrypted(path: Path) -> None:
    data = bytearray(path.read_bytes())
    local_header = data.find(b"PK\x03\x04")
    central_header = data.find(b"PK\x01\x02")
    assert local_header >= 0
    assert central_header >= 0
    data[local_header + 6] |= 0x01
    data[central_header + 8] |= 0x01
    path.write_bytes(data)


def write_tree(root: Path, files: Mapping[str, str | bytes]) -> Path:
    for name, payload in files.items():
        relative = name.removeprefix("specdock-authoring-pack/")
        path = root / "specdock-authoring-pack" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, bytes):
            path.write_bytes(payload)
        else:
            path.write_text(payload, encoding="utf-8")
    return root / "specdock-authoring-pack"


def assert_no_leak(result: subprocess.CompletedProcess[str], *payloads: str) -> None:
    combined = f"{result.stdout}\n{result.stderr}"
    for payload in payloads:
        assert payload not in combined
    assert "/Users/" not in combined
    assert "/home/" not in combined
    assert "/Volumes/" not in combined
    assert "/private/" not in combined


def test_valid_zip_generates_pass_report(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    output_dir = tmp_path / "review"

    result = run_review(zip_path, preflight, output_dir)

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "validation-report.json")
    assert report["status"] == "pass"
    assert report["authority"] == "evidence_only"
    assert report["adoption_status"] == "unreviewed"
    assert report["bundle_generation_not_promotion"] is True
    assert report["trace"]["issue_id"] == "iss-00285"
    assert report["trace"]["parent_epic"] == "epic-00283"
    assert report["trace"]["requirements"] == ["E-RQ-004", "E-RQ-005"]
    assert report["trace"]["acceptance"] == ["E-AC-002", "E-AC-003", "E-AC-004"]
    assert report["preflight"]["status"] == "pass"
    assert report["preflight"]["source_count"] == 1
    assert (output_dir / "validation-summary.md").exists()


def test_preflight_trace_drives_review_report_trace(tmp_path) -> None:
    data = preflight_data()
    data["trace"] = {
        "issue_id": "iss-00289",
        "parent_epic": "epic-00283",
        "requirements": ["E-RQ-008", "E-RQ-009", "E-RQ-010"],
        "acceptance": ["E-AC-005", "E-AC-006", "E-AC-010", "E-AC-011"],
    }
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    output_dir = tmp_path / "review"

    result = run_review(zip_path, preflight, output_dir)

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "validation-report.json")
    assert report["trace"] == data["trace"]
    assert report["preflight"]["trace"] == data["trace"]


@pytest.mark.parametrize(
    ("trace", "expected_error", "unsafe_payload"),
    [
        ("not-an-object", "preflight trace must be an object when present", None),
        (
            {"issue_id": "iss-00289", "parent_epic": "epic-00283", "requirements": "E-RQ-008", "acceptance": []},
            "preflight trace.requirements must be a string array when trace is present",
            None,
        ),
        (
            {
                "issue_id": "iss-00289",
                "parent_epic": "epic-00283",
                "requirements": ["spec-reviewer passed"],
                "acceptance": ["E-AC-005"],
            },
            "preflight trace contains unsafe text",
            "spec-reviewer passed",
        ),
        (
            {
                "issue_id": "iss-00289",
                "parent_epic": "epic-00283",
                "requirements": ["raw transcript: browser transcript"],
                "acceptance": ["E-AC-005"],
            },
            "preflight trace contains unsafe text",
            "raw transcript",
        ),
        (
            {
                "issue_id": "iss-00289",
                "parent_epic": "epic-00283",
                "requirements": ["/Users/example/project"],
                "acceptance": ["E-AC-005"],
            },
            "preflight trace contains unsafe text",
            "/Users/example/project",
        ),
    ],
)
def test_preflight_trace_invalid_inputs_fail_closed(
    tmp_path,
    trace: object,
    expected_error: str,
    unsafe_payload: str | None,
) -> None:
    data = preflight_data()
    data["trace"] = trace
    if unsafe_payload is not None:
        data["safe_output_constraints"]["forbidden_claims"] = []
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    output_dir = tmp_path / "review"

    result = run_review(zip_path, preflight, output_dir)

    assert result.returncode == 1
    report = read_json(output_dir / "validation-report.json")
    assert report["status"] == "fail"
    assert expected_error in report["errors"]
    if unsafe_payload is not None:
        assert_no_leak(result, unsafe_payload)
        assert unsafe_payload not in (output_dir / "validation-report.json").read_text(encoding="utf-8")


def test_valid_tree_generates_pass_report_with_tree_mode_note(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    tree = write_tree(tmp_path / "tree", pack_files())
    output_dir = tmp_path / "tree-review"

    result = run_review(tree, preflight, output_dir, "--input-kind", "tree")

    assert result.returncode == 0, result.stderr
    report = read_json(output_dir / "validation-report.json")
    assert report["status"] == "pass"
    assert "tree input does not provide ZIP central directory safety evidence" in report["deferred"]


def test_zip_path_traversal_is_rejected_before_extraction(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["../evil.md"] = "evil"
    zip_path = write_zip(tmp_path / "traversal.zip", files)
    output_dir = tmp_path / "review"
    extract_dir = tmp_path / "extract"

    result = run_review(zip_path, preflight, output_dir, "--extract-dir", str(extract_dir))

    assert result.returncode == 4
    report = read_json(output_dir / "validation-report.json")
    assert report["status"] == "rejected"
    assert not (extract_dir / "evil.md").exists()
    assert "../evil.md" not in (output_dir / "validation-report.json").read_text(encoding="utf-8")


def test_zip_absolute_path_is_rejected_without_echoing_path(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    unsafe_path = "/tmp/leak.md"
    files[unsafe_path] = "evil"
    zip_path = write_zip(tmp_path / "absolute.zip", files)
    output_dir = tmp_path / "review"

    result = run_review(zip_path, preflight, output_dir)

    assert result.returncode == 4
    assert_no_leak(result, unsafe_path)
    payload = (output_dir / "validation-report.json").read_text(encoding="utf-8")
    assert unsafe_path not in payload


def test_zip_hidden_path_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/.assurance.json"] = "{}"
    zip_path = write_zip(tmp_path / "hidden.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    payload = (tmp_path / "review/validation-report.json").read_text(encoding="utf-8")
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"
    assert ".assurance.json" not in payload


def test_zip_wrong_root_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    wrong_root_files = {
        name.replace("specdock-authoring-pack/", "wrong-root/", 1): payload for name, payload in pack_files().items()
    }
    zip_path = write_zip(tmp_path / "wrong-root.zip", wrong_root_files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_symlink_entry_is_rejected_before_extraction(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    link_name = "specdock-authoring-pack/drafts/link.md"
    files[link_name] = "target"
    zip_path = write_zip(tmp_path / "symlink.zip", files, modes={link_name: stat.S_IFLNK | 0o777})

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_device_like_entry_is_rejected_before_extraction(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    device_name = "specdock-authoring-pack/drafts/device.md"
    files[device_name] = "unsafe"
    zip_path = write_zip(tmp_path / "device.zip", files, modes={device_name: stat.S_IFCHR | 0o666})

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_executable_regular_file_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    executable_name = "specdock-authoring-pack/drafts/run.md"
    files[executable_name] = "unsafe"
    zip_path = write_zip(tmp_path / "executable.zip", files, modes={executable_name: stat.S_IFREG | 0o755})

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_encrypted_entry_is_rejected_before_payload_read(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "encrypted.zip", pack_files())
    mark_first_zip_entry_encrypted(zip_path)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "rejected"
    assert "encrypted zip entry rejected" in report["errors"]


def test_zip_nested_archive_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/drafts/nested.zip"] = b"PK\x03\x04"
    zip_path = write_zip(tmp_path / "nested.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_binary_file_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/drafts/binary.md"] = b"\x00\x01"
    zip_path = write_zip(tmp_path / "binary.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_zip_invalid_utf8_without_nul_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/drafts/invalid-utf8.md"] = b"\xff\xfe"
    zip_path = write_zip(tmp_path / "invalid-utf8.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_tree_unsafe_entry_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    tree = write_tree(tmp_path / "tree", pack_files())
    (tree / ".hidden.md").write_text("unsafe", encoding="utf-8")
    (tree / "drafts").mkdir(exist_ok=True)
    (tree / "drafts/link.md").symlink_to("../README.md")
    (tree / "drafts/nested.zip").write_bytes(b"PK\x03\x04")
    (tree / "drafts/invalid-utf8.md").write_bytes(b"\xff\xfe")

    result = run_review(tree, preflight, tmp_path / "review", "--input-kind", "tree")

    assert result.returncode == 4
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "rejected"


def test_tree_executable_regular_file_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    tree = write_tree(tmp_path / "tree", pack_files())
    executable = tree / "README.md"
    executable.chmod(0o755)

    result = run_review(tree, preflight, tmp_path / "review", "--input-kind", "tree")

    assert result.returncode == 4
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "rejected"


@pytest.mark.parametrize(
    "missing_file",
    [
        "specdock-authoring-pack/manifest.json",
        "specdock-authoring-pack/provenance.json",
        "specdock-authoring-pack/source-manifest.json",
        "specdock-authoring-pack/stale-if.json",
        "specdock-authoring-pack/adoption/adoption-map.json",
    ],
)
def test_missing_mandatory_metadata_fails_closed(tmp_path, missing_file: str) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    del files[missing_file]
    zip_path = write_zip(tmp_path / "missing-metadata.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "fail"


def test_source_hash_mismatch_is_stale(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files(source_sha="0" * 64)
    zip_path = write_zip(tmp_path / "stale.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 3
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "stale"


def test_unsafe_source_manifest_path_is_rejected(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    unsafe_source = "../source.md"
    files = pack_files()
    files["specdock-authoring-pack/source-manifest.json"] = json.dumps({
        "sources": [
            {
                "path": unsafe_source,
                "sha256": "0" * 64,
                "role": "unsafe",
            }
        ]
    })
    zip_path = write_zip(tmp_path / "unsafe-source.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    report_path = tmp_path / "review/validation-report.json"
    assert read_json(report_path)["status"] == "rejected"
    assert unsafe_source not in report_path.read_text(encoding="utf-8")


def test_preflight_non_pass_status_never_passes_zip(tmp_path) -> None:
    for status, code in (("fail", 1), ("blocked", 2), ("stale", 3), ("rejected", 4)):
        case_dir = tmp_path / status
        case_dir.mkdir()
        preflight = write_preflight(case_dir, preflight_data(status=status))
        zip_path = write_zip(case_dir / "valid.zip", pack_files())

        result = run_review(zip_path, preflight, case_dir / "review")

        assert result.returncode == code
        assert read_json(case_dir / "review/validation-report.json")["status"] == status


def test_preflight_boundary_missing_fails_closed(tmp_path) -> None:
    data = preflight_data()
    del data["authority"]
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "fail"


def test_preflight_repository_identity_is_required(tmp_path) -> None:
    data = preflight_data()
    del data["repository"]["full_name"]
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "fail"
    assert "preflight repository.full_name is required" in report["errors"]


def test_provenance_repository_must_match_preflight_repository(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/provenance.json"] = json.dumps({
        "authority": "evidence_only",
        "repository": {
            "full_name": "evil/repo",
            "requested_ref": "wrong-ref",
        },
        "source": "chatgpt_zip_authoring_pack",
    })
    zip_path = write_zip(tmp_path / "wrong-provenance.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "fail"
    assert "provenance.repository does not match preflight repository" in report["errors"]


def test_preflight_observed_ref_or_head_is_required(tmp_path) -> None:
    data = preflight_data()
    del data["repository"]["observed_ref"]
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "fail"
    assert "preflight repository observed_ref or observed_head is required" in report["errors"]


def test_preflight_stale_if_source_paths_must_be_safe(tmp_path) -> None:
    data = preflight_data()
    data["stale_if"][0]["source_paths"] = ["../source.md"]
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "fail"
    assert "preflight stale_if[0].source_paths[0] is invalid" in report["errors"]


def test_stale_if_current_source_hash_mismatch_is_stale(tmp_path) -> None:
    stale_sha = "0" * 64
    preflight = write_preflight(tmp_path, preflight_data(source_sha=stale_sha))
    zip_path = write_zip(tmp_path / "valid.zip", pack_files(source_sha=stale_sha))

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 3
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "stale"


def test_stale_if_missing_current_source_is_blocked(tmp_path) -> None:
    missing_source = "missing/source.md"
    expected_sha = "0" * 64
    data = preflight_data(source_sha=expected_sha)
    data["sources"][0]["path"] = missing_source
    data["sources"][0]["role"] = "missing"
    data["stale_if"][0]["source_paths"] = [missing_source]
    preflight = write_preflight(tmp_path, data)
    files = pack_files(source_sha=expected_sha)
    files["specdock-authoring-pack/source-manifest.json"] = json.dumps({
        "sources": [
            {
                "path": missing_source,
                "sha256": expected_sha,
                "role": "missing",
            }
        ]
    })
    files["specdock-authoring-pack/stale-if.json"] = json.dumps({
        "stale_if": [
            {
                "kind": "source_hash_changed",
                "source_paths": [missing_source],
            }
        ]
    })
    zip_path = write_zip(tmp_path / "blocked-source.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 2
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "blocked"


def test_stale_if_source_without_preflight_snapshot_is_stale(tmp_path) -> None:
    untracked_source = "scripts/authoring-pack/review_chatgpt_authoring_pack.py"
    data = preflight_data()
    data["stale_if"][0]["source_paths"] = [untracked_source]
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 3
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "stale"
    assert f"stale_if source missing from preflight snapshot: {untracked_source}" in report["errors"]


def test_pack_stale_if_source_without_preflight_snapshot_is_stale(tmp_path) -> None:
    untracked_source = "scripts/authoring-pack/review_chatgpt_authoring_pack.py"
    preflight = write_preflight(tmp_path, preflight_data())
    files = pack_files()
    files["specdock-authoring-pack/stale-if.json"] = json.dumps({
        "stale_if": [
            {
                "kind": "source_hash_changed",
                "source_paths": [untracked_source],
            }
        ]
    })
    zip_path = write_zip(tmp_path / "pack-stale-if.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 3
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "stale"
    assert f"stale_if source missing from preflight snapshot: {untracked_source}" in report["errors"]


@pytest.mark.parametrize(
    "stale_if_payload",
    [
        {"stale_if": [{"kind": "manual_review", "source_paths": [FIXTURE_SOURCE]}]},
        {"stale_if": [{"kind": "source_hash_changed"}]},
        {"stale_if": [{"kind": "source_hash_changed", "source_paths": []}]},
    ],
)
def test_pack_stale_if_condition_schema_fails_closed(tmp_path, stale_if_payload: dict) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["specdock-authoring-pack/stale-if.json"] = json.dumps(stale_if_payload)
    zip_path = write_zip(tmp_path / "malformed-stale-if.zip", files)

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 1
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "fail"


@pytest.mark.parametrize(
    "claim",
    [
        "The spec-reviewer-passed and .assurance.json updated.",
        "Pull Request created.",
        "authority: canonical",
        "adoption_status: adopted",
        "canonical overwrite",
        "qa-reviewer passed",
        "implementation complete",
    ],
)
def test_unsafe_authority_claim_is_rejected(tmp_path, claim: str) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(
        tmp_path / "claim.zip",
        pack_files(readme=f"{claim}\n"),
    )

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"


def test_private_key_diagnostic_is_redacted(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    secret = "-----BEGIN PRIVATE KEY-----"
    zip_path = write_zip(tmp_path / "secret.zip", pack_files(readme=secret))

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert_no_leak(result, secret)
    assert secret not in (tmp_path / "review/validation-report.json").read_text(encoding="utf-8")
    assert secret not in (tmp_path / "review/validation-summary.md").read_text(encoding="utf-8")


def test_unsafe_text_payload_is_rejected_without_echoing_payload(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    unsafe_payload = "raw transcript from /Users/alice/.oracle session"
    zip_path = write_zip(tmp_path / "unsafe-text.zip", pack_files(readme=unsafe_payload))

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 4
    assert_no_leak(result, unsafe_payload)
    assert read_json(tmp_path / "review/validation-report.json")["status"] == "rejected"
    assert unsafe_payload not in (tmp_path / "review/validation-report.json").read_text(encoding="utf-8")
    assert unsafe_payload not in (tmp_path / "review/validation-summary.md").read_text(encoding="utf-8")


def test_token_like_preflight_diagnostic_is_redacted(tmp_path) -> None:
    data = preflight_data(status="blocked")
    token_like = "token-secret-value-12345"
    data["safe_output_constraints"]["forbidden_claims"].append(token_like)
    preflight = write_preflight(tmp_path, data)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 2
    assert_no_leak(result, token_like)
    assert token_like not in (tmp_path / "review/validation-report.json").read_text(encoding="utf-8")
    assert token_like not in (tmp_path / "review/validation-summary.md").read_text(encoding="utf-8")


def test_no_canonical_docs_or_assurance_mutation(tmp_path) -> None:
    snapshots = {
        path: path.read_bytes()
        for path in (
            ISSUE_DIR / "requirement.md",
            ISSUE_DIR / "design.md",
            ISSUE_DIR / "plan.md",
            ISSUE_DIR / ".assurance.json",
        )
        if path.exists()
    }
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 0
    invalid_files = pack_files()
    invalid_files["../evil.md"] = "evil"
    invalid_zip_path = write_zip(tmp_path / "invalid.zip", invalid_files)

    invalid_result = run_review(invalid_zip_path, preflight, tmp_path / "invalid-review")

    assert invalid_result.returncode == 4
    for path, content in snapshots.items():
        assert path.read_bytes() == content


def test_unowned_output_dir_is_blocked(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    output_dir = tmp_path / "review"
    output_dir.mkdir()
    user_file = output_dir / "user.md"
    user_file.write_text("keep", encoding="utf-8")

    result = run_review(zip_path, preflight, output_dir)

    assert result.returncode == 2
    assert user_file.read_text(encoding="utf-8") == "keep"
    assert not (output_dir / "validation-report.json").exists()


def test_safe_extraction_only_after_central_directory_pass(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    files = pack_files()
    files["../evil.md"] = "evil"
    zip_path = write_zip(tmp_path / "unsafe.zip", files)
    extract_dir = tmp_path / "extract"

    result = run_review(zip_path, preflight, tmp_path / "review", "--extract-dir", str(extract_dir))

    assert result.returncode == 4
    assert not extract_dir.exists()


def test_safe_extraction_failure_is_blocked(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    extract_dir = tmp_path / "extract"
    extract_dir.write_text("not a directory", encoding="utf-8")

    result = run_review(zip_path, preflight, tmp_path / "review", "--extract-dir", str(extract_dir))

    assert result.returncode == 2
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "blocked"


def test_symlinked_extract_dir_is_blocked_before_writing(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    extract_dir = tmp_path / "extract"
    extract_dir.symlink_to(target_dir, target_is_directory=True)

    result = run_review(zip_path, preflight, tmp_path / "review", "--extract-dir", str(extract_dir))

    assert result.returncode == 2
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] == "blocked"
    assert "extract_dir must be a real directory; safe extraction skipped" in report["errors"]
    assert not (target_dir / "specdock-authoring-pack/README.md").exists()


def test_status_taxonomy_keeps_unreviewed_out_of_execution_status(tmp_path) -> None:
    preflight = write_preflight(tmp_path)
    zip_path = write_zip(tmp_path / "valid.zip", pack_files())

    result = run_review(zip_path, preflight, tmp_path / "review")

    assert result.returncode == 0
    report = read_json(tmp_path / "review/validation-report.json")
    assert report["status"] in {"pass", "fail", "blocked", "stale", "rejected", "deferred"}
    assert report["adoption_status"] == "unreviewed"
    assert "unreviewed" not in REVIEW_MODULE.STATUS_EXIT_CODES
