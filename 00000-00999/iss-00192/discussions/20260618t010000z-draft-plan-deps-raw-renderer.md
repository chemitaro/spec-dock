---
created_by_role: implementation-planner
scope_id: iss-00192
source_paths:
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/discussions/20260618t002930z-deps-raw-flat-visual-simulation.puml
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/discussions/20260618t004200z-draft-design-deps-raw-renderer.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/markdown.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - src/spec_dock/assets/spec_dock/.gitignore
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00192-generate-deps-raw-puml/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Delegated Implementation Planning Draft: deps-raw renderer

This file is delegated planning evidence only for `iss-00192 Generate Raw Dependency View`. It is intended as input for canonical `plan.md` authoring by the main orchestrator. It does not edit, approve, or replace canonical `requirement.md`, `design.md`, `plan.md`, or `report.md`.

Source revisions used:

- `requirement.md`: frontmatter `ID: "iss-00192"`, `状態: "draft"`, `最終更新: "2026-06-18"`.
- `design.md`: frontmatter `ID: "iss-00192"`, `状態: "draft"`, `最終更新: "2026-06-18"`.
- `report.md`: records requirement reviewer pass by agent `019ed863-7a20-7303-8ed1-001963199fff` and design reviewer pass by agent `019ed865-8328-7a82-8595-5e6a168fcc5a`; this draft only uses those report entries as source evidence and does not claim a new reviewer pass.
- Design reviewer P2 coverage to carry into plan: include initiative-involved mixed edge verification such as `initiative->issue` or `issue->initiative`.

## 1. Plan Summary

The implementation should add `spec-dock/deps-raw.puml` as an additive generated sync artifact. The plan should proceed from lower-level contract propagation to renderer behavior, then artifact writing/discovery, then disabled/stale behavior and regression preservation.

Primary behavior:

- `sync` writes `spec-dock/deps-raw.puml`.
- The artifact renders raw direct dependencies from `.meta.json.depends_on`, not issue-level effective dependencies.
- The view is a dependency-focused subset: direct dependency participants plus ancestor initiative / epic packages.
- Initiative and epic participants render as package endpoints; issue participants render as rectangles inside packages.
- Edges render in human-facing blocks direction as `prerequisite --> dependent : blocks`.
- Dashboard and sync output expose the new artifact.
- Generated artifact ignore rules cover `deps-raw.puml`.
- `sync --force` after deps preflight failure overwrites `deps-raw.puml` with disabled content rather than leaving stale content.

Planned implementation shape:

1. Extend sync contracts and raw map propagation.
2. Add the valid renderer and dependency-focused subset builder.
3. Add writer, dashboard, sync output, and ignore integration.
4. Add disabled artifact behavior for forced deps preflight failure.
5. Preserve existing `deps-issues` and readiness semantics through explicit regression checks.
6. Resolve docs impact in S90.
7. Run S99 final QA, code, and spec gates.

## 2. Requirement / Design Traceability

### Requirement coverage

| Requirement | Closure id | Owner step | Planned coverage |
|---|---|---|---|
| AC-001 generate `spec-dock/deps-raw.puml` during `sync` and expose discovery | `cl-001` | S03 | Runtime sync fixture asserts file existence; dashboard and sync output include `spec-dock/deps-raw.puml`. |
| AC-002 issue->issue raw direct dependency shows participants, ancestors, and `blocks` direction | `cl-002` | S02 | Renderer test verifies issue rectangles, ancestor packages, and `prerequisite --> dependent : blocks`. |
| AC-003 epic->epic or initiative->initiative direct dependency is visually distinguishable from issue-level edges | `cl-003` | S02 | Renderer test verifies package endpoints and nested package structure for parent-level edges. |
| AC-004 epic->issue or issue->epic mixed direct dependency is visually distinguishable | `cl-004` | S02 | Renderer test verifies package endpoint plus rectangle endpoint and nesting. |
| Design reviewer P2: initiative-involved mixed edge such as initiative->issue or issue->initiative | `cl-005` | S02 | Add explicit renderer test for one initiative-involved mixed edge pattern. |
| AC-005 existing `deps-issues.puml` / `.agent/deps-issues.json` semantics are unchanged | `cl-006` | S05 | Existing regression suite plus a focused characterization test for representative fixture output. |
| AC-006 forced deps preflight failure writes disabled `deps-raw.puml` | `cl-007` | S04 | Disabled renderer and `sync --force` test assert stale graph is replaced with disabled note. |
| AC-007 `deps-raw.puml` is ignored as generated artifact | `cl-008` | S03 | Scaffold `.gitignore` assertion and, where existing style supports it, `git check-ignore` in temp repo. |
| EC-001 parent participant without descendant issues still renders | `cl-009` | S02 | Renderer subset test uses epic or initiative participant with no descendant issue expansion. |
| EC-002 nonparticipants are omitted, ancestors retained | `cl-010` | S02 | Renderer subset test asserts sibling issue / epic text is absent while ancestor package is present. |
| EC-003 done / closed direct dependency participant is included | `cl-011` | S02 | Renderer test includes done / closed issue participant and asserts inclusion. |
| EC-004 zero direct dependencies generate valid PlantUML note | `cl-012` | S02/S03 | Renderer test covers valid no-edge note; sync test confirms file exists. |

### Design dependency traceability

| Design element | Plan response |
|---|---|
| `SyncStateResult.raw_node_depends_on_map` | S01 adds contract field and population from `load_node_dependency_resolutions()`. |
| `DepsRawArtifact` and `ArtifactBundle.deps_raw` | S01 adds presentation contract; S03 integrates writer and path result. |
| `render_deps_raw_artifact()` and `render_deps_raw_puml()` | S02 owns valid payload and PlantUML behavior. |
| Disabled renderer | S04 owns forced preflight failure behavior and disabled output. |
| Dashboard / CLI discovery | S03 owns normal discovery; S04 owns disabled discovery confirmation. |
| `.gitignore` generated artifact entry | S03 owns shipped scaffold ignore update and tests. |
| No `deps check`, `deps add/remove`, `deps-issues`, or raw JSON semantic changes | S05 regression gate owns explicit preservation. |

## 3. Milestones

### M1 Contract and renderer vertical tracer

Goal: establish the raw dependency contract boundary and prove a minimal raw edge can render from sync state without using `deps-issues`.

