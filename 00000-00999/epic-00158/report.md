---
種別: レポート（Epic）
ID: "epic-00158"
タイトル: "Agent Workflow PDCA Hardening"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00158 Agent Workflow PDCA Hardening — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)

- 現在地（何が完了し、何が未完か）:
  - Epic requirement draft を作成し、既存の調査、議論サマリー、accepted ADR を requirement へ採用した。
  - Requirement phase では、scope / non-scope / acceptance criteria に関する blocking question は残っていない。
  - Fresh `spec-reviewer` requirement gate は pass 済み。
  - `system-architect` の delegated design draft を採用し、canonical `design.md` へ反映した。
  - Fresh `spec-reviewer` design gate は pass 済み。
  - `implementation-planner` の delegated plan draft を採用し、canonical `plan.md` へ反映した。
  - Fresh `spec-reviewer` plan gate は pass 済み。
  - Issue decomposition handoff へ進める状態になった。
- 次のマイルストーン:
  - Plan に従って first-wave issue を作成 / 更新する。
  - 既存 `iss-00159` を T1 specimen として進める。
- ブロッカー:
  - Requirement draft 作成自体のブロッカーはなし。
  - なし。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source / source_role | claim | target_artifact / target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | discussion / orchestrator synthesis | Context surface が薄い・分散していることが主因 | `requirement.md` / 背景、目的、failure mode、scope | 複数の clean research とユーザー補正を統合した synthesis であり、Epic requirement の WHAT / WHY に直接対応するため | medium | `spec-dock/active/epic/discussions/20260605t043350z-disc-agent-workflow-pdca-analysis-summary.md` | main orchestrator | spec-reviewer requirement gate: pass, P2 auditability note only | no | なし |
