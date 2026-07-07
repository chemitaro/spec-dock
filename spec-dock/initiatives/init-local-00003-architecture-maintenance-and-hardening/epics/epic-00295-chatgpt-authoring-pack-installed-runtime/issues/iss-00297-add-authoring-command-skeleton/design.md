---
種別: 設計書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
関連GitHub: ["#297"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00297 Authoring Command Skeleton — 設計

## 設計方針

既存 runtime は `cli/parser.py` が argparse surface を定義し、`cli/registry.py` が `commands/*` の `CommandSpec` を集約する。`authoring` command group もこの形に合わせ、monolithic parser-only 実装や root helper 直呼び出しにはしない。

この Issue の `authoring` command は skeleton であり、後続 Issue の実質ロジックを先取りしない。初期 subcommand は deferred として fail-closed し、automation が判定できる診断を返す。

## Provider-side 変更

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- cli/
|   |-- parser.py
|   `-- registry.py
`-- commands/
    `-- authoring.py
```

## Dogfooding mirror

provider-side runtime 変更に対応して、`spec-dock/scripts/spec_dock_runtime/...` の mirror も更新する。mirror は consumer-side validation artifact であり、implementation source of truth は provider-side asset tree に置く。

## Command surface

`authoring --help` は command group と deferred commands を表示する。初期 skeleton が受け付ける subcommand path は、Epic requirement/design の initial command surface に合わせる。

- `authoring preflight github-sync`
- `authoring pack prepare`
- `authoring backend invoke`
- `authoring pack review`
- `authoring pack stage`
- `authoring validate initiative-epic-candidates`
- `authoring validate epic-issue-candidates`
- `authoring validate issue-draft-adoption`
- `authoring validate selected-skeleton-fill`
- `authoring approval check`

## Deferred response design

Deferred subcommand は `CommandOutcome(exit_code=1, text=CliText(...))` を返す。stdout / stderr のどちらを使うかは既存 runtime の user-facing command style に合わせるが、少なくとも次の情報を含める。

- `status=deferred`
- `authority=evidence_only`
- `command=<authoring subcommand path>`
- `next_issue=<後続 Issue ID>`
- canonical adoption、reviewer pass、PR-ready を主張しない旨

## 後続 Issue mapping

| command | deferred to |
|---|---|
| `authoring preflight github-sync` | `iss-00298` |
| `authoring pack prepare` | `iss-00299` |
| `authoring backend invoke` | `iss-00300` |
| `authoring pack review` | `iss-00301` |
| `authoring pack stage` | `iss-00301` |
| `authoring validate initiative-epic-candidates` | `iss-00302` |
| `authoring validate epic-issue-candidates` | `iss-00302` |
| `authoring validate issue-draft-adoption` | `iss-00303` |
| `authoring validate selected-skeleton-fill` | `iss-00303` |
| `authoring approval check` | `iss-00305` |

## Forbidden command boundary

以下は初期実装で作らない。存在させる場合も success status を返してはならない。

- `authoring adopt`
- `authoring create-issues-from-zip`
- `authoring mark-reviewer-pass`
- `authoring set-authorized-profile`
- `authoring issue-execution-ready`
- `authoring pr-ready`

## 検証設計

- help 出力に `authoring` command group と deferred command が出ることを確認する。
- representative deferred commands が exit code 1 を返し、`status=deferred` と対応 Issue ID を含むことを確認する。
- parser / registry に `authoring_*` command specs が登録されることを focused test で確認する。
- `spec-dock init` 後の consumer workspace でも `authoring --help` が表示されることを確認する。
