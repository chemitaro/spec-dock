---
種別: 計画書（Initiative）
ID: "init-local-00002"
タイトル: "Prototype Feature Expansion"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md"]
---

# init-local-00002 Prototype Feature Expansion — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - architecture maintenance と切り分けたうえで、prototype の機能価値を段階的に広げる。
- 対象 metric:
  - requirement の Metric-001 / Metric-002

## マイルストーン
- M1:
  - deliverable:
    - feature expansion の portfolio が architecture maintenance から分離されている
  - exit:
    - epic が value-based に整理され、dependency が明示されている
- M2:
  - deliverable:
    - core workflow completeness の feature epic が起動できる
  - exit:
    - 最初の feature epic の issue 分解方針がある
- M3:
  - deliverable:
    - operator / collaboration 方面の feature epic が優先順つきで見えている
  - exit:
    - blocker / enabler / later extension が整理されている

## Epic ポートフォリオ
- epic-0001-core-workflow-completeness:
  - 目的:
    - prototype として不足している主要 workflow を埋め、できること自体を増やす。
  - deliverable:
    - core feature gaps の整理と追加
  - metric link:
    - Metric-002
  - depends on:
    - `init-local-00003` の blocker が閉じていること
- epic-00054-github-lifecycle-command-expansion:
  - 目的:
    - GitHub / lifecycle の feature value を広げ、dogfooding で不足が見えた command-side lifecycle completeness を補う。
  - deliverable:
    - SpecDock から linked GitHub issue を close できる command と、local spec node を directory ごと削除できる安全な delete contract の定義、および 2 issue で完結する実装計画
  - metric link:
    - Metric-002
  - depends on:
    - epic-0001-core-workflow-completeness
  - 背景:
    - 現在の dogfooding では issue 作成は command 側で完結する一方、issue close は GitHub Web UI に戻る必要があり、lifecycle が途中で分断されている。
    - さらに local tree の整理も手作業で directory 削除に頼っており、issue / epic / initiative の local cleanup を command 化する operator value がある。
    - ただし GitHub-side delete は事故リスクが高いため、この epic では remote handling を close-only とし、remote delete は success path に含めない。
  - 実行方針:
    - 2 issue 構成で進める。
    - 第1 issue で close command を実装し、その issue 自身の docs/tests/review/success verification まで閉じる。
    - 第2 issue で local delete を実装し、その issue 自身の docs/tests/review/success verification に加えて epic 全体の final review / final validation まで閉じる。
- epic-0003-operator-value-expansion:
  - 目的:
    - operator が日常運用で得られる feature value を広げる。
  - deliverable:
    - operator-facing convenience / coverage の追加
  - metric link:
    - Metric-001
  - depends on:
    - epic-0001-core-workflow-completeness
- epic-0004-post-prototype-feature-candidates:
  - 目的:
    - prototype release 後でもよい feature extension を切り分ける。
  - deliverable:
    - later expansion backlog の整理
  - metric link:
    - Metric-001
  - depends on:
    - epic-0002-collaboration-and-lifecycle-expansion
    - epic-0003-operator-value-expansion

## 順序と理由
- sequencing rationale:
  - まず core workflow completeness を優先する。
  - そのうえで collaboration/lifecycle と operator value を拡張する。
  - `epic-00054` はその最初の具体化であり、create 後に Web UI へ戻っている lifecycle gap と、手作業 directory cleanup を command contract へ戻す役割を持つ。
  - `epic-00054` は review-only issue を別建てせず、各 implementation issue に review と成功性確認を内包する。
  - post-prototype 候補は current initiative の出口を曖昧にしないよう最後に整理する。
- parallelizable:
  - `epic-00054` と epic-0003 は並行検討できる。

## 意思決定ゲート
- G1 strategy review:
  - feature initiative が architecture maintenance を抱え込んでいないか確認する
- G2 milestone readiness:
  - 最初に足す feature が prototype value に直結しているか確認する
- G3 governance/docs impact:
  - architecture initiative 側の guardrail を破っていないか確認する
- G9 final initiative plan review:
  - current initiative と post-prototype candidate の境界を確認する

## 指標レビュー計画
- review timing:
  - epic 起動時
  - feature priority 見直し時
- dashboard / source:
  - initiative docs
  - architecture initiative docs

## ロールアウト計画
- rollout window:
  - architecture blocker が無い範囲で段階追加する
- release / communication:
  - feature value と dependency を docs へ残す

## Epic readiness contract
- Epic に要求する最低条件:
  - prototype value にどう効くか説明できる
  - architecture initiative 側の blocker に抵触していない
  - issue に分解可能である

## final exit contract
- milestone exit:
  - feature value 拡張の current initiative 範囲が整理されている
- success metrics reviewed:
  - requirement の Metric-001 / Metric-002 を確認している
- remaining follow-up ownership:
  - post-prototype feature candidate の行き先が明示されている

## 依存 / ブロッカー
- D-001:
  - `init-local-00003 Architecture Maintenance and Hardening`
- D-002:
  - current runtime baseline の維持

## 未確定事項
- Q-001:
  - 質問:
    - `epic-00054` と epic-0003 のどちらを先に進めるか。
  - 選択肢:
    - A:
      - collaboration / lifecycle（`epic-00054`）
    - B:
      - operator value
  - 推奨案:
    - A
  - 影響範囲:
    - epic 着手順
