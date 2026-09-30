# Issue #413 実装計画書

**全17 stepは未着手です。** ChatGPTによるこのpackの生成・静的自己点検とは別の、後続実装とCodexのローカル作業です。

実装担当は利用者指定の **GPT-6.1 Sol / reasoning High**。将来の設定値は `model="gpt-6.1-sol"`、`reasoning_effort="high"`。本資料の著述モデルと混同せず、gpt-5.6系専用coder roleへ置き換えません。モデルの公開状況や能力比較はこの作業契約の判断材料にしません。

## 作業の境界・進め方

[要件](requirement.md) / [設計](design.md) / [CLI](artifacts/cli-contract.md) / [全件対応](artifacts/acceptance-matrix.md)。RTは基準のasset runtime、NRTは予定のsrc/spec_dock/runtimeです。新設tests/APIは予定と明示し、既存として実行済みとはしません。

各stepは一つの成果を閉じます。公開APIまたは既存portへ向けた結果比較をRedにし、ImportErrorやtest collection failureだけを意味のあるRedと呼びません。新moduleの接続が必要なら最小導線を先に作り、誤った現在挙動をassertionで検出してからGreenへ進みます。成功stub・一括skipは使いません。

通常編集やmetadataに包括的lock/権限制度を足しません。sourceの変更、製品テスト、成果物レビュー、人間merge、dogfood、正式#413 import/Startを別の証拠で扱います。後半の実環境作業は明示許可が前提で、コマンド例を掲載しただけでは実施許可や成功実績になりません。

依存の主経路はP-01→02→03→04→05→06→07→09、P-08は04/07後、P-10は08/09後、以後11→12→13→14→15→16→17です。OS test設計/資料レビュー準備は先行しても、同じ保存原語を別々に実装しません。

<a id="p-01"></a>
## P-01 契約・既存回帰・Redを固定する

