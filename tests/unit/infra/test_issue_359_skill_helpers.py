from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

_REPO_ROOT = Path(__file__).resolve().parents[3]
_HELPER = (
    _REPO_ROOT
    / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py"
)
_ARTIFACT_REL = Path(
    "spec-dock/initiatives/init-00001-example/epics/epic-00002-example/"
    "issues/iss-00003-example/artifacts/20260812t000000z-research-example.md"
)


def _run_helper(
    repo_root: Path,
    *args: str,
    body: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    assert _HELPER.is_file()
    return subprocess.run(
        [sys.executable, str(_HELPER), *args],
        cwd=repo_root,
        input=body,
        capture_output=True,
        check=False,
    )


def _create_artifact(repo_root: Path, content: bytes = b"template\n") -> Path:
    artifact = repo_root / _ARTIFACT_REL
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(content)
    return artifact


def _identity(repo_root: Path) -> dict[str, int]:
    result = _run_helper(
        repo_root,
        "identity",
        "--repo-root",
        str(repo_root),
        "--artifact",
        _ARTIFACT_REL.as_posix(),
    )
    assert result.returncode == 0, result.stderr.decode()
    payload = json.loads(result.stdout)
    assert set(payload) == {"device", "inode"}
    return payload


def _finalize(repo_root: Path, identity: dict[str, int], body: bytes) -> subprocess.CompletedProcess[bytes]:
    return _run_helper(
        repo_root,
        "finalize",
        "--repo-root",
        str(repo_root),
        "--artifact",
        _ARTIFACT_REL.as_posix(),
        "--expected-device",
        str(identity["device"]),
        "--expected-inode",
        str(identity["inode"]),
        body=body,
    )


def test_issue_359_finalizer_writes_only_the_pinned_artifact(tmp_path: Path) -> None:
    artifact = _create_artifact(tmp_path)
    sibling = artifact.parent / "existing.md"
    sibling.write_bytes(b"existing\n")
    identity = _identity(tmp_path)

    result = _finalize(tmp_path, identity, b"# Final body\n")

    assert result.returncode == 0, result.stderr.decode()
    assert artifact.read_bytes() == b"# Final body\n"
    assert sibling.read_bytes() == b"existing\n"
    assert _ARTIFACT_REL.as_posix().encode() in result.stdout


def test_issue_359_finalizer_rejects_symlink_replacement_without_external_write(
    tmp_path: Path,
) -> None:
    artifact = _create_artifact(tmp_path)
    identity = _identity(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_bytes(b"outside\n")
    artifact.unlink()
    artifact.symlink_to(outside)

    result = _finalize(tmp_path, identity, b"unsafe\n")

    assert result.returncode != 0
    assert artifact.is_symlink()
    assert outside.read_bytes() == b"outside\n"
    assert b"partial Artifact requires operator recovery" in result.stderr


def test_issue_359_finalizer_rejects_inode_replacement_without_truncating_it(
    tmp_path: Path,
) -> None:
    artifact = _create_artifact(tmp_path)
    identity = _identity(tmp_path)
    artifact.unlink()
    artifact.write_bytes(b"replacement\n")

    result = _finalize(tmp_path, identity, b"unsafe\n")

    assert result.returncode != 0
    assert artifact.read_bytes() == b"replacement\n"
    assert b"identity changed" in result.stderr


def test_issue_359_identity_rejects_symlinked_artifacts_directory(tmp_path: Path) -> None:
    artifact = _create_artifact(tmp_path)
    external_dir = tmp_path / "external-artifacts"
    external_dir.mkdir()
    external_file = external_dir / artifact.name
    external_file.write_bytes(b"external\n")
    artifacts_dir = artifact.parent
    backup = artifacts_dir.with_name("artifacts-original")
    artifacts_dir.rename(backup)
    artifacts_dir.symlink_to(external_dir, target_is_directory=True)

    result = _run_helper(
        tmp_path,
        "identity",
        "--repo-root",
        str(tmp_path),
        "--artifact",
        _ARTIFACT_REL.as_posix(),
    )

    assert result.returncode != 0
    assert external_file.read_bytes() == b"external\n"
    assert b"symlink" in result.stderr.lower() or os.name == "nt"


def test_issue_359_helper_accepts_current_cli_prefix_for_repo_named_spec_dock(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "spec-dock"
    repo_root.mkdir()
    artifact = _create_artifact(repo_root)
    cli_returned_path = Path(repo_root.name) / _ARTIFACT_REL

    identity_result = _run_helper(
        repo_root,
        "identity",
        "--repo-root",
        str(repo_root),
        "--artifact",
        cli_returned_path.as_posix(),
    )

    assert identity_result.returncode == 0, identity_result.stderr.decode()
    identity = json.loads(identity_result.stdout)
    finalize_result = _run_helper(
        repo_root,
        "finalize",
        "--repo-root",
        str(repo_root),
        "--artifact",
        cli_returned_path.as_posix(),
        "--expected-device",
        str(identity["device"]),
        "--expected-inode",
        str(identity["inode"]),
        body=b"# Final body\n",
    )
    assert finalize_result.returncode == 0, finalize_result.stderr.decode()
    assert artifact.read_bytes() == b"# Final body\n"
