from __future__ import annotations

import errno
import io
import os
from pathlib import Path
import subprocess
import tarfile
from typing import Any, cast

import pytest

from spec_dock.provider_lifecycle import coordination
from spec_dock.provider_lifecycle.candidate import FIXED_DOMAINS
from spec_dock.provider_lifecycle.contracts import RepositoryBinding
from spec_dock.provider_lifecycle.coordination import (
    RepositoryBusy,
    RepositoryCoordinationError,
    RepositoryCoordinationUnavailable,
    acquire_exclusive_repository_lease,
    acquire_shared_repository_lease,
    validate_inherited_repository_lease,
)
from spec_dock.provider_lifecycle.legacy_fixture import (
    LEGACY_SOURCE_COMMIT,
    classify_exact_legacy_workspace,
    load_legacy_fixture,
)


def _materialize_verified_legacy_workspace(root: Path) -> None:
    repository = Path(__file__).parents[3]
    sources = [f"src/spec_dock/assets/{suffix}" for _kind, _public, suffix in FIXED_DOMAINS]
    archive = subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "archive",
            "--format=tar",
            LEGACY_SOURCE_COMMIT,
            "--",
            *sources,
            "spec-dock/spec-dock.version",
        ],
        check=True,
        capture_output=True,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as stream:
        for member in stream:
            if member.name == "spec-dock/spec-dock.version":
                target = root / member.name
            else:
                matched = next(
                    (
                        item
                        for item in FIXED_DOMAINS
                        if member.name == f"src/spec_dock/assets/{item[2]}"
                        or member.name.startswith(f"src/spec_dock/assets/{item[2]}/")
                    ),
                    None,
                )
                if matched is None:
                    continue
                target = root / matched[1] / member.name[len(f"src/spec_dock/assets/{matched[2]}") :].lstrip("/")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(member.linkname)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                source = stream.extractfile(member)
                assert source is not None
                target.write_bytes(source.read())
                target.chmod(0o755 if member.mode & 0o111 else 0o644)


def test_t03_fixed_roots_slots_seeds_and_protected_sentinels_are_exact(tmp_path: Path) -> None:
    workspace = tmp_path / "consumer"
    workspace.mkdir()
    _materialize_verified_legacy_workspace(workspace)

    assert tuple((kind, path) for kind, path, _source in FIXED_DOMAINS) == (
        ("root", "spec-dock/docs"),
        ("root", "spec-dock/templates"),
        ("root", "spec-dock/system"),
        ("root", "spec-dock/scripts"),
        ("slot", ".agents/skills/spec-dock"),
        ("slot", ".agents/skills/spec-dock-grill-with-docs"),
    )

    protected = workspace / "spec-dock" / "initiatives" / "protected.txt"
    protected.parent.mkdir(parents=True)
    protected.write_bytes(b"consumer-owned\n")
    protected.chmod(0o644)
    seed = workspace / "spec-dock" / ".gitignore"
    seed.write_bytes(b"consumer-seed\n")
    seed.chmod(0o644)
    ci_seed = workspace / ".github" / "workflows" / "ci.yml"
    ci_seed.parent.mkdir(parents=True)
    ci_seed.write_bytes(b"consumer-ci\n")
    ci_seed.chmod(0o644)
    sentinel_paths = (protected, seed, ci_seed)
    before = tuple((path.read_bytes(), os.lstat(path).st_ino, os.lstat(path).st_mode) for path in sentinel_paths)

    assert classify_exact_legacy_workspace(workspace) == "legacy-0.2.3"
    after = tuple((path.read_bytes(), os.lstat(path).st_ino, os.lstat(path).st_mode) for path in sentinel_paths)
    assert after == before


def test_t03_legacy_intermediate_symlink_is_not_admitted(tmp_path: Path) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    workspace = real_parent / "consumer"
    workspace.mkdir()
    _materialize_verified_legacy_workspace(workspace)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)

    assert classify_exact_legacy_workspace(linked_parent / "consumer") == "modified-legacy-workspace"


