# iss-00051 completion guard 強化の具体文言案

## 目的
- delegated workflow completion gap を埋めるために、どのファイルへどの文言をどう追加・修正するかを具体化する
- 一発出しではなく、consultant と repo 分析で出た複数案を比較し、最終的に採用推奨文言を示す

## 前提
- shim は薄いまま維持する
- adapter には minimum completion guard を置く
- workflow / issue-execution には detailed completion contract を置く
- manual test には completion quality gate を追加する

## 対象ファイル
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `spec-dock/docs/workflow_issue.md`

## consultant / analyst の要点
- shim に詳細な workflow completion を書きすぎるのは避けるべき
- 一方で、adapter 側に最低限の completion guard が無いと「route しただけで終わる」余地が残る
- detailed completion contract は workflow 正本に置くのが自然
- manual test では「runtime feasibility」と「completion quality」を分けて評価すべき

## 1. `.agents/skills/spec-dock-codex-adapter/SKILL.md` の文言案

### 現在
```md
- Use this as the Codex entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
```

### 候補 A（短い）
```md
- Use this as the Codex entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
- For issue work, do not report completion while `requirement.md`, `design.md`, `plan.md`, or `report.md` remain template-only or missing substantive content.
```

### 候補 B（標準）
```md
- Use this as the Codex entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
- For issue execution, treat completion as blocked until the active issue has concrete `requirement.md`, `design.md`, `plan.md`, and `report.md` content rather than untouched templates.
- Do not stop at route-only or active-set-only progress. If sync / validate / review cannot be completed, record the reason in `report.md` and treat the work as blocked or partial, not complete.
```

### 候補 C（厳密）
```md
- Use this as the Codex entrypoint for spec-dock work.
- Follow `spec-dock/docs/workflow_issue.md` and the fixed protocol from issue-00049.
- Route orchestration to the appropriate leaf skill; do not reimplement protocol or state logic here.
- Keep this adapter thin: wording only, no generated state, no pruning logic, no protocol interpretation.
- For issue execution, completion requires all of the following:
  - the active issue is explicitly identified
  - `requirement.md`, `design.md`, `plan.md`, and `report.md` are no longer template-only
  - the delegated flow has either executed sync / validate / required review steps or recorded why they could not be executed
- If any of the above is missing, do not report the issue as complete. Report it as blocked, partial, or pending with the reason.
```

### 比較
- 候補 A:
  - 長所: 短い
  - 短所: route-only 停止や sync/validate 未実施の扱いが弱い
- 候補 B:
  - 長所: 十分に具体的で、adapter を厚くしすぎない
  - 短所: template-only の判定がやや抽象的
- 候補 C:
  - 長所: 誤解が少ない
  - 短所: adapter としては少し重い

### 採用推奨
- 候補 B を推奨
- 理由:
  - adapter の thinness を保ちつつ、今回の gap を塞ぐ minimum completion guard として十分

## 2. `.agents/skills/spec-dock-issue-execution/SKILL.md` の文言案

### 現在
```md
- Use this skill for issue execution work.
- Typical fit: implement the active issue via TDD and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for issue governance.
```

### 候補 A（短い）
```md
- Use this skill for issue execution work.
- Typical fit: implement the active issue via TDD and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for issue governance.
- Do not treat the issue as complete while the active issue docs remain template-only.
```

### 候補 B（標準）
```md
- Use this skill for issue execution work.
- Typical fit: implement the active issue via TDD and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for issue governance.
- Completion requires concrete issue-level artifacts:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- If any of these remain template-only, the work is not complete.
- If sync / validate / review cannot be executed, record the reason in `report.md` and mark the result as blocked or partial.
```

