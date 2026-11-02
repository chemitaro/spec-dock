"""SpecDock 0.5.0 reads only schema 4: a schema-3 declaration stops every command before effects (iss-00440).

R-440-01: the business commands other than `canonical check` stop with CANONICAL_NOT_MIGRATED (exit 3), with no
effects, warnings or file changes, and point at SpecDock 0.4.2 and the migration notes of its v0.4.2 tag.
`canonical check` keeps reporting the schema-3 declaration as one failure with the same next step; help and
completion never read a declaration; schema 5 and later stay PRECONDITION_FAILED.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import pytest

from spec_dock.cli import main
from spec_dock.runtime.cli.catalog import LEAF_PATHS
from spec_dock.runtime.infra.tree_backup import tree_digest

UTILITIES = frozenset({"help", "completion"})
NEXT_STEP = (
    "This repository is not migrated (workspace schema 3); reinstall SpecDock 0.4.2 and follow "
    "scripts/migrate-to-canonical/README.md at the v0.4.2 tag to migrate it."
)


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", "-C", str(root), *arguments], check=True, capture_output=True)


def unmigrated_repository(root: Path, *, schema: int = 3) -> Path:
    """A committed repository as an unmigrated 0.4.2 consumer left it: a schema-3 declaration and nested specs."""
    root.mkdir(parents=True)
    _git(root, "init", "--initial-branch=main", "-q")
    _git(root, "config", "--local", "maintenance.auto", "false")
    _git(root, "config", "user.name", "Fixture")
    _git(root, "config", "user.email", "fixture@example.invalid")
    workspace = root / "spec-dock"
    scope = workspace / "initiatives/init-00001-fixture"
    scope.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps({"schema_version": schema, "writer_protocol": "specdock.worktree-writer/v1"}) + "\n",
        encoding="utf-8",
    )
    (scope / ".meta.json").write_text(json.dumps({"schema_version": 3, "id": "init-00001"}) + "\n", encoding="utf-8")
    for name in ("requirement.md", "design.md", "plan.md", "report.md"):
        (scope / name).write_text("# Fixture\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    return root


def _arguments(root: Path, tmp_path: Path) -> dict[str, list[str]]:
    elsewhere = str(tmp_path / "elsewhere")
    reason = ["--assurance", "light", "--assurance-reason", "fixture"]
    return {
        "scope create initiative": ["--backend", "github", "--title", "Plan", *reason],
        "scope create epic": ["--backend", "github", "--parent", "init-00001", "--title", "Plan", *reason],
        "scope create issue": ["--backend", "github", "--parent", "epic-00002", "--title", "Plan", *reason],
        "scope import github initiative": ["1", "--title", "Plan", *reason],
        "scope import github epic": ["2", "--parent", "init-00001", "--title", "Plan", *reason],
        "scope import github issue": ["3", "--parent", "epic-00002", "--title", "Plan", *reason],
        "scope list": [],
        "scope show": ["init-00001"],
        "scope check": ["init-00001"],
        "scope render": ["init-00001"],
        "scope edit": ["init-00001", "--title", "Plan"],
        "scope close": ["init-00001"],
        "scope reopen": ["init-00001"],
        "scope delete": ["init-00001"],
        "scope move": ["epic-00002", "--parent", "init-00001"],
        "active show": [],
        "active set": ["init-00001"],
        "active clear": ["--all"],
        "work start": ["init-00001"],
        "work finish": ["init-00001"],
        "branch show": ["init-00001"],
        "branch create": ["init-00001", "--base", "main"],
        "branch switch": ["init-00001"],
        "dependency list": ["init-00001"],
        "dependency check": ["init-00001"],
        "dependency add": ["--from", "init-00001", "--to", "init-00004"],
        "dependency remove": ["--from", "init-00001", "--to", "init-00004"],
        "artifact create": ["--scope", "init-00001", "--type", "blank", "--title", "Note"],
        "artifact import file": [str(root / "README.md"), "--scope", "init-00001"],
        "artifact list": ["--scope", "init-00001"],
        "artifact show": ["blank-note", "--scope", "init-00001"],
        "worktree create": ["side", "--base", "main"],
        "worktree list": [],
        "worktree show": [elsewhere],
        "worktree remove": [elsewhere],
        "worktree bootstrap": [elsewhere],
        "workspace sync": [],
        "workspace validate": [],
        "workspace doctor": [],
        "canonical link": [],
        "canonical status": [],
        "installation show": [],
        "installation init": [str(root)],
        "installation update": [],
        "installation uninstall": [],
        "canonical sync": [],
        "canonical accept": ["--deletions"],
        "canonical restore": [],
        "canonical resume": [],
        "canonical remove": [],
    }


def _run(capsys: pytest.CaptureFixture[str], root: Path, leaf: str, arguments: list[str]) -> tuple[int, Any]:
    code = main(["--project", str(root), *leaf.split(), *arguments, "--json"])
    output = capsys.readouterr()
    assert output.err == "", output.err
    return code, json.loads(output.out)


def _assert_not_migrated(code: int, result: dict[str, Any], leaf: str) -> None:
    assert code == 3, (leaf, result)
    assert result["status"] == "failed", leaf
    assert result["error"]["code"] == "CANONICAL_NOT_MIGRATED", (leaf, result["error"])
    assert result["error"]["message"] == f"{leaf} needs a migrated repository; this workspace declares schema 3"
    assert result["recovery"]["instructions"] == [NEXT_STEP], leaf
    assert result["effects"] == [] and result["warnings"] == [], leaf


def test_every_business_command_but_canonical_check_stops_on_a_schema_three_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = unmigrated_repository(tmp_path / "consumer")
    arguments = _arguments(root, tmp_path)
    assert set(arguments) == set(LEAF_PATHS) - UTILITIES - {"canonical check"}
    assert len(arguments) == 50
    before = tree_digest(root)
    for leaf, extra in arguments.items():
        code, result = _run(capsys, root, leaf, extra)
        _assert_not_migrated(code, result, leaf)
    assert tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / "spec-dock/.canonical").exists()


@pytest.mark.parametrize(
    ("leaf", "extra"),
    [
        ("workspace doctor", ["--raw"]),
        ("workspace doctor", ["--raw", "--legacy"]),
        ("scope show", ["init-00001", "--dry-run"]),
        ("work start", ["init-00001", "--dry-run"]),
        ("installation update", ["--dry-run"]),
        ("installation show", ["--expect-current", "init-00001"]),
        ("active show", ["--expect-current", "init-00001"]),
        ("worktree create", ["side", "--base", "main", "--expect-current", "init-00001"]),
    ],
)
def test_raw_dry_run_and_expectation_variants_stop_the_same_way(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], leaf: str, extra: list[str]
) -> None:
    root = unmigrated_repository(tmp_path / "consumer")
    before = tree_digest(root)
    code, result = _run(capsys, root, leaf, extra)
    _assert_not_migrated(code, result, leaf)
    assert tree_digest(root) == before


def test_a_schema_three_worktree_of_an_installation_target_stops_installation_with_an_explicit_target(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = unmigrated_repository(tmp_path / "consumer")
    before = tree_digest(root)
    for leaf in ("installation show", "installation update", "installation uninstall"):
        code = main([*leaf.split(), "--target", str(root), "--json"])
        result = json.loads(capsys.readouterr().out)
        _assert_not_migrated(code, result, leaf)
    code = main(["installation", "init", str(root), "--yes", "--json"])
    _assert_not_migrated(code, json.loads(capsys.readouterr().out), "installation init")
    assert tree_digest(root) == before


def test_canonical_check_reports_the_schema_three_declaration_with_the_same_next_step(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = unmigrated_repository(tmp_path / "consumer")
    code, result = _run(capsys, root, "canonical check", [])
    assert code == 7 and result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    failures = {item["code"]: item for item in result["data"]["result"]["failures"]}
    assert failures["WORKSPACE_NOT_MIGRATED"]["details"]["next_step"] == NEXT_STEP
    assert result["effects"] == []


@pytest.mark.parametrize("schema", [5, "4", None])
def test_other_unknown_declarations_stay_precondition_failures(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], schema: object
) -> None:
    root = unmigrated_repository(tmp_path / "consumer", schema=schema)  # type: ignore[arg-type]
    for leaf, extra in (("scope list", []), ("workspace validate", []), ("active show", [])):
        code, result = _run(capsys, root, leaf, extra)
        assert code == 3 and result["error"]["code"] == "PRECONDITION_FAILED", (leaf, result)
        assert "schema 4" in result["error"]["message"]
        assert result["effects"] == []


def test_help_and_completion_work_inside_a_schema_three_repository(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = unmigrated_repository(tmp_path / "consumer")
    monkeypatch.chdir(root)
    for argv in (["help", "scope", "show"], ["completion", "zsh"], ["scope", "show", "--help"]):
        assert main(argv) == 0, argv
        assert capsys.readouterr().out
    assert main(["help", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "succeeded"


def test_no_runtime_code_accepts_schema_three_or_reads_metadata() -> None:
    """AC-440-03: the code search of the removal; `.meta.json` remains only in the canonical checks that report it."""
    import spec_dock.runtime

    runtime = Path(spec_dock.runtime.__file__).parent
    sources = {path.relative_to(runtime).as_posix(): path.read_text(encoding="utf-8") for path in runtime.rglob("*.py")}
    assert sorted(path for path, text in sources.items() if ".meta.json" in text) == [
        "application/canonical_check.py",  # SCOPE_METADATA_TRACKED: a committed .meta.json fails the CI check
        "application/canonical_workspace.py",  # SCOPE_METADATA_PRESENT: a .meta.json left in the catalog warns
    ]
    for name in (
        "LEGACY_WORKSPACE_SCHEMA",
        "workspace_mode",
        "probe_workspace_mode",
        "WorkspaceMode",
        "scope_metadata",
    ):
        assert not [path for path, text in sources.items() if name in text], name
    assert [path for path, text in sources.items() if "NOT_MIGRATED_WORKSPACE_SCHEMA: Final = 3" in text] == [
        "application/project_context.py"
    ]
    for removed in (
        "application/direct_migration.py",
        "application/direct_workbench.py",
        "application/start_snapshot.py",
        "infra/scope_tree.py",
        "infra/fs_repo.py",
        "infra/committed_validation.py",
    ):
        assert removed not in sources, removed
