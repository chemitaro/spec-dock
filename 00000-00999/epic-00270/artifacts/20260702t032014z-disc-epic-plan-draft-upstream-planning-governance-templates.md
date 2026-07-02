---
created_by_role: system-architect
scope_id: epic-00270
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t014409z-02-interview-phase3-first-scope-interview.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t015012z-interview-phase3-issue-slicing-flexibility-criteria.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t015343z-interview-phase3-delivery-pr-boundary.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t020503z-02-disc-phase3-issue-slicing-handoff-model.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t020503z-03-disc-phase3-quality-delivery-gate-model.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t030615z-interview-phase3-handoff-package-inspection-strength.md
intended_targets:
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Epic Plan Draft - Upstream Planning Governance And Templates

This is delegated draft architecture/planning evidence for `epic-00270`. It is not canonical `plan.md`, does not create Issues, and does not claim reviewer pass, phase completion, implementation readiness, or final authority.

Source requirement revision used: `spec-dock/active/epic/requirement.md` as read on 2026-07-02, status `draft`, with E-RQ-001 through E-RQ-008 and E-AC-001 through E-AC-006 present. Canonical `design.md` was still template-shaped at read time, so this draft depends primarily on the concrete requirement, accepted ADRs, split artifacts, and `report.md` Evidence Adoption Ledger.

## Draft Epic PLAN Content

The following block is proposed content for `epic-00270/plan.md`. Main orchestrator must decide what to adopt.

