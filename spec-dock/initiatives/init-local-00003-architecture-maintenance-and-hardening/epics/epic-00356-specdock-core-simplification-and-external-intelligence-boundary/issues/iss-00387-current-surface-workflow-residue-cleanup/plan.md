---
種別: 実装計画書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "approved"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## 1. Planning Level

**standard**を選択する。

- public CLIの追加・削除、data migration、distribution architecture変更はない。
- Current docs、placeholder、内部request、package config、retirement-only test supportを横断する。
- Historical authorityとtest copy、surviving behaviorとabsence assertionを誤分類すると過剰削除またはtest debtを招くため、lightでは不足する。
- security、不可逆data、external API、release architectureを変更しないためstrict/criticalは不要である。

次のいずれかが判明したら実装を止め、R/D/Pを再評価する。

- `checkout_active_target()`のbehavior変更が必要。
- public CLI contractを変更する必要がある。
- test lane、marker、shard、timing、provider workflow、managed distributionの再設計が必要。
- authoritative Historical evidenceまたはuser-owned dataのmigrationが必要。
- 新規testでなければ観測できないsurviving behavior riskが判明。

## 2. 目標、現在地、計画改訂

### 2.1 目標

Current surfaceを親Epic #356の契約へ収束させる。同じ変更で、退役機能の不在だけを証明するtest、fixture、helper、scanner、mutation、定数も撤去する。残る正のbehaviorだけを既存testで検証し、削除確認は本Planのone-time checklistとReportで完結させる。

### 2.2 現在地

- Issue作成、依存設定、`issue start`: 実施済み。
- initial Requirement/Design/PlanとStrict review: 実施済み。
- test-withdrawal方針のStrict分析: SHA `7acaf40fff273c292c12111b81e11d997dbe18cd`で実施済み。
- 本改訂後のspec review: 未実施。
- production implementation、test/support撤去、verification、PR: 未着手。

実装結果はこの現在地を過去に遡って書き換えず、§15のstatus ledgerと`report.md`へ実測として追記する。

### 2.3 改訂履歴

| 日付 | 変更 | 既実施作業への影響 |
|---|---|---|
| 2026-08-31 | initial planはTDDでCurrent drift guard、absence assertion、mutation testを追加する方針だった | implementation未着手のため実施済みstepなし |
| 2026-08-31 | user判断とChatGPT Use Strict分析により、test-addition drivenからevidence-driven retirementへ変更 | 旧S01/S03/S05/S06は未実施のまま廃止。完了扱いにしない |
| 2026-09-01 | Strict reviewのP2指摘により、S06専用mypy overrideの条件付きexact-entry cleanupと、C60-01の同一wheel artifact bindingを追加 | implementation未着手のため実施済みcheckなし。checklist数、ledger行、closure gateは不変 |
| 2026-09-01 | fixed SHA `f3b6c2b6f1db2c3b7e54966496f76a74db34d689`のStrict review P1指摘により、`OTHER_SUBSTANTIVE_OR_AMBIGUOUS`のfinite repair checkpointと、exact ledger二列以外のR/D/P全hunkを覆う`SPECIFICATION_CONTRACT`境界を追加 | implementation未着手のため失効させる実測なし。38 checks、36 ledger rows、各check 8 fields、C90-04/C90-05の二external gatesは不変 |
| 2026-09-01 | fixed SHA `7f4ec536e34b35fe1dfe250ee786cef5ed59bc6d`のC00独立監査とChatGPT Use Strict Extra High分析により、scripts READMEと三scopeのartifacts/discussions rulesの7 provider/dogfood pairをapproved Current surfaceへ追加 | production/test/config未着手。旧C00 evidenceは破棄してNOT_RUNへ戻した。38 checks、36 ledger rows、各check 8 fields、C90-04/C90-05の二external gatesは不変 |

## 3. 実装原則

1. production writerは一人とし、milestone単位で引き継ぐ。
2. provider sourceを先に編集し、dogfood projectionを同期する。
3. 廃止機能と、その不在・無視だけを証明するtest supportを一体で撤去する。
4. 文書、設定、dead residue、retirement-only supportの削除に新しいRED testを作らない。
5. surviving behaviorは既存のpositive testを保持・最小更新する。既存testが十分なら追加しない。
6. mixed-purpose testはtest全体を削除せず、retirement-only assertionだけを除く。
7. test名、旧語彙、Issue番号だけで削除を判断しない。consumer、observed behavior、failure semanticsを確認する。
8. authoritative Historical evidenceを変更しない。test copy/synthetic fixtureはauthorityではない。
9. Epic #384のtest architecture、distribution semanticsを再設計しない。ただし削除test nodeへのledger/timing/required-node exact参照は同時に除去する。
10. 実行していないcommand、policy skip、未collection testをPASSにしない。
11. checklist用の新しいrepository script、scanner、fixture、test helperを作らない。
12. 一時物はWorkbenchまたは`mktemp -d`に置き、証拠転記後に本Issue所有物だけを片付ける。
13. current Requirement/Designの全hunkと、§15の既存rowにある`状態`・`Evidence reference`のcell value以外のcurrent Plan全hunkを`SPECIFICATION_CONTRACT`とし、production writer判断で変更・stageしない。
14. `OTHER_SUBSTANTIVE_OR_AMBIGUOUS`のrepairはapproved既存pathだけで閉じ、repair hunk・失効status・短いinvalidation evidenceを一度だけまとめてexplicit stageしたrepair checkpointから有限順序で再実行する。

## 4. 検証分類と禁止事項

| Class | 例 | このIssueでの扱い |
|---|---|---|
| A: surviving positive behavior | selection-only、issue start ordering/failure、retained CLI、parity、package output | 既存automated testを保持・最小更新 |
| B: one-time retirement evidence | 旧文言、旧field、dead config、orphan ref、no-touch diff | 本checklistで`rg`、AST、diff、build、fresh initを実行しReportへ記録 |
| C: retirement-only support | removed route/module/field inventory、phrase scanner、Historical exclusion、legacy mutation、test copy | consumer確認後に削除。mixed testはClass A部分だけ残す |

次を新しいautomated testとして追加してはならない。

- README、placeholder、overviewに旧語句がないこと。
- deleted field、module、path、glob、flagがないこと。
- removed routeがparser errorになること。
- Historical fileがscanner対象外であること。
- detectorがsynthetic旧語句を検出すること。
- `checkout_active_target()`のsource text/hashが不変であること。

## 5. Test budgetと撤退会計

implementation baselineとfinal candidateで同じ方法により次を記録する。

- collected test count。
- tracked `tests/**/*.py` LOC。
- tracked test file数。
- tracked fixture file数。
- added/deleted production LOC。
- added/deleted test/support LOC。

合格条件:

1. test count、test LOC、test file数、fixture file数はいずれも純増しない。
2. retirement candidate decision coverage `decided / discovered = 1.0`。
3. `remove`判定candidateのclosure `removed / removable = 1.0`。
4. surviving behaviorの唯一の観測手段を削除していない。
5. `deleted test LOC / max(1, deleted production LOC)`を情報として記録する。閾値は設けない。
6. removable test supportが存在する場合、test/support deletionは0より大きい。

例外は実装前のR/D/P改訂と再reviewを必要とする。本計画では新規test追加例外を予定しない。

## 6. Checklistの実行規約

本Planは38個のcheckを持つ。IDは見出しで固定し、各checkは次の8 fieldを一つずつ過不足なく持つ。field外の共通規約はこの8 fieldの構成に数えず、補足規約として扱う。

- **対象 / 目的**: 何を、なぜ確認するか。
- **前提**: 実行可能になる条件。
- **操作**: source/docs/testへの変更。
- **確認**: 実行するcommandまたは目視対象。
- **期待結果**: PASSの観測可能な条件。
- **証拠**: Reportへ転記する要約。
- **停止条件**: 続行せずmain agentへ返す条件。
- **cleanup**: 削除するtemporary/orphan item。

状態語彙は`NOT_RUN`、`PASS`、`BLOCKED`、`N/A(reason)`だけを使う。C00-01〜C90-03の36 rowだけを§15のversion管理ledgerに置く。final content writeを含むC90-04とpost-freeze C90-05は二つのexternal gateであり、同じ状態語彙をPR/handoff evidenceで使い、version管理ledgerへ追加しない。

