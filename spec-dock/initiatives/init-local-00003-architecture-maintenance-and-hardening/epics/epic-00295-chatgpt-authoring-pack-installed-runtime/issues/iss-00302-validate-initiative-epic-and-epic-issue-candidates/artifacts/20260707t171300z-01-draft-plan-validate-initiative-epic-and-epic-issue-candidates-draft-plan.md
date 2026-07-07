---
種別: 実装計画書（Issue）
ID: "iss-00302"
タイトル: "Initiative Epic Validation"
Issue Grade: "standard"
状態: "draft | approved | in-progress | completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C07 Initiative/Epic と Epic/Issue 候補 validators を実装する — draft plan

## Step sequence

1. candidate schema と required draft file mapping を定義する。
2. Initiative -> Epic validator を実装する。
3. Epic -> Issue validator を実装する。
4. duplicate/overlap と dependency diagnostics を追加する。
5. profile advisory-only / forbidden authority claim check を追加する。
6. fixtures と report snapshot tests を追加する。

## Dependencies

- 06-promote-zip-review-and-staging

## Verification

- Initiative -> Epic positive fixture
- Epic -> Issue positive fixture
- duplicate/overlap negative fixture
- parent trace missing fixture
- profile authority negative fixture

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
