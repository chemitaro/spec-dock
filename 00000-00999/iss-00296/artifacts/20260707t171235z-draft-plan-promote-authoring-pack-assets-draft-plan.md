---
種別: 実装計画書（Issue）
ID: "iss-00296"
タイトル: "Authoring Pack Assets"
Issue Grade: "standard"
状態: "draft | approved | in-progress | completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
---

# C01 authoring pack assets を provider-side installed layout へ昇格する — draft plan

## Step sequence

1. 現行 helper と関連 fixtures の inventory を作る。
2. provider-side target layout を作成する。
3. helper scripts / shared modules を移設し、旧 surface は thin wrapper または明示的 compatibility path にする。
4. tests / fixtures の参照 path を更新する。
5. 移設 inventory、compatibility note、canonical mutation なしの evidence をまとめる。

## Dependencies

- none

## Verification

- provider-side file inventory check
- legacy helper compatibility smoke test
- asset path fixture resolution test

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
