# S07 Fresh Red Team Review v4

## 1. Verdict

**FAIL — P0: 0 / P1: 1 / P2: 0 / P3: 0**

**P0/P1 remaining: Yes — one P1 remains.**

The connected GitHub repository was inspected first. The named branch `codex/iss-00354-chatgpt-context-contract` resolves exactly to `7538f74924f0052fe0a7e340b641c35ba1e2c716`, with ahead `0` / behind `0`. The attached canonical bundle was used only as supplementary cross-reference evidence. 

---

## 2. Blocking finding

### `RT-354-S07-V4-001` — The pushed report-only correction is still described as uncommitted future work

**Severity:** P1

**Exact location**

`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md`

Affected current-state sections include:

* Evidence Adoption Ledger, `EAL-049`
* Discovered Tests, S07 row
* Test Contract Closure and Closure Coverage, S07 rows
* Implementation Delegation Gate, S07 row
* Delegated Worker Evidence, S07 row
* Milestone / Commit Candidate Gate, S07 row
* Final Quality Gate, S90 row
* Final Commit

### Observed fact

The GitHub commit boundaries are unambiguous:

* `7634899dcbf31fafcba9380906e6918f87f82948` → `64de2139afe36a81031e5bf57f82c55d25167c96` adds only the Blue v3 brief and immutable Red v3 canonical/raw evidence.
* `64de2139afe36a81031e5bf57f82c55d25167c96` → `7538f74924f0052fe0a7e340b641c35ba1e2c716` modifies exactly one file: `report.md`.
* Therefore `7538f749…` is already the pushed report-only correction HEAD.

Despite this, current-state rows still describe the report correction as pending work. Examples include “report-only correction pending,” instructions to “correct report-only wording, commit/push,” and the Final Commit instruction to “commit/push the report-only correction” before Fresh Red v4.  The Final Commit row is especially explicit: it treats the correction contained in the authoritative pushed HEAD as the next mutation rather than completed repository state.

Other rows correctly preserve:

* historical Red v2 source `51ec44361934991c0ba347eed7e5047c719ec122`, `FAIL / P0=0 / P1=3`;
* the committed/pushed v2 three-path correction and three immutable evidence imports at `7634899d…`;
* Red v3’s review of `7634899d…`, `FAIL / P0=0 / P1=1`;
* S07 as open and blocked.

The defect is therefore an internally contradictory current-state ledger, not a missing code, Skill, parity, or architecture correction. Red v3 had required every current row to distinguish completed commit/import work from the still-pending fresh review gate. 

### Why this blocks the gate

`report.md` is the observed-evidence and implementation-handoff ledger. At exact HEAD `7538f749…`, it cannot simultaneously establish that the report-only correction has been pushed and instruct the next worker to commit and push that same correction.

This leaves the handoff unable to determine reliably:

* which repository mutation is complete;
* which exact HEAD this Fresh Red v4 reviewed;
* whether another report mutation is required;
* whether the next action is review or a repeated commit.

That directly blocks trusting the S07 source identity and handoff gate.

### Smallest evidence-only correction required

Modify **only `report.md`** so every current S07 row consistently records:

1. `51ec44361934991c0ba347eed7e5047c719ec122` was the Red v2 reviewed source and returned `FAIL / P0=0 / P1=3`.
2. The three Blue v2 correction paths and three immutable v2 evidence-import paths were committed and pushed before Red v3.
3. Red v3 reviewed `7634899dcbf31fafcba9380906e6918f87f82948` and returned `FAIL / P0=0 / P1=1`.
4. `64de2139afe36a81031e5bf57f82c55d25167c96` is the pushed Blue v3 brief/Red v3 evidence-import boundary.
5. `7538f74924f0052fe0a7e340b641c35ba1e2c716` is the pushed report-only correction reviewed here.
6. This Fresh Red v4 returned `FAIL / P0=0 / P1=1` with finding `RT-354-S07-V4-001`.
7. Only a later fresh Red v5 against the next exact pushed HEAD remains pending.
8. S07 remains open and blocked; S08, Delivery PR, merge, Issue close, and Issue finish remain prohibited.

