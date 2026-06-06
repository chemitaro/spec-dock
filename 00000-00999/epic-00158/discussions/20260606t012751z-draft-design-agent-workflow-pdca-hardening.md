---
種別: draft-design
created_by_role: spec-dock-system-architect
scope_id: epic-00158
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/report.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_epic.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/reference_sync.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
  - src/spec_dock/assets/install_root/.agents/skills/
  - src/spec_dock/assets/spec_dock/docs/
  - src/spec_dock/assets/spec_dock/templates/
intended_targets:
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# epic-00158 Agent Workflow PDCA Hardening - delegated design draft

## Requirement Coverage

Design summary:

- This epic should design a context-surface hardening model, not a runtime enforcement feature.
- The core target is the boundary between provider-side skills, provider-side docs, provider-side templates, and the dogfooding mirror.
- The design should preserve the accepted ADR split: skills own the operational workflow spine, docs own meanings/details/hard cases, and templates own scaffolds/examples.
- `spec-dock-clarification` is the explicit exception: its mandatory source-grounded grill loop is skill-owned, while `workflow_clarification.md` becomes a bridge/reference surface.
- Evidence, delegated drafts, ChatGPT/Deep Research output, and sub-agent output remain proposal/evidence until the main orchestrator adopts them in canonical docs and `report.md`.

Target boundary:

- In scope: provider-side installed skill text, provider-side workflow/docs/template surfaces, dogfooding mirror inspection, Epic-level authority/evidence/reviewer gates, and first-wave design boundaries.
- Out of scope: runtime gate implementation, CLI validation changes, automated regression harness as the first fix, issue-level implementation sequencing, product feature expansion, and external multi-repo strategy.

Requirement trace:

| Requirement | Design treatment | Acceptance criteria supported |
|---|---|---|
| E-RQ-001 | Context surface ownership model is the central contract. | E-AC-001 |
| E-RQ-002 | First-read executable skill surface is the default for mandatory workflow spine. | E-AC-001, E-AC-004 |
| E-RQ-003 | Clarification is a skill-owned workflow exception. | E-AC-003 |
| E-RQ-004 | Spec authoring gate is modeled as a reviewer/evidence contract. | E-AC-004, E-AC-007 |
| E-RQ-005 | Evidence and canonical authority are separated by adoption ledger and fresh review. | E-AC-005 |
| E-RQ-006 | First wave follows the accepted decomposition ADR and defers guard/harness work. | E-AC-002 |
| E-RQ-007 | Provider source is authority; dogfooding mirror is verification evidence. | E-AC-006 |

## Existing Context Findings

Active context:

- `spec-dock/active/context-pack.md` points to `init-local-00003` and `epic-00158`; no active issue is set.
- Epic `requirement.md` is authored and reports no blocking requirement questions.
- Epic `report.md` records requirement evidence adoption and says design/plan canonical authoring is still pending.
- Active `design.md` and `plan.md` are still template scaffold content, so this draft should be treated as proposal evidence only.

Provider source vs dogfooding mirror:

- Provider-side authority for installed agent tooling is `src/spec_dock/assets/install_root/.agents/skills/`.
- Provider-side authority for shipped docs/templates is `src/spec_dock/assets/spec_dock/docs/` and `src/spec_dock/assets/spec_dock/templates/`.
- Dogfooding mirror surfaces under `.agents/`, `spec-dock/docs/`, and `spec-dock/templates/` currently reflect installed behavior and are validation/inspection targets, not the implementation source of truth.
- Active epic symlink resolves to `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening`.

Relevant provider surfaces:

- Skills:
  - `spec-driven-tdd-workflow/SKILL.md` is the hub/router surface and currently still says to keep `spec-dock/docs/` as source of truth and skills concise.
  - `spec-dock-issue-planning/SKILL.md` already exposes mandatory spec authoring gates and delegated draft boundaries in compact form.
  - `spec-dock-clarification/SKILL.md` currently says `workflow_clarification.md` is the source of truth, which conflicts with the accepted clarification ADR.
  - `spec-dock-system-architect/SKILL.md` and `spec-dock-implementation-planner/SKILL.md` already model scope-local flat discussion drafts, no canonical ownership, and depth=2 delegation.
  - `spec-dock-epic-planning/SKILL.md` already states epic authoring needs fresh `spec-reviewer` pass before issue decomposition.
