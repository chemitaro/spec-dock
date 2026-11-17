---
種別: レポート（Issue）
ID: "iss-00650"
関連GitHub: ["#650"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / medium、light、2人目なし）：round-1 **合格**（P0 0、P1 0、P2 0、P3 0）。結果はこの worktree の `.workbench/spec-review/iss-00650/round-1.json` と `round-1.check.json`（reviewed_sha `92e26aff7`、文書は sha256 で固定）。
- **合格した文書の sha256**：requirement.cue `6aba51eeb1fbaa23efacbc9266aac7927bf6dcbeebf1f56c9901ca480faa320d`、design.cue `3bfd13529797a3389360fc8e0ef0411a6b44fd729917c2fbd91510e3275dd519`、plan.cue `06d2f950787f93bad17eae9ad74f75e35596fc5b8ad67acc76c6f6554fdae59d`。

## Outcome

- 原因：帯の欄（`views/graph/command_view.js` の `renderAgentPanel`）の本文 `.pn-body` に `data-tab` がなく、`panel.css` の縦の flex の規則（`.pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"])`）に乗らないため、`.sd-agent` の `flex: 1` が効かず、iframe は `min-height: 240px` のままだった。
- 直し（S-01、`f7655ea8c`）：チャットの枠を出すときだけ、本文を `<div class="pn-body" data-tab="agents">` にした。CSS は足していない。チャットを開けないときは今の `<div class="pn-body">` のまま（余白も同じ）。構造の図と『横断の構造』は同じ関数を呼ぶので、両方が直る。
- テスト（T-01）：`tests/js/dashboard_{graph,allgraph}_command_screen.mjs` の写しに本文の `data-tab` と「チャットを開けません。」を足し、`test_dashboard_graph_command_screen.py` に (1) 帯を押すと `bodyTab == "agents"`、panel.css の規則が PC とシートの2か所で `display: flex; flex-direction: column;` を持つ、(2) 描き直しても `agents` のまま（同じ iframe）、(3) detail のない統括では `data-tab` なしで「チャットを開けません。」（F-01）を、`test_dashboard_allgraph_command_screen.py` に帯を押すと `agents` を足した。Red は直す前の資産で (1)(2) と横断の件が落ちることを確かめた（3 failed）。

## 逸脱と判断

- 同じセッションの例外：light で手順が2つ、画面の JS の1行の変更なので、タスク担当（Claude Opus 5.5 / medium、依頼書が画面のコードに指定する値と同じ）が実装した。実装担当は起動していない（plan.cue の execution に記録）。
- `data-tab="agents"` はチャットの枠があるときだけ付ける（依頼書の「チャットを開けません。の表示は変えない」を余白まで保つため。requirement の decisions）。

## Verification

- 節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_command_screen.py tests/unit/presentation/test_dashboard_allgraph_command_screen.py tests/unit/infra/test_dashboard_agents_tab_js.py` 81 passed。`make lint` exit 0。
- 実機（T-02、2026-11-17）：直す前は基準のコミット `92e26aff7` を `git archive` して隔離した venv に入れ（127.0.0.1:18651）、直した後はこの worktree を隔離した venv に editable で入れた（18650、`--tailscale`）。どちらも、この PC の状態の置き場の写しと、試しの `XDG_CONFIG_HOME`（`orca_web.port` 18850）と、常駐の orca-web を GET で読むだけの中継（`relay_orca.py`、18850）。headless Chrome は `--disable-features=MacAppCodeSignClone`、終わりに CDP の `Browser.close`。常駐の 47800・8791 の設定、道具の環境には触れていない。エージェントには何も送っていない。帯の「main のチェックアウト」の統括の印を押して測った（`.workbench/iss-00650/measure.mjs`、`measure.jsonl`）。

| 画面 | 大きさ | 前：iframe の高さ / 本文の内側 | 後：iframe の高さ / 本文の内側 | 後の本文の余白 |
|---|---|---|---|---|
| 構造の図 | 1440×900 | 240 / 745 | 761 / 761 | 4px 10px 10px（タブと同じ） |
| 構造の図 | 390×844 | 240 / 406 | 430 / 430 | 2px 4px 4px（タブと同じ） |
| 横断の構造 | 1440×900 | 240 / 745 | 761 / 761 | 4px 10px 10px |
| 横断の構造 | 390×844 | 240 / 406 | 430 / 430 | 2px 4px 4px |

  - 本文の内側は「本文の高さ − 上下の余白」。後はどれも差 0px（受入の差 2px 以内）。縁取り 1px solid、角丸 8px はエージェントのタブと同じ（scope_tabs.css）。
  - 線の検査：構造の図の `specdockEdgeAudit` の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・frameExits・failed・missing・markOverflow）は前後とも 0、『横断の構造』は7つのリポジトリのどれも 0。`specdockCmdAudit` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、`spotDrift` 0.4〜0.5（前後で同じ）。横のスクロールなし。ダッシュボードのエラー0。
  - 横断の構造 1440 の後の1回で、iframe の中の orca-web の資産（`/embed/send-*.js`）の読み込みが試しの中継で `ERR_CONNECTION_RESET` になった（中継の一時の切れ。ダッシュボードの資産ではなく、ほかの7回は0）。横断の構造 390 の後の1回目は、押した帯の印が画面の外（別のエージェント）で欄が開かず、撮り直した。
  - 写し：`.workbench/iss-00650/shots/{one,all}-{before,after}-{1440,390}.png`。後は送る欄が欄の下に付き、会話の枠が見出しの下から欄の下まで広がる。
- 本人が見る試しの URL：tailnet の 18650 の `/r/github.com/chemitaro/spec-dock/graph`（構造の図）と `/graph`（横断の構造）。止め方：`.workbench/iss-00650/state/dashboard/server.json` の pid（または `pkill -f "port 18650 --state-root"`）と、`relay_orca.py` の2つ（127.0.0.1 と tailnet の 18850）。直す前のサーバー（18651、127.0.0.1 だけ）も比べのために残す。

## Residual Risks / Follow-ups

- なし（CSS は変えていない。Scope の欄に戻ると panel.js が本文の `data-tab` を描くたびに上書きする）。
