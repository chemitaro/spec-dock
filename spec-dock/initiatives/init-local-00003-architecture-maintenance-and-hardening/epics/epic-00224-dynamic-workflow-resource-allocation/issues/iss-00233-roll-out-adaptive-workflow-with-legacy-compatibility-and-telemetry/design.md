---
種別: 設計書（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry — 設計

## 目的・制約
- I07 は feature flag を切り替える Issue ではなく、初期 rollout の安全境界と将来 Auto-Lite 採用条件を runtime output / tests / docs で固定する統合 Issue とする。
- automatic Lite default は常に disabled として出力し、別 accepted ADR、policy version bump、rollout Issue、telemetry gate が揃うまで有効化しない。

## 既存実装の理解
- `domain.assurance` は `lite_candidate` と `lite_authorized` を分離済み。
- `assurance verify` は contract missing を strict-legacy success として扱う。
- `workflow next` は scaffold requirement と invalid / stale assurance を block し、substantive requirement + missing assurance は strict-legacy authority で実行可能にする。
- I06 は blocker fingerprints を PR review snapshot payload に出し、automation-stalled detection の前提 evidence を提供済み。

## 採用方針
- Auto-Lite readiness は persisted contract schema へ入れず、presentation payload に deterministic report として出す。
  - 理由: readiness は current policy の rollout interpretation であり、source binding stale 判定や persisted contract compatibility を壊さないため。
- `classification` の既存 shape は維持し、top-level `auto_lite_readiness` を追加する。
- Strict-legacy missing contract でも同じ report shape を返し、Lite authorization なし / rollback mode strict-legacy を示す。
- PR observation wait は same decision fingerprint の安定判定を持つため、blocker fingerprints が repeated した human gate を `automation_stalled` として operator-facing payload に出す。

## 変更対象
```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- presentation/assurance_text.py   # 追加: auto_lite_readiness JSON payload
|-- domain/assurance.py              # 追加: readiness payload helper
|-- application/workflow.py          # 変更: missing assurance を strict-legacy ready として扱う
`-- install_root/.agents/.../pr_observation_wait.py # 変更: automation_stalled operator surface

tests/
|-- unit/domain/test_assurance.py              # readiness helper の deterministic contract
|-- unit/presentation/test_assurance_text.py   # JSON rendering / strict-legacy rendering
|-- cli_runtime/test_assurance.py              # CLI output integration
|-- cli_runtime/test_workflow.py               # strict-legacy workflow next regression
`-- unit/infra/test_init_update.py             # provider / mirror wait script contract
```

## インターフェース契約
- `assurance ... --format json` は、classification が取得できる場合に `auto_lite_readiness` を返す。
- `workflow next issue-execution` は substantive requirement + missing assurance で `ready` / `strict-legacy-missing-assurance` / `authorized_profile=strict` を返す。invalid / stale assurance は従来どおり classification-required にする。
- `wait_pr_observation.sh` output は same blocker fingerprint が安定した human gate で `automation_stalled.present=true` を返し、`recommended_next_action` は `human_gate` のまま merge-prepared にしない。
- payload fields:
  - `automatic_lite_default_enabled: false`
  - `future_adoption_requires: ["accepted_adr", "policy_version_bump", "rollout_issue", "telemetry_gate"]`
  - `rollback_mode: "strict-legacy"`
  - `automation_stalled_routes_to: "human_gate"`
  - `required_metrics`: false positive candidates, escalation rate, P0/P1 escape, post-review blocker, wall-clock-token delta, missing metrics summary
  - `missing_metrics_summary`: present until external telemetry backend provides metrics

## 要件 → 設計マッピング
- AC-001 -> strict-legacy missing contract rendering tests。
- AC-001 -> `workflow next` strict-legacy regression tests。
- AC-002 -> `auto_lite_readiness.automatic_lite_default_enabled == false` tests。
- AC-003 -> required metrics / missing metrics summary tests。
- AC-004 -> `automation_stalled_routes_to == human_gate` tests。
- AC-004 -> PR observation wait script automation-stalled contract tests。
- EC-001 -> strict-legacy readiness payload。
- EC-002 -> existing hard trigger monotonic tests + readiness no auto-default tests。
- EC-003 -> missing metrics summary remains present。

## リスク / ロールバック
- Persisted `assurance.json` schema は変えないため、rollback は presentation helper と tests の revert で足りる。
- JSON output に field が増えるが既存 field は保持する。
- provider asset を変更するため、dogfooding mirror は `spec-dock update` または direct parity verification で確認する。
