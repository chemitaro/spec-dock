---
created_by_role: implementation-planner
scope_id: iss-00254
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/templates/issue/report.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - tests/unit/domain/test_workflow_state.py
  - tests/cli_runtime/test_workflow.py
  - tests/cli_runtime/test_validate.py
  - tests/cli_runtime/test_issue_lifecycle.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# G3 実装計画ドラフト: Grade Aware Spec Review And Evidence Gates

この文書は `iss-00254` の delegated implementation-plan draft であり、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を編集しない。採用可否は main orchestrator が Evidence Adoption Ledger と fresh `spec-reviewer` gate で判断する。

## 1. Plan Summary

G3 は、Epic #224 の `E-RQ-022` / `E-AC-022` のうち、grade-aware authoring evidence を phase promotion と issue readiness へ接続する slice として実装する。既存の `workflow_spec_authoring.md`、Issue `report.md` template、`domain/authority.py` の Evidence Adoption Ledger gate、`application/workflow.py` の fail-closed readiness preflight を利用し、次を観測可能にする。

- fresh `spec-reviewer` pass が Lite を含む全 grade の phase promotion / final handoff で必須である。
- delegated draft adoption は `report.md` の Evidence Adoption Ledger と Delegated Draft Evidence に残る。
- Standard は specialist 使用または skip reason、Strict / Critical は specialist evidence または unavailable / manual fallback evidence がない限り promotion evidence として扱えない。
- stale draft、stale reviewer、missing EAL / missing grade evidence は `workflow status` / `guidance issue-execution` で readiness block reason になる。
- Epic branch baton を維持し、`iss-00254` 単独 PR は作らない。M99 / S99 は `iss-00255` へ渡せる local closure checkpoint とする。

## 2. Requirement / Design Traceability

Source revisions observed:

- `spec-dock/active/issue/requirement.md`: `iss-00254`, Issue Grade `strict`, 最終更新 `2026-07-01`, AC-001 から AC-006。
- `spec-dock/active/issue/design.md`: `iss-00254`, Issue Grade `strict`, 最終更新 `2026-07-01`, Gate model と配置候補。
- `spec-dock/active/issue/plan.md`: `iss-00254`, G3 milestones M0 から M99, Epic branch baton / no per-issue PR policy。
- `spec-dock/active/epic/*`: `E-RQ-022`, `E-AC-022`, corrective tranche `G3`。

Traceability:

| Closure ID | Requirement / design evidence | Planned closure |
|---|---|---|
| `slc-g3-001` | AC-001, design Fresh Spec Review Gate | all grade docs/templates require fresh `spec-reviewer`; stale / missing reviewer is block |
| `slc-g3-002` | AC-002, AC-006, design Draft Adoption Gate | EAL + Delegated Draft Evidence fields and no self-claim wording are provider template authority |
| `slc-g3-003` | AC-003, design stale draft / stale reviewer fail path | readiness preflight blocks stale draft / stale reviewer evidence |
| `slc-g3-004` | AC-004, design Grade Evidence Gate | Standard skip reason and Strict / Critical fallback evidence are report evidence contract |
| `slc-g3-005` | AC-005, design Readiness Evidence Gate | `workflow status` / `guidance issue-execution` exposes missing evidence block reasons aligned with R0 |
| `slc-g3-006` | Epic branch baton in issue plan | no per-issue PR; report records local checkpoint and baton to `iss-00255` |

## 3. Milestones

