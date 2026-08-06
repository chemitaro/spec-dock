# iss-00354 S10 改訂実装ブリーフ v2 — Oracle 0.17.0 structured attempt-evidence gate

## 0. 判定

**判定: S10 production implementation gate は引き続き `blocked` とする。**

今回のOracle source inspectionにより、EAL-083で未確認だった次の部分は解消した。

* Oracle `0.17.0`のsession metadata正本が、実行ごとの`<Oracle home>/sessions/<session-id>/meta.json`であること。
* `meta.json`がversion-bound readerへ渡せるJSON objectであること。
* `browser.runtime.promptSubmitted`、`browser.modelSelection`、`response`、`artifacts[].validation`、`artifacts[].transfer`、`artifacts[].origin`、`transport`、`error`、`lifecycle`というstructured surfaceが存在すること。
* SpecDockが自ら生成したexact session IDを使い、その一つのsession pathだけをreaderへ注入できること。

一方、Canonical S10をGreenにするには、少なくとも`prompt_reconstruction_mismatch`と`attachment_submission_failed`を、raw messageやprocess exitから推測せず、Oracle `0.17.0`のclosed structured valueへ結び付ける必要がある。添付sourceでは`error.category`がopen `string`、`transport.reason`が未展開の外部型であり、どのproducerがどのexact valueを書き込むか、および実session fixtureでの値が提示されていない。したがって、この二つをcanonical failure classへbindすると推測実装になる。

また、artifact transfer statusのenumは確認できたが、`response-complete + artifact-pending`の独立session fixtureは未観測である。S09 evidence自身もartifact-pendingを未観測としてS10へ持ち越している。 

よって、**storage/path/schema candidateは採用するが、production taxonomy/recovery実装の開始は許可しない**。EAL-083は歴史的blocked evidenceとして不変に保持し、EAL-084で「path/core schema判明、failure semantics未確定」という現在状態をappend-only記録する。

```text
decision = remains_blocked
storage_path_gate = resolved
core_schema_gate = partially_resolved
closed_failure_semantics_gate = unresolved
production_mutation = forbidden
closure_claim = none
next_action = exact structured failure fixtures / producer binding
```

---

## 1. 固定identity

| 項目                            | 固定値                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------- |
| Repository                    | `chemitaro/spec-dock`                                                        |
| Named branch                  | `codex/iss-00354-chatgpt-context-contract`                                   |
| SpecDock source HEAD          | `04c76a7bef2e997f98d5b791c5c9da2d068fb378`                                   |
| Branch parity                 | named branch tipとsource HEADは`identical`、ahead `0`、behind `0`                |
| Default branch fallback       | 禁止・未使用                                                                       |
| S09 Candidate version         | `s09-blue-repair-v2`                                                         |
| S09 Candidate ID              | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                              |
| S09 implementation commit     | `470cacf5051272edfa71e9780f263d1f402a33a0`                                   |
| S09 final review              | Fresh Red v6 PASS、P0=`0`、P1=`0`、P2=`0`、P3=`0`                                |
| Prior S10 brief evidence      | EAL-082                                                                      |
| Prior S10 blocked handoff     | EAL-083                                                                      |
| Oracle package version        | `0.17.0`                                                                     |
| Oracle source HEAD            | `9fb87d9326ab1c07216f1eb904917013df6d9270`                                   |
| Oracle source identity status | ユーザー提示のlocal source identity。SpecDock GitHub connectorによる独立commit確認ではない      |
| Revised brief artifact        | `artifacts/implementation-briefs/s10-stage-recovery-taxonomy-v2-20260806.md` |
| Current S10 state             | `blocked`                                                                    |
| Issue-level closure claim     | `none`                                                                       |

GitHub connectorで、指定named branchと`04c76a7bef2e997f98d5b791c5c9da2d068fb378`の完全一致を確認した。`4ff7f852...`からcurrent HEADまでの差分は、旧S10 brief artifactと`report.md`だけであり、production source／testsは変更されていない。

Current reportはEAL-083をblocking evidenceとして保持し、S10をstructured attempt-evidence不足で停止している。EAL-083は今回の追加証跡によって削除・上書きせず、当時の正しいstop decisionとして保持する。  

---

## 2. 読んだ証跡とauthority

### 2.1 SpecDock正本

* `requirement.md`
* `design.md`
* `plan.md`
* current `report.md`
* S10 initial brief
* current provider runtime
* current exact-version artifact reader
* S09 characterization receipts
* S09 Red v6 PASS evidence

Canonical requirementは、submission stateだけでなくreconstruction mismatchの有無を判定できること、direct attachment failureを明示分類すること、五つのstage-specific failure classをgeneric capability reasonへ潰さないことを要求する。

Canonical designは、applicationがOracle metadata field名を知らず、profile-private parserがadapter-neutral evidenceへ変換すること、pre-submit new executionとpost-submit same-session recoveryを分離することを要求する。

Canonical planは、全failure classについて`prompt_submitted=False|None`ならharvest/captureが0であること、exact public pair、exact profile argv、最大一回のnew executionをS10 acceptanceとする。

### 2.2 Oracle source snapshot

添付Oracle sourceは次の論理ファイルから成る。

