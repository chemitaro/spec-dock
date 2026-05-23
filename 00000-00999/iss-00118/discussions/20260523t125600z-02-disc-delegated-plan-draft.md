---
種別: discussion
ID: "disc-iss-00118-delegated-plan-draft"
タイトル: "Delegated Plan Draft for iss-00118 Dogfooding Pilot"
作成者: "spec-dock-implementation-planner"
作成日: "2026-05-23"
状態: "draft-evidence"
親: ["iss-00118", "epic-00112", "init-local-00003"]
---

# Delegated Plan Draft for iss-00118

## Plan Summary

Run `iss-00118` as a dogfooding pilot, not as a provider implementation issue.
The execution order is:

1. S01 prerequisite / provider contract no-op check
2. S02 dogfooding parity and validation
3. S03 delegated design draft evidence
4. S04 delegated plan draft evidence
5. S05 pilot metrics and defer decision
6. S06 negative / blocked case evidence
7. S90 report/docs impact
8. S99 final quality gate

This draft is evidence only and does not claim reviewer approval.

## Requirement / Design Traceability

- AC-001 -> S01 prerequisite ledger, no false provider update claim
- AC-002 -> S02 validate/sync and parity evidence
- AC-003 -> S99 final `spec-reviewer` gate
- E-AC-004 -> S03 delegated design draft
- E-AC-005 -> S04 delegated plan draft
- E-AC-007 -> S02 provider/consumer parity
- E-AC-008 -> S05 metrics and write-capable defer decision
- E-AC-009 -> S06 negative / blocked case
- EC-001 -> uncertainty / no-op handling
- EC-002 -> drift classification

## Milestones

- M1 prerequisite ledger ready
- M2 parity verified or drift classified
- M3 design pilot artifact produced
- M4 plan pilot artifact produced
- M5 metrics and defer decision complete
- M6 negative path covered
- M7 final gates ready

## Dependency-Derived Execution Order

S01 and S02 must precede draft integration so the pilot is not performed on
stale or unverified assets. S03 precedes S04 because design draft evidence can
inform the planning draft. S05 and S06 depend on draft outcomes. S90/S99 close
the report and review gates.

## Issue / Step Slicing

- S01: inspect prior reports/assets and record no-op / uncertainty.
- S02: run/record parity validation and `validate` / `sync`.
- S03: save delegated design draft and record integration decision.
- S04: save delegated plan draft and record integration decision.
- S05: table required metrics and defer write-capable delegation.
- S06: record `adapter_contract_only` host fallback as the negative case.
- S90/S99: close report, QA/code/spec review, final validation.

## Test Strategy Mapping

- tc-001: prerequisite ledger inspection
- tc-002: validate/sync and parity evidence
- tc-009: shipped workflow/skills/adapters parity before pilot trust
- tc-006: design draft artifact + report delegation evidence
- tc-007: plan draft artifact + report delegation evidence
- tc-008: metrics + defer decision
- tc-010: negative/blocked evidence
- tc-003: final spec review

## Review Gates

- Use `qa-reviewer` for closure coverage because the pilot is evidence-heavy.
- Use `code-reviewer` only if tests/scaffold/runtime behavior changes.
- Use final `spec-reviewer` for requirement/design/plan/report/diff alignment.
- Delegated draft output is never a reviewer pass.

## Rollback / Compatibility

- Rollback is issue diff revert.
- Manual authoring remains valid.
- Runtime fallback / schema enforcement / write-capable delegation remain
  outside this issue.
- Since `iss-00117` closed as `adapter_contract_only`, this pilot must record
  `host_invocation_verified=false`.

## Docs Impact

Expected changed artifacts:

- this delegated plan draft under issue `discussions/`
- delegated design draft under issue `discussions/`
- active issue `report.md`

Provider docs/skills/templates should remain unchanged unless a prerequisite
gap is discovered.

## Final Quality Gate

Minimum final gate:

- `./spec-dock/scripts/spec-dock validate` pass
- `./spec-dock/scripts/spec-dock sync` pass
- all closure ids recorded
- S03/S04 draft paths and integration decisions recorded
- S05 metrics and defer decision recorded
- S06 negative evidence recorded
- final QA / code-if-needed / spec review results recorded

## Plan Blockers

none.

Execution-time guard: if prior issue evidence, adapter classification, or
pilot target contract cannot be verified, stop before S03/S04 and record
documented uncertainty or follow-up.

## Integration Notes for Main Orchestrator

- Use this as S04 delegated plan draft evidence.
- Integrate as `partially_integrated`: step order, metrics, negative case, and
  final gate model are adopted into `report.md`.
- Do not promote this draft into canonical plan without orchestrator judgment
  and fresh reviewer approval.

## Delegated Draft Evidence

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: active issue `iss-00118`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
- draft status: `produced`
- integration notes:
  - use as S04 draft-only plan evidence
  - preserve S01 through S99 order
  - do not treat as canonical plan update or reviewer pass
- rejected portions: none from this draft; orchestrator may reject or partially
  integrate.
- blockers: none
