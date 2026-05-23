---
種別: ディスカッション
ID: "20260524t000000z-01-disc-fallback-system-architect-design-draft"
タイトル: "S02 fallback system-architect design draft"
状態: "draft"
作成者: "spec-dock-system-architect"
親: ["iss-00125", "epic-00112", "init-local-00003"]
authority: "proposed"
source_revision: "608a7e994e37e2ee2d095eb96f6700ebe1f62e1b"
---

# S02 fallback system-architect design draft

## Requirement Coverage
- Covers `iss-00125` S02 / `tc-003` as fallback design draft evidence only.
- Supports AC-001 / AC-002 / AC-004 by recording prerequisite closure/fallback, proposed-only delegated output, and additive v1 closure without rewriting v0 or prerequisite issue reports.
- Supports AC-003 by preserving the lifecycle/context-pack block expectation for proposed artifacts; S03 still owns observation and verification.

## Existing Context Findings
- Active scope is `init-local-00003` / `epic-00112` / `iss-00125`.
- `iss-00125/report.md` records S01 evidence: #120-#124 are closed or explicitly fallbacked, validate/sync baseline passed, and S02 is locked to fallback discussion drafts.
- No safe dedicated canonical pilot target exists: `pilot_target_issue_id: none`.
- Permission/Profile evidence is not sufficient to enable canonical `design.md` writes; fallback is required.

## Design Decisions
- S02 design output remains a discussion draft, not canonical `design.md`.
- The locked fallback path is the only intended artifact target for this delegated design evidence.
- The draft has `authority: proposed`; it cannot authorize implementation, issue ready, issue finish, phase completion, or reviewer pass.
- Stale prerequisite wording is carried as caveat evidence and not rewritten.

## Alternatives Considered
- Canonical write to a pilot issue `design.md`: rejected because no safe target is locked.
- Reusing `iss-00125`, v0 issues `iss-00113`-`iss-00118`, or prerequisite v1 issues `iss-00120`-`iss-00124`: rejected by the approved S02 contract.
- Editing completed prerequisite reports to remove stale wording: rejected; v1 closure must be additive.
- Claiming host/Permission Profile verification from adapter presence: rejected; unverified or fail-open evidence must disable write-scoped authoring.

## Boundary / Contract Model
- Main orchestrator owns saving, integration, report updates, final reviewer invocation, promotion, and user dialogue.
- `spec-dock-system-architect` provides proposed design evidence only.
- Allowed artifact for this output: this locked fallback discussion draft path.
- Forbidden: canonical specs, implementation/tests/config, GitHub mutation, v0/prerequisite report rewrites, promotion, reviewer-pass claims.

## Dependency Analysis
- Upstream: approved Epic v1 amendment, `iss-00125` requirement/design/plan/report, prerequisite issue closure/fallback evidence for `iss-00120`-`iss-00124`.
- Downstream: S02 report integration, implementation-planner fallback draft, S03 lifecycle/context-pack block or fallback verification, S90/S99 gates.
- The pilot can proceed only as fallback evidence unless a new reviewed plan amendment supplies a safe canonical target and verified Permission Profile.

## Source of Record
- `spec-dock/active/context-pack.md`
- `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md}`
- `spec-dock/active/epic/{requirement.md,design.md,plan.md,report.md}`
- `.agents/skills/spec-dock-system-architect/SKILL.md`
- Supporting workflow references: `workflow_spec_authoring.md`, `phase_design.md`, `reference_sync.md`

## Data Flow / Domain Model / Interface Contract
- Inputs: approved active issue/epic docs, S02 Task Manifest Lock, and source hash `608a7e994e37e2ee2d095eb96f6700ebe1f62e1b`.
- Output: proposed design discussion draft.
- Orchestrator integration: save draft, cite evidence in `report.md`, keep `authority: proposed`.
- Lifecycle expectation: context-pack/lifecycle must not treat proposed fallback draft evidence as authoritative downstream input.

## File / Module Change Plan
- Delegated architect changes: none.
- Orchestrator saves this proposal to this locked discussion file and records S02 evidence in `iss-00125/report.md`.
- No provider source, runtime, tests, configs, v0/prerequisite reports, or GitHub state are changed.

## Migration / Compatibility / Rollback
- v0 draft-only workflow remains valid and untouched.
- Manual authoring remains valid.
- Rollback is to discard or supersede this discussion draft; no canonical artifact needs reversal.
- If a safe canonical target becomes available later, it requires a refreshed manifest, permission probe evidence, plan amendment if needed, and fresh reviewer gate.

## Observability
- Report evidence should include draft path, source hash, fallback reason, proposed authority, no-promotion statement, and forbidden changes avoided.
- S03 should record `active show` / `validate` or equivalent evidence proving proposed/fallback artifacts do not become downstream authority.
- Any provider defect discovered during pilot should be recorded as follow-up/amendment, not fixed silently in S02.

## Test Strategy
- S02 evidence test: confirm this draft is saved only to the locked discussion path and records no final authority claim.
- Scope test: confirm no canonical specs, v0 reports/plans, prerequisite reports/plans, provider code, tests, config, or GitHub state were changed by delegated authoring.
- Lifecycle test is deferred to S03: verify proposed/fallback evidence is blocked or excluded from implementation/finish authority.

## ADR Candidates
- None required for this fallback draft.

## Risks
- Risk: fallback evidence may be mistaken for successful canonical write verification.
- Risk: stale prerequisite report wording may be treated as requiring retroactive edits.
- Risk: context-pack/lifecycle block may be overclaimed before S03 observation.
- Mitigation: report this as fallback-only, additive, proposed evidence with explicit no-promotion/no-reviewer-pass language.

## Requirement Clarification Requests
- none.

## Integration Notes for Main Orchestrator
- Save this as the locked S02 fallback system-architect design draft if still source-hash-current.
- Record S02 `tc-003` as produced fallback evidence, not canonical write verification.
- Keep S02 open until the implementation-planner counterpart and required reviewer/report gates are handled.
- Do not rewrite v0 or prerequisite issue reports; carry caveats in `iss-00125/report.md`.
- No final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.

## Delegated Draft Evidence
- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00125` under `epic-00112` / `init-local-00003`
- source artifacts read: `spec-dock/active/context-pack.md`; active issue `requirement.md`, `design.md`, `plan.md`, `report.md`; active epic `requirement.md`, `design.md`, `plan.md`, `report.md`; `.agents/skills/spec-dock-system-architect/SKILL.md`; workflow reference docs
- draft artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00125-authority-aware-delegated-authoring-dogfooding-pilot/discussions/20260524t000000z-01-disc-fallback-system-architect-design-draft.md`
- draft status: `produced`
- authority: `proposed`
- integration notes: fallback discussion draft only; no canonical write verification; intended for `iss-00125/report.md` S02 evidence integration
- rejected portions, if any: canonical `design.md` write, v0/prerequisite report rewrite, Permission/Profile verification claim, lifecycle block pass claim
- blockers, if any: no safe canonical pilot target; write-scoped canonical delegation not enabled
- Permission Profile / task manifest verification result: S02 Task Manifest Lock says `pilot_target_issue_id: none`, mode is fallback discussion draft only, source hash is `608a7e994e37e2ee2d095eb96f6700ebe1f62e1b`, and canonical write verification is not allowed
- previous phase artifacts edited: `none`
- final authority claimed: `no`
