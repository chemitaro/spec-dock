# guide（全体像 / 概念 / 生成物）

このドキュメントは、spec-dock の **概念**と **生成物**と **ディレクトリ構造**を最短で理解するための総合ガイドです。  
具体的な手順（品質ゲート/チェックリストを含む）は、各ワークフローへ移動しています。

- Initiative: [workflow_initiative.md](workflow_initiative.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- Issue: [workflow_issue.md](workflow_issue.md)
- ADR: [workflow_adr.md](workflow_adr.md)

参照（仕組み）:
- GitHub: [reference_github.md](reference_github.md)
- Naming: [reference_naming.md](reference_naming.md)
- deps: [reference_deps.md](reference_deps.md)
- sync: [reference_sync.md](reference_sync.md)

## 0. phase playbook（共通の作り方）

scope（initiative / epic / issue）をまたいで再利用する requirement / design / plan の作法は、次の playbook を参照してください。

- requirement: [phase_requirement.md](phase_requirement.md)
- design: [phase_design.md](phase_design.md)
- plan: [phase_plan.md](phase_plan.md)

補足:
- scope 固有の制約や分解方針は `workflow_*.md` を正本にします。
- playbook 本文を workflow に複製せず、導線で結ぶ構成を維持します。

## 1. spec-dock が管理するもの（SSOT と生成物）

spec-dock の SSOT（Source of Truth）は **ローカルのメタデータ**です。

- SSOT（永続）: `spec-dock/initiatives/**/.meta.json`
- 生成物（git 管理しない）: `spec-dock/.agent/{active.json,index-all.json,tree-all.json,index.json,tree.json,deps-issues.json}`、`spec-dock/{tree-all.puml,tree.puml,deps-issues.puml,dashboard.md}`、`spec-dock/active/**`

GitHub は「作業の入口（Issue番号/URL）」として連携できますが、**ローカルの仕様ツリーが正**です。

## 2. 基本概念（Initiative / Epic / Issue / ADR）

- Initiative: 投資単位（なぜやるか/成功条件/スコープ）
- Epic: 設計の背骨（契約・移行・観測性・分割）
- Issue: 実装の最小単位（TDDで完了する）
- ADR: 意思決定の分離（議論→決定→accepted）

補足:
- ADR はツリーの「親子レイヤー」ではなく、initiative/epic/issue の任意のスコープに紐づく **要素**です（保存先は各ノード配下の `discussions/`）。
- 補足資料（調査メモ/図/ログ断片）も各ノード配下の `discussions/` に置きます（ガイドは `discussions/rules.md`、テンプレは `spec-dock/templates/discussions/*.md`）。

親子関係（ツリー）:

```text
Initiative
└── Epic
    └── Issue
```

## 3. ディレクトリ構造（導入先リポジトリ）

導入直後の全体像（代表例）:

```text
spec-dock/
├── initiatives/                 # SSOT（常置）
│   └── init-00001-.../
│       ├── .meta.json
│       ├── requirement.md
│       ├── design.md
│       ├── plan.md
│       ├── report.md
│       ├── discussions/
│       │   ├── rules.md
│       │   └── 001-adr-....md
│       └── epics/
│           ├── new-epic
│           └── epic-00001-.../
│               ├── discussions/
│               │   ├── rules.md
│               │   └── 002-disc-....md
│               └── issues/
│                   ├── new-issue
│                   └── iss-00001-.../
│                       └── discussions/
│                           ├── rules.md
│                           ├── 003-adr-....md
│                           └── 004-research-....md
├── templates/                   # テンプレ（導入物）
├── scripts/                     # runtime script（導入物）
├── system/                      # placeholders 等（導入物）
├── docs/                        # 配布ドキュメント（このディレクトリ）
├── active/                      # 生成物（git 管理しない）
│   ├── initiative -> ...        # symlink または `.path`
│   ├── epic -> ...
│   ├── issue -> ...
│   └── context-pack.md          # エージェントの入口（生成物）
└── .agent/                      # 生成物（git 管理しない）
    ├── active.json              # active の SSOT
    ├── index.json               # 集計（フラット）
    └── tree.json                # 集計（ツリー）
```

## 4. 大枠のワークフロー（最短）

### 4.1 作る（new / import）

- initiative / epic は、`new` / `import` の前に既存ノードの requirement / design / plan を確認し、適合するなら既存ノードを更新します。
- 新規作成は、既存ノードに収めると投資判断や Done 定義が崩れる場合だけ行います。
- 新規作成した理由や既存ノードに収めない理由は、作成後の対象ノード配下 `discussions/` の最初の `disc` に残します。
- `new`: spec-dock がローカルノードを作ります
  - issue は（デフォルトで）GitHub Issue も作ります（`--no-github` で local-only）
  - initiative/epic は（デフォルトで）local-only です（必要なら `--create-github-issue` / `--github-issue <n>` で GitHub と紐づけ）
- `import`: 既存 GitHub Issue を **読み取り確認**した上で、ローカルノードを作ります
  - `import epic` は `--initiative` を省略すると、current active から親 initiative を解決します
  - `import issue` は `--epic` を省略すると、current active から親 epic を解決します
  - `--title` / `--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。
- 生成済みノード配下では、親IDを省略できる wrapper が使えます（引数はタイトル1つのみ）。
  - initiative 配下: `epics/new-epic "<title>"`
  - epic 配下: `issues/new-issue "<title>"`
- discussion docs は runtime command で作成します（scope を明示）。
  - `./spec-dock/scripts/spec-dock new doc adr --issue <issue-id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc disc --issue <issue-id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc research --issue <issue-id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc note --issue <issue-id> --title "<title>"`
  - epic/initiative スコープでも同様に `--issue` を `--epic` / `--initiative` に置き換えて使います。

補足:
- Initiative/Epic/Issue ノード直下や `epics/` / `issues/` / `discussions/` に、テンプレ由来の `README.md` は生成されません。
- discussion docs の命名は `NNN-type-slug.md`（3桁固定）です。`rules.md` と nonconforming files は採番対象外です。

### 4.2 アクティブにする（active set）

`active set` は「いま作業する単位」を固定し、`spec-dock/active/context-pack.md` を生成します。  
デフォルトは **active 更新のみ（no-checkout）**です。  
ブランチ操作が必要な場合だけ `--checkout` を明示します（詳細は [reference_github.md](reference_github.md)）。

### 4.3 観測できる状態へ（validate / sync）

- `validate`: 仕様ツリーの整合性（メタデータ）を検証します
- `sync`: 集計物（`.agent/index-all.json` / `.agent/tree-all.json` / `.agent/index.json` / `.agent/tree.json` / `.agent/deps-issues.json`）と可視化ファイル（`tree*.puml` / `deps-issues.puml` / `dashboard.md`）を生成します

## 5. PlantUML（全体のイメージ）

```plantuml
@startuml
skinparam monochrome true
hide footbox

actor User
participant "spec-dock\n(runtime script)" as Script
database "SSOT\n.meta.json" as Meta
participant "git\n(branch)" as Git
participant "gh\n(GitHub CLI)" as GH
database "Derived\n.agent/{index,tree}.json" as Derived
database "Active\nactive/** + context-pack" as Active

User -> Script: new / import
Script -> Meta: write .meta.json\n(+ spec templates)

User -> Script: active set <target>
alt --checkout
  Script -> Git: checkout (safety checks)
end
Script -> Active: update pointers\n+ context-pack.md

User -> Script: validate
Script -> Meta: scan + validate

User -> Script: sync
Script -> Meta: scan
Script -> Derived: write index/tree
Script -> Active: (optional)\nupdate active from branch
@enduml
```

## 6. 次に読む

- 実作業を始める: [workflow_issue.md](workflow_issue.md)
- GitHub 連携の前提/注意: [reference_github.md](reference_github.md)
- `sync` の仕組み: [reference_sync.md](reference_sync.md)
