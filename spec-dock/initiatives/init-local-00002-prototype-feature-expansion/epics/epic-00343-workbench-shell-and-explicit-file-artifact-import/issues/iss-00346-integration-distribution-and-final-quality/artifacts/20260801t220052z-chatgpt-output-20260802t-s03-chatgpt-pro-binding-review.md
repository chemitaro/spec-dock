### Review scope and head binding

GitHub connector inspection succeeded on **2026-08-02** for `chemitaro/spec-dock`. The feature branch `iss-00346-integration-distribution-and-final-quality` was inspected first; the default-branch fallback was not used. The branch ref resolves exactly to the requested pushed head:

`f4b9b18a6d006335544bd88143fd3696710dcb3e`

The connector comparison between that SHA and the branch ref was identical, with no ahead/behind delta. The head is a report/review-evidence correction, not a provider-runtime repair.

The review was limited to canonical plan S03 §10.0–§10.6: candidate-wheel-installed four-target import, external and nested-CWD privacy, actual cross-filesystem behavior, Linux anonymous/no-replace and fail-closed publication, macOS clone/cleanup boundaries, host and hermetic receipts, and the S03 closure gate. 

The previously blocking probe SHA is now valid:

`0de9687f636ef0c3a185f5e9e112fe0ca180990a`

GitHub resolves it as a reachable commit whose only implementation file is `tests/integration/iss346_platform_probe.py`.  The file has Git blob SHA `d0aac0b18ca75b486ebbe679bcfe2ac979878bb7` both at `0de9687f…` and at current head `f4b9b18a…`; the attached platform probe has the same Git blob identity.   

That exact blob contains the implementation claimed by the content-free receipts:

* Linux capability-insufficient publication directly intercepts the installed publisher module’s `os.open` and `os.unlink`, counts visible-stage opens and pathname-cleanup calls, requires both counts to be zero, requires the intended fault to be injected, and requires the formal destination to remain absent.
* macOS publication directly wraps `_clone_macos_descriptor` and separately intercepts `os.rename`, `os.replace`, and `os.link`; its pass predicate requires clone invocation, zero fallback calls, destination-side exclusive/no-follow staging, no-replace formal publication, collision preservation, cleanup, byte equality, source preservation, and stable parent identity.

The canonical report now binds the receipts to the full reachable probe SHA, the candidate revision `e02b953a43b303ea99e0fa200f9153f748093825`, wheel basename `spec_dock-0.2.3-py3-none-any.whl`, and wheel SHA-256 `47326f1d064448009e7f7ededf272a5b51fad06ae9a481b2171903489b84309c`.   The provider publisher blob is unchanged between the candidate revision and current head, and the commits after the candidate affect only S03 tests/probe/report/review artifacts.

The current GitHub blobs for the canonical plan, report, integration test, platform probe, and reviewer instructions also match the supplied files.     

### Findings (P0-P3 or None)

**None.**

No actionable P0, P1, P2, or P3 defect was found within the bounded S03 scope.

The prior P1 is resolved: the active evidence ledger no longer depends on an unreachable SHA, and the corrected reachable commit contains exactly the direct-observation probe implementation to which the Linux and macOS receipts are attributed.

### S03 closure verdict with review_status, counts, production-repair decision, and whether S04 may start

* `review_status`: **pass**
* `overall_correctness`: **patch is correct**
* Unresolved findings: **P0: 0, P1: 0, P2: 0, P3: 0**
* `production_repair_justified`: **false**
* Production/provider repair decision: **none**
* S03 closed: **yes**, subject only to bounded transcription of this review verdict
* S04 may start: **yes**, after the S04 pre-step head-binding gate

The closure basis is:

1. **Candidate-wheel binding:** the fixture computes the digest of one deterministic wheel path, installs that same path, and retains the same wheel for inventory and installed-runtime execution. The report binds the S03 host evidence to its candidate revision, basename, and digest; provider/runtime bytes did not change after that candidate.

2. **Four-target installed import:** root, Initiative, Epic, and Issue selectors are exercised through the wheel-installed projected runtime. Each case checks target routing, destination bytes, source preservation, `canonical=false`, and correct artifact directory; the root case also proves collision preservation and shared-slot advancement.

