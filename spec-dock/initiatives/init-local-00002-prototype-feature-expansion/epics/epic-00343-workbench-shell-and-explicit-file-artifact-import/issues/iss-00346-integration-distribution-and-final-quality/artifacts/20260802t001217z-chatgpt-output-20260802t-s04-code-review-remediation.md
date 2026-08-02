# Overall verdict

**FAIL**

* `review_status: fail`
* `overall_correctness: patch is incorrect`
* `overall_confidence_score: 0.99`

The GitHub connector confirmed immediately before this verdict that branch `iss-00346-integration-distribution-and-final-quality` remained **identical** to requested HEAD `4565f1839a2a93d3dce43d1abca82a2bd41034e1`. The exact commit is a report-only successor of S04 remediation commit `0c510e2137a6b211dd7a0d881f0c7d2190fdff97`; the S04 implementation range from pre-step HEAD changes two test files plus the Issue report and evidence Artifacts, with no production-code change.

## Severity counts

| Severity  | Unresolved |
| --------- | ---------: |
| P0        |          0 |
| P1        |          2 |
| P2        |          2 |
| P3        |          0 |
| **Total** |      **4** |

PASS is not permitted because every unresolved count is not zero.

# P0 findings

None.

# P1 findings

## [P1] Bind the S04 ledger to the reviewed pushed HEAD

**Location:**
`spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/report.md:391-399`
Companion location: `report.md:486-489`

**Condition:** S04 is reviewed or closed at current pushed HEAD `4565f1839a2a93d3dce43d1abca82a2bd41034e1`.

**Contract:** Plan §11.6 requires the review to bind the pushed head and requires the S04 report sections to be complete. The report is the observed evidence ledger and must distinguish executable/test evidence from later report-only successors.

**Impact:** The section titled “S04 implementation evidence (exact pushed head)” records both candidate and remote HEAD as `0c510e...`, while the reviewed branch tip is `4565f183...`. The report does not identify `4565f183...` as the report-only successor or record the connector-verified fact that `0c510e...4565f183` changes only `report.md`. It also still says that a fresh exact-head review is required. A reader using the ledger alone therefore cannot establish which revision the current review covers, whether the wheel and test evidence remain attributable, or whether the closure row is current.

**Minimal fix:** Record separate fields for `S04 executable/test head=0c510e...` and `reviewed report successor=4565f183...`, include the one-file successor comparison, and explicitly bind the review verdict to `4565f183...`. After importing or transcribing this review and pushing the resulting successor, obtain the required fresh exact-head follow-up; rerun the wheel/tests only if executable, provider, or test inputs change.

**Confidence:** 1.00

---

## [P1] Assert the actual shared slots in the cross-command race

**Location:**
`tests/cli_runtime/test_artifact_import_s04.py:421-435`

**Condition:** Generic file import and the legacy blank creator use different locks or independently allocate the unsuffixed slot at the fixed timestamp.

**Contract:** `CL-346-EC-014` and `tc-346-s04-003` require a concurrent generic-versus-legacy allocation regression proving **shared allocation** and no overwrite, not merely two different filenames.

**Impact:** The oracle accepts both of these outputs simultaneously:

```text
20260714t010203z--concurrent-generic.bin
20260714t010203z-legacy-concurrent-notes.md
```

They are naturally different because the generic and legacy filename grammars and slugs differ, but both consume the same unsuffixed timestamp slot. Every current assertion still passes in that state. The test therefore does not prove that one command received the base slot and the other received `-01`, even though the production ledger defines slots by timestamp and suffix across both artifact families. The report’s claim that the outputs received distinct slots is stronger than the test establishes.

**Minimal fix:** Parse both resulting filenames with the production parsers and assert that their slot set is exactly `{(timestamp, None), (timestamp, 1)}`, independent of which thread wins. Also run `scan_artifact_slot_ledger` after both operations and require no duplicate-slot error, while retaining the source, destination, and sentinel byte checks.

**Confidence:** 1.00

# P2 findings

## [P2] Limit projection normalization to `generated_at`

**Location:**
`tests/cli_runtime/test_artifact_import_s04.py:151-161`
S04 usage: `tests/cli_runtime/test_artifact_import_s04.py:188-190` and `:1022`
Companion evidence: `report.md:418-422`

**Condition:** A JSON projection changes key ordering or whitespace while retaining the same parsed object after generic imports.

**Contract:** `tc-346-s04-002` says to normalize only the known generated timestamp, detect over-normalization, and use exact comparison for the projection/context evidence. Plan §11.3 repeats that normalization is limited to timestamps or known generated fields.

