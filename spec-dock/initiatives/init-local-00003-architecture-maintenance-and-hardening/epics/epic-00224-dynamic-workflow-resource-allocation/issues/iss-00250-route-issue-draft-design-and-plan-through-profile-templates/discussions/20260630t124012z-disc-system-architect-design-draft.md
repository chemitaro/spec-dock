---
created_by_role: system-architect
scope_id: iss-00250
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/discussions/20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/discussions/20260630t111316z-adr-grade-aware-issue-authoring-rules.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_assurance_compose.py
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/phase_design.md
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/plan.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py
  - tests/cli_runtime/test_new.py
  - src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not-run
---

# System Architect Design Draft: Issue Draft Design And Plan Profile Routing

Source requirement revision: `iss-00250` `requirement.md`, final update `2026-06-30`, related GitHub `#250`, declared `Issue Grade: "strict"`.

Lightweight provenance: this draft was created through `./spec-dock/scripts/spec-dock new doc disc --issue iss-00250 --title "System Architect Design Draft"` and then edited only at the returned issue-local discussion path. No leaf agent evidence was requested or used. Forbidden actions avoided: no canonical doc edit, no source or test edit, no package/config edit, no GitHub mutation, no phase promotion, no reviewer-pass claim, and no user-dialogue ownership.

## 1. Requirement Coverage

| Requirement | Design coverage |
|---|---|
| REQ-001 / AC-001 / AC-003 | Issue `draft-design` must select `templates/issue-profiles/<authorized_profile>/design.md` after verifying the target issue `.assurance.json`. |
| REQ-002 / AC-002 / AC-003 | Issue `draft-plan` must select `templates/issue-profiles/<authorized_profile>/plan.md` after the same contract verification. |
| REQ-003 / AC-006 | Issue `draft-requirement` continues to use `templates/issue/requirement.md`; it must not require `.assurance.json`. |
| REQ-004 / AC-006 | Initiative and Epic `draft-design` / `draft-plan` continue to use `templates/{initiative,epic}/{design,plan}.md`. |
| REQ-005 / AC-004 / AC-005 | Missing, invalid, legacy-path, symlinked, or stale `.assurance.json` fails before discussion path write. No fallback or normalized thin draft is produced. |
| REQ-006 | Error text must include the reason and direct the operator to concretize `requirement.md`, run `assurance classify --stage requirement`, and rerun required compose / verification. |
| REQ-007 / REQ-008 | Only the target issue `discussions/` file is written; canonical `design.md` / `plan.md` and authority/adoption frontmatter are not written by `new doc`. |
| REQ-009 / REQ-010 | Provider runtime, shipped docs, dogfooding docs, and CLI regression tests must all describe and test the same grade-aware routing. |

## 2. Existing Context Findings

- `create_node.py` currently maps `draft-design` and `draft-plan` to `design` and `plan`, then resolves `spec-dock/templates/<scope_kind>/<target>.md`. For Issue scope this selects the compose-before placeholder files.
- `_normalize_draft_discussion_text()` hides `artifact_state: awaiting-assurance-compose` and replaces the Issue design/plan body with a thin generic draft. That makes the output look usable while bypassing the profile template pack.
- `assurance.compose_assurance()` already verifies `.assurance.json` through `AssuranceStore.verify_contract()` and loads profile templates through `ArtifactStore.load_profile_artifact_template()`.
- `ArtifactStore.load_profile_artifact_template()` validates profile name, artifact kind, path containment, regular-file status, existence, and non-empty body. It returns a body-only model for compose, not a full markdown template source suitable for `new doc`.
- `AssuranceStore.verify_contract()` distinguishes missing, invalid, and stale source binding states. This is the correct fail-closed authority for draft design/plan routing.
- `tests/cli_runtime/test_new.py` currently fixes the old behavior by asserting Issue `draft-design` comes from `templates/issue/design.md`.
- `workflow_issue.md` and `phase_design.md` already say Issue `templates/issue/design.md` and `templates/issue/plan.md` are not manual authoring starts; profile templates are the real Issue design/plan sources after classification.
- `iss-00250` has a requirement grade of `strict`, but the current issue `design.md` / `plan.md` contents are Standard template scaffolds. Main orchestrator should resolve that canonical mismatch before adoption.