| EAL-002 | adopted | discussion / orchestrator synthesis | Regression checks は first-wave blocker ではない | `requirement.md` / first wave sequencing、scope、deferred work | ユーザー補正後の issue decomposition synthesis で、regression checks を first-wave blocker にしない判断を明確化しているため | medium | `spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md` | main orchestrator | spec-reviewer requirement gate: pass | no | Epic plan で issue 分割へ反映 |
| EAL-003 | adopted | adr / accepted decision | Skills own workflow spine、docs own details、templates own scaffolds | `requirement.md` / Context surface ownership | accepted ADR として skill / docs / templates の責務分担を固定しているため | high | `spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md` | main orchestrator | spec-reviewer requirement gate: pass | no | 後続 issue の design / plan で trace する |
| EAL-004 | adopted | adr / accepted decision | `spec-dock-clarification` は skill-owned workflow | `requirement.md` / clarification skill-owned workflow | accepted ADR として `spec-dock-clarification` の例外的な skill-owned workflow を固定しているため | high | `spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md` | main orchestrator | spec-reviewer requirement gate: pass | no | Clarification issue の requirement / design / plan で trace する |
| EAL-005 | adopted | adr / accepted decision | First wave issue decomposition と deferred work | `requirement.md` / first-wave issue decomposition | accepted ADR として first-wave issue set と deferred work を固定しているため | high | `spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md` | main orchestrator | spec-reviewer requirement gate: pass | no | Epic plan で issue dependency と acceptance trace へ反映 |
| EAL-006 | partially_adopted | research / external ChatGPT analysis | Clarification grill loop の具体化 | `requirement.md` / clarification use case、acceptance criteria | ChatGPT `じっくり思考 Pro` による分析は `spec-dock-clarification` の workflow spine を具体化する補助証跡として有用。ただし Matt Pocock 氏の原文 exact fidelity は主張しない | medium | `spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md` | main orchestrator | spec-reviewer requirement gate: pass, exact fidelity claim excluded | no | Clarification issue で採用範囲を再確認 |
| EAL-007 | adopted | sub-agent / spec-dock-system-architect | Epic design boundary and context-surface authority model | `design.md` / 全体像、コンポーネント、契約、主要フロー、失敗設計、移行、テスト戦略 | Scope-local discussion draft が requirement / ADR / provider surface に trace し、canonical design の HOW / guardrails として妥当な粒度だったため。内容は main orchestrator が再記述して採用 | high | `spec-dock/active/epic/discussions/20260606t012751z-draft-design-agent-workflow-pdca-hardening.md` | main orchestrator | design spec-reviewer pass after consent evidence fix | no | なし |
| EAL-008 | partially_adopted | sub-agent / spec-dock-implementation-planner | Epic issue slicing, dependency order, gates, deferred PDCA work | `plan.md` / issue list, tranches, dependencies, checkpoints, quality gates, readiness, final exit | Scope-local plan draft が approved requirement/design、ADR 02、existing `iss-00159` に trace し、Epic-level plan として妥当なため採用した。ただし draft に混入した non-existent `E-AC-008` / `E-AC-009` mapping は canonical `requirement.md` に存在しないため棄却し、canonical plan には反映しなかった | high for adopted portions; rejected invalid AC mappings | `spec-dock/active/epic/discussions/20260606t014721z-draft-plan-agent-workflow-pdca-hardening.md` | main orchestrator | plan spec-reviewer pass after partial-adoption evidence fix | no | なし |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は first wave の主目的を context-surface cleanup とし、skill / docs / templates の住み分けを中心に置いた | Runtime gates、regression checks、manual harness は later PDCA guard として保持した | 低（low）。副次的な guard / harness / runtime work は deferred と明記済み | pass。Fresh `spec-reviewer` requirement gate は pass、EAL auditability note は非 blocking |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `spec-dock/docs/workflow_epic.md`, `spec-dock/docs/workflow_spec_authoring.md`, `spec-dock/docs/phase_requirement.md`, `spec-dock/active/initiative/requirement.md`, `20260605t043350z-disc`, `20260605t050100z-disc`, `20260605t080509z-adr`, `20260605t080509z-01-adr`, `20260605t080509z-02-adr`, `20260605t053300z-research`, `iss-00159/requirement.md` | Blocking question はなし。Local docs / discussions / accepted ADR / ユーザー補正で scope、non-scope、acceptance criteria を確定できたため、追加 interview は作成しない | 採用（`adopted`）。EAL-001 から EAL-006 の証跡を `requirement.md` へ反映。Reviewer P2 の EAL auditability note はこの report update で補強 | passed。Fresh `spec-reviewer` returned `review_status: pass`; P2 auditability finding was non-blocking | いいえ（no） | Design phase へ進む |
| design | `spec-dock/docs/phase_design.md`, `spec-dock/docs/workflow_epic.md`, `spec-dock/docs/workflow_spec_authoring.md`, accepted ADRs, provider-side skills/docs/templates inventory, `20260606t012751z-draft-design-agent-workflow-pdca-hardening.md` | Blocking question はなし。`workflow_clarification.md` は bridge を既定、full retirement は後段判断として design に記録 | 採用（`adopted`）。EAL-007 の delegated design draft を main orchestrator が canonical `design.md` へ再記述。初回 design review fail の P1/P2 は委任同意 / invocation boundary と phase別使用状態の追記で修正 | passed。Fresh `spec-reviewer` re-review returned `review_status: pass`; stale exception note P2 is non-blocking and fixed in this report update | いいえ（no） | Plan phase へ進む |
| plan | `spec-dock/docs/phase_plan.md`, `spec-dock/docs/phase_plan_epic.md`, `spec-dock/docs/workflow_epic.md`, approved requirement/design, accepted ADRs, `iss-00159/requirement.md`, `20260606t014721z-draft-plan-agent-workflow-pdca-hardening.md` | Blocking question はなし。Issue slicing の粒度、`workflow_clarification.md` retirement、manual smoke 粒度は non-blocking defaults を plan に記録 | 部分採用（`partially_adopted`）。EAL-008 の delegated plan draft を main orchestrator が canonical `plan.md` へ再記述。Draft の non-existent `E-AC-008` / `E-AC-009` mapping は棄却し、canonical plan には反映していない | passed。Fresh `spec-reviewer` re-review returned `review_status: pass` after partial-adoption evidence fix | いいえ（no） | Issue decomposition handoff へ進む |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

