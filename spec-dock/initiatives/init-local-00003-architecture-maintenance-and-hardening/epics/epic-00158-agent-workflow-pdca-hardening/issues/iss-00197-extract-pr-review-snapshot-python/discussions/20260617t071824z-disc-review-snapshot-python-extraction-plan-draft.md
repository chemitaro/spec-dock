---
created_by_role: implementation-planner
scope_id: iss-00197
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - tests/unit/infra/test_init_update.py
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00197 implementation plan draft

This is delegated planning evidence only. It is not canonical `plan.md`, does not claim implementation readiness, and requires main-orchestrator adoption plus a fresh `spec-reviewer` pass before it can govern implementation.

## 1. Plan Summary

Objective: extract the embedded Python heredoc from `fetch_pr_review_snapshot.sh` into `scripts/lib/pr_review_snapshot.py` while preserving the public wrapper path, stdout JSON contract, stderr/exit behavior, `--out` artifacts, review decision semantics, and downstream `pr_observation_snapshot.py` behavior.

The implementation should proceed in small reviewable steps:

1. S10: characterize the current public wrapper contract and add static/contract guardrails that do not alter behavior.
2. S20: extract provider-side Python to `pr_review_snapshot.py` and keep `fetch_pr_review_snapshot.sh` as a thin compatibility wrapper.
3. S30: mirror the provider-side shape into the dogfooding `.agents/` tree and lock scaffold/install parity.
4. S90: resolve docs, scaffold, and mirror impact, including an explicit docs no-op if no docs change is required.
5. S99: run final QA, issue-wide code review, final spec review, validation, and exit checks.

Primary implementation worker for S10/S20/S30 is `dev-coder`. If S90 requires text changes, use `doc-writer`. Reviewers remain mandatory and are not replaced by delegated workers.

## 2. Requirement / Design Traceability

- Requirement AC-001: provider-side and dogfooding mirror wrappers must not contain `python3 - <<'PY'`, `<<PY`, or an embedded Python body.
- Requirement AC-002: existing review snapshot behavior must be preserved through the public wrapper and focused review snapshot tests.
- Requirement AC-003: provider-side source and dogfooding mirror must have aligned file structure and meaning, and scaffold installation must include the new Python entrypoint.
- Requirement EC-001: Python entrypoint failure and wrapper invalid usage must preserve exit/stderr behavior.
- Requirement EC-002: malformed or unavailable GitHub responses must keep current classification, fallback, and redacted failure metadata.
- Design decision: extraction target is `scripts/lib/pr_review_snapshot.py`; no new `scripts/lib/python/` directory is introduced.
- Design decision: `fetch_pr_review_snapshot.sh` remains the public wrapper and JSON payload keeps `"script": "fetch_pr_review_snapshot.sh"` and `"collector": "s04"`.
- Design dependency: `pr_observation_snapshot.py` continues to invoke the wrapper, so provider extraction must precede mirror/scaffold parity and final downstream verification.

Source revisions observed:

- `requirement.md`: iss-00197, last updated 2026-06-17, report records requirement reviewer pass.
- `design.md`: iss-00197, last updated 2026-06-17, report records design reviewer pass after prior P2 fixes.
- `report.md`: contains delegated design draft adoption evidence and plan-phase handoff context.

## 3. Milestones

- M1 Baseline and guards: wrapper usage, invalid args, static heredoc target, and existing review snapshot semantics are characterized.
- M2 Provider extraction: provider wrapper delegates to provider `pr_review_snapshot.py`; public wrapper observable behavior is unchanged.
- M3 Mirror and scaffold parity: dogfooding mirror matches provider wrapper/Python entrypoint and `init`/`update` install the new Python asset.
- M4 Impact and final gates: docs impact is resolved, all required tests and inspections pass, and QA/code/spec reviewers pass.

## 4. Dependency-Derived Execution Order

Order is derived from `design.md` dependency analysis and file plan:

1. S10 must run first because it fixes the observable baseline and gives S20 a regression target.
2. S20 depends on S10 because provider extraction must preserve the public wrapper contract already characterized.
3. S30 depends on S20 because the mirror must copy or match the provider authority, not invent a separate implementation.
4. S90 depends on S30 because docs and scaffold impact can only be resolved after final file layout and mirror strategy are known.
5. S99 depends on S10/S20/S30/S90 because final QA/code/spec review must inspect the integrated issue-wide diff and report closure evidence.

## 5. Issue / Step Slicing

