
# S01実装具体化

**結論:** S01 の最小実装は、次の五点に限定する。

1. approved design の canonical Markdown を、root / Initiative / Epic / Issue 用の4個の明示的 asset として byte-identical に追加する。
2. installer mutation 前に root freshness を一度だけ確定し、fresh root の場合だけ `spec-dock/.workbench/README.md` を exact-copy する。
3. provider と installer fallback の `.gitignore` を、direct child の `README.md` だけを tracking eligible にする同一の3-rule contractへ変更する。
4. generic scaffolder を、render 後の UTF-8 bytes が source bytes と同一なら exact-copy、変化した場合だけ従来どおり render/write する path-agnostic primitive にする。
5. approved plan が指定する focused tests で、fresh-only、future node、byte parity、Git pathname matrix、全 no-backfill trigger を閉じる。

`create_node.py`、Workbench copy/discovery、Artifact import、package/build、docs、dogfood projectionには変更を加えない。これは advisory Artifact であり、approved `requirement.md` / `design.md` / `plan.md` の canonical contractを変更しない。

## exact source observations

### Source verification

GitHub connector により次を確認した。

* repository: `chemitaro/spec-dock`
* branch: `iss-00344-workbench-shell-scaffolding`
* exact source commit: `f1446111ac52c6cfc1783f513ea679dbd72ab1ae`
* branch ref と exact commit の比較結果: `identical`、ahead / behind ともに `0`
* approved `requirement.md`、`design.md`、`plan.md` と、指定された production source / tests を exact commit から読取済み

Approved requirement は、fresh root と future Initiative / Epic / Issue だけに shell を生成し、existing root / node を backfill せず、Issue 346 に full regression、dogfood projection、PR delivery を残す境界を固定している。

添付された `設計判断と提案.txt` は exception taxonomy に関する別件資料であり、Issue 344 S01 の事実根拠または設計根拠には使用していない。

### Locked S01 contract

* Fresh root 判定は installer mutation 前に固定する。
* pre-existing file、directory、symlink、empty directory はすべて existing root とする。
* update、existing init、`init --force`、validate、sync、active switching、Artifact / ADR 作成を backfill trigger にしない。
* future child 作成では child だけが README を得て、ancestor / sibling は不変とする。
* 4 README は canonical Markdown の完全一致 bytes、UTF-8、LF、末尾 newline 1つとする。
* Node生成は既存 generic template recursion に載せ、node-kind-specific production branchを追加しない。
* Unchanged UTF-8 asset は path名に依存せず exact-copyし、placeholderで bytes が変わる通常templateはrenderする。
* Git tracking eligibility は entry type ではなく exact pathname identity で定義する。

Canonical ignore contract は次の3行で固定されている。

```gitignore
**/.workbench/*
!**/.workbench/README.md
**/.workbench/README.md/**
```

### Current source seams and gaps

| Surface                   | Exact source observation                                                                                                                           | S01での扱い                                                                               |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Installer fallback ignore | `_DEFAULT_SPEC_DOCK_GITIGNORE` は現在 `.workbench/` 全体を ignore する。                                                                                    | 上記3-rule contractへ置換する。                                                               |
| Existing file-copy seam   | `cli.py` の `_copy_file()` は parent 作成後に `shutil.copy2()` を使う。                                                                                      | fresh root README の既存 exact-copy seam として再利用する。新しいroot copy subsystemは作らない。           |
| Provider ignore           | provider `.gitignore` も現在 `.workbench/` 全体を ignore する。                                                                                             | fallback と同じ3行へ変更する。                                                                  |
| Four README assets        | 指定された4 pathは exact commit では存在しない。                                                                                                                 | approved design の fenced block をそのまま4ファイルへ追加する。                                       |
| Installer prune           | 現行 legacy prune は `templates/README.md` 以外の nested README を落とすため、新assetをそのまま追加すると node template から消える。                                             | installer側 pruneだけを exact 5-path allowlist-aware にする。`setup.py` の build prune はS03所有。 |
| Generic scaffolder        | 現行 `copy_scaffolded_tree()` は UTF-8 file を `read_text` → render → `write_text` するため、replacement不変でもCRLF等をrewriteし得る。binary側はcopy seamを持つ。          | raw bytesを基準にrender前後bytesを比較するgeneric branchへ最小修正する。                                 |
| Node plan                 | `_scaffold_file_paths()` がtemplate subtreeを再帰列挙し、`plan_node_creation()` の `planned_paths` に入れる。                                                    | template asset追加だけで3 kindに接続する。`create_node.py` は変更しない。                               |
| Node execution/result     | `execute_create_plan()` はgeneric scaffolderの返却pathを集約し、`create_node_core()` が同じpathsを `CreateNodeResult.created_paths` に載せる。                       | plan / result / filesystem parityの既存seamとしてtestする。                                    |
| Semantic opacity          | metadata discovery は exact `.workbench` subtree をtop-down pruneしている。                                                                               | S01では変更しない。                                                                           |
| Workbench copy            | 現行applicationはfull node IDを受けるnode-scoped routeでありroot routeを持たない。                                                                                 | read-only。README filter、root selector、root copyを追加しない。                                |
| Existing CLI test         | `TestCliNew::test_new_nodes_do_not_generate_readme_files` はREADMEゼロを期待しており、S01 contractと逆になる。                                                      | 削除ではなく、「許可された `.workbench/README.md` だけが生成される」期待へ改訂・改名する。                             |
| Runtime test stub         | `test_runtime_new_doc_s09.py` のstub scaffolderも全UTF-8 fileをtext rewriteする。                                                                         | path parity testではreal provider scaffolderを注入するか、stubをgeneric production挙動の証明には使用しない。 |
| New scaffolder test file  | `tests/unit/infra/test_runtime_template_scaffolder.py` は exact commit では存在しない。                                                                     | **新規候補ファイル**として追加する。                                                                  |
| Pytest lane               | `tests/cli_runtime/**` と `test_init_update.py` のnodesは自動的に `full_regression` 分類され、default runではskipされる。`--run-full-regression` はde-skip optionである。 | S01 exact nodesに限って同optionを付ける。bare full-regression runは行わない。                         |

