## S01 execution brief

The connector-confirmed branch is `iss-00346-integration-distribution-and-final-quality` at remote HEAD `75ba8f1fdec2b9cee5624dbdd2741614b4755778`. The report’s existing S01 wheel receipt is instead bound to `3d5b0ad6f675f79b8b9c3a569091c327b8bb2295`; the current HEAD is a subsequent report-only commit. Under `I346-AC-001` and the stale-evidence rule, the earlier wheel, digest, origin, and fresh-consumer results cannot close the current cycle without being rebuilt and rerun against `75ba8f…`.

The branch already contains the four S01 integration tests. Therefore, the attached “before implementation” framing is temporally stale: use this brief to **rebind and minimally complete the existing test-only implementation**, not to create a second harness or manufacture a package defect. 

Execution must use one exact candidate wheel from one clean build. The wheel inspected, hashed, installed, and exercised by the fresh consumer must be the same file. Do not inspect a `dist/` wheel and then silently install a separately built fixture wheel unless their identity is explicitly reconciled by digest.

The current package surfaces already declare the four hidden Workbench README assets, package-wide assets, defensive exclusions, and build-time stale-output pruning. The installer copies the root Workbench README only for a fresh installation. No package repair is justified by connector inspection alone.

The smallest justified code delta is confined to `tests/integration/test_epic_00343_distribution.py`:

* Exercise the **denylist branch** with one injected forbidden entry, because the existing controlled inventory negative only removes a required README.
* Run the wheel-projected runtime’s `validate` command at the end of `tc-346-s01-004`, because the current test stops after byte/source assertions while the canonical test card explicitly includes validation.

Keep this as one bounded test-only completion. Change `pyproject.toml`, `setup.py`, `src/spec_dock/cli.py`, or templates only after a fresh actual-wheel failure identifies the responsible package or installer surface. The allowed and forbidden boundaries remain those in plan §8.3.

## Required test cards

1. **`tc-346-s01-001` — candidate revision and clean wheel receipt**

   * **Precondition:** Local branch is exactly `iss-00346-integration-distribution-and-final-quality`; local and remote HEAD both equal `75ba8f1fdec2b9cee5624dbdd2741614b4755778`; working tree is clean; previous `dist/` and `build/` outputs are excluded or removed.
   * **Action:** Record repository, branch, candidate HEAD, clean state, and build command; perform the clean build; deterministically select exactly one wheel; record its basename, package version, SHA-256 distribution digest, and sorted inventory; reread HEAD and status after the build.
   * **Expected result:** Pre/post HEADs equal the expected candidate revision; pre/post status is clean; exactly one candidate wheel is selected; wheel version equals `pyproject.toml`; the recorded digest recomputes identically.
   * **Negative/control:** A non-empty pre-build status, pre/post HEAD mismatch, unexpected branch, multiple-wheel ambiguity, or installed wheel whose digest differs from the inspected wheel must reject the receipt. Do not move the real branch merely to create a negative; test the receipt/assertion helper with a synthetic mismatch.

2. **`tc-346-s01-002` — wheel inventory allowlist and denylist**

   * **Precondition:** The exact wheel selected by `tc-346-s01-001` is available as a ZIP inventory, preferably including `ZipInfo` metadata rather than filenames alone.
   * **Action:** Assert the exact template README set:

     * `README.md`
     * `root/.workbench/README.md`
     * `initiative/.workbench/README.md`
     * `epic/.workbench/README.md`
     * `issue/.workbench/README.md`

     Retain required runtime/docs checks. Reject stale wrapper-era paths, `current/`, `completed/`, non-allowlisted nested README files, Python caches/bytecode, nested archives, absolute or `..` entry paths, and—where metadata is inspected—symlink-like or unjustified executable entries. The approved design explicitly includes nested archive and unsafe-entry inspection.
   * **Expected result:** The actual wheel contains all required entries, exactly the five allowed template README files, and no denied entry.
   * **Negative/control:** Both controls must fail:

     * Remove `issue/.workbench/README.md` from a synthesized inventory.
     * Add one forbidden entry such as `spec_dock/assets/spec_dock/templates/issue/legacy/README.md` or a `__pycache__/probe.pyc` entry.

     Failure messages should distinguish missing-required, README-allowlist, and denied-entry cases.

