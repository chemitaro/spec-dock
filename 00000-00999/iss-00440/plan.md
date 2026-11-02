---
種別: 実装計画書（Issue）
ID: "iss-00440"
タイトル: "Remove Legacy Mode"
関連GitHub: ["#440"]
状態: "draft"
最終更新: "2026-11-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00440 Remove Legacy Mode — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **strict**（Epic の I-13 の決め方のまま）。
- 理由：多くのコードとテストを消し、共通の契約（R-J7）のテストを失う危険がある。0.5.0 は、5つのリポジトリが共有するパッケージで、入れた後は版3を読めなくなる。
- risk factor：消しすぎ（canonical の処理が使う部品を消す）、(b) のテストの見落とし、0.4.2 の配布資産からの更新の失敗、差分の大きさによるレビューの見落とし。
- 再評価の条件：(b) の書き直しが、`CanonicalWorld` で表せない契約（版3の作り物にしかない状態を前提にするもの）を含むとわかったとき、または1つの PR のレビューに収まらないと判断したときは、統括に分け方を `ask` で送り、返事を待つ。

## 目標

- `requirement.md` の AC-440-01〜AC-440-10 を満たす、マージできる PR（`main` へ、`Refs #440`、`Refs #424`）。
- `report.md` に、テストの分類の一覧、消したもの・残したもの、到達の判定の結果、コードの検索の結果、0.5.0 の wheel の確かめ、ゲートの結果を書く。

## 順序・依存

- 前提：I-12（`iss-00439`）の切り替えと運用の点検が終わり、利用者が I-13 を始めると決めた（2026-11-02）。
- PR は1つにする。撤去は、コード、テスト、作り物の補助が互いに頼るので、途中の状態では `uv run pytest` が通らない。コミットは下の手順の意味のまとまりごとに分け、各コミットの後で関係するテストを流す。
- 並べてよいもの：文書の書き直し（手順7）は、コードの撤去（手順3〜5）と独立に進めてよい。仕様のレビューの間に、テストの静的な分類（手順1）を進めてよい。

## 実装step

1. **テストの分類**（`design.md` の方法の1）：静的な印でテストのファイルを集め、`report.md` の一覧の下書きを作る。
2. **受け付けと振り分け**（テスト先行）：
   - Red：版3の宣言で50のコマンドが `CANONICAL_NOT_MIGRATED` で止まるテスト（`tests/cli_runtime/test_issue440_schema3_stops.py`）、版5が `PRECONDITION_FAILED` のままのテスト、`CANONICAL_NOT_MIGRATED` の次の1手が 0.4.2 を示すテスト。
   - Green：`project_context.py`（`WorkspaceNotMigrated`、`require_migrated`、`declares_schema_4`）、`runtime_dispatch.py` の振り分け、`canonical_errors.py` の `NOT_MIGRATED_RECOVERY`、`canonical_status.py` の main の判定。
   - 全体のテストを流し、失敗したテストを動的な印として一覧に足す（方法の2）。一覧を (a)、(b)、(c) に分ける（方法の3〜5）。
3. **(b) の書き直しと (a) の削除**：(b) ごとに、対応する canonical のテストを一覧に書く。ないものは `CanonicalWorld` で書き直す。(a) と移行のスクリプトのテストを消す。迷うテストは残して統括に `ask` する。
4. **コマンドと引数**（テスト先行）：
   - Red：G7 のテストを53のコマンドの形に直し、消したコマンドと引数が引数の誤りになるテストを足す。
   - Green：`cli/catalog.py`、`cli/options.py`、`canonical_dispatch.py`、`canonical_refusals.py` の削除、`canonical_worktrees.py`・`canonical_scope_read.py`・`canonical_writes.py`・`canonical_workspace.py` の拒否の分岐の削除、`canonical_errors.py` の2つのコードの削除。`--help` の文を canonical の動きだけにする。
5. **到達できないコードの削除**（`design.md` の到達の判定の方法）：モジュールの削除と vulture の繰り返し。消すたびに関係するテストを流す。`commit_tree.py` と `committed_validation.py` の `ls-tree` の重複を確かめる。
6. **雛形と名前の規則**（テスト先行）：
   - Red：配布資産の一覧のテスト（雛形の12ファイルと `epics.md`、`issues.md` がない、CUE の `report.md` に前付けの2行がない）、canonical の作成のファイルの見本のテストが変わらないこと。
   - Green：配布資産の削除、`templates/cue/*/report.md` の2行の削除、`copy_scope_template_at` と `domain/canonical_scaffold.py` の除去と書き換えの削除、`scope_scaffold.py` と `canonical_scope_create.py` の `epics.md`・`issues.md` の削除、`domain/ids.py` の slug と題名の規則の削除。
