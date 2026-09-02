---
種別: Normative Artifact
ID: "active-failure-disposition-register-v5"
タイトル: "Active Failure Disposition Register"
状態: "accepted"
最終更新: "2026-09-02"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ea168b745d3f443f11a24b975f32e3bb6fb17b1a"
source_ledger:
  path: "full-regression-ledger.json"
  git_blob_sha1: "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4"
  original_row_count: 27
---

# Active Failure Disposition Register

## 1. Normative role

This Artifact fixes the 27 original source-ledger node/signature identities and the deterministic Issue #387 admission/Issue #392 terminalization rule. Issue #387 canonical Requirement, Design and Plan remain unchanged. The only conditional rule ID is `ISS387-THREE-WAY-V2`.

The Issue #387 tracked report contains only a schema/rule declaration and the 12 deterministic remove, retain(reason), or split mappings. It contains no repository, pull-request number, candidate/head/tree identity, evidence-tail identity or future merge fact. After human merge, S00 derives all GitHub and Git identities independently and then applies this register. Luna selects no PR, successor, lineage or disposition.

## 2. Source ledger and row-count rule

- Repository: `chemitaro/spec-dock`
- Source commit: `ea168b745d3f443f11a24b975f32e3bb6fb17b1a`
- Source ledger blob: `efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4`
- Original identities: exactly 27
- Conditional identities: source rows 4–15, exactly 12
- Post-#387 row count: formula-derived, never fixed to 15 or another literal
- S60 final state: active count 0 and approved-failure count 0

## 3. `ISS387-THREE-WAY-V2` tracked report mapping contract

The completed #387 tracked report contains exactly one compact JSON object between `<!-- ISSUE-00387-DISPOSITION-BEGIN -->` and `<!-- ISSUE-00387-DISPOSITION-END -->`. Its exact top-level keys are:

```text
schema_version,kind,issue_id,rule_id,entries
```

Values are `schema_version=4`, `kind="iss-00387-pre-merge-disposition"`, `issue_id="iss-00387"`, `rule_id="ISS387-THREE-WAY-V2"`, and exactly 12 entries, one for each source row 4–15. It contains no repository, PR number, branch, commit SHA, tree OID, merge identity, timestamp, ledger hash or collection hash.

Each entry has exact keys:

```text
baseline_nodeid,outcome,retain_reason,removed_nodeids,mapped_nodes,
positive_successor_nodes,failure_lineage_node,absence_evidence_id
```

Arrays are unique UTF-8-bytewise sorted. Allowed outcomes are exactly `removed`, `retained-unchanged`, `split-or-renamed`. All fields and branch relations are defined in the machine block. The report is pre-merge and does not predict or identify its future GitHub PR or merge.

## 4. Unique merged PR discovery and merge-tree authority

After #387 is human merged, S00 performs this closed algorithm without using a report identity:

1. Read the GitHub Issue #387 timeline/cross-reference collection and collect same-repository pull-request numbers only.
2. Fetch each referenced PR object and its exact head SHA, head repository, base branch, state, merge commit and changed paths.
3. For each distinct head SHA, call `GET /repos/chemitaro/spec-dock/commits/{head_sha}/pulls` and retain the PR only when that association includes the same PR number.
4. Filter to repository `chemitaro/spec-dock`, base `main`, merged state, a report path in the merged tree, and a merge commit reachable from the admitted main/implementation base.
5. Require exactly one PR. Zero or multiple candidates stop before S10.
6. Fetch the PR head commit/tree and merge commit/tree; require `pr_head_tree == merge_commit_tree`.
7. Read the exact #387 report blob, `full-regression-ledger.json`, and pytest collection from the merge tree, not from a report-provided SHA.
8. Validate the report block and apply `ISS387-THREE-WAY-V2` to the merge-tree ledger/collection.

No extra #387 commit boundary or report-to-merge identity/tail rule exists. The current #387 one-implementation-plus-evidence-commit plan remains satisfiable without modification.

## 5. Closed outcome rules

| #387 outcome | Required merge-tree evidence | Admitted failure row | S60 terminal rule |
|---|---|---|---|
| `removed` | old node absent from ledger/collection; `removed_nodeids=[old]`; mapped nodes empty; positive successors nonempty/passing; exact absence evidence; no lineage row | none | original identity is superseded to exact positive successors; no ledger row is reinserted |
| `retained-unchanged` | same node remains with exact source signature; nonempty retain reason; removal/mapping/successor arrays empty | same source node/signature | same node is fixed in place to a normal pass and recorded resolved/fixed-in-place |
| `split-or-renamed` | old node absent; mapped nodes exact/nonempty; positive successor subset passes; zero or one exact lineage node carrying source signature | optional one mapped lineage row | original is superseded to positives; optional lineage row is fixed in place to normal pass |

