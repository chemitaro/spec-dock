# iss-00354 S10 実装ブリーフ — Stage Evidence / Failure Taxonomy / Bounded Recovery

## 0. 固定identityと実装ゲート

| 項目                        | 固定値                                                                               |
| ------------------------- | --------------------------------------------------------------------------------- |
| Repository                | `chemitaro/spec-dock`                                                             |
| Named branch              | `codex/iss-00354-chatgpt-context-contract`                                        |
| Source HEAD               | `4ff7f8528e714c6a4523f7e92b1d5c4d216d5099`                                        |
| GitHub branch parity      | named branch tipとsource HEADは`identical`、ahead `0`、behind `0`                     |
| Default branch fallback   | 禁止・未使用                                                                            |
| Active step               | S10のみ                                                                             |
| S09 Candidate version     | `s09-blue-repair-v2`                                                              |
| S09 implementation commit | `470cacf5051272edfa71e9780f263d1f402a33a0`                                        |
| S09 final reviewed HEAD   | `b3e281af2c4380c9937bfcf862bd295d3d6be960`                                        |
| S09 final verdict         | Fresh Red v6 PASS、P0=`0`、P1=`0`、P2=`0`、P3=`0`                                     |
| S09 closure-sync HEAD     | `4ff7f8528e714c6a4523f7e92b1d5c4d216d5099`                                        |
| Worker target             | GPT-5.6 Luna / Reasoning Effort Maxは実行設定であり、wrapper telemetryで実測されない限り証跡値として記録しない |
| Expected worker state     | `ready_for_fresh_review`                                                          |
| `closure_claim`           | `none`                                                                            |

GitHub connectorで指定named branchとsource HEADの完全一致を確認済みである。添付bundleのcanonical requirement／design／plan／report、関連source／testsも補助入力として照合した。

S09はexact `0.16.1`／`0.17.0` profile、version-bound reader、completed-only decoder、profile-owned harvest／capture builders、unknown-version fail-closedを実装し、Fresh Red v6で正式PASSしている。S10ではこのS09契約を再設計、再characterize、上書きしない。

---

## 1. 目的

S10の目的は、現行のstage-blind recoveryを、次の閉じたtyped contractへ置換することである。

1. Oracle attemptから、profile-privateなstructured evidenceを`OracleAttemptEvidence`へdecodeする。
2. `prompt_submitted`を境界として、pre-submit new executionとpost-submit same-session recoveryを完全に分離する。
3. Pre-submitのmodel retryとinline attachment retryで一つのoverall budgetを共有し、new executionを最大1回に制限する。
4. 一つのoperation lineageにおけるsuccessful ChatGPT submissionを最大1回にする。
5. Post-submitではselected profileのharvest／capture builderだけを各最大1回使用する。
6. Internal failure classを、canonical planのexact public `status`／`reason` pairへ一意に写像する。
7. Domain、application、CLI text／JSONが同じtyped pairを保持する。
8. Raw Oracle stdout／stderr、UI text、prompt、URL、session handle、transcriptをpublic resultへ出さない。

Canonical designはsubmissionを回復境界とし、pre-submitは限定new execution、post-submitはsame-sessionのみと定めている。Recovery actionとbudgetも閉じた型として定義されている。

---

## 2. 非目的

S10では次を行わない。

* S09 exact profile、reader schema、browser argv、same-session commandの再設計。
* Oracle `0.17.0`以外のversion追加、semver range、unknown patch acceptance。
* Personal wrapper、Oracle API、alternate backend、default branchへのfallback。
* Model `current`、別model、別strategyへの黙示fallback。
* Required attachmentのdrop、automatic ZIP、copy、conversion、content scan。
* Generic retry loop、unbounded retry、pre-submit cleanup用harvest例外。
* Public retry option、CLI flag、backend selectorの追加。
* S11のlive browser/model smoke。
* S12の新artifact reader schema、download state machine、output validator変更。
* S13のprojection／whole-Issue closure。
* PR作成、merge、Issue close、Issue finish。

---

## 3. 現行コードとの差分

### 3.1 S09で成立済みの境界

Current adapterは、exact `0.16.1`と`0.17.0` profileを持ち、各profileがbrowser argv、stage decoder、artifact reader、harvest builder、capture builderを所有している。0.17.0のharvestとcaptureは、characterize済みの同じ`session <id> --harvest --no-recover` builderへ明示bindされている。

維持するもの:

* 0.16.1の旧browser argv。
* 0.16.1／0.17.0のexact same-session argv。
* Exact version registry。
* Required root／session help token検証。
* Managed Chrome preflight。
* Executable identity recheck。
* `shell=False`、stdin disabled、sanitized environment。
* Existing ZIP／JSON validation。
* 0.17 Reviewer pre-submit capability block。
* Unknown version fail-closed。

### 3.2 現行のS10未実装部分

`invoke_issue_planning_chatgpt()`は現在、一つのbrowser execution後にprocess nonzero／timeoutまたはsession nonterminalを検出すると、submission evidenceを確認せず`_recover_same_session()`へ入る。

