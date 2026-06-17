---
created_by_role: implementation-planner
scope_id: iss-00193
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260617t000000z-draft-design-node-level-dependency-mutation.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py
  - tests/cli_runtime/test_deps.py
intended_targets:
  - plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# iss-00193 Node Level Dependency Mutation - delegated implementation plan draft

## 1. Plan Summary

This draft converts the reviewed requirement/design for `iss-00193` into an executable issue plan candidate. It is evidence for the main orchestrator to adopt into canonical `plan.md`; it is not itself authority.

Primary behavior goal:
- Extend `deps add/remove` from issue-only endpoints to existing initiative / epic / issue nodes while keeping `.meta.json.depends_on` as the only storage SoT.
- Reject invalid raw node-level state before write: self, ancestor/container, descendant, raw cycle, and compiled issue-level self-edge.
- Preserve existing issue->issue duplicate, remove-not-found, preflight-first, atomic write, and post-sync contracts.

Suggested step shape:
- S01: characterization and negative CLI tests for node-level mutation.
- S02: raw node dependency resolution and raw/candidate validation helpers.
- S03: `mutate_deps` add/remove integration and node writer wrappers.
- S04: issue->issue regression consolidation and post-sync/no-write guardrails.
- S90: docs/help/snapshot alignment.
- S99: final QA/code/spec gate.

Each implementation step is intended as one behavior slice, one review scope, and one commit boundary.

## 2. Requirement / Design Traceability

Source requirement revision:
- `spec-dock/active/issue/requirement.md`, `最終更新: 2026-06-17`, fresh requirement review recorded in `report.md`.

Source design revision:
- `spec-dock/active/issue/design.md`, `最終更新: 2026-06-17`, fresh design review recorded in `report.md`.

Parent epic constraints carried into the plan:
- `.meta.json` is the dependency SoT; no `deps.json` fallback, dual-read, or auto-migration.
- Mutation is command-first, preflight-first, fail-closed, and atomic.
- Duplicate add is success/no-op only after current graph validation passes.
- Remove of missing edge is an error, not a warning/no-op.

Design evidence carried into step order:
- `deps_reader.py` already resolves initiative / epic / issue refs and compiles them to the existing issue-level graph.
- `mutate_deps.py` currently blocks non-issue endpoint kinds after preflight.
- `fs_repo.py` issue-named writer methods already write the passed `meta_path` atomically.
- `tests/cli_runtime/test_deps.py` already contains the public CLI regression lane and issue-only expectations to replace.

## 3. Milestones

M1 test contract lock:
- Owner step: S01.
- Outcome: existing issue-only failure expectations are replaced or supplemented with red/characterization tests for valid node-level add/remove and invalid raw node edges.

M2 validation foundation:
- Owner step: S02.
- Outcome: all-node direct dependency resolution and raw/candidate validation helpers are available without changing public compiled `DepsTopologyLoadResult`.

M3 mutation behavior:
- Owner step: S03.
- Outcome: valid node-level add/remove updates only the source node `.meta.json.depends_on`; duplicate and direct-remove semantics stay direct-ref based.

M4 regression and integration guardrails:
- Owner step: S04.
- Outcome: existing issue->issue behavior, preflight-first order, no-write failures, shorthand direct refs, and post-sync behavior remain locked.

M5 docs/help and final quality:
- Owner steps: S90 and S99.
- Outcome: CLI help and provider docs describe node-level mutation; final QA/code/spec reviews can verify AC/EC closure evidence.

## 4. Dependency-Derived Execution Order

Implementation order follows the design module dependency:

```text
tests/cli_runtime/test_deps.py characterization
  -> infra/deps_reader.py all-node direct resolution
  -> domain/deps.py raw/candidate validation
  -> infra/fs_repo.py neutral node dependency wrappers
  -> application/mutate_deps.py orchestration
  -> commands/deps.py help text
  -> provider docs and dogfooding mirror inspection
  -> final QA/code/spec gate
```

Reasoning:
- Public CLI tests must lock observable behavior before removing the issue-only guard.
- Raw validation must exist before orchestration accepts initiative/epic endpoints.
- Writer naming can be neutralized in a small wrapper after validation contracts are fixed.
- Docs/help update belongs after runtime behavior is known, and before final spec alignment.

