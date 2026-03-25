# workflow: epic

Epic は設計の背骨です。
この workflow は、Epic 固有の再利用判定、作成、Issue 分割、品質ゲートを正本として扱います。
この workflow の品質ゲートは scope 固有の additive gate であり、`phase_*.md` の shared minimum gate 通過を前提とします。

対応 leaf skill:
- `.agents/skills/spec-dock-epic-planning/SKILL.md`

関連:
- 総合: [guide.md](guide.md)
- Initiative: [workflow_initiative.md](workflow_initiative.md)
- Issue: [workflow_issue.md](workflow_issue.md)
- GitHub 連携: [reference_github.md](reference_github.md)
- 共通 phase playbook: [phase_requirement.md](phase_requirement.md), [phase_design.md](phase_design.md), [phase_plan.md](phase_plan.md)
- Epic plan playbook: [phase_plan_epic.md](phase_plan_epic.md)

## 再利用判定

- まず親 initiative 配下の既存 epic の `requirement.md` / `design.md` / `plan.md` / `discussions/` を確認する
- 契約、移行、観測性、Done 定義が既存 epic に収まるなら、新規作成せず既存 epic を更新する
- 設計の背骨や rollout 順が崩れる場合だけ `new` / `import` を使う
- 新規作成した理由や既存 epic に収めない理由は、作成後の対象 epic 配下の最初の `disc` に残す

## 作成

```bash
./spec new epic --initiative <initiative-id> --title "..."
./spec new epic --initiative <initiative-id> --github-issue <n> --title "..."
./spec new epic --initiative <initiative-id> --create-github-issue --title "..."

./spec import epic <num|#num|url> --title "..." [--initiative <initiative-id>]
```

- `import epic` で `--initiative` を省略した場合は current active から親 initiative を解決する
- naming 制約と GitHub 振る舞いは [reference_naming.md](reference_naming.md), [reference_github.md](reference_github.md) を参照する
- Epic 配下では wrapper `issues/new-issue "<title>"` を使える。local-only issue が必要なら direct command で `--no-github` を付ける

## 記述

- `requirement.md`: 期待する価値、受け入れ条件、非機能、スコープ
- `design.md`: 契約、移行、観測性、リスク
- `plan.md`: Issue 分割、依存順、品質ゲート。shared axiom は `phase_plan.md`、Epic 固有の書き方は `phase_plan_epic.md`
- `discussions/`: `new doc {adr|disc|research|note} --epic <epic-id> --title "..."`
- shared な書き方は `phase_*.md`、lifecycle / governance と Epic 固有の分割判断はこの workflow を正本とする

## 品質ゲート

- requirement:
  - Done 条件が観測可能
  - スコープと非スコープが明確
  - 新規 epic が必要な理由を最初の `disc` で追える
- design:
  - 契約が明記されている
  - 移行 / 互換 / ロールバックが整理されている
  - 観測性の方針がある
- plan:
  - Issue へ分割できている
  - 依存順が現実的

## 仕上げ

```bash
./spec validate
./spec sync
```
