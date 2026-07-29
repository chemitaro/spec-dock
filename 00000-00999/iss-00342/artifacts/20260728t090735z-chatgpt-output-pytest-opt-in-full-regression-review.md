# Conclusion

**Adopt Alternative 2: conditional policy skipping behind a pytest-native `--run-full-regression` option.**

This is the best match for the owner’s stated interface:

* Ordinary pytest commands remain natural.
* Policy-classified long tests never execute accidentally.
* A focused long-test command produces an intentional skip rather than disappearing through marker deselection.
* Full execution has one semantically explicit opt-in.
* Existing `skip`, `skipif`, module-level skips, `importorskip`, imperative `pytest.skip`, and `xfail` behavior remain untouched.

The design is established pytest practice. Pytest’s official documentation demonstrates essentially the same pattern with `pytest_addoption`, `pytest_collection_modifyitems`, a `--runslow` option, and a dynamically added skip marker when that option is absent. ([pytest][1])

This recommendation **materially differs from the currently approved design**, which selects `fast` through default `addopts`, treats explicit `-m` as the full override, and explicitly rejects adding a custom full-regression flag. Canonical requirement, design, and plan amendments with fresh review are therefore required before implementation.

Repository access succeeded. The requested `unavailable` branch could not be resolved, so the default branch `main` was inspected. On `main`:

* pytest configuration currently contains only `testpaths = ["tests"]`;
* the Makefile currently owns only `lint`;
* `Provider CI` currently triggers on both `push` and `pull_request`, preserving the `provider-tests` job identity and running bare `uv run pytest`.

## Recommended internal responsibility split

Keep the accepted `fast`/`full_regression` partition, heavy prefixes, and seven-node required-fast inventory unchanged. Change only how the partition controls execution.

### 1. Register the opt-in

`pytest_addoption` owns one boolean option:

```text
--run-full-regression
```

Its help text should state that it executes tests normally skipped by the repository’s full-regression policy. The exact option must appear in `uv run pytest --help`.

### 2. Classify before marker selection

Classify each item as it is collected, preferably through `pytest_itemcollected`, and add exactly one of:

* `pytest.mark.fast`
* `pytest.mark.full_regression`

This preserves the approved classification rules:

* both markers: collection error;
* required-fast node: `fast`;
* other heavy-prefix item: `full_regression`;
* explicit `full_regression` outside a heavy prefix: `full_regression`;
* all remaining items: `fast`;
* every collected item has exactly one lane marker.

Using `pytest_itemcollected` rather than relying on ordering between several `pytest_collection_modifyitems` implementations makes dynamic lane markers available before built-in `-m` selection. Pytest’s documented collection lifecycle invokes item-collected hooks during collection and invokes `pytest_collection_modifyitems` only after collection is complete. ([pytest][2])

### 3. Apply execution policy after classification

In `pytest_collection_modifyitems`:

* when `--run-full-regression` is present, add no policy skip;
* otherwise, add `pytest.mark.skip` to every selected `full_regression` item.

Use one stable reason, for example:

```text
full regression test; rerun with --run-full-regression
```

Do not remove, inspect away, or rewrite any existing skip or xfail marker.

### 4. Keep configuration non-selecting

The pytest configuration should retain:

* `testpaths = ["tests"]`;
* marker registration for `fast` and `full_regression`;
* strict marker validation.

It should **not** contain a default `-m fast` expression.

Marker registration and strict-marker enforcement remain appropriate; registered markers are also discoverable through pytest’s marker help. ([pytest][3])

### 5. Keep global completeness separate from focused runs

The per-item hook should validate only the items collected by the current invocation. A dedicated root-collection verifier must continue to prove:

```text
F ∩ H = ∅
F ∪ H = C
U = ∅
|H| > 0
required-fast seven nodes ⊆ F
```

A focused invocation must not fail merely because other required-fast nodes or all heavy tests were outside its requested collection.

## Why this better matches the owner intent

The current `addopts = -m fast` design is technically valid and quieter, but it models the default as **selection algebra**, not as an explicit execution policy.

Pytest constructs the command line by placing configuration `addopts` before environment and explicit command-line arguments; a later conflicting option wins. Therefore an explicit `-m full_regression` overrides a configured `-m fast`. ([pytest][1])

The conditional-skip design gives the two mechanisms separate meanings:

* `-m` chooses a subset.
* `--run-full-regression` grants permission to execute long tests.

Consequently:

* `-m full_regression` alone does not execute long tests;
* `--run-full-regression -m full_regression` does;
* a new contributor sees the special operation in `pytest --help`;
* a focused heavy node reports why it was not run.

That is a closer match to the requested “ordinary commands are safe; long tests require a special operation” contract.

Permanent `@pytest.mark.skip` is not acceptable. It would continue to suppress the test in full mode, and removing static skip markers dynamically would create an unacceptable risk of also removing legitimate skip conditions.

# Exact command contract

Let `C` be the set collected by a particular invocation, with `F` and `H` its `fast` and `full_regression` subsets.

| Purpose                       | Exact command                                                    | Required behavior                                                                                                                                  |
| ----------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Daily root run                | `uv run pytest`                                                  | Collect and classify `C`; execute runnable `F`; policy-skip `H`; any fast failure returns nonzero.                                                 |
| Daily unit run                | `uv run pytest tests/unit`                                       | Execute fast unit items; policy-skip heavy items in `test_init_update.py`; no global-inventory error.                                              |
| Daily focused long node       | `uv run pytest path/to/test.py::test_name`                       | Collect the node, classify it as `H`, do not execute its body, report the policy skip reason; intentional skip is a successful run.                |
| Execute one focused long node | `uv run pytest --run-full-regression path/to/test.py::test_name` | Do not add the policy skip; execute the node unless an existing legitimate skip condition applies.                                                 |
| Formal full suite             | `uv run pytest --run-full-regression`                            | Select the logical root collection `F ∪ H`; policy-skip set is empty; existing legitimate skips remain; any executed-test failure returns nonzero. |
| Long-only diagnostics         | `uv run pytest --run-full-regression -m full_regression`         | Select `H`; execute its runnable items; retain existing static or runtime skips.                                                                   |
| Explicit fast diagnostics     | `uv run pytest -m fast`                                          | Select and execute `F`; this is diagnostic, not the ordinary daily command.                                                                        |
| PR CI                         | `make lint`, then `uv run pytest`                                | Preserve `Provider CI` / `provider-tests`; run ordinary fast behavior; do not start a full workflow.                                               |
| `main` post-merge CI          | `uv run pytest --run-full-regression`                            | Run once in the full-regression workflow for the `main` SHA; no duplicate fast job.                                                                |
| Manual GitHub full            | `uv run pytest --run-full-regression`                            | `workflow_dispatch` uses the same full contract as `main` push.                                                                                    |

Two explicit safety rules are required:

```text
uv run pytest -m full_regression
```

must select the long lane but policy-skip it; `-m` alone is not an execution opt-in.

```text
uv run pytest --run-full-regression -m fast
```

is intentionally a narrowed fast-only diagnostic, not a formal full run. The formal full evidence must always use the exact un-narrowed root command.

The separate full workflow should retain the approved event matrix:

| Event               | Fast merge gate | Full regression |
| ------------------- | --------------: | --------------: |
| `pull_request`      |             yes |              no |
| non-`main` `push`   |              no |              no |
| `main` `push`       |              no |             yes |
| `workflow_dispatch` |              no |             yes |
| `schedule`          |              no |              no |

It must not add `continue-on-error`, permissions, secrets, credentials, or consumer-shipped workflow assets.

# Skip versus deselection

| Dimension                | Conditional policy skip                                                                                                                                                             | Default `-m fast` deselection                                                                                                                                                                                             |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discoverability          | Better. The custom option appears in help, and a focused long node has an explainable skip outcome.                                                                                 | Weaker. The item disappears from the runnable set and normally produces only a deselection count.                                                                                                                         |
| Output noise             | Worse. Roughly 2,035 heavy items would appear as skipped outcomes in the root default run, in addition to legitimate skips.                                                         | Better. Heavy items are summarized as deselected rather than as individual skipped outcomes.                                                                                                                              |
| Detailed reasons         | Available with `-rs` or `-ra`. Pytest intentionally does not show detailed skip reasons by default to avoid clutter. ([pytest][4])                                                  | No per-item reason is available because the item was deselected.                                                                                                                                                          |
| Collection cost          | Still collects and imports the requested tests before applying policy skip.                                                                                                         | Also ordinarily performs collection before marker deselection. Neither mechanism removes collection-time work or collection errors. ([pytest][2])                                                                         |
| Focused long node        | Produces a visible, intentional skip. The recommended contract treats this as exit 0.                                                                                               | The only node can be deselected, leaving no selected tests. Pytest defines exit code 5 for a no-tests-collected outcome, so this path requires exact characterization and is less natural for contributors. ([pytest][5]) |
| Accidental omission risk | The omitted lane remains visibly represented, but skips are green; a broken full workflow could still hide regressions. The full-set verifier and `main` full run remain mandatory. | Quieter but easier to overlook. A deselection count alone does not prove that the full command later restores all items.                                                                                                  |
| Explicit `-m`            | Orthogonal. It narrows the selected set but cannot grant permission to execute `H` without the flag.                                                                                | It overrides the configured marker expression when supplied later on the command line.                                                                                                                                    |
| Existing static skips    | Full mode merely stops adding the policy skip. It does not remove existing `skip`, true `skipif`, module-level skip, `importorskip`, imperative skip, or xfail behavior.            | Existing static skips are also retained, but they apply only to the selected lane.                                                                                                                                        |

