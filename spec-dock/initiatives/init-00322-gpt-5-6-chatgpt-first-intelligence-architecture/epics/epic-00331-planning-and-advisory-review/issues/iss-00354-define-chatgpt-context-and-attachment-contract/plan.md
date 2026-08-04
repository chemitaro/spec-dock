---
種別: 実装計画書（Issue）
ID: "iss-00354"
タイトル: "ChatGPT Context and Attachment Contract — Oracle 0.17.0 増分計画"
状態: "approved"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
依存: ["requirement.md", "design.md", "decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md"]
親: ["epic-00331", "init-00322"]
---

# iss-00354 ChatGPT Context and Attachment Contract 実装計画書

> **Canonical / approved for Issue implementation preparation**
> 本計画は Candidate v2 の Red Team PASS と、S01〜S13 各マイルストーンの ChatGPT-Use 実装ブリーフ運用を統合した iss-00354 の正規実行計画である。
> 正規文書としての採用と実装実行可否は別であり、current exact-HEAD fresh review が FAIL の間は execution-ready としない。実装開始前に current HEAD、assurance、report のゲートを再確認し、各ステップのブリーフを生成する。実装、test execution、PR、merge、Issue close は未実施である。

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
| Historical Candidate source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Current canonical docs HEAD | `dba243168647902c8883c0a44ed58a89c754070b` |
| Branch comparison | current canonical HEADとGitHub branch tipがidentical / ahead 0 / behind 0 |
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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S01 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s01-capability-characterization.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S02 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s02-operation-resources.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S03 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s03-input-path-model.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S04 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s04-direct-attachment-transport.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S05 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s05-orchestration-cli-cutover.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S06 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s06-blue-red-continuity.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S07 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s07-projection-docs-consistency.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

- providerを先に変更し、project projection mechanismでinstalled/dogfoodを再生成する。
- recursive byte parityを固定allowlistなしで検証する。
- Option A/C、directory input、Blue/Red、direct Oracle、normal failure、output safetyをskills/docsへ反映する。
- parent Epicはconflicting body/attachment/session wordingだけをscoped updateする。
- canonical adoptionはCandidate preservation、EAL、fresh review、Human gateを経る。

## 12. Retained Milestone S08 — Regression / quality / closure evidence

**Status:** retained / unverified complete。

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S08 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s08-regression-quality-closure.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S09 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s09-oracle-017-profile.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S10 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s10-stage-recovery-taxonomy.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S11 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s11-browser-verification.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S12 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s12-artifact-reader.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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

- 実装開始前に ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で S13 専用の実装ブリーフを作成し、`artifacts/implementation-briefs/s13-integration-closure.md` に配置する。Codex はブリーフを参照して実装し、実測結果は `report.md` に記録する。

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
- 各マイルストーンの実装内容レビューはサブエージェントではなく ChatGPT-Use（GPT-5.6 Luna / Reasoning Effort Max）で実施し、指摘と採否を `report.md` に記録する。ChatGPT の出力だけで canonical adoption、assurance 更新、実装完了を主張しない。
- P0/P1をrepairし、new Candidate/review identityへbindする。
- PASSはHuman adoption / merge / Issue closeを意味しない。

## 17.6 実行可能ステップ契約（Executable Step Contract）

### 17.6.1 共通実行ルール

