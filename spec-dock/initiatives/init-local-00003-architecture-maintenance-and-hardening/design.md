---
種別: 設計書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-27"
依存: ["requirement.md"]
---

# init-local-00003 Architecture Maintenance and Hardening — 設計（HOW / Guardrails）

## initiative としての設計方針
- この initiative は open-ended architecture initiative として運用する。
- 役割は「architecture concern の受け皿」であり、「単発の達成条件を持つ project」ではない。
- そのため initiative docs は固定的な完成像ではなく、architecture epic を継続的に受け入れる portfolio guardrail を定義する。

## 現状と目指す姿
- As-Is:
  - architecture issue は散発的に見つかっているが、single GitHub repo 前提・GitHub mandatory identity・ADR mirror workflow といった新 contract を受け入れる initiative definition にはなっていない。
  - 旧 dogfooding workspace を保守対象とみなすと、強い contract change を入れにくい。
- To-Be:
  - initiative は architecture contract change を継続的に受け入れる。
  - 旧 workspace は disposable / rebuildable とみなし、新 contract を優先できる。
  - 各 epic は source-of-truth、identity、naming、sync、state boundary のいずれかを局所的に閉じる。
  - current legacy workspace 上の planning artifact path は暫定物であり、rebuild 後の runtime policy を拘束しない。

### UML（high-level context / target-state）
```plantuml
@startuml
skinparam monochrome true
left to right direction

rectangle "open-ended initiative" as initiative
rectangle "architecture epic portfolio" as epics
rectangle "new runtime / docs contracts" as contracts
rectangle "rebuildable dogfooding workspace" as dogfood

initiative --> epics
epics --> contracts
contracts --> dogfood
@enduml
```

## 構造原則
- portfolio principle:
  - architecture concern は epic として切り出す。
- contract principle:
  - source-of-truth と generated view を分離して定義する。
- migration principle:
  - 旧 dogfooding workspace の互換維持を第一目的にしない。
- repo principle:
  - single GitHub repo 前提を崩さない。

## initiative が受け入れるテーマ
- identity / linkage contract
- sync / generated artifact contract
- naming / validation contract
- state boundary / source-of-truth cleanup
- runtime / scaffold / docs parity hardening

## initiative が受け入れないテーマ
- feature value enhancement
- multi-repo / multi-tracker strategy
- temporary local-only workaround の恒久化

## ロールアウト原則
- rollout strategy:
  - 旧 workspace を守るための dual-mode を持ち込まない。
  - 新 contract を docs で固定し、epic 単位で実装と tests を追随させる。
  - dogfooding workspace は必要に応じて再構築してデータ移行する。
- rollback principle:
  - rollback は旧 contract 復帰ではなく、issue 単位で変更を戻す。
  - initiative として local-only contract を復活させない。

## ガードレール
- source-of-truth:
  - 1 つに固定する。
- generated artifacts:
  - 再生成可能な view として扱う。
- compatibility:
  - backward compatibility は原則より下位。必要なら明示的に理由を書く。
- docs parity:
  - provider-side docs と dogfooding docs の不整合を放置しない。

## 観測性 / NFR 原則
- observability:
  - contract change は validate / sync / tests で観測できること。
- reliability:
  - rebuild と migration の境界が docs に明記されること。
- operations:
  - maintainer が「何を rebuild してよいか」を判断できること。

## initiative レベルの主要リスク
- R-001:
  - open-ended を理由に epic の抽象度が下がりすぎる。
- R-002:
  - rebuild 前提を使って docs / tests の整合確認を省略してしまう。
- R-003:
  - non-goal が曖昧で feature backlog を取り込んでしまう。

## 関連 ADR
- `epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/discussions/002-adr-github-mandatory-node-linkage.md`
- `epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/discussions/001-adr-adr-symlink-mirror-without-index.md`

## 未確定事項
- Q-001:
  - 質問:
    - open-ended initiative の棚卸し cadence を明示するか。
  - 選択肢:
    - A:
      - epic 追加時に都度見直す
    - B:
      - 定期 cadence を持つ
  - 推奨案:
    - A。まずは epic 追加時の見直しに留める。
  - 影響範囲:
    - initiative maintenance process
