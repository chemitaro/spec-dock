---
種別: 設計書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 設計書（Strict）

## 1. Strict とする理由

G3 は phase promotion と issue execution readiness の workflow contract に触れる。誤って reviewer pass、delegated draft adoption、grade evidence を緩く扱うと、未完成の仕様書や stale evidence から実装へ進めてしまうため、Strict として specialist draft、fresh spec review、focused negative tests、final QA/code/spec gate を必須にする。

## 2. 設計方針

- Report evidence gate は `report.md` の structured sections を読み、missing / stale / blocked / non-pass evidence を fail-closed に扱う。
- Runtime は agent を起動しない。fresh `spec-reviewer` を実行したという証跡を report から読むだけにする。
- G3 の runtime hook は `workflow status` / `guidance issue-execution` の readiness 前段に置く。`issue finish` 既存 EAL gate は再設計しない。
- Docs/templates は runtime が読む stable headings / tokens と、人間/agent が記録する evidence destination を一致させる。
- Provider-side assets を source of truth とし、dogfooding mirror は検証対象として整合させる。
- G2 の profile-aware draft routing と PR observation policy は変更しない。

## 3. コンポーネント設計

| コンポーネント | 責務 | 配置 |
|---|---|---|
| Report Evidence Template | EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status、Grade Specialist Evidence、Final Spec Review Gate の記録先を提供する | `src/spec_dock/assets/spec_dock/templates/issue/report.md` |
| Authoring Docs | fresh reviewer、delegated adoption、grade evidence、fallback evidence、no self-claim の authoring contract を説明する | `workflow_spec_authoring.md`, `phase_requirement.md`, `phase_design.md`, `phase_plan_issue.md`, `workflow_issue.md` |
| Report Evidence Parser | report text の stable sections / rows / tokens を読み、readiness に必要な evidence を判定する | domain helper |
| Workflow Readiness Hook | requirement/design/plan readiness と assurance authority の後、ready を返す前に report evidence gate を評価する | `application/workflow.py` |
| Presentation | block reason と details を JSON / Markdown guidance に露出する | existing `WorkflowState.details` |
| Tests | docs/template structure、negative/positive readiness、EAL regression、dogfooding parity を確認する | `tests/cli_runtime/test_workflow.py`, `tests/unit/domain`, `tests/unit/infra/test_init_update.py` |

## 4. Report Evidence Gate

### 4.1 入力

- active issue directory
- `report.md` text
- `authorized_profile`
- current workflow target:
  - issue planning
  - issue execution
  - issue finish
- existing artifact readiness:
  - requirement substantive
  - design substantive
  - plan executable

### 4.2 必須 evidence

| Evidence | 必須条件 | block reason |
|---|---|---|
| Evidence Adoption Ledger | unresolved `stale` / `blocked` がない | `adoption-evidence-stale-or-blocked` |
| Delegated Draft Evidence | delegated use が claimed の場合、draft path、lifecycle state、integration result、diff guard、promotion decision がある | `delegated-draft-evidence-missing` |
| Spec Authoring Gate | requirement/design/plan promotion で latest canonical artifacts に対する reviewer verdict が exact `pass` または `passed` | `report-spec-authoring-gate-invalid` |
| Grade Specialist Evidence | Standard では used または skipped-with-reason、Strict/Critical では used または unavailable/manual fallback evidence がある | `grade-specialist-evidence-missing` |
| Reviewer Gate Status | final execution handoff では `spec-reviewer` が fresh/passed。code/QA は final quality gate に置く | `spec-reviewer-evidence-missing` |

### 4.3 pass / fail の扱い

- exact `pass` または `passed` だけを pass とする。
- `failed`, `unavailable`, `denied`, `waived`, `provisional`, `stale`, 空欄は pass ではない。
- `not used` は、Standard の specialist skip reason として十分な根拠がある場合だけ non-blocking。
- Strict / Critical の `unavailable` / `manual fallback` は、利用不可理由、代替調査、採否判断、fresh spec-reviewer への提示 evidence が揃う場合だけ non-blocking。Reviewer pass の代替にはならない。

## 5. Domain Helper 案

### 5.1 型

```text
ReportEvidenceGateResult
  ok: bool
  reason_code: str
  details: tuple[str, ...]
```

### 5.2 判定対象

```text
report_evidence_status(report_text, profile, purpose)
  -> ReportEvidenceGateResult
```

`purpose` は当面 `issue_execution` を主対象にする。`issue_finish` は既存 `require_evidence_adoption_ledger_clear` と `require_delegated_artifacts_authorized` があるため、G3 では docs/template と tests の整合に留める。

### 5.3 Parser 方針