The repository already has legitimate environment-dependent skipping in the required-fast CLI smoke class: it invokes `pytest.skip` on Windows or when Bash is unavailable. Full mode must leave this behavior intact.

A reporting caveat is important: do not calculate the policy-skipped count by adding terminal skip totals. An item can have both the policy skip and a legitimate skip condition but produces only one skipped outcome. Verify sets directly:

```text
default policy-skip marker set = selected H
full policy-skip marker set = ∅
existing skip/skipif/xfail definitions unchanged
```

# Make target recommendation

**Make targets are optional aliases, not required interfaces or semantic authorities.**

For the simplest owner-aligned implementation, add no pytest Make targets:

* retain the existing `make lint`;
* use `uv run pytest` directly in PR CI;
* use `uv run pytest --run-full-regression` directly in the full workflow and documentation.

This fits the current repository, whose Makefile currently contains only `lint`.

A Make alias is acceptable only if compatibility or contributor convention later justifies it. It must be a transparent one-line alias:

```text
test-provider-fast  → uv run pytest
test-provider-full  → uv run pytest --run-full-regression
```

A Make wrapper becomes undesirable if it:

* re-expresses marker algebra;
* becomes the only discoverable route to full execution;
* diverges from the command shown by `pytest --help`;
* causes local and CI full semantics to differ.

The requirement already permits a stable command equivalent to `make test-provider-full`; the pytest-native flag satisfies that requirement after amendment.

# Failure modes and minimum automated tests

| Failure mode                                                          | Minimum automated guard                                                                                                                                                                                             |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The option is not loaded from `tests/conftest.py`                     | Subprocess `uv run pytest --help`; assert the exact option and explanatory help text are present.                                                                                                                   |
| An item is unclassified or has both lane markers                      | Focused synthetic collections for unmarked, explicitly marked, conflicting, heavy-prefix, and required-fast cases; conflict must terminate collection nonzero.                                                      |
| Dynamic lane markers are added too late for `-m`                      | Subprocess matrix proving `-m fast` and `-m full_regression` see dynamically assigned markers. Classification during `pytest_itemcollected` avoids hook-order dependence.                                           |
| A heavy item executes without opt-in                                  | A controlled `H` test whose body writes a sentinel or deliberately fails; bare root and focused invocations must skip it and never execute the sentinel.                                                            |
| The focused skip is undiscoverable                                    | Run the controlled `H` node with `-rs`; assert the stable reason names `--run-full-regression`.                                                                                                                     |
| The full flag still leaves policy skips                               | Run the controlled project with the flag; assert no item contains the policy skip and both `F` and runnable `H` execute.                                                                                            |
| Full-mode failures are swallowed                                      | A failing `H` item must return the normal pytest tests-failed nonzero status under `--run-full-regression`. No workflow `continue-on-error`.                                                                        |
| `-m` bypasses the opt-in                                              | Assert `-m full_regression` alone selects but skips `H`; assert the flag plus that marker executes `H`.                                                                                                             |
| Existing skips are accidentally removed                               | Include static `skip`, true and false `skipif`, module-level/import skip where feasible, imperative `pytest.skip`, and xfail representatives. Under full mode, each must retain its ordinary outcome.               |
| Required-fast overrides regress                                       | Assert all seven exact nodes exist, are classified `F`, receive no policy skip, and pass in a focused invocation.                                                                                                   |
| Root completeness silently drifts                                     | Dedicated root collect verifier for `F ∩ H = ∅`, `F ∪ H = C`, `U = ∅`, `H > 0`, and seven-node membership.                                                                                                          |
| Collection-time heavy failures evade the skip                         | Characterization test that all heavy prefixes can be collected in the default environment without live network, credentials, or optional setup. Policy skipping cannot protect against import or collection errors. |
| Terminal skip counts are misused as set proof                         | Inspect item markers and report records directly; separately record collected, executed, policy-skipped, legitimate-skipped, deselected, xfailed, and failed sets.                                                  |
| PR/full routing drifts                                                | Deterministic workflow test for the five-event matrix, exact workflow/job identities, exact commands, no schedule, no permission/secret additions, and no duplicate fast job on full events.                        |
| Provider-only full workflow is shipped to consumers                   | Existing init/update non-shipping contract extended to the new full workflow path.                                                                                                                                  |
| Documentation still tells users that path-only heavy commands execute | Contract inspection of README and AGENTS command blocks against the canonical command table.                                                                                                                        |
| The speed claim is unsupported                                        | Same-checkout fast/full paired measurements and three PR observations remain required; default evidence must show `H` executed count is zero, not merely that elapsed time improved.                                |