| Milestone | Purpose | Closure IDs | Evidence destination |
|---|---|---|---|
| M0 Baseline | current docs/templates/runtime/tests を確認し、既存 EAL / readiness / lifecycle gates を固定する | `slc-g3-001` to `slc-g3-005` | `report.md` Spec Interpretation / Decision Ledger |
| M1 Report evidence contract | `templates/issue/report.md` と必要な docs に grade evidence、fresh reviewer、fallback evidence destination を明示する | `slc-g3-001`, `slc-g3-002`, `slc-g3-004` | EAL, Delegated Draft Evidence, Spec Authoring Gate, Reviewer Gate Status |
| M2 Runtime readiness hook | `application/workflow.py` の readiness preflight に report evidence gate を追加し、missing / stale evidence を block する | `slc-g3-003`, `slc-g3-005` | Step Contract Closure, Test Contract Closure |
| M3 Regression tests | docs/template assertions、domain/CLI readiness tests、EAL lifecycle tests を追加または更新する | all closure IDs | Test Contract Closure, Closure Coverage |
| M90 Provider / dogfooding parity | provider assets と dogfooding mirror の差分意図を確認する | all closure IDs | Docs Impact Resolution |
| M95 Fresh spec review | canonical artifact へ採用後、fresh `spec-reviewer` で requirement/design/plan/report/docs alignment を確認する | `slc-g3-001`, `slc-g3-006` | Final Spec Review Gate |
| M99 Baton checkpoint | final local commit候補を閉じ、`iss-00255` へ同一 Epic branch HEAD を渡す | `slc-g3-006` | Milestone / Commit Candidate Gate, Final Commit external evidence |

## 4. Dependency-Derived Execution Order

1. M0: `workflow_spec_authoring.md`、`workflow_issue.md`、`templates/issue/report.md`、`application/workflow.py`、`domain/authority.py`、`issue_lifecycle.py` の現状を固定する。
2. M1: docs/templates で evidence contract を先に明示する。runtime block reason はこの wording を authority として参照する。
3. M2: readiness hook を実装する。既存の placeholder classifier を広げるのではなく、report evidence gate の missing / stale / unresolved state を別 reason code として追加する。
4. M3: negative tests を先に置き、missing EAL、stale EAL、stale reviewer、Strict specialist evidence missing が ready にならないことを確認する。
5. M90: provider source を dogfooding mirror に反映または意図的に未反映として記録する。
6. M95: `spec-reviewer` を fresh に実行する。draft や previous reviewer verdict を pass として再利用しない。
7. M99: no per-issue PR のまま local checkpoint を閉じ、Epic branch baton を `iss-00255` に渡す。

## 5. Issue / Step Slicing

### S01 Evidence Contract Wording

- Behavior goal: report evidence contract で fresh reviewer、EAL、grade-specific specialist / fallback evidence、no self-claim を一箇所から追える。
- Allowed paths: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`, `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`, `src/spec_dock/assets/spec_dock/templates/issue/report.md`, 必要最小の provider-side profile plan/design templates。
- Forbidden changes: canonical active docs、runtime behavior、tests、`.agents`、`.codex`、`.github`。
- Concrete tests:
  - `tc-s01-001` inspection: issue report template contains `Evidence Adoption Ledger`, `Delegated Draft Evidence`, `Reviewer Gate Status`, `Final Spec Review Gate`, and grade evidence wording.
  - `tc-s01-002` structural: provider / dogfooding template parity remains intentional.
- Report destination: Docs Impact Resolution, Spec Authoring Gate, EAL adoption row if delegated evidence is used.
- Reviewer focus: `spec-reviewer` docs/spec alignment.

### S02 Runtime Report Evidence Gate

- Behavior goal: execution readiness does not pass when report evidence required by grade is missing, stale, or reviewer evidence is not fresh passed.
- Allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`, `domain/authority.py` if parser / gate helpers are reused, presentation output only if block reason needs readable details.
- Forbidden changes: raw placeholder detector expansion unrelated to evidence, draft routing G2 behavior, lifecycle close semantics beyond existing EAL gate, GitHub PR policy.
- Concrete tests:
  - `tc-s02-001` negative: valid requirement/design/plan but missing final fresh `spec-reviewer` evidence yields blocked readiness.
  - `tc-s02-002` negative: EAL row with `stale` / `blocked` remains blocking for readiness and validate / finish gates.
  - `tc-s02-003` negative: Strict issue with delegated specialist unavailable but no manual fallback evidence is blocked.
  - `tc-s02-004` positive: explicit not-used / skip reason for Standard, or valid fallback evidence for Strict, passes only when all other readiness checks pass.
