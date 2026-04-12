# spec-dock-guide-old.md（deprecated / historical）

> このファイルは historical reference です。  
> 現行の入口と正本は [README.md](README.md), [guide.md](guide.md), [workflow_issue.md](workflow_issue.md), [workflow_adr.md](workflow_adr.md), [reference_deps.md](reference_deps.md), [reference_sync.md](reference_sync.md) です。

## 現行との差分（最小）

- runtime command path は `./spec-dock/scripts/spec-dock ...` が current contract です。
- dependency metadata の canonical storage は `.meta.json` top-level `depends_on` です。
- 依存の追加/削除/確認は metadata 直編集ではなく command-first mutation（`deps add/remove/check`）で行います。
- legacy `meta.json` / `deps.json` 運用は deprecated で、no dual-read / no auto-migration / manual migration 前提です。

## 現行コマンド（参照）

```bash
./spec-dock/scripts/spec-dock active set <target>
./spec-dock/scripts/spec-dock deps check <target> --github
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
```

旧版の背景参照としては残しますが、日常運用の判断基準には使わず、必ず現行正本を参照してください。
