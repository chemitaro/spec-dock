---
種別: 設計書（Issue候補）
ID: "iss-00313"
タイトル: "PR Merge Preparer の証拠駆動 Repair Continuation Policy"
Issue Grade Candidate: "strict"
状態: "draft-candidate"
作成者: "ChatGPT 5.6 Pro"
最終更新: "2026-07-13"
関連Requirement: ["candidates/requirement.md"]
関連Plan: ["candidates/plan.md"]
親: ["epic-00158", "init-local-00003"]
authority: "evidence_only"
adoption_status: "unreviewed"
profile_authority: "recommendation_only"
source_manifest_hash: "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d"
---

# iss-00313 PR Merge Preparer の証拠駆動 Repair Continuation Policy — Issue 設計候補（Strict）

> この文書内の `[N]` は「このcandidateが採用された場合のnormative contract」を意味する。現時点のlocal integration decision、authorized profile、fresh reviewer approval、execution readinessを意味しない。

## 0. 文書の位置づけ

この設計は、現行の固定 attempt cap と同一 `root_cause_family` 再発停止を、integrated batch analysis、mandatory ChatGPT consultation、orchestrator disposition、material strategy deltaに基づくsemantic continuation gateへ置換する。

実装順、Red/Green、delegation、具体command、report evidence destinationは`candidates/plan.md`で定義する。

## 1. Strict candidate と Issue 境界確認

### 1.1 Candidate grade

- 推奨: `strict`
- profile authority: recommendation only
- 理由:
  - shipped agent workflow contractを変更する。
  - provider skill / prompt / template contractとdogfooding compatibilityへ影響する。
  - continuation、failure/recovery、human gate、evidence authorityを明示する必要がある。
- Criticalでない理由:
  - runtime / persistent schema / destructive migration / GitHub mutationを追加しない。
  - secrets / authentication materialsを扱わず、むしろ送信禁止を固定する。
  - provider prose/template revertでrollback可能。

### 1.2 Issue boundary verdict

- decision: `single_issue_coherent`
- Epic repair: no
- split: no, unless escalation trigger occurs

[N] 本Issueのdecision radiusは、`github-pr-merge-preparer` がblocking repairをcontinue / human-gateへ分岐するworkflow contractと、それを記録・配布・検証する従属surfaceに限定する。

[N] runtime consultation automation、observation schema、GitHub conversation mutation、cross-skill retry frameworkは別decision radiusであり、本Issueへ取り込まない。

### 1.3 Critical escalation guard

| 条件 | Candidate判定 | 対応 |
|---|---|---|
| secret / authentication material送信 | no | 判明したら停止しCritical評価 |
| destructive artifact migration | no | 判明したらsplit |
| GitHub state mutation追加 | no | 判明したらCritical / separate Issue |
| persistent retry state schema | no | migration designへsplit |
| automatic high-risk strategy execution | no | human gateを維持 |
| rollback不能 | no | plan amendment |

## 2. Executive Design Summary

### 2.1 変わること

1. `Fix loop limits` を `Repair continuation and human-gate policy` に置換する。
2. P0 1回、same-family P1 2回、total 4回のdefault capを削除する。
3. same-family recurrenceをautomatic stopからrecurrence analysis triggerへ変更する。
4. branch mutationを伴うblocking repair delegation前にintegrated batch-wide ChatGPT consultationを必須にする。
5. materially changed evidence / grouping / strategyがある場合はconsultation freshnessを再評価する。
6. ChatGPT outputはevidence-onlyで、main orchestrator disposition後のみrepair strategyへ変換できる。
7. batch templateへconsultation gate、integrated strategy、iteration ledger、semantic stop fieldsを追加する。
8. iteration indexはtelemetryとして維持するが、limit authorityから切り離す。

### 2.2 変えないこと

- P0/P1 blocking、P2/P3 non-blocking policy。
- P2/P3 aloneでbranch mutationしないrule。
- latest-head observation requirement。
- `github-pr-observation` collection-only boundary。
- required/non-required checksの扱い。
- merge-prepared / review-clean distinction。
- merge / auto-merge / branch deletion / issue finish / review conversation mutation禁止。
- permission/auth、external/flaky、base conflict、scope expansion、breaking/migration/secret/deployment等のhard gate。
- front matter、artifact filename、runtime CLI、JSON schema。

