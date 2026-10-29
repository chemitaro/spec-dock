"""Serial `gh api` calls for the canonical GitHub structure: GraphQL reads, conditional probes and REST."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import re
import subprocess
import time
from typing import TYPE_CHECKING, Literal, Protocol, TypeVar, cast
from urllib.parse import quote

from spec_dock.runtime.domain.canonical_structure import (
    GITHUB_HOST,
    KIND_LABELS,
    FetchedIssue,
    IssueFacts,
    LabelDefinition,
    RelatedIssue,
    format_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

_NAME = re.compile(r"^[a-z0-9_.-]+$")
GITHUB_RATE_LIMITED = "GITHUB_RATE_LIMITED"
GITHUB_UNAVAILABLE = "GITHUB_UNAVAILABLE"
GITHUB_ACCESS_DENIED = "GITHUB_ACCESS_DENIED"
GITHUB_REQUEST_REJECTED = "GITHUB_REQUEST_REJECTED"
GITHUB_RESPONSE_INVALID = "GITHUB_RESPONSE_INVALID"
GITHUB_EFFECT_UNKNOWN = "GITHUB_EFFECT_UNKNOWN"
GITHUB_CREATE_IDENTITY_UNKNOWN = "GITHUB_CREATE_IDENTITY_UNKNOWN"

MAX_RATE_LIMIT_WAIT = 60.0
READ_RETRIES = 3
WRITE_INTERVAL = 1.0

_STATUS = re.compile(r"^HTTP/\S+\s+([0-9]{3})(?:\s|$)")
_Run = Callable[..., subprocess.CompletedProcess[str]]
Method = Literal["GET", "POST", "PATCH", "DELETE"]


@dataclass(frozen=True)
class GithubRepository:
    owner: str
    name: str
    host: str = GITHUB_HOST

    def __post_init__(self) -> None:
        if self.host != GITHUB_HOST:
            raise ValueError("only github.com repositories are supported")
        for part in (self.owner, self.name):
            if _NAME.fullmatch(part) is None or part in (".", ".."):
                raise ValueError("GitHub repository must be an explicit lowercase owner/name")

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.name}"

    @property
    def key(self) -> str:
        return f"{self.host}/{self.owner}/{self.name}"

    @classmethod
    def parse(cls, value: str) -> GithubRepository:
        parts = value.strip().lower().split("/")
        if len(parts) == 3 and parts[0] == GITHUB_HOST:
            parts = parts[1:]
        if len(parts) != 2:
            raise ValueError("GitHub repository must be owner/name or github.com/owner/name")
        return cls(parts[0], parts[1])


class GithubStructureError(RuntimeError):
    """A sanitized GitHub failure; an uncertain write may have taken effect (exit 6)."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        uncertain: bool = False,
        status: int | None = None,
        retry_at: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.uncertain = uncertain
        self.status = status
        self.retry_at = retry_at
        self.endpoint = endpoint
        super().__init__(f"{code}: {message}")

    @property
    def exit_code(self) -> int:
        return 6 if self.uncertain else 5


