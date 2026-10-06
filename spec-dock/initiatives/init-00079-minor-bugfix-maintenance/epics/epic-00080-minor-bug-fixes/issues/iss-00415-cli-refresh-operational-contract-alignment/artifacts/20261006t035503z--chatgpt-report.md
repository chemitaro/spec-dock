## 1. 検証結果と調査範囲

**Strict GitHub connector検証は成功しました。** 添付から分析を始める前に、接続されたGitHub connectorで `chemitaro/spec-dock` の `main` を直接取得し、branch-tipのfull SHAが指定値と完全一致することを確認しました。先端はPR #414のマージcommitです。

| 項目 | 検証結果 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| 対象branch | `main` |
| expected_sha | `0e7dc86841cb48d011270a1a2165cb6406ac0cea` |
| 取得したfull branch-tip SHA | `0e7dc86841cb48d011270a1a2165cb6406ac0cea` |
| SHA比較 | 完全一致 |
| 以後のファイル取得 | 上記commit SHAに固定。他branchへの切替・fallbackなし |

調査では、現行README・AGENTS・関連docs、providerの配布資産、consumerの追跡済み投影、公開dispatcherからの呼出経路、installation・shim・selector・補完・Artifact実装、関連テスト、Issue 413 recovery planning packと実装記録の関連部分を確認しました。添付は行番号確認などの補助に限定し、主要なskill・CLI・導入テストの抜粋については、再構成した内容のGit blob SHAもconnector取得値と照合しました。例えば、添付の通常skillはGitHub正本と一致しています。attachments-bundle 

**今回はソース・テストコードの静的調査です。** pytest、wheelの再build、実consumerでのCLI操作、実agentによるskill起動は実行していません。以下でいう「確定指摘」は、取得した実装と文書の矛盾を確認できたものを指し、この環境で障害を再現したという意味ではありません。GitHub・repositoryへの変更も行っていません。

結論を先にまとめると、次のとおりです。

**`./spec` は現行の新規installationでは生成されません。mainに追跡されている互換ショートカットです。薄いshimはそれとは別の配布資産で、まだ文書と互換テストに依存があります。先に直すべきなのは、このリンクの一律削除ではなく、現行入口の誤案内と復旧診断です。skillのglobal配置は設計案として有望ですが、現行installerが対応しているわけではありません。**   

---

## 2. 優先順の確定指摘表

本調査範囲では、直ちにデータを破壊するP0/P1不具合は確定していません。以下は、復旧時の誤操作、現行手順の実行失敗、運用判断の混乱につながるP2指摘です。

表中の行番号は、GitHubソースファイル本文の行番号です。「確認方法」は後続の修正時に行う検証であり、今回は未実行です。

