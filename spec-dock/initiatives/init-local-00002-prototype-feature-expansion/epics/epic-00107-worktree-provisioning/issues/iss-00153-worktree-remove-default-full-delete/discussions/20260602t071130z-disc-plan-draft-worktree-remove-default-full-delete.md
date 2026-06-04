---
created_by_role: implementation-planner
scope_id: iss-00153
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - tests/cli_runtime/test_worktree.py
  - src/spec_dock/assets/spec_dock/docs/reference_worktree.md
  - spec-dock/docs/reference_worktree.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending_or_not_run
---

# Plan Draft: iss-00153 Default Full Delete For Worktree Remove

## 1. Plan Summary

This draft proposes an executable issue plan for turning `spec-dock worktree remove <target>` into default full delete for eligible linked worktrees while preserving hard blockers, target-only cleanup, output schema, branch retention, and `--force` as a compatibility input.

Covered requirement IDs:

- AC-001: untracked residue is removed by default remove.
- AC-002: tracked modification is removed by default remove.
- AC-003: `--force` remains accepted and matches default full-delete behavior.
- AC-004: hard blockers are not bypassed by the new default or by `--force`.
- AC-005: provider docs, dogfooding docs, CLI help, and tests describe the new contract.
- EC-001: Git refusal, including locked worktree cases beyond supported force depth, remains failure with no filesystem cleanup.
- EC-002: post-remove cleanup failure remains distinguishable and target-only.
- EC-003: unmanaged linked worktree remains diagnostic-only and removable when otherwise eligible.

Assumptions:

- `requirement.md` and `design.md` are approved and current as of 2026-06-02.
- No `WorktreeRemoveRequest`, `GitGateway`, or success JSON schema rename is needed in this issue.
- `src/spec_dock/assets/spec_dock/...` is the provider-side source of truth; `spec-dock/docs/reference_worktree.md` is a dogfooding parity artifact.

## 2. Requirement / Design Traceability

| Requirement / edge | Design source | Planned closure rows | Owner step |
|---|---|---|---|
| AC-001 untracked default full delete | `application.worktree` calls Git force-equivalent remove after guards | `ci-001`, `ci-009` | S01 |
| AC-002 tracked modification default full delete | add tracked-modification runtime test | `ci-002`, `ci-009` | S02 |
| AC-003 `--force` compatibility | parser keeps `--force`; application ignores it for strength selection | `ci-003`, `ci-009` | S02 |
| AC-004 hard blockers preserved | `_non_bypassable_remove_blockers`, refreshed record, containment guard remain before Git remove | `ci-004` | S03 |
| AC-005 docs/help/tests updated | provider docs, dogfooding docs, CLI help describe default full delete | `ci-005` | S90 |
| EC-001 Git refusal no cleanup | existing `git_worktree_remove_failed` path remains before filesystem cleanup | `ci-006` | S03 |
| EC-002 cleanup failure target-only | existing `post_remove_cleanup_failed` path remains after Git success only | `ci-007` | S03 |
| EC-003 unmanaged is diagnostic-only | unmanaged removal remains eligible if no hard blocker | `ci-008` | S03 |

## 3. Milestones

- M1: Runtime full-delete default is observable for dirty/untracked and tracked modifications.
- M2: Compatibility and guardrails are preserved: `--force`, hard blockers, branch retention, Git-first cleanup, target-only cleanup, and unmanaged removal.
- M3: Docs and CLI help align with the new destructive default.
- M4: Final quality gates confirm test sufficiency, integrated code quality, and spec/docs/report alignment.

## 4. Dependency-Derived Execution Order

1. S01 establishes the vertical tracer bullet: a public CLI test for untracked residue default success, plus the smallest application-layer change from `force=req.force` to force-equivalent default.
2. S02 broadens the runtime contract to tracked modifications and `--force` compatibility once the default full-delete path exists.
3. S03 verifies the unchanged guardrails and error paths under the new default, using existing fake gateway tests and focused CLI coverage.
4. S90 updates CLI help wording and provider/dogfooding reference docs after runtime behavior is fixed.
5. S99 runs final QA, issue-wide code review, final spec review, sync/validate checks, and report ledger closure.

