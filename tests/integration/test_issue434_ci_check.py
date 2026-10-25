"""spec-dock's own CI check builds a verified source wheel and runs canonical check on a checkout (AC-434-07)."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.support.canonical_check import (
    assets_with_ignore_rules,
    code_repository,
    commit,
    provider_root,
    source_checkout_with_ignore_rules,
)

if TYPE_CHECKING:
    from pathlib import Path

PROVIDER = provider_root()
SCRIPT = PROVIDER / ".github/scripts/specdock-ci-check.sh"
VALIDATE_SCRIPT = PROVIDER / ".github/scripts/specdock-ci-validate.sh"


def test_the_check_script_hardens_the_source_like_the_validate_script() -> None:
    check = SCRIPT.read_text(encoding="utf-8").splitlines()
    validate = VALIDATE_SCRIPT.read_text(encoding="utf-8").splitlines()
    assert check[-1] == '"$venv_root/bin/spec-dock" --project "$target_root" canonical check --json'
    assert [line for line in check if "usage:" not in line][:-1] == [line for line in validate if "usage:" not in line][
        :-1
    ]
    assert "usage: specdock-ci-check.sh SOURCE_CHECKOUT TARGET_CHECKOUT EXPECTED_SOURCE_SHA" in SCRIPT.read_text()


def _check(source: Path, target: Path, sha: str) -> subprocess.CompletedProcess[str]:
    before = tree_digest(source), tree_digest(target)
    result = subprocess.run(
        ["bash", str(SCRIPT), str(source), str(target), sha], capture_output=True, text=True, check=False
    )
    assert (tree_digest(source), tree_digest(target)) == before
    return result


def test_the_script_passes_a_clean_tree_and_fails_a_tree_with_specs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    sha = source_checkout_with_ignore_rules(source)
    target = code_repository(tmp_path / "consumer", assets_with_ignore_rules())

    passed = _check(source, target, sha)
    assert passed.returncode == 0, passed.stdout + passed.stderr
    assert f"SpecDock CI source={sha} wheel_sha256=" in passed.stdout
    result = json.loads(passed.stdout.splitlines()[-1])
    assert result["command"] == "canonical check" and result["data"]["result"]["valid"] is True
    assert result["warnings"] == []

    (target / "spec-dock/initiatives/init-00001-plan").mkdir(parents=True)
    (target / "spec-dock/initiatives/init-00001-plan/requirement.md").write_text("spec\n", encoding="utf-8")
    commit(target, "add a spec by mistake")
    failed = _check(source, target, sha)
    assert failed.returncode == 7, failed.stdout + failed.stderr
    result = json.loads(failed.stdout.splitlines()[-1])
    assert result["error"]["code"] == "CANONICAL_CHECK_FAILED"
    assert [item["code"] for item in result["data"]["result"]["failures"]] == ["SPEC_PATH_TRACKED"]


@pytest.mark.parametrize("case", ["sha-mismatch", "dirty-source", "short-sha"])
def test_the_script_rejects_an_untrusted_source_before_building(tmp_path: Path, case: str) -> None:
    source = tmp_path / "source"
    sha = source_checkout_with_ignore_rules(source)
    target = code_repository(tmp_path / "consumer", assets_with_ignore_rules())
    if case == "sha-mismatch":
        sha = "0" * 40
    elif case == "dirty-source":
        (source / "untracked.txt").write_text("uncommitted\n", encoding="utf-8")
    else:
        sha = sha[:12]
    rejected = subprocess.run(
        ["bash", str(SCRIPT), str(source), str(target), sha], capture_output=True, text=True, check=False
    )
    expected = {"sha-mismatch": (3, "SHA mismatch"), "dirty-source": (3, "is dirty"), "short-sha": (2, "commit ID")}
    code, message = expected[case]
    assert rejected.returncode == code and message in rejected.stderr
    assert "SpecDock CI source=" not in rejected.stdout
