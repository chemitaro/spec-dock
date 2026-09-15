---

kind: "readiness-analysis"
issue: "iss-00395"
title: "Issue #395 LunaMax Implementation Readiness Analysis"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_branch_tip: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
verified_branch_tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
current_verdict: "実装不可"
revised_pack_state: "条件付き実装可能"
implementation_allowed: false
owner_decisions_required: []
authority: "advisory-analysis"
---

# Issue #395 LunaMax実装準備度分析

## 1. 結論

**現行のDesign、Plan、LunaMax handoffをそのまま渡す場合の判定は「実装不可」です。**

理由は、仕様上のProduct修復方針そのものではなく、実行計画と証拠契約に、GREENを誤認できるP0欠陥が残っているためです。特に、現行`tests/conftest.py`では`tests/cli_runtime/`と`tests/integration/`がfull-regression laneへ分類され、`--run-full-regression`なしではskipされます。しかし現行Plan/Handoffの複数の重要gateは、そのflagなしで対象testを実行し、「pass」と扱っています。このままではProduct source、dogfood candidate parity、post-merge B1の一部を実行せずに通過できます。

本packの修正版Design、Plan、handoffは、下記P0/P1を除去したため、**canonical文書へ反映し、clean pushed exact SHAに対する独立spec reviewがpassし、明示的なimplementation dispatchが発行された後に限り「条件付き実装可能」**です。本pack自体は実装許可を与えません。

## 2. 根拠identityと分析範囲

### 2.1 GitHub connectorで確認したrepository identity

| 項目              | 確認値                                                                       |
| --------------- | ------------------------------------------------------------------------- |
| Repository      | `chemitaro/spec-dock`                                                     |
| Branch          | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Branch tip      | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| Tree            | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                                |
| P392 entry SHA  | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| P392 entry tree | `190bc566a18cd84813c4b7c043f8724e275cb55d`                                |

GitHubの対象branchを直接取得し、default branchへfallbackせずに上記tip/treeを確認しました。

### 2.2 添付local worktree bundle

| 項目              | 値                                                                  |
| --------------- | ------------------------------------------------------------------ |
| Input file      | `attachments-bundle.txt`                                           |
| Bytes           | `945170`                                                           |
| SHA-256         | `ec09f2a7327f110625cbc333ab232d31ad5744ce13e34e17daa6a210e70e24e2` |
| Contained files | 28                                                                 |

主要Product/test/ledger/verifier/workflow fileについて、bundleから復元したbytesのGit blob IDを計算し、現行Designが固定するexact blobおよびGitHub exact treeと照合しました。少なくとも次は一致しています。

* `full-regression-ledger.json`: `f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5`
* `full-regression-timing-weights.json`: `bdeeb6238609c38085aaed8023b78319a3dd0c6d`
* `tests/conftest.py`: `d574c3a3e7a09c34f708c576a3b41a3b35772072`
* `scripts/quality/verify_full_regression.py`: `d01045add90b6e98b58fd210d2ade0d340f7b576`
* `src/.../infra/git_cli.py`: `b0e34dffb3650e7cb3d202e1db243e4c75fea341`
* Row 1、3–15対象test files: Design記載blobと一致
* `.github/workflows/provider-ci.yml`: `db1adceda41e7927a9dd7e5f7934d3f88152bf06`
* `.github/workflows/provider-full-regression.yml`: `259c7988f3cf13ed4484be60bc200e01680b95f2`

### 2.3 実施した検査

* Issue Requirement、Design、Plan、handoff、manifestの全文照合
* Parent Epic Requirement/Design/Plan、failure disposition register、P392 ADRの整合確認
* Product source、test fixture、ledger、timing、verifier、pytest policy、workflowの静的解析
* 添付Python sourceのcompile確認
* ledger 15/14/1、row order、row 2 successor、timing 243の機械確認
* Plan/Handoff内bash blockの`bash -n`
* Markdown front matterのYAML parse
* commandと現行CLI/API/path/symbolの静的照合

