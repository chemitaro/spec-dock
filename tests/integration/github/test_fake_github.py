"""The shared fake GitHub answers like `gh api`, so later Issues can trust its request records."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from tests.support.fake_github import FakeGithub, install_fake_gh

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

GH = ["gh", "api", "--hostname", "github.com", "--include", "--method"]


def _status(stdout: str) -> int:
    return int(stdout.split("\r\n", 1)[0].split()[1])


def _body(stdout: str) -> object:
    text = stdout.split("\r\n\r\n", 1)[1]
    return json.loads(text) if text else None


def test_conditional_list_returns_304_with_exit_one_until_the_top_issue_changes() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", slug="core")
    endpoint = "repos/example/repo/issues?labels=spec-dock%3Aepic&state=all&sort=updated&direction=desc&per_page=1"
    first = fake([*GH, "GET", endpoint])
    etag = first.stdout.split("ETag: ", 1)[1].split("\r\n", 1)[0]
    assert first.returncode == 0 and _status(first.stdout) == 200
    again = fake([*GH, "GET", endpoint, "-H", f"If-None-Match: {etag}"])
    assert again.returncode == 1 and again.stdout.startswith("HTTP/2.0 304 Not Modified\r\n")
    fake.touch(epic.number)
    changed = fake([*GH, "GET", endpoint, "-H", f"If-None-Match: {etag}"])
    assert changed.returncode == 0 and _status(changed.stdout) == 200
    assert [request.status for request in fake.requests] == [200, 304, 200]
    assert len(fake.metered_requests()) == 2


def test_graphql_filters_labels_with_or_and_pages_with_cursors() -> None:
    fake = FakeGithub()
    for number in range(1, 6):
        fake.scope("issue" if number % 2 else "epic", slug=f"s{number}")
    fake.add_issue(title="Plain")
    fake.add_issue(labels=("spec-dock:issue",), pull_request=True)
    query = 'query { repository(owner: $owner, name: $name) { issues(first: 2, after: $after, labels: ["spec-dock:epic", "spec-dock:issue"]) { nodes { number } } } }'
    seen: list[int] = []
    after = None
    while True:
        payload = json.dumps({"query": query, "variables": {"owner": "example", "name": "repo", "after": after}})
        response = fake([*GH, "POST", "graphql", "--input", "-"], input=payload)
        issues = _body(response.stdout)["data"]["repository"]["issues"]  # type: ignore[index]
        seen.extend(node["number"] for node in issues["nodes"])
        if not issues["pageInfo"]["hasNextPage"]:
            break
        after = issues["pageInfo"]["endCursor"]
    assert seen == [1, 2, 3, 4, 5] and len(fake.graphql_requests()) == 3


def test_relation_writes_take_issue_ids_and_reject_numbers() -> None:
    fake = FakeGithub()
    parent = fake.scope("epic", slug="core")
    child = fake.scope("issue", slug="leaf")
    assert child.id != child.number
    by_number = fake(
        [*GH, "POST", f"repos/example/repo/issues/{parent.number}/sub_issues", "--input", "-"],
        input=json.dumps({"sub_issue_id": child.number}),
    )
    assert _status(by_number.stdout) == 404 and child.parent is None
    by_id = fake(
        [*GH, "POST", f"repos/example/repo/issues/{parent.number}/sub_issues", "--input", "-"],
        input=json.dumps({"sub_issue_id": child.id}),
    )
    assert _status(by_id.stdout) == 201 and child.parent == ["example/repo", parent.number]
    missing = fake([*GH, "GET", f"repos/example/repo/issues/{parent.number}/parent"])
    assert _status(missing.stdout) == 404


def test_injected_rate_limit_and_timeout_are_recorded() -> None:
    fake = FakeGithub()
    fake.inject(status=403, headers={"retry-after": "7"}, body={"message": "secondary rate limit"}, method="GET")
    fake.inject(timeout=True, method="PATCH")
    limited = fake([*GH, "GET", "user"])
    assert _status(limited.stdout) == 403 and "retry-after: 7" in limited.stdout
    assert _status(fake([*GH, "GET", "user"]).stdout) == 200
    issue = fake.scope("issue", slug="leaf")
    try:
        fake([*GH, "PATCH", f"repos/example/repo/issues/{issue.number}", "--input", "-"], input='{"title":"x"}')
    except subprocess.TimeoutExpired:
        pass
    else:
        raise AssertionError("timeout was not injected")
    assert [request.status for request in fake.requests] == [403, 200, 0]


def test_path_executable_persists_the_model_and_requests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", slug="leaf", title="Before")
    handle = install_fake_gh(tmp_path, monkeypatch, fake)
    completed = subprocess.run(
        [
            "gh",
            "api",
            "--hostname",
            "github.com",
            "--include",
            "--method",
            "PATCH",
            f"repos/example/repo/issues/{issue.number}",
            "--input",
            "-",
        ],
        input='{"title":"日本語の題名"}',
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0 and _status(completed.stdout) == 200
    stored = handle.load()
    assert stored.issue(issue.number).title == "日本語の題名"
    assert [(request.method, request.payload) for request in stored.requests] == [("PATCH", {"title": "日本語の題名"})]
