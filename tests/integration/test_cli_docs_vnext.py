"""The shipped operating guide follows the vNext command catalog."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shlex
import sys

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_scope_publish import publication_fixture

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets/spec_dock"
DOCS = ASSETS / "docs"


def test_workbench_templates_use_current_destination_flag() -> None:
    for kind in ("root", "initiative", "epic", "issue"):
        readme = (ASSETS / "templates" / kind / ".workbench/README.md").read_text(encoding="utf-8")
        assert "workbench copy --scope <full-id> --to-worktree <linked-worktree>" in readme
        assert "workbench copy --scope <full-id> --to <linked-worktree>" not in readme


def test_command_reference_covers_all_public_leaves() -> None:
    from spec_dock.runtime.cli.catalog import LEAF_PATHS

    reference = (DOCS / "reference_cli.md").read_text()
    for leaf in LEAF_PATHS:
        assert f"`{leaf}`" in reference, leaf
    assert len(LEAF_PATHS) == 44


def test_current_docs_do_not_instruct_removed_commands() -> None:
    current = [ROOT / "README.md", ROOT / "src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md"]
    current += [p for p in DOCS.rglob("*.md") if "historical" not in p.parts and p.name != "migration.md"]
    removed = re.compile(
        r"(?:\./spec-dock/scripts/)?spec-dock\s+(?:new|issue|deps|sync|validate|update|uninstall|delete|close)(?:\s|$)"
    )
    for path in current:
        assert not removed.search(path.read_text()), path


def test_offline_explanation_is_shipped_and_linked() -> None:
    guide = DOCS / "cli-redesign-guide.html"
    assert guide.exists()
    assert "<html" in guide.read_text().lower()
    assert "cli-redesign-guide.html" in (DOCS / "README.md").read_text()
    assert "reference_cli.md" in (DOCS / "README.md").read_text()


def readme_creation_commands() -> list[list[str]]:
    commands = [
        shlex.split(line)[1:]
        for line in (ROOT / "README.md").read_text().splitlines()
        if line.startswith("spec-dock scope create ")
    ]
    assert [command[2] for command in commands] == ["initiative", "epic", "issue"]
    return commands


def sequential_github_stub(executable: Path, log: Path) -> None:
    """A stateful external gh boundary: only created numbers can be read."""
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\nfrom pathlib import Path\n"
        f"log=Path({str(log)!r})\n"
        "argv=sys.argv[1:]; method=argv[argv.index('--method')+1]; endpoint=argv[argv.index('--method')+2]\n"
        "assert argv[:5]==['api','--hostname','github.com','--include','--method']\n"
        "rows=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []\n"
        "created=[row['number'] for row in rows if row['method']=='POST']\n"
        "if method=='POST':\n"
        " assert endpoint=='repos/example/repo/issues'\n"
        " payload=json.load(sys.stdin); number=501+len(created); title=payload['title']; status=201\n"
        "else:\n"
        " assert method=='GET'; number=int(endpoint.rsplit('/',1)[-1])\n"
        " assert endpoint==f'repos/example/repo/issues/{number}' and number in created\n"
        " title='Created parent'; status=200\n"
        "with log.open('a') as stream: stream.write(json.dumps(dict(method=method,number=number))+'\\n')\n"
        "response=dict(number=number,repository_url='https://api.github.com/repos/example/repo',\n"
        " html_url=f'https://github.com/example/repo/issues/{number}',title=title,state='open',\n"
        " state_reason=None,updated_at='2026-10-06T00:00:00Z')\n"
        "print(f'HTTP/2.0 {status} OK\\n\\n'+json.dumps(response))\n"
    )
    executable.chmod(0o755)


def test_readme_creation_examples_execute_noninteractively_and_keep_confirmation_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    sequential_github_stub(tmp_path / "gh-bin/gh", log)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    parent = None
    for index, command in enumerate(readme_creation_commands()):
        if parent is not None:
            command[command.index("--parent") + 1] = parent
        # No flags are supplied by the test to rescue an incomplete published example.
        assert "--json" in command and "--yes" in command
        before = tree_digest(root)
        requests = log.read_bytes() if log.exists() else b""
        assert main(["--project", str(root), *(word for word in command if word != "--yes")]) == 3
        rejected = json.loads(capsys.readouterr().out)
        assert rejected["error"]["code"] == "CONFIRMATION_REQUIRED" and rejected["effects"] == []
        assert tree_digest(root) == before
        assert (log.read_bytes() if log.exists() else b"") == requests
        assert main(["--project", str(root), *command]) == 0
        result = json.loads(capsys.readouterr().out)
        scope = result["data"]["result"]["scope"]
        assert scope["parent_id"] == parent
        assert scope["github_ref"] == f"gh:example/repo#{501 + index}"
        assert scope["id"] == f"{('init', 'epic', 'iss')[index]}-{501 + index:05d}"
        parent = scope["id"]
    assert [row["number"] for row in map(json.loads, log.read_text().splitlines()) if row["method"] == "POST"] == [
        501,
        502,
        503,
    ]


@pytest.mark.parametrize(
    "selector", ["init-00001", "gh:example/repo#1", "@current", "1", "https://github.com/example/repo/issues/1"]
)
def test_documented_scope_selector_boundary_is_readonly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], selector: str
) -> None:
    from tests.cli_runtime.test_issue413_active import select_fixture

    root, log = publication_fixture(tmp_path, monkeypatch)
    select_fixture(root)
    before = tree_digest(root)
    valid = selector in {"init-00001", "gh:example/repo#1", "@current"}
    assert main(["--project", str(root), "scope", "show", selector, "--json"]) == (0 if valid else 3)
    result = json.loads(capsys.readouterr().out)
    assert result["effects"] == []
    if valid:
        assert result["data"]["result"]["scope"]["id"] == "init-00001"
    assert tree_digest(root) == before and not log.exists()


def test_root_import_example_includes_repository_and_executes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, log = publication_fixture(tmp_path, monkeypatch)
    guide = (ROOT / "docs/github-issue-integration.md").read_text()
    command = next(shlex.split(line)[1:] for line in guide.splitlines() if line.startswith("spec-dock scope import "))
    assert "--github-repo" in command
    command[command.index("--github-repo") + 1] = "example/repo"
    command[command.index("--parent") + 1] = "init-00001"
    assert main(["--project", str(root), *command, "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data"]["result"]["scope"]["id"] == "epic-00124"
    assert all(row["method"] == "GET" for row in map(json.loads, log.read_text().splitlines()))
    assert "固定外部エンジン" not in guide
    assert "新規`--backend local`作成はできません" in guide


def test_current_operating_links_and_sync_examples_follow_observation_contract() -> None:
    from spec_dock.runtime.cli.options import parse_vnext

    guide = (ROOT / "docs/sync-aggregation.md").read_text()
    commands = [shlex.split(line)[1:] for line in guide.splitlines() if line.startswith("spec-dock ")]
    assert [parse_vnext(command).command_path for command in commands] == [
        "workspace validate",
        "workspace sync",
        "workspace sync",
        "workspace doctor",
    ]
    assert [parse_vnext(command).source for command in commands if command[:2] == ["workspace", "sync"]] == [
        "local",
        "github",
    ]
    assert "再生成せず" in guide and "unknown／partial" in guide and "自動修復しません" in guide
    agents = (ROOT / "AGENTS.md").read_text()
    current = agents.split("## SpecDock Agent-First Operations", 1)[1].split("## Dogfooding Warning", 1)[0]
    assert "PR #414 merged on 2026-10-04" in current
    assert "merge does not establish installation" in current
    assert "merge, and publication remain pending" not in current
    for relative in ("AGENTS.md", "docs/github-issue-integration.md", "docs/sync-aggregation.md"):
        path = ROOT / relative
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not link.startswith(("https:", "http:", "#")):
                assert (path.parent / link.split("#", 1)[0]).exists(), (relative, link)
    reference = (DOCS / "reference_cli.md").read_text()
    assert "裸番号＋`--github-repo OWNER/REPO`" in reference
    assert "裸番号・Issue URL・任意filesystem pathは使えません" in reference
