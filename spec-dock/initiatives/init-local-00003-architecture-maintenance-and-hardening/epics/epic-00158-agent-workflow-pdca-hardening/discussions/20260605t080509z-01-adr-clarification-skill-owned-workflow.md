---
種別: ADR（Architecture Decision Record）
ID: "20260605t080509z-01-adr"
タイトル: "Clarification Skill Owned Workflow"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
authority: "accepted"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t052200z-research-chatgpt-clarification-grill-alignment-task-package.md"
  - "spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md"
  - "user correction 2026-06-05: spec-dock-clarification workflow should be skill-owned"
reflected_to:
  - "20260605t080509z-02-adr"
---

# 20260605t080509z-01-adr Clarification Skill Owned Workflow

## 位置づけ

This ADR fixes the special ownership rule for `spec-dock-clarification`.

## ADR 化基準

- hard to reverse:
  - yes. This changes the authority boundary for a shipped skill and its surrounding docs.
- surprising without context:
  - yes. It intentionally treats clarification differently from most SpecDock workflows.
- real tradeoff:
  - yes. Skill-owned workflow improves first-read execution but reduces the value of a standalone workflow doc.
- ADR 化しない場合の反映先:
  - `disc` and follow-up issue specs.
- ADR として残す理由:
  - Clarification is a durable exception to the general skill/docs split and affects future docs/templates edits.

## 結論（Decision）

Accepted.

`spec-dock-clarification` owns its own workflow in the skill. Unlike broader lifecycle workflows, clarification does not need a separate full workflow document as the primary authority.

The skill should contain:

- the source-grounded grill workflow,
- the files/artifacts it may create,
- when to create `research`, `interview`, `disc`, and `adr`,
- how to ask one essential pressure-test question,
- how to capture the answer and route it back to existing SpecDock artifacts,
- how specialist agents return question candidates to the orchestrator.

The skill should read existing SpecDock docs/templates to understand the files it is helping create, such as requirement/design/plan/report/discussion templates and scope rules. It should not depend on a separate `workflow_clarification.md` to learn its own workflow.

`workflow_clarification.md`, if retained, should become a thin bridge or reference page, not the workflow authority. It may point users to the skill and to existing artifact docs/templates. It must not be the place where the mandatory clarification runbook is hidden.

## 背景（Context）

The previous analysis treated `spec-dock-clarification` like other skills: skill contains a compact runbook, docs contain detailed workflow. The user corrected this: `spec-dock-clarification` is primarily a skill for supporting creation of existing SpecDock files. Its workflow is the skill's own knowledge, not an independent product workflow that must be split into a separate doc.

This skill is also the SpecDock integration surface for a `Grill with me` / `Grill with dog` style interaction: read sources, form a provisional understanding, ask one high-impact question, and route the answer into artifacts.

## 選択肢（Options considered）

### Option A: Keep `workflow_clarification.md` as primary source of truth

- Pros:
  - Matches the current pattern.
  - Keeps the skill short.
- Cons:
  - Recreates the original failure mode: the model may not open the doc.
  - Hides the grill loop behind a reference.
  - Makes the skill too bland for its main purpose.
- Decision:
  - Rejected for `spec-dock-clarification`.

### Option B: Make `spec-dock-clarification` a skill-owned workflow

- Pros:
  - The model sees the clarification loop immediately.
  - Better matches the skill's purpose as a file-creation support workflow.
  - Removes the need for a separate workflow authority.
- Cons:
  - The skill becomes longer than a thin router.
  - Existing docs that link to `workflow_clarification.md` need careful bridge wording.
- Decision:
  - Accepted.

### Option C: Retire all clarification docs immediately

- Pros:
  - Simplifies the authority model.
- Cons:
  - Many existing docs link to `workflow_clarification.md`.
  - Immediate removal risks breaking documentation navigation.
- Decision:
  - Rejected for first wave. Use thin bridge or staged retirement.

## 判断理由（Rationale）

Clarification is not a standalone lifecycle with a broad policy document. It is an agent interaction skill that helps produce existing SpecDock files. The model must know the interaction loop before it can decide which docs/templates to inspect.

Therefore the workflow should be in `SKILL.md`, while referenced docs/templates describe the artifacts being created or updated.

## 影響（Consequences）

Positive:

- `spec-dock-clarification` becomes first-read executable.
- The source-grounded grill loop is not hidden behind a linked workflow doc.
- `interview`, `research`, and `disc` creation becomes clearer.
- The skill can support analysis-only, draft-only, and canonical authoring handoffs without forcing canonical docs.

Negative / debt:

- `workflow_clarification.md` must be rewritten as bridge/reference or later retired.
- Docs that currently describe `workflow_clarification.md` as source of truth must be updated.
- The skill must avoid becoming generic coaching detached from SpecDock artifacts.

Impact scope:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
- Docs that link to `workflow_clarification.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`

Migration / rollback:

- First wave should rewrite the skill and convert `workflow_clarification.md` to a thin bridge.
- Full retirement of `workflow_clarification.md` can be a later issue if links are cleaned safely.
- Rollback is to restore doc-owned workflow and shrink the skill, but that would reintroduce the first-read risk.

## 参考（References）

- Related discussions:
  - `spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md`
  - `spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md`
- Related ADR:
  - `20260605t080509z-adr`
  - `20260605t080509z-02-adr`
