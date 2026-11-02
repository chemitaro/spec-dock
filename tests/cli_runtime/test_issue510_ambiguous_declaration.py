"""A declaration that repeats a member is ambiguous: not schema 4 for business commands, still observed by raw doctor (iss-00510)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.cli_runtime.test_issue440_g4_doctor import doctor, unreadable_declaration
from tests.cli_runtime.test_issue440_schema3_stops import _run

if TYPE_CHECKING:
    from pathlib import Path

DUPLICATES = [
    b'{"schema_version":99,"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}\n',
    b'{"schema_version":4,"schema_version":4,"writer_protocol":"specdock.worktree-writer/v1"}\n',
]


@pytest.mark.parametrize("declaration", DUPLICATES)
@pytest.mark.parametrize("leaf", ["scope list", "workspace validate", "active show"])
def test_business_commands_refuse_a_duplicate_member_declaration(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    declaration: bytes,
    leaf: str,
) -> None:
    root = unreadable_declaration(tmp_path, monkeypatch, declaration)
    code, result = _run(capsys, root, leaf, [])
    assert code == 3 and result["status"] == "failed", result
    assert result["error"]["code"] == "PRECONDITION_FAILED", result["error"]
    assert result["effects"] == []
    assert (root / "spec-dock/workspace.json").read_bytes() == declaration


@pytest.mark.parametrize("declaration", DUPLICATES)
def test_raw_doctor_still_observes_a_duplicate_member_declaration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, declaration: bytes
) -> None:
    root = unreadable_declaration(tmp_path, monkeypatch, declaration)
    code, result, _ = doctor(root, capsys, "--raw")
    assert code == 7
    assert result["data"]["findings"][0]["details"]["classification"] == "invalid_json"
    assert result["effects"] == []
