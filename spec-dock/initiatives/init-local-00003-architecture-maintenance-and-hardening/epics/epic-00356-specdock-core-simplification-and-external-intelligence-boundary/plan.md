---
種別: 計画書（Epic）
ID: "<EPIC_ID>"
タイトル: "SpecDock Core Simplification and External Intelligence Boundary"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft"
作成者: "ChatGPT"
最終更新: "2026-08-07"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# <EPIC_ID> SpecDock Core Simplification and External Intelligence Boundary — 計画（Issue と実施順序）

## 1. 計画方針

### Epic classification

- `multi-issue implementation`
- 単独Epic
- Issue数: 4
- 専用のfinal-quality Issue: 作らない
- Epic全体のintegration、migration、final verificationは最後のCutover Issueへ含める

### 分割原則

- 技術レイヤーではなく、独立して検証可能な契約単位で分割する。
- Planning-only Issue、Review-only Issue、Metrics-only Issueを作らない。
- Core、Authoring Kit、Skill Integrationは責務が異なるため分離する。
- Installer / migration / dogfoodは横断統合であるため最後のIssueにまとめる。
- 既存historical nodeや文書の一括変換Issueを作らない。

## 2. Issue一覧

実際のIDはSpecDock CLIとGitHub Issue作成後に確定する。

### I1 Reduce Runtime to Storage Core

#### 目的

SpecDock runtimeから認知・運用workflowを削除し、Storage Coreの決定的操作だけを残す。

#### 成果物

- target command registry
- retained core domain / application / infra
- removed workflow / assurance / authoring / ChatGPT modules
- core-only CLI help
- focused core regression
- removal inventory

#### 主な範囲

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- runtime parser / registry / wrappers
- dogfood runtime projection
- corresponding tests

#### 完了条件

- node、artifact、deps、active、issue lifecycle、sync、validate、update、uninstallが動作する。
- workflow / assurance / delegated authoring / product ChatGPT commandが存在しない。
- existing node treeとdependency storage formatを変更しない。
- Core testが成功する。

#### 依存

- なし

---

### I2 Simplify Authoring Kit and Document Contracts

#### 目的

Requirement / Design / Planの丁寧な作成方法を維持しつつ、旧workflow gateと
provider-specificな義務を除去する。

#### 成果物

- simplified Initiative / Epic / Issue templates
- authoring overview
- requirement guide
- design guide
- plan guide
- scope layering guide
- artifact guide
- optional report semantics
- old workflow docsの削除または非current化
- template / docs regression

#### 主な範囲

- `src/spec_dock/assets/spec_dock/templates/`
- `src/spec_dock/assets/spec_dock/docs/`
- dogfood template / docs projection
- README / guide

#### 完了条件

- Templateにgrade、reviewer gate、EAL、promotion、fallback、PR readinessが残っていない。
- Guideが各文書の役割、品質、Scope差を説明する。
- Templateは最小scaffoldであり、詳細説明はGuideに集約される。
- Intelligence provider名やmodel名に依存しない。

#### 依存

- なし
- I1と並行可能

---

### I3 Replace Managed Workflow Skills with SpecDock Skills

#### 目的

現在の多数のmanaged Skill / adapter / roleを、二つのRepo-local Skillへ置き換える。

#### 成果物

- `spec-dock`
- `spec-dock-grill-with-docs`
- Codex `agents/openai.yaml`
- required external capabilityの明示
- managed Skill inventory縮小
- obsolete Skill / host adapter / named role removal
- integration contract tests

#### `spec-dock`の完了条件

- Scope、canonical docs、Artifact、node、dependencyをモデルへ案内する。
- structure mutationはCLIへ誘導する。
- invoking workflowを優先し、Planning / Review / Implementationを規定しない。
- current Authoring KitとCLI helpをpointerで参照する。

#### `spec-dock-grill-with-docs`の完了条件

- explicit / active Scopeを解決する。
- Scope-local Artifactを一つ作成する。
- 外部`grilling` / `domain-modeling`を利用する。
- Fact、Decision、Alternative、Open Question、Authoring Briefを記録する。
- canonical Requirement / Design / Planを自動変更しない。
- missing external capabilityを明確に報告する。
- implicit invocationを無効にする。

#### 依存

- I1
- I2

---

### I4 Cut Over Distribution and Retire Legacy Workflow Surfaces

#### 目的

Provider、fresh consumer、existing consumer、dogfoodを新境界へ揃え、旧workflowを
安全にretireする。

#### 成果物

- installer `init` inventory
- `update` obsolete cleanup
- `uninstall` inventory
- provider / dogfood / installed parity
- fresh consumer smoke
- existing consumer preservation smoke
- release / migration documentation
- legacy command / Skill / role / docs pointer absence checks
- manual external intelligence smoke
- `init-00322` supersede / closure plan
- mergeable delivery

