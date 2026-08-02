# S90 Documentation-Impact Pre-Step

**Repository binding:** `chemitaro/spec-dock`
**Branch:** `iss-00346-integration-distribution-and-final-quality`
**Exact pushed HEAD:** `ef467c1b84d9d7dfce64c6c4d98bcea5c560fc81`
**Disposition:** **bounded provider-doc refresh required**. An inspect-only S90 no-op is not correct.

The exact HEAD records the S04 code gate as passed with no remaining P0–P3 findings.  The S90 plan explicitly requires inspect-first resolution of platform wording, fast/full regression wording, provider projection parity, and complete Issue/Epic report and EAL trace.  The review used the attached current `spec-reviewer` evidence, materiality, and report-ledger criteria. 

## Observed gaps

| Contract area                                        | Status at `ef467c1b`                                                                                                                                                                                                                                                                                                                                                           | S90 action                                                                                                                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Workbench ignored/non-secret guidance                | **Complete.** README and guide say Workbench is optional, temporary, disposable, non-canonical; only direct-child `.workbench/README.md` is tracked; other payload is ignored; Git ignore is not a security boundary. README explicitly prohibits secrets, credentials, and private customer data.                                                                             | Preserve wording; no semantic rewrite.                                                                                                                                                               |
| No-backfill                                          | **Complete.** Fresh roots/future nodes get the shell; existing scopes do not.                                                                                                                                                                                                                                                                                                  | Preserve wording and reverify through candidate-wheel update.                                                                                                                                        |
| Generic import target/source/privacy/opaque boundary | **Complete.** The four selectors, one explicit regular file, source preservation, opaque bytes, external basename-only disclosure, repository-relative disclosure, digest/count/content suppression, `canonical=false`, and no automatic adoption are documented.                                                                                                              | Preserve wording; avoid duplicating it elsewhere.                                                                                                                                                    |
| Generic identity/shared slots                        | **Complete.** `reference_naming.md` correctly records `<ts>--<normalized-basename>`, collision suffixes, and the shared typed/blank/generic slot ledger.                                                                                                                                                                                                                       | Inspect-only for this file unless implementation reveals a contradiction.                                                                                                                            |
| Linux publication                                    | **Gap.** Current user-facing docs do not state that explicit generic import requires anonymous `O_TMPFILE` staging on Linux and does not fall back to named staging when that capability is unavailable. The implementation selects anonymous staging for the explicit-file publication probe and fails with `publication_unsupported` when `O_TMPFILE` cannot be established. | Add bounded, user-facing no-fallback wording.                                                                                                                                                        |
| macOS publication and cleanup                        | **Gap.** Current user-facing docs do not explain destination-side named staging, no-replace `fclonefileat` publication from the verified staged descriptor, conservative identity/type-checked cleanup, or cleanup uncertainty.                                                                                                                                                | Add bounded platform wording. Do not claim that the accepted same-UID final-check-to-unlink exclusion has been eliminated. The canonical design expressly requires that exclusion to remain visible. |
| Fast versus explicit full regression                 | **Gap and stale statement.** README and guide still say candidate-wheel consumer E2E and full regression are “deferred to Issue #346,” although S02–S04 evidence now exists.   The actual policy is that ordinary `uv run pytest` applies the default full-regression skip, while `--run-full-regression` opts in.                                                             | Replace the stale deferral sentence with current fast/full lane wording without claiming Issue 346 or S99 is complete.                                                                               |
| Provider-to-dogfood docs parity                      | **Currently complete.** All four allowlisted pairs have identical Git blob SHA values at this HEAD: README, guide, reference naming, and root artifact rules.                                                                                                                                                                                                                  | Preserve provider-first ownership and re-establish exact parity after the refresh.                                                                                                                   |
| Issue report/EAL trace                               | **Incomplete.** The EAL stops at S01-era entries; EAL-004 still says S01 is blocked and EAL-005 still says reviewer work is pending, despite S01–S04 closure.  The S90 final-quality row remains a `yes / no`, `...`, `pass / fail / blocked` placeholder.                                                                                                                     | Update S02–S04 adoption/rejection dispositions, eliminate stale next actions, and complete S90 evidence and closure rows.                                                                            |
| Epic report/Candidate 3 trace                        | **Incomplete and stale.** The Epic summary still describes Issue 345 amendment review as pending and S02 as not resumed, rather than tracing Issue 346 S01–S04 completion and the remaining S90/S99 boundary.                                                                                                                                                                  | Add a concise Candidate 3 trace linked to the Issue report; do not duplicate raw test/review logs.                                                                                                   |

## Required changes

### Minimum expected changed paths

1. `src/spec_dock/assets/spec_dock/docs/README.md`

   * Replace the stale Issue 346 deferral sentence.
   * State the ordinary fast lane versus explicit `--run-full-regression` lane.
   * Add only a concise platform-safety summary or a pointer to the detailed guide wording.

2. `src/spec_dock/assets/spec_dock/docs/guide.md`

   * Add the authoritative bounded platform explanation:

     * Linux: anonymous `O_TMPFILE` staging; no named-temp success fallback.
     * macOS: destination-side named stage; staged-FD `fclonefileat` no-replace publication; conservative cleanup.
     * Cleanup uncertainty may produce a committed result with warning rather than unsafe unlink or retry guidance.
     * The accepted same-UID final-check-to-unlink exclusion remains an exclusion and must not be described as solved.
   * State the fast/full regression distinction.

3. `spec-dock/docs/README.md`

4. `spec-dock/docs/guide.md`

   * Generated/projected from the provider source through the candidate-wheel update path.
   * Do not hand-author consumer-first divergence.