## 5. Issue / Step Slicing

### S01 behavior slice: node-level CLI contract tests

Behavior goal:
- Lock observable `deps add/remove` behavior for valid node-level endpoints and raw invalid candidates before implementation changes.

Depends on:
- Fresh requirement/design review evidence in `report.md`.

Unblocks:
- S02 and S03.

Target files:
- `tests/cli_runtime/test_deps.py`

Planned contract:
- Scope: CLI runtime tests and fixture helpers only.
- Test obligation: red-required for newly accepted node-level add/remove and invalid raw node edges; covered-existing for issue->issue regressions.
- Green verification: targeted `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"` after implementation steps; red evidence or failing expectations before implementation.
- Refactor guardrail: fixture helper additions only when they reduce repeated setup for node-level dependency cases.
- Amendment trigger: if tests require a new public error code not covered by requirement/design, return to plan/design before locking it.

Delegation contract:
- Delegated role: `dev-coder`.
- Input docs: `requirement.md`, `design.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`, `tests/cli_runtime/test_deps.py`.
- Allowed paths: `tests/cli_runtime/test_deps.py`.
- Forbidden changes: runtime source, docs, canonical specs, GitHub state.
- Acceptance criteria: failing or characterization tests cover AC-001..AC-007 and EC-001..EC-006 seeds without broad unrelated fixture churn.
- Required verification: focused pytest selection once implementation exists; record red/alternative evidence in `report.md`.
- Reviewer focus: `code-reviewer` for test relevance, fixture isolation, and public behavior assertions.
- Stop conditions: missing fixture support would require source changes in this step; requirement/design conflict; test cannot observe no-write.
- Output required: changed test cases, red/alternative evidence, unresolved risks, `No material implementation decisions beyond the approved plan.` unless a real decision appears.

Concrete test case seeds:
- `tc-s01-001` acceptance: `epic -> epic` add writes source epic direct ref
  - 前提: temp repo has two epics with child issues.
  - 操作: `deps add --from epic-a --to epic-b`.
  - 期待結果: stdout has `result=updated`; source epic `.meta.json.depends_on` contains `epic-b`; projection can compile child issue edges.
  - 失敗検出: non-issue endpoints still return `unsupported_node_kind`.
  - 検証方法: `tests/cli_runtime/test_deps.py`; related closure id: `slci-ac-001`.
- `tc-s01-002` acceptance: node-level remove deletes only direct raw ref
  - 前提: source initiative or epic `.meta.json.depends_on` directly contains target node id.
  - 操作: `deps remove --from <node> --to <node>`.
  - 期待結果: stdout has `result=updated`; matching direct ref is removed.
  - 失敗検出: remove only handles issue meta paths.
  - 検証方法: `tests/cli_runtime/test_deps.py`; related closure id: `slci-ac-002`.
- `tc-s01-003` negative: inherited-only remove is still `edge_not_found`
  - 前提: parent-level dependency compiles to an issue edge, but source node has no direct ref.
  - 操作: remove the compiled/inherited edge from the child source.
  - 期待結果: stderr has `code=edge_not_found`; no-write.
  - 失敗検出: compiled edge is mistaken for direct metadata.
  - 検証方法: existing inherited-only pattern extended to node-level; related closure id: `slci-ac-004`.
- `tc-s01-004` negative: raw cycle between empty epics is rejected
  - 前提: two empty epics exist; first direct dependency is present.
  - 操作: add reverse dependency.
  - 期待結果: error before write, even though compiled issue graph is empty.
  - 失敗検出: cycle validation relies only on issue expansion.
  - 検証方法: `tests/cli_runtime/test_deps.py`; related closure id: `slci-ec-001`.

Step closure contract:
- Required closure ids: `slci-ac-001`, `slci-ac-002`, `slci-ac-004`, `slci-ac-006`, `slci-ac-007`, `slci-ec-001`..`slci-ec-006`.
- Close condition: tests are present and either fail for the old issue-only behavior or are documented as characterization/covered-existing.
- Report evidence destination: TDD evidence, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Step Commit Gate.

