---
種別: ADR（Architecture Decision Record）
ID: "20260605t080509z-02-adr"
タイトル: "First Wave Issue Decomposition"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
authority: "accepted"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md"
  - "spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md"
  - "20260605t080509z-adr"
  - "20260605t080509z-01-adr"
reflected_to:
  - "iss-00159"
---

# 20260605t080509z-02-adr First Wave Issue Decomposition

## 位置づけ

This ADR fixes the first-wave issue decomposition for `epic-00158`.

## ADR 化基準

- hard to reverse:
  - yes. Issue decomposition determines the implementation order and review boundaries for shipped assets.
- surprising without context:
  - yes. Regression checks are intentionally deferred even though they were previously proposed early.
- real tradeoff:
  - yes. A broad cleanup issue can become too large, while small isolated issues can fail to fix the cross-surface problem.
- ADR 化しない場合の反映先:
  - `disc`, issue specs, or epic plan.
- ADR として残す理由:
  - The decomposition encodes durable sequencing and scoping decisions for multiple issues.

## 結論（Decision）

Accepted.

The first wave will prioritize context-surface cleanup across skills/docs/templates. It will not start with runtime gates, automated regression checks, or harness work.

The first-wave issue set should be:

1. `Make Issue Planning Skill Expose Mandatory Authoring Gates`
   - Existing issue: `iss-00159`.
   - Scope:
     - Make `spec-dock-issue-planning` first-read executable.
     - Put mandatory requirement/design/plan authoring gates in the skill.
     - Keep detailed field semantics in docs/templates.
   - Non-scope:
     - Hub rewrite.
     - Clarification rewrite.
     - Runtime gates.
     - Regression harness.
   - Purpose:
     - First concrete specimen for the skill spine pattern.

2. `Align Skill Docs Template Context Surfaces`
   - Scope:
     - Cross-cutting inventory and cleanup of provider-side skills/docs/templates.
     - Ensure every surface reflects the same ownership model from `20260605t080509z-adr`.
     - Identify contradictions and stale doc ownership claims.
   - Non-scope:
     - Runtime enforcement.
     - Automated checks first.
     - Full template compliance authority.
   - Purpose:
     - Make "どこを読んでも正しい住み分けが見える" true.

3. `Revise spec-dock-clarification as skill-owned grill workflow`
   - Scope:
     - Implement `20260605t080509z-01-adr`.
     - Rewrite `spec-dock-clarification/SKILL.md` so the workflow is skill-owned.
     - Convert `workflow_clarification.md` to a thin bridge/reference, or prepare staged retirement.
     - Align `interview`, `research`, and `disc` templates to support the same source-grounded grill loop.
   - Non-scope:
     - Exact copy of Matt Pocock's original skill.
     - Generic coaching skill.
     - Runtime gates.
     - Full retirement of all clarification docs unless link cleanup is included.
   - Purpose:
     - Treat clarification as the SpecDock integration of a source-grounded grill interaction.

4. `Clarify Hub And Leaf Skill Routing Surface`
   - Scope:
     - Update `spec-driven-tdd-workflow` as router plus global invariant layer.
     - Route clarification to the skill-owned clarification workflow.
     - Route issue planning/execution to leaf skills with first-read workflow spines.
   - Non-scope:
     - Detailed leaf skill rewrites.
   - Purpose:
     - Prevent the hub from saying or implying that mandatory workflow lives mainly in docs.

5. `Align Workflow Docs With Skill Spine Boundary`
   - Scope:
     - Update docs that currently present agent operational workflow as doc-owned.
     - Keep docs as meaning/details/source-of-truth for fields, policies, and hard cases.
     - Update links from `workflow_clarification.md` according to `20260605t080509z-01-adr`.
   - Non-scope:
     - Rewriting every docs page for style.
     - Changing lifecycle policy without a new ADR.
   - Purpose:
     - Remove contradictions after skills are made first-read executable.

6. `Align Templates As Scaffolds And Examples`
   - Scope:
     - Adjust templates to show evidence slots and good examples for the new skill-owned workflows.
     - Ensure `interview`, `research`, and `disc` support clarification's grill loop.
     - Ensure issue report/evidence slots support adoption decisions.
   - Non-scope:
     - Treating templates as compliance authorities.
   - Purpose:
     - Make templates teach behavior without replacing docs or skills.

Deferred:

- `Add Skill Spine Regression Checks`
  - Defer until cleaned surfaces exist.
  - Later role: drift detection and lightweight guard.
- `Add Manual Workflow Scenario Harness`
  - Defer until skill/docs/templates behavior is stable enough to evaluate.
- Runtime gate / `gate status` / issue start-finish guards
  - Defer until the agent-facing contract is cleaner.

## 背景（Context）

Earlier ChatGPT decomposition proposed adding skill spine regression checks soon after `iss-00159`. The user corrected the direction: the problem is not mainly missing rules, but thin/dispersed/weak context. The first fix must make all skill/docs/templates surfaces present the right boundary.

The user also corrected the treatment of `spec-dock-clarification`: it should be skill-owned, not a doc-owned workflow with a thin skill wrapper.

## 選択肢（Options considered）

### Option A: Start with regression checks

- Pros:
  - Gives measurable guardrails early.
- Cons:
  - Checks would lock in surfaces before they are cleaned.
  - Does not solve the main context visibility problem.
- Decision:
  - Rejected for first wave.

### Option B: One huge cleanup issue for all skills/docs/templates

- Pros:
  - Maximizes cross-surface consistency.
- Cons:
  - Too large to review and dogfood.
  - Hard to know which change improved behavior.
- Decision:
  - Rejected as a single implementation issue, but accepted as the organizing theme.

### Option C: Several focused issues under one first-wave cleanup theme

- Pros:
  - Keeps review boundaries clear.
  - Allows dogfooding after each slice.
  - Preserves cross-surface alignment through ADRs.
- Cons:
  - Requires discipline to avoid local-only fixes.
- Decision:
  - Accepted.

## 判断理由（Rationale）

The first wave must be concrete enough to implement and review, but broad enough to fix the actual cross-surface failure. Splitting by concern lets each issue have a clear target while the ADRs preserve a shared design.

The decomposition also prevents `spec-dock-clarification` from being treated as a low-priority wording fix. It is a distinct concern with its own authority decision.

## 影響（Consequences）

Positive:

- Follow-up issues will have clearer scope.
- `iss-00159` remains useful without becoming the entire cleanup.
- `spec-dock-clarification` gets an explicit issue-level lane.
- Regression checks are still preserved as later PDCA work.

Negative / debt:

- The first wave contains several issues before automated guards.
- Cross-issue consistency must be maintained manually until checks are added.
- Some docs may temporarily be bridge pages while links are migrated.

Impact scope:

- Provider-side installed skills.
- Provider-side docs/templates.
- Dogfooding mirror verification.
- Epic issue sequencing.

Migration / rollback:

- If a focused issue proves too small, merge it into `Align Skill Docs Template Context Surfaces`.
- If a cleanup issue becomes too broad, split by skill family or artifact family.
- Do not move regression checks earlier unless cleaned surfaces already define stable expected text/structure.

## 参考（References）

- Related ADRs:
  - `20260605t080509z-adr`
  - `20260605t080509z-01-adr`
- Related discussions:
  - `spec-dock/active/epic/discussions/20260605t050100z-disc-issue-decomposition-synthesis.md`
  - `spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md`
- Related issue:
  - `iss-00159`
