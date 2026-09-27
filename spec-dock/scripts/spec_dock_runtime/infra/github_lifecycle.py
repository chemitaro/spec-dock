"""Typed, repository-bound GitHub Issue lifecycle over the REST API."""

from __future__ import annotations

from collections.abc import Callable
import json
import re
import subprocess
from typing import TYPE_CHECKING, Literal, cast

from spec_dock_runtime.domain.lifecycle import ObservedState, observe_github_state
from spec_dock_runtime.infra.contracts import GithubIssueRecord

if TYPE_CHECKING:
    from pathlib import Path

_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_STATUS = re.compile(r"^HTTP/\S+\s+([0-9]{3})(?:\s|$)")
_Run = Callable[..., subprocess.CompletedProcess[str]]


class RemoteIssueError(RuntimeError):
    """A sanitized gateway failure; six means the remote effect is uncertain."""

    def __init__(self, code: str, *, uncertain: bool = False) -> None:
        self.code = code
        self.uncertain = uncertain
        self.exit_code = 6 if uncertain else 5
        super().__init__(code)


def _repository_slug(value: str) -> str:
    if not _REPOSITORY.fullmatch(value) or ".." in value or value.startswith("-"):
        raise ValueError("GitHub repository must be an explicit owner/name")
    return value


def _decode_response(
    response: subprocess.CompletedProcess[str], *, mutation: bool, expect_array: bool = False
) -> dict[str, object] | list[object]:
    raw = response.stdout or ""
    header, marker, body = raw.replace("\r\n", "\n").partition("\n\n")
    matched = _STATUS.match(header.splitlines()[0] if header else "")
    if not marker or matched is None:
        raise RemoteIssueError("GITHUB_RESPONSE_UNVERIFIED", uncertain=mutation)
    status = int(matched.group(1))
    if status in (401, 403, 404):
        raise RemoteIssueError("GITHUB_ACCESS_DENIED")
    if status in (400, 410, 422):
        raise RemoteIssueError("GITHUB_REQUEST_REJECTED")
    if response.returncode != 0 or status >= 400:
        raise RemoteIssueError("GITHUB_REMOTE_UNAVAILABLE", uncertain=mutation)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        raise RemoteIssueError("GITHUB_RESPONSE_INVALID", uncertain=mutation) from error
    if not isinstance(payload, list if expect_array else dict):
        raise RemoteIssueError("GITHUB_RESPONSE_INVALID", uncertain=mutation)
    return payload


def _record(payload: dict[str, object], *, repository: str, number: int | None) -> GithubIssueRecord:
    raw_number = payload.get("number")
    if not isinstance(raw_number, int) or isinstance(raw_number, bool) or raw_number <= 0:
        raise RemoteIssueError("GITHUB_ISSUE_ID_MISMATCH")
    if number is not None and raw_number != number:
        raise RemoteIssueError("GITHUB_ISSUE_ID_MISMATCH")
    if "pull_request" in payload:
        raise RemoteIssueError("GITHUB_PULL_REQUEST_REJECTED")
    expected_url = f"https://api.github.com/repos/{repository}"
    repository_url = payload.get("repository_url")
    if not isinstance(repository_url, str) or repository_url.lower() != expected_url.lower():
        raise RemoteIssueError("GITHUB_FOREIGN_REPOSITORY")
    url = payload.get("html_url")
    if not isinstance(url, str) or url.lower() != f"https://github.com/{repository}/issues/{raw_number}".lower():
        raise RemoteIssueError("GITHUB_ISSUE_URL_MISMATCH")
    raw_state = payload.get("state")
    reason = payload.get("state_reason")
    title = payload.get("title")
    updated_at = payload.get("updated_at")
    if (
        not isinstance(raw_state, str)
        or (reason is not None and not isinstance(reason, str))
        or not isinstance(title, str)
        or not isinstance(updated_at, str)
    ):
        raise RemoteIssueError("GITHUB_RESPONSE_INVALID")
    return GithubIssueRecord(
        raw_number,
        repository,
        title,
        observe_github_state(raw_state, reason),
        raw_state,
        reason,
        updated_at,
        url,
    )


