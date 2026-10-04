# CIの役割と失敗時の確認

CIは、変更をGitHubへ送ったときに実行する自動検証です。SpecDockでは、実装・配布物・このリポジトリ自身の仕様データ・コミットの著者情報を確認します。チェックの成功後に、人間がPRをマージします。

## 現在のチェック

| 表示名 | 実行環境・対象 | 確認すること |
|---|---|---|
| `provider-tests` | Ubuntu、PRのマージ候補 | `make lint` と通常の全pytest。baseとの統合を含む実装の回帰 |
| `Provider distribution parity (ubuntu-latest)` | Linux、PRのheadそのもの | wheelの内容、新規インストール、外部console、静的資産、実Gitを使う主要操作 |
| `Provider distribution parity (macos-latest)` | macOS、PRのheadそのもの | 同じ配布・実consoleの検査をmacOSの実ファイルシステムとOS機能で確認 |
| `validate` | Ubuntu、pushとPR | 候補sourceから作ったwheelでdogfoodの仕様データを検証 |
| `check`（Commit identity） | Ubuntu、pushとPR | 新しいコミットの著者・コミッター情報を検証 |

`validate` と `check` はpushとPRの両イベントで実行されるため、同名の結果が二つ表示されることがあります。配布チェックは [.github/workflows/provider-ci.yml](../.github/workflows/provider-ci.yml)、仕様検証は [ci.yml](../.github/workflows/ci.yml)、著者検証は [commit-identity.yml](../.github/workflows/commit-identity.yml) が正本です。

## macOSとLinuxでインストールを試す理由

SpecDockの対応OSはLinuxとmacOSです。外部パッケージとして配布するため、sourceを直接importするテストに加え、wheelを新しい仮想環境へ通常インストールして、実際の `spec-dock` コマンドが動くことを確認します。これにより、runtimeや必要な静的資産の収録漏れ、checkout内のsourceへの意図しない依存を検出できます。

GitHubが用意する一時的な実行環境とテスト用ディレクトリへインストールします。利用者のPCや実プロジェクトを更新する処理ではありません。GitHubのIssue操作にはテスト用の `gh` を使います。

ファイルの安全な公開・同期・ロックにはOS固有の実装もあります。Linuxだけの成功ではmacOSの動作を保証できません。[Issue #413のAC-413-02](issue-plans/iss-00413-external-cli-state/requirement.md#ac-413-02)も、両OSで外部consoleを検証することを要求しています。この二つの配布チェックを維持します。

## GitHub Actionsを再実行する権限

CIの結果を読む権限と、終了済みのジョブを再実行する権限は異なります。fine-grained PATを使う場合、対象リポジトリへのアクセスに加え、リポジトリ権限の **Actions: Read and write** が必要です。OAuth tokenやclassic PATでは `repo` scopeが必要です。[GitHubの再実行API](https://docs.github.com/en/rest/actions/workflow-runs#re-run-failed-jobs-from-a-workflow-run)

CLIが使う認証は `GH_TOKEN`、`GITHUB_TOKEN`、保存済みログインの順に選ばれます。保存済みログインに十分な権限があっても、環境変数の制限されたトークンが優先される場合があります。[GitHub CLIの認証環境変数](https://cli.github.com/manual/gh_help_environment)

1. `gh auth status --hostname github.com` で認証元とアカウントを確認する。トークンそのものを表示・記録しない。
2. `gh api user --jq .login` で実際に使われる本人を確認する。リポジトリへの書き込み権限と、トークンのActions権限を区別する。
3. 同じ利用者の保存済みログインを使うことが承認済みで、そのログインに必要な権限がある場合は、環境変数をそのコマンドだけ外して操作できる。実行前に同じ形で `gh api user --jq .login` を呼び、対象アカウントを確認する。

```bash
# OWNER/REPOとRUN_IDは対象PRの実際の値に置き換える。
env -u GH_TOKEN -u GITHUB_TOKEN gh api user --jq .login
env -u GH_TOKEN -u GITHUB_TOKEN gh run rerun RUN_ID --repo OWNER/REPO --failed
```

この方法は保存済みの認証を利用し、ログイン設定やトークンの権限を変更しません。必要な認証が存在しない場合は、対象リポジトリに限定したActions書き込み権限を用意します。workflow YAMLの `permissions:` はジョブ内の `GITHUB_TOKEN` に対する指定なので、端末からの再実行権限不足を直す目的では変更しません。

## テスト用Gitのバックグラウンド処理

Gitはcommitなどの後に自動メンテナンスを起動できます。これがテストの前後比較と重なると、テスト用 `.git/objects/maintenance.lock` が列挙後に消えるなど、製品コマンドの実行前でも失敗し得ます。[Gitのmaintenance設定](https://git-scm.com/docs/git-maintenance#_configuration)

Issue #413の共有fixtureでは、最初のcommitより前に、その一時リポジトリだけ `maintenance.auto=false` を設定します。実GitのTrace2で自動メンテナンスが起動しないことを回帰検査し、既存の全tree比較は維持します。製品runtimeや利用者のリポジトリ・グローバルGit設定は変更しません。

## 失敗からマージ準備完了まで

失敗ログから、製品動作・テスト準備・配布・外部サービス・認証のどこで失敗したかを判別します。再実行で成功しても、再現可能な不安定要因があれば修復します。原因を確認せず、検査の削除・例外の無視・無条件の再試行で隠しません。

```bash
gh pr checks PR_NUMBER --repo OWNER/REPO --json name,state,bucket,link,workflow
gh run view RUN_ID --repo OWNER/REPO --log-failed
gh pr checks PR_NUMBER --repo OWNER/REPO --watch --interval 60 --fail-fast
gh pr view PR_NUMBER --repo OWNER/REPO --json headRefOid,state,isDraft,mergeStateStatus
```

修正をpushしたら、新しいhead SHAの全チェックが終了するまで確認します。`OPEN`、non-draft、全チェック成功、`mergeStateStatus=CLEAN` がマージ準備完了の判断条件です。通常CIの結果と、特定SHAを対象に実施した外部レビュー・Final Quality Gateの原結果は別の証拠として保持します。
