---
created_by_role: implementation-planner
scope_id: iss-00272
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/artifacts/20260702t081003z-draft-plan-epic-template-redesign-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t093309z-draft-design-epic-template-redesign-system-architect-design-draft.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - src/spec_dock/assets/spec_dock/templates/epic/requirement.md
  - src/spec_dock/assets/spec_dock/templates/epic/design.md
  - src/spec_dock/assets/spec_dock/templates/epic/plan.md
  - tests/unit/infra/test_init_update.py
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/artifacts/20260702t090341z-draft-plan-implementation-plan-initiative-template-redesign.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00272 実装計画ドラフト: Epic テンプレート再設計

## 1. Plan Summary

この artifact は、`iss-00272` の canonical `plan.md` 作成に向けた実装計画 evidence であり、正本・最終判断・実装開始許可ではない。

目的は provider-side Epic templates を、capability / model envelope、cross-Issue constraints、design slice catalog、Issue handoff package、suggested grade、dependencies、final quality gate を扱える下流接続 surface に更新することである。変更の source of truth は `src/spec_dock/assets/spec_dock/templates/epic/{requirement,design,plan}.md` とし、checked-in dogfooding mirror `spec-dock/templates/epic/{requirement,design,plan}.md` は parity test に従って同期する。

実行は、`iss-00271` の Initiative template 語彙を確認してから、S00 planning normalization、S01 Red focused test、S02 requirement template、S03 design template、S04 plan template、S05 parity / wording、S90 verification、S99 review / finish の順に進める。PR はこの Issue では作らず、`issue finish` で `iss-00273` へ渡す。

Source revision note:
- active issue: `iss-00272`
- parent epic: `epic-00270`
- predecessor evidence: `iss-00271` draft-plan artifact and current Initiative template test pattern
- observed workspace note: artifact creation時点で `iss-00272` の canonical `design.md` / `plan.md` / `report.md` と `.assurance.json`、system-architect draft-design artifact は既に dirty / untracked だった。このドラフトはそれらを編集していない。

## 2. Requirement / Design Traceability

Requirement closure targets:
- `I272-AC-001`: Epic requirement template が capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope を記述できる。
- `I272-AC-002`: Epic design template が cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を記述できる。
- `I272-AC-003`: Epic plan template が Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を記述できる。
- `I272-AC-004`: Epic template が Issue plan の詳細 TDD step や private implementation design を必須化しない。
- `I272-AC-005`: Epic template が `artifacts/` を raw evidence として扱い、採用判断は canonical docs / accepted ADR / report ledger へ置くことを誘導する。
- `I272-AC-006`: 日本語運用で新規 Epic docs の説明文が日本語ファーストになる guidance を含む。
- `I272-AC-007`: 後続 Issue が parent requirement / design trace、allowed local delta、forbidden parent boundary changes、expected evidence を受け取れる。

Inherited design decisions:
- `D-001`: scope-layering reference は provider-side reference に集約する。この Issue では link target 作成を行わず、`iss-00273` が thin links を接続する。
- `D-002`: Epic templates は DDD / EDA を標準前提にしない。
- `D-003`: source-grounded understanding と採用証跡を要求する。
- `D-004`: canonical docs は採用済み decision、scope boundary、handoff contract、gate を持つ。
- `D-005`: 6 Issue baseline は柔軟だが、再分割には plan 更新と fresh review を要求する。
- `D-008`: 日本語ファースト authoring を誘導する。

## 3. Milestones

- `M0` Planning normalization:
  - this draft and design draft evidence are adopted / partially adopted / rejected in `report.md`.
  - canonical `design.md` / `plan.md` are main-orchestrator-owned and not authorized by this artifact alone.
- `M1` Focused Red:
  - add or update focused structural assertions in `tests/unit/infra/test_init_update.py` for Epic requirement / design / plan template contract.
  - preferred host is `test_spec_document_templates_keep_policy_out_of_scaffold`, following `iss-00271`.
- `M2` Epic requirement template:
  - update `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`.
  - close `I272-AC-001`, part of `I272-AC-004`, `I272-AC-005`, `I272-AC-006`.
- `M3` Epic design template:
  - update `src/spec_dock/assets/spec_dock/templates/epic/design.md`.
  - close `I272-AC-002`, part of `I272-AC-004`, `I272-AC-005`, `I272-AC-006`.
- `M4` Epic plan template:
  - update `src/spec_dock/assets/spec_dock/templates/epic/plan.md`.
  - close `I272-AC-003`, `I272-AC-004`, `I272-AC-005`, `I272-AC-006`, `I272-AC-007`.
