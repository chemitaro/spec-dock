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

## Residual Risks / Follow-ups
