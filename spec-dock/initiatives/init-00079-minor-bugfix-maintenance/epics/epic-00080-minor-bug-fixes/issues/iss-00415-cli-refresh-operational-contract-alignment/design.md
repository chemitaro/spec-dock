---
種別: 設計書（Issue）
ID: "iss-00415"
タイトル: "共通CLI刷新後の操作案内・補完契約の整合"
関連GitHub: ["#415"]
状態: "実装承認済み"
最終更新: "2026-10-06"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00415 共通CLI刷新後の操作案内・補完契約の整合 — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)。成果と受入条件は[Requirement](requirement.md)、順序・実行条件・試験は[Plan](plan.md)を参照します。

> 2026-10-06、ユーザーが本書と実装計画に沿う実装・完了を承認しました。仕様策定時点では各実装・適用は未実施でした。現在の実施状態と実測は[Plan](plan.md)と[Report](report.md)を参照します。仕様採用だけを実装・実環境適用・Issue完了の証拠にはしません。

## 設計目標

既存の受付・保全・配布契約を正本として、利用者に提示する操作契約だけを整合させます。SD-OPS-001は診断文言、002〜005は限定した現行文書、006は補完の候補集合、007はrepository descriptionの運用変更として、それぞれの所有面で修正します。

同じ成果に束ねますが、一つの巨大なhandlerや新しい運用frameworkへ統合しません。通常CLI、provider資産、consumer投影、GitHub metadataの更新単位は分けます。schema変更、認証変更、global skill、旧実装の一括撤去は不要です。

### 基準と参照規約

基準は`chemitaro/spec-dock`／`codex/iss-00415-cli-refresh-specs`／`95ec39b751054bf48098215fc077fe7b8f533f62`です。本依頼でGitHub connectorのbranch-tipを新しく照会し完全一致を確認した後、ファイルをこのSHAに固定して確認しました。`repo-root:`はrepository rootからのpathを意味します。以下の行番号はこの基準のものです。

根拠となる二つのArtifactは[ローカル照合結果](artifacts/20261006t035502z--verified-report.md)と[外部分析原文](artifacts/20261006t035503z--chatgpt-report.md)です。sourceとテストの再読で具体化しますが、本書の作成を新たなpytest／実consoleの実行証拠にはしません。

## Current / Target

| ID | Current：確認した根拠 | Target：限定する変更 |
|---|---|---|
| SD-OPS-001 | `repo-root: src/spec_dock/runtime/infra/fs_repo.py:338–365`の`ensure_no_legacy_meta_json()`がrenameを一律案内します。`repo-root: src/spec_dock/runtime/application/direct_scope_publish.py:126`から同readerを利用します | 検出・例外型・呼出順を維持し、保全、既存`.meta.json`確認、比較、手動判断の案内へ変更します |
| SD-OPS-002 | `repo-root: README.md:21–23`のJSON作成例にyesがありません。`repo-root: src/spec_dock/runtime/application/direct_scope_publish.py:56–72`は非対話の未確認作成を拒否します | 三つの作成例に`--yes`を補い、承認と返却IDの扱いを明示します |
| SD-OPS-003 | `repo-root: src/spec_dock/assets/spec_dock/docs/reference_cli.md:3`と`repo-root: docs/github-issue-integration.md:3,7,13`が現行selector・入口と不整合です | 文法の用途別表、裸番号のrepo指定、通常installed package、既存local互換の説明へ直します |
| SD-OPS-004 | `repo-root: docs/sync-aggregation.md:1–13`に保存再生成、cache、journalの旧説明があります | 観測、local/github、unknown／partial、現在の参照先に限定した短い入口にします |
| SD-OPS-005 | `repo-root: AGENTS.md:10`に0805だけの適用・merge pendingという過去状態があります | 現行の不変な操作規則と日時付き原本参照を分けます。mergeと環境適用を分けます |
| SD-OPS-006 | `repo-root: src/spec_dock/runtime/cli/options.py:257–269`が全共通optionを補完へ追加します。同file:458–463のparser制限と不一致です | leafの受付分類から候補だけを絞ります。三shellに同じ判断結果を使います |
| SD-OPS-007 | 2026-10-06のconnectorによる`GET /repos/chemitaro/spec-dock`で、descriptionがuvx／`.spec-dock/`／runtime不要の旧説明でした | descriptionのみ、採用文字列へ後続更新します。独立したGETで確認するまでは未達です |

