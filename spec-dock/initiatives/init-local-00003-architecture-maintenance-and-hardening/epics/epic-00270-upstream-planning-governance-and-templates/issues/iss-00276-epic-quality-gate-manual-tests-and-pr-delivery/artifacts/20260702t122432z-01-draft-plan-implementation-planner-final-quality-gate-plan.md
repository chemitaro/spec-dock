---
created_by_role: implementation-planner
scope_id: iss-00276
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00272-redesign-epic-requirement-design-plan-templates/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00273-update-scope-layering-reference-planning-skills-and-workflow-docs/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00274-update-epic-execution-handoff-and-issue-readiness-workflow/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00275-add-upstream-planning-smoke-tests-and-template-validation/report.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/authoring/issue-plan.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00276 implementation-planner draft: final quality gate plan

この文書は `iss-00276` の正規 `plan.md` 作成に使う artifact-only draft である。正規 `requirement.md` / `design.md` / `plan.md` / `report.md` は編集していない。ここでの reviewer、test、PR、finish は未実行の計画であり、pass 済みとは主張しない。

## 1. Plan Summary

`iss-00276` は `critical` grade の final quality / PR delivery Issue として扱う。目的は、`iss-00271` から `iss-00275` の成果を前提に、Epic 全体の automated checks、manual dogfooding、raw artifact hygiene、reviewer repair loop、Epic report 更新、final commit、PR 作成と observation を一つの順序付き gate にまとめることである。

実行計画は S00 から S07 のリレーとする。

- S00: current-state bootstrap と前段 Issue completion audit。
- S01: planning adoption と fresh `spec-reviewer`。
- S02: automated checks と SpecDock validation / assurance。
- S03: manual dogfooding / read-through と raw artifact hygiene。
- S04: reviewer gates と repair loop。
- S05: Epic report update。
- S06: final commit と clean state。
- S07: `github-pr-merge-preparer` による PR creation / observation。

停止原則:

- 前段 Issue が未完了または evidence 矛盾を持つ場合、理由と next action を `report.md` に残し、PR 作成へ進まない。
- failing checks / reviewer finding / PR observation blocker を隠して readiness を主張しない。
- final gate repair を超える新規 scope、PR merge、GitHub issue close、raw manual files の commit は行わない。

## 2. Requirement / Design Traceability

主な normative sources:

- Issue requirement: `I276-AC-001..011`, `I276-EC-001..005`。
- Epic requirement: `E-RQ-008`, `E-RQ-009`, `E-RQ-010`, `E-AC-006`, `E-AC-007`, `E-AC-008`。
- Epic design: `D-007` one-PR delivery default、`D-008` Japanese-first spec authoring、`D-009` unified draft artifact command and grade-role policy。
- Epic plan Slice 06: final quality / PR delivery は `iss-00276` の責務。
- Current Issue `design.md`: ユーザー指定どおり substantive design ではなく placeholder/template としてだけ扱う。

Traceability summary:

