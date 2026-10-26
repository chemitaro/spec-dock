"""launchd, systemd and the resident loop runner behind one Scheduler interface (iss-00430), with fake commands."""

from __future__ import annotations

import os
from pathlib import Path
import plistlib
import signal
import subprocess
import threading

import pytest

from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec
from spec_dock.runtime.infra.canonical_scheduler_launchd import LaunchdScheduler
from spec_dock.runtime.infra.canonical_scheduler_loop import LoopScheduler, read_runner, run_loop, runner_running
from spec_dock.runtime.infra.canonical_scheduler_systemd import SystemdScheduler
from spec_dock.runtime.infra.canonical_scheduling import SchedulerError
from spec_dock.runtime.infra.canonical_state import kick_path


@pytest.fixture
def spec(tmp_path: Path) -> SchedulerSpec:
    executable = tmp_path / "bin/spec-dock"
    executable.parent.mkdir()
    executable.write_text("#!/bin/sh\n")
    executable.chmod(0o755)
    return SchedulerSpec(executable, tmp_path / "state", Path("/usr/bin"), tmp_path / "home")


class Commands:
    def __init__(self, answers: dict[str, int] | None = None) -> None:
        self.calls: list[list[str]] = []
        self.answers = answers or {}
        self.loaded = False

    def __call__(self, argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        self.calls.append(argv)
        verb = argv[1] if argv[0] == "launchctl" else argv[2]
        if argv[0] == "launchctl":
            if verb == "print":
                return subprocess.CompletedProcess(argv, 0 if self.loaded else 113, b"", b"")
            if verb == "bootstrap":
                self.loaded = self.answers.get(verb, 0) == 0
            if verb == "bootout":
                self.loaded = False
        if verb == "is-active":
            return subprocess.CompletedProcess(
                argv, 0 if self.loaded else 3, b"active\n" if self.loaded else b"inactive\n", b""
            )
        if verb == "enable":
            self.loaded = True
        return subprocess.CompletedProcess(
            argv, self.answers.get(verb, 0), b"", b"boom" if self.answers.get(verb) else b""
        )


def test_launchd_installs_once_kicks_and_removes(tmp_path: Path, spec: SchedulerSpec) -> None:
    commands = Commands()
    launchd = LaunchdScheduler(agents_dir=tmp_path / "agents", label="local.test.job", uid=501, runner=commands)
    assert launchd.needs_change(spec) and launchd.write_paths(spec) == (tmp_path / "agents",)
    assert launchd.ensure(spec) == "created"
    plist = plistlib.loads((tmp_path / "agents/local.test.job.plist").read_bytes())
    assert plist["Label"] == "local.test.job" and plist["ProgramArguments"][0] == str(spec.executable)
    assert launchd.recorded_executable(spec) == spec.executable
    assert not launchd.needs_change(spec) and launchd.ensure(spec) == "unchanged"
    launchd.kick(spec)
    assert ["launchctl", "kickstart", "gui/501/local.test.job"] in commands.calls
    assert launchd.observe(spec).active is True
    assert launchd.remove(spec) is True and not (tmp_path / "agents/local.test.job.plist").exists()
    verbs = [call[1] for call in commands.calls]
    assert verbs.count("bootstrap") == 1 and "bootout" in verbs


def test_launchd_reloads_a_changed_plist_and_reports_a_refused_bootstrap(tmp_path: Path, spec: SchedulerSpec) -> None:
    commands = Commands()
    launchd = LaunchdScheduler(agents_dir=tmp_path / "agents", uid=501, runner=commands)
    launchd.ensure(spec)
    moved = SchedulerSpec(spec.executable, spec.state_root, Path("/opt/git/bin"), spec.home)
    assert launchd.needs_change(moved) and launchd.ensure(moved) == "updated"
    assert [call[1] for call in commands.calls].count("bootout") == 1
    refusing = LaunchdScheduler(agents_dir=tmp_path / "other", uid=501, runner=Commands({"bootstrap": 5}))
    with pytest.raises(SchedulerError, match="bootstrap"):
        refusing.ensure(spec)


def test_systemd_writes_both_units_enables_the_timer_and_removes_them(tmp_path: Path, spec: SchedulerSpec) -> None:
    commands = Commands()
    systemd = SystemdScheduler(unit_dir=tmp_path / "units", runner=commands)
    assert systemd.ensure(spec) == "created"
    assert (tmp_path / "units/spec-dock-canonical-sync.timer").read_text().startswith("[Unit]")
    assert systemd.recorded_executable(spec) == spec.executable
    assert systemd.ensure(spec) == "unchanged"
    systemd.kick(spec)
    systemd.remove(spec)
    assert not (tmp_path / "units/spec-dock-canonical-sync.service").exists()
    assert [call[2:] for call in commands.calls if call[2] != "is-active"] == [
        ["daemon-reload"],
        ["enable", "--now", "spec-dock-canonical-sync.timer"],
        ["start", "--no-block", "spec-dock-canonical-sync.service"],
        ["disable", "--now", "spec-dock-canonical-sync.timer"],
        ["daemon-reload"],
    ]


def test_the_loop_runner_runs_alone_wakes_on_kick_and_stops_after_its_cycle(tmp_path: Path) -> None:
    root = tmp_path / "state"
    cycles: list[str] = []
    second: list[str] = []

    def cycle() -> None:
        cycles.append("cycle")
        if len(cycles) == 1:
            assert runner_running(root) and read_runner(root) is not None
            second.append(run_loop(root, cycle=lambda: None, version="t", sleep=lambda _s: None, install_signals=False))
            kick_path(root).touch()
        elif len(cycles) == 2:
            os.kill(os.getpid(), signal.SIGTERM)  # arrives mid-cycle: this cycle still finishes
            cycles.append("finished after SIGTERM")

    slept: list[float] = []
    outcome = run_loop(root, cycle=cycle, version="t", sleep=slept.append, monotonic=lambda: 0.0)
    assert outcome == "stopped" and second == ["already_running"]
    assert cycles == ["cycle", "cycle", "finished after SIGTERM"]
    assert not kick_path(root).exists() and read_runner(root) is None and not runner_running(root)
    assert signal.getsignal(signal.SIGTERM) is signal.SIG_DFL


def test_the_loop_runner_waits_60_seconds_between_cycles_checking_every_2_seconds(tmp_path: Path) -> None:
    root = tmp_path / "state"
    clock = {"now": 0.0}
    cycles: list[float] = []

    def sleep(seconds: float) -> None:
        clock["now"] += seconds

    def cycle() -> None:
        cycles.append(clock["now"])
        if len(cycles) == 3:
            stop.set()

    stop = threading.Event()

    def guarded() -> None:
        cycle()
        if stop.is_set():
            os.kill(os.getpid(), signal.SIGINT)

    run_loop(root, cycle=guarded, version="t", sleep=sleep, monotonic=lambda: clock["now"])
    assert cycles == [0.0, 60.0, 120.0]


def test_loop_scheduler_starts_kicks_and_stops_the_runner(tmp_path: Path, spec: SchedulerSpec) -> None:
    root = spec.state_root
    spawned: list[Path] = []

    def spawn(state_root: Path, **kwargs: Path) -> int:
        spawned.append(kwargs["executable"])
        return 1

    loop = LoopScheduler(root, spawn=spawn)
    assert loop.ensure(spec) == "created" and spawned == [spec.executable]
    loop.kick(spec)
    assert len(spawned) == 2  # not running: a kick starts it
    assert loop.remove(spec) is False


def test_launchd_retries_bootstrap_and_refuses_to_forget_a_job_it_could_not_boot_out(
    tmp_path: Path, spec: SchedulerSpec
) -> None:
    class Flaky(Commands):
        def __call__(self, argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            if argv[1] == "bootstrap" and sum(call[1] == "bootstrap" for call in self.calls) == 0:
                self.calls.append(argv)
                return subprocess.CompletedProcess(argv, 5, b"", b"Bootstrap failed: 5: Input/output error")
            if argv[1] == "bootout" and self.answers.get("refuse"):
                self.calls.append(argv)
                return subprocess.CompletedProcess(argv, 1, b"", b"Operation not permitted")
            return super().__call__(argv, **kwargs)

    commands = Flaky()
    slept: list[float] = []
    launchd = LaunchdScheduler(agents_dir=tmp_path / "agents", uid=501, runner=commands, sleep=slept.append)
    assert launchd.ensure(spec) == "created" and slept == [1.0]
    commands.answers["refuse"] = 1
    with pytest.raises(SchedulerError, match="bootout"):
        launchd.remove(spec)
    assert launchd.plist.exists()


def test_the_loop_runner_logs_a_failed_cycle_and_keeps_going(tmp_path: Path) -> None:
    root = tmp_path / "state"
    calls: list[int] = []

    def cycle() -> None:
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom")
        os.kill(os.getpid(), signal.SIGTERM)

    run_loop(root, cycle=cycle, version="t", sleep=lambda _s: None, monotonic=lambda: 0.0, interval=0.0)
    assert len(calls) == 2 and "runner cycle failed: RuntimeError('boom')" in (root / "canonical-sync.log").read_text()
