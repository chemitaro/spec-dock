---
種別: disc
ID: "20260610t084958z-disc"
タイトル: "Implementation Planner Template Delta Draft"
状態: "proposed"
親: ["iss-00178"]
authority: "proposed"
adoption_status: "unreviewed"
reflected_to: []
created_by_role: "implementation-planner"
scope_id: "iss-00178"
source_paths:
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md"
  - "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - "spec-dock/docs/authoring/issue-plan.md"
  - "spec-dock/docs/workflow_issue.md"
intended_targets:
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
diff_guard_result: "pending"
---

# Implementation Planner Template Delta Draft

## 1. Plan Summary

Current `plan.md` is executable under `phase_plan_issue.md` and `authoring/issue-plan.md` after the template requirement change, with one condition for main orchestrator review: the plan re-review should treat the skill-local template file as a first-class planned artifact, not as prose embedded in `SKILL.md`.

The current plan already includes the required implementation shape:

- S01 adds the provider-side `github-pr-merge-preparer` workflow contract and `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
- S02 preserves the `github-pr-observation` collection-only boundary.
- S03 updates issue discussion rules with a short catalog contract instead of duplicating the full template.
- S04 confirms or syncs dogfooding parity, including `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
- S90/S99 verify docs impact, provider/dogfooding parity, and forbidden runtime/template diff.

No design blocker was found. The main plan finding is to keep closure evidence strict enough that a prose-only skill update cannot accidentally satisfy AC-002.

## 2. Requirement / Design Traceability

- Requirement trace:
  - AC-001 maps to S01 through the PR Repair Triage Gate before fix delegation.
  - AC-002 maps to S01 and S03 through the dedicated skill-local batch template and discussion rules catalog note.
  - AC-003 maps to S01 through required inventory fields and classification values.
  - AC-004 maps to S01/S03 through repair unit `disc` handoff.
  - AC-005 maps to S01 through rationale and residual-risk requirements for non-fix dispositions.
  - AC-006 maps to S01 through batch-aware `merge-prepared` predicates and `review-clean` separation.
  - AC-007 maps to S02 through the observation boundary.
  - AC-008 maps to S01-S04/S99 through explicit runtime/template/catalog exclusions.
- Design trace:
  - The design now fixes the template source at `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
  - The design identifies the dogfooding copy at `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
  - The design keeps runtime `new doc --template`, new doc type, and `src/spec_dock/assets/spec_dock/templates/**` catalog changes out of scope.

Source revisions inspected: active issue docs have `最終更新: "2026-06-10"` and workspace HEAD observed as `daa17bab`.

## 3. Milestones

- M1: Provider PR repair batch contract
  - Covers S01.
  - Fixes the executable source for the dedicated batch template and merge-preparer workflow reference.
- M2: Responsibility boundary and discussion catalog
  - Covers S02 and S03.
  - Keeps observation as evidence collection only and keeps discussion rules as a short catalog contract.
- M3: Dogfooding parity and no-runtime-drift proof
  - Covers S04 and S90.
  - Confirms checked-in dogfooding assets match provider assets and docs impact is resolved without runtime template work.
- M4: Final quality gate
  - Covers S99.
  - Confirms closure IDs, reviewer gates, forbidden runtime diff, and final report evidence.

## 4. Dependency-Derived Execution Order

The current step order is correct:

1. S01 must run first because the merge-preparer skill owns the PR repair batch workflow and the skill-local template is the referenced source.
2. S02 follows S01 because the observation skill should only state the downstream judgment boundary after the downstream owner is named.
3. S03 follows S01 because discussion rules should point to the already-defined skill-local template contract and avoid full template duplication.
4. S04 follows S01-S03 because dogfooding parity can only be checked after provider assets and provider docs are finalized.
5. S90/S99 close docs impact and final quality gates after all intended provider/dogfooding changes are known.

This order matches the design dependency graph: `github-pr-observation` produces evidence, `github-pr-merge-preparer` owns triage judgment, batch/unit `disc` artifacts carry repair planning, and human merge remains outside automation.

## 5. Issue / Step Slicing

The slicing is acceptable for a docs/skill/template-only issue:

- S01 is the largest slice, but it still represents one observable behavior: merge-preparer requires a PR Repair Triage Gate and a dedicated batch template before repair delegation.
- S02 is a separate boundary slice for the observation skill and should not be folded into S01.
- S03 is a separate catalog slice so discussion rules do not become the template authority.
- S04 is correctly isolated as a parity/integration slice.
- S90 and S99 are correctly outside the behavior slices.

Closure IDs to keep anchored:

- `tc-002` must explicitly require the provider template file, required sections, and `SKILL.md` reference.
- `tc-008` must explicitly guard forbidden runtime paths.
- `tc-013` must explicitly include provider/dogfooding template parity, not only the two `SKILL.md` files.
- `tc-014` should remain docs-impact focused and avoid reopening runtime template catalog decisions.
- `tc-015` should remain final gate coverage, not a substitute for per-step closure.