3. **`tc-346-s01-003` — isolated installation and origin proof**

   * **Precondition:** Empty isolated virtual environment and isolated working directory; no editable install; no source checkout in `PYTHONPATH`, current working directory, or effective import path.
   * **Action:** Install the exact candidate wheel; inspect the `spec-dock` console entrypoint, `spec_dock.__file__`, packaged assets location, package version, and relevant `sys.path` classification.
   * **Expected result:** Console entrypoint resolves inside the isolated environment; module and assets resolve from installed package storage; the repository source tree is absent from the effective runtime path; installed version equals the candidate wheel version.
   * **Negative/control:** Add the checkout’s `src/` directory to a controlled probe’s `PYTHONPATH`. The origin assertion must detect and reject the resulting source-tree import. Store only classification booleans in tracked evidence, not host-local absolute paths. The current implementation already contains this source-fallback control.

4. **`tc-346-s01-004` — fresh Workbench shell and opaque import tracer**

   * **Precondition:** Fresh temporary Git repository; the exact S01 wheel installed; public top-level installer and wheel-projected runtime available.
   * **Action:** Run fresh `spec-dock init`; create Initiative, Epic, and Issue through the projected runtime; compare root and node `.workbench/README.md` files with their corresponding provider templates; verify the Workbench ignore rule with `git check-ignore`; create a harmless binary/NUL-bearing opaque file inside the Issue Workbench; import it through `artifact import file --issue … --json`; then run the installed projected runtime’s `validate`.
   * **Expected result:** All four scopes have the tracked README shell; the opaque payload is ignored; the source remains present and byte-identical; destination bytes equal source bytes; result has `canonical=false` and the correct target; validation succeeds; stdout/stderr contains no temporary-repository absolute path or body sentinel.
   * **Negative/control:** Any tracked payload, missing/wrong README, source mutation, destination mismatch, absolute-path leak, unexpected canonical promotion, or validation failure makes the card fail. Use harmless sentinels only; do not record body, user-file digest, or byte count.

## Minimal execution order

1. Resolve branch, local HEAD, remote HEAD, and clean state. Stop unless the cycle is bound to `75ba8f1fdec2b9cee5624dbdd2741614b4755778`; if the branch moves, discard this binding and restart from the new exact HEAD.
2. Inventory existing changes. Treat `tests/integration/test_epic_00343_distribution.py` as the existing S01 implementation and avoid duplicate helpers.
3. Apply only the bounded test completion: one denylist-injection control in `tc-346-s01-002` and installed-runtime `validate` in `tc-346-s01-004`.
4. Produce one clean candidate wheel. Select it without a wildcard ambiguity and preserve its basename, version, digest, and sorted inventory in the in-memory/test receipt.
5. Install that same wheel into an empty environment and complete module/console origin proof before creating a consumer.
6. Run the fresh consumer tracer with the same environment and wheel; retain only content-free pass/fail evidence.
7. Run focused verification:

```bash
uv run pytest tests/integration/test_epic_00343_distribution.py \
  --run-full-regression -q

uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py \
  -k 'workbench or readme' --run-full-regression

uv run pytest tests/unit/infra/test_init_update.py \
  -k 'issue_69 or workbench_readme_distribution or workbench_readme_build_prune or isolated_wheel_install_runs_init_update' \
  --run-full-regression -q

uv run ruff check tests/integration/test_epic_00343_distribution.py
git diff --check
```

