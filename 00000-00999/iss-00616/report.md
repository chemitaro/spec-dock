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

## 逸脱と判断

## Residual Risks / Follow-ups