- `M5` Parity / wording:
  - sync dogfooding mirror when parity tests require it.
  - inspect Japanese-first wording, architecture-neutral wording, and no Issue-level TDD overreach.
- `M90` Verification:
  - run focused tests, mirror parity, targeted wording inspection, and `validate` as applicable.
- `M99` Review / finish:
  - update report evidence, run fresh reviewer gates required by canonical plan, then `issue finish` only. No PR creation.

## 4. Dependency-Derived Execution Order

1. Confirm `iss-00271` completion evidence and current Initiative template vocabulary. Reason: `iss-00272` should mirror or intentionally adapt the upstream wording baton rather than inventing incompatible terms.
2. Normalize planning evidence. Reason: this draft is unreviewed evidence and must be dispositioned before canonical use.
3. Add focused Red assertions. Reason: current Epic templates are skeletal and should fail at least one new structural contract before template edits.
4. Update Epic requirement template. Reason: capability / model envelope and acceptance vocabulary feed design and plan templates.
5. Update Epic design template. Reason: cross-Issue boundary and design slice catalog define what the plan hands to Issues.
6. Update Epic plan template. Reason: Issue handoff package and final quality gate should consume the requirement/design vocabulary.
7. Sync dogfooding mirror and inspect wording. Reason: scaffold-affecting template changes must keep provider and checked-in mirror aligned.
8. Run verification and review gates. Reason: `iss-00273` depends on the resulting handoff vocabulary.
9. Finish Issue without PR. Reason: Epic plan assigns PR readiness / PR creation to `iss-00276`.

## 5. Issue / Step Slicing

### S00: Planning normalization

- Inputs:
  - active issue requirement
  - pre-start draft-plan seed
  - system-architect draft-design artifact
  - parent Epic requirement / design / plan / report
  - `iss-00271` draft-plan artifact and completed template/test pattern
- Actions:
  - main orchestrator decides adoption state for this artifact and the design draft.
  - canonical `plan.md` may incorporate step order, target files, tests, gates, and baton notes.
- Stop conditions:
  - design evidence is contradictory or insufficient.
  - `iss-00271` completion evidence shows unresolved vocabulary / parity risk.
  - implementation would require Issue grade template redesign or runtime command behavior changes.

### S01: Red focused test

- Target:
  - `tests/unit/infra/test_init_update.py`
- Preferred assertion site:
  - `test_spec_document_templates_keep_policy_out_of_scaffold`
- Red expectations:
  - add `epic_requirement`, `epic_design`, and `epic_plan` fragment assertions.
  - old templates should miss at least one required fragment for each updated contract.
- Candidate fragments:
  - requirement: `capability / model envelope`, `Epic-level acceptance`, `scope / non-scope`, `日本語ファースト`
  - design: `cross-Issue boundary`, `design slice catalog`, `contract portfolio`, `failure / migration / test strategy`
  - plan: `Issue handoff package`, `suggested grade`, `dependencies`, `final quality gate`, `parent requirement / design trace`
- Command:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`

### S02: Requirement template

- Target:
  - `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- Optional mirror:
  - `spec-dock/templates/epic/requirement.md`
- Green scope:
  - add concise Japanese-first prompts for purpose / Initiative linkage, use cases, capability / model envelope, Epic requirements, Epic acceptance, scope / forbidden / non-scope.
  - describe artifact evidence as source material only; canonical adoption remains report / ADR / canonical docs.
  - keep architecture-neutral wording; DDD / EDA may appear only as optional vocabulary, not required sections.
- Avoid:
  - Issue-level implementation steps.
  - private file / class design.
  - detailed TDD cadence.

### S03: Design template

- Target:
  - `src/spec_dock/assets/spec_dock/templates/epic/design.md`
- Optional mirror:
  - `spec-dock/templates/epic/design.md`
- Green scope:
  - add cross-Issue boundary / responsibility model prompts.
  - add design slice catalog and contract portfolio prompts.
  - add failure, migration / compatibility, test strategy, and artifact adoption prompts.
  - keep diagrams as optional understanding aids, not mandatory DDD / EDA structure.
- Avoid:
  - replacing Issue design authority.
  - creating semantic reviewer behavior inside templates.
  - linking to `docs/authoring/scope-layering.md` before `iss-00273` owns the reference.

### S04: Plan template

- Target:
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- Optional mirror:
  - `spec-dock/templates/epic/plan.md`
