"""Provider CI sends the macOS distribution check of a trusted pull request to the local macOS VM (iss-00463)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tests.integration.test_issue454_runner_gate import (
    LOCAL_LINUX,
    NUMBER,
    REPOSITORY,
    WORKFLOWS,
    _jobs,
    _payload,
    _set,
)
from tests.support.canonical_check import provider_root

if TYPE_CHECKING:
    from pathlib import Path

PROVIDER = provider_root()
GATE = PROVIDER / ".github/scripts/ci-runner-job-gate.py"
LOCAL_MACOS = ["self-hosted", "macOS", "ARM64", "spec-dock-ci-macos"]


def _route(tmp_path: Path, payload: object, variables: dict[str, str]) -> subprocess.CompletedProcess[str]:
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(payload), encoding="utf-8")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GITHUB_") and not key.startswith("SPEC_DOCK_CI_")
    }
    environment |= {
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_EVENT_PATH": str(event_path),
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": f"refs/pull/{NUMBER}/merge",
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
    } | variables
    return subprocess.run(
        [sys.executable, str(GATE), "route", "--repository", REPOSITORY],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _runners(tmp_path: Path, payload: object, variables: dict[str, str]) -> dict[str, object]:
    completed = _route(tmp_path, payload, variables)
    assert completed.returncode == 0, completed.stderr
    runners: dict[str, object] = json.loads(
        (tmp_path / "github-output").read_text(encoding="utf-8").removeprefix("runners=")
    )
    return runners


@pytest.mark.parametrize(
    ("variables", "expected"),
    [
        ({}, {"ubuntu-latest": "ubuntu-latest", "macos-latest": "macos-latest"}),
        ({"SPEC_DOCK_CI_MACOS_RUNNER": "local"}, {"ubuntu-latest": "ubuntu-latest", "macos-latest": LOCAL_MACOS}),
        ({"SPEC_DOCK_CI_RUNNER": "local"}, {"ubuntu-latest": LOCAL_LINUX, "macos-latest": "macos-latest"}),
        (
            {"SPEC_DOCK_CI_RUNNER": "local", "SPEC_DOCK_CI_MACOS_RUNNER": "local"},
            {"ubuntu-latest": LOCAL_LINUX, "macos-latest": LOCAL_MACOS},
        ),
        (
            {"SPEC_DOCK_CI_RUNNER": "local", "SPEC_DOCK_CI_MACOS_RUNNER": "hosted"},
            {"ubuntu-latest": LOCAL_LINUX, "macos-latest": "macos-latest"},
        ),
        ({"SPEC_DOCK_CI_MACOS_RUNNER": ""}, {"ubuntu-latest": "ubuntu-latest", "macos-latest": "macos-latest"}),
    ],
)
def test_each_variable_moves_only_its_own_system_to_the_local_runner(
    tmp_path: Path, variables: dict[str, str], expected: dict[str, object]
) -> None:
    assert _runners(tmp_path, _payload(), variables) == expected


@pytest.mark.parametrize(
    ("path", "value"),
    [
        ("pull_request.head.repo.full_name", "someone/spec-dock"),
        ("pull_request.author_association", "CONTRIBUTOR"),
        ("sender.type", "Bot"),
    ],
)
def test_an_untrusted_pull_request_keeps_macos_on_github(tmp_path: Path, path: str, value: object) -> None:
    variables = {"SPEC_DOCK_CI_RUNNER": "local", "SPEC_DOCK_CI_MACOS_RUNNER": "local"}
    hosted = {"ubuntu-latest": "ubuntu-latest", "macos-latest": "macos-latest"}
    assert _runners(tmp_path, _set(_payload(), path, value), variables) == hosted


@pytest.mark.parametrize("value", ["Local", "macos", "true"])
def test_an_unknown_macos_variable_fails_route_without_output(tmp_path: Path, value: str) -> None:
    completed = _route(tmp_path, _payload(), {"SPEC_DOCK_CI_MACOS_RUNNER": value})
    assert completed.returncode == 2 and "SPEC_DOCK_CI_MACOS_RUNNER" in completed.stderr
    assert not (tmp_path / "github-output").exists()


def test_provider_ci_passes_both_variables_to_route_and_keeps_the_check_names() -> None:
    jobs = _jobs((WORKFLOWS / "provider-ci.yml").read_text(encoding="utf-8"))
    assert "SPEC_DOCK_CI_RUNNER: ${{ vars.SPEC_DOCK_CI_RUNNER }}" in jobs["route"]
    assert "SPEC_DOCK_CI_MACOS_RUNNER: ${{ vars.SPEC_DOCK_CI_MACOS_RUNNER }}" in jobs["route"]
    parity = jobs["provider-distribution-parity"]
    assert "name: Provider distribution parity (${{ matrix.os }})" in parity
    assert "os: [ubuntu-latest, macos-latest]" in parity
