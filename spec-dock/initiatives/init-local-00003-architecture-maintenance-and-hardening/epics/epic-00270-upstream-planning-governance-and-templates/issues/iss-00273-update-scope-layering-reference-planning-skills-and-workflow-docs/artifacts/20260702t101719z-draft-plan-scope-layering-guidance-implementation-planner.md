---
created_by_role: implementation-planner
scope_id: iss-00273
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00272-redesign-epic-requirement-design-plan-templates/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00272-redesign-epic-requirement-design-plan-templates/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00272-redesign-epic-requirement-design-plan-templates/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00272-redesign-epic-requirement-design-plan-templates/report.md
  - src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/spec_dock/docs/workflow_clarification.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md
  - src/spec_dock/assets/spec_dock/templates/initiative/design.md
  - src/spec_dock/assets/spec_dock/templates/initiative/plan.md
  - src/spec_dock/assets/spec_dock/templates/epic/plan.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
  - tests/unit/infra/test_init_update.py
  - tests/cli_runtime/test_new.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00273 Scope-layering guidance implementation-planner draft

この artifact は委任 planning evidence であり、canonical `plan.md` ではない。採用可否、正規 `plan.md` への反映、`report.md` Evidence Adoption Ledger 更新、fresh reviewer gate は main orchestrator が所有する。

## 1. Plan Summary

`iss-00273` は strict 相当の guidance / scaffold-docs Issue として扱う。実装の中心は、provider-side `docs/authoring/scope-layering.md` を狭い責務・判断配置 reference として追加し、workflow docs、phase / authoring docs、planning skills、`iss-00271` / `iss-00272` で準備済みの Initiative / Epic templates へ薄く接続すること。

この Issue では PR を作成しない。完了時は `issue finish` で `iss-00274` へ渡し、Epic delivery PR は `iss-00276` が扱う。

実行前の注意:

- 現在の active `design.md` / `plan.md` は `approved` frontmatter だが、本文の多くが generic template placeholder である。実装開始前に main orchestrator が assurance compose 後の canonical design / plan を Issue 固有に正規化し、fresh `spec-reviewer` pass を得る必要がある。
- `artifacts/20260702t101615z-draft-design-draft-design-scope-layering-guidance-system-architect.md` が並行して存在する場合は、S00 で system-architect evidence として採否を `report.md` に記録する。
- この draft は実装 readiness、reviewer pass、phase promotion、issue finish を主張しない。

## 2. Requirement / Design Traceability

| ID | 閉じる内容 | 主 step | 予定 evidence |
|---|---|---|---|
| `I273-AC-001` | `docs/authoring/scope-layering.md` が Initiative / Epic / Issue の責務、decision radius、authority flow、anti-rules を狭く説明する。 | S01, S02 | reference existence test、docs read-through、`rg` link inspection |
| `I273-AC-002` | workflow docs / phase docs / skills / templates は全文重複せず thin link で誘導する。 | S03, S04, S05, S06, S07 | duplicate wording grep、spec-reviewer |
| `I273-AC-003` | planning skills が source-grounded clarification、一問ずつ interview、採用知識の外部化を誘導する。 | S05 | skill read-through、`rg` fragments、spec-reviewer |
| `I273-AC-004` | raw `artifacts/`、research、interview、delegated draft が canonical authority でないことを明示する。 | S02, S03, S05 | authority wording grep、reviewer |
| `I273-AC-005` | 日本語ファースト guidance を docs / skills / artifact guidance へ反映する。 | S02, S03, S05, S07 | Japanese-primary existing assertion、skill/docs inspection |
| `I273-AC-006` | `iss-00271` / `iss-00272` の template 接続点を実 reference へ接続し、dangling link を残さない。 | S06 | provider / mirror template tests、link grep |
| `I273-AC-007` | focused checks / validate で reference、主要リンク、重複回避、authority leak 欠如を確認する。 | S01, S90, S99 | `uv run pytest ...`, `rg`, `validate`, `git diff --check` |
| `I273-AC-008` | Epic Planning / workflow docs / planning skills が downstream Issue handoff に `draft-design` / `draft-plan` path index、または blocked / fallback evidence を含める。 | S03, S05 | workflow / skill grep、spec-reviewer |
| `I273-AC-009` | Epic Planning は Issue Start 前に canonical Issue `design.md` / `plan.md` 本文を作成せず、pre-start seed を Issue-local artifacts として扱う。 | S03, S05 | `draft-design` / `draft-plan` wording grep、reviewer |
| `I273-EC-001` | full responsibility table を各 surface に複製しない。 | S02-S07 | duplicate phrase grep、reviewer |
| `I273-EC-002` | `artifacts/` を accepted authority と誤認させない。 | S02-S07 | negative grep、reviewer |
| `I273-EC-003` | DDD / EDA を SpecDock 標準アーキテクチャとして記述しない。 | S02-S07 | existing negative assertion、targeted grep |
| `I273-EC-004` | 日本語ファースト guidance が識別子や外部固有名詞の翻訳圧力にならない。 | S02-S07 | Japanese-first wording inspection、reviewer |

