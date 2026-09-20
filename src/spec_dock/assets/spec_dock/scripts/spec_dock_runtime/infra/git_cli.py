from __future__ import annotations

import contextlib
import ctypes
import errno
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
from typing import Literal
from urllib.parse import urlsplit

from spec_dock_runtime.application.contracts import GitWorktreeRecord

DirectoryWitness = tuple[int, int]
DirectoryWitnesses = tuple[tuple[str, DirectoryWitness], ...]


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
    match = _HTTPS_GH_REMOTE_RE.fullmatch(remote_url) or _SSH_GH_REMOTE_RE.fullmatch(remote_url)
    if match is None:
        return None
    owner = match.group("owner").strip().lower()
    repo = match.group("repo").strip().lower()
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _remote_has_userinfo(remote_url: str) -> bool:
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
    if _remote_has_userinfo(fetch_url) or _remote_has_userinfo(push_url):
        raise RuntimeError(
            "origin remote contains credentials; cannot resolve canonical repo scope: "
            f"fetch={_redact_remote_url(fetch_url)} push={_redact_remote_url(push_url)}"
        )
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


def origin_github_publication_repo_slug(repo_root: Path) -> str:
    repo_slug, _push_url = origin_github_publication_endpoint(repo_root)
    return repo_slug


def origin_github_repo_slug(repo_root: Path) -> str | None:
    return _parse_github_repo_slug(_remote_get_url(repo_root, push=False))


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
    target_fd: int,
) -> None:
    _ensure_git_available()
    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(str(path))
    _verify_worktree_target_binding(path, target_fd, phase="before Git mutation")
    try:
        subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
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


def _runtime_scripts_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _helper_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    runtime_scripts = str(_runtime_scripts_root())
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = runtime_scripts if not existing else os.pathsep.join((runtime_scripts, existing))
    return environment


def _verify_worktree_target_binding(path: Path, target_fd: int, *, phase: str) -> None:
    try:
        opened = os.fstat(target_fd)
        observed = path.stat(follow_symlinks=False)
    except OSError as error:
        raise RuntimeError(f"worktree target binding unavailable {phase}") from error
    if (
        not stat.S_ISDIR(opened.st_mode)
        or not stat.S_ISDIR(observed.st_mode)
        or (opened.st_dev, opened.st_ino) != (observed.st_dev, observed.st_ino)
    ):
        raise RuntimeError(f"worktree target binding changed {phase}")


