---
種別: レポート（Issue）
ID: "iss-00603"
関連GitHub: ["#603"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格（P0・P1 なし、P2 2・P3 2）。`.workbench/spec-review/iss-00603/round-1.json`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00603`）。P2 1件（テストの抜け）と P3 2件を反映（`review-response.md`）。
- round-2（同じレビュアー）：**合格**。P0・P1 なし、P2 1（凡例の文と木のいま・入れ子の b の枠の食い違い。凡例の文は統括の決定 msg_237502e135aa どおりなので記録だけ。次の提案に回す）。結果 `round-2.json`、検査 `round-2.check.json`（valid、status pass）。
- 合格した文書の sha256：requirement.cue `01b97b1821ba14484808a3e220a48ed6e84567a13b990ec4c1dea31038c3bcc4`、design.cue `76171726cd81868d2be1ead5a7d8b01b2248683a4eab72ddd053dceae67f650b`、plan.cue `887fcbfb7689731dd7abf92fcd0de3f32c54bcf272fe5b2a815f6bceda9b2fe1`。
- 逸脱 codex-symlink-refusal（タスク担当の記録）：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_f14e1d68e729）は、手元のコマンドの実行の前に chat-scratch の writable root の symlink による UnsupportedOperation で止まり、変更なしで failed を返した。plan の rationale と統括の了承どおり、待たずに Claude Opus 5.5 / medium（dispatch ctx_bdbc48a1d80d、launch.effective claude / claude-opus-5-5 / medium）に切り替えた。
- CP-1（code-reviewer opus / medium、範囲 `16f0cf122..63bda08e3`、S-01〜S-03、axis both）：**合格**。P0〜P2 なし、P3 1（T-03 の合成の構造に止められている c がない）。結果 `.workbench/code-review/iss-00603/cp1-round-1.json`、検査 `cp1-round-1.check.json`（valid、status pass）。P3 は S-04 の担当にあわせて足してもらう。タスク担当が手元で構造の図のテスト 56 passed を確かめた。

## 実装の記録（impl-sol の代わり：Claude Opus 5.5 / medium）

- 逸脱 codex-symlink-refusal：plan の impl-sol（codex gpt-6.1-sol / medium）が chat-scratch の symlink の拒否で起動できず、plan の rationale と統括の了承どおり Claude Opus 5.5 / medium で S-01〜S-03 を実装した（逸脱の正式な記録はタスク担当が書く）。
- 開始のコミット `16f0cf122cb2053f4f4e24cf844f505f5274c30d`。基準（同じコミット）：`make lint` pass、`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py` 38 passed。記録 `.workbench/implement/iss-00603/start.md`。
- S-01（Red）`71fb7097c`：`tests/unit/presentation/test_dashboard_graph_range.py` を足した（T-01・T-02 は開始のコミットで記録した配置の digest `tests/fixtures/issue603/layout-before.json` と比べる。4つの構造 × 入れ子・木 × 線 all・wait × 幅 既定・374 × 配線の前後。range だけ、range なし、古い showDone・fold を添えた呼び出し、誤った range を含む。T-03〜T-05 と T-07 は合成の構造）。`dashboard_graph_check.mjs` の組み合わせを range（all・now・next）にし、focus に next（入れ子・木、終わったもの・候補の Epic も）を足した。既存の showDone・fold の組を range に書き換え（全体は range all、いまで fold 偽の組は木と「いま」の畳んだ塊の検査に置き換え）、保存のテストを版3・版2・版1・壊れた値に書き換えた（T-06）。直す前のコードで 17 failed・39 passed（range を読まないための失敗）を確かめた。
- S-02（Green）`7589b8318`：layout.js に D-01（range の正規化。呼ぶ側の showDone・fold は使わない）、D-02（next の見せる判定、showsDone は常に偽）、D-03（next では端が done の組を飛ばす）。`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py`：54 passed、2 failed（S-03 の保存の2件だけ）。next を含むすべての組み合わせで edgeAudit の違反0。`make lint` pass。
- S-03 `63bda08e3`：prefs.js を版3（`PREFS_KEY = "specdock.graph.v3"`、`LEGACY_KEYS = ["specdock.graph.v2", "specdock.graph.v1"]`、`restorePrefs(current, legacies, defaults)`）にし、graph.js の loadPrefs・savePrefs を `{mode, range, deps, legend}` に合わせた。`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py`：56 passed。`uv run pytest tests/unit/infra/test_dashboard_shell_polish.py tests/unit/infra/test_dashboard_state_marks.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_scope_tabs_js.py`：53 passed。`make lint` pass。
- S-04 への引き継ぎ：graph.js の道具の帯の `done`・`fold` のボタン（`o.showDone`・`o.fold` を切り替える）は S-04 で range の切り替えに置き換える。S-03 の時点ではこの2つのボタンは layout に効かない（layout は range だけを読む）。T-11（押したときの保存の4つの鍵）は S-04 の範囲。
- impl-ui（Claude Opus 5.5 / medium、plan の execution.sessions.impl-ui どおり、dispatch ctx_aa2c7426f15c）が S-04・S-05 を担当。開始の前に requirement・design の sha256 が合格の値と一致することを確かめた。plan.cue は `5d06eded…` で合格の `887fcbfb…` と違うが、前のセッションが S-01〜S-03 の status を done にした分と見た（仕様は Git の外で、差分は直接は確かめられない）。
- S-04（Red）`b999b18df`：`tests/js/dashboard_graph_toolbar.mjs`（graph.js を node で、HTML の文字を持つだけの最小の DOM の代わりで描き、画面の click の listener でボタンを押し、各部品の HTML と localStorage を返す）と `tests/unit/presentation/test_dashboard_graph_toolbar.py`（T-08・T-11、入れ子・木、版2からの移し替え、すべて終わった構造でのこれからの知らせ）を足した。CP-1 の P3 として T-03 の合成の構造に、閉じた親 20 の下の止められている c（`iss-00023`、blocked_by 61）を足し、state blocked で cleanup に入り、これからで出ず、全体で出ることを確かめた（`test_dashboard_graph_range.py` 18 passed）。直す前のコードで toolbar のテスト 12 failed（done のボタンがある、range がない、知らせの要素がない）。
- S-04（Green）`8ae1600af`：graph.js に D-05（done・fold のボタンを消し、入れ子/木のすぐ後に role=group aria-label「見せる範囲」の3つ。icon layers・clock・sparkle、title「見せる範囲：…」。onClick は `o.range = act.dataset.range`。fit は見える文字「収める」、title・aria-label「画面に収める」）、D-06（`clnMark` を枠と箱で共有。箱（木の枠の箱を含む）は range all のときだけ、枠は next 以外。凡例の文を wide で）、D-07（`.gx-view` の中の `<p class="gx-none">`。next で nodes が0のときだけ文を出し、帯は残す）。`.gx-world` に `data-range` を足した（テストと CSS が読む）。graph.css に `.gx-none` の配置だけ（色は既存の `--ds-muted`。新しい色の値なし＝T-09）。390px は既存の `.tool-group[role="group"]` の規則がそのまま効く（ブラウザーでの写しは S-06）。テスト側は古いボタンの検査を aria-label「終わったものも」に絞った（title「全体（終わったものも、…）」が正しく含むため）。
  - `uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py tests/unit/infra/test_dashboard_shell_polish.py tests/unit/infra/test_dashboard_state_marks.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_scope_tabs_js.py tests/unit/infra/test_dashboard_orca_marks_js.py`：126 passed。`tests/unit/presentation/test_dashboard_small_screens.py`：2 passed。`make lint` pass。dashboard の資産は static-inventory.json に載っていないので更新なし。
- S-05（HEAD `8ae1600af`、コードの変更なし）：`make lint` pass（ruff check・ruff format check・mypy）。`uv run pytest`（全体）：3942 passed、7 skipped、1802s（開始時の uptime load 5.9）。新しい失敗・既存の失敗ともになし。ログ `.workbench/implement/iss-00603/s05-pytest.log`。

## Outcome

## Verification

## Residual Risks / Follow-ups