```markdown
---
種別: 計画書（Epic）
ID: "epic-00270"
タイトル: "Upstream Planning Governance And Templates"
関連GitHub: ["#270"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00270 Upstream Planning Governance And Templates - 計画

## この計画で閉じる E-RQ / E-AC

- E-RQ:
  - E-RQ-001: Issue 01 and Issue 02 update Initiative/Epic templates.
  - E-RQ-002: Issue 03 updates planning skills and workflow docs for source-grounded clarification and reviewer-gated authoring.
  - E-RQ-003: Issue 03 and Issue 05 preserve artifact-to-canonical authority flow and report evidence gates.
  - E-RQ-004: Issue 01, Issue 02, and Issue 05 enforce architecture-neutral / architecture-aware template authoring.
  - E-RQ-005: Issue 03 adds the scope-layering provider reference and thin links; Issue 05 validates discoverability and drift controls.
  - E-RQ-006: Issue 02 defines Epic-to-Issue slicing and handoff fields; Issue 04 makes Epic execution consume the handoff.
  - E-RQ-007: Issue 04 implements the Option B handoff inspection policy; Issue 05 validates the structural fail / reviewer finding split.
  - E-RQ-008: Issue 06 owns final automated/manual quality gates, review repair, and one-PR delivery readiness.
- E-AC:
  - E-AC-001: Issue 01, verified by Issue 05 and Issue 06.
  - E-AC-002: Issue 02, verified by Issue 05 and Issue 06.
  - E-AC-003: Issue 03, verified by Issue 05 and Issue 06.
  - E-AC-004: Issue 04, verified by Issue 05 and Issue 06.
  - E-AC-005: Issue 05 and Issue 06.
  - E-AC-006: Issue 06.

## 課題分割方針（Issue slicing policy）

- Baseline:
  - V3 の6 Issueを provisional baseline とする。
  - Issue 01-05 は `strict`、Issue 06 は `critical` を suggested grade とする。
  - この Epic では actual Issue scaffold は plan gate / fresh `spec-reviewer` 後に main orchestrator が作成する。この plan は actual Issue を作らない。
- 分割原則:
  - Issue は one coherent observable outcome を持つ。
  - Decision-only container を execution-ready Issue にしない。
  - Parent Epic requirement/design の境界を Issue plan で再定義しない。
  - Template/docs/skills/tests の変更は、reviewable boundary と verification boundary が一致するように切る。
- 採用済み flexibility gate:
  - 追加 Issue / 再分割は推奨しない。
  - 既存6 Issueでは独立レビュー性、責務境界、検証可能性、または PR delivery のいずれかが明確に悪化する場合に限って許可する。
  - 追加 Issue / 再分割を行う場合は、理由、影響、baselineとの差分、dependency/order、grade、handoff package を `plan.md` に反映し、fresh `spec-reviewer` gate を通す。
  - Re-slicing evidence は `report.md` Evidence Adoption Ledger / Spec Authoring Gate に記録する。
- PR 方針:
  - Epic delivery は原則1PR。
  - IssueごとのPR分割は通常方針に入れない。
  - 1PRが reviewability / delivery risk の面で破綻すると判断できる場合だけ、証跡を残して PR boundary を再検討する。

## 課題一覧（Issue list / 順序 / tranche 付き）

These are planned slices, not created SpecDock Issue IDs.

| Slice | Planned title | Suggested grade | Tranche | Purpose | Primary closes | Depends on |
|---|---|---|---|---|---|---|
| 01 | Redesign Initiative Requirement Design Plan Templates | strict | T1 templates | Initiative templates become strategic planning and Epic handoff surfaces | E-RQ-001, E-RQ-004, E-AC-001 | Plan gate |
| 02 | Redesign Epic Requirement Design Plan Templates | strict | T1 templates | Epic templates become target model, design slice, Issue handoff, and suggested-grade surfaces | E-RQ-001, E-RQ-004, E-RQ-006, E-AC-002 | Plan gate; align vocabulary with 01 |
| 03 | Update Initiative And Epic Planning Skills And Workflow Docs | strict | T2 guidance | Planning skills/docs guide artifacts -> requirement -> review -> design -> review -> plan -> review -> handoff | E-RQ-002, E-RQ-003, E-RQ-005, E-AC-003 | 01, 02; accepted ADRs |
| 04 | Update Epic Execution Handoff And Issue Readiness Workflow | strict | T2 execution readiness | Epic execution coordinates downstream Issue readiness and applies Option B handoff inspection | E-RQ-006, E-RQ-007, E-AC-004 | 02; coordinate with 03 |
| 05 | Add Upstream Planning Smoke Tests And Template Validation | strict | T3 validation | Smoke-test templates, skills, workflow docs, scope-layering links, artifact authority, and handoff readiness | E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-007, E-AC-005 | 01, 02, 03, 04 |
| 06 | Epic Quality Gate Manual Tests And PR Delivery | critical | T4 final delivery | Run Epic-wide automated/manual quality gates, repair review findings, and prepare one mergeable PR | E-RQ-008, E-AC-006 | 01-05 |

## Issue handoff package

Each downstream Issue should receive these fields from the Epic plan or Issue planning handoff:

- parent Initiative ID and Epic ID
- applicable parent requirement IDs
- applicable parent design IDs, once canonical design is adopted
- Issue purpose and one observable outcome
- allowed local delta
- forbidden parent boundary changes
- acceptance criteria seed
- model / contract / lifecycle constraints
- expected evidence type
- suggested Issue grade
- dependencies and blockers
- required verification level
- reviewer focus
- escalation triggers
- relevant artifacts and accepted ADRs

## Option B inspection policy

- Blocking fail:
  - missing canonical requirement/design/plan where required
  - missing or stale fresh `spec-reviewer` pass
  - missing Issue readiness contract
  - missing executable step / delegation contract / required verification / reviewer focus in Issue plan
  - unresolved Spec Authoring Gate or blocking/stale Evidence Adoption Ledger entry
  - raw artifact treated as canonical authority
  - decision-only Issue treated as execution-ready
- Reviewer finding / warning:
  - acceptance criteria exists but may be semantically weak
  - test strategy exists but may be insufficiently broad
  - target files are plausible but reviewer questions fit
  - artifact reference is present but may need clearer rationale
- Boundary:
  - Epic execution is a coordinator and structural gate. It must not become a semantic reviewer replacement.

## 統合チェックポイント

- G0 Canonical plan readiness:
  - `requirement.md`, `design.md`, and `plan.md` are concrete enough for downstream Issue planning.
  - Fresh `spec-reviewer` pass exists before actual Issue scaffold.
- G1 Template boundary review:
  - Initiative/Epic templates use architecture-neutral / architecture-aware wording.
  - Templates do not force DDD/EDA, private implementation design, or Issue-level TDD cycles.
- G2 Scope-layering and authority review:
  - `docs/authoring/scope-layering.md` exists as the single provider-side reusable reference.
  - Workflow docs / phase docs / skills / templates link thinly instead of duplicating the full responsibility model.
  - Raw artifacts are not treated as canonical authority.
- G3 Handoff readiness review:
  - Epic plan and Epic execution guidance include handoff package fields, suggested grades, dependencies, verification expectations, and Option B inspection policy.
- G4 Integrated smoke matrix:
  - Template shape, planning skill wording, workflow links, artifact guidance, and execution handoff are checked together.
- G9 Final quality / PR readiness:
  - Issue 06 confirms all prior slices are complete or intentionally deferred with evidence, automated/manual gates are complete, review repairs are revalidated, and one-PR delivery is ready.

## 品質ゲート

- Automated gates:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- Command policy:
  - Use the repository's available commands.
  - If a command is unavailable, inappropriate, or fails for unrelated baseline reasons, record command, exit/result, reason, and next action in `report.md`.
- Scope-layering structural fail checks:
  - provider docs must not use local artifact paths as provider authority
  - required inbound links to `authoring/scope-layering.md` must exist
  - full responsibility table must not be duplicated across templates/docs/skills
  - templates must not embed a long scope table
  - decision-only Issues must not be described as execution-ready
  - raw artifacts must not be described as canonical authority

## Manual tests

- Manual test setup:
  - Use `manual-tests/` only for local trial workspaces.
  - Initialize an independent Git repository inside a trial directory if SpecDock state is needed.
  - Do not rely on the parent repository's git history, index, or active SpecDock state as test data.
  - Do not commit raw manual-test workspaces, fixtures, logs, captures, or evidence files.
  - Summarize useful evidence in `report.md` or a scope-local artifact.
- Minimum manual scenarios:
  1. A new Initiative scaffold uses updated Initiative templates.
  2. A new Epic scaffold uses updated Epic templates.
  3. Initiative templates do not include Issue-level TDD cycles.
  4. Epic templates include Issue handoff and suggested grade fields.
  5. Initiative planning skill guides artifacts -> requirement -> review -> design -> review -> plan -> review -> Epic handoff.
  6. Epic planning skill guides artifacts -> requirement -> review -> design -> review -> plan -> review -> Issue handoff.
  7. Epic execution skill reads as a handoff / execution coordinator.
  8. `artifacts/` is the recommended destination for new working artifacts.
  9. Legacy `discussions/` is not suggested as the primary new working artifact destination.
  10. Generated/dogfooding docs remain coherent after validate/sync.

## 課題準備完了条件（Issue readiness criteria）

- Before creating actual downstream Issues:
  - Canonical `requirement.md`, `design.md`, and `plan.md` have fresh reviewer-gated adoption or explicit non-promotion state is recorded.
  - This plan's provisional six-Issue baseline has not been changed without the adopted flexibility gate.
  - `report.md` EAL has no unresolved `blocked` or `stale` entry affecting planning or handoff.
- Each Issue is ready only when:
  - it has one coherent observable outcome
  - applicable E-RQ / E-AC links are known
  - parent requirement/design constraints are known
  - allowed local delta and forbidden parent changes are explicit
  - suggested grade is known
  - dependencies and blockers are listed
  - required verification and reviewer focus are listed
  - relevant artifacts / ADRs are linked
  - major open questions are resolved or explicitly scoped

## Final delivery Issue

- Issue 06 is intentionally a `critical` quality / delivery Issue.
- It owns:
  - full Epic validation
  - automated checks
  - static analysis where available
  - SpecDock validate/sync evidence
  - manual tests
  - dogfooding workspace inspection
  - provider vs dogfooding mirror review
  - documentation/template/skill consistency review
  - review feedback repair loop
  - final report evidence
  - PR readiness checklist
  - PR creation only if authorized in the active environment
- It does not own:
  - new feature scope beyond fixing issues found by gates
  - new Initiative/Epic planning decisions
  - destructive operations
  - credentialed external mutation without explicit authorization
  - PR merge unless explicitly authorized

## 最終完了条件

- All planned Issues are complete, or any deferral has explicit evidence and is accepted by the main orchestrator.
- Initiative/Epic templates are updated in provider-side scaffold assets.
- Planning and execution skills/docs are consistent with the updated templates and adopted ADRs.
- Automated checks are passing or failures are documented with acceptable reason and follow-up.
- Manual tests are executed and summarized.
- Raw manual-test files are not committed.
- Dogfooding mirror impact is inspected.
- Reviewer comments are addressed and affected checks are rerun.
- PR description includes scope, validation, manual tests, and follow-ups.
- PR is ready for review/merge; merge is not performed without explicit authorization.

## 依存 / ブロッカー

- D-001:
  - Canonical `design.md` must be concretized before final plan adoption; current observed canonical design was still template-shaped.
- D-002:
  - Fresh `spec-reviewer` pass remains required before downstream Issue scaffold / planning.
- D-003:
  - Actual Issue IDs do not exist yet and must not be invented in this draft.
- D-004:
  - `.agent/index.json` and `.agent/deps-issues.json` were absent at read time; run `./spec-dock/scripts/spec-dock sync` before using generated readiness projection as evidence.

## 未確定事項

- none blocking for this draft:
  - Existing interviews and accepted ADRs resolve the Issue slicing, PR boundary, canonical detail, scope-layering publication, architecture-neutral template policy, complete understanding policy, and Option B handoff inspection policy.
- remaining integration gaps:
  - Main orchestrator must integrate or reject this delegated draft.
  - Fresh `spec-reviewer` must review the canonical plan after integration.
```

