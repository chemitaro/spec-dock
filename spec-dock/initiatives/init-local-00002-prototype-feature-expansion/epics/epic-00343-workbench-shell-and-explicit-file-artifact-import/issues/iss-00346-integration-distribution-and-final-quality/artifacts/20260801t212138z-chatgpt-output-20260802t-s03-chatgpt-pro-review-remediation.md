### Review scope and head binding

GitHub connector inspection succeeded for `chemitaro/spec-dock`. The branch `iss-00346-integration-distribution-and-final-quality` exists, the default-branch fallback was not used, and the pushed branch tip was verified as exactly `f1b42b6fc50d49317823aa64cf62c93a06e838ba`. The head commit is the S03 remediation-evidence transcription.

The executable remediation is commit `e02b953a43b303ea99e0fa200f9153f748093825`. From that commit to the reviewed head there is one report/artifact-only successor; no provider/runtime or test/probe implementation changed after `e02b953a`. The executable remediation remains confined to:

* `tests/integration/test_epic_00343_distribution.py`
* `tests/integration/iss346_platform_probe.py`

No production provider/runtime file was changed.

Review scope was limited to S03 §10.0–§10.6 and the five prior P1 remediation areas: portable cross-filesystem cleanup, enforced platform-safety predicates, privacy sensitivity/provenance scanning, hermetic-suite receipts, and content-free host receipts. The current reviewer contract makes any unresolved P0/P1 a failing workflow gate.  

### Findings (P0-P3 or None)

1. **[P1] Observe cleanup and fallback calls instead of inferring their absence**

   In the Linux capability-insufficient probe, `pathname_cleanup_absent` is assigned from the final absence of a visible stage. A regression could create a named stage, invoke pathname cleanup, remove the entry, and still produce `pathname_cleanup_absent=true`. Similarly, the macOS probe defines `copy_or_rename_fallback_absent` from the fact that `_publish_no_replace` was called for the formal destination; it does not observe whether that method used `fclonefileat` exclusively or fell back internally to copying or renaming. These proxies can therefore emit an exit-zero pass for precisely the named-cleanup or fallback regressions that S03 must reject. The plan requires zero pathname-cleanup calls and absence of copy/rename fallback, not merely an empty final directory or invocation of a wrapper method. 

2. **[P1] Record immutable execution identity in every platform receipt**

   The report’s Linux rows say “same pinned Linux image” but do not record the resolved container image digest. The macOS rows do not explicitly record `not_applicable` for that field. S03’s receipt schema requires, for every host lane, either the resolved image digest or `not_applicable`; a descriptive “same image” reference cannot independently bind or reproduce the execution environment. The receipts are otherwise substantially improved and no longer expose the earlier host paths or numeric user identity, but the prior traceability P1 is not fully remediated.   

No P0, P2, or P3 finding was identified within the bounded review scope.

### S03 closure verdict with review_status, counts, production-repair decision, and whether S04 may start

* `review_status`: **fail**
* Unresolved findings: **P0: 0, P1: 2, P2: 0, P3: 0**
* `production_repair_justified`: **false**
* Production/provider repair decision: **none**
* S03 closed: **no**
* S04 may start: **no**

The portable cross-filesystem allocation and cleanup defect is remediated: both temporary roots are allocated inside the protected region, unavailable roots are handled without leaking the destination workspace, and both allocations are cleaned in `finally`. 

The privacy remediation now has controlled negatives for all forbidden-value classes, covers text output, parsed JSON, and bounded public/tracked files, and preserves the `.agent` snapshot. The report also supplies the previously missing focused publisher and CLI-runtime command receipts.

However, the two unresolved P1s mean the safety-probe evidence can still overstate what was observed and the Linux execution environment is not immutably bound. Under the governing gate semantics, S03 cannot close and S04 remains blocked.

### Required follow-ups

1. Instrument the probes to record actual safety-relevant calls or syscall-level events. For the Linux insufficient lane, explicitly observe named-stage creation, visible capability probes, and `unlink` or equivalent pathname cleanup, and require each count to be zero. For macOS, observe the clone primitive and any copy/rename fallback entry points independently; do not derive fallback absence from `_publish_no_replace` invocation.

2. Update each Linux receipt with the exact resolved immutable image digest used for that run. Record `container_image_digest=not_applicable` for native macOS host rows. Preserve the existing prohibition on host-local paths, UID/username, device numbers, payload content, and user-file digest/count.

3. Rerun the affected probe lanes against the candidate wheel, update only the bounded S03 report evidence, commit and push the successor, verify branch-tip equality, and obtain a fresh exact-head review. Provider/runtime production code should remain unchanged unless the corrected probes expose an actual runtime defect.

### Uncertainty and non-findings

This was a read-only connector-backed review. I did not independently execute pytest, Docker, or the macOS host probes; the recorded command outcomes and host results remain observed-ledger claims rather than independently reproduced executions.

No production/runtime defect was established. The current provider implementation uses Linux descriptor linking and macOS `fclonefileat`, and the reviewed S03 changes do not alter that implementation.

No bounded-path violation was found. The four-target import, portable cross-filesystem cleanup, controlled privacy negatives, public/provenance scanning, and focused-suite receipt additions were not found to have an unresolved P0/P1 defect. No conclusion was drawn about S04 behavior, Issue 345 correctness, or issue-wide final-quality readiness.
