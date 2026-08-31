---
種別: 要件定義書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "approved"
最終更新: "2026-08-31"
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 1. 目的

Issue 357〜360で成立した「小さいStorage Core + Authoring Kit + agent-first lifecycle」を変更せず、現行利用者向けsurfaceに残る旧workflow、Profile、Assurance、Evidence Adoption Ledger（EAL）、delegated review、削除済みcommandの案内と内部compatibility seamを除去する。同時に、これら退役済み機能の不在だけを恒久監視するtest、fixture、helper、定数、mutation/scannerも、残存behaviorのconsumerでないことを確認したうえで撤去する。

完了後、利用者とagentはCurrent surfaceだけを読んで次を一意に判断できる。

- `active set`はlocal nodeを選択するだけである。
- branch checkout、unfinished active Issue guard、dependency readinessは`issue start`が所有する。
- Artifactはevidenceであり、採用内容はRequirement、Design、Planまたはaccepted ADRへ明示的に再記述する。
- active対象がないplaceholderは「active未設定」だけを示し、旧authoring workflowを要求しない。
- Current Authoring Kitは、現在存在する二つのrepo-local skillを現在形で案内する。
- Historical evidenceは旧語彙を含んでいても保持する。
- 廃止機能専用のtest supportはHistorical authorityではなく、機能と一緒に撤退できるtest infrastructureとして扱う。
- 削除確認は新しいabsence testへ固定せず、実装計画の一回限りのchecklistとReportの実測証拠で完結する。

本Issueは一つの「Current contractの収束」を扱うため`ONE_ISSUE`とする。installer、update、uninstall、managed distribution、provider test architectureを簡素化するEpic #384とは別Issueである。

## 2. 背景と確認済み状態

親Epic #356は、Planning、Review、Execution、Assurance、Profile routing、provider固有authoring、EAL gateをSpecDockのRuntime authorityから外した。依存Issue `iss-00357`〜`iss-00360`は完了済みであるが、次の残滓がCurrent surfaceに残っている。

1. `system/active-none/{initiative,epic,issue}/report.md`が旧delegated draft lifecycle、reviewer gate、Permission Profile、EAL、Promotion Recordを案内する。
2. root `README.md`が、削除済みの`active set --checkout`とEAL必須手順を案内する。
3. `docs/authoring/overview.md`がIssue #359完了前の未来形を残す。
4. public parserは`active set`をselection-onlyにしているが、`ActiveSetArgs`と`SetActiveRequest`は`force`、`checkout`、`use_github`、`issue_limit`等を保持し、`set_active()`からcheckoutできる。
5. `pyproject.toml`に実在しない`tests.cli_runtime.test_delegated_authoring`のmypy override member、`tests/cli_runtime/test_runtime_active_s06.py`撤去時に孤立する専用mypy override、実体のない`assets/install_root/.codex/**` package-data globがある。
6. Current-facing testには、削除済みroute/module/fieldの不在、旧語彙scanner、Historical exclusion、旧evidence mutationを恒久監視するretirement-only test supportが残っている。
7. Current-facing drift guardをroot READMEとactive-noneへ拡張すると、廃止項目が増えるたびにnegative test、phrase inventory、mutation testが増える。
8. `tests/unit/infra/test_init_update.py`にdefinition-only constant候補がある。

Strict planning baselineはbranch `iss-00387-current-surface-workflow-residue-cleanup`、SHA `93be5dbb5390f03d22e1ba882c7e2a38357f39c1`である。このSHAは仕様起草時の固定点であり、実装candidateではない。現時点でproduction implementation、test追加、test実行、PR作成は未実施である。

## 3. 用語

| 用語 | 定義 |
|---|---|
| Current surface | 現在の利用者またはagentがCurrent contractとして読む、実行する、または導入先へ配布されるsurface |
| Historical evidence | 過去状態を説明する資料の総称。保護対象かどうかはauthoritative evidenceとtest copyの分類に従う |
| residue | 退役済みbehaviorをCurrent instruction、schema、API capabilityまたはinventoryとして見せる残存物 |
| selection-only | nodeを解決してactive stateを更新するだけで、checkout、GitHub照会、dependency判定、unfinished guardを行わないこと |
| provider source | shipped assetまたはruntimeの正本である`src/spec_dock/assets/**` |
| dogfood projection | provider sourceから投影される`spec-dock/**`の対応asset |
| surviving behavior test | 現在残る利用者価値またはfailure semanticsを直接観測するdurable automated test |
| retirement-only test support | 廃止済み機能、語彙、path、fieldの不在・無視だけを証明するtest、fixture、helper、scanner、mutation、定数 |
| one-time evidence | 実装時に一度だけ取得し、PlanのchecklistとReportへ記録する`rg`、AST、diff、build inventory、fresh consumer等の証拠 |
| authoritative Historical evidence | `spec-dock/initiatives/**`、accepted ADR、Historical guide等の正本。test用copyやsynthetic fixtureは含まない |

