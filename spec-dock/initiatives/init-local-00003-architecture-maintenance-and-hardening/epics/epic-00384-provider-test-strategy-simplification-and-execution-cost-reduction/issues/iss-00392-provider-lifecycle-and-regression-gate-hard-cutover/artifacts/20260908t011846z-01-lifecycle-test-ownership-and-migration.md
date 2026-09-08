---
種別: artifact
ID: "20260908t011846z-01"
タイトル: "ライフサイクルのテスト所有と移行対応"
状態: "approved"
作成者: "blue-team specification author"
最終更新: "2026-09-08"
親: ["iss-00392"]
template: "blank"
authority: "evidence"
derived_from:
  - "../../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../../artifacts/active-failure-disposition-register.md"
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "iss-00392-provider-lifecycle-and-regression-gate-hard-cutover"
  sha: "dc638e936e763cc7a6087f258201ed9ed654e7fb"
  tree: "17ce38234033393c385c4b17e40c0ccdc78bfc19"
---

# ライフサイクルのテスト所有と移行対応

## 1. 結論

#392のテスト移行は、旧テストを一括削除して新テストへ置き換える作業ではありません。現行nodeを次の三分類へ閉じ、新保証のRED→GREENが成立した後にだけ旧実装専用nodeを撤去します。

- **KEEP**: 受入動作、公開互換、保護データ、packaging、dogfood、required-fast、14 active baseline、resolved successorをそのnode identityまたは同一behavior keyで維持します。
- **REPLACE**: 受入意図は維持するが、旧per-file writer、旧journal、旧manifest、旧wrapper-return seamへのassertionを新lifecycleの観測へ置き換えます。置換先T-IDがGREENになるまで元nodeを削除しません。
- **RETIRE**: 旧ownerそのものの存在だけを要求するnodeです。置換先T-IDがGREEN、production参照0、whole-file classificationが完了した後にだけ削除します。

分類対象はverified commit `dc638e936e763cc7a6087f258201ed9ed654e7fb`に存在するtestsです。Ordered ruleを上から適用し、最初にmatchした規則を採用します。明示例外以外はKEEPです。CP4に追加するclassification registry testは、全collected nodeがexactly one ruleへ属し、0件のunclassified/overlapであることを要求します。

## 2. 不変の回帰gate

### 2.1 Required-fast four

次のnodeidをrename、削除、`full_regression`化、skip、xfailしません。

1. `tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess`
2. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets`
3. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
4. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_provider_only_workflow_is_not_shipped_via_install_root`

### 2.2 Full-regression baseline

Root ledgerのauthorityは`failure_paths`の15 exact rowsです。#392は14 activeのnodeid、signature、lifecycleを変更せず、1 resolved rowのsuccessor behaviorを維持します。Top-level historical 27件値をcurrent countに使用しません。`full-regression-timing-weights.json`の`node_seconds`は243 entriesのままです。

| # | Lifecycle | Exact nodeid | Signature SHA-256 | #392 rule / successor |
|---:|---|---|---|---|
| 1 | `active` | `tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active` | `0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f` | preserve-active-identity |
| 2 | `resolved` | `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source` | `8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637` | preserve-resolved-behavior; concrete successor may be mechanically rebound during lifecycle cutover<br>successor: `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` |
| 3 | `active` | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote` | `f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f` | preserve-active-identity |
| 4 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression` | `3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980` | preserve-active-identity |
| 5 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression` | `55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce` | preserve-active-identity |
| 6 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression` | `ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a` | preserve-active-identity |
| 7 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read` | `ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70` | preserve-active-identity |
| 8 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present` | `22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3` | preserve-active-identity |
| 9 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression` | `0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7` | preserve-active-identity |
| 10 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression` | `541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00` | preserve-active-identity |
| 11 | `active` | `tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam` | `44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd` | preserve-active-identity |
| 12 | `active` | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` | `0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790` | preserve-active-identity |
| 13 | `active` | `tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync` | `f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6` | preserve-active-identity |
| 14 | `active` | `tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root` | `3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619` | preserve-active-identity |
| 15 | `active` | `tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | `20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9` | preserve-active-identity |

