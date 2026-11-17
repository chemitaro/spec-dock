---
種別: レポート（Issue）
ID: "iss-00621"
関連GitHub: ["#621"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし）：round-1 合格（P0 0、P1 0、P2 3、P3 2）。5件とも直した（`.workbench/spec-review/iss-00621/review-response.md`：iss-00616 への `markIds` の口、0人の worktree の札の高さの受入、Epic R-14 の実データの親子の順、S-03 の直してよい理由、仕様のレビューの記録の位置）。round-2 **合格**（P0〜P3 すべて0）。結果はこの worktree の `.workbench/spec-review/iss-00621/round-{1,2}.json` と `.check.json`（reviewed_sha `edfabc759`）。
- **合格した文書の sha256**：requirement.cue `07a0c0733908444f533302c9cb16a1d8e0e428b219dfadb1a3568114fcf4df6b`、design.cue `ab4dc444699c87032298221c44f820073fb417319044bf57bcd8842182f3dcde`、plan.cue `9c3773cb2405ac311a605ae322122ffe4133e99ebe705baeb7ec96b3c2827877`、explanation.html `d686e24d2dbf732e4c1a9ec9821d8456e1616a2b0004fac9ce3e4d56cd1bce42`。
- **仕様の変更（実機の確かめから、2026-11-17）**：枠の見出しの worktree の印が見出しの右の端（幅の広い枠では画面の外）に出たので、題名の広がりを自分の幅までにして印を題名のすぐ後に続ける（requirement.cue の decisions と R-01 の受入4、design.cue D-04、plan.cue T-04）。round-3 **合格**（P0 0、P1 0、P2 1：直しの手順が台帳にない → S-02 を doing、S-03 を todo に開き直した。P3 0）。結果 `.workbench/spec-review/iss-00621/round-3.json`（reviewed_sha `ce999075e`）。
- **今の合格した文書の sha256**（round-3、S-02・S-03 の status の開き直しの前）：requirement.cue `8703d689ccec242a9cc6f1cd704c976197c57d07f9ca8b66ee9e40a0502f6dc5`、design.cue `e9edb9e92b162c813656f4eebba4b605262fa6b410ae95d5eb7b9ab134225c4a`、plan.cue `5a936266977ec84859305278992ae32e44f614d7036d5cac93b5782951810e7a`。その後の変更は plan.cue の手順の status だけ。

## 実装の記録

- 開始のコミット `edfabc759`（origin/main、iss-00620・iss-00614・iss-00627 の後）。
- 開始の基準（`.workbench/implement/iss-00621/start.md`）：S-01 の節目の4ファイルが 63 passed。
- S-01（`dd775ba8d` テスト先行 → `99b375648`）：T-01・T-02（`test_dashboard_orca_marks_js.py`）、T-03（`test_dashboard_orca_views_js.py` の `run_panel`）を書いて落ちることを確かめ、D-01（`orca_marks.js` の WeakMap の記録、`markAgentAt`・`markIds`）、D-02（`panel.js` の `openAgent`）で通した。節目 67 passed。
- S-02（`688d9eca0` テスト先行 → `31bb71d04`）：T-04〜T-06 を書いて落ちることを確かめ、D-03（graph・allgraph・board・panel の押し）、D-04（`draw.js` の枠の見出しと木の枠の箱の `wtMark`、`graph.css` の `.gx .gx-fh > .wt { flex: none; }`）、D-05（`parts.js` の `.sd-card__agents`、`parts.css`）で通した。今の `preferTab("agents")` を固定していた静的な検査と札の HTML の検査は、R-02・R-05 の置き換えに合わせて直した。節目（S-01 の4ファイル＋`test_dashboard_screens_js.py`＋`tests/unit/presentation/`）262 passed。構造の図の golden と線の検査も通る。
- S-03（`124f9b9c7`）：`make lint` 合格（ruff check・format・mypy）。全体の `uv run pytest` は 4073 passed、7 skipped（1898秒）。dashboard の資産は `static-inventory.json` に載っていないので、sha256 の直しは要らなかった。
- 仕様の変更（round-3）の直し（`ce999075e` の上に、`3dfc3e083` テスト先行 → `797690b4f`）：T-04 に、`graph.css` の `.gx :is(.gx-ini, .gx-epic) > .gx-fh > .gx-fttl { max-width: max-content; }` が配置の規則（`max-width: none`）より後にあることの静的な検査を足して落ちることを確かめ、その規則を配置の規則のすぐ後に足して通した。`make lint` 合格、全体の `uv run pytest` 4081 passed、7 skipped（1956秒）。S-02・S-03 を done にした。

## 逸脱と判断

- 2026-11-17 S-01 の担当：plan.cue では impl-sol（Codex GPT-6.1 Sol / medium）だが、Codex が chat-scratch の symlink の拒否で止まったので、統括が了承済みの取り決めどおり、Claude Opus 5.5 / medium（impl-claude）が S-01 から S-03 まで引き継いだ。
- 2026-11-17 実装の判断（D-01 の足し）：`buildMarks` の結果に `marks` の配列がないとき（結合テストの偽の部品 `tests/js/fake_dom.mjs` の `fakeOrca` がそうだった）は、`built.marks.map` が例外を出して置き場を空にしていたので、印はそのまま描き、記録は空の並びにする（押しても F-01 でタブを開くだけ）。印の表示を落とさないための守り。
- 2026-11-17 実装の判断（D-04）：`.gx .gx-fh > .wt { flex: none; }` を足した（設計の「足りなければ」の規則）。題名だけが縮み、worktree の印が縮まず題名の行に残ることを CSS で固める。実機の確かめは S-04。
- 2026-11-17 実装の判断（D-05）：`.sd-card__meta:not(:has(> :not(.sd-orca:empty))) { display: none; }` は残した（置き場が meta の外へ出て効かなくなるが、消しても HTML は同じで、既存の静的な検査を変えずに済む）。T-03 の node のテストは、計画のとおり `test_dashboard_orca_views_js.py` の `run_panel` に、エージェントのいる構造を足して書いた（`El.prototype.querySelector` をその中だけ足した）。

## 実機の確かめ

## Residual Risks / Follow-ups
