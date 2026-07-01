---
種別: disc
ID: "20260630t171038z-disc"
タイトル: "Implementation Plan Draft For Profile Aware Routing"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00253"]
関連: []
authority: "proposed"
created_by_role: implementation-planner
scope_id: iss-00253
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/rules/issue/discussions.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py
  - src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/design.md
  - src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/plan.md
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_assurance_compose.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
derived_from: []
---

# iss-00253 実装計画ドラフト: Issue draft-design / draft-plan の profile-aware routing

## 1. Plan Summary

このドラフトは `iss-00253` の canonical `plan.md` に統合するための planning evidence であり、canonical docs の直接更新や implementation readiness は主張しない。

実装目的は、Issue scope の `new doc draft-design` / `new doc draft-plan` だけを `.assurance.json` の verified `classification.authorized_profile` に対応する `templates/issue-profiles/<profile>/{design,plan}.md` へ route し、missing / invalid / stale assurance や invalid profile template では discussion file allocation 前に no-write fail-closed することである。`draft-requirement` と Initiative / Epic の draft docs は既存挙動を維持する。

Strict grade として、最小実装は runtime routing、template validation reuse、CLI regression、docs/rules parity、final local handoff gate を同じ issue-local checkpoint で閉じる。個別 PR は作成しない。

## 2. Requirement / Design Traceability

| Source | Planning implication |
|---|---|
| Issue AC-001 / AC-002 | Issue `draft-design` / `draft-plan` は verified `.assurance.json` の `authorized_profile` で profile template を選ぶ。 |
| Issue AC-003 | missing / invalid / stale assurance、unsupported profile、missing / empty / escaped template は discussion path allocation 前に fail-closed する。 |
| Issue AC-004 | `draft-requirement` と Initiative / Epic `draft-design` / `draft-plan` は現行 template source を維持する。 |
| Issue AC-005 | profile-sourced Issue design / plan draft には `_normalize_draft_discussion_text` の thin fallback 正規化を適用しない。 |
| Issue AC-006 | generated draft は authority accepted、adoption adopted、reviewer pass、phase completion、implementation readiness を自己主張しない。 |
| Issue AC-007 | `assurance compose` の profile template validation guard は退行させない。 |
| Epic E-RQ-022 / E-AC-022 | delegated specialist draft は discussion evidence であり、canonical adoption は main orchestrator と EAL が判断する。 |
| Epic G2 | `iss-00253` は G1 後、G3/G4 前の corrective tranche。個別 PR なしで local closure checkpoint を作る。 |

Source revision snapshot:

- Git HEAD inspected: `9d172bff002d2da41e5a5ad5fffa300449a00120`
- Issue requirement blob: `3c0b73d6b0a6d5b1338ca62eebea14716b956a71`
- Issue design blob: `2fccaabbe7bf2c27186b62c825097abfe69ae32e`
- Issue plan blob: `ce8fa64e457566106ce4b4b9e4ec5f3648223647`
- Epic requirement blob: `ea29e8c91edaedc7124f9aa4fcc8a9604838f0e7`
- Epic design blob: `985ee0faba2442d07504276a067ebd333f1fa68a`
- Epic plan blob: `e9c333512c016efc913c2728df8e9bab865e7bc5`

## 3. Milestones

### M0 Baseline / characterization

- Confirm current `new doc draft-*` flow in `create_node.py`:
  - `_draft_canonical_template_path()` selects `templates/<scope_kind>/{requirement,design,plan}.md`.
  - `_normalize_draft_discussion_text()` removes `artifact_state: awaiting-assurance-compose` and creates thin draft body.
- Confirm `ArtifactStore.load_profile_artifact_template()` already validates profile names, path containment, non-file, missing, and empty body.
- Confirm `AssuranceStore.verify_contract()` already returns stale source binding as invalid.
- Red evidence:
  - Existing `tests/cli_runtime/test_new.py::test_new_doc_creates_draft_artifacts_from_scope_specific_templates` currently expects Issue `draft-design` from `templates/issue/design.md`; this becomes the intentional outer Red after expected source changes.
- Green evidence:
  - No code change in M0.

### M1 Profile-aware success path

