from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import sys

import pytest


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.application import contracts
        from spec_dock_runtime.infra import binary_artifact_publisher
    finally:
        sys.path.pop(0)
    return contracts, binary_artifact_publisher


def _layout(tmp_path: Path):
    repo_root = tmp_path / "repo"
    specdock_dir = repo_root / "spec-dock"
    initiative = specdock_dir / "initiatives" / "init-local-00003-parent"
    epic = initiative / "epics" / "epic-00312-parent"
    issue = epic / "issues" / "iss-00317-child"
    for root in (specdock_dir, initiative, epic, issue):
        (root / ".workbench").mkdir(parents=True, exist_ok=True)
    artifacts_dir = issue / "artifacts"
    artifacts_dir.mkdir()
    return repo_root, specdock_dir, (initiative, epic, issue), artifacts_dir


def _source_request(contracts, repo_root, specdock_dir, scopes, source_path):
    return contracts.WorkbenchSourceGuardRequest(
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        scope_directories=scopes,
        source_path=source_path,
    )


def _publish_request(contracts, repo_root, specdock_dir, scopes, source_path, destination):
    return contracts.BinaryArtifactPublishRequest(
        source=_source_request(contracts, repo_root, specdock_dir, scopes, source_path),
        destination_path=destination,
    )


@pytest.mark.parametrize("root_index", [0, 1, 2, 3])
@pytest.mark.parametrize("path_kind", ["relative", "absolute"])
def test_tc317_s02_01_accepts_root_and_resolved_scope_direct_child_workbench_sources(tmp_path, root_index, path_kind):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    roots = (specdock_dir, *scopes)
    source = roots[root_index] / ".workbench" / "accepted.md"
    source.write_bytes(b"accepted source\n")
    selected = source.relative_to(repo_root) if path_kind == "relative" else source
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()

    guarded = publisher.guard_source(_source_request(contracts, repo_root, specdock_dir, scopes, selected))

    assert guarded.source_path == source
    assert guarded.workbench_root == source.parent
    assert source.read_bytes() == b"accepted source\n"
    assert list(artifacts_dir.iterdir()) == []


@pytest.mark.parametrize(
    "source_case",
    ["missing", "outside", "uppercase", "directory", "source_symlink", "ancestor_symlink", "fifo"],
)
def test_tc317_s02_01_rejects_ineligible_sources_before_read_or_publish(tmp_path, monkeypatch, source_case):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    workbench = specdock_dir / ".workbench"
    external = repo_root / "external.md"
    external.write_bytes(b"external sentinel")
    formal = artifacts_dir / "existing.md"
    formal.write_bytes(b"formal sentinel")
    source = workbench / "source.md"
    if source_case == "missing":
        pass
    elif source_case == "outside":
        source = external
    elif source_case == "uppercase":
        source = workbench / "source.MD"
        source.write_bytes(b"uppercase")
    elif source_case == "directory":
        source.mkdir()
    elif source_case == "source_symlink":
        try:
            source.symlink_to(external)
        except OSError:
            pytest.skip("symlink creation is unavailable")
    elif source_case == "ancestor_symlink":
        external_dir = repo_root / "external-dir"
        external_dir.mkdir()
        (external_dir / "source.md").write_bytes(b"external nested sentinel")
        linked = workbench / "linked"
        try:
            linked.symlink_to(external_dir, target_is_directory=True)
        except OSError:
            pytest.skip("symlink creation is unavailable")
        source = linked / "source.md"
    else:
        if not hasattr(os, "mkfifo"):
            pytest.skip("FIFO creation is unavailable")
        os.mkfifo(source)

    open_calls = []
    link_calls = []
    original_open = publisher_module.os.open
    original_link = publisher_module.os.link

    def recording_open(path, *args, **kwargs):
        open_calls.append(Path(path))
        return original_open(path, *args, **kwargs)

    def recording_link(source_path, destination_path, *args, **kwargs):
        link_calls.append((Path(source_path), Path(destination_path)))
        return original_link(source_path, destination_path, *args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "open", recording_open)
    monkeypatch.setattr(publisher_module.os, "link", recording_link)
    destination = artifacts_dir / "new.md"

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher_module.FilesystemBinaryArtifactPublisher().publish(
            _publish_request(
                contracts,
                repo_root,
                specdock_dir,
                scopes,
                source.relative_to(repo_root) if source_case != "outside" else source,
                destination,
            )
        )

    assert captured.value.code == "source_ineligible"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == "not_created"
    assert open_calls == []
    assert link_calls == []
    assert not destination.exists()
    assert external.read_bytes() == b"external sentinel"
    assert formal.read_bytes() == b"formal sentinel"


