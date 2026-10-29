"""GitHub structure calls through `gh api`, against the shared fake; no live network."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.github_structure import GithubApi, GithubStructureError
from tests.support.fake_github import FakeGithub

if TYPE_CHECKING:
    from pathlib import Path


def _api(fake: FakeGithub) -> GithubApi:
    return GithubApi(runner=fake, clock=fake.clock)


def test_status_comes_from_the_status_line_so_304_with_exit_one_is_an_answer() -> None:
    fake = FakeGithub()
    fake.scope("epic", title="core")
    api = _api(fake)
    endpoint = "repos/example/repo/issues?labels=spec-dock%3Aepic&state=all&sort=updated&direction=desc&per_page=1"
    first = api.request("GET", endpoint, ok=frozenset({200, 304}))
    assert first.status == 200 and isinstance(first.body, list) and first.headers["etag"].startswith('W/"')
    second = api.request("GET", endpoint, ok=frozenset({200, 304}), headers={"If-None-Match": first.headers["etag"]})
    assert second.status == 304 and second.body is None
    assert fake.requests[-1].headers == {"If-None-Match": first.headers["etag"]}


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (401, "GITHUB_ACCESS_DENIED"),
        (403, "GITHUB_ACCESS_DENIED"),
        (404, "GITHUB_ACCESS_DENIED"),
        (422, "GITHUB_REQUEST_REJECTED"),
        (400, "GITHUB_REQUEST_REJECTED"),
    ],
)
def test_unexpected_client_errors_keep_the_current_classification(status: int, code: str) -> None:
    fake = FakeGithub()
    fake.inject(status=status, body={"message": "no"})
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("GET", "user")
    assert (caught.value.code, caught.value.exit_code, caught.value.uncertain) == (code, 5, False)


def test_expected_404_is_a_normal_answer() -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", title="leaf")
    response = _api(fake).request("GET", f"repos/example/repo/issues/{issue.number}/parent", ok=frozenset({200, 404}))
    assert response.status == 404


def test_json_bodies_with_numbers_and_arrays_go_through_standard_input() -> None:
    fake = FakeGithub()
    parent = fake.scope("epic", title="core")
    child = fake.scope("issue", title="leaf")
    _api(fake).request(
        "POST",
        f"repos/example/repo/issues/{parent.number}/sub_issues",
        payload={"sub_issue_id": child.id, "replace_parent": False},
        ok=frozenset({201}),
    )
    assert fake.requests[-1].payload == {"sub_issue_id": child.id, "replace_parent": False}
    assert child.parent == ["example/repo", parent.number]


def test_missing_gh_and_unparseable_output_are_unavailable_for_reads() -> None:
    def missing(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("gh")

    with pytest.raises(GithubStructureError) as caught:
        GithubApi(runner=missing).request("GET", "user")
    assert caught.value.code == "GITHUB_UNAVAILABLE" and not caught.value.uncertain

    def garbage(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 1, "gh: something went wrong", "")

    with pytest.raises(GithubStructureError) as caught:
        GithubApi(runner=garbage).request("GET", "user")
    assert caught.value.code == "GITHUB_UNAVAILABLE"
    with pytest.raises(GithubStructureError) as caught:
        GithubApi(runner=garbage).request("PATCH", "repos/example/repo/issues/1", payload={"title": "x"})
    assert caught.value.code == "GITHUB_EFFECT_UNKNOWN" and caught.value.uncertain and caught.value.exit_code == 6


SECONDARY = {"message": "You have exceeded a secondary rate limit."}


@pytest.mark.parametrize(
    ("status", "headers", "body", "wait"),
    [
        (403, {"retry-after": "5"}, SECONDARY, 5.0),
        (
            429,
            {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1792973430"},
            {"message": "API rate limit exceeded"},
            30.0,
        ),
        (403, {}, SECONDARY, 60.0),
    ],
)
def test_rate_limited_reads_wait_as_documented_and_retry(
    status: int, headers: dict[str, str], body: object, wait: float
) -> None:
    fake = FakeGithub()  # clock starts at 2026-10-26T00:00:00Z = 1792972800
    fake.clock.advance(600)
    fake.inject(status=status, headers=headers, body=body)
    assert _api(fake).request("GET", "user").body == {"login": "fixture-user"}
    assert fake.clock.sleeps == [wait] and [request.status for request in fake.requests] == [status, 200]


def test_reads_stop_when_the_wait_exceeds_sixty_seconds_or_after_three_retries() -> None:
    fake = FakeGithub()
    fake.inject(status=403, headers={"retry-after": "120"}, body=SECONDARY)
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("GET", "user")
    assert caught.value.code == "GITHUB_RATE_LIMITED" and caught.value.retry_at == "2026-10-26T00:02:00Z"
    assert fake.clock.sleeps == [] and caught.value.exit_code == 5
    fake = FakeGithub()
    fake.inject(status=429, headers={"retry-after": "1"}, body=SECONDARY, times=4)
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("GET", "user")
    assert caught.value.code == "GITHUB_RATE_LIMITED" and len(fake.requests) == 4 and fake.clock.sleeps == [1, 1, 1]


def test_rate_limited_writes_stop_at_once_without_an_uncertain_effect() -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", title="Before")
    fake.inject(status=403, headers={"retry-after": "5"}, body=SECONDARY, method="PATCH")
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("PATCH", f"repos/example/repo/issues/{issue.number}", payload={"title": "After"})
    assert (caught.value.code, caught.value.uncertain) == ("GITHUB_RATE_LIMITED", False)
    assert caught.value.retry_at == "2026-10-26T00:00:05Z" and len(fake.requests) == 1 and issue.title == "Before"


def test_server_errors_retry_reads_with_backoff_and_mark_writes_uncertain() -> None:
    fake = FakeGithub()
    fake.inject(status=502, body={"message": "Bad Gateway"}, times=3)
    assert _api(fake).request("GET", "user").status == 200
    assert fake.clock.sleeps == [1, 2, 4]
    fake = FakeGithub()
    fake.inject(status=500, body={"message": "boom"}, times=4)
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("GET", "user")
    assert caught.value.code == "GITHUB_UNAVAILABLE" and len(fake.requests) == 4
    fake = FakeGithub()
    fake.inject(status=503, body={"message": "busy"})
    with pytest.raises(GithubStructureError) as caught:
        _api(fake).request("POST", "repos/example/repo/labels", payload={"name": "x"})
    assert (caught.value.code, caught.value.uncertain, len(fake.requests)) == ("GITHUB_EFFECT_UNKNOWN", True, 1)


def test_writes_in_one_command_are_at_least_one_second_apart() -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", title="leaf")
    api = _api(fake)
    endpoint = f"repos/example/repo/issues/{issue.number}"
    api.request("PATCH", endpoint, payload={"title": "one"})
    api.request("GET", endpoint)
    api.request("PATCH", endpoint, payload={"title": "two"})
    fake.clock.advance(5)
    api.request("PATCH", endpoint, payload={"title": "three"})
    writes = [request.at for request in fake.writes()]
    assert writes[1] - writes[0] >= 1.0 and fake.clock.sleeps == [1.0]
    assert writes[2] - writes[1] >= 5.0


def _client(fake: FakeGithub):
    from spec_dock.runtime.infra.github_structure import GithubRepository, GithubStructureClient

    return GithubStructureClient(GithubRepository.parse("example/repo"), _api(fake))


def test_repository_names_are_lowercase_and_validated() -> None:
    from spec_dock.runtime.infra.github_structure import GithubRepository

    parsed = GithubRepository.parse("Example/Repo")
    assert (parsed.slug, parsed.key) == ("example/repo", "github.com/example/repo")
    assert GithubRepository.parse("github.com/example/repo") == parsed
    for invalid in ("example", "example/repo/extra", "../repo", "example/..", "ghe.example/acme/repo", "a b/c"):
        with pytest.raises(ValueError):
            GithubRepository.parse(invalid)


def test_full_read_pages_through_all_kind_labelled_issues_with_one_query_per_page() -> None:
    fake = FakeGithub()
    for number in range(1, 206):
        fake.scope(("initiative", "epic", "issue")[number % 3], title=f"s{number}")
    fake.add_issue(title="Not a Scope")
    fetched = _client(fake).fetch_structure()
    assert [issue.facts.number for issue in fetched] == list(range(1, 206))
    graphql = fake.graphql_requests()
    assert len(graphql) == 3 and [request.payload["variables"]["after"] for request in graphql] == [None, "100", "200"]  # type: ignore[index]
    query = graphql[0].payload["query"]  # type: ignore[index]
    assert '"spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"' in query
    assert "blockedBy(first: 100) { totalCount nodes { number title state repository { nameWithOwner } } }" in query
    assert "labels(first: 20) { totalCount nodes { name } }" in query
    assert _client(fake).last_graphql_cost is None
    client = _client(fake)
    client.fetch_structure()
    assert client.last_graphql_cost == 3


def test_full_read_completes_overflowing_relations_and_labels_with_serial_rest_reads() -> None:
    fake = FakeGithub(relation_limit=2, label_limit=2)
    epic = fake.scope("epic", title="core", labels=("a", "b"))
    children = [fake.scope("issue", title=f"c{index}", parent=epic.number) for index in range(3)]
    plain = [fake.add_issue(title=f"Plain {index}", state="closed") for index in range(3)]
    for blocker in plain:
        fake.block(children[0].number, by=blocker.number)
    fake.add_foreign_issue("other/repo", 9, title="Away")
    fake.set_foreign_child(epic.number, "other/repo", 9)
    by_number = {issue.facts.number: issue for issue in _client(fake).fetch_structure()}
    parent = by_number[epic.number]
    assert [child.number for child in parent.sub_issues] == [child.number for child in children] + [9]
    assert parent.sub_issues[-1].repository == "other/repo"
    assert set(parent.facts.labels) == {"spec-dock:epic", "a", "b"}
    first = by_number[children[0].number]
    assert [(item.number, item.state) for item in first.blocked_by] == [(item.number, "closed") for item in plain]
    assert first.parent is not None and (first.parent.number, first.parent.repository) == (epic.number, "example/repo")
    rest = [request.endpoint for request in fake.requests if request.endpoint != "graphql"]
    assert rest == [
        f"repos/example/repo/issues/{epic.number}/labels?per_page=100&page=1",
        f"repos/example/repo/issues/{epic.number}/sub_issues?per_page=100&page=1",
        f"repos/example/repo/issues/{children[0].number}/dependencies/blocked_by?per_page=100&page=1",
    ]


def test_graphql_states_are_normalized_like_rest() -> None:
    fake = FakeGithub()
    fake.scope("issue", title="dropped", state="closed", state_reason="not_planned")
    (issue,) = _client(fake).fetch_structure()
    assert (issue.facts.state, issue.facts.state_reason) == ("closed", "not_planned")


@pytest.mark.parametrize(
    ("errors", "code"),
    [
        ([{"type": "NOT_FOUND", "message": "missing"}], "GITHUB_ACCESS_DENIED"),
        ([{"message": "Field 'x' doesn't exist"}], "GITHUB_REQUEST_REJECTED"),
    ],
)
def test_graphql_errors_fail_without_partial_data(errors: list[dict[str, str]], code: str) -> None:
    fake = FakeGithub()
    fake.inject(status=200, body={"data": None, "errors": errors}, method="POST")
    with pytest.raises(GithubStructureError) as caught:
        _client(fake).fetch_structure()
    assert caught.value.code == code


def test_graphql_rate_limit_errors_wait_and_retry() -> None:
    fake = FakeGithub()
    fake.scope("issue", title="leaf")
    fake.inject(
        status=200, body={"data": None, "errors": [{"type": "RATE_LIMITED", "message": "API rate limit exceeded"}]}
    )
    assert len(_client(fake).fetch_structure()) == 1
    assert fake.clock.sleeps == [60.0]


def test_a_graphql_rate_limit_with_a_zero_wait_does_not_wait_a_minute() -> None:
    fake = FakeGithub()
    fake.scope("issue", title="leaf")
    fake.inject(
        status=200,
        headers={"retry-after": "0"},
        body={"data": None, "errors": [{"type": "RATE_LIMITED", "message": "API rate limit exceeded"}]},
    )
    assert len(_client(fake).fetch_structure()) == 1
    assert fake.clock.sleeps == [0.0]


def test_probe_sends_three_conditional_requests_and_reports_changes() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", title="core")
    client = _client(fake)
    first = client.probe({})
    assert first.changed is True and set(first.etags) == {"spec-dock:initiative", "spec-dock:epic", "spec-dock:issue"}
    assert all(value for value in first.etags.values()) and len(fake.requests) == 3
    second = client.probe(first.etags)
    assert second.changed is False and second.etags == first.etags
    assert [request.status for request in fake.requests[3:]] == [304, 304, 304]
    assert all(
        request.headers["If-None-Match"]
        == first.etags[request.endpoint.split("labels=")[1].split("&")[0].replace("%3A", ":")]
        for request in fake.requests[3:]
    )
    fake.touch(epic.number)
    third = client.probe(second.etags)
    assert third.changed is True and third.etags["spec-dock:epic"] != first.etags["spec-dock:epic"]
    assert third.statuses == {"spec-dock:initiative": 304, "spec-dock:epic": 200, "spec-dock:issue": 304}


def test_relation_writes_send_issue_ids_not_numbers() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", title="core")
    other = fake.scope("epic", title="spare")
    leaf = fake.scope("issue", title="leaf")
    blocker = fake.add_issue(title="Vendor")
    client = _client(fake)
    client.add_sub_issue(epic.number, child=leaf.number, child_id=leaf.id)
    client.add_sub_issue(other.number, child=leaf.number, child_id=leaf.id, replace_parent=True)
    client.remove_sub_issue(other.number, child=leaf.number, child_id=leaf.id)
    client.add_blocked_by(leaf.number, blocker=blocker.number, blocker_id=blocker.id)
    client.remove_blocked_by(leaf.number, blocker=blocker.number, blocker_id=blocker.id)
    writes = [(request.method, request.endpoint, request.payload) for request in fake.writes()]
    assert writes == [
        (
            "POST",
            f"repos/example/repo/issues/{epic.number}/sub_issues",
            {"sub_issue_id": leaf.id, "replace_parent": False},
        ),
        (
            "POST",
            f"repos/example/repo/issues/{other.number}/sub_issues",
            {"sub_issue_id": leaf.id, "replace_parent": True},
        ),
        ("DELETE", f"repos/example/repo/issues/{other.number}/sub_issue", {"sub_issue_id": leaf.id}),
        ("POST", f"repos/example/repo/issues/{leaf.number}/dependencies/blocked_by", {"issue_id": blocker.id}),
        ("DELETE", f"repos/example/repo/issues/{leaf.number}/dependencies/blocked_by/{blocker.id}", None),
    ]
    assert leaf.id != leaf.number and blocker.id != blocker.number
    assert leaf.parent is None and leaf.blocked_by == []


def test_issue_label_and_assignee_writes_return_or_confirm_github_state() -> None:
    from spec_dock.runtime.domain.canonical_structure import LABEL_DEFINITIONS

    fake = FakeGithub()
    client = _client(fake)
    created = client.create_issue(title="計画", labels=["spec-dock:initiative"])
    assert created.labels == ("spec-dock:initiative",) and created.title == "計画"
    assert fake.writes()[0].payload == {"title": "計画", "labels": ["spec-dock:initiative"]}
    renamed = client.update_issue(created.number, title="Plan")
    assert renamed.title == "Plan" and fake.writes()[-1].payload == {"title": "Plan"}
    closed = client.update_issue(created.number, state="closed", state_reason="completed")
    assert (closed.state, closed.state_reason) == ("closed", "completed")
    client.create_label(LABEL_DEFINITIONS[3])
    client.create_label(LABEL_DEFINITIONS[3])
    assert fake.labels["spec-dock:in-progress"]["color"] == LABEL_DEFINITIONS[3].color
    assert client.label_exists("spec-dock:in-progress") and not client.label_exists("missing:label")
    assert "spec-dock:in-progress" in client.add_labels(created.number, ["spec-dock:in-progress"])
    client.remove_label(created.number, "spec-dock:in-progress")
    client.remove_label(created.number, "spec-dock:in-progress")
    client.add_assignees(created.number, ["fixture-user"])
    assert fake.issue(created.number).assignees == ["fixture-user"] and client.current_login() == "fixture-user"


def test_parent_404_means_no_parent_and_other_reads_keep_their_meaning() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", title="core")
    leaf = fake.scope("issue", title="leaf", parent=epic.number)
    client = _client(fake)
    assert client.get_parent(epic.number) is None
    parent = client.get_parent(leaf.number)
    assert parent is not None and (parent.number, parent.repository) == (epic.number, "example/repo")
    with pytest.raises(GithubStructureError) as caught:
        client.get_issue(999)
    assert caught.value.code == "GITHUB_ACCESS_DENIED"


def test_uncertain_writes_are_confirmed_by_reading_back() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", title="core")
    leaf = fake.scope("issue", title="Before")
    client = _client(fake)
    fake.inject(status=502, body={"message": "lost"}, method="POST", endpoint="sub_issues", apply=True)
    client.add_sub_issue(epic.number, child=leaf.number, child_id=leaf.id)
    assert [(request.method, request.status) for request in fake.requests] == [("POST", 502), ("GET", 200)]
    fake.inject(timeout=True, method="PATCH")
    with pytest.raises(GithubStructureError) as caught:
        client.update_issue(leaf.number, title="After")
    assert (caught.value.code, caught.value.uncertain, caught.value.exit_code) == ("GITHUB_EFFECT_UNKNOWN", True, 6)
    fake.inject(timeout=True, method="PATCH", apply=True)
    assert client.update_issue(leaf.number, title="After").title == "After"
    fake.inject(status=502, body={"message": "lost"}, method="POST", endpoint="repos/example/repo/issues")
    with pytest.raises(GithubStructureError) as caught:
        client.create_issue(title="New", labels=[])
    assert (caught.value.code, caught.value.uncertain) == ("GITHUB_CREATE_IDENTITY_UNKNOWN", True)


def test_repository_for_a_checkout_comes_from_the_origin_remote(tmp_path: Path) -> None:
    from spec_dock.runtime.infra.github_structure import repository_for_checkout

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "remote", "add", "origin", "https://github.com/Example/Repo.git"], check=True
    )
    assert repository_for_checkout(tmp_path, timeout=10).key == "github.com/example/repo"


@pytest.mark.parametrize("body", ["not json", {"unexpected": "shape"}])
def test_a_write_answered_with_an_unreadable_body_is_confirmed_by_reading_back(body: object) -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", title="Before")
    client = _client(fake)
    fake.inject(status=200, body=body, method="PATCH", apply=True)
    assert client.update_issue(issue.number, title="After").title == "After"
    fake.inject(status=200, body=body, method="POST", endpoint="/labels", apply=True)
    assert "spec-dock:in-progress" in client.add_labels(issue.number, ["spec-dock:in-progress"])
    fake.inject(status=200, body=body, method="PATCH")
    with pytest.raises(GithubStructureError) as caught:
        client.update_issue(issue.number, title="Never applied")
    assert (caught.value.code, caught.value.uncertain) == ("GITHUB_EFFECT_UNKNOWN", True)


def test_removing_a_sub_issue_from_an_unreadable_issue_is_not_a_success() -> None:
    fake = FakeGithub()
    epic = fake.scope("epic", title="core")
    client = _client(fake)
    with pytest.raises(GithubStructureError) as caught:
        client.remove_sub_issue(epic.number, child=999, child_id=fake.issue_id(999))
    assert caught.value.code == "GITHUB_ACCESS_DENIED"
    leaf = fake.scope("issue", title="leaf")
    client.remove_sub_issue(epic.number, child=leaf.number, child_id=leaf.id)


@pytest.mark.parametrize("kind", ["pull request", "foreign"])
def test_issue_reads_and_writes_reject_pull_requests_and_foreign_issues(kind: str) -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", title="leaf")
    client = _client(fake)
    if kind == "pull request":
        issue.pull_request = True
    else:
        issue.repository = "other/repo"
        fake.issues["example/repo", issue.number] = issue
    for call in (
        lambda: client.get_issue(issue.number),
        lambda: client.update_issue(issue.number, title="x"),
    ):
        with pytest.raises(GithubStructureError) as caught:
            call()
        assert caught.value.code in ("GITHUB_RESPONSE_INVALID", "GITHUB_EFFECT_UNKNOWN")


def test_a_read_with_a_non_json_body_is_invalid() -> None:
    fake = FakeGithub()
    fake.inject(status=200, body="<html>", method="GET")
    with pytest.raises(GithubStructureError) as caught:
        _client(fake).current_login()
    assert caught.value.code == "GITHUB_RESPONSE_INVALID"


def test_graphql_on_the_client_refuses_mutations() -> None:
    with pytest.raises(ValueError):
        _client(FakeGithub()).graphql("mutation { addLabelsToLabelable }", {})


def test_the_full_read_query_uses_the_shared_kind_labels() -> None:
    from spec_dock.runtime.domain.canonical_structure import KIND_LABELS
    from spec_dock.runtime.infra.github_structure import FULL_READ_QUERY

    assert "labels: [" + ", ".join(f'"{label}"' for label in KIND_LABELS.values()) + "]" in FULL_READ_QUERY
    assert "body" not in FULL_READ_QUERY.split()


def test_rule_violations_from_the_fake_github_reach_the_snapshot_anomalies() -> None:
    from spec_dock.runtime.domain.canonical_structure import build_snapshot

    fake = FakeGithub()
    plan = fake.scope("initiative", title="plan")
    core = fake.scope("epic", title="core", parent=plan.number)
    leaf = fake.scope("issue", title="leaf", parent=core.number)
    double = fake.scope("epic", title="double", parent=plan.number, labels=("spec-dock:issue",))
    unmarked = fake.add_issue(title="No marker", body="Body", labels=("spec-dock:epic",))
    fake.set_parent(unmarked.number, plan.number)
    old_marker = fake.add_issue(
        title="Old marker", body="Text\r\n<!-- spec-dock:slug=old -->\r\nmore", labels=("spec-dock:issue",)
    )
    fake.set_parent(old_marker.number, core.number)
    under_issue = fake.scope("epic", title="under-issue", parent=leaf.number)
    moved = fake.scope("issue", title="moved", parent=core.number)
    loop_a = fake.scope("issue", title="loop-a", parent=core.number)
    loop_b = fake.scope("issue", title="loop-b", parent=core.number)
    fake.block(loop_a.number, by=loop_b.number)
    fake.block(loop_b.number, by=loop_a.number)
    plain = fake.add_issue(title="Plain blocker")
    fake.block(leaf.number, by=plain.number)
    fake.add_foreign_issue("other/repo", 5)
    fake.add_foreign_issue("other/repo", 6)
    fake.set_parent(moved.number, 6, parent_repository="other/repo")
    fake.block(leaf.number, by=5, repository="other/repo")
    snapshot = build_snapshot(
        "github.com/example/repo",
        _client(fake).fetch_structure(),
        fetched_at="2026-10-26T00:00:01Z",
        fetch_started_at="2026-10-26T00:00:00Z",
    )
    codes = {(item.number, item.code) for item in snapshot.anomalies}
    assert codes == {
        (double.number, "KIND_LABEL_MULTIPLE"),
        (under_issue.number, "PARENT_INVALID"),
        (loop_a.number, "DEPENDENCY_CYCLE"),
        (loop_b.number, "DEPENDENCY_CYCLE"),
        (moved.number, "PARENT_FOREIGN_REPOSITORY"),
        (leaf.number, "DEPENDENCY_FOREIGN_REPOSITORY"),
    }
    assert snapshot.issues[unmarked.number].id == f"epic-{unmarked.number:05d}"
    assert snapshot.issues[old_marker.number].id == f"iss-{old_marker.number:05d}"
    assert snapshot.issues[leaf.number].blocked_by == (plain.number,) and plain.number in snapshot.external


def test_an_unanswered_close_is_confirmed_only_when_the_state_reason_also_matches() -> None:
    fake = FakeGithub()
    issue = fake.scope("issue", slug="leaf", state="closed", state_reason="not_planned")
    client = _client(fake)
    fake.inject(timeout=True, method="PATCH")
    with pytest.raises(GithubStructureError) as caught:
        client.update_issue(issue.number, state="closed", state_reason="completed")
    assert (caught.value.code, caught.value.uncertain) == ("GITHUB_EFFECT_UNKNOWN", True)
    fake.inject(timeout=True, method="PATCH", apply=True)
    closed = client.update_issue(issue.number, state="closed", state_reason="completed")
    assert (closed.state, closed.state_reason) == ("closed", "completed")


def test_the_body_is_sent_and_an_unanswered_body_edit_is_compared_with_normalized_line_breaks() -> None:
    fake = FakeGithub()
    issue = fake.add_issue(title="Plain", body="Text\r\n")
    client = _client(fake)
    marked = "Text\n\n<!-- spec-dock:slug=plain -->\n"
    updated = client.update_issue(issue.number, body=marked)
    assert fake.writes()[-1].payload == {"body": marked} and updated.body == marked
    fake.issue(issue.number).body = "Text\r\n"
    fake.inject(timeout=True, method="PATCH")
    with pytest.raises(GithubStructureError) as caught:
        client.update_issue(issue.number, body=marked)
    assert caught.value.code == "GITHUB_EFFECT_UNKNOWN"
    fake.inject(timeout=True, method="PATCH")
    fake.issue(issue.number).body = marked.replace("\n", "\r\n")
    assert client.update_issue(issue.number, body=marked).body == marked.replace("\n", "\r\n")