## 3. Ordered classification registry

### Rule 1 — Baseline nodeidsはKEEP

前節15 rowのnodeidはすべてKEEPです。Resolved row #2の旧node自体は既にresolvedであり、実行保証はexact successor
`tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`
をKEEPします。Lifecycle cutoverに伴う機械的な観測先変更は、stable behavior key `provider-fixed-skill-slots-match-provider-and-dogfood`を保つ場合だけ許可します。

### Rule 2 — Required-fast nodeidsはKEEP

前節の四nodeをKEEPします。`tests/unit/infra/test_init_update.py`全体を削除・全置換してはなりません。

### Rule 3 — `tests/unit/infra/test_managed_distribution.py`

**File classification: REPLACE → conditional RETIRE.** 次のnode familyはすべてREPLACEです。

- `test_s20_*`, `test_s25_*`, `test_s30_*`, `test_s35_*`, `test_s40*`, `test_s45_*`, `test_s50_*`, `test_s55_*`, `test_s60_*`
- `test_i368_*`, `test_i369_*`, `test_i370_*`, `test_i371_*`, `test_i372_*`

置換先はT01–T07、T12、T14です。Current public catalog、unknown preservation、no-follow、native atomic、fresh/recovery/uninstall、CLI sole-ownerという**behavior**は残しますが、`DistributionPlan`、`OperationJournalStore`、`DistributionStageOwnership`、`.distribution-journal.json`、schema-2 forward guard、per-file checkpointを直接要求するassertionは残しません。

全nodeのsuccessorがGREENで、production import/callとdocs参照が0になった後、file全体にKEEP対象が残っていないことをclassification testで確認してRETIREします。一部nodeだけ先に削除しません。

### Rule 4 — `tests/unit/infra/test_init_update.py`

**File classification: KEEP with targeted REPLACE.**

KEEP:

- Required-fast 3 node。
- Package inventory、wheel/sdist/isolated installed resources、stale build prune、provider asset/dogfood parity。
- Authoring Kit、Artifact、rules、Workbench opacity、runtime command behaviorなどlifecycle非依存node。
- `test_issue_68_provider_only_workflow_is_not_shipped_via_install_root`が守るprovider-only workflow境界。

REPLACE:

- 旧version text `0.2.3
`、旧per-file managed catalog、旧manifest、旧journal/retry markerを直接生成・解釈するnode。
- Updateが`active`/`.agent`/initiativesを再構築することを要求するnode。新契約ではprotected dataであり、preserve-onlyへ置き換えます。
- `--remove-specs`成功、schema-1/2 recovery path、旧partial-rmtree結果を要求するuninstall node。T07のexit2/mutation0、tooling-only absent record、closed cleanupへ置き換えます。
- 旧runtime wrapperが外部processから戻ることを前提とするnode。T08/T09へ置き換えます。

RETIRE:

- Productionから削除されるprivate class/function名の存在だけをassertするnode。
- 旧`managed_distribution.json` inventoryのexact field setだけをassertするnode。

### Rule 5 — `tests/cli_runtime/test_distribution_cutover.py`

**File classification: KEEP with targeted REPLACE/RETIRE.**

KEEP:

- `test_s40b_provider_install_root_is_current_catalog_only`
- `test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`
- `test_s40b_legacy_bootstrap_and_skill_apply_paths_are_retired`
- Provider sourceとdogfood、installed runtime、current docs/skillsのbyte parityを守るnode。
- Unknown/unrelated path、initiatives、Workbenchの不変を観測するnode。ただし旧action vocabularyではなくbytes/type/inode witnessで観測します。

REPLACE:

- `_exclusive_distribution_operation`のthread-local behaviorだけを観測するnode → T08/T09 real-process SH/EXへ。
- `.distribution-retry.json`、`.distribution-journal.json`、`.uninstall-retry.json`をcurrent authorityにするnode → T04/T06/T07へ。
- Fresh/update/uninstallのper-file action/status、active fallback再構築、safe-subset applyを要求するnode → fixed root exchangeとprotected preservationへ。
- `execute_fresh_distribution`、`execute_recognized_distribution`、`execute_deprovision_distribution`等の旧service routeをassertするnode → `execute_provider_lifecycle` sole routeへ。

RETIRE:

- Resolved historical node `test_s40b_retained_skill_identity_matches_issue359_final_source`はledger上resolvedのまま実行対象に戻しません。
- 旧writer/journal class名だけを禁止/許可するnodeはT12のproduction-reference-zero testへ統合後に削除します。

### Rule 6 — Runtime update/uninstall tests

`tests/cli_runtime/test_update.py`:

| Current node | Classification | Successor / retained behavior |
|---|---|---|
| `TestUpdateCommand::test_update_help_describes_upstream_no_cache_and_default_target` | KEEP+wording update | Fixed upstream/no-cache/default targetを維持。terminal execを説明。 |
| `::test_update_runs_uvx_no_cache_with_default_target` | REPLACE | T09: release-to-exec、argv exact、old-module return 0。 |
| `::test_update_passes_explicit_target_to_installer_update` | REPLACE | T09: cross-target B admission、A release。 |
| `::test_update_propagates_subprocess_failure_output_and_exit_code` | REPLACE | T09: direct inherited streams/status、no capture/reprint。 |
| `::test_update_missing_uvx_fails_with_actionable_error` | REPLACE | T09: exact 127 diagnostic from frozen bootstrap。 |
| `::test_update_rejects_force_option` | KEEP | Unsupported override rejection。 |
| `::test_update_rejects_source_and_cache_overrides_without_invoking_uvx` | KEEP | Fixed upstream、mutation 0。 |

`tests/cli_runtime/test_uninstall.py`:

| Current node | Classification | Successor / retained behavior |
|---|---|---|
| `TestUninstallCommand::test_uninstall_help_describes_upstream_no_cache_and_default_target` | KEEP+wording update | Fixed upstream/default target、tooling-only semantics。 |
| `::test_uninstall_runs_uvx_no_cache_with_default_target` | REPLACE | T09 release-to-exec。 |
| `::test_uninstall_passes_explicit_target_to_installer_uninstall` | REPLACE | T09 cross-target。 |
| `::test_uninstall_forwards_apply_keep_specs_and_propagates_failure_output` | REPLACE | T09 direct streams/status。 |
| `::test_uninstall_forwards_remove_specs_flag` | RETIRE | T07: `--remove-specs` exit2/mutation0。 |
| `::test_uninstall_forwards_json_and_preserves_json_stdout` | REPLACE | T09: child JSON stdout byte-preserving terminal exec。 |
| `::test_uninstall_missing_uvx_fails_with_actionable_error` | REPLACE | T09 exact 127。 |
| `::test_uninstall_rejects_source_and_cache_overrides_without_invoking_uvx` | KEEP | Fixed source/cache policy。 |

### Rule 7 — Runtime bootstrap/wrapper tests

`tests/cli_runtime/test_wrappers.py`はKEEP with one REPLACEです。

- Rules symlink、Artifact numbering、unsafe Artifact directory testsはKEEP。
- `TestCliRulesContract::test_runtime_entrypoint_fails_fast_when_runtime_module_missing`はREPLACEし、T08でmodule pathを読む前にSH leaseとstrict ready admissionが完了すること、module missing時もprivate/Consumer write 0を検証します。

新規`tests/cli_runtime/test_provider_lifecycle_bootstrap.py`はT08、`tests/cli_runtime/test_provider_lifecycle_handoff.py`はT09を所有します。

### Rule 8 — Checkout、issue lifecycle、worktree、make

