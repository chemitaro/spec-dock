---
種別: ADR（Architecture Decision Record）
ID: "adr-00002"
タイトル: "依存可視化の状態モデル（Done/Doing/Todo/Unknown など）"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-02-27"
親: ["iss-00009"]
---

# adr-00002 依存可視化の状態モデル（Done/Doing/Todo/Unknown など）

## 結論（Decision） (必須)
- 採用: Option A（GitHub state + active のみ）
- 状態モデル（MVP）:
  - Done:
    - issue: GitHub `CLOSED`
    - epic/initiative: 配下 issue の集計で `open == 0` かつ `unknown == 0`（`total == 0` も Done 扱い）
  - Doing:
    - issue: `spec-dock/.agent/active.json` の leaf（`issue`）と一致するノード
    - epic/initiative: active leaf が配下に存在するノード（= 配下で作業中）
  - Todo:
    - issue: GitHub `OPEN` かつ Doing ではない
    - epic/initiative: Done/Doing/Unknown ではない（= 未完了だが active は無い）
  - Unknown:
    - issue: GitHub 未参照 / `github.issue_number` 無し / `gh` で見つからない
    - epic/initiative: 配下 issue の集計で `unknown > 0`
  - Blocked: 依存が未解決（open/unknown 等）で ready ではない（表示用の導出状態）

## 背景（Context） (必須)
- spec-dock は `sync --github` により GitHub Issue の `OPEN/CLOSED` を取得できるが、`In Progress` のシグナルは持たない。
- 依存グラフの可視化（PlantUML）では、状態で色分けして「次に着手できる/できない」を直感的に判断したい。
- ただし、状態の判定根拠が曖昧だと誤判定により運用を壊しやすい。

## 選択肢（Options considered） (必須)
- Option A: GitHub state + active のみで判定（MVP）
  - ルール（案）:
    - Done:
      - issue: GitHub `CLOSED`
      - epic/initiative: 配下 issue の集計で `open == 0` かつ `unknown == 0`（`total == 0` も Done 扱い）
    - Doing:
      - issue: `spec-dock/.agent/active.json` の current target と一致するノード
      - epic/initiative: active leaf が配下に存在するノード
    - Todo:
      - issue: GitHub `OPEN` かつ Doing ではない
      - epic/initiative: Done/Doing/Unknown ではない
    - Unknown:
      - issue: GitHub 未参照 / `github.issue_number` 無し / `gh` で見つからない
      - epic/initiative: 配下 issue に Unknown が存在する
    - Blocked: 依存が未解決（open/unknown 等）で ready ではない（表示用に追加）
  - Pros:
    - 取得・実装が簡単で壊れにくい。
    - 人間/エージェントが “今やっているもの” を明示できる（active）。
  - Cons:
    - “未着手” と “作業中（active 以外）” の区別がつかない。
- Option B: GitHub label / Projects status を参照して Doing を判定
  - 例（案）:
    - label: `in-progress` / `doing` / `wip`
    - Projects v2 の Status フィールド
  - Pros:
    - 状態表現が豊かになり、可視化の精度が上がる。
  - Cons:
    - 取得が複雑（API/gh の制約、リポジトリ差、権限）。
    - 運用ルール（ラベル付け等）が増える。

## 判断理由（Rationale） (必須)
- 理由: 判定根拠が明確で壊れにくく、runtime script の責務/依存を増やさずに実装できる。
- 補足: label / Projects status による拡張は、運用ルールが固まった段階で追加検討する。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - 初期実装がシンプルで、判定根拠が説明しやすい。
- Negative / Debt（悪い点 / 将来負債）:
  - “In Progress” の粒度が粗くなる（active 以外は Todo 扱い）。
- 影響範囲（コード/テスト/運用/データ）:
  - `deps check` 出力の state 表現
  - PlantUML の色分け・凡例・フィルタ（todo-only）
  - docs: 状態判定の説明
- 移行/ロールバック:
  - 追加の状態判定（label 等）は後方互換で追加可能。

## 参考（References） (任意)
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/requirement.md`（Q-002）
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/adrs/adr-00006-github-policy-and-derived-state-for-initiative-and-epic.md`
