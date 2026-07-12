---
種別: 実装計画書（Issue）
ID: "iss-00304"
タイトル: "ChatGPT Authoring Skill"
Issue Grade: "standard"
状態: "draft | approved | in-progress | completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C09 `spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する — draft plan

## Step sequence

1. new skill doc の責務と forbidden claims を作成する。
2. existing planning skill docs に modes / stop gates / ChatGPT lane relation を反映する。
3. managed skill list / installer metadata を更新する。
4. skill inventory diff と install simulation を実行する。
5. user-facing order と stop gate matrix を evidence として残す。

## Dependencies

- 02-add-authoring-command-skeleton

## Verification

- managed skill inventory test
- skill file presence test
- update/init install simulation
- stop gate wording snapshot
- user-facing name table check

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
