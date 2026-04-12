# sync.md（deprecated / historical shortcut）

> このファイルは deprecated な historical shortcut です。  
> 現行の正本は [reference_sync.md](reference_sync.md) です。依存の正本は [reference_deps.md](reference_deps.md) を参照してください。

## current contract（要点）

- sync は `spec-dock/initiatives/**/.meta.json` を走査し、状態を再集計します。
- issue dependency metadata の canonical storage は `.meta.json` top-level `depends_on` です。
- 依存変更は command-first mutation（`deps add/remove/check`）で行い、metadata 手編集を current 運用にしません。
- legacy `meta.json` / `deps.json` は deprecated であり、no dual-read / no auto-migration / manual migration 前提です。

## current command path（runtime script）

```bash
./spec-dock/scripts/spec-dock deps check <target> --github
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
```

詳細の入出力契約、`--force` 挙動、all/todo projection、PlantUML は `reference_sync.md` を正本にしてください。
