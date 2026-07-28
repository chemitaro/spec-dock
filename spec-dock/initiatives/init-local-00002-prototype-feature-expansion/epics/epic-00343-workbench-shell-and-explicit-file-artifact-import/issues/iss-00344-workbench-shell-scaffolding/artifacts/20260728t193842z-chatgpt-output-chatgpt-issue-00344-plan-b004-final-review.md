# Issue 344 Final Plan Review

## Source Verification (repo, branch, exact commit, files)

| Item                                     | Verified result                                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository                               | `chemitaro/spec-dock`                                                                                                                             |
| Branch                                   | `iss-00344-workbench-shell-scaffolding`                                                                                                           |
| Required commit                          | `995c12cd6fb25b026d48e1ecb2e35781bac2304b`                                                                                                        |
| Branch/commit relation                   | GitHub connector comparison returned `identical`, with `ahead_by=0` and `behind_by=0`; the branch head is the required commit                     |
| Commit subject                           | `docs(iss-00344): 計画スキーマ最終レビュー指摘を反映`                                                                                                              |
| Issue files read at the exact commit     | `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`                                                                          |
| Parent Epic files read                   | `requirement.md`, `design.md`, `plan.md`                                                                                                          |
| Authoring/workflow rules read            | `spec-dock/docs/workflow_issue.md`, `spec-dock/docs/authoring/issue-plan.md`, `spec-dock/docs/phase_plan_issue.md`                                |
| Relevant implementation/build files read | `src/spec_dock/cli.py`, `template_scaffolder.py`, `application/workbench.py`, `infra/fs_cli.py`, `infra/fs_repo.py`, `setup.py`, `pyproject.toml` |
| Relevant tests read                      | `test_init_update.py`, `test_runtime_fs_repo_workbench_opacity.py`, `test_runtime_new_doc_s09.py`, `test_workbench.py`                            |

The canonical Issue plan at this revision is blob `3f96c08a67df92390f8863b365494d19bdaf769f`; the requirement and design are blobs `d28e39489e32a42b7438cb3fa763abeb857cd7ff` and `fc0d6060417472890ca2d01250d6fef7c8485355`.

This was a read-only specification-plan review. The proposed future test commands were inspected against the current source and test seams, but not executed.

## Verdict (PASS or FAIL)

**FAIL**

Prior finding **B-004 is resolved**: S99 no longer requires the final commit SHA to be written into the commit that creates that SHA. The plan now finalizes the report ledger before the mandatory final evidence commit, observes `git rev-parse HEAD` and `git status --short` afterward, and records the resulting SHA and clean state only in declared external delivery evidence. It also explicitly forbids treating EVD-009 or EVD-010 as post-commit SHA storage.

However, two remaining blocking defects prevent the plan from being executable without material interpretation:

1. S90 combines creation of a Python test with docs-only ownership and review.
2. The no-backfill closure does not cover all triggers explicitly required by `I344-RQ-005`.

## Blocking Findings

### B-005 — S90 has an invalid mixed ownership and reviewer contract

**Finding**

S90 is described and gated as a docs-only slice:

* delegated role: `doc-writer`;
* reviewer: `spec-reviewer`;
* allowed paths include shipped documentation and “docs assertions”;
* Green verification requires a new Python test named `TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary`.
* Its concrete test card again names that Python test as the verification implementation, while the S90 gate requires only a fresh `spec-reviewer`.

That test is not present at the reviewed commit, so S90 is planning to create or materially modify Python test code, not merely execute an existing docs assertion.

The repository workflow assigns runtime/code/tests/scaffold behavior to `dev-coder` and requires `code-reviewer` coverage. It assigns shipped-doc changes to `doc-writer` and docs/spec review to `spec-reviewer`. Where a step contains both classes of change, the workflow requires the step to be split or to identify both reviewer focuses; final issue-wide review is not a replacement for the per-step gate.

**Impact**

The executor must decide, without a plan-level answer:

* whether the `doc-writer` may edit `tests/unit/infra/test_init_update.py`;
* whether the test belongs to S03, S90, or a separate substep;
* whether a per-step `code-reviewer` is required;
* which milestone commit owns the test.

That is a material implementation and governance interpretation, and it conflicts with the plan’s stated ownership boundaries.

**Required correction**

Choose one explicit structure:

1. **Preferred:** move creation of `test_shipped_docs_describe_workbench_readme_boundary` into an earlier `dev-coder` step with a fresh `code-reviewer`; S90 then changes documentation only and runs the already-present assertion before its `spec-reviewer` gate.
2. Split S90 into:

   * a test-contract substep owned by `dev-coder` and reviewed by `code-reviewer`;
   * a docs substep owned by `doc-writer` and reviewed by `spec-reviewer`.
3. Less preferably, define dual delegation, exact allowed paths, and both per-step reviewer gates inside S90.

The closure owner, commit candidate, and EVD-008 recording sequence must be updated accordingly.

### B-006 — `I344-RQ-005` no-backfill triggers are not fully represented in closure evidence

**Finding**

`I344-RQ-005` explicitly prohibits backfill or mutation from all of the following:

* update;
* existing-workspace init/update;
* validate;
* sync;
* active switching;
* Artifact creation;
* ADR creation;
* future child creation outside the new child.

It also requires preservation of existing Workbench entries, bytes, names, and mtimes.

The plan’s locked no-backfill row covers only an existing Workbench observed around `init/update/new child`.  Its concrete S01 negative test likewise executes only update, existing `init --force`, and new-child creation.

