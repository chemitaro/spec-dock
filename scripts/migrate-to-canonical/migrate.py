#!/usr/bin/env python3
"""Throwaway migration of one SpecDock repository from schema-3 metadata to canonical storage.

The script never imports the spec_dock package: it uses the standard library, `git` and `gh` only, so the copy in
the v0.3.0 tag keeps working after the package drops legacy mode. Every subcommand only prints its plan unless
`--apply` is given, can be run again with the same result, and records what it wrote under
`<state dir>/<owner>-<repo>/` (undo.jsonl, idmap.json, build.json). See README.md beside this file.

Exit codes: 0 ok, 1 problems found by a read-only run, 2 refused before writing (usage errors too), 3 stopped after
writing (follow the printed next step; usually the same command continues).
"""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import quote, unquote

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

# ---------------------------------------------------------------------------------------------------------------
# Contract values copied from the package (tests compare each one with the package constant or asset).
# ---------------------------------------------------------------------------------------------------------------

# C1: Scope kinds on GitHub (domain/canonical_structure.py, domain/ids.py).
KIND_LABELS: dict[str, str] = {
    "initiative": "spec-dock:initiative",
    "epic": "spec-dock:epic",
    "issue": "spec-dock:issue",
}
LABEL_DEFINITIONS: tuple[tuple[str, str, str], ...] = (
    ("spec-dock:initiative", "5319e7", "SpecDock Initiative scope"),
    ("spec-dock:epic", "1d76db", "SpecDock Epic scope"),
    ("spec-dock:issue", "0e8a16", "SpecDock Issue scope"),
)
ID_PREFIXES: dict[str, str] = {"initiative": "init", "epic": "epic", "issue": "iss"}
PARENT_KINDS: dict[str, str | None] = {"initiative": None, "epic": "initiative", "issue": "epic"}
ID_WIDTH = 5
CANONICAL_ID_RE = re.compile(r"^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$")

# C2: the shipped schema-4 declaration and the writer protocol require_writer accepts.
NEW_WRITER_PROTOCOL = "specdock.worktree-writer/v1"
WORKSPACE_V4_BYTES = b'{"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}\n'
WORKSPACE_V3_BYTES = b'{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n'

# C3: catalog, link, branch and ignore lines (domain/canonical_layout.py).
CANONICAL_BRANCH = "spec-dock/canonical"
CANONICAL_REF = "refs/heads/spec-dock/canonical"
CANONICAL_TRACKING_REF = "refs/remotes/origin/spec-dock/canonical"
CATALOG_RELATIVE = "spec-dock/.canonical"
LINK_RELATIVE = "spec-dock/initiatives"
CATALOG_LOCK_REASON = "spec-dock canonical catalog"
GITIGNORE_PATH = "spec-dock/.gitignore"
GITIGNORE_LINES: tuple[str, ...] = ("/.canonical/", "/initiatives", "!/initiatives/")
# Scope directories live at <catalog>/<bucket>/<ID>/; the bucket is the number's thousand range (I-16).
BUCKET_SIZE = 1000

# C5: the canonical branch root files, format 1 (domain/canonical_content.py).
FORMAT_FILE = ".spec-dock-canonical.json"
RUNTIME_DIRECTORY = ".runtime"
_CANONICAL_README = """\
# spec-dock/canonical

このブランチ `spec-dock/canonical` は、仕様の内容（要件、設計、計画、報告、Artifact）の正本です。
コードのブランチ（main など）とは共通の祖先を持たず、コードのブランチにマージしません。

- 仕様は、各チェックアウトの `spec-dock/initiatives/` から、普通のファイルとして読み書きします。
- 保存、取り込み、push は、SpecDock の定期の同期が行います。このブランチを手で commit、rebase、強制 push しないでください。
- 構造（番号、種類、親子、依存、状態、題名）の正本は GitHub Issue です。
"""  # noqa: RUF001
CANONICAL_ROOT_FILES: dict[str, bytes] = {
    FORMAT_FILE: b'{"format": 1}\n',
    ".gitignore": b".runtime/\n**/.workbench/*\n!**/.workbench/README.md\n**/.workbench/README.md/**\n",
    "README.md": _CANONICAL_README.encode("utf-8"),
}

# C6: catalog Git calls run without hooks, signing, fsmonitor or automatic maintenance (infra/canonical_git.py).
HOOKLESS_CONFIG: tuple[str, ...] = (
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

# Inherited GIT_* variables are dropped except identity and SSH transport (infra/canonical_git.py).
PASSED_GIT_VARIABLES: tuple[str, ...] = (
    "GIT_AUTHOR_NAME",
    "GIT_AUTHOR_EMAIL",
    "GIT_COMMITTER_NAME",
    "GIT_COMMITTER_EMAIL",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
)

# C7: the version file and the check workflow sample (application/canonical_check.py and its asset).
CI_VERSION_FILE = "spec-dock/system/spec-dock-version"
WORKFLOW_SAMPLE = "spec-dock/docs/ci/spec-dock-check.yml"
WORKFLOW_DESTINATION = ".github/workflows/spec-dock-check.yml"
WORKFLOW_BRANCH_LINE = "branches: [main]"
WORKFLOW_BRANCH_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._/-]*$")
WORKFLOW_SAMPLE_BYTES = b"""\
# \xe3\x83\x9b\xe3\x82\xb9\xe3\x83\x88\xe3\x81\xae runner\xef\xbc\x88GitHub \xe3\x81\x8c\xe8\xb2\xb8\xe3\x81\x99 ubuntu-latest \xe3\x81\xaa\xe3\x81\xa9\xef\xbc\x89\xe3\x81\xaf\xe3\x80\x81\xe5\x8b\x95\xe3\x81\x84\xe3\x81\x9f\xe6\x99\x82\xe9\x96\x93\xe3\x81\xab\xe8\xb2\xbb\xe7\x94\xa8\xe3\x81\x8c\xe3\x81\x8b\xe3\x81\x8b\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82
# \xe3\x81\x93\xe3\x81\xae\xe8\xa6\x8b\xe6\x9c\xac\xe3\x81\xaf\xe3\x80\x81PR \xe3\x81\xa8\xe6\x97\xa2\xe5\xae\x9a\xe3\x81\xae\xe3\x83\x96\xe3\x83\xa9\xe3\x83\xb3\xe3\x83\x81\xe3\x81\xb8\xe3\x81\xae push \xe3\x81\xae\xe3\x81\x9f\xe3\x81\xb3\xe3\x81\xab\xe5\x8b\x95\xe3\x81\x8d\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82
# \xe8\xb5\xb7\xe5\x8b\x95\xe3\x81\xae\xe6\x9d\xa1\xe4\xbb\xb6\xef\xbc\x88on\xef\xbc\x89\xe3\x81\xa8 runs-on \xe3\x81\xaf\xe3\x80\x81\xe3\x83\xaa\xe3\x83\x9d\xe3\x82\xb8\xe3\x83\x88\xe3\x83\xaa\xe3\x81\xae\xe6\xb1\xba\xe3\x81\xbe\xe3\x82\x8a\xe3\x81\xab\xe5\x90\x88\xe3\x82\x8f\xe3\x81\x9b\xe3\x81\xa6\xe5\xa4\x89\xe3\x81\x88\xe3\x81\xa6\xe3\x81\x8b\xe3\x81\xbe\xe3\x81\x84\xe3\x81\xbe\xe3\x81\x9b\xe3\x82\x93\xe3\x80\x82
#   - \xe6\x89\x8b\xe5\x8b\x95\xe3\x81\xae\xe8\xb5\xb7\xe5\x8b\x95\xe3\x81\xa0\xe3\x81\x91\xe3\x81\xab\xe3\x81\x99\xe3\x82\x8b: on \xe3\x82\x92 `workflow_dispatch:` \xe3\x81\xa0\xe3\x81\x91\xe3\x81\xab\xe3\x81\x99\xe3\x82\x8b
#   - \xe8\x87\xaa\xe5\x89\x8d\xe3\x81\xae runner \xe3\x81\xab\xe6\x8c\xaf\xe3\x82\x8a\xe5\x88\x86\xe3\x81\x91\xe3\x82\x8b: runs-on \xe3\x82\x92\xe3\x80\x81\xe3\x81\x9d\xe3\x81\xae\xe3\x83\xa9\xe3\x83\x99\xe3\x83\xab\xe3\x81\xab\xe6\x9b\xbf\xe3\x81\x88\xe3\x82\x8b
#   - push \xe3\x81\xae\xe5\x89\x8d\xe3\x81\xab\xe6\x89\x8b\xe5\x85\x83\xe3\x81\xa7\xe5\x9b\x9e\xe3\x81\x99: .githooks/pre-push \xe3\x81\xa7 `spec-dock canonical check --json` \xe3\x82\x92\xe5\xae\x9f\xe8\xa1\x8c\xe3\x81\x99\xe3\x82\x8b
# \xe3\x81\xa9\xe3\x81\xae\xe5\xbd\xa2\xe3\x81\xa7\xe3\x82\x82\xe3\x80\x81\xe6\xa4\x9c\xe6\x9f\xbb\xe3\x81\xae\xe4\xb8\xad\xe8\xba\xab\xe3\x81\xaf\xe5\x90\x8c\xe3\x81\x98 `spec-dock canonical check --json` \xe3\x81\xa7\xe3\x81\x99\xe3\x80\x82
name: SpecDock check
on:
  pull_request:
  push:
    branches: [main]   # \xe6\x97\xa2\xe5\xae\x9a\xe3\x81\xae\xe3\x83\x96\xe3\x83\xa9\xe3\x83\xb3\xe3\x83\x81\xe3\x81\xae\xe5\x90\x8d\xe5\x89\x8d\xe3\x81\xab\xe5\x90\x88\xe3\x82\x8f\xe3\x81\x9b\xe3\x82\x8b
permissions:
  contents: read
jobs:
  spec-dock-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install SpecDock
        run: pipx install "spec-dock @ git+https://github.com/chemitaro/spec-dock@v$(cat spec-dock/system/spec-dock-version)"
      - name: Check
        run: spec-dock canonical check --json
"""

