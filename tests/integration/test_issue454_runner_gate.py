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
NUMBER = 7


def _payload() -> dict[str, Any]:
    return {
        "repository": {"full_name": REPOSITORY},
        "sender": {"login": "chemitaro", "type": "User"},
        "number": NUMBER,
        "pull_request": {
            "number": NUMBER,
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
    ref: str = f"refs/pull/{NUMBER}/merge",
    extra: dict[str, str] | None = None,
    arguments: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    event_path = tmp_path / "event.json"
    if isinstance(payload, bytes):
        event_path.write_bytes(payload)
    else:
        event_path.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GITHUB_") and key != "SPEC_DOCK_CI_RUNNER"
    }
    environment |= {
        "GITHUB_EVENT_NAME": event,
        "GITHUB_EVENT_PATH": str(event_path),
        "GITHUB_REPOSITORY": repository,
        "GITHUB_REF": ref,
    }
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


@pytest.mark.parametrize("ref", ["refs/pull/8/merge", "refs/heads/main", "refs/pull/7/head", ""])
def test_an_event_file_left_by_another_job_is_refused(tmp_path: Path, ref: str) -> None:
    # The runner rewrites event.json for each job; a leftover payload names another pull request (iss-00463 T-7).
    completed = _run(tmp_path, "admit", _payload(), ref=ref, arguments=("--event-path", str(tmp_path / "event.json")))
    assert completed.returncode == 1 and "does not belong to this job" in completed.stderr


@pytest.mark.parametrize("payload", ["{not json", b"\xff"])
def test_an_unreadable_event_file_is_refused_for_that_reason(tmp_path: Path, payload: str | bytes) -> None:
    completed = _run(tmp_path, "admit", payload, arguments=("--event-path", str(tmp_path / "event.json")))
    assert completed.returncode == 1 and "could not be read" in completed.stderr


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


@pytest.mark.parametrize("event", ["push", "pull_request_target", "workflow_dispatch", "workflow_run"])
def test_route_keeps_hosted_runners_for_other_events(tmp_path: Path, event: str) -> None:
    assert _route(tmp_path, _payload(), "local", event=event) == HOSTED


@pytest.mark.parametrize("payload", ["{not json", "[]", b"\xff"])
def test_route_keeps_hosted_runners_for_an_unreadable_event(tmp_path: Path, payload: str | bytes) -> None:
    assert _route(tmp_path, payload, "local") == HOSTED


def test_admit_refuses_a_job_without_an_event_file_or_away_from_the_runner_home(tmp_path: Path) -> None:
    event_path = str(tmp_path / "event.json")
    unnamed = _run(
        tmp_path, "admit", _payload(), extra={"GITHUB_EVENT_PATH": ""}, arguments=("--event-path", event_path)
    )
    assert unnamed.returncode == 1 and "event file other than" in unnamed.stderr
    # Without --event-path the hook reads the file under the account's own runner directory, not the job's file.
    default = _run(tmp_path, "admit", _payload())
    assert default.returncode == 1 and "event file other than" in default.stderr


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
    # route runs pull request code with a read token it does not need to keep (iss-00463 T-10).
    assert "persist-credentials: false" in jobs["route"]
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
        # A job stuck on the self-hosted runner gives the runner back well before GitHub's 360-minute default.
        assert "    timeout-minutes: 30\n" in jobs[name]
        first_step = jobs[name].split("    steps:\n", 1)[1].split("\n      - ", 1)[0]
        assert "if: needs.route.result != 'success'" in first_step and "exit 1" in first_step
    parity = jobs["provider-distribution-parity"]
    assert "name: Provider distribution parity (${{ matrix.os }})" in parity
    assert "os: [ubuntu-latest, macos-latest]" in parity
    assert "make lint" in jobs["provider-tests"] and "uv run pytest\n" in jobs["provider-tests"]
    # The check is named after the job id, so a name: line would rename the required check.
    assert not re.search(r"^    name:", jobs["provider-tests"], flags=re.MULTILINE)


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
        "exec /opt/spec-dock-ci/python3 -I /opt/spec-dock-ci/ci-runner-job-gate.py admit --repository chemitaro/spec-dock"
    )
    setup = (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")
    settings = (RUNNER / "settings.sh").read_text(encoding="utf-8")
    assert 'ln -sfn "$GATE_PYTHON" /opt/spec-dock-ci/python3' in setup and "GATE_PYTHON=/usr/bin/python3\n" in settings
    assert "ACTIONS_RUNNER_HOOK_JOB_STARTED=/opt/spec-dock-ci/job-started.sh" in setup
    assert "ACTIONS_RUNNER_HOOK_JOB_COMPLETED=/opt/spec-dock-ci/job-completed.sh" in setup
    # Every download root uses is checked against a pinned SHA256 (iss-00463 R-3, U-2).
    assert '"$archive" "$RUNNER_SHA256"' in setup and '"$python_archive" "$PYTHON_SHA256"' in setup
    assert '"$uv_wheel" "$UV_WHEEL_SHA256"' in setup and "--no-index --no-deps" in setup and "-I -m pip" in setup
    # setup-python builds look for libpython under the hosted tool cache, which root owns here (iss-00454).
    assert "AGENT_TOOLSDIRECTORY=$TOOL_CACHE" in setup and "TOOL_CACHE=/opt/hostedtoolcache" in settings
    assert "must not belong to an administrative group" in setup and "usermod" not in setup
    register = (RUNNER / "register-runner.sh").read_text(encoding="utf-8")
    # sudo records the environment it passes, so the token travels through a pipe instead (iss-00454 RQ-454-06).
    assert "IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN" in register and "printf '%s\\n' \"$token\" | sudo -u" in register
    assert not re.search(r"--preserve-env|--token|ACTIONS_RUNNER_INPUT_TOKEN=", register)


def test_guest_setup_keeps_its_files_to_root_and_checks_the_rules_before_installing_them() -> None:
    setup = (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")
    assert "\numask 022\n" in setup and setup.rstrip().splitlines()[-2].startswith("check_root_tree /opt/spec-dock-ci ")
    assert setup.index('nft -c -f "$here/nftables.conf"') < setup.index('install -m 644 "$here/nftables.conf"')
    assert '"origin=LP-PPA-git-core"' in setup and "/etc/apt/apt.conf.d/" in setup


RUNNER_HOME_REFERENCE = re.compile(r"\$dir\b|\$RUNNER_HOME|/home/")
# Naming the runner's files in the unit or LaunchDaemon root writes, and creating the account's home, are allowed.
ALLOWED_HOME_COMMAND = re.compile(
    r"^\s*(dir=|ExecStart=|WorkingDirectory=|<key>(ProgramArguments|WorkingDirectory|HOME)</key>)"
    r'|(--home-dir|-home) "\$RUNNER_HOME/\$user"'
)
AS_RUNNER_USER = 'sudo -u "$user"'


def root_lines_touching_runner_files(script: str) -> list[str]:
    """Lines of a root script that use something under a runner user's home other than through that user's own shell.

    Each command of a line (split at pipes, lists and `;`) may test whether such a file exists, name it in the unit
    root writes, or reach it only as an argument of `sudo -u "$user"`.
    """
    found = []
    for line in script.splitlines():
        if line.lstrip().startswith("#"):
            continue
        code = re.sub(r"'[^']*'", "''", re.sub(r'\[ !? ?-f "\$dir/[^"]+" \]', "", line))
        for command in re.split(r"\|\||&&|\||;", code):
            reference = RUNNER_HOME_REFERENCE.search(command)
            if reference is None or ALLOWED_HOME_COMMAND.search(command):
                continue
            if AS_RUNNER_USER not in command[: reference.start()]:
                found.append(line)
                break
    return found


def test_the_runner_home_check_finds_root_using_a_runner_file() -> None:
    assert root_lines_touching_runner_files('  "$dir/bin/installdependencies.sh"\n  . "$dir/.env"\n  cp /home/x/a /opt')
    assert len(root_lines_touching_runner_files('  grep -q x "$dir/.env"\n  sh -c "$RUNNER_HOME/u/run.sh"')) == 2
    old_q2 = '  grep -q -x -F "$hook" "$dir/.env" || echo "$hook" | sudo -u "$user" tee -a "$dir/.env" >/dev/null'
    assert root_lines_touching_runner_files(old_q2) == [old_q2]
    assert not root_lines_touching_runner_files('  if [ ! -f "$dir/config.sh" ]; then\n  sudo -u "$user" tar -C "$dir"')


def test_root_runs_nothing_a_runner_user_can_change() -> None:
    setup = (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")
    register = (RUNNER / "register-runner.sh").read_text(encoding="utf-8")
    assert '"$dist/bin/installdependencies.sh"' in setup and "dist=/opt/spec-dock-ci/runner-dist-" in setup
    assert root_lines_touching_runner_files(setup) == []
    # Root's own extractions never keep the archive's owners, so no file under /opt belongs to a runner user.
    root_extractions = [line for line in setup.splitlines() if "tar -x" in line and 'sudo -u "$user"' not in line]
    assert len(root_extractions) == 2 and all("--no-same-owner" in line for line in root_extractions)
    assert "User=$user" in setup and "ExecStart=$dir/bin/runsvc.sh" in setup
    commands = [line for line in (setup + register).splitlines() if not line.lstrip().startswith("#")]
    assert not any("svc.sh" in line.replace("runsvc.sh", "") for line in commands)
    assert "systemctl enable --now" in register


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


def test_the_job_completed_hook_removes_nothing_through_a_linked_work_directory(tmp_path: Path) -> None:
    target = tmp_path / "elsewhere"
    (target / "_temp").mkdir(parents=True)
    (target / "keep").write_text("keep", encoding="utf-8")
    runner = tmp_path / "home/actions-runner"
    runner.mkdir(parents=True)
    (runner / "_work").symlink_to(target)
    completed = _completed(tmp_path, runner / "_work/_temp")
    assert completed.returncode == 1 and "unexpected work directory" in completed.stderr
    assert (target / "keep").is_file()


def test_the_job_completed_hook_removes_nothing_outside_its_own_work_directory(tmp_path: Path) -> None:
    work = _work(tmp_path)
    other = tmp_path / "other/_temp"
    other.mkdir(parents=True)
    completed = _completed(tmp_path, other)
    assert completed.returncode == 1 and "unexpected RUNNER_TEMP" in completed.stderr
    assert (work / "spec-dock/spec-dock/src/file").is_file() and other.is_dir()


def test_every_place_that_names_the_repository_names_the_same_one() -> None:
    # The name stays written out where each file needs it, so a rename has to change all of them together (T-11).
    settings = (RUNNER / "settings.sh").read_text(encoding="utf-8")
    assert f"SPEC_DOCK_REPOSITORY={REPOSITORY}\n" in settings
    assert f"--repository {REPOSITORY}" in (RUNNER / "job-started.sh").read_text(encoding="utf-8")
    assert f"route --repository {REPOSITORY}" in (WORKFLOWS / "provider-ci.yml").read_text(encoding="utf-8")
    needrestart_unit = "actions\\.runner\\." + REPOSITORY.replace("/", "-") + "\\."
    assert needrestart_unit in (RUNNER / "guest-setup.sh").read_text(encoding="utf-8")


@pytest.mark.parametrize("script", ["guest-setup.sh", "macos/guest-setup.sh"])
def test_root_uses_runner_files_only_through_the_runner_user_on_either_system(script: str) -> None:
    setup = (RUNNER / script).read_text(encoding="utf-8")
    assert root_lines_touching_runner_files(setup) == []
    root_extractions = [line for line in setup.splitlines() if "tar -x" in line and 'sudo -u "$user"' not in line]
    assert root_extractions and all("--no-same-owner" in line for line in root_extractions)
