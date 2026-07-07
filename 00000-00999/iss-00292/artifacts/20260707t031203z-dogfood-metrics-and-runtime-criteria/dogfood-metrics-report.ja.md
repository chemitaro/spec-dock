# Dogfood metrics report

## 位置づけ

この report は `iss-00292` の Issue-local evidence です。ChatGPT ZIP 仕様作成パックの dogfood 結果から、runtime 昇格、保留、却下を後続判断するための材料を整理します。

この文書は runtime promotion を承認しません。`scripts/authoring-pack/` は dogfood-only helper であり、SpecDock runtime command ではありません。

## Source evidence

| source | scope | evidence |
|---|---|---|
| `iss-00288` | Scenario A: Epic-to-Issue candidate-only pack | candidate validator evidence and `188 passed` full suite |
| `iss-00289` | Scenario B: existing Issue selected-profile pack | review / selected skeleton validation / dry-run pass evidence |
| `iss-00290` | Scenario C: mismatch / stale / unsafe claim negative probes | 6 / 6 adoption-ineligible probes and `201 passed` full suite |
| `iss-00291` | workflow docs | README, prompt contract, EAL examples, manual fallback notes |

## Metric summary

| metric_id | scenario | metric | measurement_type | observed_value | interpretation | decision signal |
|---|---|---|---|---|---|---|
| M-A-001 | A | candidate-only focused tests | computed | `19 / 19 pass` | candidate-only validator has focused positive / negative coverage | promote signal for candidate-only validation |
| M-A-002 | A | full authoring-pack suite at `iss-00288` | computed | `188 / 188 pass` | issue-local full suite passed at Scenario A checkpoint | promote signal, later superseded by larger suite |
| M-A-003 | A | candidate helper correction deltas | computed | `2` dispositions | candidate helper required reviewer-driven corrections | defer signal for more dogfood samples before runtime promotion |
| M-B-001 | B | selected-profile review / validation / dry-run | computed | `pass / pass / pass` | selected-profile dogfood path worked end-to-end as staged evidence | promote signal for selected skeleton flow |
| M-B-002 | B | local authority preserved | computed | `canonical_written=false`, `assurance_mutated=false`, `reviewer_pass_claimed=false` | generated / staged output did not claim local authority | strong promote signal for authority boundary |
| M-B-003 | B | profile suggestion ignored for authority | computed | ChatGPT `strict` suggestion ignored; local target `standard` | ChatGPT recommendation stayed advisory-only | strong promote signal for profile boundary |
| M-B-004 | B | staged section eligibility | computed | `3 / 3` required sections eligible; `1` optional missing | required sections were usable; optional missing section was reported | promote signal with completeness caveat |
| M-B-005 | B | dry-run canonical write prevention | computed | `3` staged sections, all `canonical_written=false` | staged adoption did not directly overwrite canonical docs | promote signal for no-overwrite invariant |
| M-C-001 | C | negative probe block success | computed | `6 / 6 adoption_eligible=false` | stale / mismatch / unsafe claim probes all remained non-adoptable | strong promote signal for fail-closed behavior |
| M-C-002 | C | negative status distribution | computed | `stale=5`, `rejected=1` | failure classes remain distinguishable | promote signal for status taxonomy |
| M-C-003 | C | stale staging prevention | computed | returncode `3`, `status=stale`, `staged_artifact_count=0` | stale review could not stage artifacts | strong promote signal for stale gate |
| M-C-004 | C | final authoring-pack manual suite | computed | `201 / 201 pass` | latest full suite passed after negative probe work | promote signal for current helper suite |
| M-DOC-001 | docs | workflow docs deliverables | computed | README + 4 Issue-local docs + summary | dogfood workflow, prompt contract, EAL examples, fallback notes exist | promote signal for documentation readiness |
| M-DOC-002 | docs | leakage / unsafe-claim inspection | computed | pass | unsafe words appear as forbidden examples, not authority claims | promote signal for documentation boundary |
| M-RR-001 | cross | reviewer repair loop count | partial | issue-local findings exist; aggregate rule not fixed | findings and dispositions are available, but loop aggregation is undefined | defer signal until aggregate rule exists |
| M-UN-001 | cross | human edit burden | unmeasured | not measured | edit time / edit volume are not captured in durable evidence | defer signal for runtime promotion |
| M-UN-002 | cross | manual fallback success rate | partial / unmeasured | fallback docs exist; outage run not exercised | fallback is documented but not proven under outage | defer signal before formal runtime promotion |
| M-UN-003 | cross | backend command adapter readiness | deferred | owned by `iss-00293` | local wrapper dependency removal is a final-gate requirement | defer signal until `iss-00293` passes |

## Interpretation

The dogfood helper evidence is strong for evidence-only boundaries, local profile authority, no canonical overwrite, stale / mismatch / unsafe-claim fail-closed behavior, and documentation readiness.

The evidence is not sufficient to approve runtime promotion because human edit burden, outage fallback success, aggregate repair-loop semantics, and backend command adapter readiness remain incomplete or deferred.

## Recommended decision material

- `promote`: only after additional operational evidence and `iss-00293` backend adapter / final gate pass.
- `defer`: current recommended stance for formal runtime promotion.
- `reject`: not supported by current evidence; no safety-boundary violation requiring rejection was observed.
