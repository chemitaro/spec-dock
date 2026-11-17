---
種別: レポート（Issue）
ID: "iss-00616"
関連GitHub: ["#616"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし）：round-1 不合格（P0 0、P1 1、P2 3、P3 5）。9件とも直した（`.workbench/spec-review/iss-00616/review-response.md`：箱の CSS を『組がないときの見え方』のただ1つの例外として明記、入れ子の枠の見出しの弧を下へ、帯の詳細の欄の iframe を保つ、帯の z-index と帯の弧を上へ、帯の幅の式、点の流れ 2.5 秒、blur の検査の範囲、ResizeObserver の経路、端の層の目立たせ）。round-2 **合格**（P0 0、P1 0、P2 0、P3 2）。結果はこの worktree の `.workbench/spec-review/iss-00616/round-{1,2}.json` と `.check.json`（reviewed_sha `3f5f8d8e9`）。
- **合格した文書の sha256**：requirement.cue `f7b9edb5e5a9ae9ad8013074cab8416447b31ae649f3cf14416d38edc6032d7e`、design.cue `8c3d0d5b8810b51d47c0b9921845eabacda32ab9f5d35c00a2f68b394fb4192d`、plan.cue `631f969055670bbba61b960b173b39d6e26046b962429e6a4617cdb8b7e31b4d`、explanation.html `51938e4bf6855968e342451f25d14b68d52cbc1f4297410838e0347685ef1159`。
- round-2 の P3（止めない。実装担当への申し送り）：(1) 端の層の stubs にも `--cl-len` を置き、箱の中の短い線の点も流す（D-05 の意図どおり）。(2) plan.cue S-03 の『横断の構造』のテストは、箱の CSS で変わらないはずで、変えない（requirement の制約が優先）。

## 実装の記録

- 開始のコミット `3f5f8d8e9`（origin/main、iss-00621 の PR #637 の後）。
- 基準（impl-claude、最初のセッション）：`3f5f8d8e9` で S-01 の節目のテストのうち既存の3つ（marks_rows・graph_js・graph_fit）が 52 passed。既存の失敗なし（`.workbench/implement/iss-00616/start.md`）。
- S-01（impl-claude）：`layout.js` に `packMarks`・`markSpots` と定数 `MARK_H`・`MARK_LEFT`・`MARK_BOTTOM`・`FRAME_TITLE`・`FRAME_GAP`（`markRows` は `packMarks` から）、新しい `views/graph/command.js`（`commandPairs`・`ownWorktrees`・`placeAgents`・`bandLabel`・`bandItems`・`BAND`・`labelWidth`・`commandModel`・`commandKey`）。`link.len` は 8 の倍数に切り上げ、stubs も同じ `len` で流せる（round-2 P3 の申し送り）。テスト `tests/js/dashboard_graph_command.mjs` と `tests/unit/presentation/test_dashboard_graph_command.py`（T-01〜T-03、30件）。Red は開始のコミットの資産で確かめた（`command.js` がない・`packMarks` がない）。
- S-02 も同じ順（実装を先に、テストを後に）で、Red は開始のコミットの資産に対して確かめた。
  - `uv run pytest tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_graph_marks_rows.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_fit.py -q` → 82 passed。
  - `uv run ruff check`・`ruff format --check`・`mypy`（新しいテスト）→ 合格。
- S-02（impl-claude）：`graph.js` に `paintCommand`（`paintOrca` の `checkRows()` の後と ResizeObserver の後。鍵 `commandKey` が同じなら何もしない）、指揮の層 `.gx-cmd`（最後の枠の後）・端の層 `.gx-cmd-top`（依存の線の前）・帯 `.gx-band`（世界の最後）、指揮の選び `V.cmdSel`（帯のボタン・箱と枠の見出しの印・Esc・閉じる・空いたところ）、帯のエージェントの詳細の欄（`agentFrame` と `AGENT_SANDBOX` の iframe。同じエージェントと同じテーマなら書き直さない）、初めの見え方と『収める』の外接の四角に帯の上の縁、`window.specdockCmdAudit`。`graph.css` に層・帯・線・波紋・減らす設定と箱の印の行を底に寄せる規則、`app.css` の3か所に `--sd-cmd`・`--sd-cmd-glow`、`draw.js` の `renderLegend(el, open, {cmd})`（既定は今と同じ）。`fake_dom.mjs` に `insertBefore` と偽の orca の `summary()`・`orderAgents`・`set({summary})`（今の呼び手は変わらない）。テスト `tests/js/dashboard_graph_command_screen.mjs` と `tests/unit/presentation/test_dashboard_graph_command_screen.py`（T-04・T-05、21件）。Red は開始のコミットの資産で確かめた（CSS に札がない、帯のボタンがない）。
  - 既存のテストの直し：`test_dashboard_graph_golden.py` は、Orca のある run（`marks`）の凡例から指揮の2行を除いて比べる（2行があることも確かめる）。違いがその2行だけであることを、写しの全 run・全段で確かめた（ほかの部分の差は0）。写し（`graph_dom_golden.json`）は書き直していない。`test_dashboard_orca_views_js.py` の固定した行に合わせ、`graph.js` の import の行と `V.pn?.openAgent(markAgentAt(slot, target));` の行をそのまま残した。
  - `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py -q` → 281 passed。`ruff check`・`ruff format --check`（tests、src/spec_dock）合格、新しいテストの mypy 合格。
  - 画面の写しは S-02 では撮っていない（S-04 の実機の確かめに任せる）。

## 逸脱と判断

- S-01 は plan.cue では impl-sol（Codex）だが、Codex が chat-scratch の symlink の拒否で止まったため、統括が了承済みの取り決め（plan.cue の impl-sol の rationale）どおり impl-claude（Claude Opus 5.5 / medium）が S-01 から引き継いだ。
- S-01 の TDD の順：`layout.js` の変更を先に書き、テストを後に書いた。Red は、開始のコミットの資産（`git archive 3f5f8d8e9`）に対して新しいテストの node の部分を走らせて確かめた（`command.js` がない・`packMarks` がない）。

- 2026-11-17 タスク担当：S-01 は plan.cue では impl-sol（Codex GPT-6.1 Sol / medium、dispatch `ctx_9b2613c74505`、launch.effective は計画どおり）だが、Codex が chat-scratch の symlink の拒否で何も変えずに止まったので、統括が了承済みの取り決めどおり止め（worker-stop）、Claude Opus 5.5 / medium（impl-claude、dispatch `ctx_1cbbfb48a81d`）が S-01 から S-03 まで引き継ぐ。

## Residual Risks / Follow-ups
