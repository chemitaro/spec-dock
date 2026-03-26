---
種別: 要件定義書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
---

# init-local-00003 Architecture Maintenance and Hardening — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - prototype の継続開発を支える architecture maintenance / governance / hardening を独立 initiative として扱う。
  - feature expansion を無理なく進められるよう、sync contract、compatibility boundary、structural invariant、state boundary cleanup を閉じる。
- Secondary:
  - 旧 initiative で混在していた architecture concern を、独立した投資単位として管理できるようにする。
  - `大きな構造破綻はないが、放置すると後で効く課題` を先回りで整理する。

## 背景と Why now
- 現状の課題:
  - 第三者レビューでは、全面的な architecture failure は見えなかった。
  - しかし、provider/generated sync contract、compatibility boundary、structural verification、active-state source-of-truth、create lock layer leak など、放置すると feature expansion を不安定にする課題が見つかった。
  - これらは細かい bugfix ではなく、architecture / governance / hardening のテーマである。
- 影響:
  - feature initiative に混ぜると価値拡張の優先順位が見えにくくなる。
  - 一方で無視すると、drift、compatibility break、state divergence が後で高コスト化する。
- なぜ今やるか:
  - いまなら致命傷になる前に独立 initiative として閉じ込められる。
  - feature expansion を始める前に、architecture concern の受け皿を切り分けておいたほうがよい。
- 情報源:
  - `discussions/001-disc-architecture-gap-review.md`

## 成功指標
- Metric-001:
  - Baseline:
    - sync / compatibility / invariant が暗黙で、feature 追加時の判断が運用者依存になりやすい。
  - Target:
    - architecture guardrail が docs と issue backlog に落ちている。
  - 計測方法:
    - sync contract、compatibility boundary、structural invariant が docs 化されていること。
  - 判定時期:
    - architecture initiative の初期整理完了時。
- Metric-002:
  - Baseline:
    - active-state source-of-truth や create lock の責務漏れが実装上残っている。
  - Target:
    - architecture cleanup 対象が明確な issue として切り出されている。
  - 計測方法:
    - cleanup 対象が epic / issue に配置され、feature initiative から切り離されていること。
  - 判定時期:
    - epic 分解時。

## スコープ
- MUST:
  - sync contract を定義する。
  - shipped runtime / scaffold / generated workspace の compatibility boundary を定義する。
  - architecture health review 用の structural invariant を定義する。
  - active-state source-of-truth cleanup と create lock layer cleanup を architecture issue として扱う。
  - unresolved safety ownership を整理する。
- MUST NOT:
  - 新しい feature value を主目的にしない。
  - feature convenience のための work を architecture initiative に抱え込まない。
  - 大規模な全面再設計を前提にしない。
- OUT OF SCOPE:
  - collaboration / lifecycle / operator value の feature expansion
  - prototype feature breadth の拡大

## 境界
- Always:
  - architecture initiative は feature value ではなく、guardrail と hardening を扱う。
  - `問題なし` を言うためではなく、`問題の所在を先に閉じる` ための initiative とする。
  - baseline は再実装対象ではなく、差分と gap を閉じる対象とする。
- Ask:
  - その課題は release blocker か、feature enabler か、later maintenance か。
  - その問題は docs/gov で閉じるべきか、実装 cleanup で閉じるべきか。
- Never:
  - feature backlog の受け皿として使うこと。
  - structure problem を曖昧にしたまま `大丈夫そう` で進めること。

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を dogfooding する coding agent
- 運用者:
  - generated workspace と docs parity を維持する maintainer
- 開発者:
  - runtime / scaffold / installer の境界を守る開発者
- 影響システム / 領域:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/`
  - `spec-dock/`

## 非交渉制約
- 互換性:
  - additive migration を原則とする。
- セキュリティ / 監査:
  - fail-safe / fail-closed posture を壊さない。
- 性能 / 可用性:
  - validate/sync/doctor の基本信頼性を落とさない。
- 運用:
  - source-of-truth と sync path を曖昧にしない。
  - feature initiative とは役割分担を維持する。

## リスク / 依存
- R-001:
  - cleanup だけに寄りすぎると終わらない maintenance initiative になる。
- R-002:
  - docs/gov だけで止まると、実装上の leak が残る。
- D-001:
  - feature initiative との優先順位調整

## 未確定事項
- Q-001:
  - 質問:
    - create lock layer cleanup と active-state source-of-truth cleanup のどちらを先に着手するか。
  - 選択肢:
    - A:
      - active-state source-of-truth cleanup
    - B:
      - create lock layer cleanup
  - 推奨案:
    - A。source-of-truth 二重化のほうが drift と実行経路差分を増やしやすいため。
  - 影響範囲:
    - architecture cleanup epic の順序
