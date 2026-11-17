---
種別: レポート（Issue）
ID: "iss-00656"
関連GitHub: ["#656"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし。同じレビュアーで続けた）：round-1 fail（P1 1・P2 2・P3 2）、round-2 fail（P1 1：wrap-reverse の送り）、round-3 合格（P2 1）、統括の追加（R-09、msg_0358bd3f97b4）の後の round-4 **合格**（P0 0、P1 0、P2 1、P3 1。reviewed_sha `afe2df5c2`＝iss-00650 のマージ後の origin/main）。結果はこの worktree の `.workbench/spec-review/iss-00656/round-{1,2,3,4}.json` と `.check.json`、対応は `review-response.md`。
- **合格した文書の sha256**（round-4）：requirement.cue `9bdd0e9e516691f0b68205bc6b1d0537856465d3b758c70a41122ed52a799a91`、design.cue `b13005c09856a9ba33700d8e9bcac89328322adeb97947a3818860b97fcbe818`、plan.cue `e86defd4a9c2b9d8fc555d30e8aac033de35105700ecf2535e54bfcfb5fb7492`、explanation.html `8383f56b3f24c061150acad84251cc32ea9e1bf08a107b4218fc4aa2b7ddea86`。Epic epic-00573 の R-06・D-06・slice `iss-00656` も同じ回で読まれた。
- P2 の扱い（round-3・4 で同じ指摘。止めない。文書は変えず、実装担当への申し送り）：`fitHead` を、D-07 の3つの時に加えて、スマートフォンの段の切り替え（`release`・`pointercancel`・取っ手のタップの `applySnap()` の後。全体の段で `is-stacked` を外し、戻したら測り直す）と、見出しの幅の変化（Orca で開くの遅れた表示など。`.pn-head` の `ResizeObserver`、ないときは今の3つだけ）でも呼ぶ。T-02 に、段の切り替えと見出しの幅の変化で送りが付け直されることを足す。
- P3 の扱い：D-08 は、帯の欄（`renderAgentPanel`）の描き直し（別のエージェントへの切り替え、明暗の変化）でも全面を保つ（今は半分に戻る）。片付けの候補と同じ考え（開いている欄の描き直しで段を変えない）なので受け入れ、統括に報告する。直しは構造の図（`graph.js`）の片付けの候補にも効く。
- 申し送り（指摘でない懸念）：1000×800・祖先2つ・印2つで1行に収まる余地は小さい見込み。S-04 の実機で R-01 の受入[2]を測り、届かなければ統括に問う。

## Residual Risks / Follow-ups
