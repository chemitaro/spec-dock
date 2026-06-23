---
種別: 設計書ドラフト（Issue）
ID: "iss-00228"
タイトル: "Compile State Aware Workflow Runbooks And Fixed Skill Kernels"
関連GitHub: ["#228"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00228 Draft Design

## 設計方針
- Skill は fixed kernel とし、runtime public CLI `workflow next` だけへ依存する。
- Runbook は canonical authority ではなく ignored generated projection。
- State Resolver は active issue / artifact readiness / assurance status から next action を一つ返す。

## 変更対象
- Provider:
  - `domain/workflow_state.py`
  - `domain/runbook.py`
  - `application/resolve_workflow_next.py`
  - `application/compile_runbook.py`
  - `infra/runbook_store.py`
  - `commands/workflow.py`
  - fixed skill assets under `src/spec_dock/assets/install_root/.agents/skills/`
- Dogfooding mirror:
  - `spec-dock/.agent/runbooks/**` ignored。
  - `spec-dock/active/current-runbook.{md,json}` ignored/projection。

## Interface
- `spec-dock workflow status --format text|json`
- `spec-dock workflow next issue-planning --format markdown|json`
- `spec-dock workflow next issue-execution --format markdown|json`

## 検証
- no-active state returns only issue start / target request。
- Runbook JSON schema / Markdown projection golden tests。
- Issue switch does not mutate tracked Skill files。
- generated state ignored / clean Git。
- `lite_candidate` never reduces obligations without `authorized_profile`.

## Handoff
- I03 consumes Runbook / Assurance source binding for planning artifact composition。
- I07 validates fixed kernel in dogfooding rollout。