def test_t03_legacy_fixture_is_verified_and_exact_workspace_is_admitted(tmp_path: Path) -> None:
    fixture = load_legacy_fixture()
    assert fixture["source_commit"] == LEGACY_SOURCE_COMMIT
    domains = cast("list[dict[str, Any]]", fixture["domains"])
    assert [domain["path"] for domain in domains] == [domain[1] for domain in FIXED_DOMAINS]

    workspace = tmp_path / "consumer"
    workspace.mkdir()
    _materialize_verified_legacy_workspace(workspace)
    assert classify_exact_legacy_workspace(workspace, fixture) == "legacy-0.2.3"

    (workspace / "spec-dock" / "docs" / "extra.md").write_text("modified\n", encoding="utf-8")
    (workspace / "spec-dock" / "docs" / "extra.md").chmod(0o644)
    assert classify_exact_legacy_workspace(workspace, fixture) == "modified-legacy-workspace"


def test_t03_foreign_slot_marker_is_not_adopted(tmp_path: Path) -> None:
    workspace = tmp_path / "consumer"
    workspace.mkdir()
    _materialize_verified_legacy_workspace(workspace)
    marker = workspace / ".agents" / "skills" / "spec-dock" / ".spec-dock-provider-slot.json"
    marker.write_text("foreign\n", encoding="utf-8")
    marker.chmod(0o644)
    assert classify_exact_legacy_workspace(workspace) == "modified-legacy-workspace"


def test_t06_repository_lease_is_nonblocking_and_identity_bound(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()

    exclusive = acquire_exclusive_repository_lease(repository)
    try:
        assert (
            validate_inherited_repository_lease(
                exclusive.fd,
                exclusive.binding,
                "exclusive",
            )
            == exclusive.binding
        )
        with pytest.raises(RepositoryBusy):
            acquire_shared_repository_lease(repository)
        with pytest.raises(ValueError):
            validate_inherited_repository_lease(exclusive.fd, exclusive.binding, "invalid")
        with pytest.raises(RepositoryCoordinationError):
            validate_inherited_repository_lease(
                exclusive.fd,
                RepositoryBinding(
                    exclusive.binding.device,
                    exclusive.binding.inode + 1,
                    exclusive.binding.euid,
                ),
            )
    finally:
        exclusive.close()

    with acquire_shared_repository_lease(repository) as shared:
        with acquire_shared_repository_lease(repository) as second_shared:
            assert second_shared.binding == shared.binding
        with pytest.raises(RepositoryBusy):
            acquire_exclusive_repository_lease(repository)


def test_t06_lease_rebinds_visible_root_after_successful_flock(monkeypatch, tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    replacement = tmp_path / "replacement"
    replacement.mkdir()
    old_path = tmp_path / "repository-old"

    def replace_visible_root(_fd: int, _operation: int) -> None:
        repository.rename(old_path)
        replacement.rename(repository)

    monkeypatch.setattr(coordination.fcntl, "flock", replace_visible_root)

    with pytest.raises(RepositoryCoordinationError):
        acquire_exclusive_repository_lease(repository)


@pytest.mark.parametrize("root_kind", ["missing", "symlink", "regular"])
def test_t06_unsafe_visible_root_binding_is_not_reported_as_unavailable(
    tmp_path: Path,
    root_kind: str,
) -> None:
    repository = tmp_path / "repository"
    if root_kind == "symlink":
        target = tmp_path / "target"
        target.mkdir()
        repository.symlink_to(target, target_is_directory=True)
    elif root_kind == "regular":
        repository.write_text("not a directory\n", encoding="utf-8")

    with pytest.raises(RepositoryCoordinationError) as error:
        acquire_exclusive_repository_lease(repository)
    assert type(error.value) is RepositoryCoordinationError
    assert not isinstance(error.value, RepositoryCoordinationUnavailable)


def test_t06_busy_classification_rechecks_visible_root_binding(monkeypatch, tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    replacement = tmp_path / "replacement"
    replacement.mkdir()
    old_path = tmp_path / "repository-old"

    def replace_then_report_busy(_fd: int, _operation: int) -> None:
        repository.rename(old_path)
        replacement.rename(repository)
        raise OSError(errno.EAGAIN, "busy")

    monkeypatch.setattr(coordination.fcntl, "flock", replace_then_report_busy)

    with pytest.raises(RepositoryCoordinationError) as error:
        acquire_exclusive_repository_lease(repository)
    assert type(error.value) is RepositoryCoordinationError
