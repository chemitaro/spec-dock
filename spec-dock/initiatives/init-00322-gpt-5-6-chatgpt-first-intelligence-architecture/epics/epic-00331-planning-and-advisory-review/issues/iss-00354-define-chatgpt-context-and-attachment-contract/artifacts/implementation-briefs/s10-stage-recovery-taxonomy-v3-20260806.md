# iss-00354 S10 実装着手可否 再評価ブリーフ v3 — Oracle 0.17.0 producer binding

## 0. 固定 identity と判定

| 項目                               | 確認値                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------- |
| Repository                       | `chemitaro/spec-dock`                                                                 |
| Named branch                     | `codex/iss-00354-chatgpt-context-contract`                                            |
| Current pushed HEAD              | `c45cb102bc956807820073022e7ecd66db1b27c1`                                            |
| Branch parity                    | named branch tip と current HEAD は `identical`、ahead `0`、behind `0`                    |
| Default branch fallback          | 使用していない                                                                               |
| Current `report.md` Git blob     | `70d81025563664b458c042e8d860c00dabf8291d`                                            |
| Oracle package version           | `0.17.0`                                                                              |
| Oracle source snapshot identity  | `9fb87d9326ab1c07216f1eb904917013df6d9270`                                            |
| Oracle source identity authority | 添付source bundleおよび既存EAL-084に記録されたidentity。SpecDock GitHub connectorによる独立commit確認値ではない |
| Prior blocked evidence           | `EAL-083`                                                                             |
| Prior partial source adoption    | `EAL-084`                                                                             |
| 今回の判定                            | **S10 production implementationは引き続き blocked**                                        |
| `closure_claim`                  | `none`                                                                                |
| Fresh Red review                 | 未開始                                                                                   |

GitHub connectorで指定named branchと`c45cb102bc956807820073022e7ecd66db1b27c1`の完全一致を確認した。Default branchまたは別branchは参照していない。

**実装開始を許可しない理由:** 今回のOracle sourceにより、`prompt-reconstruction-mismatch`、`attachment-send-not-ready`、`response incomplete`については実行時producerを特定できた。しかし、現在のSpecDock invocationが後から読む`meta.json`へ、`artifact pending`と`transfer failed`を閉じた値として永続化するproducerは確認できない。さらに、前二つのpre-submit failureはsource上では送信前であることを証明できるが、exact codeごとの`performSessionRun → meta.json` positive fixtureと明示的な`promptSubmitted=false` persistenceは存在しない。

Canonical要件はfailure stageを混同せず、submission evidenceが不明な場合に推測せず停止すること、pre-submit new executionとpost-submit same-session recoveryを分離することを要求する。 Canonical designもOracle field名の解釈をversion-private parserへ閉じ、ambiguous evidenceをBooleanへ推測変換しないとしている。 Canonical planは五分類、exact public mapping、最大一回のnew execution、各一回のharvest/captureをS10の一つの閉じたchange-setとして要求する。

EAL-083とEAL-084は、当時のblocked判断およびstorage/core schemaだけを部分採用した履歴として変更しない。現在のreportも未解決blocked entryがpromotionとimplementation startを止める契約を明記している。

---

## 1. 再評価対象とauthority境界

### 1.1 Oracle一次証拠として読んだ論理ファイル

```text
workspace/tools/oracle/package.json
workspace/tools/oracle/src/oracle/types.ts
workspace/tools/oracle/src/oracle/errors.ts
workspace/tools/oracle/src/browser/actions/promptComposer.ts
workspace/tools/oracle/src/browser/attachments.ts
workspace/tools/oracle/src/browser/sessionRunner.ts
workspace/tools/oracle/src/browser/artifacts.ts
workspace/tools/oracle/src/cli/sessionRunner.ts
workspace/tools/oracle/src/remote/client.ts
workspace/tools/oracle/src/sessionManager.ts

workspace/tools/oracle/tests/browser/promptComposer.test.ts
workspace/tools/oracle/tests/cli/sessionRunner.test.ts
workspace/tools/oracle/tests/remote/server.test.ts
```

