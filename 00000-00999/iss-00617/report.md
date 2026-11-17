---
種別: レポート（Issue）
ID: "iss-00617"
関連GitHub: ["#617"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし）：round-1 合格（P0 0、P1 0、P2 3、P3 6）。P2 3件と P3 6件を直し（この worktree の `.workbench/spec-review/iss-00617/review-response.md`）、統括の答え（msg_473d9e036b83『推奨で』）を decisions に記録した。round-2 **合格**（P0 0、P1 0、P2 0、P3 1）。結果は `.workbench/spec-review/iss-00617/round-{1,2}.json` と `.check.json`（reviewed_sha `0ef2dfeae`）。
- **合格した文書の sha256**（round-2）：requirement.cue `bb963877e6ee8af369c038a67d4614d41976347d25fbed520b8d7a966c1cef2d`、design.cue `a3736e2d38637ae68050a331af0b9963484aff8522e86289aee9491b267bfd8e`、plan.cue `fc25bf50f72253bc00f7da4cce163fa609c9d7a320e16468f59c9e5a0ce6545e`、explanation.html `ff61af14de4a166621fbd8549b3458a77853ca7e90a3776a89bbc50c59613988`。
- round-2 の P3（止めない。実装担当への申し送り）：F-05 の数えを0に戻す鍵（居場所の入力）に、各リポジトリの構造の読み込み（`of`・`unknown`）と見える集合の変化も含めるとよい（Scope のないリポジトリの構造の読み込みで帯の形が変わっても、数えが戻らないため）。

## 実装の記録

- 開始のコミット `0ef2dfeae`（origin/main、iss-00616 の PR #642 の後）。
- 実装担当（impl-claude、Claude Opus 5.5 / medium）が S-01 から担当した。開始のコミットでの S-01 の節目のテストの基準：今あるファイル（`test_dashboard_allgraph_compose.py`・`test_dashboard_graph_command.py`・`test_dashboard_graph_js.py`・`test_dashboard_graph_marks_rows.py`）で 90 passed（`test_dashboard_allgraph_command.py` は新しいので基準なし）。
- S-01：T-01〜T-03 を先に書いて落ちることを確かめ（allgraph_command の 21 件のうち 21 件が失敗・エラー、compose の足した 6 件と `REPO` の完全一致の 1 件が失敗）、D-01（`graph/command.js` の `bandKeys` の export・`placer`・`bandRowWidth`・`commandModel` の `rows` と `boundsOf`）、D-02（新しい `allgraph/command.js` の `repoOfWorktrees`・`crossPlace`・`bandShape`・`crossModel`・`crossKey`）、D-03（`compose.js` の `REPO` の `band`・`bandTop`・`other`・`otherTop`、`bands[key]` の `{h, w}`、`keep`、`other`、`anchorShift`）を入れて通した。節目の5ファイルで 117 passed、変えたテストの ruff check・ruff format --check・mypy は合格。
- S-02：T-04・T-05 を先に書いて落ちることを確かめ（新しい `test_dashboard_allgraph_command_screen.py` の CSS の検査 5 件が失敗、画面の 12 件が帯のボタンがなくエラー）、D-04（新しい `graph/command_view.js` に層の HTML・帯の印・指揮の選びの class・帯のエージェントの欄・`headsAudit` を移し、`graph.js` はそれを呼ぶ。`graph.js` の今のテストはそのまま通る）、D-05（`allgraph.js` の `paintCommand`・帯の形のやり直しと F-05 の数え・`anchorShift` の補い・指揮の選び・帯のチャット・凡例の行・`window.specdockCmdAudit`、`graph.js` の `cmdAudit` の `heads`）、D-06（`graph.css`・`allgraph.css` の見出しの規則と下地、`.gx-band-lead`）を入れて通した。`test_dashboard_graph_command_screen.py` の枠の z-index の期待（1 → auto）を D-06 に合わせて直した。S-02 の節目のテストで 354 passed。
- S-03：`make lint` 合格（ruff check・ruff format --check・mypy）、全体の `uv run pytest` で 4208 passed, 7 skipped（30分21秒、`57517bb32`）。golden と静的な検査の変更は S-02 の枠の z-index の期待の1件だけ（D-06 の CSS が理由）。`static-inventory.json` は dashboard の資産を載せていないので変えていない。

## 逸脱と判断

- S-01 の担当：計画では impl-sol（Codex）だが、Codex が chat-scratch の symlink の拒否で何も変えずに止まったので、統括が了承済みの取り決めどおり impl-claude が S-01 から引き継いだ。
- F-05 の数えを0に戻す鍵（round-2 の P3 の申し送り）：`crossKey` の入力に、要約・各リポジトリの配置（`eg`）・測った印の幅と記録に加えて、各リポジトリの構造（`structure` の同一性。構造の読み込みで worktree の対応 `of`・`unknown` が変わる）と、帯を渡さない `compose` で見える集合（`visible`）を含めた。`comp` を `null` にすると `comp` を除いた鍵になり、`allgraph.js` はこれを F-05 の数えの鍵に使う（仕様の『居場所の入力』の意味の範囲の実装の判断）。
- `crossPlace` で見えないリポジトリの端を『ほかの場所』へ移すのは、仕様どおり帯の端に限らず、`visible2` にないリポジトリのすべての端にした（グラフのあるリポジトリは必ず見えるので、帯の端のほかは起きない。起きたときに描けない端を残さないため）。
- `crossModel` の `spotsOf` は `(配置の node, リポジトリの key) → markSpots の矩形（配置の座標）` を受け取り、`crossModel` が本文の原点だけずらす（純粋な計算のまま、呼び手は各リポジトリの測った幅と記録を渡すだけ）。戻りに、世界の座標の写し（`world: {nodes, groups, origin}`）を足した（`specdockCmdAudit` の `spotDrift` に使う）。

- 2026-11-17 タスク担当：S-01 は plan.cue では impl-sol（Codex GPT-6.1 Sol / medium、dispatch `ctx_71115940fbe5`、launch.effective は計画どおり）だが、Codex が chat-scratch の symlink の拒否で何も変えずに止まったので、統括が了承済みの取り決めどおり止め（worker-stop）、Claude Opus 5.5 / medium（impl-claude、dispatch `ctx_78ece349361c`、launch.effective claude-opus-5-5 / medium）が S-01 から S-03 まで引き継ぐ。
- D-06 の `--gx-fbg`：設計は「背景もこの変数で書いてよい」なので、今の背景の宣言（`.gx .gx-ini`・`.gx .gx-epic`・`.gx .gx-frame[data-st="done"]`）は文面のまま残し、変数は別の規則で同じ値を置いた（今のテスト `test_dashboard_graph_fit.py` が背景の宣言の文面を固定しているため）。下地の規則は、選択子の行（`:not(.gx-agents)` を含む）と宣言の行を分けて書いた（`test_dashboard_orca_views_js.py` の「エージェントの行の規則に色を足さない」検査の意味を保つ。下地はエージェントの行を除く）。
- 自分の地の色を持つ見出しの札として、今の CSS から `.ds-docid`（`--ds-accent-soft`）・`.sbar`（`--ds-surface-3`）・`.hm`（`--sd-blocked-bg`）・`.dn`（`--ds-surface-2`）を列挙し、2層の背景にした。ほかの子（状態の印・Initiative の文字・題名・worktree の印・進み具合の数・状態の数・保証レベル・片付けの印）は自分の地の色を持たないので、下地だけを敷く。
- 帯の形をなくすとき（組がなくなったとき）の組み立て直しは F-05 の数えに入れない（形を null にした後は組がない限り形が出ないので、繰り返さない）。
- `window.specdockAllGraphStats` に `composes`（枠の組み立ての回数）を足した（T-05 の「同じ形で組み立て直さない」「F-05 の2回」の数え。今の項目は変えない）。
- 偽の DOM には位置（offset）がないので、`specdockCmdAudit` の `spotDrift` は T-05 では項目があることだけを確かめ、値は実機（T-06）で数える。

- **最終品質ゲート（2026-11-17、合格）**：合格のコミット `18ba5383a`（origin/main の #643 を取り込んだマージ。base `0ef2dfeae`）。レビュー（quality-gate-reviewer opus / medium）P0〜P3 すべて0、網羅は完全。`make lint` exit 0、`uv run pytest` 4213 passed・7 skipped。この worktree の `.workbench/final-quality-gate/iss-00617/closure.md`。attempt 01（`57517bb32`）はレビュー合格だったが、テストの途中で main が進んだ（#643）ので止め、取り込んだコミットで attempt 02 をやり直した。記録だけのコミットはない（記録は Git の外）。

- **PR**：https://github.com/chemitaro/spec-dock/pull/644（head `18ba5383a`、`Refs #617`）。CI（Commit identity、SpecDock check、Provider CI）すべて合格、マージの準備 READY（2026-11-17）。マージは統括。

## 実機の確かめ（S-04、2026-11-17、`57517bb32`）

- 試しのサーバー：この worktree の候補の wheel を隔離した venv（`.workbench/iss-00617/venv`）に入れ、この PC の状態の置き場の写し（`.workbench/iss-00617/state`）と試しの `XDG_CONFIG_HOME`（`orca_web.port` 18817）で、`spec-dock dashboard serve --offline --tailscale --port 18617`。試しの orca の口は iss-00616 の `relay_orca.py`（常駐の orca-web を GET で読むだけの中継）を写して 18817 に。常駐の 47800・8791 の設定、道具の環境には触れていない。エージェントには何も送っていない。
- 実データ：今の Run の統括（spec-dock の main のチェックアウト）→ 各 Issue の worktree のタスク担当・実装担当、それに統括が用意した試しのエージェント3人（何もしない claude-haiku-5-5）：親 P は会社のリポジトリ（Scope がなく、子のリポジトリの入れ物の枠）の main のチェックアウト、子1はこの Issue の worktree（spec-dock）、子2はダッシュボードに登録していないリポジトリの main のチェックアウト。
- 結果（`.workbench/iss-00617/shots/`、`result.json`）：『横断の構造』の 1440・390 × 明・暗 × 全体・いま・これから の12通りで、`specdockEdgeAudit().total` の違反0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`crowded`・`heads` 0、`spotDrift` 0.4、`spotMissing` 0、ブラウザーのエラー0、横のスクロールなし、『収める』の後に帯と全部の枠が図の領域に収まる、凡例に「指揮（親 → 子）」。線は6〜7本（done 5、flow 1〜2）。
  - 全体の帯『ほかの場所』が世界のいちばん上に出て、行の頭の文字と「<登録していないリポジトリの名前> · main」の札が並び、そこから P の印への線が出た（R-01・R-02・R-03 の子だけの行き先）。
  - 親 P は、その会社のリポジトリの枠の見出しのすぐ下の帯に「main のチェックアウト」で出て、そこから入れ子のリポジトリの枠をいくつもまたいで、spec-dock の枠の中の iss-00617 の箱の印へ線が出た（リポジトリをまたぐ線）。spec-dock の帯にも統括の「main のチェックアウト」が出た。
  - 帯のエージェントを押すと、欄に `/embed/agent?id=<id>` の iframe が開き、そのエージェントの線1本が目立ち（ほかの5本は淡く）、`aria-pressed`。Esc で解けて欄が閉じた。
  - 見出し：リポジトリの枠の名前、Initiative・Epic の ID の札・題名・要約の行の上を、線が通らない（文字の背の下地に隠れ、すき間では見える）。構造の図（spec-dock、1440 × 明・暗、これから）でも init-00423 の見出しの拡大（`graph-1440-{light,dark}-next-heading.png`）で同じ。構造の図の `specdockCmdAudit` も `heads` 0、違反0、`spotDrift` 0.4。
- 写せなかったもの：帯だけの入れ物の枠（R-03）の実例。試しの親のいるリポジトリは、子のリポジトリの入れ物の枠として『これから』でも出るので、例外が効く場面にならなかった（node のテスト T-01・T-02 と偽の DOM の T-05 が、出る・消えるを確かめている）。
- 本人が見る試しの URL：tailnet の 18617 の `/graph`（横断の構造）と `/r/github.com/chemitaro/spec-dock/graph`（`57517bb32`）。止め方：`.workbench/iss-00617/state/dashboard/server.json` の pid と、`relay_orca.py` の2つ（127.0.0.1 と tailnet の 18817）を止める。

## Residual Risks / Follow-ups

- 帯だけの入れ物の枠（R-03）は、実データで例外が効く場面を写せていない（node・偽の DOM のテストで確かめた）。『これから』で見せる Scope がなく、入れ物の枠でもないリポジトリ（例：Scope のない単独のリポジトリ）の main に親がいる状態で、本人の試しの URL で見られる。
- 長い線：入れ子の枠を深くまたぐ線（会社のリポジトリの帯 → 奥の spec-dock の Issue）は、世界の高さの分だけ長くなる。線を押すことはできないので、帯の押しで目立たせて追う。
- 試しのエージェント3人（統括が用意）は、統括が止める。
