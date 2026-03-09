# phase playbook: design

このドキュメントは、Initiative / Epic / Issue に共通する **設計書の作り方** をまとめた shared playbook です。  
ここでは HOW / Guardrails の詰め方を扱い、scope ごとの操作や個別フローは `workflow_*.md` を参照します。

関連:
- 全体像: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 議論資料の置き方: `discussions/rules.md`

## 1. この phase の目的 / 出力 / 非ゴール

### 目的
- requirement で固定した WHAT / WHY を、実装・運用・移行が可能な HOW に落とす
- 境界、契約、依存、観測性、テスト戦略を reviewer が追跡できる形にする
- 重要な意思決定を discussion / ADR に切り出し、設計本文を読みやすく保つ

### 出力
- 承認可能な `design.md`
- 必要に応じた UML
- 必要に応じて `discussions/` 配下の `disc-*` / `research-*`
- 必要に応じて `discussions/` 配下の `adr-*`

### 非ゴール
- 変更ファイルや実装手順の全詳細を先に plan 化すること
- requirement の不足を設計本文でごまかすこと
- 図を描くこと自体を目的化すること

## 2. 着手前に確認すること

- 先に requirement.md の reviewer 承認状態を確認する
- 未確定事項のうち、設計で扱うものと、先にヒアリング/追加調査が必要なものを分ける
- 既存実装、既存 docs、既存 ADR を読み、採用すべき既存パターンを把握する

template 参照先:
- Initiative: `spec-dock/templates/initiative/design.md`
- Epic: `spec-dock/templates/epic/design.md`
- Issue: `spec-dock/templates/issue/design.md`

## 3. 調査・分析の進め方

設計 phase の基本は、**既存を 99.9% 理解してから差分を設計する** ことです。

### 3.1 最初に押さえるもの
- 既存の責務分割
- 現在の入出力契約
- データ境界と SoR
- 既存のテストの守備範囲
- 運用・監視・移行で破壊しうる点

### 3.2 調査の進め方
- 既存パターンがあるなら、まずそれに乗れるかを検討する
- 新しい概念を追加する場合は、なぜ既存パターンで足りないかを明記する
- 主要な流れは文章で短く固定し、図は複雑さが高いときだけ補助として使う
- 設計本文には「採用する」「採用しない」を両方書くと reviewer が追いやすい

## 4. ユーザーヒアリングの進め方

設計 phase でも、次の条件ではヒアリングを挟みます。
- UX / 運用フロー / 監査要件など、コードだけでは決められない前提がある
- ロールアウト条件や業務手順が設計の境界に影響する
- requirement で残した TBD が、利用者側の都合でしか閉じられない

聞く内容の中心:
- 何を守る必要があるか
- 何が壊れると困るか
- どこまでが許容変更か
- 段階移行や例外運用の許容範囲

## 5. discussion sheet を作る条件

次の条件なら、設計本文に直接押し込まず `discussions/` へ分離します。
- 選択肢比較が 2 案以上ある
- pros/cons の説明が長くなり、設計本文の見通しを悪くする
- migration / observability / security の方針比較が必要
- reviewer やユーザーと論点を切り分けて議論したい

目安:
- `research-*`: 既存実装調査、類似機能比較、外部仕様調査
- `disc-*`: 設計案比較、トレードオフ整理、採否判断の前段
- `note-*`: 図の叩き台、軽量メモ

## 6. ADR を切る条件

設計 phase は ADR を切る主戦場です。  
次のどれかに当てはまるなら ADR を検討します。

- 境界、契約、整合性、移行戦略などの採択が後続へ長く効く
- 代替案を検討したうえで 1 案を明示的に選ぶ
- reviewer や将来の変更者が「なぜこうしたか」を参照する必要がある

逆に、単なる実装メモ、未整理の比較、局所的な TODO は ADR ではなく discussion へ置きます。

## 7. template のどこを埋めるか

### Initiative design
- `アーキテクチャ上の狙い`
- `現状の把握`
- `目指す姿`
- `システム境界 / 依存`
- `ガードレール`
- `移行 / ロールアウト方針`
- `主要リスクと軽減策`

### Epic design
- `全体像`
- `契約`
- `データモデル設計`
- `主要フロー`
- `失敗設計`
- `移行戦略`
- `観測性`
- `テスト戦略`

### Issue design
- `既存実装/規約の調査結果`
- `主要フロー`
- `判断材料/トレードオフ`
- `インターフェース契約`
- `変更計画`
- `マッピング（要件 → 設計）`
- `テスト戦略`

## 8. reviewer に渡す前の exit criteria

- requirement の主要論点に対応する設計上の置き場がある
- 境界、契約、観測性、テスト戦略のうち必要なものが抜けていない
- 既存パターンを採る / 採らない理由が説明できる
- discussion と ADR の切り分けが整理されている
- 図がある場合、本文なしでは読めない図になっていない
- plan に渡す変更単位の見取り図が最低限ある

## 9. 次 phase へ進める条件

設計は reviewer 承認前に plan へ進めません。  
次の条件を満たしたら plan へ進みます。

- design.md が reviewer 承認レベルに達している
- 変更境界、依存、テスト戦略が plan の分割判断に使える粒度になっている
- 重要な決定は ADR または設計本文のどちらかに居場所がある
- 残る TBD が「実装中に解ける作業メモ」ではなく、管理可能な論点として整理されている

## 10. subagent 活用ガイダンス

- researcher / consultant 系:
  - 比較案、周辺事例、選択肢の網羅に使う
- doc writer:
  - 設計本文の構造化、UML と文の整合確認に使う
- reviewer:
  - layering 崩れ、責務混線、テスト戦略不足の検出に使う

注意:
- subagent へは「対象範囲」「比較したい論点」「採用判断に必要な観点」を渡す
- UML を依頼する場合も、図単体ではなく本文で何を説明したいかを先に決める

## 11. 迷ったときの判断順

1. requirement の不足か、設計の論点かを切り分ける
2. 既存パターンに乗れるか確認する
3. 論点が長くなるなら discussion sheet を作る
4. 後続へ残る決定なら ADR を切る
5. reviewer が plan に進めるかで exit criteria を確認する