```text
workspace/tools/oracle/package.json
workspace/tools/oracle/src/sessionManager.ts
workspace/tools/oracle/src/browser/sessionRunner.ts
```

`package.json`はpackage versionを`0.17.0`とする。

`sessionManager.ts`は次を定義する。

* Oracle home配下の`sessions` directory。
* `<session-id>/meta.json`。
* temporary fileへのwrite後renameするmetadata更新。
* `SessionMetadata.id`、`status`、`mode`。
* `browser.runtime.promptSubmitted?: boolean`。
* `browser.modelSelection`。
* `artifacts[].validation`。
* `artifacts[].transfer`。
* `artifacts[].origin`。
* `response`。
* `transport`。
* `error`。
* `lifecycle`。 

`sessionRunner.ts`はbrowser execution結果からruntimeの`promptSubmitted`、model-selection evidence、artifactsを構成し、private callbackを通じてruntime hintをpersistできる構造を持つ。Model unavailable時には`status="unavailable"`、`verified=false`、`resolvedLabel=null`を構成する。

### 2.3 Existing characterization

S09 direct rerunは次を観測した。

```text
Oracle version = 0.17.0
requested model = gpt-5.6
observed model = GPT-5.6 Sol
strategy = select
verified = true
promptSubmitted = true
response complete = true
top-level status = completed
artifact kind = file/ZIP
transfer.status = not-needed
origin.mode = local
same-session command = session <id> --harvest --no-recover
```

Inline receiptはtext attachmentについてのみ`--browser-attachments never`の成功を観測したが、そのrunのmodel strategyは`current`、verifiedは`false`であり、model success evidenceには昇格していない。 

GPT-5.6 LunaまたはReasoning Effort Maxを実測値として記録しない。本ブリーフで使用するmodel telemetryは上記の`GPT-5.6 Sol / select / verified=true`と、inline runの`current / verified=false`だけである。

---

## 3. Evidence sufficiency matrix

| 契約要素                                 | Source上のfield／型                                                      |                                            実session観測 | 安全なproduction binding                                       | 判定               |
| ------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------: | ----------------------------------------------------------- | ---------------- |
| Exact session metadata path          | `<Oracle home>/sessions/<session-id>/meta.json`                      |                        S09 readerで同じsession rootを使用済み | exact invocation receiptから一件だけ注入可能                          | **sufficient**   |
| Session identity                     | `id`, `mode`                                                         |                                        `mode=browser` | exact session IDと`browser`を照合可能                             | **sufficient**   |
| Top-level terminal status            | `status`                                                             |                                           `completed` | exact `completed`だけをterminalとできる                            | **sufficient**   |
| Submission state                     | `browser.runtime.promptSubmitted`                                    |       `true`; pre-submit failuresで`false`も既存reportに観測 | exact boolのみ使用、missingは`None`                               | **sufficient**   |
| Model selection                      | requested/resolved/status/verified/strategy                          |             verified direct runとunverified inline run | source enumとexact fieldsを使用可能                               | **sufficient**   |
| Response completion                  | `response.status`, `incompleteReason`                                |                             completed response自体は観測済み | exact field valueのfixtureが必要。missingから推測不可                  | **partial**      |
| Artifact transfer                    | `not-needed`, `ready`, `streaming`, `completed`, `failed`, `skipped` |                                       `not-needed`を観測 | enum surfaceは確認済み                                           | **partial**      |
| Artifact pending                     | candidateは`ready`または`streaming`                                      |                                   独立pending fixtureなし | enum名だけでproduction actionを確定しない                             | **insufficient** |
| Transfer failed                      | candidateは`failed`                                                   |                                exact failed fixtureなし | output-download failureへのbindingは未検証                        | **insufficient** |
| Model unavailable                    | `modelSelection.status="unavailable"`                                |                                  source constructorあり | exact model classへbind可能                                    | **sufficient**   |
| Prompt reconstruction mismatch       | `error.category?: string`候補                                          | wrapper diagnostic identifierはあるがmeta field bindingなし | raw message／process exitから推測禁止                              | **insufficient** |
| Direct attachment submission failure | `error.category`または`transport.reason`候補                              | `attachment-send-not-ready`診断はあるがmeta field bindingなし | transfer fieldはoutput artifact用でありinput upload failureに流用不可 | **insufficient** |
| Closed transport reason              | `TransportFailureReason`をimport                                      |                              型定義／exact literalsが添付にない | generic string mappingは禁止                                   | **insufficient** |
| Error category producer              | `error.category?: string`                                            |                              exact producer／fixtureなし | known stage classへbind不可                                    | **insufficient** |
| Same-session harvest/capture argv    | profile-owned builder                                                |                                        同一commandを観測済み | S09 bindingを維持可能                                            | **sufficient**   |

### 結論

Exact pathとcore structured reader inputは定義できる。しかしCanonical S10は単なる`promptSubmitted` gateではなく、model、attachment、reconstruction、generation、downloadを互いに混同しないclosed taxonomyを要求する。

現在のsource evidenceから安全に生成できるのは、少なくとも次までである。

```text
prompt_submitted = True | False | None
model_selection = verified | unavailable | undecidable
top_level_status = completed | known_nonterminal | unknown
artifact_transfer = source enum value | missing | malformed
```