Steps: S01, first S02 acceptance case.

Exit: `SyncStateResult` carries raw direct dependencies and the renderer can emit a valid dependency-focused PlantUML source for issue->issue.

### M2 Sync artifact integration

Goal: include `deps-raw.puml` in the shipped sync artifact pipeline and human discovery surfaces.

Steps: remaining S02 cases, S03.

Exit: hermetic sync runtime test writes `spec-dock/deps-raw.puml`; dashboard, sync output, and gitignore contract are covered.

### M3 Failure mode and compatibility hardening

Goal: handle forced deps failure without stale output and prove existing effective dependency artifacts remain stable.

Steps: S04, S05.

Exit: disabled output is covered; `deps-issues` regressions are unchanged.

### M4 Docs, final review, and delivery gates

Goal: resolve docs impact and complete final QA / code / spec review obligations.

Steps: S90, S99.

Exit: final report ledgers, reviewers, commits, sync/validate, and PR/merge preparation evidence are complete per `workflow_issue.md`.

## 4. Dependency-Derived Execution Order

The execution order follows `design.md` dependency analysis:

1. `infra/deps_reader.load_node_dependency_resolutions()` already resolves raw node dependencies; the missing boundary is `application.sync_state` retaining that map. Therefore S01 comes first.
2. `presentation.json_state` and `presentation.puml` cannot render a raw view until S01 has a stable contract. Therefore S02 depends on S01.
3. `infra.artifact_writer`, `presentation.markdown`, and `presentation.cli_text` need a `DepsRawArtifact` before adding root output and discovery. Therefore S03 depends on S01 and S02.
4. Disabled output needs the same artifact bundle path as normal output, plus preflight failure handling. Therefore S04 depends on S03 and reuses S02 renderer patterns.
5. Compatibility checks must run after the new artifact has been integrated, because accidental regressions can come from contract field changes and shared renderer helper extraction. Therefore S05 depends on S01-S04.
6. Docs impact can be finalized after implementation surface is known. Therefore S90 follows S05.
7. Final quality gate depends on all implementation, docs, step reviews, report updates, and commits. Therefore S99 is last.

## 5. Issue / Step Slicing

### Step list and AC / EC mapping

| Step | Behavior slice | Depends on | Unblocks | Main target files | AC / EC / closure ids |
|---|---|---|---|---|---|
| S01 | Raw direct dependency contract propagation | approved requirement/design/plan | S02, S03, S04 | `application/contracts.py`, `application/sync_state.py`, `presentation/contracts.py`, affected constructor fixtures | `cl-001`, support for `cl-002`..`cl-012` |
| S02 | Valid `deps-raw.puml` dependency-focused renderer | S01 | S03, S04 | `presentation/json_state.py`, `presentation/puml.py`, focused presentation tests | `cl-002`, `cl-003`, `cl-004`, `cl-005`, `cl-009`, `cl-010`, `cl-011`, `cl-012` |
| S03 | Normal sync artifact write, discovery, and ignore integration | S01, S02 | S04, S05 | `infra/artifact_writer.py`, `application/contracts.py`, `presentation/markdown.py`, `presentation/cli_text.py`, `src/spec_dock/assets/spec_dock/.gitignore`, runtime tests | `cl-001`, `cl-008`, `cl-012` |
| S04 | Forced deps failure disabled artifact behavior | S03 | S05 | `presentation/puml.py`, `presentation/json_state.py`, `application/sync_state.py`, `infra/artifact_writer.py`, CLI runtime tests | `cl-007` |
| S05 | Existing dependency artifact and readiness regression preservation | S01-S04 | S90, S99 | existing deps tests and any constructor fixture updates | `cl-006` |
| S90 | Docs impact resolution / docs refresh | S01-S05 | S99 | likely `src/spec_dock/assets/spec_dock/docs/reference_sync.md`, possibly `reference_deps.md`; report evidence | docs closure |
| S99 | Final quality gate | S01-S90 complete | final exit | report evidence and final checks | all closure ids |

## 6. Test Strategy Mapping

### Risk-calibrated obligations

- Contract field additions have medium regression risk because many tests may instantiate `SyncStateResult`, `ArtifactBundle`, or `ArtifactWriteResult`. Use focused unit tests and update constructor fixtures mechanically.
- Renderer behavior has high specification risk because it defines the observable artifact. Use text-level PlantUML tests for every AC / EC pattern, including the design reviewer P2 initiative-involved mixed edge.
- Sync writer and discovery have medium integration risk. Use hermetic runtime tests rather than manual inspection only.
- Disabled behavior has high stale-artifact risk. Use a forced preflight failure test that can distinguish old valid graph text from disabled replacement text.
- Compatibility has high product risk because `deps-issues` is an existing readiness-adjacent view. Run existing deps/sync presentation tests plus focused unchanged-semantics characterization.
- Docs impact should not rely on code tests alone because sync artifact inventory is user-facing. S90 must include docs inspection and spec review evidence.

### Planned commands

The canonical plan should name narrow checks first, then broaden:

- `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py`
- `uv run pytest tests/cli_runtime/test_sync.py`
- `uv run pytest tests/cli_runtime/test_deps.py`
- `uv run pytest tests/unit/infra/test_init_update.py`
- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`

If implementation touches only a subset, the executor may start with even narrower node-selected tests, but S99 should run a broad enough lane to cover runtime and scaffold behavior.

## 7. Review Gates

Per `workflow_issue.md`, final implementation should use delegated worker / reviewer gates; this draft only describes the planned gates.

| Gate | Applies to | Reviewer focus | Pass condition |
|---|---|---|---|
| Step code review | S01-S05 | `code-reviewer` | Step diff matches allowed files, closure ids, tests, and no unrelated refactor. |
| Step docs/spec review | S90 | `spec-reviewer` | Docs impact is either updated or recorded as justified no-op; docs align with requirement/design/plan. |
| Step commit gate | S01-S05, S90 | step reviewer + orchestrator | One implementation step equals one review scope equals one commit, or valid approved-no-op evidence. |
| Final QA gate | S99 | `qa-reviewer` | Test obligation coverage is sufficient; additional integration test need is resolved. |
| Final code review gate | S99 | issue-wide `code-reviewer` | Integrated diff preserves architecture, contracts, compatibility, and maintainability. |
| Final spec review gate | S99 | `spec-reviewer` | Requirement, design, plan, report, implementation, tests, and docs are aligned. |

Delegated worker output is not a reviewer substitute. Any `failed`, `unavailable`, `denied`, `waived`, or `provisional` reviewer state remains incomplete unless handled through the workflow.

## 8. Rollback / Compatibility

Rollback plan:

- Remove `raw_node_depends_on_map` from `SyncStateResult` and any fixture updates.
- Remove `DepsRawArtifact`, `ArtifactBundle.deps_raw`, and `ArtifactWriteResult.deps_raw_puml_path`.
- Remove `render_deps_raw_artifact()`, `render_deps_raw_puml()`, and disabled renderer additions.
- Remove writer output for `spec-dock/deps-raw.puml`.
- Remove dashboard / sync output discovery entries.
- Remove `.gitignore` entry and tests introduced for the generated artifact.
- Leave user-generated or stale ignored `spec-dock/deps-raw.puml` as disposable generated output; it is not a source of truth.

Compatibility guardrails:

- Do not change `deps check` readiness semantics.
- Do not change `deps add/remove` mutation contract.
- Do not add `.agent/deps-raw.json`.
- Do not change existing `.agent/deps-issues.json` or `deps-issues.puml` meaning.
- Do not read `.meta.json` in presentation layer; application/infra owns dependency resolution.

## 9. Docs Impact

Docs impact is not `none` by default because this issue adds a new generated sync artifact and a new dependency visualization surface.

S90 should inspect at least:

- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- any generated artifact list in shipped templates or README-like docs, if referenced by existing tests
- dogfooding `spec-dock/docs/...` only as validation output after provider-side changes, not as implementation source of truth

Expected resolution:

- Update shipped `reference_sync.md` if it enumerates sync outputs, adding `spec-dock/deps-raw.puml` as a human-facing raw direct dependency view.
- Update shipped `reference_deps.md` only if needed to clarify that `deps-raw.puml` visualizes raw direct `.meta.json.depends_on` and is not a readiness source.
- Record docs update or justified no-op in `report.md` Docs Impact Resolution.
- Run docs/spec alignment review through `spec-reviewer`.

## 10. Final Quality Gate

S99 must be independent of step reviews. It should not substitute for any per-step reviewer gate.

Required final checks:

- `qa-reviewer`: confirms closure ids `cl-001`..`cl-012` have sufficient test evidence and decides whether an additional integration test is required.
- issue-wide `code-reviewer`: reviews the full integrated diff across application, presentation, infra, tests, docs, and scaffold assets.
- `spec-reviewer`: verifies requirement/design/plan/report/implementation/tests/docs alignment and confirms S90 docs impact is resolved.
- `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` or their canonical project-equivalent checks are recorded where workflow requires.
- PR Delivery Gate and Merge Preparation Gate evidence are recorded before `issue finish`, per `workflow_issue.md`.

Final gate failure handling:

- Any final reviewer `fail` requires a bounded follow-up fix and fresh re-review.
- Any `unavailable`, `denied`, `waived`, or `provisional` final reviewer state is not a pass.
- Any unresolved `Status=open` report decision entry blocks completion.

## 11. Plan Blockers

No design blocker found.

Known non-blocking plan coverage item:

- The design reviewer P2 asks for initiative-involved mixed edge coverage. This draft covers it through `cl-005`, S02 closure, and `tc-s02-004`.

Potential amendment triggers:

- If PlantUML package endpoint edges cannot be represented without hidden anchors in the project-supported PlantUML version, return to design before implementation continues.
- If the implementation must add raw dependency JSON, return to requirement/design because raw JSON is explicitly out of scope.
- If presentation needs to read `.meta.json` directly, return to design because this violates the accepted layer boundary.
- If docs impact requires broad workflow/skill text changes beyond sync/deps references, handle through S90 and consider plan amendment if the scope becomes material.

## 12. Integration Notes for Main Orchestrator

Suggested canonical `plan.md` adoption shape:

1. Keep this draft as evidence only and rewrite the selected plan into canonical `plan.md`.
2. Add this discussion file to `report.md` Delegated Draft Evidence and Evidence Adoption Ledger if adopted.
3. Run a fresh `spec-reviewer` on canonical `plan.md`; do not treat this draft as reviewer pass.
4. Preserve one-step-at-a-time execution, step review, step commit, S90, and S99 gates from `workflow_issue.md`.

Leaf evidence used:

- No additional depth=2 leaf agent was called by this implementation-planner draft.
- Evidence came from canonical issue docs, prior discussion artifacts, report ledger entries, workflow docs, and read-only runtime source inspection.

Forbidden actions avoided:

- No canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edit.
- No implementation, test, package/config, workflow, GitHub state, or secret edit.
- No phase promotion, reviewer-pass claim, implementation-readiness claim, issue ready/finish claim, git add, git commit, or git push.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

## Spec-Locked Closure Index

| ID | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure owner step |
|---|---|---|---|---|---|---|---|
| `cl-001` | AC-001, design artifact pipeline | `sync` generates `spec-dock/deps-raw.puml` and exposes it in dashboard and sync output | temp repo with valid raw dependency, run sync | artifact omitted or undiscoverable | yes | red-required | S03 |
| `cl-002` | AC-002 | issue->issue direct dependency renders participants, ancestor packages, and `blocks` direction | raw map `dependent issue -> prerequisite issue` | raw view collapses to issue-only graph without hierarchy | yes | red-required | S02 |
| `cl-003` | AC-003 | parent-level epic->epic or initiative->initiative dependency renders as package endpoint dependency | raw parent node dependency | parent-level intent hidden as issue-level edge | yes | red-required | S02 |
| `cl-004` | AC-004 | epic->issue or issue->epic mixed dependency renders package endpoint / rectangle endpoint with nesting | mixed parent/issue raw dependency | mixed node-kind dependency indistinguishable from issue->issue | yes | red-required | S02 |
| `cl-005` | design reviewer P2 | initiative-involved mixed edge, such as initiative->issue or issue->initiative, is covered | raw dependency crossing initiative package endpoint and issue rectangle | plan misses initiative-involved mixed edge regression | yes | red-required | S02 |
| `cl-006` | AC-005, design compatibility | existing `deps-issues.puml` and `.agent/deps-issues.json` semantics remain unchanged | representative existing deps fixture | raw view accidentally changes readiness/effective graph | yes | covered-existing plus focused regression | S05 |
| `cl-007` | AC-006 | forced deps preflight failure writes disabled `deps-raw.puml`, not stale graph | invalid deps tree with `sync --force` | stale artifact after failure | yes | red-required | S04 |
| `cl-008` | AC-007 | shipped scaffold ignores generated `spec-dock/deps-raw.puml` | installed temp repo `.gitignore` / `git check-ignore` | generated artifact appears as source change | yes | red-required or inspect assertion | S03 |
| `cl-009` | EC-001 | parent participant with no descendant issues still renders as raw participant | epic or initiative dependency with no issue expansion | empty parent package dropped | yes | red-required | S02 |
| `cl-010` | EC-002 | nonparticipant siblings are omitted; participant ancestors remain | tree with unrelated sibling issue / epic | full-tree leak into dependency-focused subset | yes | red-required | S02 |
| `cl-011` | EC-003 | done / closed participant is included in raw view | done / closed issue with direct raw dependency | raw view incorrectly filters by todo status | yes | red-required | S02 |
| `cl-012` | EC-004 | zero raw dependencies still generate valid PlantUML with no-dependencies note | valid tree with no `.meta.json.depends_on` edges | empty file, skipped file, or stale graph | yes | red-required | S02/S03 |

## Executable Behavior-Slice Steps

### S01 Raw Direct Dependency Contract Propagation

#### Behavior goal

Expose resolved raw direct dependencies from application sync state without changing readiness or `deps-issues` behavior.

#### Planned contract

- Scope:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py`
  - tests that instantiate these contracts
