---
種別: レポート（Issue）
ID: "iss-00575"
関連GitHub: ["#575"]
最終更新: "2026-11-05"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

構造の図の最上位で、依存でつながっていない Initiative が、行の残りの幅（最小幅 420 以上）に収まり、下の行に積むより高くならないとき、その幅で作り直して同じ行に並ぶようにした（`views/graph/layout.js` の `childrenBlock`）。採った幅は wraps の `root#shares` に残し、配線の広げ直しでは動かさない。依存でつながった Initiative の鎖と Epic などは今までの幅のまま。

- コミット：`c8d5ba8bb`（実装）、`a675f35b8`（鎖と幅の固定のテスト）、`ed6635322`（書式）。

## Verification

- 仕様のレビュー：`spec-reviewer`（opus / medium）が合格（P0・P1 なし）。1回目は私の sha256 の書き写しの誤りで入力の不備、その後の2回は合格。残った P2・P3 は表現の直しとして反映した。最終の文書の sha256：requirement `90f44b05…`、design `f71a1b66…`、plan は手順を done にした後の値（plan.cue の最終の内容）。
- コードのレビュー：`code-reviewer`（sonnet / high）が `c8d5ba8bb` で合格。P2（T-02・T-03 のテストがない）は、鎖のテストと広げ直しの前後の幅のテストを足して直した。広げ直しの固定経路を壊すとテストが落ちることを確かめた。
- 最終品質ゲート（`quality-gate-reviewer` opus / high）：1回目は P1（テストの2行が `ruff format --check` に落ちる）で不合格。整形して `ed6635322` で合格（P0・P1 なし、coverage 完了、P3 が2件）。P3：高さの条件を確かめるテストがない（情報のみ）、report.md が雛形のまま（この記述で解消）。
- テストの段：`make lint`（ruff check、ruff format、mypy）と `uv run pytest`（全体）を `ed6635322` で実行した結果は PR とゲートの closure に残す。1回目の `a675f35b8` では pytest 全体が 3718 passed、7 skipped。
- 実データ（spec-dock の構造、325件）の写し：[PC 1440](artifacts/20261105t131850z--pc-1440-graph-fit.png)、[PC 1000](artifacts/20261105t131850z-01--pc-1000-graph-fit.png)、[390px](artifacts/20261105t131851z--390-graph-fit.png)、[結果](artifacts/20261105t131851z-01--result.json)。一時の状態の置き場（`.workbench/iss-00575/browser/state`）に、この PC のスナップショットを写し（取得の時刻だけ今に動かし）、`spec-dock dashboard serve --port 18575 --offline` で開いた。headless Chrome は `--disable-features=MacAppCodeSignClone` で起動し、`Browser.close` で閉じた。`window.specdockEdgeAudit()` の違反は 1440、1000、390 のすべてで0件。ページの横のはみ出しなし、ブラウザーのエラー0件。窓の高さだけの変化では配置が変わらず、幅を 1000 にして 1440 に戻すと元の配置に戻る。

## Residual Risks / Follow-ups

- **実データでは、Initiative が横に並ばなかった**（1440、1000、390 のすべてで縦に積み）。理由：先頭の init-00423 は依存の鎖で幅が 1358 まで広がり、init-00079 は中の Epic が折り返して幅 1194 に広がる。残りの幅が最小幅（420）に足りず、作り直しの対象にならない。合成した構造（Initiative が4つ、Epic 1つに Issue 4つずつ）では、幅 1400 で2つずつ並ぶことをテストで確かめた。
- 実データで並べるには、先に置く Initiative を狭める（前の Initiative と次の Initiative で幅を分け合う）案が要る。折り返した中身は面積がほぼ保たれるので、高さが減るのは枠に空きがあるとき（init-00039 は幅 932 で 157px）に限られる。この案は未実装。統括の判断を仰ぐ。
- 高さの条件（下の行に積むより高くなるときは置かない）を確かめるテストはない（ゲートの P3）。
