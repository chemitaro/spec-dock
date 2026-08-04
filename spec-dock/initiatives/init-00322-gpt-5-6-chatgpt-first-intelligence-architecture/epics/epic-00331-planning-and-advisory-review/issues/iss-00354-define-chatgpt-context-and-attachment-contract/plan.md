---
種別: 実装計画書（Issue）
ID: "iss-00354"
タイトル: "ChatGPT Context and Attachment Contract — Oracle 0.17.0 増分計画"
状態: "draft"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
依存: ["requirement.md", "design.md", "decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md"]
親: ["epic-00331", "init-00322"]
---

# iss-00354 ChatGPT Context and Attachment Contract 実装計画書

> **Candidate / evidence-only / unreviewed**  
> 本計画は `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` の未採用案である。repository mutation、Red Team判定、実装、test execution、commit、PR、mergeを
> このturnでは行っていない。

## 1. 実装方針

Issue #334で実装済みのIssue Planning lifecycleと、source HEADで既に計画されたIssue #354 S01–S08を保持する。
Oracle `0.17.0` 対応はS09以降へ追加し、既存処理をゼロから再実装しない。

- provider sourceを正本とする。
- current 0.16.1 behaviorをcharacterization testで保持した上でprofileへ抽出する。
- Option A / C、direct path、Blue continuity / fresh Red、typed outputを既存S01–S08どおり実装する。
- 0.17 version/config/stage/artifact contractをprofileへ局所化する。
- automatic retryはgeneric loopにせず、pre-submit new executionをoverall最大1、post-submitをsame-sessionだけにする。
- browser smokeはopt-in evidence laneとし、unit testsがundocumented Oracle field / flagを発明しない。
- capability gapではstopし、wrapper / API / alternate model / default branchへfallbackしない。

## 2. Status baseline

| Scope | Source HEAD時点の状態 | 本計画での扱い |
|---|---|---|
| Issue #334 create/review/revise/apply lifecycle | production codeとtestsが存在 | 実施済みbaselineとして保持 |
| PATH Oracle / managed Chrome / explicit model / one submit | production codeとtestsが存在 | regression保持 |
| Oracle 0.16.1 strict session artifact reader | production codeとtestsが存在 | profile化して保持 |
| Issue #354 requirement/design/plan/artifacts | prior Candidate内容がcommit済み | current sourceとして増分改訂 |
| Issue #354 S01–S08 implementation | reportに完了evidenceなし | planned / unverified。完了claimしない |
| Oracle 0.17 external wrapper observations | GitHub外のlocal evidence | test hypothesis / classification input |
| Direct PATH Oracle 0.17 compatibility | 未検証 | S09–S13のblocking evidence |

## 3. Source baseline

| 項目 | 値 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Branch comparison | exact HEADとidentical / ahead 0 / behind 0 |
| Default fallback | not used |
| Current supported Oracle constant | `0.16.1` |
| Current model argv | `--model Pro --browser-model-strategy select` |
| Current input transport | generated prompt-pack directory via one `--file` |
| Current recovery trigger | nonzero/timeoutまたはsession nonterminal。`promptSubmitted`を判定しないstage-blind trigger |
| Current recovery argv | generic adapterが`oracle session <id> --harvest --no-recover`をhardcode |
| Current output | typed authoring ZIP / Review JSON |

S09はこのstage-blind/hardcoded baselineを先にcharacterization testで固定し、その後profile-owned recoveryへ移行する。

## 4. 変更対象