`_recover_same_session()`も、`prompt_submitted`を受け取らず、selected profileのharvest builderを一度呼ぶstage-blind構造である。Capture builderはprofileに存在するが、runtimeから使用されていない。

不足しているもの:

* `OracleStage`
* `OracleAttemptEvidence`
* `OracleFailureClass`
* `RecoveryAction`
* `RecoveryBudget`
* Pure decision function
* Structured attempt-evidence decoder
* Pre-submit new-execution budget
* Inline new-execution path
* Successful submission count
* Post-submit capture invocation
* Exact internal failure → public pair mapper
* Five newpublic reasons
* Domain／application／CLIのclosed Oracle pair enforcement

### 3.3 Domainとapplicationの現状

`PlanningInvocationResult`は既存Oracle reasonsを検証するが、S10の五つのstage-specific reasonをまだ持たない。`PlanningCommandResult`はsuccess pairだけを閉じ、non-successでは任意のlower-snake-case reasonを受理するため、未知の`oracle_*` reasonも現状は通り得る。

Applicationはtransport failureの`status`、`reason`、`details`をそのまま`PlanningCommandResult`へ投影している。

CLI text／JSON rendererは`PlanningCommandResult.to_dict()`を忠実にserializeしているため、production serializerの変更は不要である。Domainとapplicationでpairを閉じ、CLI testsでbyte-level expectationを固定する。

### 3.4 現行testsの変更点

Current infra testsには、timeout／nonzero／nonterminalでprompt 1回、harvest 1回となるS09までのstage-blind characterizationが残る。S10ではこれを削除するのではなく、次の二群へ分割する。

* Exact S09 builder／argv regression。
* Submission evidenceに従うS10 invocation expectation。

現行stage-blind invocation expectationをS10の正しいproduction behaviorとして残してはならない。

---

## 4. 実装するdomain contract

実装場所:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
domain/issue_planning_contracts.py
```

### 4.1 `OracleStage`

```python
class OracleStage(str, Enum):
    PREFLIGHT = "preflight"
    BROWSER_READY = "browser_ready"
    MODEL_SELECTED = "model_selected"
    ATTACHMENTS_PREPARED = "attachments_prepared"
    PROMPT_RECONSTRUCTED = "prompt_reconstructed"
    PROMPT_SUBMITTED = "prompt_submitted"
    RESPONSE_COMPLETED = "response_completed"
    ARTIFACT_DOWNLOADED = "artifact_downloaded"
    ARTIFACT_SNAPSHOTTED = "artifact_snapshotted"
```

Canonical designのstage名称をそのまま使用する。

### 4.2 `OracleFailureClass`

Canonical planはfailure classの意味とpublic mappingを閉じているが、Python enum宣言自体は提示していない。最小実装では、mapping tableの各意味を次のclosed enumへ固定する。

```python
class OracleFailureClass(str, Enum):
    EXECUTABLE_UNAVAILABLE = "executable_unavailable"
    MANAGED_CHROME_UNAVAILABLE = "managed_chrome_unavailable"

    PROFILE_UNSUPPORTED = "profile_unsupported"
    CAPABILITY_MISSING = "capability_missing"
    SUBMISSION_STATE_UNKNOWN = "submission_state_unknown"
    PROFILE_BUILDER_MISSING = "profile_builder_missing"

    MODEL_SELECTION_UNAVAILABLE = "model_selection_unavailable"
    ATTACHMENT_SUBMISSION_FAILED = "attachment_submission_failed"
    PROMPT_RECONSTRUCTION_MISMATCH = "prompt_reconstruction_mismatch"
    GENERATION_INCOMPLETE = "generation_incomplete"
    SESSION_RECOVERY_REQUIRED = "session_recovery_required"
    OUTPUT_DOWNLOAD_FAILED = "output_download_failed"

    ARTIFACT_MISSING = "artifact_missing"
    ARTIFACT_AMBIGUOUS = "artifact_ambiguous"
    ARTIFACT_VALIDATION_FAILED = "artifact_validation_failed"
```

禁止:

* `UNKNOWN`
* `OTHER`
* `RETRYABLE_ERROR`
* Generic backend error class
* String→enum default
* Unknown class→generic public reason

### 4.3 `OracleAttemptEvidence`

```python
@dataclass(frozen=True)
class OracleAttemptEvidence:
    profile_version: str
    terminal_stage: OracleStage
    logical_model: str
    observed_model_label: str | None
    model_verified: bool | None
    attachment_mode: Literal["direct", "inline", "none"]
    prompt_submitted: bool | None
    response_completed: bool | None
    artifact_state: Literal[
        "none",
        "pending",
        "downloaded",
        "snapshotted",
        "invalid",
    ]
    failure_class: OracleFailureClass | None