### 1.2 維持するSpecDock境界

Current SpecDockはexact `0.16.1`／`0.17.0` profile、profile-owned browser/session builders、completed-only 0.17 decoderを持つ。

一方、current runtimeは依然としてprocess nonzero／timeoutまたはnonterminal sessionを条件に、submission evidenceを読まずsame-session recoveryへ進む。 Current artifact readerもstatus、completed ZIP、validationを読むが、attempt stageを読むentry pointは持たない。

S09 direct receiptが実測したtransfer stateは`not-needed`だけであり、独立artifact-pendingは未観測である。 Inline receiptもcompleted ZIPを確認したが、独立pending stateやtransfer failureを確認していない。

---

## 2. Oracle `meta.json` のversion-bound入力境界

### 2.1 Exact path

Oracle `0.17.0`のsession metadata正本は次である。

```text
<Oracle home>/sessions/<session-id>/meta.json
```

SpecDockが読んでよいのは、当該Oracle executionのために自ら生成したexact `session_id`から導出した一件だけとする。

```text
session_root = _oracle_home(child_env) / "sessions" / session_id
metadata_path = session_root / "meta.json"
```

禁止:

```text
Path.home()
~/.oracle の直接参照
sessions/ の列挙
最新sessionの探索
glob / rglob
Oracle user configの解析
ChatGPT-Use wrapper receiptの参照
stdout / stderrの分類
process exit codeからのstage推定
```

### 2.2 Reader入力

将来unblockされた場合、version-bound readerへ渡す最小入力は次だけとする。

```text
session_root
session_id
oracle_version
profile_id
logical_model
attachment_mode
```

`session_root`はOracle invocation境界が構成し、readerがユーザーhomeから再探索しない。

### 2.3 読取可能なstructured surface

Oracle sourceは次のfield surfaceを定義する。

```text
id
status
mode
browser.runtime.promptSubmitted
browser.modelSelection
browser.warnings
response.status
response.incompleteReason
transport.reason
error.category
error.details
artifacts[].kind
artifacts[].validation
artifacts[].transfer.status
artifacts[].origin.mode
lifecycle
```

Artifact transfer typeには次のliteralが宣言されている。

```text
not-needed
ready
streaming
completed
failed
skipped
```

ただし、**型にliteralが存在することと、current runtimeがその値を`meta.json`へ書くことは別証拠である**。

---

## 3. 五分類のproducer／persistence再評価

| 分類                             | Runtime producer                                                                    | `meta.json`への実際のbinding                                                                                                           | Producer結合test                                                     | 判定                                    |
| ------------------------------ | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------- |
| Prompt reconstruction mismatch | `src/browser/actions/promptComposer.ts:591-628`                                     | `error.category="browser-automation"`、`error.details.stage="submit-prompt"`、`error.details.code="prompt-reconstruction-mismatch"` | producer単体testあり。Exact codeを`performSessionRun`経由でpersistするtestなし  | **分類sourceは十分、retry gateは部分的**        |
| Attachment send not ready      | `src/browser/actions/promptComposer.ts:1121-1133`                                   | `error.category="browser-automation"`、`error.details.stage="submit-prompt"`、`error.details.code="attachment-send-not-ready"`      | timeout producer testあり。Exact codeのsession persistence testなし      | **分類sourceは十分、inline retry gateは部分的** |
| Response incomplete            | `src/cli/sessionRunner.ts` assistant-timeout branch                                 | `browser.runtime.promptSubmitted=true`、`response.status="incomplete"`、`response.incompleteReason="incomplete-capture"`            | exact integrated `performSessionRun` testあり                        | **十分**                                |
| Artifact pending               | transfer typeの`ready`／`streaming`、remote eventの`artifact-ready`／`artifact-progress` | Current local session metadataへ`ready`／`streaming`を書き込むproducerなし                                                                 | bridge event testのみ。`meta.json` positive fixtureなし                 | **不十分**                               |
| Transfer failed                | remote clientのtransfer catch                                                        | Browser result warning `code="remote-artifact-transfer-failed"`。`artifacts[].transfer.status="failed"`は書かれない                      | remote client result testあり。Current session metadata persistenceなし | **不十分**                               |