- Test obligation:
  - Verify `SyncStateResult.raw_node_depends_on_map` is populated from `load_node_dependency_resolutions()`.
  - Verify forced preflight failure leaves the raw map empty and records deps disabled state for later disabled rendering.
  - Verify no existing readiness calculation consumes the raw map.
- Red or alternative evidence requirement:
  - `red-required` for raw map population.
  - `covered-existing` for readiness behavior until S05, with targeted regression in S05.
- Green verification:
  - focused unit/application or presentation sync test for raw map population.
  - existing constructor fixture tests updated without broad refactor.
- Refactor guardrail:
  - Do not move dependency validation ownership.
  - Do not introduce raw JSON artifact contracts.
- Amendment trigger:
  - Any need to read `.meta.json` in presentation or add `.agent/deps-raw.json`.

#### Delegation contract

- Delegated role: `dev-coder`.
- Input docs: `requirement.md`, `design.md`, this canonical plan once adopted, `workflow_issue.md`, `application/contracts.py`, `application/sync_state.py`, `presentation/contracts.py`.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py`
  - minimal affected tests / fixtures
- Forbidden changes:
  - `deps check`, `deps add/remove`, `.meta.json` storage, raw JSON artifact addition, unrelated constructor refactors.
- Acceptance criteria:
  - `raw_node_depends_on_map` carries direct dependency node ids keyed by dependent node id.
  - Existing `issue_depends_on_map` and `deps_eval_by_id` remain the readiness path.
- Required tests or docs-only verification:
  - Focused red/green test for raw map propagation.
  - Existing affected contract tests updated and passing.
- Reviewer focus:
  - `code-reviewer` verifies contract boundary, no readiness semantic change, and narrow fixture updates.
- Stop conditions:
  - raw map cannot be populated without changing `deps_reader` semantics; presentation layer filesystem read appears necessary; test fixture churn becomes broad enough to indicate step split.
- Output required:
  - changed files, test command/result, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`

#### Concrete Test Cases

- `tc-s01-001` acceptance: sync state carries raw direct dependencies
  - Premise: temp graph has an issue node whose `.meta.json.depends_on` points to another issue, and deps preflight is valid.
  - Operation: collect sync state through the existing application sync path or its focused test harness.
  - Expected result: `SyncStateResult.raw_node_depends_on_map` contains the dependent issue id mapped to the prerequisite issue id.
  - Failure detection: catches the current behavior where raw dependency resolutions are validated and then discarded.
  - Verification method: focused test in existing sync/application test area.
  - Related closure id: `cl-001`

- `tc-s01-002` regression: raw map does not replace effective dependency map
  - Premise: temp graph has raw parent-level dependency that compiles differently from issue-level effective dependency output.
  - Operation: collect sync state and inspect both `raw_node_depends_on_map` and `issue_depends_on_map`.
  - Expected result: raw map preserves node-level ids while `issue_depends_on_map` remains the existing effective issue dependency structure.
  - Failure detection: catches accidental reuse of raw map as readiness input.
  - Verification method: focused assertion in sync/application test or S05 regression if fixture is easier there.
  - Related closure id: `cl-006`

#### Step closure contract

- `cl-001` support is present at the contract layer.
- `cl-006` support is not violated by the contract addition.
- Report records Red/Green evidence, constructor fixture updates, and no material implementation decisions unless a ledger note is needed.

#### Step gate

- Step reviewer: `code-reviewer` pass required.
- Commit gate: one S01 commit after reviewer pass and clean status.
- No-op gate: only valid if existing code already carries raw map, which current source inspection says it does not.
- Report update: Implementation Delegation Gate, Test Contract Closure for S01 cases, Step Commit Gate.

### S02 Valid `deps-raw.puml` Renderer and Dependency-Focused Subset

#### Behavior goal

Render valid `deps-raw.puml` PlantUML from raw direct dependency state with dependency-focused hierarchy, node-kind endpoint distinction, deterministic output, and zero-dependency note.

#### Planned contract

- Scope:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - focused presentation tests
- Test obligation:
  - Cover issue->issue, parent-level, mixed parent/issue, initiative-involved mixed edge, nonparticipant omission, done/closed inclusion, empty parent participant, and zero-dependency behavior.
- Red or alternative evidence requirement:
  - `red-required` for all renderer AC/EC cases because the renderer does not exist yet.
- Green verification:
  - Text-level PlantUML tests assert package structure, rectangle structure, edge direction, title/skinparams, and absence of nonparticipants.
- Refactor guardrail:
  - Reuse or minimally extract helpers only where it reduces duplication; do not rewrite existing `deps-issues` renderer.
