from __future__ import annotations

import contextlib
import ctypes
import errno
import fcntl
import hashlib
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
import unicodedata
from urllib.parse import urlsplit

from spec_dock_runtime.application.contracts import (
    GitCapabilityAssessment,
    GitWorktreeRecord,
    PinnedCheckout,
    PinnedProviderClosure,
)

_PROVIDER_CLOSURE_PATHS = (
    "spec-dock/docs",
    "spec-dock/templates",
    "spec-dock/system",
    "spec-dock/scripts",
    ".agents/skills/spec-dock",
    ".agents/skills/spec-dock-grill-with-docs",
)
_WRITING_GIT_COMMANDS = frozenset({"checkout", "switch", "update-ref", "worktree"})


def _ensure_git_available() -> None:
    if shutil.which("git") is None:
        raise RuntimeError("'git' CLI not found. Install Git, or disable git-dependent operations.")


def require_clean_working_tree(repo_root: Path, *, allowed_missing_paths: tuple[str, ...] = ()) -> None:
    _ensure_git_available()
    try:
        p = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: git status --porcelain\n{(e.stderr or '').strip()}") from e

    allowed = set(allowed_missing_paths)
    dirty_lines = [
        line for line in (p.stdout or "").splitlines() if not (line[:2] in {" D", "D "} and line[3:] in allowed)
    ]
    if dirty_lines:
        head = "\n".join(dirty_lines[:20])
        more = "" if len(dirty_lines) <= 20 else "\n..."
        raise RuntimeError(
            "Working tree is not clean; aborting checkout for safety.\n"
            "Please commit/stash your changes first.\n\n"
            f"{head}{more}"
        )


def current_branch_or_none(repo_root: Path) -> str | None:
    _ensure_git_available()
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: git rev-parse --abbrev-ref HEAD\n{(e.stderr or '').strip()}") from e
    branch = (p.stdout or "").strip()
    if not branch or branch == "HEAD":
        return None
    return branch


def current_head_or_none(repo_root: Path) -> str | None:
    _ensure_git_available()
    p = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        return None
    head = (p.stdout or "").strip()
    return head or None


