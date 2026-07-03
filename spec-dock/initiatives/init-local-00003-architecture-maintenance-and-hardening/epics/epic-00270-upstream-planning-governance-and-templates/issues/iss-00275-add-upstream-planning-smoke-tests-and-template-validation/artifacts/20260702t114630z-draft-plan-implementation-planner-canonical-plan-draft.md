---
created_by_role: implementation-planner
scope_id: iss-00275
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081008z-draft-design-upstream-planning-validation-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081009z-draft-plan-upstream-planning-validation-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - tests/unit/infra/test_init_update.py
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_validate.py
  - tests/cli_runtime/test_workflow.py
  - tests/unit/domain/test_workflow_state.py
  - tests/unit/application/test_assurance.py
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
intended_targets:
  - spec-dock/active/issue/plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00275 implementation-planner draft for canonical plan.md

## 1. Plan Summary

この artifact は `iss-00275` の canonical `plan.md` へ統合するための implementation-planner 証跡ドラフトである。canonical docs、code、tests、templates、skills、report は編集していない。

実行方針は、前段 `iss-00271` から `iss-00274` の成果を読み込んだうえで、構造的に検出できる欠落を focused tests / smoke checks に閉じ、自然言語の意味的十分性は reviewer finding として残す。PR 作成はこの Issue では行わず、検証結果と未解決リスクを `report.md` に記録して `iss-00276` へ handoff する。

現状の canonical `design.md` / `plan.md` は profile template 由来の placeholder が多く、pre-start seed artifacts のほうが具体的な計画材料を持つ。main orchestrator が採用する場合は、この artifact の milestone / closure / command mapping を canonical `plan.md` へ移し、fresh `spec-reviewer` gate を通す必要がある。

## 2. Requirement / Design Traceability

| Requirement / design source | Planning consequence |
|---|---|
| `I275-AC-001`, Epic `D-001` | `docs/authoring/scope-layering.md` の存在と inbound thin links を structural smoke として確認する。 |
| `I275-AC-002`, Epic `D-003`, `D-006` | full responsibility table duplication、raw artifact authority language、decision-only ready language は machine-checkable な blocker 候補として検査する。 |
| `I275-AC-003`, Epic `D-002` | DDD / EDA の語彙自体は許容し、mandatory section / required premise 化だけを検査する。 |
| `I275-AC-004`, Epic `D-006`, `D-009` | Epic template / execution guidance が handoff package、Option B、draft artifact boundary、handoff-ready / execution-ready distinction を持つことを確認する。 |
| `I275-AC-005`, Epic `D-008` | templates / docs / skills / artifact guidance の日本語ファースト導線を確認する。識別子、commands、paths、固定語は原文保持を許容する。 |
| `I275-AC-006`, `I275-EC-001..004` | brittle natural-language tests を避け、semantic quality は `spec-reviewer` finding として扱う境界を計画と report に残す。 |
| `I275-AC-007` | focused command、`validate`、manual smoke / skipped checks を `report.md` に記録する。 |
| `I275-AC-008..011`, Epic `D-009` | pre-start canonical draft body absence、draft artifact path index、`new artifact draft-*` non-mutation / fail-closed、Strict / Critical specialist gate を検証対象にする。 |

## 3. Milestones

| Milestone | Outcome | Primary checks | Report evidence |
|---|---|---|---|
| M0 Baseline characterization | 既存 coverage と前段差分を分類する。既に covered なら no-op evidence、gap があれば Red candidate を固定する。 | `rg` inventory、既存 focused tests の単体実行 | `report.md#仕様解釈・判断台帳`, `report.md#検証` |
| M1 Structural smoke matrix | scope-layering、authority、architecture-neutral、日本語ファースト、handoff package の structural tests を足すか強化する。 | `tests/unit/infra/test_init_update.py` focused node | `report.md#実装記録`, `report.md#Step Evidence` |
| M2 Draft artifact command / readiness gates | `new artifact draft-design` / `draft-plan`、canonical non-mutation、fail-closed、Strict / Critical readiness を characterization または追加 tests で固定する。 | `tests/cli_runtime/test_new.py`, `tests/unit/domain/test_workflow_state.py`, `tests/cli_runtime/test_workflow.py` | `report.md#検証` |
| M3 Minimal gate repair | M1 / M2 で in-scope gaps が出た場合だけ provider docs / templates / skills / runtime を最小修正する。 | 変更面に応じた focused suite | `report.md#仕様解釈・判断台帳` |
| M90 Docs and smoke validation | machine checks の限界、manual dogfooding read-through、false-positive policy を report に残す。 | `./spec-dock/scripts/spec-dock validate`, optional `sync --no-github` | `report.md#検証` |
| M99 Finish handoff | PR なしで `issue finish` し、`iss-00276` へ command list / risks / evidence を渡す。 | final focused commands, dirty-file inspection | `report.md#完了 / PR` |