この分析環境からGitHubへ通常の`git clone`はできなかったため、full suiteやPlan全commandは実行していません。GitHub connectorでexact sourceを読み、添付bytesのblob identityを照合した静的実行可能性分析です。

## 3. P0課題

### P0-01 — heavy testが実行されずskipされるgateがある

**事実:** `tests/conftest.py`は`tests/cli_runtime/`と`tests/integration/`をfull-regression laneへ分類し、`--run-full-regression`がない場合はpolicy skipを付与します。

**現行Plan/Handoffの誤り:** 次の重要commandに`--run-full-regression --full-regression-shard`がありません。

* Provider source focused gateの`tests/cli_runtime/test_import.py`、`test_runtime_import_s10.py`、`test_runtime_shell_s11.py`
* Dogfood parity node `test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical`
* Ordinary/lifecycle/package gate中の`tests/integration/test_provider_lifecycle_dogfood.py`
* Exact clean candidate rerun中の同test
* Post-merge B1中の同test

**影響:** pytest exit 0でも、対象testはpassではなくskipです。Product source GREEN、dogfood parity、post-merge B1を偽陽性にできます。

**修正:** heavy pathを直接指定する全commandに、必ず次を付けます。

```text
--run-full-regression --full-regression-shard
```

ordinary laneの`uv run pytest`だけは、現行policy skipを意図的に保持します。

### P0-02 — ledgerのhistorical fieldsを壊してもfull verifierがGREENになり得る

**事実:** 現行ledger transition scriptは、active node集合とrow 2だけを強く確認し、rows 1、3–15の`fixed_point_signature_sha256`、`current_signature_sha256`、historical status、disposition、top-level historical metadataの不変をbefore/after比較しません。

`evaluate_baseline`は`resolved/fixed-in-place` rowについてnormal passだけを評価し、historical signatureは照合しません。

**影響:** agentがledgerのhistorical signatureやstatusを誤編集しても、14 nodeがpassすればfull verifierはGREENになり得ます。I395-RQ-007とregisterのhistorical preservationを破ったままB2を宣言できます。

**修正:** ledger変更前にfull parsed payloadを外部evidenceへ保存し、変更直前にbyte-semantic equalityを再確認します。遷移後は、14 rowsについて許容差分を`lifecycle: active -> resolved`と`resolution_mode: fixed-in-place`の追加だけに限定し、row 2とtop-level payloadを完全一致させます。

### P0-03 — post-merge B1がcurrent required Provider CIを証明していない

**事実:** current Provider CIはordinary/lintに加え、Linux/macOS matrixでprovider lifecycle、distribution cutover、platform coordination、packaged distribution parityを実行します。

**現行Planのpost-merge B1:** ordinary、provider lifecycle unit、dogfood、lint、validate、full verifierだけで、distribution cutover、platform suite、`test_epic_00343_distribution.py`がありません。さらにdogfood commandはP0-01によりskipです。

**影響:** exact integration tipでcurrent required gateが成立したというB1主張を裏付けません。

**修正:** post-merge exact tipでProvider CIと同じcommand群をすべて実行し、PR head treeとmerge treeの一致も検証します。current required check receiptはPR head SHAへ、local rerunとfull verifierはpost-merge full SHAへ束縛します。

### P0-04 — 実装許可falseをshell mutation gateが強制していない

**事実:** 現行PlanのStep 0は`SPEC_FREEZE_SHA`だけを必須化し、`IMPLEMENTATION_AUTHORIZED=true`、spec review target/status/P0/P1、review receipt identity、concurrent writer assertionを機械確認しません。Handoffの「read-only preflight」は逆に冒頭で`IMPLEMENTATION_AUTHORIZED=true`を要求し、read-only preflightとmutation gateが混線しています。

**影響:** Planだけを実行したLunaMaxが、`実装開始許可: false`の状態でもProduct/test/ledger変更へ進めます。逆に、許可前に安全なidentity preflightだけを行う経路も明確ではありません。

