---
created_by_role: system-architect
scope_id: iss-00253
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - spec-dock/active/issue/discussions/rules.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py
  - src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/design.md
  - src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/plan.md
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_assurance_compose.py
  - tests/cli_runtime/test_runtime_new_doc_s09.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00253 G2 draft-design - draft artifact source routing

この文書は `system-architect` による delegated design evidence であり、canonical `design.md` / `plan.md` / `report.md` の直接更新、reviewer pass、phase completion、implementation readiness を主張しない。採用可否は main orchestrator が判断し、必要な内容だけを canonical artifact と `report.md` Evidence Adoption Ledger へ再記述する。

Source requirement revision:

- repo HEAD: `9d172bff`
- `spec-dock/active/issue/requirement.md` sha256: `3c7ff05a6765b27c5250869bb781bf93ecebfc75f1011222d1e069449c515d76`
- active scope: `iss-00253`

## 1. Requirement Coverage

| Requirement | Coverage in this draft |
|---|---|
| AC-001 | Issue `draft-design` は `.assurance.json` の verified `classification.authorized_profile` から `templates/issue-profiles/<profile>/design.md` を読む。 |
| AC-002 | Issue `draft-plan` は同じ profile source から `templates/issue-profiles/<profile>/plan.md` を読む。 |
| AC-003 | contract missing / invalid / stale、unsupported profile、template missing / invalid / empty は discussion filename allocation 前に no-write fail-closed とする。 |
| AC-004 | `draft-requirement` と Initiative / Epic `draft-design` / `draft-plan` は既存の scope canonical template 経路を維持する。 |
| AC-005 | Issue profile-sourced design / plan では `_normalize_draft_discussion_text` の thin draft normalization を適用しない。 |
| AC-006 | generated draft は evidence であり、authority accepted、adopted、reviewer pass、phase completion、implementation readiness を自己主張しない。 |
| AC-007 | `assurance compose` で使う profile template validation guard を分岐させず、既存 regression を維持する。 |

要件上の未解決 gap はない。active issue 自体には現時点で `.assurance.json` が存在しないが、これは G2 実装対象の no-write fail-closed 条件であり、この delegated draft 作成の blocking gap ではない。

## 2. Existing Context Findings

- Epic design は Issue `draft-design` / `draft-plan` の source authority を `.assurance.json` の `classification.authorized_profile` と定義し、`lite_candidate`、frontmatter、command title、implicit default を template selection authority にしないと明記している。
- Epic plan G2 は `new doc draft-design` / `draft-plan` routing、missing / invalid / stale `.assurance.json` no-write fail-closed、`draft-requirement` と Initiative / Epic draft preservation、delegated draft provenance / self-claim 禁止を成果物にしている。
- 現行 `application/create_node.py` は `_draft_canonical_template_path()` で `templates/<scope_kind>/{requirement,design,plan}.md` を選び、Issue `draft-design` / `draft-plan` でも `templates/issue/design.md` / `plan.md` を使う。
- 現行 `_normalize_draft_discussion_text()` は `artifact_state: awaiting-assurance-compose` を含む Issue design / plan scaffold を薄い draft body へ正規化する。profile full template を使う G2 ではこの正規化は誤動作になる。
- 現行 `plan_discussion_doc()` は template path を決めた後に discussion filename を allocate する。G2 の fail-closed 要件では、Issue design / plan の contract verify と profile template validation を allocation 前に完了させる必要がある。
- `infra/assurance_store.py` は `verify_contract()` で `.assurance.json` の read / schema / source binding stale 判定を提供済みである。
- `infra/artifact_store.py` は `load_profile_artifact_template(artifact, profile)` で profile whitelist、workspace escape、non-file、missing、empty body を guard している。
- `tests/cli_runtime/test_new.py` は現在、Issue `draft-design` が `templates/issue/design.md` を使うことを期待している。この期待値は G2 で Red にする。
- `tests/cli_runtime/test_assurance_compose.py` は profile template validation failure の no-write を既に固定している。G2 はこの guard の意味論を `new doc` 側へ接続する。

## 3. Design Decisions

