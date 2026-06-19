---
created_by_role: system-architect
scope_id: iss-00210
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/discussions/20260619t023116z-research-issue-210-clarification-research.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/discussions/20260619t023120z-interview-issue-210-essential-scope-question.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_epic.md
  - spec-dock/docs/authoring/decision-routing.md
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/report.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
report_evidence_destination: spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00210-epic-planning-system-architect-draft-cycles/report.md#委任ドラフト証跡delegated-draft-evidence--必須
source_requirement_revision: 1c88346d
---

# Issue 210 System Architect Draft Design

This is delegated architecture evidence for Issue 210 only. It is not a canonical design, reviewer result, phase promotion, implementation plan approval, or authority claim. The main orchestrator owns adoption, canonical integration, fresh `spec-reviewer` gates, and downstream handoff.

## 1. Requirement Coverage

- AC-001: Add a first-read Epic planning spine that tells the main orchestrator when a `system-architect` discussion draft is expected before Epic design / plan authoring.
- AC-002: Preserve delegated draft authority as scope-local evidence only; canonical Epic docs remain main-orchestrator-owned and require Evidence Adoption Ledger recording plus fresh reviewer pass.
- AC-003: Define Epic planning completion before Issue decomposition: reviewer-gated Epic requirement/design/plan, issue slicing policy, dependency analysis, and no unresolved scope/design gaps.
- AC-004: Define post-Issue creation cross-issue draft package: shared vocabulary, ownership boundaries, dependency order, handoff inputs/outputs, and issue-local `draft-requirement` / `draft-design` evidence.
- AC-005: Keep issue-local drafts as planning inputs, not canonical issue docs.
- AC-006: Keep Issue 211 independent. Issue 210 only produces a planning completion / handoff contract that Issue 211 may consume.
- AC-007: Keep dependency mutation command-first through `spec-dock deps add/remove/check`, not `.meta.json` direct edits.
- AC-008: Require provider-side source update plus dogfooding mirror validation evidence through the route chosen in canonical design / plan.

## 2. Existing Context Findings

- `spec-dock-epic-planning/SKILL.md` is currently a thin routing surface. It already requires fresh `spec-reviewer` pass before phase movement and forbids depth=3 delegation, but it does not yet describe the system-architect draft cycle, cross-issue draft package, or Issue 211 handoff contract.
- `workflow_spec_authoring.md` already contains the strongest delegated authoring policy: single-writer canonical authority, scope-local `discussions/` output, minimum provenance fields, Evidence Adoption Ledger, failure modes, and static adapter boundaries.
- `workflow_epic.md` already owns Epic-specific lifecycle details: reuse checks, Issue creation commands, dependency commands, Epic as cross-issue design backbone, and plan-gate-before-Issue-decomposition.
- `decision-routing.md` already gives the placement rule needed by Issue 210: cross-issue design backbone belongs at Epic scope; cross-epic operating decisions route to Initiative; long-lived reusable decisions route to ADR; missing source of truth routes to clarification.
- Provider docs and dogfooding mirror docs inspected for this draft matched for the relevant files; implementation should still treat `src/spec_dock/assets/...` as source of truth and mirror files as validation targets.

## 3. Design Decisions

- Decision 1: Put the short mandatory first-read spine in `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`.
  - The skill should say: for non-trivial Epic design / plan work, after requirement gate pass and before canonical design / plan authoring, request a `system-architect` scope-local discussion draft unless the Epic is lightweight and a skip reason is recorded.
- Decision 2: Keep detailed semantics in docs rather than copying policy into the skill.
  - `workflow_epic.md` should own Epic-specific completion and handoff semantics.
  - `workflow_spec_authoring.md` should remain the shared authority for delegated draft evidence, adoption, and reviewer gates. It may need only a small cross-reference or Epic-specific pointer if canonical design chooses to avoid duplication.
- Decision 3: Define Epic planning completion as a producer contract, not an execution coordinator contract.
  - Producer outputs: reviewer-gated Epic requirement/design/plan, issue list, dependency order, command-first dependency evidence, cross-issue draft package, issue-local draft requirement/design artifacts, and report ledger entries.
  - Consumer boundary: future `spec-dock-epic-execution` / Issue 211 can rely on those outputs but must define execution coordination, `issue start` / `issue finish`, PR readiness, and closeout loops itself.
- Decision 4: Use conditional delegation, not heavyweight delegation for every Epic.
  - Non-trivial Epic indicators should include cross-issue ownership boundaries, dependency ordering, shared workflow policy, durable handoff vocabulary, or Issue 211-style downstream consumers.
  - Lightweight Epic skip should require a short report or design note, but not a full delegated draft.
- Decision 5: Keep Issue 211 reference independent.
  - Issue 210 should mention Issue 211 only as a downstream consumer of the handoff contract, not as a subtask, dependency completion condition, or execution-scope owner.

## 4. Alternatives Considered

