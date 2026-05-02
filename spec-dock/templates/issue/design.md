---
種別: 設計書（Issue）
ID: "<ISS_ID>"
タイトル: "<ISS_TITLE>"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md"]
親: ["<EPIC_ID>", "<INIT_ID>"]
---

# <ISS_ID> <ISS_TITLE> — 設計（HOW）

## Parent Diagram References
- Epic diagrams:
  - ...
- Initiative diagrams:
  - ...
- reused decisions:
  - ...

## 目的・制約
- 目的:
  - ...
- MUST / MUST NOT:
  - ...
- 非交渉制約:
  - ...
- 前提:
  - ...

## 既存実装 / 規約の理解
- 参照した実装 / docs:
  - ...
- 現状理解:
  - ...
- 採用するパターン:
  - ...
- 採用しないもの:
  - ...
- 影響範囲:
  - ...

## 採用方針 / トレードオフ
- 論点:
  - ...
- 選択肢:
  - ...
- 決定:
  - ...

## 依存関係分析
- upstream / prerequisite:
  - ...
- downstream / dependent:
  - ...
- 実装起点:
  - 依存の少ないもの / 先に固定すべき interface / 先に通すべき test を書く
- sequencing implications:
  - plan では upstream / prerequisite から順に step を組む

## Local Diagram Delta
- Question answered:
  - ...
- Scope:
  - ...
- Excluded details:
  - ...
- Update trigger:
  - ...
- Diagram:
  - N/A: reason

### UML（必要時: local diagram delta / package delta）
```plantuml
@startuml
top to bottom direction
' show only the changed boundary, responsibility, dependency, or interaction
' do not copy Initiative/Epic diagrams

rectangle "replace-with-module-a" as A
rectangle "replace-with-module-b" as B
A --> B : depends_on
@enduml
```

## インターフェース契約
- API / function / protocol / data boundary:
  - ...

## Sequence Delta（必要時）
- changed interaction:
  - N/A: reason
- retry / transaction / external API / queue:
  - ...

### UML（任意: sequence delta）
```plantuml
@startuml
' sequence delta diagram
@enduml
```

## Domain Model Delta（必要時）
- parent model refs:
  - ...
- aggregate / entity / value object changes:
  - N/A: reason
- domain event / policy / specification changes:
  - ...
- invariant changes:
  - ...

### UML（任意: domain model delta）
```plantuml
@startuml
' domain model delta diagram
@enduml
```

## クラス / インターフェース詳細設計（必要時）
- Class / Interface:
  - ...
- responsibility:
  - ...
- collaboration:
  - ...

### UML（任意: class / interface）
```plantuml
@startuml
' class / interface diagram
@enduml
```

## 変更計画
- Add:
  - ...
- Modify:
  - ...
- Delete:
  - ...
- Move/Rename:
  - ...
- Read only:
  - ...

## 要件 → 設計マッピング
- AC-001 -> ...
- EC-001 -> ...
- constraint -> ...

## テスト戦略
- Unit:
  - ...
- Integration:
  - ...
- E2E / manual:
  - ...
- migration / rollback / feature flag if needed:
  - ...

## 要件 / 例外 -> verification mapping
- AC-001 -> ...
- EC-001 -> ...
- constraint -> ...

## リスク / 移行 / ロールバック（必要時）
- ...

## 未確定事項
- Q-001:
  - 質問:
  - 選択肢:
    - A:
      - ...
    - B:
      - ...
  - 推奨案:
    - ...
  - 影響範囲:
    - ...