## 3. Design Decisions

- [N] Add a profile-aware draft source resolver used only for Issue `draft-design` and Issue `draft-plan`.
- [N] The resolver must verify the target issue assurance contract before resolving a profile template. It must use `authorized_profile`, not `lite_candidate`, user-provided title text, or a default profile.
- [N] Missing, invalid, legacy-path, symlinked, stale, unsupported-profile, missing-template, non-file-template, symlink-escape, or empty-template cases fail before discussion file write.
- [N] Do not produce a fallback draft from `templates/issue/design.md` or `templates/issue/plan.md` for Issue design/plan.
- [N] Preserve the existing generic draft path for Issue `draft-requirement` and all Initiative/Epic draft artifacts.
- [P] Refactor `ArtifactStore` with a shared profile template path/text loader so compose and `new doc` share validation without coupling `create_node.py` directly to profile directory internals.
- [P] Add a narrow application-level `DraftTemplateSourceResolver` or equivalent dependency to `create_discussion_doc`, wired in CLI bootstrap from existing `AssuranceStore` and `ArtifactStore`.
- [N] Remove or bypass `_normalize_draft_discussion_text()` for Issue profile-sourced `draft-design` / `draft-plan`; profile templates are already authoring sources and must not be collapsed into the thin legacy body.

## 4. Alternatives Considered

| Alternative | Decision | Reason |
|---|---|---|
| Keep current scope-template routing | Reject | It conflicts with Issue #247 and ADR grade-aware authoring rules. It creates drafts that differ from canonical composed artifacts. |
| Automatic Standard fallback when `.assurance.json` is absent | Reject | Violates Lite automatic default prohibition and masks stale or unclassified requirements. |
| Use `templates/issue/design.md` / `plan.md` but keep placeholder text visible | Reject | It correctly signals incompleteness but still lets specialists start from the wrong source. |
| Add `templates/issue-profiles/unclassified` | Defer/reject for this issue | It creates another quasi-authoring path for classified artifacts. Use `disc` or `research` before classification instead. |
| Directly read `spec-dock/templates/issue-profiles/...` inside `create_node.py` | Avoid if practical | It works, but duplicates containment and validation rules already owned by `ArtifactStore`. |

## 5. Boundary / Contract Model

Public CLI contract:

- `spec-dock new doc draft-design --issue <id>` and `draft-plan` now require a valid, non-stale `.assurance.json` for that Issue.
- Success still prints the same `new doc` result shape and writes one timestamped Markdown under the issue `discussions/`.
- Failure returns non-zero and no discussion file is written.

Internal contracts:

- `CreateDiscussionDocRequest` remains unchanged unless implementation discovers a need for richer error typing.
- A draft template source resolution boundary returns either:
  - a canonical template path for legacy generic draft rendering; or
  - profile template markdown text plus metadata for Issue profile draft rendering.
- Contract verification uses `AssuranceStore.verify_contract(target)`, where `target` is the resolved Issue scope.
- Profile template validation uses the same allowed profiles and filesystem guards as `ArtifactStore.load_profile_artifact_template()`.

Authority:

- `.assurance.json` `classification.authorized_profile` is the only profile selection authority.
- `draft-design` / `draft-plan` discussion files are evidence only. They do not set `authority: accepted`, `adoption_status: adopted`, or non-empty `reflected_to`.

## 6. Dependency Analysis

Recommended dependency direction:

```text
commands/new.py
  -> application/create_node.py
      -> DraftTemplateSourceResolver protocol
          -> infra/assurance_store.py
          -> infra/artifact_store.py
      -> template_scaffolder for replacement/write
```

Keep domain purity:

- `domain.assurance` remains contract validation and profile vocabulary.
- `application.create_node` orchestrates `new doc` behavior but does not own filesystem security details for profile templates.
- `infra.artifact_store` owns profile template filesystem validation.
- `infra.assurance_store` owns issue target resolution and contract freshness.

