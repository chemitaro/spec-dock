# Issue #413 実環境dogfooding記録（2026-10-03）

## 許可・対象

利用者の「ドックフーディングして、動作確認まで行って下さい」を受け、マージ前にこのworktreeへ導入する実環境作業を開始しました。PR作成・merge・package公開・他worktreeへの自動適用をこの許可に含めません。対象は `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/0805/spec-dock`、branchは `codex/iss-00413-external-cli-state`、開始HEADは `495d10ab7e47b02f2ba873df976afd6a12a0ad88` です。

## 初回導入と移行前観測

FQ候補wheel `spec_dock-0.2.4-py3-none-any.whl`（SHA-256 `d5afa8ab759ee04b236d54821524978a95defe6d396ef1aa83a824de7aaae74c`）を、通常の `uv tool install` で非editable導入しました。consoleは `/Users/iwasawayuuta/.local/bin/spec-dock`、package importはcheckout外のuv tool環境です。external help、legacy raw doctor、active show、workspace validateはactual exit 0。構造は240 Scope、direct selectionはemptyで、control/engine/registry/journal等は不在でした。workspace migration dry-runもactual exit 0、変更対象はworkspace宣言一件でした。

## 発見した保全不具合と必要な追加修正

初回migration applyはactual exit 6、`MIGRATION_INCOMPLETE`、backup unknown、workspace.migrate not_attemptedでした。workspace宣言と既存データは未変更。失敗した外部backup `/Volumes/990p2t/workspace/tools/spec-dock-backups/iss00413-20261003-workspace` は削除せず保持します。

現物の全entry type/mode/bytes/link比較で、過去のLinux試験から保存されたsymlink自身のmodeが0777から0755へ変わっていました。targetや通常fileの不一致ではありません。macOSのsymlink生成がumaskの影響を受ける一方、copyがlink自身のmodeを再設定していなかったことが原因です。検証hashや保存対象を弱めず、providerの `runtime/infra/tree_backup.py` が、生成後のmodeが異なる場合だけ、held directory descriptorとfollow_symlinks=Falseでlink自身のmodeを保持するよう修正します。Linuxではmodeが一致するため新chmodを行いません。

追加作業の契約は「異なる作成umaskで得たsymlinkも、外部targetを追跡・変更せず保全・復元照合を成功させる」です。schema、CLI引数、ID、control、台帳、writer範囲は変更しません。

TDDは実migration公開入口で一件を再現。Redは1 failed（期待0に対しmigration exit6）、Greenは1 passed。新backupのlink mode0777・link値維持、source link0777、外部target bytes/mode0640の不変、backup_verified/restore_verified=trueを確認しました。必要な回帰・導入・実運用結果は続報で記録します。

## 先に判明した別の前提条件

同cloneのGit一覧は5 WT。このWT以外に旧activeやworkspace宣言のないWTが存在します。許可なしに別WTを書き換えません。また実GitHubでEpic #356とIssue #413はOPENですが、親initiative `init-local-00003` が参照するGitHub #31はCLOSEDで、titleも `Replace Wrapper Scripts With Symlink Rules` でした。正式import/Startの前提成立とは扱わず、祖先の自動reopen・linkage変更は行いません。

この記録の導入・実環境適用結果は、495d10abで得たマージ前FQ certificationとは別の証拠です。追加修正後のcandidate検証が完了するまで、旧certificationを新コードのpassとして転記しません。

## 既知static資産の更新対象漏れ

消費側scripts/README.mdは比較基準6fec3099のprovider配布元blobと完全一致し、SHA-256は `38b8a802dcac5e0e3ba4505ddac63fd89380c370b60443cdfb2734ada698b794` でした。既知旧hash一覧だけが空だったため、自動更新ではunknownとなります。履歴で照合したこのhashと、直前candidateの配布元hashだけを既知版へ追加し、改変資料は引き続き拒否します。併せて配布元READMEの旧cache・固定engine・active取得手順を現行CLI契約へ更新しました。消費側を直接上書きする代替操作はしていません。

公開installation update入口のTDDは、完全一致する旧READMEと同じREADMEへの利用者追記を実fixtureで区別します。Redは旧版の誤拒否1 failed・改変版の正しい拒否1 passed。Greenは2 passed、旧bytesの外部backup・新provider bytes一致と、改変時のeffects=[]/backup未作成を確認しました。移行・installation・構造validate・実wheel配布の関連選択は全件成功です。

## 全件テストでの独立した観測

最初のmacOS全件は `2 failed, 1898 passed, 1 skipped`（actual exit 1）でした。失敗は構造validateの読取不変テスト2件で、fixtureのGit内部にpack/info/refsが追加されたことが直接の差分です。backupのmode不具合とは異なり、この3行修正はvalidateの処理を変えていません。Git背景処理かどうかは未確定で、原因を確定済みとは記録しません。テストの不変条件を緩めず、そのままのvalidate関連80件は成功しました。最初の失敗ログは保持し、新しいcandidateの全件結果で再確認します。
