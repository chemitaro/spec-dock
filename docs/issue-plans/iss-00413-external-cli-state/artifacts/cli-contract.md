# CLI契約 — Issue #413

これは未実装の新契約です。基準の公開leafを残し、独自control/registry/journal/cacheに依存する意味を必要な範囲で変更します。実装済みの実行記録ではありません。

<a id="catalog"></a>
## C-01 既存44 leafの全件対応

出典: [source-basis](source-basis.md#implementation)。維持は無変更という意味ではなく、主な業務目的とsyntaxを保つ分類です。現context引数、v1 JSON、台帳保証は共通変更の対象です。今回の新leafは0、公開leaf全体の廃止は0です。廃止するのは表とC-02に列挙した機能・引数です。

| No. | 既存leaf | 分類 | 新syntax | 効果・変更 | 読取根拠 |
|---|---|---|---|---|---|
| 1 | scope create initiative | 必要変更 | scope create initiative --backend github --title TITLE [--slug SLUG] | 旧syntaxを維持。--backend localはexit2。GH発行番号でmetadata公開、独自採番なし。 | catalog / ids / lifecycle / local tests |
| 2 | scope create epic | 必要変更 | scope create epic --backend github --title TITLE --parent TARGET [--slug SLUG] | 旧syntaxを維持。--backend localはexit2。GH発行番号でmetadata公開、独自採番なし。 | catalog / ids / lifecycle / local tests |
| 3 | scope create issue | 必要変更 | scope create issue --backend github --title TITLE --parent TARGET [--slug SLUG] | 旧syntaxを維持。--backend localはexit2。GH発行番号でmetadata公開、独自採番なし。 | catalog / ids / lifecycle / local tests |
| 4 | scope import github initiative | 維持・内部変更 | scope import github initiative REF --title TITLE [--slug SLUG] [--github-repo OWNER/REPO] | 指定IssueをGET/import、POSTなし。現在treeのID/ref重複を検査。resume/rollbackなし。 | catalog / selectors / github_lifecycle |
| 5 | scope import github epic | 維持・内部変更 | scope import github epic REF --title TITLE --parent TARGET [--slug SLUG] [--github-repo OWNER/REPO] | 指定IssueをGET/import、POSTなし。現在treeのID/ref重複を検査。resume/rollbackなし。 | catalog / selectors / github_lifecycle |
| 6 | scope import github issue | 維持・内部変更 | scope import github issue REF --title TITLE --parent TARGET [--slug SLUG] [--github-repo OWNER/REPO] | 指定IssueをGET/import、POSTなし。現在treeのID/ref重複を検査。resume/rollbackなし。 | catalog / selectors / github_lifecycle |
| 7 | scope list | 維持・必要変更 | scope list [--kind KIND] [--parent TARGET] [--state STATE] | 自treeの一覧。GH未観測はunknown。state filterで除外したunknownの件数も返す。 | catalog / #409 D-10〜13 |
| 8 | scope show | 維持・必要変更 | scope show TARGET | 自treeの対象とauthorityを表示。動的role維持。 | catalog / #409 D-10〜13 |
| 9 | scope edit | 維持・必要変更 | scope edit TARGET --title TITLE | 対象metadataのtitle更新。ID/slug/path/backendを勝手に変えない。 | catalog / #409 D-10〜13 |
| 10 | scope close | 維持・必要変更 | scope close TARGET [--reason completed&#124;not-planned] --yes | 既定completed。GH live条件と完了理由。selection/branchを変えない。 | catalog / #409 D-10〜13 |
| 11 | scope reopen | 維持・必要変更 | scope reopen TARGET --yes | 対象をopenへ。親祖先条件を維持しselection/branchを変えない。 | catalog / #409 D-10〜13 |
| 12 | scope delete | 維持・必要変更 | scope delete TARGET [--recursive] [--clear-active] [--detach-dependencies] --backup-dir ABS --yes | 既存の削除範囲option維持。旧journal前像の代わりに人間向けbackupを明示。詳細C-05。 | catalog / #409 D-10〜13 |
| 13 | active show | 維持・出力変更 | active show | 自WT直接対象・導出祖先・branch差。空でも成功。 | active_selection / active tests |
| 14 | active set | 必要な機能制限 | active set TARGET | 同一妥当directのunchangedだけ。空/別対象はWORK_START_REQUIRED。旧--from-branchはexit2。 | active_selection / active tests / D-07 |
| 15 | active clear | 必要変更 | active clear (--all&#124;--from TARGET) | 観測した自WTの記録を解除。親自動昇格なし。壊れJSONの--allは--yes必須。 | active_selection / active tests / D-07 |
| 16 | work start | 維持・必要変更 | work start TARGET [--branch NAME] [--base REF] [--switch-active] [--source github] | branch作成/checkout維持。新直接取得唯一の入口。全体lock→Startだけ。 | work_lifecycle / start tests |
| 17 | work finish | 維持・必要変更 | work finish TARGET --yes | completed/Close確認後、自WTの該当記録だけ解除。branch保持。 | work_lifecycle / finish tests |
| 18 | branch show | 維持・必要変更 | branch show TARGET [--name NAME] | 明示名または従来形式の候補refを観測。永久bindingとは返さない。 | branch_vnext / catalog |
| 19 | branch create | 維持・内部変更 | branch create TARGET --base REF [--name NAME] | 新branchだけ作成。台帳へのbindingなし。既存refは拒否。 | branch_vnext / catalog |
| 20 | branch switch | 維持・必要変更 | branch switch TARGET [--name NAME] | 対象/祖先のある既存branchへ切替、直接記録は不変。 | branch_vnext / catalog |
| 21 | dependency list | 維持・内部変更 | dependency list TARGET [--view declared&#124;effective] | 既存宣言/実効依存を表示。 | catalog / #409 D-11 |
| 22 | dependency check | 維持・内部変更 | dependency check TARGET [--source local&#124;github] | 既定local。GH未観測unknownはready=false。source cache退役。 | catalog / #409 D-11 |
| 23 | dependency add | 維持・内部変更 | dependency add --from TARGET --to TARGET | 依存を一metadataへ追加。graph検査、共通lockなし。 | catalog / #409 D-11 |
| 24 | dependency remove | 維持・内部変更 | dependency remove --from TARGET --to TARGET [--missing-ok] | 指定edgeだけ解除。既知対象かつmissing-okで不存在edgeはunchanged。 | catalog / #409 D-11 |
| 25 | artifact create | 維持・内部変更 | artifact create --scope TARGET&#124;@root --type TYPE --title TITLE [--slug SLUG] | 六creation type維持。Scope内の既存Artifact ID/path方式、無上書き公開。 | catalog / #409 D-11 / installed skills |
| 26 | artifact import file | 維持・内部変更 | artifact import file PATH --scope TARGET&#124;@root | 一つの明示fileをopaque evidenceとして保全import。 | catalog / #409 D-11 / installed skills |
| 27 | artifact list | 維持・内部変更 | artifact list --scope TARGET&#124;@root | owner内一覧、unknown保存済みevidence種別を勝手に削除しない。 | catalog / #409 D-11 / installed skills |
| 28 | artifact show | 維持・内部変更 | artifact show ARTIFACT_ID --scope TARGET&#124;@root | 所有者内の対象だけ。本文の無断公開をしない。 | catalog / #409 D-11 / installed skills |
| 29 | worktree create | 維持・必要変更 | worktree create NAME --base REF [--root ABS] | NAMEを必須化。Git branch worktree/NAMEを作り、root/NAMEへGit add。自前ID予約なし。 | catalog / #409 D-08 |
| 30 | worktree list | 維持・必要変更 | worktree list | Git inventoryを表示、未登録というエラーなし。 | catalog / #409 D-08 |
| 31 | worktree show | 維持・必要変更 | worktree show ABS | 同じcloneの正確なpathを観測。wt:ID/registry aliasはexit2。 | catalog / #409 D-08 |
| 32 | worktree remove | 維持・必要変更 | worktree remove ABS [--unlock] [--discard-ignored] --yes | main/現在/bare/dirty拒否。ignored破棄は明示flag。branchは残す。 | catalog / #409 D-08 |
| 33 | worktree bootstrap | 維持・必要変更 | worktree bootstrap ABS --yes | 明示したprojectのmake initを一回実行。dry-runでmake呼出し0。receipt/recover廃止。 | catalog / #409 D-08 |
| 34 | workbench copy | 維持・内部変更 | workbench copy --scope TARGET --to-worktree ABS [--on-conflict error&#124;overwrite] | 既存copy目的維持。overwriteはsource優先、dest-only保持。全体rollbackなし。 | catalog / #409 D-12 |
| 35 | workspace sync | 必要な効果変更 | workspace sync [--source local&#124;github] [--allow-invalid] | stdoutの必要時観測。旧generation/cacheを書かず、複数WTを表示。新render leafを増やさない。 | workspace_sync / sync tests |
| 36 | workspace validate | 維持・内部変更 | workspace validate [--ci] [--require-nodes] | 通常は作業tree、--ciは固定HEADの構造検査。controlなし。 | catalog / entrypoint tests |
| 37 | workspace doctor | 維持・必要変更 | workspace doctor [--raw] [--legacy] [--github-repo REPO --github-pr N --github-head-sha OID --github-extended] | 既存GH診断指定を維持し、raw/旧記録の読取だけ追加。control修復/書込なし。 | catalog / installation/source context |
| 38 | workspace migrate | 必要変更 | workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 [--dry-run] | applyには--backup-dir ABS --confirm-old-writers-stopped --yes。現在WTの宣言だけ切替。 | catalog / lifecycle / D-12 |
| 39 | installation show | 必要変更 | installation show [--target ABS] | 外部package版と指定WTのschema/資産版を表示。全登録WT/digest/epochなし。 | installation_vnext / catalog |
| 40 | installation init | 必要変更 | installation init ABS --yes | 未導入WTへworkspaceとstatic資産のみ生成。既存file競合は拒否。 | catalog / #409 D-02 |
| 41 | installation update | 必要変更 | installation update [--target ABS] --backup-dir ABS --yes | 現在installed packageの既知static資産差分だけ。既知旧hashまたは新hashのみ扱う。 | installation_vnext / catalog |
| 42 | installation uninstall | 必要変更 | installation uninstall [--target ABS] --backup-dir ABS --yes | 既知のtool-owned static資産のみ退役。仕様/成果物/直接状態は消さない。package uninstallは外部。 | catalog / D-12 |
| 43 | help | 維持 | help [PATH...] / -h / --help | 静的utility。既存44 leafを同catalogから説明。 | catalog / options / entrypoint tests |
| 44 | completion | 維持 | completion bash&#124;zsh&#124;fish | 同catalogから静的補完。Git/network/状態読取なし。 | catalog / options |

<a id="globals"></a>
## C-02 共通option・廃止入力

| option | 契約 |
|---|---|
| --project PATH | 起動CWD基準で絶対化した明示Git root。別repo/default branchにfallbackしない |
| --json | stdoutにUTF-8 JSON object一個と末尾LF。text/progress混入なし |
| --non-interactive | prompt禁止。必要な確認がなければ副作用前停止 |
| --yes / -y | 既存の確認の肯定だけ。schema/対象/重複/lock/安全条件を迂回しない |
| --dry-run | planned結果。write/lock/branch/checkout/remote変更/make/予約0。必要な明示GETのみ許す。readにも安全なpreview表示を許す |
| --offline | GitHubを呼ばない。create/import/必要GH条件のあるStart/Finishは副作用前停止。local読取は可能 |
| --expect-current ID | 自WTの直接対象IDとの比較。引数のIDは既存selectorでcanonical化し、検査対象を途中で切り替えない。Startはlock内でも確認、Finishは捕捉時に確認。remote/global CASではない |
| --expect-backend local&#124;github | 解決した対象backendとの比較。新規local作成許可ではない |
| --timeout SECONDS | Git/gh各subprocessの有限上限。既定30、0超〜300。送信後timeoutを未送信にしない |
| --lock-timeout SECONDS | Start取得待ちだけ、既定5、0〜300。Start以外への明示指定はexit2で適用先を説明する |
| --color auto&#124;always&#124;never | text表示だけ。JSONにANSI制御を入れない |
| --version, -h/--help | Git/project/設定を解決しないutility。新たな初期化をしない |

dry-runは変更の承認を要求せず、Finish等の--yesは本実行時にだけ必須です。previewは副作用も予約も行いません。

共通optionをleaf前後に置ける既存parserの操作性を維持します。曖昧prefix補完は無効です。root/leaf helpは必須引数チェックより先に処理します。引数/廃止機能の診断はcontextより前で、--yesを付けても副作用0です。変更後のhelp/completion/JSON schemaを同catalogから検査します。

廃止: 全 `--resume/--rollback`、worktree `--recover`、active `--from-branch`、`--source cache`、`--allow-stale`、migrate `--mapping-file`、installationの `--version/--commit/--maintenance/--finalize/--activate-engine/--from-update`。root --versionは存続します。廃止理由は順に「永続操作記録なし」「receiptなし」「共有bindingなし」「cacheなし」「全件mapping移行でない」「package更新/engine世代管理は外部」です。exit2/ARGUMENT_RETIREDと明示した代替を返します。古いroot new/import/sync/install等の既に廃止されたsyntaxは復活させません。work releaseはunknown commandです。

`--source github` はStartで既定、dependency check/Syncは明示時だけlive。localはcacheではなく現在metadataと直接記録の観測です。createのGitHub repositoryは既存のorigin publication endpointを検証して固定し、fetch/push不一致・認証情報入りURLを安全側に拒否します。importの--github-repoと完全refが矛盾すれば停止します。

<a id="work"></a>
## C-03 Work / active / Syncのデータ型

全envelopeは [cli-schema.json](cli-schema.json)。dataの必須fieldは次です。未確定値はnullを使い、未確定なのに成功型を作りません。事前失敗時のdataはdiagnosticでも構いません。Startの部分失敗はstarted=falseです。Finishのcompletedはremote等で完了を確認できたかを示し、Close成功・選択解除失敗の部分結果ならtrue、Close unknownならfalseです。操作全体の成功と混同しません。

| data.kind | 必須field |
|---|---|
| work-start | scope_id, started:boolean, branch_before:string\|null, branch_after:string\|null, selection_token:string\|null |
| work-finish | scope_id, completed:boolean, branch_before:string\|null, branch_after:string\|null, selection_token:string\|null（返却時の自WT記録） |
| active | selection:SelectionView、ancestors:string[] |
| sync | observed_at, source:local\|github, complete:boolean, worktrees:WorktreeObservation[], scopes:ScopeObservation[], counts:Count[], findings:Diagnostic[] |
| diagnostic | findings:Diagnostic[], unverified:string[] |
| utility | text:string, version:string\|null |

SelectionView = `status:empty|selected|stale|unavailable|invalid`, `scope_id:string|null`, `github_ref:string|null`, `selection_token:string|null`, `selected_branch:string|null`, `current_branch:string|null`, `branch_changed:boolean`。
WorktreeObservation = `path:string`, `selection:SelectionView`, `lifecycle:open|completed|not-planned|unknown`, `process_state:not_observed`, `findings:Diagnostic[]`。
Count = `scope_id`, `direct_selected_count:int>=0`, `descendant_selected_count:int>=0`, `complete:boolean`。不明な祖先は架空のcountを作らず、既知集計のcomplete=falseで示します。

ScopeObservation = `scope_id:string`, `github_ref:string|null`, `lifecycle:open|completed|not-planned|unknown`。GitHub-backedはcanonical ref、既存local Scopeはnullです。

`scopes` は選択の有無で絞らず、現在treeの表示対象と他WTから必要な直接対象/祖先を含めます。同一identityの行は重複させません。lifecycleは同じ観測集合から作り、対応するworktrees行と一致させます。local sourceのGH-backedはunknown、github sourceは今回GETした状態だけです。

他WTの直接対象pathはGitのNUL区切りpathname検索からその都度導出します。tracked/untracked（ignore対象を含む）の現在pathを扱い、製品のmetadata読取とnofollow実体検証は対象/祖先に限定します。無関係なScope-shaped file/symlinkは観測を妨げません。Git検索のエラー・不完全な警告・timeout、現存候補重複、選択chainのredirectはunavailable、現存対象がない場合はstaleとして、読めた直接記録のID/refを保持します。いずれもcomplete=falseであり、Startの重複確認をすり抜けません。直接記録のfieldと公開JSON schemaは追加しません。

`counts` は各scopes行のscope_idに対応する行を持ち、未選択も既知件数0で明示します。complete=falseの0は全WTで未選択との確定ではありません。未知の対象や祖先を架空行で補完せずfindingsとcomplete=falseで示す規則は維持します。例えばAが選択中かつcompleted、Bが未選択かつopenなら、scopesにA/Bのlifecycle、countsにAのdirect=1/Bのdirect=0（全読取成功ならcomplete=true）を返します。これは表示用memory値で、永続化しません。

`started` は今回要求したStartの全必須効果を確認できた場合だけtrue。既存の同じ妥当記録/branchならunchangedかつtrue。partialではfalseです。記録公開後に確認不能なら、現物が存在していても今回started=trueとは返しません。
`completed` は対象authorityがcompletedと確認できた意味。Close成功/解除失敗ならcompleted=trueでもoperation statusはpartialです。どのrecordが残っているかをeffectsとselection_tokenで分けます。これを実装/mergeの完了と呼びません。

<a id="json"></a>
## C-04 stdout / stderr / exit / effects

共通envelope: `schema_version="specdock.cli/v2"`, `command`, `status`, `exit_code`, `data`, `effects`, `warnings`, `error`, `recovery`。v1の意味を黙って変えずv2へ切り替えます。永続operation_id、epoch、engine_digestは返しません。

| exit | status | 条件 |
|---|---|---|
| 0 | succeeded / unchanged / planned | 確認済みの成功・無変更・有効なdry-run |
| 1 | failed | 効果前の内部不具合 |
| 2 | failed | syntax/廃止option。不用意にbusiness/contextへ入らない |
| 3 | failed | readiness/競合/対象条件/確認不足/Start lock timeout。効果前 |
| 4 | failed | 明示local対象が存在しない。通信失敗をnot-foundとしない |
| 5 | failed | IO/Git/gh環境失敗で、変更効果がないと確認できる |
| 6 | partial | 確認済みの一部効果またはunknown。残る効果を隠さない |
| 7 | failed / partial | validate/doctor/Syncの不適合または不完全な診断。effects=[]も許す |

Effect = `kind:string`, `status:planned|succeeded|unchanged|failed|not_attempted|unknown`, `target:string|null`。今回使うWork kindは `git.branch.create`, `git.checkout`, `selection.clear`, `selection.publish`, `github.issue.close`, `scope.lifecycle`。実施しない段階はnot_attempted、既存で無変更ならunchanged。failed operationがsucceeded/unknown effectを含むことは禁止し、partial6へ昇格します。partial6はsucceededまたはunknown effectを少なくとも一件持ちます。plannedはplannedのみ、unchangedはunchangedのみまたは空です。

JSON modeの制御下stderrは空にし、子process出力をそのままconsoleへ流しません。元Git stderrは **error.details.git.stderr** に元の改行・文言を保って入れます。ネイティブ終了値は同 `.returncode`（起動前/timeoutはnull）、CLI終了値はenvelope.exit_codeです。text modeでは見出しと効果サマリを付けても、取得したGit原文はstderrにそのまま続けます。大文字小文字、語句、複数行を一般文言に置換しません。

秘密を含むURL userinfoや既知の認証tokenだけを最小部分秘匿し、`redacted=true` と理由を付けます。通常Gitエラーの内容やpath全体を一般文言に潰しません。`git.argv` は安全に表示できる引数だけで、環境変数・認証情報・Artifact本文を入れません。非UTF-8のbyteがあればdecode replacementの有無を `decoding_replaced` で明示し、byte原本保持とは主張しません。通常のUTF-8 stderrにはstrip/翻訳/切捨てをしません。子プロセスが未捕捉のsignalで終わった等、CLI自体が出力できない状況は有効JSONの保証外です。

recoveryはnullまたは `can_resume=false, can_rollback=false, instructions:string[]`。これは人に現物確認と新しい明示操作を案内するだけで、送信token/実行権ではありません。

[実例](examples.json) は成功、重複拒否、Git途中失敗、remote unknown、Sync不完全を含みます。例えばcheckoutがネイティブexit1でも、branch作成が既に成功していればCLIはexit6です。エラーを隠してexit1/5やeffects=[]にしません。

<a id="other-operations"></a>
## C-05 付随操作の必要変更を限定する

### Scope / dependency / Artifact

通常scope list/showのGH状態は未観測ならunknown。list --stateは一致が確認できたものだけを返し、未観測除外件数をresultに付けます。create/import/close/reopen/Finishは意味に必要なlive観測を行います。原文資料を編集することにGH通信や編集権限を要求しません。

deleteは対象subtreeを確定し、recursiveなしで子があれば拒否します。incoming dependencyは--detach-dependenciesなしなら拒否し、ありなら参照元metadata変更→対象subtree削除の順にします。選択中の自WT対象/配下があれば--clear-activeなしで拒否し、ありなら捕捉済みtokenのみを解除します。他WTの記録は変更せず、残った参照は次回staleと表示します。GitHubをCloseせずbranchも消しません。--backup-dirに対象/変更元の実体を保全・確認してから変更します。途中で停止すれば各変更pathをeffectsに残し、自動巻戻ししません。

Artifactの採番は所有者directoryにある既存fileから候補を求め、実Artifactを無上書き公開します。共有採番台帳は作りません。同時候補衝突は副作用なしの競合として返し、新しい明示操作で再観測します。別scopeの番号は別です。

全writerロックを外すため、Scopeの同時importで異なるslug/pathに同じID/refが競合することまでatomicに禁止する保証はありません。snapshotで二重登録を検査し、公開前と後にも検査します。事後に競合を検出したらpartialとして双方のpathを提示し、どちらも自動削除しません。並行metadata操作は同一treeの全体serializable transactionではなく、通常validateと人間の統合が必要です。Startの同時重複開始だけはD-05の強い排他保証を持ちます。

### Workbench

sourceは指定Scopeの.workbench、destinationは同cloneの明示WTの同Scopeだけです。errorは既存衝突で停止。overwriteはsourceと同名のfileを置換し、destinationにだけある成果物を残します。コピー前に差分を提示し、source/destinationの必要bytes/identityを再確認、file単位でstage/atomic公開します。no-follow/領域境界を守り、途中失敗では適用済みpathと未適用pathを返します。共通lockや全体rollbackを足しません。

### Worktree / bootstrap

create NAMEの配置rootは--root、既存 `SPEC_DOCK_WORKTREE_ROOT` の順で解決し、両方なければ配置先の明示を要求します。NAMEの既存安全な文字規則を保ち、root/NAMEに新worktree、`worktree/NAME` にnew branchを作ります。baseはcommitへ固定。既存path/nameは競合、採番・alias予約なし。Git途中成功はpartialで残します。Scopeの開始は別のwork startです。

show/remove/bootstrapの参照は絶対path。Windowsはdrive-root absoluteも同じ境界検査で認めます。wt:ID/登録aliasはexit2。removeはmain/現在/bare、tracked/untracked dirty、path接続不正を拒否します。lockedは--unlockがある時だけGitのunlockを実施します。ignoredファイルは--discard-ignoredと明示確認なしに捨てません。明示破棄でも対象外pathやbranchを消しません。先にunlock成功後remove失敗ならpartialとしてunlock効果を残します。

bootstrapは既存のproject-owned make initを明示targetで一回実行します。dry-runはmake -nも呼びません。--offlineでは未知の任意hook通信を保証できないので実行前に拒否します。receipt/--recoverを廃止し、失敗時はproject側の現状を人が確認します。Start共通lockは取得しません。

### installation / migrate / doctor

installationはpackage managerの代替ではありません。initは既存fileを上書きしない初期static配置と新workspace宣言だけ。update/uninstallはpackage内static inventory（許可path、既知旧hash、新hash）と現在hashを比較し、既知のtool-owned資産だけをbackup後に一件ずつ更新/退役します。未知改変資産が一件でも計画範囲にあれば適用前に止め、人間mergeへ戻します。scope metadata/本文/Artifact/Workbench/直接状態/旧.gitは対象にしません。全worktree更新やエンジン世代はありません。

migrateはD-12の既存schema3 workspace宣言切替だけ。--to-schemaを維持し、旧mapping/maintenance/recoveryは拒否します。doctor --legacyは旧control/active/registry/journalの読める範囲を分類するだけで、復旧や起動をしません。raw modeは未知schemaでも安全なfile情報まで読めます。既存のGitHub PR診断指定を使うときは明示repository/PR/headを固定し、業務書込は0です。

### その他familyのresult契約

上記以外はdata=`{kind:FAMILY,result:OBJECT}`。fieldの主契約は次です。未知値はnull、flagsはboolean、配列は空でも省略しません。dry-runではresultにcan_applyとblockersを加えます。

| FAMILY / command | resultのfield |
|---|---|
| scope / show, edit, create, import, close, reopen | scope:ScopeView\|null、github_ref:string\|null、changed:boolean |
| scope-list / list | items:ScopeView[]、unknown_filtered_count:int>=0 |
| deletion / delete | removed_ids:string[]、changed_paths:string[]、remaining_paths:string[]、backup_path:string\|null |
| branch / show/create/switch | scope_id,name,tip:string\|null、created:boolean、switched:boolean、binding_persisted:false |
| dependency / list/check/add/remove | scope_id,declared:string[],effective:string[],ready:boolean\|null,blockers:Diagnostic[],changed:boolean |
| artifact / create/import/show | artifact:{id,scope_id,path,type}\|null、changed:boolean |
| artifact-list / list | scope_id,items:ArtifactView[] |
| worktree / create/show/remove/bootstrap | path,branch:string\|null,head:string\|null,changed:boolean,observed:object |
| worktree-list / list | items:{path,branch,head,bare,locked,prunable}[] |
| workbench / copy | scope_id,source_path,destination_path,copied_paths:string[],remaining_paths:string[] |
| installation / show/init/update/uninstall | target,package_version,created_paths:string[],changed_paths:string[],retired_paths:string[],backup_path:string\|null |
| migration / migrate | target,before_protocol:string\|null,after_protocol:string\|null,changed_paths:string[],backup_path:string\|null |
| validation / validate | valid:boolean,findings:Diagnostic[],snapshot_source:working-tree\|HEAD |

ScopeViewはid,kind,title,parent_id,backend,github_ref,path,revision,status（state/authority/source/observed_at）を持ちます。構造schemaはenvelopeとWork/active/Syncを厳密に定義し、その他familyのresult内fieldはこの表とapplication contract testで検査します。JSON Schemaだけで全コマンドの意味を証明したとは扱いません。

<a id="examples"></a>
## C-06 正常操作例（未実装の新仕様）

以下のROOTやbranch名は例です。対象IDが現在tree/切替先commitに存在し、移行済みであることを先に確認します。importで生じたtracked資料は利用者の通常Git作業で保存してから、clean条件を要するStartに進みます。

```text
spec-dock --help
spec-dock --project /projects/spec-dock scope show iss-00413
spec-dock --project /projects/spec-dock work start iss-00413 --base HEAD --branch fix/external-cli --dry-run --json
spec-dock --project /projects/spec-dock work start iss-00413 --base HEAD --branch fix/external-cli --json
spec-dock --project /projects/spec-dock active show
spec-dock --project /projects/spec-dock workspace sync --source github --json
spec-dock --project /projects/spec-dock work finish iss-00413 --dry-run --json
spec-dock --project /projects/spec-dock work finish iss-00413 --yes --json
```

同じ妥当な直接Scopeを別branchで明示Startする場合は--switch-active不要で、Git成功後に新tokenと選択時branchの記録へ置換します。同じScope/branchの妥当な記録ならunchangedです。

途中失敗でbranchだけが作られた場合は現状確認後、新しい `work start iss-00413 --branch fix/external-cli` を使います（既存branchなので--baseなし）。中断だけなら `active clear --all`。これは完了/Closeをしません。既存#413の正式登録例は [migration-runbook](migration-runbook.md#m-06) に分離しています。
