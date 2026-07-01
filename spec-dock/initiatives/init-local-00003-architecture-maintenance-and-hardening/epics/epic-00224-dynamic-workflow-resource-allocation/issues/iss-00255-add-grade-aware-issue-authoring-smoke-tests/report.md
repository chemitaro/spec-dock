---
種別: 実装報告書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
関連GitHub: ["#255"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — 実装報告

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | G4 が R0〜G3 本体ロジックを吸収するリスク | smoke-only; production repair | smoke-only | Epic plan defines G4 as integrated smoke matrix | applied | design.md; plan.md | none |
| D-002 | resolved | operation | user | Issue単位PRではなくEpic単位PRにしたい | per-issue PR; Epic single PR | Epic single PR | Epic plan was amended before G4 start | applied | epic plan; issue plan.md | Epic final quality gate |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | rejected | sub-agent system-architect | design.md plan.md report.md | draft frontmatter recorded `diff_guard_result: failed`; therefore it is not promotion evidence | discussions/20260630t204916z-disc-g4-smoke-test-design-augmentation.md | manual-authored canonical docs require fresh spec review |
| EAL-002 | rejected | sub-agent implementation-planner | plan.md report.md | draft frontmatter recorded `diff_guard_result: failed`; therefore it is not promotion evidence | discussions/20260630t204853z-disc-strict-plan-augmentation-for-g4-smoke-tests.md | manual-authored canonical docs require fresh spec review |
| EAL-003 | adopted | orchestrator manual authoring | design.md plan.md report.md | canonical docs were manually authored from Epic plan, issue requirement, workflow docs, and local test inspection; delegated drafts were reference input only, not promotion evidence | design.md plan.md report.md | fresh spec review |

## Objective Alignment Ledger

| Target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| OAL-001 | G4 remains integrated smoke and parity closure | Epic single PR policy is preserved in plan.md | low | pass |

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | requirement.md and Epic plan reviewed | none | adopted | pass | no | execute approved plan |
| design | Epic design, issue requirement, workflow docs, related tests, and rejected design draft reviewed | none | manual-authored | pass | no | execute approved plan |
| plan | issue-plan workflow, Epic plan, related tests, and rejected plan draft reviewed | none | manual-authored | pass | no | execute approved plan |

## Delegated Draft Evidence

| created_by_role | scope_id | discussion draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00255 | discussions/20260630t204916z-disc-g4-smoke-test-design-augmentation.md | design.md; plan.md; Epic plan; tests | design.md; plan.md; report.md | rejected | [] | failed | not used as promotion evidence; canonical docs are manual-authored | all draft claims requiring diff-guard adoption | none | pass | manual-authored canonical docs reviewed fresh |
| implementation-planner | iss-00255 | discussions/20260630t204853z-disc-strict-plan-augmentation-for-g4-smoke-tests.md | requirement.md; design.md; plan.md; issue-plan docs; tests | plan.md; report.md | rejected | [] | failed | not used as promotion evidence; canonical docs are manual-authored | all draft claims requiring diff-guard adoption | none | pass | manual-authored canonical docs reviewed fresh |
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring | diff-guard-failed drafts not promoted | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect / implementation-planner | used | specialist drafts were created, inspected, and rejected as promotion evidence because `diff_guard_result: failed`; canonical docs are manual-authored from Epic plan, issue requirement, workflow docs, local source/test inspection, and non-authoritative draft input; residual risk recorded in EAL-001/EAL-002/EAL-003 | pass | ready |

## Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | Kepler review_status=pass; canonical docs were manually authored from Epic plan, issue requirement, workflow docs, local source inspection, and rejected drafts as non-authoritative reference input |
| S95 | follow-up spec-review | spec-reviewer | fresh | pass | no | proceed to issue-local handoff | Confucius review_status=pass; prior P1/P2 resolved; AC-001〜AC-008 traceable; no per-Issue PR gate implied |

## Session Log

### 2026-07-01 Planning hardening

- Step: planning gate before execution.
- AC: AC-001〜AC-008.
- Planned source: issue requirement/design/plan and Epic single PR plan.
- Actions:
  - Started `iss-00255`.
  - Confirmed `guidance issue-planning` blocked on `design-not-substantive`.
  - Requested system-architect and implementation-planner discussion drafts.
  - Rejected both delegated drafts as promotion evidence because each recorded `diff_guard_result: failed`.
  - Manually authored canonical `design.md` and `plan.md` from Epic plan, Issue requirement, workflow docs, local test inspection, and non-authoritative draft input.
- Commands:
  - `./spec-dock/scripts/spec-dock issue start iss-00255` -> pass.
  - `./spec-dock/scripts/spec-dock guidance issue-planning` -> blocked before planning hardening, reason `design-not-substantive`.

### 2026-07-01 S00 Baseline inspection

- Step: S00 Baseline inspection.
- AC: AC-001〜AC-008.
- Actions:
  - Inspected existing owner tests and provider/dogfooding template surfaces.
  - Confirmed `tests/cli_runtime/test_new.py` owns profile draft routing and no-write fail-closed smoke.
  - Confirmed `tests/cli_runtime/test_workflow.py` owns placeholder/stale readiness false-positive smoke.
  - Confirmed `tests/unit/domain/test_workflow_state.py` owns report evidence gate relation smoke.
  - Confirmed `tests/unit/infra/test_init_update.py` owns provider/dogfooding asset parity assertions.
- Commands:
  - `rg -n "draft-design|draft-plan|authorized_profile_templates|no_write|stale|profile template|issue-profiles" tests/cli_runtime/test_new.py` -> pass.
  - `rg -n "placeholder|heading|stale|report evidence|guidance_blocks|plan-not-executable|design-not-substantive|strict_legacy|report_evidence" tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py` -> pass.
  - `rg -n "_DOGFOODING_MIRROR_PROVIDER_ASSET_MAP|templates/issue-profiles|workflow_spec_authoring|phase_plan_issue|workflow_issue_doc_matches|issue-profiles" tests/unit/infra/test_init_update.py` -> pass.
  - `find src/spec_dock/assets/spec_dock/templates/issue-profiles spec-dock/templates/issue-profiles -maxdepth 2 -type f` -> pass; provider and dogfooding profile roots both expose `{lite,standard,strict,critical}/{design,plan}.md`.

### 2026-07-01 S01 / S02 / S90 Smoke implementation

- Step: S01 Profile plan smoke, S02 Draft routing and fail-closed smoke, S90 Docs / parity impact.
- AC: AC-001, AC-002, AC-003, AC-004, AC-007.
- Actions:
  - Added Lite to the authorized profile draft generation smoke.
  - Added draft-plan assertions that Lite does not include `commit候補:`, `static analysis / lint:`, or the PR-after-CI quality-gate text.
  - Added draft-plan assertions that Standard / Strict / Critical include final quality or safety gate text with `static analysis / lint:`, `tests:`, `report:`, and `commit候補:`.
  - Updated the test helper so synthetic `.assurance.json` profile switching recomputes classification through the runtime classifier instead of hand-copying classifier output.
  - Added `templates/issue-profiles/lite/plan.md` to provider/dogfooding parity coverage.
- Commands:
  - `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` -> pass, 4 selected; missing / invalid / stale / unsupported-profile no-write states cover both `draft-design` and `draft-plan`.
  - `uv run pytest tests/unit/infra/test_init_update.py -k "issue_247_grade_profile_template_followup_contract_assets"` -> pass, 1 selected.

### 2026-07-01 S03 / S04 Existing owner verification

- Step: S03 Readiness regression smoke, S04 Evidence gate smoke.
- AC: AC-005, AC-006.
- Actions:
  - Reused existing readiness false-positive tests instead of adding duplicate fixtures.
  - Reused existing report evidence gate positive/negative tests instead of adding duplicate fixtures.
- Commands:
  - `uv run pytest tests/cli_runtime/test_workflow.py -k "placeholder or stale_source_binding"` -> pass, 16 selected.
  - `uv run pytest tests/unit/domain/test_workflow_state.py -k "report_evidence_gate"` -> pass, 42 selected.

### 2026-07-01 S95 Spec review repair

- Step: S95 Strict spec review.
- AC: AC-004, AC-006, AC-008.
- Findings:
  - Schrodinger spec-reviewer returned `review_status: fail`.
  - P1: Grade Specialist Evidence Gate incorrectly said `manual fallback | unavailable` even though specialists produced drafts that were rejected due `diff_guard_result: failed`.
  - P2: S02 no-write closure claimed missing / invalid / stale states broadly, while the smoke covered one draft type per failure mode.
- Actions:
  - Corrected Grade Specialist Evidence Gate to state that system-architect / implementation-planner drafts were used as inspected input but rejected as promotion evidence.
  - Broadened no-write smoke so both `draft-design` and `draft-plan` are checked for missing, invalid, stale, and unsupported-profile assurance states.
- Fresh review:
  - Confucius spec-reviewer returned `review_status: pass`.
  - Prior P1 and P2 were confirmed resolved.
  - AC-001〜AC-008 remained traceable, and no per-Issue PR gate was implied.

### 2026-07-01 S99 Focused verification

- Step: S99 Issue-local handoff gate.
- AC: AC-008.
- Actions:
  - Ran the combined focused test lane for G4 smoke coverage.
  - Ran whitespace diff check.
  - Ran SpecDock validation.
  - Did not create a per-Issue PR; Epic final PR gate remains owned by Epic plan after all corrective Issues finish.
- Commands:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py tests/unit/infra/test_init_update.py -k "authorized_profile_templates or profile_drafts_fail_closed or placeholder or stale_source_binding or report_evidence_gate or issue_247_grade_profile_template_followup_contract_assets"` -> pass, 74 selected; rerun after S95 repair also pass, 74 selected.
  - `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` -> pass, 4 selected after fixture type cleanup.
  - `git diff --check` -> pass.
  - `./spec-dock/scripts/spec-dock validate` -> pass, nodes=160.

## Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| planning | C-G4-001〜C-G4-008 | design/plan/report are substantive and reviewer-ready | design.md; plan.md; report.md; fresh spec-reviewer pass | pass | execution planning handoff ready |
| S00 | C-G4-001〜C-G4-008 | owner file mapping is known and no upstream body ownership is required | Session Log S00; related `rg` and `find` commands | pass | G4 remains smoke/parity/report scope |
| S01 | C-G4-001, C-G4-002 | Lite negative and Standard+ positive profile plan smoke passes | `tests/cli_runtime/test_new.py`; focused pytest pass | pass | runtime/profile template body unchanged |
| S02 | C-G4-003, C-G4-004 | draft routing and no-write fail-closed smoke passes | `tests/cli_runtime/test_new.py`; focused pytest pass | pass | success path and missing / invalid / stale / unsupported-profile no-write paths covered |
| S03 | C-G4-005 | placeholder/stale readiness false positives stay blocked | `tests/cli_runtime/test_workflow.py`; focused pytest pass | pass | existing owner tests reused |
| S04 | C-G4-006 | report evidence gate relation is observable | `tests/unit/domain/test_workflow_state.py`; focused pytest pass | pass | existing owner tests reused |
| S90 | C-G4-007 | provider/dogfooding parity includes grade profile templates | `tests/unit/infra/test_init_update.py`; focused pytest pass | pass | added Lite plan parity assertion |
| S99 | C-G4-008 | focused tests, validate, diff check, and report evidence are complete | focused pytest 74 selected; `git diff --check`; `spec-dock validate` | pass | no per-Issue PR created |

## Test Contract Closure

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| C-G4-001 | S01 | yes | red-required | Lite case added to authorized profile draft smoke | `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` | pass | Lite draft-plan remains lightweight |
| C-G4-002 | S01 | yes | red-required | Standard+ plan gate assertions added to draft smoke | `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` | pass | Standard / Strict / Critical include final local quality gate |
| C-G4-003 | S02 | yes | covered-existing plus smoke | profile draft routing inspected and extended | `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` | pass | `authorized_profile` selects profile templates |
| C-G4-004 | S02 | yes | covered-existing plus smoke | no-write failure tests rerun for both draft types | `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or profile_drafts_fail_closed"` | pass | missing / invalid / stale / unsupported-profile assurance states remain no-write for `draft-design` and `draft-plan` |
| C-G4-005 | S03 | yes | covered-existing plus smoke | placeholder and stale readiness tests inspected | `uv run pytest tests/cli_runtime/test_workflow.py -k "placeholder or stale_source_binding"` | pass | false-positive readiness stays blocked |
| C-G4-006 | S04 | yes | covered-existing plus smoke | report evidence gate tests inspected | `uv run pytest tests/unit/domain/test_workflow_state.py -k "report_evidence_gate"` | pass | positive and negative evidence gate relations remain observable |
| C-G4-007 | S90 | yes | assertion | Lite plan parity assertion added | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_247_grade_profile_template_followup_contract_assets"` | pass | provider/dogfooding parity coverage includes Lite plan |
| C-G4-008 | S99 | yes | manual-required | focused tests, validate, diff check, and report evidence recorded | `uv run pytest ... -k "authorized_profile_templates or profile_drafts_fail_closed or placeholder or stale_source_binding or report_evidence_gate or issue_247_grade_profile_template_followup_contract_assets"`; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | pass | issue-local handoff; no per-Issue PR |

## Closure Coverage

| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| C-G4-001 | S01 | `tests/cli_runtime/test_new.py` focused smoke | pass | Lite negative assertions added |
| C-G4-002 | S01 | `tests/cli_runtime/test_new.py` focused smoke | pass | Standard+ final gate assertions added |
| C-G4-003 | S02 | `tests/cli_runtime/test_new.py` focused smoke | pass | draft routing follows `authorized_profile` |
| C-G4-004 | S02 | `tests/cli_runtime/test_new.py` focused smoke | pass | no-write fail-closed tests rerun for both draft types |
| C-G4-005 | S03 | `tests/cli_runtime/test_workflow.py` focused smoke | pass | placeholder/stale readiness tests reused |
| C-G4-006 | S04 | `tests/unit/domain/test_workflow_state.py` focused smoke | pass | report evidence gate tests reused |
| C-G4-007 | S90 | `tests/unit/infra/test_init_update.py` focused smoke | pass | Lite plan parity added |
| C-G4-008 | S99 | focused pytest, diff check, SpecDock validate, report evidence | pass | Epic final PR gate remains deferred to Epic plan |

## Final Quality Gate

| gate | scope | evidence | result |
|---|---|---|---|
| planning handoff | requirement/design/plan/report readiness | Kepler review_status=pass | pass |
| issue-local M99 | focused tests, validate, report evidence, commit candidate | focused pytest 74 selected; `git diff --check`; `spec-dock validate`; report closure rows | pass |
| Epic final PR gate | Epic #224 single PR readiness | owned by Epic plan after G4 finish | not executed in this Issue |