- `tests/unit/application/test_set_active.py`と`tests/cli_runtime/test_active.py`: KEEP。Existing selection-only behaviorを維持し、checkoutを行うpathだけT10 assertionを追加します。
- `tests/cli_runtime/test_issue_lifecycle.py`: KEEP。`issue start` node identityを保ち、checkout前pin、post-drift active/sync 0をT10へ追加します。`issue finish`はcheckoutしないためlifecycle generation guardを新設しません。
- `tests/unit/application/test_workbench.py`、`tests/cli_runtime/test_workbench.py`: KEEP。Baseline row #15を変更しません。
- `tests/cli_runtime/test_worktree.py`: KEEP ordinary list/show/remove guards。Create/remove/bootstrapの旧path-based nodeはREPLACEし、T11でB EX、entrypoint-last、path C preservation、terminal hookを検証します。
- `tests/unit/infra`のGit CLI tests: KEEP ordinary Git validation。Direct `checkout_branch`/`create_and_checkout_branch`/`add_worktree_with_new_branch`/`remove_worktree` seamはT10/T11のpin/helper/capability APIへREPLACEします。
- `src/.../infra/make_cli.py`に対応するtest: make detection/status classifierはKEEP、process実行とcwdはT11のfrozen bootstrap testへREPLACEします。

### Rule 9 — Integration/public compatibility

- `tests/integration/test_epic_00343_distribution.py`: KEEP file。公開init/update/uninstall、provider assets、package boundaryの受入意図を新record/root semanticsへ更新します。Old journal/per-file action assertionだけREPLACEします。
- `tests/cli_runtime/test_import.py`、`test_runtime_import_s10.py`、`test_runtime_shell_s11.py`、`test_sync.py`、`test_delete.py`: 前節baseline nodeidsをKEEPし、#392でその失敗を修正しません。Coordination/bootstrap変更に必要なtest harness追随は、signature/lifecycleを変えずnormal behaviorを壊さない範囲だけです。
- その他の`tests/unit/**`、`tests/cli_runtime/**`、`tests/integration/**`: Default KEEP。#392に無関係なrename、assertion弱化、lane変更をしません。

## 4. New test IDs and exact owners

| T-ID | Checkpoint owner | Exact primary node | Requirement proof |
|---|---|---|---|
| T01 | CP1 | `tests/unit/provider_lifecycle/test_wire.py::test_t01_wire_v12_inventory_and_generated_projection_are_exact` | 6/41/23/24/168/40/4、relation closure、generation determinism。 |
| T02 | CP1 | `tests/unit/provider_lifecycle/test_candidate.py::test_t02_candidate_record_marker_and_legacy_fixture_are_closed_and_deterministic` | Candidate digest、7-key record、4-key marker、exact-clean 0.2.3 fixture。 |
| T03 | CP1 | `tests/unit/provider_lifecycle/test_authority.py::test_t03_fixed_roots_slots_seeds_and_protected_sentinels_are_exact` | Four roots、two slots、fresh-only seeds、protected data、unknown preservation。 |
| T04 | CP1 | `tests/unit/provider_lifecycle/test_private_state.py::test_t04_prepared_active_precedes_stage_and_p1_only_rebuilds_registered_entries` | Private namespace、closed rendered-command allowlist、RECORD-TEMP witness、ACTIVE/receipt/inode schema、P0/P1/P2。 |
| T05 | CP1 | `tests/unit/provider_lifecycle/test_atomic_filesystem.py::test_t05_linux_and_macos_native_atomic_adapters_have_no_unsafe_fallback` | Native no-replace/exchange、RECORD-TEMP/public record mode0644保存、no-follow、identity drift、fsync。 |
| T06 | CP2 | `tests/unit/provider_lifecycle/test_engine.py::test_t06_all_fixed_fault_boundaries_converge_to_wire_continuations` | Write order、record exchange residue、root interruption、terminal/cleanup/receipt/replay、response loss。 |
| T07 | CP2 | `tests/unit/provider_lifecycle/test_engine.py::test_t07_legacy_migration_uninstall_and_old_package_mutation_zero` | Exact migration、tooling-absent record、purge rejection、old-package guard。 |
| T08 | CP3 | `tests/cli_runtime/test_provider_lifecycle_bootstrap.py::test_t08_pre_import_shared_lease_and_ready_admission_are_enforced` | Stdlib bootstrap、SH/NB、busy/not-ready/unsafe/unavailable、no pre-admission import。 |
| T09 | CP3 | `tests/cli_runtime/test_provider_lifecycle_handoff.py::test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal` | Release-to-exec、streams/status/127、pass_fds、parent-only SIGKILL。 |
| T10 | CP3 | `tests/cli_runtime/test_generation_checkout.py::test_t10_existing_and_new_checkout_are_pinned_and_generation_safe` | Existing/new branch pin、三種のwriting hookを含むcapability guard、pre/post drift、normal Git guard維持。 |
| T11 | CP3 | `tests/cli_runtime/test_worktree_lifecycle_coordination.py::test_t11_worktree_b_create_remove_and_make_handoff_are_inode_bound` | B EX、entrypoint-last、path C preservation、nonlocking B fd、make compatibility。 |
| T12 | CP2 | `tests/integration/test_issue_392_acceptance.py::test_t12_public_cli_uses_only_new_lifecycle_and_old_writer_is_absent` | Sole route、old module/manifest/journal references 0、public compatibility。 |
| T13 | CP4 | `tests/integration/test_provider_lifecycle_dogfood.py::test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical` | Provider-first、package inventory、bootstrap/fixture/docs/skills/fresh install/dogfood parity。 |
| T14 | CP4 | `tests/integration/test_issue_392_acceptance.py::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged` | Required-fast、15/14/1、243、provider CI、#395/#396 no-touch。 |

