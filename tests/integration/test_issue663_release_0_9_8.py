"""SpecDock 0.9.8: the version, its migration notes, and the upgrade path from the 0.9.7 assets (iss-00663)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from spec_dock.cli import main
from tests.integration.test_issue413_assets import uninitialized_worktree

if TYPE_CHECKING:
    import pytest
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/spec_dock/assets"
SCAFFOLD = ASSETS / "spec_dock"
F663 = ROOT / "tests/fixtures/issue663"
# Installed path -> (provider source, the bytes 0.9.7 shipped). A 0.9.7 consumer must be able to `installation update`.
CHANGED = {
    "spec-dock/docs/migration.md": (SCAFFOLD / "docs/migration.md", F663 / "migration.md.0.9.7.txt"),
    "spec-dock/system/spec-dock-version": (SCAFFOLD / "system/spec-dock-version", F663 / "spec-dock-version.0.9.7.txt"),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_the_migration_notes_describe_0_9_8_and_the_dogfood_copy_matches() -> None:
    text = (SCAFFOLD / "docs/migration.md").read_text("utf-8")
    headings = re.findall(r"^## (.+)$", text, re.M)
    assert headings.index("0.9.8 への更新") == headings.index("0.9.7 への更新") + 1
    [section] = re.findall(r"^## 0\.9\.8 への更新\n(.*?)(?=^## )", text, re.M | re.S)
    for token in (
        "installation update",
        "#649",
        "#658",
        "#659",
        "#660",
        "#661",
        "#662",
        "指揮の線",
        "画面の外",
        "裏",
        "ホップの弧",
        "上の縁",
        "矢じり",
        "24px",
        "向き",
        "欄の高さいっぱい",
        "全面",
        "片付けの候補",
        "矢印キー",
        "Shift",
        "`+`",
        "`-`",
        "`0`",
        "マウスのホイール",
        "トラックパッド",
        "ピンチ",
        "パンくず",
        "題名",
        "帯",
        "新しいタブで開く",
        "契約",
        "自動で起動し直",
        "0.9.7 に戻",
    ):
        assert token in section, token
    assert (ROOT / "spec-dock/docs/migration.md").read_bytes() == (SCAFFOLD / "docs/migration.md").read_bytes()


def test_the_inventory_accepts_the_0_9_7_bytes_once() -> None:
    entries = {
        item["path"]: item for item in json.loads((ASSETS / "static-inventory.json").read_text("utf-8"))["files"]
    }
    for relative, (source, previous) in CHANGED.items():
        entry = entries[relative]
        assert entry["sha256"] == _sha(source.read_bytes()), relative
        assert _sha(previous.read_bytes()) in entry["known_old_sha256"], relative
        assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"])), relative
        assert previous.read_bytes() != source.read_bytes(), relative


def _run(capsys: pytest.CaptureFixture[str], *arguments: str) -> tuple[int, dict[str, Any]]:
    code = main([*arguments, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_installation_update_upgrades_a_0_9_7_consumer(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = uninitialized_worktree(tmp_path / "consumer")
    assert _run(capsys, "installation", "init", str(target), "--yes")[0] == 0
    for relative, (_, previous) in CHANGED.items():
        (target / relative).write_bytes(previous.read_bytes())
    backup = tmp_path / "backup"
    code, applied = _run(
        capsys, "installation", "update", "--target", str(target), "--backup-dir", str(backup), "--yes"
    )
    assert (code, applied["status"]) == (0, "succeeded"), applied["error"]
    result = applied["data"]["result"]
    assert sorted(result["changed_paths"]) == sorted(CHANGED)
    assert result["created_paths"] == []
    for relative, (source, previous) in CHANGED.items():
        assert (target / relative).read_bytes() == source.read_bytes(), relative
        assert (backup / "static" / relative).read_bytes() == previous.read_bytes(), relative