### Assumptions and unverified points

* 本briefではsourceを変更しておらず、testsも実行していない。以下のcommandsはdev-coderが実行して結果を返すためのもの。
* Plan記載のS01 test seed名は、現行で存在すると確認できた名前ではなく、原則として**新規候補名**である。Plan自身もこれらをRed test seedsとして定義している。
* Symlinkを含むGit matrixはsymlinkを作成できる環境での証跡が必要。ローカル環境が非対応の場合、そのrowを未検証のままPASS扱いしてはならない。

## minimal implementation sequence

### 1. Red testsをproduction変更より先に追加する

最初に次のfailureを個別に観測する。

* 4 asset pathが存在しない。
* fresh init後にroot READMEが存在しない。
* provider / fallback ignoreがREADMEも含めてWorkbench全体をignoreする。
* future nodeにREADMEが生成されない。
* unchanged CRLF UTF-8 fixtureがtext rewriteされる。
* 既存の「node READMEを生成しない」testが、新contractと衝突する。
* existing root / nodeの全trigger no-backfill testがまだ存在しない。

Redはcollection error、skip、Git未導入、fixture不足ではなく、上記の対象assertionで失敗させる。`test_init_update.py` と `tests/cli_runtime/**` のRed確認には、exact node selectionと `--run-full-regression` を併用する。

### 2. Canonical README assetを4個追加する

追加path:

* `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`
* `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`
* `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`
* `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`

内容は approved design の `# Workbench` から canonical fenced block末尾までを、そのまま使用する。

実装上の禁止事項:

* 4 asset間でwordingを変えない。
* node ID、title、date等のtemplate replacement tokenを追加しない。
* `.gitkeep` を追加しない。
* 1個のgenerated sourceからbuild-time生成する新frameworkを作らない。
* root / nodeごとの説明差分を作らない。

4個の明示的asset重複はapproved design上の意図された構造であり、過剰なDRY化をしない。

### 3. `cli.py` でpre-mutation freshnessを固定する

`spec-dock` pathへの最初のmutationより前に、`os.path.lexists` 相当でfreshnessを一度だけ確定する。

期待する分類:

| Initial path state           | `fresh_specdock` | Root README    |
| ---------------------------- | ---------------: | -------------- |
| path absent                  |             true | 生成する           |
| empty directory              |            false | backfillしない    |
| existing workspace directory |            false | backfillしない    |
| regular file                 |            false | 置換・backfillしない |
| directory symlink            |            false | 置換・backfillしない |
| dangling symlink             |            false | 置換・backfillしない |

その後の通常managed asset同期は現行どおり行う。root README copyは、最初に固定した `fresh_specdock` がtrueの場合だけ、providerのroot assetから既存 `_copy_file()` seamを通して行う。

重要なnegative条件:

* `spec-dock_dir.mkdir()` 後にfreshnessを再判定しない。
* `Path.exists()` のみで判定しない。dangling symlinkがfreshと誤認される。
* updateまたはforce init時に「READMEがないから生成する」という存在ベースrepairをしない。
* user-created root READMEを上書きしない。
* README削除後のupdateで再生成しない。
* root Workbenchをmanaged treeとしてreplaceしない。

### 4. Installer pruneをexact 5-path allowlist-awareにする

S01で必要なのは `cli.py` 内のinstaller pruneだけである。保持対象をtemplate-root-relativeで次の5件に限定する。

* `README.md`
* `root/.workbench/README.md`
* `initiative/.workbench/README.md`
* `epic/.workbench/README.md`
* `issue/.workbench/README.md`

これにより、fresh/update後のconsumer treeにfuture node用assetが残る一方、allowlist外のlegacy nested READMEは引き続き削除される。

`pyproject.toml`、`setup.py`、wheel / sdist / installed resourceのbuild pruneはS03で扱う。S01でdistribution全体を直そうとしてはならない。Approved planもS01ではinstaller側allowlist-aware pruneを要求し、distribution closureをS03へ分離している。

