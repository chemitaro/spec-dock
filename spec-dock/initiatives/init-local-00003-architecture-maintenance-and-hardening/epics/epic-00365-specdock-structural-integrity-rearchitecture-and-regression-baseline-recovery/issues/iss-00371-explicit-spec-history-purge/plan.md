---
種別: 実装計画書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-28"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## 1. Planning Level

**selected level: `strict`**

理由:

- `spec-dock/initiatives` の不可逆削除を扱う。
- public CLI/JSON/text/exit compatibilityを維持する。
- intent/authority non-escalationをjournal recoveryまで証明する。
- partial recursive deletionをsame-plan forward recoveryへ収束させる。
- legacy `.uninstall-retry.json` の情報不足を推測で補わない。
- Issue 370のcommon writerへhard cutoverし、old writerを同じIssueで削除する。

`critical`へ再評価して実装を停止する条件:

- exact `spec-dock/initiatives` 外またはrepository外を削除し得る。
- history subtreeのsymlink/hardlink/specialを安全確認なしで削除する必要が生じる。
- pre-write blockerがある状態でsafe subset mutationを許可しなければacceptanceを満たせない。
- dry-runまたはblocker resultでtarget/guard/journal/stage writeが発生する。
- old/new writerを同時にproduction有効にする必要が生じる。
- journal recoveryにintent/authority/root/planの推測が必要になる。
- approved Full Regression failure ledgerまたはverifier semanticsを変更しなければ通らない。

## 2. Baseline

実装開始点を次へ固定する。

| 項目 | baseline |
|---|---|
| repository | `chemitaro/spec-dock` |
| branch | `iss-00371-explicit-spec-history-purge` |
| verified SHA | `94546a138bd34b253c87ca8749f3c5678d172f2a` |
| package version | `0.2.3` |
| Python | `>=3.10` |
| Issue 370 status | complete / merged; common deprovision assessment, action kernel, journal, result, mapper成立済み |

実装者は作業開始時に次を再確認する。

```bash
git rev-parse HEAD
git status --short
```

`git rev-parse HEAD` がbaseline SHAでない場合、baseline差分を独自解釈せず作業を停止する。working treeがdirtyの場合は、Issue 371と無関係な差分を混在させない。

## 3. Single production writer rule

production codeの編集ownerは一人・一つのimplementation sessionとする。`src/spec_dock/managed_distribution.py` と `src/spec_dock/cli.py` のwriter変更を複数agentへ並列委任しない。

許可する並行作業はread-only reviewまたはtest evidence収集だけである。production filesystem writerの変更順は必ず次とする。

1. current behavior characterization tests
2. intent/guard/domain extension
3. read-only purge contract/assessment
4. common journal/recovery/service
5. CLI typed result cutover
6. old writer physical deletion
7. docs/verification

old routeを削除する前にnew routeのfocused greenを得るが、old/new routeを選択するruntime flag、environment toggle、fallbackは作らない。中間commitでold writerが存在してもproduction dispatchは一度にnew serviceへ切り替え、同じIssueの次commitまたは同commitでold writerを削除する。release可能な状態にdual writerを残さない。

## 4. Expected file ownership

### 4.1 Production files

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/cli.py`
- `README.md`

### 4.2 Test files

- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_distribution_cutover.py`

### 4.3 Canonical Issue files

- Issue 371 `requirement.md`
- Issue 371 `design.md`
- Issue 371 `plan.md`
- implementation完了時はcanonical Issue directoryに`report.md`を作成し、candidate SHAと実施evidenceを記録する。本ZIPはimplementation前authoringであるため`report.md`を含めない。

### 4.4 変更禁止

- `spec-dock/initiatives/.../iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-ledger.json`
- `verify-full-regression.py` のfailure判定、ledger照合、timeout semantics
- Full Regressionを通すためのtest skip、xfail、expectation緩和
- public argparse command/flag/schema
- Issue 370のapproved evidence

## 5. Step 0 — Baseline characterizationをredで固定する

### 5.1 目的

current exact behaviorとcutover seamをtestsで固定し、実装中にpublic compatibilityまたはauthority boundaryを推測しない状態にする。このstepはproduction codeを変更しない。

### 5.2 Production ownership

production edit: 0。test filesのみをsingle writerが編集する。

### 5.3 対象

`tests/unit/infra/test_init_update.py`

- current test `test_i370_uninstall_cli_maps_six_typed_deprovision_rows_and_one_remove_route` をIssue 371 red contractへ展開する。
- remove dry/applyがcurrent `_run_uninstall_remove_specs_compatibility()`へ到達することをbaseline assertionとして一時的に記録し、new service expectationをredにする。
- public `spec_history` path/category/reason、schema field set、exitをcharacterizeする。

`tests/cli_runtime/test_distribution_cutover.py`

- current old symbolsが存在することをbaseline evidenceとして確認する。
- target assertionはold symbols absent/new service reachableでredにする。

`tests/unit/infra/test_managed_distribution.py`

- `JournaledDistributionIntent` がまだ`purge`を受理しないことを確認し、new contract/service testsをredで追加する。

### 5.4 Red tests

追加するexact test names:

