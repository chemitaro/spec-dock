# 旧fixed engine locator / group installationの製品source退役

D-11/D-12に従い、旧三module・48 top-level symbolsを退役する。通常consoleは既にspec_dock.cli:main、新installationはdirect_installation/direct_static_updateが明示一WTのstatic資産だけを扱う。engine pin、全WT control、epoch、group journal、resume/rollback/finalizeを残さない。

対象全文とsource/testsのAST importを確認した。TYPE_CHECKINGとfrom-importの子moduleも含め、候補外からのimportは0。候補内部の依存はengine_handover→runtime_loader、installation_update→engine_handover/runtime_loaderの三箇所だけで、閉じた三moduleを一緒に削除する。testのruntime_loader禁止文字列はCI/utilityのsentinelであり、旧moduleの呼出しではない。名称や到達不能だけを削除根拠にせず、先に[54旧試験の個別判断](test-port-installation-retirement.md)と現行公開installation/wheel/退役診断を照合した。既知旧資産のstatic inventory path/digestはownership証拠として保持する。

## src/spec_dock/runtime_loader.py

| 旧symbol | 判断・後継 |
|---|---|
| `EnginePin` | fixed executable/distribution digestのlocator型を廃止。通常packageのconsole/resourcesをauthorityにする。 |
| `VerifiedEngine` | 起動の前提だった固定engine検証値を廃止。別bundleを保持しない。 |
| `digest_distribution` | 固定lib/bin copyのdigest生成を廃止。通常wheel/static inventoryのhash検査は現行公開試験で維持。 |
| `verify_engine_pin` | Git内pinとfixed layoutを起動条件にしない。公開consoleの通常package起動へ統合済み。 |
| `git_common_directory` | 現行project_context.resolve_git_contextがnative Gitからcommon-dirを読取る。旧pin用helperを残さない。 |
| `read_engine_pin` | 旧locatorを新authorityとして読まない。必要な旧所在診断はlegacy_readerのread-only観測へ分離済み。 |
| `write_engine_pin` | Git内engine locatorの作成を廃止。 |
| `replace_engine_pin` | Git内engine locatorの差替えとhandoverを廃止。 |

## src/spec_dock/runtime/application/engine_handover_vnext.py

| 旧symbol | 判断・後継 |
|---|---|
| `verify_source_update` | fixed engineのcommit/version source取得と一致検査を廃止。外部package更新と局所static更新を分離。 |
| `_engine_from_record` | 旧handover journalから実行engineを復元しない。resumeは公開入口で退役診断。 |
| `_rotated_control` | 全WT registration/digest/epochの回転を廃止。 |
| `handover_candidate` | 別fixed engine候補の取得・検証を廃止。 |
| `plan_engine_handover` | engine/control世代切替のplanを廃止。現行installation previewは一WTの静的資産だけを観測。 |
| `activate_engine_group` | 全WT engine activationとcontrol公開を廃止。--activate-engineは効果前拒否。 |
| `resume_engine_handover` | 永続handover操作の再開を廃止。旧証拠は保全し、新journalに移植しない。 |
| `rollback_engine_handover` | engine pin/controlの自動巻戻しを廃止。--rollbackは効果前拒否。 |

## src/spec_dock/runtime/application/installation_update_vnext.py

