---
種別: 要件定義書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "draft"
最終更新: "2026-08-31"
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 1. 目的

Issue 357〜360で成立した「小さいStorage Core + Authoring Kit + agent-first lifecycle」を変更せず、現行利用者向けsurfaceに残る旧workflow、Profile、Assurance、Evidence Adoption Ledger（EAL）、delegated review、削除済みcommandの案内と内部compatibility seamを除去する。

完了後、利用者とagentはCurrent surfaceだけを読んで次を一意に判断できる。

- `active set`はlocal nodeを選択するだけである。
- branch checkout、unfinished active Issue guard、dependency readinessは`issue start`が所有する。
- Artifactはevidenceであり、採用内容はRequirement、Design、Planまたはaccepted ADRへ明示的に再記述する。
- active対象がないplaceholderは「active未設定」だけを示し、旧authoring workflowを要求しない。
- Current Authoring Kitは、現在存在する二つのrepo-local skillを現在形で案内する。
- Historical evidenceは旧語彙を含んでいても保持する。

本Issueは一つの「Current contractの収束」を扱うため`ONE_ISSUE`とする。installer、update、uninstall、managed distribution、provider test architectureを簡素化するEpic #384とは別Issueである。

## 2. 背景と確認済み状態

親Epic #356は、Planning、Review、Execution、Assurance、Profile routing、provider固有authoring、EAL gateをSpecDockのRuntime authorityから外した。依存Issue `iss-00357`〜`iss-00360`は完了済みであるが、次の残滓がCurrent surfaceに残っている。

1. `system/active-none/{initiative,epic,issue}/report.md`が旧delegated draft lifecycle、reviewer gate、Permission Profile、EAL、Promotion Recordを案内する。
2. root `README.md`が、削除済みの`active set --checkout`とEAL必須手順を案内する。
3. `docs/authoring/overview.md`がIssue #359完了前の未来形を残す。
4. public parserは`active set`をselection-onlyにしているが、`ActiveSetArgs`と`SetActiveRequest`は`force`、`checkout`、`use_github`、`issue_limit`等を保持し、`set_active()`からcheckoutできる。
5. `pyproject.toml`に退役済みtest moduleのmypy overrideと、実体のない`assets/install_root/.codex/**` package-data globがある。
6. Current-facing drift guardがroot READMEとactive-none placeholderを検査しない。
7. `tests/unit/infra/test_init_update.py`にdefinition-only constant候補がある。

Strict planning baselineはbranch `iss-00387-current-surface-workflow-residue-cleanup`、SHA `93be5dbb5390f03d22e1ba882c7e2a38357f39c1`である。このSHAは仕様起草時の固定点であり、実装candidateではない。現時点でproduction implementation、test追加、test実行、PR作成は未実施である。

## 3. 用語

| 用語 | 定義 |
|---|---|
| Current surface | 現在の利用者またはagentがCurrent contractとして読む、実行する、または導入先へ配布されるsurface |
| Historical evidence | 過去のIssue、Artifact、ADR、Report、Discussion、fixture、Historical guide等、変更せず保持すべき証跡 |
| residue | 退役済みbehaviorをCurrent instruction、schema、API capabilityまたはinventoryとして見せる残存物 |
| selection-only | nodeを解決してactive stateを更新するだけで、checkout、GitHub照会、dependency判定、unfinished guardを行わないこと |
| provider source | shipped assetまたはruntimeの正本である`src/spec_dock/assets/**` |
| dogfood projection | provider sourceから投影される`spec-dock/**`の対応asset |
| drift guard | 明示したCurrent surfaceが採用済みcontractから逸脱したときに失敗するtest-only assertion |

## 4. スコープ

### 4.1 必須対象

- Current placeholder: provider/dogfoodの`system/active-none/{initiative,epic,issue}/report.md`
- Current documentation: `README.md`、provider/dogfoodの`docs/authoring/overview.md`
- active selection internal contract: provider/dogfoodの`commands/active.py`、`application/contracts.py`、`application/set_active.py`、call siteとしての`application/issue_lifecycle.py`
- package/test hygiene: `pyproject.toml`と既存のauthoring asset、set-active、issue lifecycle、storage-core、init/update test

### 4.2 条件付き対象

`_ISSUE_359_EXPECTED_CODEX_CONFIG`、`_REQUIRED_ISSUE_PROFILE_TEMPLATE_PATHS`等のdefinition-only候補は、repository-wide searchとASTで定義以外の参照、dynamic lookup、fixture discoveryへの利用がないことを証明できた場合だけ削除する。新たに見つけた無関係なdead codeは便乗削除しない。