### 5. Provider / fallback ignoreを同一の3-rule contractへ変更する

変更対象:

* `src/spec_dock/assets/spec_dock/.gitignore`
* `src/spec_dock/cli.py` の fallback定数

両方のWorkbench部分を完全に同じ3行へ変更する。既存の `.agent/`、`.work/`、`active/` 等の周辺contractは変更しない。

このruleは「regular fileだけをunignoreする」ruleではない。exact pathnameをunignoreするruleであるため、testではregular file、symlink、directory、descendantを区別して観測する。

### 6. Generic scaffolderをbyte-stable primitiveへ変更する

`copy_scaffolded_tree()` の各source fileについて、次の順序だけを追加する。

1. source raw bytesを取得する。
2. raw bytesをUTF-8としてdecodeできるか判定する。
3. decodeできない場合は既存binary exact-copyを維持する。
4. decodeできる場合は既存replacementを適用する。
5. rendered textをUTF-8 bytesへencodeする。
6. rendered bytesとsource raw bytesが同一なら、text writeを行わず既存copy metadata seam相当でcopyする。
7. bytesが異なる場合だけ、既存のrender/writeおよび実行bit処理を維持する。

禁止する分岐条件:

* filenameが`README.md`
* pathに`.workbench`を含む
* node kind
* extension
* replacements dictが空かどうか

判定根拠は**render後bytesがsource bytesと同一か**だけにする。`Path.read_text()` をraw byte比較より先に使用するとnewline translationが起こり得るため、CRLF fixtureを使って検出する。

### 7. Existing node creation seamにはassetだけを接続する

`application/create_node.py` は変更しない。

4 assetのうち Initiative / Epic / Issue用3 assetは、既存の:

* `_scaffold_file_paths()`
* `plan_node_creation()`
* `execute_create_plan()`
* `CreateNodeResult.created_paths`

を通ることをtestで証明する。既存 seam はtemplate subtreeを再帰列挙し、copy resultをcommand resultに載せている。

### 8. Contradictory existing testsを新contractへ狭く改訂する

特に次を放置しない。

* `TestCliNew::test_new_nodes_do_not_generate_readme_files`

  * 新規候補名: `test_new_nodes_generate_only_workbench_readmes`
  * 「READMEが0件」から、「各nodeのdirect `.workbench/README.md` だけが存在し、それ以外のREADME proliferationがない」へ変更する。
* `test_init_creates_expected_structure`

  * 既存のnested README否定を、exact five README inventoryへ変更する。
  * allowlist外のnested README否定は維持する。

## Red/Green/refactor

### Red

各Redで、少なくとも次を記録する。

| Red                | Expected failing observation                                         |
| ------------------ | -------------------------------------------------------------------- |
| Asset parity       | 4 assetのうち少なくとも1つがmissing                                            |
| Fresh root         | output README missing、またはGitでREADMEまでignored                         |
| Existing root      | force/updateでREADMEがbackfillされる実装を入れた場合にsnapshot差分                   |
| Node matrix        | planned/result/filesystemのREADME pathがmissing                        |
| Exact-copy         | CRLF source bytesとdestination bytesが不一致                              |
| Placeholder render | exact-copyへ寄せ過ぎた場合にtokenが未置換                                         |
| Path agnostic      | README以外のunchanged UTF-8がrewriteされる                                  |
| Git matrix         | nested/case/payloadがstatusへ露出、またはtop-level READMEがignored            |
| Trigger matrix     | validate/sync/active/artifact/ADR/future child後にexisting snapshotが変化 |

Red evidenceには、実行command、failed node ID、期待したassertion、実際の差分を残す。skipされたtestはRed evidenceではない。

### Green

Greenは次の順で最小化する。

1. 4 canonical assets
2. fresh-only root copy
3. installer prune allowlist
4. provider / fallback ignore
5. generic exact-copy / render branch
6. contradictory test期待の改訂
7. node matrix / no-backfill matrix

Green中に次の新規production abstractionを作らない。

* Workbench service
* README renderer
* asset generator
* node-kind dispatch
* root Workbench route
* README-aware copy filter
* migration / repair command

### Refactor

許可するrefactorはtest helperの局所整理だけとする。

例:

* Workbench subtree snapshot helper
* Git command result assertion helper
* canonical asset path tuple
* node path resolver helper
* operation label付きsnapshot comparison helper

Refactor後も、productionにREADME/path-specific abstractionがないことをdiff reviewで確認し、全focused testsを再実行する。Approved planもGreen後の重複bytes抽象化を禁止し、test helperの局所整理だけを許可している。

## concrete test cases

以下で「新規候補」は、exact commitに既存functionとして存在すると主張しない名称である。

### Case 1 — 4 asset byte parityとcanonical content

* **対象test file / function候補:**
  `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete`
  **新規候補**
* **Fixture / precondition:**
  source checkout内の4 provider asset path。
* **Operation:**
  4ファイルをraw bytesで読み、approved canonical blockと比較する。