- 各ステップは一つずつ開始し、開始前に指定された ChatGPT-Use 実装ブリーフを作成する。
- ブリーフの出力先は当該 Issue の `artifacts/implementation-briefs/` direct child とし、ブリーフ本文は canonical requirement/design/plan を変更しない。
- runtime / CLI / infra / code / tests は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` を委任先とする。親 Codex は統合、証跡、ゲート判定を担当する。
- 許可パスは各カードに記載した対象とし、別 Issue、親 Epic の境界、Oracle wrapper 本体、秘密情報、private browser profile は変更しない。
- 各カードの具体テストケースは、前提、操作、期待結果、失敗検出、検証方法をすべて満たす。実装後の結果は `report.md` の Step Contract Closure と Test Contract Closure に記録する。

### 17.6.2 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | 対応要件 | 観測可能な受入条件 | 必須証跡 |
|---|---|---|---|---|
| `cl-s01-capability` | S01 | REQ-004–007, REQ-021–023, REQ-026 | 0.16.1 と 0.17.0 の capability 境界を実測し、未確定 capability では invocation しない | capability receipt、characterization test、report |
| `cl-s02-resources` | S02 | REQ-002, REQ-003, REQ-009, REQ-010 | operation resource の追加・削除が registry 変更なしで反映される | resource diff、unit test、report |
| `cl-s03-path-input` | S03 | REQ-004–007 | 入力は path のまま保持され、tree traversal と内容再構成を行わない | argv assertion、failure spy、report |
| `cl-s04-direct-transport` | S04 | REQ-004, REQ-006, REQ-007, REQ-016 | original path が Oracle argv に直接渡り、生成 pack が作られない | direct argv test、CLI test、report |
| `cl-s05-cli-cutover` | S05 | REQ-001, REQ-009, REQ-010, REQ-019 | planning/review/revision の parser と identity binding が新契約で一致する | command test、closed identity test、report |
| `cl-s06-blue-red` | S06 | REQ-011–014, REQ-031, REQ-032 | successful submission lineage を Blue に保持し、Red は fresh thread のみを使う | lineage test、privacy test、report |
| `cl-s07-projection` | S07 | REQ-018, REQ-020 | provider、installed、dogfood の docs/skill projection が一致する | parity check、docs diff、report |
| `cl-s08-regression` | S08 | REQ-017, REQ-033 | focused suite、static gate、validate が pass し、closure ledger が完成する | command output、report |
| `cl-s09-profile` | S09 | REQ-021, REQ-023 | versioned profile が capability と harvest/capture builder を所有する | profile tests、0.17 receipt、report |
| `cl-s10-recovery` | S10 | REQ-027, REQ-028, REQ-030 | false/unknown submission は recovery 0、post-submit は profile builder のみ一回 | table-driven tests、mapping tests、report |
| `cl-s11-browser` | S11 | REQ-024, REQ-025, REQ-026, REQ-033 | prompt、model、attachment、response、artifact の同一 lineage 証跡が得られる | sanitized smoke receipt、report |
| `cl-s12-artifact-reader` | S12 | REQ-029, REQ-030 | versioned reader が exact capture と strict artifact validation を行う | fixture tests、integration output、report |
| `cl-s13-closure` | S13 | REQ-018, REQ-020, REQ-031–033 | projection、docs、quality、review、adoption の最終ゲートが一致する | parity、quality commands、final report |

### 17.6.3 ステップ別実行カード

#### S01 — Capability characterization

- 振る舞いスライス: direct directory、multiple path、continuation の capability を現在の PATH Oracle で観測し、未対応 capability は停止する。
- delegation contract: delegated role=`dev-coder`; input docs=`requirement.md`, `design.md`, S01 brief, existing Oracle adapter/tests; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, `tests/unit/infra/`, `artifacts/implementation-briefs/s01-capability-characterization.md`; forbidden changes=application orchestration, generic recovery policy, Oracle wrapper, unrelated docs; acceptance criteria=`cl-s01-capability` receipt proves 0.16.1/0.17.0 capability boundary and unsupported invocation count 0; required verification=infra characterization unit test and recorded receipt; reviewer focus=`code-reviewer` checks capability boundary, argv, and no fallback; stop conditions=capability remains ambiguous or allowed-path expansion is required; output required=changed files, capability receipt, test result, risks, and report Ledger Note.
- 具体テストケース: `tc-s01-001` は capability が未対応の fixture を与えたとき prompt/recovery invocation が 0 になることを確認する。前提は fake Oracle と version receipt、操作は S01 characterization command、期待結果は capability receipt と blocked classification、失敗検出は未対応 capability の押し切り、検証方法は infra unit test と report command output。
- step closure contract: `cl-s01-capability` の receipt、test pass、ChatGPT-Use ブリーフ、report EAL を記録する。
- step gate / report destination: capability が安全に確定できなければ停止。`report.md` の Step Contract Closure、Test Contract Closure、Reviewer Gate Status に記録する。

#### S02 — Operation resources

- 振る舞いスライス: planning/review/revision の resource directory と minimal body を self-contained にする。
- delegation contract: primary delegated role=`dev-coder` for renderer/tests plus `doc-writer` subtask for shipped resources; input docs=S02 brief, `requirement.md`, `design.md`, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/`, and prompt renderer tests; allowed paths=`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `tests/unit/application/test_issue_planning_prompt.py`, and installed projection; forbidden changes=operation policy, Oracle transport, unrelated CLI; acceptance criteria=`cl-s02-resources` proves operation-specific resources drive a deterministic minimal body without registry edits; required verification=resource unit tests, renderer snapshot/byte diff, and docs projection check; reviewer focus=`code-reviewer` checks renderer/registry contract and `spec-reviewer` checks resource wording; stop conditions=registry code edit or missing operation resource; output required=resource diff, test result, rendered body sample, risks, and report Ledger Note.
- 具体テストケース: `tc-s02-001` は resource file を一つ増減しても registry のコード変更なしに renderer が deterministic body を出すことを確認する。前提は temp resource tree、操作は resource fixture の差し替え、期待結果は body identity が変わり必要 attachment 一覧だけが更新、失敗検出は未知 operation fallback、検証方法は application unit test と byte diff。
- step closure contract: resource diff、minimal body snapshot、fresh ChatGPT-Use brief review を記録する。
- step gate / report destination: unknown operation や registry edit が必要なら停止。docs/worker evidence と closure を `report.md` に記録する。

#### S03 — Path input model

- 振る舞いスライス: synthesized bytes/classification を path input に置換し、operator path text を保持する。
- delegation contract: delegated role=`dev-coder`; input docs=S03 brief, `requirement.md`, `design.md`, application contracts, scanner tests; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`, `tests/unit/application/test_issue_planning_prompt.py`, `tests/unit/domain/test_issue_planning_contracts.py`; forbidden changes=symlink/FIFO traversal, path materialization, new content hashing, transport adapter; acceptance criteria=`cl-s03-path-input` proves original paths and limits survive with zero tree/content inspection; required verification=unit tests with read/rglob/stat spies and argv assertions; reviewer focus=`code-reviewer` checks path-only contract and input immutability; stop conditions=any required materialization or new inspection rule; output required=contract diff, spy result, tests, risks, and report Ledger Note.
- 具体テストケース: `tc-s03-001` は nested/hidden/symlink/FIFO fixture に対して tree API spy が 0 のまま argv assembly が成功することを確認する。前提は path-only request、操作は synthesize request、期待結果は original paths と limits のみが保持される、失敗検出は read_bytes/rglob/stat の呼び出し、検証方法は unit test と spy assertion。
- step closure contract: input contract diff と spy pass を `cl-s03-path-input` に紐付ける。
- step gate / report destination: path materialization が必要になったら S03 を閉じず report から plan amendment へ戻す。