```text
test_i371_uninstall_cli_routes_remove_dry_run_to_typed_purge_service
test_i371_uninstall_cli_routes_remove_apply_to_locked_typed_purge_service
test_i371_uninstall_cli_never_escalates_default_keep_update_or_init_to_purge
test_i371_uninstall_public_remove_specs_contract_is_schema_one_root_aggregated
test_i371_distribution_cutover_has_no_legacy_remove_specs_writer
test_i371_purge_contract_binds_exact_history_root_and_authority
```

red acceptance:

- route testsはnew service symbol不存在またはold route呼出しにより失敗する。
- cutover absence testはold symbols存在により失敗する。
- contract testはnew dataclass/builder不存在により失敗する。
-既存 testsのexpectationを緩めてredを消さない。

### 5.5 Characterization command

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'i371 or uninstall or remove_specs' -q
uv run pytest tests/cli_runtime/test_distribution_cutover.py -k 'i371 or uninstall' -q
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i371 or deprovision' -q
```

### 5.6 Minimal change boundary

- production import、type、route、filesystem behaviorを変更しない。
- public goldenをcurrent outputから抽出するが、absolute temp pathやnondeterministic timestampをgoldenに含めない。

### 5.7 禁止事項

- current old behaviorをcanonical targetとしてそのままgreenにすること。
- test monkeypatchだけでnew serviceを偽装すること。
- legacy marker fixtureを削除すること。

### 5.8 Stop conditions

- current public schema/exit/categoryを一意にcharacterizeできない。
- current route matrixがbaseline sourceと一致しない。
- test fixtureがtarget outside pathを変更する。

## 6. Step 1 — Intent、authority、guard、retry policyを追加する

### 6.1 目的

filesystem mutationをまだ追加せず、current journal protocolにpurge discriminantを導入する。

### 6.2 Production ownership

single writerが `src/spec_dock/managed_distribution.py` だけを編集する。`cli.py` dispatchはまだ変更しない。

### 6.3 変更symbol

- `JournaledDistributionIntent`
- `DistributionRetryPolicy`
- `DistributionRetryMarker.operation` / purpose type
- `_DISTRIBUTION_PURGE_JOURNAL_GUARD_PURPOSE`
- `_DISTRIBUTION_JOURNAL_AUTHORITIES`
- `_journal_guard_purpose_for_intent()`
- `_journal_authority_for_intent()`
- `_plan_operation_for_intent()`
- `_intent_allows_distribution_action()`
- `_read_distribution_retry_marker()`
- journal parser/serializerのintent/purpose validation

### 6.4 Red tests

`tests/unit/infra/test_managed_distribution.py`:

```text
test_i371_purge_intent_maps_only_to_uninstall_action_grammar
test_i371_purge_guard_purpose_maps_to_exact_authority
test_i371_purge_guard_rejects_deprovision_purpose_operation_pair
test_i371_deprovision_guard_rejects_purge_purpose_operation_pair
test_i371_purge_marker_round_trip_preserves_existing_schema_two_field_set
test_i371_retry_policy_distinguishes_same_remove_from_same_keep
```

red acceptance:

- `purge` literalがunsupportedで失敗する。
- purpose/authority mapping不存在で失敗する。
- marker field setを増やす実装はtestで失敗する。

### 6.5 Implementation

1. `purge` literalをdomainへ追加する。
2. `purge`を`uninstall` operationへmapする。
3. allowed action grammarをdestructive subsetへ限定する。
4. guard purpose/authority mappingを追加する。
5. marker parserのsupported purpose/operation pairを追加する。
6. retry policy `same-remove-command`を追加する。
7. existing deprovision/fresh/update/init marker round-tripを再実行する。

### 6.6 Green acceptance

- new intent/guard tests green。
- existing marker parser tests green。
- journal schema version、protocol version、guard schema versionの値不変。
- serialized field names不変。
- `purge` guardをdeprovision routeが受理しない。

### 6.7 Focused command

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i371 and (intent or guard or marker or authority or retry_policy)' -q
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'journal or guard or marker' -q
```

### 6.8 Minimal change boundary

- new contract/assessment/service/CLI routeをまだ追加しない。
- current `_DISTRIBUTION_JOURNAL_AUTHORITIES` のexisting valuesを変更しない。

### 6.9 禁止事項

- new journal/marker fileを追加する。
- authorityをCLI引数またはcaller stringにする。
- marker schema versionを上げる。
- unknown purposeをlenientに受理する。

### 6.10 Stop conditions

- current schema field shapeではintent/authority mismatchをfail closedにできない。
- deprovision guardがpurgeとしてresume可能になる。
- existing fresh/update/init/deprovision parser regressionが発生する。

## 7. Step 2 — Read-only purge contractとassessmentを実装する

### 7.1 目的

mutation/journal writeなしで、exact history root、deprovision component、preservation、blocker、action/witnessを一つの`WorkspaceAssessment(intent="purge")`へ構築する。

### 7.2 Production ownership

single writerが `src/spec_dock/managed_distribution.py` を編集する。CLI dispatchとlegacy writerはまだ変更しない。

### 7.3 追加・変更symbol

追加:

- `DistributionExplicitSpecHistoryPurgeContract`
- `_build_deprovision_contract(..., preserved_roots=...)`
- `_capture_distribution_tree()`
- `build_explicit_spec_history_purge_contract()`
- `build_explicit_spec_history_purge_assessment()`
- purge tree digest helper
- purge action/reason validators

変更:

- `build_deprovision_contract()` はprivate factory wrapperへし、signature/behavior不変
- `_capture_preservation_witness()` はcommon capture helperを使用し、behavior不変
- `WorkspaceAssessment` にoptional purge contract field
- deprovision tree augmentation private seamに`additional_managed_roots/actions/snapshots`のempty-default input
- `build_executable_mutation_plan()` のpurge domain validation
- destructive action condition common body + purge wrapper

### 7.4 Red tests: contract

`tests/unit/infra/test_managed_distribution.py`:

```text
test_i371_purge_contract_binds_exact_history_root_and_authority
test_i371_purge_contract_preserves_only_workbench_in_component
test_i371_purge_contract_digest_changes_on_history_identity_change
test_i371_purge_contract_rejects_noncanonical_history_root_override
test_i371_deprovision_contract_preserved_roots_are_unchanged
```

### 7.5 Red tests: tree policy

```text
test_i371_purge_assessment_authorizes_unknown_regular_history_content
test_i371_purge_assessment_orders_history_directories_deepest_first
test_i371_purge_assessment_blocks_history_root_symlink_without_writes
test_i371_purge_assessment_blocks_history_child_symlink_without_writes
test_i371_purge_assessment_blocks_history_hardlink_without_writes
test_i371_purge_assessment_blocks_history_special_file_without_writes
test_i371_purge_assessment_blocks_unreadable_or_rebound_history_entry
test_i371_purge_assessment_preserves_workbench_and_outside_sentinel
test_i371_purge_assessment_combines_component_blocker_operation_wide
test_i371_purge_assessment_records_absent_history_witness_without_actions
```

### 7.6 Implementation order

1. current `build_deprovision_contract()` bodyをprivate factoryへ抽出する。
2. deprovision wrapperがexact existing preserved rootsを渡すことをtestで固定する。
3. current preservation walkerのnested traversalを`_capture_distribution_tree()`へ抽出する。
4. preservation wrapperのbefore/after result equalityをtestする。
5. purge policyを固定してcontract builderを追加する。
6. history regular leaf snapshots/actionsを作る。
7. history directory snapshots/immediate child evidence/actionsを作る。
8. combined deprovision + history action setを一度のtree augmentationへ渡す。
9. `.workbench` preservation witnessとhistory absence witnessを付与する。
10. blockerを統合する。
11. executable plan validationを追加する。

### 7.7 Green acceptance

- arbitrary regular history contentがcatalogなしで`prune`になる。
- symlink/hardlink/special/unreadableはblockerでaction authorityを得ない。
- blocker mixed fixtureでexecutable planを発行しない。
- all history actionsはexact root配下。
- component actionsはIssue 370 semanticsと同じ。
- `.workbench` witnessが存在し、history preservation witnessは存在しない。
- absent historyはmutating action 0 + absence witness。
- production write spyが0。

