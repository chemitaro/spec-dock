---
type: review
source: deep-consultant
created_at: 2026-05-23T10:19:00+09:00
epic: epic-00112
verdict: conditional_pass
---

# Deep Consultant Review: Delegated Authoring Architecture

## verdict

conditional_pass

## must_fix_before_implementation

1. Child issue acceptance / closure is too abstract.

   `issues/iss-00113..00117/*/requirement.md` AC-001..003 are mostly generic and can be satisfied by thin provider contract edits. The issue-specific invariants must be locked directly into AC and closure index:

   - `iss-00114`: lifecycle states, failure modes, report surfaces
   - `iss-00115`: role outputs and forbidden actions
   - `iss-00116`: reviewer criteria
   - `iss-00117`: verified adapter versus documented uncertainty

2. The authority hierarchy must be explicit.

   Epic design says role skill is canonical, while policy/gate/evidence are distributed across workflow and phase docs. Before implementation, freeze one table that says what is source of truth for:

   - `workflow_spec_authoring.md`
   - `phase_*.md`
   - report templates
   - role skills
   - `.codex/agents`

   Recommended hierarchy:

   - `workflow_spec_authoring.md`: policy source of truth
   - phase docs: phase precondition source of truth
   - report templates: evidence rendering source of truth
   - role skills: executable role prompt source of truth
   - host adapter: thin shim

3. Issue 005 host adapter fallback makes Epic success ambiguous.

   E-RQ-010 includes `.codex/agents` in scope, but `iss-00117` can close as documented uncertainty if path/schema is unverified. This is acceptable only if Epic / Issue 006 explicitly records `host invocation verified=false` and does not claim verified callable role integration.

4. Dogfooding pilot target is underdefined.

   `iss-00118` requires at least one design draft and one plan draft, but does not specify:

   - target active node
   - previous phase reviewer-pass evidence
   - whether invocation is direct role skill or host adapter
   - where integration / rejection is recorded

5. Shipped asset init/update regression tests should not be optional.

   Role skills and `.codex/agents` are provider-side shipped assets, so `tests/test_init_update.py` or equivalent managed asset parity checks should be a mandatory gate, especially for `iss-00115` and `iss-00117`.

6. Epic report state is inconsistent.

   `report.md` still contains earlier placeholder/current-state inconsistencies. The progress summary and frontmatter status should match the current child issue creation state before implementation starts.

## should_improve

- Define minimum `source_snapshot` fields. If commit hash is not mandatory, require at least source artifact path and last reviewed timestamp/reference.
- Specify who marks `stale` / `superseded` and when.
- Add one negative-path pilot in Issue 006, such as RCR, Plan Blocked, stale, or rejected draft.
- Keep role skills concise and explicitly reference workflow / phase docs to avoid role skills becoming independent policy source of truth.

## architecture_assessment

The six-issue decomposition is sound. Policy -> evidence schema -> role skills -> phase gates/reviewer -> host adapter -> dogfooding pilot realizes the original report's draft-only delegation, main orchestrator ownership, and fresh reviewer gate. Scope control is also appropriate: write-capable delegation, runtime validation, role registry, and Copilot support remain out of scope.

The main problem is not the architecture concept but the placement of authority and the roughness of issue-level completion criteria. Epic design is strong, but child issues remain template-like enough that implementers could satisfy them with shallow updates.

## agentic_workflow_assessment

Delegation design is correct. `system-architect` returns RCR on requirement gaps; `implementation-planner` returns Plan Blocked on design gaps. Reviewer independence is preserved.

For Codex-style agents, however, issue docs need sharper, executable contracts. Generic acceptance criteria such as "provider contract exists" are too easy to satisfy without implementing the required role boundaries, evidence fields, reviewer checks, and dogfooding proof.

## suggested_doc_edits

- Add `Authority Hierarchy / Section Ownership` to Epic design.
- Replace each child issue generic AC-001 with issue-specific acceptance criteria.
- Make managed asset parity tests mandatory in `iss-00115` and `iss-00117`.
- Add pilot target node, invocation path, negative-path evidence, and host adapter verification flag to `iss-00118`.
- Update Epic `report.md` progress summary to the child-issues-created state.
