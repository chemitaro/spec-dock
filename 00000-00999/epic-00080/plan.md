---
種別: 計画書（Epic）
ID: "epic-00080"
タイトル: "minor bug fixes"
関連GitHub: ["#80"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-04-17"
依存: ["requirement.md", "design.md"]
親: ["init-00079"]
---

# epic-00080 minor bug fixes — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
- E-AC:
  - E-AC-001
  - E-AC-002

## Issue 分割方針
- slicing principle:
  - 1 issue = 1 actionable bug または tightly coupled contract bug
  - bug routing 用の parent docs と、実装-ready な issue docs を分離する
- exceptions:
  - 同一 root cause を共有する場合のみ 1 issue に束ねる

## Issue 一覧（順序 / tranche 付き）
- iss-00082-fail-fast-on-malformed-node-metadata:
  - 目的:
    - malformed `.meta.json` の `type` / `id` 欠落を silent skip せず fail-fast にする
  - deliverable:
    - issue spec
    - research note
  - tranche:
    - tranche-1
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-RQ-003
    - E-RQ-004
    - E-AC-001
    - E-AC-002
  - depends on:
    - なし
- iss-00342-reduce-unit-test-and-provider-ci-runtime:
  - 目的:
    - repo-local の tightly coupled test / Provider CI contract bug として、通常開発と PR feedback を阻害する長時間完全回帰の実行契約を整理する
  - deliverable:
    - requirement / design / plan / report
    - research / interview / accepted ADR
  - tranche:
    - tranche-2
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-RQ-004
    - E-AC-001
  - depends on:
    - なし

## 統合チェックポイント
- G1 decomposition review:
  - issue scope が single actionable bug に閉じているか
- G2 integration readiness:
  - first issue と future appended issues の issue docs が、それぞれの issue status に応じて implementation-ready か
- G3 rollout/docs impact:
  - background evidence と fix scope が混線していないか
- G9 final epic spec review:
  - reusable bucket、first issue、future appended issues が整合しているか

## 品質ゲート
- test / observability / migration / docs:
  - issue 作成後に active set / validate / sync が成功する
  - issue report に evidence を残す

## ロールアウト / docs impact
- rollout order:
  - parent bucket docs
  - first issue creation
  - issue spec / research authoring
- contract / docs refresh:
  - 新しい minor bug はこの epic 配下へ順次追加する

## Issue readiness contract
- Issue に要求する最低条件:
  - repo-local actionable bug に閉じている
  - requirement / design / plan / report が具体化されている
  - external staging failure などは non-goal として整理されている

## final exit contract
- E-AC closure:
  - first issue `iss-00082` と future appended issues は、それぞれの issue status に応じた spec-authoring / closure evidence を持つ。追加だけで issue の承認または完了を意味しない
- integration / rollout complete:
  - yes
- docs impact resolved:
  - yes

## 依存 / ブロッカー
- D-001:
  - GitHub-backed issue creation
- D-002:
  - issue docs を埋めるための evidence availability

## 未確定事項
- なし:
  - future issues are appended when new repo-local bugs are confirmed
