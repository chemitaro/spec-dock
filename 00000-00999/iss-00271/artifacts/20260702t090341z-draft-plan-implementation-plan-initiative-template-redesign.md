---
created_by_role: implementation-planner
scope_id: iss-00271
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/artifacts/20260702t081001z-draft-plan-initiative-template-redesign-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - src/spec_dock/assets/spec_dock/templates/initiative/requirement.md
  - src/spec_dock/assets/spec_dock/templates/initiative/design.md
  - src/spec_dock/assets/spec_dock/templates/initiative/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: failed
---

# iss-00271 実装計画ドラフト: Initiative テンプレート再設計

## 1. Plan Summary

このドラフトは、`iss-00271` の canonical `plan.md` へ採用するための実装計画 evidence であり、正本ではない。目的は Initiative の `requirement.md` / `design.md` / `plan.md` テンプレートを、戦略的変更、capability landscape、source-of-truth、artifact adoption、reviewer gate、Epic handoff を扱える上流 planning surface に更新することである。

計画の基本方針は、provider-side template を source of truth として更新し、必要なら checked-in dogfooding mirror を一致させ、既存 template/scaffold regression に最小限の構造 assertion を足す。Issue-level TDD cycle、private code design、DDD / EDA mandatory wording は Initiative template へ持ち込まない。

Source revision note:
- repo HEAD at draft creation: `bf6b1254f6bf83c27431ded05658a27f3ef09a01`
- canonical Issue `design.md` / `plan.md`: `artifact_state: awaiting-assurance-compose` placeholder
- design input used here: pre-start `draft-design` artifact and Epic design decisions, not canonical design adoption

Diff guard note:
- `new artifact draft-plan` created this artifact but also transiently composed canonical `design.md` / `plan.md` / `report.md` and `.assurance.json`; those command side effects were reverted by the authoring adapter.
- A separate untracked `draft-design` artifact appeared in the same artifact directory during this run and was not edited. Because the post-run status is not limited to this draft alone, this draft marks `diff_guard_result: failed` and remains adoption-ineligible until the main orchestrator performs a clean diff guard and report EAL entry.

## 2. Requirement / Design Traceability

Requirement closure targets:
- `I271-AC-001`: `requirement.md` template gets strategic purpose, capability landscape, source-of-truth, stakeholder / trigger, Epic handoff prompts.
- `I271-AC-002`: `design.md` template gets system context, scope boundary, decision authority, artifact adoption, reviewer gate, Epic boundary prompts.
- `I271-AC-003`: `plan.md` template gets Epic decomposition, handoff readiness, fresh reviewer gate, report evidence, controlled re-slicing prompts.
- `I271-AC-004`: all three templates avoid mandatory Issue-level implementation detail, TDD cycle, private code design.
- `I271-AC-005`: all three templates avoid DDD / EDA as default assumptions while permitting architecture-aware adaptation.
- `I271-AC-006`: Japanese-first guidance is explicit; paths, commands, identifiers, fixed SpecDock terms may remain original.
- `I271-AC-007`: a future thin-link insertion point for `docs/authoring/scope-layering.md` exists without adding a dangling link before `iss-00273`.

Inherited design decisions:
- `D-001`: scope-layering reference will live as provider-side reference; this Issue only prepares thin-link wording / insertion point.
- `D-002`: templates stay architecture-neutral / architecture-aware.
- `D-003`: source-grounded understanding precedes canonical authoring.
- `D-005`: six-Issue baseline remains; this Issue feeds `iss-00272`.
- `D-008`: Japanese-first spec / artifact authoring is preserved.
- `D-009`: Issue-local draft artifacts are evidence only and do not make canonical docs implementation-ready.

## 3. Milestones

- `M0` Planning normalization gate:
  - canonical `design.md` / `plan.md` must be composed or manually authored by the main orchestrator before implementation, with this draft adopted / partially adopted / rejected in `report.md`.
  - stop if the canonical design remains placeholder when implementation starts.
- `M1` Initiative requirement template:
  - update `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`.
  - close `I271-AC-001`, part of `I271-AC-004`, `I271-AC-005`, `I271-AC-006`.
- `M2` Initiative design template:
  - update `src/spec_dock/assets/spec_dock/templates/initiative/design.md`.
  - close `I271-AC-002`, part of `I271-AC-004`, `I271-AC-005`, `I271-AC-006`, `I271-AC-007`.
- `M3` Initiative plan template:
  - update `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`.
  - close `I271-AC-003`, part of `I271-AC-004`, `I271-AC-005`, `I271-AC-006`, `I271-AC-007`.
- `M4` Tests and dogfooding mirror:
  - update focused tests and mirror files only if required by existing provider/dogfooding parity.