| ID | Decision | Status |
|---|---|---|
| DES-001 | Issue `draft-design` / `draft-plan` にだけ profile-aware branch を追加する。 | proposed |
| DES-002 | `AssuranceStore.verify_contract()` を filename allocation 前に呼び、valid contract 以外は no-write fail-closed にする。 | proposed |
| DES-003 | profile template read / validation は `ArtifactStore.load_profile_artifact_template()` を再利用する。 | proposed |
| DES-004 | loaded profile template body を `TemplateScaffolder.render_text()` に渡し、既存 replacement token を使って materialize する。 | proposed |
| DES-005 | profile-sourced draft には `_normalize_draft_discussion_text()` を適用しない。scope canonical template 経路だけ legacy normalization を維持する。 | proposed |
| DES-006 | `create_discussion_doc` は bootstrap から `AssuranceStore` と `ArtifactStore` を注入できるようにし、unit test 互換のため既存 call shape は最小変更にする。 | proposed |
| DES-007 | CLI error は non-zero とし、stderr に reason / details を含める。discussion file は生成しない。JSON output は `new doc` にないため追加しない。 | proposed |

最小実装の形は、`plan_discussion_doc()` から profile resolution を分離し、`create_discussion_doc()` 内の lock acquisition 後、`_allocate_discussion_doc_filename()` より前に profile contract を確認する設計である。現在の create lock は concurrent filename allocation protection のために維持するが、contract / template validation failure では write も filename allocation も行わない。

## 4. Alternatives Considered

| Alternative | Rejected / deferred reason |
|---|---|
| `templates/issue/design.md` / `plan.md` を profile template へ include させる | `new doc` の source authority が common placeholder に残り、AC-001 / AC-002 の直接性が弱くなる。 |
| Missing assurance contract では Standard profile を fallback する | AC-003 と Epic design の fail-closed / no Standard fallback に反する。 |
| `assurance compose --dry-run` を内部実行して draft source を得る | canonical compose use case と discussion draft generation の責務が混ざり、no-write保証とエラー理由が複雑になる。 |
| `ArtifactStore.load_profile_artifact_template()` を複製する | compose と new doc の filesystem guard が drift し、AC-007 の regression risk が上がる。 |
| `new doc` に JSON error contract を追加する | G2 の範囲外。既存 command surface を広げるより CLI runtime tests で stderr / no-write を固定する方が小さい。 |

## 5. Boundary / Contract Model

### Runtime boundary

- Command layer:
  - `commands/new.py` は既存の `new doc` args contract を維持する。
  - 新しい flag は追加しない。
- Application layer:
  - `application/create_node.py` が Issue draft routing を orchestrate する。
  - scope / doc type を見て、Issue design / plan だけ profile-aware route に入れる。
- Infra layer:
  - `AssuranceStore` が `.assurance.json` の valid / stale 判定を担う。
  - `ArtifactStore` が profile template path validation と full text read を担う。
  - `TemplateScaffolder` は token replacement と final discussion write を担う。

### Public behavior contract

| Input | Expected result |
|---|---|
| Issue `new doc draft-design` with valid strict contract | one issue discussion file whose structure comes from `templates/issue-profiles/strict/design.md` |
| Issue `new doc draft-plan` with valid critical contract | one issue discussion file whose structure comes from `templates/issue-profiles/critical/plan.md` |
| Issue `new doc draft-design` without `.assurance.json` | non-zero, no new discussion file |
| Issue `new doc draft-plan` with stale source binding | non-zero, no new discussion file |
| Initiative / Epic `draft-design` / `draft-plan` | current scope canonical template behavior preserved |
| Issue `draft-requirement` | current `templates/issue/requirement.md` behavior preserved |

### No self-authority contract

Generated draft body must not introduce:

- accepted-authority frontmatter
- adopted-status frontmatter
- non-empty `reflected_to`
- reviewer pass claim
- phase completion claim
- implementation readiness claim

If current profile templates contain such claims, G2 should fail tests and repair templates in the same issue only if the claims are generated by the shipped templates. It should not add a new post-render sanitizer that hides template defects silently.

## 6. Dependency Analysis

`iss-00253` depends on `iss-00252` because G1 defines the grade-aware authoring vocabulary and separates `authorized_profile` from manual escalation. G2 must not re-open that policy decision.

Implementation dependencies:

- `create_node.py` can import `AssuranceStore` / `ArtifactStore` protocols or accept store-like parameters from bootstrap.
- `artifact_store.py` already depends on domain artifact composer types and can remain infra-only.
- `assurance_store.py` already owns target resolution by issue id / active issue / path. G2 should call `resolve_issue_target(scope.id)` or use the resolved `scope.path` consistently.

Risky dependency direction to avoid:

- Domain code must not import filesystem stores.
- `ArtifactStore` must not call `AssuranceStore`.
- `commands/new.py` must not inspect `.assurance.json` directly.
- Tests should not rely on live GitHub.

## 7. Source of Record