### 7.8 Focused command

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i371 and (contract or assessment or history or blocker or witness)' -q
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'deprovision_contract or preservation or collapsed_absence or directory' -q
```

### 7.9 Minimal change boundary

- apply service/journal/checkpoint/CLIをまだ変更しない。
- existing generated-state authority、provider source semantics、manifest catalogを変更しない。
- history contentをmanifestへ追加しない。

### 7.10 禁止事項

- generic caller-provided allowed roots。
- symlink leafをunlink authorityへ変換する。
- hardlink peerを許可する。
- unknown siblingをhistory rootへprefix推定する。
- blockerをaction listから除外してsafe subset planを作る。
- dry-runでguard/journalをprepareする。

### 7.11 Stop conditions

- current `_remove_distribution_directory_if_bound()` が要求するdirectory evidenceをhistory treeから生成できない。
- component tree augmentationとhistory parent cleanupが一つのaction graphへ統合できない。
- `.workbench` preservationとhistory removalが同じpath evidenceへ二重分類される。

## 8. Step 3 — Common journaled purge serviceとforward recoveryを実装する

### 8.1 目的

Issue 370のsingle writer/state machineへpurgeを追加し、partial deletionをjournalから再構成してforward recoveryする。

### 8.2 Production ownership

single writerが `src/spec_dock/managed_distribution.py` を編集する。CLI old routeはまだdispatch ownerだがnew serviceを直接unit testする。new/old writerを同じtest invocationで一つのtargetへ実行しない。

### 8.3 追加・変更symbol

追加:

- `execute_explicit_spec_history_purge_distribution()`
- `_execute_destructive_distribution()`
- `_reconstruct_explicit_spec_history_purge_contract()`
- `_validate_explicit_spec_history_purge_recovery_action_semantics()`
- purge result/outcome aggregation helper
- purge-specific request/service error codes

変更:

- `execute_deprovision_distribution()` をcommon executor wrapperへするがsignature/behavior不変
- deprovision recovery hard-coded intent/authority validatorsをdestructive intent parameterized private bodyへ抽出
- current journal compatibility gateへpurge discriminant追加
- action dispatcherへpurge context追加
- result populationへ`intent="purge"`、`same-remove-command`追加

### 8.4 Red tests: dry-run/pre-write

```text
test_i371_purge_service_dry_run_is_byte_and_metadata_write_free
test_i371_purge_service_prewrite_history_blocker_writes_nothing
test_i371_purge_service_prewrite_component_blocker_writes_nothing
test_i371_purge_service_noop_writes_no_guard_journal_or_stage
test_i371_purge_service_guard_publish_failure_mutates_no_target
test_i371_purge_service_journal_prepare_failure_mutates_no_target
```

write spy対象:

- target tree
- `.distribution-retry.json`
- `.distribution-journal.json`
- `.uninstall-retry.json`
- stage/quarantine entry
- directory create/remove
- chmod/replace/rename/unlink/rmdir/fsync side effect

### 8.5 Red tests: kernel safety

```text
test_i371_purge_apply_removes_regular_history_and_owned_component
test_i371_purge_apply_revalidates_root_before_first_mutation
test_i371_purge_apply_revalidates_each_parent_before_leaf_mutation
test_i371_purge_apply_revalidates_leaf_identity_and_sha_before_unlink
test_i371_purge_apply_revalidates_directory_child_digest_before_rmdir
test_i371_purge_directory_recovery_accepts_only_authorized_parent_ctime_and_link_count_transition
test_i371_purge_apply_stops_on_root_rebind
test_i371_purge_apply_stops_on_parent_rebind
test_i371_purge_apply_stops_on_child_rewrite
test_i371_purge_apply_stops_on_unknown_child_appearance
test_i371_purge_apply_never_mutates_symlink_target_or_hardlink_peer
```

### 8.6 Red tests: recovery

```text
test_i371_purge_journal_binds_exact_intent_authority_contract_and_plan
test_i371_purge_forward_recovers_same_plan_after_leaf_checkpoint_failure
test_i371_purge_forward_recovers_same_plan_after_directory_checkpoint_failure
test_i371_purge_reconstructs_deleted_history_from_journal_preconditions
test_i371_purge_rejects_deprovision_journal_without_checkpoint_progress
test_i371_deprovision_rejects_purge_journal_without_checkpoint_progress
test_i371_update_and_init_reject_purge_recovery_state
test_i371_purge_rejects_changed_history_plan_without_new_authority
test_i371_purge_rejects_different_root_or_contract
test_i371_purge_rejects_nonterminal_journal_without_matching_guard
test_i371_purge_completed_journal_cleanup_does_not_reexecute_target_actions
```

### 8.7 Red tests: legacy marker

```text
test_i371_purge_valid_legacy_marker_requires_manual_recovery_and_writes_nothing
test_i371_purge_copied_legacy_marker_does_not_gain_root_or_remove_authority
test_i371_purge_invalid_legacy_marker_errors_and_writes_nothing
test_i371_purge_symlinked_hardlinked_or_special_legacy_marker_is_invalid
test_i371_purge_legacy_marker_plus_new_journal_advances_neither_state
```

### 8.8 Implementation order

1. current `execute_deprovision_distribution()` orchestrationを`_execute_destructive_distribution(intent)`へextractする。
2. deprovision wrapper/testsをgreenに戻し、behavior diff 0を確認する。
3. purge wrapperを追加し、dry-run pathだけgreenにする。
4. blocker gateをjournal prepare前に共通化する。
5. purge guard/journal prepareを追加する。
6. existing `_execute_journaled_action()` へhistory regular/directory actionsを流す。
7. root/parent/leaf/directory revalidation hooksをpurge intentでも有効化する。
8. purge semantic recovery validatorを追加する。
9. partial history contractをjournal preconditionsからreconstructする。
10. same-plan checkpoint resumeを追加する。
11. public-oriented root outcome aggregationを`DistributionProcessResult.action_outcomes`生成時に追加する。
12. legacy marker/dual stateのtyped resultをpurge serviceへ適用する。
13. terminal post-assessment/finalizationを追加する。

### 8.9 Green acceptance

- dry-run/write0、pre-write blocker/write0、no-op/write0がすべてgreen。
- normal applyでhistory root absent、component postcondition完了、`.workbench`/outside sentinel不変。
- interruption後にsame explicit planだけがforward recoveryする。
- already published actionを再unlinkしない。
- history deletion後もjournal preconditionからoriginal planをreconstructできる。
- cross-intent/authority/plan/rootでcheckpoint進行0。
- legacy marker stateを変更しない。
- deprovision existing focused suite green。

### 8.10 Focused command

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i371 and (service or apply or recovery or journal or legacy or rebind)' -q
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i370 or deprovision or journal or recovery or kernel' -q
```

### 8.11 Minimal change boundary

- action/journal/resultのnew parallel typeを作らない。
- current schema/protocol versionを変更しない。
- fresh/update/init-force orchestrationをdestructive executorへ移さない。
- Issue 370 semantic source/generated state contractを変更しない。

### 8.12 禁止事項

- recovery時にcurrent treeからmissing deleted actionsを推測する。
- journal planをcurrent treeに合わせてrewriteする。
- deprovision journalをpurgeへupgradeする。
- purge guardだけでCLI explicitnessを代替する。
- failure時にjournal/guardを無条件削除する。
- deleted historyをpackage assetsから再作成する。

### 8.13 Stop conditions

- partial deletionからoriginal action graphをjournalだけでlossless再構成できない。
- common kernelを使用せずrecursive purge writerが必要になる。
- same-plan recoveryにnew public token/flagが必要になる。
- deprovision existing recovery regressionが残る。

## 9. Step 4 — CLI typed result hard cutoverを実装する