Design evidence mapping:

- Parent Epic D-001: S02 で provider-side reference、S03-S06 で thin links。
- Parent Epic D-003: S03 / S05 で source-grounded clarification と adoption evidence。
- Parent Epic D-005: S03 / S05 で Issue handoff と re-slicing boundary を薄く参照。
- Parent Epic D-008: S02-S07 で日本語ファーストと識別子原文保持。
- Parent Epic D-009: S03 / S05 で Issue-local `draft-design` / `draft-plan` と canonical compose boundary。

## 3. Milestones

| Milestone | 成果 | 主な step | Gate |
|---|---|---|---|
| M00 Planning normalization | issue 固有の canonical design / plan / report gate が揃う。 | S00 | `assurance verify`, fresh `spec-reviewer`, EAL update |
| M01 Red / characterization | reference 欠落、link 欠落、authority leak、template final link 未接続を検出する tests / grep seed を置く。 | S01 | expected Red or inspect-only evidence |
| M02 Reference publication | `scope-layering.md` provider / dogfooding mirror が存在し、狭い reference として読める。 | S02 | focused test partial Green、manual read-through |
| M03 Workflow / phase docs thin links | workflow / phase / authoring docs が reference と draft artifact handoff を薄く案内する。 | S03, S04 | docs grep、spec-reviewer |
| M04 Skill guidance alignment | planning / clarification skills が source-grounded、artifact authority、日本語ファースト、draft handoff を案内する。 | S05 | skill grep、spec-reviewer |
| M05 Template final links | Initiative / Epic templates の準備済み接続点が actual reference へ接続される。 | S06 | provider / mirror parity、template contract test |
| M06 Refactor / drift control | 重複、過度な table、英語本文混入、DDD / EDA 標準化、authority leak を除く。 | S07 | targeted `rg`, `git diff --check` |
| M90 Verification / report | tests、validate、grep、report evidence、reviewer gates を揃える。 | S90 | focused commands pass |
| M99 Finish handoff | no PR で `issue finish` 可能な evidence を揃え、`iss-00274` へ渡す。 | S99 | final QA / code / spec review pass、finish gate |

## 4. Dependency-Derived Execution Order

1. `iss-00271` / `iss-00272` が準備した template vocabulary と tests を先に確認する。これが template final link の前提。
2. Red / characterization を先に置く。現在は `docs/authoring/scope-layering.md` が存在せず、`tests/unit/infra/test_init_update.py` には `docs/authoring/scope-layering.md` が templates に含まれないことを期待する negative assertion があるため、S01 で検出対象を反転させられる。
3. Reference を先に作る。thin links の target が存在しない状態で workflow / templates を更新すると dangling link になる。
4. workflow / phase / authoring docs を更新してから skills を更新する。skills は docs への first-read routing surface であり、詳細を持ちすぎない。
5. templates final links は reference と docs wording が確定してから入れる。`iss-00271` / `iss-00272` の scope-link 接続点だけを使い、テンプレート本体の再設計に戻らない。
6. tests / grep / validate / reviewer を最後にまとめるが、S01-S07 の各 step は step-local verification を持つ。

## 5. Issue / Step Slicing

### S00 Planning normalization / evidence adoption