- Markdown の自由文意味推論はしない。
- 既存 EAL parser は再利用する。
- 新規 helper は、特定 section の table row / token を最小限に読む。
- Missing section / missing row は fail-closed。
- Historical scaffold template の placeholder row は pass ではない。

## 6. Workflow Readiness Hook

`application/workflow.py` の `_resolve_state` で、次の順序を維持する。

1. active issue resolve
2. requirement readability / substantiveness
3. assurance authority
4. design substantive
5. plan executable
6. report evidence gate
7. `ready`

`report evidence gate` が fail の場合:

- `WorkflowState.kind = "blocked"`
- `reason_code = gate.reason_code`
- `artifact_readiness = "substantive"`
- `details = gate.details`
- `may_execute_approved_plan = false`

これにより、R0 の artifact readiness と G3 の evidence readiness を混同しない。

## 7. Docs / Template 設計

### 7.1 Issue report template

追加 / 強化する section:

- Grade Specialist Evidence Gate
- Spec Authoring Gate の freshness semantics
- Reviewer Gate Status の accepted states
- Final Spec Review Gate と phase promotion gate の違い
- Evidence Adoption Ledger unresolved statuses の downstream block

### 7.2 Workflow docs

`workflow_spec_authoring.md`:

- phase promotion と issue readiness は fresh `spec-reviewer` + report evidence gate を必要とする。
- delegated draft は EAL 採用前に authority を持たない。

`phase_requirement.md` / `phase_design.md` / `phase_plan_issue.md`:

- Standard skip reason と Strict/Critical fallback evidence の report destination を明確にする。

`workflow_issue.md`:

- issue execution handoff 前に report evidence gate が missing/stale evidence を incomplete として扱う。
- final PR/code-review policy とは別 gate であることを明確にする。

## 8. テスト設計

| Test ID | 対象 | 検証内容 |
|---|---|---|
| tc-g3-001 | report template | Grade Specialist Evidence Gate と fresh reviewer evidence slots が provider/dogfooding report template に存在する |
| tc-g3-002 | workflow negative | executable plan があっても fresh spec-reviewer evidence がなければ `guidance issue-execution` は blocked |
| tc-g3-003 | workflow negative | EAL に unresolved `stale` / `blocked` がある場合は blocked |
| tc-g3-004 | workflow negative | Strict profile で specialist/fallback evidence が missing の場合は blocked |
| tc-g3-005 | workflow positive | fresh spec-reviewer、resolved EAL、Strict fallback/used evidence が揃うと ready |
| tc-g3-006 | docs parity | provider docs/templates と dogfooding mirror の G3 wording が整合する |
| tc-g3-007 | regression | G2 `new doc` routing tests と existing EAL lifecycle tests が維持される |

## 9. 非対象 / 境界

- `spec-reviewer` sub-agent の実行自体を runtime command に組み込まない。
- GitHub PR review / code-reviewer / QA reviewer policy を変更しない。
- issue finish の GitHub close / active clear lifecycle を再設計しない。
- Report evidence を完全 schema 化しない。
- Existing strict-legacy issue をすべて即時 blocked にするような広すぎる enforcement は避ける。Active issue の `authorized_profile` が取得できる場合を主対象にし、strict-legacy missing assurance は現行挙動と矛盾しないよう扱う。

## 10. リスクと対策

| リスク | 対策 |
|---|---|
| Markdown parser が brittle になる | stable headings / tokens に限定し、tests で template contract を固定する |
| final review gate と phase promotion gate が混線する | docs/template で用途を分け、runtime hook は issue execution readiness に限定する |
| Existing reports が template row のままで pass してしまう | placeholder-like rows / empty evidence は pass にしない |
| Strict/Critical fallback が reviewer pass の代替に見える | fallback は evidence であり、fresh `spec-reviewer` pass とは別に必須と書く |
| Dogfooding mirror drift | provider / dogfooding parity inspection と focused template tests を実行する |

## 11. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 | Report Evidence Gate、Workflow Readiness Hook、Spec Authoring Gate |
| AC-002 | EAL / Delegated Draft Evidence template and parser |
| AC-003 | EAL unresolved block、freshness semantics、negative tests |
| AC-004 | Grade Specialist Evidence Gate |
| AC-005 | `WorkflowState` blocked reason codes |
| AC-006 | docs/template no self-claim wording and existing delegated draft guard |
| AC-007 | non-goals / regression tests |
| AC-008 | provider/dogfooding parity |

## 12. 採用した delegated draft

この設計は次の delegated draft を source evidence として採用する。ただし draft 自体は canonical authority ではなく、本設計への再記述と `report.md` の EAL により採用を成立させる。

- `discussions/20260630t180146z-draft-design-g3-evidence-gate-design-proposal.md`
- `discussions/20260630t180152z-disc-g3-implementation-plan-draft.md`
