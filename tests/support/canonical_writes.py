"""A linked canonical clone for writing commands (iss-00432 CLI tests).

    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")
    code, payload = world.run("scope", "create", "epic", "--backend", "github", "--parent", "init-00001", ...)

The clone's commits carry the shipped templates and rules (scope creation copies them). GitHub is the fake on
PATH; the write clock records the spacing between writes instead of sleeping. State lives under a temporary
XDG_STATE_HOME. Nothing reaches the user's GitHub, state, tools or periodic jobs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spec_dock.runtime.application import canonical_writes
from spec_dock.runtime.domain.canonical_layout import scope_relative
from spec_dock.runtime.infra import github_snapshot, runtime_environment
from tests.support.canonical_repo import bare_remote, clone, environment, git, isolate_user_state
from tests.support.canonical_scopes import REPOSITORY, CanonicalWorld
from tests.support.fake_github import FakeGithub, install_fake_gh

if TYPE_CHECKING:
    import pytest

ASSETS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock"


def seeded_files() -> dict[str, bytes]:
    """The shipped Scope and Artifact templates and the Artifact rules, as committed checkout files."""
    files: dict[str, bytes] = {}
    for top in ("templates", "docs/rules"):
        for path in sorted((ASSETS / top).rglob("*")):
            if path.is_file():
                files[f"spec-dock/{path.relative_to(ASSETS).as_posix()}"] = path.read_bytes()
    return files


class WriteClock:
    """Real time plus an offset; sleeping is recorded and only advances the offset."""

    def __init__(self) -> None:
        self.offset = timedelta()
        self.sleeps: list[float] = []

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + self.offset

    def monotonic(self) -> float:
        return self.offset.total_seconds()

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.offset += timedelta(seconds=seconds)


@dataclass
class WriteWorld(CanonicalWorld):
    clock: WriteClock = field(default_factory=WriteClock)

    @classmethod
    def create(  # type: ignore[override]
        cls, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> WriteWorld:
        isolate_user_state(monkeypatch, tmp_path)
        monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: environment())
        github_snapshot.clear_memory()
        clock = WriteClock()
        monkeypatch.setattr(canonical_writes, "WRITE_CLOCK", clock)
        checkout = clone(bare_remote(tmp_path / "remote.git", files=seeded_files()), tmp_path / "main")
        world = cls(
            tmp_path,
            capsys,
            checkout,
            install_fake_gh(tmp_path, monkeypatch, FakeGithub(REPOSITORY)),
            tmp_path / "state",
            clock,
        )
        code, payload = world.run("canonical", "link")
        assert code == 0, payload
        git(checkout, "remote", "set-url", "origin", f"https://github.com/{REPOSITORY}.git")
        return world

    def write(self, *argv: str, checkout: Path | None = None) -> tuple[int, dict[str, Any]]:
        """Run a writing command with --yes."""
        return self.run(*argv, "--yes", checkout=checkout)

    def changesets(self) -> list[dict[str, Any]]:
        directory = self.catalog / ".runtime/changesets"
        if not directory.is_dir():
            return []
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]

    def writes(self) -> list[tuple[str, str, object]]:
        return [(item.method, item.endpoint, item.payload) for item in self.fake().writes()]

    def find(self, scope_id: str) -> Path:
        """The flat Scope directory <catalog>/<bucket>/<ID>/ (it must exist)."""
        found = self.catalog / scope_relative(scope_id)
        assert found.is_dir(), found
        return found