### Step list

- S10 Characterize wrapper and static extraction guard
  - Depends on: reviewed requirement/design.
  - Unblocks: provider extraction.
  - Target files: `tests/unit/infra/test_init_update.py`; report evidence only.
  - Closes: `tc-001`, `tc-002` baseline portions.

- S20 Provider extraction to `pr_review_snapshot.py`
  - Depends on: S10.
  - Unblocks: mirror/scaffold parity.
  - Target files:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - focused assertions in `tests/unit/infra/test_init_update.py`
  - Closes: `tc-002`, `tc-003`, `tc-004`, `tc-005`.

- S30 Dogfooding mirror and scaffold parity
  - Depends on: S20.
  - Unblocks: docs impact and final gates.
  - Target files:
    - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `tests/unit/infra/test_init_update.py`
  - Closes: `tc-006`, `tc-007`.

- S90 Docs/scaffold/mirror impact resolution
  - Depends on: S30.
  - Unblocks: final quality gate.
  - Target files: docs or skill text only if inspection proves an update is required; otherwise report no-op evidence.
  - Closes: `tc-008`.

- S99 Final quality gate
  - Depends on: S10/S20/S30/S90.
  - Target files: no implementation changes unless a reviewer fails and a bounded follow-up step is created.
  - Closes: `tc-009`.

### Requirement to step mapping

- AC-001 -> S10, S20, S30, S99
- AC-002 -> S10, S20, S99
- AC-003 -> S30, S99
- EC-001 -> S10, S20, S99
- EC-002 -> S20, S99
- Non-negotiable constraints -> S20, S30, S90, S99

## Spec-Locked Closure Index

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input / state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S10 | baseline | inspection | requirement background; AC-001 | Current provider and mirror wrappers are confirmed to contain the heredoc before extraction, and the exact search pattern for final removal is fixed. | `rg -n "python3 - <<'PY'|<<PY|<<'PY'"` against provider and mirror wrappers. | Red target drift; incomplete extraction hidden by vague inspection. | yes | inspect-only | Report Test Contract Closure records baseline output and final expected no-match command. |
| tc-002 | S10/S20 | wrapper compatibility | negative / acceptance | EC-001; interface contract | `--help` exits 0 with usage; invalid args exit 64 before `gh`; public wrapper path remains executable. | Direct invocation of provider `fetch_pr_review_snapshot.sh`. | Wrapper validation regression; Python extraction changing shell-facing usage behavior. | yes | red-required or covered-existing | Focused pytest and Step Contract Closure. |
| tc-003 | S20 | provider extraction | acceptance | AC-001; design file plan | Provider `fetch_pr_review_snapshot.sh` has no embedded Python heredoc and invokes sibling `pr_review_snapshot.py` by relative path. | Provider wrapper text and provider Python file existence. | Heredoc moved but not extracted; wrapper coupled to cwd. | yes | red-required | Static test plus direct inspection. |
| tc-004 | S20 | review JSON semantics | regression | AC-002; EC-002 | Public wrapper emits parseable compatible S04 JSON with unchanged `script`, `collector`, `decision`, `review`, `codex_review`, `limitations`, fingerprints, and redacted failure metadata. | Fake `gh` fixtures through provider wrapper. | Behavior change hidden by mechanical extraction. | yes | covered-existing plus focused regression | Existing review collector tests and any added issue-197 wrapper regression. |
| tc-005 | S20 | `--out` artifact semantics | regression | AC-002; EC-001 | `--out` still writes `raw/review_bodies.json` only when requested and preserves body-mode behavior. | Provider wrapper with `--body-mode` and `--out`. | Artifact path or body redaction regression. | yes | covered-existing | Existing body/out tests through public wrapper. |
| tc-006 | S30 | dogfooding mirror parity | acceptance | AC-003; dogfooding rules | Mirror wrapper and mirror `pr_review_snapshot.py` match provider meaning and have no heredoc. | `cmp` or byte comparison for provider/mirror files where appropriate; static heredoc guard across both trees. | Provider/mirror drift; dogfooding validation false positive. | yes | red-required | Static parity test and report closure. |
| tc-007 | S30 | install/update scaffold | acceptance | AC-003; provider-side authority | `spec-dock init` and `spec-dock update` install `.agents/.../scripts/lib/pr_review_snapshot.py` byte-for-byte from provider source. | Temp target repo after `main(["init", target])` and `main(["update", target])`. | New asset missing from installed scaffold or authoritative path inventory. | yes | red-required | `tests/unit/infra/test_init_update.py` install/update test. |
| tc-008 | S90 | docs/scaffold/mirror impact | docs / inspection | non-negotiable constraints; S90 policy | Docs, skill text, scaffold inventory, and mirror impact are either updated by `doc-writer` or explicitly closed as no-op with evidence. | Search for stale heredoc/extraction references and affected skill/docs paths. | Silent docs drift; scaffold impact unresolved before final gate. | yes | inspect-only or docs-only | Report docs impact ledger plus spec-reviewer docs/spec alignment. |
| tc-009 | S99 | final gate | quality gate | all AC/EC; workflow final gate | All required closure rows are pass/approved-no-op in report; targeted tests and static inspections pass; qa-reviewer, issue-wide code-reviewer, and spec-reviewer pass. | Integrated branch diff, report ledgers, final commands. | Completing without full closure, tests, or reviewers. | yes | manual-required | Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Exit Contract. |