- 種別: planning gate / docs-only
- Red / Green / Refactor: not applicable。実装前 gate。
- allowed paths: main orchestrator only `spec-dock/active/issue/{design.md,plan.md,report.md}` と採用対象 artifact evidence。
- forbidden paths for this delegated draft: canonical docs、implementation files、templates、tests、skills、GitHub state。
- 実行内容:
  - `./spec-dock/scripts/spec-dock deps check iss-00273` で predecessor readiness を確認する。
  - `assurance classify --stage requirement`、`assurance compose --artifact all`、`assurance verify` を実行する。
  - pre-start seed、system-architect draft、implementation-planner draft を `report.md` EAL / Delegated Draft Evidence に採用・部分採用・棄却・deferred として記録する。
  - active `design.md` / `plan.md` が placeholder でない Issue 固有正本になったことを fresh `spec-reviewer` に確認させる。
- stop:
  - `iss-00272` finish / dependency readiness が確認できない。
  - `design.md` / `plan.md` が template-only のまま。
  - specialist evidence または manual fallback evidence が missing。

### S01 Red: scope-layering and handoff contract checks

- 種別: Red / characterization-first
- delegated role: `dev-coder` for test assertion, or main orchestrator inspect-only if tests are deferred to `iss-00275`.
- allowed paths:
  - `tests/unit/infra/test_init_update.py`
- target assertions:
  - provider docs include `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`.
  - dogfooding mirror includes `spec-dock/docs/authoring/scope-layering.md`.
  - workflow / phase / skills / templates link to `docs/authoring/scope-layering.md` only as thin references.
  - Initiative / Epic templates no longer assert absence of `docs/authoring/scope-layering.md`.
  - `draft-design` と `draft-plan` の Issue-local path index が Epic planning handoff wording に存在する。
  - authority leak fragments such as `artifact is canonical authority`, `adoption_status: adopted` as self-claim, or `authority: accepted` in draft guidance are absent.
- expected Red:
  - reference file is absent.
  - current template test explicitly rejects `docs/authoring/scope-layering.md`.
- command:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- stop:
  - test passes before production docs/templates change.
  - assertion requires dogfooding-specific Issue IDs or full prose equality.

### S02 Green: publish narrow scope-layering reference

- 種別: Green / docs-only
- delegated role: `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `spec-dock/docs/authoring/scope-layering.md`
- forbidden:
  - workflow docs、skills、templates、tests in this step.
  - ADR daily operational replacement.
- content contract:
  - Initiative: strategic / investment / cross-epic operating model ownership.
  - Epic: cross-Issue design backbone, dependency order, handoff package ownership.
  - Issue: local observable behavior / contract delta, execution plan, report evidence ownership.
  - Authority flow: raw artifact / delegated draft -> EAL / canonical docs / accepted ADR -> fresh review -> downstream use.
  - Anti-rules: decision-only Issue ready、full table duplication、artifact accepted authority self-claim、DDD / EDA default、identifier translation pressure。
- verification:
  - `test -f src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `test -f spec-dock/docs/authoring/scope-layering.md`
  - manual read-through for Japanese-first and narrowness.

### S03 Green: workflow docs thin links and draft handoff boundary

- 種別: Green / docs-only
- delegated role: `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` only if source-grounded / interview wording needs a thin reference adjustment.
  - dogfooding mirror `spec-dock/docs/workflow_*.md` if this repo maintains checked-in mirror parity for shipped docs.
- required deltas:
  - add related link to `[authoring/scope-layering.md](authoring/scope-layering.md)` or correct relative equivalent.
  - `workflow_epic.md` handoff package must mention Issue-local `draft-design` and `draft-plan` path index, or explicit skipped / blocked / fallback evidence.
  - pre-start canonical Issue `design.md` / `plan.md` must remain placeholder until Issue Planning / assurance compose; draft seed lives in Issue-local artifacts.
  - `workflow_issue.md` should say Issue does not redefine parent envelope; it adopts parent trace and closes local delta.
- verification:
  - `rg -n "authoring/scope-layering\\.md|draft-design|draft-plan|Issue-local" src/spec_dock/assets/spec_dock/docs/workflow_*.md`
  - `rg -n "assurance compose.*draft artifact|draft artifact.*canonical authority" src/spec_dock/assets/spec_dock/docs/workflow_*.md` should not find misleading wording.