---

## 4. 分類別の詳細判断

### 4.1 `prompt-reconstruction-mismatch`

#### Producer

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts
lines 591–628
symbol reconstructMultilinePrompt
```

三つのreconstruction failureはいずれも次の`BrowserAutomationError`を生成する。

```json
{
  "category": "browser-automation",
  "details": {
    "stage": "submit-prompt",
    "code": "prompt-reconstruction-mismatch",
    "promptLength": "<integer>",
    "observedLength": "<integer>"
  }
}
```

Producer testはexact code、length fields、raw prompt非保持を確認している。 

`BrowserAutomationError`のcategoryは`browser-automation`であり、CLI runnerのgeneric catchは`category`と`details`をそのままsession updateへ渡す。 

#### Submission boundary

Reconstructionはsend button処理より前に発生し、`onPromptSubmitted`はsend dispatch後にだけ呼ばれる。したがってsource上はpre-submitである。

ただし、新規sessionのerror metadataでは`browser.runtime.promptSubmitted`が明示的な`false`ではなく**欠落する可能性がある**。Current S10 v2 gateはmissingをFalseへ変換することを禁止している。

#### 採用可能範囲

安全に採用できること:

```text
exact failure classification
public blocked / oracle_prompt_reconstruction_mismatch
harvest count = 0
capture count = 0
new execution count = 0
```

現時点で採用しないこと:

```text
missing promptSubmitted を false とみなすこと
generic pre-submit retry eligibility
```

Prompt reconstruction mismatch自体はretry対象ではないため、分類とblock mappingはsourceから閉じられる。しかし五分類全体のproduction integrationは別の不足により開始しない。

---

### 4.2 `attachment-send-not-ready`

#### Producer

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts
lines 1121–1133
symbol attemptSendButton
```

Attachment付きsend buttonがdeadline内にclickableにならない場合、次を生成する。

```json
{
  "category": "browser-automation",
  "details": {
    "stage": "submit-prompt",
    "code": "attachment-send-not-ready",
    "attachmentNames": ["<private>"],
    "timeoutMs": "<integer>"
  }
}
```

Producerは`onPromptSubmitted`より前である。Attachment send timeout testも、attachment時はEnter fallbackへ進まずerrorになることを確認している。

#### Privacy boundary

SpecDock readerが参照してよいのは次の三scalarだけである。

```text
error.category
error.details.stage
error.details.code
```

参照・公開禁止:

```text
attachmentNames
timeoutMs
error.message
raw attachment path
```

#### 未確定部分

Exact `attachment-send-not-ready`を`performSessionRun`へ投入し、final session updateで次を確認するtestがない。

```text
status=error
error.category=browser-automation
error.details.stage=submit-prompt
error.details.code=attachment-send-not-ready
browser.runtime.promptSubmitted=false
```

Source orderingはpre-submitを示すが、current metadata contractではexplicit falseが保証されていない。したがって、分類は可能でも、**automatic inline retryを許可するためのsubmission evidenceは未完成**である。

Safe state:

```text
classification = oracle_attachment_submission_failed
prompt_submitted = None unless exact false is present
new execution = 0 while None
harvest/capture = 0
```

---

### 4.3 `response incomplete`

#### Producer

CLI session runnerは`BrowserAutomationError.details.stage=="assistant-timeout"`を認識し、runtime hintに`promptSubmitted=true`がある場合、次をsession metadataへ保存する。

```json
{
  "browser": {
    "runtime": {
      "promptSubmitted": true
    }
  },
  "response": {
    "status": "incomplete",
    "incompleteReason": "incomplete-capture"
  },
  "error": {
    "category": "browser-automation",
    "details": {
      "stage": "assistant-timeout"
    }
  }
}
```

Exact integrated testは`persistRuntimeHint(promptSubmitted=true)`から`performSessionRun`のfinal updateまでを通し、上記response fieldsを確認している。 