Normative sources for G2:

| Source | Meaning |
|---|---|
| `spec-dock/active/issue/requirement.md` | AC-001 through AC-007, constraints, scope / non-scope |
| `spec-dock/active/epic/design.md` | authority split, Issue discussion draft routing, implementation placement |
| `spec-dock/active/epic/plan.md` | G2 tranche scope, integration checks, regression expectations |
| `.assurance.json` | runtime template source authority for implementation behavior |
| `templates/issue-profiles/<profile>/{design,plan}.md` | body source for Issue design / plan draft generation |
| `workflow_spec_authoring.md` and `phase_design.md` | delegated draft evidence and no-authority rules |

Non-authoritative signals:

- Issue frontmatter `Issue Grade`
- command title / slug
- `lite_candidate`
- missing contract default
- current active context synthetic approval

## 8. Data Flow / Domain Model / Interface Contract

### Data flow

```text
new doc draft-design --issue iss-xxxxx
  -> resolve scope node from graph
  -> if scope.kind == issue and doc_type in {draft-design,draft-plan}
       -> AssuranceStore.resolve_issue_target(scope.id)
       -> AssuranceStore.verify_contract(target)
       -> fail if status != valid
       -> profile = contract.classification.authorized_profile.value
       -> artifact = design | plan
       -> ArtifactStore.load_profile_artifact_template(artifact, profile)
       -> use template.body as render source
     else
       -> use existing scope canonical template path
  -> allocate discussion filename
  -> render replacements
  -> skip legacy thin normalization for profile-sourced drafts
  -> write one Markdown file under target discussions/
```

### Proposed internal contract

Introduce a small internal value in `create_node.py`:

```python
@dataclass(frozen=True)
class DiscussionTemplateSelection:
    template_text: str | None
    template_path: Path | None
    profile_sourced: bool
```

The existing path-based template loading can remain for normal discussion docs and legacy draft docs. For profile-sourced issue design / plan, `template_text` can carry the validated body from `ArtifactStore`, while `template_path` remains only for diagnostics. A simpler equivalent is also acceptable: return `(template_path, template_text_override, profile_sourced)`.

### Error model

Use typed helper messages rather than silent fallback:

- `missing_assurance_contract`
- `invalid_schema`
- `stale_source_binding`
- `Profile template not found`
- `Profile template is outside spec-dock workspace`
- `Profile template is not a file`
- `Profile template body is empty`

The exact CLI wording can follow existing `AssuranceStoreResult.reason` and `ArtifactStore` exception text. The key contract is non-zero exit and no discussion file allocation / write.

## 9. File / Module Change Plan

Implementation files:

| Path | Change |
|---|---|
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` | Add profile-aware Issue draft selection and no-write preflight before filename allocation. |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | Inject `AssuranceStore` and `ArtifactStore` into `create_discussion_doc` or the relevant helper. |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py` | Prefer no change. Add helper only if `load_profile_artifact_template()` cannot serve discussion draft rendering cleanly. |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py` | Prefer no change. Use existing `verify_contract()` and target resolution. |
| `tests/cli_runtime/test_new.py` | Replace old Issue draft expectation with profile template success cases and no-write fail-closed cases. Preserve Initiative / Epic / `draft-requirement` cases. |
| `tests/cli_runtime/test_assurance_compose.py` | Keep existing template validation regression. Add no test unless shared helper behavior changes. |
| `tests/cli_runtime/test_runtime_new_doc_s09.py` | Update unit-level expectation for profile-sourced Issue design / plan only, while keeping suffix allocation behavior. |

Docs / rules changes are only needed if generated guidance or shipped discussion rules still say Issue `draft-design` / `draft-plan` use `templates/issue/design.md` / `plan.md`. Canonical active docs are not changed by this delegated draft.

## 10. Migration / Compatibility / Rollback

Migration:

- No repository data migration is required.
- Existing discussion drafts remain grandfathered evidence and are not renamed or rewritten.
- Existing canonical issue `design.md` / `plan.md` are unaffected by `new doc`.

Compatibility:

- Existing users can still create Initiative / Epic draft docs as before.
- Issue `draft-requirement` remains available before classification.
- Issue design / plan draft creation now requires a valid, non-stale `.assurance.json`; this is an intentional stricter contract, not a regression.

Rollback:

- Revert `create_node.py` routing and test updates to restore old common-template behavior.
- No data rollback is needed because successful G2 writes only new discussion Markdown files.
- If a failure occurs during preflight, no filename allocation or discussion write should have occurred.

## 11. Observability

Minimum observability is CLI-visible:

- success output keeps `spec-dock: ok (new doc) type=<doc_type> ... path=...`
- failure output includes contract reason or template validation detail on stderr
- tests assert created file count before / after for no-write cases

Optional future observability, out of G2 scope:

- machine-readable `new doc --format json`
- workflow event recording for failed delegated draft preflight
- report evidence gate automation in G3

## 12. Test Strategy

Focused tests:

1. `test_new_doc_issue_draft_design_uses_authorized_profile_template`
   - create classified issue fixture
   - force or assert `authorized_profile=standard` or `strict`
   - run `new doc draft-design --issue <id>`
   - assert created body includes profile template heading and not common placeholder / thin normalized body

2. `test_new_doc_issue_draft_plan_uses_authorized_profile_template`
   - same as above for `draft-plan`
   - assert profile plan sections are present

3. `test_new_doc_issue_draft_design_missing_assurance_fails_before_write`
   - create issue fixture without `.assurance.json`
   - snapshot discussions directory
   - run command
   - assert return code non-zero and no new file

4. `test_new_doc_issue_draft_plan_invalid_or_stale_assurance_fails_before_write`
   - corrupt JSON or change source artifact after classification
   - assert no new file

5. `test_new_doc_issue_draft_profile_template_validation_reuses_guard`
   - remove / symlink escape / directory / empty body template
   - assert no new file and expected detail

6. `test_new_doc_preserves_non_profile_draft_routes`
   - `draft-requirement` for Issue uses `templates/issue/requirement.md`
   - Initiative / Epic `draft-design` / `draft-plan` still use scope canonical templates

Regression lanes:

- `uv run pytest tests/cli_runtime/test_new.py`
- `uv run pytest tests/cli_runtime/test_assurance_compose.py`
- `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py`
- If bootstrap or installer assets are touched: `uv run pytest tests/unit/infra/test_init_update.py -k issue_profiles` or the narrow matching tests.

## 13. ADR Candidates

No new ADR is required for the core G2 design. The durable decision already exists at Epic level: `authorized_profile` is runtime template / guidance / obligation authority, while manual escalation is separate.

Potential ADR only if implementation discovers one of these cross-cutting changes:

- `new doc` needs a machine-readable JSON error contract across all doc types.
- delegated draft generation needs a general template source resolver shared by more than Issue design / plan.
- profile template source authority must extend to non-Issue scopes.

## 14. Risks

| Risk | Mitigation |
|---|---|
| Discussion filename is allocated before preflight failure | Move Issue profile preflight before `_allocate_discussion_doc_filename()` and assert no new file in tests. |
| New route silently falls back to Standard | Never synthesize a fallback profile; use only `contract.classification.authorized_profile.value`. |
| Compose and new doc template guards drift | Reuse `ArtifactStore.load_profile_artifact_template()` instead of duplicating path checks. |
| Legacy thin normalization strips profile template sections | Track `profile_sourced` and skip `_normalize_draft_discussion_text()` for that path. |
| Current unit tests use direct `create_discussion_doc(req, ports)` without stores | Provide default-compatible injection or focused stubs so non-profile paths remain testable. |
| Active issue has no `.assurance.json` during development | Treat as failure fixture for G2. Success tests should create classified fixture through existing assurance command. |
| Profile templates contain self-authority wording | Tests should catch forbidden claims in generated draft body; repair template wording if necessary. |

## 15. Requirement Clarification Requests

None. The active requirement, Epic design, Epic plan, and workflow docs are sufficient for G2 design.

Non-blocking implementation question for main orchestrator:

- Should the CLI stderr for fail-closed `new doc` use raw `AssuranceStoreResult.reason`, or should it map to a user-facing sentence like `Issue draft-design requires a valid .assurance.json before writing discussion drafts`? Either is compatible with the design if tests assert stable behavior.

## 16. Integration Notes for Main Orchestrator

- Adopt DES-001 through DES-005 into canonical `design.md` if they match the intended implementation boundary.
- Keep `plan.md` focused on Red tests for `test_new.py`, then the minimal routing implementation, then preservation / no-write regression.
- Record this delegated draft path in `report.md` Evidence Adoption Ledger if any content is adopted.
- Do not treat this draft as reviewer pass. Fresh `spec-reviewer` remains required after canonical integration.
- Note that a concurrent untracked `disc` artifact was observed in the same discussions directory and was not edited by this draft run.
- The main orchestrator should run the formal post-run diff guard before adopting this evidence; this draft leaves `diff_guard_result: pending`.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
