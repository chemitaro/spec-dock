---
created_by_role: system-architect
scope_id: iss-00275
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/.agent/active.json
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081008z-draft-design-upstream-planning-validation-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081009z-draft-plan-upstream-planning-validation-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
  - src/spec_dock/assets/spec_dock/templates/initiative/
  - src/spec_dock/assets/spec_dock/templates/epic/
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - tests/cli_runtime/test_new.py
  - tests/unit/infra/test_init_update.py
  - tests/unit/domain/test_workflow_state.py
  - tests/unit/domain/test_delegated_authoring.py
  - tests/cli_runtime/test_delegated_authoring.py
  - tests/unit/application/test_assurance.py
intended_targets:
  - spec-dock/active/issue/design.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# iss-00275 system-architect draft design

この artifact は canonical `design.md` のための system-architect 設計証跡である。正本編集、採用判断、phase promotion、reviewer pass、implementation readiness は主張しない。

## 1. Requirement Coverage

### AC / EC と設計 ID の対応

| 要件 | 設計 ID | 設計上の扱い | 検証レベル |
|---|---|---|---|
| `I275-AC-001` | `DES-001 scope-layering reachability` | `docs/authoring/scope-layering.md` の存在と、workflow docs / phase docs / templates / skills からの薄い到達性を検査する。全文表の複製ではなく thin link を期待する。 | machine test + smoke read-through |
| `I275-AC-002` | `DES-002 authority and duplication guard` | full responsibility table の過剰重複、raw artifact authority leak、decision-only Issue ready language を構造的に検出する。 | machine test |
| `I275-AC-003` | `DES-003 architecture-neutral wording guard` | Initiative / Epic templates で DDD / EDA を補助語彙として許容し、mandatory section / mandatory process として要求しない。 | machine test + reviewer-only semantic check |
| `I275-AC-004` | `DES-004 handoff readiness contract` | Epic template / execution guidance が Issue handoff package、Option B structural blocker / reviewer finding split、handoff-ready / execution-ready の分離を含むことを検査する。 | machine test + smoke read-through |
| `I275-AC-005` | `DES-005 Japanese-first guidance coverage` | templates / skills / workflow docs / artifact guidance に、日本語本文優先と識別子原文保持の境界があることを検査する。 | machine test + reviewer-only quality check |
| `I275-AC-006` | `DES-006 false-positive boundary` | machine check が自然言語品質を裁きすぎない境界を design / plan / report evidence に明示し、意味品質は reviewer に残す。 | reviewer-only + smoke read-through |
| `I275-AC-007` | `DES-007 evidence reporting` | `validate` と対象 test command の結果は `report.md` に記録し、未実施 / 失敗は理由と次アクションを持つ。 | smoke/read-through; final execution evidence |
| `I275-AC-008` | `DES-008 canonical pre-start draft absence` | 未開始 Issue canonical `design.md` / `plan.md` に `artifact_state: "draft-before-issue-start"` や本文入り pre-start draft body が残らないことを検査する。 | machine test |
| `I275-AC-009` | `DES-009 issue-local draft path index` | Issue-local `draft-design` / `draft-plan` artifact path index が report / handoff package に残ることを検査する。 | machine test + smoke read-through |
| `I275-AC-010` | `DES-010 draft artifact command boundary` | `new artifact draft-design` / `draft-plan` は Issue-local artifact のみを作り、canonical docs を変更しない。missing / invalid / stale `.assurance.json` は no-write fail-closed にする。 | machine test |
| `I275-AC-011` | `DES-011 strict-critical readiness gate` | Strict / Critical は draft artifact の存在だけでは ready にならず、specialist / fallback evidence と fresh reviewer gate が必要である。 | machine test + smoke read-through |
| `I275-EC-001` | `DES-006` | brittle な文字列一致だけで自然言語品質を合否判定しない。 | reviewer-only boundary |
| `I275-EC-002` | `DES-003` | DDD / EDA 語彙そのものは禁止せず、必須化だけを問題にする。 | machine negative assertion + reviewer-only |
| `I275-EC-003` | `DES-005` | path、command、identifier、固定語、外部固有名詞の英語を日本語ファースト違反にしない。 | machine allow-list + reviewer-only |
| `I275-EC-004` | `DES-012 manual artifact hygiene` | raw manual smoke workspace、logs、captures を commit しない。証跡は `report.md` か scope-local artifact へ要約する。 | smoke/read-through + `git status` inspection |

### Machine / Smoke / Reviewer の分担

