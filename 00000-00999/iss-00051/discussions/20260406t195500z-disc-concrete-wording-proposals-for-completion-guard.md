# iss-00051 completion guard 文言案レビュー

## 目的
- delegated workflow gap を埋めるために、どのファイルへどの強さの文言を入れるべきかを具体化する
- 特に「goal-level task を受けたとき、docs 4 点がテンプレートのままなら完了扱いにしない」を、誤解の少ない表現に落とす

## 対象
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `spec-dock/docs/workflow_issue.md`

## 前提整理
- shim は薄いまま維持する
- adapter には minimum completion guard を置く
- detailed completion contract は issue execution skill / workflow docs 側に置く
- 完了条件と blocked 条件は分けて書く

## consultant 観点の整理

### 観点 1: 短すぎる文言の問題
- 「テンプレートのままなら未完了」だけだと、
  - どのファイルが対象か
  - blocked と fail のどちらか
  - review / validate / sync の扱い
  が曖昧なまま残る

### 観点 2: 厳密すぎる文言の問題
- shim や adapter に詳細な completion logic を詰め込みすぎると、
  - workflow 正本と二重管理になる
  - host ごとの drift を招きやすい

### 観点 3: 文言を置く場所ごとの役割
- adapter skill:
  - 最低限の終了条件と未完了条件を明示する場所
- issue execution skill:
  - issue work の completion / blocked / report の扱いを少し詳しく書く場所
- workflow docs:
  - 最も詳細な execution contract の正本

## 修正文言の候補

## 1. `.agents/skills/spec-dock-codex-adapter/SKILL.md`

### 追加位置
- 既存の bullet 群の直後

### 短い版
```md
- Issue work では、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままなら完了扱いにしない。
```

### 標準版
```md
- Issue work を扱う場合は、active issue を確定し、`requirement.md` / `design.md` / `plan.md` / `report.md` を実データで埋めるまで完了扱いにしない。
- 上記のいずれかがテンプレートのまま残る場合は、完了ではなく未完了または blocked として扱い、その理由を報告する。
```

### 厳密版
```md
- Issue work を扱う場合は、active issue を確定し、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` を実データで更新するまで完了扱いにしない。
- 4 点の issue docs のいずれかがテンプレートのまま、または実質未記入の状態で残る場合は、完了宣言をしてはならない。
- `sync` / `validate` / review を実施できない場合は、完了扱いにせず、未実施理由または blocker を `report.md` に残す。
```

### 推奨
- `標準版`

### 理由
- 短い版は曖昧さが残る
- 厳密版は adapter に詳細を書きすぎる
- adapter では「完了扱いにしない」「理由を報告する」まで書けば十分

## 2. `.agents/skills/spec-dock-issue-execution/SKILL.md`

### 追加位置
- `Treat workflow_issue.md as the source of truth` の後ろ

### 短い版
```md
- Issue docs 4 点がテンプレートのままなら未完了として扱う。
```

### 標準版
```md
- Issue execution では、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残る状態で終了してはならない。
- `sync` / `validate` / review を実施した場合は結果を `report.md` に残し、実施できない場合は理由または blocker を `report.md` に残す。
```

### 厳密版
```md
- Issue execution の終了条件は、active issue が確定しており、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままではなく、実行した `sync` / `validate` / review の証跡が `report.md` に残っていることである。
- 4 点の issue docs のいずれかがテンプレートのまま残る場合、または `sync` / `validate` / review の未実施理由が `report.md` に記録されていない場合は、完了扱いにしない。
- この場合は `blocked` または `未完了` として明示し、次のアクションを `report.md` に残す。
```

### 推奨
- `標準版` と `厳密版` の中間

### 推奨採用文
```md
- Issue execution では、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残る状態で終了してはならない。
- `sync` / `validate` / review を実施した場合は結果を `report.md` に残し、実施できない場合は理由または blocker を `report.md` に残す。
- 上記が満たせない場合は、完了ではなく `blocked` または `未完了` として扱う。
```

### 理由
- issue execution skill では adapter より一段詳しく書ける
- ただし workflow docs ほど詳細にしなくてよい

## 3. `spec-dock/docs/workflow_issue.md`

### 追加位置
- `## 実行 contract` の箇条書きの後半

