# Issue #413 実装計画書

**全17 stepの実装を進行中です。** 各stepの実装・検証・独立レビューの状態は下記と[実装記録](implementation-report.md)で区別します。ChatGPTによるこのpackの生成・静的自己点検は、後続実装や製品の合格証拠とは別です。

実装担当は利用者指定の **GPT-6.1 Sol / reasoning Max**（2026-10-01の追加指示でHighから変更）。設定値は `model="gpt-6.1-sol"`、`reasoning_effort="max"`。本資料の著述モデルや独立Strictレビュー用のGPT-5.6 Sol / Proと混同せず、gpt-5.6系専用coder roleへ置き換えません。モデルの公開状況や能力比較はこの作業契約の判断材料にしません。

## 作業の境界・進め方

[要件](requirement.md) / [設計](design.md) / [CLI](artifacts/cli-contract.md) / [全件対応](artifacts/acceptance-matrix.md)。RTは基準のasset runtime、NRTは予定のsrc/spec_dock/runtimeです。新設tests/APIは予定と明示し、既存として実行済みとはしません。

各stepは一つの成果を閉じます。公開APIまたは既存portへ向けた結果比較をRedにし、ImportErrorやtest collection failureだけを意味のあるRedと呼びません。新moduleの接続が必要なら最小導線を先に作り、誤った現在挙動をassertionで検出してからGreenへ進みます。成功stub・一括skipは使いません。

通常編集やmetadataに包括的lock/権限制度を足しません。sourceの変更、製品テスト、成果物レビュー、人間merge、dogfood、正式#413 import/Startを別の証拠で扱います。後半の実環境作業は明示許可が前提で、コマンド例を掲載しただけでは実施許可や成功実績になりません。

依存の主経路はP-01→02→03→04→05→06→07→09、P-08は04/07後、P-10は08/09後、以後11→12→13→14→15→16→17です。OS test設計/資料レビュー準備は先行しても、同じ保存原語を別々に実装しません。

<a id="p-01"></a>
## P-01 契約・既存回帰・Redを固定する