- Docs:
  - `workflow_spec_authoring.md` is the shared phase-promotion and delegated evidence contract.
  - `workflow_epic.md` adds Epic-specific reuse, decomposition, discussion naming, and quality gates.
  - `phase_design.md` defines Epic design content, delegated design authoring gate, and diagram selection.
  - `workflow_clarification.md` is currently a full workflow page, but accepted ADR says it should become a bridge/reference if retained.
  - `reference_sync.md` fixes the `.agent` generated state and dogfooding read-order contract.
- Templates:
  - `templates/README.md` states `draft-requirement` / `draft-design` / `draft-plan` have no dedicated draft template and render from scope canonical templates as discussion-local drafts.
  - `templates/epic/report.md` already includes Evidence Adoption Ledger, Spec Authoring Gate, Delegated Draft Evidence, failure modes, and non-pass reviewer states.
  - `templates/discussions/{interview,research,disc}.md` are the likely scaffold/example surfaces for clarification evidence.

## Design Decisions

1. Context surface ownership is a first-class Epic architecture contract.
   - Skills must carry the minimum executable workflow spine: what to read first, what order to follow, when to stop, what evidence to leave, what gates are non-negotiable, and which docs/templates to inspect next.
   - Docs must carry meanings, policy detail, field semantics, lifecycle references, hard-case criteria, and longer examples.
   - Templates must carry scaffold shape, evidence slots, and good examples. They must not become compliance authority.

2. First-read skill surface is compact, not complete.
   - The design does not copy full docs into skills.
   - Each affected skill should be able to prevent the known failure modes before linked docs are opened: skipped phase order, missing fresh reviewer pass, degraded reviewer state treated as pass, evidence treated as canonical without adoption, and unresolved gaps absorbed into execution.

3. `spec-dock-clarification` is the durable exception.
   - Its `SKILL.md` should own the source-grounded grill loop directly.
   - It should instruct agents to read sources, form provisional understanding, pick one essential pressure-test question, route human-facing questions through the orchestrator, capture answers in the right artifact, and decide iterate/handoff.
   - `workflow_clarification.md` should stop being the mandatory runbook. If retained in first wave, it should point to the skill and describe artifact/document relationships.

4. Spec authoring gate is modeled as an authority/evidence contract.
   - Requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> downstream handoff remains the only promotion path.
   - missing, stale, failed, unavailable, denied, waived, and provisional states are non-pass states.
   - Waiver can record user risk acceptance but must not be called reviewer pass.

5. Evidence adoption remains main-orchestrator-owned.
   - Delegated draft, research, discussion, ADR candidate, sub-agent output, and external ChatGPT/Deep Research output are evidence until adopted.
   - Canonical adoption requires main-orchestrator rewrite into canonical docs and `report.md` Evidence Adoption Ledger disposition.
   - Delegated drafts must keep `adoption_status: unreviewed`, `reflected_to: []`, and pending/not-run diff guard state until the orchestrator records otherwise.

6. First wave should preserve the accepted issue decomposition.
   - `iss-00159` remains the first concrete specimen for the issue-planning skill spine.
   - Cross-surface alignment, clarification rewrite, hub/leaf routing, workflow docs, and templates follow as the first wave.
   - Regression checks, manual workflow harness, and runtime gates stay deferred until the cleaned context surfaces define stable expected behavior.

7. Provider-side source is the source of record for shipped assets.
   - Edits should start under `src/spec_dock/assets/install_root/.agents/skills/` or `src/spec_dock/assets/spec_dock/{docs,templates}/`.
   - Dogfooding mirror inspection must confirm update behavior and human/agent read-order, but mirror edits alone must not be treated as shipped source changes.

## Alternatives Considered