### 4.1 Provider runtime

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`
- 必要な既存ports/bootstrap wiring。新generic backend abstractionは追加しない。

### 4.2 Resources / projection / docs

- Issue Planning operation resources / skill。
- Clarification resource convention（public command追加なし）。
- provider-installed-dogfood projection。
- workflow / authoring pack docs。
- parent Epicのconflicting input/session wording。
- Issue reportのDecision Ledger / Evidence Adoption Ledger。

### 4.3 Tests

- `tests/unit/application/test_issue_planning_prompt.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/infra/test_issue_planning_chatgpt.py`
- Oracle artifact readerのunit tests（existing fileまたはdedicated test module）。
- `tests/unit/commands/test_issue_planning.py`
- `tests/cli_runtime/test_chatgpt_cli.py`
- `tests/integration/test_issue_planning_e2e.py`
- provider / installed / dogfood parity tests。
- opt-in local browser smoke script / test marker。private evidenceをcommitしない。

## 5. Retained Milestone S01 — Capability characterization と regression boundary

**Status:** retained from prior plan; source HEADでcompletion evidenceなし。

### Red

- direct Oracle directory attachment exact syntax。
- static directory + dynamic file multiple path syntax。
- direct continuation interface。
- attachment failure exit/session/artifact behavior。
- personal wrapper/API invocation 0。
- unsupported capabilityでprompt submission 0。

### Green

- current `_ROOT_CAPABILITIES` / `_SESSION_CAPABILITIES`をactual interfaceに合わせる。
- application architectureを先行変更せずcapability receiptを作る。
- version / command surfaceだけをcontent-free report evidenceにする。

### Gate

directory、multiple path、continuationのいずれかがunsupportedならS02以降を押し切らない。

## 6. Retained Milestone S02 — Operation resources と minimal body

**Status:** retained / unverified complete。

### Red

- planning/review/revision bodyにidentity、authority、outputがある。
- detailed instructions、attachment SHA/inventory、fixed 13 headings / 4 diagramsがbodyにない。
- operationごとに`prompt.md`と`attachments/`が分離される。
- resource file増減でapplication registry変更不要。
- reviewer=fresh/read-only/defect-only。

### Green

- `resources/operations/{planning,review,revision}/`をself-containedにする。
- operation registryとdeterministic minimal body rendererを導入する。
- unknown operation fallbackを作らない。

## 7. Retained Milestone S03 — Input model をbytesからpathへ

**Status:** retained / unverified complete。

### Red

- synthesized contractがattachment bytes/classification/SHAを保持しない。
- nested/hidden/symlink/FIFOでもtree API 0。
- `rglob` / `iterdir` / `stat` / `resolve` / `read_bytes`をfailure spyにしてもargv assembly成功。
- operator path textが保持される。

### Green

- `attachment_paths`を導入する。
- input scanner / limits / materialization-only fieldsをproduction pathから除去する。
- source preflight stateとattachment transport stateを分離する。

## 8. Retained Milestone S04 — Direct Oracle attachment transport

**Status:** retained / unverified complete。

### Red

- static directoryとdynamic evidenceがoriginal `--file` operandsになる。
- input prompt-pack / `context-NNN.md` / manifest群を生成しない。
- tree API 0、copy/ZIP/exclusion/retry 0。
- managed Chrome/env/executable/output regressions pass。

### Green

- `_write_transport_pack`を削除する。
- pure argv builderでdirect pathsを追加する。
- output snapshot private stagingだけを残す。
- prompt submission one-shotを維持する。

## 9. Retained Milestone S05 — Orchestration / CLI cutover

**Status:** retained / unverified complete。

### Planning

- old `--context-manifest`をhelp/parserから削除する。
- optional repeatable directory-oriented pathをrequestへ渡す。
- exact pre/postflight、Candidate publication不変。

### Review

- fresh Red requestを強制する。
- Candidate ZIP original pathをcopy/renameしない。
- reviewed identity / closed JSON parser不変。

### Semantic Revision

- prior Candidate / exact Review / revision request original paths。
- selected P0/P1とpreserved assumptionsをminimal body identityにする。
- mechanical lane不変。

## 10. Retained Milestone S06 — Blue continuity / fresh Red

**Status:** retained / unverified complete。

### Red

- first planning starts Blue。
- exact identity/lineage revision continues Blue。
- review always fresh Red。
- source HEAD change invalidates Blue。
- handle unavailable + lineage exact -> complete input new Blue。
- lineage ambiguous -> backend invocation 0 / Human block。
- no handle/transcript public persistence。

### Green

- `ChatGptThreadPort` / private `BlueThreadBinding`を追加する。
- reviewはreusable bindingを残さない。
- same-invocation harvestとcross-operation continuityを分離する。

### Gate

direct continuation unsupportedならwrapperで補わず、capability gapをreportする。

## 11. Retained Milestone S07 — Projection / docs / parent consistency

**Status:** retained / unverified complete。

- providerを先に変更し、project projection mechanismでinstalled/dogfoodを再生成する。
- recursive byte parityを固定allowlistなしで検証する。
- Option A/C、directory input、Blue/Red、direct Oracle、normal failure、output safetyをskills/docsへ反映する。
- parent Epicはconflicting body/attachment/session wordingだけをscoped updateする。
- canonical adoptionはCandidate preservation、EAL、fresh review、Human gateを経る。

## 12. Retained Milestone S08 — Regression / quality / closure evidence

**Status:** retained / unverified complete。

### Focused suite

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py -q
```