* **Exact assertions:**

  * 4 pathがregular fileとして存在する。
  * 4 byte stringsが完全一致する。
  * canonical Markdown bytesと完全一致する。
  * UTF-8 decode可能。
  * UTF-8 BOMなし。
  * `\r`なし。
  * 末尾はnewline 1つで、空行の余分な追加がない。
  * `<INIT_ID>`、`<EPIC_ID>`、`<ISS_ID>`、`<YOUR_NAME>`、`YYYY-MM-DD` 等のnode rendering tokenを含まない。
  * canonicalな `<full-id>` はoperator commandの一部として残る。
  * exact import command
    `./spec-dock/scripts/spec-dock artifact import file ...`
    を含む。
  * exact node copy command
    `./spec-dock/scripts/spec-dock workbench copy --scope <full-id> --to <linked-worktree>`
    を含む。
  * 4 SHA-256 digestの集合sizeが1。
* **Failure detected:**
  asset missing、wording drift、root/node差分、newline変換、template token混入。
* **Closure mapping:**
  `TC-344-003`、`EVD-003`。`tc-s01-001` のcanonical bytes前提。

### Case 2 — Fresh init root vertical tracer

* **対象test file / function候補:**
  `tests/unit/infra/test_init_update.py::TestInitUpdate::test_fresh_init_creates_only_tracked_root_workbench_readme`
  **新規候補**
* **Fixture / precondition:**
  `spec-dock/` がlexically存在しないtemporary Git repository。Git baselineを初期化し、必要なら生成後にREADME以外のpayloadを配置する。
* **Operation:**
  current providerからpublic installer `init`を実行し、filesystem、provider asset bytes、`git check-ignore -v --no-index`、path限定 `git status --short --untracked-files=all` を観測する。
* **Exact assertions:**

  * `spec-dock/.workbench/README.md` がregular fileとして存在する。
  * output bytesがroot provider asset bytesと完全一致する。
  * `.workbench/.gitkeep` が存在しない。
  * root READMEに対する `git check-ignore` はnon-ignoredを示す。
  * README path限定statusは `?? spec-dock/.workbench/README.md` を示す。
  * `.workbench/draft.txt`、binary、nested fileはignoredで、path限定statusに出ない。
  * installed `.gitignore` にexact 3-rule contractが1回だけ存在する。
* **Failure detected:**
  assetだけ追加してpublic installerへ未接続、text rewrite、READMEまでignore、payload露出、`.gitkeep`生成。
* **Closure mapping:**
  `tc-s01-001`、`TC-344-001`、`TC-344-003`、`TC-344-004`、`EVD-001/003/004`。

### Case 3 — Existing root variants、update、force initのno-backfill

* **対象test file / function候補:**
  `tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme`
  **新規候補**
* **Fixture / precondition:**
  次のsubcasesを別temporary directoryで作る。

  1. pre-existing empty `spec-dock/` directory
  2. installed workspaceからroot READMEを削除した状態
  3. user-created root READMEを持つworkspace
  4. pre-existing regular file `spec-dock`
  5. pre-existing directory symlink
  6. dangling symlink
* **Operation:**

  * empty directoryにはexisting `init --force` seamを実行する。
  * installed workspaceにはupdateとforce initを順に実行する。
  * file / symlink variantsには既存installer invocationを実行し、成功可否ではなくno-mutationを観測する。
* **Exact assertions:**

  * freshnessは全existing variantsでfalse扱い。
  * missing root READMEはupdate / force後もmissing。
  * user-created READMEはbytes、name、entry type、`lstat().st_mtime_ns` が不変。
  * regular file / symlinkは置換されず、link targetまたはfile bytesが不変。
  * empty directoryはmanaged workspaceへ更新され得るが、root READMEは生成されない。
  * provider templates、runtime、`.gitignore` の正常更新は許可される。
* **Failure detected:**
  `exists()`によるdangling symlink誤判定、mutation後freshness判定、missing READMEのrepair、user file overwrite。
* **Closure mapping:**
  `tc-s01-002`、`TC-344-001`、`TC-344-005`、`EVD-001`。

### Case 4 — Exact pathname Git ignore matrix

* **対象test file / function候補:**
  `tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_gitignore_tracks_only_top_level_readme`
  **新規候補**
* **Fixture / precondition:**
  Real temporary Git repositoryで次を配置する。

  * exact direct `.workbench/README.md` regular file
  * exact pathname symlink
  * exact pathname directoryとそのdescendant
  * `.workbench/nested/README.md`
  * `.workbench/readme.md`
  * `.workbench/README.MD`
  * `.workbench/README.md.bak`
  * `.workbench/payload.bin`
  * `.workbench-notes/file.md`
* **Operation:**
  provider-installed ignoreとfallback-generated ignoreの両subcaseで、各pathに `git check-ignore -v --no-index` とpath限定statusを実行する。
