"""The self-hosted runner admits only trusted same-repository pull request jobs (iss-00454)."""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.canonical_check import provider_root

if TYPE_CHECKING:
    from pathlib import Path

PROVIDER = provider_root()
GATE = PROVIDER / ".github/scripts/ci-runner-job-gate.py"
RUNNER = PROVIDER / ".github/runner"
WORKFLOWS = PROVIDER / ".github/workflows"
REPOSITORY = "chemitaro/spec-dock"
LOCAL_LINUX = ["self-hosted", "Linux", "ARM64", "spec-dock-ci"]
HOSTED = {"ubuntu-latest": "ubuntu-latest", "macos-latest": "macos-latest"}


def _payload() -> dict[str, Any]:
    return {
        "repository": {"full_name": REPOSITORY},
        "sender": {"login": "chemitaro", "type": "User"},
        "pull_request": {
            "author_association": "OWNER",
            "user": {"login": "chemitaro", "type": "User"},
            "head": {"repo": {"full_name": REPOSITORY}},
            "base": {"repo": {"full_name": REPOSITORY}},
        },
    }


def _run(
    tmp_path: Path,
    command: str,
    payload: object,
    *,
    event: str = "pull_request",
    repository: str = REPOSITORY,
    extra: dict[str, str] | None = None,
    arguments: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    event_path = tmp_path / "event.json"
    event_path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GITHUB_") and key != "SPEC_DOCK_CI_RUNNER"
    }
    environment |= {"GITHUB_EVENT_NAME": event, "GITHUB_EVENT_PATH": str(event_path), "GITHUB_REPOSITORY": repository}
    environment |= extra or {}
    return subprocess.run(
        [sys.executable, str(GATE), command, "--repository", REPOSITORY, *arguments],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _gate(tmp_path: Path, payload: object, *, event: str = "pull_request", repository: str = REPOSITORY) -> int:
    event_path = str(tmp_path / "event.json")
    completed = _run(
        tmp_path, "admit", payload, event=event, repository=repository, arguments=("--event-path", event_path)
    )
    if completed.returncode:
        assert completed.stderr.startswith("SpecDock runner refused this job: ")
    return completed.returncode


def _route(tmp_path: Path, payload: object, mode: str | None, **options: Any) -> dict[str, object]:
    output = tmp_path / "github-output"
    extra = {"GITHUB_OUTPUT": str(output)} | ({} if mode is None else {"SPEC_DOCK_CI_RUNNER": mode})
    completed = _run(tmp_path, "route", payload, extra=extra, **options)
    assert completed.returncode == 0, completed.stderr
    key, _, value = output.read_text(encoding="utf-8").partition("=")
    assert key == "runners" and value.endswith("\n")
    runners: dict[str, object] = json.loads(value)
    return runners


@pytest.mark.parametrize("association", ["OWNER", "MEMBER", "COLLABORATOR"])
def test_a_same_repository_pull_request_by_a_trusted_human_runs(tmp_path: Path, association: str) -> None:
    payload = _payload()
    payload["pull_request"]["author_association"] = association
    assert _gate(tmp_path, payload) == 0


def _set(payload: dict[str, Any], path: str, value: object) -> dict[str, Any]:
    changed = copy.deepcopy(payload)
    *parents, leaf = path.split(".")
    node = changed
    for key in parents:
        node = node[key]
    node[leaf] = value
    return changed


UNTRUSTED = [
    ("pull_request.head.repo.full_name", "someone/spec-dock"),
    ("pull_request.head.repo", None),
    ("pull_request.base.repo.full_name", "someone/spec-dock"),
    ("repository.full_name", "someone/spec-dock"),
    ("pull_request.user.type", "Bot"),
    ("sender.type", "Bot"),
    ("pull_request.author_association", "CONTRIBUTOR"),
    ("pull_request.author_association", "FIRST_TIME_CONTRIBUTOR"),
    ("pull_request.author_association", "NONE"),
    ("pull_request", None),
]


@pytest.mark.parametrize(("path", "value"), UNTRUSTED)
def test_forks_bots_and_outsiders_are_refused(tmp_path: Path, path: str, value: object) -> None:
    assert _gate(tmp_path, _set(_payload(), path, value)) == 1


@pytest.mark.parametrize("event", ["push", "pull_request_target", "workflow_dispatch", "workflow_run"])
def test_other_events_are_refused(tmp_path: Path, event: str) -> None:
    assert _gate(tmp_path, _payload(), event=event) == 1


def test_another_repository_or_an_unreadable_payload_is_refused(tmp_path: Path) -> None:
    assert _gate(tmp_path, _payload(), repository="someone/spec-dock") == 1
    assert _gate(tmp_path, "{not json") == 1
    assert _gate(tmp_path, "[]") == 1


def test_a_job_that_names_another_event_file_is_refused(tmp_path: Path) -> None:
    planted = tmp_path / "planted.json"
    planted.write_text(json.dumps(_payload()), encoding="utf-8")
    completed = _run(tmp_path, "admit", _payload(), arguments=("--event-path", str(planted)))
    assert completed.returncode == 1 and "event file other than" in completed.stderr


def test_route_sends_only_the_linux_jobs_of_a_trusted_pull_request_to_the_local_runner(tmp_path: Path) -> None:
    assert _route(tmp_path, _payload(), "local") == {"ubuntu-latest": LOCAL_LINUX, "macos-latest": "macos-latest"}


@pytest.mark.parametrize("mode", [None, "", "hosted"])
def test_route_keeps_hosted_runners_until_the_variable_says_local(tmp_path: Path, mode: str | None) -> None:
    assert _route(tmp_path, _payload(), mode) == HOSTED


@pytest.mark.parametrize(("path", "value"), UNTRUSTED)
def test_route_keeps_hosted_runners_for_forks_bots_and_outsiders(tmp_path: Path, path: str, value: object) -> None:
    assert _route(tmp_path, _set(_payload(), path, value), "local") == HOSTED


def test_route_keeps_hosted_runners_for_another_repository(tmp_path: Path) -> None:
    assert _route(tmp_path, _payload(), "local", repository="someone/spec-dock") == HOSTED


def test_route_fails_on_an_unknown_variable_value(tmp_path: Path) -> None:
    output = tmp_path / "github-output"
    completed = _run(
        tmp_path, "route", _payload(), extra={"GITHUB_OUTPUT": str(output), "SPEC_DOCK_CI_RUNNER": "Local"}
    )
    assert completed.returncode == 2 and "SPEC_DOCK_CI_RUNNER" in completed.stderr
    assert not output.exists()


def _jobs(workflow: str) -> dict[str, str]:
    """Split a workflow into the text of each job under `jobs:`."""
    body = workflow.split("\njobs:\n", 1)[1]
    parts = re.split(r"^  (?=[a-z][a-z0-9-]*:\n)", body, flags=re.MULTILINE)
    return {part.split(":", 1)[0]: part for part in parts if part.strip() and not part.startswith(" ")}


def test_provider_ci_runs_its_checks_where_route_says_and_never_names_the_runner_itself() -> None:
    workflow = (WORKFLOWS / "provider-ci.yml").read_text(encoding="utf-8")
    jobs = _jobs(workflow)
    assert set(jobs) == {"route", "provider-tests", "provider-distribution-parity"}
    assert "permissions:\n  contents: read\n" in workflow and not re.search(r"runs-on:.*self-hosted", workflow)
    assert "runs-on: ubuntu-latest\n" in jobs["route"]
    assert "SPEC_DOCK_CI_RUNNER: ${{ vars.SPEC_DOCK_CI_RUNNER }}" in jobs["route"]
    assert "ci-runner-job-gate.py route --repository chemitaro/spec-dock" in jobs["route"]
    assert "runners: ${{ steps.route.outputs.runners }}" in jobs["route"]
    # Without route's output, fromJSON('') would stop GitHub from creating the job at all (seen in run 40878463664),
    # so each job falls back to its hosted runner and fails in its first step instead.
    tests_runner = "${{ needs.route.outputs.runners && fromJSON(needs.route.outputs.runners)['ubuntu-latest'] || 'ubuntu-latest' }}"
    parity_runner = (
        "${{ needs.route.outputs.runners && fromJSON(needs.route.outputs.runners)[matrix.os] || matrix.os }}"
    )
    assert f"runs-on: {tests_runner}" in jobs["provider-tests"]
    assert f"runs-on: {parity_runner}" in jobs["provider-distribution-parity"]
    for name in ("provider-tests", "provider-distribution-parity"):
        assert "needs: route\n" in jobs[name] and "if: ${{ !cancelled() }}\n" in jobs[name]
        first_step = jobs[name].split("    steps:\n", 1)[1].split("\n      - ", 1)[0]
        assert "if: needs.route.result != 'success'" in first_step and "exit 1" in first_step
    parity = jobs["provider-distribution-parity"]
    assert "name: Provider distribution parity (${{ matrix.os }})" in parity
    assert "os: [ubuntu-latest, macos-latest]" in parity
    assert "make lint" in jobs["provider-tests"] and "uv run pytest\n" in jobs["provider-tests"]


@pytest.mark.parametrize("name", ["ci.yml", "commit-identity.yml", "release-tag.yml"])
def test_short_and_writing_workflows_stay_on_github_hosted_runners(name: str) -> None:
    workflow = (WORKFLOWS / name).read_text(encoding="utf-8")
    assert re.findall(r"runs-on: (.+)", workflow) == ["ubuntu-latest"]


def test_the_vm_shares_nothing_with_the_mac_and_blocks_the_mac_and_private_networks() -> None:
    lima = (RUNNER / "spec-dock-ci.lima.yaml").read_text(encoding="utf-8")
    for line in ("vmType: vz", "plain: true", "mounts: []", "loadDotSSHPubKeys: false", "forwardAgent: false"):
        assert f"\n{line}\n" in lima or f"  {line}\n" in lima
    assert "portForwards" not in lima and 'digest: "sha256:' in lima
    rules = (RUNNER / "nftables.conf").read_text(encoding="utf-8")
    for network in ("10.0.0.0/8", "100.64.0.0/10", "169.254.0.0/16", "172.16.0.0/12", "192.168.0.0/16"):
        assert network in rules
    assert "meta nfproto ipv6 counter reject" in rules
    assert rules.index("192.168.5.2 meta l4proto { tcp, udp } th dport 53 accept") < rules.index(
        "@blocked_ipv4 counter reject"
    )


def test_the_runner_hooks_gate_each_job_and_runner_users_get_no_administrative_group() -> None:
    started = (RUNNER / "job-started.sh").read_text(encoding="utf-8")
    assert started.rstrip().endswith(
        "exec /usr/bin/python3 -I /opt/spec-dock-ci/ci-runner-job-gate.py admit --repository chemitaro/spec-dock"
    )
    setup = (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")
    assert "ACTIONS_RUNNER_HOOK_JOB_STARTED=/opt/spec-dock-ci/job-started.sh" in setup
    assert "ACTIONS_RUNNER_HOOK_JOB_COMPLETED=/opt/spec-dock-ci/job-completed.sh" in setup
    assert 'echo "$RUNNER_SHA256  $archive" | sha256sum -c -' in setup
    # setup-python builds look for libpython under the hosted tool cache, which root owns here (iss-00454).
    assert 'echo "$PYTHON_SHA256  $python_archive" | sha256sum -c -' in setup
    assert "AGENT_TOOLSDIRECTORY=$TOOL_CACHE" in setup and "TOOL_CACHE=/opt/hostedtoolcache" in (
        RUNNER / "settings.sh"
    ).read_text(encoding="utf-8")
    assert "must not belong to an administrative group" in setup and "usermod" not in setup
    register = (RUNNER / "register-runner.sh").read_text(encoding="utf-8")
    # sudo records the environment it passes, so the token travels through a pipe instead (iss-00454 RQ-454-06).
    assert "IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN" in register and "printf '%s\\n' \"$token\" | sudo -u" in register
    assert (
        "--preserve-env" not in register
        and "--token" not in register
        and "export ACTIONS_RUNNER_INPUT_TOKEN\n" not in register
    )


def test_root_runs_nothing_a_runner_user_can_change() -> None:
    setup = (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")
    register = (RUNNER / "register-runner.sh").read_text(encoding="utf-8")
    assert '"$dist/bin/installdependencies.sh"' in setup and "dist=/opt/spec-dock-ci/runner-dist-" in setup
    # No command line of the root script starts a script under a runner user's home (only the unit names one).
    assert not re.search(r'^\s*"?(\$dir|/home)/.*\.sh', setup, flags=re.MULTILINE)
    assert "User=$user" in setup and "ExecStart=$dir/bin/runsvc.sh" in setup
    assert "svc.sh install" not in setup + register and "systemctl enable --now" in register


def _work(tmp_path: Path) -> Path:
    work = tmp_path / "home/actions-runner/_work"
    for name in ("_tool/Python", "_actions/actions", "_temp/x", "spec-dock/spec-dock/src", "_PipelineMapping/x"):
        (work / name).mkdir(parents=True)
    (work / "spec-dock/spec-dock/src/file").write_text("checkout", encoding="utf-8")
    return work


def _completed(tmp_path: Path, runner_temp: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ | {"HOME": str(tmp_path / "home"), "RUNNER_TEMP": str(runner_temp)}
    return subprocess.run(
        ["/bin/sh", str(RUNNER / "job-completed.sh")],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def test_the_job_completed_hook_removes_the_job_files_and_keeps_the_tool_cache(tmp_path: Path) -> None:
    work = _work(tmp_path)
    completed = _completed(tmp_path, work / "_temp")
    assert completed.returncode == 0, completed.stderr
    assert [path.name for path in work.iterdir()] == ["_tool"] and (work / "_tool/Python").is_dir()


def test_the_job_completed_hook_removes_nothing_outside_its_own_work_directory(tmp_path: Path) -> None:
    work = _work(tmp_path)
    other = tmp_path / "other/_temp"
    other.mkdir(parents=True)
    completed = _completed(tmp_path, other)
    assert completed.returncode == 1 and "unexpected RUNNER_TEMP" in completed.stderr
    assert (work / "spec-dock/spec-dock/src/file").is_file() and other.is_dir()
