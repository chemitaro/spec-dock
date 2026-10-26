"""Suite-wide guard: no test may install, kick or remove a real periodic job (launchd, systemd, a detached runner).

Two layers: (1) fakes for the scheduler factory and friends, set outside any monkeypatch; (2) for the whole
session, PATH starts with launchctl, systemctl and loginctl stand-ins that refuse loudly and record the call,
and the session fails at teardown if any was called. Real-machine checks run outside this suite on purpose.

canonical link registers periodic sync (iss-00430). The session replaces the scheduler factory, the spec-dock
path, systemd probing and the 15-second wait outside any monkeypatch, so even `monkeypatch.undo()` falls
back to fakes; each test also gets its own recording fakes. Tests of the real schedulers construct them
directly with injected command runners.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.application import canonical_schedule
from spec_dock.runtime.infra import canonical_scheduling, runtime_environment
from tests.support.canonical_sync import FakeScheduler

if TYPE_CHECKING:
    from collections.abc import Iterator

_FAKE_EXECUTABLE = Path("/opt/spec-dock/bin/spec-dock")


def _fresh_fake(kind: str, **_kwargs: object) -> FakeScheduler:
    return FakeScheduler(kind, simulate_run=True)


def _no_service_manager(environment: runtime_environment.RuntimeEnvironment, **_kwargs: object) -> object:
    return environment


_GUARDED_COMMANDS = ("launchctl", "systemctl", "loginctl")


@pytest.fixture(autouse=True, scope="session")  # noqa: RUF076 -- a suite-wide safety guard
def _service_manager_commands_refuse() -> Iterator[None]:
    """Any real service-manager call from a test reaches these stand-ins, fails, and fails the session."""
    with tempfile.TemporaryDirectory(prefix="spec-dock-guard-") as directory:
        guard = Path(directory)
        calls = guard / "calls.log"
        for name in _GUARDED_COMMANDS:
            script = guard / name
            script.write_text(
                "#!/bin/sh\n"
                f'echo "{name} $*" >> "{calls}"\n'
                f'echo "BLOCKED: a test called {name}; tests must never reach a real service manager" >&2\n'
                "exit 99\n",
                encoding="utf-8",
            )
            script.chmod(0o755)
        previous = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{guard}{os.pathsep}{previous}"
        try:
            yield
        finally:
            os.environ["PATH"] = previous
            if calls.exists():
                pytest.fail(f"tests called a real service manager:\n{calls.read_text(encoding='utf-8')}")


@pytest.fixture(autouse=True, scope="session")  # noqa: RUF076 -- a suite-wide safety guard
def _session_guard() -> Iterator[None]:
    saved = (
        canonical_scheduling.scheduler_for,
        canonical_scheduling.spec_dock_executable,
        runtime_environment.detect_service_manager,
        canonical_schedule.FIRST_RUN_WAIT,
    )
    canonical_scheduling.scheduler_for = _fresh_fake  # type: ignore[assignment]
    canonical_scheduling.spec_dock_executable = lambda: _FAKE_EXECUTABLE
    runtime_environment.detect_service_manager = _no_service_manager  # type: ignore[assignment]
    canonical_schedule.FIRST_RUN_WAIT = 0.0
    try:
        yield
    finally:
        (
            canonical_scheduling.scheduler_for,
            canonical_scheduling.spec_dock_executable,
            runtime_environment.detect_service_manager,
            canonical_schedule.FIRST_RUN_WAIT,
        ) = saved


@pytest.fixture(autouse=True)  # noqa: RUF076 -- every test gets its own recording fakes
def periodic_jobs(monkeypatch: pytest.MonkeyPatch) -> dict[str, FakeScheduler]:
    """This test's recording fake schedulers, by kind."""
    schedulers: dict[str, FakeScheduler] = {}

    def scheduler_for(kind: str, **_kwargs: object) -> FakeScheduler:
        return schedulers.setdefault(kind, FakeScheduler(kind, simulate_run=True))

    monkeypatch.setattr(canonical_scheduling, "scheduler_for", scheduler_for)
    return schedulers
