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

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 fail（P1 1・P2 2・P3 2）、round-2 fail（P1 1：wrap-reverse の送り）、round-3 **合格**（P0 0、P1 0、P2 1、P3 0）。結果はこの worktree の `.workbench/spec-review/iss-00656/round-{1,2,3}.json` と `.check.json`、対応は `review-response.md`（reviewed_sha `92e26aff7`、文書は sha256 で固定）。
- **合格した文書の sha256**（round-3）：requirement.cue `aeb8c7014d23c5bee83b2afb781206b399c82424b2160c68f01ea5c8c6c134cd`、design.cue `8691ec8614b18aeee76f34792130f2bf03ddbb74b1b3b701589af9e65a6e4f8e`、plan.cue `16b8009c5f495a740b033933059d530067b2dde02bc2d1b3b5b44b9b774bfd28`、explanation.html `8383f56b3f24c061150acad84251cc32ea9e1bf08a107b4218fc4aa2b7ddea86`。Epic epic-00573 の R-06・D-06・slice `iss-00656` も同じ回で読まれた。
- P2 の扱い（止めない。文書は変えず、実装で扱う。実装担当への申し送り）：`fitHead` を、D-07 の3つの時に加えて、スマートフォンの段の切り替え（`applySnap()` の後。全体の段で `is-stacked` を外し、戻したら測り直す）と、見出しの幅の変化（Orca で開くの遅れた表示など。`.pn-head` の `ResizeObserver`、ないときは今の3つだけ）でも呼ぶ。T-02 に、段の切り替えと見出しの幅の変化で送りが付け直されることを足す。
- 申し送り（指摘でない懸念）：1000×800・祖先2つ・印2つで1行に収まる余地は小さい見込み。S-04 の実機で R-01 の受入[2]を測り、届かなければ統括に問う。

## Residual Risks / Follow-ups