- Change target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_new.py`
- Plan:
  - Add profile-aware branch for `scope.kind == "issue"` and `doc_type in {"draft-design", "draft-plan"}` before discussion filename allocation.
  - Resolve active/requested issue to an issue-local target, verify `.assurance.json`, read `classification.authorized_profile`, then load full profile template through `ArtifactStore`.
  - Render full profile template with existing replacements and write discussion doc as evidence, not canonical artifact.
- Red tests:
  - Parametrize Standard / Strict / Critical Issue fixtures and assert `new doc draft-design --issue <id>` includes profile design template headings and does not include common `templates/issue/design.md` placeholder text.
  - Parametrize Standard / Strict / Critical Issue fixtures and assert `new doc draft-plan --issue <id>` includes profile plan template headings and does not include common `templates/issue/plan.md` placeholder text.
- Green tests:
  - `uv run pytest tests/cli_runtime/test_new.py -k "draft_design or draft_plan or scope_specific_templates"`

### M2 Fail-closed / no-write path

- Change target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py` only if a small reusable verifier method is needed.
  - `tests/cli_runtime/test_new.py`
- Plan:
  - Convert `AssuranceStoreResult.status != "valid"` into deterministic `RuntimeError` before `_allocate_discussion_doc_filename()`.
  - Preserve `reason` values such as `missing_assurance_contract`, `invalid_json`, `invalid_schema`, and `stale_source_binding` in CLI stderr/stdout-visible failure text.
  - Do not silent-repair `.assurance.json`; do not fallback to Standard.
- Red tests:
  - missing `.assurance.json`: command fails and `discussions` file count is unchanged.
  - invalid JSON `.assurance.json`: command fails and `discussions` file count is unchanged.
  - stale source binding: mutate `requirement.md` after classify, command fails and `discussions` file count is unchanged.
  - unsupported profile in contract fixture, if schema bypass fixture is feasible: command fails before write. If schema validation already rejects it, assert `invalid_schema` no-write.
- Green tests:
  - `uv run pytest tests/cli_runtime/test_new.py -k "assurance or fail_closed or no_write or draft"`

### M3 Profile template guard reuse

- Change target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_assurance_compose.py` for regression only.
- Plan:
  - Reuse `ArtifactStore.load_profile_artifact_template()` for `new doc` rather than duplicating path checks in `create_node.py`.
  - If `new doc` needs frontmatter plus body rather than body-only, add a narrow `load_profile_artifact_template_text()` or extend the dataclass conservatively; keep existing compose behavior stable.
  - Keep filesystem guards identical for missing template, symlink escape, non-file, and empty body.
- Red tests:
  - remove `templates/issue-profiles/standard/plan.md` and assert `new doc draft-plan` fails with no new discussion file.
  - symlink profile template outside `spec-dock` and assert no-write fail-closed.
  - empty-body template and non-file template fail before write.
- Green tests:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`

### M4 Preservation / compatibility

- Change target:
  - `tests/cli_runtime/test_new.py`
  - `create_node.py`
- Plan:
  - Preserve `draft-requirement` source path for all scopes.
  - Preserve Initiative / Epic `draft-design` / `draft-plan` source path.
  - Keep timestamp naming and same-second suffix allocation unchanged.
  - Keep historical discussion docs grandfathered.
- Red tests:
  - Existing `draft-requirement` case continues to assert common requirement template source.
  - Existing Epic `draft-plan` case continues to assert `templates/epic/plan.md`.
  - Add explicit Initiative `draft-design` preservation if current coverage is insufficient.
- Green tests:
  - `uv run pytest tests/cli_runtime/test_new.py`

### M90 Docs / rules impact

- Change target:
  - Provider authority docs under `src/spec_dock/assets/spec_dock/docs/...`, and dogfooding mirror only if this issue execution policy requires parity refresh.
- Plan:
  - Update discussion rules / workflow text only where it still says Issue `draft-design` / `draft-plan` use `templates/issue/{design,plan}.md`.
  - State that Issue design/plan draft source is `issue-profiles/<authorized_profile>` and assurance verification is required.
  - Do not add role skills or shipped specialist assets in this issue.
- Red / alternative evidence:
  - `rg -n "draft-design|draft-plan|templates/issue" src/spec_dock/assets/spec_dock/docs spec-dock/docs` before docs update.
- Green verification:
  - `rg -n "draft-design|draft-plan|templates/issue" src/spec_dock/assets/spec_dock/docs spec-dock/docs` after update, with remaining matches inspected.

### M95 Strict review gate

- Required reviews:
  - per-step code/runtime/tests changes: `code-reviewer`
  - docs/rules changes: `spec-reviewer`
  - issue-wide final: `qa-reviewer`, `code-reviewer`, `spec-reviewer`
- Report destinations:
  - `report.md` Reviewer Gate Status
  - Final QA Gate
  - Final Code Review Gate
  - Final Spec Review Gate
- This draft does not claim any review pass.

### M99 Local handoff gate

- No individual PR for `iss-00253`.
- Required local handoff evidence:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `git status --short`
  - no-write failures prove no new file in target `discussions/` on failure.
  - `report.md` records Red / Green evidence, docs impact, reviewer status, and local closure checkpoint.
