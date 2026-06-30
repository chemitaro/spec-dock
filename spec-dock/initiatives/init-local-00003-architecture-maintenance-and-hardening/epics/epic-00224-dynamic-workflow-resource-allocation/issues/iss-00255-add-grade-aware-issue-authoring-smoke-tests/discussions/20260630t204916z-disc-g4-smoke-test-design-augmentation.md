---
created_by_role: system-architect
scope_id: iss-00255
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/phase_plan_issue.md
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_workflow.py
  - tests/unit/domain/test_workflow_state.py
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00255-add-grade-aware-issue-authoring-smoke-tests/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: failed
---

# G4 Smoke Test Design Augmentation

## 1. Requirement Coverage

This draft covers `iss-00255` AC-001 through AC-008 by treating G4 as an integrated smoke closure slice, not a new implementation slice for R0, G1, G2, or G3 logic.

- AC-001 and AC-002: verify grade-specific authoring guidance and M99 gate text across Lite, Standard, Strict, and Critical fixtures.
- AC-003 and AC-004: reuse `new doc` profile draft routing and no-write fail-closed surfaces.
- AC-005: reuse readiness false-positive surfaces for placeholder, heading-only, stale evidence, missing adoption evidence, and stale reviewer evidence.
- AC-006: verify the minimum report evidence relation among delegated specialist evidence, Evidence Adoption Ledger, Grade Specialist Evidence Gate, and fresh `spec-reviewer`.
- AC-007: add a provider/dogfooding parity inspection for docs and profile templates relevant to grade-aware authoring.
- AC-008: require report evidence to record commands, results, skipped checks, and residual risk after smoke execution.

## 2. Existing Context Findings

Issue `design.md` currently names smoke surfaces and candidate files, but it does not specify which surface belongs in which existing test file, how fixtures should be shared, or what G4 must not reimplement.

Existing tests already provide strong anchors:

- `tests/cli_runtime/test_new.py` owns `new doc` discussion creation, `authorized_profile` draft source routing, invalid/missing/stale `.assurance.json` no-write behavior, and profile template validity.
- `tests/cli_runtime/test_workflow.py` owns CLI-level `workflow status` and `guidance issue-execution` readiness behavior, including report evidence blocks and placeholder artifact blocks.
- `tests/unit/domain/test_workflow_state.py` owns domain-level report evidence gate predicates and grade-specific specialist/fallback/fresh review validation.
- `tests/unit/infra/test_init_update.py` owns provider-to-dogfooding asset parity mapping and should remain the parity inspection home for shipped docs/templates.

## 3. Design Decisions

1. Keep G4 as a smoke matrix over public behavior and shipped asset parity.
2. Do not add new runtime policy branches in G4. Any failing smoke should point back to R0, G1, G2, or G3.
3. Place CLI draft routing smoke in `tests/cli_runtime/test_new.py` because the public contract is `spec-dock new doc`.
4. Place CLI readiness smoke in `tests/cli_runtime/test_workflow.py` because the public contract is `workflow status` / `guidance issue-execution`.
5. Place low-level evidence gate matrix in `tests/unit/domain/test_workflow_state.py` because it already isolates `evaluate_report_evidence_gate`.
6. Place provider/dogfooding docs/template parity in `tests/unit/infra/test_init_update.py` because it already owns `_DOGFOODING_MIRROR_PROVIDER_ASSET_MAP`.
7. Keep Epic single-PR policy out of these tests. G4 records local checkpoint evidence; PR Delivery Gate and Merge Preparation Gate remain Epic final quality gate concerns.

## 4. Alternatives Considered

- Single broad end-to-end test: rejected because it would blur failure ownership and make R0/G1/G2/G3 regressions harder to diagnose.
- New `tests/cli_runtime/test_grade_aware_authoring.py`: possible, but weaker locality than extending the existing owner files. Only use a new file if smoke setup becomes too large for the existing classes.
- Provider/dogfooding parity in a shell script: rejected for unit regression because the existing pytest parity map is hermetic and already tracks shipped assets.
- Full `uv run pytest` as the only signal: rejected because G4 needs targeted failure localization before any broader suite.

## 5. Boundary / Contract Model

G4 should assert boundaries, not implement them:

- R0 owns artifact readiness predicates and no-ready false positive prevention.
- G1 owns grade-aware planning guidance text and Lite non-default rule.
- G2 owns delegated specialist draft routing and profile template source selection.
- G3 owns report evidence gate, EAL, delegated draft adoption, and fresh review evidence.
- G4 owns integrated smoke detection that these surfaces still agree.

The smoke contract is: "Given representative fixtures for each grade and evidence state, public commands and domain predicates expose the expected allow/block result without mutating canonical docs or requiring live GitHub."

## 6. Dependency Analysis

Dependency order for tests should follow the upstream slice ownership:

1. Domain report evidence fixture helpers in `test_workflow_state.py`.
2. CLI workflow fixture helpers in `test_workflow.py`.
3. CLI draft routing fixture helpers in `test_new.py`.
4. Provider/dogfooding parity assertion in `test_init_update.py`.

G4 should not introduce a dependency from domain tests to CLI harnesses. CLI tests may build on hermetic temp repos and runtime commands; domain tests should stay pure function tests.

## 7. Source of Record

Source authority for this design proposal:

- Epic `requirement.md`: E-RQ-006, E-RQ-022, E-AC-006, E-AC-022.
- Epic `design.md`: `Profile Template Resolver`, `Issue Draft Authoring Router`, `Spec Authoring Evidence Gate`, `Epic PR Integration Gate`.
- Epic `plan.md`: G4 scope and Epic single-PR execution model.
- Issue `requirement.md`: AC-001 through AC-008.
- Existing test files listed in `source_paths`.

This draft is not source of record. It is adoption input for the main orchestrator.

## 8. Data Flow / Domain Model / Interface Contract

Representative G4 fixture flow:

```text
fixture issue
  + .assurance.json authorized_profile
  + requirement/design/plan/report evidence state
  + provider/dogfooding asset pair
        |
        +--> new doc draft-design/draft-plan
        |       expects selected issue-profiles/<profile> template or no-write failure
        |
        +--> workflow status / guidance issue-execution
        |       expects ready or blocked reason_code
        |
        +--> evaluate_report_evidence_gate
        |       expects grade-specific evidence verdict
        |
        +--> provider/dogfooding parity assertion
                expects semantic parity or documented exception
```

The interface contract should stay at public seams:

- CLI stdout/stderr, return code, projected runbook JSON, and discussion file count for `new doc`.
- CLI JSON / projected runbook state and `reason_code` for workflow readiness.
- Domain result status and `reason_code` for report evidence.
- File content equality or explicitly documented exception for provider/dogfooding parity.

## 9. File / Module Change Plan

Recommended placement:

- `tests/cli_runtime/test_new.py`
  - Add a compact `profile_cases` matrix that includes Lite in addition to existing Standard / Strict / Critical draft routing coverage if Lite profile templates exist.
  - Add an integrated no-write assertion for missing / invalid / stale `.assurance.json` that verifies the discussion file set is unchanged for both `draft-design` and `draft-plan`.
  - Do not duplicate profile template validation tests already present.

- `tests/cli_runtime/test_workflow.py`
  - Add smoke fixtures for Lite, Standard, Strict, Critical report evidence readiness.
  - Assert Lite does not require intermediate commit/full static analysis language in current guidance.
  - Assert Standard / Strict / Critical expose M99 quality gate obligations through plan/report evidence or guidance text, depending on the implemented surface.
  - Keep placeholder / heading-only / stale evidence regressions near existing readiness tests.

- `tests/unit/domain/test_workflow_state.py`
  - Add or consolidate a table-driven evidence gate smoke covering:
    - Lite `not applicable` specialist row plus fresh spec-reviewer pass.
    - Standard skip reason or specialist evidence.
    - Strict specialist used or explicit unavailable/manual fallback evidence.
    - Critical explicit approval plus risk acceptance for fallback.
  - Add negative rows for cross-profile grade row, stale reviewer row, unresolved EAL, and missing delegated draft evidence if any are not already represented by existing tests.

- `tests/unit/infra/test_init_update.py`
  - Extend `_DOGFOODING_MIRROR_PROVIDER_ASSET_MAP` coverage or equivalent assertion to include `templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` and grade-aware docs if not already covered.
  - Treat missing parity entries as test failures unless the design records a deliberate dogfooding-only exception.

No implementation source, canonical docs, package/config, or GitHub workflow files should be edited as part of this delegated draft.

## 10. Migration / Compatibility / Rollback

