import os
from pathlib import Path
import sys

import pytest


def _runtime_fs_cli():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import fs_cli
    finally:
        sys.path.pop(0)
    return fs_cli


def _tree_snapshot(root: Path) -> dict[str, bytes | None]:
    return {
        str(path.relative_to(root)): None if path.is_dir() else path.read_bytes() for path in sorted(root.rglob("*"))
    }


def test_copy_workbench_recursively_merges_source_wins_and_is_idempotent(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    (source / "nested").mkdir(parents=True)
    (destination / "nested").mkdir(parents=True)
    (source / "source-only.txt").write_bytes(b"source only")
    (source / "same.txt").write_bytes(b"source version")
    (source / "nested" / "from-source.txt").write_bytes(b"nested source")
    (destination / "destination-only.txt").write_bytes(b"destination only")
    (destination / "same.txt").write_bytes(b"old destination")
    (destination / "nested" / "destination-only.txt").write_bytes(b"nested destination")

    fs_cli.copy_workbench(source, destination)

    assert (destination / "source-only.txt").read_bytes() == b"source only"
    assert (destination / "destination-only.txt").read_bytes() == b"destination only"
    assert (destination / "same.txt").read_bytes() == b"source version"
    assert (destination / "nested" / "from-source.txt").read_bytes() == b"nested source"
    assert (destination / "nested" / "destination-only.txt").read_bytes() == b"nested destination"
    (source / "same.txt").write_bytes(b"revised source version")

    fs_cli.copy_workbench(source, destination)

    assert (destination / "same.txt").read_bytes() == b"revised source version"
    second_snapshot = _tree_snapshot(destination)

    fs_cli.copy_workbench(source, destination)

    assert _tree_snapshot(destination) == second_snapshot


def test_copy_workbench_copies_opaque_ordinary_file_bytes_without_classification(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    payloads = {
        "binary.bin": b"\x00\xff\x80binary",
        "archive.zip": b"PK\x03\x04not-filtered",
        ".env": b"SECRET_TOKEN=opaque\n",
        "script.py": b"print('opaque')\n",
        "config.yaml": b"enabled: true\n",
        ".git/config": b"[core]\n\tbare = false\n",
    }
    source.mkdir()
    for relative, body in payloads.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)

    fs_cli.copy_workbench(source, destination)

    assert {relative: (destination / relative).read_bytes() for relative in payloads} == payloads


def test_copy_workbench_replaces_destination_symlink_leaf_without_touching_its_target(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external.txt"
    source.mkdir()
    destination.mkdir()
    external.write_bytes(b"external sentinel")
    (source / "same.txt").write_bytes(b"source bytes")
    try:
        (destination / "same.txt").symlink_to(external)
    except OSError:
        pytest.skip("symlink not available")

    fs_cli.copy_workbench(source, destination)

    assert not (destination / "same.txt").is_symlink()
    assert (destination / "same.txt").read_bytes() == b"source bytes"
    assert external.read_bytes() == b"external sentinel"


def test_copy_workbench_copies_broken_and_external_symlinks_as_link_objects(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external.txt"
    source.mkdir()
    external.write_bytes(b"external sentinel")
    broken_text = "../missing-target"
    external_text = str(external)
    try:
        (source / "broken-link").symlink_to(broken_text)
        (source / "external-link").symlink_to(external_text)
    except OSError:
        pytest.skip("symlink creation is not available on this host")

    fs_cli.copy_workbench(source, destination)

    assert (destination / "broken-link").is_symlink()
    assert (destination / "broken-link").readlink() == Path(broken_text)
    assert (destination / "external-link").is_symlink()
    assert (destination / "external-link").readlink() == Path(external_text)
    assert external.read_bytes() == b"external sentinel"


def test_copy_workbench_does_not_traverse_destination_symlink_as_a_directory(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    external.mkdir()
    (source / "nested" / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    try:
        (destination / "nested").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("symlink not available")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
    assert (destination / "nested").is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "source.txt").exists()


def test_destination_traversal_symlink_failure_after_first_copy_reports_mutation_started(
    tmp_path: Path,
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external"
    (source / "z-nested").mkdir(parents=True)
    destination.mkdir()
    external.mkdir()
    (source / "a-first.txt").write_bytes(b"first")
    (source / "z-nested" / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    try:
        (destination / "z-nested").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is not available on this host")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert (destination / "a-first.txt").read_bytes() == b"first"
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "source.txt").exists()


def test_copy_workbench_rejects_source_directory_identity_swap_without_external_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_source = tmp_path / "displaced-source"
    external = tmp_path / "external-source"
    source.mkdir()
    destination.mkdir()
    external.mkdir()
    (source / "safe.txt").write_bytes(b"safe source")
    sentinel = external / "external-secret.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open_directory = fs_cli._open_verified_directory
    swapped = False

    def swap_before_descriptor_acquisition(path: Path, expected) -> int:
        nonlocal swapped
        if path == source and not swapped:
            source.rename(displaced_source)
            try:
                source.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_source.rename(source)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_open_directory(path, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory", swap_before_descriptor_acquisition)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (destination / "external-secret.txt").exists()
    assert list(destination.iterdir()) == []


def test_copy_workbench_rejects_destination_directory_identity_swap_without_external_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_destination = tmp_path / "displaced-destination"
    external = tmp_path / "external-destination"
    source.mkdir()
    destination.mkdir()
    external.mkdir()
    (source / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open_directory = fs_cli._open_verified_directory
    swapped = False

    def swap_before_descriptor_acquisition(path: Path, expected) -> int:
        nonlocal swapped
        if path == destination and not swapped:
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_open_directory(path, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory", swap_before_descriptor_acquisition)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "source.txt").exists()


def test_copy_workbench_rejects_missing_destination_parent_swap_before_mkdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    target_parent = tmp_path / "target-parent"
    displaced_parent = tmp_path / "displaced-target-parent"
    external = tmp_path / "external-destination"
    destination = target_parent / ".workbench"
    source.mkdir()
    target_parent.mkdir()
    external.mkdir()
    (source / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open_directory = fs_cli._open_verified_directory
    swapped = False

    def swap_parent_before_descriptor_acquisition(path: Path, expected) -> int:
        nonlocal swapped
        if path == target_parent and not swapped:
            target_parent.rename(displaced_parent)
            try:
                target_parent.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_parent.rename(target_parent)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_open_directory(path, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory", swap_parent_before_descriptor_acquisition)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / ".workbench").exists()
    assert list(displaced_parent.iterdir()) == []


def test_copy_workbench_root_mkdir_stays_in_verified_parent_after_visible_parent_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    target_parent = tmp_path / "target-parent"
    displaced_parent = tmp_path / "displaced-target-parent"
    external = tmp_path / "external-destination"
    destination = target_parent / ".workbench"
    source.mkdir()
    target_parent.mkdir()
    external.mkdir()
    (source / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_mkdir = fs_cli.os.mkdir
    swapped = False

    def swap_parent_before_root_mkdir(path, *args, **kwargs):
        nonlocal swapped
        is_root_creation = path == destination or (path == destination.name and kwargs.get("dir_fd") is not None)
        if is_root_creation and not swapped:
            target_parent.rename(displaced_parent)
            try:
                target_parent.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_parent.rename(target_parent)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "mkdir", swap_parent_before_root_mkdir)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert target_parent.is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / ".workbench").exists()
    assert (displaced_parent / ".workbench" / "source.txt").read_bytes() == b"source"


def test_copy_workbench_root_mkdir_success_then_open_failure_reports_mutation_without_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    target_parent = tmp_path / "target-parent"
    destination = target_parent / ".workbench"
    source.mkdir()
    target_parent.mkdir()
    original_open_directory_at = fs_cli._open_verified_directory_at

    def fail_after_root_mkdir(parent_fd: int, name: str, expected) -> int:
        if name == destination.name:
            raise OSError("injected post-mkdir open failure")
        return original_open_directory_at(parent_fd, name, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory_at", fail_after_root_mkdir)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert destination.is_dir()


def test_copy_workbench_nested_mkdir_stays_in_held_parent_after_visible_parent_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_destination = tmp_path / "displaced-destination"
    external = tmp_path / "external-destination"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    external.mkdir()
    (source / "nested" / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_mkdir = fs_cli.os.mkdir
    swapped = False

    def swap_parent_before_nested_mkdir(path, *args, **kwargs):
        nonlocal swapped
        is_nested_creation = path == destination / "nested" or (path == "nested" and kwargs.get("dir_fd") is not None)
        if is_nested_creation and not swapped:
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "mkdir", swap_parent_before_nested_mkdir)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert destination.is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "nested").exists()
    assert (displaced_destination / "nested" / "source.txt").read_bytes() == b"source"


def test_copy_workbench_symlink_create_stays_in_held_parent_after_visible_parent_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_destination = tmp_path / "displaced-destination"
    external = tmp_path / "external-destination"
    source.mkdir()
    destination.mkdir()
    external.mkdir()
    try:
        (source / "link").symlink_to("source-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_symlink = fs_cli.os.symlink
    swapped = False

    def swap_parent_before_symlink_create(target, path, *args, **kwargs):
        nonlocal swapped
        is_destination_creation = path == destination / "link" or (path == "link" and kwargs.get("dir_fd") is not None)
        if is_destination_creation and not swapped:
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_symlink(target, path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "symlink", swap_parent_before_symlink_create)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert destination.is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "link").exists()
    assert (displaced_destination / "link").readlink() == Path("source-target")


def test_copy_workbench_source_readlink_uses_held_parent_after_visible_parent_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    displaced_source = tmp_path / "displaced-source"
    replacement_source = tmp_path / "replacement-source"
    destination = tmp_path / "destination"
    source.mkdir()
    replacement_source.mkdir()
    destination.mkdir()
    try:
        (source / "link").symlink_to("original-target")
        (replacement_source / "link").symlink_to("replacement-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    original_readlink = fs_cli.os.readlink
    swapped = False

    def swap_source_before_readlink(path, *args, **kwargs):
        nonlocal swapped
        is_source_read = path == source / "link" or (path == "link" and kwargs.get("dir_fd") is not None)
        if is_source_read and not swapped:
            source.rename(displaced_source)
            replacement_source.rename(source)
            swapped = True
        return original_readlink(path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "readlink", swap_source_before_readlink)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert (destination / "link").readlink() == Path("original-target")


def test_copy_workbench_rejects_created_directory_replaced_with_symlink_without_external_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_nested = tmp_path / "displaced-nested"
    external = tmp_path / "external"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    external.mkdir()
    (source / "nested" / "source.txt").write_bytes(b"source")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open_directory_at = fs_cli._open_verified_directory_at
    destination_identity = (destination.stat().st_dev, destination.stat().st_ino)
    swapped = False

    def swap_created_directory_before_open(parent_fd: int, name: str, expected) -> int:
        nonlocal swapped
        parent_status = os.fstat(parent_fd)
        is_destination_child = (parent_status.st_dev, parent_status.st_ino) == destination_identity
        if is_destination_child and name == "nested" and not swapped:
            (destination / "nested").rename(displaced_nested)
            try:
                (destination / "nested").symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_nested.rename(destination / "nested")
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_open_directory_at(parent_fd, name, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory_at", swap_created_directory_before_open)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is True
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "source.txt").exists()


def test_copy_workbench_rejects_source_child_directory_swap_before_destination_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_nested = tmp_path / "displaced-source-nested"
    external = tmp_path / "external"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    external.mkdir()
    (source / "nested" / "safe.txt").write_bytes(b"safe")
    (external / "secret.txt").write_bytes(b"external sentinel")
    original_open_directory_at = fs_cli._open_verified_directory_at
    source_identity = (source.stat().st_dev, source.stat().st_ino)
    swapped = False

    def swap_source_child_before_open(parent_fd: int, name: str, expected) -> int:
        nonlocal swapped
        parent_status = os.fstat(parent_fd)
        is_source_child = (parent_status.st_dev, parent_status.st_ino) == source_identity
        if is_source_child and name == "nested" and not swapped:
            (source / "nested").rename(displaced_nested)
            try:
                (source / "nested").symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_nested.rename(source / "nested")
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_open_directory_at(parent_fd, name, expected)

    monkeypatch.setattr(fs_cli, "_open_verified_directory_at", swap_source_child_before_open)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert list(destination.iterdir()) == []


def test_copy_workbench_existing_nested_destination_frame_stays_on_opened_child_after_visible_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_nested = tmp_path / "displaced-destination-nested"
    external = tmp_path / "external"
    (source / "nested" / "created").mkdir(parents=True)
    (destination / "nested").mkdir(parents=True)
    external.mkdir()
    (source / "nested" / "file.txt").write_bytes(b"original file")
    (source / "nested" / "created" / "deep.txt").write_bytes(b"deep original")
    (destination / "nested" / "destination-only.txt").write_bytes(b"destination only")
    try:
        (source / "nested" / "link").symlink_to("original-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open_directory_at = fs_cli._open_verified_directory_at
    destination_identity = (destination.stat().st_dev, destination.stat().st_ino)
    swapped = False

    def swap_after_destination_child_open(parent_fd: int, name: str, expected) -> int:
        nonlocal swapped
        descriptor = original_open_directory_at(parent_fd, name, expected)
        parent_status = os.fstat(parent_fd)
        is_destination_child = (parent_status.st_dev, parent_status.st_ino) == destination_identity
        if is_destination_child and name == "nested" and not swapped:
            (destination / "nested").rename(displaced_nested)
            try:
                (destination / "nested").symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_nested.rename(destination / "nested")
                os.close(descriptor)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return descriptor

    monkeypatch.setattr(fs_cli, "_open_verified_directory_at", swap_after_destination_child_open)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert destination.is_dir()
    assert (destination / "nested").is_symlink()
    assert _tree_snapshot(external) == {"sentinel.txt": b"external sentinel"}
    assert (displaced_nested / "file.txt").read_bytes() == b"original file"
    assert (displaced_nested / "link").readlink() == Path("original-target")
    assert (displaced_nested / "created" / "deep.txt").read_bytes() == b"deep original"
    assert (displaced_nested / "destination-only.txt").read_bytes() == b"destination only"


def test_copy_workbench_nested_source_frame_reads_opened_child_after_visible_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_nested = tmp_path / "displaced-source-nested"
    replacement_nested = tmp_path / "replacement-source-nested"
    (source / "nested" / "child").mkdir(parents=True)
    replacement_nested.mkdir()
    destination.mkdir()
    (source / "nested" / "original.txt").write_bytes(b"original file")
    (source / "nested" / "child" / "deep.txt").write_bytes(b"deep original")
    (replacement_nested / "replacement.txt").write_bytes(b"replacement file")
    try:
        (source / "nested" / "link").symlink_to("original-target")
        (replacement_nested / "link").symlink_to("replacement-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    original_open_directory_at = fs_cli._open_verified_directory_at
    source_identity = (source.stat().st_dev, source.stat().st_ino)
    swapped = False

    def replace_after_source_child_open(parent_fd: int, name: str, expected) -> int:
        nonlocal swapped
        descriptor = original_open_directory_at(parent_fd, name, expected)
        parent_status = os.fstat(parent_fd)
        is_source_child = (parent_status.st_dev, parent_status.st_ino) == source_identity
        if is_source_child and name == "nested" and not swapped:
            (source / "nested").rename(displaced_nested)
            replacement_nested.rename(source / "nested")
            swapped = True
        return descriptor

    monkeypatch.setattr(fs_cli, "_open_verified_directory_at", replace_after_source_child_open)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert (destination / "nested" / "original.txt").read_bytes() == b"original file"
    assert (destination / "nested" / "link").readlink() == Path("original-target")
    assert (destination / "nested" / "child" / "deep.txt").read_bytes() == b"deep original"
    assert not (destination / "nested" / "replacement.txt").exists()


def test_copy_workbench_rejects_source_symlink_swap_after_readlink_before_destination_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_link = tmp_path / "displaced-link"
    source.mkdir()
    destination.mkdir()
    try:
        (source / "link").symlink_to("original-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    original_readlink = fs_cli.os.readlink
    swapped = False

    def swap_link_after_read(path, *args, **kwargs):
        nonlocal swapped
        target = original_readlink(path, *args, **kwargs)
        if path == "link" and kwargs.get("dir_fd") is not None and not swapped:
            (source / "link").rename(displaced_link)
            (source / "link").symlink_to("replacement-target")
            swapped = True
        return target

    monkeypatch.setattr(fs_cli.os, "readlink", swap_link_after_read)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert not (destination / "link").exists()


@pytest.mark.parametrize(
    "capability",
    ["_WORKBENCH_DIR_FD_SUPPORTED", "_WORKBENCH_FD_INSPECTION_SUPPORTED"],
)
def test_copy_workbench_fails_closed_before_mutation_when_descriptor_capability_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capability: str
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "source.txt").write_bytes(b"source")
    monkeypatch.setattr(fs_cli, capability, False)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
    assert not destination.exists()


@pytest.mark.parametrize("inject_copy_failure", [False, True])
def test_copy_workbench_closes_each_opened_descriptor_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    inject_copy_failure: bool,
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    (source / "nested" / "source.txt").write_bytes(b"source")
    original_open = fs_cli.os.open
    original_close = fs_cli.os.close
    original_copy = fs_cli._copy_descriptor_bytes
    active: set[int] = set()
    open_count = 0
    close_count = 0

    def tracked_open(*args, **kwargs) -> int:
        nonlocal open_count
        descriptor = original_open(*args, **kwargs)
        assert descriptor not in active
        active.add(descriptor)
        open_count += 1
        return descriptor

    def tracked_close(descriptor: int) -> None:
        nonlocal close_count
        assert descriptor in active
        active.remove(descriptor)
        close_count += 1
        original_close(descriptor)

    def maybe_fail_copy(source_fd: int, destination_fd: int) -> None:
        if inject_copy_failure:
            raise OSError("injected copy failure")
        original_copy(source_fd, destination_fd)

    monkeypatch.setattr(fs_cli.os, "open", tracked_open)
    monkeypatch.setattr(fs_cli.os, "close", tracked_close)
    monkeypatch.setattr(fs_cli, "_copy_descriptor_bytes", maybe_fail_copy)

    if inject_copy_failure:
        with pytest.raises(RuntimeError):
            fs_cli.copy_workbench(source, destination)
    else:
        fs_cli.copy_workbench(source, destination)

    assert active == set()
    assert close_count == open_count


def test_copy_workbench_rejects_nested_destination_leaf_swap_before_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    nested_destination = destination / "nested"
    displaced_leaf = tmp_path / "displaced-leaf"
    external = tmp_path / "external-sentinel.txt"
    (source / "nested").mkdir(parents=True)
    nested_destination.mkdir(parents=True)
    (source / "nested" / "same.txt").write_bytes(b"source")
    (nested_destination / "same.txt").write_bytes(b"old destination")
    external.write_bytes(b"external sentinel")
    original_unlink = fs_cli._unlink_verified_entry_at
    swapped = False

    def swap_nested_leaf_at_mutation_boundary(parent_fd: int, name: str, expected) -> None:
        nonlocal swapped
        if name == "same.txt" and not swapped:
            destination_leaf = nested_destination / "same.txt"
            destination_leaf.rename(displaced_leaf)
            try:
                destination_leaf.symlink_to(external)
            except OSError:
                displaced_leaf.rename(destination_leaf)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        original_unlink(parent_fd, name, expected)

    monkeypatch.setattr(fs_cli, "_unlink_verified_entry_at", swap_nested_leaf_at_mutation_boundary)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert external.read_bytes() == b"external sentinel"
    assert displaced_leaf.read_bytes() == b"old destination"


def test_copy_workbench_keeps_destination_parent_fd_after_symlink_read_path_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_destination = tmp_path / "displaced-destination"
    external = tmp_path / "external-destination"
    source.mkdir()
    destination.mkdir()
    external.mkdir()
    try:
        (source / "link").symlink_to("target-text")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_readlink = fs_cli._read_verified_symlink_at
    swapped = False

    def swap_parent_during_symlink_read(parent_fd: int, name: str, expected) -> str:
        nonlocal swapped
        result = original_readlink(parent_fd, name, expected)
        if name == "link":
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return result

    monkeypatch.setattr(fs_cli, "_read_verified_symlink_at", swap_parent_during_symlink_read)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "link").exists()
    assert (displaced_destination / "link").readlink() == Path("target-text")


@pytest.mark.parametrize("source_kind", ["symlink"])
def test_copy_workbench_rejects_missing_leaf_that_appears_before_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_kind: str,
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external-sentinel.txt"
    source.mkdir()
    destination.mkdir()
    external.write_bytes(b"external sentinel")
    source_leaf = source / "leaf"
    destination_leaf = destination / "leaf"
    try:
        if source_kind == "file":
            source_leaf.write_bytes(b"source bytes")
        else:
            source_leaf.symlink_to("source-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    original_assert_path_missing = fs_cli._assert_fd_path_missing
    inserted = False

    def insert_leaf_before_missing_assertion(parent_fd: int, name: str) -> None:
        nonlocal inserted
        if name == destination_leaf.name and not inserted:
            try:
                destination_leaf.symlink_to(external)
            except OSError:
                pytest.skip("symlink creation is not available on this host")
            inserted = True
        original_assert_path_missing(parent_fd, name)

    monkeypatch.setattr(fs_cli, "_assert_fd_path_missing", insert_leaf_before_missing_assertion)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert destination_leaf.is_symlink()
    assert destination_leaf.readlink() == external
    assert external.read_bytes() == b"external sentinel"


@pytest.mark.parametrize("source_kind", ["symlink"])
def test_copy_workbench_rejects_leaf_inserted_after_destination_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_kind: str,
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external-sentinel.txt"
    source.mkdir()
    destination.mkdir()
    external.write_bytes(b"external sentinel")
    source_leaf = source / "leaf"
    try:
        if source_kind == "file":
            source_leaf.write_bytes(b"source bytes")
        else:
            source_leaf.symlink_to("source-target")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    destination_leaf = destination / "leaf"
    destination_leaf.write_bytes(b"old destination bytes")
    original_assert_path_missing = fs_cli._assert_fd_path_missing
    inserted = False

    def insert_leaf_after_unlink(parent_fd: int, name: str) -> None:
        nonlocal inserted
        if name == destination_leaf.name and not inserted:
            assert not destination_leaf.exists()
            try:
                destination_leaf.symlink_to(external)
            except OSError:
                pytest.skip("symlink creation is not available on this host")
            inserted = True
        original_assert_path_missing(parent_fd, name)

    monkeypatch.setattr(fs_cli, "_assert_fd_path_missing", insert_leaf_after_unlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is True
    assert destination_leaf.is_symlink()
    assert destination_leaf.readlink() == external
    assert external.read_bytes() == b"external sentinel"


def test_copy_workbench_regular_file_rejects_symlink_inserted_before_exclusive_create(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external-sentinel.txt"
    source.mkdir()
    destination.mkdir()
    (source / "leaf").write_bytes(b"source bytes")
    external.write_bytes(b"external sentinel")
    destination_leaf = destination / "leaf"
    original_open = fs_cli._open_exclusive_regular_file
    inserted = False

    def insert_symlink(parent_fd: int, name: str) -> int:
        nonlocal inserted
        try:
            destination_leaf.symlink_to(external)
        except OSError:
            pytest.skip("symlink creation is not available on this host")
        inserted = True
        return original_open(parent_fd, name)

    monkeypatch.setattr(fs_cli, "_open_exclusive_regular_file", insert_symlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert destination_leaf.is_symlink()
    assert external.read_bytes() == b"external sentinel"
    assert (source / "leaf").read_bytes() == b"source bytes"


def test_copy_workbench_regular_file_rejects_symlink_inserted_after_fd_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    external = tmp_path / "external-sentinel.txt"
    source.mkdir()
    destination.mkdir()
    (source / "leaf").write_bytes(b"source bytes")
    destination_leaf = destination / "leaf"
    destination_leaf.write_bytes(b"old destination bytes")
    external.write_bytes(b"external sentinel")
    original_open = fs_cli._open_exclusive_regular_file
    inserted = False

    def insert_symlink(parent_fd: int, name: str) -> int:
        nonlocal inserted
        assert not destination_leaf.exists()
        try:
            destination_leaf.symlink_to(external)
        except OSError:
            pytest.skip("symlink creation is not available on this host")
        inserted = True
        return original_open(parent_fd, name)

    monkeypatch.setattr(fs_cli, "_open_exclusive_regular_file", insert_symlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is True
    assert destination_leaf.is_symlink()
    assert external.read_bytes() == b"external sentinel"


def test_copy_workbench_regular_file_keeps_verified_parent_fd_after_path_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    displaced_destination = tmp_path / "displaced-destination"
    external = tmp_path / "external"
    source.mkdir()
    destination.mkdir()
    external.mkdir()
    (source / "leaf").write_bytes(b"source bytes")
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    original_open = fs_cli._open_exclusive_regular_file
    swapped = False

    def swap_parent(parent_fd: int, name: str) -> int:
        nonlocal swapped
        destination.rename(displaced_destination)
        try:
            destination.symlink_to(external, target_is_directory=True)
        except OSError:
            displaced_destination.rename(destination)
            pytest.skip("symlink creation is not available on this host")
        swapped = True
        return original_open(parent_fd, name)

    monkeypatch.setattr(fs_cli, "_open_exclusive_regular_file", swap_parent)

    fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert destination.is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert sorted(path.name for path in external.iterdir()) == ["sentinel.txt"]
    assert (displaced_destination / "leaf").read_bytes() == b"source bytes"


def test_copy_workbench_regular_file_preserves_bytes_mode_and_mtime(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    source_leaf = source / "leaf"
    destination_leaf = destination / "leaf"
    source_leaf.write_bytes(b"\x00opaque source bytes\xff")
    source_leaf.chmod(0o640)
    fixed_mtime_ns = 1_700_000_000_123_456_789
    os.utime(source_leaf, ns=(fixed_mtime_ns, fixed_mtime_ns))

    fs_cli.copy_workbench(source, destination)

    source_status = source_leaf.stat()
    destination_status = destination_leaf.stat()
    assert destination_leaf.read_bytes() == source_leaf.read_bytes()
    assert destination_status.st_mode & 0o777 == source_status.st_mode & 0o777 == 0o640
    assert destination_status.st_mtime_ns == source_status.st_mtime_ns


@pytest.mark.parametrize("source_kind", ["directory", "file"])
def test_copy_workbench_type_collision_fails_without_removing_destination_data(
    tmp_path: Path, source_kind: str
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    collision_source = source / "collision"
    collision_destination = destination / "collision"
    if source_kind == "directory":
        collision_source.mkdir()
        (collision_source / "source.txt").write_bytes(b"source")
        collision_destination.write_bytes(b"destination leaf")
    else:
        collision_source.write_bytes(b"source leaf")
        collision_destination.mkdir()
        (collision_destination / "sentinel.txt").write_bytes(b"destination subtree")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
    if source_kind == "directory":
        assert collision_destination.read_bytes() == b"destination leaf"
    else:
        assert (collision_destination / "sentinel.txt").read_bytes() == b"destination subtree"


def test_copy_workbench_empty_source_creates_empty_destination(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()

    fs_cli.copy_workbench(source, destination)

    assert destination.is_dir()
    assert list(destination.iterdir()) == []


def test_copy_workbench_unsupported_special_entry_fails_instead_of_skipping(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO creation not available")
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    sentinel = destination / "sentinel.txt"
    sentinel.write_bytes(b"destination")
    os.mkfifo(source / "special")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"destination"


@pytest.mark.parametrize("linked_component", ["repo", "spec-dock", "scope", ".workbench"])
def test_guard_workbench_ancestry_rejects_each_symlink_component_without_touching_external(
    tmp_path: Path, linked_component: str
) -> None:
    fs_cli = _runtime_fs_cli()
    real_repo = tmp_path / "real-repo"
    repo = tmp_path / "repo"
    external = tmp_path / "external"
    real_repo.mkdir()
    external.mkdir()
    sentinel = external / "sentinel.txt"
    sentinel.write_bytes(b"external sentinel")
    try:
        if linked_component == "repo":
            repo.symlink_to(real_repo, target_is_directory=True)
            endpoint = repo / "spec-dock" / "scope" / ".workbench"
        else:
            repo.mkdir()
            current = repo
            for component in ("spec-dock", "scope", ".workbench"):
                next_path = current / component
                if component == linked_component:
                    next_path.symlink_to(external, target_is_directory=True)
                    current = next_path
                    break
                next_path.mkdir()
                current = next_path
            endpoint = repo / "spec-dock" / "scope" / ".workbench"
    except OSError:
        pytest.skip("symlink creation is not available on this host")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.guard_workbench_ancestry(repo, endpoint, allow_missing_leaf=False)

    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"


def test_guard_workbench_ancestry_rejects_lexical_escape_before_external_inspection(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    repo = tmp_path / "repo"
    repo.mkdir()
    endpoint = repo / ".." / "external" / ".workbench"

    with pytest.raises(RuntimeError) as captured:
        fs_cli.guard_workbench_ancestry(repo, endpoint, allow_missing_leaf=True)

    assert getattr(captured.value, "mutation_started", None) is False


@pytest.mark.parametrize("meta_parent", ["initiatives-root", "unexpected-directory"])
def test_guard_workbench_inventory_rejects_metadata_symlink_anywhere_without_reading_target(
    tmp_path: Path, meta_parent: str
) -> None:
    fs_cli = _runtime_fs_cli()
    initiatives = tmp_path / "spec-dock" / "initiatives"
    initiatives.mkdir(parents=True)
    parent = initiatives if meta_parent == "initiatives-root" else initiatives / "misc"
    parent.mkdir(exist_ok=True)
    external = tmp_path / f"external-{meta_parent}.json"
    external.write_bytes(b"external sentinel")
    try:
        (parent / ".meta.json").symlink_to(external)
    except OSError:
        pytest.skip("symlink creation is not available on this host")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.guard_workbench_inventory(tmp_path / "spec-dock")

    assert getattr(captured.value, "mutation_started", None) is False
    assert external.read_bytes() == b"external sentinel"


def test_guard_workbench_inventory_prunes_exact_workbench_but_traverses_near_name(tmp_path: Path) -> None:
    fs_cli = _runtime_fs_cli()
    initiatives = tmp_path / "spec-dock" / "initiatives"
    ignored = initiatives / ".workbench"
    traversed = initiatives / ".workbench-notes"
    ignored.mkdir(parents=True)
    traversed.mkdir()
    external = tmp_path / "external.json"
    external.write_bytes(b"external sentinel")
    try:
        (ignored / ".meta.json").symlink_to(external)
        (traversed / ".meta.json").symlink_to(external)
    except OSError:
        pytest.skip("symlink creation is not available on this host")

    with pytest.raises(RuntimeError) as captured:
        fs_cli.guard_workbench_inventory(tmp_path / "spec-dock")

    assert getattr(captured.value, "mutation_started", None) is False
    assert external.read_bytes() == b"external sentinel"


def test_copy_workbench_mid_copy_fault_reports_mutation_started_without_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "a-first.txt").write_bytes(b"first")
    (source / "b-secret.txt").write_bytes(b"secret body")
    original_copy = fs_cli._copy_descriptor_bytes
    copy_count = 0

    def injected_copy(source_fd: int, destination_fd: int) -> None:
        nonlocal copy_count
        copy_count += 1
        if copy_count == 2:
            raise OSError("raw secret body must not escape")
        original_copy(source_fd, destination_fd)

    monkeypatch.setattr(fs_cli, "_copy_descriptor_bytes", injected_copy)

    with pytest.raises(Exception) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert "raw secret body" not in str(captured.value)
    assert (destination / "a-first.txt").read_bytes() == b"first"
    assert (destination / "b-secret.txt").read_bytes() == b""


def test_copy_workbench_failed_destination_mkdir_reports_no_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    original_mkdir = fs_cli.os.mkdir

    def injected_mkdir(path, *args, **kwargs):
        if path == destination.name and kwargs.get("dir_fd") is not None:
            raise OSError("injected mkdir failure")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "mkdir", injected_mkdir)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False


def test_copy_workbench_failed_unlink_reports_no_mutation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "same.txt").write_bytes(b"source")
    destination_entry = destination / "same.txt"
    destination_entry.write_bytes(b"destination")
    original_unlink = fs_cli.os.unlink

    def injected_unlink(path, *args, **kwargs):
        if path == destination_entry.name and kwargs.get("dir_fd") is not None:
            raise OSError("injected unlink failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "unlink", injected_unlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
    assert destination_entry.read_bytes() == b"destination"


def test_copy_workbench_failure_after_successful_removal_reports_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "same.txt").write_bytes(b"source")
    destination_entry = destination / "same.txt"
    destination_entry.write_bytes(b"destination")

    def injected_copy(*_args, **_kwargs):
        raise OSError("injected copy failure")

    monkeypatch.setattr(fs_cli, "_copy_descriptor_bytes", injected_copy)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert destination_entry.read_bytes() == b""


def test_copy_workbench_failed_symlink_creation_reports_no_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    source_link = source / "link"
    try:
        source_link.symlink_to("missing")
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    destination_link = destination / "link"
    original_symlink = fs_cli.os.symlink

    def injected_symlink(target, path, *args, **kwargs):
        if path == destination_link.name and kwargs.get("dir_fd") is not None:
            raise OSError("injected symlink failure")
        return original_symlink(target, path, *args, **kwargs)

    monkeypatch.setattr(fs_cli.os, "symlink", injected_symlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