### S02 behavior slice: raw node resolution and validation helpers

Behavior goal:
- Provide reusable helpers for raw node dependency validation and candidate add checks without changing the public compiled issue-level topology result.

Depends on:
- S01 test contract.

Unblocks:
- S03 orchestration.

Target files:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` only if protocol exposure is needed.

Planned contract:
- Scope: all-node direct dependency resolution and domain validation helpers.
- Test obligation: red-required through S01 CLI tests; add focused helper-level tests only if CLI setup cannot distinguish raw validation failure causes.
- Green verification: focused CLI runtime tests plus any new unit test selection if helper unit coverage is added.
- Refactor guardrail: keep `DepsTopologyLoadResult(issue_depends_on_map, warnings)` stable.
- Amendment trigger: adding public raw graph projection, changing warning semantics, or exposing visualization is out of scope.

Delegation contract:
- Delegated role: `dev-coder`.
- Input docs: requirement/design, delegated design draft, `deps_reader.py`, `domain/deps.py`, `application/ports.py`.
- Allowed paths: files listed in target files.
- Forbidden changes: `deps-raw.puml`, docs/help, CLI parser, delete/sync/active redesign, legacy `deps.json` fallback.
- Acceptance criteria: raw self, ancestor/container, descendant, and raw cycle can be rejected before write; empty containers are still included in raw validation.
- Required verification: S01 negative tests or helper unit tests show no-write rejection for EC-001..EC-004 and preflight for EC-006.
- Reviewer focus: `code-reviewer` for layering, cycle detection correctness, empty container handling, and public surface stability.
- Stop conditions: validation needs requirement change; helper requires broad topology model rewrite; candidate compiled self-edge cannot be tested without changing design.
- Output required: helper names, changed files, verification result, unresolved risks, ledger note if any new error-code decision is proposed.

Concrete test case seeds:
- `tc-s02-001` negative: source cannot depend on descendant
  - 前提: `epic-a` has child `issue-x`.
  - 操作: candidate raw edge `epic-a -> issue-x`.
  - 期待結果: validation rejects before write.
  - 失敗検出: only current `_is_descendant` reader path catches stored state but candidate add bypasses it.
  - 検証方法: CLI test from S01 or helper unit test; related closure id: `slci-ec-003`.
- `tc-s02-002` negative: source cannot depend on ancestor/container
  - 前提: `issue-x` under `epic-a` or `epic-a` under `init-a`.
  - 操作: add `issue-x -> epic-a` or `epic-a -> init-a`.
  - 期待結果: no-write error before save.
  - 失敗検出: ancestor/container edge is accepted when compiled graph is empty or ambiguous.
  - 検証方法: CLI/helper test; related closure ids: `slci-ec-002`, `slci-ec-004`.
- `tc-s02-003` preflight: broken existing raw graph fails before duplicate/not-found
  - 前提: current raw graph already has a cycle.
  - 操作: duplicate add or remove missing edge.
  - 期待結果: `preflight_validate_failed`; duplicate/no-op and `edge_not_found` are not reached.
  - 失敗検出: semantic checks run before current graph validation.
  - 検証方法: CLI runtime test; related closure id: `slci-ec-006`.

Step closure contract:
- Required closure ids: `slci-ac-006`, `slci-ac-007`, `slci-ec-001`, `slci-ec-002`, `slci-ec-003`, `slci-ec-004`, `slci-ec-006`.
- Close condition: raw validation helpers are covered by public CLI or helper tests, and compiled topology API remains stable.
- Report evidence destination: TDD evidence, Step Contract Closure, Test Contract Closure, Closure Delta if helper-level tests are added.

### S03 behavior slice: `deps add/remove` node-level integration

Behavior goal:
- Remove the issue-only mutation guard and integrate raw/candidate validation, direct-ref matching, atomic write, and post-sync behavior for initiative / epic / issue endpoints.

Depends on:
- S02 validation helpers.

Unblocks:
- S04 regression consolidation and S90 docs/help.

Target files:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`