Machine tested に寄せるもの:
- ファイル存在、リンク文字列、path index、template source、profile template selection、canonical non-mutation、no-write fail-closed、readiness gate の構造条件。
- 禁止語の完全禁止ではなく、明確な authority leak や mandatory wording の限定 pattern。

Smoke / read-through に残すもの:
- workflow docs、skills、templates を人間が導線として読めるか。
- `report.md` に test / validate / manual evidence が十分に要約されているか。
- raw manual files が staged / tracked されていないことの確認。

Reviewer-only に残すもの:
- 受け入れ条件の意味的十分性。
- 日本語本文の読みやすさ、説明責任、文脈に対する過不足。
- DDD / EDA の語彙が対象 repo の実態に照らして適切か。

## 2. Existing Context Findings

- `epic-00270` は D-001 / D-002 / D-006 / D-008 / D-009 により、scope-layering reference、architecture-neutral template policy、Option B structural blocker split、日本語ファースト、unified draft artifact command を固定している。
- `iss-00275` の requirement は `strict` と明記しているが、現在の generated artifact body は profile template 由来で Standard と表示されうる。canonical compose 時は `.assurance.json` の authorized profile と requirement の grade を照合し、Strict 相当に揃える必要がある。
- `tests/cli_runtime/test_new.py` には `draft-design` / `draft-plan` が authorized profile template を使うこと、`artifact_state: awaiting-assurance-compose` を artifact へ持ち込まないこと、missing / invalid / stale assurance で no-write fail-closed することの既存テストがある。
- `tests/unit/infra/test_init_update.py` には shipped docs / templates / skills の snapshot-ish structural assertion がまとまっており、scope-layering、Japanese-first、DDD / EDA non-mandatory、Issue handoff package、Issue placeholder の既存 surface がある。
- `tests/unit/domain/test_workflow_state.py` は report evidence gate と Grade Specialist Evidence Gate の主要 surface で、Strict / Critical readiness を draft artifact existence だけで進めない設計に近い。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` は issue `draft-design` / `draft-plan` 作成時に assurance contract を `verify_contract` し、profile artifact template を読む。ここは既存 runtime contract であり、今回の主作業は不足 regression test と docs/smoke matrix の補強で済む可能性が高い。

## 3. Design Decisions

- `[N] DES-001` Scope-layering は single provider-side reference を正本にし、templates / docs / skills には thin link と局所 guidance だけを置く。
- `[N] DES-002` Authority checks は raw artifact が canonical authority と読める文面、decision-only Issue が execution-ready と読める文面、full responsibility table の重複を検出対象にする。
- `[N] DES-003` DDD / EDA checks は「語彙の存在」ではなく「必須化」を検出する。`DDD 必要時` や補助語彙は許容する。
- `[N] DES-004` Epic handoff は `draft-design` / `draft-plan` path index、canonical placeholder boundary、handoff-ready / execution-ready split、Option B split を持つ。
- `[N] DES-005` 日本語ファースト checks は本文 guidance の存在を検査し、path / command / identifier / fixed terms の英語を許容する。
- `[N] DES-010` `new artifact draft-design` / `draft-plan` は runtime-owned artifact primitive であり、canonical docs を変更しない。`assurance compose` は canonical compose 専用である。
- `[P] DES-013` この Issue は docs/tests-only を基本とする。runtime/code 変更は既存 tests が証明できない contract gap を実際に見つけた場合だけに限定する。

## 4. Alternatives Considered

| 代替 | 採用しない理由 |
|---|---|
| 自然言語の品質をすべて regex で合否判定する | `I275-EC-001` に反する。構造欠落だけ machine に寄せ、意味品質は reviewer finding とする。 |
| DDD / EDA 文字列を全面禁止する | `I275-EC-002` に反する。補助語彙と mandatory wording の区別が必要。 |
| 日本語以外の token 数や英字率で failure にする | `I275-EC-003` に反する。path / command / identifier を誤検知しやすい。 |
| `validate` にすべての semantic smoke を組み込む | overbuild。`validate` は構造整合に留め、read-through / reviewer-only を併用する。 |
| 新しい runtime readiness command を作る | Issue scope を超える可能性が高い。既存 `test_workflow_state.py` と workflow docs の report gate で足りるかを先に確認する。 |

## 5. Boundary / Contract Model

対象 boundary:
- Provider assets: `src/spec_dock/assets/spec_dock/docs/`, `templates/initiative/`, `templates/epic/`, `src/spec_dock/assets/install_root/.agents/skills/`
- Runtime command boundary: `new artifact draft-design` / `draft-plan`, `assurance classify`, `assurance compose`, `validate`
- Dogfooding confirmation: `spec-dock/active/issue/report.md` への evidence summary と path index read-through

契約:
- Artifact は evidence-only。canonical `design.md` へ採用するには main orchestrator の EAL と fresh `spec-reviewer` が必要。
- `draft-design` / `draft-plan` は Issue-local artifact direct child の Markdown であり、canonical docs ではない。
- Missing / invalid / stale assurance contract は fail-closed で、artifact file も canonical mutation も残さない。
- Strict / Critical readiness は specialist / fallback evidence と fresh reviewer gate を必要とし、draft artifact path の存在だけでは不足。

## 6. Dependency Analysis

- `iss-00275` は `iss-00271` から `iss-00274` の template / docs / skills / runtime primitive 変更を検証する validation slice であり、後続 `iss-00276` の final quality gate へ evidence を渡す。
- Upstream dependency:
  - `iss-00271`: Initiative template の scope / Japanese-first / architecture-neutral vocabulary。
  - `iss-00272`: Epic template の handoff package / suggested grade / final gate。
  - `iss-00273`: scope-layering reference、artifact authority、draft artifact handoff guidance。
  - `iss-00274`: Epic execution readiness、Option B split、draft artifact primitive、Strict / Critical readiness。
- Internal dependency:
  - docs/templates/skills structural smoke は runtime code に依存しない。
  - `new artifact` behavior は assurance contract と profile templates に依存する。
  - readiness gate tests は report evidence parser / workflow state domain に依存する。

## 7. Source of Record

Canonical design の source of record 候補:
- Requirement authority: `spec-dock/active/issue/requirement.md`
- Parent design authority: `spec-dock/active/epic/design.md`, `spec-dock/active/epic/plan.md`
- Workflow authority: `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, `docs/authoring/scope-layering.md`
- Runtime behavior authority: existing implementation under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` plus tests.
- This artifact: unreviewed evidence only.

Source requirement revision: active `iss-00275` as observed in `spec-dock/.agent/active.json` and `spec-dock/active/context-pack.md` on 2026-07-02.

## 8. Data Flow / Domain Model / Interface Contract

```text
Epic planning handoff
  -> Issue-local draft-design / draft-plan path index
  -> Issue planning EAL adoption decision
  -> assurance compose of canonical design.md / plan.md
  -> fresh spec-reviewer gate
  -> execution-ready only if report evidence gate passes