* **Exact assertions:**

  * direct exact regular READMEはnon-ignoredかつstatusへ出る。
  * exact pathname symlinkもpathnameとしてnon-ignoredかつstatusへ出る。
  * exact pathnameがdirectoryの場合、directory自体はGit objectにならず、そのdescendantはignored。
  * nested README、case variants、near-file-name、other payloadはignored。
  * `.workbench-notes` はWorkbench ruleの対象外でstatusへ出る。
  * providerとfallbackの判定matrixが完全一致する。
* **Failure detected:**
  nested/case/payload露出、README過剰ignore、near-name overmatch、directory descendant再包含、fallback drift。
* **Closure mapping:**
  `tc-s01-004`、`TC-344-004`、`EVD-004`。

### Case 5 — Unchanged UTF-8 CRLF exact-copy

* **対象test file / function候補:**
  `tests/unit/infra/test_runtime_template_scaffolder.py::test_copy_scaffolded_tree_uses_exact_copy_for_unchanged_utf8_bytes`
  **新規候補ファイル / 新規候補function**
* **Fixture / precondition:**
  READMEでもWorkbenchでもないpathに、CRLFを含むvalid UTF-8 bytesを置く。replacement keysはsourceに現れない。
* **Operation:**
  real provider `copy_scaffolded_tree()` を実行する。
* **Exact assertions:**

  * destination raw bytesがsource raw bytesと完全一致。
  * `\r\n` countが不変。
  * returned `created_paths` がdestination pathをexactに含む。
  * source / destination textの意味一致だけではなくbytes一致をassertする。
* **Failure detected:**
  `read_text` / `write_text` newline normalization、unnecessary render rewrite。
* **Closure mapping:**
  `tc-s01-003`、`TC-344-002B`、`TC-344-003`、`EVD-002/003`。

### Case 6 — Changed placeholder templateはrenderする

* **対象test file / function候補:**
  `tests/unit/infra/test_runtime_template_scaffolder.py::test_copy_scaffolded_tree_still_renders_changed_placeholder_text`
  **新規候補**
* **Fixture / precondition:**
  `<ISS_ID>` 等、既存replacement mapでbytesが変化する通常UTF-8 template。
* **Operation:**
  real provider `copy_scaffolded_tree()` をreplacement付きで実行する。
* **Exact assertions:**

  * destination bytesがsource bytesとは異なる。
  * destination textにreplacement valueが存在する。
    -置換対象tokenが残らない。
  * surrounding textとexpected newlineが既存render contractどおり。
  * returned pathが正しい。
* **Failure detected:**
  exact-copy branchを広げ過ぎてplaceholder renderを停止する回帰。
* **Closure mapping:**
  `tc-s01-003`、`TC-344-002B`、`EVD-002`。

### Case 7 — Exact-copy判定のpath agnosticism

* **対象test file / function候補:**
  `tests/unit/infra/test_runtime_template_scaffolder.py::test_copy_scaffolded_tree_exact_copy_is_path_agnostic`
  **新規候補**
* **Fixture / precondition:**
  同じunchanged CRLF UTF-8 bytesを、少なくとも次の異なるrelative pathへ配置する。

  * `.workbench/README.md`
  * `ordinary/note.txt`
  * `nested/extensionless`
* **Operation:**
  同じreplacement mapでtree全体をcopyする。
* **Exact assertions:**

  * 全destinationでsource bytes完全一致。
  * 全pathがcreated resultに一度だけ存在。
  * path、basename、extensionによる結果差がない。
* **Failure detected:**
  README-specific、Workbench-specific、extension-specific branch。
* **Closure mapping:**
  `tc-s01-003`、`TC-344-002B`、`EVD-002/003`。

### Case 8 — Initiative / Epic / Issue plan-result-filesystem matrix

* **対象test file / function候補:**
  `tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_new_node_workbench_readme_matrix`
  **新規候補**
* **Fixture / precondition:**
  temporary `spec-dock` provider treeに3 node templates、required rules sources、canonical README assetsを配置する。Testの`Ports`にはreal `template_scaffolder` moduleを注入する。
* **Operation:**
  Initiative、Epic、Issueを順にplanし、対応するpublic application create seamを実行する。
* **Exact assertions:**

  * 各kindでexpected pathは `<new-node>/.workbench/README.md`。
  * expected pathが `plan.planned_paths` にexactに1回存在する。
    -同じpathが `result.created_paths` にexactに1回存在する。
  * filesystem上でregular fileとして存在する。
  * planned path setとmaterialized file/symlink/meta path setが一致する。
  * 3 output bytesがcanonical asset bytesと一致する。
  * `.gitkeep` または追加Workbench payloadは生成されない。
  * node-kind-specific production hookを必要としない。
* **Failure detected:**
  template recursion未接続、kind漏れ、plan/result drift、stubだけ通るfalse positive。
* **Closure mapping:**
  `TC-344-002A`、`TC-344-003`、`EVD-002/003`。

### Case 9 — Future child creationはancestor / siblingを変更しない

* **対象test file / function候補:**
  `tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_new_node_workbench_readme_does_not_touch_existing_scopes`
  **新規候補**