Planned contract:
- Scope: mutation orchestration and neutral node dependency writer wrappers.
- Test obligation: red-required for valid node-level add/remove, duplicate unchanged, shorthand direct matching, inherited-only remove, and no-write failures.
- Green verification: targeted CLI runtime tests in `tests/cli_runtime/test_deps.py`.
- Refactor guardrail: keep issue-named wrappers as compatibility aliases if delete/scrub code still calls them.
- Amendment trigger: if direct removal requires changing raw ref grammar or storage format, return to design.

Delegation contract:
- Delegated role: `dev-coder`.
- Input docs: requirement/design, S01/S02 test evidence, `mutate_deps.py`, `fs_repo.py`, `cli/bootstrap.py`, `ports.py`.
- Allowed paths: target files.
- Forbidden changes: tests except if implementation exposes an unavoidable plan gap, docs/help, unrelated delete/sync behavior, public output shape changes not required by AC.
- Acceptance criteria: AC-001..AC-005 pass for initiative/epic/issue nodes; AC-008 issue->issue regressions remain intact.
- Required verification: `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"`.
- Reviewer focus: `code-reviewer` for orchestration order, direct-vs-inherited semantics, atomic writer use, compatibility wrapper scope.
- Stop conditions: preflight order changes conflict with parent epic; new storage field needed; post-sync semantics cannot stay compatible.
- Output required: changed files, tests run, worker summary, unresolved risks, ledger note for any public error-code changes.

Concrete test case seeds:
- `tc-s03-001` acceptance: duplicate node-level add is unchanged without duplicate storage
  - 前提: source epic direct ref already resolves to target epic through node id or shorthand.
  - 操作: add the same edge by node id.
  - 期待結果: `result=unchanged`; post-sync skipped; storage still has one logical direct ref.
  - 失敗検出: duplicate append or compiled/inherited edge treated as direct.
  - 検証方法: CLI runtime test; related closure ids: `slci-ac-003`, `slci-ec-005`.
- `tc-s03-002` acceptance: empty container dependency is stored when raw graph is valid
  - 前提: source or target epic/initiative has no child issue.
  - 操作: valid `deps add`.
  - 期待結果: source `.meta.json.depends_on` stores target node id; empty expansion warning/projection behavior is not a write failure.
  - 失敗検出: implementation rejects empty source/target because compiled issue expansion is empty.
  - 検証方法: CLI runtime test; related closure id: `slci-ac-005`.
- `tc-s03-003` acceptance: shorthand direct ref remove resolves to node target
  - 前提: source node direct ref is `123`, `"123"`, `owner/repo#123`, or canonical URL.
  - 操作: remove by node id.
  - 期待結果: matching raw ref is removed.
  - 失敗検出: remove only compares stringified target id.
  - 検証方法: CLI runtime parameterized test; related closure id: `slci-ec-005`.

Step closure contract:
- Required closure ids: `slci-ac-001`, `slci-ac-002`, `slci-ac-003`, `slci-ac-004`, `slci-ac-005`, `slci-ac-008`, `slci-ec-005`.
- Close condition: node-level add/remove and issue->issue regressions pass under focused CLI runtime tests.
- Report evidence destination: TDD evidence, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.

### S04 behavior slice: regression consolidation and no-write/post-sync guardrails

Behavior goal:
- Verify the integrated mutation path preserves pre-existing issue->issue behavior, preflight-first ordering, write failure no-write behavior, and post-sync skip/update semantics.

Depends on:
- S03.

Unblocks:
- S90 docs/help.

Target files:
- `tests/cli_runtime/test_deps.py`
- implementation files touched by S03 only if regressions require a minimal fix.

Planned contract:
- Scope: regression tests and minimal repair only.
- Test obligation: covered-existing plus red-required for any gaps found in existing issue->issue tests after node-level integration.
- Green verification: `uv run pytest tests/cli_runtime/test_deps.py`.
- Refactor guardrail: no broad fixture rewrite; no unrelated sync/check tests.
- Amendment trigger: if regression repair requires changing AC or design semantics, stop for plan/design amendment.