# Legacy mode: the title rule and slug derivation (domain/ids.py), and the child-layer rule links that Scope
# creation puts in an Initiative and an Epic (application/scope_scaffold.py).
LEGACY_TITLE_RE = re.compile(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$")
LEGACY_CHILD_RULES: dict[str, tuple[str, str]] = {
    "initiative": ("epics", "spec-dock/docs/rules/initiative/epics.md"),
    "epic": ("issues", "spec-dock/docs/rules/epic/issues.md"),
}

# Script-only values.
SPEC_ROOT = LINK_RELATIVE
META_FILE = ".meta.json"
META_REQUIRED_KEYS = frozenset({
    "schema_version",
    "type",
    "id",
    "title",
    "slug",
    "parent_id",
    "initiative_id",
    "epic_id",
    "depends_on",
    "backend",
    "github",
    "lifecycle",
    "revision",
})
META_KEY_ORDER = (
    "schema_version",
    "type",
    "id",
    "title",
    "slug",
    "parent_id",
    "initiative_id",
    "epic_id",
    "depends_on",
    "backend",
    "github",
    "lifecycle",
    "revision",
)
GITHUB_ID_RE = re.compile(r"^(init|epic|iss)-([0-9]+)$")
LOCAL_ID_RE = re.compile(r"^(init|epic|iss)-local-([0-9]+)$")
DEFAULT_CUT_BRANCH = "spec-dock/migrate-to-canonical"
DEFAULT_EXPORT_BRANCH = "spec-dock/export-legacy"
CANONICAL_COMMIT_MESSAGE = "spec-dock: migrate to canonical"
CUT_COMMIT_MESSAGE = "spec-dock: move specs to the canonical branch"
EXPORT_COMMIT_MESSAGE = "spec-dock: restore legacy spec storage"
WRITE_INTERVAL = 1.0
WRITES_PER_MINUTE = 80
WRITES_PER_HOUR = 500
READ_RETRY_LIMIT = 60.0
WRITE_RETRY_LIMIT = 3600.0
NUMBER_BATCH = 50
CLOCK_ALLOWANCE = timedelta(minutes=5)
MINIMUM_GIT = (2, 31)  # rev-parse --path-format=absolute; checked on 2.34.1, 2.39.5, 2.43.0 and 2.54.0
ADOPT_GIT = (2, 40)  # merge-tree --write-tree --merge-base
EXIT_OK, EXIT_PROBLEMS, EXIT_REFUSED, EXIT_STOPPED = 0, 1, 2, 3

BLOCKING_CODES = frozenset({
    "META_INVALID",
    "DUPLICATE_ID",
    "DUPLICATE_NUMBER",
    "ID_NUMBER_MISMATCH",
    "ISSUE_MISSING",
    "KIND_RULE",
    "PARENT_MISSING",
    "DEPENDENCY_MISSING",
    "DEPENDENCY_CYCLE",
})


# ---------------------------------------------------------------------------------------------------------------
# Copied rules (C1, C3, legacy) and naming.
# ---------------------------------------------------------------------------------------------------------------


def scope_id(kind: str, number: int) -> str:
    if number <= 0:
        raise ValueError("GitHub Issue number must be positive")
    return f"{ID_PREFIXES[kind]}-{number:0{ID_WIDTH}d}"


def scope_bucket(number: int) -> str:
    """The thousand range of a number, both ends as wide as the ID's number: 00000-00999, 100000-100999."""
    if number < 1:
        raise ValueError("GitHub Issue number must be positive")
    width = max(ID_WIDTH, len(str(number)))
    lower = number - number % BUCKET_SIZE
    return f"{lower:0{width}d}-{lower + BUCKET_SIZE - 1:0{width}d}"


def scope_relative(value: str) -> str:
    """`<bucket>/<ID>`: where a Scope directory lives in the catalog."""
    if CANONICAL_ID_RE.fullmatch(value) is None:
        raise ValueError(f"not a Scope ID: {value!r}")
    return f"{scope_bucket(int(value.rsplit('-', 1)[1]))}/{value}"


def legacy_slug(title: str) -> str:
    """The legacy slug a title gives (lowercase, spaces to hyphens), or `untitled` outside the legacy title rule."""
    text = title.strip()
    return text.lower().replace(" ", "-") if LEGACY_TITLE_RE.fullmatch(text) else "untitled"


def ignore_rules_effective(text: str | None) -> bool:
    """All three lines present and the negation after the link rule (domain/canonical_layout.missing_lines)."""
    stripped = [line.rstrip() for line in (text or "").splitlines()]
    if any(rule not in stripped for rule in GITIGNORE_LINES):
        return False
    rule, negation = GITIGNORE_LINES[-2], GITIGNORE_LINES[-1]
    last = {value: max(index for index, line in enumerate(stripped) if line == value) for value in (rule, negation)}
    return last[negation] > last[rule]


def pc_name(hostname: str | None = None) -> str:
    """Epic design ch. 5: host name before the first dot, lowercase, a-z0-9- only, at most 32 characters."""
    name = (hostname if hostname is not None else socket.gethostname()).split(".", 1)[0].lower()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")[:32].strip("-")
    return name or "pc"


def split_name(name: str) -> tuple[str, str]:
    """(body, extension with its dot); a leading-dot-only or dotless name has no extension."""
    index = name.rfind(".")
    if index <= 0:
        return name, ""
    return name[:index], name[index:]


def alternate_name(name: str, tag: str, taken: Callable[[str], bool]) -> str:
    """`<body>.<tag>[.<ext>]`, then `<body>.<tag>-2[.<ext>]`, ... until the name is free."""
    body, extension = split_name(name)
    candidate = f"{body}.{tag}{extension}"
    counter = 2
    while taken(candidate):
        candidate = f"{body}.{tag}-{counter}{extension}"
        counter += 1
    return candidate


def conflict_tag(pc: str, now: datetime) -> str:
    return f"conflict-{pc}-{now.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


# ---------------------------------------------------------------------------------------------------------------
# Errors, clock and output.
# ---------------------------------------------------------------------------------------------------------------


class MigrationError(Exception):
    exit_code = EXIT_REFUSED

    def __init__(self, message: str, next_step: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.next_step = next_step


class Refused(MigrationError):
    """Stopped before this run wrote anything."""

    exit_code = EXIT_REFUSED


class Stopped(MigrationError):
    """Stopped after this run wrote something; the same command continues."""

    exit_code = EXIT_STOPPED


class SystemClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


@dataclass
class Report:
    command: str
    apply: bool
    repository: str | None = None
    default_branch: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)

    def say(self, text: str) -> None:
        self.lines.append(text)

    def warn(self, text: str) -> None:
        self.warnings.append(text)

    def step(self, text: str) -> None:
        if text not in self.next_steps:
            self.next_steps.append(text)


def _status(code: int) -> str:
    return {EXIT_OK: "ok", EXIT_PROBLEMS: "problems", EXIT_REFUSED: "refused", EXIT_STOPPED: "stopped"}[code]


def emit(report: Report, code: int, as_json: bool, error: str | None, stream: Any) -> None:
    if as_json:
        payload = {
            "command": report.command,
            "apply": report.apply,
            "status": _status(code),
            "exit_code": code,
            "repository": report.repository,
            "default_branch": report.default_branch,
            "data": report.data,
            "anomalies": report.anomalies,
            "warnings": report.warnings,
            "next_steps": report.next_steps,
            "messages": report.lines,
            "error": error,
        }
        stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return
    mode = "apply" if report.apply else "plan only (add --apply to write)"
    stream.write(f"migrate.py {report.command}: {_status(code)} [{mode}]\n")
    if report.repository:
        stream.write(f"repository: {report.repository} (default branch {report.default_branch})\n")
    for line in report.lines:
        stream.write(f"{line}\n")
    if report.anomalies:
        stream.write("anomalies:\n")
        for item in report.anomalies:
            flag = " [blocking]" if item.get("blocking") else ""
            stream.write(f"  - {item['code']}{flag}: {item['message']}\n")
    for warning in report.warnings:
        stream.write(f"warning: {warning}\n")
    if error:
        stream.write(f"error: {error}\n")
    for step in report.next_steps:
        stream.write(f"next: {step}\n")


# ---------------------------------------------------------------------------------------------------------------
# Git.
# ---------------------------------------------------------------------------------------------------------------


class GitError(Exception):
    def __init__(self, args: Sequence[str], returncode: int, stderr: bytes) -> None:
        detail = stderr.decode("utf-8", errors="replace").strip()
        super().__init__(f"git {' '.join(args)} failed ({returncode}): {detail}")
        self.returncode = returncode
        self.stderr = detail


def run_git(
    cwd: Path | None,
    *args: str,
    input: bytes | None = None,
    env: Mapping[str, str] | None = None,
    read_only: bool = False,
    hookless: bool = False,
    ok: Iterable[int] = (0,),
) -> subprocess.CompletedProcess[bytes]:
    argv = ["git"]
    if cwd is not None:
        argv += ["-C", str(cwd)]
    if hookless:
        argv += list(HOOKLESS_CONFIG)
    if read_only:
        argv.append("--no-optional-locks")
    argv += list(args)
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({key: os.environ[key] for key in PASSED_GIT_VARIABLES if key in os.environ})
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment.update(env or {})
    completed = subprocess.run(argv, input=input, capture_output=True, env=environment, check=False)
    if completed.returncode not in tuple(ok):
        raise GitError(args, completed.returncode, completed.stderr)
    return completed


def git_text(cwd: Path | None, *args: str, read_only: bool = True, **kwargs: Any) -> str:
    return run_git(cwd, *args, read_only=read_only, **kwargs).stdout.decode("utf-8", errors="surrogateescape").strip()


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    kind: str
    oid: str
    path: str


def list_tree(cwd: Path, treeish: str) -> list[TreeEntry]:
    output = run_git(cwd, "ls-tree", "-r", "-z", "--full-tree", treeish, read_only=True).stdout
    entries = []
    for record in output.split(b"\0"):
        if not record:
            continue
        header, _, path = record.partition(b"\t")
        mode, kind, oid = header.decode().split(" ")
        entries.append(TreeEntry(mode, kind, oid, path.decode("utf-8", errors="surrogateescape")))
    return entries


def tree_oid(cwd: Path, treeish: str) -> str | None:
    """The tree of a commit, or of `<rev>:<path>` when that path is a directory; None otherwise."""
    spec = treeish if ":" in treeish else f"{treeish}^{{tree}}"
    completed = run_git(cwd, "rev-parse", "--verify", "--quiet", spec, read_only=True, ok=(0, 1, 128))
    oid = completed.stdout.decode().strip()
    if completed.returncode != 0 or not oid:
        return None
    kind = run_git(cwd, "cat-file", "-t", oid, read_only=True, ok=(0, 128)).stdout.decode().strip()
    return oid if kind == "tree" else None


def read_blobs(cwd: Path, oids: Iterable[str]) -> dict[str, bytes]:
    wanted = list(dict.fromkeys(oids))
    if not wanted:
        return {}
    output = run_git(cwd, "cat-file", "--batch", input="".join(f"{oid}\n" for oid in wanted).encode()).stdout
    blobs: dict[str, bytes] = {}
    position = 0
    for oid in wanted:
        newline = output.index(b"\n", position)
        header = output[position:newline].decode().split(" ")
        if len(header) < 3:
            raise GitError(("cat-file", oid), 128, b"missing object")
        size = int(header[2])
        blobs[oid] = output[newline + 1 : newline + 1 + size]
        position = newline + 1 + size + 1
    return blobs


def hash_blob(repo: Path, payload: bytes) -> str:
    return git_text(repo, "hash-object", "-w", "--stdin", input=payload, read_only=False)


def write_tree(repo: Path, entries: Iterable[TreeEntry], scratch: Path) -> str:
    index = scratch / f"index-{os.getpid()}-{time.monotonic_ns()}"
    payload = b"".join(
        f"{entry.mode} {entry.oid}\t".encode() + entry.path.encode("utf-8", "surrogateescape") + b"\0"
        for entry in entries
    )
    env = {"GIT_INDEX_FILE": str(index)}
    try:
        run_git(repo, "update-index", "-z", "--index-info", input=payload, env=env)
        return git_text(repo, "write-tree", env=env, read_only=False)
    finally:
        index.unlink(missing_ok=True)


@dataclass(frozen=True)
class Identity:
    name: str
    email: str


def commit_tree(repo: Path, tree: str, parents: Sequence[str], message: str, identity: Identity, date: str) -> str:
    env = {
        "GIT_AUTHOR_NAME": identity.name,
        "GIT_AUTHOR_EMAIL": identity.email,
        "GIT_COMMITTER_NAME": identity.name,
        "GIT_COMMITTER_EMAIL": identity.email,
        "GIT_AUTHOR_DATE": date,
        "GIT_COMMITTER_DATE": date,
    }
    args = ["commit-tree", tree]
    for parent in parents:
        args += ["-p", parent]
    args += ["-m", message]
    return git_text(repo, *args, env=env, read_only=False, hookless=True)


# ---------------------------------------------------------------------------------------------------------------
# Target resolution.
# ---------------------------------------------------------------------------------------------------------------

_GITHUB_URL = re.compile(
    r"^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)(?P<owner>[^/]+)/(?P<name>[^/]+?)(?:\.git)?/?$"
)


@dataclass
class Target:
    project: Path
    common_dir: Path
    default_branch: str
    owner: str
    name: str
    origin_url: str
    state_dir: Path
    identity: Identity

    @property
    def repository(self) -> str:
        return f"github.com/{self.owner}/{self.name}"

    @property
    def default_ref(self) -> str:
        return f"refs/remotes/origin/{self.default_branch}"


def resolve_target(project_arg: str, repo_arg: str | None, state_arg: str | None) -> Target:
    project = Path(project_arg).expanduser().resolve()
    if not project.is_dir():
        raise Refused(f"--project is not a directory: {project}")
    try:
        common = Path(git_text(project, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    except GitError as error:
        raise Refused(f"--project is not a Git checkout: {error}") from error
    if common.name != ".git" or common.parent != project:
        raise Refused(
            f"--project must be the main checkout of its clone (its Git common directory is {common})",
            f"Pass the main checkout: --project {common.parent if common.name == '.git' else '<main checkout>'}",
        )
    try:
        origin_url = git_text(project, "remote", "get-url", "origin")
    except GitError as error:
        raise Refused("the repository has no origin remote") from error
    head = run_git(project, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", read_only=True, ok=(0, 1))
    reference = head.stdout.decode().strip()
    if head.returncode != 0 or not reference.startswith("refs/remotes/origin/"):
        raise Refused(
            "origin/HEAD is not set, so the default branch is unknown",
            f"git -C {project} remote set-head origin --auto",
        )
    default_branch = reference.removeprefix("refs/remotes/origin/")
    matched = _GITHUB_URL.match(origin_url)
    if matched is not None:
        owner, name = matched.group("owner"), matched.group("name")
        if repo_arg is not None and repo_arg.lower() != f"{owner}/{name}".lower():
            raise Refused(f"--repo {repo_arg} differs from origin ({owner}/{name})", "Drop --repo or fix it")
    elif repo_arg is not None:
        if re.fullmatch(r"[^/\s]+/[^/\s]+", repo_arg) is None:
            raise Refused("--repo must be OWNER/NAME")
        owner, name = repo_arg.split("/")
    else:
        raise Refused(
            f"origin is not a GitHub URL ({origin_url}); a rehearsal clone needs the real repository",
            "Add --repo OWNER/NAME",
        )
    base = Path(state_arg).expanduser().resolve() if state_arg else Path(__file__).resolve().parent / ".state"
    name_cfg = git_text(project, "config", "user.name", ok=(0, 1)) or "spec-dock migrate"
    email_cfg = git_text(project, "config", "user.email", ok=(0, 1)) or "spec-dock-migrate@localhost"
    return Target(
        project=project,
        common_dir=common,
        default_branch=default_branch,
        owner=owner,
        name=name,
        origin_url=origin_url,
        state_dir=base / f"{owner}-{name}".lower(),
        identity=Identity(name_cfg, email_cfg),
    )


def resolve_commit(cwd: Path, ref: str) -> str | None:
    completed = run_git(cwd, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", read_only=True, ok=(0, 1))
    return completed.stdout.decode().strip() if completed.returncode == 0 else None


def source_commit(target: Target) -> str:
    commit = resolve_commit(target.project, target.default_ref)
    if commit is None:
        raise Refused(f"{target.default_ref} does not exist", f"git -C {target.project} fetch origin")
    return commit


def stale_default(target: Target) -> str | None:
    """A message when the local origin/<default> differs from origin's current head (the script never fetches)."""
    local = resolve_commit(target.project, target.default_ref)
    remote = remote_ref(target, f"refs/heads/{target.default_branch}")
    if remote is not None and remote != local:
        return f"origin/{target.default_branch} is {local} here but {remote} on origin"
    return None


def require_fresh_default(target: Target) -> None:
    message = stale_default(target)
    if message is not None:
        raise Refused(message, f"git -C {target.project} fetch origin, then run again")


def tracked_spec_files(cwd: Path, commit: str) -> list[TreeEntry]:
    return list_tree(cwd, f"{commit}:{SPEC_ROOT}") if tree_oid(cwd, f"{commit}:{SPEC_ROOT}") else []


def has_path(cwd: Path, commit: str, path: str) -> bool:
    return tree_oid(cwd, f"{commit}:{path}") is not None or bool(
        run_git(cwd, "ls-tree", commit, "--", path, read_only=True).stdout
    )


def legacy_commit(target: Target, state: State) -> str | None:
    """The commit whose spec-dock/initiatives holds the schema-3 metadata (before the cut when it is merged)."""
    source = source_commit(target)
    if has_path(target.project, source, SPEC_ROOT):
        return source
    recorded = state.build.get("source_commit")
    if isinstance(recorded, str) and resolve_commit(target.project, recorded):
        return recorded
    last = git_text(target.project, "log", "--first-parent", "-1", "--format=%H", source, "--", SPEC_ROOT)
    if last:
        parent = resolve_commit(target.project, f"{last}^1")
        if parent and has_path(target.project, parent, SPEC_ROOT):
            return parent
    return None


def remote_ref(target: Target, ref: str) -> str | None:
    completed = run_git(target.project, "ls-remote", "--exit-code", "origin", ref, read_only=True, ok=(0, 2))
    if completed.returncode == 2:
        return None
    line = completed.stdout.decode().split("\n", 1)[0]
    return line.split("\t", 1)[0] or None


def commit_date(cwd: Path, commit: str) -> str:
    return git_text(cwd, "show", "-s", "--format=%cI", commit)


def committer(cwd: Path, commit: str) -> Identity:
    name, email = git_text(cwd, "show", "-s", "--format=%cn%x00%ce", commit).split("\0")
    return Identity(name, email)


# ---------------------------------------------------------------------------------------------------------------
# Work records.
# ---------------------------------------------------------------------------------------------------------------


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class State:
    """idmap.json, undo.jsonl and build.json of one repository; read-only runs never create the directory."""

    def __init__(self, directory: Path, repository: str) -> None:
        self.directory = directory
        self.repository = repository
        self.idmap: dict[str, dict[str, Any]] = {}
        self.build: dict[str, Any] = {}
        idmap_path = directory / "idmap.json"
        if idmap_path.exists():
            payload = json.loads(idmap_path.read_text(encoding="utf-8"))
            self.idmap = dict(payload.get("entries", {}))
        build_path = directory / "build.json"
        if build_path.exists():
            self.build = json.loads(build_path.read_text(encoding="utf-8"))

    def save_idmap(self) -> None:
        _write_json(self.directory / "idmap.json", {"version": 1, "repository": self.repository, "entries": self.idmap})

    def save_build(self, payload: dict[str, Any]) -> None:
        self.build = {"version": 1, **payload}
        _write_json(self.directory / "build.json", self.build)

    def undo_records(self) -> list[dict[str, Any]]:
        path = self.directory / "undo.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append_undo(self, record: dict[str, Any], clock: Any) -> dict[str, Any]:
        records = self.undo_records()
        entry = {"seq": len(records) + 1, "at": _iso(clock.now()), **record}
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "undo.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return entry

    def renames(self) -> dict[str, str]:
        return {old: entry["id"] for old, entry in self.idmap.items() if entry.get("id")}


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------------------------------------------
# Schema-3 metadata.
# ---------------------------------------------------------------------------------------------------------------


@dataclass
class Scope:
    id: str
    kind: str
    title: str
    slug: str
    parent_id: str | None
    depends_on: list[str]
    number: int | None
    owner: str | None
    repo: str | None
    directory: str  # relative to spec-dock/initiatives
    raw: dict[str, Any]
    payload: bytes

    @property
    def local(self) -> bool:
        return LOCAL_ID_RE.fullmatch(self.id) is not None


def anomaly(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, "blocking": code in BLOCKING_CODES, **details}


def load_scopes(cwd: Path, commit: str, prefix: str = SPEC_ROOT) -> tuple[list[Scope], list[dict[str, Any]]]:
    if tree_oid(cwd, f"{commit}:{prefix}") is None:
        return [], []
    entries = [entry for entry in list_tree(cwd, f"{commit}:{prefix}") if PurePosixPath(entry.path).name == META_FILE]
    blobs = read_blobs(cwd, [entry.oid for entry in entries])
    return parse_scopes((entry.path, blobs[entry.oid]) for entry in entries)


def parse_scopes(files: Iterable[tuple[str, bytes]]) -> tuple[list[Scope], list[dict[str, Any]]]:
    scopes: list[Scope] = []
    problems: list[dict[str, Any]] = []
    for path, payload in files:
        directory = str(PurePosixPath(path).parent)
        try:
            raw = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            problems.append(anomaly("META_INVALID", f"{path} is not JSON", path=path))
            continue
        if not isinstance(raw, dict) or not raw.keys() >= META_REQUIRED_KEYS or raw.get("type") not in ID_PREFIXES:
            problems.append(anomaly("META_INVALID", f"{path} lacks schema-3 keys or has an unknown type", path=path))
            continue
        if raw.get("backend") != "github":
            problems.append(
                anomaly("META_INVALID", f"{path} has backend {raw.get('backend')!r}, not github", path=path)
            )
            continue
        github: dict[str, Any] = raw["github"] if isinstance(raw.get("github"), dict) else {}
        number = github.get("issue_number")
        depends: list[Any] = raw["depends_on"] if isinstance(raw.get("depends_on"), list) else []
        scopes.append(
            Scope(
                id=str(raw["id"]),
                kind=str(raw["type"]),
                title=str(raw.get("title") or ""),
                slug=str(raw.get("slug") or ""),
                parent_id=raw.get("parent_id") if isinstance(raw.get("parent_id"), str) else None,
                depends_on=[str(item) for item in depends],
                number=number if type(number) is int and number > 0 else None,
                owner=github.get("repo_owner") if isinstance(github.get("repo_owner"), str) else None,
                repo=github.get("repo_name") if isinstance(github.get("repo_name"), str) else None,
                directory=directory,
                raw=raw,
                payload=payload,
            )
        )
    return scopes, problems


# ---------------------------------------------------------------------------------------------------------------
# Flattening (Epic design ch. 11): nested Scope directories to <bucket>/<ID>/ and back, keeping relative links.
# ---------------------------------------------------------------------------------------------------------------

NESTED_DIRECTORIES: tuple[str, ...] = ("epics", "issues")
CHILD_RULE_FILES = frozenset(f"{name}/rules.md" for name in NESTED_DIRECTORIES)
DROPPED = "dropped"  # not copied: .meta.json, epics/rules.md, issues/rules.md
FLATTEN_NESTED_FILE = "FLATTEN_NESTED_FILE"
FLATTEN_OUTSIDE_SCOPE = "FLATTEN_OUTSIDE_SCOPE"
FLATTEN_SCOPE_UNMAPPED = "FLATTEN_SCOPE_UNMAPPED"
FLATTEN_DUPLICATE_ID = "FLATTEN_DUPLICATE_ID"
CATALOG_PATH_OUTSIDE_SCOPE = "CATALOG_PATH_OUTSIDE_SCOPE"
MARKDOWN_SUFFIXES = (".md",)
HTML_SUFFIXES = (".html", ".htm")


@dataclass(frozen=True)
class Layout:
    """Scope directories of one nested tree (paths relative to spec-dock/initiatives) and their catalog places."""

    places: dict[str, str]  # Scope directory -> scope_relative(new ID), or a pending place for plan
    unmapped: dict[str, dict[str, Any]]  # Scope directory -> FLATTEN_SCOPE_UNMAPPED / FLATTEN_DUPLICATE_ID
    pending: dict[str, str]  # Scope directory -> local ID still to be created by register (plan only)


def _identity(payload: bytes) -> tuple[Any, Any, Any] | None:
    """(type, id, github.issue_number) of a .meta.json; nothing else is read, so old history files work too."""
    try:
        raw = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    github = raw.get("github")
    return raw.get("type"), raw.get("id"), github.get("issue_number") if isinstance(github, dict) else None


def _place_of(identity: tuple[Any, Any, Any] | None, idmap: Mapping[str, Mapping[str, Any]]) -> str | None:
    if identity is None:
        return None
    kind, value, number = identity
    if not isinstance(value, str):
        return None
    if LOCAL_ID_RE.fullmatch(value):
        entry = idmap.get(value) or {}
        if isinstance(entry.get("relative"), str):
            return entry["relative"]
        new = entry.get("id")
        return scope_relative(new) if isinstance(new, str) and CANONICAL_ID_RE.fullmatch(new) else None
    if kind not in ID_PREFIXES or CANONICAL_ID_RE.fullmatch(value) is None:
        return None
    if not value.startswith(f"{ID_PREFIXES[kind]}-") or type(number) is not int or number != int(value.split("-")[1]):
        return None
    return scope_relative(value)


def nested_layout(metas: Mapping[str, bytes], idmap: Mapping[str, Mapping[str, Any]]) -> Layout:
    """A Scope directory has .meta.json and sits at the root or right under a Scope's epics/ or issues/."""

    def is_scope(directory: str) -> bool:
        if directory not in metas:
            return False
        parts = directory.split("/")
        if len(parts) == 1:
            return True
        return len(parts) >= 3 and parts[-2] in NESTED_DIRECTORIES and is_scope("/".join(parts[:-2]))

    unmapped: dict[str, dict[str, Any]] = {}
    pending: dict[str, str] = {}
    by_place: dict[str, list[str]] = {}
    for directory in sorted(d for d in metas if is_scope(d)):
        identity = _identity(metas[directory])
        place = _place_of(identity, idmap)
        if place is None:
            value = identity[1] if identity is not None else None
            unmapped[directory] = anomaly(
                FLATTEN_SCOPE_UNMAPPED,
                f"{directory}: its .meta.json gives no Scope ID (id {value!r}; a local ID needs register first)",
                path=directory,
            )
            continue
        by_place.setdefault(place, []).append(directory)
        if not place.split("/", 1)[0][:1].isdigit():
            pending[directory] = str(identity[1])  # type: ignore[index]
    places: dict[str, str] = {}
    for place, directories in by_place.items():
        if len(directories) == 1:
            places[directories[0]] = place
            continue
        for directory in directories:
            pending.pop(directory, None)
            unmapped[directory] = anomaly(
                FLATTEN_DUPLICATE_ID, f"{', '.join(directories)} all become {place}", path=directory
            )
    return Layout(places, unmapped, pending)


class FlatMap:
    """Nested -> flat paths relative to spec-dock/initiatives."""

    def __init__(self, layout: Layout) -> None:
        self.layout = layout
        self._scopes = set(layout.places) | set(layout.unmapped)

    def _scope(self, path: str, *, include_self: bool) -> tuple[str | None, str]:
        parts = path.split("/") if path else []
        for size in range(len(parts) if include_self else len(parts) - 1, 0, -1):
            directory = "/".join(parts[:size])
            if directory in self._scopes:
                return directory, "/".join(parts[size:])
        return None, path

    def file(self, path: str) -> str | dict[str, Any]:
        """Where a file goes, DROPPED, or the anomaly that keeps it from being flattened."""
        if PurePosixPath(path).name == META_FILE:
            return DROPPED
        scope, rest = self._scope(path, include_self=False)
        if scope is None:
            return anomaly(FLATTEN_OUTSIDE_SCOPE, f"{path} is in no Scope directory", path=path)
        if scope in self.layout.unmapped:
            return self.layout.unmapped[scope]
        if rest in CHILD_RULE_FILES:
            return DROPPED
        if rest.split("/", 1)[0] in NESTED_DIRECTORIES:
            return anomaly(
                FLATTEN_NESTED_FILE, f"{path} is under {scope}'s child layer but in no child Scope", path=path
            )
        return f"{self.layout.places[scope]}/{rest}"

    def dropped_rule(self, path: str) -> bool:
        scope, rest = self._scope(path, include_self=False)
        return scope in self.layout.places and rest in CHILD_RULE_FILES

    def place(self, path: str) -> str | None:
        """Where a path (file or directory) is after flattening; a vanished epics/ or issues/ is its Scope."""
        if path in ("", "."):
            return ""
        scope, rest = self._scope(path, include_self=True)
        if scope is None or scope not in self.layout.places:
            return None
        base = self.layout.places[scope]
        if not rest or rest in NESTED_DIRECTORIES:
            return base
        if rest.split("/", 1)[0] in NESTED_DIRECTORIES:
            return None
        return f"{base}/{rest}"


class NestMap:
    """Flat -> nested paths relative to spec-dock/initiatives (export-legacy); nested maps an ID to its directory."""

    def __init__(self, nested: Mapping[str, str]) -> None:
        self.nested = nested

    def _split(self, path: str) -> tuple[str, str] | None:
        parts = path.split("/")
        if len(parts) < 2 or parts[1] not in self.nested or scope_relative(parts[1]) != f"{parts[0]}/{parts[1]}":
            return None
        return self.nested[parts[1]], "/".join(parts[2:])

    def file(self, path: str) -> str | dict[str, Any]:
        found = self._split(path)
        if found is None or not found[1]:
            return anomaly(CATALOG_PATH_OUTSIDE_SCOPE, f"{path} is not inside a Scope's <bucket>/<ID>/", path=path)
        return f"{found[0]}/{found[1]}"

    def dropped_rule(self, path: str) -> bool:  # noqa: ARG002 - the flat catalog drops nothing
        return False

    def place(self, path: str) -> str | None:
        if path in ("", "."):
            return ""
        found = self._split(path)
        if found is None:
            return None
        return f"{found[0]}/{found[1]}" if found[1] else found[0]


@dataclass(frozen=True)
class Link:
    file: str  # the file's new path, relative to the repository
    text: str  # the link as written
    rewritten: str | None  # the new text, or None when it stays
    before: str  # what it opened at the old path (repository-relative)
    after: str | None  # what it should open at the new path; None when the target has no place


@dataclass(frozen=True)
class _Span:
    start: int
    end: int
    value: str


_URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_BLANK_LINE = re.compile(r"\n[ \t]*\n")
_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", re.DOTALL)
_INLINE_LINK = re.compile(r"\]\(\s*(?:<([^>\n]+)>|([^\s()<>]+))")
_REFERENCE_LINK = re.compile(r"^ {0,3}\[[^\]\n]+\]:[ \t]*(?:<([^>\n]+)>|(\S+))", re.MULTILINE)
_HTML_LINK = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"\n]*)"|'([^'\n]*)')""", re.IGNORECASE)


def _code_ranges(text: str) -> list[tuple[int, int]]:
    """Fenced blocks and code spans of a Markdown text, which hold no links."""
    ranges: list[tuple[int, int]] = []
    position = 0
    fence: str | None = None
    fence_start = 0
    prose_start = 0
    for line in text.splitlines(keepends=True):
        matched = _FENCE.match(line)
        if fence is None and matched:
            fence, fence_start = matched.group(1), position
            ranges.extend(_span_ranges(text, prose_start, position))
        elif fence is not None and matched and matched.group(1)[0] == fence[0] and len(matched.group(1)) >= len(fence):
            ranges.append((fence_start, position + len(line)))
            fence = None
            prose_start = position + len(line)
        position += len(line)
    if fence is not None:
        ranges.append((fence_start, len(text)))
    else:
        ranges.extend(_span_ranges(text, prose_start, len(text)))
    return ranges


def _span_ranges(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """Code spans between start and end; a span never crosses a blank line, so a lone backtick stays text."""
    ranges: list[tuple[int, int]] = []
    paragraph = start
    for gap in [*_BLANK_LINE.finditer(text, start, end), None]:
        stop = gap.start() if gap is not None else end
        ranges.extend((paragraph + m.start(), paragraph + m.end()) for m in _CODE_SPAN.finditer(text[paragraph:stop]))
        if gap is not None:
            paragraph = gap.end()
    return ranges


def find_links(payload: bytes, kind: str) -> tuple[str, list[_Span]] | None:
    """The decoded text and the link targets in it; None when the payload is not UTF-8."""
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if kind == "symlink":
        return text, [_Span(0, len(text), text)]
    patterns = (_INLINE_LINK, _REFERENCE_LINK) if kind == "markdown" else (_HTML_LINK,)
    code = _code_ranges(text) if kind == "markdown" else []
    spans: list[_Span] = []
    for pattern in patterns:
        for matched in pattern.finditer(text):
            group = 1 if matched.group(1) is not None else 2
            start, end = matched.span(group)
            if any(low <= start < high for low, high in code):
                continue
            spans.append(_Span(start, end, matched.group(group)))
    return text, sorted(spans, key=lambda span: span.start)


def _relative_parts(value: str) -> tuple[str, str] | None:
    """(path, suffix) of a relative link; None for URLs, anchors, absolute paths and empty paths."""
    stripped = value.strip()
    if not stripped or _URL.match(stripped) or stripped.startswith(("#", "/")):
        return None
    cut = min((index for index in (stripped.find("#"), stripped.find("?")) if index >= 0), default=len(stripped))
    path, suffix = stripped[:cut], stripped[cut:]
    return (path, suffix) if path else None


def _resolve(directory: str, path: str) -> str | None:
    joined = posixpath.normpath(posixpath.join(directory, unquote(path)))
    return None if joined == ".." or joined.startswith("../") else joined


def link_target(mapping: FlatMap | NestMap, symlinks: Mapping[str, bytes]) -> Callable[[str], str | None]:
    """Repository path at the old place -> repository path at the new place (None: no place for it)."""

    def target(path: str, depth: int = 0) -> str | None:
        if path != SPEC_ROOT and not path.startswith(f"{SPEC_ROOT}/"):
            return path
        inner = path[len(SPEC_ROOT) + 1 :]
        if mapping.dropped_rule(inner):
            content = symlinks.get(inner)
            final = _resolve(posixpath.dirname(path), content.decode("utf-8", "replace")) if content else None
            return target(final, depth + 1) if final is not None and depth < 8 else None
        place = mapping.place(inner)
        return None if place is None else (f"{SPEC_ROOT}/{place}" if place else SPEC_ROOT)

    return target


def plan_links(
    spans: Sequence[_Span], old: str, target: Callable[[str], str | None]
) -> list[tuple[str, str | None, str | None]]:
    """(text, before, after) per span; before is None for URLs, anchors and paths outside the repository."""
    planned = []
    for span in spans:
        parts = _relative_parts(span.value)
        before = _resolve(posixpath.dirname(old), parts[0]) if parts else None
        planned.append((span.value, before, target(before) if before is not None else None))
    return planned


def rewrite_links(
    payload: bytes, *, kind: str, old: str, new: str, target: Callable[[str], str | None]
) -> tuple[bytes, list[Link]]:
    found = find_links(payload, kind)
    if found is None:
        return payload, []
    text, spans = found
    rewritten, links = apply_links(text, spans, plan_links(spans, old, target), new=new)
    return (payload if rewritten is None else rewritten.encode("utf-8")), links


def apply_links(
    text: str, spans: Sequence[_Span], planned: Sequence[tuple[str, str | None, str | None]], *, new: str
) -> tuple[str | None, list[Link]]:
    """The text with each link that would open another target at `new` rewritten; None when nothing changes."""
    directory = posixpath.dirname(new)
    pieces: list[str] = []
    links: list[Link] = []
    cursor = 0
    for span, (value, before, after) in zip(spans, planned, strict=True):
        if before is None:
            continue
        path, suffix = _relative_parts(value)  # type: ignore[misc]
        rewritten = None
        if after is not None and _resolve(directory, path) != after:
            rewritten = posixpath.relpath(after, directory)
            if path.endswith("/") and not rewritten.endswith("/"):
                rewritten += "/"
            if "%" in path:
                rewritten = quote(rewritten, safe="/._-~")
            rewritten += suffix
            pieces.append(text[cursor : span.start])
            pieces.append(text[span.start : span.end].replace(value.strip(), rewritten, 1))
            cursor = span.end
        links.append(Link(new, value, rewritten, before, after))
    if cursor == 0:
        return None, links
    pieces.append(text[cursor:])
    return "".join(pieces), links


class PathSet:
    """Files and their parent directories, repository-relative."""

    def __init__(self, files: Iterable[str]) -> None:
        self.items: set[str] = set()
        for path in files:
            self.items.add(path)
            parent = posixpath.dirname(path)
            while parent and parent not in self.items:
                self.items.add(parent)
                parent = posixpath.dirname(parent)

    def __contains__(self, path: object) -> bool:
        return path in self.items


@dataclass
class LinkReport:
    rewritten: int = 0
    unrewritable: list[dict[str, str]] = field(default_factory=list)
    broken_before: list[dict[str, str]] = field(default_factory=list)

    def as_data(self) -> dict[str, Any]:
        return {
            "rewritten": self.rewritten,
            "unrewritable": self.unrewritable,
            "broken_before": self.broken_before,
        }


def link_report(links: Iterable[Link], before: PathSet, after: PathSet) -> LinkReport:
    """Links that opened before but not after are unrewritable; links already broken are listed apart."""
    report = LinkReport()
    for link in links:
        if link.rewritten is not None:
            report.rewritten += 1
        item = {"file": link.file, "text": link.text, "target": link.before}
        if link.before not in before:
            report.broken_before.append(item)
        elif link.after is None or link.after not in after:
            report.unrewritable.append(item)
    return report


def linkable(path: str, mode: str) -> str | None:
    """The link kind a tree entry may hold."""
    if mode == "120000":
        return "symlink"
    if path.endswith(MARKDOWN_SUFFIXES):
        return "markdown"
    if path.endswith(HTML_SUFFIXES):
        return "html"
    return None


@dataclass
class Flattened:
    entries: list[TreeEntry]  # paths relative to spec-dock/initiatives after flattening
    problems: list[dict[str, Any]]  # what cannot be flattened (left out; a caller flattening a tip stops)
    dropped: dict[str, int]  # paths left out, by anomaly code
    links: list[Link]
    layout: Layout
    moved: dict[str, TreeEntry | None] = field(default_factory=dict)  # source path -> flattened entry (None: dropped)


class TreeFlattener:
    """Flattens nested spec trees read from one repository, remembering parsed and rewritten blobs.

    With a scratch directory (a throwaway clone) rewritten blobs are written; without one (the real repository)
    nothing is written and their object ids are computed in memory.
    """

    def __init__(self, repo: Path, idmap: Mapping[str, Mapping[str, Any]], scratch: Path | None) -> None:
        self.repo = repo
        self.idmap = idmap
        self.scratch = scratch
        self._small: dict[str, bytes] = {}  # .meta.json and symlink payloads
        self._parsed: dict[tuple[str, str], tuple[str, list[_Span]] | None] = {}
        self._results: dict[tuple[Any, ...], tuple[str | None, list[Link]]] = {}
        self._format: str | None = None

    def _object_id(self, payload: bytes) -> str:
        if self._format is None:
            self._format = git_text(self.repo, "rev-parse", "--show-object-format", ok=(0, 128)) or "sha1"
        digest = hashlib.sha256 if self._format == "sha256" else hashlib.sha1
        return digest(b"blob %d\0" % len(payload) + payload).hexdigest()

    def _write(self, payloads: Sequence[bytes]) -> list[str]:
        if not payloads:
            return []
        if self.scratch is None:
            return [self._object_id(payload) for payload in payloads]
        folder = Path(tempfile.mkdtemp(prefix="blobs-", dir=self.scratch))
        try:
            paths = []
            for index, payload in enumerate(payloads):
                path = folder / str(index)
                path.write_bytes(payload)
                paths.append(path)
            output = git_text(
                self.repo,
                "hash-object",
                "-w",
                "--no-filters",
                "--stdin-paths",
                input="".join(f"{path}\n" for path in paths).encode(),
                read_only=False,
            )
            return output.splitlines()
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def _read(self, entries: Sequence[TreeEntry]) -> None:
        small = [e.oid for e in entries if (e.mode == "120000" or e.path.endswith(f"/{META_FILE}"))]
        documents: list[tuple[str, str]] = []
        for entry in entries:
            kind = linkable(entry.path, entry.mode)
            if kind is not None and kind != "symlink":
                documents.append((entry.oid, kind))
        wanted = [oid for oid in small if oid not in self._small]
        wanted += [oid for oid, kind in documents if (oid, kind) not in self._parsed]
        blobs = read_blobs(self.repo, wanted)
        for oid in small:
            if oid in blobs:
                self._small[oid] = blobs[oid]
        for oid, kind in documents:
            if (oid, kind) not in self._parsed:
                found = find_links(blobs[oid], kind)
                self._parsed[oid, kind] = found if found is not None and found[1] else None

    def flatten(self, entries: Sequence[TreeEntry]) -> Flattened:
        """Paths that cannot be flattened are left out and listed; callers flattening a tip stop on them."""
        self._read(entries)
        metas = {
            str(PurePosixPath(e.path).parent): self._small[e.oid]
            for e in entries
            if PurePosixPath(e.path).name == META_FILE and "/" in e.path
        }
        layout = nested_layout(metas, self.idmap)
        mapping = FlatMap(layout)
        target = link_target(mapping, {e.path: self._small[e.oid] for e in entries if e.mode == "120000"})
        result: list[TreeEntry] = []
        problems: dict[tuple[str, str], dict[str, Any]] = {}
        dropped: dict[str, int] = {}
        links: list[Link] = []
        pending: list[tuple[int, bytes, tuple[Any, ...]]] = []
        sources: list[str] = []
        moved: dict[str, TreeEntry | None] = {}
        for entry in entries:
            place = mapping.file(entry.path)
            if place == DROPPED:
                moved[entry.path] = None
                continue
            if isinstance(place, dict):
                problems.setdefault((place["code"], str(place.get("path"))), place)
                dropped[place["code"]] = dropped.get(place["code"], 0) + 1
                continue
            oid = entry.oid
            kind = linkable(entry.path, entry.mode)
            parsed = None
            if kind == "symlink":
                parsed = find_links(self._small[entry.oid], kind)
            elif kind is not None:
                parsed = self._parsed[entry.oid, kind]
            if parsed is not None:
                text, spans = parsed
                old, new = f"{SPEC_ROOT}/{entry.path}", f"{SPEC_ROOT}/{place}"
                planned = plan_links(spans, old, target)
                key = (entry.oid, kind, old, new, tuple(item[2] for item in planned))
                if key not in self._results:
                    rewritten, file_links = apply_links(text, spans, planned, new=new)
                    self._results[key] = (None, file_links)
                    if rewritten is not None:
                        pending.append((len(result), rewritten.encode("utf-8"), key))
                cached_oid, file_links = self._results[key]
                oid = cached_oid or oid
                links.extend(file_links)
            result.append(TreeEntry(entry.mode, entry.kind, oid, place))
            sources.append(entry.path)
        for (index, _, key), written in zip(pending, self._write([item[1] for item in pending]), strict=True):
            self._results[key] = (written, self._results[key][1])
            old_entry = result[index]
            result[index] = TreeEntry(old_entry.mode, old_entry.kind, written, old_entry.path)
        moved.update(zip(sources, result, strict=True))
        return Flattened(result, list(problems.values()), dropped, links, layout, moved)


def flattened_links(source: Sequence[TreeEntry], flat: Flattened, prefix: str = SPEC_ROOT) -> LinkReport:
    """Link report of one flattening: source holds the whole repository tree at the old place."""
    before = PathSet(e.path for e in source)
    outside = (e.path for e in source if e.path != prefix and not e.path.startswith(f"{prefix}/"))
    after = PathSet([*outside, *(f"{prefix}/{e.path}" for e in flat.entries)])
    return link_report(flat.links, before, after)


def write_commit(repo: Path, raw: bytes, tree: str, parents: Sequence[str]) -> str:
    """A copy of a commit with another tree and parents; author, committer, dates and message stay."""
    header, _, message = raw.partition(b"\n\n")
    kept: list[bytes] = []
    skipping = False
    for line in header.split(b"\n"):
        if line.startswith(b" ") and skipping:
            continue
        skipping = line.split(b" ", 1)[0] in (b"tree", b"parent", b"gpgsig", b"gpgsig-sha256", b"mergetag")
        if not skipping:
            kept.append(line)
    lines = [b"tree " + tree.encode(), *(b"parent " + parent.encode() for parent in parents), *kept]
    payload = b"\n".join(lines) + b"\n\n" + message
    return git_text(repo, "hash-object", "-t", "commit", "-w", "--stdin", input=payload, read_only=False)


@dataclass
class History:
    tip: str
    commits: int = 0
    dropped_commits: int = 0
    dropped: dict[str, int] = field(default_factory=dict)
    examples: dict[str, list[str]] = field(default_factory=dict)

    def as_data(self) -> dict[str, Any]:
        return {
            "commits": self.commits,
            "dropped_commits": self.dropped_commits,
            "dropped_paths": self.dropped,
            "examples": self.examples,
        }


def rewrite_history(repo: Path, tip: str, flattener: TreeFlattener, scratch: Path) -> History:
    """Flatten every commit of a subtree split; paths that cannot be flattened leave that commit only."""
    order = [
        line.split() for line in git_text(repo, "rev-list", "--reverse", "--topo-order", "--parents", tip).splitlines()
    ]
    raws = read_blobs(repo, [line[0] for line in order])
    mapped: dict[str, str] = {}
    history = History(tip="")
    for oid, *parents in order:
        flat = flattener.flatten(list_tree(repo, oid))
        tree = write_tree(repo, flat.entries, scratch)
        mapped[oid] = write_commit(repo, raws[oid], tree, [mapped[parent] for parent in parents])
        history.commits += 1
        if flat.dropped:
            history.dropped_commits += 1
            for code, count in flat.dropped.items():
                history.dropped[code] = history.dropped.get(code, 0) + count
        for item in flat.problems:
            examples = history.examples.setdefault(item["code"], [])
            if len(examples) < 5 and item["path"] not in examples:
                examples.append(item["path"])
    history.tip = mapped[tip]
    return history


# ---------------------------------------------------------------------------------------------------------------
# GitHub.
# ---------------------------------------------------------------------------------------------------------------


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: Any


class GithubError(Exception):
    def __init__(self, message: str, *, status: int | None = None, unknown: bool = False) -> None:
        super().__init__(message)
        self.status = status
        self.unknown = unknown


class Github:
    """Sequential `gh api` calls: reads retry rate limits and server errors, writes are paced (Epic design ch. 11)."""

    def __init__(self, owner: str, name: str, *, runner: Callable[..., Any] | None = None, clock: Any = None) -> None:
        self.owner = owner
        self.name = name
        self.runner = runner or subprocess.run
        self.clock = clock or SystemClock()
        self.write_times: list[float] = []
        self.write_count = 0
        self._login: str | None = None

    @property
    def prefix(self) -> str:
        return f"repos/{self.owner}/{self.name}"

    def login(self) -> str:
        """The account gh acts as (GET /user), read once."""
        if self._login is None:
            body = self.read("user").body
            self._login = str(body.get("login") or "") if isinstance(body, dict) else ""
        return self._login

    def _call(self, method: str, endpoint: str, payload: object = None) -> Response:
        argv = ["gh", "api", "--hostname", "github.com", "--include", "--method", method, endpoint]
        stdin = None
        if payload is not None:
            argv += ["--input", "-"]
            stdin = json.dumps(payload, ensure_ascii=False)
        try:
            completed = self.runner(argv, input=stdin, capture_output=True, text=True, check=False, timeout=120)
        except subprocess.TimeoutExpired as error:
            raise GithubError(f"{method} {endpoint} timed out", unknown=True) from error
        except OSError as error:
            raise GithubError(f"gh could not run: {error}", unknown=True) from error
        return parse_response(completed.stdout or "", method, endpoint)

    @staticmethod
    def _rate_limited(response: Response) -> bool:
        if response.status not in (403, 429):
            return False
        text = json.dumps(response.body).lower() if response.body is not None else ""
        return (
            "retry-after" in response.headers
            or response.headers.get("x-ratelimit-remaining") == "0"
            or "rate limit" in text
        )

    def _wait_for(self, response: Response) -> float:
        if "retry-after" in response.headers:
            try:
                return max(float(response.headers["retry-after"]), 0.0)
            except ValueError:
                return 60.0
        reset = response.headers.get("x-ratelimit-reset")
        if reset and reset.isdigit():
            return max(float(reset) - self.clock.now().timestamp(), 0.0) + 1.0
        return 60.0

    def read(
        self, endpoint: str, *, ok: Iterable[int] = (200,), method: str = "GET", payload: object = None
    ) -> Response:
        accepted = tuple(ok)
        failures = 0
        server_waits = iter((1.0, 2.0, 4.0))
        while True:
            try:
                response = self._call(method, endpoint, payload)
            except GithubError as error:
                wait = next(server_waits, None)
                if wait is None:
                    raise GithubError(f"{error}; GitHub is unreachable") from error
                self.clock.sleep(wait)
                continue
            if response.status in accepted:
                return response
            if self._rate_limited(response):
                wait = self._wait_for(response)
                failures += 1
                if wait > READ_RETRY_LIMIT or failures > 3:
                    raise GithubError(f"GitHub rate limit; retry after {wait:.0f}s", status=response.status)
                self.clock.sleep(wait)
                continue
            if response.status >= 500:
                wait = next(server_waits, None)
                if wait is None:
                    raise GithubError(f"{method} {endpoint} answered {response.status}", status=response.status)
                self.clock.sleep(wait)
                continue
            raise GithubError(
                f"{method} {endpoint} answered {response.status}: {response.body}", status=response.status
            )

    def graphql(self, query: str, variables: Mapping[str, object]) -> dict[str, Any]:
        for attempt in range(4):
            response = self.read("graphql", method="POST", payload={"query": query, "variables": dict(variables)})
            body = response.body if isinstance(response.body, dict) else {}
            if not any(item.get("type") == "RATE_LIMITED" for item in body.get("errors") or []):
                break
            if attempt == 3:
                raise GithubError("GitHub GraphQL rate limit; retry later")
            self.clock.sleep(READ_RETRY_LIMIT)
        errors = [item for item in body.get("errors") or [] if item.get("type") != "NOT_FOUND"]
        if errors or not isinstance(body.get("data"), dict):
            raise GithubError(f"GraphQL error: {errors or body}")
        return body["data"]

    def _pace(self) -> None:
        while True:
            now = self.clock.monotonic()
            recent = [moment for moment in self.write_times if now - moment < 3600]
            self.write_times = recent
            waits = [0.0]
            if recent:
                waits.append(recent[-1] + WRITE_INTERVAL - now)
            minute = [moment for moment in recent if now - moment < 60]
            if len(minute) >= WRITES_PER_MINUTE:
                waits.append(minute[-WRITES_PER_MINUTE] + 60 - now)
            if len(recent) >= WRITES_PER_HOUR:
                waits.append(recent[-WRITES_PER_HOUR] + 3600 - now)
            wait = max(waits)
            if wait <= 0:
                return
            self.clock.sleep(wait)

    def write(
        self, method: str, endpoint: str, payload: object = None, *, ok: Iterable[int] = (200, 201, 204)
    ) -> Response:
        """One paced write; a rate limit waits and repeats it, an unknown outcome raises GithubError(unknown=True)."""
        accepted = tuple(ok)
        limited = 0
        while True:
            self._pace()
            self.write_times.append(self.clock.monotonic())
            self.write_count += 1
            response = self._call(method, endpoint, payload)
            if response.status in accepted:
                return response
            if self._rate_limited(response):
                wait = self._wait_for(response)
                limited += 1
                if wait > WRITE_RETRY_LIMIT or limited > 5:
                    raise GithubError(f"GitHub rate limit on {method} {endpoint}; retry later", status=response.status)
                self.clock.sleep(wait)
                continue
            if response.status >= 500:
                raise GithubError(
                    f"{method} {endpoint} answered {response.status}", status=response.status, unknown=True
                )
            raise GithubError(
                f"{method} {endpoint} answered {response.status}: {response.body}", status=response.status
            )


def parse_response(stdout: str, method: str, endpoint: str) -> Response:
    text = stdout.replace("\r\n", "\n")
    head, separator, body_text = text.partition("\n\n")
    lines = head.split("\n")
    matched = re.match(r"^HTTP/\S+\s+(\d{3})", lines[0]) if lines else None
    if matched is None or (not separator and not head.startswith("HTTP/")):
        raise GithubError(f"{method} {endpoint}: unreadable gh output", unknown=method != "GET")
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    body: Any = None
    if body_text.strip():
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            body = body_text
    return Response(int(matched.group(1)), headers, body)


@dataclass
class Facts:
    number: int
    database_id: int
    title: str
    state: str
    labels: list[str]
    parent: int | None
    parent_foreign: str | None
    blocked_by: list[int]
    blocked_foreign: list[str]
    author: str = ""
    created_at: str = ""

    @property
    def kind_labels(self) -> list[str]:
        return sorted(label for label in self.labels if label in KIND_LABELS.values())


_ISSUE_FIELDS = (
    "number databaseId title state stateReason author { login } createdAt "
    "labels(first: 20) { totalCount nodes { name } } "
    "parent { number repository { nameWithOwner } } "
    "blockedBy(first: 100) { totalCount nodes { number state title repository { nameWithOwner } } }"
)
_LABELED_QUERY = (
    "query($owner: String!, $name: String!, $after: String) { rateLimit { cost remaining resetAt } "
    "repository(owner: $owner, name: $name) { issues(first: 100, after: $after, states: [OPEN, CLOSED], "
    'labels: ["spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"]) { '
    "pageInfo { hasNextPage endCursor } nodes { " + _ISSUE_FIELDS + " } } } }"
)


def _facts(gh: Github, node: Mapping[str, Any]) -> Facts:
    own = f"{gh.owner}/{gh.name}".lower()
    number = int(node["number"])
    labels_node = node.get("labels") or {}
    labels = [item["name"] for item in labels_node.get("nodes") or []]
    if (labels_node.get("totalCount") or 0) > len(labels):
        labels = [item["name"] for item in _rest_pages(gh, f"{gh.prefix}/issues/{number}/labels")]
    parent_node = node.get("parent")
    parent = parent_foreign = None
    if parent_node:
        parent_repo = str((parent_node.get("repository") or {}).get("nameWithOwner", "")).lower()
        if parent_repo == own:
            parent = int(parent_node["number"])
        else:
            parent_foreign = f"{parent_repo}#{parent_node['number']}"
    blocked_node = node.get("blockedBy") or {}
    references = [
        (str((item.get("repository") or {}).get("nameWithOwner", "")).lower(), int(item["number"]))
        for item in blocked_node.get("nodes") or []
    ]
    if (blocked_node.get("totalCount") or 0) > len(references):
        references = [
            (_repository_of(item), int(item["number"]))
            for item in _rest_pages(gh, f"{gh.prefix}/issues/{number}/dependencies/blocked_by")
        ]
    return Facts(
        number=number,
        database_id=int(node["databaseId"]),
        title=str(node.get("title") or ""),
        state=str(node.get("state") or "").lower(),
        labels=labels,
        parent=parent,
        parent_foreign=parent_foreign,
        blocked_by=sorted(n for repo, n in references if repo == own),
        blocked_foreign=[f"{repo}#{n}" for repo, n in references if repo != own],
        author=str((node.get("author") or {}).get("login") or ""),
        created_at=str(node.get("createdAt") or ""),
    )


def _repository_of(item: Mapping[str, Any]) -> str:
    url = str(item.get("repository_url") or "")
    return "/".join(url.rstrip("/").split("/")[-2:]).lower()


def _rest_pages(gh: Github, endpoint: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    while True:
        response = gh.read(f"{endpoint}?per_page=100&page={page}")
        chunk = response.body if isinstance(response.body, list) else []
        items.extend(chunk)
        if len(chunk) < 100:
            return items
        page += 1


def fetch_numbers(gh: Github, numbers: Iterable[int]) -> dict[int, Facts]:
    """Read Issues by number with aliased GraphQL fields; a missing number or a pull request is absent."""
    wanted = sorted(set(numbers))
    found: dict[int, Facts] = {}
    for start in range(0, len(wanted), NUMBER_BATCH):
        chunk = wanted[start : start + NUMBER_BATCH]
        fields = " ".join(f"i{n}: issue(number: {n}) {{ {_ISSUE_FIELDS} }}" for n in chunk)
        query = f"query($owner: String!, $name: String!) {{ repository(owner: $owner, name: $name) {{ {fields} }} }}"
        data = gh.graphql(query, {"owner": gh.owner, "name": gh.name})
        repository = data.get("repository") or {}
        for n in chunk:
            node = repository.get(f"i{n}")
            if node:
                found[n] = _facts(gh, node)
    return found


def fetch_labeled(gh: Github) -> dict[int, Facts]:
    found: dict[int, Facts] = {}
    after: str | None = None
    while True:
        data = gh.graphql(_LABELED_QUERY, {"owner": gh.owner, "name": gh.name, "after": after})
        issues = (data.get("repository") or {}).get("issues") or {}
        for node in issues.get("nodes") or []:
            facts = _facts(gh, node)
            found[facts.number] = facts
        page = issues.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            return found
        after = page.get("endCursor")


def label_exists(gh: Github, name: str) -> bool:
    return gh.read(f"{gh.prefix}/labels/{name}", ok=(200, 404)).status == 200


# ---------------------------------------------------------------------------------------------------------------
# Analysis shared by plan, register and verify.
# ---------------------------------------------------------------------------------------------------------------


@dataclass
class Analysis:
    scopes: list[Scope]
    problems: list[dict[str, Any]]
    facts: dict[int, Facts]
    labeled: dict[int, Facts]
    numbers: dict[str, int | None]  # Scope ID (as in .meta.json) -> Issue number after the ID map (None: to create)
    new_ids: dict[str, str]  # Scope ID -> ID after the ID map
    local_plan: dict[str, dict[str, Any]]

    @property
    def blocking(self) -> list[dict[str, Any]]:
        return [item for item in self.problems if item["blocking"]]

    def scope_numbers(self) -> set[int]:
        return {n for n in self.numbers.values() if n is not None} | set(self.labeled)


def analyze(gh: Github, scopes: list[Scope], problems: list[dict[str, Any]], state: State) -> Analysis:
    problems = list(problems)
    by_id = {scope.id: scope for scope in scopes}
    wanted = {scope.number for scope in scopes if scope.number is not None}
    wanted |= {entry["number"] for entry in state.idmap.values() if isinstance(entry.get("number"), int)}
    facts = fetch_numbers(gh, wanted)
    labeled = fetch_labeled(gh)
    numbers: dict[str, int | None] = {}
    new_ids: dict[str, str] = {}
    local_plan: dict[str, dict[str, Any]] = {}
    for scope in scopes:
        if scope.local:
            entry = state.idmap.get(scope.id)
            if entry is not None:
                numbers[scope.id] = int(entry["number"])
                new_ids[scope.id] = str(entry["id"])
                local_plan[scope.id] = dict(entry)
                how = f"mapped to {entry['id']} (#{entry['number']}, {entry['how']})"
            else:
                linked = facts.get(scope.number) if scope.number else None
                if linked is not None and linked.title == scope.title:
                    new_id = scope_id(scope.kind, linked.number)
                    numbers[scope.id] = linked.number
                    new_ids[scope.id] = new_id
                    local_plan[scope.id] = {"how": "existing", "number": linked.number, "id": new_id}
                    how = f"will map to {new_id} (#{linked.number} has the same title)"
                else:
                    numbers[scope.id] = None
                    new_ids[scope.id] = scope.id
                    local_plan[scope.id] = {"how": "created", "number": None, "id": None}
                    reason = (
                        f"#{scope.number} is titled {linked.title!r}"
                        if linked is not None
                        else f"#{scope.number} does not exist"
                        if scope.number
                        else "no Issue is linked"
                    )
                    how = f"register will create a new {scope.kind} Issue titled {scope.title!r} ({reason})"
            problems.append(anomaly("LOCAL_SCOPE", f"{scope.id} is a local Scope; {how}", scope=scope.id))
            continue
        numbers[scope.id] = scope.number
        new_ids[scope.id] = scope.id
        if scope.number is not None and scope.number not in facts:
            problems.append(
                anomaly(
                    "ISSUE_MISSING",
                    f"{scope.id}: Issue #{scope.number} does not exist or is a pull request",
                    scope=scope.id,
                )
            )
    problems.extend(metadata_problems(scopes, numbers))
    for scope in scopes:
        parent = by_id.get(scope.parent_id) if scope.parent_id else None
        own_number = numbers.get(scope.id)
        own = facts.get(own_number) if own_number is not None else None
        if own is None:
            continue
        if not (scope.local and local_plan[scope.id]["how"] == "created") and own.title != scope.title:
            problems.append(
                anomaly(
                    "TITLE_MISMATCH",
                    f"{scope.id}: .meta.json {scope.title!r} vs GitHub {own.title!r} (GitHub is kept)",
                    scope=scope.id,
                )
            )
        expected_label = KIND_LABELS[scope.kind]
        if any(label != expected_label for label in own.kind_labels):
            problems.append(
                anomaly("KIND_LABEL_CONFLICT", f"{scope.id}: #{own.number} has {own.kind_labels}", scope=scope.id)
            )
        parent_number = numbers.get(parent.id) if parent is not None else None
        if own.parent_foreign or (own.parent is not None and own.parent != parent_number):
            problems.append(
                anomaly(
                    "PARENT_CONFLICT",
                    f"{scope.id}: #{own.number} already has parent {own.parent_foreign or '#' + str(own.parent)}",
                    scope=scope.id,
                )
            )
        parent_facts = facts.get(parent_number) if parent_number else None
        if parent_facts is not None and parent_facts.state == "closed" and own.state == "open":
            problems.append(
                anomaly("CLOSED_PARENT_OPEN_CHILD", f"{scope.id} is open under closed {parent.id}", scope=scope.id)  # type: ignore[union-attr]
            )
    known = {n for n in numbers.values() if n is not None}
    for number in sorted(set(labeled) - known):
        problems.append(
            anomaly(
                "GITHUB_SCOPE_UNKNOWN",
                f"#{number} has {labeled[number].kind_labels} but no .meta.json",
                number=number,
            )
        )
    return Analysis(scopes, problems, facts, labeled, numbers, new_ids, local_plan)


def metadata_problems(scopes: Sequence[Scope], numbers: Mapping[str, int | None]) -> list[dict[str, Any]]:
    """Anomalies visible in .meta.json alone (numbers: Scope ID -> Issue number after the ID map)."""
    problems: list[dict[str, Any]] = []
    by_id: dict[str, Scope] = {}
    for scope in scopes:
        if scope.id in by_id:
            problems.append(anomaly("DUPLICATE_ID", f"{scope.id} appears more than once", scope=scope.id))
        by_id[scope.id] = scope
        if scope.local:
            continue
        matched = GITHUB_ID_RE.fullmatch(scope.id)
        if matched is None:
            problems.append(anomaly("META_INVALID", f"{scope.id} is not a Scope ID", scope=scope.id))
        elif scope.number is None or int(matched.group(2)) != scope.number:
            problems.append(
                anomaly(
                    "ID_NUMBER_MISMATCH",
                    f"{scope.id} is linked to Issue #{scope.number}",
                    scope=scope.id,
                    number=scope.number,
                )
            )
    seen: dict[int, str] = {}
    for scope in scopes:
        number = numbers.get(scope.id)
        if number is None:
            continue
        if number in seen:
            problems.append(
                anomaly("DUPLICATE_NUMBER", f"{seen[number]} and {scope.id} use Issue #{number}", number=number)
            )
        seen[number] = scope.id
    for scope in scopes:
        expected_parent = PARENT_KINDS[scope.kind]
        parent = by_id.get(scope.parent_id) if scope.parent_id else None
        if scope.parent_id and parent is None:
            problems.append(
                anomaly("PARENT_MISSING", f"{scope.id}: parent {scope.parent_id} is not a Scope", scope=scope.id)
            )
        elif expected_parent is None and scope.parent_id:
            problems.append(anomaly("KIND_RULE", f"{scope.id}: an Initiative has no parent", scope=scope.id))
        elif expected_parent is not None and (parent is None or parent.kind != expected_parent):
            problems.append(
                anomaly(
                    "KIND_RULE", f"{scope.id}: the parent of a {scope.kind} must be a {expected_parent}", scope=scope.id
                )
            )
        for dependency in scope.depends_on:
            if dependency not in by_id:
                problems.append(
                    anomaly("DEPENDENCY_MISSING", f"{scope.id}: dependency {dependency} is not a Scope", scope=scope.id)
                )
    for cycle in _cycles(by_id):
        problems.append(anomaly("DEPENDENCY_CYCLE", " -> ".join(cycle), scopes=cycle))
    return problems


def _cycles(by_id: Mapping[str, Scope]) -> list[list[str]]:
    color: dict[str, int] = {}
    stack: list[str] = []
    found: list[list[str]] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for nxt in by_id[node].depends_on:
            if nxt not in by_id:
                continue
            if color.get(nxt) == 1:
                found.append([*stack[stack.index(nxt) :], nxt])
            elif nxt not in color:
                visit(nxt)
        stack.pop()
        color[node] = 2

    for node in sorted(by_id):
        if node not in color:
            visit(node)
    return found


# ---------------------------------------------------------------------------------------------------------------
# Registration plan.
# ---------------------------------------------------------------------------------------------------------------


@dataclass
class Operation:
    op: str
    scope: str | None = None
    number: int | None = None
    target: str | None = None  # parent / dependency Scope ID, or label name
    detail: str = ""

    def describe(self) -> str:
        return self.detail


def registration_plan(gh: Github, analysis: Analysis) -> list[Operation]:
    plan: list[Operation] = []
    for name, _color, _description in LABEL_DEFINITIONS:
        if not label_exists(gh, name):
            plan.append(Operation("label.create", target=name, detail=f"create label {name}"))
    conflicts = {(item.get("scope"), item["code"]) for item in analysis.problems}
    ordered = sorted(analysis.scopes, key=lambda s: (analysis.numbers.get(s.id) or 10**9, s.id))
    by_id = {scope.id: scope for scope in analysis.scopes}
    for scope in ordered:
        if analysis.numbers.get(scope.id) is None:
            plan.append(
                Operation("issue.create", scope.id, detail=f"create {scope.kind} Issue {scope.title!r} for {scope.id}")
            )
    for scope in ordered:
        number = analysis.numbers.get(scope.id)
        own = analysis.facts.get(number) if number else None
        label = KIND_LABELS[scope.kind]
        if own is None:
            continue  # created later in this run with its label
        if label not in own.labels and (scope.id, "KIND_LABEL_CONFLICT") not in conflicts:
            plan.append(Operation("issue.label", scope.id, number, label, f"label #{number} {label}"))
    for scope in ordered:
        if not scope.parent_id or scope.parent_id not in by_id:
            continue
        number = analysis.numbers.get(scope.id)
        own = analysis.facts.get(number) if number else None
        if own is not None and (own.parent is not None or own.parent_foreign):
            continue
        plan.append(
            Operation(
                "sub_issue", scope.id, number, scope.parent_id, f"make {scope.id} a sub-issue of {scope.parent_id}"
            )
        )
    for scope in ordered:
        number = analysis.numbers.get(scope.id)
        own = analysis.facts.get(number) if number else None
        for dependency in scope.depends_on:
            if dependency not in by_id:
                continue
            blocker = analysis.numbers.get(dependency)
            if own is not None and blocker is not None and blocker in own.blocked_by:
                continue
            plan.append(Operation("blocked_by", scope.id, number, dependency, f"{scope.id} blocked by {dependency}"))
    return plan


class Registrar:
    """Executes a registration plan, recording intent and outcome of every write in undo.jsonl."""

    def __init__(self, gh: Github, state: State, analysis: Analysis, report: Report) -> None:
        self.gh = gh
        self.state = state
        self.analysis = analysis
        self.report = report
        self.ids: dict[int, int] = {n: facts.database_id for n, facts in {**analysis.labeled, **analysis.facts}.items()}
        self.wrote = 0

    def run(self, plan: Sequence[Operation]) -> None:
        for operation in plan:
            try:
                self._apply(operation)
            except GithubError as error:
                raise self._stop(f"{operation.describe()}: {error}") from error

    def _stop(self, message: str) -> MigrationError:
        if self.wrote:
            return Stopped(message, "Run the same register --apply again; it continues from GitHub's current state")
        return Refused(message, "Run the same register --apply again")

    def _number(self, scope_id: str) -> int:
        number = self.analysis.numbers.get(scope_id)
        if number is None:
            raise self._stop(f"{scope_id} has no Issue yet")
        return number

    def _database_id(self, number: int) -> int:
        if number not in self.ids:
            response = self.gh.read(f"{self.gh.prefix}/issues/{number}")
            self.ids[number] = int(response.body["id"])
        return self.ids[number]

    def _record(self, phase: str, op: str, **details: Any) -> dict[str, Any]:
        return self.state.append_undo({"phase": phase, "op": op, **details}, self.gh.clock)

    def _write(self, op: str, details: dict[str, Any], send: Callable[[], Any], applied: Callable[[], bool]) -> Any:
        intent = self._record("intent", op, **details)
        try:
            result = send()
        except GithubError as error:
            if not error.unknown or not applied():
                raise
            result = None
        self.wrote += 1
        self._record("done", op, ref=intent["seq"], **details)
        return result

    def _apply(self, operation: Operation) -> None:
        gh = self.gh
        if operation.op == "label.create":
            name = operation.target or ""
            definition = next(item for item in LABEL_DEFINITIONS if item[0] == name)

            # Only a definition this run certainly created is recorded, so undo never deletes someone else's label.
            try:
                gh.write(
                    "POST", f"{gh.prefix}/labels", {"name": name, "color": definition[1], "description": definition[2]}
                )
            except GithubError as error:
                if error.status == 422 and label_exists(gh, name):
                    return
                raise
            self.wrote += 1
            self._record("done", "label.create", name=name)
            return
        scope = next(s for s in self.analysis.scopes if s.id == operation.scope)
        if operation.op == "issue.create":
            self._create(scope)
            return
        number = self._number(scope.id)
        if operation.op == "issue.label":
            label = operation.target or ""
            self._write(
                "issue.label",
                {"number": number, "label": label},
                lambda: gh.write("POST", f"{gh.prefix}/issues/{number}/labels", {"labels": [label]}),
                lambda: label in self._issue(number).get("labels_names", []),
            )
        elif operation.op == "sub_issue":
            parent = self._number(operation.target or "")
            child_id = self._database_id(number)
            self._write(
                "sub_issue",
                {"parent": parent, "child": number, "child_id": child_id},
                lambda: gh.write(
                    "POST",
                    f"{gh.prefix}/issues/{parent}/sub_issues",
                    {"sub_issue_id": child_id, "replace_parent": False},
                ),
                lambda: self._parent(number) == parent,
            )
        elif operation.op == "blocked_by":
            blocker = self._number(operation.target or "")
            if blocker in self._blockers(number):
                return
            blocker_id = self._database_id(blocker)

            def send_dependency() -> Any:
                try:
                    return gh.write(
                        "POST", f"{gh.prefix}/issues/{number}/dependencies/blocked_by", {"issue_id": blocker_id}
                    )
                except GithubError as error:
                    if error.status == 422 and blocker in self._blockers(number):
                        return None
                    raise

            self._write(
                "blocked_by",
                {"number": number, "blocker": blocker, "blocker_id": blocker_id},
                send_dependency,
                lambda: blocker in self._blockers(number),
            )

    def _issue(self, number: int) -> dict[str, Any]:
        body = self.gh.read(f"{self.gh.prefix}/issues/{number}").body
        body = dict(body) if isinstance(body, dict) else {}
        body["labels_names"] = [item.get("name") for item in body.get("labels") or [] if isinstance(item, dict)]
        return body

    def _parent(self, number: int) -> int | None:
        response = self.gh.read(f"{self.gh.prefix}/issues/{number}/parent", ok=(200, 404))
        return int(response.body["number"]) if response.status == 200 else None

    def _blockers(self, number: int) -> list[int]:
        return [
            int(item["number"])
            for item in _rest_pages(self.gh, f"{self.gh.prefix}/issues/{number}/dependencies/blocked_by")
        ]

    def _pending_creation(self, scope: Scope) -> dict[str, Any] | None:
        """The oldest creation intent for this Scope without a recorded outcome (a run stopped after sending it)."""
        records = self.state.undo_records()
        finished = {record.get("ref") for record in records if record.get("phase") == "done"}
        pending = [
            record
            for record in records
            if record.get("phase") == "intent"
            and record.get("op") == "issue.create"
            and record.get("local_id") == scope.id
            and record["seq"] not in finished
        ]
        return pending[0] if pending else None

    def _recorded_creation(self, scope: Scope) -> dict[str, Any] | None:
        """A creation whose outcome undo.jsonl holds but idmap.json may lack (a run stopped between the two)."""
        records = self.state.undo_records()
        undone = {record.get("ref") for record in records if record.get("phase") == "undone"}
        done = [
            record
            for record in records
            if record.get("phase") == "done"
            and record.get("op") == "issue.create"
            and record.get("local_id") == scope.id
            and isinstance(record.get("number"), int)
            and (record.get("ref") or record["seq"]) not in undone
        ]
        return done[-1] if done else None

    def _find_created(self, scope: Scope, since: str) -> Facts | None:
        """The Issue a creation intent made: same kind label and title, created by this gh user at or after it."""
        used = {n for n in self.analysis.numbers.values() if n is not None}
        found = created_issues(self.gh, KIND_LABELS[scope.kind], scope.title, since, exclude=used)
        if len(found) > 1:
            raise _ambiguous_creation(found, self.wrote > 0, "register --apply")
        return found[0] if found else None

    def _create(self, scope: Scope) -> None:
        label = KIND_LABELS[scope.kind]
        details = {"local_id": scope.id, "title": scope.title, "label": label}
        recorded = self._recorded_creation(scope)
        pending = self._pending_creation(scope) if recorded is None else None
        found = self._find_created(scope, pending["at"]) if pending is not None else None
        if recorded is not None:
            number = int(recorded["number"])
            database_id = int(recorded.get("database_id") or self._database_id(number))
        elif found is None:
            intent = self._record("intent", "issue.create", **details)
            try:
                response = self.gh.write("POST", f"{self.gh.prefix}/issues", {"title": scope.title, "labels": [label]})
                number, database_id = int(response.body["number"]), int(response.body["id"])
            except GithubError as error:
                found = self._find_created(scope, intent["at"]) if error.unknown else None
                if found is None:
                    raise
                number, database_id = found.number, found.database_id
            self.wrote += 1
            self._record("done", "issue.create", ref=intent["seq"], number=number, database_id=database_id, **details)
        else:
            number, database_id = found.number, found.database_id
            self._record(
                "done",
                "issue.create",
                ref=pending["seq"],  # type: ignore[index]
                number=number,
                database_id=database_id,
                recovered=True,
                **details,
            )
        new_id = scope_id(scope.kind, number)
        self.ids[number] = database_id
        self.analysis.numbers[scope.id] = number
        self.analysis.new_ids[scope.id] = new_id
        self.state.idmap[scope.id] = {"id": new_id, "number": number, "how": "created"}
        self.state.save_idmap()
        self.report.say(f"created #{number} for {scope.id} -> {new_id}")


# ---------------------------------------------------------------------------------------------------------------
# Repository observations for plan.
# ---------------------------------------------------------------------------------------------------------------


def ci_steps(cwd: Path, commit: str) -> list[dict[str, Any]]:
    completed = run_git(
        cwd, "grep", "-n", "-I", "-i", "-E", "spec-?dock", commit, "--", ".github", read_only=True, ok=(0, 1)
    )
    steps = []
    for line in completed.stdout.decode("utf-8", errors="replace").splitlines():
        _, _, rest = line.partition(":")
        path, _, rest = rest.partition(":")
        number, _, text = rest.partition(":")
        steps.append({"path": path, "line": int(number), "text": text.strip()})
    return steps


@dataclass
class Worktree:
    path: Path
    head: str | None
    branch: str | None
    prunable: bool


def list_worktrees(project: Path) -> list[Worktree]:
    output = git_text(project, "worktree", "list", "--porcelain")
    items: list[Worktree] = []
    current: dict[str, str] = {}
    for line in [*output.splitlines(), ""]:
        if not line:
            if current:
                items.append(
                    Worktree(
                        Path(current["worktree"]),
                        current.get("HEAD"),
                        current.get("branch", "").removeprefix("refs/heads/") or None,
                        "prunable" in current,
                    )
                )
            current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return items


def spec_changes(worktree: Path, default_ref: str) -> dict[str, list[str]]:
    committed = git_text(worktree, "diff", "--name-only", f"{default_ref}...HEAD", "--", SPEC_ROOT, ok=(0, 128))
    status = run_git(
        worktree, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", SPEC_ROOT, read_only=True
    ).stdout
    uncommitted = [record[3:].decode("utf-8", "replace") for record in status.split(b"\0") if len(record) > 3]
    return {"committed": [p for p in committed.splitlines() if p], "uncommitted": uncommitted}


def local_files(checkout: Path) -> list[str]:
    """Untracked and ignored files under spec-dock/initiatives (what move-local moves)."""
    root = checkout / SPEC_ROOT
    if root.is_symlink() or not root.is_dir():
        return []
    output = run_git(checkout, "ls-files", "-z", "--others", "--", SPEC_ROOT, read_only=True).stdout
    return [path.decode("utf-8", "surrogateescape") for path in output.split(b"\0") if path]


# ---------------------------------------------------------------------------------------------------------------
# Subcommands.
# ---------------------------------------------------------------------------------------------------------------


@dataclass
class Context:
    args: argparse.Namespace
    report: Report
    runner: Callable[..., Any] | None
    clock: Any
    wrote: bool = False  # this run changed the repository, its .git or origin
    githubs: list[Github] = field(default_factory=list)

    def has_written(self) -> bool:
        return self.wrote or any(gh.write_count for gh in self.githubs)

    def target(self) -> Target:
        if not _git_version(MINIMUM_GIT):
            raise Refused(
                f"migrate.py needs git {MINIMUM_GIT[0]}.{MINIMUM_GIT[1]} or newer (rev-parse --path-format)",
                "Install a newer Git (README), then run again",
            )
        target = resolve_target(self.args.project, self.args.repo, self.args.state_dir)
        self.report.repository = target.repository
        self.report.default_branch = target.default_branch
        return target

    def github(self, target: Target) -> Github:
        gh = Github(target.owner, target.name, runner=self.runner, clock=self.clock)
        self.githubs.append(gh)
        return gh


def _summarize(report: Report, analysis: Analysis) -> None:
    kinds: dict[str, int] = {}
    for scope in analysis.scopes:
        kinds[scope.kind] = kinds.get(scope.kind, 0) + 1
    dependencies = sum(len(scope.depends_on) for scope in analysis.scopes)
    report.data["scopes"] = {"total": len(analysis.scopes), **kinds, "dependencies": dependencies}
    report.data["local_scopes"] = analysis.local_plan
    report.anomalies.extend(analysis.problems)
    report.say(f"scopes: {len(analysis.scopes)} {kinds}, dependencies: {dependencies}")


def _analysis(context: Context, target: Target, state: State, commit: str) -> tuple[Github, Analysis]:
    scopes, problems = load_scopes(target.project, commit)
    gh = context.github(target)
    try:
        analysis = analyze(gh, scopes, problems, state)
    except GithubError as error:
        raise Refused(f"GitHub read failed: {error}", "Check gh auth status and the network, then run again") from error
    return gh, analysis


def _report_flattening(report: Report, flat: Flattened, links: LinkReport) -> None:
    report.data["flatten"] = {
        "problems": flat.problems,
        "pending": flat.layout.pending,
        "links": links.as_data(),
    }
    report.say(
        f"flatten: {len(flat.entries)} files, {len(flat.problems)} paths cannot be flattened, "
        f"{links.rewritten} links rewritten, {len(links.unrewritable)} unrewritable, "
        f"{len(links.broken_before)} already broken"
    )
    for item in links.unrewritable:
        report.warn(f"link {item['text']!r} in {item['file']} will not open {item['target']} after flattening")


def command_plan(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    commit = legacy_commit(target, state) or source_commit(target)
    report.data["source_commit"] = commit
    gh, analysis = _analysis(context, target, state, commit)
    _summarize(report, analysis)
    planned_ids = {
        old: {"id": entry["id"]} if entry.get("id") else {"relative": f"pending/{old}"}
        for old, entry in analysis.local_plan.items()
    }
    flat = Flattened([], [], {}, [], Layout({}, {}, {}))
    links = LinkReport()
    if tree_oid(target.project, f"{commit}:{SPEC_ROOT}") is not None:
        flattener = TreeFlattener(target.project, planned_ids, scratch=None)  # reads only; writes no object
        flat = flattener.flatten(list_tree(target.project, f"{commit}:{SPEC_ROOT}"))
        links = flattened_links(list_tree(target.project, commit), flat)
    _report_flattening(report, flat, links)
    report.anomalies.extend(flat.problems)
    try:
        operations = registration_plan(gh, analysis) if not analysis.blocking else []
    except GithubError as error:
        raise Refused(f"GitHub read failed: {error}") from error
    counts: dict[str, int] = {}
    for operation in operations:
        counts[operation.op] = counts.get(operation.op, 0) + 1
    writes = sum(counts.values())
    minutes = max(writes * WRITE_INTERVAL / 60, writes / WRITES_PER_MINUTE, writes / WRITES_PER_HOUR * 60)
    report.data["registration"] = {"writes": writes, "by_operation": counts, "estimated_minutes": round(minutes, 1)}
    report.say(f"registration: {writes} writes {counts}, about {minutes:.0f} minutes")
    steps = ci_steps(target.project, source_commit(target))
    report.data["ci_steps"] = steps
    report.say(f"CI lines calling SpecDock: {len(steps)}")
    for step in steps:
        report.say(f"  {step['path']}:{step['line']}: {step['text']}")
    worktrees = []
    for worktree in list_worktrees(target.project):
        if worktree.path == target.project:
            continue
        item: dict[str, Any] = {"path": str(worktree.path), "branch": worktree.branch, "prunable": worktree.prunable}
        if worktree.branch == CANONICAL_BRANCH:
            item["catalog"] = True
        elif worktree.prunable or not worktree.path.is_dir():
            item["missing"] = True
        else:
            item["spec_changes"] = spec_changes(worktree.path, target.default_ref)
        worktrees.append(item)
        changes = item.get("spec_changes") or {}
        flag = (
            "prunable"
            if item.get("missing")
            else f"{len(changes.get('committed', []))} committed, {len(changes.get('uncommitted', []))} uncommitted spec changes"
        )
        report.say(f"worktree {worktree.path} [{worktree.branch}]: {flag}")
    report.data["worktrees"] = worktrees
    moving = local_files(target.project)
    report.data["main_local_files"] = len(moving)
    report.say(f"untracked or ignored files under {SPEC_ROOT} in the main checkout: {len(moving)}")
    stale = stale_default(target)
    if stale:
        report.warn(f"{stale}; run git fetch origin before writing")
    head = resolve_commit(target.project, "HEAD")
    if head != source_commit(target):
        report.warn(f"the main checkout HEAD {head} differs from origin/{target.default_branch}")
    if analysis.blocking:
        report.step("Fix the blocking anomalies with the schema-3 SpecDock commands, merge, and run plan again")
        return EXIT_PROBLEMS
    if flat.problems:
        report.step("Move or remove the paths that cannot be flattened (README), merge, and run plan again")
        return EXIT_PROBLEMS
    report.step("register --apply, then verify")
    return EXIT_OK


def command_register(context: Context) -> int:
    report = context.report
    target = context.target()
    if context.args.apply:
        require_fresh_default(target)
    state = State(target.state_dir, target.repository)
    commit = legacy_commit(target, state) or source_commit(target)
    gh, analysis = _analysis(context, target, state, commit)
    _summarize(report, analysis)
    if analysis.blocking:
        raise Refused("blocking anomalies in .meta.json", "Fix them with the schema-3 SpecDock commands and run again")
    try:
        plan = registration_plan(gh, analysis)
    except GithubError as error:
        raise Refused(f"GitHub read failed: {error}") from error
    report.data["operations"] = [operation.describe() for operation in plan]
    for operation in plan:
        report.say(f"{'write' if context.args.apply else 'would'}: {operation.describe()}")
    existing = {
        old: entry
        for old, entry in analysis.local_plan.items()
        if entry["how"] == "existing" and old not in state.idmap
    }
    if not context.args.apply:
        report.step("register --apply")
        return EXIT_OK
    for old, entry in existing.items():
        state.idmap[old] = {"id": entry["id"], "number": entry["number"], "how": "existing"}
    if existing:
        state.save_idmap()
    registrar = Registrar(gh, state, analysis, report)
    registrar.run(plan)
    report.data["writes"] = registrar.wrote
    report.step("verify")
    return EXIT_OK


def command_verify(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    commit = legacy_commit(target, state)
    if commit is None:
        raise Refused("no commit with schema-3 metadata was found")
    report.data["source_commit"] = commit
    stale = stale_default(target)
    if stale:
        report.warn(stale)
    _gh, analysis = _analysis(context, target, state, commit)
    report.data["scopes"] = len(analysis.scopes)
    mismatches: list[str] = []
    by_id = {scope.id: scope for scope in analysis.scopes}
    scope_numbers = analysis.scope_numbers()
    for scope in analysis.scopes:
        number = analysis.numbers.get(scope.id)
        own = analysis.facts.get(number) if number else None
        if own is None:
            mismatches.append(
                f"{scope.id}: no Issue registered" if number is None else f"{scope.id}: #{number} missing"
            )
            continue
        if own.kind_labels != [KIND_LABELS[scope.kind]]:
            mismatches.append(f"{scope.id}: #{number} kind labels {own.kind_labels}")
        parent = analysis.numbers.get(scope.parent_id) if scope.parent_id in by_id else None
        if own.parent_foreign or own.parent != parent:
            mismatches.append(f"{scope.id}: #{number} parent {own.parent_foreign or own.parent}, expected {parent}")
        expected = sorted(analysis.numbers[d] or 0 for d in scope.depends_on if d in by_id)
        actual = sorted(n for n in own.blocked_by if n in scope_numbers)
        if expected != actual:
            mismatches.append(f"{scope.id}: #{number} blocked by {actual}, expected {expected}")
        outside = [n for n in own.blocked_by if n not in scope_numbers] + own.blocked_foreign
        if outside:
            report.say(f"info: {scope.id} is also blocked by non-Scope Issues {outside}")
        if own.title != scope.title:
            report.warn(f"{scope.id}: title differs (.meta.json {scope.title!r}, GitHub {own.title!r}); GitHub is kept")
    known = {n for n in analysis.numbers.values() if n is not None}
    mismatches.extend(f"#{n} has a kind label but no .meta.json" for n in sorted(set(analysis.labeled) - known))
    paths = _canonical_paths(target)
    if paths is None:
        report.data["canonical_meta_json"] = "not checked (no spec-dock/canonical on origin and no local catalog)"
    else:
        metas = [path for path in paths if PurePosixPath(path).name == META_FILE]
        report.data["canonical_meta_json"] = metas
        if metas:
            mismatches.append(f"the canonical branch has .meta.json: {metas[:5]}")
        registered = {
            scope_id(scope.kind, number)
            for scope in analysis.scopes
            if (number := analysis.numbers.get(scope.id)) is not None
        }
        layout = canonical_layout_problems(paths, registered)
        report.data["canonical_layout"] = layout
        mismatches.extend(layout)
    report.data["mismatches"] = mismatches
    for item in mismatches:
        report.say(f"mismatch: {item}")
    if mismatches:
        report.step("register --apply for missing items; fix conflicts on GitHub by hand; run verify again")
        return EXIT_PROBLEMS
    report.say("GitHub matches the schema-3 structure")
    return EXIT_OK


def _canonical_paths(target: Target) -> list[str] | None:
    """Files of origin's canonical (read in a throwaway clone), else of the local catalog; None when neither exists."""
    if remote_ref(target, CANONICAL_REF) is not None:
        with Workspace(target) as workspace:
            commit = workspace.fetch_canonical()
            return [entry.path for entry in list_tree(workspace.repo, commit)] if commit else []
    catalog = target.project / CATALOG_RELATIVE
    if not catalog.is_dir():
        return None
    return sorted(
        path.relative_to(catalog).as_posix()
        for path in catalog.rglob("*")
        if (path.is_file() or path.is_symlink())
        and path.relative_to(catalog).parts[0] not in (".git", RUNTIME_DIRECTORY)
    )


def canonical_layout_problems(paths: Iterable[str], expected: Iterable[str]) -> list[str]:
    """Paths outside <bucket>/<ID>/ (or nested epics/, issues/) and expected Scopes without their directory."""
    problems: dict[str, str] = {}
    present: set[str] = set()
    for path in paths:
        if path in CANONICAL_ROOT_FILES:
            continue
        parts = path.split("/")
        place = "/".join(parts[:2])
        if len(parts) < 3 or CANONICAL_ID_RE.fullmatch(parts[1]) is None or scope_relative(parts[1]) != place:
            problems.setdefault(place, f"{place} in canonical is not a Scope's <bucket>/<ID>/")
        elif parts[2] in NESTED_DIRECTORIES and len(parts) > 3:
            problems.setdefault(f"{place}/{parts[2]}", f"{place}/{parts[2]} in canonical is a nested leftover")
        else:
            present.add(parts[1])
    for scope in sorted(set(expected) - present):
        problems.setdefault(scope, f"{scope}: canonical has no {scope_relative(scope)}/")
    return list(problems.values())


def command_undo(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    record_path = state.directory / "undo.jsonl"
    if not record_path.is_file():
        # A wrong or missing --state-dir would otherwise look like "nothing to undo" (iss-00436, I-8 ST-1).
        raise Refused(
            f"no work record at {record_path}",
            "Pass the same --state-dir that register used (default scripts/migrate-to-canonical/.state/)",
        )
    gh = context.github(target)
    records = state.undo_records()
    undone = {record["ref"] for record in records if record.get("phase") == "undone"}
    latest: dict[int, dict[str, Any]] = {}
    for record in records:
        if record.get("phase") == "intent":
            latest[record["seq"]] = record
        elif record.get("phase") == "done":
            key = record.get("ref") or record["seq"]
            latest[key] = record
    pending = [(seq, record) for seq, record in sorted(latest.items(), reverse=True) if seq not in undone]
    recorded = {
        record["number"]
        for record in records
        if record.get("op") == "issue.create"
        and record.get("phase") == "done"
        and isinstance(record.get("number"), int)
    }
    wrote = 0
    for seq, record in pending:
        op = record["op"]
        try:
            action = _undo_action(gh, record, recorded)
        except GithubError as error:
            raise (Stopped if wrote else Refused)(f"GitHub read failed: {error}", "Run undo again") from error
        if action is None:
            if context.args.apply:
                state.append_undo({"phase": "undone", "op": op, "ref": seq, "absent": True}, gh.clock)
            continue
        description, steps = action
        report.say(f"{'undo' if context.args.apply else 'would undo'}: {description}")
        if not context.args.apply:
            continue
        try:
            for method, endpoint, payload, ok in steps:
                gh.write(method, endpoint, payload, ok=ok)
                wrote += 1
        except GithubError as error:
            raise (Stopped if wrote else Refused)(f"{description}: {error}", "Run undo --apply again") from error
        state.append_undo({"phase": "undone", "op": op, "ref": seq}, gh.clock)
        if op == "issue.create":
            for old, entry in list(state.idmap.items()):
                if entry.get("how") == "created" and entry.get("number") == record.get("number"):
                    del state.idmap[old]
            state.save_idmap()
    if not context.args.apply:
        report.step("undo --apply")
    return EXIT_OK


Step = tuple[str, str, object, tuple[int, ...]]


def _undo_action(gh: Github, record: Mapping[str, Any], recorded: Iterable[int]) -> tuple[str, list[Step]] | None:
    """recorded: Issues another creation record already names; an unrecorded creation is never one of them."""
    op = record["op"]
    prefix = gh.prefix
    if op == "label.create":
        name = record["name"]
        if not label_exists(gh, name):
            return None
        return f"delete label {name}", [("DELETE", f"{prefix}/labels/{name}", None, (200, 204, 404))]
    if op == "issue.create":
        number = record.get("number")
        if not isinstance(number, int):
            number = _created_without_record(gh, record, recorded)
            if number is None:
                return None
        issue = gh.read(f"{prefix}/issues/{number}").body
        labels = [item["name"] for item in issue.get("labels") or []]
        steps: list[Step] = []
        if record["label"] in labels:
            steps.append(("DELETE", f"{prefix}/issues/{number}/labels/{record['label']}", None, (200, 204, 404)))
        if issue.get("state") != "closed":
            steps.append((
                "PATCH",
                f"{prefix}/issues/{number}",
                {"state": "closed", "state_reason": "not_planned"},
                (200,),
            ))
        return (f"close #{number} as not planned and remove its label", steps) if steps else None
    number = record.get("number") or record.get("child")
    if op == "issue.label":
        issue = gh.read(f"{prefix}/issues/{number}").body
        if record["label"] not in [item["name"] for item in issue.get("labels") or []]:
            return None
        return f"remove {record['label']} from #{number}", [
            ("DELETE", f"{prefix}/issues/{number}/labels/{record['label']}", None, (200, 204, 404))
        ]
    if op == "sub_issue":
        child, parent = record["child"], record["parent"]
        response = gh.read(f"{prefix}/issues/{child}/parent", ok=(200, 404))
        if response.status != 200 or int(response.body["number"]) != parent:
            return None
        return f"detach #{child} from #{parent}", [
            ("DELETE", f"{prefix}/issues/{parent}/sub_issue", {"sub_issue_id": record["child_id"]}, (200, 204))
        ]
    if op == "blocked_by":
        blockers = [
            int(item["number"]) for item in _rest_pages(gh, f"{prefix}/issues/{number}/dependencies/blocked_by")
        ]
        if record["blocker"] not in blockers:
            return None
        return f"remove #{record['blocker']} from the blockers of #{number}", [
            ("DELETE", f"{prefix}/issues/{number}/dependencies/blocked_by/{record['blocker_id']}", None, (200, 204))
        ]
    return None


def _created_without_record(gh: Github, record: Mapping[str, Any], recorded: Iterable[int]) -> int | None:
    """The open Issue an interrupted register created, found as register finds it."""
    title, since = str(record.get("title") or ""), str(record.get("at") or "")
    found = [
        facts for facts in created_issues(gh, record["label"], title, since, exclude=recorded) if facts.state == "open"
    ]
    if len(found) > 1:
        raise _ambiguous_creation(found, False, "undo --apply")
    return found[0].number if found else None


def created_issues(gh: Github, label: str, title: str, since: str, *, exclude: Iterable[int] = ()) -> list[Facts]:
    """Issues with the kind label and title that the current gh user created since the intent (Epic ch. 11)."""
    login = gh.login()
    skipped = set(exclude)
    return [
        facts
        for number, facts in sorted(fetch_labeled(gh).items())
        if number not in skipped
        and label in facts.labels
        and facts.title == title
        and facts.author == login
        and _not_before(facts.created_at, since)
    ]


def _not_before(moment: str, since: str) -> bool:
    """`moment` is no earlier than `since` less the allowance for the local and GitHub clocks."""
    try:
        return _parse_time(moment) >= _parse_time(since) - CLOCK_ALLOWANCE
    except ValueError:
        return False


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _ambiguous_creation(found: Sequence[Facts], wrote: bool, command: str) -> MigrationError:
    numbers = ", ".join(f"#{facts.number}" for facts in found)
    return (Stopped if wrote else Refused)(
        f"{len(found)} Issues match the interrupted creation ({numbers}); none is used and none is created",
        f"Keep one of {numbers}: remove the kind label from the others (or close them as not planned), "
        f"then run the same {command} again",
    )


# --- throwaway clones ------------------------------------------------------------------------------------------


class Workspace:
    """A temporary clone of the project with its default branch commit as refs/heads/migrate-source."""

    def __init__(self, target: Target) -> None:
        self.target = target
        self.root = Path(tempfile.mkdtemp(prefix="spec-dock-migrate-"))
        self.repo = self.root / "repo"

    def __enter__(self) -> Workspace:
        try:
            self._prepare()
        except BaseException:
            shutil.rmtree(self.root, ignore_errors=True)
            raise
        return self

    def _prepare(self) -> None:
        run_git(
            None,
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--no-checkout",
            "--origin",
            "source",
            str(self.target.project),
            str(self.repo),
        )
        run_git(self.repo, "config", "gc.auto", "0")
        run_git(
            self.repo,
            "fetch",
            "--quiet",
            "--no-tags",
            "source",
            f"+{self.target.default_ref}:refs/heads/migrate-source",
        )

    def __exit__(self, *exc: object) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def fetch_canonical(self) -> str | None:
        completed = run_git(
            self.repo,
            "fetch",
            "--quiet",
            "--no-tags",
            self.target.origin_url,
            f"+{CANONICAL_REF}:refs/heads/canonical",
            ok=(0, 1, 128),
        )
        if completed.returncode != 0:
            if remote_ref(self.target, CANONICAL_REF) is None:
                return None
            raise GitError(("fetch", "canonical"), completed.returncode, completed.stderr)
        return resolve_commit(self.repo, "refs/heads/canonical")

    def push(self, commit: str, ref: str) -> str:
        """Push without force: 'pushed', 'unchanged' or 'rejected'."""
        current = remote_ref(self.target, ref)
        if current == commit:
            return "unchanged"
        completed = run_git(self.repo, "push", "--quiet", self.target.origin_url, f"{commit}:{ref}", ok=(0, 1))
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", "replace")
            if "rejected" in detail or "non-fast-forward" in detail or "fetch first" in detail:
                return "rejected"
            raise GitError(("push", ref), completed.returncode, completed.stderr)
        return "pushed"


def _existing_ref_refusal(ref: str, current: str, commit: str) -> Refused:
    return Refused(
        f"origin {ref} already points at {current}, not the expected {commit}; nothing is forced",
        "Inspect that branch; delete it on GitHub only if it is a stale migration attempt, then run again",
    )


def command_build_canonical(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    if context.args.apply:
        require_fresh_default(target)
    source = source_commit(target)
    scopes, problems = load_scopes(target.project, source)
    report.data["source_commit"] = source
    if not tracked_spec_files(target.project, source):
        report.say(f"{SPEC_ROOT} has no tracked file in origin/{target.default_branch}; nothing to build")
        report.step("After the cutover merge, move-local and spec-dock canonical link create the first canonical")
        return EXIT_OK
    numbers = {
        scope.id: (state.idmap[scope.id]["number"] if scope.id in state.idmap else None)
        if scope.local
        else scope.number
        for scope in scopes
    }
    blocking = [item for item in [*problems, *metadata_problems(scopes, numbers)] if item["blocking"]]
    if blocking:
        report.anomalies.extend(blocking)
        raise Refused("blocking anomalies in .meta.json", "Run plan and fix them first")
    unmapped = [scope.id for scope in scopes if scope.local and scope.id not in state.idmap]
    if unmapped:
        raise Refused(f"local Scopes without an ID map entry: {unmapped}", "register --apply")
    if run_git(None, "subtree", "-h", ok=(0, 1, 129)).returncode not in (0, 129):
        raise Refused("git subtree is not available", "Install a Git that ships git-subtree")
    current = remote_ref(target, CANONICAL_REF)
    with Workspace(target) as workspace:
        repo = workspace.repo
        flattener = TreeFlattener(repo, state.idmap, workspace.root)
        whole = list_tree(repo, "migrate-source")
        tip = flattener.flatten(list_tree(repo, f"migrate-source:{SPEC_ROOT}"))
        links = flattened_links(whole, tip)
        _report_flattening(report, tip, links)
        if tip.problems:
            report.anomalies.extend(tip.problems)
            raise Refused(
                f"{len(tip.problems)} paths of {SPEC_ROOT} cannot be flattened; nothing was pushed",
                "Fix them with the schema-3 SpecDock commands (README), merge, and run plan again",
            )
        # git-subtree of git 2.39 and older knows only -q, and that of 2.43 (Ubuntu 24.04) wants the prefix in the
        # work tree even for a split; this clone has no checkout, so an empty directory stands in for it.
        (repo / SPEC_ROOT).mkdir(parents=True, exist_ok=True)
        split = git_text(repo, "subtree", "split", "-q", f"--prefix={SPEC_ROOT}", "migrate-source", read_only=False)
        split = split.splitlines()[-1].strip()
        history = rewrite_history(repo, split, flattener, workspace.root)
        report.data["history"] = history.as_data()
        report.say(
            f"history: {history.commits} commits rewritten; {history.dropped_commits} left out paths that cannot be "
            f"flattened {history.dropped} (they stay in the default branch history)"
        )
        expected = write_tree(repo, tip.entries, workspace.root)
        if tree_oid(repo, history.tip) != expected:
            raise Refused("the rewritten history does not end in the flattened spec tree; nothing was pushed")
        entries = [*tip.entries]
        for name, payload in CANONICAL_ROOT_FILES.items():
            entries.append(TreeEntry("100644", "blob", hash_blob(repo, payload), name))
        tree = write_tree(repo, entries, workspace.root)
        commit = commit_tree(
            repo,
            tree,
            [history.tip],
            CANONICAL_COMMIT_MESSAGE,
            committer(repo, split),  # same inputs give the same commit after unrelated default-branch PRs
            commit_date(repo, split),
        )
        report.data.update({
            "split_commit": split,
            "flat_commit": history.tip,
            "canonical_commit": commit,
            "files": len(entries),
        })
        report.say(f"canonical commit {commit} ({len(entries)} files) on top of the flattened history {history.tip}")
        if current is not None and current != commit:
            raise _existing_ref_refusal(CANONICAL_REF, current, commit)
        if not context.args.apply:
            report.say("would push it to origin " + CANONICAL_BRANCH if current is None else "origin already has it")
            report.step("build-canonical --apply")
            return EXIT_OK
        context.wrote = True
        outcome = workspace.push(commit, CANONICAL_REF)
        if outcome == "rejected":
            raise Refused("origin rejected the canonical branch push", "Inspect origin spec-dock/canonical")
        report.say(f"origin {CANONICAL_BRANCH}: {outcome}")
    state.save_build({
        "source_commit": source,
        "source_tree": tree_oid(target.project, f"{source}:{SPEC_ROOT}"),
        "split_commit": split,
        "canonical_commit": commit,
    })
    report.step("cut --apply")
    return EXIT_OK


def _blob(cwd: Path, commit: str, path: str) -> bytes | None:
    completed = run_git(cwd, "cat-file", "blob", f"{commit}:{path}", read_only=True, ok=(0, 128))
    return completed.stdout if completed.returncode == 0 else None


def command_cut(context: Context) -> int:
    report = context.report
    target = context.target()
    branch = context.args.branch
    state = State(target.state_dir, target.repository)
    if context.args.apply:
        require_fresh_default(target)
    source = source_commit(target)
    report.data["source_commit"] = source
    if run_git(None, "check-ref-format", "--branch", branch, ok=(0, 1, 128)).returncode != 0:
        raise Refused(f"invalid branch name {branch}")
    if WORKFLOW_BRANCH_NAME_RE.fullmatch(target.default_branch) is None:
        raise Refused(f"the default branch name {target.default_branch!r} cannot go into the workflow sample")
    declaration = _blob(target.project, source, "spec-dock/workspace.json")
    try:
        schema = json.loads(declaration or b"null").get("schema_version")
    except (AttributeError, json.JSONDecodeError):
        schema = None
    if schema != 3:
        raise Refused(f"origin/{target.default_branch} does not declare workspace schema 3 (found {schema!r})")
    gitignore = _blob(target.project, source, GITIGNORE_PATH)
    if _blob(target.project, source, CI_VERSION_FILE) is None or not ignore_rules_effective(
        (gitignore or b"").decode("utf-8", "replace")
    ):
        raise Refused(
            "the default branch lacks the SpecDock 0.3.0 static files (version file and the three ignore lines)",
            "Merge a PR made with spec-dock installation update (0.3.0) first",
        )
    if tracked_spec_files(target.project, source):
        if remote_ref(target, CANONICAL_REF) is None:
            raise Refused("origin has no spec-dock/canonical yet", "build-canonical --apply")
        built = state.build.get("source_tree")
        if built != tree_oid(target.project, f"{source}:{SPEC_ROOT}"):
            raise Refused(
                "the spec tree changed since build-canonical (or build.json is missing in this state directory)",
                "Run build-canonical again; changes made after the canonical exists go in later with adopt-worktree",
            )
    workflow = WORKFLOW_SAMPLE_BYTES.replace(
        WORKFLOW_BRANCH_LINE.encode(), f"branches: [{target.default_branch}]".encode(), 1
    )
    current = remote_ref(target, f"refs/heads/{branch}")
    with Workspace(target) as workspace:
        entries = [
            e
            for e in list_tree(workspace.repo, source)
            if e.path != SPEC_ROOT
            and not e.path.startswith(SPEC_ROOT + "/")
            and e.path not in ("spec-dock/workspace.json", WORKFLOW_DESTINATION)
        ]
        entries.append(
            TreeEntry("100644", "blob", hash_blob(workspace.repo, WORKSPACE_V4_BYTES), "spec-dock/workspace.json")
        )
        entries.append(TreeEntry("100644", "blob", hash_blob(workspace.repo, workflow), WORKFLOW_DESTINATION))
        others = [
            e.path for e in entries if e.path.startswith("spec-dock/") and PurePosixPath(e.path).name == META_FILE
        ]
        if others:
            report.warn(f"other .meta.json files stay under spec-dock/ and fail canonical check: {others}")
        tree = write_tree(workspace.repo, entries, workspace.root)
        commit = commit_tree(
            workspace.repo, tree, [source], CUT_COMMIT_MESSAGE, target.identity, commit_date(target.project, source)
        )
        report.data.update({"branch": branch, "commit": commit})
        report.say(f"cut commit {commit} for branch {branch}")
        if current is not None and current != commit:
            raise _existing_ref_refusal(f"refs/heads/{branch}", current, commit)
        steps = ci_steps(target.project, source)
        report.data["ci_steps"] = steps
        for step in steps:
            report.say(f"remove by hand if it calls SpecDock: {step['path']}:{step['line']}: {step['text']}")
        if not context.args.apply:
            report.step("cut --apply")
            return EXIT_OK
        context.wrote = True
        outcome = workspace.push(commit, f"refs/heads/{branch}")
        if outcome == "rejected":
            raise Refused(f"origin rejected {branch}")
        report.say(f"origin {branch}: {outcome}")
    report.step(f"Add a commit removing the current CI SpecDock steps to {branch}, open the PR and wait for its checks")
    return EXIT_OK


# --- move-local ----------------------------------------------------------------------------------------------


def _checkout(target: Target, value: str) -> Path:
    checkout = Path(value).expanduser().resolve()
    try:
        common = Path(git_text(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
        top = Path(git_text(checkout, "rev-parse", "--show-toplevel")).resolve()
    except GitError as error:
        raise Refused(f"{checkout} is not a Git checkout") from error
    if common != target.common_dir or top != checkout:
        raise Refused(f"{checkout} is not the top of a checkout of {target.project}")
    return checkout


def _catalog_registered(target: Target) -> bool:
    catalog = target.project / CATALOG_RELATIVE
    return (
        any(
            item.path.resolve() == catalog.resolve() and item.branch == CANONICAL_BRANCH
            for item in list_worktrees(target.project)
        )
        if catalog.exists()
        else False
    )


def create_catalog(target: Target) -> None:
    """canonical link step 3 for an existing remote canonical, with the C6 settings."""
    project = target.project
    catalog = project / CATALOG_RELATIVE
    if remote_ref(target, CANONICAL_REF) is None:
        raise Refused("origin has no spec-dock/canonical to hold the files", "build-canonical --apply first")
    fetches = run_git(project, "config", "--get-all", "remote.origin.fetch", read_only=True, ok=(0, 1)).stdout.decode()
    covered = any(
        refspec.strip().lstrip("+").partition(":")[0] in (CANONICAL_REF, "refs/heads/*")
        for refspec in fetches.splitlines()
    )
    if not covered:
        run_git(project, "remote", "set-branches", "--add", "origin", CANONICAL_BRANCH, hookless=True)
    run_git(
        project,
        "fetch",
        "--quiet",
        "--no-tags",
        "--no-recurse-submodules",
        "origin",
        f"+{CANONICAL_REF}:{CANONICAL_TRACKING_REF}",
        hookless=True,
    )
    local = resolve_commit(project, CANONICAL_REF)
    if local is not None:
        ahead = run_git(
            project, "merge-base", "--is-ancestor", local, CANONICAL_TRACKING_REF, read_only=True, ok=(0, 1)
        )
        if ahead.returncode != 0:
            raise Refused(
                f"the local {CANONICAL_BRANCH} ({local}) is not contained in origin's; it would bring back other content",
                f"Inspect git -C {project} log {CANONICAL_BRANCH}, then delete or push it by hand",
            )
    if local is None:
        run_git(
            project,
            "worktree",
            "add",
            "--quiet",
            "--track",
            "-b",
            CANONICAL_BRANCH,
            str(catalog),
            f"origin/{CANONICAL_BRANCH}",
            hookless=True,
        )
    else:
        run_git(project, "worktree", "add", "--quiet", str(catalog), CANONICAL_BRANCH, hookless=True)
    run_git(project, "worktree", "lock", "--reason", CATALOG_LOCK_REASON, str(catalog), hookless=True)


def _free_name(directory: Path, name: str, tag: str, planned: set[Path]) -> Path:
    def taken(candidate: str) -> bool:
        path = directory / candidate
        return path.exists() or path.is_symlink() or path in planned

    if not taken(name):
        return directory / name
    return directory / alternate_name(name, tag, taken)


def command_move_local(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    checkout = _checkout(target, context.args.checkout)
    root = checkout / SPEC_ROOT
    if root.is_symlink() or not root.exists():
        report.say(f"{root} is {'a link' if root.is_symlink() else 'absent'}; nothing to move")
        return EXIT_OK
    tracked = git_text(checkout, "ls-files", "--", SPEC_ROOT)
    if tracked:
        raise Refused(
            f"{SPEC_ROOT} still has tracked files in {checkout}",
            "Merge the default branch (the cutover) into this checkout first",
        )
    files = sorted(path for path in root.rglob("*") if path.is_symlink() or path.is_file())
    metadata = [str(path) for path in files if path.name == META_FILE]
    if metadata:
        raise Refused(
            f"schema-3 metadata must not enter the catalog: {metadata}",
            "Register those Scopes with SpecDock commands or remove the files, then run move-local again",
        )
    directories = sorted(
        (p for p in root.rglob("*") if p.is_dir() and not p.is_symlink()), key=lambda p: len(p.parts), reverse=True
    )
    catalog = target.project / CATALOG_RELATIVE
    tag = f"local-{pc_name(context.args.pc_name)}"
    placements = _place_local_files(target, state, checkout, files) if files else []

    def plan_moves() -> list[tuple[Path, Path, bytes | None]]:
        planned: set[Path] = set()
        moves: list[tuple[Path, Path, bytes | None]] = []
        for path, place, content in placements:
            destination = catalog / place
            destination = _free_name(destination.parent, destination.name, tag, planned)
            planned.add(destination)
            moves.append((path, destination, content))
        return moves

    needs_catalog = bool(files) and not _catalog_registered(target)
    if needs_catalog and (catalog.exists() or catalog.is_symlink()):
        raise Refused(f"{catalog} exists but is not the catalog worktree")
    if needs_catalog and context.args.apply:
        context.wrote = True
        try:
            create_catalog(target)
        except GitError as error:
            raise Refused(f"could not create the catalog: {error}") from error
        report.say(f"created the catalog {catalog}")
    elif needs_catalog:
        remote = remote_ref(target, CANONICAL_REF)
        if remote is None:
            raise Refused("origin has no spec-dock/canonical to hold the files", "build-canonical --apply first")
        local = resolve_commit(target.project, CANONICAL_REF)
        if local is not None and local != remote:
            known = resolve_commit(target.project, remote) is not None
            ahead = (
                known
                and run_git(
                    target.project, "merge-base", "--is-ancestor", local, remote, read_only=True, ok=(0, 1)
                ).returncode
                == 0
            )
            if not ahead:
                report.warn(
                    f"the local {CANONICAL_BRANCH} must be contained in origin's; --apply checks it after fetching"
                )
        report.say(f"would create the catalog {catalog}; names are checked against it once it exists")
    moves = plan_moves()
    report.data["moves"] = [{"from": str(a), "to": str(b), "links_rewritten": c is not None} for a, b, c in moves]
    report.data["directories"] = [str(d) for d in [*directories, root]]
    report.data["create_catalog"] = needs_catalog
    for source, destination, _content in moves:
        report.say(f"{'move' if context.args.apply else 'would move'} {source} -> {destination}")
    if not context.args.apply:
        report.step("move-local --apply")
        return EXIT_OK
    moved = 0
    context.wrote = True
    try:
        for source, destination, content in moves:
            if destination.exists() or destination.is_symlink():
                raise Stopped(f"{destination} appeared while moving; nothing is overwritten", "Run move-local again")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if content is not None:  # its relative links follow the new depth
                if source.is_symlink():
                    destination.symlink_to(os.fsdecode(content))
                else:
                    destination.write_bytes(content)
                    shutil.copymode(source, destination)
                source.unlink()
                moved += 1
                continue
            try:
                source.rename(destination)
            except OSError:
                if source.is_symlink():
                    destination.symlink_to(source.readlink())
                    source.unlink()
                else:
                    shutil.copy2(source, destination)
                    source.unlink()
            moved += 1
    except OSError as error:
        raise (Stopped if moved else Refused)(f"move failed: {error}", "Run move-local again") from error
    for directory in [*directories, root]:
        with contextlib.suppress(OSError):
            directory.rmdir()
    if root.exists():
        raise Stopped(f"{root} is not empty after moving", "Inspect it and run move-local again")
    report.step(f"spec-dock --project {checkout} canonical link")
    return EXIT_OK


def _place_local_files(
    target: Target, state: State, checkout: Path, files: Sequence[Path]
) -> list[tuple[Path, str, bytes | None]]:
    """(file, catalog path, rewritten content or None) for each file; refuses before writing if one has no place."""
    commit = legacy_commit(target, state)
    entries = tracked_spec_files(target.project, commit) if commit else []
    wanted = [e for e in entries if e.mode == "120000" or PurePosixPath(e.path).name == META_FILE]
    blobs = read_blobs(target.project, [e.oid for e in wanted])
    metas = {str(PurePosixPath(e.path).parent): blobs[e.oid] for e in wanted if e.path.endswith(f"/{META_FILE}")}
    branch = git_text(checkout, "symbolic-ref", "--quiet", "--short", "HEAD", ok=(0, 1))
    record = state.directory / "adopt" / f"{branch.replace('/', '-')}.json"
    if branch and record.exists():
        for path, text in (json.loads(record.read_text(encoding="utf-8")).get("metadata") or {}).items():
            directory, payload = str(PurePosixPath(path).parent), str(text).encode("utf-8")
            if directory in metas and _identity(metas[directory]) != _identity(payload):
                raise Refused(
                    f"{directory}: the cutover commit and the adopt-worktree record of {branch} name different Scopes",
                    "Inspect both .meta.json versions; fix the record or move the files by hand (README)",
                )
            metas[directory] = payload
    flat = FlatMap(nested_layout(metas, state.idmap))
    target_of = link_target(flat, {e.path: blobs[e.oid] for e in wanted if e.mode == "120000"})
    root = checkout / SPEC_ROOT
    placements: list[tuple[Path, str, bytes | None]] = []
    problems: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        place = flat.file(relative)
        if isinstance(place, dict):
            problems.append(place)
            continue
        if place == DROPPED:
            problems.append(anomaly(FLATTEN_NESTED_FILE, f"{relative} has no place in the catalog", path=relative))
            continue
        kind = linkable(relative, "120000" if path.is_symlink() else "100644")
        content = None
        if kind is not None:
            payload = os.fsencode(str(path.readlink())) if kind == "symlink" else path.read_bytes()
            rewritten, _ = rewrite_links(
                payload, kind=kind, old=f"{SPEC_ROOT}/{relative}", new=f"{SPEC_ROOT}/{place}", target=target_of
            )
            content = rewritten if rewritten != payload else None
        placements.append((path, place, content))
    if problems:
        raise Refused(
            f"{len(problems)} files have no place in the flat catalog; nothing was moved: "
            + ", ".join(str(item.get("path")) for item in problems[:10]),
            "Move them into a Scope directory or delete them, then run move-local again",
        )
    return placements


# --- adopt-worktree ----------------------------------------------------------------------------------------------


def _worktree_entries(repo: Path, checkout: Path, paths: Iterable[str]) -> list[TreeEntry]:
    entries = []
    regular: list[tuple[str, Path, str]] = []
    for relative in paths:
        absolute = checkout / relative
        if absolute.is_symlink():
            oid = hash_blob(repo, os.fsencode(str(absolute.readlink())))
            entries.append(TreeEntry("120000", "blob", oid, relative))
        elif absolute.is_file():
            mode = "100755" if os.access(absolute, os.X_OK) else "100644"
            regular.append((relative, absolute, mode))
    if regular:
        output = git_text(
            repo,
            "hash-object",
            "-w",
            "--no-filters",
            "--stdin-paths",
            input="".join(f"{absolute}\n" for _, absolute, _ in regular).encode(),
            read_only=False,
        )
        for (relative, _, mode), oid in zip(regular, output.splitlines(), strict=True):
            entries.append(TreeEntry(mode, "blob", oid, relative))
    return entries


def _merge(
    repo: Path, base: str, ours: str, theirs: str, pc: str, now: datetime, scratch: Path
) -> tuple[str, list[dict[str, str]]]:
    """merge-tree X (stage 2) with canonical R (stage 3); R keeps the path, X goes to a conflict-named file."""
    completed = run_git(repo, "merge-tree", "--write-tree", "-z", f"--merge-base={base}", ours, theirs, ok=(0, 1))
    parts = completed.stdout.split(b"\0")
    merged = parts[0].decode()
    if completed.returncode == 0:
        return merged, []
    stages: dict[str, dict[int, tuple[str, str]]] = {}
    for record in parts[1:]:
        if not record:
            break
        header, _, raw_path = record.partition(b"\t")
        mode, oid, stage = header.decode().split(" ")
        stages.setdefault(raw_path.decode("utf-8", "surrogateescape"), {})[int(stage)] = (mode, oid)
    entries = {e.path: e for e in list_tree(repo, merged)}
    names = set(entries)
    conflicts: list[dict[str, str]] = []
    tag = conflict_tag(pc, now)
    for path, found in stages.items():
        entries.pop(path, None)
        if 3 in found:
            entries[path] = TreeEntry(found[3][0], "blob", found[3][1], path)
        if 2 in found:
            if 3 in found:
                directory, _, name = path.rpartition("/")

                def taken(candidate: str, folder: str = directory) -> bool:
                    return (f"{folder}/{candidate}" if folder else candidate) in names

                alias = alternate_name(name, tag, taken)
                alias_path = f"{directory}/{alias}" if directory else alias
                names.add(alias_path)
                entries[alias_path] = TreeEntry(found[2][0], "blob", found[2][1], alias_path)
                conflicts.append({"path": path, "copy": alias_path})
            else:
                entries[path] = TreeEntry(found[2][0], "blob", found[2][1], path)
    return write_tree(repo, entries.values(), scratch), conflicts


def _meta_differences(before: list[Scope], after: list[Scope]) -> list[str]:
    old = {scope.id: scope for scope in before}
    new = {scope.id: scope for scope in after}
    lines = [f"added Scope {i}" for i in sorted(set(new) - set(old))]
    lines += [f"removed Scope {i}" for i in sorted(set(old) - set(new))]
    for scope_key in sorted(set(old) & set(new)):
        a, b = old[scope_key], new[scope_key]
        if a.title != b.title:
            lines.append(f"{scope_key}: title {a.title!r} -> {b.title!r}")
        if a.parent_id != b.parent_id:
            lines.append(f"{scope_key}: parent {a.parent_id} -> {b.parent_id}")
        if sorted(a.depends_on) != sorted(b.depends_on):
            lines.append(f"{scope_key}: depends_on {sorted(a.depends_on)} -> {sorted(b.depends_on)}")
    return lines


def _git_version(minimum: tuple[int, int]) -> bool:
    matched = re.match(r"git version (\d+)\.(\d+)", git_text(None, "--version"))
    return matched is not None and (int(matched.group(1)), int(matched.group(2))) >= minimum


def _find_tree_commit(repo: Path, ref: str, tree: str) -> str | None:
    candidate = None
    for line in git_text(repo, "rev-list", "--format=%T", ref).splitlines():
        if line.startswith("commit "):
            candidate = line.split(" ", 1)[1]
        elif line.strip() == tree:
            return candidate
    return None


def _adopt_into_canonical(
    context: Context,
    target: Target,
    workspace: Workspace,
    adopted: list[TreeEntry],
    base: str,
    flat_base_tree: str,
    branch: str,
) -> tuple[str, list[dict[str, str]]]:
    """Merge the checkout's flattened specs into canonical and push; returns the commit that must be on origin.

    The merge base C is the canonical commit whose tree is the flattened merge-base spec tree (build-canonical
    flattened every commit the same way).
    """
    repo, report = workspace.repo, context.report
    date = commit_date(repo, base)
    pc = pc_name(context.args.pc_name)
    for attempt in range(3):
        canonical = workspace.fetch_canonical()
        if canonical is None:
            raise Refused("origin has no spec-dock/canonical", "build-canonical --apply")
        found = _find_tree_commit(repo, "refs/heads/canonical", flat_base_tree)
        if found is None:
            raise Refused(f"no canonical commit has the flattened spec tree of the merge base {base}")
        identity = target.identity
        base_commit = found
        x_commit = commit_tree(
            repo, write_tree(repo, adopted, workspace.root), [found], f"spec-dock: adopt {branch}", identity, date
        )
        if run_git(repo, "merge-base", "--is-ancestor", x_commit, canonical, ok=(0, 1)).returncode == 0:
            report.say(f"{branch} is already in canonical")
            return canonical, []
        merged_tree, conflicts = _merge(repo, base_commit, x_commit, canonical, pc, context.clock.now(), workspace.root)
        y_commit = commit_tree(
            repo, merged_tree, [canonical, x_commit], f"spec-dock: merge {branch} into canonical", identity, date
        )
        for item in conflicts:
            report.say(f"conflict: canonical keeps {item['path']}; this branch's version goes to {item['copy']}")
        if not context.args.apply:
            return y_commit, conflicts
        context.wrote = True
        outcome = workspace.push(y_commit, CANONICAL_REF)
        if outcome != "rejected":
            report.say(f"origin {CANONICAL_BRANCH}: {outcome}")
            return y_commit, conflicts
        report.say(f"origin moved during the merge (attempt {attempt + 1})")
    raise Refused("origin spec-dock/canonical kept moving; nothing was changed", "Run adopt-worktree again")


def command_adopt_worktree(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    checkout = _checkout(target, context.args.checkout)
    branch = git_text(checkout, "symbolic-ref", "--quiet", "--short", "HEAD", ok=(0, 1))
    if not branch:
        raise Refused(f"{checkout} is not on a branch")
    if not _git_version(ADOPT_GIT):
        raise Refused(f"adopt-worktree needs git {ADOPT_GIT[0]}.{ADOPT_GIT[1]} or newer (merge-tree --merge-base)")
    if tree_oid(target.project, f"{target.default_ref}:{SPEC_ROOT}") is not None:
        raise Refused(
            f"origin/{target.default_branch} still has {SPEC_ROOT}; the cutover PR is not merged",
            "Merge the cutover PR and fetch origin first",
        )
    head = resolve_commit(checkout, "HEAD")
    base = git_text(checkout, "merge-base", "HEAD", target.default_ref, ok=(0, 1))
    if not head or not base:
        raise Refused(f"{branch} has no merge base with origin/{target.default_branch}")

    def listed(*options: str) -> list[str]:
        output = run_git(checkout, "ls-files", "-z", *options, "--", SPEC_ROOT, read_only=True).stdout
        return [p.decode("utf-8", "surrogateescape") for p in output.split(b"\0") if p]

    if not run_git(checkout, "ls-tree", "HEAD", "--", SPEC_ROOT, read_only=True).stdout and not listed():
        # A finished adoption: an empty tree here would read as deleting every canonical file.
        report.say(f"{branch} no longer tracks {SPEC_ROOT}; it is already adopted")
        report.step("Merge the default branch into this branch, then run spec-dock canonical link")
        return EXIT_OK
    base_tree = tree_oid(checkout, f"{base}:{SPEC_ROOT}")
    if base_tree is None:
        raise Refused(f"the merge base {base} has no {SPEC_ROOT}; this branch already left legacy storage")
    staged = run_git(
        checkout, "diff", "--cached", "--quiet", "--", ".", f":(exclude){SPEC_ROOT}", read_only=True, ok=(0, 1)
    )
    if staged.returncode != 0:
        raise Refused("the checkout has staged changes outside spec-dock/initiatives", "Commit or unstage them first")

    missing = [p for p in listed() if not ((checkout / p).is_symlink() or (checkout / p).is_file())]
    if missing:
        raise Refused(
            f"tracked spec files are missing from the working tree (sparse checkout or unstaged deletions): {missing[:10]}",
            "Restore them, or stage the deletions with git rm, then run adopt-worktree again",
        )
    present = [
        p
        for p in dict.fromkeys([*listed(), *listed("--others", "--exclude-standard")])
        if (checkout / p).is_symlink() or (checkout / p).is_file()
    ]
    with Workspace(target) as workspace:
        repo = workspace.repo
        # The branch may exist only in this checkout's clone; its objects back the merge-base trees read below.
        run_git(repo, "fetch", "--quiet", "--no-tags", str(checkout), f"+{head}:refs/heads/adopt-branch")
        full = _worktree_entries(repo, checkout, present)
        relative = [TreeEntry(e.mode, e.kind, e.oid, e.path.removeprefix(SPEC_ROOT + "/")) for e in full]
        base_entries = {e.path: e for e in list_tree(repo, f"{base}:{SPEC_ROOT}")}
        before_scopes, _ = load_scopes(repo, base)
        meta_payloads = [
            (e.path, (checkout / SPEC_ROOT / e.path).read_bytes())
            for e in relative
            if PurePosixPath(e.path).name == META_FILE
        ]
        after_scopes, _ = parse_scopes(meta_payloads)
        differences = _meta_differences(before_scopes, after_scopes)
        report.data["structure_differences"] = differences
        for line in differences:
            report.say(f"structure: {line}")
        changed = write_tree(repo, relative, workspace.root) != base_tree
        conflicts: list[dict[str, str]] = []
        final: dict[str, TreeEntry] = {}
        expected_commit = None
        flattener = TreeFlattener(repo, state.idmap, workspace.root)
        flat = flattener.flatten(relative)
        if flat.problems:
            report.anomalies.extend(flat.problems)
            raise Refused(
                f"{len(flat.problems)} spec paths of {branch} cannot be flattened; nothing was written",
                "Move or remove them on the branch (README), then run adopt-worktree again",
            )
        moved = flat.moved
        if changed:
            flat_base = flattener.flatten(list_tree(repo, f"{base}:{SPEC_ROOT}"))
            expected_commit, conflicts = _adopt_into_canonical(
                context,
                target,
                workspace,
                flat.entries,
                base,
                write_tree(repo, flat_base.entries, workspace.root),
                branch,
            )
            final = {e.path: e for e in list_tree(repo, expected_commit)}
        else:
            report.say(f"no spec changes since {base}; only the spec tree is removed from {branch}")
        deletions, mismatched = [], []
        for entry in full:
            inner = entry.path.removeprefix(SPEC_ROOT + "/")
            copied = moved.get(inner)  # the flattened entry: links rewritten, so compared by that content
            in_canonical = final.get(copied.path) if copied is not None else None
            at_base = base_entries.get(inner)
            if copied is None or (
                (in_canonical and (in_canonical.mode, in_canonical.oid) == (copied.mode, copied.oid))
                or (at_base and (at_base.mode, at_base.oid) == (entry.mode, entry.oid))
            ):
                deletions.append(entry.path)
            else:
                mismatched.append(entry.path)
        report.data.update({
            "canonical_commit": expected_commit,
            "conflicts": conflicts,
            "delete": deletions,
            "mismatched": mismatched,
        })
        if not context.args.apply:
            for path in deletions:
                report.say(f"would remove from the checkout: {path}")
            for path in mismatched:
                report.warn(f"{path} differs from canonical after the merge; --apply stops before removing anything")
            report.step("adopt-worktree --apply")
            return EXIT_OK
        if expected_commit is not None:
            tip = remote_ref(target, CANONICAL_REF)
            reached = tip == expected_commit or (
                tip is not None
                and workspace.fetch_canonical() is not None
                and run_git(
                    repo, "merge-base", "--is-ancestor", expected_commit, "refs/heads/canonical", ok=(0, 1)
                ).returncode
                == 0
            )
            if not reached:
                raise Stopped(
                    "origin spec-dock/canonical does not contain the adopted commit", "Inspect origin and run again"
                )
    record = {
        "branch": branch,
        "checkout": str(checkout),
        "canonical_commit": expected_commit,
        "structure_differences": differences,
        "metadata": {path: payload.decode("utf-8", "replace") for path, payload in meta_payloads},
    }
    _write_json(state.directory / "adopt" / f"{branch.replace('/', '-')}.json", record)
    after = Stopped if expected_commit is not None else Refused
    if mismatched:
        raise after(
            f"these files differ from canonical, so nothing was removed: {mismatched}",
            "Compare them with the catalog, then remove spec-dock/initiatives from the branch by hand (README)",
        )
    context.wrote = True
    run_git(checkout, "rm", "-r", "-q", "--cached", "--", SPEC_ROOT)
    commit = run_git(checkout, "commit", "-q", "-m", CUT_COMMIT_MESSAGE, ok=(0, 1))
    if commit.returncode != 0:
        run_git(checkout, "reset", "-q", "--", SPEC_ROOT)
        raise after(
            f"the commit removing {SPEC_ROOT} failed: {commit.stderr.decode('utf-8', 'replace').strip()}",
            "Fix the commit problem (hooks or signing) and run adopt-worktree again",
        )
    if run_git(checkout, "ls-tree", "HEAD", "--", SPEC_ROOT, read_only=True).stdout:
        raise Stopped(f"HEAD still has {SPEC_ROOT}; nothing was removed from the working tree", "Inspect the branch")
    hashed = {entry.path: entry.oid for entry in full}
    for path in deletions:
        absolute = checkout / path
        current = (
            git_text(None, "hash-object", "--stdin", input=os.fsencode(str(absolute.readlink())))
            if absolute.is_symlink()
            else git_text(None, "hash-object", "--no-filters", str(absolute))
        )
        if current != hashed[path]:
            raise Stopped(f"{path} changed during adopt-worktree; it and the files after it were kept", "Run again")
        absolute.unlink()
    root = checkout / SPEC_ROOT
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        with contextlib.suppress(OSError):
            directory.rmdir()
    try:
        root.rmdir()
    except OSError:
        report.step(f"move-local {checkout} (ignored files remain)")
    report.step("Merge the default branch into this branch, then run spec-dock canonical link")
    if differences:
        report.step("Register the structure differences again with SpecDock commands")
    return EXIT_OK


# --- export-legacy -----------------------------------------------------------------------------------------------


@dataclass
class Nesting:
    """Where each GitHub Scope goes back to in the nested layout, and why some cannot (export-legacy)."""

    nested: dict[str, str]  # Scope ID -> nested directory relative to spec-dock/initiatives
    ids: dict[int, str]  # Issue number -> Scope ID
    kinds: dict[int, str]
    anomalies: list[dict[str, Any]]


def nest_plan(entries: Iterable[TreeEntry], labeled: Mapping[int, Facts], slugs: Mapping[int, str]) -> Nesting:
    """GitHub parents give the nested path; slugs are the pre-cutover ones, else legacy_slug of the title."""
    anomalies: dict[tuple[str, str], dict[str, Any]] = {}

    def problem(code: str, key: str, message: str, **details: Any) -> None:
        anomalies.setdefault((code, key), anomaly(code, message, **details))

    ids: dict[int, str] = {}
    kinds: dict[int, str] = {}
    for number, facts in sorted(labeled.items()):
        if len(facts.kind_labels) == 1:
            kinds[number] = next(k for k, label in KIND_LABELS.items() if label == facts.kind_labels[0])
            ids[number] = scope_id(kinds[number], number)
        else:
            problem("KIND_LABEL_MULTIPLE", f"#{number}", f"#{number} has {facts.kind_labels}", number=number)
    directories: set[str] = set()
    for entry in entries:
        parts = entry.path.split("/")
        if len(parts) < 3:
            problem(
                CATALOG_PATH_OUTSIDE_SCOPE, entry.path, f"{entry.path} is not inside a <bucket>/<ID>/", path=entry.path
            )
            continue
        place = f"{parts[0]}/{parts[1]}"
        if CANONICAL_ID_RE.fullmatch(parts[1]) is None or scope_relative(parts[1]) != place:
            problem("SCOPE_DIRECTORY_MISPLACED", place, f"{place} is not <bucket>/<ID> of its number", path=place)
        elif parts[2] in NESTED_DIRECTORIES and len(parts) > 3:
            leftover = f"{place}/{parts[2]}"
            problem("SCOPE_DIRECTORY_MISPLACED", leftover, f"{leftover} is a nested leftover", path=leftover)
        else:
            directories.add(parts[1])
    changed: set[str] = set()  # current IDs whose number has a directory of another kind
    for name in sorted(directories):
        number = int(name.split("-")[1])
        current = ids.get(number)
        if current is None and number not in labeled:
            problem("SCOPE_ISSUE_MISSING", name, f"{name}/ has no Scope Issue on GitHub", scope=name)
        elif current is not None and current != name:
            problem("SCOPE_KIND_CHANGED", name, f"{name}/ is {current} on GitHub", scope=name, current=current)
            changed.add(current)
    nested: dict[str, str] = {}

    def place_of(number: int) -> str | None:
        scope = ids[number]
        if scope in nested:
            return nested[scope]
        if scope not in directories:
            if scope not in changed:
                problem("SCOPE_DIRECTORY_MISSING", scope, f"{scope} has no {scope_relative(scope)}/", scope=scope)
            return None
        facts, kind = labeled[number], kinds[number]
        name = f"{scope}-{slugs.get(number) or legacy_slug(facts.title)}"
        expected = PARENT_KINDS[kind]
        if expected is None:
            if facts.parent is not None or facts.parent_foreign:
                problem("KIND_RULE", scope, f"{scope}: an Initiative has the parent #{facts.parent}", scope=scope)
                return None
            nested[scope] = name
            return name
        if facts.parent_foreign:
            problem(
                "PARENT_CONFLICT",
                scope,
                f"{scope}: its parent {facts.parent_foreign} is in another repository",
                scope=scope,
            )
            return None
        if facts.parent is None or facts.parent not in ids:
            problem("PARENT_MISSING", scope, f"{scope}: a {kind} needs a {expected} parent on GitHub", scope=scope)
            return None
        if kinds[facts.parent] != expected:
            problem("KIND_RULE", scope, f"{scope}: the parent of a {kind} must be a {expected}", scope=scope)
            return None
        parent = place_of(facts.parent)
        if parent is None:
            return None
        nested[scope] = f"{parent}/{NESTED_DIRECTORIES[0] if kind == 'epic' else NESTED_DIRECTORIES[1]}/{name}"
        return nested[scope]

    for number in sorted(ids):
        place_of(number)
    return Nesting(nested, ids, kinds, list(anomalies.values()))


def _meta_payload(base: Scope | None, values: dict[str, Any], base_depends: list[str] | None) -> bytes:
    if base is not None:
        merged = dict(base.raw)
        if base_depends is not None and sorted(base_depends) == sorted(values["depends_on"]):
            values = {**values, "depends_on": base_depends}
        changed = {key: value for key, value in values.items() if merged.get(key) != value}
        if not changed:
            return base.payload
        merged.update(changed)
        if isinstance(merged.get("revision"), int):
            merged["revision"] += 1
        return _dump_like(merged, base.payload)
    payload = {key: values.get(key) for key in META_KEY_ORDER}
    payload.update({"schema_version": 3, "lifecycle": None, "revision": 0})
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _dump_like(payload: Mapping[str, Any], original: bytes) -> bytes:
    """Serialize in the original file's style: one line without spaces, or indented; same trailing newline."""
    text = original.decode("utf-8", "replace")
    one_line = text.strip().count("\n") == 0
    if one_line:
        dumped = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        dumped = json.dumps(payload, ensure_ascii=False, indent=2)
    return (dumped + ("\n" if text.endswith("\n") else "")).encode("utf-8")


def command_export_legacy(context: Context) -> int:
    report = context.report
    target = context.target()
    state = State(target.state_dir, target.repository)
    branch = context.args.branch
    if context.args.apply:
        require_fresh_default(target)
    source = source_commit(target)
    try:
        schema = json.loads(_blob(target.project, source, "spec-dock/workspace.json") or b"null").get("schema_version")
    except (AttributeError, json.JSONDecodeError):
        schema = None
    if schema != 4:
        raise Refused(f"origin/{target.default_branch} is not cut over (workspace schema {schema!r})")
    legacy = legacy_commit(target, state)
    base_scopes, _ = load_scopes(target.project, legacy) if legacy else ([], [])
    renames = state.renames()
    number_of_old = {old: entry["number"] for old, entry in state.idmap.items()}
    base_by_number: dict[int, Scope] = {}
    for scope in base_scopes:
        number = number_of_old.get(scope.id, scope.number)
        if number is not None:
            base_by_number[number] = scope
    declaration = _blob(target.project, legacy, "spec-dock/workspace.json") if legacy else None
    gh = context.github(target)
    try:
        labeled = fetch_labeled(gh)
    except GithubError as error:
        raise Refused(f"GitHub read failed: {error}") from error
    current = remote_ref(target, f"refs/heads/{branch}")
    with Workspace(target) as workspace:
        canonical = workspace.fetch_canonical()
        if canonical is None:
            raise Refused("origin has no spec-dock/canonical")
        repo = workspace.repo
        catalog_entries = [
            e
            for e in list_tree(repo, canonical)
            if e.path not in CANONICAL_ROOT_FILES
            and not e.path.startswith(RUNTIME_DIRECTORY + "/")
            and PurePosixPath(e.path).name != META_FILE
        ]
        slugs = {number: scope.slug for number, scope in base_by_number.items() if scope.slug}
        nesting = nest_plan(catalog_entries, labeled, slugs)
        if nesting.anomalies:
            report.anomalies.extend(nesting.anomalies)
            raise Refused(
                f"{len(nesting.anomalies)} problems keep the catalog from nesting back; nothing was written",
                "Fix them on GitHub or in the catalog (README), then run export-legacy again",
            )
        ids, kinds = nesting.ids, nesting.kinds
        spec_files, links = _nest_files(repo, catalog_entries, nesting)
        metas: list[TreeEntry] = []
        for number in sorted(ids):
            facts = labeled[number]
            scope_key = ids[number]
            parent_key = ids.get(facts.parent) if facts.parent else None
            grandparent = labeled[facts.parent].parent if facts.parent in labeled else None
            grand = ids.get(grandparent) if grandparent is not None else None
            kind = kinds[number]
            values: dict[str, Any] = {
                "type": kind,
                "id": scope_key,
                "title": facts.title,
                "slug": nesting.nested[scope_key].rsplit("/", 1)[-1][len(scope_key) + 1 :],
                "parent_id": parent_key,
                "initiative_id": parent_key if kind == "epic" else grand if kind == "issue" else None,
                "epic_id": parent_key if kind == "issue" else None,
                "depends_on": sorted(ids[n] for n in facts.blocked_by if n in ids),
                "backend": "github",
            }
            base = base_by_number.get(number)
            github = dict(base.raw["github"]) if base is not None and isinstance(base.raw.get("github"), dict) else {}
            github.update({"issue_number": number})
            github.setdefault("repo_owner", target.owner)
            github.setdefault("repo_name", target.name)
            values["github"] = github
            base_depends = [rename_id(d, renames) for d in base.depends_on] if base is not None else None
            payload = _meta_payload(base, values, base_depends)
            metas.append(
                TreeEntry(
                    "100644", "blob", hash_blob(repo, payload), f"{SPEC_ROOT}/{nesting.nested[scope_key]}/{META_FILE}"
                )
            )
        entries = [
            e
            for e in list_tree(workspace.repo, source)
            if e.path not in (WORKFLOW_DESTINATION, "spec-dock/workspace.json")
            and e.path != SPEC_ROOT
            and not e.path.startswith(SPEC_ROOT + "/")
        ]
        entries.append(
            TreeEntry(
                "100644",
                "blob",
                hash_blob(workspace.repo, declaration or WORKSPACE_V3_BYTES),
                "spec-dock/workspace.json",
            )
        )
        outside = [e.path for e in entries]
        before = PathSet([*outside, *(f"{SPEC_ROOT}/{e.path}" for e in catalog_entries)])
        after = PathSet([*outside, *(e.path for e in spec_files)])
        report_links = link_report(links, before, after)
        report.data["links"] = report_links.as_data()
        report.say(
            f"links: {report_links.rewritten} rewritten back, {len(report_links.unrewritable)} unrewritable, "
            f"{len(report_links.broken_before)} already broken"
        )
        for item in report_links.unrewritable:
            report.warn(f"link {item['text']!r} in {item['file']} will not open {item['target']} after nesting")
        entries.extend(spec_files)
        entries.extend(metas)
        tree = write_tree(workspace.repo, entries, workspace.root)
        commit = commit_tree(
            workspace.repo, tree, [source], EXPORT_COMMIT_MESSAGE, target.identity, commit_date(target.project, source)
        )
        report.data.update({"branch": branch, "commit": commit, "scopes": len(metas), "legacy_commit": legacy})
        report.say(f"export commit {commit} with {len(metas)} .meta.json files for branch {branch}")
        if current is not None and current != commit:
            raise _existing_ref_refusal(f"refs/heads/{branch}", current, commit)
        if not context.args.apply:
            report.step("export-legacy --apply")
            return EXIT_OK
        context.wrote = True
        outcome = workspace.push(commit, f"refs/heads/{branch}")
        if outcome == "rejected":
            raise Refused(f"origin rejected {branch}")
        report.say(f"origin {branch}: {outcome}")
    report.step(f"Add a commit restoring the CI SpecDock steps removed by the cutover PR to {branch} and open the PR")
    report.step("After the merge, run spec-dock canonical remove --yes in each checkout; undo --apply if needed")
    return EXIT_OK


def _nest_files(
    repo: Path, catalog_entries: Sequence[TreeEntry], nesting: Nesting
) -> tuple[list[TreeEntry], list[Link]]:
    """Catalog files at their nested paths with links rewritten back, plus the child-layer rule links."""
    mapping = NestMap(nesting.nested)
    target = link_target(mapping, {})
    blobs = read_blobs(repo, [e.oid for e in catalog_entries if linkable(e.path, e.mode)])
    files: list[TreeEntry] = []
    links: list[Link] = []
    for entry in catalog_entries:
        place = mapping.file(entry.path)
        assert isinstance(place, str)  # nest_plan refused everything else
        oid = entry.oid
        kind = linkable(entry.path, entry.mode)
        if kind is not None:
            payload, file_links = rewrite_links(
                blobs[entry.oid], kind=kind, old=f"{SPEC_ROOT}/{entry.path}", new=f"{SPEC_ROOT}/{place}", target=target
            )
            links.extend(file_links)
            if payload != blobs[entry.oid]:
                oid = hash_blob(repo, payload)
        files.append(TreeEntry(entry.mode, entry.kind, oid, f"{SPEC_ROOT}/{place}"))
    taken = {e.path for e in files}
    for number, scope in sorted(nesting.ids.items()):
        rule = LEGACY_CHILD_RULES.get(nesting.kinds[number])
        if rule is None:
            continue
        path = f"{SPEC_ROOT}/{nesting.nested[scope]}/{rule[0]}/rules.md"
        if path not in taken:
            relative = posixpath.relpath(rule[1], posixpath.dirname(path))
            files.append(TreeEntry("120000", "blob", hash_blob(repo, relative.encode()), path))
    return files, links


def rename_id(value: str, renames: Mapping[str, str]) -> str:
    return renames.get(value, value)


# ---------------------------------------------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------------------------------------------

COMMANDS: dict[str, Callable[[Context], int]] = {
    "plan": command_plan,
    "register": command_register,
    "verify": command_verify,
    "build-canonical": command_build_canonical,
    "cut": command_cut,
    "move-local": command_move_local,
    "adopt-worktree": command_adopt_worktree,
    "undo": command_undo,
    "export-legacy": command_export_legacy,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="migrate.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in COMMANDS:
        command = sub.add_parser(name)
        command.add_argument("--project", required=True, help="the main checkout of the repository to migrate")
        command.add_argument("--repo", help="OWNER/NAME when origin is not GitHub (rehearsal clones)")
        command.add_argument("--state-dir", help="where <owner>-<repo>/ work records live (default: .state)")
        command.add_argument("--json", action="store_true", help="print one JSON object")
        if name not in ("plan", "verify"):
            command.add_argument("--apply", action="store_true", help="write; without it only the plan is printed")
        if name in ("move-local", "adopt-worktree"):
            command.add_argument("checkout", help="a checkout of the same clone")
            command.add_argument("--pc-name", help="name used in .local-<PC> and .conflict-<PC> file names")
        if name == "cut":
            command.add_argument("--branch", default=DEFAULT_CUT_BRANCH)
        if name == "export-legacy":
            command.add_argument("--branch", default=DEFAULT_EXPORT_BRANCH)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: Callable[..., Any] | None = None,
    clock: Any = None,
    stdout: Any = None,
) -> int:
    args = build_parser().parse_args(argv)
    if not hasattr(args, "apply"):
        args.apply = False
    if not hasattr(args, "pc_name"):
        args.pc_name = None
    report = Report(args.command, args.apply)
    context = Context(args, report, runner, clock or SystemClock())
    error: str | None = None
    try:
        code = COMMANDS[args.command](context)
    except MigrationError as failure:
        code = EXIT_STOPPED if context.has_written() else failure.exit_code
        error = failure.message
        if failure.next_step:
            report.step(failure.next_step)
    except (GitError, GithubError) as failure:
        code = EXIT_STOPPED if context.has_written() else EXIT_REFUSED
        error = str(failure)
        report.step("Inspect the error, then run the same command again")
    emit(report, code, args.json, error, stdout or sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
