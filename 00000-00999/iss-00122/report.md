---
種別: レポート（Issue）
ID: "iss-00122"
タイトル: "Evidence Adoption Ledger and Bounded Depth2 Delegation"
関連GitHub: ["#122"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00122 Evidence Adoption Ledger and Bounded Depth2 Delegation — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S01 provider docs/templates ledger schema implementation and spec-reviewer gate are passed.
- 未完了: S02, S90, and S99.
- 次のマイルストーン: implement S02 bounded depth=2 role graph and managed asset assertions.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00122, current session, named read-only specialist/reviewer roles.
- allowed roles: system-architect, implementation-planner, repo-analyst, consultant/deep-consultant if needed, spec-reviewer.
- boundary: no destructive action, no credentialed private browsing, no write-capable delegation without separate approval.

## Delegated Draft Evidence
- evidence artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/discussions/20260523t144246z-disc-v1-issue-authoring-delegated-evidence.md`
- system-architect `Lovelace`:
  - role: `system-architect`
  - phase: requirement/design input
  - source artifacts: parent Epic requirement/design/plan/report, v0 historical Issue #113〜#118 docs, current Issue scaffold, workflow/phase docs.
  - status: `integrated`
  - integration result: AC/EC/non-scope/provider/test/rollback guidance reflected into this Issue requirement/design.
  - rejected portions: none.
  - blockers: none.
  - reviewer result: Heisenberg `review_status: pass` on canonical docs.
  - promotion decision: not promoted by itself; used as draft evidence only.
- repo-analyst `Mencius`:
  - role: `repo-analyst`
  - phase: design path/test surface input
  - source artifacts: provider source tree, dogfooding paths, test directories.
  - status: `integrated`
  - integration result: provider source, dogfooding validation surface, likely tests, and risk reflected into design/plan.
  - rejected portions: none.
  - blockers: Permission/Profile behavior remains probe-driven and fail-closed where relevant.
  - reviewer result: Heisenberg `review_status: pass`.
  - promotion decision: not promoted by itself; used as draft evidence only.
- implementation-planner `Archimedes`:
  - role: `implementation-planner`
  - phase: plan slicing input
  - source artifacts: workflow_issue.md, phase_plan_issue.md, authoring/issue-plan.md, parent Epic v1 amendment, current Issue docs.
  - status: `integrated_after_canonicalization`
  - integration result: step slicing, delegated roles, closure ids, reviewer mapping reflected into plan.
  - rejected portions: treating original scaffold plans as implementation-ready.
  - blockers: none after canonical docs were rewritten.
  - reviewer result: Heisenberg `review_status: pass`.
  - promotion decision: not promoted by itself; used as draft planning input only.

## Spec Interpretation / Decision Ledger
- D-001:
  - Status: resolved
  - Type: scope
  - Decision: This Issue is an additive v1 amendment and must not rewrite v0 Issue 001〜006 / #113〜#118 plans or reports.
  - Disposition: promoted_to_requirement_design_plan
  - Evidence: parent Epic v1 amendment and this Issue docs.
- D-002:
  - Status: resolved
  - Type: authority
  - Decision: final authority and phase promotion remain with main orchestrator plus fresh reviewer gates.
  - Disposition: promoted_to_requirement_design_plan
  - Evidence: requirement constraints and design interface contract.

## Spec Authoring Gate
- Requirement Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - reviewed scope: requirement.md, design.md, plan.md, report.md, parent epic v1 amendment.
  - investigated facts: parent Epic docs, v0 issue historical evidence, delegated evidence artifact, Avicenna failed-review findings, and Heisenberg re-review evidence.
  - promotion: approved for issue execution; implementation remains not started.
- Design Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - finding closure: role/gate/probe-scope issues from Avicenna were fixed before pass.
- Plan Gate:
  - state: passed
  - reviewer: Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`)
  - review_status: pass
  - execution boundary: issue specs are approved, but no issue implementation has started.

## Reviewer History
- Avicenna (`019e556c-cf16-7d23-a773-3a7b23cf89df`): `review_status: fail`
  - findings: iss-00123 required real positive/negative write probe steps; iss-00123 S01 had `.codex/agents` and manual probe evidence under spec-reviewer scope; iss-00122 S01 had `.agents/skills` under spec-reviewer scope.
  - disposition: fixed in plan.md before re-review.
- Heisenberg (`019e5570-9ebf-72f0-bdfc-762f906a2c7a`): `review_status: pass`
  - findings: none.
  - rationale: prior findings closed; no P0/P1 blockers in reviewed scope.

## 受け入れ条件の現在状況
- status: S01 implementation evidence recorded; reviewer gate pending.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 evidence adoption ledger schema:
  - changed files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - implementation summary:
    - Added Evidence Adoption Ledger semantics for `adopted`, `partially_adopted`, `rejected`, `deferred`, `stale`, and `blocked`.
    - Added unresolved `blocked` / `stale` promotion-blocking rule.
    - Added report template table fields for source, target, rationale, evidence, and next action.
  - tc-001 command:
    - `rg -n 'adopted|partially_adopted|rejected|deferred|blocked|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; provider docs/templates now expose adoption status values and active-none already exposes delegated evidence failure states.
  - tc-002 command:
    - `rg -n 'unresolved|blocked|promotion|cannot promote|must not promote|stale' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates`
    - result: pass; workflow docs/templates state that unresolved `blocked` / `stale` Evidence Adoption Ledger entries block promotion / implementation start / issue ready / issue finish / phase completion.
  - guardrail:
    - `git diff --check`
    - result: pass.
  - reviewer gate:
    - Nash (`019e5613-b432-7c61-a7db-4af725486a01`) `review_status: fail`.
    - finding: P1, tc-001 plan command still searched delegated draft lifecycle state `partially_integrated` instead of Evidence Adoption Ledger state `partially_adopted`.
    - disposition: fixed by amending tc-001 in `plan.md` to search `partially_adopted`, matching requirement AC-001 and the implemented EAL schema.
    - re-review: pass; no findings.
  - final reviewer gate:
    - Nash (`019e5613-b432-7c61-a7db-4af725486a01`) `review_status: pass`.
    - reason: plan tc-001, report evidence, AC-001, and implemented Evidence Adoption Ledger schema now use `partially_adopted`; changed files remain limited to S01 provider docs/templates plus active issue plan/report.

## ブロッカー / 未完了
- S02/S90/S99 not started.
