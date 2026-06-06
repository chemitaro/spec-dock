---
種別: draft-plan
created_by_role: spec-dock-implementation-planner
scope_id: epic-00158
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/docs/workflow_epic.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_epic.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
  - spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/requirement.md
intended_targets:
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Draft Plan: epic-00158 Agent Workflow PDCA Hardening

## Plan Summary

This draft proposes an Epic-level plan for first-wave agent workflow PDCA hardening. It keeps the plan at Epic scope: issue slicing, dependency order, integration checkpoints, issue readiness, verification strategy, docs / rollout impact, and final quality gates. It intentionally does not define issue-internal implementation steps, TDD cadence, or commit rhythm.

The core plan is dependency-derived:

1. Start with existing `iss-00159` as the smallest concrete specimen for the skill-owned workflow spine pattern.
2. Use that specimen to ground a broader skills / docs / templates inventory and cleanup.
3. Apply the special clarification ADR after the general ownership model is visible.
4. Update hub routing after the leaf surfaces it routes to are stable enough to reference.
5. Align workflow docs and templates after skill responsibilities and routing are clear.
6. Defer regression checks, manual harness, and runtime gates until cleaned surfaces define stable expectations.

Plan adoption remains main-orchestrator-owned. This draft is proposal evidence only and requires canonical rewrite into `plan.md`, report ledger adoption, post-run diff guard, and a fresh `spec-reviewer` plan gate before downstream handoff.

## Requirement / Design Traceability

### E-RQ / E-AC closure mapping

| Requirement / AC | Primary plan treatment | Closure evidence expected |
|---|---|---|
| E-RQ-001 Context surface ownership | Issue lane 2 inventory plus lanes 5 and 6 cleanup make skill / docs / templates ownership consistent | Provider-side skill/docs/templates diff, contradiction check, dogfooding mirror inspection |
| E-RQ-002 First-read executable skill surface | `iss-00159` establishes the specimen; later skill lanes generalize it | Skill first-read smoke, non-pass wording inspection, doc routing inspection |
| E-RQ-003 Clarification skill-owned workflow | Dedicated clarification issue implements ADR 01 and keeps `workflow_clarification.md` as bridge unless link cleanup supports retirement | `spec-dock-clarification/SKILL.md`, bridge/reference doc, interview/research/disc templates |
| E-RQ-004 Spec authoring gate visibility | `iss-00159`, hub routing, workflow docs alignment, and templates all repeat the fresh reviewer / non-pass boundary without making templates authority | Targeted `rg` inspection for fresh pass, non-pass states, report evidence obligation |
| E-RQ-005 Evidence and canonical authority boundary | `iss-00159`, docs alignment, and template alignment make delegated evidence adoption visible | Report EAL / Delegated Draft Evidence slots and wording inspection |
| E-RQ-006 First wave decomposition | Canonical plan should adopt the ordered issue list from ADR 02 with deferred guard work clearly separated | Epic plan issue list, dependencies, report follow-up ledger |
| E-RQ-007 Provider source / dogfooding mirror boundary | Every implementation issue must name provider source authority and mirror validation | Provider source diff, root `.agents` / `spec-dock` mirror inspection, validate / sync evidence |
| E-AC-001 | Cross-surface ownership consistency after lanes 2, 5, 6 | Surface inventory matrix and contradiction check |
| E-AC-002 | ADR 02 issue set represented in canonical plan | Issue list and dependency graph in `plan.md` |
| E-AC-003 | Dedicated clarification issue | First-read smoke for `spec-dock-clarification` |
| E-AC-004 | Reviewer gate wording across skills/docs/templates | Non-pass wording and Spec Authoring Gate inspection |
| E-AC-005 | Evidence adoption boundary | EAL entries in Epic / Issue reports |
| E-AC-006 | Provider / mirror validation | `validate`, `sync`, provider/mirror targeted inspection |
| E-AC-007 | No blocking question for authoring handoff | Plan gate records no unresolved requirement/design blocker before issue handoff |

### Design decision trace

| Design decision | Plan consequence |
|---|---|
| Skills own operational workflow spine; docs own detail; templates own scaffolds/examples | Slice work by context surface and prevent template-compliance or docs-hidden-runbook drift |
| `spec-dock-clarification` is a skill-owned exception | Give clarification its own issue lane, not a subtask hidden inside generic docs cleanup |
| Delegated / external evidence stays non-canonical until main orchestrator adoption | Require report ledger updates at each phase and keep this draft unreviewed / unreflected |
| Provider source is shipped asset authority; dogfooding mirror is validation | Each issue readiness contract must include provider-side source and mirror verification |
| Runtime guard / harness is later PDCA work | Defer guard issues until cleaned surfaces define stable expected behavior |

