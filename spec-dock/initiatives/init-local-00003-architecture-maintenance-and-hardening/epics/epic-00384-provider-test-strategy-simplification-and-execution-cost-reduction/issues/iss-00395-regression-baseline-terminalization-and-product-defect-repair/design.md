---

kind: "corrected-design"
issue: "iss-00395"
title: "Issue #395 LunaMax-ready Design"
generated_at: "2026-09-16"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
elaboration_input_sha: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
elaboration_input_tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
support_history_sha: "c0736434503117d5d468d1438fb18da16d382a56"
support_history_tree: "cec02ce70fbcbbbac811a04106dcc15540ad4d09"
implementation_allowed: true
owner_decisions_required: []
human_merge_only: true
authority: "advisory-corrected-design"
---

# Issue #395 LunaMax-ready Design

## 1. Status and authority

This document is a corrected implementation design for Issue #395. It does not grant permission to modify policy, workflows, Git history, pull requests, or Issue state. Following the prior specification-review cycle and the user's explicit dispatch, the current `implementation_allowed` value is `true`.

Before the first mutation, the executor must still verify all of the following for one clean pushed specification tip:

1. the canonical Issue Requirement, Design, Plan, LunaMax handoff, human guide, and manifest;
2. exact local `HEAD`, configured upstream, and remote Issue-branch equality;
3. an independent specification review bound to that exact SHA and tree with `review_status=pass`, P0=0, P1=0;
4. an explicit execution packet with `implementation_authorized=true` and an identified concurrent-writer absence assertion.

`owner_decisions_required=[]` means the Product design has no unresolved owner choice. It does not mean implementation, commit, push, PR preparation, or merge is authorized.

## 2. Immutable upstream contracts

The corrected design preserves these parent and Issue boundaries without reinterpretation.

| Contract       | Preserved rule                                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Delivery order | `#392 -> #395 -> #396 -> one human Epic merge to main`                                                                          |
| P392           | Exact Product/test/ledger entry point; not B1, not Issue #392 acceptance, not implementation permission                         |
| Issue #395     | Restore the accepted behavior represented by rows 1 and 3–15 and terminalize them as normal pass                                |
| Issue #396     | Sole writer of `E384-QUAL-001` implementation, policy retirement, required-context transition, and final gate                   |
| Ledger target  | 15 total, 0 active, 15 resolved, 14 `fixed-in-place`, 1 `superseded`, approved 0, unexpected 0                                  |
| Lifecycle      | Issue #392 lifecycle, wire, schema, migration, uninstall, recovery, coordination, and protected-data semantics remain read-only |
| Merge          | Human only; no direct push to the integration branch; no agent merge or revert                                                  |
| Permission     | `implementation_allowed=true` after the reviewed user dispatch; exact identity and writer checks remain mandatory              |

The integration branch remains `codex/epic-00384-provider-test-strategy-planning`. The Issue branch remains `iss-00395-regression-baseline-terminalization-and-product-defect-repair`.

## 3. Verified entry architecture

### 3.1 Repository identities