* **Fixture / precondition:**
  existing root、ancestor Initiative / Epic、sibling nodeのWorkbenchに、file、nested directory、binary、可能ならsymlinkを置き、entry kind、relative name、bytes / link target、mtime_nsをsnapshotする。
* **Operation:**
  Initiative、Epic、Issueの各future child creationを独立fixtureまたはparameterized caseで実行する。
* **Exact assertions:**

  * new childだけにcanonical READMEが生成される。
  * root、ancestor、siblingのsnapshotが完全一致する。
  * missing READMEをancestor / siblingへbackfillしない。
  * ancestor / siblingのcanonical docs / metadataもunrelated diffを持たない。
* **Failure detected:**
  parent traversal mutation、template backfill、ancestor directory reuse、sibling污染。
* **Closure mapping:**
  `TC-344-002A`、`TC-344-005`、`EVD-001/002`。

### Case 10 — 全triggerのpublic lifecycle no-backfill

* **対象test file / function候補:**
  `tests/cli_runtime/test_new.py::TestCliNew::test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers`
  **新規候補**
* **Fixture / precondition:**

  1. public initとexisting helperでroot / Initiative / Epic / Issue hierarchyを作る。
  2. 生成READMEを削除し、pre-S01 existing workspaceを模擬する。
  3. rootと3 node Workbenchへ、regular file、binary、nested file、empty directory、可能ならsymlinkを配置する。
  4. recursive inventory、entry type、file bytes、link target、`lstat().st_mtime_ns`をsnapshotする。
* **Operation:**
  次を順に実行し、各操作直後にsnapshotを比較する。

  1. existing `init --force`
  2. update
  3. `validate`
  4. `sync`
  5. `active set`
  6. `new artifact blank`
  7. `new artifact adr`
  8. future child issue creation
* **Exact assertions:**

  * 1〜7の各操作後、root / existing Initiative / Epic / IssueにREADMEがbackfillされない。
  * 各existing Workbench snapshotが完全一致する。
  * Artifact / ADRは正規`artifacts/` surfaceだけを変更する。
  * future childだけにcanonical READMEが生成される。
  * child作成後もancestor / sibling snapshotは不変。
  * validate / sync / active結果はWorkbench不在をfailureにしない。
  * assertion failureにはoperation labelとchanged pathを含める。
* **Failure detected:**
  hidden backfill trigger、read-only command side effect、Artifact setupによるWorkbench mutation、future childのancestor污染。
* **Closure mapping:**
  `tc-s01-002`、`TC-344-001`、`TC-344-002A`、`TC-344-005`、`EVD-001/002`。

### Existing test revision

`TestCliNew::test_new_nodes_do_not_generate_readme_files` は残存させない。新規候補名 `test_new_nodes_generate_only_workbench_readmes` へ改訂し、次をassertする。

* Initiative / Epic / Issueの各direct `.workbench/README.md` は存在する。
* それら3件以外にnode subtreeで新規READMEを増殖させない。
* 3件はbyte-identical。
* `.gitkeep` は存在しない。

## exact verification commands

### 1. Generic scaffolder exact nodes

この新規test fileはheavy prefix外なのでdefault fast laneで実行される。

```bash
uv run pytest -q -ra tests/unit/infra/test_runtime_template_scaffolder.py
```

### 2. Installer exact nodes

`test_init_update.py` はcurrent policy上full-regression分類されるため、**選択したS01 nodesだけ**をde-skipする。

```bash
uv run pytest -q -ra --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_fresh_init_creates_only_tracked_root_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_gitignore_tracks_only_top_level_readme
```

### 3. Node plan / result / filesystem exact nodes

```bash
uv run pytest -q -ra --run-full-regression \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_new_node_workbench_readme_matrix \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_new_node_workbench_readme_does_not_touch_existing_scopes
```

### 4. Public lifecycle exact nodes

```bash
uv run pytest -q -ra --run-full-regression \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_nodes_generate_only_workbench_readmes \
  tests/cli_runtime/test_new.py::TestCliNew::test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers
```

### 5. S01 focused regressions

```bash
uv run pytest -q -ra --run-full-regression \
  tests/unit/infra/test_init_update.py -k 'workbench or readme'

uv run pytest -q -ra --run-full-regression \
  tests/cli_runtime/test_runtime_new_doc_s09.py
```

Approved planのoriginal gateも、installer、generic scaffolder、node lifecycleのfocused verificationを要求している。

### 6. Optional current default fast suite

```bash
uv run pytest -q -ra
```

これはcurrent main-derived fast laneの確認であり、`tests/cli_runtime/**` と大部分の `test_init_update.py` がpolicy skipされる。したがって、上記S01 exact-node commandsの代替にはならない。

`--run-full-regression` は選択したheavy nodesをde-skipするためだけに使用する。次のbare commandは実行しない。

```text
uv run pytest --run-full-regression
```

Issue 346所有の全full-regression closure、candidate wheel E2E、PR deliveryはS01に要求しない。Requirementもfull suite closureとdeliveryを明示的にout of scopeとしている。

