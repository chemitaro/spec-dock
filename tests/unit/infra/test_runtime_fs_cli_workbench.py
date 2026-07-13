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

    with pytest.raises(RuntimeError, match="type collision"):
        fs_cli.copy_workbench(source, destination)

    assert (destination / "nested").is_symlink()
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "source.txt").exists()


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

    with pytest.raises(RuntimeError, match="type collision"):
        fs_cli.copy_workbench(source, destination)

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

    with pytest.raises(RuntimeError, match="unsupported"):
        fs_cli.copy_workbench(source, destination)

    assert sentinel.read_bytes() == b"destination"
