"""release-tag.yml tags only a push that raises the package to a new version of 0.3.0 or later (AC-434-08)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.canonical_check import commit, git, provider_root

if TYPE_CHECKING:
    from pathlib import Path

PROVIDER = provider_root()
SCRIPT = PROVIDER / ".github/scripts/release-tag-decision.py"
WORKFLOW = PROVIDER / ".github/workflows/release-tag.yml"
ZERO = "0" * 40


def _pyproject(version: str) -> str:
    return f'[project]\nname = "spec-dock"\nversion = "{version}"\n'


def _history(root: Path, *contents: str) -> list[str]:
    """Commit each pyproject.toml content in turn and return the commit IDs."""
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "--local", "maintenance.auto", "false")
    shas = []
    for index, content in enumerate(contents):
        (root / "pyproject.toml").write_text(content, encoding="utf-8")
        (root / "change.txt").write_text(str(index), encoding="utf-8")
        shas.append(commit(root, f"commit {index}"))
    return shas


def _decide(root: Path, before: str, after: str, output: Path | None = None) -> tuple[int, Any]:
    env = {key: value for key, value in os.environ.items() if key != "GITHUB_OUTPUT"}
    if output is not None:
        env["GITHUB_OUTPUT"] = str(output)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(root), "--before", before, "--after", after],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return result.returncode, (json.loads(result.stdout) if result.returncode == 0 else result.stderr)


@pytest.mark.parametrize(
    ("before", "after", "reason", "tag"),
    [
        ("0.2.4", "0.2.4", "version-unchanged", None),
        ("0.2.4", "0.2.5", "below-minimum", None),
        ("0.2.4", "0.3.0", "create", "v0.3.0"),
        ("0.3.0", "0.3.0", "version-unchanged", None),
        ("0.3.0", "0.4.0", "create", "v0.4.0"),
        ("0.3.0", "0.3.1rc1", "not-a-release-version", None),
        ("0.3.0", "1.0", "not-a-release-version", None),
    ],
)
def test_a_tag_is_created_only_for_a_changed_release_version_from_0_3_0(
    tmp_path: Path, before: str, after: str, reason: str, tag: str | None
) -> None:
    old, new = _history(tmp_path / "repo", _pyproject(before), _pyproject(after))
    output = tmp_path / "github-output"
    code, decision = _decide(tmp_path / "repo", old, new, output)
    assert code == 0, decision
    assert decision == {"tag": tag, "version": after, "previous": before, "reason": reason}
    assert output.read_text(encoding="utf-8") == f"tag={tag or ''}\n"


def test_an_existing_tag_is_never_recreated(tmp_path: Path) -> None:
    old, new = _history(tmp_path / "repo", _pyproject("0.3.0"), _pyproject("0.4.0"))
    git(tmp_path / "repo", "tag", "v0.4.0", old)
    code, decision = _decide(tmp_path / "repo", old, new)
    assert code == 0 and (decision["tag"], decision["reason"]) == (None, "tag-exists")


@pytest.mark.parametrize("before", ["zero", "unknown-commit", "no-pyproject"])
def test_an_unavailable_previous_version_never_tags(tmp_path: Path, before: str) -> None:
    shas = _history(tmp_path / "repo", "# no project table yet\n", _pyproject("0.3.0"))
    previous = {"zero": ZERO, "unknown-commit": "f" * 40, "no-pyproject": shas[0]}[before]
    code, decision = _decide(tmp_path / "repo", previous, shas[1])
    assert code == 0, decision
    assert decision == {"tag": None, "version": "0.3.0", "previous": None, "reason": "before-unavailable"}


def test_the_current_provider_version_tags_only_from_0_3_0(tmp_path: Path) -> None:
    """Before I-9 the package is below 0.3.0, so merging this change creates no tag; from 0.3.0 it would."""
    current = (PROVIDER / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version = "([0-9]+)\.([0-9]+)\.([0-9]+)"$', current, re.MULTILINE)
    assert version is not None
    released = tuple(int(part) for part in version.groups()) >= (0, 3, 0)
    old, new = _history(tmp_path / "repo", current.replace(version[0], 'version = "0.0.1"'), current)
    assert _decide(tmp_path / "repo", old, new)[1]["reason"] == ("create" if released else "below-minimum")
    assert _decide(tmp_path / "repo", new, new)[1]["reason"] == "version-unchanged"


@pytest.mark.parametrize("argument", ["--before", "--after"])
def test_malformed_commit_ids_are_usage_errors(tmp_path: Path, argument: str) -> None:
    old, new = _history(tmp_path / "repo", _pyproject("0.2.4"), _pyproject("0.3.0"))
    values = {"--before": old, "--after": new, argument: "HEAD"}
    code, stderr = _decide(tmp_path / "repo", values["--before"], values["--after"])
    assert code == 2 and "commit ID" in stderr


def test_the_workflow_runs_on_main_pushes_and_tags_only_on_the_decision() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "on:\n  push:\n    branches: [main]\n" in workflow and "pull_request" not in workflow
    assert "permissions:\n  contents: write\n" in workflow
    assert "fetch-depth: 0" in workflow
    assert "BEFORE: ${{ github.event.before }}" in workflow
    assert 'python3 .github/scripts/release-tag-decision.py --repo "$GITHUB_WORKSPACE"' in workflow
    assert '--before "$BEFORE" --after "$GITHUB_SHA"' in workflow
    assert "if: steps.decide.outputs.tag != ''" in workflow
    assert 'git tag "$TAG" "$GITHUB_SHA"' in workflow and 'git push origin "refs/tags/$TAG"' in workflow
    assert "--force" not in workflow and " -f " not in workflow
    assert '${{ github.event.before }}"' not in workflow
