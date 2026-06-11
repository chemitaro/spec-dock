---
種別: disc
ID: "20260610t034048z-disc"
タイトル: "Implementation Planner Draft"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["iss-00178"]
関連: []
authority: "proposed"
created_by_role: implementation-planner
scope_id: iss-00178
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
derived_from:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# 20260610t034048z-disc Implementation Planner Draft

## 1. Plan Summary

この draft は、iss-00178 `Review Feedback Triage` の reviewer-pass 済み requirement / design を、canonical `plan.md` へ採用可能な実装計画へ変換するための delegated planning evidence である。canonical authority、phase promotion、implementation readiness、reviewer pass は主張しない。

実装は docs / skill guidance 変更に閉じる。runtime `new doc --template`、new doc type、`spec_dock_runtime`、自動分類 runtime、CI log parser、GitHub mutation は対象外であり、必要性が見つかった場合は実装を止めて plan amendment と fresh review に戻す。

実行順は、design の依存関係分析どおり、運用主体である provider-side `github-pr-merge-preparer` の contract を先に固定し、次に `github-pr-observation` の collection-only boundary を補強し、最後に issue discussion rules と dogfooding parity を確認する。

想定 closure ID は `tc-001` から `tc-012` までとし、すべて docs-only / inspect-only を基本にする。S04 で supported sync/update path を使う場合だけ command evidence を追加する。

## 2. Requirement / Design Traceability

Source revision note:

- Requirement source: `spec-dock/active/issue/requirement.md`, `ID=iss-00178`, `最終更新=2026-06-10`, user-provided fresh pass.
- Design source: `spec-dock/active/issue/design.md`, `ID=iss-00178`, `最終更新=2026-06-10`, user-provided fresh pass.
- Report ledger source: `spec-dock/active/issue/report.md`, current Evidence Adoption Ledger includes system-architect draft adoption toward `design.md`; this implementation-planner draft remains unreviewed until main orchestrator adoption.

Traceability:

| Requirement / design item | Planned step | Closure IDs | Evidence level |
|---|---:|---|---|
| AC-001 PR Repair Triage Gate | S01 | `tc-001` | inspect-only |
| AC-002 batch dedicated skeleton | S01 | `tc-002` | inspect-only |
| AC-003 inventory classification vocabulary | S01 | `tc-003` | inspect-only |
| AC-004 repair unit handoff | S01 | `tc-004` | inspect-only |
| AC-005 non-fix disposition rationale | S01 | `tc-005` | inspect-only |
| AC-006 merge-prepared predicate / response checklist | S01 | `tc-006` | inspect-only |
| AC-007 observation boundary preservation | S02 | `tc-007` | inspect-only |
| AC-008 scope containment / no runtime or template contract change | S01-S04, S99 | `tc-008`, `tc-012` | inspect-only |
| EC-001 timeout / observation limit | S01 | `tc-009` | inspect-only |
| EC-002 same root cause grouping | S01 | `tc-010` | inspect-only |
| EC-003 false positive / stale review | S01 | `tc-011` | inspect-only |
| EC-004 scope expansion | S01 | `tc-009` | inspect-only |
| EC-005 repeated failure class | S01 | `tc-009` | inspect-only |
| Provider-side source-of-truth / dogfooding parity | S04 | `tc-013` | inspect-only or command evidence |
| Docs impact resolution | S90 | `tc-014` | inspect-only |
| Final quality gate | S99 | `tc-015` | command + reviewer evidence |

## 3. Milestones

M1: Provider skill contract fixed

- Complete S01 and S02.
- `github-pr-merge-preparer` owns PR Repair Triage Gate and judgment vocabulary.
- `github-pr-observation` remains collection-only and does not gain classification, disposition, or grouping responsibility.

M2: Discussion contract and dogfooding parity resolved

- Complete S03 and S04.
- `docs/rules/issue/discussions.md` names PR repair batch / unit as existing `disc` usage without duplicating the full skeleton.
- Dogfooding copies are confirmed or synchronized through the safe provider-first path.