| Role                     | SHA                                        | Tree                                       | Meaning                                                                     |
| ------------------------ | ------------------------------------------ | ------------------------------------------ | --------------------------------------------------------------------------- |
| P392 Product entry       | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3` | `190bc566a18cd84813c4b7c043f8724e275cb55d` | Human-merged #392 Product/test/ledger baseline                              |
| Elaboration input        | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9` | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599` | Exact Issue-branch tip reviewed in this readiness analysis                  |
| Support-history checkpoint | `c0736434503117d5d468d1438fb18da16d382a56` | `cec02ce70fbcbbbac811a04106dcc15540ad4d09` | Exact 16 existing support artifacts; immutable, non-authoritative history |
| Specification freeze     | Runtime value                              | Runtime value                              | Future clean pushed canonical six-file specification pack                   |
| Implementation candidate | Runtime value                              | Runtime value                              | Future clean pushed Product/test/ledger candidate, if separately authorized |
| Post-merge B1/B2 tip     | Runtime value                              | Runtime value                              | Future human-merged integration tip                                         |

No future SHA or tree is predeclared in tracked content. Every future identity is supplied and then verified at the corresponding gate.

### 3.2 Baseline semantics

The P392 historical ledger contains 15 rows. Row 2 is `resolved/superseded`; rows 1 and 3–15 are active. The current root ledger retains the same rows and, after the approved U05 transition, is terminalized as 15 resolved / 0 active / 14 `fixed-in-place` / 1 `superseded`. The root timing file contains 243 node weights. The current full-regression evaluator has these relevant rules:

* active row: the historical node executes exactly once and fails normally with the historical signature;
* resolved/fixed-in-place row: the historical node executes exactly once and passes normally;
* resolved/superseded row: the successor executes exactly once and passes normally;
* any other failure or error: unexpected violation.

`tests/integration/test_issue_392_acceptance.py::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged` is a historical boundary witness for the P392 entry, not a current-root-ledger assertion. Its existing baseline assertions continue to read the immutable `full-regression-ledger.json` blob at P392 entry SHA `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`. This preserves the 15-row/14-active/1-resolved baseline while the current root ledger is later terminalized by Issue #395. The test keeps its baseline, timing, required-fast, policy, workflow, and boundary assertions unchanged; only the three Issue #395 canonical-document SHA expectations are synchronized.

Therefore the safe transition order is fixed:

```text
entry baseline observation
  -> each historical row's first RED
  -> test-harness repairs
  -> Product row 3 repair
  -> row 12 no-edit guard
  -> all 14 historical nodes + row 2 successor normal-pass proof
  -> complete dogfood projection and protection proof
  -> atomic ledger transition
  -> current full verifier GREEN
  -> exact clean candidate freeze and full rerun
  -> independent implementation review
  -> human PR merge
  -> same-tip B1, then B2
```

### 3.3 Specification admission/history design

The specification freeze is modeled as three separate history segments rather than one combined allowlist:

```text
P392
  └─ exact two receipt documents
      ↓
Elaboration input
  └─ six primary specification paths + sixteen existing support-history paths
      ↓
Support-history checkpoint c0736434503117d5d468d1438fb18da16d382a56
  ├─ sixteen support tree entries are immutable and non-authoritative
  └─ six primary paths remain the only current specification surface
      ↓
Reviewed specification freeze
  └─ only the six primary paths may change
```

The six primary paths are the Issue Requirement, Design, Plan, LunaMax handoff, human guide, and ChatGPT spec-pack manifest. The sixteen support-history paths are the exact paths listed by the Requirement. They are preserved as history only: they cannot provide current permission, owner decisions, implementation input, or a replacement authority for the canonical R/D/P.

The B5 design must prove, for every support-history path, equality of path, mode, object type, and Git object ID between the checkpoint and the reviewed specification freeze. A same-content copy, rename, recompressed ZIP, directory-prefix match, or manifest-only declaration is not equivalent. This governance correction does not alter Product behavior, Row 3's credential/no-secret/publication guarantees, lifecycle, policy, protected-data, timing, workflow, or the Row 12 no-edit boundary.

Changing the ledger before the normal-pass proof is forbidden. Treating working-tree verifier output as exact candidate identity is forbidden.

## 4. Test-lane contract

`tests/conftest.py` classifies all `tests/cli_runtime/` and `tests/integration/` nodes as full-regression tests, except the four exact required-fast nodes. Without `--run-full-regression`, those heavy tests are skipped.

This design therefore fixes the lane contract:

1. `uv run pytest` is the ordinary lane. Its current policy skips are intentional and must remain unchanged.

2. Every command that directly selects a path or node under `tests/cli_runtime/` or `tests/integration/` must include both:

   ```text
   --run-full-regression --full-regression-shard
   ```

3. The standalone current full verifier owns full collection, deterministic four-shard partitioning, coverage verification, and evaluator execution. It receives a private `--artifact-dir` for every run.

4. A selected heavy node is accepted only when pytest reports a normal pass. Exit 0 with `skipped`, `xfailed`, or no execution is not GREEN.

This contract applies to first RED, focused GREEN, dogfood parity, exact clean reruns, and post-merge B1.

## 5. Ownership and exact write surfaces

### 5.1 Product row 3

Only these existing symbols in the provider source may be edited:

| Path                                                                        | Symbol                               | Target responsibility                                                                                                                                                           |
| --------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` | `_parse_github_repo_slug`            | Parse read-only GitHub repository identity, including credential-bearing HTTPS fetch URLs, without returning or logging credentials                                             |
| same                                                                        | `origin_github_repo_slug`            | Read only the fetch origin and return normalized owner/repo identity                                                                                                            |
| same                                                                        | `origin_github_publication_endpoint` | Enforce publication policy: reject userinfo in fetch or push URL, require both URLs to be GitHub repository URLs, require exact slug equality, and return the accepted push URL |