## Milestones

| Milestone | Scope | Exit condition |
|---|---|---|
| M0 Plan adoption gate | Canonical Epic plan authoring | Main orchestrator integrates accepted portions into `plan.md` / `report.md`; post-run diff guard and fresh plan reviewer are handled by orchestrator |
| M1 Specimen skill spine | `iss-00159` | Issue planning skill demonstrates the minimal first-read workflow spine pattern without changing runtime policy |
| M2 Ownership inventory and first cleanup pass | `Align Skill Docs Template Context Surfaces` | Contradictions in skills/docs/templates are inventoried and priority surfaces align to ADR ownership |
| M3 Clarification exception implemented | `Revise spec-dock-clarification as skill-owned grill workflow` | Clarification workflow is visible from the skill first-read surface and bridge/doc/template support is coherent |
| M4 Routing and reference surfaces aligned | Hub routing plus workflow docs | Hub routes to leaf-owned workflows; docs no longer hide mandatory operational workflow omitted by skills |
| M5 Template teaching surface aligned | Templates | Templates provide slots and examples without becoming compliance authorities |
| M9 Epic final quality gate | Whole Epic | E-RQ/E-AC closure evidence, provider/mirror validation, report ledgers, and final reviewers are complete enough for human merge judgment |

## Dependency-Derived Execution Order

The recommended dependency order is:

1. `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`
   - Depends on: accepted ADRs and existing issue requirement.
   - Reason: creates the first concrete, small specimen for the workflow spine pattern before wider cleanup.

2. `Align Skill Docs Template Context Surfaces`
   - Depends on: `iss-00159` specimen outcome.
   - Reason: broad inventory should reuse the specimen vocabulary and prevent one-off wording from spreading.

3. `Revise spec-dock-clarification as skill-owned grill workflow`
   - Depends on: ADR 01 and at least the ownership inventory from lane 2.
   - Reason: clarification is an explicit exception; implementing it before the general boundary is visible risks either generic coaching drift or doc-owned workflow relapse.

4. `Clarify Hub And Leaf Skill Routing Surface`
   - Depends on: the issue-planning specimen and clarification lane.
   - Reason: the hub can only route accurately once the important leaf surfaces own the right workflow spine.

5. `Align Workflow Docs With Skill Spine Boundary`
   - Depends on: lanes 1, 3, and 4.
   - Reason: docs should preserve lifecycle/detail authority without contradicting the now-stabilized skill-owned operational spines.

6. `Align Templates As Scaffolds And Examples`
   - Depends on: lanes 2, 3, and 5.
   - Reason: templates should teach the final adopted behavior and report/evidence slots after skill/docs boundaries are known.

Later PDCA work starts only after M5 has stable expected surface behavior.

## Issue / Step Slicing

### Issue slicing policy

- Slice by context-surface responsibility and review boundary, not by file count.
- Keep each issue small enough to dogfood and inspect before the next lane.
- Every issue must trace to at least one E-RQ / E-AC and one design decision.
- Provider-side shipped asset source is the implementation authority; dogfooding mirror is validation.
- Templates are never compliance authority.
- Regression / harness / runtime enforcement must not become first-wave blockers.
- If a planned issue becomes too broad, split by skill family or artifact family.
- If a planned issue becomes too narrow to close a cross-surface contradiction, merge it into the cross-surface alignment lane.
- Issue-internal implementation steps and TDD cadence belong to issue `plan.md`, not this Epic plan.

### Recommended issue list and tranches

