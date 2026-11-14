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
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `7e50ac583..881280ed3`、観点 functional-correctness・requirements-closure・test-adequacy・security-baseline）：**合格**（attempt 1）。P0〜P3 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3801 passed / 7 skipped）。closure `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00589/.workbench/final-quality-gate/iss-00589-fqg-1/closure.md`。
- 注：plan.cue は合格の後、手順の status だけを書き換えている（中身は合格のまま）。

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

注：直す後を撮る前に、状態の置き場を写し直して（`rsync`、2026-11-14）、直す前と後を同じ状態で撮り直した（最初の写しが古く、上に「構造が1時間前から更新されていません」の知らせが出て欄が 101px 低くなったため）。表の値は撮り直したもの。

## 直した後の写し（S-03、タスク担当）

コミット 881280ed3 から作った隔離の venv（`.workbench/iss-00589/venv-after`、ポート 18590、`--tailscale`、同じ状態の置き場の写し）で、同じ `shoot.mjs` で撮って測った（`shots/after/`、測り `shots/after/measure.json`）。

**本人がスマホで見られる URL（tailnet）**：http://100.85.74.8:18590/r/github.com/chemitaro/spec-dock/ （構造の図で epic-00573 の枠の見出しを押し、欄の「文書」「説明資料」のタブ。スマホでは取っ手を押すと全体の段）

| 場面 | 枠の上端（中身の上端から） | 枠の高さ | 最初に見える高さ（前 → 後） | 欄に対する割合（前 → 後） | 枠の下端と中身の下端の差 | 中身のスクロール |
|---|---|---|---|---|---|---|
| 欄 1440 文書 | 359 → **30px** | 630 → 496px | 178 → **496px** | 21.6% → **60.3%** | 10px | あり → なし |
| 欄 1000 文書 | 475 → **30px** | 560 → 356px | 0 → **356px** | 0% → **49.2%** | 10px | あり → なし |
| 欄 1440 説明資料 | 38 → **30px** | 488 → 496px | 488 → 496px | 59.3% → 60.3% | 10px | なし |
| 欄 1000 説明資料 | 38 → **30px** | 348 → 356px | 348 → 356px | 48.1% → 49.2% | 10px | なし |
| シート 390 全体 文書 | 475 → **28px** | 591 → 656px | 213 → **656px** | 25.3% → **77.7%** | 4px | あり → なし |
| シート 390 全体 説明資料 | 30 → 28px | 652 → **656px** | 652 → 656px | 77.3% → 77.7% | 4px | なし |
| 詳しい画面 1440 文書 | 229 → **44px** | 702 → **780px**（900 − 120） | 317 → 502px | — | — | ページ |
| 詳しい画面 1000 文書 | 229 → **44px** | 624 → **680px**（800 − 120） | 183 → 367px | — | — | ページ |
| 詳しい画面 1440 説明資料 | 48 → 44px | 680 → 780px | 498 → 502px | — | — | ページ |
| 詳しい画面 1000 説明資料 | 48 → 44px | 580 → 680px | 363 → 367px | — | — | ページ |

- 帯の行の高さ：どの場面も 24px（R-02 の 32px 以下、R-05 の 24px 以下）。セグメントの項目は「仕様」「報告」の2つ（説明資料なし、`.sd-doc` の札 0）。右端のリンクは印だけで、href は選んでいる文書の view（`/r/…/scopes/epic-00573/doc`）、target `_blank`。
- 詳しい画面：枠 780px ≥ 900 − 150、帯 24 ＋ 枠 780 = 804 ≤ 900（1440）。枠 680 ≥ 800 − 150、704 ≤ 800（1000）。
- 欄で「報告」を押す：location.href は `/r/github.com/chemitaro/spec-dock/` のまま、枠の src が `/r/github.com/chemitaro/spec-dock/scopes/epic-00573/doc/report.md`、aria-current が「報告」（`panel-docs-report-1440.png`）。
- 誤りの帯（R-03）：実データの Scope に誤りのあるものがないので、配った scope_tabs.js を import し、誤り3件・警告1件（長い文）の check で docsTab を描いて、その帯を欄の中身に差し込んで測った。閉じた高さは 1000 と 390 の全体の段のどちらも **28px**（1行、はみ出しは省略）。390 では枠が 624px で中身はスクロールしない。1000 では、帯 28 ＋ 帯の行 24 ＋ 枠 324px で中身はスクロールしない（`panel-docs-errors-1000.png`、`sheet-full-docs-errors-390.png`）。誤り 0 件の epic-00573 では check- の帯は出ない。
- 計画の進み具合：文書のタブにない。概要のタブにある（手順を持つ iss-00589 の詳しい画面の概要で「計画の進み具合 2／3 終わった」、`shots/after-iss/page-summary-1440.png`）。epic-00573 は計画の手順を持たないので、直す前も後も出ない。

写し：`shots/after/` に、直す前と同じ名前の11枚と、`panel-docs-errors-1000.png`、`sheet-full-docs-errors-390.png`、`panel-docs-report-1440.png`。

## 実装の記録

- S-01（6f067a753）：scope_tabs.js の docsTab・documentEntries・checkResults・explanationTab・DOC_INFO。node のテスト T-01〜T-03 を先に書いて落ちることを確かめた。test_dashboard_documents.py の目印を合わせた。
- S-02（881280ed3）：scope_tabs.css・panel.css・scope.css。静的なテスト T-04。
- S-03（タスク担当）：実データの写しと測り（上の表）、tailnet のサーバー。

## Outcome

実装担当：impl-ui（S-01・S-02）claude opus / medium（dispatch ctx_488bf91291e0、launch.effective claude・opus・medium）。Codex の手順はなし（データの形・API の変更がなく、計画の execution に理由を記録）。S-03 はタスク担当（opus / medium）。

## 逸脱と判断

- 実装担当の開始のコミットの pytest の基準線は、走らせている間に作業の木を編集したため無効になった（lint は合格）。HEAD で失敗 0 なので、既存の失敗の区別は要らない。
- 実装担当が、git-autocommit が付けなかった Co-Authored-By を、未公開の2つのコミットに amend で足した（公開前）。
- 最初の状態の写しが古く、知らせの帯で欄が低くなったので、状態を写し直して直す前と後を撮り直した。
- 誤りの帯の高さは、実データに誤りのある Scope がないので、配った scope_tabs.js で描いた帯を差し込んで測った（設計 D-07 のとおり）。
- 後の提案：欄の見出し（状態、題名、理由、道筋）とタブの帯が PC の欄で約 234px を取る。全体の段のスマホと同じように、文書・説明資料のタブでは見出しを1行に畳む選択肢がある（今回は範囲外）。

## Verification

## Residual Risks / Follow-ups
