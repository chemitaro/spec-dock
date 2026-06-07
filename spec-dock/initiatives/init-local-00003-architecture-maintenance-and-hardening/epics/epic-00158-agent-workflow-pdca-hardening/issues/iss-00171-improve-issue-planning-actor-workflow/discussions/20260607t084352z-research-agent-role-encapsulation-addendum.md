---
種別: research
ID: "20260607t084352z-research"
タイトル: "Agent Role Encapsulation Addendum"
状態: "completed"
作成者: "codex"
最終更新: "2026-06-07"
親: ["iss-00171", "epic-00158"]
authority: "evidence"
adoption_status: "adopted"
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# Agent role encapsulation addendum

## Context

During iss-00171 planning, the user identified an additional structural problem:

- `spec-dock-system-architect` and `spec-dock-implementation-planner` should not exist as skills.
- These two surfaces are not reusable user-facing skills. They are delegated agent roles.
- Their role knowledge should be encapsulated in agent instructions, not moved into `.agents/skills/`.

## Current repository evidence

- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml` is currently a thin adapter that points at `.agents/skills/spec-dock-system-architect/SKILL.md` as the canonical role contract.
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml` is currently a thin adapter that points at `.agents/skills/spec-dock-implementation-planner/SKILL.md` as the canonical role contract.
- Dogfooding mirrors under `.codex/agents/` have the same pattern.
- Provider-side and dogfooding role skill directories currently exist under `.agents/skills/`.

## Planning decision

iss-00171 should be redesigned so that:

- `system-architect` and `implementation-planner` are agent roles, not skills.
- Provider-side `.codex/agents/system-architect.toml` and `.codex/agents/implementation-planner.toml` become the role contract source of truth.
- Dogfooding `.codex/agents/*.toml` mirrors are kept aligned with provider-side source.
- Provider-side and dogfooding `spec-dock-system-architect` / `spec-dock-implementation-planner` skill directories are deleted.
- `spec-dock-issue-planning` invokes these roles as agents and records adoption/fallback/report obligations, but does not copy the full role knowledge into the issue-planning skill.

## Implication for implementation planning

The implementation plan must include:

- Agent TOML instruction migration.
- Role skill deletion.
- Hub / docs / runtime stale reference cleanup.
- Verification that no installed surface instructs agents to read deleted role skills.
- Fresh reviewer gates after the redesign, because the earlier spec-reviewer pass covered the pre-encapsulation plan.
