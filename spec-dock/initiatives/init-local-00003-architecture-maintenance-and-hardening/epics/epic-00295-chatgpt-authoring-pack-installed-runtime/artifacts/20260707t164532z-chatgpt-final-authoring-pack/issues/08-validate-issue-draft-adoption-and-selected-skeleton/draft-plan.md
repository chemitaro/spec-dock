---
種別: "Issue draft plan"
ID: "epic-00295-08"
Issue候補: "C08"
タイトル: "Issue draft adoption と selected skeleton validation contracts を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C08 Issue draft adoption と selected skeleton validation contracts を実装する — draft plan

## Step sequence

1. draft adoption input schema を定義する。
2. Issue node / parent trace / draft digest / target mapping checks を実装する。
3. selected skeleton fill validation を runtime module に接続する。
4. assurance observation-only と forbidden mutation check を追加する。
5. execution-ready self-claim rejection を追加する。
6. fixtures と reports を追加する。

## Dependencies

- 06-promote-zip-review-and-staging

## Verification

- issue draft adoption positive fixture
- selected skeleton fill positive fixture
- missing/extra section fixture
- profile/template hash mismatch fixture
- assurance mutation negative fixture
- execution-ready forbidden claim fixture

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