**修正:** read-only preflightとmutation authorization gateを分離します。Product/test/ledger/dogfood変更の直前に、exact review target、receipt SHA-256、review pass、P0/P1=0、implementation authorization、concurrent writer absenceを必須環境値として検証します。

## 4. P1課題

### P1-01 — grouped REDがrow単位の初回失敗を証明しない

Rows 4–11とrows 1、13、14、15をまとめて実行し、command全体のexit 1と一つのgrep matchだけを確認しています。一部rowが想定外にpassまたは別原因でfailしても通過できます。

**修正:** 14 rowsを一件ずつ実行し、rowごとのexit、expected failure pattern、log SHA-256、entry verifier violationを記録します。Row 12だけはnode自身がGREENで、active-ledger evaluatorの`coverage_mismatch`を最初のREDとします。

### P1-02 — repository identity変数が未使用

`EXPECTED_REPOSITORY=chemitaro/spec-dock`を設定していますが、origin URLからowner/repoを検証していません。同名branch/SHAだけを見ています。

**修正:** credential-bearing URLを出力しない独立parserでorigin fetch URLをslugへ正規化し、`chemitaro/spec-dock`と一致させます。

### P1-03 — elaboration input ancestryがPlanで未検証

PlanはP392のancestor性だけを確認し、`ELABORATION_INPUT_SHA -> SPEC_FREEZE_SHA`のancestor性を確認しません。そのうえspec pack diffにtriple-dotを使っています。

**修正:** P392 -> elaboration input -> spec freezeの二段ancestorを確認し、diffは明示的なtwo-endpoint diffを使用します。

### P1-04 — full verifier result選択が競合する

共有`spec-dock/.workbench/full-regression`から`find | sort | tail -1`で最新directoryを選びます。別のread-only verifierが並行実行すると別runの`result.json`を取得できます。

**修正:** 各runへprivateで空の`--artifact-dir`を渡し、そのroot配下に`result.json`がexactly oneであることを確認します。

### P1-05 — `/private/tmp`固定とpredictable log path

`TMPDIR=/private/tmp`はmacOS依存です。Linuxではdirectoryが存在しない場合があります。また`/tmp/iss-00395-*.log`はpredictableな共有pathです。

**修正:** writableな`${TMPDIR:-/tmp}`へfallbackし、`umask 077`と`mktemp -d`でprivate evidence directoryを作成します。raw logsはそこへ保存し、配布evidenceにはsanitized summaryとhashだけを載せます。

### P1-06 — publication strictnessの証明が不完全でexact candidateへ再束縛されない

現行diagnosticはcredential-bearing fetch/default pushとclean fetch/foreign push mismatchを確認しますが、clean fetch + credential-bearing pushの拒否を確認しません。またcommit後のexact clean rerunとpost-merge B1で再実行しません。

**修正:** fetch userinfo、push-only userinfo、fetch/push mismatch、clean equal endpointの4 caseを確認し、working tree、exact clean implementation SHA、post-merge exact SHAで再実行します。

### P1-07 — dogfood candidateが「new digest」であることを確認しない

record/markersのdigest equalityと64文字長だけを確認し、projection前digestとの差を確認しません。digest algorithmがchanged runtimeを取り込まなくても通過できます。

**修正:** pre-projection digestを保存し、post-projection digestがlowercase 64-hexで、三者一致かつ旧digestと不一致であることを確認します。update JSON resultのdigestとも一致させます。

### P1-08 — actual protected dataのbefore/after proofがない

lifecycle fixture testsとtracked diffだけでは、actual working repositoryのignored/untracked Workbenchやconsumer dataが不変であることを証明しません。

**修正:** projection直前・直後に`spec-dock/initiatives`、既存Workbench/Artifacts roots、二slotの`SKILL.md`をtype/mode/symlink target/file SHA-256でsnapshotし、exact equalityを要求します。

### P1-09 — exact clean rerunがmanual invariantsを再実行しない