The current plan’s controlled-failure, focused-collection, set-algebra, workflow-routing, non-shipping, and performance evidence remain useful; their expected selected/skipped sets must be amended rather than discarded.

## Hard-stop conditions

Implementation must not proceed to delivery if any of these occurs:

* any `H` body executes without `--run-full-regression`;
* any policy skip remains in formal full mode;
* the flag causes a legitimate existing skip or skipif to execute;
* the seven required-fast nodes stop being `F`;
* dynamic markers are invisible to explicit `-m`;
* `pytest --help` does not expose the option;
* a heavy module fails during default collection before skipping can apply;
* formal full collection differs from the root `F ∪ H` baseline without explanation;
* PR check identity changes;
* the full workflow introduces schedule, permissions, secrets, consumer shipping, or swallowed failure status.

# Required canonical amendments

## Requirement amendments

The requirement’s product-level lane policy remains valid, but the following contracts need amendment.

### BH-001 / AC-001: define default execution precisely

Replace a selection-only interpretation with:

```text
Default commands collect and classify the requested set,
execute fast items,
and policy-skip full-regression items.
```

Add the focused-long-node behavior and required skip reason.

### BH-002 / AC-002: redefine formal full

Make the canonical local full command:

```text
uv run pytest --run-full-regression
```

Define completeness as:

* root selected set equals `F ∪ H`;
* policy-skip set is empty;
* legitimate pre-existing skips remain legitimate skips;
* any executed failure is nonzero.

Avoid wording that requires every collected item to execute, because valid static skips make that impossible.

### AC-007 / CON-004: distinguish policy skip from coverage weakening

The current prohibition on broad skip must explicitly distinguish:

* **forbidden:** permanent skip, new static skipif, xfail, test deletion, or assertion weakening used to obtain speed;
* **permitted:** a reversible session-local policy skip applied exactly to `H` when the opt-in is absent and never applied in full mode.

Static skip/xfail definition deltas must remain zero unless individually justified. Policy skips need their own audited set.

### AC-008: revise measurement fields

Record separately:

* collected;
* selected;
* executed;
* policy-skipped;
* legitimately skipped;
* deselected;
* xfailed;
* failed.

The current “heavy execution count is zero” condition remains.

### External command and edge-case contracts

Add:

* `--run-full-regression`;
* focused `H` default skip behavior;
* focused `H` execution with the flag;
* long-only diagnostic command;
* `-m full_regression` alone does not opt in;
* full mode does not unskip existing conditions;
* Make aliases are optional.

## Design amendments

The approved design must be updated before code changes because it currently commits to default `-m fast`, a Make facade, and no custom full flag.

Required changes:

1. **§2.2 / §2.3:** adopt the custom pytest flag and remove the rejection of a custom flag and of this narrowly defined dynamic policy skip.
2. **DES-TL-001:** separate lane classification from execution gating; classify before marker selection and add policy skips later.
3. **DES-TL-003:** remove default `-m fast`; make bare pytest the policy-skip command and the flag the full command; make Make aliases optional.
4. **DES-TL-004:** PR workflow invokes bare pytest directly.
5. **DES-TL-005:** `main` and dispatch workflow invoke the flag directly.
6. **DES-TL-006:** revise verification from `selected=F` to `collected=C, executed=F, policy-skipped=H` in default mode; add the flag/marker/static-skip matrix.
7. **DES-TL-007:** update rollback. The safe rollback is to run PR pytest with `--run-full-regression`; there is no default `-m fast` setting to remove.
8. Update the responsibility model, failure table, command table, diagrams, docs impact, and evidence definitions accordingly.

## Plan amendments

