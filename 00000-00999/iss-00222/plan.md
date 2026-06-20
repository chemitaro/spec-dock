---
種別: 実装計画書（Issue）
ID: "iss-00222"
タイトル: "Forbid Checks API In PR Observation"
関連GitHub: ["#222"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00222 Forbid Checks API In PR Observation — 実装計画

## この計画で満たす要件ID

- AC:
  - AC-001 Forbidden Checks API surface を呼ばない
  - AC-002 Actions green は pass として観測できる
  - AC-003 Actions failure / pending / running は Actions のみで判定される
  - AC-004 zero Actions runs は pass しない
  - AC-005 Review/comment/thread 監視を維持する
  - AC-006 Doctor は不要な Checks/status permissions を要求しない
  - AC-007 Docs / skill guidance は API 禁止と語彙禁止を混同しない
- EC:
  - EC-001 Actions API unavailable
  - EC-002 Jobs API unavailable but run-level conclusion is failed
  - EC-003 External required check が failed / pending
  - EC-004 Status-only repository
  - EC-005 Historical compatibility names
- 制約:
  - Provider-side shipped assets first.
  - `checks` 語は禁止しない。GitHub Checks API / status rollup surface の利用を禁止する。
  - Review/comment/thread observation を弱めない。

## 依存関係から導く実装順序

1. `pr_observation_checks.py` が CI collection / classification の source of truth なので、最初に forbidden API guard と Actions-only collector を閉じる。
2. `pr_observation_snapshot.py` / `pr_observation_wait.py` は CI payload consumer なので、collector の payload semantics 固定後に更新する。
3. `pr_review_snapshot.py` は sibling collector なので、CI forbidden guard が効いた状態で regression として維持確認する。
4. `github_capability_cli.py` / `doctor.py` は runtime diagnostics consumer なので、Actions-only contract 固定後に capability guidance を同期する。
5. Shipped skill/docs/template wording は実装 semantics と doctor semantics が固まった後に更新する。
6. 最後に S99 で QA / code / spec の issue-wide gate を通す。

## ステップ一覧

- S01: Forbidden CI surface guard and collector boundary
  - 依存: approved requirement/design/ADR
  - unblock: S02, S03, S04
  - 対象: `pr_observation_checks.py`, shipped script tests
  - レビューゲート: code-reviewer
- S02: Actions-only CI state classification
  - 依存: S01
  - unblock: S03, S05, S90
  - 対象: `pr_observation_checks.py`, shipped script tests
  - レビューゲート: code-reviewer
- S03: Snapshot/wait compatibility and decision consumption
  - 依存: S02
  - unblock: S90, S99
  - 対象: `pr_observation_snapshot.py`, `pr_observation_wait.py`, focused tests
  - レビューゲート: code-reviewer
- S04: Review/comment/thread preservation regression
  - 依存: S01
  - unblock: S99
  - 対象: review/snapshot tests; `pr_review_snapshot.py` only if narrow fix is required
  - レビューゲート: code-reviewer
- S05: Doctor/capability migration
  - 依存: S02
  - unblock: S90, S99
  - 対象: `github_capability_cli.py`, `doctor.py`, doctor tests
  - レビューゲート: code-reviewer
- S90: Docs impact resolution and skill wording
  - 依存: S02, S03, S05
  - unblock: S99
  - 対象: shipped skill docs/templates/usage wording
  - レビューゲート: spec-reviewer
- S99: Final quality gate
  - 依存: S01-S05, S90
  - 対象: report evidence / final review only
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, final spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S01
- AC-002 -> S02, S03
- AC-003 -> S02, S03
- AC-004 -> S02, S03
- AC-005 -> S04
- AC-006 -> S05
- AC-007 -> S90
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S90
- EC-004 -> S02
- EC-005 -> S01, S90

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | acceptance | AC-001 | CI collector never calls `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or `gh pr checks` equivalent | fake `gh` fails on forbidden surfaces | forbidden fallback regression | yes | red-required | Test Contract Closure + fake-gh call log |
| cl-002 | S02 | acceptance | AC-002 | Actions success terminal state can produce passed CI without Checks/status limitation | workflow runs/jobs fixture for current head SHA | loss of valid Actions pass | yes | red-required | Test Contract Closure + JSON payload |
| cl-003 | S02 | acceptance | AC-003 | Actions failure/pending/running states classify from Actions only | workflow run/job fixtures for each state family | mixed-source or stale fallback classification | yes | red-required | Test Contract Closure + JSON payload |
| cl-004 | S02 | negative | AC-004, EC-004 | zero Actions runs and status-only repos never become passed | no Actions runs plus legacy green fixture | false green pass | yes | red-required | Test Contract Closure + wait decision evidence |
| cl-005 | S02 | edge | EC-001 | Actions API unavailable becomes unknown/human gate without fallback | permission/rate/schema/transient failure fixture | silent fallback to forbidden source | yes | red-required | limitations payload + test result |
| cl-006 | S02 | edge | EC-002 | failed run-level conclusion remains failed when jobs API is unavailable | run failed, jobs endpoint unavailable | masking failed CI as unknown/pass | yes | red-required | JSON payload + test result |
| cl-007 | S03 | compatibility | AC-002, AC-003, AC-004 | snapshot/wait progress and fingerprint use Actions summary, not legacy check fields | observation payload with deprecated legacy fields empty | downstream decision drift | yes | red-required | wait result + fingerprint test |
| cl-008 | S04 | regression | AC-005 | issue comments, PR reviews, review comments, reviewThreads remain present | PR fixture with review blockers and forbidden CI endpoints blocked | accidental review-observation weakening | yes | red-required | review payload test |
| cl-009 | S05 | acceptance | AC-006 | doctor does not require Checks/statuses/status rollup permissions for PR observation repair | token capability fixture without Checks/statuses permissions | false repair blocker | yes | red-required | doctor output test |
| cl-010 | S90 | docs | AC-007, EC-003 | guidance says API/surface is forbidden, not the word `checks`; external checks are intentionally unobserved | shipped skills/templates/docs inspection | future rollback through confusing wording | yes | inspect-only | docs diff + spec-reviewer pass |
| cl-011 | S90 | docs | EC-005 | compatibility names may remain but must say Actions-only behavior | `fetch_pr_checks_snapshot.sh` and skill docs wording | accidental breaking rename or misleading compatibility | yes | inspect-only | docs diff + static scan |
| cl-012 | S99 | gate | workflow_issue.md | final QA/code/spec gates pass and report ledgers close all required rows | issue-wide diff and report evidence | incomplete delivery reported as complete | yes | manual-required | Final QA/Code/Spec Gate entries |

## レビュー / QA ゲート方針

- S01-S05:
  - worker: dev-coder
  - reviewer: code-reviewer
  - commit: each step is one commit scope after reviewer pass and report evidence update.
- S90:
  - worker: doc-writer
  - reviewer: spec-reviewer
  - commit: docs-only commit scope after reviewer pass.
- S99:
  - qa-reviewer checks test sufficiency and missing high-value coverage.
  - issue-wide code-reviewer checks integrated diff and responsibility boundaries.
  - final spec-reviewer checks requirement/design/plan/report/docs alignment.

## 実装ステップ

### S01 — Forbidden CI Surface Guard And Collector Boundary

- behavior goal:
  - PR observation CI collection does not call forbidden GitHub Checks API, commit status, PR status rollup, or `gh pr checks` equivalent surface.
- target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- planned contract:
  - scope:
    - Remove or bypass forbidden collectors/fallbacks in CI collector.
    - Add fail-fast fake-gh tests for forbidden calls.
    - Keep compatibility names if needed; do not treat `checks` token as banned.
  - test obligation:
    - cl-001 and cl-011.
  - red evidence:
    - fake `gh` must fail if `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or checks rollup equivalent is requested.
  - green verification:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "observation or checks or github_pr"`
    - static inspection of provider-side CI collector for forbidden decision calls.
  - amendment trigger:
    - Any need to retain forbidden API calls or broadly rename public compatibility surfaces.

#### Delegation Contract

- delegated role: dev-coder
- input docs: `requirement.md`, `design.md`, accepted ADR, compatibility interview, `plan.md`
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - canonical docs/report
  - dogfooding mirror `.agents/` as implementation source
  - review/comment collector behavior
  - broad rename/removal of `checks` named compatibility surfaces
- acceptance criteria:
  - cl-001 passes and forbidden surfaces are never called.
- required verification:
  - focused pytest and static inspection.
- reviewer focus:
  - code-reviewer: fake-gh sensitivity, no forbidden fallback, narrow scope.
- stop conditions:
  - fake-gh cannot detect forbidden calls; required behavior appears to require forbidden API; allowed paths insufficient.
- output required:
  - changed files, red/green evidence, static inspection note, unresolved risks, ledger note or no material decision statement.

#### 具体テストケース一覧

- `tc-s01-001` negative: forbidden API calls fail the CI collector
  - 前提: fake `gh` exits non-zero and logs when `/check-runs`, `/commits/{sha}/status`, `statusCheckRollup`, or checks rollup equivalent is requested.
  - 操作: run the PR observation CI collection path for a PR head SHA.
  - 期待結果: no forbidden call is logged and the collector returns an Actions-only payload or non-pass Actions unavailable state.
  - 失敗検出: any forbidden call fails the test even if final CI state would otherwise pass.
  - 検証方法: focused test in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: cl-001.
- `tc-s01-002` static: compatibility names are not treated as a word ban
  - 前提: provider-side source may still include historical names such as `fetch_pr_checks_snapshot.sh`.
  - 操作: run or inspect the static forbidden-surface check.
  - 期待結果: the scan targets forbidden endpoint/field/CLI usage, not every occurrence of `checks`.
  - 失敗検出: a test fails only because a compatibility filename contains `checks`.
  - 検証方法: code-reviewer inspection plus any static assertion added in the focused test.
  - 関連 closure id: cl-011.

#### Step Closure Contract

- close condition: cl-001 is covered by red-required evidence and green verification; no review/comment behavior changed.
- report evidence: Implementation Delegation Gate S01, Step Contract Closure, Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S02 — Actions-Only CI State Classification

- behavior goal:
  - Actions workflow runs/jobs alone determine CI state; zero/unavailable Actions evidence never becomes pass through legacy fallback.
- depends on: S01
- target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- planned contract:
  - scope:
    - Implement Actions run/job summary and classification.
    - Add explicit source policy marker such as `github_actions_only`.
    - Remove `ci_coverage_limited_to_github_actions`.
  - test obligation:
    - cl-002, cl-003, cl-004, cl-005, cl-006.
  - red evidence:
    - fixtures for success, failure, pending/running, zero runs, Actions unavailable, and jobs unavailable with failed run.
  - green verification:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "actions or observation or checks"`
  - amendment trigger:
    - New status vocabulary or changed pass/fail semantics beyond design.

#### Delegation Contract

- delegated role: dev-coder
- input docs: requirement/design/ADR/interview, `plan.md`, S01 evidence
- allowed paths:
  - `pr_observation_checks.py`
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - doctor/docs/merge-preparer wording
  - review/comment collector behavior
  - GitHub UI mergeability or branch protection inference
- acceptance criteria:
  - AC-002, AC-003, AC-004, EC-001, EC-002, EC-004 close through Actions-only fixtures.
- required verification:
  - focused pytest and JSON payload assertions.
- reviewer focus:
  - code-reviewer: status classification, no fallback, source-policy marker, edge-case coverage.
- stop conditions:
  - payload shape cannot support downstream consumers without broader compatibility design.
- output required:
  - changed files, test result, payload shape notes, unresolved compatibility risks.

#### 具体テストケース一覧

- `tc-s02-001` acceptance: Actions success passes
  - 前提: current head SHA has Actions workflow runs/jobs with terminal success.
  - 操作: run CI collection.
  - 期待結果: CI state is passed and no Checks/statuses limitation is emitted.
  - 失敗検出: passed depends on forbidden legacy fields or missing source-policy marker.
  - 検証方法: focused pytest fixture.
  - 関連 closure id: cl-002.
- `tc-s02-002` acceptance: Actions non-success states do not pass
  - 前提: fixtures cover failure, queued, in_progress, pending, cancelled, timed_out, and unknown combinations.
  - 操作: run CI collection for each fixture.
  - 期待結果: each state maps to failed, pending, running, or unknown according to Actions evidence only.
  - 失敗検出: any state becomes passed through check-runs/statuses fallback.
  - 検証方法: parameterized focused pytest.
  - 関連 closure id: cl-003.
- `tc-s02-003` negative: zero Actions runs do not pass
  - 前提: Actions runs list is empty and legacy check/status fixtures would be green if called.
  - 操作: run CI collection.
  - 期待結果: CI is none/unknown/human gate, never passed, and legacy fixtures are not called.
  - 失敗検出: pass state or legacy call log entry.
  - 検証方法: focused pytest with fake-gh forbidden guard.
  - 関連 closure id: cl-004.
- `tc-s02-004` edge: Actions unavailable does not fallback
  - 前提: Actions API returns permission denied, rate limit, transient failure, or malformed response.
  - 操作: run CI collection.
  - 期待結果: output records unavailable/unknown/human gate and no forbidden fallback.
  - 失敗検出: fallback to check-runs/statuses or missing limitation/diagnostic.
  - 検証方法: focused pytest fixture.
  - 関連 closure id: cl-005.
- `tc-s02-005` edge: failed run remains failed when jobs are unavailable
  - 前提: run-level conclusion is failure and jobs endpoint is unavailable.
  - 操作: run CI collection.
  - 期待結果: CI failed is preserved and job detail unavailable is recorded.
  - 失敗検出: failed run becomes unknown/pass or check-runs fallback is called.
  - 検証方法: focused pytest fixture.
  - 関連 closure id: cl-006.

#### Step Closure Contract

- close condition: cl-002 through cl-006 have passing tests and reviewer pass.
- report evidence: Implementation Delegation Gate S02, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S03 — Snapshot/Wait Compatibility And Decision Consumption

- behavior goal:
  - Snapshot and wait flows consume Actions-only CI payload without deriving decisions from legacy compatibility fields.
- depends on: S02
- target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
- planned contract:
  - scope:
    - Update progress/fingerprint/wait decision to use Actions summary and source policy.
    - Keep legacy fields empty/deprecated if needed, not evidence.
  - test obligation:
    - cl-007.
  - green verification:
    - focused pytest around wait/snapshot plus S02 collector tests.
  - amendment trigger:
    - Removing public payload fields or changing shell entrypoint contract.

#### Delegation Contract

- delegated role: dev-coder
- input docs: requirement/design/ADR/interview, `plan.md`, S02 payload evidence
- allowed paths:
  - `pr_observation_snapshot.py`
  - `pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - bounded discovery under `tests/unit/infra/` only if existing PR observation fixtures require local reuse
- forbidden changes:
  - Doctor migration
  - Skill/docs wording except inseparable script usage line
  - broad JSON contract removal without design amendment
- acceptance criteria:
  - cl-007 closes; wait/snapshot do not use legacy compatibility fields as decision evidence.
- required verification:
  - focused tests plus payload/fingerprint inspection.
- reviewer focus:
  - code-reviewer: downstream consistency, compatibility fields, no hidden fallback.
- stop conditions:
  - downstream contract cannot be preserved without canonical design change.
- output required:
  - changed files, verification result, payload/fingerprint compatibility note.

#### 具体テストケース一覧

- `tc-s03-001` compatibility: wait uses Actions summary
  - 前提: snapshot payload has Actions success summary and empty/deprecated legacy fields.
  - 操作: run wait decision path.
  - 期待結果: wait can conclude eligible/passed from Actions summary only.
  - 失敗検出: wait requires non-empty `ci.check_runs` or required check rollup.
  - 検証方法: focused pytest.
  - 関連 closure id: cl-007.
- `tc-s03-002` negative: contradictory legacy fields do not override Actions
  - 前提: test fixture injects deprecated legacy fields that would imply pass/fail differently from Actions.
  - 操作: run snapshot/wait fingerprint and decision logic.
  - 期待結果: decision and fingerprint use Actions summary and source policy, not legacy fields.
  - 失敗検出: legacy field changes alter CI decision.
  - 検証方法: focused pytest or characterization test.
  - 関連 closure id: cl-007.

#### Step Closure Contract

- close condition: cl-007 passes and S02 behavior still passes.
- report evidence: Implementation Delegation Gate S03, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S04 — Review/Comment/Thread Preservation Regression

- behavior goal:
  - Review/comment/thread observation remains intact while CI forbidden surfaces are blocked.
- depends on: S01
- target files:
  - `tests/unit/infra/test_init_update.py`
  - `pr_review_snapshot.py` only for narrow preservation fixes
  - `pr_observation_snapshot.py` only for payload integration fixes
- planned contract:
  - scope:
    - Verify issue comments, PR reviews, review comments, requested reviewers/teams, GraphQL reviewThreads, and reviewDecision remain present.
    - Keep review GraphQL separate from CI rollup GraphQL.
  - test obligation:
    - cl-008.
  - green verification:
    - focused pytest around review payload.
  - amendment trigger:
    - Any weakening of review/comment evidence or removal of reviewThreads.

#### Delegation Contract

- delegated role: dev-coder
- input docs: AC-005, design review/comment payload contract, `plan.md`, S01 evidence
- allowed paths:
  - `tests/unit/infra/test_init_update.py`
  - bounded discovery under `tests/unit/infra/` only if existing review/snapshot fixtures require local reuse
  - `pr_review_snapshot.py` only for narrow preservation fixes
  - `pr_observation_snapshot.py` only for payload integration fixes
- forbidden changes:
  - CI collector classification changes
  - removing reviewThreads or reviewDecision observation
  - treating all GraphQL as forbidden
- acceptance criteria:
  - AC-005 closes while forbidden CI calls remain blocked.
- required verification:
  - focused pytest with review/comment/thread fixture.
- reviewer focus:
  - code-reviewer: boundary between review GraphQL and forbidden CI rollup.
- stop conditions:
  - review fixture cannot distinguish CI rollup GraphQL from review thread GraphQL.
- output required:
  - changed files or approved-no-op evidence, verification result, review payload note.

#### 具体テストケース一覧

- `tc-s04-001` regression: review evidence survives Actions-only change
  - 前提: PR fixture includes issue comments, PR reviews, review comments, unresolved reviewThreads, and forbidden CI endpoints blocked.
  - 操作: run observation snapshot/review collection.
  - 期待結果: review payload includes the review/comment/thread evidence and CI guard logs no forbidden calls.
  - 失敗検出: review blockers disappear or forbidden CI endpoint is called.
  - 検証方法: focused pytest.
  - 関連 closure id: cl-008.
- `tc-s04-002` boundary: review GraphQL is not status rollup
  - 前提: GraphQL reviewThreads query is allowed, but `statusCheckRollup` field is forbidden.
  - 操作: inspect or test GraphQL query construction.
  - 期待結果: reviewThreads/reviewDecision are retained and no status rollup field is requested.
  - 失敗検出: removing reviewThreads or requesting `statusCheckRollup`.
  - 検証方法: focused pytest or code-reviewer inspection.
  - 関連 closure id: cl-008.

#### Step Closure Contract

- close condition: cl-008 passes or is approved-no-op with existing coverage and reviewer agreement.
- report evidence: Implementation Delegation Gate S04, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S05 — Doctor/Capability Migration

- behavior goal:
  - Doctor/capability diagnostics stop treating Checks/statuses/status rollup permissions as PR observation repair requirements.
- depends on: S02
- target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- planned contract:
  - scope:
    - Change PR observation capability model to Actions read plus PR/comment read.
    - Remove repair guidance for Checks/statuses/status rollup permissions from PR observation path.
  - test obligation:
    - cl-009.
  - green verification:
    - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`
  - amendment trigger:
    - Need to change global doctor capability schema beyond PR observation.

#### Delegation Contract

- delegated role: dev-coder
- input docs: AC-006, design doctor capability section, `plan.md`, current doctor tests
- allowed paths:
  - `github_capability_cli.py`
  - `doctor.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- forbidden changes:
  - Observation script implementation
  - shipped docs wording outside runtime doctor output
  - GitHub write capability changes
- acceptance criteria:
  - AC-006 closes.
- required verification:
  - `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`.
- reviewer focus:
  - code-reviewer: capability boundaries and unrelated doctor behavior.
- stop conditions:
  - doctor architecture cannot represent Actions/read and review/comment/read separately.
- output required:
  - changed files, test result, diagnostic wording note.

#### 具体テストケース一覧

- `tc-s05-001` acceptance: doctor does not require Checks/statuses permissions
  - 前提: capability fixture has Actions read and PR/comment read, but lacks Checks and Commit statuses permissions.
  - 操作: run doctor S04 capability diagnostic.
  - 期待結果: PR observation capability is not blocked by missing Checks/statuses/status rollup permission.
  - 失敗検出: output recommends repairing Checks/statuses/status rollup for PR observation.
  - 検証方法: `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py`.
  - 関連 closure id: cl-009.
- `tc-s05-002` negative: missing Actions read remains diagnostic
  - 前提: capability fixture lacks Actions read.
  - 操作: run doctor S04 capability diagnostic.
  - 期待結果: Actions read is still reported as relevant for PR observation.
  - 失敗検出: doctor under-reports actual Actions observation blocker.
  - 検証方法: focused doctor test.
  - 関連 closure id: cl-009.

#### Step Closure Contract

- close condition: cl-009 passes and unrelated doctor behavior remains stable.
- report evidence: Implementation Delegation Gate S05, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.

### S90 — Docs Impact Resolution And Skill Wording

- behavior goal:
  - Shipped guidance reflects Actions-only CI observation, intentional losses, compatibility names, and doctor capability boundaries.
- depends on: S02, S03, S05
- target files:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` if usage text requires it
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` if usage text requires it
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
- planned contract:
  - scope:
    - Document Actions-only CI source.
    - Document external/non-Actions checks as intentionally unobserved.
    - Document compatibility names without implying GitHub Checks API usage.
    - Update merge-preparer wording so it does not overclaim all GitHub required checks are observed.
  - test obligation:
    - cl-010, cl-011.
  - red/alternative evidence:
    - inspect-only.
  - green verification:
    - docs diff inspection, static scan where practical, spec-reviewer docs/spec alignment pass.
  - amendment trigger:
    - Need to rename public compatibility surfaces or claim complete GitHub UI mergeability.

#### Delegation Contract

- delegated role: doc-writer
- input docs: requirement/design/ADR/interview, `plan.md`, S02/S03/S05 evidence
- allowed paths:
  - docs/skill/template paths listed in S90 target files.
- forbidden changes:
  - runtime Python or test files
  - canonical requirement/design/plan/report
  - historical discussions
  - dogfooding mirror `.agents/` as source of truth
- acceptance criteria:
  - AC-007, EC-003, EC-005 close in shipped guidance.
- required verification:
  - docs diff inspection and spec-reviewer docs/spec alignment.
- reviewer focus:
  - spec-reviewer: no API/word-ban confusion, no mergeability overclaim, consistency with requirement/design.
- stop conditions:
  - wording cannot be aligned without changing canonical requirement/design.
- output required:
  - changed docs files, inspection result, residual docs risk.

#### 具体テストケース一覧

- `tc-s90-001` inspect-only: Actions-only guidance is explicit
  - 前提: shipped skill docs are updated by doc-writer.
  - 操作: inspect `github-pr-observation/SKILL.md` and relevant script usage text.
  - 期待結果: guidance says Actions workflow runs/jobs are the only CI source of truth.
  - 失敗検出: guidance still describes supplemental Checks/statuses/status rollup fallback.
  - 検証方法: docs diff inspection and spec-reviewer pass.
  - 関連 closure id: cl-010.
- `tc-s90-002` inspect-only: compatibility names are not a word ban
  - 前提: compatibility files or fields with `checks` in the name remain.
  - 操作: inspect docs and compatibility usage wording.
  - 期待結果: wording explains historical naming and forbids GitHub Checks API usage, not the token `checks`.
  - 失敗検出: docs require deleting every `checks` token or imply compatibility names call Checks API.
  - 検証方法: docs diff inspection.
  - 関連 closure id: cl-011.
- `tc-s90-003` inspect-only: merge-preparer does not overclaim UI checks
  - 前提: merge-preparer skill/template wording is updated.
  - 操作: inspect merge-preparer guidance.
  - 期待結果: merge readiness wording is limited to observed Actions CI and review/thread evidence, with external/non-Actions checks recorded as intentionally unobserved residual risk when relevant.
  - 失敗検出: wording claims complete GitHub UI required-check coverage.
  - 検証方法: docs diff inspection and spec-reviewer pass.
  - 関連 closure id: cl-010.

#### Step Closure Contract

- close condition: cl-010 and cl-011 inspect-only closure pass with spec-reviewer approval.
- report evidence: Implementation Delegation Gate S90, Step/Test Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate, docs impact section.

### S99 — Final Quality Gate

- behavior goal:
  - Confirm issue-wide implementation, tests, docs, report evidence, and reviewer gates close all required requirements.
- depends on: S01-S05, S90
- target files:
  - `report.md` evidence integration by main orchestrator only.
- planned contract:
  - scope:
    - Run final validation and reviews.
    - Confirm closure index coverage.
    - Confirm no forbidden paths were edited outside approved steps.
  - test obligation:
    - cl-012.
  - green verification:
    - focused test commands from S01-S05
    - any added observation script tests
    - `./spec-dock/scripts/spec-dock validate`
    - `git status --short` and `git diff --name-only` inspection.
  - amendment trigger:
    - missing required test, failed final reviewer gate, open decision ledger entry, or closure index mismatch.

#### Delegation Contract

- delegated roles:
  - qa-reviewer, code-reviewer, spec-reviewer
- input docs:
  - requirement/design/plan/report, all changed files and evidence.
- allowed paths:
  - `report.md` evidence updates by main orchestrator.
- forbidden changes:
  - catch-up implementation in final commit
  - marking unavailable/waived/provisional review as pass
- acceptance criteria:
  - cl-012 closes.
- required verification:
  - final test subset and reviewer passes.
- reviewer focus:
  - QA: obligation coverage and missing tests.
  - Code: integrated diff and responsibility boundaries.
  - Spec: requirement/design/plan/report/docs alignment.
- stop conditions:
  - any final gate fails; report has unresolved adoption/decision entry; unreviewed implementation changes remain.
- output required:
  - final verification commands/results, reviewer verdicts, closure coverage summary, unresolved risks.

#### 具体テストケース一覧

- `tc-s99-001` manual-required: final closure coverage is complete
  - 前提: S01-S05 and S90 are closed as committed or approved-no-op.
  - 操作: inspect report closure ledgers against the Spec-Locked Closure Index.
  - 期待結果: every required closure id cl-001 through cl-012 has evidence and disposition.
  - 失敗検出: missing evidence, open closure delta, or unresolved delegated artifact adoption.
  - 検証方法: manual inspection plus final spec-reviewer pass.
  - 関連 closure id: cl-012.
- `tc-s99-002` manual-required: final reviews pass
  - 前提: issue-wide diff and test evidence are ready.
  - 操作: run qa-reviewer, issue-wide code-reviewer, and final spec-reviewer.
  - 期待結果: all three return pass; any fail is resolved through bounded follow-up and re-review.
  - 失敗検出: unavailable, waived, provisional, or failed review treated as pass.
  - 検証方法: reviewer evidence in report.
  - 関連 closure id: cl-012.

#### Step Closure Contract

- close condition:
  - Final QA, code, and spec gates pass; report ledgers close all required rows.
- residual risk:
  - PR delivery and merge preparation remain separate workflow gates after local implementation closure.

## Final Exit Contract

- All AC/EC and constraints map to closure ids.
- S01-S05 and S90 are closed as committed or approved-no-op.
- S99 final QA/code/spec pass is recorded.
- Report contains delegation, closure, tests, reviewer gates, commit gates, docs impact, final gates, and adoption evidence.
- No unresolved plan blockers or open decision ledger entries remain.
- No claim says external/non-Actions checks or full GitHub UI mergeability are observed.