### 2.3 Fixed design contracts

- `[N] DES-001`: repair countはtelemetryであり、continue/stop authorityではない。
- `[N] DES-002`: same-family recurrenceはautomatic stopではなくmandatory re-analysis triggerである。
- `[N] DES-003`: branch-mutating blocking repairにはcurrent integrated batchへboundしたfresh ChatGPT consultationが必要である。
- `[N] DES-004`: ChatGPT outputはevidence-onlyで、orchestrator dispositionなしにworker handoffへ入らない。
- `[N] DES-005`: continueにはfresh evidence、complete triage、no hard stop、materially distinct bounded strategy、fresh consultation、scope-safe validationが必要である。
- `[N] DES-006`: no new viable strategy、same ineffective strategy、insufficient/stale/unsafe evidenceはhuman gateである。
- `[N] DES-007`: skillがworkflow authority、templatesはevidence slots、testsはprojection contractを検証する。
- `[N] DES-008`: provider sourceを先に変更し、mirrorはstandard updateで生成・検証する。mirror-only direct editは禁止する。
- `[N] DES-009`: existing batchは非破壊resume可能で、bulk migrationを要求しない。
- `[N] DES-010`: runtime、observation schema、GitHub mutation、assurance authorityを変更しない。

## 3. Normative Sources と優先順位

| 種別 | Path / ID | 意味 |
|---|---|---|
| Parent requirement | `epic-00158/requirement.md` | skill ownership、evidence authority、provider/mirror boundary |
| Parent design | `epic-00158/design.md` | provider source-first、main orchestrator adoption boundary |
| Parent plan | `epic-00158/plan.md` | issue slicing、readiness、mirror validation、EAL |
| Current skill | `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | current workflow and attempt limits |
| Current prompt | `.../github-pr-merge-preparer/agents/openai.yaml` | agent invocation wording |
| Current templates | skill-local + artifact + discussion `pr-repair-batch.md` | batch evidence contract |
| Historical design | `iss-00178` | triage batch / repair unit / root family / human gate baseline |
| Strict planning rules | `phase_plan_issue.md`, `authoring/issue-plan.md`, strict plan template | closure/delegation/test/S90/S99 contract |
| Prompt-pack | listed local paths + source manifest | candidate intent; body unverified |

Priority for this candidate:

```text
repository-wide accepted rules / parent contracts
  > current shipped behavior
  > Issue requirement candidate
  > Issue design candidate
  > Issue plan candidate
  > local research / interview / ChatGPT evidence
```

Local artifact filenameに`adopted`が含まれていても、本packはそのauthorityを引き継がない。actual bodyとEAL dispositionの検証が必要である。

## 4. Requirement-to-Design Traceability

| Requirement | Design | 扱い |
|---|---|---|
| BH-001 / AC-001 | DES-001 | numeric cap削除、iteration telemetry化 |
| BH-002 / AC-003 | DES-003, DES-007 | integrated batch -> consultation -> disposition -> delegation |
| BH-003 / AC-004 / AC-007 | DES-003, DES-006 | consultation freshness / failure handling |
| BH-004 / AC-005 | DES-004 | evidence-only outputとorchestrator disposition |
| BH-005 / AC-002 | DES-002 | recurrence classification |
| BH-006 / AC-006 | DES-005, DES-006 | semantic continuation algorithm |
| BH-007 / AC-008 | DES-006, DES-010 | hard stops preserved |
| BH-008 / AC-009 | DES-007 | template evidence schema |
| BH-009 / AC-010..AC-012 | DES-007, DES-008 | provider/prompt/templates/tests/mirror |
| BH-010 / AC-011 | DES-009 | legacy batch resume compatibility |
| AC-013 | DES-010 | non-scope diff guard |
| AC-014 | plan contract | closure/delegation/tests/S90/S99 |
| CON-001 / CON-002 | DES-004, DES-010 | no authority escalation |
| CON-003 | DES-008 | provider source first |
| CON-004 / CON-005 | DES-010 | unchanged observation/GitHub boundaries |
| CON-006..CON-008 | DES-001..DES-006 | mandatory consultation + semantic termination |
| CON-009..CON-012 | DES-007..DES-010 | no runtime, safe output, freshness |

## 5. Decision Radius / Escalation

| ID | 判断 | 扱い | 理由 |
|---|---|---|---|
| DEC-001 | fixed attempt capsを削除する | owned | Issue titleとcurrent defectの中心 |
| DEC-002 | recurrenceをanalysis triggerへ変更 | owned | count removal後のcore behavior |
| DEC-003 | mandatory integrated ChatGPT consultation | owned candidate | local evidence filenameとprompt intentに整合 |
| DEC-004 | ChatGPT output disposition vocabulary | owned | authority boundaryに必要 |
| DEC-005 | semantic continue/human-gate algorithm | owned | blind retry防止に必要 |
| DEC-006 | batch template evidence fields | owned | auditabilityに必要 |
| DEL-001 | exact prose / headings / helper test structure | delegated to implementation | semanticsを維持すれば局所選択可 |
| ESC-001 | runtime ChatGPT automation | separate Issue / architecture review | network/host boundaryを跨ぐ |
| ESC-002 | observation JSON change | separate Issue | collection contractを跨ぐ |
| ESC-003 | cross-skill retry framework | Epic/ADR candidate | durable broad policy |
| ESC-004 | GitHub mutation追加 | Critical / separate Issue | safety boundary |

ADR candidate:

- このIssueだけのskill-local contractとしては新規ADR不要。
- 3つ以上のunrelated skillsへevidence-gated retryを展開する場合、cross-skill ADRを検討する。

## 6. Current State と Target State

### 6.1 Current state

```text
observe latest head
  -> triage batch
  -> if blocking:
       apply severity + fixed attempt caps
       if same family reappears after repair: stop
       else delegate bounded fix
  -> push
  -> re-observe
