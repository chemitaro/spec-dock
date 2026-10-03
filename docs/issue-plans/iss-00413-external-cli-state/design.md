# Issue #413 設計書

原本生成時の状態: 対応OS決定と第三者分析を採用した設計。P-18は未実装。検証済み対象SHAは `121228c6fca1fd016e7bccef009902396112ba43`、main比較基準は `6fec3099d8759b4e5b3b393b2987534b46dfa383`。

2026-10-02の採用後進捗: P-18とP-07の候補実装、Linux/macOS通常全件、両OSの外部console個別操作、新OS範囲Code Reviewを確認しました。[対象SHAと実結果](artifacts/supported-os-verification-3b803ced.md)を参照してください。本書の要求/設計意味を変えず、Final Quality Gate・人間merge・実導入の完了と分けて記録します。

[要件](requirement.md) / [CLI契約](artifacts/cli-contract.md) / [実装計画](plan.md) / [出典](artifacts/source-basis.md)。本文のAPI名・新pathは実装予定の契約であり、基準に存在するとは限りません。

<a id="d-01"></a>
## D-01 採用する小さな構造と判断の区別

通常の `spec-dock` processが、現在worktreeの仕様と最小の直接対象を読み、必要なGit/GitHub操作をして終了します。main worktreeも同じ利用者です。Gitの一覧がworktreeの正本であり、SpecDockによる登録・常駐管理はありません。

| 判断 | 採用する具体案 | 根拠・代償 |
|---|---|---|
| 外部実装 | `spec_dock.runtime` を通常wheelの唯一のruntimeにする | Q&Aの通常CLI。checkoutで実装が変わらない |
| 直接状態 | `.agent/work-target/` の変更しない一件ファイル | 保存先/schemaは技術判断。固定pathnameの遅い解除が次の選択を消す事故を避ける |
| 排他 | common-dirの物理identityに対応するOS排他をStartのみで取得 | 利用者の短い開始排他。ファイル編集やFinishを参加させない |
| active | show/clear維持。setは同一対象no-opに限定、取得はStartへ | 任意setをlock外に残すと重複禁止を迂回する。第二の閲覧状態も増やさない |
| 親の扱い | 直接対象から祖先を導出し、解除/Finishで親を選ばない | 一直接対象と親配下集計を両立。従来の自動昇格を明示変更 |
| Sync | コマンド名を維持し、その場のstdout/JSON表示にする | 世代・cache・中央選択コピーを廃止する必要な効果変更 |
| 同じ対象の定義 | 完全Scope ID一致、または完全GH linkage一致を重複とする | 旧ID綴りの違いで同じ実Issueを二重開始しない |
| writer宣言 | schema3を維持しworkspaceだけ `specdock.worktree-writer/v1` へ切替 | 全Scope変換なし。旧writer封鎖の証拠ではない |
| CLI範囲 | 既存44 leafを維持し、台帳依存の機能/optionだけ退役 | 新namespace/Release/管理制度を追加しない |
| 対応OS | Linux/macOSのPOSIX原語だけを製品契約に残す | Windows adapterを完成させず、代替管理基盤も追加しない |

上表の実装細部を利用者が逐語承認したと記録しません。Q1〜Q8と合意事項は [確定回答](artifacts/user-decisions.md) にそのまま保持します。技術上の具体化が要求に反することが判明した場合は該当実装を止め、本設計を直してから進めます。

<a id="d-02"></a>
## D-02 通常package、入口、context

### 唯一の実装とutility

`pyproject.toml` の `spec-dock = "spec_dock.cli:main"` は維持します。asset内RTを `src/spec_dock/runtime/`（以下NRT）へ移し、通常subpackageとして配布します。import先を `spec_dock.runtime.*` に統一します。`assets/scripts` をsys.pathへ追加する処理、fixed bin/lib、独自version.txt要求、digest pin、別runtimeへのfallbackを通常経路から除きます。installed metadataでversionを取得します。pyprojectのPython>=3.10を維持し、3.11専用APIを無条件で使いません。

root/leaf help、version、completion、syntax/廃止入力判定を先に行い、Git/project/control/ネットワークと対応OSguardを解決しません。`--project` が壊れていてもhelpは動きます。引数parserを使うためにbusiness/contextをimportしてIOしない構造にします。utility dispatch後の業務コマンドだけ、`runtime_dispatch.dispatch` の先頭でLinux/macOSを確認し、非対応OSはproject/Git/GitHub/file効果前に `UNSUPPORTED_PLATFORM`・effects=[]で止めます。この一箇所のguardを広範なOS抽象化へ発展させません。v2 JSONを一度だけ出力する責務はpresentationに置きます。

consumerに配布するのは仕様template、説明・skills等のstatic資産だけです。Python runtimeのコピーは配布しません。static資産の読取はpackageの `importlib.resources.files("spec_dock")` から行い、filesystem上の固定lib配置を仮定しません。`setup.py` のbuild先清掃とbytecode除外を保ち、sdistからのwheelも同じ収録内容にします。

### 既存 `./spec` の扱い

標準入口はPATH上のinstalled `spec-dock`。互換の小さなshimは、明示されたstatic資産更新で、外部consoleへargvをそのまま渡すだけの橋へ改修します。Git common-dirやconsumer Pythonを読みません。自身/同一shimへの再帰委譲は実行前に拒否し、外部console不在はインストール案内と非0で返します。自動installも旧engine起動も行いません。旧branchから旧shimが戻っても外部consoleを直接使えることを説明します。新shimのhelpも外部consoleのhelpへ委譲します。

