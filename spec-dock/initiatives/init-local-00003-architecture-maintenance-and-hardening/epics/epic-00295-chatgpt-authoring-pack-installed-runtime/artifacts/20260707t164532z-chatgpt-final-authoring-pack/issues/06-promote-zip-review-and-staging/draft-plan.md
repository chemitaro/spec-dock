---
種別: "Issue draft plan"
ID: "epic-00295-06"
Issue候補: "C06"
タイトル: "ZIP/tree review と staging を runtime command へ昇格する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C06 ZIP/tree review と staging を runtime command へ昇格する — draft plan

## Step sequence

1. ZIP root / entry / metadata validation を実装する。
2. forbidden authority claim scanner を追加する。
3. safe extraction と staging output を実装する。
4. tree fallback の limitation diagnostics を追加する。
5. EAL candidates と dry-run diff を生成する。
6. positive/negative fixtures を追加する。

## Dependencies

- 04-prepare-prompt-pack-and-safe-output-constraints

## Verification

- valid ZIP fixture test
- unsafe ZIP fixtures
- forbidden claim scanner tests
- tree fallback classification test
- stage output ownership marker test
- canonical unchanged test

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