**状態: 進行中。変更前baselineはlint成功・1217 passed/1 skipped、44 leafの契約照合と最初の公開入口Redを記録済み。個別回帰のRed→Greenは後続stepで追加し、全体gateは未完了。前提/依存: なし。** 読む節: [D-01](design.md#d-01), [D-11](design.md#d-11), [D-13](design.md#d-13)。補足: D-01, D-11, D-13。

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

**状態: 実装中。utility/package縦経路は検証済み、全gate未合格。実結果は[実装記録](implementation-report.md)。前提/依存: P-01。** 読む節: [D-02](design.md#d-02)。補足: D-02。

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

**状態: 実装中（POSIX境界とWindows API契約を検証、Windows native/storeと後続接続は未完了）。前提/依存: P-02。** 読む節: [D-03](design.md#d-03), [D-09](design.md#d-09)。補足: D-03, D-09。

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

**状態: 実装中（POSIX境界とWindows API契約を検証、Windows native/storeと後続接続は未完了）。前提/依存: P-03。** 読む節: [D-02](design.md#d-02), [D-04](design.md#d-04)。補足: D-02, D-04。

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

**状態: 実装中（POSIX境界とWindows API契約を検証、Windows native/storeと後続接続は未完了）。前提/依存: P-04。** 読む節: [D-05](design.md#d-05)。補足: D-05。

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

第10回Strictは`3e300afa`を固定してP1一件・P3一件でfail。全件を[分析記録](artifacts/code-review-p06-10-analysis.md)へ残し、branch familyのGit変更前後で捕捉したimmutable直接記録のidentity/hashを照合する修正と、Scope read helpの旧cache説明の訂正を行った。実checkout/reference-transaction hookで削除・置換・追記・空からの新規記録、nativeエラー経路を確認し、関連171 testsと変更3 source限定mypyが通過した。hookの変更を復元せず、確認済みGit効果と原文エラーをpartialへ保持する。P3の分類と利用者の修正認可を分けて記録し、fresh Strict passは未取得。

第6回Strictは`e6513650`のP-03〜P-08を対象にP1一件・P2四件でfail。全件を[分析記録](artifacts/code-review-p06-06-analysis.md)へ残し、未知/重複inventoryの行単位診断・Start停止、残存stageのpublication unknownをTDDで修正した。関連252 testsが通過し、fresh Strict passは未取得。P2の分類を変えず、同じfail batchに対する利用者の明示的な修正認可を適用した。

**状態: 実装中（第3回独立レビューは8ad73cfdを対象にfail。全5件を分析後、no-op checkout、checkout後clean、候補Scope/container構造、未確認token、sole selection公開確認を修正し、関連619件を検証。branch leafとPOSIX stage/rename/unlink強制停止も検証済み。Windows store/native受入と現在候補の独立レビュー等は未完了）。前提/依存: P-05。** 読む節: [D-05](design.md#d-05), [D-06](design.md#d-06), [D-09](design.md#d-09)。補足: D-05, D-06, D-09。

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

第6回Strictの物理identity不一致recordの無確認clearを修正し、captured recordを保全して`--all --yes`確認だけで解除できることを検証した。新しいlock・別WT操作・metadata補完は追加していない。

**状態: 実装中（POSIXの既存record境界を使いactive set/clearと動的selectorを接続・検証。GitHub-backed Finishの完了確認→captured token解除、子孫guard、dry-run、metadata再確認、native遅延解除/Start-only排他を検証。真正の既存local backendは単一metadataの保全更新を接続・検証。現在候補の独立認定、Windows nativeと旧runtime/testの退役は未完了。P-06の独立レビュー、Windows adapter/native受入は引き続き未完了）。前提/依存: P-06。** 読む節: [D-03](design.md#d-03), [D-07](design.md#d-07), [D-08](design.md#d-08)。補足: D-03, D-07, D-08。

第5回Strictの2件のP1と1件のP2を `artifacts/code-review-p06-05-analysis.md` で全件分析した。単一selection観測からのFinish target/handle固定、Close停止時のclear not_attempted、複数record解除のfailed/unknown/後続not_attemptedをTDDとOS境界で検証した。後続候補のfresh Strict passはまだ未取得であり、P-07完了とは扱わない。

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

第6回Strictに基づき、stale/unavailableで読めた直接recordの既知ID/refと件数を保持し、metadataがないGH refも今回のGET対象へ含めた。ID→refとref→IDの両方向のidentity conflictを検出する。unknown、祖先不明、readonly partial/7を維持し、記録や派生cacheを作らない。

**状態: 実装中（通常dispatchのreadonly Sync、現在treeと同clone各WTの必要対象/祖先、直接/子孫件数、local/github lifecycle、矛盾/不明の診断、JSON schemaとtextを検証。現在候補の独立レビュー、旧generation実装/testの退役、Windows nativeと全体gateは未完了）。前提/依存: P-04,P-07。** 読む節: [D-04](design.md#d-04), [D-10](design.md#d-10)。補足: D-04, D-10。

通常実装はNRT/application/direct_sync.py、presentation/command_data.py・envelope.py、cli/catalog.py・options.py、commands/runtime_dispatch.pyに配置した。旧workspace_sync_vnextは通常経路へ戻さず、P-12で実装/testを退役させる。readonly partial/exit7はeffects=[]であり、変更後失敗のpartial/exit6と区別する。

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

**状態: 実装中。三階層のGitHub-only create、GET-only import、close/reopenとdependencyの通常経路を検証。r8はcreate/import/close/reopenまでpass。dependencyの独立レビューと旧writer退役は未完了。前提/依存: P-07。** 読む節: [D-09](design.md#d-09)。補足: D-09。

通常createはNRT/application/direct_scope_publish.py、infra/directory_publication.py・github_remote.py、commands/runtime_dispatch.pyへ接続した。旧create/importのwriterは実行せず、既存のpure scaffold/親判定helperを再利用する。これらの旧moduleへのimport依存の抽出・退役はP-12で閉じる。22 creation testsとpublic contract/fresh wheelを含む29 tests、対象Ruffと変更6 source限定mypyが通過した。GitHub番号の旧allocator/marker/journalやScope UUIDを通常createへ戻さない。

importは同じ通常publicationに接続し、完全ref/URL/明示repository付き裸番号を検証してGETだけを行う。現在treeの二重登録を事前・公開直前・公開後に検査し、事後競合は両方のpathを返して保全する。新規metadataはinfra/scope_metadata.pyの無上書きwriterを使い、旧chmodによる編集制限を引き継がない。作成・取り込み・public contract・fresh wheelの47 tests、既存Start/active/Finish/observation/Syncの164 tests、全Ruff（379 files）と変更6 source限定mypyが通過した。この追加unitは93b15112のr7対象に含まれず、後続レビューを必要とする。

close/reopenはdirect_scope_lifecycleへ接続した。必要なlive target・子孫/祖先を観測し、純粋な完了/再開規則を維持する。選択とGit branchは変更せず、GitHub変更は一回のPATCHとGET確認だけ、真正の既存localはmetadataの未知fieldを保持して安全に置換する。unknownでは再送・Open推定をしない。実TTY確認と旧resumeのcontext前拒否も検証した。

第7回Strictは93b15112にP1二件でfailとなり、原文と[完全分析](artifacts/code-review-p06-07-analysis.md)を保存した。Finish内のnative Git診断、Scope dry-run必須field、確認済みdirectory公開後のScope結果をTDDで修正した。途中でidentity/linkageが変わったScopeは推定せずscope=nullを保つ。作成・取り込み・close/reopen・Finishの88 tests（28.76秒）が通過した。ローカル修正だけでは指摘を閉じず、新しいclean・push済みSHAでのfresh Strict passを必要とする。

第8回Strictは29d53925でpassとなった。P1はなく、P2二件を原文と[完全分析](artifacts/code-review-p06-08-analysis.md)へ保存した。Startとactive clearの並行解除、全leaf helpのv2表示は明示利用者認可に基づいてTDD修正し、関連175 tests・全Ruff・変更2 source限定mypyを通過した。限定passをIssue全体や最終gateの完了へ読み替えない。

dependencyはdirect_dependenciesへ接続し、metadataから宣言/継承を毎回導出する。checkの既定localは未観測GHをunknownとし、明示githubは対象/祖先/実効前提だけをGETする。add/removeは未知fieldとmodeを保全した一metadata置換で、全writer lockを取得しない。捕捉snapshotと物理identityの再検査、graph循環拒否、前段の並行編集保全、確認済み/不明な公開効果、readonly preview、text viewを公開境界で検証した。新公開/共有境界332 testsと旧dependency/query/help24 tests、全Ruff（383 files）・変更6 source限定mypyが通過した。旧read helperのpure部分抽出と旧writer退役はP-12で閉じる。

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

第11回Strictは `8c59994c` を対象にpass、P0/P1なし、P2五件。[原文](artifacts/code-review-p06-11.json)と[完全batch分析](artifacts/code-review-p06-11-analysis.md)を保全し、利用者の全指摘修正指示に従って、root Artifact create、Workbenchのmode競合、読取expect guard、Artifact sourceの終了値分類、静的shell補完をTDDで修正した。関連344 tests（63.50秒）、全source/testsのRuff check/format（400 files）、変更9 source限定mypy、diff checkが通過した。Bash/Zshは実shellで検証し、未導入のFishのnative検証を未実施として残す。native Worktree create/list/showは先行commit `245bcc1b` で検証済み。修正とnative unitを含む現在候補のfresh Strict、後続step、全体gateは未完了。

第9回Strictは`3c68053e`のP-02〜P-09を固定し、P1一件・P2二件でfailした。[完全batch分析](artifacts/code-review-p06-09-analysis.md)後、Scope create/importの明示guard、branch switchのcheckout後clean検査、stale/unavailableの既知recordを含むSync重複診断をTDDで修正した。関連83 tests（25.02秒）、変更3 source限定mypy、変更6 fileのRuff check/formatが通過した。P2のnon-blocking分類を維持し、利用者の全指摘修正の明示認可を適用する。Scope edit/deleteはr9の対象外であり、全体のfresh Strict合格は未取得。

**状態: 進行中。Scope query/edit/delete、Artifact、Workbench、native Worktree create/list/show/removeとPOSIX bootstrapの通常経路をローカル検証済み。native Windows、今回変更のfresh Strictと後続stepは未完了。前提/依存: P-08,P-09。** 読む節: [D-07](design.md#d-07), [D-11](design.md#d-11)。補足: D-07, D-11, C-05。

Scope editは一つの捕捉直接選択からdynamic selectorとguardを解決し、全metadata/workspaceのbytes・identityを再照合してtitle/revisionだけを変更する。未知field、本文、既存file mode、真正の既存local lifecycle、選択recordを保全し、GH通信・Start lock・control・journalを使わない。無変更はbytes/revision/identityを保持する。dry-runはstageを作らずC-05の必須fieldを返す。確認済み公開後のcleanup/Git失敗、置換結果不明、並行編集保全を公開CLIとネイティブOS/Git境界で確認した。関連124 tests（24.83秒）、全Ruff check/format（385 files）、変更4 source限定mypyとdiff checkが通過した。redirected stagingのexit3を期待したtestは、実際にはGitの原文拒否・exit5・write0が成立していたため、C-04へ期待値を訂正したもので製品Redではない。

Scope deleteは対象・incoming参照元・捕捉直接recordを新しい絶対pathの実backupへ保全・確認してから、参照元metadata変更、必要な捕捉token解除、対象subtree削除の順に進む。子・incoming edge・現在選択には各明示flagを要求し、GitHubやbranch、別WT recordを変更しない。backupはheld descriptorからexclusiveにコピーし、bytes/mode/link文字列を維持する。追加・変更された削除entryを保全し、各確認済み/unknown/未実施pathをpartialに残す。dry-runは同じ安全条件をread-onlyで検査し、全予定効果を表示する。実TTY、native Git原文、FIFO、リンク置換、mkdir/replace/unlink/close途中失敗、別processのStart排他非参加、別WTのstale、後続token保全を公開CLIで検証した。関連160 tests（26.86秒）、全Ruff check/format（389 files）、変更6 source限定mypyが成功した。旧inspection表の不足による初回collectionエラーを補正し、製品Redとは区別した。Artifact以後と全体gateは未完了。

**所有/対象file**: NRTのscope query/edit/delete、Artifact、Workbench、worktree/target/bootstrap関連とcommands、cli/catalog.py/options.py。既存 test_scope_delete_vnext.py、test_artifact_vnext.py、test_workbench_vnext.py、test_worktree_create_vnext.py、test_worktree_remove_vnext.py、test_worktree_bootstrap_vnext.py。

Artifactは所有者directoryの現存fileからtimestamp/suffixを候補化し、六typeのMarkdownとopaque fileを無上書き公開する。既存filename、未知evidence、旧scope/template置換tokenを保全する。実候補bytesを含む排他的な同directory stageで、同slotの並行候補を競合として返し、カウンタ・台帳・共通lock・自動再送を作らない。dynamic owner/guardは同じ捕捉直接選択を使い、root import/list/showは無関係なScope metadataへ依存しない。一覧は安全に保持したdirectory FDを列挙し、本文や外部source pathを開示しない。公開後のnative Git失敗、stage置換、結果不明なlink/mkdir、確認済み公開後cleanupを保全・分類した。関連227 passed/1 skipped（14.12秒）、source/tests Ruff check/format（392 files）、変更7 source限定mypyが成功した。fresh Strictと後続familyは未完了。

**具体的変更順**: まずquery/editとdynamic selector、次にdelete/detach/clear observed、次にArtifact/Workbench、最後にGit worktree/明示bootstrapの順で接続する。それぞれold context/lock/journal/receiptを除き、C-05のpath/保全/partialを適用する。公開leafを増減させずtableと実parserを照合する。

Workbenchは同cloneの明示された絶対pathをGit inventoryへ照合し、同Scopeの現存成果物をfile単位でコピーする。GitHub linkageは既存の正規化refで比較し、大小文字やlifecycle観測値を別Scopeと誤判定しない。errorは全衝突を適用前に拒否、overwriteは完全な候補を原子的に置換してdestination-onlyを保持する。相対link文字列・file mode・空directoryを保全し、source/destination/contextを再確認する。途中失敗では確認済み/unknown/未実施を分け、Gitエラー原文を保持する。共通Start排他・registry・journal・一括巻戻しは追加しない。実TTY、dynamic selector/guard、stage置換、unknown publication、無関係なprunable WTを公開CLIで検証し、関連153 tests（27.36秒）、source/tests Ruff check/format（396 files）、変更7 source限定mypyが通過した。旧CLI testのalias指定だけをC-05の絶対pathへ移し、既存のconflict/overwrite検査を維持した。全体型gateとfresh Strictは別途継続する。

native Worktree create/list/showはGitのNUL inventoryと同cloneの明示pathを使う。createのNAME必須化、root指定/既存環境変数、固定baseから`worktree/NAME`への作成を接続し、registry/receipt/recoverを使わない。sourceのclean/physical identity/直接recordを捕捉・再照合し、Git hookがselection/ref/作業treeを変えた場合や配置先の置換では現物を保全してpartialにする。dry-runは配置directoryもrefも作らない。関連52 tests（14.16秒）、旧createの六tests（4.10秒）、398 filesのRuff check/format、変更四source限定mypyが成功した。旧CLI recovery assertionはC-02の退役拒否と明示NAMEへ更新し、旧helperの退役はP-12へ残す。remove/bootstrapとこのunitの独立Strictは次の工程である。

native Worktree removeも同cloneの明示絶対pathへ接続した。main/current/bare、tracked/untracked dirty、locked/ignoredの無許可処理を適用前に拒否し、branchと外部pathを保全する。必要なsource contextと直接選択、保持したtargetの物理identity、native branch/HEAD/flagsとdirty/ignored条件をdry-run・unlock前・remove前に再確認する。unlock後のactor編集・ignored追加・branch変更・同path置換では後続削除を止め、完了したunlockは残す。Git途中エラー・timeout/signal・起動失敗・確認済み効果後のhandle cleanupを区別し、raw Git診断と確認済み/unknown/未実施の効果を返す。receipt/共通lock/force/branch削除/自動巻戻しを足さない。関連119 tests（24.90秒）、全source/testsのRuff check/format（401 files）、変更三source限定mypy、diff checkが成功した。bootstrap、fresh Strict、native OS検証と後続stepは未完了。

fresh Strict用の通常pushは自動承認審査により二回、実行前に拒否された。現在branchの通常非force pushについて明示的な利用者許可を質問中であり、回答前に再実行しない。既存Strict skillの一般的なpreapproval記述は審査で認可根拠として受理されなかった。ローカル実装・検証・checkpointは既存の実装認可に従って継続する。remoteとのSHA一致がない状態でStrictを起動したとは扱わない。

native bootstrapは同cloneの明示絶対pathでproject-owned `make init`を一回実行する。main/currentやtargetにworkspaceがない初期化も許し、bareを拒否する。dry-runはmakeを呼ばず、offline applyと未確認の実行は副作用前に停止する。makefileの優先順位・bytes/identityと捕捉したsource context/直接選択を実行前に再確認し、継承make optionと追加makefile注入を外す。出力を保持・開示せず、起動不能はfailed、非zero/signal/timeoutはunknownのpartial6、確認済み実行後のtarget置換やcleanup失敗ではsucceeded効果を残す。POSIX子process groupの停止、停止処理のIO失敗でstarted効果を隠さないこと、別processがStart排他を持つ間のbootstrapを実測した。関連168 tests（44.82秒）、全Ruff check/format（404 files）、変更四source限定mypy、diff checkが成功した。旧CLI recovery assertionのみ退役拒否へ更新し、旧helper/receipt退役はP-12へ残す。Windows process adapterは未接続で、P-12/P-13のnative実装・検証を別に完了させる。

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

**状態: 実装中。通常/raw/legacy Doctor、workspace局所移行、working-tree/固定HEAD validateをローカル検証済み。fresh Strictは未完了。前提/依存: P-10。** 読む節: [D-03](design.md#d-03), [D-12](design.md#d-12)。補足: D-03, D-12。

通常Doctorは共通controlを必要とせず、現在のScope構造・依存・Artifact・直接選択を読み取る。raw専用のGit-only admissionは未知workspaceでも安全なfile情報を返し、通常コマンドの既知schema/protocol判定を弱めない。`--legacy`だけが旧control/engine/registry/activeと操作・移行・installation・finalization・handoverの記録を読む。各fileは1 MiB、各記録directoryは4096 entriesまでに限定し、unsafe/破損/未知/途中記録は診断不完全のexit7とする。旧実行物を起動せず、phaseを現物の成功証明として採用せず、旧activeを新recordへ自動変換しない。任意bodyを出力せず、旧記録のdecoded bodyも分類後に保持しない。GitHub capability診断はrepository/PR/headの全指定と応答の一致を検査し、offline・指定不備を副作用前に拒否する。関連460 tests（88.15秒）、全source/testsのRuff check/format（410 files）、変更12 source限定mypy、diff checkが成功した。実consumerの宣言・metadata・直接選択は変更していない。

局所移行は新 `application/direct_migration.py` と `infra/migration_backup.py` に分離し、通常dispatchへ接続した。applyは新しい外部保全先・旧writer停止の運用確認・`--yes`を必要とし、dry-runはlock/stage/backup/Git/GitHub writeを行わない。現在checkoutの全実体と、外部common-Gitがある場合はその実体を保全し、隔離directoryへ復元してbytes/type/mode/symlink値を比較する。確認後も保全先の物理identity/contentとsourceを公開前後に再確認する。変更するtracked fileは自workspace宣言だけで、既存control_epochだけを除き、title/project_linkageや未知設定を追加・改名しない。旧activeは保全し新recordへ取り込まない。未確定旧記録は適用前停止とする。新宣言で妥当なら旧記録をresumeせずunchangedを返す。

240 Scope fixtureの全metadata bytes・二つの旧local綴りGitHub ID・未知任意fieldを保全した。構造検査のArtifact読取に取得済みviewsを渡し、Scope metadataの再ロードを57,840回から240回へ減らした。永続cacheは追加していない。native別processを公開前後の境界でSIGKILLし、fresh processの未切替/切替済み判定を確認した。保全・復元の失敗、後続のuser edit、保全先改変、原文Gitエラーとpartial効果も検証した。関連runは643 passed/1 failed（旧mapping help assertion、131.65秒）で、現在の宣言切替helpへport後、migration/help 60 tests（10.98秒）と全source/testsのRuff check/format（413 files）、変更9 source限定mypy、diff checkが成功した。全体gateやfresh Strictの合格とは扱わない。

validateは`application/direct_validation.py`と`infra/committed_validation.py`へ接続した。通常は現在の既知workspaceの構造だけを検査し、明示expect-currentがある時だけ直接選択の期待条件を確認する。CIはGit-only contextでHEADを一度固定し、固定OIDのtreeとmetadata blobだけからworkspace/三階層Scope/親子/依存/Artifactの名前・種類を検査する。Artifact本文、実行状態、旧記録を取得せず、作業treeの未commit破損や検査中のHEAD移動に混ぜない。CIのlive expect-current/expect-backendは無視せず明示拒否する。構造不適合はexit7、原文Git失敗は効果0のexit5。空workspaceは通常valid、require-nodes時だけ不適合とする。Start lock、Git/GitHub write、永続cache・検査recordを追加していない。

公開CLI 50 tests（5.26秒）とfresh wheel/sdist/外部venv実consoleを含む51 tests（11.51秒）が成功した。固定HEADとworking copyの逆方向の破損、HEAD移動、linked自身のHEAD、三階層、Artifact slot衝突とsymlink、metadata bodyだけの取得、旧protocol reader、未知実行状態非採用、期待条件、dry-run、Git原文エラーを検証した。全source/testsのRuff check/format（416 files）、変更source/test六file限定mypy、diff checkが成功した。全体gate・native Windows・fresh Strictの合格とは扱わない。

Doctor・migration・Start・Finish・Sync・依存・Artifact・Workbench・Worktree・store/lock・helpの関連24 filesは646 passed（114.68秒）。修正済みmigration helpもこのfresh runで成功した。独立Strictの取得までP-11の状態は実装中として維持する。

**所有/対象file**: 新runtime `src/spec_dock/runtime/` の infra/legacy_reader.py、infra/migration_backup.py、infra/committed_validation.py、application/direct_migration.py、application/direct_validation.py、application/workspace_structure.py、commands/runtime_dispatch.py、cli/catalog.py/options.py。旧application/migrate_workspace_vnext.pyとworkspace_diagnostics_vnext.pyの退役はP-12。tests/integration/test_issue413_migration.py、cli_runtime/test_issue413_workspace_doctor.py、cli_runtime/test_issue413_workspace_validate.py、integration/test_issue413_wheel.pyとhelp tests。

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

**状態: 実装中。PATH委譲shim、package資産inventory、単WTのinstallation四leaf、配布docs/skillsとsource/wheel/新規consumerの一致をローカル検証済み。既知旧hashの更新・退役と保全・部分失敗も確認した。provider旧実装退役は未完了。前提/依存: P-11（ローカル検証済み・fresh Strict未完了）。** 読む節: [D-02](design.md#d-02), [D-11](design.md#d-11), [D-12](design.md#d-12)。補足: D-02, D-11, D-12。

`shim_vnext.py`と配布static shimを、PATH上の外部consoleへargv/cwd/終了値/stderrを保持して委譲する入口へ置換した。Git/control/engine digest/consumer Pythonの取得を削除し、自身の同inode・symlink・hardlink・同shimのコピー・既知旧shimを委譲先に認めない。既存package managerで導入したconsoleへの正常symlinkは受理する。外部console不在等は導入案内とv2診断を返し、double-dash後のjson文字列は共通flagとして解釈しない。caller Python import環境を外し、通常の利用者設定は保持する。

native POSIX `./spec -h` symlink経路、Git不在・nested cwd・不正project・Unicode/改行を含む引数、外部stderr/終了値、再帰防止とPython import分離を12 casesで確認した。fresh wheel/sdist/外部venv/配布shim実起動とprovider parityを含む16 tests（6.71秒）、全source/testsのRuff check/format（417 files）、変更四file限定mypy、diff checkが成功した。実consumerのshim/本文/状態は未更新。旧fixed-entrypoint suiteは13 passed/2 failed（3.92秒）で、PATHを無視するpin期待と旧group init経路を残している。前者は新PATH契約へ、後者と旧engine helpersは後続installation/退役作業へportし、full gate前に閉じる。native Windowsとfresh Strictは未完了。

`installation init ABS`と`show --target ABS`はGit-only admissionで明示rootを解決し、未導入先でも共通controlなしで動く。initはpackage inventoryの86 static filesと新writer宣言を一件ずつ公開し、既存fileを計画時に拒否する。dry-runはdirectory/stage/recordを作らない。途中失敗では公開済みdirectory/file、unknown publication/候補、未実施資産を区別し、自動巻戻ししない。main/linked間の一括適用は行わず、実consumerも未変更である。新規導入・unsafe entries・guard・途中失敗・Traversable ZIP資産・fresh wheel/sdist/外部venvの実consoleを含む関連67 tests（18.05秒）、全source/tests Ruff check/format（420 files）、変更七file限定mypy、diff checkが成功した。full-suite/type gateとfresh Strictの実績ではない。

`update/uninstall --target ABS --backup-dir ABS --yes`を新writer workspaceの既知static hashへ限定した。置換・退役する旧bytesは外部backupで実際に復元・比較し、未知改変は保全前に拒否する。workspace宣言の未知設定、Scope、Artifact、Workbench、直接記録、Git内の旧情報は変更しない。uninstallはworkspace宣言とignore規則も残す。既知旧runtime138 filesとversion一fileのpath/hashは基準commitへ照合済みで、名前だけの再帰削除をしない。外部保全の後片付け・公開・退役失敗はbackupと実施済み/unknown/未実施をpartial6へ残す。四leafのhelpと廃止引数も更新した。関連98 tests（75.93秒）、全source/tests Ruff check/format（421 files）、変更八file限定mypyが成功した。fresh wheelの外部venvでupdate/uninstallも実行した。旧provider helpers、配布docs/skills、native Windows、full gate、fresh Strictは引き続き未完了。

**所有/対象file**: src/spec_dock/shim_vnext.py、asset_layout.py、runtime/application/direct_installation.py、runtime/infra/static_assets.py、installation関連、assets/install_root/.agents/skills/spec-dock/SKILL.md、spec-dock-grill-with-docs/SKILL.md、assets/spec_dock/docs/templates、assets/static-inventory.json。tests/unit/infra/test_provider_distribution.py、tests/integration/test_installation_group_init_vnext.py、tests/integration/test_issue413_assets.py、tests/integration/test_issue413_wheel.py。

README・配布reference・migration・offline HTML・二skillを外部CLIと一件直接対象の契約へ改定した。active setは同一妥当directへのunchangedだけ、Syncはdata直下の観測、Artifactはdata.result.artifact.pathを使う。旧engine/control/cache/新規local作成のHistorical操作案内は退役通知へ置換し、pathsは保持した。実dogfoodを更新せず、新CLIによる一時consumerとwheel全86静的資産をproviderへ照合する。変更18資産の旧hashはfb42d21fe53e993439c293a1412e746665a81399のblobから検証・登録した。文書/配布/Grill helperの213 tests（2.35秒）、wheel/installation/shim/help関連98 tests（74.42秒）、全source/tests Ruff check/format（423 files）、変更五test file限定mypyが成功した。Grill finalizerが実Artifact JSON pathを受け、16 canonical文書とmetadata/Gitを保持することも確認した。HTMLは24 unique IDs・35解決済みlinks・外部依存0の静的検査を通過した。最終人間資料・ブラウザ検査・native Windows・full gate・fresh Strictは別途未完了。

**具体的変更順**: package静的inventoryに既知tool-owned path/hashを収録する。installation show/init/update/uninstallを単WT static処理へ限定する。shimを外部console委譲へ改修する。skills/referenceのfixedengine/active取得/Sync世代/復旧説明を新契約へ変更する。配布parityはrealconsumer一括適用と切り離し、wheel内staticとprovider契約を比較する。

公開migration helpの復旧option注入を一件のRed→Greenで除去し、native bash/zshの補完でも旧flagを提示しないことを確認した。CLI契約とhelp suiteを新契約/public mainへportし、旧44 leaf・引数・有限timeout・usage/JSON等の検査目的は維持する。関連113 tests（22.36秒）、型境界補足後のhelp 29 tests（0.78秒）、全source/tests Ruff check/format（423 files）、変更四file限定mypyが成功した。残る旧内部dispatcher用対応表・provider/runtime helpersの退役とfull gateは未完了。

旧fixed-entrypoint suiteを通常wheelの非editable外部venvと実consoleへportした。廃止/維持する各保証の根拠は[公開入口テストの移行](artifacts/test-port-entrypoint.md)へ全15旧test単位で記録する。Issue Start→Sync→Finish、旧locator不採用、環境分離、二cloneの独立観測、通常/CI validateの書込0を確認した。entrypoint 14 cases（6.23秒）と関連wheel/shim/providerの30 tests（23.84秒）が成功した。実Gitのbranch保持とfake GHのIssue一回closeも別に照合した。これは既存実装のGreen回帰であり、native Windows/full gate/fresh Strict/最終手動検証ではない。

CIのfixed bundle経路も通常wheelへ移し、新writerのHEAD検証が旧v1/exit7からv2/exit0へ変わるRed→Greenを確認した。[CIテストの移行](artifacts/test-port-ci.md)に七casesの維持/変更理由を記録する。source SHA/clean確認後のGit archiveをbuildし、外部venvの実consoleで読取だけを行う。元source/targetは全entry type/mode/bytesが不変、旧builder sentinelの実行0。CI suite 7 tests（4.42秒）が成功した。既存Ubuntu/macOS配布laneは新wheel/static installationの試験へ切替え、通常lint/全pytestは保持した。remote CI実行、Windows、全体gateは未完了。

同候補の実consumerを通常wheel/実consoleでHEAD検証し、240 nodes/valid/効果0、metadata/workspace hash不変を確認した。通常全pytestの途中確認は79 failed/2056 passed/1 skipped（417.10秒）で、18旧経路filesの個別portが残る。[Writer admission移行](artifacts/test-port-writer-admission.md)では旧14 casesの仕様判断を記録し、自WT宣言、他WT protocol不一致の非干渉、実Start排他中の別WT Scope編集を四公開cases（0.77秒）で確認した。全件成功/Windows native/実cutover/fresh Strictの実績へ読み替えない。

**変更禁止**: 実導入先への無断一括同期、Scope/成果物/直接状態の削除、未知ユーザー改変の上書き、gpt-5.6専用coder roleへの誘導を禁止。

Work/branch旧adapter三filesも公開mainへportし、[七旧関数の対応](artifacts/test-port-work-branch.md)を記録した。三kindの一件選択/Finish、ref非reset、preview書込0、v2/current selector、親昇格なしを九casesで確認し、既存hook/Start/active/Finishと合わせた186 tests（62.83秒）が成功した。全Ruffと変更三test file限定mypyも成功。旧Scope/installation/recovery経路のport、provider/runtime退役と全体gateは引き続き未完了。

Scope lifecycleの旧確認競合保証は公開processへ移し、確認中に別Startで選択を変更しても旧対象をCloseしてしまうRedを検出した。[修正根拠](artifacts/scope-confirmation-recheck.md)の自WT再読取比較で同じtestをGreenにし、関連90 tests（20.90秒）と変更source/test限定mypyが成功した。共通lock/lease/権限は追加せず、Scope確認だけの楽観的比較を保持する。新候補の独立Strictは未実施。

Scope lifecycle/query/deleteの旧三filesも[十一関数の判断](artifacts/test-port-scope-lifecycle-query-delete.md)を記録して公開mainへ移した。既存local codec保全、GH-backed current/guard、読取とtitle/revision編集、確認・preview・実backup後の削除を十casesで確認し、guard省略を含む確認競合四casesと現行Scope suiteを合わせて81 tests（21.05秒）が成功した。全Ruff/変更四test限定mypyも成功。残る旧公開経路のport・provider退役・全体gateは引き続き進行中である。

Scope create/importの旧二十関数も[個別の移行判断](artifacts/test-port-scope-create-import.md)を記録し、公開mainの十三casesへ移した。GH番号・preview・承認・不存在親・既存local codec・確認中origin変更・remote成功後の明示importを検査し、関連publication/import/editを合わせて78 tests（24.92秒）が成功した。全Ruffと変更二test限定mypyも成功。通常全体gateとprovider退役は未完了のまま継続する。

Workspace diagnosticsの旧二ファイル・九関数も[移行対応](artifacts/test-port-workspace-diagnostics.md)を記録して公開mainへ移し、関連122 tests（16.75秒）が成功した。空tree、HEADのCI検査、旧制御情報の明示legacy診断、同時dependency/artifact不整合をread-onlyで保護する。全Ruff/変更二test限定mypyも成功。移行/同期/旧配布経路とprovider退役は継続する。

Workspace migrate/syncの旧十二関数も[対応表](artifacts/test-port-workspace-migrate-sync.md)を作り、公開mainの九casesへ移した。自宣言だけのpreview/backup後apply、退役mapping/rollback拒否、既存local/空tree、directとopaque旧cacheの保全、GH取得失敗とinvalid metadataを検査。現行integrationを合わせて67 tests（16.30秒）、全Ruffと変更二test限定mypyが成功した。全体gate/provider退役/Windowsは継続中。

Worktree旧adapterの三関数も[移行記録](artifacts/test-port-worktree-adapter.md)を残して公開mainへ移し、native path/list/show、create/removeのpreviewとbranch保持、make initの明示実行を検査した。関連115 tests（23.83秒）、全Ruff/変更一test限定mypyが成功。旧installation/recoveryとprovider退役、通常全体gateは継続する。

旧recovery suiteの31関数も[個別の判断](artifacts/test-port-recovery.md)を記録した。23件のjournal/control前提は公開matrixへ移し、十二操作×resume/rollbackの24 casesでproject読取前の拒否・旧証拠保全を検査した。低水準atomic JSON八件は本文を変えず別suiteへ分離し、共有helpersと旧transaction APIの参照整理は後続stepへ残す。関連Scope publication/import/Finish/migrationを合わせた148 tests（39.36秒）、全Ruff/変更二test限定mypyが成功した。provider退役、全体gate、native Windowsとfresh Strictは継続中。

旧group installation/finalization/engine handover四files・54関数も[個別判断](artifacts/test-port-installation-retirement.md)を記録して退役した。新仕様と逆向きの全WT control/epoch/rollback成功条件を外し、公開static・wheel/provider/retired-option suiteで後継を維持する。native fsync境界でsame-bytes/mode・別inodeの外部差替えを注入するupdate/uninstall二casesも成功し、関連99 tests（74.91秒）、全Ruff/変更一test限定mypyが成功した。旧sourceの参照整理と全体gateは継続する。

旧fixed bundleの二入口も[製品退役の判断](artifacts/provider-retirement-fixed-entrypoints.md)を記録し、先行した実wheel収録禁止のRed（1 failed/0.80秒）から二source削除後のGreen（1 passed/14.34秒）を確認した。fresh sdist/通常wheel/外部venv/実consoleと静的資産保全を検査し、関連24 tests（13.03秒）と全Ruff/変更test限定mypyが成功。runtime_loaderと旧dispatcher/制御sourceの参照整理、README/AGENTS記述、通常全体gateは継続する。


通常全pytestはclean a3844fc3で2048 passed/1 skipped（369.70秒）、失敗0になった。同snapshotの通常make lintはRuff成功・mypy 559 errors/63 filesで未合格。最後の旧CLI adapter四files・十二関数も[個別対応](artifacts/test-port-remaining-adapters.md)に従い退役し、公開Installation showの非Git target保全/raw Git診断を補った。後継四suiteは182 tests（94.98秒）、全Ruffと変更一test限定mypyが成功した。旧providerの退役・通常型gate・native Windows・fresh Strictは引き続き未完了である。


旧dispatcherとcommand 17 files・84 symbolsも[製品退役の対応](artifacts/provider-retirement-dispatcher.md)を確認し、候補外import 0で一緒に削除した。実wheelの収録禁止はRed 1 failed（0.79秒）→同じtestのGreen 1 passed（14.41秒）。関連公開入口/44 leaf/CI/recovery/providerの88 tests（13.37秒）、通常collection 2038件、全Ruff/変更wheel test限定mypyが成功した。旧application/control/journalの共有helpers分離と退役、full type gateは引き続き継続する。


現行Scope publicationの旧writer importも[十一helpersの分離](artifacts/provider-scope-helper-isolation.md)で解消した。公開previewが旧七modulesを読むRed 1 failed（0.44秒）→同test Green 1 passed（0.32秒）、GH importを含む二cases（0.92秒）を確認。関連97 tests（23.72秒）と通常wheel一test（15.66秒）が成功した。通常make lintはRuff成功・mypy 443 errors/49 filesで未合格。旧private writers/controlの退役と残る型問題は継続する。

**fixed engine locator / group installationの製品退役**

旧三module・48 symbolsの全文と候補内外のimportを確認し、[個別判断](artifacts/provider-retirement-engine-group.md)を保存した。candidate外source/test importはTYPE_CHECKINGを含め0で、閉じた三moduleを一緒に削除した。engine pin、全WT control/epoch、group journal、handover/finalization/resume/rollbackを通常配布から除去し、既存legacy証拠の読取・保全は維持する。互換alias・fallback・build除外は追加していない。

通常wheelへ三moduleの収録禁止を先行し、正常build後に旧codeが存在するRed 1 failed（0.96秒）を確認した。削除後、同じ受入れ試験は1 passed（14.12秒）。fresh wheel/sdist/外部非editable venv/実console/局所static操作とtree保全を検査した。公開assets/entrypoint/provider/retired-recoveryの関連100 tests（72.84秒）も成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-engine-retirement-{red,green,related}.logへ保持した。

全source/tests Ruff check/format（395 files）、変更wheel test限定mypy --follow-imports=silent、diff checkが成功した。直近通常make lintの443 errors/49 filesは未合格のままで、この限定検証をfull gateへ読み替えない。旧private writers/journal/registry/shared helpersの参照整理、残る型問題、native Windows/別Python、fresh Strict、最終手動確認を続ける。実consumer・既存WT・旧Git領域・live GitHubは未変更。

**Scope完了判定の旧writer分離**

現行close/reopenのpure plan七symbolsを[小moduleへ分離](artifacts/provider-scope-completion-isolation.md)し、旧control/WriterLock/journalを現行経路からimportしないようにした。移動七nodes、旧moduleに残る七nodes、現行adapterの四functionsはAST本体が元HEADと同一。旧private callersも同じauthorityを使い、三階層/既存codec/選択/checkoutの契約を変えない。

fresh processの公開close previewは旧六modules読込でRed 1 failed（0.61秒）、分離後の同testはGreen 1 passed（0.58秒）。reopenへ広げた二casesは2 passed（0.94秒）。GH GET一回だけ、v2/planned、tree不変を確認した。関連old lifecycle/current lifecycle/Finishの76 tests（22.00秒）、通常wheel一test（13.60秒）、全Ruff check/format（396 files）、変更三files限定mypy --follow-imports=silentとdiff checkも成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-completion-isolation-{red,green,related,wheel}.logへ保存した。

通常全体lintは直近443 errors/49 filesで未合格のまま。通常source rootsの保守的AST closureは88 modules、未到達96 modulesだが、これだけを一括削除の根拠にしない。old writer/private testsの個別対応と製品参照確認、残る型問題、native Windows/別Python、fresh Strict、最終手動検証を継続する。実consumer/live GitHubは未変更。

**参照を失った旧入口・facade・派生保存adapterの退役**

旧21 modules・136 top-level関数/classの全文と[個別責務](artifacts/provider-retirement-unused-entrypoints.md)を確認して削除した。AST importに加えてsource/tests/setup/pyproject/scripts/CIの文字列参照を検査し、候補外import 0・内部deps→ids一件だけを確認。未使用に見えたgit_helperは旧git_cliのpython -m呼出しがあったため保持した。現在の三階層/ID codec/業務/safetyと、明示操作の後継を照合し、中央control/cache/派生保存/復旧receiptを温存しない。

通常wheelは先行した収録禁止でRed 1 failed（0.75秒）、削除後の同testはGreen 1 passed（13.38秒）。通常collectionは2042 tests（0.38秒）、関連公開CLI/entrypoint/Doctor/Sync/依存/Workbenchは222 tests（36.58秒）が成功した。通常make lintはRuff成功・mypy 407 errors/45 files（294 source files）、exit2で未合格。source 58/test 349 errorsを個別に整理・修正する。変更wheel test限定mypyとdiff checkも成功。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-unused-entrypoints-{red,green,collection,related}.log、lint-p12-c633-retirement.logへ保存した。

通常全pytestの再合格、full type gate、native Windows/別Python、fresh Strict、最終手動検証は未完了である。実consumer・既存WT・旧Git領域・live GitHubは未変更。

**新規local Scope作成試験の退役**

旧local createの十二test関数と二helpersを全文確認し、[保証別の判断](artifacts/test-port-local-scope-retirement.md)で退役した。候補外helper importは0。独自local採番/high-water/cache/offline createの成功条件を残さず、GH番号SSOTと既存local metadata保全を維持する。親差替えsafetyはpublic main/native Git/stateful gh/OS fsyncの境界へ移し、replacement tree不変・元metadata/ref保全・partial/6を二casesで確認した（2 passed、1.15秒）。最初のnot_attempted期待はstage開始済みを反映したfailedへ訂正し、製品Redには数えない。

関連current publication/import/create/query/lifecycle/migrationの128 tests（38.34秒）、全Ruff check/format（374 files）、変更publication test限定mypy --follow-imports=silentとdiff checkが成功した。最初の存在しない二test file指定はexit4/zero testsで、実在fileへ訂正した結果だけを回帰証拠にする。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-local-creation-retirement-related.log（中断）とpytest-local-creation-retirement-related-2.log（成功）へ保持した。全体lintは直近407 errorsで未合格のまま。旧source/private writersの整理、full gates、native Windows/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**Scope照会・タイトル編集試験の公開CLI移行**

旧三testを[公開CLIの保証へ置換](artifacts/test-port-scope-query-edit.md)した。既存local/GH metadataのkind/state/query、直接recordの@current、旧cache非採用、title/revision以外の未知field・仕様bytes・既存mode保存、同title noopを確認する。新local作成/control付きfixtureを残さず、gh request 0・effects空・tree保全を公開main/native境界で検査した。一件ずつ1 passed（0.34/0.24/0.34秒）で、既存Greenのcharacterizationであり製品Redではない。

参照を失った旧edit_scope.pyの二symbolsを全文・source/test import確認のうえ退役した。通常wheelの収録禁止はRed 1 failed（0.77秒）、source削除後の同testはGreen 1 passed（13.37秒）。関連query/edit/create/契約40 tests（6.23秒）、全Ruff check/format（373 files）、変更二test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-query-port.log、pytest-scope-query-source-{red,green}.log、pytest-scope-query-port-related.logへ保持する。

直近通常lintの407 errors/full gate・native Windows/別Python/fresh Strict・最終手動確認は未完了である。旧作業/Scope/private writersの整理を続ける。実consumer/live GitHubは未変更。

**旧Start/Finish試験・writerの退役**

旧二filesの29 test関数・1002行と旧work_lifecycle.pyの26 symbols・1175行を全文確認し、[保証別の個別判断](artifacts/test-port-work-lifecycle-retirement.md)を残した。candidate外importはTYPE_CHECKING/from-import子moduleを含め0。暗黙祖先switch/Finish後の親昇格/registry/epoch/journal/cache resumeを廃止し、必要な保証は公開main/native Git/stateful ghへ対応づけた。skip/収集除外は増やさない。

新しい公開試験では、子だけのFinishが直接選択中の祖先を保持（1 passed/0.75秒）、既存local親がGH子のopenを拒否しlive completed後に親だけを完了・capture解除（1 passed/0.67秒）、親子どちら向きのStartも明示switch必須（2 passed/1.12秒）、candidate graphでの明示branch readiness（1 passed/0.82秒）、三kind×attached/detachedのbase必須とdetached明示開始（6 passed/2.96秒）を検査した。現行Greenのcharacterizationである。parametrizationのcollection誤りとreadonly GETも0とした過剰期待は訂正し、元失敗logを保持した。

通常wheelの旧writer収録禁止はRed 1 failed（1.11秒）、source削除後の同testはGreen 1 passed（14.59秒）。関連Start/Finish/Active/lifecycle/native並行Startは187 tests（66.63秒）が成功し、その後base六casesをfocused実行した。全Ruff check/format（370 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-work-lifecycle-port.log、pytest-work-start-candidate-readiness.log、pytest-work-lifecycle-source-{red,green}.log、pytest-work-lifecycle-retirement-related.logへ保持する。

旧source/private helpersの残り、通常full type/pytest、native Windows/別Python、fresh Strict、最終手動確認は継続中である。直近通常lintの407 errorsは別snapshotの未合格記録で、今回の限定成功で置換しない。実consumer/live GitHubは未変更。

**旧Scope lifecycle試験・writerの退役**

旧八test・一fixture class（303行）と旧scope_completion.pyの七symbols（494行）を全文確認し、[個別対応](artifacts/test-port-scope-lifecycle-retirement.md)を保存した。pure completion planの本体を維持し、最後のScope delete helper importだけをauthorityへ向けた。一importのmodule field以外、全ASTは元HEADと同一で、退役二fileへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

公開Close/Reopenの子/祖先三状態guardは六casesで6 passed（2.24秒）、terminal reason conflictは1 passed（0.46秒）、既存local noop/任意field/metadata/record/tree保全は1 passed（0.37秒）だった。collection parametrization誤りとnoop effectsの過剰な空期待を訂正し、失敗logも保持した。現行Greenのcharacterizationであり製品Redではない。

通常wheelの旧writer収録禁止はRed 1 failed（0.76秒）、source削除後の同testはGreen 1 passed（13.71秒）。関連Scope lifecycle/Finish/旧・現行Scope deleteの115 tests（34.01秒）、全Ruff check/format（368 files）、変更二test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-lifecycle-port.log、pytest-scope-lifecycle-source-{red,green}.log、pytest-scope-lifecycle-retirement.logへ保持する。

このunit前のclean 0c04677bada135dbb50ea0c48f7fc3b4aae368c9の通常make lintはRuff成功・mypy 313 errors/40 files（289 source files）、source 54/test 259 errors、make exit2で未合格だった。元logはiss-00413-implementation/lint-p12-0c04677b.logへ保持。旧407 errorsとはsnapshotが異なる。残る旧private writersの整理と現行型問題、full gates、native Windows/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧Worktree試験・writerの退役**

旧Worktree create/bootstrap/remove三filesの20 test関数・433行と、旧二writerの28 symbols・809行を全文確認し、[個別対応](artifacts/test-port-worktree-retirement.md)を保存した。明示NAME/base/path・Git inventory・branch/payload保全・明示makeと出力省略を公開CLIへ対応づけ、control/epoch/registry/receipt/recover/Start以外の共通排他を廃止した。まだ旧callerを持つworktree_target.pyはこのunitで削除しない。退役五filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

新しい公開保証は元選択保持1 passed（0.50秒）、detached base1 passed（0.49秒）、base/path/branch拒否3 passed（0.39秒）、成功hookの大出力省略1 passed（0.26秒）、欠落/non-native target2 passed（0.30秒）。現行Greenのcharacterizationである。欠落pathをexit5とした初期期待はv2のLOCAL_TARGET_NOT_FOUND/exit4へ訂正し、失敗logを保持した。

通常wheelの収録禁止はRed 1 failed（0.78秒）、source削除後の同testはGreen 1 passed（13.87秒）。関連Worktree/native Git観測124 tests（23.14秒）、全Ruff check/format（363 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-worktree-retirement-port.log、pytest-worktree-retirement-source-{red,green}.log、pytest-worktree-retirement-related.logへ保持する。

直近通常lintの313 errors/full gate、残る旧source/private helpers、native OS/別Python、fresh Strict、最終手動確認は未完了である。実consumer/live GitHubは未変更。

**旧Active・branch・Scope deleteの退役**

旧Active/branch/Scope deleteの三test files（28 test関数・815行）と三writer（53 symbols・1400行）を全文確認し、[個別判断](artifacts/test-port-selection-retirement.md)を保存した。dirty/候補graph/他WT占有、metadata/直接record/branch/backup保全を公開CLIへ対応づけた。親自動昇格・from-branch取得・永久binding・local ID tombstone・共通WriterLock・operation journal/recoveryを廃止する。退役六filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

新しい公開保証は既存ref/非ASCII拒否2 passed（0.30秒）、tracked/untracked拒否2 passed（0.49秒）、Scopeを失った候補refの切替拒否1 passed（0.31秒）、tracked subtreeのbackup/元branch/checkout/GH保全1 passed（0.39秒）。既存Greenのcharacterizationである。

通常wheel収録禁止はRed 1 failed（0.80秒）、source退役後の同testはGreen 1 passed（15.49秒）。関連Active/branch/Scope delete/Finish148 tests（34.11秒）、全Ruff check/format（357 files）、変更三test限定mypyとdiff checkも成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-selection-retirement-port.log、pytest-selection-retirement-source-{red,green}.log、pytest-selection-retirement-related.logへ保持。

直近通常lintの313 errorsは別snapshotの未合格記録である。残る旧Source/tests、現行型問題、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**通常型gateと現行試験の型補正**

clean `2c45e885ca48c32616d4899ee79844c553d96dc5` の通常 `make lint` はRuff成功、mypy 189 errors/32 files（276 source files）、make exit2で未合格だった。元logは既存Epic Workbenchの `iss-00413-implementation/lint-p12-2c45e885.log` に保持した。313 errorsは旧snapshotの記録である。

現行のGit診断・Windows外部API fixture・branch adapter・legacy doctor・migrationの五test filesについて29件の型問題を補正した。Git診断のdict形状をassertし、空list/JSON payloadの型、bytes refとtree digestの変数を区別した。migrationの障害注入callbackは実際のbackup/context/OS replaceの引数と返値へ揃え、検証条件と障害時機を保持した。ignore/cast/skip/収集除外を増やさず、製品sourceやconsumer状態は変更しない。

五suiteは108 passed（18.48秒）、全source/tests Ruff check/format（357 files）、変更五test限定mypy `--follow-imports=silent` とdiff checkが成功した。元logは `iss-00413-implementation/pytest-current-test-types.log`。これは既存試験の型補正であり、新機能Red→Green、Windows native、通常full gate、fresh Strictの合格ではない。残る旧実装の個別退役と全体検証を続ける。

**旧dependency writer・試験の退役**

旧七test関数・二helpers（218行）と旧application/dependency_vnext.pyの十symbols（235行）を全文確認し、[個別対応](artifacts/test-port-dependency-retirement.md)を保存した。宣言/継承・循環・未知field/mode・直接record保全・必要対象だけのlive観測を公開CLIへ対応づける。control/epoch・共通WriterLock・旧selection/cache/stale opt-inのadapterを削除し、現行pure domainとraw snapshot helperは維持する。退役二filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

公開確認は三kind×三kind 9 passed（2.02秒）、duplicate add全tree保全1 passed（0.37秒）、cross-tree継承/親完了待ちcycle 2 passed（0.57秒）、子の依存/完了を親と混同しないreadiness 2 passed（0.28秒）。既存Greenのcharacterizationである。

通常wheelの収録禁止はRed 1 failed（0.77秒）、source退役後の同testはGreen 1 passed（14.01秒）。関連dependency/Start/Scope delete/pure domain 188 tests（48.28秒）、全Ruff check/format（355 files）、変更二test限定mypyとdiff checkが成功した。元logは既存Epic Workbenchのiss-00413-implementation/pytest-dependency-retirement-port.log、pytest-dependency-retirement-source-{red,green}.log、pytest-dependency-retirement-related.logへ保持。

直近通常lintの189 errorsはclean 2c45e885の別snapshotである。残る旧source/private helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧Artifact writer・試験の退役**

旧五test関数（111行）と旧application/artifact_vnext.py（152行・六関数/classと一type alias）を全文確認し、[個別対応](artifacts/test-port-artifact-retirement.md)を保存した。mixed catalog、本文非読取、重複slot拒否、六template、既存local/root、metadata/資料/privacy保全を公開CLIへ対応づけ、control/epoch・共通WriterLock・三段旧activeのadapterを削除した。現行artifact_queryと局所publicationは維持する。退役二filesへのsource/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認はmixed catalog本文open 0で1 passed（0.23秒）、root/Scope重複slotと全tree保全2 passed（0.37秒）、既存local Initiativeの六type・metadata/仕様/mode/ref保全6 passed（1.45秒）。既存Greenのcharacterizationである。最初の本文open拒否を試験側digestまで延長したharness失敗1 failed（0.31秒）はCLIのcontextへ限定して訂正し、元logを保持した。

通常wheelの収録禁止はRed 1 failed（0.77秒）、source退役後の同testはGreen 1 passed（14.08秒）。Artifact/Grill finalizer/domain/templateの関連141 tests（8.89秒）、全Ruff check/format（353 files）、変更二test限定mypyとdiff checkが成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-artifact-retirement-port.log、pytest-artifact-retirement-source-{red,green}.log、pytest-artifact-retirement-related.logへ保持。

このunit前のclean 82240b58の通常make lintはRuff成功・mypy 95 errors/26 files（274 source files）、source 47/test 48 errors、make exit2で未合格。元logはiss-00413-implementation/lint-p12-82240b58.log。旧189 errorsとはsnapshotが異なる。残る旧source/tests、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧Scope発行・取り込み・復旧の退役**

旧十九test関数（698行）と旧五source files（1478行・27 symbols）を全文確認し、[個別対応](artifacts/test-port-scope-github-retirement.md)を保存した。GitHub番号、三階層、live open親、明示title/ref、GET-only import、効果と既存資料保全を公開CLIへ対応づける。新規local採番・marker・control/epoch・共通WriterLock・registry/tombstone・永続journal/resumeを除去した。pure github_scope_scaffold/scope_ancestors/scope_scaffoldと既存local codecは維持する。候補外source/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認は階層import 2 passed（1.47秒）、terminal親/祖先のPOST前拒否6 passed（2.49秒）、GET後競合と新しい明示import 1 passed（0.88秒）、確定拒否のfailed/5・一POST・ID未発行3 passed（1.37秒）。既存Greenのcharacterizationである。最初の衝突fixtureを起動前から不正Scope pathにした期待誤り1 failed（0.20秒）は、確認済みGET中の競合を測るよう訂正し、失敗logも保持した。

通常wheelの五旧module収録禁止はRed 1 failed（0.76秒）、source/test退役後の同testはGreen 1 passed（13.82秒）。関連Scope create/import/GitHub gateway五suiteは99 passed（27.76秒）。全Ruff check/format（347 files）、変更三test限定mypyとdiff checkが成功した。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-github-retirement-port.log、pytest-scope-github-retirement-source-{red,green}.log、pytest-scope-github-retirement-related.logに保持する。

95 errorsの通常lintはclean 82240b58の別snapshotであり、現在値としない。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**GitHubの旧マーカー検索の退役**

[個別対応](artifacts/test-port-github-marker-retirement.md)に従い、最後の旧writer退役後にcallerを失ったGithubIssueGateway.find_by_markerと二private試験を削除した。全Issueページ走査/marker検索を現行writerへ移さない。専用array decoder optionを除去し、GET/POST/PATCHの単一Issue object返値を明確にした。repository/record/HTTP分類/完了処理のASTと元の残る13 test関数は同一で、skip/収集除外を増やさない。

array応答のGET/5・create unknown/6・再送なしを旧sourceで先に2 passed（0.03秒）、refactor後の同testも2 passed（0.03秒）で確認した。既存Greenのcharacterization/refactorであり、製品Redではない。POST endpointの初期期待をargv末尾としたfixture誤り1 passed/1 failed（0.04秒）は正しい--method後の位置へ訂正し、失敗logを保持した。関連七suiteは131 passed（40.62秒）、work finishは33 passed（11.93秒）、全Ruff check/format（347 files）・変更source/test限定mypy・diff/AST検査が成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-github-marker-retirement-{before,after,related}.logに保持。

このunit前のclean d7f47fc0の通常make lintはRuff成功・mypy 55 errors/19 files（266 source files）、source 40/test 15 errors、make exit2で未合格。元logはiss-00413-implementation/lint-p12-d7f47fc0.log。旧95 errorsとは別snapshotであり、残る旧helpers、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧migration・共通writer admissionの退役**

旧二test filesの22 test関数・920行と旧五source filesの52 symbols・1505行を全文確認し、[個別対応](artifacts/test-port-migration-retirement.md)を保存した。schema1変換、全WT登録/control/epoch/branch binding/local ID予約、UUID journal/resume/rollbackを廃止した。現schema3 bytes、current一宣言の切替、外部実backup/restore、途中user edit拒否、他WT/Git/旧activeの保全を公開CLIへ対応づける。現domain/writer_admission、migration_backup、legacy_reader、current writerは保持する。候補外source/test importはTYPE_CHECKING/子moduleを含め0。skip/収集除外を増やさない。

追加確認は不正metadata/旧active四casesで4 passed（0.46秒）、scoped Workbenchのopaque metadata/外部link保全で1 passed（0.25秒）。既存Greenのcharacterizationである。通常wheelの旧五module実収録禁止はRed 1 failed（0.82秒）、source/test退役後の同testはGreen 1 passed（14.40秒）。関連migration/doctor/validate/公開adapter四suiteは159 passed（23.91秒）。初回関連suiteの旧filename誤指定はpytest exit4、0 tests（0.00秒）で、実inventory確認後に訂正し元logを保持した。製品Redに数えない。

全Ruff check/format（340 files）、変更二test限定mypyとdiff checkが成功。元logは既存Epic Workbenchのiss-00413-implementation/pytest-migration-retirement-port.log、pytest-migration-retirement-source-{red,green}.log、pytest-migration-retirement-related.logへ保持。55 errorsの通常lintはclean d7f47fc0の別snapshotであり、残る旧helpers、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧control・registry・writer lock helpersの退役**

旧七source filesの1002行・38 top-level symbolsを全文確認し、[対応記録](artifacts/test-port-control-retirement.md)を保存した。絶対／相対／TYPE_CHECKING／子moduleを含む候補外importは0。Git共通領域のcontrol/epoch/engine登録、local採番予約・永久branch binding、operation/handover/finalization journal、全writer lock file／WT lifetime leaseを削除した。current Startだけの排他、直接選択・捕捉token解除、現schema/protocol検査、readonly legacy診断は維持する。旧Git内データと別packageのgroup journalはこのunitで変更しない。

通常wheelの旧七module収録禁止はRed 1 failed（0.90秒）、退役後の同testはGreen 1 passed（16.52秒）。Start/lock options/Doctor/別process競合・kill/migration/static assets七suiteは259 passed（120.89秒）、exit0。全Ruff check/format（333 files）・変更test限定mypy・diff checkが成功。既存test削除0、skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-control-retirement-source-{red,green}.logとpytest-control-retirement-related.logへ保持。残る旧source、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧domain台帳・復旧契約の退役**

旧四source filesの435行・14 top-level symbolsを全文確認し、[対応記録](artifacts/test-port-domain-retirement.md)を保存した。local採番予約、高水位/tombstone/永久branch binding、UUID付き操作計画・epoch/engine/revision固定・intent再送/resumeの型とexecutorを削除した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。既存ID/selector codec、current Git branch検査、今回操作のeffects/partial/unknown、readonly legacy診断は維持する。

通常wheelの旧四module収録禁止はRed 1 failed（0.73秒、exit1）、退役後の同testはGreen 1 passed（15.02秒、exit0）。公開Scope create/import/lifecycle/branch/recovery argument拒否の五suiteは156 passed（47.47秒）、exit0。全Ruff check/format（329 files）・変更test限定mypy・diff checkが成功。既存test削除0、skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-domain-retirement-source-{red,green}.logとpytest-domain-retirement-related.logへ保持。残る旧installation等、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧fixed-source installer・journal・復旧executorの退役**

旧五source filesの1750行・58 symbolsと旧三test filesの1378行・56 test関数を全文確認し、[個別対応](artifacts/test-port-fixed-installer-retirement.md)を保存した。package/相対/TYPE_CHECKING/子moduleを含む候補外importは0。固定GitHub sourceのtag/commit/archive取得、engine candidate照合、group/child UUID journal、recovery area/ignore marker、全root交換とresume/rollbackを削除した。current static manifest/bytes検査、明示一WT、外部実backup/restore、個別file公開・unknown/partial、user仕様/選択/未知file/Git保全は維持する。旧backup子inodeのrollback所有認証と現行root identity/bytes検査を同じ保証と主張しない。

公開CLIにhardlink拒否四case（4 passed、8.10秒）、候補hardlink化（1 passed、2.41秒）、asset/backup same-inode edit（2 passed、4.56秒）、実ZIP package bytes改変拒否（1 passed、0.20秒）を追加した。既存Greenのcharacterizationである。通常wheelの旧五module収録禁止はRed 1 failed（0.80秒、exit1）、退役後の同testはGreen 1 passed（14.77秒、exit0）。関連五suiteは208 passed（97.97秒）、exit0。後から追加したZIP改変一caseは別focused runであり、この208へ加算しない。全Ruff check/format（321 files）・変更二test限定mypy・diff checkが成功。skip/収集除外追加0。元logは既存Epic Workbenchのiss-00413-implementation/pytest-installation-retirement-{port,source-red,source-green,related}.logへ保持。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**公開v2出力と維持する実file試験の型整合**

旧v1出力を固定していた七test関数は、同じ名前のまま公開v2・直接一件のActiveData・operation IDなし・can_resume/can_rollback=falseの案内へ更新した。成功/unknown効果をtop-levelで隠せない検査、stderr、秘密値秘匿、現行CLI補完を保持する。[対応記録](artifacts/test-port-public-output.md)へ記録した。既存local lifecycleはLocalBackendを実際に確認してからstateを検査する。原子的JSONの別process kill試験は保持し、代入するOS callbackのkeyword契約だけを合わせた。production変更0、test削除0、skip追加0。

clean e1397459の通常make lintはRuff成功・mypy 41 errors/16 files（240 source files）、make exit2。限定mypyはMYPYPATH未指定だとsource importを解決せず0と表示したが、MYPYPATH=srcを明示すると対象三filesの3 errorsを再現した。修正後は同条件で0、関連三suite 43 passed（0.13秒）、Ruff check/format・diff checkが成功。最初の型注釈importをfuture annotationsなしで追加したcollection error（0.09秒）はharness修正として別logを保持し、製品Redに数えない。元logsはiss-00413-implementation/lint-p12-e1397459.log、pytest-retained-output-type.log（collection error）、pytest-retained-output-type-2.log（成功）。通常full gate、旧helpers、native OS/別Python、fresh Strictは継続中。実consumer/live GitHubは未変更。

**旧target resolver・補完rendererの退役**

旧二source filesの246行・10 symbolsと旧二test filesの185行・12 test関数を全文確認し、[個別対応](artifacts/test-port-target-resolver-retirement.md)を保存した。候補外importは0。旧三role保存snapshotとregistry ID/aliasを削除し、current tree/direct/guard/native inventory/外部shimのargv/cwdを維持する。補完は公開cli/optionsへ統一する。旧consumer静的資産の退役hash/pathは保持する。

公開project context/完全GH linkageの八caseを退役前に8 passed（0.60秒）、exit0で確認した。診断codeのfixture誤りによる初回3 failed/5 passed（0.62秒）はSCOPE_NOT_FOUNDへ訂正し、製品Redに数えない。通常wheelの旧二module収録禁止はRed 1 failed（0.77秒、exit1）→Green 1 passed（13.53秒、exit0）。関連七suiteは169 passed（18.55秒）、exit0。全Ruff check/format（317 files）、MYPYPATH=srcを明示した変更二test限定mypyとdiff checkが成功した。skip/収集除外追加0、旧helper以外のproduction変更0。元logsはiss-00413-implementation/pytest-resolve-retirement-{before,before-2,source-red,source-green,related}.log。残る旧helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**標準text表示と現行開発手順の整合**

[C-01/C-04の表示不足](artifacts/public-text-output.md)を公開Scope/Activeと診断の三testで再現した（Red 3 failed/21 deselected、0.22秒、exit1）。typed dataを既存の秘匿処理後に表示する修正で同三testがGreen（3 passed/21 deselected、0.22秒、exit0）となり、関連九suite 176 passed（42.57秒）が成功した。JSON v2、既存Sync/依存表示、raw Git stderrは維持し、永続状態や書込を追加しない。

AGENTS.mdの実装path、現在選択の取得、通常wheel、独立consumerでの検証を現構成へ更新した。既存二suite 236 passed（2.37秒）、全source/tests Ruff check/format（317 files）、MYPYPATH=srcの変更三Python file限定mypyとdiff checkが成功した。通常wheel hash 97378c2ab1a8a9d88f23c926a0a2c7b0009b267ca355f19a5b439a552830538bを再照合し、provider外の非editable実consoleで五read-onlyコマンドの表示/JSON/全tree不変を確認した（0.66秒、exit0）。一時fixtureは削除済み。選択recordはtest準備であり、実Start/実dogfood適用ではない。初回確認scriptのcurrent_branch項目名誤りは別logへ保持した。

この変更前のclean 32c372e1で通常全pytestは1878 passed/1 skipped（340.17秒、exit0）。skip理由は元実行で収集していない。通常make lintはRuff成功・mypy 37 errors/12旧source files（236 source files）、make exit2で未合格。旧helpersの退役、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧generation・状態cache・cache付きGit snapshotの退役**

旧三source files（299行・11 symbols）と旧generation三test関数（60行）を全文確認し、[個別対応](artifacts/test-port-generated-state-retirement.md)を保存した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。UUID付き世代/manifest/current pointerの公開・saved OPENの採用・cacheを混ぜる一時Git snapshotを削除した。通常Syncの必要時観測、unknown/partial、直接record、固定HEAD/候補OIDの読取と旧証拠保全を維持する。旧consumerのpath/hash inventoryは変更しない。

旧generation pointerが正常/不正でも旧filesと直接recordを全tree保全し、現在のlocal Syncだけを表示する二caseを退役前に確認した（2 passed/24 deselected、0.49秒、exit0）。既存Greenのcharacterizationである。通常wheelの旧三module収録禁止はRed 1 failed（0.71秒、exit1）→同test Green 1 passed（13.55秒、exit0）。関連Sync/Validate/Doctor/query/Start/wheelの六suiteは231 passed（65.73秒）、exit0。全Ruff check/format（313 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功した。skip/収集除外を増やさない。旧generationのatomic pointer/rollback保証を新しい機能として温存しない。

元logsは既存Epic Workbenchのiss-00413-implementation/pytest-generated-state-retirement-{before,source-red,source-green,related}.logへ保持した。37 errorsの通常lintはclean 32c372e1の別snapshotである。残る旧source/tests、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**旧三段Active保存・投影adapterの退役**

旧infra/active_store.py（645行・29 functions）と旧二test files（1067行・18 test関数）を全文確認し、[個別対応](artifacts/test-port-active-projection-retirement.md)を保存した。候補外importは絶対／相対／TYPE_CHECKING／子moduleを含め0。固定active.jsonへの三段保存、旧manifest自動採用/.work prune、symlink/path/context-pack投影、index/tree patch、全体snapshot/restoreを削除した。直接一件/現存祖先、捕捉tokenだけの解除、legacy資料の安全な観測と保全は維持する。application/set_active等の残る旧graphは別の退役対象であり、このunitで全て削除したとは扱わない。

公開unchangedの四selectorと、旧manifest/projection/cache/不正directory/hardlink保全の二caseは退役前に6 passed/38 deselected（0.53秒）、exit0。通常wheelの旧module収録禁止はRed 1 failed（0.73秒、exit1）→同test Green 1 passed（14.47秒、exit0）。関連Active/record/Finish/native kill/Sync/Doctor/wheel七suiteは185 passed（49.75秒）、exit0。後から追加した現record hardlinkのSet/Clear拒否は別runで2 passed/44 deselected（0.25秒）、exit0であり、この185に加算しない。全Ruff check/format（310 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功した。skip/収集除外を増やさない。

通常make lintはこのunitのPython差分を適用したc93100ba基準でRuff成功・mypy 32 errors/11旧source files（229 source files）、make exit2。37 errorsはclean 32c372e1の旧snapshotである。元logsは既存Epic Workbenchのiss-00413-implementation/pytest-old-active-infra-retirement-{before,source-red,source-green,related}.log、pytest-old-active-infra-hardlink.log、lint-p12-old-active-infra.logへ保持した。残る旧source/tests、full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**Validateの必須Scope文書検査の維持**

旧構造検査を照合し、現行経路が四canonical文書の欠落を見逃す差異を[記録](artifacts/validation-required-documents.md)した。公開CLIのRed 28 failed/2 passed（4.40秒、exit1）を、guarded descriptorで名前/通常fileだけを検査する修正でGreen 30 passed（4.44秒、exit0）にした。固定HEADでもmetadata以外の本文を取得せず、本文・承認・計画レベルをgateにしない。Doctorと明示移行前の構造検査にも接続し、旧validate source/testsはこのunitでは削除しない。

共有fixtureを完全なScope構造に揃えた。通常全pytestの初回は1863 passed/3 failed/1 skipped（355.05秒、exit1）。増えた文書に伴う三削除途中の一覧期待値を修正し、240件移行fixtureと合わせ4 passed、Validate/Scope Delete全二suiteは117 passed（16.52秒、exit0）。限定mypyは変更10 Python filesで成功し、全Ruff（311 files）も成功。通常make lintの旧graph 32 errors/11 filesと、修正後の通常全pytest再実行、native OS/別Python、fresh Strict、最終手動確認は未完了であり、部分成功をfull gate合格にしない。CLI help・配布reference・一行のstatic hashを更新し、実consumer/live GitHubは未変更。

**入力/出力例**: 入力: 既知旧資産、ユーザー改変資産、古いbranchから戻ったshim。出力: 既知差分だけのplan/apply、改変資産は停止、外部consoleは独立動作。

**Red → Green / 検証**: Red: 新installがruntime/controlをconsumerへ置く、更新が別WTへ及ぶ。Green: staticのみ、source/wheel整合、既存code更新でも仕様bytes不変。

**実行コマンド（将来実行）**:

```text
uv run pytest tests/unit/infra/test_provider_distribution.py tests/integration/test_issue413_wheel.py tests/integration/test_issue413_assets.py -q
uv build --wheel
```

**期待結果・完了条件**: 新版skillsとhelpが同じ44 leaf/部分制限を案内する。未導入consumer/dogfoodの更新をこのstepの実績へ含めない。

**対応**: RQ-413-16 ／ AC-413-37。

**失敗時の停止/戻り先**: static ownershipを立証できないfileはD-12へ戻す。名前だけでdirectoryごと削除しない。

## P-12 対応下限Pythonの予備検証

[Python 3.10互換性の記録](artifacts/python-compatibility.md)を保存した。実3.10.15の隔離venvとprovider import元を照合し、全pytestの初回1864 passed/2 failed/1 skipped（380.34秒、exit1）を切り分けた。spawn時に確認用runnerがpytestを再実行する不具合と、Path.statのaccessor差によるLinux模擬の不達を修正した。製品source、既存assertions、kill境界、test選択とskip条件は維持する。runnerだけの修正後も一件のfixture失敗が再現したことを別logへ保持し、製品Redと区別した。

修正後、3.10の関連二suiteは56 passed/1 skipped（0.30秒）、既定3.12の同suiteは56 passed/1 skipped（0.21秒）、実3.10の通常全pytestは1866 passed/1 skipped（365.74秒）、全てexit0。skipは既存Linux O_TMPFILE capability testでありDarwinでのnative成功ではない。全Ruff（311 files）、MYPYPATH=srcの変更test限定mypyとdiff checkが成功した。P-12中の予備検証であり、残る旧source/tests、実Linux/Python3.11、Windows native、通常full lint、fresh Strict、最終手動確認は継続中。実consumer/live GitHubは未変更。

## P-12 旧JSON transaction writerの退役

旧json_store.py全345行・16 functionsと旧八test（157行）を全文確認し、[個別対応](artifacts/test-port-json-journal-retirement.md)を保存した。guarded reader/物理directory/native no-replaceと基本JSON I/Oは残し、UUID付きintent/stage/done、exchange後復元、reconcileを退役した。旧六関数を削除し、flag切替helperを現行no-replaceへ統合した。候補外import/attribute参照は0。現行のbytes/identity再検査、一file置換、unknown/partialを維持し、任意writerの原子的CASや旧bytes常設保存と同じ保証を主張しない。旧consumerの証拠/path/hashは変更しない。

削除前の後継九casesは9 passed（0.20秒）、既存Greenのcharacterizationである。通常wheelの旧writer収録禁止はRed 1 failed（0.73秒）→Green 1 passed（13.49秒）。関連九suiteは236 passed（79.68秒）、実Python 3.10.15の後継/native record kill/store三suiteは23 passed（4.14秒）、全てexit0。全Ruff（311 files）、MYPYPATH=srcの変更三Python files限定mypyとdiff checkが成功した。初回のregex/OS callback型の二指摘はfixtureの実契約へ修正し、ignore/cast/skip/収集除外を増やさない。

通常make lintは今回Python差分適用後にRuff成功・mypy 32 errors/11旧source files（230 source files）、make exit2。先行3.10全件成功は別候補であり、残る旧source/tests、今回の全件/native Linux/Python3.11/Windows、fresh Strict、最終手動確認は継続中。元logsはiss-00413-implementation/pytest-direct-json-retirement-{port,source-red,source-green,related,python310}.log、direct-json-test-typing.log、lint-direct-json-retirement.logへ保持。実consumer/live GitHubは未変更。

**実Linux / Python 3.11の予備検証**

[環境とfixture補正](artifacts/linux-python311-verification.md)を記録した。clean bdf44fe2のDocker Linux/Python 3.11.16全件は1844 passed/7 failed/17 skipped（870.24秒、exit1）。Artifact六casesのUSER未設定依存と、root capabilityがStart試験のnative書込み拒否を迂回する条件を切り分けた。capabilityだけを外した再実行は6 failed/1 passed（5.56秒）で、両原因を混同しない。試験のUSERを明示し、作成者文字列もassertした補正候補のLinux七casesは7 passed（5.53秒）、macOSのArtifact/Start全二suiteは139 passed（40.56秒）、全てexit0。全Ruff（311 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功した。製品挙動・元のnative拒否・skip条件は維持し、full Linux再合格と通常full lint、Windows、fresh Strict、最終手動確認は別途継続する。

**旧Workbench / Worktree helper群の退役**

旧application三files・1366行/54 symbolsと旧unit testの416行/13関数を全文・[個別判断](artifacts/test-port-workbench-helper-retirement.md)で確認し、外部production参照0の閉じた群を退役した。両WTの別slug、trim/大文字、真正の既存local ID、両側の不正metadata、missing/regular-file Workbench root、三階層のリンク差替えと外部metadata非読取を公開main/native Gitへ移す。無関係なmetadata linkの一律拒否・旧private結果型・登録ID/独自採番/Worktree flockは同等保証として温存しない。共有infraと別callerの残る旧rendererは保持する。

後継十八casesは18 passed（3.90秒）、root file二casesは2 passed（0.48秒）。wheel収録禁止はRed 1 failed（0.75秒）→Green 1 passed（12.86秒）。関連九suiteは245 passed（37.68秒）、実Python 3.10.15の新二十casesは20 passed（4.35秒）、全てexit0。初回collection/spy fixtureの失敗は元logsを保全し、製品Redとは区別した。全Ruff（307 files）、MYPYPATH=srcの変更二files限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 30 errors/10旧files（226 filesを検査）、make exit2で未合格。残る旧source、Linux全件再検証、Windows、fresh Strict、最終手動確認を続ける。実consumer/live GitHubは未変更。

**旧Artifact composition adapterの退役**

未使用infra/artifact_ports.py全57行・四symbolsを全文確認し、候補外参照0をAST/文字列検索で確認して退役した。[対応記録](artifacts/test-port-artifact-adapter-retirement.md)に各wrapperの理由を保存する。現行Artifactと別callerのあるbinary publisher、その試験、旧静的inventoryのpath/hashは保持する。test削除・skip/型ignore/収集除外追加0。

wheel禁止のRed 1 failed（0.83秒）→Green 1 passed（17.35秒）、関連三suite 105 passed/1 skipped（10.89秒）、全て期待したexitとなった。skipは既存Linux O_TMPFILE試験でDarwinでは未実施。全Ruff（306 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功。Linux全件は別候補c4c26bdbで実行中、通常full lint・残る旧source・Windows・fresh Strict・最終手動確認は未完了。実consumer/live GitHubは未変更。

**旧Delete use caseとprivate resolver testの退役**

通常production参照0の旧Delete全1437行/42 symbolsと旧opacity test全44行/一関数を全文確認し、[個別判断](artifacts/test-port-delete-helper-retirement.md)に基づき退役した。公開CLIの三階層/.workbench・near-name/現存・ghost target十二casesへprivate metadata非読取・保全を移す。旧一般walkの列挙順、三段Active restore、GitHub自動Close、自動SyncはC-05/D-03の決定に従い残さない。退役後AST参照0、旧inventory path/hashと現在のDelete安全性suiteは保持する。

後継は削除前12 passed/37 deselected（2.22秒）。wheel禁止のRed 1 failed（0.77秒）→Green 1 passed（16.35秒）、関連三suite 56 passed（9.56秒）、実Python 3.10.15の後継12 passed/37 deselected（1.91秒）、全て期待したexitとなった。初回関連runの誤test path/no tests ranは別logへ保持した。全Ruff（304 files）、MYPYPATH=srcの変更二files限定mypy、diff checkが成功。通常make lintはRuff成功・mypy 30 errors/10旧files（223 files）、make exit2。Linux全件の別候補に残る失敗、残り旧source、Windows、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。

**Linux全件の二回目とnative bootstrap fixture**

clean c4c26bdbの実Linux/Python 3.11.16全件は1839 passed/1 failed/17 skipped（921.27秒、exit1）。残る失敗はmake起動前のGit rev-parseが100msでtimeoutしたもので、同じSHAの単独再実行は1 passed（0.74秒）。[環境と切分け記録](artifacts/linux-python311-verification.md)へ結果を追記した。testの有限timeoutを2.0秒へ修正し、sleep5に対する実timeout・native process-group終了と応答OSError、unknown効果の元assertionsを維持する。製品挙動/test選択/skip条件は変更しない。

補正候補はLinux bootstrap全suite 32 passed（20.48秒）、macOSの同suite 32 passed（7.82秒）、全てexit0。Linux base/test hash・変更一file・実効capability0とprovider/prefix、主checkoutとの関連production bytes一致を照合した。全Ruff（304 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功。現在の全件再合格、通常full lint、残る旧source、Windows、fresh Strict、最終手動確認は別途継続する。実consumer/live GitHubは未変更。

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