| Order | Tranche | Issue / candidate | Primary closes | Scope notes |
|---:|---|---|---|---|
| 1 | T1 specimen | `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates` | E-RQ-002, E-RQ-004, E-RQ-005, E-RQ-007; E-AC-004, E-AC-005, E-AC-006, E-AC-007, E-AC-008, E-AC-009 | Existing issue. Limit first change to `spec-dock-issue-planning` provider source plus dogfooding mirror semantic identity. No runtime gate. |
| 2 | T2 inventory / consistency | `Align Skill Docs Template Context Surfaces` | E-RQ-001, E-RQ-006, E-RQ-007; E-AC-001, E-AC-002, E-AC-006 | Cross-cutting inventory and contradiction cleanup. Should produce or update a traceable matrix of skill/docs/templates ownership. |
| 3 | T2 exception lane | `Revise spec-dock-clarification as skill-owned grill workflow` | E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-007; E-AC-003, E-AC-004, E-AC-005, E-AC-006 | Implement ADR 01. Keep `workflow_clarification.md` as bridge/reference unless link cleanup safely supports retirement. |
| 4 | T3 routing | `Clarify Hub And Leaf Skill Routing Surface` | E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004; E-AC-001, E-AC-003, E-AC-004 | Hub acts as router plus invariant surface; leaf skills own detailed operational spines. |
| 5 | T3 docs boundary | `Align Workflow Docs With Skill Spine Boundary` | E-RQ-001, E-RQ-004, E-RQ-005; E-AC-001, E-AC-004, E-AC-005 | Remove docs-hidden mandatory workflow that skills omit; keep detailed lifecycle/field/hard-case guidance in docs. |
| 6 | T4 templates | `Align Templates As Scaffolds And Examples` | E-RQ-001, E-RQ-003, E-RQ-005; E-AC-001, E-AC-003, E-AC-005 | Templates show artifact shape, evidence slots, and examples; they must not claim compliance authority. |

### Deferred work list with revisit conditions

| Deferred candidate | Revisit condition | Reason deferred now |
|---|---|---|
| `Add Skill Spine Regression Checks` | M5 complete and cleaned surfaces define stable expected wording / structure | Checks before cleanup would lock in unstable surfaces |
| `Add Manual Workflow Scenario Harness` | At least two representative skill workflows have stable first-read smoke criteria | Harness needs stable scenarios to evaluate |
| Runtime gate / `gate status` / issue start-finish guards | Authoring contract has machine-checkable signals and report ledger conventions are stable | Runtime enforcement is not the first-wave problem |
| Full retirement of `workflow_clarification.md` | Link inventory shows no mandatory references requiring bridge behavior | Immediate deletion risks breaking navigation |
| `.github/agents` / Copilot support or role registry expansion | A separate requirement/design fixes product need and support boundary | Explicitly outside this delegated plan scope |

## Test Strategy Mapping

| Verification layer | Applies to | Expected evidence |
|---|---|---|
| Content inspection | All first-wave issues | Targeted `rg` / review for ownership wording, fresh reviewer pass, non-pass state handling, evidence adoption, provider/mirror boundary |
| Provider/mirror semantic identity | Shipped skill/docs/templates changes | Provider-side source diff plus dogfooding mirror inspection; exact divergence must be explained in report |
| SpecDock validation | Scaffold / mirror-affecting changes | `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` where applicable |
| Installer / update regression | Changes that affect shipped asset installation or generated structure | Narrow unittest coverage in installer/runtime test area when structure or copy behavior changes |
| Manual first-read smoke | Skill-owned workflow changes | A reader can identify next action, stop condition, reviewer gate, evidence obligation, and next docs from the skill first-read surface |
| Report ledger audit | Delegated evidence or external research adoption | EAL and Delegated Draft Evidence entries identify source, adoption status, target, reviewer state, blockers, and next action |
| Final Epic diff review | Whole Epic | Base/head endpoints, `git diff --stat`, `git diff --name-status`, and shared evidence for final reviewers |

## Review Gates

- Plan integration gate:
  - Main orchestrator decides which parts of this draft to adopt.
  - Adopted content is rewritten into canonical `plan.md`; this draft is not canonical.
  - `report.md` should record delegated plan draft evidence and EAL adoption.
  - Fresh `spec-reviewer` must review canonical plan before downstream handoff.

- Issue readiness gate:
  - Each issue has requirement/design/plan that trace to Epic E-RQ/E-AC and ADRs.
  - Scope and non-scope explicitly exclude runtime guard / harness when not in that issue.
  - Provider-side source and dogfooding mirror validation expectations are named.
  - Rollback / compatibility and report evidence destinations are present.
  - Fresh reviewer gates for that issue are recorded before execution handoff.

- Integration checkpoint gate:
  - After each tranche, inspect whether new wording introduced cross-surface contradiction.
  - If contradiction exists, route it to the next alignment lane or return to the responsible issue.
  - Do not start deferred guard work merely because contradiction was discovered.

