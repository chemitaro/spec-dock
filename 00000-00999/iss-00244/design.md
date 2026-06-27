---
種別: 設計書（Issue）
ID: "iss-00244"
タイトル: "Simplify Issue Execution Guidance Into Plan Centric Preflight Validation"
関連GitHub: ["#244"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00244 Simplify Issue Execution Guidance Into Plan Centric Preflight Validation — 設計

## 親設計参照

- Epic: `epic-00224 Dynamic Workflow Resource Allocation`
- 採用済み補正:
  - `iss-00244` では Epic 初期設計の runtime-selected `Step Assurance Compiler` / `Context Packet Compiler` default path を採用しない。
  - `plan.md` を executable workflow contract、`report.md` を observed evidence ledger とする。
  - `guidance issue-execution` は preflight / consistency validator とし、execution order / worker / reviewer / verification の authority を持たない。
  - `hard cutover` のため、旧 dynamic fields / interfaces は deprecated として残さず削除対象にする。

## 既存実装 / 規約の理解

### 現行 runtime

- `application/workflow.py`
  - `workflow_next()` は `issue-execution` かつ `state.kind == "ready"` のとき `_compile_execution_context()` を呼ぶ。
  - `_compile_execution_context()` は `plan.md` / `report.md` / `assurance.json` / `context-routing-policy.json` などの source refs を作り、step assurance と context packet を生成する。
  - selected step が `issue_wide_default` の場合は `workflow-plan-unselectable` として block する。
  - context packet write failure は `context-packet-write-failure` として block する。
- `application/context_packets.py`
  - `_select_step()` が `plan.md` heading と `report.md` completion rows から次 step を推定する。
  - `_classify_task_kind()` が free text から docs/runtime/migration/security を推定する。
  - `compile_step_assurance_projection()` が worker / reasoning / context / verification / reviewer を決める。
  - `compile_context_packet_projection()` が generated context packet を書く。
- `domain/context_routing.py`
  - runtime-selected worker / reviewer / context matrix を持つ。
- `domain/runbook.py`、`presentation/workflow.py`、`infra/runbook_store.py`
  - `Runbook` が `step_assurance` / `context_packets` を保持し、Markdown / JSON / projection に出力する。
- `commands` / `cli/bootstrap.py`
  - workflow use case に context policy store / context packet store / continuation probe を注入している。

### 現行 docs / skill

- `phase_plan_issue.md` と `authoring/issue-plan.md` は、すでに plan-centric な契約を持つ。
- `spec-dock-issue-planning` / `spec-dock-issue-execution` skill は generated projection を authority としない一方、まだ `selected step when present` を checklist 登録するよう記述している。
- `assurance compose` の `profile-sections.json` は薄い managed section だけを追加し、Step-level Obligation Pattern を作り込む scaffold には不足している。

### 現行 tests

- `tests/cli_runtime/test_workflow_context_routing.py` は旧 dynamic model を強く期待している。
- `tests/cli_runtime/test_workflow.py` は guidance の lifecycle / projection 挙動を確認している。
- `tests/cli_runtime/test_assurance_compose.py` は compose の managed section 追加を確認している。

## 採用方針

### 方針 A: default issue-execution から dynamic context を削除する

- `workflow_next()` は ready な `issue-execution` でも `_compile_execution_context()` を呼ばない。
- `Runbook` は `step_assurance` / `context_packets` を持たない。
- Markdown / JSON / runbook projection は dynamic fields を出力しない。
- context packet write failure は default issue-execution の blocker ではなくなる。
- `report.md` completion rows は guidance control flow に使わない。

### 方針 B: plan readiness / consistency を明示する

- `guidance issue-execution` の ready output は次を示す:
  - `next_action`: approved plan を実行することを示す固定表現。
  - `contract_source`: `spec-dock/active/issue/plan.md`
  - `evidence_ledger`: `spec-dock/active/issue/report.md`
  - `commands`: `active show`、必要な validation / status 確認。
  - `notes`: `plan.md` を上から実行し、step obligations は plan に従う。
  - `stop_conditions`: non-executable / stale / unresolved / reviewer missing / assurance invalid など。
- `guidance issue-planning` も同じ Runbook schema を使うため、agent を誤誘導する `selected step` 登録文面を skill から削除する。

### 方針 C: Step-level Obligation Pattern は planning-time contract に移す

- runtime が text inference で worker/reviewer を選ばない。
- `phase_plan_issue.md` / `authoring/issue-plan.md` / `templates/assurance/profile-sections.json` を更新し、plan author が step obligation を明示できるようにする。
- 標準 pattern:
  - `SpecOnly`: docs/templates/skills/workflow text。`doc-writer` と `spec-reviewer` focus。
  - `CodeReview`: runtime/tests/scaffold behavior。`dev-coder` と `code-reviewer` focus。
  - `CodePlusSpec`: code + docs が不可分な mixed step。両 reviewer focus。
  - `StrictGate`: migration/rollback/filesystem/GitHub/active lifecycle/public contract risk。
  - `CriticalGate`: auth/security/privacy/permission/secrets。
  - `InspectOnly`: read-only / no implementation diff。canonical mutation は不可。
- `NoReview-ReadOnly` という名前は採用せず、誤用を避けるため `InspectOnly` と `approved-no-op` rationale に分ける。canonical artifact mutation がある step は no-review にできない。

## Module Dependency Diagram

```plantuml
@startuml
title Issue Execution Guidance Hard Cutover
' Question answered: Which runtime dependencies are removed from default issue-execution guidance?
' Scope: workflow_next, runbook, presentation, context packet dynamic selector.
' Excluded details: exact parser implementation and PR delivery workflow.
' Update trigger: guidance output schema or default issue-execution authority changes.

package "commands / presentation" as P {
  [guidance command]
  [workflow renderer]
}

package "application" as A {
  [workflow_next]
  [context_packets module] #LightGray
}

package "domain" as D {
  [runbook]
  [workflow_state]
  [context_routing] #LightGray
}

package "infra" as I {
  [runbook_store]
  [context_packet_store] #LightGray
  [context_policy_store] #LightGray
}

[guidance command] --> [workflow_next] : invokes
[workflow_next] --> [workflow_state] : resolves readiness
[workflow_next] --> [runbook] : builds preflight runbook
[runbook] --> [workflow renderer] : markdown/json
[runbook] --> [runbook_store] : human/debug projection

[workflow_next] -[#red,dashed]-> [context_packets module] : remove default call
[context_packets module] -[#red,dashed]-> [context_routing] : remove default dependency
[context_packets module] -[#red,dashed]-> [context_packet_store] : remove default write
[workflow_next] -[#red,dashed]-> [context_policy_store] : no default issue-execution need
@enduml
```

設計判断:

- `context_packets` / `context_routing` 系は default issue-execution path から外す。
- 残存 import / tests がなければ provider source から削除する。
- 残存利用がある場合でも、default `guidance issue-execution` の public contract からは削除し、別機能として明示されない限り保持しない。

## 依存関係分析

- 上流:
  - `workflow_state.py` が active issue / requirement readiness / assurance validity を解決する。
  - `assurance_store.py` が `assurance.json` の source binding / profile authority を扱う。
- 中央:
  - `workflow.py` が guidance state を Runbook に変換する。
  - `runbook.py` が public output contract の domain model。
- 下流:
  - `presentation/workflow.py` と `infra/runbook_store.py` が Markdown / JSON / projection を出す。
  - skills と docs が agent-facing instruction surface。
  - tests が contract を固定する。
- 削除候補:
  - `application/context_packets.py`
  - `domain/context_routing.py`
  - `infra/context_packet_store.py`
  - `infra/context_policy_store.py`
  - `spec-dock/system/assurance/context-routing-policy.json`
  - `spec-dock/system/assurance/schemas/context-routing-policy.schema.json`
  - provider 側の同等 assets
  - 旧 context routing tests
- 削除前確認:
  - `rg` で import / reference を確認する。
  - context routing policy が他機能に使われていないことを確認する。
  - deletion が package import / bootstrap を壊さないことを tests で確認する。

## ディレクトリ / ファイル変更計画

```text
src/spec_dock/assets/
|-- install_root/
|   `-- .agents/
|       `-- skills/
|           |-- spec-dock-issue-planning/
|           |   `-- SKILL.md                 # Modify: selected step 登録文面を削除
|           `-- spec-dock-issue-execution/
|               `-- SKILL.md                 # Modify: plan-centric execution を明示
`-- spec_dock/
    |-- docs/
    |   |-- authoring/
    |   |   `-- issue-plan.md                # Modify: step obligation pattern を明示
    |   |-- phase_plan_issue.md              # Modify: planning-time taxonomy / guidance simplification
    |   `-- workflow_issue.md                # Modify: hard cutover reference / default guidance contract
    |-- templates/
    |   `-- assurance/
    |       `-- profile-sections.json        # Modify: plan scaffold を厚くする
    |-- system/
    |   `-- assurance/
    |       |-- context-routing-policy.json   # Delete if no residual usage
    |       `-- schemas/
    |           `-- context-routing-policy.schema.json # Delete if no residual usage
    `-- scripts/
        `-- spec_dock_runtime/
            |-- application/
            |   |-- workflow.py              # Modify: default dynamic context compile を削除
            |   `-- context_packets.py       # Delete if unused
            |-- domain/
            |   |-- runbook.py               # Modify: step_assurance/context_packets fields を削除
            |   `-- context_routing.py       # Delete if unused
            |-- infra/
            |   |-- runbook_store.py         # Modify: projection schema から dynamic fields を削除
            |   |-- context_packet_store.py  # Delete if unused
            |   `-- context_policy_store.py  # Delete if unused
            |-- cli/
            |   `-- bootstrap.py             # Modify: unused store injection を削除
            `-- presentation/
                `-- workflow.py              # Modify: markdown/json dynamic sections を削除

tests/
|-- cli_runtime/
|   |-- test_workflow.py                     # Modify/Add: plan-centric guidance contract
|   |-- test_workflow_context_routing.py     # Delete/Replace: dynamic selection tests
|   `-- test_assurance_compose.py            # Modify/Add: richer plan sections
`-- unit/
    `-- ...                                  # Add if plan lint/domain helpers are introduced

spec-dock/
`-- initiatives/.../iss-00244...             # Modify: requirement/design/plan/report and discussions only
```

## インターフェース契約

### `guidance issue-execution` Markdown

Must include:

- `state`
- `next_action`
- `reason_code`
- `active_issue`
- `authority`
- `Commands`
- `Notes`
- `Stop Conditions`
- `Projection`
- `contract_source: spec-dock/active/issue/plan.md`
- `evidence_ledger: spec-dock/active/issue/report.md`

Must not include:

- `## Step Assurance`
- `## Context Packets`
- `selected_step`
- `worker` inferred by runtime
- `reasoning_effort` inferred by runtime
- `context_mode` inferred by runtime
- `verification` inferred by runtime
- `reviewers` inferred by runtime

### `workflow next --format json` / `guidance` projection JSON

Must include:

- `schema_version`
- `workflow_target`
- `state`
- `next_action`
- `reason_code`
- `authority`
- `commands`
- `notes`
- `stop_conditions`
- `active_issue_id`
- `contract_source`
- `evidence_ledger`

Must not include:

- `step_assurance`
- `context_packets`

### Plan contract lint / readiness

Minimum checks:

- `plan.md` is non-placeholder and has no unresolved scaffold marker.
- It contains implementation steps or explicit approved-no-op / decision-only closure.
- Each implementation step has:
  - behavior goal
  - obligation pattern
  - delegated role / worker allocation
  - allowed paths
  - forbidden changes
  - acceptance / closure ids
  - verification or alternative evidence path
  - reviewer / QA gate or inspect-only rationale
  - report evidence destination
  - commit/no-op gate
  - stop / amendment triggers
- S90 and S99 are present unless design explicitly marks a valid waiver syntax.

## 状態 / Activity 差分

```plantuml
@startuml
title Issue Execution Guidance State Delta
' Question answered: How does guidance choose readiness without selecting a step?
' Scope: issue-execution guidance state only.
' Excluded details: implementation step execution and PR delivery.
' Update trigger: guidance state machine change.

start
:Resolve active issue;
if (active issue?) then (no)
  :Return issue-start-required;
  stop
else (yes)
endif

:Read requirement/design/plan/report/assurance;
if (requirement/design/plan substantive and fresh?) then (no)
  :Return planning-required or classification-required;
  stop
else (yes)
endif

if (plan executable contract?) then (no)
  :Return planning-required;
  stop
else (yes)
endif

:Return execute-approved-plan;
:Point to plan.md and report.md;
note right
No selected_step.
No worker inference.
No context packet generation.
end note
stop
@enduml
```

## 要件 → 設計マッピング

| Requirement | Design response |
|---|---|
| AC-001 | Runbook に `contract_source` / `evidence_ledger` を追加し、ready guidance を `execute-approved-plan` にする |
| AC-002 | Runbook / renderer / store から `step_assurance` / `context_packets` を削除 |
| AC-003 | `workflow_next()` から report parser / `_select_step()` default call を削除 |
| AC-004 | plan readiness / lint check を guidance preflight に追加 |
| AC-005 | `authoring/issue-plan.md` と compose fragments を更新 |
| AC-006 | step obligation pattern を docs / templates / tests で固定 |
| AC-007 | planning/execution skill から selected step 登録文を削除 |
| AC-008 | old context routing tests を plan-centric tests に置換 |
| AC-009 | planning manual test findings を report / discussion に記録 |
| AC-010 | provider / dogfood parity と guidance profile authority consistency を validate / tests / inspection で確認 |

## テスト戦略

- Unit / domain:
  - Runbook model no longer accepts dynamic fields.
  - Plan readiness helper detects placeholder / missing required fields / missing S90-S99.
- CLI runtime:
  - ready `guidance issue-execution` has no dynamic fields.
  - report completion rows do not affect guidance output.
  - context policy missing/invalid no longer blocks default ready guidance.
  - non-executable plan blocks execution.
  - stale source binding still blocks as before.
- Asset / scaffold:
  - skill text no longer mentions registering selected step.
  - `profile-sections.json` includes planning-time obligation scaffold.
  - deleted context policy assets are not copied by installer/update.
- Dogfooding:
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement`
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all`
  - `./spec-dock/scripts/spec-dock validate`
  - `guidance` が表示する `authorized_profile` と `assurance classify` の current source binding が矛盾しないことを確認する。

## 互換性 / 移行 / ロールバック

- 互換性:
  - hard cutover。default output schema から dynamic fields を削除する。
  - deprecated field は残さない。
- 移行:
  - tests を新 contract へ置換する。
  - docs / skills を同じ authority model へ更新する。
  - dogfooding mirror は provider source の検証対象として確認する。
- ロールバック:
  - 旧 dynamic model の復活はこの Issue の rollback path ではない。
  - rollback が必要な場合は、`plan.md` preflight の導入差分を戻す。ただし `selected_step` 復活は別 decision を必要とする。

## Manual Test Findings の扱い

- `guidance issue-planning` は dogfooding runtime で `状態: "draft"` を `requirement-scaffold` に分類する。
- これは safety としては block 方向だが、reason_code が scaffold と draft/review-required を区別しない。
- 本 Issue の実装時には、issue-execution hard cutover に加えて、guidance reason semantics が agent を誤誘導しないことを確認する。
- provider / dogfood runtime の drift は実装前に `rg` / tests で確認し、必要なら provider source と shipped dogfood assets の同期対象に含める。

## 未解決論点

- `context_packets.py` / `context_routing.py` の完全削除可否:
  - design 方針: default issue-execution interface としては削除。残存利用がなければ file / assets / tests を削除する。
  - 実装前調査で残存利用が見つかった場合は、保持理由と public surface を report に記録する。
- S90 / S99 waiver:
  - design 方針: 原則必須。waiver は existing `workflow_issue.md` と矛盾しない明示 rationale が plan にある場合だけ。
- `InspectOnly` pattern:
  - design 方針: read-only / no implementation diff 専用。canonical mutation がある場合は spec/code review obligation を持つ。

## Assurance Profile

- authorized_profile: `standard`
- lite_candidate: `false`
- planning obligation:
  - Standard profile として、runtime behavior / docs / tests / skill / template / provider asset の統合確認を要求する。
  - `lite_candidate` による obligation reduction は行わない。
