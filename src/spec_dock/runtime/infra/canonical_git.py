"""The only path SpecDock uses to run Git for the catalog: hooks and signing are always off (contract C6).

Callers in canonical mode (link, status, sync, restore, remove, finish) run catalog Git through
run_catalog_git; never call Git for the catalog another way.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import fnmatch
import os
from pathlib import Path
import subprocess
import tempfile
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.canonical_content import CANONICAL_ROOT_FILES, INITIAL_COMMIT_MESSAGE
from spec_dock.runtime.domain.canonical_layout import (
    CANONICAL_BRANCH,
    CANONICAL_REF,
    CANONICAL_REMOTE,
    CANONICAL_TRACKING_REF,
    CATALOG_LOCK_REASON,
)
from spec_dock.runtime.infra.git_cli import _parse_worktree_porcelain_nul, sanitized_git_environment
from spec_dock.runtime.infra.git_process import GitProcessError

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from spec_dock.runtime.application.contracts import GitWorktreeRecord
    from spec_dock.runtime.domain.canonical_sync_rules import CatalogChange, ChangeKind, ConflictEntry, Resolution

# Hooks, signing, fsmonitor hooks and automatic gc/maintenance (whose worktree prune SpecDock never runs) are off.
HOOKLESS_CONFIG: Final = (
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
)
# Identity and transport settings do not redirect the repository; CI and containers often carry them only here.
PASSED_GIT_VARIABLES: Final = (
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
)
AddMode = Literal["track", "local", "readd"]
_FETCH_REFSPEC: Final = f"+{CANONICAL_REF}:{CANONICAL_TRACKING_REF}"


@dataclass(frozen=True)
class GitOutput:
    returncode: int
    stdout: bytes
    stderr: bytes


def run_catalog_git(
    cwd: Path,
    *args: str,
    git: str = "git",
    read_only: bool = False,
    mutation: bool = False,
    timeout: float = 30.0,
    pathspecs: Sequence[str] | None = None,
    environment: Mapping[str, str] | None = None,
    input: bytes | None = None,
    returncodes: frozenset[int] = frozenset({0}),
) -> GitOutput:
    """Run `git -C cwd -c core.hooksPath=/dev/null -c commit.gpgSign=false [...] args`.

    read_only adds --no-optional-locks; pathspecs go through --literal-pathspecs and a NUL file.
    Inherited GIT_* variables are dropped except the identity and SSH ones (PASSED_GIT_VARIABLES);
    GIT_TERMINAL_PROMPT=0 keeps HTTPS credential prompts off the terminal.
    """
    options = [*HOOKLESS_CONFIG]
    if read_only:
        options.append("--no-optional-locks")
    if pathspecs is not None:
        options.append("--literal-pathspecs")
    env = sanitized_git_environment()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env.update({key: os.environ[key] for key in PASSED_GIT_VARIABLES if key in os.environ})
    env.update(environment or {})
    spec_file: str | None = None
    try:
        tail: list[str] = []
        if pathspecs is not None:
            descriptor, spec_file = tempfile.mkstemp(prefix="spec-dock-pathspec-")
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"".join(os.fsencode(path) + b"\0" for path in pathspecs))
            tail = [f"--pathspec-from-file={spec_file}", "--pathspec-file-nul"]
        argv = (git, "-C", str(cwd), *options, *args, *tail)
        try:
            completed = subprocess.run(argv, capture_output=True, check=False, env=env, input=input, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            stderr = error.stderr if isinstance(error.stderr, bytes) else b""
            stdout = error.stdout if isinstance(error.stdout, bytes) else b""
            raise GitProcessError(argv, stderr, None, uncertain=mutation, stdout=stdout, timed_out=True) from error
        except OSError as error:
            raise GitProcessError(argv, str(error).encode(), None) from error
        if completed.returncode not in returncodes:
            raise GitProcessError(
                argv,
                completed.stderr,
                completed.returncode,
                uncertain=mutation and completed.returncode < 0,
                stdout=completed.stdout,
            )
        return GitOutput(completed.returncode, completed.stdout, completed.stderr)
    finally:
        if spec_file is not None:
            Path(spec_file).unlink()


def _text(output: GitOutput) -> str:
    return os.fsdecode(output.stdout).strip()


def list_worktrees(main: Path, *, timeout: float = 30.0) -> tuple[GitWorktreeRecord, ...]:
    output = run_catalog_git(main, "worktree", "list", "--porcelain", "-z", read_only=True, timeout=timeout)
    return tuple(_parse_worktree_porcelain_nul(os.fsdecode(output.stdout)))


def read_gitdir(directory: Path) -> Path | None:
    """The administrative directory a linked worktree's `.git` file names, or None when it is not such a file."""
    marker = directory / ".git"
    try:
        if not marker.is_file() or marker.is_symlink():
            return None
        text = marker.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("gitdir: "):
        return None
    target = Path(text.removeprefix("gitdir: ").strip())
    return target if target.is_absolute() else Path(os.path.normpath(directory / target))


