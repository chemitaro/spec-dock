---
created_by_role: system-architect
scope_id: iss-00254
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/spec_dock/docs/workflow_clarification.md
  - src/spec_dock/assets/spec_dock/docs/phase_requirement.md
  - src/spec_dock/assets/spec_dock/docs/phase_design.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
  - src/spec_dock/assets/spec_dock/templates/issue/report.md
  - src/spec_dock/assets/spec_dock/templates/epic/report.md
  - src/spec_dock/assets/spec_dock/templates/initiative/report.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/artifact_preflight.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py
  - tests/cli_runtime/test_workflow.py
  - tests/cli_runtime/test_new.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/spec_dock/docs/phase_design.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/templates/issue/report.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py
  - tests/cli_runtime/test_workflow.py
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# iss-00254 G3 Evidence Gate 設計提案

この文書は system-architect による委任 design draft です。canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映、採否、phase promotion、reviewer pass、issue readiness は主張しません。

## 1. Requirement Coverage

- AC-001: phase promotion は fresh `spec-reviewer` の `passed` だけを通す。`waived` / `provisional` / `unavailable` / `denied` / `stale` は evidence として記録できるが pass ではない。
- AC-002: delegated draft adoption は `report.md` の Evidence Adoption Ledger（EAL）へ source、claim、target、rationale、evidence、next_action を残す。
- AC-003: stale draft / stale reviewer evidence は promotion evidence に使えない。stale / blocked EAL entry が未解決なら readiness と phase promotion を block する。
- AC-004: Standard は specialist use または skip reason、Strict / Critical は specialist evidence または unavailable / manual fallback evidence を report evidence contract に入れる。
- AC-005: missing adoption evidence / reviewer evidence は runtime readiness の block reason として扱う。ただし R0 の placeholder classifier を再設計しない。
- AC-006: discussion draft は authority、adoption、reviewer pass、phase completion、implementation readiness を自己主張しない。

## 2. Existing Context Findings

- `workflow_spec_authoring.md` は、fresh `spec-reviewer` gate、Issue grade matrix、delegated authoring policy、EAL、scope-local discussion write gate、Promotion Record をすでに定義している。
- `phase_design.md` / `phase_plan.md` は、Standard の specialist skip reason、Strict / Critical の unavailable / manual fallback evidence、delegated draft provenance、failure condition を phase-specific に定義している。
- `workflow_issue.md` は、execution / issue finish / final quality gate の report evidence を厚く持つ。特に issue finish は local delegated artifact gate と EAL gate を GitHub close / active clear 前に fail-closed で見る方針を持つ。
- `templates/*/report.md` と active `report.md` は EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status を持つが、grade-specific specialist/fallback evidence を promotion/readiness gate として読む runtime contract はまだ薄い。
- runtime の `workflow_state.py` は requirement/design/plan の scaffold/executable 判定を行うが、report evidence、fresh reviewer、EAL、grade-specific specialist/fallback evidence は readiness 判定へ接続していない。
- `artifact_preflight.py` は required artifact existence のみを見る。`workflow_status` / `guidance` の readiness は主に `workflow_state.py` が担っている。
- `delegated_authoring.py` は scope-local discussion direct child、required provenance、non-authority state、exactly-one new discussion draft の diff guard を持つ。これは G3 の adoption gate で再利用すべき既存 boundary である。
- `new doc draft-design` / `draft-plan` の profile template routing と fail-closed tests は既に存在する。G3 は PR/code-review policy や G2 routing enforcement へ広げない。

## 3. Design Decisions

- D1: `Spec Authoring Evidence Gate` を docs/template/runtime の共通語彙として固定し、phase promotion と issue readiness の evidence check を同じ report evidence source から読む。
- D2: gate は `report.md` を source of observed evidence とする。canonical artifacts の内容そのものではなく、fresh reviewer verdict、EAL disposition、delegated draft lifecycle、grade-specific specialist/fallback evidence の記録有無を確認する。
- D3: runtime は最初は textual/structural fail-closed validator として追加する。schema 導入は別 issue にせずともよいが、G3 では report template の stable headings / accepted tokens を最小 contract とする。
- D4: `workflow_status` / `guidance issue-execution` の `ready` 判定前に `Report Evidence Gate` を挿入する。missing / stale / blocked の場合は `kind=blocked`、`reason_code` は個別 code にする。
- D5: `issue finish` 側の EAL/local delegated gate 方針は再定義せず、同じ validator または同じ domain predicate を呼べるよう責務を切り出す。
- D6: PR observation、code-reviewer policy、GitHub Codex review trigger、blocker-centric repair は G3 の非ゴールとして明示し、final PR/code-review gate は既存 `workflow_issue.md` のまま使う。

