# Overall verdict

**FAIL**

`review_status: fail`
`overall_correctness: patch is incorrect`
`overall_confidence_score: 0.97`

The S04 patch is **incomplete against the approved step contract**. This does not establish a production-code defect: the exact implementation commit is test-only. It does establish three required closure gaps and one additional privacy-oracle gap. Under the supplied reviewer gate, any unresolved P1 requires `fail`; the user-specified gate is stricter and permits PASS only when every severity count is zero. 

## Binding

| Field                                       | Observed binding                                                                                                              |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Repository                                  | `chemitaro/spec-dock`                                                                                                         |
| Default branch                              | `main`                                                                                                                        |
| Reviewed branch                             | `iss-00346-integration-distribution-and-final-quality`                                                                        |
| Requested pushed HEAD                       | `89480b1ef37fa433d398ccc983dd60c716599079`                                                                                    |
| Observed branch HEAD                        | `89480b1ef37fa433d398ccc983dd60c716599079`                                                                                    |
| Binding result                              | **Exact match**; the GitHub connector reported the branch and requested SHA as identical both before and after review         |
| Exact implementation commit scope           | `tests/cli_runtime/test_artifact_import_s04.py`; `tests/integration/test_epic_00343_distribution.py`                          |
| Production-code changes in the exact commit | None                                                                                                                          |
| Review basis                                | Exact GitHub blobs and commit diff, canonical `plan.md`, observed `report.md`, supplied tests, current code-reviewer contract |
| Web research                                | None; only the GitHub connector and supplied files were used                                                                  |

The exact commit describes and contains test-only S04 additions for opaque lifecycle, projection equivalence, and dogfood integration.  The canonical plan is authoritative; the report is the evidence ledger.  

## Severity counts

| Severity  | Unresolved |
| --------- | ---------: |
| P0        |          0 |
| P1        |          3 |
| P2        |          1 |
| P3        |          0 |
| **Total** |      **4** |

# Findings

## [P1] Bind S04 evidence to the reviewed pushed head

**Location:**
`spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/report.md:383-391`

**Condition:** The current S04 implementation is evaluated or closed at pushed HEAD `89480b1ef37fa433d398ccc983dd60c716599079`.

**Contract:** Plan §11.3 requires the opaque lifecycle matrix, compatibility evidence, dogfood matrix, provider-to-dogfood manifest, S04 step/test closures, and delegated-worker evidence. Plan §11.6 requires all legacy suites Green, dogfood closure Green, the real worktree attributable and clean, and the S04 report sections complete. The reviewer contract separately requires Red/alternative evidence, Green results, closure IDs, review scope, and commit/no-op evidence in `report.md`.  

**Impact:** The exact-head report contains only pre-step advice bound to older HEAD `c3da337ad10f51b75943f4856484467bb53f1272`. It expressly says tests had not been run and that final wheel, test, report, and review evidence must bind a later pushed S04 head. It then falls through to generic placeholder rows. There are no exact-head S04 command results, compatibility-suite results, test counts, closure mappings, changed-path receipt, no-production-repair rationale, dogfood manifest, cleanup receipt, or worker evidence. Therefore, the report cannot support S04 closure or prove that the production no-op is justified.

**Minimal fix:** Execute the exact §11.3 S04 command queue against a clean pushed successor, record the actual results and test nodes, add the seven named S04 evidence sections with closure mappings and changed paths, record `production_repair=false` only if the exact-head tests substantiate it, then commit/push and obtain a fresh review against that new head. No production or public-contract change is authorized by this finding.

**Confidence:** 1.00

---

## [P1] Prove provider-to-dogfood projection and exact diff

**Location:**
`tests/integration/test_epic_00343_distribution.py:1171-1174`
Companion location: `tests/integration/test_epic_00343_distribution.py:1308-1310`

**Condition:** `spec-dock update` is stale, becomes a no-op, fails to project one or more managed provider assets, or modifies an unrelated consumer path.

**Contract:** `tc-346-s04-004` requires a pre/post provider-projection manifest, managed projection matching provider changes, and an exact changed-path manifest. `tc-346-s04-005` requires an expected-only checkout diff. These close `CL-346-AC-006` and provider-first ownership under `CL-346-CON-004`. 

**Impact:** The no-backfill test snapshots the canonical initiatives tree and the **provider source tree**, then proves only that update did not mutate those two areas. It never compares managed consumer files under `spec-dock/**` with the wheel/provider assets and never proves that update projected anything. The future-import test merely rejects status paths under `src/spec_dock/assets/spec_dock/` and the ignored payload path; arbitrary unrelated modifications elsewhere in the disposable checkout remain acceptable. Consequently, a broken or stale update projection, consumer-first drift, or an unrelated active/managed-file rewrite can pass both dogfood tests. This also disconnects the source-backed body-open spy from the actual projected dogfood runtime because projection byte parity is not established.  

**Minimal fix:** Add a bounded source-to-projection map for the managed assets relevant to S04, compare wheel/provider bytes with their projected `spec-dock/**` counterparts after update, and assert an exact expected status manifest. The manifest should allow only the dynamically created future issue, its tracked shell/artifact outputs, and known generated files; all other paths must fail the test. Keep the current canonical no-backfill, provider-source immutability, and cleanup checks.

**Confidence:** 0.99

---

## [P1] Add a concurrent generic-versus-legacy slot regression

**Location:**
`tests/cli_runtime/test_artifact_import_s04.py:888-958`

**Condition:** `artifact import file` races at the same fixed timestamp with either legacy `chatgpt-output` import or `new artifact`.