Delegation contract:
- Delegated role: `dev-coder`.
- Input docs: requirement/design, S03 diff/evidence, current test failures.
- Allowed paths: `tests/cli_runtime/test_deps.py` and already-touched runtime mutation files only for minimal repair.
- Forbidden changes: docs/help, canonical specs, unrelated command suites, GitHub state.
- Acceptance criteria: AC-008 and EC-006 remain locked; all add/remove failure paths are no-write.
- Required verification: full `uv run pytest tests/cli_runtime/test_deps.py`.
- Reviewer focus: `code-reviewer` for regression completeness, no-write assertions, and avoiding behavior drift.
- Stop conditions: broad failures outside deps suite; need to change public CLI response format; flaky external GitHub dependency appears.
- Output required: test summary, repair summary if any, unresolved risks, no material decision note.

Concrete test case seeds:
- `tc-s04-001` regression: existing issue->issue add/remove output stays unchanged
  - 前提: existing two-issue fixture.
  - 操作: add, duplicate add, remove, remove not-found.
  - 期待結果: existing `result=updated|unchanged`, skipped post-sync on unchanged, `edge_not_found` on not-found.
  - 失敗検出: node-level generalization changes issue output or post-sync.
  - 検証方法: existing and adjusted CLI tests; related closure id: `slci-ac-008`.
- `tc-s04-002` no-write: write failure preserves before content
  - 前提: source meta path or directory is made unwritable as existing POSIX test does.
  - 操作: remove or add direct edge.
  - 期待結果: `code=write_failed`; `.meta.json` content unchanged.
  - 失敗検出: partial write or unlock/lock regression.
  - 検証方法: existing POSIX write failure test extended only if needed; related closure id: `slci-ac-008`.

Step closure contract:
- Required closure ids: `slci-ac-008`, `slci-ec-006`.
- Close condition: full deps CLI runtime lane passes or unrelated failures are classified with evidence.
- Report evidence destination: Test Contract Closure, Closure Coverage, Step Commit Gate.

### S90 docs impact resolution / docs refresh

Behavior goal:
- Align user-facing help/docs with initiative / epic / issue node mutation semantics and direct-edge validation boundary.

Depends on:
- S03/S04 runtime contract.

Unblocks:
- S99 final quality gate.

Target files:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- Dogfooding mirror `spec-dock/docs/reference_deps.md` and `spec-dock/docs/workflow_issue.md` inspection or refresh evidence, according to repo workflow.
- Snapshot/scaffold tests only if docs/help snapshots require update.

Planned contract:
- Scope: docs/help wording and any required snapshot assertions.
- Test obligation: docs-only / inspect-only plus focused parser/help assertion if existing tests cover help text.
- Green verification: help output inspection and targeted tests affected by docs/help snapshots.
- Refactor guardrail: do not rewrite broader workflow policy; only align dependency command wording and validation notes.
- Amendment trigger: docs need to claim raw visualization, issue readiness redesign, or GitHub lifecycle behavior.

Delegation contract:
- Delegated role: `doc-writer`.
- Input docs: requirement/design, accepted runtime behavior evidence, `reference_deps.md`, `workflow_issue.md`, `commands/deps.py`.
- Allowed paths: target files and necessary test snapshot files if present.
- Forbidden changes: runtime behavior, canonical specs/report, agent instructions, GitHub state, unrelated docs.
- Acceptance criteria: AC-009 is covered: help and docs say node id / initiative / epic / issue, direct edge remove, duplicate unchanged, empty containers, and raw validation boundary.
- Required verification: docs diff inspection; CLI help output or relevant tests; dogfooding mirror inspected or refreshed with evidence.
- Reviewer focus: `spec-reviewer` docs/spec alignment; `code-reviewer` only if help parser/test code changes are nontrivial.
- Stop conditions: docs reveal runtime/spec mismatch; mirror refresh would overwrite unrelated dogfooding data; snapshot update exceeds docs scope.
- Output required: docs changed, inspection commands, mirror handling, unresolved risks.

Concrete test / inspection seeds:
- `tc-s90-001` docs: `workflow_issue.md` no longer documents issue-only add/remove
  - 前提: provider-side workflow docs contain dependency command examples.
  - 操作: inspect updated text.
  - 期待結果: examples use `<node-id>` or explicitly mention initiative / epic / issue.
  - 失敗検出: docs still instruct issue-only mutation.
  - 検証方法: docs diff inspection; related closure id: `slci-ac-009`.
