### Review scope and head binding

GitHub connector inspection succeeded on `chemitaro/spec-dock`, branch `iss-00346-integration-distribution-and-final-quality`; the default-branch fallback was not used.

* Current pushed branch tip: `675579ad5cc05fbec88f7b8c9e5951cdaf3e3bef`.
* Executable S03 commit: `5d6f1f88583ca138caa7fe9a29475560e5446b44`.
* The executable commit adds only `tests/integration/test_epic_00343_distribution.py` and `tests/integration/iss346_platform_probe.py`; it makes no provider/runtime production change.
* The only commit from `5d6f1f88` to the current tip is the report-only S03 evidence transcription at `675579ad`.
* The attached plan, report, integration test, platform probe, and reviewer instructions match the corresponding branch blobs inspected through GitHub.     

Review scope was limited to S03 §10.0–§10.6: installed four-target import, external and nested-CWD privacy, actual cross-filesystem behavior, Linux anonymous/no-replace/fail-closed publication, macOS clone/cleanup, receipt honesty, and bounded paths. Under the current code-reviewer gate, any unresolved P0 or P1 requires `review_status=fail`.

### Findings

1. **[P1] Make the actual cross-filesystem test capability-safe on Linux** — `tests/integration/test_epic_00343_distribution.py:918-920`
   The test creates its destination workspace and then unconditionally calls `mkdtemp(..., dir="/private/tmp")` before entering the `try/finally`. On any required host where `/private/tmp` does not exist, including ordinary Linux installations, it raises before the `st_dev` capability check and before cleanup, leaving the first temporary directory in the repository and failing the suite rather than recording the cross-filesystem lane as unavailable. Select from existing host roots, put both allocations under cleanup, and skip or return unavailable only after an actual device comparison.

2. **[P1] Make every platform probe fail when a safety assertion is false** — `tests/integration/iss346_platform_probe.py:204-221, 255-278, 368-400`
   The Linux supported probe returns `result="pass"` and exit status `0` after checking only committed state and byte equality; `first_link_target_is_formal_destination`, visible-stage absence, pathname-cleanup absence, and collision preservation can all be false without failing the process. The macOS probe similarly passes even when destination-side staging, cleanup, collision preservation, or device binding is false. The Linux insufficient probe does not require `fault_injected=true` and unconditionally reports `pathname_cleanup_absent=true`. Consequently, an unsafe regression can produce an exit-0 “pass” receipt containing false safety fields, contrary to the plan’s requirement that contract defects return `1`. All required observations must participate in the pass predicate, and unobserved properties must not be emitted as true.

3. **[P1] Add the required privacy sensitivity negative and provenance scan** — `tests/integration/test_epic_00343_distribution.py:303-325, 858-913`
   The plan requires a controlled renderer/output leak negative and scanning of captured output, parsed JSON, and any public provenance or tracked-text changes made by the import. The implementation invokes the privacy helper only against real successful output and snapshots only `spec-dock/.agent`; there is no deliberately leaked output proving the oracle fails, and a leak written to another public/tracked file can remain undetected. Add a controlled negative for path, body, digest/count, and derived-value leakage, together with a bounded changed-path inventory that scans any public provenance files created or modified by the import.

4. **[P1] Supply current-head Green evidence for the required hermetic suites** — `report.md:353-355, 369-374`
   The report records only the three `-k s03` integration tests, Ruff, and `git diff --check`. It does not record the planned focused run of `tests/unit/infra/test_binary_artifact_publisher.py` or `tests/cli_runtime/test_artifact_import_file.py`. Those existing tests contain the Linux O_TMPFILE/procfs/formal-capability fault cases and the macOS-style missing/replacement/type/stat/fstat/open cleanup matrix, but their presence is not current-head execution evidence. Therefore the report’s claims that Linux failure classes and the macOS cleanup trust boundary are Green are not yet supported, and the §10.6 “all hermetic tests Green” condition is unmet.

5. **[P1] Correct the platform receipts so every claim is content-free and traceable** — `report.md:357-367`
   The report says no host-local absolute path or UID was recorded while the same table contains `/Volumes`, `/private/tmp`, and `501:20`. It attributes `uncertain_stage_retained_without_unlink=true` to the macOS actual-host row even though `macos-clone-publication` never emits that field. It also omits required receipt elements including kernel, explicit filesystem type for macOS, execution kind, repo-relative command, result-evidence reference, and an explicit per-host candidate binding. These contradictions prevent independent verification and improperly mix hermetic cleanup evidence with actual-host output. Record the raw content-free JSON result or a stable evidence reference, remove host paths and numeric identity, and include only fields actually emitted or separately linked to named hermetic tests.

### S03 closure verdict

* `review_status`: **fail**
* `overall_correctness`: **S03 closure packet is incorrect/incomplete**
* Unresolved findings: **P0: 0, P1: 5, P2: 0, P3: 0**
* Production repair established by this review: **none**
* S03 closed: **no**
* **S04 may start: no**

The four-target and host runs may reflect correct current production behavior, but the test/probe oracles and the observed-evidence ledger do not yet meet the mandatory privacy, platform-failure, cleanup, and receipt-honesty contracts. Because pass requires zero unresolved P0/P1, the current exact-head review cannot authorize S03 closure.

### Required follow-ups

1. Repair only the S03 test/probe/report surfaces for the five findings; do not change provider/runtime production code unless a corrected test or actual-host run demonstrates a production defect.
2. Make the cross-filesystem test portable and cleanup-safe, then rerun it on both the required macOS lane and a Linux environment without relying on `/private/tmp`.
3. Convert every probe safety field into an enforced predicate, require the intended fault point to execute, snapshot source bytes before publication, and directly observe any pathname cleanup or fallback claim.
4. Add the controlled privacy negative and bounded public-provenance/tracked-change scan.
5. On the resulting pushed successor, run and record the plan’s focused publisher-unit, CLI-runtime, integration, Linux actual-host, and macOS actual-host commands, including exact node/probe IDs and content-free result references.
6. Correct the S03 closure ledger and receipts, commit and push the bounded remediation, verify local/remote head equality, and obtain a fresh exact-head review. S04 remains blocked until that review has no P0/P1.

### Uncertainty and non-findings

* This was a read-only inspection. I did not independently execute pytest, Docker, or macOS host commands; reported command outcomes remain observed-ledger claims rather than independently reproduced results.
* No S03 production/provider source was changed, so this review does not identify or request a production fix. All current blockers are in test construction, host-probe gating, or report evidence.
* The executable changes stay within S03’s allowed test/probe paths, and the successor changes only the canonical report. No bounded-path violation was found.
* The four-target test does exercise root, Initiative, Epic, and Issue routing; checks destination bytes, source preservation, `canonical=false`, and a root collision/no-overwrite case. No P0/P1 finding was identified in that target-routing portion itself.
* No conclusion was drawn about S04 behavior or Issue 345 implementation correctness.
