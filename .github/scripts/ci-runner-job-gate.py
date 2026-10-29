"""Keep the SpecDock self-hosted runners to trusted same-repository pull requests (iss-00454, iss-00463).

`route` runs in a GitHub-hosted job and chooses the runner for each Provider CI job. Each system has its own repository
variable: SPEC_DOCK_CI_RUNNER for the Linux jobs and SPEC_DOCK_CI_MACOS_RUNNER for the macOS job. A job goes to its
self-hosted runner only when its variable is `local` and the pull request passes the same check the runner applies
itself; every other case keeps the GitHub-hosted runner.

`admit` is the runner's ACTIONS_RUNNER_HOOK_JOB_STARTED hook, called from a copy installed outside the job
workspace. It reads the event payload the runner wrote at the fixed place under the runner account's home and refuses
a job that points GITHUB_EVENT_PATH elsewhere, so a pull request that edits the workflow cannot change the decision.
Exit 0 lets the job run; any other exit fails the job before its first step.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import pwd
import sys

TRUSTED_ASSOCIATIONS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
# Each hosted runner name used by Provider CI, the repository variable that moves it, and its self-hosted labels.
LOCAL_RUNNERS = {
    "ubuntu-latest": ("SPEC_DOCK_CI_RUNNER", ("self-hosted", "Linux", "ARM64", "spec-dock-ci")),
    "macos-latest": ("SPEC_DOCK_CI_MACOS_RUNNER", ("self-hosted", "macOS", "ARM64", "spec-dock-ci-macos")),
}
RUNNER_MODES = frozenset({"hosted", "local"})


def _full_name(value: object) -> object:
    return value.get("full_name") if isinstance(value, dict) else None


def _type(value: object) -> object:
    return value.get("type") if isinstance(value, dict) else None


def decide(
    repository: str,
    event_name: str | None,
    environment_repository: str | None,
    payload: object,
    ref: str | None,
) -> str | None:
    """Return None when the job may run, otherwise the reason it must not."""
    if environment_repository != repository:
        return "the job does not belong to the expected repository"
    if event_name != "pull_request":
        return "only pull_request jobs may use this runner"
    if not isinstance(payload, dict) or _full_name(payload.get("repository")) != repository:
        return "the event payload does not name the expected repository"
    pull_request = payload.get("pull_request")
    if not isinstance(pull_request, dict):
        return "the event payload has no pull request"
    head = pull_request.get("head")
    base = pull_request.get("base")
    if not isinstance(head, dict) or not isinstance(base, dict):
        return "the pull request has no head or base"
    if _full_name(base.get("repo")) != repository:
        return "the pull request does not target the expected repository"
    if _full_name(head.get("repo")) != repository:
        return "the pull request comes from another repository"
    if _type(pull_request.get("user")) != "User" or _type(payload.get("sender")) != "User":
        return "the pull request author and the triggering user must be human users"
    if pull_request.get("author_association") not in TRUSTED_ASSOCIATIONS:
        return "the pull request author is not an owner, member or collaborator"
    # A payload left by an earlier job names another pull request than the ref the runner set for this one.
    number = pull_request.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or ref != f"refs/pull/{number}/merge":
        return "the event payload does not belong to this job"
    return None


def route(modes: dict[str, str], refusal: str | None) -> dict[str, object]:
    """Map each hosted runner name used by Provider CI to the runner its job should use."""
    runners: dict[str, object] = {}
    for name, (_, labels) in LOCAL_RUNNERS.items():
        runners[name] = list(labels) if modes[name] == "local" and refusal is None else name
    return runners


def _current_refusal(repository: str, event_path: str | None) -> str | None:
    if not event_path:
        return "the job names no event file"
    try:
        payload: object = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "the event file could not be read"
    return decide(
        repository,
        os.environ.get("GITHUB_EVENT_NAME"),
        os.environ.get("GITHUB_REPOSITORY"),
        payload,
        os.environ.get("GITHUB_REF"),
    )


def _runner_event_path() -> Path:
    """The event file the runner writes for the current job, found from the account rather than the job's variables."""
    return Path(pwd.getpwuid(os.getuid()).pw_dir) / "actions-runner/_work/_temp/_github_workflow/event.json"


def _admit(repository: str, event_path: Path) -> int:
    named = os.environ.get("GITHUB_EVENT_PATH")
    if named is None or os.path.realpath(named) != os.path.realpath(event_path):
        reason: str | None = "the job names an event file other than the one the runner wrote"
    else:
        reason = _current_refusal(repository, str(event_path))
    if reason is not None:
        print(f"SpecDock runner refused this job: {reason}", file=sys.stderr)
        return 1
    print("SpecDock runner admitted a same-repository pull request job")
    return 0


def _route(repository: str) -> int:
    modes = {}
    for name, (variable, _) in LOCAL_RUNNERS.items():
        modes[name] = os.environ.get(variable) or "hosted"
        if modes[name] not in RUNNER_MODES:
            print(f"{variable} must be unset, hosted or local, not {modes[name]!r}", file=sys.stderr)
            return 2
    refusal = _current_refusal(repository, os.environ.get("GITHUB_EVENT_PATH"))
    runners = route(modes, refusal)
    line = f"runners={json.dumps(runners, separators=(',', ':'))}"
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(line + "\n")
    print(line)
    if "local" in modes.values() and refusal is not None:
        print(f"Kept GitHub-hosted runners: {refusal}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("admit", "route"))
    parser.add_argument("--repository", required=True)
    parser.add_argument("--event-path", type=Path, help="admit: the runner's event file (default: from the account)")
    arguments = parser.parse_args(argv)
    if arguments.command == "admit":
        return _admit(arguments.repository, arguments.event_path or _runner_event_path())
    return _route(arguments.repository)


if __name__ == "__main__":
    sys.exit(main())