#### S04 — Direct attachment transport

- 振る舞いスライス: static directory と dynamic evidence を original `--file` operands として Oracle へ渡す。
- delegation contract: delegated role=`dev-coder`; input docs=S04 brief, `requirement.md`, `design.md`, Oracle transport adapter, CLI tests; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, `tests/unit/infra/test_issue_planning_chatgpt.py`, `tests/integration/test_issue_planning_chatgpt_transport.py`; forbidden changes=generated pack, copy, ZIP, exclusion, retry policy, Oracle wrapper; acceptance criteria=`cl-s04-direct-transport` proves original paths are direct `--file` operands and no generated input pack is created; required verification=argv equality test, no-tree spy, and transport CLI smoke; reviewer focus=`code-reviewer` checks direct Oracle boundary and one-shot semantics; stop conditions=direct capability unsupported or generated context appears; output required=adapter diff, argv receipt, tests, risks, and report Ledger Note.
- 具体テストケース: `tc-s04-001` は required direct path を渡したとき argv に同一 path が現れ、tree/copy/ZIP API が 0 であることを確認する。前提は static directory と dynamic evidence file、操作は direct command build、期待結果は one-shot submission argv、失敗検出は generated context file、検証方法は argv equality test と CLI smoke。
- step closure contract: direct argv、no-tree spy、CLI regression を `cl-s04-direct-transport` に紐付ける。
- step gate / report destination: direct capability が無ければ inline を勝手に追加せず S01 receipt を参照して停止する。

#### S05 — Orchestration / CLI cutover

