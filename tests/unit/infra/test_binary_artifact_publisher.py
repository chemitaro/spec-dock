from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile

import pytest


def _explicit_cleanup_state(named_stage_state: str) -> str:
    return "not_created" if sys.platform.startswith("linux") else named_stage_state


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


def _explicit_source_request(contracts, repo_root, source_path):
    return contracts.ExplicitFileSourcePreflightRequest(
        repo_root=repo_root,
        source_path=source_path,
    )


def _explicit_publish_request(contracts, repo_root, guarded_source, destination):
    return contracts.ExplicitFileArtifactPublishRequest(
        repo_root=repo_root,
        guarded_source=guarded_source,
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


@pytest.mark.parametrize("path_kind", ["repo_relative", "absolute_external", "relative_external"])
def test_explicit_source_path_forms_are_repo_root_based_and_privacy_classified(tmp_path, path_kind):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    external_dir = tmp_path / "private-parent-sentinel"
    external_dir.mkdir()
    if path_kind == "repo_relative":
        source = repo_root / "nested" / "source.bin"
        selected = Path("nested/source.bin")
        expected_visibility = "repo_relative"
        expected_display = "nested/source.bin"
    elif path_kind == "absolute_external":
        source = external_dir / "source.bin"
        selected = source
        expected_visibility = "basename_only"
        expected_display = "source.bin"
    else:
        source = external_dir / "source.bin"
        selected = Path("../private-parent-sentinel/source.bin")
        expected_visibility = "basename_only"
        expected_display = "source.bin"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"opaque")
    publisher = publisher_module.FilesystemBinaryArtifactPublisher(chunk_size=2)

    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, selected))
    try:
        result = publisher.publish_explicit_file(
            _explicit_publish_request(
                contracts,
                repo_root,
                guarded,
                artifacts_dir / f"{path_kind}.bin",
            )
        )
    finally:
        guarded.close()

    assert result.source_visibility == expected_visibility
    assert result.source_display == expected_display
    assert "private-parent-sentinel" not in result.source_display
    assert result.destination_path.read_bytes() == b"opaque"


@pytest.mark.parametrize(
    "source_case",
    ["missing", "directory", "leaf_symlink", "fifo", "socket", "device", "unreadable"],
)
def test_explicit_source_rejects_ineligible_leaf_without_blocking_or_destination_mutation(
    tmp_path, monkeypatch, source_case
):
    import socket

    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source"
    socket_handle = None
    socket_directory = None
    if source_case == "missing":
        pass
    elif source_case == "directory":
        source.mkdir()
    elif source_case == "leaf_symlink":
        target = repo_root / "target"
        target.write_bytes(b"target")
        try:
            source.symlink_to(target)
        except OSError:
            pytest.skip("symlink creation is unavailable")
    elif source_case == "fifo":
        if not hasattr(os, "mkfifo"):
            pytest.skip("FIFO creation is unavailable")
        os.mkfifo(source)
    elif source_case == "socket":
        if not hasattr(socket, "AF_UNIX"):
            pytest.skip("Unix-domain socket creation is unavailable")
        socket_directory = Path(tempfile.mkdtemp(prefix="sd-s02-"))
        source = socket_directory / "s"
        try:
            socket_handle = socket.socket(socket.AF_UNIX)
            socket_handle.bind(str(source))
        except OSError as exc:
            if socket_handle is not None:
                socket_handle.close()
                socket_handle = None
            source.unlink(missing_ok=True)
            socket_directory.rmdir()
            socket_directory = None
            pytest.skip(f"Unix-domain socket creation is unavailable: errno={exc.errno}")
    elif source_case == "device":
        source = Path("/dev/null")
    else:
        source.write_bytes(b"denied")
        original_open = publisher_module.os.open

        def deny_selected(path, flags, *args, **kwargs):
            if Path(path) == source:
                raise PermissionError("private-parent-sentinel")
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(publisher_module.os, "open", deny_selected)

    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher_module.FilesystemBinaryArtifactPublisher().guard_explicit_file_source(
                _explicit_source_request(contracts, repo_root, source)
            )
    finally:
        if socket_handle is not None:
            socket_handle.close()
        if socket_directory is not None:
            source.unlink(missing_ok=True)
            socket_directory.rmdir()

    assert captured.value.code == "source_ineligible"
    assert captured.value.cleanup_state == "not_created"
    assert list(artifacts_dir.iterdir()) == []
    assert "private-parent-sentinel" not in str(captured.value)


