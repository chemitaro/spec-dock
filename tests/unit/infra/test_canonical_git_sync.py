"""Git operations of the periodic sync on a temporary catalog-like repository (iss-00430)."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.domain.canonical_sync_rules import resolve_conflicts
from spec_dock.runtime.infra import canonical_git
from tests.support.canonical_repo import configure, git

if TYPE_CHECKING:
    from pathlib import Path

NOW = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def catalog(tmp_path: Path) -> Path:
    root = tmp_path / "catalog"
    git(tmp_path, "init", "-q", "--initial-branch=spec-dock/canonical", str(root))
    configure(root)
    (root / ".gitignore").write_text(".runtime/\n")
    (root / "a.md").write_text("a\n")
    (root / "b.md").write_text("b\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    (root / ".runtime").mkdir()
    return root


def test_list_changes_reports_edits_additions_and_deletions_against_head(catalog: Path) -> None:
    (catalog / "a.md").write_text("changed\n")
    (catalog / "b.md").unlink()
    (catalog / "new dir").mkdir()
    (catalog / "new dir/c.md").write_text("c\n")
    git(catalog, "add", "new dir/c.md")  # someone staged it; the sync still sees it as unsaved after reset
    canonical_git.reset_index(catalog)
    changes = {change.path: change for change in canonical_git.list_changes(catalog)}
    assert sorted(changes) == ["a.md", "b.md", "new dir/c.md"]
    assert (changes["a.md"].kind, changes["b.md"].kind, changes["new dir/c.md"].kind) == (
        "modified",
        "deleted",
        "added",
    )
    assert changes["b.md"].mtime is None
    assert changes["a.md"].mtime is not None and changes["a.md"].mtime.tzinfo is not None
    assert git(catalog, "diff", "--cached", "--name-only") == ""


def test_save_commit_commits_only_the_given_paths_and_keeps_the_rest_unsaved(catalog: Path) -> None:
    hooks = catalog / ".git/hooks"
    hooks.mkdir(exist_ok=True)
    for name in ("pre-commit", "commit-msg", "post-commit", "reference-transaction"):
        (hooks / name).write_text("#!/bin/sh\nexit 1\n")
        (hooks / name).chmod(0o755)
    git(catalog, "config", "commit.gpgSign", "true")
    head = git(catalog, "rev-parse", "HEAD")
    (catalog / "a.md").write_text("saved\n")
    (catalog / "b.md").unlink()
    (catalog / "later.md").write_text("later\n")
    commit = canonical_git.save_commit(
        catalog, ["a.md", "b.md"], message="spec-dock: save 2 files (mac)", parent=head
    ).commit
    assert git(catalog, "rev-parse", "HEAD") == commit
    assert git(catalog, "show", "-s", "--format=%P %s", commit) == f"{head} spec-dock: save 2 files (mac)"
    assert git(catalog, "show", "HEAD:a.md") == "saved"
    assert git(catalog, "ls-tree", "--name-only", "HEAD").splitlines() == [".gitignore", "a.md"]
    assert git(catalog, "status", "--porcelain") == "?? later.md"
    assert not (catalog / ".runtime/index.tmp").exists()


def test_save_commit_refuses_to_move_a_branch_that_moved(catalog: Path) -> None:
    head = git(catalog, "rev-parse", "HEAD")
    (catalog / "a.md").write_text("one\n")
    canonical_git.save_commit(catalog, ["a.md"], message="m", parent=head)
    (catalog / "b.md").write_text("two\n")
    with pytest.raises(canonical_git.GitProcessError):
        canonical_git.save_commit(catalog, ["b.md"], message="m", parent=head)


def _branch_commit(catalog: Path, base: str, files: dict[str, str | None], message: str) -> str:
    """A commit on top of `base` made without touching the catalog work tree."""
    index = catalog / ".git/test-index"
    environment = {**os.environ, "GIT_INDEX_FILE": str(index)}
    import subprocess

    def run(*args: str, data: bytes | None = None) -> str:
        return (
            subprocess
            .run(["git", "-C", str(catalog), *args], check=True, capture_output=True, env=environment, input=data)
            .stdout.decode()
            .strip()
        )

    run("read-tree", base)
    for path, content in files.items():
        if content is None:
            run("rm", "-q", "--cached", "--", path)
        else:
            oid = run("hash-object", "-w", "--stdin", data=content.encode())
            run("update-index", "--add", "--cacheinfo", f"100644,{oid},{path}")
    tree = run("write-tree")
    index.unlink()
    return run("commit-tree", tree, "-p", base, "-m", message)


def test_a_conflicting_merge_keeps_the_remote_version_and_a_local_copy(catalog: Path) -> None:
    base = git(catalog, "rev-parse", "HEAD")
    local = _branch_commit(catalog, base, {"a.md": "local\n", "b.md": None}, "local")
    remote = _branch_commit(catalog, base, {"a.md": "remote\n", "b.md": "remote b\n"}, "remote")
    result = canonical_git.merge_tree(catalog, local, remote)
    assert result.code == 1 and result.tree is not None
    assert {(entry.stage, entry.path) for entry in result.entries} == {
        (1, "a.md"),
        (2, "a.md"),
        (3, "a.md"),
        (1, "b.md"),
        (3, "b.md"),
    }
    resolution = resolve_conflicts(
        result.entries, pc="mac", now=NOW, taken=canonical_git.tree_paths(catalog, result.tree)
    )
    tree = canonical_git.write_resolution(catalog, result.tree, resolution)
    merged = canonical_git.commit_merge(catalog, tree, local, remote, message="spec-dock: merge (mac)")
    files = {path: git(catalog, "show", f"{merged}:{path}") for path in canonical_git.tree_paths(catalog, tree)}
    assert files == {
        ".gitignore": ".runtime/",
        "a.md": "remote",
        "a.conflict-mac-20261026T120000Z.md": "local",
        "b.md": "remote b",
    }
    assert "<<<<<<<" not in "".join(files.values())
    assert git(catalog, "show", "-s", "--format=%P", merged) == f"{local} {remote}"


def test_unrelated_histories_fail_unless_explicitly_allowed(catalog: Path) -> None:
    head = git(catalog, "rev-parse", "HEAD")
    empty_tree = git(catalog, "hash-object", "-t", "tree", "-w", "--stdin", input=b"")
    orphan = git(catalog, "commit-tree", empty_tree, "-m", "orphan")
    other = _branch_commit(catalog, orphan, {"other.md": "o\n"}, "other")
    failed = canonical_git.merge_tree(catalog, head, other)
    assert failed.code >= 2 and failed.tree is None and "unrelated" in failed.message
    allowed = canonical_git.merge_tree(catalog, head, other, allow_unrelated=True)
    assert allowed.code == 0 and allowed.tree is not None
    assert canonical_git.tree_paths(catalog, allowed.tree) == {".gitignore", "a.md", "b.md", "other.md"}


def test_fast_forward_refuses_to_overwrite_a_local_edit_and_changes_nothing(catalog: Path) -> None:
    base = git(catalog, "rev-parse", "HEAD")
    remote = _branch_commit(catalog, base, {"a.md": "remote\n"}, "remote")
    assert canonical_git.is_ancestor(catalog, base, remote) and not canonical_git.is_ancestor(catalog, remote, base)
    assert canonical_git.changed_paths(catalog, base, remote) == {"a.md"}
    (catalog / "a.md").write_text("editing\n")
    with pytest.raises(canonical_git.GitProcessError):
        canonical_git.fast_forward(catalog, remote)
    assert (catalog / "a.md").read_text() == "editing\n" and git(catalog, "rev-parse", "HEAD") == base
    (catalog / "a.md").write_text("a\n")
    canonical_git.fast_forward(catalog, remote)
    assert (catalog / "a.md").read_text() == "remote\n"


def test_restore_ignored_files_and_operations_in_progress(catalog: Path) -> None:
    (catalog / "a.md").unlink()
    (catalog / "b.md").write_text("held edit\n")
    canonical_git.restore_from_head(catalog, ["a.md"])
    assert (catalog / "a.md").read_text() == "a\n" and (catalog / "b.md").read_text() == "held edit\n"
    (catalog / ".runtime/changesets").mkdir()
    (catalog / ".runtime/changesets/x.json").write_text("{}")
    assert canonical_git.ignored_files(catalog) == ()
    (catalog / ".gitignore").write_text(".runtime/\nscratch/\n")
    (catalog / "scratch").mkdir()
    (catalog / "scratch/notes.txt").write_text("keep me")
    assert canonical_git.ignored_files(catalog) == ("scratch/notes.txt",)
    assert canonical_git.operation_in_progress(catalog / ".git") is None
    (catalog / ".git/MERGE_HEAD").write_text("x")
    assert canonical_git.operation_in_progress(catalog / ".git") == "MERGE_HEAD"


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr", "outcome"),
    [
        (0, b"To r\n*\tHEAD:refs/heads/spec-dock/canonical\t[new branch]\nDone\n", b"", "pushed"),
        (0, b"To r\n \tHEAD:refs/heads/spec-dock/canonical\ta..b\nDone\n", b"", "pushed"),
        (0, b"To r\n=\tHEAD:refs/heads/spec-dock/canonical\t[up to date]\nDone\n", b"", "up_to_date"),
        (1, b"To r\n!\tHEAD:refs/heads/spec-dock/canonical\t[rejected] (fetch first)\nDone\n", b"", "rejected"),
        (128, b"", b"fatal: Authentication failed for 'https://github.com/o/r.git/'\n", "auth_failed"),
        (
            128,
            b"",
            b"fatal: could not read Username for 'https://github.com': terminal prompts disabled\n",
            "auth_failed",
        ),
        (128, b"", b"git@github.com: Permission denied (publickey).\n", "auth_failed"),
        (1, b"To r\n!\tHEAD:refs/heads/spec-dock/canonical\t[remote rejected] (hook declined)\n", b"", "failed"),
        (128, b"", b"fatal: unable to access: Could not resolve host\n", "failed"),
    ],
)
def test_push_results_are_classified(returncode: int, stdout: bytes, stderr: bytes, outcome: str) -> None:
    assert canonical_git.classify_push(returncode, stdout, stderr).outcome == outcome


def test_save_commit_stores_the_checked_bytes_not_a_later_write(catalog: Path) -> None:
    head = git(catalog, "rev-parse", "HEAD")
    (catalog / "a.md").write_text("ghp_ secret written a moment later\n")
    canonical_git.save_commit(catalog, ["a.md"], message="m", parent=head, contents={"a.md": b"checked\n"})
    assert git(catalog, "show", "HEAD:a.md") == "checked"


def test_the_auth_next_step_depends_on_the_remote_kind() -> None:
    from spec_dock.runtime.application.canonical_sync import auth_next_step

    assert "gh auth setup-git" in auth_next_step("https://github.com/o/r.git")
    assert "https" in auth_next_step("git@github.com:o/r.git") and "SSH" in auth_next_step("ssh://git@github.com/o/r")


def test_checked_bytes_keep_the_mode_git_would_choose(catalog: Path) -> None:
    git(catalog, "config", "core.fileMode", "false")
    head = git(catalog, "rev-parse", "HEAD")
    (catalog / "tool.sh").write_text("echo\n")
    (catalog / "tool.sh").chmod(0o755)
    canonical_git.save_commit(catalog, ["tool.sh"], message="m", parent=head, contents={"tool.sh": b"echo\n"})
    assert git(catalog, "ls-tree", "HEAD", "tool.sh").split()[0] == "100644"


def test_authentication_is_recognised_in_any_locale() -> None:
    assert canonical_git.UNTRANSLATED == {"LC_ALL": "C"}
    assert canonical_git.is_auth_failure("fatal: Authentication failed for 'https://github.com/o/r.git/'")