### context契約

| API（新契約） | 入出力・責務 |
|---|---|
| `cli.main(argv=None) -> int` | utility/parse→必要ならcontext→dispatch→presentation。終了値を一回返す |
| `resolve_context(project, cwd) -> ProjectContext` | 明示root優先。Git root/common-dirの実体、workspace宣言、現在branch/HEADを取得 |
| `load_scope_views(root) -> tuple[ScopeView,...]` | 現在worktreeのschema3、ID、親子、linkageを読む。既存未知fieldを保持 |
| `read_selection(context) -> SelectionObservation` | 自worktreeの直接一件と、その場の祖先を読む。IO状態をemptyと混同しない |
| `observe_worktrees(context) -> WorktreeObservation[]` | Git inventoryと各worktreeの直接記録を読む。保存しない |

`ProjectContext(root, common_dir, clone_identity, worktree_identity, head, branch, workspace)` をメモリに持ちます。永続worktree_id/epoch/engine_digestを要求しません。明示rootが不正なら親repoやdefault branchへfallbackしません。裸repositoryでは通常業務を拒否します。submoduleは別common-dirの別対象です。呼出側のGIT_DIR/GIT_WORK_TREE等による対象すり替えを防ぎ、argv配列でGitを呼びます。

readerは既知schema3の旧writer宣言でも安全な範囲を読めます。通常writerは自workspaceの新宣言を要求します。旧宣言なら明示migrateを案内します。未知schema/protocolは通常writeを止めますがhelpとdoctorの安全なraw診断は可能です。他worktreeのwriter宣言を自分の通常編集の許可条件にはしません。

<a id="d-03"></a>
## D-03 直接対象の保存場所・schema・寿命

### 一件だけの保存

保存先は `<worktree-root>/spec-dock/.agent/work-target/target-<32桁lower-hex>.json`。有効な最終ファイルは0か1件だけです。32桁tokenは `secrets.token_hex(16)` 相当の**一つの保存実体の名前**であり、Scope UUID、採番、operation ID、履歴ではありません。同じScopeを選び直しても新しい名前を使い、名前を再利用せず、公開後の内容を書き換えません。古い記録は解除時に削除し、履歴を蓄積しません。

既存assetの `.gitignore` は `.agent/` を無視します。ただし各checkoutで `git check-ignore` と `git ls-files` を用い、記録pathと既存親がtrackedではなくignore対象であることをStart前に検査します。違う場合は `WORK_TARGET_PATH_NOT_IGNORED`、副作用前停止。Startが `.gitignore` や `.git/info/exclude` を勝手に書き換えません。必要なignore規則は明示static更新/人間レビューで整えます。

保存例は [examples.json](artifacts/examples.json) の `work_target`。機械構造は [data-schema.json](artifacts/data-schema.json) の `$defs/work_target` です。

| field | 型・意味 |
|---|---|
| schema_version | 定数 `specdock.work-target/v1` |
| scope_id | 保存済み完全Scope ID。旧local綴りを改名しない |
| github_ref | 正規化した `gh:owner/repo#number`。真正の既存local backendだけnull |
| selected_branch | 開始確定時のbranch名。履歴/手掛かりでありbinding正本ではない |
| selected_at | UTC RFC3339。期限や稼働判定には使わない |
| clone_identity | Git common-dirのPOSIX物理identity `(st_dev, st_ino)` |
| worktree_identity | worktree rootのPOSIX物理identity `(st_dev, st_ino)` |

親ID、GitHub完了値、PID、Codex実行状態、branch対応表、revisionカウンタ、operation phase、remote送信意図、全worktree一覧を保存しません。`SelectionObservation` は `status=empty|selected|stale|unavailable|invalid`、直接record、token、現在branch、現存祖先、理由をメモリ上に持ちます。CLIの `selection_token` は保存実体名から得た不透明値で、過去操作の再開tokenとして受け付けません。

### 公開と解除の最小原語

`WorkTargetStore.read() -> SelectionObservation`、`publish(record) -> SelectionHandle`、`remove_observed(handle) -> removed|already_absent|conflict` を用意します。`SelectionHandle` は安全に開いたdirectory、basename、inode/file identity、bytes hashをそのprocessだけが保持します。

Startのロック内で完成JSONを同directoryの `.stage-<random>` に排他的作成し、write/flush/fsync後、Linuxの `renameat2(RENAME_NOREPLACE)` またはmacOSの `renameatx_np(RENAME_EXCL)` によって未存在の最終名へ無上書きrenameし、directoryを同期します。最終名だけを読取対象にし、不完全なstageを選択と見なしません。並行Startは共通排他に参加するため同じ保存先に最終recordを二つ作りません。未知の最終名/特殊fileを見つけたら勝手に上書きしません。Windows move adapterは設計・実装対象から除きます。

解除は読取時の**正確なbasenameだけ**を消します。最新recordを再読込して「現在の一件」を無条件unlinkする実装は禁止です。basenameは再利用されないため、Finish Aの遅い解除は新しいBや新しいAに触れません。既に旧basenameがない場合は `already_absent`。保存先directoryのidentityが変わった場合は停止します。nofollow/descriptor基準でpathを扱い、手動の悪意ある置換まで原子的CASと主張しません。

`--switch-active` による置換はGit効果完了後、ロック内で旧basenameを解除してから新recordを公開します。二件並存を避けるため、この短い隙間では無選択を観測し得ます。旧解除後に新公開が失敗すればselection lossをpartialとして返し、旧対象を自動復活させません。これは二ファイルtransactionではありません。

