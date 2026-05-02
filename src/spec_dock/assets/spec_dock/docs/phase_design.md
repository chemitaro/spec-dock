# phase playbook: design

Initiative / Epic / Issue に共通する design の shared playbook です。
scope 固有の entry / quality gate は `workflow_*.md` が additive に定義します。議論資料の置き方は対象 scope 配下の `discussions/rules.md`、命名は [reference_naming.md](reference_naming.md) を参照してください。

関連:
- 全体像: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 議論資料の置き方と命名: 対象 scope 配下の `discussions/rules.md`, [reference_naming.md](reference_naming.md)

## phase contract

- 位置: 全体 workflow の `調査分析 → requirement → design → plan → 実装/品質ゲート` の `design`
- 責務: requirement で固定した `WHAT / WHY` を、実装可能な HOW / guardrails に落とす
- 前提入力: reviewer 承認レベルの `requirement.md`、既存実装 / docs / ADR、設計で閉じる論点
- 固定すること: 方針、境界 / 契約、SoR / 依存、依存関係分析、移行、観測性、テスト戦略
- 出力: reviewer が plan へ送れる `design.md` と必要な `research` / `disc` / `adr`
- 非ゴール: requirement の不足のごまかし、比較表の本文への押し込み、実装手順の plan 化
- 正本参照: この playbook の `review / handoff gate` が shared minimum gate。scope 固有 gate は `workflow_*.md` が additive に定義する

## scope ownership

- Initiative design:
  - 所有する判断:
    - system context、architecture policy、cross-cutting constraint、target-state、bounded context / ubiquitous language、Epic が守る guardrail
  - 所有しない判断:
    - Issue-level class / function / file design、局所 sequence、実装順序
- Epic design:
  - 所有する判断:
    - 複数 Issue が共有する boundary、responsibility、data flow、domain model / aggregate、failure / migration strategy、ADR 分離基準
  - 所有しない判断:
    - Issue 内だけで閉じる細かな実装手順や局所 refactor
- Issue design:
  - 所有する判断:
    - 局所構造、既存 pattern の採否、interface contract、dependency direction、domain model delta、test strategy、rollback / compatibility
  - 所有しない判断:
    - 親 design の再定義、Red / Green / Refactor の作業手順、commit / review の運用順序
- ADR rule:
  - 長寿命・横断的・不可逆寄りの判断は ADR / decision log に分離する
  - 局所的で可逆な判断は対象 scope の design に置く

## 標準順

1. requirement と対象 scope の workflow を確認する
2. 既存実装 / 既存 docs / 既存 ADR を調べる
3. 比較や下調べは `research` / `disc` に分離する
4. 必要ならヒアリングし、反映前に docs に整理する
5. `design.md` を固めて reviewer loop を回す
6. 関連 docs を束ねて plan へ handoff する

## entry checklist

- `requirement.md` が reviewer 承認レベルにある
- design で閉じる論点と、先にヒアリング / 追加調査が要る論点を分けた
- 既存実装、既存 docs、既存 ADR を見て、採用候補の既存パターンを把握した
- ヒアリング前に docs へ残す前提を整理した
  - 決めたい設計論点
  - 確定事実と既存パターン
  - 未確定事項 / 仮説
  - 選択肢と推奨案
  - 反映先の本文節または ADR
- template:
  - Initiative: `spec-dock/templates/initiative/design.md`
  - Epic: `spec-dock/templates/epic/design.md`
  - Issue: `spec-dock/templates/issue/design.md`

## design checklist

- 既存パターンに乗れるかを最初に確認し、新しい概念は「既存で足りない理由」を残す
- 先に押さえる:
  - 既存の責務分割
  - 現在の入出力契約
  - データ境界と SoR
  - domain vocabulary / bounded context / invariant
  - upstream / downstream / prerequisite の依存関係
  - 依存の少ない実装起点
  - 既存テストの守備範囲
  - 移行 / 運用 / 監視で壊しうる点