3. **Privacy negative and provenance scan:** absolute and nested-CWD external sources are exercised in text and JSON modes. The oracle checks absolute and parent paths, body text, digest, byte count, derived values, and content-derived field names; it includes controlled leak negatives, parsed JSON values, bounded `.agent`/tracked public surfaces, and preservation of the pre-import `.agent` snapshot.

4. **Actual cross-filesystem evidence and portability:** the integration test selects `/private/tmp` only when available and otherwise `/tmp`, verifies different `st_dev` values before counting the lane as success, confirms destination-side publication and privacy, and cleans both independently allocated temporary roots in `finally`. The host ledger additionally records `source_destination_same_device=false` for both macOS and Linux.

5. **Linux publication boundary:** preflight, supported publication, and capability-insufficient probes are distinct. The report uses one immutable 64-hex `sha256:` image digest consistently across all Linux rows, records non-root execution and cross-device placement, and reports no visible stage, no pathname cleanup, no fallback, no overwrite, byte equality, and source preservation. No `unavailable` result is counted as success.

6. **macOS publication boundary:** both macOS rows explicitly use `container_image_digest=not_applicable`. The actual publication row reports four clone primitive calls, zero copy/rename/link fallback calls, destination-side secure staging, no-replace publication, cleanup, collision preservation, byte equality, source preservation, and the accepted same-UID exclusion without expanding the trust claim.

7. **Hermetic evidence:** the ledger separately records the S03 integration run, focused publisher suite, CLI-runtime suite, Ruff, bytecode compilation, and diff check. Its `59 passed, 2 skipped` publisher result is not substituted for the separately required actual Linux and macOS successes, and no skip or `unavailable` result is represented as actual-host Green.

8. **Bounded paths:** the executable S03 delta is confined to the two plan-authorized test/probe paths. Later commits contain only report and review-artifact evidence. No production/provider file, accepted ADR, platform policy, or S04 behavior changed. The reviewer gate therefore has no production repair to authorize. The applied priority and gate semantics match the current code-reviewer contract: only P0/P1 block a pass, while any P2/P3 would still have been reported.

### Required follow-ups

No blocking implementation, test, probe, host-rerun, or production-repair follow-up is required.

The remaining workflow action is evidence-only: transcribe this exact-head `pass` verdict and counts into the bounded S03 review/report artifact, without changing the reviewed test, probe, or provider/runtime content. Before starting S04, execute its required pre-step gate against the then-current pushed successor and re-confirm local/remote head equality.

The corrected SHA alone does not require repeating the host lanes because the reachable commit’s probe blob exactly matches the implementation already identified by the receipts. A rerun becomes necessary only if the candidate-wheel digest, provider/runtime blob, probe blob, or host-evidence claims are subsequently changed.

### Uncertainty and non-findings

This was a read-only connector-backed review. I did not independently execute pytest, build the wheel, start the Linux container, or run either actual-host platform lane. Therefore, the reported wheel SHA-256, command outcomes, kernel/filesystem observations, and probe result values remain observed-ledger claims rather than independently reproduced measurements. The branch/head identity, commit reachability, ancestry, changed paths, GitHub blob identities, and equality of the supplied probe to the reachable GitHub blob were independently verified.

No unresolved candidate-wheel provenance defect was found. The test fixture binds digest calculation and installation to the same wheel path, and no provider/runtime change occurs after the recorded candidate revision.

No unresolved privacy or provenance-scan blocker was found. The oracle has controlled sensitivity negatives and covers text, stderr, parsed JSON, bounded public/tracked files, and `.agent` preservation while excluding the imported generic body from the public-surface scan.

No unresolved portability defect was found. Unavailable cross-device placement is skipped rather than counted as success, and both temporary roots are cleanup-protected.

No unsafe Linux named-stage, visible-probe, pathname-cleanup, overwrite, or fallback behavior was established. No macOS copy/rename/link fallback or assurance stronger than the accepted same-UID exclusion was established.

No hermetic-receipt inflation, bounded-path violation, production defect, ADR change, new platform-support decision, or S04-scope conclusion was identified.