- Green scope:
  - add Issue handoff package fields:
    - parent requirement / design trace
    - allowed local delta
    - forbidden parent boundary changes
    - acceptance seed
    - expected evidence
    - suggested grade
    - dependencies
    - escalation triggers
    - relevant artifacts / ADRs
  - add integration checkpoints and final quality gate.
  - add controlled re-slicing rule and PR boundary note.
- Avoid:
  - detailed per-Issue Red-Green-Refactor steps.
  - treating decision-only Issues as execution-ready.
  - PR creation or GitHub mutation in this Issue.

### S05: Parity / wording

- Targets:
  - `spec-dock/templates/epic/{requirement,design,plan}.md` if parity requires mirror update.
  - `tests/unit/infra/test_init_update.py`
- Actions:
  - keep `_assert_installed_templates_match_provider_assets` and `test_checked_in_dogfooding_mirror_templates_match_provider_assets` passing.
  - inspect for Japanese-first wording and allowed English boundary.
  - inspect for no mandatory DDD / EDA and no Issue-level TDD cadence.
- Commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
  - `rg -n "DDD|EDA|TDD|Issue-level|private class|private file|scope-layering\\.md" src/spec_dock/assets/spec_dock/templates/epic spec-dock/templates/epic`

### S90: Verification

- Focused template contract:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- Mirror parity:
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
- Broader targeted lane:
  - `uv run pytest tests/unit/infra/test_init_update.py`
- Targeted wording inspection:
  - `rg -n "capability / model envelope|design slice catalog|Issue handoff package|suggested grade|final quality gate|日本語ファースト" src/spec_dock/assets/spec_dock/templates/epic spec-dock/templates/epic`
  - `rg -n "Issue-level|private class|private file|detailed TDD|詳細 TDD|docs/authoring/scope-layering\\.md" src/spec_dock/assets/spec_dock/templates/epic spec-dock/templates/epic`
- SpecDock validation:
  - `./spec-dock/scripts/spec-dock validate`
- Optional local sync:
  - `./spec-dock/scripts/spec-dock sync --no-github`

### S99: Review / finish

- Required before finish:
  - report records adoption state for this draft.
  - report records test output and targeted inspections.
  - no PR is created.
  - `iss-00273` baton names final Epic handoff package fields and any deferred thin-link work.
  - fresh `spec-reviewer` confirms requirement/design/plan/report alignment if required by canonical plan.
  - `code-reviewer` confirms test/template diff if tests were changed.
  - `issue finish` is run only by the main orchestrator after gates pass.

## 6. Test Strategy Mapping

Existing test anchors:
- `_assert_installed_templates_match_provider_assets`: installed templates match provider assets.
- `test_checked_in_dogfooding_mirror_templates_match_provider_assets`: checked-in dogfooding mirror parity.
- `test_spec_document_templates_keep_policy_out_of_scaffold`: Japanese-primary labels and template contract fragments; best host for focused Epic template assertions.
- runtime `new artifact` tests are out of scope unless implementation changes draft artifact command behavior. This Issue should avoid that.

Mapping:
- `I272-AC-001`:
  - focused fragment assertions for Epic requirement template.
  - grep inspection for capability / model envelope and Epic-level acceptance.
- `I272-AC-002`:
  - focused fragment assertions for Epic design template.
  - grep inspection for design slice catalog, contract portfolio, failure / migration / test strategy.
- `I272-AC-003` and `I272-AC-007`:
  - focused fragment assertions for Epic plan template.
  - grep inspection for Issue handoff package fields.
- `I272-AC-004`:
  - targeted wording inspection for no required Issue-level TDD / private implementation design.
- `I272-AC-005`:
  - template assertions or grep for artifact evidence / adoption wording.
- `I272-AC-006`:
  - existing Japanese-primary label guard plus targeted read-through.
- Provider / dogfooding sync:
  - mirror parity test and optional direct diff inspection.

## 7. Review Gates

- Planning adoption gate:
  - main orchestrator records this artifact in `report.md` EAL.
  - this draft remains `adoption_status: unreviewed` until that happens.
- Template wording gate:
  - reviewer: `spec-reviewer`
  - focus: scope ownership, artifact authority, handoff completeness, Japanese-first authoring, architecture neutrality.
- Test / scaffold gate:
  - reviewer: `code-reviewer`
  - focus: focused assertions are structural and not brittle paragraph snapshots.