```

Canonical field setを増減しない。

#### Constructor invariants

* `profile_version`はexact normalized version。
* `logical_model`は空でない。
* `observed_model_label`はinternal evidenceでありpublic serialization対象外。
* Optional booleanへ`0`、`1`、stringを受け入れない。
* `prompt_submitted is False or None`なら:

  * `response_completed is True`を禁止。
  * `artifact_state`は`downloaded`／`snapshotted`にできない。
* `response_completed is True`なら`prompt_submitted is True`。
* `artifact_state in {"pending", "downloaded", "snapshotted", "invalid"}`なら`prompt_submitted is True`。
* `artifact_state in {"downloaded", "snapshotted", "invalid"}`なら`response_completed is True`。
* `failure_class is None`で`RecoveryAction.ACCEPT`可能なのは:

  * `prompt_submitted is True`
  * `response_completed is True`
  * `artifact_state in {"downloaded", "snapshotted"}`
* `SUBMISSION_STATE_UNKNOWN`では`prompt_submitted is None`。
* `MODEL_SELECTION_UNAVAILABLE`、`ATTACHMENT_SUBMISSION_FAILED`、`PROMPT_RECONSTRUCTION_MISMATCH`では`prompt_submitted is False`。
* `GENERATION_INCOMPLETE`では:

  * `prompt_submitted is True`
  * `response_completed is not True`
* `OUTPUT_DOWNLOAD_FAILED`では:

  * `prompt_submitted is True`
  * `response_completed is True`
  * `artifact_state == "pending"`
* `SESSION_RECOVERY_REQUIRED`はpost-submit recovery infrastructure failureに限定する。
* `ARTIFACT_VALIDATION_FAILED`では`artifact_state == "invalid"`。
* 矛盾するevidenceはconstructorで拒否し、recovery actionを生成しない。

### 4.4 `RecoveryAction`

```python
class RecoveryAction(str, Enum):
    BLOCK = "block"
    NEW_EXECUTION_SAME_MODEL = "new_execution_same_model"
    NEW_EXECUTION_INLINE = "new_execution_inline"
    SAME_SESSION_HARVEST = "same_session_harvest"
    SAME_SESSION_CAPTURE = "same_session_capture"
    ACCEPT = "accept"
```

Canonical designと同じ値を使う。

### 4.5 `RecoveryBudget`

```python
@dataclass(frozen=True)
class RecoveryBudget:
    automatic_new_executions_remaining: int = 1
    same_session_harvest_remaining: int = 1
    same_session_capture_remaining: int = 1
```

Invariants:

* 各fieldはexact `int`。`bool`禁止。
* 許可値は`0`または`1`だけ。
* Negative、2以上、resetは禁止。
* Model retryとinline retryは、同じ`automatic_new_executions_remaining`を消費する。
* Harvestとcaptureは別budgetだが各最大1。
* Budget消費は元objectを変更せず、新しい`RecoveryBudget`を返すpure helperで行う。
* `successful_submission_count`はbudgetへ追加しない。Invocation control flow内のlocal integerとして最大1を構造的に保証する。

---

## 5. Pure decision engine

Domainへ次のpure functionを置く。

```python
def decide_oracle_recovery(
    evidence: OracleAttemptEvidence,
    budget: RecoveryBudget,
    *,
    inline_mode_characterized: bool,
) -> RecoveryAction:
    ...
```

### 5.1 優先規則

1. `prompt_submitted is None`

   * 常に`BLOCK`
   * Harvest／capture禁止
   * New execution禁止
   * Public pairは`blocked / oracle_capability_unsupported`

2. `prompt_submitted is False`

   * Harvest／capture禁止
   * `MODEL_SELECTION_UNAVAILABLE`

     * new-execution budget=`1` → `NEW_EXECUTION_SAME_MODEL`
     * budget=`0` → `BLOCK`
   * `ATTACHMENT_SUBMISSION_FAILED`

     * initial mode=`direct`
     * `inline_mode_characterized is True`
     * new-execution budget=`1`
     * 上記すべて成立 → `NEW_EXECUTION_INLINE`
     * それ以外 → `BLOCK`
   * `PROMPT_RECONSTRUCTION_MISMATCH`

     * 常に`BLOCK`
     * Retry 0
   * Profile／capability／runtime failure

     * `BLOCK`
   * Artifact／generation系classとの組合せ

     * Invalid evidenceとしてconstructor rejection

3. `prompt_submitted is True`

   * New execution actionを絶対に返さない。
   * `GENERATION_INCOMPLETE`

     * harvest budget=`1` → `SAME_SESSION_HARVEST`
     * harvest budget=`0` → `BLOCK`
   * `OUTPUT_DOWNLOAD_FAILED`

     * capture budget=`1` → `SAME_SESSION_CAPTURE`
     * capture budget=`0` → `BLOCK`
   * Artifact missing／ambiguous／invalid

     * `BLOCK`。Public statusはtyped mapperにより`rejected`
   * Safe downloaded／snapshotted output、failureなし

     * `ACCEPT`

4. Unknown enum／unknown object

   * Default actionなし。
   * `assert_never()`またはexplicit type rejection。
   * `BLOCK`へのgeneric fallback禁止。

### 5.2 Successful submission invariant

Infra control flowは次の構造にする。

```text
initial execution
  ├─ submitted=false + permitted pre-submit action
  │    └─ one new execution
  ├─ submitted=None
  │    └─ block
  └─ submitted=true
       └─ post-submit path only
