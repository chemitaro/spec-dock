"""migrate.py build-canonical and cut against a bare origin (AC-435-02, 03, 04, 09, 19, AC-456-03)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock.cli import main as spec_dock_main
from spec_dock.runtime.domain.canonical_content import CANONICAL_ROOT_FILES
from tests.support.canonical_repo import clone, git
from tests.support.migration_repo import (
    INIT,
    ISSUE3,
    ROOT,
    build_legacy,
    flat_path,
    legacy_specs,
    meta,
    migrate_module,
    refs,
    write_files,
)

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


def _flat_tree(repository: Path, commit: str) -> None:
    """Every Scope directory is <bucket>/<ID>/, nothing is nested and no .meta.json is left."""
    import re

    for path in _tree(repository, commit):
        if path in CANONICAL_ROOT_FILES:
            continue
        bucket, scope, *rest = path.split("/")
        number = int(scope.split("-")[1])
        assert re.fullmatch(r"(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})", scope), path
        assert bucket == migrate_module().scope_bucket(number), path
        assert rest and rest[0] not in ("epics", "issues"), path
        assert not path.endswith(".meta.json"), path


def _commits(repository: Path, ref: str) -> list[str]:
    return git(repository, "rev-list", ref).splitlines()


def test_build_canonical_pushes_the_flattened_history_with_format_one_files(
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
    expected = {flat_path(path): payload for path, payload in legacy_specs().items() if not path.endswith(".meta.json")}
    assert {path for path in tree if path not in CANONICAL_ROOT_FILES} == set(expected)
    for relative, payload in expected.items():
        assert _blob(legacy.remote, f"spec-dock/canonical:{relative}") == payload
    commits = _commits(legacy.remote, "spec-dock/canonical")
    for commit in commits:
        _flat_tree(legacy.remote, commit)
    assert git(legacy.remote, "rev-parse", "spec-dock/canonical^") == result["data"]["flat_commit"]
    assert result["data"]["history"] == {"commits": 1, "dropped_commits": 0, "dropped_paths": {}, "examples": {}}
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


def test_build_canonical_refuses_structure_anomalies_found_in_metadata_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.support.migration_repo import ISSUE4, meta

    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    legacy.commit_to_origin(
        {
            f"{ISSUE4}/.meta.json": meta(
                "issue", "iss-00004", "Delta", "delta", 4, parent="init-00001", depends_on=("iss-00003",)
            )
        },
        "broken after register",
    )
    before = refs(legacy.remote)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 2
    assert {"KIND_RULE", "DEPENDENCY_CYCLE"} <= {item["code"] for item in result["anomalies"]}
    assert refs(legacy.remote) == before


def test_git_environment_overrides_do_not_redirect_the_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "elsewhere.git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "foreign-index"))
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 0, result
    assert not (tmp_path / "foreign-index").exists()


def test_history_commits_drop_what_cannot_be_flattened_and_stay_flat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    old_local = "spec-dock/initiatives/init-local-00009-dropped"
    legacy.commit_to_origin(
        {
            f"{INIT}/epics/new-epic/requirement.md": b"# placeholder\n",
            f"{old_local}/.meta.json": meta("initiative", "init-local-00009", "Dropped", "dropped", None),
            f"{old_local}/requirement.md": b"# never registered\n",
            f"{ISSUE3}/plan.md": b"# Gamma plan, first edit\n",
        },
        "old layout",
    )
    legacy.commit_to_origin(
        {
            f"{INIT}/epics/new-epic/requirement.md": None,
            f"{old_local}/.meta.json": None,
            f"{old_local}/requirement.md": None,
            f"{ISSUE3}/plan.md": b"# Gamma plan\n",
        },
        "tidy",
    )
    assert legacy.run("register", apply=True)[0] == 0
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 0, result
    history = result["data"]["history"]
    assert history["commits"] == 3 and history["dropped_commits"] == 1
    assert history["dropped_paths"] == {
        "FLATTEN_NESTED_FILE": 1,
        "FLATTEN_SCOPE_UNMAPPED": 1,
    }  # .meta.json is never kept
    assert history["examples"]["FLATTEN_SCOPE_UNMAPPED"] == ["init-local-00009-dropped"]
    commits = _commits(legacy.remote, "spec-dock/canonical")
    assert len(commits) == 4
    for commit in commits:
        _flat_tree(legacy.remote, commit)
    middle = commits[2]
    assert _blob(legacy.remote, f"{middle}:00000-00999/iss-00003/plan.md") == b"# Gamma plan, first edit\n"
    subjects = git(legacy.remote, "log", "--format=%s", "spec-dock/canonical").splitlines()
    assert subjects == ["spec-dock: migrate to canonical", "tidy", "old layout", "legacy seed"]


def test_a_tip_that_cannot_be_flattened_stops_plan_and_build_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    legacy.commit_to_origin({f"{INIT}/epics/stray.md": b"# not in a child Scope\n"}, "stray")
    code, result = legacy.run("plan")
    assert code == 1
    problems = result["data"]["flatten"]["problems"]
    assert [(item["code"], item["path"]) for item in problems] == [
        ("FLATTEN_NESTED_FILE", "init-00001-alpha/epics/stray.md")
    ]
    assert all(item["blocking"] is False for item in problems)  # register is not stopped by a path problem
    assert legacy.run("register", apply=True)[0] == 0
    before = refs(legacy.remote)
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 2 and "cannot be flattened" in result["error"]
    assert "FLATTEN_NESTED_FILE" in {item["code"] for item in result["anomalies"]}
    assert refs(legacy.remote) == before


def test_verify_checks_the_flat_layout_of_origins_canonical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    assert legacy.run("build-canonical", apply=True)[0] == 0
    code, result = legacy.run("verify")
    assert code == 0, result
    assert result["data"]["canonical_layout"] == [] and result["data"]["canonical_meta_json"] == []
    other = clone(legacy.remote, tmp_path / "canonical-editor", "--branch", "spec-dock/canonical")
    git(other, "mv", "00000-00999/iss-00004", "iss-00004")
    write_files(other, {"00000-00999/epic-00002/issues/iss-00009/x.md": b"x\n", "01000-01999/iss-00003/y.md": b"y\n"})
    write_files(other, {"00000-00999/iss-00003/.meta.json": b"{}\n"})
    git(other, "add", "-A")
    git(other, "commit", "-qm", "misplaced")
    git(other, "push", "-q", "origin", "HEAD:spec-dock/canonical")
    code, result = legacy.run("verify")
    assert code == 1
    mismatches = "\n".join(result["data"]["mismatches"])
    for text in (
        "iss-00004/requirement.md in canonical is not",
        "00000-00999/epic-00002/issues in canonical is a nested leftover",
        "01000-01999/iss-00003 in canonical is not",
        "iss-00004: canonical has no 00000-00999/iss-00004/",
        "the canonical branch has .meta.json",
    ):
        assert text in mismatches, (text, mismatches)


def _old_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, version: str) -> None:
    """A git on PATH that reports `version` and splits like git-subtree of Ubuntu 22.04 to 24.04."""
    import os
    import shutil
    import sys

    real = shutil.which("git")
    folder = tmp_path / "old-git"
    folder.mkdir()
    wrapper = folder / "git"
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import os, subprocess, sys\n"
        "args = sys.argv[1:]\n"
        f"if args and args[-1] == '--version':\n    print('git version {version}'); sys.exit(0)\n"
        "if 'subtree' in args:\n"
        "    if '--quiet' in args:\n        print('error: unknown option `quiet', file=sys.stderr); sys.exit(129)\n"
        "    cwd = args[args.index('-C') + 1] if '-C' in args else '.'\n"
        "    prefix = next((a.split('=', 1)[1] for a in args if a.startswith('--prefix=')), None)\n"
        "    if prefix and not os.path.exists(os.path.join(cwd, prefix)):\n"
        "        print(f\"fatal: '{prefix}' does not exist; use 'git subtree add'\", file=sys.stderr); sys.exit(1)\n"
        f"sys.exit(subprocess.call([{real!r}, *args]))\n"
    )
    wrapper.chmod(0o755)
    monkeypatch.setenv("PATH", f"{folder}{os.pathsep}{os.environ['PATH']}")


def test_build_canonical_works_with_the_git_subtree_of_older_distributions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    assert legacy.run("register", apply=True)[0] == 0
    _old_git(tmp_path, monkeypatch, "2.34.1")
    code, result = legacy.run("build-canonical", apply=True)
    assert code == 0, result
    _flat_tree(legacy.remote, "spec-dock/canonical")


def test_a_git_older_than_the_script_needs_is_refused_before_anything_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = build_legacy(tmp_path, monkeypatch)
    _old_git(tmp_path, monkeypatch, "2.30.2")
    before = refs(legacy.remote)
    for command in ("plan", "build-canonical"):
        code, result = legacy.run(command)
        assert code == 2 and "git 2.31 or newer" in result["error"], result
    assert legacy.github.requests == [] and refs(legacy.remote) == before