- 振る舞いスライス: old manifest option を除去し、planning/review/revision の exact identity と output contract を維持する。
- delegation contract: delegated role=`dev-coder`; input docs=S05 brief, `requirement.md`, `design.md`, command contracts, CLI tests; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`, `tests/unit/commands/test_issue_planning.py`, `tests/unit/application/test_issue_planning.py`; forbidden changes=Candidate publication format, closed JSON parser, unrelated commands; acceptance criteria=`cl-s05-cli-cutover` proves planning/review/revision parser and exact branch/repository/HEAD identity binding; required verification=command unit tests and closed-identity test; reviewer focus=`code-reviewer` checks parser compatibility and publication transaction; stop conditions=identity mismatch, old option still accepted, or publication mutation; output required=command/application diff, tests, identity receipt, risks, and report Ledger Note.
- 具体テストケース: `tc-s05-001` は old option を拒否し、repeatable path option を同じ request identity へ渡すことを確認する。前提は parser fixture と exact branch identity、操作は planning/review/revision command、期待結果は deterministic request、失敗検出は candidate rename/copy、検証方法は command unit test。
- step closure contract: parser、identity、publication transaction の三点を pass にする。
- step gate / report destination: identity mismatch または publication mutation が検出されたら stop。report の implementation ledger に記録する。

#### S06 — Blue continuity / fresh Red

- 振る舞いスライス: successful submission semantics に基づく Blue lineage と fresh Red isolation を実装する。
- delegation contract: delegated role=`dev-coder`; input docs=S06 brief, `requirement.md`, `design.md`, thread ports, lineage tests; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`, `tests/unit/application/test_issue_planning.py`, `tests/unit/domain/`; forbidden changes=private handle/transcript public persistence, Red thread reuse, merge/close; acceptance criteria=`cl-s06-blue-red` proves successful-submission Blue continuity and fresh Red binding with no private evidence leakage; required verification=lineage transaction tests, privacy assertions, and unavailable handling test; reviewer focus=`code-reviewer` checks lifecycle isolation and `qa-reviewer` checks evidence boundary; stop conditions=continuation identity is ambiguous or Red binding can be reused; output required=lineage diff, receipt, tests, risks, and report Ledger Note.
- 具体テストケース: `tc-s06-001` は successful submission 後の revision が同一 Blue binding を使い、review invocation は新しい binding を作ることを確認する。前提は exact candidate identity、操作は revise then review、期待結果は Blue continuation と fresh Red、失敗検出は Red binding reuse、検証方法は transaction test と privacy assertion。
- step closure contract: source HEAD drift、ambiguous lineage、unavailable handling を pass にする。
- step gate / report destination: continuation capability が未対応なら wrapper fallback を作らず capability gap を report に記録する。

#### S07 — Projection / docs consistency

- 振る舞いスライス: provider source を更新し installed/dogfood projection と parent wording を一致させる。
- delegation contract: delegated role=`doc-writer`; input docs=S07 brief, `requirement.md`, `design.md`, provider assets, workflow/docs; allowed paths=`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/`, `src/spec_dock/assets/spec_dock/docs/`, `spec-dock/`, and the scoped parent Epic wording; forbidden changes=runtime code, unrelated Issue canonical docs, parent lifecycle state; acceptance criteria=`cl-s07-projection` proves provider/installed/dogfood byte parity and parent wording consistency; required verification=projection update, recursive parity check, and docs diff; reviewer focus=`spec-reviewer` checks requirement wording and `qa-reviewer` checks projection parity; stop conditions=parent boundary or generated projection source is ambiguous; output required=docs diff, parity receipt, tests/docs-only result, risks, and report Ledger Note.
- 具体テストケース: `tc-s07-001` は provider update 後に projection command を実行し、recursive byte parity が pass することを確認する。前提は clean projection baseline、操作は provider update、期待結果は allowlist なしの parity、失敗検出は provider/dogfood drift、検証方法は parity script と docs diff。
- step closure contract: docs impact S90 と provider parity receipt を記録する。
- step gate / report destination: parent boundaryが変わる場合は Epic planningへ戻す。

#### S08 — Regression / quality closure