The signatures and behavior of `_remote_get_url`, `_remote_has_userinfo`, `_redact_remote_url`, `GitGateway.origin_github_repo_slug`, bootstrap adapter bindings, and application consumers remain unchanged.

The Product edit must not weaken:

* same-repository canonical URL validation;
* numeric-target current-repository scope requirements;
* foreign repository rejection;
* publication userinfo rejection;
* fetch/push repository equality;
* credential non-exposure in stdout, stderr, exception text, or evidence.

### 5.2 Rows 4–11 test fixture

Only `tests/cli_runtime/test_runtime_import_s10.py::_StubTemplateScaffolder` is changed.

The test double gains the current descriptor-bound port method:

```python
def copy_scaffolded_tree_at(
    self,
    src_dir: Path,
    dest_dir: Path,
    dest_dir_fd: int,
    replacements: dict[str, str],
) -> list[Path]:
```

It records the event exactly once and delegates all four arguments to `spec_dock_runtime.infra.template_scaffolder.copy_scaffolded_tree_at`. It does not implement a second pathname writer. The existing legacy method remains only for unrelated test compatibility. Production `application.create_node.execute_create_plan`, `application.ports.TemplateScaffolder`, and `infra.template_scaffolder` are read-only.

### 5.3 Rows 1, 13, 14, and 15 observers

Only obsolete observer arguments are removed:

| Row | Path                                  | Before                                 | After                       |
| --: | ------------------------------------- | -------------------------------------- | --------------------------- |
|   1 | `tests/cli_runtime/test_delete.py`    | `active set --id iss-00058 --force`    | `active set --id iss-00058` |
|  13 | `tests/cli_runtime/test_sync.py`      | `active set iss-00003 --force`         | `active set iss-00003`      |
|  14 | `tests/cli_runtime/test_sync.py`      | `active set 305 --force --no-checkout` | `active set 305`            |
|  15 | `tests/cli_runtime/test_workbench.py` | `active set --id scope_id --force`     | `active set --id scope_id`  |

Row 15 additionally checks the active command return code before reading generated state. No delete, sync, tree, PUML, ready-board, active-field, or Workbench opacity assertion is removed or weakened.

### 5.4 Row 3 observer strengthening

The existing row 3 node remains the same node. It adds assertions that combined stdout/stderr contains neither the synthetic credential token nor the credential-bearing remote URL, while preserving the existing successful import assertion. It does not add a ledger row.

### 5.5 Row 12 no-edit boundary

The accepted current dependency direction is:

```text
commands/new.py
  -> application/contracts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
     -> domain/artifacts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
```

The provider source blobs and AST import edges are guarded before edits and again on the exact clean candidate. When they match the verified input, there is no Product or test edit for row 12. The row is resolved through normal-pass observation and the atomic ledger transition only.

### 5.6 Generated dogfood projection

After provider source GREEN, the current lifecycle command projects one complete candidate. These files are generated, never hand-edited:

* `spec-dock/scripts/spec_dock_runtime/infra/git_cli.py`
* `spec-dock/spec-dock.version`
* `.agents/skills/spec-dock/.spec-dock-provider-slot.json`
* `.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json`