- `tc-s90-002` help: add/remove help says node id
  - 前提: CLI help text is rendered from `commands/deps.py`.
  - 操作: inspect `deps add --help` / `deps remove --help` or targeted parser/help test.
  - 期待結果: `--from` and `--to` help mention initiative / epic / issue node ids.
  - 失敗検出: user-facing CLI still says issue-only.
  - 検証方法: command output or test assertion; related closure id: `slci-ac-009`.

Step closure contract:
- Required closure ids: `slci-ac-009`.
- Close condition: docs/help and provider/dogfooding mirror handling are recorded, with spec-reviewer docs/spec alignment pass required before final gate.
- Report evidence destination: Docs impact section, Reviewer Gate Status, Step Commit Gate.

### S99 final quality gate

Behavior goal:
- Verify issue-wide closure before any adoption or delivery claim.

Depends on:
- S01..S04 and S90 closed.

Target files:
- No product edit by default. Report evidence updates only by main orchestrator after review.

Planned contract:
- Scope: final verification and review orchestration.
- Test obligation: issue-wide coverage review, not a substitute for step reviews.
- Green verification: relevant focused tests plus `uv run pytest tests/cli_runtime/test_deps.py`; consider `uv run pytest tests/unit` if helper or protocol changes affect unit surfaces.
- Refactor guardrail: no new implementation in S99; findings go back to bounded delegated steps.
- Amendment trigger: missing AC/EC closure, docs/spec mismatch, or reviewer fail.

Delegation contract:
- Delegated roles: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
- Input docs: requirement, design, adopted plan, report evidence, final diff, test output.
- Allowed paths: read-only review by default; fixes must be delegated back to bounded implementation/doc steps.
- Forbidden changes: direct parent implementation without Parent Implementation Exception, reviewer-pass self-claim, issue finish, GitHub mutation.
- Acceptance criteria: all required closure ids are pass or approved-no-op with evidence; final reviewers pass.
- Required verification: final test command evidence, final reviewer verdicts, closure coverage table.
- Reviewer focus: QA test sufficiency, code integration/diff quality, spec/plan/report/docs alignment.
- Stop conditions: any reviewer fail/unavailable/denied without explicit accepted waiver; missing closure id; dirty uncommitted step diff.
- Output required: final review summaries, unresolved risks, closure delta, external delivery evidence location.

Concrete verification seeds:
- `tc-s99-001` final test lane
  - 前提: all step commits complete.
  - 操作: run `uv run pytest tests/cli_runtime/test_deps.py`.
  - 期待結果: pass, or unrelated failure classified with evidence and accepted handling.
  - 失敗検出: integration regression not caught by step-local tests.
  - 検証方法: command output in `report.md`.
- `tc-s99-002` closure coverage review
  - 前提: report has Step Contract Closure, Test Contract Closure, Closure Coverage, reviewer gate status.
  - 操作: compare every `Spec-Locked Closure Index` row to evidence.
  - 期待結果: no required closure is missing; any closure delta has re-review evidence.
  - 失敗検出: AC/EC marked done without test/report evidence.
  - 検証方法: QA/spec review.

Step closure contract:
- Required closure ids: all rows in `Spec-Locked Closure Index`.
- Close condition: final QA/code/spec reviewer gates pass after S90; no unresolved blockers.
- Report evidence destination: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Closure Coverage, Final Commit external evidence.

## 6. Test Strategy Mapping

Risk-calibrated strategy:
- Public CLI behavior: lock with `tests/cli_runtime/test_deps.py`.
- Raw/candidate invariants: prefer public CLI tests; add helper unit tests only if CLI coverage cannot isolate the bug class.
- Direct-vs-inherited semantics: assert source `.meta.json.depends_on` before/after and output code.
- Empty containers: assert storage succeeds while compiled projection may be empty/warning.
- Regression: preserve existing issue->issue add/remove, duplicate unchanged, shorthand remove, write failure, preflight-first, post-sync update/skip.
- Docs/help: inspect provider docs and rendered help text; refresh dogfooding mirror only through accepted repo workflow.