```

* Initial executionとone pre-submit retryの合計は最大2。
* 最初のexecutionが`prompt_submitted=True`になった時点でnew-execution code pathを破棄する。
* 二回目のexecutionが`prompt_submitted=True`ならsuccessful submission countは1。
* 二回のsuccessful submissionを表現するcontrol-flow edgeを作らない。
* `while True`、再帰retry、汎用retry utilityを使わない。

---

## 6. Authoritative public status／reason mapping

Domainへ一つのclosed mapperを置く。

```python
def oracle_public_outcome(
    failure_class: OracleFailureClass,
) -> tuple[Literal["blocked", "rejected"], OraclePublicReason]:
    ...
```

`dict.get(default)`やgeneric catch-allを使わず、closed `match`と`assert_never()`で実装する。

| Internal failure class           | Public status | Public reason                           |
| -------------------------------- | ------------- | --------------------------------------- |
| `EXECUTABLE_UNAVAILABLE`         | `blocked`     | `oracle_unavailable`                    |
| `MANAGED_CHROME_UNAVAILABLE`     | `blocked`     | `oracle_unavailable`                    |
| `PROFILE_UNSUPPORTED`            | `blocked`     | `oracle_capability_unsupported`         |
| `CAPABILITY_MISSING`             | `blocked`     | `oracle_capability_unsupported`         |
| `SUBMISSION_STATE_UNKNOWN`       | `blocked`     | `oracle_capability_unsupported`         |
| `PROFILE_BUILDER_MISSING`        | `blocked`     | `oracle_capability_unsupported`         |
| `MODEL_SELECTION_UNAVAILABLE`    | `blocked`     | `oracle_model_selection_unavailable`    |
| `ATTACHMENT_SUBMISSION_FAILED`   | `blocked`     | `oracle_attachment_submission_failed`   |
| `PROMPT_RECONSTRUCTION_MISMATCH` | `blocked`     | `oracle_prompt_reconstruction_mismatch` |
| `GENERATION_INCOMPLETE`          | `blocked`     | `oracle_generation_incomplete`          |
| `SESSION_RECOVERY_REQUIRED`      | `blocked`     | `oracle_session_recovery_required`      |
| `OUTPUT_DOWNLOAD_FAILED`         | `blocked`     | `oracle_output_download_failed`         |
| `ARTIFACT_MISSING`               | `rejected`    | `oracle_artifact_missing`               |
| `ARTIFACT_AMBIGUOUS`             | `rejected`    | `oracle_artifact_ambiguous`             |
| `ARTIFACT_VALIDATION_FAILED`     | `rejected`    | `oracle_artifact_rejected`              |

このmappingはcanonical plan §14.2のauthoritative tableである。Five stage-specific classesを別reasonへ潰してはならず、many-to-oneはruntime unavailable、capability/profile、artifact validationの三familyだけに限定される。

### 6.1 Five new public reasons

追加するexact strings:

```text
oracle_model_selection_unavailable
oracle_attachment_submission_failed
oracle_prompt_reconstruction_mismatch
oracle_generation_incomplete
oracle_output_download_failed
```

維持するexisting reasons:

```text
oracle_unavailable
oracle_capability_unsupported
oracle_session_recovery_required
oracle_artifact_missing
oracle_artifact_ambiguous
oracle_artifact_rejected
```

### 6.2 Domain constructor enforcement

`PlanningInvocationResult`:

* Five new reasonsをallowed setへ追加。
* すべての`oracle_*` reasonについてexact status pairを検査。
* Unknown `oracle_*` reasonを拒否。
* `pass / transport_received`を維持。
* Detailed `OracleAttemptEvidence`を`to_dict()`へ含めない。

`PlanningCommandResult`:

* Existing non-Oracle command reasonsは維持。
* `reason.startswith("oracle_")`の場合、exact Oracle pairだけを許可。
* Unknown Oracle reason、wrong status pairをconstructorで拒否。
* Applicationから受け取ったpairを別reasonへ変換しない。

Application:

* Transport failureを一つのhelperから`PlanningCommandResult`へ投影する。
* `status`／`reason`をそのまま保持する。
* Oracle internal classをapplicationで再分類しない。
* `details`は空またはclosed content-free tokenだけにする。

CLI:

* Production rendererは変更しない。
* Text／JSON testsで同じexact pairをassertする。
* Retry mode、failure class、raw evidenceをCLI option／outputへ追加しない。

---

## 7. Infra orchestration設計

実装場所:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
infra/issue_planning_chatgpt.py
```

### 7.1 Profile-owned direct／inline argv

Generic adapterが`--browser-attachments`値を差し替えてはならない。

Private profile builderを次のmode-aware contractへ拡張する。

```python
BrowserAttachmentMode = Literal["direct", "inline", "none"]

BrowserArgvBuilder = Callable[
    [Path, tuple[str, int], str, str, tuple[Path, ...], BrowserAttachmentMode],
    list[str],
]
```

Profile-specific behavior:

| Profile  | `direct`                               | `inline`                                          |
| -------- | -------------------------------------- | ------------------------------------------------- |
| `0.16.1` | 現行exact argv                           | unsupported。呼出し前にblock                            |
| `0.17.0` | 現行exact `--browser-attachments always` | characterized exact `--browser-attachments never` |

