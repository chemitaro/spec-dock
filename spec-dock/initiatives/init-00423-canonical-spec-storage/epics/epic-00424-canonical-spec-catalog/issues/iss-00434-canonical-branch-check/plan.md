---
種別: 実装計画書（Issue）
ID: "iss-00434"
タイトル: "Add Default Branch Spec Check And Workflow"
関連GitHub: ["#434"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00434 Add Default Branch Spec Check And Workflow — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- 選択：`standard`（Epic の `plan.md` の指定）。
- 理由：足すのは読むだけのコマンド1つと、配布資産2つと、spec-dock の CI のファイルである。どれも PR の `git revert` で戻せ、データの移行がない。従来モードの処理には触れない。
- risk factor：配布資産の値（`static-inventory.json`）と、後の Issue が使う公開の形（C7）を決めること。`release-tag.yml` が、マージの後に spec-dock のリポジトリにタグを作れること（書き込みの権限を持つワークフロー）。
- 再評価条件：従来の処理、`specdock-ci-validate.sh`、`ci.yml` の変更が要るとわかったとき、Epic の契約（C2、C3、C7）を変える必要が出たとき、許された区分のほかに版3の振る舞いのテストの変更が要るとわかったときは、止まって統括に聞き、`strict` を検討する。

## 目標

- `requirement.md` の AC-434-01〜10 を、テスト先行の単体テスト、CLI のテスト、結合のテストと、`make lint`、`uv run pytest` で満たす。AC-434-09 は実機で確かめ、本物の GitHub Actions は未確認として残す。
- `design.md` の「C7 の公開の形」を、I-8、I-9、I-10、I-12、I-13 がそのまま使える状態にする。

## 順序・依存

1. 文書（この3つ）を書き、独立のレビューを受けて直す（S0）。
2. 部品を下から作る：配布資産の分類の関数（S1）→ コミットのツリーの読み取り（S2）→ 検査の判定（S3）。S1 と S2 は並べて進めてよい。
3. コマンドとしてつなぐ（S4）。S3 の後。
4. 配布資産（S5）、spec-dock の CI のファイル（S6、S7）は、S3 と独立している。S6 の通過のテストは S4 の後に通る。
5. 全体の確かめ（S8）、実機の確かめ（S9）、実装のレビュー（S10）、最終の品質の関門（S11）、報告書と PR（S12）。

並行の注意：I-2（`iss-00429`）が、`cli/catalog.py`、`commands/canonical_dispatch.py`、`static-inventory.json`、`reference_cli.md`、コマンドの数のテストで同時に変更している。先に `main` に入った方を、後の方が `origin/main` のマージで取り込む（rebase しない。`resolving-merge-conflicts`）。I-2 が先に入ったら、`SPEC_DOCK_IGNORE_LINES` を C3 の定数に置き換え、無視の3行を持つ `.gitignore` の注入が要らなくなったかを確かめる。

## 実装step

各 step は `tdd` の Red → Green → Refactor で進め、区切りで `git-commit` でコミットする。

- **S0 文書**：`requirement.md`、`design.md`、`plan.md` を書き、この会話を知らないサブエージェントに、Epic の要件・設計・計画と照らしてレビューさせる。指摘を `analyze-review-findings` で分析し、根拠のあるものを直してコミットする。Epic の契約を変える必要や、設計書で決まっていない判断は、Orca の `ask` で統括に聞く。
- **S1 配布資産の分類**：`infra/static_assets.py` に `classify_static_digest` を足し、`installation show` をそれに置き換える。既存の `installation show` のテストが変更なしで通ることで、振る舞いが同じことを確かめる。
- **S2 コミットのツリー**：`infra/commit_tree.py`（`resolve_commit`、`list_commit_tree`、`read_blob`）。一時のリポジトリで、regular、実行可能、symlink、gitlink、UTF-8 でないパス、知らない名前を確かめる。
- **S3 検査の判定**：`application/canonical_check.py` の `evaluate_commit_tree` と、失敗のコード、次の1手、C7 の定数。調べること1〜6を1つずつ Red → Green。
- **S4 コマンド**：`cli/catalog.py`（一覧、引数、`--help`）、`commands/canonical_dispatch.py`（表への登録）、`check_canonical_commit`、`presentation/envelope.py`（文字の出力）。CLI のテスト（AC-434-01〜05）。新しいコマンドで落ちるコマンドの数と一覧のテストを、`design.md` の testability の表のとおりに直す。
- **S5 配布資産**：`spec-dock/system/spec-dock-version`、`spec-dock/docs/ci/spec-dock-check.yml`、`reference_cli.md` と `docs/README.md` とルートの `README.md` の数と行、`static-inventory.json`（`sha256`、`known_old_sha256`）。版のファイルと `pyproject.toml` の単体テスト、見本の中身のテスト（AC-434-06）。資産が2つ増えることで落ちる資産の数のテスト（`test_issue413_assets.py` の2か所）を、`design.md` の testability の表のとおりに直す。見本の手順を取り出して実行する結合テスト（AC-434-09、`tests/integration/test_issue434_workflow_sample.py`）。
- **S6 `specdock-ci-check.sh`**：`specdock-ci-validate.sh` を写して最後の1行を変える。結合のテスト（AC-434-07）。
- **S7 版のタグ**：`release-tag-decision.py` と `release-tag.yml`。判定のテスト（AC-434-08）。`make lint` の対象外なので、ruff（check と format）と mypy を手で当てる。
- **S8 全体の確かめ**：`make lint`、`uv run pytest`。`git diff origin/main -- tests/` で、変えた既存のテストが testability の表のものだけであることを確かめる。
- **S9 実機の確かめ**（AC-434-09）：手元で wheel を作り、scratchpad の一時ディレクトリに、一時の venv（または一時の `PIPX_HOME` と `PIPX_BIN_DIR` の `pipx`）で入れる。一時のリポジトリで、見本の手順と同じ形（版のファイルを読んで入れ、`spec-dock canonical check --json`）を実行し、正しいツリー（無視の3行を持つ `.gitignore` を重ねた写しから作った wheel）、仕様のパスのあるツリー、本物の配布資産だけのツリー（I-2 の前は `IGNORE_RULES_MISSING`）の結果を `report.md` に書く。`specdock-ci-check.sh` も同じ一時のリポジトリで実行する。終わったら一時ディレクトリを消す。利用者の環境（`~/.local/pipx` など）に入れない。
- **S10 実装のレビュー**：`code-review` の観点で、規約（Standards）と仕様（Spec）を、独立した2つのサブエージェントにレビューさせる。指摘を `analyze-review-findings` で分析して直し、必要ならもう一度レビューする。
- **S11 最終の品質の関門**：すべてをコミットし、通常の push をする。`origin/main` をマージし（PR #443 が入っていれば Epic の文書を含む）、その SHA を固定して、`make lint` と `uv run pytest` を通し、`origin/main...HEAD` の全差分を、新しい2つのサブエージェント（規約と仕様。仕様の基準は、この Issue と Epic の受け入れ条件、Issue をまたぐ契約、AC-15）にレビューさせる。止める指摘を直したら、新しい SHA で最初からやり直す。合格の証拠を `report.md` に書く。
- **S12 報告と PR**：`report.md` を書き、`github-pr-creator` で `main` への PR（`Refs #434`）を作り、`github-pr-checks` で CI を確かめる。マージはしない。`work finish` は実行しない。

## 検証

| 対象 | 方法 |
|---|---|
| AC-434-01〜05 | `tests/cli_runtime/test_issue434_canonical_check.py`、`tests/unit/application/test_canonical_check.py`、`tests/unit/commands/test_canonical_dispatch.py` |
| AC-434-06 | `tests/unit/infra/test_issue434_version_file.py` |
| AC-434-07 | `tests/integration/test_issue434_ci_check.py` |
| AC-434-08 | `tests/integration/test_issue434_release_tag.py` |
| AC-434-09 | `tests/integration/test_issue434_workflow_sample.py` と、S9 の実機の確かめ（`report.md`）。本物の GitHub Actions は未確認 |
| AC-434-10（AC-15） | `make lint`、`uv run pytest`（変更の前の全体のテストと同じテストが、許された変更のほかは変更なしで通る）。最終の品質の関門の SHA で `.github/scripts/specdock-ci-validate.sh <worktree> <worktree> <HEAD>` も通す（今の CI を壊していないこと） |
| negative test | コミットのないリポジトリ、知らない名前、`--expect-current`、壊れた宣言の各 `reason`、資産の `missing`/`unknown`/`unsafe`、無視の3行の欠けと逆の順、版の違い、`specdock-ci-check.sh` の引数の誤りと SHA の食い違いと汚れたソース、判定のスクリプトの各 `reason` |
| 外部の依存を使えない場合 | 本物の GitHub Actions（見本のワークフロー、`release-tag.yml`）はこの Issue では動かせない。手元の wheel と一時のリポジトリで手順を確かめ、本物は I-10（見本）と I-9 のマージの後（`release-tag.yml` の最初のタグ）で確かめる |

- security / privacy：検査は読むだけで、トークンを使わない。見本のワークフローは `permissions: contents: read`。`release-tag.yml` だけが `contents: write` を持ち、作るのはタグだけで、判定はスクリプトに分けてテストする。`github.event.before` などは環境変数で渡し、シェルの文字列に直接埋め込まない。
- operability：失敗ごとにパスと次の1手を JSON と文字の両方で示す。CI の記録で、外すべきパスが分かる。
- migration：N/A。データの移行はない（配布資産が2つ増えるだけで、`installation update` が足す）。

## rollback

- マージの前：ブランチを捨てるか、コミットを revert する。
- マージの後、I-8 などが C7 を使う前：PR を `git revert` する。`canonical check` を使うものはまだなく、版3のリポジトリの動きは変わらない。`release-tag.yml` は 0.3.0 まで何もしない。
- `release-tag.yml` が、版を上げた push で失敗したとき（I-9、I-13 のマージの後）：失敗した run を Re-run するか、そのコミットに軽量のタグを手で作って push する（`design.md` の「移行・互換性・rollback」）。
- 後の Issue が C7 を使い始めた後：forward recovery で直す（C7 の形を変えるときは、先に Epic の `design.md` とこの `design.md` を直す）。

## exit / handoff

- 完了の条件：AC-434-01〜10 をテストと実機で確かめ（AC-434-09 の本物の GitHub Actions は未確認として記録）、最終の品質の関門に合格し、`report.md` に証拠を書き、PR がマージできる状態（CI が通っている）で止まる。マージは人が行い、`work finish` は統括の指示で行う。
- 後の Issue への引き渡し（`design.md` の「C7 の公開の形」）：
  - I-8：`CI_VERSION_FILE`、`WORKFLOW_SAMPLE`、`WORKFLOW_DESTINATION`、`WORKFLOW_BRANCH_LINE` と見本のバイト列を写し（テストでパッケージの定数と資産と比べる）、`cut` で見本を写して既定のブランチの行を置き換える。`export-legacy` で外す。
  - I-9：版を 0.3.0 にするとき、版のファイルと `known_old_sha256` を更新する。配布する `cli-redesign-guide.html` のコマンドの一覧に `canonical` のコマンドを足す。`CANONICAL_CHECK_FAILED` と失敗のコードを、エラーの一覧の確かめに入れる。`canonical check` の使い方を文書に書く。
  - I-10：`.github/workflows/spec-dock-check.yml` から `specdock-ci-check.sh` を呼び、`ci.yml` の `workspace validate --ci` の手順を外す。本物の GitHub Actions での見本の動きを確かめる。
  - I-12：各リポジトリの既定のブランチで `canonical check` を通す。
  - I-13：版を 0.4.0 にするとき、版のファイルと `known_old_sha256` を更新し、`release-tag.yml` が `v0.4.0` を作ったことを確かめる。`specdock-ci-validate.sh` を消す。`infra/commit_tree.py` と `infra/committed_validation.py` の `ls-tree` の解析を1つにする。
  - I-2（後から入るとき）：`SPEC_DOCK_IGNORE_LINES` を C3 の定数に置き換える。
- 残るリスク：本物の GitHub Actions での見本と `release-tag.yml` の動き（未確認）。I-2 が入るまで、本物の配布資産だけのツリーが `IGNORE_RULES_MISSING` で失敗すること。