5. `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/report.md`

   * Fill the S90 documentation-impact section.
   * Record exact changed/no-op paths and provider-to-projection parity.
   * Add EAL dispositions for the S02–S04 pre-step and review evidence actually used.
   * Resolve stale EAL-004/EAL-005 next actions and reviewer states.
   * Close or supersede stale decision-ledger entries; record no material product decision if that remains true.
   * Add S90 reviewer status and closure evidence for `CL-346-AC-016`, `CL-346-CON-004`, `CL-346-CON-008`, `CL-346-CON-012`, and `CL-346-EC-016`.

6. `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/report.md`

   * Bring Candidate 3 progress through S04.
   * Record S90 docs/parity status and that S99 remains.
   * Link to the Issue evidence rather than copying matrices and transcripts.
   * Correct stale blocking/pending EAL or progress statements.

### Allowed but expected inspect-only paths

These remain inside the S90 allowlist but do not currently require prose changes:

```text
src/spec_dock/assets/spec_dock/docs/reference_naming.md
src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md
spec-dock/docs/reference_naming.md
spec-dock/docs/rules/root/artifacts.md
```

Their current contracts are accurate and their provider/projection pairs are byte-identical. Editing them without a newly observed gap would be unnecessary churn.

No runtime mirror is eligible in S90 at this HEAD: S04 records `production repair=false`, and the S90 conditional runtime-projection allowance therefore does not activate.

## Structural checks

Use `ef467c1b84d9d7dfce64c6c4d98bcea5c560fc81` as the S90 baseline.

```bash
BASE=ef467c1b84d9d7dfce64c6c4d98bcea5c560fc81

# Scope guard
git diff --name-only "$BASE" HEAD
git diff --check

# Required concepts and stale wording
rg -n \
  'workbench|no-backfill|security boundary|artifact import file|opaque|canonical=false|O_TMPFILE|fclonefileat|same-UID|run-full-regression' \
  src/spec_dock/assets/spec_dock/docs/README.md \
  src/spec_dock/assets/spec_dock/docs/guide.md \
  src/spec_dock/assets/spec_dock/docs/reference_naming.md \
  src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md

! rg -n 'deferred.*Issue #346|Issue #346.*deferred' \
  src/spec_dock/assets/spec_dock/docs/README.md \
  src/spec_dock/assets/spec_dock/docs/guide.md

# Exact checked-in parity
cmp -s src/spec_dock/assets/spec_dock/docs/README.md \
       spec-dock/docs/README.md
cmp -s src/spec_dock/assets/spec_dock/docs/guide.md \
       spec-dock/docs/guide.md
cmp -s src/spec_dock/assets/spec_dock/docs/reference_naming.md \
       spec-dock/docs/reference_naming.md
cmp -s src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md \
       spec-dock/docs/rules/root/artifacts.md

# Targeted managed-doc parity
uv run pytest \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets

# Candidate-wheel projection, not the GitHub-fetching repository wrapper
"$ISS346_VENV/bin/spec-dock" update "$ISS346_DOGFOOD_REPO"

# Repository gates
make check
uv run pytest
uv run pytest --run-full-regression
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

After candidate-wheel update, verify all of the following:

* Existing `epic-00343/.workbench/README.md` remains absent.
* Provider and projected docs are byte-identical.
* No unrelated canonical or active data changes.
* The changed-path manifest is confined to the S90 allowlist.
* Ordinary pytest records its policy skip; explicit full regression executes the marked nodes.
* Reports contain no unresolved `blocked`, `stale`, `pending`, placeholder, or `Status=open` entry relevant to S01–S90.

## Recommended S90 execution and closure checklist

* [ ] Record baseline branch, exact HEAD, clean-state evidence, and this pre-step artifact disposition.
* [ ] Delegate only the provider README/guide refresh to `doc-writer`; keep reports under orchestrator ownership.
* [ ] Update provider docs first; do not edit dogfood copies first.
* [ ] Review and commit the provider-doc change before rebuilding the candidate wheel, as required by the S90 plan.
* [ ] Build/install the new candidate wheel and update a disposable exact-revision dogfood checkout.
* [ ] Re-establish exact provider/projection parity and prove no-backfill and unrelated-diff negatives.
* [ ] Update the Issue and Epic reports, including EAL, decision-ledger, exact-head, reviewer, and closure trace.
* [ ] Run structural, targeted, fast, explicit-full, validate, and sync checks.
* [ ] Obtain a fresh `spec-reviewer` docs/spec-alignment `pass` against the final pushed S90 head.
* [ ] Close S90 as **committed**, not `approved-no-op`, with a clean post-commit status. Leave S99 explicitly pending.

## Amendment triggers

Stop S90 and return to amendment/re-review if any of these occurs:

* A required change falls outside the ten allowlisted docs/report paths.
* Correct documentation would require changing runtime, tests, templates, skills, workflows, or canonical requirement/design/plan.
* Current behavior conflicts with an accepted ADR or the approved platform contract.
* The Linux fallback policy, macOS cleanup trust boundary, or same-UID exclusion needs a new product decision rather than documentation.
* Fast/full test policy itself must change.
* Candidate-wheel update backfills an existing Workbench shell or mutates unrelated canonical data.
* A durable report decision has no existing canonical design/ADR/plan authority.

## Uncertainty and unverified claims

The recommended division—platform detail in `guide.md`, concise summary/pointer and test-lane wording in `README.md`—is the smallest coherent placement within the approved allowlist; exact sentence construction remains subject to the fresh S90 spec review.

This was a read-only pre-step. The listed commands, regenerated projection, report edits, final parity, and fresh S90 reviewer pass have **not** yet been executed or claimed.
