---
種別: レポート（Issue）
ID: "iss-00646"
関連GitHub: ["#646"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 **合格**（P0 0、P1 0、P2 3、P3 0）。結果はこの worktree の `.workbench/spec-review/iss-00646/round-1.json` と `.check.json`（reviewed_sha `2fa809271`）。
- **合格した文書の sha256**（round-1）：requirement.cue `a0cac08933fa9294412de17828d1bdba6e7a785e22ee44c981a644a3c743e6bd`、design.cue `6e4f47e0601a91079c6298c76b4e6fc950aa6c828f339cb44084fa61b93801d7`、plan.cue `3fbe3f740ca91d80cc7ada42717341468989404f5fb3972c4be5ee9a7b5faf7e`、explanation.html `f260b115432d4e958ac7611213810e7ab98efa5b9f29add85cd0dd0275b3de8c`。
- P2 の扱い（止めない。文書は変えず、実装と測りで扱う）：
  1. F-02 の時計：`watch(null)`（層を消したとき）でも、止める印の時計を消し `is-still` を外す（ページが裏なら残す）ように実装し、T-03 で確かめる（実装担当への申し送り。F-02 の文言の範囲の実装の判断）。
  2. Epic D-04・R-05（端から端まで2〜3秒、stroke-dashoffset の動き）との食い違い：この Issue の decisions の統括の決定（msg_b598780e1110、40px/秒、切り替えの方式）が置き換える。Epic の文書を直すかどうかは統括に報告して任せる。
  3. 前と後の比べ：S-04 で、直す前（基準のコミットを入れた別の venv、ポート 18647）と後（18646）のサーバーを同じ状態の写しと同じ orca の中継で立て、交互に測り、測りごとに線・切り替えの絵・波紋の数を記録する。

## Residual Risks / Follow-ups