```

問題は、`attempt_count` と `same_family recurrence` がtermination authorityになっており、新しいevidence / strategyを評価する前にstopし得ることである。

### 6.2 Target state

```text
observe latest head
  -> verify freshness / trigger boundary
  -> create or update integrated blocking batch
  -> complete triage and family/coupling analysis
  -> hard-stop check
  -> obtain fresh sanitized ChatGPT consultation for current batch
  -> main orchestrator dispositions recommendations
  -> require bounded strategy + material delta + validation plan
  -> delegate repair
  -> confirm commit/push
  -> re-observe latest head
  -> classify recurrence/new blockers
  -> repeat semantic gate or human gate
```

[N] There is no numeric iteration ceiling in this decision path.

[N] The path is not infinite by default: every branch mutation requires new current evidence, a fresh/valid consultation, explicit disposition, and an evidence-supported bounded strategy. When those are absent, the path terminates at a human gate.

## 7. Responsibility Architecture

### 7.1 Components

| Component | Owns | Must not own |
|---|---|---|
| `github-pr-observation` | trigger and evidence collection, latest-head observation result | risk disposition, consultation, continuation judgment |
| `github-pr-merge-preparer/SKILL.md` | operational sequence, gates, stop conditions, authority boundary | raw template duplication, runtime parser |
| `openai.yaml` | concise invocation intent | policy details or independent authority |
| skill-local template | detailed operational batch worksheet | workflow authority independent of skill |
| shipped artifact/discussion templates | generated evidence slots and compatible structure | different policy from skill-local template |
| ChatGPT | options, diagnosis hypotheses, tradeoffs, risk/strategy proposal | approval, local integration decision, merge judgment |
| Main orchestrator | evidence verification, dispositions, worker handoff, continue/human-gate | delegating authority to ChatGPT implicitly |
| Repair worker | scoped implementation and validation | redefining requirement/scope or consultation disposition |
| Human | ambiguous/high-risk/unsupported decisions and merge | N/A |

### 7.2 Dependency direction

```plantuml
@startuml
actor Human
participant "github-pr-observation\ncollection only" as Obs
participant "github-pr-merge-preparer\njudgment owner" as Prep
collections "Integrated Repair Batch\nevidence control sheet" as Batch
participant "ChatGPT\nevidence-only consultant" as GPT
participant "Main Orchestrator\ndisposition owner" as Orch
participant "Repair Worker" as Worker

Obs --> Prep : latest-head evidence
Prep --> Batch : inventory / family analysis
Batch --> GPT : sanitized current batch context
GPT --> Orch : recommendations / risks / options
Orch --> Batch : disposition + strategy delta
alt safe bounded strategy exists
  Orch --> Worker : scoped handoff
  Worker --> Orch : commit + validation evidence
  Orch --> Obs : re-observe current head
