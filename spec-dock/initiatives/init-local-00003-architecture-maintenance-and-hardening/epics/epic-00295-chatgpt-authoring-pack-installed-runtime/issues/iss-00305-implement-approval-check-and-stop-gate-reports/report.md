---
種別: 実装報告書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00305 Approval Stop Gate Reports — 実装報告

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | Issue-local draft requirement | `requirement.md` | approval check scope, non-scope, acceptance criteria を採用し、authority boundary を補強した。 | `artifacts/20260707t171312z-draft-requirement-implement-approval-check-and-stop-gate-reports-draft-requirement.md` | no_action |
| EAL-002 | adopted | Issue-local draft design | `design.md` | target paths, schema, failure modes を採用し、既存 runtime structure に合わせて再設計した。 | `artifacts/20260707t171313z-draft-design-implement-approval-check-and-stop-gate-reports-draft-design.md` | no_action |
| EAL-003 | adopted | Issue-local draft plan | `plan.md` | step sequence, verification, relay policy を採用し、closure / delegation / test contract を追加した。 | `artifacts/20260707t171313z-01-draft-plan-implement-approval-check-and-stop-gate-reports-draft-plan.md` | no_action |
| EAL-004 | adopted | repo inspection | `design.md`, `plan.md` | `authoring approval check` が deferred command であること、既存 validators / renderers の構造を確認した。 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`; `tests/cli_runtime/test_authoring.py` | no_action |
| EAL-005 | partially_adopted | ChatGPT Use GPT-5.5 Pro Extended analysis | `requirement.md`, `design.md`, `plan.md` | approval schema、status model、CLI shape、failure modes、test strategy を採用した。`strict` 推奨は `.assurance.json` authority ではなく manual escalation recommendation として扱う。 | `artifacts/20260708t061422z-chatgpt-approval-stop-gate-planning-analysis.md` | no_action |

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | draft requirement, parent Epic requirement/design/plan, issue-planning guidance | none | draft adopted and rewritten into canonical requirement | pass | no | promote |
| design | draft design, current authoring runtime files, candidate validator patterns | none | draft adopted and rewritten into canonical design | pass | no | promote |
| plan | draft plan, issue-plan obligations, relay policy | none | draft adopted and expanded into executable plan | pass | no | promote |

## Spec Interpretation / Decision Ledger

| ID | decision | rationale | source evidence | impact |
|---|---|---|---|---|
| D-001 | Approval check validates evidence only and never performs node creation. | Parent Epic keeps ChatGPT output and runtime validation in evidence-only lane. | `requirement.md#5.2-out-of-scope`; `design.md#2-設計意図` | output must keep mutation boundary false |
| D-002 | Candidate freshness separates pack tree digest, candidate evidence file digest, and source manifest hash. | A valid approval for an old source snapshot must not pass for a regenerated candidate pack, and evidence file identity must not be confused with pack tree identity. | `requirement.md#rb-003-candidate-digest-stale`; `requirement.md#rb-004-source-hash-stale`; `design.md#11-cli-contract` | CLI/design/plan include `--expected-candidate-pack-digest`, `--expected-candidate-evidence-digest`, and `--expected-source-manifest-hash` |
| D-003 | Unsynced operation is represented by explicit `--evidence-mode local-context`, not `--force`. | User rejected casual bypass while allowing explicit local evidence mode. | `requirement.md#3-親スコープから継承する制約`; `design.md#11-cli-contract` | no `--force`; mode name makes responsibility visible |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Epic planning / ChatGPT authoring pack | iss-00305 | `artifacts/20260707t171312z-draft-requirement-implement-approval-check-and-stop-gate-reports-draft-requirement.md`; `artifacts/20260707t171313z-draft-design-implement-approval-check-and-stop-gate-reports-draft-design.md`; `artifacts/20260707t171313z-01-draft-plan-implement-approval-check-and-stop-gate-reports-draft-plan.md`; `artifacts/20260708t061422z-chatgpt-approval-stop-gate-planning-analysis.md` | parent Epic docs, authoring pack analysis, current runtime inspection | `requirement.md`, `design.md`, `plan.md`, `report.md` | partially_integrated | `requirement.md`, `design.md`, `plan.md`, `report.md` | `assurance verify` and `git diff --check` passed after canonical docs finalization | main orchestrator rewrote selected claims into canonical docs and report ledgers | old branch trace, raw authority claims, any node-creation-ready implication, and ChatGPT `strict` recommendation as authoritative profile | none | pass | promote |

## Grade Specialist Evidence Gate

| grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| `standard` | manual fallback with fresh `spec-reviewer` required | used | manual-authored canonical docs from EAL-001 through EAL-005; Delegated Draft Evidence row; `assurance verify` passed after docs finalization | pass | ready |

## Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | spec authoring review | spec-reviewer | fresh | passed | no | promote | re-review `019f4077-edeb-7b52-b8ae-9ac946ad856a` returned `review_status: pass`; prior P1/P2 findings resolved |
| implementation | code review | code-reviewer | fresh | passed | no | promote | final review `019f4085-15a8-7cd3-b43f-8e1ca232ae95` returned no findings and `review_status: pass` |
| implementation | QA review | qa-reviewer | fresh | passed | no | promote | final review `019f4085-381a-7073-aa76-619c087ceeb6` returned no findings and `review_status: pass` |

## Closure Coverage

