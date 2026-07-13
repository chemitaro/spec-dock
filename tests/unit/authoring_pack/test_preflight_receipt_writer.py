from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.authoring_pack.github_sync_preflight import _finalize_publication  # noqa: E402
from spec_dock_runtime.domain.authoring_pack.preflight_contract import (  # noqa: E402
    PreflightResult,
    PublicationEvidence,
)
from spec_dock_runtime.domain.authoring_pack.source_manifest import SourceManifest  # noqa: E402
from spec_dock_runtime.infra.authoring_pack.preflight_receipt_writer import (  # noqa: E402
    RECEIPT_FILENAME,
    publish_preflight_receipt,
    validate_preflight_receipt_output,
)


def _owned_payload(status: str = "pass") -> dict[str, object]:
    return {
        "schema_version": 1,
        "receipt_kind": "spec-dock.authoring.github-sync-preflight",
        "status": status,
    }


def test_writer_publishes_fixed_name_with_private_mode(tmp_path: Path) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload())

    target = output / RECEIPT_FILENAME
    assert outcome.status == "published"
    assert outcome.filename == RECEIPT_FILENAME
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == "pass"
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert not list(output.glob(f".{RECEIPT_FILENAME}.*.tmp"))


@pytest.mark.parametrize("kind", ("repository", "missing", "not_directory", "symlink", "broken_symlink"))
def test_writer_rejects_unsafe_output_directory(tmp_path: Path, kind: str) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    if kind == "repository":
        output = repo / "evidence"
        output.mkdir()
        expected = "receipt_output_inside_repository"
    elif kind == "missing":
        output = tmp_path / "missing"
        expected = "receipt_output_directory_missing"
    elif kind == "not_directory":
        output = tmp_path / "file"
        output.write_text("mine", encoding="utf-8")
        expected = "receipt_output_not_directory"
    elif kind == "symlink":
        output = tmp_path / "link"
        output.symlink_to(outside, target_is_directory=True)
        expected = "receipt_output_symlink"
    else:
        output = tmp_path / "broken"
        output.symlink_to(tmp_path / "absent", target_is_directory=True)
        expected = "receipt_output_symlink"

    assert validate_preflight_receipt_output(repo_root=repo, output_dir=output) == expected
    assert not (outside / RECEIPT_FILENAME).exists()


def test_writer_rejects_parent_traversal_and_symlink_ancestor(tmp_path: Path) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    repo.mkdir()
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)

    assert validate_preflight_receipt_output(repo_root=repo, output_dir=Path("../evidence")) == (
        "receipt_output_parent_traversal"
    )
    assert validate_preflight_receipt_output(repo_root=repo, output_dir=link / "child") == (
        "receipt_output_symlink"
    )


@pytest.mark.parametrize("contents", (b"user data", b"{bad json", b'{}'))
def test_writer_preserves_non_owned_existing_target(tmp_path: Path, contents: bytes) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    target = output / RECEIPT_FILENAME
    target.write_bytes(contents)

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload())

    assert outcome.status == "rejected"
    assert outcome.blocker == "non_owned_existing_receipt_target"
    assert target.read_bytes() == contents


@pytest.mark.parametrize("target_kind", ("symlink", "directory"))
def test_writer_rejects_non_regular_fixed_target_without_mutating_it(tmp_path: Path, target_kind: str) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    target = output / RECEIPT_FILENAME
    link_destination = tmp_path / "user-owned.txt"
    link_destination.write_text("keep me\n", encoding="utf-8")
    if target_kind == "symlink":
        target.symlink_to(link_destination)
    else:
        target.mkdir()
        (target / "keep.txt").write_text("keep me\n", encoding="utf-8")

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload())

    assert outcome.status == "rejected"
    assert outcome.blocker == "non_owned_existing_receipt_target"
    if target_kind == "symlink":
        assert target.is_symlink()
        assert link_destination.read_text(encoding="utf-8") == "keep me\n"
    else:
        assert target.is_dir()
        assert (target / "keep.txt").read_text(encoding="utf-8") == "keep me\n"


@pytest.mark.parametrize("target_kind", ("unsupported_schema", "oversize"))
def test_writer_rejects_unowned_receipt_boundary_cases(tmp_path: Path, target_kind: str) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    target = output / RECEIPT_FILENAME
    if target_kind == "unsupported_schema":
        original = json.dumps(
            {
                "schema_version": 2,
                "receipt_kind": "spec-dock.authoring.github-sync-preflight",
                "status": "pass",
            }
        ).encode()
    else:
        original = b"x" * (1024 * 1024 + 1)
    target.write_bytes(original)

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload())

    assert outcome.status == "rejected"
    assert outcome.blocker == "non_owned_existing_receipt_target"
    assert target.read_bytes() == original


def test_writer_replaces_owned_receipt_atomically(tmp_path: Path) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    target = output / RECEIPT_FILENAME
    target.write_text(json.dumps(_owned_payload("blocked")), encoding="utf-8")

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload("pass"))

    assert outcome.status == "published"
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == "pass"


@pytest.mark.parametrize("failure", ("file_fsync", "replace"))
def test_writer_preserves_owned_receipt_when_publication_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    target = output / RECEIPT_FILENAME
    old = json.dumps(_owned_payload("blocked")).encode()
    target.write_bytes(old)

    if failure == "file_fsync":
        monkeypatch.setattr(os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError("fsync failed")))
    else:
        monkeypatch.setattr(Path, "replace", lambda *_args: (_ for _ in ()).throw(OSError("replace failed")))

    outcome = publish_preflight_receipt(repo_root=repo, output_dir=output, payload=_owned_payload("pass"))

    assert outcome.status == "failed"
    assert outcome.blocker == "receipt_publication_failed"
    assert target.read_bytes() == old
    assert not list(output.glob(f".{RECEIPT_FILENAME}.*.tmp"))


def test_publication_failure_blocks_result_without_erasing_sync_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tmp_path = tmp_path.resolve()
    repo = tmp_path / "repo"
    output = tmp_path / "evidence"
    repo.mkdir()
    output.mkdir()
    result = PreflightResult(
        status="pass",
        evidence_mode="github-synced",
        sync_state="synced",
        github_sync="verified",
        requested_ref="main",
        effective_ref="main",
        local_head="abc",
        remote_head="abc",
        source_manifest=SourceManifest((), {}, "manifest"),
        source_hash_mismatch_checked=False,
    )
    monkeypatch.setattr(
        "spec_dock_runtime.application.authoring_pack.github_sync_preflight.publish_preflight_receipt",
        lambda **_kwargs: PublicationEvidence(
            requested=True,
            status="failed",
            filename=RECEIPT_FILENAME,
            blocker="receipt_publication_failed",
        ),
    )

    finalized = _finalize_publication(result, repo, output, None)

    assert finalized.status == "blocked"
    assert finalized.sync_state == "synced"
    assert finalized.github_sync == "verified"
    assert finalized.publication.status == "failed"
    assert "receipt_publication_failed" in finalized.blockers