## 4. スコープ

### 4.1 必須対象

- Current placeholder: provider/dogfoodの`system/active-none/{initiative,epic,issue}/report.md`
- Current documentation: `README.md`、provider/dogfoodの`docs/authoring/overview.md`
- active selection internal contract: provider/dogfoodの`commands/active.py`、`application/contracts.py`、`application/set_active.py`、call siteとしての`application/issue_lifecycle.py`
- package/test hygiene: `pyproject.toml`と既存のauthoring asset、set-active、issue lifecycle、doctor、storage-core、init/update test
- retirement-only test support: `tests/unit/infra/test_authoring_kit_assets.py`、`tests/unit/application/test_set_active.py`、`tests/cli_runtime/{test_storage_core_cli.py,test_issue_lifecycle.py,test_doctor.py,s09_invariance.py}`、関連fixture/helper/constant

### 4.2 条件付き対象

`_ISSUE_359_EXPECTED_CODEX_CONFIG`、`_REQUIRED_ISSUE_PROFILE_TEMPLATE_PATHS`等のdefinition-only候補、およびStrict分析で列挙したretirement-only test supportは、repository-wide searchとASTでsurviving behavior、dynamic lookup、fixture discoveryへの利用がないことを証明できた場合だけ削除する。旧語彙を含むという名前や見た目だけで削除せず、新たに見つけた無関係なdead codeは便乗削除しない。

### 4.3 明示的対象外

- `spec-dock/initiatives/**`の履歴。ただし本Issue自身のR/D/P/Report更新は除く。
- provider/dogfoodの`docs/authoring/historical.md`等のauthoritative Historical evidence。test用copyまたはsynthetic fixtureは自動的に対象外とせず、surviving consumerがなければ§4.2の条件付き撤去対象とする。
- 現在の二つのinstalled skillとconsumer `ci.yml`。
- `checkout_active_target()`のsignature、body、docstring、behavior。`issue start`が使用するCurrent coreとして保持する。
- `managed_distribution.py`、`managed_distribution.json`、journal/checkpoint/recovery、legacy identity catalog、uninstall/purge。
- provider workflow、shard、test lane policy、provider test portfolio再編。`full-regression-ledger.json`、`full-regression-timing-weights.json`、`tests/conftest.py`は原則対象外だが、本Issueで実際に削除するtest nodeへの参照を除くためのexact entry更新だけをreferential-integrity例外として許可する。
- `pyproject.toml`のI387-R06で明示したmodule member、条件付き専用override、package-data glob以外のentry、override structure、error-code policy。
- Epic #384のfixed skill slot、distribution root replacement、test simplificationの先取り。
- public CLI command、flag、JSON schema、exit codeの変更。
- repository全体をscanする新しいproduction linterやpolicy engine。

## 5. 機能要件

### I387-R01 — active-noneをminimal placeholderにする

三scopeのplaceholderは、active対象がないこと、編集対象でないこと、実際のReportのcanonical pathだけを示す。旧role、phase、reviewer、Profile、EAL、Promotion、failure-mode schemaを除去する。placeholder file自体は残す。

### I387-R02 — root READMEをCurrent lifecycleへ合わせる

`active set`をselection-onlyとして説明し、checkoutを伴う実装開始は`issue start`へ案内する。`active set --checkout`のexample、recovery案内、branch normalization説明を除去する。

### I387-R03 — Artifact authority flowをCurrent化する

Artifactはevidence-onlyであり、review/synthesis後に採用内容をR/D/Pまたはaccepted ADRへ明示的に再記述する、とroot READMEへ記載する。EALを必須手順またはauthority gateとして要求しない。

### I387-R04 — Authoring overviewを現在形にする

現在存在する`spec-dock`と`spec-dock-grill-with-docs`を現在形で案内する。provider sourceとdogfood projectionの両方で壊れない既存のcode-path表記契約を維持する。

### I387-R05 — active internal requestをtarget-onlyにする

- `ActiveSetArgs`は`target_ref`と表示用`target_display`だけを持つ。
- `SetActiveRequest`は`target`だけを持つ。
- `set_active()`はcheckoutを行わず、`ActiveSetResult.branch`は互換上`None`を返す。
- `issue start`は従来どおりdependency check後に`checkout_active_target()`を呼び、その後target-only requestでactive stateを書く。
- `active set`のpublic syntaxと結果表示は変更しない。

### I387-R06 — stale package/test residueを証拠付きで整理する

