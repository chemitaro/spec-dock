---
created_by_role: implementation-planner
scope_id: iss-00274
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081006z-draft-design-epic-execution-readiness-workflow-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081007z-draft-plan-epic-execution-readiness-workflow-pre-start-seed.md
  - spec-dock/active/epic/plan.md
  - src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - .agents/skills/spec-dock-epic-execution/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
intended_targets:
  - plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: failed
source_revision: 866722ec640377acd5194efd75f46f3c954c0318
---

# iss-00274 implementation plan draft artifact

この artifact は、正規 `plan.md` を作るための evidence-only implementation plan draft です。Canonical `design.md` / `plan.md` / `report.md` への反映、reviewer pass、phase promotion、execution-ready、Issue完了は主張しません。

## 1. Plan Summary

- 目的: Epic execution skill / workflow guidance が reviewer-gated Epic planning outputs と downstream Issue handoff package を読み、Issue start / execution 前に structural readiness を確認できるようにする。
- 中心判断: この Issue はまず docs / skills-only で閉じられるかを characterization し、runtime behavior / tests が必要な場合だけ step を分岐させる。
- 実行順: Red / characterization / implementation / verification / review / finish の順に固定する。
- PR方針: この Issue では PR を作らない。完了後は `./spec-dock/scripts/spec-dock issue finish` で lifecycle closure し、`iss-00275` へバトンを渡す。Epic delivery PR は `iss-00276` が扱う。
- 主な成果: structural blocker / reviewer finding 分離、handoff-ready / execution-ready 分離、Issue-local `draft-design` / `draft-plan` primitive、日本語ファースト guidance、no per-Issue PR 方針を plan 上で追跡可能にする。

## 2. Requirement / Design Traceability

| Requirement | Plan上の扱い | 主 step |
|---|---|---|
| `I274-AC-001` | Epic requirement / design / plan / report と Issue handoff package を execution input として読む導線を入れる。 | S03 |
| `I274-AC-002` | structural blocker list を skill / workflow guidance に反映し、machine-checkable 欠落を blocking とする。 | S03 |
| `I274-AC-003` | semantic sufficiency の弱さは reviewer finding として残し、coordinator が `spec-reviewer` を置き換えないことを明記する。 | S03 |
| `I274-AC-004` | raw artifact authority leak と decision-only ready を禁止する wording を入れる。 | S03 |
| `I274-AC-005` | Issueごとの PR 作成を通常フローにせず、final PR delivery は `iss-00276` に集約する。 | S03, S08 |
| `I274-AC-006` | docs / report / artifacts の本文を日本語ファーストにする guidance を execution / readiness に反映する。 | S03, S04 |
| `I274-AC-007` | `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` を pre-start Issue handoff artifact primitive として扱う。 | S04 |
| `I274-AC-008` | actor / specialist / depth 別 draft command を増やさず、`assurance compose` は canonical compose 専用に保つ。 | S04 |
| `I274-AC-009` | handoff-ready と execution-ready を分離し、grade別 specialist obligation を readiness evidence gate に反映する。 | S03, S05 |
| `I274-EC-001` | readiness check が `spec-reviewer` の代替にならないことを禁止条件として検証する。 | S06, S07 |
| `I274-EC-002` | structural blocker がある Issue を実行可能として扱う導線を禁止する。 | S03, S06 |
| `I274-EC-003` | reviewer finding をすべて blocking にせず、Option B の分離を保つ。 | S03, S07 |
| `I274-EC-004` | PR merge / credentialed GitHub mutation をこの Issue に含めない。 | S08 |

Design evidence は current canonical `design.md` に placeholder が残るため、pre-start seed artifact と Epic plan の Slice 04 handoff を補助 evidence として使う。ただし採否は main orchestrator が canonical `plan.md` / `report.md` ledger で判断する。

## 3. Milestones