Invariants:

* Model retryでは、model、strategy、prompt、attachment paths、modeを変更しない。
* Inline retryでは、model、strategy、prompt、original pathsを変更せず、profile-owned modeだけを`inline`へする。
* New executionでは新しいsession slugを使う。
* Original path orderを維持する。
* File／directoryをopen、stat、classify、copy、ZIP、filterしない。
* Required attachmentを`none`へ落とさない。
* Third executionを作らない。

### 7.2 Attempt executionとpost-submit recoveryを分離する

推奨private structure:

```python
def _run_new_oracle_execution(...) -> _DecodedAttempt:
    ...

def _run_pre_submit_attempts(...) -> _DecodedAttempt:
    ...

def _run_post_submit_recovery(...) -> _DecodedAttempt:
    ...
```

`_run_pre_submit_attempts`だけがbrowser new executionを作成できる。

`_run_post_submit_recovery`は次のcallableを受け取らない。

* Browser argv builder
* New session ID factory
* New execution runner

これによりpost-submitからnew execution APIへ到達できないことを構造的に保証する。

### 7.3 Bounded control flow

```text
budget = RecoveryBudget()
successful_submissions = 0

attempt 1
  decode evidence
  decide

if NEW_EXECUTION_*:
  consume shared new-execution budget
  attempt 2
  decode evidence
  decide

if prompt_submitted=True:
  successful_submissions += 1
  enter post-submit recovery

if SAME_SESSION_HARVEST:
  consume harvest budget
  invoke exact selected-profile harvest argv once
  decode same session again

if SAME_SESSION_CAPTURE:
  consume capture budget
  invoke exact selected-profile capture argv once
  decode same session again

ACCEPT:
  run existing typed artifact collection

BLOCK:
  use closed public mapper
```

Harvest後のevidenceがresponse-complete／artifact-pendingなら、同じpost-submit path内でcaptureへ一度進める。Harvestまたはcaptureを再度呼ぶloopは作らない。

### 7.4 Builder invocation guards

Builderを呼ぶ直前に、次を同一branch内でassertする。

```text
evidence.prompt_submitted is True
selected profile is exact
builder is callable
budget remaining == 1
Oracle executable identity unchanged
session ID unchanged
```

`prompt_submitted is False or None`では、次の全call countを0にする。

```text
harvest_argv_builder
capture_argv_builder
harvest subprocess
capture subprocess
same-session poll
```

Pre-submit cleanup例外を作らない。

---

## 8. 実装前に確認する一点

### Exact profile-private attempt-evidence source

S10 production integration前に、**Oracle `0.17.0`のstructured attempt evidenceをどのexact file／receipt／fieldから読むかを一つのversion-bound fixtureとして確認すること**。

必要なfield:

```text
promptSubmitted
model selection outcome / verified state
attachment preparation or submission failure
prompt reconstruction outcome
response completed
artifact pending / downloaded state
```

現行SpecDock adapterはprocess exit codeと`meta.json.status`／artifact inventoryしか読んでいない。S09 receiptは`promptSubmitted=true`とmodel-selection evidenceがbrowser runtime receiptへ記録されたことを示すが、current adapterが安全に読むexact path／closed schemaは実装されていない。また独立したartifact-pending stateもS09では実測されていない。

したがって:

* Structured fixture／schemaが現行Oracle 0.17.0 contractから確認できる場合だけdecoderを実装する。
* Stdout／stderrの自然言語substringからfailure classを推測しない。
* Process return codeだけから`prompt_submitted=False`を推測しない。
* Missing fieldをFalseへ変換しない。
* Artifact-pendingをartifact absenceから推測しない。
* S09のtext-only inline evidenceを任意file／directoryへ一般化しない。
* Inline eligibilityをsuffix、MIME、content scanで判定しない。

Exact structured evidenceまたはprofile-private inline eligibilityを確認できない場合、S10 production integrationを停止し、`blocked / oracle_capability_unsupported`とevidence gapをreportへ記録する。Decision types、pure mapper、unit testsだけを完了してもS10 closureを主張しない。

---

## 9. ファイルallowlist

### 9.1 Production write allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
domain/issue_planning_contracts.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
infra/issue_planning_chatgpt.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
application/issue_planning.py
```

### 9.2 Test write allowlist

```text
tests/unit/domain/test_issue_planning_contracts.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/application/test_issue_planning.py
tests/unit/commands/test_issue_planning.py
tests/cli_runtime/test_chatgpt_cli.py
```

### 9.3 Evidence allowlist

```text
spec-dock/.../iss-00354-define-chatgpt-context-and-attachment-contract/
report.md

spec-dock/.../iss-00354-define-chatgpt-context-and-attachment-contract/
artifacts/implementation-briefs/s10-stage-recovery-taxonomy.md
```

### 9.4 Read／run-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
infra/issue_planning_oracle_artifact.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
application/ports.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
commands/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
presentation/issue_planning.py

src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
cli/bootstrap.py

tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/integration/test_issue_planning_e2e.py
```

Command／presentationは既にtyped resultをそのままserializeするため、S10ではproduction変更不要である。Commands testsとCLI runtime testsでexact pairを固定する。