Alternative A: Keep skills thin and leave mandatory workflow in docs.

- Rejected. This is the observed failure mode: agents may not open the right linked docs before acting.

Alternative B: Copy full workflow docs into every relevant skill.

- Rejected. This would create skill bloat and drift. The design only moves compact operational spine into skills.

Alternative C: Start with runtime gates or regression harness.

- Rejected for first wave. Enforcement before context cleanup risks locking in weak or contradictory surfaces.

Alternative D: Treat templates as the compliance authority.

- Rejected. Templates are examples and scaffolds; compliance authority belongs to workflow contracts, canonical docs, reviewer gates, and report ledger evidence.

Alternative E: Remove `workflow_clarification.md` immediately.

- Deferred. Existing links make immediate removal risky. Bridge/reference conversion is safer for first wave; retirement can be revisited after link cleanup.

## Boundary / Contract Model

Authority boundaries:

| Surface | Owns | Must not own |
|---|---|---|
| Skill `SKILL.md` | Mandatory task order, stop conditions, first-read gates, evidence obligations, next-doc routing | Full field semantics, long policy explanation, exhaustive examples |
| Workflow/phase docs | Lifecycle details, field meanings, hard cases, shared policy, phase-specific review criteria | Hidden mandatory first action that a skill omits |
| Templates | Starting shape, evidence slots, good examples, discussion/canonical scaffold | Compliance authority, phase promotion authority |
| Discussion drafts/research | Evidence, proposal, synthesis, ADR candidates | Canonical authority, reviewer pass, phase promotion |
| Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` | Main orchestrator-owned source of truth and adoption ledger | Sub-agent direct ownership |
| Accepted ADR | Durable architecture decision evidence | Implementation readiness by itself |
| Dogfooding mirror | Validation and installed-surface inspection | Provider source authority |

Clarification exception:

- General workflows can be skill-spine plus docs-detail.
- `spec-dock-clarification` owns its own workflow loop in the skill because the interaction is the skill's primary behavior.
- The workflow doc can remain as navigation/reference for artifact relationships and links.

Reviewer/evidence gates:

- `spec-reviewer` pass must be fresh and target the canonical artifact being promoted.
- Delegated draft review is improvement input only.
- Post-run diff guard and `report.md` ledger adoption are required before delegated content can be considered adoption-ready evidence.

Provider/mirror handling:

- Provider edits should be applied first.
- Dogfooding mirror should be refreshed or inspected according to the change type.
- Validation evidence should distinguish provider source diff, dogfooding generated mirror state, and active `.agent` projection.

## Dependency Analysis

Package/dependency view: N/A for runtime package dependencies.

Reason:

- This epic is a shipped asset context-surface cleanup. It does not require adding Python package dependencies, changing import direction, introducing runtime services, or changing CLI module dependencies in the first wave.
- The meaningful dependency is an authority/read dependency between text surfaces:
  - hub skill routes to leaf skills,
  - leaf skills route to workflow/phase/reference docs,
  - docs route to templates/rules where field examples or naming rules are needed,
  - report ledgers route evidence into canonical authority.

Text-surface dependency guard:

- Avoid circular authority claims such as "skill says docs own mandatory workflow" while an ADR says "skill owns operational workflow spine".
- Avoid requiring agents to discover non-pass reviewer states only in docs after the skill has already authorized handoff.
- Avoid template examples that imply templates are pass/fail authorities.

## Source of Record

Primary source of record for implementation-facing changes:

- `src/spec_dock/assets/install_root/.agents/skills/`
- `src/spec_dock/assets/spec_dock/docs/`
- `src/spec_dock/assets/spec_dock/templates/`

Primary source of record for this epic's canonical design, once adopted:

- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/report.md`

Validation and generated state sources:

- `spec-dock/.agent/active.json` is the authority source for active selection.
- `spec-dock/active/context-pack.md` is human guidance mirroring active state.
- `spec-dock/.agent/index.json`, `spec-dock/.agent/deps-issues.json`, `spec-dock/.agent/tree.json`, and related projections are generated inspection surfaces.