### Static / repository gates

```bash
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

- no generated input pack / no tree inspection。
- output manifest / Candidate provenanceは残る。
- wrapper/API/default branch fallback 0。
- fresh Red reuse 0、private handle serialization 0。
- provider / dogfood parity。
- fresh code reviewはexact pushed HEADを対象とする。

## 13. Added Milestone S09 — Oracle 0.17.0 compatibility profile

**Depends on:** S01 baseline characterization。  
**Blocking:** yes。

### 13.1 Red — current stage-blind behaviorとhardcoded argvを固定

- current `0.16.1` exact version、help flags、artifact schema testsを保持する。
- nonzero/timeoutまたはsession nonterminalで、submission evidenceを判定せず`_recover_same_session`へ入る現行behaviorをfixture化する。
- current generic adapterが`oracle session <id> --harvest --no-recover`を直接組み立てることをcharacterization testで固定する。
- unknown `0.16.2` / `0.17.0`がprofile追加前にsubmission 0でblockすることを確認する。
- `SUPPORTED_ORACLE_VERSION`単一constantとhardcoded recovery argvの依存箇所をinventory化する。
- user configをtemporary HOMEで隔離しないtestを保持する。

### 13.2 Characterization — direct PATH Oracle 0.17.0

read-only / opt-in local runで次を取得する。

- `oracle --version` exact normalized output。
- root / session helpのrequired flags。
- browser argvのaccepted model / strategy / direct / inline attachment syntax。
- `inline_mode_characterized`をtrueにできるpositive/negative evidence。
- session directory、metadata、status、artifact inventoryのsanitized shape。
- prompt submission / response completion / model verifiedを判定できるevidence source。
- generation-incomplete用のexact same-session harvest command。
- response-complete / artifact-pending用のexact same-session capture command。
- harvestとcaptureが同一commandなら、その同一性をreceiptに明示する。

raw config、target URL、session handle、prompt、transcriptをcommitしない。fixtureはfield names / enums / booleans / dummy pathsへ
sanitizationし、実データhashを持ち込まない。

### 13.3 Green — profile ownershipへ移行

- `OracleCompatibilityProfile` registryに`inline_mode_characterized`、`harvest_argv_builder`、`capture_argv_builder`を追加する。
- current 0.16.1 hardcoded harvest argvをbehavior-preserving 0.16.1 profile builderへ抽出する。
- generic `issue_planning_chatgpt.py`から`session` / `--harvest` / `--no-recover`のrecovery argv assemblyを削除する。
- characterized 0.17.0 profile、stage decoder、harvest/capture builders、artifact readerを追加する。
- exact version + capability + decoder + builders bindingをpreflightする。
- unknown version / partial schema / required builder missingはfail-closed。

### 13.4 Verification

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run pytest tests/unit/infra -k 'oracle and (artifact or session or profile)' -q
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra tests/unit/infra
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra
```

Required assertions:

- 0.16.1 profile builder returns the former exact argv。
- 0.17 builders return only characterized fixture argv。
- generic adapter recovery path has no hardcoded session command tokens。
- profile missing inline declaration or required recovery builder blocks before prompt/recovery invocation。

### 13.5 Stop gate

submission state、model verified、artifact schema、inline capability、harvest command、capture commandのいずれかをsafeにcharacterize
できなければS10以降をproduction-enableしない。

## 14. Added Milestone S10 — Stage evidence / failure taxonomy / bounded recovery

**Depends on:** S09。  
**Blocking:** yes。

### 14.1 Red — invocation-level recovery boundary

Table-driven testsで次を固定する。

| Evidence | Expected action | Harvest builder | Capture builder |
|---|---|---:|---:|
| unknown profile | block / process 0 | 0 | 0 |
| any failure + `promptSubmitted=None` | capability unsupported | 0 | 0 |
| model failure + submitted=false + retryable | new execution 1 | 0 | 0 |
| model failure after budget used | block | 0 | 0 |
| direct attachment failure + submitted=false + inline characterized | inline new execution 1 | 0 | 0 |
| reconstruction mismatch + submitted=false | block / retry 0 | 0 | 0 |
| submitted=true + response incomplete | same-session harvest 1 | 1 exact profile argv | 0 |
| submitted=true + response complete + download pending | same-session capture 1 | 0 | 1 exact profile argv |
| artifact invalid | reject / regenerate 0 | 0 | 0 additional |

Cross-product testは全`OracleFailureClass`と`prompt_submitted=False|None`を組み合わせ、harvest/capture invocationが常に0であることを
assertする。pre-submit cleanup例外は作らない。

- model retryとinline retryが同じoverall budgetを共有する。
- successful submission最大1。
- pre-submit failureでBlue binding / Red stateをadvanceしない。
- generic adapterのhardcoded recovery argv invocation 0。
- content-free public resultにraw diagnosticsが出ない。

### 14.2 Red — authoritative public mapping

次の表をdomain constructor、application mapper、CLI serializationのexact expectationとする。

| Internal failure class | Public status | Public reason | Contract status |
|---|---|---|---|
| executable / managed Chrome unavailable | `blocked` | `oracle_unavailable` | existing reason retained |
| `profile_unsupported` / required capability missing / `prompt_submitted=unknown` / required profile builder missing | `blocked` | `oracle_capability_unsupported` | existing reason retained; allowed many-to-one capability family |
| `model_selection_unavailable` after the permitted retry is unavailable or exhausted | `blocked` | `oracle_model_selection_unavailable` | new public reason |
| `attachment_submission_failed` after the permitted inline path is unavailable or exhausted | `blocked` | `oracle_attachment_submission_failed` | new public reason |
| `prompt_reconstruction_mismatch` | `blocked` | `oracle_prompt_reconstruction_mismatch` | new public reason |
| `generation_incomplete` after one characterized same-session harvest | `blocked` | `oracle_generation_incomplete` | new public reason |
| characterized recovery command cannot be executed safely, or same-session state remains undecidable for infrastructure reasons | `blocked` | `oracle_session_recovery_required` | existing reason retained; not a known-stage catch-all |
| `output_download_failed` after one characterized same-session capture | `blocked` | `oracle_output_download_failed` | new public reason |
| expected artifact absent after terminal capture | `rejected` | `oracle_artifact_missing` | existing reason retained |
| multiple candidate artifacts | `rejected` | `oracle_artifact_ambiguous` | existing reason retained |
| path / mode / size / SHA / validation / ZIP / JSON defect | `rejected` | `oracle_artifact_rejected` | existing reason retained; allowed many-to-one validation family |

Test rules:

- five new reason stringsをexactにacceptする。
- existing reason stringsを維持する。
- stage-specific five classesは別reasonへmappingできない。
- many-to-oneはcapability/profile、runtime unavailable、artifact validationの三familyだけ。
- unknown internal classにdefault mappingを与えない。

