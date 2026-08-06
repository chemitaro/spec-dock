# iss-00354 S10 追加producer検証ブリーフ v4 — Oracle 0.17.0 persistence chain再評価

## 0. 固定identityと判定

| 項目                      | 確認値                                                             |
| ----------------------- | --------------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                           |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`                      |
| ユーザー提示HEAD              | `d712d85d5c65b1679a5f6c70efebfdaecf4d9b0a`                      |
| GitHubで確認した実HEAD        | `d712d85db9c572b86b2ecac6e180e74fcd0d5e88`                      |
| Branch parity           | named branch tipと実HEADは同一                                       |
| Default branch fallback | 使用していない                                                         |
| Current commit          | S10 v3 brief、EAL-085、S10 blocked current-stateの同期               |
| Oracle package version  | `0.17.0`                                                        |
| Oracle source identity  | provided source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270` |
| Prior blocked evidence  | `EAL-083`                                                       |
| Prior source adoption   | `EAL-084`、`EAL-085`                                             |
| 今回の判定                   | **S10 production implementationは引き続き blocked**                  |
| `closure_claim`         | `none`                                                          |
| Fresh Red review        | 未開始                                                             |

ユーザー提示SHAはGitHub上のnamed branch tipと一致しなかった。GitHub connectorで実測したbranch tipは`d712d85db9c572b86b2ecac6e180e74fcd0d5e88`であり、このcommitはS10 v3再評価briefとEAL-085を採用したdocs commitである。

### 判定要旨

今回のsource再検証により、前回v3 briefのうち次の一点は精密化できる。

> `prompt-reconstruction-mismatch`と`attachment-send-not-ready`の実行経路では、正常にruntime-hint persistenceが動作する限り、Oracleはエラー発生前に`promptSubmitted=false`を一度persistするsource chainを持つ。

ただし、次の二つは依然として成立しない。

1. `artifact pending`をlocal session `meta.json`へ永続化するproducerがない。
2. `transfer failed`をlocal session `meta.json`へ永続化するclosed discriminatorがない。

したがって、canonical planが要求する五分類を一つの閉じたS10 change-setとしてSpecDock側だけで実装することはできない。Canonical designはsubmissionを回復境界とし、stage evidenceをprofile-private parserからadapter-neutral contractへ変換すること、ambiguous evidenceを推測しないことを要求している。

```text
decision = remains_blocked

pre_submit_false_source_chain = identified
pre_submit_positive_fixture = still required

response_incomplete_producer = sufficient

artifact_pending_persisted_producer = absent
transfer_failed_persisted_discriminator = absent

SpecDock production mutation = prohibited
Oracle external producer/persistence prerequisite = required
```

---

## 1. Canonical境界

維持する設計前提は次のとおりである。

* `promptSubmitted=true`だけがpost-submit same-session recoveryを許可する。
* `promptSubmitted=false`は限定pre-submit new executionの候補である。
* `promptSubmitted`欠落または型不正は`None`であり、`false`へ変換しない。
* 一つのoperation lineageでsuccessful submissionは最大1回。
* Pre-submitではharvest／captureを呼ばない。
* Post-submitではnew executionを呼ばない。
* Model、attachment、prompt reconstruction、generation、downloadを別failure classとして扱う。
* Known stage-specific classをgeneric capability reasonへ潰さない。
* Unknown contractでは停止する。
* Wrapper、API、default branch、alternate backendへfallbackしない。

Requirementでは、pre-submit failureを「`promptSubmitted=false`またはunknown」と区別し、same-session recoveryを`promptSubmitted=true`に限定している。 Designでは、submissionを回復境界とし、failureをstage別に分類する原則を明示している。 Planではgeneric retry loopを禁止し、pre-submit new executionをoverall最大1、post-submitをsame-sessionだけに限定している。

---

## 2. A — pre-submit `promptSubmitted=false` persistence

## 2.1 Source execution chain

Oracle browser runtimeは、browser execution開始時に次のlocal stateを持つ。

```ts
let promptSubmitted = false;
```

