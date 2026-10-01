# Worktree adapterのテスト移行

変更前は `48a7ce3fcbe6ff365a05370511fb56bc6210c43c`。旧 `test_worktree_commands_vnext.py` の三関数を全文確認し、RQ-413-18、D-11とCLI v2へ照合した。run_vnext・control登録・登録alias・central receiptではなく、公開mainとnative Git inventory/ref、実Makefileを入口にする。

| 旧test | 後継・判断 |
|---|---|
| `test_worktree_list_show_cli_uses_registered_identity` | list/showはnative path/branch/HEADを返す。Scope metadataが壊れていても独立して読み、全tree不変。登録ID/`wt:wt1`は撤去。relative/旧alias拒否と別WTのworkspace非読取は既存worktree suiteへ |
| `test_worktree_create_remove_cli_previews_and_keeps_branch` | createの明示root/name/baseとpath、preview時のGit/filesystem不変を検査。removeの確認不足/previewでtargetとGit不変、--yesだけで実削除、native branch refのtip保持を確認。旧登録採番をしない |
| `test_worktree_bootstrap_cli_dry_run_and_actual_result` | 明示native pathへmake init。preview/offlineはtree不変・makeの副作用0、--yesで該当WTだけ実行する。旧bootstrap receipt・自動実行・登録aliasは撤去。make入力安全性/timeout/unknown/process停止は現行bootstrap suiteで保護 |

後継も三cases。fresh tmp consumerでのみcreate/remove/bootstrapを実行し、実consumerや既存worktreeの削除承認と混同しない。通常suiteのskip・除外を追加せず、native Windows・全体gate・Strict合格を限定Greenから推論しない。
