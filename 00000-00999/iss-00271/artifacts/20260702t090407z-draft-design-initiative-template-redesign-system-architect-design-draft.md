---
created_by_role: system-architect
scope_id: iss-00271
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/.agent/active.json
  - spec-dock/.agent/index.json
  - spec-dock/.agent/deps-issues.json
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md
  - src/spec_dock/assets/spec_dock/templates/initiative/requirement.md
  - src/spec_dock/assets/spec_dock/templates/initiative/design.md
  - src/spec_dock/assets/spec_dock/templates/initiative/plan.md
  - src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
  - src/spec_dock/assets/spec_dock/docs/phase_requirement.md
  - src/spec_dock/assets/spec_dock/docs/phase_design.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md
intended_targets:
  - spec-dock/active/issue/design.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00271 Initiative テンプレート再設計 正規設計ドラフト

この artifact は `system-architect` による delegated design draft である。Canonical `design.md` への採用可否、採用範囲、表現の再記述、`report.md` Evidence Adoption Ledger への記録、fresh `spec-reviewer` gate は main orchestrator が行う。この artifact は evidence-only であり、正本、実装許可、phase promotion、reviewer pass を主張しない。

## 1. Requirement Coverage

| 要件ID | 設計対応 | 採用候補 |
|---|---|---|
| `I271-AC-001` | Initiative `requirement.md` template に、戦略目的、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff を入力する節を追加する。 | 採用推奨 |
| `I271-AC-002` | Initiative `design.md` template に、system context、scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary を表現する節を置く。 | 採用推奨 |
| `I271-AC-003` | Initiative `plan.md` template に、Epic decomposition、handoff readiness、fresh reviewer gate、report evidence、controlled re-slicing を扱う節を置く。 | 採用推奨 |
| `I271-AC-004` | 3 templates すべてで Issue-level implementation detail、TDD cycle、private code design を必須欄にしない。 | 採用推奨 |
| `I271-AC-005` | DDD / EDA は標準前提にせず、既存 architecture が明確な場合だけ補助語彙として使える guidance にする。 | 採用推奨 |
| `I271-AC-006` | 見出しと説明本文は日本語ファーストにし、file path、command、code identifier、SpecDock fixed term、外部固有名詞は原文保持を許可する。 | 採用推奨 |
| `I271-AC-007` | `authoring/scope-layering.md` への final link は `iss-00273` が担当するため、本 Issue では「後続で薄くリンクする置き場」と壊れない文言だけを用意する。 | 部分採用推奨 |

設計上の中心は、Initiative template を「実装 detail を書く空欄」から「下流 Epic へ渡す strategic envelope を固定する空欄」へ変えることである。

## 2. Existing Context Findings

- Active context は `iss-00271` を指しており、dependency view では `iss-00271` が ready、`iss-00272` 以降はこの Issue を blocker とする relay chain になっている。
- Issue requirement は、canonical `design.md` / `plan.md` を直接編集せず、pre-start seed を Issue-local `draft-design` / `draft-plan` artifact として扱う boundary を明記している。
- 既存 pre-start seed は方向性として妥当だが、正規 design に必要な source-of-record、リンク導線、non-target、verification、risk、adoption ledger note が薄い。
- 現行 Initiative templates は日本語ファーストの基本形を持つ一方、`artifacts/` adoption、fresh reviewer gate、Epic handoff、scope-layering link readiness が十分に誘導されていない。
- `workflow_initiative.md` は `draft-requirement` / `draft-design` / `draft-plan` を Issue-only artifact として扱うため、Initiative template 側では artifact authority を誤認させない説明が必要である。
- `phase_design.md` は delegated draft を evidence-only とし、canonical docs / report は main orchestrator single-writer authority とする。この artifact もその境界内にある。

## 3. Design Decisions