### 消失・破損・寿命

有効recordは明示clear/該当Finish/許可されたworktree削除まで存続します。branch変更、process終了、GitHub Close、日時経過では解除しません。新cloneや通常worktree addにはignored記録がコピーされないので空です。同FSでの移動はGit repair後に同identityなら維持でき、別FSへのコピーはidentity不一致で自動採用しません。媒体やinode再利用を超えて世界的一意性を保証するものではありません。

0件はempty。2件以上、未知schema、壊れJSON、symlink/特殊file、読取権限不足はinvalid/unavailable。選択を一件選び出さずStartを止めます。`active clear --all --yes` は自分のdirectoryで観測した正規basenameの通常fileだけを解除でき、壊れJSONでも明示的に捨てられます。読取不能/redirect/未知entryは削除せず、人が外部へ保全・調査します。新しく現れたbasenameはこのclearの対象外です。stage残骸は診断だけで自動resumeや一括purgeをしません。

ignored記録は `git clean -fdx` などで失えます。台帳がないので復元できたと偽らず、Git/remote確認後に新しいStartで選択し直します。

<a id="d-04"></a>
## D-04 Gitの一覧とbranch切替後の意味

一覧は `git -C ROOT worktree list --porcelain -z` をNUL区切りで解析します。pathをstrip/splitlinesで壊しません。main/linked、HEAD、branch、detached、bare、locked、prunableを保持します。一覧のpathから得たcommon-dir identityを照合し、aliasは物理identityで重複排除します。別cloneのディレクトリを外部探索しません。

| 状態 | Startでの扱い | Sync/showでの扱い |
|---|---|---|
| 読める同clone WT、新記録も未移行の旧選択もなし | 直接対象なしとして検査 | empty |
| 新recordなし、旧writer宣言で旧active.jsonが残る | 未移行の選択を空と見なさず開始前停止 | legacy/unavailableのfinding、complete=false |
| 妥当な直接記録 | ID/refを重複検査 | selectedと現branchを別表示 |
| branch変更、対象/祖先が現在treeに存在 | 記録を保持、現在条件で評価 | selected、branch_changed=true。名前から別対象を推測しない |
| 対象が現在treeから消えた/リンク変更 | 既知ID/refを予約として保持。自対象の動的操作を停止 | stale。過去の親を保存値で捏造しない |
| WT path消失・読めない・common-dir不一致 | 完全な重複確認不能として開始前停止 | 行を残してunavailable、complete=false |
| prunableだがまだGit inventoryに存在 | 消えた扱いにして無視しない | Gitの理由を表示。自動pruneなし |
| Git inventoryから明示remove/prune済み | 対象集合外。別名簿で探さない | 通常一覧から除外 |
| JSON破損/複数最終record/identity不一致 | invalid、開始前停止 | 不明点を表示。空や完了にしない |
| GitHub completedだが記録あり | 依然直接選択であり、他WTの重複開始を止める | selected=trueとcompletedを同時表示 |

新recordがないWTではworkspace宣言と旧 `.agent/active.json` の存在も安全に確認します。旧宣言と旧選択が共存する場合は新選択へ変換せず、当該WTの保全・明示移行を求めます。新writer宣言へ明示移行済みで残る旧activeは退役資料であり、新recordと合成しません。宣言やpathを読めず区別できない場合はunavailableです。これは起動全体の旧control検査ではなく、Start/Syncで選択を空と誤認しないための観測です。

Startはロック取得後に一覧と直接記録を必ず取り直し、記録公開前にもinventory/対象identityを確認します。列挙直後の外部Git worktree変更や手編集を完全に封鎖する仕組みは追加しません。差分を検出したら後続効果を停止し、既にGit効果があればpartialです。

通常の `scope show ID` は自treeだけを読むため、無関係なWTの不調で停止しません。Syncは可能な行を返す診断として不完全性を示します。これを全writerのready判定に流用しません。

<a id="d-05"></a>
## D-05 Startだけの共通排他とPOSIX物理識別

### 保証する区間

入力検証→対象/切替先snapshot確定→必要なGitHub GET→利用者確認をロック外で済ませます。**ロック取得後、Git inventory再取得・重複確認→branch作成（必要なら）→checkout→対象の事後照合→旧対象解除（明示切替時だけ）→新記録公開/確認までを一つの区間**にします。記録前に解放しません。成功/失敗/取消いずれもfinallyで解放します。

GitHubの最新性は今回の明示観測であり、世界的なatomic transactionではありません。取得した対象/依存snapshotがロック内のlocal再観測と一致しなければ、Git効果前に止めます。remote再観測が必要な場合は解放して新しい操作としてやり直す案内を出し、ロック内にnetwork待ちを戻しません。外部GitHub writerとのraceまでlockで防げるとはしません。

### Linux/macOSの最小原語

| OS | identity / 排他 | 公開・終了・異常 |
|---|---|---|
| Linux | 開いた既存common-dir/rootの `fstat(st_dev,st_ino)`。read-only directory descriptorへ `fcntl.flock(LOCK_EX\|LOCK_NB)`。新しい.git entryを作らない | `renameat2(RENAME_NOREPLACE)`、file/directory fsync、LOCK_UN/close。descriptorは非継承。原語不足は副作用前停止 |
| macOS | 開いた既存common-dir/rootの `fstat(st_dev,st_ino)`。read-only directory descriptorへ `fcntl.flock(LOCK_EX\|LOCK_NB)`。新しい.git entryを作らない | `renameatx_np(RENAME_EXCL)`、file/directory fsync、LOCK_UN/close。descriptorは非継承。原語不足は副作用前停止 |

