# spec-dock docs（入口）

このディレクトリは `spec-dock init/update` により導入先リポジトリへ配置されます。  
まず `guide.md` で全体像を掴み、その後は対象 scope の `workflow_*.md` を入口にしてください。
plan だけは `phase_plan.md` の shared axiom と `phase_plan_<scope>.md` の scope-specific playbook を合わせて参照します。

## エージェント起点

`spec-dock init/update` は次の skill を導入します。

- Hub: `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- Initiative: `.agents/skills/spec-dock-initiative-planning/SKILL.md`
- Epic: `.agents/skills/spec-dock-epic-planning/SKILL.md`
- Issue: `.agents/skills/spec-dock-issue-execution/SKILL.md`
- ADR: `.agents/skills/spec-dock-adr-facilitation/SKILL.md`

## 読み順

1. [guide.md](guide.md)
2. 対象 scope の workflow
   - [workflow_initiative.md](workflow_initiative.md)
   - [workflow_epic.md](workflow_epic.md)
   - [workflow_issue.md](workflow_issue.md)
   - [workflow_adr.md](workflow_adr.md)
3. phase の shared playbook
   - [phase_requirement.md](phase_requirement.md)
   - [phase_design.md](phase_design.md)
   - [phase_plan.md](phase_plan.md)
4. scope 固有の plan playbook
   - [phase_plan_initiative.md](phase_plan_initiative.md)
   - [phase_plan_epic.md](phase_plan_epic.md)
   - [phase_plan_issue.md](phase_plan_issue.md)
5. reference レイヤ
   - [reference_github.md](reference_github.md)
   - [reference_naming.md](reference_naming.md)
   - [reference_deps.md](reference_deps.md)
   - [reference_sync.md](reference_sync.md)

## 最短コマンド

```bash
./spec new initiative --title "..."
./spec new epic --initiative <initiative-id> --title "..."
./spec new issue --epic <epic-id> --title "..."
./spec new issue --create-github-issue --epic <epic-id> --title "..."

./spec import epic <num-or-canonical-url> --title "..." [--initiative <id>] [--allow-foreign-url]
./spec import issue <num-or-canonical-url> --title "..." [--epic <id>] [--allow-foreign-url]

./spec active set <id|#num|url>
./spec active set --id <node-id>
./spec active set --github-issue <n>
./spec active set <id|#num|url> --checkout
./spec active show

./spec validate
./spec sync
```

## 高頻度ルール

- Initiative / Epic は `new` / `import` の前に既存ノード再利用を確認する
- plan は shared `phase_plan.md` の後に対象 scope の `phase_plan_<scope>.md` を読む
- `new issue` はデフォルトで GitHub Issue を作る。local-only は `--no-github`
- `new issue --create-github-issue` は default create の explicit alias
- `new initiative` / `new epic` はデフォルトで local-only。GitHub 連携は opt-in
- `import` は読み取り確認のみで、GitHub を更新しない。canonical URL は current repo と照合し、cross-repo は `--allow-foreign-url` が必要
- `active set` / `deps check` は `<target>` の後方互換を維持しつつ、`--id` / `--github-issue` の explicit form も使える
- Issue plan は TDD ベースの execution contract を持つが、cadence policy の正本は `workflow_issue.md`
- naming 制約、GitHub 副作用、deps / sync の詳細は `reference_*.md` を参照する