### S04 Green: phase / authoring docs thin links

- 種別: Green / docs-only
- delegated role: `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md` only for delegated evidence / scope boundary link if needed.
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`
  - dogfooding mirror counterparts where present.
- required deltas:
  - add reference pointer without copying full scope ownership table.
  - keep `authoring/issue-plan.md` focused on executable step schema; only mention scope-layering as boundary input.
  - keep `decision-routing.md` as examples / routing; do not absorb the new reference body.
- verification:
  - `rg -n "scope-layering|authoring/scope-layering" src/spec_dock/assets/spec_dock/docs/phase_*.md src/spec_dock/assets/spec_dock/docs/authoring`
  - duplicate guard by reviewer inspection.

### S05 Green: planning / clarification skills alignment

- 種別: Green / skill-text-only
- delegated role: `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` only for handoff-ready / execution-ready wording if not left to `iss-00274`.
  - checked-in dogfooding `.agents/skills/...` only if repo policy requires installed asset mirror refresh.
- required deltas:
  - add first-read pointer to `spec-dock/docs/authoring/scope-layering.md`.
  - initiative/epic planning skills should route source-grounded clarification and adoption evidence without asking humans for locally answerable facts.
  - epic planning should explicitly avoid pre-start canonical Issue `design.md` / `plan.md` body creation; use Issue-local `draft-design` / `draft-plan`.
  - issue planning should treat draft artifacts as evidence to adopt / partially adopt / reject before canonical compose and fresh review.
  - clarification skill should keep one essential question at a time and Japanese-first artifact guidance.
- verification:
  - `rg -n "scope-layering|draft-design|draft-plan|日本語ファースト|source-grounded|一問" src/spec_dock/assets/install_root/.agents/skills`
  - spec-reviewer docs/spec alignment pass.

### S06 Green: final template links and mirror sync

- 種別: Green / template-only
- delegated role: `doc-writer`
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` if Epic handoff wording needs path index.
  - `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` only if required for link discoverability.
  - `src/spec_dock/assets/spec_dock/templates/epic/design.md` only if scope boundary link is missing.
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - dogfooding mirror `spec-dock/templates/initiative/...` and `spec-dock/templates/epic/...`.
  - `tests/unit/infra/test_init_update.py`
- required deltas:
  - replace "authoring reference が存在する場合" placeholder with actual thin link.
  - keep template prose short; do not copy responsibility table.
  - update test assertions that currently require `docs/authoring/scope-layering.md` to be absent.
- verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`

### S07 Refactor / wording drift control

- 種別: Refactor / inspect-only
- delegated role: main orchestrator or `doc-writer` for bounded wording repair
- allowed paths: files changed in S02-S06 only.
- checks:
  - no full responsibility table outside `scope-layering.md`.
  - no DDD / EDA as default.
  - no `artifacts/` accepted authority leak.
  - Japanese-first body with identifiers / commands preserved.
  - no dogfooding-specific Issue IDs in shipped templates.
- commands:
  - `rg -n "iss-0027[123]|mandatory DDD|mandatory EDA|DDD / EDA を必須前提にする|artifact.*canonical authority|authority: accepted|adoption_status: adopted" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/install_root/.agents/skills spec-dock/docs spec-dock/templates tests/unit/infra/test_init_update.py`
  - `git diff --check`

### S90 Verification / report evidence

- 種別: verification / report
- allowed paths:
  - `spec-dock/active/issue/report.md` by main orchestrator only.
- commands:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
  - `uv run pytest tests/unit/infra/test_init_update.py` if changes touch shared scaffold assertions broadly.
  - `uv run pytest tests/cli_runtime/test_new.py -k "draft_design or draft_plan or artifact"` only if runtime-owned `new artifact` behavior or command help is changed. Guidance-only changes should not require this lane.
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- grep / link inspections:
  - `rg -n "docs/authoring/scope-layering\\.md|authoring/scope-layering\\.md" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/install_root/.agents/skills spec-dock/docs spec-dock/templates`
  - `rg -n "draft-design|draft-plan|Issue-local" src/spec_dock/assets/spec_dock/docs/workflow_epic.md src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - targeted negative grep from S07.