#### Safe S10 binding

次の全条件が成立する場合だけ`generation_incomplete`へ分類できる。

```text
mode == browser
browser.runtime.promptSubmitted is True
response.status == incomplete
response.incompleteReason == incomplete-capture
error.category == browser-automation
error.details.stage == assistant-timeout
```

Recovery:

```text
new execution = 0
successful submission = 1
harvest builder = 1 maximum
harvest subprocess = 1 maximum
capture = 0 unless later evidence becomes response-complete/artifact-pending
```

Unknown response statusやmissing fieldsを`generation_incomplete`へ変換しない。

---

### 4.4 `artifact pending`

#### 確認できた事実

* `SessionArtifactTransferStatus`には`ready`と`streaming`が存在する。
* Remote protocolには`artifact-ready`／`artifact-progress` eventが存在する。
* Remote server testのdescriptorは`transferStatus="ready"`を持つ。

#### 確認できないこと

Current attached sourceでは、`ready`または`streaming`を`SessionMetadata.artifacts[]`へ永続化するproducerがない。

Local artifact writerが保存する値:

```json
{"transfer":{"status":"not-needed"}}
```

Remote transfer成功後にclientが返す値:

```json
{"transfer":{"status":"completed"}}
```

`artifact-ready` descriptorの`transferStatus="ready"`はbridge event上の一時状態であり、current SpecDock readerが読む`meta.json`へ保存されたことを示さない。Local completed receiptも`not-needed`だけを観測している。 

#### 判定

```text
artifact_state=pending
RecoveryAction.SAME_SESSION_CAPTURE
```

をproduction-enableできない。

以下をpendingと推測することも禁止する。

```text
response complete + artifact absence
artifact-ready log
process nonzero
timeout
session nonterminal
remote event descriptor
```

---

### 4.5 `transfer failed`

#### 実際のproducer

Remote clientはartifact transfer failureをcatchし、最終`BrowserRunResult.warnings`へ次を追加する。

```json
{
  "code": "remote-artifact-transfer-failed",
  "severity": "warning",
  "message": "<raw diagnostic>"
}
```



成功時にはremote artifactへ次を付ける。

```json
{
  "transfer": {
    "status": "completed",
    "bytes": "<integer>"
  },
  "origin": {
    "mode": "bridge"
  }
}
```

一方、failure時に`transfer.status="failed"`を持つartifactは生成されない。

さらに、`src/browser/sessionRunner.ts`は`browserResult.warnings`をsession resultへmergeせず、model-related `buildBrowserRunWarnings()`の戻り値で`warnings`を置換する。そのためremote clientが生成した`remote-artifact-transfer-failed` warningが、current CLI runnerの`meta.json.browser.warnings`へ到達するproducer chainは成立していない。

Remote testはclient return value内のwarningを確認するだけであり、current Oracle session metadataへのpersistenceを確認していない。

#### 判定

次のいずれもproduction evidenceとして使用できない。

```text
SessionArtifactTransferStatus unionに "failed" があること
remote clientのraw failure message
remote-artifact-transfer-failed warningのclient-local存在
bridge descriptorのready state
```

`oracle_output_download_failed`へbindできるpersisted discriminatorは現時点でない。

---

## 5. Runtime producerとの結合判定

| 分類                             |            Producer単体 |    Producer→Browser runner | Browser runner→CLI persistence | Exact code positive persistence test | Production-ready |
| ------------------------------ | --------------------: | -------------------------: | -----------------------------: | -----------------------------------: | ---------------: |
| Prompt reconstruction mismatch |                   yes |                        yes |               generic path yes |                                   no |      **partial** |
| Attachment send not ready      |                   yes |                        yes |               generic path yes |                                   no |      **partial** |
| Response incomplete            |                   yes |                        yes |                            yes |                                  yes |          **yes** |
| Artifact pending               |       event/type only |      no persisted producer |                             no |                                   no |           **no** |
| Transfer failed                | remote client warning | warning propagation breaks |                             no |                                   no |           **no** |

