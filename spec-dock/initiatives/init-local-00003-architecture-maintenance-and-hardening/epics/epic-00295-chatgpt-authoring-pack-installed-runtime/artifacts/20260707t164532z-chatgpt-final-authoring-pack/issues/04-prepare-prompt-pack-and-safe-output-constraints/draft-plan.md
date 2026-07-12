---
種別: "Issue draft plan"
ID: "epic-00295-04"
Issue候補: "C04"
タイトル: "prompt pack prepare と safe output constraints を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md", "draft-design.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C04 prompt pack prepare と safe output constraints を実装する — draft plan

## Step sequence

1. prompt pack schema と required entries を定義する。
2. preflight summary と source manifest から pack tree を生成する。
3. safe output constraints と forbidden claims list を生成する。
4. mode-specific prompt sections を追加する。
5. local-context provenance fields を追加する。
6. fixtures と deterministic output tests を追加する。

## Dependencies

- 03-implement-github-sync-preflight

## Verification

- deterministic prompt pack generation test
- metadata schema fixture test
- forbidden claims instruction fixture test
- local-context prompt fixture test
- secret/raw transcript exclusion test

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
