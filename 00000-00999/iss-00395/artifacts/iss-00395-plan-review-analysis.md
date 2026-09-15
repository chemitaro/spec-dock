---

kind: "implementation-readiness-analysis"
issue: "iss-00395"
title: "Issue #395 Plan/Handoff厳密評価とTDD実装準備版への改訂判断"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
verdict_current_pack: "do-not-implement-as-is"
verdict_revised_pack: "review-required-before-dispatch"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-analysis"
---

# Issue #395 Plan/Handoff厳密評価とTDD実装準備版への改訂判断

## 1. 結論

**現行Design、Plan、LunaMax handoffのままLunaMaxへ実装を委ねるべきではありません。先に本packのような、コードを埋め込まないTDD実装準備版へ改めるべきです。**

この判定は、Issue #395のProduct修復方針を否定するものではありません。Row 3のread-only repository identityとpublication policyの分離、rows 4–11のdescriptor-bound test-double seam、row 12のno-edit guard、rows 1・13・14・15のobserver更新、dogfood projection後のledger terminalizationという方向は、verified commitの実装と親契約に整合しています。

問題は、現行Planとhandoffが「実装判断を支援する仕様」ではなく、実装コード、テスト実行器、証拠生成器、Git操作手順、PR操作手順、post-merge検証器を一つのMarkdownへ埋め込んだ巨大な実行スクリプトになっている点です。これにより、TDDで各段階に判断すべき失敗層、最小変更、保護すべき振る舞い、停止理由が大量の固定コードに埋没しています。

したがって、現時点の判定は次のとおりです。

| 対象                  | 判定   | 理由                                                               |
| ------------------- | ---- | ---------------------------------------------------------------- |
| Product修復の原因分類      | 採用可能 | 親register、現行実装、P392契約と整合するためです。                                  |
| 現行Requirement       | 要整理  | 受入条件は有効ですが、実装・運用gateの詳細が混入しています。                                 |
| 現行Design            | 要整理  | 境界は概ね正しい一方、具体コード形状と実行手順まで降りています。                                 |
| 現行Plan              | 全面改訂 | 実装コードと巨大なBash/Python断片がTDDの判断構造を置換しています。                         |
| 現行handoff           | 全面改訂 | Planの大部分を複製し、authorityとdispatch contractが埋没しています。                |
| 現状のLunaMax dispatch | 不可   | exact-tip independent spec reviewと明示的実装許可以前に、仕様pack自体を改訂すべきためです。 |

## 2. 分析のauthorityと範囲

GitHub connectorで、repository、target branch、branch-tip SHAを直接確認しました。対象は次のexact commitです。

| 項目                       | 値                                                                         |
| ------------------------ | ------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                     |
| Branch                   | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Verified tip             | `25b33cfaf6214d8c78494f0e0520ef8738bc862f`                                |
| Verified tree            | `ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8`                                |
| Parent elaboration input | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| P392 entry               | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |

対象commitのRequirement、Design、Plan、handoff、Epic Requirement/Design/Plan、P392 ADR、Post-#387 Regression Baseline Register、Rolling-Wave Contract、Epic Integration Branch Contract、Provider Lifecycle Wire Contract、AGENTS.md、および関連Product/test sourceを読みました。添付bundle中の主要文書bytesは、同commitのGit blob IDと一致しています。

本分析は静的な仕様・実装整合性評価です。pytest、full verifier、lifecycle update、SpecDock validate、commit、push、PR、mergeは実行していません。

## 3. 定量的な文書構造の問題

Verified bytesを機械集計した結果は次のとおりです。

| 文書          |   総行数 | fenced block数 | fenced block本文行 | 本文比率 | 主なblock                                |
| ----------- | ----: | ------------: | --------------: | ---: | -------------------------------------- |
| Requirement |   319 |             0 |               0 |   0% | なし                                     |
| Design      |   505 |             9 |              55 | 約11% | text、Python、JSON                       |
| Plan        | 3,961 |            62 |           2,852 | 約72% | Bash 51、Python 2、JSON 1、text 8         |
| Handoff     | 2,809 |            69 |           1,490 | 約53% | Bash 28、Python 2、JSON 4、YAML 1、text 34 |

Planとhandoffには、multiset基準で1,095行の完全一致するnonblank lineがあり、3行連続の同一shingleも863件あります。これは単に両文書が同じ要件を参照しているという範囲を超え、同じ実行ロジックを二つのauthorityへ複製している状態です。

Plan内には、最大147行の個別RED runner、147行のpublication security diagnostic、145行のstop JSON schema、134行のledger baseline validator、125行のentry verifier validator、124行のauthorization validator、119行のprotected-data snapshot helper、118行のrow 12 AST/blob guardなどが埋め込まれています。Handoffにも同種のrunner、receipt validator、schema、commit/push手順が再掲されています。