identityは `{platform:"posix", device:string, file_id:string}`。`device` と `file_id` はunsigned整数の10進文字列です。branch名、remote URL、path文字列、Scope番号をidentityやlock keyにしません。common-dir/rootのdescriptorは操作の間保持し、pathが同じでも実体が変われば停止します。

Windows named mutex、VolumeSerialNumber/FileId128、Win32 directory/JSON handle、WAIT_ABANDONED、NTFS受入は削除対象です。非対応OSを動かすためのLocal namespace、PID file、mkdir lock、独自lease台帳、ACL変更、registry/cache/daemon、別storeへのfallbackを作りません。utilityはD-02の順序で独立し、業務コマンドは一つの対応OSguardで副作用前に停止します。

`--lock-timeout` は取得待ちだけ。既定5秒、0は即時、有限0〜300秒。単調時計で総待ちを測り、NaN/inf/負数を拒否します。Git subprocess `--timeout` は既定30秒、有限0超〜300秒。一回の呼出しの上限です。短い区間とは効果のために必要な区間であり、何ms以内という架空の実測保証は置きません。Git timeout時は現在ref/HEADを安全に再観測し、確定不能ならunknownです。

通常編集、metadata/依存/Artifact操作、branch単機能操作、worktree操作、Sync、GitHub操作、Finish、active clear、migrate、installationはこの共通ロックを取得しません。OSファイル公開の原子性やGit自身のindex/refロックは、SpecDock全writerロックとは区別します。

Linux local filesystemとmacOS APFSで別processの保持/timeout/kill後解放、同clone/別clone、no-follow、publication/removalを実測します。network filesystem、複数host、異なるOSの同時mountは保証対象外です。OS API文書やmockだけで対応を認定しません。[対応OS撤去計画](artifacts/os-support-retirement-plan.md)を参照してください。

<a id="d-06"></a>
## D-06 Startとbranchの順序・途中失敗

### branch決定

公開syntaxは `work start TARGET [--base REF] [--branch NAME] [--switch-active]` を維持します。新規候補は従来同様 `<Scope ID>-<slug>`、--branchがあればその名前です。registryは参照しません。

候補branchがない場合は--baseを必須とし、commit OIDに一度固定します。候補が既存なら、**再利用は--branchによる明示指定を要求**し、--baseを拒否します。これは永久canonical bindingの代わりの明示承認です。暗黙候補が既に存在する場合は、名前を示して明示指定を求め、adopt台帳は作りません。ASCII/ref-format、HEADの40/64桁object format、他WTでの使用、clean、切替先のScope/祖先/schema/linkageを検査します。

`branch create TARGET --base REF [--name NAME]` は新branchだけ。`branch show TARGET [--name NAME]` / `branch switch TARGET [--name NAME]` は明示名または既定候補を対象にし、永久bindingの存在とは表示しません。branch switchは選択を書き換えません。全て既存refをresetしません。

### Start APIと実行順

`plan_start(request, context, local_snapshot, live_observations) -> StartPlan` はメモリ値だけです。`StartPlan(target_id, github_ref, branch, resolved_tip, create_branch, expected_local_hashes, old_selection_handle, switch_allowed)` を返します。dry-runは同じ検査を行いますが、ロック・Git変更・stage・記録を作りません。dry-run成功は予約ではなく、本実行は再検査します。

`start_work(plan, ports) -> OperationResult` は次の順序です。

1. 自分の直接対象が別なら--switch-activeを要求する。同祖先やcompletedだから暗黙で捨てない。既存の通常資料を保存/commitする必要があれば利用者へ返し、自動stashしない。
2. 自/他WTの暫定観測、切替先metadataと実効依存、GH live条件を確認する。target自体と祖先はopen、依存先自体はcompletedを要求する。
3. D-05の共通排他を取得。current root/common identity、必要metadata bytes、branch tip、clean、Git inventoryと全直接対象を再観測する。他WTとのID/ref一致は `SCOPE_ALREADY_SELECTED`、効果0。
4. 新branchなら固定OIDから作成し、refを確認。既存branchなら作成effectはunchanged。Gitの生stderrを捕捉して保持する。
5. checkoutし、HEAD/branchと対象snapshot、ignore条件、inventoryを再確認する。metadataをbranch間で自動コピーしない。
6. 同じ対象・同じbranch・同じ記録が妥当なら記録はunchanged。それ以外の許可済み開始は、捕捉した旧記録があれば解除し新recordをD-03で公開する。同じ妥当なScopeを別branchで明示Startする場合は--switch-active不要だが、新token/選択時branchへ置換する。異なるScopeだけは--switch-active必須。旧linkage不一致などのstaleを暗黙に採用しない。publish完了が直接選択の成立点。
7. 排他を解放して結果を返す。SyncやGitHub操作を後から自動付加しない。

### failure契約

| 境界 | 残す現物 | 戻り値・次の明示操作 |
|---|---|---|
| 入力/readiness/重複/lock待ち失敗 | 変更なし | exit2/3/4/5。原因修正後に新Start |
| branch作成失敗、未作成確認 | 旧選択/branch | exit5、Git原文。作成成否不明なら6 |
| branch作成成功、checkout失敗 | 新branchと旧選択 | partial6、branch succeeded / checkout failed / selection not_attempted。新branchを消さない |
| checkout成功、照合/公開失敗 | 現branchと成功済みGit効果。旧選択があれば残る | partial6、開始成功false。現branch/選択を読んで新操作 |
| 旧選択解除後、新公開失敗 | 現branch、選択なし | partial6、selection.clear succeeded / selection.publish failed。旧対象を自動復活させない |
| record rename後、同期/結果確認失敗 | recordが存在し得る | partial6、publish unknown（確認できた効果だけsucceeded）。active showで再観測 |
| 応答前に強制停止 | 上記境界までの現物だけ | JSONを返せない。次processに過去のintentがあると仮定しない |