## 5. Issue / Step Slicing

### Spec-Locked Closure Index

| id | spec link | observable input/state | locked expectation | bug class guarded | required | evidence level | owner step |
|---|---|---|---|---|---|---|---|
| ci-001 | AC-001 | linked worktree with untracked `cache.tmp`; `worktree remove dirty --json` | exit 0; record removed; path removed; `branch_deleted=false`; branch remains | default remove still fails on untracked residue | yes | red-required | S01 |
| ci-002 | AC-002 | linked worktree with tracked file modification; `worktree remove modified --json` | exit 0; record removed; path removed; `branch_deleted=false`; branch remains | tracked dirty state not covered by untracked-only test | yes | red-required | S02 |
| ci-003 | AC-003 | dirty linked worktree; `worktree remove <target> --force --json` | accepted and same success contract as default | backward compatibility break for scripts using `--force` | yes | red-required or characterization-update | S02 |
| ci-004 | AC-004 | main/current/bare/missing/record-missing/containment-blocked target | fail with existing blocker; Git remove not called; `--force` does not bypass | destructive guard bypass after default force change | yes | covered-existing plus targeted update | S03 |
| ci-005 | AC-005 | CLI help and provider/dogfooding `reference_worktree.md` | no wording says `--force` is required for dirty/untracked full delete; docs say default full delete and compatibility input | operator misreads destructive default | yes | inspect-only plus help assertion | S90 |
| ci-006 | EC-001 | Git refuses force-equivalent remove, including locked worktree when Git does not allow it | `git_worktree_remove_failed`; target cleanup is not called | filesystem cleanup after failed Git remove | yes | covered-existing plus assertion update | S03 |
| ci-007 | EC-002 | Git remove succeeds but target cleanup fails | `post_remove_cleanup_failed`; `removed_record=true`; `removed_directory=false`; cleanup remains target-only | cleanup failure hidden or parent cleanup widened | yes | covered-existing plus assertion update | S03 |
| ci-008 | EC-003 | unmanaged linked worktree with no hard blocker | default remove succeeds; diagnostic fields preserved; branch remains | unmanaged misclassified as blocker | yes | characterization-update | S03 |
| ci-009 | AC-001, AC-002, AC-003 | success JSON/text for default and `--force` removal | output schema unchanged: `removed_record`, `removed_directory`, `branch_deleted=false`, resolved target diagnostics | schema drift while changing behavior | yes | covered-existing plus focused assertions | S01/S02/S03 |

### S01 Runtime Default Full Delete For Untracked Residue

