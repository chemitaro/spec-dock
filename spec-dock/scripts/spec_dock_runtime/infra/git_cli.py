from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


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
        subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"git failed: {' '.join(cmd)}\n{(e.stderr or '').strip()}") from e


def create_and_checkout_branch(repo_root: Path, branch: str) -> None:
    _ensure_git_available()
    cmd = ["git", "checkout", "-b", branch]
    try:
        subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=True)
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