| closure id | step | evidence | observed result | notes |
|---|---|---|---|---|
| CLOS-001 | S01/S04 | help contract fixture | passed | approval check help exposes implemented contract and omits `--force` |
| CLOS-002 | S02/S03/S04 | valid epic-issue and initiative-epic approval fixtures | passed | valid approval fixtures pass with evidence-only authority |
| CLOS-003 | S02 | missing approval fixture | passed | missing approval returns `status=blocked` |
| CLOS-004 | S02 | candidate digest mismatch fixture | passed | pack digest mismatch returns `status=stale` |
| CLOS-005 | S03 | requested/effective scope mismatch fixtures | passed | scope mismatch returns `status=blocked` |
| CLOS-006 | S02 | invalid self-approval fixture | passed | self approval returns `status=rejected` |
| CLOS-007 | S02/S04 | forbidden authority claim and sensitive statement fixtures | passed | forbidden authority claim and secret-like payload return `status=rejected` |
| CLOS-008 | S03 | unsafe and safe report path fixtures | passed | safe report writes JSON; canonical docs, `.assurance.json`, and symlink report paths are rejected |
| CLOS-009 | S03/S04/S05 | mutation boundary false and candidate-validation-alone fixture | passed | output boundary stays false and protected `spec-dock/` tree snapshot is unchanged |
| CLOS-010 | S05/S99 | no per-Issue PR relay | passed | no PR created for `iss-00305`; relay continues to next Issue |
| CLOS-011 | S02 | source manifest hash mismatch fixture | passed | source manifest hash mismatch returns `status=stale` |
| CLOS-012 | S02 | candidate evidence file digest mismatch fixture | passed | candidate evidence file digest mismatch returns `status=stale` |
| CLOS-013 | S03/S04 | JSON/text candidate-source comparisons and authority boundary output | passed | JSON/text output includes comparisons and false authority boundary fields |

## Delegated Worker Evidence

| step | delegated role | summary | changed files | verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S02-S05 | dev-coder | `authoring approval check` を deferred から evidence-only approval validator へ実装し、code-reviewer / qa-reviewer P1/P2 指摘を repair した。 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/approval_check_renderer.py`; dogfooding mirror under `spec-dock/scripts/spec_dock_runtime/`; `tests/cli_runtime/test_authoring.py` | `uv run pytest tests/cli_runtime/test_authoring.py -k "approval_check" -q`: 42 passed; `uv run pytest tests/cli_runtime/test_authoring.py -q`: 312 passed, 1 skipped; mirror inventory test: 1 passed; `validate`: ok; `assurance verify`: ok; `git diff --check`: pass | code-reviewer pass; qa-reviewer pass | none observed in focused runtime tests or reviewer gates after repair | integrated |

## Test Contract Closure

| test id | step | required | verification command | observed result | notes |
|---|---|---|---|---|---|
| tc-s00-001 | S00 | yes | `assurance classify`, `assurance compose`, `assurance verify` | classify/compose/verify passed after canonical docs finalization | planning in progress |
| tc-s02-001 | S02 | yes | approval pass/missing/stale/scope/self-approval tests | passed | `uv run pytest tests/cli_runtime/test_authoring.py -k "approval_check" -q` passed |
| tc-s04-001 | S04 | yes | help/json/text/auto-create tests | passed | approval help/output/boundary tests passed as part of focused and full authoring suite |
| tc-s05-001 | S05 | yes | focused authoring tests | passed | `uv run pytest tests/cli_runtime/test_authoring.py -q` passed: 312 passed, 1 skipped |
| tc-s99-001 | S99 | yes | commit/push/finish evidence | pending | final closeout |

## No-PR Relay Policy

| target | policy | evidence | state |
|---|---|---|---|
| iss-00305 | Do not create a per-Issue PR; defer PR delivery to `iss-00307`. | parent Epic plan and this plan final exit contract; no PR created during implementation | maintained |

## Final Quality Gate

| gate | status | evidence |
|---|---|---|
| spec-dock validate | passed | `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=202` |
| assurance verify | passed | `./spec-dock/scripts/spec-dock assurance verify`: ok |
| focused tests | passed | `uv run pytest tests/cli_runtime/test_authoring.py -k "approval_check" -q`: 42 passed, 271 deselected |
| authoring regression tests | passed | `uv run pytest tests/cli_runtime/test_authoring.py -q`: 312 passed, 1 skipped |
| dogfooding runtime mirror | passed | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets -q`: 1 passed |
| git diff --check | passed | no whitespace errors |
| code-reviewer | passed | final review `019f4085-15a8-7cd3-b43f-8e1ca232ae95`: no findings, `review_status=pass` |
| qa-reviewer | passed | final review `019f4085-381a-7073-aa76-619c087ceeb6`: no findings, `review_status=pass` |
| no per-Issue PR | pending | final closeout |

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- S01 Red: before implementation, `authoring approval check --help` exposed only skeletal deferred help and did not satisfy the approved CLI contract.
- S02-S04 Green: `authoring approval check` now exposes the implemented help contract including `--candidate-evidence` and `--expected-candidate-evidence-digest`; focused approval tests passed with 42 passed / 271 deselected after repair.
- S05 Verification: full `tests/cli_runtime/test_authoring.py` passed with 312 passed / 1 skipped; dogfooding runtime mirror test passed with 1 passed; `validate`, `assurance verify`, and `git diff --check` passed.
- CLOS-010 relay: no per-Issue PR was created; PR delivery remains deferred to final Issue `iss-00307`.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