The runtime mirror must be byte-equal to provider source. The ready record and both slot markers must share one lowercase 64-hex candidate digest that differs from the pre-projection digest. Version remains `0.2.4`, record state remains `ready`, operation remains `null`, seed policy remains `preserve-only`, and fixed slot names remain unchanged.

### 5.7 Ledger write surface

Only `full-regression-ledger.json` changes. The immutable before payload is read from `921bf7512c72bfa2887673cb7ec9bc512cec6ff3:full-regression-ledger.json`; the after payload is the current root ledger. For rows 1 and 3–15, the only semantic changes are:

```json
{
  "lifecycle": "active"
}
```

to:

```json
{
  "lifecycle": "resolved",
  "resolution_mode": "fixed-in-place"
}
```

Every other field in those rows, the complete row 2 object, row order, and all top-level historical fields must be identical to the P392 before payload. A current root ledger that is already terminalized is never used as a substitute for the immutable historical before payload.

### 5.8 Expected implementation file set

The exact expected tracked implementation diff contains 13 files:

```text
full-regression-ledger.json
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
spec-dock/scripts/spec_dock_runtime/infra/git_cli.py
spec-dock/spec-dock.version
.agents/skills/spec-dock/.spec-dock-provider-slot.json
.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json
tests/cli_runtime/test_delete.py
tests/cli_runtime/test_import.py
tests/cli_runtime/test_runtime_import_s10.py
tests/cli_runtime/test_sync.py
tests/cli_runtime/test_workbench.py
tests/unit/test_provider_test_lanes.py
tests/integration/test_issue_392_acceptance.py
```

A missing expected file means the candidate was not completely projected or corrected. An extra file means scope drift. Either condition stops the execution.

## 6. Exact row acceptance design

| Row | Historical node                                                                                                                                  | Repair surface            | First RED contract                                                                     | GREEN contract                                                                               |
| --: | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
|   1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active`                           | Test observer             | Individual node fails because retired active argument is rejected                      | Normal pass with deleted metadata still absent after validate, sync, and active observation  |
|   3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote`                    | Product + observer        | Individual node fails because read-only current repository identity cannot be resolved | Normal pass, same-repo import accepted, no credential material emitted                       |
|   4 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression`                                            | Test double               | Individual node fails for absent `copy_scaffolded_tree_at`                             | Normal pass; accepted existing parent fallback remains intact                                |
|   5 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression`                                 | Test double               | Same missing current port                                                              | Normal pass; two active-manifest observations and current chain preserved                    |
|   6 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | Test double               | Same missing current port                                                              | Normal pass; parent is resolved twice and second parent is used under lock                   |
|   7 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | Test double               | Same missing current port                                                              | Normal pass; current repo slug reaches GitHub read and stored linkage                        |
|   8 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present`     | Test double               | Same missing current port                                                              | Normal pass; explicit target slug and same-repo validation remain                            |
|   9 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression`                | Test double               | Same missing current port                                                              | Normal pass; artifact path, name, content, and projections remain                            |
|  10 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression`                             | Test double               | Same missing current port                                                              | Normal pass; sync failure remains visible and committed import survives                      |
|  11 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam`                                        | Test double               | Same missing current port                                                              | Normal pass; one create-plan writer, rules symlink, no retired outputs                       |
|  12 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression`                           | Product contract, no edit | Node itself passes, while entry evaluator reports active-ledger `coverage_mismatch`    | Node remains normal pass; exact source/AST boundary unchanged; ledger becomes fixed-in-place |
|  13 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync`                                                                      | Test observer             | Individual node fails because retired active argument is rejected                      | Normal pass; new/active/sync convergence preserved                                           |
|  14 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root`                                           | Test observer             | Individual node fails because retired arguments are rejected                           | Normal pass; root tree, PUML, and ready-board content preserved                              |
|  15 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands`             | Test observer             | Individual node fails for retired argument or subsequent missing active state          | Normal pass; command success checked before read; copied bytes and observations preserved    |

