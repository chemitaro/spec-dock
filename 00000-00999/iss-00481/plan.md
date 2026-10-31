---
種別: 実装計画書（Issue）
ID: "iss-00481"
関連GitHub: ["#481"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
---

# iss-00481 Fix Template Link Tests In Linked Worktrees — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level
light。テストだけの小さな直しで、すぐ戻せる。

## 目標
この worktree で12件が通り、全体の lint とテストが通る。

## 順序・依存
Red の確認（済）→ 補助関数の追加と置き換え → Green → レビュー → 最終ゲート → PR。

## 実装step
1. `_lexical_resolve` を追加する。
2. 3箇所の `resolve()` を置き換える。
3. 同形の `resolve()` が `tests/` に残っていないか探す（調査済み: 他は `__file__` 基準か tmp_path）。

## 検証
`uv run pytest tests/unit/infra/test_authoring_kit_assets.py`、その後 `make lint` と `uv run pytest`。

## rollback
コミットを revert する。

## exit / handoff
PR をマージ可能な状態で止める。`work finish` は実行しない。