class GithubClock(Protocol):
    def monotonic(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...

    def now(self) -> datetime: ...


class _SystemClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


SYSTEM_CLOCK: GithubClock = _SystemClock()


@dataclass(frozen=True)
class GithubResponse:
    status: int
    headers: Mapping[str, str]
    body: object | None


class GithubApi:
    """One serial `gh api` caller per command; it never runs requests in parallel."""

    def __init__(
        self,
        *,
        runner: _Run = subprocess.run,
        clock: GithubClock = SYSTEM_CLOCK,
        timeout: float = 30.0,
        cwd: Path | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("GitHub timeout must be positive")
        self._runner = runner
        self._clock = clock
        self._timeout = timeout
        self._cwd = cwd
        self._last_write: float | None = None

    @property
    def clock(self) -> GithubClock:
        return self._clock

    def request(
        self,
        method: Method,
        endpoint: str,
        *,
        payload: object | None = None,
        ok: frozenset[int] = frozenset({200}),
        headers: Mapping[str, str] | None = None,
        write: bool | None = None,
    ) -> GithubResponse:
        mutation = (method != "GET" and endpoint != "graphql") if write is None else write
        rate_retries = server_retries = 0
        while True:
            if mutation:
                self._space_writes()
            try:
                response = self._send(method, endpoint, payload, headers, mutation=mutation)
            finally:
                if mutation:
                    self._last_write = self._clock.monotonic()
            if response.status in ok:
                return response
            wait = _rate_limit_wait(response, self._clock.now())
            if wait is not None:
                retry_at = format_timestamp(self._clock.now() + timedelta(seconds=wait))
                if mutation or wait > MAX_RATE_LIMIT_WAIT or rate_retries >= READ_RETRIES:
                    raise GithubStructureError(
                        GITHUB_RATE_LIMITED,
                        f"GitHub rate limit; retry after {retry_at}",
                        status=response.status,
                        retry_at=retry_at,
                        endpoint=endpoint,
                    )
                self._clock.sleep(wait)
                rate_retries += 1
                continue
            if response.status >= 500 and not mutation and server_retries < READ_RETRIES:
                self._clock.sleep(float(2**server_retries))
                server_retries += 1
                continue
            raise self._classify(response, endpoint, mutation=mutation)

    def _space_writes(self) -> None:
        if self._last_write is None:
            return
        elapsed = self._clock.monotonic() - self._last_write
        if elapsed < WRITE_INTERVAL:
            self._clock.sleep(WRITE_INTERVAL - elapsed)

    def _send(
        self,
        method: Method,
        endpoint: str,
        payload: object | None,
        headers: Mapping[str, str] | None,
        *,
        mutation: bool,
    ) -> GithubResponse:
        argv = ["gh", "api", "--hostname", GITHUB_HOST, "--include", "--method", method, endpoint]
        for name, value in (headers or {}).items():
            argv.extend(["-H", f"{name}: {value}"])
        if payload is not None:
            argv.extend(["--input", "-"])
        try:
            completed = self._runner(
                argv,
                cwd=str(self._cwd) if self._cwd is not None else None,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=self._timeout,
                input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            )
        except (FileNotFoundError, PermissionError, NotADirectoryError) as error:
            raise GithubStructureError(GITHUB_UNAVAILABLE, "gh could not be started", endpoint=endpoint) from error
        except subprocess.TimeoutExpired as error:
            raise _unreachable("gh timed out", endpoint, mutation=mutation) from error
        except OSError as error:
            raise _unreachable("gh failed to run", endpoint, mutation=mutation) from error
        return _parse(completed.stdout or "", endpoint, mutation=mutation)

    def _classify(self, response: GithubResponse, endpoint: str, *, mutation: bool) -> GithubStructureError:
        status = response.status
        if status in (401, 403, 404):
            return GithubStructureError(
                GITHUB_ACCESS_DENIED, f"GitHub denied the request (HTTP {status})", status=status, endpoint=endpoint
            )
        if status in (400, 410, 422):
            return GithubStructureError(
                GITHUB_REQUEST_REJECTED,
                f"GitHub rejected the request (HTTP {status})",
                status=status,
                endpoint=endpoint,
            )
        return _unreachable(f"GitHub answered HTTP {status}", endpoint, mutation=mutation, status=status)


def _rate_limit_wait(response: GithubResponse, now: datetime) -> float | None:
    """Return the documented wait for a primary or secondary rate limit, or None for other errors."""
    if response.status not in (403, 429):
        return None
    headers = response.headers
    remaining_zero = headers.get("x-ratelimit-remaining") == "0"
    mentions = "rate limit" in json.dumps(response.body).lower() if response.body is not None else False
    if "retry-after" not in headers and not remaining_zero and not mentions:
        return None
    try:
        return max(0.0, float(headers["retry-after"]))
    except (KeyError, ValueError):
        pass
    if remaining_zero:
        try:
            return max(1.0, float(headers["x-ratelimit-reset"]) - now.timestamp())
        except (KeyError, ValueError):
            pass
    return 60.0


def _unreachable(message: str, endpoint: str, *, mutation: bool, status: int | None = None) -> GithubStructureError:
    if mutation:
        return GithubStructureError(
            GITHUB_EFFECT_UNKNOWN,
            f"{message}; the write may have applied",
            uncertain=True,
            status=status,
            endpoint=endpoint,
        )
    return GithubStructureError(GITHUB_UNAVAILABLE, message, status=status, endpoint=endpoint)


def _parse(raw: str, endpoint: str, *, mutation: bool) -> GithubResponse:
    """Use the status line, never the gh exit code: gh exits 1 for 304 Not Modified."""
    head, marker, text = raw.replace("\r\n", "\n").partition("\n\n")
    lines = head.split("\n")
    matched = _STATUS.match(lines[0]) if lines else None
    if not marker or matched is None:
        raise _unreachable("gh returned no HTTP status line", endpoint, mutation=mutation)
    headers: dict[str, str] = {}
    for line in lines[1:]:
        name, separator, value = line.partition(":")
        if separator:
            headers[name.strip().lower()] = value.strip()
    body: object | None = None
    if text.strip():
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            body = text
    return GithubResponse(int(matched.group(1)), headers, body)


_KIND_FILTER = ", ".join(f'"{label}"' for label in KIND_LABELS.values())
FULL_READ_QUERY = f"""query($owner: String!, $name: String!, $after: String) {{
  rateLimit {{ cost remaining resetAt }}
  repository(owner: $owner, name: $name) {{
    issues(first: 100, after: $after, states: [OPEN, CLOSED],
           labels: [{_KIND_FILTER}]) {{
      pageInfo {{ hasNextPage endCursor }}
      nodes {{
        number databaseId title state stateReason updatedAt createdAt closedAt url
        labels(first: 20) {{ totalCount nodes {{ name }} }}
        assignees(first: 10) {{ nodes {{ login }} }}
        parent {{ number repository {{ nameWithOwner }} }}
        subIssues(first: 100) {{ totalCount nodes {{ number repository {{ nameWithOwner }} }} }}
        blockedBy(first: 100) {{ totalCount nodes {{ number title state repository {{ nameWithOwner }} }} }}
      }}
    }}
  }}
}}"""
REST_PAGE_SIZE = 100
_T = TypeVar("_T")


@dataclass(frozen=True)
class ProbeResult:
    changed: bool
    etags: dict[str, str | None]
    statuses: dict[str, int]


def _invalid(message: str, endpoint: str) -> GithubStructureError:
    return GithubStructureError(GITHUB_RESPONSE_INVALID, message, endpoint=endpoint)


def _dict(value: object, what: str, endpoint: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise _invalid(f"GitHub {what} is not an object", endpoint)
    return cast("dict[str, object]", value)


def _list(value: object, what: str, endpoint: str) -> list[object]:
    if not isinstance(value, list):
        raise _invalid(f"GitHub {what} is not a list", endpoint)
    return cast("list[object]", value)


def _int(value: object, what: str, endpoint: str) -> int:
    if type(value) is not int or cast("int", value) <= 0:
        raise _invalid(f"GitHub {what} is not a positive integer", endpoint)
    return cast("int", value)


def _text(value: object, what: str, endpoint: str) -> str:
    if not isinstance(value, str):
        raise _invalid(f"GitHub {what} is not a string", endpoint)
    return value


def _optional_text(value: object, what: str, endpoint: str) -> str | None:
    return None if value is None else _text(value, what, endpoint)


def _state(value: object, what: str, endpoint: str) -> str:
    state = _text(value, what, endpoint).lower()
    if state not in ("open", "closed"):
        raise _invalid(f"GitHub {what} is not open or closed", endpoint)
    return state


def _optional_lower(value: object, what: str, endpoint: str) -> str | None:
    text = _optional_text(value, what, endpoint)
    return text.lower() if text else None


def _names(value: object, key: str, what: str, endpoint: str) -> tuple[str, ...]:
    return tuple(_text(_dict(item, what, endpoint).get(key), what, endpoint) for item in _list(value, what, endpoint))


def _repository_of_url(value: object, endpoint: str) -> str:
    url = _text(value, "repository_url", endpoint)
    prefix = "https://api.github.com/repos/"
    if not url.lower().startswith(prefix) or url[len(prefix) :].count("/") != 1:
        raise _invalid("GitHub repository_url is not a repository", endpoint)
    return url[len(prefix) :].lower()


class GithubStructureClient:
    """Typed reads and writes of the canonical structure of one repository."""

    def __init__(self, repository: GithubRepository, api: GithubApi) -> None:
        self.repository = repository
        self.api = api
        self.last_graphql_cost: int | None = None

    # Reads.

    def fetch_structure(self) -> tuple[FetchedIssue, ...]:
        """Read every kind-labelled Issue with one GraphQL query per page, then complete overflows."""
        fetched: list[FetchedIssue] = []
        after: str | None = None
        cost = 0
        while True:
            data = self.graphql(
                FULL_READ_QUERY, {"owner": self.repository.owner, "name": self.repository.name, "after": after}
            )
            rate = data.get("rateLimit")
            if isinstance(rate, dict) and type(rate.get("cost")) is int:
                cost += cast("int", rate["cost"])
            repository = _dict(data.get("repository"), "repository", "graphql")
            issues = _dict(repository.get("issues"), "issues", "graphql")
            for node in _list(issues.get("nodes"), "issue nodes", "graphql"):
                fetched.append(self._fetched_from_graphql(_dict(node, "issue", "graphql")))
            page = _dict(issues.get("pageInfo"), "pageInfo", "graphql")
            if page.get("hasNextPage") is not True:
                break
            after = _text(page.get("endCursor"), "endCursor", "graphql")
        self.last_graphql_cost = cost
        return tuple(fetched)

    def graphql(self, query: str, variables: Mapping[str, object]) -> dict[str, object]:
        """Send one read-only GraphQL query; it is retried like any read, so mutations are refused."""
        if query.lstrip().lower().startswith("mutation"):
            raise ValueError("GithubStructureClient.graphql sends queries only")
        retries = 0
        while True:
            response = self.api.request(
                "POST", "graphql", payload={"query": query, "variables": dict(variables)}, write=False
            )
            body = _dict(response.body, "GraphQL response", "graphql")
            errors = body.get("errors")
            if not errors:
                return _dict(body.get("data"), "GraphQL data", "graphql")
            types = (
                {item.get("type") for item in errors if isinstance(item, dict)} if isinstance(errors, list) else set()
            )
            if "RATE_LIMITED" in types:
                limited = _rate_limit_wait(GithubResponse(429, response.headers, body), self.api.clock.now())
                wait = 60.0 if limited is None else limited
                if wait > MAX_RATE_LIMIT_WAIT or retries >= READ_RETRIES:
                    retry_at = format_timestamp(self.api.clock.now() + timedelta(seconds=wait))
                    raise GithubStructureError(
                        GITHUB_RATE_LIMITED, f"GitHub GraphQL rate limit; retry after {retry_at}", retry_at=retry_at
                    )
                self.api.clock.sleep(wait)
                retries += 1
                continue
            if "NOT_FOUND" in types:
                raise GithubStructureError(GITHUB_ACCESS_DENIED, "GitHub GraphQL could not read the repository")
            raise GithubStructureError(GITHUB_REQUEST_REJECTED, "GitHub GraphQL rejected the structure query")

    def probe(self, etags: Mapping[str, str | None]) -> ProbeResult:
        """One conditional list request per kind label; a 304 does not use the primary rate limit."""
        fresh: dict[str, str | None] = {}
        statuses: dict[str, int] = {}
        for label in KIND_LABELS.values():
            previous = etags.get(label)
            response = self.api.request(
                "GET",
                f"{self._base}/issues?labels={quote(label, safe='')}&state=all&sort=updated&direction=desc&per_page=1",
                ok=frozenset({200, 304}),
                headers={"If-None-Match": previous} if previous else None,
            )
            statuses[label] = response.status
            fresh[label] = response.headers.get("etag") or (previous if response.status == 304 else None)
        return ProbeResult(any(status != 304 for status in statuses.values()), fresh, statuses)

    def get_issue(self, number: int) -> IssueFacts:
        endpoint = f"{self._base}/issues/{_positive(number)}"
        return self._facts_from_rest(self.api.request("GET", endpoint).body, endpoint, number=number)

    def get_parent(self, number: int) -> RelatedIssue | None:
        endpoint = f"{self._base}/issues/{_positive(number)}/parent"
        response = self.api.request("GET", endpoint, ok=frozenset({200, 404}))
        return None if response.status == 404 else self._related_from_rest(response.body, endpoint)

    def list_sub_issues(self, number: int) -> tuple[RelatedIssue, ...]:
        return self._related_pages(f"{self._base}/issues/{_positive(number)}/sub_issues")

    def list_blocked_by(self, number: int) -> tuple[RelatedIssue, ...]:
        return self._related_pages(f"{self._base}/issues/{_positive(number)}/dependencies/blocked_by")

    def list_labels(self, number: int) -> tuple[str, ...]:
        endpoint = f"{self._base}/issues/{_positive(number)}/labels"
        return _names(self._pages(endpoint), "name", "label", endpoint)

    def label_exists(self, name: str) -> bool:
        endpoint = f"{self._base}/labels/{quote(name, safe='')}"
        return self.api.request("GET", endpoint, ok=frozenset({200, 404})).status == 200

    def current_login(self) -> str:
        body = _dict(self.api.request("GET", "user").body, "user", "user")
        return _text(body.get("login"), "login", "user")

    # Writes. Each is sent alone; an uncertain result is read back before it is reported as unknown.

    def create_issue(self, *, title: str, labels: Sequence[str]) -> IssueFacts:
        """Create a Scope Issue with its title and labels only; SpecDock keeps nothing in the body."""
        if not title.strip():
            raise ValueError("GitHub Issue title must be nonempty")
        endpoint = f"{self._base}/issues"
        try:
            response = self.api.request(
                "POST", endpoint, payload={"title": title, "labels": list(labels)}, ok=frozenset({201})
            )
            return self._facts_from_rest(response.body, endpoint, number=None)
        except GithubStructureError as error:
            if not error.uncertain and error.code != GITHUB_RESPONSE_INVALID:
                raise
            raise GithubStructureError(
                GITHUB_CREATE_IDENTITY_UNKNOWN,
                "GitHub may have created the Issue but its number is unknown",
                uncertain=True,
                endpoint=endpoint,
            ) from error

    def update_issue(
        self,
        number: int,
        *,
        title: str | None = None,
        state: Literal["open", "closed"] | None = None,
        state_reason: Literal["completed", "not_planned", "reopened"] | None = None,
    ) -> IssueFacts:
        payload = {
            key: value
            for key, value in (("title", title), ("state", state), ("state_reason", state_reason))
            if value is not None
        }
        if not payload:
            raise ValueError("an Issue update needs a title or state")
        endpoint = f"{self._base}/issues/{_positive(number)}"

        def confirmed() -> IssueFacts | None:
            observed = self.get_issue(number)
            matches = (title is None or observed.title == title) and (state is None or observed.state == state)
            return observed if matches else None

        return self._write(
            "PATCH",
            endpoint,
            payload,
            ok=frozenset({200}),
            decode=lambda response: self._facts_from_rest(response.body, endpoint, number=number),
            confirm=confirmed,
        )

    def add_sub_issue(self, parent: int, *, child: int, child_id: int, replace_parent: bool = False) -> None:
        self._write(
            "POST",
            f"{self._base}/issues/{_positive(parent)}/sub_issues",
            {"sub_issue_id": _positive(child_id), "replace_parent": replace_parent},
            ok=frozenset({200, 201}),
            decode=_done,
            confirm=lambda: self._parent_is(child, parent) or None,
        )

    def remove_sub_issue(self, parent: int, *, child: int, child_id: int) -> None:
        def detached() -> bool | None:
            self.get_issue(child)  # a 404 here means no access, not an absent relation
            return (not self._parent_is(child, parent)) or None

        self._write(
            "DELETE",
            f"{self._base}/issues/{_positive(parent)}/sub_issue",
            {"sub_issue_id": _positive(child_id)},
            ok=frozenset({200}),
            decode=_done,
            confirm=detached,
            absent_ok=True,
        )

    def add_blocked_by(self, number: int, *, blocker: int, blocker_id: int) -> None:
        self._write(
            "POST",
            f"{self._base}/issues/{_positive(number)}/dependencies/blocked_by",
            {"issue_id": _positive(blocker_id)},
            ok=frozenset({200, 201}),
            decode=_done,
            confirm=lambda: self._blocked_by(number, blocker) or None,
        )

    def remove_blocked_by(self, number: int, *, blocker: int, blocker_id: int) -> None:
        self._write(
            "DELETE",
            f"{self._base}/issues/{_positive(number)}/dependencies/blocked_by/{_positive(blocker_id)}",
            None,
            ok=frozenset({200, 204}),
            decode=_done,
            confirm=lambda: (not self._blocked_by(number, blocker)) or None,
            absent_ok=True,
        )

    def create_label(self, definition: LabelDefinition) -> None:
        endpoint = f"{self._base}/labels"

        def accepted(response: GithubResponse) -> bool:
            if response.status == 422 and not _already_exists(response.body):
                raise GithubStructureError(
                    GITHUB_REQUEST_REJECTED, "GitHub rejected the label definition", status=422, endpoint=endpoint
                )
            return True

        self._write(
            "POST",
            endpoint,
            {"name": definition.name, "color": definition.color, "description": definition.description},
            ok=frozenset({201, 422}),
            decode=accepted,
            confirm=lambda: self.label_exists(definition.name) or None,
        )

    def add_labels(self, number: int, labels: Sequence[str]) -> tuple[str, ...]:
        endpoint = f"{self._base}/issues/{_positive(number)}/labels"
        wanted = set(labels)
        return self._write(
            "POST",
            endpoint,
            {"labels": list(labels)},
            ok=frozenset({200}),
            decode=lambda response: _names(response.body, "name", "label", endpoint),
            confirm=lambda: self._labels_if(number, lambda current: wanted <= set(current)),
        )

    def remove_label(self, number: int, name: str) -> None:
        self._write(
            "DELETE",
            f"{self._base}/issues/{_positive(number)}/labels/{quote(name, safe='')}",
            None,
            ok=frozenset({200}),
            decode=_done,
            confirm=lambda: self._labels_if(number, lambda current: name not in current),
            absent_ok=True,
        )

    def add_assignees(self, number: int, logins: Sequence[str]) -> None:
        wanted = set(logins)
        self._write(
            "POST",
            f"{self._base}/issues/{_positive(number)}/assignees",
            {"assignees": list(logins)},
            ok=frozenset({200, 201}),
            decode=_done,
            confirm=lambda: (wanted <= set(self.get_issue(number).assignees)) or None,
        )

    def _write(
        self,
        method: Method,
        endpoint: str,
        payload: object | None,
        *,
        ok: frozenset[int],
        decode: Callable[[GithubResponse], _T],
        confirm: Callable[[], _T | None],
        absent_ok: bool = False,
    ) -> _T:
        """Send one write. Read back when the answer is uncertain, unreadable, or a removal answers 404."""
        try:
            response = self.api.request(method, endpoint, payload=payload, ok=ok | ({404} if absent_ok else set()))
            if absent_ok and response.status == 404:
                observed = confirm()
                if observed is None:
                    raise GithubStructureError(
                        GITHUB_ACCESS_DENIED,
                        "GitHub could not find the relation to remove",
                        status=404,
                        endpoint=endpoint,
                    )
                return observed
            return decode(response)
        except GithubStructureError as error:
            # A 2xx write whose body cannot be read may still have applied, like a lost answer.
            if not error.uncertain and error.code != GITHUB_RESPONSE_INVALID:
                raise
            try:
                observed = confirm()
            except GithubStructureError as observation:
                raise GithubStructureError(
                    GITHUB_EFFECT_UNKNOWN, "the write result could not be read back", uncertain=True, endpoint=endpoint
                ) from observation
            if observed is None:
                raise GithubStructureError(
                    GITHUB_EFFECT_UNKNOWN,
                    "the write result is not visible on GitHub",
                    uncertain=True,
                    endpoint=endpoint,
                ) from error
            return observed

    def _parent_is(self, child: int, parent: int) -> bool:
        found = self.get_parent(child)
        return found is not None and found.repository == self.repository.slug and found.number == parent

    def _blocked_by(self, number: int, blocker: int) -> bool:
        return any(
            item.repository == self.repository.slug and item.number == blocker for item in self.list_blocked_by(number)
        )

    def _labels_if(self, number: int, accept: Callable[[tuple[str, ...]], bool]) -> tuple[str, ...] | None:
        current = self.get_issue(number).labels
        return current if accept(current) else None

    # Internals.

    @property
    def _base(self) -> str:
        return f"repos/{self.repository.slug}"

    def _pages(self, endpoint: str) -> list[object]:
        items: list[object] = []
        page = 1
        while True:
            response = self.api.request("GET", f"{endpoint}?per_page={REST_PAGE_SIZE}&page={page}")
            batch = _list(response.body, "list", endpoint)
            items.extend(batch)
            if len(batch) < REST_PAGE_SIZE:
                return items
            page += 1

    def _related_pages(self, endpoint: str) -> tuple[RelatedIssue, ...]:
        return tuple(self._related_from_rest(item, endpoint) for item in self._pages(endpoint))

    def _related_from_rest(self, payload: object, endpoint: str) -> RelatedIssue:
        item = _dict(payload, "Issue", endpoint)
        return RelatedIssue(
            _int(item.get("number"), "number", endpoint),
            _repository_of_url(item.get("repository_url"), endpoint),
            _text(item.get("title"), "title", endpoint),
            _state(item.get("state"), "state", endpoint),
        )

    def _facts_from_rest(self, payload: object, endpoint: str, *, number: int | None) -> IssueFacts:
        item = _dict(payload, "Issue", endpoint)
        found = _int(item.get("number"), "number", endpoint)
        if (number is not None and found != number) or "pull_request" in item:
            raise _invalid("GitHub returned a different Issue or a pull request", endpoint)
        if _repository_of_url(item.get("repository_url"), endpoint) != self.repository.slug:
            raise _invalid("GitHub returned an Issue of another repository", endpoint)
        return IssueFacts(
            number=found,
            database_id=_int(item.get("id"), "id", endpoint),
            title=_text(item.get("title"), "title", endpoint),
            state=_state(item.get("state"), "state", endpoint),
            state_reason=_optional_lower(item.get("state_reason"), "state_reason", endpoint),
            labels=_names(item.get("labels"), "name", "label", endpoint),
            assignees=_names(item.get("assignees"), "login", "assignee", endpoint),
            updated_at=_text(item.get("updated_at"), "updated_at", endpoint),
            url=_text(item.get("html_url"), "html_url", endpoint),
            created_at=_text(item.get("created_at"), "created_at", endpoint),
            closed_at=_optional_text(item.get("closed_at"), "closed_at", endpoint),
        )

    def _fetched_from_graphql(self, node: dict[str, object]) -> FetchedIssue:
        endpoint = "graphql"
        number = _int(node.get("number"), "number", endpoint)
        labels_block = _dict(node.get("labels"), "labels", endpoint)
        labels = _names(labels_block.get("nodes"), "name", "label", endpoint)
        if type(labels_block.get("totalCount")) is int and cast("int", labels_block["totalCount"]) > len(labels):
            labels = self.list_labels(number)
        facts = IssueFacts(
            number=number,
            database_id=_int(node.get("databaseId"), "databaseId", endpoint),
            title=_text(node.get("title"), "title", endpoint),
            state=_state(node.get("state"), "state", endpoint),
            state_reason=_optional_lower(node.get("stateReason"), "stateReason", endpoint),
            labels=labels,
            assignees=_names(
                _dict(node.get("assignees"), "assignees", endpoint).get("nodes"), "login", "assignee", endpoint
            ),
            updated_at=_text(node.get("updatedAt"), "updatedAt", endpoint),
            url=_text(node.get("url"), "url", endpoint),
            created_at=_text(node.get("createdAt"), "createdAt", endpoint),
            closed_at=_optional_text(node.get("closedAt"), "closedAt", endpoint),
        )
        parent = None if node.get("parent") is None else self._related_from_graphql(node.get("parent"))
        children = self._connection(node.get("subIssues"), "subIssues")
        sub_issues = self.list_sub_issues(number) if children is None else children
        blockers = self._connection(node.get("blockedBy"), "blockedBy")
        blocked_by = self.list_blocked_by(number) if blockers is None else blockers
        return FetchedIssue(facts, parent, sub_issues, blocked_by)

    def _connection(self, value: object, what: str) -> tuple[RelatedIssue, ...] | None:
        """Return the related Issues, or None when totalCount says the page was truncated."""
        block = _dict(value, what, "graphql")
        items = tuple(self._related_from_graphql(item) for item in _list(block.get("nodes"), what, "graphql"))
        total = block.get("totalCount")
        if type(total) is not int:
            raise _invalid(f"GitHub {what}.totalCount is missing", "graphql")
        return None if cast("int", total) > len(items) else items

    def _related_from_graphql(self, value: object) -> RelatedIssue:
        item = _dict(value, "related Issue", "graphql")
        repository = _dict(item.get("repository"), "repository", "graphql")
        state = item.get("state")
        return RelatedIssue(
            _int(item.get("number"), "number", "graphql"),
            _text(repository.get("nameWithOwner"), "nameWithOwner", "graphql").lower(),
            _optional_text(item.get("title"), "title", "graphql"),
            None if state is None else _state(state, "state", "graphql"),
        )


def _done(_response: GithubResponse) -> bool:
    return True


def repository_for_checkout(root: Path, *, timeout: float) -> GithubRepository:
    """The repository whose Issues hold this checkout's structure: the credential-free origin remote."""
    from spec_dock.runtime.infra.github_remote import github_publication_repository

    return GithubRepository.parse(github_publication_repository(root, timeout=timeout))


def _already_exists(body: object) -> bool:
    errors = body.get("errors") if isinstance(body, dict) else None
    return isinstance(errors, list) and any(
        isinstance(item, dict) and item.get("code") == "already_exists" for item in errors
    )


def _positive(number: int) -> int:
    if type(number) is not int or number <= 0:
        raise ValueError("GitHub Issue number must be positive")
    return number