Read-only pathの変更が必要になった場合はallowlistを黙示拡張せず停止する。

---

## 10. 実装手順

### Step 1 — Red: domain typesとinvalid-state tests

先に次をfailureさせる。

* Closed `OracleFailureClass`不存在。
* `OracleAttemptEvidence`矛盾状態が受理される。
* Budget negative／2以上／boolが受理される。
* Unknown Oracle public reasonが受理される。
* Wrong status/reason pairが受理される。
* Unknown internal classがdefault mappingされる。

### Step 2 — Green: domain contract

* `OracleStage`
* `OracleFailureClass`
* `OracleAttemptEvidence`
* `RecoveryAction`
* `RecoveryBudget`
* `decide_oracle_recovery`
* Budget consume helper
* `oracle_public_outcome`
* Five new reasons
* Exact Oracle pair enforcement

を追加する。

### Step 3 — Red: decision table

Canonical cross-productをtable-driven testとして追加する。

* 全`OracleFailureClass`
* `prompt_submitted=False`
* `prompt_submitted=None`
* budget 0／1
* inline characterized false／true

最低assertion:

```text
prompt_submitted False/None
  -> harvest builder 0
  -> capture builder 0
```

### Step 4 — Green: pure decision engine

Infra subprocessを呼ばないpure functionとして実装する。

### Step 5 — Red: bounded invocation spies

Existing stage-blind testsをS10 expectationへ更新する。

* Timeoutだけではharvestしない。
* Nonzeroだけではharvestしない。
* Session nonterminalだけではharvestしない。
* Decoder evidenceが`prompt_submitted=True`かつgeneration incompleteの場合だけharvestする。
* Model／attachment pre-submit failureだけが一度のnew executionへ進む。
* Reconstruction mismatchはretryしない。

### Step 6 — Green: bounded infra orchestration

* Initial + optional one pre-submit execution。
* Shared overall new-execution budget。
* Successful submission最大1。
* Separate post-submit function。
* Exact harvest／capture builder invocation。
* Closed public mapper。

### Step 7 — Red／Green: application projection

* Transportのexact pairをCommand resultへ変更なしで投影。
* Unknown Oracle pairを拒否。
* Applicationによるgeneric reason変換なし。
* Thread publication receiptはsuccessful submission一件だけを要求する既存契約を維持する。Current applicationは一つのpublishable receiptだけを許可している。

### Step 8 — Red／Green: CLI serialization

五つの新reasonについてtext／JSON双方でexact pairとexit code `1`をassertする。

### Step 9 — S09 regression

* Exact 0.16.1／0.17.0 profile registry。
* Direct argv。
* Same-session argv。
* Unknown version fail-closed。
* 0.17 reader／mixed inventory。
* Reviewer pre-submit block。

を再実行する。

### Step 10 — Evidence update

実装・検証後にのみreportへcontent-free evidenceを追加し、fresh Red reviewへ渡す。

---

## 11. Red→Greenテスト表

### 11.1 Decision／call-count matrix