## 6. Test Strategy Mapping

- Public wrapper first: tests must call `fetch_pr_review_snapshot.sh` for behavior assertions before relying on `pr_review_snapshot.py` internals.
- Static extraction guard: add a focused assertion that provider and mirror wrappers do not contain heredoc markers after S20/S30.
- Behavior preservation: reuse existing fake-`gh` wrapper tests around S410 inventory, S04 collector, body-mode, fallback, no-completion, and unresolved-thread decisions.
- Downstream compatibility: keep `pr_observation_snapshot.py` verification through `fetch_pr_observation_snapshot.sh` so the top-level observer still sees S04 review collector output.
- Scaffold parity: extend existing `init`/`update` asset installation tests that already cover `pr_observation_checks.py`, `pr_observation_snapshot.py`, and `pr_observation_wait.py`.
- Negative/failure coverage: preserve invalid wrapper usage exit 64, missing `gh`/API failure JSON redaction, malformed API fallback classification, and no traceback leakage.

Suggested focused validation commands after implementation:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "issue_197 or issue_187_s410 or issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads or issue_176_s03_review_collector_returns_codex_review_contract or issue_75_pr_observation_snapshot_includes_s04_review_collector_result"
rg -n "python3 - <<'PY'|<<PY|<<'PY'" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh .agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
```

The `rg` command must return no matches for completion. If pytest `-k` selection misses a renamed issue-197 test, S99 must run the relevant concrete test names or broaden to `uv run pytest tests/unit/infra/test_init_update.py`.

## 7. Review Gates

- Per implementation step:
  - S10/S20/S30 require `code-reviewer` because they affect tests, runtime wrapper behavior, shipped scaffold assets, or dogfooding mirror behavior.
  - S90 requires `spec-reviewer` if it is docs-only/no-op; if docs text changes are needed, `doc-writer` performs the change and `spec-reviewer` checks docs/spec alignment.
  - Each step must be reviewed before its commit/no-op gate closes.

- Final gates:
  - `qa-reviewer`: confirms risk-calibrated test sufficiency and whether broader integration tests are required.
  - Issue-wide `code-reviewer`: reviews integrated diff, responsibility split, shell/Python boundary, scaffold parity, and regression risk.
  - `spec-reviewer`: checks requirement/design/plan/report/docs/implementation/test alignment.

Reviewer `failed`, `unavailable`, `denied`, `waived`, or `provisional` does not satisfy a required pass. A failing reviewer requires a bounded follow-up step and re-review.

## 8. Rollback / Compatibility

Compatibility expectations:

- Existing callers continue invoking `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`.
- Wrapper usage, accepted options, invalid argument exit `64`, help exit `0`, stdout JSON shape, `--out` behavior, and GitHub failure redaction remain unchanged.
- `pr_observation_snapshot.py` continues to call the public wrapper rather than importing `pr_review_snapshot.py`.
- No behavior-policy changes are allowed for review completion, carryover unresolved threads, CI status, fallback pass candidates, or no-completion evidence.

Rollback path:

- Revert provider wrapper and mirror wrapper to the pre-extraction version.
- Remove provider and mirror `pr_review_snapshot.py`.
- Revert issue-197 tests and asset inventory additions.
- Do not roll back only the mirror or only the provider; provider and mirror must move together through normal git revert.

## 9. Docs Impact

Expected docs impact is likely no-op because the public wrapper path remains unchanged and the extraction is internal to the skill-local implementation. S90 must still inspect:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`
- docs or templates that mention `fetch_pr_review_snapshot.sh`, heredoc, or Python extraction
- scaffold/authoritative path lists in `tests/unit/infra/test_init_update.py`