## 4. Dependency-Derived Execution Order

1. 前提確認: `iss-00271..iss-00274` の report / changed files / reviewer results を読む。`iss-00274` の Option B / readiness guidance が未完了なら、この Issue の Red ではなく upstream blocker として止める。
2. Baseline characterization: 既存 tests を inventory し、次の分類に分ける: `covered-existing`, `characterization-first`, `red-required`, `inspect-only`, `manual-required`。
3. Focused Red: structural gap が未検査なら、最小の failing assertion を追加する。自然言語の質を丸ごと文字列一致にしない。
4. Minimal Green: Red が出た surface だけを修正する。template wording / docs links / skill wording / runtime fail-closed のいずれかに閉じる。
5. Regression ladder: focused tests、関連 lane、`validate`、必要に応じた dogfooding read-through の順に広げる。
6. Reviewer gate: smoke coverage relevance、false-positive risk、日本語ファーストの検査粒度を `spec-reviewer` へ出す。
7. Finish handoff: PR は作らず、`iss-00276` が再実行すべき commands と未解決リスクを report に残す。

## 5. Issue / Step Slicing

| Step | Type | Allowed targets if implementation is needed | Done when |
|---|---|---|---|
| S00 Readiness intake | inspect-only | canonical docs / artifacts / reports only | 前段成果、active issue docs、existing coverage が report に要約できる。 |
| S01 Characterize existing template/doc coverage | characterization-first | `tests/unit/infra/test_init_update.py` | 既存 assertions が `I275-AC-001..005` のどれを閉じるか説明できる。 |
| S02 Add missing structural smoke tests | red-required if gap exists | `tests/unit/infra/test_init_update.py` または small dedicated test file | scope-layering / authority / architecture-neutral / Japanese-first / handoff gaps を検出できる。 |
| S03 Characterize draft artifact command behavior | characterization-first | `tests/cli_runtime/test_new.py` | profile template source、canonical non-mutation、missing / invalid / stale assurance fail-closed の coverage が明確になる。 |
| S04 Add readiness gate coverage only if missing | red-required if gap exists | `tests/unit/domain/test_workflow_state.py`, `tests/cli_runtime/test_workflow.py` | Strict / Critical が artifact existence だけで ready にならないことを確認できる。 |
| S05 Minimal repair | minimal green | `src/spec_dock/assets/spec_dock/docs/`, `src/spec_dock/assets/spec_dock/templates/`, `src/spec_dock/assets/install_root/.agents/skills/`, runtime only if tests prove behavior gap | Red を最小修正で Green にし、unrelated wording cleanup をしない。 |
| S90 Integrated validation | validation | no new production edits | focused commands と `validate` の結果を report に記録する。 |
| S99 Finish handoff | lifecycle | report / SpecDock lifecycle only by orchestrator | PR なしで `iss-00276` に evidence を渡せる。 |

Conditional branch:

- If runtime behavior is already covered: add no runtime code; run the focused tests as characterization evidence and record no-op rationale in `report.md`.
- If runtime behavior gaps are found: add the smallest failing CLI/domain test first, then repair only the relevant runtime target, likely `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`, `application/create_artifact_doc.py`, or `domain/workflow_state.py`.
- If only docs/templates/skills wording is missing: keep the change in provider assets and cover it with scaffold / text-structure tests, not runtime behavior tests.

## 6. Test Strategy Mapping

Suggested focused commands:

```sh
uv run pytest tests/unit/infra/test_init_update.py -k 'template or scope or japanese or draft or readiness'
uv run pytest tests/cli_runtime/test_new.py -k 'draft_requirement or profile_drafts or artifact_stdout'
uv run pytest tests/cli_runtime/test_validate.py -k delegated_draft
uv run pytest tests/unit/domain/test_workflow_state.py -k 'specialist or delegated_draft or strict or critical'
uv run pytest tests/cli_runtime/test_workflow.py -k 'grade_evidence or assurance or workflow_status'
./spec-dock/scripts/spec-dock validate
```

Concrete existing coverage to reuse:

- `tests/unit/infra/test_init_update.py` already checks `authoring/scope-layering.md`, Japanese-first labels, Initiative / Epic template fragments, DDD / EDA non-mandatory wording, Issue placeholder state, and Epic handoff draft path fragments.
- `tests/cli_runtime/test_new.py::test_new_artifact_issue_design_and_plan_use_authorized_profile_templates` covers profile-based `draft-design` / `draft-plan` creation and absence of `artifact_state: awaiting-assurance-compose` in generated drafts.
- `tests/cli_runtime/test_new.py::test_new_artifact_issue_profile_drafts_fail_closed_without_valid_assurance_contract` covers missing / invalid / stale `.assurance.json` fail-closed behavior.
- `tests/unit/domain/test_workflow_state.py` covers delegated draft evidence, specialist / fallback evidence, and Strict / Critical readiness gate semantics.
- `tests/cli_runtime/test_workflow.py::test_guidance_blocks_strict_legacy_execution_when_grade_evidence_is_missing` covers guidance-level blocking when grade evidence is absent.
- `tests/cli_runtime/test_validate.py::test_validate_blocks_proposed_or_missing_metadata_delegated_draft_artifacts` covers validation failure for invalid delegated draft authority metadata.

Avoid brittle natural-language tests:

- Assert structural anchors, headings, required field names, link targets, and forbidden authority phrases.
- Prefer section-scoped assertions over whole-document snapshots.
- For Japanese-first, test guidance presence and allowed-English boundary, not every token in prose.
- For DDD / EDA, assert absence of mandatory wording patterns, not absence of the terms.
- For Option B, assert that structural blocker and reviewer finding categories both exist and are not collapsed.
- Leave semantic sufficiency, wording quality, and reviewer persuasion to fresh `spec-reviewer` findings.

## 7. Review Gates

| Gate | Reviewer focus | Blocks execution if missing |
|---|---|---|
| Plan adoption gate | This artifact is adopted / partially adopted / rejected in `report.md` EAL before canonical `plan.md` integration. | yes |
| Fresh spec-reviewer gate | `plan.md` has executable steps, closure mapping, required verification, false-positive boundary, and no raw artifact authority leak. | yes |
| Focused test gate | New/updated tests fail for the intended gap and pass after minimal repair, or existing coverage is recorded as no-op evidence. | yes for changed behavior |
| Semantic quality gate | Reviewer evaluates coverage relevance and Japanese-first adequacy; machine tests do not replace this judgment. | reviewer finding unless structural requirement missing |
| Finish handoff gate | `report.md` includes commands, outcomes, skipped checks, issue finish rationale, and `iss-00276` handoff. | yes |

## 8. Rollback / Compatibility

- Rollback is file-level revert of tests and provider asset repairs made in this Issue. No data migration or destructive workspace change is planned.
- Existing managed repos should continue to receive architecture-neutral templates; this Issue must not introduce DDD / EDA as a default requirement.
- `draft-design` / `draft-plan` remain Issue-local evidence. They do not become canonical `design.md` / `plan.md` without main orchestrator adoption, `assurance compose`, and fresh review.
- Manual smoke workspaces, raw logs, captures, and temporary artifacts must remain untracked.
- If `sync` or dogfooding refresh would rewrite broad generated workspace files, record the need and defer to `iss-00276` unless it is required to close an explicit AC.

## 9. Docs Impact

Expected docs impact is conditional:

- No docs edit is required if existing guidance already satisfies the structural checks.
- If gaps are found, likely targets are `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, `phase_plan_epic.md`, `phase_plan_issue.md`, or `docs/rules/issue/artifacts.md`.
- Skill wording repairs should stay in `src/spec_dock/assets/install_root/.agents/skills/` and remain thin links to docs, not duplicate full responsibility tables.
- Template repairs should stay in `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/` and avoid product-specific issue IDs or this Epic's historical artifact names.

## 10. Final Quality Gate

Minimum final gate for `iss-00275`:

```sh
uv run pytest tests/unit/infra/test_init_update.py -k 'template or scope or japanese or draft or readiness'
uv run pytest tests/cli_runtime/test_new.py -k 'draft_requirement or profile_drafts or artifact_stdout'
uv run pytest tests/cli_runtime/test_validate.py -k delegated_draft
uv run pytest tests/unit/domain/test_workflow_state.py -k 'specialist or delegated_draft or strict or critical'
uv run pytest tests/cli_runtime/test_workflow.py -k 'grade_evidence or assurance or workflow_status'
./spec-dock/scripts/spec-dock validate
```

Escalate to broader lanes if production runtime or scaffold behavior changes:

```sh
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_new.py
uv run pytest tests/cli_runtime/test_workflow.py
uv run pytest tests/unit/domain/test_workflow_state.py
uv run pytest tests/cli_runtime
uv run pytest tests/unit
```

`report.md` must record command, result, failure cause if any, and next action. This Issue should not create a PR; `iss-00276` owns final quality / PR delivery.

## 11. Plan Blockers

- Current canonical `design.md` and `plan.md` still contain generic template placeholders. Before implementation, main orchestrator should compose or author canonical docs from reviewed evidence.
- Dirty pre-existing changes exist in canonical issue docs and `.assurance.json`; this planner artifact does not classify or own those changes.
- If `iss-00271..iss-00274` are not actually complete or their reports lack reviewer evidence, implementation should stop and treat this as upstream blocker.
- If tests reveal a contradiction in Epic design decisions, do not patch around it in tests; return to Epic design / plan and fresh review.

## 12. Integration Notes for Main Orchestrator

Closure mapping:

| Closure | Requirement | Planned evidence |
|---|---|---|
| CLOS-275-001 | `I275-AC-001` | scope-layering file existence plus inbound links from docs / templates / skills. |
| CLOS-275-002 | `I275-AC-002` | tests or inspections for duplicate full responsibility table, raw artifact authority language, decision-only execution-ready language. |
| CLOS-275-003 | `I275-AC-003` | template checks that DDD / EDA are optional / needed-only, not mandatory. |
| CLOS-275-004 | `I275-AC-004` | Epic template / execution guidance checks for handoff package and Option B split. |
| CLOS-275-005 | `I275-AC-005` | Japanese-first guidance checks across templates / docs / skills / artifact guidance with identifier exceptions. |
| CLOS-275-006 | `I275-AC-006` | plan/report statement and reviewer gate proving semantic quality is not machine-only. |
| CLOS-275-007 | `I275-AC-007` | `report.md` command result ledger for focused tests and `validate`. |
| CLOS-275-008 | `I275-AC-008` | `rg` / test evidence that pre-start canonical `design.md` / `plan.md` do not contain `artifact_state: "draft-before-issue-start"`. |
| CLOS-275-009 | `I275-AC-009` | report / handoff package includes Issue-local `draft-design` / `draft-plan` path index. |
| CLOS-275-010 | `I275-AC-010` | `test_new.py` coverage for non-mutation and missing / invalid / stale assurance fail-closed. |
| CLOS-275-011 | `I275-AC-011` | workflow_state / workflow guidance tests that Strict / Critical require specialist or manual fallback evidence and fresh review. |
| CLOS-275-EC-001 | `I275-EC-001` | tests avoid whole-prose quality scoring; semantic quality remains reviewer-owned. |
| CLOS-275-EC-002 | `I275-EC-002` | tests reject mandatory DDD / EDA wording only, not the vocabulary. |
| CLOS-275-EC-003 | `I275-EC-003` | Japanese-first tests allow paths, commands, IDs, fixed terms, and external names. |
| CLOS-275-EC-004 | `I275-EC-004` | report / final status confirms raw manual smoke artifacts are untracked. |

Suggested canonical `plan.md` integration:

- Adopt sections 3 through 10 as the canonical milestone / validation ladder.
- Keep section 11 blockers as Plan Readiness or Stop Conditions.
- Convert section 12 closure mapping into the plan closure index.
- Add an explicit "No PR in this issue; handoff to `iss-00276`" final step.
- Record this artifact in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger before reflecting it to canonical `plan.md`.

Source revisions / status observed:

- `spec-dock/active/issue/requirement.md`: concrete requirement, status `draft`, includes `I275-AC-001..011` and `I275-EC-001..004`.
- `spec-dock/active/issue/design.md`: status `approved`, but body remains mostly Standard template placeholders.
- `spec-dock/active/issue/plan.md`: status `approved`, but body remains mostly Standard template placeholders.
- `spec-dock/active/epic/{requirement,design,plan}.md`: planning source for `iss-00275`, especially Slice 05 and `D-001..D-009`.

Leaf evidence used: none. This draft used direct local source inspection only.

Forbidden actions avoided: no canonical edit, no code edit, no test edit, no template edit, no skill edit, no report edit, no PR, no issue finish, no reviewer-pass claim.

Unresolved design gaps: canonical issue `design.md` / `plan.md` placeholder content should be resolved by main orchestrator before implementation.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