| Milestone | 成果 | Step | Closure |
|---|---|---|---|
| M0 Red / readiness baseline | 現行 skill / docs が要求項目を満たさないこと、または docs-only で Red を置けない場合の inspect-only baseline を固定する。 | S01 | AC001-009 / EC001-004 の sensitivity evidence |
| M1 Characterization | docs / skills-only で十分か、runtime behavior / tests が必要かを判定する。 | S02 | AC007-009 / EC004 |
| M2 Implementation | provider-side skill / workflow docs を最小更新し、dogfooding skill mirror の扱いを判定する。 | S03-S04 | AC001-009 / EC001-003 |
| M3 Verification | grep / read-through / focused tests / validate で closure を確認する。 | S05-S06 | AC001-009 / EC001-004 |
| M4 Review | docs/spec alignment と必要時 code/test review の gate を通す。 | S07 | EC001-003 |
| M5 Finish handoff | PRを作らず `issue finish` し、`iss-00275` に smoke evidence を渡す。 | S08 | AC005 / EC004 |

## 4. Dependency-Derived Execution Order

1. `iss-00273` の成果である `scope-layering.md`、`workflow_epic.md`、`workflow_issue.md`、provider-side `spec-dock-epic-execution` skill を読む。
2. `iss-00274` の Red / characterization で、現行 guidance の欠落と runtime change 要否を先に固定する。
3. provider authority である `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` と必要な `src/spec_dock/assets/spec_dock/docs/...` を更新する。
4. dogfooding mirror `.agents/skills/spec-dock-epic-execution/SKILL.md` は、provider change を反映すべきか、後続 sync / update evidence で足りるかを docs impact step で判断する。
5. `iss-00275` は validation slice なので、この Issue では smoke test 観点と expected evidence を渡し、網羅的 smoke matrix は後続に残す。

## 5. Issue / Step Slicing

### S01 Red baseline

- Red分類: `characterization-first` または `inspect-only`。
- Goal: 現行 `spec-dock-epic-execution` skill / workflow docs が、Issue handoff package、Option B structural blocker / reviewer finding split、draft artifact primitive、handoff-ready / execution-ready split を十分に案内しているかを観測する。
- Expected Red: `rg` / manual read-through で必須語彙や禁止語彙の不足が見つかる。
- Allowed paths: read-only。
- Verification seed:
  - `rg -n "handoff-ready|execution-ready|structural blocker|reviewer finding|draft-plan|draft-design|iss-00276|issue finish" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
- Report evidence: `report.md#step-evidence` / Red or alternative evidence。

### S02 Characterization / scope decision

- Goal: docs / skills-only で足りるか、runtime behavior / tests が必要かを判定する。
- Decision rule:
  - guidance wording だけで behavior が変わらないなら docs / skills-only。
  - `new artifact draft-design` / `draft-plan` の command behavior、canonical non-mutation、assurance stale fail-closed、Issue readiness projection を runtime が判定する必要が見つかった場合は runtime/test step を追加し、plan amendment と reviewer gate を先に通す。
- Close condition: 判定理由、選ばなかった path、必要な verification level を `report.md` に残す。
- Closure: `I274-AC-007`, `I274-AC-008`, `I274-AC-009`, `I274-EC-004`。

### S03 Implementation: Epic execution skill readiness guidance

- Delegated role: `doc-writer`。
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - 必要時のみ `.agents/skills/spec-dock-epic-execution/SKILL.md`
- Required changes:
  - first-read input に reviewer-gated Epic docs と Issue handoff package を追加する。
  - structural blockers と reviewer findings を分ける。
  - raw artifact authority leak、decision-only ready、missing / stale reviewer pass、missing executable plan structure、missing delegation contract、missing verification、missing reviewer focus、unresolved blocking report entries を fail-closed として扱う。
  - semantic reviewer 非代替、fresh reviewer gate 非省略、no per-Issue PR / `iss-00276` final PR delivery を明示する。
  - 日本語ファースト authoring を execution / readiness 中の docs / report / artifacts に適用する。
- Closure: `I274-AC-001` から `I274-AC-006`, `I274-AC-009`, `I274-EC-001` から `I274-EC-003`。

### S04 Implementation: workflow docs / draft artifact primitive