Suggested command queue:
- After S03: `uv run pytest tests/cli_runtime/test_deps.py -k "deps_add or deps_remove"`.
- After S04: `uv run pytest tests/cli_runtime/test_deps.py`.
- If S02 adds unit tests: run the targeted unit path in addition to CLI runtime tests.
- Before final delivery: `uv run pytest tests/cli_runtime/test_deps.py`; broaden to `uv run pytest tests/unit` if protocol/domain helpers were materially changed.

## Spec-Locked Closure Index

| id | spec link | locked expectation | observable input/state | evidence level | owner step | required |
|---|---|---|---|---|---|---|
| slci-ac-001 | AC-001 | Valid node-level add stores target node id in source `.meta.json.depends_on` and returns `result=updated` | `deps add --from <initiative|epic|issue> --to <initiative|epic|issue>` | red-required | S01/S03 | yes |
| slci-ac-002 | AC-002 | Node-level remove deletes matching direct ref and returns `result=updated` | source direct ref exists | red-required | S01/S03 | yes |
| slci-ac-003 | AC-003 | Duplicate direct add on healthy graph returns `result=unchanged`, skips post-sync, and does not duplicate storage | same direct edge already resolves | red-required | S03 | yes |
| slci-ac-004 | AC-004 | Inherited-only edge is not direct and remove returns `edge_not_found` with no-write | compiled edge exists but source direct ref absent | red-required | S01/S03 | yes |
| slci-ac-005 | AC-005 | Empty epic/initiative valid raw dependency is stored; empty issue expansion is not a write failure | source or target has no child issues | red-required | S03 | yes |
| slci-ac-006 | AC-006 | Candidate raw cycle is rejected before write regardless of child issue presence | reverse edge between empty or non-empty parent nodes | red-required | S01/S02 | yes |
| slci-ac-007 | AC-007 | Self, ancestor/container, descendant, and compiled self-edge candidates are rejected before write | invalid candidate direct edges | red-required | S01/S02 | yes |
| slci-ac-008 | AC-008 | Existing issue->issue add/remove contracts do not regress | existing issue-level scenarios | covered-existing | S04 | yes |
| slci-ac-009 | AC-009 | CLI help and docs describe node-level endpoints, validation, duplicate, empty-container, and direct-edge semantics | `deps add/remove --help`, provider docs, dogfooding mirror | inspect-only | S90 | yes |
| slci-ec-001 | EC-001 | `epic-a -> epic-b` plus `epic-b -> epic-a` is rejected as raw cycle, even empty | two epics, reverse add | red-required | S01/S02 | yes |
| slci-ec-002 | EC-002 | `issue-x -> parent epic-a` or compiled self-edge candidate is rejected before write | child issue to parent/container | red-required | S02 | yes |
| slci-ec-003 | EC-003 | `epic-a -> child issue-x` descendant dependency is rejected before write | parent to descendant | red-required | S02 | yes |
| slci-ec-004 | EC-004 | `epic-a -> parent initiative-a` ancestor/container dependency is rejected before write, even empty | child scope to ancestor | red-required | S02 | yes |
| slci-ec-005 | EC-005 | Direct resolution matching handles numeric/scoped/URL refs for duplicate add and remove | raw ref is `123`, `"123"`, `owner/repo#123`, URL | red-required | S03 | yes |
| slci-ec-006 | EC-006 | Broken current graph fails preflight before duplicate/no-op, remove not-found, or node-kind semantics | existing invalid graph | red-required | S02/S04 | yes |

## 7. Review Gates

Per-step gates:
- S01: `code-reviewer` on test coverage and fixture scope.
- S02: `code-reviewer` on domain/infra layering and raw validation correctness.
- S03: `code-reviewer` on mutation orchestration, direct matching, writer wrapper compatibility, and no-write behavior.
- S04: `code-reviewer` on regression coverage and no unrelated broadening.
- S90: `doc-writer` implementation with `spec-reviewer` docs/spec alignment; add `code-reviewer` only if help parser/test code changes are nontrivial.
- S99: `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` all pass.

Commit/review boundary:
- One implementation step equals one review scope and one commit.
- A failed reviewer finding returns to the same bounded delegated worker unless a Parent Implementation Exception is explicitly recorded.
- No step may begin implementation until the previous step has Step Result Approval.