def test_explicit_source_regular_to_fifo_race_is_nonblocking_and_rejected(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, _artifacts_dir = _layout(tmp_path)
    source = repo_root / "source"
    source.write_bytes(b"regular")
    original_lstat = Path.lstat
    calls = 0

    def replace_after_first_lstat(path):
        nonlocal calls
        status = original_lstat(path)
        if path == source and calls == 0:
            calls += 1
            source.unlink()
            os.mkfifo(source)
        return status

    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO creation is unavailable")
    monkeypatch.setattr(Path, "lstat", replace_after_first_lstat)

    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher_module.FilesystemBinaryArtifactPublisher().guard_explicit_file_source(
            _explicit_source_request(contracts, repo_root, source)
        )

    assert captured.value.code == "source_ineligible"


def test_explicit_source_allows_stable_ancestor_symlink_but_rejects_leaf_symlink(tmp_path):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, _artifacts_dir = _layout(tmp_path)
    actual = repo_root / "actual"
    actual.mkdir()
    source = actual / "source.bin"
    source.write_bytes(b"stable")
    linked = repo_root / "linked"
    leaf_link = repo_root / "leaf-link.bin"
    try:
        linked.symlink_to(actual, target_is_directory=True)
        leaf_link.symlink_to(source)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()

    guarded = publisher.guard_explicit_file_source(
        _explicit_source_request(contracts, repo_root, Path("linked/source.bin"))
    )
    guarded.close()
    with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
        publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, Path("leaf-link.bin")))

    assert captured.value.code == "source_ineligible"