`emitRuntimeHint()`が生成するstructured runtime hintには、このbooleanが常に含まれる。

```ts
{
  ...
  promptSubmitted,
  ...
}
```

`markPromptSubmitted()`だけが値を`true`へ変更し、その後に再度runtime hintをpersistする。

さらに、browser runtimeはmodel selectionおよびprompt submission処理より前に次を実行する。

```ts
await captureRuntimeSnapshot();
```

`captureRuntimeSnapshot()`は内部で`emitRuntimeHint()`を呼ぶため、この時点で`promptSubmitted=false`がruntime callbackへ渡される。

Browser session runnerはこのcallbackをCLI layerの`persistRuntimeHint`へ転送する。

CLI `performSessionRun()`は受信したruntime hintを即時にsession storeへ保存し、同時に`currentBrowser`へ保持する。

```ts
await sessionStore.updateSession(... {
  status: "running",
  browser,
});
currentBrowser = browser;
```



Generic error catchは、エラーの`details.runtime`が存在しなくても、次のfallbackを使う。

```ts
runtime: browserRuntime ?? currentBrowser?.runtime
```

したがって、initial runtime hint persistenceが成功していれば、後続のgeneric error updateにも`promptSubmitted=false`が残る。

## 2.2 Prompt reconstruction mismatch

実際のproducer:

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts
lines 591–628
symbol reconstructMultilinePrompt
```

Structured discriminator:

```json
{
  "category": "browser-automation",
  "details": {
    "stage": "submit-prompt",
    "code": "prompt-reconstruction-mismatch"
  }
}
```

このerrorは`markPromptSubmitted()`より前に発生する。Producer単体ではexact codeが確認済みである。

### 再評価

前回v3 briefの「この経路では`promptSubmitted`が欠落する可能性がある」という記述は、通常のpersistence成功経路については過度に保守的だった。

Source chain上は次が成立する。

```text
promptSubmitted initialized false
→ initial captureRuntimeSnapshot
→ emitRuntimeHint(false)
→ performSessionRun.persistRuntimeHint
→ currentBrowser.runtime.promptSubmitted=false
→ prompt reconstruction error
→ generic catch retains currentBrowser.runtime
→ final meta.json contains false
```

ただし、`emitRuntimeHint()`はpersistence callback failureをcatchしてlogだけを残す。このcallback自体が失敗した場合、metadataにexplicit falseがない可能性は残る。そのためSpecDock decoderの契約は次とする。

```text
exact boolean false -> pre-submit evidence
exact boolean true  -> post-submit evidence
missing/non-bool    -> None / undecidable
```

Missingをsource orderingだけから`false`へ補完してはならない。

## 2.3 Attachment send not ready

実際のproducer:

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts
lines 1121–1133
symbol attemptSendButton
```

Structured discriminator:

```json
{
  "category": "browser-automation",
  "details": {
    "stage": "submit-prompt",
    "code": "attachment-send-not-ready"
  }
}
```

このerrorも`markPromptSubmitted()`より前に発生し、attachment時にEnter fallbackへ進まず停止する。

### 再評価

Prompt reconstructionと同じinitial runtime snapshot chainにより、persistence成功時は`promptSubmitted=false`がfinal metadataに残ると判断できる。

ただしautomatic inline retryをproduction-enableするには、次のexact conjunctionをpositive fixtureで固定する必要がある。

```text
mode=browser
attachment mode=direct
browser.runtime.promptSubmitted=false
error.category=browser-automation
error.details.stage=submit-prompt
error.details.code=attachment-send-not-ready
response absent
artifacts absent
```

### Aの結論

| 項目                                          | 判定                                    |
| ------------------------------------------- | ------------------------------------- |
| Explicit falseのsource producer chain        | **確認済み**                              |
| Generic catchがruntimeを保持するか                 | **保持する**                              |
| Missingをfalseと扱ってよいか                        | **不可**                                |
| Error codeからpre-submit分類可能か                 | **explicit falseとのconjunctionに限り可能**  |
| Source inspectionだけでproduction retryを解禁できるか | **不可。producer-integrated fixtureが必要** |

