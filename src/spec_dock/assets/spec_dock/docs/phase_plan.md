# phase playbook: plan

Initiative / Epic / Issue に共通する plan の shared playbook です。
scope 固有の実行ルールと品質ゲートは `workflow_*.md` が additive に定義します。議論資料の置き方は対象 scope 配下の `discussions/rules.md`、命名は [reference_naming.md](reference_naming.md) を参照してください。

関連:
- 全体像: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 議論資料の置き方と命名: 対象 scope 配下の `discussions/rules.md`, [reference_naming.md](reference_naming.md)

## phase contract

- 位置: 全体 workflow の `調査分析 → requirement → design → plan → 実装/品質ゲート` の `plan`
- 責務: 確定した requirement / design を、実行順・分解単位・停止点・品質ゲートに変換する
- 前提入力: reviewer 承認レベルの `requirement.md` / `design.md`、依存とブロッカー、対象 `workflow_*.md`
- 固定すること: 分解単位、順序、完了判定、review / docs / quality gate の位置
- 出力: reviewer が実行へ送れる `plan.md` と必要な `disc` / `research` / `adr`
- 非ゴール: requirement / design の再議論、設計不足の隠蔽、将来作業の過剰先読み
- 正本参照: この playbook の `review / handoff gate` が shared minimum gate。scope 固有の実行ルールと品質ゲートは `workflow_*.md` が additive に定義する

## 標準順

1. requirement / design と対象 scope の workflow を確認する
2. 依存、並行性、停止点、品質ゲートを洗う
3. 分割案や順序案の比較は `disc` / `note` に分離する
4. 必要ならヒアリングし、反映前に docs に整理する
5. `plan.md` を固めて reviewer loop を回す
6. 関連 docs を束ねて実行へ handoff する

## entry checklist

- `requirement.md` と `design.md` が reviewer 承認レベルにある
- この plan が扱う単位を明確にした
  - Initiative: roadmap / epic decomposition
  - Epic: issue decomposition / rollout order
  - Issue: implementation steps / review loop / quality gate
- 新規 epic / issue を増やす前に、既存ノードの plan / Done 定義 / 依存順に収まるかを確認した
- 依存、ブロッカー、外部調整の有無を見える化した
- ヒアリング前に docs へ残す前提を整理した
  - 決めたい分解 / 順序 / 停止点
  - 確定した依存と制約
  - 未確定事項 / ブロッカー
  - 選択肢と推奨案
  - 反映先の本文節
- template:
  - Initiative: `spec-dock/templates/initiative/plan.md`
  - Epic: `spec-dock/templates/epic/plan.md`
  - Issue: `spec-dock/templates/issue/plan.md`

## planning checklist

- 先に固める:
  - 依存順序
  - 並行可能な作業
  - 各単位の完了判定
  - 新規ノードを増やさずに進められる分解案
  - review / test / docs 更新 / quality gate の位置
- 粒度の目安:
  - Initiative: Epic 単位で価値のまとまりと順序を示す
  - Epic: Issue 単位で縦切りと依存を示す
  - Issue: `1 step = 1 つの観測可能な振る舞い` を原則にする
- Issue plan では `workflow_issue.md` の TDD / step review / docs impact / final diff review gate を plan に反映する
- plan 本文には実行順、停止点、完了判定を残し、長い比較や作業メモは `discussions/` へ逃がす
- 先に埋める節:
  - Initiative: `ロードマップ`, `Epic 分解`, `順序と理由`, `計測計画`, `ロールアウト計画`, `依存関係 / ブロッカー`
  - Epic: `Issue 分割`, `Issue 一覧`, `品質ゲート`, `ロールアウト / 移行`, `Issue Definition of Ready`
  - Issue: `この計画で満たす要件ID`, `ステップ一覧`, `要件 ↔ ステップ対応表`, `実行ルール`, `期待する振る舞い`

## 論点の逃がし先

- `research`: 外部制約や運用条件の確認
- `disc`: 分割案、順序案、quality gate の比較
- `note`: 軽量メモ、叩き台
- `adr`: 恒久化すべき運用方針やロールアウト判断
- 次なら先に docs 化する:
  - 分割案や順序案が複数ある
  - quality gate や docs impact の扱いを事前合意したい
  - 外部依存やリリース順が複雑で plan 本文だけでは追いにくい
  - 既存ノードへ収める案と新規ノード案の比較が要る
- 次ならヒアリングを挟む:
  - ロールアウト日程や調整先が順序に影響する
  - 運用停止時間帯やリリース制約がある
  - 依存先チームとの合意がないと進められない
- 次なら ADR を検討する:
  - 反復レビューや品質ゲートの運用ルールを恒久化したい
  - ロールアウト戦略や切替方式が単なる順序ではなく方針決定になる
- 通常の step 分解、実装順序、作業メモは ADR にしない

## review / handoff gate

この節は shared minimum gate です。通過後も scope 固有 gate は対応する `workflow_*.md` に追加で従います。

- 順序の理由が説明できる
- 粒度が大きすぎず、review / test / commit / report が回る
- 依存とブロッカーが plan に露出している
- 新規ノードを増やす場合、その理由を対象ノード配下の最初の `disc` で追える
- scope 固有の実行ルールや品質ゲートを対応する `workflow_*.md` に沿って反映できている
- `plan.md` と必要な `disc` / `research` / `adr` を束で渡せる
- reviewer が「この計画で実行してよい」と判断できる

## short rules

- subagent は `researcher / consultant = 分割案や順序比較`, `doc writer = gate と文面整理`, `reviewer = 粒度 / 依存 / quality gate の抜け確認` で使い分ける
- subagent には `対象 scope / 依存関係 / 求める粒度` を渡す
- 迷ったら `requirement / design 不足の切り分け → 価値単位または観測可能な振る舞いで再分割 → disc → workflow gate 再確認` の順で判断する