| Scenario                                                           | New execution | Successful submission | Harvest builder/subprocess | Capture builder/subprocess | Expected public pair                              |
| ------------------------------------------------------------------ | ------------: | --------------------: | -------------------------: | -------------------------: | ------------------------------------------------- |
| Unknown profile                                                    |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_capability_unsupported`         |
| Required capability missing                                        |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_capability_unsupported`         |
| Required profile builder missing                                   |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_capability_unsupported`         |
| Any failure + `prompt_submitted=None`                              |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_capability_unsupported`         |
| Executable unavailable                                             |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_unavailable`                    |
| Managed Chrome unavailable                                         |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_unavailable`                    |
| Model failure、submitted=false、budget=1                             |             1 |                 0または1 |                      0 / 0 |                      0 / 0 | retry result                                      |
| Model failure after shared budget exhausted                        |           0追加 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_model_selection_unavailable`    |
| Direct attachment failure、submitted=false、inline eligible、budget=1 |      1 inline |                 0または1 |                      0 / 0 |                      0 / 0 | retry result                                      |
| Attachment failure、inline unavailable／budget=0                     |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_attachment_submission_failed`   |
| Model retry consumes budget、second attempt attachment failure      |       total 1 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_attachment_submission_failed`   |
| Reconstruction mismatch、submitted=false                            |             0 |                     0 |                      0 / 0 |                      0 / 0 | `blocked / oracle_prompt_reconstruction_mismatch` |
| Submitted=true、response incomplete、harvest budget=1                |             0 |                     1 |                      1 / 1 |                      0 / 0 | recovered result                                  |
| Submitted=true、still incomplete after harvest                      |             0 |                     1 |                total 1 / 1 |                      0 / 0 | `blocked / oracle_generation_incomplete`          |
| Submitted=true、response complete、artifact pending、capture budget=1 |             0 |                     1 |                      0 / 0 |                      1 / 1 | recovered result                                  |
| Still pending after capture                                        |             0 |                     1 |                      0 / 0 |                total 1 / 1 | `blocked / oracle_output_download_failed`         |
| Recovery executable identity changed                               |             0 |                     1 |   builder 0 / subprocess 0 |   builder 0 / subprocess 0 | `blocked / oracle_session_recovery_required`      |
| Expected artifact absent after terminal capture                    |             0 |                     1 |                    ≤1 / ≤1 |                    ≤1 / ≤1 | `rejected / oracle_artifact_missing`              |
| Multiple candidate artifacts                                       |             0 |                     1 |                    ≤1 / ≤1 |                    ≤1 / ≤1 | `rejected / oracle_artifact_ambiguous`            |
| Path／mode／size／SHA／ZIP／JSON defect                                 |             0 |                     1 |                    ≤1 / ≤1 |                    ≤1 / ≤1 | `rejected / oracle_artifact_rejected`             |
| Valid downloaded artifact                                          |             0 |                     1 |                      0または1 |                      0または1 | `pass / transport_received`                       |

### 11.2 Exact argv assertions

#### Model retry

二つのbrowser argvはsession slug以外について同一である。

```text
same executable
same engine
same logical model
same strategy
same managed Chrome
same cookie policy
same prompt bytes
same attachment mode
same original path operands/order
different session slug
```

#### 0.17 inline retry

Second execution:

```text
--model gpt-5.6
--browser-model-strategy select
--browser-attachments never
same exact --prompt
same exact repeated --file operands
new session slug
```

Generic codeが`always`を`never`へ文字列置換しない。0.17 profile builderのexact outputをassertする。

#### Same-session harvest／capture

```text
<exact selected executable>
session
<same submitted session ID>
--harvest
--no-recover
```

* 0.16.1 builder regression。
* 0.17.0 harvest／capture builder identity。
* Harvest actionはharvest fieldだけを呼ぶ。
* Capture actionはcapture fieldだけを呼ぶ。
* Generic adapter内でliteral commandを再構築しない。

### 11.3 Cross-product invariant

全failure classについて、次の両値をparameterizeする。

```text
prompt_submitted=False
prompt_submitted=None
```

必須assertion:

```text
harvest_argv_builder calls == 0
capture_argv_builder calls == 0
same-session subprocess calls == 0
same-session poll calls == 0
```

---

## 12. Public contract tests

### Domain

* Five new exact reasonsを正しいstatusでaccept。
* Wrong statusでreject。
* Unknown`oracle_*` reasonをreject。
* Existing Oracle reasonsを維持。
* Non-Oracle command reasonsを不必要に閉じない。
* Mapper全enum member coverage。
* Fake／unknown memberにdefault mappingなし。

### Application

Planning create／review／reviseそれぞれについて、backendが次を返すfixtureを作る。

```text
blocked / oracle_model_selection_unavailable
blocked / oracle_attachment_submission_failed
blocked / oracle_prompt_reconstruction_mismatch
blocked / oracle_generation_incomplete
blocked / oracle_output_download_failed
rejected / oracle_artifact_missing
rejected / oracle_artifact_ambiguous
rejected / oracle_artifact_rejected
```

Command resultが同じpairを返すことをassertする。

### Commands／CLI

Text:

```text
status: blocked
reason: oracle_model_selection_unavailable
```

JSON:

```json
{"status":"blocked","reason":"oracle_model_selection_unavailable", ...}
```

* Both exit code `1`。
* Raw diagnostic、prompt、URL、session handle、model labelなし。
* CLI option追加なし。

---

## 13. Public data safety

`OracleAttemptEvidence`はpublic `to_dict()`へ直接入れない。

Publicに許容するもの:

* Exact `status`
* Exact content-free `reason`
* Existing backend exit code
* Existing response size／SHA
* 必要な場合のclosed terminal stage enum
* Report evidenceにおけるcontent-free call counts

Publicに含めないもの:

* Raw stdout／stderr
* Exception message
* Prompt text／digest以外のprompt content
* Target URL
* Conversation／session handle
* Chrome target ID／profile path
* Raw artifact path
* Transcript
* UI error text
* Oracle config
* Unverified model label
* Attachment content
* Detailed attempt object

`details`を使う場合は、closed allowlistのcontent-free categoryだけを許可する。Oracle stderrやexception stringを追加しない。

---

## 14. Verification commands

### 14.1 Domain contract

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py -q
```

### 14.2 Canonical S10 focused suite

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py -q
```

このcommandはcanonical plan §14.5のfocused verificationである。

### 14.3 S09 reader regression

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py -q
```

### 14.4 Focused taxonomy selection

```bash
uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  -k 'oracle and (attempt or failure or recovery or reason or submission)' -q
```

### 14.5 Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
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

### 14.6 Hardcoded recovery audit

```bash
rg -n \
  '"session"|--harvest|--no-recover' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

Expected:

* Tokensはexact profile builder definitionsだけ。
* Generic decision／recovery code内のassemblyは0。

### 14.7 Retry-loop audit

```bash
rg -n \
  'while True|retry|new_execution|harvest_argv_builder|capture_argv_builder' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

Manual assertion:

* New execution上限が静的に2。
* Generic unbounded loopなし。
* Harvest／capture各最大1。
* Pre-submit same-session callなし。

### 14.8 Scope audit