Do not modify the provider Skill, `.agents` projection, parent Epic documents, cleanup receipt, Blue briefs, immutable Red outputs, runtime, CLI, application, domain, infra, or tests.

---

## 3. Verification matrix

| Check                                  |                          Result | Verification                                                                                                                                                                                                                                 |
| -------------------------------------- | ------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact source HEAD                      |                        **PASS** | Named branch tip is exactly `7538f74924f0052fe0a7e340b641c35ba1e2c716`; ahead `0`, behind `0`.                                                                                                                                               |
| Branch identity                        |                        **PASS** | `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract`; no default-branch substitution.                                                                                                                                          |
| Current correction boundary            |                        **PASS** | `7634899d… → 64de2139…` is v3 brief/Red v3 evidence import; `64de2139… → 7538f749…` changes only `report.md`. No runtime, test, Skill, projection, or parent-document path occurs in the report-only range.                                  |
| Provider/projection parity             |                        **PASS** | Provider Skill and root `.agents` projection have identical Git blob SHA `69b0a87c5fa23e78bbe776f75d61f154b222bf87`.                                                                                                                         |
| Historical scope receipt               |                        **PASS** | `21a2c4c2… → 51ec4436…` is exactly five direct Blue edits plus three immutable evidence imports, eight files total, with no missing or unexpected path.                                                                                      |
| Fresh-install recursive parity receipt | **PASS — receipt completeness** | Receipt includes the complete recursive command, provider preflight/fresh-init/parity exit `0`, distinguishable fresh-installed Skill/docs roots, counts `7/7` and `37/37`, tree hashes `2ec1f6…` and `821ee2…`, and `parity_exclusions=[]`. |
| Report current-state rows              |                        **FAIL** | Multiple current rows still make the already-pushed `7538f749…` report correction a future commit/push action.                                                                                                                               |
| Evidence-import boundary               |                        **PASS** | Blue v2 correction files, immutable Red v2 imports, Blue v3 brief import, immutable Red v3 imports, and the later report-only correction remain distinguishable.                                                                             |
| Epic §6.3 boundary                     |                        **PASS** | Compact form body, provider-owned operation resources, and opaque repeatable `--provided-context-path` remain separated; input walking/materialization is prohibited and output ZIP/JSON validation is retained.                             |
| Exact-branch fail-closed instructions  |                        **PASS** | Formal runs require exact GitHub repository/named-branch/HEAD verification and prohibit `local-context`, default branch, attachment, prompt context, or memory substitution.                                                                 |
| Operation-specific path contract       |                        **PASS** | Create, archive/git-bound Review, and Semantic Revision accept the repeatable path option; apply and Mechanical Revision explicitly do not.                                                                                                  |
| Output/JSON/ZIP contracts              |                        **PASS** | Exactly one authoring ZIP with the canonical three documents plus exactly one onboarding companion, and a separate closed Reviewer JSON, remain intact.                                                                                      |
| S07/downstream status                  |                        **PASS** | No S07 PASS or closure, S08 start, Delivery PR, merge, Issue close, or Issue finish is claimed. S07 remains blocked pending a fresh passing review.                                                                                          |

---

## 4. Gate statement

```text
S07 gate: FAIL
P0 remaining: 0
P1 remaining: 1
S07 closure: prohibited
S08 start: prohibited
Delivery PR: prohibited
merge: prohibited
Issue close / finish: prohibited
```

The recursive parity, fresh-install, validation, and diff-check commands were not independently rerun in this read-only review. Their committed receipts, persistent GitHub blobs, and exact commit ranges were inspected; the temporary fresh-installed directory itself was not available for direct reinspection.