- Report destination: Step Contract Closure, Test Contract Closure, Reviewer Gate Status.
- Reviewer focus: `code-reviewer` for runtime behavior.

### S03 Regression Coverage

- Behavior goal: tests prove docs/template evidence and runtime readiness are coupled.
- Allowed paths: `tests/unit/domain/test_workflow_state.py`, `tests/cli_runtime/test_workflow.py`, `tests/cli_runtime/test_validate.py`, `tests/cli_runtime/test_issue_lifecycle.py`, targeted installer/template parity tests if template assets change.
- Concrete tests:
  - `tc-s03-001` CLI: `guidance issue-execution` emits blocked state and reason code for missing reviewer evidence.
  - `tc-s03-002` CLI: `workflow status --format json` exposes evidence block details without claiming implementation readiness.
  - `tc-s03-003` validate/lifecycle: unresolved EAL remains blocked before `issue finish`.
  - `tc-s03-004` template: generated Issue report includes grade / reviewer / fallback evidence destinations.
- Report destination: Test Contract Closure, Closure Coverage, Discovered Tests.
- Reviewer focus: `qa-reviewer` for coverage adequacy, `code-reviewer` for behavior.

### S90 Docs Impact Resolution

- Behavior goal: provider docs/templates and dogfooding mirror are either synchronized or explicitly recorded as intentionally pending.
- Allowed paths: docs/templates affected by S01 and generated mirror if standard sync/update workflow requires it.
- Report destination: Docs Impact Resolution.
- Reviewer focus: `spec-reviewer`.

### S99 Final Quality Gate / Baton

- Behavior goal: no per-issue PR; local Epic branch remains ready for `iss-00255`.
- Required gates: focused tests, `./spec-dock/scripts/spec-dock validate`, final `qa-reviewer`, issue-wide `code-reviewer`, final fresh `spec-reviewer`, clean worktree after commit candidate.
- Report destination: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Milestone / Commit Candidate Gate, Final Commit external evidence.

## 6. Test Strategy Mapping

Primary commands:

```bash
uv run pytest tests/unit/domain/test_workflow_state.py
uv run pytest tests/cli_runtime/test_workflow.py
uv run pytest tests/cli_runtime/test_validate.py -k evidence_adoption_ledger
uv run pytest tests/cli_runtime/test_issue_lifecycle.py -k "Evidence Adoption Ledger or delegated"
uv run pytest tests/cli_runtime/test_new.py -k "profile_drafts or authorized_profile"
./spec-dock/scripts/spec-dock validate
```

Conditional commands:

- If provider template scaffolding changes: `uv run pytest tests/unit/infra/test_init_update.py -k report`
- If generated dogfooding mirror is refreshed: run `./spec-dock/scripts/spec-dock sync --no-github` and inspect provider / mirror parity.
- If block reason presentation changes: add `tests/cli_runtime/test_workflow.py` JSON and Markdown assertions.

Red / alternative evidence expectation:

- Runtime behavior uses red-first negative CLI tests for missing / stale evidence.
- Docs-only wording uses structural assertion or inspection evidence; do not invent code tests for purely wording-only changes.

## 7. Review Gates

- Per-step docs/template gate: fresh `spec-reviewer` pass for docs/spec alignment.
- Per-step runtime gate: `code-reviewer` pass for readiness behavior and parser scope.
- Test sufficiency gate: `qa-reviewer` pass before S99 if new evidence block matrix or smoke coverage is added.
- Final gate: final `spec-reviewer` must review canonical requirement/design/plan/report plus implementation/tests/docs after EAL adoption. Draft review, stale review, waiver, provisional verdict, or reviewer unavailable state does not satisfy this gate.
- Reviewer evidence destination: `report.md` Reviewer Gate Status and Final Spec Review Gate. For phase promotion, also Spec Authoring Gate.

## 8. Rollback / Compatibility

