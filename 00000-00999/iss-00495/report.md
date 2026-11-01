---
種別: レポート（Issue）
ID: "iss-00495"
関連GitHub: ["#495"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

要件の変更（R-01）：元の案「`export-legacy` が戻すか一覧を示す」はコードを直す案だった。利用者の決定（2026-11-01）で範囲を README だけにした（道具は 0.5.0 の撤去で消え、戻しは `v0.3.0` のタグのスクリプトで行うため、一度きりの道具のコードは直さない）。そのため R-01 を「README に手で戻す手順を書く」に直した。

## Verification

- 仕様レビュー（opus/medium）：2周で P0〜P3 なし。
- コードレビュー（sonnet/high）：P0〜P3 なし。
- 最終品質ゲート（opus/high）：コミット 2fb140a1b、レビュー pass（P0/P1/P2/P3 = 0）。`make lint` と `uv run pytest`（4052 passed, 8 skipped）が同じコミットで成功。
- 追加のテスト：`tests/integration/migration/test_migrate_plan.py::test_the_readme_documents_the_gaps_found_in_the_i12_cutover`。

## Residual Risks / Follow-ups

- コードは直していない（道具は 0.5.0 の撤去で消える）。ツリーの外のリンクの手での戻しは、README の手順に従う。