- Amendment trigger:
  - Package endpoint rendering requires hidden anchors or a visual rule not in design.

#### Delegation contract

- Delegated role: `dev-coder`.
- Input docs: `requirement.md`, `design.md`, visual simulation `.puml`, this canonical plan once adopted, `presentation/json_state.py`, `presentation/puml.py`.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - focused presentation tests
- Forbidden changes:
  - full-tree rendering, hidden anchor node design without plan amendment, raw JSON output, changing `deps-issues` output except tiny shared helper extraction guarded by S05.
- Acceptance criteria:
  - Valid PlantUML text matches canonical visual rules: `@startuml`, `left to right direction`, `skinparam shadowing false`, `skinparam linetype ortho`, `skinparam packageStyle rectangle`, white packages, issue state rectangles, `blocks` edges.
- Required tests:
  - All concrete test cases below.
- Reviewer focus:
  - `code-reviewer` verifies renderer correctness, deterministic sorting, escaping, and separation from `deps-issues`.
- Stop conditions:
  - PlantUML syntax cannot express accepted endpoint design; status color mapping conflicts with current issue status contract; renderer requires broad tree model redesign.
- Output required:
  - changed files, test command/result, before/after sample snippets if useful, unresolved risks, and ledger note.

#### Concrete Test Cases

- `tc-s02-001` acceptance: issue->issue edge with ancestors
  - Premise: raw map has `iss-b` depending on `iss-a` under the same or different epic, both with ancestor packages.
  - Operation: render `deps-raw.puml`.
  - Expected result: output includes ancestor initiative/epic packages, issue rectangles for both issues, and edge `iss-a alias --> iss-b alias : blocks`.
  - Failure detection: catches missing hierarchy or reversed edge direction.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-002`

- `tc-s02-002` acceptance: parent-level package endpoint edge
  - Premise: raw map has `epic-b` depending on `epic-a`, or `init-b` depending on `init-a`.
  - Operation: render `deps-raw.puml`.
  - Expected result: output includes package aliases for parent nodes and a `blocks` edge between package endpoints without expanding to issue-only edges.
  - Failure detection: catches accidental issue-level compilation or parent package omission.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-003`

- `tc-s02-003` acceptance: epic->issue or issue->epic mixed edge
  - Premise: raw map includes `iss-x depends_on epic-y` or `epic-y depends_on iss-x`.
  - Operation: render `deps-raw.puml`.
  - Expected result: output includes one package endpoint and one issue rectangle endpoint with nested package context.
  - Failure detection: catches mixed dependency rendered as two issue rectangles or lost endpoint kind.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-004`

- `tc-s02-004` reviewer P2: initiative-involved mixed edge
  - Premise: raw map includes `iss-x depends_on init-y` or `init-y depends_on iss-x`.
  - Operation: render `deps-raw.puml`.
  - Expected result: output includes initiative package endpoint and issue rectangle endpoint, with edge direction preserving `blocks` semantics.
  - Failure detection: specifically catches the design reviewer P2 gap where initiative-involved mixed edges were not planned.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-005`

- `tc-s02-005` edge case: nonparticipants omitted and ancestors retained
  - Premise: tree contains participant issue, unrelated sibling issue, and ancestor initiative/epic packages.
  - Operation: render `deps-raw.puml`.
  - Expected result: participant and ancestors are present; unrelated sibling issue and unrelated sibling epic are absent.
  - Failure detection: catches full-tree leakage into dependency-focused subset.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-010`

- `tc-s02-006` edge case: parent participant without descendant issue expansion
  - Premise: raw dependency participant is an epic or initiative with no descendant issue included as direct participant.
  - Operation: render `deps-raw.puml`.
  - Expected result: package endpoint is present and usable in edge even without descendant issue rectangles.
  - Failure detection: catches empty package removal that loses raw intent.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-009`

- `tc-s02-007` edge case: done / closed participant included
  - Premise: closed or done issue participates in raw direct dependency.
  - Operation: render `deps-raw.puml`.
  - Expected result: issue appears in raw view with done/closed-equivalent state color or non-ready state representation, not filtered by todo projection.
  - Failure detection: catches accidental reuse of todo-only index filtering.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-011`

- `tc-s02-008` edge case: zero raw direct dependencies
  - Premise: valid tree has no `.meta.json.depends_on` direct edges.
  - Operation: render `deps-raw.puml`.
  - Expected result: output is valid PlantUML with title, skinparams, note indicating no raw direct dependencies, and `@enduml`.
  - Failure detection: catches skipped artifact, empty output, or stale graph risk.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-012`

#### Step closure contract

- `cl-002`, `cl-003`, `cl-004`, `cl-005`, `cl-009`, `cl-010`, `cl-011`, and renderer half of `cl-012` have passing evidence.
- Renderer output remains text-contract based; rendered bitmap inspection is optional manual evidence, not mandatory automatic verification.
- Report records any helper extraction and confirms `deps-issues` renderer was not semantically changed.

#### Step gate

- Step reviewer: `code-reviewer` pass required.
- Commit gate: one S02 commit after reviewer pass and clean status.
- No-op gate: invalid because renderer does not exist.
- Report update: Step Contract Closure and Test Contract Closure for all S02 closure ids.

### S03 Normal Sync Artifact Write, Discovery, and Ignore Integration

#### Behavior goal

Write `spec-dock/deps-raw.puml` during normal sync and make it discoverable in dashboard and sync output while marking it as generated.

#### Planned contract

- Scope:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/markdown.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `src/spec_dock/assets/spec_dock/.gitignore`
  - runtime / infra tests
- Test obligation:
  - Sync writes file.
  - `ArtifactWriteResult.deps_raw_puml_path` is returned.
  - dashboard normal Observability includes path.
  - `render_sync_text()` includes path in `wrote=`.
  - shipped `.gitignore` ignores `deps-raw.puml`.
- Red or alternative evidence requirement:
  - `red-required` for file write and discovery.
  - `inspect assertion` acceptable for `.gitignore` content if existing test style does not use `git check-ignore`.
- Green verification:
  - CLI runtime sync test and presentation/infra unit tests.
- Refactor guardrail:
  - Do not alter existing artifact path order except appending new path in a predictable place.