Migration impact is test-only for G4. The smoke tests should be hermetic and should not require live GitHub or production telemetry.

Compatibility expectations:

- Existing Issue `draft-requirement` and Initiative/Epic `draft-design` / `draft-plan` behavior remains unchanged.
- Existing strict-legacy Issue execution remains supported.
- G4 must not convert legacy Issues to adaptive workflow.
- G4 must not enable automatic Lite default.

Rollback is straightforward: revert only G4 test additions and any report evidence updates. If a smoke failure exposes an upstream R0/G1/G2/G3 gap, fix that upstream-owned surface rather than weakening G4 expectations.

## 11. Observability

G4 observability should be report evidence, not production telemetry.

The Issue report should capture:

- Targeted test commands and pass/fail result.
- Any skipped check and exact reason.
- Smoke matrix rows executed for Lite / Standard / Strict / Critical.
- Provider/dogfooding parity result and exceptions, if any.
- Residual risk when a smoke fixture is representative rather than exhaustive.

No raw shell transcript, private reasoning, secret, or credential material should be recorded.

## 12. Test Strategy

Use a four-lane smoke strategy:

| Lane | File | Primary failure detected |
|---|---|---|
| Draft routing | `tests/cli_runtime/test_new.py` | G2 regression in profile template selection or fail-closed no-write behavior |
| Readiness CLI | `tests/cli_runtime/test_workflow.py` | R0/G3 regression in execution readiness and report evidence blocks |
| Evidence domain | `tests/unit/domain/test_workflow_state.py` | G3 predicate regression without CLI fixture noise |
| Parity | `tests/unit/infra/test_init_update.py` | Provider/dogfooding drift for docs/templates |

Recommended focused verification after implementation:

```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py tests/unit/infra/test_init_update.py
./spec-dock/scripts/spec-dock validate
```

Full `uv run pytest` can be deferred to the Epic final quality gate if the focused lane and validate pass, unless the implementation touches shared helpers beyond these surfaces.

## 13. ADR Candidates

No new ADR is required for this issue if G4 only codifies the Epic design and the accepted grade-aware authoring rules.

ADR candidate only if implementation discovers a new durable policy such as:

- Provider/dogfooding parity intentionally allowing non-byte-identical profile templates.
- M99 gate semantics changing across profiles.
- Automatic Lite default activation or relaxation.

Those are out of scope for G4 and should block or route back to Epic-level decision handling.

## 14. Risks

- Existing `iss-00255` design is too shallow for plan review because "配置候補" names files without assigning test ownership.
- Over-broad end-to-end smoke could hide which upstream slice regressed.
- Provider/dogfooding parity may be brittle if assertions require byte equality where generated local differences are legitimate.
- Existing target `discussions/` already had an untracked draft before this run, so this delegated output is adoption-ineligible until the orchestrator resolves baseline dirtiness and reruns a post-run diff guard.

## 15. Requirement Clarification Requests

None blocking.

Non-blocking clarification candidates for the main orchestrator:

- Should G4 require Lite `draft-design` / `draft-plan` routing smoke if Lite profile templates are present, or should Lite be limited to guidance/report evidence smoke because automatic Lite remains disabled?
- Should provider/dogfooding parity for profile templates be byte-identical, or should frontmatter/path-local generated differences be explicitly normalized?

## 16. Integration Notes for Main Orchestrator

Recommended canonical integration into Issue `design.md`:

- Replace "配置候補" with an owner table mapping each smoke surface to the exact test file and fixture strategy.
- Add a "G4 responsibility boundary" subsection that states G4 detects R0/G1/G2/G3 integration drift and does not implement upstream logic.
- Add "provider / dogfooding parity" as an explicit design contract, including intended exact-match or documented-exception semantics.
- Add "Epic single PR boundary" stating Issue M99 is a local checkpoint and PR Delivery / Merge Preparation Gates remain in the Epic final quality gate.

Recommended integration into Issue `plan.md`:

- Convert M1-M6/M90 into step-local closure IDs and test commands.
- Add explicit report evidence destination rows for smoke matrix, parity inspection, skipped checks, and residual risks.

Recommended integration into Issue `report.md`:

- Record this draft in Delegated Draft Evidence and Evidence Adoption Ledger only after main orchestrator inspection.
- Keep `adoption_status` unreviewed until canonical integration and fresh `spec-reviewer` review.
