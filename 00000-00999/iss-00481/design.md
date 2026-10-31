---
種別: 設計書（Issue）
ID: "iss-00481"
関連GitHub: ["#481"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md"]
---

# iss-00481 Fix Template Link Tests In Linked Worktrees — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標
リンク解決を、ファイルシステムのリンクをたどらない、道筋の上だけの計算にする。

## Current / Target
- Current: `(node_path.parent / link).resolve()` が、`initiatives` のリンクをたどって main 側へ移る。
- Target: `os.path.normpath` で `..` を畳み、`scaffold_root` 配下の道筋と比べる。

## 責務・Interface
テスト内の小さな補助関数 `_lexical_resolve(path: Path) -> Path`（`Path(os.path.normpath(path))`）を足し、該当箇所で `.resolve()` の代わりに使う。

## data / failure
畳んだ道筋は `scaffold_root/docs/authoring/<ガイド>` になる。ここは実在の場所なので `is_file()` で存在を確かめられる。行き先が違えば比較で、無ければ `is_file()` で失敗する。

## 変更対象
`test_authoring_kit_assets.py` の、旧入れ子の置き場に基づく3箇所（`_relative_link_violations`、RDP ガイドのテスト、report ガイドのテスト）。ほかの `resolve()`（`__file__` の親や tmp_path の正規化）は、旧入れ子の置き場ではないので変えない。

## 移行・互換性・rollback
テストのみ。コミットを戻せば元に戻る。

## testability
修正前に12件が落ち、修正後に通ることで確かめる。

## risk
`..` を畳む結果が実際のリンクの行き先と異なる場合があるが、ここでは雛形を置く場所の道筋の意味を確かめたいので、意図に合う。