| 安定ID | 深刻度 | 対象path:line | 現在の問題 | 実害 | 最小修正 | 確認方法 |
|---|---|---|---|---|---|---|
| **SD-OPS-001** | P2・復旧安全性 | `src/spec_dock/runtime/infra/fs_repo.py:338–348,361–365` | 旧 `meta.json` を検出すると、一律に `.meta.json` へrenameして再試行するよう案内する。このreaderは現在のScope作成経路からも呼ばれる。 | 妥当なschema3 `.meta.json` と旧 `meta.json` が同居する場合、案内に従った手作業が現行metadataとの衝突・上書きを招き得る。CLI自身が上書きするわけではない。 | 「保全・内容比較・既存 `.meta.json` の確認」を促す診断へ変更。単純renameを一般的な移行手順として勧めない。 | 正常schema3 Scopeに旧 `meta.json` を追加し、create/importが副作用前に停止すること、保護ファイル不変、危険なrename案内が出ないことを確認。 |
| **SD-OPS-002** | P2・導入手順 | `README.md:21–23` | Scope作成例が `--json` を指定しながら `--yes` を欠く。実装はこの組合せを `CONFIRMATION_REQUIRED` で停止する。 | READMEをそのまま実行しても最初のScopeを作れない。JSON出力の説明と実行契約が食い違う。 | 作成が許可された例に `--yes` を付ける。単にparserが通るだけでなく、非対話確認条件も文書テストに含める。 | stateful `gh` stubを使い、掲載例が確認不足で停止しないこと、想定外の重複作成がないことを確認。 |
| **SD-OPS-003** | P2・対象指定 | `src/spec_dock/assets/spec_dock/docs/reference_cli.md:3`、`docs/github-issue-integration.md:13` | 通常TARGETの説明にGitHub番号・URLを含めているが、通常Scope selectorとimport用GitHub refは別文法。root docsの裸番号import例にも `--github-repo` がない。 | `scope show URL` や、repository指定なしの裸番号importなどが失敗する。誤った対象文法が各種自動化へ広がる。 | 通常TARGETを完全ID・`gh:OWNER/REPO#NUMBER`・許可された動的selectorとして説明。importのみURL、または番号＋`--github-repo`を説明する。parserを無闇に拡張しない。 | 通常selectorとimport refの正例・負例を分けて検証。文書例と実際の解決経路を照合する。 |
| **SD-OPS-004** | P2・現行運用 | `docs/sync-aggregation.md:1–13` | 「現行」と題した文書が、Syncによる生成物再構築と `--source cache` を案内している。現在はその場の観測で、cache指定は退役診断となる。 | 存在しない更新効果を期待したり、実行不能なコマンドへ誘導されたりする。 | 小さな現行説明、またはproviderの現行Sync参照への案内にする。歴史的な生成処理の説明は明確に分離する。 | `--source cache` が退役診断、local/githubが現行選択肢であることを確認。Sync前後で保存物が増えない境界も維持する。 |
| **SD-OPS-005** | P2・運用状態表示 | `AGENTS.md:10` | 現行agent入口に「0805のみ適用済み、main等未移行、人間merge pending」という2026-10-03の引継ぎ状態が残る。現在取得したmainはPR #414のマージcommit。 | agentがマージ済みmainでも未merge扱いしたり、過去のlocal rollout状況を現在の実環境状態と混同したりする。 | 当時の観測を履歴として残し、現在の入口から分離する。merge済みというcommit上の事実と、未再観測の各tool環境・worktree状態を別記する。 | AGENTSの現行説明、マージcommit、追跡済みconsumer資産を照合。実環境の移行完了は別の現物確認を要求する。 |
| **SD-OPS-006** | P2・補完 | `src/spec_dock/runtime/cli/options.py:257–269,458–463` | 補完生成が全leafへ全共通optionを追加する一方、parserは読取コマンドの `--yes`、Start以外の `--lock-timeout` を拒否する。 | 補完が実行不能な入力を積極的に提示する。help・補完を正本として使うagent-first運用とも不整合。 | leafごとの適用条件で候補を絞る。共通optionの位置自由度やcontext-free性は維持する。 | Bash/Zsh/Fishで、例えば `scope list` に `--yes`、`active show` に `--lock-timeout` が出ないことを検査する。 |

根拠は、SD-OPS-001が現在のScope公開処理と旧readerの接続、SD-OPS-002がREADMEと非対話確認guard、SD-OPS-003が二種類のselector実装です。     

SD-OPS-004は現行扱いのroot文書と退役引数処理、SD-OPS-005はAGENTSと検証済みマージcommit、SD-OPS-006は同じファイル内の補完生成とparser判定の矛盾です。    

### commit外で確認した公開入口の不整合

**SD-OPS-007／P2：GitHub repositoryのAbout説明が旧方式のままです。** `repository.description` は、`uvx`、`.spec-dock/`、任意のCodex skill、runtime依存なし・コピー済みファイルだけ、という紹介になっています。これは現在の外部installed packageと `spec-dock/` 静的資産の説明とは一致しません。対象はGitHub metadataなので `path:line` はなく、指定commitの内容とは別の観測です。

最小対応は公開説明の更新です。ただし、今回は設定変更を行っていません。README修正のcommitに含めたつもりで放置しやすい、独立した公開入口の更新項目として扱うべきです。

### 修正時に外してはいけない付随作業

provider配布文書やskillを変更する場合、本文だけを直して終わりにはできません。`static-inventory.json` の現在hashと、必要な既知旧hashの扱いを更新し、fresh wheel・fresh consumerへの投影を確認する必要があります。現行loaderは配布bytesとinventoryの不一致を拒否するためです。rootの通常docsやAGENTSの変更と、inventory管理下の配布資産変更は区別してください。 

---

## 3. 意図的維持・履歴・未検証の分類

### 3.1 現時点で問題を確認していないもの

