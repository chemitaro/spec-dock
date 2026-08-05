# S07 Fresh Red Team Review v3 — defect-only gate

## 1. Verdict

**FAIL**

| Severity | Count |
| -------- | ----: |
| P0       |     0 |
| P1       |     1 |
| P2       |     0 |
| P3       |     0 |

**P0/P1 remains: Yes — `RT-354-S07-V3-001`.**

The GitHub connector resolved the named branch and confirmed that its tip is exactly:

```text
chemitaro/spec-dock
codex/iss-00354-chatgpt-context-contract
7634899dcbf31fafcba9380906e6918f87f82948
```

The branch-to-SHA comparison was `identical`, ahead `0`, behind `0`. The current commit is the S07 v2 evidence-introduction commit.

---

## 2. Blocking finding

### `RT-354-S07-V3-001` — the current-state report still describes the committed and pushed v2 correction as uncommitted

**Severity:** P1

**Exact location**

`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md`

Affected sections:

* `Delegated Worker Evidence` — S07 row
* `Milestone / Commit Candidate Gate` — S07 row
* `Final Commit`
* Related S07 test/closure rows that still describe the evidence correction itself, rather than only its fresh review, as pending

**Observed fact**

The GitHub connector comparison from reviewed Red v2 source `51ec44361934991c0ba347eed7e5047c719ec122` to current HEAD `7634899dcbf31fafcba9380906e6918f87f82948` reports two commits and six changed paths:

**Three Blue correction paths**

1. `artifacts/implementation-briefs/s07-blue-repair-v1-20260805.md`
2. `artifacts/20260805t-projection-cleanup-analysis.md`
3. `report.md`

**Three immutable evidence-import paths**

1. `artifacts/implementation-briefs/s07-blue-repair-v2-20260805.md`
2. `reviews/red-team-review-s07-v2.md`
3. `reviews/red-team-review-s07-v2-raw.md`

No runtime or test path is present in that range.

Nevertheless, the current `Final Commit` row states that the “v2 correction is currently uncommitted” and directs the next operator to “commit/push the three-file correction” and “import v2 evidence bytes separately.” The S07 worker and milestone rows similarly describe commit/push of the correction as a future action.

Other portions of the same report correctly record that Red v2 reviewed exact HEAD `51ec4436…`, returned `FAIL / P0=0 / P1=3`, and that S07 remains blocked pending a fresh v3 review.

**Why this blocks the gate**

`report.md` is the Observed Evidence Ledger and implementation handoff record. Its current-state rows must distinguish:

* the historical Red v2 source HEAD;
* the already-committed three-file evidence correction;
* the separately imported immutable evidence;
* the still-pending fresh review gate.

The present wording instead represents repository state already present at the authoritative HEAD as future work. This makes the report unreliable for determining the current correction boundary and next review identity, and could cause a subsequent worker to repeat the correction or construct the next review handoff from the wrong baseline.

This is the same material exact-state defect class identified by Red v2, now shifted from the v1 repair to the v2 correction. It blocks trusting the documented S07 handoff.

**Smallest evidence-only correction**

Modify **only `report.md`** so every current S07 row consistently states:

1. `51ec44361934991c0ba347eed7e5047c719ec122` is the historical Red v2 reviewed source and Red v2 returned `FAIL / P0=0 / P1=3`.
2. The bounded three-file correction and the three immutable v2 evidence imports were subsequently committed and pushed before this v3 review.
3. This v3 review returned `FAIL / P0=0 / P1=1`.
4. S07 remains open and requires a later fresh Red review against the new exact pushed HEAD.
5. S08, Delivery PR, merge, Issue close, Issue finish, and any S07 PASS or closure claim remain prohibited.

Do not modify the Skill, its projection, parent Epic documents, cleanup receipt, Blue briefs, prior Red outputs, runtime, CLI, application, domain, infra, or tests. The resulting repair commit need not self-reference its own SHA; the later review prompt and GitHub connector should supply that exact identity externally.

---

## 3. Verification matrix