### 9.1 目的

remove dry/applyをnew serviceへdispatchし、public JSON/text/exit/retryをtyped resultだけから生成する。

### 9.2 Production ownership

single writerが `src/spec_dock/cli.py` を編集する。`managed_distribution.py` serviceがfocused green済みであることを前提とする。

### 9.3 追加・変更symbol

追加:

- import `execute_explicit_spec_history_purge_distribution`
- `_run_uninstall_explicit_spec_history_purge()`
- `_purge_request_error_result()`
- purge public error mappings

変更:

- `_run_uninstall()` dispatch
- `_emit_uninstall_deprovision_result()` → `_emit_uninstall_result()`
- `_validate_uninstall_process_result(result, specs_mode=...)`
- `_uninstall_payload_from_result()`
- `_uninstall_guidance_from_result()`
- retry command projection
- generic operation/action error mapping

維持:

- `_uninstall_retry_command()`
- `_uninstall_exit_code_from_result()`
- `_summarize_uninstall_outcomes()`
- `_render_uninstall_text()`
- argparse grammar

### 9.4 Red route matrix

`tests/unit/infra/test_init_update.py` に8-row matrixを固定する。

| row | expected service | apply | specs mode |
|---|---|---:|---|
| default dry-run | deprovision | false | null |
| keep dry-run | deprovision | false | keep |
| apply modeなし | service mutationなし、request error | true | null |
| apply keep | deprovision | true | keep |
| remove dry-run | purge | false | remove |
| apply remove | purge | true | remove |
| update | recognized/fresh existing service | N/A | N/A |
| init/init-force | existing service | N/A | N/A |

exact tests:

```text
test_i371_uninstall_cli_routes_remove_dry_run_to_typed_purge_service
test_i371_uninstall_cli_routes_remove_apply_to_locked_typed_purge_service
test_i371_uninstall_cli_keeps_six_deprovision_rows_on_deprovision_service
test_i371_uninstall_cli_never_routes_update_or_init_to_purge
test_i371_uninstall_cli_calls_each_selected_service_once
test_i371_uninstall_cli_does_not_read_journal_or_guard
```

### 9.5 Red public mapper tests

```text
test_i371_uninstall_mapper_accepts_only_purge_remove_pair
test_i371_uninstall_mapper_rejects_purge_keep_or_default_pair
test_i371_uninstall_mapper_rejects_deprovision_remove_pair
test_i371_uninstall_remove_json_is_schema_one_and_exactly_one_object
test_i371_uninstall_remove_public_history_action_is_root_aggregated
test_i371_uninstall_remove_status_and_exit_mapping_is_stable
test_i371_uninstall_remove_same_plan_guidance_uses_remove_specs
test_i371_uninstall_remove_legacy_ambiguity_has_no_automatic_retry_command
test_i371_uninstall_remove_text_contains_sanitized_phase_and_relative_paths
test_i371_uninstall_remove_does_not_expose_journal_contract_or_stage_state
```

### 9.6 Implementation order

1. new service importを追加する。
2. `_run_uninstall_explicit_spec_history_purge()` をdeprovision adapterと同じasset/root/error boundaryで追加する。
3. remove dry-run routeをnew adapterへ切り替える。
4. remove apply routeをexisting exclusive lock + bound root identityでnew adapterへ切り替える。
5. emitterをintent-neutral nameへgeneralizeする。
6. typed result validatorにaccepted pairとretry policy invariantを追加する。
7. mapperへsame-remove retry commandとpurge error mappingを追加する。
8. public root action aggregationがservice resultからそのまま出ることを確認する。
9. CLI journal/guard monkeypatchがraiseしてもmapperがresultから出力できることを確認する。

### 9.7 Green acceptance

- remove dry/applyのproduction dispatchがnew serviceだけ。
- default/keep behavior unchanged。
- `--apply` modeなしerror unchanged。
- schema version 1、field set、one-object、status/exit unchanged。
- present history public outcomeはroot一件。
- same-plan purge retry commandは`--apply --remove-specs`。
- legacy ambiguityはretry command null/manual guidance。
- CLIがjournal/marker/checkpointを解釈しない。

