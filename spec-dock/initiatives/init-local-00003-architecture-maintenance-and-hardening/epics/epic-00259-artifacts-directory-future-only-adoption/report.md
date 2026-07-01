---
種別: レポート（Epic）
ID: "epic-00259"
タイトル: "Artifacts Directory Future Only Adoption"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00259 Artifacts Directory Future Only Adoption — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - Phase 2 policy clarification interviews were completed.
  - Accepted ADR `20260701t055644z-adr` records the `artifacts/` future-only command unification decision.
  - Canonical `requirement.md`, `design.md`, and `plan.md` reflect the accepted ADR as approved Epic planning artifacts.
  - Fresh requirement `spec-reviewer` returned `pass` after two failed review/fix loops.
  - Design `spec-reviewer` returned `pass`; its non-blocking P2 wording clarification was fixed.
  - Plan `spec-reviewer` returned `fail` once; both P1 findings were fixed by rejecting unguarded delegated plan evidence as promotion evidence and assigning `draft-*` assurance/profile migration to the command/runtime candidate slice.
  - Fresh plan `spec-reviewer` re-review returned `pass` with `findings=[]`.
  - Concrete Issues `iss-00261` through `iss-00268` were created and linked to GitHub `#261` through `#268`.
  - Dependency edges were added with `spec-dock deps add`; `.meta.json` was not manually edited.
  - Each Issue now has an approved `requirement.md` plus draft `design.md` and draft `plan.md` created as an integrated cross-Issue package.
  - `assurance classify --stage requirement` and `assurance compose --artifact all` were run for the initially created Issues; after `iss-00261` was abolished, changed executable Issues were reclassified and remain `standard`.
  - Fresh cross-Issue package `spec-reviewer` returned `pass` with `findings=[]`.
  - User review identified `iss-00261` as an Epic foundation decision rather than an executable Issue.
  - Accepted ADR `20260701t072851z-adr` now owns the artifact domain / filename / draft template routing contract at Epic level.
  - `iss-00261` / GitHub `#261` was closed and local node was deleted; remaining executable Issues are `iss-00262` through `iss-00268`.
  - Dependency metadata was corrected with `spec-dock deps remove`; Issue docs and Epic plan now reference the Epic ADR instead of depending on `iss-00261`.
- 次のマイルストーン:
  - Run fresh package validation/review after this plan correction, then begin staged Epic execution from `iss-00262`, preserving the one Epic-level PR delivery policy.
