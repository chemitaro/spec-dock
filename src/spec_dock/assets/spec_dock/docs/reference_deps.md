# reference: deps（依存関係管理）

対象コマンド:

```bash
./spec deps check <target> [--github] [--gh-limit N] [--json]
./spec deps check --id <node-id> [--github] [--gh-limit N] [--json]
./spec deps check --github-issue <n> [--github] [--gh-limit N] [--json]
./spec active set <target> [--github] [--gh-limit N] [--force|-f] [--checkout]
./spec active set --id <node-id> [--github] [--gh-limit N] [--force|-f] [--checkout]
./spec active set --github-issue <n> [--github] [--gh-limit N] [--force|-f] [--checkout]
./spec sync [--github] [--gh-limit N] [--no-update-active] [--force]
```

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)
- sync: [reference_sync.md](reference_sync.md)

## 1. 結論（v2）

- canonical storage は node 直下 `.meta.json` の top-level `depends_on` です。
- reader（`infra/deps_reader.py`）は `.meta.json` だけを読み、`deps.json` dual-read / auto-migration は行いません。
- `depends_on` の field absence は `[]` と同義です。
- raw value grammar は既存 shorthand に限定し、node id / GitHub issue number（int または numeric string）/ `owner/repo#123` / canonical issue URL のみを許可します。
- shorthand は canonical な issue->issue direct edge にコンパイルされ、downstream consumer は既存 `DepsTopologyLoadResult` surface を継続利用します。
- rollback は compatibility mode ではなく issue diff revert 前提です。

## 2. `.meta.json`（ノード直下 / 任意）

配置場所:
- initiative: `<initiative-dir>/.meta.json`
- epic: `<epic-dir>/.meta.json`
- issue: `<issue-dir>/.meta.json`

スキーマ例:

```json
{
  "schema_version": 1,
  "type": "issue",
  "id": "iss-00100",
  "title": "Example issue",
  "slug": "example-issue",
  "depends_on": [
    "iss-00123",
    "epic-local-00001",
    456,
    "789",
    "owner/repo#123",
    "https://github.com/owner/repo/issues/123"
  ]
}
```

ルール:
- `depends_on` は optional top-level field です
- field absence は `[]` と同義です
- `depends_on` 要素は node id、GitHub issue番号（int / numeric string）、repo-scoped ref（`owner/repo#123` / canonical issue URL）に限定されます
- shorthand は最終的に issue->issue edge へ還元されます
- reader は `.meta.json` だけを読み、legacy `deps.json` は migration 入力にも fallback read source にもしません

構造エラー（fail-fast）:
- JSONパース不正 / top-level object 不正 / `depends_on` の型不正
- unsupported element type / unsupported string
- 未解決参照
- 親->配下（descendant）依存
- 自己依存（shorthand展開で生じる implicit self も含む）

補足:
- shorthand 展開結果が空でもエラーにはせず、warning `deps_ref_expanded_to_empty` を出します。
- no dual-read / no auto-migration / rollback-by-revert を前提にします。

## 3. reader contract

- `infra/deps_reader.py` は node 直下 `.meta.json` から `depends_on` を読みます。
- shorthand 解決、issue-level direct edge compile、dedupe、deterministic sort、descendant/self reject、warning `deps_ref_expanded_to_empty` は current contract を維持します。
- downstream consumer 向けの return shape は既存 `DepsTopologyLoadResult(issue_depends_on_map, warnings)` のままです。
- cycle detection、mutation、delete scrub、`validate` / `sync` / `active set` parity はこの T1 reference update の完了条件に含めません。

## 4. downstream boundary note

- `deps check`、`active set`、`validate`、`sync`、`delete` は compiled dependency result を消費する downstream consumer です。
- この文書更新は `.meta.json` schema と reader contract の固定を目的とし、mutation command や downstream parity が完了済みであることを意味しません。
- provider-side のこのファイルが dependency reference の正本であり、dogfooding 側 copy は secondary verification です。

## 5. migration / rollback guardrails

- no dual-read: reader は `.meta.json` のみを対象にし、`deps.json` fallback read を持ちません。
- no auto-migration: runtime は `deps.json` から `.meta.json` への自動変換・救済を行いません。
- rollback-by-revert: compatibility mode は導入せず、issue diff revert で戻します。

## 6. hard cutover owner boundary

- legacy `deps.json` checked-in data manual fix と dogfooding `./spec-dock/scripts/spec-dock validate` / `sync` evidence、hard cutover judgment の primary owner は `iss-00062` です。
- `iss-00060` が固定するのは `.meta.json` schema、reader contract、provider-side dependency docs 正本更新までです。