Deletion test coupling:

- If the old `_normalize_draft_discussion_text()` branch for Issue design/plan is removed, Issue profile draft tests should still pass.
- If `templates/issue/design.md` is changed back to a placeholder, Issue profile draft tests should not fail because they no longer read it.
- If `.assurance.json` is deleted or stale, Issue profile draft tests must fail before writing.

## 7. Source of Record

Normative sources for the implementation:

- `iss-00250/requirement.md`: specific requirements and acceptance criteria.
- `20260630t111316z-adr-grade-aware-issue-authoring-rules.md`: `authorized_profile` is workflow/template authority; Lite automatic default is prohibited.
- `workflow_issue.md` and `phase_design.md`: Issue design/plan common templates are compose-before placeholders.
- `assurance_store.py`: canonical assurance contract read/verify semantics.
- `artifact_store.py`: canonical profile template filesystem validation semantics.

Secondary evidence:

- `20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md`: current routing bug and recommended Option A + Option B.
- `tests/cli_runtime/test_new.py` and `tests/cli_runtime/test_assurance_compose.py`: regression surfaces.

## 8. Data Flow / Domain Model / Interface Contract

Success flow for Issue `draft-design`:

```text
new doc draft-design --issue iss-XXXXX
  -> resolve scope node from graph
  -> detect scope.kind == issue and doc_type == draft-design
  -> resolve issue target from scope path or id
  -> verify .assurance.json
  -> read contract.classification.authorized_profile
  -> load full profile template text for issue-profiles/<profile>/design.md
  -> render replacements
  -> allocate timestamped discussion filename
  -> write rendered discussion draft
```

Failure flow:

```text
new doc draft-plan --issue iss-XXXXX
  -> verify .assurance.json
  -> status != valid or reason == stale_source_binding
  -> raise error with reason and remediation
  -> no filename write
```

Draft artifact mapping:

| Scope | draft-requirement | draft-design | draft-plan |
|---|---|---|---|
| Initiative | `templates/initiative/requirement.md` | `templates/initiative/design.md` | `templates/initiative/plan.md` |
| Epic | `templates/epic/requirement.md` | `templates/epic/design.md` | `templates/epic/plan.md` |
| Issue | `templates/issue/requirement.md` | `templates/issue-profiles/<authorized_profile>/design.md` | `templates/issue-profiles/<authorized_profile>/plan.md` |

## 9. File / Module Change Plan