各primary nodeはparameterized subcaseを持てますが、T-IDの責務を別Issueへ分けません。Fault/platform evidenceは同T-IDのsubcaseまたは同file内の補助nodeに置きます。

## 5. Fault evidence matrix

| Boundary | Required injection | Required observation |
|---|---|---|
| Private parent/open/mkdir/chmod/fsync | errno別P0 | Consumer write 0、trusted ACTIVEなし、retryなし。 |
| ACTIVE temp write/fsync/rename/parent fsync | rename前/後 | foreign tempを削除せず、durable preparedを一意判定。 |
| Stage owner/payload create/copy/fsync | 各fixed entry | P1だけregistered entry再構築、P2 stage bytes/inode unchanged。 |
| Incomplete record temp/write/rename/fsync | 各点 | Originalまたはown expected incompleteだけを許容。 |
| Record no-replace/exchange/residue | 各publish境界とparent fsync loss | Public/temp mode0644、exchange後旧recordはoriginal bytes/hash/inode一致時だけcleanup。 |
| Each root detach/publish | docs/templates/system/scripts | Scripts last、re-entryがtarget/stage identityから一意。 |
| Each skill slot detach/publish | two exact slots | Marker authority、other skill/parent scan 0。 |
| Seed create | container/file/fsync | Missing+create-if-absentのみ。既存seed unchanged。 |
| ACTIVE ready/terminal record | before/after publication | ready先行、same candidate updateを誤完了認定しない。 |
| Stage removal/receipt/ACTIVE unlink | unlink/fsync/response loss | Token replay idempotent、deferred request自動実行なし。 |
| Native rename capability | ENOSYS/EINVAL/unsupported | Unsafe fallback 0、closed failure。 |
| Helper parent SIGKILL | parent only | Descendant last writeまでEX busy、終了後admit。 |
| Git writing hook capability | executable `post-checkout` / `reference-transaction` / `post-index-change` | 設定変更せずpre-mutation block、checkout/active/sync 0。 |
| Checkout drift | pre/post | Preはcheckout 0、postはbranch side effectを報告しactive/sync 0。 |
| Worktree create/remove | each Git/helper/fsync boundary | B entrypoint未公開またはready、C preserved。 |
| Make detect/run | missing/fail/nested installer | Lock fd 0、original B cwd、outer status compatibility。 |

## 6. Concurrency and platform matrix

