---
種別: レポート（Issue）
ID: "iss-00434"
タイトル: "Add Default Branch Spec Check And Workflow"
関連GitHub: ["#434"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Epic の I-7 として、既定のブランチの検査（契約 C7 の持ち主）を足した。公開の形は `design.md` の「C7 の公開の形」のとおりである。

- **`spec-dock canonical check [--commit REV]`**（`application/canonical_check.py`、`infra/commit_tree.py`）：指定したコミット（既定 `HEAD`）のツリーと blob だけを読み、Epic の8章の6つを調べる。問題は1件ずつ、パスと次の1手（`details.path`、`details.next_step`）を付けて `data.result.failures` に並べ、`CANONICAL_CHECK_FAILED`（終了コード7）で終わる。版3の宣言は `WORKSPACE_NOT_MIGRATED` の1件として返し、ほかの調べることも続ける。版のファイルの版の違いは警告 `SPEC_DOCK_VERSION_MISMATCH`。作業ツリー、インデックス、カタログ、状態の置き場、ネットワーク、GitHub を読まず、何も書かない。
- **振り分け**：I-1 の `REPOSITORY_INDEPENDENT_HANDLERS`（C2）に登録した。`runtime_dispatch.py` は変えていない。作業ツリーの宣言（版3、版4、ない、壊れている）によらず、コミットのツリーで判定する。
- **配布資産の分類**：`installation show` の分類の式を `infra/static_assets.classify_static_digest` に移し、`installation show` と `canonical check` が同じ関数を使う（振る舞いは同じ）。
- **CLI**：`cli/catalog.py` に `canonical check`（読むだけ。44 → 45）と `--help` の文、`presentation/envelope.py` に文字の出力（失敗と警告ごとに、パスと次の1手の1行）。`CANONICAL_CHECK_FAILED` は I-1 の決まりどおり `application/canonical_errors.py` に置いた。
- **配布資産（C7）**：`spec-dock/system/spec-dock-version`（`0.2.4\n`）、`spec-dock/docs/ci/spec-dock-check.yml`（Epic の8章の見本）。`static-inventory.json` に足し、`reference_cli.md`（数と C45 の行）と `docs/README.md`（数）を直して、前の中身の SHA-256 を `known_old_sha256` に足した。リポジトリのルートの `README.md` の数も直した。
- **spec-dock の CI（C7）**：`.github/scripts/specdock-ci-check.sh`（`specdock-ci-validate.sh` と同じ固め方で、最後だけ `canonical check --json`）、`.github/scripts/release-tag-decision.py`（版のタグの判定）、`.github/workflows/release-tag.yml`（`main` への push で、判定がタグを返したときだけ軽量のタグを作って push）。spec-dock 自身の `spec-dock-check.yml` と `ci.yml` の変更は、計画どおり I-10 に残した。
- **C3 の値**：無視の3行は、I-2 がまだ `main` にないので、`canonical_check.SPEC_DOCK_IGNORE_LINES` に Epic の3章の値を写して持つ。I-2 と I-7 のうち後から `main` に入る側が、C3 の定数に置き換える。
- 実現しなかったこと：なし（I-7 の範囲で）。

## Verification

### 最終品質ゲート（2026-10-26。ChatGPT のゲートは利用者の設定で無効のため、Claude だけのゲート）

- **ゲートの SHA**：`2fa9a42df653e603a2fdb95ad16a323eb2547a19`。通常の push の後、ローカルの `HEAD` と `origin/chemitaro/iss-00434-canonical-branch-check` が同じ SHA で、作業ツリーに変更がないことを確かめてから始めた。`origin/main` は `41a4c57c0` から進んでおらず（PR #443 は未マージ）、マージするものはなかった。この記録のコミットは、ゲートの後に `report.md` だけを変える。
- `make lint`：ruff check、ruff format check、mypy のすべてが成功（終了コード0）。
- `uv run pytest`：2318 件成功、8 件スキップ（594.83 秒、終了コード0）。実行の後も `HEAD` は同じで、作業ツリーに変更はない。
- `.github/scripts/specdock-ci-validate.sh "$PWD" "$PWD" 2fa9a42df…`（今の CI の手順。AC-15）：成功（終了コード0）。wheel の `sha256` は `b5d1c482227097eb655206644125350e513a52eda383a3010245737513df6168`、`workspace validate --ci` は `succeeded`、`valid: true`、`snapshot_source: HEAD`、`node_count: 260`。手元の `python3` の問題のため、`PATH` の先頭に Homebrew の `python3` を置いた（下の実機の確かめと同じ）。
- **独立レビュー**（この作業に関わっていない新しいサブエージェント2つ。規約と仕様。対象は `origin/main...2fa9a42df` の全差分）：どちらも **P0/P1 なし**。P2/P3 は、ゲートの決まりで情報として扱い、修正もレビューのやり直しもしない。中身は下の「Residual Risks / Follow-ups」に引き継ぐ。
  - 規約：P2 1件（ST-1）、P3 7件（ST-2〜ST-8）。
  - 仕様：P3 5件（SP-1〜SP-5）。AC-434-01〜09 は「満たす」（08 と 09 の本物の GitHub Actions は計画どおり後の Issue）、10 は「一部」（レビューの中で全体のテストを走らせていないため。上のとおりゲートで実行して成功した）。

### 自動のテストと lint

- この Issue で足したテスト：`tests/unit/application/test_canonical_check.py`、`tests/unit/infra/test_commit_tree.py`、`tests/unit/infra/test_static_asset_classification.py`、`tests/unit/infra/test_issue434_version_file.py`、`tests/cli_runtime/test_issue434_canonical_check.py`、`tests/integration/test_issue434_ci_check.py`、`tests/integration/test_issue434_release_tag.py`、`tests/integration/test_issue434_workflow_sample.py`、`tests/unit/commands/test_canonical_dispatch.py` の1件。共通の部品 `tests/support/canonical_check.py`。
- `make lint` は `.github/scripts/` を対象にしないので、`release-tag-decision.py` には ruff check、ruff format、`mypy --strict` を手で当てて通した。
- `880b5e0d1`（S4〜S7 の後）で `uv run pytest`：2314 件成功、8 件スキップ（595.69 秒、終了コード0）。

### 文書と実装の独立レビュー

- **文書のレビュー**（S0、この会話を知らないサブエージェント1つ）：ブロッカー0、major 3、minor 9。`analyze-review-findings` で分析し、次のとおり対応した（コミット `5bff2037`、`880b5e0d1`）。
  - 版のファイルが調べること5と6の両方に当たる扱いを、要件と設計にそろえた（既知の古い版は警告だけ、知らない中身は失敗も）。単体テストを足した。
  - 資産が増えて落ちる `test_issue413_assets.py` の2か所（資産の数）を、許された変更の表に足した（実際に全体のテストで落ち、表のとおり直した）。
  - I-8 の `cut` が見本を埋め込んで持ち、テストで資産とバイト単位で比べること、既定のブランチの名前の範囲を C7 に書いた。
  - 定数を `CI_VERSION_FILE` に改名した（`asset_layout.VERSION_FILE` は退けた engine pin のパス）。`CANONICAL_CHECK_FAILED` を `canonical_errors.py` に置いた。
  - `--expect-*` の止まり方に次の1手、文字の出力に警告の次の1手、`--dry-run` の扱いを足した。見本の手順を取り出して実行する結合テスト（AC-434-09）を足した。`release-tag.yml` の失敗の戻し方を書いた。ルートの `README.md` の数を直した。
  - 反論（変えない）：版4で古い既知の `writer_protocol` を通すこと（Epic の「既知である」のとおり。下の「統括に判断してほしいこと」）。
- **実装のレビュー**（S10、`code-review` の観点で、独立した2つのサブエージェント。対象 `41a4c57c0..880b5e0d1`）：規約（Standards）は ST-1〜ST-8、仕様（Spec）は SP-1〜SP-7。どちらもブロッカーなし。仕様の AC の判定は 01、02、03、05、06、07、08 が「満たす」、04 と 09 と 10 が「一部」（04 はテストの弱さ、09 と 10 は報告書の未記入）。分析と対応：
  - SP-3：`--commit 'HEAD^{tree}'` などコミットでない名前が `GIT_FAILED`（5）になった → `resolve_commit` が `rev-parse --verify` の終了コード1を「ない」とするよう直した（テストを追加）。
  - SP-4：深い入れ子の宣言で `RecursionError` が外に出た → `invalid-json` の1件にした（テストを追加）。
  - ST-1：`release-tag.yml` の `concurrency` は、待ち中の版上げの run を取り消しうる → 外した。ST-8：判定のスクリプトの `git` に時間切れを付けた。
  - SP-1/ST-6：`gh` が git と同じディレクトリにあると外れていなかった → `PATH` を git だけのディレクトリにし、`gh` がないことを確かめるようにした。ST-2/SP-7：`--dry-run` の「何も書かない」を呼び出しごとに確かめるようにし、UTF-8 でないパスのテストを足した。ST-5：版の判定のテストが 0.3.0 で壊れないよう、今の版から期待を決めるようにした。ST-3：本物の配布資産のままのツリーの結果を固定するテストを足し、重ねる部品が C3 と違う書き方を黙って隠さないようにした。
  - SP-5、版のファイルの `\r\n`：設計と要件の記述を実装にそろえた。SP-2：この報告書を書いた。
  - 反論・引き継ぎ（変えない）：ST-4（仕様のパスが数千のツリーで出力が大きい。要件で「すべてを1件ずつ返す」と決めたとおり。切り替えの後の既定のブランチでは起きない）、ST-7（`committed_validation.py` との `ls-tree` の解析の重複。従来の処理は変えない決まりなので、I-13 の撤去で統合する）、SP-6（配布する `cli-redesign-guide.html` の「全44コマンド」の一覧は、C45 の行を含めた更新が要るので、使い方の文書を受け持つ I-9 に引き継ぐ）。

### 従来モードの回帰で変えた既存のテスト（Epic の testability の許された区分）

| テスト | 変えた行 | 区分 |
|---|---|---|
| `tests/cli_runtime/test_issue413_contract.py` | コマンドの数 44 → 45 | コマンドの数 |
| `tests/cli_runtime/test_cli_vnext_contract.py` | 一覧に `canonical check`、数 44 → 45 | コマンドの数と一覧 |
| `tests/integration/test_cli_docs_vnext.py` | コマンドの数 44 → 45 | コマンドの数 |
| `tests/cli_runtime/test_help_completion_vnext.py` | コマンドの数 44 → 45、読むだけのコマンドの一覧に `canonical check` | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue428_canonical_mode.py` | 全コマンドの引数の表に `canonical check`（I-1 の canonical モードのテスト） | コマンドの一覧 |
| `tests/integration/test_issue413_assets.py`（2か所） | `installation uninstall` が外す資産の数 84 → 86、効果の数 85 → 87 | 配布資産の数 |

- このほかに、既存のテストは、`tests/unit/commands/test_canonical_dispatch.py` にテストを1件足しただけである（既存のテストの中身は変えていない）。

### 実機の確かめ（2026-10-26、macOS、scratchpad の一時ディレクトリ）

- **見本の手順**（AC-434-09）：見本の `Install SpecDock` と `Check` の `run:` を、見本から取り出して書かれたとおりに実行した。GitHub の代わりに、このブランチ（`880b5e0d1`）の一時のクローンにローカルのタグ `v0.2.4` を付け、一時の `GIT_CONFIG_GLOBAL` の `url.<file://…>.insteadOf = https://github.com/chemitaro/spec-dock` で向け先を変えた。`pipx`（1.18.4）は一時の venv に入れ、`PIPX_HOME`、`PIPX_BIN_DIR`、`PIP_CACHE_DIR`、`XDG_STATE_HOME` を一時ディレクトリにした。
  - 本物の配布資産（I-2 の前）：`pipx install "spec-dock @ git+https://github.com/chemitaro/spec-dock@v$(cat spec-dock/system/spec-dock-version)"` は成功（終了コード0）。正しいツリーの検査は、`IGNORE_RULES_MISSING`（`spec-dock/.gitignore`）の1件だけで終了コード7（I-2 の無視の3行がまだ配布資産にないため。想定どおり）。
  - 無視の3行を配布資産に足した写し（I-2 の後の代わり）：正しいツリーで終了コード0（`succeeded`、失敗なし、警告なし）、仕様のパスを足したツリーで終了コード7（`SPEC_PATH_TRACKED` の1件）。
  - どちらも、状態の置き場（一時の `XDG_STATE_HOME`）は作られなかった。
- **`specdock-ci-check.sh`**：このブランチ（`880b5e0d1`）をソースにして本物の配布資産のツリーで終了コード7（`IGNORE_RULES_MISSING` だけ）、無視の3行を足した写し（`22b54508f`）をソースにして正しいツリーで0、仕様のパスのあるツリーで7。
  - 手元の `python3`（`~/.local/bin/python3`）がスクリプトの中で `init_fs_encoding` で起動できない、I-1 の報告と同じ手元の環境の問題があり、`PATH` の先頭に Homebrew の `python3`（3.14.6）を置いて実行した。CI の `ubuntu-latest` には当たらない。
- **版のタグの判定**：このリポジトリで `--before origin/main --after HEAD` を判定すると `version-unchanged`（タグなし）。
- 一時ディレクトリは確かめの後に消した。利用者の `~/.local/state/spec-dock/` は作られていない。

### 確かめていないこと（未確認）

- 本物の GitHub Actions での見本のワークフローの動き（版のタグからの `pipx install` と、PR への結果の表示）。I-10 で確かめる。
- 本物の GitHub Actions での `release-tag.yml` の動き（`v0.3.0` の作成）。I-9（0.3.0）のマージの後に確かめる。
- Linux での実行は、提供側の CI（`ubuntu-latest`）の結果で確かめる（PR の検査）。

## Residual Risks / Follow-ups

- I-2 の配布資産 `spec-dock/.gitignore` に無視の3行が入るまで、本物の配布資産だけのツリーは `IGNORE_RULES_MISSING` で失敗する（正しい動き）。テストは、無視の3行を持つ `.gitignore` を重ねた資産で通過を確かめている。I-2 が先に入ったら、後から入る側が `SPEC_DOCK_IGNORE_LINES` を C3 の定数に置き換え、重ねる部品（`tests/support/canonical_check.py`）が何もしないことを確かめる。
- 版を上げる Issue（I-9 の 0.3.0、I-13 の 0.4.0）は、版のファイルの前の中身の SHA-256 を `known_old_sha256` に足す（C7 の決まり）。
- I-9 への引き継ぎ：配布する `spec-dock/docs/cli-redesign-guide.html` のコマンドの一覧（「全44コマンド」、C01〜C44 の表）に、`canonical` のコマンドを足す。
- I-13 への引き継ぎ：`infra/commit_tree.py` と `infra/committed_validation.py` の `ls-tree` の解析の重複を、撤去のときに1つにする。
- 利用側の `spec-dock/`（この repo の dogfooding の workspace）は、計画どおり更新していない（I-9 の `installation update`、I-10）。今の利用側の `docs/README.md` と `reference_cli.md` は、新しい `static-inventory.json` でも `known-old` なので害はない。新しい2つの資産は `missing` と示される。
- 最終品質ゲートの P2/P3（直さずに引き継ぐもの）：
  - ST-1（P2）：`IGNORE_RULES_MISSING` の次の1手は「3行を手で足す」だが、手で足すと `.gitignore` が知らない中身になり、`STATIC_ASSET_INVALID` に変わる（`installation update` も知らない中身を拒む）。I-2 が配布資産に3行を入れた後は、`.gitignore` が `current` か `known-old` のときの次の1手を `spec-dock installation update …` にするのがよい。I-2 と I-7 のうち後から入る側か、I-9 のエラーの一覧の確かめで、設計の表と一緒に直す。
  - SP-2（P3）：3行がそろっていて順だけが逆のときも、次の1手が「この順で足す」になる（並べ替えが要る）。ST-1 と一緒に直す。
  - ST-5（P3）：見本の版のファイルは `0.2.4` だが、版のタグは 0.3.0 から作るので、0.2.4 のうちに見本をそのまま置くと `pipx install` が失敗する。各リポジトリへの組み込みは 0.3.0 の後（I-10、I-12）なので実害はないが、I-9 の文書に「0.3.0 以降」と書く。
  - SP-1/ST-2（P3）：宣言を UTF-8 として読んでから解析するので、BOM 付きの `workspace.json` を `invalid-json` にする（作業ツリーの宣言の読み取りは受け付ける）。安全側の違い。`json.loads(read(entry))` にそろえる。
  - ST-3（P3）：`ls-tree -r --full-tree` はコミットの全体を読み、資産の blob を1つずつ `cat-file` で読む。大きなリポジトリでは時間とメモリが要る（この repo で約0.7秒）。pathspec で `spec-dock` と `.agents` に絞るか、`cat-file --batch` にする余地がある。`entry_count` はツリー全体の数。
  - ST-4（P3）：文字の出力が、警告の `details` に `path` と `next_step` があると決め打ちしている（今の警告は1種類で、どちらもある）。ST-7（P3）：`ls-tree` の出力が壊れているときの `ValueError` が `PRECONDITION_FAILED`（3）になる。SP-4（P3）：失敗が1件でもエラーの文が「1 problems」。
  - ST-6（P3）：判定のスクリプトのコメントの「3.10 では tomli」は、runner の `python3` には当たらない（`ubuntu-latest` は 3.12 なので実害はない）。SP-3（P3）：判定のスクリプトの「判定できないとき終了コード1」のテストがない。
  - ST-8（P3）、SP-5（P3）：`cli-redesign-guide.html` の数（I-9 に引き継ぎ済み）と、この報告書のゲートの記録（この節で記録した）。
- 統括に判断してほしいこと：版4の宣言で `writer_protocol` が古い既知の値（`specdock.writer/v1`）のとき、Epic の「既知である」のとおり通している。書くコマンドは `require_writer` で止まる状態なので、失敗にするかどうか（`design.md` の risk）。