Missing report block/entry, report identity field, unmapped new row, signature drift, multiple lineage rows, failed/missing positive successor or #387-contract-external merge-tree result stops before S10 and requires canonical spec-owner amendment plus independent Strict re-review.

## 6. Original identity table

| # | Baseline node ID | Signature SHA-256 | Permitted post-#387 state | Exact S60 terminal rule | Verification owner |
|---:|---|---|---|---|---|
| 1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active | `runtime-delete` |
| 2 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source` | `8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637` | `resolved` exact same node/signature | superseded → tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood | `provider-assets` |
| 3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote | `runtime-import` |
| 4 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract` | `88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-context-pack` |
| 5 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-context-pack` |
| 6 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-context-pack` |
| 7 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack` | `c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-context-pack` |
| 8 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 9 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative` | `c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 10 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning` | `b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 11 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 12 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 13 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 14 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 15 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed | retained-unchanged | split-or-renamed` via `ISS387-THREE-WAY-V2` | closed branch: removed→superseded; retained→fixed-in-place; split→superseded + optional lineage fixed-in-place | `current-surface-selection` |
| 16 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression | `runtime-import` |
| 17 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression | `runtime-import` |
| 18 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression | `runtime-import` |
| 19 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read | `runtime-import` |
| 20 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present | `runtime-import` |
| 21 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression | `runtime-import` |
| 22 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression | `runtime-import` |
| 23 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam | `runtime-import` |
| 24 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression | `runtime-shell` |
| 25 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync | `runtime-sync` |
| 26 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root | `runtime-sync` |
| 27 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | `active` exact same node/signature | fixed-in-place → tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands | `runtime-workbench` |

## 7. Machine-readable register