- `M90` Docs impact:
  - confirm no `docs/authoring/scope-layering.md` dangling link is introduced; record whether docs changes are intentionally deferred to `iss-00273`.
- `M99` Final quality gate:
  - focused tests, grep checks, validate/sync decision, reviewer gates, report ledger, and `issue finish` readiness.

## 4. Dependency-Derived Execution Order

1. `M0`: adopt or reject seed artifacts and compose canonical Issue design/plan. Reason: implementation must not run from placeholder canonical docs.
2. `M1`: update requirement template first. Reason: design and plan prompts depend on the upstream strategic / capability vocabulary.
3. `M2`: update design template second. Reason: design must own source-of-truth, artifact adoption, reviewer gate, and Epic boundary before plan can decompose work.
4. `M3`: update plan template third. Reason: plan prompt should consume the requirement/design vocabulary and produce Epic portfolio / handoff readiness.
5. `M4`: add or update tests after final wording stabilizes. Reason: template assertions should lock the intended contract, not intermediate phrasing.
6. `M90` and `M99`: confirm docs, dogfooding, report, reviewer, and finish gates. Reason: `iss-00272` consumes this vocabulary.

No parallel implementation is recommended inside this Issue. The three templates are coupled by shared vocabulary, and reviewing one coherent vocabulary pass is lower risk than parallel text edits.

## 5. Issue / Step Slicing

### S00: Canonical planning readiness

- Target files: canonical docs only by main orchestrator, not by this delegated draft.
- Planned contract:
  - classify / compose or manually author Issue design and plan.
  - record this artifact in `report.md` Evidence Adoption Ledger.
  - maintain canonical `design.md` / `plan.md` as main-orchestrator-owned.
- Red / alternative evidence:
  - inspect-only: `spec-dock/active/issue/design.md` and `plan.md` must no longer be placeholder before execution starts.
- Stop condition:
  - canonical plan remains placeholder, or seed artifacts are adopted without EAL disposition.

### S01: Requirement template vertical slice

- Target file:
  - `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
- Optional mirror:
  - `spec-dock/templates/initiative/requirement.md` if checked-in dogfooding parity is required.
- TDD-style split:
  - Red: add or update a focused assertion in `tests/unit/infra/test_init_update.py` that fails because the current requirement template lacks strategic purpose / capability landscape / source-of-truth / Epic handoff prompts.
  - Green: add the minimal template sections and Japanese-first guidance needed to pass the assertion.
  - Refactor: tighten headings and remove duplicate wording, keeping template scaffold concise.
- Test candidates:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `rg -n "strategic purpose|capability landscape|source-of-truth|Epic handoff|日本語ファースト" src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`

### S02: Design template vertical slice

- Target file:
  - `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
- Optional mirror:
  - `spec-dock/templates/initiative/design.md` if checked-in dogfooding parity is required.
- TDD-style split:
  - Red: add or update a structural assertion for decision authority / artifact adoption / reviewer gate / Epic boundary; current template should fail at least one new required fragment.
  - Green: update only Initiative design prompts, preserving architecture-neutral wording and existing system-context diagram if still useful.
  - Refactor: collapse duplicated architecture wording and ensure DDD / EDA are optional, not default.
- Test candidates:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `rg -n "artifact adoption|reviewer gate|decision authority|Epic boundary|DDD|EDA" src/spec_dock/assets/spec_dock/templates/initiative/design.md`

### S03: Plan template vertical slice

- Target file:
  - `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- Optional mirror:
  - `spec-dock/templates/initiative/plan.md` if checked-in dogfooding parity is required.
- TDD-style split:
  - Red: add or update a focused assertion that the Initiative plan template exposes Epic decomposition, handoff readiness, controlled re-slicing, report evidence, and fresh reviewer gate.
  - Green: add concise sections for Epic portfolio / dependency order / handoff readiness / final reviewer gate.
  - Refactor: keep Issue-level executable TDD steps out of the Initiative plan template.
- Test candidates:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `rg -n "Epic decomposition|handoff readiness|controlled re-slicing|report evidence|fresh reviewer" src/spec_dock/assets/spec_dock/templates/initiative/plan.md`

### S04: Scaffold / dogfooding parity checks

- Target files:
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/templates/initiative/{requirement,design,plan}.md` only if existing parity tests require checked-in dogfooding mirror updates.
- Planned contract:
  - provider templates and installed / dogfooding templates stay in sync.
  - no legacy nested template scaffolds are reintroduced.
- Test candidates:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "checked_in_dogfooding_mirror_templates_match_provider_assets or spec_document_templates_keep_policy_out_of_scaffold"`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "init_installs"`
  - `uv run pytest tests/unit/infra/test_init_update.py`

### S90: Docs impact and deferred link gate

