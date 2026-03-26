---
種別: 計画書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
依存: ["requirement.md", "design.md"]
---

# init-local-00003 Architecture Maintenance and Hardening — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - prototype の feature expansion を支える architecture guardrail と cleanup backlog を独立 initiative として閉じる。
- 対象 metric:
  - requirement の Metric-001 / Metric-002

## マイルストーン
- M1:
  - deliverable:
    - architecture gap review が initiative 正本へ取り込まれている
  - exit:
    - sync / compatibility / invariant / cleanup 対象が整理されている
- M2:
  - deliverable:
    - docs/gov 系の architecture contract が discussion で閉じ始めている
  - exit:
    - sync contract と compatibility boundary の論点が明文化されている
- M3:
  - deliverable:
    - code cleanup 対象が epic / issue に分解されている
  - exit:
    - active-state と create lock の cleanup 着手順が決まっている

## Epic ポートフォリオ
- epic-0001-sync-and-compatibility-contract:
  - 目的:
    - provider/generated sync contract と shipped runtime compatibility boundary を定義する。
  - deliverable:
    - sync / compatibility contract docs
  - metric link:
    - Metric-001
  - depends on:
    - なし
- epic-0002-architecture-invariants-and-review:
  - 目的:
    - architecture health review 用の structural invariant と review rule を定義する。
  - deliverable:
    - invariant checklist
  - metric link:
    - Metric-001
  - depends on:
    - epic-0001-sync-and-compatibility-contract
- epic-0003-runtime-state-boundary-cleanup:
  - 目的:
    - active-state source-of-truth cleanup を扱う。
  - deliverable:
    - canonical active-state boundary へ寄せる issue 群
  - metric link:
    - Metric-002
  - depends on:
    - epic-0002-architecture-invariants-and-review
- epic-0004-runtime-layer-hardening:
  - 目的:
    - create lock layer leak と unresolved safety ownership を扱う。
  - deliverable:
    - create/recovery/safety hardening issue 群
  - metric link:
    - Metric-002
  - depends on:
    - epic-0002-architecture-invariants-and-review

## 順序と理由
- sequencing rationale:
  - 先に sync / compatibility を閉じる。
  - 次に architecture invariant を置く。
  - その後、source-of-truth cleanup と layer cleanup を実装 issue として扱う。
- parallelizable:
  - epic-0003 と epic-0004 は並行着手可能。

## 意思決定ゲート
- G1 strategy review:
  - architecture initiative の範囲が feature initiative と混ざっていないか確認する
- G2 milestone readiness:
  - docs/gov が先に閉じる順序になっているか確認する
- G3 governance/docs impact:
  - cleanup 対象が architecture risk として正しく整理されているか確認する
- G9 final initiative plan review:
  - feature initiative に渡す guardrail が十分か確認する

## 指標レビュー計画
- review timing:
  - gap review 反映時
  - epic 分解時
- dashboard / source:
  - initiative docs
  - discussion sheet

## ロールアウト計画
- rollout window:
  - docs/gov を先行し、code cleanup は後続で issue 化する
- release / communication:
  - feature initiative 側へ guardrail と dependency を共有する

## Epic readiness contract
- Epic に要求する最低条件:
  - architecture risk が何か説明できる
  - As-Is / To-Be / gap / risk が見える
  - feature initiative との境界が明示されている

## final exit contract
- milestone exit:
  - architecture-level の主要 gap が docs と issue backlog に落ちている
- success metrics reviewed:
  - requirement の Metric-001 / Metric-002 を確認している
- remaining follow-up ownership:
  - feature initiative 側へ渡す guardrail と残件が整理されている

## 依存 / ブロッカー
- D-001:
  - feature initiative との優先順位調整
- D-002:
  - current runtime baseline の理解

## 未確定事項
- Q-001:
  - 質問:
    - epic-0003 と epic-0004 のどちらを先に実装 issue 化するか。
  - 選択肢:
    - A:
      - active-state source-of-truth cleanup
    - B:
      - create lock / safety hardening
  - 推奨案:
    - A
  - 影響範囲:
    - issue 着手順