PAYLOADS = [
    b"line one\nline two\n",
    b"line one\r\nline two\r\n",
    b"\xef\xbb\xbfheading\n",
    b"no final newline",
    "日本語の本文\n".encode(),
    b"before\x00after\n",
    b"invalid:\xff\xfe\x80",
    b"",
]


@pytest.mark.parametrize("payload", PAYLOADS, ids=["lf", "crlf", "bom", "no-final", "ja", "nul", "invalid", "empty"])
def test_tc317_s02_02_chunked_opaque_stage_preserves_all_bytes(tmp_path, payload):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(payload)
    destination = artifacts_dir / "published.md"

    result = publisher_module.FilesystemBinaryArtifactPublisher(chunk_size=3).publish(
        _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
    )

    expected_hash = hashlib.sha256(payload).hexdigest()
    assert result.source_sha256 == result.stream_sha256 == result.staged_sha256 == expected_hash
    assert result.source_byte_count == result.stream_byte_count == result.staged_byte_count == len(payload)
    assert result.destination_sha256 == expected_hash
    assert result.destination_byte_count == len(payload)
    assert result.source_inode != result.staged_inode
    assert destination.stat().st_ino != result.source_inode
    assert source.read_bytes() == payload
    assert destination.read_bytes() == payload
    assert not list(artifacts_dir.glob(".spec-dock-import-*"))


@pytest.mark.parametrize("mutation", ["same_size", "replace", "unlink"])
def test_tc317_s02_03_barrier_detects_source_mutation_replacement_and_unlink(tmp_path, mutation):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    original = b"original bytes"
    source.write_bytes(original)
    displaced = source.with_name("displaced.md")

    def mutate_after_stage():
        if mutation == "same_size":
            source.write_bytes(b"mutated! bytes")
        elif mutation == "replace":
            source.rename(displaced)
            source.write_bytes(original)
        else:
            source.unlink()

    destination = artifacts_dir / "published.md"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher(stage_barrier=mutate_after_stage)

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert captured.value.code == "source_changed"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == "removed"
    assert not destination.exists()
    assert not list(artifacts_dir.glob(".spec-dock-import-*"))
    if mutation == "replace":
        assert displaced.read_bytes() == original


@pytest.mark.parametrize(
    ("primary_fault", "cleanup_fault", "expected_code", "expected_cleanup"),
    [
        ("temp_create", None, "temp_create_failed", "not_created"),
        ("write", None, "copy_failed", "removed"),
        ("hash", None, "hash_failed", "removed"),
        ("file_fsync", None, "file_fsync_failed", "removed"),
        ("publication_unsupported", None, "publication_unsupported", "removed"),
        ("write", "cleanup", "copy_failed", "retained"),
    ],
)
def test_tc317_s02_04_prepublish_faults_preserve_source_and_formal_state(
    tmp_path, primary_fault, cleanup_fault, expected_code, expected_cleanup
):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source sentinel\x00\xff"
    source.write_bytes(source_body)
    formal = artifacts_dir / "existing.md"
    formal.write_bytes(b"formal sentinel")
    destination = artifacts_dir / "new.md"

    def inject(point):
        if point in (primary_fault, cleanup_fault):
            raise OSError("secret raw injected detail")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    error = captured.value
    assert error.code == expected_code
    assert error.committed is False
    assert error.cleanup_state == expected_cleanup
    assert "secret" not in str(error)
    assert str(source) not in str(error)
    assert source.read_bytes() == source_body
    assert formal.read_bytes() == b"formal sentinel"
    assert not destination.exists()
    leftovers = list(artifacts_dir.glob(".spec-dock-import-*"))
    assert (len(leftovers) == 1) is (expected_cleanup == "retained")
    assert all(not path.name.endswith(".md") for path in leftovers)