例: branch作成だけ成功した後は `branch show ID --name NAME` と通常Gitでref/HEADを確認し、新しい `work start ID --branch NAME`（--baseなし）を使います。journal resumeでも自動retryでもありません。原文の `error: Your local changes ... would be overwritten by checkout:` を汎用「checkout failed」に置き換えません。JSON/秘密部分の最小秘匿はCLI契約を正本とします。

<a id="d-07"></a>
## D-07 activeと動的selectorの最小対応

基準のactive setはGit/lifecycleを変えず任意対象を選べます。しかし同じ直接対象を取得する入口をlock外に残せません。そこで**取得をStartだけに集約し、active用の第二ロックも第二の選択状態も作りません**。

| 操作 | 新契約 |
|---|---|
| active show | emptyをexit0で返す。direct/祖先/current branch/selected branch/staleを表示する |
| active set TARGET | 現在の妥当なdirectと同じならunchanged。空・別対象はWORK_START_REQUIRED/exit3、変更なし。資料閲覧はscope show TARGETを使う |
| active set --from-branch | exit2、binding台帳廃止を説明。branch名からIDを推定しない |
| active clear --all | 読み取った自worktreeの記録だけ解除。Git/remote効果なし |
| active clear --from TARGET | directまたは現在の祖先に一致すればdirect全体を解除。親へ昇格しない。既知チェーン外はunchanged、不明IDはexit4 |
| @current | direct IDを現在snapshotで解決。空はexit4、stale/invalidはexit3 |
| @initiative/@epic/@issue | 現在directから現在の祖先チェーンを導出。そのroleがなければexit4。保存済み親で補わない |
| @root | Artifact所有者だけ。ScopeやStart対象ではない |

branch変更後のstaleな記録を外す場合は `active clear --all`。--fromは現在の祖先を確定できなければ停止します。部分解除で親を選ぶ旧仕様を残すと、別WTで同じ親が選択されていてもlockなしに新取得してしまうため撤回します。

中断/引継ぎは既存のclearと通常Gitを使い、対象をCloseしません。`--switch-active` も明示的な選択変更であり旧対象の完了ではありません。新しいwork releaseはありません。clearは「観測した選択の解除」であり、進行中/未来のStartの取消ではありません。

<a id="d-08"></a>
## D-08 Finishの順序と遅い解除

`finish_work(request, context, gateway) -> OperationResult`。TARGETは一度解決して固定し、本実行は`--yes`を必要とします。dry-runは承認不要で予定結果のみ返します。共通Startロックもoperation journalも使いません。

1. 現在の明示対象と祖先/子孫を読取り、current selection handleを捕捉する。動的selectorをremote送信後に再解決しない。
2. target/全子孫の必要なGH状態をlive GETする。親のcompletedは全子孫自身がcompletedであることを要求する。unknown/open/not-plannedは子孫完了ではない。対象not-plannedはreopenが必要。
3. 現在の対象metadata/linkageが変わっていないことを再確認する。GH-backedなら `closed/completed` を一回要求し、応答/再GETで確認する。既にcompletedならPATCHせず子孫条件を確認する。真正の既存local backendだけは既存lifecycle codecで一metadataを更新する保全互換性とし、GitHubをCloseしたとは表示しない。
4. completionが確認できた場合だけ、最初に捕捉した自分の記録のうち、対象またはその配下に直接選択されていたものを `remove_observed` で解除する。別WTを変更しない。
5. current branchに留まって結果を返す。merge/push/branch削除、親の自動選択、Syncは行わない。

Close unknownなら選択は残します。Close成功で解除失敗ならpartial6と二つのeffectを別表示します。次の明示Finishは現在remoteをGETし、completedなら再PATCHなしで今の適切な記録だけ処理できます。これは過去operationの続行ではありません。

Finish AがGET/PATCH中に、利用者が既存clearまたは `Start B --switch-active` を使うことは、この設計のlockでは禁止しません。FinishはAのremoteだけを扱い、Aの旧tokenだけを解除します。Bのrecordへ置き換えられていれば旧tokenはalready_absent、Bは残ります。先に読んだscope idと後から再解決した@currentを取り違えません。

<a id="d-09"></a>
## D-09 Scope、依存、GitHub、既存データ

### schemaとID

現Scope schema3と既存numeric ID codecを維持します。IDのlocalという綴りからbackendを決めません。利用者/Codexの添付証拠では240件全てschema3/github、`init-local-00002`→#39、`init-local-00003`→#31です。本生成環境は240件全bytesを取得して再検査していないため、全件適合は後続試験です。work-target v1はScope metadataとは別で、identityだけをPOSIX形へ狭めます。schema/version/ID採番を増やさず、実在Windows recordが見つかった場合は変換せずP-18を停止します。

新規は既存syntax `scope create KIND --backend github ...` と `scope import github KIND REF ...` に限定します。--backend localはsyntax段階でexit2、正式local IDを生成しません。GH create成功/GET importで確認した番号を `format_id(prefix,number)` に渡します。kind別prefixはinit/epic/iss、最小5桁。UUID・予約・high-water・履歴採番は不要です。

