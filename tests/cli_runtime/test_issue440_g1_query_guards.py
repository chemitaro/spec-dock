"""Read-only leaves honor --expect-current/--expect-backend against one direct selection, in canonical mode.

Replaces tests/cli_runtime/test_issue413_query_guards.py (iss-00440), whose fixture was a schema-3 workspace.
Canonical reads load the GitHub structure snapshot before they check the guards, so the legacy "no GitHub GET
before the guard" counts become "no GitHub write and no effect"; the guard outcomes are the same.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.support.legacy_contracts_g1 import chain_world, select_record

if TYPE_CHECKING:
    from pathlib import Path

    from tests.support.canonical_scopes import CanonicalWorld

MATCHING = ("--expect-current", "gh:example/repo#3", "--expect-backend", "github")


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> CanonicalWorld:
    world = chain_world(tmp_path, monkeypatch, capsys)
    world.scope("epic", 4, "other", parent=1)
    return world


def _mismatch(guard: str, *, backend: str = "local") -> list[str]:
    return ["--expect-current", "gh:example/repo#1"] if guard == "current" else ["--expect-backend", backend]


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_branch_show_checks_expectations_and_preserves_the_direct_record(world: CanonicalWorld, guard: str) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("branch", "show", "@current", *_mismatch(guard))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("branch", "show", "@current", *MATCHING)
    assert code == 0, result
    assert result["effects"] == [] and record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_scope_show_checks_resolved_scope_expectations_before_success(world: CanonicalWorld, guard: str) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("scope", "show", "@current", *_mismatch(guard))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("scope", "show", "@current", *MATCHING)
    assert code == 0, result
    assert result["data"]["result"]["scope"]["id"] == "iss-00003"
    assert record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_active_show_checks_expectations_without_claiming_a_single_scope_backend(
    world: CanonicalWorld, guard: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("active", "show", *_mismatch(guard, backend="github"))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("active", "show", "--expect-current", "gh:example/repo#3")
    assert code == 0, result
    assert result["data"]["selection"]["scope_id"] == "iss-00003" and record.read_bytes() == before


@pytest.mark.parametrize("leaf", ["list", "check"])
@pytest.mark.parametrize("guard", ["current", "backend"])
def test_dependency_queries_apply_expectations_before_any_github_get(
    world: CanonicalWorld, leaf: str, guard: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    source = ["--source", "github"] if leaf == "check" else []
    code, result = world.run("dependency", leaf, "@current", *source, *_mismatch(guard))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("dependency", leaf, "@current", *source, *MATCHING)
    assert code == 0, result
    assert result["data"]["result"]["scope_id"] == "iss-00003"
    assert record.read_bytes() == before
    assert world.fake().writes() == []


@pytest.mark.parametrize("leaf", ["list", "show"])
@pytest.mark.parametrize("guard", ["current", "backend"])
def test_artifact_queries_check_owner_expectations_without_disclosing_or_changing_evidence(
    world: CanonicalWorld, leaf: str, guard: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    artifacts = world.catalog / world.relative("issue", 3) / "artifacts"
    artifacts.mkdir()
    evidence = artifacts / "20261001t000000z--private.bin"
    evidence.write_bytes(b"private evidence must remain opaque")
    operand = [evidence.name] if leaf == "show" else []
    code, result = world.run("artifact", leaf, *operand, "--scope", "@current", *_mismatch(guard))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("artifact", leaf, *operand, "--scope", "@current", *MATCHING)
    assert code == 0, result
    assert "private evidence must remain opaque" not in str(result)
    assert record.read_bytes() == before and evidence.read_bytes() == b"private evidence must remain opaque"


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_scope_list_checks_current_guard_and_rejects_a_backend_without_one_target(
    world: CanonicalWorld, guard: str
) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("scope", "list", *_mismatch(guard, backend="github"))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("scope", "list", "--expect-current", "gh:example/repo#3")
    assert code == 0, result
    assert {item["id"] for item in result["data"]["result"]["items"]} == {
        "init-00001",
        "epic-00002",
        "epic-00004",
        "iss-00003",
    }
    assert record.read_bytes() == before


@pytest.mark.parametrize("guard", ["current", "backend"])
def test_sync_checks_expectations_before_observing_remote_state(world: CanonicalWorld, guard: str) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    code, result = world.run("workspace", "sync", "--source", "github", *_mismatch(guard, backend="github"))
    assert code == 3, result
    assert result["effects"] == [] and record.read_bytes() == before
    code, result = world.run("workspace", "sync", "--source", "github", "--expect-current", "gh:example/repo#3")
    assert code == 0, result
    assert result["data"]["kind"] == "sync"
    assert record.read_bytes() == before
    assert world.fake().writes() == []


@pytest.mark.parametrize("leaf", ["list", "show"])
def test_root_artifact_query_checks_current_but_has_no_scope_backend(world: CanonicalWorld, leaf: str) -> None:
    record = select_record(world, "iss-00003", 3)
    before = record.read_bytes()
    artifacts = world.main / "spec-dock/artifacts"
    artifacts.mkdir()
    evidence = artifacts / "20261001t010000z--opaque.bin"
    evidence.write_bytes(b"opaque root evidence")
    operand = [evidence.name] if leaf == "show" else []
    # @root has no Scope backend: --expect-backend alone stops before any read (fixed in iss-00440 after G1's report).
    code, result = world.run("artifact", leaf, *operand, "--scope", "@root", "--expect-backend", "github")
    assert (code, result["error"]["code"]) == (3, "PRECONDITION_FAILED"), result
    assert "--expect-backend requires one existing Scope target" in result["error"]["message"]
    assert result["effects"] == []
    code, result = world.run("artifact", leaf, *operand, "--scope", "@root", "--expect-current", "gh:example/repo#1")
    assert code == 3, result
    assert result["effects"] == []
    code, result = world.run("artifact", leaf, *operand, "--scope", "@root", "--expect-current", "gh:example/repo#3")
    assert code == 0, result
    assert "opaque root evidence" not in str(result)
    assert record.read_bytes() == before and evidence.read_bytes() == b"opaque root evidence"
    assert not (world.main / ".git/spec-dock").exists()


@pytest.mark.parametrize("status", ["empty", "stale"])
def test_scope_query_current_guard_does_not_accept_empty_or_stale_selection(world: CanonicalWorld, status: str) -> None:
    record = select_record(world, "iss-00003", 999) if status == "stale" else None
    before = record.read_bytes() if record is not None else None
    code, result = world.run("scope", "show", "init-00001", "--expect-current", "gh:example/repo#1")
    assert code == 3, result
    assert result["effects"] == []
    assert record is None or record.read_bytes() == before
    code, result = world.run("scope", "show", "init-00001")
    assert code == 0, result
    assert result["data"]["result"]["scope"]["id"] == "init-00001"
