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

続く固定候補 `1badca8bb9ca17e970d2494939590fc8840ba165` は `make lint`、`uv run pytest`（`2075 passed, 25 skipped`）、`git diff --check` と固定wheel検査を通過しましたが、同じ Final Quality Gate Strict v2 でP1が4件でした。指摘ごとに Strict 分析を行い、helpの実際のmode、移行時の確認計画とmapping identity、準備済みGitHub作成の再開とowner由来の復旧コマンド、Scopeの計画結果・一覧のJSON契約を修正しました。修正はproviderとこのworktreeのdogfood投影だけに適用し、`9b5fa8d9`、`84aa1614`、`710cc89e`、`847a7e1e` として順にコミット・非force pushしました。各範囲のfocused testsとlintは通過しています。最終候補での全テスト、固定wheel、Strict v2再審査の結果は、この後の固定SHAに結び付けて記録します。

固定候補 `8613582da4cbe649cd7bd82ff75ce236e419a5b8` は全テスト `2080 passed, 25 skipped` と固定wheel検査を通過しました。同じ Final Quality Gate Strict v2 ではP1が3件残り、別の Strict 分析で原因と修正方針を確認しました。TTYで承認したGitHub repositoryをwriter lock内の実行対象へ照合し、移行マップは単一file descriptorから読んだbytesとidentityを一つの計画に束ねました。`installation init` のrollbackコマンドには必須のpathを含め、ローカルScopeの作成プレビューには正規化済みslugを含めました。配布元・このworktreeのdogfood投影・回帰テストに反映し、focused tests `67 passed`、`make lint`、全テスト `2084 passed, 25 skipped`、`git diff --check` が通過しました。固定SHAの検証結果と独立レビューの判定は、上記 `.workbench` のmanifestおよびレビューログに保存します。

固定候補 `c6e838fcf71b24a2e364ddb8d733eb74dd67db12` は全テスト `2084 passed, 25 skipped` と同じレビュアーの Final Quality Gate Strict v2（12観点、P0/P1=0、pass）を通過しました。ただし、このworktreeの実行CLIは旧版のままで、配布元と投影のbyte一致だけでは実際の導入・移行・作業開始を確認できていませんでした。

利用者が承認した独立cloneで、新しい固定engineによる実導入とschema 3への移行を実施しました。最初の実行では、既存Scopeの一部に `depends_on` がなく、移行後の依存関係検査とworkspace validationが失敗しました。移行時に空リストを補完する修正を `1a89aaeebf774d1a7647545b9b054e08620f1f00` にコミットしました。次の実行では、導入の復旧用バックアップが未追跡ファイルとなり、`work start` のclean tree条件を妨げることを確認しました。復旧データを保持したまま専用ディレクトリ内でGit ignoreする修正を `812bf674897bd933abaa8ce81d2ca32bfbc00b93` にコミットしました。両修正には失敗を再現するテストを追加し、修正後に通過を確認しています。

`812bf674` のGitHub上のcommitから作った、登録worktreeが一つだけの独立cloneでは、`installation update --maintenance`、239 Scopeの `workspace migrate --to-schema 3`、`installation update --finalize`、`workspace validate`、`workspace sync` が成功しました。移行差分を確認し、元の239 Scopeの属性・既存依存を保持したままschema 3、backend、空依存の初期値を設定したことを検査しました。clone内でlocal Initiative `init-local-00004`、Epic `epic-local-00002`、Issue `iss-local-00002` を作成し、`work start` を上位から順に実行して各専用ブランチへのcheckoutとactive選択を確認しました。`work finish` は下位から順に実行し、三つのScopeがcompleted、activeが空、最終 `workspace validate` がvalidであることを確認しました。GitHubのScopeは作成・変更していません。導入、移行、作業操作の証拠は本Issueの無追跡 `.workbench/dogfood/` に保存しました。共有Git領域を持つこの開発worktreeと他の稼働中worktreeは更新していません。

独立cloneを置いた後の全テストでは `2084 passed, 1 failed, 25 skipped` でした。失敗は旧CLIのdogfooding検証fixtureが `spec-dock/initiatives/` を複製する際、Git管理外の `.workbench/dogfood/` に入った独立cloneまで複製し、同じ旧Issue IDを重複検出したためです。正本ツリーだけを複製するよう `.workbench` を除外し、該当テストを再実行して `1 passed` を確認しました。最終候補の全テスト結果は固定SHAに対して改めて取得します。

## Residual Risks / Follow-ups

- 他worktree・consumerは未更新です。更新時には[導入・移行・復旧手順](../../../../../../docs/migration.md)に沿って、選んだGit common directoryの全登録worktreeを確認してください。
- 既存の導入先を新CLIへ更新するまでは、その導入先で旧CLIが動きます。製品sourceの変更だけで実行中のwriterは切り替わりません。
- 独立cloneの239件の既存GitHub Scopeはcacheに状態がないため、最終validationに `status_unknown` warningが239件残ります。local Scopeのstart/finishとworkspace整合性は成功しています。
