---
種別: ADR（Architecture Decision Record）
ID: "adr-00002"
タイトル: "依存可視化の状態モデル（Done/Doing/Todo/Unknown など）"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-02-24"
親: ["iss-00009"]
---

# adr-00002 依存可視化の状態モデル（Done/Doing/Todo/Unknown など）

## 結論（Decision） (必須)
- **未決（TBD）**: この ADR は「議題が上がった時点」で作成し、結論はユーザー/レビュアーが最終決定した後に更新する。
- （注意）コーディングエージェントは、ユーザーの明示的な決定なしに結論を埋めない。
- ステータス運用:
  - 結論が未決の間は `状態: draft` のままにする
  - 結論が確定したら `accepted` にする
- 決定（決定後に記入）:
  - A

## 背景（Context） (必須)
- spec-dock は `sync --github` により GitHub Issue の `OPEN/CLOSED` を取得できるが、`In Progress` のシグナルは持たない。
- 依存グラフの可視化（PlantUML）では、状態で色分けして「次に着手できる/できない」を直感的に判断したい。
- ただし、状態の判定根拠が曖昧だと誤判定により運用を壊しやすい。

## 選択肢（Options considered） (必須)
- Option A: GitHub state + active のみで判定（MVP）
  - ルール（案）:
    - Done: GitHub `CLOSED`
    - Doing: `spec-dock/.agent/active.json` の current target と一致するノード
    - Todo: GitHub `OPEN` かつ Doing ではない
    - Unknown: GitHub 未参照 / `github.issue_number` 無し / `gh` で見つからない
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
- （暫定案）MVP は Option A を推奨（active を Doing の唯一のシグナルにする）。
- Option B は追加要件が固まった段階で拡張する（設定可能な label 名など）。

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
- `spec-on-dev/requirement.md`（Q-002）
