from __future__ import annotations

import errno
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil
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


def require_clean_working_tree(repo_root: Path) -> None:
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

    out = (p.stdout or "").strip()
    if out:
        head = "\n".join(out.splitlines()[:20])
        more = "" if len(out.splitlines()) <= 20 else "\n..."
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


def checkout_branch(repo_root: Path, branch: str) -> None:
    _ensure_git_available()
    cmd = ["git", "checkout", branch]
    try:
        _run_git_write(repo_root, cmd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e


def create_and_checkout_branch(repo_root: Path, branch: str) -> None:
    _ensure_git_available()
    cmd = ["git", "checkout", "-b", branch]
    try:
        _run_git_write(repo_root, cmd)
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


def add_worktree_with_new_branch(repo_root: Path, *, path: Path, branch: str) -> None:
    _ensure_git_available()
    cmd = ["git", "worktree", "add", "-b", branch, str(path)]
    try:
        _run_git_write(repo_root, cmd)
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        details = "\n".join(part for part in (stderr, stdout) if part)
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{details}") from e


def remove_worktree(
    repo_root: Path,
    *,
    path: Path,
    force: bool,
    source_fd: int | None = None,
    target_fd: int | None = None,
) -> None:
    _ensure_git_available()
    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.extend(["--force", "--force"])
    cmd.append(str(path))
    try:
        _run_git_write(
            repo_root,
            cmd,
            bound_fds=tuple(fd for fd in (source_fd, target_fd) if fd is not None),
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
    resolved = os.path.realpath(raw)
    current = os.open(
        os.sep,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        for component in Path(resolved).parts[1:]:
            if component in {"", ".", ".."}:
                raise RuntimeError("repository root contains an unsafe component")
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
) -> subprocess.CompletedProcess[str]:
    """Run a writing Git command through the lease-retaining helper."""

    root_fd = _open_repository_root(repo_root)
    try:
        try:
            fcntl.flock(root_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except OSError as error:
            if error.errno in {errno.EAGAIN, errno.EWOULDBLOCK}:
                raise RuntimeError("repository coordination is busy") from error
            raise RuntimeError("repository coordination is unavailable") from error
        all_fds = (root_fd, *bound_fds)
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
        helper.extend(["--", *command])
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


def provider_closure(repo_root: Path, pinned_commit: str) -> PinnedProviderClosure:
    raw = _ls_tree(repo_root, pinned_commit, _PROVIDER_CLOSURE_PATHS)
    entries = _tree_entries(raw)
    digest = hashlib.sha256()
    for mode, object_type, object_id, path in sorted(entries, key=lambda item: os.fsencode(item[3])):
        digest.update(mode.encode("ascii"))
        digest.update(b"\0")
        digest.update(object_type.encode("ascii"))
        digest.update(b"\0")
        digest.update(object_id.encode("ascii"))
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

    if _config(repo_root, "core.fsmonitor") is not None:
        reasons.append("fsmonitor-enabled")
    if _config(repo_root, "core.sparseCheckout") in {"true", "1", "yes", "on"}:
        reasons.append("sparse-checkout-enabled")
    sparse_bits = subprocess.run(
        ["git", "ls-files", "-v"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if any(line.startswith("s ") for line in (sparse_bits.stdout or "").splitlines()):
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

    attr_command = [
        "git",
        "--literal-pathspecs",
        "check-attr",
        f"--source={pinned_commit}",
        "-z",
        "--all",
        "--",
        *closure_paths,
    ]
    attrs = subprocess.run(attr_command, cwd=str(repo_root), capture_output=True, check=False)
    if attrs.returncode != 0:
        reasons.append("attributes-unprovable")
    else:
        fields = attrs.stdout.split(b"\0")
        for index in range(0, len(fields) - 2, 3):
            value = fields[index + 2].decode("utf-8", errors="replace")
            if value not in {"unspecified", ""}:
                reasons.append(f"attribute-enabled:{fields[index + 1].decode(errors='replace')}={value}")
                break

    try:
        target_entries = _tree_entries(_ls_tree(repo_root, pinned_commit, closure_paths))
    except RuntimeError:
        target_entries = []
        reasons.append("target-tree-unprovable")
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
            link = subprocess.run(
                ["git", "cat-file", "blob", object_id],
                cwd=str(repo_root),
                capture_output=True,
                check=False,
            ).stdout.decode("utf-8", errors="replace")
            if not link or link.startswith("/") or "\\" in link or any(part == ".." for part in link.split("/")):
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
            if record.path.resolve(strict=False) != repo_root.resolve(strict=False) and record.head == pinned_commit:
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
) -> PinnedCheckout:
    before_branch = current_branch_or_none(repo_root)
    before_head = current_head_or_none(repo_root)
    assessment = assess_capabilities(repo_root, pinned_commit=pinned_commit, closure_paths=closure_paths)
    if not assessment.allowed:
        raise RuntimeError("Git capability guard failed: " + ", ".join(assessment.reasons))
    closure_digest = assessment.provider_closure_digest
    if closure_digest is None:
        raise RuntimeError("Git capability guard failed: provider closure is unprovable")
    if checkout_kind == "existing":
        _run_git_write(repo_root, ["git", "update-ref", f"refs/heads/{branch}", pinned_commit, pinned_commit])
        if before_branch != branch:
            _run_git_write(repo_root, ["git", "switch", branch])
    elif checkout_kind == "new":
        _run_git_write(repo_root, ["git", "switch", "-c", branch, pinned_commit])
    else:
        raise RuntimeError(f"unsupported checkout kind: {checkout_kind}")
    checkout = PinnedCheckout(
        target_branch=branch,
        pinned_commit=pinned_commit,
        before_branch=before_branch,
        before_head=before_head,
        provider_closure_digest=closure_digest,
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
    assessment = assess_capabilities(repo_root, pinned_commit=checkout.pinned_commit, closure_paths=closure_paths)
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
) -> None:
    bound_fds = tuple(fd for fd in (source_fd, target_fd) if fd is not None)
    _run_git_write(
        repo_root,
        ["git", "worktree", "add", "--no-checkout", "-b", branch, str(path), pinned_commit],
        bound_fds=bound_fds,
    )


def materialize_worktree(repo_root: Path, *, path: Path, pinned_commit: str) -> None:
    del repo_root
    command = ["git", "read-tree", "--reset", pinned_commit]
    try:
        _run_git_write(path, command)
        listing = subprocess.run(
            ["git", "ls-tree", "-rz", "-r", "--name-only", "--full-tree", pinned_commit],
            cwd=str(path),
            capture_output=True,
            check=True,
        )
        tracked_paths = [
            raw.decode("utf-8")
            for raw in (listing.stdout or b"").split(b"\0")
            if raw and raw.decode("utf-8") != "spec-dock/scripts/spec-dock"
        ]
        for tracked_path in tracked_paths:
            _run_git_write(path, ["git", "checkout-index", "--force", "--", tracked_path])
        _run_git_write(path, ["git", "checkout-index", "--force", "--", "spec-dock/scripts/spec-dock"])
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error
