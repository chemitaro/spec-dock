# phase playbook: plan

このドキュメントは、Initiative / Epic / Issue に共通する **計画書の作り方** をまとめた shared playbook です。  
ここでは「どう進めるか」「どこで止まるか」「どの粒度で区切るか」を扱い、scope ごとの固有手順は `workflow_*.md` を参照します。

関連:
- 全体像: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 議論資料の置き方: `discussions/rules.md`

## 1. plan phase の全体 workflow

plan phase は、全体 workflow の **調査分析 → requirement → design → plan → 実装/品質ゲート** のうち、`plan` を扱います。  
この phase では、requirement / design で確定した内容を、実行可能な順序と粒度、停止点、品質ゲートに落とします。  
Initiative / Epic / Issue のどれでも、まず対象 scope の `workflow_*.md` で前後の流れと品質ゲートを確認し、そのうえでこの playbook に沿って計画を組み立てます。

- この phase の位置づけ:
  - 確定した要求と設計を、実行順・分解単位・停止点・品質ゲートへ変換する
- 前段で揃っている前提:
  - requirement と design が reviewer 承認レベルに達している
  - 依存とブロッカーを見積もれるだけの情報がある
- この phase で固定すること:
  - 分解単位
  - 順序
  - 完了判定
  - review / docs / quality gate の置き方
- この phase の完了条件:
  - reviewer が「この計画で実行してよい」と判断できること

標準順:
1. 目的理解
2. 徹底調査
3. 調査結果の docs 化（`research` / `disc` / `note` / `adr`）
4. discussion / ADR 準備
5. 必要ならヒアリング
6. 本文作成
7. reviewer loop
8. handoff

注意:
- requirement / design の再議論を plan 本文へ持ち込みません。
- 分割案や順序案の比較が長くなる場合は `disc` に分離します。
- scope 固有の操作、entry 条件、品質ゲートは `workflow_*.md` を正本とします。

## 2. この phase の目的 / 出力 / 非ゴール

### 目的
- requirement / design で確定した内容を、実行可能な順序と単位へ落とす
- 大きすぎる塊を分割し、レビュー・テスト・コミット・報告が回る計画にする
- 実行前に reviewer が「この順で進めてよい」と判断できる状態を作る

### 出力
- 承認可能な `plan.md`
- 必要に応じた順序図や構成図
- 必要に応じて `discussions/` 配下の `NNN-disc-*` / `NNN-research-*`
- 必要に応じて `discussions/` 配下の `NNN-adr-*`

### 非ゴール
- 設計不足を計画の細かさで補うこと
- 実行中に守るべき review / docs / quality gate を曖昧にすること
- 将来の全作業を過剰に先読みして plan を巨大化させること

## 3. workflow 開始前に確認すること

- requirement と design が reviewer 承認レベルにあることを確認する
- plan が扱う単位を明確にする
  - Initiative: roadmap / epic decomposition
  - Epic: issue decomposition / rollout order
  - Issue: implementation steps / review loop / quality gate
- 分解で新しい epic / issue を増やす前に、既存ノードの plan / Done 定義 / 依存順に収まるかを確認する
- 依存、ブロッカー、外部調整の有無を確認する

template 参照先:
- Initiative: `spec-dock/templates/initiative/plan.md`
- Epic: `spec-dock/templates/epic/plan.md`
- Issue: `spec-dock/templates/issue/plan.md`

## 4. plan workflow の進め方

計画 phase では、**何をいつやるか** だけでなく、**どこで止まるか** まで明確にします。

### 4.1 先に固めるもの
- 依存順序
- 並行可能な作業
- 各ステップ/各 issue/各 epic の完了判定
- 新規ノードを増やさずに進められる分解案
- レビュー、テスト、docs 更新、品質ゲートの位置

### 4.2 粒度の目安
- Initiative plan:
  - Epic 単位で価値のまとまりと順序を示す
- Epic plan:
  - Issue 単位で縦切りと依存を示す
- Issue plan:
  - 1 ステップ = 1 つの観測可能な振る舞いを原則にする
- 分割案や順序案の比較が必要なら、plan 本文へ押し込まず先に `disc` / `note` に残す
- plan 本文には実行順、停止点、完了判定を残し、長い比較や作業メモは discussion 系 docs へ分離する