### 候補 C（厳密）
```md
- Use this skill for issue execution work.
- Typical fit: implement the active issue via TDD and update `report.md`.
- Start from `spec-dock/active/context-pack.md`, then follow the issue workflow.
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for issue governance.
- An issue execution run is not complete unless all of the following are true:
  - the active issue is confirmed
  - `requirement.md`, `design.md`, and `plan.md` contain concrete issue-specific content
  - `report.md` contains execution evidence
  - required sync / validate / review steps are complete, or their omission is explained in `report.md`
- Template-only docs must be treated as an incomplete execution result.
```

### 比較
- 候補 A:
  - 長所: 最も軽い
  - 短所: report や sync/validate の扱いが弱い
- 候補 B:
  - 長所: 実行 skill の contract としてちょうどよい
  - 短所: 「concrete」の判断が若干運用依存
- 候補 C:
  - 長所: 非常に明確
  - 短所: wording が硬く、skill がやや規約文書化する

### 採用推奨
- 候補 B を推奨
- 理由:
  - issue execution skill は completion quality を担うので、docs 4 点と report/sync/validate の扱いを明示する価値が高い

## 3. `spec-dock/docs/workflow_issue.md` の文言案

### 追加位置の推奨
- `## 実行 contract` の直後
- `## report` の直後
- 必要なら `## 品質ゲート` に completion quality を追加

### 候補 A（短い）
```md
- issue work は、active issue docs がテンプレートのままなら完了扱いにしない
- sync / validate / review を省略した場合は、その理由を `report.md` に残す
```

### 候補 B（標準）
```md
- issue execution の completion quality gate:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` のいずれかがテンプレートのままなら完了扱いにしない
  - `sync`, `validate`, review を実施できなかった場合は、未実施理由を `report.md` に残す
  - route-only、active-set-only、artifact-only の状態は issue 完了ではない
  - blocked と fail は区別して記録する
```

### 候補 C（厳密）
```md
- issue completion の最低条件:
  - active issue が確定している
  - `requirement.md`, `design.md`, `plan.md`, `report.md` が issue 固有の内容で埋まっている
  - `report.md` に実行コマンド、結果、判断、想定外と対処が記録されている
  - `sync`, `validate`, review を実施したか、未実施理由が `report.md` に記録されている
- 上記を満たさない限り、issue を complete とみなしてはならない
```

### 比較
- 候補 A:
  - 長所: 読みやすい
  - 短所: quality gate としては弱い
- 候補 B:
  - 長所: workflow docs に置くには最もバランスがよい
  - 短所: `report.md` の必須内容は別節も参照が必要
- 候補 C:
  - 長所: 最も明確
  - 短所: workflow docs 全体のトーンとしてはやや強い

### 採用推奨
- `実行 contract` には候補 B
- `report` 節には次の補強を追加
```md
- completion quality の観点では、docs 4 点未充足や sync / validate / review 未実施理由も future reviewer が追える粒度で残す
```

## 4. manual test 向け文言案

### checklist へ追加する最小文言
```md
- [ ] completion quality check:
  - [ ] `requirement.md` がテンプレートのままではない
  - [ ] `design.md` がテンプレートのままではない
  - [ ] `plan.md` がテンプレートのままではない
  - [ ] `report.md` に実行証跡がある
```

### summary に追加する最小文言
```md
- completion quality:
  - `PASS` / `FAIL` / `BLOCKED`
  - docs 4 点の具体化状況
  - runtime blocker か product gap かの判定
```

## 最終推奨セット

### 採用推奨の組み合わせ
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - 候補 B
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - 候補 B
- `spec-dock/docs/workflow_issue.md`
  - 候補 B + `report` 節への補強 1 行
- manual test docs
  - completion quality check を新設

## 採用理由
- shim を太らせずに gap を塞げる
- adapter に minimum completion guard を置くことで「route しただけで止まる」を防げる
- issue execution skill と workflow docs に詳細 contract を置くことで、completion の正本を一貫化できる
- manual test で「runtime feasibility」と「completion quality」を分離できる

## 非推奨
- shim に detailed completion logic を直接書くこと
- file ごとに異なる completion 定義を置くこと
- manual test で docs 4 点未充足を見逃すこと
