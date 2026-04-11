# workflow-adr.md（deprecated / historical alias）

> このファイルは deprecated な historical alias です。  
> 現行の正本は [workflow_adr.md](workflow_adr.md) です。ADR の運用 contract は正本を参照してください。

## 現行の入口

- ADR 正本: [workflow_adr.md](workflow_adr.md)
- 総合導線: [guide.md](guide.md)
- 命名/採番: [reference_naming.md](reference_naming.md)
- 依存関係（必要時）: [reference_deps.md](reference_deps.md)

## current command path（runtime script）

```bash
./spec-dock/scripts/spec-dock new doc adr --initiative <initiative-id> --title "..."
./spec-dock/scripts/spec-dock new doc adr --epic <epic-id> --title "..."
./spec-dock/scripts/spec-dock new doc adr --issue <issue-id> --title "..."
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
```

- ADR で依存変更を採用した場合も mutation は command-first（`deps add/remove/check`）で扱います。
- historical 参照として残しますが、current workflow は `workflow_adr.md` を正本とします。