**Contract:** Required closure `CL-346-EC-014` states that legacy/generic same-second slot contention must preserve shared allocation and no-overwrite behavior, with evidence level `concurrent allocation regression`. The S04 compatibility card also explicitly requires shared-slot concurrency cases. 

**Impact:** The newly added Issue 346 S04 cases stop after opaque lifecycle and projection equivalence. Existing coverage is split across scenarios that do not close the cross-command race:

* The existing threaded test races legacy `chatgpt-output` import against legacy import or `new artifact`, not generic file import.
* Generic-versus-typed allocation is tested sequentially through pre-created files.
* Generic file concurrency is tested generic-versus-generic only.

Thus, a regression where generic import and a legacy creator stop sharing the same lock or rescan discipline could overwrite, duplicate a slot, or deadlock while all current tests remain Green. 

**Minimal fix:** Add one barrier-controlled test using the real generic `import_file_artifact` path and one real legacy creator under the same fixed clock and artifacts directory. Assert termination within a bounded timeout, two distinct shared slots, byte preservation for both outputs, and no mutation of an existing sentinel. This is test-only and belongs in an already allowed S04 path.

**Confidence:** 0.98

---

## [P2] Scan dogfood output values for privacy sentinels

**Location:**
`tests/integration/test_epic_00343_distribution.py:1278-1283`

**Condition:** The projected dogfood runtime places body text, a body-derived value, digest, count, or a private parent value into an allowed JSON field or stderr without using the literal key names `sha256` or `byte_count`.

**Contract:** `tc-346-s04-005` requires the projected dogfood import to be privacy-safe. The S04 integration is specifically intended to establish that the provider-projected runtime retains the generic import privacy boundary. 

**Impact:** The test verifies the JSON key set, rejects two key-name strings, and rejects the checkout’s absolute root. It does not scan the flattened JSON values or stderr for the body sentinel, actual digest, count, derived values, or other private path components. For example, a body-derived value placed in `warning_codes`, `source`, or another permitted field would pass. Existing S03 privacy coverage lowers this to P2, but the projected dogfood integration is not independently sensitive to the regression it claims to close.  

**Minimal fix:** Add a dogfood-specific sentinel oracle that permits the expected repository-relative source value but rejects the absolute checkout path, body bytes/text, actual digest, byte count, derived markers, and unexpected private parent values across stdout, stderr, flattened parsed JSON, and any import-owned public provenance files. Exclude the generic destination body itself from the scan.

**Confidence:** 0.94

# Verified without a finding

## Opaque filter-before-read and spy construction

The new matrix imports binary, ZIP, invalid UTF-8, NUL-bearing, and ADR-looking generic artifacts through the projected public command. The sensitivity read is performed under a separate monkeypatch context; the measured lifecycle guard is freshly allocated and starts with an empty observation list. It intercepts `Path.open`, `Path.read_text`, `Path.read_bytes`, `builtins.open`, and `io.open`, and source/destination body equality is checked only after the measured guard exits.  

`bootstrap.build_runtime` constructs ports and use-case closures; the inspected bootstrap path does not itself open artifact bodies before the measured guard.  The harness executes projected CLI commands in subprocesses, while the guarded lifecycle calls are in-process, so the import-copy reads are not incorrectly counted as lifecycle reads.

## Projection and context equality

The new projection test requires the complete enumerated projection set and compares indexes, tree/dependency JSON and PUML, dashboard, active context pack, dependency JSON output, ADR mirror, and typed artifact names before and after generic imports. The top-level `generated_at` field is removed from JSON snapshots; non-JSON projections and the separately captured context/deps outputs remain exact comparisons.

## Disposable checkout, no-backfill, and cleanup

The dogfood helper creates a local no-hardlink clone, checks out the exact candidate revision detached, verifies a clean checkout, and restores a GitHub origin URL. Both tests delete the disposable checkout and assert deletion; they also prove the real provider repository’s HEAD and status are unchanged. The no-backfill negative deliberately inserts the forbidden Epic README and proves the oracle rejects it.

The future payload is checked as ignored and absent from `git ls-files`; after import and lifecycle commands it remains ignored and absent from status. The future README is byte-compared with the wheel’s Issue shell template.

## Repair boundary

The exact implementation commit changes only the two allowed test files. No production path, public API, provider source, canonical plan, or backfill behavior was changed in that commit. Therefore:

* **Wrongly introduced production repair:** none found.
* **Provably missing production repair:** none established by static inspection.
* **No-production-repair conclusion:** still provisional because the exact-head Green and compatibility evidence is absent from `report.md`.

# Non-blocking risks

1. I did not execute the test suites. The exact pushed report contains no S04 run receipt, and the GitHub connector returned no combined status contexts or pull-request workflow runs for this SHA. Actual pass counts, durations, skips, and platform behavior remain unverified.
2. JSON projection snapshots are reserialized with sorted keys and compact separators after removing `generated_at`. That makes formatting-only JSON drift invisible. Because the planned expectation is semantic equivalence, I did not elevate this to a finding, but it should be documented as the intentional normalization boundary rather than described as timestamp-only byte normalization.
3. The new tests use temporary directories, fixed clocks, dynamic future issue allocation, bounded thread timeouts in existing concurrency coverage, and explicit cleanup. No new deterministic flake mechanism was identified in the S04 additions themselves.

# Assumptions and unverified claims

* The canonical `plan.md` was treated as authoritative and the pre-step Artifact as advisory, as instructed.
* The reviewed GitHub branch remained exactly at `89480b1ef37fa433d398ccc983dd60c716599079` through the final binding check.
* No test result or production no-op claim has been inferred from test source alone.
* PASS requires **P0=0, P1=0, P2=0, and P3=0**. The current counts are `0/3/1/0`, so the only valid overall result is **FAIL**.