## 1. Requirement Coverage

- E-RQ-001 and E-AC-001/002 are covered by Issues 01 and 02, with Issue 05/06 validation.
- E-RQ-002 and E-AC-003 are covered by Issue 03.
- E-RQ-003 is covered by Issue 03 guidance, Issue 05 validation, and final report evidence in Issue 06.
- E-RQ-004 is covered by Issues 01, 02, and 05, using the accepted architecture-neutral ADR.
- E-RQ-005 is covered by Issue 03 and Issue 05, using the accepted scope-layering publication ADR.
- E-RQ-006 and E-RQ-007 are covered by Issue 02 and Issue 04 with Issue 05 smoke coverage.
- E-RQ-008 and E-AC-006 are covered by Issue 06.

## 2. Existing Context Findings

- Active context points to `init-local-00003` and `epic-00270`; no active Issue is set.
- Current concrete requirement already contains E-RQ-001 through E-RQ-008 and E-AC-001 through E-AC-006.
- Current canonical `design.md` was still template-shaped when read, so final plan adoption should wait for a concrete design and fresh reviewer pass.
- `report.md` EAL records V3 intake, user interviews, split artifacts, and accepted ADRs as adopted source evidence.
- `.agent/index.json` and `.agent/deps-issues.json` were absent when checked; `sync` should be rerun before using generated readiness projections.

