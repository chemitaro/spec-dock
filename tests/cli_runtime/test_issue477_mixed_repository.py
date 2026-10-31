"""One repository with Markdown and CUE Scopes side by side, through every command that touches them (iss-00477).

The CUE Issue is made by `scope create` and holds the sample of the CUE Authoring Guide, so the guide's sample
also passes in a Scope the CLI made (Epic epic-00425 AC-12; iss-00477 AC-08).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

import pytest

from spec_dock.runtime.application import canonical_scopes, canonical_work, canonical_writes
from spec_dock.runtime.application.canonical_catalog import catalog_changes
from spec_dock.runtime.infra import github_structure
from spec_dock.runtime.infra.github_structure import GithubRepository
from tests.support.canonical_repo import git
from tests.support.canonical_scopes import REPOSITORY
from tests.support.canonical_writes import WriteWorld
from tests.support.cue import cue_executable
from tests.support.cue_scopes import written_explanation

if TYPE_CHECKING:
    from tests.support.canonical_sync import FakeScheduler

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "src/spec_dock/assets/spec_dock/docs/authoring/cue.md"
REASON = "新しいコマンドを足すが、既存のコマンドは変えず、PR を戻せば元に戻る"


class _Clock:
    def __init__(self) -> None:
        self.offset = 0.0

    def now(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=self.offset)

    def monotonic(self) -> float:
        return self.offset

    def sleep(self, seconds: float) -> None:
        self.offset += seconds


def _guide_sample() -> dict[str, str]:
    blocks = re.findall(r"```cue\n// (requirement|design|plan)\.cue\n(.*?)```", GUIDE.read_text("utf-8"), re.DOTALL)
    return {f"{name}.cue": body for name, body in blocks}


@pytest.fixture
def world(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    periodic_jobs: dict[str, FakeScheduler],
) -> WriteWorld:
    cue_executable()
    world = WriteWorld.create(tmp_path, monkeypatch, capsys)
    git(world.main, "remote", "set-url", "origin", str(tmp_path / "remote.git"))
    repository = GithubRepository.parse(REPOSITORY)
    for module in (github_structure, canonical_writes, canonical_scopes):
        monkeypatch.setattr(module, "repository_for_checkout", lambda root, *, timeout: repository)
    monkeypatch.setattr(canonical_work, "SAVE_CLOCK", _Clock())
    world.scope("initiative", 1, "plan")
    world.scope("epic", 2, "core", parent=1)
    world.scope("issue", 3, "markdown leaf", parent=2)
    code, payload = world.write(
        "scope",
        "create",
        "issue",
        "--backend",
        "github",
        "--parent",
        "epic-00002",
        "--title",
        "CUE の葉",
        "--assurance",
        "standard",
        "--assurance-reason",
        REASON,
    )
    assert code == 0, payload
    assert payload["data"]["result"]["scope"]["id"] == "iss-00004"
    cue_leaf = world.find("iss-00004")
    for name, body in _guide_sample().items():
        (cue_leaf / name).write_text(body, encoding="utf-8")
    (cue_leaf / "explanation.html").write_text(written_explanation(), encoding="utf-8")
    with catalog_changes(world.catalog.resolve(), command="test setup") as changes:
        for kind, number in (("initiative", 1), ("epic", 2), ("issue", 3), ("issue", 4)):
            changes.add(world.relative(kind, number).as_posix())
    assert world.run("canonical", "sync")[0] == 0
    for scheduler in periodic_jobs.values():
        scheduler.simulate_run = False

        def kick() -> None:
            code, payload = world.run("canonical", "sync")
            assert code == 0, payload

        scheduler.on_kick = kick
    return world


def _result(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["data"]["result"]


def test_reading_commands_treat_each_format_by_its_own_rules(world: WriteWorld) -> None:
    code, payload = world.run("scope", "show", "iss-3")
    assert code == 0 and _result(payload)["assurance"]["source"] == "unset"
    code, payload = world.run("scope", "show", "iss-4")
    assert code == 0, payload
    assurance = _result(payload)["assurance"]
    assert (assurance["source"], assurance["level"], assurance["reason"]) == ("cue", "standard", REASON)

    code, payload = world.run("scope", "check", "iss-3")
    assert code == 0 and _result(payload)["checked"] is False, payload
    code, payload = world.run("scope", "check", "iss-4")
    assert code == 0, payload
    assert _result(payload)["checked"] is True
    assert (_result(payload)["errors"], payload["warnings"]) == ([], [])

    code, payload = world.run("scope", "render", "iss-4")
    assert code == 0, payload
    html = _result(payload)["html"]
    assert "R-01" in html and "S-03" in html and "T-03" in html
    code, payload = world.run("scope", "render", "iss-3")
    assert (code, payload["error"]["code"]) == (7, "SCOPE_NOT_CUE")

    code, payload = world.run("workspace", "validate", "--require-nodes")
    assert code == 0 and _result(payload)["findings"] == [], payload
    code, payload = world.run("workspace", "doctor")
    assert not [item for item in payload["data"]["findings"] if item["code"].startswith("SCOPE_")], payload


def test_work_start_and_finish_follow_each_format(world: WriteWorld) -> None:
    plan = world.find("iss-00004") / "plan.cue"
    correct = plan.read_text(encoding="utf-8")
    code, payload = world.run("work", "start", "iss-4", "--base", "HEAD")
    assert code == 0, payload
    plan.write_text(correct.replace('verifies: ["R-02"]', 'verifies: ["R-01"]'), encoding="utf-8")
    code, payload = world.write("work", "finish", "iss-4")
    assert (code, payload["error"]["code"]) == (3, "SCOPE_CHECK_FAILED"), payload
    [error] = payload["error"]["details"]["errors"]
    assert (error["code"], error["details"]["rule"]) == ("SPEC_FINDINGS", "requirement-without-test")
    assert payload["effects"] == [] and world.fake().issue(4).state == "open"

    plan.write_text(correct, encoding="utf-8")
    code, payload = world.write("work", "finish", "iss-4")
    assert code == 0, payload
    assert world.fake().issue(4).state == "closed"

    code, payload = world.run("work", "start", "iss-3", "--base", "HEAD")
    assert code == 0, payload
    code, payload = world.write("work", "finish", "iss-3")
    assert code == 0, payload
    assert world.fake().issue(3).state == "closed"
    assert world.run("active", "show")[1]["data"]["selection"]["status"] != "selected"