- Final sufficiency gate:
  - reviewer: `qa-reviewer` if canonical plan requires it.
  - focus: command ladder, report evidence, mirror parity, `iss-00273` baton.

This artifact claims no reviewer pass.

## 8. Rollback / Compatibility

- Rollback:
  - revert provider Epic template changes and matching dogfooding mirror changes together.
  - revert focused test assertions added for the rejected template contract.
  - leave historical artifacts untouched unless the main orchestrator explicitly decides otherwise.
- Compatibility:
  - existing authored Epic docs in managed repos are not migrated.
  - new / updated managed repos receive template guidance through init/update.
  - no runtime command behavior, GitHub mutation, metadata schema, dependency graph, or package/config change is planned.
  - dogfooding mirror must match provider assets when checked in.
- Escalation triggers:
  - Issue grade templates need redesign.
  - runtime draft artifact command behavior needs change.
  - `docs/authoring/scope-layering.md` must be created now rather than deferred to `iss-00273`.
  - Epic templates cannot satisfy ACs without workflow docs / skill changes beyond narrow wording.

## 9. Docs Impact

Primary docs-like assets:
- `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/epic/design.md`
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`

Dogfooding mirror impact:
- `spec-dock/templates/epic/requirement.md`
- `spec-dock/templates/epic/design.md`
- `spec-dock/templates/epic/plan.md`

Deferred docs impact:
- `docs/authoring/scope-layering.md` reference creation and thin-link finalization belong to `iss-00273`.
- Workflow docs / skills should not be changed in this Issue unless implementation finds a direct contradiction that blocks Epic template wording.

Report should record whether mirror sync was required and which wording patterns are handed to `iss-00273`.

## 10. Final Quality Gate

Before `issue finish`, confirm:
- canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` are issue-specific and reviewed according to the canonical workflow.
- this artifact has an EAL disposition.
- every `I272-AC-*` and `I272-EC-*` has closure evidence or an explicit non-applicability rationale.
- focused template contract test passes.
- dogfooding mirror parity passes.
- targeted wording inspection confirms no mandatory DDD / EDA, no Issue-level TDD cadence, and no private implementation design requirement.
- `./spec-dock/scripts/spec-dock validate` passes or a blocking reason is recorded.
- `git status --short` contains only intended changes for this Issue.
- no PR is created here.
- baton to `iss-00273` is clear: Epic handoff package fields, scope-layering thin-link wording, and artifact authority language.

## 11. Plan Blockers

- Blocker candidate: if `iss-00271` completion evidence is not available or reveals unresolved template vocabulary drift, stop before S01.
- Blocker candidate: if canonical design evidence contradicts parent Epic design or `I272-AC-*`, return to design rather than implementing from this plan.
- Blocker candidate: if Epic template ACs require Issue grade template redesign or runtime command changes, this Issue scope is insufficient.
- Non-blocking risk: prose-fragment assertions can become brittle. Prefer stable contract headings / field names and anti-rules.
- Non-blocking risk: adding `scope-layering.md` links before the file exists can create dangling guidance. Defer final links to `iss-00273`.

Unresolved design gaps: none known from the provided sources; adoption remains orchestrator-owned.

## 12. Integration Notes for Main Orchestrator

Recommended adoption:
- Adopt S00-S99 sequence, target files, command ladder, and finish boundary into canonical `plan.md` if consistent with canonical design.
- Partially adopt exact fragment names only after final template wording is chosen.
- Record this artifact as evidence, not authority.

Lightweight provenance summary:
- Created by role: `implementation-planner`.
- Scope: `iss-00272`.
- Leaf evidence used: none; no peer or downstream agent was called.
- Source requirement/design revisions: active issue requirement, active parent Epic requirement/design/plan/report, current provider Epic templates, current test anchors, `iss-00271` completed draft-plan pattern.
- Forbidden actions avoided:
  - no canonical docs intentionally edited by this adapter.
  - no implementation files, tests, package/config, agent config, GitHub workflow, or secrets edited.
  - no PR, GitHub mutation, phase promotion, reviewer-pass claim, implementation-readiness claim, or `issue finish`.

Baton to `iss-00273`:
- Epic handoff package fields should be available in the updated Epic plan template.
- Scope-layering reference links remain deferred.
- Artifact authority wording should distinguish raw evidence from canonical adoption.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

diff_guard_result: passed - this adapter created and edited only `spec-dock/active/issue/artifacts/20260702t093345z-draft-plan-implementation-plan-epic-template-redesign.md`; canonical docs were already dirty before this artifact run and were not edited by this adapter.
