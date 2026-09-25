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

修正中、実Git管理領域 `/Volumes/990p2t/workspace/tools/spec-dock/.git/worktrees/spec-dock4/index.lock` の作成が `Operation not permitted` となり、Git書込みを一旦停止しました。lockの消失と実Git経路を読み取り専用で確認した後、許可済みの通常Git操作を権限付きで実行し、実装payloadを `d7f5f6a081f8332ff598ed3f0e7a627a9a0737d8` として非forceでpushしました。HEAD・upstream・GitHub先頭は一致し、作業ツリーはcleanでした。

この固定SHAで `make lint`、`git diff --check`、`uv run pytest` を再実行し、すべて終了コード0でした。pytestは `2053 passed, 25 skipped in 910.94s`。同じSHAから `uv build --wheel` で構築したwheelのSHA-256は `c08954fdf7dc31deace208d9f7c31d1aa189ddd70178d9d5430331803a1f765d` です。隔離venvへの導入、`--help --json`、`work start --help --json` はいずれも終了コード0で、wheel内のskill・runtime・migration guide・四つのWorkbench templateを確認しました。全テストには隔離fixtureでのinstallation/group updateのresume・rollback、workspace migrationの適用・復元が含まれます。実導入先への更新・migration・rollbackは実行していません。

検証log・各SHA-256・コマンド別終了コードは本Issueの無追跡 `.workbench/chatgpt-final-quality-gate-strict-v2/issue409-cli-on-demand-update/test-results/manifest.json` に保存しました。このReportを含む後続commitではGit SHAが変わるため、最終レビュー対象SHAで必須コマンドを再実行してmanifestを更新します。追跡文書に自身のcommit SHAを埋め込む自己参照は行いません。最終レビューは前回と同じChatGPT conversationで実施します。

前回の固定候補 `51dbb214dce6e49ad8afd4a13d43c8eb8fd014e5` は、lint・全テスト・wheel導入には成功しましたが、同じレビュアーの Final Quality Gate Strict v2 でP1が4件残りました。指摘はleaf別help、TTY確認と実行対象の固定、失敗時の復旧receipt、Scope群のJSON payloadです。本作業ツリーで配布元・dogfood投影・関連テストを修正しました。他の稼働中のworktreeおよびconsumerは更新していません。修正後の固定SHAで再検証し、同じレビュアーに再審査を依頼します。

## Residual Risks / Follow-ups

- 他worktree・consumerは未更新です。更新時には[導入・移行・復旧手順](../../../../../../docs/migration.md)に沿って、選んだGit common directoryの全登録worktreeを確認してください。
- 既存の導入先を新CLIへ更新するまでは、その導入先で旧CLIが動きます。製品sourceの変更だけで実行中のwriterは切り替わりません。