def admin_branch(admin_dir: Path) -> str | None:
    """The branch an administrative directory's HEAD names, read without Git."""
    try:
        head = (admin_dir / "HEAD").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return head.removeprefix("ref: refs/heads/") if head.startswith("ref: refs/heads/") else None


def admin_worktree_path(admin_dir: Path) -> Path | None:
    """The worktree path an administrative directory's `gitdir` file records."""
    try:
        recorded = Path((admin_dir / "gitdir").read_text(encoding="utf-8").strip())
    except (OSError, UnicodeDecodeError):
        return None
    if not recorded.is_absolute():
        recorded = Path(os.path.normpath(admin_dir / recorded))
    return recorded.parent


def lock_worktree(main: Path, catalog: Path, *, timeout: float = 30.0) -> None:
    run_catalog_git(
        main, "worktree", "lock", "--reason", CATALOG_LOCK_REASON, str(catalog), mutation=True, timeout=timeout
    )


def repair_worktree(main: Path, catalog: Path, *, timeout: float = 30.0) -> None:
    """Git also reconnects linked worktrees that did not move (repair_worktrees)."""
    run_catalog_git(main, "worktree", "repair", str(catalog), mutation=True, timeout=timeout)


def add_catalog_worktree(main: Path, catalog: Path, *, mode: AddMode, timeout: float = 30.0) -> None:
    args: tuple[str, ...]
    if mode == "track":
        args = ("worktree", "add", "--track", "-b", CANONICAL_BRANCH, str(catalog), f"origin/{CANONICAL_BRANCH}")
    elif mode == "local":
        args = ("worktree", "add", str(catalog), CANONICAL_BRANCH)
    else:
        # Re-add a registered-but-missing (and locked) catalog without a clone-wide prune.
        args = ("worktree", "add", "-f", "-f", str(catalog), CANONICAL_BRANCH)
    run_catalog_git(main, *args, mutation=True, timeout=timeout)


def remote_canonical(main: Path, *, timeout: float = 30.0, git: str = "git") -> Literal["present", "absent"]:
    output = run_catalog_git(
        main,
        "ls-remote",
        "--exit-code",
        CANONICAL_REMOTE,
        CANONICAL_REF,
        git=git,
        read_only=True,
        timeout=timeout,
        returncodes=frozenset({0, 2}),
    )
    return "present" if output.returncode == 0 else "absent"


def fetch_covers_canonical(main: Path, *, timeout: float = 30.0) -> bool:
    output = run_catalog_git(
        main,
        "config",
        "--get-all",
        f"remote.{CANONICAL_REMOTE}.fetch",
        read_only=True,
        timeout=timeout,
        returncodes=frozenset({0, 1}),
    )
    for refspec in os.fsdecode(output.stdout).splitlines():
        source = refspec.strip().removeprefix("+").partition(":")[0]
        if source.startswith("^"):
            continue
        if source == CANONICAL_REF or (source.count("*") == 1 and fnmatch.fnmatchcase(CANONICAL_REF, source)):
            return True
    return False


def add_fetch_branch(main: Path, *, timeout: float = 30.0) -> None:
    run_catalog_git(
        main, "remote", "set-branches", "--add", CANONICAL_REMOTE, CANONICAL_BRANCH, mutation=True, timeout=timeout
    )


def fetch_canonical(main: Path, *, timeout: float = 30.0, git: str = "git") -> None:
    run_catalog_git(
        main,
        "fetch",
        "--no-tags",
        "--no-recurse-submodules",  # the main checkout's submodules are not the catalog's business
        CANONICAL_REMOTE,
        _FETCH_REFSPEC,
        git=git,
        mutation=True,
        timeout=timeout,
    )


def resolve_commit(main: Path, ref: str, *, timeout: float = 30.0, git: str = "git") -> str | None:
    output = run_catalog_git(
        main,
        "rev-parse",
        "--verify",
        "--quiet",
        "--end-of-options",
        f"{ref}^{{commit}}",
        git=git,
        read_only=True,
        timeout=timeout,
        returncodes=frozenset({0, 1}),
    )
    return _text(output) or None if output.returncode == 0 else None


