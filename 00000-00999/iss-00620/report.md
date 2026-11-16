---
種別: レポート（Issue）
ID: "iss-00620"
関連GitHub: ["#620"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格（P0・P1 なし、P2 4）。`.workbench/spec-review/iss-00620/round-1.json`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00620`）。P2 4件（rowsOf の名前の衝突、F-03 の歯止めの戻し方、ほかの印の折り返し、幅0の子）はすべて実装の前に反映した（`review-response.md`）。
- round-2（同じレビュアー）：**合格**。P0〜P3 すべて0。結果 `round-2.json`、検査 `round-2.check.json`（valid、status pass、reviewed_sha `d9bb6164d`）。
- round-2 で合格した文書の sha256（後に改めた）：requirement.cue `ae0cf137fdd77381adc0690b2fb4aa2c329eecf6c914232bc51b40fd91e8769c`、design.cue `60f3afdd0ec7cd8f31e50364165ec9bd1b50aba6af0f631a6602f683e70dd2fc`、plan.cue `9c6fbf42da033d142dae3bbfaa94e955a9e5cd7ba47615051c63dd6d955209c2`。

- 仕様の変更1（本人の決定、2026-11-17、統括 msg_c07bd9a3a2d9）：稼働の印は、エージェントがいればいつもほかの印の下の専用の行に左寄せで置く（先の「1行目に収まれば右寄せ」を改めた）。round-3 は、そのレビュー中に次の変更が来たので止めた（評価なし）。
- 仕様の変更2（本人の決定、2026-11-17、統括 msg_a0d7a1c08fcc）：『後に続く』の数は構造の図・凡例とも今のまま残す（dnMark を消すことを範囲から外した）。
- round-4（spec-reviewer opus / high、新しいレビュアー、先の P2 を prior_findings で再確認）：合格（P0・P1 なし、P2 1：枠の置き場を `.gx-fh` の外に出すと、押したときの扱いと淡くする規則から外れる）。反映した（枠の `.gx-agents` は `.gx-fh` の最後の子）。
- round-5（同じレビュアー）：**合格**。P0〜P3 すべて0。`round-5.json`、`round-5.check.json`（valid、pass、reviewed_sha `5de15a1`。実装担当の WIP コミットで、仕様の外）。
- **合格した文書の sha256**：requirement.cue `26055baba339f8d5bc6349578f15c9ad40ea32ac91885a384fd9b1974b19ac5d`、design.cue `e30e8098ad35724eb9674a16b330cd534352b18f6bcf34ea4115498707837a18`、plan.cue `9164afc4a986a987c588a01b09200a96c22d148794428e3c40e6b31d3bb099d4`。

## 実装の記録

- 逸脱 codex-symlink-refusal：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_b3e45e72d5e8、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink で手元のコマンドを起動できず、変更なしで止まった。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium（dispatch ctx_ed9b9a3801df、launch claude / opus / medium）に切り替え、impl-claude と同じ値なので S-01〜S-04 を1つのセッションにまとめた。

## Outcome

## Verification

## Residual Risks / Follow-ups
