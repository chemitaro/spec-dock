"""The shipped CLI reference explains the repository list's parent, and no tier (iss-00613 T-07, iss-00635 T-04)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src/spec_dock/assets"
REFERENCE = ASSETS / "spec_dock/docs/reference_cli.md"
DOGFOOD = ROOT / "spec-dock/docs/reference_cli.md"
# The bytes before iss-00635 (iss-00614, never released): a consumer holding them can still update.
BEFORE_ISS_00635 = "bd8b72aff0b0829c84a39ead0db666f70bcfd8d67523749deb4bc0505e0f8eac"


def _section() -> str:
    text = REFERENCE.read_text(encoding="utf-8")
    start = text.index("\n## ダッシュボードのサーバーの契約\n")
    end = text.index("\n## ", start + 1)
    return text[start:end]


def _api_item() -> str:
    section = _section()
    item = section[section.index("\n- **API**：") :]
    return item[: item.index("\n- ", 1)]


def test_the_api_item_explains_parent() -> None:
    item = _api_item()
    assert "`GET /api/v1/repositories`の各リポジトリには" in item
    assert "`parent`（同じ応答の`repositories`にある親のリポジトリの鍵か`null`）" in item
    assert "いちばん近い出すリポジトリ" in item  # the nearest shown ancestor
    assert "名前の頭が同じだけのものと同じ道は含まない" in item
    assert "隠したリポジトリは親にならず" in item and "外の出す祖先の子" in item
    assert "クローンが2つのもの" in item and "絶対の道でない行" in item
    assert "チェックアウトとカタログの道は返しません" in item


def test_the_api_item_has_no_tier_labels_and_states_the_exception() -> None:
    item = _api_item()
    for word in (
        "段の札",
        "businesses",
        "products",
        "services",
        "事業",
        "プロダクト",
        "サービス",
        "ほかの名前はそのまま",
    ):
        assert word not in item, word
    assert "0.9.6 で消し" in item and "版の規則の例外" in item and "`tier`" in item
    # The rule itself stays as it is at the head of the section.
    assert "項目を足すのは版を変えずに行い、消すか意味を変えるときは版を上げます。" in _section()


def test_the_dogfood_copy_has_the_same_bytes() -> None:
    assert DOGFOOD.read_bytes() == REFERENCE.read_bytes()


def test_the_inventory_carries_the_new_reference() -> None:
    entries = {e["path"]: e for e in json.loads((ASSETS / "static-inventory.json").read_text())["files"]}
    entry = entries["spec-dock/docs/reference_cli.md"]
    assert entry["sha256"] == hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    assert len(entry["known_old_sha256"]) == len(set(entry["known_old_sha256"]))
    assert entry["sha256"] not in entry["known_old_sha256"]
    assert BEFORE_ISS_00635 in entry["known_old_sha256"]
