# 補助アーティファクト: 決定履歴・矛盾・移行台帳

> **non-canonical / Red Team レビュー対象外**  
> `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` のsource-grounded synthesis。既存17件のclarification/interview/research履歴とprior Candidate decisionsを
> 失効させず、Oracle 0.17増分を追記する。正式なEvidence Adoption Ledgerではない。

## 1. GitHub verification

| Field | Result |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Requested branch | `codex/iss-00354-chatgpt-context-contract` |
| Requested source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Branch existence | confirmed via GitHub Connector |
| Branch vs HEAD | identical / ahead 0 / behind 0 |
| Default branch fallback | not used |
| Mutation | none |

## 2. Preserved historical evidence inventory

source HEADのexisting ledgerが確認した17件を、今回も歴史的sourceとして保持する。

1. `20260803t005640z-research-current-chatgpt-context-attachment-research.md`
2. `20260803t005840z-interview-chatgpt-thread-continuity-scope-interview.md`
3. `20260803t010552z-chatgpt-output-chatgpt-clarification-analysis.md`
4. `20260803t011239z-interview-chatgpt-thread-failure-recovery-interview.md`
5. `20260803t011552z-chatgpt-output-chatgpt-continuity-recovery-analysis.md`
6. `20260803t023549z-interview-chatgpt-context-attachment-matrix-interview.md`
7. `20260803t023819z-chatgpt-output-chatgpt-context-attachment-matrix-analysis.md`
8. `20260803t024349z-interview-chatgpt-output-template-contract-interview.md`
9. `20260803t024658z-chatgpt-output-chatgpt-output-template-contract-analysis.md`
10. `20260803t025103z-interview-chatgpt-context-contract-scope-interview.md`
11. `20260803t025321z-chatgpt-output-chatgpt-context-contract-scope-analysis.md`
12. `20260803t030211z-disc-chatgpt-operation-pack-flexible-input-discussion.md`
13. `20260803t030323z-interview-chatgpt-attachment-directory-safety-interview.md`
14. `20260803t030543z-chatgpt-output-chatgpt-attachment-directory-safety-analysis.md`
15. `20260803t034911z-interview-chatgpt-attachment-transport-entry-boundary-interview.md`
16. `20260803t035221z-chatgpt-output-chatgpt-attachment-transport-entry-boundary-analysis.md`
17. `rules.md`

今回のCandidateはこれらのraw contentを再生成・削除・renameせず、existing ledgerの採否を前提にする。

## 3. Preserved decisions D-001–D-010

| ID | Decision | Status in this Candidate |
|---|---|---|
| D-001 | minimal body | retained |
| D-002 | detailed instructions in attachments | retained |
| D-003 | operation-specific prompt + attachment directory | retained |
| D-004 | Option C direct opaque path transport | retained |
| D-005 | no per-entry exclusion/conversion/backend retry | retained; D-014でnarrow clarification |
| D-006 | typed ZIP / closed JSON output | retained |
| D-007 | Blue continuity / fresh Red | retained |
| D-008 | exact-lineage new Blue / ambiguous Human block | retained |
| D-009 | direct PATH Oracle; no personal wrapper dependency | retained |
| D-010 | ChatGPT non-authority / evidence-only | retained |

## 4. New Oracle 0.17 decisions

### D-011 Exact versioned profile

`0.17.0`をexact compatibility profileとしてcharacterizeする。single constant replacementやsemver wildcardを採用しない。

### D-012 Oracle-native config remains allowed

accepted #334 boundaryを維持し、Oracle user/project configを隔離しない。required formal valuesだけexplicit argvにする。

### D-013 Logical model / observed label separation

logical `Pro` requestとUI labelを分離する。external smokeの`GPT-5.6 Sol`をdirect evidenceなしにhardcodeしない。

### D-014 One bounded Oracle-native transport recovery

D-005の「retry禁止」は、failing entry exclusion、input mutation、backend/model/branch fallback、unbounded retryを禁止した判断として維持する。
今回、classified direct attachment failureかつ`promptSubmitted=false`の場合だけ、same original pathsをOracle-native inline modeで
一度new executionへ渡すnarrow amendmentを追加する。reconstruction mismatchには適用しない。

### D-015 Submission boundary

pre-submit model/attachment failureはoverall budget内のnew execution、reconstruction mismatchはblock、post-submit failureはsame-sessionのみ。

### D-016 Versioned artifact capture

response completionとdownload/snapshotを分離し、0.17 session schemaをdedicated readerで検証する。invalid outputを再生成しない。

### D-017 External evidence provenance

`oracle-browser-recovery-report.md`はexternal local observationであり、GitHub sourceまたはSpecDock production executionと表現しない。
raw personal pathはCandidate本文へ複製しない。

### D-018 Provisional scope

ADRはIssue/Initiative-local。other operations / global architectureへの展開は別triageとする。

## 5. Candidate v1 Red Review repair ledger