**状態: 未着手。前提/依存: なし。** 読む節: [D-01](design.md#d-01), [D-11](design.md#d-11), [D-13](design.md#d-13)。補足: D-01, D-11, D-13。

**所有/対象file**: 既存 tests/cli_runtime/test_cli_vnext_contract.py、test_active_vnext.py、test_work_start_vnext.py、test_work_finish_vnext.py、test_workspace_sync_vnext.py、tests/integration/test_cli_entrypoint_vnext.py。新 tests/cli_runtime/test_issue413_contract.py（予定）。

**具体的変更順**: 実装branchと基準SHAの差分を確認する。catalogの44 leaf/共通optionを列挙してCLI対応表と比較し、既存CI baselineを取得する。その後、controlなし実console、Git原文、親自動昇格なし、Start以外が共通lockを取らない要求を公開入口の回帰テストとして追加する。新テストのfixtureは正式Scope手作成の実運用と区別し、GitHub-backed schema3を用意する。

**変更禁止**: 旧テストの一括削除・skip、240件の実metadata変更、復旧例外配置を正式Scopeと見なすこと、baseline未実行をpassにすることを禁止する。

**入力/出力例**: 入力: 基準catalogと本pack。出力: 44行の対応、baseline結果、旧挙動と新期待の差で失敗する限定テスト。

**Red → Green / 検証**: Red: 旧shimのcontrol依存、親昇格、原文を失うエラーがassertionで失敗する。collection/import失敗はRed完了にしない。Greenは本stepでは対応表/fixture検査だけ、製品挙動のGreenは後続へ紐付ける。

**実行コマンド（将来実行）**:

```text
git diff --check
make lint
uv run pytest
uv run pytest tests/cli_runtime/test_issue413_contract.py -q
```

**期待結果・完了条件**: 通常CIの実exitを保存し、baseline失敗と新規Redを別項目にする。新規仕様のRedがどのRQに対応するか一意。

**対応**: RQ-413-09, RQ-413-15, RQ-413-17 ／ AC-413-19, AC-413-32, AC-413-38。

**失敗時の停止/戻り先**: 対応不能な既存leaf/重要業務が見つかったらD-11/C-01へ戻り、無関係な廃止で解決しない。

<a id="p-02"></a>
## P-02 通常wheelとutilityだけの縦経路を成立させる

**状態: 未着手。前提/依存: P-01。** 読む節: [D-02](design.md#d-02)。補足: D-02。

**所有/対象file**: src/spec_dock/cli.py、external_cli.py、pyproject.toml、setup.py、asset_layout.py。RT→NRT移設、tests/integration/test_cli_entrypoint_vnext.py。新 tests/integration/test_issue413_wheel.py（予定）。

**具体的変更順**: runtimeを通常subpackageへ機械的に移設し絶対importを揃える。package discoveryとstatic resource指定を修正する。root/leaf help、version、completionをcontext前にdispatchし、実consoleから到達させる。古いasset importのtest fixtureを新packageへ変更し、通常build清掃を維持する。businessの個別変更は後続stepへ分ける。

**変更禁止**: runtimeの二重配布、sys.path fallback、通常wheelをfixed engineへ再梱包、consumerへのPython展開、途中段階をrelease-readyと表示することは禁止。

**入力/出力例**: 入力: Gitもcontrolもない一時CWDとfresh wheel。出力: 実consoleのhelp/JSONがexit0、site-packages配下の唯一のruntime。

**Red → Green / 検証**: Red: fresh wheelを使うと旧fixed layout前提でbusiness/context到達が失敗することを記録。Green: Git/ghなしroot/44leaf help/version/補完が成功し、業務の未接続箇所は成功stubにせず明示される。

**実行コマンド（将来実行）**:

```text
uv build --wheel
uv run pytest tests/integration/test_issue413_wheel.py tests/integration/test_cli_entrypoint_vnext.py -q
```

**期待結果・完了条件**: sourceを読めない環境でutility成功。wheel/再build/sdist-derived wheelのruntimeが一組だけで、必要dotfileが含まれる。

**対応**: RQ-413-01 ／ AC-413-01, AC-413-02。

**失敗時の停止/戻り先**: consoleがsourceを参照していればD-02へ戻る。businessが未完成なら配布の合格を全機能合格にしない。

<a id="p-03"></a>
## P-03 schema3と直接対象一件の保存境界を作る

**状態: 未着手。前提/依存: P-02。** 読む節: [D-03](design.md#d-03), [D-09](design.md#d-09)。補足: D-03, D-09。

**所有/対象file**: NRT/domain/work_target.py、infra/work_target_store.py、infra/identity.py（新設）、domain/lifecycle.py、ids.py、selectors.py、infra/active_store.py。新 tests/unit/infra/test_work_target_store.py（予定）。

**具体的変更順**: 既存metadata codecを移設・保持し、work_target codecを分離する。no-followで0/1件を読む、immutable filenameで公開する、捕捉basenameだけを解除する三操作を実装する。stageは現在の完成候補のみで履歴を持たせない。record数、ignore/tracked、identity、未知schema、破損を分類する。CLI showに接続してfixtureの結果で検査する。

**変更禁止**: Scope全件schema bump、local綴りIDの改名、固定active.jsonの遅い無条件unlink、既存recordの上書き、operation journal/PID/TTLの追加を禁止。

**入力/出力例**: 入力: examples.jsonのwork_target/旧local綴りGH metadataと、0/1/2件・壊れJSON。出力: selected/empty/invalidと不透明selection_token。

**Red → Green / 検証**: Red: 旧storeの固定pathnameと親chain型では新record/解除の期待を満たさない。Green: 一件公開、失敗注入で半端JSONを有効選択にしない。Aのhandleを捕捉→A解除→B公開→古いA解除でB bytes不変。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/unit/infra/test_work_target_store.py tests/cli_runtime/test_active_vnext.py -q
```

**期待結果・完了条件**: 正常例/異常例がdata schemaと一致。legacy IDと未知任意fieldを保持し、通常操作で.gitへ独自write0。

**対応**: RQ-413-02, RQ-413-07, RQ-413-13, RQ-413-14 ／ AC-413-03, AC-413-04, AC-413-15, AC-413-28, AC-413-31。

**失敗時の停止/戻り先**: token再利用、二件公開、前の解除が次を消す挙動があればD-03へ戻り、Finishへ共通lockを足して隠さない。

<a id="p-04"></a>
## P-04 Git inventoryとstale観測を接続する

**状態: 未着手。前提/依存: P-03。** 読む節: [D-02](design.md#d-02), [D-04](design.md#d-04)。補足: D-02, D-04。

**所有/対象file**: NRT/infra/git_cli.py、application/worktree_observation.py（新設）、cli/vnext_runtime.py::_context、application/scope_query.py。新 tests/integration/test_issue413_observation.py（予定）。

**具体的変更順**: Git root/common-dirをcontrolなしで解決する。porcelain -zのNUL parserへ置換し、各WTの直接recordと必要な対象/祖先を読む。physical identityでaliasを同一視する。branch差は情報として返し、対象不在/stale/読取不能をemptyと分ける。raw doctorの入口を用意する。新recordなし・旧writer宣言・旧activeありのWTをemptyにしないfixtureを追加し、移行済みの旧資料残存と区別する。

**変更禁止**: 別clone探索、全WTの全metadataロード、.gitにworktree名簿を作成、main worktree経由の制御、branch名からScope推測を禁止。

**入力/出力例**: 入力: main+linked、同remote別clone、改行path、対象のないcheckout。出力: 同clone行だけ、stale/不明を残した観測。

**Red → Green / 検証**: Red: 旧contextが未登録linked/controlなしで失敗する。Green: 一覧/独立Scope読取が動き、branch切替してもrecord bytes不変。不明なWTは行を消さず理由を返す。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/integration/test_issue413_observation.py -q
```

**期待結果・完了条件**: Git一覧外のpath走査0。scope showのother-WT metadata open0。読取/doctorでstate write0。

**対応**: RQ-413-03, RQ-413-14 ／ AC-413-05, AC-413-06, AC-413-30, AC-413-31。

**失敗時の停止/戻り先**: 消えたWTを空と見なす、othercloneを混ぜるならD-04へ戻る。OS identity不明は正常値を補完しない。

<a id="p-05"></a>
## P-05 Start専用のOS排他を実装する

**状態: 未着手。前提/依存: P-04。** 読む節: [D-05](design.md#d-05)。補足: D-05。

**所有/対象file**: NRT/infra/start_lock.py、identity.py（新設）、既存writer_lock.py/admission参照の整理。新 tests/integration/test_start_lock.py（予定）。

**具体的変更順**: POSIX directory flock、Windows common identity由来named mutexを小adapterとして実装する。wait budgetと非継承handle、finally解放、abandoned再観測を共通化する。Start以外のdispatchにcommon lockが接続されないことをspyではなく別processの進行でも検査する。

**変更禁止**: 新lock file、mkdir/PID回収、daemon、対象別lock、全writer lock、Windows権限変更や別namespace fallbackを禁止。

**入力/出力例**: 入力: 同commonのpath alias二processと別clone二process。出力: 同cloneだけ直列、別clone独立。timeoutは副作用前exit3。

**Red → Green / 検証**: Red: 同clone二Startの重複区間、または旧lockがmetadata/Finishまで止めるケース。Green: 同clone重複区間0、他操作は取得0、kill後に次processが取得可能。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/integration/test_start_lock.py -q
```

**期待結果・完了条件**: Linux/macOS/Windowsで実行/skip/未実施を別記録する。各対応宣言には別processと実FSの証拠がある。

**対応**: RQ-413-02, RQ-413-04, RQ-413-06 ／ AC-413-04, AC-413-07, AC-413-11, AC-413-12。

**失敗時の停止/戻り先**: 必要原語がないOS/FSはD-05のunsupported経路へ。既存directory上のflockを未試験のまま保証済みにしない。

<a id="p-06"></a>
## P-06 Git効果を含むStartを閉じる

**状態: 未着手。前提/依存: P-05。** 読む節: [D-05](design.md#d-05), [D-06](design.md#d-06), [D-09](design.md#d-09)。補足: D-05, D-06, D-09。

**所有/対象file**: NRT/application/work_lifecycle.py、branch_vnext.py、commands/work_vnext.py、branch_vnext.py、infra/git_cli.py、presentation/envelope.py。tests/cli_runtime/test_work_start_vnext.py、test_branch_vnext.py、新 tests/integration/test_issue413_start.py（予定）。

**具体的変更順**: branch候補/明示再利用/固定base、必要なGH readinessをplanへまとめる。lock内で重複確認とGit効果、record公開まで繋ぐ。own別directの--switch-active規則を統一する。CalledProcessError/timeoutを薄いGitFailure型へ保持し、元stdout/stderr/returncodeをeffectsと一緒に返す。journal/registry phaseを除去する。

**変更禁止**: チェックだけlock内、recordをlock外、GH待ち/promptをlock内、既存branch reset、原文を汎用文言へ置換、失敗時自動checkout/branch deleteは禁止。

**入力/出力例**: 入力: work start iss-00413 --base HEAD --branch fix/external-cli。出力: branch作成/checkout/selectionが成立。checkout失敗fixtureはraw stderr付きpartial6。

**Red → Green / 検証**: Red: 同じScopeの同時二Start、記録失敗後resume必須、原文喪失。Green: 敗者Git効果0、異なる子は成立、branch後失敗は現物を残す。既存branch再試行は--branchだけで新操作になる。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_work_start_vnext.py tests/cli_runtime/test_branch_vnext.py tests/integration/test_issue413_start.py -q
```

**期待結果・完了条件**: 新規/既存branch、三階層、detached base、dirty/対象不在、kill境界が一致。started=falseとpartial/effectsの整合をschemaと意味の両方で検査。

**対応**: RQ-413-03, RQ-413-04, RQ-413-05, RQ-413-06, RQ-413-09, RQ-413-12 ／ AC-413-06, AC-413-07, AC-413-08, AC-413-09, AC-413-10, AC-413-11, AC-413-18, AC-413-19, AC-413-20, AC-413-26。

**失敗時の停止/戻り先**: 重複を保証できなければD-05へ、branch効果が消えるならD-06へ。新しいjournalを戻して解決しない。

<a id="p-07"></a>
## P-07 Finishとactiveの解除を閉じる

**状態: 未着手。前提/依存: P-06。** 読む節: [D-03](design.md#d-03), [D-07](design.md#d-07), [D-08](design.md#d-08)。補足: D-03, D-07, D-08。

**所有/対象file**: NRT/application/work_lifecycle.py、active_selection.py、scope_completion.py、commands/work_vnext.py、active_vnext.py、domain/selectors.py。tests/cli_runtime/test_active_vnext.py、test_work_finish_vnext.py、test_work_commands_vnext.py。新 tests/integration/test_issue413_finish_race.py（予定）。

**具体的変更順**: active show、同一direct set no-op、clear observed、動的祖先selectorを接続する。Finish対象とselection handleをremote前に固定し、完了確認後だけ該当handleを消す。親自動昇格とresume/rollbackを除く。既存のチェーン外Finish/子孫完了条件/--yesを維持する。

**変更禁止**: Finishの単なる選択解除化、Release追加、Close unknownでの解除、別WT record変更、最後に@currentを再解決、Finish/clearの共通lock追加は禁止。

**入力/出力例**: 入力: A選択→Finish A、またはFinish Aをremote待ちで止めてStart B --switch-active。出力: A completed、branch不変、B recordは保持。

**Red → Green / 検証**: Red: 旧テストの親昇格結果が新期待と異なる、遅い解除が新recordを消す、FinishがStart lock待ちになる。Green: captured tokenのみ解除、既にcompletedならPATCHなし、unknownなら選択保持。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_active_vnext.py tests/cli_runtime/test_work_finish_vnext.py tests/cli_runtime/test_work_commands_vnext.py tests/integration/test_issue413_finish_race.py -q
```

**期待結果・完了条件**: A Finish→B Startがflag追加なしで成立。not-plannedと未完了子孫は拒否。setの取得迂回0、GitHub/選択/branchの三結果が整合。

**対応**: RQ-413-05, RQ-413-07, RQ-413-08, RQ-413-10, RQ-413-12, RQ-413-14 ／ AC-413-10, AC-413-13, AC-413-14, AC-413-15, AC-413-16, AC-413-17, AC-413-21, AC-413-26, AC-413-30。

**失敗時の停止/戻り先**: active setのために第二stateやlockが必要になったらD-07へ。Close効果と解除成否が混ざればD-08へ戻る。

<a id="p-08"></a>
## P-08 Syncの複数選択表示を完成させる

**状態: 未着手。前提/依存: P-04,P-07。** 読む節: [D-04](design.md#d-04), [D-10](design.md#d-10)。補足: D-04, D-10。

**所有/対象file**: NRT/application/workspace_sync_vnext.py、commands/workspace_sync_vnext.py、presentation、domain表示型。tests/cli_runtime/test_workspace_sync_vnext.py、新 tests/integration/test_issue413_sync.py（予定）。

**具体的変更順**: generation/cache読書きを外し、worktree_observationからmemory viewを作る。local/github source、direct/descendant件数、親関係不一致、unknown/selected/プロセス未観測を表示する。CLIは既存workspace syncのまま。C-03のscopes行とcounts行をscope_idで対応させ、現在treeの未選択Scopeもlifecycleを出力する。scopesはJSON schemaの必須fieldとし、対応worktrees行のlifecycleと同じ観測結果を使う。

**変更禁止**: 中央active snapshot保存、cached GH状態のfresh化、activeによる依存完了、daemon/PID観測、未知件数を0へ補完することは禁止。

**入力/出力例**: 入力: 同親A/B選択、別WT読取不能、Aがremote closed。出力: 親descendant known count、complete=false、selectedとcompletedを独立表示。

**Red → Green / 検証**: Red: 旧Syncがcurrent active一つだけ、generation書込、cacheを使う。Green: 二WTが表示され、全record/metadata bytes不変、必要対象/祖先以外の他WT metadata読取0。AC-413-23ではA選択中/completed・B未選択/openを同時に置き、scopesに両行、countsにdirect=1/0、worktreesにAだけを要求する。CLI実出力をcli-schema.jsonで検証し、scopes欠落・不正lifecycle・未選択Bの脱落がRedになることを確認する。local modeでは同じGH-backed行がunknownとなる例も検証する。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_workspace_sync_vnext.py tests/integration/test_issue413_sync.py -q
```

**期待結果・完了条件**: local mode GET0、github mode ref dedup、失敗はunknown/exit7。全体をatomic snapshotと誤表示しない。

**対応**: RQ-413-04, RQ-413-11 ／ AC-413-08, AC-413-23, AC-413-24。

**失敗時の停止/戻り先**: 表示のために中央storeが必要になればD-10へ戻る。枝違いの祖先を片方へ黙って統一しない。

<a id="p-09"></a>
## P-09 GitHub発行・lifecycle・依存を台帳から切り離す

**状態: 未着手。前提/依存: P-07。** 読む節: [D-09](design.md#d-09)。補足: D-09。

**所有/対象file**: NRT/application/create_github_scope.py、import_github_scope.py、scope_create_vnext.py、scope_completion.py、dependency_vnext.py、github_scope_scaffold.py、infra/github_lifecycle.py。tests/cli_runtime/test_scope_github_vnext.py、test_scope_create_commands_vnext.py、test_scope_import_commands_vnext.py、test_scope_local_vnext.py、test_dependency_vnext.py。

**具体的変更順**: create --backend githubに限定して既存scaffoldへ確定番号を渡す。importの完全ref/currenttree重複検査を維持する。local新規/予約/marker/journal/retryを撤去する。GH authority/readinessはliveかunknownにし、既存local codecは保全互換性として残す。依存graphの実効値・循環検査を共通lockなしのsnapshot検査へ繋ぐ。

**変更禁止**: 新規local fallback、UUID、全件ID変換、GitHub応答を待たず正式Scope公開、unknown mutationのblind retry、依存にactive完了を使うことは禁止。

**入力/出力例**: 入力: fake ghが#57/#9012を返す三階層作成、#413 GET import、応答喪失。出力: 返却番号由来ID、unknown時scope=null、確定ref後local失敗はimport案内。

**Red → Green / 検証**: Red: --backend localで正式発行できる、cacheだけでGH祖先をopenと扱う、Create unknownで再POSTする。Green: 新規発行三kindがGH限定、metadata未知field保持、親kind/循環/二重登録の不正ケース拒否。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_scope_github_vnext.py tests/cli_runtime/test_scope_create_commands_vnext.py tests/cli_runtime/test_scope_import_commands_vnext.py tests/cli_runtime/test_scope_local_vnext.py tests/cli_runtime/test_dependency_vnext.py -q
```

**期待結果・完了条件**: POST/PATCH一回とGET確認をstateful fakeで検証。保全する旧ID/metadata testと廃止するallocator testが区別される。

**対応**: RQ-413-10, RQ-413-12, RQ-413-13 ／ AC-413-21, AC-413-22, AC-413-25, AC-413-26, AC-413-27, AC-413-29。

**失敗時の停止/戻り先**: 旧local testを全削除して構造安全まで失ったらD-09へ。通常metadata競合に全writer lockを戻さない。

<a id="p-10"></a>
## P-10 残る既存操作を狭い契約へ接続する

**状態: 未着手。前提/依存: P-08,P-09。** 読む節: [D-07](design.md#d-07), [D-11](design.md#d-11)。補足: D-07, D-11, C-05。

**所有/対象file**: NRTのscope query/edit/delete、Artifact、Workbench、worktree/target/bootstrap関連とcommands、cli/catalog.py/options.py。既存 test_scope_delete_vnext.py、test_artifact_vnext.py、test_workbench_vnext.py、test_worktree_create_vnext.py、test_worktree_remove_vnext.py、test_worktree_bootstrap_vnext.py。

**具体的変更順**: まずquery/editとdynamic selector、次にdelete/detach/clear observed、次にArtifact/Workbench、最後にGit worktree/明示bootstrapの順で接続する。それぞれold context/lock/journal/receiptを除き、C-05のpath/保全/partialを適用する。公開leafを増減させずtableと実parserを照合する。

**変更禁止**: 業務leafの大量削除、無関係なsyntax置換、overwrite/安全flagの理由なし廃止、make自動実行、stable WT ID台帳、metadataのchmod編集禁止は追加しない。

**入力/出力例**: 入力: branchを問わない明示Scope編集、Workbench上書きとdest-only、NAME/base/root指定WT作成。出力: 限定されたfile/Git効果だけと正確なpartial。

**Red → Green / 検証**: Red: controlなしで各既存業務が失敗、wt:aliasに依存、ignored成果物を無断削除、copyでdest-onlyを失う。Green: 各familyの正常/安全拒否/途中失敗を実file/Gitで検証する。query/edit→delete→Artifact→Workbench→worktreeの順で、一familyのfocused testがGreenになるまで次のfamilyへ進まない。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_scope_delete_vnext.py tests/cli_runtime/test_artifact_vnext.py tests/cli_runtime/test_workbench_vnext.py tests/cli_runtime/test_worktree_create_vnext.py tests/cli_runtime/test_worktree_remove_vnext.py tests/cli_runtime/test_worktree_bootstrap_vnext.py -q
```

**期待結果・完了条件**: 44 leafの対応に穴がなく、Start以外の共通lock取得0。各result fieldはC-05の表とcontract testが一致。

**対応**: RQ-413-12, RQ-413-15 ／ AC-413-25, AC-413-32, AC-413-33, AC-413-34。

**失敗時の停止/戻り先**: 未読の現仕様との衝突があればまず現file/testsを読み、D-11/C-05で最小差分を確定。便利機能を勝手に全廃しない。

<a id="p-11"></a>
## P-11 旧記録の保全診断とworkspace局所移行を実装する

**状態: 未着手。前提/依存: P-10。** 読む節: [D-03](design.md#d-03), [D-12](design.md#d-12)。補足: D-03, D-12。

**所有/対象file**: NRT/infra/legacy_reader.py（新設）、application/migrate_workspace_vnext.py、workspace_diagnostics_vnext.py、commands、cli/catalog.py。tests/cli_runtime/test_workspace_migrate_vnext.py、test_workspace_doctor_vnext.py、新 tests/integration/test_issue413_migration.py（予定）。

**具体的変更順**: 旧control/registry/active/journalを実行しないreaderに切り分ける。backupの実体確認後、schema3 workspaceのwriter_protocolだけ変更する。旧activeは自動変換せず、所在/保全方針を出力する。新protocolならunchanged、未知値は停止。通常経路に残った旧writer/receipt参照を除く。

**変更禁止**: 全metadata schema変換、旧control再生成、旧journal更新、active自動移植、旧writer停止をmarkerだけで証明、外部領域の勝手な削除を禁止。

**入力/出力例**: 入力: controlなし/正常/破損、旧protocolのworkspace、240件相当の保全fixture。出力: workspace一件だけの許可差分、旧.gitと全Scope bytes不変。

**Red → Green / 検証**: Red: controlなしでmigrateが始まらない、旧activeを二重採用、Scope全件を書換える。Green: 公開前後killでも次の新操作が現protocolで判定、backup不備なら変更0。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/cli_runtime/test_workspace_migrate_vnext.py tests/cli_runtime/test_workspace_doctor_vnext.py tests/integration/test_issue413_migration.py -q
```

**期待結果・完了条件**: 復元可能な実体保全、schema3保持、read-only legacy、不明を不明として返すことが確認できる。

**対応**: RQ-413-02, RQ-413-13, RQ-413-16 ／ AC-413-03, AC-413-28, AC-413-35, AC-413-36。

**失敗時の停止/戻り先**: 未知schema/未完了remoteの影響を確定できなければD-12とrunbookへ。通常起動へlegacy依存を戻さない。

<a id="p-12"></a>
## P-12 static資産・shim・配布skillsを更新する

**状態: 未着手。前提/依存: P-11。** 読む節: [D-02](design.md#d-02), [D-11](design.md#d-11), [D-12](design.md#d-12)。補足: D-02, D-11, D-12。

**所有/対象file**: src/spec_dock/shim_vnext.py、asset_layout.py、installation関連、assets/install_root/.agents/skills/spec-dock/SKILL.md、spec-dock-grill-with-docs/SKILL.md、assets/spec_dock/docs/templates、static inventory（package内新設）。tests/unit/infra/test_provider_distribution.py、tests/integration/test_installation_group_init_vnext.py、新 tests/integration/test_issue413_assets.py（予定）。

**具体的変更順**: package静的inventoryに既知tool-owned path/hashを収録する。installation show/init/update/uninstallを単WT static処理へ限定する。shimを外部console委譲へ改修する。skills/referenceのfixedengine/active取得/Sync世代/復旧説明を新契約へ変更する。配布parityはrealconsumer一括適用と切り離し、wheel内staticとprovider契約を比較する。

**変更禁止**: 実導入先への無断一括同期、Scope/成果物/直接状態の削除、未知ユーザー改変の上書き、gpt-5.6専用coder roleへの誘導を禁止。

**入力/出力例**: 入力: 既知旧資産、ユーザー改変資産、古いbranchから戻ったshim。出力: 既知差分だけのplan/apply、改変資産は停止、外部consoleは独立動作。

**Red → Green / 検証**: Red: 新installがruntime/controlをconsumerへ置く、更新が別WTへ及ぶ。Green: staticのみ、source/wheel整合、既存code更新でも仕様bytes不変。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/unit/infra/test_provider_distribution.py tests/integration/test_installation_group_init_vnext.py tests/integration/test_issue413_assets.py -q
uv build --wheel
```

**期待結果・完了条件**: 新版skillsとhelpが同じ44 leaf/部分制限を案内する。未導入consumer/dogfoodの更新をこのstepの実績へ含めない。

**対応**: RQ-413-16 ／ AC-413-37。

**失敗時の停止/戻り先**: static ownershipを立証できないfileはD-12へ戻す。名前だけでdirectoryごと削除しない。

<a id="p-13"></a>
## P-13 実入口E2Eと通常CIを閉じる

**状態: 未着手。前提/依存: P-12。** 読む節: [D-13](design.md#d-13)。補足: D-13 / 全D節。

**所有/対象file**: 全tests、.github/workflows/provider-ci.yml、fresh wheel harness。新 tests/integration/test_issue413_e2e.py（予定）。

**具体的変更順**: 下記E2E仕様を通常pytestへ組み込み、source importだけの検査と分離する。既存Ubuntu/macOS distribution laneを新wheelへ更新し、Windows adapterの実検査を明示する。最低Python3.10とCI3.11を含め、全部の通常testsを走らせる。

**変更禁止**: 部分Greenを全ACpassにする、skipをpassと記録する、fake GHをlive実績と呼ぶ、消えた保証のテストを理由なし削除、追加cacheによるテスト回避を禁止。

**入力/出力例**: 入力: candidate sourceとwheel hash。出力: 環境別help/Start/Finish/Syncの実console結果、全CI結果、未実施一覧。

**Red → Green / 検証**: Red: source不可でCLI停止、checkoutで別版import、二重開始、禁止write、Git原文喪失。Green: 全主要経路と境界に再現可能な証拠。通常CIもcandidateで実行する。

**実行コマンド（将来実行）**:

```text
git diff --check
make lint
uv run pytest
uv build --wheel
uv run pytest tests/integration/test_issue413_e2e.py -q
```

**期待結果・完了条件**: 42 ACの製品検証対象ごとにcandidate/command/actual exit/OS/Python/FSを記録。文書検査と実適用ACは別状態のまま。

**対応**: RQ-413-01, RQ-413-02, RQ-413-03, RQ-413-04, RQ-413-05, RQ-413-06, RQ-413-07, RQ-413-08, RQ-413-09, RQ-413-11, RQ-413-13, RQ-413-17 ／ AC-413-01, AC-413-02, AC-413-03, AC-413-05, AC-413-07, AC-413-09, AC-413-12, AC-413-15, AC-413-16, AC-413-18, AC-413-20, AC-413-24, AC-413-29, AC-413-38, AC-413-39。

**失敗時の停止/戻り先**: 失敗は該当D節/所有stepへ戻す。未試験OSをrelease対応として先に表明しない。

<a id="p-14"></a>
## P-14 Codexの成果物レビューとブラウザ検査

**状態: 未着手。前提/依存: P-13。** 読む節: [D-14](design.md#d-14)。補足: D-14 / requirement / CLI契約。

**所有/対象file**: 本packの採用コピー、provider docs/skills、local report.mdとartifacts/interview-worktree-start.mdはCodexが保持。

**具体的変更順**: 利用者確定回答と全R/D/P/CLI/schema/examplesをレビューする。ChatGPT自己点検を再実施し、さらに元validatorまたは独立DOM検査でCDN実描画/diagnostic拒否/zoom/keyboard/focus/mobileを確認する。変更が必要なら正文とmanifestを同時更新し、第二正本を作らない。

**変更禁止**: report/interviewの自動上書き、旧stateless案の混入、ブラウザ未実行を動作済み記録、独立Strictレビューを受けたふりを禁止。

**入力/出力例**: 入力: 配布ZIPとCodex保有証拠。出力: 採用差分、ブラウザ実結果、残余リスク。

**Red → Green / 検証**: Red: altered executable JS、切れたanchor、diagnostic SVG、390pxの全体横overflowを検出。Green: template byte一致、4/4正常図とzoom挙動、文書の整合。

**実行コマンド（将来実行）**:

```text
python -m json.tool manifest.json
# 同梱self-check.mdの再検査手順と、利用者環境のHTML validatorを実行する。
# validatorの実在path/commandはローカルcatalogから確認し、未確認の名前を実行済みにしない。
```

**期待結果・完了条件**: 文書採用レビューと動的HTML証拠が揃う。未実施をpassにしない。

**対応**: RQ-413-18 ／ AC-413-40, AC-413-41。

**失敗時の停止/戻り先**: 表示契約違反ならHTMLテンプレートへ戻す。重大なProduct矛盾なら当該RQ/D節を直してから実装側へ戻す。

<a id="p-15"></a>
## P-15 candidateを人間mergeへ渡す

**状態: 未着手。前提/依存: P-14。** 読む節: [D-14](design.md#d-14)。補足: D-14。

**所有/対象file**: 承認された実装branch、candidate source/wheel、通常CI/レビュー証拠。

**具体的変更順**: 製品実装結果と残余リスクを整理し、sourceとwheel対応を固定する。必要な通常Git配送は別途承認済みの作業契約に従う。mergeは利用者/人間の判断として渡し、自動mergeしない。package公開はさらに別の明示許可であり、merge成功に含めない。

**変更禁止**: ChatGPT文書作成をcode実装証拠にする、source不明wheelを受け入れる、自動commit/push/merge/publishを行うことは禁止。

**入力/出力例**: 入力: candidateとAC証拠。出力: 人間のレビュー/merge結果と実装履歴、公開未実施の区別。

**Red → Green / 検証**: 確認不成立: wheel/source不一致、必須未検証、保全方針なしならmerge-readyにしない。成立: 証拠が揃って人間が判断する。実施前に架空のRed/Greenを記録しない。

**実行コマンド（将来実行）**:

```text
git rev-parse HEAD
git status --short
# 人間が既存repository運用に従ってmergeする。自動mergeコマンドは本計画に含めない。
```

**期待結果・完了条件**: 人間mergeの実証がある。package公開、dogfood、#413登録は別途未完了として残す。

**対応**: RQ-413-18 ／ AC-413-42。

**失敗時の停止/戻り先**: 証拠不足はP-13/14へ戻る。scope Finishをmerge証明の代わりにしない。

<a id="p-16"></a>
## P-16 許可されたdogfood環境だけに適用する

**状態: 未着手。前提/依存: P-15。** 読む節: [D-12](design.md#d-12)。補足: D-12 / runbook M-01〜M-05。

**所有/対象file**: 許可されたcloneと対象WT、旧writer起動元、外部backup、承認wheel、workspace/static資産。

**具体的変更順**: 旧writer停止と実体backup/復元確認を先行し、外部環境へwheelをinstallする。controlなしのhelp/read/doctor、migrate dry-run→apply、static更新を個別に実施する。実際の240 Scopeとworkspaceを差分検査し、旧.gitと成果物が保全されることを確認する。

**変更禁止**: 全consumer/全WTへの自動展開、旧control再生成、未確認pendingの無視、git clean/reset --hard、実施許可がない環境へのwriteを禁止。

**入力/出力例**: 入力: 許可対象とbackup/wheel。出力: 実環境のsource/package識別、前後hash、command exit、未解決事項。

**Red → Green / 検証**: 適用前の不成立: writer停止不明、backup復元不能、unknown remote影響不明は停止。適用後の成立: 実対象の観測が条件と一致。fixtureのGreenを実適用へ転記しない。

**実行コマンド（将来実行）**:

```text
spec-dock --help
spec-dock --project "$ROOT" workspace doctor --raw --legacy --json
spec-dock --project "$ROOT" workspace migrate --to-schema 3 --to-writer-protocol specdock.worktree-writer/v1 --dry-run --json
# applyの正確な引数はrunbook M-04。ROOT/BACKUPは実在する許可対象を使う。
```

**期待結果・完了条件**: 対象WTだけの復旧が実測される。旧全Scope bytes一致、元資料保全、他WT未変更を記録する。

**対応**: RQ-413-16, RQ-413-18 ／ AC-413-36, AC-413-42。

**失敗時の停止/戻り先**: 異常はrunbookの観測段階へ戻し、自動rollbackせず、影響範囲を固定して停止する。

<a id="p-17"></a>
## P-17 既存#413を正式importし、資料と開始証拠を結び付ける

**状態: 未着手。前提/依存: P-16。** 読む節: [D-14](design.md#d-14)。補足: D-14 / runbook M-06。

**所有/対象file**: 既存GitHub #413、親epic-00356、許可例外配置、importが返すScope、Codexが保持するreport/interview。

**具体的変更順**: remoteと現在treeの登録有無、親祖先openを再確認する。既存#413をGET/importし、新規Issueを作らない。CLIが返したpathへ正文と二つの既存証拠を保全移動する。正式metadataを手作りしない。通常Gitで資料/metadataを保存してclean条件を満たした後、既存作業branchを明示した新しいwork startを実行し、開始証拠を別記録する。

**変更禁止**: #413再作成、pack名を登録証拠にする、report/interview上書き、旧新二箇所に正文を残す、資料importだけでFinish/Closeを実行することは禁止。

**入力/出力例**: 入力: 既存#413の完全refと親ID。出力: 実CLIのScope ID/path/linkage、移動後hash/link検査、明示Start結果。

**Red → Green / 検証**: 不成立: 二重登録、親terminal/unknown、dirty、切替先に新metadataなしは止める。成立: 正式Scopeと資料が一箇所にあり、Start成功と未完了項目を別々に記録。

**実行コマンド（将来実行）**:

```text
spec-dock --project "$ROOT" scope import github issue gh:chemitaro/spec-dock#413 --parent epic-00356 --title "External CLI State" --slug external-cli-state --dry-run --json
# applyはrunbook M-06。保存後、既存branchを--branchで明示してStartする。
```

**期待結果・完了条件**: 正式importとwork startがそれぞれ実測された時だけ完了。全受け入れを人間が承認した後のFinish/Closeは明示した別の完了操作である。

**対応**: RQ-413-18 ／ AC-413-42。

**失敗時の停止/戻り先**: 未登録/未開始を手編集で補わない。parent/target/Git条件不成立はD-06/D-09へ戻り、勝手にreopen/付替えしない。

<a id="regression"></a>
## 既存テストの維持・更新・削除理由

本文読取したテストと、treeで存在を確認し実装stepで全文再読するテストを [source-basis](artifacts/source-basis.md#tests) で区別します。以下の判断は名前だけでtest fileを丸ごと削除する指示ではありません。

| 既存test / 主な期待 | 扱いと意味のある後継 |
|---|---|
| test_active_vnext.py: select exact chain / noop / metadata不変 | chain導出、noop、metadata不変を維持。setによる新規取得だけWORK_START_REQUIREDへ更新 |
| 同file: clear_from_scope_preserves_ancestors | 親昇格期待を廃止。direct全解除、knownチェーン外noop、未知not-found、古いtoken解除が新recordを残す試験へ |
| test_work_start_vnext.py: open sibling switch flag / ancestry flag不要 | sibling明示許可を維持し、別directは祖先でも明示許可へ更新 |
| 同file: canonical branch / base / dirty / checkout / metadata | Git効果と対象整合を維持。registry参照は明示名へ。新規branchと既存branch再利用を別検査 |
| 同file: resume after branch/checkout/publication | operation IDのresume期待を廃止。成功済みGitを残す、開始false、現物観測後の新Startに置換 |
| test_work_finish_vnext.py: parent requires completed child / outside selected chain | 完了条件/チェーン外選択不変を維持。親の選択を残す期待だけ撤去 |
| 同file: local/GH lifecycle、already completed / resume | 既存local保全とGH完了を分けて維持。resumeをcurrent GET→新Finishに置換しunknown/遅い解除raceを追加 |
| test_workspace_sync_vnext.py: selection不変 / unknown freshness | 維持して複数WTへ拡張。generation/projection/cacheの成功期待は削除しreadonly stdout/JSONに置換 |
| test_scope_local_vnext.py: monotone allocator / gap / high-water | 新規local採番の仕様testを廃止し、旧入力拒否のnegative testへ。kind/祖先/保全はGH経路へ移して残す |
| 同file: stale open cache | cache利用の期待を撤去。明示live GETまたはunknown停止へ |
| test_cli_entrypoint_vnext.py: wheel rejected as mutating engine | この期待を撤回。fresh wheel実consoleが通常業務まで動く試験へ |
| 同file: controlなしCI validate、誤対象、環境分離 | 維持・強化。通常reader/業務へもcontrol-freeを拡張。fixed bundle hash試験は新package検査に置換 |
| test_provider_distribution.py: providerとdogfoodのruntime写し一致 | runtimeコピー保証は撤去。provider static→wheel→新consumerの一致を検査。実dogfood適用はP-16に分離 |
| 既存installation/group migration recovery | global control/engine handover/journal保証を廃止。単WT static保全、workspace宣言切替、中断後現物観測へ |
| 既存scope/dependency/Artifact/Workbench/worktreeの安全性 | 原則維持。context/lock/state差分だけ更新。既存test fileの末尾まで再読し、落とす各testにRQと理由を対応させる |

新規で必要なのは、同clone二processの重複開始、兄弟Issue並行、Start lock中の通常編集進行、Finish/clearと新tokenのrace、branch切替stale、Git原文、no cache/no独自.git write、fresh wheel E2Eです。実装を一行ずつ写しただけのtestではなく、誤った旧構造が残ると失敗する境界を選びます。

<a id="e2e"></a>
## Fresh wheel → 実console → fresh clone/linked worktree E2E

これは製品実装後の自動test harness仕様で、今回実行した試験ではありません。

1. candidateの `uv build --wheel` とsdist由来wheelを作り、source SHAとwheel hashを記録する。必要依存wheelは事前にwheelhouseへ揃える。
2. provider checkout外にfresh venvを作り、`pip install --no-index --find-links WHEELHOUSE WHEEL` で非editable installする。PYTHONPATH/PYTHONHOMEを除去し、制御したHOME/Git config/PATHを使う。
3. sourceとは別のfixture repositoryをGit commitしてcloneし、Gitでlinked worktreeを作る。GH-backed三階層metadataを持ち、独自control/registry/journal/cacheは存在しない。fixtureのGit commitを製品repoへのcommitと混同しない。
4. installed実consoleを絶対pathで起動する。Git/ghなしhelp/version/44leaf help、通常reader、旧writer宣言の明示migrationを確認する。source checkoutを改名/参照不能にし、import元がsite-packagesのみであることを診断する。
5. stateful fake ghを別実行fileとしてPATHへ置き、GET/POST/PATCHの状態と回数を記録する。製品APIへ直接mockしただけでconsole成功と呼ばない。実Gitを使ってStartのnew branch/checkout/record、別WT重複拒否、兄弟Issue並行、Sync複数行を検査する。
6. Finishはfake remoteをcompletedにし、記録だけ解除、branch不変を確認する。A Finish→B Start、途中checkout失敗/Close unknownを試す。wire通信を遮断し、live GitHub writeは0であることを検査する。
7. 前後で許可対象のbytes/mode/entry type、refs/index、記録file、禁止領域を比較する。read/dry-run/Syncの書込0、Start以外のcommon lock0を確かめる。OS atimeは内容変更証拠から除外する。
8. Linux/macOS/Windows adapterとPython3.10/3.11の実施状況を記録する。Windows起動/FS未確認を単なるPython unit testからpassへ変えない。ネットワークFS保証は追加しない。

通常CIは `git diff --check`、`make lint`、`uv run pytest` を維持します。配布専用laneの見直しは現在のprovider-ci内で行い、新しい品質ゲート組織や承認台帳を作りません。

## 完成証拠の別管理

| 証拠 | 所有者・実施step | 現在 |
|---|---|---|
| ChatGPTのpack静的自己点検 | artifacts/self-check.md | この納品内に実測範囲のみ記録 |
| 製品実装とfocused/全test | 実装担当、P-01〜13 | 未着手 |
| Codex成果物レビュー/実ブラウザ | Codex、P-14、保有reportへ追記 | 未着手 |
| 人間merge/任意の公開 | 人間、P-15 / 別途許可 | 未着手 |
| dogfood適用と実metadata保全 | 許可された実施者、P-16 | 未着手 |
| 正式#413 import / work start | 実施者、P-17 | 未着手 |

`report.md` と `artifacts/interview-worktree-start.md` はCodexの既存証拠であり、このpackの生成scriptや静的検査は書き換えません。unknown remote、旧writer停止不明、実体backup不足があれば該当適用を止めます。コードrevertでGitHub効果まで戻ったとは説明しません。