次はまだ安全に生成できない。

```text
failure_class = prompt_reconstruction_mismatch
failure_class = attachment_submission_failed
artifact_state = pending
failure_class = output_download_failed
```

既知のstage-specific classを`oracle_capability_unsupported`へ潰すこともCanonical REQ-030違反になるため、部分的なproduction classifierを先行投入しない。

---

## 4. Safe reader input / injection boundary candidate

この境界は採用可能な設計入力である。ただし、§5のmissing evidenceが揃うまでproductionへ実装しない。

### 4.1 Private invocation receipt

Current adapterがbrowser processを起動する直前に、privateな一回限りのreceiptを構成する。

```text
profile_version
profile_id
execution_index
session_id
session_root
metadata_path
logical_model
attachment_mode
```

Invariants:

```text
session_root = oracle_home(child_env) / "sessions" / session_id
metadata_path = session_root / "meta.json"
execution_index ∈ {0, 1}
profile_version ∈ {"0.16.1", "0.17.0"}
```

このreceiptはpublic result、application DTO、CLI、reportへserializeしない。

### 4.2 Reader injection

Versioned readerは次を引数として受け取る。

```text
session_root
session_id
oracle_version
logical_model
attachment_mode
```

Reader自身が次を行ってはならない。

```text
Path.home()
~/.oracle/sessions のlist/rglob/glob
最新sessionの探索
session IDの推測
Oracle configの解析
wrapper receiptの参照
stdout/stderrの解析
process exit codeによるstage推測
```

Readerは、SpecDockがそのexecution用に生成したexact session ID配下の`meta.json`一件だけをdescriptor-rootedに読む。

### 4.3 Path safety

既存`issue_planning_oracle_artifact.py`のdescriptor-rooted regular-file readerを再利用する。

必須検証:

* `session_root.name == session_id`
* `metadata_path == session_root / "meta.json"`
* Oracle version exact match
* session mode exact `browser`
* metadata size上限
* UTF-8 strict
* duplicate JSON key拒否
* non-standard number拒否
* symlink／root swap／path escape拒否
* file identityのread前後不変
* raw pathを例外に含めない

### 4.4 Existing artifact readerを緩めない

Current `_read_metadata_0170()`はartifact snapshot用に`status=="completed"`を要求している。このfunctionをpre-submit reader用に緩めてはならない。

将来実装する場合は、別entry pointを追加する。

```text
read_attempt_metadata_0170
```

役割:

* `_read_metadata_for_version()`のidentity／path safetyを再利用する。
* `completed`以外のattempt metadataも読む。
* Artifact snapshotやReview JSON extractionを行わない。
* Raw message、URL、handle、promptをreturnしない。
* Adapter-neutralなsanitized scalarだけをreturnする。

---

## 5. S10をunblockするために必要なexact evidence

次の全てを、一つのOracle `0.17.0` source identityまたはsanitized native fixtureへbindする。

### 5.1 Prompt reconstruction mismatch

必要証跡:

```text
promptSubmitted = false
exact top-level status
exact response status or absence
exact error.category or transport.reason
producer source location
raw diagnostic messageを使わず同classを識別できること
```

必要なpositive fixture:

```text
failure_class = prompt_reconstruction_mismatch
```

必要なnegative fixture:

```text
同じpromptSubmitted=falseでも
model unavailable / attachment failure / unknown infrastructureを
reconstruction mismatchへ分類しない
```

### 5.2 Direct attachment submission failure

必要証跡:

```text
attachment mode = direct
promptSubmitted = false
exact structured failure field
exact field value
producer source location
```

`artifacts[].transfer`はoutput artifact transfer用であり、input attachment upload failureの代替証跡にしてはならない。

必要なpositive fixture:

```text
failure_class = attachment_submission_failed
inline eligibility = exact characterized text-only condition
```

### 5.3 Response incomplete

必要証跡:

```text
promptSubmitted = true
response.status = exact non-completed value
top-level status
response.incompleteReasonのclosed valueまたはabsence
same-session harvest前後のmetadata
```

これにより`generation_incomplete`とinfrastructure-undecidableを分離する。

### 5.4 Artifact pending

必要証跡:

```text
promptSubmitted = true
response.status = completed
matching expected file artifact entry
transfer.status = exact pending value
capture前metadata
same-session capture後metadata
```

`response complete + artifact entry absence`をpendingと推測しない。

### 5.5 Transfer failed

必要証跡:

```text
promptSubmitted = true
response.status = completed
matching expected file artifact
transfer.status = failed
capture前後のmetadata
```

`validation.ok=false`はtransfer failureではなくartifact rejection familyへ分離する。

### 5.6 Source binding

次のいずれかが必要である。

1. `error.category`／`transport.reason`へexact failure valueを書き込むOracle source producer。
2. Exact source HEADに対するunit test。
3. Exact PATH Oracleから得たsanitized `meta.json` fixture。

Source type宣言だけ、wrapper logだけ、human-readable error messageだけでは不十分である。

---

## 6. 現時点のallowlist