- Alternative A: Skill-only update.
  - Rejected as too narrow. It would improve first-read behavior but leave Issue 211 to rediscover planning completion and handoff details.
- Alternative B: Handoff-focused skill plus docs update.
  - Recommended. It matches the answered interview artifact: Issue 210 fixes the planning completion / handoff contract while keeping Issue 211 independent.
- Alternative C: Broad docs/templates/delegated-authoring redesign.
  - Not recommended for Issue 210. Existing `workflow_spec_authoring.md` already carries delegated authoring semantics, and a broad cleanup would blur this issue with parent Epic alignment work.

## 5. Boundary / Contract Model

- `spec-dock-epic-planning` owns:
  - first-read routing for Epic planning;
  - phase order and fresh reviewer gate reminders;
  - conditional system-architect draft cycle trigger;
  - skip reason requirement;
  - pointer to Epic completion / handoff docs;
  - reminder that delegated evidence needs EAL adoption and fresh reviewer pass.
- `workflow_epic.md` owns:
  - Epic planning completion definition;
  - Issue decomposition preconditions;
  - cross-issue draft package shape;
  - command-first Issue creation and dependency registration references;
  - handoff output list for downstream Epic execution.
- `workflow_spec_authoring.md` owns:
  - canonical single-writer authority;
  - delegated discussion draft provenance;
  - Evidence Adoption Ledger and Delegated Draft Evidence semantics;
  - reviewer gate and non-pass state semantics;
  - static adapter failure modes.
- Future `spec-dock-epic-execution` / Issue 211 should own:
  - consuming the planning completion package;
  - coordinating issue lifecycle after planning;
  - execution sequencing, `issue start` / `issue finish`, PR readiness, closeout, and stale handoff handling.

## 6. Dependency Analysis

- Upstream dependency: Issue 210 requirement has adopted Option B and records no blocking user question.
- Source dependency: provider-side installed skill and provider-side docs must be changed before mirror validation.
- Workflow dependency: delegated draft adoption requires Issue 210 `report.md` Evidence Adoption Ledger and fresh `spec-reviewer` on canonical docs.
- Downstream dependency: Issue 211 can reference the handoff contract after Issue 210 is integrated and reviewer-gated, but Issue 210 should not wait on Issue 211 implementation.
- Command dependency: Issue dependency mutations must be represented through `spec-dock deps add/remove/check` and verified with `validate` / `sync` or a recorded no-run reason.

## 7. Source of Record