M3: Plan-wide docs impact and final gates ready

- Complete S90 and S99.
- Runtime/template non-change is inspected.
- Required reviewer gates are explicit and not replaced by this draft.

## 4. Dependency-Derived Execution Order

Dependency basis:

- `design.md` states full operational skeleton belongs in `github-pr-merge-preparer` because it creates and operates batch artifacts.
- `github-pr-observation` produces authoritative stdout JSON and must not depend on merge-preparer vocabulary.
- `docs/rules/issue/discussions.md` should stay a short catalog contract and refer to the skill guidance rather than duplicate the skeleton.
- Parent epic fixes `src/spec_dock/assets/install_root/` as agent-tooling source of truth; dogfooding `.agents/` is confirmation / installed-copy surface.

Execution order:

1. S01: Modify provider-side `github-pr-merge-preparer/SKILL.md`.
2. S02: Modify provider-side `github-pr-observation/SKILL.md` minimally.
3. S03: Modify provider-side `docs/rules/issue/discussions.md` minimally.
4. S04: Bring dogfooding copies into parity with provider sources or confirm no drift through a safe supported path.
5. S90: Resolve docs impact and record whether additional docs/templates/README updates are required.
6. S99: Run final validation and reviewer gates.

Stop before implementation and amend the plan if:

- Any step requires `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`.
- Any step requires `new doc --template`, new first-class doc types, template registry, or `spec-dock validate` structural validation for PR repair batch/unit.
- Any step requires GitHub mutation, review comment replies, thread resolution, auto-merge, branch deletion, issue close, or `spec-dock issue finish`.
- Provider-side and dogfooding copy parity cannot be achieved without deleting or rewriting issue data under `spec-dock/`.

## 5. Issue / Step Slicing

### S01 - Add PR Repair Triage Gate to provider merge-preparer skill

Behavior goal:

- After observation and before any repair delegation, `github-pr-merge-preparer` requires a PR repair batch `disc`, triages all findings/failures/limitations, creates repair unit `disc` only when needed, and uses a batch-aware merge-prepared predicate.

