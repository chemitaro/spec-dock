---
種別: 実装計画書（Issue）
ID: "iss-00303"
タイトル: "Issue Draft Adoption Validation"
関連GitHub: ["#303"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00303 Issue Draft Adoption Validation — 実装計画

## 1. 実装方針

`iss-00303` は、Issue node 作成後に ChatGPT draft pack と selected skeleton fill を canonical adoption input として検証する runtime command を追加する。

実装は provider-side source of truth から始め、dogfood mirror に反映し、focused CLI runtime tests で provider/dogfood parity と fail-closed behavior を確認する。

中間 Issue のため、この Issue では PR を作成しない。検証結果と finish evidence を残し、`iss-00307` の final quality gate / mergeable PR delivery に defer する。

## 2. Closure IDs

| ID | Close condition | Evidence |
|---|---|---|
| CLOS-001 | deferred command list / help baseline inspected | pre-change tests or inspection |
| CLOS-002 | Issue draft adoption result contract implemented | domain tests |
| CLOS-003 | Selected skeleton fill result contract implemented | domain tests |
| CLOS-004 | issue draft adoption positive and negative fixtures pass | focused pytest |
| CLOS-005 | selected skeleton fill positive and negative fixtures pass | focused pytest |
| CLOS-006 | safe report path tests pass | focused pytest |
| CLOS-007 | text/JSON renderers preserve authority boundary | focused pytest |
| CLOS-008 | CLI help and invocation tests pass | focused pytest |
| CLOS-009 | provider and dogfood compatibility wrappers pass | focused pytest |
| CLOS-010 | forbidden authority / secret redaction matrix passes | focused pytest |
| CLOS-011 | active report records adoption, reviewer, and no-PR evidence | report.md |
| CLOS-012 | `spec-dock validate` passes | command output |
| CLOS-013 | `assurance verify` passes | command output |
| CLOS-014 | `git diff --check` passes | command output |
| CLOS-015 | no hardcoded local ChatGPT wrapper path in shipped runtime/tests | `rg` output |
| CLOS-016 | issue is committed, pushed, and finished without per-Issue PR | git / spec-dock output |

## 2.1 この計画で満たす要件ID

| Requirement / AC | Covered by steps | Notes |
|---|---|---|
| BH-001, AC-003, AC-006, AC-007, AC-008 | S02, S03, S05, S08 | Issue draft adoption validation, parent trace, digest, canonical target mapping |
| BH-002, AC-011, AC-012 | S03, S05, S08 | Forbidden authority claims, unsafe paths, report path safety |
| BH-003, AC-004, AC-009, AC-010 | S02, S04, S05, S08 | selected skeleton fill, profile/template/section inventory |
| BH-004 | S04, S08 | stale profile/template/skeleton evidence |
| BH-005, AC-005 | S03, S04, S08 | fail-closed status taxonomy and review report status propagation |
| AC-001, AC-002, AC-013 | S01, S06, S07, S08 | CLI help, parser wiring, provider/dogfood wrappers |
| AC-014 | S90, S99 | no per-Issue PR delivery; defer to `iss-00307` |

## 2.2 依存関係から導く実装順序

1. S00 planning evidence を確定する。
2. S01 command surface red baseline を固定する。
3. S02 common result / status / finding contract を先に作る。
4. S03 issue draft adoption domain validation を作る。
5. S04 selected skeleton fill domain validation を作る。
6. S05 application use cases and safe report path を接続する。
7. S06 renderers and CLI wiring を接続する。
8. S07 compatibility wrappers and dogfood mirror を反映する。
9. S08 focused test matrix を埋める。
10. S90 docs impact を確認する。
11. S99 final quality gate を通す。

## 2.3 ステップ一覧

| Step | Behavior slice | Primary owner | Gate |
|---|---|---|---|
| S00 | Planning evidence adoption | main orchestrator | spec-reviewer |
| S01 | Command surface baseline | dev-coder | code-reviewer after implementation |
| S02 | Shared result contracts | dev-coder | focused tests |
| S03 | issue-draft-adoption validation | dev-coder | focused tests |
| S04 | selected-skeleton-fill validation | dev-coder | focused tests |
| S05 | Application use cases and report path guard | dev-coder | focused tests |
| S06 | Presentation and CLI wiring | dev-coder | focused tests |
| S07 | Compatibility wrappers and dogfood mirror | dev-coder | focused tests |
| S08 | Focused matrix completion | dev-coder | qa-reviewer |
| S90 | Docs impact resolution | main orchestrator / doc-writer if needed | spec-reviewer |
| S99 | Final quality gate | main orchestrator | spec/code/QA reviewers |

## 2.4 Spec-Locked Closure Index

| Closure ID | Spec link | Observable input/state | Locked expectation | Evidence level | Closure evidence | Owning step | Close condition / planned verification path | Report destination |
|---|---|---|---|---|---|---|---|---|
| CLOS-001 | AC-001, AC-002 | `authoring validate issue-draft-adoption --help`; `authoring validate selected-skeleton-fill --help` | implemented help exposes required args and does not say `Deferred` | red-required | focused help tests | S01/S06 | tests fail before wiring or inspection proves deferred state; pass after wiring | Step Contract Closure |
| CLOS-002 | BH-001, AC-003 | issue draft adoption result object | result has evidence-only authority flags and no readiness/adoption claims | red-required | domain/CLI result assertions | S02 | result contract tests pass | Test Contract Closure |
| CLOS-003 | BH-003, AC-004 | selected skeleton fill result object | result has profile/template/section summary and no readiness/adoption claims | red-required | domain/CLI result assertions | S02/S04 | selected skeleton result tests pass | Test Contract Closure |
| CLOS-004 | AC-003, AC-005, AC-006, AC-007, AC-008 | issue draft adoption stage fixtures | positive fixture passes; missing/stale/rejected/fail/blocked cases map deterministically | red-required | issue draft adoption matrix tests | S03 | focused matrix passes and findings are stable | Test Contract Closure |
| CLOS-005 | AC-004, AC-009, AC-010 | selected skeleton fill fixtures | positive fixture passes; missing/extra/duplicate/empty sections fail; profile/template mismatches stale | red-required | selected skeleton matrix tests | S04 | focused matrix passes including empty required section list | Test Contract Closure |
| CLOS-006 | AC-012 | `--report-path` safe/unsafe fixtures | safe non-canonical report writes; canonical, `.assurance.json`, symlink paths reject | red-required | report path tests | S05 | safe and unsafe report path tests pass | Test Contract Closure |
| CLOS-007 | authority boundary | text/JSON output | success output cannot imply canonical adoption, reviewer pass, execution-ready, or PR-ready | red-required | renderer output assertions | S06 | output assertions pass and no secret leak appears | Step Contract Closure |
| CLOS-008 | AC-001, AC-002 | parser/command invocation | both commands are promoted from deferred placeholders | red-required | help and invocation tests | S06 | parser and command tests pass | Step Contract Closure |
| CLOS-009 | AC-013 | provider and dogfood wrapper paths | wrappers delegate to runtime contract in both surfaces | covered-existing | wrapper smoke tests | S07 | provider and dogfood smoke pass | Step Contract Closure |
| CLOS-010 | AC-011 | forbidden authority / secret fixtures | forbidden claims reject and raw secrets are not printed | red-required | forbidden claim and redaction tests | S03/S04/S08 | rejection and redaction tests pass | Test Contract Closure |
| CLOS-011 | planning adoption | Issue-local draft artifacts and ChatGPT Use planning output | adoption decisions are recorded without treating ChatGPT output as authority | manual-required | Evidence Adoption Ledger, Spec Authoring Gate | S00 | report records adopted/rejected claims and fresh spec-reviewer pass | Evidence Adoption Ledger |
| CLOS-012 | tree validity | SpecDock tree | tree remains valid | manual-required | `./spec-dock/scripts/spec-dock validate` | S99 | command exits 0 | Final Quality Gate |
| CLOS-013 | assurance validity | active issue assurance contract | assurance source binding and profile are valid | manual-required | `./spec-dock/scripts/spec-dock assurance verify` | S99 | command exits 0 | Final Quality Gate |
| CLOS-014 | formatting | git diff | no whitespace errors | manual-required | `git diff --check` | S99 | command exits 0 | Final Quality Gate |
| CLOS-015 | portability | shipped runtime/scripts/tests | no hardcoded personal ChatGPT wrapper path | manual-required | local-wrapper path scan | S99 | `rg` finds no matches in shipped runtime/scripts/tests | Final Quality Gate |
| CLOS-016 | relay policy | branch, commit, issue lifecycle | commit/push/issue finish happen without per-Issue PR | manual-required | git and `issue finish` output | S99 | branch pushed, issue finished, PR delivery deferred to `iss-00307` | Milestone / Commit Candidate Gate |

## 2.5 要件 ↔ ステップ対応

| Step | Requirement / AC | Verification obligation |
|---|---|---|
| S01 | AC-001, AC-002 | help tests fail before wiring and pass after wiring |
| S02 | BH-001, BH-003 | result contract unit/CLI fixture assertions |
| S03 | BH-001, BH-002, BH-005, AC-003, AC-005, AC-006, AC-007, AC-008, AC-011 | issue draft adoption positive and negative CLI tests |
| S04 | BH-003, BH-004, BH-005, AC-004, AC-009, AC-010, AC-011 | selected skeleton positive and negative CLI tests |
| S05 | AC-012 | safe report path and no canonical write assertions |
| S06 | AC-001, AC-002 | CLI help, JSON/text output assertions |
| S07 | AC-013 | provider and dogfood wrapper smoke |
| S08 | all validation ACs | focused matrix command |
| S90 | AC-014 | docs impact decision recorded |
| S99 | all closures | final verification bundle and reviewer gates |

## 2.6 具体テストケース一覧

| Test seed | Step | Expected status | Closure |
|---|---|---|---|
| `issue_draft_adoption_help` | S01/S06 | help contains implemented args and no `Deferred` | CLOS-001, CLOS-008 |
| `selected_skeleton_fill_help` | S01/S06 | help contains implemented args and no `Deferred` | CLOS-001, CLOS-008 |
| `issue_draft_adoption_valid_stage` | S03 | `pass` | CLOS-004 |
| `issue_draft_adoption_review_missing` | S03 | `blocked` | CLOS-004 |
| `issue_draft_adoption_review_stale_fail_blocked_rejected_unsupported` | S03 | mapped status | CLOS-004 |
| `issue_draft_adoption_issue_missing` | S03 | `blocked` | CLOS-004 |
| `issue_draft_adoption_issue_or_parent_mismatch` | S03 | `stale` | CLOS-004 |
| `issue_draft_adoption_draft_pack_digest_mismatch` | S03 | `stale` | CLOS-004 |
| `issue_draft_adoption_review_digest_mismatch` | S03 | `stale`; computed from exact `--review-report` bytes, not embedded digest fields | CLOS-004 |
| `issue_draft_adoption_unsafe_target_or_assurance_target` | S03/S05 | `rejected` | CLOS-004, CLOS-006 |
| `issue_draft_adoption_forbidden_authority_claims` | S03 | `rejected` | CLOS-010 |
| `selected_skeleton_fill_valid_stage` | S04 | `pass` | CLOS-005 |
| `selected_skeleton_fill_missing_extra_duplicate_empty_sections` | S04 | `fail` | CLOS-005 |
| `selected_skeleton_fill_profile_template_skeleton_mismatch` | S04 | `stale` | CLOS-005 |
| `selected_skeleton_fill_forbidden_authority_claims` | S04 | `rejected` | CLOS-010 |
| `safe_report_path_writes_noncanonical_report` | S05 | `pass` | CLOS-006 |
| `unsafe_report_path_rejected` | S05 | `rejected` | CLOS-006 |
| `provider_and_dogfood_wrapper_smoke` | S07 | `pass` | CLOS-009 |

## 2.7 Step Closure Contract

Each step closes only when:

- Planned behavior slice is implemented or intentionally deferred with reason.
- Required tests/inspection for the step have observed evidence.
- No canonical docs or `.assurance.json` mutation is performed by authoring runtime.
- Findings and discovered tests are recorded in `report.md`.
- Any P0/P1 reviewer finding is fixed and re-reviewed before moving to `issue finish`.

## 2.8 Report Evidence Destinations

| Evidence type | Report section |
|---|---|
| draft adoption decisions | Evidence Adoption Ledger |
| workflow authorization | Workflow-Scoped Authorization |
| step red/green/refactor evidence | TDD / Red / Green / Refactor Evidence |
| discovered tests or risks | Discovered Tests |
| step completion | Step Contract Closure |
| test closure | Test Contract Closure |
| reviewer results | Reviewer Gate Status / Final QA / Code / Spec Review Gate |
| commit or no-op evidence | Milestone / Commit Candidate Gate |
| no-per-Issue-PR rationale | Final Commit / Deferred PR delivery notes |

## 2.9 Per-Step Delegation Contract

| Step | Delegated role | Input docs | Allowed paths | Forbidden changes | Acceptance criteria | Required verification | Reviewer focus | Stop conditions | Output required |
|---|---|---|---|---|---|---|---|---|---|
| S01 | dev-coder | requirement/design/plan, existing authoring command tests | `tests/cli_runtime/test_authoring.py`, `commands/authoring.py`, `cli/parser.py` | implementation beyond help surface | AC-001, AC-002 | focused help tests | code-reviewer | command naming conflict or need for `--force` | help test evidence |
| S02 | dev-coder | design data contracts | provider/dogfood `domain/authoring_pack/*` | CLI-only behavior without domain contract | CLOS-002, CLOS-003 | domain/CLI fixture assertions | code-reviewer | result contract cannot express no-mutation boundary | changed files and tests |
| S03 | dev-coder | requirement BH-001/BH-002/BH-005, design issue adoption schema | provider/dogfood domain/application files, tests | canonical docs write, `.assurance.json` mutation, Issue creation | AC-003, AC-005, AC-006, AC-007, AC-008, AC-011 | issue draft adoption matrix tests | code-reviewer / qa-reviewer | implementation cannot compute digest from exact `--review-report` bytes | status/finding evidence |
| S04 | dev-coder | requirement BH-003/BH-004/BH-005, design skeleton schema | provider/dogfood domain/application files, tests | authorized profile decision, assurance mutation | AC-004, AC-009, AC-010, AC-011 | selected skeleton matrix tests including empty section inventory | code-reviewer / qa-reviewer | selected skeleton schema cannot be validated deterministically | status/finding evidence |
| S05 | dev-coder | design report path safety | application files, tests | writes to canonical docs or `.assurance.json` | AC-012 | safe/unsafe report path tests | code-reviewer | safe report guard cannot reject symlink paths | report path evidence |
| S06 | dev-coder | design output rendering | presentation files, command wiring, parser, tests | success wording that implies adoption/readiness | AC-001, AC-002, CLOS-007 | JSON/text output assertions | code-reviewer | renderer leaks secrets or authority claims | output snapshot evidence |
| S07 | dev-coder | provider/dogfood parity rules | provider wrappers, dogfood wrappers, mirrored runtime files | personal absolute path dependency | AC-013 | wrapper smoke and local-wrapper path scan | code-reviewer | wrapper requires local-only backend path | parity evidence |
| S08 | dev-coder | full AC matrix | tests only unless bug fix requires runtime change | unrelated refactor | all validation ACs | focused matrix and full authoring tests when practical | qa-reviewer | uncovered P1/P2 acceptance gap | coverage summary |
| S90 | main orchestrator or doc-writer if docs change | requirement/design/plan | docs only if needed | broad workflow rewrite outside Issue scope | AC-014 | docs impact inspection | spec-reviewer | user-facing docs need changes but are not planned | docs impact note |
| S99 | main orchestrator | all changed files and report | report evidence only before commit; code fixes only if reviewer finds issues | per-Issue PR delivery | all closures | validate, assurance verify, diff-check, focused/full tests, reviewers | spec/code/QA reviewers | P0/P1/P2 required fix remains open | final closeout evidence |

## 2.10 Step Gate

| Step | Gate to proceed |
|---|---|
| S01-S07 | step-local tests pass or report records approved no-op; no forbidden authority/canonical mutation introduced |
| S08 | QA reviewer confirms acceptance coverage or all actionable findings are fixed |
| S90 | docs impact is either not needed or updated and reviewed |
| S99 | spec-reviewer, code-reviewer, and qa-reviewer pass; final verification bundle recorded |

## 2.11 S90 Docs Impact Resolution

This Issue primarily adds runtime validators and compatibility wrappers. Broader user-facing workflow docs are planned in `iss-00306`. S90 must still inspect whether command reference docs or README entries are required for this Issue. If docs are not updated, `report.md` must record the no-op rationale and defer broad workflow guidance to `iss-00306`.

## 2.12 S99 Final Quality Gate

S99 must run after implementation and before `issue finish`:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption or selected_skeleton_fill or authoring_validate"
uv run pytest tests/cli_runtime/test_authoring.py -q
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption --help
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill --help
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests/cli_runtime/test_authoring.py
```

S99 also requires fresh `spec-reviewer`, `code-reviewer`, and `qa-reviewer` pass evidence. Non-pass, unavailable, denied, waived, provisional, or stale reviewer results block `issue finish`.

## 2.13 Final Exit Contract

`iss-00303` may finish only when:

- `requirement.md`, `design.md`, `plan.md`, and `report.md` have fresh planning review pass.
- Runtime implementation matches the approved command contract.
- CLOS-001 through CLOS-016 are satisfied or explicitly deferred with non-blocking rationale.
- No authoring runtime command writes canonical docs or mutates `.assurance.json`.
- No validator output claims reviewer pass, execution-ready, PR-ready, merge-ready, or canonical adoption.
- Provider-side source and dogfood mirror are in parity for touched runtime files.
- Branch is committed and pushed.
- No per-Issue PR is created; PR delivery remains deferred to `iss-00307`.

## 3. 実装ステップ（Step Plan）

### S00: Planning and draft adoption evidence

Goal:

- Adopt Issue-local draft artifacts and ChatGPT Use planning result into canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` evidence notes.

Actions:

- Read active Issue drafts.
- Run ChatGPT Use planning pass.
- Rewrite canonical docs through main orchestrator adoption.
- Record uncertainty that ChatGPT could access GitHub repository but not current branch, and inspected `main` fallback.

Verification:

- `./spec-dock/scripts/spec-dock guidance issue-planning`
- `./spec-dock/scripts/spec-dock validate`

Closure:

- CLOS-011 partially satisfied before implementation.

Step-local test cards:

- Card S00-A:
  - 前提: Issue-local draft artifacts and ChatGPT Use planning output exist only as evidence.
  - 操作: Inspect `artifacts/`, canonical docs, and `report.md` adoption entries.
  - 期待結果: Canonical docs record adopted/rejected evidence without treating ChatGPT output as reviewer pass, authorized profile, or execution readiness.
  - 失敗検出: `report.md` implies ChatGPT output is canonical authority or omits the current-branch fallback uncertainty.
  - 検証方法: `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock validate`.
  - Closure: CLOS-011.

### S01: Red baseline and command surface tests

Goal:

- Lock the expected command surface before implementation.

Actions:

- Add/adjust tests proving `issue-draft-adoption` and `selected-skeleton-fill` are no longer deferred.
- Add help tests for both commands.
- Confirm no `--force` appears.

Red evidence:

- New help tests fail before implementation or existing deferred command inspection proves current gap.

Green evidence:

- Help tests pass after command wiring.

Closure:

- CLOS-001, CLOS-008

Step-local test cards:

- Card S01-A:
  - 前提: `issue-draft-adoption` may still be deferred before implementation.
  - 操作: Run the focused help test for `authoring validate issue-draft-adoption`.
  - 期待結果: The red baseline fails because required args are missing or the help text still exposes deferred status; after implementation, help exposes required args and no `Deferred` wording.
  - 失敗検出: Help remains deferred, omits `--input`, `--review-report`, or `--issue-dir`, or exposes a broad `--force`.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption_help"`.
  - Closure: CLOS-001, CLOS-008.
- Card S01-B:
  - 前提: `selected-skeleton-fill` may still be deferred before implementation.
  - 操作: Run the focused help test for `authoring validate selected-skeleton-fill`.
  - 期待結果: The red baseline fails before wiring; after implementation, help exposes `--input`, `--issue-dir`, `--assurance`, and `--selected-skeleton` without deferred wording.
  - 失敗検出: Help remains deferred, omits required args, or exposes a broad bypass flag.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "selected_skeleton_fill_help"`.
  - Closure: CLOS-001, CLOS-008.

### S02: Domain result contracts

Goal:

- Implement pure result and finding contracts for both validators.

Actions:

- Add `issue_draft_adoption_contract.py`.
- Add `selected_skeleton_fill_contract.py`.
- Define status taxonomy, findings, authority boundary flags, and stable `to_dict()`.
- Reuse common status/finding style from candidate validators where it reduces duplication.

Red evidence:

- Result contract assertions fail before implementation.

Green evidence:

- Domain contract tests pass.

Closure:

- CLOS-002, CLOS-003

Step-local test cards:

- Card S02-A:
  - 前提: Issue draft adoption validation needs a stable evidence-only result object before CLI wiring.
  - 操作: Instantiate or invoke the issue draft adoption result contract with passing and failing findings.
  - 期待結果: `to_dict()` includes status, findings, authority boundary fields, and no canonical adoption / reviewer pass / execution-ready claims.
  - 失敗検出: Result shape is CLI-only, unstable, or includes readiness/adoption authority flags.
  - 検証方法: focused domain or CLI contract assertions in `tests/cli_runtime/test_authoring.py`.
  - Closure: CLOS-002.
- Card S02-B:
  - 前提: Selected skeleton validation needs a stable result object with profile/template/section summary.
  - 操作: Instantiate or invoke the selected skeleton result contract with passing and failing findings.
  - 期待結果: `to_dict()` exposes selected profile, template/skeleton observations, section summary, findings, and no readiness/adoption claims.
  - 失敗検出: Missing section inventory, ambiguous status, or authority leakage.
  - 検証方法: focused domain or CLI contract assertions in `tests/cli_runtime/test_authoring.py`.
  - Closure: CLOS-003.

### S03: issue draft adoption validation

Goal:

- Validate post-Issue-node draft adoption input.

Actions:

- Read adoption input JSON.
- Validate schema version and required fields.
- Validate Issue node exists and parent trace matches.
- Validate draft paths, draft digests, draft pack digest, and expected source/review hash.
- Validate canonical target mapping.
- Reject `.assurance.json` target and forbidden authority claims.
- Reuse sensitive scan and safe path concepts.

Red evidence:

- Positive and negative fixtures fail before domain/application implementation.

Green evidence:

- Positive fixture returns `pass`.
- Missing node returns `blocked`.
- Parent mismatch / digest mismatch returns `stale`.
- Unsafe target / authority claim returns `rejected`.
- Malformed schema returns `fail`.

Closure:

- CLOS-004, CLOS-010

Step-local test cards:

- Card S03-A:
  - 前提: A valid Issue node, matching parent trace, passing review report, and matching draft/source/review digests are present.
  - 操作: Run `authoring validate issue-draft-adoption` with the positive fixture.
  - 期待結果: Status is `pass`, findings are non-blocking, and output remains evidence-only.
  - 失敗検出: Positive fixture returns `blocked`, `stale`, `fail`, or `rejected`, or claims canonical adoption.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption_valid_stage"`.
  - Closure: CLOS-004.
- Card S03-B:
  - 前提: Review report is missing, stale, rejected, failed, blocked, unsupported, or digest-mismatched.
  - 操作: Run negative issue draft adoption fixtures.
  - 期待結果: Missing review blocks; stale/rejected/fail/blocked/unsupported review maps deterministically; review digest mismatch is computed from exact `--review-report` bytes and returns `stale`.
  - 失敗検出: Validator trusts embedded digest fields, collapses statuses, or accepts a stale/rejected review.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption_review"`.
  - Closure: CLOS-004.
- Card S03-C:
  - 前提: Issue node, parent trace, draft pack digest, target mapping, or authority claims are invalid.
  - 操作: Run missing node, Issue/parent mismatch, draft digest mismatch, unsafe target, and forbidden authority claim fixtures.
  - 期待結果: Missing node returns `blocked`; mismatch/digest cases return `stale`; unsafe target and forbidden authority claims return `rejected`.
  - 失敗検出: Validator writes canonical docs, mutates `.assurance.json`, accepts unsafe targets, or allows reviewer-pass/execution-ready/PR-ready claims.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption_issue or issue_draft_adoption_draft_pack or issue_draft_adoption_unsafe or issue_draft_adoption_forbidden"`.
  - Closure: CLOS-004, CLOS-010.

### S04: selected skeleton fill validation

Goal:

- Validate selected profile, template hash, skeleton hash, and section inventory.

Actions:

- Read selected skeleton fill input JSON.
- Read selected skeleton evidence.
- Read `.assurance.json` as observation only.
- Validate selected profile against expected profile and assurance observation.
- Validate template hash and skeleton hash.
- Validate missing / extra / duplicate sections.
- Reject unsafe section fill paths and forbidden authority claims.

Red evidence:

- Positive and negative skeleton fixtures fail before implementation.

Green evidence:

- Positive fixture returns `pass`.
- Missing / extra / duplicate sections return `fail`.
- Profile/template/skeleton mismatch returns `stale`.
- Authority claims return `rejected`.

Closure:

- CLOS-005, CLOS-010

Step-local test cards:

- Card S04-A:
  - 前提: Selected profile, template hash, skeleton hash, and section inventory match expected Issue skeleton evidence.
  - 操作: Run `authoring validate selected-skeleton-fill` with the positive fixture.
  - 期待結果: Status is `pass`, section summary is complete, and output remains evidence-only.
  - 失敗検出: Positive fixture returns non-pass or implies authorized profile / execution readiness.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "selected_skeleton_fill_valid_stage"`.
  - Closure: CLOS-005.
- Card S04-B:
  - 前提: Section inventory is missing, extra, duplicate, or empty.
  - 操作: Run selected skeleton negative section fixtures.
  - 期待結果: Missing/extra/duplicate/empty required section inventory returns `fail` with deterministic findings.
  - 失敗検出: Empty section inventory passes, duplicate sections are ignored, or findings do not identify the section problem.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "selected_skeleton_fill_missing_extra_duplicate_empty_sections"`.
  - Closure: CLOS-005.
- Card S04-C:
  - 前提: Profile, template hash, skeleton hash, or authority claims are invalid.
  - 操作: Run profile/template/skeleton mismatch and forbidden authority claim fixtures.
  - 期待結果: Profile/template/skeleton mismatches return `stale`; forbidden authority claims return `rejected`.
  - 失敗検出: Validator accepts mismatched profile/template evidence or allows reviewer-pass/execution-ready/PR-ready claims.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "selected_skeleton_fill_profile_template_skeleton_mismatch or selected_skeleton_fill_forbidden_authority_claims"`.
  - Closure: CLOS-005, CLOS-010.

### S05: Application use cases and report path guard

Goal:

- Connect CLI requests to domain validation and safe report writing.

Actions:

- Add `issue_draft_adoption_validation.py`.
- Add `selected_skeleton_fill_validation.py`.
- Reuse or extract safe report path guard from candidate validation.
- Report writing is limited to safe non-canonical output paths.
- Canonical docs and `.assurance.json` are never written.

Red evidence:

- Unsafe report path tests fail before implementation.

Green evidence:

- Safe report paths under `.specdock-authoring` write output.
- canonical docs / `.assurance.json` / symlink report paths are rejected.

Closure:

- CLOS-006

Step-local test cards:

- Card S05-A:
  - 前提: Caller supplies a safe report path under a non-canonical authoring evidence directory.
  - 操作: Run each validator with `--report-path` pointing to safe output.
  - 期待結果: Report file is written only to the safe path; canonical docs and `.assurance.json` remain untouched.
  - 失敗検出: Command writes canonical docs, writes `.assurance.json`, or omits requested safe report output.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "safe_report_path_writes_noncanonical_report"`.
  - Closure: CLOS-006.
- Card S05-B:
  - 前提: Caller supplies a report path targeting canonical docs, `.assurance.json`, or a symlink escape.
  - 操作: Run unsafe report path fixtures.
  - 期待結果: Command rejects the unsafe path before writing.
  - 失敗検出: Any unsafe path is created or overwritten.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "unsafe_report_path_rejected"`.
  - Closure: CLOS-006.

### S06: Presentation renderers

Goal:

- Produce text and JSON output with adoption-specific semantics.

Actions:

- Add `issue_draft_adoption_renderer.py`.
- Add `selected_skeleton_fill_renderer.py`.
- Include authority boundary fields in output.
- Ensure success text does not imply adoption or readiness.

Verification:

- Renderer assertions in CLI tests.

Closure:

- CLOS-007

Step-local test cards:

- Card S06-A:
  - 前提: Domain/application validators return pass, stale, blocked, fail, and rejected statuses.
  - 操作: Render text and JSON output for representative statuses.
  - 期待結果: Output reports validation evidence, status, findings, and next action without implying canonical adoption, reviewer pass, execution-ready, PR-ready, or merge-ready.
  - 失敗検出: Output wording grants authority, leaks raw secret-like content, or diverges between text and JSON contracts.
  - 検証方法: renderer assertions in `tests/cli_runtime/test_authoring.py`; forbidden wording scan in focused tests.
  - Closure: CLOS-007.

### S07: CLI wiring and wrappers

Goal:

- Promote commands from deferred placeholders to implemented runtime commands.

Actions:

- Update `commands/authoring.py`.
- Update parser specs in `cli/parser.py`.
- Add provider wrappers:
  - `validate_issue_draft_adoption.py`
  - `validate_selected_skeleton_fill.py`
- Mirror wrappers and runtime files under the dogfood `spec-dock/scripts` runtime tree.

Verification:

- Help tests.
- Wrapper smoke tests.
- Dogfood runtime path smoke.

Closure:

- CLOS-008, CLOS-009

Step-local test cards:

- Card S07-A:
  - 前提: Parser and command registry expose the two validator commands.
  - 操作: Invoke both commands through provider runtime and dogfood `./spec-dock/scripts/spec-dock` paths with help and minimal fixture inputs.
  - 期待結果: Commands dispatch to implemented validators in both surfaces.
  - 失敗検出: Either surface remains deferred, parser dispatch fails, or provider/dogfood behavior diverges.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "provider_and_dogfood_wrapper_smoke or issue_draft_adoption_help or selected_skeleton_fill_help"`.
  - Closure: CLOS-008, CLOS-009.
- Card S07-B:
  - 前提: Runtime and wrappers must not depend on the local ChatGPT wrapper path.
  - 操作: Scan shipped runtime/scripts/tests for personal absolute ChatGPT wrapper references.
  - 期待結果: No matches are found in shipped runtime/scripts/tests.
  - 失敗検出: `/Users/iwasawayuuta`, `.codex/skills/chatgpt-use`, or `oracle-chatgpt` appears in shipped runtime code as a dependency.
  - 検証方法: `rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests/cli_runtime/test_authoring.py`.
  - Closure: CLOS-009, CLOS-015.

### S08: Focused test matrix completion

Goal:

- Cover acceptance criteria with focused tests.

Tests to add:

- command help implemented
- issue draft adoption positive fixture
- selected skeleton fill positive fixture
- missing review report
- review `stale` / `rejected` / `fail` / `blocked` / unsupported
- Issue node missing
- Issue ID / parent mismatch
- draft pack digest mismatch
- source/review digest mismatch
- missing draft
- unsafe canonical target
- `.assurance.json` mutation claim
- execution-ready / reviewer-pass / PR-ready claims
- missing / extra / duplicate sections
- selected profile mismatch
- template hash mismatch
- unsafe report path
- symlink report path
- secret/raw transcript redaction
- provider/dogfood wrapper smoke

Verification:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption or selected_skeleton_fill or authoring_validate"
```

Closure:

- CLOS-004 through CLOS-010

Step-local test cards:

- Card S08-A:
  - 前提: S01-S07 implementation is complete.
  - 操作: Run the focused acceptance matrix for issue draft adoption, selected skeleton fill, and authoring validation.
  - 期待結果: All AC-linked positive and negative fixtures pass.
  - 失敗検出: Any AC row is missing coverage, has ambiguous expected status, or passes while forbidden authority/canonical mutation is present.
  - 検証方法: `uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption or selected_skeleton_fill or authoring_validate"`.
  - Closure: CLOS-004 through CLOS-010.
- Card S08-B:
  - 前提: Focused matrix passes.
  - 操作: Record QA coverage summary and any discovered tests or residual risks in `report.md`.
  - 期待結果: `report.md` links acceptance coverage to closure IDs and records no unresolved P1/P2 gap.
  - 失敗検出: QA reviewer cannot trace an acceptance criterion to a concrete test or inspection.
  - 検証方法: fresh `qa-reviewer` pass after implementation.
  - Closure: CLOS-004 through CLOS-010.

### S90: Docs impact resolution

Goal:

- Resolve whether this Issue requires user-facing docs or command reference updates before final closeout.

Actions:

- Inspect changed command help, runtime surface, and existing docs references.
- If this Issue adds only validator internals and command behavior already covered by later `iss-00306`, record a no-op rationale in `report.md`.
- If a command reference must change for the implemented validator surface, route the bounded docs update to `doc-writer` before final gates.

Report evidence:

- docs impact decision
- docs paths changed or no-op rationale
- deferral target when broader workflow guidance belongs to `iss-00306`

Closure:

- CLOS-011, AC-014

Step-local test cards:

- Card S90-A:
  - 前提: S01-S08 implementation is complete enough to know the shipped command surface.
  - 操作: Inspect existing user-facing docs and command references for required immediate updates.
  - 期待結果: `report.md` records either changed docs with verification or a no-op/defer rationale pointing to `iss-00306`.
  - 失敗検出: User-facing docs become stale for commands introduced by this Issue, or broad workflow docs are rewritten outside this Issue scope.
  - 検証方法: docs impact inspection recorded in `report.md`; fresh spec-reviewer checks the disposition.
  - Closure: CLOS-011.

### S99: Final verification and closeout

Goal:

- Produce finish-ready evidence for this intermediate Issue and defer PR delivery to `iss-00307`.

Commands:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption or selected_skeleton_fill or authoring_validate"
uv run pytest tests/cli_runtime/test_authoring.py -q
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption --help
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill --help
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests/cli_runtime/test_authoring.py
```

Report evidence:

- implemented scope summary
- files changed inventory
- command help summary
- positive fixture summary
- negative fixture matrix summary
- redaction / forbidden authority evidence
- no canonical docs write by runtime command
- no `.assurance.json` mutation by runtime command
- known residual risks
- deferred PR delivery rationale

Closure:

- CLOS-011 through CLOS-016

Step-local test cards:

- Card S99-A:
  - 前提: S01-S08 implementation and report evidence are complete.
  - 操作: Run the final command bundle listed above.
  - 期待結果: Focused tests, full authoring tests, help commands, `validate`, `assurance verify`, `git diff --check`, and local-wrapper scan all pass or, for the scan, return no matches.
  - 失敗検出: Any command fails for a change-caused reason, help remains deferred, or local wrapper dependency appears in shipped runtime/scripts/tests.
  - 検証方法: final command bundle output recorded in `report.md`.
  - Closure: CLOS-012 through CLOS-015.
- Card S99-B:
  - 前提: Final verification bundle passes and reviewers have no blocking findings.
  - 操作: Commit, push, run `issue finish`, and defer PR delivery to `iss-00307`.
  - 期待結果: Branch is pushed, Issue finishes, active issue clears or moves by workflow, and no per-Issue PR is created.
  - 失敗検出: PR is created for this intermediate Issue, branch is unpushed, or `issue finish` reports an unmet gate.
  - 検証方法: git status/log/push output and `./spec-dock/scripts/spec-dock issue finish` output recorded in `report.md`.
  - Closure: CLOS-016.

## 4. Files Expected To Change

Provider-side:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/issue_draft_adoption_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/selected_skeleton_fill_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/issue_draft_adoption_validation.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/selected_skeleton_fill_validation.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/issue_draft_adoption_renderer.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/selected_skeleton_fill_renderer.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_draft_adoption.py`
- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_selected_skeleton_fill.py`

Dogfood mirror:

- corresponding files under the dogfood `spec-dock/scripts` runtime tree.

Tests:

- `tests/cli_runtime/test_authoring.py`

Issue docs:

- active Issue `requirement.md`, `design.md`, `plan.md`, `report.md`
- `.assurance.json` only through SpecDock assurance workflow, not authoring runtime command

## 5. Amendment Triggers

Return to planning if:

- implementation requires canonical docs write in runtime command
- `.assurance.json` mutation becomes necessary inside authoring runtime
- command needs `--force`
- validator pass must imply canonical adoption or reviewer pass
- automatic issue creation is pulled into this Issue
- report path safety cannot be enforced
- selected skeleton schema cannot be derived from existing templates without guessing

## 6. Reviewer Focus

Spec reviewer:

- Ensure requirement/design/plan preserve authority boundary and distinguish validation from adoption.
- Ensure PR delivery defer to `iss-00307` is explicit.

Code reviewer:

- Check fail-closed status mapping.
- Check path safety and no secret leak.
- Check provider/dogfood parity.
- Check no canonical docs or `.assurance.json` mutation occurs in authoring runtime.

QA reviewer:

- Check acceptance criteria coverage and negative fixture matrix.
- Check command help and JSON/text output semantics.
- Check dogfood mirror smoke and compatibility wrapper behavior.