- Delegated role: `doc-writer`。
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - 必要時のみ `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- Required changes:
  - Epic execution lifecycle に handoff inspection と Issue readiness の structural gate を置く。
  - `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` を Issue-local pre-start handoff primitive として確認する。
  - `assurance compose` は canonical compose 専用で、draft artifact 作成 command ではないことを残す。
  - actor / specialist / depth 別 draft command を増やさない。
- Closure: `I274-AC-001`, `I274-AC-002`, `I274-AC-004`, `I274-AC-007`, `I274-AC-008`, `I274-AC-009`。

### S05 Verification: docs / skills consistency

- Goal: docs / skills-only path の closure を command と read-through で確認する。
- Commands:
  - `rg -n "structural blocker|reviewer finding|handoff-ready|execution-ready|draft-design|draft-plan|assurance compose|iss-00276|issue finish" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
  - `rg -n "semantic reviewer|spec-reviewer|raw artifact|decision-only|日本語ファースト" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
  - `./spec-dock/scripts/spec-dock validate`
- Closure: all AC / EC, subject to reviewer。

### S06 Conditional runtime / test verification

- Trigger: S02 が runtime behavior / tests required と判定した場合だけ。
- Delegated role: `dev-coder`。
- Allowed paths:
  - focused runtime code under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - focused tests under `tests/cli_runtime/` or `tests/unit/...`
- Forbidden unless plan amended:
  - large runtime validation system
  - public CLI contract changes beyond existing `new artifact` behavior
  - dependency algorithm changes
  - GitHub mutation behavior
- Commands:
  - `uv run pytest tests/cli_runtime`
  - narrower `uv run pytest <focused-test-path>`
  - `./spec-dock/scripts/spec-dock validate`

### S07 Review gate

- docs / skills-only diff: fresh `spec-reviewer` docs/spec alignment pass。
- runtime / tests diff: `code-reviewer` pass と `qa-reviewer` focus を追加し、必要なら `spec-reviewer` も再実行。
- Reviewer focus:
  - lifecycle / authority correctness
  - structural blocker と reviewer finding の分離
  - `spec-reviewer` 非代替
  - draft artifact primitive と canonical non-mutation
  - no per-Issue PR / `iss-00276` final delivery
  - 日本語ファースト guidance

### S08 Finish / handoff

- Goal: この Issue の report evidence を閉じ、PRを作らず `issue finish` で `iss-00275` へ渡す。
- Commands:
  - `git status --short`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock issue finish`
  - `./spec-dock/scripts/spec-dock issue start iss-00275`
- Handoff evidence:
  - changed docs / skills paths
  - S02 docs-only / runtime-required decision
  - closure index result for `I274-AC-001..009` / `I274-EC-001..004`
  - reviewer findings / blockers disposition
  - grep / validate / focused test output

## 6. Test Strategy Mapping

| Evidence level | Use when | Commands / evidence |
|---|---|---|
| Red / characterization | docs wording gap and scope decision | `rg` checks and read-through summary |
| Docs / skill consistency | docs-only / skills-only implementation | `rg` terms, manual read-through, `spec-reviewer` |
| Runtime focused tests | S02 finds runtime behavior change required | `uv run pytest tests/cli_runtime` or focused unit tests |
| Validation | every path | `./spec-dock/scripts/spec-dock validate` |
| Final handoff | before `issue finish` | report ledger closure and clean / intentional diff check |

## 7. Review Gates

- Step reviewer mapping:
  - S03 / S04 docs-only changes: `spec-reviewer` required。
  - S06 runtime / tests changes: `code-reviewer` and `qa-reviewer` required; `spec-reviewer` re-check if workflow contract changed。
- Required reviewer focus:
  - structural blocker / reviewer finding 分離が Option B に合うこと。
  - structural readiness が `spec-reviewer` の semantic review を置換しないこと。
  - raw artifact を canonical authority と扱わないこと。
  - draft artifact command を actor / specialist / depth 別に増やしていないこと。
  - `assurance compose` を canonical compose 専用として保つこと。
  - no per-Issue PR と `issue finish` -> `iss-00275` handoff が明確であること。

