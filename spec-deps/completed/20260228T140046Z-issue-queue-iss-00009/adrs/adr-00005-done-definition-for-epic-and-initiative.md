---
種別: ADR（Architecture Decision Record）
ID: "adr-00005"
タイトル: "epic/initiative を依存先にしたときの Done 判定"
状態: "superseded"
作成者: "Codex CLI"
最終更新: "2026-02-27"
親: ["iss-00009"]
---

# adr-00005 epic/initiative を依存先にしたときの Done 判定

> Superseded by: `adr-00006-github-policy-and-derived-state-for-initiative-and-epic.md`

## 結論（Decision） (必須)
- 採用: Option C（A または B を満たせば Done）
- Done 判定ルール:
  - A: epic/initiative 自身の GitHub Issue が `CLOSED` なら Done
  - B: 配下 issue がすべて Done（`total > 0` かつ `done == total` かつ `open == 0` かつ `unknown == 0`）なら Done
    - 例外: `total == 0` の場合は B を満たさない（自動 Done を防ぐ）。この場合は A のみで Done を判定する。

## 背景（Context） (必須)
- 依存関係は issue だけでなく epic / initiative も依存先として指定できる必要がある（要件）。
- その場合、`deps check` / `active set` ガード / PlantUML 生成のために “Done” 判定が必要になる。
- しかし現状の spec-dock は epic/initiative に対して “完了” を定義していない（`sync` は issue の OPEN/CLOSED から progress を集計するのみ）。

## 選択肢（Options considered） (必須)
- Option A: epic/initiative 自身の GitHub Issue が `CLOSED` なら Done
  - Pros:
    - 直感的で分かりやすい（そのノードの issue 状態に従う）。
  - Cons:
    - 親 issue を閉じ忘れると永遠に blocked になる。
    - 親 issue を先に閉じると、未完了の子 issue があっても Done 扱いになり得る。
- Option B: 配下 issue がすべて Done なら Done
  - Done 条件（案）:
    - `done == total` かつ `open == 0` かつ `unknown == 0`
  - Pros:
    - 実態（実装単位）に沿った判定になり、閉じ忘れに強い。
  - Cons:
    - `unknown` があると Done にならない（local-only 運用に厳しい可能性）。
    - 子 issue が 0 件のときの扱いを別途決める必要がある。
- Option C: A または B を満たせば Done
  - Pros:
    - 運用の柔軟性がある。
  - Cons:
    - “いつ Done になるか” が曖昧になり、誤解が生まれやすい。

## 判断理由（Rationale） (必須)
- 理由:
  - 基本は B（実体 = issue 完了）を優先しつつ、A（親 issue を閉じた）も Done として扱える柔軟性を残すため。
  - 親 issue を先に閉じる運用がある場合でも依存判定が破綻しにくい。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - epic/initiative 依存を実用的に評価できる。
- Negative / Debt（悪い点 / 将来負債）:
  - Option B の場合、local-only（unknown）運用では Done 判定が厳しくなる。
- 影響範囲（コード/テスト/運用/データ）:
  - 依存解決ロジック（node の state 計算）
  - PlantUML の色分け（done/doing/todo/unknown/blocked）
  - docs: “Done の定義” の明文化

## 参考（References） (任意)
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/requirement.md`（Q-005）
