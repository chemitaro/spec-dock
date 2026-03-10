# guide（全体像 / 導線）

spec-dock の docs レイヤ、概念、生成物を最短で把握するための入口です。
scope 固有の手順は `workflow_*.md`、shared な requirement / design / plan の作法は `phase_*.md`、コマンドや制約は `reference_*.md` を正本とします。

## docs の読み分け

- `workflow_*.md`: Initiative / Epic / Issue / ADR の scope 固有 workflow
- `phase_*.md`: phase playbook（共通の作り方）
- `reference_*.md`: GitHub / naming / deps / sync などの参照仕様
- `discussions/`: 調査、議論、メモ、ADR の置き場

phase playbook:
- [phase_requirement.md](phase_requirement.md)
- [phase_design.md](phase_design.md)
- [phase_plan.md](phase_plan.md)

入口:
- Initiative: [workflow_initiative.md](workflow_initiative.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- Issue: [workflow_issue.md](workflow_issue.md)
- ADR: [workflow_adr.md](workflow_adr.md)

## 基本概念

- Initiative: 投資単位。なぜやるか、成功条件、スコープを持つ
- Epic: 設計の背骨。契約、移行、観測性、Issue 分割を持つ
- Issue: 実装の最小単位。active issue を起点に TDD で完了する
- ADR: 後続へ残る意思決定。initiative / epic / issue の任意 scope に紐づく

親子関係:

```text
Initiative
└── Epic
    └── Issue
```

## 生成物と SSOT

- SSOT: `spec-dock/initiatives/**/.meta.json`
- 主な生成物: `spec-dock/active/**`, `spec-dock/.agent/{active,index,tree}*.json`, `spec-dock/{tree,deps-issues}*.puml`, `spec-dock/dashboard.md`
- GitHub は入口として連携できるが、仕様ツリーの正はローカル metadata

代表構造:

```text
spec-dock/
├── initiatives/
│   └── init-.../
│       ├── requirement.md
│       ├── design.md
│       ├── plan.md
│       ├── report.md
│       ├── discussions/
│       └── epics/
│           └── epic-.../
│               ├── requirement.md
│               ├── design.md
│               ├── plan.md
│               └── issues/
│                   └── issue-.../
│                       ├── requirement.md
│                       ├── design.md
│                       ├── plan.md
│                       ├── report.md
│                       └── discussions/
├── templates/
├── scripts/
├── docs/
├── active/
└── .agent/
```

## 最短 workflow

1. 既存ノードに収まるか確認し、必要なら `new` / `import` する
2. `active set` で作業対象を固定する
3. 対象 scope の `workflow_*.md` を正本にし、requirement / design / plan は `phase_*.md` に沿って書く
4. Initiative は Epic 分解、Epic は Issue 分割、Issue は TDD + review loop を進める
5. `validate` / `sync` で整合性と生成物を更新する

## 次に読む

- 実務導線: [README.md](README.md)
- 作業対象別 workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 参照仕様: [reference_github.md](reference_github.md), [reference_naming.md](reference_naming.md), [reference_deps.md](reference_deps.md), [reference_sync.md](reference_sync.md)