| 旧symbol | 判断・後継 |
|---|---|
| `_child_root` | group child recordのtarget解決を廃止。現行installationは明示一WT rootをnative Gitで解決。 |
| `_require_maintenance` | 中央controlのmaintenance前提を廃止。自workspace宣言と明示確認だけを検査。 |
| `_can_restore_ready` | group ready復帰条件を廃止。全writer modeを操作しない。 |
| `_commit_update_matches_engine` | commit由来group updateと実行engineの整合契約を廃止。 |
| `_verify_finalization_targets` | 全WT finalization target検証を廃止。局所static資産のsnapshot再検査は現行処理で維持。 |
| `_verify_latest_installed_children` | 全WTの最新installed child record検証を廃止。静的資産の既知hash/未知改変判定へ移行済み。 |
| `plan_installation_finalization` | whole-group finalization previewを廃止。--finalizeは効果前拒否。 |
| `finalize_installation_group` | whole-group commit/ready公開を廃止。 |
| `resume_installation_finalization` | finalizationのjournal再開を廃止。 |
| `_fixed_targets` | registry/controlに固定した全WT target群を廃止。別WTへ一括適用しない。 |
| `_check_bundle` | 別fixed engine由来bundleの検査を廃止。通常packageのstatic inventory照合は保持。 |
| `_quarantine_unjournaled_stage` | 旧group operationの未記録stageをjournalへ補完しない。旧証拠を変更しない。 |
| `_stage_missing` | 全childへの一括stageを廃止。現行init/updateは一WT内で正確なpartial効果を返す。 |
| `_apply_children` | 全childへの順次applyを廃止。別WTを変更しない。 |
| `_verify_group_markers` | 全child markerのgroup commit検証を廃止。現行資産の現物snapshot検証へ移行済み。 |
| `_commit_group` | installation group journal/markerのcommitを廃止。 |
| `_fresh_group` | 新規全WT installation groupの生成を廃止。 |
| `_check_init_inventory` | 全WT group init inventory検査を廃止。明示targetの既存path/unsafe path拒否は現行initで維持。 |
| `initial_worktree_id` | 中央registry用の独自worktree ID発行を廃止。native WT path/物理identityを使用。 |
| `_legacy_group` | legacy全WT groupのcontrol bootstrapを廃止。旧Git領域はread-onlyで保全。 |
| `inspect_legacy_installation` | group writerへ接続する旧検査を廃止。現行show/Doctorは旧所在をread-onlyで診断。 |
| `_initial_control` | maintenance control/registrationの生成を廃止。 |
| `plan_init_installation_group` | 全WT group init planを廃止。現行installation init previewは明示WTだけを扱う。 |
| `bind_installation_engine` | init前のengine pin公開を廃止。Git内locatorを書かない。 |
| `init_installation_group` | 全WT group initを廃止。direct_installation.install_static_assetsへ局所化済み。 |
| `resume_init_installation_group` | group initのjournal再開を廃止。公開--resumeは効果前拒否。 |
| `rollback_init_installation_group` | group initの自動巻戻しを廃止。公開--rollbackは効果前拒否。 |
| `update_installation_group` | 全WT group updateを廃止。direct_static_update.update_static_assetsで明示一WTの既知資産だけを更新。 |
| `uninstall_installation_group` | 全WT group uninstallを廃止。明示一WTの既知資産だけをbackup後に退役し、仕様/未知fileを保持。 |
| `resume_installation_group` | group update再開を廃止。現物を観測し直す新しい明示操作へ移す。 |
| `resume_uninstall_installation_group` | group uninstall再開を廃止。旧journalを新authorityにしない。 |
| `rollback_installation_group` | group update/uninstallの自動巻戻しを廃止。backup保全と明示partial表示を維持。 |

## Red → Green

先に通常wheelの収録禁止へ三moduleを追加した。正常build後、artifactに三moduleが存在するため1 failed（0.96秒）。source削除後、同じ受入れ試験は1 passed（14.12秒）。fresh wheel/sdistからのderived wheel、非editable外部venv、実consoleの44 leaf help/version/completion、validate/CI HEAD検査、shim、局所static installationとtree保全を最後まで確認した。新たなbuild除外・互換alias・fallbackは追加していない。

公開assets/entrypoint/provider/retired-recoveryの関連100 tests（72.84秒）、全source/tests Ruff check/format（395 files）、変更wheel test限定mypy --follow-imports=silent、diff checkも成功した。

元ログは既存Epic Workbenchのiss-00413-implementation/pytest-engine-retirement-{red,green,related}.logへ保持する。実consumer・既存WT・旧Git領域・live GitHubには適用していない。旧installationの再利用可能helpers、旧journal/registry/private writersの参照整理、full type gate、native Windows/別Python、fresh Strict、最終手動検証は別の残作業である。直近通常make lintの443 errors/49 filesは未合格のままであり、限定mypyを全体合格にしない。