- Behavior goal: `worktree remove <target>` deletes an eligible linked worktree with untracked files without requiring `--force`.
- Depends on: approved `requirement.md` and `design.md`.
- Unblocks: S02 compatibility/dirty variants and S03 guardrail verification.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Scope: application remove call and the existing dirty/untracked CLI test.
  - Test obligation: AC-001 and success output/branch retention.
  - Red evidence requirement: `red-required`; update the old `test_worktree_remove_dirty_default_fails_and_force_removes_directory` expectation so it fails on current implementation.
  - Green verification: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_remove_dirty_default_fails_and_force_removes_directory -v` after renaming/updating the test.
  - Refactor guardrail: do not rename request/port/schema; do not change `git_cli.py` unless a test proves the existing `force=True` mapping is insufficient.
  - Amendment trigger: any need to add a preservation mode such as `--keep-untracked`, delete branches, or broaden cleanup target requires design/plan amendment.
- Delegation contract:
  - delegated role: `dev-coder`
  - input docs: active issue `requirement.md`, `design.md`, this plan, `workflow_issue.md`, target source/test files.
  - allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`, `tests/cli_runtime/test_worktree.py`.
  - forbidden changes: docs, CLI help, `git_cli.py` signature, branch deletion, `WorktreeRemoveRequest` rename, cleanup outside resolved target, canonical spec docs.
  - acceptance criteria: closure `ci-001` and `ci-009` pass.
  - required tests: focused updated dirty/untracked CLI test.
  - reviewer focus: `code-reviewer` checks default force-equivalent call, output schema stability, and no guard bypass.
  - stop conditions: Git behavior differs enough that `force=True` does not remove untracked residue; target cleanup must widen beyond resolved target; schema change appears necessary.
  - output required: changed files, red/green command results, closure IDs satisfied, unresolved risks, `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Concrete test case cards:
  - `tc-s01-001` acceptance: untracked residue default remove succeeds
    - 前提: temp Git repo に `worktree create dirty` で linked worktree があり、`cache.tmp` が Git 管理外で存在する。
    - 操作: `spec-dock worktree remove dirty --json` を実行する。
    - 期待結果: exit code 0、`removed_record=true`、`removed_directory=true`、`branch_deleted=false`、target path deleted、Git worktree record removed、branch remains。
    - 失敗検出: default remove が旧 contract のまま `git_worktree_remove_failed` になる回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_worktree.py` の dirty remove test を red-first 更新する。
    - 関連 closure id: `ci-001`, `ci-009`
  - `tc-s01-002` application: eligible default request calls GitGateway with force-equivalent strength
    - 前提: fake gateway を使う application-level remove test で `WorktreeRemoveRequest(target="leftover")` を渡す。
    - 操作: `app_worktree.worktree_remove(...)` を実行する。
    - 期待結果: `git_gateway.remove_calls` は `(worktree_path, True)` になる。
    - 失敗検出: application layer が `req.force=False` をそのまま GitGateway に渡す回帰を検出する。
    - 検証方法: existing cleanup test の gateway force assertion を更新する。
    - 関連 closure id: `ci-001`
- Step closure contract:
  - Close only when `ci-001` and S01-owned `ci-009` observations pass, report records red/green evidence, per-step `code-reviewer` is passed, and step commit or approved-no-op evidence is recorded by the orchestrator.
- Report evidence destination:
  - `TDD / Red / Green / Refactor Evidence`
  - `Step Contract Closure`
  - `Test Contract Closure`
  - `Implementation Delegation Gate`
  - `Delegated Worker Evidence`
  - `Reviewer Gate Status`
  - `Step Commit Gate`

### S02 Tracked Modification And `--force` Compatibility

- Behavior goal: tracked modifications are also full-deleted by default, and existing `--force` invocations remain accepted with the same contract.
- Depends on: S01.
- Unblocks: S03 guardrail regression and S90 docs wording.
- Target files:
  - `tests/cli_runtime/test_worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` only if S01 was insufficient.
- Planned contract:
  - Scope: runtime tests for AC-002 and AC-003; minimal implementation only if tests expose a gap.
  - Test obligation: tracked dirty state, compatibility input, branch retention, unchanged JSON fields.
  - Red evidence requirement: `red-required` for tracked modification default success; `characterization-update` for `--force` compatibility if existing dirty force test is split.
  - Green verification: focused tests for tracked default remove and `--force` compatibility, then `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v` if fixture interactions are broad.
  - Refactor guardrail: do not remove `--force` parser support; do not introduce a new strength enum.
  - Amendment trigger: if locked worktree behavior is interpreted as requiring a new force depth option, return to design.