```

Important state split:
- `handoff-ready`: draft artifact paths / skip evidence exist and Issue planning can inspect them.
- `execution-ready`: canonical docs are composed / reviewed, plan is executable, required verification and specialist / fallback evidence are recorded.

Interface expectations:
- `./spec-dock/scripts/spec-dock new artifact draft-design --issue <id> --title "..."`
- `./spec-dock/scripts/spec-dock new artifact draft-plan --issue <id> --title "..."`
- stdout `path=...` is the only path the caller should edit.
- `./spec-dock/scripts/spec-dock validate` remains final structural validation, not semantic review.

## 9. File / Module Change Plan

Recommended target test files:
- `tests/unit/infra/test_init_update.py`
  - Add or extend structural assertions for scope-layering inbound reachability, DDD / EDA non-mandatory wording, Japanese-first guidance, Issue handoff package path index, and canonical Issue placeholder boundaries.
  - Keep assertions fragment-based, not full-document snapshots.
- `tests/cli_runtime/test_new.py`
  - Reuse existing `draft-design` / `draft-plan` tests for canonical non-mutation and no-write fail-closed.
  - Add only missing assertions if current tests do not check path-specific canonical docs before/after content.
- `tests/unit/domain/test_workflow_state.py`
  - Add or extend report evidence gate cases so Strict / Critical are blocked when only draft artifact paths exist without specialist / fallback evidence and fresh reviewer pass.
- `tests/cli_runtime/test_validate.py` or `tests/unit/application/test_validate.py`
  - Use only if `validate` should detect structural projection issues such as malformed artifact filename/index. Do not put semantic wording quality here.
- `tests/unit/infra/test_artifact_templates.py`
  - Use if artifact template guidance itself needs coverage for no-write fail-closed / evidence-only language.

Recommended docs/read-through targets:
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`

Runtime/code change expectation:
- Not necessary by default. Existing `create_node.py` and `tests/cli_runtime/test_new.py` already cover the core `draft-design` / `draft-plan` primitive.
- Runtime code changes are justified only if focused tests reveal a real behavior gap: canonical mutation, write-before-fail, stale assurance acceptance, invalid profile template acceptance, or readiness parser accepting draft-only Strict / Critical evidence.

