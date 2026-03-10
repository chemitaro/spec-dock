# spec-dock docs（入口）

このディレクトリは `spec-dock init/update` により導入先リポジトリへ配置されます。  
まず `guide.md` で全体像を掴み、その後は対象 scope の `workflow_*.md` を入口にしてください。

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
4. 参照仕様
   - [reference_github.md](reference_github.md)
   - [reference_naming.md](reference_naming.md)
   - [reference_deps.md](reference_deps.md)
   - [reference_sync.md](reference_sync.md)

## 最短コマンド

```bash
./spec new initiative --title "..."
./spec new epic --initiative <initiative-id> --title "..."
./spec new issue --epic <epic-id> --title "..."

./spec import epic <num-or-url> --title "..." [--initiative <id>]
./spec import issue <num-or-url> --title "..." [--epic <id>]

./spec active set <id|#num|url>
./spec active set <id|#num|url> --checkout
./spec active show

./spec validate
./spec sync
```

## 高頻度ルール

- Initiative / Epic は `new` / `import` の前に既存ノード再利用を確認する
- `new issue` はデフォルトで GitHub Issue を作る。local-only は `--no-github`
- `new initiative` / `new epic` はデフォルトで local-only。GitHub 連携は opt-in
- `import` は読み取り確認のみで、GitHub を更新しない
- naming 制約、GitHub 副作用、deps / sync の詳細は `reference_*.md` を参照する