- Delegation contract:
  - delegated role: `dev-coder`
  - input docs: active issue `requirement.md`, `design.md`, this plan, S01 result, target tests/source.
  - allowed paths: `tests/cli_runtime/test_worktree.py`; `application/worktree.py` only for minimal follow-up.
  - forbidden changes: deleting `--force`, changing `git_cli.remove_worktree` signature, branch deletion, docs/help edits.
  - acceptance criteria: closure `ci-002`, `ci-003`, S02-owned `ci-009` pass.
  - required tests: tracked modification default success and `--force` compatibility success.
  - reviewer focus: `code-reviewer` checks test sensitivity, compatibility coverage, and no over-broad API changes.
  - stop conditions: compatibility input cannot be retained without parser contract change; tracked modification cannot be represented in temp repo fixture.
  - output required: changed files, commands, closure IDs, compatibility notes, `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Concrete test case cards:
  - `tc-s02-001` acceptance: tracked modification default remove succeeds
    - 前提: temp Git repo の linked worktree に committed tracked file があり、その file を未コミット変更する。
    - 操作: `spec-dock worktree remove modified --json` を実行する。
    - 期待結果: exit code 0、Git worktree record removed、target path deleted、`branch_deleted=false`、branch remains。
    - 失敗検出: untracked residue だけ通り、tracked dirty state が Git refusal になる回帰を検出する。
    - 検証方法: `tests/cli_runtime/test_worktree.py` に tracked modification default remove test を追加する。
    - 関連 closure id: `ci-002`, `ci-009`
  - `tc-s02-002` compatibility: `--force` remains accepted
    - 前提: dirty linked worktree があり、default remove と同じ eligible target 条件を満たす。
    - 操作: `spec-dock worktree remove <target> --force --json` を実行する。
    - 期待結果: default と同じ success contract を満たし、`--force` 指定による schema 差分はない。
    - 失敗検出: `--force` parser 削除、または `--force` path だけ別挙動になる互換回帰を検出する。
    - 検証方法: existing force portion を独立 test または updated dirty test の second case として残す。
    - 関連 closure id: `ci-003`, `ci-009`
- Step closure contract:
  - Close only when `ci-002`, `ci-003`, and S02-owned `ci-009` pass, report records evidence, per-step `code-reviewer` is passed, and step commit or approved-no-op evidence is recorded.
- Report evidence destination:
  - `TDD / Red / Green / Refactor Evidence`
  - `Discovered Tests`
  - `Step Contract Closure`
  - `Test Contract Closure`
  - `Implementation Delegation Gate`
  - `Delegated Worker Evidence`
  - `Reviewer Gate Status`
  - `Step Commit Gate`

### S03 Guardrail, Error Path, And Diagnostic Preservation

- Behavior goal: default full delete does not weaken hard blockers, Git-first semantics, target-only cleanup, unmanaged diagnostic behavior, or branch retention.
- Depends on: S01 and S02.
- Unblocks: S90 docs wording and S99 final quality gate.
- Target files:
  - `tests/cli_runtime/test_worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` only for guard-preserving fixes.
- Planned contract:
  - Scope: update or add tests for AC-004, EC-001, EC-002, EC-003 under the new default.
  - Test obligation: negative/error paths and invariants most likely to regress when application always passes `force=True`.
  - Red evidence requirement: `covered-existing` for existing hard blocker/cleanup tests, with assertion updates where the expected gateway force flag changes; `characterization-update` for unmanaged default remove without `--force`.
  - Green verification: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`.
  - Refactor guardrail: do not collapse blocker resolution into infra; do not remove refreshed record check or containment guard.
  - Amendment trigger: any required cleanup outside resolved target, branch deletion, or hard-blocker bypass is a design gap.
