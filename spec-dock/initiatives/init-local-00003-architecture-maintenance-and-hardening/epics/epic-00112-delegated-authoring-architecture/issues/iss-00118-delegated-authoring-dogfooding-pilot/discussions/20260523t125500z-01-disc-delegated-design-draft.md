---
種別: discussion
ID: "disc-iss-00118-delegated-design-draft"
タイトル: "Delegated Design Draft for iss-00118 Dogfooding Pilot"
作成者: "spec-dock-system-architect"
作成日: "2026-05-23"
状態: "draft-evidence"
親: ["iss-00118", "epic-00112", "init-local-00003"]
---

# Delegated Design Draft for iss-00118

## Requirement Coverage

The dogfooding pilot is feasible as draft-only evidence for `iss-00118`.
It can close the operational evidence side of the parent Epic by demonstrating:

- provider/consumer parity before trusting pilot evidence
- delegated design draft evidence
- delegated plan draft evidence
- metrics and the write-capable delegation defer decision
- at least one negative / blocked case

This draft is not canonical authority and does not replace a fresh
`spec-reviewer` pass.

## Existing Context Findings

- Active context is consistent: initiative `init-local-00003`, Epic
  `epic-00112`, Issue `iss-00118`.
- `iss-00118` depends on `iss-00113` through `iss-00117`.
- `iss-00117` closed as `adapter_contract_only`, so this pilot must record
  `host_invocation_verified=false`.
- Role skills and thin Codex adapter assets exist in provider and dogfooding
  surfaces.
- `workflow_spec_authoring.md` and `phase_design.md` already encode the
  draft-only policy, evidence lifecycle, failure modes, and delegated design
  gate.

## Design Decisions

- Use `iss-00118` as the active pilot target.
- Treat direct role skill invocation as the pilot invocation path.
- Treat Codex host adapter availability as static contract evidence only.
- Save this draft as produced evidence and let the orchestrator decide whether
  to integrate, partially integrate, or reject it.
- Use the `adapter_contract_only` host fallback as the negative / blocked case.
- Keep write-capable delegation deferred.

## Alternatives Considered

- Verified Codex host invocation: rejected because live host callability is not
  verified by `iss-00117`.
- Canonical design mutation by the delegated role: rejected because delegated
  authors produce draft evidence only.
- Success-path-only pilot: rejected because `iss-00118` requires negative /
  blocked evidence.
- Runtime validation or role registry work: rejected as parent Epic non-scope.

## Boundary / Contract Model

- Node: `iss-00118`
- Phase: design evidence for dogfooding pilot
- Role: `spec-dock-system-architect`
- Mode: draft-only
- Invocation path: direct role skill / documented contract
- Host invocation: `host_invocation_verified=false`
- Report location: `spec-dock/active/issue/report.md`

Forbidden:

- canonical doc or implementation edits by the delegated role
- GitHub mutation
- phase promotion
- reviewer pass claims
- write-capable delegation, runtime validation, role registry, or
  `.github/agents` support

## Dependency Analysis

Upstream:

- `iss-00113`: policy foundation
- `iss-00114`: draft evidence schema
- `iss-00115`: role skills
- `iss-00116`: phase gates / reviewer criteria
- `iss-00117`: Codex thin adapters, closed as `adapter_contract_only`

The pilot is not blocked by `adapter_contract_only` if it avoids verified live
host callability claims.

## Source Of Record

- Provider source: `src/spec_dock/assets/spec_dock/docs/`,
  `src/spec_dock/assets/install_root/.agents/skills/`,
  `src/spec_dock/assets/install_root/.codex/agents/`
- Dogfooding verification surface: `spec-dock/docs/`, `.agents/skills/`,
  `.codex/agents/`
- Canonical ledger: `spec-dock/active/issue/report.md`

## Data Flow / Domain Model / Interface Contract

1. Orchestrator establishes invocation contract.
2. Delegated role reads active context, parent docs, workflow docs, and phase
   docs.
3. Delegated role produces draft evidence.
4. Orchestrator saves, integrates, partially integrates, or rejects the draft.
5. `report.md` records status, source artifacts, integration result, rejected
   portions, blockers, reviewer result, and promotion decision.
6. Fresh `spec-reviewer` reviews canonical artifacts and evidence.

## File / Module Change Plan

- Add this design draft under issue `discussions/`.
- Add a plan draft under issue `discussions/`.
- Update `report.md` with invocation, integration, metrics, negative case,
  validation, and reviewer evidence.
- Do not change provider source unless prerequisite inspection reveals a
  missing prior contract.

## Migration / Compatibility / Rollback

- No runtime migration is required.
- Manual authoring remains valid.
- If this draft becomes stale before integration, mark it `stale` or
  `superseded` and regenerate/reconcile before use.

## Observability

Record:

- draft count
- design draft path
- plan draft path
- integration ratio / integration cost
- rejected reasons
- traceability defects
- scope creep or gate violations
- forbidden action attempts
- reviewer findings
- stale draft events
- provider/consumer drift
- implementation deviation
- `host_invocation_verified=false`
- write-capable delegation defer decision

## Test Strategy

- Inspect provider/consumer parity for role skills and adapters.
- Run `./spec-dock/scripts/spec-dock validate`.
- Run `./spec-dock/scripts/spec-dock sync`.
- Run targeted tests only if tests or scaffold assertions change.
- Run fresh `spec-reviewer` after report integration.

## ADR Candidates

- Future guardrails for write-capable delegation.
- Whether live host adapter verification is required for future adapter-backed
  pilots.
- Whether delegated draft evidence should gain runtime schema validation after
  this pilot.

## Risks

- False success if `adapter_contract_only` is described as live host
  callability.
- False authority if delegated draft is treated as reviewer pass.
- Provider/consumer drift if dogfooding copies are trusted without parity.
- Missing negative evidence if only happy-path drafts are recorded.
- Vague metrics if integration cost and rejected portions are not recorded.

## Requirement Clarification Requests

none.

## Integration Notes for Main Orchestrator

- Use this as S03 delegated design draft evidence.
- Integrate as `partially_integrated`: boundary, invocation classification,
  negative case, observability metrics, and risk model are adopted into
  `report.md`.
- Reject any implication of verified live Codex host callability or
  write-capable delegation.
- Run fresh final reviewers after integration.

## Delegated Draft Evidence

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00118`
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
  - `spec-dock/docs/phase_design.md`
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.codex/agents/system-architect.toml`
- draft status: `produced`
- integration notes: use direct role skill / documented invocation contract;
  record `host_invocation_verified=false`.
- rejected portions:
  - verified live Codex host callability claim
  - write-capable delegation implication
  - treating delegated draft as canonical authority or reviewer pass
- blockers: none