current R/D/P/Reportの`SPECIFICATION_CONTRACT`判定はC00-01開始後の全期間に適用し、C50-01の初回stage前snapshotでも確認する。Plan内で`EVIDENCE_ONLY`として更新できるのは、§15に既に存在する36 rowの`状態`列と`Evidence reference`列のcell valueだけである。column header、separator、`ID`列、rowの追加・削除・並べ替え、§15の説明本文を含むそれ以外のPlan hunkはすべて`SPECIFICATION_CONTRACT`である。Requirement/Designの全hunkも`SPECIFICATION_CONTRACT`とし、Reportでは既存の`Outcome`、`Verification`、`Residual Risks / Follow-ups`本文への実測記録だけを`EVIDENCE_ONLY`とする。Reportの見出し・構造変更も`SPECIFICATION_CONTRACT`とする。許可領域と他領域が同一hunkに混在する場合、または同一classification snapshotの別hunkに一件でも`SPECIFICATION_CONTRACT`がある場合はsnapshot全体を同classとしてfail-closedし、他classのhunkもstageしない。長いstdout/stderrをPlanへ貼らず、command、exit、count、主要observed resultをReportへ記録する。

current Issueのexact directoryは`spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup`であり、分類対象のR/D/P/Reportはその直下の`requirement.md`、`design.md`、`plan.md`、`report.md`に固定する。

## 7. Milestone

| Milestone | 内容 | Exit |
|---|---|---|
| M0 | admission、baseline、consumer map | exact baseline、test metrics、candidate分類、no-touch pathを確定 |
| M1 | Current docs/placeholder撤退 | provider-first更新、parity、one-time content review、Historical no-touch |
| M2 | active request contraction | target-only、legacy checkout seam/test撤去、positive behavior GREEN |
| M3 | package/config hygiene | stale entry削除、definition proof、clean archive inventory |
| M4 | retirement-only test/support withdrawal | 全candidateをremove/retain分類し、orphan supportを撤去 |
| M5 | surviving behavior/integration | focused、lint、ordinary、build、fresh init、current verifier |
| M99 | audit/handoff | test budget、scope、Report、Strict gate、merge-ready PR |

## 8. M0 — Admission、baseline、consumer map

### C00-01 — Git/Issue固定点

- **対象 / 目的:** implementation baselineを一意にする。
- **前提:** 改訂R/D/PがStrict reviewを通過し、commit/push済み。
- **操作:** 変更しない。
- **確認:** `git status --short`、`git branch --show-current`、`git rev-parse HEAD`、`git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'`、`git rev-parse '@{upstream}'`を別々に実行する。最後に`IMPLEMENTATION_BASELINE_SHA="$(git rev-parse --verify 'HEAD^{commit}')"`、`printf '%s\n' "$IMPLEMENTATION_BASELINE_SHA" | rg -q '^[0-9a-f]{40}$'`、`test "$(git rev-parse '@{upstream}')" = "$IMPLEMENTATION_BASELINE_SHA"`を実行する。
- **期待結果:** clean、branch=`iss-00387-current-surface-workflow-residue-cleanup`、HEAD=upstream。検証済み40桁値を`<implementation-baseline-sha>`として以後のdiffへ使用する。
- **証拠:** branch、検証済みfull SHA、clean status。full SHAはReportへ一度記録し、後続shellでは同じ40桁値を再代入してC00-01値と一致確認する。
- **停止条件:** dirty、detached、upstream不一致、Git operation/lock。
- **cleanup:** なし。

### C00-02 — Active/dependency readiness

- **対象 / 目的:** 正しいIssueで実装可能か確認する。
- **前提:** C00-01 PASS。
- **操作:** 変更しない。
- **確認:** `./spec-dock/scripts/spec-dock active show`、`./spec-dock/scripts/spec-dock deps check --id iss-00387 --github --json`。
- **期待結果:** active Issue=`iss-00387`、ready=`true`。
- **証拠:** resolved canonical path、dependency result。
- **停止条件:** target ambiguity、not ready、GitHub/local state conflict。
- **cleanup:** なし。

### C00-03 — Change/no-touch inventory

- **対象 / 目的:** 変更可能pathと保護pathを固定する。
- **前提:** C00-02 PASS。
- **操作:** Requirement §4とDesign §2/§5のknown candidateを実pathへ解決し、provider/dogfoodの`scripts/README.md`と`docs/rules/{initiative,epic,issue}/{artifacts,discussions}.md`の14 pathsをapproved inventoryへ明示する。
- **確認:** `rg -n 'ActiveSetArgs|SetActiveRequest|checkout_active_target|active set .*--checkout|Evidence Adoption Ledger|Issue 359' README.md src/spec_dock/assets/spec_dock spec-dock tests`、`rg -n 'REMOVED_HELP_ROUTES|REMOVED_RUNTIME_MODULES|CURRENT_LEGACY_VOCABULARY_PATTERNS|S09_LEGACY_EVIDENCE_MUTATIONS|existing_issue|test_active_set_legacy_flag_reports_parser_error|test_runtime_active_s05|test_runtime_active_s06' tests pyproject.toml full-regression-ledger.json full-regression-timing-weights.json`、`rg -n 'tests\.cli_runtime\.test_delegated_authoring|tests\.cli_runtime\.test_runtime_active_s06|assets/install_root/\.codex/\*\*' pyproject.toml`。
- **期待結果:** candidate path、追加した14 Current paths、surviving consumer、S06 testと専用mypy overrideのcoupling、no-touch pathが一覧化される。
- **証拠:** inventory表をReportへ要約。
- **停止条件:** candidateがEpic #384またはauthoritative historyだけに存在する。
- **cleanup:** なし。

### C00-04 — Before test metrics

- **対象 / 目的:** test純増と撤退量の比較基準を採取する。
- **前提:** clean baseline。
- **操作:** 変更しない。
- **確認:** `uv run pytest --collect-only -q`、`git ls-files tests`、`git ls-files tests/fixtures`。tracked Python test LOCは最初のlistingから明示pathを`wc -l`へ渡して集計する。
- **期待結果:** collected count、test LOC、test file数、fixture file数が再現可能に記録される。
- **証拠:** `metrics-before`四値、skip/errorの有無、command。
- **停止条件:** collection error、generated/untracked testを混入、集計母集団が不明。
- **cleanup:** pytest cacheはM99で本Issue生成分だけ確認する。

### C00-05 — Retirement candidate decision ledger

- **対象 / 目的:** test/supportを名前だけで削除しない。
- **前提:** C00-03/04 PASS。
- **操作:** 各candidateについて定義、参照、fixture input、observed behaviorを調べ、`remove`、`retain(surviving consumer)`、`split`へ分類する。
- **確認:** `rg -n '<candidate-symbol-or-path>' tests src/spec_dock spec-dock`をcandidateごとに実行し、必要なPython symbolはAST上のLoad/importも確認する。
- **期待結果:** discovered candidate全件にdecision、consumer、予定操作がある。
- **証拠:** Reportのdecision ledger。coverage=`1.0`。
- **停止条件:** dynamic import/discovery、唯一のfailure semantics、canonical authorityか不明。
- **cleanup:** なし。

### C00-06 — Historical authority/test-copy分類

- **対象 / 目的:** 履歴を保全しつつtest copyを聖域化しない。
- **前提:** C00-05実行中。
- **操作:** `spec-dock/initiatives/**`、accepted ADR、Historical guideをauthority、`tests/fixtures/**`とsynthetic mutationをtest infrastructureとして分類する。
- **確認:** fixture参照とcanonical copy元を`rg`/path inspectionで確認する。
- **期待結果:** authorityはno-touch、test copyはconsumer有無でremove/retain判断。
- **証拠:** path別classification。
- **停止条件:** fixture自体が唯一のcanonical source、runtime input、external compatibility fixture。
- **cleanup:** なし。

### C00-07 — Baseline package inventory

- **対象 / 目的:** phantom `.codex/**`判定を実物で行う。
- **前提:** baseline clean。
- **操作:** clean buildを既存commandで作る。
- **確認:** `uv build`、`python -m zipfile -l <exact-wheel-path>`、`tar -tf <exact-sdist-path>`。source `install_root`、wheel、sdistを比較する。
- **期待結果:** current `.agents/**`と`.github/**`があり、live `.codex/**` assetがない。
- **証拠:** exact artifact pathとinventory summary。
- **停止条件:** live `.codex` source/consumer、stale artifactをbaselineとして使用、build failure。
- **cleanup:** baseline build artifactはinventory採取後にownershipを記録し、M99で片付ける。