---

## 3. B — artifact pending

## 3.1 型とevent surface

`SessionArtifactTransferStatus`には次の値が宣言されている。

```text
not-needed
ready
streaming
completed
failed
skipped
```



Remote serverは完成済みfileをartifact registryへ登録する際、remote protocol descriptorへ次を設定する。

```ts
transferStatus: "ready"
```



Remote protocolには`artifact-ready`および`artifact-progress` eventも存在する。

## 3.2 Local `meta.json` persistence

確認できたactual producersは次の二つだけである。

Local browser artifact writer:

```json
{
  "transfer": {
    "status": "not-needed"
  }
}
```

Remote clientのtransfer成功後:

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



確認できないもの:

```text
SessionMetadata.artifacts[].transfer.status="ready"
SessionMetadata.artifacts[].transfer.status="streaming"
```

`ready`はremote server上のdescriptor stateであり、SpecDockが読むlocal session `meta.json`のartifact entryではない。`artifact-progress`もtransport eventであり、session metadataの永続状態ではない。

## 3.3 判定

次をartifact-pending evidenceとして使用してはならない。

* `SessionArtifactTransferStatus` unionに`ready`／`streaming`があること。
* `artifact-ready` event。
* `artifact-progress` event。
* Remote descriptorの`transferStatus="ready"`。
* Response completedだがfile artifactがないこと。
* Process timeout、nonzero、session nonterminal。
* Log message。
* `.crdownload`の存在をSpecDockが探索すること。

### Bの結論

```text
artifact_state=pending
RecoveryAction.SAME_SESSION_CAPTURE
```

をcurrent Oracle `0.17.0` contractへbindできない。

**Persisted artifact-pending producerは存在しない。**

---

## 4. C — transfer failed

## 4.1 Remote client producer

Remote clientはdownload、size、SHA、validation failureをcatchし、最終`BrowserRunResult.warnings`へ次を追加する。

```json
{
  "code": "remote-artifact-transfer-failed",
  "severity": "warning",
  "message": "<raw diagnostic>"
}
```

成功時だけlocal artifactを生成し、`transfer.status="completed"`を付ける。Failure時に`transfer.status="failed"`を持つartifactは生成しない。

## 4.2 Browser session runnerでのwarning loss

Remote clientが返したwarningは`browserResult.warnings`に存在する。

しかしbrowser session runnerは、browser resultのwarningsをmergeせず、新しく次を構築する。

```ts
const warnings = buildBrowserRunWarnings({
  runOptions,
  browserConfig,
  inputTokens,
  elapsedMs,
  modelSelection,
});
```

その後に返すresultのwarningsはこのlocal `warnings`であり、`browserResult.warnings`ではない。

したがってproducer chainは次で途切れる。

```text
remote client
  -> BrowserRunResult.warnings
  -X-> browser/sessionRunner result.warnings
  -X-> cli/performSessionRun
  -X-> meta.json.browser.warnings
```

CLI layerがbrowser execution resultをsession metadataへ保存しても、既にwarningがdropされているため`remote-artifact-transfer-failed`は残らない。

## 4.3 判定

次をtransfer-failed discriminatorとして使用してはならない。

* Type unionに`failed`が存在すること。
* Remote clientのraw error。
* Remote client-local warning。
* Remote server registration warning。
* Artifactがないこと。
* Validation false。
* Process exit code。
* Stdout／stderr。
* Wrapper observation。

### Cの結論

**Current Oracle sourceには、SpecDockが後から読むlocal `meta.json`上のclosed transfer-failed discriminatorが存在しない。**

`oracle_output_download_failed`へ安全にbindできない。

---

## 5. D — producer fixtureとsynthetic dependency fixture

## 5.1 Synthetic dependency fixture

次のようなtestは、CLI persistence plumbingを検証するには有効である。

```ts
vi.mocked(runBrowserSessionExecution).mockImplementationOnce(
  async (_args, deps) => {
    await deps?.persistRuntimeHint?.({
      promptSubmitted: false,
      ...
    });
    throw new BrowserAutomationError(...);
  },
);
```

