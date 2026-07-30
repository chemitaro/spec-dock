from collections.abc import Callable
from datetime import datetime, timezone
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
from typing import TYPE_CHECKING
import zipfile

import pytest

if TYPE_CHECKING:
    from spec_dock_runtime.domain.issue_planning_contracts import IssueCandidateIdentity

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _infra():
    return __import__(
        "spec_dock_runtime.infra.issue_planning_candidate",
        fromlist=["build_deterministic_zip"],
    )


def _files() -> dict[str, bytes]:
    return {
        "CHECKSUMS.sha256": b"checksums\n",
        "MANIFEST.json": b"{}\n",
        "PLACEHOLDER-ORACLE-MAP.json": b"{}\n",
        "SOURCE-BASELINE.json": b"{}\n",
        "design.md": b"design\n",
        "plan.md": b"plan\n",
        "requirement.md": b"requirement\n",
        "artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md": (b"guide\n"),
    }


COMPANION_PATH = "artifacts/20260729t120000z-guide-new-member-chatgpt-first-issue-planning.md"


def _companion() -> bytes:
    preface = """
# First-day onboarding

This subordinate guide defers to requirement.md, design.md, and plan.md.

## Initiative, Epic, and Issue lineage

The target is init-00001, epic-00002, and iss-00003.

## Purpose and scope

Purpose and scope are bounded to onboarding.

## System context

The system context identifies the actors.

## Authority and responsibility boundary

Authority and responsibility remain deterministic.

## Current architecture and target architecture

Current architecture and target architecture define the transition.

## ChatGPT First planning lifecycle

ChatGPT First governs the planning lifecycle.

## Direct Oracle and reference-only chatgpt-use

Oracle is direct and chatgpt-use is reference-only.

## Candidate, Review, Human, and apply lifecycle

Candidate, Review, Human decision, and apply are controlled.

## Exact current branch gate

The exact current branch is required.

## Implementation roadmap

S01 through S07 are complete; S08 through S14 remain.

## Provider authority and projection

Provider authority precedes projection.

## Failure modes

Failure handling stops closed.

## First-day checklist

The first-day checklist directs onboarding.
"""
    roles = (
        "system context",
        "responsibility authority boundary",
        "planning sequence",
        "implementation roadmap",
    )
    blocks = "".join(f"\n```plantuml\n@startuml\ntitle {role}\nactor Human\n@enduml\n```\n" for role in roles)
    return (preface + blocks).encode()


def test_zip_bytes_are_reproducible_for_fixed_inputs_and_timestamp(tmp_path: Path) -> None:
    instant = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    _infra().build_deterministic_zip(first, "candidate", _files(), instant)
    _infra().build_deterministic_zip(second, "candidate", _files(), instant)
    assert first.read_bytes() == second.read_bytes()


