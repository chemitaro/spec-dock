---
種別: "consultant-analysis"
ID: "iss-00023"
タイトル: "runtime CLI の責務分割と sync 状態導出リファクタの現状分析"
関連GitHub: ["#23", "https://github.com/chemitaro/spec-dock/issues/23"]
作成者: "Codex"
最終更新: "2026-03-11"
---

# Consultant Analysis Sheet — iss-00023

## 結論
- issue #23 の refactor は、当初の実害と保守上の急所を解消する目的には到達している。
- 判定は `merge-ready / 問題は実用上解消 / ただし構造改善は継続余地あり`。

## 何が解消されたか
- `sync` の責務集中は部分的に解消された。
  - `app.py` に `_IssueStatusResolution`, `_load_cached_issue_snapshot`, `_resolve_issue_statuses`, `_build_progress_map` が導入され、`_sync()` から状態導出責務が切り分けられた。
- cached status の意味が内部表現として明示された。
  - `source` により GitHub 由来と cache 由来をコード上で区別できる。
  - 既存 artifact schema は維持されている。
- README と runtime CLI 契約のズレは解消された。
  - `new adr` 誤記は `new doc adr` 契約へ修正済み。
- 検証の裏付けがある。
  - `python -m unittest discover -v` は `162 tests, OK`
  - code review: pass
  - spec review: requirement/design/plan/final diff/re-review すべて pass

## まだ残る課題
- アーキテクチャ上の大本課題は軽減であって消滅ではない。
  - helper は `app.py` 内に留まっており、module 境界としてはまだ `app.py` 中心。
- `sync` 以外の command 群は今回ほぼ untouched。
  - `deps check` / `active set` は互換確認対象であり、構造的整理は今後の課題。
- テスト構造の改善は未着手。
  - `tests/test_cli.py` は依然として巨大で、保守コストは高い。
- delivery hygiene の残件がある。
  - 差分は merge-ready だが、未コミット。

## 評価
- 「今回の refactor で問題は解消したか」への答えは `Yes, mostly`。
- ただし意味は限定的で、`sync` の読みづらさ・状態由来の曖昧さ・README 契約不整合は解消されたが、runtime 全体の再編が完了したわけではない。
- 実務上は、変更リスクを抑えつつ最も痛かった箇所を分離し、テストと spec で固めた合理的な第一段階と評価できる。

## 推奨アクション
1. この差分を commit / PR 化する。
2. 別 issue で `app.py` を command/domain 単位に module 分割する。
3. `tests/test_cli.py` を領域別に分割する。
4. README の CLI 例を将来的に機械検証する仕組みを検討する。