### 9.8 Focused command

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'i371 or uninstall or remove_specs or keep_specs or retry_marker' -q
uv run pytest tests/cli_runtime/test_distribution_cutover.py -k 'i371 or uninstall or purge' -q
```

### 9.9 Minimal change boundary

- argparse help/flagsを変更しない。
- public JSON fieldを追加・削除しない。
- deprovision result status/error mappingを変更しない。

### 9.10 禁止事項

- CLIでhistory treeをscan/removeする。
- CLIでauthority string、plan digest、journal recordを作る。
- old routeへexception fallbackする。
- `--remove-specs`なしでpurge adapterを呼ぶ。
- partial recovery時にkeep/remove modeをjournalから推測してCLI flagを補う。

### 9.11 Stop conditions

- public compatibilityを保つためnew schema fieldが必要になる。
- typed resultだけではcurrent public outputを再現できない。
- routeがold writerへ到達するfallbackを残す必要が生じる。

## 10. Step 5 — Legacy purge writerを物理削除する

### 10.1 目的

production executable pathからold remove-specs mutation authority、recursive kernel、marker writerを除去し、single writerをsource/ASTで証明する。

### 10.2 Production ownership

single writerが `src/spec_dock/cli.py` を編集する。new route focused green後に実施する。

### 10.3 Delete set

call graph確認後、remove compatibility clusterだけから到達する次を削除する。

```text
_run_uninstall_remove_specs_compatibility
_UninstallTargetIdentity
_UninstallAction
_build_uninstall_plan
_apply_uninstall_plan
_remove_uninstall_path
_remove_uninstall_tree_fd
_write_uninstall_retry_marker
_finalize_uninstall_retry_marker
_restore_uninstall_retry_marker_action
_ensure_uninstall_retry_marker_action
_verify_uninstall_postcondition
_cleanup_empty_uninstall_dirs
_uninstall_apply_blockers
legacy _uninstall_payload
_emit_uninstall_preflight_error
old uninstall identity capture/classification/walk helpers with no remaining caller
```

retain set:

```text
_uninstall_retry_command
_safe_retry_target_label
_uninstall_payload_from_result
_validate_uninstall_process_result
_uninstall_exit_code_from_result
_summarize_uninstall_outcomes
_uninstall_guidance_from_result
_uninstall_public_operation_error
_uninstall_public_action_error
_render_uninstall_text
```

`managed_distribution.py`のlegacy marker reader/constantsは保持する。writerだけを消す。

### 10.4 Red/green seam tests

`tests/cli_runtime/test_distribution_cutover.py`:

```text
test_i371_distribution_cutover_has_no_legacy_remove_specs_route
test_i371_distribution_cutover_has_no_cli_recursive_uninstall_mutator
test_i371_distribution_cutover_has_no_uninstall_retry_marker_writer
test_i371_distribution_cutover_retains_legacy_marker_reader_only
test_i371_distribution_cutover_remove_route_calls_common_purge_service
test_i371_distribution_cutover_cli_mapper_has_no_journal_interpretation
test_i371_distribution_cutover_has_single_production_purge_writer
```

red acceptance: old symbol/AST call edgeが存在する限り失敗。

green acceptance:

- old route definition 0。
- old marker write/finalize/delete symbol 0。
- CLI `os.walk`/recursive unlink/rmdir call edgeがpurge routeに0。
- purge service import/call edge exact 1。
- legacy marker readerはmanaged distribution admissionからreachable。
- public mapper retained。

### 10.5 Verification command

```bash
uv run pytest tests/cli_runtime/test_distribution_cutover.py -k 'i371 or uninstall or purge' -q
uv run pytest tests/unit/infra/test_init_update.py -k 'i371 or uninstall or remove_specs' -q
```

### 10.6 Minimal change boundary

- unrelated init/update installer helpersを削除しない。
- retained mapper helperの名前一致だけで誤削除しない。
- public testsのexpected action/statusをold helper不在に合わせて緩めない。

### 10.7 禁止事項

- dead codeとしてold writerを残す。
- `if False`、feature flag、environment variableで隠す。
- test-only import可能なprivate fallbackを残す。
- legacy marker readerまで削除してambiguous stateを無視する。

### 10.8 Stop conditions

- old helperがremove route以外のproduction behaviorに実際に必要である。
- delete setの一部がpublic mapperに必要で、責務分離なしに削除できない。
- AST testではなく文字列置換だけでabsenceを主張する必要が生じる。

## 11. Step 6 — Documentation、focused suites、normal gates

### 11.1 目的

code/tests/docsをcurrent behaviorへ同期し、Full Regression前のnormal quality gateを完了する。

### 11.2 Documentation changes

`README.md`:

- remove-specs compatibility route記述を削除
- exact history rootを明記
- dry-run write0、apply再assessmentを明記
- `--apply` + `--remove-specs` two-part authority
- symlink/hardlink/special blocker
- `.workbench`/outside preservation
- same-remove forward recovery
- legacy marker automatic conversionなし

canonical Issue docs:

- 本`requirement.md`、`design.md`、`plan.md`を採用
- implementation後のsymbol名が本設計と一致することをsource review
- document内にold fictional API、old compatibility owner、timeout flagsを残さない

### 11.3 Focused suites

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'i371 or purge or remove_specs' -q
uv run pytest tests/unit/infra/test_init_update.py -k 'i371 or uninstall or remove_specs or keep_specs or retry_marker' -q
uv run pytest tests/cli_runtime/test_distribution_cutover.py -k 'i371 or uninstall or purge' -q
uv run pytest \
  tests/unit/infra/test_managed_distribution.py \
  tests/unit/infra/test_init_update.py \
  tests/cli_runtime/test_distribution_cutover.py
```

focused green acceptance:

- new I371 tests全green。
- existing I370 deprovision tests全green。
- route/mapper/cutover tests全green。
- flaky rerunでのみgreenをacceptしない。

### 11.4 Fast lane

```bash
uv run pytest -m fast -q
```

fast lane green後、default suiteへ進む。

### 11.5 Default suite

```bash
uv run pytest
```

`pyproject.toml` のcurrent defaultはFull Regression markerを除外する。default suiteをFull Regression evidenceの代替にしない。

### 11.6 Static/metadata gates