If no text change is needed, S90 records an approved-no-op with search commands, inspected paths, and spec-reviewer docs/spec alignment. If text is stale, `doc-writer` updates only the affected docs/skill text and `spec-reviewer` re-checks.

## 10. Final Quality Gate

S99 must confirm:

- all closure IDs `tc-001` through `tc-009` have report closure evidence;
- provider and mirror wrappers contain no Python heredoc;
- provider and mirror `pr_review_snapshot.py` exist and are aligned with the provider-first rule;
- `init` and `update` install the new Python entrypoint;
- public wrapper behavior remains compatible through focused fake-`gh` tests;
- downstream `fetch_pr_observation_snapshot.sh` still includes the S04 review collector result;
- S90 docs impact is resolved;
- `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` have fresh pass verdicts;
- final report ledger, final commit scope, and post-commit clean-state evidence are recorded by the main orchestrator before lifecycle completion.

## 11. Plan Blockers

No design blocker was found for drafting. The extraction target, public wrapper contract, provider authority, mirror responsibility, and behavior-preservation boundary are sufficiently specified.

Implementation must not start from this draft alone. Blockers for implementation start are:

- main orchestrator has not adopted this draft into canonical `plan.md` / `report.md`;
- fresh `spec-reviewer` plan pass has not been obtained;
- S10/S20/S30 worker delegation and reviewer gates have not been scheduled or recorded.

## 12. Integration Notes for Main Orchestrator

Recommended adoption actions:

1. Copy the step order, closure index, step contracts, S90, S99, and final exit contract into canonical `plan.md` with any wording adjustments needed for local style.
2. Add an Evidence Adoption Ledger row in `report.md` for this discussion draft after post-run diff guard confirms only this file was created by the delegate.
3. Run fresh `spec-reviewer` against canonical `plan.md`; this draft is not a reviewer pass.
4. During implementation, keep S10/S20/S30 as separate review/commit scopes unless a fresh plan amendment and re-review changes the boundary.

Lightweight provenance:

- Used source docs: reviewed `requirement.md`, reviewed `design.md`, current `report.md`, plan authoring docs, existing `test_init_update.py` review snapshot/scaffold tests, and current provider wrapper script.
- Supplemental context inspected for execution semantics: active context pack, current plan scaffold, and `workflow_issue.md`.
- Leaf evidence used: none; no repo-analysis, research, consultant, QA-style, peer authoring, or dev-coder roles were invoked.
- Forbidden actions avoided: no canonical docs were edited, no implementation files were edited, no tests/config/GitHub state were changed, and no git add/commit/push was run.
- Unresolved design gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

## Implementation Step Contracts

### S10 Characterize wrapper and static extraction guard

- Behavior goal: lock the current public wrapper contract and final static heredoc-removal target before extraction.
- Design reference: existing wrapper validation plus design interface contract.
- Depends on: reviewed requirement/design.
- Unblocks: S20 provider extraction.

Planned contract:

- Scope:
  - Add focused characterization/static guard tests in `tests/unit/infra/test_init_update.py`.
  - Record baseline heredoc presence and current wrapper behavior in `report.md`.
- Test obligation:
  - closure IDs: `tc-001`, `tc-002`
  - coverage rationale: extraction can accidentally change wrapper-facing behavior before Python logic changes are visible.
- Red / alternative evidence:
  - `tc-001`: inspect-only baseline shows heredoc is currently present and fixes the final no-match search pattern.
  - `tc-002`: characterization test should pass before and after extraction; if it fails before extraction, stop and repair the plan because the assumed current contract is wrong.
- Implementation scope:
  - Allowed paths: `tests/unit/infra/test_init_update.py`; `report.md` evidence by main orchestrator.
  - Forbidden changes: provider wrapper, mirror wrapper, Python extraction, docs, config, GitHub state.
- Green verification:
  - focused pytest for new S10 tests.
  - `rg` baseline recorded in report.
- Refactor guardrail:
  - no helper extraction unless required by existing test style.
- Amendment trigger:
  - wrapper validation differs from `design.md`, or the heredoc is absent before extraction.

Delegation contract:

- Delegated role: `dev-coder`
- Input docs: `requirement.md`, `design.md`, canonical `plan.md` after adoption, `phase_plan_issue.md`, `authoring/issue-plan.md`, current provider wrapper, focused test sections.
- Allowed paths: `tests/unit/infra/test_init_update.py`
- Forbidden changes: runtime implementation, mirror assets, docs/skills, package/config, GitHub state.
- Acceptance criteria: `tc-001` and `tc-002` have planned/observed evidence; no behavior change.
- Required tests or inspection:
  - focused pytest for S10 characterization tests.
  - baseline `rg` command for heredoc presence recorded in report.
- Reviewer focus: `code-reviewer` checks tests are public-wrapper oriented and do not encode private implementation beyond the static heredoc guard.
- Stop conditions:
  - existing wrapper contract contradicts reviewed design;
  - tests require changing implementation to pass;
  - path outside allowed scope is needed.
- Output required:
  - changed files;
  - commands/results;
  - report ledger note;
  - `No material implementation decisions beyond the approved plan.` unless a real ambiguity is found.

Concrete test case cards:

- `tc-s10-001` inspect-only: baseline heredoc target is fixed
  - Prerequisite: provider and mirror `fetch_pr_review_snapshot.sh` exist.
  - Action: run `rg -n "python3 - <<'PY'|<<PY|<<'PY'"` against both wrappers.
  - Expected result: baseline finds current heredoc before implementation; final expectation is no matches after S20/S30.
  - Failure detection: prevents closing AC-001 with an imprecise manual search.
  - Verification method: report Test Contract Closure records command and expected transition.
  - Related closure id: `tc-001`

- `tc-s10-002` negative: wrapper rejects invalid args before `gh`
  - Prerequisite: provider wrapper is invoked with a fake `PATH` containing a `gh` stub that would fail if called.
  - Action: call `fetch_pr_review_snapshot.sh --repo bad --pr 13` and `--help`.
  - Expected result: invalid args return `64` with usage and do not call `gh`; `--help` returns `0`.
  - Failure detection: catches wrapper validation moving into Python in a user-visible way or calling `gh` before validation.
  - Verification method: focused pytest in `tests/unit/infra/test_init_update.py`.
  - Related closure id: `tc-002`

Step closure contract:

- Close when S10 tests pass, baseline `rg` evidence is recorded, code-reviewer passes, and the step is committed or approved-no-op with report evidence.

### S20 Provider extraction to `pr_review_snapshot.py`

- Behavior goal: replace provider heredoc with a thin shell wrapper that executes sibling Python while preserving observable review snapshot behavior.
- Design reference: extraction target `scripts/lib/pr_review_snapshot.py`; public wrapper compatibility.
- Depends on: S10.
- Unblocks: S30.

Planned contract:

- Scope:
  - Add provider `pr_review_snapshot.py`.
  - Modify provider `fetch_pr_review_snapshot.sh` to validate args and exec/call the Python entrypoint.
  - Add or update focused tests needed for provider no-heredoc and provider wrapper behavior.
- Test obligation:
  - closure IDs: `tc-002`, `tc-003`, `tc-004`, `tc-005`
  - coverage rationale: this is the highest-risk behavior-preserving extraction point.
- Red / alternative evidence:
  - `tc-003` static no-heredoc test must fail before extraction and pass after.
  - `tc-004` and `tc-005` are covered by existing public wrapper tests and can be re-run as regression.
- Implementation scope:
  - Allowed paths:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `tests/unit/infra/test_init_update.py`
  - Forbidden changes:
    - `.agents/` mirror files in S20;
    - `pr_observation_snapshot.py` behavior;
    - review completion/fallback/unresolved-thread semantics;
    - GitHub API endpoints/query policy;
    - package/config/docs.
- Green verification:
  - focused issue-197 tests;
  - existing direct wrapper review tests for S410, body modes, fallback/no-completion, and redacted failure paths.
- Refactor guardrail:
  - mechanical extraction only; no shared helper or behavior cleanup unless needed to preserve semantics.
- Amendment trigger:
  - any need to change JSON keys, decision semantics, accepted args, or downstream caller behavior.

Delegation contract:

- Delegated role: `dev-coder`
- Input docs: `requirement.md`, `design.md`, adopted `plan.md`, current provider wrapper, existing review snapshot tests.
- Allowed paths: provider wrapper, provider `pr_review_snapshot.py`, focused tests.
- Forbidden changes: mirror assets, docs, unrelated PR observation scripts, completion policy, CI/check collector behavior.
- Acceptance criteria: provider wrapper no heredoc, provider Python exists, wrapper behavior and JSON contract preserved.
- Required tests:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_197 or issue_187_s410 or issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads or issue_176_s03_review_collector_returns_codex_review_contract"`
- Reviewer focus: `code-reviewer` checks behavior preservation, subprocess boundary, path resolution, bash 3.2 compatibility, no new public env requirements, no semantics drift.
- Stop conditions:
  - extraction requires changing review decision policy;
  - Python entrypoint cannot be invoked by relative path;
  - failure path emits tracebacks or leaks stderr;
  - mirror changes become necessary before provider behavior passes.
- Output required:
  - changed files;
  - commands/results;
  - any material decision as Ledger Note;
  - unresolved risks.

Concrete test case cards:

- `tc-s20-001` acceptance: provider wrapper has no embedded Python
  - Prerequisite: S20 extraction is applied to provider source.
  - Action: inspect provider wrapper text for `python3 - <<'PY'`, `<<PY`, `<<'PY'`, and Python-only definitions from the previous heredoc.
  - Expected result: no heredoc markers or embedded Python body remain; wrapper invokes sibling `pr_review_snapshot.py`.
  - Failure detection: catches partial extraction or moving Python inside another shell heredoc.
  - Verification method: static pytest or `rg` inspection.
  - Related closure id: `tc-003`

- `tc-s20-002` acceptance: public wrapper still emits compatible S04 JSON
  - Prerequisite: fake `gh` fixture returns issue comments, reviews, inline comments, PR metadata, and GraphQL thread state.
  - Action: call provider `fetch_pr_review_snapshot.sh --repo owner/repo --pr 13 --head-sha ... --trigger-comment-id 99 --trigger-created-at ...`.
  - Expected result: JSON keeps `script`, `collector`, `decision`, `review`, `codex_review`, fingerprints, and limitations contract.
  - Failure detection: catches semantics drift from module/global initialization changes.
  - Verification method: existing review collector pytest plus focused issue-197 assertion if needed.
  - Related closure id: `tc-004`

- `tc-s20-003` regression: `--out` and body modes remain stable
  - Prerequisite: fake `gh` fixture includes old/new body content and review thread bodies.
  - Action: invoke wrapper with `--body-mode none`, `out-only`, and `trigger-window-truncated`, with `--out`.
  - Expected result: body inclusion, omission reasons, truncation caps, and `raw/review_bodies.json` behavior match existing assertions.
  - Failure detection: catches artifact/body leakage or missing output directory behavior.
  - Verification method: existing body-mode/out pytest.
  - Related closure id: `tc-005`

Step closure contract:

- Close when provider extraction passes focused tests, static no-heredoc check, code-reviewer pass, report closure entries, and a step commit.

### S30 Dogfooding mirror and scaffold parity

- Behavior goal: reflect provider extraction into dogfooding mirror and scaffold installation tests without changing semantics.
- Design reference: provider authority and dogfooding mirror validation surface.
- Depends on: S20.
- Unblocks: S90 and S99.

Planned contract:

- Scope:
  - Update mirror wrapper and mirror `pr_review_snapshot.py` to match provider meaning.
  - Add new asset path to provider install-root authoritative path expectations.
  - Add install/update assertion for `pr_review_snapshot.py`.
  - Add provider/mirror no-heredoc and parity assertions.
- Test obligation:
  - closure IDs: `tc-006`, `tc-007`
- Red / alternative evidence:
  - install/update test for new `pr_review_snapshot.py` fails before asset inventory/scaffold update.
  - static mirror no-heredoc guard fails before mirror update.
- Implementation scope:
  - Allowed paths:
    - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `tests/unit/infra/test_init_update.py`
  - Forbidden changes:
    - provider behavior changes beyond copying already-reviewed S20 result;
    - docs/skill text unless moved to S90;
    - unrelated installed assets.
- Green verification:
  - init/update asset test for `pr_review_snapshot.py`;
  - provider/mirror static no-heredoc check;
  - provider/mirror byte comparison where local generated mirror is intended to match provider.
- Refactor guardrail:
  - no test suite reorganization; follow existing issue-187 asset install test pattern.
- Amendment trigger:
  - provider and mirror cannot be kept equivalent without changing installer semantics.

Delegation contract:

- Delegated role: `dev-coder`
- Input docs: adopted `plan.md`, dogfooding rules, tests around `_ISSUE_68_AUTHORITATIVE_RELATIVE_PATHS`, existing issue-187 asset install tests.
- Allowed paths: mirror wrapper/Python file and focused `test_init_update.py` scaffold assertions.
- Forbidden changes: provider logic changes except exact parity fixes, docs, config, GitHub state.
- Acceptance criteria: mirror no heredoc, mirror Python present, init/update installs new Python asset byte-for-byte from provider, provider/mirror parity evidence recorded.
- Required tests:
  - focused install/update pytest for new asset;
  - static no-heredoc/parity tests.
- Reviewer focus: `code-reviewer` checks provider-first discipline, shipped asset inventory completeness, mirror drift risk, and test hermeticity.
- Stop conditions:
  - mirror cannot be updated without manual generated-output shortcuts outside plan;
  - installer needs behavior change beyond asset inclusion;
  - new asset is not copied by current init/update mechanics.
- Output required:
  - changed files;
  - install/update test result;
  - provider/mirror comparison evidence;
  - Ledger Note or no-material-decision statement.

Concrete test case cards:

- `tc-s30-001` acceptance: mirror wrapper and provider wrapper are heredoc-free
  - Prerequisite: S20 provider extraction is complete.
  - Action: run the static heredoc check against both provider and mirror wrappers.
  - Expected result: no heredoc markers in either wrapper.
  - Failure detection: catches provider-only extraction or dogfooding drift.
  - Verification method: pytest static assertion or `rg` command.
  - Related closure id: `tc-006`

- `tc-s30-002` acceptance: new Python asset installs by init and update
  - Prerequisite: temp target repo and provider `pr_review_snapshot.py`.
  - Action: call `main(["init", target])`, compare installed asset bytes, delete installed asset, call `main(["update", target])`, compare bytes again.
  - Expected result: installed `.agents/.../scripts/lib/pr_review_snapshot.py` exists after init and update and equals provider bytes.
  - Failure detection: catches missing authoritative path or update not restoring the new asset.
  - Verification method: `tests/unit/infra/test_init_update.py`.
  - Related closure id: `tc-007`

Step closure contract:

- Close when S30 tests pass, provider/mirror parity evidence is in report, code-reviewer passes, and the step is committed.

### S90 Docs/scaffold/mirror impact resolution

- Behavior goal: ensure the extraction leaves no stale docs, skill text, scaffold inventory, or mirror impact unresolved.
- Depends on: S30.
- Unblocks: S99.

Planned contract:

- Scope:
  - Inspect docs/skill text and scaffold references.
  - If no update is needed, record approved-no-op evidence.
  - If update is needed, delegate text-only change to `doc-writer`.
- Test obligation:
  - closure ID: `tc-008`
- Red / alternative evidence:
  - inspect-only unless stale text is found.
- Implementation scope:
  - Allowed paths if update is required:
    - affected docs or skill text only, such as `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` and mirror equivalent.
  - Forbidden changes:
    - runtime scripts, tests, package/config, canonical issue docs unless main orchestrator owns report adoption.
- Green verification:
  - search results for stale `fetch_pr_review_snapshot.sh` heredoc/Python extraction wording;
  - spec-reviewer docs/spec alignment.
- Refactor guardrail:
  - no broad docs rewrite; only stale extraction-related statements.
- Amendment trigger:
  - docs require new behavior promises not in requirement/design.

Delegation contract:

- Delegated role: `doc-writer` only if docs/skill text changes are required; otherwise no-op evidence by orchestrator plus `spec-reviewer`.
- Input docs: requirement/design/adopted plan, affected skill/docs paths, S30 scaffold evidence.
- Allowed paths: affected docs/skill text only.
- Forbidden changes: code, tests, runtime scripts, config, GitHub state.
- Acceptance criteria: docs impact is either updated and reviewed or explicitly closed as no-op with evidence.
- Required verification:
  - `rg -n "heredoc|pr_review_snapshot.py|fetch_pr_review_snapshot" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation spec-dock/docs src/spec_dock/assets/spec_dock/docs`
  - spec-reviewer docs/spec alignment.
- Reviewer focus: `spec-reviewer` checks no stale docs and no unapproved new behavior contract.
- Stop conditions:
  - docs change requires design change;
  - stale docs are found outside allowed path and cannot be updated in this step.
- Output required:
  - inspected paths/search commands;
  - docs changed or no-op rationale;
  - reviewer result.

Concrete test case cards:

- `tc-s90-001` inspect-only: docs impact is resolved
  - Prerequisite: S30 mirror/scaffold parity is complete.
  - Action: search affected skill/docs paths for stale heredoc or wrapper/Python extraction references.
  - Expected result: either no stale references remain, or doc-writer updates only the stale text.
  - Failure detection: catches hidden docs drift before final spec review.
  - Verification method: search output plus spec-reviewer docs/spec alignment.
  - Related closure id: `tc-008`

Step closure contract:

- Close when docs impact is recorded as updated or approved-no-op, spec-reviewer passes docs/spec alignment, and report evidence is complete.

### S99 Final quality gate

- Behavior goal: verify the integrated issue satisfies all requirement/design/plan obligations before delivery and lifecycle completion.
- Depends on: S10/S20/S30/S90.

Planned contract:

- Scope:
  - No implementation changes in the success path.
  - Run final validation, collect reviewer passes, and ensure report closure evidence is complete.
- Test obligation:
  - closure ID: `tc-009`
- Red / alternative evidence:
  - manual-required final gate; failures create bounded follow-up steps.
- Implementation scope:
  - Allowed paths: report ledger updates by main orchestrator; no product changes unless a reviewer-triggered follow-up is planned.
  - Forbidden changes: bundling new implementation into final gate.
- Green verification:
  - focused pytest and static no-heredoc check;
  - broader `uv run pytest tests/unit/infra/test_init_update.py` if QA requests it;
  - `./spec-dock/scripts/spec-dock validate` when canonical adoption/report updates are complete.
- Refactor guardrail:
  - final gate is not a cleanup step.
- Amendment trigger:
  - missing closure row, unplanned bug class, test insufficiency, or reviewer failure that changes implementation scope.

Delegation contract:

- Delegated roles:
  - `qa-reviewer` for test sufficiency.
  - issue-wide `code-reviewer` for integrated diff.
  - `spec-reviewer` for spec/report/docs alignment.
- Input docs: canonical requirement/design/plan/report after adoption, implementation diff, test output, S90 evidence.
- Allowed paths: none for reviewers; follow-up implementation requires new bounded worker step.
- Forbidden changes: direct final-gate implementation changes, reviewer waiver as pass, skipped report closure.
- Acceptance criteria: all final reviewers pass and report ledgers close required obligations.
- Required verification:
  - focused pytest/static commands;
  - final reviewer outputs;
  - clean worktree evidence after final commit by orchestrator.
- Reviewer focus:
  - QA: test coverage sufficiency and integration test need.
  - Code: shell/Python boundary, provider-first asset handling, mirror parity, behavior preservation.
  - Spec: AC/EC closure, docs impact, report ledger completeness.
- Stop conditions:
  - any reviewer fails;
  - closure evidence missing;
  - static heredoc check has matches;
  - tests fail and cannot be traced to unrelated baseline.
- Output required:
  - final test/inspection commands and results;
  - reviewer verdicts;
  - unresolved risks;
  - final exit decision.

Concrete test case cards:

- `tc-s99-001` final gate: all locked expectations are closed
  - Prerequisite: S10/S20/S30/S90 are complete and reviewed.
  - Action: inspect report closure ledgers and run final focused tests plus static heredoc check.
  - Expected result: every required closure row has pass/approved-no-op evidence; tests pass; heredoc check has no matches.
  - Failure detection: catches premature completion with missing evidence.
  - Verification method: report ledger inspection, pytest, `rg`, reviewer passes.
  - Related closure id: `tc-009`

Step closure contract:

- Close when QA, issue-wide code review, and spec review all pass; final report ledger is complete; final commit/delivery evidence is recorded by main orchestrator; and no unintended staged or unstaged changes remain.

## Final Exit Contract

The issue may be considered delivery-complete only after the main orchestrator verifies and records:

- canonical `plan.md` adopted from reviewed planning evidence and fresh `spec-reviewer` plan pass;
- S10/S20/S30/S90/S99 closure evidence in `report.md`;
- all required tests and static inspections pass;
- provider and mirror wrappers are heredoc-free;
- provider and mirror `pr_review_snapshot.py` exist and scaffold installation covers the provider asset;
- no behavior policy changes were introduced;
- docs impact is resolved;
- per-step reviewer gates and commits/no-op gates are closed;
- final `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass;
- PR delivery and merge-preparation gates are handled if this issue proceeds to PR delivery;
- lifecycle completion, if requested, uses `./spec-dock/scripts/spec-dock issue finish` and not manual metadata edits.
