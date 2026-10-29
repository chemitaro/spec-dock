"""The five dashboard files keep the 2026-09-21 shape (iss-00438, AC-438-02).

The samples were copied from spec-dock's main checkout before the canonical cutover. The same Scopes are
built on the fake GitHub; a full read gives the snapshot and the drawn files must equal the samples except
for the allowed differences: the Observability line, and local IDs that canonical mode cannot create.
"""

from __future__ import annotations

from pathlib import Path
import re

from spec_dock.runtime.application.canonical_dashboard import render_dashboard_files
from spec_dock.runtime.domain.canonical_dashboard import DASHBOARD_FILES
from spec_dock.runtime.infra.github_snapshot import SnapshotStore, StructureSnapshotService, clear_memory
from spec_dock.runtime.infra.github_structure import GithubApi, GithubRepository, GithubStructureClient
from tests.support.fake_github import FakeGithub

SAMPLES = Path(__file__).resolve().parents[2] / "fixtures/issue438/legacy-dashboard"
LOCAL_IDS = {"init-local-00002": "init-00900", "init-local-00003": "init-00901"}  # keeps the sample order
SNAPSHOT_PATH = Path("/state/spec-dock/github/github.com/example/repo/snapshot.json")
_PACKAGE = re.compile(r'^( *)package "([^"\\]+)\\n(.*)" as N\w+ \{$')
_RECTANGLE = re.compile(r'^ *rectangle "([^"\\]+)\\n\[([A-Z]+)\]" as N\w+ #\w+$')
_LISTED = re.compile(r"^- `([^`]+)` (.*)$")


def _canonical(text: str) -> str:
    for local, numbered in LOCAL_IDS.items():
        text = text.replace(local, numbered).replace(local.replace("-", "_"), numbered.replace("-", "_"))
    return text


def _number(scope: str) -> int:
    return int(scope.rsplit("-", 1)[1])


def _sample_world() -> FakeGithub:
    """Initiatives, Epics and Issues of tree-all.puml with their states; READY titles from dashboard.md."""
    titles = {}
    for line in (SAMPLES / "dashboard.md").read_text(encoding="utf-8").splitlines():
        matched = _LISTED.match(line)
        if matched:
            titles[matched.group(1)] = matched.group(2)
    fake = FakeGithub("example/repo")
    parents: dict[int, int] = {}
    for line in _canonical((SAMPLES / "tree-all.puml").read_text(encoding="utf-8")).splitlines():
        package = _PACKAGE.match(line)
        if package:
            indent, scope, title = package.groups()
            kind = "initiative" if len(indent) == 2 else "epic"
            parent = None if kind == "initiative" else parents[2]
            fake.scope(kind, title=title, number=_number(scope), parent=parent)
            parents[len(indent)] = _number(scope)
            continue
        rectangle = _RECTANGLE.match(line)
        if rectangle:
            scope, state = rectangle.groups()
            done = state == "DONE"
            fake.scope(
                "issue",
                title=titles.get(scope, f"Done {scope}"),
                number=_number(scope),
                parent=parents[4],
                state="closed" if done else "open",
                state_reason="completed" if done else None,
            )
    return fake


def _drawn(fake: FakeGithub, tmp_path: Path) -> dict[str, str]:
    repository = GithubRepository.parse("example/repo")
    clear_memory()
    service = StructureSnapshotService(
        repository,
        store=SnapshotStore(tmp_path / "state", repository),
        client=GithubStructureClient(repository, GithubApi(runner=fake, clock=fake.clock)),
        clock=fake.clock,
    )
    return render_dashboard_files(service.ensure_fresh("cycle").require(), snapshot_path=SNAPSHOT_PATH)


def test_the_five_files_equal_the_samples_except_the_observability_line(tmp_path: Path) -> None:
    drawn = _drawn(_sample_world(), tmp_path)
    assert tuple(drawn) == DASHBOARD_FILES
    for name in DASHBOARD_FILES:
        expected = _canonical((SAMPLES / name).read_text(encoding="utf-8"))
        if name == "dashboard.md":
            expected = expected.replace("- index: `spec-dock/.agent/index.json`", f"- snapshot: `{SNAPSHOT_PATH}`")
        assert drawn[name].splitlines() == expected.splitlines(), name
        assert drawn[name].endswith("@enduml\n" if name.endswith(".puml") else "(none)\n")


def test_japanese_and_quoted_titles_are_escaped_as_plantuml_strings(tmp_path: Path) -> None:
    fake = FakeGithub("example/repo")
    initiative = fake.scope("initiative", title='仕様の "正本" を集める')
    epic = fake.scope("epic", title="ダッシュボード\\作り直し", parent=initiative.number)
    fake.scope("issue", title="日本語の題名", parent=epic.number, labels=("spec-dock:in-progress",))
    drawn = _drawn(fake, tmp_path)
    assert 'package "init-00001\\n仕様の \\"正本\\" を集める" as Ninit_00001 {' in drawn["tree.puml"]
    assert 'package "epic-00002\\nダッシュボード\\\\作り直し" as Nepic_00002 {' in drawn["tree-all.puml"]
    assert 'rectangle "iss-00003\\n[DOING]" as Niss_00003 #DAE8FC' in drawn["tree.puml"]
    assert "## Doing\n- `iss-00003` 日本語の題名\n" in drawn["dashboard.md"]
    assert 'rectangle "iss-00003\\nissue\\nDoing" as Niss_00003 #DAE8FC' in drawn["deps-issues.puml"]
