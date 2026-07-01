---
created_by_role: implementation-planner
scope_id: iss-00250
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/discussions/20260630t124012z-disc-system-architect-design-draft.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/discussions/20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_assurance_compose.py
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not-run
---

# Implementation Planner Plan Draft: iss-00250 Profile-Aware Issue Draft Routing

Source requirement / design revisions: `iss-00250` requirement and design, both dated `2026-06-30`; current repository HEAD observed as `c98a47d0`. This draft is proposal evidence only.

Lightweight provenance: created with `./spec-dock/scripts/spec-dock new doc disc --issue iss-00250 --title "Implementation Planner Plan Draft"`. The command printed `path=spec-dock/spec-dock/.../20260630t124640z-disc-implementation-planner-plan-draft.md`, while the actual created file resolved under `spec-dock/initiatives/.../iss-00250.../discussions/20260630t124640z-disc-implementation-planner-plan-draft.md`. This draft edits only that created discussion artifact.

Leaf evidence used: none. Local source reads only. Forbidden actions avoided: no canonical `requirement.md` / `design.md` / `plan.md` / `report.md` edit, no source or test edit, no package/config edit, no `.agents` / `.codex` / `.github` edit, no GitHub mutation, no phase promotion, no reviewer-pass claim, no implementation-readiness claim, and no user-dialogue ownership.

## 1. Plan Summary

Implement `new doc` routing so Issue-scope `draft-design` and `draft-plan` use the Issue `.assurance.json` `classification.authorized_profile` and load `templates/issue-profiles/<profile>/{design,plan}.md`, while preserving `draft-requirement` and Initiative / Epic draft behavior.

The execution should be strict-grade even though `authorized_profile` is currently `standard`, because the design declares `manual_escalation: "strict"` and the touched surface spans runtime, profile template authority, discussion draft governance, tests, provider docs, and dogfooding docs.

Behavior backlog:

- `BH-001`: classified Issue `draft-design` creates exactly one discussion file from the authorized profile design template.
- `BH-002`: classified Issue `draft-plan` creates exactly one discussion file from the authorized profile plan template.
- `BH-003`: Issue `draft-requirement` remains common-template based and does not require `.assurance.json`.
- `BH-004`: Initiative / Epic `draft-design` and `draft-plan` remain scope canonical-template based.
- `BH-005`: missing / invalid / stale `.assurance.json` fails before allocating or writing a discussion draft.
- `BH-006`: unsupported profile and unsafe / missing / empty / non-file profile templates fail before write and reuse compose-grade filesystem guards.
- `BH-007`: generated drafts do not self-claim canonical authority, adoption, reviewer pass, or phase completion.
- `BH-008`: provider docs and dogfooding docs no longer say Issue design/plan drafts are sourced from `templates/issue/{design,plan}.md`.

Recommended milestone order: Red tests first, shared profile template source loader second, `new doc` routing third, docs update fourth, final quality gate last.

## 2. Requirement / Design Traceability

| Requirement / Design | Planned closure |
|---|---|
| REQ-001 / REQ-002; DES-001 / DES-002 | `tests/cli_runtime/test_new.py` adds classified Issue `draft-design` / `draft-plan` Red tests expecting Standard headings from `issue-profiles/standard`. Runtime then routes through `authorized_profile`. |
| REQ-003; DES-005 | Existing or updated `draft-requirement` test proves no assurance contract is required and `templates/issue/requirement.md` remains the source. |
| REQ-004; DES-006 | Existing Initiative / Epic draft tests stay in `test_new.py`; keep them as regression checks while changing only Issue design/plan. |
| REQ-005 / REQ-006; DES-004 | Add fail-closed tests for missing, invalid JSON/schema, stale source binding, unsupported profile, and template validation failures. Error text must include issue target, doc type, reason, and `assurance classify --stage requirement` remediation. |
| REQ-007; DES-007 | Tests count `discussions/` files before and after failures and assert canonical `design.md` / `plan.md` content remains unchanged. |
| REQ-008; DES-008 | Success tests inspect frontmatter for absence of forbidden authority/adoption claims. |
| REQ-009 | Docs step updates provider source docs and dogfooding mirror where applicable. |
| REQ-010; DES-009 | `tests/cli_runtime/test_assurance_compose.py` remains a guardrail for profile template validation; add coverage there only if loader extraction changes compose behavior. |

## 3. Milestones

### M01 Red Contract Tests

Scope: `tests/cli_runtime/test_new.py`, with minimal fixture reuse from `test_assurance_compose.py`.

Deliverables:

- Replace the old Issue `draft-design` expectation that points at `templates/issue/design.md`.
- Add Red tests for Standard `draft-design` and `draft-plan`.
- Add Strict / Critical heading smoke checks by writing valid assurance contracts or by extending helper fixtures if existing classification cannot produce those profiles deterministically.
- Add fail-closed no-write tests for missing / invalid / stale contracts.
- Preserve tests for `draft-requirement` and Initiative / Epic drafts.

Commit candidate: test-only Red commit after confirming new tests fail for the old reason and existing unrelated tests are not broadened.

### M02 Shared Profile Template Source Loader

Scope: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`, optionally `application/ports.py` and `cli/bootstrap.py`.

Deliverables:

- Extract reusable profile template validation so compose and draft routing share allowed profile, containment, regular-file, existence, and non-empty checks.
- Add a loader returning full Markdown text and repo-relative source path for draft rendering, while preserving `load_profile_artifact_template()` body-only compose contract.
- Avoid duplicating path validation inside `create_node.py`.

Commit candidate: infra/application wiring commit with focused tests still Red on routing until M03, or combined with M03 if a separate commit would not be reviewable.

### M03 Issue Draft Routing Behavior

Scope: `application/create_node.py`, plus narrow port/bootstrap wiring if M02 introduces a port.

Deliverables:

- Detect `scope.kind == "issue"` and `doc_type in {"draft-design", "draft-plan"}`.
- Resolve the target Issue through `AssuranceStore.resolve_issue_target()` using the already-resolved issue scope path or id.
- Call `AssuranceStore.verify_contract()` before filename allocation and before `write_text`.
- Select only `contract.classification.authorized_profile.value`.
- Render full profile template text with existing replacements.
- Bypass legacy `_normalize_draft_discussion_text()` for profile-sourced Issue design/plan drafts.
- Preserve existing generic path for non-Issue drafts and Issue `draft-requirement`.

Commit candidate: behavior commit after `tests/cli_runtime/test_new.py` and `tests/cli_runtime/test_assurance_compose.py` pass.

### M04 Docs And Dogfooding Mirror

Scope: `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` and dogfooding mirror `spec-dock/docs/rules/issue/discussions.md` if the provider asset change requires checked-in parity.

Deliverables:

- Update Issue discussion rules to say `draft-design` / `draft-plan` use `templates/issue-profiles/<authorized_profile>/{design,plan}.md`.
- Keep `draft-requirement` wording on common Issue requirement template.
- Mention fail-closed behavior for unclassified / stale Issue design/plan drafts and use `disc` / `research` for pre-classification thinking.

Commit candidate: docs-only commit after `spec-reviewer` docs/spec alignment pass.

### M99 Final Quality Gate

Scope: entire issue diff and report evidence.

Deliverables:

- Run focused tests and repository validation.
- Confirm no unintended canonical discussion draft authority claims.
- Run final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` gates.
- Record closure, reviewer, commit, PR delivery, and merge-preparation evidence in canonical `report.md` before completion.

## 4. Dependency-Derived Execution Order

1. Confirm issue dependencies: `iss-00250` depends on the profile template pack from `iss-00247` and the grade-aware authoring ADR. If not already satisfied, run `./spec-dock/scripts/spec-dock deps check iss-00250` before implementation.
2. Start with `test_new.py` Red tests because current behavior is explicitly fixed there and the bug is observable at CLI level.
3. Extract the template loader before routing logic so filesystem safety remains centralized in `ArtifactStore`.
4. Implement routing in `create_node.py` after the loader exists, preserving existing command shape and filename conventions.
5. Update docs only after behavior is green, so documentation follows the verified contract.
6. Run `validate` / `sync` after docs and tests, because generated readiness and docs parity are downstream confirmations rather than implementation prerequisites.

## 5. Issue / Step Slicing

### S01 Profile Draft Success Path

- Behavior goal: classified Issue `draft-design` / `draft-plan` uses `authorized_profile` templates.
- Red evidence: `test_new_doc_issue_draft_design_uses_authorized_profile_template` and `test_new_doc_issue_draft_plan_uses_authorized_profile_template` fail against current `templates/issue/{design,plan}.md` routing.
- Implementation slice: profile template loader + Issue design/plan routing only.
- Reviewer focus: `code-reviewer` for runtime/tests.

Concrete test seeds:

- `tc-s01-001` acceptance: Standard design draft includes profile heading
  - Preconditions: temp repo, linked Issue, active Issue, valid `.assurance.json` with `authorized_profile=standard`.
  - Operation: `spec-dock new doc draft-design --issue <id> --title "Design Draft"`.
  - Expected: one `*-draft-design-design-draft.md`; content includes `Issue 設計書（Standard）`; content does not include legacy thin body heading.
  - Failure detection: old scope-template routing still reads `templates/issue/design.md`.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k profile_template`.

- `tc-s01-002` acceptance: Standard plan draft includes profile heading and Standard plan section
  - Preconditions: same fixture with valid contract.
  - Operation: `spec-dock new doc draft-plan --issue <id> --title "Plan Draft"`.
  - Expected: one `*-draft-plan-plan-draft.md`; content includes `Issue 実装計画書（Standard / TDD）` and `## 6. 仕様固定クロージャ一覧`.
  - Failure detection: old normalized thin plan contains only generic `## 計画` / `## 検証`.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k profile_template`.

### S02 Fail-Closed Contract And Template Guards

- Behavior goal: unsafe or unclassified Issue design/plan draft paths fail before discussion write.
- Red evidence: no-write tests fail today because old generic fallback succeeds.
- Implementation slice: assurance verification before filename allocation / write; template validation errors propagated with remediation.
- Reviewer focus: `code-reviewer`.

Concrete test seeds:

- `tc-s02-001` negative: missing `.assurance.json` creates no design/plan draft
  - Preconditions: temp Issue with no contract and empty matching draft glob count.
  - Operation: `new doc draft-design --issue <id>` and `new doc draft-plan --issue <id>`.
  - Expected: non-zero exit; stderr/stdout includes `missing_assurance_contract` and `assurance classify --stage requirement`; matching draft count remains unchanged.
  - Failure detection: generic fallback creates a draft despite missing contract.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k fail_closed`.

- `tc-s02-002` negative: invalid JSON/schema and stale binding create no fallback
  - Preconditions: invalid `.assurance.json` case and a stale binding case copied from compose fixture style.
  - Operation: `new doc draft-plan --issue <id>`.
  - Expected: non-zero with reason `invalid_json`, `invalid_schema`, or `stale_source_binding`; no new `*-draft-plan-*`.
  - Failure detection: write occurs before verification or stale contract is ignored.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k fail_closed`.

- `tc-s02-003` negative: unsafe profile template source creates no fallback
  - Preconditions: classified Issue and one profile template missing, symlink escape, non-file, or empty.
  - Operation: matching `draft-design` / `draft-plan`.
  - Expected: non-zero; no discussion file; error reason points to template validation.
  - Failure detection: duplicate loader misses a guard covered by compose.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py -k "template or draft"`.

### S03 Legacy Behavior Preservation

- Behavior goal: preserve all non-target draft doc paths.
- Red evidence: regression tests should pass before and after implementation; if they fail, routing was broadened incorrectly.
- Implementation slice: explicit branch only for Issue `draft-design` / `draft-plan`.
- Reviewer focus: `code-reviewer`.

Concrete test seeds:

- `tc-s03-001` regression: Issue `draft-requirement` works without assurance contract
  - Preconditions: temp Issue without `.assurance.json`.
  - Operation: `new doc draft-requirement --issue <id>`.
  - Expected: success; common Issue requirement template markers render; no profile lookup error.
  - Failure detection: assurance gate was applied too broadly.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k draft_requirement`.

- `tc-s03-002` regression: Initiative / Epic draft design/plan remain scope-template based
  - Preconditions: temp initiative and epic from existing helper.
  - Operation: `new doc draft-design --initiative <id>` and `new doc draft-plan --epic <id>`.
  - Expected: success using `templates/{initiative,epic}/{design,plan}.md`.
  - Failure detection: profile routing leaks outside Issue scope.
  - Verification: `uv run pytest tests/cli_runtime/test_new.py -k scope_specific`.

### S90 Docs Impact Resolution

- Behavior goal: update provider and dogfooding docs that describe discussion draft sources.
- Verification: docs diff inspection plus focused tests; `spec-reviewer` docs/spec alignment.
- Reviewer focus: `spec-reviewer`.

### S99 Final Quality Gate

- Behavior goal: prove the whole issue closes REQ / DES coverage without hidden regressions.
- Verification commands:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`
  - `uv run pytest tests/cli_runtime` if bootstrap, ports, or shared runtime wiring changes more than the narrow branch.
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --no-github` for local dogfooding projection, or default `sync` if GitHub state is required and available.

## 6. Test Strategy Mapping

TDD / Red strategy:

- The first Red tests must observe public CLI behavior, not private helpers.
- Red should assert the current wrong source by expecting profile headings that the old generic draft cannot contain.
- Fail-closed Red should assert both non-zero exit and unchanged discussion file count.
- Existing compose tests stay as safety net for profile template validation; do not retest every compose detail in `test_new.py`.

Mapping:

| Closure | Test evidence |
|---|---|
| Profile source selected | `test_new.py` success tests inspect headings from `templates/issue-profiles/<profile>`. |
| `authorized_profile` is authority | Fixture sets contract profile; tests do not use frontmatter `Issue Grade` as selector. |
| No fallback on invalid contract | missing / invalid / stale no-write tests. |
| Template guard parity | `test_new.py` unsafe template tests plus existing `test_assurance_compose.py` guard tests. |
| Non-target behavior preserved | existing scope-specific draft tests updated only for Issue design/plan. |
| Canonical artifacts untouched | before/after text snapshots for issue `design.md` and `plan.md` in fail and success cases. |

## 7. Review Gates

- After M01: parent orchestrator records Red evidence in `report.md`; no implementation commit should claim success yet.
- After M02/M03: `code-reviewer` reviews runtime, tests, port/bootstrap wiring, fail-before-write ordering, and guard reuse.
- After M04: `spec-reviewer` reviews provider/dogfooding docs against requirement/design.
- After each milestone: commit candidate or justified approved-no-op, plus `git status --short` clean check for that milestone scope.
- Final gate: `qa-reviewer` for test sufficiency, issue-wide `code-reviewer` for integrated diff, and final `spec-reviewer` for requirement/design/plan/report/docs alignment.

## 8. Rollback / Compatibility

- Compatibility: existing discussion drafts remain grandfathered and are not rewritten.
- Compatibility: unclassified Issues can still use `disc`, `research`, and `draft-requirement`.
- Breaking surface: Issue `draft-design` / `draft-plan` now fail for missing / invalid / stale contracts. This is intentional fail-closed behavior.
- Rollback path: revert runtime/docs/tests diff. That restores thin generic drafts but reintroduces the grade-aware authoring inconsistency; prefer forward fix if possible.
- Safety guard: verification and template source resolution must complete before destination filename allocation and `write_text`.

## 9. Docs Impact

Update candidates:

- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- `spec-dock/docs/rules/issue/discussions.md`

Potential wording:

- Issue `draft-requirement` uses the common Issue requirement template.
- Issue `draft-design` / `draft-plan` use `templates/issue-profiles/<authorized_profile>/{design,plan}.md` after valid `.assurance.json` verification.
- Missing / invalid / stale assurance contracts fail closed; use `disc` / `research` before classification.

No new ADR is required if implementation follows the accepted grade-aware authoring ADR. Create an ADR candidate only if implementation introduces unclassified design/plan draft mode or a new public structured error schema.

## 10. Final Quality Gate

Final exit contract for the canonical plan should require:

- All REQ-001 through REQ-010 mapped to passing tests, docs evidence, or explicit non-scope rationale.
- Focused CLI regression command passes.
- Any broadened runtime change gets `uv run pytest tests/cli_runtime`.
- `./spec-dock/scripts/spec-dock validate` passes.
- `./spec-dock/scripts/spec-dock sync` or `sync --no-github` evidence is recorded with reason for selected mode.
- `report.md` contains Red / Green / Refactor evidence, Delegation Gate entries, Step Contract Closure, Test Contract Closure, Closure Coverage, Docs Impact Resolution, Reviewer Gate Status, Milestone / Commit Candidate Gate, PR Delivery Gate, Merge Preparation Gate, and Final Commit evidence destination.

## 11. Plan Blockers

- No blocker for drafting this delegated plan.
- Adoption blocker: this discussion draft has `diff_guard_result: not-run` and `adoption_status: unreviewed`; main orchestrator must run a post-run diff guard and record Evidence Adoption Ledger disposition before using it as promotion evidence.
- Gate blocker before implementation: requirement/design reviewer pass and canonical plan reviewer pass were not verified in this delegated run.
- Design caution: the Issue is manually escalated to strict while `authorized_profile` is standard. The implementation plan should use strict process gates but must not select runtime templates from the manual escalation field.
- Stop / replan triggers: `AssuranceStore.verify_contract()` cannot safely resolve the issue scope from `new doc`; full-text profile template loading cannot share `ArtifactStore` guards; public CLI success shape must change; or existing discussion compatibility requires migration.

## 12. Integration Notes for Main Orchestrator

- Reflect this draft only through canonical `plan.md` and `report.md` Evidence Adoption Ledger if adopted.
- Keep implementation steps one behavior slice at a time: Red tests, shared loader, routing, docs, final gate.
- Use `dev-coder` for runtime/tests and `doc-writer` for docs updates; then run the matching reviewer gates.
- Treat the `new doc` returned `spec-dock/spec-dock/...` path display anomaly as an observed tooling note, not an iss-00250 behavior requirement unless the orchestrator decides it is in scope or opens a follow-up.
- Unresolved design gaps: none requiring user clarification for this plan draft; the manual strict vs authorized standard distinction must remain explicit in canonical plan wording.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