- Implementation source of truth for skill: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`.
- Implementation source of truth for shipped docs: `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` and, if needed, `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`.
- Dogfooding validation targets: `.agents/skills/spec-dock-epic-planning/SKILL.md`, `spec-dock/docs/workflow_epic.md`, `spec-dock/docs/workflow_spec_authoring.md`, and `spec-dock/.agent/*` outputs as relevant.
- Issue-level evidence destination: Issue 210 `report.md`, especially Evidence Adoption Ledger, Delegated Draft Evidence, Spec Authoring Gate, and implementation session evidence.

## 8. Data Flow / Domain Model / Interface Contract

```text
Epic requirement reviewer pass
  -> conditional system-architect draft request
  -> scope-local discussion draft evidence
  -> main orchestrator adoption decision in EAL
  -> canonical Epic design / plan updates
  -> fresh spec-reviewer gates
  -> Issue list and dependency order
  -> cross-issue draft package
  -> issue-local draft requirement/design evidence
  -> downstream Epic execution handoff
```

Handoff package fields should be described as expected content, not as a new runtime schema:

- Epic planning completion status and reviewer gate references.
- Canonical Epic requirement/design/plan paths.
- Issue list, dependency order, and dependency command evidence.
- Shared vocabulary and ownership boundary notes.
- Cross-issue risks and rollback/compatibility notes.
- Issue-local draft requirement/design artifact paths.
- Known non-blocking deferrals and revisit conditions.

## 9. File / Module Change Plan

Recommended minimal implementation surface:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  change: add first-read spine for conditional system-architect draft cycle,
          adoption boundary, skip reason, cross-issue draft package, and Issue 211 independence.

src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  change: add Epic planning completion / handoff contract and cross-issue draft package semantics.

src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  change: optional small cross-reference only if needed; avoid duplicating existing delegated authoring policy.

.agents/skills/spec-dock-epic-planning/SKILL.md
spec-dock/docs/workflow_epic.md
spec-dock/docs/workflow_spec_authoring.md
  validation target: refresh or targeted inspect after provider-side changes.
```

Avoid changing templates unless canonical design finds a concrete missing evidence slot. Existing `report.md` already has Delegated Draft Evidence and EAL sections for Issue 210.

## 10. Migration / Compatibility / Rollback

- Compatibility: The change is documentation/skill workflow guidance only. It should not change runtime CLI behavior or existing discussion artifact validity.
- Existing lightweight Epic workflows remain valid if they record a skip reason and still satisfy reviewer gates.
- Existing delegated authoring artifacts remain governed by `workflow_spec_authoring.md`; no grandfathered evidence should be renamed or invalidated.
- Rollback: revert provider-side skill/docs wording and refresh or inspect the dogfooding mirror. Since no runtime schema is proposed, rollback is text-level.

## 11. Observability

- Record delegated draft adoption in Issue 210 `report.md` Evidence Adoption Ledger.
- Record design and plan reviewer gates in Issue 210 `report.md` Spec Authoring Gate.
- Record dogfooding mirror route in implementation evidence:
  - Option 1: run provider update into the dogfooding workspace, then inspect mirror diff.
  - Option 2: if update is intentionally skipped, run targeted provider-vs-mirror diff inspection for changed files and record the no-update reason.
  - Option 3: run `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` after mirror update when the canonical plan requires full validation.
- Use targeted `rg` checks for key phrases: `system-architect`, `cross-issue draft`, `Evidence Adoption Ledger`, `Issue 211`, `skip reason`, `spec-reviewer`.

## 12. Test Strategy

- Docs-only inspection:
  - Read provider-side `spec-dock-epic-planning/SKILL.md` as a first-read agent and verify it answers: when to request the draft, when to skip, where adoption is recorded, when reviewer gates apply, and what Issue 211 does not own.
  - Inspect `workflow_epic.md` to verify Epic planning completion and handoff package are discoverable without copying all delegated authoring policy.
- Traceability check:
  - Map AC-001 through AC-008 to changed skill/docs wording.
  - Confirm Issue 211 is referenced only as independent downstream consumer.
- Mirror validation:
  - Compare provider-side changed files against dogfooding mirror after update or targeted inspection.
  - Run `validate` / `sync` if the canonical plan selects a full dogfooding route; otherwise record the explicit no-run reason.
- Negative inspection:
  - Confirm no wording grants `system-architect` canonical doc authority.
  - Confirm no wording makes all Epics require heavyweight delegation.
  - Confirm no wording defines `spec-dock-epic-execution` behavior inside Issue 210.

## 13. ADR Candidates

- No ADR is required for Issue 210 if the implementation stays within the Epic planning workflow and existing delegated authoring policy.
- ADR candidate only if the team wants a durable, cross-scope default that all future planning workflows must use delegated architecture drafts by default.
- Follow-up candidate: a later guard/harness issue that checks skill first-read surfaces once the parent Epic stabilizes wording across skills.

## 14. Risks

- Risk: The skill becomes too long and duplicates `workflow_spec_authoring.md`.
  - Mitigation: keep skill to trigger/stop/routing bullets and link to docs for semantics.
- Risk: Issue 210 accidentally specifies execution coordination and overlaps Issue 211.
  - Mitigation: keep execution lifecycle terms in an explicit "future Issue 211 owns" boundary.
- Risk: Cross-issue draft package is treated as canonical issue docs.
  - Mitigation: repeatedly label issue-local drafts as `discussions/` evidence and require individual Issue planning to canonicalize.
- Risk: Dogfooding mirror appears updated because files currently match, but provider changes are not propagated.
  - Mitigation: require either actual update plus inspection or an explicit provider-vs-mirror diff/no-update evidence entry.
- Risk: Skip reason becomes a loophole for non-trivial Epics.
  - Mitigation: define non-trivial indicators and require reviewer visibility of skip rationale.

## 15. Requirement Clarification Requests

- none.

Non-blocking design decisions for the main orchestrator:

- Choose whether `workflow_spec_authoring.md` needs any change, or whether existing delegated authoring sections are sufficient and should only be linked from skill / `workflow_epic.md`.
- Choose the dogfooding mirror validation route: full update + validate/sync, targeted provider-vs-mirror inspection, or a staged route with recorded rationale.
- Choose exact wording for lightweight Epic skip evidence location: Epic `report.md` Spec Authoring Gate, design note, or both.

## 16. Integration Notes for Main Orchestrator

- Recommended adoption: partially or fully integrate this draft into Issue 210 canonical `design.md`, then update `report.md` Delegated Draft Evidence and Evidence Adoption Ledger.
- Do not adopt this draft without a fresh `spec-reviewer` pass on the canonical design.
- Keep implementation plan steps small:
  - Step 1: provider-side skill first-read spine.
  - Step 2: provider-side `workflow_epic.md` completion / handoff details.
  - Step 3: optional `workflow_spec_authoring.md` cross-reference only if the design finds a discoverability gap.
  - Step 4: dogfooding mirror validation and report evidence.
- Leaf evidence used: none beyond local source inspection; no depth=2 subdelegation was used.
- Forbidden actions avoided: no canonical docs edited, no implementation files edited, no tests/config/agent instructions/GitHub state edited, no dependency metadata mutated, no reviewer pass or promotion claimed.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