commit後はfull verifierとtest群を再実行しますが、publication diagnostic、row 12 AST/blob guard、ledger immutable proof、no-touch、protected snapshotを同じexact implementation SHAへ再束縛していません。

**修正:** merge-blocking invariantをすべてexact clean SHAで再実行します。

### P1-10 — stop payload schemaがowner decisionとrow 2 driftを表現できない

Plan schemaの`owner_decision_required`は`false`固定ですが、stop conditionにはnew owner decisionが含まれます。また`row_ordinal`が2を表現できません。

**修正:** stop schemaを一つに統一し、`owner_decision_required`をboolean、row ordinalを1–15またはnullとします。

### P1-11 — execution packet fieldとshell variableのmappingが未定義

YAML packetはsnake_case、shellはuppercaseで、どの値を誰がexportするか固定されていません。review receipt target/tree/hashも欠けます。

**修正:** packet schema v2とenvironment mapping tableをhandoffへ収録します。

### P1-12 — local manifestのYAML front matterがparse不能

添付`iss-00395-chatgpt-spec-pack-manifest.md`は`derived_from:`配下で`*`を使っており、YAML aliasとして解釈されparseに失敗します。同manifestの「五Markdown filesのfront matter parse成功」という記述と矛盾します。

**影響:** provenance/static-validation claimを信用できず、spec freeze gateの一部が再現不能です。

**修正:** 本packのmanifestはvalid YAMLを使用します。canonical pack採用時は既存manifestも修正し、再validationが必要です。

### P1-13 — supplied bundleにhuman guide本体がない

現行spec freeze diff gateは`iss-00395-human-guide.html`を含むsix-file packを要求しますが、今回の添付bundleには同HTML本体がありません。既存manifestのhash claimだけでは内容検証を代替できません。

**修正:** canonical spec freeze前にhuman guide bytesを取得し、path、hash、HTML/static contractを再検証します。取得できなければimplementation dispatchを発行しません。

## 5. P2課題

* Row 12 guardが文字列検索中心で、import ASTを厳密に検査していません。Exact blob guardがあるため直ちに誤実装にはなりませんが、修正版ではAST import edgeを検査します。
* `shasum -a 256`へ依存しています。修正版はPython `hashlib`へ統一します。
* Raw verifier resultはabsolute artifact pathを含み得ます。修正版はraw local evidenceとsanitized distribution evidenceを分けます。
* Planとhandoffの大規模重複により、既にpermission gate、stop schema、test flagsがdriftしています。修正版はPlanをnormative execution order、handoffをdispatch/return contractとして責務分離します。
* Current expected outputの一部が自然言語だけで、machine assertionがありません。修正版はexit code、JSON fields、count、hash、path setを機械確認します。

## 6. 要求観点別評価

| 観点                         | 現行評価          | 理由                                                   | 修正版                                 |
| -------------------------- | ------------- | ---------------------------------------------------- | ----------------------------------- |
| LunaMax実行順序                | 不可            | read-only preflightとmutation gateが混線                 | phase A–Nへ固定                        |
| 正確なfile/symbol             | 概ね良好          | Product/test boundaryは正確                             | exact symbolとno-touchを維持            |
| RED再現性                     | 不十分           | grouped REDでrowごとに証明しない                              | 14 row個別RED + row12 evaluator RED   |
| 最小diff                     | 概ね良好          | expected 11 pathsは妥当                                 | 11 pathsをbefore/afterで機械確認          |
| fixture契約                  | 良好            | `copy_scaffolded_tree_at` call shapeは現行portと一致       | exact code shapeを明示                 |
| Product/test harness境界     | 良好            | rows 4–11/selectionはtest側、row3 Product、row12 no-edit | 維持                                  |
| dogfood projection         | 不可            | parity testがskip、new digest/protected data proof不足   | heavy flags、digest delta、snapshot追加 |
| ledger遷移                   | 不可            | historical fields driftを検出しない                        | full payload before/after invariant |
| verification gate          | 不可            | exact clean/manual gatesとpost-merge B1が不足            | exact SHAへ全gate再束縛                  |
| stop condition             | 不十分           | schemaがowner decision/row2を表現不能                      | unified schema v2                   |
| command実行可能性               | 条件付き          | path/APIは概ね現行、TMPDIR/test flagsが不正                   | portable temp、exact lane flags      |
| stale API/path/args        | Product側は概ねなし | `update . --json`、active args、scaffolder portは現行     | blob/AST/CLI guardを追加               |
| simultaneous writer        | 不十分           | booleanだけでscope/identityなし                           | assertion IDとscopeをpacketへ追加        |
| commit/push/PR/human merge | narrativeは明確  | shell authorizationとmappingが不足                       | 三boolean分離、human merge only         |
| unresolved decisions       | Product設計はなし  | operational evidence contractに欠落                     | `owner_decisions_required=[]`維持     |