else hard stop / no strategy / unavailable evidence
  Orch --> Human : human gate evidence
end
@enduml
```

[N] ChatGPT does not call the worker directly in the authority model. The main orchestrator must translate only explicitly dispositioned content into the worker contract.

## 8. Domain Vocabulary / Data Contract

These are workflow-document vocabulary, not a new runtime schema.

### 8.1 `RepairBatchSnapshot`

Conceptual fields:

- `pr_number`
- `head_sha`
- `observation_status`
- `trigger_state`
- `blocking_item_ids`
- `blocking_family_ids`
- `nonblocking_context_ids`
- `allowed_paths`
- `forbidden_paths`
- `requirement_constraints`
- `compatibility_constraints`
- `validation_obligations`
- `snapshot_fingerprint` (human-readable evidence binding; not necessarily machine hash)

### 8.2 `RecurrenceClass`

Candidate vocabulary:

- `not_recurrent`
- `same_family_new_evidence`
- `same_family_incomplete_implementation`
- `same_family_strategy_failed`
- `same_family_misclassified`
- `same_family_stale_observation`
- `same_family_unknown`

[N] `same_family_*` is not itself a stop decision. It selects the required analysis and freshness response.

### 8.3 `RepairStrategy`

Conceptual fields:

- `strategy_id`
- `root_cause_hypothesis`
- `covered_item_ids`
- `covered_family_ids`
- `allowed_paths`
- `behavior_change`
- `compatibility_effect`
- `validation_plan`
- `rollback_plan`
- `delta_from_prior_strategy`
- `bounded_reason`

### 8.4 `ConsultationEvidence`

Conceptual fields:

- `consultation_id`
- `status`: `fresh` / `stale` / `failed` / `unavailable` / `denied` / `unsafe`
- `consulted_at`
- `bound_head_sha`
- `bound_observation_status`
- `bound_family_ids`
- `bound_strategy_context`
- `input_summary_ref`
- `recommendation_summary_ref`
- `open_risks`
- `freshness_invalidators`

[N] Verbatim model conversation record is not a required or permitted batch field. A repository-relative evidence reference may point to a sanitized summary artifact, not to authentication materials, host paths, or unreviewed verbatim model conversation record content.

### 8.5 `OrchestratorDisposition`

Candidate values:

- `use`
- `partial-use`
- `reject`
- `defer`
- `human-gate`

Required fields:

- recommendation or option ID
- disposition
- rationale
- evidence used
- scope effect
- residual risk
- resulting strategy ID, if any

### 8.6 `ContinuationDecision`

Candidate values:

- `continue-repair`
- `reobserve-first`
- `refresh-consultation`
- `human-gate`
- `merge-prepared-evaluation`

[N] No `attempt-limit-reached` value exists.

## 9. ChatGPT Consultation Contract

### 9.1 Trigger

[N] A fresh consultation is required before every branch-mutating blocking repair delegation.

This includes:

- initial blocking batch repair。
- re-observation after a prior repair when blocking items remain。
- new blocking family introduced by repair。
- materially changed family grouping / root cause / allowed scope / validation plan。
- resume of a legacy or paused batch when current evidence differs from the last consultation binding。

A consultation is not required solely because P2/P3 or optional/no-action items remain and no repair mutation is planned.

### 9.2 Consultation scope

[N] Consultation input covers the integrated current blocking batch, not a single isolated comment, unless there is exactly one blocking item and no coupled obligation.

Required input summary:

1. PR / latest-head metadata。
2. observation completeness and trigger state。
3. all blocking inventory items and evidence references。
4. family / coupling analysis。
5. previous strategies, commits, validation, and re-observation results。
6. current recurrence classification。
7. allowed and forbidden paths/actions。
8. requirement/design/compatibility/security constraints。
9. proposed questions: root cause, options, strategy delta, tests, risks, stop conditions。

### 9.3 Sanitization

[N] The orchestrator must remove or redact:

- secrets, tokens, authentication materials, asymmetric signing materials。
- personal/private information not necessary for diagnosis。
- host-local absolute paths。
- raw environment dumps。
- unrelated repository content。
- executable/binary payloads。

When sanitization would remove evidence essential to a safe decision, consultation status is `unsafe` and the workflow goes to human gate.

### 9.4 Retained output

Retain only:

- consultation provenance/status/freshness binding。
- concise diagnosis/options/risks summary。
- proposed strategy deltas。
- unresolved questions。
- orchestrator disposition and rationale。

Do not paste a verbatim model conversation record into canonical docs or the repair batch.

### 9.5 Authority

[N] Consultation is advisory evidence.

It cannot:

- authorize branch mutation。
- change requirements or allowed scope。
- approve a profile or assurance state。
- provide fresh reviewer approval。
- declare merge-prepared / pull-request handoff eligibility。
- resolve review conversations。
- perform local integration decision。

### 9.6 Freshness invalidation

A consultation becomes stale when any material binding changes:

- `head_sha`
- observation trigger state or completeness
- blocking items/families
- root-cause grouping
- previous strategy outcome
- allowed/forbidden paths
- requirement/design/compatibility/security constraints
- validation or rollback plan

A head SHA change caused only by a non-semantic metadata commit still requires explicit orchestrator freshness judgment; no silent carry-forward.

## 10. Recurrence Analysis and Continuation Algorithm

### 10.1 Algorithm

```text
INPUT: latest observation, current batch, prior ledger