Implementation files:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - Add Issue profile draft routing branch for `draft-design` / `draft-plan`.
  - Fail before discussion write when profile source resolution fails.
  - Stop applying legacy thin-body normalization to profile-sourced Issue design/plan drafts.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
  - Extract a reusable profile artifact template path/text loader.
  - Keep existing compose-facing `load_profile_artifact_template()` behavior intact.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` and possibly `application/ports.py`
  - Wire the new resolver or ports without broadening unrelated use cases.

Tests:

- `tests/cli_runtime/test_new.py`
  - Replace old Issue `draft-design` expectation with classified Issue fixtures.
  - Add missing / invalid / stale fail-closed assertions for Issue `draft-design` and `draft-plan`.
  - Preserve `draft-requirement`, Initiative, and Epic cases.
- `tests/cli_runtime/test_assurance_compose.py`
  - Keep existing compose tests as guardrails; add only if shared template loader changes need coverage.
- Optional unit tests under `tests/unit/application/` if a separate resolver is introduced.

Docs:

- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- Dogfooding mirror docs if the provider asset update flow requires checked-in sync.

## 10. Migration / Compatibility / Rollback

Compatibility:

- Existing discussion drafts are grandfathered and must not be rewritten or invalidated.
- Existing unclassified Issues can still create `disc`, `research`, and `draft-requirement`; only Issue `draft-design` / `draft-plan` becomes contract-gated.
- Initiative and Epic draft behavior remains unchanged.

Migration:

- No migration of existing user files is required.
- No canonical `design.md` / `plan.md` rewrite is required by this issue.

Rollback:

- Reverting the routing change returns to thin generic drafts, but that reintroduces ADR inconsistency.
- Safer rollback for a failed implementation is to keep fail-closed behavior and temporarily document use of `disc` / `research` before classification.

Partial failure:

- Contract verification or template load failure must occur before `write_text(dest_path, ...)`.
- Lock acquisition/release behavior should stay unchanged.

## 11. Observability

- CLI failure should include:
  - target issue id or path,
  - doc type,
  - contract reason such as `missing_assurance_contract`, `invalid_json`, `invalid_schema`, or `stale_source_binding`,
  - remediation commands.
- JSON output is not currently part of `new doc`; do not add a new output format unless existing command architecture already supports it.
- Tests should assert absence of a newly created matching discussion file on failure.
- `report.md` adoption, if any, should record that this draft is unreviewed evidence and not a reviewer pass.

## 12. Test Strategy

Focused CLI regression tests:

- Classified Standard Issue `draft-design` creates a discussion draft containing `Issue 設計書（Standard）`.
- Classified Standard Issue `draft-plan` creates a discussion draft containing `Issue 実装計画書（Standard / TDD）` and Standard-specific plan sections.
- Classified Strict and Critical fixtures create drafts containing their profile headings.
- Missing `.assurance.json` for Issue `draft-design` / `draft-plan` exits non-zero and creates no `*-draft-design-*` or `*-draft-plan-*` file.
- Invalid JSON / invalid schema / stale source binding each exits non-zero and creates no fallback file.
- Issue `draft-requirement` still succeeds without `.assurance.json`.
- Initiative/Epic `draft-design` / `draft-plan` still use scope canonical templates.

Verification command target:

```sh
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py
```

Broaden to `uv run pytest tests/cli_runtime` only if the implementation touches bootstrap, ports, or shared store behavior beyond the resolver boundary.

## 13. ADR Candidates

- No new ADR is required if implementation follows the accepted grade-aware authoring ADR.
- ADR candidate only if the team decides to allow an unclassified Issue design/plan draft mode, because that would weaken the accepted fail-closed profile authority.
- ADR candidate if `new doc` command output format or public error schema becomes a stable machine-readable contract.

## 14. Risks

- Current `iss-00250` canonical `design.md` / `plan.md` appear Standard while the requirement declares Strict. Adopting this draft should include a canonical grade/template correction or an explicit reason not to.
- Adding store dependencies directly into `create_node.py` could blur application/infra boundaries. Use a narrow resolver or port.
- Reusing `ArtifactStore.load_profile_artifact_template()` body-only result would lose profile template frontmatter. The draft source needs full markdown template text.
- Filename allocation before failure would leave empty or placeholder artifacts if implementation order is wrong. Resolve and verify source before write.
- Error messages that only say "missing template" may send users to edit templates instead of classifying the Issue. Include contract remediation.

## 15. Requirement Clarification Requests

- Confirm whether `iss-00250` canonical `design.md` and `plan.md` should be re-composed as Strict before implementation planning proceeds. Requirement says Strict; current canonical artifacts read as Standard scaffolds.
- Confirm whether failure remediation should mention `assurance compose --artifact all` or only `assurance classify --stage requirement`. Requirement REQ-006 asks for classify and necessary compose / verification; the draft recommends mentioning both.
- Confirm whether `new doc` should expose structured error details in the future. This draft assumes plain CLI error text is sufficient for this issue.

## 16. Integration Notes for Main Orchestrator

- Recommended adoption path:
  1. Resolve the `strict` requirement vs Standard canonical artifact mismatch.
  2. Reflect the boundary decisions into canonical `design.md`.
  3. Reflect the test ladder into canonical `plan.md`.
  4. Run a fresh `spec-reviewer` pass before implementation.
- Do not treat this discussion draft as canonical authority or reviewer approval.
- Unresolved requirement gaps: grade mismatch in current canonical issue artifacts; exact remediation wording.
- Leaf evidence used: none.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
