# workflow-issue.md（deprecated / historical alias）

> このファイルは deprecated な historical alias です。  
> 現行の正本は [workflow_issue.md](workflow_issue.md) です。Issue 実行 contract は正本を参照してください。

## 現行の入口

- 総合導線: [guide.md](guide.md)
- Issue 正本: [workflow_issue.md](workflow_issue.md)
- 依存関係: [reference_deps.md](reference_deps.md)
- GitHub 連携: [reference_github.md](reference_github.md)
- sync/生成物: [reference_sync.md](reference_sync.md)

## current command path（runtime script）

```bash
./spec-dock/scripts/spec-dock active set <issue-id|#num|url>
./spec-dock/scripts/spec-dock deps check <target> --github
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
```

- dependency mutation は metadata 手編集ではなく command-first（`deps add/remove/check`）で行います。
- 旧導線は compatibility/historical 参照に限定し、current workflow の手順は `workflow_issue.md` を参照してください。