このtestが証明すること:

* `persistRuntimeHint`が`currentBrowser`を更新する。
* Generic catchが`currentBrowser.runtime`を保持する。
* Final `updateSession`へexplicit falseが入る。
* SpecDock decoder用のsanitized fixture shape。

このtestが証明しないこと:

* 実際のpromptComposer producerがerrorを生成したこと。
* Actual browser/index call order。
* `captureRuntimeSnapshot()`が当該failure前に実行されたこと。
* `markPromptSubmitted()`がまだ呼ばれていないこと。
* Remote transfer eventが実際に起きたこと。
* Artifact pending／transfer failedがreal runtimeでpersistされたこと。

## 5.2 Producer-integrated fixture

Production unblock evidenceとして採用できるのは次のいずれかである。

### Option 1 — actual producer-integrated Oracle test

```text
browser/index.ts
  -> actual promptComposer producer
  -> runtimeHintCb
  -> browser/sessionRunner
  -> cli/performSessionRun
  -> sessionStore.updateSession
```

Testはerror objectを`runBrowserSessionExecution`境界で直接fabricateするのではなく、actual `promptComposer.ts` codeを通す。

Required assertions:

```text
final status=error
final error.category=browser-automation
final error.details.stage=submit-prompt
final exact error.details.code
final browser.runtime.promptSubmitted=false
response absent
artifacts absent
```

### Option 2 — native Oracle receipt

PATH Oracle `0.17.0`でexact session IDを指定してfailureを実際に発生させ、終了後にそのsessionの`meta.json`一件だけをsanitized snapshotする。

採用禁止:

* Stdout／stderrだけの証跡。
* Wrapper telemetryだけの証跡。
* Error message substring。
* Synthetic `meta.json`だけ。
* Manually constructed enum fixtureだけ。

## 5.3 Dの結論

**Synthetic dependency fixture単独ではproduction allowlistを解禁しない。**

Synthetic fixtureはSpecDock decoder unit testまたはOracle persistence-plumbing testには使えるが、external Oracle contractのproducer evidenceにはならない。

---

## 6. E — S10実装可否

## 6.1 五分類の最終評価

| 分類                             |              Producer | Final metadata persistence | Positive producer fixture | S10 production-ready |
| ------------------------------ | --------------------: | -------------------------: | ------------------------: | -------------------: |
| Prompt reconstruction mismatch |                   yes |           source chain上yes |                        no |          **partial** |
| Attachment send not ready      |                   yes |           source chain上yes |                        no |          **partial** |
| Response incomplete            |                   yes |                        yes |                       yes |              **yes** |
| Artifact pending               |       event/type only |                         no |                        no |               **no** |
| Transfer failed                | remote client warning |             no、runnerでdrop |                        no |               **no** |

## 6.2 判定

SpecDock側だけで五分類のclosed stage contractを安全に実装することはできない。

必要な外部前提:

1. Oracleがartifact-pending stateをcurrent session `meta.json`へpersistすること。
2. Oracleがtransfer-failed stateをcurrent session `meta.json`へpersistすること。
3. そのfieldがSpecDockの実際のPATH Oracle／`--remote-chrome` execution pathで生成されること。
4. Same-session command前後のtransition fixtureが存在すること。

これはSpecDock architecture redesignの要求ではなく、既存canonical S10が依存する外部Oracle contractの欠落である。

### 実装状態

```text
S10 production implementation = blocked
partial three-class implementation = prohibited
production candidate = none
test candidate = none
fresh Red review = not started
S11 start = prohibited
```

一部のfailure classだけを先行実装すると、未確認stateをgeneric reasonへ落とすか、canonical decision tableの一部だけを有効化する必要がある。そのため、S10を分割して部分実装しない。

---

## 7. 現時点の最小allowlist

### 7.1 Semantic mutation

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/
report.md
```

### 7.2 Immutable brief import

本回答をbyte-identicalに保存する場合:

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s10-stage-recovery-taxonomy-v4-20260806.md
```