| Scenario | Linux | macOS | Proof |
|---|---:|---:|---|
| Two runtime SH leases coexist | required | required | Real subprocess。 |
| Installer EX while SH alive is busy | required | required | Nonblocking flock。 |
| Runtime SH while EX alive is busy/not-ready | required | required | Import spy remains 0。 |
| Helper inherited SH survives parent-only SIGKILL | required | required | `pass_fds` and open-file-description lifetime。 |
| Native no-replace/exchange | `renameat2` | `renameatx_np` | Real filesystem, not monkeypatch only。 |
| Root/slot identity drift | required | required | Before every mutation and post-publication verify。 |
| Worktree B path reused as C | required | required | C bytes/type/inode unchanged。 |
| Hook nested installer after lease release | required | required | No self-contention。 |

Windowsは#392 supported lifecycle platformではありません。Silent path-based fallbackを追加せず、unsupported platformはWireのclosed failureです。

## 7. Packaging and dogfood evidence

T13は同一build sessionで次を採取し、aggregate candidate digest、six domain digests、fixture bytes、frozen bootstrap SHA-256、two skill tree digestsを比較します。

CP3のT08–T11はprovider asset treeまたはそこから作ったtemporary installを対象とし、checked-in dogfood parityを前提にしません。CP4でcomplete provider candidateを確定しsource testsをGREENにした後、同一source treeからartifact proofを取り、そのproofがGREENになった後だけdogfoodを一括projectします。

1. Source tree。
2. Built wheel。
3. Built sdist。
4. Wheelだけを入れたisolated installed environment。Checkout pathを`sys.path`へ入れません。
5. Checked-in dogfood `spec-dock/`と`.agents/skills/{spec-dock,spec-dock-grill-with-docs}`。
6. Fresh install output。

Wheel/sdistはlegacy fixture、new package、runtime bootstrapを欠いてはなりません。Build stagingのstale旧writer/manifestがartifactへ混入しないnegative proofを含めます。

## 8. Migration order and deletion rule

1. T01–T05をREDにする。
2. Foundation実装でGREENにする。
3. T06/T07をRED→GREENにし、新installer public routeを通す。
4. CP2で`tests/integration/test_issue_392_acceptance.py`を作成し、T12のold production reference scanをGREENにする。
5. その後にだけ`managed_distribution.py`、`managed_distribution.json`、旧writer専用testsを削除する。
6. T08–T11をRED→GREENにする。
7. CP4で同じacceptance fileへT14だけを追加し、artifact proof後にcomplete dogfoodを一括projectしてT13/T14をGREENにし、既存KEEP nodeを実行する。
8. Default fast、current full verifier、Linux/macOS provider parityがGREENになって初めてPR受入候補とする。

削除が先行した場合はstopです。Successor testを同じcommitで追加していても、そのtestの実行証拠がなければ削除を正当化しません。

## 9. Provider CI rule

`.github/workflows/provider-ci.yml`はPR-only、`provider-tests`、Linux/macOS `provider-distribution-parity`、candidate SHA checkout/assert、no `continue-on-error`を維持します。旧focused commandを次へ差し替えます。

```bash
uv run pytest tests/unit/provider_lifecycle
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
```

T08–T11のreal concurrency/platform nodesが別fileにある場合、同jobへ明示追加します。`uv run pytest` default laneと`uv run python -m scripts.quality.verify_full_regression --shards 4`は維持します。

## 10. Completion evidence

#392のテスト移行完了は次を一つのReport evidence blockで示します。

- Classification registry: unclassified=0、overlap=0、prematurely_retired=0。
- T01–T14: all pass。
- Required-fast: exact four present and pass。
- Ledger: total15/active14/resolved1、active nodeid/signature/lifecycle unchanged、resolved successor present/pass。
- Timing: 243 entries unchanged。
- Default fast/current full/focused Linux/macOS/package/dogfood: exit0。
- Unexpected failure/error/skip/xfail/approved failure additions: 0。
- Old production writer/manifest/current-authority references: 0。

現時点ではこれらProduct testsを実行していません。本Artifactは移行契約であり、GREEN証拠ではありません。