- 委任 authoring の使用:
  - requirement: not used
  - design: used (`spec-dock-system-architect`)
  - plan: used (`spec-dock-implementation-planner`)
- 未使用の場合:
  - Requirement draft は main orchestrator が手動で作成した。Sub-agent / delegated authoring draft を requirement phase promotion evidence として使用していない。
- 使用した場合:
  - Design draft は、ユーザーの「サブエージェントと協力して、スペックレビュアー、システムアーキテクト、インプリメンテーションプランナーと協力」という明示指示を、current repo/worktree、active epic、this session、named role `system-architect` に限定した workflow-scoped delegation consent として扱った。
  - Scope-local discussion direct-write consent は design draft invocation 単位で限定し、canonical docs / implementation / tests / package/config / `.agents` / `.codex` / `.github` / `.env*` / GitHub mutation / phase promotion / reviewer-pass claim / user への直接質問を禁止した。
  - Allowed write は `spec-dock/active/epic/discussions/` direct child の naming-rule compliant Markdown 1 件だけとした。
  - Invalidation conditions は、requested scope mismatch、non-discussion write、canonical edit、forbidden path/action、reviewer pass claim、phase promotion claim、implementation readiness claim、stale source discovery、または post-run diff guard failure とした。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
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

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | epic-00158 requirement | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | Requirement は手動 authoring | 該当なし | なし（none） | requirement spec-reviewer pass | requirement phase pass |
| spec-dock-system-architect | epic-00158 design | `spec-dock/active/epic/discussions/20260606t012751z-draft-design-agent-workflow-pdca-hardening.md` | `requirement.md`, `report.md`, workflow docs, accepted ADRs, provider skills/docs/templates | `spec-dock/active/epic/design.md`, `spec-dock/active/epic/report.md` | adopted via EAL-007 | `spec-dock/active/epic/design.md`, `spec-dock/active/epic/report.md` | `git diff --check`: pass; no forbidden canonical edits by sub-agent observed | Adopted after main-orchestrator rewrite | None | なし（none） | design spec-reviewer pass after report evidence fix | design phase pass |
| spec-dock-implementation-planner | epic-00158 plan | `spec-dock/active/epic/discussions/20260606t014721z-draft-plan-agent-workflow-pdca-hardening.md` | `requirement.md`, `design.md`, `report.md`, workflow docs, phase plan docs, accepted ADRs, `iss-00159/requirement.md` | `spec-dock/active/epic/plan.md`, `spec-dock/active/epic/report.md` | partially_adopted via EAL-008 | `spec-dock/active/epic/plan.md`, `spec-dock/active/epic/report.md` | `git diff --check`: pass; no forbidden canonical edits by sub-agent observed | Adopted portions after main-orchestrator rewrite | Draft mappings to non-existent Epic `E-AC-008` / `E-AC-009` were rejected and not reflected | なし（none） | plan spec-reviewer pass after evidence fix | plan phase pass |

### 委任同意 / Invocation Boundary（Delegation Consent / Invocation Boundary）

| 対象 phase | role | consent source | scope | allowed write | forbidden actions / paths | invalidation conditions | evidence destination |
|---|---|---|---|---|---|---|---|
| design | `system-architect` / frontmatter role `spec-dock-system-architect` | User request in this turn: sub-agent cooperation with spec-reviewer, system-architect, implementation-planner for this Epic planning workflow | current repo/worktree `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`, active epic `epic-00158`, this session, design draft only | one new flat Markdown file under `spec-dock/active/epic/discussions/` matching `<ts>-draft-design-<slug>.md` | canonical docs, implementation, tests, package/config, `.agents`, `.codex`, `.github`, `.env*`, GitHub mutation, phase promotion, reviewer-pass claim, user direct question, implementation-readiness claim | scope mismatch, forbidden write/action, missing provenance, stale source, failed diff guard, self-claimed authority, non-discussion side effect | EAL-007 and Delegated Draft Evidence table in this `report.md` |
| plan | `implementation-planner` / frontmatter role `spec-dock-implementation-planner` | User request in this turn: sub-agent cooperation with spec-reviewer, system-architect, implementation-planner for this Epic planning workflow | current repo/worktree `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock`, active epic `epic-00158`, this session, plan draft only | one new flat Markdown file under `spec-dock/active/epic/discussions/` matching `<ts>-draft-plan-<slug>.md` | canonical docs, implementation, tests, package/config, `.agents`, `.codex`, `.github`, `.env*`, GitHub mutation, phase promotion, reviewer-pass claim, issue-ready / issue-finish claim, implementation-readiness claim, user direct question | scope mismatch, forbidden write/action, missing provenance, stale source, failed diff guard, self-claimed authority, non-discussion side effect | EAL-008 and Delegated Draft Evidence table in this `report.md` |

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
| 委任利用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任利用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)