- Delegation contract:
  - delegated role: `dev-coder`
  - input docs: active issue `requirement.md`, `design.md`, this plan, S01/S02 results, target tests/source.
  - allowed paths: `tests/cli_runtime/test_worktree.py`; `application/worktree.py` only for guard-preserving fixes.
  - forbidden changes: docs/help, `git_cli.py` force-depth changes unless explicitly justified, branch deletion, parent/namespace/root cleanup, canonical spec docs.
  - acceptance criteria: `ci-004`, `ci-006`, `ci-007`, `ci-008`, remaining `ci-009` pass.
  - required tests: hard blocker no-call assertions, Git failure no cleanup, post-remove cleanup failure fields, unmanaged default removal.
  - reviewer focus: `code-reviewer` checks destructive safety, containment, error code stability, and output schema stability.
  - stop conditions: existing fake tests cannot distinguish pre-Git blockers; Git version makes locked test unstable beyond guarded skip; fix needs infra signature/API changes.
  - output required: changed files, verification command result, closure IDs, unresolved Git-version risks, `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Concrete test case cards:
  - `tc-s03-001` negative: hard blockers stop before Git remove
    - 前提: fake gateway subcases for main, current, bare, missing path, record missing, and containment-protected targets.
    - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(...))` with default request and, where existing coverage uses it, `force=True`.
    - 期待結果: `remove_blocked` with expected blocker and `git_gateway.remove_calls == []`.
    - 失敗検出: default full delete accidentally bypasses application guard and calls Git remove.
    - 検証方法: existing hard-blocker tests are updated or supplemented for default request semantics.
    - 関連 closure id: `ci-004`
  - `tc-s03-002` negative: Git refusal does not cleanup target
    - 前提: fake GitGateway raises `RuntimeError("git refused")` from `remove_worktree`; filesystem gateway raises if cleanup is touched.
    - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(target="leftover"))` を実行する。
    - 期待結果: `git_worktree_remove_failed`; filesystem `path_exists` and `remove_target` are not called.
    - 失敗検出: Git failure after default force change triggers filesystem cleanup.
    - 検証方法: existing Git failure test, with expected force flag adjusted only if asserted.
    - 関連 closure id: `ci-006`
  - `tc-s03-003` negative: post-remove cleanup failure remains distinguishable and target-only
    - 前提: GitGateway succeeds; filesystem gateway reports target exists and then raises `cleanup denied`.
    - 操作: `app_worktree.worktree_remove(WorktreeRemoveRequest(target="leftover"))` を実行する。
    - 期待結果: `post_remove_cleanup_failed`, `removed_record=true`, `removed_directory=false`, cleanup called only for resolved target path.
    - 失敗検出: cleanup error is hidden, schema changes, or parent/namespace cleanup is attempted.
    - 検証方法: existing cleanup failure and target-only cleanup tests with gateway force assertion updated to `True`.
    - 関連 closure id: `ci-007`
  - `tc-s03-004` diagnostic: unmanaged linked worktree default remove succeeds
    - 前提: temp Git repo has external linked worktree created by raw `git worktree add`, no hard blocker.
    - 操作: `spec-dock worktree remove <external-basename> --json` without `--force`.
    - 期待結果: success, `removed_record=true`, `removed_directory=true`, `branch_deleted=false`, diagnostic fields remain present.
    - 失敗検出: unmanaged is incorrectly treated as a blocker or only `--force` path removes it.
    - 検証方法: update existing unmanaged remove assertion that currently uses `--force`.
    - 関連 closure id: `ci-008`, `ci-009`
- Step closure contract:
  - Close only when `ci-004`, `ci-006`, `ci-007`, `ci-008`, and remaining `ci-009` pass, report records evidence, per-step `code-reviewer` is passed, and step commit or approved-no-op evidence is recorded.
- Report evidence destination:
  - `TDD / Red / Green / Refactor Evidence`
  - `Step Contract Closure`
  - `Test Contract Closure`
  - `Closure Coverage`
  - `Implementation Delegation Gate`
  - `Delegated Worker Evidence`
  - `Reviewer Gate Status`
  - `Step Commit Gate`

### S90 Docs Impact Resolution / Docs Refresh

- Behavior goal: CLI help and reference docs accurately describe default full delete and `--force` compatibility.
- Depends on: S01, S02, S03.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - `tests/cli_runtime/test_worktree.py` only for CLI help assertion.
- Planned contract:
  - Scope: wording only; no runtime behavior change except CLI help text.
  - Test obligation: AC-005.
  - Red or alternative evidence requirement: `inspect-only` for docs; `red-required` or `characterization-update` for help assertion if current test does not check `--force` wording.
  - Green verification: focused help test plus direct docs inspection; optionally `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_remove_help_uses_all_worktree_wording -v`.
  - Refactor guardrail: do not add new command options; do not describe `--force` as required; do not add unsupported preserve mode.
  - Amendment trigger: if docs need to explain a new behavior not in requirement/design, return to design/plan amendment.
- Delegation contract:
  - delegated role: `doc-writer`
  - input docs: active issue `requirement.md`, `design.md`, this plan, provider and dogfooding reference docs, current CLI help source.
  - allowed paths: listed S90 target files only.
  - forbidden changes: application logic, infra logic, tests beyond help assertion, canonical issue docs, branch/delete/prune/status docs expansion beyond scope.
  - acceptance criteria: `ci-005` pass.
  - required tests or docs-only verification: CLI help assertion or inspection; provider/dogfooding docs parity inspection.
  - reviewer focus: `spec-reviewer` checks docs/spec alignment; `code-reviewer` is required only if CLI parser/help code change has material behavior risk beyond help text.
  - stop conditions: doc wording needs a new option or contradicts locked worktree EC; dogfooding docs cannot be updated consistently with provider docs.
  - output required: changed docs/help paths, inspection summary, verification result, unresolved wording risks, `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Concrete test case cards:
  - `tc-s90-001` help: `--force` compatibility wording
    - 前提: initialized temp repo with runtime script available.
    - 操作: `spec-dock worktree remove --help` を実行する。
    - 期待結果: help text says default remove fully deletes eligible worktrees and `--force` is accepted for compatibility, not required to enable dirty/untracked deletion.
    - 失敗検出: old wording `Pass --force to git worktree remove` remains and implies required option.
    - 検証方法: update existing remove help test or add focused help assertion.
    - 関連 closure id: `ci-005`
  - `tc-s90-002` docs: provider and dogfooding reference parity
    - 前提: provider `src/.../reference_worktree.md` and dogfooding `spec-dock/docs/reference_worktree.md` are readable.
    - 操作: inspect remove section in both files.
    - 期待結果: both docs describe Git-first full-delete default, hard blockers, target-only cleanup, branch retention, `--force` compatibility, and Git refusal behavior without contradiction.
    - 失敗検出: provider and dogfooding docs drift or old dirty/untracked failure wording remains.
    - 検証方法: docs diff inspection; if available, run focused help test after wording update.
    - 関連 closure id: `ci-005`