## 4. Alternatives Considered

- A1: docs/template だけで終える案。既存 workflow wording はかなり揃っているが、runtime readiness が `ready` を返す path に evidence gate がないため AC-005 を満たしにくい。
- A2: report evidence を完全 YAML/JSON schema 化する案。将来は望ましいが、G3 で report authoring surface 全体を移行すると PR/code-review policy redesign と同程度に広がる。
- A3: `spec-reviewer` 実行そのものを runtime が起動する案。SpecDock runtime の現在責務は state/guidance/readiness であり、agent invocation orchestration まで持たせると boundary が広がる。
- A4: issue finish だけで gate する案。implementation start / issue readiness の手前で stale draft や missing reviewer を止められないため、phase promotion/readiness の要求に不足する。

## 5. Boundary / Contract Model

- Canonical owner: main orchestrator。canonical docs と `report.md` の最終採否、EAL、Promotion Record、phase promotion を所有する。
- Evidence producer: delegated specialist。`discussions/` 直下の flat Markdown draft 1 件だけを作り、authority/adoption/pass/readiness を自己主張しない。
- Reviewer gate: fresh `spec-reviewer`。draft ではなく、main orchestrator が統合した canonical artifact と report evidence を review する。
- Runtime readiness: `workflow_status` / `guidance issue-execution`。canonical docs と report evidence を読んで execution handoff 可否を fail-closed に返す。
- Template/report contract: report templates は evidence slots と token vocabulary を提供するが、templates 自体を compliance authority とは扱わない。

## 6. Dependency Analysis

- Upstream: G1 の grade matrix wording、G2 の profile-aware draft routing、R0 の placeholder/executable artifact readiness preflight。
- Required existing surfaces: `workflow_spec_authoring.md`、`phase_design.md`、`phase_plan.md`、`workflow_issue.md`、`templates/issue/report.md`、`workflow_state.py`、`delegated_authoring.py`。
- Runtime dependency direction: `commands/presentation -> application -> domain` を維持する。report evidence predicate は domain、file read / active target resolve は application/infra 側に置く。
- Dogfooding parity: provider-side `src/spec_dock/assets/spec_dock/...` を authority とし、dogfooding `spec-dock/...` は validation target として inspection する。

## 7. Source of Record

- Requirement source revision: `iss-00254` active `requirement.md`、最終更新 `2026-07-01`、Issue Grade `strict`。
- Parent source: `epic-00224` E-RQ-022 / E-AC-022、Epic plan G3。
- Runtime authority source: `.assurance.json` の `classification.authorized_profile`、`workflow_state.py` の readiness state、`spec-dock/.agent/active.json` の active authority。
- Evidence source: active issue `report.md` の EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status / Final Spec Review Gate。

## 8. Data Flow / Domain Model / Interface Contract

```text
canonical docs + report.md
  -> ReportEvidenceReader
  -> SpecAuthoringEvidenceGate
  -> WorkflowState(kind=ready|blocked, reason_code=...)
  -> Guidance runbook / issue finish preflight
```

Proposed value objects:

- `ReportEvidenceStatus`: `passed`, `missing`, `stale`, `blocked`, `incomplete`, `not_applicable`
- `ReviewerEvidence`: phase/gate, reviewer role, freshness, state, target artifact, target hash or revision if available
- `DelegatedAdoptionEvidence`: source path, source role, adoption status, target artifact, blocking flag, next action
- `GradeSpecialistEvidence`: grade, phase, specialist used/skipped/unavailable/fallback, rationale, blocking flag
- `ReportEvidenceGateResult`: `ok`, `reason_code`, `details`

Proposed block reason codes:

- `report-missing`
- `spec-reviewer-evidence-missing`
- `spec-reviewer-evidence-stale`
- `adoption-evidence-missing`
- `adoption-evidence-stale-or-blocked`
- `delegated-draft-evidence-invalid`
- `grade-specialist-evidence-missing`
- `manual-fallback-evidence-missing`

## 9. File / Module Change Plan

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - G3 term を `Report Evidence Gate` として phase promotion / readiness に明示接続する。
  - `passed` 以外の reviewer state が non-pass である wording を維持する。
- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - Standard skip reason、Strict/Critical unavailable/fallback evidence の report destination を EAL / Delegated Draft Evidence / Spec Authoring Gate に具体化する。
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - plan authoring でも same gate vocabulary を使い、execution handoff 前の report evidence gate を明記する。
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - issue readiness / issue finish / final spec review gate が同じ report evidence predicate を使うことを明記する。
- `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - grade-specific specialist/fallback evidence の最小 table row / accepted token を追加する。
  - Final Spec Review Gate と Spec Authoring Gate の使い分けを短く示す。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
  - report evidence gate の result を受け取り、ready 前に block reason を返せる shape にする。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - active issue dir から report text を読み、domain predicate に渡す。
- `tests/cli_runtime/test_workflow.py`
  - missing EAL / stale reviewer / missing grade-specific evidence で `guidance issue-execution` が blocked になる tests を追加する。
- `tests/cli_runtime/test_new.py` または report template tests
  - generated report template に grade-specific evidence slots があることを確認する。

## 10. Migration / Compatibility / Rollback

- Existing issues は strict-legacy compatibility path を壊さない。ただし G3 対象以降の adaptive/grade-aware issue では report evidence gate を fail-closed にする。
- Historical discussion drafts は grandfathered evidence とし、manifest-heavy old artifacts を削除・rename・validation failure 化しない。
- Rollback は runtime predicate call を feature-local に戻し、docs/template wording は G3 issue revert で戻せる範囲に保つ。
- Report template に追加する token は既存 ledger rows を破壊しない additive change にする。

## 11. Observability

- `guidance issue-execution` / `workflow status --format json` に `reason_code` と detail を出す。
- report evidence gate の failure detail は、missing section、missing row、non-pass reviewer state、stale/blocked EAL entry、grade/fallback missing の単位で返す。
- raw reviewer transcript や private reasoning は記録しない。report には verdict、scope、evidence path、next action だけを置く。

## 12. Test Strategy

- Docs/template inspection:
  - `templates/issue/report.md` に EAL、Delegated Draft Evidence、Spec Authoring Gate、Reviewer Gate Status、grade-specific specialist/fallback evidence slot がある。
- Runtime red tests:
  - substantive requirement/design/executable plan があっても `report.md` に fresh `spec-reviewer passed` がなければ blocked。
  - EAL に `stale` または `blocked` unresolved entry がある場合は blocked。
  - delegated draft adoption claim があるが EAL entry がない場合は blocked。
  - Standard で specialist skipped なのに skip reason がない場合は blocked。
  - Strict/Critical で specialist unavailable/fallback evidence がない場合は blocked。
- Runtime green tests:
  - required report evidence が揃うと existing plan/executable readiness と合わせて `ready` になる。
  - Lite でも fresh `spec-reviewer passed` がない場合は ready にならない。
- Regression boundary:
  - `new doc draft-design` / `draft-plan` の authorized_profile routing tests は既存のまま維持する。
  - PR observation / code-reviewer tests は G3 では変更しない。

## 13. ADR Candidates

- ADR candidate なし。G3 は E-RQ-022 と既存 `workflow_spec_authoring.md` の方針を issue-local に実装へ落とす範囲で足りる。
- ただし report evidence を将来 machine-readable schema へ移す場合は、別 ADR または follow-up issue で検討する価値がある。

## 14. Risks

- Textual report parsing は false positive / false negative を起こしうる。最初は accepted token と stable headings を狭く定義し、missing は fail-closed にする。
- `Spec Authoring Gate` と `Final Spec Review Gate` の境界が曖昧だと、phase promotion と final execution completion が混線する。docs/template で phase gate と final gate の用途を分ける必要がある。
- Existing strict-legacy issue へいきなり強い report gate を適用すると dogfoodingが止まる可能性がある。対象を grade-aware/adaptive issue に絞るか、legacy fallback reason を明示する。
- Runtime readiness が report evidence を読むようになると、report template drift が runtime failure になる。provider/dogfooding parity inspection と focused tests が必要。

## 15. Requirement Clarification Requests

- none

現時点の要件は G3 の scope / non-goal / AC が十分に具体化されている。未確定として残すなら、runtime gate を legacy issue 全体へ即時適用するか、新規 grade-aware issue へ限定するかの rollout boundary だけである。ただしこれは design/plan で conservative default を選べるため blocking ではない。

## 16. Integration Notes for Main Orchestrator

- この draft を採用する場合、main orchestrator は active issue `report.md` の EAL に本 artifact の採否を記録し、採用部分だけ canonical `design.md` / `plan.md` へ再記述する。
- Fresh `spec-reviewer` は、この discussion draft ではなく、統合後の canonical docs と report evidenceを対象に実行する。
- G3 の最小実装は `workflow_state.py` readiness predicate + report template/docs + focused workflow tests で閉じるのが妥当で、PR/code-review policy redesign は扱わない。
- Suggested closure mapping:
  - AC-001: docs + runtime missing/stale reviewer block tests
  - AC-002/AC-003: EAL template/docs + stale/blocked adoption tests
  - AC-004: grade-specific evidence template/docs + Standard/Strict/Critical tests
  - AC-005: `guidance issue-execution` block reason tests
  - AC-006: delegated authoring diff guard/provenance docs, existing tests維持

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