S02 invokes validate, sync, dependency, and active-context seams, but its locked expectation is semantic-opacity equivalence rather than a before/after Workbench preservation snapshot. It does not close the bytes/names/mtime no-backfill contract, and Artifact/ADR creation is not included in that card.

**Impact**

The plan can presently mark `TC-344-005` and therefore `AC-344-005` closed without observed evidence for several expressly enumerated mutation triggers. The executor or reviewer would need to infer that unrelated existing tests are sufficient, but the plan neither names those tests nor defines the required before/after observation.

This is a closure-coverage gap, not merely a request for extra test volume.

**Required correction**

Extend `TC-344-005` and its step-local test cards so that the locked observation includes:

* existing root and representative existing Initiative/Epic/Issue Workbenches;
* before/after entry inventory, file bytes, names, and mtimes;
* `validate`;
* `sync`;
* active switching;
* Artifact creation;
* ADR creation;
* existing init/update;
* future child creation with ancestor/sibling preservation.

The plan must name the exact test node or command sequence that produces this evidence. Existing characterization tests may be reused, but their identifiers and the preservation observations must be explicitly mapped to `TC-344-005` and EVD-001/EVD-002.

## Non-blocking Findings

No additional non-blocking plan defect is recorded.

The current `report.md` still identifies the plan gate as failed with B-004 corrected and re-review pending, and `.assurance.json` remains provisional. Those are expected lifecycle states at the reviewed revision rather than independent plan defects; they must not be promoted until the blocking findings above are corrected and freshly reviewed.

## Closure Review

| Review area                              | Result                           | Assessment                                                                                                                                                                                                                                                                              |
| ---------------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact source binding                     | **PASS**                         | Exact repository, branch, and commit were verified through the connected GitHub source.                                                                                                                                                                                                 |
| B-004 self-reference repair              | **PASS**                         | Report ledger, final commit scope, external destination, and ready/blocked are fixed before commit; SHA and clean result are observed afterward and remain external.                                                                                                                    |
| EVD identities                           | **PASS**                         | EVD-009 remains review findings/adoption/fix/fresh verdict; EVD-010 remains dependency/deferred-delivery handoff. Neither is repurposed as SHA storage.                                                                                                                                 |
| Requirement/design trace                 | **FAIL**                         | Most requirements map cleanly, but the explicit `I344-RQ-005` trigger set is not fully closed by a concrete preservation test.                                                                                                                                                          |
| Vertical slicing                         | **PASS**                         | S01 shell generation, S02 opacity/copy compatibility, S03 distribution, S90 docs, and S99 final quality follow the approved provider-first dependency direction.                                                                                                                        |
| Step-local planned contracts             | **PASS with blocking exception** | S01, S02, S03, and S99 contain scope, obligations, Red/alternative evidence, Green verification, guardrails, evidence destinations, and amendment triggers. S90’s mixed docs/test ownership is invalid.                                                                                 |
| Concrete test cards                      | **FAIL**                         | Cards are generally concrete and observable, but `TC-344-005` omits required triggers and S90 assigns a new Python test to a docs-only worker/gate.                                                                                                                                     |
| Distribution/build executability         | **PASS**                         | The current `setup.py` has the active custom `build_py` seed, pre-prune snapshot, and post-build prune seam planned by S03.  The current test suite also contains the reusable local-wheelhouse `python -m build --wheel --sdist --no-isolation` infrastructure referenced by the plan. |
| Exact five-path contract                 | **PASS**                         | Plan and design consistently require `templates/README.md` plus the four hidden Workbench README assets, while retaining removal of stale non-allowlisted nested README files.                                                                                                          |
| Current Red seams                        | **PASS**                         | Current installer cleanup broadly removes nested template READMEs, and the generic scaffolder rewrites unchanged UTF-8 through text I/O, so the planned Red cases correspond to real implementation seams.                                                                              |
| Copy/discovery boundary                  | **PASS**                         | Production copy/discovery files are correctly treated as read/verify-only; existing source-wins, byte-copy, safety, and `.workbench` discovery exclusion seams exist.                                                                                                                   |
| Dependency and sibling ownership         | **PASS**                         | Issue 344 owns focused shell evidence; Issue 345 owns generic import; Issue 346 owns consumer E2E, dogfood, full regression, Epic-wide review, and PR delivery.                                                                                                                         |
| Human-only delivery boundary             | **PASS**                         | Per-Issue PR, merge preparation, and Issue finish are excluded; S99 stops at Issue 346 handoff. Parent Epic retains human-only merge and final delivery in Issue 346.                                                                                                                   |
| Overall execution without interpretation | **FAIL**                         | B-005 and B-006 require plan-author decisions before a worker can execute and close the plan correctly.                                                                                                                                                                                 |

## Recommendation

Do **not** promote this plan to execution-ready at commit `995c12cd6fb25b026d48e1ecb2e35781bac2304b`.

Revise the plan to:

1. give the S90 Python assertion an explicit `dev-coder` owner and per-step `code-reviewer`, preferably by moving or splitting that work from the docs-only step;
2. extend `TC-344-005` with exact before/after preservation evidence for validate, sync, active switching, Artifact creation, ADR creation, existing init/update, and future child creation;
3. update the Evidence Adoption Ledger and Spec Authoring Gate with the dispositions;
4. preserve the corrected S99 sequence and EVD-009/EVD-010 meanings unchanged;
5. run a fresh final plan review and fresh `spec-reviewer` gate against the resulting exact commit.

The plan should be promoted only after both blocking findings are closed and the fresh review returns zero blocking findings.