class GithubIssueGateway:
    """Send only minimal Issue fields to one explicit GitHub repository."""

    def __init__(self, *, runner: _Run = subprocess.run, timeout: float = 30.0) -> None:
        if timeout <= 0:
            raise ValueError("GitHub timeout must be positive")
        self._runner = runner
        self._timeout = timeout

    def _api(
        self,
        repo_root: Path,
        *,
        method: Literal["GET", "POST", "PATCH"],
        endpoint: str,
        payload: dict[str, str] | None = None,
        expect_array: bool = False,
    ) -> dict[str, object] | list[object]:
        argv = ["gh", "api", "--hostname", "github.com", "--include", "--method", method, endpoint]
        if payload is not None:
            argv.extend(["--input", "-"])
        try:
            response = self._runner(
                argv,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=self._timeout,
                input=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            )
        except subprocess.TimeoutExpired as error:
            raise RemoteIssueError("GITHUB_TIMEOUT", uncertain=method != "GET") from error
        except (FileNotFoundError, PermissionError, NotADirectoryError) as error:
            raise RemoteIssueError("GITHUB_PROCESS_NOT_STARTED") from error
        except OSError as error:
            raise RemoteIssueError("GITHUB_PROCESS_ERROR", uncertain=method != "GET") from error
        return _decode_response(response, mutation=method != "GET", expect_array=expect_array)

    def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
        repository = _repository_slug(repository)
        if number <= 0:
            raise ValueError("GitHub Issue number must be positive")
        payload = cast(
            "dict[str, object]", self._api(repo_root, method="GET", endpoint=f"repos/{repository}/issues/{number}")
        )
        return _record(payload, repository=repository, number=number)

    def create(self, repo_root: Path, repository: str, *, title: str, body: str) -> GithubIssueRecord:
        repository = _repository_slug(repository)
        if not title.strip():
            raise ValueError("GitHub Issue title must be nonempty")
        payload = cast(
            "dict[str, object]",
            self._api(
                repo_root,
                method="POST",
                endpoint=f"repos/{repository}/issues",
                payload={"title": title, "body": body},
            ),
        )
        try:
            return _record(payload, repository=repository, number=None)
        except RemoteIssueError as error:
            raise RemoteIssueError("GITHUB_CREATE_IDENTITY_UNKNOWN", uncertain=True) from error

    def find_by_marker(self, repo_root: Path, repository: str, marker: str) -> tuple[GithubIssueRecord, ...]:
        """Scan every Issue page; zero matches is diagnostic, never proof to retry a POST."""
        repository = _repository_slug(repository)
        if not marker.startswith("<!-- spec-dock-operation:") or not marker.endswith(" -->"):
            raise ValueError("invalid GitHub operation marker")
        matches: list[GithubIssueRecord] = []
        page = 1
        while True:
            payload = cast(
                "list[object]",
                self._api(
                    repo_root,
                    method="GET",
                    endpoint=f"repos/{repository}/issues?state=all&per_page=100&page={page}",
                    expect_array=True,
                ),
            )
            for item in payload:
                if not isinstance(item, dict):
                    raise RemoteIssueError("GITHUB_RESPONSE_INVALID")
                if "pull_request" in item:
                    continue
                body = item.get("body")
                if body is None:
                    continue
                if not isinstance(body, str):
                    raise RemoteIssueError("GITHUB_RESPONSE_INVALID")
                if marker in body:
                    matches.append(_record(item, repository=repository, number=None))
            if len(payload) < 100:
                return tuple(matches)
            page += 1

    def set_state(
        self,
        repo_root: Path,
        repository: str,
        number: int,
        *,
        state: Literal["open", "closed"],
        reason: Literal["completed", "not_planned"] | None,
    ) -> GithubIssueRecord:
        if (state == "closed") != (reason is not None):
            raise ValueError("closed requires completed or not_planned; open requires no reason")
        current = self.get(repo_root, repository, number)
        desired: ObservedState = "open" if state == "open" else "completed" if reason == "completed" else "not-planned"
        if current.state == desired:
            return current
        if current.raw_state.lower() == state:
            raise RemoteIssueError("GITHUB_REASON_CHANGE_REQUIRES_REOPEN")
        data: dict[str, str] = {"state": state, "state_reason": reason or "reopened"}
        try:
            self._api(
                repo_root,
                method="PATCH",
                endpoint=f"repos/{_repository_slug(repository)}/issues/{number}",
                payload=data,
            )
        except RemoteIssueError as error:
            if not error.uncertain:
                raise
            try:
                observed = self.get(repo_root, repository, number)
            except RemoteIssueError as observation_error:
                raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True) from observation_error
            if observed.state == desired:
                return observed
            raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True) from error
        try:
            observed = self.get(repo_root, repository, number)
        except RemoteIssueError as error:
            raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True) from error
        if observed.state != desired:
            raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True)
        return observed
