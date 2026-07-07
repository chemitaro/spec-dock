---
種別: "Issue draft plan"
ID: "epic-00295-03"
Issue候補: "C03"
タイトル: "block-first GitHub sync preflight を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C03 block-first GitHub sync preflight を実装する — draft plan

## Step sequence

1. preflight input/output schema を確定する。
2. local git observation と remote tracking comparison を実装する。
3. GitHub connector-visible ref / default branch observation slot を実装または adapter 化する。
4. source hash manifest と stale condition を記録する。
5. block/stale diagnostics と local-context provenance を実装する。
6. positive/negative fixtures を追加する。

## Dependencies

- 02-add-authoring-command-skeleton

## Verification

- positive exact remote match fixture
- dirty/staged/untracked negative fixtures
- ahead/behind/diverged negative fixtures
- branch missing / origin mismatch / connector failure fixtures
- default fallback requested/effective ref fixture
- local-context provenance fixture

## Finish evidence

- Completed scope summary.
- Files changed / docs changed inventory.
- Test and validation output summary.
- Known residual risks and deferred items.
- Evidence that forbidden authority claims were not introduced.
- Relay evidence: 中間 Issue のため PR delivery は行わない。finish 時に no-per-Issue-PR rationale、local verification、Issue 12 への dependency edge を記録する。

## Relay policy

中間 Issue のため PR delivery は行わない。finish 時に no-per-Issue-PR rationale、local verification、Issue 12 への dependency edge を記録する。

## PR delivery policy

No PR delivery in this intermediate Issue. PR delivery is deferred to Issue 12.