## 7. Product修復方針自体の評価

現行の原因分類と最小修復方針は、親register、P392 ADR、実装sourceに整合しています。

1. **Row 3:** `_parse_github_repo_slug`のidentity parsingと`origin_github_publication_endpoint`のpublication policyを分離する方針は妥当です。`origin_github_repo_slug`がfetch originのみを読む変更も既存port signatureを保ちます。
2. **Rows 4–11:** `_StubTemplateScaffolder`へcurrent descriptor-bound methodを追加し、production adapterへ委譲する方針は妥当です。本番`execute_create_plan`をobsolete pathへ戻しません。
3. **Rows 1、13、14、15:** retired `--force` / `--no-checkout`をtest observerから除去する方針は妥当です。
4. **Row 12:** current P392 sourceは既に`commands -> application.contracts -> domain`です。Product edit 0、node normal pass、ledger fixed-in-placeだけで閉じる方針が妥当です。
5. **Ledger:** 14 active rowsをresolved/fixed-in-place、row 2をresolved/supersededのまま保持するtargetは親契約と一致します。

したがって、実装不可の原因はProduct設計の未決ではなく、実行・検証・証拠化contractの欠陥です。新しいowner decisionは不要で、`owner_decisions_required=[]`を維持できます。

## 8. 修正版packの成立条件

本packをcanonical Issue資料へ反映した後、次を満たすまでProduct/test/ledgerを変更しません。

1. Canonical Requirement/Design/Plan/handoff/human guide/manifestがclean pushed exact spec freeze SHAへ束縛される。
2. GitHub repository、Issue branch、local HEAD、upstream、remote tipが一致する。
3. P392 -> elaboration input -> spec freeze ancestryとdoc-only diffが成立する。
4. Human guideを含むsix-file packが実在し、static validationがpassする。
5. Fresh independent `chatgpt-spec-review-strict`がtarget SHAに対してpass、P0=0、P1=0である。
6. Separate execution packetが`implementation_authorized=true`とconcurrent writer absenceを明示する。
7. Commit/pushとPR preparationは、それぞれ別booleanで明示される。
8. Human merge authorityを維持する。

## 9. 残余リスクと未確認事項

* この分析ではfull repository checkoutを取得できず、pytest、full verifier、SpecDock validate、lifecycle updateを実行していません。実装dispatch前のread-only preflightで実測が必要です。
* 添付bundleにはhuman guide本体がありません。Canonical spec freeze前に別途検証が必要です。
* GitHub branch tipは確認済みですが、ユーザーlocal worktreeのclean status、upstream、active pointer、uncommitted file setは外部から直接観測していません。
* Spec review、implementation authorization、code review、Final Quality Gate、human merge、B1/B2は未実施です。
* Actual runner OSとfilesystem capabilityは未確認です。修正版はportable temp pathを使いますが、descriptor/no-replace capability failureではstopします。

## 10. 実施していない操作

Product source、tests、ledger、timing、policy、workflow、managed metadataを変更していません。Commit、push、PR作成・更新、merge、revert、Issue closeも行っていません。