def _run_git_in_bound_cwd(
    command: list[str],
    *,
    cwd_fd: int,
) -> subprocess.CompletedProcess[str]:
    try:
        value = os.fstat(cwd_fd)
    except OSError as error:
        raise RuntimeError("worktree cwd binding is unavailable") from error
    if not stat.S_ISDIR(value.st_mode):
        raise RuntimeError("worktree cwd binding is not a directory")
    helper = [
        sys.executable,
        "-m",
        "spec_dock_runtime.infra.git_helper",
        "--cwd-fd",
        str(cwd_fd),
        "--expected-device",
        str(value.st_dev),
        "--expected-inode",
        str(value.st_ino),
        "--",
        *command,
    ]
    result = subprocess.run(
        helper,
        cwd=str(_runtime_scripts_root()),
        env=_helper_environment(),
        pass_fds=(cwd_fd,),
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


def resolve_commit(repo_root: Path, ref: str) -> str:
    _ensure_git_available()
    command = ["git", "rev-parse", f"{ref}^{{commit}}"]
    try:
        result = subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error
    return (result.stdout or "").strip()


def _ls_tree_all(repo_root: Path, target_commit: str) -> bytes:
    command = ["git", "ls-tree", "-rz", "-r", "--full-tree", target_commit]
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


def checkout_fixed_ref(
    repo_root: Path,
    *,
    branch: str,
    target_commit: str,
    checkout_kind: Literal["existing", "new"],
) -> None:
    _ensure_git_available()
    if checkout_kind == "existing":
        commands = [["git", "update-ref", f"refs/heads/{branch}", target_commit, target_commit]]
        if current_branch_or_none(repo_root) != branch:
            commands.append(["git", "switch", branch])
    elif checkout_kind == "new":
        commands = [["git", "switch", "-c", branch, target_commit]]
    else:
        raise RuntimeError(f"unsupported checkout kind: {checkout_kind}")

    for command in commands:
        try:
            subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error

    observed_branch = current_branch_or_none(repo_root)
    observed_head = current_head_or_none(repo_root)
    if observed_branch != branch or observed_head != target_commit:
        raise RuntimeError(
            "Git checkout did not reach the fixed target: "
            f"expected={branch}:{target_commit} observed={observed_branch or '(detached)'}:{observed_head or '(none)'}"
        )


def add_worktree_at_commit(
    repo_root: Path,
    *,
    path: Path,
    branch: str,
    target_commit: str,
    target_fd: int,
) -> None:
    _ensure_git_available()
    command = ["git", "worktree", "add", "--no-checkout", "-b", branch, str(path), target_commit]
    _verify_worktree_target_binding(path, target_fd, phase="before Git mutation")
    try:
        subprocess.run(command, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as error:
        details = "\n".join(part for part in ((error.stderr or "").strip(), (error.stdout or "").strip()) if part)
        raise RuntimeError(f"git failed: {' '.join(command)}\n{details}") from error
    _verify_worktree_target_binding(path, target_fd, phase="after Git mutation")


def _relative_components(path: str) -> tuple[str, ...]:
    if not path or path.startswith("/") or "\\" in path or "\x00" in path:
        raise RuntimeError(f"worktree path is unsafe: {path}")
    components = tuple(path.split("/"))
    if any(component in {"", ".", ".."} for component in components):
        raise RuntimeError(f"worktree path is unsafe: {path}")
    return components


def _directory_witness(value: os.stat_result) -> DirectoryWitness:
    if not stat.S_ISDIR(value.st_mode):
        raise RuntimeError("materializer directory binding is not a directory")
    return (value.st_dev, value.st_ino)


def _open_or_create_directory(
    parent_fd: int,
    name: str,
    *,
    relative_path: str,
    created_directory_witnesses: dict[str, DirectoryWitness],
) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        os.mkdir(name, 0o755, dir_fd=parent_fd)
        created_fd: int | None = None
        try:
            created = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            created_fd = os.open(name, flags, dir_fd=parent_fd)
            opened = os.fstat(created_fd)
            if (opened.st_dev, opened.st_ino) != (created.st_dev, created.st_ino):
                raise RuntimeError(f"materializer directory binding changed: {relative_path}")
            os.fchmod(created_fd, 0o755)
            created_directory_witnesses[relative_path] = _directory_witness(os.fstat(created_fd))
            return created_fd
        except BaseException:
            if created_fd is not None:
                os.close(created_fd)
            raise
    try:
        expected = created_directory_witnesses.get(relative_path)
        if expected is None:
            raise RuntimeError(f"materializer encountered a foreign directory: {relative_path}")
        observed = _directory_witness(os.fstat(fd))
        if observed != expected:
            raise RuntimeError(f"materializer directory binding changed: {relative_path}")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _open_relative_parent(
    root_fd: int,
    components: tuple[str, ...],
    *,
    created_directory_witnesses: dict[str, DirectoryWitness],
) -> int:
    current = os.dup(root_fd)
    relative_components: list[str] = []
    try:
        for component in components[:-1]:
            relative_components.append(component)
            relative_path = "/".join(relative_components)
            next_fd = _open_or_create_directory(
                current,
                component,
                relative_path=relative_path,
                created_directory_witnesses=created_directory_witnesses,
            )
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
    created_directory_witnesses: dict[str, DirectoryWitness],
) -> None:
    mode, object_type, object_id, relative_path = entry
    components = _relative_components(relative_path)
    parent_fd = _open_relative_parent(
        target_fd,
        components,
        created_directory_witnesses=created_directory_witnesses,
    )
    try:
        if mode == "160000" or object_type == "commit":
            raise RuntimeError(f"submodule is not supported in a materialized worktree: {relative_path}")
        payload = _git_object_bytes(repo_root, object_type=object_type, object_id=object_id)
        if mode == "100644":
            _materialize_regular(parent_fd, components[-1], payload, 0o644)
        elif mode == "100755":
            _materialize_regular(parent_fd, components[-1], payload, 0o755)
        elif mode == "120000":
            _materialize_symlink(parent_fd, components[-1], payload, relative_path)
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
    created_directory_witnesses: dict[str, DirectoryWitness],
) -> None:
    mode, object_type, object_id, relative_path = entry
    if mode != "100755" or object_type != "blob":
        raise RuntimeError("worktree entrypoint has an unsupported Git binding")
    components = _relative_components(relative_path)
    parent_fd = _open_relative_parent(
        target_fd,
        components,
        created_directory_witnesses=created_directory_witnesses,
    )
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
    target_commit: str,
    target_fd: int,
) -> DirectoryWitnesses:
    command = ["git", "read-tree", "--reset", target_commit]
    try:
        _run_git_in_bound_cwd(command, cwd_fd=target_fd)
        entries = _tree_entries(_ls_tree_all(path, target_commit))
        entrypoint = "spec-dock/scripts/spec-dock"
        pending_entrypoint: tuple[str, str, str, str] | None = None
        created_directory_witnesses: dict[str, DirectoryWitness] = {}
        for entry in entries:
            if entry[3] == entrypoint:
                pending_entrypoint = entry
                continue
            _materialize_tree_entry(
                target_fd,
                entry,
                repo_root=repo_root,
                created_directory_witnesses=created_directory_witnesses,
            )
        if pending_entrypoint is None:
            raise RuntimeError("worktree entrypoint is missing from the pinned tree")
        entrypoint_components = _relative_components(pending_entrypoint[3])
        entrypoint_parent_fd = _open_relative_parent(
            target_fd,
            entrypoint_components,
            created_directory_witnesses=created_directory_witnesses,
        )
        os.close(entrypoint_parent_fd)
        return tuple(sorted(created_directory_witnesses.items()))
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"git failed: {' '.join(command)}\n{(error.stderr or '').strip()}") from error
    except OSError as error:
        raise RuntimeError(f"worktree materialization filesystem operation failed: {error}") from error


def publish_worktree_entrypoint(
    repo_root: Path,
    *,
    target_fd: int,
    target_commit: str,
    directory_witnesses: DirectoryWitnesses,
) -> None:
    entries = _tree_entries(_ls_tree_all(repo_root, target_commit))
    pending_entrypoint = next((entry for entry in entries if entry[3] == "spec-dock/scripts/spec-dock"), None)
    if pending_entrypoint is None:
        raise RuntimeError("worktree entrypoint is missing from the pinned tree")
    _publish_entrypoint(
        target_fd,
        pending_entrypoint,
        repo_root=repo_root,
        created_directory_witnesses=dict(directory_witnesses),
    )
