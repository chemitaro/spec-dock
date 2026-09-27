"""The shared installation operation fixes every worktree target before writes."""

from __future__ import annotations

from dataclasses import replace
import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.installation.group_journal import (
    InstallationGroupRecord,
    InstallationTarget,
    child_operation_id,
    read_group_record,
    write_group_record,
)

if TYPE_CHECKING:
    from pathlib import Path


def _record(common: Path) -> InstallationGroupRecord:
    return InstallationGroupRecord(
        operation_id="a" * 32,
        action="update",
        common_dir=str(common),
        control_epoch=4,
        engine_digest="b" * 64,
        source_commit="c" * 40,
        source_digest="d" * 64,
        keep_maintenance=True,
        targets=(
            InstallationTarget("main", "/tmp/main", None, False),
            InstallationTarget("wt1", "/tmp/other", None, False),
        ),
        phase="preparing",
    )


def test_group_journal_roundtrips_target_progress_and_terminal_state(tmp_path: Path) -> None:
    common = tmp_path / "common"
    first = _record(common)
    write_group_record(common, first, create=True)
    assert read_group_record(common, first.operation_id) == first
    staged = replace(
        first,
        phase="staged",
        targets=tuple(
            replace(target, child_operation_id=str(index + 1) * 32) for index, target in enumerate(first.targets)
        ),
    )
    write_group_record(common, staged)
    assert read_group_record(common, first.operation_id) == staged
    committed = replace(
        staged, phase="committed", targets=tuple(replace(target, completed=True) for target in staged.targets)
    )
    write_group_record(common, committed)
    assert read_group_record(common, first.operation_id) == committed


def test_group_journal_rejects_incomplete_success_and_duplicate_targets(tmp_path: Path) -> None:
    common = tmp_path / "common"
    first = _record(common)
    with pytest.raises(ValueError, match="unstaged"):
        write_group_record(common, replace(first, phase="staged"), create=True)
    with pytest.raises(ValueError, match="target"):
        write_group_record(common, replace(first, targets=(first.targets[0], first.targets[0])), create=True)
    assert not (common / "spec-dock/control/installations").exists()


def test_group_journal_rejects_corruption_and_symlink(tmp_path: Path) -> None:
    common = tmp_path / "common"
    first = _record(common)
    write_group_record(common, first, create=True)
    path = common / "spec-dock/control/installations" / first.operation_id / "group.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["targets"][0]["root"] = "/tmp/other"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="target"):
        read_group_record(common, first.operation_id)
    path.unlink()
    path.symlink_to(tmp_path / "external")
    with pytest.raises(ValueError, match="redirected"):
        read_group_record(common, first.operation_id)


def test_child_operation_ids_are_stable_and_distinct() -> None:
    first = child_operation_id("a" * 32, "main")
    assert first == child_operation_id("a" * 32, "main")
    assert first != child_operation_id("a" * 32, "wt1")
    assert first != child_operation_id("b" * 32, "main")
    with pytest.raises(ValueError, match="identity"):
        child_operation_id("bad", "main")