PR #414のmetadataは`merged=true`、merge commitは`0e7dc86841cb48d011270a1a2165cb6406ac0cea`、merge日時は2026-10-04T03:33:19Zです。このmerge commitは基準SHAの親として返されています。これは他branchの現在tipを照会した結果でも、利用者の全環境移行を確認した結果でもありません。

### 親契約との整合

[親Epic](../../requirement.md)と[親Initiative](../../../../requirement.md)の保守目的、provider-first、責務・証拠の分離を維持します。親の旧active set取得・`.agent/index.json`・生成projection更新は、本IssueのInterfaceや受入点にしません。親文書を新CLIの実装に合わせて一括改稿する作業は含めません。

## 責務・Interface

### 所有境界

| 面 | 所有するもの | このIssueで行わないこと |
|---|---|---|
| 公開CLI／runtime | 検出後の診断、parserの既存受付、補完生成 | schema、leaf、writer、GitHub番号発行、状態格納の変更 |
| provider資産 | 配布される現在版のCLI参照文書とinventory | consumerを正本として先に書き換えること |
| root文書 | README、GitHub連携、Sync、AGENTS | Issue413や過去Artifactの原文改変 |
| consumer静的投影 | 明示された一つのworktreeの既知資産 | 他worktree更新、metadata／direct recordの手編集 |
| 外部package | 実際に実行される通常installed CLI | worktree内runtimeコピー、旧fixed engineへのfallback |
| GitHub metadata | このrepositoryのdescription | homepage、topics、認証、権限、その他設定 |

<a id="d-415-001"></a>
### D-415-001 legacy診断は文言の変更に閉じる

