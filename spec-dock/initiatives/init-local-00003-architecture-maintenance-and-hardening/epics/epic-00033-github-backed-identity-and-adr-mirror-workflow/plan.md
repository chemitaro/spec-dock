---
種別: 計画書（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
関連GitHub: ["#33"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00033 GitHub backed identity and ADR mirror workflow — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004
  - E-AC-005

## Issue 分割方針
- slicing principle:
  - contract を 1 issue 1 責務で切る
  - `new`、`new doc`、`sync`、migration/validate、docs/tests parity を分離する
- rationale:
  - node identity contract を先に固定しないと、後続の naming / sync / validate が揺れるため

## Issue 一覧（順序 / tranche 付き）
- issue-1-github-mandatory-node-creation-contract:
  - 目的:
    - initiative / epic / issue を GitHub mandatory へ切り替え、local-only path を除去する
  - deliverable:
    - `new` command contract 更新
    - repo-scoped GitHub linkage persistence
    - 旧 workspace に対して in-place 自動移行を保証しない境界を docs/tests/validate へ先行反映
    - related tests
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-001, E-RQ-002, E-AC-001
  - depends on:
    - なし
- issue-2-timestamp-based-discussion-and-adr-naming:
  - 目的:
    - discussion / ADR filename を timestamp-prefix naming に切り替える
  - deliverable:
    - `new doc` contract 更新
    - naming validation 更新
    - 旧 sequential docs を自動 rename/migrate しない境界を docs/tests/validate で固定
    - related tests
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-003, E-AC-002
  - depends on:
    - issue-1-github-mandatory-node-creation-contract
- issue-3-sync-adr-symlink-mirror:
  - 目的:
    - `sync` で `spec-dock/adrs/` symlink mirror を全再生成する
  - deliverable:
    - sync mirror clear-then-rebuild
    - stale symlink が残らないことの検証
    - non-symlink warning handling
    - related tests
  - tranche:
    - tranche-2 / now
  - closes:
    - E-RQ-004, E-AC-003
  - depends on:
    - issue-2-timestamp-based-discussion-and-adr-naming
- issue-4-migration-guardrails-and-validation-hardening:
  - 目的:
    - issue-1〜3 で先行固定した migration boundary を仕上げとして横断 hardening する
  - deliverable:
    - legacy boundary docs/tests/validate の抜け漏れ解消
    - old workspace 非サポート境界の最終整合
    - validate hardening（仕上げ）
  - tranche:
    - tranche-2 / now
  - closes:
    - E-AC-004
  - depends on:
    - issue-1-github-mandatory-node-creation-contract
    - issue-2-timestamp-based-discussion-and-adr-naming
    - issue-3-sync-adr-symlink-mirror
- issue-5-docs-dogfooding-parity-and-final-regression-gate:
  - 目的:
    - provider docs / tests / dogfooding mirror を新 contract に揃え、最終回帰を閉じる
  - deliverable:
    - docs parity
    - full regression
    - final review evidence
  - tranche:
    - tranche-3 / close-out
  - closes:
    - E-RQ-005, E-AC-005
  - depends on:
    - issue-1-github-mandatory-node-creation-contract
    - issue-2-timestamp-based-discussion-and-adr-naming
    - issue-3-sync-adr-symlink-mirror
    - issue-4-migration-guardrails-and-validation-hardening

## 統合チェックポイント
- G1 decomposition review:
  - issue 分解が contract 単位で分かれている
- G2 integration readiness:
  - create / doc / sync / validate / docs parity の依存順が成立している
- G3 rollout/docs impact:
  - rebuildable workspace boundary が docs と tests に現れている
- G9 final epic spec review:
  - 全 issue の closure evidence が揃っている

## 品質ゲート
- test / observability / migration / docs:
  - gate-1:
    - issue-1 完了時に create contract review と migration boundary 初期固定を確認
  - gate-2:
    - issue-2 完了時に naming contract review と legacy 非自動移行境界の固定を確認
  - gate-3:
    - issue-3 完了時に clear-then-rebuild と stale symlink 不残存を確認
  - gate-4:
    - issue-4 完了時に migration/validate 境界の最終整合を確認
  - gate-5:
    - issue-5 完了時に final spec / QA / docs parity review

## ロールアウト / docs impact
- rollout order:
  - create contract -> doc naming -> sync mirror -> migration guardrails -> docs/tests parity
- contract / docs refresh:
  - GitHub mandatory
  - no local-only
  - timestamp naming
  - `adrs/` mirror generated view

## Issue readiness contract
- Issue に要求する最低条件:
  - contract が 1 つに絞られている
  - observable command/test が定義されている
  - old workspace boundary をどう扱うか書かれている

## final exit contract
- E-AC closure:
  - 全 acceptance criteria に evidence がある
- integration / rollout complete:
  - create / doc / sync / validate / docs parity が新 contract に揃う
- docs impact resolved:
  - old local-only / sequential / index assumptions が repo docs に残っていない

## 依存 / ブロッカー
- D-001:
  - GitHub auth / CLI availability
- D-002:
  - symlink capability

## 未確定事項
- なし:
  - issue 分解と順序は discussion で確定済み