**Impact:** `_projection_snapshot` removes `generated_at` but then reserializes every JSON projection with sorted keys and compact separators. That also erases key-order and formatting changes. Two byte-distinct JSON projections therefore compare equal even though the report says that only the named `generated_at` field was normalized. The semantic fields remain covered, so this is not classified as P1, but the current closure evidence is not an honest timestamp-only comparison.

**Minimal fix:** Preserve two checks: parsed-object equality after removing only `generated_at`, and raw-byte equality after replacing only the concrete `generated_at` value in otherwise untouched JSON text. Alternatively, an approved plan amendment would need to state explicitly that JSON serialization and key order are intentionally outside the contract; the current canonical plan does not.

**Confidence:** 0.97

---

## [P2] Make the dogfood privacy oracle detect sanitized body and count leaks

**Location:**
`tests/integration/test_epic_00343_distribution.py:419-434`
Fixture location: `tests/integration/test_epic_00343_distribution.py:1338-1340`

**Condition:** The projected runtime exposes the printable body text after stripping binary control bytes, or exposes the byte count as text in stdout, stderr, an allowed JSON string, or provenance content.

**Contract:** `tc-346-s04-005` requires the projected dogfood import to remain privacy-safe. The initial review specifically required body, digest, count, derived-value, and private-path sentinels across stdout, stderr, flattened JSON, and bounded public provenance.

**Impact:** The forbidden body value is the complete ASCII-decoded payload, including its NUL and trailing newline. An output such as `S04 dogfood generic payload`—the likely form after sanitization or trimming—does not contain that exact sentinel and passes. The byte count is checked only as numeric scalar equality in parsed JSON; the string `"30"` or text such as `count=30` is not rejected. Thus the test can pass while leaking body text or the count through a public surface, contrary to the report’s stronger claim.

**Minimal fix:** Embed and scan a dedicated printable body marker independently of the binary suffix, choose a deliberately distinctive byte count and detect it as a token in all textual surfaces, and add controlled negatives that inject the printable body marker and count into stdout, stderr, parsed JSON strings, and a bounded provenance file. Continue excluding the generic destination body itself.

**Confidence:** 0.99

# P3 findings

None.

# Verified without a finding

## Opaque lifecycle and filter-before-read

The five fixtures are imported through the projected public command before measurement. The sensitivity read runs under a separate monkeypatch context, while the measured guard starts fresh and intercepts `Path.open`, `Path.read_text`, `Path.read_bytes`, `builtins.open`, and `io.open`. The lifecycle calls are in-process rather than routed through a harness that reads the generic destinations, and source/destination byte verification occurs after the measured guard exits. The matrix covers binary, ZIP, invalid UTF-8, NUL-bearing, and ADR-looking generic files.

## Provider-to-dogfood projection and expected paths

The remediation now compares every regular wheel asset under managed roots `docs`, `templates`, `scripts`, and `system` byte-for-byte with the projected consumer tree and rejects missing or unexpected managed paths. Both dogfood tests perform the parity check after update, and the update-only and future-flow tests compare the resulting status path sets with explicit expected manifests. No separate projection-parity finding remains.

## Compatibility

The report records focused results for the existing chatgpt-output, Workbench, generic import, nearest new-artifact, unit, and full distribution suites. No legacy public expectation was changed in the S04 diff. The blocker is the new cross-command race oracle’s insufficient assertion, not a demonstrated legacy production regression.

## Hermeticity and cleanup

The dogfood tests use a local no-hardlink clone, detached checkout of the candidate revision, a local GitHub stub, dynamically selected future issue number, and `finally` cleanup. They verify deletion of the disposable checkout and preservation of the provider repository’s HEAD and status. The S04 implementation changes are confined to the two plan-authorized test files; the remaining changed paths are the target report and Issue-local evidence Artifacts. No production repair or forbidden path was introduced.

# Non-blocking risks

* I did not independently execute the reported test commands. GitHub exposes no combined status contexts or pull-request workflow runs for `4565f183...`; the pass counts and durations remain report evidence rather than independently reproduced results.
* The exact-head GitHub inspection establishes that `4565f183...` is one report-only commit after `0c510e...`. That materially lowers code-staleness risk, but it does not repair the missing two-head binding inside the report itself.
* No production defect was established. All blocking findings concern the validity and freshness of the S04 closure evidence and test oracles.

# Final gate

`review_status: fail`

`review_status_reason:` Two P1 closure defects remain: the evidence ledger is not bound to the reviewed branch tip, and the generic-versus-legacy race test does not prove distinct shared slots. Two additional P2 evidence-oracle defects remain. Under the requested zero-unresolved gate, S04 cannot PASS with counts `P0=0, P1=2, P2=2, P3=0`.