新規scope directoryは従来の `<id>-<slug>` と三階層配置。CLI新規title/slugの既存ASCII入力契約は変えません。日本語本文はUTF-8です。current treeのID/ref重複、親kind/存在、path/metadata一致を確認し、他branchの同Scopeコピーを重複登録と呼びません。GH refはmetadataのowner/repo/numberから正規化します。importの裸番号は--github-repo付きだけ、普通のScope selectorは完全ID/gh参照/動的roleです。

構造schemaは [data-schema.json](artifacts/data-schema.json)。unknown任意fieldはdeep-copyで保持し、unknown required_featuresや未知schemaはwrite拒否。workspace必須はschema_versionとwriter_protocolのみで、title/project_linkageを架空補完しません。既存local backendが別consumerにある場合は読取・編集・close/reopen・保全を維持し、新規local発行やbackend変換を復活させません。

### lifecycleと依存

`github_lifecycle.GithubIssueGateway` の完全repository-bound GET/POST/PATCH、PR拒否、state_reason検査を再利用します。GHのclosedだけではcompletedとしません。not_plannedはnot-planned、未知理由はunknown。completed対象の同理由closeでも子孫条件を検査します。close not-plannedは現在の契約どおり子を自動完了せず、残る子を確認結果へ表示します。scope close/reopenはselection/Gitを変更しません。

実効依存は対象と祖先の宣言依存の集合です。親への依存は親自身のcompletedを必要とします。子の完了率/選択件数で代用しません。WaitGraphの `node→effective prerequisite` と `parent→immediate child` による自己待ち/循環検査を残します。依存更新には全writerロックを付けず、読取snapshotと公開前比較、後続validateで不整合を検出します。

### remote不明と公開

GH変更は一回だけ。現gatewayの確認GETは維持できますが、確認不能な効果を未送信として再POST/PATCHしません。作成応答不明ならlocal scopeを公開せずunknown/exit6。確定remote refの後にlocal公開が失敗すればrefを返し、新しい明示importを案内します。旧operation marker検索・journalは通常経路から外します。

新Scopeは同FSのstageに完成し、既存destinationがなければdirectory単位で公開します。metadata更新は一file単位のatomic replaceと必要なbefore bytes/identity確認を使います。新しい全writerロックや永続transaction intentを作りません。複数metadataにまたがるdelete/detachは前検査・保全・効果順序・partialを明記し、全体rollbackを約束しません。

<a id="d-10"></a>
## D-10 Syncは複数worktreeのその場の観測

`workspace sync [--source local|github] [--allow-invalid]`。既定はlocal（旧cacheはexit2で移行案内）。current treeの仕様を読み、Git inventoryに含まれる各WTからD-03の直接記録と、必要な対象/祖先だけを読みます。other WTの全Scopeの内容・実体を横断検証する方式や中央一覧の書込みをしません。

**2026-10-03採用A: IDから現在pathをGitで検索する。** 固定7fieldの直接記録を維持し、path locatorやcacheを追加しません。`git ls-files -z --cached --others -- PATHSPEC...` により対象IDを含む正規の三階層pathを検索します。ignore対象も検索し、現在の未追跡Scopeを落としません。環境変数を除去する既存Git adapterと有限timeoutを使い、NUL区切りを解釈します。追跡済みの旧pathが消えていれば候補から除き、現存する新pathを採用します。現存候補が複数なら曖昧な選択をせず停止します。対象と祖先のcontainer/directoryをnofollowで確認し、metadataのID、親、GitHub ref、構造を既存規則で検証します。対象不存在はstaleとして既知ID/refを保持し、検索失敗・重複・選択chainのredirect等はunavailableとして保持します。無関係なScopeのmetadata読取・実体検証は行いません。

Git内部の未追跡ファイル名探索は許容するため、IO全体を対象3件だけ・定数時間と約束しません。Gitの名前検索を許容することと、製品が全Scopeの内容や実体を検証することを区別します。この規則はStartの他WT確認、Sync、対象限定のactive解除、公開直後の未追跡Scope検証に共通適用します。現在tree全体を扱う通常の一覧/検証は従来どおり全件を検証します。

`SyncView(observed_at, source, complete, worktrees, scopes, counts, findings)` をメモリで作り、textまたはJSONへ返します。各WTのdirect、現在branch、選択時branch、selection状態、GH観測状態は別fieldです。Codex processは `process_state="not_observed"` 固定で、PID/セッションを調べません。