- Epic-wide pre-PR / final review gate:
  - Follow `workflow_epic.md` epic-wide pre-PR gate: record base/head endpoints, diff stat, name-status, shared evidence, fresh deep-consultant where orchestrator chooses, and fresh spec-reviewer on the same evidence.
  - All findings need disposition as fixed, superseded, or explicitly deferred with user acceptance before PR update / push.

## Rollback / Compatibility

- Text-surface rollback is provider-source rollback plus dogfooding mirror re-validation.
- If a skill rewrite becomes too large or duplicates docs, roll back to the last minimal workflow spine and move details back to docs/templates.
- If `workflow_clarification.md` bridge wording causes link ambiguity, restore bridge clarity rather than retiring the doc early.
- Existing historical discussion / delegated artifacts remain grandfathered; first-wave changes should not rename or invalidate them.
- New consumer repos may receive shipped asset updates through init/update, so issue plans must consider both fresh init and update behavior where file structure changes.
- Compatibility is semantic, not necessarily byte-for-byte, between provider and dogfooding mirror; any intentional divergence must be recorded.

## Docs Impact

- Provider-side docs impact is expected under `src/spec_dock/assets/spec_dock/docs/`, especially workflow / phase / clarification references.
- Provider-side templates impact is expected under `src/spec_dock/assets/spec_dock/templates/`, especially discussion and report evidence slots.
- Installed agent-tooling assets impact is expected under `src/spec_dock/assets/install_root/.agents/skills/`.
- Dogfooding mirror validation should inspect `.agents/` and `spec-dock/` after shipped asset changes.
- Documentation changes must preserve the authority boundary:
  - Skills: mandatory operational workflow spine.
  - Docs: details, meanings, lifecycle policy, hard cases.
  - Templates: scaffolds, evidence slots, examples.
- Docs should not contain hidden mandatory first actions that the corresponding skill omits.

## Final Quality Gate

The Epic final quality gate should require:

- All first-wave issue lanes either completed or explicitly deferred with non-blocking rationale.
- E-RQ / E-AC closure matrix updated in canonical `plan.md` or `report.md`.
- Provider-side source and dogfooding mirror validation recorded for every shipped asset change.
- `validate` / `sync` evidence recorded or explicit reason documented when not applicable.
- Evidence Adoption Ledger has no unresolved `blocked` or `stale` entries.
- Spec Authoring Gate records fresh plan reviewer pass before downstream handoff.
- Deferred work list includes revisit conditions, owner candidate, and why it is not a first-wave blocker.
- Final epic-wide review follows `workflow_epic.md` before PR update / push.

## Plan Blockers

Plan Blockers: none for draft production.

Unresolved questions for canonical integration:

- Whether the broad `Align Skill Docs Template Context Surfaces` lane should be a single issue or split by skill family / artifact family after inventory. Recommended default: keep one issue for inventory and first cleanup, split only if review scope becomes too broad.
- Whether `workflow_clarification.md` can be fully retired in first wave. Recommended default: bridge/reference only; full retirement is deferred until link inventory supports it.
- Whether manual smoke probes should be required in every first-wave issue. Recommended default: require targeted first-read smoke for skill-owned workflow changes; defer full harness.

These questions do not block Epic-level plan drafting because the default choices are already constrained by requirement, design, and ADR 02.

## Integration Notes for Main Orchestrator

- Draft artifact path: `spec-dock/active/epic/discussions/20260606t014721z-draft-plan-agent-workflow-pdca-hardening.md`
- Suggested canonical targets:
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
- Suggested report evidence entry:
  - role: `spec-dock-implementation-planner`
  - phase: plan
  - scope: `epic-00158`
  - source artifacts read: see frontmatter `source_paths`
  - draft artifact path: this file
  - draft status: produced
  - authority: proposed
  - adoption_status: unreviewed
  - reflected_to: `[]`
  - intended_targets: see frontmatter
  - diff_guard_result: pending
  - rejected portions: none identified in draft
  - blockers: none for draft production
  - canonical artifacts edited: none
  - final authority claimed: no
- The repository state observed before this draft already had modified canonical Epic docs and one untracked draft-design discussion file. This draft did not edit those files. The orchestrator should run the post-run diff guard with its own baseline rules and verify this delegated run contributed exactly this new Markdown file.
- `workflow_epic.md` and `reference_naming.md` list `draft-plan` in the current discussion catalog. The implementation-planner skill also contains older cautionary wording to avoid introducing new kinds unless canonical docs added them; canonical docs now do list `draft-plan`, so this filename kind is treated as naming-rule compliant.
- No leaf evidence producer was used.
- No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
