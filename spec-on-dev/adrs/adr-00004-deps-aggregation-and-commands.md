---
種別: ADR（Architecture Decision Record）
ID: "adr-00004"
タイトル: "依存の統合 SSOT（deps.json）をどのコマンドで生成するか"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-02-24"
親: ["iss-00009"]
---

# adr-00004 依存の統合 SSOT（deps.json）をどのコマンドで生成するか

## 結論（Decision） (必須)
- 採用: Option A（`sync` に統合して毎回生成）
- `sync` の追加生成物（git 管理しない。`spec-dock/.agent/` 配下）:
  - `deps.json`（依存グラフの統合 SSOT）
  - `deps.puml`（全体: Done を含む）
  - `deps.todo.puml`（todo-only: Done を除外）
- enrich:
  - `sync --github` で GitHub state を取得できる場合、状態（Done/Todo/Unknown）や Doing（active）を反映する

## 背景（Context） (必須)
- spec-dock は `sync` で `.agent/index.json` / `.agent/tree.json` を生成している。
- 依存関係も同様に「全体統合した SSOT（派生状態）」があると、エージェントや人間が参照しやすい。
- ただし、既存 `sync` の責務を増やしすぎると、コマンド体系が分かりにくくなる可能性がある。

## 選択肢（Options considered） (必須)
- Option A: `sync` に統合して毎回生成
  - 概要:
    - `sync` 実行時に `.agent/deps.json` と PlantUML も生成する（または `--deps` フラグで生成）。
  - Pros:
    - “状態集計” の一環として分かりやすい（ワンコマンド）。
  - Cons:
    - `sync` の責務・実行コストが増える。
    - deps のみ更新したいケースで過剰。
- Option B: `deps` コマンド群で生成（check/puml 等）
  - 概要:
    - `deps check` / `deps puml` などの実行時に `.agent/deps.json` を生成・更新する。
  - Pros:
    - 依存関連は `deps` に閉じ、`sync` の目的がブレない。
    - 必要な時だけ生成できる。
  - Cons:
    - “まず何を叩けば良いか” を docs で明確にしないと迷う。

## 判断理由（Rationale） (必須)
- 理由: “sync を回せば派生状態がすべて最新” を優先し、エージェント/人間の運用を単純化するため。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - コマンド責務が整理される（`sync` vs `deps`）。
- Negative / Debt（悪い点 / 将来負債）:
  - 生成タイミングが分かりにくいと、`.agent/deps.json` が古いまま参照されるリスク。
- 影響範囲（コード/テスト/運用/データ）:
  - CLI 構成（`argparse` サブコマンド）
  - docs（入口に “deps を回す” を明記）
  - tests（期待する生成物と失敗条件）

## 参考（References） (任意)
- `spec-on-dev/requirement.md`（Q-004）