- `D271-001` Initiative requirement template は、目的、背景、成功指標、scope だけでなく、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff seed を持つ。
- `D271-002` Initiative design template は、system context、scope boundary、decision authority、artifact adoption flow、reviewer gate、Epic boundary を一貫した guardrail として表現する。
- `D271-003` Initiative plan template は、Epic portfolio を単なる一覧ではなく、handoff readiness、dependency、fresh reviewer gate、report evidence、controlled re-slicing の管理面として扱う。
- `D271-004` Template には Issue-level TDD cycle、private class / file design、implementation sequencing を必須欄として入れない。
- `D271-005` DDD / EDA は「必要時の補助語彙」に留める。必須見出しや必須 smoke expectation として固定しない。
- `D271-006` `authoring/scope-layering.md` が未作成の時点では dangling link を置かない。代わりに `scope-layering reference: follow-up by iss-00273` 相当の接続点を置く。
- `D271-007` 日本語ファースト guidance は、翻訳強制ではなく説明本文の既定言語を日本語にするルールとして書く。

## 4. Alternatives Considered

| 代替案 | 判断 | 理由 |
|---|---|---|
| 現行 templates へ最小の見出し追加だけ行う | 不採用 | `artifact adoption`、`reviewer gate`、`Epic handoff` が別々の断片になり、AC-001..003 の trace が弱くなる。 |
| scope-layering の責務表を Initiative templates に全文埋め込む | 不採用 | `epic-00270` の D-001 に反し、後続 docs / skills と drift しやすい。 |
| `authoring/scope-layering.md` へのリンクを今すぐ追加する | 不採用 | `I271-EC-001` により、未作成 target への壊れた相対リンクは禁止されている。 |
| DDD / EDA 中心の Initiative design template にする | 不採用 | `I271-AC-005` と architecture-neutral template policy に反する。 |
| Issue execution / TDD 手順まで Initiative plan template に入れる | 不採用 | Initiative plan の scope ownership は roadmap / milestone / Epic portfolio であり、Issue plan の責務を奪う。 |

## 5. Boundary / Contract Model

```text
Initiative requirement
  owns: why, strategic purpose, capability landscape, source-of-truth, success metric
  hands off: Epic candidates, constraints, stakeholder / trigger context

Initiative design
  owns: system context, scope boundary, decision authority, artifact adoption, reviewer gate
  hands off: Epic guardrails, architecture-neutral vocabulary, non-goals

Initiative plan
  owns: Epic decomposition, roadmap, dependencies, readiness gates, report evidence
  hands off: Epic start criteria and controlled re-slicing rules
```

Template contract:
- templates are starting scaffolds, not exhaustive policy documents.
- high-detail responsibility model is linked later by `iss-00273`, not copied into each template.
- `artifacts/` are evidence surfaces. Canonical authority requires adoption into canonical docs, accepted ADR, or `report.md` ledger plus reviewer gate.
- Initiative templates must leave Issue-level implementation, TDD, private design, and test-command detail to Epic / Issue scopes.

## 6. Dependency Analysis

- `iss-00271` has no issue blocker and must complete before `iss-00272`.
- `iss-00272` depends on shared vocabulary and Japanese-first guidance established here; therefore terms such as `capability landscape`, `handoff readiness`, `artifact adoption`, `reviewer gate`, and `scope boundary` should be stable enough for Epic templates.
- `iss-00273` owns final creation and linking of `docs/authoring/scope-layering.md`; this Issue only prepares non-broken link placement.
- `iss-00275` will verify template shape and smoke scenarios, so design must make verification points explicit and machine-checkable where practical.
- Existing `workflow_initiative.md`, `phase_requirement.md`, `phase_design.md`, `phase_plan.md`, and `phase_plan_initiative.md` remain authority for workflow semantics; templates should not fork their rules.

## 7. Source of Record

Priority for adoption:
1. Accepted ADRs referenced by `epic-00270`, especially architecture-neutral template authoring, scope-layering reference publication, complete understanding, Japanese-first authoring, and unified draft artifact command policy.
2. `spec-dock/active/epic/requirement.md`, `design.md`, `plan.md`, and `report.md` for parent scope decisions and current reviewer-gated planning state.
3. `spec-dock/active/issue/requirement.md` for `I271-AC-001..007`, exception conditions, non-scope, and relay handoff.
4. Current provider templates under `src/spec_dock/assets/spec_dock/templates/initiative/`.
5. Workflow and phase docs under `src/spec_dock/assets/spec_dock/docs/`.
6. Pre-start draft artifact as advisory seed only.