- Step closure contract:
  - Close only when `ci-005` passes, docs impact evidence is recorded, docs/spec alignment review passes, and step commit or approved-no-op evidence is recorded.
- Report evidence destination:
  - `TDD / Red / Green / Refactor Evidence` for help assertion if used.
  - `Step Contract Closure`
  - `Test Contract Closure`
  - `Docs impact` session log entry
  - `Implementation Delegation Gate`
  - `Delegated Worker Evidence`
  - `Reviewer Gate Status`
  - `Step Commit Gate`

### S99 Final Quality Gate

- Behavior goal: prove issue-wide behavior, docs, report evidence, and reviews are complete before final handoff.
- Depends on: S01, S02, S03, S90.
- Target files:
  - no product edits expected; report ledger updates are main-orchestrator-owned.
- Planned contract:
  - Scope: verification, review gates, report closure, final exit readiness.
  - Test obligation: all required closure rows `ci-001` through `ci-009`.
  - Red or alternative evidence requirement: `covered-existing`; no new implementation expected unless final reviewers find gaps.
  - Green verification:
    - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
    - broader `python -m unittest discover -v` if issue-wide risk or changed docs/help integration warrants it.
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
  - Refactor guardrail: final reviewers may request bounded fixes only; any new spec behavior needs plan amendment and re-review.
  - Amendment trigger: missing required closure row, reviewer fail, docs/spec mismatch, test gap outside current closure index, or unrecorded material decision.
- Delegation contract:
  - delegated role: `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` as review gates, not implementation workers.
  - input docs: active `requirement.md`, `design.md`, final canonical `plan.md`, `report.md`, product diff, docs diff, test output.
  - allowed paths: review-only unless bounded follow-up is explicitly delegated by main orchestrator.
  - forbidden changes: direct canonical edits by reviewer, implementation-readiness claim by worker, promotion/finish claims without report evidence.
  - acceptance criteria: all closure rows pass or are valid approved-no-op; final QA/code/spec reviewers pass fresh.
  - required verification: focused runtime test, chosen broader test command, validate, sync, final report ledger inspection.
  - reviewer focus: QA checks test sufficiency; code reviewer checks integrated diff and layering; spec reviewer checks requirement/design/plan/report/docs alignment.
  - stop conditions: any final reviewer fail, required command fail caused by issue changes, unresolved Evidence Adoption Ledger entry, missing closure evidence, or uncommitted step state not intentionally handled.
  - output required: final review verdicts, command results, closure coverage summary, unresolved risks, final exit contract status.