- 本文には採用結論と guardrails を残し、長い比較や生の調査ログは `discussions/` へ逃がす
- UML / PlantUML は、人間が誤読しやすい構造・境界・責務・流れ・状態・依存を可視化する用途で使う
- 図は本文の代替ではなく、本文で固定した設計判断を視覚的に検証する補助資料にする
- 図を置かない場合も、期待される図が不要な理由を `N/A: reason` として残す
- 先に埋める節:
  - Initiative: `アーキテクチャ上の狙い`, `現状と目指す姿`, `System Context`, `ドメイン境界 / ユビキタス言語`, `対象境界 / 依存`, `ガードレール`, `ロールアウト原則`, `観測性 / NFR 原則`, `主要リスク`
  - Epic: `全体像`, `Component / Module View`, `Package Dependency`, `Domain Model（DDD 必要時）`, `契約`, `データモデル`, `主要フロー`, `State / Activity（必要時）`, `失敗設計`, `移行戦略`, `観測性 / セキュリティ`, `テスト戦略`
  - Issue: `Parent Diagram References`, `既存実装 / 規約の理解`, `依存関係分析`, `Local Diagram Delta`, `インターフェース契約`, `Sequence Delta（必要時）`, `Domain Model Delta（必要時）`, `採用方針 / トレードオフ`, `変更計画`, `要件 → 設計マッピング`, `テスト戦略`, `要件 / 例外 -> verification mapping`

## PlantUML / UML usage policy

- Markdown preview compatibility:
  - PlantUML / C4 / DDD 図は Markdown 内では `plantuml` fence を使う
  - C4 Context が必要な場合は `!include C4_Context.puml` を明示する
  - `c4plantuml` fence は VS Code Markdown preview 互換性のため使わない
  - remote include は原則避け、利用する場合は理由と render 環境を明記する
- Diagram metadata:
  - すべての図は `Question answered`, `Scope`, `Excluded details`, `Update trigger` を持つ
  - 図の直後か直前に、その図で固定する設計判断を本文で説明する
  - 図だけにしか存在しない設計判断を残さない
- Relationship rules:
  - arrow は意味ラベルを持つ
  - `dependency`, `data flow`, `runtime call`, `ownership`, `publishes`, `implements` を曖昧にしない
  - 外部 actor / external system / out of scope component は境界外として分かるようにする
- Diagram budget:
  - Initiative / Epic は 1-3 図を目安にする
  - Issue は 0-2 図を目安にし、親 design の図を再掲しない
  - 図が増えすぎる場合は、親 scope への昇格、`discussions/` への分離、または低価値図の削除を検討する
- Avoid:
  - exhaustive class / file / method diagram
  - 実装作業順序だけを表す plan 相当の図
  - requirement の価値説明だけを表す図
  - すぐ古くなる generated call graph

## diagram selection rules

- Initiative:
  - 標準:
    - C4 System Context
  - DDD 採用時:
    - Bounded Context Map
    - Ubiquitous Language table
  - 必要時:
    - C4 Container
    - C4 Deployment
    - Activity / State for central lifecycle or business process
    - Use Case for actor-goal clarification
  - 避ける:
    - detailed class diagram
    - object diagram
    - issue-level sequence diagram
    - exhaustive component diagram
- Epic:
  - 主戦場:
    - Component / Module View
    - Package Dependency
    - Domain Model / Aggregate
    - Main Sequence
  - required when applicable:
    - State diagram if lifecycle exists
    - Activity diagram if workflow has complex branching
    - C4 Dynamic / sequence if multiple C4 elements collaborate in a non-trivial runtime flow
  - 必要時:
    - Object diagram for concrete invariant examples
    - Deployment diagram for infra-impacting epics
  - 避ける:
    - 親 System Context の再掲
    - 変更のない full Container architecture
    - exhaustive generated-code class diagram
- Issue:
  - default:
    - 図は必須ではない
  - required when applicable:
    - Sequence Delta if crossing components, transactions, queues, external APIs, or retries
    - State Delta if changing lifecycle
    - Domain Model Delta if changing aggregate, entity, value object, domain event, policy, or specification
    - Package Delta if changing dependency direction
  - 避ける:
    - System Context
    - full Container diagram
    - full Domain Model
    - full Deployment diagram

## DDD diagram guidance

- Initiative:
  - bounded context、core / supporting / generic domain、ubiquitous language の境界を扱う
  - 同じ語が context によって異なる意味を持つ場合は、context map と用語表で分ける
  - aggregate / entity / value object の詳細は原則 Epic へ降ろす
- Epic:
  - aggregate root、entity、value object、domain event、policy / specification、invariant の共有モデルを固定する
  - domain event は過去形の名前にし、internal domain event と integration event を必要時に区別する
  - repository は domain behavior ではなく port / contract として扱う