This draft's status:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `epic-00158`
- draft artifact path: `spec-dock/active/epic/discussions/20260606t012751z-draft-design-agent-workflow-pdca-hardening.md`
- draft status: produced
- authority: proposed
- adoption_status: unreviewed
- reflected_to: []
- intended_targets: `spec-dock/active/epic/design.md`, `spec-dock/active/epic/report.md`
- diff_guard_result: pending
- canonical artifacts edited: none
- final authority claimed: no

## Data Flow / Domain Model / Interface Contract

Domain vocabulary:

- `Context surface`: a file or generated view an agent reads before or during work.
- `Workflow spine`: the compact operational steps and hard stops that must be visible on first skill read.
- `Detail surface`: docs that explain why, meaning, hard cases, and field semantics.
- `Scaffold surface`: templates that make correct artifact shape easy to start from.
- `Evidence`: non-canonical input that may influence canonical docs only after adoption.
- `Adoption`: main-orchestrator decision recorded in `report.md` and reflected into canonical docs if accepted.
- `Dogfooding mirror`: installed local copy used to verify the shipped source behavior.

Main authoring and dogfooding flow:

```plantuml
@startuml
title epic-00158 context-surface authoring and dogfooding flow
' Question answered: How does evidence become shipped context-surface design without crossing authority boundaries?
' Scope: Epic design-level authority, adoption, provider source, and dogfooding mirror.
' Excluded details: issue-level file edits, exact implementation steps, runtime guard internals.
' Update trigger: authority boundary, evidence adoption, provider/mirror handling, or first-wave sequencing changes.

actor "Main orchestrator" as Orchestrator
participant "Delegated architect\n(system-architect)" as Architect
database "Epic discussions\nproposal evidence" as Discussions
database "Epic canonical docs\nrequirement/design/plan/report" as Canonical
participant "spec-reviewer\nfresh gate" as Reviewer
folder "Provider assets\nsrc/spec_dock/assets/..." as Provider
folder "Dogfooding mirror\n.agents/ + spec-dock/" as Mirror
database ".agent projections\nactive/index/deps/tree" as AgentState

Orchestrator -> Architect: bounded design draft request
Architect -> Discussions: create one draft-design Markdown
Architect --> Orchestrator: proposed evidence, no authority claim
Orchestrator -> Canonical: adopt/reject in report ledger
Orchestrator -> Canonical: rewrite accepted design content
Orchestrator -> Reviewer: fresh review of canonical design
Reviewer --> Orchestrator: passed or non-pass state
Orchestrator -> Provider: later issue-level edits start from provider source
Provider -> Mirror: update/inspect installed dogfooding copy
Mirror -> AgentState: validate/sync generated views
AgentState --> Orchestrator: dogfooding evidence
@enduml
```

Interface contracts:

- Skill contract:
  - Input: task type, active context, role boundary.
  - Output: mandatory workflow spine, stop conditions, evidence obligations, next surfaces to read.
  - Failure output: blocked/incomplete reason and route to clarification or prior phase.
- Docs contract:
  - Input: skill-routed need for detail.
  - Output: meanings, policy, hard cases, naming, lifecycle, and phase details.
  - Failure output: contradiction or stale authority claim to be corrected under first-wave cleanup.
- Template contract:
  - Input: new canonical or discussion artifact creation.
  - Output: scaffold/evidence slots/good examples.
  - Failure output: misleading authority wording or missing slots requiring template alignment.
- Report ledger contract:
  - Input: evidence or draft that may influence canonical state.
  - Output: adopted/partially_adopted/rejected/deferred/stale/blocked disposition with rationale, target, and next action.

## File / Module Change Plan

Epic-level change surface guidance, not issue-level implementation steps:

