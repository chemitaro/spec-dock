"""Resolve one canonical GitHub publication repository through the native Git boundary."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.git_cli import _parse_github_repo_slug, _remote_has_userinfo
from spec_dock.runtime.infra.git_process import run_git

if TYPE_CHECKING:
    from pathlib import Path


def github_publication_repository(root: Path, *, timeout: float) -> str:
    slugs = []
    for options in ((), ("--push",)):
        urls = os.fsdecode(
            run_git(root, "remote", "get-url", *options, "--all", "origin", timeout=timeout)
        ).splitlines()
        if len(urls) != 1 or _remote_has_userinfo(urls[0]):
            raise ValueError("origin must have exactly one credential-free fetch and push URL")
        slug = _parse_github_repo_slug(urls[0])
        if slug is None:
            raise ValueError("origin must resolve to one public GitHub repository")
        slugs.append(slug)
    if slugs[0] != slugs[1]:
        raise ValueError("origin fetch and push repositories differ")
    return slugs[0]