### 6.1 直ちに許可するsemantic mutation

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/
report.md
```

### 6.2 Immutable brief import

本回答本文をbyte-identicalに次へ保存できる。

```text
${ISSUE_DIR}/artifacts/implementation-briefs/
s10-stage-recovery-taxonomy-v2-20260806.md
```

Brief artifactはsemantic production mutationではない。

### 6.3 任意の追加characterization artifact

不足証跡を取得した場合だけ、sanitized evidenceを次へ保存できる。

```text
${ISSUE_DIR}/artifacts/characterization/
s10-oracle-017-attempt-metadata-20260806.md
```

許容内容:

* Oracle version
* Oracle source HEAD
* profile ID
* field names
* closed enum values
* boolean／status matrix
* call counts
* sanitized dummy session ID
* sanitized relative dummy paths

禁止内容:

* Prompt
* Transcript
* ChatGPT URL
* Conversation ID
* Chrome target ID
* Local absolute path
* User config
* Credentials
* Raw error message
* Session handle
* Attachment contents

### 6.4 現時点で変更禁止

```text
src/spec_dock/
tests/
requirement.md
design.md
plan.md
decisions/
MANIFEST.json
CHECKSUMS.sha256
S09 characterization receipts
S09 implementation and repair briefs
S09 Red reviews
EAL-067〜EAL-083
OAL-001/OAL-002
```

---

## 7. Conditional production/test allowlist

§5の全evidenceが揃い、EAL-084後の別preflightでgateを明示的にunblockした場合に限り、次を許可する。

### 7.1 Production

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

### 7.2 Tests

```text
tests/unit/domain/test_issue_planning_contracts.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/application/test_issue_planning.py
tests/unit/commands/test_issue_planning.py
tests/cli_runtime/test_chatgpt_cli.py
```

### 7.3 Read/run-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
application/ports.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
commands/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
presentation/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
cli/bootstrap.py

tests/integration/test_issue_planning_e2e.py
```

Read/run-only pathの変更が必要ならallowlistを黙示拡張せず停止する。

---

## 8. Conditional typed domain contract

不足証跡が揃った後、次のclosed typesを実装する。

### 8.1 `OracleStage`

```text
preflight
browser_ready
model_selected
attachments_prepared
prompt_reconstructed
prompt_submitted
response_completed
artifact_downloaded
artifact_snapshotted
```

### 8.2 `OracleFailureClass`

```text
executable_unavailable
managed_chrome_unavailable
profile_unsupported
capability_missing
submission_state_unknown
profile_builder_missing
model_selection_unavailable
attachment_submission_failed
prompt_reconstruction_mismatch
generation_incomplete
session_recovery_required
output_download_failed
artifact_missing
artifact_ambiguous
artifact_validation_failed
```

禁止member:

```text
unknown
other
generic_error
retryable_error
```

### 8.3 `RecoveryAction`

```text
block
new_execution_same_model
new_execution_inline
same_session_harvest
same_session_capture
accept
```

### 8.4 `RecoveryBudget`

Exact fields:

```text
automatic_new_executions_remaining = 1
same_session_harvest_remaining = 1
same_session_capture_remaining = 1
```

Invariants:

* Exact `int`だけ。`bool`禁止。
* 値は`0|1`だけ。
* Model retryとinline retryは同じnew-execution budgetを消費する。
* Budget resetなし。
* Recursive retryなし。
* Configurable retry countなし。

### 8.5 `OracleAttemptEvidence`

Canonical fields:

```text
profile_version
terminal_stage
logical_model
observed_model_label
model_verified
attachment_mode
prompt_submitted
response_completed
artifact_state
failure_class
```

Invariants:

* `prompt_submitted=False|None`ではresponse complete、artifact downloaded、artifact snapshottedを禁止。
* `response_completed=True`なら`prompt_submitted=True`。
* Artifact pending／downloaded／invalidなら`prompt_submitted=True`。
* `generation_incomplete`なら`prompt_submitted=True`かつresponse completeではない。
* `output_download_failed`なら`prompt_submitted=True`かつresponse complete。
* `model_selection_unavailable`、`attachment_submission_failed`、`prompt_reconstruction_mismatch`なら`prompt_submitted=False`。
* Contradictory evidenceはconstructorで拒否する。
* Raw metadata objectをfieldとして保持しない。

---

## 9. Conditional reader／mapper／application changes

### 9.1 `issue_planning_oracle_artifact.py`

追加候補:

```text
OracleAttemptMetadata
OracleArtifactReader.read_attempt_metadata
read_attempt_metadata_0161
read_attempt_metadata_0170
```

`OracleAttemptMetadata`に許可するscalar:

```text
top_level_status
prompt_submitted
model_selection_status
requested_model
resolved_model_label
model_strategy
model_verified
response_status
response_incomplete_reason_code
artifact_transfer_statuses
artifact_validation_states
error_category
transport_reason
```

次は保持しない。

```text
error.message
error.details
promptPreview
options.prompt
cwd
runtime tab URL
conversation ID
Chrome profile
Chrome target ID
artifact sourceUrl
artifact path
origin.host
```

0.16.1:

* Existing successful terminal artifact pathを維持する。
* Prompt submission evidenceはuncharacterizedなので`None`。
* Recoveryが必要な状態ではcapability unsupported。
* Stage-blind harvestを継続しない。
* Exact 0.16.1 argv builderは変更しない。

0.17.0:

* Exact `meta.json` reader。
* Exact version／id／browser mode。
* Unknown or malformed fieldsはfail-closed。
* Existing completed-only artifact snapshot entry pointsは変更しない。

### 9.2 `issue_planning_chatgpt.py`

追加候補:

```text
_OracleExecutionReceipt
_decode_attempt_evidence
_decide_oracle_recovery
_run_initial_execution
_run_one_pre_submit_recovery
_run_post_submit_recovery
```

構造上の制約:

* New execution APIを持つfunctionとsame-session recovery functionを分離する。
* Post-submit functionへbrowser argv builder／session ID factoryを渡さない。
* Generic adapterがsame-session commandを組み立てない。
* Exact profile builderだけを呼ぶ。
* Stdout／stderr／exception messageをfailure classifierへ渡さない。
* Process return codeはdiagnosticでありstage authorityではない。

### 9.3 `issue_planning_contracts.py`

* Five newpublic reasonsを追加する。
* Exact Oracle status/reason pairをconstructorで閉じる。
* Unknown `oracle_*` reasonを拒否する。
* Unknown internal classにdefault mapperを作らない。
* Private attempt evidenceを`to_dict()`へ含めない。

### 9.4 `application/issue_planning.py`

* Infraが生成したexact typed pairを変更せず`PlanningCommandResult`へ投影する。
* Application側でOracle metadata fieldを読まない。
* Generic status/reason normalizationを追加しない。
* `details`へraw diagnosticsをコピーしない。
* Pre-submit failureでBlue／Red thread bindingをadvanceしない。

### 9.5 Commands／CLI

Production変更なし。

Testsで次を固定する。

* TextとJSONが同じpair。
* Exit code `1`。
* Raw metadata／path／prompt／URL／session handleが出ない。
* New retry optionがhelpへ出ない。

---

## 10. Exact public mapping

| Internal class                                                            | Public status | Public reason                           |
| ------------------------------------------------------------------------- | ------------- | --------------------------------------- |
| executable／managed Chrome unavailable                                     | `blocked`     | `oracle_unavailable`                    |
| profile unsupported／capability missing／submission unknown／builder missing | `blocked`     | `oracle_capability_unsupported`         |
| model selection unavailable                                               | `blocked`     | `oracle_model_selection_unavailable`    |
| attachment submission failed                                              | `blocked`     | `oracle_attachment_submission_failed`   |
| prompt reconstruction mismatch                                            | `blocked`     | `oracle_prompt_reconstruction_mismatch` |
| generation incomplete                                                     | `blocked`     | `oracle_generation_incomplete`          |
| same-session recovery infrastructure unsafe／undecidable                   | `blocked`     | `oracle_session_recovery_required`      |
| output download failed                                                    | `blocked`     | `oracle_output_download_failed`         |
| artifact missing                                                          | `rejected`    | `oracle_artifact_missing`               |
| artifact ambiguous                                                        | `rejected`    | `oracle_artifact_ambiguous`             |
| artifact validation defect                                                | `rejected`    | `oracle_artifact_rejected`              |

Rules:

* Known stage-specific classを`oracle_capability_unsupported`へ変換しない。
* `oracle_session_recovery_required`をknown-stage catch-allにしない。
* Many-to-oneはcapability/profile、runtime unavailable、artifact validationの三familyだけ。
* Unknown raw categoryはknown internal classを生成しない。
* Unknown raw categoryのoperationはfail closedで停止し、mapperへ渡さない。

---

## 11. Call-count／budget contract

| 状態                                                                | New execution | Successful submission | Harvest builder／process | Capture builder／process |
| ----------------------------------------------------------------- | ------------: | --------------------: | ----------------------: | ----------------------: |
| Unknown profile                                                   |             0 |                     0 |                   0 / 0 |                   0 / 0 |
| `promptSubmitted=None`                                            |             0 |                     0 |                   0 / 0 |                   0 / 0 |
| `promptSubmitted=false`、unknown class                             |             0 |                     0 |                   0 / 0 |                   0 / 0 |
| Model unavailable、budget 1                                        |             1 |                 0または1 |                   0 / 0 |                   0 / 0 |
| Model unavailable、budget 0                                        |           0追加 |                     0 |                   0 / 0 |                   0 / 0 |
| Exact direct attachment failure、inline characterized、budget 1     |             1 |                 0または1 |                   0 / 0 |                   0 / 0 |
| Reconstruction mismatch                                           |             0 |                     0 |                   0 / 0 |                   0 / 0 |
| Submitted=true、generation incomplete                              |             0 |                     1 |               最大1 / 最大1 |                   0 / 0 |
| Submitted=true、response complete、artifact pending／transfer failed |             0 |                     1 |                   0 / 0 |               最大1 / 最大1 |
| Artifact invalid                                                  |             0 |                     1 |                     0追加 |                     0追加 |
| Accepted artifact                                                 |             0 |                     1 |                   0または1 |                   0または1 |

Global invariants:

```text
maximum browser executions = 2
maximum automatic new executions = 1
maximum successful ChatGPT submissions = 1
maximum harvest = 1
maximum capture = 1
model and inline retry share one budget
post-submit new execution = 0
pre-submit same-session command = 0
```

Model retry後にattachment failureが起きてもinlineへ進まない。