- ブロッカー:
  - None for Issue decomposition / cross-Issue planning package.

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | interview | ADR | Eight user-approved clarification interviews were synthesized into the Epic-level command unification ADR. | `discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md`; `discussions/20260701t043624z-interview-delegated-authoring-artifact-boundary.md`; `discussions/20260701t044839z-interview-blank-versus-scratch-artifact-template.md`; `discussions/20260701t050929z-interview-adr-artifact-boundary.md`; `discussions/20260701t051314z-interview-future-adr-command-surface.md`; `discussions/20260701t052324z-interview-draft-artifact-command-boundary.md`; `discussions/20260701t052702z-interview-new-doc-removal-failure-mode.md`; `discussions/20260701t055220z-interview-legacy-discussions-validation-boundary.md`; `artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md` | Completed; ADR reflected into canonical requirement/design/plan and passed reviewer gates. |
| EAL-002 | adopted | ADR | requirement.md / design.md / plan.md / report.md | Accepted ADR is the authoritative policy source for future `artifacts/`, `new artifact`, `new doc` removal, ADR/draft/delegated output inclusion, and legacy `discussions/` preservation. ADR `reflected_to` metadata has been updated to match canonical adoption. | `artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md`; `requirement.md`; `design.md`; `plan.md`; `report.md` | Completed for Epic planning; use approved plan for future Issue creation. |
| EAL-003 | rejected | implementation-planner | plan.md | Planner evidence was considered but not adopted as promotion evidence because the delegated draft records `diff_guard_result: not_run`. The canonical plan is manually authored by the main orchestrator from the approved requirement/design, accepted ADR, interviews, ZIP baseline, and repo inspection; overlapping slicing ideas are not claimed as delegated adoption. | `artifacts/20260701t060722z-draft-plan-implementation-planner-issue-slicing-evidence.md`; `plan.md` | No action for this phase; future delegated plan evidence must pass the artifact-scope diff guard before adoption. |
| EAL-004 | rejected | system-architect | design.md | System-architect output was produced in legacy `discussions/` after the accepted ADR moved delegated output to `artifacts/`, and the created file remained template-like rather than substantive. It is retained as historical evidence only and is not used as promotion evidence. | `discussions/20260701t060637z-disc-artifacts-future-only-architecture-evidence.md` | No action; canonical design is main-orchestrator-authored from ADR, repo inspection, and ZIP/reference evidence. |
| EAL-005 | partially_adopted | command output | plan.md / issues/* | Initial Issue creation output established concrete IDs, GitHub links, and scaffold paths for `iss-00261` through `iss-00268`; later review superseded `iss-00261` because it represented an Epic foundation decision rather than an executable slice. | `new issue` command outputs for `iss-00261` through `iss-00268`; `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`; `plan.md` | Superseded by EAL-008 for `iss-00261`; remaining executable Issues are `iss-00262` through `iss-00268`. |
| EAL-006 | adopted | command output | plan.md / issue .meta.json | Dependency edges were added via `spec-dock deps add` according to the approved Epic dependency map. | `deps add` command outputs; `.meta.json` generated by runtime | Completed; no direct metadata edits. |
| EAL-007 | partially_adopted | assurance command output | issue requirement/design/plan drafts | Runtime classified the initially created Issues as `authorized_profile: standard` and composed design/plan/report scaffolds before manual Issue-specific drafting. Classification/scaffold evidence for abolished `iss-00261` is historical only; remaining executable Issues retain `standard` authorization. | `assurance classify --stage requirement`; `assurance compose --artifact all`; `.assurance.json` under remaining executable Issues | Re-ran requirement classification for changed executable Issues after `iss-00261` abolition; all remained `standard`. |
| EAL-008 | adopted | user review / consultant / ADR | requirement.md / design.md / plan.md / issues/* | User correctly identified that `iss-00261` owned an Epic-wide foundation decision. The contract was promoted to accepted Epic ADR, `iss-00261` was abolished, and executable implementation responsibility was redistributed across `iss-00262` through `iss-00268`. Consultant agreed that the dependency graph should remove `iss-00261` and use the Epic ADR as the contract source. | `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`; `close iss-00261`; `delete iss-00261`; `deps remove` command outputs; consultant notification `019f1c93-83c5-7bc2-abbb-e58110ed86a7` | Run validation and fresh package spec review before implementation handoff. |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is command unification and future artifact creation under `artifacts/`. | Existing `discussions/` remain valid and strictly validated, but are not the future creation surface. | low | requirement, design, and plan reviewer gates passed after fixes |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| clarification -> ADR | ZIP pack, active Epic scaffold, workflow clarification docs, decision routing docs, ADR workflow, current runtime/docs/tests around `new doc`, `discussions`, ADR mirror, delegated authoring, draft artifacts, validation. | Answered in eight interview artifacts. | adopted into ADR `20260701t055644z-adr` | not applicable; ADR accepted from user-approved interviews | no | Completed; ADR is the policy source for Epic planning. |
| requirement | workflow_epic, workflow_spec_authoring, phase_requirement, decision-routing, active initiative docs, accepted ADR, eight interviews, ZIP pack as superseded baseline, current runtime/docs/tests around new doc/discussions/drafts/validation. | No scope-affecting open questions remain. First reviewer found ambiguous custom migration hint for `new doc` and missing AC coverage for full artifact catalog. Second reviewer found ADR authority ambiguity inside `artifacts/` and missing old-node on-demand setup AC. | adopted ADR into requirement; fixed hard-removal wording, catalog-wide AC, accepted ADR authority exception, and old-node on-demand setup AC. | passed on fresh second re-review; findings=[] | no | Promoted to design phase; run fresh design reviewer. |
| design | Approved requirement, workflow_epic, workflow_spec_authoring, phase_design, decision-routing, accepted ADR, interviews, current delegated authoring code, current new doc/discussion implementation, ZIP pack as superseded baseline. | No new scope question. First reviewer found draft-* scope ambiguity, delegated authoring boundary under-specification, and stale ADR reflected_to metadata. Re-review returned pass with one P2 wording clarification about forbidden side effects. | fixed draft-* as issue-only no-write unsupported for initiative/epic; specified delegated authoring artifacts direct-child guard and tests; updated ADR reflected_to; clarified that forbidden side effects are rejected even if git-ignored. | passed on fresh re-review; non-blocking P2 fixed | no | Promoted to plan phase; plan reviewer gate completed. |
| plan | Approved requirement/design, workflow_epic, workflow_spec_authoring, phase_plan, phase_plan_epic, decision-routing, accepted ADR, interviews, current runtime/docs/tests, ZIP pack as superseded baseline. | No scope-affecting open questions remain. First reviewer found unguarded implementation-planner evidence adopted despite `diff_guard_result: not_run`, and found that `draft-*` assurance/profile migration lacked an explicit candidate Issue owner. | rejected implementation-planner evidence as promotion evidence and clarified that the canonical plan is manually authored; assigned `draft-requirement` / `draft-design` / `draft-plan` `.assurance.json` / authorized profile preflight migration and no-write tests to candidate-issue-03. | passed on fresh re-review; findings=[]; overall_confidence_score=0.9 | no | Promoted; concrete Issue creation completed in subsequent decomposition step. |
| issue decomposition | Approved Epic plan, workflow_epic handoff, workflow_issue, spec-dock-issue-planning guidance, phase_plan_issue, authoring/issue-plan, runtime `new issue`, `deps add`, `assurance classify`, `assurance compose`. | Runtime issue-planning guidance reports `state: no-active` / `issue-start-required`; for this cross-Issue Epic decomposition package, individual issue execution start is intentionally deferred. User later identified `iss-00261` as decision-only. | initially created Issues `iss-00261` through `iss-00268`; then abolished `iss-00261`, promoted its policy content to accepted Epic ADR, corrected dependencies, and retained executable Issues `iss-00262` through `iss-00268`. | fresh re-review pending after correction | no | Run validation and package spec review; then start staged execution with `iss-00262`. |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - This Epic's accepted ADR changes future delegated output to target scope `artifacts/` direct child.
  - Legacy `discussions/` delegated output from stale workflow instructions is historical / non-compliant for promotion evidence unless explicitly adopted through this ledger.
  - filename policy follows the artifact filename contract being planned by this Epic.
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | epic-00259 | `discussions/20260701t060637z-disc-artifacts-future-only-architecture-evidence.md` | ADR, interviews, workflow docs, ZIP pack, repo runtime/docs/tests | `design.md`, `report.md` | rejected | [] | not_run | rejected; legacy output location and template-like content | all canonical claims | none; not used for promotion | not reviewed as design evidence | not promotion evidence |
| implementation-planner | epic-00259 | `artifacts/20260701t060722z-draft-plan-implementation-planner-issue-slicing-evidence.md` | ADR, interviews, workflow docs, ZIP pack, repo runtime/docs/tests | `plan.md`, `report.md` | rejected | [] | not_run | not integrated; canonical plan manually authored by the main orchestrator | all promotion claims | none; not used for promotion | plan reviewer rejected adoption with unrun diff guard | not promotion evidence |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)
- `artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md`: Future artifact creation is unified under `new artifact`, including ADR, draft artifacts, and delegated authoring outputs; `new doc` is removed; existing `discussions/` remain valid and strictly validated.
- `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`: Artifact domain / filename / draft template routing is an Epic-level contract; `iss-00261` / `#261` is abolished; draft-* reuse existing requirement/design/plan templates and Issue grade/profile-aware selection.

## 完了した Issue / PR / Release (必須)
- iss-xxxx-...: Done（PR: ...）
- ...

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: Pass / Fail（証拠: ...）
- E-AC-002: ...

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- iss-xxxx-...:
  - ...

## 省略/例外メモ (必須)
- 該当なし
