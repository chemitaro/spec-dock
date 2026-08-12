---
種別: disc
ID: "20260812t134617z-disc"
タイトル: "PR Repair Unit PR363-U001 Skill Invocation Policy"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-12"
親: ["iss-00359"]
template: "disc"
authority: "evidence"
derived_from: []
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# 20260812t134617z-disc PR Repair Unit PR363-U001 Skill Invocation Policy

## Repair Contract

- `source_batch`: `report.md#11`
- `unit_id`: `PR363-U001`
- `root_cause_family`: `skill-invocation-policy`
- `covered_ids`: `PR363-P1-001`
- `source_links`: PR #363 review thread `PRRT_kwDOQ99OK86YlhKI`
- `failure_class`: `review_feedback:skill-invocation-policy`
- `decided_priority`: `P1`
- `merge_blocking`: `yes`
- `disposition`: `fix-now`

## Validity Analysis

Codexが認識するexplicit-only policyはskill front matterではなく`agents/openai.yaml`の`policy.allow_implicit_invocation: false`である。Current provider assetは未認識keyだけに依存するため、write-capable skillが暗黙選択され得る。指摘はvalid。

## Need-To-Fix Decision

I359-RQ-003の明示呼出し限定を実効化するため、このPRで修正する。

## Root Cause

authoring上のuser-invoked metadataとCurrent Codex hostが認識するinvocation policyを同一視した。

## Options Considered

1. `disable-model-invocation`だけを維持: host enforcementがなく棄却。
2. `agents/openai.yaml`をprovider / dogfoodへ追加: 最小かつrecognized contractとして採用。
3. skill自体を配布しない: Issue 359の目的を満たさないため棄却。

## Recommended Design

`spec-dock-grill-with-docs/agents/openai.yaml`をprovider authorityとdogfood projectionへbyte-identicalに追加する。SKILL front matterの未認識keyは削除し、明示呼出しの正本をpolicy metadataへ一本化する。

## Implementation Plan

1. metadata欠落でfailするstatic contract testを追加する。
2. provider / dogfood metadataを追加し、skill testをdirectory parityへ拡張する。
3. R/D/Pとreportのexplicit invocation記述をrecognized metadataへ更新する。

## Validation Plan

focused static test、provider / dogfood tree parity、全体lint / pytest、最終Spec review。

## Out of Scope

他skillのinvocation policy変更、global skill install、Codex設定一般の再設計。

## Implementation Result

Provider / dogfoodへbyte-identicalな`agents/openai.yaml`を追加し、未認識front matter keyを削除した。static contractはdirectory parityとexact policy valueを確認する。

## Validation Result

Issue 359 focused contract 20件、ordinary suite 1647件、lintがpassした。provider / dogfood skill treeもbyte-identicalである。包括的な最終品質ゲートはP0=0 / P1=0でpass。PR latest-head再観測はpending。

## Commit Evidence

pending

## Re-observation Result

pending

## Residual Risk / Follow-up

Current hostが将来metadata schemaを変更する場合は別Issueで追随する。本PRではCurrent recognized contractだけを固定する。
