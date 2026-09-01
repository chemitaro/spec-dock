---
種別: Normative Artifact
ID: "active-failure-disposition-register-v1"
タイトル: "Active Failure Disposition Register"
状態: "accepted"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
source_ledger:
  path: "full-regression-ledger.json"
  git_blob_sha1: "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4"
---

# Active Failure Disposition Register

## 1. Normative role

本Artifactは、repository evidence SHA `ef183ae46febe52f0152431cb3a8b4846c9972fc` の`full-regression-ledger.json`にある全27行について、#387後に期待するdeltaと#392で採用するfinal dispositionを事前決定する。Lunaは行を再分類せず、本registerのexact node ID、signature、successor、authority、verification ownerを実装する。

Epic/Issue R/D/P、accepted ADR、Luna handoffは本Artifactをnormative inputとして参照する。内容差異がある場合は実装を開始せず、canonical specification ownerによるregister更新とindependent Strict re-reviewを要求する。

## 2. #387 expected delta

Issue #387はmanaged distribution/provider test architectureを所有しないが、Current surface cleanupとして次の12行だけをledgerから除去する。

- Rows 4〜7: `test_runtime_active_s05.py`の旧Authority、grants、Promotion、EAL contract。
- Rows 8〜15: `test_runtime_active_s06.py`の旧force、dependency、GitHub behavior。

Rows 4〜15は#387のpositive successorへsupersedeされ、post-#387 root ledgerへ再挿入しない。Rows 1〜3と16〜27のnode ID、signature、lifecycle fieldは#387により変更されない。Expected post-#387 ledgerは15行、active 14、resolved 1、retired 0である。

次のいずれかはS00 hard stopである。

- expected removal以外のrowがmissing。
- row 4〜15のいずれかが残る。
- signature change。
- new row。
- row 2のexisting resolved/superseded relationが変わる。
- expected successor nodeがcollectionに存在しない。

Stop時はS10へ進まず、canonical specification ownerが本registerを更新し、同じStrict reviewを再実行する。Implementation agentはequivalent successorを選ばない。

## 3. Final disposition table

