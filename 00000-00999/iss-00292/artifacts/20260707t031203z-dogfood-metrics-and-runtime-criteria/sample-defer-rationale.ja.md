# Sample defer rationale

## 1. Rationale type

- type: `defer`
- evaluated_scope: `scripts/authoring-pack/` dogfood-only helper workflow
- evaluated_ref: `iss-00292`
- date: `2026-07-07`
- evaluator: main orchestrator
- this_is_not_promotion_decision: `true`

## 2. Summary

- one_sentence_rationale: dogfood evidence is promising, but formal runtime promotion should wait for backend adapter verification and operational metrics.
- primary_blocker_or_gap: backend command adapter readiness is deferred to `iss-00293`; manual fallback success and human edit burden are unmeasured.
- next_reassessment_condition: `iss-00293` final quality gate passes and remaining metrics are measured or explicitly waived.

## 3. Evidence reviewed

| evidence_id | path | scenario | status | notes |
|---|---|---|---|---|
| EV-A | `iss-00288` report | candidate-only pack | pass | candidate validation passed |
| EV-B | `iss-00289` report | selected-profile pack | pass | local authority preserved |
| EV-C | `iss-00290` report | negative probes | pass | 6 / 6 non-adoptable |
| EV-D | `iss-00291` report | workflow docs | pass | docs and fallback notes exist |

## 4. Metric snapshot

| metric_id | measurement_type | signal | sample interpretation |
|---|---|---|---|
| M-A-001 | computed | promote | candidate-only focused tests passed |
| M-B-002 | computed | promote | local authority was preserved |
| M-C-001 | computed | promote | negative probes failed closed |
| M-DOC-001 | computed | promote | workflow docs exist |
| M-A-003 | computed | defer | correction deltas indicate more samples are useful |
| M-RR-001 | partial | defer | aggregate reviewer repair-loop rule is not fixed |
| M-UN-001 | unmeasured | defer | human edit burden is not measured |
| M-UN-002 | partial_unmeasured | defer | fallback docs exist, but outage run was not exercised |
| M-UN-003 | deferred | defer | backend command adapter readiness belongs to `iss-00293` |

## 5. Boundary checks

- canonical_written: `false` for generated / staged evidence.
- assurance_mutated: `false`.
- reviewer_pass_claimed: `false`.
- profile_suggestion_used_for_authority: `false`.
- host_local_path_or_secret_present: no adopted evidence.
- raw_zip_or_raw_transcript_committed: no.
- src_runtime_touched: no.

## 6. Follow-up

- owner: `iss-00293`
- issue_or_ADR: final quality gate / backend adapter verification
- required_tests: authoring-pack manual suite, SpecDock validate, backend adapter fail-closed tests
- required_reviewer_gate: fresh spec / code / QA review before PR