The approved plan must be revised rather than treated as implementation-local encoding.

At minimum:

* **S00:** baseline legitimate skip/skipif/xfail behavior separately from future policy skips.
* **S01:** add option/help tests, early classification, policy-skip tests, static-skip preservation, and the `-m` matrix.
* **S02:** remove the mandatory Make-facade milestone, or merge it into S01 as an optional-alias inspection.
* **S03:** change workflow command expectations to direct pytest commands.
* **S04:** replace `bare root selected=F` with `root collected=C, executed=F, policy-skipped=H`; add focused-long default and opt-in probes.
* **S05:** require policy-skipped count zero in every full run while legitimate skips remain; do not assert that every `C` item executed.
* **S90:** update README and AGENTS. Both currently describe `uv run pytest` as the full baseline and path-only integration/CLI commands as execution commands; those long-lane examples will require the flag.
* Amend the affected AC/BH/CON closure rows, evidence keys, test cards, rollback wording, and reviewer focus.

## Contracts that do not change

No amendment is needed to these owner-approved outcomes:

* every collected item belongs to exactly one lane;
* the heavy prefixes;
* the exact seven required-fast nodes;
* `F ∩ H = ∅`, `F ∪ H = C`, `U = ∅`, `H > 0`;
* ordinary pytest and PR do not execute `H`;
* explicit local/manual/`main` full includes the logical full set;
* `Provider CI` / `provider-tests` identity;
* the event routing truth table;
* no schedule;
* no test deletion, assertion weakening, permanent speed-motivated skip, or xfail;
* full failures remain red and nonzero;
* post-merge full does not retroactively block a completed merge;
* no permission, secret, dependency, branch-protection, automatic-merge, or consumer-workflow change.

# Evidence

GitHub connector inspection was performed against `chemitaro/spec-dock` using `main` after the requested current branch was unavailable. The attached Issue documents were then reviewed as the task’s canonical planning inputs. Current repository files confirm that none of the proposed marker, flag, conftest, Make, or split-workflow changes has yet been implemented.

Web references were limited to official pytest documentation retrieved on **July 28, 2026**. They establish that:

* command-line-controlled dynamic slow-test skipping is an official example;
* collection modification occurs after item collection;
* custom markers and strict marker validation are supported;
* skip details are available through `-r`;
* no-tests-collected is exit code 5. ([pytest][1])

# Assumptions

* The prompt-provided local pytest version, 9.0.3, is authoritative for implementation testing; `pyproject.toml` itself specifies only `pytest>=8.0`.
* Official commands run from the repository root and collect tests beneath `tests/`, so `tests/conftest.py` is loaded.
* An intentional policy-skipped focused long node returning success is acceptable to the owner. A required nonzero outcome for that command would be a different interface contract.
* Heavy tests are safe to import and collect without executing live external operations.
* Formal full evidence uses the exact root command without externally injected `-k`, path restrictions, or `PYTEST_ADDOPTS` marker narrowing.
* The attached requirement, design, and plan are the intended canonical revisions even though their exact bytes were not independently established as files on the inspected `main` ref.

# Uncertainty and unverified claims

* The exact terminal verbosity of roughly 2,035 policy skips has not been measured on this repository under pytest 9.0.3. It is the principal usability cost of this recommendation.
* Whether `tests/conftest.py` exposes the custom option during `pytest --help` in the exact repository environment must be verified by subprocess test. Failure would require reconsidering plugin placement.
* The full repository-wide inventory of existing static skips, skipifs, import skips, imperative skips, and xfails was not enumerated in this review. S00 characterization remains mandatory.
* Runtime improvements are not yet demonstrated. The recommendation preserves the existing paired-performance and PR-observation obligations.
* A focused node deselected by default `-m fast` may lead to the documented no-tests exit category; the exact pytest 9.0.3 repository behavior must be characterized rather than assumed.

[1]: https://docs.pytest.org/en/stable/example/simple.html "https://docs.pytest.org/en/stable/example/simple.html"
[2]: https://docs.pytest.org/en/stable/reference/reference.html "https://docs.pytest.org/en/stable/reference/reference.html"
[3]: https://docs.pytest.org/en/latest/how-to/mark.html "https://docs.pytest.org/en/latest/how-to/mark.html"
[4]: https://docs.pytest.org/en/stable/how-to/skipping.html "https://docs.pytest.org/en/stable/how-to/skipping.html"
[5]: https://docs.pytest.org/en/stable/reference/exit-codes.html "https://docs.pytest.org/en/stable/reference/exit-codes.html"