- Handoff output:
  - committed local checkpoint suitable as starting HEAD for `iss-00254`.
  - no PR creation until G4 / Epic #224 corrective tranche final gate.

## 4. Dependency-Derived Execution Order

1. M0: Characterize current routing and identify tests that must flip.
2. M1: Add success-path tests first, then implement Issue-only profile-aware routing.
3. M2: Add fail-closed/no-write tests, then move assurance verification before path allocation.
4. M3: Extend or reuse profile template loader, then run compose regression.
5. M4: Lock preservation cases for requirement, Initiative, and Epic.
6. M90: Update docs/rules after runtime behavior is known.
7. M95: Run fresh reviews; fix and re-review until pass.
8. M99: Record report evidence and leave a local checkpoint for G3/G4 without opening a PR.

Dependency rationale:

- G2 depends on G1 and must not implement G3 evidence gates.
- Template guard reuse depends on the existing `assurance compose` template loader.
- Fail-closed behavior must precede write allocation to satisfy AC-003.
- Docs updates should follow runtime test shape to avoid documenting an unimplemented route.

## 5. Issue / Step Slicing

### S01 Profile draft success path

- Behavior goal: classified Issue `draft-design` / `draft-plan` uses profile template source.
- Allowed paths:
  - `create_node.py`
  - `artifact_store.py` only if full-text loader is required
  - `tests/cli_runtime/test_new.py`
- Forbidden changes:
  - canonical active issue docs
  - role skill creation
  - readiness classifier / G3 gates
- Red:
  - profile source assertion fails under current implementation.
- Green:
  - profile template headings appear; placeholder/thin fallback text does not.

### S02 Assurance fail-closed no-write

- Behavior goal: missing / invalid / stale `.assurance.json` blocks before discussion file allocation.
- Allowed paths:
  - `create_node.py`
  - `assurance_store.py` only for narrow reusable error helper
  - `tests/cli_runtime/test_new.py`
- Forbidden changes:
  - automatic Standard fallback
  - silent `.assurance.json` repair
  - canonical artifact mutation
- Red:
  - current `new doc draft-plan` succeeds without assurance.
- Green:
  - command returns non-zero and `discussions` file set is unchanged.

### S03 Template validation reuse

- Behavior goal: `new doc` inherits the same profile template filesystem guard as `assurance compose`.
- Allowed paths:
  - `artifact_store.py`
  - `create_node.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_assurance_compose.py` if regression fixture must be adjusted
- Forbidden changes:
  - parallel ad hoc path validation with different semantics
  - weakening existing compose tests
- Red:
  - missing/symlink/empty/non-file profile template creates or attempts a draft.
- Green:
  - no-write failure with existing guard detail.

### S04 Compatibility preservation

- Behavior goal: non-Issue or non-design/plan draft behavior remains stable.
- Allowed paths:
  - `create_node.py`
  - `tests/cli_runtime/test_new.py`
- Forbidden changes:
  - changing discussion filename grammar
  - changing `draft-requirement`
  - changing Initiative / Epic draft source
- Red:
  - preservation test catches accidental profile routing for non-Issue scope.
- Green:
  - existing source-specific tests pass.

### S90 Docs impact

- Behavior goal: user-facing docs/rules match G2 behavior.
- Allowed paths:
  - provider docs under `src/spec_dock/assets/spec_dock/docs/...`
  - dogfooding mirror docs only when parity update is intentionally required
- Forbidden changes:
  - canonical issue docs
  - role skill shipped asset additions
- Verification:
  - targeted `rg` inspection and final `spec-reviewer`.

### S99 Final local handoff

- Behavior goal: issue-local local closure checkpoint, no individual PR.
- Allowed paths:
  - report evidence only by main orchestrator, not by this delegated draft
- Verification:
  - targeted tests, validate, diff check, clean status expectation after final commit.

## 6. Test Strategy Mapping

| Closure | Test / evidence | File |
|---|---|---|
| AC-001 | `draft-design` for Standard / Strict / Critical uses profile design template headings | `tests/cli_runtime/test_new.py` |
| AC-002 | `draft-plan` for Standard / Strict / Critical uses profile plan template headings | `tests/cli_runtime/test_new.py` |
| AC-003 | missing / invalid / stale assurance and invalid template variants fail without new discussion file | `tests/cli_runtime/test_new.py` |
| AC-004 | `draft-requirement`, Initiative `draft-design`, Epic `draft-plan` keep current source templates | `tests/cli_runtime/test_new.py` |
| AC-005 | profile drafts do not pass through thin fallback body | `tests/cli_runtime/test_new.py` content assertions |
| AC-006 | generated draft contains no self-claiming authority/adoption/reviewer/completion readiness fields | `tests/cli_runtime/test_new.py` content assertions |
| AC-007 | compose guard behavior remains stable | `tests/cli_runtime/test_assurance_compose.py` |