## 3. Design Decisions

- Preserve the provisional six-Issue baseline rather than creating Issues now.
- Preserve adopted flexibility gate: re-slicing is allowed only when the six-Issue baseline harms independent reviewability, responsibility boundary, verifiability, or PR delivery, and only after canonical plan update plus fresh reviewer gate.
- Preserve one-PR default; Issue-level PR splitting is not a normal plan path.
- Use `strict` for Issues 01-05 and `critical` for Issue 06.
- Apply Option B handoff inspection: machine-checkable structural omissions block; semantic sufficiency becomes reviewer finding.
- Keep Epic execution as a coordinator, not a semantic reviewer replacement.

## 4. Alternatives Considered

- Fixed six Issues with no re-slicing:
  - Rejected by adopted user evidence because planning discoveries may expose a better boundary.
- Open-ended Issue creation:
  - Rejected because it risks Issue sprawl and decision-only execution containers.
- Issue-per-PR delivery:
  - Rejected as default by adopted delivery-boundary interview; it can be reconsidered only if one-PR delivery breaks down.
- Strong semantic blocking at Epic execution:
  - Rejected by Option B handoff policy because it would make the coordinator act as a reviewer.

## 5. Boundary / Contract Model

- Initiative owns strategic change, capability landscape, context ownership, source of truth, strategic invariants, transition architecture, and Epic handoff.
- Epic owns capability/model envelope, lifecycle, cross-Issue invariants, contract portfolio, design slice catalog, Issue handoff, dependency/order, and Epic final gate.
- Issue owns one observable behavior or local model/contract delta and local verification.
- Issue plan owns implementation sequencing, concrete test cases, validation ladder, and step-local evidence.
- Report owns observed evidence, reviewer verdicts, deviations, adoption ledger, and delivery evidence.
- Raw artifacts remain evidence; canonical authority requires main-orchestrator integration and reviewer-gated canonical docs or accepted ADRs.

