---
種別: 設計書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — Issue 設計書（Strict）

## 1. Strict とする理由

G4 は R0〜G3 の統合品質を保証する closure slice である。workflow readiness、profile template routing、report evidence gate、provider / dogfooding parity の複数 surface を横断するため、Strict として specialist evidence、fresh spec review、issue-local handoff evidence を要求する。

Critical には上げない。G4 は hermetic smoke tests と parity inspection が中心であり、GitHub state mutation、credential、データ削除、forward-only migration、automatic Lite default activation を扱わない。

## 2. 設計要約

- `[N]` G4 は R0〜G3 の本体責務を実装しない。G4 は統合 smoke、parity、evidence fixture によって上流 slice の漏れを検出する。
- `[N]` smoke は public seam を優先する。`new doc` CLI、`workflow status` / `guidance issue-execution`、domain evidence gate、provider / dogfooding asset parity を観測点にする。
- `[N]` Issue-local M99 は Epic 最終品質ゲートへの local closure checkpoint であり、PR Delivery Gate / Merge Preparation Gate を実行しない。
- `[N]` Lite は lightweight を守る。Lite に途中 commit gate や full static analysis 必須を混入させない。
- `[N]` Standard / Strict / Critical では M99 static analysis / lint / tests / report / commit candidate gate を検出できるようにする。

## 3. R0〜G3 との責務境界

| Slice | 所有責務 | G4 の扱い |
|---|---|---|
| R0 / iss-00251 | artifact readiness preflight と false-positive prevention | readiness smoke で回帰を検出する。classifier 本体は変更しない。 |
| G1 / iss-00252 | grade-aware issue planning guidance | profile 別 plan / guidance の存在を smoke する。authoring rule は再定義しない。 |
| G2 / iss-00253 | delegated specialist draft routing と profile template source selection | `new doc draft-design` / `draft-plan` の routing と no-write fail-closed を smoke する。 |
| G3 / iss-00254 | report evidence gate、EAL、delegated draft adoption、fresh review evidence | report evidence fixture で gate の relation を smoke する。parser 本体は変更しない。 |
| G4 / iss-00255 | integrated smoke matrix、provider / dogfooding parity、issue-local handoff evidence | focused tests と report evidence を追加し、Epic final gate へ渡す。 |

## 4. Smoke surface と test owner

| Surface | owner file | 主な観測点 | 対応AC |
|---|---|---|---|
| Lite / Standard+ profile plan smoke | `tests/cli_runtime/test_new.py` | profile template materialization と M99 gate wording | AC-001, AC-002 |
| Draft routing smoke | `tests/cli_runtime/test_new.py` | `authorized_profile` に対応する `templates/issue-profiles/<profile>/{design,plan}.md` source | AC-003 |
| Assurance fail-closed smoke | `tests/cli_runtime/test_new.py` | missing / invalid / stale `.assurance.json` で no-write failure | AC-004 |
| Readiness CLI smoke | `tests/cli_runtime/test_workflow.py` | placeholder / heading-only / stale evidence が ready にならない | AC-005 |
| Evidence domain smoke | `tests/unit/domain/test_workflow_state.py` | EAL、delegated draft evidence、Grade Specialist Evidence Gate、fresh spec review relation | AC-006 |
| Provider / dogfooding parity | `tests/unit/infra/test_init_update.py` | shipped docs / profile templates の mirror parity または明示例外 | AC-007 |
| Report evidence | `report.md` | command、result、skipped reason、residual risk | AC-008 |

新規 test file は原則作らない。既存 owner file の責務境界が崩れる場合だけ plan amendment を行う。

## 5. Interface contract

G4 の smoke は private helper ではなく、次の public / stable seam を観測する。

- `spec-dock new doc draft-design --issue <id>` / `draft-plan`:
  - success 時は discussion file が作成され、source profile template の内容が反映される。
  - fail-closed 時は return code が non-zero になり、discussion file set が変化しない。
- `spec-dock workflow status --format json` / `spec-dock guidance issue-execution`:
  - substantive artifact と report evidence が揃うまで blocked reason を返す。
  - placeholder、heading-only、stale evidence、missing adoption evidence を ready として扱わない。
- `evaluate_report_evidence_gate`:
  - profile ごとに delegated evidence、EAL、Grade Specialist Evidence Gate、fresh review evidence の不足を reason code で区別する。
- provider / dogfooding parity:
  - provider source of truth と dogfooding mirror の profile templates / workflow docs が意図した内容で整合する。

## 6. 互換性と非対象

- Existing `draft-requirement`、Initiative / Epic `draft-design` / `draft-plan` behavior は変更しない。
- Existing strict-legacy Issue execution は維持する。
- G4 は automatic Lite default を有効化しない。
- G4 は live GitHub repository、external telemetry backend、PR observation policy を必須にしない。
- G4 で upstream production behavior gap が見つかった場合、G4 内で本体修正を吸収せず、owning slice への repair または Epic follow-up へ戻す。

## 7. Provider / dogfooding parity contract

Parity は byte equality を無条件に要求しない。runtime / shipped scaffold の source of truth は `src/spec_dock/assets/spec_dock/...` であり、dogfooding 側 `spec-dock/...` は installed mirror / validation surface である。

G4 では次を確認する。

- `templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` が provider と dogfooding の両方に存在する。
- grade-aware workflow docs が provider と dogfooding で意味的に一致する。
- 既知の generated / local-only difference がある場合は、test または report に明示例外として残す。

## 8. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 | Lite / Standard+ profile plan smoke の Lite negative contract |
| AC-002 | Lite / Standard+ profile plan smoke の Standard+ positive contract |
| AC-003 | Draft routing smoke |
| AC-004 | Assurance fail-closed smoke |
| AC-005 | Readiness CLI smoke |
| AC-006 | Evidence domain smoke |
| AC-007 | Provider / dogfooding parity contract |
| AC-008 | Report evidence contract |

## 9. Epic single PR boundary

`iss-00255` の M99 は local closure checkpoint である。G4 完了後、Epic `plan.md` の「Epic 最終品質ゲート（単一 PR 前）」で fresh spec review、code review、QA review、required tests、PR body evidence を集約し、その後に Epic #224 corrective tranche の単一 PR を作成する。
