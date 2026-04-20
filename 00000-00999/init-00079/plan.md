---
種別: 計画書（Initiative）
ID: "init-00079"
タイトル: "minor bugfix maintenance"
関連GitHub: ["#79"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-04-17"
依存: ["requirement.md", "design.md"]
---

# init-00079 minor bugfix maintenance — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - dogfooding で見つかった minor bug を、既存 reusable bucket の中で継続的に issue 化できるようにする。
- 対象 metric:
  - Metric-001
  - Metric-002

## マイルストーン
- M1:
  - deliverable:
    - `init-00079 / epic-00080` の boundary と out-of-scope が docs に固定されている
  - exit:
    - initiative / epic requirement / design / plan がテンプレート状態を脱している
- M2:
  - deliverable:
    - first minor bug issue が `epic-00080` 配下へ作成されている
  - exit:
    - `iss-00082` が active issue として spec 化され、research を伴って追跡可能になっている

## Epic ポートフォリオ
- epic-00080-minor-bug-fixes:
  - 目的:
    - repo-local actionable bug を single-issue 単位で受け入れる。
  - deliverable:
    - issue spec と evidence を伴う minor bug 対応トラック
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - なし

## 順序と理由
- sequencing rationale:
  - まず reusable bucket の guardrail を固定し、その後 concrete issue を追加する。
  - 各 issue は互いに独立な minor bug として扱い、必要なものだけ active にする。
- parallelizable:
  - issue spec 作成は並行可能だが、active issue は 1 つずつ切り替えて運用する。

## 意思決定ゲート
- G1 strategy review:
  - その bug report は repo-local actionable bug か
- G2 milestone readiness:
  - 親 bucket docs が issue 作成の guardrail として十分か
- G3 governance/docs impact:
  - issue scope に external consumer concern を混ぜていないか
- G9 final initiative plan review:
  - 追加された issue が reusable bucket の趣旨に沿っているか

## 指標レビュー計画
- review timing:
  - issue 作成ごと
- dashboard / source:
  - `spec-dock/.agent/index.json`
  - issue requirement / design / plan / report

## ロールアウト計画
- rollout window:
  - dogfooding 中に bug report が actionable と判定された時点
- release / communication:
  - issue docs と GitHub issue を正本とする

## Epic readiness contract
- Epic に要求する最低条件:
  - repo-local bug と external issue の境界が明確
  - single actionable issue へ分割できる
  - evidence を issue research / report に残せる

## final exit contract
- milestone exit:
  - M1: parent bucket docs fixed
  - M2: first issue created and spec-authored
- success metrics reviewed:
  - yes
- remaining follow-up ownership:
  - future minor bug triage owner

## 依存 / ブロッカー
- D-001:
  - GitHub issue creation が利用可能であること
- D-002:
  - dogfooding report から repo-local actionable bug を抽出できること

## 未確定事項
- なし:
  - 初回 issue は `iss-00082` として作成済み