- 振る舞いスライス: retained S01–S07 の focused suite、static gate、validate と closure ledger を確定する。
- delegation contract: delegated role=`dev-coder`; input docs=S08 brief, `requirement.md`, `design.md`, focused test list, quality commands; allowed paths=`tests/`, `report.md`, and step quality evidence; forbidden changes=production behavior, unrelated docs, merge/close; acceptance criteria=`cl-s08-regression` proves focused suite, static gate, validate, diff check, and closure ledger all pass on one HEAD; required verification=the plan-listed pytest/ruff/mypy/validate commands and report audit; reviewer focus=`qa-reviewer` checks coverage and `code-reviewer` checks no production drift; stop conditions=any quality gate fails or closure is stale; output required=command output, test summary, closure update, risks, and report Ledger Note.
- 具体テストケース: `tc-s08-001` は focused pytest、ruff、mypy、validate、diff check を同一 HEAD で実行する。前提は全 step closure が pass、操作は計画記載コマンド、期待結果は全 exit 0、失敗検出は stale projection/未記録 closure、検証方法は command output と report。
- step closure contract: `cl-s08-regression` と S99 input を記録する。
- step gate / report destination: いずれかの quality gate が fail なら commit candidate を作らず report を blocked にする。

#### S09 — Oracle 0.17 profile

- 振る舞いスライス: exact version/capability/profile-owned builders を追加し、0.16.1 の旧 argv を回帰保持する。
- delegation contract: delegated role=`dev-coder`; input docs=S09 brief, `requirement.md`, `design.md`, Oracle profile contracts, characterization receipt; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`, `tests/unit/infra/test_issue_planning_chatgpt.py`, `tests/unit/infra/test_issue_planning_oracle_artifact.py`; forbidden changes=generic backend abstraction, wrapper/API fallback, unrelated profiles; acceptance criteria=`cl-s09-profile` proves versioned profile owns capability and harvest/capture builders for 0.16.1 and characterized 0.17.0; required verification=profile tests, builder spy, ruff/mypy, and 0.17 receipt; reviewer focus=`code-reviewer` checks version locality and builder binding; stop conditions=help/metadata/model/capability remains ambiguous; output required=profile diff, receipt, tests, risks, and report Ledger Note.
- 具体テストケース: `tc-s09-001` は 0.16.1 fixture が旧 exact argv、0.17.0 fixture が characterized builders、unknown version が invocation 0 になることを確認する。前提は versioned fixture、操作は profile preflight、期待結果は exact builder binding、失敗検出は generic hardcode、検証方法は profile unit test。
- step closure contract: `cl-s09-profile` の receipt、builder spy、mypy/ruff を記録する。
- step gate / report destination: help/metadata/model/capabilityが曖昧なら S10 以降へ進まない。

#### S10 — Stage evidence / bounded recovery

- 振る舞いスライス: failure class と public reason mapping を pure decision engine で固定し、submission evidence に基づき回復を限定する。
- delegation contract: delegated role=`dev-coder`; input docs=S10 brief, `requirement.md`, `design.md`, failure taxonomy, domain/application/CLI contracts; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `tests/unit/domain/`, `tests/unit/application/`; forbidden changes=fallback/default mapping, post-submit new execution, unrelated recovery policy; acceptance criteria=`cl-s10-recovery` proves exact internal-to-public status/reason mapping and bounded call counts for false/unknown/submitted evidence; required verification=table-driven mapping tests, call-count assertions, public serialization test; reviewer focus=`code-reviewer` checks pure decision boundary and `qa-reviewer` checks failure matrix; stop conditions=exact mapping or recovery budget is ambiguous; output required=decision/mapping diff, matrix result, tests, risks, and report Ledger Note.
- 具体テストケース: `tc-s10-001` は全 failure class × `prompt_submitted=False|None` で harvest/capture 0、submitted true の incomplete/download pending で profile builder 一回を確認する。前提は table fixtures、操作は decision function、期待結果は exact status/reason pair、失敗検出は stage-blind retry、検証方法は table-driven unit test。
- step closure contract: `cl-s10-recovery` の call count、mapping、public serialization を記録する。
- step gate / report destination: exact mapping または recovery budget が崩れたら S11 を開始しない。

#### S11 — Prompt / model / attachment verification

- 振る舞いスライス: representative prompt、model evidence、direct/inline attachment、response completion を一つの attempt lineage で検証する。
- delegation contract: delegated role=`dev-coder`; input docs=S11 brief, `requirement.md`, `design.md`, prompt corpus, browser smoke matrix, sanitized receipts; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`, `tests/unit/application/`, and the opt-in smoke script; forbidden changes=private credentials, browser profile, raw transcript, unrelated Oracle wrapper; acceptance criteria=`cl-s11-browser` proves prompt, model evidence, direct/inline attachment, response, and artifact fields share one attempt lineage; required verification=receipt schema assertions and opt-in browser smoke with sanitized output; reviewer focus=`qa-reviewer` checks external evidence and `code-reviewer` checks prompt/attachment wiring; stop conditions=GPT-5.6 Luna/Max or attachment delivery is unverified; output required=sanitized receipt, test result, model evidence status, risks, and report Ledger Note.
- 具体テストケース: `tc-s11-001` は Japanese/Unicode prompt と required direct attachment で model verified、prompt submitted、response completed を同一 receipt に記録する。前提は managed Chrome、操作は opt-in smoke、期待結果は sanitized fields、失敗検出は unverified model/attachment drop、検証方法は receipt schema assertion。
- step closure contract: `cl-s11-browser` の external_local_observation と test result を report に記録する。
- step gate / report destination: GPT-5.6 Luna / Max が実測できない場合はその事実を記録し、未検証を成功扱いしない。

