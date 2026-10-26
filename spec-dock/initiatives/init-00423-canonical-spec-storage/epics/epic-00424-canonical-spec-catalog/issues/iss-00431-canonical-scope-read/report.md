---
種別: レポート（Issue）
ID: "iss-00431"
タイトル: "Read Scopes From GitHub In Canonical Mode"
関連GitHub: ["#431"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Epic の I-4 として、canonical モードで Scope とその周りを読むコマンドを動かした。構造（題名、種類、状態、親子、依存、作業中の印）は構造のスナップショット（C10、`ensure_fresh(display)`）から、内容の場所はカタログ（C3、`CatalogTree`）から読み、`.meta.json` は読まない。公開の形は `design.md` のとおりである。

- **動くようにしたコマンド**：`scope show`、`scope list`、`dependency list`、`dependency check`、`active show`、`active set`、`active clear`、`artifact list`、`artifact show`、`branch show`、`branch create`、`branch switch`、`worktree list`、`worktree show`、`worktree remove`、`worktree bootstrap`、`workbench copy`（`CANONICAL_WORKBENCH_SHARED` で止まる）、`workspace sync`、`workspace validate`、`workspace doctor`。`worktree create --expect-current` と、版4の `installation show/update/uninstall --expect-current` も、スナップショットで選択を確かめてから今の処理をする。`CANONICAL_NOT_IMPLEMENTED` が残るのは、I-5 の書くコマンド16個だけである（テストで確かめる）。
- **読む側の共通の部品**（`application/canonical_scopes.py`）：スナップショットから、従来と同じ形の `ScopeView` を作る。パスはこのチェックアウトのリンクを通した解決しないパスなので、従来の `read_selection`、`resolve_scope`、`check_scope_expectations`、`list_scopes`、`dependency_listing`、`sync_selection_links` を変えずに使える。`--offline` は GitHub に何も送らずに今のスナップショットで示す。同じ ID のディレクトリが2つあっても、ほかの読み取りを止めない。
- **着手の判定の部品**（`domain/canonical_readiness.py`。I-5 と I-11 が使う）：`evaluate_readiness` と `evaluate_all` が、状態（`DONE` > `UNKNOWN` > `DOING` > `BLOCKED` > `READY`）、`ready`（`DOING` を見ない）、ブロッカーの一覧（`CanonicalBlocker`：番号、Scope の ID、役、求める状態、見えた状態、宣言した Scope）、`UNKNOWN` の理由の一覧（異常のコード）を返す。
- **`workspace validate`**：Epic の6章の検査をすべて行う。誤りは `findings`（終了コード7）、入れ子のずれ（次の1手 `spec-dock scope move <ID>`）、別名ファイル、Scope でない Issue への依存は警告。`--ci` は `CANONICAL_NOT_APPLICABLE` で `spec-dock canonical check` を示す。
- **`canonical status --structure`**（I-2 から引き継いだもの）：付けたときだけ GitHub の構造を確かめ、入れ子のずれを `structure` の項目と警告に示す。付けないときは `not_checked` で、GitHub に問い合わせない。
- **`--source` の既定**（統括の判断 Q1）：`dependency check` と `workspace sync` のパーサーの既定を None にし、`parse_vnext` の中で従来どおり `local` に戻す。canonical モードは、明示の `--source local` だけを `CANONICAL_NOT_APPLICABLE` で止める。
- **ブランチ**（統括の判断 Q3）：従来の `.meta.json` の照合の代わりに、対象のコミットのツリーに `spec-dock/initiatives` があれば `CANONICAL_BASE_HAS_SPECS` で止める（定数は I-5 も使う）。
- **I-1 から引き継いだ直し**：GraphQL のレート制限で待ち時間0を60秒にしない（`is None` の比較）。`github_error_result` と dispatch の `except GithubStructureError` のテスト。2つ目のファイル（`probe.json`）の書き込みの失敗のテストを、その経路を通る形に直した。
- 実現しなかったこと：なし（I-4 の範囲で）。

## Verification

### 最終品質ゲート

ゲートの形は、統括の指示どおりの Claude だけのもの（ChatGPT は使わない）。push した SHA で `make lint` と全体の `uv run pytest` を通し、この作業に関わっていない新しい2つのサブエージェント（Standards と Spec）にレビューを頼む。P0 と P1 は直してやり直し、P2 と P3 は情報として扱う。

- **ゲートの SHA**：`f35b0896300a5d07fd7d179865b15b7d87e8431f`（`bf84d46c9` に `origin/main` の `2e16d3f06`（#448、Epic の文書だけ）を merge したコミット。競合なし）。push 済みで、ローカルの `HEAD` と `origin/chemitaro/iss-00431-canonical-scope-read` が同じ SHA であることを確かめてから始めた。
- `make lint`：ruff check、ruff format check、mypy のすべてが成功（終了コード0）。
- `uv run pytest`：2649 passed、8 skipped、終了コード0（711秒）。実行の後も `HEAD` は同じ。作業ツリーの変更は、実行中に書いたこの `report.md`（文書だけ）1件だけだった。
- **Standards**：P0、P1 なし。P2 が3件（ST-1 checkout の失敗の後の再観察が従来より弱い、ST-2 作成の失敗の後の `_branch_tip` の例外で効果が消える、ST-3 `--expect-current` の確かめと従来の処理の取り込みの間の時間と docstring のずれ）、P3 が5件（ST-4 `@root` の `--expect-current` がリンクを求める、ST-5 取り直したときも `source` が `cache`、ST-6 異常のある Scope のディレクトリを `SCOPE_ISSUE_MISSING` と示しうる・`os.walk` の読めないディレクトリ、ST-7 checkout の後のきれいさの確かめがない、ST-8 `clear_active` の写しと `replace_namespace` の置き場）。ゲートの決まりで直さず、下の「Residual Risks」に引き継ぐ。
- **Spec**：P0 なし。P1 が1件（SP-1 ゲートの SHA で `report.md` が空）。計画では報告書をゲートの後に書く順（S11）だったための指摘で、この報告書を書いた文書だけのコミットで解決し、同じレビュアーに解決を確かめてもらった（下の「SP-1 の確かめ」）。P2 が1件（SP-2 版3の `dependency check` を `--source` なしで動かした JSON を直接比べるテストがない。値は `parse_vnext` の中で `local` に戻し、`--help` の出力は `origin/main` と同じ md5 であることをレビュアーが確かめた）、P3 が4件（SP-3 origin がないときの終了コードがコマンドで違う、SP-4 は ST-3 と同じ、SP-5 一部の異常のコードを CLI で個別に作っていない、SP-6 祖先のディレクトリがないときの `active set` のテストが弱い）。AC-431-01〜14、16 は「満たす」、15 は「実装は満たす。証跡は SP-1」、17 はゲートの実行で満たす。
- コードはゲートの SHA から変えていないので、lint と全体のテストはやり直していない（文書だけの変更。統括の指示）。

### 変えた既存のテスト（`git diff origin/main...HEAD -- tests/`。AC-15）

版3の振る舞いを確かめるテストは変えていない。変えた既存のテストは7つのファイルで、すべて canonical モードのテスト（I-1、I-2 が置いたもの）か、I-1 から引き継いだ直しである。

| ファイル | 変えたこと | 区分 |
|---|---|---|
| `tests/cli_runtime/test_issue428_canonical_mode.py` | 文字の出力のテストの未実装の例を `scope list` から `scope close` に。版4の `installation … --expect-current` が未実装であることのテストを、スナップショットで確かめて書く前に止まること（GitHub の origin がない作り物なので `GIT_FAILED`）のテストに | canonical モードのテスト（I-1） |
| `tests/cli_runtime/test_issue429_canonical_link.py` | `worktree create --expect-current` が未実装であることのテストを、確かめられないときに何も作らないことのテストに | canonical モードのテスト（I-2） |
| `tests/cli_runtime/test_issue429_canonical_status.py` | `structure` の期待を `not_implemented` から `not_checked` に | canonical モードのテスト（I-2） |
| `tests/integration/test_issue413_assets.py` | init の直後の版4の `workspace validate` の期待を `CANONICAL_NOT_IMPLEMENTED` から `CANONICAL_NOT_LINKED` に（I-1 が版4への振り分けを確かめるために変えた1行） | canonical モードへの振り分け（I-1 が許された区分で変えた行） |
| `tests/unit/commands/test_canonical_dispatch.py` | 未実装の例を `scope show` から `scope close` に | canonical モードのテスト（I-1） |
| `tests/unit/infra/test_github_snapshot.py` | `test_a_failed_second_file_write_keeps_one_reflection_in_memory` を、`commit_refresh` で `probe.json` の書き込みを失敗させる形に | I-1 から引き継いだ直し（R-431-12） |
| `tests/unit/infra/test_github_structure.py` | 待ち時間0の GraphQL のレート制限のテストを足した | I-1 から引き継いだ直し（R-431-12） |

### この Issue で足したテスト

- `tests/unit/domain/test_canonical_readiness.py`（着手の判定）、`tests/unit/cli/test_issue431_source_default.py`（`--source` の既定、`--help`）、`tests/unit/application/test_canonical_github_errors.py`（GitHub の失敗の結果と dispatch）。
- `tests/cli_runtime/test_issue431_scope_read.py`、`test_issue431_dependency_active.py`、`test_issue431_branch.py`、`test_issue431_worktree.py`、`test_issue431_workspace.py`、`test_issue431_read_only.py`。部品は `tests/support/canonical_scopes.py`（一時の bare とクローン、`canonical link`、`origin` の付け替え、偽の `gh`、一時の `XDG_STATE_HOME`、選択の記録の直接の書き込み）。

### 文書と実装の独立レビュー

- 文書（S0）：blocker 1、major 6、minor 7。すべて妥当で、`plan.md` の「文書のレビューの指摘の対応」のとおり直した。
- 実装（S9）：規約 9件（high 1、medium 3、low 3、judgment-call 2）、仕様 6件（high 1、medium 1、low 4）。`plan.md` の「実装のレビューの指摘の対応」のとおり、ST-7 と ST-8 のほかを直した。

### 実機の確かめ

- macOS（外付けのボリューム、scratchpad の一時ディレクトリ）：`uv build --wheel` の wheel（`spec_dock-0.2.4`）を一時の venv に入れ、一時の bare のリポジトリから作ったクローンで `canonical link` を行い、カタログに Scope のディレクトリを置き、`origin` を `https://github.com/example/repo.git` に替え、偽の `gh` を `PATH` の先頭に置いた。`HOME`、`XDG_STATE_HOME`、`XDG_CONFIG_HOME` は一時ディレクトリ。
- 外の console で、`scope show`（題名）、`scope list`、`dependency check`（`BLOCKED`）、`dependency check --source github`、`workspace validate`、`workspace sync`、`workspace doctor`、`canonical status --structure`、`branch show`（`init-00001-plan`）、`worktree list` がすべて `succeeded`（終了コード0）、`dependency check --source local` が `CANONICAL_NOT_APPLICABLE`（終了コード3）だった。前後で、チェックアウトとカタログの `git status --porcelain --ignored` は同じで、偽の GitHub への書き込みの要求は0件、状態の置き場には `snapshot.json` と `probe.json` だけができた。確かめた後に一時のものを消した。利用者の `~/.local/state/spec-dock/` とツールの設定は使っていない。
- 偽の `gh` は標準入力を読むので、閉じない標準入力の端末からは待ち続けて `GITHUB_UNAVAILABLE`（時間切れ）になった。偽物の作りによるもので、本物の `gh` は GET で標準入力を読まない（`/dev/null` を渡して確かめた）。

### 確かめていないこと（未確認）

- 本物の GitHub での読み取り（このリポジトリには種類のラベルのある Issue がなく、I-10 より前に canonical のコマンドを本物の spec-dock で実行しない決まりのため）。偽の `gh` だけで確かめた。
- Linux での実行は、提供側の CI（`ubuntu-latest`）の結果で確かめる（PR の検査）。

## Residual Risks / Follow-ups

- **最終品質ゲートの P2 と P3**（ゲートの決まりで情報。コードは変えていない）：上の「最終品質ゲート」の ST-1〜ST-8 と SP-2〜SP-6。とくに、ブランチの失敗の後の再観察（ST-1、ST-2、ST-7）は従来の `branch_operations` より簡単にしてあり、Git が途中で失敗したときの効果を `failed` と示しうる。I-5 か I-9 で従来と同じ形にそろえるかは、統括の判断に任せる。

- **従来の部品への依存**（ST-7、ST-8。判断で直さない）：canonical の処理は、従来のモジュールの非公開の関数（`branch_operations` の `_capture_selection` など、`direct_diagnostics` の `_github_request` など、`scope_query._sort_key`、`direct_artifact._view`）を使い、Artifact の走査は従来の `list_artifacts` の写しである。従来のモジュールを変えない制約（AC-15）のためで、I-13 の撤去で canonical 側に寄せる。
- **`worktree remove` と無視されたファイル**：canonical モードのworktreeには、いつも無視されたリンク `spec-dock/initiatives` があるので、`worktree remove` には `--discard-ignored` が要る（従来の `spec-dock/active/` のリンクと同じ扱い。リンクを消すだけで、カタログの中身は消えない）。I-9 の文書に書くか、リンクを数えない扱いにするかは、統括の判断に任せる。
- **`worktree remove --expect-current` の選択**：canonical 側が取り込んだ記録で確かめ、従来の処理がその後に自分で取り込んだ記録の変化を見る。2回の読み取りの間の変化は、従来の処理の確かめで止まるが、間の時間はわずかに残る。
- **`display` の古さ**：表示は最大30分古い構造を示しうる（Epic の設計どおり）。`--source github` で取り直せる。
- **I-9 への申し送り**：`plan.md` の「exit / handoff」のとおり（`--source` と `--offline` の意味、`canonical status --structure`、Epic の12章にない新しいコード）。
- **I-5、I-11 への引き渡し**：`plan.md` の「exit / handoff」のとおり。