```bash
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

acceptance:

- Ruff/MyPy/project lint all green。
- SpecDock structural validation green。
- whitespace error 0。
- docs/metadata pathがcanonical。
- no generated cache/artifactをcommit対象に含めない。

### 11.7 Source review commands

```bash
git diff -- src/spec_dock/managed_distribution.py src/spec_dock/cli.py
git diff -- tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py
git diff -- README.md
git grep -n '_run_uninstall_remove_specs_compatibility\|_write_uninstall_retry_marker\|_apply_uninstall_plan\|_remove_uninstall_tree_fd' -- src tests
git grep -n 'execute_explicit_spec_history_purge_distribution' -- src tests
```

old symbol grepはcanonical historical docsやIssue attachmentsではなく、production `src`とactive testsのseamを判定する。production definition/call edgeは0でなければならない。

### 11.8 Stop conditions

- focused/fast/default/lint/validateのいずれかがred。
- unrelated test expectationを緩めなければgreenにならない。
- public schema diffが発生する。
- old writer symbol/call edgeが残る。
- git diffにledger/verifier変更が含まれる。

## 12. Step 7 — Full Regression evidence

### 12.1 Entry conditions

次がすべてgreenの場合だけ実行する。

- focused suites
- `uv run pytest -m fast -q`
- `uv run pytest`
- `make lint`
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`
- old writer absence review
- public schema review

### 12.2 Approved ledger

変更禁止path:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/full-regression-ledger.json
```

Full Regressionを通すため、次をしてはならない。

- approved signature追加・削除・変更
- failure countのrebaseline
- verifier判定の緩和
- test skip/xfail
- shard除外
- timeout復活または短縮
- workflow/harness変更

### 12.3 Command

fresh artifact directoryで実行する。

```bash
rm -rf .artifacts/iss-00371-full-regression
uv run python \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py \
  --shards 4 \
  --artifact-dir .artifacts/iss-00371-full-regression
