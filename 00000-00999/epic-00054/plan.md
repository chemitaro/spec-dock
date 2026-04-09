---
種別: 計画書（Epic）
ID: "epic-00054"
タイトル: "GitHub lifecycle command expansion"
関連GitHub: ["#54"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-08"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00054 GitHub lifecycle command expansion — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
  - E-RQ-006
  - E-RQ-007
  - E-RQ-008
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004

## Issue 分割方針
- slicing principle:
  - remote close と local delete は別の observable behavior として分割する
  - 各 issue が自身の docs/tests/review/success verification を内包して閉じる
  - destructive subtree delete は第2 issue で issue / parent scope guardrail、docs/test evidence、epic final close-out まで一括で扱う
- exceptions:
  - 実装途中で irreversible boundary を追加で固定する必要が出た場合は discussion または ADR を追加する

## Issue 一覧（順序 / tranche 付き）
- planned-issue-01-close-linked-github-issues:
  - 目的:
    - linked GitHub issue を SpecDock command から close できるようにする
  - deliverable:
    - close command contract、runtime 実装、docs/tests、issue-level review、success verification
  - tranche:
    - tranche-1 / lifecycle close
  - closes:
    - E-RQ-001
    - E-RQ-003（一部）
    - E-RQ-007（一部）
    - E-AC-001
  - depends on:
    - epic-0001-core-workflow-completeness
- planned-issue-02-delete-local-spec-nodes-with-guardrails:
  - 目的:
    - issue / epic / initiative の local directory delete を安全な contract で提供し、epic 全体の final close-out まで完了させる
  - deliverable:
    - delete command contract、subtree guardrail、remote close-only boundary、docs/tests、issue-level review、success verification、epic final review / final validation / close-out evidence
  - tranche:
    - tranche-2 / local delete and epic close-out
  - closes:
    - E-RQ-002
    - E-RQ-004
    - E-RQ-005
    - E-RQ-006
    - E-RQ-007
    - E-RQ-008
    - E-AC-002
    - E-AC-003
    - E-AC-004
  - depends on:
    - planned-issue-01-close-linked-github-issues

## 統合チェックポイント
- G1 decomposition review:
  - close と delete が別 capability として分離され、remote delete exclusion と 2 issue 構成が requirement/design/plan に露出している
- G2 integration readiness:
  - 第1 issue の close contract と第2 issue の delete / final close-out contract が partial failure / confirmation / subtree 境界で矛盾しない
- G3 rollout/docs impact:
  - provider docs / dogfooding docs / CLI help / tests が各 issue 内の review / success verification と同じ safety wording を返す
- G9 final epic spec review:
  - 第2 issue の final review で、dogfooding feedback で見えた lifecycle gap が docs と evidence で閉じている

## 品質ゲート
- test / observability / migration / docs:
  - 第1 issue で close command の runtime / CLI tests と review / success verification を完了する
  - 第2 issue で local delete の filesystem / guardrail tests、remote close-only boundary の docs/test evidence、dogfooding validation、final spec review を完了する

## ロールアウト / docs impact
- rollout order:
  - close command を先に追加し、その後 local delete を導入する
  - destructive parent scope delete と epic final close-out は、第1 issue の学習を踏まえて第2 issue に集約する
- contract / docs refresh:
  - `reference_github.md`、workflow docs、CLI help、dogfooding docs の close / delete contract を各 issue 内で更新し、第2 issue で最終整列する

## Issue readiness contract
- Issue に要求する最低条件:
  - close または delete のどちらか 1 つの observable behavior を主対象にしている
  - remote delete exclusion が明文化されている
  - review と success verification をその issue 自身で閉じる方針が見えている
  - 第2 issue は destructive guardrail と epic final close-out responsibility を持つ

## final exit contract
- E-AC closure:
  - E-AC-001 は第1 issue の tests / docs / runtime evidence / review / success verification で閉じる
  - E-AC-002 / E-AC-003 は第2 issue の local delete と subtree guardrail の tests / docs / runtime evidence / review / success verification で閉じる
  - E-AC-004 は第2 issue の provider / dogfooding docs parity、dogfooding validation、final spec review で閉じる
- integration / rollout complete:
  - command-side create -> close と、必要時の local delete が同じ tool surface で説明でき、review-only issue を置かずに epic を閉じられる
- docs impact resolved:
  - remote close-only / local delete / remote delete exclusion が docs 群で一貫している

## 依存 / ブロッカー
- D-001:
  - `init-local-00003 Architecture Maintenance and Hardening`
- D-002:
  - current runtime baseline の維持
- D-003:
  - `gh` auth / permission と dogfooding repo の GitHub linkage

## 未確定事項
- Q-001:
  - 質問:
    - local delete の parent scope で、remote close を child issue 群へどこまで自動適用するか。
  - 選択肢:
    - A:
      - subtree 内の linked issue を一括 close
    - B:
      - parent node だけ close し、child は別途扱う
  - 推奨案:
    - A。local subtree delete と remote lifecycle の整合が高い。ただし explicit recursive opt-in は維持する。
  - 影響範囲:
    - command UX
    - guardrail design
    - integration tests