Row 2 is read-only and remains represented by successor:

```text
tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood
```

## 7. Product row 3 runtime design

### 7.1 Read-only identity path

```text
application import request
  -> GitGateway.origin_github_repo_slug
  -> infra.git_cli.origin_github_repo_slug
  -> _remote_get_url(push=False)
  -> _parse_github_repo_slug(fetch_url)
  -> normalized lowercase owner/repo
```

`_parse_github_repo_slug` is an identity parser, not a publication-policy decision. It may parse a credential-bearing GitHub HTTPS fetch URL but never returns the raw URL or credential.

### 7.2 Publication path

```text
publication request
  -> read fetch URL
  -> read push URL
  -> reject userinfo in either URL using redacted diagnostics
  -> parse both GitHub repository identities
  -> require exact normalized slug equality
  -> return accepted slug and push URL
```

The verification matrix contains four mandatory cases:

1. credential-bearing fetch URL: read-only identity succeeds; publication rejects without exposure;
2. clean fetch plus credential-bearing push URL: publication rejects without exposure;
3. clean fetch and clean push with different repositories: publication rejects mismatch;
4. clean matching fetch and push: publication succeeds and returns the expected normalized slug.

This diagnostic is run before commit, on the exact clean implementation commit, and on the post-merge B1 tip.

## 8. Dogfood and protected-data design

### 8.1 Pre-projection snapshot

Immediately before lifecycle update, record outside the repository:

* pre-projection ready record and candidate digest;
* hashes and metadata of both fixed-slot `SKILL.md` files;
* a deterministic type/mode/symlink-target/file-content snapshot of consumer-owned `spec-dock/initiatives`, repository Workbench paths, and existing Artifacts paths;
* current tracked diff.

The snapshot excludes transient evidence and secret-bearing output.

### 8.2 Projection

Run the current external provider CLI as one complete update. Validate its JSON result before reading generated files. The projection may change only the four generated identities listed in §5.6 in addition to the provider source already edited.

### 8.3 Post-projection proof

Require:

* source/dogfood runtime byte equality;
* old candidate digest differs from new candidate digest;
* update result, ready record, and both markers agree on the new digest;
* record and marker closed fields are unchanged;
* the protected-data snapshot is exactly equal;
* fixed-slot `SKILL.md` bytes are exactly equal;
* package/source/wheel/sdist/installed/dogfood parity node executes and passes in the full-regression shard lane.

Any version, lifecycle, wire, schema, protected-data, policy, workflow, or unrelated root drift stops the execution and discards the projection candidate.

## 9. Ledger transition design

The ledger transition is an atomic working-tree operation after all 15 observed nodes pass and the dogfood/protection checkpoint is GREEN.

The transition program must:

1. load the exact saved pre-transition payload;
2. confirm the current ledger is byte-semantically equal to that payload immediately before mutation;
3. confirm exact row order, historical node IDs, signatures, row 2 object, and active set;
4. mutate only `lifecycle` and `resolution_mode` for rows 1 and 3–15;
5. compare the resulting payload against an expected payload constructed from the saved input;
6. write one normalized JSON file with a terminal newline;
7. rerun evaluator tests and all 15 selected nodes;
8. run the current full verifier in a private artifact root.

A verifier pass is necessary but not sufficient. The before/after ledger invariant is a separate merge-blocking proof.

## 10. Authorization and concurrency design

### 10.1 Read-only preflight

Read-only preflight may run before or after implementation authorization. It may fetch refs, read repository state, parse files, collect tests, and execute known entry observations that do not change tracked Product/test/ledger/dogfood state.

It must not run lifecycle update, edit files, stage, commit, push, create/update a PR, or merge.

### 10.2 Mutation gate

Immediately before the first file edit, the executor validates an execution packet with:

* exact specification SHA and tree;
* review target SHA and tree equal to the specification identity;
* immutable review receipt path and SHA-256;
* `review_status=pass`, P0=0, P1=0;
* `implementation_authorized=true`;
* `concurrent_writer_absent=true` plus a non-empty assertion identity and scope;
* separate booleans for commit/push and PR preparation;
* `human_merge_only=true`.

Missing, inconsistent, or unparsable values stop with zero mutations.

### 10.3 Writer scope

Concurrent-writer absence means no other process, worktree, agent, or Issue task is authorized to write any of:

* the exact 13 expected implementation paths;
* lifecycle-owned generated roots during the projection;
* the Issue branch ref.

The sixteen preserved support-history paths are explicitly excluded from the writer scope. No process, worktree, agent, or Issue task may edit, delete, rename, regenerate, recompress, or reclassify them. Their unchanged tree entries are an entry-gate assertion, not an implementation write permission.

A boolean without an assertion identity and scope is insufficient.

## 11. Evidence design

### 11.1 Private evidence root

Each execution uses `umask 077` and a private `mktemp -d` directory under a writable `${TMPDIR:-/tmp}` fallback. Predictable shared `/tmp/iss-...` paths are forbidden.

Every full verifier run receives a dedicated empty `--artifact-dir`. The executor selects `result.json` only from that private root and requires exactly one result.

### 11.2 Per-row evidence

Each of the 14 rows records:

* ordinal, node ID, historical signature;
* exact first-RED command, exit code, sanitized failure summary, raw-log SHA-256;
* changed path and symbol;
* exact GREEN command, exit code, execution count, normal-pass result;
* protected assertions;
* ledger before and after.

Row 12 records the entry evaluator `coverage_mismatch` as RED and the independently passing node as the current Product-boundary observation.

### 11.3 Candidate evidence

Working-tree evidence records both Git `HEAD` and a SHA-256 of the complete binary diff and is explicitly provisional. Candidate-wheel and merge-ready full-verifier evidence is never produced from that dirty state; it is rerun on one clean pushed implementation SHA and tree and contains:

* exact changed-file set;
* all per-row evidence;
* ledger before/after invariant;
* private full-verifier result hash and a sanitized distributable summary;
* ordinary, Provider CI-equivalent, package/dogfood, lint, and SpecDock validation results;
* row 3 security diagnostic;
* row 12 blob and AST guard;
* no-touch proof;
* protected-data proof;
* independent code review and final quality gate receipts.

Raw local evidence containing absolute paths is not copied into a distributed artifact. Distributed evidence contains redacted summaries and content hashes.

## 12. Exact clean candidate and review boundary

Commit and push are allowed only when the execution packet separately authorizes them. Only the exact 13 paths are staged. Untracked files, caches, logs, and evidence are not staged.

The boundary-test path is `tests/integration/test_issue_392_acceptance.py`. Its permitted change is limited to binding the baseline payload read to the immutable P392 entry blob, while preserving every Issue #392 assertion, and synchronizing the three Issue #395 canonical-document SHA-256 expectations with the final reviewed specification freeze. The separate migration observer path is `tests/unit/test_provider_test_lanes.py`; it compares the P392 before payload with the current root after payload and does not alter evaluator/verifier behavior. The existing Issue #392 ledger, timing, required-fast, policy, workflow, and boundary assertions remain intact; the synchronization must not weaken, remove, skip, or xfail any assertion.

After commit and push, all merge-blocking invariants are rerun on the clean candidate, including manual diagnostics and no-touch proofs—not only tests. Any remediation creates a new SHA and invalidates prior exact-SHA evidence.

Independent implementation review consists of:

1. `chatgpt-code-review-strict` on the exact clean pushed candidate, accepted only with pass and P0/P1=0;
2. `chatgpt-final-quality-gate-strict-v2` on the same final candidate, accepted only with pass, complete coverage, P0/P1=0, and empty unreviewed/unresolved lists.

Neither review authorizes merge. The PR base remains the Epic integration branch and the human remains the only merge authority.

## 13. Post-merge B1 and B2 design

### 13.1 B1

After human merge, use a separate clean verification checkout of the integration branch and fix the exact merge SHA and tree.

