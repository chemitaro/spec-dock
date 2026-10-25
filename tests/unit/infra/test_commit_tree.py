"""Read one commit tree and its blobs without touching the working tree or index."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.commit_tree import TreeEntry, list_commit_tree, read_blob, resolve_commit

if TYPE_CHECKING:
    from pathlib import Path


def _git(root: Path, *args: str, stdin: bytes | None = None) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, input=stdin).stdout.decode()


def _repository(root: Path) -> Path:
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "--local", "maintenance.auto", "false")
    return root


def _commit(root: Path, *, stage: bool = True) -> str:
    if stage:
        _git(root, "add", "--all")
    _git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
    return _git(root, "rev-parse", "HEAD").strip()


def test_resolve_commit_returns_the_full_commit_or_none(tmp_path: Path) -> None:
    root = _repository(tmp_path / "repo")
    assert resolve_commit(root, "HEAD", timeout=30) is None
    (root / "file.txt").write_text("one\n", encoding="utf-8")
    head = _commit(root)
    assert resolve_commit(root, "HEAD", timeout=30) == head
    assert resolve_commit(root, "main", timeout=30) == head
    assert resolve_commit(root, "missing-branch", timeout=30) is None
    assert resolve_commit(root, "--output=/dev/null", timeout=30) is None


def test_list_commit_tree_names_regular_symlink_and_gitlink_entries(tmp_path: Path) -> None:
    root = _repository(tmp_path / "repo")
    (root / "spec-dock").mkdir()
    (root / "spec-dock/workspace.json").write_text("{}\n", encoding="utf-8")
    script = root / "spec-dock/run"
    script.write_text("#!/bin/sh\n", encoding="utf-8")
    script.chmod(0o755)
    (root / "spec-dock/initiatives").symlink_to(".canonical")
    (root / "café.md").write_text("accent\n", encoding="utf-8")
    first = _commit(root)
    _git(root, "update-index", "--add", "--cacheinfo", f"160000,{first},spec-dock/.canonical")
    head = _commit(root, stage=False)
    blob = _git(root, "rev-parse", "HEAD:spec-dock/workspace.json").strip()

    entries = list_commit_tree(root, head, timeout=30)

    by_path = {entry.path: entry for entry in entries}
    assert set(by_path) == {
        "café.md",
        "spec-dock/.canonical",
        "spec-dock/initiatives",
        "spec-dock/run",
        "spec-dock/workspace.json",
    }
    assert by_path["spec-dock/workspace.json"] == TreeEntry("spec-dock/workspace.json", "regular", blob)
    assert by_path["spec-dock/run"].kind == "regular"
    assert by_path["spec-dock/initiatives"].kind == "symlink"
    assert by_path["spec-dock/.canonical"] == TreeEntry("spec-dock/.canonical", "gitlink", first)
    assert [entry.path for entry in entries] == sorted(by_path, key=lambda path: path.encode())


def test_read_blob_returns_committed_bytes_not_the_working_tree(tmp_path: Path) -> None:
    root = _repository(tmp_path / "repo")
    path = root / "data.bin"
    path.write_bytes(b"\x00committed\r\n")
    head = _commit(root)
    path.write_bytes(b"edited in the working tree\n")
    (entry,) = list_commit_tree(root, head, timeout=30)

    assert read_blob(root, entry.object_id, timeout=30) == b"\x00committed\r\n"


def test_a_path_that_is_not_utf8_is_listed_with_escaped_bytes(tmp_path: Path) -> None:
    root = _repository(tmp_path / "repo")
    (root / "keep.txt").write_text("keep\n", encoding="utf-8")
    _commit(root)
    blob = _git(root, "hash-object", "-w", "--stdin", stdin=b"latin-1 name\n").strip()
    subprocess.run(
        [
            b"git",
            b"-C",
            bytes(root),
            b"update-index",
            b"--add",
            b"--cacheinfo",
            f"100644,{blob},".encode() + b"caf\xe9.md",
        ],
        check=True,
    )
    head = _commit(root, stage=False)

    paths = [entry.path for entry in list_commit_tree(root, head, timeout=30)]

    assert paths == ["caf\\xe9.md", "keep.txt"]
