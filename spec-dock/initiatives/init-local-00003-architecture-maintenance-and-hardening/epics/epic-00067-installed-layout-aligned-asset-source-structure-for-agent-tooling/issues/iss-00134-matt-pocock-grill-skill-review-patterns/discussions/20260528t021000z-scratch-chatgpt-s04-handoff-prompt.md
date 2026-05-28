---
kind: scratch
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T02:10:00Z
created_by: codex
purpose: ChatGPT Web prompt for S04 existing skill handoff boundary analysis
---

# ChatGPT Prompt: S04 Existing Skill Handoff Boundary

目的:
spec-dock issue `iss-00134` is adopting Matt Pocock-style grill patterns as a spec-dock-native workflow. S01-S03 are implemented: local source snapshot, ChatGPT research discussions, new `spec-dock-requirement-grill` skill, four specialized discussion templates, managed skill registration, dogfooding mirror refresh, and `tests.test_init_update` pass. The remaining S04 question is whether existing skills should be updated with handoff guidance, or whether S04 should close as a documented no-op/deferred decision.

背景:
The new skill is not a direct import of `grill-me` / `grill-with-docs`. It is a docs-aware clarification workflow for active spec-dock issues. It reads active issue docs, parent docs, discussions, `.agent` state, source/tests/templates, then asks at most one high-impact human question if local sources cannot resolve ambiguity. It can create issue-local `research`, `interview`, `disc`, or `scratch` discussion artifacts and propose requirement/design/plan patches. It hands ADR work to `spec-dock-adr-facilitation`, and implementation should start only after requirement/design/plan are ready enough.

現在の実装/状況:
- New skill path:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md`
- New template paths:
  - `src/spec_dock/assets/spec_dock/templates/discussions/research-source-grounding.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview-grill-session.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-decision-tree.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc-adr-triage.md`
- Managed skill manifest was updated in `src/spec_dock/cli.py`.
- Dogfooding mirror was refreshed with `uvx --from . spec-dock update .`.
- `python -m unittest tests.test_init_update` passes.

関連ファイルと抜粋:

1. `spec-driven-tdd-workflow/SKILL.md`
Current routing list:
- `spec-dock-initiative-planning`: initiative-level requirement/design/plan planning.
- `spec-dock-epic-planning`: epic-level requirement/design/plan planning.
- `spec-dock-issue-execution`: issue implementation execution.
- `spec-dock-system-architect`: delegated architecture analysis and draft design evidence written as scope-local flat discussions. Canonical docs remain main-orchestrator-only.
- `spec-dock-implementation-planner`: delegated planning analysis and draft plan evidence written as scope-local flat discussions. Canonical docs remain main-orchestrator-only.
- `spec-dock-adr-facilitation`: ADR drafting/decision facilitation linked to the current workflow.

It also says:
- Put interview and investigation notes under `discussions/` in the active node.
- Sub-agent authoring outputs may be direct-written under target `discussions/`, but do not become canonical authority until adopted.

2. `spec-dock-issue-execution/SKILL.md`
It says:
- Preserve parent invariants before/during/after delegated work.
- Treat `plan.md` as planned executable workflow contract.
- Treat `report.md` as observed evidence ledger and decision ledger.
- Before completion, ensure ledger entries have no `Status=open`.
- Route runtime/tests/scaffold behavior to `dev-coder`.
- Route shipped docs/templates/skills/workflow text to `doc-writer`.

3. `spec-dock-system-architect/SKILL.md`
It says:
- Use for delegated architecture analysis or draft design proposal.
- Active context includes active requirement/design/plan and parent docs.
- If active context is missing, stale, contradictory, or insufficient, return a blocker to the main orchestrator. Do not ask the user directly.
- Allowed: create one new flat discussion artifact.
- Prohibited: edit canonical docs or ask the user directly for clarification.
- If requirement gaps prevent safe design, report requirement clarification requests to orchestrator.

4. `spec-dock-implementation-planner/SKILL.md`
It says:
- Use for delegated implementation planning analysis or draft plan proposal.
- If design evidence is missing, stale, contradictory, or insufficient for planning, return a blocker to the main orchestrator. Do not ask the user directly.
- Allowed: create one new flat discussion artifact.
- Prohibited: edit canonical docs or ask the user directly.
- If design gaps prevent safe planning, report the blocked planning decision and smallest next action to the orchestrator.

5. New `spec-dock-requirement-grill/SKILL.md`
Key contract:
- Use when an active spec-dock issue is not implementation-ready because requirement, design, plan, artifact authority, validation path, or ADR need is ambiguous.
- Read local context before asking user.
- Ask exactly one highest-impact remaining question only after local sources cannot answer it.
- May create issue-local discussion artifacts and propose/apply requirement/design/plan updates when task permits.
- Use `spec-dock-issue-execution` only after requirement/design/plan are ready enough for implementation.
- Use `spec-dock-adr-facilitation` for final ADR drafting.

制約と非ゴール:
- Do not recommend broad rewrites of existing skills.
- Do not add a new CLI command in S04.
- Do not add a new Codex agent wrapper in S04.
- Existing skills should remain concise; if guidance is needed, prefer one or two small routing bullets.
- Canonical docs remain main-orchestrator-owned; discussion artifacts are evidence until adopted.
- S04 acceptance allows either explicit deferral/no-op with rationale or minimal documented handoff/stop conditions.

既知の不確実性:
- If no existing skill references `spec-dock-requirement-grill`, users/agents may not discover it when requirements are ambiguous.
- If too many skills reference it, responsibility boundaries may become circular or noisy.
- `system-architect` / `implementation-planner` currently say to return blockers and not ask the user directly; they might or might not need to name requirement grill as the recommended orchestrator follow-up.

依頼:
Please decide the smallest correct S04 action. Should we:

A. Update only `spec-driven-tdd-workflow/SKILL.md` to include `spec-dock-requirement-grill` in the routing list and say to use it before issue execution/design/planning when issue readiness is ambiguous?
B. Also update `spec-dock-system-architect/SKILL.md` and/or `spec-dock-implementation-planner/SKILL.md` to mention requirement grill as the orchestrator follow-up when requirement/design gaps block them?
C. Close S04 as no-op/deferred because the new skill's own boundaries are enough?

望ましい出力形式:
1. Recommendation: A/B/C or another minimal option.
2. Exact files to change.
3. Suggested wording, keeping it short.
4. Risks avoided.
5. Tests/inspection to run.
6. Any reason this should become a follow-up instead of current issue scope.
