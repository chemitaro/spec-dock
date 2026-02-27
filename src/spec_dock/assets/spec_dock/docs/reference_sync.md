# reference: sync（状態集計）

対象コマンド:

```bash
./spec sync [--github] [--gh-limit N] [--no-update-active] [--force]
```

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)

## 1. 結論（何をしているか）

`sync` はローカル SSOT（`spec-dock/initiatives/**/meta.json`）を走査し、以下を生成します（git 管理しない）:

- `spec-dock/.agent/index.json`
- `spec-dock/.agent/tree.json`
- `spec-dock/.agent/deps.json`
- `spec-dock/.agent/deps.puml`
- `spec-dock/.agent/deps.todo.puml`

加えて、デフォルトでは **現在ブランチ名から active を推定して更新**します（best-effort）。

- `sync --no-update-active`: ブランチ名からの active 更新をしません（生成物のみ）
- `sync` は実行前に preflight validate を行い、致命的不整合がある場合は失敗します
  - `sync --force`: validate NG でも警告して継続します（デバッグ用途）

deps（依存関係）に関する補足:
- `sync` は deps 派生物（`.agent/deps*.{json,puml}`）を生成するために、deps の preflight（`deps.json` の解決/循環検出など）も行います。
  - deps 構造エラー（不正 JSON/未解決参照/循環依存/親→配下依存など）がある場合、通常は `sync` が失敗します。
  - `sync --force` の場合は `deps_preflight_failed` を warn して **index/tree の更新を継続**しますが、deps 派生物は **削除** して「最新が無い」ことを明確にします（古い派生物の誤用を防ぐため）。

### preflight validate で弾かれる代表例

- `github.issue_number` の重複（同じ Issue番号が複数 node にリンクされている）
  - 復旧手順は [reference_github.md](reference_github.md) の「github.issue_number のリンクと一意性」を参照してください

### active 推定の例（2〜3例）

`sync` は「ブランチ名に含まれる id / GitHub Issue番号」を手がかりに、仕様ツリー内のノードへ **一意に対応**する場合のみ active を更新します（曖昧なら更新しません）。

例:
- `feature/iss-00123-add-refresh` → `iss-00123` が存在すれば、その issue を active に更新
- `feature/issue-123-add-refresh` / `feature/gh-123-add-refresh` → `github.issue_number=123` のノードが 1つなら active を更新
- `feature/123-add-refresh` → 末尾が `123-...` なら GitHub Issue番号候補として扱い、1つに解決できれば更新

補足:
- `main` / `develop` など「手がかりが無い」ブランチでは、active は変更されません（静かに維持されます）
- この挙動を避けたい場合は `sync --no-update-active` を使ってください

## 2. `--github`（GitHub enrich）

`sync --github` を付けた場合のみ、`gh issue list ...` を用いて GitHub 側の状態を取得し、ローカル集計に補強します。

- 読み取りのみ（GitHub への更新はしません）
- `github.issue_number` が無いノードは enrich できません（`unknown` のまま）
- `--github` を付けない場合は GitHub 状態を更新しません（`gh` を呼びません）。ただし `.agent/index.json` が既に存在する場合は、過去のスナップショット（`status` / `github.state` 等）を保持します（古くなり得るため、必要なら再度 `sync --github` してください）。

## 3. 入出力（まとめ）

入力:
- ローカル: `spec-dock/initiatives/**/meta.json`（常に）
- active SSOT: `spec-dock/.agent/active.json`（存在すれば）
- 任意: GitHub（`--github` の場合のみ）

出力:
- `spec-dock/.agent/index.json`（フラット索引 + progress）
- `spec-dock/.agent/tree.json`（ツリー表示）
- `spec-dock/.agent/deps.json`（依存グラフ SSOT）
- `spec-dock/.agent/deps.puml`（依存グラフ: 全体）
- `spec-dock/.agent/deps.todo.puml`（依存グラフ: Done 除外）
- `spec-dock/active/**`（active pointer + `context-pack.md`、ただし `--no-update-active` では更新しない）

補足:
- deps 派生物は deps preflight が成功した場合に生成されます（`sync --force` で deps 構造エラーがある場合は削除されます）。

## 4. PlantUML（処理フロー）

```plantuml
@startuml
skinparam monochrome true
hide footbox

actor User
participant "spec-dock\n(runtime script)" as Script
participant "Local FS\n(meta.json)" as FS
participant "git\n(branch)" as Git
participant "gh\n(GitHub CLI)" as GH
database ".agent/index.json" as Index
database ".agent/tree.json" as Tree

User -> Script: sync [flags]
Script -> FS: scan meta.json
Script -> Script: preflight validate\n(fail unless --force)

alt update_active (default)
  Script -> Git: current branch
  Script -> Script: infer active (best-effort)
end

alt --github
  Script -> GH: gh issue list ...
  Script -> Script: enrich states
end

Script -> Index: write
Script -> Tree: write
@enduml
```