This artifact itself is not source of record until main orchestrator adopts parts of it into canonical `design.md` and records that decision.

## 8. Data Flow / Domain Model / Interface Contract

No runtime data model change is proposed by this draft. The relevant interface is the scaffolded Markdown template contract.

```text
source-grounded evidence / artifacts
  -> Initiative requirement template prompts
  -> Initiative design template guardrails
  -> Initiative plan template Epic portfolio and readiness gates
  -> Epic requirement/design/plan authoring
  -> downstream Issue handoff package
```

Interface expectations for templates:
- `requirement.md` exposes strategic inputs: purpose, capability landscape, source-of-truth, stakeholders, triggers, metrics, scope, non-scope, Epic handoff seed.
- `design.md` exposes guardrail inputs: system context, scope ownership, decision authority, artifact adoption, reviewer gate, Epic boundary, observability, risks.
- `plan.md` exposes execution-management inputs: Epic portfolio, sequencing, dependencies, handoff readiness, report evidence, reviewer gates, controlled re-slicing.
- All three templates must be readable as Japanese-first documents without translating identifiers, commands, and fixed terms.

## 9. File / Module Change Plan

This draft recommends the following future implementation surface. This artifact does not edit these files.

```text
src/spec_dock/assets/spec_dock/templates/initiative/
|-- requirement.md  # Modify: strategic purpose, capability landscape, SoT, stakeholder/trigger, Epic handoff prompts
|-- design.md       # Modify: system context, scope boundary, decision authority, artifact adoption, reviewer gate, Epic boundary prompts
`-- plan.md         # Modify: Epic decomposition, handoff readiness, report evidence, fresh reviewer gate, controlled re-slicing prompts

tests/
`-- ...             # Modify/Add if existing scaffold/template assertions require update; exact path to be selected by implementation inspection

spec-dock/
`-- ...             # Read/validate only unless dogfooding refresh is explicitly part of implementation plan
```

Non-targets:
- canonical `spec-dock/active/issue/design.md` and `plan.md` during this delegated draft run.
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` creation; owned by `iss-00273`.
- Issue grade templates and profile templates, except compatibility updates if implementation discovers a direct break.
- Runtime dependency algorithm, GitHub mutation, PR creation, merge, issue close.
- Actor-specific or specialist-specific draft artifact commands.

## 10. Migration / Compatibility / Rollback

- Migration: No persisted data migration is expected. This is provider-side scaffold/template content.
- Existing repos: Managed repos receiving `spec-dock update` will receive improved Initiative templates; they should not be forced into DDD / EDA terminology.
- Dogfooding: After implementation, inspect or validate local `spec-dock/` impact, but do not treat dogfooding generated files as implementation source of truth.
- Compatibility: Existing Issue grade / TDD planning behavior remains downstream authority.
- Rollback: If template changes fail review or tests, revert the provider template diff for this Issue. Do not roll back to raw artifact authority wording, DDD / EDA mandatory templates, or dangling scope-layering links.

## 11. Observability

Recommended report evidence after main orchestrator adoption:
- Evidence Adoption Ledger entry for this artifact: adopted / partially_adopted / rejected / deferred, with adopted sections listed.
- Spec Authoring Gate entry for canonical design adoption and fresh `spec-reviewer` result.
- Template diff summary showing AC-001..007 mapping.
- Verification command outputs or explicit skip reasons.
- Link-readiness note stating that final `authoring/scope-layering.md` link insertion remains with `iss-00273`.

## 12. Test Strategy