def tree_has_path(main: Path, rev: str, path: str, *, timeout: float = 30.0) -> bool:
    output = run_catalog_git(
        main, "--literal-pathspecs", "ls-tree", "--name-only", rev, "--", path, read_only=True, timeout=timeout
    )
    return bool(_text(output))


def _blob_oid(main: Path, payload: bytes, *, write: bool, timeout: float) -> str:
    args = ("hash-object", "-w", "--stdin") if write else ("hash-object", "--stdin")
    return _text(run_catalog_git(main, *args, input=payload, read_only=not write, mutation=write, timeout=timeout))


def is_initial_commit(main: Path, oid: str, *, timeout: float = 30.0) -> bool:
    """A parentless commit whose tree holds exactly the format-1 root files (a link that could not push)."""
    parents = _text(run_catalog_git(main, "rev-list", "--parents", "-n", "1", oid, read_only=True, timeout=timeout))
    if parents.split() != [oid]:
        return False
    listing = run_catalog_git(main, "ls-tree", "-z", oid, read_only=True, timeout=timeout).stdout
    entries: dict[str, tuple[str, str, str]] = {}
    for record in listing.split(b"\0"):
        if not record:
            continue
        meta, _, name = record.partition(b"\t")
        mode, kind, blob = os.fsdecode(meta).split(" ")
        entries[os.fsdecode(name)] = (mode, kind, blob)
    expected = {
        name: ("100644", "blob", _blob_oid(main, payload, write=False, timeout=timeout))
        for name, payload in CANONICAL_ROOT_FILES.items()
    }
    return entries == expected


def create_initial_commit(main: Path, *, timeout: float = 30.0) -> str:
    """Write the parentless format-1 commit's objects; no ref is created."""
    lines = []
    for name, payload in sorted(CANONICAL_ROOT_FILES.items()):
        lines.append(f"100644 blob {_blob_oid(main, payload, write=True, timeout=timeout)}\t{name}\n")
    tree = _text(run_catalog_git(main, "mktree", input="".join(lines).encode(), mutation=True, timeout=timeout))
    return _text(
        run_catalog_git(main, "commit-tree", tree, "-m", INITIAL_COMMIT_MESSAGE, mutation=True, timeout=timeout)
    )


def push_initial(main: Path, oid: str, *, timeout: float = 30.0) -> Literal["pushed", "rejected"]:
    output = run_catalog_git(
        main,
        "push",
        "--porcelain",
        CANONICAL_REMOTE,
        f"{oid}:{CANONICAL_REF}",
        mutation=True,
        timeout=timeout,
        returncodes=frozenset({0, 1}),
    )
    rows = [line.split("\t") for line in os.fsdecode(output.stdout).splitlines() if "\t" in line]
    flags = [row[0] for row in rows]
    if output.returncode == 0 and flags and all(flag in ("*", "=", " ", "+") for flag in flags):
        return "pushed"
    # Only [rejected] means the ref exists already; [remote rejected] is the server refusing it (a ruleset, a name).
    refused = [row[2] if len(row) > 2 else "" for row in rows if row[0] == "!"]
    if output.returncode == 1 and refused and all(summary.startswith("[rejected]") for summary in refused):
        return "rejected"
    raise GitProcessError(
        ("git", "push", CANONICAL_REMOTE, f"{oid}:{CANONICAL_REF}"),
        output.stderr,
        output.returncode,
        uncertain=True,
        stdout=output.stdout,
    )


def reset_branch(main: Path, oid: str, *, expected: str, timeout: float = 30.0) -> None:
    """Move the local branch to `oid` only while it still points at `expected`."""
    run_catalog_git(main, "update-ref", CANONICAL_REF, oid, expected, mutation=True, timeout=timeout)


@dataclass(frozen=True)
class CatalogChangeSummary:
    unsaved: int
    conflict_files: tuple[str, ...]