#### S12 — Download / ZIP artifact reader

- 振る舞いスライス: versioned reader で response complete と artifact downloaded を分離し、strict ZIP validation を通す。
- delegation contract: delegated role=`dev-coder`; input docs=S12 brief, `requirement.md`, `design.md`, artifact fixtures, reader contracts; allowed paths=`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`, `tests/unit/infra/`, `tests/integration/`; forbidden changes=generic hardcoded harvest/capture, unsafe extraction, automatic regeneration; acceptance criteria=`cl-s12-artifact-reader` proves response/download/capture separation, exact profile capture, and strict ZIP validation; required verification=0.16.1/0.17.0 fixture matrix, invocation spy, and integration output; reviewer focus=`code-reviewer` checks extraction safety and version binding; stop conditions=missing/ambiguous artifact or path escape; output required=reader diff, fixture results, integration output, risks, and report Ledger Note.
- 具体テストケース: `tc-s12-001` は submitted true/response complete/artifact pending で selected profile capture 一回、missing/ambiguous/path escape は rejected になることを確認する。前提は 0.16.1/0.17.0 fixture、操作は reader/capture、期待結果は exact reason、失敗検出は wrong-version acceptance、検証方法は fixture unit/integration test。
- step closure contract: `cl-s12-artifact-reader` の fixture matrix と invocation spy を記録する。
- step gate / report destination: expected artifact が不在または複数の場合は publication を行わず blocked/rejected evidence を残す。

#### S13 — Integration / projection / closure

- 振る舞いスライス: direct 0.17 planning、review/revision、projection、docs、quality、review/adoption の全体を current HEAD で閉じる。
- delegation contract: delegated roles=`dev-coder` plus `doc-writer`; input docs=S13 brief, `requirement.md`, `design.md`, S01–S12 closures, full quality commands; allowed paths=`tests/integration/`, provider/docs projection, and `report.md`; forbidden changes=merge, Issue close, production rollout, unrelated canonical docs; acceptance criteria=`cl-s13-closure` proves direct 0.17 planning→fresh Red→Blue revision, projection parity, quality, review, and adoption gates on one pushed HEAD; required verification=integration suite, validate, parity, report audit, and final exit contract; reviewer focus=`qa-reviewer` checks whole-issue evidence and `spec-reviewer` checks docs/identity alignment; stop conditions=P0/P1, stale identity, required check, or unresolved EAL; output required=integration receipt, final gate matrix, changed files, risks, and report Ledger Note.
- 具体テストケース: `tc-s13-001` は planning→fresh Red review→Blue revision と provider/dogfood parity を同一 pushed HEAD で確認する。前提は S01–S12 pass、操作は full quality gate、期待結果は all required evidence と no unresolved ledger、失敗検出は stale HEAD/未採用 artifact、検証方法は integration suite、validate、parity、report audit。
- step closure contract: `cl-s13-closure`、S90、S99、Final Exit Contract を report に記録し、PR/merge workflowへ引き渡す。
- step gate / report destination: P0/P1、fresh review、source identity、required check のいずれかが未解決なら Issue finish を実行しない。

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

1. Verify the reviewed Candidate identity, current HEAD, and report adoption record; do not overwrite canonical docs from unreviewed output。
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