- Issue:
  - 親 Epic の domain model を参照し、変える aggregate / entity / value object / event / policy の差分だけを書く
  - full domain model を再掲しない
  - invariant や ownership を誤解しやすい場合だけ object diagram で具体例を補う

## UML review gate

- Diagram necessity:
  - 図が named design question に答えている
  - 図の owner level が Initiative / Epic / Issue のどれか明確
  - 図数が budget 内にある
  - 親文書が所有する情報を重複していない
  - 期待される図を省略した場合は `N/A: reason` がある
- Diagram correctness:
  - `plantuml` block が `@startuml` / `@enduml` を持つ
  - 図種が目的に合っている
  - title / scope / update trigger がある
  - stereotype、色、線種、icon を使う場合は凡例がある
  - element は名前と責務を持つ
  - relationship arrow は意味ラベルを持つ
  - 本文の用語、責務、依存方向と矛盾していない
- UML-specific gate:
  - Use Case は actor-goal を表し、内部実装を表さない
  - Class / Domain Model は概念・責務・関係を表し、生成コード inventory にしない
  - Package は compile-time / source dependency を表し、runtime call と混ぜない
  - Sequence は meaningful participants と messages を持つ
  - Activity は decision-heavy / parallel workflow に限定する
  - State は event、guard、terminal state を必要時に含む
  - ER / DB schema は永続化設計であり、domain model の代替にしない

## diagram guidance

- Initiative:
  - 推奨:
    - C4 Context
    - target-state / capability map
  - Markdown preview compatibility:
    - C4 図も Markdown 内では `c4plantuml` fence ではなく `plantuml` fence を使う
    - C4 Context が必要な場合は `!include C4_Context.puml` を明示する
    - `target-state` は C4 図種ではなく、将来状態の overview として扱う
  - 原則不要:
    - detailed sequence / class diagram
- Epic:
  - 推奨:
    - C4 Container / Component
    - module responsibility map
    - data flow
    - sequence / activity / state
  - review:
    - Issue slicing と責務境界に対応している
- Issue:
  - 推奨:
    - module / dependency diagram
    - sequence / activity / state
    - class / domain model
  - review:
    - plan の step order、error handling、test strategy に対応している
- all scopes:
  - 図表には目的、配置、更新タイミング、review 観点を添える
  - 図表だけにしか存在しない設計判断を残さない

## 論点の逃がし先

- `research`: 既存実装調査、類似機能比較、外部仕様調査
- `disc`: 設計案比較、トレードオフ整理、採否判断の前段
- `note`: 図の叩き台、軽量メモ
- `adr`: 境界 / 契約 / 移行などの長期判断
- 次なら先に docs 化する:
  - 2 案以上の比較がある
  - migration / observability / security の方針比較が長い
  - reviewer やユーザーと論点を切り分けて議論したい
- 次ならヒアリングを挟む:
  - UX / 運用フロー / 監査要件など、code だけでは決められない前提がある
  - ロールアウト条件や業務手順が境界に影響する
  - requirement で残した TBD が利用者都合でしか閉じられない
- 次なら ADR を検討する:
  - 境界、契約、整合性、移行戦略の採択が後続へ長く効く
  - 代替案を比較したうえで 1 案を明示的に選ぶ
  - 将来の変更者が「なぜこうしたか」を参照する必要がある

## review / handoff gate

この節は shared minimum gate です。通過後も scope 固有 gate は対応する `workflow_*.md` に追加で従います。

- requirement の主要論点に対応する設計の置き場がある
- 境界、契約、依存関係分析、観測性、テスト戦略のうち必要なものが抜けていない
- 既存パターンを採る / 採らない理由が説明できる
- plan に渡せる変更単位の見取り図と依存順がある
- `design.md` と必要な `research` / `disc` / `adr` を束で渡せる
- reviewer が「plan へ進めてよい」と判断できる

## short rules

- subagent は `researcher / consultant = 比較と事例収集`, `doc writer = 本文と図の整合`, `reviewer = layering / guardrails / テスト戦略の検出` で使い分ける
- subagent には `対象範囲 / 比較したい論点 / 採用判断に必要な観点` を渡す
- 迷ったら `requirement 不足の切り分け → 既存パターン確認 → disc → adr → review gate 再確認` の順で判断する
