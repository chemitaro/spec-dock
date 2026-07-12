---
種別: "Issue draft plan"
ID: "epic-00295-10"
Issue候補: "C10"
タイトル: "approval check と stop-gate evidence reports を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C10 approval check と stop-gate evidence reports を実装する — draft plan

## Step sequence

1. approval evidence schema を定義する。
2. candidate pack digest と scope matching を実装する。
3. missing/stale/scope mismatch diagnostics を実装する。
4. unsupported auto-creation message を help / diagnostics と整合させる。
5. fixtures と report snapshots を追加する。

## Dependencies

- 07-validate-initiative-epic-and-epic-issue-candidates

## Verification

- approval pass fixture
- missing approval blocked fixture
- stale candidate digest fixture
- scope mismatch fixture
- unsupported auto-creation diagnostics test

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