### C00-08 — Admission decision

- **対象 / 目的:** 推測削除を防ぐ最終gate。
- **前提:** C00-01〜07完了。
- **操作:** main agentがcandidate ledgerとstop conditionを確認する。
- **確認:** checklist目視。
- **期待結果:** 各milestoneのexact ownershipが確定し、未決candidateがない。
- **証拠:** `GO`または`BLOCKED(reason)`。
- **停止条件:** unresolved consumer、scope overlap、新規test例外の必要。
- **cleanup:** なし。

## 9. M1 — Current docs/placeholder撤退

### C10-01 — active-none minimalization

- **対象 / 目的:** 三scope placeholderから旧workflow schemaを除く。
- **前提:** C00-08 GO。
- **操作:** providerのinitiative/epic/issue `report.md`をDesign §3.3のminimal contentへ変更し、対応dogfoodへ同期する。
- **確認:** providerとdogfood各pairを`cmp`し、6ファイルを目視する。
- **期待結果:** active未設定、編集禁止、canonical Report pathだけを示し、pairがbyte一致。
- **証拠:** changed paths、`cmp` exit 0、目視結果。
- **停止条件:** placeholder構造変更、Historical/fixture変更が必要。
- **cleanup:** 旧schemaを固定していたretirement-only test/supportはM4候補へ追加。

### C10-02 — Current lifecycle / Artifact authority docs cleanup

- **対象 / 目的:** root README、scripts README、三scopeのartifacts/discussions rulesでCurrent lifecycleとArtifact authorityを正しく案内する。
- **前提:** C00-08 GO。
- **操作:** root `README.md`では`active set --checkout`、recovery/normalization、EAL必須説明を削り、selection-only、`issue start`、evidence review + canonical rewriteへ置換する。providerの`scripts/README.md`は旧checkout exampleをselection-onlyと`issue start`の二経路へ置換する。providerの三scopeのartifacts/discussions rulesはEAL/report ledgerをCurrent adoption authorityとする文だけをR/D/Pまたはaccepted ADRへの明示的再記述へ置換し、Historical grandfathering/catalogを保持する。7 provider filesをdogfoodへ同期する。
- **確認:** 対象sectionを目視し、14 provider/dogfood pathsのpairを`cmp`する。`rg -n 'active set .*--checkout|Evidence Adoption Ledger|EAL|report ledger' README.md src/spec_dock/assets/spec_dock/scripts/README.md src/spec_dock/assets/spec_dock/docs/rules spec-dock/scripts/README.md spec-dock/docs/rules`をone-time確認し、Historical文脈とCurrent instructionを区別する。
- **期待結果:** Current手順が一意で、旧checkout exampleとCurrent EAL/report-ledger adoption authorityが残らず、7 pairがbyte一致する。Historical grandfathering/catalogは保持される。
- **証拠:** section見出し、14 changed paths、7 pairの`cmp` exit 0、rg結果、diff summary。
- **停止条件:** migration/history originalsまで消す必要がある、列挙外のsibling Current docs変更、public CLI変更が必要。
- **cleanup:** README phrase absence testは追加しない。

### C10-03 — Authoring overview cleanup

- **対象 / 目的:** 二skillを現在形で案内する。
- **前提:** C00-08 GO。
- **操作:** provider overviewのIssue #359未来形をCurrent説明へ変更しdogfoodへ同期する。
- **確認:** `cmp src/spec_dock/assets/spec_dock/docs/authoring/overview.md spec-dock/docs/authoring/overview.md`と目視。
- **期待結果:** 現在存在する二skillのpath/役割が現在形で一致。
- **証拠:** cmp result、reviewed headings。
- **停止条件:** installed skill本文の変更が必要。
- **cleanup:** future wording absence testは追加しない。

### C10-04 — Docs no-touch audit

- **対象 / 目的:** authoritative historyとEpic #384境界を守る。
- **前提:** C10-01〜03実装後。
- **操作:** 変更しない。
- **確認:** `<implementation-baseline-sha>`からHistorical guide、他Issue履歴、migration docs、Epic #384 docsをpath限定diffする。
- **期待結果:** C10-01〜03のapproved Current docsと本Issue R/D/P/Report以外のauthoritative history差分0。scripts READMEと三scopeのartifacts/discussions rulesの7 pair以外のsibling rules差分0。
- **証拠:** diff exit/result。
- **停止条件:** 一件でも意図しない差分。
- **cleanup:** unintended diffだけを原因pathで修正する。historyを書き換えて合わせない。

## 10. M2 — Active request contraction

### C20-01 — Existing positive coverage baseline

- **対象 / 目的:** 新規test不要を実証する。
- **前提:** M1完了。
- **操作:** 変更前に既存positive testsを特定・実行する。
- **確認:** `uv run pytest tests/unit/application/test_set_active.py -q`、`uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_issue_lifecycle.py -q`、`uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_storage_core_cli.py -q`。
- **期待結果:** selection-only、three selector、invalid no-write、issue-start ordering/failureの既存観測点が確認できる。
- **証拠:** test names、pass/skip/fail/count/duration。
- **停止条件:** 必要behaviorを既存testが観測せず新規testが必要。
- **cleanup:** なし。

### C20-02 — Provider target-only implementation

- **対象 / 目的:** internal seamをCurrent responsibilityへ合わせる。
- **前提:** C20-01でpositive coverage確認済み。
- **操作:** provider `ActiveSetArgs`を`target_ref,target_display`、`SetActiveRequest`を`target`だけに縮小し、`set_active()`のconditional checkoutを削除する。`issue_lifecycle.py`はcheckout後にtarget-only requestを渡す。
- **確認:** `rg -n 'SetActiveRequest\(' src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests`、compile/lint、call-site review。
- **期待結果:** repository内call siteがtarget-only、`branch=None`、provider-first。
- **証拠:** changed symbols/call sites。
- **停止条件:** external/public compatibility requirement、target-only化不能consumer。
- **cleanup:** unused imports/fieldsのみ。

### C20-03 — Dogfood projection and helper no-change

- **対象 / 目的:** projection一致とcheckout owner維持。
- **前提:** C20-02完了。
- **操作:** provider runtimeをdogfoodへ同期する。
- **確認:** relevant provider/dogfood filesを`cmp`し、baselineから`checkout_active_target()`のsignature/body/docstringをdiffする。
- **期待結果:** projection一致、helper差分0。
- **証拠:** cmp/diff result。
- **停止条件:** helper変更またはdual modeが必要。
- **cleanup:** なし。

### C20-04 — Legacy checkout test/support withdrawal

- **対象 / 目的:** internal checkout compatibility test debtを撤去する。
- **前提:** issue-start positive ordering/failure testsを保持。
- **操作:** `test_internal_checkout_request_preserves_issue_start_compatibility`を削除し、test request helperをtarget-onlyへ縮小する。`tests/cli_runtime/test_runtime_active_s06.py`の旧force/dependency/GitHub behavior群をconsumer分類し、surviving behaviorでなければfile/test、ledger参照、専用mypy overrideを連動撤去候補にする。専用mypy overrideのexact処理はC30-01、ledger参照はC40-09で行う。専用Git/GitHub/dependency stub/importはconsumer 0なら削除する。
- **確認:** candidate symbolごとの`rg`、AST/import review、focused tests、S06 fileの`remove`または`retain(reason)` decision。
- **期待結果:** internal checkout path専用test/supportなし、surviving positive testsは存在し、S06 file decisionがC30-01/C40-09へ一意に渡る。
- **証拠:** deleted test/helper、retained test names、S06 decision。
- **停止条件:** stub/helperが他のcurrent failure semanticsで使用中。
- **cleanup:** orphan imports/classes。

### C20-05 — M2 positive verification

- **対象 / 目的:** 残存behaviorの非回帰を確認する。
- **前提:** C20-02〜04完了。
- **操作:** 既存testを最小更新して実行する。field absence専用testは追加しない。
- **確認:** C20-01と同じ3 commandを、同じ`--run-full-regression --full-regression-shard` modeで実行する。global ledger completenessはここでは評価せずC60-02だけで評価する。
- **期待結果:** required testsが実行されGREEN。policy skipをPASSにしない。
- **証拠:** names/count/durationとconstructor更新内容。
- **停止条件:** 新しいabsence assertionでなければ通せない、ordering/failure regression。
- **cleanup:** pytest cacheはM99。