Concrete Red / Green seeds:

- `tc-s01-001` acceptance: strict Issue `draft-plan` includes `仕様固定TDD` profile plan heading, not `実装計画 placeholder`.
- `tc-s01-002` acceptance: standard Issue `draft-design` includes profile design sections, not `設計 placeholder`.
- `tc-s02-001` negative: missing `.assurance.json` fails and no `*-draft-plan-*` file is created.
- `tc-s02-002` negative: stale requirement source binding fails and no `*-draft-design-*` file is created.
- `tc-s03-001` negative: symlinked profile template outside `spec-dock` fails before write.
- `tc-s04-001` regression: Epic `draft-plan` still uses `templates/epic/plan.md`.

## 7. Review Gates

- Step reviewer gate:
  - S01-S04 runtime/tests changes require `code-reviewer`.
  - S90 docs/rules changes require `spec-reviewer`.
- Final gate:
  - `qa-reviewer`: confirms test sufficiency and integration smoke need.
  - `code-reviewer`: reviews integrated runtime / test diff.
  - `spec-reviewer`: checks requirement / design / plan / report / docs consistency.
- Any reviewer `failed`, `unavailable`, `denied`, `waived`, or `provisional` state is not a pass. Required pass evidence belongs in `report.md`, not in this draft.

## 8. Rollback / Compatibility

- Rollback:
  - Revert G2 commit(s) to restore old discussion draft routing.
  - No data migration rollback is expected because successful writes are new discussion drafts only.
- Compatibility:
  - Existing discussion artifacts remain valid and are not renamed.
  - Existing Initiative / Epic draft behavior remains unchanged.
  - Existing Issue `draft-requirement` remains assurance-free.
  - Existing `.assurance.json` schema is not changed.
- Failure safety:
  - Fail-closed paths must not allocate a new discussion filename and must not write partial draft files.
  - Lock acquisition/release behavior remains owned by existing create lock logic.

## 9. Docs Impact

Docs likely requiring update:

- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- dogfooding mirror equivalents only if this tranche expects provider / mirror parity before G4.

Docs not in scope:

- New role skill documentation.
- G3 Evidence Adoption Ledger enforcement.
- G4 end-to-end smoke matrix beyond references to the future smoke owner.

## 10. Final Quality Gate

Before local handoff to G3/G4:

1. Run focused tests:
   - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`
2. Run SpecDock validation:
   - `./spec-dock/scripts/spec-dock validate`
3. Run diff hygiene:
   - `git diff --check`
   - `git status --short`
4. Confirm no-write evidence:
   - failure tests compare discussion file set before/after.
5. Confirm report evidence:
   - Red / Green / Refactor evidence
   - Test Contract Closure
   - Step Contract Closure
   - Reviewer Gate Status
   - M99 local handoff gate
6. Do not create an individual PR for `iss-00253`.

## 11. Plan Blockers

- None that block drafting this implementation plan.
- Implementation must stop and return to design if `create_node.py` cannot verify `.assurance.json` before filename allocation without broad command-layer refactor.
- Implementation must stop and return to design if profile template full-text loading cannot be shared with `assurance compose` without changing compose output semantics.
- Implementation must stop and return to G3 if evidence adoption / phase promotion enforcement becomes necessary to satisfy a test; that is out of scope for G2.

## 12. Integration Notes for Main Orchestrator

- Adopt this draft only through `report.md` Evidence Adoption Ledger and canonical `plan.md` rewrite.
- This draft intentionally uses `disc` rather than `draft-plan` because the issue is about changing `draft-plan` routing itself.
- Diff guard result: passed for this artifact. `git diff --name-status` was empty, and untracked files were limited to active issue `discussions/`; the sibling untracked `20260630t171026z-draft-design-g2-draft-artifact-source-routing-design.md` was not modified by this planner draft.
- Leaf evidence used: active issue docs, Epic #224 requirement/design/plan G2 sections, `create_node.py`, `artifact_store.py`, `assurance_store.py`, profile templates, `test_new.py`, `test_assurance_compose.py`, workflow issue docs, issue-plan authoring docs, discussion rules.
- Forbidden actions avoided: no canonical doc edit, no implementation edit, no tests edit, no package/config edit, no GitHub mutation, no phase promotion, no reviewer-pass claim, no PR creation.
- Unresolved design gaps: none for planning. The implementation should still treat any inability to verify before filename allocation as a design blocker.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
