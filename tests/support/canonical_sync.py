"""Two clones of one bare origin for periodic-sync tests: an injected clock, PC names and fake schedulers.

pair = SyncPair.create(tmp_path, monkeypatch, capsys)   # both clones linked with --no-schedule
pair.write(pair.a, "x.md", "text"); pair.advance(31); pair.sync(pair.a)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from spec_dock.runtime.application import canonical_sync
from spec_dock.runtime.domain.canonical_sync_state import CatalogSyncState
from spec_dock.runtime.infra import canonical_scheduling, runtime_environment
from spec_dock.runtime.infra.canonical_scheduling import EnsureOutcome, SchedulerObservation
from spec_dock.runtime.infra.canonical_state import read_catalog_state
from spec_dock.runtime.infra.github_structure import GithubApi
from tests.support.canonical_repo import bare_remote, clone, environment, git, isolate_user_state

if TYPE_CHECKING:
    from collections.abc import Callable
    import subprocess

    import pytest

    from spec_dock.runtime.domain.canonical_scheduler import SchedulerSpec


class SyncClock:
    """Real time plus an offset the test advances; sleeping only advances the offset."""

    def __init__(self) -> None:
        self.offset = timedelta()

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + self.offset

    def monotonic(self) -> float:
        return self.offset.total_seconds()

    def sleep(self, seconds: float) -> None:
        self.offset += timedelta(seconds=seconds)


@dataclass
class FakeScheduler:
    """Records every call; `on_kick` may run a cycle in-process to stand in for the job."""

    kind: str = "launchd"
    calls: list[tuple[str, str]] = field(default_factory=list)
    specs: list[SchedulerSpec] = field(default_factory=list)
    installed: bool = False
    fail_ensure: bool = False
    on_kick: Callable[[], object] | None = None
    recorded: Path | None = None
    simulate_run: bool = False  # a kick records a successful cycle for every registered catalog
    tail: str = "/usr/bin:/bin"  # the fixed end of the job's PATH

    def needs_change(self, spec: SchedulerSpec) -> bool:
        return not self.installed or (self.specs[-1] != spec if self.specs else True)

    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]:
        return ()

    def recorded_executable(self, spec: SchedulerSpec) -> Path | None:
        return self.recorded

    def recorded_state_root(self, spec: SchedulerSpec) -> Path | None:
        return self.specs[-1].state_root if self.installed and self.specs else None

    def recorded_search_path(self, spec: SchedulerSpec) -> str | None:
        if not self.specs:
            return None
        return self.specs[-1].search_path(self.tail)

    def ensure(self, spec: SchedulerSpec) -> EnsureOutcome:
        self.calls.append(("ensure", self.kind))
        if self.fail_ensure:
            raise canonical_scheduling.SchedulerError("launchctl bootstrap failed: Input/output error")
        changed = self.needs_change(spec)
        created = not self.installed
        self.installed = True
        self.specs.append(spec)
        self.recorded = spec.executable
        return "created" if created else ("updated" if changed else "unchanged")

    def kick(self, spec: SchedulerSpec) -> None:
        self.calls.append(("kick", self.kind))
        if self.on_kick is not None:
            self.on_kick()
        elif self.simulate_run:
            record_successful_cycle(spec.state_root)

    def remove(self, spec: SchedulerSpec) -> bool:
        self.calls.append(("remove", self.kind))
        existed, self.installed = self.installed, False
        return existed

    def observe(self, spec: SchedulerSpec) -> SchedulerObservation:
        return SchedulerObservation(self.installed, self.installed)


def _no_gh(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
    raise OSError("gh api is not reachable from the tests")


@dataclass
class SyncPair:
    tmp_path: Path
    monkeypatch: pytest.MonkeyPatch
    capsys: pytest.CaptureFixture[str]
    remote: Path
    a: Path
    b: Path
    clock: SyncClock
    schedulers: dict[str, FakeScheduler]

    @classmethod
    def create(
        cls,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        *,
        link: bool = True,
        **environment_options: Any,
    ) -> SyncPair:
        isolate_user_state(monkeypatch, tmp_path)
        monkeypatch.setattr(
            runtime_environment,
            "detect_runtime_environment",
            lambda *args, **kwargs: environment(**environment_options),
        )
        clock = SyncClock()
        monkeypatch.setattr(canonical_sync, "SYNC_CLOCK", clock)
        monkeypatch.setattr(canonical_sync, "hostname", lambda: "pc-test")
        # Step 7 never reaches the real GitHub: a test that needs `gh api` installs its own fake.
        monkeypatch.setattr(canonical_sync, "github_api_for", lambda cwd: GithubApi(runner=_no_gh, cwd=cwd))
        schedulers: dict[str, FakeScheduler] = {}

        def scheduler_for(kind: str, **_kwargs: object) -> FakeScheduler:
            return schedulers.setdefault(kind, FakeScheduler(kind))

        monkeypatch.setattr(canonical_scheduling, "scheduler_for", scheduler_for)
        monkeypatch.setattr(canonical_scheduling, "spec_dock_executable", lambda: Path("/opt/spec-dock/bin/spec-dock"))
        remote = bare_remote(tmp_path / "remote.git")
        a = clone(remote, tmp_path / "a")
        pair = cls(tmp_path, monkeypatch, capsys, remote, a, a, clock, schedulers)
        if link:
            code, result = pair.run(a, "canonical", "link", "--no-schedule")
            assert code == 0, result
        pair.b = clone(remote, tmp_path / "b")
        if link:
            code, result = pair.run(pair.b, "canonical", "link", "--no-schedule")
            assert code == 0, result
        return pair

    @property
    def state_root(self) -> Path:
        return self.tmp_path / "state" / "spec-dock"

    def run(self, checkout: Path, *argv: str) -> tuple[int, dict[str, Any]]:
        self.capsys.readouterr()
        code = main(["--project", str(checkout), *argv, "--json"])
        output = self.capsys.readouterr()
        return code, json.loads(output.out)

    def sync(self, checkout: Path, *extra: str, pc: str | None = None) -> tuple[int, dict[str, Any]]:
        if pc is not None:
            self.monkeypatch.setattr(canonical_sync, "hostname", lambda: pc)
        return self.run(checkout, "canonical", "sync", *extra)

    def advance(self, seconds: float) -> None:
        self.clock.sleep(seconds)

    @staticmethod
    def catalog(checkout: Path) -> Path:
        return checkout / "spec-dock/.canonical"

    def specs(self, checkout: Path) -> Path:
        return checkout / "spec-dock/initiatives"

    def write(self, checkout: Path, relative: str, text: str) -> Path:
        path = self.specs(checkout) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        stamp = self.clock.now().timestamp()
        os.utime(path, (stamp, stamp))  # written "now" on the injected clock
        return path

    def state(self, checkout: Path) -> CatalogSyncState | None:
        return read_catalog_state(self.state_root, os.path.realpath(self.catalog(checkout)))

    def remote_head(self) -> str:
        return git(self.remote, "rev-parse", "refs/heads/spec-dock/canonical")

    def remote_file(self, relative: str) -> str | None:
        completed = git(self.remote, "cat-file", "-p", f"refs/heads/spec-dock/canonical:{relative}", check=False)
        return completed or None


def catalog_result(result: dict[str, Any]) -> dict[str, Any]:
    (item,) = result["data"]["catalogs"]
    return item


def record_successful_cycle(state_root: Path) -> None:
    """Stand in for a working job: every registered catalog gets an ok cycle with push_auth ok."""
    from spec_dock.runtime.domain.canonical_structure import format_timestamp
    from spec_dock.runtime.domain.canonical_sync_state import LastCycle, PushAuth
    from spec_dock.runtime.infra.canonical_registry import read_registry
    from spec_dock.runtime.infra.canonical_state import update_catalog_state

    stamp = format_timestamp(canonical_sync.SYNC_CLOCK.now())
    for entry in read_registry(state_root).catalogs:

        def mutate(current: CatalogSyncState | None, catalog: str = entry.catalog) -> CatalogSyncState:
            state = current or CatalogSyncState.new(catalog, at=stamp)
            return state.evolve(last_cycle=LastCycle(stamp, stamp, "ok"), push_auth=PushAuth("ok", stamp))

        update_catalog_state(state_root, entry.catalog, mutate)