| # | Baseline node ID | Signature SHA-256 | Expected after #387 | Final disposition | Exact successor | Authority / rationale | Verification owner |
|---:|---|---|---|---|---|---|---|
| 1 | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-delete` |
| 2 | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source` | `8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637` | `unchanged-resolved-superseded` | `superseded` | `tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood` | epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract: 旧Issue #359固定source比較をfinal provider/dogfood fixed-slot asset parityへ置換する。 | `provider-assets` |
| 3 | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 4 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract` | `88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-context-pack` |
| 5 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-context-pack` |
| 6 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal` | `8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-context-pack` |
| 7 | `tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack` | `c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_refreshes_current_structural_context_pack` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `runtime-sync` |
| 8 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 9 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative` | `c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_issue_lifecycle.py::TestIssueLifecycle::test_issue_start_orders_dependency_checkout_active_write_and_sync` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `issue-lifecycle` |
| 10 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning` | `b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 11 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug` | `f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5` | `removed-by-iss-00387` | `superseded` | `tests/cli_runtime/test_storage_core_cli.py::TestStorageCoreCli::test_active_set_exposes_only_target_selectors_and_invalid_target_is_no_write` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 12 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 13 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 14 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 15 | `tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision` | `23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8` | `removed-by-iss-00387` | `superseded` | `tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports` | iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09: 旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。 | `current-surface-selection` |
| 16 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 17 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 18 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 19 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 20 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 21 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 22 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 23 | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-import` |
| 24 | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-shell` |
| 25 | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-sync` |
| 26 | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-sync` |
| 27 | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | `unchanged-active` | `fixed-in-place` | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | N/A; same Current behavior remains: 当該Current behaviorはretireしない。同一node IDをnormal passへ修正し、skip/xfail/approved failureを使用しない。 | `runtime-workbench` |

## 4. S60 transitional ledger contract

S60では、post-#387に残る15行だけをcurrent ledgerへ保持し、全行を`lifecycle=resolved`へterminalizeする。

- Row 2: `resolution_mode=superseded`、successorは`tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood`。
- Rows 1、3、16〜27: `resolution_mode=fixed-in-place`、same node IDがnormal pass。
- Rows 4〜15: #387でremoved済みのため再挿入しない。
- `active_count=0`、`resolved_count=15`、`retired_count=0`。
- skip、xfail、approved-no-op、signature acceptanceをterminal outcomeに使用しない。

`tests/unit/test_provider_test_lanes.py`はS60でこのexact contract、transitional `provider-ci.yml` successor paths、current pytest adapter/standalone evaluator parityを検証する。S70でpolicy providerとともにretireし、final gateへfailure approval logicを移植しない。

## 5. Machine-readable register

<!-- BEGIN ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->
```json
{
  "schema_version": 1,
  "source": {
    "repository": "chemitaro/spec-dock",
    "branch": "codex/epic-00384-provider-test-strategy-planning",
    "commit": "ef183ae46febe52f0152431cb3a8b4846c9972fc",
    "path": "full-regression-ledger.json",
    "git_blob_sha1": "efb5cd87ec6cfcae05f1f38222e4d372fe6ff1e4",
    "row_count": 27
  },
  "expected_post_387": {
    "row_count": 15,
    "active_count": 14,
    "resolved_count": 1,
    "removed_rows": [
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
    "unchanged_rows": [
      1,
      2,
      3,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27
    ],
    "allowed_changes": [
      "remove rows 4 through 15 exactly",
      "remove exact timing/REQUIRED_FAST references belonging only to those deleted nodes",
      "do not change signatures or add rows"
    ]
  },
  "s60_transitional_ledger": {
    "row_count": 15,
    "active_count": 0,
    "resolved_count": 15,
    "retired_count": 0,
    "rule": "rows removed by iss-00387 stay absent; all remaining rows resolve as fixed-in-place except row 2 superseded to its final successor"
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
      "verification_owner": "runtime-delete"
    },
    {
      "row": 2,
      "nodeid": "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source",
      "signature_sha256": "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
      "expected_post_387": "unchanged-resolved-superseded",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/infra/test_provider_assets.py::test_fixed_skill_slots_match_provider_and_dogfood",
      "retirement_authority": "epic-00384 E384-RQ-001/E384-RQ-012; provider fixed two-slot asset contract",
      "rationale": "旧Issue #359固定source比較をfinal provider/dogfood fixed-slot asset parityへ置換する。",
      "verification_owner": "provider-assets"
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
      "verification_owner": "runtime-import"
    },
    {
      "row": 4,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_render_context_pack_states_entry_default_and_escalation_contract",
      "signature_sha256": "88a470cf10de911a0cc467dbf9a872689fd7126ae543ae2ffad00d8b343ea0ca",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-context-pack"
    },
    {
      "row": 5,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_marks_proposed_active_artifact_non_authoritative",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-context-pack"
    },
    {
      "row": 6,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_blocks_authoritative_input_when_scope_report_has_unresolved_eal",
      "signature_sha256": "8cca85a0280051a5a2e98ef5101d4b47603dfc282ed8ad6f44ef8d9de1d6dace",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_context_pack_contains_current_selection_entries",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-context-pack"
    },
    {
      "row": 7,
      "nodeid": "tests/cli_runtime/test_runtime_active_s05.py::TestRuntimeActiveS05::test_sync_auto_update_from_branch_writes_authority_context_pack",
      "signature_sha256": "c677546d7a10751f1e5a80133e319652ab7c075f88476eaef8f958bb25ee8d71",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_sync.py::TestCliSync::test_sync_refreshes_current_structural_context_pack",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "runtime-sync"
    },
    {
      "row": 8,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_blocked_without_force_fails_before_snapshot",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 9,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_force_commits_and_order_is_authoritative",
      "signature_sha256": "c074e342afb1d9047bcde6d3d2e49dff2f151e327f21cb2d581aa2c91679d30a",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_issue_lifecycle.py::TestIssueLifecycle::test_issue_start_orders_dependency_checkout_active_write_and_sync",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "issue-lifecycle"
    },
    {
      "row": 10,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_absorbs_github_issue_index_failure_as_warning",
      "signature_sha256": "b7d59944f1a444c0d2d6ee4fe8685885aad6ab5bdf3e976b540a0dadf01b75cf",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 11,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_resolves_current_unscoped_issue_with_current_repo_slug",
      "signature_sha256": "f5f895b159f95a46d5c868eb14d9f3f786485f797f1ec60d4dbb03ac5a856da5",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/cli_runtime/test_storage_core_cli.py::TestStorageCoreCli::test_active_set_exposes_only_target_selectors_and_invalid_target_is_no_write",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 12,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_skips_same_repo_repo_scoped_view_fetch_when_index_contains_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 13,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_same_repo_repo_scoped_view_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 14,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_falls_back_to_current_repo_view_for_unscoped_linked_initiative_when_index_missing_key",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
    },
    {
      "row": 15,
      "nodeid": "tests/cli_runtime/test_runtime_active_s06.py::TestRuntimeActiveS06::test_set_active_github_prefers_foreign_snapshot_under_same_number_collision",
      "signature_sha256": "23c33661669278ce159e442edc402d631a8ba836ecdf1fcb2a922e68883574e8",
      "expected_post_387": "removed-by-iss-00387",
      "final_disposition": "superseded",
      "successor_nodeid": "tests/unit/application/test_set_active.py::TestSetActiveApplication::test_set_active_is_selection_only_and_does_not_call_git_github_or_dependency_ports",
      "retirement_authority": "iss-00387 I387-R03/I387-R05/I387-R07; Design §5.3; Plan C20-04/C40-08/C40-09",
      "rationale": "旧EAL/Authorityまたはset_active内のforce/GitHub/dependency behaviorをCurrent selection-only/issue-start責務へ置換する。",
      "verification_owner": "current-surface-selection"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-import"
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
      "verification_owner": "runtime-shell"
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
      "verification_owner": "runtime-sync"
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
      "verification_owner": "runtime-sync"
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
      "verification_owner": "runtime-workbench"
    }
  ]
}
```
<!-- END ACTIVE_FAILURE_DISPOSITION_REGISTER_JSON -->

Canonical extractionは上記marker間の単一JSON fenceだけを対象とする。Duplicate marker、parse failure、schema/version mismatchはhard stop。

## 6. Verification commands

S00はsource commitとpost-#387 workspaceの両方を照合する。

```bash
python3 - <<'PY_VERIFY_REGISTER'
# Read the JSON between the exact BEGIN/END markers.
# Compare source row count/node/signature against:
#   git show "$REPOSITORY_EVIDENCE_SHA:full-regression-ledger.json"
# Compare current post-#387 ledger against expected_post_387.
# Exit nonzero on any new/missing/signature/lifecycle/successor mismatch.
PY_VERIFY_REGISTER
```

S60はtransitional ledger、all exact successors、normal-pass resultを確認する。S70はledger/test consumersをprovider moduleより先にretireする。

## 7. Owner decisions

`owner_decisions_required = []`。全27行のdispositionは本Artifactで決定済みである。
