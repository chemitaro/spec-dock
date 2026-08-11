from __future__ import annotations

import errno
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