### 14.3 Green

- `OracleAttemptEvidence`、`OracleFailureClass`、`RecoveryAction`、`RecoveryBudget`を追加する。
- decision engineをpure functionとして実装する。
- infra invocation loopは最大2 executions（initial + one pre-submit recovery）に静的上限を持つ。
- recovery builderは`prompt_submitted is True` guardの内側だけで呼ぶ。
- post-submit pathはnew execution APIへ到達できない構造にする。
- Design §15 / REQ-030のclosed mappingを一つのtyped mapperとして実装し、domain/CLIへ同じpairを投影する。
- `oracle_model_selection_unavailable`、`oracle_attachment_submission_failed`、`oracle_prompt_reconstruction_mismatch`、
  `oracle_generation_incomplete`、`oracle_output_download_failed`を新規public reasonとして追加する。
- `oracle_unavailable`、`oracle_capability_unsupported`、`oracle_session_recovery_required`、`oracle_artifact_*`を維持する。

### 14.4 Refactor

- private evidenceとpublic resultを型で分ける。
- UI diagnostic string matchingをgeneric applicationへ漏らさずprofile decoderへ閉じる。
- retry countとterminal stageをmetrics / report summaryへ出せるcontent-free shapeにする。
- public mapperにfallback/default branchを持たせない。

