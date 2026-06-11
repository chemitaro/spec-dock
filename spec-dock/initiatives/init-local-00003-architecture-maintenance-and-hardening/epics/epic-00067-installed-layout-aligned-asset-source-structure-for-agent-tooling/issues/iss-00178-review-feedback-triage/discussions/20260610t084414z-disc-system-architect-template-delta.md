---
種別: disc
ID: "20260610t084414z-disc"
タイトル: "System Architect Template Delta Draft"
状態: "proposed"
親: ["iss-00178"]
authority: "proposed"
adoption_status: "unreviewed"
reflected_to: []
created_by_role: "system-architect"
scope_id: "iss-00178"
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
diff_guard_result: "pending"
---

# System Architect Template Delta Draft

Source requirement revision: `iss-00178` requirement draft inspected from `spec-dock/active/issue/requirement.md`, `最終更新: "2026-06-10"`. User context states this requirement has a fresh spec-reviewer pass after adding/fixing the PR repair batch dedicated template requirement.

## 1. Requirement Coverage

- `AC-002` now requires PR repair batch artifacts to use a `github-pr-merge-preparer` skill-local dedicated template, not only a prose skeleton in the skill body.
- The required provider source path is `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
- The required dogfooding copy path is `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`.
- Runtime `new doc --template`, first-class doc type expansion, and `src/spec_dock/assets/spec_dock/templates/**` runtime catalog changes remain out of scope.
- Current `design.md` covers these deltas in the adoption policy, interface contract, file/module plan, requirement mapping, test strategy, and forbidden paths.

## 2. Existing Context Findings

- Parent epic establishes `src/spec_dock/assets/install_root/` as the provider-side authority for agent-tooling assets and `.agents/` as the installed/dogfooding projection.
- Current provider `github-pr-merge-preparer/SKILL.md` still has only coarse failure classification and bounded repair delegation; it does not yet contain the PR Repair Triage Gate or a template reference.
- Current provider `github-pr-observation/SKILL.md` is collection-only and already has strong stdout JSON / trigger-boundary semantics. It should only receive a boundary clarification, not triage vocabulary.
- Current issue discussion rules define `disc` as synthesis / proposal evidence and confirm delegated drafts are flat, scope-local, and non-canonical.
- At inspection time, neither provider nor dogfooding `templates/pr-repair-batch.md` exists yet. This is expected before implementation but must be closed by S01/S04.

## 3. Design Decisions

- Keep the PR repair batch as existing `disc` semantics, but require a dedicated skill-local template for the batch control sheet.
- Place the full operational template under `github-pr-merge-preparer` because that skill owns PR preparation, batch creation, repair delegation, and merge-prepared reporting.
- Keep `discussions.md` as a short catalog contract that points to the skill workflow instead of duplicating the full template.
- Preserve `github-pr-observation` as evidence collection only. Triage judgment belongs to `github-pr-merge-preparer`.
- Treat `.agents/.../templates/pr-repair-batch.md` as dogfooding parity, not provider authority.

## 4. Alternatives Considered

- Embedding the whole batch skeleton in `github-pr-merge-preparer/SKILL.md`: rejected because the skill body would mix workflow and long form artifact content, increasing drift and copy omissions.
- Putting the full template in `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`: rejected because issue discussion rules should remain a catalog/rules surface, not a workflow-specific template store.
- Adding `new doc disc --template pr-repair-batch`: rejected as explicit non-scope and premature runtime contract expansion.
- Adding a first-class `pr-repair-batch` doc type: rejected because the artifact still fits `disc` authority and lifecycle semantics.
- Adding the template under `src/spec_dock/assets/spec_dock/templates/**`: rejected because that is the runtime template catalog and is explicitly out of scope.

## 5. Boundary / Contract Model

- Provider authority:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Dogfooding copy:
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Workflow owner:
  - `github-pr-merge-preparer`
- Evidence producer:
  - `github-pr-observation` stdout JSON
- Artifact type:
  - existing `disc`, created under issue-scope `discussions/`
- Forbidden boundaries:
  - no runtime `new doc --template`
  - no new first-class doc type
  - no runtime template catalog addition
  - no GitHub mutation beyond already-scoped observation trigger behavior

## 6. Dependency Analysis

- `github-pr-merge-preparer` depends on `github-pr-observation` stdout JSON as authoritative evidence.
- PR repair batch template depends on the requirement vocabulary: `validity`, `risk_class`, `need_to_fix`, `disposition`, `repair_unit`, and `status`.
- Discussion rules should depend on the skill guidance only as a named contract and should not copy the template structure.
- Dogfooding copy depends on provider asset synchronization/parity.
- Runtime `spec_dock_runtime` and runtime discussion templates should have no dependency on this template in this issue.

## 7. Source of Record

- Requirement source of record for this issue:
  - `spec-dock/active/issue/requirement.md`
- Design source of record after main-orchestrator adoption:
  - `spec-dock/active/issue/design.md`
- Provider implementation source of record:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Dogfooding verification source:
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`

## 8. Data Flow / Domain Model / Interface Contract

1. `github-pr-observation` collects checks, review bodies, selected review comments, limitations, and resume metadata.
2. `github-pr-merge-preparer` verifies latest head SHA freshness.
3. `github-pr-merge-preparer` creates a PR repair batch `disc` using the skill-local template.
4. The batch inventory records every finding / failure / limitation with classification and disposition.
5. Items needing design or implementation repair are grouped into repair units.
6. Repair worker receives the repair unit `disc`, not raw findings, as the implementation source.
7. After push, `github-pr-merge-preparer` re-observes latest head SHA and updates merge-prepared evidence.

The batch template must include `PR / Observation Metadata`, `Batch Purpose`, `Concern Catalog`, `Inventory`, `Classification Values`, `Per-Concern Analysis`, `Repair Queue`, `Unit Discussion Plan`, `Stop Conditions`, and `Merge-Prepared Gate`.

## 9. File / Module Change Plan

- Add provider template:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- Update provider workflow guidance:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- Clarify provider observation boundary only:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- Add short provider discussion-rule catalog note:
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- Verify dogfooding parity:
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `spec-dock/docs/rules/issue/discussions.md`

Do not change `src/spec_dock/assets/spec_dock/templates/**` or `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`.

## 10. Migration / Compatibility / Rollback

- Migration: no existing runtime or persisted data migration is needed because the batch remains a `disc` artifact.
- Compatibility: existing discussion creation commands remain valid; the dedicated template is copied/referenced by the skill workflow, not by `new doc`.
- Rollback: revert provider skill/docs/template changes and resync or manually confirm dogfooding parity. No runtime rollback is required.

## 11. Observability

- Primary inspection evidence should be text/path based:
  - template file exists at the provider path.
  - skill guidance references that provider template.
  - template contains required sections and classification vocabulary.
  - dogfooding copy is byte-for-byte aligned with provider source.
  - runtime template and runtime script diffs are empty.
- Runtime telemetry or new validation logic is not required.

## 12. Test Strategy

- Use inspect-only checks for skill/docs/template contracts.
- Required focused checks should include:
  - `test -f src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `rg` for required batch sections in the provider template.
  - `rg` for `PR Repair Triage Gate`, `fix delegation`, `review-clean`, and `merge-prepared` in provider merge-preparer skill.
  - `diff -u` between provider and dogfooding template paths after dogfooding copy is updated.
  - `git diff -- src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime` to confirm forbidden runtime surfaces remain untouched.
- New Python tests are not necessary unless implementation touches installer/runtime behavior despite the design guard.

## 13. ADR Candidates

- No ADR is required for the local template placement decision because it is reversible and scoped to one skill workflow.
- A future ADR may be warranted only if SpecDock later generalizes skill-local templates into a cross-skill or runtime-supported template mechanism.

## 14. Risks

- Skill guidance and template file can drift.
  - Mitigation: inspect both the skill reference and template required sections.
- Dogfooding copy can lag provider source.
  - Mitigation: S04 parity check must include the new template file.
- Agents may still delegate raw findings directly to repair workers.
  - Mitigation: PR Repair Triage Gate must be explicitly placed before fix delegation.
- Runtime template support may be accidentally introduced.
  - Mitigation: forbidden diff check over runtime template and runtime script paths.
- `github-pr-observation` may accumulate judgment language.
  - Mitigation: restrict its change to collection-only boundary clarification.

## 15. Requirement Clarification Requests

None. The current requirement sufficiently fixes the template path, artifact type, non-scope boundaries, and acceptance criteria.

## 16. Integration Notes for Main Orchestrator

- Design finding: current `design.md` correctly reflects the new dedicated template requirement, including the provider path, dogfooding copy path, runtime catalog exclusion, and inspect-only verification strategy.
- Gap to fix before design spec-reviewer gate: no substantive design contradiction found. The main practical gap is ensuring implementation/review checks require both the skill guidance reference and the actual provider template file, because current provider/dogfooding template files are not yet present.
- Suggested adoption target: no canonical wording change is strictly required from this draft unless the orchestrator wants to strengthen `design.md` with an explicit "template file existence is required; prose-only skeleton is insufficient" sentence near the interface contract or test strategy.
- Leaf evidence used: none.
- Forbidden actions avoided: no canonical edit, no implementation edit, no tests/config edit, no GitHub mutation, no phase promotion, no reviewer-pass claim, no user-dialogue ownership.
- Unresolved requirement gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