- `20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`: Skills own operational workflow spine、docs own meanings/details、templates own scaffolds/examples という責務分担を accepted とした。
- `20260605t080509z-01-adr-clarification-skill-owned-workflow.md`: `spec-dock-clarification` は例外的に skill-owned workflow とし、`workflow_clarification.md` は bridge / reference とする。
- `20260605t080509z-02-adr-first-wave-issue-decomposition.md`: First wave は context-surface cleanup を優先し、regression checks / harness / runtime gate は後段へ延期する。

## 完了した Issue / PR / Release (必須)

- なし。

## 受け入れ条件（E-AC）の達成状況 (必須)

- E-AC-001: 未評価（証拠: first-wave implementation 未完了）
- E-AC-002: 部分達成（証拠: canonical `plan.md` に ADR 02 と整合する first-wave issue list / dependencies を作成し、fresh plan reviewer pass 済み。Issue 作成 / 完了は未実施）
- E-AC-003: 未評価（証拠: clarification skill rewrite 未実施）
- E-AC-004: 未評価（証拠: skill / docs cleanup 未実施）
- E-AC-005: 部分達成（証拠: この `report.md` の EAL に requirement 採用証跡を記録）
- E-AC-006: 未評価（証拠: shipped asset implementation 未実施）
- E-AC-007: 部分達成（証拠: `requirement.md` の `未確定事項` とこの Spec Authoring Gate に blocking question なしを記録）

## ロールアウト結果（必要なら） (任意)

- 段階公開の状況:
  - 未実施。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)

- `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`:
  - First concrete specimen として `spec-dock-issue-planning` skill の first-read workflow spine を改善する。
- `Align Skill Docs Template Context Surfaces`:
  - Skills / docs / templates 横断で責務分担、導線、矛盾を整理する。
- `Revise spec-dock-clarification as source-grounded grill workflow`:
  - `spec-dock-clarification` を skill-owned workflow とし、`workflow_clarification.md` と discussion templates を整える。
- `Clarify Hub And Leaf Skill Routing Surface`:
  - Hub skill を router + global invariant として整理し、leaf skill の workflow spine へ正しく誘導する。
- `Align Workflow Docs With Skill Spine Boundary`:
  - Docs 側に埋もれた agent operational workflow と、docs 側に残すべき detailed reference を分ける。
- `Align Templates As Scaffolds And Examples`:
  - Templates を scaffold / evidence slot / example surface として整え、compliance authority 化を避ける。
- Deferred:
  - `Add Skill Spine Regression Checks`
  - `Add Manual Workflow Scenario Harness`
  - Runtime gate / `gate status` / issue start-finish guards

## 省略/例外メモ (必須)

- 追加 interview は作成していない。
  - 理由: local docs、discussions、accepted ADR、ユーザー補正を調査した結果、requirement phase の scope / non-scope / acceptance criteria に関する blocking question は残っていないため。
- Fresh `spec-reviewer`:
  - Requirement gate は pass 済み。
  - Design gate は初回 fail 後、委任同意 / invocation boundary と stale claim を修正し、fresh re-review で pass 済み。
  - Plan gate は delegated draft の partial adoption 証跡を修正し、fresh re-review で pass 済み。