- Rollback path: revert G3 docs/templates/runtime/test changes as one local Epic-branch checkpoint before PR publication.
- Compatibility: existing historical delegated authoring artifacts and manifest-heavy evidence remain grandfathered. Do not rename, delete, or validation-fail them merely because current G3 evidence is lighter.
- Readiness behavior must be fail-closed for new missing / stale evidence, but should avoid broad false positives by parsing only well-defined report ledger sections.
- Strict-legacy path may continue, but cannot bypass unresolved EAL or stale delegated evidence where current lifecycle gates already block.
- Manual fallback is not success by itself. It is acceptable only as recorded evidence with reason, scope, checked sources, reviewer handling, and non-blocking rationale.

## 9. Docs Impact

Expected docs/template impact:

- `workflow_spec_authoring.md`: ensure grade matrix and report evidence gate wording state that fresh `spec-reviewer` is never omitted and delegated drafts are evidence only.
- `workflow_issue.md`: ensure readiness / completion policy names missing reviewer evidence, stale reviewer, missing adoption evidence, and grade-specific fallback evidence as incomplete / blocked.
- `templates/issue/report.md`: ensure Issue report scaffold has explicit slots for EAL, delegated draft evidence, specialist use/skip/fallback, Reviewer Gate Status, Final Spec Review Gate, and closure coverage.
- `docs/authoring/issue-plan.md`: only update if step/report evidence destination semantics need sharper wording.
- Dogfooding mirror under `spec-dock/`: inspect after provider-side changes; refresh only through normal scaffold/update/sync path if required by repo workflow.

No docs impact claims should be marked `none` unless the report records inspection evidence and `spec-reviewer` confirms no docs update is required.

## 10. Final Quality Gate

S99 exit conditions:

- All `slc-g3-*` closure IDs are closed in Step Contract Closure, Test Contract Closure, and Closure Coverage.
- `workflow status` and `guidance issue-execution` block missing / stale evidence with explicit reason codes and do not report `may_execute_approved_plan: true`.
- Required commands above pass or have non-success evidence recorded as blocked / incomplete.
- `report.md` records EAL adoption for this delegated draft if adopted, plus delegated evidence path and diff guard result.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and fresh `spec-reviewer` pass.
- No per-issue PR is created. Final response / external delivery evidence records the local checkpoint and baton to `iss-00255`.

## 11. Plan Blockers

- Current canonical `requirement.md` / `design.md` / `plan.md` are still draft text; this delegated draft cannot authorize implementation by itself.
- If main orchestrator cannot run fresh `spec-reviewer`, phase promotion and final readiness remain incomplete.
- If runtime lacks a stable parser for grade-specific report evidence, implement the smallest explicit parser rather than widening placeholder detection.
- If docs/template wording and runtime block reason disagree, stop and amend design/plan before implementation.

Unresolved design gaps: none identified that block drafting. The main orchestrator must still decide adoption and exact parser contract.

## 12. Integration Notes for Main Orchestrator

- Changed discussion artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00254-add-grade-aware-spec-review-and-evidence-gates/discussions/20260630t180152z-disc-g3-implementation-plan-draft.md`
- Source requirement/design revisions: active issue requirement/design/plan observed with `iss-00254`, Issue Grade `strict`, 最終更新 `2026-07-01`; parent Epic requirement/design/plan observed with `E-RQ-022`, `E-AC-022`, G3 tranche.
- Lightweight provenance summary: created by `implementation-planner`, source paths listed in frontmatter, intended targets are canonical `plan.md` and `report.md`, adoption status remains `unreviewed`, reflected targets remain empty, diff guard remains `pending`.
- Leaf evidence used: none. No depth=2 leaf delegation was invoked.
- Forbidden actions avoided: no canonical doc edit, no source code edit, no test edit, no package/config edit, no `.agents` / `.codex` / `.github` edit, no GitHub mutation, no phase promotion, no reviewer-pass claim, no implementation-readiness claim, no user-dialogue ownership.
- Report adoption note candidate: add an EAL row for this draft only if main orchestrator adopts it; until then it is proposal evidence.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
