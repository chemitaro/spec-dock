---
種別: Normative Artifact
ID: "active-failure-disposition-register-v2"
タイトル: "Active Failure Disposition Register"
状態: "accepted"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "eaddf76806c338ee05463741f15fd3967bbceb57"
source_ledger:
  path: "full-regression-ledger.json"
  git_blob_sha1: "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4"
  original_row_count: 27
---

# Active Failure Disposition Register

## 1. Normative role

本Artifactはrepository evidence SHA `eaddf76806c338ee05463741f15fd3967bbceb57` のsource ledger全27 original identitiesを固定し、Issue #387の許容された実装結果を三分岐でdeterministically受理し、Issue #392 S60でactive 0へ収束させる唯一のauthorityである。

Issue #387 canonical Requirement/Design/Planは変更しない。#392は#387 completion report、#387 merge tree、post-merge ledger、post-merge pytest collectionをauthority inputとして読み、本Artifactのclosed ruleだけを適用する。Lunaはremove/retain/split、successor、failure lineage、dispositionを選択しない。

## 2. Source ledger identity

- Repository: `chemitaro/spec-dock`
- Branch: `codex/epic-00384-provider-test-strategy-planning`
- Commit: `eaddf76806c338ee05463741f15fd3967bbceb57`
- Ledger blob: `efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4`
- Original row count: `27`。This count identifies the source ledger only; post-#387 and S60 row counts are formula-derived and are not fixed to 15 or any other literal。

## 3. #387 report evidence contract

S00 requires exactly one JSON object between the following markers in the completed #387 report:

```text
<!-- ISSUE-00387-DISPOSITION-BEGIN -->
<!-- ISSUE-00387-DISPOSITION-END -->
```

The enclosed object has `schema_version=1`、`issue_id="iss-00387"`、exact merge SHA/tree、and exactly one `entries[]` item for each conditional baseline node in rows 4〜15。Each entry has the exact keys declared in the machine block below。Missing markers/entry, duplicate entry, free-form-only prose, or an outcome outside the closed three-way enum is a hard stop before S10。

## 4. Closed three-way admission rule

| #387 outcome | Exact evidence | S00 admitted ledger identity | S60 terminalization |
|---|---|---|---|
| `removed` | old node absent; report `removed_nodeids=[old]`; nonempty exact positive successors; absence evidence; no failure-lineage node | none | original identity is superseded to the report successors in this register; do not reinsert into transitional ledger |
| `retained-unchanged` | same node remains; exact source signature; nonempty retain(reason); no mapping/removal fields | same active node/signature | same node becomes a normal pass and is `resolved/fixed-in-place` |
| `split-or-renamed` | old node absent; exact report mapping; nonempty passing positive successors; zero or one exact failure-lineage node | the one failure-lineage node with exact source signature, or none | original identity superseded to positive successors; admitted failure-lineage node becomes normal pass and `resolved/fixed-in-place` |

Any unmapped new ledger row、signature drift、multiple failure-lineage nodes、missing/failed successor、or #387 contract-external tree result stops before S10 and requires canonical specification owner update plus a new Strict review。No best-effort mapping is permitted。

## 5. Original 27-row authority table

| # | Baseline node ID | Signature SHA-256 | Scope / admission | S60 closed rule | Authority / rationale | Verification owner |
|---:|---|---|---|---|---|---|
| 1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-delete` |
| 2 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source` | `8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637` | `outside #387; existing resolved identity unchanged` | `superseded -> tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood` | epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract: The historical Issue #359 source comparison is superseded by the final two fixed-slot provider/dogfood asset parity test. | `provider-assets` |
| 3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 4 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract` | `88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09: This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract. | `current-surface-context-pack` |
| 5 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09: This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract. | `current-surface-context-pack` |
| 6 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09: This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract. | `current-surface-context-pack` |
| 7 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack` | `c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09: This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract. | `current-surface-context-pack` |
| 8 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 9 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative` | `c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 10 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning` | `b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 11 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 12 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 13 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 14 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 15 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `#387 conditional: removed | retained-unchanged | split-or-renamed` | `ISS387-THREE-WAY-V1 mechanical branch` | iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09: This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior. | `current-surface-selection` |
| 16 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 17 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 18 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 19 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 20 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 21 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 22 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 23 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 24 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-shell` |
| 25 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-sync` |
| 26 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-sync` |
| 27 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | `outside #387; node/signature unchanged` | `fixed-in-place same admitted node` | Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-workbench` |

## 6. Post-#387 admission and S60 ledger rules

S00 writes an ignored `post-387-admission.json` matching the machine schema. It records report/ledger/tree/collection identities and the mechanically admitted active rows. Its row count is computed by:

```text
outside_scope_rows_present
+ conditional_retained_rows
+ conditional_split_rows_with_failure_lineage
```

No fixed post-#387 row count is accepted. S60 applies the row-specific `s60_rule` and the three-way rule, then requires:

