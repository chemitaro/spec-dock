"""iss-00474 AC-07/AC-09: schema 3 keeps creating Markdown Scopes and refuses the assurance arguments."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from tests.cli_runtime.test_issue413_scope_publish import publication_fixture

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("operation", ["create", "import"])
@pytest.mark.parametrize(
    "assurance",
    [
        ("--assurance", "standard", "--assurance-reason", "理由"),
        ("--assurance", "standard"),
        ("--assurance-reason", "理由"),
    ],
)
def test_the_assurance_arguments_stop_schema_3_before_any_effect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    operation: str,
    assurance: tuple[str, ...],
) -> None:
    from spec_dock.runtime.infra.tree_backup import tree_digest

    root, log = publication_fixture(tmp_path, monkeypatch)
    before = tree_digest(root)
    command = (
        ["scope", "create", "initiative", "--backend", "github", "--yes"]
        if operation == "create"
        else ["scope", "import", "github", "initiative", "gh:example/repo#413"]
    )
    code = main(["--project", str(root), *command, "--title", "Plan", *assurance, "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert (code, payload["error"]["code"]) == (3, "CANONICAL_NOT_MIGRATED"), payload
    assert "canonical mode" in payload["error"]["message"]
    assert payload["error"]["details"] == {"argument": assurance[0]}
    assert payload["recovery"]["instructions"]
    assert not log.exists() and tree_digest(root) == before


def test_schema_3_create_without_the_arguments_still_writes_the_markdown_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _log = publication_fixture(tmp_path, monkeypatch)
    assert (root / "spec-dock/templates/cue/initiative/requirement.cue").is_file()  # the new assets are there
    argv = ["--project", str(root), "scope", "create", "initiative", "--backend", "github", "--title", "Plan"]
    code = main([*argv, "--yes", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0, payload
    path = root / payload["data"]["result"]["scope"]["path"]
    names = sorted(item.name for item in path.iterdir())
    assert {"requirement.md", "design.md", "plan.md", "report.md"} <= set(names)
    assert not [name for name in names if name.endswith(".cue") or name == "explanation.html"]