- Amendment trigger:
  - If writer requires atomic transaction redesign; if generated artifact should live outside root `spec-dock/`.

#### Delegation contract

- Delegated role: `dev-coder`.
- Input docs: `requirement.md`, `design.md`, this canonical plan once adopted, `artifact_writer.py`, `markdown.py`, `cli_text.py`, `.gitignore`, existing sync tests.
- Allowed paths:
  - files listed in planned contract plus focused tests.
- Forbidden changes:
  - generated dogfooding artifact edits, global gitignore policy changes, unrelated dashboard redesign.
- Acceptance criteria:
  - `sync` writes and reports `spec-dock/deps-raw.puml`; dashboard reports raw deps view; `.gitignore` marks it generated.
- Required tests:
  - Concrete tests below.
- Reviewer focus:
  - `code-reviewer` verifies artifact pipeline integration and scaffold source-of-truth discipline.
- Stop conditions:
  - Integration requires editing dogfooding `spec-dock/` generated artifacts directly; `.gitignore` update conflicts with scaffold update tests.
- Output required:
  - changed files, test command/result, generated artifact path evidence, ledger note.

#### Concrete Test Cases

- `tc-s03-001` acceptance: sync writes deps-raw artifact
  - Premise: temp initialized repo has valid direct raw dependency and normal deps preflight.
  - Operation: run the existing hermetic sync command/test harness.
  - Expected result: `spec-dock/deps-raw.puml` exists and contains valid renderer output.
  - Failure detection: catches missing writer integration despite renderer success.
  - Verification method: `tests/cli_runtime/test_sync.py` or existing runtime sync fixture.
  - Related closure id: `cl-001`

- `tc-s03-002` discovery: dashboard and sync output include raw path
  - Premise: normal sync succeeds in temp repo.
  - Operation: inspect `spec-dock/dashboard.md` and `render_sync_text()` or command stdout.
  - Expected result: both include `spec-dock/deps-raw.puml`.
  - Failure detection: catches artifact created but undiscoverable to users/agents.
  - Verification method: presentation unit test plus runtime sync assertion.
  - Related closure id: `cl-001`

- `tc-s03-003` generated artifact ignore
  - Premise: temp initialized repo includes shipped `spec-dock/.gitignore`.
  - Operation: inspect `.gitignore` and, if existing test style supports it, run `git check-ignore spec-dock/deps-raw.puml`.
  - Expected result: `deps-raw.puml` is ignored as generated artifact.
  - Failure detection: catches generated file appearing as source change.
  - Verification method: `tests/cli_runtime/test_sync.py` gitignore tests or `tests/unit/infra/test_init_update.py`.
  - Related closure id: `cl-008`

- `tc-s03-004` edge case: zero dependency sync still writes file
  - Premise: valid temp repo has no direct raw dependencies.
  - Operation: run sync.
  - Expected result: `spec-dock/deps-raw.puml` exists and contains no-dependencies note.
  - Failure detection: catches file skipped when edge list is empty.
  - Verification method: CLI runtime sync test.
  - Related closure id: `cl-012`

#### Step closure contract

- `cl-001`, `cl-008`, and sync half of `cl-012` pass.
- Report records artifact write evidence, dashboard/stdout discovery evidence, and ignore evidence.

#### Step gate

- Step reviewer: `code-reviewer` pass required.
- Commit gate: one S03 commit after reviewer pass and clean status.
- No-op gate: invalid because writer/discovery/ignore do not exist.
- Report update: Step Contract Closure, Test Contract Closure, Step Commit Gate.

### S04 Forced Deps Failure Disabled Artifact Behavior

#### Behavior goal

When `sync --force` permits deps preflight failure, write disabled `deps-raw.puml` content so stale valid graph content is not left behind.

#### Planned contract

- Scope:
  - `presentation/puml.py`
  - `presentation/json_state.py`
  - `application/sync_state.py` only if bundle construction needs explicit disabled artifact handling
  - `infra/artifact_writer.py` only if writer integration from S03 needs adjustment
  - CLI runtime tests
- Test obligation:
  - Disabled renderer includes `deps_preflight_failed`, `deps.valid=false`, `mode=sync --force`, and sanitized error text.
  - Forced sync overwrites previous valid `deps-raw.puml` with disabled content.
- Red or alternative evidence requirement:
  - `red-required`, because stale artifact behavior is user-facing and explicitly required.
- Green verification:
  - focused disabled renderer unit test and forced sync runtime test.
- Refactor guardrail:
  - Align disabled style with existing disabled tree/deps-issues renderers; no new failure framework.
- Amendment trigger:
  - If existing sync force path cannot build a bundle without broader error-handling changes.

#### Delegation contract

- Delegated role: `dev-coder`.
- Input docs: AC-006, design disabled output contract, existing disabled renderers in `puml.py`, `workflow_issue.md`.
- Allowed paths:
  - files listed in planned contract plus focused tests.
- Forbidden changes:
  - changing preflight validation rules, making forced sync successful without disabled warning, swallowing errors outside existing force behavior.
- Acceptance criteria:
  - Forced failure output is disabled PlantUML, not skipped and not stale.
- Required tests:
  - Concrete tests below.
- Reviewer focus:
  - `code-reviewer` checks stale-artifact prevention, error sanitization, and no validation semantics change.
- Stop conditions:
  - Cannot create a forced preflight failure fixture hermetically; disabled behavior requires changing validation contract.
- Output required:
  - changed files, test command/result, stale prevention evidence, ledger note.

#### Concrete Test Cases

- `tc-s04-001` acceptance: disabled renderer includes failure note
  - Premise: renderer receives `deps_preflight_error="..."`.
  - Operation: render disabled `deps-raw.puml`.
  - Expected result: output includes `title deps-raw - DEPS_DISABLED`, `deps_preflight_failed`, `deps.valid=false`, `mode=sync --force`, sanitized error, and `@enduml`.
  - Failure detection: catches missing disabled diagnostic content.
  - Verification method: presentation renderer unit test.
  - Related closure id: `cl-007`

- `tc-s04-002` acceptance: forced sync overwrites stale valid graph
  - Premise: temp repo has an existing valid `spec-dock/deps-raw.puml`, then metadata is changed to trigger deps preflight failure.
  - Operation: run `sync --force`.
  - Expected result: `spec-dock/deps-raw.puml` is overwritten with disabled content and no previous edge text remains.
  - Failure detection: catches stale artifact left after forced failure.
  - Verification method: CLI runtime sync failure fixture.
  - Related closure id: `cl-007`