- mypy overrideの既存module listから実在しない`tests.cli_runtime.test_delegated_authoring`だけを除き、同じoverride内の現存moduleと`disable_error_code`は保持する。
- `tests/cli_runtime/test_runtime_active_s06.py`を削除する場合に限り、`module = "tests.cli_runtime.test_runtime_active_s06"`と`disable_error_code = ["assignment", "var-annotated"]`から成る専用`[[tool.mypy.overrides]]` entry全体を削除する。同test fileを保持する場合は専用entryを変更せず保持する。
- package-dataから実体のない`assets/install_root/.codex/**`だけを除く。
- current `.agents/**`と`.github/**` package-dataは保持する。
- 上記以外の`pyproject.toml` entry、override structure、error-code policyは変更しない。
- definition-only候補は§4.2のproof成立時だけ削除する。

### I387-R07 — 廃止機能専用のtest supportも撤退する

廃止済み機能の不在・無視だけを目的とするtest、fixture、helper、scanner、mutation、定数をinventory化し、各項目についてsurviving behaviorのconsumer有無を確認する。consumerがない項目はproduction residueと同じIssueで削除する。正のbehaviorも観測する混合testは、retirement-only assertionだけを除き、残存behaviorを検証する最小testへ縮小する。新しいnegative route test、phrase scanner、absence assertion、Historical exclusion testは追加しない。

### I387-R08 — provider-first projectionを維持する

shipped asset/runtimeはprovider sourceを先に変更し、dogfood projectionへ同期する。対象pairはbyte parityを保ち、projectionだけを独立編集しない。

### I387-R09 — 実装計画を一回限りの撤退checklistとして実行する

Planは、各確認項目に一意のID、対象、目的、前提、操作、確認command、期待結果、採取証拠、fail-closed停止条件、cleanup対象、実施状態を持つ。文書・設定・dead residue・retirement-only test supportの削除は、このchecklistで事前確認と実後確認を行い、実測をReportへ記録する。checklistを恒久pytestへ転記しない。

## 6. 非機能要件

### I387-N01 — 最小性

新しいproduction abstraction、compatibility mode、migration layer、feature flagを追加しない。既存のlayerとtest helperを利用する。

### I387-N02 — 履歴保全

authoritative Historical evidenceのbyteを本Issueのcleanup理由で変更しない。test copy/synthetic fixtureはauthorityではなく、I387-R07のconsumer分類に従う。

### I387-N03 — fail-closed

definition-only、phantom package-data、Epic #384 ownershipを証明できない場合は削除せず、未確定事項として停止またはhandoffする。

### I387-N04 — 比例的検証と再現性

TDDは、現在残るbehaviorに実質的変更があり、既存testで期待する失敗を再現できない場合だけ適用する。文書、設定、dead residue、retirement-only test supportの削除には新しいRED/absence testを作らず、Planのone-time checklistを使う。既存testで残存behaviorを十分に観測できる場合は新規testを追加しない。実行したcommand、結果、未実施checkを区別してReportへ記録する。fresh consumerはclean buildで一意に確定し、inventoryとdigestを採取した同一wheelのabsolute pathを`uvx --isolated --no-cache --from <exact-wheel-path>`へ渡して実行する。sdistは同じbuildのinventory evidenceとして検査するが、fresh consumer executionには使用しない。

### I387-N05 — distribution非変更

Epic #384が所有するdistribution semanticsとprovider test architectureを再設計しない。build/fresh initは変更の検証にだけ用いる。ただし、本Issueで削除するtest nodeを参照するledger/timing/required-nodeのexact entry削除または現存nodeへの最小更新は、現行verifierの参照整合を保つため本Issueが所有する。schema、policy、marker、shard、workflow、weight算出方法は変更しない。

### I387-N06 — test budget

原則としてcollected test count、tracked test Python LOC、tracked test file数、tracked fixture file数をimplementation baselineより増やさない。新しいtest file、fixture、scanner、mutation framework、Issue固有helperを追加しない。残存behaviorに未検出riskがあり新規test以外で観測できない場合は、実装前にRequirement/Design/Planを改訂して理由、最小範囲、相殺するretirementを承認し直す。本Issueの現行分析ではこの例外を予定しない。

## 7. 境界・失敗条件