### 7.3 Optional sanitized characterization evidence

Actual producer-integrated fixtureを取得した場合だけ:

```text
${ISSUE_DIR}/artifacts/characterization/
s10-oracle-017-producer-persistence-v2-20260806.md
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
EAL-085

OAL-001
OAL-002

S09 source/tests/receipts/reviews/briefs
Oracle source
```

Oracle source patchは今回の作業範囲外である。

---

## 8. 条件付きSpecDock allowlist

Oracle側のmissing producer／fixtureが揃い、別のunblock briefで明示的にgateを開いた場合だけ有効とする。

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

Allowlistを暗黙に拡張しない。

---

## 9. Unblockに必要な追加証跡

## 9.1 Prompt reconstruction producer fixture

対象:

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts:591–628
workspace/tools/oracle/src/browser/index.ts:952–990
workspace/tools/oracle/src/browser/index.ts:1419–1471
workspace/tools/oracle/src/browser/sessionRunner.ts:200–240
workspace/tools/oracle/src/cli/sessionRunner.ts:93–144, 745–773
```

必要な実行:

```text
actual promptComposer producer
→ browser/index initial emitRuntimeHint(false)
→ browser/sessionRunner callback
→ performSessionRun
→ final sessionStore.updateSession
```

Required final fixture:

```json
{
  "status": "error",
  "mode": "browser",
  "browser": {
    "runtime": {
      "promptSubmitted": false
    }
  },
  "error": {
    "category": "browser-automation",
    "details": {
      "stage": "submit-prompt",
      "code": "prompt-reconstruction-mismatch"
    }
  }
}
```

## 9.2 Attachment producer fixture

対象:

```text
workspace/tools/oracle/src/browser/actions/promptComposer.ts:1121–1133
workspace/tools/oracle/src/browser/index.ts:952–990
workspace/tools/oracle/src/browser/index.ts:1419–1471
workspace/tools/oracle/src/cli/sessionRunner.ts:745–773
```

Required final fixture:

```json
{
  "status": "error",
  "mode": "browser",
  "browser": {
    "runtime": {
      "promptSubmitted": false
    }
  },
  "error": {
    "category": "browser-automation",
    "details": {
      "stage": "submit-prompt",
      "code": "attachment-send-not-ready"
    }
  },
  "artifacts": []
}
```

Private `attachmentNames`、paths、raw messageはevidenceへ保存しない。

## 9.3 Artifact-pending producer

必要なOracle source contract:

```text
current SpecDock PATH browser executionが読むsession meta.jsonへ
artifacts[].transfer.status="ready"|"streaming"
を実際に書くproducer
```

必要なbefore fixture:

```json
{
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

必要なafter fixture:

```text
same exact session
exact profile-owned same-session command once
transfer.status=completed
validation.ok=true
size/SHA available
```

Remote event descriptorだけでは不足する。

## 9.4 Transfer-failed producer

必要なpersisted discriminatorは次のいずれか一つである。

```text
artifacts[].transfer.status="failed"
```

または:

```text
browser.warnings[].code="remote-artifact-transfer-failed"
```

後者を使う場合、次のchain全体が必要である。

```text
remote/client
→ BrowserRunResult.warnings
→ browser/sessionRunner result.warnings
→ cli/performSessionRun
→ meta.json.browser.warnings
```

Current sourceでは二番目のarrowでwarningがdropされるため、Oracle側のproducer／persistence変更が必要である。

## 9.5 SpecDock実行経路とのbinding

Remote bridge codeをevidenceに採用する前に、次をsourceまたはnative receiptで確認する。

```text
SpecDock direct Oracle invocation
  --engine browser
  --remote-chrome <loopback endpoint>
→ actual Oracle executor
→ remote/client transfer path under evaluation
```

`--remote-chrome`が単なるCDP接続で、remote bridge clientを使用しない場合、remote clientのpending／failure evidenceはSpecDock S10へ採用しない。

---

## 10. 必要なRed／Green tests

### 10.1 Oracle external prerequisite tests

| Test                                 | Actual producer required | Synthetic onlyで可 |
| ------------------------------------ | -----------------------: | ---------------: |
| Reconstruction exact code generation |                      yes |               no |
| Initial runtime false emission       |                      yes |               no |
| Final meta reconstruction + false    |                      yes |               no |
| Attachment exact code generation     |                      yes |               no |
| Final meta attachment + false        |                      yes |               no |
| Response incomplete + true           |             existing yes |                — |
| Pending persisted before capture     |                      yes |               no |
| Completed persisted after capture    |                      yes |               no |
| Transfer failure persisted           |                      yes |               no |
| Warning propagation to final meta    |                      yes |               no |

### 10.2 Conditional SpecDock tests

Oracle evidence gate解消後に追加する。

* Exact `0.17.0` attempt reader。
* Explicit false／true／missingの三値decode。
* Unknown error code fail-closed。
* Reconstruction mismatchはnew execution 0、harvest 0、capture 0。
* Attachment failureはexplicit false時だけinline retry候補。
* Missing promptSubmittedではnew execution、harvest、captureすべて0。
* Response incompleteではsuccessful submission 1、harvest最大1。
* Artifact pendingではcapture最大1。
* Transfer failedではcapture後もfailedなら`oracle_output_download_failed`。
* Post-submitからnew execution APIへ到達不可。
* Model retryとinline retryでshared budget 1。
* Successful submission最大1。
* Raw metadata、error message、path、URL、session handleのpublic leak 0。
* S09 exact 0.16.1／0.17.0 profile regression。

---

## 11. Report更新

`EAL-083`、`EAL-084`、`EAL-085`はhistorical evidenceとして一文字も変更しない。

Current reportはblockedまたはstaleのunresolved entryがimplementation startを止めると明示している。

### Exact `EAL-086`

Current EALでID競合がないことを確認したうえで、EAL-085直後へappend-only追加する。

```markdown
| EAL-086 | partially_adopted | `artifacts/implementation-briefs/s10-stage-recovery-taxonomy-v4-20260806.md`; Oracle `0.17.0` source snapshot at provided HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; browser `index.ts`; browser／CLI `sessionRunner.ts`; `promptComposer.ts`; remote client／server | oracle-source-producer-persistence-reevaluation / chatgpt-use-blue-team | Browser runtimeは`promptSubmitted=false`で開始し、model selection／prompt submission前のinitial runtime snapshotでfalseをpersist callbackへ渡す。CLI `performSessionRun`はそのruntimeを`currentBrowser`へ保持しgeneric error updateへ継承するため、`prompt-reconstruction-mismatch`と`attachment-send-not-ready`はexplicit falseがfinal metadataに存在する場合に限りsafe pre-submit evidenceへbindできる。一方、artifact `ready|streaming`をlocal session metadataへpersistするproducerはなく、remote transfer failure warningはbrowser session runnerでdropされ、`failed` artifactも生成されない | `report.md`; conditional S10 production/test allowlist | S10 implementation-start gate refinement | Synthetic dependency fixtureはpersistence plumbingの検証には使えるがactual producer contractの採用証跡にはならない。Pending／transfer-failedのclosed persisted discriminatorがないため五分類の部分実装は行わず、S10をblockedに維持する | source_chain_refined_external_producer_blocked | SpecDock repository/branch/actual HEAD `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract` / `d712d85db9c572b86b2ecac6e180e74fcd0d5e88`; user-provided unresolved SHA `d712d85d5c65b1679a5f6c70efebfdaecf4d9b0a`; Oracle provided source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; package version `0.17.0` | issue orchestrator | ChatGPT-Use Blue Team | yes | Actual producer-integrated pre-submit fixturesと、current SpecDock execution pathでpersistされるartifact-pending／transfer-failed discriminatorおよびsame-session before/after fixtureを取得する。全gateが揃うまでSpecDock production/test変更、S10 fresh Red review、S10 closure、S11以降、PR、merge、Issue close、Issue finishを行わない |
```

### S10 current-state

```text
blocked /
pre-submit-false-source-chain-identified /
pre-submit-positive-fixture-pending /
artifact-pending-producer-absent /
transfer-failed-persistence-absent
```

---

## 12. 今回の検証コマンド

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='d712d85db9c572b86b2ecac6e180e74fcd0d5e88'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE"
test "$(git rev-parse '@{upstream}')" = "$SOURCE"
test -z "$(git status --short)"
```

EAL不変性:

```bash
python - "$ISSUE_DIR/report.md" <<'PY'
from pathlib import Path
import subprocess
import sys

source = "d712d85db9c572b86b2ecac6e180e74fcd0d5e88"
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

for identifier in ("EAL-083", "EAL-084", "EAL-085"):
    assert row(before, identifier) == row(after, identifier)

eal_086 = row(after, "EAL-086")
assert len([part.strip() for part in eal_086.strip("|").split("|")]) == 14
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
s10-stage-recovery-taxonomy-v4-20260806.md
```

Repository checks:

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

Production／testsを変更しないため、今回の再評価でpytest、Ruff、MypyのGreenを主張しない。

---

## 13. 停止条件

次のいずれかではSpecDock production implementationを開始しない。

1. Named branchの実HEADを再確認できない。
2. Default branchまたは別branchが必要になる。
3. `promptSubmitted`欠落をfalseへ変換する必要がある。
4. Runtime-hint persistence failureを無視してpre-submit retryする必要がある。
5. Error message substringからstageを判定する必要がある。
6. Synthetic dependency fixtureだけでOracle producer contractを採用する必要がある。
7. `ready`／`streaming`のtype宣言だけでartifact pendingを有効化する必要がある。
8. Remote eventだけでlocal metadata stateを推定する必要がある。
9. Artifact absenceをpendingへ変換する必要がある。
10. `failed`のtype宣言だけでtransfer failureを有効化する必要がある。
11. Remote warningがsession metadataへ到達しないままpublic failureへbindする必要がある。
12. Raw remote warning messageをpublic resultへ出す必要がある。
13. SpecDock `--remote-chrome`とremote bridge clientのwiringを推測する必要がある。
14. 五分類の一部だけを先行実装する必要がある。
15. Unknown classをgeneric capability／session-recovery reasonへ潰す必要がある。
16. S09 profile、reader、builders、testsを変更する必要がある。
17. Wrapper、API、alternate backend、alternate modelへfallbackする必要がある。
18. S11以降を先取りする必要がある。
19. Conditional allowlist外を変更する必要がある。

---

## 14. Handoff

```text
decision
  remains_blocked

SpecDock repository
  chemitaro/spec-dock

named branch
  codex/iss-00354-chatgpt-context-contract

actual branch HEAD
  d712d85db9c572b86b2ecac6e180e74fcd0d5e88

user-provided unresolved SHA
  d712d85d5c65b1679a5f6c70efebfdaecf4d9b0a

default fallback
  0

Oracle package version
  0.17.0

Oracle provided source HEAD
  9fb87d9326ab1c07216f1eb904917013df6d9270

classification evidence
  prompt_reconstruction_mismatch:
    producer identified
    explicit-false source chain identified
    actual producer-integrated fixture pending

  attachment_send_not_ready:
    producer identified
    explicit-false source chain identified
    actual producer-integrated fixture pending

  response_incomplete:
    producer and persistence fixture sufficient

  artifact_pending:
    no local meta.json persistence producer

  transfer_failed:
    remote client warning exists
    warning is dropped before session metadata
    no failed artifact producer

production candidate
  none

test candidate
  none

semantic mutation
  report.md only

append-only evidence
  EAL-086

closure_claim
  none

fresh Red review
  not started

next action
  obtain actual producer-integrated pre-submit fixtures
  obtain Oracle artifact-pending persistence producer and fixture
  obtain Oracle transfer-failed persistence producer and fixture
  verify exact SpecDock --remote-chrome execution wiring

S11 / PR / merge / Issue close / Issue finish
  prohibited
```