B1 requires:

* the accepted PR head tree equals the post-merge integration tree;
* Provider CI receipts for both Linux and macOS matrix roles are successful on that PR head tree;
* ordinary lane, provider lifecycle unit suite, distribution cutover, lifecycle platform/coordination suite, packaged distribution parity, dogfood parity, lint, SpecDock validate, row 3 publication diagnostic, row 12 guard, protected-data proof, and current full verifier are all GREEN or unchanged as applicable;
* unexpected failures are zero;
* the exact integration SHA remains unchanged throughout local verification.

Tree equality is required because CI status is attached to the PR head commit while B1/B2 identity is the human-merged integration commit. If trees differ, CI evidence cannot be reused and B1 stops.

### 13.2 B2

On the same exact SHA and tree, verify:

* 15 total rows;
* 0 active;
* 15 resolved;
* 14 fixed-in-place;
* 1 superseded;
* approved 0;
* unexpected 0;
* timing remains 243;
* ledger historical fields remain preserved.

B1 and B2 are not split across commits or substituted by future reruns. LunaMax does not close Issues or start #396.

## 14. Stop, recovery, and rollback

Stop without selecting a new design when any of these occurs:

* repository, branch, SHA, tree, upstream, remote, ancestry, or spec-pack identity mismatch;
* dirty or unaccounted worktree state before execution;
* incomplete or inconsistent review/authorization packet;
* concurrent writer detected or assertion scope inadequate;
* baseline row/order/signature/successor/timing drift;
* entry full-verifier violation outside the exact P392 allowance;
* first RED differs from the row contract;
* row 12 source or AST boundary drift;
* a heavy selected test skips or xfails;
* credential exposure or publication-policy weakening;
* dogfood/protected-data/lifecycle drift;
* ledger field drift outside the exact two-field transition;
* unexpected failure outside the 14 rows;
* need for lifecycle redesign, `E384-QUAL-001`, policy retirement, workflow redesign, main merge, or a new owner decision.

Before human merge, abandon or repair the complete Issue candidate. After human merge and before #396, the rollback unit is the whole Issue #395 merge or an owned forward-fix chosen by a human. Ledger-only, Product-only, test-only, generated-mirror-only, and automatic rollback are forbidden.

## 15. Requirement traceability

| Requirement | Corrected design |
| ----------- | ---------------- |
| I395-RQ-001 | §§3, 10, 11      |
| I395-RQ-002 | §§5–7            |
| I395-RQ-003 | §7               |
| I395-RQ-004 | §5.2, §6         |
| I395-RQ-005 | §5.3, §6         |
| I395-RQ-006 | §5.5, §6         |
| I395-RQ-007 | §9               |
| I395-RQ-008 | §§4–6, 9         |
| I395-RQ-009 | §§3.2, 4, 12–13  |
| I395-RQ-010 | §8               |
| I395-RQ-011 | §§11–13          |
| I395-RQ-012 | §13              |
| I395-RQ-013 | §§1, 10, 12      |
| I395-RQ-014 | §11              |
| I395-RQ-015 | §14              |
| I395-RQ-016 | §14              |
| I395-RQ-017 | §12              |

## 16. Decision state

The Issue-specific admission/history decision is now explicit: the current canonical specification pack remains exactly six paths, and the existing exact sixteen support artifacts remain immutable, non-authoritative, grandfathered support history at the recorded checkpoint. No new support artifact is admitted and no support-history content is updated to match current R/D/P. This decision changes no Product, security, lifecycle, policy, protected-data, workflow, or parent contract.

`owner_decisions_required=[]` is therefore consistent with the current design. Following the explicit user dispatch, `implementation_allowed=true` remains the recorded owner permission. Effective mutation is still gated separately: the repaired exact SHA/tree must first pass a fresh Strict specification review with `review_status=pass`, P0=0, P1=0, and a valid execution packet with concurrent-writer absence. Exact identity, clean push, human merge, and all implementation/delivery gates remain separate requirements.
