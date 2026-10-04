# Issue #413 / PR #414 CI安定化の追加作業

2026-10-04 JST。利用者の追加指示により、CI失敗と再実行権限を調査し、必要な修復・push・全チェック待機を行い、PRを人間がマージできる状態へ進める。開始headは `6e31e6ce108c0d88993f21fed9b788895a7b7324`。

## 結論と変更境界

- macOSとLinuxの配布検証を維持する。[AC-413-02](iss-00413-external-cli-state/requirement.md#ac-413-02)が要求する、通常インストールされた外部consoleの実動作を確認するために必要。
- 製品の要件・設計・runtimeを変更せず、テスト用fixtureの自動Gitメンテナンスだけを停止する。既存の全tree比較、Git管理領域の無書込み確認、OS別CIは維持する。
- 再実行権限は、同じ利用者の保存済みGitHubログインで解消した。トークンの権限・アカウント設定・workflowの権限指定は変更していない。
- `8606e132327066d56567556e336e4bc1ae6a0b17` の原Final Quality Gate証拠を保持する。今回のテスト修正を、そのSHAに対する外部レビューで認定済みとは扱わない。

## 失敗の分析

[最初のmacOS失敗](https://github.com/chemitaro/spec-dock/actions/runs/37136037299/job/111240645474)は、既存の `test_installed_validation_needs_no_control_and_writes_nothing[head]` で発生した。結果は1 failed / 87 passed。`before = tree_digest(root)` が `.git/objects/maintenance.lock` を列挙した後、`lstat()` の前にそのファイルが消え、`FileNotFoundError` になった。製品consoleはまだ呼ばれていなかった。

仮説を次のように比較した。

| 仮説 | 観測・判定 |
|---|---|
| fixture commit後のGit自動メンテナンスとの競合 | 実GitのTrace2で、50回すべてに `git maintenance run --auto --quiet --detach` の起動を確認。失敗したlockの所有者・タイミングと一致 |
| SpecDock自身の副作用 | console呼出し前で失敗しており、この失敗の原因にはならない |
| 静止したtreeの比較不良 | 通常条件50回とmaintenance対象を増やした条件50回の自然試行では例外0。静止条件だけでの再現はなかった |

CIの順序を固定し、列挙済みの一時lockを`lstat()`直前に消す制御再現では、同じpath・例外・製品コードの位置で失敗した。自然再現率と制御再現を混同しない。Gitはローカル2.54.0、再実行したmacOS runnerは2.55.0だった。修正前headのmacOSジョブは、同じコードで再実行すると88件成功した。不安定な競合を再実行だけで解決済みにせず、fixtureのバックグラウンド処理を止める。

`tree_digest` は保全・比較のための厳格な処理であり、同時変更を無視するようには変更しない。テストから `.git` を除外する方法も、Git管理領域への書込みを見逃すので採用しない。

## 具体的な修復

1. `make_workspace` が作る一時リポジトリへ、最初のcommit前に `git config --local maintenance.auto false` を設定する。
2. 実Gitの `committed_workspace` を呼び、Trace2に自動maintenance/gc子processがないことを回帰テストにする。利用者のglobal/system設定に結果が依存しない条件で実行する。
3. 元の実console試験と共有fixtureを使う試験を実行する。
4. `make lint` と通常の全pytestを実行する。修正を通常commit/pushし、Linux/macOSを含む全PRチェックの完了を待つ。
5. 最新headの全check成功、OPEN/non-draft、`mergeStateStatus=CLEAN` を確認して引き渡す。人間merge自体は行わない。

製品のインストール・更新・実行時に、このGit設定を利用者のリポジトリへ書き込む処理は追加しない。

## 権限の原因と解消

`gh auth status` では、環境変数 `GH_TOKEN` のfine-grained PATが優先され、同じ `chemitaro` の保存済みOAuthログインは非選択だった。リポジトリ自体のadmin/write権限はあっても、PATに必要なActions書き込み権限がなければ再実行APIは拒否される。

保存済みログインでも本人が `chemitaro`、対象が `chemitaro/spec-dock`、repository write権限ありと照合したうえで、次の一操作だけ環境トークンを外した。

```bash
env -u GH_TOKEN -u GITHUB_TOKEN gh run rerun 37136037299 --repo chemitaro/spec-dock --failed
```

native exit 0。再実行したmacOSジョブは成功し、元headの全7チェック成功とCLEANを確認した。恒久的な認証設定変更や、追加トークンの発行は不要だった。必要権限と通常運用の説明は [CIガイド](../ci.md) に記載した。

## 検証記録

- 回帰テストRed: 1 failed、exit 1。期待した差分は自動maintenance子processが1件存在すること。
- 同じ回帰テストGreen: 1 passed、exit 0。
- 同じ実Git観測50回の比較: 自動maintenance起動は修正前50件、修正後0件。修正後の全tree snapshotは50回すべて成功。
- 関連3ファイル: 130 passed、exit 0。元の外部console検査を含む。
- `make lint`: 成功、exit 0。
- 通常全pytest: native macOSで1917 passed / 1 skipped、394.96秒、exit 0。
- 修正後headのPR CI: 最新headに対する結果はPRのChecksを正本とする。全チェック成功とCLEANを確認してからマージ準備完了と報告する。

再現用harness、Trace2、nativeログはEpic 356のignored Workbench内 `ci-414-repair/` に保管する。原Final Quality Gateのraw JSONは変更しない。最新のGitHubチェック結果は [PR #414](https://github.com/chemitaro/spec-dock/pull/414) で確認する。
