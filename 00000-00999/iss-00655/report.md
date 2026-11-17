---
種別: レポート（Issue）
ID: "iss-00655"
関連GitHub: ["#655"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 不合格（P1 1、P2 2、P3 1。main#view のフォーカス、Firefox の横のホイール、画面が隠れているときのテスト、T-03 の符号）→ 全部直した（この worktree の `.workbench/spec-review/iss-00655/review-response.md`）→ round-2 **合格**（P0〜P3 すべて0）。結果は `.workbench/spec-review/iss-00655/round-2.json` と `.check.json`（reviewed_sha `92e26aff7`）。
- **合格した文書の sha256**（round-2）：requirement.cue `58e360d8446f9de5ef53d3493611e2e6522b779b0c98e71366d39477d93e0a1a`、design.cue `a25ff30b4df79205fa712a02ab7e1ccbc2ee809490a571a4f3114e2687b932d6`、plan.cue `a70cd6027249a905b298766576680b2e4a1d44c0491b6cc9b5ac6e94d02a2f6e`、explanation.html `58c1d8099ffb0f8133ee54654a34b994aec3a1bbbb7adf17e82405e0681f4b44`。Epic epic-00654 の requirement.cue `fed47250…f278`、design.cue `539998af…7340`、plan.cue `7262bbbd…60a5`。
- 仕様の変更（2026-11-18）：実機の CDP の値の食い違いへの統括の決定（msg_e0c1b3a11a47、A ＋一続きの判定の引き継ぎ）で、D-02・R-02・F-01・T-01・D-06・explanation.html を直した。round-3 合格（P2 2）→ P2 を直して round-4 **合格**（P0〜P3 すべて0、reviewed_sha `25d5e48d2`。結果は `.workbench/spec-review/iss-00655/round-4.json` と `.check.json`）。セッションの値と手順の割り当ては変えていない。
- **今の合格の sha256**（round-4）：requirement.cue `4aefb2376a2f41326f2486d8b8d23a7f285faac3aa527cb7f2928cd337777732`、design.cue `87ce59e8a4973d7e9690ace66dc92b280d5df9de2ade646701a4dfedf7e95844`、plan.cue `4dbcadfe45ba0a2bed302a8aaaf0327ccd0e0cdbb84d5564a306ca40a8762f64`、explanation.html `51789b8a344fd342f5eb3242e1eab4ab7e227c39419a558e38896fdc9d1a3f62`。Epic の文書は round-2 と同じ。
- 開始のコミット：`92e26aff7256a9a32ba6edd5bc7f790ed8e4f149`。

## Residual Risks / Follow-ups