1. Verify latest-head and trigger freshness.
   - stale/incomplete -> reobserve-first or human-gate.

2. Rebuild integrated blocking inventory and family/coupling analysis.
   - no blockers -> merge-prepared-evaluation.

3. Evaluate hard human gates.
   - any hard gate -> human-gate.

4. Classify recurrence for each blocking family.
   - stale observation -> reobserve-first.
   - misclassified -> regroup; material change.
   - incomplete implementation -> describe missing bounded work.
   - strategy failed/new evidence -> require new hypothesis and strategy delta.
   - unknown -> human-gate unless evidence resolves it.

5. Obtain/refresh sanitized ChatGPT consultation for current batch.
   - unavailable/failed/denied/unsafe/stale -> human-gate.

6. Main orchestrator dispositions recommendations.
   - no use/partial-use strategy -> human-gate.

7. Validate candidate strategy.
   - must be bounded, in scope, materially distinct where needed,
     have tests/rollback/re-observation path, and preserve hard contracts.
   - otherwise -> human-gate or plan amendment.

8. Delegate one coherent repair unit or ordered set of coupled units.

9. Confirm commit/push evidence and re-observe latest head.

10. Append ledger and repeat from step 1.
```

### 10.2 Decision table

| Evidence state | Recurrence | Strategy state | Consultation | Decision |
|---|---|---|---|---|
| stale / incomplete | any | any | any | `reobserve-first` or human gate |
| fresh, no blockers | none | N/A | N/A | merge-prepared evaluation |
| fresh | first occurrence | bounded/in-scope | fresh + dispositioned | continue repair |
| fresh | incomplete implementation | bounded completion delta | fresh + dispositioned | continue repair |
| fresh | prior strategy failed | materially distinct strategy | fresh + dispositioned | continue repair |
| fresh | prior strategy failed | same/renamed strategy only | any | human gate |
| fresh | misclassified family | regrouped evidence | refreshed | continue only after new disposition |
| fresh | unknown recurrence | no resolvable evidence | any | human gate |
| fresh | any | scope expansion required | any | plan amendment / human gate |
| fresh | any | safe strategy | unavailable/failed/denied/unsafe | human gate |
| fresh | any | any | stale | refresh consultation before repair |
| fresh | any | any | verbatim model conversation record only/no disposition | human gate |

### 10.3 Semantic termination properties

The loop terminates or stops autonomously when:

- no blockers remain。
- no fresh latest-head evidence exists。
- a hard gate is present。
- no materially distinct bounded strategy exists。
- consultation cannot be completed safely/freshly。
- orchestrator cannot disposition a recommendation confidently。
- required scope/contract would expand。

Therefore removing numeric caps does not imply unconditional infinite retry.

## 11. Hard Human Gate Contract

[N] The following categories remain immediate or pre-delegation human gates regardless of iteration count:

- permission / authentication / authorization failure。
- external service / platform / flaky failure that is not safely repairable in repository scope。
- base branch conflict or required rebase/merge judgment。
- unknown failure without sufficient source evidence。
- requirement expansion or design contract change。
- breaking change, migration, secret, authentication material, deployment, production-state impact。
- ambiguous review intent or conflicting reviewer directions。
- platform-only review reply / thread resolution / dismissal / admin override。
- unapproved review trigger, stale trigger, or missing resume metadata。
- unsafe consultation payload or unavailable mandatory consultation。
- same ineffective strategy without a material delta。
- user-authored artifact protection cannot be guaranteed。

[N] Existing forbidden writes/actions remain unchanged.

## 12. Skill / Prompt / Template Contract Delta

### 12.1 `SKILL.md`

Replace:

- heading `Fix loop limits`
- numeric P0/P1/total defaults
- same-family recurrence hard-stop rule

With:

- `Repair continuation and human-gate policy`
- attempt count telemetry statement
- integrated batch consultation gate
- recurrence classification
- consultation freshness and authority
- strategy-delta continuation conditions
- semantic stop / human gate list
- ledger requirements

Preserve:

- workflow sequence around observation / triage / worker / push / re-observe。
- forbidden writes/actions。
- P2/P3 policy。
- merge-prepared predicate and human merge decision boundary。

### 12.2 `openai.yaml`

Current wording that emphasizes “bounded fixes” may be interpreted as attempt-bounded. Candidate wording should emphasize:

- integrated blocking batch triage
- evidence-gated repair continuation
- fresh ChatGPT consultation
- bounded scope/strategy, not bounded number of attempts
- human merge judgment remains external

Example intent, not mandatory exact text:

```yaml
default_prompt: >-
  Prepare the current PR for human merge judgment by observing the latest head,
  triaging the integrated repair batch, consulting ChatGPT as evidence before
  branch-mutating blocking repairs, delegating only dispositioned in-scope
  strategies, re-observing after each push, and stopping at semantic human gates.
