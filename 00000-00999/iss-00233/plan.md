---
種別: 実装計画書（Issue）
ID: "iss-00233"
タイトル: "Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry"
関連GitHub: ["#233"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00233 Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry — 実装計画

## この計画で満たす要件ID
- Issue: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003
- Epic: E-RQ-012, E-RQ-013, E-RQ-014, E-AC-013, E-AC-014, E-AC-015, E-AC-016

## 実装順序
- S01: Auto-Lite readiness / rollout telemetry payload を `assurance` JSON に追加する。
- S02: missing assurance の `workflow next` strict-legacy compatibility を実装する。
- S03: repeated blocker fingerprint の automation-stalled operator surface を PR observation wait に追加する。
- S90: provider / dogfooding docs impact と issue report を更新する。
- S99: lint / targeted tests / validate / assurance / reviewer gates / final commit。

## 仕様固定クロージャ索引
| ID | step | 種別 | 固定する期待値 | 証跡レベル |
|---|---|---|---|---|
| tc-233-001 | S01 | acceptance | adaptive assurance JSON は `automatic_lite_default_enabled=false` を出す | red-required |
| tc-233-002 | S01 | acceptance | future Auto-Lite adoption requirements と rollback mode が出る | red-required |
| tc-233-003 | S01 | compatibility | missing contract は strict-legacy で success し、Lite を authorize しない | covered-existing |
| tc-233-004 | S01 | telemetry | required metrics、missing metrics summary、efficiency baseline が report される | red-required |
| tc-233-005 | S02 | compatibility | `workflow next issue-execution` は missing assurance を strict-legacy ready として扱う | red-required |
| tc-233-006 | S03 | safety | repeated blocker fingerprint は `automation_stalled` / human gate として report される | red-required |
| tc-233-007 | S90 | docs | parent Epic / issue report は I07 rollout closure と efficiency evidence を記録する | inspect-only |
| tc-233-008 | S99 | final | lint、targeted tests、validate、reviewer gates が通る | manual-required |

## S01 — Readiness report integration
- 対象:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `tests/unit/domain/test_assurance.py`
  - `tests/unit/presentation/test_assurance_text.py`
  - `tests/cli_runtime/test_assurance.py`
- Green 検証:
  - `uv run pytest tests/unit/domain/test_assurance.py tests/unit/presentation/test_assurance_text.py tests/cli_runtime/test_assurance.py`
- closure:
  - tc-233-001〜tc-233-004
- reviewer:
  - code-reviewer

## S02 — Strict-legacy workflow compatibility
- 対象:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `tests/cli_runtime/test_workflow.py`
- Green 検証:
  - `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py -k 'missing_assurance or malformed_assurance or stale_source_binding'`
- closure:
  - tc-233-005
- reviewer:
  - code-reviewer

## S03 — Automation-stalled operator surface
- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_233_pr_observation_wait'`
- closure:
  - tc-233-006
- reviewer:
  - code-reviewer

## S90 — Docs / rollout evidence
- 対象:
  - issue report
  - parent Epic report
- Green 検証:
  - `./spec-dock/scripts/spec-dock validate`
- closure:
  - tc-233-007
- reviewer:
  - spec-reviewer

## S99 — Final quality gate
- 必須 validation:
  - `make lint`
  - targeted tests
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock assurance verify --format json`
- final QA gate:
  - qa-reviewer
- final code review:
  - code-reviewer
- final spec review:
  - spec-reviewer
