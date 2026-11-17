---
種別: レポート（Issue）
ID: "iss-00648"
関連GitHub: ["#648"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 不合格（P1 2：hop の頂点のはみ出し、Epic に古い決まりが残る。P3 2）→ 直して round-2 **合格**（P0〜P3 すべて0）。結果はこの worktree の `.workbench/spec-review/iss-00648/round-{1,2}.json`・`.check.json`・`review-response.md`（reviewed_sha `92e26aff7`）。
- **合格した文書の sha256**（round-2）：iss-00648/requirement.cue `0eaa489858b3912ea7b1c10eb7acbb1a663936e15067a0c910c42368095a0487`、iss-00648/design.cue `7f624aa028e527e77393b3c03114dcc8f07dc519915a678074d4cc81deaeeb3a`、iss-00648/plan.cue `08edcc3f9c585c18a468611050610051d35a961d6760437afaa12af136c50a30`、iss-00648/explanation.html `862df12fed3328e04d3719d9e50a90bad45bd1337d10fd75cf06dc18fc984c0b`、epic-00615/requirement.cue `e2fffa69623b78b89cde0a508a681e41ba8909379d86aff2a38774ea2854b2b8`、epic-00615/design.cue `51323b73d86669e5148ffe9ed70fe9a38768393e20164838e66c36e295047b2f`。
- round-1 の間に、タスク担当が `.workbench/iss-00648/` に写しの台本と直す前の写しを足した（レビューの対象の文書は sha256 で固定していて変わっていない）。

## 実装の記録

- 開始のコミット `92e26aff7256a9a32ba6edd5bc7f790ed8e4f149`（origin/main、iss-00646 のマージ後）。
- 仕様化と S-01（Epic の文書の直し）：タスク担当（Claude Opus 5.5 / medium、統括が選んだ値）。

- S-02（impl-claude：Claude Opus 5.5 / medium。計画では impl-sol だったが、Codex が chat-scratch の symlink の拒否で何も変えずに止まったので、計画の rationale と統括の了承のとおり引き継いだ）：コミット `074191092`。
  - 基準（開始のコミット `92e26aff7`、`.workbench/implement/iss-00648/start.md`）：`make lint` 合格、S-02 の節目のテスト 51 passed。全体の `uv run pytest` は30分かかるので基準では省き、S-04 で行う。
  - 変えたもの：`views/graph/command.js`（`HOP`・`hop`・上の縁の端 `fixedEnd`・`sameHop`・線の `mark` と `peak`・`top`・引数 `ceiling`。`faceOf`・`DOWN`・`SIDES` の下と左右・`contains`・`center`・`boxArc`・`frameArc`・`bandArc`・`CHORD`・`ARC_D`・`ARC_MIN`・`FRAME_ARC_D` と `roomOf` の下・右を消した）、`views/allgraph/command.js`（`crossModel` が `ceiling: 4`）、`tests/js/dashboard_graph_command.mjs`（`hop` の依頼と `HOP` の定数）、`tests/unit/presentation/test_dashboard_{graph,allgraph}_command.py`。描き方のファイルは変えていない。
  - Red：新しいテストを開始のコミットの `command.js` 2つで走らせて 22 failed・3 errors（`hop` がない）（`.workbench/implement/iss-00648/s02-red.log`）。Green：`uv run pytest tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_allgraph_command.py` 60 passed（`s02-green.log`）。`make lint` 合格（`s02-lint.log`）。CP-1 の『S-02 の節目のテストの合格』はこれで確かめた。
  - 直した今の期待：下の端（帯の項目の下の縁・箱の下の縁・枠の見出しの印の下・枠の内側の下の縁・F-04 の箱の下の縁）→ 上の縁。`stubs`（箱の中の短い線）→ 空。`boxArc`（下・右の縁の外、16px、弦 40、右へ逃げる・依存の線から逃げる）・`frameArc`（見出しの下 12px）・`bandArc`（上 16px）→ `sameHop`（上の縁、18px、弦 12、余白 − 3 へ下げ下限 8、`crowded`）。曲線の制御点（`k = min(140, max(24, 0.45·L))`、両端の向き）→ `hop`（頂点がちょうど H 上）。`top` の `-32` → ホップの頂点を含む `-78`（`five`）。同じ枠の上の縁へ入る3本のずらし（前は2本 ±5、内側の下の縁の1本は別）→ 3本 −10・0・+10。『Epic の統括の線が枠の上の縁より上に出ない』→『枠の上の縁から出て Issue の上の縁へ入るホップ』。`boundsOf` の弧の下の縁の制限 → 上の縁の制限（16/10 → 18/10）。依存の線から右へ逃げるテスト → `edgeOverlaps` に数えるテスト。
  - 足したテスト：木の枠の箱（`tframe`）、縦に重なる印（12 に離す）、上の余白 14px（11、`crowded` 1、`boxOverlaps` 0）・6px（8、重なり1）、依存の線の水平な区間（`edgeOverlaps` 1）、子が上・同じ高さ・下、`hop` の直の計算（同じ高さ、差 700px、dx 0 の横のふくらみ、`ceiling` と `HOP.low`）、線の `mark`、`top`、横断の構造の『ほかの場所』から 500px 以上下の箱（頂点 4）。

## 逸脱と判断

- 観察（仕様どおり、変えていない）：横断の構造の『ほかの場所』の帯の同じ項目のホップは、帯の上の縁 y 24 と `ceiling` 4 から `room` 20、高さ min(18, 20 − 3) = 17 になり、`crowded` に 1 数える（テストの場面 `deep`。`boxOverlaps`・`edgeOverlaps` は 0）。実データで『ほかの場所』の中の親子があると、`specdockCmdAudit()` の `crowded` が 1 以上になる。
- S-02 の担当の交代：計画では impl-sol（Codex gpt-6.1-sol / medium、dispatch `ctx_17c1d5a4151a`）だったが、Codex が chat-scratch の symlink の拒否（symlinked writable roots are not supported）で何も変えずに止まった。計画の rationale と統括の了承のとおり worker-stop し、impl-claude（Claude Opus 5.5 / medium、dispatch `ctx_aec9f6b0309e`、provider claude / model opus）が S-02〜S-04 を1つのセッションで行う。CP-1 の S-02 の節目のテストの確かめは、実装担当が S-02 の後に行い、記録する。


## Residual Risks / Follow-ups