Minimum verification candidates for implementation:
- Template snapshot or focused assertions that Initiative requirement template includes strategic purpose, capability landscape, source-of-truth, stakeholder / trigger, and Epic handoff prompts.
- Focused assertions that Initiative design template includes system context, scope boundary, decision authority, artifact adoption, reviewer gate, and Epic boundary prompts.
- Focused assertions that Initiative plan template includes Epic decomposition, handoff readiness, fresh reviewer gate, report evidence, and controlled re-slicing prompts.
- Grep or test assertions that Initiative templates do not require Issue-level TDD cycle, private class / file design, or mandatory DDD / EDA sections.
- Japanese-first read-through: explanation text is Japanese-first, while paths, commands, code identifiers, SpecDock fixed terms, and external proper nouns may remain original.
- Link check: no broken `authoring/scope-layering.md` relative link is introduced before `iss-00273`.
- Existing project checks selected by implementation plan, likely a focused unit/scaffold test lane plus `./spec-dock/scripts/spec-dock validate`.

## 13. ADR Candidates

No new ADR is required from this Issue if implementation stays within the parent Epic decisions.

ADR candidate only if implementation discovers one of these:
- Initiative templates require a new global authoring policy beyond architecture-neutral / Japanese-first / scope-layering reference decisions.
- `artifacts/` authority flow must change for Initiative scope, rather than merely be described.
- `authoring/scope-layering.md` ownership or publication surface differs from accepted ADR expectations.

## 14. Risks

- R-271-001: Templates become too large and duplicate workflow docs. Mitigation: keep high-detail policy in docs and use thin prompts in templates.
- R-271-002: Artifact adoption wording implies raw artifacts are canonical. Mitigation: explicitly state evidence-only and report-ledger adoption flow.
- R-271-003: Dangling link to `authoring/scope-layering.md`. Mitigation: prepare wording/slot only; final link in `iss-00273`.
- R-271-004: DDD / EDA language becomes mandatory by example. Mitigation: phrase as optional adaptation when existing architecture uses those terms.
- R-271-005: Japanese-first guidance over-translates technical identifiers. Mitigation: preserve paths, commands, code identifiers, SpecDock fixed terms, and external proper nouns.
- R-271-006: Implementation touches dogfooding `spec-dock/` as source of truth. Mitigation: edit provider templates first; dogfooding is validation / refresh surface.

## 15. Requirement Clarification Requests

None.

Current requirements and parent Epic decisions are sufficient for design drafting. The only adoption-time judgment is whether main orchestrator wants canonical `design.md` to use this artifact as primary structure or only as a checklist against the existing pre-start seed.

## 16. Integration Notes for Main Orchestrator

- Suggested source requirement revision: active `iss-00271` requirement, `最終更新: "2026-07-02"`, plus current `epic-00270` Goodall-reviewed planning correction evidence in `epic/report.md`.
- Use this artifact as a structured replacement or supplement for the pre-start seed. The pre-start seed remains valuable for the concise target-file and AC mapping.
- Before canonical adoption, record this artifact in `report.md` EAL with `adoption_status` chosen by main orchestrator.
- If canonical `design.md` is composed from Issue profile template, adopt the decisions above into its local design sections rather than copying this artifact wholesale.
- Keep `iss-00273` responsible for actual `authoring/scope-layering.md` creation and final thin-link insertion.

## Ledger Note

Adopt into canonical design:
- AC-001..007 traceability table.
- `D271-001` through `D271-007` design decisions.
- Non-target list, especially canonical-doc mutation boundary for this delegated run, scope-layering final-link deferral, and no Issue-level TDD/private design in Initiative templates.
- Verification strategy covering template shape, prohibited mandatory details, Japanese-first guidance, and no dangling link.
- Risk list and mitigation notes.

Do not adopt into canonical design:
- Any statement that this artifact itself is accepted authority.
- The temporary command-output anomaly where `new artifact` stdout included `spec-dock/spec-dock/...`; canonical design only needs the actual artifact path if referenced.
- Full source path inventory from this artifact frontmatter, unless useful for report provenance.
- Implementation ordering detail beyond the file/module change surface; concrete TDD cycles belong in canonical `plan.md`.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
