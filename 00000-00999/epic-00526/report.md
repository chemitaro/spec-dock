---
種別: レポート（Epic）
ID: "epic-00526"
関連GitHub: ["#526"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 2026-11-14：要件・設計・計画を、統括の決定（Orca の依頼 task_87517b448497）どおりに書き、子の Issue に切り分けた。
  - iss-00593「横の欄と詳しい画面に「エージェント」のタブを足し、orca-web のチャットを埋め込む」（strict）
  - 依存：iss-00593 → iss-00591（epic-00471）、iss-00593 → iss-00589（epic-00573、2026-11-14 に完了）。
- 統括の決定に足した設計の判断（requirement.cue の decisions の最後の2つ）：「エージェントがいるときだけ出す」は orca-web を読めているときの条件で、読めないときは worktree の記録のある Scope にだけタブを出して理由を示す。埋め込みの画面では iframe を置かず知らせを出す。
- レビューで固めた、相手の選びの決まり：1人のときの自動の選びも選びとして覚える。選んだ相手がいなくなったら `gone:<id>` の印を付け、同じ id が戻っても、残った別の相手がいても、人が選び直すまで開かない。タブの中身の HTML は選んだ相手と明暗と理由だけで決め、一覧は置き場に後から描く（ほかの相手の増減で iframe を作り直さない）。選んだ相手のブランチか種類が変わったときは、確かめ直せるよう置き直す。送信の確かめは、iss-00593 を名指す確かめ専用の worktree の、作業を任せていないエージェントにだけ送る（常駐の orca-web の `sendEnabled` は統括の了承を得て確かめの間だけ有効にする）。

## レビュー記録

- 2026-11-14 仕様レビュー：合格（round-4）。strict なので2人。
  - 対象の sha256（合格の版）：requirement.cue `bfda1113b0e6fcbbb9b5b9f80f4e2d18acb15f81d86e4bd8dff6e44ee21e7dd2`、design.cue `59cd175fffeefcfdadbccd36f24160f8e61948d34f1a1f10206daf86e207d771`、plan.cue `9b554a5dfa90e13862715ac13e4049aa7135467f19ef7cb08c723d81f10cb36a`、explanation.html `478c8adfeecf9a6a21c79875bc2ea51b398958c662a864648319527e9462aae5`。カタログの `spec-dock/canonical` の `1a15a10e17778e2bacb8f5242d0e32b2f9ede304`（GitHub と一致）。main の HEAD `89f51588a`（clean）。
  - spec-reviewer（Opus 5.5 / high、同じレビュアー）：round-1 fail（P1 2、P2 2、P3 2）→ round-2 pass（P3 1）→ round-3 pass（0）→ round-4 pass（0）。結果は main のチェックアウトの `.workbench/spec-review/epic-00526/round-{1..4}.json`（検査 `round-{n}.check.json`、すべて valid）。
  - 2人目 ChatGPT（GPT-6 / Extra High、`chatgpt-spec-review-strict`、カタログの SHA に固定して GitHub の接続で読んだ）：round-1 fail（P1 3）→ round-2 fail（P1 1、P2 1）→ round-3 fail（P1 1）→ round-4 pass（0、確信 0.96）。結果は `.workbench/spec-review/epic-00526/chatgpt-{1..4}.json`。モデルの選択の証拠は round-1 で verified、round-2〜4（同じ会話の続き）は `status=skipped; verified=no; source=config`（思考の深さ Extra High はどの回も verified）。別のモデルだという証拠はないが、確かめられていないものとして記録する。
  - P0/P1 はすべて訂正した。分析と訂正は `.workbench/spec-review/epic-00526/review-response.md`。合格の版の P2/P3 は 0。

## Verification

- `spec-dock scope check epic-00526`：誤りなし、警告なし（2026-11-14）。

## Residual Risks / Follow-ups

- design.cue の risks を参照（`/embed/agent` の契約の変化、sandbox を付けない iframe、エージェントの多い worktree の一覧、宛先の指紋が守れない範囲）。
- iss-00593 の担当は、iframe の sandbox の形を試して決め、report.md に残す（D-03）。