- Target files:
  - no docs change unless implementation discovers broken guidance caused by the template edit.
- Planned contract:
  - if a scope-layering link target does not exist yet, do not add a broken relative link.
  - record `iss-00273` baton for final thin link insertion.
- Test / inspection candidates:
  - `test ! -e src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md || rg -n "authoring/scope-layering" src/spec_dock/assets/spec_dock/templates/initiative spec-dock/templates/initiative`
  - `rg -n "authoring/scope-layering\\.md" src/spec_dock/assets/spec_dock/templates/initiative spec-dock/templates/initiative`

### S99: Final quality gate

- Target files:
  - no new implementation target; this is verification / report / review closure.
- Required evidence before finish:
  - focused test pass.
  - template grep checks for required guidance and forbidden overreach.
  - `./spec-dock/scripts/spec-dock validate` or documented reason if deferred.
  - `./spec-dock/scripts/spec-dock sync --no-github` or documented reason if deferred.
  - `spec-reviewer` pass for template/spec alignment.
  - `code-reviewer` pass if tests or scaffold behavior assertions were changed.
  - `qa-reviewer` final sufficiency check if required by canonical plan.
  - report ledgers updated before `issue finish`.

## 6. Test Strategy Mapping

Existing test candidates found by `rg`:
- `tests/unit/infra/test_init_update.py`
  - `_assert_installed_templates_match_provider_assets` checks installed templates match provider assets.
  - `test_checked_in_dogfooding_mirror_templates_match_provider_assets` checks checked-in dogfooding mirror parity.
  - `test_spec_document_templates_keep_policy_out_of_scaffold` already validates Japanese-primary labels and several Initiative / Epic / Issue template fragments.
  - issue-specific asset contract tests near delegated authoring and bundled skill routing can host focused fragment assertions if the template contract crosses docs / skills.
- `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - draft artifact / node template behavior tests are relevant only if the implementation changes runtime creation behavior. This Issue should avoid that.
- `tests/unit/commands/test_runtime_new_s08.py`
  - relevant only if node creation semantics are affected. This Issue should avoid that.

Recommended command ladder:
- L1 focused:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- L2 parity:
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
- L3 installer/scaffold regression:
  - `uv run pytest tests/unit/infra/test_init_update.py`
- L4 runtime validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --no-github`
- L5 grep inspection:
  - `rg -n "Issue-level|TDD cycle|private code|private class|DDD|EDA" src/spec_dock/assets/spec_dock/templates/initiative spec-dock/templates/initiative`
  - Required result: no mandatory Issue-level or mandatory DDD / EDA wording. Occurrences are acceptable only when explicitly framed as non-goals or optional adaptation.

## 7. Review Gates

- Per-step template edits:
  - delegated role: `doc-writer`
  - reviewer: `spec-reviewer`
  - focus: requirement/design/plan traceability, Japanese-first wording, architecture-neutrality, artifact authority, Epic handoff.
- Test / scaffold assertion edits:
  - delegated role: `dev-coder`
  - reviewer: `code-reviewer`
  - focus: tests fail for the old contract and pass for the new one; no brittle prose overfitting beyond accepted template contract.
- Final issue gate:
  - `qa-reviewer`: confirms test sufficiency and whether broader integration tests are needed.
  - issue-wide `code-reviewer`: confirms implementation + test + mirror diff is coherent.
  - final `spec-reviewer`: confirms requirement/design/plan/report/template alignment.

Reviewer-pass is not claimed by this draft. The main orchestrator must run fresh reviewers after canonical integration.

## 8. Rollback / Compatibility

- Rollback:
  - revert provider template changes and any matching dogfooding mirror updates in the same reviewable unit.
  - revert focused tests added for the rejected template contract.
- Compatibility:
  - existing managed repos receive new template guidance only on update/init; existing authored Initiative docs are not migrated by this Issue.
  - no runtime command behavior, dependency graph behavior, GitHub mutation, data migration, or `.meta.json` schema change is planned.
  - `authoring/scope-layering.md` link must not be introduced as a broken link before `iss-00273`.
- Escalation triggers:
  - runtime artifact command changes become necessary.
  - Issue grade template changes become necessary.
  - DDD / EDA becomes mandatory wording.
  - template update requires broad workflow docs or skill changes beyond thin guidance.

## 9. Docs Impact

