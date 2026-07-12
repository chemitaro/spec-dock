---
種別: 実装計画書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
Issue Grade: "standard"
状態: "draft | approved | in-progress | completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
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