## 5. ユーザーヒアリングを挟む条件

計画 phase でも、次の条件ではヒアリングを行います。
- ロールアウト日程や調整先が順序に影響する
- 運用停止時間帯やリリース制約がある
- 依存先チームとの合意がないと進められない

聞く内容の中心:
- いつまでに何が必要か
- どこまで並行できるか
- 何を先に出すと価値があるか
- どの品質ゲートが必須か
- 回答は先に discussion sheet へ整理し、その後に plan 本文へ反映する

## 6. discussion / docs 化の使い分け

次の条件では discussion sheet を作ります。
- 分割案や順序案が複数あり、比較が必要
- quality gate や docs impact の扱いを事前合意したい
- reviewer へ「なぜこの順番か」を説明する材料が必要
- 外部依存やリリース順が複雑で、計画本文だけでは追いにくい
- 既存 epic / issue に収める案と、新規ノードを増やす案を比較したい

ヒアリングや reviewer へ渡す前に、少なくとも次を見えるようにします。
- 今回決めたい分解 / 順序 / 停止点
- 確定した依存と制約
- 未確定事項 / ブロッカー
- 選択肢と比較
- 推奨案
- 反映先の本文節

## 7. ADR を切る条件

plan phase で ADR を切るのは例外的です。  
ただし、計画自体が次のような **運用方針の決定** を含むなら ADR を検討します。

- 反復レビューや品質ゲートの運用ルールを恒久化したい
- ロールアウト戦略や切替方式の選択が、単なる順序ではなく方針決定になる
- 実装前提の大きな段取りが、将来も参照される判断になる

通常の step 分解、実装順序、作業メモは ADR ではなく plan 本文または discussion sheet に置きます。

## 8. template で先に埋める節

### Initiative plan
- `ロードマップ`
- `Epic 分解`
- `順序と理由`
- `計測計画`
- `ロールアウト計画`
- `依存関係 / ブロッカー`

### Epic plan
- `Issue 分割`
- `Issue 一覧`
- `品質ゲート`
- `ロールアウト / 移行`
- `Issue Definition of Ready`

### Issue plan
- `この計画で満たす要件ID`
- `ステップ一覧`
- `要件 ↔ ステップ対応表`
- `実行ルール`
- 各ステップの `期待する振る舞い`
- Issue 固有の実行/品質ゲートは `workflow_issue.md` の要求を plan に反映する

## 9. reviewer に渡す前の exit criteria

- 順序の理由が説明できる
- 粒度が大きすぎず、review / test / commit / report が回る
- 依存とブロッカーが plan に露出している
- 新規ノードを増やす場合、その理由を作成後の対象ノード配下の最初の `disc` で追える
- scope 固有の実行ルールや品質ゲートは対応する `workflow_*.md` の要求を plan に反映できている
- `plan.md` 単体ではなく、必要な `disc` / `research` / `adr` を束で渡せる
- reviewer コメント反映後に re-review し、提出可能状態まで戻せる

## 10. 実行へ進める条件

plan の次は authoring phase ではなく実行です。  
次の条件を満たしたら実装/遂行へ進みます。

- plan.md が reviewer 承認レベルに達している
- requirement / design / plan のあいだで矛盾がない
- 依存と順序に関する blocking 論点が管理可能になっている
- scope 固有の実行ルールや品質ゲートが対応する `workflow_*.md` と矛盾していない
- `plan.md` と関連 docs を handoff 単位としてまとめられる

## 11. subagent 活用ガイダンス

- researcher / consultant 系:
  - 分割案、順序比較、外部ベストプラクティス確認に使う
- doc writer:
  - plan 文面、チェックリスト、quality gate の書き方整理に使う
- reviewer:
  - 粒度、依存、docs impact、最終品質ゲートの抜け漏れ確認に使う

注意:
- subagent には、対象スコープ、依存関係、求める粒度を明示する
- scope 固有の実行ルールや品質ゲート確認が必要なら、対応する `workflow_*.md` を前提として共有する

## 12. 迷ったときの判断順

1. requirement / design の不足が原因でないか確認する
2. 価値単位または観測可能な振る舞いで分割できるかを見る
3. 依存と並行性を整理する
4. discussion sheet で順序案を比較する
5. reviewer が「この計画で実行できる」と言える状態まで磨く