#### Step closure contract

- `cl-007` passes at renderer and runtime levels.
- Report records pre-existing valid content setup, forced failure command/result, and disabled replacement evidence.

#### Step gate

- Step reviewer: `code-reviewer` pass required.
- Commit gate: one S04 commit after reviewer pass and clean status.
- No-op gate: invalid because disabled raw artifact behavior does not exist.
- Report update: Step Contract Closure, Test Contract Closure, Step Commit Gate.

### S05 Existing Dependency Artifact and Readiness Regression Preservation

#### Behavior goal

Prove the new raw dependency view does not change existing effective dependency artifacts, readiness behavior, mutation contract, or generated JSON semantics.

#### Planned contract

- Scope:
  - tests and any minimal fixture updates caused by contract field additions
  - no product code unless a regression is found from S01-S04
- Test obligation:
  - Existing `deps-issues.puml` / `.agent/deps-issues.json` tests pass.
  - Existing `deps check`, `deps add/remove`, and sync readiness tests pass where relevant.
  - Focused characterization confirms `render_deps_issues_artifact()` remains issue-only effective graph.
- Red or alternative evidence requirement:
  - `covered-existing` plus focused regression assertion.
- Green verification:
  - targeted existing tests and broader runtime/presentation lane.
- Refactor guardrail:
  - Do not use S05 to add new features; it is a compatibility gate.
- Amendment trigger:
  - Any existing semantics change requires plan amendment or rollback of offending step.

#### Delegation contract

- Delegated role: `dev-coder` for test repair if needed; otherwise orchestrator records approved-no-op after evidence.
- Input docs: AC-005, design compatibility/rollback sections, existing tests.
- Allowed paths:
  - focused tests / fixture updates only unless a real regression points to S01-S04 code.
- Forbidden changes:
  - rewriting dependency semantics to make tests pass, broad snapshot churn without explanation, changing `deps check` expected behavior.
- Acceptance criteria:
  - AC-005 and `cl-006` closed with evidence.
- Required tests:
  - Concrete tests below.
- Reviewer focus:
  - `code-reviewer` checks compatibility evidence and any fixture updates are mechanical.
- Stop conditions:
  - Existing tests fail due to semantic drift; broad fixture churn suggests raw view changed existing artifacts.
- Output required:
  - commands/results, changed files if any, no-op or fix evidence, ledger note.

#### Concrete Test Cases

- `tc-s05-001` regression: existing deps-issues JSON and PUML remain issue-only
  - Premise: representative fixture has raw parent-level dependencies and issue-level effective dependencies.
  - Operation: render or run sync and inspect `.agent/deps-issues.json` plus `deps-issues.puml`.
  - Expected result: output remains the existing todo issue-only effective graph and does not include raw parent packages from `deps-raw`.
  - Failure detection: catches raw map leaking into existing deps-issues artifacts.
  - Verification method: existing `test_deps` / `test_sync` assertions plus focused characterization if needed.
  - Related closure id: `cl-006`

- `tc-s05-002` regression: dependency mutation and readiness commands still pass
  - Premise: existing tests cover `deps add/remove`, `deps check`, and sync readiness.
  - Operation: run targeted existing regression lane.
  - Expected result: no behavior changes except constructor/wrote-output additions explicitly expected by new artifact tests.
  - Failure detection: catches readiness or mutation contract drift.
  - Verification method: `uv run pytest tests/cli_runtime/test_deps.py` and relevant sync tests.
  - Related closure id: `cl-006`

#### Step closure contract

- `cl-006` passes or issue is blocked/incomplete with exact failing command and likely cause.
- Report records whether S05 was a no-op evidence gate or required bounded fixes.

#### Step gate

- Step reviewer: `code-reviewer` pass required for any changes; if no changes, approved-no-op evidence and reviewer/read-only confirmation per workflow.
- Commit gate: commit only if changes were made; otherwise approved-no-op evidence.
- Report update: Test Contract Closure, Closure Coverage, Step Commit Gate or approved-no-op rationale.

### S90 Docs Impact Resolution / Docs Refresh

#### Behavior goal

Resolve documentation impact for the new generated sync artifact and raw dependency view.

#### Planned contract

- Scope:
  - likely `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - possibly `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - existing docs/tests that assert shipped docs text if applicable
- Test obligation:
  - Docs inspection or docs diff proves generated artifact inventory and dependency view explanation are aligned.
  - If docs are changed, relevant tests or validation run.
- Red or alternative evidence requirement:
  - `inspect-only` first; `red-required` only if existing docs tests assert artifact inventory.
- Green verification:
  - docs diff inspection, `spec-reviewer` docs/spec alignment, and relevant tests if docs test exists.
- Refactor guardrail:
  - Do not revise workflow policy or skills unless docs inspection finds a direct stale reference that blocks user understanding.
- Amendment trigger:
  - required docs surface expands materially beyond sync/deps references.

#### Delegation contract

- Delegated role: `doc-writer`.
- Input docs: `requirement.md`, `design.md`, S01-S05 observed behavior, `reference_sync.md`, `reference_deps.md`.
- Allowed paths:
  - shipped docs paths identified above and focused docs tests.
- Forbidden changes:
  - canonical issue docs except report evidence by orchestrator, workflow policy rewrites, unrelated wording cleanup.
- Acceptance criteria:
  - Docs either mention `deps-raw.puml` appropriately or report records why no docs update is needed.
- Required tests or docs-only verification:
  - docs diff inspection; relevant pytest if docs are covered by tests; `spec-reviewer` docs/spec alignment.
- Reviewer focus:
  - `spec-reviewer` for docs/spec alignment.
- Stop conditions:
  - docs update would change product contract beyond approved requirement/design.
- Output required:
  - changed docs, verification result, docs impact evidence, ledger note.

#### Concrete Test Cases

- `tc-s90-001` docs impact: sync artifact inventory is not stale
  - Premise: shipped docs that enumerate sync outputs are inspected after implementation.
  - Operation: compare docs against actual normal sync wrote list and dashboard Observability.
  - Expected result: docs mention `spec-dock/deps-raw.puml` or report records non-blocking no-op rationale.
  - Failure detection: catches stale docs that omit the new generated artifact.
  - Verification method: docs diff inspection and relevant docs tests if present.
  - Related closure id: docs impact closure