## 11. M3 — Package/config hygiene

### C30-01 — Stale pyproject entries

- **対象 / 目的:** phantom package/test configを除き、S06 testのremove/retain decisionと専用mypy overrideを一致させる。
- **前提:** C00-07でlive `.codex` consumerなし。C20-04でS06 fileの`remove`または`retain(reason)` decisionが確定。
- **操作:** 既存の複数module overrideから`tests.cli_runtime.test_delegated_authoring` memberだけを削除し、`assets/install_root/.codex/**` package-data globだけを削除する。S06 fileを削除した場合に限り、`module = "tests.cli_runtime.test_runtime_active_s06"`と`disable_error_code = ["assignment", "var-annotated"]`から成る専用`[[tool.mypy.overrides]]` entry全体を削除する。S06 fileを保持した場合は同entryを変更せず保持する。その他の`pyproject.toml` entryは変更しない。
- **確認:** `rg -n 'tests\.cli_runtime\.test_delegated_authoring|assets/install_root/\.codex/\*\*' pyproject.toml`が0件であること、S06 fileがある場合は専用overrideがexactly oneで、ない場合は`tests.cli_runtime.test_runtime_active_s06`参照が0件であること、`git diff -- pyproject.toml`で無関係entryに差分がないことを確認する。
- **期待結果:** delegated memberと`.codex` globなし。S06 fileと専用overrideの存在が一致し、`.agents/**`と`.github/**`および無関係entryは保持。
- **証拠:** S06 decision、reference count、pyproject exact diff。
- **停止条件:** S06 file/override不一致、live `.codex` asset/consumer、unrelated config変更が必要。
- **cleanup:** stale entry absence testは追加しない。

### C30-02 — Definition-only candidates

- **対象 / 目的:** orphan test constantsを証拠付きで削除する。
- **前提:** C00-05 ledgerにcandidateあり。
- **操作:** reference 0、AST Load 0、dynamic discoveryなしの候補だけ削除する。
- **確認:** candidateごとの`rg`、AST inspection、`uv run pytest --collect-only -q`、lint。
- **期待結果:** removable candidate削除、retain candidateにはconsumer理由。
- **証拠:** per-candidate decision。
- **停止条件:** dynamic/reflection/fixture discoveryが不明。
- **cleanup:** orphan import/helper。

### C30-03 — Post-change package inventory

- **対象 / 目的:** 配布物を不在testなしで確認する。
- **前提:** C30-01/02完了。
- **操作:** clean wheel/sdistを作り、source/wheel/sdist/installed resourceを比較する。
- **確認:** `uv build`、exact artifactに対するzip/tar listing、既存full install-root inventory testまたはisolated install inspection。
- **期待結果:** current二skillと`ci.yml`あり、retired `.codex`なし、四surface一致。
- **証拠:** artifact path、inventory delta、build result。
- **停止条件:** current asset欠落、Epic #384実装変更が必要。
- **cleanup:** 本Issueのbuild/temp installのみM99で削除。

## 12. M4 — Retirement-only test/support withdrawal

### C40-01 — Removed CLI/runtime inventory family

- **対象 / 目的:** 削除済み項目の不在リストを恒久維持しない。
- **前提:** retained registry/import/parity testを特定済み。
- **操作:** `REMOVED_HELP_ROUTES`、`REMOVED_RUNTIME_MODULES`、`REMOVED_APPLICATION_CONTRACT_SYMBOLS`、`REMOVED_USE_CASE_FIELDS`とabsence部分を削除する。mixed helperはretained imports/parityだけへ縮小する。
- **確認:** symbol refs、remaining test names、focused storage-core test。
- **期待結果:** removed inventory/absence assertionなし、retained CLI/runtime positive smokeあり。
- **証拠:** deleted constants/assertions、retained tests。
- **停止条件:** removalによりcurrent import/parity観測が消える。
- **cleanup:** orphan `hashlib/os/subprocess/sys`等は実consumer確認後。

### C40-02 — Removed route/flag negative tests

- **対象 / 目的:** 廃止route/flagを永久に列挙するtestを撤去する。
- **前提:** retained root/leaf help、selector success、invalid no-write coverageあり。
- **操作:** `test_removed_routes_are_parser_errors_without_tree_or_state_writes`、direct `active set --checkout` parser-error test、`test_active_set_legacy_flag_reports_parser_error`、helpの旧flag集合assertionを削除する。positive selector/assertionは残す。削除fast nodeに対応する`REQUIRED_FAST_NODE_IDS`とtiming weightのexact entryを同時に削除する。
- **確認:** `rg`で`--checkout`、`--issue`を含むremoved flag/route専用test全体とnode ID参照を確認し、remaining CLI testsを実行する。
- **期待結果:** positive Current CLI testはGREEN、retirement-only negative testsなし。
- **証拠:** removed/retained assertion list。
- **停止条件:** invalid target no-writeやcurrent help inventoryまで失われる。
- **cleanup:** `_tree_snapshot`等はremaining consumer確認後。

### C40-03 — Authoring phrase scanner family

- **対象 / 目的:** wording debtとscanner保守を撤去する。
- **前提:** link/parity/current template schemaのpositive testsを分類済み。
- **操作:** `CURRENT_LEGACY_VOCABULARY_PATTERNS`、`_current_vocabulary_violations()`、retirement-only forbidden detector、synthetic mutation/infix/Historical positive-control testを削除する。mixed testはpositive schema部分だけ残す。
- **確認:** exact symbols/pattern familyを`rg`し、remaining `test_authoring_kit_assets.py`を実行する。
- **期待結果:** phrase scanner/mutationなし、current links/parity/schema testsはGREEN。
- **証拠:** removed helper/test/constantとretained test names。
- **停止条件:** detectorがsecurity/schema invariantも担う、境界分離不能。
- **cleanup:** orphan regex/constants/imports。

### C40-04 — Legacy evidence mutation family

- **対象 / 目的:** EAL/Assurance等の旧証跡を人工生成するtest supportを撤去する。
- **前提:** issue lifecycle/doctorのcurrent positive behaviorを別testが観測。
- **操作:** `S09_LEGACY_EVIDENCE_MUTATIONS`、`apply_s09_legacy_evidence_mutation` consumerを分類し、retirement-only tests/importsを削除する。consumer 0後に`s09_invariance.py`を削除する。
- **確認:** `rg -n 'S09_LEGACY_EVIDENCE_MUTATIONS|apply_s09_legacy_evidence_mutation|s09_invariance' tests`、remaining doctor/lifecycle tests。
- **期待結果:** refs 0、helper fileなし、current positive tests GREEN。
- **証拠:** consumer map、deleted path。
- **停止条件:** mutation testがcurrent validate/doctor failure semanticsの唯一の観測。
- **cleanup:** orphan imports/parametrize data。

### C40-05 — Issue-finish quality-evidence ignore tests

- **対象 / 目的:** removed quality gateを読まないことだけを証明するtestを撤去する。
- **前提:** ordinary `issue finish` success/failure testsを特定済み。
- **操作:** `test_issue_finish_does_not_read_quality_evidence`、`test_issue_finish_ignores_heavy_report_and_assurance`等をconsumer分類し、retirement-onlyなら削除する。current lifecycle assertionが混在する場合はpositive部分へ縮小する。
- **確認:** test bodies、fixtures、remaining finish testsを確認・実行する。
- **期待結果:** removed gate無視専用testなし、current finish behaviorは観測される。
- **証拠:** per-test decision。
- **停止条件:** current no-write/failure behaviorの唯一のtest。
- **cleanup:** heavy report/EAL fixture builders。

### C40-06 — Historical test-copy machinery

- **対象 / 目的:** authoritative historyを残し、test copy debtを撤去する。
- **前提:** C00-06 classification、canonical originals存在。
- **操作:** preservation SHA/copy/mutation constants/helpers/testsをconsumer 0まで削除し、その後`tests/fixtures/authoring_kit/existing_issue/**`を削除する。
- **確認:** `rg -n 'PRESERVATION_BASELINE_SHA256|PRESERVATION_COPIED_SOURCE_PATHS|PRESERVATION_FIXTURE_ROOT|existing_issue' tests`、canonical source path確認。
- **期待結果:** test refs 0、fixture copyなし、authoritative originals無変更。
- **証拠:** deleted path list、canonical no-diff。
- **停止条件:** fixtureがruntime input、external compatibility contract、唯一のpositive behavior input。
- **cleanup:** orphan SHA/copy utilities。

