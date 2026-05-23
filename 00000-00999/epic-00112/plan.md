---
種別: 計画書（Epic）
ID: "epic-00112"
タイトル: "Delegated Authoring Architecture for Spec Workflow"
関連GitHub: ["#112"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00112 Delegated Authoring Architecture for Spec Workflow — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001 Canonical artifact ownership invariant
  - E-RQ-002 Draft-only delegated authoring mode
  - E-RQ-003 Delegation consent and scope contract
  - E-RQ-004 Delegated design authoring contract
  - E-RQ-005 Delegated plan authoring contract
  - E-RQ-006 Delegated draft artifact lifecycle
  - E-RQ-007 Report evidence integration
  - E-RQ-008 Independent spec-reviewer treatment
  - E-RQ-009 Provider-first and dogfooding parity
  - E-RQ-010 Host adapter boundary
  - E-RQ-011 Failure mode handling
  - E-RQ-012 Dogfooding pilot and future write-capable readiness
- E-AC:
  - E-AC-001 Ownership contract
  - E-AC-002 Draft-only safety
  - E-AC-003 Delegated draft lifecycle
  - E-AC-004 Delegated design gate
  - E-AC-005 Delegated plan gate
  - E-AC-006 Reviewer independence
  - E-AC-007 Provider/consumer parity
  - E-AC-008 Dogfooding pilot
  - E-AC-009 Failure mode evidence

## Issue 分割方針
- 分割原則:
  - Policy / schema / role / gate / host / dogfooding を分離し、各 Issue が一つの contract boundary を閉じる。
  - Earlier Issues define authority and evidence before later Issues add callable roles or pilot the workflow.
  - Provider-side source of truth is updated before dogfooding parity work.
  - `.github/agents` / Copilot agent、write-capable delegation、runtime validation、role registry は Issue 化しない。
- 例外:
  - If `.codex/agents` path / syntax cannot be verified in Issue 005, the Issue may close with adapter contract + documented uncertainty, but must not claim verified host integration.

## Issue 一覧（順序 / tranche 付き）
- Issue 001: delegated authoring policy foundation
  - 目的:
    - `workflow_spec_authoring.md` に canonical ownership、draft-only authoring delegation、consent granularity、forbidden actions、manual fallback を固定する。
  - 推奨 title / slug:
    - title: `Delegated Authoring Policy Foundation`
    - slug: `delegated-authoring-policy-foundation`
  - 成果物:
    - Provider docs update under `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - Dogfooding docs parity under `spec-dock/docs/workflow_spec_authoring.md`
    - Report evidence update for policy decision.
  - tranche:
    - T1 Policy foundation
  - closes:
    - E-RQ-001, E-RQ-002, E-RQ-003 baseline
    - E-AC-001, E-AC-002 baseline
  - 依存:
    - none
  - Issue readiness:
    - Must include explicit non-scope for write-capable delegation and `.github/agents`.
    - Must preserve existing manual authoring path and fresh reviewer pass rule.

- Issue 002: delegated draft artifact and report evidence schema
  - 目的:
    - Delegated draft lifecycle、structured draft artifact、report evidence、report template / active-none surfaces を固定する。
  - 推奨 title / slug:
    - title: `Delegated Draft Evidence Schema`
    - slug: `delegated-draft-evidence-schema`
  - 成果物:
    - Draft lifecycle and artifact contract in provider docs.
    - Report evidence contract in workflow / phase docs.
    - Provider report templates:
      - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
      - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
    - Dogfooding parity for corresponding `spec-dock/templates/**/report.md` and `spec-dock/system/active-none/**/report.md`.
  - tranche:
    - T1 Evidence foundation
  - closes:
    - E-RQ-006, E-RQ-007, E-RQ-011
    - E-AC-003, E-AC-009
  - 依存:
    - Issue 001
  - Issue readiness:
    - Must represent `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`.
    - Must include expected verdict, allowed next action, evidence path, and promotion eligibility for every failure mode.

- Issue 003: role skill assets for delegated design and plan authors
  - 目的:
    - `spec-dock-system-architect` と `spec-dock-implementation-planner` の provider-first role skills を追加する。
  - 推奨 title / slug:
    - title: `Delegated Author Role Skills`
    - slug: `delegated-author-role-skills`
  - 成果物:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
    - Dogfooding `.agents/skills/...` parity.
    - Managed asset / init-update tests as needed.
  - tranche:
    - T2 Role capability
  - closes:
    - E-RQ-004, E-RQ-005
    - E-AC-004, E-AC-005 role-contract baseline only
  - 依存:
    - Issue 001
    - Issue 002
  - Issue readiness:
    - `system-architect` output must include the design draft required sections from `design.md`.
    - `implementation-planner` output must include the plan draft required sections from `design.md`.
    - Both skills must forbid canonical edits, implementation edits, GitHub mutation, destructive command, phase promotion, and reviewer-pass claims.

- Issue 004: phase gate and spec-reviewer integration
  - 目的:
    - `phase_design.md` / `phase_plan.md` / `phase_plan_issue.md` に delegated authoring gates と reviewer criteria を組み込む。
  - 推奨 title / slug:
    - title: `Delegated Authoring Phase Gates`
    - slug: `delegated-authoring-phase-gates`
  - 成果物:
    - Delegated Design Authoring Gate.
    - Delegated Plan Authoring Gate.
    - Reviewer criteria for delegated draft provenance, staleness, traceability, scope discipline, and phase gate preservation.
    - Epic-specific plan handoff updates in `phase_plan_epic.md`, or explicit rationale if shared `phase_plan.md` fully owns the delegated plan gate.
    - Provider / dogfooding docs parity.
  - tranche:
    - T2 Gate integration
  - closes:
    - E-RQ-003, E-RQ-008, E-RQ-011
    - E-AC-004, E-AC-005 gate/reviewer readiness only
    - E-AC-006, E-AC-009
  - 依存:
    - Issue 001
    - Issue 002
    - Issue 003
  - Issue readiness:
    - Must state that delegated draft is not reviewer pass.
    - Must preserve manual authoring as valid path when delegation is unavailable or intentionally skipped.

- Issue 005: Codex host callable role adapter
  - 目的:
    - `.codex/agents` に thin callable entrypoints を追加し、role skill を正本にした host adapter boundary を固定する。
  - 推奨 title / slug:
    - title: `Codex Delegated Author Adapters`
    - slug: `codex-delegated-author-adapters`
  - 成果物:
    - Verified or documented `.codex/agents/system-architect.toml`.
    - Verified or documented `.codex/agents/implementation-planner.toml`.
    - Provider source under `src/spec_dock/assets/install_root/.codex/agents/`.
    - Dogfooding parity under `.codex/agents/`.
    - Adapter/skill drift prevention note.
  - tranche:
    - T3 Host integration
  - closes:
    - E-RQ-010
    - E-AC-002 host-adapter portion
  - 依存:
    - Issue 003
    - Issue 004
  - Issue readiness:
    - Must not duplicate long-form role instructions.
    - Must explicitly exclude `.github/agents` / Copilot agent implementation.
    - If host syntax is uncertain, close only with documented uncertainty and no verified-integration claim.

- Issue 006: dogfooding parity and validation pilot
  - 目的:
    - Shipped workflow / skills / adapters を dogfooding workspace で使い、draft-only delegated authoring の実地証跡を残す。
  - 推奨 title / slug:
    - title: `Delegated Authoring Dogfooding Pilot`
    - slug: `delegated-authoring-dogfooding-pilot`
  - 成果物:
    - Provider / consumer parity evidence.
    - `spec-dock validate` and `spec-dock sync` evidence.
    - At least one delegated design draft and one delegated plan draft saved under `discussions/`.
    - Canonical integration evidence in `report.md`.
    - Fresh `spec-reviewer` result for pilot artifacts.
    - Metrics summary and write-capable defer decision.
  - tranche:
    - T4 Dogfooding and final evidence
  - closes:
    - E-RQ-009, E-RQ-012
    - E-AC-004 operational evidence
    - E-AC-005 operational evidence
    - E-AC-007, E-AC-008
  - 依存:
    - Issue 001
    - Issue 002
    - Issue 003
    - Issue 004
    - Issue 005
  - Issue readiness:
    - Must use shipped / documented workflow assets, not ad hoc prompt-only delegation.
    - Must record pilot metrics for draft count, integration ratio/cost, rejected reasons, traceability defects, scope creep or gate violations, forbidden action attempts, reviewer findings, stale draft events, provider/consumer drift, and implementation deviation if implementation follows.
    - Must record `write-capable delegation remains deferred` unless a later Epic / Issue explicitly approves it.

## Issue dependency graph
- タイトル:
  - Delegated authoring issue dependency graph
- 答える問い:
  - Which Issues must land before later role, host, and dogfooding work can safely proceed?
- 範囲:
  - Epic issue dependencies only.
- 含めない詳細:
  - Issue-internal TDD steps, commit rhythm, implementation tasks.
- 更新条件:
  - Issue split, dependency order, or tranche changes.

```plantuml
@startuml
skinparam monochrome true
left to right direction

rectangle "Issue 001\nPolicy foundation" as I1
rectangle "Issue 002\nDraft evidence schema" as I2
rectangle "Issue 003\nRole skill assets" as I3
rectangle "Issue 004\nPhase gates / reviewer" as I4
rectangle "Issue 005\nCodex thin adapters" as I5
rectangle "Issue 006\nDogfooding pilot" as I6

I1 --> I2
I1 --> I3
I2 --> I3
I1 --> I4
I2 --> I4
I3 --> I4
I3 --> I5
I4 --> I5
I1 --> I6
I2 --> I6
I3 --> I6
I4 --> I6
I5 --> I6
@enduml
```

## 統合チェックポイント
- G1 Requirement / design gate closure:
  - Epic requirement and design have fresh `spec-reviewer` pass.
  - Issue 001 and Issue 002 cannot start from stale requirement/design assumptions.
- G2 Policy + evidence foundation:
  - Issue 001 and Issue 002 complete.
  - Draft-only ownership and report evidence are defined before role skills are introduced.
- G3 Role + gate integration:
  - Issue 003 and Issue 004 complete.
  - Role skills and reviewer criteria agree on draft output, blockers, forbidden actions, and evidence.
- G4 Host adapter integration:
  - Issue 005 complete or documented uncertainty accepted.
  - `.codex/agents` is thin and does not duplicate canonical skill instructions.
- G9 Final dogfooding / Epic closure:
  - Issue 006 complete.
  - Provider/consumer parity, validation, sync, reviewer, and pilot metrics are recorded.

## 品質ゲート
- test:
  - Unit / content tests for managed assets and docs where existing patterns support them.
  - Init/update asset parity tests for new role skills and `.codex/agents` adapters.
- observability:
  - `report.md` records each delegated draft invocation, artifact path, integration result, reviewer result, and promotion decision.
- migration:
  - No runtime data migration.
  - Existing manual authoring workflow remains valid throughout rollout.
- docs:
  - Provider docs and dogfooding docs are updated together or dogfooding refresh evidence explains intended differences.
  - Report templates and active-none report scaffolds include delegated evidence sections.

## ロールアウト / docs impact
- ロールアウト順序:
  1. Policy docs.
  2. Draft evidence schema and report templates.
  3. Role skills.
  4. Phase/reviewer docs.
  5. Codex adapters.
  6. Dogfooding pilot and final evidence.
- 契約 / docs 更新:
  - `workflow_spec_authoring.md`
  - `phase_design.md`
  - `phase_plan.md`
  - `phase_plan_epic.md`
  - `phase_plan_issue.md`
  - report templates / active-none scaffolds
  - role skills
  - `.codex/agents`
  - dogfooding workspace copies

## Issue 準備完了条件
- Issue に要求する最低条件:
  - Requirement/design/plan for the Issue must trace to this Epic E-RQ/E-AC and design decisions.
  - Each Issue must state provider-side source of truth and dogfooding parity surface.
  - Each Issue must include step-local verification strategy appropriate to docs / skills / adapters / tests.
  - Any delegated authoring used while authoring the Issue must follow the draft-only evidence contract once implemented; before implementation, manual authoring remains valid.

## 最終完了条件
- E-AC 完了:
  - E-AC-001..E-AC-009 have implementation evidence or explicit non-applicable evidence.
- 統合 / ロールアウト完了:
  - All six Issues are done or explicitly superseded by reviewer-approved plan amendment.
  - Provider / consumer parity is verified.
  - `spec-dock validate` and `spec-dock sync` evidence is recorded.
- docs 影響解決:
  - Provider docs, templates, active-none scaffolds, role skills, host adapters, and dogfooding copies are aligned.
  - Final fresh `spec-reviewer` confirms requirement / design / plan / report alignment.

## 依存 / ブロッカー
- D-001:
  - `.codex/agents` path / syntax verification may affect whether Issue 005 closes as verified adapter implementation or documented uncertainty.
- D-002:
  - `spec-reviewer` availability is required for phase gates and final closure.
- D-003:
  - GitHub auth is required to create the six GitHub-backed child Issues.

## 未確定事項
- なし:
  - `.github/agents` / Copilot support remains non-scope.
  - Runtime validation and write-capable delegation remain deferred.
  - Issue 005 fallback for host syntax uncertainty is part of the plan, not an unresolved scope question.