def catalog_change_summary(catalog: Path, *, timeout: float = 30.0) -> CatalogChangeSummary:
    """Unsaved paths from status, and conflict copies among every tracked or untracked catalog file."""
    status = run_catalog_git(
        catalog, "status", "--porcelain=v2", "-z", "--untracked-files=all", read_only=True, timeout=timeout
    )
    unsaved = 0
    skip = False
    for record in os.fsdecode(status.stdout).split("\0"):
        if skip:
            skip = False
            continue
        if not record or record.startswith("#"):
            continue
        unsaved += 1
        skip = record.startswith("2 ")  # a rename's source path follows as its own record
    listed = run_catalog_git(
        catalog, "ls-files", "-z", "--cached", "--others", "--exclude-standard", read_only=True, timeout=timeout
    )
    conflicts = tuple(
        sorted({
            path
            for path in os.fsdecode(listed.stdout).split("\0")
            if path and fnmatch.fnmatchcase(Path(path).name, "*.conflict-*")
        })
    )
    return CatalogChangeSummary(unsaved, conflicts)


def unpushed(catalog: Path, *, timeout: float = 30.0) -> tuple[int, str | None] | None:
    """Commits on HEAD that the fetched GitHub canonical lacks, from local refs only (no network)."""
    if resolve_commit(catalog, CANONICAL_TRACKING_REF, timeout=timeout) is None:
        return None
    span = f"{CANONICAL_TRACKING_REF}..HEAD"
    count = int(_text(run_catalog_git(catalog, "rev-list", "--count", span, read_only=True, timeout=timeout)) or 0)
    if count == 0:
        return 0, None
    dates = _text(run_catalog_git(catalog, "log", "--reverse", "--format=%cI", span, read_only=True, timeout=timeout))
    return count, dates.splitlines()[0] if dates else None


# The periodic sync (iss-00430): save in a temporary index, merge without touching the work tree, push.

PushOutcome = Literal["pushed", "up_to_date", "rejected", "auth_failed", "failed"]
_AUTH_FAILURES: Final = (
    "Authentication failed",
    "could not read Username",
    "could not read Password",
    "terminal prompts disabled",
    "Permission denied (publickey)",
    "The requested URL returned error: 403",
    "The requested URL returned error: 401",
)
_IN_PROGRESS: Final = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")
TEMPORARY_INDEX: Final = ".runtime/index.tmp"


def reset_index(catalog: Path, *, git: str = "git", timeout: float = 30.0) -> None:
    """Align the real index with HEAD (someone's `git add` must not stop the sync); the work tree is untouched."""
    run_catalog_git(catalog, "reset", "-q", git=git, mutation=True, timeout=timeout)


def list_changes(catalog: Path, *, git: str = "git", timeout: float = 30.0) -> tuple[CatalogChange, ...]:
    """Unsaved catalog paths (work tree against HEAD after reset_index), with their modification time."""
    from datetime import datetime, timezone

    from spec_dock.runtime.domain.canonical_sync_rules import CatalogChange

    output = run_catalog_git(
        catalog, "status", "--porcelain=v2", "-z", "--untracked-files=all", "--no-renames", git=git, timeout=timeout
    )
    records = os.fsdecode(output.stdout).split("\0")
    changes: dict[str, CatalogChange] = {}
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if record.startswith("? "):
            paths, kind = [record[2:]], "added"
        elif record.startswith("1 "):
            paths, kind = [record.split(" ", 8)[8]], "modified"
        elif record.startswith("2 "):
            paths, kind = [record.split(" ", 9)[9], records[index]], "modified"
            index += 1
        elif record.startswith("u "):
            paths, kind = [record.split(" ", 10)[10]], "modified"
        else:
            continue
        for path in paths:
            try:
                observed = os.lstat(catalog / path)
            except FileNotFoundError:
                changes[path] = CatalogChange(path, "deleted", None)
                continue
            mtime = datetime.fromtimestamp(observed.st_mtime, timezone.utc)
            changes[path] = CatalogChange(path, cast("ChangeKind", kind), mtime)
    return tuple(changes[path] for path in sorted(changes))


def tracked_count(catalog: Path, *, git: str = "git", timeout: float = 30.0) -> int:
    output = run_catalog_git(
        catalog, "ls-tree", "-r", "-z", "--name-only", "HEAD", git=git, read_only=True, timeout=timeout
    )
    return sum(1 for item in output.stdout.split(b"\0") if item)


def blob_of(catalog: Path, path: str, *, git: str = "git", timeout: float = 30.0) -> str:
    """The blob value `git add` would store for the file, as accepted.json records it."""
    target = catalog / path
    if target.is_symlink():
        payload = os.fsencode(target.readlink())
        output = run_catalog_git(
            catalog, "hash-object", "--stdin", input=payload, git=git, read_only=True, timeout=timeout
        )
    else:
        output = run_catalog_git(
            catalog, "hash-object", "--no-filters", "--", str(target), git=git, read_only=True, timeout=timeout
        )
    return _text(output)