この構造は、Markdownを変更しただけで実装ランナーの挙動が変わる一方、そのランナー自体にunit testがないという逆転を生みます。検証可能性を高める意図で追加されたコードが、別の未検証コード面を増やしています。

## 4. 観点別の厳密評価

### 4.1 コード断片の過剰さ

現行Planは、次の三つを同時に担っています。

1. 何を実現するかという仕様
2. どの順序で判断するかというTDD計画
3. 具体的にどう自動実行・証拠化・commit・push・PR作成するかというrunbook

この混在は不適切です。Rolling-Wave ContractがIssue詳細化へ求めるのは、exact file/symbol、test ownership、first RED、expected result、ordered steps、stop/returnです。これは「判断可能な詳細」を要求するものであり、完成したPython/Bash実装をMarkdownへ埋め込むことを要求していません。

特に次はPlanの責務外です。

* `_StubTemplateScaffolder`へ追加するmethod bodyの完成形
* 13 rowsを実行するPython runnerの完成形
* publication matrixを構築するPython diagnosticの完成形
* protected-data snapshot utilityの完成形
* ledgerを書き換えるPython programの完成形
* review receiptをparseするPython programの完成形
* commit messageと`git add`対象を固定したcommit/push script
* `gh pr create`と`gh pr edit`の固定script
* post-merge checkoutとB1/B2の実行script

これらは実装者が現行repository API、test harness、runtime結果を確認したうえで作るか、既存toolへ委譲すべき実行物です。仕様に埋め込むと、repositoryが少し変化しただけで仕様本文がstale implementationになります。

### 4.2 TDDの粒度

現行Planには「個別RED」「GREEN」「ledgerを最後に変更する」という正しい骨格があります。しかし、粒度は次のように整理すべきです。

| TDD unit        | 適切な粒度                                                                            | 現行の問題                                                   |
| --------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Rows 4–11       | 一つのtest-double seam変更、8 behaviorの独立GREEN                                         | 8 rowsのrunner実装が中心となり、seamの意味が薄れています。                   |
| Rows 1・13・14・15 | 一つのobsolete observer migration、4 behaviorの独立GREEN                                | exact replacementとrunnerが前面に出て、保持assertionの理由が後景化しています。 |
| Row 3           | test-first security observation → identity/publication boundary修復 → matrix GREEN | 完成コード断片が先に示され、既存実装から最小修復を導く余地を狭めています。                   |
| Row 12          | evaluatorのcoverage REDとnodeの現行GREENを分離するguard                                    | 「RED=失敗test」と誤認しやすく、no-edit判断が長いguard scriptに埋没しています。   |
| Ledger          | 15 node normal pass後の最後のsemantic transition                                      | 書換えprogramが仕様の中心になり、遷移前提が見えにくくなっています。                   |

TDDの各stepでLunaMaxに必要なのは、「何を観測し、どの失敗層なら続行でき、どの変更面を最小とし、どの振る舞いがGREENなら次へ進めるか」です。具体的なmethod bodyやshell loopではありません。

### 4.3 仕様と実装手順の責務分離

推奨する責務は次のとおりです。

| 文書          | 責務                                                                 |
| ----------- | ------------------------------------------------------------------ |
| Requirement | 利用価値、受け入れる振る舞い、禁止される結果、最終受入条件                                      |
| Design      | layer境界、責務、不変条件、状態遷移、testable contract、write/read/no-touch surface |
| Plan        | TDDの実行順序、各stepのRED・最小変更意図・GREEN・証拠・停止条件                            |
| Handoff     | dispatch前提、authority、許可範囲、返却物、terminal point、human boundary        |
| Manifest    | 配布内容、source identity、byte/ZIP contract                             |

現行handoffはPlanの短いdispatch contractではなく、Planをほぼ再実装しています。どちらかだけが修正されると、test flags、stop schema、file set、evidence fields、post-merge責務がdriftします。HandoffはPlanを参照し、実装agentへ「何が渡され、何を返すか」だけを固定すべきです。

### 4.4 既存リポジトリの実装パターンとの整合

Verified sourceから、修復面は次のように確認できます。

* `infra/git_cli.py`では、`_parse_github_repo_slug`がuserinfoを理由にidentity解析を拒否し、`origin_github_repo_slug`がpublication endpointへ委譲しています。Row 3の原因分類は正しいです。
* `TemplateScaffolder` protocolにはdescriptor-bound `copy_scaffolded_tree_at`があり、production infraにもcollision、binary/text、mode、shebangを扱う実装があります。一方、test doubleだけが旧methodしか持ちません。Rows 4–11はtest double側の追随が正しいです。
* `commands/active.py`が公開する`active set`引数はpositional target、`--id`、`--github-issue`であり、`--force`と`--no-checkout`はありません。Rows 1・13・14・15はobserver更新が正しいです。
* `commands/new.py`はapplication contractからcatalogueを読み、application contractがdomain catalogueをre-exportしています。Row 12は既に正しいdependency directionであり、Product edit 0が正しいです。
* AGENTS.mdはprovider sourceを先に変更し、dogfood workspaceをgenerated consumerとして更新する方針です。Row 3のsource-first、projection-later順序は妥当です。