- report:
  - record Red / Green / Refactor evidence.
  - record specialist draft adoption status.
  - record unresolved gaps or `none`.
  - record skipped broad tests and why.

### S99 Final quality gate / no-PR handoff

- 種別: final gate
- required reviewers:
  - `spec-reviewer`: requirement / design / plan / report / docs / skills / templates alignment, AC / EC closure, authority boundary.
  - `code-reviewer`: required if `tests/unit/infra/test_init_update.py` or scaffold behavior assertions change.
  - `qa-reviewer`: test coverage sufficiency and whether `iss-00275` can own broader smoke coverage.
- finish:
  - no PR creation.
  - no GitHub issue close outside `issue finish`.
  - run `./spec-dock/scripts/spec-dock issue finish` only after final gates and report evidence are complete.
  - handoff to `iss-00274` with reference path, link surfaces, draft artifact boundary, and any remaining readiness wording that belongs to execution workflow.

## 6. Test Strategy Mapping

| Test / command | Purpose | Step | Expected |
|---|---|---|---|
| `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` | docs / template / skill contract fragments and forbidden wording. | S01, S06, S90 | Red before implementation, pass after Green |
| `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` | provider assets and dogfooding mirror parity for templates. | S06, S90 | pass |
| `uv run pytest tests/unit/infra/test_init_update.py` | broader scaffold regression when assertions become shared. | S90 | pass or documented skip |
| `uv run pytest tests/cli_runtime/test_new.py -k "draft_design or draft_plan or artifact"` | only if runtime artifact command behavior is changed. | S90 | pass or not applicable |
| `./spec-dock/scripts/spec-dock validate` | SpecDock tree / links / metadata sanity. | S90 | pass |
| `git diff --check` | whitespace / conflict marker sanity. | S07, S90 | pass |
| targeted `rg` link inspection | discoverability and no dangling link. | S03-S07, S90 | expected links present |
| targeted `rg` negative inspection | no authority leak, DDD / EDA default, dogfooding ID, over-translation. | S07, S90 | no production hits except tests / negative assertions |

## 7. Review Gates

Before execution:

- S00 must update canonical `design.md` / `plan.md` from placeholder to Issue-specific content or explicitly block.
- `report.md` must include EAL rows for pre-start seed, system-architect draft, this implementation-planner draft, assurance commands, and fresh spec-reviewer.
- Strict planning obligation requires system-architect / implementation-planner evidence or manual fallback. This artifact satisfies only implementation-planner draft production, not adoption.

Per step:

- docs-only / template-only / skill-text-only steps use `doc-writer` or justified parent implementation exception plus `spec-reviewer`.
- test / scaffold assertion changes require `code-reviewer` and `qa-reviewer` as appropriate.
- reviewer pass is not replaced by this draft, worker output, or `validate`.

Before finish:

- all `I273-AC-001..009` and `I273-EC-001..004` must be mapped to observed evidence in `report.md`.
- `spec-reviewer`, `qa-reviewer`, and issue-wide `code-reviewer` where applicable must be fresh pass.
- final report must state no PR was created and `iss-00274` receives the handoff.

## 8. Rollback / Compatibility

- Rollback is file-level revert of provider docs / skills / templates / tests from this Issue. No migration, data conversion, or runtime metadata transformation is planned.
- Existing authored Initiative / Epic / Issue docs are not rewritten. Updated scaffold affects future `init` / `update` consumers and checked-in dogfooding mirror.
- `artifacts/` and legacy `discussions/` preservation behavior remains unchanged.
- Existing Issue grade / TDD workflow remains authority for Issue execution; this Issue only adds reference and guidance.
- If reference grows into workflow lifecycle detail, move lifecycle detail back to `workflow_*.md` and keep `scope-layering.md` narrow.
- If runtime command behavior appears necessary, stop and coordinate with `iss-00274` / `iss-00275` rather than expanding this Issue silently.

## 9. Docs Impact

Provider assets:

