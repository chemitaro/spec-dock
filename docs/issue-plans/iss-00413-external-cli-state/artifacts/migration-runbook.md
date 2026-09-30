# 移行runbook — controlを作り直さず通常CLIへ移る

**全て将来の手順です。実環境での実行、backup、導入、正式import、Startは未実施です。** 製品candidateの受け入れ・人間merge・対象への明示許可を得てから [P-16/P-17](../plan.md#p-16) で実行します。新しいコマンド契約を示す文書であり、基準SHAでそのまま動く手順ではありません。

正本は [D-12](../design.md#d-12)、公開syntaxは [CLI契約](cli-contract.md) です。本手順は一回の切替のための保全であり、以後の全編集にmaintenanceや共有管理台帳を要求する仕組みではありません。

<a id="m-01"></a>
## M-01 対象と実行物を固定する

対象は、利用者が許可した同じcloneと、今回適用するworktreeです。Gitの通常一覧、各root/common-dir、現在branch/HEAD、tracked/untracked/ignoredの内容を読取り、remote URLだけでcloneを同一視しません。main worktreeへの移動は必要ありません。別clone・別PCを探索しません。

外部CLIは承認candidateから作った通常wheelをcheckout外の環境へ非editable installします。実consoleの絶対path、package version、source SHA、wheel SHA-256、OS/Python/FSを実施者の記録に残します。source開発用の `uv run` と、consumerが使うinstalled consoleを区別します。旧fixed bundleを生成し直しません。

| 確認 | 合格条件 | 停止条件 |
|---|---|---|
| 実行物 | candidateとwheelの対応を示せる | 由来不明、sourceや旧engineへのfallbackがある |
| 対象 | Gitが返したroot/common-dirと許可範囲が一致 | path接続不正、別clone、想定外の作業場 |
| 保全先 | 全checkout・Git管理領域・install先の外にある所有者指定の保存先 | cache扱い、容量不足、保存先/保持責任が不明 |
| 対応環境 | 新しいOS原語・実consoleの実試験結果が対象構成に対応 | 未試験を合格扱いする必要がある |

通常Gitの例は `git -C ROOT worktree list --porcelain -z`、`git -C ROOT status --porcelain=v1 --untracked-files=all` です。ROOTは実在する許可pathへ置き換えます。ignored成果物はstatusだけでは把握できないため、所有者が別途確認します。Gitの出力を含め、認証情報や私的な成果物を公開レポートへ転載しません。

<a id="m-02"></a>
## M-02 旧writerを止め、実体を保全する

同じ対象に書き込む旧CLI、agent、shell alias、scheduler、旧venvなどの起動元を止めます。停止元不明・自動再起動を止められない場合は適用しません。新workspace宣言や新mutexが旧writerを強制封鎖するとは考えません。通常編集を常時監視・権限管理する機能は追加しません。

保全対象は、仕様/R/D/P、Artifact、Workbench、未commit/ignoredの利用者成果物、workspace宣言、旧active、旧registryの任意branch対応・予約・削除記録、未完了journalと必要な前像、必要なGit状態、更新対象static資産です。旧engineが別consumerと共用されている場合、その実体を無断で消しません。

実体を外部保全先へコピーし、bytes、entry type、mode、link、必要なhashを確認します。別の隔離directoryへ復元して比較します。manifestだけを作って「backup済み」としません。任意symlink/特殊fileはCLIに勝手に追跡させず、人が適切な方法で保全します。`git clean -fdx`、`git reset --hard` を保全の代わりに使いません。

**[../report.md](../report.md) と [interview-worktree-start.md](interview-worktree-start.md) はCodex所有の原文のまま保持します。** 本packから生成せず、差替え・移動の前後でhashを確認します。この二つはZIPのpayload manifest外です。記録の追記が必要な場合はCodexが自分の実行事実として追記し、ChatGPTの文書自己点検と混ぜません。

<a id="m-03"></a>
## M-03 controlなしで診断し、旧状態を扱い分ける

新しい外部consoleで最初にutilityとreaderを確認します。以下は例示pathで、導入済み実consoleを使用します。

```text
spec-dock --help
spec-dock --version
spec-dock --project /projects/spec-dock workspace doctor --raw --legacy --json
spec-dock --project /projects/spec-dock workspace validate --json
spec-dock --project /projects/spec-dock active show --json
```

旧controlの欠落を直すために `engine.json`、`control.json`、registryを手作成しません。通常readerが旧.gitを必要としないことと、legacy診断が旧.gitの読取を明示的に許すことは別です。legacy診断も旧状態を書き換えません。

| 観測した旧状態 | 保全・確認 | 新しい方式への扱い |
|---|---|---|
| controlがない | 不在を今回観測する。過去の予約まで不存在とは断言しない | readerと移行planを進められる。controlを生成しない |
| 正常control/registry | 必要な履歴、任意branch名、旧選択を人間向けに保全 | 新しい中央台帳へ移植しない |
| activeがある | 最後に選んだ直接focusと現在Git/Scopeを人が確認 | 新recordへ自動変換しない。後で明示Startする |
| local予約/high-water/tombstone | 過去の意味が必要なら証拠を保存 | 新規GitHub発行だけ。永久再import禁止は引き継がない |
| Startの途中記録 | 実branch/ref/HEADと選択を照合 | 成功済みGit効果を保ち、新しい明示操作へ。旧resumeなし |
| Close等のremote結果不明 | 固定refがあればGitHubを読取り、なければ人が特定 | unknownを未送信にしない。勝手な再POST/PATCHなし |
| 移行/installationの途中 | source/target/backupの現物を比較 | 新journalへphase移植せず、安全に特定した差分だけ適用 |
| 破損/未知journal | 読める範囲と読めない範囲を分離して保全 | 影響対象を特定できなければ、その対象への適用を停止 |
| Gitに残る消失/prunable WT | Gitの通常診断と実体確認 | 自動pruneしない。Startの重複確認は完了扱いにしない |
| ignored内に手作り資料 | 生成物と決めつけず本文を保存 | 残すものを明示して採用。無差別purgeなし |

旧選択がなくなることを対象の完了と呼びません。旧phaseを読み取れたことも、remoteやファイルの実状態がそのphaseどおりである証明にはなりません。

<a id="m-04"></a>
## M-04 workspace宣言だけを明示的に切り替える

前提はschema3、既知の旧writer宣言、妥当な現在のScope構造です。利用者/Codexの添付記録は240件のschema3/githubと二つのlocal綴りGitHub IDを報告しています。適用時に実件数と全metadataを再検査し、今回の期待との違いがあれば原因を確認します。自動で240件に合わせたり、全件schema変換を追加したりしません。

```text
spec-dock --project /projects/spec-dock workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 --dry-run --json
spec-dock --project /projects/spec-dock workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 --backup-dir /backups/specdock-cutover-01 --confirm-old-writers-stopped --yes --json
```

上のbackup pathは説明例です。実体保全先を明示し、既存backupへ無条件上書きしません。dry-runはlock、stage、backup作成、Git/GitHub変更をしません。本実行は改めて現物を検査します。

許可するtracked差分は自worktreeの `spec-dock/workspace.json` のwriter_protocolを `specdock.worktree-writer/v1` にし、存在する旧control_epochだけを除くことです。schema_versionは3。title/project_linkageが元々なければ追加しません。未知の任意設定を保持します。全Scope metadataのID/path/backend/linkage/親子/依存/本文のbytesは不変です。

migrateはStart共通ロックを取得しません。切替中の同じworkspace編集を人間の一回の運用前提として止め、before bytesとentry identityを再確認して一fileをatomic公開します。これは通常編集全体のロック制度ではありません。旧.git独自file、別worktree、Git ref/index、remoteを変更しません。

公開前の中断は旧宣言、公開後の中断は新宣言を現物から判定します。新宣言で妥当なら次のmigrateはunchanged。未知schema/protocol、backup不備、想定外の後続編集は停止し、以前の操作を自動resume/rollbackしません。

<a id="m-05"></a>
## M-05 static資産・旧入口と通常操作を確認する

`installation update` はinstalled packageの既知static資産だけを対象worktreeへ適用します。package本体の更新は通常package managerの作業です。未知改変資産があれば上書きせず人間が比較します。旧runtimeの存在だけを理由にdirectoryを丸ごと削除しません。退役する既知のtool-owned fileは保全して明示allowlistで処理し、旧.gitはその対象外です。

```text
spec-dock --project /projects/spec-dock installation show --json
spec-dock --project /projects/spec-dock installation update --backup-dir /backups/specdock-assets-01 --dry-run --json
spec-dock --project /projects/spec-dock installation update --backup-dir /backups/specdock-assets-01 --yes --json
spec-dock --project /projects/spec-dock workspace validate --json
spec-dock --project /projects/spec-dock workspace sync --source local --json
```

新shimは外部consoleへ委譲するだけです。更新前または旧branchへcheckoutした後の `./spec` が旧controlエラーになる場合でも、外部consoleを直接使用します。無断で別engineを探しません。新shimの導入確認と外部CLIの成立確認を分けます。

`.agent/` のignoreが現在のcheckoutで有効か確認します。Start前にtracked/ignore検査が通らなければ止め、static差分を人間がレビューします。ignoredなdirect recordをGit内部へ移すことで解決しません。

別のlinked worktreeでも同じ通常CLIを起動できます。各worktreeへの宣言切替とstatic適用は許可された対象ごとです。同じcloneの全worktreeへ一括適用しません。ただしStartの重複確認で旧形式・壊れた記録や読めないworktreeが見つかる場合は、観測が完全になるまで新規開始を止めます。通常の独立readerまで全体停止にはしません。

<a id="m-06"></a>
## M-06 既存#413を正式importし、正文を保全移動する

[P-17](../plan.md#p-17) の独立した実環境作業です。実施直前にGitHub #413が目的のIssueであること、現在treeに同じID/refの登録がないこと、親epic-00356と祖先が存在し必要なopen条件を満たすことを再確認します。既存#413を新しいcreateで作り直しません。親の自動reopen・別親への付替えもしません。

```text
spec-dock --project /projects/spec-dock scope import github issue gh:chemitaro/spec-dock#413 --parent epic-00356 --title "External CLI State" --slug external-cli-state --dry-run --json
spec-dock --project /projects/spec-dock scope import github issue gh:chemitaro/spec-dock#413 --parent epic-00356 --title "External CLI State" --slug external-cli-state --json
```

importの成功出力が返すScope ID/pathを使います。実体 `.meta.json` を手作りして成功の代用にしません。生成されたR/D/Pの空templateに既に人の編集がないことを確認し、例外配置 `docs/issue-plans/iss-00413-external-cli-state/` から本packのpayloadを採用します。Codex保有のreportとinterviewは実体のhashを保って同じ相対位置へ移します。import生成reportが存在していても、保有記録を空templateで上書きしません。

相対link/anchor/schema/manifestを検査し、旧例外配置の正文は撤去または新しい正式配置への案内だけにします。旧R/D/P本文を二箇所で維持しません。元ZIPは配布時点のarchiveであり、その後の第二正本ではありません。正式配置への移動や実施者の追記に伴う採用manifestはCodexが新たに計算し、元ZIPの来歴と混同しません。

**import直後はtracked差分が生じます。Startはcleanと切替先commitの対象存在を要求します。** 利用者の通常Git保存・レビュー・必要なcommitを明示許可の範囲で完了し、対象/祖先/schemaを候補commitに含めます。本runbookは自動commit/pushを行う仕様ではありません。

既存の復旧用branchを利用する場合、名前とtipを通常Git/branch showで確認し、例えば `work start iss-00413 --branch codex/iss-00413-external-cli-state --dry-run --json` を新契約で確認します。既存branchなので--baseは付けません。新branchを作るなら許可された未使用名と--baseを明示します。出力を確認してから同じ引数の本実行へ進みます。

Start成功の証拠は、実consoleのexit、current branch、妥当な一件record、他WT重複なしの確認です。import成功や文書配置だけでStart成功とはしません。資料移動が終わっただけで#413をFinishしてCloseしません。製品受け入れと人間の完了判断後のFinishは、別の明示実施です。

<a id="m-07"></a>
## M-07 結果を分けて記録し、失敗は現物から判断する

| 証拠 | 何を示すか | 示さないこと |
|---|---|---|
| ChatGPTのself-check | このZIPの文書構造・schema・hash等 | 製品テスト、ブラウザの実描画、実導入 |
| Codexの文書検査/ブラウザ結果 | 採用後のリンク・図・modal・viewportの実測 | 製品runtimeの動作 |
| candidateの通常CIとfresh wheel E2E | 指定candidate/fixture/OSでの製品検証 | 実対象への導入、live GitHub変更 |
| 人間merge | source統合の判断と実施 | package公開やdogfood切替 |
| dogfood cutover | 許可した対象への導入/宣言切替/reader確認 | 他consumer全体の移行 |
| #413 importとStart | 正式Scopeと作業開始の現物 | 製品完了、Close、配送やmerge |

Git効果後の失敗では、元のGit stderr、CLI exit、各effects、現在branch/ref、選択の有無を記録します。GitHub unknownは確認不能のまま残し、再送前に現状を照合します。出力を失った新processが前回のintentを復元できるとは記載しません。

適用前なら新writerを止め、backupとbefore bytesを照合して限定したworkspace/static差分を人が戻せます。新しいScope、GitHub変更、後続編集がある場合はそれらを保全・統合し、source revertだけでremoteまで戻ったとしません。旧writer再開には旧方式自身の前提確認が必要です。旧control再生成、無条件hard reset、git clean、blind retryを標準の復旧手順にしません。
