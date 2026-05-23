---
種別: 実装報告書（Issue）
ID: "iss-00114"
タイトル: "Delegated Draft Evidence Schema"
関連GitHub: ["#114"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00114 Delegated Draft Evidence Schema — 実装報告（Observed Evidence Ledger）

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Raised By | Trigger / Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | implementation | orchestrator | report surfaces needed a schema that works for Initiative / Epic / Issue and active-none placeholders | scope-specific schemas; common schema block; runtime validation | Use one common Markdown evidence schema in report templates and a compact reference schema in active-none reports. | The Epic requires report evidence surfaces, not runtime enforcement; a common block keeps promotion rules consistent across scopes. | applied | provider and dogfooding report surfaces; targeted init/update assertions | none |
| D-002 | resolved | test-strategy | reviewer / dev-coder | QA/spec reviewers recommended stronger active-none parity and all failure-mode assertions | leave inspect-only; add assertions | Strengthen `tests/test_init_update.py` to assert all required failure modes and checked-in active-none report parity. | This directly protects tc-009/tc-010 and provider/consumer drift handling without changing runtime behavior. | applied | `test_init_creates_expected_structure`; `test_checked_in_dogfooding_active_none_reports_match_provider_assets`; 4 targeted tests OK | none |
| D-003 | resolved | test-strategy | code-reviewer | failure-mode labels alone did not prove each row carried verdict/action/evidence/eligibility | accept P2; defer; assert full rows | Assert each required failure-mode table row with canonical verdict, next action, non-empty evidence path, and ineligible promotion eligibility. | The issue contract is a scaffold evidence schema; malformed rows should fail targeted tests before promotion. | applied | first strengthened test failed on row drift, schema normalized, 4 targeted tests OK | none |

## 実装サマリー

- `workflow_spec_authoring.md` に delegated draft lifecycle、promotion-ineligible states、required evidence fields、`source_snapshot`、required failure modes を追加した。
- Initiative / Epic / Issue の provider report templates と active-none report placeholders に Delegated Draft Evidence schema を追加した。
- Dogfooding mirrors を current checkout から更新し、targeted init/update tests、provider/mirror parity、validate/sync/diff-check で確認した。

## Delegated Draft Evidence

- delegated authoring use:
  - not used for this implementation report
- If not used:
  - manual implementation path; no delegated draft was used as promotion evidence.

| role | phase | scope | consent | source artifacts | draft artifact path | status | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | implementation | iss-00114 | N/A | active issue docs and parent Epic docs | N/A | not used | manual implementation | N/A | none | code/QA/spec pass | no delegated draft promotion |

## 実装記録（セッションログ）

### 2026-05-23 S01 Provider Draft Evidence Schema

#### 対象
- Step: S01
- AC/EC: AC-001
- Planned source:
  - `plan.md` section: `S01 — Provider source update`
  - closure ids: tc-001, tc-006, tc-007, tc-008, tc-009, tc-010

#### 実施内容
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` に `delegated draft evidence schema` section を追加した。
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md` に `Delegated Draft Evidence` section と failure-mode table を追加した。
- `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md` に compact reference schema を追加した。

#### 実行コマンド / 結果
```bash
rg -n "Delegated Draft Evidence|delegated draft evidence schema|Lifecycle states|Promotion-ineligible states|missing consent|reviewer unavailable/denied/waived/provisional" \
  src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md \
  src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md \
  src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md

# pass
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S01 | alternative | inspect-only | Provider workflow/report surfaces did not contain a delegated draft evidence schema before this issue. | pre-change `rg` during issue intake | pass | docs/scaffold-content issue; no failing-first runtime test required. |
| S01 | Green | provider source contains draft evidence schema contract | Provider workflow doc, report templates, and active-none report surfaces contain lifecycle, promotion, evidence, and failure-mode schema. | targeted `rg`; provider diff inspection | pass | Covers provider-side portions of tc-001, tc-006, tc-007, tc-008, tc-009, tc-010. |
| S01 | Refactor | guardrail satisfied / no refactor needed | Changes are limited to provider docs/templates/placeholders. | `git diff --check` | pass | No runtime validation, dogfooding mirror update, tests, or write-capable delegation added in S01. |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-006, tc-007, tc-008, tc-009, tc-010 | target provider source is updated and inspected | provider workflow, report templates, and active-none reports contain the required schema terms and complete failure-mode rows | pass | code-reviewer, QA, and final spec-reviewer pass |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | inspect-only | schema absent from provider surfaces | provider diff + targeted `rg` | pass | provider contract exists |
| tc-006 | S01 | yes | inspect-only | lifecycle states absent | targeted `rg` fragments | pass | all eight states present |
| tc-007 | S01 | yes | inspect-only | promotion-ineligible states absent | targeted `rg` fragments | pass | stale/rejected/superseded/blocked ineligible |
| tc-008 | S01 | yes | inspect-only | report evidence fields absent | targeted `rg` fragments | pass | required evidence fields present |
| tc-009 | S01 | yes | inspect-only | failure-mode table absent | targeted `rg` fragments | pass | expected verdict / next action / evidence path / eligibility present |
| tc-010 | S01 | yes | inspect-only | report surfaces absent | provider report template and active-none diff | pass | provider surfaces carry schema |

### 2026-05-23 S02 Dogfooding Parity and Verification

#### 対象
- Step: S02
- AC/EC: AC-002, EC-002
- Planned source:
  - `plan.md` section: `S02 — Dogfooding parity and verification`
  - closure ids: tc-002, tc-005, tc-010

#### 実施内容
- provider docs から `spec-dock/docs/workflow_spec_authoring.md` を更新し、dogfooding docs mirror の drift を解消した。
- `spec-dock/docs/workflow_spec_authoring.md`、`spec-dock/templates/{initiative,epic,issue}/report.md`、`spec-dock/system/active-none/{initiative,epic,issue}/report.md` に schema が反映されたことを確認した。
- provider/mirror parity と targeted tests、validate/sync を確認した。

#### 実行コマンド / 結果
```bash
cp src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md spec-dock/docs/workflow_spec_authoring.md

# dogfooding workflow docs mirror refreshed from provider source

python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure -v

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_templates_match_provider_assets -v

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_active_none_reports_match_provider_assets -v

OK

./spec-dock/scripts/spec-dock validate

# spec-dock: ok (validate) nodes=57

./spec-dock/scripts/spec-dock sync

# spec-dock: ok (sync) wrote generated index/tree/deps/dashboard artifacts

git diff --check

# pass
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S02 | alternative | inspect-only parity evidence | Dogfooding docs mirror needed refresh after provider change. | `cmp -s src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md spec-dock/docs/workflow_spec_authoring.md` initially failed, then passed after provider copy | pass | template mirrors already matched provider; docs mirror was refreshed. |
| S02 | Green | dogfooding mirrors/tests/validation reflect provider change | mirrors contain the schema; targeted init/update, docs/template parity, active-none parity tests pass; validate/sync pass. | 4 targeted unittests, validate, sync | pass | Covers tc-002, tc-005, tc-009, tc-010. |
| S02 | Refactor | guardrail satisfied / no refactor needed | No unrelated implementation refactor; no runtime validation added. | `git diff --check` | pass | scope limited to docs/templates/placeholders/tests/report. |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S02 | tc-002, tc-005, tc-010 | parity/verification evidence is recorded | dogfooding mirrors reflect provider schema; tests/validate/sync/diff-check pass | pass | code-reviewer, QA, and final spec-reviewer pass |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-002 | S02 | yes | inspect-only + targeted test | dogfooding mirrors needed refresh | local update + targeted tests + validate/sync | pass | mirrors reflect provider change |
| tc-005 | S02 | yes | inspect-only + targeted test | possible provider/consumer drift | docs/templates/active-none provider-mirror parity tests | pass | no unintended drift |
| tc-009 | S02 | yes | inspect-only + targeted test | failure-mode table coverage needed full required-mode assertions | strengthened init structure test | pass | all required failure modes asserted |
| tc-010 | S02 | yes | inspect-only + targeted test | dogfooding report surfaces needed schema | local update + targeted tests, including active-none parity | pass | report surfaces carry schema |

## Closure Coverage

| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | provider diff + targeted `rg` | pass | provider schema exists |
| tc-002 | S02 | dogfooding update + validate/sync | pass | parity evidence recorded |
| tc-003 | S99 | final spec-reviewer | pass | final spec-reviewer found no findings after S01/S02 evidence separation fix |
| tc-004 | S90 | provider/mirror/test paths verified | pass | EC-001 not triggered |
| tc-005 | S02 | provider/mirror parity test | pass | no drift |
| tc-006 | S01 | lifecycle state inspection | pass | all states present |
| tc-007 | S01 | promotion-ineligible inspection | pass | ineligible states present |
| tc-008 | S01 | evidence field inspection | pass | required fields present |
| tc-009 | S01/S02 | provider failure-mode inspection plus S02 required-mode and complete-row assertions | pass | failure-mode table fields, all required modes, canonical verdict/action, evidence path, and eligibility present |
| tc-010 | S01/S02 | provider + dogfooding report surfaces + active-none parity test | pass | report surfaces carry schema |

## Closure Delta

| change | closure id | test id alias | resolves to closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| strengthened assertion | tc-009 | failure-mode table row assertions | tc-009 | code-reviewer P2 requested complete row coverage | no | yes |

## Workflow Delegation Consent

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user objective to execute all Epic issues with referenced issue-execution workflow | current repo/worktree | iss-00114 | current session | doc-writer, dev-coder, spec-reviewer, code-reviewer, qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

## Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | provider docs/templates/placeholders update | doc-writer | provider workflow/report schema surfaces | active issue requirement/design/plan and parent Epic docs | provider docs/templates/active-none reports | runtime validation, write-capable delegation, `.github/agents`, GitHub state, dogfooding mirrors/tests | diff inspection, spec review | scope expansion or reviewer fail | changed files, verification, risks | pass |
| S02 | delegated | dogfooding parity and targeted tests | dev-coder | dogfooding mirrors, parity evidence, and targeted assertions | active issue plan and provider assets | dogfooding docs/templates/active-none reports, tests, report evidence | unrelated implementation refactor, runtime validation, GitHub state | targeted tests, validate/sync, diff-check | validation/test failure or unexpected drift | command output, changed files, verification result | pass |

## Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01/S02 | step reviewer | code-reviewer | fresh | pass | N/A | proceed to final spec review | P2 row-coverage finding accepted and fixed after pass |
| S01/S02 | QA reviewer | qa-reviewer | fresh | pass | N/A | proceed to final spec review | no P0/P1 test adequacy issues remained before row-coverage tightening |
| S01/S02/S99 | final reviewer | spec-reviewer | fresh | pass | N/A | proceed to commit and issue finish | prior P2 resolved; S01 provider-only evidence and S02 dogfooding/tests evidence are separated |

## Step Commit Gate

| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01/S02 | ready to commit | provider schema surfaces, dogfooding mirrors, targeted tests, report evidence | pending | pending | N/A | N/A | N/A | N/A |

## 変更したファイル

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` - delegated draft evidence schema.
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md` - report evidence schema surfaces.
- `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md` - active-none schema reference surfaces.
- `spec-dock/docs/workflow_spec_authoring.md` - dogfooding mirror.
- `spec-dock/templates/{initiative,epic,issue}/report.md` - dogfooding report template mirrors.
- `spec-dock/system/active-none/{initiative,epic,issue}/report.md` - dogfooding active-none mirrors.
- `tests/test_init_update.py` - targeted scaffold assertions.
- `spec-dock/active/issue/report.md` - observed evidence ledger.

## Final Quality Gate

### S90 Docs Impact Resolution
| target | update required | owner | evidence | spec-reviewer result |
|---|---|---|---|---|
| workflow authoring docs | yes | approved-local-execution | delegated draft evidence schema added and normalized | pass |
| report templates | yes | approved-local-execution | Initiative / Epic / Issue templates carry evidence and failure-mode tables | pass |
| active-none reports | yes | approved-local-execution | compact schema reference present and normalized | pass |
| EC-001 documented uncertainty path | no uncertainty triggered | orchestrator | provider/mirror/test paths verified | pass |

### Final QA Gate
| reviewer | scope | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | targeted scaffold tests and active-none parity coverage are sufficient for Markdown scaffold/report schema | 4 targeted unittests, validate, sync, git diff --check | pass |

### Final Code Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | previous P1 fixed; P2 row-coverage finding accepted and fixed with full failure-mode row assertions | 2 | pass |

### Final Spec Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | no findings after S01 provider-only evidence and S02 dogfooding/tests evidence separation fix | 2 | pass |

### Final Commit
| final report ledger | final commit scope | post-commit external evidence destination | result |
|---|---|---|---|
| S01/S02 evidence recorded; code/QA/spec pass | provider schema surfaces, dogfooding mirrors, tests, report | final response / Epic PR / GitHub issue lifecycle | ready to commit |

## 遭遇した問題と解決
- 問題: なし。
  - 解決: N/A

## 学んだこと
- Report evidence schema は templates と active-none placeholders の両方に置くと、active 未設定時にも reviewer が必要な evidence fields を発見しやすい。

## 今後の推奨事項
- 後続 Issue では、この schema を前提に role skill、phase gate、host adapter の evidence を記録する。

## 省略/例外メモ
- EC-001 は対象 path / host uncertainty が発生しなかったため、not-triggered closure として S90 に記録した。