| Surface family | Provider-side source | Dogfooding mirror / validation | Epic design expectation |
|---|---|---|---|
| Hub skill | `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` | `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | Router must not imply mandatory workflow is docs-only. |
| Issue planning skill specimen | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | `.agents/skills/spec-dock-issue-planning/SKILL.md` | First concrete specimen for first-read authoring gate spine. |
| Clarification skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | `.agents/skills/spec-dock-clarification/SKILL.md` | Skill-owned source-grounded grill workflow. |
| Authoring docs | `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`, `phase_design.md`, related workflow docs | `spec-dock/docs/...` | Docs own detailed semantics and gate definitions without hiding first-read stops. |
| Clarification doc | `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` | `spec-dock/docs/workflow_clarification.md` | Bridge/reference, not mandatory runbook authority. |
| Templates | `src/spec_dock/assets/spec_dock/templates/...` | `spec-dock/templates/...` | Scaffold evidence slots and examples; no compliance authority. |
| Generated active/read state | N/A generated runtime state | `spec-dock/.agent/*`, `spec-dock/active/*` | Validate/sync evidence, not provider source. |

## Migration / Compatibility / Rollback

Migration:

- Stage wording changes through provider-side assets first.
- Keep existing links working while authority wording shifts; especially preserve `workflow_clarification.md` as bridge/reference until link cleanup is complete.
- Treat historical `note` and manifest-heavy delegated authoring artifacts as grandfathered; do not rename or invalidate old evidence merely because current standard changed.
- For installed consumer repos, `spec-dock update` is the normal refresh path; dogfooding should inspect the installed mirror after provider changes.

Compatibility:

- No runtime API or Python package compatibility change is required in first wave.
- Existing docs that still link to `workflow_clarification.md` remain usable if the doc becomes a bridge rather than being deleted.
- Existing discussion draft naming accepts `draft-design`; the filename used by this draft follows the current catalog.

Rollback:

- Text-surface changes can be reverted by restoring provider-side asset content and re-running update/dogfooding verification.
- If clarification bridge conversion causes link ambiguity, rollback to the prior doc-owned text is mechanically possible but should be recorded as reintroducing the accepted ADR's first-read risk.
- If first-wave issues reveal that one slice is too broad or too narrow, use the accepted decomposition ADR's merge/split guidance rather than moving regression checks earlier.

## Observability

Operational observability for this epic is evidence-based, not telemetry-based:

- Diff evidence:
  - provider-side asset diff grouped by skill/docs/templates family.
  - dogfooding mirror diff or targeted mirror inspection after refresh.
- Command evidence:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync` or `sync --no-github` when network/GitHub access is intentionally avoided.
  - targeted `rg` checks for non-pass reviewer wording, evidence adoption wording, clarification source-of-truth wording, and template authority wording.
- Ledger evidence:
  - Epic/Issue `report.md` Evidence Adoption Ledger.
  - Spec Authoring Gate per phase.
  - Delegated Draft Evidence for any scope-local drafts.

Security:

- No secrets, tokens, `.env*`, or credentialed external side effects are required.
- GitHub mutation is outside first-wave design authoring unless a later issue explicitly authorizes it.
- External research and ChatGPT/Deep Research outputs must keep source/adoption status and must not become canonical authority without ledger adoption.

## Test Strategy

Test strategy is layered by risk and surface:

- Static/content assertions:
  - Verify provider skills contain mandatory first-read gates and do not contradict the ownership ADR.
  - Verify docs explain detailed semantics and do not claim doc-owned mandatory workflow where ADR says skill-owned.
  - Verify templates retain scaffold/evidence-slot wording and avoid compliance-authority language.
- Scaffold/update tests:
  - For shipped asset changes, update installer/init/update assertions where existing tests cover bundled asset content or file presence.
  - Confirm provider-side assets install into `.agents/` and `spec-dock/` mirror as expected.
- Runtime validation:
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Run `./spec-dock/scripts/spec-dock sync` when GitHub state is relevant, or `sync --no-github` for local-only dogfooding evidence.
- Manual dogfooding smoke:
  - Read a target skill as an agent would and confirm the next action, stop condition, reviewer gate, evidence obligation, and next docs are visible before opening linked docs.
  - Confirm `spec-dock-clarification/SKILL.md` is executable as a source-grounded grill loop without relying on `workflow_clarification.md`.
- Later deferred tests:
  - Add regression checks only after the cleaned surfaces stabilize.
  - Add manual workflow scenario harness only after the expected behavior is explicit enough to evaluate.

## ADR Candidates

Already accepted and should be referenced in canonical design:

- `20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
- `20260605t080509z-01-adr-clarification-skill-owned-workflow.md`
- `20260605t080509z-02-adr-first-wave-issue-decomposition.md`

Potential future ADR candidates:

- Whether `workflow_clarification.md` should be fully retired after bridge/link cleanup.
- When the project should move from context-surface cleanup to runtime/validation enforcement.
- Whether future delegated authoring role labels should normalize on host role names (`system-architect`) or skill names (`spec-dock-system-architect`) across user-facing reports and diff guard frontmatter. Current diff guard accepts the skill name in frontmatter.

No new ADR is required before canonical Epic design adoption if the canonical design simply implements the three accepted ADRs.

## Risks

- Skill bloat risk:
  - Mitigation: keep only mandatory operational spine in skills; leave semantics and hard cases in docs.
- Drift risk:
  - Mitigation: provider source first, dogfooding mirror inspection, later regression checks after stabilization.
- Authority confusion risk:
  - Mitigation: report ledger adoption, non-pass reviewer state wording, and no delegated final authority claims.
- Clarification link risk:
  - Mitigation: bridge `workflow_clarification.md` before retirement.
- Over-broad first-wave issue risk:
  - Mitigation: follow accepted decomposition ADR and split/merge cleanup slices only when evidence shows reviewability problems.
- Guard/harness inversion risk:
  - Mitigation: keep enforcement deferred until expected text and behavior are stable.
- Existing dirty canonical docs risk:
  - Mitigation: orchestrator should distinguish pre-existing canonical edits from this delegated draft during post-run diff guard and adoption.

## Requirement Clarification Requests

none

Non-blocking design questions for the orchestrator:

- Should canonical design explicitly record `created_by_role` normalization as `system-architect` host role -> `spec-dock-system-architect` frontmatter role, or leave it as implementation detail of delegated authoring guard?
- Should `workflow_clarification.md` first-wave outcome be fixed as bridge-only, or should canonical design allow bridge-or-staged-retirement depending on link cleanup scope?
- Should the cross-surface alignment issue be one broad issue or split by skill/docs/templates family after `iss-00159` dogfooding evidence?

## Integration Notes for Main Orchestrator

Recommended canonical design adoption:

- Adopt the context-surface ownership model as the `全体像` and `契約` spine of `design.md`.
- Use the component/module and authority-boundary tables as the main Epic-level design view.
- Mark package dependency as `N/A` with the text-surface dependency reason.
- Include the PlantUML flow if the canonical design needs a visual; it is Epic-level and avoids issue implementation sequencing.
- Record this draft in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger before reflecting any content into canonical `design.md`.
- Run a fresh `spec-reviewer` on the canonical design after integration; this draft does not claim review pass.

Lightweight delegated draft evidence block:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `epic-00158`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/report.md`
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/active/initiative/requirement.md`
  - accepted ADRs under `spec-dock/active/epic/discussions/20260605t080509z-*`
  - provider-side `src/spec_dock/assets/install_root/.agents/skills/`
  - provider-side `src/spec_dock/assets/spec_dock/docs/`
  - provider-side `src/spec_dock/assets/spec_dock/templates/`
- draft artifact path: `spec-dock/active/epic/discussions/20260606t012751z-draft-design-agent-workflow-pdca-hardening.md`
- draft status: produced
- authority: proposed
- adoption_status: unreviewed
- reflected_to: []
- intended_targets:
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/report.md`
- diff_guard_result: pending
- integration notes: main orchestrator must run post-run diff guard, adopt/reject in `report.md`, rewrite accepted content into canonical design, and run fresh `spec-reviewer`.
- rejected portions: none proposed
- blockers: none
- canonical artifacts edited: none
- final authority claimed: no

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