## 8. Rollback / Compatibility

Rollback:
- Revert the issue diff by step commit if needed.
- Do not add feature flags, fallback readers, or `deps.json` compatibility paths.

Compatibility:
- Existing `.meta.json.depends_on` schema remains unchanged.
- Existing issue->issue command output stays compatible.
- Existing `DepsTopologyLoadResult(issue_depends_on_map, warnings)` remains compiled issue-level output.
- Existing issue-named writer methods may remain as compatibility wrappers while neutral node methods are introduced.

No-write requirements:
- Validation failure, unresolved add target/source, edge-not-found remove, unsupported raw state, and write failure must preserve before content.
- Current graph validation runs before duplicate/no-op or remove-not-found semantics.

## 9. Docs Impact

Docs/help updates are required, not optional:
- `commands/deps.py`: `--from` / `--to` help text must say initiative / epic / issue node id, not issue-only.
- Provider `reference_deps.md`: document node-level direct dependency mutation, direct-edge remove semantics, duplicate unchanged, empty-container behavior, and raw validation failures.
- Provider `workflow_issue.md`: command examples must stop encouraging issue-only dependency mutation.
- Dogfooding mirror under `spec-dock/docs/`: inspect or refresh according to shipped asset workflow; record the decision and evidence in `report.md`.

Docs impact `none` is not valid for this issue because AC-009 explicitly requires docs/help alignment.

## 10. Final Quality Gate

Required before any completion or implementation-readiness claim:
- All SLCI rows have evidence in report Step Contract Closure, Test Contract Closure, and Closure Coverage.
- `uv run pytest tests/cli_runtime/test_deps.py` is passing or any unrelated failure is classified with evidence and accepted handling.
- If helper/protocol changes affect unit surfaces, targeted unit tests or `uv run pytest tests/unit` have been run.
- `qa-reviewer` passes test sufficiency and integration coverage.
- Issue-wide `code-reviewer` passes final diff structure and regression risk.
- Final `spec-reviewer` passes requirement/design/plan/report/docs alignment.
- Final report ledger records docs impact, closure delta, reviewer gates, and commit evidence.

S99 must not be used to bundle implementation fixes. Findings return to bounded S01..S90 follow-up steps.

## 11. Plan Blockers

None identified from the reviewed requirement/design evidence.

Clarification candidates for orchestrator if they arise during adoption:
- Whether public error code names for ancestor/descendant should be locked explicitly or treated as implementation detail under existing invalid-add categories.
- Whether helper-level unit tests are required in addition to CLI runtime coverage after the actual implementation shape is known.
- Whether dogfooding mirror docs should be refreshed in the same issue step or inspected and recorded if provider-side shipped docs are the only source-of-truth change.

These are not current blockers because requirement/design already fix the behavior boundary.

## 12. Integration Notes for Main Orchestrator

Suggested adoption into canonical `plan.md`:
- Preserve S01..S04/S90/S99 step boundaries so implementation remains one-step-at-a-time with per-step review and commit.
- Keep the `Spec-Locked Closure Index` central and require every AC/EC row to map to step-local test seeds and report closure evidence.
- Keep docs/help work in S90 after runtime contract is implemented; do not merge docs-only review with code review unless the step is deliberately split.
- In `report.md`, add this draft to Delegated Draft Evidence and Evidence Adoption Ledger only after the main orchestrator performs the post-run diff guard.
- Run a fresh `spec-reviewer` on canonical `plan.md` after adoption. This draft is not a reviewer pass.

Leaf evidence used:
- Active requirement/design/report and delegated design draft.
- Parent epic requirement/design/plan.
- Issue workflow, phase plan issue playbook, and issue plan authoring schema.
- Current runtime/test surfaces for deps mutation, reader, writer, CLI help, and CLI runtime tests.

Forbidden actions avoided:
- No canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edit is intended by this draft.
- No source code, tests, docs, config, workflow, agent instruction, GitHub state, or secret edit is intended by this draft.
- No reviewer pass, adoption, phase completion, implementation readiness, or final authority is claimed.

Unresolved design gaps:
- none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