8. If the actual wheel and tracer pass after the controlled negatives demonstrate sensitivity, classify production behavior as `covered-existing`; do not create a production failure or modify package files.
9. Refresh the S01 report receipt against the current candidate revision. The receipt must include wheel basename, version, distribution digest, inventory result, installed-origin classification, exact test nodes/results, and changed-path classification—not only HEAD and clean status.
10. Commit and push any bounded test-only completion before the required current-head code-review gate. S02 remains blocked until S01 review has zero unresolved blockers, as required by plan §8.6.

## Evidence and stop conditions

Required evidence is:

* Repository, branch, exact candidate revision, pre/post clean state, and local/remote equality.
* Build command and uniquely selected wheel basename.
* Package version and candidate-wheel SHA-256. The distribution digest is permitted provenance; it is distinct from a user-imported file digest.
* Exact five-README allowlist result, required runtime/docs result, denylist result, and both controlled inventory negatives.
* Console/module/assets origin classifications, including successful detection of the checkout-injection control.
* Fresh root/Initiative/Epic/Issue shell matrix and provider-template equality.
* Workbench payload ignored state.
* Generic import result, source-preserved boolean, destination-byte-match boolean, `canonical=false`, path-leak scan, and installed validation result.
* Exact focused commands, exit status, concise counts, changed files, and production-repair disposition.
* Current-head reviewer result. The prior report’s `3d5b0ad…` pass claims are historical inputs, not current-cycle closure evidence.

Stop immediately when any of the following occurs:

* Branch or HEAD changes during build, installation, test, or review.
* Local and remote HEAD differ, or unrelated dirty state prevents attribution.
* More than one wheel can qualify as the candidate, or the installed wheel cannot be proven identical to the inspected wheel.
* A required package entry is absent, a denied entry is present, or unsafe ZIP metadata cannot be classified.
* Module, console, assets, or runtime resolution touches the source checkout.
* The fresh consumer requires a new public command/API or changes to Issue 344/345 contracts.
* A package repair needs a path outside plan §8.3 or changes the package version/release process.
* The generic import exposes an absolute source path, body, user-file digest, byte count, or other content-derived value.
* `validate` fails after the import.
* A requirement/design/plan/ADR conflict is found; do not resolve it with an Issue-local implementation.
* The current-head review is unavailable, stale, or has an unresolved blocker.

If the actual wheel fails, route only the demonstrated root cause:

* Missing hidden README or package-data omission: smallest `pyproject.toml`/`setup.py` repair.
* Stale entry surviving the build: smallest exclusion/pruning repair.
* Fresh root shell missing despite correct wheel inventory: smallest installer/template repair.
* Test oracle or fixture defect: test-only repair.

Every package or production repair changes HEAD and therefore invalidates the wheel, origin, and fresh-consumer evidence; restart S01 from the build boundary.

## Assumptions and uncertainty

* GitHub connector inspection verifies the remote branch and remote HEAD. It does not verify the implementer’s local working-tree cleanliness or rerun the reported tests.
* The current report states that S01 passed at `3d5b0ad…`, but those observations have not been independently reproduced here and are stale for the current `75ba8f…` cycle. The current HEAD appears to differ only by report content, so an identical wheel digest is plausible, but that is an inference—not a substitute for a fresh build receipt.
* The approved design’s fresh-consumer boundary names both `validate` and `sync --no-github`, while plan card `tc-346-s01-004` explicitly names `validate` but not `sync`. For this bounded S01 packet, `validate` is required; do not silently add `sync --no-github` to S01 or claim it complete here without orchestrator clarification. `sync --no-github` remains covered by later lifecycle/final gates.
* The current inventory assertion consumes filename strings. Full proof of the design’s symlink-like metadata and unexpected executable-entry checks may require a small test-only `ZipInfo` inspection. Until that is present or explicitly dispositioned, do not overstate metadata-level wheel safety.
* Formal review evidence may identify only the supported current `Pro` browser selection. No `Cheetah` execution claim is supported by the task brief or current wrapper contract. 