### C40-07 — Orphan cleanup and interim metrics

- **対象 / 目的:** test撤退で生じたsupport残滓を閉じる。
- **前提:** C40-01〜06のdecision完了。
- **操作:** 本Issueの削除で未使用になったimport、constant、helper、fixtureだけを削除する。
- **確認:** `make lint`、`uv run pytest --collect-only -q`、beforeと同じtracked test/fixture metrics。
- **期待結果:** lint/collection成功、test metrics純増なし。C40-01〜06でdiscoveredしたinterim subsetのdecision coverage/closure=1.0。C40-08/09を含む全体closureはここで判定せずC90-02で判定する。
- **証拠:** interim subset metrics、対象ID範囲、orphan list。
- **停止条件:** unrelated refactorが必要、collection対象が予期せず消える。
- **cleanup:** 本Issue由来orphanのみ。

### C40-08 — Legacy active S05 context-pack contracts

- **対象 / 目的:** 旧Authority、grants、Promotion、EALをCurrent context-pack contractとして固定するtestを撤去する。
- **前提:** Current `ActiveManifestEntry(id,path)`とstructural context-pack behaviorを観測するpositive testを特定済み。
- **操作:** `tests/cli_runtime/test_runtime_active_s05.py`の4 ledger nodeを含むtestを分類し、retirement-only test/assertionを削除する。mixed testはCurrent structural assertionだけへ縮小する。
- **確認:** `rg -n 'test_runtime_active_s05|Authority|grants|Promotion|EAL' tests/cli_runtime/test_runtime_active_s05.py full-regression-ledger.json`とremaining focused test。
- **期待結果:** old authority/evidence contract専用testなし、Current structural behaviorは観測される。
- **証拠:** 4 nodeを含むper-test remove/retain/split decisionとretained assertion。
- **停止条件:** active state write、sync failure、Current structural context packの唯一の観測手段で分離不能。
- **cleanup:** retirement-only fixture/helper/importと、削除nodeへのexact ledger参照をC40-09へ渡す。

### C40-09 — Full Regression/fast-node referential integrity

- **対象 / 目的:** test撤去と現行verifier inventoryを矛盾させない。
- **前提:** C20-04、C40-01〜08で実際に削除するnode IDが確定。
- **操作:** 削除node IDに一致する`full-regression-ledger.json` failure row/command input、`full-regression-timing-weights.json` weight、`tests/conftest.py`の`REQUIRED_FAST_NODE_IDS`だけを削除または現存successorへ最小更新する。
- **確認:** 削除node IDごとに3ファイルを`rg`し、ledger parser/current verifier、collectionを実行する。
- **期待結果:** deleted node参照0、現存nodeのledger/timing/required classificationは整合、verifier成功。
- **証拠:** node ID別before/after entry、parser/verifier result。
- **停止条件:** schema、failure disposition、marker、shard、workflow、weight算出方法の変更、無関係nodeへの波及。
- **cleanup:** orphan exact entriesだけ。ledger/timing全体の再生成はしない。

## 13. M5 — Surviving behavior、build、fresh consumer

### C50-01 — Focused positive suites

- **対象 / 目的:** 残存契約を最小の既存suiteで検証する。
- **前提:** M1〜M4完了。
- **操作:** focused suiteの前に、Reportへ記録したC00-01の40桁値を`export IMPLEMENTATION_BASELINE_SHA='<C00-01 full SHAへ一度だけ置換>'`へ再代入する。初回stage前snapshotのcurrent R/D/P/Reportを§6のspecification境界で確認し、`SPECIFICATION_CONTRACT` hunkが0である場合だけ、C00〜C40のapproved inventoryにある変更pathとcurrent IssueのPlan/Reportを`git add -- <explicit-path>...`でstageする。globや動的path展開を使わない。以後このindexをcandidate checkpointとする。
- **確認:** `printf '%s\n' "$IMPLEMENTATION_BASELINE_SHA" | rg -q '^[0-9a-f]{40}$'`、`test "$(git rev-parse --verify "${IMPLEMENTATION_BASELINE_SHA}^{commit}")" = "$IMPLEMENTATION_BASELINE_SHA"`、`test "$IMPLEMENTATION_BASELINE_SHA" = '<Reportに記録したC00-01 full SHAへ一度だけ置換>'`を実行する。`git diff --name-status`が空、`git ls-files --others --exclude-standard`が空、`git diff --cached --name-status "$IMPLEMENTATION_BASELINE_SHA"`がapproved inventoryだけであることを確認する。その後`uv run pytest tests/unit/application/test_set_active.py tests/unit/infra/test_authoring_kit_assets.py -q`、`uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_issue_lifecycle.py tests/cli_runtime/test_doctor.py -q`、`uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -q`を実行する。削除済みfileはcommandから除き、残存focused fileを明示する。
- **期待結果:** required testsが実行されGREEN。skipは理由付き。
- **証拠:** command、selected tests、pass/skip/fail、duration。
- **停止条件:** 初回stage前snapshotに`SPECIFICATION_CONTRACT` hunkがある、retirement-only test再導入でしか通らない、selector/ordering/failure/parity regression。
- **cleanup:** cacheはC90-04。

### C50-02 — Static and ordinary suite

- **対象 / 目的:** repository全体の非回帰。
- **前提:** C50-01 PASS。
- **操作:** 変更しない。
- **確認:** `make lint`、`git diff --cached --check "$IMPLEMENTATION_BASELINE_SHA"`、`uv run pytest`。
- **期待結果:** 全command成功。ordinary laneのpolicy skipを実測記録。
- **証拠:** summary/count/duration。
- **停止条件:** failure無視、test lane/marker変更で回避。
- **cleanup:** なし。

### C60-01 — Clean package/fresh init

