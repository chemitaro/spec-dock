"""A linked canonical clone with Scope directories and a fake GitHub on PATH (iss-00431 CLI tests).

    world = CanonicalWorld.create(tmp_path, monkeypatch, capsys)
    world.scope("initiative", 1, "plan")                 # GitHub Issue #1 with its catalog directory
    code, payload = world.run("scope", "show", "init-00001")

The clone's origin points at a temporary bare repository while `canonical link` runs; afterwards its URL is
changed to the fake GitHub repository, since reading commands never contact the remote. State lives under a
temporary XDG_STATE_HOME; the user's state, tools and GitHub are never touched.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from spec_dock.runtime.infra import github_snapshot, runtime_environment
from tests.support.canonical_repo import bare_remote, clone, environment, git, isolate_user_state
from tests.support.fake_github import FakeGithub, install_fake_gh

if TYPE_CHECKING:
    import pytest

    from tests.support.fake_github import FakeGhExecutable, FakeIssue

REPOSITORY = "example/repo"
DOCUMENTS = ("requirement.md", "design.md", "plan.md", "report.md")
_NESTING = {"epic": "epics", "issue": "issues"}
_PREFIX = {"initiative": "init", "epic": "epic", "issue": "iss"}


@dataclass
class CanonicalWorld:
    tmp_path: Path
    capsys: pytest.CaptureFixture[str]
    main: Path
    gh: FakeGhExecutable
    state: Path

    @classmethod
    def create(
        cls, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> CanonicalWorld:
        isolate_user_state(monkeypatch, tmp_path)
        monkeypatch.setattr(runtime_environment, "detect_runtime_environment", lambda *a, **k: environment())
        github_snapshot.clear_memory()
        checkout = clone(bare_remote(tmp_path / "remote.git"), tmp_path / "main")
        world = cls(tmp_path, capsys, checkout, install_fake_gh(tmp_path, monkeypatch, FakeGithub(REPOSITORY)), tmp_path / "state")
        code, payload = world.run("canonical", "link")
        assert code == 0, payload
        git(checkout, "remote", "set-url", "origin", f"https://github.com/{REPOSITORY}.git")
        return world

    @property
    def catalog(self) -> Path:
        return self.main / "spec-dock/.canonical"

    def run(self, *argv: str, checkout: Path | None = None) -> tuple[int, dict[str, Any]]:
        code = main(["--project", str(checkout or self.main), *argv, "--json"])
        captured = self.capsys.readouterr()
        return code, json.loads(captured.out)

    def fake(self) -> FakeGithub:
        return self.gh.load()

    def edit(self, change: Any) -> None:
        """Change the fake GitHub between commands: change(fake) runs on the persisted model."""
        fake = self.gh.load()
        change(fake)
        self.gh.save(fake)

    def scope(
        self,
        kind: str,
        number: int,
        slug: str,
        *,
        parent: int | None = None,
        title: str | None = None,
        directory: bool = True,
        documents: tuple[str, ...] = DOCUMENTS,
        **options: Any,
    ) -> FakeIssue:
        fake = self.gh.load()
        issue = fake.scope(kind, slug=slug, title=title, number=number, parent=parent, **options)
        self.gh.save(fake)
        if directory:
            self.directory(kind, number, slug, parent=parent, documents=documents)
        return issue

    def directory(
        self, kind: str, number: int, slug: str, *, parent: int | None = None, documents: tuple[str, ...] = DOCUMENTS
    ) -> Path:
        path = self.catalog / self.relative(kind, number, slug, parent=parent)
        path.mkdir(parents=True, exist_ok=True)
        for name in documents:
            (path / name).write_text(f"# {name}\n", encoding="utf-8")
        return path

    def relative(self, kind: str, number: int, slug: str, *, parent: int | None = None) -> Path:
        name = f"{_PREFIX[kind]}-{number:05d}-{slug}"
        if parent is None:
            return Path(name)
        found = next(self.catalog.rglob(f"*-{parent:05d}-*"))
        return found.relative_to(self.catalog) / _NESTING[kind] / name

    def requests(self) -> list[tuple[str, str, int]]:
        return [(item.method, item.endpoint.split("?")[0], item.status) for item in self.fake().requests]

    def age_probe(self, seconds: int = 120) -> None:
        """Make the last change check older than the display interval so the next display read probes."""
        probe = next(self.state.rglob("probe.json"))
        payload = json.loads(probe.read_text(encoding="utf-8"))
        old = datetime.now(timezone.utc) - timedelta(seconds=seconds)
        payload["checked_at"] = old.strftime("%Y-%m-%dT%H:%M:%SZ")
        probe.write_text(json.dumps(payload), encoding="utf-8")
