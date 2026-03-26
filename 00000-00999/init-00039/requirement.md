---
種別: 要件定義書（Initiative）
ID: "init-local-00002"
タイトル: "Prototype Feature Expansion"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
---

# init-local-00002 Prototype Feature Expansion — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - `spec-dock` のプロトタイプ価値を、実際に使える機能セットとして拡張する。
  - feature backlog を、architecture maintenance と混ぜずに前進できる initiative として切り出す。
- Secondary:
  - core flow の次に必要な operator value、GitHub lifecycle value、feature completeness を段階的に追加できるようにする。
  - architecture initiative が定義する guardrail の上で、機能追加を継続できる portfolio を持つ。

## 背景と Why now
- 現状の課題:
  - 旧 initiative は dogfooding prototype 全体を一つに抱えており、architecture hardening と feature expansion が混在していた。
  - その結果、機能追加の優先順位と architecture cleanup の優先順位が同じ plan 上で競合しやすかった。
  - prototype を前に進めるには、守るための work と広げるための work を分けたほうが判断しやすい。
- 影響:
  - feature work が architecture concern に吸われると、価値拡張の進捗が見えにくくなる。
  - 逆に architecture issue が未整理のまま feature を増やすと、ガードレールを崩す危険がある。
- なぜ今やるか:
  - architecture-level の致命的破綻は見えていないため、条件付きで feature expansion は継続可能である。
  - ただし、その条件を architecture initiative 側へ分離したうえで、feature initiative は価値拡張に集中したほうが運用しやすい。
- 情報源:
  - `../init-local-00003-architecture-maintenance-and-hardening/requirement.md`
  - `../init-local-00003-architecture-maintenance-and-hardening/plan.md`
  - `../init-local-00003-architecture-maintenance-and-hardening/discussions/001-disc-architecture-gap-review.md`

## 成功指標
- Metric-001:
  - Baseline:
    - feature work と architecture maintenance が同じ initiative で混在し、進める work の意味がぶれやすい。
  - Target:
    - feature expansion の initiative だけを読めば、何の機能価値をどの順序で拡張するかが分かる。
  - 計測方法:
    - plan が feature value 中心の epic だけで構成され、architecture maintenance は dependency / guardrail としてのみ参照されること。
  - 判定時期:
    - initiative 再構成完了時。
- Metric-002:
  - Baseline:
    - prototype の次に足すべき機能群が、hardening や cleanup に埋もれやすい。
  - Target:
    - 機能追加の優先順位が `core value -> collaboration/lifecycle -> operator value -> extras` で説明できる。
  - 計測方法:
    - feature epic が価値単位で整理され、blocker / enabler / later extension が区別されていること。
  - 判定時期:
    - epic 分解時。

## スコープ
- MUST:
  - prototype の機能価値を拡張する。
  - feature backlog を architecture maintenance から分離した portfolio として扱う。
  - 既存の dogfooding runtime baseline を壊さずに、新しい capability を追加する。
  - architecture initiative が定義する sync / compatibility / structural invariant guardrail を前提に feature work を進める。
  - feature epic は、利用者価値と operator value の拡張に直接つながるものだけを扱う。
- MUST NOT:
  - architecture-level cleanup を feature initiative の主目的にしない。
  - provider/generated source-of-truth の再定義や runtime persistence cleanup をこの initiative に抱え込まない。
  - feature convenience のために fail-safe / fail-closed posture を崩さない。
- OUT OF SCOPE:
  - sync contract や compatibility boundary の定義
  - architecture invariant の定義
  - active manifest source-of-truth cleanup
  - create lock の infra port 化などの architecture maintenance work

## 境界
- Always:
  - feature initiative は価値拡張を扱い、architecture maintenance は別 initiative に置く。
  - feature 追加は architecture initiative 側の guardrail を満たした上でのみ行う。
  - feature epic は利用者が体感できる能力追加、operator が運用上得る価値追加、workflow completeness の追加に寄せる。
- Ask:
  - その feature は prototype release blocker か、release enabler か、post-release improvement か。
  - その feature を入れるために architecture initiative 側の課題を先に閉じる必要があるか。
- Never:
  - architecture gap を無視して feature を優先し、既存 baseline を壊すこと。
  - cleanup と機能追加を同じ epic に混在させること。

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を日常的に使う coding agent
  - repo docs を正本として進める開発者
- 運用者:
  - dogfooding workspace を使い続ける maintainer
  - feature rollout の優先順位を判断する人
- 開発者:
  - runtime CLI と shipped scaffold を拡張する開発者
- 影響システム / 領域:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - shipped scaffold docs/templates/system
  - local dogfooding workspace `spec-dock/`

## 非交渉制約
- 互換性:
  - additive change を基本とし、既存の major flow を壊さない。
- セキュリティ / 監査:
  - external mutation は opt-in を維持する。
  - wrong-repo risk を高める convenience は採らない。
- 性能 / 可用性:
  - feature 追加のために validate/sync/doctor の基本信頼性を落とさない。
- 運用:
  - architecture initiative 側の guardrail を無視して feature を入れない。
  - repo docs を正本とし、value-based epic で分解する。

## リスク / 依存
- R-001:
  - architecture initiative 側の課題が先に閉じていないのに feature を積むと、あとで rollback コストが高くなる。
- R-002:
  - feature epic の切り方が粗いと、利用者価値ではなく implementation detail 単位の backlog に戻りやすい。
- D-001:
  - `init-local-00003 Architecture Maintenance and Hardening`

## 未確定事項
- Q-001:
  - 質問:
    - feature epic の優先順を、operator value 先行にするか、workflow completeness 先行にするか。
  - 選択肢:
    - A:
      - core workflow completeness を先に進める。
    - B:
      - operator guidance / convenience を先に進める。
  - 推奨案:
    - A。prototype の feature value を広げる initiative なので、まず「できること」を増やすほうが筋がよい。
  - 影響範囲:
    - plan の epic 順序
