"""The single Git entry point for the catalog (contract C6) and the catalog Git operations of I-2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spec_dock.runtime.domain.canonical_content import CANONICAL_ROOT_FILES
from spec_dock.runtime.infra import canonical_git as cg
from spec_dock.runtime.infra.git_process import GitProcessError
from tests.support.canonical_repo import bare_remote, clone, git, isolate_user_state


@pytest.fixture
def isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    return isolate_user_state(monkeypatch, tmp_path)


pytestmark = pytest.mark.usefixtures("isolated")


def _recording_git(tmp_path: Path, *, exit_code: int = 0) -> tuple[Path, Path]:
    log = tmp_path / "argv.jsonl"
    script = tmp_path / "fake-git"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        f"with open({str(log)!r}, 'a') as stream:\n"
        "    env = {k: v for k, v in os.environ.items() if k.startswith('GIT_')}\n"
        "    files = [open(a.split('=', 1)[1], 'rb').read().decode() for a in sys.argv if a.startswith('--pathspec-from-file=')]\n"
        "    stream.write(json.dumps({'argv': sys.argv[1:], 'env': env, 'files': files}) + '\\n')\n"
        f"sys.exit({exit_code})\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script, log


def _calls(log: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_every_call_disables_hooks_and_signing_and_drops_inherited_git_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script, log = _recording_git(tmp_path)
    monkeypatch.setenv("GIT_DIR", "/elsewhere")
    cg.run_catalog_git(tmp_path, "status", git=str(script))
    (call,) = _calls(log)
    assert call["argv"] == [
        "-C",
        str(tmp_path),
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "commit.gpgSign=false",
        "-c",
        "push.gpgSign=false",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "gc.auto=0",
        "-c",
        "maintenance.auto=false",
        "status",
    ]
    assert call["env"] == {"GIT_TERMINAL_PROMPT": "0"}


def test_identity_and_ssh_variables_pass_while_repository_overrides_are_dropped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script, log = _recording_git(tmp_path)
    for key, value in {
        "GIT_AUTHOR_NAME": "CI",
        "GIT_AUTHOR_EMAIL": "ci@example.invalid",
        "GIT_COMMITTER_NAME": "CI",
        "GIT_COMMITTER_EMAIL": "ci@example.invalid",
        "GIT_SSH_COMMAND": "ssh -i key",
        "GIT_WORK_TREE": "/elsewhere",
        "GIT_INDEX_FILE": "/elsewhere/index",
        "GIT_CONFIG_PARAMETERS": "'core.hooksPath'='/x'",
    }.items():
        monkeypatch.setenv(key, value)
    cg.run_catalog_git(tmp_path, "commit-tree", git=str(script))
    (call,) = _calls(log)
    assert call["env"] == {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": "CI",
        "GIT_AUTHOR_EMAIL": "ci@example.invalid",
        "GIT_COMMITTER_NAME": "CI",
        "GIT_COMMITTER_EMAIL": "ci@example.invalid",
        "GIT_SSH_COMMAND": "ssh -i key",
    }


def test_read_only_calls_take_no_optional_locks_and_explicit_variables_pass(tmp_path: Path) -> None:
    script, log = _recording_git(tmp_path)
    cg.run_catalog_git(tmp_path, "status", git=str(script), read_only=True, environment={"GIT_INDEX_FILE": "/x/index"})
    (call,) = _calls(log)
    assert call["argv"][-3:] == ["maintenance.auto=false", "--no-optional-locks", "status"]
    assert call["env"] == {"GIT_TERMINAL_PROMPT": "0", "GIT_INDEX_FILE": "/x/index"}


def test_paths_go_through_a_literal_nul_separated_pathspec_file(tmp_path: Path) -> None:
    script, log = _recording_git(tmp_path)
    cg.run_catalog_git(tmp_path, "add", "-A", git=str(script), pathspecs=["a b/*.md", ":(glob)x"])
    (call,) = _calls(log)
    argv = call["argv"]
    assert "--literal-pathspecs" in argv and argv.index("--literal-pathspecs") < argv.index("add")
    assert argv[-1] == "--pathspec-file-nul" and argv[-2].startswith("--pathspec-from-file=")
    assert call["files"] == ["a b/*.md\0:(glob)x\0"]
    assert not Path(argv[-2].split("=", 1)[1]).exists()


def test_unexpected_exit_codes_raise_with_the_native_details(tmp_path: Path) -> None:
    script, _log = _recording_git(tmp_path, exit_code=2)
    assert cg.run_catalog_git(tmp_path, "x", git=str(script), returncodes=frozenset({0, 2})).returncode == 2
    with pytest.raises(GitProcessError) as raised:
        cg.run_catalog_git(tmp_path, "x", git=str(script))
    assert raised.value.returncode == 2 and not raised.value.uncertain


def test_a_timed_out_mutation_is_uncertain(tmp_path: Path) -> None:
    slow = tmp_path / "slow-git"
    slow.write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    slow.chmod(0o755)
    with pytest.raises(GitProcessError) as raised:
        cg.run_catalog_git(tmp_path, "push", git=str(slow), mutation=True, timeout=0.2)
    assert raised.value.timed_out and raised.value.uncertain


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    remote = bare_remote(tmp_path / "remote.git")
    return clone(remote, tmp_path / "main")


def test_remote_canonical_reports_absent_then_present(repo: Path) -> None:
    assert cg.remote_canonical(repo) == "absent"
    oid = cg.create_initial_commit(repo)
    assert cg.push_initial(repo, oid) == "pushed"
    assert cg.remote_canonical(repo) == "present"


def test_an_unreachable_remote_raises(repo: Path) -> None:
    git(repo, "remote", "set-url", "origin", str(repo.parent / "missing.git"))
    with pytest.raises(GitProcessError):
        cg.remote_canonical(repo)


def test_the_initial_commit_has_no_parent_and_only_the_format_files(repo: Path) -> None:
    oid = cg.create_initial_commit(repo)
    assert git(repo, "rev-list", "--parents", "-n", "1", oid) == oid
    names = git(repo, "ls-tree", "--name-only", oid).splitlines()
    assert sorted(names) == sorted(CANONICAL_ROOT_FILES)
    for name, payload in CANONICAL_ROOT_FILES.items():
        assert (
            git(repo, "cat-file", "blob", f"{oid}:{name}").encode() + b"\n" == payload
            or (git(repo, "cat-file", "-p", f"{oid}:{name}") + "\n").encode() == payload
        )
    assert git(repo, "log", "-1", "--format=%s", oid) == "spec-dock: create canonical"
    assert cg.is_initial_commit(repo, oid)
    assert cg.resolve_commit(repo, "refs/heads/spec-dock/canonical") is None


def test_a_commit_with_content_is_not_the_initial_commit(repo: Path) -> None:
    oid = cg.create_initial_commit(repo)
    blob = git(repo, "hash-object", "-w", "--stdin", input=b"spec\n")
    tree = git(repo, "mktree", input=f"100644 blob {blob}\tinit-00001-x.md\n".encode())
    other = git(repo, "commit-tree", tree, "-p", oid, "-m", "save")
    assert not cg.is_initial_commit(repo, other)
    child = git(repo, "commit-tree", git(repo, "rev-parse", f"{oid}^{{tree}}"), "-p", oid, "-m", "again")
    assert not cg.is_initial_commit(repo, child)


def test_a_second_unrelated_initial_commit_is_rejected(repo: Path, tmp_path: Path) -> None:
    first = cg.create_initial_commit(repo)
    assert cg.push_initial(repo, first) == "pushed"
    other = clone(repo.parent / "remote.git", tmp_path / "other")
    git(other, "config", "user.name", "Other PC")
    second = cg.create_initial_commit(other)
    assert second != first
    assert cg.push_initial(other, second) == "rejected"


def test_an_identical_initial_commit_from_the_same_identity_counts_as_pushed(repo: Path, tmp_path: Path) -> None:
    first = cg.create_initial_commit(repo)
    assert cg.push_initial(repo, first) == "pushed"
    assert cg.push_initial(repo, first) == "pushed"


def test_a_ref_the_remote_refuses_is_a_failure_not_a_canonical_created_first(repo: Path) -> None:
    # A branch named spec-dock on GitHub makes spec-dock/canonical impossible ([remote rejected], not [rejected]).
    git(repo, "push", "-q", "origin", "HEAD:refs/heads/spec-dock")
    with pytest.raises(GitProcessError) as raised:
        cg.push_initial(repo, cg.create_initial_commit(repo))
    assert b"spec-dock" in raised.value.stderr + (raised.value.stdout or b"")


def test_fetching_the_canonical_does_not_recurse_into_submodules(repo: Path, tmp_path: Path) -> None:
    library = tmp_path / "library"
    git(tmp_path, "init", "-q", "-b", "main", str(library))
    git(library, "-c", "user.name=F", "-c", "user.email=f@example.invalid", "commit", "-q", "--allow-empty", "-m", "x")
    git(repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(library), "library")
    git(repo, "commit", "-qm", "submodule")
    git(repo / "library", "remote", "set-url", "origin", str(tmp_path / "unreachable"))
    git(repo, "config", "submodule.recurse", "true")
    oid = cg.create_initial_commit(repo)
    cg.push_initial(repo, oid)
    cg.fetch_canonical(repo)
    assert cg.resolve_commit(repo, "refs/remotes/origin/spec-dock/canonical") == oid


def test_fetch_coverage_follows_the_configured_refspecs(repo: Path, tmp_path: Path) -> None:
    assert cg.fetch_covers_canonical(repo)
    single = clone(repo.parent / "remote.git", tmp_path / "single", "--single-branch", "--branch", "main")
    assert not cg.fetch_covers_canonical(single)
    cg.add_fetch_branch(single)
    assert cg.fetch_covers_canonical(single)


def test_fetching_the_canonical_updates_the_tracking_ref(repo: Path) -> None:
    oid = cg.create_initial_commit(repo)
    cg.push_initial(repo, oid)
    cg.fetch_canonical(repo)
    assert cg.resolve_commit(repo, "refs/remotes/origin/spec-dock/canonical") == oid


def test_tree_has_path_checks_a_committed_tree(repo: Path) -> None:
    assert cg.tree_has_path(repo, "HEAD", "spec-dock/workspace.json")
    assert not cg.tree_has_path(repo, "HEAD", "spec-dock/initiatives")


def _failing_hooks(repo: Path) -> None:
    hooks = repo / ".git" / "failing-hooks"
    hooks.mkdir()
    for name in ("post-checkout", "pre-push", "pre-commit", "post-merge", "reference-transaction"):
        hook = hooks / name
        hook.write_text("#!/bin/sh\necho hook ran >&2\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
    git(repo, "config", "core.hooksPath", str(hooks))
    git(repo, "config", "commit.gpgSign", "true")
    git(repo, "config", "gpg.program", "/nonexistent-gpg")


def test_catalog_worktree_operations_ignore_failing_hooks_and_signing(repo: Path) -> None:
    _failing_hooks(repo)
    oid = cg.create_initial_commit(repo)
    assert cg.push_initial(repo, oid) == "pushed"
    cg.fetch_canonical(repo)
    catalog = repo / "spec-dock/.canonical"
    cg.add_catalog_worktree(repo, catalog, mode="track")
    cg.lock_worktree(repo, catalog)
    (entry,) = [item for item in cg.list_worktrees(repo) if item.branch == "spec-dock/canonical"]
    assert entry.path == catalog and entry.locked and entry.locked_reason == "spec-dock canonical catalog"
    admin = cg.read_gitdir(catalog)
    assert admin is not None and admin.parent == repo / ".git/worktrees"
    assert cg.admin_branch(admin) == "spec-dock/canonical" and cg.admin_worktree_path(admin) == catalog
    assert git(repo, "config", "--get", "branch.spec-dock/canonical.merge") == "refs/heads/spec-dock/canonical"


def test_a_missing_locked_catalog_is_re_added_without_pruning_other_worktrees(repo: Path, tmp_path: Path) -> None:
    import shutil

    oid = cg.create_initial_commit(repo)
    cg.push_initial(repo, oid)
    cg.fetch_canonical(repo)
    catalog = repo / "spec-dock/.canonical"
    cg.add_catalog_worktree(repo, catalog, mode="track")
    cg.lock_worktree(repo, catalog)
    git(repo, "worktree", "add", "-q", "-b", "gone", str(tmp_path / "gone"))
    shutil.rmtree(tmp_path / "gone")
    shutil.rmtree(catalog)
    before = sorted(path.name for path in (repo / ".git/worktrees").iterdir())
    cg.add_catalog_worktree(repo, catalog, mode="readd")
    assert sorted(path.name for path in (repo / ".git/worktrees").iterdir()) == before
    gone = [item for item in cg.list_worktrees(repo) if item.branch == "gone"]
    assert gone and gone[0].prunable


def test_the_change_summary_counts_unsaved_paths_and_conflict_copies(repo: Path) -> None:
    oid = cg.create_initial_commit(repo)
    cg.push_initial(repo, oid)
    cg.fetch_canonical(repo)
    catalog = repo / "spec-dock/.canonical"
    cg.add_catalog_worktree(repo, catalog, mode="track")
    assert cg.catalog_change_summary(catalog) == cg.CatalogChangeSummary(0, ())
    assert cg.unpushed(catalog) == (0, None)
    (catalog / "init-00001-x").mkdir()
    (catalog / "init-00001-x/plan.md").write_text("x\n", encoding="utf-8")
    (catalog / "init-00001-x/plan.conflict-mac-20261025T120000Z.md").write_text("y\n", encoding="utf-8")
    (catalog / "README.md").write_text("changed\n", encoding="utf-8")
    (catalog / ".runtime").mkdir()
    (catalog / ".runtime/ignored.json").write_text("{}", encoding="utf-8")
    summary = cg.catalog_change_summary(catalog)
    assert summary.unsaved == 3
    assert summary.conflict_files == ("init-00001-x/plan.conflict-mac-20261025T120000Z.md",)
    git(catalog, "add", "-A")
    git(catalog, "commit", "-qm", "local save")
    count, oldest = cg.unpushed(catalog) or (None, None)
    assert count == 1 and oldest is not None


def test_resetting_the_branch_requires_its_expected_old_value(repo: Path) -> None:
    first = cg.create_initial_commit(repo)
    git(repo, "branch", "spec-dock/canonical", first)
    blob = git(repo, "hash-object", "-w", "--stdin", input=b"x\n")
    other = git(repo, "commit-tree", git(repo, "mktree", input=f"100644 blob {blob}\tx\n".encode()), "-m", "other")
    with pytest.raises(GitProcessError):
        cg.reset_branch(repo, other, expected=other)
    cg.reset_branch(repo, other, expected=first)
    assert cg.resolve_commit(repo, "refs/heads/spec-dock/canonical") == other