## 10. Migration / Compatibility / Rollback

- No data migration is expected.
- Existing managed repos should receive docs/templates/skills/test improvements through normal provider asset update behavior.
- Existing historical artifacts / discussions are grandfathered; this Issue should not rewrite them.
- Rollback is normal git revert of tests/docs changes. Do not roll back to raw artifact authority, DDD / EDA mandatory wording, or pre-start canonical draft bodies.
- Manual smoke workspaces, raw logs, captures, and temporary validation outputs must remain untracked.

## 11. Observability

Required report evidence after implementation:
- Focused test commands and results.
- `./spec-dock/scripts/spec-dock validate` result.
- Any manual dogfooding read-through summary.
- Any command skipped with reason and next action.
- Gate repair summary if tests find gaps in preceding Issue outputs.
- Confirmation that raw manual artifacts were not committed.

Suggested evidence rows:
- Smoke matrix row for docs/templates/skills coverage.
- Closure coverage row mapping `I275-AC-001..011` and `I275-EC-001..004` to verification evidence.
- False-positive boundary note for DDD / EDA and Japanese-first checks.

## 12. Test Strategy

Machine tests:
- `uv run pytest tests/unit/infra/test_init_update.py -k "template or scope or japanese or handoff"` style focused run after adding structural assertions.
- `uv run pytest tests/cli_runtime/test_new.py -k "draft"` for artifact command behavior.
- `uv run pytest tests/unit/domain/test_workflow_state.py -k "specialist or report_evidence"` for readiness/report evidence gate.
- Broaden to `uv run pytest tests/unit` or `uv run pytest tests/cli_runtime` only after focused tests pass or when touched surfaces justify it.

Smoke/read-through:
- Read `scope-layering.md`, `workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, epic planning/execution skills, Initiative/Epic templates.
- Confirm thin links, handoff package fields, path index wording, non-canonical artifact boundary, Japanese-first guidance.

Reviewer-only:
- Ask `spec-reviewer` to evaluate smoke coverage relevance, false positive risk, and whether canonical design/plan/report evidence close all AC/EC.

Negative test principles:
- For DDD / EDA, assert absence of mandatory phrases such as `DDD / EDA 必須` or mandatory section language, not absence of every `DDD` token.
- For Japanese-first, assert presence of guidance and allowed-original boundary, not total absence of English.
- For artifact authority, assert absence of `authority: accepted` / `adoption_status: adopted` in draft artifacts and absence of wording that artifact existence alone grants readiness.

## 13. ADR Candidates

- None required for this Issue if implementation remains docs/tests-only.
- ADR candidate only if tests reveal a new cross-Issue policy, such as moving readiness enforcement from docs/report gate into runtime `validate` or a new command surface.

## 14. Risks

- Overfitting string assertions to exact prose can cause noisy failures during harmless wording edits.
- Under-testing structural gaps can let raw artifact authority or draft-only readiness regress.
- The generated artifact path printed by `new artifact` may include a display prefix that differs from the repo-relative actual path; callers should verify the actual file under active issue artifacts and use the returned / resolved path consistently.
- Current issue directory already has unrelated local modifications and another draft-plan artifact; integration must avoid attributing those to this system-architect draft.
- The current issue requirement says `strict`; any canonical design composed from Standard profile would be a planning inconsistency to resolve before implementation.

## 15. Requirement Clarification Requests

None for the main orchestrator before drafting canonical design.

Clarification candidates if implementation uncovers gaps:
- Should any newly discovered readiness gap become runtime `validate` behavior, or remain docs/report-gate evidence?
- If Japanese-first wording drift appears in historical artifacts, should it be grandfathered or repaired in this Epic?

## 16. Integration Notes for Main Orchestrator

- Treat this artifact as unreviewed design evidence for canonical `design.md`.
- Recommended canonical design stance: docs/tests-only unless focused tests prove runtime behavior gaps.
- Canonical design should explicitly mark `iss-00275` as `strict` per requirement, even if generated draft templates say Standard.
- Integrate AC/EC mapping as design traceability, then let `plan.md` turn it into closure IDs and step-local test cases.
- Do not adopt this artifact without EAL disposition and fresh `spec-reviewer` pass against the integrated canonical docs.

Leaf evidence used: none. This draft used local repository source reads only.

Forbidden actions avoided: no canonical docs edited, no implementation files edited, no tests edited, no templates edited, no skills edited, no report edited, no GitHub mutation, no phase promotion, no reviewer-pass claim.

Unresolved requirement gaps: none known.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
