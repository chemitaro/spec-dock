from __future__ import annotations

import errno
import inspect
import os
import stat
import sys
from typing import TYPE_CHECKING, Any, cast

import pytest

from spec_dock.provider_lifecycle.contracts import LifecycleRequest
from spec_dock.provider_lifecycle.engine import ProviderLifecycleEngine
from spec_dock.provider_lifecycle.filesystem import (
    AtomicRenameUnavailable,
    FilesystemSafetyError,
    LinuxRenameAt2Adapter,
    MacOSRenameAtXAdapter,
    NativeAtomicFilesystem,
)
from spec_dock.provider_lifecycle.wire import serialize_public_result


class _UnavailableAfterProbe:
    def __init__(self) -> None:
        self.exchange_calls = 0

    def rename_no_replace(self, *_args: object) -> None:
        raise OSError(errno.ENOENT, "probe source is absent")

    def exchange(self, *_args: object) -> None:
        self.exchange_calls += 1
        if self.exchange_calls == 1:
            raise OSError(errno.ENOENT, "probe source is absent")
        raise AtomicRenameUnavailable("native primitive became unavailable")


if TYPE_CHECKING:
    from pathlib import Path


def test_t05_linux_and_macos_native_atomic_adapters_have_no_unsafe_fallback() -> None:
    assert LinuxRenameAt2Adapter is not None
    assert MacOSRenameAtXAdapter is not None
    sources = (
        inspect.getsource(NativeAtomicFilesystem)
        + inspect.getsource(LinuxRenameAt2Adapter)
        + inspect.getsource(MacOSRenameAtXAdapter)
    )
    assert "os.rename(" not in sources
    assert "os.replace(" not in sources
    assert "copytree" not in sources


def test_t05_current_host_executes_only_its_native_adapter(tmp_path: Path) -> None:
    if sys.platform == "darwin":
        filesystem = NativeAtomicFilesystem()
        with pytest.raises(AtomicRenameUnavailable):
            LinuxRenameAt2Adapter()
    elif sys.platform == "linux":
        filesystem = NativeAtomicFilesystem()
        with pytest.raises(AtomicRenameUnavailable):
            MacOSRenameAtXAdapter()
    else:
        pytest.fail(f"unsupported test host: {sys.platform}")

    parent = tmp_path / "parent"
    parent.mkdir()
    source = parent / "source"
    destination = parent / "destination"
    source.write_text("source\n", encoding="utf-8")
    destination.write_text("destination\n", encoding="utf-8")
    source.chmod(0o644)
    destination.chmod(0o755)
    with filesystem.open_directory_chain_no_follow(str(parent)) as bound:
        source_witness = filesystem.capture_inode(bound.fd, "source", "regular")
        assert source_witness is not None
        filesystem.exchange(bound.fd, "source", bound.fd, "destination")
        assert (source.read_text(encoding="utf-8"), destination.read_text(encoding="utf-8")) == (
            "destination\n",
            "source\n",
        )
        assert stat.S_IMODE(os.lstat(source).st_mode) == 0o755
        assert stat.S_IMODE(os.lstat(destination).st_mode) == 0o644
        destination_witness = filesystem.capture_inode(bound.fd, "destination", "regular")
        assert destination_witness is not None
        filesystem.unlink_bound(bound.fd, "destination", destination_witness)


