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

## Residual Risks / Follow-ups