```

### 12.3 Batch template sections

Required target sections:

1. `PR / Observation Metadata`
2. `Batch Purpose`
3. `Concern Catalog`
4. `Inventory`
5. `Per-Concern Analysis`
6. `Root-Cause Family and Coupling Analysis`
7. `Integrated Repair Strategy`
8. `ChatGPT Consultation Gate`
9. `Orchestrator Disposition`
10. `Repair Queue / Unit Plan`
11. `Repair Iteration Ledger`
12. `Semantic Stop / Human-Gate Conditions`
13. `Merge-Prepared Gate`
14. `Final Summary`

### 12.4 Consultation block fields

```text
consultation_required
consultation_status
consultation_id
consulted_at
bound_head_sha
bound_observation_status
bound_family_ids
input_summary_ref
recommendation_summary_ref
freshness_invalidators
open_risks
orchestrator_disposition_summary
```

### 12.5 Iteration ledger fields

| Field | Meaning |
|---|---|
| `iteration_index` | telemetry only; no cap |
| `head_sha` | observation binding |
| `observation_status` | complete/limited/stale/etc. |
| `family_ids` | current affected families |
| `recurrence_class` | recurrence analysis |
| `prior_strategy_id` | previous attempted strategy |
| `proposed_strategy_id` | current candidate strategy |
| `strategy_delta` | material difference |
| `consultation_id/status` | evidence reference and freshness |
| `orchestrator_disposition` | use/partial/reject/defer/human-gate |
| `action_taken` | delegated/none/reobserve/etc. |
| `fix_commit` | commit evidence |
| `re_observation_result` | latest result |
| `continuation_decision` | continue/reobserve/refresh/human/merge-eval |
| `stop_reason` | semantic reason, not count threshold |

### 12.6 Removed template semantics

- `Default autonomous repair limit`
- `Default total autonomous repair limit`
- `loop limits reached`
- “same family reappeared” as a sufficient stop condition

### 12.7 Preserved template semantics

- required/non-required CI evidence。
- review findings / thread state / merge blockers。
- validity / risk / need-to-fix / disposition inventory。
- repair units and validation evidence。
- review-clean vs merge-prepared。
- forbidden actions and residual risk。

## 13. File Change Plan

### 13.1 Provider files

| Path | Change |
|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | primary workflow contract replacement |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml` | evidence-gated integrated repair intent |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` | skill-local detailed worksheet |
| `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md` | generated artifact contract |
| `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md` | generated discussion contract, lockstep with artifact template |

### 13.2 Tests

| Path | Planned coverage |
|---|---|
| `tests/cli_runtime/test_new.py` | generated pr-repair-batch contains new markers, excludes old limits, preserves metadata/path |
| `tests/cli_runtime/test_runtime_new_doc_s09.py` | doc/artifact type selection and template parity still work; content contract updated |
| `tests/cli_runtime/test_wrappers.py` | installed/dogfooding skill/template projection matches provider semantics and old limit markers absent |

### 13.3 Generated / dogfooding verification surfaces

- `.agents/skills/github-pr-merge-preparer/**`
- `spec-dock/templates/artifacts/pr-repair-batch.md`
- `spec-dock/templates/discussions/pr-repair-batch.md`

[N] Edit provider first. Refresh via repository-standard `spec-dock update .`. Generated changes may appear in the diff, but direct mirror-only hand editing is forbidden.

### 13.4 Forbidden paths

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/**`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- `src/spec_dock/cli.py`
- GitHub workflow/action code unrelated to asset projection
- `.assurance.json`
- unrelated Issue/Epic/Initiative canonical docs except explicit main-orchestrator adoption after this pack

## 14. Compatibility and Migration

### 14.1 Compatibility strategy

[N] This is an additive/rewording Markdown contract change with removal of obsolete stop semantics; no runtime schema version is introduced.

- Existing repair-batch files remain valid historical evidence。
- Existing front matter / filename / ID / scope behavior remains unchanged。
- A legacy batch may be resumed by appending current consultation / strategy / iteration sections without deleting historical content。
- Any old `attempt limit reached` decision remains historical evidence; it is not silently rewritten。
- New continuation decisions use the new semantic gate from the resume point forward。

### 14.2 Migration

- bulk migration: none
- automated rewrite: none
- required manual update for active legacy batch: append current snapshot + consultation/disposition before next repair mutation
- read compatibility: Markdown remains readable
- write compatibility: new templates produce additional sections

### 14.3 Rollback

1. Revert provider skill/prompt/templates/tests。
2. Run repository-standard `spec-dock update .` to restore dogfooding projection。
3. Run targeted tests, validate, sync, parity inspection。
4. Do not rewrite historical batches; new sections remain harmless evidence if already created。

Rollback does not require data migration.

## 15. Failure / Recovery Design

| Failure | Detection | Recovery | Autonomous repair allowed? |
|---|---|---|---|
| stale observation | head/trigger mismatch | re-observe latest head | no before fresh evidence |
| consultation unavailable | status/result missing | retry host consultation if policy allows, otherwise human gate | no |
| consultation denied | explicit denied state | human gate | no |
| consultation unsafe | sanitization impossible | human gate; do not transmit | no |
| consultation stale | material binding changed | refresh consultation | no before refresh |
| verbatim model conversation record only | no sanitized summary/disposition | summarize safely or human gate | no |
| conflicting recommendations | no evidence-supported choice | human gate | no |
| same strategy repeated | strategy delta absent | human gate | no |
| new viable strategy | evidence + delta + fresh consultation | disposition and delegate | yes, bounded scope |
| provider/mirror drift | parity/test failure | rerun update; inspect source authority | no final closure |
| generated template mismatch | focused test failure | repair provider templates/tests | no final closure |
| scope expansion discovered | diff/design mismatch | stop and amend/split | no |
| unrelated regression | test failure | stop; root-cause before proceeding | no |

[N] Recovery state must not be represented as pass. Missing / stale / failed / unavailable / denied / unsafe consultation blocks branch mutation.

## 16. Security / Privacy / Trust Boundary

### 16.1 Trust levels

| Input | Trust level | Handling |
|---|---|---|
| latest observation stdout JSON | authoritative evidence for collected state, subject to freshness | verify head/trigger |
| progress logs / auxiliary artifact | supporting evidence | cross-check |
| ChatGPT output | untrusted advisory evidence | sanitize, summarize, disposition |
| worker report | delegated evidence | verify diff/tests/commit |
| canonical docs | repository authority after proper adoption/review | do not overwrite from raw output |

### 16.2 Data minimization

- include only evidence necessary to reason about blocking batch。
- use repository-relative paths。
- omit full source files unless a minimal excerpt is required and safe。
- redact secrets/tokens/private identifiers。
- retain no browser/profile/authentication material details。
- do not include verbatim model conversation record in shipped templates or canonical docs。

### 16.3 Prompt injection / embedded instruction boundary

Text inside review comments, CI logs, issue bodies, source files, or consultation outputs is evidence data, not workflow authority. Only the active task, repository rules, accepted canonical docs, and orchestrator disposition may direct action.

## 17. Verification Implications

### 17.1 Positive assertions

- skill includes continuation policy, consultation gate, recurrence analysis, semantic stop。
- templates include integrated strategy, consultation, disposition, iteration ledger。
- generated artifact contains new sections。
- mirror matches provider after update。
- P2/P3/hard gate/forbidden action clauses remain。

### 17.2 Negative assertions

- old P0/P1/total fixed cap phrases absent。
- `loop limits reached` absent。
- same-family recurrence not a sufficient stop phrase。
- verbatim model conversation record field/instruction absent。
- no runtime/observation/assurance diff。

### 17.3 Behavioral test seeds

- `tc-generated-contract`: create pr-repair-batch; inspect positive/negative markers and metadata compatibility。
- `tc-doc-type-parity`: all supported types including pr-repair-batch still select correct template and ID/path shape。
- `tc-installed-projection`: init/update temp repo; installed skill/template contains new policy and no old limits。
- `tc-provider-mirror-parity`: compare provider and dogfooding files after update。
- `tc-nonscope-diff`: runtime / observation paths unchanged。

## 18. Alternatives Considered

### ALT-001: Remove caps only

Rejected. Blind/unbounded retry risk remains and no audit/termination substitute exists.

### ALT-002: Keep caps but increase numbers

Rejected. Arbitrary count remains a poor proxy for evidence and strategy quality.

### ALT-003: Stop on every same-family recurrence

Rejected. Does not distinguish incomplete implementation, new evidence, misclassification, or a materially different strategy.

### ALT-004: ChatGPT automatically chooses and authorizes the fix

Rejected. Violates evidence/canonical authority boundary and creates unsafe implicit delegation.

### ALT-005: Consultation only after N failed attempts

Rejected. Reintroduces numeric authority and allows initial repair without integrated batch review.

### ALT-006: Consultation for every observation including P2/P3-only state

Rejected. Unnecessary overhead and conflicts with no-mutation policy for nonblocking findings. Consultation is mandatory when branch-mutating blocking repair is contemplated.

### ALT-007: Implement runtime counter/state machine

Rejected as out of scope. Current change is a skill/template workflow contract and can be tested without runtime persistence.

### ALT-008: Split skill, templates, tests into separate Issues

Rejected. They are one vertical contract slice; splitting would create temporary drift and cross-Issue incomplete behavior.

## 19. Open Items / Assumptions

### A-001 Mandatory consultation scope

Candidate decision: every branch-mutating blocking repair delegation requires fresh integrated consultation. This is inferred from prompt-pack artifact naming; actual local synthesis body must be inspected before adoption.

### A-002 Consultation storage

Candidate decision: store sanitized summary/provenance/disposition, not verbatim model conversation record. If local workflow requires a raw artifact for separate host operation, that raw artifact remains outside this output and cannot become canonical without safe review.

### A-003 Template exact headings

Exact Japanese/English heading names may vary during implementation if all semantic fields and tests remain. This is `[P]`, not a contract change.

No unresolved item proves the Issue boundary unsafe. These are adoption verification items, not a reason for `information_insufficient`.

## 20. Plan Handoff Contract

The strict candidate plan must:

1. characterize current fixed-limit clauses and template markers before edits。
2. add Red assertions for positive new contract and negative old markers。
3. update skill/prompt before or in lockstep with templates without direct mirror edits。
4. preserve hard gates and non-scope behavior with explicit checks。
5. run repository-standard update, focused tests, static checks, validate, sync, parity inspection。
6. include closure index mapping every AC/DES。
7. include step-local delegation and concrete test cases。
8. include S90 impact resolution, strict review gate, S99 final gate, Final Exit Contract。
9. stop on source drift, local artifact contradiction, scope expansion, regression, or authority ambiguity。
10. record all observed evidence in `report.md` after local integration decision; this pack cannot create that evidence claim.