| 対象 | 確認できた状態・評価 |
|---|---|
| **provider／consumerの静的投影** | `docs`、`templates`、`system`、`scripts` はproviderとconsumerのGit tree IDが一致しています。「providerだけ更新され、mainのconsumer docsが旧版のまま」という状態ではありません。root `.agents` もproviderのinstall_root側と一致します。 |
| **consumerの追跡済み `.agents`** | 現在は通常skillとGrill skillの二つ。Grillの付属ファイルはYAMLとfinalizerです。退役skillがこの追跡treeに大量に残っている、という指摘は成立しません。 |
| **通常skillの主要契約** | 外部console、四層の所有境界、新規ScopeはGitHub、Startだけが直接対象を取得、Finishとdelivery/mergeの分離、Artifactの新JSON pathを説明しています。 |
| **GrillのArtifact JSON契約** | `specdock.cli/v2`、`status=succeeded`、`data.kind=artifact`、`data.result.artifact.path` を確認する手順は現在の実装に合っています。 |
| **Grillのrulesリンクpreflight** | `artifacts/rules.md` を要求すること自体は取り残しではありません。現在のScope作成も、対応するArtifact rulesへの相対symlinkを生成します。 |
| **uninstallの保全境界** | 仕様、Artifact、Workbench、直接記録、workspace宣言、ignore、未知ファイルを残すことがテストされています。「消し残しだから一括削除すべき」とは扱いません。 |
| **配布検査の構成** | wheel内runtimeの一重化、旧runtime・旧entrypointの非収録、hidden assets、inventory hash、sdist由来wheelの比較を検査するテストがあります。 |
| **対応OSのCI構成** | Provider CIは通常lint・pytestを維持し、配布検査はUbuntu/macOSのmatrixです。今回の刷新にWindows再対応を混ぜる理由は確認していません。 |

静的投影とskill inventoryの評価は、内容検索ではなくGit treeの同一性・完全なskill subtree取得に基づきます。  

Grillの現行契約は、実装と統合テストの両方で対応を確認しました。統合テストは公開CLIでArtifactを作成し、その返却pathをfinalizerへ渡し、canonical文書・metadata・Gitの不変を検査しています。ただし、このテストを今回実行したわけではありません。   

uninstallと配布検査も、期待する境界がコードに存在することの確認です。**テストが存在することと、今回の候補wheelを実環境で再認定したことは別です。**    

### 3.2 現在到達する診断と、旧コードを区別する

**現行の退役診断は残してよいものです。** `--source cache`、新規 `--backend local`、旧resume/rollback等に対する `ARGUMENT_RETIRED` 系の拒否は、旧機能を復活させるコードではありません。旧入力を無言で別の意味に解釈せず停止する、移行上必要な入口です。shimの `EXTERNAL_CLI_UNAVAILABLE` と `SHIM_RECURSION` も、旧engineへfallbackさせないための現在の診断です。  

一方、`presentation/cli_text.py` に残る旧active表示を、現在の `active show` の出力不具合とすることはできません。現在のdispatcherは直接記録から新しいdataを構成し、`presentation.envelope` の表示経路へ渡しています。旧 `render_active_show_text()` があるという検索hitだけでは、現在の利用者へその文言が出る証拠になりません。 

また、`fs_repo.py` はファイル全体がdead codeではありません。現在のScope公開処理が旧readerの一部を再利用しています。そのため、**SD-OPS-001のrename案内は優先対象ですが、同ファイルにある旧create-lock・readonly writer等を一括撤去するのは不適切**です。特に旧「metadata欠落＋create.lock」診断は、新しいschema readerが先にmetadata欠落を拒否する経路があるため、通常操作での到達をそのまま認定していません。  

旧presentation関数を直接検査するunit testも残っています。これは直ちに「現在の公開CLIが旧契約」という意味ではなく、**保守している内部APIの期待値と、公開CLIの期待値が混在している状態**として整理するのが妥当です。削除候補は関数単位で呼出元を確認し、対応する旧テストと一緒に扱うべきです。 

### 3.3 履歴として保存するもの

Issue 413の要件冒頭にある旧SHA・試験件数・0805の観測は、2026-10-03時点の記録です。その記録自身が、既存Gate証拠、caller-provided local observation、文書差し替え、実適用を区別しています。これらを現在のmainに合わせて一括置換すると、むしろ証拠の時点が壊れます。**AGENTSという現行入口の整理と、recovery packの当時の記録の保存を分けるべきです。** 

`docs/scope-lifecycle-start-finish-analysis.md` には、移行前の調査記録であることと現行CLI参照への案内が既にあります。この文書の旧 `issue start/finish` や旧module pathは、現在の不具合として置換する対象ではありません。配布側のHistorical説明やdiscussion rulesも、旧資料を新規作成手順としない方針を明示しています。  

### 3.4 未検証・条件付き事項