- Concrete test case cards:
  - `tc-s99-001` final verification: worktree focused suite
    - 前提: all implementation/docs steps are closed.
    - 操作: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v` を実行する。
    - 期待結果: pass; failures are classified as issue-caused or pre-existing before proceeding.
    - 失敗検出: cross-test fixture regressions from remove contract changes.
    - 検証方法: command output recorded in `report.md`.
    - 関連 closure id: `ci-001` through `ci-009`
  - `tc-s99-002` final workflow validation: spec-dock validate/sync
    - 前提: report evidence and docs are updated by main orchestrator.
    - 操作: `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` を実行する。
    - 期待結果: pass/success, or failures are recorded with cause and next action.
    - 失敗検出: scaffold/docs/spec metadata drift after issue work.
    - 検証方法: command output recorded in final report ledger.
    - 関連 closure id: `ci-005`
- Step closure contract:
  - Close only when final QA reviewer, issue-wide code reviewer, and final spec reviewer pass fresh; all required closure IDs are recorded pass or valid approved-no-op; report ledger has final evidence destinations filled; final commit/clean external evidence is available to the orchestrator.
- Report evidence destination:
  - `Closure Coverage`
  - `Reviewer Gate Status`
  - `Final QA Gate`
  - `Final Code Review Gate`
  - `Final Spec Review Gate`
  - `Final Commit`
  - `PR Delivery Gate` and `Merge Preparation Gate` if this issue proceeds to PR handoff.

## 6. Test Strategy Mapping

- Focused runtime command: `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`.
- Minimum per-step focused commands:
  - S01: updated untracked default remove test.
  - S02: tracked modification default remove and `--force` compatibility tests.
  - S03: hard blocker, Git failure no cleanup, cleanup failure, unmanaged default remove tests.
  - S90: CLI help assertion plus docs inspection.
  - S99: full `TestCliWorktree`; broader discovery if final reviewers require it.
- Manual live worktree deletion is not planned; tests use temp Git repos and temp central roots.
- Test additions are risk-calibrated to public CLI behavior and destructive safety, not raw count.

## 7. Review Gates

- Each implementation step S01-S03 requires a fresh per-step `code-reviewer` pass before step commit/closure.
- S90 requires a `spec-reviewer` docs/spec alignment pass; if CLI help code change is considered non-trivial, add `code-reviewer` focus for parser/help contract.
- S99 requires all three final gates:
  - `qa-reviewer`: test sufficiency and need for broader integration tests.
  - issue-wide `code-reviewer`: integrated diff, layering, destructive safety, maintainability.
  - final `spec-reviewer`: requirement/design/plan/report/docs alignment and closure coverage.
- Delegated worker output is not reviewer approval and must not substitute for review gates.

## 8. Rollback / Compatibility

- Compatibility:
  - Keep `spec-dock worktree remove <target> [--force] [--json]`.
  - Keep `--force` accepted as compatibility input.
  - Keep success schema and `branch_deleted=false`.
  - Keep hard blockers, Git-first deletion, target-only cleanup, and unmanaged diagnostic behavior.
- Rollback path:
  - Revert application `GitGateway.remove_worktree(... force=True)` default back to request-selected force.
  - Revert tests/docs/help to old dirty/untracked default failure contract.
  - No persisted SpecDock state migration is involved.
  - Worktrees already deleted by the new behavior are not recoverable by SpecDock rollback.

## 9. Docs Impact

Docs impact is required, not `none`.

- Provider docs impact:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` remove section must replace old dirty/untracked default failure wording.
- Dogfooding docs impact:
  - `spec-dock/docs/reference_worktree.md` must match provider contract.