- **対象 / 目的:** inventoryした同一wheel artifactからCurrent contractを再現し、source pathからの暗黙rebuildを排除する。
- **前提:** C50-02 PASS。
- **操作:** 空の専用artifact directoryへ1回だけclean buildし、exactly one wheel/sdistを確定する。両artifactのinventory/digestを採取し、同じ`$WHEEL` absolute pathを`uvx --isolated --no-cache --from`へ渡してfresh consumerをinitする。sdistはinventory evidenceにだけ使う。各一時pathを作成直後に出力し、nonzero終了時は同check内で作成済みexact pathだけをcleanupする。
- **確認:** repository rootで次のzsh blockをそのまま実行し、consumer contentを確認する。

  ```zsh
  (
  set -euo pipefail
  typeset ARTIFACT_DIR=''
  typeset CONSUMER=''
  cleanup_c60_01_failure() {
    local exit_status=$?
    trap - EXIT
    set +e
    [[ -z "$CONSUMER" ]] || { printf 'C60-01_FAILURE_CLEANUP_CONSUMER=%s\n' "$CONSUMER" >&2; rm -rf -- "$CONSUMER"; }
    [[ -z "$ARTIFACT_DIR" ]] || { printf 'C60-01_FAILURE_CLEANUP_ARTIFACT_DIR=%s\n' "$ARTIFACT_DIR" >&2; rm -rf -- "$ARTIFACT_DIR"; }
    [[ -z "$CONSUMER" || ! -e "$CONSUMER" ]] || printf 'C60-01_FAILURE_CLEANUP_REMAINS_CONSUMER=%s\n' "$CONSUMER" >&2
    [[ -z "$ARTIFACT_DIR" || ! -e "$ARTIFACT_DIR" ]] || printf 'C60-01_FAILURE_CLEANUP_REMAINS_ARTIFACT_DIR=%s\n' "$ARTIFACT_DIR" >&2
    exit "$exit_status"
  }
  trap cleanup_c60_01_failure EXIT
  ARTIFACT_DIR="$(mktemp -d)"
  printf 'ARTIFACT_DIR=%s\n' "$ARTIFACT_DIR"
  CONSUMER="$(mktemp -d)"
  printf 'CONSUMER=%s\n' "$CONSUMER"
  uv build --clear --out-dir "$ARTIFACT_DIR" .
  test "$(find "$ARTIFACT_DIR" -maxdepth 1 -type f -name 'spec_dock-*.whl' -print | wc -l | tr -d ' ')" -eq 1
  test "$(find "$ARTIFACT_DIR" -maxdepth 1 -type f -name 'spec_dock-*.tar.gz' -print | wc -l | tr -d ' ')" -eq 1
  WHEEL="$(realpath "$(find "$ARTIFACT_DIR" -maxdepth 1 -type f -name 'spec_dock-*.whl' -print -quit)")"
  SDIST="$(realpath "$(find "$ARTIFACT_DIR" -maxdepth 1 -type f -name 'spec_dock-*.tar.gz' -print -quit)")"
  python -m zipfile -l "$WHEEL"
  tar -tf "$SDIST"
  shasum -a 256 "$WHEEL" "$SDIST"
  uvx --isolated --no-cache --from "$WHEEL" spec-dock init "$CONSUMER"
  typeset VALIDATE_OUTPUT=''
  typeset VALIDATE_STATUS=0
  if VALIDATE_OUTPUT="$(cd "$CONSUMER" && ./spec-dock/scripts/spec-dock validate 2>&1)"; then
    VALIDATE_STATUS=0
  else
    VALIDATE_STATUS=$?
  fi
  printf 'C60-01_VALIDATE_STATUS=%s\n' "$VALIDATE_STATUS"
  printf 'C60-01_VALIDATE_OUTPUT=%s\n' "$VALIDATE_OUTPUT"
  test "$VALIDATE_STATUS" -eq 1
  test "$VALIDATE_OUTPUT" = 'error: No nodes found.'
  (cd "$CONSUMER" && ./spec-dock/scripts/spec-dock --help)
  test -f "$CONSUMER/.agents/skills/spec-dock/SKILL.md"
  test -f "$CONSUMER/.agents/skills/spec-dock-grill-with-docs/SKILL.md"
  test -f "$CONSUMER/.github/workflows/ci.yml"
  test ! -e "$CONSUMER/.codex"
  cmp src/spec_dock/assets/spec_dock/docs/authoring/overview.md "$CONSUMER/spec-dock/docs/authoring/overview.md"
  cmp src/spec_dock/assets/spec_dock/scripts/README.md "$CONSUMER/spec-dock/scripts/README.md"
  for scope in initiative epic issue; do
    cmp "src/spec_dock/assets/spec_dock/system/active-none/$scope/report.md" "$CONSUMER/spec-dock/system/active-none/$scope/report.md"
    for rule in artifacts discussions; do
      cmp "src/spec_dock/assets/spec_dock/docs/rules/$scope/$rule.md" "$CONSUMER/spec-dock/docs/rules/$scope/$rule.md"
    done
  done
  shasum -a 256 "$WHEEL" "$SDIST"
  printf 'ARTIFACT_DIR=%s\nWHEEL=%s\nSDIST=%s\nCONSUMER=%s\n' "$ARTIFACT_DIR" "$WHEEL" "$SDIST" "$CONSUMER"
  trap - EXIT
  )
  ```

- **期待結果:** 一時pathが各作成直後に出力される。one wheel/one sdist、inventory/digest成功。exact `uvx` commandがinventory済み`$WHEEL`を使い、init成功後、validateはstatus=`1`かつcombined outputがexact `error: No nodes found.`となり、そのassert後のhelp/cmpが成功する。current二skillと`ci.yml`あり、retired `.codex`なし。overview、active-none、scripts README、三scopeのartifacts/discussions rulesがprovider sourceと一致する。success時はtrapが解除され、二directoryがC90-04まで残る。
- **証拠:** immediate path lines、wheel/sdist absolute pathと前後SHA-256、archive inventory、exact `uvx` command、validate status/output、help exit、cmp summary。予期しないnonzero時はfailure cleanup pathと残存有無。
- **停止条件:** artifact countが1でない、`--from .`/sdist/別buildを使う、既存installed toolを再利用する、live GitHub操作またはmanaged distribution変更が必要、validateの期待status/output以外の予期しないnonzero後に作成済みpathが残る、またはcleanupがその二path以外へ及ぶ。
- **cleanup:** validateの期待status=`1`かつexact output以外を含む予期しないnonzero時はfailure trapが作成済みの`$CONSUMER`と`$ARTIFACT_DIR`だけを削除する。success時はC90-04がimmediate path evidenceと照合して削除する。

**Evidence recording, classification, and repair-checkpoint rule:** C50-01で作ったGit index checkpoint以後、各tracked editまたはnon-ignored untracked追加の直後に、`CURRENT_ISSUE_DIR='spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00387-current-surface-workflow-residue-cleanup'`を設定し、`git diff --name-status`、`git diff -- "$CURRENT_ISSUE_DIR/requirement.md" "$CURRENT_ISSUE_DIR/design.md" "$CURRENT_ISSUE_DIR/plan.md" "$CURRENT_ISSUE_DIR/report.md"`、`git ls-files --others --exclude-standard`を確認してhunk単位で次の順に分類する。複数classが同一hunkに混在する場合は上位の停止側へ倒す。同一snapshot内の別hunkに一件でも`SPECIFICATION_CONTRACT`があればsnapshot全体を同classとし、他classのhunkもstageしない。

1. Plan §15の既存C00-01〜C90-03 rowにある`状態`列・`Evidence reference`列のcell valueだけ、またはReportの既存`Outcome`・`Verification`・`Residual Risks / Follow-ups`本文へ実測事実だけを記録するhunkは`EVIDENCE_ONLY`とする。Planのheader、separator、`ID`列、row set/order、§15説明本文、およびReport見出し・構造は含めない。該当Plan/Report pathだけをexplicit stageし、unstaged/untracked 0を確認して次checkへ進む。
2. current RequirementとDesignの全hunk、および1のexact二列cell value以外のcurrent Planの全hunkは`SPECIFICATION_CONTRACT`とする。front matter、原則、test budget、実行規約、milestone、check本文、exit、ledger規約・構造を含む。Report見出し・構造も同じ扱いとする。C60-01 success時の一時directoryが残っていれば、immediate path evidenceとbyte-for-byte照合し、nonempty・distinct・directoryを確認して旧`$CONSUMER`と`$ARTIFACT_DIR`だけをexact cleanupする。その後production writerは直ちに`BLOCKED` handoffし、そのhunkまたはcurrent candidateを追加stage/commitしない。main agentはoriginal C00-01 implementation baselineから分離したclean worktree/branchを用意し、production/test/config差分0を確認して改訂R/D/Pだけをcommit/pushする。remote branch tipと一致するfixed full SHAにindependent Strict再reviewを通した後、その実装前treeからC00-01を新規実行する。旧status/evidenceは流用しない。
3. 1、2以外のtracked hunk、non-ignored untracked追加、または分類不能な変更は`OTHER_SUBSTANTIVE_OR_AMBIGUOUS`とする。最初の検出からrepair checkpoint成立までを一つのrepair windowとし、その間は通常のcheck実行と通常のledger/Report evidence editを停止する。次の有限順序を一repair windowにつき一度だけ実行する。
   1. C60-01 success時の一時directoryが残っている場合は、immediate path evidenceとbyte-for-byte照合した旧`$CONSUMER`と`$ARTIFACT_DIR`だけを削除して不在確認し、旧wheel、digest、fresh consumer、verifier、audit evidenceを失効させる。
   2. repairをC00-03で承認済みの既存pathだけで完了する。新規path、rename先を含むapproved inventory外path、またはnon-ignored untracked pathが一件でも必要・出現した場合は、repair bundleの一部もstageせず`BLOCKED` handoffする。
   3. §15のC50-01〜C90-03を`NOT_RUN`へ戻し、該当`Evidence reference` cellへexact string `INVALIDATED: OTHER_SUBSTANTIVE_OR_AMBIGUOUS repair; see Report Verification`を記録する。C90-04とC90-05もPR/handoff evidence上で`NOT_RUN`へ戻し、各Evidence referenceをexact string `INVALIDATED: OTHER_SUBSTANTIVE_OR_AMBIGUOUS repair`とする。C00-01〜C40-09のstatus/evidenceはoriginal implementation baselineまたは実装前観測へ束縛されたまま保持し、repair checkpoint上で再実行しない。Reportの`Verification`へ`class=OTHER_SUBSTANTIVE_OR_AMBIGUOUS; repair_paths=<approved paths>; invalidated=C50-01..C90-05; preimplementation=C00-01..C40-09 retained; temp_cleanup=<none|exact removed paths>`の一entryだけを記録する。
   4. classified repair hunk、失効status、Plan/Reportの短いinvalidation evidenceを一つのunstaged repair bundleとして一度だけまとめて確認する。全hunkがapproved repairまたは3の記録だけで、`SPECIFICATION_CONTRACT`、新規path、未承認pathを含まないことを確認する。
   5. approved repair pathのexplicit listに`"$CURRENT_ISSUE_DIR/plan.md"`と`"$CURRENT_ISSUE_DIR/report.md"`を加え、一回の`git add -- <approved-repair-path-1> ... "$CURRENT_ISSUE_DIR/plan.md" "$CURRENT_ISSUE_DIR/report.md"`でstageする。`git add .`、glob、動的path展開、部分stageは使わない。`git diff --name-status`が空、`git ls-files --others --exclude-standard`が空、`git diff --cached --name-status "$IMPLEMENTATION_BASELINE_SHA"`がapproved inventoryだけであることを確認し、これをrepair checkpointとする。成立しなければ再実行へ進まず`BLOCKED` handoffする。
   6. repair checkpointからC50-01〜C90-04をID順に再実行し、そのPASS後にC90-05を先頭から実行する。再実行中の後続`EVIDENCE_ONLY` editは1の通常規約でstageする。新たな`OTHER_SUBSTANTIVE_OR_AMBIGUOUS`を検出した場合だけ、新しいrepair windowとして同じ順序を最初から適用する。