- providerとdogfoodに差分が出た場合、片側をauthority化せずprovider sourceから再同期する。
- `issue start`のcheckout順序またはfailure behaviorが変わる場合、internal request縮小を完了扱いにしない。
- `.codex`のlive sourceまたはpackage consumerが見つかった場合、package-data entryを削除せず再調査する。
- `tests/cli_runtime/test_runtime_active_s06.py`のremove/retain判断と専用mypy overrideのremove/retainが一致しない場合は停止する。
- fresh consumerがinventory済みwheel以外、project path `.`、またはsdistを`--from`へ渡す場合は停止し、同一wheel artifactへ再束縛する。
- test assetがauthoritative Historical evidenceまたはsurviving behaviorの唯一の観測手段である場合、その項目の削除を止め、混合責務を分離できるか再判定する。
- checklist確認を自動化するために新しいabsence test/scannerが必要になった場合、その自動化を止め、one-time evidenceとして実行する。
- Epic #384所有fileの変更が必要になった場合、その作業を本Issueへ取り込まずEpic #384へ返す。
- 削除testのnode IDが`full-regression-ledger.json`、`full-regression-timing-weights.json`、`tests/conftest.py`に存在する場合、そのexact参照だけを同じcommitで除去する。別node、schema、policyへ影響する場合は停止する。
- Full Regression failureをledger/timing/shard変更で回避しない。I387-N05のdeleted-node exact参照更新はtest削除と同時に完了させ、failure後のsignature合わせやbaseline緩和には使わない。

## 8. 受け入れ条件

| ID | 条件 |
|---|---|
| I387-AC01 | 三scopeのactive-none provider/dogfood pairがminimal placeholderでbyte一致する |
| I387-AC02 | Current placeholderに旧delegated/reviewer/Profile/EAL/Promotion schemaがない |
| I387-AC03 | root READMEに`active set --checkout`のCurrent案内がなく、`issue start`へ案内する |
| I387-AC04 | root READMEがArtifactのevidence-only/canonical rewrite contractを説明し、EALを必須にしない |
| I387-AC05 | Authoring overviewが二skillを現在形で案内し、provider/dogfoodで一致する |
| I387-AC06 | `ActiveSetArgs`が`target_ref`/`target_display`、`SetActiveRequest`が`target`だけを持つ |
| I387-AC07 | `active set`がGit/GitHub/dependency portを呼ばずselection-only behaviorを維持する |
| I387-AC08 | `issue start`がdependency check → checkout → active writeの契約を維持する |
| I387-AC09 | `checkout_active_target()`に差分がない |
| I387-AC10 | `tests.cli_runtime.test_delegated_authoring` module memberとphantom package-data globがなく、S06 testを削除した場合だけ専用mypy override全体もなく、S06 testを保持した場合は同overrideが不変で残る。その他の`pyproject.toml` entryとcurrent install assetsは保持される |
| I387-AC11 | definition-only候補がproof成立時だけ削除され、判断結果がReportに残る |
| I387-AC12 | retirement-only test/support候補が100%分類され、削除可能項目とそのorphan supportが撤去され、保持項目にはsurviving consumerと理由がある |
| I387-AC13 | 新しいabsence test/scanner/fixture/helperを追加せず、collected test count、test LOC、test file数、fixture file数がbaselineから純増しない |
| I387-AC14 | version管理ledgerのC00-01〜C90-03がPASSまたは理由付きN/AでReportに追跡でき、candidate freeze C90-04とcommit/push/final validate/Strict/PR C90-05はfinal SHAを変えないPR/handoff evidenceで追跡できる |
| I387-AC15 | focused tests、lint、ordinary tests、current full-regression verifier、clean packageの実結果が記録され、fresh consumerはinventory/digest採取済みの同一exact wheelを`uvx --isolated --no-cache --from`で実行する。sdistはinventory evidenceとして検査され、project path `.`またはsdistをfresh consumerのexecution sourceにしない |
| I387-AC16 | current二skill、consumer CI、authoritative Historical evidence、Epic #384所有surfaceに意図しない差分がない |
| I387-AC17 | final candidate内容を含むSHAで`spec-dock validate`が成功し、Issue #387のR/D/P/Reportが履歴を捏造しない |
| I387-AC18 | 削除testを参照していたledger/timing/required-node entryが同じ変更で整合し、その他のFull Regression schema、policy、shard、workflow、weight算出方法に差分がない |

## 9. Traceability

| 観測対象 | 要件 | 主要な検証 |
|---|---|---|
| active-none / README / overview | R01〜R04, R08, R09 | one-time content review、provider/dogfood parity、fresh consumer |
| active selection | R05, N01, N04 | existing positive application/CLI/lifecycle tests、call-site audit |
| package/test hygiene | R06, R09, N03, N04, N05 | AST/reference proof、S06 testと専用mypy overrideの条件付きexact-entry audit、clean wheel/sdist inventory、同一wheel-bound fresh consumer |
| retirement-only test support | R07, R09, N04, N06 | consumer map、before/after metrics、deleted/retained decision ledger |
| Historical / Epic #384境界 | R07, N02, N05 | baseline diff auditと削除node参照のexact-entry audit。恒久exclusion testは作らない |
| Issue完了 | 全要件 | ordinary suite、current verifier、validate、actual Report、human PR gate |