**結論:** source producerを特定できたことだけを理由に、五分類全体をGreenにしてはならない。Current S10 v2の「producer + persisted field + positive fixture」gateを満たすのはresponse incompleteだけである。

---

## 6. 実装着手判定

### 6.1 判定

```text
S10 production implementation = blocked
partial classifier implementation = prohibited
fresh Red review = not started
S11 start = prohibited
```

### 6.2 理由

1. Artifact pendingのpersisted producerがない。
2. Transfer failedのpersisted producerがない。
3. Remote transfer warningはcurrent session metadataへ伝播しない。
4. Attachment failureではexplicit `promptSubmitted=false` positive fixtureがない。
5. 一部classだけをproduction-enableすると、unknown stateをgeneric capability/session reasonへ潰すか、部分的なdecision tableを持つ必要が生じる。
6. それはCanonical five-stage taxonomyとEAL-084のstop gateに反する。

---

## 7. 現時点のallowlist

### 7.1 Semantic mutation allowlist

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/
report.md
```

### 7.2 Immutable brief import

本回答をbyte-identicalに次へ保存できる。

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s10-stage-recovery-taxonomy-v3-20260806.md
```

### 7.3 任意のsanitized evidence artifact

追加Oracle evidenceを取得した場合に限り、次を許可する。

```text
${ISSUE_DIR}/artifacts/characterization/
s10-oracle-017-attempt-producer-binding-20260806.md
```

### 7.4 現時点で変更禁止

```text
src/spec_dock/
tests/
requirement.md
design.md
plan.md
decisions/
MANIFEST.json
CHECKSUMS.sha256
EAL-083
EAL-084
OAL-001
OAL-002
S09 runtime / tests / receipts / reviews / briefs
```

Production/testの部分実装、Red用test-only scaffold、placeholder enum追加も行わない。

---

## 8. 条件付き最小production/test allowlist

以下は§9の追加証跡が全て揃った後、別preflightでunblockした場合だけ有効とする。

### Production

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
domain/issue_planning_contracts.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
infra/issue_planning_oracle_artifact.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
infra/issue_planning_chatgpt.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
application/issue_planning.py
```

### Tests

```text
tests/unit/domain/test_issue_planning_contracts.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/application/test_issue_planning.py
tests/unit/commands/test_issue_planning.py
tests/cli_runtime/test_chatgpt_cli.py
```

### Read/run-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
commands/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
presentation/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
cli/bootstrap.py

tests/integration/test_issue_planning_e2e.py
```

これ以外のproduction/test変更が必要ならallowlistを黙示拡張せず停止する。

---

## 9. Unblockに必要な追加証跡

### 9.1 Prompt reconstruction persistence fixture

必要なOracle testまたはnative receipt:

```text
File:
  workspace/tools/oracle/tests/cli/sessionRunner.test.ts

Execution:
  performSessionRun()
  runBrowserSessionExecution rejects with BrowserAutomationError:
    category=browser-automation
    details.stage=submit-prompt
    details.code=prompt-reconstruction-mismatch

Required assertion:
  final sessionStore.updateSession:
    status=error
    error.category=browser-automation
    error.details.stage=submit-prompt
    error.details.code=prompt-reconstruction-mismatch
    browser.runtime.promptSubmitted is false
      またはsource-contract上のexplicit pre-submit discriminator
```

Native代替:

```text
PATH Oracle 0.17.0をexact session IDで実行
prompt reconstruction mismatchを発生させる
終了後、そのsessionのmeta.json一件をsanitized snapshot
stdout/stderrは証跡にしない
```

### 9.2 Attachment failure persistence fixture

必要なOracle testまたはnative receipt:

```text
File:
  workspace/tools/oracle/tests/cli/sessionRunner.test.ts

Execution:
  performSessionRun()
  exact attachment-send-not-ready errorを通す

Required assertion:
  error.category=browser-automation
  error.details.stage=submit-prompt
  error.details.code=attachment-send-not-ready
  promptSubmitted=falseのexplicit evidence
  response absent/incompleteではない
  artifacts absent
```

`attachmentNames`、path、raw messageはfixture/reportから除外する。

