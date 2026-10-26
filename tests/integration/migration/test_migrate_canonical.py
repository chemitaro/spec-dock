"""migrate.py build-canonical and cut against a bare origin (AC-435-02, 03, 04, 09, 19)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock.cli import main as spec_dock_main
from spec_dock.runtime.domain.canonical_content import CANONICAL_ROOT_FILES
from tests.support.canonical_repo import clone, git
from tests.support.migration_repo import ISSUE3, ROOT, build_legacy, legacy_specs, migrate_module, refs, write_files

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _tree(repository: Path, ref: str) -> dict[str, str]:
    output = git(repository, "ls-tree", "-r", "--full-tree", ref)
    return {line.split("\t", 1)[1]: line.split(" ")[2].split("\t")[0] for line in output.splitlines()}


def _blob(repository: Path, spec: str) -> bytes:
    import subprocess

    return subprocess.run(
        ["git", "-C", str(repository), "cat-file", "blob", spec], check=True, capture_output=True
    ).stdout


def test_build_canonical_pushes_the_renamed_split_with_format_one_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    writes = len(legacy.github.writes())
    main_refs = refs(legacy.main)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 0, result
    assert len(legacy.github.writes()) == writes
    assert refs(legacy.main) == main_refs  # nothing lands in the real .git
    remote = refs(legacy.remote)
    assert remote["refs/heads/spec-dock/canonical"] == result["data"]["canonical_commit"]
    tree = _tree(legacy.remote, "spec-dock/canonical")
    for name, payload in CANONICAL_ROOT_FILES.items():
        assert _blob(legacy.remote, f"spec-dock/canonical:{name}") == payload
    assert not [path for path in tree if path.endswith(".meta.json")]
    expected = {}
    for path, payload in legacy_specs().items():
        if path.endswith(".meta.json"):
            continue
        relative = path.removeprefix("spec-dock/initiatives/")
        relative = relative.replace("init-local-00002-", "init-00039-").replace("init-local-00003-", "init-00040-")
        expected[relative] = payload
    assert {path for path in tree if path not in CANONICAL_ROOT_FILES} == set(expected)
    for relative, payload in expected.items():
        assert _blob(legacy.remote, f"spec-dock/canonical:{relative}") == payload
    split = result["data"]["split_commit"]
    assert git(legacy.remote, "rev-parse", "spec-dock/canonical^") == split
    record = json.loads((legacy.records / "build.json").read_text())
    assert record["canonical_commit"] == result["data"]["canonical_commit"]
    code, again = legacy.run("build-canonical", apply=True)
    assert code == 0 and again["data"]["canonical_commit"] == result["data"]["canonical_commit"]
    assert refs(legacy.remote) == remote


def test_build_canonical_needs_the_id_map_and_never_forces_another_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 2 and "register --apply" in result["next_steps"]
    assert legacy.run("register", apply=True)[0] == 0
    other = clone(legacy.remote, tmp_path / "other")
    git(other, "checkout", "-q", "--orphan", "spec-dock/canonical")
    git(other, "rm", "-rfq", ".")
    write_files(other, {"x.md": b"x\n"})
    git(other, "add", "-A")
    git(other, "commit", "-qm", "foreign")
    git(other, "push", "-q", "origin", "spec-dock/canonical")
    before = refs(legacy.remote)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 2 and "nothing is forced" in result["error"]
    assert refs(legacy.remote) == before


def test_a_repository_without_scopes_builds_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch, specs={})
    (legacy.main / "spec-dock/initiatives").mkdir(parents=True)
    before = refs(legacy.remote)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 0, result
    assert "nothing to build" in "\n".join(result["messages"])
    assert refs(legacy.remote) == before
    code, result = legacy.run("move-local", str(legacy.main), apply=True)
    assert code == 0, result
    assert not (legacy.main / "spec-dock/initiatives").exists()
    assert not (legacy.main / "spec-dock/.canonical").exists()


def _cut_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, default_branch: str = "main"):
    legacy = build_legacy(tmp_path, monkeypatch, default_branch=default_branch)
    assert legacy.run("register", apply=True)[0] == 0
    assert legacy.run("build-canonical", apply=True)[0] == 0
    return legacy


def test_cut_branches_from_develop_with_the_sample_workflow_and_the_schema_four_declaration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = _cut_ready(tmp_path, monkeypatch, "develop")
    writes = len(legacy.github.writes())
    main_refs = refs(legacy.main)
    code, result = legacy.run("cut", apply=True)
    assert code == 0, result
    assert len(legacy.github.writes()) == writes and refs(legacy.main) == main_refs
    branch = "spec-dock/migrate-to-canonical"
    remote = refs(legacy.remote)
    assert git(legacy.remote, "rev-parse", f"{branch}^") == remote["refs/heads/develop"]
    tree = _tree(legacy.remote, branch)
    assert not [p for p in tree if p.startswith("spec-dock/initiatives")]
    module = migrate_module()
    asset = (ROOT / "src/spec_dock/assets/spec_dock/docs/ci/spec-dock-check.yml").read_bytes()
    workflow = _blob(legacy.remote, f"{branch}:.github/workflows/spec-dock-check.yml")
    assert workflow == asset.replace(b"branches: [main]", b"branches: [develop]", 1)
    declaration = _blob(legacy.remote, f"{branch}:spec-dock/workspace.json")
    assert (
        declaration
        == (ROOT / "src/spec_dock/assets/spec_dock/workspace.json").read_bytes()
        == module.WORKSPACE_V4_BYTES
    )
    assert [step["path"] for step in result["data"]["ci_steps"]] == [".github/workflows/ci.yml"] * 2
    checkout = clone(legacy.remote, tmp_path / "cut-checkout", "--branch", branch)
    assert spec_dock_main(["--project", str(checkout), "canonical", "check", "--json"]) == 0
    code, _again = legacy.run("cut", apply=True)
    assert code == 0 and refs(legacy.remote) == remote


def test_cut_refuses_without_static_files_canonical_or_after_spec_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    code, result = legacy.run("cut", apply=True)
    assert code == 2 and "build-canonical --apply" in result["next_steps"]
    assert legacy.run("register", apply=True)[0] == 0
    assert legacy.run("build-canonical", apply=True)[0] == 0
    legacy.commit_to_origin({f"{ISSUE3}/plan.md": b"# changed after build\n"}, "late spec edit")
    before = refs(legacy.remote)
    code, result = legacy.run("cut", apply=True)
    assert code == 2 and "changed since build-canonical" in result["error"]
    legacy.commit_to_origin({"spec-dock/system/spec-dock-version": None}, "drop version file")
    code, result = legacy.run("cut", apply=True)
    assert code == 2 and "0.3.0" in result["error"]
    assert refs(legacy.remote) == before | {"refs/heads/main": refs(legacy.remote)["refs/heads/main"]}
