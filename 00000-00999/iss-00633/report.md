---
種別: レポート（Issue）
ID: "iss-00633"
関連GitHub: ["#633"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## 原因（測り、2026-11-17、開始のコミット 3f5f8d8e9）

測りの道具（iss-00627 の道具は worktree とともに消えていたので作り直した）：`.workbench/iss-00633/tools/`。
`case.mjs`（1組の routeLayout と audit、経路の digest）、`sweep.py`（直す前と後の資産で 300 組を比べる）、`diag.mjs`（違反の線の座標と巡ごとの違反の数）、`stair.mjs`（route(G) の小さな通り道）。
構造は、この PC の状態の置き場の写し（`.workbench/iss-00633/state`）を installed の `spec-dock dashboard serve --offline` で 127.0.0.1 の別のポートに立てて取った（8 つのリポジトリ）。固定した入力は `tests/fixtures/issue627/route_inputs.json`。

- 再現：固定した入力の product（taikyohiyou_project）の木の『全体』、稼働の印なしで overlaps 9（iss-00627 の 9 と同じ。印ありでは 1）。今日の taikyohiyou_project の構造では 3。木は見える幅で変わらない。入れ子はすべて 0。
- 巡ごとの違反の数（固定した入力）：1351, 1255, 1231, 50, 26, 28, 25, 11, 59, 9。10 巡で落ち着かず、最後の巡の 9 が採られる。広げの要求はすべて Initiative の親の線（x 148）と Epic の列（x 502）の間の通り道の x（`tree.indent` に写る）。
- 混んだ束の中身：同時に重なる線分は 10〜11 本、通り道は 43 車線ぶんなのに、詰めは 136〜176px あふれる。

### (A) 寄せの詰め方の階段（router.js の nudgePass）

束の並びの順は、重なる組（nb）のすべてに前後を決める。交差の数が同じ組（長い縦の線分の範囲が少しずつずれ、両端がどちらも右へ曲がる組は、どちらに置いても交差1）も、A* の位置と線の番号で前後を決める。
詰めは「nb の手前の線分 + S」より奥なので、A（0〜100）・B（50〜150）・C（120〜200）のように範囲が鎖につながると、A と C が重ならなくても C は2車線奥へ行く。
木では Initiative の通り道を何十本の長い線分が通るので、この鎖が通り道を奥へ押し、`lacking()` も同じ鎖の数え方で不足を申告する。広げても次の巡でまた積むので落ち着かない。
小さな再現（`stair.mjs`：左に親の線、右に 40 個の箱、箱 i → i + 5、通り道 120px）で、直す前は overlaps 35・広げの要求 26（最大 92px）。

### (B) 違反の残る巡を落ち着いたと見なす（layout.js の routeLayout）

`settled` は広げの要求と出入りの不足だけを見て、検査の違反を数えずに problems 0 とする。横の寄せは縦の線分の長さを変えるので、最後の横の寄せの後に縦の線分の近い重なりが残る巡がある。
(A) だけを直した試作で、housing-lifecycle と固定した入力の business の木の『全体』が、違反4のまま落ち着いた巡として採られた（それより前に違反0の巡があった）。

### 試作の結果（`.workbench/iss-00633/dbg/`）

| 試作 | 固定した入力 product『全体』 | taikyohiyou『全体』 | 木のほかの組 |
|---|---|---|---|
| 直す前 | 9 | 3 | 0 |
| (B) だけ | 9 | 3 | 0 |
| (A) だけ | 0 | 0 | business・housing-lifecycle『全体』が 4 |
| (A) + (B) | 0（5 巡） | 0（5 巡） | すべて 0（最大 9 巡） |
| 巡の上限 16・広い線分の留め・入口の細かい格子（木だけ） | 4・9・2 | 3・9・2 | — |

(A) + (B) で、300 組（8 つのリポジトリと固定した入力の2つの構造 × 30）の比べ：違反の増えた組0、減った組2、入れ子の 270 組は経路まで同じ、経路の変わった組は木の 11。

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 **合格**（P0・P1 0、P2 2：golden の写しに木の run がある・入れ子の不変が経験的、P3 2：詰めの間隔の S と S − 0.5 の食い違い・T-02 の maxWiden の出力）→ 文を直した（golden は試作を一時的に当てて `test_dashboard_graph_golden.py` ほか 54 passed を確かめた。`.workbench/spec-review/iss-00633/review-response.md`）。round-2 **合格**（P0〜P2 0、P3 1：purpose と plan の goal に『入れ子の結果を変えない』の言い切りが残る。契約は constraints と D-02 の『悪くしない』で決まる。記録のみ）。結果 `.workbench/spec-review/iss-00633/round-{1,2}.json` と `.check.json`（reviewed_sha `3f5f8d8e9`）。
- **合格した文書の sha256**：requirement.cue `767be0c836dd432015b5a8b4d678cf139138ecb1fb417f5d67f5046d481df2f9`、design.cue `04790767f9b05aacb1d6e018d87367c7382b4216ede124b874b739be599736cc`、plan.cue `ef8845772471321b673e445505014ecec05721d13d3f74c8ee532cab1d4af1fa`。

## 実装の記録

- 開始のコミット `3f5f8d8e9`（origin/main）。
- 逸脱 codex-symlink-refusal：S-01・S-02 の impl-sol（codex gpt-6.1-sol / medium、dispatch `ctx_a63a8c1831f8`、launch.effective codex / gpt-6.1-sol / medium）は、chat-scratch の writable root の symlink（UnsupportedOperation）で手元のコマンドを起動できず、変更なしで止まった（worker_done failed）。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium に切り替え、同じ値のタスク担当のこのセッションが S-01・S-02 を行った（iss-00627 と同じ扱い。別のセッションは起こしていない）。
- S-01（Claude Opus 5.5 / medium、このセッション）：Red `672cb3153`（`tests/unit/presentation/test_dashboard_graph_tree_route.py`、`tests/js/dashboard_graph_route_fix.mjs` に mode・marks・problems・maxWiden。product の木の『全体』・通り道・静的な検査の3件が落ち、business の木の『全体』は直す前も0で通る：(A) だけを直したときの退行の見張り）→ Green `18958e562`（router.js D-01 の `prefer`・`packFree`・`centre`・nudgePass の (c)・`lacking` の packed、layout.js D-02）。静的な検査の正規表現が packFree の定義も数えていたので、呼び出しだけに直した（テストの誤り）。整形 `3ca68b2c9`。
- 節目の検証：`uv run pytest tests/unit/presentation/test_dashboard_graph_tree_route.py tests/unit/presentation/test_dashboard_graph_route_fix.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_fit.py` 56 件（静的な検査を直した後、新しいテストの4件を再実行して全部合格）。`make lint` pass。static-inventory.json は dashboard の資産を持たないので変わらない。
- 実装の経路は試作と同じ（300 組のすべてで経路の digest が試作と一致）。
- S-02（同じセッション）：全体の `uv run pytest` で `test_dashboard_graph_range.py::test_all_and_now_lay_out_as_the_two_old_combinations` が落ちた（iss-00603 の `tests/fixtures/issue603/layout-before.json` の木の routed の digest 4つ：spec-dock と generated の『全体』『いま』）。木の経路が変わる設計どおりの差で、その組の audit はすべて0、入れ子の digest は同じ。iss-00627 と同じく、digest を記録し直し注記の鍵 `iss-00633` を足した（`a4fe0f8f0`）。graph_dom_golden.json（入れ子と木の run）は書き直しなしで通る。
- origin/main（#638・#639、dd3724b22）を取り込んだ（`5d7c5fb1a`、競合なし。graph の資産は上流で変わらない）。

## 比べ（S-03、T-04）

[sweep-300.txt](artifacts/20261117t044625z-01--sweep-300.txt)（`.workbench/iss-00633/tools/sweep.py`、直す前 `3f5f8d8e9` の資産 → 直した後）。

| 組 | 数 | 違反の増えた組 | 減った組 | 経路が同じ | 経路が変わった | 違反のある組（前 → 後） |
|---|---|---|---|---|---|---|
| 8 リポジトリ（iss-00627 R-05 と同じ 240 組） | 240 | 0 | 1 | 233 | 7（すべて木） | 1 → 0 |
| うち入れ子 | 216 | 0 | 0 | 216 | 0 | 0 → 0 |
| 固定した入力を含む | 300 | 0 | 2 | 289 | 11（すべて木） | 2 → 0 |

- 違反のあった組：taikyohiyou_project の木の『全体』 3 → 0、固定した入力 product の木の『全体』 9 → 0（巡 10 → 5）。
- 固定した入力の木（product・business × 範囲3 × 稼働の印あり・なし）の 12 組：直した後すべて 0。
- 既存の写し（`graph_dom_golden.json` の入れ子と木の run）は書き直しなしで通る。
- 木の大きな構造では、字下げの広げが減り、世界が狭くなる（taikyohiyou の木の『全体』は幅 1182 → 712px）。

## 実機の確かめ（S-03、T-05）

- 試しのサーバー：この worktree の wheel（`3ca68b2c9`）を隔離した venv（`.workbench/iss-00633/venv-after`）に入れ、この PC の状態の置き場の写し（`.workbench/iss-00633/state`）と、空の `XDG_CONFIG_HOME`（orca-web なし＝稼働の印なし）で `spec-dock dashboard serve --offline --tailscale --port 18633`。直す前は開始のコミットの wheel（`venv-before`、状態の写しは別）を 127.0.0.1 の 18634 に。常駐の 47800 と 8791、道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）、窓 1440×900、倍率 100%、taikyohiyou_project の木の『全体』（`.workbench/iss-00633/tools/shot.mjs`）。

| 組 | 直す前 | 直した後 |
|---|---|---|
| 1440 明 | overlaps 9（ほか0、世界 1182×36908） | すべて 0（世界 712×37503） |
| 1440 暗 | overlaps 9 | すべて 0 |

  直す前の 9 は iss-00627 の報告の 9 と同じ線の組（`lane r90#11~r144#17` ほか）。違反は boxHits・ownHits・overlaps・diagonal・portShare・failed・missing・markOverflow。
- 写し（題名は Scope の ID に置き換えて写した。公開のリポジトリに題名を載せないため）：直す前 [1440 明](artifacts/20261117t044624z--before-tree-all-1440-light.png)・[1440 暗](artifacts/20261117t044624z-02--before-tree-all-1440-dark.png) → 直した後 [1440 明](artifacts/20261117t044624z-01--after-tree-all-1440-light.png)・[1440 暗](artifacts/20261117t044625z--after-tree-all-1440-dark.png)。epic-02026 に入る線の束のあたり。直す前は Epic の左の通り道に線が 2〜6px で詰まり、直した後は車線（8px）に分かれ、字下げが狭くなる。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18633 番（`/r/github.com/chemitaro/taikyohiyou_project/` で「木」と「全体」。URL は統括への報告で伝える）。止め方：`kill $(lsof -tnP -iTCP:18633 -sTCP:LISTEN) $(lsof -tnP -iTCP:18634 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。

## 最終品質ゲート

- キャンペーン iss-00633-fqg-1（quality-gate-reviewer opus / medium、second opinion なし、範囲 `3f5f8d8e9..HEAD`、観点 functional-correctness・requirements-closure・test-adequacy・compatibility-regression、test_commands `make lint`・`uv run pytest`）。
- attempt 01（`a4fe0f8f0`）：レビュー合格（P0〜P3 0）。テストは origin/main が進んだ（統括 msg_73c77ba94794）ので途中で止め、数えない。
- attempt 02（`5d7c5fb1a`、取り込みの後）で **合格**：review lane P0〜P3 0、coverage complete。`make lint` exit 0、`uv run pytest` exit 0（4108 passed、7 skipped）。closure は worktree の `.workbench/final-quality-gate/iss-00633-fqg-1/closure.md`。

## Outcome

木の表示で、寄せの詰めが範囲からあふれる束を、前後の決まる組の順だけを守って空いた位置に詰め直し（router.js の packFree）、検査の違反が残る巡を落ち着いたと見なさないようにした（layout.js）。taikyohiyou_project の木の『全体』の線の違反は、node・実機とも 9（今日のデータの node は 3）→ 0。入れ子の表示は 270 組すべてで経路まで同じ。

## Verification

- 仕様のレビュー合格（round-2）。最終品質ゲート合格（`5d7c5fb1a`、review P0〜P3 0、`make lint`・`uv run pytest` 4108 passed）。
- 比べ：300 組で違反の増えた組0、違反のある組 2 → 0、入れ子 270 組は経路まで同じ。固定した入力の木 12 組（稼働の印あり・なし）すべて0。
- 実機：taikyohiyou_project の木の『全体』1440 明暗で edgeAudit の違反 9 → 0。前後の写しあり。
- PR https://github.com/chemitaro/spec-dock/pull/641（head `5d7c5fb1a`）。CI は観測中（`.workbench/iss-00633/pr-checks.json`）。マージは統括が行う。

## Residual Risks / Follow-ups

- packFree は交差の数が同じ組の前後を決めないので、詰め直した束では交差の数が今と違うことがある（重ならないことを優先）。
- 木の大きな構造では 10 巡で落ち着かない構造もありうる（そのときは今どおり最も違反の少ない巡）。今の 8 リポジトリと固定した入力の木は最大 9 巡で落ち着く。
- 試しのサーバー 18633（tailnet）と 18634（127.0.0.1、直す前）は本人の確かめまで残す。

## 次の提案

- 横断の構造（`/graph`）には木の表示がないので範囲外にした。木の表示の線の検査を CI の node のテストで常に見るなら、固定した入力の木の『いま』『これから』も T-01 に足せる（今は比べで0を確かめただけ）。
- 仕様のレビューの P3（purpose と plan の goal の『入れ子の結果を変えない』の言い切り）は、文書を合格の後に変えないため残した。