---

## 12. Red／Green test matrix

現時点では、`blocked`としたfixtureを推測生成してはならない。

| Test                                     | Expected                                      | Current evidence                           |               |
| ---------------------------------------- | --------------------------------------------- | ------------------------------------------ | ------------- |
| Exact session root／meta path             | One explicit path only、directory scan 0       | **Greenable**                              |               |
| Wrong session ID／mode／version            | Reject                                        | **Greenable**                              |               |
| Symlink／root swap／oversize／duplicate key | Reject                                        | **Greenable**                              |               |
| `promptSubmitted=true`                   | Post-submit                                   | **Greenable**                              |               |
| `promptSubmitted=false`                  | Pre-submit、harvest/capture 0                  | **Greenable**                              |               |
| `promptSubmitted` missing／non-bool       | Unknown、capability unsupported、all recovery 0 | **Greenable**                              |               |
| Model status unavailable                 | Model failure candidate                       | **Greenable from source**                  |               |
| Verified model selection                 | Preserve observed label privately             | **Greenable from source/receipt**          |               |
| Reconstruction mismatch positive         | Exact class、retry 0                           | **Blocked: exact meta field/value absent** |               |
| Direct attachment failure positive       | Exact class、inline budget 1                   | **Blocked: exact meta field/value absent** |               |
| Unknown error category                   | No stage-specific class、all recovery 0        | **Greenable**                              |               |
| Response completed                       | Exact response field                          | **Blocked until exact fixture**            |               |
| Generation incomplete                    | Harvest once                                  | **Blocked until exact fixture**            |               |
| Artifact pending                         | Capture once                                  | **Blocked until exact fixture**            |               |
| Transfer failed                          | Capture once then output-download reason      | **Blocked until exact fixture**            |               |
| Validation false                         | Artifact rejected、recovery 0                  | **Greenable from schema**                  |               |
| `promptSubmitted=False                   | None` cross-product                           | Builder/process/poll all 0                 | **Greenable** |
| Unknown internal class public mapping    | Constructor/mapper rejection                  | **Greenable**                              |               |
| Raw diagnostics privacy                  | Public result contains none                   | **Greenable**                              |               |
| 0.16.1 exact argv/profile                | Unchanged                                     | **Existing S09 regression**                |               |
| 0.17.0 exact profile/builders/reader     | Unchanged                                     | **Existing S09 regression**                |               |

S10 implementationを開始するには、表の五つのblocked positive fixtureを先に証跡化する。

---

## 13. EAL-084 exact append-only row

EAL-083を一文字も変更せず、その直後へ次の14-field rowを追加する。