| Requirement | Closure ID | Primary step | Planned evidence |
|---|---|---|---|
| `I276-AC-001` | `C276-001` | S00 | `iss-00271..iss-00275` reports、`deps check iss-00276`、`active show`、未完了 / deferred の reason と next action |
| `I276-AC-002` | `C276-002` | S02 | `uv run pytest tests/unit`、`uv run pytest tests/cli_runtime`、可能なら `uv run pytest`、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock assurance verify` の結果 |
| `I276-AC-003` | `C276-003` | S03 | manual dogfooding / scaffold / skill read-through summary、`git status --short`、raw manual files not staged evidence |
| `I276-AC-004` | `C276-004` | S04 | final `spec-reviewer` verdict と repair / re-review evidence |
| `I276-AC-005` | `C276-005` | S04 | `qa-reviewer` verdict、必要時の issue-wide `code-reviewer` verdict、または unavailable / denied reason と fallback evidence |
| `I276-AC-006` | `C276-006` | S07 | PR description draft / PR body with scope, background, changes, impact, verification, risk, follow-up |
| `I276-AC-007` | `C276-007` | S00, S07 | one-PR feasibility decision。破綻時は `epic-00270/plan.md` amendment + fresh review before PR split |
| `I276-AC-008` | `C276-008` | S03, S04 | Japanese-first read-through summary and `spec-reviewer` confirmation |
| `I276-AC-009` | `C276-009` | S00, S03 | `iss-00271..iss-00275` completion evidence plus pre-start draft migration confirmation |
| `I276-AC-010` | `C276-010` | S00, S03 | canonical Issue `design.md` / `plan.md` grep proving no misplaced draft body remains |
| `I276-AC-011` | `C276-011` | S07 | PR description explains handoff-ready / execution-ready, draft artifact adoption, final validation |
| `I276-EC-001` | `C276-012` | S00, S07 | PR creation blocked unless previous Issues are complete or explicitly deferred |
| `I276-EC-002` | `C276-013` | S02, S04, S07 | failing checks / reviewers / observation recorded with reason and next action |
| `I276-EC-003` | `C276-014` | S00, S04 | repair scope check; scope expansion triggers plan amendment / follow-up |
| `I276-EC-004` | `C276-015` | S03, S06 | `git status --short` and raw artifact hygiene before commit / PR |
| `I276-EC-005` | `C276-016` | S07 | PR merge and GitHub issue close explicitly excluded unless user separately instructs |

## 3. Milestones

### S00 current-state bootstrap and 前段Issue completion audit

Goal:

- `iss-00276` の実行開始時点を固定し、前段 `iss-00271..iss-00275` の completion / report / reviewer / validation evidence を監査する。

Planned checks:

- `git status --short`
- `./spec-dock/scripts/spec-dock active show`
- `./spec-dock/scripts/spec-dock deps check iss-00276`
- 前段 reports の `進捗サマリー`、`Evidence Adoption Ledger`、`Reviewer Gate Status`、`検証`、`完了 / PR` を読む。
- `rg -n "artifact_state: awaiting-assurance-compose|draft-before-issue-start" <iss-00276 design.md plan.md>`

Closure:

- `C276-001`, `C276-007`, `C276-009`, `C276-010`, `C276-012`, `C276-014`。

Stop conditions:

- 前段 Issue が実状態として未完了で、明示的 defer / next action がない。
- report 上の古い文言と projection / active state が矛盾し、どちらを採用すべきか判断できない。
- `iss-00276` の canonical `design.md` / `plan.md` に misplaced pre-start draft body が戻っている。

### S01 planning adoption and fresh spec-review

Goal:

- pre-start draft と本 artifact の採否を main orchestrator が `report.md` EAL に記録し、正規 `design.md` / `plan.md` を `assurance compose` 後に具体化し、fresh `spec-reviewer` に通す。

Planned checks:

- `./spec-dock/scripts/spec-dock assurance classify --stage requirement`
- `./spec-dock/scripts/spec-dock assurance compose --artifact all`
- `./spec-dock/scripts/spec-dock assurance verify`
- fresh `spec-reviewer` for `requirement.md` / composed `design.md` / composed `plan.md` / `report.md` / source artifacts。

Closure:

- `C276-004`, `C276-009`, `C276-010`。

Stop conditions:

- `design.md` が substantive final-quality contract にならず、placeholder/template のまま残る。
- `plan.md` が executable step、delegation contract、verification、reviewer focus、closure mapping を欠く。
- delegated draft を reviewer pass や final authority の代替として扱っている。

### S02 automated checks

Goal:

- Epic-wide diff に対し、狭い focused checks ではなく final quality として十分な automated evidence を取る。

Command ladder:

- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`
- `uv run pytest` if practical. If not practical, record reason, duration/risk, and next action.
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock assurance verify`
- 必要なら `./spec-dock/scripts/spec-dock sync`。実行時は generated projection diff と branch state を report に残す。

Closure:

- `C276-002`, `C276-013`。

Stop conditions:

- failure を unexplained のまま PR readiness に進める必要がある。
- failure が final gate repair を超える新規 scope を示す。

### S03 manual dogfooding/read-through and raw artifact hygiene

Goal:

- automated checks だけでは拾えない authoring / scaffold / workflow / skill の一貫性を、読解と必要最小限の manual dogfooding summary で確認する。

Manual targets:

- Initiative / Epic templates の日本語ファースト本文、scope-layering link、Issue handoff fields。
- `spec-dock/docs/workflow_issue.md`, `workflow_spec_authoring.md`, `authoring/issue-plan.md` の handoff-ready / execution-ready、draft artifact、review gate、PR delivery gate 記述。
- `src/spec_dock/assets/spec_dock/...` provider source と dogfooding `spec-dock/...` mirror の差分意図。
- `manual-tests/`、raw logs、captures、tmp artifacts が staged / tracked されていないこと。

Suggested inspections:

- `git status --short`
- `git diff --name-status`
- `git diff --check`
- targeted `rg` for `draft-before-issue-start`, `artifact_state: awaiting-assurance-compose`, `handoff-ready`, `execution-ready`, `日本語ファースト`, `raw artifact`, `canonical authority`。

Closure:

- `C276-003`, `C276-008`, `C276-009`, `C276-010`, `C276-015`。

Stop conditions:

- raw manual workspace / log / capture が staged されている。
- Japanese-first authoring guidance が識別子以外の英語説明本文として残り、reviewer finding ではなく template / skill guidance の欠落と判断される。

### S04 reviewer gates and repair loop

Goal:

- final `qa-reviewer`、issue-wide `code-reviewer`、final `spec-reviewer` を fresh gate として実行し、finding があれば bounded repair と再検証を行う。

Reviewer mapping:

- `qa-reviewer`: S02 automated checks と S03 manual evidence の十分性、full `uv run pytest` 要否、未実施 check の妥当性。
- `code-reviewer`: implementation diff が大きい場合、または tests / runtime / scaffold behavior を含む場合に issue-wide review。利用しない場合は diff が docs-only / report-only 等である理由と fallback を `report.md` に残す。
- `spec-reviewer`: Epic requirement / design / plan fulfillment、Issue closure coverage、日本語ファースト authoring、draft artifact boundary、PR description readiness。

Repair loop:

1. reviewer finding を severity / scope / affected closure へ分類する。
2. in-scope repair は bounded worker または approved local exception で修正する。
3. affected checks を再実行する。
4. 該当 reviewer を fresh re-review する。
5. `report.md` の Reviewer Gate Status / Step Evidence / Closure Coverage を更新する。

Closure:

- `C276-004`, `C276-005`, `C276-013`, `C276-014`。

Stop conditions:

- reviewer gate が `pass` 以外で、waiver / unavailable を pass として扱う必要が出る。
- repair が new upstream planning policy、new feature、PR split を必要とする。

### S05 Epic report update

Goal:

- `epic-00270/report.md` に final quality evidence、E-AC status、manual summary、reviewer result、PR readiness boundary を反映する。

Planned content:

- `iss-00271..iss-00275` completion / defer summary。
- S02 checks の result / failure reason / next action。
- S03 manual dogfooding summary と raw artifact hygiene。
- S04 reviewer gates and repair loop summary。
- E-AC-001..008 の final status。
- PR description に入れる validation / risk / follow-up summary。

Closure:

- `C276-006`, `C276-008`, `C276-009`, `C276-011`, plus Epic `E-AC-006..008`。

Stop conditions:

- Epic report に unresolved `blocked` / `stale` EAL entry が残る。
- observed evidence ではなく予定や希望を完了証跡として書く必要がある。

### S06 final commit / clean state

Goal:

- final report ledger と delivery evidence boundary を閉じ、意図しない staged / unstaged / untracked raw artifact がない状態にする。

Planned checks:

- `git status --short`
- `git diff --check`
- staged diff inspection before commit
- final commit using repository commit policy. Commit message creation should use the `git-commit-message` skill if main orchestrator creates the commit.
- post-commit `git status --short`

Closure:

- `C276-015`, and prerequisite evidence for S07。

Stop conditions:

- implementation milestone の未commit差分を final commit にまとめて救済しようとしている。
- raw manual files、temporary logs、captures、local-only artifacts が commit対象に含まれる。

### S07 PR creation / observation via github-pr-merge-preparer

Goal:

- 原則1PRで GitHub PR を作成または既存 PR を再利用し、PR Delivery Gate と Merge Preparation Gate を report に記録する。

Planned actions:

- `github-pr-merge-preparer` を使う。
- PR description には scope、背景、変更内容、影響範囲、検証、manual dogfooding、risk、follow-up、handoff-ready / execution-ready boundary、draft artifact adoption、final validation を含める。
- Observation では latest head SHA、Actions / required checks、review state、unresolved review thread limitation、merge conflict / visible blocker、fix loop history を確認する。

Closure:

- `C276-006`, `C276-007`, `C276-011`, `C276-012`, `C276-013`, `C276-016`。

Stop conditions:

- 前段 completion / final gates / final commit が閉じていない。
- PR split が必要だが Epic plan amendment と fresh review がまだない。
- PR merge または GitHub issue close をこの Issue の暗黙作業として進める必要がある。

## 4. Dependency-Derived Execution Order

依存順は Epic plan の relay chain に従う。

```text
iss-00271 -> iss-00272 -> iss-00273 -> iss-00274 -> iss-00275 -> iss-00276
```

`iss-00276` 内部では、PR delivery は最後にしか置かない。前段 completion audit が S00、canonical plan adoption が S01、automated / manual / reviewer evidence が S02-S04、Epic report closure が S05、commit clean state が S06、PR delivery / observation が S07 である。

理由:

- `I276-EC-001` により、前段未完了のまま PR 作成できない。
- `workflow_issue.md` により、PR Delivery Gate / Merge Preparation Gate は final commit gates 後、`issue finish` 前に report evidence を残す必要がある。
- `D-007` one-PR delivery default は、PR split 判断より先に final integrated gate を要求する。

## 5. Issue / Step Slicing

この Issue は新機能を足す slice ではなく final quality gate slice である。したがって step は変更種別ではなく closure gate で分ける。

- Bootstrap slice: S00。前段 state と misplaced draft absence を閉じる。
- Planning slice: S01。draft adoption / canonical compose / fresh spec-review を閉じる。
- Automated validation slice: S02。test / validate / assurance を閉じる。
- Manual validation slice: S03。dogfooding read-through / hygiene / Japanese-first を閉じる。
- Review and repair slice: S04。qa / code / spec review loop を閉じる。
- Reporting slice: S05。Epic report と PR body source summary を閉じる。
- Delivery state slice: S06-S07。final commit、PR creation、observation、merge-prepared evidence を閉じる。

Step-local delegation guidance:

- Code / runtime / tests / scaffold repairs found in S02-S04 should use `dev-coder` unless main orchestrator records a valid Parent Implementation Exception.
- Shipped docs / templates / skills / workflow text repairs should use `doc-writer` unless a valid exception is recorded.
- Reviewers are independent fresh gates and are not replaced by worker output.

## 6. Test Strategy Mapping

Automated:

- `uv run pytest tests/unit`: broad unit baseline for provider assets, domain/application/presentation, and scaffold checks.
- `uv run pytest tests/cli_runtime`: runtime CLI behavior including `new artifact`, validate / workflow status surfaces.
- `uv run pytest`: full suite if practical. If skipped, record why focused + final QA review is sufficient or what remains.
- `./spec-dock/scripts/spec-dock validate`: SpecDock projection / metadata consistency.
- `./spec-dock/scripts/spec-dock assurance verify`: assurance state / grade evidence consistency.

Manual:

- Read Initiative / Epic templates and scope-layering / workflow docs for Japanese-first and authority boundary.
- Confirm `iss-00276` canonical `design.md` / `plan.md` no longer contain pre-start draft body except approved composed content after S01.
- Inspect `git status --short` before commit and PR to prevent raw manual files from being staged.

Reviewer:

- `qa-reviewer` decides test sufficiency and full-suite gap.
- `code-reviewer` reviews integrated implementation diff when material code / runtime / tests / scaffold changes exist.
- `spec-reviewer` reviews requirement / design / plan / report / docs alignment and Japanese-first policy.

## 7. Review Gates

Required gates:

- S01 planning `spec-reviewer`: validates canonical `design.md` / `plan.md` readiness after adoption.
- S04 final `qa-reviewer`: validates S02/S03 coverage and missing integration test risk.
- S04 issue-wide `code-reviewer`: required if implementation diff is large or includes code / runtime / tests / scaffold behavior; otherwise record explicit not-applicable rationale.
- S04/S05 final `spec-reviewer`: validates Epic and Issue fulfillment, report evidence, Japanese-first authoring, and PR description readiness.
- S07 PR observation: `github-pr-merge-preparer` evidence for PR Delivery Gate and Merge Preparation Gate.

Required report destinations:

- Evidence Adoption Ledger for pre-start seed and this draft adoption.
- Reviewer Gate Status for every reviewer attempt and re-review.
- Step Contract Closure / Test Contract Closure / Closure Coverage for `C276-001..016`.
- PR Delivery Gate and Merge Preparation Gate for PR evidence.

## 8. Rollback / Compatibility

Rollback:

- If S02/S04 repair introduces regressions, revert or narrow the repair at the step / commit boundary rather than hiding failures in PR description.
- If PR split becomes necessary, stop before PR creation, amend `epic-00270/plan.md`, rerun fresh `spec-reviewer`, and record the decision in `report.md`.
- If `github-pr-merge-preparer` cannot observe required PR state, record blocker / next action and do not claim merge-prepared.

Compatibility:

- No database migration is expected.
- Existing managed repos should receive provider scaffold changes through normal `spec-dock update`; final gate must not reintroduce DDD / EDA mandatory assumptions.
- Issue-local draft artifacts remain evidence-only; canonical docs gain authority only through main orchestrator adoption and fresh review.

## 9. Docs Impact

Expected docs impact is report / PR-description heavy.

- `iss-00276/report.md`: required evidence ledger for all S00-S07 gates.
- `epic-00270/report.md`: final E-AC status, integrated validation, manual summary, reviewer result, PR readiness.
- PR body: delivery narrative and boundary explanation.

Potential docs repairs:

- If manual read-through finds stale or contradictory shipped docs / templates / skills, use `doc-writer` or record a valid Parent Implementation Exception before editing.
- If docs repair changes Epic contract or PR boundary, treat it as plan amendment and fresh review, not as final-gate cleanup.

## 10. Final Quality Gate

Final exit contract:

- `C276-001..016` are closed in report evidence or explicitly blocked / incomplete with next action.
- `uv run pytest tests/unit`, `uv run pytest tests/cli_runtime`, `./spec-dock/scripts/spec-dock validate`, and `./spec-dock/scripts/spec-dock assurance verify` have recorded results.
- Full `uv run pytest` is either recorded or intentionally deferred with reason and QA acceptance evidence.
- Manual dogfooding summary and raw artifact hygiene are recorded.
- Final `qa-reviewer`, applicable issue-wide `code-reviewer`, and final `spec-reviewer` are fresh and passed, or the Issue is not reported complete.
- Epic report is updated with final evidence.
- Final commit exists and post-commit `git status --short` is clean except intentionally untracked external items documented outside commit scope.
- `github-pr-merge-preparer` has produced PR Delivery Gate and Merge Preparation Gate evidence.
- PR merge and GitHub issue close remain outside this Issue unless the user explicitly instructs them.

## 11. Plan Blockers

Current blockers identified from source reading:

- None that prevent drafting this artifact.

Execution blockers to check at S00:

- `iss-00275` report currently says Issue completion and PR creation are not yet done, while Epic report may lag behind current active state. S00 must verify live `deps check iss-00276`, active state, and issue reports before PR work.
- `iss-00271..iss-00274` reports include old `Issue完了: 未実施` wording in places despite Epic report saying completed. S00 must reconcile actual lifecycle/projection evidence and not rely on a single stale line.
- Current `iss-00276` design is treated as placeholder/template by user instruction. S01 must produce substantive canonical design before canonical plan adoption.

Clarification candidates for main orchestrator:

- If full `uv run pytest` is slow or flaky, should the final gate require it before PR, or can `qa-reviewer` accept focused + partial full-suite evidence with explicit risk?
- If `github-pr-merge-preparer` reports merge-prepared but non-required checks are unavailable due to GitHub permission limits, what waiver evidence should be recorded?

## 12. Integration Notes for Main Orchestrator

Suggested adoption steps:

1. Record this artifact in `iss-00276/report.md` Delegated Draft Evidence with `adoption_status: unreviewed` until inspected.
2. If adopting, map sections 2-10 into canonical `plan.md` after `assurance compose` has materialized the appropriate profile template.
3. Update `report.md` EAL with adopted / partially_adopted / rejected rows for:
   - pre-start draft-plan seed `20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md`
   - this implementation-planner draft
4. Run fresh `spec-reviewer`; do not treat this draft as reviewer pass or implementation readiness.
5. Keep S00 as a hard audit gate because reports and projection may differ after recent issue relay work.

Leaf evidence used:

- None. This draft used only local source reading and no depth=2 leaf delegation.

Forbidden actions avoided:

- No canonical docs were edited.
- No implementation files, tests, package/config files, `.agents`, `.codex`, `.github`, secrets, or GitHub state were edited.
- No reviewer pass, phase promotion, issue readiness, issue finish, PR readiness, PR merge, or user-dialogue ownership is claimed.

Unresolved design gaps:

- Current Issue design requires main orchestrator composition and review before canonical plan adoption. No substantive final-quality design authority is claimed by this draft.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

## Ledger Note

No material implementation decisions beyond the approved plan.
