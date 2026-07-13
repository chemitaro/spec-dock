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
    path_type = type(source)
    original_lstat = path_type.lstat
    source_inspections = 0
    swapped = False

    def swap_before_revalidation(path, *args, **kwargs):
        nonlocal source_inspections, swapped
        if path == source:
            source_inspections += 1
        if path == source and source_inspections == 2:
            source.rename(displaced_source)
            try:
                source.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_source.rename(source)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "lstat", swap_before_revalidation)

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
    path_type = type(destination)
    original_lstat = path_type.lstat
    destination_inspections = 0
    swapped = False

    def swap_before_revalidation(path, *args, **kwargs):
        nonlocal destination_inspections, swapped
        if path == destination:
            destination_inspections += 1
        if path == destination and destination_inspections == 3:
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "lstat", swap_before_revalidation)

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
    path_type = type(target_parent)
    original_lstat = path_type.lstat
    parent_inspections = 0
    swapped = False

    def swap_parent_before_mkdir_revalidation(path, *args, **kwargs):
        nonlocal parent_inspections, swapped
        if path == target_parent:
            parent_inspections += 1
        if path == target_parent and parent_inspections == 2:
            target_parent.rename(displaced_parent)
            try:
                target_parent.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_parent.rename(target_parent)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "lstat", swap_parent_before_mkdir_revalidation)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / ".workbench").exists()
    assert list(displaced_parent.iterdir()) == []


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
    path_type = type(nested_destination)
    original_lstat = path_type.lstat
    nested_inspections = 0
    swapped = False

    def swap_nested_leaf_at_mutation_boundary(path, *args, **kwargs):
        nonlocal nested_inspections, swapped
        if path == nested_destination:
            nested_inspections += 1
        if path == nested_destination and nested_inspections == 7:
            destination_leaf = nested_destination / "same.txt"
            destination_leaf.rename(displaced_leaf)
            try:
                destination_leaf.symlink_to(external)
            except OSError:
                displaced_leaf.rename(destination_leaf)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return original_lstat(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "lstat", swap_nested_leaf_at_mutation_boundary)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert external.read_bytes() == b"external sentinel"
    assert displaced_leaf.read_bytes() == b"old destination"


def test_copy_workbench_rejects_destination_parent_swap_after_symlink_read(
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
    path_type = type(destination)
    original_readlink = path_type.readlink
    swapped = False

    def swap_parent_during_symlink_read(path, *args, **kwargs):
        nonlocal swapped
        result = original_readlink(path, *args, **kwargs)
        if path == source / "link":
            destination.rename(displaced_destination)
            try:
                destination.symlink_to(external, target_is_directory=True)
            except OSError:
                displaced_destination.rename(destination)
                pytest.skip("symlink creation is not available on this host")
            swapped = True
        return result

    monkeypatch.setattr(path_type, "readlink", swap_parent_during_symlink_read)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert swapped is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert sentinel.read_bytes() == b"external sentinel"
    assert not (external / "link").exists()


@pytest.mark.parametrize("source_kind", ["file", "symlink"])
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
    original_assert_path_missing = fs_cli._assert_path_missing
    inserted = False

    def insert_leaf_before_missing_assertion(path: Path) -> None:
        nonlocal inserted
        if path == destination_leaf and not inserted:
            try:
                path.symlink_to(external)
            except OSError:
                pytest.skip("symlink creation is not available on this host")
            inserted = True
        original_assert_path_missing(path)

    monkeypatch.setattr(fs_cli, "_assert_path_missing", insert_leaf_before_missing_assertion)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is False
    assert destination_leaf.is_symlink()
    assert destination_leaf.readlink() == external
    assert external.read_bytes() == b"external sentinel"


@pytest.mark.parametrize("source_kind", ["file", "symlink"])
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
    original_assert_path_missing = fs_cli._assert_path_missing
    inserted = False

    def insert_leaf_after_unlink(path: Path) -> None:
        nonlocal inserted
        if path == destination_leaf and not inserted:
            assert not path.exists()
            try:
                path.symlink_to(external)
            except OSError:
                pytest.skip("symlink creation is not available on this host")
            inserted = True
        original_assert_path_missing(path)

    monkeypatch.setattr(fs_cli, "_assert_path_missing", insert_leaf_after_unlink)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert inserted is True
    assert getattr(captured.value, "mutation_started", None) is True
    assert destination_leaf.is_symlink()
    assert destination_leaf.readlink() == external
    assert external.read_bytes() == b"external sentinel"


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
    original_copy2 = fs_cli.shutil.copy2

    def injected_copy2(source_path, destination_path, *, follow_symlinks):
        if Path(source_path).name == "b-secret.txt":
            raise OSError("raw secret body must not escape")
        return original_copy2(source_path, destination_path, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(fs_cli.shutil, "copy2", injected_copy2)

    with pytest.raises(Exception) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert "raw secret body" not in str(captured.value)
    assert (destination / "a-first.txt").read_bytes() == b"first"
    assert not (destination / "b-secret.txt").exists()


def test_copy_workbench_failed_destination_mkdir_reports_no_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fs_cli = _runtime_fs_cli()
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    path_type = type(destination)
    original_mkdir = path_type.mkdir

    def injected_mkdir(path, *args, **kwargs):
        if path == destination:
            raise OSError("injected mkdir failure")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "mkdir", injected_mkdir)

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
    path_type = type(destination_entry)
    original_unlink = path_type.unlink

    def injected_unlink(path, *args, **kwargs):
        if path == destination_entry:
            raise OSError("injected unlink failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "unlink", injected_unlink)

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

    def injected_copy2(*_args, **_kwargs):
        raise OSError("injected copy failure")

    monkeypatch.setattr(fs_cli.shutil, "copy2", injected_copy2)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is True
    assert not destination_entry.exists()


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
    path_type = type(destination_link)
    original_symlink_to = path_type.symlink_to

    def injected_symlink_to(path, target, *args, **kwargs):
        if path == destination_link:
            raise OSError("injected symlink failure")
        return original_symlink_to(path, target, *args, **kwargs)

    monkeypatch.setattr(path_type, "symlink_to", injected_symlink_to)

    with pytest.raises(RuntimeError) as captured:
        fs_cli.copy_workbench(source, destination)

    assert getattr(captured.value, "mutation_started", None) is False