### 4.3 明示的対象外

- `spec-dock/initiatives/**`の履歴。ただし本Issue自身のR/D/P/Report更新は除く。
- provider/dogfoodの`docs/authoring/historical.md`とhistorical preservation fixture。
- 現在の二つのinstalled skillとconsumer `ci.yml`。
- `checkout_active_target()`のsignature、body、docstring、behavior。`issue start`が使用するCurrent coreとして保持する。
- `managed_distribution.py`、`managed_distribution.json`、journal/checkpoint/recovery、legacy identity catalog、uninstall/purge。
- `full-regression-ledger.json`、`full-regression-timing-weights.json`、provider workflow、shard、test lane policy、provider test portfolio再編。
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

- mypy overrideから実在しない`tests.cli_runtime.test_delegated_authoring`だけを除く。
- package-dataから実体のない`assets/install_root/.codex/**`だけを除く。
- current `.agents/**`と`.github/**` package-dataは保持する。
- definition-only候補は§4.2のproof成立時だけ削除する。

### I387-R07 — Current-facing drift guardを追加する

既存testへ明示的なCurrent path inventoryを追加し、root README、active-none、authoring overview、active request contractの退行を検出する。Historical path、migration-only説明、removed-route negative test、Epic #384文書はscan対象外とする。raw repository-wide word banは作らない。

### I387-R08 — provider-first projectionを維持する

shipped asset/runtimeはprovider sourceを先に変更し、dogfood projectionへ同期する。対象pairはbyte parityを保ち、projectionだけを独立編集しない。

## 6. 非機能要件

### I387-N01 — 最小性

新しいproduction abstraction、compatibility mode、migration layer、feature flagを追加しない。既存のlayerとtest helperを利用する。

### I387-N02 — 履歴保全

Historical evidenceのbyteを本Issueのcleanup理由で変更しない。Current scanのfalse positiveは履歴を直さずinventory境界を直す。

### I387-N03 — fail-closed

definition-only、phantom package-data、Epic #384 ownershipを証明できない場合は削除せず、未確定事項として停止またはhandoffする。

### I387-N04 — TDDと再現性

behavior変更は先に失敗testを追加し、REDを確認してから実装する。実行したcommand、結果、未実施checkを区別してReportへ記録する。

### I387-N05 — distribution非変更

Epic #384が所有するdistribution semanticsとprovider test architectureに差分を作らない。build/fresh initは変更の検証にだけ用いる。

## 7. 境界・失敗条件

- providerとdogfoodに差分が出た場合、片側をauthority化せずprovider sourceから再同期する。
- `issue start`のcheckout順序またはfailure behaviorが変わる場合、internal request縮小を完了扱いにしない。
- `.codex`のlive sourceまたはpackage consumerが見つかった場合、package-data entryを削除せず再調査する。
- Current guardがHistorical fileを違反扱いした場合、Historical fileを変更せずguardのinventoryを修正する。
- Epic #384所有fileの変更が必要になった場合、その作業を本Issueへ取り込まずEpic #384へ返す。
- Full Regression failureをledger/timing/shard変更で回避しない。

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
| I387-AC10 | stale mypy overrideとphantom package-data globがなく、current install assetsがpackageに残る |
| I387-AC11 | definition-only候補がproof成立時だけ削除され、判断結果がReportに残る |
| I387-AC12 | Current drift guardが違反を検出し、Historical evidenceを対象にしない |
| I387-AC13 | focused tests、lint、ordinary tests、current full-regression verifier、clean package/fresh initの実結果が記録される |
| I387-AC14 | current二skill、consumer CI、historical fixtures、Epic #384所有surfaceに意図しない差分がない |
| I387-AC15 | `spec-dock validate`が成功し、Issue #387のR/D/P/Reportが履歴を捏造しない |

## 9. Traceability

| 観測対象 | 要件 | 主要な検証 |
|---|---|---|
| active-none / README / overview | R01〜R04, R07, R08 | authoring asset test、exact content、provider/dogfood parity |
| active selection | R05, N01, N04 | application test、CLI negative test、issue lifecycle test |
| package/test hygiene | R06, N03, N05 | init/update test、AST/reference proof、clean wheel/sdist inventory |
| Historical / Epic #384境界 | R07, N02, N05 | explicit exclusion test、diff audit |
| Issue完了 | 全要件 | ordinary suite、current verifier、validate、actual Report、human PR gate |