Allowed paths:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`

Forbidden changes:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- `src/spec_dock/assets/spec_dock/templates/**`
- `.agents/**` dogfooding copy in this step
- GitHub state, canonical issue docs, tests, package/config files

Required content:

- Insert a PR Repair Triage Gate between current workflow steps equivalent to observation freshness check and bounded fix delegation.
- Add batch dedicated skeleton with these sections: `PR / Observation Metadata`, `Batch Purpose`, `Concern Catalog`, `Inventory`, `Classification Values`, `Per-Concern Analysis`, `Repair Queue`, `Unit Discussion Plan`, `Stop Conditions`, `Merge-Prepared Gate`.
- Add inventory columns: `ID`, `source_type`, `concern`, `evidence`, `summary`, `validity`, `risk_class`, `need_to_fix`, `disposition`, `repair_unit`, `status`.
- Add classification values exactly from requirement: `validity`, `risk_class`, `need_to_fix`, `disposition`, `status`.
- Add repair unit checklist: `source_batch`, `unit_id`, `covered_ids`, `source_links`, `failure_class`, `risk_class`, `disposition`, `Validity Analysis`, `Need-To-Fix Decision`, `Root Cause`, `Options Considered`, `Recommended Design`, `Implementation Plan`, `Validation Plan`, `Implementation Result`, `Commit Evidence`, `Re-observation Result`, `Residual Risk / Follow-up`.
- Add non-fix disposition requirements for `follow-up`, `no-action`, `covered-by`, `duplicate`, `false-positive`: rationale, evidence, residual risk where relevant, and follow-up target where needed.
- Add stop conditions for timeout/observation limit, stale head, scope expansion, repeated failure class, ambiguous review intent, unresolved `needs-human`, and loop limit hit.
- Add batch-aware merge-prepared predicate: no `untriaged`, no unresolved `needs-human`, no incomplete blocking `fix-now` repair unit, rationale for non-fix dispositions, latest head SHA re-observed.
- Add response checklist fields: batch path, repair units, review-clean yes/no, merge-prepared yes/no, residual risks, human gate reason, and explicit "merge remains human action".

Concrete verification:

```bash
rg -n "PR Repair Triage Gate|fix delegation|PR repair batch|Concern Catalog|Inventory|Unit Discussion Plan|Merge-Prepared Gate" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
rg -n "validity|risk_class|need_to_fix|disposition|repair_unit|status" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
rg -n "source_batch|covered_ids|Implementation Plan|Re-observation Result|Residual Risk" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
rg -n "review-clean|merge-prepared|untriaged|needs-human|human gate" src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
```

Step closure:

- `tc-001`: Gate exists after observation and before repair delegation.
- `tc-002`: Batch skeleton sections exist.
- `tc-003`: Classification vocabulary exists.
- `tc-004`: Repair unit checklist and worker handoff exist.
- `tc-005`: Non-fix dispositions require rationale/residual risk.
- `tc-006`: Merge-prepared predicate and response checklist are batch-aware.
- `tc-009`: Stop conditions cover timeout, scope expansion, repeated failure, and human gate.
- `tc-010`: Same-root-cause grouping is represented by Concern Catalog / Per-Concern Analysis / Repair Queue.
- `tc-011`: False-positive / stale review rationale is represented.

Reviewer gate:

- Step reviewer: `spec-reviewer` for docs/spec alignment.
- If reviewer finds implementation/runtime behavior changes are needed, stop and amend plan before code changes.

Report evidence destination:

- `Implementation Delegation Gate`
- `Step Contract Closure`
- `Test Contract Closure`
- `Closure Coverage`
- `Reviewer Gate Status`
- `Step Commit Gate`

### S02 - Clarify collection-only boundary in provider observation skill

Behavior goal:

- `github-pr-observation` remains deterministic trigger and evidence collection only; classification, disposition, and repair unit grouping belong to `github-pr-merge-preparer`.

Allowed paths:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

Forbidden changes:

- Observation scripts, collector libraries, stdout JSON schema, GitHub API calls, tests, dogfooding copy in this step.

Required content:

- Add a minimal boundary note, preferably near Overview / Observation Semantics / Safety Boundary.
- State that the final stdout JSON is evidence only.
- State that this skill does not assign `risk_class`, `need_to_fix`, `disposition`, or `repair_unit`, and does not group findings into repair units.
- State that downstream workflows such as `github-pr-merge-preparer` may classify the collected evidence after verifying latest head SHA.

Concrete verification:

```bash
rg -n "collection-only|evidence collection|risk_class|need_to_fix|disposition|repair unit grouping|github-pr-merge-preparer" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md
```

Step closure:

- `tc-007`: Observation boundary preservation is explicit.
- `tc-008`: No observation script / runtime change is present.

Reviewer gate:

- Step reviewer: `spec-reviewer`.

Report evidence destination:

- Same as S01.

### S03 - Add short PR repair batch/unit discussion contract

Behavior goal:

- Issue discussion rules mention PR repair batch and repair unit as specialized existing `disc` usages without becoming the long workflow manual.

Allowed paths:

- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`

Forbidden changes:

- `spec-dock/templates/discussions/**`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- `spec-dock/docs/rules/issue/discussions.md` dogfooding copy in this step

Required content:

- Under current catalog or near `disc`, add a short contract:
  - PR repair batch is an existing `disc` control sheet for one observation / repair loop batch.
  - Repair unit is an existing `disc` detail sheet for one root-cause / fix unit.
  - Full skeleton and checklist are owned by `github-pr-merge-preparer`.
  - These docs are proposal/evidence until adopted into canonical report / plan; they do not authorize merge or issue finish.

Concrete verification:

```bash
rg -n "PR repair batch|repair unit|github-pr-merge-preparer|existing `disc`|canonical" src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md
```

Step closure:

- `tc-012`: Discussion rules contain a short catalog contract and do not duplicate full skeleton.

Reviewer gate:

- Step reviewer: `spec-reviewer`.

Report evidence destination:

- Same as S01.

### S04 - Dogfooding copy parity

Behavior goal:

- Dogfooding checked-in copies match provider-side source-of-truth for the changed skill/docs assets, using the repo's provider-first rule.

Allowed paths:

- `.agents/skills/github-pr-merge-preparer/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`
- `spec-dock/docs/rules/issue/discussions.md`

Safe approach:

- Preferred: run the supported local provider-to-consumer update path if it is expected to synchronize install_root assets and scaffold docs into the dogfooding repo without unrelated data rewrite.
- Acceptable fallback: directly copy only the three corresponding provider files into the dogfooding locations when update would touch unrelated generated state or when the plan/report records why direct parity copy is safer.
- In both paths, inspect the diff and confirm only intended dogfooding copies changed.

Candidate commands:

```bash
./spec-dock/scripts/spec-dock update .
diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md .agents/skills/github-pr-merge-preparer/SKILL.md
diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md .agents/skills/github-pr-observation/SKILL.md
diff -u src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md spec-dock/docs/rules/issue/discussions.md
git diff -- .agents/skills/github-pr-merge-preparer/SKILL.md .agents/skills/github-pr-observation/SKILL.md spec-dock/docs/rules/issue/discussions.md
```

Stop conditions:

- `update .` proposes broad unmanaged issue data rewrites unrelated to these provider assets.
- Parity requires changing generated active/canonical docs.
- Parity requires changing runtime or templates.

Step closure:

- `tc-013`: Provider and dogfooding copies are identical for the three changed surfaces, or a no-op is recorded with diff evidence.

Reviewer gate:

- Step reviewer: `code-reviewer` if installer/scaffold behavior or update command behavior changes; otherwise `spec-reviewer` for docs/spec alignment.

Report evidence destination:

- `Implementation Delegation Gate`
- `Step Contract Closure`
- `Test Contract Closure`
- `Closure Coverage`
- `Reviewer Gate Status`
- `Step Commit Gate`

### S90 - Docs Impact Resolution

Behavior goal:

- Confirm all docs impact from S01-S04 is either implemented or explicitly no-op with evidence.

Targets to inspect:

- Provider changed docs/skills.
- Dogfooding copies.
- README, templates, migration notes, workflow docs only if S01-S04 revealed a contract beyond the approved design.

Concrete verification:

```bash
rg -n "PR Repair Triage Gate|PR repair batch|repair unit|review-clean|merge-prepared" src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/spec_dock/docs/rules/issue .agents/skills spec-dock/docs/rules/issue
git diff -- src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
```

Step closure:

- `tc-014`: Docs impact is resolved; if no further docs are required, report records why the changed skill/docs surfaces are sufficient.

Reviewer gate:

- `spec-reviewer` docs/spec alignment pass.

### S99 - Final Quality Gate

Behavior goal:

- Confirm the issue-wide diff satisfies requirement/design/plan, preserves runtime scope, and has final QA/code/spec review evidence before handoff.

Required validation:

```bash
git diff --check
git diff -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime src/spec_dock/assets/spec_dock/templates
uv run pytest tests/unit/infra
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

Validation notes:

- `uv run pytest tests/unit/infra` is a conservative scaffold/installer regression lane. If unchanged docs-only scope makes it too broad for the executor environment, record the reason and run the narrowest available provider/dogfooding parity inspection instead.
- `sync --no-github` avoids GitHub live-state drift for local planning validation. If final delivery requires live state, the orchestrator can add default `sync` evidence outside this draft.

Final reviewer gates:

- `qa-reviewer`: issue-wide obligation coverage and whether additional tests are needed.
- `code-reviewer`: integrated diff review if any scaffold behavior, installer behavior, or command behavior changed; otherwise may focus on confirming no code/runtime diff.
- `spec-reviewer`: requirement/design/plan/report/docs alignment.

Step closure:

- `tc-015`: final validation commands or justified alternatives are recorded; final reviewer gates are fresh `passed` before main orchestrator claims readiness.

## 6. Test Strategy Mapping

This issue is docs / skill guidance only. Runtime tests are not the primary evidence unless implementation strays into runtime or installer behavior.

Spec-Locked Closure Index draft:

| ID | Step | Type | Spec link | Locked expectation | Observable input / state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|
| `tc-001` | S01 | acceptance | AC-001 | PR Repair Triage Gate exists after observation and before fix delegation | merge-preparer skill text | raw finding delegated without triage | yes | inspect-only | `rg` output + reviewer pass |
| `tc-002` | S01 | acceptance | AC-002 | batch skeleton contains required sections | merge-preparer skill text | incomplete control sheet | yes | inspect-only | `rg` output + reviewer pass |
| `tc-003` | S01 | acceptance | AC-003 | vocabulary includes required fields and values | merge-preparer skill text | severity-only or ad hoc classification | yes | inspect-only | `rg` output + reviewer pass |
| `tc-004` | S01 | acceptance | AC-004 | repair unit checklist and handoff exist | merge-preparer skill text | raw finding used as worker source | yes | inspect-only | `rg` output + reviewer pass |
| `tc-005` | S01 | acceptance | AC-005 | non-fix dispositions require rationale/residual risk | merge-preparer skill text | silent dismissal of findings | yes | inspect-only | `rg` output + reviewer pass |
| `tc-006` | S01 | acceptance | AC-006 | merge-prepared predicate is batch-aware and distinct from review-clean | merge-preparer skill text | endless review-clean loop or premature merge-prepared | yes | inspect-only | `rg` output + reviewer pass |
| `tc-007` | S02 | acceptance | AC-007 | observation skill is collection-only | observation skill text | collector starts making judgment | yes | inspect-only | `rg` output + reviewer pass |
| `tc-008` | S01-S04/S99 | negative | AC-008 | runtime/templates/doc type are unchanged | git diff for forbidden paths | scope creep into runtime/template registry | yes | inspect-only | empty diff |
| `tc-009` | S01 | edge | EC-001/004/005 | stop conditions cover timeout, scope expansion, repeated failures | merge-preparer skill text | unsafe repeated repair loop | yes | inspect-only | `rg` output + reviewer pass |
| `tc-010` | S01 | edge | EC-002 | same root cause can be grouped by concern/unit | merge-preparer skill text | duplicate repair units | yes | inspect-only | `rg` output + reviewer pass |
| `tc-011` | S01 | edge | EC-003 | false positive / stale review has rationale path | merge-preparer skill text | invalid finding treated as required fix | yes | inspect-only | `rg` output + reviewer pass |
| `tc-012` | S03 | acceptance | design discussion contract | discussion rules stay short and refer to skill skeleton | provider discussion rules | duplicated drift-prone skeleton | yes | inspect-only | `rg` output + reviewer pass |
| `tc-013` | S04 | integration | parent epic provider-first | dogfooding copy matches provider source | provider and dogfooding files | provider/dogfooding drift | yes | inspect-only / command | `diff -u` outputs |
| `tc-014` | S90 | docs impact | workflow_issue docs impact | docs impact resolved or justified no-op | relevant docs/skills | undocumented contract drift | yes | inspect-only | docs impact ledger |
| `tc-015` | S99 | final | workflow_issue final gate | final validation and reviewers pass | full issue diff | incomplete closure | yes | command + reviewer | final report gates |

Concrete test case seeds should be copied into canonical `plan.md` as step-local cards rather than only keeping this table.

## 7. Review Gates

Per-step gates:

- S01: `spec-reviewer` because the change is skill-text-only / workflow contract text. Escalate to `code-reviewer` only if code/runtime behavior changes.
- S02: `spec-reviewer`.
- S03: `spec-reviewer`.
- S04: `spec-reviewer` for parity copy only; `code-reviewer` if update/sync behavior, installer behavior, or scaffold generation code changes.
- S90: `spec-reviewer`.
- S99: final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.

Reviewer policy:

- Delegated worker output is not reviewer pass.
- This implementation-planner draft is not reviewer pass.
- `waived`, `provisional`, `unavailable`, or `denied` reviewer states do not satisfy readiness without explicit main-orchestrator risk acceptance, and even then must not be called `passed`.
- Any reviewer fail must be repaired and re-reviewed fresh.

## 8. Rollback / Compatibility

Rollback:

- Revert provider-side changes in the three planned provider files.
- Re-run dogfooding parity step to return checked-in copies to provider state.
- No runtime migration rollback is expected because runtime/template/doc type changes are forbidden.

Compatibility:

- Existing `disc` semantics remain unchanged.
- Existing discussion files are grandfathered; no rename or migration.
- Existing `github-pr-observation` stdout JSON contract remains unchanged.
- Existing `github-pr-merge-preparer` forbidden writes remain unchanged and should be restated, not weakened.

## 9. Docs Impact

Required docs changes:

- S01 changes `github-pr-merge-preparer` skill guidance.
- S02 changes `github-pr-observation` skill guidance.
- S03 changes issue discussion rules.
- S04 updates or confirms dogfooding copies.

Likely no-op docs:

- README: no user-facing CLI change.
- Templates: no `disc` template or new template added.
- Runtime docs: no `new doc --template` or validation contract added.
- Migration notes: no migration.

S90 must re-evaluate these after implementation. If implementation discovers a wider docs contract, stop and amend plan instead of silently expanding scope.

## 10. Final Quality Gate

Final exit contract draft:

- All required closure IDs `tc-001` through `tc-015` are closed in `report.md` with pass or justified approved-no-op.
- `git diff --check` passes.
- Forbidden runtime/template diff is empty.
- Provider/dogfooding parity is proven for changed skill/docs files.
- S90 docs impact is resolved.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` are fresh passed where required by workflow.
- PR delivery / merge-preparation is outside this plan draft's authority but must be handled by the main orchestrator before issue completion if this issue proceeds to delivery.

## 11. Plan Blockers

Current blockers:

- なし。

Plan amendment triggers:

- Runtime `new doc --template` support appears necessary.
- New discussion doc type appears necessary.
- `spec_dock_runtime` or template changes appear necessary.
- `github-pr-observation` needs JSON schema or script behavior changes.
- Reviewer requires a behavior test that cannot be satisfied by docs-only inspection.
- Dogfooding parity cannot be achieved through safe provider-first update/copy without unrelated rewrites.

## 12. Integration Notes for Main Orchestrator

Suggested adoption path:

- Add this draft to `report.md` Delegated Draft Evidence as `created_by_role=implementation-planner`, `adoption_status=unreviewed` until reviewed.
- Run post-run diff guard and record the result before adopting.
- If adopted, copy the step structure, closure index, review gates, and stop conditions into canonical `plan.md`; do not cite this draft as canonical authority by itself.
- After canonical `plan.md` is updated, run fresh `spec-reviewer` against requirement/design/plan/report.

Leaf evidence used:

- None beyond local source reads; no depth=2 leaf specialist was invoked.

Forbidden actions avoided:

- No canonical doc edit claimed.
- No implementation file, test, package/config, GitHub state, or runtime edit claimed.
- No phase promotion, reviewer pass, issue readiness, issue finish, PR merge, or user-dialogue ownership claimed.

Unresolved design gaps:

- なし。

Unresolved planning risks:

- なし。

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