| 項目 | 今回の境界 |
|---|---|
| **ユーザー環境のactive／Scope #413** | `active show` がempty、`scope show iss-00413` がSCOPE_NOT_FOUNDという観測は再実行していません。GitHub Issueの存在、planning packの存在、consumerへの正式import、work start成立は別です。 |
| **他worktree・別clone・別PCの移行完了** | mainの追跡ファイルの一致からは認定できません。外部tool環境やignored recordもconnectorのcommit内容からは見えません。 |
| **Grillの実host動作** | `grilling` と `domain-modeling` の実際の発見・read-only互換・一連の起動は未検証です。 |
| **Grillのnested CWD** | SKILL.mdのhelper例はrepo相対pathです。統合テストは絶対helper path＋root CWDです。nested起動時の手順品質は追加検証対象で、今回、実host障害までは認定していません。 |
| **公開リンクの全件検査** | 直接辿った現行README・主要参照・HTML末尾の参照先には欠落を確認していません。ただし全Markdownの全anchor、過去artifact内URL、ブラウザ描画の全件検査は未実行です。 |
| **実際のwheel配布物** | sourceとテスト構成を確認しました。今回のwheel build・インストール・実processによる再検証は未実行です。 |

GrillのCWD依存は、現行root運用の確定障害というより、**global化前に解消すべき具体的な可搬性課題**です。skillのある場所と対象projectの場所を分離し、helperは読み込まれたskill directoryからの絶対path、CLIは明示したprojectへ固定する設計が適切です。 

---

## 4. `./spec` の結論と、shimを廃止する場合の影響

### 4.1 新規installationは `./spec` を生成しない

現行の経路は、概ね次の構成です。

```text
公開CLI
  → installation dispatcher
  → install_static_assets()
  → package_static_assets()
  → inventoryにある静的ファイルをpublish
```

`package_static_assets()` の許可対象にrootの `spec` はありません。initもそのinventoryを順に公開する処理で、rootのsymlinkを作る別処理は確認されません。したがって、**現在の新規initで `./spec` が自動生成されるという仮説は、取得した実装とは一致しません。**  

一方、このmainには `spec` がGitのsymlink mode `120000` で追跡され、blob内容は `spec-dock/scripts/spec-dock` です。少なくとも現在の分類は「新規installerが作る資産」ではなく、**repositoryが追跡している互換ショートカット**です。どの過去commitで導入されたかまでは今回追跡していません。 

### 4.2 テストは「生成」ではなく「既存リンク経由の互換」を守っている

`test_native_spec_symlink_uses_isolated_python_and_forwards_help_without_git` は、fixtureで明示的に `shortcut.symlink_to(script)` を実行しています。そのうえで `./spec -h` の転送とcheckout-local Pythonの混入防止を検査します。

このテストを根拠に「initがリンクを作る」と読むのは誤りです。しかし逆に、**既存のリンクからの起動を完全に無関係な過去契約として捨てるのも誤り**です。現在も互換動作を検査する意図が残っています。

### 4.3 `./spec`、薄いshim、外部consoleは三つに分ける

| 入口 | 現在の役割 | 廃止の意味 |
|---|---|---|
| `spec-dock` | PATH上の外部installed console。標準入口。 | CLIそのものの導入・利用を変える話。今回の整理対象ではない。 |
| `./spec-dock/scripts/spec-dock` | 外部consoleへargv・CWD・終了値を渡す薄いshim。現在の配布資産。 | rules等の案内、既存automation、互換入口、配布inventoryを変更する話。 |
| `./spec` | 上記shimを指す追跡済みsymlink。現行initの管理対象外。 | この短縮名を使う利用者・スクリプトとの互換を変更する話。 |

shimはcheckout runtimeやGit controlを探しません。PATH上の外部consoleを解決し、再帰委譲を拒否し、Python関連の混入環境変数を除去して `execve` します。したがって、単なる旧runtimeの残骸ではありません。一方、外部consoleを直接使う経路はshimを必要としません。

shell補完も標準の `spec-dock` 名へ登録されています。少なくとも確認したBash/Zsh生成コードは `./spec` を補完の前提にしていません。よって、**「補完のためにrootのsymlinkが必須」という根拠はありません。** 

### 4.4 uninstallとの関係

現行installationは `./spec` を所有資産として列挙していません。一方、shimは既知静的資産なのでuninstallの削除対象になります。したがって、**既存の `./spec → spec-dock/scripts/spec-dock` がある環境でshimをuninstallすると、rootのリンクだけが残り、danglingになる構成です。**

これは今回実行したuninstallの観測ではなく、inventoryと削除境界から分かる帰結です。所有権が不明なrootファイルを勝手に消さない安全性と、互換リンクの後始末が未定義であることを分けて扱うべきです。 

### 4.5 推奨する段階移行

