# 旧Scope lifecycle試験・writerの退役

D-09/D-11に従い、Scope Close/Reopenの安全性を公開mainに残し、control/epoch/WriterLock/operation journalを通常配布から除く。旧test_scope_close_vnext.py全303行・八test関数とfixture _Gateway、旧application/scope_completion.py全494行・七関数/classを全文確認した。

## 八test関数の個別判断

| 旧test | 判断・公開側の後継 |
|---|---|
| `test_completed_parent_rechecks_each_descendant_even_if_already_completed` | 保持。公開test_completed_parent_close_still_checks_unfinished_descendantsをopen/not-planned/unknownの三statesへ拡張し、completed parentのnoop候補でも全子孫条件を検査、tree/捕捉record保持・GETだけを確認。 |
| `test_empty_parent_can_complete_and_not_planned_is_explicit` | 保持。公開通常Closeとtest_not_planned_close_lists_children_and_never_closes_themがempty parentの完了と明示not-planned理由を扱う。子を自動完了しない。 |
| `test_close_reason_conflict_and_reopen_ancestor_guard` | 保持。新test_completed_close_requires_reopen_after_not_planned_and_preserves_selectionでterminal reason conflict、既存公開Reopenをcompleted/not-planned/unknown ancestorの三statesへ拡張してopen祖先必須を確認。 |
| `test_local_close_and_reopen_persist_only_lifecycle` | 既存local保全として保持。test_scope_close_reopen_previews_and_updates_only_existing_local_lifecycleとunknown field保全の公開testへ対応。後者に同理由Closeの再実行を加え、unchanged/changed=false、unchanged effect、全tree/metadata/record不変・gh接触0を確認。新local Scopeの発行はしない。 |
| `test_github_close_uses_live_status_and_leaves_metadata_unchanged` | 保持。test_scope_close_confirms_completed_without_releasing_the_direct_record、一PATCH/確定GET、local metadata/branch/record保全、completed parent guardと新mixed-backend Finish試験へ対応。旧control/epoch fixtureは退役。 |
| `test_local_close_resume_reconciles_saved_state_after_journal_failure` | journal resumeを廃止。test_local_close_retains_confirmed_effect_after_descriptor_cleanup_failureがnative完了後のcleanup failureをpartial/confirmedとして保持し、次の明示操作へ案内する。 |
| `test_github_close_resume_observes_remote_before_finishing_journal` | journal resumeを廃止。公開のClose確定/unknown/一PATCHと既存retry系試験が、現物再観測と二重送信禁止を維持する。operation IDは使わない。 |
| `test_github_unknown_effect_is_not_resent_on_resume` | no blind resendを保持しresumeは廃止。test_unconfirmed_close_reports_unknown_and_never_repeats_a_patchでunknown・local保全・第二PATCHなし、retired-recoveryの公開syntax拒否へ対応。 |

## 七symbolsの個別判断

| 旧symbol | 判断・現行authority |
|---|---|
| `CompletionResult` | 旧operation_id返却型を退役。公開v2 Scope FamilyData/OperationResultとchanged/effectsが現行authority。 |
| `_completion_fingerprint` | journal fixed requestのfingerprint保存を廃止。操作履歴を新しく保持しない。 |
| `_decide_lifecycle` | 旧control付き入口の観測composerを退役。direct_scope_lifecycleが必要target/祖先/子孫をlive観測し、pure scope_completion_planへ渡す。 |
| `preview_scope_lifecycle` | 旧admission/controlを前提にしたpreviewを退役。現在の公開dry-runは局所writer宣言検査/必要GETだけで効果をplannedとして返す。 |
| `change_scope_lifecycle` | 旧WriterLock/epoch/journal writerを退役。direct_scope_lifecycleがmetadata bytes/identity比較・局所公開・GH確定・unknown/partialを提供し、選択やGitを変えない。 |
| `resume_scope_lifecycle` | operation journalからのlocal/GH再開を廃止。現物確認後の新しい明示Close/Reopenへ戻し、blind retryしない。 |
| `_resume_github_lifecycle` | 旧GH intent/resultを継続する処理を廃止。現在の確認GET/一PATCH/unknown判定はdirect_scope_lifecycle/github_lifecycleで扱う。 |

pureなCompletionDecision/CompletionReason/_ancestors/_descendants/plan_close/plan_reopenは既にscope_completion_plan.pyが唯一のauthorityで、このunitではその本体を変更しない。最後の旧scope_delete_vnext.pyによる_descendants参照だけを同authorityへ向ける。import先の一field以外は全ASTが元HEADと同一である。

二file退役後、source/testsの全ASTでTYPE_CHECKINGとfrom-import子moduleを含め旧module/fixture import 0を確認した。残る文字列はwheel/fresh processの収録・import禁止assertion、既知asset inventoryの旧path/digestだけで、後者はownership証拠として保持する。新fallback/alias/build除外は作らず、旧Scope delete等の残るprivate writerは別unitで整理する。skip/pytest収集除外は増やさない。

## 公開保証の検証

childのopen/not-planned/unknownによるcompleted parent拒否と、祖先のcompleted/not-planned/unknownによるReopen拒否は六casesで6 passed（2.24秒）。新terminal reason conflictは1 passed（0.46秒）。既存local Close後の同理由再要求は1 passed（0.37秒）、仕様/unknown任意field/metadata bytes/直接record/treeを保持した。いずれも現行公開実装のcharacterizationで製品Redではない。

新test挿入時のmultiline signature違いによるpatch照合失敗はfile変更を伴わず、次のparametrization配置誤りはexit4/collection errorだった。元help testのdecoratorを正しい位置へ戻して実行した。local noopのeffectsを空とする過剰期待も1 failed（0.41秒）になったため、v2のunchanged effectを期待する形に訂正した。これらを製品Redや成功の代わりにせず元logを保存する。

通常wheelの収録禁止は旧scope_completion.pyを含むRed 1 failed（0.76秒）、source退役後の同testはGreen 1 passed（13.71秒）。fresh wheel/sdist・外部非editable venv・実console・局所static操作・入力保全を確認した。

関連Scope lifecycle/Finish/旧・現行Scope deleteの115 tests（34.01秒）、全source/tests Ruff check/format（368 files）、変更二test限定mypy --follow-imports=silent、diff checkが成功した。logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-lifecycle-port.log、pytest-scope-lifecycle-source-{red,green}.log、pytest-scope-lifecycle-retirement.logへ保持する。

このunit前のclean 0c04677bada135dbb50ea0c48f7fc3b4aae368c9で通常make lintを再実行した。Ruff check/format（370 files）は成功したがmypyは313 errors/40 files（289 source filesを検査）、source 54/test 259 errors、make exit2で未合格だった。元logはiss-00413-implementation/lint-p12-0c04677b.logへ保持する。以前の407 errorsは別snapshotの記録であり、新しい通常gateの結果で現状を更新する。今回の限定Greenをfull gateに読み替えず、残る旧private writersの参照整理と現行型問題、全pytest、native Windows/別Python、fresh Strict、最終手動製品確認を継続する。実consumer・既存WT・旧Git領域・live GitHubは未変更。