7. **文書**：README、配布する `spec-dock/docs/`、配布するスキル、`AGENTS.md`、`templates/README.md`、雛形の `.workbench/README.md`、`cli-redesign-guide.html` から従来モードの記述を消す。規則の節は Epic の10章の撤去の指示のとおりにする。`migration.md` に「## 0.5.0 への更新」の節（撤去の内容、#496、#497、上げる手順、版3のリポジトリの移し方と手順書の読み替え）を足し、版の節でない節を直す。文書の中身のテストを直す。Epic の `requirement.md`、`design.md`、`plan.md` の撤去の後の戻し先と、コマンドの数を直す（R-440-09、R-440-02）。
8. **移行のスクリプトと従来のCIの手順**：`scripts/migrate-to-canonical/` と `.github/scripts/specdock-ci-validate.sh` を消し、`run.sh` の `TARGETS` から外す。`tests/unit/test_static_analysis_script.py` など関係するテストを直す。
9. **版と配布資産の一覧**（テスト先行）：
   - Red：`tests/integration/test_issue440_release_0_5_0.py`（版、`migration.md` の節、`static-inventory.json` の既知の古い版、0.4.2 の配布資産からの `installation update`）。0.4.2 のバイトを `tests/fixtures/issue440/` に置く。
   - Green：`pyproject.toml`、`uv.lock`、版のファイルを 0.5.0 にし、`static-inventory.json` と退役の許可（`infra/static_assets.py`）を直す。`test_issue501_release_0_4_2.py` からは、前例（`5a7552b67`）と同じく版の置き場の確かめ（`test_the_version_is_0_4_2_in_every_place`）だけを消し、更新の経路のテストは残す。
10. **dogfood**：wheel を作って一時の venv に入れ、その `spec-dock installation update --target <この worktree> --backup-dir <一時> --yes` で spec-dock の配布資産を 0.5.0 に上げる。差分が、提供側の資産と同じバイトであることを確かめてコミットする（利用者の uv の tool の環境は変えない）。
11. **確かめ**：`make lint`、`uv run pytest`（全体）、wheel の確かめ（AC-440-09）、コードの検索（AC-440-03）。`report.md` を書く。
12. **レビュー**：コードのレビュー（`code-review`）、最終品質ゲート（`final-quality-gate`）。指摘を直し、合格の証拠を `report.md` に書く。
13. **PR**：`github-pr-creator` で PR を作り、`github-pr-checks` で CI の通過を確かめる。マージできる状態で止める。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-440-01 | `tests/cli_runtime/test_issue440_schema3_stops.py`（50のコマンド、`canonical check`、版5） |
| AC-440-02 | 直した `tests/cli_runtime/test_issue436_every_command.py` と、コマンドの数と一覧のテスト（`test_cli_vnext_contract.py`、`test_issue413_contract.py`、`test_cli_docs_vnext.py` など） |
| AC-440-03 | コードの検索のテストと、`report.md` の到達の判定と検索の結果 |
| AC-440-04 | 配布資産の一覧のテスト、canonical の作成の見本のテスト、`domain/ids.py` の名前がないことの検索 |
| AC-440-05 | 文書の中身のテスト（`test_issue436_docs.py`、`test_issue436_agent_rules.py` など） |
| AC-440-06 | 検索と `tests/unit/test_static_analysis_script.py` |
| AC-440-07 | `report.md` の一覧と、`make lint`、`uv run pytest` |
| AC-440-08 | `tests/integration/test_issue440_release_0_5_0.py` と dogfood の更新の結果 |
| AC-440-09 | wheel を作って一時の venv に入れた確かめ（テストの外。`report.md`） |
| AC-440-10 | Epic の文書と `migration.md` と次の1手の検索 |

- 従来モードの回帰（AC-15）は、この Issue で終わる。版3の動きを確かめていたテストは、(a) として消すか、(b) として canonical に移す。

## rollback

- マージの前：PR を閉じる。
- マージの後：PR を `git revert` するか、利用者の環境に 0.4.2 を入れ直す（`design.md` の「移行・互換性・rollback」）。各リポジトリの配布資産を 0.5.0 に上げた後なら、版のファイルを戻す PR も作る。

## モデルと推論

- 実装（この worker）：opus / xhigh（統括の依頼。strict の実装の opus/high から1段上げた。要件・設計・計画が雛形のままで、着手のときに Epic の材料から具体化するため）。
- 仕様のレビュー（`spec-review`、spec-reviewer）：opus / xhigh（統括の依頼）。
- コードのレビュー（`code-review`、code-reviewer）：opus / high（統括の依頼）。
- 最終品質ゲート（`final-quality-gate`、quality-gate-reviewer）：主 opus / xhigh、2人目 sonnet / high（統括の依頼。strict のため2人）。ChatGPT を使うスキルは無効なので使わない。

## exit / handoff

- 完了の条件：AC-440-01〜AC-440-10 を満たし、`make lint` と `uv run pytest` が通り、仕様のレビュー、コードのレビュー、最終品質ゲートに合格し、PR の CI が通り、PR がマージできる状態にある。
- 統括に渡すもの（Orca の `worker_done`）：PR の URL、最終の SHA、ゲートの結果、`report.md` のパス、テストの分類の一覧の場所。
- マージの後に統括が行うこと：`spec-dock work finish`、0.5.0 を利用者の環境に入れる、`release-tag.yml` の `v0.5.0` の確かめ、ほかの4つのリポジトリの `installation update` と PR、各 PR の検査のワークフローの 0.5.0 での通過（AC-20 の残り）。
- 残るリスク：vulture で見つからない消し残し（動きは変えない）。0.4.2 の雛形のままの Scope の作成（`report.md` に前付けの2行が残る）。