**推奨は、標準入口を外部 `spec-dock` に統一し、`./spec` の新規生成は追加せず、既存リンクの扱いだけを明文化することです。**

最初に現行docs・rules・bootstrap・CI・利用スクリプトを外部console基準へ揃えます。この段階ではshimと既存リンクを残し、利用者のコマンド履歴や外部automationを急に壊しません。現在のrulesにはshimを保証された実行経路とする文言があるため、shimを先に消す順序は避けます。 

次に、このrepositoryの追跡済み `spec` を将来のPRで廃止するか判断します。廃止する場合も、他consumerの同名通常ファイル、別targetのsymlink、ユーザー改変を一律に削除しません。uninstall後の互換リンクについては、正確なlink targetを確認した明示的な整理手順を用意する方が、汎用symlink管理機構を新設するより小さな変更です。

shim自体の廃止はさらに別段階です。inventoryから消すだけでは既存consumerのshimは退役しませんし、現行のretired path許可範囲はversion fileと旧runtime Pythonに限定されています。将来shimをinstallerで退役させるなら、その所有権・既知bytes・退役path検証・backup・互換テストまで、独立した変更として設計する必要があります。

---

## 5. skill配置3案の比較と推奨

### 5.1 現行実装と外部製品の機能を混同しない

**現行SpecDockのinstallationはproject-localです。** 明示したGit worktreeのroot `.agents/skills/` に静的資産を配置します。ユーザー共通skill directoryへ導入する経路は、確認したinstaller・inventoryにはありません。外部CLIをユーザー共通のtool環境へ導入することは、skillもglobalへ導入することを意味しません。 