def save_commit(
    catalog: Path, paths: Sequence[str], *, message: str, parent: str, git: str = "git", timeout: float = 30.0
) -> str:
    """Commit exactly `paths` on top of `parent` through a temporary index and advance the branch from `parent`."""
    index = catalog / TEMPORARY_INDEX
    environment = {"GIT_INDEX_FILE": str(index)}
    try:
        run_catalog_git(catalog, "read-tree", parent, git=git, environment=environment, mutation=True, timeout=timeout)
        run_catalog_git(
            catalog, "add", "-A", git=git, environment=environment, pathspecs=paths, mutation=True, timeout=timeout
        )
        tree = _text(
            run_catalog_git(catalog, "write-tree", git=git, environment=environment, mutation=True, timeout=timeout)
        )
        commit = _text(
            run_catalog_git(
                catalog, "commit-tree", tree, "-p", parent, "-m", message, git=git, mutation=True, timeout=timeout
            )
        )
        run_catalog_git(catalog, "update-ref", CANONICAL_REF, commit, parent, git=git, mutation=True, timeout=timeout)
    finally:
        with contextlib.suppress(FileNotFoundError):
            index.unlink()
    reset_index(catalog, git=git, timeout=timeout)
    return commit


def is_ancestor(catalog: Path, ancestor: str, descendant: str, *, git: str = "git", timeout: float = 30.0) -> bool:
    """`merge-base --is-ancestor`; a missing object raises GitProcessError (the caller pauses on it)."""
    output = run_catalog_git(
        catalog,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        git=git,
        read_only=True,
        timeout=timeout,
        returncodes=frozenset({0, 1}),
    )
    return output.returncode == 0


@dataclass(frozen=True)
class MergeTreeResult:
    code: int
    tree: str | None
    entries: tuple[ConflictEntry, ...]
    message: str


def merge_tree(
    catalog: Path, left: str, right: str, *, allow_unrelated: bool = False, git: str = "git", timeout: float = 30.0
) -> MergeTreeResult:
    """Merge without touching the work tree: 0 clean, 1 conflicts (with stage records), 2 or more failed."""
    from spec_dock.runtime.domain.canonical_sync_rules import ConflictEntry

    args = ["merge-tree", "--write-tree", "-z"]
    if allow_unrelated:
        args.append("--allow-unrelated-histories")
    output = run_catalog_git(
        catalog, *args, left, right, git=git, read_only=True, timeout=timeout, returncodes=frozenset(range(256))
    )
    if output.returncode not in (0, 1):
        return MergeTreeResult(output.returncode, None, (), os.fsdecode(output.stderr).strip())
    parts = os.fsdecode(output.stdout).split("\0")
    tree, entries = parts[0], []
    for part in parts[1:]:
        if not part:
            break
        meta, _, path = part.partition("\t")
        mode, oid, stage = meta.split(" ")
        entries.append(ConflictEntry(mode, oid, int(stage), path))
    return MergeTreeResult(output.returncode, tree, tuple(entries), os.fsdecode(output.stderr).strip())


def tree_paths(catalog: Path, tree: str, *, git: str = "git", timeout: float = 30.0) -> frozenset[str]:
    output = run_catalog_git(
        catalog, "ls-tree", "-r", "-z", "--name-only", tree, git=git, read_only=True, timeout=timeout
    )
    return frozenset(os.fsdecode(item) for item in output.stdout.split(b"\0") if item)


def write_resolution(
    catalog: Path, tree: str, resolution: Resolution, *, git: str = "git", timeout: float = 30.0
) -> str:
    """Apply a stage-only resolution to a merged tree in a temporary index and return the resolved tree."""
    index = catalog / TEMPORARY_INDEX
    environment = {"GIT_INDEX_FILE": str(index)}
    records = [f"{entry.mode} {entry.oid}\t{entry.path}" for entry in resolution.updates]
    records += [f"0 {'0' * 40}\t{path}" for path in resolution.removals]
    try:
        run_catalog_git(catalog, "read-tree", tree, git=git, environment=environment, mutation=True, timeout=timeout)
        if records:
            payload = b"".join(os.fsencode(record) + b"\0" for record in records)
            run_catalog_git(
                catalog,
                "update-index",
                "-z",
                "--index-info",
                git=git,
                environment=environment,
                input=payload,
                mutation=True,
                timeout=timeout,
            )
        return _text(
            run_catalog_git(catalog, "write-tree", git=git, environment=environment, mutation=True, timeout=timeout)
        )
    finally:
        with contextlib.suppress(FileNotFoundError):
            index.unlink()