#### 完了条件

- Fresh initがStorage Core、Authoring Kit、二つのSkillだけを導入する。
- Existing updateがnode、docs、Artifact、dependency、Workbench contentを保持する。
- 旧managed workflow assetが残らない。
- Full Core regression、lint、validate、syncが成功する。
- 次の手動シナリオを確認する。
  1. Scope作成
  2. Artifact作成
  3. dependency登録
  4. `spec-dock-grill-with-docs`
  5. ChatGPT-Use Strict等で三文書作成
  6. Codex GoalでIssue実装
- Historical `init-00322` dataは保持され、current workflowとして参照されない。
- Breaking changeとmigration boundaryがREADME / release noteに明記される。

#### 依存

- I1
- I2
- I3

## 3. 依存グラフ

```plantuml
@startuml
skinparam monochrome true
left to right direction

rectangle "I1
Reduce Runtime to Storage Core" as I1
rectangle "I2
Simplify Authoring Kit" as I2
rectangle "I3
Replace Managed Skills" as I3
rectangle "I4
Cut Over and Retire Legacy" as I4

I1 --> I3 : blocks
I2 --> I3 : blocks
I1 --> I4 : blocks
I2 --> I4 : blocks
I3 --> I4 : blocks
@enduml
```

SpecDock dependency direction:

```text
I3 depends_on I1
I3 depends_on I2
I4 depends_on I1
I4 depends_on I2
I4 depends_on I3
```

CLI適用時は、dependentを`--from`、prerequisiteを`--to`にする。

## 4. 実施順序

### Lane A

1. I1 Storage Core
2. I3 Skills
3. I4 Cutover

### Lane B

1. I2 Authoring Kit
2. I3との統合
3. I4 Cutover

I1とI2は並行可能。I3は両方のstable contractを参照する。I4が唯一の横断統合Issueとなる。

## 5. Issue handoff共通条件

各Issueは次を継承する。

- Parent EpicのRequirement / Design / Planを変更せず、必要な変更はEpicへ戻す。
- Existing `spec-dock/initiatives/**` dataを一括変換しない。
- Provider sourceをauthorityとし、dogfood projectionを検証する。
- User-owned external Skillを削除しない。
- External providerをCore dependencyにしない。
- 旧workflowを別名で再実装しない。
- 変更対象のtestsとcurrent full Core regressionを通す。
- `validate`と`sync`でlocal graph整合性を確認する。

## 6. 品質戦略

### 必須自動検証

- Ruff / format / mypy
- Core unit / CLI regression
- installer init / update / uninstall
- packaged asset inventory
- provider / dogfood parity
- no-current-reference regression
- fresh consumer
- existing consumer preservation

### 手動検証

- `spec-dock` SkillによるScope / docs / dependency参照
- `spec-dock-grill-with-docs`によるArtifact作成
- external capability absence時の停止
- ChatGPT-Use Strict等によるAuthoring Kit利用
- Codex GoalによるPlanベース実装

External browser/model自体をCIへ組み込まない。

## 7. Migrationとrollout

### Rollout順序

1. I1 / I2を完成させる。
2. I3を新Core / Kitへ接続する。
3. I4でinstallerとdogfoodをhard cutoverする。
4. Majorまたは明確なbreaking releaseとして配布する。
5. Existing consumerは`update`前に通常のGit backupを持つ。
6. Update後に`validate` / `sync`を実行する。
7. Legacy automation Initiativeとopen workをsupersededとして整理する。

### Data preservation

保持:

- node directories
- `.meta.json`
- dependency edges
- Requirement / Design / Plan / Report
- Artifact / Discussion / ADR
- Workbench unmanaged content

削除対象:

- SpecDock-managed workflow Skill
- SpecDock-managed agent role / host adapter
- SpecDock-managed PR workflow asset
- product-owned ChatGPT runtime
- obsolete workflow docs / templates / scripts
- generated stateは再生成可能な範囲で更新

## 8. 最終完了条件

- Storage CoreとAuthoring Kitが明確な製品境界としてREADMEに記載されている。
- Managed Skillは二つだけである。
- Runtimeに旧workflow commandがない。
- Existing dataとdependency graphが保持される。
- Fresh / existing consumerの両方でCoreが動作する。
- External intelligenceを交換してもCore変更が不要な契約になっている。
- `init-00322`の旧自動化方針がcurrent routeとして残っていない。
- 本Epicの4 Issueが完了し、required CIとレビューを通した一つのmergeable PRまたは
  明示されたdelivery単位が完成している。

## 9. 未確定事項

なし。