- `tc-s90-002` docs impact: raw view is not described as readiness source
  - Premise: dependency docs are inspected after implementation.
  - Operation: search for `deps-raw` / `deps-issues` dependency view language.
  - Expected result: docs distinguish raw direct dependency visualization from issue-level effective readiness view.
  - Failure detection: catches misleading docs that could make users treat `deps-raw.puml` as authority.
  - Verification method: docs inspection and `spec-reviewer`.
  - Related closure id: `cl-006`

#### Step closure contract

- S90 docs impact is resolved as updated or approved-no-op.
- `report.md` Docs Impact Resolution records owner, evidence, and spec-reviewer result.

#### Step gate

- Step reviewer: `spec-reviewer` docs/spec alignment pass required.
- Commit gate: one S90 commit if docs changed; approved-no-op evidence if not.
- Report update: Final Quality Gate / Docs Impact Resolution plus Step Commit Gate or approved-no-op.

### S99 Final Quality Gate

#### Behavior goal

Close issue-wide quality gates after all implementation and docs steps are reviewed and committed or approved-no-op.

#### Planned contract

- Scope:
  - no product implementation unless reviewers require bounded fixes
  - `report.md` evidence completion by main orchestrator
- Test obligation:
  - Confirm closure coverage for `cl-001`..`cl-012`.
  - Confirm sync/validate and relevant pytest lanes.
  - Confirm final QA, code, and spec review pass.
- Red or alternative evidence requirement:
  - `covered-existing` plus final reviewer evidence; no new red test unless QA requires one.
- Green verification:
  - final test commands and reviewer pass evidence.
- Refactor guardrail:
  - Do not use final commit to catch up uncommitted implementation step changes.
- Amendment trigger:
  - final reviewer finds missing closure, design mismatch, or docs mismatch outside current plan.

#### Delegation contract

- Delegated role:
  - `qa-reviewer` for test sufficiency.
  - issue-wide `code-reviewer` for integrated diff.
  - `spec-reviewer` for final spec alignment.
- Input docs:
  - requirement/design/plan/report, full diff, test results, docs impact evidence.
- Allowed paths:
  - reviewer output only; bounded follow-up worker paths if a reviewer fails and orchestrator delegates a fix.
- Forbidden changes:
  - final catch-up implementation commit, reviewer pass self-claim, issue finish before delivery evidence.
- Acceptance criteria:
  - all final reviewers pass; report ledgers closed; no open decision entries; clean status after final commit.
- Required tests:
  - final selected commands from Test Strategy Mapping, plus any QA-required integration test.
- Reviewer focus:
  - QA sufficiency, integrated code risk, spec alignment.
- Stop conditions:
  - any final reviewer non-pass; unresolved ledger entry; missing step commit; failing required test.
- Output required:
  - reviewer verdicts, final command results, closure coverage, final commit scope, post-commit external evidence destination.

#### Concrete Test Cases

- `tc-s99-001` final QA coverage
  - Premise: S01-S90 report evidence is complete.
  - Operation: `qa-reviewer` reviews closure ids, tests, and integration need.
  - Expected result: QA passes or identifies bounded missing tests that are added and re-reviewed.
  - Failure detection: catches false completion with insufficient behavior coverage.
  - Verification method: `qa-reviewer` verdict recorded in report.

- `tc-s99-002` final integrated diff review
  - Premise: all step commits are present.
  - Operation: issue-wide `code-reviewer` reviews integrated diff.
  - Expected result: code review passes after any bounded fixes.
  - Failure detection: catches cross-step architecture or compatibility regressions.
  - Verification method: `code-reviewer` verdict recorded in report.

- `tc-s99-003` final spec alignment
  - Premise: implementation, tests, docs, and report are complete.
  - Operation: `spec-reviewer` checks requirement/design/plan/report alignment.
  - Expected result: spec review passes after any bounded fixes.
  - Failure detection: catches unsatisfied AC/EC, docs impact gaps, or stale plan/report evidence.
  - Verification method: `spec-reviewer` verdict recorded in report.

#### Step closure contract

- All required closure ids are passed or valid approved-no-op.
- No final reviewer non-pass remains.
- Final report evidence is complete before final commit.

#### Step gate

- Final QA gate: `qa-reviewer` pass.
- Final code review gate: issue-wide `code-reviewer` pass.
- Final spec review gate: `spec-reviewer` pass.
- Final commit gate: final report ledger / delivery evidence boundary commit only; no implementation catch-up.
- PR / merge preparation gates: required by `workflow_issue.md` before `issue finish`.

## Final Exit Contract

The issue can be reported complete only when the main orchestrator has observed and recorded all of the following in canonical `report.md` or external delivery evidence:

- canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are issue-specific and reviewer-gated as required;
- S01-S05 and S90 are each `committed` or valid `approved-no-op`;
- each implementation step has delegation decision evidence, step reviewer pass, test closure evidence, and step commit/no-op evidence;
- `cl-001`..`cl-012` are covered in Step Contract Closure, Test Contract Closure, and Closure Coverage;
- docs impact is resolved in S90;
- final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` are passed;
- required sync/validate/test commands have pass evidence or a documented non-blocking rationale accepted by the relevant reviewer;
- PR Delivery Gate and Merge Preparation Gate have pass evidence before `issue finish`;
- final commit is made after final report ledger completion, with clean post-commit status recorded as external delivery evidence;
- no unresolved `Status=open`, stale delegated evidence, stale adoption ledger entry, or missing reviewer gate remains.

Risks / questions:

- Risk: PlantUML package endpoint rendering may vary visually by PlantUML version. Mitigation: test source text contract and optionally keep manual render evidence if visual risk resurfaces.
- Risk: `ArtifactWriteResult` and `ArtifactBundle` field additions may require broad fixture updates. Mitigation: keep updates mechanical and review for semantic churn.
- Risk: docs impact may include `reference_sync.md` and `reference_deps.md` even though the design file change plan focuses on runtime files. Mitigation: S90 explicitly resolves docs impact before final quality gate.
- Blockers: no blockers.
