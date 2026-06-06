---
種別: ADR（Architecture Decision Record）
ID: "20260605t080509z-adr"
タイトル: "Skill Docs Template Context Surface Ownership"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
authority: "accepted"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t043350z-disc-agent-workflow-pdca-analysis-summary.md"
  - "spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md"
  - "user correction 2026-06-05: context surface is thin/dispersed/weak; regression checks are not first"
reflected_to:
  - "20260605t080509z-02-adr"
---

# 20260605t080509z-adr Skill Docs Template Context Surface Ownership

## 位置づけ

この ADR は、agent が読む `skill` / `docs` / `templates` の責務分担を固定する。

## ADR 化基準

- hard to reverse:
  - yes. Shipped assets across skills/docs/templates influence all future installed SpecDock workspaces.
- surprising without context:
  - yes. Conventional documentation practice would put workflows in docs, but this epic found that model-facing workflow must often be present in the skill first-read surface.
- real tradeoff:
  - yes. Putting more in skills improves adherence but risks skill bloat and drift from docs/templates.
- ADR 化しない場合の反映先:
  - `disc` and later issue specs.
- ADR として残す理由:
  - This is a durable context-surface ownership rule for multiple future issues, not a one-off wording edit.

## 結論（Decision）

Accepted.

For SpecDock agent-facing assets, use this default ownership model:

- Skills own the operational workflow spine that the model must follow during the task.
- Docs own concepts, field meanings, policy details, references, and hard-case decision criteria.
- Templates own scaffolds, evidence slots, and good examples. Templates are not compliance authorities.

The immediate improvement wave must clean the context surfaces themselves, not start with regression checks or runtime gates. `Add Skill Spine Regression Checks` is deferred until the skill/docs/templates surfaces have been cleaned and dogfooded.

## 背景（Context）

The observed failure mode is not primarily a lack of rules. The more important problem is that models first see thin skills, while mandatory workflow is buried in multiple docs. If the model does not open the right docs, it does not know the workflow.

The user corrected the prior issue decomposition: the most effective first fix is to clean every relevant skill/docs/templates surface so the same ownership boundary is visible everywhere.

## 選択肢（Options considered）

### Option A: Keep skills thin and put workflows in docs

- Pros:
  - Reduces skill length.
  - Keeps long explanations in one place.
- Cons:
  - Fails when the model does not open the referenced docs.
  - Mandatory workflow becomes hidden behind links.
  - Agent behavior depends on optional context retrieval.
- Decision:
  - Rejected as the default for mandatory operational workflow.

### Option B: Copy full docs into skills

- Pros:
  - The model sees most information immediately.
- Cons:
  - Creates skill bloat.
  - Increases source-of-truth drift.
  - Makes docs/templates harder to trust.
- Decision:
  - Rejected.

### Option C: Put compact workflow spine in skills and keep details in docs/templates

- Pros:
  - Model sees the mandatory task sequence on first read.
  - Docs remain the detailed source of truth.
  - Templates teach examples without becoming authorities.
- Cons:
  - Requires careful cross-surface editing.
  - Needs later drift checks after cleanup.
- Decision:
  - Accepted.

## 判断理由（Rationale）

The first-read skill surface is the strongest lever for agent behavior. The skill must tell the model what to do next, when to stop, when to ask, and what evidence to leave. Docs should explain the meaning and detailed rules behind those actions. Templates should make the correct behavior easy to imitate.

This reduces the chance that workflow-critical behavior is missed because it was hidden in a linked document or distributed across multiple files.

## 影響（Consequences）

Positive:

- Skills become directly executable by the model.
- Docs are less likely to be overloaded with agent runbook obligations.
- Templates become better examples without becoming policy authorities.
- Future issue specs can inspect surfaces using the same boundary.

Negative / debt:

- Skills will grow somewhat.
- Cross-surface drift remains possible until later regression checks are added.
- Existing docs that say workflow is owned by docs may need bridge wording or removal.

Impact scope:

- Provider-side skills under `src/spec_dock/assets/install_root/.agents/skills/`.
- Provider-side docs under `src/spec_dock/assets/spec_dock/docs/`.
- Provider-side templates under `src/spec_dock/assets/spec_dock/templates/`.
- Dogfooding mirror is verification only.

Follow-ups:

- Create or update issues according to `20260605t080509z-02-adr`.
- Defer regression/harness work until after the cleanup pass.

## 参考（References）

- Related discussions:
  - `spec-dock/active/epic/discussions/20260605t043350z-disc-agent-workflow-pdca-analysis-summary.md`
  - `spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md`
- Related ADR:
  - `20260605t080509z-01-adr`
  - `20260605t080509z-02-adr`