- new candidate: `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- likely docs updates: `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, selected `phase_plan*.md`, `authoring/issue-plan.md`, possibly `workflow_clarification.md` / `decision-routing.md`.
- likely skill updates: `spec-dock-initiative-planning`, `spec-dock-epic-planning`, `spec-dock-issue-planning`, `spec-dock-clarification`; `spec-dock-epic-execution` only if handoff-ready / execution-ready boundary needs a thin pointer before `iss-00274`.
- likely template updates: Initiative design / plan and Epic plan, plus only minimal Epic requirement / design links if needed.
- tests: `tests/unit/infra/test_init_update.py` is the primary focused lane.

Dogfooding mirror:

- For shipped docs/templates, inspect whether checked-in mirror under `spec-dock/docs/...` and `spec-dock/templates/...` exists and keep it synced where local dogfooding validation expects parity.
- For installed agent tooling, `src/spec_dock/assets/install_root/` is source of truth. Update root `.agents/skills/...` only if the repo intentionally tracks dogfooding installed assets as a mirror for this change; otherwise verify via installer/update tests or note non-refresh.

Forbidden surfaces:

- canonical docs in this delegated draft task.
- implementation runtime command behavior unless S00 re-plans.
- `src/spec_dock/assets/spec_dock/templates/issue*` and issue profile templates.
- dependency algorithm, `.meta.json` manual edits, `.assurance.json` manual edits.
- package/config, `.github`, secrets, GitHub mutation, PR creation.

## 10. Final Quality Gate

Final gate checklist:

- `scope-layering.md` exists in provider source and dogfooding mirror if applicable.
- all thin links resolve and are not dangling.
- templates use actual reference link and do not carry full responsibility table.
- Epic handoff guidance includes Issue-local `draft-design` / `draft-plan` path index or explicit blocked / fallback evidence.
- canonical Issue pre-start design / plan body creation is not encouraged.
- artifact authority language is safe: evidence-only until EAL / canonical adoption / fresh review.
- Japanese-first guidance is present without translating paths, commands, identifiers, fixed SpecDock terms, or external proper nouns.
- focused tests, `validate`, `git diff --check`, and targeted grep pass or have recorded skip rationale.
- `report.md` has Step Evidence, EAL, Delegated Draft Evidence, Reviewer Gate Status, Closure Coverage, and no unresolved stale / blocked rows.
- no PR is created in this Issue.
- `issue finish` hands off to `iss-00274`.

## 11. Plan Blockers

Current blockers before execution:

- active `design.md` and `plan.md` still contain broad template placeholder sections. Main orchestrator must normalize them into Issue-specific canonical docs before implementation.
- S00 must verify whether `iss-00272` is lifecycle-finished in the current projection. `iss-00272/report.md` says implementation and review gates are complete but `issue finish` was pending at the time read.
- Any newly created system-architect draft must be reconciled in `report.md`; existence alone is not readiness.

Unresolved design gaps for this draft: none beyond the S00 canonical-normalization blockers above.

Clarification candidates for orchestrator:

- If root `.agents/skills` mirror differs from `src/spec_dock/assets/install_root/.agents/skills`, decide whether this Issue refreshes the checked-in dogfooding mirror or records provider-only update with installer validation.
- If `scope-layering.md` should be linked from every workflow / phase doc or only scope-affecting docs, prefer minimal links; reviewer can request expansion.

## 12. Integration Notes for Main Orchestrator

- Treat this file as `implementation-planner` source evidence. Do not copy it wholesale into canonical `plan.md`; adopt the step order, closure mapping, target surfaces, and verification ladder after reconciling with system-architect evidence.
- Record adoption in `spec-dock/active/issue/report.md` with `adoption_status: adopted` or `partially_adopted` only after inspection. This artifact itself keeps `adoption_status: unreviewed`.
- Before canonical adoption, run fresh `spec-reviewer` on the integrated `requirement.md` / `design.md` / `plan.md` / `report.md` set.
- This draft used no leaf delegated evidence beyond local source reads and repository inspection. Leaf evidence used: none.
- Forbidden actions avoided: canonical edits, implementation edits, template/test/skill changes, PR creation, GitHub mutation, reviewer-pass claim, implementation-readiness claim, user-dialogue ownership.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

diff_guard_result: passed - this role wrote only this issue-local artifact; pre-existing or parallel canonical / assurance / system-architect artifact changes were not edited.