def status_short_or_none(repo_root: Path) -> str | None:
    _ensure_git_available()
    p = subprocess.run(
        ["git", "status", "--short"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        return None
    return (p.stdout or "").strip()


def local_branch_exists(repo_root: Path, branch: str) -> bool:
    _ensure_git_available()
    p = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return p.returncode == 0


def checkout_branch(repo_root: Path, branch: str, *, lease_fd: int | None = None) -> None:
    _ensure_git_available()
    cmd = ["git", "checkout", branch]
    try:
        _run_git_write(repo_root, cmd, lease_fd=lease_fd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e


def create_and_checkout_branch(repo_root: Path, branch: str, *, lease_fd: int | None = None) -> None:
    _ensure_git_available()
    cmd = ["git", "checkout", "-b", branch]
    try:
        _run_git_write(repo_root, cmd, lease_fd=lease_fd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e


def check_ref_format_branch(repo_root: Path, branch: str) -> bool:
    _ensure_git_available()
    p = subprocess.run(
        ["git", "check-ref-format", "--branch", branch],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    return p.returncode == 0


_HTTPS_GH_REMOTE_RE = re.compile(
    r"^https?://(?:[^@/]+@)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_SSH_GH_REMOTE_RE = re.compile(
    r"^(?:ssh://)?git@github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


def _remote_get_url(repo_root: Path, *, push: bool) -> str:
    _ensure_git_available()
    cmd = ["git", "remote", "get-url"]
    if push:
        cmd.append("--push")
    cmd.append("origin")
    p = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        stderr = (p.stderr or "").strip()
        if "No such remote" in stderr and "origin" in stderr:
            raise RuntimeError("origin remote is missing; cannot resolve canonical GitHub repo scope.")
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{stderr}")
    raw = (p.stdout or "").strip()
    if not raw:
        raise RuntimeError("origin remote is missing; cannot resolve canonical GitHub repo scope.")
    return raw


def _parse_github_repo_slug(remote_url: str) -> str | None:
    if _remote_has_userinfo(remote_url):
        return None
    match = _HTTPS_GH_REMOTE_RE.fullmatch(remote_url) or _SSH_GH_REMOTE_RE.fullmatch(remote_url)
    if match is None:
        return None
    owner = match.group("owner").strip().lower()
    repo = match.group("repo").strip().lower()
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _remote_has_userinfo(remote_url: str) -> bool:
    if not remote_url.lower().startswith(("http://", "https://")):
        return False
    try:
        parsed = urlsplit(remote_url)
    except ValueError:
        return True
    return parsed.username is not None or parsed.password is not None


def _redact_remote_url(remote_url: str) -> str:
    return "<credential-bearing remote>" if _remote_has_userinfo(remote_url) else remote_url


def _directory_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


def origin_github_publication_endpoint(repo_root: Path) -> tuple[str, str]:
    fetch_url = _remote_get_url(repo_root, push=False)
    push_url = _remote_get_url(repo_root, push=True)
    fetch_slug = _parse_github_repo_slug(fetch_url)
    push_slug = _parse_github_repo_slug(push_url)
    if fetch_slug is None or push_slug is None:
        raise RuntimeError(
            "origin remote is not a GitHub repository; cannot resolve canonical repo scope: "
            f"fetch={_redact_remote_url(fetch_url)} push={_redact_remote_url(push_url)}"
        )
    if fetch_slug != push_slug:
        raise RuntimeError(
            "origin remote fetch/push mismatch; cannot resolve canonical repo scope: "
            f"fetch={fetch_slug} push={push_slug}"
        )
    return fetch_slug, push_url


def origin_github_repo_slug(repo_root: Path) -> str | None:
    slug, _push_url = origin_github_publication_endpoint(repo_root)
    return slug


def worktree_list(repo_root: Path) -> list[GitWorktreeRecord]:
    _ensure_git_available()
    cmd = ["git", "worktree", "list", "--porcelain"]
    try:
        p = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e
    return _parse_worktree_porcelain(p.stdout or "")


def remove_worktree(
    repo_root: Path,
    *,
    path: Path,
    force: bool,
    source_fd: int | None = None,
    target_fd: int | None = None,
    lease_fd: int | None = None,
) -> None:
    _ensure_git_available()
    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(str(path))
    try:
        _run_git_write(
            repo_root,
            cmd,
            bound_fds=tuple(fd for fd in (source_fd, target_fd) if fd is not None),
            lease_fd=lease_fd,
        )
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        details = "\n".join(part for part in (stderr, stdout) if part)
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{details}") from e


def _parse_worktree_porcelain(text: str) -> list[GitWorktreeRecord]:
    records: list[GitWorktreeRecord] = []
    current: dict[str, object] = {}

    def flush() -> None:
        if "path" not in current:
            return
        branch_ref = current.get("branch")
        branch = None
        if isinstance(branch_ref, str):
            prefix = "refs/heads/"
            branch = branch_ref[len(prefix) :] if branch_ref.startswith(prefix) else branch_ref
        records.append(
            GitWorktreeRecord(
                path=Path(str(current["path"])),
                head=current.get("head") if isinstance(current.get("head"), str) else None,
                branch=branch,
                detached=bool(current.get("detached", False)),
                bare=bool(current.get("bare", False)),
                locked=bool(current.get("locked", False)),
            )
        )

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            current = {}
            continue
        if line.startswith("worktree "):
            flush()
            current = {"path": line[len("worktree ") :]}
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD ") :]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch ") :]
        elif line == "detached":
            current["detached"] = True
        elif line == "bare":
            current["bare"] = True
        elif line == "locked" or line.startswith("locked "):
            current["locked"] = True
    flush()
    return records


def _open_repository_root(repo_root: Path) -> int:
    raw = os.fspath(repo_root)
    if not Path(raw).is_absolute() or "\x00" in raw:
        raise RuntimeError("repository root must be absolute and NUL-free")
    if Path(raw).is_symlink():
        raise RuntimeError("repository root must not be a symlink")
    absolute = Path(raw)
    current = os.open(
        os.sep,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        for index, component in enumerate(absolute.parts[1:]):
            if component in {"", ".", ".."}:
                raise RuntimeError("repository root contains an unsafe component")
            try:
                binding = os.stat(component, dir_fd=current, follow_symlinks=False)
            except FileNotFoundError:
                binding = None
            if binding is not None and stat.S_ISLNK(binding.st_mode):
                allowed_var_alias = (
                    sys.platform == "darwin"
                    and index == 0
                    and component == "var"
                    and os.readlink(component, dir_fd=current) in {"/private/var", "private/var"}
                )
                if not allowed_var_alias:
                    raise RuntimeError("repository root contains an unsafe symlink component")
                private_fd = os.open("private", _directory_flags(), dir_fd=current)
                os.close(current)
                current = private_fd
                var_fd = os.open("var", _directory_flags(), dir_fd=current)
                os.close(current)
                current = var_fd
                continue
            next_fd = os.open(
                component,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=current,
            )
            os.close(current)
            current = next_fd
        return current
    except BaseException:
        os.close(current)
        raise


def _helper_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    runtime_scripts = str(Path(__file__).resolve().parents[2])
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = runtime_scripts if not existing else os.pathsep.join((runtime_scripts, existing))
    return environment


def _run_git_write(
    repo_root: Path,
    command: list[str],
    *,
    bound_fds: tuple[int, ...] = (),
    lease_fd: int | None = None,
    cwd_fd: int | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a writing Git command through the lease-retaining helper."""

    owns_lease = lease_fd is None
    root_fd = _open_repository_root(repo_root) if lease_fd is None else lease_fd
    try:
        try:
            value = os.fstat(root_fd)
        except OSError as error:
            raise RuntimeError("repository coordination is unavailable") from error
        if not stat.S_ISDIR(value.st_mode):
            raise RuntimeError("repository coordination is unavailable")
        if owns_lease:
            try:
                fcntl.flock(root_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except OSError as error:
                if error.errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
                    raise RuntimeError("repository coordination is busy") from error
                raise RuntimeError("repository coordination is unavailable") from error
        working_directory_fd = root_fd if cwd_fd is None else cwd_fd
        all_fds = tuple(dict.fromkeys((root_fd, *bound_fds, working_directory_fd)))
        helper = [
            sys.executable,
            "-m",
            "spec_dock_runtime.infra.git_helper",
        ]
        for bound_fd in all_fds:
            value = os.fstat(bound_fd)
            helper.extend([
                "--lease-fd",
                str(bound_fd),
                "--expected-device",
                str(value.st_dev),
                "--expected-inode",
                str(value.st_ino),
            ])
        helper.extend(["--cwd-fd", str(working_directory_fd), "--", *command])
        result = subprocess.run(
            helper,
            cwd=str(repo_root),
            env=_helper_environment(),
            pass_fds=all_fds,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                command,
                output=result.stdout,
                stderr=result.stderr,
            )
        return result
    finally:
        if owns_lease:
            os.close(root_fd)


def resolve_commit(repo_root: Path, ref: str) -> str:
    _ensure_git_available()
    command = ["git", "rev-parse", f"{ref}^{{commit}}"]
    try:
        result = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error
    return (result.stdout or "").strip()


def _ls_tree(repo_root: Path, pinned_commit: str, paths: tuple[str, ...]) -> bytes:
    command = ["git", "ls-tree", "-rz", "-r", "--full-tree", pinned_commit, "--", *paths]
    result = subprocess.run(command, cwd=str(repo_root), capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"git failed: {' '.join(command)}\n{(result.stderr or b'').decode(errors='replace').strip()}"
        )
    return result.stdout or b""


def _ls_tree_all(repo_root: Path, pinned_commit: str) -> bytes:
    command = ["git", "ls-tree", "-rz", "-r", "--full-tree", pinned_commit]
    result = subprocess.run(command, cwd=str(repo_root), capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"git failed: {' '.join(command)}\n{(result.stderr or b'').decode(errors='replace').strip()}"
        )
    return result.stdout or b""


def _tree_entries(raw: bytes) -> list[tuple[str, str, str, str]]:
    entries: list[tuple[str, str, str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        if not separator:
            raise RuntimeError("git tree output is malformed")
        fields = metadata.decode("ascii").split(" ")
        if len(fields) != 3:
            raise RuntimeError("git tree metadata is malformed")
        mode, object_type, object_id = fields
        path = raw_path.decode("utf-8")
        if "\x00" in path or path.startswith("/") or "\\" in path or any(part == ".." for part in path.split("/")):
            raise RuntimeError(f"provider closure path is unsafe: {path}")
        entries.append((mode, object_type, object_id, path))
    return entries


def _git_object_bytes(repo_root: Path, *, object_type: str, object_id: str) -> bytes:
    if object_type != "blob":
        raise RuntimeError(f"provider closure contains unsupported Git object type: {object_type}")
    command = ["git", "cat-file", "blob", object_id]
    result = subprocess.run(command, cwd=str(repo_root), capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"git failed: {' '.join(command)}\n{(result.stderr or b'').decode(errors='replace').strip()}"
        )
    return result.stdout or b""


def provider_closure(repo_root: Path, pinned_commit: str) -> PinnedProviderClosure:
    raw = _ls_tree(repo_root, pinned_commit, _PROVIDER_CLOSURE_PATHS)
    entries = _tree_entries(raw)
    digest = hashlib.sha256()
    for mode, object_type, object_id, path in sorted(entries, key=lambda item: os.fsencode(item[3])):
        digest.update(mode.encode("ascii"))
        digest.update(b"\0")
        digest.update(object_type.encode("ascii"))
        digest.update(b"\0")
        payload = _git_object_bytes(repo_root, object_type=object_type, object_id=object_id)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
        digest.update(b"\0")
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
    return PinnedProviderClosure(pinned_commit=pinned_commit, paths=_PROVIDER_CLOSURE_PATHS, digest=digest.hexdigest())


def _config(repo_root: Path, key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", key],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = (result.stdout or "").strip()
    return value or None


def _git_path(repo_root: Path, name: str) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", name],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return repo_root / name
    candidate = Path((result.stdout or "").strip())
    return candidate if candidate.is_absolute() else repo_root / candidate


def assess_capabilities(
    repo_root: Path,
    *,
    pinned_commit: str,
    closure_paths: tuple[str, ...] = _PROVIDER_CLOSURE_PATHS,
    branch: str | None = None,
    check_other_worktree: bool = True,
) -> GitCapabilityAssessment:
    reasons: list[str] = []

    status = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0:
        reasons.append("status-unavailable")
    elif status.stdout:
        reasons.append("working-tree-not-clean")

    if subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    ).stdout:
        reasons.append("unmerged-index")

    for state_name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG"):
        if _git_path(repo_root, state_name).exists():
            reasons.append(f"operation-state:{state_name.lower()}")
    if any(_git_path(repo_root, state).exists() for state in ("rebase-apply", "rebase-merge")):
        reasons.append("operation-state:rebase")

    hooks_value = _config(repo_root, "core.hooksPath")
    hooks_root = Path(hooks_value).expanduser() if hooks_value else _git_path(repo_root, "hooks")
    if not hooks_root.is_absolute():
        hooks_root = repo_root / hooks_root
    for hook_name in ("post-checkout", "reference-transaction", "post-index-change"):
        hook = hooks_root / hook_name
        try:
            if hook.is_file() and os.access(hook, os.X_OK):
                reasons.append(f"writing-hook:{hook_name}")
        except OSError:
            reasons.append(f"writing-hook-unavailable:{hook_name}")

    fsmonitor = _config(repo_root, "core.fsmonitor")
    if fsmonitor is not None and fsmonitor.lower() not in {"false", "0", "off", "no", "none"}:
        reasons.append("fsmonitor-enabled")
    sparse_checkout = _config(repo_root, "core.sparseCheckout")
    if sparse_checkout is not None and sparse_checkout.lower() in {"true", "1", "yes", "on"}:
        reasons.append("sparse-checkout-enabled")
    sparse_bits = subprocess.run(
        ["git", "ls-files", "-v"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if sparse_bits.returncode != 0:
        reasons.append("skip-worktree-probe-unavailable")
    elif any(line.startswith("S ") for line in (sparse_bits.stdout or "").splitlines()):
        reasons.append("skip-worktree-bit-set")

    if (_config(repo_root, "core.autocrlf") or "false").lower() not in {"false", "0", "off"}:
        reasons.append("autocrlf-enabled")
    if _config(repo_root, "core.eol") is not None:
        reasons.append("core-eol-set")

    try:
        closure = provider_closure(repo_root, pinned_commit)
    except RuntimeError:
        closure = None
        reasons.append("provider-closure-unprovable")

    try:
        target_entries = _tree_entries(_ls_tree_all(repo_root, pinned_commit))
    except RuntimeError:
        target_entries = []
        reasons.append("target-tree-unprovable")

    attr_paths = [entry[3] for entry in target_entries] or list(closure_paths)
    attr_command = [
        "git",
        "--literal-pathspecs",
        "check-attr",
        f"--source={pinned_commit}",
        "-z",
        "--all",
        "--",
        *attr_paths,
    ]
    attrs = subprocess.run(attr_command, cwd=str(repo_root), capture_output=True, check=False)
    if attrs.returncode != 0:
        reasons.append("attributes-unprovable")
    else:
        fields = attrs.stdout.split(b"\0")
        for index in range(0, len(fields) - 2, 3):
            attribute = fields[index + 1].decode("utf-8", errors="replace")
            value = fields[index + 2].decode("utf-8", errors="replace")
            if attribute in {
                "eol",
                "text",
                "working-tree-encoding",
                "ident",
                "filter",
                "diff",
                "merge",
            } and value not in {
                "unspecified",
                "",
                "-",
            }:
                reasons.append(f"attribute-enabled:{attribute}={value}")
                break

    normalized: dict[str, str] = {}
    for mode, object_type, object_id, path in target_entries:
        normalized_path = unicodedata.normalize("NFC", path).casefold()
        previous = normalized.get(normalized_path)
        if previous is not None and previous != path:
            reasons.append(f"path-collision:{previous}:{path}")
        normalized[normalized_path] = path
        if mode == "160000" or object_type == "commit":
            reasons.append(f"submodule:{path}")
        if mode == "120000":
            try:
                link = _git_object_bytes(repo_root, object_type=object_type, object_id=object_id)
                _validate_link_target(link, path)
            except RuntimeError:
                reasons.append(f"unsafe-symlink:{path}")

    if check_other_worktree:
        other_worktree = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        for record in _parse_worktree_porcelain(other_worktree.stdout or ""):
            same_path = record.path.resolve(strict=False) == repo_root.resolve(strict=False)
            conflicting_branch = branch is not None and record.branch == branch
            conflicting_head = branch is None and record.head == pinned_commit
            if not same_path and (conflicting_branch or conflicting_head):
                reasons.append("commit-checked-out-in-other-worktree")

    return GitCapabilityAssessment(
        allowed=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
        pinned_commit=pinned_commit,
        closure_paths=closure_paths,
        provider_closure_digest=closure.digest if closure is not None else None,
    )


def pinned_checkout(
    repo_root: Path,
    *,
    branch: str,
    pinned_commit: str,
    checkout_kind: str,
    closure_paths: tuple[str, ...] = _PROVIDER_CLOSURE_PATHS,
    lease_fd: int | None = None,
) -> PinnedCheckout:
    before_branch = current_branch_or_none(repo_root)
    before_head = current_head_or_none(repo_root)
    target_closure = provider_closure(repo_root, pinned_commit)
    if before_head is not None:
        admitted_closure = provider_closure(repo_root, before_head)
        if admitted_closure.digest != target_closure.digest:
            raise RuntimeError("runtime-generation-change-blocked: target closure differs from admitted generation")
    assessment = assess_capabilities(
        repo_root,
        pinned_commit=pinned_commit,
        closure_paths=closure_paths,
        branch=branch,
    )
    if not assessment.allowed:
        raise RuntimeError("Git capability guard failed: " + ", ".join(assessment.reasons))
    closure_digest = assessment.provider_closure_digest
    if closure_digest is None:
        raise RuntimeError("Git capability guard failed: provider closure is unprovable")
    if checkout_kind == "existing":
        _run_git_write(
            repo_root,
            ["git", "update-ref", f"refs/heads/{branch}", pinned_commit, pinned_commit],
            lease_fd=lease_fd,
        )
        if before_branch != branch:
            _run_git_write(repo_root, ["git", "switch", branch], lease_fd=lease_fd)
    elif checkout_kind == "new":
        _run_git_write(repo_root, ["git", "switch", "-c", branch, pinned_commit], lease_fd=lease_fd)
    else:
        raise RuntimeError(f"unsupported checkout kind: {checkout_kind}")
    checkout = PinnedCheckout(
        target_branch=branch,
        pinned_commit=pinned_commit,
        before_branch=before_branch,
        before_head=before_head,
        provider_closure_digest=target_closure.digest,
        checkout_kind=checkout_kind,  # type: ignore[arg-type]
    )
    verify_pinned_checkout(repo_root, checkout=checkout, closure_paths=closure_paths)
    return checkout


def verify_pinned_checkout(
    repo_root: Path,
    *,
    checkout: PinnedCheckout,
    closure_paths: tuple[str, ...] = _PROVIDER_CLOSURE_PATHS,
) -> None:
    branch = current_branch_or_none(repo_root)
    head = current_head_or_none(repo_root)
    if branch != checkout.target_branch or head != checkout.pinned_commit:
        raise RuntimeError(
            "runtime-generation-drift: "
            f"before={checkout.before_branch or '(detached)'}:{checkout.before_head or '(none)'} "
            f"after={branch or '(detached)'}:{head or '(none)'}"
        )
    closure = provider_closure(repo_root, checkout.pinned_commit)
    if closure.digest != checkout.provider_closure_digest:
        raise RuntimeError("runtime-generation-drift: provider closure changed")
    assessment = assess_capabilities(
        repo_root,
        pinned_commit=checkout.pinned_commit,
        closure_paths=closure_paths,
        branch=checkout.target_branch,
    )
    if not assessment.allowed:
        raise RuntimeError("runtime-generation-drift: " + ", ".join(assessment.reasons))


def add_worktree_pinned(
    repo_root: Path,
    *,
    path: Path,
    branch: str,
    pinned_commit: str,
    source_fd: int | None = None,
    target_fd: int | None = None,
    lease_fd: int | None = None,
) -> None:
    bound_fds = tuple(fd for fd in (source_fd, target_fd) if fd is not None)
    _run_git_write(
        repo_root,
        ["git", "worktree", "add", "--no-checkout", "-b", branch, str(path), pinned_commit],
        bound_fds=bound_fds,
        lease_fd=lease_fd,
    )


def _relative_components(path: str) -> tuple[str, ...]:
    if not path or path.startswith("/") or "\\" in path or "\x00" in path:
        raise RuntimeError(f"worktree path is unsafe: {path}")
    components = tuple(path.split("/"))
    if any(component in {"", ".", ".."} for component in components):
        raise RuntimeError(f"worktree path is unsafe: {path}")
    return components


def _open_or_create_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        os.mkdir(name, 0o755, dir_fd=parent_fd)
        fd = os.open(name, flags, dir_fd=parent_fd)
        try:
            os.fchmod(fd, 0o755)
        except BaseException:
            os.close(fd)
            raise
        return fd


def _open_relative_parent(root_fd: int, components: tuple[str, ...]) -> int:
    current = os.dup(root_fd)
    try:
        for component in components[:-1]:
            next_fd = _open_or_create_directory(current, component)
            os.close(current)
            current = next_fd
        return current
    except BaseException:
        os.close(current)
        raise


def _write_all(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            raise RuntimeError("worktree file write made no progress")
        offset += written


def _read_all(fd: int, maximum: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(fd, min(1024 * 1024, maximum + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
        if total > maximum:
            raise RuntimeError("materialized worktree file is too large")


def _verify_regular_entry(parent_fd: int, name: str, payload: bytes, mode: int) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or stat.S_IMODE(before.st_mode) != mode:
            raise RuntimeError(f"materialized worktree entry has an unsafe binding: {name}")
        observed = _read_all(fd, len(payload))
        after = os.fstat(fd)
        if observed != payload or (before.st_dev, before.st_ino, before.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise RuntimeError(f"materialized worktree entry changed while reading: {name}")
    finally:
        os.close(fd)


def _materialize_regular(parent_fd: int, name: str, payload: bytes, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(name, flags, mode, dir_fd=parent_fd)
    try:
        os.fchmod(fd, mode)
        _write_all(fd, payload)
        os.fsync(fd)
        value = os.fstat(fd)
        if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1 or stat.S_IMODE(value.st_mode) != mode:
            raise RuntimeError(f"materialized worktree entry has an unsafe binding: {name}")
    finally:
        os.close(fd)
    _verify_regular_entry(parent_fd, name, payload, mode)


def _validate_link_target(payload: bytes, path: str) -> str:
    try:
        target = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"worktree symlink target is not UTF-8: {path}") from error
    if not target or target.startswith("/") or "\\" in target or "\x00" in target:
        raise RuntimeError(f"worktree symlink target is unsafe: {path}")
    depth = len(path.split("/")) - 1
    for component in target.split("/"):
        if component == "":
            raise RuntimeError(f"worktree symlink target is unsafe: {path}")
        if component == "..":
            depth -= 1
            if depth < 0:
                raise RuntimeError(f"worktree symlink target escapes the worktree: {path}")
    return target


def _materialize_symlink(parent_fd: int, name: str, payload: bytes, path: str) -> None:
    target = _validate_link_target(payload, path)
    os.symlink(target, name, dir_fd=parent_fd)
    observed = os.readlink(name, dir_fd=parent_fd)
    if observed != target:
        raise RuntimeError(f"materialized worktree symlink changed: {path}")


def _materialize_tree_entry(
    target_fd: int,
    entry: tuple[str, str, str, str],
    *,
    repo_root: Path,
) -> None:
    mode, object_type, object_id, relative_path = entry
    components = _relative_components(relative_path)
    parent_fd = _open_relative_parent(target_fd, components)
    try:
        payload = _git_object_bytes(repo_root, object_type=object_type, object_id=object_id)
        if mode == "100644":
            _materialize_regular(parent_fd, components[-1], payload, 0o644)
        elif mode == "100755":
            _materialize_regular(parent_fd, components[-1], payload, 0o755)
        elif mode == "120000":
            _materialize_symlink(parent_fd, components[-1], payload, relative_path)
        elif mode == "160000" or object_type == "commit":
            raise RuntimeError(f"submodule is not supported in a materialized worktree: {relative_path}")
        else:
            raise RuntimeError(f"unsupported Git tree mode: {mode} ({relative_path})")
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _native_rename_no_replace(parent_fd: int, source: str, destination: str) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin":
        try:
            rename = libc.renameatx_np
        except AttributeError as error:
            raise RuntimeError("atomic-rename-unavailable") from error
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(parent_fd, source_bytes, parent_fd, destination_bytes, 0x00000004)
    else:
        try:
            rename = libc.renameat2
        except AttributeError as error:
            raise RuntimeError("atomic-rename-unavailable") from error
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(parent_fd, source_bytes, parent_fd, destination_bytes, 0x00000001)
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise FileExistsError(error_number, os.strerror(error_number), destination)
    raise OSError(error_number, os.strerror(error_number), destination)


def _unlink_owned_temp(parent_fd: int, name: str, witness: os.stat_result) -> None:
    try:
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if (current.st_dev, current.st_ino) != (witness.st_dev, witness.st_ino):
        return
    os.unlink(name, dir_fd=parent_fd)


def _publish_entrypoint(
    target_fd: int,
    entry: tuple[str, str, str, str],
    *,
    repo_root: Path,
) -> None:
    mode, object_type, object_id, relative_path = entry
    if mode != "100755" or object_type != "blob":
        raise RuntimeError("worktree entrypoint has an unsupported Git binding")
    components = _relative_components(relative_path)
    parent_fd = _open_relative_parent(target_fd, components)
    temp_name: str | None = None
    temp_witness: os.stat_result | None = None
    try:
        payload = _git_object_bytes(repo_root, object_type=object_type, object_id=object_id)
        for _attempt in range(32):
            candidate = f".spec-dock-entrypoint-{secrets.token_hex(8)}.tmp"
            try:
                temp_fd = os.open(
                    candidate,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                    0o755,
                    dir_fd=parent_fd,
                )
            except FileExistsError:
                continue
            temp_name = candidate
            try:
                os.fchmod(temp_fd, 0o755)
                _write_all(temp_fd, payload)
                os.fsync(temp_fd)
                temp_witness = os.fstat(temp_fd)
            finally:
                os.close(temp_fd)
            break
        else:
            raise RuntimeError("could not allocate a private worktree entrypoint temporary")
        _native_rename_no_replace(parent_fd, temp_name, components[-1])
        temp_name = None
        os.fsync(parent_fd)
        _verify_regular_entry(parent_fd, components[-1], payload, 0o755)
    except FileExistsError as error:
        raise RuntimeError("worktree entrypoint already exists; refusing to overwrite it") from error
    finally:
        if temp_name is not None and temp_witness is not None:
            with contextlib.suppress(OSError):
                _unlink_owned_temp(parent_fd, temp_name, temp_witness)
        os.close(parent_fd)


def materialize_worktree(
    repo_root: Path,
    *,
    path: Path,
    pinned_commit: str,
    source_fd: int,
    target_fd: int,
) -> None:
    command = ["git", "read-tree", "--reset", pinned_commit]
    try:
        _run_git_write(
            path,
            command,
            bound_fds=(source_fd,),
            lease_fd=target_fd,
            cwd_fd=target_fd,
        )
        entries = _tree_entries(_ls_tree_all(path, pinned_commit))
        entrypoint = "spec-dock/scripts/spec-dock"
        pending_entrypoint: tuple[str, str, str, str] | None = None
        for entry in entries:
            if entry[3] == entrypoint:
                pending_entrypoint = entry
                continue
            _materialize_tree_entry(target_fd, entry, repo_root=repo_root)
        if pending_entrypoint is None:
            raise RuntimeError("worktree entrypoint is missing from the pinned tree")
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error
    except OSError as error:
        raise RuntimeError(f"worktree materialization filesystem operation failed: {error}") from error


def publish_worktree_entrypoint(repo_root: Path, *, target_fd: int, pinned_commit: str) -> None:
    entries = _tree_entries(_ls_tree_all(repo_root, pinned_commit))
    pending_entrypoint = next((entry for entry in entries if entry[3] == "spec-dock/scripts/spec-dock"), None)
    if pending_entrypoint is None:
        raise RuntimeError("worktree entrypoint is missing from the pinned tree")
    _publish_entrypoint(target_fd, pending_entrypoint, repo_root=repo_root)