`scopes:ScopeObservation[]` は未選択を除外せず、現在treeの表示対象と他WTの必要な直接対象/祖先のlifecycleを保持します。各行はscope_id/github_ref/lifecycleで、選択件数は同じscope_idのcounts行に分けます。全読取成功時の未選択Scopeはdirect=0を明示し、GitHubのopen/completedとは独立して表します。型・不完全時の扱いは[C-03](artifacts/cli-contract.md#work)が規定します。

親の `descendant_selected_count` は自分以外の子孫を直接選択しているWT数、`direct_selected_count` はそのScope自体を直接選択しているWT数。例えば同じEpic配下A/Bの二WTならEpicはdescendant=2、direct=0です。Epicを別WTで直接選択していればdirect=1、descendant=2です。記録がGitHub closedでも選択件数に含め、completed件数とは別表示します。

他WTの祖先関係はそのWTの現在metadataから導出します。同じID/refに矛盾する親が観測されればconflictとして当該集計を不完全にし、一方を黙って採用しません。不明なWT/祖先があればknown件数は表示しますが `complete=false` とし、「全件0」と誤認させません。重複記録が手操作等で既にある場合は両行を示しduplicate findingを付け、自動解除しません。

--source localはGHを呼ばず、GH-backed lifecycleはunknown。--source githubは現在treeの表示対象と直接選択対象の必要なrefを一回の観測集合としてdeduplicateしてGETします。GET失敗は古い値へfallbackせずunknownにします。取得時刻は今回の時刻、完了確定は今回のstate_reasonだけです。

Syncはreadonlyなのでeffects=[]。妥当かつ読取が全て完了したらexit0、GH状態を意図的に未観測のlocal modeでもcompleteは「要求した読取集合」の完了を表します。modeがgithubで取得失敗、WT読取不能、許可された診断表示に構造不整合があればexit7/status=partial。安全に一行も構成できない場合はfailed/7（Git自体の環境失敗は5）。不明状態を正常完了にしません。--allow-invalidはpath安全性や未知schemaを迂回しません。

<a id="d-11"></a>
## D-11 既存ファイルと公開機能の変更対応

RT=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`、NRT=`src/spec_dock/runtime/`。次表の現pathは[tree/読取根拠](artifacts/source-basis.md#implementation)で確認しました。tree存在のみの群と本文読取を区別し、実装着手時に関係する全文を再読します。source内に `cli/context.py` を想定せず、実際の `cli/vnext_runtime.py::_context` を改修します。

| 現行file/群 | 対応 | 新しい責務 |
|---|---|---|
| src/spec_dock/cli.py, external_cli.py | 改修/統合 | 通常console、utility先行。fixed layoutの検査を除去 |
| runtime_loader.py, fixed_bundle.py | 通常経路/配布から削除 | Git common-dir helperはNRTへ。pin/bundle生成を復活させない |
| shim_vnext.py, assets/spec_dock/scripts/spec-dock, root spec | 改修 | 外部consoleへの薄い委譲だけ。既存ユーザー改変は保全 |
| pyproject.toml, setup.py, asset_layout.py | 改修 | NRTを通常package、static resources、旧runtimeを二重収録しない |
| RT cli/catalog.py, options.py, vnext_runtime.py, admission.py | 移設・改修 | 44 leaf、v2、contextと自workspace guard。global admission撤去 |
| RT commands/work_vnext.py, active_vnext.py, workspace_sync_vnext.py | 移設・改修 | D-06〜10の薄いadapter、new contextと正確なeffects |
| RT application/work_lifecycle.py, active_selection.py, branch_vnext.py, workspace_sync_vnext.py | 移設・改修 | Startだけの取得、Finish/clear個別token削除、registry不要のbranch、readonlySync |
| RT domain/ids.py, selectors.py, lifecycle.py, models.py | 移設・改修 | ID/metadata codec保持、直接一件と派生chain、WTpath selector |
| RT infra/active_store.py | 通常v3 writerを置換 | NRT/infra/work_target_store.py。旧読取はlegacy_readerへ分離 |
| RT infra/control_store.py, registry_store.py, writer_lock.py, operation_journal.py | 通常writer/参照を削除 | 必要な旧decodeだけlegacy_readerへ。StartLockは別の小module |
| RT domain/registry.py, branch_binding.py, operation.py | 台帳/復旧契約を削除 | 使わない型を互換aliasで温存しない。effects値はpresentationに残す |
| RT application/create_local_scope.py, resume_github_scope.py, operation_executor.py | 通常の新規/復旧経路を削除 | 既存local metadata codecはdomainへ維持 |
| RT application/create_github_scope.py, import_github_scope.py, scope_create_vnext.py, scope_completion.py, scope_delete_vnext.py | 移設・改修 | GitHub発行、局所公開、live lifecycle、partial。新journalなし |
| RT infra/git_cli.py, github_cli.py, github_lifecycle.py | 移設・改修 | NUL inventory、元Git出力、typed outcome、旧cache/marker/asset PYTHONPATH除去 |
| RT infra/generation_store.py, github_status_cache.py, failure_receipts.py | 通常経路から削除 | Syncはmemory表示、旧値はlegacy診断のみ。代替cacheは作らない |
| RT application/依存・Artifact・Workbench関連 | 移設・必要改修 | 既存業務・safety維持。writer admission/生成dirty/台帳引数を除去 |
| RT application/worktree_vnext.py, worktree_target.py, worktree_bootstrap_vnext.py | 移設・改修 | 明示NAME/path、Git一覧、明示make init。registry/receipt/recoverなし |
| RT application/installation_vnext.py, installation_update_vnext.py, migrate_workspace_vnext.py, engine_handover_vnext.py | 最初の3つを局所化、handover削除 | 明示static資産とworkspace宣言切替。全worktree更新/engine世代なし |
| src/spec_dock/installation のgroup_journal/journal/source等 | 利用箇所を検査して旧制御部分削除 | static差分/保全の再利用可能部分だけ維持。旧engine取得をしない |
| NRT infra/start_lock.py, identity.py, work_target_store.py, legacy_reader.py | 改修/維持 | Linux/macOSのPOSIX descriptor/flock/直接一件/旧read-only decodeだけ。Windows分岐を残さない |
| NRT infra/windows_handles.py | 削除 | Win32 directory/mutex/JSON readerを互換aliasやfallbackなしで撤去 |
| NRT domain/work_target.py, artifacts/data-schema.json | 改修 | PhysicalIdentityをplatform=posixと10進device/file_idに限定。work-target v1は維持 |
| NRT application/worktree_observation.py | 維持 | 必要時観測。常駐サービスなし |
| assets/install_root/.agents/skills/spec-dock、spec-dock-grill-with-docs | 改修 | 新入口/直接対象/失敗を説明。既存read-only/一Artifact境界保持 |
| tests、provider-ci.yml、docs/authoring/reference、README/AGENTS | 改修 | Windows専用三testとnative WAIT_ABANDONED部分、Windows CI laneを撤去。共有POSIX/E2Eを保持し、GPT-5.6 Sol / Proの分析と後続brief境界を明記 |
| dogfood spec-dock/workspace.json / 全Scope .meta.json | 実適用は別step | workspace宣言だけ明示切替。全Scope bytes不変 |

Scope deleteの--recursive/--clear-active/--detach-dependencies、Workbenchのoverwrite、worktreeの--unlock/--discard-ignored、明示bootstrapは、旧草案のように理由なく一括廃止しません。手順・入力・安全な部分失敗を [CLI契約](artifacts/cli-contract.md#other-operations) に固定します。--clear-activeも観測済みtokenだけを消し、新規選択や共通lockを増やしません。

<a id="d-12"></a>
## D-12 移行と後戻り条件

[runbook](artifacts/migration-runbook.md) が実施手順です。通常の外部CLIが旧controlなしで読取/診断できることを先に実装します。旧controlを作って起動を直す手順にはしません。

旧writer/agent/shell起動元を停止し、仕様・ignored成果物・旧active/registry/pending journal・必要Git状態を外部へ実体保全します。停止確認は人の運用前提で、管理daemon/全writer名簿を新設する理由にしません。未完了remoteの参照を人が照合し、旧phaseを新journalへ移植しません。旧.git独自領域はread-onlyで、切替のための削除/更新もしません。

`workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1` を既存leaf内の新optionとして定義します。applyは--backup-dir ABS、--confirm-old-writers-stopped、--yesを要求し、dry-runはwrite0です。自workspaceのschema3/旧protocol→新protocolだけをatomicに切り替え、旧control_epochがある場合だけ除去します。全Scope、ID/path/linkage、未知設定はそのまま。旧schema<3はこの復旧版で黙って全件変換せず、対象外として既存保全と別の明示判断へ戻します。

旧activeは外部保全した後、現在WTの旧active.json等を明示した退役対象として扱います。新recordへ自動変換するとStart以外の取得になるため、**自動importしません**。利用者がGit状態を確認して新しいStartで選択し直します。切替後に旧記録が残っても新readerは合成しませんが、未保全の旧選択を無視して開始したことにならないよう、移行検査で所在と方針を記録します。

一file切替の前に止まれば旧protocol、後なら新protocolです。次のmigrateは現在を再観測し、既に新宣言ならunchanged。過去操作resumeではありません。static資産の更新はinstallation updateとして別に行い、未知改変fileは人間mergeします。

コードのrevertとremote効果の巻戻しは別です。適用前なら新writerを止め保全物から自workspace/static差分だけ復元可能。適用後の新Scope/GH効果/後続編集があれば、無条件に旧writerを再開しません。必要な成果物を比較・統合し、旧writerを使うなら旧保証/前提を別途満たす必要があります。本版は自動rollbackを提供しません。

<a id="d-13"></a>
## D-13 検証境界と既存保証の置換

[AC対応表](artifacts/acceptance-matrix.md) と [Plan](plan.md#regression) の実測が必要です。threadだけでなく別processでStart/clear/Finishの順序を固定して競合を検査します。全writerロックが残っている実装、Check→unlock→recordという誤実装、固定active.jsonを後で消す誤実装がRedになる試験を用意します。

producer sourceのtest import成功だけでは配布成功としません。Linux/macOSでfresh wheel/外部venv/実console/別clone/linked worktree/controlなし/実Gitとstateful fake ghを通します。通常 `make lint` と `uv run pytest` を維持し、OS/Python/FS/候補SHA/wheel hash/exit/skipを記録します。Windows native/NTFS laneはgateにしません。非対応OSの境界は、utilityがcontext-freeであることと、代表的な業務writerがGit/GitHub/file効果前にeffects=[]で拒否されることだけをplatform simulationで検査します。ベンチマーク制度やcacheを増やしません。最小のIO検査として、scope showが他WT全Scopeを読まないこと、Syncの製品側metadata読取・path安全性検証が必要な直接対象/祖先に限定されることを測ります。Gitのファイル名探索は許容し、全IOが定数時間であるという検査に置き換えません。無関係なfile/symlink、未追跡対象、path移動、対象重複、選択chainのredirect、Git検索の失敗/timeoutを公開CLIで検証します。

<a id="d-14"></a>
## D-14 実施境界・完成証拠

このpackは文書生成物です。schemaの自己検証やZIP整合は製品ACのpassではありません。HTMLの実行JS/modal byte一致は動的なSVG描画成功の代わりではありません。

本追加分析と差替え候補の著述モデルは、利用者指定の **GPT-5.6 Sol / Pro** です。既存P-01〜P-17の実装履歴に記録された別モデル設定を改ざんしません。P-18を含む実装担当は既に利用者指定のGPT-6.1 Sol / Max（gpt-6.1-sol / max）です。具体commandと実在test pathは、更新済み正本を通常pushした後の独立ChatGPT Implementation Brief Strictで具体化します。本資料だけで実装開始可能、SpecDock正式Start成功、レビュー/FQ完了とは扱いません。コード変更、テスト、成果物レビュー、人間merge、実環境dogfood、#413 import/Startを別step・別証拠にし、自動commit/push/merge/公開を含めません。