### 9.3 Artifact-pending producer

必要なsource:

```text
current Oracle local browser execution pathで
SessionMetadata.artifacts[]へtransfer.status=ready|streamingを
実際に書き込むproducer symbol
```

必要なintegration fixture:

```json
{
  "status": "<exact>",
  "mode": "browser",
  "browser": {
    "runtime": {
      "promptSubmitted": true
    }
  },
  "response": {
    "status": "completed"
  },
  "artifacts": [
    {
      "kind": "file",
      "transfer": {
        "status": "ready"
      }
    }
  ]
}
```

必要なtransition:

```text
before same-session capture:
  transfer.status=ready|streaming

after exact profile-owned same-session command:
  transfer.status=completed
  validation.ok=true
  size/SHA available
```

`artifact-ready` NDJSON eventだけでは不足する。

### 9.4 Transfer-failed producer

必要なsource producerは次のいずれかである。

```text
A:
  matching SessionArtifact.transfer.status = failed

B:
  meta.json.browser.warnings[].code =
    remote-artifact-transfer-failed
```

Bを使用する場合は、次も必要である。

```text
createRemoteBrowserExecutor
  -> BrowserRunResult.warnings
  -> runBrowserSessionExecution
  -> BrowserExecutionResult.warnings
  -> performSessionRun
  -> meta.json.browser.warnings
```

Current sourceでは`runBrowserSessionExecution`がremote warningsをdropするため、このchainは成立していない。

Required positive fixture:

```text
promptSubmitted=true
response completed
exact failure field persisted
same-session capture called once
still failed after capture
-> blocked / oracle_output_download_failed
```

### 9.5 Current SpecDock pathとのwiring

Remote bridge evidenceを採用するには、次のsource wiringが必要である。

```text
SpecDock --remote-chrome invocation
  -> exact Oracle browser executor selection
  -> source producer under evaluation
```

`createRemoteBrowserExecutor`が別remote-host／bridge feature専用であり、SpecDockの`--remote-chrome` pathから到達しない場合、そのsource/testをS10 evidenceに採用しない。

---

## 10. 条件付きRed／Green test matrix

| Scenario                                                          | Browser executions | Successful submissions | Harvest | Capture | Public pair                                             |
| ----------------------------------------------------------------- | -----------------: | ---------------------: | ------: | ------: | ------------------------------------------------------- |
| Unknown version/profile                                           |                  0 |                      0 |       0 |       0 | `blocked / oracle_capability_unsupported`               |
| `promptSubmitted=None`                                            |                0追加 |                      0 |       0 |       0 | `blocked / oracle_capability_unsupported`               |
| Reconstruction mismatch                                           |                  1 |                      0 |       0 |       0 | `blocked / oracle_prompt_reconstruction_mismatch`       |
| Attachment not ready、explicit pre-submit、inline eligible、budget 1 |            total 2 |                    最大1 |       0 |       0 | retry result                                            |
| Attachment not ready、submission unknown                           |                  1 |                      0 |       0 |       0 | `blocked / oracle_capability_unsupported`               |
| Response incomplete                                               |                  1 |                      1 |     最大1 |       0 | recovered resultまたは`oracle_generation_incomplete`       |
| Artifact pending                                                  |                  1 |                      1 |       0 |     最大1 | recovered resultまたは`oracle_output_download_failed`      |
| Transfer failed                                                   |                  1 |                      1 |       0 |     最大1 | `blocked / oracle_output_download_failed` if unresolved |
| Artifact validation defect                                        |                  1 |                      1 |     0追加 |     0追加 | `rejected / oracle_artifact_rejected`                   |

Global invariants:

```text
maximum browser executions = 2
maximum automatic new executions = 1
maximum successful submissions = 1
maximum harvest = 1
maximum capture = 1
post-submit new execution = 0
pre-submit harvest/capture = 0
model retryとinline retryは同じbudget
```

### 必須negative tests

