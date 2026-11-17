---
種別: レポート（Issue）
ID: "iss-00646"
関連GitHub: ["#646"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 **合格**（P0 0、P1 0、P2 3、P3 0）。結果はこの worktree の `.workbench/spec-review/iss-00646/round-1.json` と `.check.json`（reviewed_sha `2fa809271`）。
- **合格した文書の sha256**（round-1）：requirement.cue `a0cac08933fa9294412de17828d1bdba6e7a785e22ee44c981a644a3c743e6bd`、design.cue `6e4f47e0601a91079c6298c76b4e6fc950aa6c828f339cb44084fa61b93801d7`、plan.cue `3fbe3f740ca91d80cc7ada42717341468989404f5fb3972c4be5ee9a7b5faf7e`、explanation.html `f260b115432d4e958ac7611213810e7ab98efa5b9f29add85cd0dd0275b3de8c`。
- P2 の扱い（止めない。文書は変えず、実装と測りで扱う）：
  1. F-02 の時計：`watch(null)`（層を消したとき）でも、止める印の時計を消し `is-still` を外す（ページが裏なら残す）ように実装し、T-03 で確かめる（実装担当への申し送り。F-02 の文言の範囲の実装の判断）。
  2. Epic D-04・R-05（端から端まで2〜3秒、stroke-dashoffset の動き）との食い違い：この Issue の decisions の統括の決定（msg_b598780e1110、40px/秒、切り替えの方式）が置き換える。Epic の文書を直すかどうかは統括に報告して任せる。
  3. 前と後の比べ：S-04 で、直す前（基準のコミットを入れた別の venv、ポート 18647）と後（18646）のサーバーを同じ状態の写しと同じ orca の中継で立て、交互に測り、測りごとに線・切り替えの絵・波紋の数を記録する。

## 実装の記録

- 担当：impl-claude（Claude Opus 5.5 / medium）が S-01〜S-03 を行った。開始のコミット `2fa8092716530e48f48c9eeb70d5f6017853acde`。
- S-01 `8524ae343`：`views/graph/command_motion.js`（新、D-01）と T-01（`tests/js/dashboard_graph_command_motion.mjs`・`tests/unit/presentation/test_dashboard_graph_command_motion.py`）。Red（モジュールなし）→ Green：11 passed。
- S-02 `b0d8bf54b`：D-02（`layersHtml`）、D-03（`createMotion`）、D-04（`graph.js`・`allgraph.js`、`specdockCmdAudit` の `motion`）、D-05（`graph.css`）。T-02・T-03 を先に書いて Red（graph 7件・allgraph 2件が落ちる）→ Green。偽の時計・可視性・IntersectionObserver は `tests/js/fake_motion.mjs`（新）。節目（plan の S-02 の verification）：376 passed。
- S-03：`make lint` 合格（ruff check・ruff format check・mypy）。全体の `uv run pytest`：**4230 passed, 7 skipped**（29分55秒、exit 0）。落ちるものがなく、基準のコミットとの区別は要らなかった。ログはこの worktree の `.workbench/implement/iss-00646/{lint,full}.log`。
- `static-inventory.json`：dashboard の資産は載っていない（変更なし）。パッケージには `assets/**/*` で入る。
- 直した今のテストの期待（層の中の HTML と点・波紋の CSS だけ）：`sd-cmd-flow`・`stroke-dashoffset` の CSS の期待 → 切り替えの期待、`.cr circle` の規則 → `.cr > i`、減らす設定の規則、帯の波紋の位置（円の cx・cy → `.cr` の left・top）、帯の波紋の入れ物の選択子（`.gx-band > svg` → `.gx-band > .gx-band-cr`）、横断の `cmdSize`（世界と同じ大きさの SVG）→ 世界と同じ大きさの SVG がないこと、横断の道と端の点の読み方（本体の SVG に `cl-line` がない流れる線と、点のない切り替えの絵を読み分ける）。それ以外の期待は変えていない。
- レビューの申し送り（P2-1）：`watch(null)` で時計を消し、`is-still` を外す（ページが裏なら残す）。T-03（`watch` の run の 5・7〜9 番目）で確かめた。

## 逸脱と判断

- S-01 の担当の交代：計画では impl-sol（Codex）だったが、Codex が chat-scratch の symlink の拒否で何も変えずに止まった（dispatch ctx_ce223ee3c6ca）ので、計画の rationale と統括の了承のとおり impl-claude が S-01 から引き継いだ。
- `svgOpen(box, cls, extra, attrs = "")`：設計の引数に、`data-ph` を書くための4つ目の省略できる引数を足した（出力の形は設計の HTML のとおり）。
- 減らす設定の今の規則 `.gx .cl-line, .gx .cl-stub, .gx .cl[data-state] :is(.cl-line, .cl-stub) { animation: none; }` は、線のアニメーションがなくなり意味を失うので、設計の `.cl-ph` の規則に置き換えた。
- `state()` の `phases`・`ripples` は IntersectionObserver が見張っている数（ないときは 0、F-01）。`off` は世界の中の `is-off` の数。
- 呼ぶ側の `layersHtml(model, {width, height})` は `layersHtml(model)` にした（設計で使わない引数）。
- 世界と同じ大きさの SVG がないことの検査は、指揮の層について行う（依存の線の `.gx-edges` は範囲の外で、今のまま世界の大きさ）。

## 実機の確かめ（S-04、2026-11-17、`b0d8bf54b`。測りは `b400ed00f` と同じ dashboard の資産）

- 試しのサーバー：直す前は基準のコミット `2fa809271` を `git archive` して隔離した venv（`.workbench/iss-00646/venv-before`）に入れ、ポート 18647。直した後はこの worktree を隔離した venv に editable で入れ（`.workbench/iss-00646/venv`）、ポート 18646（`--tailscale`）。どちらも同じ状態の置き場の写しと、常駐の orca-web を GET で読むだけの中継（`relay_orca.py`、18846）を使う。headless Chrome は `--disable-features=MacAppCodeSignClone`。常駐の 47800・8791 の設定、道具の環境には触れていない。
- 台本：統括の `perf-measure.mjs` のポートだけを変えた写し（1440×900、deviceScaleFactor 2、読み込みの15秒後から10秒の TaskDuration）。前と後を交互に3回ずつ（同じ時刻の同じエージェントの組。P2-3 の申し送り）。

| 画面 | 前・動きあり | 後・動きあり | 前・減らす設定 | 後・減らす設定 |
|---|---|---|---|---|
| 横断の構造（`/graph`） | 1.31・1.39・1.54（中央 1.39） | 0.01・0.01・0.01（中央 0.01） | 0.02・0.03・0.02 | 0.11・0.02・0.02 |
| spec-dock の構造の図 | 0.83・0.99・0.95（中央 0.95） | 0.03・0.02・0.02（中央 0.02） | 0.02・0.03・0.03 | 0.03・0.03・0.03 |

  - 受入（横断 0.11秒以下、単体 0.07秒以下／10秒）を満たす。前の数が統括の測り（0.54・0.32）より大きいのは、同じ PC で全体のテストやほかの作業が並んで走り CPU が混んでいたため（前と後を交互に測ったので比べは公平）。統括の測りの数と比べても、後は5分の1を大きく下回る。
  - 測りのときの指揮の組：線1本（`flow`）と波紋1つ。後のページは切り替えの絵4枚・輪1組・アニメーション7つ（ほか3つは今の印の点滅など）。前の試作の測り（線5〜8本の時刻）でも、同じ方式で単体 0.015・横断 0.044。
  - 線が画面に入っている場合：横断の構造で、流れる線を図の中央に動かしてから測ると、前 1.32、後 0.019（`motion.off` 0）。単体の図は初めから線が画面に入っている（`off` 0）。横断の初めの見え方では線が画面の外にあり、後は `off` 5（4枚と輪）で止まる。
- ドラッグ（CDP の Input.dispatchMouseEvent で約4秒、121回）：前も後も、50ms を超える長いタスク 0、1秒あたり 60 コマ。その間の TaskDuration は前 0.46〜0.60、後 0.48〜0.52（世界の transform の描き直しが主で、この Issue の範囲の外）。実機で、ホイールの直後に `.gx-view` に `is-still` が付き、7つのうち6つのアニメーションが paused、0.4秒後に外れて動き出すことを確かめた。
- 検査：両方の画面で `specdockEdgeAudit().total` の違反0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、`spotDrift` 0、`spotMissing` 0、ブラウザーのエラー0。世界と同じ大きさの SVG は指揮の層にない（2000px を超える SVG は依存の線 `.gx-edges` だけ）。
- 写し（`.workbench/iss-00646/shots/`、`one-montage.png`・`all-montage.png`）：両方の画面の 1440 × 明・暗で、流れる線と波紋の周りを、アニメーションを 10・60・110・160ms に固定して前と後で並べた。線・点・光・波紋・端の点の見え方は同じ。
- 点の向き：アニメーションを 10・60・110・160・210ms に固定すると、見える絵はちょうど1枚で、そのずらしが 0 → −2 → −4 → −6 → 0px と進む（道の向き、親から子へ 40px/秒）。
- 本人が見る試しの URL：tailnet の 18646 の `/graph`（横断の構造）と `/r/github.com/chemitaro/spec-dock/graph`。止め方：`.workbench/iss-00646/state/dashboard/server.json` の pid（または `pkill -f "port 18646 --state-root"`）と、`relay_orca.py` の2つ（127.0.0.1 と tailnet の 18846）。直す前のサーバー（18647、127.0.0.1 だけ）も比べのために残す。

- **最終品質ゲート（2026-11-17、合格）**：合格のコミット `b400ed00f`（origin/main の 0.9.7 #647 を取り込んだマージ。base `2fa809271`）。レビュー（quality-gate-reviewer opus / medium、4観点）P0〜P3 すべて0、網羅は完全。`make lint` exit 0、`uv run pytest` 4233 passed・7 skipped。この worktree の `.workbench/final-quality-gate/iss-00646/closure.md`。記録だけのコミットはない（記録は Git の外）。
- 実装担当の起動：impl-sol（Codex、dispatch `ctx_ce223ee3c6ca`、launch.effective codex gpt-6.1-sol / medium）は chat-scratch の symlink の拒否で何も変えずに止まった（worker-stop）。impl-claude（dispatch `ctx_35f9782138ae`、launch.effective claude-opus-5-5 / medium）が S-01〜S-03 を行った。

## Residual Risks / Follow-ups

- Epic epic-00615 の D-04・R-05（点を端から端まで2〜3秒、stroke-dashoffset の動き）は、この Issue の統括の決定（40px/秒、止めた絵の切り替え）で置き換わった。Epic の文書を直すかどうかは統括に任せる（仕様のレビュー round-1 の P2-2）。
- 合成スレッドのレイヤーは、流れる線1本につき本体と切り替えの4枚、端の層の4枚。線が数十本に増えたときの GPU のメモリは測っていない。
- 試しのサーバー（18646 tailnet、18647 ローカル、中継 18846）は本人の確かめまで残す。