- CLI help impact:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py` `--force` help should say compatibility input, not "Pass --force to git worktree remove."
- Report evidence:
  - Main orchestrator should record docs update evidence in `report.md` `Docs impact` / session log, `Step Contract Closure`, `Reviewer Gate Status`, and final spec review gate.

## 10. Final Quality Gate

S99 should require:

- all required closure rows `ci-001` through `ci-009` closed in report ledgers;
- focused worktree runtime suite pass;
- `validate` and `sync` evidence or explicit failure classification;
- fresh final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass;
- no unresolved material decision entry;
- no unresolved/stale Evidence Adoption Ledger entry for delegated drafts;
- final report ledger updated before final commit/external delivery evidence.

## 11. Plan Blockers

None.

Unresolved questions: none.

Potential non-blocking risks to carry into implementation:

- Git version differences can make locked worktree force behavior skip/fail; EC-001 should keep guarded skip/failure evidence rather than over-specifying Git internals.
- The internal field name `WorktreeRemoveRequest.force` remains semantically old but is intentionally retained to avoid unnecessary blast radius.

## 12. Integration Notes for Main Orchestrator

Source requirement/design revisions:

- `spec-dock/active/issue/requirement.md`: `状態: "approved"`, `最終更新: "2026-06-02"`.
- `spec-dock/active/issue/design.md`: `状態: "approved"`, `最終更新: "2026-06-02"`.

Suggested canonical `plan.md` structure:

- `この計画で満たす要件ID`: AC-001 through AC-005, EC-001 through EC-003.
- `依存関係から導く実装順序`: S01 -> S02 -> S03 -> S90 -> S99.
- `ステップ一覧`: copy/adapt S01, S02, S03, S90, S99.
- `要件 ↔ ステップ対応`: use the traceability table.
- `Spec-Locked Closure Index`: use `ci-001` through `ci-009`.
- Per-step `delegation contract`: use each step contract above.
- Per-step `具体テストケース一覧`: use the cards above.
- `Final Exit Contract`: see below.

Final exit contract:

- All implementation steps S01-S03 and docs step S90 are closed with report evidence.
- Every required closure row has `pass` or valid `approved-no-op` evidence in `Step Contract Closure`, `Test Contract Closure`, and `Closure Coverage`.
- Required per-step reviewer gates and S99 final gates are fresh `passed`.
- `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v` passes; broader discovery result is recorded if run or required.
- `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` results are recorded.
- Provider and dogfooding docs are aligned with the new remove contract.
- No branch deletion, cleanup broadening, new preserve mode, or canonical spec divergence was introduced.
- Final report ledger and final external commit/clean evidence are available before issue completion or PR handoff.

Report evidence destinations:

- Evidence Adoption Ledger: adoption decision for this draft, with this path, role, source paths, intended targets, `adoption_status=unreviewed` until reviewed, and diff guard result.
- Delegated Draft Evidence: created discussion path and provenance.
- Workflow Delegation Consent: this task-local scope-local discussion direct-write consent.
- Implementation Delegation Gate and Delegated Worker Evidence: S01, S02, S03, S90, S99 as applicable.
- TDD / Red / Green / Refactor Evidence: per-step command and result.
- Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta.
- Reviewer Gate Status, Final QA Gate, Final Code Review Gate, Final Spec Review Gate.
- Step Commit Gate and Final Commit evidence destinations.

Delegated draft evidence block:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00153`
- source artifacts read: listed in frontmatter `source_paths`
- draft artifact path: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00153-worktree-remove-default-full-delete/discussions/20260602t071130z-disc-plan-draft-worktree-remove-default-full-delete.md`
- draft status: produced
- authority: proposed
- adoption_status: unreviewed
- reflected_to: []
- intended_targets: listed in frontmatter `intended_targets`
- diff_guard_result: pending_or_not_run
- integration notes: main orchestrator must run diff guard, decide adoption in canonical report, and obtain fresh spec-reviewer pass before using as canonical plan evidence.
- rejected portions: none proposed
- blockers: none
- canonical artifacts edited: none
- final authority claimed: no

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
