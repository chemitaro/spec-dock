"""A stateful fake of `gh api` for GitHub REST and GraphQL; it never touches the network.

The same model answers in-process (as a subprocess runner) and through a `gh` executable placed
first on PATH. Issue numbers and Issue ids differ, conditional list requests return 304 with exit 1
like the real CLI, and every request is recorded so tests can count metered calls.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, unquote, urlsplit

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    import pytest

ROOT = Path(__file__).resolve().parents[2]
BASE_TIME = datetime(2026, 10, 26, 0, 0, tzinfo=timezone.utc)
KIND_LABELS = {"initiative": "spec-dock:initiative", "epic": "spec-dock:epic", "issue": "spec-dock:issue"}
_REASONS = {200: "OK", 201: "Created", 204: "No Content", 304: "Not Modified", 404: "Not Found", 422: "Unprocessable"}


def _timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FakeClock:
    """Injected monotonic and wall clock; sleeping advances time without waiting."""

    def __init__(self, start: datetime = BASE_TIME, monotonic: float = 1000.0) -> None:
        self._now = start
        self._monotonic = monotonic
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self._monotonic

    def now(self) -> datetime:
        return self._now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        self._monotonic += seconds
        self._now += timedelta(seconds=seconds)


@dataclass
class FakeIssue:
    number: int
    id: int
    title: str
    body: str = ""
    state: str = "open"
    state_reason: str | None = None
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    parent: list[Any] | None = None  # [repository, number]
    sub_issues: list[list[Any]] = field(default_factory=list)
    blocked_by: list[list[Any]] = field(default_factory=list)
    updated_at: str = ""
    pull_request: bool = False
    repository: str = ""


@dataclass
class FakeRequest:
    method: str
    endpoint: str
    payload: object
    headers: dict[str, str]
    status: int
    at: float
    when: str


@dataclass
class _Fault:
    status: int | None
    headers: dict[str, str]
    body: object
    method: str | None
    endpoint: str | None
    timeout: bool
    times: int
    apply: bool = False


class FakeGithub:
    """One GitHub repository plus foreign Issues it can reference."""

    def __init__(
        self,
        repository: str = "example/repo",
        *,
        login: str = "fixture-user",
        clock: FakeClock | None = None,
        relation_limit: int = 100,
        label_limit: int = 20,
        relation_updates_timestamp: bool = False,
    ) -> None:
        self.repository = repository.lower()
        self.login = login
        self.clock = clock or FakeClock()
        self.relation_limit = relation_limit
        self.label_limit = label_limit
        self.relation_updates_timestamp = relation_updates_timestamp
        self.issues: dict[tuple[str, int], FakeIssue] = {}
        self.labels: dict[str, dict[str, str]] = {}
        self.requests: list[FakeRequest] = []
        self._faults: list[_Fault] = []
        self._tick = 0
        self._next_number = 1

    # Model setup (not recorded as requests).

    def add_issue(
        self,
        number: int | None = None,
        *,
        title: str = "Issue",
        body: str = "",
        labels: Iterable[str] = (),
        state: str = "open",
        state_reason: str | None = None,
        assignees: Iterable[str] = (),
        pull_request: bool = False,
        repository: str | None = None,
    ) -> FakeIssue:
        owner = (repository or self.repository).lower()
        if number is None:
            number = self._next_number
        if owner == self.repository:
            self._next_number = max(self._next_number, number + 1)
        if (owner, number) in self.issues:
            raise ValueError(f"fake Issue already exists: {owner}#{number}")
        issue = FakeIssue(
            number=number,
            id=self.issue_id(number, owner),
            title=title,
            body=body,
            state=state,
            state_reason=state_reason,
            labels=sorted(set(labels)),
            assignees=list(assignees),
            pull_request=pull_request,
            repository=owner,
        )
        for name in issue.labels:
            self.labels.setdefault(name, {"name": name, "color": "ededed", "description": ""})
        self.issues[owner, number] = issue
        self._touch(issue)
        return issue

    def scope(
        self,
        kind: str,
        *,
        slug: str,
        title: str | None = None,
        number: int | None = None,
        parent: int | None = None,
        state: str = "open",
        state_reason: str | None = None,
        labels: Iterable[str] = (),
        body: str = "Scope body.",
    ) -> FakeIssue:
        """Add a Scope Issue with one kind label and a trailing slug marker."""
        issue = self.add_issue(
            number,
            title=title or slug.replace("-", " ").title(),
            body=f"{body}\n\n<!-- spec-dock:slug={slug} -->\n",
            labels=(KIND_LABELS[kind], *labels),
            state=state,
            state_reason=state_reason,
        )
        if parent is not None:
            self.set_parent(issue.number, parent)
        return issue

    def add_foreign_issue(
        self, repository: str, number: int, *, title: str = "Foreign", state: str = "open"
    ) -> FakeIssue:
        return self.add_issue(number, title=title, state=state, repository=repository)

    def issue(self, number: int, repository: str | None = None) -> FakeIssue:
        return self.issues[(repository or self.repository).lower(), number]

    def issue_id(self, number: int, repository: str | None = None) -> int:
        owner = (repository or self.repository).lower()
        offset = 0 if owner == self.repository else 500_000
        return 1_000_000 + offset + number * 7

    def set_parent(self, child: int, parent: int | None, *, parent_repository: str | None = None) -> None:
        self._set_parent(self.issue(child), None if parent is None else self.issue(parent, parent_repository))

    def set_foreign_child(self, parent: int, repository: str, number: int) -> None:
        self._set_parent(self.issue(number, repository), self.issue(parent))

    def block(self, number: int, *, by: int, repository: str | None = None) -> None:
        blocker = self.issue(by, repository)
        target = self.issue(number)
        reference = [blocker.repository, blocker.number]
        if reference not in target.blocked_by:
            target.blocked_by.append(reference)
            if self.relation_updates_timestamp:
                self._touch(target)

    def touch(self, number: int) -> None:
        self._touch(self.issue(number))

    def inject(
        self,
        *,
        status: int | None = None,
        headers: dict[str, str] | None = None,
        body: object = None,
        method: str | None = None,
        endpoint: str | None = None,
        timeout: bool = False,
        times: int = 1,
        apply: bool = False,
    ) -> None:
        """Answer the next matching requests with a fixed response or a runner timeout.

        With ``apply=True`` the request takes effect first, as when GitHub applied a write but the answer was lost.
        """
        self._faults.append(_Fault(status, dict(headers or {}), body, method, endpoint, timeout, times, apply))

    def clear_faults(self) -> None:
        self._faults.clear()

    # Inspection.

    def metered_requests(self) -> list[FakeRequest]:
        """Requests that consume the primary rate limit; a 304 answer does not."""
        return [request for request in self.requests if request.status != 304]

    def writes(self) -> list[FakeRequest]:
        return [request for request in self.requests if request.method != "GET" and request.endpoint != "graphql"]

    def graphql_requests(self) -> list[FakeRequest]:
        return [request for request in self.requests if request.endpoint == "graphql"]

    # In-process runner with the subprocess.run calling convention.

    def __call__(self, argv: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        stdin = kwargs.get("input")
        stdout, returncode = self.handle(list(argv), stdin if isinstance(stdin, str) else None)
        return subprocess.CompletedProcess(list(argv), returncode, stdout, "")

    def handle(self, argv: list[str], stdin: str | None) -> tuple[str, int]:
        method, endpoint, headers, has_input = _parse_argv(argv)
        payload = json.loads(stdin) if has_input and stdin else None
        fault = self._take_fault(method, endpoint)
        if fault is not None and fault.apply and endpoint != "graphql":
            self._rest(method, endpoint, payload, headers)
        if fault is not None:
            if fault.timeout:
                self._record(method, endpoint, payload, headers, 0)
                raise subprocess.TimeoutExpired(argv, 30)
            assert fault.status is not None
            self._record(method, endpoint, payload, headers, fault.status)
            return _response(fault.status, fault.body, fault.headers)
        if endpoint == "graphql":
            assert method == "POST" and isinstance(payload, dict)
            status, body, extra = self._graphql(payload)
        else:
            status, body, extra = self._rest(method, endpoint, payload, headers)
        self._record(method, endpoint, payload, headers, status)
        return _response(status, body, extra)

    # Persistence for the PATH executable.

    def to_json(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "login": self.login,
            "clock": {"now": _timestamp(self.clock.now()), "monotonic": self.clock.monotonic()},
            "relation_limit": self.relation_limit,
            "label_limit": self.label_limit,
            "relation_updates_timestamp": self.relation_updates_timestamp,
            "issues": [asdict(issue) for issue in self.issues.values()],
            "labels": self.labels,
            "requests": [asdict(request) for request in self.requests],
            "faults": [asdict(fault) for fault in self._faults],
            "tick": self._tick,
            "next_number": self._next_number,
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> FakeGithub:
        clock = FakeClock(
            datetime.strptime(payload["clock"]["now"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),
            payload["clock"]["monotonic"],
        )
        fake = cls(
            payload["repository"],
            login=payload["login"],
            clock=clock,
            relation_limit=payload["relation_limit"],
            label_limit=payload["label_limit"],
            relation_updates_timestamp=payload["relation_updates_timestamp"],
        )
        for raw in payload["issues"]:
            issue = FakeIssue(**raw)
            fake.issues[issue.repository, issue.number] = issue
        fake.labels = payload["labels"]
        fake.requests = [FakeRequest(**raw) for raw in payload["requests"]]
        fake._faults = [_Fault(**raw) for raw in payload["faults"]]
        fake._tick = payload["tick"]
        fake._next_number = payload["next_number"]
        return fake

    # Internals.

    def _touch(self, issue: FakeIssue) -> None:
        self._tick += 1
        issue.updated_at = _timestamp(BASE_TIME + timedelta(seconds=self._tick))

    def _record(self, method: str, endpoint: str, payload: object, headers: dict[str, str], status: int) -> None:
        self.requests.append(
            FakeRequest(
                method, endpoint, payload, headers, status, self.clock.monotonic(), _timestamp(self.clock.now())
            )
        )

    def _take_fault(self, method: str, endpoint: str) -> _Fault | None:
        for fault in self._faults:
            if fault.times <= 0:
                continue
            if fault.method is not None and fault.method != method:
                continue
            if fault.endpoint is not None and fault.endpoint not in endpoint:
                continue
            fault.times -= 1
            return fault
        return None

    def _set_parent(self, child: FakeIssue, parent: FakeIssue | None) -> None:
        child_reference = [child.repository, child.number]
        if child.parent is not None:
            old = self.issues.get((child.parent[0], child.parent[1]))
            if old is not None and child_reference in old.sub_issues:
                old.sub_issues.remove(child_reference)
                if self.relation_updates_timestamp:
                    self._touch(old)
        child.parent = None if parent is None else [parent.repository, parent.number]
        if parent is not None:
            parent.sub_issues.append(child_reference)
            if self.relation_updates_timestamp:
                self._touch(parent)
        if self.relation_updates_timestamp:
            self._touch(child)

    def _by_id(self, value: object) -> FakeIssue | None:
        for issue in self.issues.values():
            if issue.id == value:
                return issue
        return None

    def _local(self, number: int) -> FakeIssue | None:
        return self.issues.get((self.repository, number))

    def _rest_issue(self, issue: FakeIssue) -> dict[str, object]:
        rendered: dict[str, object] = {
            "id": issue.id,
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "state_reason": issue.state_reason,
            "labels": [{"name": name} for name in issue.labels],
            "assignees": [{"login": login} for login in issue.assignees],
            "updated_at": issue.updated_at,
            "html_url": f"https://github.com/{issue.repository}/issues/{issue.number}",
            "repository_url": f"https://api.github.com/repos/{issue.repository}",
        }
        if issue.pull_request:
            rendered["pull_request"] = {"url": f"https://api.github.com/repos/{issue.repository}/pulls/{issue.number}"}
        return rendered

    def _graphql(self, payload: dict[str, Any]) -> tuple[int, object, dict[str, str]]:
        query = payload.get("query")
        variables = payload.get("variables") or {}
        assert isinstance(query, str) and isinstance(variables, dict)
        if f"{variables.get('owner')}/{variables.get('name')}".lower() != self.repository:
            return 200, {"data": {"repository": None}, "errors": [{"type": "NOT_FOUND", "message": "missing"}]}, {}
        filter_match = re.search(r"issues\(([^)]*)\)", query)
        assert filter_match is not None, "fake GraphQL expects repository.issues(...)"
        arguments = filter_match.group(1)
        label_filter = re.search(r"labels:\s*\[([^\]]*)\]", arguments)
        page_size = re.search(r"first:\s*(\d+)", arguments)
        assert label_filter is not None and page_size is not None, "fake GraphQL expects labels and first"
        wanted = set(re.findall(r'"([^"]+)"', label_filter.group(1)))
        assert wanted, "an empty label filter returns no Issues on GitHub"
        first = int(page_size.group(1))
        candidates = sorted(
            (
                issue
                for issue in self.issues.values()
                if issue.repository == self.repository and not issue.pull_request and wanted & set(issue.labels)
            ),
            key=lambda issue: issue.number,
        )
        start = int(variables["after"]) if variables.get("after") else 0
        page = candidates[start : start + first]
        end = start + len(page)
        nodes = [self._graphql_node(issue) for issue in page]
        data = {
            "rateLimit": {"cost": 1, "remaining": 4999, "resetAt": "2026-10-26T01:00:00Z"},
            "repository": {
                "issues": {
                    "pageInfo": {"hasNextPage": end < len(candidates), "endCursor": str(end) if page else None},
                    "nodes": nodes,
                }
            },
        }
        return 200, {"data": data}, {}

    def _graphql_reference(self, reference: list[Any]) -> dict[str, object]:
        issue = self.issues[reference[0], reference[1]]
        return {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state.upper(),
            "repository": {"nameWithOwner": issue.repository},
        }

    def _graphql_node(self, issue: FakeIssue) -> dict[str, object]:
        limit = self.relation_limit
        return {
            "number": issue.number,
            "databaseId": issue.id,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state.upper(),
            "stateReason": issue.state_reason.upper() if issue.state_reason else None,
            "updatedAt": issue.updated_at,
            "url": f"https://github.com/{issue.repository}/issues/{issue.number}",
            "labels": {
                "totalCount": len(issue.labels),
                "nodes": [{"name": name} for name in issue.labels[: self.label_limit]],
            },
            "assignees": {"nodes": [{"login": login} for login in issue.assignees[:10]]},
            "parent": None if issue.parent is None else self._graphql_reference(issue.parent),
            "subIssues": {
                "totalCount": len(issue.sub_issues),
                "nodes": [self._graphql_reference(reference) for reference in issue.sub_issues[:limit]],
            },
            "blockedBy": {
                "totalCount": len(issue.blocked_by),
                "nodes": [self._graphql_reference(reference) for reference in issue.blocked_by[:limit]],
            },
        }

    def _list_etag(self, label: str) -> tuple[list[dict[str, object]], str]:
        issues = sorted(
            (issue for issue in self.issues.values() if issue.repository == self.repository and label in issue.labels),
            key=lambda issue: (issue.updated_at, issue.number),
            reverse=True,
        )
        body = [self._rest_issue(issue) for issue in issues[:1]]
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:32]
        return body, f'W/"{digest}"'

    def _rest(
        self, method: str, endpoint: str, payload: object, headers: dict[str, str]
    ) -> tuple[int, object, dict[str, str]]:
        parts = urlsplit(endpoint)
        path = [unquote(part) for part in parts.path.split("/")]
        query = {key: values[-1] for key, values in parse_qs(parts.query).items()}
        if path == ["user"] and method == "GET":
            return 200, {"login": self.login}, {}
        prefix = ["repos", *self.repository.split("/")]
        if path[:3] != prefix:
            return 404, {"message": "Not Found"}, {}
        rest = path[3:]
        page_size = int(query.get("per_page", "30"))
        page = int(query.get("page", "1"))

        def paged(items: list[Any]) -> list[Any]:
            return items[(page - 1) * page_size : page * page_size]

        if rest == ["issues"] and method == "GET":
            label = query.get("labels", "")
            assert query.get("state") == "all" and query.get("sort") == "updated" and query.get("direction") == "desc"
            body, etag = self._list_etag(label)
            if headers.get("If-None-Match") == etag:
                return 304, None, {"ETag": etag}
            return 200, body, {"ETag": etag}
        if rest == ["issues"] and method == "POST":
            assert isinstance(payload, dict)
            issue = self.add_issue(
                title=payload["title"], body=payload.get("body", ""), labels=payload.get("labels", [])
            )
            return 201, self._rest_issue(issue), {}
        if rest == ["labels"] and method == "POST":
            assert isinstance(payload, dict)
            if payload["name"] in self.labels:
                return 422, {"message": "Validation Failed", "errors": [{"code": "already_exists"}]}, {}
            self.labels[payload["name"]] = {
                "name": payload["name"],
                "color": payload.get("color", ""),
                "description": payload.get("description", ""),
            }
            return 201, self.labels[payload["name"]], {}
        if len(rest) == 2 and rest[0] == "labels" and method == "GET":
            label_body = self.labels.get(rest[1])
            return (200, label_body, {}) if label_body is not None else (404, {"message": "Not Found"}, {})
        if len(rest) < 2 or rest[0] != "issues" or not rest[1].isdigit():
            return 404, {"message": "Not Found"}, {}
        found = self._local(int(rest[1]))
        if found is None:
            return 404, {"message": "Not Found"}, {}
        issue = found
        tail = rest[2:]
        if not tail and method == "GET":
            return 200, self._rest_issue(issue), {}
        if not tail and method == "PATCH":
            assert isinstance(payload, dict)
            for key in ("title", "state", "state_reason"):
                if key in payload:
                    setattr(issue, key, payload[key])
            if payload.get("state") == "open":
                issue.state_reason = "reopened"
            self._touch(issue)
            return 200, self._rest_issue(issue), {}
        if tail == ["parent"] and method == "GET":
            if issue.parent is None:
                return 404, {"message": "Not Found"}, {}
            return 200, self._rest_issue(self.issues[issue.parent[0], issue.parent[1]]), {}
        if tail == ["sub_issues"] and method == "GET":
            children = [self._rest_issue(self.issues[ref[0], ref[1]]) for ref in issue.sub_issues]
            return 200, paged(children), {}
        if tail == ["sub_issues"] and method == "POST":
            assert isinstance(payload, dict)
            child = self._by_id(payload.get("sub_issue_id"))
            if child is None:
                return 404, {"message": "Not Found"}, {}
            if child.parent is not None and not payload.get("replace_parent"):
                return 422, {"message": "Issue may only have one parent"}, {}
            self._set_parent(child, issue)
            return 201, self._rest_issue(issue), {}
        if tail == ["sub_issue"] and method == "DELETE":
            assert isinstance(payload, dict)
            child = self._by_id(payload.get("sub_issue_id"))
            if child is None or child.parent != [issue.repository, issue.number]:
                return 404, {"message": "Not Found"}, {}
            self._set_parent(child, None)
            return 200, self._rest_issue(issue), {}
        if tail == ["dependencies", "blocked_by"] and method == "GET":
            blockers = [self._rest_issue(self.issues[ref[0], ref[1]]) for ref in issue.blocked_by]
            return 200, paged(blockers), {}
        if tail == ["dependencies", "blocked_by"] and method == "POST":
            assert isinstance(payload, dict)
            blocker = self._by_id(payload.get("issue_id"))
            if blocker is None:
                return 404, {"message": "Not Found"}, {}
            reference = [blocker.repository, blocker.number]
            if reference in issue.blocked_by:
                return 422, {"message": "Dependency already exists"}, {}
            issue.blocked_by.append(reference)
            if self.relation_updates_timestamp:
                self._touch(issue)
            return 201, self._rest_issue(issue), {}
        if len(tail) == 3 and tail[:2] == ["dependencies", "blocked_by"] and method == "DELETE":
            blocker = self._by_id(int(tail[2])) if tail[2].isdigit() else None
            if blocker is None or [blocker.repository, blocker.number] not in issue.blocked_by:
                return 404, {"message": "Not Found"}, {}
            issue.blocked_by.remove([blocker.repository, blocker.number])
            if self.relation_updates_timestamp:
                self._touch(issue)
            return 200, self._rest_issue(issue), {}
        if tail == ["labels"] and method == "GET":
            return 200, paged([{"name": name} for name in issue.labels]), {}
        if tail == ["labels"] and method == "POST":
            assert isinstance(payload, dict)
            for name in payload["labels"]:
                self.labels.setdefault(name, {"name": name, "color": "ededed", "description": ""})
            issue.labels = sorted(set(issue.labels) | set(payload["labels"]))
            self._touch(issue)
            return 200, [{"name": name} for name in issue.labels], {}
        if len(tail) == 2 and tail[0] == "labels" and method == "DELETE":
            if tail[1] not in issue.labels:
                return 404, {"message": "Label does not exist"}, {}
            issue.labels.remove(tail[1])
            self._touch(issue)
            return 200, [{"name": name} for name in issue.labels], {}
        if tail == ["assignees"] and method == "POST":
            assert isinstance(payload, dict)
            for login in payload["assignees"]:
                if login not in issue.assignees:
                    issue.assignees.append(login)
            self._touch(issue)
            return 201, self._rest_issue(issue), {}
        return 404, {"message": f"fake does not implement {method} {endpoint}"}, {}


def _parse_argv(argv: list[str]) -> tuple[str, str, dict[str, str], bool]:
    """Accept only the fixed `gh api --hostname github.com --include --method M ENDPOINT` shape."""
    assert argv[:6] == ["gh", "api", "--hostname", "github.com", "--include", "--method"], argv
    method, endpoint = argv[6], argv[7]
    headers: dict[str, str] = {}
    has_input = False
    index = 8
    while index < len(argv):
        if argv[index] == "-H":
            name, _, value = argv[index + 1].partition(": ")
            headers[name] = value
            index += 2
        elif argv[index : index + 2] == ["--input", "-"]:
            has_input = True
            index += 2
        else:
            raise AssertionError(f"unexpected gh argument: {argv[index]}")
    return method, endpoint, headers, has_input


def _response(status: int, body: object, headers: dict[str, str]) -> tuple[str, int]:
    lines = [f"HTTP/2.0 {status} {_REASONS.get(status, 'Status')}", "Content-Type: application/json; charset=utf-8"]
    lines.extend(f"{name}: {value}" for name, value in headers.items())
    text = "" if body is None else json.dumps(body, ensure_ascii=False)
    returncode = 1 if status >= 400 or status == 304 else 0
    return "\r\n".join(lines) + "\r\n\r\n" + text, returncode


@dataclass(frozen=True)
class FakeGhExecutable:
    """A `gh` executable on PATH that persists the fake model between invocations."""

    state: Path
    bin_dir: Path

    def load(self) -> FakeGithub:
        return FakeGithub.from_json(json.loads(self.state.read_text(encoding="utf-8")))

    def save(self, fake: FakeGithub) -> None:
        self.state.write_text(json.dumps(fake.to_json(), ensure_ascii=False), encoding="utf-8")


def install_fake_gh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fake: FakeGithub) -> FakeGhExecutable:
    bin_dir = tmp_path / "fake-gh-bin"
    bin_dir.mkdir()
    handle = FakeGhExecutable(tmp_path / "fake-github.json", bin_dir)
    handle.save(fake)
    executable = bin_dir / "gh"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "from tests.support.fake_github import run_executable\n"
        f"sys.exit(run_executable({str(handle.state)!r}, sys.argv[1:]))\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    return handle


def run_executable(state: str, arguments: list[str]) -> int:
    handle = FakeGhExecutable(Path(state), Path(state).parent)
    fake = handle.load()
    stdin = None if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
    try:
        stdout, returncode = fake.handle(["gh", *arguments], stdin or None)
    except subprocess.TimeoutExpired:
        handle.save(fake)
        return 124
    handle.save(fake)
    sys.stdout.write(stdout)
    return returncode