def test_t05_descriptor_relative_tree_removal_does_not_follow_links(tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    (tree / "nested").mkdir(parents=True)
    (tree / "nested" / "value").write_text("value\n", encoding="utf-8")
    (tree / "nested" / "value").chmod(0o644)
    outside = tmp_path / "outside"
    outside.write_text("keep\n", encoding="utf-8")
    (tree / "link").symlink_to(outside)
    with filesystem.open_directory_chain_no_follow(str(parent)) as bound:
        captured = filesystem.capture_domain_tree(bound.fd, "tree")
        assert any(entry.kind == "symlink" for entry in captured.entries)
        filesystem.remove_tree_bound(bound.fd, "tree", captured)
    assert outside.read_text(encoding="utf-8") == "keep\n"


def test_t05_regular_tree_capture_revalidates_open_fd_before_and_after_hash(monkeypatch, tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    tree.mkdir()
    value = tree / "value"
    value.write_text("before\n", encoding="utf-8")
    original_hash = NativeAtomicFilesystem._sha256_fd

    def mutate_during_hash(fd: int) -> str:
        value.write_text("after!\n", encoding="utf-8")
        return original_hash(fd)

    monkeypatch.setattr(NativeAtomicFilesystem, "_sha256_fd", staticmethod(mutate_during_hash))
    with filesystem.open_directory_chain_no_follow(str(parent)) as bound, pytest.raises(FilesystemSafetyError):
        filesystem.capture_domain_tree(bound.fd, "tree")


def test_t05_domain_tree_capture_revalidates_root_identity_before_open(monkeypatch, tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    tree.mkdir()
    replacement = tmp_path / "replacement"
    replacement.mkdir()
    old = tmp_path / "tree-old"

    with filesystem.open_directory_chain_no_follow(str(parent)) as bound:
        original_open = os.open
        replaced = False

        def replace_root(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
            nonlocal replaced
            if path == "tree" and kwargs.get("dir_fd") == bound.fd and not replaced:
                tree.rename(old)
                replacement.rename(tree)
                replaced = True
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", replace_root)
        with pytest.raises(FilesystemSafetyError):
            filesystem.capture_domain_tree(bound.fd, "tree")
    assert replaced


def test_t05_domain_tree_capture_revalidates_nested_directory_identity_before_open(monkeypatch, tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    (tree / "nested").mkdir(parents=True)
    replacement = tmp_path / "nested-replacement"
    replacement.mkdir()
    old = tmp_path / "nested-old"

    with filesystem.open_directory_chain_no_follow(str(parent)) as bound:
        original_open = os.open
        replaced = False

        def replace_nested(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
            nonlocal replaced
            if path == "nested" and not replaced:
                (tree / "nested").rename(old)
                replacement.rename(tree / "nested")
                replaced = True
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", replace_nested)
        with pytest.raises(FilesystemSafetyError):
            filesystem.capture_domain_tree(bound.fd, "tree")
    assert replaced


def test_t05_domain_tree_capture_rejects_regular_hard_links(tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    tree.mkdir()
    source = parent / "source"
    source.write_text("shared\n", encoding="utf-8")
    os.link(source, tree / "linked")

    with filesystem.open_directory_chain_no_follow(str(parent)) as bound:
        with pytest.raises(FilesystemSafetyError):
            filesystem.capture_inode(bound.fd, "source", "regular")
        with pytest.raises(FilesystemSafetyError):
            filesystem.capture_domain_tree(bound.fd, "tree")


def test_t05_domain_tree_capture_revalidates_symlink_identity_after_readlink(monkeypatch, tmp_path: Path) -> None:
    filesystem = NativeAtomicFilesystem()
    parent = tmp_path / "parent"
    parent.mkdir()
    tree = parent / "tree"
    tree.mkdir()
    link = tree / "link"
    link.symlink_to("old-target")

    original_readlink = cast("Any", os.readlink)
    replaced = False

    def replace_symlink(path: Any, *args: Any, **kwargs: Any) -> str:
        nonlocal replaced
        target = original_readlink(path, *args, **kwargs)
        if path == "link" and not replaced:
            link.unlink()
            link.symlink_to("new-target")
            replaced = True
        return cast("str", target)

    monkeypatch.setattr(os, "readlink", replace_symlink)
    with filesystem.open_directory_chain_no_follow(str(parent)) as bound, pytest.raises(FilesystemSafetyError):
        filesystem.capture_domain_tree(bound.fd, "tree")
    assert replaced


def test_t08_unavailable_native_capability_is_closed_before_repository_observation(monkeypatch, tmp_path: Path) -> None:
    workspace = (tmp_path / "unavailable-native").resolve()
    workspace.mkdir()
    monkeypatch.setattr(
        NativeAtomicFilesystem,
        "_current_adapter",
        staticmethod(lambda: (_ for _ in ()).throw(AtomicRenameUnavailable("native primitive unavailable"))),
    )
    request = LifecycleRequest(
        str(workspace),
        "apply",
        True,
        operation="install",
        seed_policy="create-if-absent",
    )

    result = ProviderLifecycleEngine().execute(request, force=True)

    serialize_public_result(result)
    assert result.status == "blocked"
    assert result.code == "atomic-rename-unavailable"
    assert result.operation == "install"
    assert result.candidate_digest is None
    assert result.seed_policy == "create-if-absent"
    assert result.mutation_started is False
    assert tuple(workspace.iterdir()) == ()


def test_t08_runtime_native_capability_failure_uses_preparation_wire_row(tmp_path: Path) -> None:
    workspace = (tmp_path / "runtime-unavailable-native").resolve()
    workspace.mkdir()
    install = LifecycleRequest(
        str(workspace),
        "apply",
        True,
        operation="install",
        seed_policy="create-if-absent",
    )
    assert ProviderLifecycleEngine().execute(install, force=True).status == "completed"

    update = LifecycleRequest(
        str(workspace),
        "apply",
        True,
        operation="update",
        seed_policy="preserve-only",
    )
    adapter = _UnavailableAfterProbe()
    result = ProviderLifecycleEngine(filesystem=NativeAtomicFilesystem(adapter=adapter)).execute(update)

    serialize_public_result(result)
    assert adapter.exchange_calls == 2
    assert result.status == "blocked"
    assert result.code == "lifecycle-preparation-failed"
    assert result.operation == "update"
    assert result.candidate_digest is not None
    assert result.seed_policy == "preserve-only"
    assert result.mutation_started is False
    assert result.phase == "publish-incomplete-record"
    assert result.last_completed_phase == "candidate-staging"
    assert result.retry_command == f"spec-dock update -- {workspace}"
