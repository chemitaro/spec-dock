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

製品sourceの前回候補 `3057e4f8a619070f868f96f31e7fb3f86084143e` では、固定wheelと隔離engineの検査に成功しました。同SHAの Final Quality Gate Strict v2 はP1が11件で未通過、必須の `uv run pytest` も配布元とdogfooding側の差分により未通過でした。これらを最終候補の成功証拠には流用しません。

2026-09-25の修正作業では `make lint` と `git diff --check` が終了コード0、全テストの初回実行は `2047 passed, 6 failed, 25 skipped`（終了コード1）でした。失敗5件はGit helperの子プロセス環境で `PYTHONDONTWRITEBYTECODE` を落としたこと、1件は旧 `--to` 文面を期待するテストが原因です。該当6件の修正後の再実行は `6 passed`（終了コード0）、続く全テストは `2053 passed, 25 skipped`（終了コード0、926.73秒）でした。配布元とこのworktreeの写しのbyte一致テストも通過しました。これらは未コミット作業ツリーの結果であり、固定SHAに紐付く認証結果ではありません。

修正中、実Git管理領域 `/Volumes/990p2t/workspace/tools/spec-dock/.git/worktrees/spec-dock4/index.lock` の作成が `Operation not permitted` となり、Git書込みを一旦停止しました。lockの消失と実Git経路を読み取り専用で確認した後、許可済みの通常 `git add` を権限付きで実行し、stageに成功しました。上記の全テストはstage前の同じ作業ツリーの結果です。本レポート作成時点で、固定SHAでの全テスト、wheel構築、同じChatGPTセッションの最終再レビューは未実施であり、後続の品質ゲート証跡にSHA・コマンド・終了コード・配布物ダイジェストを固定します。実導入先への適用は実行していません。

## Residual Risks / Follow-ups

- 他worktree・consumerは未更新です。更新時には[導入・移行・復旧手順](../../../../../../docs/migration.md)に沿って、選んだGit common directoryの全登録worktreeを確認してください。
- 既存の導入先を新CLIへ更新するまでは、その導入先で旧CLIが動きます。製品sourceの変更だけで実行中のwriterは切り替わりません。