### 7. Static and diff checks

```bash
uv run ruff check \
  src/spec_dock/cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  tests/unit/infra/test_init_update.py \
  tests/unit/infra/test_runtime_template_scaffolder.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_new.py

uv run ruff format --check \
  src/spec_dock/cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  tests/unit/infra/test_init_update.py \
  tests/unit/infra/test_runtime_template_scaffolder.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_new.py

git diff --check
git diff --name-only
git status --short
```

S01 exact nodesについては、pytest summaryに`skipped`がないことを確認する。Symlink非対応によるmatrix row未実行は、別のsupported environmentで閉じるまでclosure未完了とする。

## allowed/forbidden boundary

### Allowed changes

| Path                                                                                    | 許可する差分                                                                                         |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `src/spec_dock/cli.py`                                                                  | pre-mutation freshness、fresh-only root asset copy、fallback ignore、installer exact README prune |
| `src/spec_dock/assets/spec_dock/.gitignore`                                             | Workbench部分をexact 3-rule contractへ変更                                                           |
| `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`                    | canonical asset追加                                                                              |
| `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`              | canonical asset追加                                                                              |
| `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`                    | canonical asset追加                                                                              |
| `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`                   | canonical asset追加                                                                              |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` | generic render後bytes比較とexact-copy branch                                                       |
| `tests/unit/infra/test_init_update.py`                                                  | asset、freshness、no-backfill、Git matrix、既存structure期待の改訂                                        |
| `tests/unit/infra/test_runtime_template_scaffolder.py`                                  | 新規generic exact-copy / render / path-neutral tests                                             |
| `tests/cli_runtime/test_runtime_new_doc_s09.py`                                         | 3-kind plan/result/fs matrix、ancestor/sibling不変                                                |
| `tests/cli_runtime/test_new.py`                                                         | existing contradictory test改訂、全trigger lifecycle test                                          |

### Forbidden changes

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workbench.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
* generic Artifact import implementationまたはglobal installer dispatch
* root `workbench copy` selector、route、bulk copy、path selection
* README-aware copy filter
* `pyproject.toml`
* `setup.py`
* package / wheel / sdist / installed resource tests
* provider docs
* dogfood `spec-dock/**` projection
* `requirement.md`、`design.md`、`plan.md` の変更
* canonical `report.md` のworker直接編集
* Issue 345 / 346の実装または完了主張
* PR作成、merge preparation、merge、Issue finishの主張

Current Workbench implementationはopaque source-wins copyとexact `.workbench` discovery pruneを既に持つため、S01で触る理由はない。

## stop conditions

次のいずれかが発生した時点で、S01 implementationを拡張せずmain orchestratorへ返す。

1. Checkout HEADが `f1446111ac52c6cfc1783f513ea679dbd72ab1ae` と一致しない。
2. Canonical README wording、9 guidance elements、exact commandsの変更が必要になる。
3. Allowed path外のproduction変更が必要になる。
4. Freshnessをinstaller mutation前に固定できない。
5. Existing rootをbackfillしないためにmigrationまたはrepair commandが必要になる。
6. Generic exact-copyを成立させるためにREADME、`.workbench`、node kind、extensionの分岐が必要になる。
7. Red testがproduction変更前から成功する、または意図しない理由で失敗する。
8. S01 exact nodeがpytest policyによりskipされる。
9. Real Git matrixでREADME以外のWorkbench contentがstatusへ露出する。
10. Symlink matrixをsupported environmentで実行できず、代替evidenceもない。
11. Existing Workbench entry、bytes、names、mtimeに差分が出る。
12. Existing focused testにS01差分由来のregressionが出る。
13. `pyproject.toml` / `setup.py`を変更しないとwheel/sdistを通せない。これはS03へのhandoffであり、S01で修正しない。
14. Workbench copy、semantic discovery、root route、Artifact importのcontract変更が必要になる。
15. Issue 346所有のfull regressionまたはdeliveryをS01 closure条件にする必要が出る。

## risks and anti-overengineering

| Risk                                           | Control                                                                                                                           |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `Path.exists()` がdangling symlinkをabsent扱いする   | freshnessは`lexists`相当で一度だけ固定し、dangling symlink caseをtestする。                                                                       |
| UTF-8 text APIがCRLFをnormalizeする                | source raw bytesを先に保持し、rendered UTF-8 bytesと比較する。                                                                                 |
| Installer pruneが新assetを削除する                    | target template subtreeのexact 5-path inventoryをtestする。                                                                            |
| Fallback ignoreだけ旧contractのまま残る                | provider/fallback両subcaseを同じreal Git matrixで検証する。                                                                                 |
| README unignore ruleがdirectory descendantを露出する | third ruleとdirectory/descendant status rowを必須にする。                                                                                 |
| Existing negative testが新機能を阻害する                | READMEゼロではなくexact allowed READMEだけをassertするよう改訂する。                                                                                |
| Default pytestがfalse greenになる                  | heavy nodesをexact selection + `--run-full-regression`で明示実行する。                                                                     |
| Lifecycle testがmtime resolutionでflakyになる       | fixture mutation完了後に`lstat().st_mtime_ns`をsnapshotし、不要なsleepを入れない。                                                                |
| Asset duplicationを過剰に抽象化する                     | 4 explicit assetsを維持し、parity testでdriftを防ぐ。                                                                                       |
| Generic exact-copyがmode/mtimeまで過剰contract化される  | S01のpublic assertionはbytesとcreated pathを中心にする。existing Workbench preservationだけmtimeをassertする。                                    |
| Package exclusionが4 assetを落とす                  | known deferred S03 concernとして記録し、S01で`pyproject.toml` / `setup.py`を触らない。Current package configにはnested README broad exclusionが残る。 |
| READMEをsemantic authorityとして解釈する実装が入り込む        | parser、classifier、metadata registration、source manifest登録を追加しない。                                                                  |
| Root Workbench copyを便利機能として追加する                | root READMEはGit checkout、root ignored payloadのdurable化はIssue 345 generic importという境界を維持する。                                        |
| Full regressionをS01で実施してscopeが拡散する             | focused nodesとdefault fast suiteまで。bare full-regression、wheel E2E、PR deliveryはIssue 346へ残す。                                       |

## dev-coder handoff checklist

### Before implementation

* [ ] repository / branch / HEADが指定値と一致している。
* [ ] working treeの開始状態を記録した。
* [ ] approved designのcanonical README fenced blockを再確認した。
* [ ] S01 allowed path一覧を作業前に固定した。
* [ ] Plan seed名をexisting test名と誤認せず、新規候補として扱った。

### Red

* [ ] 4 asset missing Redを確認した。
* [ ] fresh root未生成 / README ignored Redを確認した。
* [ ] node path missing Redを確認した。
* [ ] CRLF rewrite Redを確認した。
* [ ] placeholder renderのcharacterizationを確認した。
* [ ] Git nested/case/payload matrix Redを確認した。
* [ ] no-backfill trigger testが意図した差分を検出できることを確認した。
* [ ] 各Redはskipやcollection failureではなく対象assertionで失敗した。

### Green

* [ ] 4 assetsがcanonical bytesと完全一致する。
* [ ] freshnessが最初のinstaller mutation前に一度だけ固定される。
* [ ] fresh rootだけにREADMEがcopyされる。
* [ ] update / force initはmissing READMEを再生成しない。
* [ ] user-created root READMEを上書きしない。
* [ ] installer pruneがexact 5 README pathsを保持する。
* [ ] provider / fallback ignoreが同じ3-rule contractである。
* [ ] generic scaffolderにREADME/path-specific branchがない。
* [ ] unchanged CRLF bytesが完全一致する。
* [ ] changed placeholder templateがrenderされる。
* [ ] Initiative / Epic / Issueでplan / result / filesystem pathが一致する。
* [ ] future childだけがREADMEを得る。
* [ ] existing root / nodeのentry、bytes、names、mtimeが不変である。

### Verification

* [ ] Generic scaffolder suiteを実行した。
* [ ] Installer exact nodesを `--run-full-regression` 付きexact selectionで実行した。
* [ ] Node matrix exact nodesを実行した。
* [ ] Public lifecycle exact nodeを実行した。
* [ ] S01 selected nodesにunexpected skipがない。
* [ ] `test_init_update.py -k 'workbench or readme'` がPASSした。
* [ ] `test_runtime_new_doc_s09.py` focused regressionがPASSした。
* [ ] Optional default fast suite結果を記録した。
* [ ] Ruff check / format checkがPASSした。
* [ ] `git diff --check` がPASSした。
* [ ] `git diff --name-only` がallowed pathだけである。
* [ ] package build、full regression、docs、dogfood、generic importを実行・変更していない。

### Evidence returned to main orchestrator

* [ ] Changed files一覧
* [ ] Red command / expected failure / actual failure
* [ ] Green command / pass count / skip count
* [ ] Refactor内容と再実行結果
* [ ] 4 README SHA-256
* [ ] Fresh / existing root snapshot summary
* [ ] 3 node plan-result-filesystem path matrix
* [ ] CRLF source / destination byte evidence
* [ ] Placeholder render evidence
* [ ] Real Git ignore/status matrix
* [ ] 全trigger before/after Workbench snapshot summary
* [ ] `EVD-001`〜`EVD-004` へ転記できるworker summary
* [ ] 未解決riskとS03 / Issue 346へのdeferred事項
* [ ] 実装判断を追加していない場合は、
  `No material implementation decisions beyond the approved plan.`
* [ ] approved planを超える判断があった場合は、実装継続せずLedger Note候補として明示した
* [ ] PR-ready、merge-ready、Issue finish、Epic completionを主張していない

S01 close条件は `TC-344-001`、`TC-344-002A/B`、`TC-344-003`、`TC-344-004`、`TC-344-005` の全件であり、特にTC-344-005はinstaller exact nodeとpublic lifecycle exact nodeの2本で既存root/node全trigger不変を証明する。
