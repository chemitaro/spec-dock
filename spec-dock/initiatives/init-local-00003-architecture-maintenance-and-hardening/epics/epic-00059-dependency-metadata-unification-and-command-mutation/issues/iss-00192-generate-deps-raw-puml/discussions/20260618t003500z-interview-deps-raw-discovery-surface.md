---
種別: interview
ID: "20260618t003500z-interview"
タイトル: "deps-raw Discovery Surface"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00192"]
関連:
  - "20260617t154655z-research"
  - "20260617t154656z-interview"
  - "20260618t001154z-disc"
  - "20260618t002930z-deps-raw-flat-visual-simulation.puml"
authority: "user-approved"
derived_from:
  - "requirement.md"
  - "report.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/markdown.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py"
reflected_to:
  - "requirement.md"
  - "report.md"
---

# 20260618t003500z-interview deps-raw Discovery Surface

## 正式質問として扱う理由
- `requirement.md` は `dashboard または sync output から deps-raw.puml の存在を発見できる` ことを要求している。
- 既存の generated artifact は dashboard / context pack / sync output に複数の発見導線を持つ。
- どこまで発見導線を増やすかで、実装範囲、テスト期待値、ユーザーの通常フローが変わる。

## 質問の目的
- `deps-raw.puml` をどの画面・出力から見つけられるべきかを決める。
- MVP として過不足のない discovery contract を固定する。

## 質問
`deps-raw.puml` の発見導線は、どこまで入れたいですか？

## 選択肢
- Option A: dashboard の Observability / generated artifacts list に追加するだけ。
  - 最小実装。既存の `dashboard.md` を見れば見つかる。
- Option B: dashboard に加えて、`sync` 完了メッセージにも `deps-raw.puml` を含める。
  - 実行直後にも気づける。CLI output のテスト更新が必要。
- Option C: dashboard、`sync` 完了メッセージ、context pack / active-none guidance まで含める。
  - agent が見つけやすいが、今回の issue としては変更面が広がる。

## 推奨
- Option B。
- 理由:
  - 人間は `sync` 実行直後に生成物を知りたい。
  - agent は dashboard から再発見できる。
  - context pack / active-none guidance まで広げるのは、この issue の主目的から少し外れ、後続でも対応できる。

## 回答欄
- 回答:
  - Option B を採用する。
  - `deps-raw.puml` は dashboard に加えて、`sync` 完了メッセージからも発見できるようにする。
- 採用判断:
  - adopted。
  - dashboard は後から agent / maintainer が artifact を再発見する導線として使う。
  - `sync` 完了メッセージは人間が生成直後に `deps-raw.puml` の存在に気づく導線として使う。
  - context pack / active-none guidance まではこの issue の必須範囲に含めない。
- 反映先:
  - `requirement.md`
  - `report.md` Evidence Adoption Ledger
