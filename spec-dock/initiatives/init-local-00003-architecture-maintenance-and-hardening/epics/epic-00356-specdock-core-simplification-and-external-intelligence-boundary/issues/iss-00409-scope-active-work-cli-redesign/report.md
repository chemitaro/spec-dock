---
種別: レポート（Issue）
ID: "iss-00409"
タイトル: "SpecDock CLI Scope Active Work Redesign"
関連GitHub: ["#409"]
最終更新: "2026-09-25"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

新しい `scope / active / work` のコマンド体系、Initiative/Epic/Issueの `work start` / `work finish`、固定engineの導入・更新、schema移行と復旧経路をprovider sourceへ実装しました。製品sourceと同一worktree内の仕様・説明資料を本Issueの成果とします。

2026-09-25の利用者指示により、稼働中の他worktree・consumerの一斉更新は本Issueの完了条件から除外しました。各導入先は所有者が必要な時に明示更新します。`installation update` と `workspace migrate` は指定されたGit common directoryの全登録worktreeを整合性単位として扱うため、その単位の更新時には同居するworktreeの停止・保全・検証が必要です。別のGit common directoryへは波及しません。

## Verification

固定candidateのwheelと隔離engineを構築し、複数worktree・consumer fixtureで更新・移行を検証しました。実導入先への適用は実行していません。最終品質ゲートと必須テストの結果、検証したSHA、終了コードは完了時に追記します。

## Residual Risks / Follow-ups

- 他worktree・consumerは未更新です。更新時には[導入・移行・復旧手順](../../../../../../docs/migration.md)に沿って、選んだGit common directoryの全登録worktreeを確認してください。
- 既存の導入先を新CLIへ更新するまでは、その導入先で旧CLIが動きます。製品sourceの変更だけで実行中のwriterは切り替わりません。
