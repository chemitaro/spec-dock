"""The shipped CLI reference explains the repository list's parent and tier (iss-00613 T-07, D-04)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets"
REFERENCE = ASSETS / "spec_dock/docs/reference_cli.md"


def _api_item() -> str:
    text = REFERENCE.read_text(encoding="utf-8")
    start = text.index("\n## ダッシュボードのサーバーの契約\n")
    end = text.index("\n## ", start + 1)
    section = text[start:end]
    item = section[section.index("\n- **API**：") :]
    return item[: item.index("\n- ", 1)]


def test_the_api_item_explains_parent_and_tier() -> None:
    item = _api_item()
    assert "`GET /api/v1/repositories`の各リポジトリには" in item
    assert "`parent`（同じ応答の`repositories`にある親のリポジトリの鍵か`null`）" in item
    assert "`tier`（文字列の配列）" in item
    assert "いちばん近い出すリポジトリ" in item  # the nearest shown ancestor
    assert "名前の頭が同じだけのものと同じ道は含まない" in item
    assert "いちばん近い登録された行" in item  # the labels count from the nearest registered row
    for name, label in (("businesses", "事業"), ("products", "プロダクト"), ("services", "サービス")):
        assert f"`{name}`→`{label}`" in item, name
    assert "ほかの名前はそのまま" in item
    assert "隠したリポジトリは親にならず" in item and "外の出す祖先の子" in item
    assert "クローンが2つのもの" in item and "絶対の道でない行" in item
    assert "チェックアウトとカタログの道は返しません" in item


def test_the_inventory_carries_the_new_reference() -> None:
    entries = {e["path"]: e for e in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    entry = entries["spec-dock/docs/reference_cli.md"]
    assert entry["sha256"] == hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"]))
    assert entry["sha256"] not in entry["known_old_sha256"]