* Unknown `error.details.code`はknown failure classへ変換しない。
* `promptSubmitted` missingをFalseにしない。
* `artifact-ready` logだけでpendingにしない。
* Artifact absenceをpendingにしない。
* Remote warningがmetaへpersistされていなければtransfer failedにしない。
* `transfer.status=failed`の型宣言だけでproduction classificationしない。
* Raw `error.message`、attachment names、URL、pathをpublic resultへ出さない。
* 全failure class × `promptSubmitted=False|None`でharvest/capture builder、process、pollが0。

---

## 11. 条件付きverification commands

Evidence gateを解消し、別briefでunblockした後だけ実行する。

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py -q
```

S09 regression:

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  -k 'oracle and (profile or version or artifact or session or builder)' -q
```

Static gates:

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
```

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

Forbidden inference audit:

```bash
rg -n \
  'stdout|stderr|errorMessage|Path\.home|rglob|glob\(|listdir|scandir' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

---

## 12. 今回実行可能なreport／evidence更新

### 12.1 EAL-083／EAL-084

次を一文字も変更しない。

```text
EAL-083
EAL-084
```

EAL-083は当時structured sourceが不明だったため停止した正しい履歴である。EAL-084はstorage path/core schemaを部分採用した正しい履歴である。

### 12.2 Exact `EAL-085` row

Current EALでID競合がないことを確認したうえで、EAL-084直後へ次をappend-only追加する。

```markdown
| EAL-085 | partially_adopted | `artifacts/implementation-briefs/s10-stage-recovery-taxonomy-v3-20260806.md`; Oracle `0.17.0` source snapshot at provided HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; `promptComposer.ts`; `errors.ts`; browser／CLI `sessionRunner.ts`; `artifacts.ts`; remote client and related tests | oracle-source-reevaluation / chatgpt-use-blue-team | Exact runtime sourceから`prompt-reconstruction-mismatch`、`attachment-send-not-ready`、`response.status=incomplete / incompleteReason=incomplete-capture`のproducer chainを特定した。Reconstructionとattachment failureは`error.category=browser-automation`、`error.details.stage=submit-prompt`、exact `error.details.code`へbindでき、response incompleteは`promptSubmitted=true`を含むCLI integration fixtureまで確認した。一方、artifact pendingの`ready|streaming`をsession metadataへpersistするproducerと、transfer failedを`artifacts[].transfer.status=failed`またはpersisted closed warningへbindするproducerは確認できず、remote transfer warningはcurrent browser session runnerでmetaへ伝播しない | `report.md`; conditional S10 production/test allowlist | S10 implementation-start re-evaluation and blocked evidence refinement | 五分類の一部だけをproduction-enableするとunknown stateの推測またはgeneric mappingが必要になるため、EAL-083/EAL-084を保持してS10をblockedにする。Source enum、remote event、raw diagnostic、process exitをmeta evidenceの代替にしない | source_producer_partial | SpecDock repository/branch/HEAD `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract` / `c45cb102bc956807820073022e7ecd66db1b27c1`; current report blob `70d81025563664b458c042e8d860c00dabf8291d`; Oracle provided source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; package version `0.17.0`; observed model evidence remains S09 `GPT-5.6 Sol` / `select` / verified `true`, while inline run remains verified `false` | issue orchestrator | ChatGPT-Use Blue Team | yes | Exact code-specific persistence fixtures for reconstruction／attachmentと、current SpecDock execution pathにおけるartifact pending／transfer failedのpersisted producer、before/after same-session fixtureを取得する。全gateが揃うまでproduction/test変更、S10 fresh Red review、S10 closure、S11以降、PR、merge、Issue close、Issue finishを行わない |
```

### 12.3 S10 current-state

Current S10 statusは次へ精密化する。

```text
blocked /
three-source-producers-identified /
pre-submit-persistence-partial /
artifact-transfer-persistence-unbound
```

次アクション:

```text
Oracle 0.17.0 exact producer-integrated fixturesを取得
→ EALへ採用
→ 別のunblock implementation brief
→ allowlisted implementation
→ fresh Red review
```

Production candidateまたはtest candidateが存在するとは記録しない。

---