```markdown
| EAL-084 | partially_adopted | `artifacts/implementation-briefs/s10-stage-recovery-taxonomy-v2-20260806.md`; Oracle `0.17.0` source snapshot at provided HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; `artifacts/characterization/s09-oracle-017-native-rerun-20260806.md`; `artifacts/characterization/s09-oracle-017-native-inline-20260806.md` | oracle-source-characterization / chatgpt-use-blue-team | Oracle `0.17.0`は`<Oracle home>/sessions/<session-id>/meta.json`へversion-bound structured session metadataを書き、`promptSubmitted`、model-selection evidence、response、artifact validation／transfer／origin、transport、error、lifecycleのfield surfaceを持つため、EAL-083のstorage pathとcore reader-input gapは解消した。一方、prompt reconstruction mismatchとdirect attachment submission failureをexact structured valueへbindするproducer／fixture、および独立artifact-pending／transfer-failed fixtureがなく、Canonical S10 taxonomyを推測なしで実装できない | `report.md`, conditional S10 production/test allowlist | S10 evidence gate and revised implementation boundary | Exact session pathはcurrent invocationが生成したsession IDから一意に注入でき、arbitrary Oracle-home scanやChatGPT-Use wrapper dependencyは不要である。ただしopen `error.category`、未展開`TransportFailureReason`、未観測pending stateをstage-specific classへ推測変換するとREQ-025〜REQ-030に違反するためproduction implementationは継続blockする | source_schema_partial | SpecDock repository/branch/HEAD `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract` / `04c76a7bef2e997f98d5b791c5c9da2d068fb378`; Oracle provided source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`; package version `0.17.0`; S09 observed model `GPT-5.6 Sol`, strategy `select`, verified `true`; inline run model verified `false` | issue orchestrator | ChatGPT-Use Blue Team | yes | Exact 0.17 sanitized fixturesとproducer bindingでreconstruction、direct attachment failure、response incomplete、artifact pending、transfer failedを確定する。全五fixtureが揃うまでsource/test変更、S10 fresh Red review、S10 closure、S11以降、PR、merge、Issue close、Issue finishを行わない |
```

---

## 14. S10 current-state exact replacement rows

### 14.1 Implementation Delegation Gate

```markdown
| S10 | blocked / source-path-characterized / failure-semantics-pending | Oracle 0.17.0のexact session metadata pathとcore structured schemaは確認したが、Canonical S10のstage-specific taxonomyを成立させるclosed failure producer／fixtureが不足しているためproduction implementationを開始しない | dev-coder / issue orchestrator | `report.md`、EAL-082〜EAL-084、S10 v1/v2 briefs、S09 immutable evidence、Oracle source snapshot、将来のsanitized S10 characterization artifact | plan.md、current Issue scope、exact SpecDock branch/HEAD、provided Oracle source HEAD | 現時点ではEAL-084追加とS10 current-state同期だけ。Exact reconstruction／attachment／response-incomplete／artifact-pending／transfer-failed evidence取得後にconditional allowlistを再度preflightする | S09 runtime／tests／profile／reader／builders、requirement/design/plan、wrapper/API/default branch/alternate backend、raw Oracle diagnostics、S11以降、PR、merge、Issue close、Issue finishを変更しない | exact branch/HEAD、EAL-083 immutability、EAL-084 field count、Oracle source/receipt identity、missing-evidence matrix、SpecDock validate、diff-check、scope audit | open error categoryの推測、stdout/stderr分類、artifact absenceからpending推測、input attachment failureへoutput transferを流用、allowlist driftでは停止する | blocked evidence update、exact missing-evidence list、conditional implementation allowlist。production/test Candidateは生成しない | EAL-083の当時のblocked判断は維持する。EAL-084でstorage path/core schema判明を採用するが、closed failure semanticsが不足するためS10はblocked、closure claimは`none` |
```

### 14.2 Delegated Worker Evidence

```markdown
| S10 | dev-coder / issue orchestrator | Initial workerはEAL-083で推測実装を停止した。追加Oracle source inspectionによりexact `meta.json` path、promptSubmitted、modelSelection、response、artifact transfer surfaceは確認したが、reconstruction／direct attachment failureのclosed category producerとartifact-pending／transfer-failed positive fixtureは確認できなかった | Production/test変更なし。Semantic mutationは`report.md`のみ。本v2 briefはimmutable evidence import | GitHub exact HEAD parity、Oracle package/version/source field inspection、S09 direct/inline receipts、EAL-083 historical preservation、`git diff --check`、SpecDock validate | blocked; fresh implementation review not started | Reader path boundaryは解消したがCanonical five stage-specific mappingsのうち複数が未characterize。Known classをcapability reasonへ潰すことも不可 | EAL-084をappend-only採用し、exact five-state fixture取得までS10をblockedに保つ。Production/test commit Candidate、fresh Red、S11開始は行わない |
```

### 14.3 Parent Implementation Exception

```markdown
| S10 | no delegation exception; source evidence precondition remains blocking | user request to revisit the exact structured source; risk accepted: no | 現時点のsemantic allowlistは`report.md`のみ。Conditional production/test allowlistはmissing evidence解消後にだけ有効 | Oracle source/core-schema inspection、S09 receipt reconciliation、EAL-084 report-only update | 失敗時はsource HEAD `04c76a7bef2e997f98d5b791c5c9da2d068fb378`のreportへ戻す。EAL-083、S09 closure、briefs、receiptsを保持する | branch/source identity、EAL equality、scope audit、validate、diff-check | Error category／transport reason／pending stateを推測しない。必要なproducer／fixtureがない限りproduction implementationへ進まない |
```

### 14.4 Reviewer Gate Status

```markdown
| S10 | implementation review | ChatGPT-Use Red Team | not started / source-characterization incomplete | blocked | no | EAL-083のstorage/path不存在という説明はEAL-084で「exact path/core schemaあり」へ更新するが、prompt reconstruction、direct attachment failure、response incomplete、artifact pending、transfer failedのclosed positive evidenceが不足する。Production implementation Candidateがないためfresh Red reviewは開始しない | EAL-082 initial brief、EAL-083 blocked handoff、EAL-084 partial source adoption、SpecDock source HEAD `04c76a7bef2e997f98d5b791c5c9da2d068fb378`、Oracle provided source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`、S09 characterization receipts |
```

### 14.5 Milestone / Commit Candidate Gate

```markdown
| S10 | blocked / no production-test commit candidate | SpecDock source HEAD `04c76a7bef2e997f98d5b791c5c9da2d068fb378`、EAL-082 initial brief、EAL-083 blocked handoff、EAL-084 partial source-schema adoptionをcurrent S10 ledgerとする。S09 Candidate version／ID／implementation commitは不変 | Current sourceはnamed branch exact HEAD。Oracle source identityはprovided HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270`／package `0.17.0`として記録し、SpecDock GitHub identityと分離する | Report-only evidence commit/push後にworktree clean、HEAD/upstream exact、ahead `0`／behind `0`を確認する。Resulting SHAは事前reportへ自己参照しない | Production source、tests、canonical docs、S09 evidenceはno-op。Current changeはblocked reasonの精密化とmissing-evidence contractだけである | Conditional source/test allowlist、S09 files、requirement/design/plan、ADR、MANIFEST、CHECKSUMS、receipts、reviews | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; EAL-083 equality; EAL-084 14 fields; scoped diff; post-push parity | S10はblockedを維持する。Exact five-state evidence取得後に別のunblock brief／implementation Candidateを作成し、その後だけfresh Red reviewへ進む。S11以降、PR、merge、Issue close、Issue finishは保留する |
```

---

## 15. 現時点で実行するverification

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
SOURCE='04c76a7bef2e997f98d5b791c5c9da2d068fb378'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE"
test "$(git rev-parse '@{upstream}')" = "$SOURCE"
test -z "$(git status --short)"
```