一方、現在のCodex公式文書は、repo内の `.agents/skills` とユーザー共通の `$HOME/.agents/skills` を区別しています。repo内ではCWDからrepository rootまでを探索し、同名skillを自動統合せず、両方がselectorに出る場合があると説明しています。**「localが必ずglobalを上書きする」と仮定してはいけません。** [developers.openai.com](https://developers.openai.com/codex/skills)

Claude Codeの公式文書では主な配置先が `.claude/skills`／`~/.claude/skills` で、同名のenterprise・personal・project間ではenterprise、personal、projectの順です。Codexと配置先・衝突規則が同じではありません。したがって、SpecDockの現在の `.agents` 配置を、そのまま全agent providerの共通導入保証とは扱えません。[Claude](https://code.claude.com/docs/en/skills)

### 5.2 三案の比較

以下は**設計比較・推奨**であり、未実装のglobal導入を現在の機能として説明するものではありません。

| 比較軸 | A. project-local | B. user-global | C. global入口＋local project情報 |
|---|---|---|---|
| **複数repo／worktreeの更新コスト** | 共通手順の更新も各worktreeへ明示適用が必要。管理対象が増える。 | 共通skillはユーザー単位で更新できる。複数ユーザー・端末・providerには別配布が必要。 | 共通入口はユーザー単位。project情報だけrepo内で保守できる。 |
| **複数CLI版・schema互換** | repoに対応する手順を固定しやすい。ただし実際にPATHで選ばれるCLIまで固定されるわけではない。 | 一つの新版skillが旧CLI／旧projectへ誤った手順を出す危険が大きい。 | 入口がCLI版・公開JSON・workspace宣言を確認し、localの互換条件と照合する設計にできる。 |
| **チーム再現性** | commitされたskill内容をチームで共有しやすい。 | 各人の導入状態に差が出る。cloneだけでは再現しない。 | localに必要版・導入案内・project規則を残せるが、global側の導入確認が必要。 |
| **CI** | agentを使うCIならrepo内skillを利用しやすい。通常CLI検証自体は外部packageを明示導入する。 | 開発者のHOMEをCIが持つと仮定できない。CI側の明示導入が必要。 | CLIと共通skillをCIで固定導入し、local情報を検査する形にできる。 |
| **新規cloneの発見性** | commit済みのskillが利用者の目に入りやすい。 | 未導入ユーザーには入口そのものがない。 | local AGENTS／READMEに入口・必要条件・不足時の説明を置ける。 |
| **複数agent provider** | providerごとの配置資産がrepoに増える可能性。 | providerごとにglobal配置・発見規則の確認が必要。 | 共通の手順内容と、薄いprovider別入口を分けやすい。 |
| **同名衝突** | ユーザー既存global skillと衝突し得る。 | 既存project-local版と二重発見・優先順位問題が生じる。 | localは同名SKILLではなくproject情報にし、共通skillの二重配置を避けやすい。 |
| **アンインストール・復旧** | worktreeごとに既知資産を保全・退役できる。 | 一つの削除・更新が全projectに効く。復旧もユーザー共通になる。 | global入口とlocal情報を独立して復旧できるが、片方だけ残った状態の説明が必要。 |
| **誤操作** | repo規則は見つけやすいが、古いskill＋新CLIの組合せに注意。 | 別repoにも同じ手順を適用しやすく、対象混同を防ぐ必要がある。 | exact project bindingと互換確認を入口に集約できる。自動fallbackは設けない。 |
| **保守負担** | 実装は最も単純。共通文書の複製更新が負担。 | 配置は単純でも、版管理・衝突・チーム配布が運用へ移る。 | 初期設計は増えるが、共通手順とproject固有事項の責務が最も明確。 |

### 5.3 推奨

**当面はAを維持し、将来案はCを第一候補とします。Bへの全面移行は勧めません。**

Cでは、global側にCLI操作の共通手順、公開JSONの解釈、安全な失敗時の扱いを置き、local側にrepository固有のcanonical docs、承認済み計画、human merge gate、bootstrapの意味、必要なCLI／skill互換条件を残します。local情報は可能なら既存のAGENTS・README・正本文書を使い、新しい状態台帳やproject registryは作りません。

この案の重要点は、**「global skillがlocal skillを上書きする」構造にしないこと**です。共通skillは一つの入口、localはその入口が読むproject情報とします。これなら同名skillの優先順位に依存せず、複数providerにも責務を説明しやすくなります。

ただし、互換確認を「最新版なら何でも動く」という文章だけで済ませてはいけません。必要なのは、少なくともCLIの実際の版、`specdock.cli/v2` の期待するdata形状、workspace schema／writer protocol、必要leafとoptionの対応表です。現在のruntimeにもwriterの受入境界があるため、それを尊重し、skill側で旧CLIへの無検証fallbackや自動migrationを追加しない方針が適切です。 

### 5.4 二つのskillでglobal化の難しさは異なる

**通常の `spec-dock` skillは先行検証に向いています。** 現在の追跡資産はSKILL.mdのみで、専用scriptや `agents/openai.yaml` はありません。YAMLはCodexで任意のmetadataなので、欠落自体は不具合ではありません。主な課題は対象projectの固定、CLI版との整合、project規則の読込みです。 [OpenAI Developers](https://developers.openai.com/codex/skills)

**Grillは一段慎重に扱うべきです。** YAMLの `allow_implicit_invocation: false` は、明示起動だけにするSKILL本文と一致しています。Codex公式の当該policyの意味とも整合しています。外部の `grilling`／`domain-modeling` が必要であること、activeをselectorとして使わないこと、read-only調査後に一件だけArtifactを残すことも、意図された制約です。  [OpenAI Developers](https://developers.openai.com/codex/skills)

finalizerはprovider runtimeをimportせず、明示されたrepo rootとArtifact pathを使う独立したscriptです。identity照合、nofollowの親探索、CLI生成prefixの保持という契約も残っています。しかしSKILL本文の起動例はrepo内 `.agents/...` を前提にしています。global化では、**scriptの実体pathをskill側から、書込み対象rootをproject側から、それぞれ独立に解決する修正**が必要です。 

なお、Codexがsymlinked skill folderを発見できることと、SpecDock installerがそのsymlink経由の管理を許すことは別です。現行installerは親directoryのsymlinkやredirectを拒否するため、`.agents` をglobal directoryへ単純にリンクして現行updateを継続する方法は、安全境界と衝突します。[developers.openai.com](https://developers.openai.com/codex/skills) 

---

## 6. 適切な日常運用と導入・更新フロー

### 6.1 最初に「何を更新するのか」を決める

現在の運用で最も重要なのは、次の四つを混同しないことです。

| 対象 | 更新・確認の単位 |
|---|---|
| provider source | `src/spec_dock/runtime` と `src/spec_dock/assets` の開発変更 |
| 実行CLI | worktree外の、実際にPATHで選ばれるinstalled package |
| consumer静的資産 | 明示したworktreeのdocs・templates・system・skills・shim等 |
| 直接作業記録 | そのworktreeのignoredな `.agent/work-target/` |

source編集やbranch切替はinstalled packageの更新ではなく、package更新は各worktreeの静的資産更新でもありません。また、静的資産が一致してもactive recordの正しさは証明されません。これは現在のskill自身が説明している境界で、維持すべき運用です。

日常の確認は、外部consoleの所在・版、明示worktreeのinstallation状態、直接対象、必要なScopeを順に観測します。以下は実行例であり、今回は実行していません。

```sh
PROJECT=/absolute/project

command -v spec-dock
spec-dock --version
spec-dock help

spec-dock installation show --target "$PROJECT" --json
spec-dock --project "$PROJECT" active show --json
spec-dock --project "$PROJECT" scope show iss-00123 --json
```

Scope番号は実際の対象に置き換えます。通常のScope問い合わせに裸のGitHub番号やURLを代入せず、完全Scope IDまたは完全な `gh:` refを使います。

### 6.2 新規導入と「既に資産があるclone」を分ける

新しい、まだ配布先ファイルがないGit worktreeには、外部package導入後に `installation init ABS --dry-run --json`、続いて許可された本適用を行います。`init` は既存配布先を上書きしない契約です。**既に `spec-dock/` や `.agents` がcommitされているcloneで、毎回initし直す運用にはしません。** まず `installation show` で分類し、必要ならupdateへ進みます。

packageはレビュー・試験済みのwheelを明示して導入するのが、この刷新の意図に合います。`uv tool` の環境更新・再導入はpackage側の操作であり、tool環境を手作業のpip操作で混ぜて直す運用は避けます。複数版が必要な場合も、worktree内runtimeを復活させず、別の外部環境と実際に使うconsoleを明示する方が境界を保てます。 [Astral Docs](https://docs.astral.sh/uv/concepts/tools/)

### 6.3 旧writerからの移行は、静的更新とは別

旧schema3 writerでは、旧writer・自動起動を停止し、実体の外部保全と復元確認を先行させます。その後、raw legacy診断、writer宣言の明示migration、静的資産のupdateを別操作として扱います。

```sh
spec-dock --project "$PROJECT" workspace doctor --raw --legacy --json

spec-dock --project "$PROJECT" workspace migrate \
  --to-schema 3 \
  --to-writer-protocol specdock.worktree-writer/v1 \
  --dry-run --json

# 旧writer停止・対象・保全先を確認し、本適用が許可された場合
spec-dock --project "$PROJECT" workspace migrate \
  --to-schema 3 \
  --to-writer-protocol specdock.worktree-writer/v1 \
  --backup-dir /absolute/new-migration-backup \
  --confirm-old-writers-stopped --yes --json

spec-dock installation update --target "$PROJECT" --dry-run --json
spec-dock installation update --target "$PROJECT" \
  --backup-dir /absolute/new-static-backup --yes --json
```

この流れは、旧activeの自動採用や旧journalの再開ではありません。新規直接対象の取得は新しいStartへ戻します。schema3未満や未知protocolを、この手順で黙って変換できると説明してはいけません。 

unknown改変でstatic updateが停止した場合も、hashを無理に合わせたりproviderファイルを直接上書きしたりするのではなく、改変の所有者と内容を確認してmanual mergeへ戻します。既知資産だけを保全・変更する現在の境界を維持します。 

### 6.4 日常の作業開始・中断・完了

新branchへ進むStartでは明示base、既存branchを再利用するStartでは明示branchを使い、baseを併用しません。単なる資料閲覧は `scope show` とcanonical docsの読取りで足り、閲覧のために `active set` で新規対象を取得しようとしません。新しい直接対象を取得する入口はStartです。

中断・引継ぎと完了も分けます。`active clear` は選択の解除、`scope close` は完了状態の操作、`work finish` は完了確認と捕捉した直接記録の解除です。Finish成功をcommit・test・push・PR・merge完了の代用にはしません。Syncも保存物の再構築ではなく観測なので、古いdashboard等が更新されることを期待して繰り返さない運用が適切です。 

`worktree bootstrap` はproject-ownedなbootstrapの実行です。CLI導入、静的資産更新、writer migrationの別名ではありません。`make init` の中身を確認し、SpecDockがそのproject固有処理の安全性を自動保証すると考えないことが必要です。 

### 6.5 Issue 413とAGENTSの現在状態

マージ済みmainであることは確認済みですが、それだけで正式なScope #413 import／Start、利用者のpackage更新、全linked worktreeの移行を完了扱いにはできません。

ユーザー提供のempty active／SCOPE_NOT_FOUND観測が現在も続いている場合は、明示されたrecovery planning packを読むことと、consumer内の正式Scopeを解決できることを分けます。**計画packを読めたからwork start済み、GitHub #413があるからconsumer Scopeもある、とはしません。** AGENTSの修正でも、この区別を残すべきです。 

---

## 7. 独立した後続Issue候補、順序、完了条件

以下はIssue候補であり、GitHub上には作成していません。

| 順序 | Issue候補 | 対象・境界 | 完了条件 |
|---|---|---|---|
| **1** | **現行の復旧診断と実行例を修正する** | SD-OPS-001〜004。旧metaの案内、README確認flag、selector文法、Sync説明。機能拡張はしない。 | 文書例がstub環境で成立。旧meta同居時に保護データ不変。通常selectorとimport refの正負例が一致。配布資産はinventoryとfresh consumerまで検証。 |
| **2** | **マージ後の運用入口と公開説明を整理する** | SD-OPS-005・007。AGENTSとGitHub About。履歴packは保存する。 | commit上のmerge事実、日時付きの過去観測、未再確認の実環境状態が分離される。現在の入口から旧方式へ誘導しない。 |
| **3** | **補完候補をleafの受付条件へ合わせる** | SD-OPS-006。Bash/Zsh/Fishの候補生成とテスト。 | 読取leafへの `--yes`、Start以外への `--lock-timeout` 等の無効候補が消える。全44 leafとcontext-free性を維持。 |
| **4** | **互換入口とuninstallの方針を明文化する** | root `./spec` と配布shimを別々に扱う。自動一括削除を追加しない。 | fresh initでroot specを作らない明示テスト、既存リンク互換、uninstall後の扱い、別target／通常ファイル／改変ファイルの保護が整理される。 |
| **5** | **公開経路から外れた旧API・テストを関数単位で整理する** | 旧presentation、旧writer helper等。共有readerや保全互換を巻き込まない。 | 現在の呼出元一覧と削除理由を記録。必要な保証は公開CLIテストへ移し、未使用関数とその専用旧テストだけを退役。検索hitの一括置換は禁止。 |
| **6** | **skillの実配置・nested起動を検証する** | 現行project-local方式をまず対象にする。通常skill、Grill、YAML、helper、外部能力の境界。 | fresh consumerのroot／nested CWDで確認。Grillは実際に配布されたhelperを使用し、一件のArtifactだけを残す。partial時に再作成しない。 |
| **7** | **global入口＋local情報の限定実験を行う** | まず通常skillを対象。新しい状態台帳やCLI全面再設計はしない。Grillは後段。 | 二つ以上のrepo／worktree、異なるCLI互換条件、同名衝突、fresh clone、CI、削除・復旧を検証。現行local方式へ戻せる。採用判断までは既定配置を変更しない。 |

1〜3は現在利用者への誤誘導の修正です。4〜7は互換方針・保守整理・将来設計を含み、同じ修正PRへ混ぜない方がよいと判断します。

特に配布テストは既に、fresh consumerのparityと実wheelの構成を検査しています。これを捨てて新しい巨大な検査制度を作るより、**文書例の非対話条件、補完の負例、rootリンク非生成、配布されたskillからの起動**という不足している境界を追加するのが最小です。  

---

## 8. 未決の人間判断

| 判断事項 | 決める内容 |
|---|---|
| **`./spec` の互換期間** | このrepositoryの追跡済み短縮名を残すか、段階的に廃止するか。新規生成を追加する必要性は今回確認されていません。 |
| **薄いshimの位置づけ** | 長期の互換入口として残すか、docs・automation移行後に退役させるか。rootリンクの判断とは別です。 |
| **共通skillの配布単位** | チーム再現性を重視してlocalを既定にするか、限定利用者向けにglobal入口を追加するか。単独利用とチーム利用を同じ既定にする必要はありません。 |
| **対応するCLI／skillの組合せ** | どのCLI版・JSON契約・workspace protocolを同じskillで支えるか。非対応の組合せは明示停止とするか、版別の入口を用意するか。 |
| **project固有規則の正本** | global入口が読むAGENTS・canonical docs・承認計画の場所と優先関係。project情報をglobal skill本文へ複製しない方針が望まれます。 |
| **実環境rolloutの認定範囲** | 0805以外のworktree、各利用者のtool環境、正式Scope #413の登録・開始について、どの現物を誰が確認するか。マージ済みという事実では代替できません。 |
| **未知の旧資産の扱い** | 改変済みskill、旧runtime拡張、別targetのsymlink等をどこまで製品が自動退役させるか。現行の保全優先を緩める判断は独立させるべきです。 |

**今回の刷新自体を全面的にやり直す必要は確認していません。** 外部CLI、worktree単位の静的投影、直接対象記録という主要な境界は、現行source・資産・テストに反映されています。優先すべき順序は、現在の復旧案内と実行例を直し、運用状態の時点を整理し、その後に `./spec`／shimの互換方針とskillのglobal化を独立して判断することです。