### C60-02 — Current Full Regression

- **対象 / 目的:** 現行policy内の非回帰。
- **前提:** C60-01 PASS。
- **操作:** C40-09でreview済みのdeleted-node exact参照更新を固定し、それ以外のworkflow/ledger/timing/shardを変更せずverifierを実行する。
- **確認:** `uv run python -m scripts.quality.verify_full_regression --shards 4`。
- **期待結果:** verifier成功。
- **証拠:** summary、duration、shard結果。
- **停止条件:** C40-09以外のledger/timing、shard、provider workflow変更が必要、failureをfuture Epicで無視。
- **cleanup:** verifier temp outputはownership確認後。

## 14. M99 — Audit、Report、handoff

### C90-01 — Scope/no-touch diff audit

- **対象 / 目的:** approved scopeだけが変わったことを確認する。
- **前提:** M5完了。
- **操作:** 変更しない。
- **確認:** `git diff --name-status <implementation-baseline-sha>`、Historical authority、current skills/CI、Epic #384 pathsをpath限定diffし、`git diff <implementation-baseline-sha> -- pyproject.toml`をC30-01のexact decisionと照合する。
- **期待結果:** changed pathはC00-03のapproved inventoryのみ。追加したscripts READMEと三scopeのartifacts/discussions rulesの14 pathsは7 pairでbyte一致し、列挙外のsibling rules差分0。R/D/P/Report以外のIssue history差分0。managed distribution、workflow、scripts/quality差分0。ledger/timing/conftestはC40-09で承認したdeleted-node exact entry以外の差分0。`pyproject.toml`はdelegated member、`.codex` glob、およびS06 file削除時だけ専用S06 overrideに差分があり、その他entryの差分0。
- **証拠:** name-statusとno-touch results。
- **停止条件:** unrelated/unowned diff、S06 file/override不一致。
- **cleanup:** unintended diffを原因箇所で修正。user変更を消さない。

### C90-02 — After metrics/test budget

- **対象 / 目的:** stagingに依存しないworking-tree母集団で、testを含む撤退を数量確認する。
- **前提:** C90-01完了。C50-01以降のcandidate checkpointは既にindexにある。C90-02の計測目的では追加のstaging/index mutationを行わない。
- **操作:** `git ls-files -z -- tests`からworking treeに現存するtracked pathだけを明示listへ残し、missing tracked pathは除外する。`tests`配下のnon-ignored untracked pathがあれば計測前に停止する。collected countはC00-04と同じrepository全体のcollect-only、残る三指標は同じexisting tracked listから算出する。
- **確認:** repository rootで次のzsh blockをそのまま実行する。

  ```zsh
  export IMPLEMENTATION_BASELINE_SHA='<C00-01に記録した40桁full SHAへ一度だけ置換>'
  (
  set -euo pipefail
  printf '%s\n' "$IMPLEMENTATION_BASELINE_SHA" | rg -q '^[0-9a-f]{40}$'
  test "$(git rev-parse --verify "${IMPLEMENTATION_BASELINE_SHA}^{commit}")" = "$IMPLEMENTATION_BASELINE_SHA"
  C90_METRIC_DIR="$(mktemp -d)"
  trap 'c90_02_exit_status=$?; rm -rf -- "$C90_METRIC_DIR"; exit "$c90_02_exit_status"' EXIT
  TRACKED_LIST="$C90_METRIC_DIR/tracked-tests.zlist"
  UNTRACKED_LIST="$C90_METRIC_DIR/untracked-tests.zlist"
  COLLECT_OUTPUT="$C90_METRIC_DIR/collect-only.txt"
  git ls-files -z -- tests > "$TRACKED_LIST"
  typeset -a EXISTING_TRACKED_TESTS=()
  typeset -a EXISTING_TRACKED_TEST_PY=()
  typeset -a EXISTING_TRACKED_FIXTURES=()
  while IFS= read -r -d '' tracked_test_path; do
    if [[ ! -e "$tracked_test_path" ]]; then
      printf 'C90-02_EXCLUDED_MISSING_TRACKED=%s\n' "$tracked_test_path"
      continue
    fi
    EXISTING_TRACKED_TESTS+=("$tracked_test_path")
    [[ "$tracked_test_path" != *.py ]] || EXISTING_TRACKED_TEST_PY+=("$tracked_test_path")
    [[ "$tracked_test_path" != tests/fixtures/* ]] || EXISTING_TRACKED_FIXTURES+=("$tracked_test_path")
  done < "$TRACKED_LIST"
  git ls-files -z --others --exclude-standard -- tests > "$UNTRACKED_LIST"
  if [[ -s "$UNTRACKED_LIST" ]]; then
    while IFS= read -r -d '' untracked_test_path; do printf 'C90-02_NON_IGNORED_UNTRACKED=%s\n' "$untracked_test_path" >&2; done < "$UNTRACKED_LIST"
    exit 1
  fi
  (( ${#EXISTING_TRACKED_TESTS[@]} > 0 ))
  (( ${#EXISTING_TRACKED_TEST_PY[@]} > 0 ))
  uv run pytest --collect-only -q | tee "$COLLECT_OUTPUT"
  COLLECTED_TEST_COUNT="$(sed -nE 's/^([0-9]+) tests? collected.*$/\1/p' "$COLLECT_OUTPUT" | tail -n 1)"
  [[ -n "$COLLECTED_TEST_COUNT" ]]
  TRACKED_TEST_PY_LOC="$(wc -l "${EXISTING_TRACKED_TEST_PY[@]}" | awk 'END { print $1 }')"
  printf 'COLLECTED_TEST_COUNT=%s\nTRACKED_TEST_PY_LOC=%s\nTRACKED_TEST_FILE_COUNT=%s\nTRACKED_FIXTURE_FILE_COUNT=%s\n' \
    "$COLLECTED_TEST_COUNT" "$TRACKED_TEST_PY_LOC" "${#EXISTING_TRACKED_TESTS[@]}" "${#EXISTING_TRACKED_FIXTURES[@]}"
  git diff --numstat "$IMPLEMENTATION_BASELINE_SHA"
  rm -rf -- "$C90_METRIC_DIR"
  trap - EXIT
  )
  ```

- **期待結果:** `IMPLEMENTATION_BASELINE_SHA`がC00-01の40桁full SHAと一致する。non-ignored untracked path 0。unstaged deletionを含むmissing tracked pathは母集団から除外される。四指標純増なし、candidate coverage=1.0、removable closure=1.0、surviving tests保持。
- **証拠:** existing tracked path数、excluded missing path、collect summary、before/after/delta、`git diff --numstat`によるdeleted production/test LOCと情報比率。
- **停止条件:** baseline SHA未置換・非40桁・C00-01不一致、non-ignored untracked path、existing tracked母集団0、collection/parse error、未承認増加、candidate未決、positive coverage欠落、stagingを要求する手順、数字を稼ぐ削除。
- **cleanup:** `$C90_METRIC_DIR`だけをblock内で削除し、candidate listをrepository script/helper/testへ保存しない。

