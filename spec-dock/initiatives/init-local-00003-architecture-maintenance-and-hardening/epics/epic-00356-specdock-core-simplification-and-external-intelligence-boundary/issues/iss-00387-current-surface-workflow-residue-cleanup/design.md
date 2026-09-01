---
種別: 設計書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "approved"
最終更新: "2026-09-01"
依存: ["requirement.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 1. 設計目標

新しい仕組みを追加せず、Current surfaceを親Epic #356の採用済み契約へ収束させる。

1. Current textは旧workflow authorityを提示しない。
2. `active set`のpublic behaviorとinternal request shapeをselection-onlyに一致させる。
3. provider sourceを正本とし、dogfood projectionとのparityを維持する。
4. Historical evidenceとEpic #384所有surfaceを変更対象から隔離する。
5. 廃止機能専用のtest supportをproduction residueと同時に撤退させ、削除の不在を監視する新しい恒久testを作らない。
6. Planをone-time manual verification checklist兼execution recordとして使い、確認漏れを恒久scannerではなく証拠付き手順で防ぐ。

## 2. Current / Target

| Surface | Current | Target |
|---|---|---|
| active-none report | 旧role、phase、reviewer、Profile、EAL、Promotion schemaを含む | active未設定・編集禁止・canonical pathだけを示す |
| root README | `active set --checkout`とEAL必須を案内 | selection-only、`issue start`、canonical rewriteを案内 |
| Authoring overview | Issue #359完了前の未来形 | 現在の二skillを現在形で案内 |
| active command args | parserにない旧flagのdefault値を内部へ運ぶ | targetと表示文字列だけを運ぶ |
| SetActiveRequest | targetのほかcheckout/GitHub/force系fieldを持つ | targetだけを持つ |
| set_active use case | `checkout=True`ならGit操作可能 | active stateのselection/writeだけを行う |
| issue start | helperでcheckout後、旧shape requestを生成 | helperでcheckout後、target-only requestを生成 |
| package config | stale mypy overrideとphantom glob | live inventoryだけを列挙 |
| retirement test support | removed route/module/field、旧語彙、Historical exclusion、旧evidence mutationを恒久監視 | consumerを分類し、retirement-only部分を削除 |
| verification | absence test追加によるRED/GREEN | surviving behaviorは既存test、削除確認はone-time checklist |

## 3. Authorityとprojection

### 3.1 Source of truth

- shipped docs/system/runtimeの正本は`src/spec_dock/assets/spec_dock/**`である。
- `spec-dock/**`はdogfood projectionである。
- root `README.md`と`pyproject.toml`はprovider repository固有の正本であり、projection pairを持たない。
- 本IssueのR/D/Pは履歴領域内であるが、本Issue自身のcanonical authorityとして通常どおり更新する。

### 3.2 更新順序

1. provider sourceを変更する。
2. 既存の同期経路またはbyte-exact copyで対応projectionを更新する。
3. `cmp`または既存parity testで一致を確認する。
4. projection側だけの修正で差分を隠さない。

### 3.3 Placeholder content contract

三scopeのreportは同じ意味を持ち、scope名とcanonical pathだけを変える。

```markdown
# No active <Scope>

現在 active な <Scope> はありません。
このファイルは active 未設定時の placeholder であり、編集対象ではありません。
実際の Report は `<canonical-node-path>/report.md` にあります。
```

exact wordingはprovider sourceを正本とし、実装時の`cmp`とfresh consumerで一回だけ確認する。文言を固定する新しいtest fixture、required/forbidden phrase assertion、template engineは作らない。

## 4. Active selectionの責務境界

### 4.1 Public command

`active set`の公開入力は現状どおり次の三形式である。

- positional target
- `--id`
- `--github-issue`

ここでいうGitHub issue numberはlocal linkageを解決するselectorであり、GitHub network accessの許可ではない。新しいflagやaliasを追加しない。

### 4.2 Command contract

```text
ActiveSetArgs
  target_ref: TargetRef
  target_display: str

SetActiveRequest
  target: TargetRef
```

`_active_set_args()`はparser結果からこの二fieldだけを構築し、`_run_active_set()`はtargetだけをuse caseへ渡す。

### 4.3 Application contract

`set_active()`の責務は次に限定する。

1. node recordsを読みgraphを構築する。
2. target nodeを解決する。
3. active chainを選択する。
4. manifest/context packを生成する。
5. rollback付きactive writeを行う。
6. `ActiveSetResult(branch=None, ...)`を返す。

`set_active()`はGit gateway、GitHub、dependency evaluation、unfinished guardを呼ばない。

### 4.4 Issue start contract

`issue start`は既存順序を維持する。

```text
unfinished active guard
  -> dependency readiness
  -> checkout_active_target()
  -> set_active(SetActiveRequest(target=...))
  -> sync
```

`checkout_active_target()`はこのIssueで変更しない。active request縮小は、checkout helperの削除や移動ではない。

### 4.5 Compatibility

- public help、target resolution、rendered result、exit codeは変更しない。
- `ActiveSetResult.branch`は既存result shape維持のため残し、`active set`では常に`None`とする。
- repository内のdirect `SetActiveRequest` call siteはcompile/testで全てtarget-onlyへ更新する。
- repository外のPython internal importはpublic stability保証の対象としない。新しいdeprecated wrapperは作らない。

## 5. 検証設計: surviving behaviorとone-time evidence

### 5.1 三つの検証分類

| Class | 対象 | 手段 | durableか |
|---|---|---|---|
| A: surviving behavior | selection-only、issue start ordering/failure、current CLI、provider/dogfood parity、current package output | 既存のpositive automated testを保持・最小更新 | durable |
| B: retirement evidence | 旧文言、旧field、dead config、orphan support、no-touch boundary | `rg`、AST、`git diff`、`cmp`、build/archive inventory、fresh init | one-time。Plan/Reportへ記録 |
| C: retirement-only support | removed route/module/fieldの不在、phrase scanner、Historical exclusion、legacy mutation、test copy | consumerを確認して削除。混合testはpositive部分だけ残す | 撤退対象 |

Class BをClass Aへ昇格させることは原則禁止する。すなわち、旧語句がないこと、旧pathがないこと、旧flagがparser errorになること、Historicalがscanner対象外であることを新しいpytestへしない。

### 5.2 Durable automated testとして残す契約

- `active set`の三selectorが成功し、invalid targetでwriteしない。
- `set_active()`がselection/writeを行い、Git/GitHub/dependency portを呼ばず`branch is None`を返す。
- `issue start`がguard、dependency readiness、checkout、active write、syncの順を守り、checkout/write failureで安全に止まる。
- retained root help、registry、leaf helpがCurrent CLIを提示する。
- provider/dogfood runtimeとshipped assetが一致する。
- source、wheel、sdist、installed resourcesがCurrent install-root inventoryを保持する。

同じ観測点を既存testが覆う場合、新規testを追加しない。既存testがretirement-only assertionを併せ持つ場合、そのassertionだけを削り、positive behaviorへ名前と責務を合わせる。

### 5.3 Known retirement candidates

実装者はPlanのconsumer inventoryを先に行い、次を機械的に削除せず、各候補を`remove`または`retain(reason)`へ分類する。

| Family | Known candidate | 推奨処置 |
|---|---|---|
| set-active compatibility | `test_internal_checkout_request_preserves_issue_start_compatibility`、legacy request helper args、専用Git stub | issue-startのpositive ordering testを保持したうえで削除・縮小 |
| removed CLI/runtime inventory | `REMOVED_HELP_ROUTES`、`REMOVED_RUNTIME_MODULES`、`REMOVED_APPLICATION_CONTRACT_SYMBOLS`、`REMOVED_USE_CASE_FIELDS`、関連absence test/helper | retained registry/import/parityだけを残して削除・分離 |
| removed flag rejection | direct `active set --checkout` parser-error test、helpの旧flag集合assertion | selector success/no-writeを残して削除 |
| authoring scanner | `CURRENT_LEGACY_VOCABULARY_PATTERNS`、`_current_vocabulary_violations()`、forbidden phrase detector、mutation/infix/Historical positive control | link/parity/current schemaのpositive testと分離して削除 |
| legacy active context pack | `tests/cli_runtime/test_runtime_active_s05.py`のAuthority、grants、Promotion、EAL contract test群とledger row | Current structural context-pack assertionを分離し、retirement-only test/assertionとexact ledger参照を撤去 |
| legacy active behavior | `tests/cli_runtime/test_runtime_active_s06.py`のforce/dependency/GitHub behavior test群、ledger row、専用mypy override | surviving selection-only/issue-start testを保持し、file/testを削除する場合だけexact ledger参照と専用mypy overrideを一体撤去。fileを保持する場合はoverrideも保持 |
| legacy flag fast node | `test_active_set_legacy_flag_reports_parser_error`と`REQUIRED_FAST_NODE_IDS`/timing weight entry | positive selector smokeを保持し、testとexact参照を一体撤去 |
| legacy evidence mutation | `S09_LEGACY_EVIDENCE_MUTATIONS`、`apply_s09_legacy_evidence_mutation`、`s09_invariance.py`とconsumer tests | current lifecycle/doctor behaviorの唯一の観測でなければ削除 |
| Historical test copy | preservation SHA/copy/mutation machinery、`tests/fixtures/authoring_kit/existing_issue/**` | authoritative originalを保持し、test-only copyであれば削除 |
| definition-only | Issue/Profile-era constants、orphan imports/helpers | reference、AST、dynamic discovery proof後に削除 |

### 5.4 Historical boundary

`spec-dock/initiatives/**`、accepted ADR、provider/dogfood `docs/authoring/historical.md`はauthoritative Historical evidenceとして変更しない。一方、`tests/fixtures/**`のcopyやsynthetic mutationはtest infrastructureであり、自動的な保存対象ではない。canonical source、runtime input、surviving positive testのconsumerがなければ撤去できる。

### 5.5 新規testの例外gate

新規testを許可するのは、現在残るbehaviorに新しいobservable riskがあり、既存testの最小更新、compile/type/lint、one-time evidenceのいずれでも検出できない場合だけである。実装者はcode追加前にR/D/Pへ、risk、失敗例、既存testで不足する理由、最小test、test budgetへの影響を追記し、再reviewする。本Issueの現行計画では例外を使わない。

## 6. Package/test hygiene

### 6.1 pyproject

変更対象を次に限定する。

- 無条件cleanup:
  - 既存の複数module mypy overrideから`tests.cli_runtime.test_delegated_authoring` memberだけを削除し、同じentryの現存moduleと`disable_error_code = ["var-annotated"]`を保持する。
  - package-dataから`assets/install_root/.codex/**`だけを削除する。
- 条件付きexact-entry cleanup:
  - `tests/cli_runtime/test_runtime_active_s06.py`を削除する場合に限り、`module = "tests.cli_runtime.test_runtime_active_s06"`と`disable_error_code = ["assignment", "var-annotated"]`から成る専用`[[tool.mypy.overrides]]` entry全体を削除する。
  - 同test fileを保持する場合は、専用entryを変更せず保持する。

`.agents/**`と`.github/**`はcurrent installed assetのため保持する。上記以外の`pyproject.toml` entry、override structure、error-code policyは変更しない。clean wheel/sdistの実inventoryでpackage-data削除の安全性を確認する。

### 6.2 Definition-only constants

候補ごとに次を満たす場合だけ削除する。

1. `rg`で定義以外の参照がない。
2. AST上の`Load`がない。
3. string/dynamic discoveryに使われない。
4. focused test、lint、collectionが成功する。

proofが成立しない候補は残し、理由をReportに記載する。このcleanupを理由に一般dead-code sweepを行わない。

### 6.3 Test budgetと撤退会計

implementation baselineとfinal candidateで次を同じcommandにより採取する。

- collected test count
- tracked `tests/**/*.py` LOC
- tracked test file数
- tracked fixture file数
- added/deleted production LOCとtest/support LOC

品質ゲートは次とする。

1. test count、test LOC、test file数、fixture file数はいずれも純増しない。
2. retirement candidate decision coverageは`decided / discovered = 1.0`。
3. `remove`判定したcandidateのclosureは`removed / removable = 1.0`。
4. surviving behaviorを観測するtestを誤って削除していない。
5. `deleted test LOC / max(1, deleted production LOC)`は情報として記録するが、値を稼ぐためにtestを削ることを防ぐため合否閾値にはしない。

削除可能なtest supportが発見された場合はtest/support deletionが0でないことを要求する。候補を全てretainする場合は、各項目にsurviving consumerの具体的証拠が必要である。

### 6.4 Exact build artifact binding

C60-01は専用の空の一時artifact directoryへ`uv build --clear --out-dir "$ARTIFACT_DIR" .`を1回だけ実行し、そdirectoryにexactly one wheelとexactly one sdistがあることを確認する。両artifactのabsolute path、SHA-256、archive inventoryを採取する。

fresh consumerのinstaller executionは、その場でinventoryした同一wheelのabsolute pathだけを`uvx --isolated --no-cache --from "$WHEEL" spec-dock init "$CONSUMER"`へ渡す。`--from .`、別build、sdist、artifact directoryだけを指定する代替は認めない。sdistはinventory evidenceとして保持するが、installation/execution sourceにはしない。Reportにはwheel/sdistのpathとdigest、exact `uvx` command、init/validate/cmp結果を対応付ける。

C60-01は最初の一時directory作成前にfailure trapを設定し、`ARTIFACT_DIR`と`CONSUMER`を各`mktemp -d`直後に記録する。nonzero終了時は同checkで作成済みのexact pathだけを削除する。success時だけtrapを解除し、C90-04が同じpath evidenceを照合してcleanupする。

C50-01開始前に、C00〜C40で承認されたcandidate pathとcurrent IssueのPlan/Reportだけをexplicit pathでGit indexへstageする。`git diff`が空、non-ignored untrackedが0、`git diff --cached`がapproved inventoryだけである状態をcandidate checkpointとする。これにより、C50以降に加えた編集はunstaged/untracked差分として直接観測でき、一時snapshot fileやshell session状態を持たない。

current R/D/P/Reportの`SPECIFICATION_CONTRACT`判定はC00-01開始後の全期間に適用し、C50-01の初回stage前snapshotでも次の境界を確認する。post-checkpointの全変更は三classへ分類する。

1. **EVIDENCE_ONLY:** current Planの§15に既に存在するC00-01〜C90-03の36 rowについて、`状態`列と`Evidence reference`列のcell valueだけを更新するhunk、またはcurrent Reportの既存`Outcome`、`Verification`、`Residual Risks / Follow-ups`本文へ実測事実だけを記録するhunk。Planのcolumn header、separator、`ID`列、row set/order、ledger前後の本文、およびReportの見出し・構造は含まない。該当hunkだけなら既存checkを失効させず、exact Plan/Report pathだけをstageしてunstaged/untracked 0へ戻せる。
2. **SPECIFICATION_CONTRACT:** current RequirementとDesignの全hunk、および1のexact二列cell value以外のcurrent Planの全hunk。Planのfront matter、Planning Level、改訂履歴、実装原則、検証分類、test budget、実行規約、milestone、各checkのID・8 field・command、external gate、ledger説明・header・ID・row set/order、Exit / handoffをすべて含む。Reportの見出し・構造変更も同じ扱いとし、許可領域と他領域が混在するhunkはfail-closedでこのclassにする。同一classification snapshotの別hunkに一件でもこのclassがあればsnapshot全体を`SPECIFICATION_CONTRACT`として扱い、他classのhunkもstageしない。C60-01保持物があればimmediate path evidenceと照合し、nonempty・distinct・directoryを確認してexact cleanupしてから、production writerは実装を`BLOCKED`としてmain agentへ返し、そのhunkまたはcurrent candidateを追加stage/commitしない。main agentはoriginal C00-01 implementation baselineから分離したclean worktree/branchでproduction/test/config差分0を確認し、改訂R/D/Pだけをcommit/pushしてfixed full SHAのindependent Strict reviewを完了する。その実装前treeからC00-01を新規実行し、旧candidateのstatus/evidenceは流用しない。
3. **OTHER_SUBSTANTIVE_OR_AMBIGUOUS:** 1、2以外のtracked hunk、non-ignored untracked追加、または分類不能な変更。最初の検出からrepair checkpoint成立までを一つのrepair windowとし、通常のcheck実行と通常のledger/Report evidence editを止める。repairはC00-03で承認済みのinventoryに含まれる既存pathだけに限定する。

`OTHER_SUBSTANTIVE_OR_AMBIGUOUS`の収束順序は一回のrepair windowごとに次で固定する。

1. C60-01 success時の一時directoryが残っていれば、immediate path evidenceとbyte-for-byte照合した旧`CONSUMER`と`ARTIFACT_DIR`だけをcleanupし、不在を確認する。旧wheel、digest、fresh consumer、verifier、audit結果をfinal evidenceから失効させる。
2. approved既存path上でrepairを完了する。新規path、rename先を含む未承認path、またはnon-ignored untracked pathが一件でも必要・出現した場合は、repair bundleの一部もstageせず`BLOCKED` handoffとする。
3. Plan ledgerのC50-01〜C90-03を`NOT_RUN`へ戻し、該当`Evidence reference` cellへexact string `INVALIDATED: OTHER_SUBSTANTIVE_OR_AMBIGUOUS repair; see Report Verification`を記録する。C90-04とC90-05もPR/handoff evidence上で`NOT_RUN`へ戻し、各Evidence referenceをexact string `INVALIDATED: OTHER_SUBSTANTIVE_OR_AMBIGUOUS repair`とする。C00-01〜C40-09のstatus/evidenceはoriginal implementation baselineまたは実装前観測へ束縛されたまま保持し、repair checkpoint上で再実行しない。Reportの`Verification`へ`class=OTHER_SUBSTANTIVE_OR_AMBIGUOUS; repair_paths=<approved paths>; invalidated=C50-01..C90-05; preimplementation=C00-01..C40-09 retained; temp_cleanup=<none|exact removed paths>`の一entryだけを記録する。
4. classified repair hunk、3の失効status、Plan/Reportのinvalidation evidenceを一つのunstaged repair bundleとして一度だけまとめて確認する。各hunkがapproved repairまたは3の記録だけであり、R/D/Pの`SPECIFICATION_CONTRACT` hunk、新規path、未承認pathを含まないことを確認する。
5. approved repair pathとexact current Plan/Report pathだけを、一回の`git add -- <explicit-path>...`でstageする。`git diff --name-status`が空、`git ls-files --others --exclude-standard`が空、`git diff --cached --name-status <implementation-baseline-sha>`がapproved inventoryだけであることを確認し、これをrepair checkpointとする。部分stage、`git add .`、glob、動的path展開は使わない。
6. repair checkpoint成立後、C50-01からC90-04までID順に再実行し、そのPASS後にC90-05を先頭から実行する。再実行中の後続`EVIDENCE_ONLY` editは通常規約どおり個別にstageできる。新たな`OTHER_SUBSTANTIVE_OR_AMBIGUOUS`を検出した場合だけ、新しいrepair windowとして同じ有限順序を最初から適用する。

after test metricsはstagingへ依存させない。`git ls-files -z -- tests`のうちworking treeに現存するpathだけをLOC/file/fixture指標の母集団とし、non-ignored untracked test pathがあれば計測前に停止する。collected countはC00-04と同じrepository全体の`uv run pytest --collect-only -q`を使い、個別のfilename patternでdiscoveryを再定義しない。

## 7. Checklistとexecution record

Planは38個のcheckを持つ。IDは各checkの見出しとして固定し、各checkは次の8 fieldを一つずつ過不足なく持つ。field外の共通規約はこの8 fieldの構成に数えず、補足規約として扱う。

| Field | 意味 |
|---|---|
| 対象 / 目的 | 何を、なぜ確認するか |
| 前提 | 実行可能になる条件 |
| 操作 | production/test/docsへの具体的変更 |
| 確認 | 一回限りのmanual evidenceまたは既存test |
| 期待結果 | PASSの観測可能な条件 |
| 証拠 | Reportへ要約するoutput/diff/metric |
| 停止条件 | 続行せず仕様判断へ戻す条件 |
| cleanup | temp/build/cache/orphan support |

状態語彙は`NOT_RUN`、`PASS`、`BLOCKED`、`N/A(reason)`とする。version管理status ledgerはC00-01〜C90-03の36 rowだけを持ち、C90-04とC90-05はfinal SHAを変更しない二つのexternal gateとしてPR/handoff evidenceへ記録する。command未実行、policy skip、対象test未collectionをPASSにしない。ledgerの既存rowにある`状態`と`Evidence reference`のcell value、およびReportの3実測欄だけの更新は6.4の`EVIDENCE_ONLY` editとして扱い、記録行為だけでcheckを自己失効させない。それ以外のR/D/P hunkはすべて`SPECIFICATION_CONTRACT`である。詳細な長いlogはReportへ複製せず要約と参照だけを残す。

## 8. Epic #384との境界

本IssueはCurrent contentと内部selection seamをcleanにし、Epic #384が扱うdistribution/test redesignの入力を単純化するだけである。次には触れない。

- managed asset ownership/manifestの置換
- fixed skill slot marker
- journal/checkpoint/recovery
- legacy identity catalog
- uninstall/purge semantics
- Full Regression schema、failure disposition、shard、provider workflow、timing weight算出方法、およびdeleted-node exact参照以外のledger/timing entry
- provider test portfolioの削減・統合

package buildとcurrent full-regression verifierは非回帰確認として実行するが、その構成やpolicyを変更しない。一方、削除したtest nodeを参照する`full-regression-ledger.json`、`full-regression-timing-weights.json`、`tests/conftest.py`のexact entryはreferential-integrity projectionとして同時に除去する。これはschema、failure disposition、marker、shard、workflow、weight算出方法の再設計を許可しない。

## 9. Data、failure、recovery

### 9.1 Data migration

不要。node metadata、consumer user data、Historical document、schema、distribution stateを変更しない。

### 9.2 Failure handling

| Failure | 処置 |
|---|---|
| provider/dogfood不一致 | provider sourceを確認し再同期する |
| active setがGit portを呼ぶ | request contractionを未完了とし、application testから修正する |
| issue start regression | public `active set --checkout`を復活させず、call site/orderingをforward-fixする |
| live `.codex` assetを発見 | phantom判定を撤回しpackage config削除を止める |
| S06 testと専用mypy overrideのremove/retain不一致 | C20-04のtest decisionとC30-01のexact entry処理を一致させ、無関係overrideを変更せず再確認する |
| fresh consumerがinventory済みwheel以外を実行 | `--from .`、sdist、別buildを止め、同一absolute wheel pathとdigestへ再束縛してC60-01を再実行する |
| C60-01がnonzero終了 | failure trapで作成済みの`CONSUMER`と`ARTIFACT_DIR`だけをexact pathで削除し、残存の有無を記録する |
| C90-02でnon-ignored untracked test pathを検出 | 四指標の計測前に停止し、stagingで隠さない |
| Requirement/Design hunk、またはexact ledger二列以外のPlan hunkを検出 | C60保持物をexact cleanupし、`SPECIFICATION_CONTRACT`としてstageせずBLOCKED handoffする。original baseline由来の実装前treeでclean fixed SHA Strict再review後にC00-01から新規実行する |
| OTHER repairに新規・未承認pathが必要、またはrepair checkpointでunstaged/untracked 0にならない | repair bundleを一部もstageせずBLOCKED handoffする |
| test candidateがsurviving behaviorの唯一の観測 | 削除を止め、retirement-only assertionだけを分離できるか再設計する |
| checklistを恒久testへ転記したくなる | 自動化を止め、one-time evidenceとReport記録へ戻す |
| test budgetが純増 | 新規test/supportを除去する。例外が必要なら実装を止めR/D/Pを再承認する |
| Epic #384 file変更が必要 | 本Issueから除外しEpic #384へhandoffする |
| 削除nodeへのledger/timing/required-node参照 | exact entryだけを同時に除去し、他entryまたはpolicyへ波及するなら停止する |
| Full Regression failure | C40-09のdeleted-node exact参照更新をfailure前に確定し、それ以外のledger/timing/shardを変更せず原因diffを修正する |

### 9.3 Rollback

変更をdocs/placeholder、active request、package hygieneの小さいcommit境界に分ける。data migrationがないため各境界を独立revertできる。旧workflow schemaや`active set --checkout`をfallbackとして再導入しない。

## 10. Verification matrix

| 設計観測点 | Test surface |
|---|---|
| placeholder/README/overview | one-time content review、`cmp`、fresh init。新しいphrase testは作らない |
| request shape | `rg`/AST/call-site audit、compile。field absence専用testは作らない |
| selection-only | 既存`tests/unit/application/test_set_active.py`のpositive behavior |
| issue start ordering | `tests/cli_runtime/test_issue_lifecycle.py` |
| package config/archive | delegated member、条件付きS06専用override、package-dataのexact diff audit。clean buildのwheel/sdist inventoryを採取し、同一wheelだけを`uvx --isolated --no-cache --from`へ渡す。stale path不在testは作らない |
| source/projection parity | existing `cmp`/parity assertions |
| overall non-regression | ordinary `uv run pytest`、current verifier、fresh init、`spec-dock validate` |
| retirement test support | consumer map、deletion diff、before/after metrics、remaining positive suite |
| no-touch boundary | implementation baselineからのpath diff audit。恒久exclusion testは作らない |

## 11. 代替案と却下理由

| 案 | 判断 | 理由 |
|---|---|---|
| docsだけ直す | 却下 | internal checkout capabilityとrequest driftが残る |
| internal seamだけ直す | 却下 | Current利用者への誤案内が残る |
| repository-wide旧語彙ban | 却下 | Historical evidenceとmigration説明を破壊する |
| Current surface限定drift guard | 却下 | 廃止のたびにinventory、negative assertion、mutation testが増える |
| 削除確認を一切しない | 却下 | orphan support、配布欠落、責務回帰を見逃す |
| 全削除をTDD化 | 却下 | 一回限りの不在確認を恒久test debtへ変える |
| manual checklist + surviving positive tests | 採用 | 撤退確認を完結させながらdurable suiteを小さくできる |
| `checkout_active_target()`も削除 | 却下 | `issue start`のCurrent behaviorを壊す |
| Epic #384と同時実装 | 却下 | owner、failure boundary、review範囲が混ざる |
| compatibility wrapper/feature flag | 却下 | public surfaceは既に削除済みで、複雑性を再導入する |
| 本設計の限定cleanup | 採用 | Current contractを一つのIssueで最小に収束できる |

## 12. 要件対応

| 要件 | 設計 |
|---|---|
| R01〜R04, R08, R09 | §3、§5、§7 |
| R05 | §4 |
| R06 | §6 |
| R07 | §5、§6 |
| N01〜N06 | §3〜§9 |
| AC01〜AC18 | §10とPlanのchecklist/status ledger |