## 8. Rollback / Compatibility

- Rollback: docs / skill wording は targeted revert 可能。runtime behavior を変更した場合は tests と runtime code を同じ revert unit にする。
- Compatibility: `new artifact draft-design` / `draft-plan` は existing catalog として扱い、command shape を増やさない。
- GitHub / PR: この Issue は credentialed GitHub mutation、PR creation、PR merge、auto-merge を含めない。
- Existing workspaces: provider-side asset change は新規 / update 先に効く。dogfooding mirror 反映が必要なら report に反映方法を残す。

## 9. Docs Impact

Allowed paths:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
- `.agents/skills/spec-dock-epic-execution/SKILL.md` only if dogfooding mirror refresh is intentionally included
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` only for narrow link / wording correction

Forbidden paths without replan:

- canonical `spec-dock/active/issue/design.md`
- canonical `spec-dock/active/issue/plan.md`
- canonical `spec-dock/active/issue/report.md` except main orchestrator integration
- code / tests / runtime unless S02 records runtime-required decision and plan is amended
- package / config / secrets / GitHub workflow files
- metadata direct edits

Docs impact must state whether docs / skills-only was sufficient. If docs impact is `none`, the report must include why no docs / skills update was needed and reviewer confirmation.

## 10. Final Quality Gate

- `I274-AC-001..009` and `I274-EC-001..004` have closure rows with evidence.
- S02 scope decision is recorded: docs / skills-only or runtime-required.
- Required reviewer gates are fresh `passed`; unavailable / waived / provisional is not a pass.
- `./spec-dock/scripts/spec-dock validate` passes or failure is classified with reason and next action.
- No PR is created for this Issue.
- `issue finish` is run only after report evidence and closure gates are complete.
- `iss-00275` handoff evidence is explicit enough for smoke tests to verify structural blocker / reviewer finding split.

## 11. Plan Blockers

- Current canonical `design.md` / `plan.md` content seen by this adapter appears template-like despite approved frontmatter. Main orchestrator should decide whether to adopt the system-architect draft and this implementation-planner draft into canonical docs before execution.
- If S02 finds runtime behavior is required, the current docs-only planning assumption is insufficient; canonical `plan.md` must add S06 and focused tests before implementation.
- If provider-side and dogfooding skill copies diverge after updates, report must explain whether immediate mirror update, `spec-dock update`, or later dogfooding validation owns the drift.
- No unresolved user clarification is required for this draft. Main orchestrator may still need reviewer feedback before canonical adoption.

## 12. Integration Notes for Main Orchestrator

- Changed artifact path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00274-update-epic-execution-handoff-and-issue-readiness-workflow/artifacts/20260702t111145z-draft-plan-implementation-planner-plan-draft.md`
- Source requirement / design revision: read from working tree at `HEAD=866722ec640377acd5194efd75f46f3c954c0318`; active symlink input paths showed no path-specific `git diff --name-only` output during draft creation.
- Lightweight provenance: implementation-planner adapter read active issue docs, seed artifacts, parent Epic plan, scope-layering reference, workflow docs, and both Epic execution skill copies; no leaf delegation was used.
- Forbidden actions avoided: no canonical edit, no code/test/docs/skill/template edit, no metadata direct edit, no PR, no GitHub mutation, no phase promotion, no reviewer pass claim.
- Unresolved design gaps: canonical `design.md` / `plan.md` still need main-orchestrator adoption from evidence and fresh reviewer pass before execution; runtime behavior need is intentionally deferred to S02.
- Diff guard: `./spec-dock/scripts/spec-dock validate` passed, but global `git status --short` showed pre-existing or concurrent changes outside this artifact, so artifact-only worktree diff guard is recorded as `failed` pending main-orchestrator review.
- Evidence to pass to `iss-00275`: final changed path list, S02 scope decision, grep/read-through results, `validate` result, reviewer verdicts, and closure index result for all AC / EC.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