## 13. 今回のverification

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='c45cb102bc956807820073022e7ecd66db1b27c1'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE"
test "$(git rev-parse '@{upstream}')" = "$SOURCE"
test -z "$(git status --short)"
```

Current report blob:

```bash
REPORT="$ISSUE_DIR/report.md"

test "$(git rev-parse "$SOURCE:$REPORT")" = \
  '70d81025563664b458c042e8d860c00dabf8291d'
```

Historical EAL preservation:

```bash
python - "$REPORT" <<'PY'
from pathlib import Path
import subprocess
import sys

source = "c45cb102bc956807820073022e7ecd66db1b27c1"
path = Path(sys.argv[1])
relative = path.as_posix()

before = subprocess.check_output(
    ["git", "show", f"{source}:{relative}"],
    text=True,
)
after = path.read_text(encoding="utf-8")

def row(text: str, identifier: str) -> str:
    matches = [
        line for line in text.splitlines()
        if line.startswith(f"| {identifier} |")
    ]
    assert len(matches) == 1, (identifier, len(matches))
    return matches[0]

for identifier in ("EAL-083", "EAL-084"):
    assert row(before, identifier) == row(after, identifier)

eal_085 = row(after, "EAL-085")
assert len([field.strip() for field in eal_085.strip("|").split("|")]) == 14
PY
```

Scope:

```bash
git diff --name-only
```

許容値:

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/artifacts/implementation-briefs/
s10-stage-recovery-taxonomy-v3-20260806.md
```

Repository validation:

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

Production／testsを変更しないため、今回の再評価でpytest、Ruff、MypyのGreen結果を主張しない。

---

## 14. Stop gates

次のいずれかではproduction implementationを開始しない。

1. Named branchと`c45cb102bc956807820073022e7ecd66db1b27c1`が一致しない。
2. Default branchまたは別branchが必要になる。
3. EAL-083／EAL-084の変更が必要になる。
4. `promptSubmitted` missingをFalseへ変換する必要がある。
5. Raw error messageからfailure classを推測する必要がある。
6. `attachmentNames`またはpathをdecoder／public resultへ取り込む必要がある。
7. `artifact-ready` eventだけをpending stateへ変換する必要がある。
8. Artifact absenceをpendingへ変換する必要がある。
9. Transfer status unionの宣言だけでfailed stateをproduction-enableする必要がある。
10. Remote warningがmetaへpersistされないまま`oracle_output_download_failed`へbindする必要がある。
11. `createRemoteBrowserExecutor`とSpecDockの`--remote-chrome` pathのwiringを推測する必要がある。
12. Partial three-class implementationを先にcommitする必要がある。
13. Known classを`oracle_capability_unsupported`または`oracle_session_recovery_required`へ潰す必要がある。
14. S09 profile、reader、builders、testsを変更する必要がある。
15. Wrapper、API、alternate backend、alternate modelが必要になる。
16. S11以降を先取りする必要がある。
17. Conditional allowlist外のproduction/test変更が必要になる。

---

## 15. Handoff

```text
decision
  remains_blocked

SpecDock identity
  repository=chemitaro/spec-dock
  branch=codex/iss-00354-chatgpt-context-contract
  head=c45cb102bc956807820073022e7ecd66db1b27c1
  default_fallback=0

Oracle source identity
  package_version=0.17.0
  provided_source_head=9fb87d9326ab1c07216f1eb904917013df6d9270
  independent_connector_verification=no

source producer status
  prompt_reconstruction_mismatch=identified
  attachment_send_not_ready=identified
  response_incomplete=identified_and_integrated_tested
  artifact_pending=not_persisted
  transfer_failed=not_persisted

production_candidate
  none

test_candidate
  none

semantic_changed_file
  report.md only

append_only_evidence
  EAL-085

closure_claim
  none

fresh_red_review
  not_started

next_action
  obtain exact producer-integrated metadata fixtures for:
    prompt-reconstruction persistence
    attachment-send persistence
    artifact pending
    transfer failed

S11 / PR / merge / Issue close / Issue finish
  prohibited
```