@pytest.mark.parametrize("mutation", ["same_size", "replace", "unlink", "ancestor_retarget"])
def test_explicit_source_mutation_or_ancestor_retarget_fails_before_commit(tmp_path, mutation):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    first = repo_root / "first"
    second = repo_root / "second"
    first.mkdir()
    second.mkdir()
    (first / "source.bin").write_bytes(b"original")
    (second / "source.bin").write_bytes(b"original")
    linked = repo_root / "linked"
    try:
        linked.symlink_to(first, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    source = linked / "source.bin"
    displaced = first / "displaced.bin"

    def mutate_after_stage():
        if mutation == "same_size":
            (first / "source.bin").write_bytes(b"mutated!")
        elif mutation == "replace":
            (first / "source.bin").rename(displaced)
            (first / "source.bin").write_bytes(b"original")
        elif mutation == "unlink":
            (first / "source.bin").unlink()
        else:
            linked.unlink()
            linked.symlink_to(second, target_is_directory=True)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(stage_barrier=mutate_after_stage)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    destination = artifacts_dir / "formal.bin"
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "source_changed"
    assert captured.value.cleanup_state == _explicit_cleanup_state("removed")
    assert not destination.exists()


def test_explicit_copy_is_bounded_and_cross_filesystem_source_is_supported(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = (
        Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts" / "spec-dock"
    )
    if source.stat().st_dev == artifacts_dir.stat().st_dev:
        pytest.skip("no distinct source filesystem is available for this platform fixture")
    original_body = source.read_bytes()
    observed_read_sizes = []
    original_read = publisher_module.os.read

    def bounded_read(descriptor, size):
        observed_read_sizes.append(size)
        return original_read(descriptor, size)

    monkeypatch.setattr(publisher_module.os, "read", bounded_read)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher(chunk_size=7)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        result = publisher.publish_explicit_file(
            _explicit_publish_request(
                contracts,
                repo_root,
                guarded,
                artifacts_dir / "cross-filesystem.bin",
            )
        )
    finally:
        guarded.close()

    assert observed_read_sizes
    assert max(observed_read_sizes) <= 7
    assert result.destination_path.read_bytes() == original_body
    assert source.read_bytes() == original_body


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS named-stage capability probe contract")
def test_macos_explicit_publication_probes_no_replace_capability_before_formal_commit(tmp_path):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    points = []

    def inject(point):
        points.append(point)
        if point == "capability_probe":
            raise OSError("unsupported sentinel")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    destination = artifacts_dir / "formal.bin"
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "publication_unsupported"
    assert "capability_probe" in points
    assert not destination.exists()


def test_linux_explicit_import_uses_anonymous_staging_without_visible_probe_or_unlink(
    tmp_path,
    monkeypatch,
):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    original_open = publisher_module.os.open
    original_unlink = publisher_module.os.unlink
    original_stat = publisher_module.os.stat
    original_fsync = publisher_module.os.fsync
    anonymous_flag = 0x40000000
    anonymous_fd = None
    visible_stage_creates = []
    commit_names = []
    unlink_calls = []
    events = []

    monkeypatch.setattr(publisher_module.sys, "platform", "linux")
    monkeypatch.setattr(publisher_module.os, "O_TMPFILE", anonymous_flag, raising=False)

    def open_spy(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal anonymous_fd
        if path == "." and flags & anonymous_flag:
            events.append("anonymous_create")
            anonymous_fd = original_open(
                ".anonymous-stage-fixture",
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=dir_fd,
            )
            original_unlink(".anonymous-stage-fixture", dir_fd=dir_fd)
            return anonymous_fd
        if isinstance(path, str) and path.startswith(".spec-dock-import-"):
            visible_stage_creates.append(path)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    def stat_spy(path, *args, **kwargs):
        if anonymous_fd is not None and os.fspath(path) == f"/proc/self/fd/{anonymous_fd}":
            events.append("proc_reference")
            return os.fstat(anonymous_fd)
        return original_stat(path, *args, **kwargs)

    def commit_spy(source_fd, destination_parent_fd, destination_name):
        events.append(f"commit:{destination_name}")
        commit_names.append(destination_name)
        if destination_name.startswith(".spec-dock-import-"):
            raise FileExistsError(errno.EEXIST, "visible probe already exists", destination_name)
        output_fd = original_open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=destination_parent_fd,
        )
        try:
            os.lseek(source_fd, 0, os.SEEK_SET)
            while chunk := os.read(source_fd, 1024):
                os.write(output_fd, chunk)
        finally:
            os.close(output_fd)

    def unlink_spy(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        return original_unlink(*args, **kwargs)

    def fsync_spy(descriptor):
        if anonymous_fd is not None and descriptor != anonymous_fd:
            events.append("directory_durability")
        return original_fsync(descriptor)

    monkeypatch.setattr(publisher_module.os, "open", open_spy)
    monkeypatch.setattr(publisher_module.os, "stat", stat_spy)
    monkeypatch.setattr(publisher_module.os, "fsync", fsync_spy)
    monkeypatch.setattr(publisher_module, "_commit_descriptor_no_replace", commit_spy)
    monkeypatch.setattr(publisher_module.os, "unlink", unlink_spy)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        result = publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert result.committed is True
    assert result.cleanup_state == "not_created"
    assert result.warning_codes == ()
    assert destination.read_bytes() == b"source"
    assert visible_stage_creates == []
    assert commit_names == ["formal.bin"]
    assert unlink_calls == []
    assert events.index("anonymous_create") < events.index("proc_reference")
    assert events.index("proc_reference") < events.index("directory_durability")
    assert events.index("directory_durability") < events.index("commit:formal.bin")


@pytest.mark.parametrize(
    ("fault_point", "expected_code"),
    [
        ("write", "copy_failed"),
        ("formal_capability", "publication_unsupported"),
        ("formal_collision", "destination_exists"),
    ],
)
def test_linux_anonymous_precommit_failures_close_fd_without_pathname_cleanup(
    tmp_path,
    monkeypatch,
    fault_point,
    expected_code,
):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    anonymous_path = artifacts_dir / ".anonymous-stage-fixture"
    anonymous_fd = os.open(anonymous_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    anonymous_path.unlink()
    unlink_calls = []
    commit_names = []
    original_unlink = publisher_module.os.unlink

    monkeypatch.setattr(publisher_module.sys, "platform", "linux")
    monkeypatch.setattr(
        publisher_module.FilesystemBinaryArtifactPublisher,
        "_create_linux_anonymous_temp",
        lambda _self, _parent_fd: anonymous_fd,
    )

    def fail_or_collide(_source_fd, _destination_parent_fd, destination_name):
        commit_names.append(destination_name)
        if fault_point == "formal_collision":
            raise FileExistsError(errno.EEXIST, "collision", destination_name)
        raise OSError(errno.EPERM, "private capability sentinel")

    def inject(point):
        if fault_point == "write" and point == "write":
            raise OSError("private write sentinel")

    def unlink_spy(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        return original_unlink(*args, **kwargs)

    if fault_point != "write":
        monkeypatch.setattr(
            publisher_module,
            "_commit_descriptor_no_replace",
            fail_or_collide,
        )
    monkeypatch.setattr(publisher_module.os, "unlink", unlink_spy)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == expected_code
    assert captured.value.committed is False
    assert captured.value.cleanup_state == "not_created"
    assert not destination.exists()
    assert unlink_calls == []
    assert commit_names == ([] if fault_point == "write" else ["formal.bin"])
    with pytest.raises(OSError) as closed:
        os.fstat(anonymous_fd)
    assert closed.value.errno == errno.EBADF


def test_linux_missing_anonymous_staging_capability_fails_closed_without_named_fallback(
    tmp_path,
    monkeypatch,
):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    visible_stage_creates = []
    unlink_calls = []
    original_open = publisher_module.os.open
    original_unlink = publisher_module.os.unlink

    monkeypatch.setattr(publisher_module.sys, "platform", "linux")
    monkeypatch.delattr(publisher_module.os, "O_TMPFILE", raising=False)

    def open_spy(path, flags, mode=0o777, *, dir_fd=None):
        if isinstance(path, str) and path.startswith(".spec-dock-import-"):
            visible_stage_creates.append(path)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    def unlink_spy(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        return original_unlink(*args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "open", open_spy)
    monkeypatch.setattr(publisher_module.os, "unlink", unlink_spy)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "publication_unsupported"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == "not_created"
    assert not destination.exists()
    assert visible_stage_creates == []
    assert unlink_calls == []


@pytest.mark.parametrize("unavailable_preflight", ["proc_reference", "directory_durability"])
def test_linux_anonymous_preflight_capability_failure_closes_fd_and_fails_closed(
    tmp_path,
    monkeypatch,
    unavailable_preflight,
):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    original_open = publisher_module.os.open
    original_unlink = publisher_module.os.unlink
    original_stat = publisher_module.os.stat
    original_fsync = publisher_module.os.fsync
    anonymous_flag = 0x40000000
    anonymous_fd = None
    unlink_calls = []

    monkeypatch.setattr(publisher_module.sys, "platform", "linux")
    monkeypatch.setattr(publisher_module.os, "O_TMPFILE", anonymous_flag, raising=False)

    def open_spy(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal anonymous_fd
        if path == "." and flags & anonymous_flag:
            anonymous_fd = original_open(
                ".anonymous-stage-fixture",
                os.O_RDWR | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=dir_fd,
            )
            original_unlink(".anonymous-stage-fixture", dir_fd=dir_fd)
            return anonymous_fd
        return original_open(path, flags, mode, dir_fd=dir_fd)

    def stat_spy(path, *args, **kwargs):
        if anonymous_fd is not None and os.fspath(path) == f"/proc/self/fd/{anonymous_fd}":
            if unavailable_preflight == "proc_reference":
                raise OSError(errno.ENOENT, "private procfs sentinel")
            return os.fstat(anonymous_fd)
        return original_stat(path, *args, **kwargs)

    def fsync_spy(descriptor):
        if unavailable_preflight == "directory_durability" and descriptor != anonymous_fd:
            raise OSError(errno.EINVAL, "private directory fsync sentinel")
        return original_fsync(descriptor)

    def unlink_spy(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        return original_unlink(*args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "open", open_spy)
    monkeypatch.setattr(publisher_module.os, "stat", stat_spy)
    monkeypatch.setattr(publisher_module.os, "fsync", fsync_spy)
    monkeypatch.setattr(publisher_module.os, "unlink", unlink_spy)

    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "publication_unsupported"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == "not_created"
    assert not destination.exists()
    assert unlink_calls == []
    assert anonymous_fd is not None
    with pytest.raises(OSError) as closed:
        os.fstat(anonymous_fd)
    assert closed.value.errno == errno.EBADF


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux O_TMPFILE capability test")
def test_linux_anonymous_staging_publishes_on_supported_real_filesystem(tmp_path):
    contracts, publisher_module = _runtime_modules()
    if not hasattr(publisher_module.os, "O_TMPFILE"):
        pytest.skip("Python runtime does not expose O_TMPFILE")
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        try:
            result = publisher.publish_explicit_file(
                _explicit_publish_request(contracts, repo_root, guarded, destination)
            )
        except contracts.BinaryArtifactPublishError as error:
            if error.code == "publication_unsupported":
                pytest.skip("test filesystem does not support linkable O_TMPFILE publication")
            raise
    finally:
        guarded.close()

    assert result.committed is True
    assert result.cleanup_state == "not_created"
    assert result.warning_codes == ()
    assert destination.read_bytes() == b"source"
    assert not tuple(artifacts_dir.glob(".spec-dock-import-*"))


def test_explicit_capability_probe_never_unlinks_replacement_after_existing_check(tmp_path, monkeypatch):
    _contracts, publisher_module = _runtime_modules()
    _repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    replacement_body = b"unrelated replacement sentinel"
    replacement_source = artifacts_dir / "replacement-sentinel"
    replacement_source.write_bytes(replacement_body)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    parent_fd = os.open(artifacts_dir, os.O_RDONLY | os.O_DIRECTORY)
    temp_fd, temp_name = publisher._create_temp(parent_fd)
    os.write(temp_fd, b"owned staged bytes")
    temp_path = artifacts_dir / temp_name
    unlink_calls = []

    def inject(point):
        if point == "capability_probe_after_existing_check":
            replacement_source.replace(temp_path)

    def forbidden_unlink(*args, dir_fd=None):
        unlink_calls.append((args, dir_fd))
        raise AssertionError("capability probe must not unlink any pathname")

    publisher._fault_injector = inject
    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(publisher_module.os, "unlink", forbidden_unlink)
            publisher._probe_no_replace_capability(temp_fd, parent_fd, temp_name)
    finally:
        os.close(temp_fd)
        os.close(parent_fd)

    assert unlink_calls == []
    assert temp_path.read_bytes() == replacement_body
    temp_path.unlink()


def test_cleanup_missing_path_is_retained_and_never_reported_removed(tmp_path, monkeypatch):
    _contracts, publisher_module = _runtime_modules()
    _repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    parent_fd = os.open(artifacts_dir, os.O_RDONLY | os.O_DIRECTORY)
    temp_fd, temp_name = publisher._create_temp(parent_fd)
    os.unlink(temp_name, dir_fd=parent_fd)
    unlink_calls = []
    original_unlink = publisher_module.os.unlink

    def record_unlink(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        return original_unlink(*args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "unlink", record_unlink)
    try:
        cleanup_state = publisher._cleanup_temp(temp_name, temp_fd, parent_fd)
    finally:
        os.close(temp_fd)
        os.close(parent_fd)

    assert cleanup_state == "retained"
    assert unlink_calls == []


@pytest.mark.parametrize("uncertainty", ["replacement", "path_type", "descriptor_type"])
def test_cleanup_identity_or_type_uncertainty_retains_without_unlink(tmp_path, monkeypatch, uncertainty):
    _contracts, publisher_module = _runtime_modules()
    _repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    parent_fd = os.open(artifacts_dir, os.O_RDONLY | os.O_DIRECTORY)
    temp_fd, temp_name = publisher._create_temp(parent_fd)
    os.write(temp_fd, b"owned staged bytes")
    temp_path = artifacts_dir / temp_name
    displaced = artifacts_dir / f"{temp_name}.owned"
    original_stat = publisher_module.os.stat
    original_fstat = publisher_module.os.fstat
    unlink_calls = []

    if uncertainty == "replacement":
        temp_path.rename(displaced)
        temp_path.write_bytes(b"replacement sentinel")
    elif uncertainty == "path_type":
        held_status = original_fstat(temp_fd)

        def nonregular_path_status(path, *args, **kwargs):
            if path == temp_name and kwargs.get("dir_fd") == parent_fd:
                values = list(held_status)
                values[stat.ST_MODE] = stat.S_IFDIR | 0o700
                return os.stat_result(values)
            return original_stat(path, *args, **kwargs)

        monkeypatch.setattr(publisher_module.os, "stat", nonregular_path_status)
    else:
        held_status = original_fstat(temp_fd)

        def nonregular_descriptor_status(descriptor):
            if descriptor == temp_fd:
                values = list(held_status)
                values[stat.ST_MODE] = stat.S_IFDIR | 0o700
                return os.stat_result(values)
            return original_fstat(descriptor)

        monkeypatch.setattr(publisher_module.os, "fstat", nonregular_descriptor_status)

    def forbidden_unlink(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        raise AssertionError("cleanup must not unlink when ownership is uncertain")

    monkeypatch.setattr(publisher_module.os, "unlink", forbidden_unlink)
    try:
        cleanup_state = publisher._cleanup_temp(temp_name, temp_fd, parent_fd)
    finally:
        os.close(temp_fd)
        os.close(parent_fd)

    assert cleanup_state == "retained"
    assert unlink_calls == []
    assert temp_path.exists()
    if uncertainty == "replacement":
        assert temp_path.read_bytes() == b"replacement sentinel"
        assert displaced.read_bytes() == b"owned staged bytes"


@pytest.mark.parametrize("uncertainty", ["stat", "fstat", "open"])
def test_cleanup_observation_failure_retains_without_unlink(tmp_path, monkeypatch, uncertainty):
    _contracts, publisher_module = _runtime_modules()
    _repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    parent_fd = os.open(artifacts_dir, os.O_RDONLY | os.O_DIRECTORY)
    temp_fd, temp_name = publisher._create_temp(parent_fd)
    os.write(temp_fd, b"owned staged bytes")
    original_stat = publisher_module.os.stat
    original_fstat = publisher_module.os.fstat
    original_open = publisher_module.os.open
    observation_calls = []
    unlink_calls = []

    def fail_stat(path, *args, **kwargs):
        if path == temp_name and kwargs.get("dir_fd") == parent_fd:
            observation_calls.append("stat")
            raise OSError("private stat sentinel")
        return original_stat(path, *args, **kwargs)

    def fail_fstat(descriptor):
        if descriptor == temp_fd:
            observation_calls.append("fstat")
            raise OSError("private fstat sentinel")
        return original_fstat(descriptor)

    def fail_open(path, *args, **kwargs):
        if path == temp_name and kwargs.get("dir_fd") == parent_fd:
            observation_calls.append("open")
            raise OSError("private open sentinel")
        return original_open(path, *args, **kwargs)

    if uncertainty == "stat":
        monkeypatch.setattr(publisher_module.os, "stat", fail_stat)
    elif uncertainty == "fstat":
        monkeypatch.setattr(publisher_module.os, "fstat", fail_fstat)
    else:
        monkeypatch.setattr(publisher_module.os, "open", fail_open)

    def forbidden_unlink(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        raise AssertionError("cleanup must not unlink after observation failure")

    monkeypatch.setattr(publisher_module.os, "unlink", forbidden_unlink)
    try:
        cleanup_state = publisher._cleanup_temp(temp_name, temp_fd, parent_fd)
    finally:
        os.close(temp_fd)
        os.close(parent_fd)

    assert cleanup_state == "retained"
    assert observation_calls == [uncertainty]
    assert unlink_calls == []
    assert (artifacts_dir / temp_name).read_bytes() == b"owned staged bytes"


def test_cleanup_replacement_after_reopen_is_detected_by_final_path_check(tmp_path, monkeypatch):
    _contracts, publisher_module = _runtime_modules()
    _repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    parent_fd = os.open(artifacts_dir, os.O_RDONLY | os.O_DIRECTORY)
    temp_fd, temp_name = publisher._create_temp(parent_fd)
    os.write(temp_fd, b"owned staged bytes")
    temp_path = artifacts_dir / temp_name
    displaced = artifacts_dir / f"{temp_name}.owned"
    unlink_calls = []
    barrier_calls = 0

    def replace_after_reopen(point):
        nonlocal barrier_calls
        if point == "cleanup_before_final_path_check":
            barrier_calls += 1
            temp_path.rename(displaced)
            temp_path.write_bytes(b"replacement sentinel")

    def forbidden_unlink(*args, **kwargs):
        unlink_calls.append((args, kwargs))
        raise AssertionError("cleanup must not unlink a replacement detected by the final pathname check")

    publisher._fault_injector = replace_after_reopen
    monkeypatch.setattr(publisher_module.os, "unlink", forbidden_unlink)
    try:
        cleanup_state = publisher._cleanup_temp(temp_name, temp_fd, parent_fd)
    finally:
        os.close(temp_fd)
        os.close(parent_fd)

    assert barrier_calls == 1
    assert cleanup_state == "retained"
    assert unlink_calls == []
    assert temp_path.read_bytes() == b"replacement sentinel"
    assert displaced.read_bytes() == b"owned staged bytes"


@pytest.mark.parametrize("committed", [False, True])
def test_cleanup_missing_is_retained_for_precommit_and_postcommit_state(tmp_path, monkeypatch, committed):
    if sys.platform.startswith("linux"):
        pytest.skip("Linux explicit import uses anonymous staging without pathname cleanup")
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    original_stat = publisher_module.os.stat

    def missing_during_cleanup(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith(".spec-dock-import-") and kwargs.get("dir_fd") is not None:
            raise FileNotFoundError(path)
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(publisher_module.os, "stat", missing_during_cleanup)

    def inject(point):
        if not committed and point == "write":
            raise OSError("private precommit sentinel")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        if committed:
            result = publisher.publish_explicit_file(
                _explicit_publish_request(contracts, repo_root, guarded, destination)
            )
        else:
            with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
                publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    if committed:
        assert result.committed is True
        assert result.cleanup_state == "retained"
        assert result.warning_codes == ("temp_cleanup_retained",)
        assert destination.read_bytes() == b"source"
    else:
        assert captured.value.committed is False
        assert captured.value.cleanup_state == "retained"
        assert not destination.exists()


def test_explicit_destination_parent_identity_failure_is_precommit_and_no_publish(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    visible_checks = 0
    publish_calls = 0
    original_visible_matches = publisher_module._visible_directory_matches

    def fail_final_parent_identity(*args, **kwargs):
        nonlocal visible_checks
        visible_checks += 1
        if visible_checks == 1:
            return False
        return original_visible_matches(*args, **kwargs)

    def forbidden_publish(*args, **kwargs):
        nonlocal publish_calls
        publish_calls += 1
        raise AssertionError("formal publication must not run after parent mismatch")

    monkeypatch.setattr(publisher_module, "_visible_directory_matches", fail_final_parent_identity)
    monkeypatch.setattr(publisher, "_publish_no_replace", forbidden_publish)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "destination_ineligible"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == _explicit_cleanup_state("removed")
    assert visible_checks == 1
    assert publish_calls == 0
    assert not destination.exists()


def test_explicit_nonrace_publication_failure_is_precommit_and_no_formal_destination(tmp_path, monkeypatch):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    commit_calls = 0

    def fail_formal_commit(_source_fd, _destination_parent_fd, destination_name):
        nonlocal commit_calls
        commit_calls += 1
        if destination_name.startswith(".spec-dock-import-"):
            raise FileExistsError(errno.EEXIST, "owned stage already exists", destination_name)
        raise OSError(errno.EIO, "private publication sentinel")

    monkeypatch.setattr(publisher_module, "_commit_descriptor_no_replace", fail_formal_commit)
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == "publication_failed"
    assert captured.value.committed is False
    assert captured.value.cleanup_state == _explicit_cleanup_state("removed")
    assert commit_calls == (1 if sys.platform.startswith("linux") else 2)
    assert not destination.exists()


@pytest.mark.parametrize(
    ("fault_point", "expected_code", "expected_cleanup"),
    [
        ("temp_create", "temp_create_failed", "not_created"),
        ("write", "copy_failed", "removed"),
        ("file_fsync", "file_fsync_failed", "removed"),
        ("hash", "hash_failed", "removed"),
        ("publication_unsupported", "publication_unsupported", "removed"),
    ],
)
def test_explicit_precommit_faults_are_content_free_and_leave_no_formal_destination(
    tmp_path, fault_point, expected_code, expected_cleanup
):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "private-source.bin"
    source.write_bytes(b"private body hash count sentinel")

    def inject(point):
        if point == fault_point:
            raise OSError("private raw exception sentinel")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    destination = artifacts_dir / "formal.bin"
    try:
        with pytest.raises(contracts.BinaryArtifactPublishError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert captured.value.code == expected_code
    assert captured.value.cleanup_state == _explicit_cleanup_state(expected_cleanup)
    assert captured.value.committed is False
    assert not destination.exists()
    assert "private raw exception sentinel" not in str(captured.value)


@pytest.mark.parametrize("close_point", ["temp_fd_close", "destination_parent_fd_close"])
def test_explicit_postcommit_descriptor_close_failure_is_no_throw_without_public_warning(tmp_path, close_point):
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    observed_points = []

    def inject(point):
        observed_points.append(point)
        if point == close_point:
            raise OSError("close sentinel")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        result = publisher.publish_explicit_file(
            _explicit_publish_request(
                contracts,
                repo_root,
                guarded,
                artifacts_dir / "formal.bin",
            )
        )
    finally:
        guarded.close()

    assert result.committed is True
    assert result.warning_codes == ()
    assert result.destination_path.read_bytes() == b"source"
    assert close_point in observed_points


@pytest.mark.parametrize(
    ("fault_point", "expected_warning", "expected_cleanup"),
    [
        ("directory_fsync", "directory_fsync_failed", "removed"),
        ("cleanup", "temp_cleanup_retained", "retained"),
    ],
)
def test_explicit_postcommit_faults_return_exact_warning_and_committed_identity(
    tmp_path, fault_point, expected_warning, expected_cleanup
):
    if fault_point == "cleanup" and sys.platform.startswith("linux"):
        pytest.skip("Linux explicit import has no pathname cleanup seam")
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")

    def inject(point):
        if point == fault_point:
            raise OSError("postcommit sentinel")

    publisher = publisher_module.FilesystemBinaryArtifactPublisher(fault_injector=inject)
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    try:
        result = publisher.publish_explicit_file(
            _explicit_publish_request(
                contracts,
                repo_root,
                guarded,
                artifacts_dir / "formal.bin",
            )
        )
    finally:
        guarded.close()

    assert result.committed is True
    assert result.cleanup_state == _explicit_cleanup_state(expected_cleanup)
    assert result.warning_codes == (expected_warning,)
    assert result.destination_path.read_bytes() == b"source"


def test_unexpected_postcommit_oserror_is_not_misclassified_as_not_committed(tmp_path, monkeypatch):
    if sys.platform.startswith("linux"):
        pytest.skip("Linux explicit import has no pathname cleanup seam")
    contracts, publisher_module = _runtime_modules()
    repo_root, _specdock_dir, _scopes, artifacts_dir = _layout(tmp_path)
    source = repo_root / "source.bin"
    source.write_bytes(b"source")
    destination = artifacts_dir / "formal.bin"
    publisher = publisher_module.FilesystemBinaryArtifactPublisher()
    guarded = publisher.guard_explicit_file_source(_explicit_source_request(contracts, repo_root, source))
    monkeypatch.setattr(
        publisher,
        "_cleanup_temp",
        lambda *_args: (_ for _ in ()).throw(OSError("private postcommit sentinel")),
    )

    try:
        with pytest.raises(OSError) as captured:
            publisher.publish_explicit_file(_explicit_publish_request(contracts, repo_root, guarded, destination))
    finally:
        guarded.close()

    assert "private postcommit sentinel" in str(captured.value)
    assert destination.read_bytes() == b"source"


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
    assert hash_calls == 1
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