### 短い版
```md
- `requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままなら完了扱いにしない。
```

### 標準版
```md
- Issue work は、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残る状態で完了としてはならない。
- `sync` / `validate` / review を実施した場合は結果を `report.md` に残し、実施できない場合は理由または blocker を `report.md` に残す。
```

### 厳密版
```md
- Issue work の完了条件は、active issue が確定しており、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままではなく、必要な `sync` / `validate` / review の結果または未実施理由が `report.md` に記録されていることである。
- 4 点の issue docs のいずれかがテンプレートのまま、または実質未記入の状態で残る場合は、完了扱いにしない。
- `sync` / `validate` / review を実施できない場合は、その理由、影響、次のアクションを `report.md` に残す。
- 完了条件を満たせない状態は `blocked` または `未完了` として扱い、成功報告をしてはならない。
```

### 推奨
- `厳密版`

### 理由
- workflow docs は正本なので、ここは厳密に書くべき
- 他の skill はこの表現を参照する前提にできる

## ベストプラクティス提案

### 基本方針
- shim:
  - 薄いまま
- adapter:
  - 最小限の completion guard
- issue execution skill:
  - 実行時の completion / blocked / report の扱いを明示
- workflow docs:
  - 最も厳密な正本

### 文言の強さ
- shim:
  - 強すぎない
- adapter:
  - 標準版
- issue execution skill:
  - 標準版より少し強め
- workflow docs:
  - 厳密版

## 推奨する具体修正

### `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- 採用推奨:
```md
- Issue work を扱う場合は、active issue を確定し、`requirement.md` / `design.md` / `plan.md` / `report.md` を実データで埋めるまで完了扱いにしない。
- 上記のいずれかがテンプレートのまま残る場合は、完了ではなく未完了または blocked として扱い、その理由を報告する。
```

### `.agents/skills/spec-dock-issue-execution/SKILL.md`
- 採用推奨:
```md
- Issue execution では、`requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残る状態で終了してはならない。
- `sync` / `validate` / review を実施した場合は結果を `report.md` に残し、実施できない場合は理由または blocker を `report.md` に残す。
- 上記が満たせない場合は、完了ではなく `blocked` または `未完了` として扱う。
```

### `spec-dock/docs/workflow_issue.md`
- 採用推奨:
```md
- Issue work の完了条件は、active issue が確定しており、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままではなく、必要な `sync` / `validate` / review の結果または未実施理由が `report.md` に記録されていることである。
- 4 点の issue docs のいずれかがテンプレートのまま、または実質未記入の状態で残る場合は、完了扱いにしない。
- `sync` / `validate` / review を実施できない場合は、その理由、影響、次のアクションを `report.md` に残す。
- 完了条件を満たせない状態は `blocked` または `未完了` として扱い、成功報告をしてはならない。
```

## 推奨順序
1. `workflow_issue.md` の厳密版を正本として固める
2. `spec-dock-issue-execution/SKILL.md` に中間強度の completion wording を入れる
3. `spec-dock-codex-adapter/SKILL.md` に最小限の completion guard を入れる

## 最終判断
- 最も誤解が少ないのは、同じ内容を 1 箇所にしか書かないことではなく、
  - workflow docs に厳密版
  - issue execution skill に中間版
  - adapter に最小版
 という階層的な書き分けをすること
- これにより、
  - shim は薄いまま
  - adapter は route + minimum guard
  - workflow は正本
  という責務分離を保ったまま、docs 4 点がテンプレートのままでも完了扱いされる gap を埋められる