## 6. Dependency Analysis

- Issue 01 and Issue 02 form the template foundation.
- Issue 03 depends on 01/02 vocabulary and the accepted scope-layering / architecture-neutral / complete-understanding ADRs.
- Issue 04 depends on Epic template handoff fields from Issue 02 and should coordinate with Issue 03 wording.
- Issue 05 depends on 01-04 because smoke tests must observe the integrated template/docs/skill behavior.
- Issue 06 depends on 01-05 and owns final quality, manual tests, review repair, and PR readiness.

## 7. Source of Record

- Primary draft source: active epic requirement read on 2026-07-02.
- Evidence sources:
  - V3 full intake artifact for baseline Issues and quality gate.
  - User interviews for six-Issue flexibility, one-PR default, canonical detail, scope-layering strictness, and handoff inspection policy.
  - Split discussion artifacts for scope authority, template model, Issue slicing/handoff, and quality/delivery model.
  - Accepted ADRs for scope-layering publication, architecture-neutral templates, and complete understanding before canonical authoring.
  - `report.md` EAL for adoption status.
- Non-source:
  - This delegated draft is not a source of record until integrated by the main orchestrator.

## 8. Data Flow / Domain Model / Interface Contract

Planning flow:

```text
V3 raw intake / repo evidence / interviews / accepted ADRs
  -> canonical requirement/design/plan by main orchestrator
    -> fresh spec-reviewer pass
      -> downstream Issue scaffold/planning
        -> Issue execution
          -> final quality gate and one-PR readiness
```

Epic-to-Issue handoff interface:

- parent trace: Initiative/Epic IDs, E-RQ/E-AC, design IDs
- slice contract: purpose, observable outcome, allowed local delta, forbidden parent boundary changes
- quality contract: suggested grade, required verification, reviewer focus, evidence type
- coordination contract: dependencies, blockers, escalation triggers, relevant artifacts/ADRs

## 9. File / Module Change Plan

Expected implementation surfaces for future Issues:

- Issue 01:
  - `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
  - `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- Issue 02:
  - `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/design.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- Issue 03:
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - relevant phase docs and planning skills under `src/spec_dock/assets/install_root/.agents/skills/`
- Issue 04:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
- Issue 05:
  - tests under the relevant `tests/` lanes for template/scaffold/doc/skill smoke checks
- Issue 06:
  - no planned feature surface; owns validation evidence, repair loop, and PR readiness

This draft does not edit any implementation, test, package/config, canonical doc, or GitHub state.

## 10. Migration / Compatibility / Rollback

- Migration:
  - Provider-side scaffold assets change future generated templates/docs/skills.
  - Dogfooding workspace impact must be inspected after scaffold-affecting changes.
- Compatibility:
  - Existing Issue grade/TDD workflow remains the downstream source of truth for Issue execution.
  - DDD/EDA terms remain optional support, not mandatory template contract.
- Rollback:
  - Revert Issue-level changes by slice if validation fails.
  - Do not rollback by restoring raw artifact authority or decision-only execution Issues.
  - If `scope-layering.md` becomes too broad, narrow it and keep lifecycle details in workflow docs.

## 11. Observability

- `report.md` EAL should record integration of this draft if adopted.
- Spec Authoring Gate should record canonical plan review state.
- Final Issue should record:
  - command, exit code, pass/fail, and summary for automated checks
  - manual test scenario summary
  - dogfooding mirror inspection notes
  - review comments and repair actions
  - PR readiness evidence

## 12. Test Strategy

- Narrow checks per implementation Issue:
  - template structure inspection / snapshot or unit checks
  - skill text smoke checks for reviewer gates and artifact guidance
  - workflow doc link checks for scope-layering reference
  - negative checks for Issue-level TDD/private implementation obligations in Initiative/Epic templates
- Integrated checks:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- Manual checks:
  - fresh Initiative/Epic scaffold shape
  - planning skill read-through
  - Epic execution handoff coordinator read-through
  - `artifacts/` vs legacy `discussions/` guidance
  - dogfooding coherence after validate/sync

## 13. ADR Candidates

- No new ADR is required by this plan draft.
- Existing accepted ADRs already cover:
  - scope-layering reference publication surface
  - architecture-neutral template authoring policy
  - complete understanding before canonical authoring
- Future ADR may be needed only if:
  - re-slicing changes a durable global planning rule
  - PR boundary policy becomes a reusable SpecDock-wide delivery rule
  - handoff inspection semantics move from Epic-specific workflow into global runtime validation

## 14. Risks

- Canonical `design.md` was still template-shaped; adopting a final plan before design concretization would push design gaps downstream.
- One-PR default can become too large; plan includes a reconsideration path but does not normalize PR splitting.
- Scope-layering smoke checks can become brittle if they try to judge semantic sufficiency mechanically.
- Template redesign can become too DDD/EDA-heavy despite the accepted architecture-neutral ADR.
- Missing generated `.agent/index.json` / `.agent/deps-issues.json` means readiness projection evidence should be refreshed before downstream planning.

## 15. Requirement Clarification Requests

- none blocking for this delegated draft.
- Main orchestrator may still need to clarify or decide:
  - whether to integrate this plan before or after a concrete `design.md` draft is reviewed
  - whether the existing design draft artifact should be adopted, superseded, or ignored
  - whether to refresh `sync` before reviewer handoff

## 16. Integration Notes for Main Orchestrator

- Changed artifact path:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t032014z-disc-epic-plan-draft-upstream-planning-governance-templates.md`
- Source requirement revision:
  - active `epic-00270` requirement read on 2026-07-02, status `draft`, containing E-RQ-001 through E-RQ-008 and E-AC-001 through E-AC-006.
- Lightweight provenance:
  - Created through `./spec-dock/scripts/spec-dock new artifact disc --epic epic-00270 ...`.
  - Edited only the returned scope-local artifact path.
  - Used active docs, V3 intake, split discussion artifacts, accepted ADRs, and `report.md` EAL.
- Leaf evidence used:
  - none. No depth=2 delegated leaf evidence was requested in this run.
- Forbidden actions avoided:
  - no canonical `requirement.md` / `design.md` / `plan.md` / `report.md` edit
  - no implementation, test, package/config, agent config, GitHub workflow, or secret edit
  - no Issue creation
  - no promotion, closeout, reviewer-pass claim, PR creation, GitHub mutation, or user-dialogue ownership claim
- Unresolved requirement gaps:
  - none blocking for draft evidence.
  - integration gap: canonical `design.md` still needs concrete adoption/review before final plan promotion.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
