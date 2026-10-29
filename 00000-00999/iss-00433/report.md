---
種別: レポート（Issue）
ID: "iss-00433"
タイトル: "Accept Japanese Titles In Canonical Mode"
関連GitHub: ["#433"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

実装せずに、not planned で閉じた（2026-10-29）。利用者が slug を廃止し、ID・ディレクトリ名・ブランチ名を `<種類>-<番号5桁>` にすると決めたため、この Issue の中身は、canonical モードの `scope create`、`scope import github`、`scope edit` の題名の検査（空でない、制御文字を含まない、256文字以下）だけになった。それは同じコマンドを作る I-5（`iss-00432`）に移した（統括の判断。Epic の `plan.md` の I-5 と I-6 の節、`design.md` の「設計の判断」）。

## Verification

## Residual Risks / Follow-ups