```

PR #380後のcurrent verifierにはtimeout flagsを渡さない。

### 12.4 Acceptance

- command exit 0。
- verifier summary `status=verified`。
- approved failure signaturesがledgerとexact一致。
- unexpected failure 0。
- unexpected error 0。
- collection mismatch 0。
- missing shard/artifact 0。
- candidate attributable new failure 0。
- ledger file diff 0。

### 12.5 Attribution

unexpected failure/errorがある場合:

1. exact candidate SHAを記録する。
2. failing node/test signatureを保存する。
3. Issue 371 diffとの因果をfocused reproductionで確認する。
4. attributableならproduction/test fixを行い、Step 6から再実行する。
5. unrelatedと判断してもledgerを変更せず、approved ledger policyに従えない限りIssue completionをclaimしない。

### 12.6 Stop conditions

- verifierを通すためledger/harness変更が必要。
- artifact directory再利用で結果が混在する。
- verifierが`verified`以外。
- candidate SHA不明のevidenceしか残らない。

## 13. Negative case matrix

| ID | fixture | expected |
|---|---|---|
| I371-N01 | remove dry-run | target/guard/journal/legacy/stage write0、planned/0 |
| I371-N02 | apply modeなし | purge service call0、error/2 |
| I371-N03 | apply keep | deprovisionのみ、history mutation0 |
| I371-N04 | update/init | purge action/authority/journal0 |
| I371-N05 | history root symlink | blocked/1、operation-wide write0、target不変 |
| I371-N06 | child symlink to external | blocked/1、link/target不変、write0 |
| I371-N07 | hard-linked history regular | blocked/1、peer不変、write0 |
| I371-N08 | FIFO/socket/device | blocked/1、write0 |
| I371-N09 | unreadable/rebound entry | blockedまたはrecovery_required、unsafe unlink0 |
| I371-N10 | unknown regular history content | explicit purge対象、success時absent |
| I371-N11 | unknown sibling outside history | preserve-and-blockまたはaction外、削除0 |
| I371-N12 | `.workbench` nested content | witness unchanged |
| I371-N13 | component blocker + safe history | operation-wide write0 |
| I371-N14 | history absent no-op | history action0、guard/journal/stage0 |
| I371-N15 | history appearance after absence witness | new authority発行0、blocked/recovery_required |
| I371-N16 | root rebind before first mutation | target write0 |
| I371-N17 | parent rebind before leaf | current/future mutation停止、journal保持 |
| I371-N18 | child rewrite after assessment | unlink0、recovery_required |
| I371-N19 | unknown child appears before rmdir | rmdir0、entry保持、recovery_required |
| I371-N20 | deprovision journal + remove | checkpoint進行0 |
| I371-N21 | purge journal + keep/default | checkpoint進行0 |
| I371-N22 | purge journal + update/init | checkpoint進行0 |
| I371-N23 | purge journal different root | write0 |
| I371-N24 | purge journal changed plan | write0 |
| I371-N25 | valid legacy marker | partial_failure/1、manual、marker/target不変 |
| I371-N26 | copied legacy marker | authority補完0、marker/target不変 |
| I371-N27 | invalid/symlink/hardlink/special legacy marker | error/2、write0 |
| I371-N28 | legacy + new journal/guard | dual state、双方進行0 |
| I371-N29 | guard publish failure | target write0 |
| I371-N30 | journal prepare failure | target write0 |
| I371-N31 | checkpoint write failure after unlink | recovery_required、journal/guard保持 |
| I371-N32 | terminal post-assessment failure | completedをclaimせずrecovery_required |
| I371-N33 | CLI journal read monkeypatch raises | typed mapper output成功、journal interpretation0 |
| I371-N34 | purge result + keep mapper pair | RuntimeError、public output生成なし |
| I371-N35 | deprovision result + remove mapper pair | RuntimeError、public output生成なし |
| I371-N36 | old route/helper source scan | production definition/call edge0 |
| I371-N37 | Full Regression ledger diff | completion block |

## 14. Red/green acceptance summary by step

| Step | red evidence | green evidence |
|---|---|---|
| 0 | new route/contract/absence expectations fail on baseline | characterization is deterministic; production unchanged |
| 1 | purge literal/purpose/retry unsupported | strict discriminator tests green; schema unchanged |
| 2 | contract/assessment/tree tests fail | read-only exact actions/witnesses/blockers green |
| 3 | service/recovery tests fail | single journaled writer、same-plan recovery、write0 boundaries green |
| 4 | remove route/mapping tests fail | typed service dispatch、public parity green |
| 5 | old symbols/call edges present | old writer absent、reader/mapper retained |
| 6 | focused/fast/default/lint/validate red | normal gates all green |
| 7 | verifier not verified | exact ledger、unexpected 0、candidate evidence complete |

## 15. Minimal implementation boundary

Issue 371 candidateのproduction diffは次の責務に限定する。

- `purge` intent/authority discriminator
- exact history contract/assessment
- deprovision component composition
- common destructive service/recovery parameterization
- typed result aggregation
- CLI remove route cutover
- old purge writer deletion
- README synchronization

次を混在させない。

- package version bump
- unrelated refactor/naming cleanup
- fresh/update/init journal redesign
- generic transaction framework
- generic subtree deletion library
- Windows abstraction
- Full Regression baseline repair
- new public UX

## 16. Rollback plan

### 16.1 Before first purge guard/journal reaches a consumer

- candidate diffをrevert可能。
- focused fixtureでtarget/guard/journal/legacy/stage write0を確認する。
- old writerを再導入した中間releaseを作らず、candidate全体をwithdrawする。

### 16.2 After purge guard/journal creation

- old packageへdowngradeしない。
- `intent=purge`、authority=`explicit-spec-history-purge`、same root/contract/plan、protocol 2を理解するcorrective packageを作る。
- userはexact `spec-dock uninstall --apply --remove-specs <target>`でforward recoveryする。
- guard/journal/legacy marker/stageを手動削除しない。
- completed deletionをrollbackしない。
- deleted historyのautomatic restoreを約束しない。

### 16.3 Ambiguous state

- automatic cleanup停止。
- public JSON、candidate SHA、package version、relative inventory、guard/journal digestsを保全する。
- authority/root/planを人間が確認できるまでmutationしない。
- file contents、credentials、absolute consumer pathを外部artifactへ転載しない。

## 17. Handoff

### 17.1 Luna/max implementation handoff completion

implementation authorへ渡す判断は本3文書で完結する。

- internal intent: `purge`
- authority: `explicit-spec-history-purge`
- guard purpose: `purge-journal-forward-only`
- history root: `spec-dock/initiatives`
- preserved root: `spec-dock/.workbench`
- history regular/dir: delete authorityあり
- history symlink/hardlink/special/unreadable: operation-wide blocker
- dry-run: write0、cached authorityなし
- apply: lock後reassessment
- recovery: same-plan forward only
- legacy marker: conversionなし/manual
- public schema/flags: unchanged
- public history action: root-level aggregation
- old writer: same Issueで削除
- Full Regression ledger:変更禁止

### 17.2 Issue 372 handoff

Issue 372へ渡すもの:

- D1〜D4 public flowのlegacy seam absence evidence
- package surface parity inventory
- Linux/macOS focused evidence
- candidate-wide Full Regression artifact
- current protocol compatibility evidence

Issue 372へ渡さないもの:

- Issue 371 old writer削除
- purge authority/root decision
- legacy marker conversion decision
- public mapper cutover
- Issue 371 attributable test failure

### 17.3 Completion evidence bundle

implementation完了時のreportは少なくとも次を記録する。

- candidate full SHA
- modified production/test/docs paths
- focused commands/results
- fast/default/lint/validate/diff-check results
- Full Regression command/artifact/status
- approved ledger diff 0
- old writer source/AST absence
- public schema parity
- recovery/legacy negative evidence
- P0/P1 residual 0

## 18. Final completion gate

次がすべて真でなければIssue 371をcompleteにしない。

1. Requirement I371-R01〜R40をtest/evidenceへmapping済み。
2. normal remove applyがhistory rootを削除し、`.workbench`/outside contentを保持する。
3. symlink/hardlink/special/rebind/unknown appearanceでunsafe mutation 0。
4. pre-write blockerとdry-runがoperation-wide write0。
5. same-plan purge recoveryだけがcheckpointを進める。
6. legacy markerからpurge authorityを推測しない。
7. public command/flag/schema/status/exit/root action semanticsが維持される。
8. `_run_uninstall_remove_specs_compatibility` とlegacy writer/mutatorがproductionから削除済み。
9. CLI mapperがjournal/guardを解釈しない。
10. focused、fast、default、lint、validate、diff-checkがgreen。
11. Full Regression verifierがverified、unexpected 0、ledger変更0。
12. unresolved P0/P1が0。
13. human authority/design decisionが0。