| Check                                    | Result                          | Verification                                                                                                                                                                                                                                                                      |
| ---------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact source HEAD                        | **PASS**                        | Named branch tip is exactly `7634899dcbf31fafcba9380906e6918f87f82948`; no default-branch substitution.                                                                                                                                                                           |
| Branch identity                          | **PASS**                        | Connector comparison returned `identical`, ahead `0`, behind `0`.                                                                                                                                                                                                                 |
| Current v2 correction scope              | **PASS**                        | `51ec4436… → 7634899…` contains three correction paths and three separately added evidence-import paths; no runtime/test files.                                                                                                                                                   |
| Historical repair scope                  | **PASS**                        | `21a2c4c2… → 51ec4436…` is exactly five direct Blue paths plus three immutable evidence-import paths, eight total, with no missing or unexpected paths. The committed cleanup receipt contains the exact audit command and result.                                                |
| Provider/projection Skill parity         | **PASS**                        | Provider Skill and root `.agents` projection have the same Git blob SHA, `69b0a87c5fa23e78bbe776f75d61f154b222bf87`, and therefore identical bytes.                                                                                                                               |
| Fresh-install recursive parity receipt   | **PASS — receipt completeness** | The committed evidence records the complete command, provider preflight exit `0`, fresh-init exit `0`, recursive parity exit `0`, distinguishable fresh-installed Skill/docs subroots, counts `7/7` and `37/37`, tree hashes `2ec1f6…` and `821ee2…`, and `parity_exclusions=[]`. |
| Report current-state rows                | **FAIL**                        | The report still calls the already-committed v2 correction “currently uncommitted” and makes its commit/push/import future work. This is `RT-354-S07-V3-001`.                                                                                                                     |
| Red v1 evidence immutability             | **PASS**                        | Canonical/raw v1 review files share Git blob SHA `58ebacdd03c522a385dda9589718366d91602306` and retain exact HEAD `21a2c4c2…`, `FAIL / P0=0 / P1=4`.                                                                                                                              |
| Red v2 evidence immutability             | **PASS**                        | Canonical/raw v2 review files share Git blob SHA `ce808edde47143d10b40a2ff5be4cb9eda9bc6f6` and retain exact HEAD `51ec4436…`, `FAIL / P0=0 / P1=3`.                                                                                                                              |
| Evidence-import boundary                 | **PASS**                        | Blue v2 explicitly limits its correction to three files and treats the Blue v2 brief plus Red v2 canonical/raw files as separate immutable imports.                                                                                                                               |
| Epic §6.3 input boundary                 | **PASS**                        | Compact body, provider-owned operation resources, and opaque repeatable `--provided-context-path` are separated; input walk/open/snapshot/hash/archive/filter/rename/copy/manifest creation is prohibited, while output ZIP/JSON validation remains intact.                       |
| Exact-branch fail-closed instructions    | **PASS**                        | The official Skill unconditionally requires exact GitHub repository/named-branch/HEAD verification and forbids `local-context`, default branch, attachments, prompt context, or memory as substitutes.                                                                            |
| Operation-specific context-path contract | **PASS**                        | Create, archive/git-bound Review, and Semantic Revision document the repeatable option; apply and Mechanical Revision explicitly do not consume it.                                                                                                                               |
| Output/JSON/ZIP contract                 | **PASS**                        | One authoring ZIP containing the canonical three documents plus exactly one onboarding companion, and a separate closed Reviewer JSON, remain the formal outputs.                                                                                                                 |
| PASS/closure/S08/Delivery PR claim       | **PASS**                        | The current evidence still records S07 as failed/pending and does not claim S07 closure, S08 start, or Delivery PR authorization. The defect is the stale commit state, not premature promotion.                                                                                  |

## 4. Assumptions and unverified claims

The GitHub named branch and exact HEAD were inspected through the connected GitHub repository and treated as repository authority. The attached canonical bundle was used only as supplementary cross-reference evidence. 

This read-only review did not independently rerun `fresh init`, the recursive parity script, `spec-dock validate`, or `git diff --check`. It verified the completeness and internal consistency of their committed receipts, plus the persistent GitHub files and commit ranges. The temporary fresh-installed tree itself is no longer available for direct byte reinspection.

## 5. Gate statement

**One P1 remains: `RT-354-S07-V3-001`.**

Therefore:

```text
S07 gate: FAIL
S07 closure: prohibited
S08 start: prohibited
Delivery PR: prohibited
P0/P1 remaining: yes
```