def commit_merge(
    catalog: Path, tree: str, left: str, right: str, *, message: str, git: str = "git", timeout: float = 30.0
) -> str:
    output = run_catalog_git(
        catalog, "commit-tree", tree, "-p", left, "-p", right, "-m", message, git=git, mutation=True, timeout=timeout
    )
    return _text(output)


def changed_paths(catalog: Path, before: str, after: str, *, git: str = "git", timeout: float = 30.0) -> frozenset[str]:
    output = run_catalog_git(
        catalog, "diff", "--name-only", "-z", "--no-renames", before, after, git=git, read_only=True, timeout=timeout
    )
    return frozenset(os.fsdecode(item) for item in output.stdout.split(b"\0") if item)


def fast_forward(catalog: Path, target: str, *, git: str = "git", timeout: float = 30.0) -> None:
    """Advance HEAD and the work tree; Git refuses (and changes nothing) when a local edit would be overwritten."""
    run_catalog_git(catalog, "merge", "--ff-only", "--no-edit", target, git=git, mutation=True, timeout=timeout)


@dataclass(frozen=True)
class PushResult:
    outcome: PushOutcome
    message: str


def push_canonical(catalog: Path, *, dry_run: bool = False, git: str = "git", timeout: float = 60.0) -> PushResult:
    """Push HEAD to origin's spec-dock/canonical without force; classify rejection and authentication failure."""
    args = ["push", "--porcelain"]
    if dry_run:
        args.append("--dry-run")
    output = run_catalog_git(
        catalog,
        *args,
        CANONICAL_REMOTE,
        f"HEAD:{CANONICAL_REF}",
        git=git,
        mutation=not dry_run,
        timeout=timeout,
        returncodes=frozenset(range(256)),
    )
    return classify_push(output.returncode, output.stdout, output.stderr)


def classify_push(returncode: int, stdout: bytes, stderr: bytes) -> PushResult:
    text = os.fsdecode(stderr).strip()
    rows = [line.split("\t") for line in os.fsdecode(stdout).splitlines() if "\t" in line]
    flags = [row[0] for row in rows]
    if returncode == 0 and flags and all(flag == "=" for flag in flags):
        return PushResult("up_to_date", text)
    if returncode == 0 and flags and all(flag in ("*", "=", " ", "+") for flag in flags):
        return PushResult("pushed", text)
    if any(marker in text for marker in _AUTH_FAILURES):
        return PushResult("auth_failed", text)
    refused = [row[2] if len(row) > 2 else "" for row in rows if row[0] == "!"]
    if refused and all(summary.startswith("[rejected]") for summary in refused):
        return PushResult("rejected", text)
    return PushResult("failed", text or os.fsdecode(stdout).strip())


def push_url(catalog: Path, *, git: str = "git", timeout: float = 30.0) -> str | None:
    output = run_catalog_git(
        catalog,
        "remote",
        "get-url",
        "--push",
        CANONICAL_REMOTE,
        git=git,
        read_only=True,
        timeout=timeout,
        returncodes=frozenset({0, 1, 2, 128}),
    )
    return _text(output) or None if output.returncode == 0 else None


def restore_from_head(catalog: Path, paths: Sequence[str], *, git: str = "git", timeout: float = 30.0) -> None:
    """Bring `paths` back from HEAD into the work tree only; the index is not touched and nothing is committed."""
    run_catalog_git(
        catalog, "restore", "--source=HEAD", "--worktree", git=git, pathspecs=paths, mutation=True, timeout=timeout
    )


def ignored_files(catalog: Path, *, git: str = "git", timeout: float = 30.0) -> tuple[str, ...]:
    """Ignored files a worktree removal would delete, except the catalog's own .runtime area."""
    output = run_catalog_git(
        catalog,
        "ls-files",
        "-z",
        "--others",
        "--ignored",
        "--exclude-standard",
        git=git,
        read_only=True,
        timeout=timeout,
    )
    paths = (os.fsdecode(item) for item in output.stdout.split(b"\0") if item)
    return tuple(sorted(path for path in paths if path != ".runtime" and not path.startswith(".runtime/")))


def operation_in_progress(admin_dir: Path) -> str | None:
    """The name of an unfinished Git operation in a worktree's administrative directory, if any."""
    return next((name for name in _IN_PROGRESS if os.path.lexists(admin_dir / name)), None)
