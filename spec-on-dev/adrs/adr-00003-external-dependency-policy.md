---
種別: ADR（Architecture Decision Record）
ID: "adr-00003"
タイトル: "依存先の許容範囲（spec ツリー内限定か、外部 GitHub Issue も許可するか）"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-02-24"
親: ["iss-00009"]
---

# adr-00003 依存先の許容範囲（spec ツリー内限定か、外部 GitHub Issue も許可するか）

## 結論（Decision） (必須)
- **未決（TBD）**: この ADR は「議題が上がった時点」で作成し、結論はユーザー/レビュアーが最終決定した後に更新する。
- （注意）コーディングエージェントは、ユーザーの明示的な決定なしに結論を埋めない。
- ステータス運用:
  - 結論が未決の間は `状態: draft` のままにする
  - 結論が確定したら `accepted` にする
- 決定（決定後に記入）:
  - A

## 背景（Context） (必須)
- spec-dock の依存グラフは「spec ツリー（initiative/epic/issue）にある作業単位」を可視化する目的。
- 一方、現実の運用では「まだ import していない GitHub Issue」や「別レポの Issue」などを依存として参照したいケースがあり得る。
- 許可範囲を曖昧にすると、解決不能な参照やタイトル不明ノードが増え、可視化・判定が崩れる。

## 選択肢（Options considered） (必須)
- Option A: spec ツリー内ノードに限定（MVP）
  - 概要:
    - 依存先は「`meta.json` を持つノード（initiative/epic/issue）」に解決できるものだけ許可する。
    - GitHub issue number 参照も、ツリー内に一意に解決できる場合のみ許可する。
  - Pros:
    - 可視化/判定の境界が明確で、エラーが減る。
    - PlantUML のノードがすべてローカル spec と対応し、ドキュメントへ辿れる。
  - Cons:
    - “未 import の Issue に依存” を表現できない。
- Option B: 外部 GitHub Issue も許可（拡張）
  - 概要:
    - 依存先が spec ツリーに無くても、GitHub issue number が指定されていれば外部ノードとして扱う。
    - `gh` から title/state/url を取得し、依存可視化・ready 判定に反映する。
  - Pros:
    - 現実の依存関係（spec 化前も含む）を表現できる。
  - Cons:
    - ノードの保存先/ドキュメントへの導線が無い。
    - `gh` 取得が前提になりやすい。
    - 別レポや権限の違いなど、要件が増えやすい。

## 判断理由（Rationale） (必須)
- （暫定案）MVP は Option A を推奨（境界を明確化して壊れにくくする）。
- Option B は「本当に必要なユースケース」が具体化した段階で追加検討する。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - 依存可視化が spec ツリーと一致し、運用がシンプル。
- Negative / Debt（悪い点 / 将来負債）:
  - import していない依存を表現できない（運用で困る可能性）。
- 影響範囲（コード/テスト/運用/データ）:
  - 依存解決ロジック（id/number → ノード）
  - エラー設計（未解決参照の扱い）
  - PlantUML 表示（外部ノードの見せ方）

## 参考（References） (任意)
- `spec-on-dev/requirement.md`（Q-003）