def test_zip_entry_order_permissions_timestamp_comments_and_extra_fields_are_fixed(
    tmp_path: Path,
) -> None:
    path = tmp_path / "candidate.zip"
    _infra().build_deterministic_zip(
        path,
        "candidate",
        _files(),
        datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        assert [info.filename for info in infos] == sorted(
            [f"candidate/{name}" for name in _files()],
            key=lambda value: value.encode(),
        )
        assert archive.comment == b""
        assert all(info.external_attr >> 16 == 0o100644 for info in infos)
        assert all(info.extra == b"" and info.comment == b"" for info in infos)


@pytest.mark.parametrize("kind", ["missing", "inside", "ancestor", "symlink"])
def test_output_guard_requires_existing_external_non_symlink_directory(
    tmp_path: Path,
    kind: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    output = tmp_path / "output"
    if kind == "inside":
        output = repo / "output"
        output.mkdir()
    elif kind == "ancestor":
        output = tmp_path
    elif kind == "symlink":
        target = tmp_path / "target"
        target.mkdir()
        output.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="output"):
        _infra().validate_candidate_output_directory(output, repo)


def test_atomic_publication_collision_preserves_existing_bytes(tmp_path: Path) -> None:
    source = tmp_path / "staged.zip"
    source.write_bytes(b"new")
    destination = tmp_path / "candidate.zip"
    destination.write_bytes(b"existing")
    before = hashlib.sha256(destination.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        _infra().atomic_publish_no_replace(source, destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == before


@pytest.mark.parametrize(
    ("backend_name", "symbol_name", "expected_call"),
    [
        (
            "_link_exclusive_linux_at",
            "linkat",
            (-100, b"/proc/self/fd/11", 22, b"candidate.zip", 0x00000400),
        ),
        (
            "_clone_exclusive_darwin_at",
            "fclonefileat",
            (11, 22, b"candidate.zip", 0),
        ),
    ],
)
def test_fd_publication_backends_pass_verified_descriptor_to_os_primitive(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    expected_call: tuple[object, ...],
) -> None:
    infra = _infra()
    calls: list[tuple[object, ...]] = []

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *args):
            calls.append(args)
            return 0

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(infra.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    getattr(infra, backend_name)(11, 22, "candidate.zip")

    assert calls == [expected_call]


def test_candidate_publication_entry_binding_covers_linux_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra = _infra()
    output = tmp_path / "output"
    output.mkdir()
    output_descriptor = os.open(output, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    staged_descriptor = os.open(
        "staged.zip",
        os.O_RDWR | os.O_CREAT | os.O_EXCL,
        0o600,
        dir_fd=output_descriptor,
    )
    staged_bytes = b"linux staged bytes"
    os.write(staged_descriptor, staged_bytes)
    published_aside = output / "published-aside.zip"
    published_inode = [-1]
    replacement_inode = [-1]

    def link_staged(
        source_descriptor: int,
        destination_descriptor: int,
        destination_name: str,
    ) -> None:
        assert source_descriptor == staged_descriptor
        os.link(
            "staged.zip",
            destination_name,
            src_dir_fd=destination_descriptor,
            dst_dir_fd=destination_descriptor,
            follow_symlinks=False,
        )
        published_inode[0] = os.stat(
            destination_name,
            dir_fd=destination_descriptor,
            follow_symlinks=False,
        ).st_ino
        os.rename(
            destination_name,
            published_aside.name,
            src_dir_fd=destination_descriptor,
            dst_dir_fd=destination_descriptor,
        )
        replacement_descriptor = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=destination_descriptor,
        )
        try:
            os.write(replacement_descriptor, staged_bytes)
            os.fsync(replacement_descriptor)
            replacement_inode[0] = os.fstat(replacement_descriptor).st_ino
        finally:
            os.close(replacement_descriptor)

    monkeypatch.setattr(infra.platform, "system", lambda: "Linux")
    monkeypatch.setattr(infra, "_link_exclusive_linux_at", link_staged)
    published_entry = None
    try:
        staged_identity = os.fstat(staged_descriptor)
        published_entry = infra._publish_verified_fd_no_replace_at(
            staged_descriptor,
            output_descriptor,
            "candidate.zip",
        )
        final_identity = os.stat(
            "candidate.zip",
            dir_fd=output_descriptor,
            follow_symlinks=False,
        )

        assert published_entry.name == "candidate.zip"
        assert (published_entry.device, published_entry.inode) == (
            staged_identity.st_dev,
            staged_identity.st_ino,
        )
        assert published_aside.stat().st_ino == published_inode[0]
        assert published_entry.inode == published_inode[0]
        assert final_identity.st_ino == replacement_inode[0]
        assert (final_identity.st_dev, final_identity.st_ino) != (
            published_entry.device,
            published_entry.inode,
        )
        assert final_identity.st_ino != published_inode[0]
        assert (output / "candidate.zip").read_bytes() == staged_bytes
        assert published_aside.read_bytes() == staged_bytes
    finally:
        if published_entry is not None:
            os.close(published_entry.descriptor)
        os.close(staged_descriptor)
        os.close(output_descriptor)


def test_candidate_publication_entry_binding_covers_darwin_clone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra = _infra()
    output = tmp_path / "output"
    output.mkdir()
    output_descriptor = os.open(output, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    staged_descriptor = os.open(
        "staged.zip",
        os.O_RDWR | os.O_CREAT | os.O_EXCL,
        0o600,
        dir_fd=output_descriptor,
    )
    staged_bytes = b"darwin staged bytes"
    os.write(staged_descriptor, staged_bytes)
    published_aside = output / "published-aside.zip"
    published_inode = [-1]
    replacement_inode = [-1]

    def clone_to_distinct_inode(
        source_descriptor: int,
        destination_descriptor: int,
        destination_name: str,
    ) -> None:
        os.lseek(source_descriptor, 0, os.SEEK_SET)
        cloned_descriptor = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=destination_descriptor,
        )
        try:
            os.write(cloned_descriptor, os.read(source_descriptor, len(staged_bytes)))
            os.fsync(cloned_descriptor)
        finally:
            os.close(cloned_descriptor)

    def rename_capture_no_replace(
        source_descriptor: int,
        source_name: str,
        destination_descriptor: int,
        destination_name: str,
    ) -> None:
        with pytest.raises(FileNotFoundError):
            os.stat(
                destination_name,
                dir_fd=destination_descriptor,
                follow_symlinks=False,
            )
        os.rename(
            source_name,
            destination_name,
            src_dir_fd=source_descriptor,
            dst_dir_fd=destination_descriptor,
        )
        published_inode[0] = os.stat(
            destination_name,
            dir_fd=destination_descriptor,
            follow_symlinks=False,
        ).st_ino
        os.rename(
            destination_name,
            published_aside.name,
            src_dir_fd=destination_descriptor,
            dst_dir_fd=destination_descriptor,
        )
        replacement_descriptor = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=destination_descriptor,
        )
        try:
            os.write(replacement_descriptor, staged_bytes)
            os.fsync(replacement_descriptor)
            replacement_inode[0] = os.fstat(replacement_descriptor).st_ino
        finally:
            os.close(replacement_descriptor)

    monkeypatch.setattr(infra.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(infra, "_clone_exclusive_darwin_at", clone_to_distinct_inode)
    monkeypatch.setattr(infra, "_rename_exclusive_darwin_at", rename_capture_no_replace)
    published_entry = None
    try:
        staged_identity = os.fstat(staged_descriptor)
        published_entry = infra._publish_verified_fd_no_replace_at(
            staged_descriptor,
            output_descriptor,
            "candidate.zip",
        )
        final_identity = os.stat(
            "candidate.zip",
            dir_fd=output_descriptor,
            follow_symlinks=False,
        )

        assert published_entry.name == "candidate.zip"
        assert (published_entry.device, published_entry.inode) != (
            staged_identity.st_dev,
            staged_identity.st_ino,
        )
        assert published_aside.stat().st_ino == published_inode[0]
        assert published_entry.inode == published_inode[0]
        assert final_identity.st_ino == replacement_inode[0]
        assert (final_identity.st_dev, final_identity.st_ino) != (
            published_entry.device,
            published_entry.inode,
        )
        assert final_identity.st_ino != published_inode[0]
        assert (output / "candidate.zip").read_bytes() == staged_bytes
        assert published_aside.read_bytes() == staged_bytes
    finally:
        if published_entry is not None:
            os.close(published_entry.descriptor)
        os.close(staged_descriptor)
        os.close(output_descriptor)


@pytest.mark.parametrize(
    ("backend_name", "symbol_name", "expected_call"),
    [
        (
            "_rename_exclusive_linux_at",
            "renameat2",
            (11, b"source.zip", 22, b"destination.zip", 0x00000001),
        ),
        (
            "_rename_exclusive_darwin_at",
            "renameatx_np",
            (11, b"source.zip", 22, b"destination.zip", 0x00000004),
        ),
    ],
)
def test_candidate_cleanup_no_replace_backend_arguments(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    expected_call: tuple[object, ...],
) -> None:
    infra = _infra()
    calls: list[tuple[object, ...]] = []

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *args):
            calls.append(args)
            return 0

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(infra.ctypes, "CDLL", lambda *_args, **_kwargs: library)

    getattr(infra, backend_name)(11, "source.zip", 22, "destination.zip")

    assert calls == [expected_call]


@pytest.mark.parametrize(
    ("backend_name", "symbol_name"),
    [
        ("_rename_exclusive_linux_at", "renameat2"),
        ("_rename_exclusive_darwin_at", "renameatx_np"),
    ],
)
def test_candidate_cleanup_no_replace_backend_missing_symbol_is_unsupported(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
) -> None:
    infra = _infra()

    class FakeLibrary:
        pass

    monkeypatch.setattr(infra.ctypes, "CDLL", lambda *_args, **_kwargs: FakeLibrary())

    with pytest.raises(NotImplementedError, match=f"{symbol_name} is unavailable"):
        getattr(infra, backend_name)(11, "source.zip", 22, "destination.zip")


@pytest.mark.parametrize(
    ("backend_name", "symbol_name"),
    [
        ("_rename_exclusive_linux_at", "renameat2"),
        ("_rename_exclusive_darwin_at", "renameatx_np"),
    ],
)
@pytest.mark.parametrize(
    ("error_number", "expected_error"),
    [
        (errno.EEXIST, FileExistsError),
        (errno.EPERM, OSError),
    ],
)
def test_candidate_cleanup_no_replace_backend_maps_native_errors(
    monkeypatch: pytest.MonkeyPatch,
    backend_name: str,
    symbol_name: str,
    error_number: int,
    expected_error: type[OSError],
) -> None:
    infra = _infra()

    class FakeFunction:
        argtypes = None
        restype = None

        def __call__(self, *_args):
            return -1

    class FakeLibrary:
        pass

    library = FakeLibrary()
    setattr(library, symbol_name, FakeFunction())
    monkeypatch.setattr(infra.ctypes, "CDLL", lambda *_args, **_kwargs: library)
    monkeypatch.setattr(infra.ctypes, "get_errno", lambda: error_number)

    with pytest.raises(expected_error) as raised:
        getattr(infra, backend_name)(11, "source.zip", 22, "destination.zip")

    assert raised.value.errno == error_number


@pytest.mark.skipif(sys.platform != "linux", reason="Linux linkat contract")
def test_linux_proc_fd_publication_is_real_unprivileged_descriptor_bound_and_no_replace(
    tmp_path: Path,
) -> None:
    infra = _infra()
    capability_status = Path("/proc/self/status").read_text()
    effective_capabilities = int(
        next(line.split(":", 1)[1].strip() for line in capability_status.splitlines() if line.startswith("CapEff:")),
        16,
    )
    assert os.geteuid() != 0
    assert effective_capabilities & (1 << 2) == 0

    output = tmp_path / "output"
    output.mkdir()
    output_descriptor = os.open(output, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    staged_descriptor = -1
    original_bytes = b"verified staged descriptor bytes"
    replacement_bytes = b"replacement staged name bytes"
    staged_name = "staged.zip"
    renamed_name = "renamed-staged.zip"
    final_name = "candidate.zip"
    try:
        staged_descriptor = os.open(
            staged_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=output_descriptor,
        )
        os.write(staged_descriptor, original_bytes)
        os.fsync(staged_descriptor)
        staged_stat = os.fstat(staged_descriptor)

        os.rename(
            staged_name,
            renamed_name,
            src_dir_fd=output_descriptor,
            dst_dir_fd=output_descriptor,
        )
        replacement_descriptor = os.open(
            staged_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=output_descriptor,
        )
        try:
            os.write(replacement_descriptor, replacement_bytes)
        finally:
            os.close(replacement_descriptor)

        infra._link_exclusive_linux_at(
            staged_descriptor,
            output_descriptor,
            final_name,
        )

        assert (output / final_name).read_bytes() == original_bytes
        final_stat = os.stat(
            final_name,
            dir_fd=output_descriptor,
            follow_symlinks=False,
        )
        assert (final_stat.st_dev, final_stat.st_ino) == (
            staged_stat.st_dev,
            staged_stat.st_ino,
        )

        with pytest.raises(FileExistsError):
            infra._link_exclusive_linux_at(
                staged_descriptor,
                output_descriptor,
                final_name,
            )
        assert (output / final_name).read_bytes() == original_bytes
    finally:
        if staged_descriptor >= 0:
            os.close(staged_descriptor)
        os.close(output_descriptor)


def _publish_setup(tmp_path: Path):
    repo = tmp_path / "repo"
    output = tmp_path / "output"
    repo.mkdir()
    output.mkdir()
    infra = _infra()
    return (
        infra,
        repo,
        output,
        infra.validate_candidate_output_directory(output, repo),
        _candidate_material(),
    )


def test_candidate_publish_rejects_pre_capture_path_replacement_before_any_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    original_output = tmp_path / "original-output"
    redirected_output = tmp_path / "redirected-output"
    redirected_output.mkdir()
    original_open_safe = infra.open_safe_directory_descriptor
    original_mkdtemp = infra.tempfile.mkdtemp
    original_build = infra.build_deterministic_zip
    writes: list[Path] = []
    replaced = [False]

    def replace_path() -> None:
        if replaced[0]:
            return
        replaced[0] = True
        output.rename(original_output)
        output.symlink_to(redirected_output, target_is_directory=True)

    def open_after_replacement(path: Path) -> int:
        if path == output:
            replace_path()
        return original_open_safe(path)

    def mkdtemp_after_replacement(*args, **kwargs):
        directory = kwargs.get("dir", args[2] if len(args) > 2 else None)
        if directory is not None and Path(directory) == output:
            replace_path()
        return original_mkdtemp(*args, **kwargs)

    def observe_build(destination: Path, *args, **kwargs) -> None:
        writes.append(destination)
        original_build(destination, *args, **kwargs)

    monkeypatch.setattr(infra, "open_safe_directory_descriptor", open_after_replacement)
    monkeypatch.setattr(infra.tempfile, "mkdtemp", mkdtemp_after_replacement)
    monkeypatch.setattr(infra, "build_deterministic_zip", observe_build)

    with pytest.raises(infra.CandidateOutputRejected):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert replaced == [True]
    assert writes == []
    assert list(original_output.iterdir()) == []
    assert list(redirected_output.iterdir()) == []


@pytest.mark.parametrize("replacement_kind", ["symlink", "directory"])
def test_candidate_publish_rejects_detached_public_path_and_removes_published_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement_kind: str,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    original_output = tmp_path / "original-output"
    redirected_output = tmp_path / "redirected-output"
    redirected_output.mkdir()
    original_open = infra.os.open
    replaced = [False]

    def replace_path() -> None:
        if replaced[0]:
            return
        replaced[0] = True
        output.rename(original_output)
        if replacement_kind == "symlink":
            output.symlink_to(redirected_output, target_is_directory=True)
        else:
            output.mkdir()

    def open_after_capture(path, flags, *args, **kwargs):
        if (
            kwargs.get("dir_fd") is not None
            and str(path).startswith(".spec-dock-issue-candidate-")
            and str(path).endswith(".zip")
            and flags & os.O_CREAT
        ):
            replace_path()
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(infra.os, "open", open_after_capture)

    with pytest.raises(infra.CandidateOutputRejected):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert replaced == [True]
    assert list(original_output.iterdir()) == []
    assert list(redirected_output.iterdir()) == []
    if replacement_kind == "directory":
        assert list(output.iterdir()) == []


def test_candidate_rejection_cleanup_post_match_swap_preserves_unknown_final(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    final_path = output / material.logical_filename
    displaced_path = output / "displaced-owned-candidate.zip"
    unknown_bytes = b"unknown racing final bytes"
    original_matches = infra._owned_entry_matches
    swapped = [False]

    def reject_attachment(*_args, **_kwargs) -> None:
        raise infra.CandidateOutputRejected("forced attachment rejection")

    def match_then_swap(parent_descriptor, entry, *, expected_kind):
        matched = original_matches(
            parent_descriptor,
            entry,
            expected_kind=expected_kind,
        )
        if matched and entry.name == material.logical_filename and not swapped[0]:
            swapped[0] = True
            os.rename(
                material.logical_filename,
                displaced_path.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
            unknown_descriptor = os.open(
                material.logical_filename,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=parent_descriptor,
            )
            try:
                os.write(unknown_descriptor, unknown_bytes)
                os.fsync(unknown_descriptor)
            finally:
                os.close(unknown_descriptor)
        return matched

    monkeypatch.setattr(infra, "_verify_published_candidate_attachment", reject_attachment)
    monkeypatch.setattr(infra, "_owned_entry_matches", match_then_swap)

    with pytest.raises(infra.CandidateOutputRejected):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert swapped == [True]
    assert final_path.read_bytes() == unknown_bytes
    assert displaced_path.read_bytes() != unknown_bytes


def test_candidate_post_publication_pre_capture_same_bytes_replacement_is_preserved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    final_path = output / material.logical_filename
    published_aside = output / "published-aside.zip"
    original_publish = infra._publish_verified_fd_no_replace_at
    replacement_inode = [-1]
    published_inode = [-1]

    def publish_then_replace(staged_descriptor, destination_descriptor, destination_name):
        published_entry = original_publish(
            staged_descriptor,
            destination_descriptor,
            destination_name,
        )
        published_bytes = final_path.read_bytes()
        published_inode[0] = final_path.stat().st_ino
        os.rename(
            destination_name,
            published_aside.name,
            src_dir_fd=destination_descriptor,
            dst_dir_fd=destination_descriptor,
        )
        replacement_descriptor = os.open(
            destination_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
            dir_fd=destination_descriptor,
        )
        try:
            os.write(replacement_descriptor, published_bytes)
            os.fsync(replacement_descriptor)
            replacement_inode[0] = os.fstat(replacement_descriptor).st_ino
        finally:
            os.close(replacement_descriptor)
        return published_entry

    def reject_attachment(*_args, **_kwargs) -> None:
        raise infra.CandidateOutputRejected("forced attachment rejection")

    monkeypatch.setattr(infra, "_publish_verified_fd_no_replace_at", publish_then_replace)
    monkeypatch.setattr(infra, "_verify_published_candidate_attachment", reject_attachment)

    with pytest.raises(infra.CandidateOutputRejected):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert published_inode[0] != replacement_inode[0]
    assert final_path.read_bytes() == published_aside.read_bytes()
    assert final_path.stat().st_ino == replacement_inode[0]
    assert published_aside.stat().st_ino == published_inode[0]
    assert not any(path.name.startswith(".spec-dock-issue-candidate-cleanup-") for path in output.iterdir())


def test_candidate_cleanup_missing_native_primitive_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    final_path = output / material.logical_filename
    displaced_path = output / "displaced-owned-candidate.zip"
    unknown_bytes = b"unknown bytes retained without native rename"
    original_matches = infra._owned_entry_matches
    original_rename = os.rename
    swapped = [False]

    def reject_attachment(*_args, **_kwargs) -> None:
        raise infra.CandidateOutputRejected("forced attachment rejection")

    def match_then_swap(parent_descriptor, entry, *, expected_kind):
        matched = original_matches(
            parent_descriptor,
            entry,
            expected_kind=expected_kind,
        )
        if matched and entry.name == material.logical_filename and not swapped[0]:
            swapped[0] = True
            original_rename(
                material.logical_filename,
                displaced_path.name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
            unknown_descriptor = os.open(
                material.logical_filename,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=parent_descriptor,
            )
            try:
                os.write(unknown_descriptor, unknown_bytes)
                os.fsync(unknown_descriptor)
            finally:
                os.close(unknown_descriptor)
        return matched

    def unavailable_native_rename(*_args, **_kwargs) -> None:
        raise NotImplementedError("native no-replace rename unavailable")

    monkeypatch.setattr(infra, "_verify_published_candidate_attachment", reject_attachment)
    monkeypatch.setattr(infra, "_owned_entry_matches", match_then_swap)
    monkeypatch.setattr(infra, "_rename_exclusive_at", unavailable_native_rename)
    monkeypatch.setattr(
        infra.os,
        "rename",
        lambda *_args, **_kwargs: pytest.fail("rename fallback must not be used"),
    )

    with pytest.raises(infra.CandidateOutputRejected):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert swapped == [True]
    assert final_path.read_bytes() == unknown_bytes
    assert displaced_path.read_bytes() != unknown_bytes


def test_candidate_publish_collision_preserves_existing_entry_and_cleans_private_stage(
    tmp_path: Path,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    existing = output / material.logical_filename
    existing.write_bytes(b"existing candidate")

    with pytest.raises(infra.CandidateCollision):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert existing.read_bytes() == b"existing candidate"
    assert [path.name for path in output.iterdir()] == [material.logical_filename]


def test_candidate_publish_racing_collision_preserves_existing_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    existing = output / material.logical_filename
    original_review = infra._review_candidate_snapshot

    def review_then_collide(*args, **kwargs):
        review = original_review(*args, **kwargs)
        existing.write_bytes(b"racing candidate")
        return review

    monkeypatch.setattr(infra, "_review_candidate_snapshot", review_then_collide)

    with pytest.raises(infra.CandidateCollision):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert existing.read_bytes() == b"racing candidate"
    assert [path.name for path in output.iterdir()] == [material.logical_filename]


def test_candidate_fd_publication_backend_collision_preserves_racing_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    existing = output / material.logical_filename

    def collide(_staged_descriptor, _destination_descriptor, destination_name):
        assert destination_name == material.logical_filename
        existing.write_bytes(b"racing candidate")
        raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), destination_name)

    monkeypatch.setattr(infra, "_publish_verified_fd_no_replace_at", collide)

    with pytest.raises(infra.CandidateCollision):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert existing.read_bytes() == b"racing candidate"
    assert [path.name for path in output.iterdir()] == [material.logical_filename]


def test_candidate_fd_publication_backend_failure_fails_closed_without_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)

    def fail_backend(_staged_descriptor, _destination_descriptor, _destination_name):
        raise OSError(errno.ENOTSUP, os.strerror(errno.ENOTSUP))

    monkeypatch.setattr(infra, "_publish_verified_fd_no_replace_at", fail_backend)
    monkeypatch.setattr(
        infra,
        "_atomic_publish_no_replace_at",
        lambda *_args, **_kwargs: pytest.fail("pathname publication fallback must not be used"),
        raising=False,
    )

    with pytest.raises(infra.CandidatePublicationFailed):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert list(output.iterdir()) == []


def test_candidate_publish_unsupported_platform_fails_closed_and_cleans_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    monkeypatch.setattr(infra.platform, "system", lambda: "unsupported")

    with pytest.raises(infra.CandidatePublicationFailed):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert list(output.iterdir()) == []


def test_candidate_uses_atomic_hidden_staged_file_without_output_stage_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    original_open = infra.os.open
    original_mkdir = infra.os.mkdir
    staged_open_calls: list[tuple[str, int, int]] = []

    def reject_output_stage_directory(path, mode=0o777, *, dir_fd=None):
        if dir_fd is not None and str(path).startswith(".spec-dock-issue-candidate-"):
            pytest.fail("Candidate staging directory must not be created")
        return original_mkdir(path, mode, dir_fd=dir_fd)

    def record_staged_open(path, flags, mode=0o777, *, dir_fd=None):
        if (
            dir_fd is not None
            and str(path).startswith(".spec-dock-issue-candidate-")
            and str(path).endswith(".zip")
            and flags & os.O_CREAT
        ):
            staged_open_calls.append((str(path), flags, mode))
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(infra.os, "mkdir", reject_output_stage_directory)
    monkeypatch.setattr(infra.os, "open", record_staged_open)

    published = infra.build_and_publish_candidate(
        output_guard=guard,
        repo_root=repo,
        material=material,
    )

    assert len(staged_open_calls) == 1
    _name, flags, mode = staged_open_calls[0]
    assert flags & os.O_RDWR
    assert flags & os.O_CREAT
    assert flags & os.O_EXCL
    assert flags & getattr(os, "O_NOFOLLOW", 0)
    assert flags & getattr(os, "O_NONBLOCK", 0)
    assert mode == 0o600
    assert [path.name for path in output.iterdir()] == [published.identity.logical_filename]


def test_candidate_atomic_staged_file_replacement_is_preserved_and_not_published(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    original_open = infra.os.open
    staged_names: list[str] = []
    sentinel = b"replacement staged ZIP"

    def replace_after_atomic_open(path, flags, mode=0o777, *, dir_fd=None):
        descriptor = original_open(path, flags, mode, dir_fd=dir_fd)
        if (
            dir_fd is not None
            and str(path).startswith(".spec-dock-issue-candidate-")
            and str(path).endswith(".zip")
            and flags & os.O_CREAT
            and not staged_names
        ):
            staged_name = str(path)
            staged_names.append(staged_name)
            os.rename(
                staged_name,
                f"{staged_name}.owned",
                src_dir_fd=dir_fd,
                dst_dir_fd=dir_fd,
            )
            sentinel_descriptor = original_open(
                staged_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=dir_fd,
            )
            os.write(sentinel_descriptor, sentinel)
            os.close(sentinel_descriptor)
        return descriptor

    monkeypatch.setattr(infra.os, "open", replace_after_atomic_open)

    with pytest.raises(infra.CandidatePublicationFailed):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert len(staged_names) == 1
    assert (output / staged_names[0]).read_bytes() == sentinel
    assert (output / f"{staged_names[0]}.owned").is_file()
    assert not (output / material.logical_filename).exists()


def test_candidate_post_match_staged_name_swap_publishes_verified_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    original_matches = infra._owned_entry_matches
    sentinel = b"replacement staged ZIP"
    swapped_names: list[str] = []

    def match_then_swap(parent_descriptor, entry, *, expected_kind):
        matches = original_matches(
            parent_descriptor,
            entry,
            expected_kind=expected_kind,
        )
        if matches and not swapped_names:
            swapped_names.append(entry.name)
            os.rename(
                entry.name,
                f"{entry.name}.owned",
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
            replacement_descriptor = os.open(
                entry.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
                dir_fd=parent_descriptor,
            )
            try:
                os.write(replacement_descriptor, sentinel)
            finally:
                os.close(replacement_descriptor)
        return matches

    monkeypatch.setattr(infra, "_owned_entry_matches", match_then_swap)

    published = infra.build_and_publish_candidate(
        output_guard=guard,
        repo_root=repo,
        material=material,
    )

    final_bytes = (output / material.logical_filename).read_bytes()
    assert hashlib.sha256(final_bytes).hexdigest() == published.identity.zip_sha256
    assert len(final_bytes) == published.zip_byte_count
    assert len(swapped_names) == 1
    assert (output / swapped_names[0]).read_bytes() == sentinel
    assert (output / f"{swapped_names[0]}.owned").is_file()


def test_candidate_random_staged_name_collision_retries_without_modifying_existing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    tokens = iter(("a" * 32, "b" * 32))
    first_name = f".spec-dock-issue-candidate-{'a' * 32}.zip"
    sentinel = output / first_name
    sentinel.write_bytes(b"existing random-name collision")
    calls: list[int] = []

    def next_token(size: int) -> str:
        calls.append(size)
        return next(tokens)

    monkeypatch.setattr(infra.secrets, "token_hex", next_token)

    published = infra.build_and_publish_candidate(
        output_guard=guard,
        repo_root=repo,
        material=material,
    )

    assert calls == [16, 16]
    assert sentinel.read_bytes() == b"existing random-name collision"
    assert (output / published.identity.logical_filename).is_file()


def test_candidate_all_random_staged_name_collisions_fail_and_preserve_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    infra, repo, output, guard, material = _publish_setup(tmp_path)
    tokens = tuple(f"{index:032x}" for index in range(32))
    existing = {
        f".spec-dock-issue-candidate-{token}.zip": f"sentinel-{index}".encode() for index, token in enumerate(tokens)
    }
    for name, payload in existing.items():
        (output / name).write_bytes(payload)
    sequence = iter(tokens)
    monkeypatch.setattr(infra.secrets, "token_hex", lambda size: next(sequence))

    with pytest.raises(infra.CandidateBuildFailed):
        infra.build_and_publish_candidate(
            output_guard=guard,
            repo_root=repo,
            material=material,
        )

    assert {path.name: path.read_bytes() for path in output.iterdir()} == existing
    assert not (output / material.logical_filename).exists()


def _candidate_material(*, body: str = "Substantive content."):
    domain = __import__(
        "spec_dock_runtime.domain.issue_planning_candidate",
        fromlist=["build_candidate_material"],
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningContext"],
    )
    documents = {
        name: (
            "---\n"
            f"種別: {kind}\n"
            'ID: "iss-00003"\n'
            'タイトル: "Issue"\n'
            '状態: "approved"\n'
            '作成者: "Author"\n'
            '最終更新: "2026-07-28"\n'
            + (
                '依存: ["requirement.md"]\n'
                if name == "design.md"
                else '依存: ["requirement.md", "design.md"]\n'
                if name == "plan.md"
                else ""
            )
            + '親: ["epic-00002", "init-00001"]\n'
            "---\n\n"
            f"# iss-00003 Issue\n\n## Section\n\n{body}\n"
        ).encode()
        for name, kind in (
            ("requirement.md", "要件定義書（Issue）"),
            ("design.md", "設計書（Issue）"),
            ("plan.md", "実装計画書（Issue）"),
        )
    }
    companion = _companion()
    source_payload = b"exact four-file Oracle authoring ZIP"
    context = contracts.PlanningContext(
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        parent_epic_id="epic-00002",
        parent_initiative_id="init-00001",
        dependency_summary=(),
        canonical_issue_paths=(
            "spec-dock/initiatives/i/epics/e/issues/x/design.md",
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md",
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md",
        ),
        relevant_source_paths=(),
        operator_context=(),
        onboarding_companion_path=COMPANION_PATH,
    )
    source = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash="b" * 64,
        snapshot_id="c" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    return domain.build_candidate_material(
        planner_documents=documents,
        onboarding_companion_path=COMPANION_PATH,
        onboarding_companion_bytes=companion,
        baseline=domain.parse_current_front_matter_baseline(documents),
        context=context,
        source_evidence=source,
        source_payload_sha256=hashlib.sha256(source_payload).hexdigest(),
        source_payload_size=len(source_payload),
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )


def _valid_candidate(
    tmp_path: Path,
    *,
    body: str = "Substantive content.",
) -> tuple[Path, Path, "IssueCandidateIdentity"]:
    material = _candidate_material(body=body)
    repo = tmp_path / "repo"
    output = tmp_path / "output"
    repo.mkdir()
    output.mkdir()
    published = _infra().build_and_publish_candidate(
        output_guard=_infra().validate_candidate_output_directory(output, repo),
        repo_root=repo,
        material=material,
    )
    with zipfile.ZipFile(output / published.identity.logical_filename) as archive:
        assert len(archive.namelist()) == 8
    assert published.onboarding_companion.path == COMPANION_PATH
    assert published.onboarding_companion.sha256 == hashlib.sha256(_companion()).hexdigest()
    return repo, output / published.identity.logical_filename, published.identity


def _rewrite_candidate(
    candidate: Path,
    mutate: Callable[[dict[str, bytes]], None],
) -> None:
    original = candidate.read_bytes()
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        entries = {name: source.read(name) for name in source.namelist()}
    mutate(entries)
    with zipfile.ZipFile(candidate, "w") as destination:
        for name, payload in entries.items():
            destination.writestr(name, payload)


def test_load_validated_authoring_zip_accepts_exact_four_file_inventory_and_alias(
    tmp_path: Path,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    root = "20260729t120000z-iss-00003-issue-planning-authoring-v1"
    logical = f"{root}.zip"
    authoring = tmp_path / logical
    with zipfile.ZipFile(candidate) as source:
        candidate_root = source.namelist()[0].split("/", 1)[0]
        files = {
            path: source.read(f"{candidate_root}/{path}")
            for path in ("design.md", "plan.md", "requirement.md", COMPANION_PATH)
        }
    _infra().build_deterministic_zip(
        authoring,
        root,
        files,
        datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc),
    )
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["OracleAuthoringZipSnapshot"],
    )
    payload = authoring.read_bytes()
    snapshot = contracts.OracleAuthoringZipSnapshot(
        expected_logical_filename=logical,
        observed_transport_filename=f"{root} (2).zip",
        internal_root=root,
        size_bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        zip_bytes=payload,
    )
    loaded = _infra().load_validated_issue_authoring_payload(
        snapshot,
        expected_companion_path=COMPANION_PATH,
        repo_root=repo,
    )
    assert set(loaded.documents) == {"design.md", "plan.md", "requirement.md"}
    assert loaded.onboarding_companion_path == COMPANION_PATH
    assert loaded.onboarding_companion_bytes == files[COMPANION_PATH]


@pytest.mark.parametrize("damage", ["zero-role", "multiple-role", "checksum", "blob"])
def test_load_verified_candidate_rejects_invalid_companion_binding(
    tmp_path: Path,
    damage: str,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)

    def mutate(entries: dict[str, bytes]) -> None:
        root = candidate.stem
        manifest_name = f"{root}/MANIFEST.json"
        checksums_name = f"{root}/CHECKSUMS.sha256"
        companion_name = f"{root}/{COMPANION_PATH}"
        if damage in {"zero-role", "multiple-role"}:
            manifest = json.loads(entries[manifest_name])
            companion_entry = next(entry for entry in manifest["entries"] if entry["path"] == COMPANION_PATH)
            companion_entry["role"] = "artifact"
            if damage == "multiple-role":
                next(entry for entry in manifest["entries"] if entry["path"] == "design.md")["role"] = (
                    "onboarding-companion"
                )
            entries[manifest_name] = (
                json.dumps(
                    manifest,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
                + b"\n"
            )
        elif damage == "checksum":
            entries[checksums_name] = entries[checksums_name].replace(
                hashlib.sha256(entries[companion_name]).hexdigest().encode(),
                b"0" * 64,
            )
        else:
            entries[companion_name] += b"tampered\n"

    _rewrite_candidate(candidate, mutate)
    with pytest.raises(_infra().CandidateArchiveRejected):
        _infra().load_verified_issue_candidate(candidate, repo)


@pytest.mark.parametrize("renamed", ["candidate-copy.zip", "candidate (0).zip", "candidate.zip.bak"])
def test_load_verified_candidate_rejects_fuzzy_and_unauthorized_rename(
    tmp_path: Path,
    renamed: str,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    target = candidate.with_name(renamed)
    candidate.rename(target)
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(target, repo)


def test_load_verified_candidate_accepts_closed_alias_and_rejects_repack_and_root_mismatch(
    tmp_path: Path,
) -> None:
    repo, candidate, identity = _valid_candidate(tmp_path)
    alias = candidate.with_name(f"{candidate.stem} (2).zip")
    shutil.copyfile(candidate, alias)
    loaded = _infra().load_verified_issue_candidate(alias, repo)
    assert loaded.identity.logical_filename == identity.logical_filename
    assert loaded.identity.observed_transport_filename == alias.name

    repacked = candidate.with_name(identity.logical_filename)
    candidate.unlink()
    with zipfile.ZipFile(alias) as source, zipfile.ZipFile(repacked, "w") as destination:
        for name in source.namelist():
            destination.writestr(name, source.read(name))
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(repacked, repo)

    root_mismatch = candidate.with_name(f"{candidate.stem} (3).zip")
    with zipfile.ZipFile(alias) as source, zipfile.ZipFile(root_mismatch, "w") as destination:
        for name in source.namelist():
            relative = name.split("/", 1)[1]
            destination.writestr(f"wrong-root/{relative}", source.read(name))
    with pytest.raises(ValueError):
        _infra().load_verified_issue_candidate(root_mismatch, repo)


def test_load_verified_candidate_uses_validated_bytes_when_path_is_swapped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    repo, candidate, _ = _valid_candidate(first_root)
    _, other_candidate, _ = _valid_candidate(second_root, body="Different valid content.")
    first_bytes = candidate.read_bytes()
    other_bytes = other_candidate.read_bytes()
    assert first_bytes != other_bytes
    infra = _infra()
    original_review = infra.review_pack_input

    def swap_after_validation(path: Path, *, profile):
        result = original_review(path, profile=profile)
        candidate.write_bytes(other_bytes)
        return result

    monkeypatch.setattr(infra, "review_pack_input", swap_after_validation)
    loaded = infra.load_verified_issue_candidate(candidate, repo)
    assert loaded.zip_bytes == first_bytes
    assert loaded.identity.zip_sha256 == hashlib.sha256(first_bytes).hexdigest()


def test_load_verified_candidate_never_returns_transient_sensitive_malformed_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    original_candidate_bytes = candidate.read_bytes()
    transient_bytes = b"token=abc123secret; not a ZIP"
    infra = _infra()
    original_review = infra.review_pack_input
    original_read_bytes = Path.read_bytes
    restore_on_read = [False]

    def swap_after_validation(path: Path, *, profile):
        result = original_review(path, profile=profile)
        candidate.write_bytes(transient_bytes)
        restore_on_read[0] = True
        return result

    def transient_read(path: Path) -> bytes:
        data = original_read_bytes(path)
        if path == candidate and restore_on_read[0]:
            candidate.write_bytes(original_candidate_bytes)
            restore_on_read[0] = False
        return data

    monkeypatch.setattr(infra, "review_pack_input", swap_after_validation)
    monkeypatch.setattr(Path, "read_bytes", transient_read)
    try:
        loaded = infra.load_verified_issue_candidate(candidate, repo)
    finally:
        candidate.write_bytes(original_candidate_bytes)
    assert loaded.zip_bytes == original_candidate_bytes
    assert b"abc123secret" not in loaded.zip_bytes


def test_load_verified_candidate_fifo_swap_is_nonblocking_and_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, candidate, _ = _valid_candidate(tmp_path)
    infra = _infra()
    original_open = infra.os.open
    swapped = [False]

    def swap_before_open(path, flags, *args, **kwargs):
        if (Path(path) == candidate or (path == candidate.name and kwargs.get("dir_fd") is not None)) and not swapped[
            0
        ]:
            swapped[0] = True
            candidate.unlink()
            os.mkfifo(candidate)
            assert flags & infra.os.O_NONBLOCK
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(infra.os, "open", swap_before_open)
    with pytest.raises(ValueError):
        infra.load_verified_issue_candidate(candidate, repo)
    assert swapped == [True]


def test_load_verified_candidate_parent_swap_never_redirects_into_repo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_root = tmp_path / "external"
    repo_root = tmp_path / "repo-side"
    external_root.mkdir()
    repo_root.mkdir()
    repo, candidate, _ = _valid_candidate(external_root)
    _, repo_candidate, _ = _valid_candidate(repo_root, body="Repository secret data.")
    original_bytes = candidate.read_bytes()
    redirected_bytes = repo_candidate.read_bytes()
    assert original_bytes != redirected_bytes
    redirected = repo / candidate.name
    shutil.copyfile(repo_candidate, redirected)
    parent = candidate.parent
    backup = tmp_path / "external-parent-backup"
    infra = _infra()
    original_open = infra.os.open
    swapped = [False]

    def swap_parent() -> None:
        if swapped[0]:
            return
        swapped[0] = True
        parent.rename(backup)
        parent.symlink_to(repo, target_is_directory=True)

    def swap_during_open(path, flags, *args, **kwargs):
        if Path(path) == candidate and not swapped[0]:
            swap_parent()
            return original_open(path, flags, *args, **kwargs)
        if path == parent.name and flags & getattr(os, "O_DIRECTORY", 0) and not swapped[0]:
            descriptor = original_open(path, flags, *args, **kwargs)
            swap_parent()
            return descriptor
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(infra.os, "open", swap_during_open)
    loaded = infra.load_verified_issue_candidate(candidate, repo)
    assert loaded.zip_bytes == original_bytes
    assert redirected_bytes not in loaded.zip_bytes
    assert swapped == [True]