したがって、新しいPlanは既存patternを説明し、最小変更の境界を示すべきですが、method bodyを固定する必要はありません。

### 4.5 検証可能性

現行packが改善した次の点は維持すべきです。

* selected heavy testは`--run-full-regression --full-regression-shard`を伴い、skipをGREENと扱わない
* rowごとのfirst REDを観測する
* row 12はentry evaluator REDとnode GREENを分離する
* private artifact rootを使う
* ledger before/afterのhistorical preservationを別に証明する
* working-tree evidenceとexact clean SHA evidenceを区別する
* row 3のpublication security matrixをexact candidateへ再束縛する
* protected dataとdogfood digestを観測する
* same-tip B1/B2を要求する

ただし、検証contractと検証programを分ける必要があります。Planは「入力、観測項目、期待値、証拠identity」を記載し、実際のrunnerは既存test suite、verifier、または実装時の一時的なevidence toolへ任せます。Markdown内の長大なrunnerを成功させること自体を受入条件にしてはなりません。

### 4.6 停止条件

現行停止条件は内容自体は広く妥当ですが、Requirement、Design、Plan、handoffへ重複しており、authorityが不明です。本packでは次の分類へ集約します。

1. identity・authorization不一致
2. baseline・source drift
3. expected REDと異なる失敗
4. security contract不成立
5. row 12 no-edit boundary drift
6. dogfood・protected-data・lifecycle drift
7. ledgerの前提または許容差分違反
8. policy・workflow・timing・wire・#396 scopeへの越境
9. unexpected failureまたはowner decision発生

停止時は、新しい設計をLunaMaxが選ばず、expected/actual、対象row、path/symbol、実行済み操作、変更済みpath、次に必要な確認を返します。長大なJSON SchemaをPlanとhandoffへ二重に埋め込む必要はありません。

### 4.7 LunaMaxが迷う点

現行packでは、LunaMaxが次を判断しにくい状態です。

* Planとhandoffのどちらが実行authorityか
* 固定されたmethod bodyをそのまま貼るべきか、current sourceから最小修復を導くべきか
* row 3のfirst REDをobserver強化前と強化後のどちらで扱うか
* row 12で「testはGREEN、ledger evaluatorはRED」という二重状態をどう扱うか
* working-tree verifierの`candidate_sha`がuncommitted bytesを表さないことを、どのevidence identityで補うか
* expected 11 pathsが「変更を強制するfile list」なのか「許容・期待されるprojection surface」なのか
* post-merge B1/B2をLunaMax自身が実行するのか、human/Codexへ渡すのか
* commit/push/PR準備の許可とProduct mutation許可が別であることを、どの時点で再確認するか

修正版では、Planを唯一のTDD実行順序、handoffをdispatch/return contractに限定し、これらを明示します。

## 5. 保持すべき仕様

全面改訂しても、次は変更しません。

* exact 15 regression rowsとrow order
* row 2の`resolved/superseded`とsuccessor
* row 3のcredential-bearing read-only identityとstrict publication boundary
* rows 4–11のdescriptor-bound test-double seam
* row 12の`commands -> application.contracts -> domain` guardとno-edit方針
* rows 1・13・14・15のselection-only observer修復
* 14 rowsの`resolved/fixed-in-place`遷移
* ledgerを最後に変更する順序
* provider source first、complete dogfood projection、digest/protected-data proof
* timing 243、required-fast 4、current policy、current workflowsのno-touch
* Provider Lifecycle Wireのread-only consumer境界
* P392以外の非GREEN禁止
* human merge only
* `implementation_allowed=false`
* `owner_decisions_required=[]`

## 6. 改訂後の実装開始条件

本packを作成しただけでは実装を開始しません。次がすべて必要です。

1. canonical Issue文書へ採用されたclean pushed specification SHA/tree
2. local HEAD、upstream、remote branch tipのexact一致
3. P392からspec freezeまでの許可されたdocumentation-only provenance
4. exact spec tipに対するfresh independent specification review pass
5. P0=0、P1=0
6. explicit `implementation_authorized=true`
7. scoped concurrent-writer absence assertion
8. mutation直前のclean identity再確認
9. commit/pushとPR preparationの個別許可
10. human merge onlyの維持

## 7. 未確認事項

* full test suite、full verifier、lifecycle update、SpecDock validateは未実行です。
* local worktreeのclean状態、configured upstream、active pointer、concurrent writerは未確認です。
* canonical adoption、independent spec review、implementation dispatchは未実施です。
* Product source、tests、ledger、timing、policy、workflow、Git history、PR、Issue stateは変更していません。