def test_tc317_s02_04_staged_hash_mismatch_is_prepublish_failure(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    source.write_bytes(source_body)
    destination = artifacts_dir / "new.md"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    original_hash_descriptor = publisher._hash_descriptor
    hash_calls = 0

    def mismatched_staged_hash(descriptor):
        nonlocal hash_calls
        hash_calls += 1
        digest, byte_count = original_hash_descriptor(descriptor)
        if hash_calls == 1:
            return "0" * 64, byte_count
        return digest, byte_count

    monkeypatch.setattr(publisher, "_hash_descriptor", mismatched_staged_hash)

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert captured.value.code == "hash_mismatch"
    assert captured.value.cleanup_state == "removed"
    assert source.read_bytes() == source_body
    assert not destination.exists()
    assert not list(artifacts_dir.glob(".spec-dock-import-*"))


def test_no_replace_primitive_preserves_existing_destination(tmp_path):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(b"new bytes")
    destination = artifacts_dir / "published.md"
    destination.write_bytes(b"existing bytes")

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher_module.FilesystemBinaryArtifactPublisher().publish(
            _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
        )

    assert captured.value.code == "destination_exists"
    assert captured.value.cleanup_state == "removed"
    assert destination.read_bytes() == b"existing bytes"
    assert source.read_bytes() == b"new bytes"
    assert not list(artifacts_dir.glob(".spec-dock-import-*"))


@pytest.mark.parametrize("unavailable_primitive", [False, True])
def test_unsupported_descriptor_publication_fails_closed(tmp_path, monkeypatch, unavailable_primitive):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(b"source bytes")
    destination = artifacts_dir / "published.md"
    if unavailable_primitive:
        monkeypatch.setattr(publisher_module.sys, "platform", "linux")

        def unavailable_link(*args, **kwargs):
            raise OSError(publisher_module.errno.ENOENT, "proc fd unavailable")

        monkeypatch.setattr(publisher_module.os, "link", unavailable_link)
    else:
        monkeypatch.setattr(publisher_module.sys, "platform", "unsupported")

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher_module.FilesystemBinaryArtifactPublisher().publish(
            _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
        )

    assert captured.value.code == "publication_unsupported"
    assert captured.value.cleanup_state == "removed"
    assert not destination.exists()
    assert source.read_bytes() == b"source bytes"
    assert not list(artifacts_dir.glob(".spec-dock-import-*"))


@pytest.mark.parametrize("replacement_kind", ["different_bytes", "source_inode"])
def test_publication_is_bound_to_verified_staged_descriptor_after_path_replacement(tmp_path, replacement_kind):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    verified_body = b"verified staged bytes"
    replacement_body = b"unverified replacement"
    source.write_bytes(verified_body)
    destination = artifacts_dir / "published.md"
    replacement_path = None

    def replace_staged_path_after_verification(point):
        nonlocal replacement_path
        if point != "before_publication":
            return
        [replacement_path] = artifacts_dir.glob(".spec-dock-import-*")
        verified_path = replacement_path.with_name(replacement_path.name + ".verified")
        replacement_path.rename(verified_path)
        if replacement_kind == "different_bytes":
            replacement_path.write_bytes(replacement_body)
        else:
            os.link(source, replacement_path)

    result = publisher_module.FilesystemBinaryArtifactPublisher(
        fault_injector=replace_staged_path_after_verification
    ).publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert result.committed is True
    assert destination.read_bytes() == verified_body
    assert result.destination_sha256 == hashlib.sha256(verified_body).hexdigest()
    assert destination.stat().st_ino != source.stat().st_ino
    assert replacement_path is not None
    assert replacement_path.exists()
    assert destination.stat().st_ino != replacement_path.stat().st_ino
    assert result.cleanup_state == "retained"
    assert result.warning_codes == ("temp_cleanup_retained",)


def test_tc317_s02_03_destination_mismatch_after_publication_is_committed_warning(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    mutated_body = b"mutated destination"
    source.write_bytes(source_body)
    destination = artifacts_dir / "published.md"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    original_publish = publisher._publish_no_replace

    def publish_then_mutate(temp_fd, destination_parent_fd, destination_name):
        original_publish(temp_fd, destination_parent_fd, destination_name)
        descriptor = os.open(destination_name, os.O_WRONLY | os.O_TRUNC, dir_fd=destination_parent_fd)
        try:
            os.write(descriptor, mutated_body)
        finally:
            os.close(descriptor)

    monkeypatch.setattr(publisher, "_publish_no_replace", publish_then_mutate)
    result = publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert result.committed is True
    assert result.warning_codes == ("destination_mismatch",)
    assert result.destination_path == destination
    assert result.destination_sha256 == hashlib.sha256(mutated_body).hexdigest()
    assert result.destination_byte_count == len(mutated_body)
    assert result.staged_sha256 == hashlib.sha256(source_body).hexdigest()
    assert destination.read_bytes() == mutated_body


def test_tc317_s02_03_destination_confirmation_read_failure_is_committed_warning(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    source.write_bytes(source_body)
    destination = artifacts_dir / "published.md"
    original_open = publisher_module.os.open

    def fail_destination_confirmation(path, *args, **kwargs):
        if path == destination.name and kwargs.get("dir_fd") is not None:
            raise OSError("secret destination confirmation detail")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "open", fail_destination_confirmation)

    result = publisher_module.FilesystemBinaryArtifactPublisher().publish(
        _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
    )

    expected_hash = hashlib.sha256(source_body).hexdigest()
    assert result.committed is True
    assert result.warning_codes == ("destination_read_failed",)
    assert result.destination_path == destination
    assert result.destination_sha256 == result.staged_sha256 == expected_hash
    assert result.destination_byte_count == result.staged_byte_count == len(source_body)
    assert destination.read_bytes() == source_body


def test_tc317_s02_04_post_publish_temp_retention_is_committed_warning(tmp_path):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    source.write_bytes(source_body)
    destination = artifacts_dir / "published.md"

    def retain_temp_after_publish(point):
        if point == "cleanup":
            raise OSError("secret cleanup detail")

    result = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=retain_temp_after_publish).publish(
        _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
    )

    assert result.committed is True
    assert result.warning_codes == ("temp_cleanup_retained",)
    assert result.cleanup_state == "retained"
    assert result.destination_path == destination
    assert destination.read_bytes() == source_body
    assert len(list(artifacts_dir.glob(".spec-dock-import-*"))) == 1


def _swap_directory_for_external_symlink(directory: Path, displaced: Path, external: Path) -> None:
    directory.rename(displaced)
    try:
        directory.symlink_to(external, target_is_directory=True)
    except OSError:
        displaced.rename(directory)
        pytest.skip("symlink creation is unavailable")


def test_temp_create_hook_precedes_secure_parent_open_and_rejects_parent_swap(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(b"source bytes")
    destination = artifacts_dir / "published.md"
    displaced = artifacts_dir.with_name("artifacts-original")
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "sentinel"
    sentinel.write_bytes(b"external sentinel")
    calls = []
    original_secure_open = publisher_module._open_secure_directory

    def record_secure_open(*args, **kwargs):
        calls.append("secure_parent_open")
        return original_secure_open(*args, **kwargs)

    def swap_before_secure_open(point):
        calls.append(point)
        if point == "temp_create":
            _swap_directory_for_external_symlink(artifacts_dir, displaced, external)

    monkeypatch.setattr(publisher_module, "_open_secure_directory", record_secure_open)

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=swap_before_secure_open).publish(
            _publish_request(contracts, repo_root, specdock_dir, scopes, source, destination)
        )

    assert captured.value.code == "destination_ineligible"
    assert captured.value.cleanup_state == "not_created"
    assert captured.value.committed is False
    assert calls[:2] == ["temp_create", "secure_parent_open"]
    assert list(displaced.iterdir()) == []
    assert list(external.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b"external sentinel"


def test_before_publication_parent_swap_is_rejected_and_temp_cleanup_uses_held_parent(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(b"source bytes")
    destination = artifacts_dir / "published.md"
    displaced = artifacts_dir.with_name("artifacts-original")
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "sentinel"
    sentinel.write_bytes(b"external sentinel")
    same_name_sentinel = None

    def swap_before_publication(point):
        nonlocal same_name_sentinel
        if point == "before_publication":
            [temp_path] = artifacts_dir.glob(".spec-dock-import-*")
            same_name_sentinel = external / temp_path.name
            same_name_sentinel.write_bytes(b"external same-name sentinel")
            _swap_directory_for_external_symlink(artifacts_dir, displaced, external)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=swap_before_publication)

    def reject_publication(*args, **kwargs):
        raise AssertionError("publication must not run after parent identity mismatch")

    monkeypatch.setattr(publisher, "_publish_no_replace", reject_publication)

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert captured.value.code == "destination_ineligible"
    assert captured.value.cleanup_state == "removed"
    assert captured.value.committed is False
    assert list(displaced.iterdir()) == []
    assert same_name_sentinel is not None
    assert sorted(external.iterdir()) == sorted((sentinel, same_name_sentinel))
    assert sentinel.read_bytes() == b"external sentinel"
    assert same_name_sentinel.read_bytes() == b"external same-name sentinel"


def test_publication_syscall_window_parent_swap_commits_to_held_parent_with_existing_warning(
    tmp_path,
    monkeypatch,
):
    if sys.platform != "darwin":
        pytest.skip("actual fclonefileat race gate runs on macOS")
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    source.write_bytes(source_body)
    destination = artifacts_dir / "published.md"
    displaced = artifacts_dir.with_name("artifacts-original")
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "sentinel"
    sentinel.write_bytes(b"external sentinel")
    original_clone = publisher_module._clone_macos_descriptor

    def swap_inside_clone(source_fd, destination_parent_fd, destination_name):
        _swap_directory_for_external_symlink(artifacts_dir, displaced, external)
        return original_clone(source_fd, destination_parent_fd, destination_name)

    monkeypatch.setattr(publisher_module, "_clone_macos_descriptor", swap_inside_clone)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher()

    def reject_confirmation(*args, **kwargs):
        raise AssertionError("confirmation must not run after parent identity mismatch")

    monkeypatch.setattr(publisher, "_hash_published_destination", reject_confirmation)

    result = publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    expected_hash = hashlib.sha256(source_body).hexdigest()
    assert result.committed is True
    assert result.warning_codes == ("destination_read_failed",)
    assert result.destination_sha256 == result.staged_sha256 == expected_hash
    assert result.destination_byte_count == result.staged_byte_count == len(source_body)
    assert result.cleanup_state == "removed"
    assert (displaced / destination.name).read_bytes() == source_body
    assert list(displaced.glob(".spec-dock-import-*")) == []
    assert list(external.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b"external sentinel"


def test_linux_publication_uses_captured_parent_fd_without_late_parent_open(monkeypatch):
    _, publisher_module = _runtime_modules()
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    calls = []

    def record_link(source, destination, **kwargs):
        calls.append((source, destination, kwargs))

    def reject_open(*args, **kwargs):
        raise AssertionError("publication must not reopen destination parent")

    monkeypatch.setattr(publisher_module.sys, "platform", "linux")
    monkeypatch.setattr(publisher_module.os, "link", record_link)
    monkeypatch.setattr(publisher_module.os, "open", reject_open)

    publisher._publish_no_replace(41, 73, "published.md")

    assert calls == [
        (
            "/proc/self/fd/41",
            "published.md",
            {"dst_dir_fd": 73, "follow_symlinks": True},
        )
    ]


def test_linux_publication_syscall_window_parent_swap_commits_to_held_parent_with_existing_warning(
    tmp_path,
    monkeypatch,
):
    if not sys.platform.startswith("linux"):
        pytest.skip("actual linkat race gate runs on Linux")
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source_body = b"source bytes"
    source.write_bytes(source_body)
    destination = artifacts_dir / "published.md"
    displaced = artifacts_dir.with_name("artifacts-original")
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "sentinel"
    sentinel.write_bytes(b"external sentinel")
    original_link = publisher_module.os.link

    def swap_inside_link(source_path, destination_name, **kwargs):
        _swap_directory_for_external_symlink(artifacts_dir, displaced, external)
        return original_link(source_path, destination_name, **kwargs)

    monkeypatch.setattr(publisher_module.os, "link", swap_inside_link)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher()

    def reject_confirmation(*args, **kwargs):
        raise AssertionError("confirmation must not run after parent identity mismatch")

    monkeypatch.setattr(publisher, "_hash_published_destination", reject_confirmation)

    result = publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    expected_hash = hashlib.sha256(source_body).hexdigest()
    assert result.committed is True
    assert result.warning_codes == ("destination_read_failed",)
    assert result.destination_sha256 == result.staged_sha256 == expected_hash
    assert result.destination_byte_count == result.staged_byte_count == len(source_body)
    assert result.cleanup_state == "removed"
    assert (displaced / destination.name).read_bytes() == source_body
    assert list(displaced.glob(".spec-dock-import-*")) == []
    assert list(external.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b"external sentinel"


def test_macos_publication_uses_captured_parent_fd_and_destination_basename(monkeypatch):
    _, publisher_module = _runtime_modules()
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    calls = []

    def record_clone(source_fd, destination_parent_fd, destination_name):
        calls.append((source_fd, destination_parent_fd, destination_name))

    monkeypatch.setattr(publisher_module.sys, "platform", "darwin")
    monkeypatch.setattr(publisher_module, "_clone_macos_descriptor", record_clone)

    publisher._publish_no_replace(41, 73, "published.md")

    assert calls == [(41, 73, "published.md")]


def test_descriptor_lifecycle_order_uses_held_parent_through_cleanup(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, specdock_dir, scopes, artifacts_dir = _layout(tmp_path)
    source = specdock_dir / ".workbench" / "source.md"
    source.write_bytes(b"source bytes")
    destination = artifacts_dir / "published.md"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    calls = []
    held_parent_fd = None
    temp_mode = None

    def wrap_method(name):
        original = getattr(publisher, name)

        def wrapped(*args, **kwargs):
            calls.append(name)
            return original(*args, **kwargs)

        monkeypatch.setattr(publisher, name, wrapped)

    for name in (
        "_create_temp",
        "_copy_source_to_temp",
        "_verify_source_stability",
        "_publish_no_replace",
        "_fsync_directory",
        "_hash_published_destination",
        "_cleanup_temp",
    ):
        wrap_method(name)

    original_secure_open = publisher_module._open_secure_directory

    def record_secure_open(*args, **kwargs):
        nonlocal held_parent_fd
        calls.append("secure_parent_open")
        descriptor, identity = original_secure_open(*args, **kwargs)
        if held_parent_fd is None:
            held_parent_fd = descriptor
        return descriptor, identity

    original_close = publisher_module.os.close

    def record_close(descriptor):
        if descriptor == held_parent_fd:
            calls.append("held_parent_close")
        return original_close(descriptor)

    def inject(point):
        nonlocal temp_mode
        calls.append(point)
        if point == "before_publication":
            [temp_path] = artifacts_dir.glob(".spec-dock-import-*")
            temp_mode = stat.S_IMODE(temp_path.stat().st_mode)

    monkeypatch.setattr(publisher_module, "_open_secure_directory", record_secure_open)
    monkeypatch.setattr(publisher_module.os, "close", record_close)
    publisher._fault_injector = inject

    result = publisher.publish(_publish_request(contracts, repo_root, specdock_dir, scopes, source, destination))

    assert result.committed is True
    assert temp_mode == 0o600
    expected_order = (
        "temp_create",
        "secure_parent_open",
        "_create_temp",
        "_copy_source_to_temp",
        "file_fsync",
        "hash",
        "_verify_source_stability",
        "before_publication",
        "secure_parent_open",
        "_publish_no_replace",
        "publication_unsupported",
        "_fsync_directory",
        "directory_fsync",
        "secure_parent_open",
        "_hash_published_destination",
        "post_confirmation",
        "_cleanup_temp",
        "cleanup",
        "held_parent_close",
    )
    next_position = 0
    for event in expected_order:
        next_position = calls.index(event, next_position) + 1