### EAL-083不変／EAL-084追加

```bash
python - "$ISSUE_DIR/report.md" <<'PY'
from pathlib import Path
import subprocess
import sys

SOURCE = "04c76a7bef2e997f98d5b791c5c9da2d068fb378"
path = Path(sys.argv[1])
relative = path.as_posix()

before = subprocess.check_output(
    ["git", "show", f"{SOURCE}:{relative}"],
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

assert row(before, "EAL-083") == row(after, "EAL-083")
eal_084 = row(after, "EAL-084")
assert len([part.strip() for part in eal_084.strip("|").split("|")]) == 14
assert after.index(eal_084) > after.index(row(after, "EAL-083"))
PY
```

### Scope

```bash
git diff --name-only
```

許容値:

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/artifacts/implementation-briefs/s10-stage-recovery-taxonomy-v2-20260806.md
```

### Repository checks

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

Production／test baselineは変更しないため、pytest、Ruff、Mypyの新しいGreen結果を主張しない。

---

## 16. Conditional implementation verification

§5のevidenceが揃ってproduction gateを別途unblockした後に実行する。

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

Static:

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

Forbidden behavior audit:

```bash
rg -n \
  'Path\.home|rglob|glob\(|listdir|scandir|stdout.*prompt|stderr.*prompt|errorMessage|error\.message|details.*message' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

Generic recovery-token audit:

```bash
rg -n \
  '"session"|--harvest|--no-recover' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

Expected:

* Literal recovery tokensはexact profile builder definitionsだけ。
* Generic decision／orchestration codeのassemblyは0。

---

## 17. Stop gates

次のいずれかではproduction／test実装を開始しない。

1. Named branch tipが`04c76a7...`と一致しない。
2. Default branchまたは別branchが必要になる。
3. Oracle source snapshotとpackage versionのidentityが再現できない。
4. Exact session pathをcurrent invocation receiptから一意に構成できない。
5. Arbitrary Oracle-home scanが必要になる。
6. Oracle config、target URL、wrapper receiptの解析が必要になる。
7. `promptSubmitted` missingをFalseへ変換する必要がある。
8. Prompt reconstructionをraw message substringから分類する必要がある。
9. Attachment failureをprocess exit、timeout、artifact transferから推測する必要がある。
10. `error.category`の未確認値をhardcodeする必要がある。
11. `TransportFailureReason`の未確認literalを発明する必要がある。
12. Response completeをtop-level completedまたはartifact existenceだけから推測する必要がある。
13. Artifact absenceをpendingへ変換する必要がある。
14. `transfer.status`のsource enumだけでcapture behaviorをproduction-enableし、positive fixtureを省略する必要がある。
15. Known stage-specific classをcapability／session-recovery reasonへ潰す必要がある。
16. 0.16.1 reader／argv／profileをS09 evidence外で変更する必要がある。
17. Wrapper／API／alternate backend／alternate modelが必要になる。
18. Pre-submit harvest/capture cleanup例外が必要になる。
19. New executionを二回以上許可する必要がある。
20. Successful submissionが二回になり得る。
21. Post-submit pathからnew execution APIへ到達できる。
22. S11 browser smokeまたはS12 artifact-validation変更を先取りする必要がある。
23. Conditional allowlist外のsource／test変更が必要になる。
24. Raw diagnosticsをpublic resultへ出す必要がある。

---

## 18. Handoff

### 現時点

```text
handoff_status = blocked
fresh_red_review = not_started
production_candidate = none
test_candidate = none
closure_claim = none
next_action = exact structured failure characterization
```

### 次のevidence handoffに必須のfields

```text
SpecDock repository
SpecDock named branch
SpecDock exact HEAD

Oracle package version
Oracle source HEAD
Oracle source file and producer symbol

sanitized fixture ID
top-level status
mode
promptSubmitted
modelSelection.status
modelSelection.verified
response.status
response.incompleteReason code
artifact kind
artifact validation.ok
artifact transfer.status
error.category
transport.reason

expected OracleFailureClass
expected RecoveryAction
expected public status
expected public reason

expected new-execution count
expected successful-submission count
expected harvest builder/process count
expected capture builder/process count
```

### Fresh Red reviewを開始できる条件

次の全てを満たしたresulting pushed exact HEADだけをfresh Redへ渡す。

1. §5の五つのpositive fixtureがexact source identityへbindされている。
2. Conditional production/test allowlistだけが変更されている。
3. Domain mapperにdefault branchがない。
4. Pre-submit False／None cross-productでsame-session call countが全て0。
5. Initial + one retryの最大2 executions。
6. Successful submission最大1。
7. Harvest／capture各最大1。
8. Exact profile argv assertionsがpass。
9. Five stage-specific public reasonsが互いにdistinct。
10. S09 regressionがpass。
11. Raw diagnostics privacy testsがpass。
12. Ruff、Mypy、validate、diff-checkがpass。
13. Branch／upstream exact parity。
14. `closure_claim=none`。
15. `handoff_status=ready_for_fresh_review`。

Fresh RedでP0/P1=`0`になるまで、S10 closure、S11以降、PR、merge、Issue close、Issue finishを行わない。
