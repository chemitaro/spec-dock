---
種別: レポート（Issue）
ID: "iss-00506"
関連GitHub: ["#506"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `scope close`／`scope reopen`：端末で確認したとき（`--yes` なし）、確認の後に直接の選択を読み直し、`(status, record, handle)` が変わっていれば `ValueError("direct selection changed during confirmation")` で止まる（`PRECONDITION_FAILED`、failed、終了コード3、effects 空、PATCH しない）。`canonical_writes.selection_unchanged` を足した。
- `scope create`：`WriteSession.require_same_repository()` と `RepositoryChanged`（`ValueError` の子、recovery 付き）を足し、確認の後（`ensure_labels` の前）、POST の直前、POST の後（親への追加の前）、親への追加の後（カタログへの公開の前）に `origin` を読み直す。
  - 何も書いていなければ `PRECONDITION_FAILED`（終了コード3）。種類のラベルを作った後なら `CANONICAL_WRITE_INCOMPLETE`（partial、終了コード6）。
  - POST の後なら `SCOPE_PUBLICATION_INCOMPLETE`（partial、終了コード6）、`github_ref` は確認したリポジトリの ref、残りの手順は `not_attempted`、recovery の先頭は「origin を確認したリポジトリに戻す」。
- 手本：`caaeebe45` の `direct_scope_lifecycle.py` と `direct_scope_publish.py`（文言とエラーのコードを合わせた）。
- コミット：`605f29e4a`（実装とテスト `tests/cli_runtime/test_issue506_reread_after_confirmation.py`、10件）。

### requirement.cue を直した理由

- `failures` に F-01（最後の読み直しと GitHub への書き込みの間の短い時間は守れない）を足した。epic-00512 の切り分けがこの Issue に F-01 を割り当てていて、設計の risks の根拠にするため。
- 仕様のレビューの P3 に従い、F-01 の recovery から「`--expect-current` でさらに狭く守れる」を外した（設計の動きでは効かないため）。

### 0.5.1 の `migration.md` に載せる契約の変更（#513 向け）

1. `scope close`／`scope reopen` を端末で確認したとき、確認の間に直接の選択が変わると `PRECONDITION_FAILED`（failed、終了コード3、effects 空）で止まり、GitHub に書かない。
2. `scope create` で、確認の後や POST の前に `origin` のリポジトリが変わると、Issue を作らずに止まる。何も書いていなければ `PRECONDITION_FAILED`（終了コード3）、種類のラベルを作った後なら `CANONICAL_WRITE_INCOMPLETE`（partial、終了コード6、effects は `github.label.create succeeded` と残りの `not_attempted`）。
3. `scope create` で、POST の後に `origin` のリポジトリが変わると `SCOPE_PUBLICATION_INCOMPLETE`（partial、終了コード6）で止まり、親への追加とカタログへの公開をしない。recovery の先頭に「origin を確認したリポジトリに戻す」案内が入る。

## Verification

| テスト | 確かめたこと | 結果 |
|---|---|---|
| T-01 | close（open から）／reopen（completed から）× `--expect-current` の有無で、確認の入力の間に選択を `epic-00002` に変えると、終了コード3・`PRECONDITION_FAILED`・書き込みなし・新しい記録が変わらない | 通過 |
| T-02 | 既存の `test_scope_close_accepts_a_terminal_confirmation_after_planning` と、`--yes` の close が今までどおり PATCH する | 通過 |
| T-03 | 確認の入力の間に `origin` を変えると、終了コード3・`PRECONDITION_FAILED`・GitHub の書き込みなし・カタログが変わらない | 通過 |
| T-04／T-05 | POST の間に `origin` を変えると（親あり・なし）、終了コード6・`SCOPE_PUBLICATION_INCOMPLETE`、`github-create succeeded`、残りが `not_attempted`、POST 1回、sub-issue の書き込みなし、カタログと changeset なし、recovery の先頭が origin の案内 | 通過 |
| T-07 | ラベルの作成の後・POST の前に `origin` を変えると、終了コード6・`CANONICAL_WRITE_INCOMPLETE`、Issue の POST なし | 通過 |
| T-08 | 親への追加の間に `origin` を変えると、`github.sub-issue.add succeeded`・`scaffold not_attempted`・終了コード6、カタログなし | 通過 |
| T-06 | 既存の scope の作成・変更のテスト（127件）と全体 | 通過 |

- Red：実装の前に新しいテスト10件のうち9件が落ちた（`--yes` の close の1件だけ通った）。
- 仕様のレビュー（`spec-review`、spec-reviewer opus/high）：1回目で合格（P0・P1 なし、P2 2件、P3 2件。requirement `9b095b64…`、design `42ff14f3…`、plan `f38fb80b…`）。P2・P3 も直した（T-07・T-08 の追加、compatibility の書き足し、recovery の理由の訂正、F-01 の recovery の訂正。直した後の sha256：requirement `084a4a41…`、design `b7d5355e…`）。記録：`.workbench/spec-review/iss-00506/`。
- コードのレビュー（`code-review`、code-reviewer opus/high、axis both、`3156ac15c..605f29e4a`）：合格、指摘なし。記録：`.workbench/code-review/iss-00506/round-1.json`。
- 最終品質ゲート（`final-quality-gate`、campaign `iss-00506-fqg-1`、quality-gate-reviewer opus/high 1人、ChatGPT のゲートは無効）：合格の commit `605f29e4aba8aa7a8b278ad9b0f1c58dcb3022c4`（1回目で合格）。レビューの道 pass（網羅、P0・P1・P2 なし、P3 1件）。テストの道 pass：`uv run pytest -q -p no:cacheprovider` 終了コード0（3268 passed、7 skipped、1748秒）、`make lint` 終了コード0（ruff check、ruff format check、mypy すべて pass）。記録：`.workbench/final-quality-gate/iss-00506-fqg-1/closure.md`。

## Residual Risks / Follow-ups

- F-01：最後の読み直しから GitHub の要求までの短い間の変化は守れない（design の risks）。
- FQG-001（P3）：確認の直後（`ensure_labels` の前）の読み直しを単独で守るテストはない。ラベルがある世界では POST の直前の読み直しが同じ結果を返すため。
- `scope import github` は確認を問わないので、読み直しを足していない（要件の外）。
- #520 が同じ `lifecycle_scope` を直す。後にマージするほうが main を取り込む。
- `spec-dock work finish` はマージの後に統括が行う。