Planned docs impact is intentionally narrow:
- `src/spec_dock/assets/spec_dock/templates/initiative/{requirement,design,plan}.md` are the primary docs-like shipped assets.
- `spec-dock/templates/initiative/{requirement,design,plan}.md` may need mirror updates to satisfy dogfooding parity.
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` is not created here; `iss-00273` owns it.
- workflow docs / skills are not changed here unless the template wording exposes a contradiction that blocks `iss-00271`.

Report must record docs impact as either implemented, intentionally deferred to `iss-00273`, or not applicable with evidence.

## 10. Final Quality Gate

Before `issue finish`, the main orchestrator should confirm:
- canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are issue-specific and not placeholders.
- this draft has an Evidence Adoption Ledger disposition.
- all `I271-AC-*` and `I271-EC-*` rows have closure evidence.
- focused and parity tests pass, or skipped commands have explicit reasons and lower-risk substitute evidence.
- no canonical docs, implementation files, package/config, `.agents`, `.codex`, `.github`, or secrets were changed outside the approved implementation scope.
- `git status --short` contains only intended tracked/untracked changes for the Issue.
- PR delivery is not performed here; `iss-00276` owns the one-PR delivery gate.
- `./spec-dock/scripts/spec-dock issue finish` is run only after report evidence and reviewer gates are complete.

## 11. Plan Blockers

- Blocker: canonical `design.md` / `plan.md` currently remain `awaiting-assurance-compose` placeholders. This draft cannot authorize implementation start.
- Blocker: this draft's diff guard is marked failed because post-run status includes another untracked artifact not edited by this role. Main orchestrator must perform a clean diff guard and ledger disposition before adoption.
- Non-blocking risk: focused test assertions over prose can become brittle. Keep assertions on contract fragments and anti-rules, not full paragraphs.
- Non-blocking risk: adding scope-layering wording before `iss-00273` can accidentally create a dangling link. Use a placeholder phrase or explicit deferred note, not a relative link to a missing file.

## 12. Integration Notes for Main Orchestrator

- Recommended adoption:
  - partially adopt the step order, target files, test ladder, and finish gates into canonical `plan.md` after canonical design is composed.
  - do not adopt the `diff_guard_result: failed` state as success evidence; resolve it in `report.md`.
- Evidence used:
  - active Issue requirement and pre-start draft design/plan seeds.
  - Epic requirement/design/plan including `D-001`, `D-002`, `D-003`, `D-005`, `D-008`, `D-009`.
  - current Initiative templates.
  - `rg` investigation of related tests, especially `tests/unit/infra/test_init_update.py`.
  - workflow references for artifact authority, Issue plan schema, final gates, deps and sync validation.
- Forbidden actions avoided:
  - no canonical `requirement.md` / `design.md` / `plan.md` / `report.md` edit retained.
  - no implementation file, test file, package/config, agent config, GitHub workflow, or secret edit.
  - no GitHub mutation, phase promotion, reviewer-pass claim, issue-ready claim, or `issue finish`.
- Unresolved design gaps:
  - canonical design is not yet composed / adopted; execution readiness remains blocked.
  - exact final wording for scope-layering thin-link insertion should be settled with `iss-00273`.
- Baton to `iss-00272`:
  - pass the shared vocabulary: strategic purpose, capability landscape, source-of-truth, artifact adoption, reviewer gate, handoff readiness, Japanese-first guidance.
  - explicitly note any wording pattern that Epic templates should mirror or intentionally avoid.
  - include whether dogfooding mirror updates were required and which tests locked the Initiative template contract.

## Ledger Note

source-agent: implementation-planner
topic: `iss-00271` implementation plan draft evidence
trigger: user requested a scope-local artifact-only implementation plan draft
ambiguity / constraint: canonical design and plan are placeholders; artifact creation command produced transient forbidden canonical side effects that were reverted; another untracked draft-design artifact exists and was not edited
observed facts: active issue is `iss-00271`; pre-start seed artifacts exist; Epic plan assigns Slice 01 to Initiative templates and defers PR delivery to `iss-00276`; existing tests concentrate template parity and Japanese-primary label checks in `tests/unit/infra/test_init_update.py`
options considered: single broad template rewrite, three template vertical slices, runtime behavior change
proposed decision: use three template vertical slices plus focused tests and mirror parity checks
rationale: this follows provider-side source of truth, keeps Initiative scope above Issue-level TDD detail, and gives `iss-00272` a stable vocabulary baton
affected files: `src/spec_dock/assets/spec_dock/templates/initiative/{requirement,design,plan}.md`, optional `spec-dock/templates/initiative/{requirement,design,plan}.md`, focused tests in `tests/unit/infra/test_init_update.py`
affected tests: focused `test_spec_document_templates_keep_policy_out_of_scaffold`, dogfooding mirror parity, installer/scaffold regression as needed
risk if wrong: brittle prose tests or scope creep into workflow docs / Issue-level execution detail
rollback or revisit: revert template and test diffs for this Issue; defer scope-layering links to `iss-00273`
confidence: medium
needs orchestrator decision: yes, canonical design/plan composition and Evidence Adoption Ledger adoption are required

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
