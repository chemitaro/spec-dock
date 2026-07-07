---
種別: 実装計画書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
Issue Grade: "standard"
状態: "draft | approved | in-progress | completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
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