### 14.5 Verification

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py -q
```

Acceptance requires exact call counts、exact profile argv、exact status/reason pairsの全assertionがpassすること。

## 15. Added Milestone S11 — Prompt / model / attachment browser verification

**Depends on:** S09–S10とS02–S05のtarget input path。  
**Blocking:** yes。

### 15.1 Prompt synthesis tests

- short ASCII control。
- Japanese / Unicode / quote / backtick / shell-like literal。
- LF / trailing newline cases。
- representative Issue #354 Markdown brief。
- subprocess argv exact equality / shell false / one prompt。
- prompt digestがdirect / inline variationで同一。

### 15.2 Model evidence tests

- logical Pro requestがprofile argvへ変換される。
- observed label + verified flagがsame attemptへbindされる。
- unverified / empty labelはformal successにならない。
- `GPT-5.6 Sol`はexternal observation fixtureとしてだけ記録し、direct characterizationなしにaccepted constantにしない。
- `current` / alternate model fallback 0。

### 15.3 Attachment tests

- direct required path primary。
- direct failure fixtureからinline one-shot。
- same original paths、tree access/copy/archive 0。
- reconstruction mismatchからinlineへ遷移しない。
- no-attachmentはdiagnostic smokeだけでproduction required evidenceを削除しない。

### 15.4 Opt-in browser smoke matrix

1. clean managed Chrome stateを記録する。
2. short control prompt / no attachmentでbrowser readinessとmodel evidenceを確認する。
3. representative prompt / required direct attachmentsでsubmissionを確認する。
4. characterized direct attachment failure fixtureが得られる場合だけinline recoveryを確認する。
5. standard/project target kindをOracle-native configのcategoryとして別runで記録する。
6. successful responseからsmall file、次にauthoring ZIP captureを確認する。

各runは次だけをsanitized receiptとして残す。

```text
oracle_version, profile_id, target_kind, prompt_case_id,
logical_model, observed_model_label, model_verified,
attachment_mode, terminal_stage, prompt_submitted,
response_completed, artifact_state, failure_class, retry_count
```

### 15.5 Acceptance gate

representative prompt + required direct attachment + verified model + prompt submitted + response completed + artifact capturedが
一つのattempt lineageでpassしない限り0.17 formal compatibilityをPASSとしない。

## 16. Added Milestone S12 — Download / ZIP capture と versioned artifact reader

**Depends on:** S09–S11。  
**Blocking:** yes。

### 16.1 Red

- 0.17 completed session + valid ZIP fixture。
- response completed / submitted=true / artifact pending -> selected profile capture exact argv once。
- download failed after characterized capture -> `blocked` / `oracle_output_download_failed`、new execution 0。
- capture builder cannot be safely executed -> `blocked` / `oracle_session_recovery_required`。
- terminal capture succeeded but expected file absent -> `rejected` / `oracle_artifact_missing`。
- missing / ambiguous / wrong mode / wrong session / path escape / symlink / SHA mismatch / validation false。
- malformed/encrypted/unsupported compression/entry limits。
- Review transcript or 0.17 equivalent closed JSON extraction。
- 0.16.1 fixtureを0.17 readerへ、0.17 fixtureを0.16.1 readerへ渡すとreject。
- every fixture with submitted=false or unknown -> harvest/capture command count 0。

### 16.2 Green

- version-dispatched artifact readerを実装する。
- common safe file/ZIP primitivesはsemantic parityが確認できたものだけ共有する。
- `response_completed`と`artifact_downloaded`を別stateとしてdecodeする。
- captureはselected exact-version profileの`capture_argv_builder`だけを使う。
- generic adapterから0.16.1 hardcoded harvest/capture commandを完全に除去する。
- characterized capture後のterminal classをREQ-030 exact status/reasonへmappingする。
- typed output snapshot / Candidate publication pathは変更しない。

### 16.3 Verification

```bash
uv run pytest tests/unit/infra -k 'oracle and (artifact or download or session or profile)' -q
uv run pytest tests/integration/test_issue_planning_e2e.py -q
```

Invocation-level spiesでprofile builder以外のsession command 0、false/unknown recovery 0、post-submit exact builder 1を確認する。

## 17. Added Milestone S13 — Integration / projection / docs / closure

**Depends on:** S01–S12。  
**Blocking:** yes。

### 17.1 Integration

- planning direct 0.17 -> authoring ZIP。
- Candidate review -> fresh Red / closed JSON。
- failed Review -> verified Blue revision。
- pre-submit model/attachment recoveryはconversation stateをadvanceしない。
- post-submit timeout/downloadはsame-sessionで回収する。
- exact GitHub postflight、source stale、publication transaction不変。

### 17.2 Projection / docs

- provider first、installed/dogfood regenerate、recursive parity。
- skills/docsへprofile、stage reasons、one-shot inline、same-session boundary、withdrawal条件を反映する。
- parent EpicへOracle 0.17 implementation detailを広げず、direct Oracle / session wordingの矛盾だけを解消する。
- ADRはIssue/Initiative-local provisionalとして参照する。

### 17.3 Full quality gate

S08 focused / static suiteに加え:

```bash
uv run pytest tests/unit/infra -k oracle -q
uv run pytest tests/integration/test_issue_planning_e2e.py -q
./spec-dock/scripts/spec-dock validate
git diff --check
```

opt-in browser smokeのactual commandはrepository-owned scriptとしてdocumentし、CI defaultでprivate browserを要求しない。

### 17.4 Report evidence

- source/resulting HEAD。
- exact Oracle version/profile/capabilities。
- external wrapper observationは`external_local_observation`としてdirect evidenceと分離。
- stage matrix resultsとretry counts。
- model observed label / verified result。
- direct / inline / prompt reconstruction / download scenarios。
- artifact reader fixtures / test results。
- provider parity / regression / remaining gaps。
- Candidate / Review / Human authorityとno mutation。

### 17.5 Review / adoption

- implementation後のfresh code reviewはexact pushed HEADを対象にする。
- P0/P1をrepairし、new Candidate/review identityへbindする。
- PASSはHuman adoption / merge / Issue closeを意味しない。

## 18. Test matrix

| Requirement | Primary tests | Exact acceptance |
|---|---|---|
| REQ-021–023 | profile selection/help/config/builder boundary | inline declaration + harvest/capture builders complete or capability unsupported |
| REQ-024 | model policy/verified receipt | observed label + verified on same attempt |
| REQ-025 | prompt corpus/argv equality | representative reconstruction/submission |
| REQ-026 | direct/inline argv + no tree access | required direct; inline only classified false-submission failure |
| REQ-027 | failure-class × false/unknown cross-product | harvest/capture calls exactly 0 |
| REQ-028 | submit count / profile harvest spy | submitted=true only; exact profile argv once; generic hardcode 0 |
| REQ-029 | versioned reader/profile capture spy | response-complete delayed ZIP; exact profile capture once |
| REQ-030 | typed internal/public mapper + CLI/domain tests | every exact status/reason pair; only three allowed many-to-one families |
| REQ-031 | Blue/Red transaction tests | first successful submission semantics |
| REQ-032 | serialization/privacy tests | sanitized receipt only |
| REQ-033 | full unit/integration matrix | opt-in direct PATH Oracle smoke |

## 19. Migration order

1. Adopt/review this Candidate; do not modify canonical docs directly from Blue output。
2. Execute retained S01 capability gate against current and 0.17 environment。
3. Implement S02–S05 Option A/C input path。
4. Characterize current stage-blind recovery and extract its hardcoded argv into the 0.16.1 profile。
5. Remove generic hardcoded recovery argv and add characterized 0.17 inline/harvest/capture profile fields in S09。
6. Add S10 false/unknown recovery-zero boundary and closed public status/reason mapper before enabling any retry。
7. Complete S06 thread policy using successful-submission semantics。
8. Run S11 browser matrix。
9. Complete S12 profile-owned artifact reader/download capture。
10. Apply S07 docs/projection and S08 regressions as expanded by S13。
11. Fresh review / Human adoption / owning PR workflow。

parallel workはallowedだが、S09 builder evidenceとS10 exact mapping testsなしにS10/S11/S12 production enablementをmergeしない。

## 20. Rollback / withdrawal

- runtime内にautomatic 0.16.1 downgrade switchを入れない。
- 0.17 profileをwithdrawする場合、reviewed commit/deploymentでregistryから除きformal operationをblockする。
- Oracle binary versionを戻す運用はoperator decisionであり、SpecDockが別binary/pathを探索しない。
- Candidate / Review dataはsource identity付きevidenceとして保持するが、failed outputをadoptしない。
- rollback後もOption A/C、exact GitHub、output validation、Blue/Red、Human gateを維持する。

## 21. 実装中の停止条件

- requested branch / source baselineが変化し、rebase / adoption判断がない。
- task scope外worktree changeを隔離できない。
- 0.17 help / metadata / model / submission evidenceがambiguous。
- representative prompt mismatchが再現し、原因変更なしでretryだけ増やす必要がある。
- inlineがpath materialization / attachment dropを要求する。
- 0.17 harvest/capture commandをcharacterizeできない、generic hardcoded argvを除去できない、またはfalse/unknown recovery 0を保証できない。
- post-submit recoveryにnew executionが必要になる。
- REQ-030 exact mapping / new reasons / allowed many-to-one constraintsをdomain、application、CLI、testsで一致させられない。
- output validator、source gate、Human authorityを緩める必要がある。
- provider parity、focused tests、P0/P1 reviewが未解決。

## 22. Definition of Done

- canonical three docs + ADRがadopted and freshly reviewed。
- retained S01–S08とadded S09–S13のblocking gatesがpass。
- direct PATH Oracle 0.17 representative smokeがpass。
- model verified、prompt submitted、response completed、ZIP capturedがsame attempt lineageで証明される。
- current stage-blind/hardcoded recoveryがgeneric adapterから除去され、exact-version profile buildersへ移ったことをtestで証明する。
- every false/unknown submission path has harvest/capture invocation count 0。
- post-submit harvest/captureはcharacterized profile commandだけをexactly once実行する。
- REQ-030のexact status/reason pairs、新規reason、既存reason、many-to-one制約がdomain / CLI / testsで一致する。
- versioned readerとstrict output regressionがpass。
- provider/installed/dogfood、skills/docs/parent consistencyがpass。
- report EAL/Decision Ledger/closure evidenceが完了する。
- merge / Issue closeはowning workflowで明示判断される。
