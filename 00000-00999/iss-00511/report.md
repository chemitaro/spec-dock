---
種別: レポート（Issue）
ID: "iss-00511"
関連GitHub: ["#511"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- README の「全N コマンド」を 53 に直し、固定のしかたを文の数字ではなく `cli.catalog.LEAF_ARGUMENTS` の数から確かめるテストにした（D-06）。`docs/github-issue-integration.md` の local backend の記述を直し、`pyproject.toml` の package-data から外した `templates/{initiative,epic,issue}/.workbench/README.md` の3行を外した。
- `tests/unit/infra/test_issue511_docs_and_templates.py`：撤去した案内（`workspace migrate`、`workbench copy`、`--ci`、`--source local`、`.meta.json`）が、`src/spec_dock/assets/` の配布する文書の全体で、許可の表（migration.md の 0.5.0 の節、canonical.md の撤去の注記、`.meta.json` を検出として説明する4文書）の外に現れないことを確かめる。許可が古くなったら失敗する。
- `tests/cli_runtime/test_issue511_report_bytes.py` と `tests/fixtures/issue511/`：`scope create` が作る `report.md`（3種類）が、0.4.2 の出力（`git show v0.4.2:` の雛形に 0.4.2 の手順を当てて再現）とバイトで一致する。0.4.2 は実行時に `タイトル:` `親:` の行を落とし、0.5.0 は雛形から外しただけで、出力は同じ。
- R-03：`canonical check` の `_declaration_failure` が重複キー（入れ子を含む）を `WORKSPACE_DECLARATION_INVALID`（`details.reason=duplicate-member`）の1件にする。`project_context._unique_members` は非公開で編集範囲の外なので、同じ6行の hook を `canonical_check.py` に持った。**契約の変更**：新しいエラーのコードはなく、終了コードは既存の値のまま。版3で重複キーがある宣言は `WORKSPACE_NOT_MIGRATED` でなくこの失敗になる。
- 配布する文書（`src/spec_dock/assets/`）の本文は変えていないので、`static-inventory.json` と dogfood の写しは更新不要（S-05 は変更なしで完了）。
- 候補14（入れたコンソールでの `work start`／`work finish` の e2e）は足さない。本物の定期の実行（GitHub と定期のカタログの同期）に触れずに子のプロセスで動かす手段がなく、足すとテストが利用者の環境に作用するため。`work start`／`work finish` はプロセス内のテストと、入れたコンソールでの読むコマンド・`workspace sync` で確かめる。
- `requirement.cue` は変えていない。

実装コミット：a58bbf1ce（base 9221c08df）。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：合格（P0/P1 なし、P2 1件・P3 1件）。P2（D-02 の許可の表が今の出現と合わない）と P3（重複キーは版3にも及ぶ）は design.cue に反映した。
- Red：新しいテストは直す前に、README の数・文書・package-data・重複キー3件が失敗することを確かめた。撤去の不在とバイトのテストは、今の状態を固定する回帰の守り（直す前から通る）。
- コードのレビュー（code-reviewer sonnet/high）：合格（指摘 0）。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、`.workbench/final-quality-gate/iss-00511/`）：a58bbf1ce で合格。P0/P1 0、coverage_complete、P3 1件（FQG-001：`.meta.json` を作る指示の文型の正規表現が「書く」などの活用を捕まえない。今の文書に該当行はなく、表の外は別に0件で守られるため、直さない）。
- テスト lane（a58bbf1ce）：`make lint` 合格（ruff check、ruff format、mypy）、`uv run pytest` 3285 passed / 7 skipped（exit 0）。

## Residual Risks / Follow-ups

- #513 が `migration.md` の 0.5.1 の節に載せる契約の変更：`canonical check` が、重複したキーを持つ `spec-dock/workspace.json`（入れ子を含む。版3でも）を `WORKSPACE_DECLARATION_INVALID`（`details.reason=duplicate-member`）の失敗の1件にする。コマンド・引数・終了コード・JSON の形は変わらず、`reason` の値が1つ増える。
- FQG-001（P3）：禁止の語の文型の検出は、許可した4文書の中で「書いてください」などを見逃す。
