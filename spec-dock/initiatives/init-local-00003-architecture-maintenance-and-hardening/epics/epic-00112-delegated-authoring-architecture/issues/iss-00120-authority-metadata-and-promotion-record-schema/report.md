---
種別: レポート（Issue）
ID: "iss-00120"
タイトル: "Authority Metadata and Promotion Record Schema"
関連GitHub: ["#120"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00120 Authority Metadata and Promotion Record Schema — レポート（進捗 / 決定 / 結果）

## 進捗サマリー
- 現在地: S01 provider docs/templates/system active-none update completed with targeted docs-only inspection evidence and spec-reviewer pass.
- 未完了: S02/S90/S99 remain unstarted in committed issue evidence.
- 次のマイルストーン: S02 managed scaffold/content assertions.

## Workflow Delegation Consent
- source: user explicitly requested appropriate sub-agent use for issue requirement/design/plan authoring.
- scope: current repo/worktree, iss-00120, current session, named read-only specialist/reviewer roles.
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
- D-003:
  - Status: resolved
  - Type: implementation-time interpretation
  - Source-agent: doc-writer `Parfit`
  - Topic: S01 explicit grant key spelling
  - Trigger: S01 required an explicit grant key set including write grants and lifecycle grants.
  - Ambiguity / constraint: approved plan names `can_write_requirement` etc. and requires implementation/ready/finish/phase completion grants, but not every lifecycle key spelling was pre-enumerated.
  - Observed facts: AC-003 requires exact grants; S01 closure requires no wildcard semantics; forbidden scope excludes runtime/tests.
  - Options considered: only document five `can_write_*` keys; add lifecycle keys using explicit names; defer lifecycle key names.
  - Decision: Document `can_write_implementation`, `can_mark_issue_ready`, `can_finish_issue`, and `can_complete_phase` alongside the five requested write keys.
  - Rationale: This keeps AC-003 exact and fail-closed without adding runtime behavior.
  - Affected files: `workflow_spec_authoring.md`, report templates, and active-none report placeholders.
  - Affected tests: none edited in S01; docs-only rg inspections passed.
  - Risk if wrong: later S02/runtime assertions may need different key names.
  - Rollback or revisit: revise key spelling during S01 spec-reviewer gate before S02 assertions.
  - Disposition: applied
  - Evidence: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`, report templates, active-none report placeholders, S01 tc-001〜tc-003 rg evidence below, and Carson S01 `review_status: pass`.

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
- status: pending implementation; specs are approved and implementation has not started.
- required evidence: see `plan.md` Spec-Locked Closure Index and final completion conditions.

## 実行証跡
- S01 docs-only implementation:
  - changed files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/templates/epic/report.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/epic/report.md`
    - `src/spec_dock/assets/spec_dock/system/active-none/issue/report.md`
  - tc-001 command:
    - `rg -n 'status|authority|owner_role|draft_author_role|approval|source_revision|approved_revision|approved_hash' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; required authority metadata fields appear in provider docs, report templates, and active-none report placeholders.
  - tc-002 command:
    - `rg -n 'can_write_requirement|can_write_design|can_write_plan|can_write_report|can_write_discussions|wildcard|\*' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates`
    - result: pass; explicit grant keys appear in `workflow_spec_authoring.md` and report templates, and wildcard grant semantics are denied.
  - tc-003 command:
    - `rg -n 'Promotion Record|promotion_record|approved_hash|approved_revision|reviewer_target_hash|mismatch|stale|promotion' src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/system/active-none`
    - result: pass; promotion_record fields, approved hash/revision, reviewer target hash, mismatch handling, stale handling, and promotion blocking semantics appear in provider contracts/templates/placeholders.
  - reviewer gate: Carson (`019e55a8-d638-7101-a6a6-a55cbb01d5dc`) `review_status: pass`.
  - reviewer finding disposition: P2 ledger disposition naming fixed by changing D-003 disposition to `applied`.
  - material decision: integrated as D-003 and accepted by S01 spec-reviewer gate.

## ブロッカー / 未完了
- S02, S90, and S99 are still unstarted in committed issue evidence.