| Repair ID | Review finding | v2 disposition | Scope boundary |
|---|---|---|---|
| R-001 | stage-blind hardcoded harvest/profile command ownership gap | corrected in requirement §3.1/REQ-021/027–029, design §3/6/10–13, plan S09–S12, ADR Decisions 1/4/5 | no architecture replacement; current behavior characterized then moved into version profile |
| R-002 | non-authoritative public reason mapping | corrected with one closed mapping in REQ-030, design §15, plan S10/S12/§18, ADR Decision 6 | only reason contract and tests; no new backend or lifecycle |

Prior Candidate `iss-00354-oracle-017-compatibility-candidate-20260804t033922z.zip` and SHA `8f979a5609b5d4dfa899871d50d51a659e273a7191b97e36c4d8de253348d13c` remain immutable. The attached review copy is
`reviews/red-team-review-v1.md`; only its two P1 findings are selected for semantic revision. No P2/P3 or unrequested redesign is introduced.

### D-019 Profile-owned recovery command boundary

Current stage-blind/hardcoded 0.16.1 recovery is a migration baseline, not target behavior. Exact-version profile owns declared inline capability,
harvest builder, and capture builder. False/unknown submission invokes neither builder.

### D-020 Closed public mapping

Five stage-specific reasons are added; existing unavailability/capability/session/artifact reasons are retained. Many-to-one is permitted only inside
capability/profile、runtime unavailable、artifact validation families and forbidden across model/attachment/reconstruction/generation/download stages.

## 6. Facts / hypotheses / unverified matrix

| Claim | Classification | Consequence |
|---|---|---|
| current adapter exact-pins 0.16.1 | GitHub confirmed | profile extraction required |
| current adapter explicit Pro/select and one prompt | GitHub confirmed | regression baseline |
| current reader rejects other versions | GitHub confirmed | no constant-only migration |
| external representative prompt mismatch across modes | external observed | stage class / no auto retry |
| short smoke observed GPT-5.6 Sol verified | external observed | mapping hypothesis only |
| `Available: Got it.` then retry success | external observed | possible transient model class; root cause unknown |
| browser state/start order caused failure | hypothesis | smoke dimension, not design fact |
| direct PATH Oracle reproduces wrapper behavior | unverified | S09/S11 blocking test |
| 0.17 metadata has `promptSubmitted` exact field | unverified | decoder must characterize equivalent evidence |
| inline transport is safe/available in direct Oracle | unverified | disabled until profile evidence |

## 7. Current implementation conflict / delta

| Current implementation | Existing #354 target | Oracle 0.17 delta |
|---|---|---|
| exact 0.16.1 constant | preserve fail-closed semantics | profile registry + 0.17 decoder |
| generated prompt pack | direct path / no materialization | direct primary + optional Oracle-native inline |
| `Pro` / `select` fixed argv | keep logical explicit request | verified observed label / no hardcoded UI name |
| stage-blind hardcoded harvest on nonzero/nonterminal | characterize then remove from generic adapter | profile builder + true-submission gate; false/unknown calls 0 |
| generic nonzero -> recovery | refine | pre-submit class must not be harvested blindly |
| artifact reader assumes 0.16.1 schema | strict output retained | version-dispatched reader |
| public reasons mostly artifact/session generic | retain existing reasons | add five stage-specific reasons and closed many-to-one rules |

## 8. Rejected / not adopted

| Proposal | Disposition | Reason |
|---|---|---|
| personal wrapper integration | rejected | D-009 / product boundary |
| automatic API fallback | rejected | authority/provenance drift |
| semver range acceptance | rejected | unknown browser/schema behavior |
| prompt normalization / shortening | rejected | changes exact input |
| model `current` fallback | rejected | silent model drift |
| hardcode `GPT-5.6 Sol` globally | rejected | one external observation only |
| no-attachment production fallback | rejected | required evidence loss |
| per-entry exclusion / automatic ZIP | rejected | Option C violation |
| post-submit new execution | rejected | duplicate conversation/output |
| unlimited/configurable retry | rejected | non-deterministic and duplicate risk |
| config isolation | rejected | accepted Oracle-native config boundary |
| output validator relaxation | rejected | input compatibility does not weaken output safety |

## 9. Migration ledger

| Step | From | To | Rollback boundary |
|---|---|---|---|
| M-01 | single 0.16.1 constant | behavior-preserving 0.16.1 profile | revert extraction |
| M-02 | unknown 0.17 blocked | characterized 0.17 profile | remove profile / block |
| M-03 | generic execution outcome | stage evidence + pure recovery decision | disable new recovery actions |
| M-04 | generated pack | direct paths | commit-level revert; no dual mode |
| M-05 | direct only | direct + classified one-shot inline | disable inline policy only |
| M-06 | single-version reader | version-dispatched readers | remove 0.17 reader/profile |
| M-07 | external observation only | direct browser smoke evidence | no promotion if smoke fails |

## 10. Adoption caution

このCandidate自体はEAL adoptionではない。Humanが採用する場合、reportで少なくとも次を別entryにする。

- prior Option A/C Candidate adoption。
- external wrapper recovery report: source role `external_local_observation`。
- direct PATH Oracle 0.17 capability receipt: source role `command` / `integration evidence`。
- browser smoke result。
- model mapping acceptance / rejection。
- ADR adoption / withdrawal。