```bash
git diff --name-only \
  4ff7f8528e714c6a4523f7e92b1d5c4d216d5099...HEAD
```

Allowlist外pathがあれば停止する。

---

## 15. `report.md`へ記録する証跡

実装後にのみ、次をcontent-freeで記録する。

### Identity

```text
source repository
named branch
source HEAD
resulting local HEAD
resulting pushed HEAD
ahead / behind
default fallback = 0
worktree clean
```

### S10 brief adoption

次のavailable EAL IDを使用する。競合がなければ:

```text
EAL-082 = S10 implementation brief adoption
```

### S10 implementation evidence

競合がなければ:

```text
EAL-083 = S10 implementation / verification / fresh-review handoff
```

記録内容:

* Changed files。
* Added types。
* Exact public mapping。
* New-execution max count。
* Successful submission max count。
* Harvest／capture call-count matrix。
* Exact profile argv assertions。
* Focused test results。
* Ruff／Mypy／validate／diff-check。
* S09 regression result。
* Wrapper／API／alternate backend／default branch usage 0。
* Raw diagnostic leakage test result。
* Unresolved attempt-evidence gapの有無。
* `closure_claim=none`
* `handoff_status=ready_for_fresh_review`

### 記録禁止

* Raw prompt
* Raw Oracle diagnostics
* Session handle
* Browser URL
* Private path
* Transcript
* Oracle config
* Attachment contents
* Unverified model claim

GPT-5.6 Luna／Reasoning Effort Maxは実行設定であり、wrapperがrequested／target／resolved／strategy／verifiedを実際に返した場合だけその観測値を記録する。

---

## 16. 停止条件

次のいずれかではS10を完了扱いせず停止する。

1. Named branchまたはsource HEADが固定identityと一致しない。
2. S09 exact profile、reader、builder、review evidenceの変更が必要になる。
3. Exact structured sourceから`prompt_submitted`をdecodeできない。
4. `prompt_submitted=None`をFalseとして扱う必要がある。
5. Model／attachment／reconstruction failureをraw text substringから分類する必要がある。
6. Text-only inline characterizationを任意file／directoryへ一般化する必要がある。
7. Inline eligibility判定のためpath suffix、MIME、file content、directory entriesを検査する必要がある。
8. Independent artifact-pending stateを推測する必要がある。
9. Output download recoveryのためartifact reader／validator緩和が必要になる。
10. Pre-submit harvest／capture cleanup例外が必要になる。
11. New executionを2回以上追加する必要がある。
12. Successful submissionが2回になり得る。
13. Post-submit codeからnew execution APIへ到達できる。
14. Unknown internal classへdefault mappingが必要になる。
15. Five stage-specific reasonsをgeneric reasonへ潰す必要がある。
16. New CLI option、backend selector、retry flagが必要になる。
17. Wrapper／API／alternate model／default branch fallbackが必要になる。
18. S11 live smokeまたはS12 reader behaviorを先取りする必要がある。
19. S09 regressionが失敗する。
20. Allowlist外のproduction／test変更が必要になる。
21. Raw diagnosticをpublic resultへ含めなければ判定できない。
22. Focused tests、Ruff、Mypy、validate、diff-checkのいずれかが失敗する。

停止時はcanonical mapperのcontent-free pairとevidence gapをreportへ記録し、推測で実装を続行しない。Canonical requirementも、`promptSubmitted`を判定できない場合やexact mappingを固定できない場合に停止することを求めている。

---

## 17. Fresh Red review handoff

Workerは次を出力する。

```text
source_identity
  repository
  named_branch
  source_head
  default_fallback=0

resulting_identity
  resulting_head
  pushed_head
  ahead=0
  behind=0
  clean=true

changed_files
  exact allowlisted paths

domain_contract
  OracleStage members
  OracleFailureClass members
  RecoveryAction members
  RecoveryBudget defaults/invariants
  OracleAttemptEvidence invariants

public_mapping
  every internal class
  exact status
  exact reason
  no_default=true

budget_evidence
  max_total_executions=2
  max_automatic_new_executions=1
  max_successful_submissions=1
  max_harvest=1
  max_capture=1
  shared_model_inline_budget=true

call_count_matrix
  prompt
  new_execution
  successful_submission
  harvest_builder
  harvest_subprocess
  capture_builder
  capture_subprocess

argv_evidence
  0.16.1 direct
  0.17.0 direct
  0.17.0 inline
  exact harvest
  exact capture

test_results
  domain
  focused_S10
  S09_regression
  command_CLI
  ruff
  mypy
  validate
  diff_check

privacy_audit
  raw_diagnostic_publication=0
  prompt_publication=0
  URL_handle_transcript_publication=0

unresolved_evidence
  none
  またはS10をblockするexact gap

closure_claim
  none

handoff_status
  ready_for_fresh_review
  またはblocked
```

Fresh Red reviewは、S09 Red v6とは別のfresh、read-only、defect-only threadで、S10 resulting pushed exact HEADを対象にする。

Fresh RedがP0/P1=`0`を確認するまで:

```text
S10 closure = pending
S11 start = prohibited
PR = not created
merge = not performed
Issue close / finish = not performed
```