- `active_count=0` and `approved_failure_count=0`;
- every retained/failure-lineage row normally passes;
- row 2 maps to `tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood`;
- all other outside-#387 rows normally pass under the same node ID;
- removed/no-lineage original identities remain preserved in this register and are not reinserted just to reach a fixed count;
- `tests/unit/test_provider_test_lanes.py` verifies report admission, formulas, zero active, exact collection mappings, andcurrent verifier compatibility;
- no skip、xfail、approved-no-op、signature acceptance is treated as completion。

## 7. Machine-readable register

<!-- BEGIN ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->
```json
{
  "schema_version": 2,
  "kind": "active-failure-disposition-register",
  "source": {
    "repository": "chemitaro/spec-dock",
    "branch": "codex/epic-00384-provider-test-strategy-planning",
    "commit": "eaddf76806c338ee05463741f15fd3967bbceb57",
    "path": "full-regression-ledger.json",
    "git_blob_sha1": "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4",
    "original_row_count": 27,
    "original_row_identity": "nodeid + fixed_point_signature_sha256"
  },
  "issue_387_contract": {
    "requirement_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/requirement.md",
    "design_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/design.md",
    "plan_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/plan.md",
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
    "must_not_modify_issue_387_canonical_documents": true
  },
  "conditional_rule": {
    "rule_id": "ISS387-THREE-WAY-V1",
    "authority_inputs": {
      "report_path": "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup/report.md",
      "report_block_begin": "<!-- ISSUE-00387-DISPOSITION-BEGIN -->",
      "report_block_end": "<!-- ISSUE-00387-DISPOSITION-END -->",
      "post_merge_tree": "ISSUE_387_MERGE^{tree}",
      "post_merge_ledger": "full-regression-ledger.json",
      "collection_command": "uv run pytest --run-full-regression --collect-only -q"
    },
    "report_entry_schema": {
      "required_keys": [
        "baseline_nodeid",
        "outcome",
        "retain_reason",
        "removed_nodeids",
        "mapped_nodes",
        "positive_successor_nodes",
        "failure_lineage_node",
        "absence_evidence_id"
      ],
      "outcome_enum": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "node_array_order": "UTF-8 bytewise ascending, unique"
    },
    "branches": {
      "removed": {
        "required": [
          "baseline node absent from post-#387 collection and ledger",
          "removed_nodeids equals [baseline_nodeid]",
          "mapped_nodes is empty",
          "positive_successor_nodes is non-empty and every node normally passes",
          "failure_lineage_node is null",
          "absence_evidence_id is non-null and resolves to #387 report evidence",
          "retain_reason is null"
        ],
        "s00_admitted_row": "none",
        "s60_original_row_terminalization": "superseded-to-positive-successor-nodes in this register; do not reinsert into transitional ledger"
      },
      "retained-unchanged": {
        "required": [
          "baseline node remains in post-#387 collection and ledger",
          "nodeid and failure signature equal the baseline row exactly",
          "retain_reason is a non-empty #387 report string",
          "removed_nodeids, mapped_nodes, positive_successor_nodes are empty",
          "failure_lineage_node and absence_evidence_id are null"
        ],
        "s00_admitted_row": "same baseline node active with unchanged signature",
        "s60_original_row_terminalization": "same node fixed-in-place normal pass"
      },
      "split-or-renamed": {
        "required": [
          "baseline node absent from post-#387 collection and ledger",
          "mapped_nodes is non-empty and exactly equals the #387 report old-to-new mapping",
          "positive_successor_nodes is a non-empty subset of mapped_nodes and every node normally passes",
          "failure_lineage_node is null or one member of mapped_nodes",
          "if failure_lineage_node is non-null, it is the only post-#387 ledger row carrying the exact baseline signature",
          "if failure_lineage_node is null, no post-#387 ledger row carries the baseline signature",
          "removed_nodeids equals [baseline_nodeid]",
          "absence_evidence_id is non-null",
          "retain_reason is null"
        ],
        "s00_admitted_row": "failure_lineage_node active with unchanged signature when non-null; otherwise none",
        "s60_original_row_terminalization": "original baseline row superseded to all positive_successor_nodes; any admitted failure_lineage_node is separately fixed-in-place to a normal pass"
      }
    }
  },
  "post_387_admission_schema": {
    "schema_version": 1,
    "required_keys": [
      "issue_387_merge_sha",
      "issue_387_tree_sha",
      "issue_387_report_blob_sha1",
      "post_387_ledger_blob_sha1",
      "post_387_collection_sha256",
      "conditional_entries",
      "admitted_ledger_rows"
    ],
    "conditional_entries_count": 12,
    "admitted_ledger_row_count_formula": "outside_scope_rows_present + conditional_retained_rows + conditional_split_rows_with_failure_lineage",
    "fixed_numeric_row_count": null,
    "signature_policy": "all admitted active rows use the exact source signature for their original baseline identity",
    "stop_codes": [
      "issue-387-report-block-missing",
      "issue-387-report-entry-missing",
      "issue-387-report-entry-duplicate",
      "issue-387-outcome-invalid",
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
    "outside_scope_rule": "row 2 superseded; all other admitted outside-scope active rows fixed-in-place",
    "conditional_rule": "apply ISS387-THREE-WAY-V1 branch mechanically; no implementer choice",
    "ledger_row_count_formula": "post_387_admitted_ledger_row_count; removed/no-lineage original identities remain terminal only in this register",
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
      "nodeid": "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
      "signature_sha256": "0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-delete",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 2,
      "nodeid": "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source",
      "signature_sha256": "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
      "expected_post_387": "unchanged-resolved-superseded",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood",
      "retirement_authority": "epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract",
      "rationale": "The historical Issue #359 source comparison is superseded by the final two fixed-slot provider/dogfood asset parity test.",
      "verification_owner": "provider-assets",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "supersede-to-fixed-provider-asset-test",
      "s60_successor": "tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood",
      "authority": "epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract"
    },
    {
      "row": 3,
      "nodeid": "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
      "signature_sha256": "f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 4,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract",
      "signature_sha256": "88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 5,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 6,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 7,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack",
      "signature_sha256": "c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_refreshes_current_structural_context_pack",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node mixes or observes legacy Authority/EAL/context-pack behavior. Issue #387 may remove it, retain a surviving positive slice, or split/rename it under its accepted consumer-classification contract.",
      "verification_owner": "current-surface-context-pack",
      "authority": "iss-00387 I387-R03/I387-R07; Design §5.3; Plan C40-08/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 8,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 9,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative",
      "signature_sha256": "c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_issue_lifecycle.py::TestIssueLifecycle::test_issue_start_orders_dependency_checkout_active_write_and_sync",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 10,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning",
      "signature_sha256": "b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 11,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_storage_core_cli.py::TestStorageCoreCli::test_active_set_exposes_only_target_selectors_and_invalid_target_is_no_write",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 12,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 13,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 14,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 15,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "This node belongs to the legacy set_active force/GitHub/dependency surface. Issue #387 may remove, retain(reason), or split/rename it while preserving Current selection-only/issue-start positive behavior.",
      "verification_owner": "current-surface-selection",
      "authority": "iss-00387 I387-R05/I387-R07; Design §4/§5.3; Plan C20-04/C30-01/C40-09",
      "scope": "iss-00387-conditional",
      "admission_rule": "ISS387-THREE-WAY-V1",
      "allowed_post_387_outcomes": [
        "removed",
        "retained-unchanged",
        "split-or-renamed"
      ],
      "s60_rule": "conditional-terminalization-v1"
    },
    {
      "row": 16,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
      "signature_sha256": "3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 17,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
      "signature_sha256": "55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 18,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
      "signature_sha256": "ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 19,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
      "signature_sha256": "ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 20,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
      "signature_sha256": "22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 21,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
      "signature_sha256": "0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 22,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
      "signature_sha256": "541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 23,
      "nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
      "signature_sha256": "44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-import",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 24,
      "nodeid": "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
      "signature_sha256": "0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-shell",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 25,
      "nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
      "signature_sha256": "f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-sync",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 26,
      "nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
      "signature_sha256": "3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-sync",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    },
    {
      "row": 27,
      "nodeid": "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
      "signature_sha256": "20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9",
      "expected_post_387": "unchanged-active",
      "final_disposition": "fixed-in-place",
      "successor_nodeid": "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
      "retirement_authority": null,
      "rationale": "当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。",
      "verification_owner": "runtime-workbench",
      "scope": "outside-iss-00387",
      "admission_rule": "OUTSIDE-387-UNCHANGED-V1",
      "allowed_post_387_outcomes": [
        "unchanged"
      ],
      "s60_rule": "fixed-in-place-same-node",
      "s60_successor": "tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
      "authority": "Current surviving behavior outside Issue #387 scope; Epic #384 failure terminalization"
    }
  ],
  "owner_decisions_required": []
}
```
<!-- END ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->

## 8. Verification commands

```bash
uv run python - <<'PY'
from pathlib import Path
import json, re
p = Path("spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/active-failure-disposition-register.md")
m = re.search(r"<!-- BEGIN ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->\n```json\n(.*?)\n```\n<!-- END ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->", p.read_text(encoding="utf-8"), re.S)
assert m is not None
d = json.loads(m.group(1))
assert d["schema_version"] == 2
assert len(d["rows"]) == 27
assert d["owner_decisions_required"] == []
assert d["s60_finalization"]["active_count"] == 0
assert d["post_387_admission_schema"]["fixed_numeric_row_count"] is None
PY
uv run pytest -q tests/unit/test_provider_test_lanes.py
uv run python -m scripts.quality.verify_full_regression --shards 4
```

## 9. Owner decisions

`owner_decisions_required=[]`。All three #387 outcomes and their #392 consequences are already decided。
