---
種別: research
ID: "20260702t022727z-research"
タイトル: "Deep Consultant Scope Layering Publication Recommendation"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t021107z-interview"
  - "20260702t020503z-01-disc"
authority: "synthesized"
derived_from:
  - "fresh ChatGPT GPT-5.5 Pro Extended consultant via chatgpt-use"
  - "artifacts/20260702t021107z-interview-phase3-scope-layering-publication-surface.md"
  - "artifacts/20260702t020503z-01-disc-phase3-scope-authority-model.md"
reflected_to: []
---

# 20260702t022727z-research Deep Consultant Scope Layering Publication Recommendation

## 調査目的

Fresh deep-consultant に、scope-layering / Initiative-Epic-Issue responsibility model の公開面について、ファイル増殖リスクと情報分散リスクの両方を踏まえたベストプラクティスを依頼した。

## sources / 調査方法

- Tool: `chatgpt-use` wrapper (`oracle-chatgpt`) with GPT-5.5 Pro Extended.
- Attached local context:
  - `Phase 3 Scope Authority Model`
  - `Phase 3 Reference Adoption Map`
  - `Phase 3 Scope Layering Publication Surface`
  - `Phase 3 Repo Context And Implementation Survey`
  - provider-side workflow docs
  - phase plan docs
  - `authoring/decision-routing.md`
  - initiative/epic/epic-execution planning skills
- Consultant prompt explicitly asked:
  - whether to add `docs/authoring/scope-layering.md`, embed into existing docs, use ADR, or hybrid;
  - how to avoid both file proliferation and scattered duplicated rules;
  - which surface should own canonical rule and which docs should summarize/link it;
  - what tests/smoke checks should protect it.

## facts / 観測できた事実

- Consultant recommended a constrained Option A:
  - create exactly one new provider-side reusable reference:
    - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - make it the canonical reusable rule for Initiative / Epic / Issue / Issue Plan / Report responsibility model.
  - keep it narrow: deciding which scope owns a requirement, design decision, plan obligation, evidence, report finding, or ADR candidate.
- Existing docs should not duplicate the full table. They should add thin links:
  - `authoring/decision-routing.md`
  - `workflow_initiative.md`
  - `workflow_epic.md`
  - `workflow_issue.md`
  - `phase_plan_initiative.md`
  - `phase_plan_epic.md`
  - `phase_plan_issue.md`
  - planning skills
- Templates should remain thin. At most they should include short prompts/links, not reusable tutorials.
- ADR should not be primary publication surface. ADR is fallback only if the rule becomes a global architecture commitment beyond authoring guidance.

## inference / 推測

- This recommendation is not "create more files"; it is "create one hub to prevent many files and drift".
- The proposed new file clears the bar because:
  - the model is reusable across Initiative/Epic/Issue/Plan/Report;
  - it is a lookup/routing table, not lifecycle prose;
  - existing workflow docs contain partial responsibility text but not a single first-read overview.
- `decision-routing.md` remains the examples/patterns guide, not the owner of the scope ownership model.

## recommended publication model

### Owner

- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - Purpose / first-read use case.
  - Scope ownership table.
  - Canonical authority flow.
  - Decision-radius rule.
  - Anti-rules.
  - Links outward to decision routing, workflow docs, phase docs, and ADR workflow.

### Thin link surfaces

- `authoring/decision-routing.md`
  - Add "for canonical responsibility model, see scope-layering.md".
- `workflow_initiative.md`
  - Link near Decision routing / 記述 section.
- `workflow_epic.md`
  - Link near Decision routing / Issue slicing / 記述 section.
- `workflow_issue.md`
  - Link in spec-authoring / parent-boundary section.
- `phase_plan_*`
  - Add see-also links or one-sentence guard only.
- Planning skills
  - Add first-read pointer; keep skills operational and short.

### Epic-local reflection

- `epic-00270/design.md`
  - Adopt the provider reference as the publication surface and summarize why.
- `epic-00270/plan.md`
  - Use it to justify Issue slicing, no decision-only Issues, and Issue 03/05 scopes.
- `epic-00270/report.md`
  - Record adoption of V3 intake, synthesized artifacts, user answer, and consultant recommendation.

## suggested smoke checks

- Provider doc presence:
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` exists.
  - contains headings like `Scope ownership`, `Decision radius`, `Authority flow`, `Anti-rules`.
- No duplicate full table drift:
  - full Initiative/Epic/Issue/Issue Plan/Report responsibility table appears only in `scope-layering.md`.
- Required inbound links:
  - workflow docs, decision-routing, and planning skills link to `scope-layering.md`.
- No artifact authority leak:
  - shipped provider docs do not cite scope-local `epic-00270/artifacts/...` as canonical authority.
- Template thinness:
  - templates do not embed full routing examples or full scope table.
- Reviewer/smoke guidance:
  - detect Issue plans creating parent requirements/design decisions;
  - detect decision-only Issues treated as execution-ready;
  - detect raw artifacts treated as canonical authority.

## failure modes

- New reference becomes a second workflow manual.
  - Mitigation: keep it limited to scope ownership/routing, link lifecycle rules outward.
- Workflow docs drift from the reference.
  - Mitigation: inbound-link checks and single-full-table-owner check.
- Skills do not point to the page, so agents miss it.
  - Mitigation: add one first-read pointer to planning skills.
- ADR is skipped when a rule becomes architecture-wide.
  - Mitigation: include ADR escalation rule in the reference.
- Artifacts accidentally become canonical.
  - Mitigation: provider docs cite canonical reference, while report ledger records artifact adoption.

## verification proposal

1. Confirm `epic-00270/design.md` adopts provider reference and does not paste the V3 pack.
2. Confirm `epic-00270/plan.md` maps Issue 03 to docs/skills updates and Issue 05 to smoke/template validation.
3. Confirm `epic-00270/report.md` records user answer and artifact adoption.
4. Add focused smoke checks for link coverage, no duplicated full table, no local artifact authority, and template thinness.
5. Run `./spec-dock/scripts/spec-dock validate` and sync-related checks after implementation.

## adoption target

- `design.md`:
  - Adopt constrained Option A as the publication model.
- `plan.md`:
  - Assign provider doc creation/linking to docs/skills Issue and smoke checks to validation Issue.
- `report.md`:
  - Record this consultant recommendation as advisory evidence.

## uncertainty

- Consultant did not inspect live repo beyond attached files.
- Exact test file names were not verified.
- Recommendation is advisory and must be checked against repository facts before implementation.
