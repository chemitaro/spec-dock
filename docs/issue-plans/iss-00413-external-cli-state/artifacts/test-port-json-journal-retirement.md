# 旧JSON transaction writerの退役と試験の引継ぎ

## 判断と読取範囲

RQ-413-02、RQ-413-09、D-03/D-09/D-12、P-12に従い、現在の業務経路から使われていないJSON transaction writerだけを退役する。旧 `infra/json_store.py` 全345行・16 functionsと `test_atomic_json_publication.py` 全157行・八test関数を全文確認した。

現行のguarded JSON読取、物理directory保持、Start/Scope directory公開のnative no-replace rename、fs_repoから使う基本JSON I/Oは同fileに残す。旧writerと復旧六関数（atomic_write_json、reconcile_atomic_json、_rename_exchange_at、_exchange_topology、_write_transaction_record、_target_identity）を削除し、exchange/no-replace切替helperを現行no-replace関数へ統合した。Linuxの0x1、Darwinの0x4、衝突拒否・未対応環境の拒否は維持する。全src/testsのASTで、候補外import/attribute参照は0。最終helperは112行・九functionsである。

`.specdock-json-transactions`、UUID付きintent/stage/done、exchange後の競合復元、保存intentのreconcileを削除した。通常Scope更新は既存 `direct_json.replace_existing_json` のbytes/identity再検査、一file置換、unknown/partial、現物の再観測を使う。immutable直接recordの公開/解除は別に維持する。旧consumerのJSON証拠やpath/hash inventoryは変更しない。

## 旧testごとの対応

後継は `tests/integration/test_direct_json_publication.py`。全八旧testを以下へ対応させる。機械的な同等性ではなく、維持する安全境界と廃止する保証を区別する。

| 旧test | 維持・変更する内容と後継 |
|---|---|
| test_atomic_json_exchange_failure_keeps_previous_bytes | 現行置換が効果前に失敗した時の元bytes/mode保全、未確認のstage保全をtest_metadata_replace_failure_keeps_previous_bytes_without_rollbackで確認。exchangeや自動rollbackは残さない |
| test_atomic_json_exchange_preserves_racing_destination | test_metadata_replace_preserves_actor_change_observed_before_replacementで、直前再検査により別actorの変更を保全。旧exchange後の競合復元は廃止。検査とrenameの隙間への任意writerを原子的CASで守るとは主張しない |
| test_atomic_json_exchange_error_after_effect_blocks_blind_retry | test_metadata_replace_error_after_effect_preserves_visible_bytes_and_reobservesで、効果後エラーをunknownとして変更済みbytesを保全。intentによる再送阻止/reconcileは廃止。現物確認後の新しい明示操作を検査 |
| test_atomic_json_create_only_has_no_second_hardlink | test_file_create_only_has_one_link_and_preserves_an_existing_destinationで、現行file公開の最終nlink=1、既存先不変、stageなしを確認 |
| test_atomic_json_killed_after_exchange_retains_old_and_blocks_retry | test_killed_metadata_replace_preserves_the_visible_boundary_without_journalのbefore/after二caseで別processを強制終了。効果前は元bytesと未公開stage、効果後は完成した新bytesを保全。旧bytesの常設transaction保存とintent復旧は廃止。後の明示操作が残ったstageを触らないことも確認 |
| test_atomic_json_refuses_symlink_destination | test_metadata_replace_refuses_symlink_destinationで対象と実file不変を確認 |
| test_atomic_json_refuses_symlink_ancestor | test_metadata_replace_refuses_symlink_ancestorで外部先のbytes/entry不変を確認 |
| test_atomic_json_rejects_hardlinked_target_and_accidental_replace | test_metadata_replace_rejects_hardlinked_targetで二linkのbytes保全、上のcreate-only testで既存先の意図しない置換拒否を確認 |

旧sourceの削除前、後継九casesは **9 passed、0.20秒、exit0**。これは既存Greenのcharacterizationであり、製品機能の新しいRedとは数えない。初回Ruffのregex表記とmypyのOS callback引数型の指摘は、fixtureの実契約へ合わせて修正した。ignore/cast/skip/収集除外は追加していない。型補正で後継の強制終了phase/assertionsは変更していない。旧assertionsの扱いは上の表に示す。

## 実測と残り

- 通常wheelが旧六関数・transaction領域・uuid importを含まない検査: **Red 1 failed、0.73秒、exit1 → Green 1 passed、13.49秒、exit0**。
- 後継、直接record、native kill、Start、Scope edit、依存、lifecycle、migration、wheelの九suite: **236 passed、79.68秒、exit0**。
- 実Python 3.10.15の隔離venvとprovider import元を再照合し、後継/native record kill/store三suite: **23 passed、4.14秒、exit0**。
- 全Ruff check/format（311 files）、MYPYPATH=srcの変更三Python files限定mypy、diff checkが成功。
- 通常make lintはb572538cに今回のPython差分を適用した候補で **mypy 32 errors / 11旧source files（230 source files）、make exit2**。限定成功をfull gate合格にしない。

元logsは既存Epic Workbenchの `iss-00413-implementation/pytest-direct-json-retirement-{port,source-red,source-green,related,python310}.log`、`direct-json-test-typing.log`、`lint-direct-json-retirement.log` に保持する。先行Python 3.10全件成功は別の候補であり、今回の全件/実Linux/Windows native/fresh Strict/最終手動確認は別途残る。実consumer、metadata、直接record、live GitHubは未変更。
