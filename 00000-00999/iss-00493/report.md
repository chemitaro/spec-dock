---
種別: レポート（Issue）
ID: "iss-00493"
関連GitHub: ["#493"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

OS が作る不要なファイル（`.DS_Store`、`._*`、`Icon\r`、`Thumbs.db`、`ehthumbs.db`、`ehthumbs_vista.db`、`desktop.ini`、`.directory`）を、カタログの同期が新しく保存しないようにした。カタログの `.gitignore` は変えず、同期の規則（`canonical_sync_rules.is_os_junk`）で除くので、パッケージを更新するだけで、既存の5つのカタログにも効く（カタログには何も書かない）。

- 同期の保存（`canonical_sync._save`）：まだツリーにない不要なファイルを候補から外す。ツリーにあるものの変更と削除は保存する。
- 未保存の数（`canonical_git.catalog_change_summary`）と `work finish` の確かめ（`canonical_work._unsaved_places`）：未追跡の不要なファイルを数えない。
- `canonical status`：`changes.junk_files` と、消し方の次の1手。
- 大量の削除の保留（`classify_holds`）：不要なファイルの削除を数えない。
- `canonical remove`：残った不要なファイルを `CANONICAL_IGNORED_FILES_PRESENT` で名指して止まる。
- 配布の文書 `spec-dock/docs/canonical.md`（提供側と dogfood）と `static-inventory.json`。

実装のコミット：`f9bdded67`（`feat(canonical): OS由来の不要ファイルを同期対象から除外`）。

## 要件を足した理由

統括が書いた `requirement.cue` の R-01、R-02 に、実装担当が R-03、R-04、F-01 を足した。カタログの `.gitignore` ではなく同期の規則で除外する設計（design.cue の compatibility）にしたため、同期の規則が保存しないファイルが、ほかの経路でどう見えるかを決める必要が出た。

- R-03：保存しないファイルを未保存と数え続けると、Finder が Scope のフォルダーに `.DS_Store` を作るたびに、`work finish` の保存の確かめ（`canonical_work._unsaved_places`）が最大180秒待って `CANONICAL_SAVE_UNCONFIRMED` で止まる。`canonical status` の `changes.unsaved` も 0 にならない。
- R-04：R-02 の案内で保存済みの不要なファイルをまとめて消すと、大量の削除の保留（20件以上、または5件以上かつ1割以上）に当たり、`canonical accept --deletions` が要る。不要なファイルの削除は仕様の中身を失わないので、数えない。
- F-01：未保存と数えなくなると、`canonical remove` の未保存の確かめを通り抜け、`git worktree remove`（`--force` なし）が未追跡のファイルで失敗する。リンクなどを消す前に止める必要がある。

## 仕様のレビュー

- 1回目（2026-11-01、spec-reviewer opus/high）：合格。P0 0、P1 0、P2 1、P3 2。結果は Workbench の `.workbench/spec-review/iss-00493/round-1.json`。
  - P2（未追跡の不要なファイルが、取り込む変更と重なると取り込みを待ち続ける。新しい版どうしでも起きうる）：design.cue の risks を正確に書き直し、範囲の外として残した（手元の不要なファイルを消せば進む）。
  - P3（R-04 の「削除が保存される」のテストがない）：T-05 に同期での確かめを足した。
  - P3（この節がなかった）：この節を書いた。

## Verification

- TDD：T-01〜T-06 を先に書き、意図した理由で赤になることを確かめてから実装した（T-04 は `CANONICAL_SAVE_UNCONFIRMED`、T-06 は `git worktree remove` の途中の失敗で赤）。
- コードのレビュー（code-review、code-reviewer opus/high、規約と仕様の2人、`627a48075..f9bdded67`）：どちらも合格、指摘なし。
- 最終品質ゲート（final-quality-gate、キャンペーン `iss-00493-fqg-1`、quality-gate-reviewer opus/high 1人、試行1回）：`f9bdded67` で合格。
  - 審査役の枠：pass、観点（functional-correctness、requirements-closure、test-adequacy）すべて complete、P0〜P3 なし。
  - テストの枠：`make lint` exit 0（ruff check、ruff format、mypy が合格）、`uv run pytest` exit 0（4083 passed、8 skipped）。
  - 証拠：Workbench の `.workbench/final-quality-gate/iss-00493-fqg-1/closure.md`、`attempts/01/review.json`、`attempts/01/tests/manifest.json` と各 `.check.json`。
- ChatGPT を使うレビューは無効のため使っていない（統括の指示）。
- `main`（#498、移行の README とテストだけ）を取り込んだ（`f94068728`、衝突なし）。
- PR：https://github.com/chemitaro/spec-dock/pull/499（head `f94068728`）。CI（Provider CI、SpecDock check、Commit identity）は合格、GitHub の状態は MERGEABLE・CLEAN（2026-11-01T14:10Z の観測）。マージと `work finish` は統括が行う。

## Residual Risks / Follow-ups

- 取り込む変更がある不要なファイルのパスに、手元の未追跡の不要なファイルがあると、取り込みは `blocking`（`local_edit`）で待ち続ける。手元のファイルを消せば進む。自動で消して取り込む扱いは別の Issue の候補。