<!-- BEGIN ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->
```json
{
  "schema_version": 5,
  "kind": "epic384_active_failure_disposition_register_v5",
  "source": {
    "repository": "chemitaro/spec-dock",
    "branch": "codex/epic-00384-provider-test-strategy-planning",
    "commit": "ea168b745d3f443f11a24b975f32e3bb6fb17b1a",
    "path": "full-regression-ledger.json",
    "git_blob_sha1": "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4",
    "original_row_count": 27,
    "original_row_identity": "baseline_nodeid + signature_sha256"
  },
  "issue_387_contract": {
    "canonical_documents_are_read_only": true,
    "allowed_outcomes": [
      "removed",
      "retained-unchanged",
      "split-or-renamed"
    ],
    "conditional_baseline_rows": [
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15
    ],
    "requirement_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/requirement.md",
    "design_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/design.md",
    "plan_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/plan.md"
  },
  "tracked_report_contract": {
    "schema_version": 4,
    "kind": "iss-00387-pre-merge-disposition",
    "report_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md",
    "block_begin": "<!-- ISSUE-00387-DISPOSITION-BEGIN -->",
    "block_end": "<!-- ISSUE-00387-DISPOSITION-END -->",
    "required_top_level_keys": [
      "schema_version",
      "kind",
      "issue_id",
      "rule_id",
      "entries"
    ],
    "additional_top_level_keys_allowed": false,
    "entries_count": 12,
    "entry_keys": [
      "baseline_nodeid",
      "outcome",
      "retain_reason",
      "removed_nodeids",
      "mapped_nodes",
      "positive_successor_nodes",
      "failure_lineage_node",
      "absence_evidence_id"
    ],
    "node_array_order": "UTF-8 bytewise ascending and unique"
  },
  "s00_github_merge_verification": {
    "rule_id": "ISS387-THREE-WAY-V2",
    "issue_timeline_endpoint": "GET /repos/chemitaro/spec-dock/issues/387/timeline",
    "pull_request_endpoint": "GET /repos/chemitaro/spec-dock/pulls/{pull_request_number}",
    "head_commit_association_endpoint": "GET /repos/chemitaro/spec-dock/commits/{pull_request_head_sha}/pulls",
    "discovery_rule": "collect same-repository PR references from Issue #387 timeline; fetch each PR; require its exact head commit association to include the same PR; filter repo chemitaro/spec-dock, base main, merged, report present; exactly one",
    "required_relations": [
      "repository equals chemitaro/spec-dock",
      "pull request is human merged and merge commit is reachable from admitted main and implementation base",
      "pull-request head tree equals merge-commit tree",
      "implementation base contains SPEC_FREEZE_COMMIT and the Issue #387 merge commit",
      "report blob, post-merge ledger and full collection are read from the merge tree",
      "merged report block, ledger and collection satisfy ISS387-THREE-WAY-V2"
    ],
    "forbidden": [
      "report identity dependency",
      "new Issue #387 commit boundary",
      "future merge identity in tracked report",
      "trusting report prose without GitHub verification",
      "blanket repository-evidence-SHA diff"
    ]
  },
  "conditional_rule": {
    "rule_id": "ISS387-THREE-WAY-V2",
    "branches": {
      "removed": {
        "required": [
          "baseline node is absent from the post-#387 collection and ledger",
          "removed_nodeids equals [baseline_nodeid]",
          "mapped_nodes is empty",
          "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
          "failure_lineage_node is null",
          "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
          "retain_reason is null"
        ],
        "s00_admitted_rows": [],
        "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
      },
      "retained-unchanged": {
        "required": [
          "baseline node remains in the post-#387 collection and ledger",
          "nodeid and failure signature equal the source row exactly",
          "retain_reason is a non-empty tracked #387 report string",
          "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
          "failure_lineage_node and absence_evidence_id are null"
        ],
        "s00_admitted_rows": [
          "baseline_nodeid with exact source signature"
        ],
        "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
      },
      "split-or-renamed": {
        "required": [
          "baseline node is absent from the post-#387 collection and ledger",
          "removed_nodeids equals [baseline_nodeid]",
          "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
          "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
          "failure_lineage_node is null or exactly one member of mapped_nodes",
          "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
          "when null, no post-#387 ledger row carries the source signature",
          "absence_evidence_id is non-null",
          "retain_reason is null"
        ],
        "s00_admitted_rows": [
          "failure_lineage_node with exact source signature when non-null"
        ],
        "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
      }
    }
  },
  "post_387_admission_schema": {
    "schema_version": 4,
    "required_keys": [
      "repository",
      "issue_387_pull_request_number",
      "issue_387_pull_request_head_sha",
      "issue_387_pull_request_head_tree",
      "issue_387_merge_sha",
      "issue_387_merge_tree",
      "issue_387_head_merge_tree_equality",
      "issue_387_report_blob_sha1",
      "post_387_ledger_blob_sha1",
      "post_387_collection_sha256",
      "conditional_entries",
      "admitted_ledger_rows"
    ],
    "conditional_entries_count": 12,
    "admitted_ledger_row_count_formula": "outside_scope_rows_present + conditional_retained_rows + conditional_split_rows_with_failure_lineage",
    "fixed_numeric_row_count": null,
    "signature_policy": "every admitted active row uses the exact source signature of its original identity",
    "stop_codes": [
      "issue-387-report-block-missing",
      "issue-387-report-schema-invalid",
      "issue-387-report-identity-field-forbidden",
      "issue-387-report-entry-missing",
      "issue-387-report-entry-duplicate",
      "issue-387-outcome-invalid",
      "issue-387-timeline-pr-zero-or-multiple",
      "issue-387-head-association-mismatch",
      "issue-387-merge-lineage-invalid",
      "issue-387-head-merge-tree-equality-failed",
      "issue-387-removal-unproven",
      "issue-387-retain-node-or-signature-drift",
      "issue-387-split-mapping-invalid",
      "issue-387-successor-missing-or-not-passing",
      "issue-387-failure-lineage-ambiguous",
      "issue-387-unmapped-new-ledger-row",
      "issue-387-out-of-contract-tree-delta"
    ]
  },
  "s60_finalization": {
    "active_count": 0,
    "approved_failure_count": 0,
    "fixed_numeric_row_count": null,
    "outside_scope_rule": "row 2 superseded to the fixed provider asset test; every other admitted outside-scope active row fixed in place",
    "conditional_rule": "apply ISS387-THREE-WAY-V2 mechanically with no implementer choice",
    "forbidden": [
      "approved-no-op",
      "active",
      "xfail",
      "policy-skip-as-success",
      "signature-acceptance-as-success"
    ]
  },
  "rows": [
    {
      "row": 1,
      "baseline_nodeid": "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
      "signature_sha256": "0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-delete",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
        "signature_sha256": "0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 2,
      "baseline_nodeid": "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source",
      "signature_sha256": "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
      "scope": "outside-iss-00387",
      "authority": "epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract",
      "rationale": "The historical Issue #359 source comparison is superseded by the final two fixed-slot provider/dogfood asset parity test.",
      "verification_owner": "provider-assets",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source",
        "signature_sha256": "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
        "lifecycle": "resolved"
      },
      "s60_terminalization": {
        "disposition": "superseded",
        "successor_nodeids": [
          "tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 3,
      "baseline_nodeid": "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
      "signature_sha256": "f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
        "signature_sha256": "f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 4,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract",
      "signature_sha256": "88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 5,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 6,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 7,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack",
      "signature_sha256": "c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 8,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 9,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative",
      "signature_sha256": "c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 10,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning",
      "signature_sha256": "b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 11,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 12,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 13,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 14,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 15,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "scope": "iss-00387-conditional",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "admission_rule": "ISS387-THREE-WAY-V2",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "outcome_rules": {
        "removed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is empty",
            "positive_successor_nodes is non-empty, unique, UTF-8 bytewise sorted, and every node normally passes",
            "failure_lineage_node is null",
            "absence_evidence_id is non-null and resolves to tracked #387 pre-merge evidence",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [],
          "s60_terminalization": "original identity is superseded to the exact report positive_successor_nodes; do not reinsert a ledger row"
        },
        "retained-unchanged": {
          "required": [
            "baseline node remains in the post-#387 collection and ledger",
            "nodeid and failure signature equal the source row exactly",
            "retain_reason is a non-empty tracked #387 report string",
            "removed_nodeids, mapped_nodes, and positive_successor_nodes are empty",
            "failure_lineage_node and absence_evidence_id are null"
          ],
          "s00_admitted_rows": [
            "baseline_nodeid with exact source signature"
          ],
          "s60_terminalization": "same node is fixed in place to a normal pass and recorded resolved/fixed-in-place"
        },
        "split-or-renamed": {
          "required": [
            "baseline node is absent from the post-#387 collection and ledger",
            "removed_nodeids equals [baseline_nodeid]",
            "mapped_nodes is non-empty, unique, UTF-8 bytewise sorted, and exactly equals the tracked #387 mapping",
            "positive_successor_nodes is a non-empty subset of mapped_nodes and every positive node normally passes",
            "failure_lineage_node is null or exactly one member of mapped_nodes",
            "when non-null, failure_lineage_node is the only post-#387 ledger row carrying the exact source signature",
            "when null, no post-#387 ledger row carries the source signature",
            "absence_evidence_id is non-null",
            "retain_reason is null"
          ],
          "s00_admitted_rows": [
            "failure_lineage_node with exact source signature when non-null"
          ],
          "s60_terminalization": "original identity is superseded to positive_successor_nodes; any admitted failure-lineage node is fixed in place to a normal pass"
        }
      }
    },
    {
      "row": 16,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
      "signature_sha256": "3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
        "signature_sha256": "3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 17,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
      "signature_sha256": "55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
        "signature_sha256": "55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 18,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
      "signature_sha256": "ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
        "signature_sha256": "ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 19,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
      "signature_sha256": "ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
        "signature_sha256": "ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 20,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
      "signature_sha256": "22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
        "signature_sha256": "22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 21,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
      "signature_sha256": "0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
        "signature_sha256": "0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 22,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
      "signature_sha256": "541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
        "signature_sha256": "541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 23,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
      "signature_sha256": "44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
        "signature_sha256": "44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 24,
      "baseline_nodeid": "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
      "signature_sha256": "0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-shell",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
        "signature_sha256": "0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 25,
      "baseline_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
      "signature_sha256": "f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-sync",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
        "signature_sha256": "f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 26,
      "baseline_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
      "signature_sha256": "3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-sync",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
        "signature_sha256": "3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root"
        ],
        "normal_pass_required": true
      }
    },
    {
      "row": 27,
      "baseline_nodeid": "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
      "signature_sha256": "20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9",
      "scope": "outside-iss-00387",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization",
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-workbench",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "required_post_387": {
        "nodeid": "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
        "signature_sha256": "20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9",
        "lifecycle": "active"
      },
      "s60_terminalization": {
        "disposition": "fixed-in-place",
        "successor_nodeids": [
          "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands"
        ],
        "normal_pass_required": true
      }
    }
  ],
  "owner_decisions_required": []
}
```
<!-- END ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->

## 8. Verification

The normative parser must assert schema 4, 27 source rows, 12 conditional entries, rule ID `ISS387-THREE-WAY-V2`, no conditional branch-fixed fields, no report repository/PR/candidate/head/tree/merge field, formula-derived post row count, S60 active/approved counts zero and `owner_decisions_required=[]`. It must discover the unique merged PR from GitHub Issue timeline/cross-reference and head-commit association evidence, verify PR-head-tree/merge-tree equality and read the mapping block, ledger and collection from the merge tree before S10.

## 9. Owner decisions

`owner_decisions_required=[]`. All allowed Issue #387 outcomes and their Issue #392 consequences are already decided.
