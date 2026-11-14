---
種別: レポート（Issue）
ID: "iss-00589"
関連GitHub: ["#589"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

## レビュー記録

- round-1（spec-reviewer opus / high）：不合格（P1 1・P2 2・P3 1）。`.workbench/spec-review/iss-00589/round-1.json`、検査 `round-1.check.json`。対応 `review-response.md`（説明資料の帯と余白の寸法、誤りの帯の高さの測り、枠の flex の効く範囲、リンクを印だけに）。
- round-2（同じレビュアー）：**合格**。P0〜P3 なし。`round-2.json`、検査 `round-2.check.json`（valid、status pass）。
- 合格した文書の sha256：requirement.cue `ad2eae3c40c5636d2b5d00467a59e36f1d989e081eb0d56d2848b43a3a81ebb5`、design.cue `3070c360a832b7f3128b16a670e20e81ad2c39b0ea0d476390b5b29e8b02450a`、plan.cue `7186130c5d8ccf338160f41a3fa81b0e7fdd119e4ae88d2565656eeadfa6b7ca`。
- 結果の場所：worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00589` の `.workbench/spec-review/iss-00589/`。

## 直す前の写し

開始のコミット 7e50ac583 から作った隔離の venv（`.workbench/iss-00589/venv-before`、ポート 18589、状態の置き場の写し `.workbench/iss-00589/state`）で、`.workbench/iss-00589/shoot.mjs` で撮って測った（`shots/before/`、測り `shots/before/measure.json`）。Scope は epic-00573。

| 場面 | 枠の上端（中身の上端から） | 枠の高さ | 最初に見える高さ | 欄に対する割合（見える高さ） | 中身のスクロール |
|---|---|---|---|---|---|
| 欄 1440 文書 | 359px | 630px | 178px | 21.6% | あり（二重） |
| 欄 1000 文書 | 475px | 560px | 0px | 0% | あり（二重） |
| 欄 1440 説明資料 | 38px | 488px | 488px | 59.3% | なし |
| 欄 1000 説明資料 | 38px | 348px | 348px | 48.1% | なし |
| シート 390 全体 文書 | — | 591px | 213px | 25.3% | あり（二重） |
| シート 390 全体 説明資料 | — | 652px | 652px | 77.3% | なし |
| 詳しい画面 1440 文書 | 229px | 702px | 317px（画面の中） | — | ページ |
| 詳しい画面 1000 文書 | 229px | 624px | 183px | — | ページ |
| 詳しい画面 1440 説明資料 | 48px | 680px | 498px | — | ページ |

写し：`panel-docs-1440.png`、`panel-docs-1000.png`、`panel-explanation-1440.png`、`panel-explanation-1000.png`、`sheet-full-docs-390.png`、`sheet-full-explanation-390.png`、`page-docs-1440.png`、`page-docs-1000.png`、`page-explanation-1440.png`、`page-explanation-1000.png`、`page-summary-1440.png`。文書のタブの上は「検査の誤りなし」の帯と、3枚の札（要件・設計・計画、説明資料、報告）。

## 実装の記録

## Outcome

## 逸脱と判断

## Verification

## Residual Risks / Follow-ups
