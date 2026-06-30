---
種別: 要件定義書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
関連GitHub: ["#254"]
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 要件定義

## 1. 目的

Grade-aware Issue authoring workflow に、fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist adoption、grade-specific specialist / fallback evidence、report evidence gate を接続する。これにより、canonical phase promotion と issue execution readiness が、draft、stale review、missing adoption evidence、または grade-specific evidence 不足のまま成立しないようにする。

## 2. 背景

Epic #224 の corrective tranche では、R0 が artifact readiness を fail-closed にし、G1 が grade-aware issue planning guidance を定義し、G2 が Issue `draft-design` / `draft-plan` を `authorized_profile` 対応 profile template source に接続した。G3 はその上で、delegated specialist が作った draft や review 結果を canonical artifact / issue readiness に採用するための証跡契約を固める。

現状の `workflow_spec_authoring.md`、phase docs、report template には fresh `spec-reviewer`、Evidence Adoption Ledger、delegated draft evidence の概念が存在する。一方で、`workflow status` / `guidance issue-execution` の readiness は requirement/design/plan の substantive/executable 判定が中心であり、report evidence の missing / stale / blocked 状態を execution handoff 前に十分に露出していない。G3 では docs/template と runtime readiness hook を揃え、後続 G4 の smoke tests が確認できる状態にする。

## 3. 用語

| 用語 | 意味 |
|---|---|
| fresh `spec-reviewer` | 最新の canonical requirement/design/plan/report 候補に対して、`review_status: pass` を返した spec review。過去版、draft-only review、waiver、provisional、unavailable、denied は pass ではない。 |
| Evidence Adoption Ledger | delegated draft、research、reviewer finding、command output を canonical artifact や実装判断へ採用する際の採否台帳。unresolved `stale` / `blocked` は downstream gate を止める。 |
| Delegated Draft Evidence | system-architect / implementation-planner などが scope-local `discussions/` に作る draft evidence。canonical authority、reviewer pass、phase completion、implementation readiness を自己主張しない。 |
| Grade Evidence Gate | Standard の specialist use / skip reason、Strict / Critical の specialist evidence / unavailable / manual fallback evidence を report で追跡する gate。 |
| Report Evidence Gate | `report.md` の EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status、Grade Evidence Gate を読み、phase promotion / issue readiness の前提不足を fail-closed にする gate。 |

## 4. スコープ

対象:

- provider-side docs/templates:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- dogfooding mirror の対応箇所:
  - `spec-dock/docs/...`
  - `spec-dock/templates/issue/report.md`
- runtime readiness hook:
  - `workflow status`
  - `guidance issue-execution`
  - 必要な domain helper
- focused tests:
  - report evidence gate
  - missing / stale / blocked evidence readiness
  - docs/template scaffold contract

対象外:

- G2 で実装済みの `new doc draft-design` / `draft-plan` routing の再設計
- R0 の placeholder classifier / artifact readiness preflight の全面再設計
- PR observation、GitHub Codex review、code-reviewer / qa-reviewer の PR policy 再設計
- report evidence 全体の JSON schema 化
- historical delegated-authoring artifacts の削除、rename、validation failure 化

## 5. 観測可能な成果

- `report.md` template から、EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status、grade-specific specialist / fallback evidence の記録先が確認できる。
- docs から、fresh `spec-reviewer` が Lite を含む全 grade で省略不可であることが分かる。
- docs から、Standard では specialist 使用または skip reason、Strict / Critical では specialist evidence または unavailable / manual fallback evidence が必要であることが分かる。
- `workflow status --format json` と `guidance issue-execution` が、substantive requirement/design と executable plan があっても、report evidence gate 未充足時には `ready` を返さない。
- unresolved `stale` / `blocked` EAL entry は issue readiness を止める。
- fresh reviewer evidence が missing / stale / non-pass の場合は issue readiness を止める。
- delegated draft 使用を主張しているのに adoption evidence がない場合は issue readiness を止める。
- Issue 単位の PR は作成せず、G3 完了後の local checkpoint commit を G4 / iss-00255 へ渡せる。

## 6. 受け入れ条件

| ID | 条件 | 検証 |
|---|---|---|
| AC-001 | Phase promotion と issue execution readiness には fresh `spec-reviewer` pass が必要であることを docs/template/runtime guidance が示す。 | docs/template inspection、`guidance issue-execution` negative/positive tests |
| AC-002 | Delegated draft adoption は Evidence Adoption Ledger と Delegated Draft Evidence に記録され、EAL なしに採用済みと扱えない。 | report template tests、runtime missing adoption evidence tests |
| AC-003 | stale draft、stale reviewer、unresolved `stale` / `blocked` EAL entry は promotion / readiness evidence として使えない。 | domain/CLI negative tests |
| AC-004 | Standard の specialist use / skip reason と、Strict / Critical の specialist evidence / unavailable / manual fallback evidence が report evidence contract に入る。 | report template tests、CLI negative/positive tests |
| AC-005 | missing adoption evidence / reviewer evidence / grade evidence は R0 の artifact readiness と矛盾しない別 reason code として readiness を block する。 | `workflow status` / `guidance issue-execution` tests |
| AC-006 | Discussion draft は authority / adoption / reviewer pass / phase completion / issue readiness を自己主張できない方針を維持し、G3 の docs/template でもそれを弱めない。 | docs inspection、既存 delegated draft / new doc tests の維持 |
| AC-007 | G3 の変更は G2 draft routing、PR observation policy、issue finish GitHub close policy を変更しない。 | focused regression / diff inspection |
| AC-008 | Provider-side source of truth と dogfooding mirror の docs/template は整合する。 | parity inspection |

## 7. 制約

- `authorized_profile` は obligation authority であり、`lite_candidate` は obligation を下げる根拠にしない。
- Fresh reviewer gate は user waiver / manual fallback / unavailable 証跡で pass 扱いにしない。
- Manual fallback は証跡であり成功ではない。blocking でないと判断するには理由、対象 scope、確認 source、残リスク、fresh review 提示 evidence を report に残す。
- Runtime hook は report template の stable headings / accepted tokens を最小限に読む。自由文の意味推論に広げない。
- Historical delegated-authoring artifacts は grandfathered evidence として残し、G3 の新契約だけを理由に破壊しない。

## 8. 親 Epic との対応

- `E-RQ-022`: grade-aware authoring guidance / delegated specialist / draft routing / fresh review / evidence gate のうち、fresh review / evidence gate subset。
- `E-AC-022`: grade-aware Issue authoring workflow の review / evidence subset。
- Epic design: `Spec Authoring Evidence Gate`
- Epic plan: `G3 — Add Grade-Aware Spec Review And Evidence Gates`

## 9. 完了条件

- AC-001〜AC-008 が `report.md` の closure evidence で閉じている。
- `guidance issue-execution` が G3 evidence gate の missing / stale / blocked 状態を `may_execute_approved_plan: false` として示せる。
- Focused tests、`make lint`、`./spec-dock/scripts/spec-dock validate`、`git diff --check` が通る。
- Final QA / code / spec review が pass している。
- `issue finish` が完了し、個別 PR を作らず G4 / `iss-00255` へ渡せる clean checkpoint commit がある。
