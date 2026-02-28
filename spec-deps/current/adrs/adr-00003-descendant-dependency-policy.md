---
種別: ADR（Architecture Decision Record）
ID: "ADR-00003"
タイトル: "descendant（親→配下）依存の扱い: 禁止（fail-fast）を維持するか"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-02-28"
親: ["iss-00010"]
---

# ADR-00003 descendant（親→配下）依存の扱い: 禁止（fail-fast）を維持するか

## 結論（Decision） (必須)
- **未決（TBD）**: この ADR はディスカッションのために作成しました。結論はユーザーが最終決定した後に更新します。
- 決定（決定後に記入）:
  - ...

## 背景（Context） (必須)
deps v2 は shorthand（initiative/epic 参照）を **issue→issue** へ展開します。  
このとき「親が配下に依存する（descendant 参照）」を許すと、展開結果として **自己依存（self-edge）** や **循環（cycle）** を生みやすく、運用上の事故が起きやすいです。

現状（deps v1）の事実:
- `deps.json` では「親→配下（descendant）依存は禁止」というルールが既にあります。
  - ドキュメント: `src/spec_dock/assets/spec_dock/docs/reference_deps.md`（理由も記載）
  - 実運用でも、親依存マージにより自己循環が起きる事例が確認されています（手動テスト指摘）。

v2 では「compile（展開）」が入るため、禁止ルールをどうするかを決める必要があります。

### UML（任意） (任意)
```plantuml
@startuml
left to right direction
skinparam shadowing false

package "epic E (contains)" {
  rectangle "iss-A" as A
  rectangle "iss-G (gate)" as G
}

note top of E
deps.json on epic E:
depends_on=[\"iss-G\"]
end note

rectangle "compile result\n(canonical issue edges)" as C

E --> C : applies to\n(all issues in E)
C --> A : A depends_on G
C --> G : G depends_on G\n(self-edge)

note bottom of G
self-edge は永久blockedの原因。
fail-fast で検出できると安全。
end note
@enduml
```

## 選択肢（Options considered） (必須)

### Option A: descendant 依存は禁止を維持（fail-fast）
概要:
- 「宣言元ノードの subtree（配下）にある node id」を `depends_on` に含めることを構造エラーにする。
- v2 の shorthand 展開でも同様に、展開により self-edge が生まれるケースを “早い段階で” 落とす。

Pros:
- 事故が起きやすいパターンを単純ルールで排除でき、運用が安定する。
- エラーメッセージを「どの deps.json で、どの ref が、なぜ禁止か」まで説明しやすい。

Cons:
- 「epic 内の gate issue に、epic 全体を依存させたい」などの表現が直接できない。
  - 代替は “各 issue が gate issue に依存する（issue→issue を明示）” 等で吸収する必要がある。

### Option B: descendant 依存を許可し、self-edge を自動除外する（特殊ルール）
概要:
- 例: `epic E depends_on iss-G`（G が E 配下）の場合、展開を `E配下の issue（ただしGを除く） -> G` とする。

Pros:
- gate issue パターンを shorthand で表現でき、記述量が減る。

Cons:
- “自分だけ依存が外れる” という例外が直感に反し、仕様理解が難しくなる。
- 他の複雑な循環（G が別依存を持つ等）を誘発しやすい。
- 実装・テスト・説明が重くなる。

### Option C: descendant 依存チェックはしない（compile 後の self-edge/cycle でのみエラー）
概要:
- 禁止条件を “descendant 参照” ではなく “結果が self-edge/cycle になったらエラー” に寄せる。

Pros:
- ルールが少なく見える（実装上は compile 後検出に集約できる）。

Cons:
- エラーが “結果” ベースになり、ユーザーが原因（どの ref が何を展開したか）を理解しづらい。
- 実質的には descendant 参照がほぼ self-edge を生むため、許可しても多くがエラーになり得る（混乱しやすい）。

## 判断理由（Rationale） (必須)
このADRは「結論未決」です。  
ただし、現時点の暫定推奨は **Option A（禁止維持）** です。

推奨理由（暫定）:
- “一目瞭然” を支えるのは、まず **運用事故を起こさない単純ルール** です。
- gate issue パターンは別の表現（issue→issue 明示 or 外出し）で代替できます。

## 影響（Consequences） (必須)
Positive（良い点）:
- fail-fast により、永久blocked系の不具合を早期に排除できる。

Negative / Debt（悪い点 / 将来負債）:
- shorthand の表現力が一部制限される（gate issue のまとめ指定等）。

影響範囲（コード/テスト/運用/データ）:
- runtime: compile 前後の検証（descendant 判定 or self-edge 判定）
- docs: `reference_deps.md` / 運用ガイド（禁止例/代替案）
- tests: self-edge/cycle の回帰（EC-003/004）

移行/ロールバック:
- Option A は v1 と整合しやすい。

## 参考（References） (任意)
- `spec-deps/current/requirement.md`（Q-003 / EC-003 / EC-004）
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`（現行の禁止ルール）
- `spec-deps/current/artifacts/deps-best-practice-issue-normalization.md`

