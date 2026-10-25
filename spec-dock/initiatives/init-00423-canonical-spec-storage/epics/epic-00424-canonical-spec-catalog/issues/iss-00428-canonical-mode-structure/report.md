---
種別: レポート（Issue）
ID: "iss-00428"
タイトル: "Add Canonical Mode And GitHub Structure Snapshot"
関連GitHub: ["#428"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Epic の I-1 として、canonical モードの土台（契約 C1、C2、C10）を、利用者の動きを変えずに足した。公開の形は `design.md` のとおりである。

- **モードの判定（C2）**：`read_workspace_declaration` が版3と版4を受け付け、`workspace_mode` と `ProjectContext.mode` がモード（`legacy` / `canonical`）を返す。版5、真偽値、文字列は今と同じく `PRECONDITION_FAILED`。
- **振り分けの入口（C2）**：`commands/canonical_dispatch.py` の2つの表（`CANONICAL_HANDLERS`、`resolve_context` の前に呼ぶ `REPOSITORY_INDEPENDENT_HANDLERS`）と、`runtime_dispatch.dispatch` の5か所の変更。版4で処理のないコマンドは `CANONICAL_NOT_IMPLEMENTED`（終了コード3、「SpecDock 0.3.0 を待つ」）、版4の `workspace migrate` は `CANONICAL_NOT_APPLICABLE`、版3の `canonical …` は `CANONICAL_NOT_MIGRATED`。エラーのコードと次の1手は `application/canonical_errors.py` に1か所で置いた（I-2 が使う `CANONICAL_NOT_LINKED` を含む）。
- **`installation`**：配布資産 `spec-dock/workspace.json` を版4にし（`static-inventory.json` の `sha256` と、版3の内容を `known_old_sha256` に）、`installation init` の結果に次の1手 `spec-dock canonical link`（警告 `CANONICAL_NOT_LINKED`）を入れた。`show`、`update`、`uninstall` は版4で動き、版4の `--expect-current` は `CANONICAL_NOT_IMPLEMENTED`（canonical の処理は I-4）。
- **構造の表し方と規則（C1）**：`domain/canonical_structure.py`（種類のラベル、作業中のラベル、ラベルの色と説明、slug の印の読み書き、ID、`ScopeNode`、`StructureSnapshot`、異常のコード、`build_snapshot`、書き込みの反映 `apply_changes`、取り直しへの重ね合わせ `merge_refresh`、`dependency_violations`）。循環の確かめは今の `domain/dependency_vnext.py` の規則を使う。
- **GitHub の呼び出しの部品（C1）**：`infra/github_structure.py`（`GithubApi`：状態行での判定、304、レート制限、500番台の再試行、書き込みの間の1秒。`GithubStructureClient`：GraphQL の全体の読み取り、条件付きの確かめ、REST の読み取りと書き込み、結果が分からない書き込みの読み直し）。
- **構造のスナップショット（C10）**：`infra/github_snapshot.py`（置き場、ディレクトリへの `flock`、原子的な書き込み、メモリーの上の扱い、`ensure_fresh` の3つの段階、`refresh`、`reread`、`reflect`）と、`infra/state_root.py`（状態の置き場の根。明示の上書きを受け取る）。
- **テストの共通の部品**：`tests/support/fake_github.py`（REST と GraphQL のモデル、条件付きの要求と 304、要求の記録、`inject`、時計、`PATH` に置く `gh`）。使い方は `design.md` の testability。
- 実現しなかったこと：なし（I-1 の範囲で）。`canonical` グループのコマンドは、計画どおり作っていない（I-2 以降）。

## Verification

### 最終品質ゲート（2026-10-26）

- **ゲートの SHA**：`33888954fcc59a5f443063cd6fa23be51b1889c2`（`a0281481d` に `origin/claude/epic-00424-canonical-spec-catalog`（`ed98cf861`、PR #441）をマージしたコミット。競合なし）。push 済みで、ローカルの `HEAD` と `origin/chemitaro/iss-00428-canonical-mode-structure` が同じ SHA で、作業ツリーに変更がないことを確かめてから始めた。この記録のコミットは、ゲートの後に `report.md` だけを変える。
- `make lint`：ruff check、ruff format check、mypy のすべてが成功（終了コード0）。
- `uv run pytest`：2227 件成功、8 件スキップ（513.81 秒、終了コード0）。実行の後も `HEAD` は同じで、作業ツリーに変更はない。
- `.github/scripts/specdock-ci-validate.sh "$PWD" "$PWD" 33888954f…`（統括の判断 C）：成功（終了コード0）。wheel の `sha256` は `45e31c594bbbf4169e491421a0126b6b4f59fb696b5b2d147cf68b353732d5dc`、`workspace validate --ci` は `succeeded`、`valid: true`、`snapshot_source: HEAD`、`node_count: 260`。
  - 1回目は、手元の `python3`（uv が管理する venv）が `init_fs_encoding`（`No module named 'encodings'`）で起動できず、終了コード2で止まった。この変更と関係のない手元の環境の問題である。`PATH` の先頭に Homebrew の `python3`（3.14）を置く一時の仕掛けで実行し直して成功し、仕掛けは消した。CI の `ubuntu-latest` では、PR の検査で確かめる。
- **独立レビュー**（この会話を知らない新しいサブエージェント2つ。規約と仕様。対象はゲートの SHA）：どちらも **P0/P1 なし**。P2/P3 は、ゲートの決まりで情報として扱い、修正もレビューのやり直しもしない。中身は下の「Residual Risks / Follow-ups」に引き継ぐ。
  - 規約：P2 2件（ST-1 2つ目のファイルの書き込みの失敗のテストが、その経路を通っていない。ST-2 `github_error_result` と dispatch の `except GithubStructureError` のテストがない）、P3 10件。
  - 仕様：P2 2件（SP-1 スナップショットにない番号への `SetParent` / `AddBlockedBy` / `RemoveBlockedBy` の反映が `ValueError` を出す。SP-2 Epic の C1 の「書く」表に本文の PATCH がない）、P3 4件。AC は 01〜11、13〜15 が「満たす」、12 は「確かめられない」、16 は「一部」（レビューの中で `specdock-ci-validate.sh` を実行していないため。上のとおりゲートで実行して成功した）。
  - 指摘の主張は、ソースで確かめた。SP-1 は、I-1 の中に `SetParent` などで `reflect` を呼ぶところがなく（`reread` は `UpsertIssue` だけで、これは `ValueError` を出さない）、I-5 が使い始めるときの契約の欠けである。

### 自動のテストと lint

- 変更の前（`be4810244`、2026-10-26）：`uv run pytest` は 2067 件成功、8 件スキップ（約8分）。
- S6 の後（`393b29f99` の作業ツリー）：`uv run pytest` は 2208 件成功、8 件スキップ（約9分）、`make lint` は ruff check、ruff format、mypy のすべてが成功。
- この Issue で足したテスト：`tests/unit/domain/test_canonical_structure.py`、`tests/unit/infra/test_github_structure.py`、`tests/unit/infra/test_github_snapshot.py`、`tests/integration/github/test_fake_github.py`、`tests/unit/application/test_project_context_mode.py`、`tests/unit/commands/test_canonical_dispatch.py`、`tests/cli_runtime/test_issue428_canonical_mode.py`、`tests/cli_runtime/test_issue428_legacy_outputs.py`。

### 版3の出力の比較（AC-428-16、統括の判断 C）

- 変更の前のソース（`git archive be4810244 src`）と今のソースで、同じ作り物（版3の宣言、Scope 1件、コミット済み）に対して `workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update --dry-run`、`installation update`（古い shim を戻す適用）を実行し、パスと SHA と版を置き換えた結果が一致した。変更の前の結果を `tests/fixtures/issue428/legacy-outputs.json` に置き、`tests/cli_runtime/test_issue428_legacy_outputs.py` が今のコードと比べる。`installation update` の後も、版3の宣言のバイト列は変わらない。

### 従来モードの回帰で変えた既存のテスト（統括の判断 1、2026-10-26）

| テスト | 変えた行 | 理由 |
|---|---|---|
| `tests/cli_runtime/test_issue413_work_start.py::test_start_accepts_the_standard_rule_documents_created_by_scope_import` | `installation init` の直後に、宣言を版3に書き戻す準備の4行を足した。`assert` は変えていない | init が版4を書くため。この後の `scope import` と `work start` は従来モードで動かす |
| `tests/integration/test_issue413_assets.py::test_init_places_only_static_assets_and_a_new_declaration_in_the_explicit_worktree` | 宣言の値の確かめを版4に。init の直後の `workspace validate` を、`CANONICAL_NOT_IMPLEMENTED`（終了コード3）の確かめにした | 配布資産の値の変化。新しい版4のリポジトリは canonical モードへ送られる |
| `tests/integration/test_issue413_assets.py::test_init_in_a_linked_worktree_does_not_install_into_main_or_shared_git` | `installation show` が示す宣言の版の確かめを4に | 配布資産の値の変化 |
| `tests/integration/test_issue413_wheel.py::test_fresh_wheel_contains_one_normal_runtime_and_context_free_utilities` | wheel の中の資産と init の宣言の値の確かめを版4に。`verify_issue415_console` の init の直後に、宣言を版3に書き戻す準備の4行を足した（README の `scope create` は従来モードで動かす。`assert` は変えていない） | 配布資産の値の変化と、init が版4を書くため |

- このほかに変えた既存のテストはない（`git diff be4810244 -- tests/` の既存のファイルはこの3つだけ）。

### 文書と実装の独立レビュー

- **文書のレビュー**（S0、この会話を知らないサブエージェント1つ）：15件（blocker 1、major 7、minor 7）。分析し、文書の訂正と実装の修正で対応した。Epic の記述と解釈が違う点は統括に確かめ、了承を得た（`plan.md` の「統括の判断」2回目）。
- **実装のレビュー**（S8、`code-review` の観点で、規約と仕様の独立した2つのサブエージェント。対象 `be4810244..393b29f99`）：規約 15件（high 1、medium 1、low 7、judgment-call 6）、仕様 10件（medium 1、low 9）。高い順の主なものと対応：
  - ST-1 / SP-1：2xx の書き込みで本文が読めないと「確かな失敗」になる → `_write` が本文の解析の失敗を「結果が不明」として読み直しへ回すよう直した（テストを追加）。
  - ST-2：`CanonicalCommandError` が終了コード6を受けると封筒の例外が漏れる → 1、2、3、4、5、7 だけを受け付けるよう直した。
  - ST-3 / SP-3：2つのファイルを毎回書き、2つ目の失敗で変更を2回当てる、304 の確かめでも `snapshot.json` を置き換える → 変わったファイルだけを書き、排他の中で計算した値をメモリーに置くよう直した。
  - ST-4 / SP-7：組み立ての `ValueError` が `cycle` を止める → `GITHUB_RESPONSE_INVALID` に写して段階ごとの扱いを通すよう直した。
  - ST-5 / SP-2：失敗の記録が別のプロセスの新しい確かめを巻き戻す → `record_probe_error` と、`save_probe` の新しさの比べを足した。
  - SP-4：読めない Issue の `remove_sub_issue` が成功になる → 子が読めることを先に確かめるよう直した。
  - そのほか（ST-6 UTF-8、ST-8 型、ST-9 `HOME`、ST-10 GraphQL は問い合わせだけ、ST-11 排他の待ち時間、ST-12 `clear_faults`、ST-13 型ヒント、ST-14 二重の定数、SP-5 型の別名、SP-6 定数、SP-8 偽の GitHub を通した異常のテスト、SP-9 足りない negative test、SP-10 設計の文）を直した。
  - 直さなかったもの（反論）：ST-7（`dependency_vnext` に `cast` で渡す）は、従来の domain のモジュールを変えない制約のための設計どおりの選択で、`design.md` に明記している。ST-15（保存形式を domain に置く）は、`design.md` の配置どおりで、純粋な関数として保つ。
- 再レビューは、最終品質ゲートの2つの新しいサブエージェントで行った（上の「最終品質ゲート」）。

### 実機の確かめ（本物の GitHub、読むだけ、2026-10-26）

- 設計どおりの GraphQL の問い合わせの費用は1ページ104点、`blockedBy` の要素のラベルを外すと4点（`rateLimit.cost`。`chemitaro/spec-dock` で読むだけ）。統括の判断 3 で外した。
- 今の実装の `StructureSnapshotService` を `chemitaro/spec-dock` に対して、書き込みを拒む実行器（GET と GraphQL の POST だけを通す）で動かした。1回目：確かめの3回（200）と GraphQL の1回（費用4点、種類のラベルのある Issue は0件）で取り直し、`probe.json` に3つの `ETag` を記録した。2回目（`decision`）：確かめの3回がすべて `HTTP/2.0 304 Not Modified`（`gh` の終了コード1）で、状態行で正しく判定し、取り直さなかった。状態の置き場は scratchpad の一時ディレクトリで、確かめの後に消した。利用者の `~/.local/state/spec-dock/` は作られていない。

### 確かめていないこと（未確認）

- 本物の GitHub への書き込み（ラベル、sub-issue、依存、Issue の作成と更新）。この Issue では行わない決まりで、偽の GitHub だけで確かめた。I-10 で本物で確かめる。
- 本物の GitHub での、レート制限の応答（403/429 と `retry-after`）と500番台の応答の形。公式の文書の記述と偽の GitHub で確かめた。
- 種類のラベルのある Issue が本物にないため、全体の読み取りの結果の中身（親子、依存、印）は、本物では確かめていない（偽の GitHub で確かめた）。
- Linux での実行は、提供側の CI（`ubuntu-latest`）の結果で確かめる（PR の検査）。

## Residual Risks / Follow-ups

- 版4のリポジトリは、0.3.0（I-9）まで、`installation` と `workspace migrate` のほかは `CANONICAL_NOT_IMPLEMENTED` で止まる（Epic の計画のとおり）。この間に `installation init` で作ったリポジトリは、使えない。
- `read_workspace_declaration` が版4を受け付けるので、従来の処理が別の宣言（基点のコミット、`--ci` の HEAD、同じクローンのほかのworktree）を版4として読む場面がある。移行していないリポジトリには版4がなく、切り替えの途中（I-10、I-12）だけの出来事で、従来の処理はその後の `.meta.json` の確かめで止まる。
- 親子と依存の変更で Issue の `updated_at` が変わるかは未確認（Epic の未確認の事項）。偽の GitHub の既定は「変わらない」側にしてあり、30分ごとの取り直しで補う。
- 統括が Epic の文書（`design.md`、`plan.md`）に反映する事項：`plan.md` の「統括の判断」の1回目と2回目（A1〜A7、B、C）。このうち PR #441 にまだない次の3点（最終品質ゲートの SP-2、SP-5、SP-6）：
  - Epic の design.md 2章（215行、290行の付近）の異常のコードに、この Issue が足した3つ目の `SUB_ISSUE_FOREIGN_REPOSITORY`（別のリポジトリの子。読む側は「着手できる」にしない）を足す。
  - Epic の design.md 651行の `CANONICAL_NOT_LINKED` の次の1手は、警告に `recovery` の欄がないため、実装と Issue の design.md 4章のとおり `details.next_step` と書く。
  - Epic の design.md 2章の C1 の「書く」表に、Issue の本文の PATCH（6章の `scope import github` が既にある Issue に印を足すため）がない。`update_issue(body=…)` を誰が足すか（I-1 の追補か I-5 か）を決める。
- 最終品質ゲートの P2/P3 で、直さずに引き継ぐもの（ゲートの決まりで情報として扱った）：
  - SP-1（P2）：スナップショットにない番号への `SetParent`、`AddBlockedBy`、`RemoveBlockedBy` を `reflect` すると `ValueError` が出て、dispatch では `PRECONDITION_FAILED`（failed、終了コード3）になる。GitHub に書いた後の反映でこれが起きると、効果のある書き込みが「効果なし」と返る。I-1 には呼び出し元がない。I-5 が使い始める前に、扱い（当てずに飛ばして警告にする、など）を C10 の design.md 7章で決め、テストを足す。
  - ST-1（P2）/ SP-4（P3）：`tests/unit/infra/test_github_snapshot.py` の `test_a_failed_second_file_write_keeps_one_reflection_in_memory` は、`reflect` が `probe.json` を書かないため、2つ目のファイルの失敗の経路を通っていない。`commit_refresh` で `probe.json` の書き込みを失敗させ、メモリーの値、`persisted=False`、`local_writes` が1回だけであることを確かめるテストに直す。
  - ST-2（P2）：`application/canonical_errors.github_error_result` と、`runtime_dispatch` の `except GithubStructureError` のテストがない（partial の終了コード6、failed の5、`retry_at` の文）。I-2 以降で最初に使うときに足す。
  - SP-3 / ST-10（P3）：`update_issue` の読み直しが `state_reason` を比べない。
  - ST-6（P3）：`_rate_limit_wait(...) or 60.0` は待ち時間0を60秒にする（`is None` で比べる）。
  - ST-3（相対の `HOME` を受け付ける）、ST-4（`_read` が `read_guarded_json_at` を使わない、`_DirectoryLock` と `StartLock` の重複）、ST-5（`rename` の後のディレクトリの `fsync` の失敗を書き込みの失敗として扱う）、ST-7（`ScopeView` への `cast`）、ST-8（終了コードの規則の重複）、ST-9（表にない 4xx の書き込みを「結果が不明」とする）、ST-11（ラベルの `totalCount` がないときを黙って受け付ける）、ST-12（GraphQL のエラーに `endpoint="graphql"` がない）（いずれも P3）。
- 後の Issue への引き渡し：`plan.md` の「exit / handoff」のとおり。
