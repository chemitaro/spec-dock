### Review scope and head binding

GitHub connector inspection succeeded for `chemitaro/spec-dock`. The current branch `iss-00346-integration-distribution-and-final-quality` exists, was inspected before `main`, and the default-branch fallback was not used. Comparing the branch tip with `3418c502eedde2c65ae526fbf7f0db88fdc82fbe` returned `identical` with `ahead_by=0` and `behind_by=0`; the reviewed pushed head is therefore exactly the requested SHA. The head commit is a report/evidence successor rather than a provider-runtime repair.

The review was limited to S03 §10.0–§10.6: four-target installed import, external and nested-CWD privacy, actual cross-filesystem behavior, Linux anonymous/no-replace and failed-closed publication, macOS clone/cleanup boundaries, host receipts, and the step closure gate. The canonical plan requires host receipts to bind candidate revision, execution environment, named probe, result reference, and immutable image digest or `not_applicable`; S03 may close only with all required host lanes, privacy evidence, hermetic tests, and zero unresolved blockers. 

The current code-reviewer severity semantics were applied: any unresolved P0 or P1 makes `review_status=fail`; P2/P3 alone would remain non-blocking. 

### Findings (P0-P3 or None)

1. **[P1] Bind the platform receipts to a reachable pushed probe commit**

   In `report.md:356` and `report.md:362`, the final probe remediation and all actual-host receipts are bound to `0de9687f25c791db47f20958c5aa53b6a03e6cb0`. Exact GitHub connector lookups for that full SHA failed: `fetch_commit` returned “No commit found” and `fetch_file` at that ref returned HTTP 404. By contrast, the earlier executable commit `e02b953a43b303ea99e0fa200f9153f748093825` resolves successfully, but it predates the final direct-call instrumentation.   Because the Linux and macOS receipts cannot currently be traced to a reachable pushed revision containing the reviewed probe implementation, the exact-candidate/probe/result linkage required by §10.3 and §10.6 is not independently verifiable. Whether `0de9687f…` is a transcription error or an amended/force-replaced commit does not change the closure consequence: the ledger must identify the actual reachable pushed commit, or the affected host evidence must be rerun.

No P0, P2, or P3 finding was identified within the bounded scope.

### S03 closure verdict with review_status, counts, production-repair decision, and whether S04 may start

* `review_status`: **fail**
* Unresolved findings: **P0: 0, P1: 1, P2: 0, P3: 0**
* `production_repair_justified`: **false**
* Production/provider repair decision: **none**
* S03 closed: **no**
* S04 may start: **no**

The final probe implementation itself addresses the two prior blocking remediation areas:

* The Linux capability-insufficient lane directly intercepts the installed publisher module’s `os.open` and `os.unlink`, requires zero visible-stage opens and zero pathname-cleanup calls, verifies fault injection, and requires the formal destination to remain absent.
* The macOS lane directly observes `_clone_macos_descriptor` calls and independently intercepts `os.rename`, `os.replace`, and `os.link`; its pass predicate requires clone invocation and zero fallback calls.
* Linux receipts record a 64-hex `sha256:` image binding, while native macOS receipts explicitly record `container_image_digest=not_applicable`. The probe validates and emits those values. 
* The report records actual cross-device Linux and macOS lanes, required host results without `unavailable`, hermetic publisher and CLI receipts, and `production repair: false`. 

Those remediations are substantively correct, but the unreachable probe-revision identifier prevents the host observations from satisfying the exact binding gate.

### Required follow-ups

1. Identify the actual reachable pushed commit containing the final `iss346_platform_probe.py` direct-observation changes. Replace `0de9687f25c791db47f20958c5aa53b6a03e6cb0` in the implementation and platform-receipt ledger with that exact full SHA, and verify that the file blob at that commit matches the implementation used for the recorded runs.

2. If the original executions cannot be durably shown to have used that reachable probe revision, rerun the three Linux probes and two macOS probes against the same candidate-wheel digest. Preserve the current direct-call counters, immutable Linux image digest, native macOS `not_applicable`, ordinary-user status, cross-device boolean, repo-relative commands, probe IDs, and content-free result references.

3. Commit and push the bounded report/evidence correction, verify local/remote branch-tip equality, and obtain a fresh exact-head review. No provider/runtime change is authorized unless the corrected or repeated probes expose an actual production defect.

### Uncertainty and non-findings

This was a read-only, connector-backed review. I did not independently execute pytest, Docker, or either actual-host probe lane; command outcomes and host results remain observed-ledger claims. The inability to resolve `0de9687f…`, however, was directly reproduced through the GitHub connector rather than inferred from the report.

No unresolved portability defect was found. The cross-filesystem test verifies differing `st_dev` values, destination-side publication, source preservation, privacy behavior, and cleans both independently allocated temporary roots in `finally`. 

No unresolved privacy blocker was found. The installed integration test covers absolute and nested-CWD external sources, text and JSON output, path/body/digest/count/derived-value sentinels, controlled negative sensitivity, parsed payloads, bounded public/tracked surfaces, and preservation of the `.agent` snapshot. 

No hermetic-receipt inflation was identified: the report distinguishes the focused publisher result, including its two skips, from the separately required actual Linux and macOS successes; it does not count `unavailable` as Green. No macOS assurance stronger than the accepted same-UID exclusion was claimed.

No bounded-path violation was found. The post-review remediation changed the allowed platform probe plus the Issue report/review artifact; no provider/runtime production file changed. No production defect, ADR change, new platform policy, or S04 behavior was reviewed or established.
