---
種別: レポート（Issue）
ID: "iss-00627"
関連GitHub: ["#627"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## 原因（測り、2026-11-17、開始のコミット 5c0ebb916）

測りの道具：`.workbench/iss-00627/tools/probe.mjs`（headless Chrome、倍率 100%、稼働の印の後に、layout の矩形と DOM の矩形を箱・枠ごとに比べ、同じ入力（構造・稼働の印の測った幅・見える幅）で node の routeLayout と audit も走らせる）。状態の置き場は iss-00614 の写し、試しのサーバーは 127.0.0.1 の別のポート。

### (A) 枠の見出しの実寸と見込みのずれ（DOM の側）

| 枠 | 見込み（layout） | 実寸（DOM） | 差 |
|---|---|---|---|
| Initiative | 上 16（縁4+余白12）+ 題名の行 22 + 6 + 要約の行 18 = 62 | 16 + 25.59（16px × 1.6）+ 6 + 19.19 = 66.78 | +4.78 |
| Epic | 上 9 + 22 + 6 + 18 = 55 | 縁 1 + 余白 9 + 21.59（13.5px × 1.6）+ 6 + 19.19 = 56.78 | +1.78 |
| 縮めた Epic（題名1行） | 高さ 67（固定） | 中身 69.45 | +2.45（はみ出し） |
| 縮めた Epic（題名2行） | 高さ 67（固定） | 中身 約 87 | +20（はみ出し） |

要約の行の 19.19 は `.frac`・`.cnts`（12px × 1.6）。箱（`.gx-box`）は中身の下端 84.25 で高さ 88 に収まり、ずれはない（稼働の印の行のある箱も 104.25 / 108）。
housing-lifecycle『全体』1440 の boxHits 6（`box r9#1 n:epic-00004` など）は、Epic の見出しの 1.78px の帯を通る線。
edgeAudit は縮めた枠を枠の矩形で測るので、はみ出しは数えない（線がはみ出した題名の上を通りうる）。
見出しが見込みより低い枠（−4.2・−20.2）は、線の口のために layout が見出しの障害物を高くした（grow）分で、ずれではない。

### (B) 線の通り道の計算そのもの（node でも再現）

taikyohiyou_project の overlaps は、DOM なしで、ページで測った稼働の印の幅を入れた routeLayout の audit に同じ数だけある（『いま』360：8、『全体』1312：2、1424：2、872：1、360：1）。iss-00614 の node の audit が0だったのは、稼働の印なし（箱の高さが違う入力）だったため。router.js の寄せの3つの不具合：

1. 範囲の広い線分（160px より広い通り道、iss-00578）は目指す範囲を A* の位置1点に縮める。束の並びの比べ `cmp` が、動かない線分との前後をこの1点で決めるので、広い線分が動かない線分の手前に並び、そこから動けずに重なる。`lacking()` は広い線分の不足を申告しないので、配置は『足りている』と判断して終わる（『いま』360：iters 6、problems 0、overlaps 8）。
2. 入口の辺に S（8px）おきに並ぶ動かない線分（櫛、iss-00578 の細かい入口）の間に動く線分が挟まり、並べ替えの手当て（12回）も合計が減らずに戻る（『全体』1312 の r335#2 が r320#2 と同じ高さ）。
3. 入口にその線だけのとき入口を出口の高さにそろえる規則が、向かいの箱の出口と同じ高さに入口を置く（『全体』1424 の r145#4 と r164#0、稼働の印なしの 1424 の overlaps 1 もこれ）。

試作（`.workbench/iss-00627/dbg/`）で 1〜3 を直すと、6つの入力で違反0、240 組の node の比べで悪化0。

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 不合格（P1 1：R-01 の受入が線の口の伸び grow のある枠で満たせない、P2 1：縮めた枠の測りの切り上げで1行の枠も 1px 高くなりうる、P3 5）→ 直した（`.workbench/spec-review/iss-00627/review-response.md`）。round-2 **合格**（P0〜P3 すべて0）。結果 `.workbench/spec-review/iss-00627/round-{1,2}.json` と `.check.json`（reviewed_sha `cc40aa708`）。
- **合格した文書の sha256**：requirement.cue `7d410cf6e28c9a5f0b2076af31eceb895a761e979fde2ca396dd8306e4e73c87`、design.cue `755e247a4b04b68fb9e9d2da595a4a2328f25d4b38f10e0dfc2d59e93c218d33`、plan.cue `0369b05ef4b513530390cdde04bcd8500570b0cfe1079ccf3e55a6c2764dcf84`。
- 合格の後の変更：plan.cue の手順の status、design.cue D-03 に `tallNeeds`（compactHeight より高い測りの値だけを heads に残す）を足した（実装で、allgraph.js のリポジトリの印が測るたびに変わり配置をやり直すのを避けるため。判断の意味は同じ）。

## 実装の記録

- 開始のコミット `5c0ebb916`（origin/main）。基準の `uv run pytest tests/unit/presentation/test_dashboard_graph_js.py` 合格。
- S-01 `cc40aa708`（タスク担当）：`tests/fixtures/issue627/route_inputs.json`。この PC の状態の置き場の写しから、受入の組の routeLayout の入力（構造・稼働の印の測った幅・見える幅・範囲）を取り、title を Scope の ID、cleanup の text を code に置き換え、配置に使わない項目を落とした（2つの構造、6つの case）。伏せる前と同じ違反の数（product の5 case：8・1・1・2・2、business 0）を node で確かめた。
- 逸脱 codex-symlink-refusal：S-02 の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_0af00414f153、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink（UnsupportedOperation）で手元のコマンドを起動できず、変更なしで止まった（worker_done failed）。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium に切り替え、同じ値のタスク担当のこのセッションが S-02 を行った（別のセッションは起こしていない）。
- S-02（Claude Opus 5.5 / medium、このセッション）：Red `b909221b1`（`tests/js/dashboard_graph_route_fix.mjs`・`test_dashboard_graph_route_fix.py`、T-01・T-02 の6件が落ちる）→ Green `fe50a2dc8`（router.js の D-04・D-05、8 passed）。経路が変わった stored の『全体』の1組（世界が 6px 広い、違反は前後とも0）について、iss-00614 の写し（`graph_dom_golden.json`、docstring の手順で書き直し、ほかの run は同じ）と iss-00603 の digest（`layout-before.json` の `spec-dock|all|nest|all|None|routed` の1つ、注記の鍵 `iss-00627` を足した）を記録し直した。
- S-03（Claude Opus 5.5 / medium、このセッション）：Red `44c7973d5`（`tests/js/dashboard_graph_fit.mjs`・`test_dashboard_graph_fit.py`、6件が落ちる）→ Green `10610ce89`（graph.css D-01、layout.js D-02 の `compactHeight` と `heads`、measure.js D-03 の `compactNeeds`・`tallNeeds`・`headsDiffer`、graph.js と allgraph.js の checkRows）。iss-00620 の静的な検査（`test_the_graph_measures_the_marks_and_lays_out_again_only_when_the_rows_change`）の `if (!M) return;`・`V.marks = M;` を、測れないときは何もしない同じ契約の新しい文（`if (!M && !H) return;`・`if (M) V.marks = M;`）に直した。
- 節目の検証：`uv run pytest tests/unit/presentation/ -k "graph or allgraph" tests/unit/infra -k dashboard`（317 passed の後、上の1件を直して全部合格）、`make lint` pass。static-inventory.json は dashboard の資産を持たないので変わらない。

## 最終品質ゲート

- キャンペーン iss-00627-fqg-1（quality-gate-reviewer opus / medium、second opinion なし、範囲 `5c0ebb916..HEAD`、観点 functional-correctness・requirements-closure・test-adequacy・compatibility-regression、test_commands `make lint`・`uv run pytest`）：attempt 01（`10610ce89`）で **合格**。review lane P0〜P3 0、coverage complete。`make lint` exit 0、`uv run pytest` exit 0（4066 passed、7 skipped）。closure は worktree の `.workbench/final-quality-gate/iss-00627-fqg-1/closure.md`。
- 計画の観点 ui-behavior は観点の一覧にないので compatibility-regression に置き換えた（campaign に記録）。
- 検証の時、実行中に書き足した plan.cue の status と report.md のため authority の sha256 が合わず機械の失敗になった。固めた時点の内容（足した部分を除くとバイトまで一致）を一時的に戻して検証し、戻した（closure.md に記録）。

## 実機の確かめ（S-05、タスク担当）

- 試しのサーバー：この worktree の `10610ce89` の wheel を隔離した venv（`.workbench/iss-00627/venv`）に入れ、この PC の状態の置き場の写し（`.workbench/iss-00627/state`、iss-00614 の写しから）と `XDG_CONFIG_HOME` の試しの設定（`orca_web.port` 18727）で `spec-dock dashboard serve --offline --tailscale --port 18627`。試しの orca は `relay_orca.py`（GET だけで常駐の orca-web を中継し CORS の頭を足す）を 127.0.0.1 と tailnet の 18727 に。常駐の 47800 と 8791、道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）、倍率 100%、稼働の印の後（`.workbench/iss-00627/tools/fitscan.mjs`、数字は [accept.json](artifacts/20261116t235826z-02--accept.json)）。

| 画面 | 組 | edgeAudit の違反 | 縮めた枠のはみ出し | 見出しの差の最大 |
|---|---|---|---|---|
| housing-lifecycle 単体 | 1440・1000・390 × 全体・いま・これから × 明・暗（18） | すべて0 | 0 | 0px |
| taikyohiyou_project 単体 | 同じ 18 組 | すべて0 | 0 | 0px |
| 横断の構造 `/graph` | 同じ 18 組 | すべて0（total） | 0 | 0px |

  違反は boxHits・ownHits・overlaps・diagonal・portShare・failed・missing・markOverflow・trunkOverlaps。直す前（iss-00614 の試しのサーバー 18614、同じ状態の写し）は、housing-lifecycle『全体』1440 で boxHits 6、taikyohiyou の『全体』で overlaps 1〜2、縮めた枠のはみ出し 2〜37、見出しの差 4.78px。
- 再現の組（taikyohiyou_project、窓 376・見える幅 360、『いま』、稼働の印 26）：直す前 overlaps 8 → 直した後 0（`.workbench/iss-00627/probe/repro-after.json`）。
- R-05：直す前（`5c0ebb916` の資産）と後の node の比べ、Scope のある 8 つのリポジトリ × 入れ子 27 ＋ 木 3 = 240 組：違反の増えた組 0、減った組 7、経路が同じ組 199、変わった組 41（違反なしのまま経路だけ変わったものを含む）、直した後に違反が残るのは木の表示の taikyohiyou『全体』（9 → 9、範囲の外）だけ（[sweep-240.txt](artifacts/20261116t235826z-03--sweep-240.txt)）。
- 写し（倍率 100%、題名の行と2行の縮めた枠）：直す前 [縮めた枠 1440 明](artifacts/20261116t235824z--before-compact2-1440-light.png)（2行の題名の枠で要約の行が下の縁に重なる）→ 直した後 [縮めた枠 1440 明](artifacts/20261116t235824z-01--after-compact2-1440-light.png)（枠が中身の高さに伸びる）。題名の行：直す前 [Initiative 1440 明](artifacts/20261116t235825z--before-initiative-1440-light.png) → 直した後 [1440 明](artifacts/20261116t235825z-01--after-initiative-1440-light.png)、[1440 暗](artifacts/20261116t235825z-02--after-initiative-1440-dark.png)、[390 明](artifacts/20261116t235825z-03--after-initiative-390-light.png)、[390 暗](artifacts/20261116t235826z--after-initiative-390-dark.png)、[縮めた枠 390 暗](artifacts/20261116t235826z-01--after-compact2-390-dark.png)。Initiative の題名（16px、行 22px）と Epic の日本語の題名（例『CI の実行時間の短縮』）は、明暗・1440・390 で上下が切れない。見た目の変化：Initiative の題名の行が 3.6px、要約の行が 1.2px 詰まり、Epic の見出しが 1px 上がる。2行の縮めた枠は中身の高さまで伸びる。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18627 番（`/graph` と `/r/<repo>/`。URL は統括への報告で伝える）。止め方：`kill $(lsof -tnP -iTCP:18627 -sTCP:LISTEN) $(lsof -tnP -iTCP:18727 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。

## 次の提案

- 木の表示（mode tree）の taikyohiyou_project『全体』の線の違反 9（overlaps。直す前から同じ数で、曲がりの多い長い線どうし）：統括が別の Issue にする（統括の決定 msg_61e7c3c8f34f）。
- 計画の観点 ui-behavior は最終品質ゲートの観点の一覧にないので、compatibility-regression に置き換えた（iss-00620 の計画も同じ名を使っている。方針の観点の名をそろえるとよい）。

## Outcome

## Verification

## Residual Risks / Follow-ups
