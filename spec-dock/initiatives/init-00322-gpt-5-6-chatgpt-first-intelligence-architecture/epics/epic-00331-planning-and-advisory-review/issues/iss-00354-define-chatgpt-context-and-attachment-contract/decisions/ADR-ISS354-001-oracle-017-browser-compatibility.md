---
種別: issue-local decision record
ID: "ADR-ISS354-001"
タイトル: "Oracle 0.17.0 browser compatibility profile and bounded recovery boundary"
状態: "proposed"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
対象: ["iss-00354", "epic-00331", "init-00322"]
---

# ADR-ISS354-001 Oracle 0.17.0 browser compatibility profile and bounded recovery boundary

> **Review target / evidence-only / provisional**  
> 本recordは `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` のレビュー対象である。Issue `iss-00354` と Initiative `init-00322` のformal Issue Planning laneに
> 限定した暫定判断であり、Oracle全利用、全ChatGPT operation、組織全体の永続architectureを変更しない。

## Status

`proposed` / unreviewed / not adopted。Candidate v1の正式Red Review FAILに含まれたP1二件だけを修正したv2である。

## Context

| Field | Value |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` |
| Verification | identical / ahead 0 / behind 0; default fallback not used |
| Prior Candidate | `iss-00354-oracle-017-compatibility-candidate-20260804t033922z.zip` / `8f979a5609b5d4dfa899871d50d51a659e273a7191b97e36c4d8de253348d13c` |

source HEADのSpecDock adapterはPATH-resolved Oracle `0.16.1`をexactに受理し、managed Chrome、logical `Pro` / `select`、
one prompt submission、strict session artifact readerを持つ。現行recoveryはstage-blindである。Oracle exit nonzero/timeoutまたはsession
nonterminalでsubmission evidenceを判定せず`_recover_same_session`へ入り、generic adapterが
`oracle session <session-id> --harvest --no-recover`を直接構築する。

Issue #354はminimal body + direct attachment paths、Blue continuity / fresh Red、output validators維持を既に計画している。
外部ローカル証跡ではOracle `0.17.0` + personal wrapperでrepresentative briefが送信前に
`Prompt reconstruction did not match the exact input`となり、direct / inline / none、standard / project、select / currentにまたがって
`promptSubmitted=false`だった。短いsmokeでは`GPT-5.6 Sol` verified成功例と、`Available: Got it.`を伴う初回model discovery failure後の
成功例がある。これらはdirect SpecDock adapterのcompatibility証明ではない。

## Decision 1 — Exact characterized compatibility profile owns recovery commands

Oracle `0.17.0`は、exact version、required help capabilities、browser argv、model/submission stage evidence、attachment modes、session
artifact schemaに加え、次を束ねたprofileとして導入する。

- declared `inline_mode_characterized` capability。
- generation-incomplete用`harvest_argv_builder`。
- response-complete/download-pending用`capture_argv_builder`。

Current 0.16.1 hardcoded commandは0.16.1 profile builderへbehavior-preservingに移す。generic adapterからsession recovery argv assemblyを
削除し、0.17はcharacterized builder以外を実行しない。unknown patch / wildcard semver / missing builderはfail-closedにする。
0.17でharvestとcaptureが同一commandの場合も、同じcharacterized builderを二つのsemantic fieldへ明示bindする。

## Decision 2 — PATH Oracle と Oracle-native config boundary を維持

product dependencyはPATH Oracle本体とmanaged Chromeのままとする。personal wrapper、absolute path、API、alternate backendを呼ばない。
Oracle user/project configは隔離・無効化しない。formal必須値はcharacterized explicit argvで指定する。raw standard/project URLはproduct
contractまたはpublic evidenceへ取り込まない。

## Decision 3 — Logical model request + verified observed evidence

applicationはlogical model selectorを要求し、UI表示名をgeneric constantにしない。formal successにはsame attemptのmodel verified evidenceと
observed non-empty labelを必要とする。`GPT-5.6 Sol`は外部観測であり、direct 0.17 characterizationでmappingが確認された場合だけprofile fixtureへ
局所化する。`current`、default、alternate modelへの黙示fallbackは禁止する。

## Decision 4 — Submission evidence is the recovery gate

- `promptSubmitted=false`またはunknownの全failure class: harvest/capture command invocationは0。unknownをfalseと推測しない。
- pre-submit model failure: profileがretryableと明示する場合、same logical modelでnew executionを最大一回。
- pre-submit direct attachment failure: profileの`inline_mode_characterized=true`の場合、same original pathsでinline new executionを最大一回。
- model retryとinline retryは同じoverall new-execution budget `1`を共有する。
- pre-submit prompt reconstruction mismatch: automatic retryなし。changed precondition後の明示再実行だけ。
- post-submit response incomplete: selected profileのharvest builderだけを一度実行する。
- post-submit response complete / download pending: selected profileのcapture builderだけを一度実行する。
- prompt再送またはnew executionをpost-submit recoveryとして使わない。
- Candidate versionのsuccessful Red submissionは最大一回。pre-submit failureはRed conversationを作成したとみなさない。

Pre-submit cleanup commandをrecovery例外として追加しない。

## Decision 5 — Response completion と download / artifact validation を分離

responseが完了してもZIP download / session artifact snapshotが完了したとはみなさない。stage evidenceで区別し、download pending/failureは
profile-owned capture commandを一度だけ行う。なおmissing/ambiguous/corruptならexisting strict artifact reasonでrejectし、responseを生成し直さない。
Generic adapterは0.16.1 recovery commandを0.17 captureへ流用しない。

## Decision 6 — Authoritative public status / reason mapping

Internal failure classからpublic resultへの唯一のmappingは次である。

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

The mapping is closed and authoritative. The five stage-specific classes—model selection, attachment submission,
prompt reconstruction, generation, and output download—must not be collapsed into one another, into
`oracle_capability_unsupported`, or into `oracle_session_recovery_required`. Many-to-one normalization is allowed only for the
three explicitly listed same-semantics families: capability/profile validation, runtime unavailability, and artifact validation.
An unknown internal failure class has no default public mapping and must fail the mapper contract before serialization.

`planning_context_rejected`、`github_exact_branch_unavailable`、successful `transport_received`などstage taxonomy外の既存pairは変更しない。

## Decision 7 — Issue-local evidence / privacy

internal receiptはversion、stage、logical/observed model、verified、attachment mode、submission/response booleans、artifact state、retry countを
保持できる。raw prompt、attachment content、private path、target URL、session handle、transcriptをCandidate / Review / public resultへ保存しない。
external wrapper observationとdirect PATH Oracle evidenceをreport ledgerで別source roleにする。

## Rejected options

1. `SUPPORTED_ORACLE_VERSION`を`0.17.0`へ単純置換する。
2. `>=0.17`を無条件に許可する。
3. generic adapterに0.16.1 hardcoded harvest argvを残し0.17へ流用する。
4. `promptSubmitted=false` / unknownでharvest、capture、cleanup commandを呼ぶ。
5. personal wrapper / API / alternate backendへfallbackする。
6. reconstruction mismatch時にpromptをshorten / normalize / rewriteする。
7. `GPT-5.6 Sol`またはmodel `current`をgeneric fallbackとしてhardcodeする。
8. direct failure時にrequired attachmentをdrop、per-entry exclude、copy、ZIP化する。
9. post-submit failureでnew ChatGPT executionを開始する。
10. stage-specific five classesをgeneric retryable/session reasonへmany-to-one mappingする。
11. retry回数をconfigで無制限化する。
12. Oracle configをtemporary HOMEで隔離する。
13. output ZIP / Review JSON validatorを緩める。

## Consequences

### Positive

- fast-moving Oracle CLI差分とsame-session commandをversion-localにし、unknown behaviorをformal evidence laneへ入れない。
- pre-submit failureへstage-blind harvestする現行riskを除去できる。
- reconstruction/model/attachment/generation/downloadをpublic contractでも一意に診断できる。
- duplicate Candidate / reviewを防ぎつつ、限定的なpre-submit recoveryとpost-submit profile recoveryを扱える。
- Option A/C、Blue/Red、direct Oracle、Human authorityを維持できる。

### Cost

- 0.17 profile、sanitized session fixtures、stage decoder、two semantic recovery builders、browser smokeの保守が必要になる。
- five new public reason valuesとexact CLI/domain testsが必要になる。
- model labelやsession schema/commandが変わるたびにprofile reviewが必要になる。
- reconstruction/submission evidenceが不足するOracle versionはformal operationで使用できない。

## Migration

1. current 0.16.1 stage-blind/hardcoded behaviorをcharacterization testで固定する。
2. current 0.16.1 recovery argvを0.16.1 profile builderへ移し、generic adapterからhardcodeを削除する。
3. direct PATH Oracle 0.17 help/session/browser/inline/harvest/capture behaviorをcharacterizeする。
4. 0.17 profile / decoder / two semantic builders / artifact readerを追加する。
5. false/unknown -> recovery command 0のcross-product testsを導入する。
6. closed public mapping、新規reason、既存reason、many-to-one constraintsをdomain/application/CLI testsで固定する。
7. direct path transportをprimaryにし、classified attachment failureだけinline one-shotをenableする。
8. representative prompt / verified model / required direct attachment / response / ZIP capture smokeをpassする。
9. provider projection、docs、report、fresh review、Human gateを完了する。

## Withdrawal / rollback conditions

次のいずれかで0.17 profileをwithdrawまたは未昇格とする。

- representative prompt reconstructionがclean-state runsで安定しない。
- submission前後またはmodel verifiedを安全に判定できず、false/unknown recovery 0を保証できない。
- 0.17 harvest/capture exact commandをcharacterizeできない、またはgeneric hardcodeを除去できない。
- direct/inline transportにSpecDock側materializationが必要になる。
- 0.17 session artifact schemaをstrict readerで扱えない。
- same-session download captureが成立せずnew executionまたはvalidator緩和が必要になる。
- authoritative public mappingをdomain / CLI / testsで一意に固定できない。
- wrapper/API/alternate model/default branch fallbackが必要になる。
- output/source/authority/projection regressionが残る。

rollbackはreviewed commit/deploymentでprofileを無効化する。runtime内のsilent 0.16 downgradeやalternate backend switchは作らない。

## Scope limitation

本recordは`iss-00354` / `init-00322`のOracle browser formal planning contractに限定する。clarification public command、他Initiative、
API-based product architecture、全Oracle user config policy、全model naming policyへ自動適用しない。scope拡張時は別ADR triageを行う。