### C90-03 — SpecDock integrity

- **対象 / 目的:** canonical structureとprojectionを検証する。
- **前提:** diff確定。
- **操作:** `validate`、`sync --no-github`、再`validate`を実行する。
- **確認:** 各command outputとsync後status/diff。
- **期待結果:** 全成功、unrelated generated diffなし。
- **証拠:** command results。
- **停止条件:** syncがscope外tracked diffを生成。
- **cleanup:** scope外diffをcommitしない。

### C90-04 — Final cleanup、Report completion、candidate freeze

- **対象 / 目的:** 未実施捏造を防ぎ、証拠をhandoff可能にする。
- **前提:** C00-01〜C90-03のversion管理ledgerが全てPASSまたは理由付きN/A。
- **操作:** C60-01のimmediate path evidenceをbyte-for-byteで`ARTIFACT_DIR`と`CONSUMER`へ設定し、空でないこと、相互に異なること、各directoryが存在することを確認する。exact pathを出力後、`rm -rf -- "$CONSUMER" "$ARTIFACT_DIR"`を1回だけ実行し、両pathの不在を確認する。Plan §15の既存rowにある`状態`・`Evidence reference`のcell valueとReportの`Outcome`・`Verification`・`Residual Risks / Follow-ups`本文だけに実測事実を記録し、Evidence recording, classification, and repair-checkpoint ruleの`EVIDENCE_ONLY`であることをunstaged diff hunkごとに確認して該当Plan/Report pathだけをstageする。ledger header・ID・row set/orderや他のR/D/P本文は変更しない。その他の本Issue所有cacheもexact ownership確認後に削除・不在確認し、open repair windowがなく、unstaged/untracked差分0のfinal indexをcommit candidateとしてfreezeする。C90-04自身のPASSをPlan/Reportへ書かない。
- **確認:** `test -n "$ARTIFACT_DIR"`、`test -n "$CONSUMER"`、`test "$ARTIFACT_DIR" != "$CONSUMER"`、各`test -d`、cleanup前後のexact path出力、各`test ! -e`を実行する。その後、version管理ledgerとraw command evidence、Report内容、空の`git diff --name-status`、空のnon-ignored untracked一覧、`git diff --cached --name-status "$IMPLEMENTATION_BASELINE_SHA"`、`git diff --cached --check "$IMPLEMENTATION_BASELINE_SHA"`を照合する。
- **期待結果:** C60-01 success時に保持された二つのmktemp-owned directoryだけがexact pathで削除される。C00-01〜C90-03にNOT_RUN/BLOCKEDなし、N/Aは理由付き。Reportにactual changed/deleted/retained files、test metrics、verification、residual riskがあり、意図したtracked diffだけが残る。
- **証拠:** candidate freezeのPASS/BLOCKEDをPR/handoff evidenceへ記録し、version管理Plan/Reportには追記しない。
- **停止条件:** C60-01 evidenceとcleanup変数の不一致、empty/same/missing/unknown path、raw実行なしのPASS、final SHA自己参照、長いlog複製、unknown temporary/untracked path。
- **cleanup:** C60-01がsuccess時に保持したexact `$CONSUMER`と`$ARTIFACT_DIR`、およびownershipを証明できる本Issue所有temporary/duplicate scratch/logだけ。glob、prefix、parent directory、user-owned/unknown pathは削除しない。

### C90-05 — Commit、push、Strict quality gate、PR

- **対象 / 目的:** human merge判断へ固定candidateを渡す。
- **前提:** version管理ledgerのC00-01〜C90-03が完了し、C90-04 candidate freezeがhandoff evidence上でPASS、identity確認済み。
- **操作:** C90-04でfreezeしたfinal indexに追加stageがないことを確認してcommit/pushし、Issue #387参照PRを作る。cleanなfinal SHA上でもう一度`spec-dock validate`を実行してから、固定SHAでindependent ChatGPT code review/Final Quality Gateを実施する。`review_status=fail`またはP0/P1 findingによるtracked修正が必要ならfreezeを解除し、Evidence recording, classification, and repair-checkpoint ruleで分類して必要な再reviewまたは再実行を行い、Plan/Report/evidenceを新candidateへ再束縛し、新SHAでC90-05を最初から行う。P2/P3は記録するが、それだけを理由に修正・再reviewを必須にしない。
- **確認:** staged name-status、clean status、remote SHA、final SHA上のvalidate、PR checks、Strict review status。
- **期待結果:** pushed clean candidate、P0/P1=0、review pass、merge-ready PR。agentはmergeしない。
- **証拠:** final SHA、PR URL、checks/review summaryをversion管理Plan/ReportではなくPR/handoff evidenceへ記録する。これらの記録のためにreviewed SHAを変更しない。
- **停止条件:** identity不一致、unexpected staged path、`review_status=fail`、P0/P1 finding、CI failure。
- **cleanup:** なし。

## 15. Execution status ledger

初期状態はversion管理対象のC00-01〜C90-03の36 rowが全て`NOT_RUN`である。実装者は各milestone終了時に、既存rowの`状態`と短い`Evidence reference`のcell valueだけを更新する。このexact二列だけの実測更新は`EVIDENCE_ONLY`であり、既にPASSしたcheckを失効させない。column header、separator、`ID`列、row set/order、この説明本文を含むそれ以外のPlan hunkはすべて`SPECIFICATION_CONTRACT`である。C90-04とC90-05はfinal tracked contentの自己参照を避ける二つのexternal gateであるためversion管理ledgerへ含めず、PR/handoff evidenceだけで閉じる。実施済みでない項目を過去形にしない。

| ID | 状態 | Evidence reference |
|---|---|---|
| C00-01 | NOT_RUN | |
| C00-02 | NOT_RUN | |
| C00-03 | NOT_RUN | |
| C00-04 | NOT_RUN | |
| C00-05 | NOT_RUN | |
| C00-06 | NOT_RUN | |
| C00-07 | NOT_RUN | |
| C00-08 | NOT_RUN | |
| C10-01 | NOT_RUN | |
| C10-02 | NOT_RUN | |
| C10-03 | NOT_RUN | |
| C10-04 | NOT_RUN | |
| C20-01 | NOT_RUN | |
| C20-02 | NOT_RUN | |
| C20-03 | NOT_RUN | |
| C20-04 | NOT_RUN | |
| C20-05 | NOT_RUN | |
| C30-01 | NOT_RUN | |
| C30-02 | NOT_RUN | |
| C30-03 | NOT_RUN | |
| C40-01 | NOT_RUN | |
| C40-02 | NOT_RUN | |
| C40-03 | NOT_RUN | |
| C40-04 | NOT_RUN | |
| C40-05 | NOT_RUN | |
| C40-06 | NOT_RUN | |
| C40-07 | NOT_RUN | |
| C40-08 | NOT_RUN | |
| C40-09 | NOT_RUN | |
| C50-01 | NOT_RUN | |
| C50-02 | NOT_RUN | |
| C60-01 | NOT_RUN | |
| C60-02 | NOT_RUN | |
| C90-01 | NOT_RUN | |
| C90-02 | NOT_RUN | |
| C90-03 | NOT_RUN | |

## 16. Exit / handoff

次をすべて満たしたときだけproduction writerからmain agentへ返す。

- I387-AC01〜AC18のevidenceがある。
- version管理ledgerのC00-01〜C90-03が全てPASSまたは理由付きN/Aで、C90-04とC90-05がPR/handoff evidence上でPASSしている。
- production residueとremovable test/supportが一体で撤去されている。
- new absence test/scanner/fixture/helperがない。
- surviving positive behavior、provider/dogfood parity、package outputが確認済み。
- test budget、candidate coverage、removable closureが合格している。
- authoritative Historical evidence、current二skill、consumer CI、Epic #384 surfaceに意図しない差分がない。
- focused、lint、ordinary、current verifier、package/fresh consumer、validateの実結果がある。
- pushed clean branch、fixed final SHA、merge-ready PR、Strict quality gate pass、residual riskが明確である。
- open repair windowがなく、latest candidate/repair checkpointのunstaged/untracked差分が0で、全R/D/P hunkがfixed SHA Strict review済みである。
- human merge前に`issue finish`を実行していない。