## 6. Test Strategy Mapping

The inspect-only strategy is appropriate because the implementation changes shipped skill/docs/template assets rather than runtime behavior. The verification bundle should include:

```bash
test -f src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
test -f .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
rg -n "PR / Observation Metadata|Batch Purpose|Concern Catalog|Inventory|Classification Values|Per-Concern Analysis|Repair Queue|Unit Discussion Plan|Stop Conditions|Merge-Prepared Gate" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
rg -n "validity.*valid.*partially-valid.*false-positive.*duplicate.*unknown|risk_class.*blocking.*material-follow-up.*minor.*false-positive.*duplicate|need_to_fix.*yes.*no.*follow-up.*human-decision|disposition.*fix-now.*follow-up.*no-action.*covered-by.*needs-human|status.*untriaged.*triaged.*unit-needed.*unit-created.*implemented.*reobserved-pass.*blocked" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
git diff -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime src/spec_dock/assets/spec_dock/templates
```

The current plan already contains these categories. Main orchestrator should verify that report evidence records actual command outputs for template existence, required sections, classification values, parity, and forbidden runtime diff.

## 7. Review Gates

- Per-step `spec-reviewer` is sufficient for S01-S04 if changes remain skill/docs/template-only.
- `code-reviewer` becomes required if implementation touches runtime behavior, installer/update behavior, tests, scripts, or runtime templates.
- S99 should keep the three final reviewers:
  - `qa-reviewer` for obligation coverage and whether inspect-only evidence is sufficient.
  - issue-wide `code-reviewer` for integrated diff and no forbidden runtime/template drift.
  - final `spec-reviewer` for requirement/design/plan/report alignment.

Delegated drafts and worker outputs must remain evidence only. They do not replace fresh reviewer pass.

## 8. Rollback / Compatibility

Rollback is straightforward because the change is additive and asset-scoped:

- Remove the provider skill-local template if S01 is rejected.
- Remove the dogfooding copy if S04 was applied.
- Revert only the corresponding `SKILL.md` and discussion rules text if the template contract is rejected.

Compatibility constraints:

- Existing `disc` semantics stay unchanged.
- No new document type is introduced.
- No runtime `new doc --template` support is introduced.
- No runtime template catalog under `src/spec_dock/assets/spec_dock/templates/**` is introduced.
- `github-pr-observation` stdout JSON remains the evidence boundary and does not gain classification responsibility.

## 9. Docs Impact

Docs impact is intentionally limited:

- `github-pr-merge-preparer/SKILL.md` should name the template file and operational gate.
- `github-pr-observation/SKILL.md` should state collection-only responsibility and downstream triage ownership.
- `docs/rules/issue/discussions.md` should add only the catalog-level note that PR repair batch/unit are existing `disc` usage and the batch uses the merge-preparer skill-local template.

The plan should continue rejecting full template duplication in discussion rules because the full operational template belongs with the skill that uses it.

## 10. Final Quality Gate

S99 is strong enough if it records:

- `git diff --check`.
- Provider/dogfooding parity for both `SKILL.md` files, discussion rules, and `pr-repair-batch.md`.
- Empty forbidden diff for `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime` and `src/spec_dock/assets/spec_dock/templates`.
- `uv run pytest tests/unit/infra` or a recorded justified alternative if the environment cannot run it.
- `./spec-dock/scripts/spec-dock validate`.
- `./spec-dock/scripts/spec-dock sync --no-github` or a recorded justified alternative if it touches unrelated state.
- Fresh final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass.

## 11. Plan Blockers

None.

Clarification candidates for the main orchestrator:

- Whether S01 should explicitly add a separate verification line proving `SKILL.md` references `templates/pr-repair-batch.md` by exact path.
- Whether S99 should require `git diff --name-only` inspection to prove no unrelated managed dogfooding files changed during sync.

These are plan-tightening candidates, not blockers.

## 12. Integration Notes for Main Orchestrator

- This draft should be considered proposed evidence only.
- If adopted, reflect it in `report.md` Evidence Adoption Ledger and Delegated Draft Evidence before using it as plan re-review support.
- Suggested plan finding to carry forward: current `plan.md` is executable after the template delta, provided `tc-002`, `tc-013`, and `tc-008` remain strict enough to catch prose-only template work, dogfooding drift, and runtime template/catalog scope creep.
- Leaf evidence used: active requirement/design/plan/report, provider merge-preparer and observation skills, provider discussion rules, `phase_plan_issue.md`, `authoring/issue-plan.md`, and `workflow_issue.md`.
- Forbidden actions avoided: no canonical doc edits, no implementation edits, no tests/config/runtime edits, no GitHub mutation, no lifecycle promotion, no reviewer-pass claim.
- Unresolved design gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
