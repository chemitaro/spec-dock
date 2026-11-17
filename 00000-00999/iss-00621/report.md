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
- 合格の後の変更は、plan.cue の手順の status だけにする。

## 実装の記録

- 開始のコミット `edfabc759`（origin/main、iss-00620・iss-00614・iss-00627 の後）。

## 逸脱と判断

- 2026-11-17 S-01 の担当：plan.cue では impl-sol（Codex GPT-6.1 Sol / medium）だが、Codex が chat-scratch の symlink の拒否で止まったので、統括が了承済みの取り決めどおり、Claude Opus 5.5 / medium（impl-claude）が S-01 から S-03 まで引き継いだ。
- 2026-11-17 実装の判断（D-01 の足し）：`buildMarks` の結果に `marks` の配列がないとき（結合テストの偽の部品 `tests/js/fake_dom.mjs` の `fakeOrca` がそうだった）は、`built.marks.map` が例外を出して置き場を空にしていたので、印はそのまま描き、記録は空の並びにする（押しても F-01 でタブを開くだけ）。印の表示を落とさないための守り。
- 2026-11-17 実装の判断（D-04）：`.gx .gx-fh > .wt { flex: none; }` を足した（設計の「足りなければ」の規則）。題名だけが縮み、worktree の印が縮まず題名の行に残ることを CSS で固める。実機の確かめは S-04。
- 2026-11-17 実装の判断（D-05）：`.sd-card__meta:not(:has(> :not(.sd-orca:empty))) { display: none; }` は残した（置き場が meta の外へ出て効かなくなるが、消しても HTML は同じで、既存の静的な検査を変えずに済む）。T-03 の node のテストは、計画のとおり `test_dashboard_orca_views_js.py` の `run_panel` に、エージェントのいる構造を足して書いた（`El.prototype.querySelector` をその中だけ足した）。

## 実機の確かめ

## Residual Risks / Follow-ups
