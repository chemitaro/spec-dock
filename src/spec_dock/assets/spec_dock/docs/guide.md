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
- sync: [reference_sync.md](reference_sync.md)

## 1. spec-dock が管理するもの（SSOT と生成物）

spec-dock の SSOT（Source of Truth）は **ローカルのメタデータ**です。

- SSOT（永続）: `spec-dock/initiatives/**/meta.json`
- 生成物（git 管理しない）: `spec-dock/.agent/{active.json,index.json,tree.json}`、`spec-dock/active/**`

GitHub は「作業の入口（Issue番号/URL）」として連携できますが、**ローカルの仕様ツリーが正**です。

## 2. 基本概念（Initiative / Epic / Issue / ADR）

- Initiative: 投資単位（なぜやるか/成功条件/スコープ）
- Epic: 設計の背骨（契約・移行・観測性・分割）
- Issue: 実装の最小単位（TDDで完了する）
- ADR: 意思決定の分離（議論→決定→accepted）

補足:
- ADR はツリーの「親子レイヤー」ではなく、initiative/epic/issue の任意のスコープに紐づく **要素**です（保存先は各ノード配下の `adrs/`）。
- 補足資料（調査メモ/図/ログ断片）は各ノード配下の `artifacts/` に置きます（初期ファイル: `artifacts/_template.md`）。

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
│       ├── meta.json
│       ├── requirement.md
│       ├── design.md
│       ├── plan.md
│       ├── report.md
│       ├── artifacts/
│       │   └── _template.md
│       ├── adrs/                # ADR（initiative scope）
│       │   └── new-adr
│       └── epics/
│           ├── new-epic
│           └── epic-00001-.../
│               ├── artifacts/
│               │   └── _template.md
│               ├── adrs/        # ADR（epic scope）
│               │   └── new-adr
│               └── issues/
│                   ├── new-issue
│                   └── iss-00001-.../
│                       ├── artifacts/
│                       │   └── _template.md
│                       └── adrs/  # ADR（issue scope）
│                           └── new-adr
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

- `new`: spec-dock がローカルノードを作り、（デフォルトでは）GitHub Issue も作ります
- `import`: 既存 GitHub Issue を **読み取り確認**した上で、ローカルノードを作ります
  - `--title` / `--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。
- 生成済みノード配下では、親IDを省略できる wrapper が使えます（引数はタイトル1つのみ）。
  - initiative 配下: `epics/new-epic "<title>"`
  - epic 配下: `issues/new-issue "<title>"`
  - 任意スコープ配下: `adrs/new-adr "<title>"`

補足:
- Initiative/Epic/Issue ノード直下や `epics/` / `issues/` / `adrs/` / `artifacts/` に、テンプレ由来の `README.md` は生成されません。

### 4.2 アクティブにする（active set）

`active set` は「いま作業する単位」を固定し、`spec-dock/active/context-pack.md` を生成します。  
デフォルトは **active 更新のみ（no-checkout）**です。  
ブランチ操作が必要な場合だけ `--checkout` を明示します（詳細は [reference_github.md](reference_github.md)）。

### 4.3 観測できる状態へ（validate / sync）

- `validate`: 仕様ツリーの整合性（メタデータ）を検証します
- `sync`: 集計物（`.agent/index.json` / `.agent/tree.json`）を生成します

## 5. PlantUML（全体のイメージ）

```plantuml
@startuml
skinparam monochrome true
hide footbox

actor User
participant "spec-dock\n(runtime script)" as Script
database "SSOT\nmeta.json" as Meta
participant "git\n(branch)" as Git
participant "gh\n(GitHub CLI)" as GH
database "Derived\n.agent/{index,tree}.json" as Derived
database "Active\nactive/** + context-pack" as Active

User -> Script: new / import
Script -> Meta: write meta.json\n(+ spec templates)

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