対応: [RQ-415-001](requirement.md#rq-415-001)。公開create/importの経路は次のとおりです。

```text
spec_dock.cli.main
  → runtime.commands.runtime_dispatch.dispatch
  → direct_scope_publish.create_scope / import_scope
  → _publish_scope
      writer／確認／現行Scope読取／target／repo／pathの事前検査
      → fs_repo.load_node_records
          → ensure_no_legacy_meta_json
              legacy検出 → RuntimeError
      （この先の祖先GitHub観測・Issue作成／取込・scaffold公開へ進まない）
  → 現在の失敗envelope／textを返す
```

`load_scope_views()`はlegacy readerより先に現行metadataを検査します。したがってnegative fixtureは、妥当なschema3 `.meta.json`と別の`meta.json`を同居させます。現行metadataを欠落させて先行検査を失敗させるだけでは、本件の診断を検証したことになりません。

変更するのは`ensure_no_legacy_meta_json()`の説明文です。`_find_legacy_meta_paths()`、探索範囲、`RuntimeError`、呼出位置を保持します。現行dispatcherの`LOCAL_IO_FAILED`／exit 5という分類と、JSONの`status=failed`／`effects=[]`を変更しません。本Issueで新しいerror codeや例外階層を追加する必要はありません。

文言候補は次です。パス列挙は現在の検出結果を使い、metadata本文を出力しません。

```text
Unsupported legacy meta.json detected. Preserve the legacy files before making changes. Check whether .meta.json already exists in the same directory; if present, preserve both files and compare their contents. Decide the authoritative metadata and recovery steps manually. Do not blindly rename, overwrite, or delete either file; renaming alone does not validate or migrate its schema.
```

同居をCLIが自動解消する、backupをCLIが新たに作る、file内容を自動mergeする、legacyを無視して実行継続する変更はしません。案内は次の手作業を安全に判断するためのものです。保全ができない場合は操作を止めたままにします。`mv`や削除コマンドを復旧の一般例として出しません。

同じhelperのunit testだけでは不十分です。既存fixtureを使う公開create/importの試験で、guardまでの到達、正しい診断、両file・Git・成果物不変、remote呼出し・local公開なしを同時に観測します。旧文言のassertionだけを新文言へ置換して、失敗の安全性検査を削ることは禁止します。

<a id="d-415-002"></a>
### D-415-002 READMEは承認済みJSON作成例として成立させる

対応: [RQ-415-002](requirement.md#rq-415-002)。変更対象は`repo-root: README.md`の三つの作成例と必要最小限の前置きです。例示番号は実際の返却IDへ置き換えることを維持します。

```sh
spec-dock scope create initiative --backend github --title "Platform" --yes --json
spec-dock scope create epic --backend github --parent init-00123 --title "Authentication" --yes --json
spec-dock scope create issue --backend github --parent epic-00124 --title "Refresh tokens" --yes --json
```

`--yes`は依頼または承認済み計画の範囲内で作成する例に付けます。CLI確認の省略と、業務上の認可・安全検査を分けます。読取りコマンド、Sync、全shell例へ無条件にyesを挿入しません。現行の`CONFIRMATION_REQUIRED` guardやTTY確認方式は変更しません。

文書テストは実際の掲載例からargvを抽出し、fixtureの返却IDを親へ渡します。三つのコマンドをテスト側に別コピーするだけでREADMEとの乖離を見逃す構成は避けます。`parse_vnext()`の成功だけではなく、非対話createの公開handlerを通す点が既存help例テストに対する追加境界です。

<a id="d-415-003"></a>
### D-415-003 文法は用途別に説明し、実装を広げない

対応: [RQ-415-003](requirement.md#rq-415-003)。文法の実装正本は`repo-root: src/spec_dock/runtime/domain/selectors.py`の`parse_scope_selector()`と`parse_github_ref()`です。

| 文書surface | 具体的な内容 |
|---|---|
| provider `docs/reference_cli.md`冒頭 | 通常TARGETは完全Scope ID・完全gh ref・許可された動的selectorです。import用REFとは別の表にします |
| root `docs/github-issue-integration.md` | 外部installed packageを入口とします。裸番号import例に`--github-repo OWNER/REPO`を追加します |
| 同文書のlocal説明 | 既存local backendの読取り・lifecycle等の保全互換を示し、新規`--backend local`の作成案内にしません |
| 現行参照へのリンク | 既存のprovider CLI／GitHub参照を維持し、相対pathが実在することを検査します |

root文書のimport例は、例えば次の構造へ直します。`OWNER/REPO`は操作対象repositoryへ明示的に置き換え、parent IDも実在する値を使います。

```sh
spec-dock scope import github epic 124 --github-repo OWNER/REPO --parent init-00123 --title "Authentication"
```

通常selectorへURL・裸番号を追加しません。既存のID正規化、旧local綴りの既存ID、repo名の正規化、完全URL、hint矛盾、別repository拒否、動的selectorの状態条件を維持します。importがGETのみでremote Issueを作らないことと、local scaffoldを公開する変更操作であることを分けます。

文法としての受付と、対象不存在・選択不正等の業務拒否を混同しない説明にします。通常のinvalid selector／hint不足の公開経路は適切なproject fixtureで検査します。全てをparser exit 2と決め打ちしません。

<a id="d-415-004"></a>
### D-415-004 root Sync文書は現在の観測への入口にする

対応: [RQ-415-004](requirement.md#rq-415-004)。`repo-root: docs/sync-aggregation.md`のタイトル、冒頭、例、doctor説明を現在の契約へ直します。新しい詳細仕様を重複作成せず、providerの`reference_sync.md`と`reference_cli.md`への既存参照を利用します。

現行例は`workspace sync --source local`と`workspace sync --source github`を区別します。localではGitHub lifecycleを未観測として扱い、githubは今回の明示的な観測です。SyncのJSON観測dataを保存cache、世代、index/tree再生成に読み替えません。read-onlyのvalidateと、自動修復しないdoctorも役割を分けます。

旧journalは歴史・raw legacy診断の対象として必要な場合だけ言及し、現在のoperation管理や再開手段として説明しません。`--source cache`は現行実行例から除きますが、退役入力を拒否するruntimeは残します。旧projectionが残っていてもSyncが上書きしない既存テストを維持します。

<a id="d-415-005"></a>
### D-415-005 AGENTSは不変の運用規則と履歴参照を分ける

対応: [RQ-415-005](requirement.md#rq-415-005)。`repo-root: AGENTS.md`のOperating入口は、外部console、薄いshim、現在help、scope内の操作、fail-closedという現在の規則を維持します。その規則と一体化している0805のみ適用済み・merge pendingの当時の状態を分離します。

置換する段落は、少なくとも次の三点を区別して説明します。

- 外部installed `spec-dock`またはPATHへ委譲する薄いshimを使い、旧repository-local runtimeをfallbackにしないことです。
- Issue 413の2026-10-03引継ぎ記録は当時の観測です。PR #414は2026-10-04にmergeされましたが、mergeは各tool環境・worktreeへの適用確認ではありません。
- package更新、対象一つのstatic更新、直接対象の観測を個別に確認し、他環境・正式Issue413 Start・公開を推測で完了にしないことです。

履歴参照先は既存の[Issue413 Requirement](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/requirement.md)の日時付きrollout節と[実装記録](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/implementation-report.md)です。AGENTSへ採用するときはroot文書からの相対pathへ合わせます。これらの原本を新しい現状に合わせて書き換えません。

現在の許可境界、human merge gate、provider/consumer責務を削りません。親文書の古いactive/index記述を、この修正に便乗して全て変更することもしません。テストは現在段落の意味と履歴参照の実在を確認し、履歴原本の旧語を全面禁止するgrepにはしません。

<a id="d-415-006"></a>
### D-415-006 補完は既存分類に基づく純粋な候補選別にする

対応: [RQ-415-006](requirement.md#rq-415-006)。公開catalogの`LEAF_PATHS`、`LEAF_ARGUMENTS`、`MUTATING_LEAF_PATHS`を再利用します。以下は補完候補の規則であり、parserの新しい受付規則ではありません。

| leaf分類 | `--yes`／`-y` | `--lock-timeout` | その他 |
|---|---|---|---|
| `work start` | 提示します | 提示します | 現在の共通optionとleaf固有optionを維持します |
| `MUTATING_LEAF_PATHS`に含まれるStart以外 | 提示します | 提示しません | 同上です |
| それ以外のleaf | 提示しません | 提示しません | その他の現行候補を維持します |

`active set`は現行catalog上MUTATINGに含まれます。同一対象へのunchangedしか成立しない場合があることを理由に、今回readへ再分類しません。importはremote GETのみでもlocal公開を行うので、同様に現行分類を守ります。

修正場所は`repo-root: src/spec_dock/runtime/cli/options.py::completion_script()`が共通候補をleafへ追加する箇所です。必要なら同module内に小さな純粋helperを置けますが、その名前・存在を既存APIと偽りません。候補の重複排除・順序を保持し、一つの候補mapをBash／Zsh／Fishの出力へ渡します。既存のshell出力形式は原則維持します。native検査で正候補が出ない場合は、当該候補をshellへ伝える符号化・登録処理に限り最小修正し、parserや別機能の変更へ広げません。この条件は追加の不具合が既に確認済みという意味ではありません。

**候補を絞るために`_COMMON_VALUES`自体を削らないことが重要です。** この定義はparserだけでなく、command pathより前の共通option値をskipする処理にも使われます。候補選別と、既存入力を文脈として読む処理を混同すると、位置自由度や値の処理が壊れます。

44 leaf、short alias、共通optionの前・中・後の位置、`--key=value`、空白を含む値、Scope operand後の候補、必要値の入力中、既存`--`境界のテストを維持します。動的なGitHub番号候補、filesystem探索、agent provider判定等を追加しません。無効な手入力は現在のparserが拒否するままです。

三shellの生成文字列を点検するだけでなく、公開CLIが返したscriptを隔離した実shellで読み込んだ候補を検査します。既存native harnessはBash/Zsh中心なので、Fishのnative検査を追加境界とします。Fishでは公式の`complete -C STRING`で補完を評価でき、コマンド本体を実行する必要はありません。新たなFish常駐サービスや製品依存は追加しません。

<a id="d-415-007"></a>
### D-415-007 Aboutはdescriptionだけの独立した外部変更にする

対応: [RQ-415-007](requirement.md#rq-415-007)。採用候補は次の一つです。これは候補文字列であり、設定済みという表示ではありません。

> GitHub Issueに紐づく仕様・依存・成果物とworktreeごとの作業対象を管理する外部インストール型Python CLI。Linux/macOS・Python 3.10+に対応し、指定projectへ文書・template・project-local skill・薄いshimを静的配置します。

操作対象は`chemitaro/spec-dock`の`description`だけです。後続実施では、正規のconnector操作または許可されたGitHub CLIの`PATCH /repos/chemitaro/spec-dock`に、descriptionだけを送信します。利用する認証で実際に書けるかは実施前に確認し、metadataの読取成功や一般的なrepository権限表示だけで保証しません。

| 状態 | 保存する証拠 | 受入判定 |
|---|---|---|
| 未実施 | 候補、保留理由、実施担当・必要な確認 | 未達です |
| 送信前に停止 | 読取結果、認可／入力／権限等の不成立 | 未達です。設定変更済みとしません |
| 送信後に応答不明 | 正確な対象・送信文字列・時刻・取得できた結果 | 確認不能です。「未送信」と断定しません |
| PATCH成功、read-back未確認 | PATCH結果と未確認理由 | 未達です |
| live read-back一致 | 独立したGETの`full_name`と`description`、確認時刻、exit、前後比較 | この観測時点のAbout整合を確認済みとします |
| 他者変更／不一致 | 観測した現在値と候補の差 | 競合として停止します。自動再送・自動巻戻しはしません |

実施直前のdescriptionが既に採用候補と一致している場合、PATCHを省略してlive read-backと「変更なし」を記録できます。今回の作業が変更したと主張せず、現在状態を確認した証拠として扱います。homepage/topics等の前後値に差があれば、本操作の送信内容と第三者の同時変更を分け、勝手に戻しません。

GitHubの更新APIを原子的なcompare-and-swapと仮定しません。直前の再読と短い操作範囲で競合リスクを減らしますが、同時編集を完全に封鎖した保証は付けません。rollbackは後述の対象限定・別許可の復元です。

<a id="d-415-008"></a>
### D-415-008 配布と適用は既存のinventory・保全経路を使う

対応: [RQ-415-008](requirement.md#rq-415-008)。確定したprovider文書変更は`repo-root: src/spec_dock/assets/spec_dock/docs/reference_cli.md`です。root README・AGENTS・`docs/`はそのままconsumerへコピーされるinventory資産とは扱いません。READMEはpackage metadataのreadmeでもあるため、wheel検査の対象に含めます。

基準inventoryの該当entryは次の値です。

| field | 基準値・将来の更新規則 |
|---|---|
| `path` | `spec-dock/docs/reference_cli.md`。変更しません |
| `source` | `spec_dock/docs/reference_cli.md`。変更しません |
| `sha256` | `1ee708029bae2fa92eb2c2bd9fe79e9885fc11815b535bf8e1be344b6d3689dc`。改稿後の正確なUTF-8 bytesから新値を計算します |
| `known_old_sha256[0]` | `e7dee1bbf7502528e59ba88d755afe6b23d4b6d0e7da4c6c3419140a031eba32`。保持します |
| `known_old_sha256[1]` | `d7e94faafdff0c1ab9f0b765ad7b7cfb421fcb7920170c67ee9c9ae8e2a7f1c5`。保持します |
| 追加する既知旧hash | 上記の変更前current hashです。基準Git blobのbytesに由来することを確認し、重複させません |
| `mode`／`init_only` | `420`（0644）／`false`を維持します |
| 変更しない集合 | 他entryのpath/source/mode/init_only、既存retired集合、skill・template・system・shim・workspace宣言です |

新しいcurrent hashは将来の実装bytesで決まるため、今回の仕様ファイルのhashや架空値を代入しません。unknown改変を便宜的にknown-oldへ追加してupdateを通すことは禁止します。追加の配布文書修正が本件に不可欠と分かった場合だけ、理由・path・旧bytes根拠を明記して同じ扱いにします。

検証は、provider bytes → wheel内resource → 外部非editable installed resource → fresh consumerの実file、という四点を照合します。source importだけを使う試験と、実consoleで副作用を観測する配布試験を分けます。sdist経由の既存配布検査、hidden assets、runtime一重化も維持します。

既存consumerの更新は`installation update`を使い、対象rootを明示します。このcommandは全current／retired inventoryを評価するので、実環境によっては本件以外の旧runtime退役や欠落資産作成が計画されます。dry-runの`planned_paths`、`planned_retired_paths`、effectsが今回許可された差分を超える場合は適用を停止します。存在しないpath選択flagを発明したり、余分な効果を無言で実行したりしません。必要な別の整理は別許可・別判断へ返します。

外部package更新は利用者のtool環境に作用し、static更新は指定worktreeに作用します。candidate隔離環境への導入を、ユーザー共通package更新の代用実績にはしません。旧writer移行、package公開、他worktree更新はこのIssueに含めません。

<a id="d-415-009"></a>
### D-415-009 証拠は現在候補へ結び付け、Reportと履歴を分ける

対応: [RQ-415-009](requirement.md#rq-415-009)。既存の通常`make lint`／`uv run pytest`を維持します。対象回帰は高速な局所確認として追加しますが、全件の代用にしません。shell不足・OS未確認・既存失敗・新規Red・成功・skipを分けて記録します。

実装者は既存の[report.md](report.md)へ、Outcome／Verification／Residual Risksに相当する実結果の要約と、実在する証拠への参照を残します。長い生ログは認可された作業場所で保全し、Artifact化した場合はCLIが返した実在pathを用います。本書は将来のArtifact名を依存先として作りません。

Issue413のpack、実装記録、既存review、二つの調査Artifactは保全対象です。本Issueの新しい結果を過去原本に混ぜません。親Planの古い試験制度、過去のモデル指定、別Issueのレビュー工程を、自動的にIssue415の新しい必須制度へ転記しません。

## data / failure

### 保存するものと保存しないもの

新しい製品データモデル、schema、event、journal、中央ledgerはありません。通常のsource/doc差分とinventoryの内容hash、既存installerの外部backup、実施結果の証拠だけを扱います。Planning Levelをmetadataや実行権限へ複製しません。

| 失敗点 | 維持・保全するもの | 回復の境界 |
|---|---|---|
| legacy診断 | 両metadata、Git、直接記録、成果物を無変更で残します | 人が保全・比較して扱いを決めます。CLI自動修復はしません |
| docs／補完のnegative test失敗 | fixture、実argv、stdout/stderr、exitを記録します | 対象修正へ戻ります。parserの条件を緩めてGreenにしません |
| wheel／resource hash不一致 | 候補source識別、wheel、実hashと失敗結果を残します | 利用者環境へ適用せず、provider／inventory／build入力を確認します |
| static unknown／危険path／backup不備 | 元consumerと既存の保全物を残します | manual mergeまたは適用条件の調査です。hash登録・symlink迂回は禁止です |
| static partial | backup、適用済み／不明／未実行のpath、残存candidateを残します | 現物を再読し、必要な差分だけを別の明示操作で回復します |
| About不明／競合 | 変更前・送信値・現在値・時刻を分けて残します | GETによる観測を先行します。API再送や巻戻しを自動化しません |

診断・証拠へmetadata本文、tokens、認証ヘッダ、環境変数全体を転載しません。実argvは秘密を含まない形にし、秘密部分がある場合は明示的に最小秘匿します。permission不足を理由に認証設定やrepository権限を変更する作業は含みません。

## 変更対象

| 区分 | `repo-root:`からのpath | 扱い |
|---|---|---|
| runtimeの最小修正 | `src/spec_dock/runtime/infra/fs_repo.py`、`src/spec_dock/runtime/cli/options.py` | legacy文言と補完の候補選別だけです |
| root現行文書 | `README.md`、`AGENTS.md`、`docs/github-issue-integration.md`、`docs/sync-aggregation.md` | 七件に直接対応する範囲です |
| provider配布文書 | `src/spec_dock/assets/spec_dock/docs/reference_cli.md` | 通常TARGETとimport refの説明です |
| 配布inventory | `src/spec_dock/assets/static-inventory.json` | 該当current／known-old hashの更新です |
| consumer投影 | `spec-dock/docs/reference_cli.md` | 許可された対象worktreeへのCLIによる明示適用で更新します |
| 既存テスト | 次節の正確なpath | 既存保証を保ち、本Issueの追加境界を拡充します |
| commit外 | GitHub `chemitaro/spec-dock`のdescription | 独立した後続の運用変更です |

`selectors.py`、`direct_scope_publish.py`、`runtime_dispatch.py`、`catalog.py`、static installerは主に参照・回帰確認対象です。本設計では受付・副作用・保存の変更を要求しません。調査したから変更対象である、とは扱いません。

## 移行・互換性・rollback

**データmigrationはN/Aです。** 本IssueではScope schema、workspace writer protocol、ID、linkage、active記録を変更しないためです。一方で、配布文書と外部packageの更新・復元は対象です。migration不要をstatic更新の検証不要と読み替えません。

| 更新面 | 戻せる条件と方法 | 戻さないもの |
|---|---|---|
| source／root文書 | 後続編集を確認して、本Issueの差分だけをレビュー可能な逆変更にします | `git reset --hard`、`git clean`、履歴packの改変を一般手順にしません |
| 外部package | 更新前の実package／wheel識別を保全し、新writerと互換な既知版へ正規のtool操作で戻します。PATH上の実consoleを再確認します | 旧fixed engine、checkout-local runtime、writer宣言の逆変換は復元しません |
| consumer静的資産 | backupのbytes/modeを独立場所へ復元・比較した上で、現在fileに後続編集がないことを確認し、承認された対象差分だけ復元します | 仕様、Artifact、Workbench、直接記録、他worktreeを上書きしません |
| About | 更新後の現在値が自分の設定した候補と一致し、復元が許可された場合だけ、保全した旧descriptionへ戻して再GETします | 他者の新しいdescriptionやhomepage/topics等を巻き戻しません |

古いpackageのinventoryが新しいstatic bytesをunknownと分類する可能性があります。packageのdowngradeとstatic復元は自動的に対称ではありません。旧CLIのupdateを強行せず、backupと現在bytesの比較による限定復元か、修正版へのforward recoveryを選びます。判定不能なら保全したまま停止します。

## testability

以下は既存ファイルと既存検査の再利用先です。「追加境界」はこれから実装する検査であり、現時点でその検査が存在・合格しているとは主張しません。具体的なargv、fixture、順序は[Planの検証](plan.md#verification)で定義します。

| 既存test path（repo rootから） | 確認できる既存の検査・用途 | 本Issueの追加境界 |
|---|---|---|
| `tests/cli_runtime/test_issue413_scope_publish.py` | `publication_fixture`、公開create/import、事前guard、remote/local効果の区別です | 妥当な`.meta.json`と旧`meta.json`の同居、text/JSON・apply/dry-run、診断と無副作用です |
| `tests/cli_runtime/test_issue413_scope_import.py` | exact ref／URL／hint付き番号、GET-only、親・metadata保全です | 文書の裸番号＋repo例との結合、hint不足・矛盾の対照です |
| `tests/integration/test_cli_docs_vnext.py` | 配布CLI参照の44 leaf、旧rootコマンド検出、現行入口リンクです | README実例の非対話成立、root GitHub／Sync／AGENTSの限定した意味と実在リンクです |
| `tests/cli_runtime/test_help_completion_vnext.py` | public help、生成script、Bash/Zsh nativeのoption位置・operand・値の処理です | 全leafのyes/lock適用表、同義`-y`、Fish native、三shellの正負候補です |
| `tests/cli_runtime/test_cli_vnext_contract.py` | 既存parser/catalogの回帰先です | 受付を変更していないことと、補完の期待との照合です |
| `tests/cli_runtime/test_issue413_lock_options.py` | Start限定lock optionの既存回帰先です | Start以外の候補除外が、parserの現行拒否と一致することです |
| `tests/cli_runtime/test_workspace_sync_vnext.py` | readonly Sync、opaqueな旧projection保全、local unknown、live失敗のpartialです | root文書の例・説明との結合です。Sync実装の再設計はしません |
| `tests/unit/infra/test_provider_distribution.py` | fresh consumerとのdocs／skills parity、static scripts、shim bytesです | 改稿後の配布文書が現行inventory経由で渡ることです |
| `tests/integration/test_issue413_assets.py` | init／update／known-old／unknown／backup／partial／保全です | 改稿前CLI参照の実bytesを使う更新と、保護対象不変です |
| `tests/integration/test_issue413_wheel.py` | fresh wheel、非editable実console、hidden resources、sdist parity、旧runtime非収録です | 配布文書と現在の診断／補完をcandidate packageから確認します |
| `tests/integration/test_cli_entrypoint_vnext.py` | 外部consoleの既存入口回帰先です | checkout sourceへの依存を戻していないことを確認します |

Aboutはpytestからlive更新しません。description値・操作範囲の計画レビューと、許可された実運用のread-backを別の検証にします。

## risk

| リスク | 設計上の対応 |
|---|---|
| 文言修正のつもりでlegacy停止条件を緩める | 例外型・経路・effects・file/remote不変を公開negative testで同時検査します |
| 補完のために共通option定義を削り、位置自由度を壊す | 候補選別を局所化し、parserとlexical処理を維持します |
| candidate試験が実installed packageではなくsourceを読む | 外部非editable環境、実console、import元・resourceの照合を要求します |
| 改稿直前のhashがknown-oldへ入らず既存consumerがunknownになる | 基準bytesから計算した旧current hashを個別に継承します |
| static updateが本Issue外の資産を退役させる | dry-runの効果集合を確認し、範囲外なら本適用を停止します |
| AboutとGit文書の更新時点がずれる | 独立した実施・read-back・保留状態を記録します |
| 履歴の古い値が現在の実績として再利用される | 日時・SHA・環境を保ち、現在のReportと混ぜません |
| 仕様作成の承認を実環境変更許可と誤解する | package／consumer／Aboutごとに実施対象と許可を確認します |

性能改善・新しいbenchmarkはN/Aです。追加の永続IO・ネットワーク・全worktree探索は不要で、補完の候補選別は既存catalogサイズ内の処理です。security/privacyの新機能は追加しませんが、秘密を含まない診断、対象固定、無断上書き防止は本Issueの検証対象です。

将来の`./spec`／shim廃止、global共通skill＋local project情報、同名skill優先順位、dead code整理は未決のまま別Issueへ残します。本Issueの設計採用によって、それらを決定したことにはしません。

### 外部手段の一次情報

以下は2026-10-06に確認した外部手段の仕様です。repository内容の代替情報源ではありません。実施時には使用するtool版と仕様の対応を確認します。

- GitHub Docs「Update a repository」: `https://docs.github.com/en/rest/repos/repos#update-a-repository`。description更新のAPIと権限の確認先です。
- GitHub CLI「gh api」: `https://cli.github.com/manual/gh_api`。明示method、raw-field、GETによる確認の確認先です。
- Fish公式「complete」: `https://fishshell.com/docs/current/cmds/complete.html`。`complete -C`によるnative補完評価の確認先です。
