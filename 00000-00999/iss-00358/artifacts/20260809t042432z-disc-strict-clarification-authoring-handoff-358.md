---
種別: disc
ID: "20260809t042432z-disc"
タイトル: "Issue 358 Strict clarification authoring handoff"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00358"]
関連: ["iss-00357"]
authority: "advisory"
derived_from:
  - "20260808t082616z-research-authoring-kit-clarification.md"
  - "20260808t083300z-interview-issue-profile-and-draft-routing.md"
  - "20260808t085519z-01-disc-planning-level-authoring-documents-architecture.md"
  - "20260808t085519z-interview-planning-level-authoring-architecture-adoption.md"
  - "20260809t025001z-interview-target-report-contract.md"
  - "iss-00357/20260808t092131z-interview-target-issue-finish-semantics.md"
  - "iss-00357/20260808t162136z-interview-target-active-start-and-readiness-semantics.md"
  - "iss-00357/20260809t004834z-interview-target-artifact-surface.md"
reflected_to: []
strict_session: "required-strict-github-connector-verificati-8"
verified_github_sha: "d265c2eeb2cc8112f158d17e3b082581941aba37"
---

# Issue 358 Strict clarification authoring handoff

## 位置づけ

このArtifactは、元のChatGPTスレッドに対してChatGPT Use Strictを実施し、Issue 358の`requirement.md`、`design.md`、`plan.md`を新規作成するための引き継ぎを整理したAdvisory Evidenceである。

- GitHub connectorで`chemitaro/spec-dock`の`main`を確認し、先端が`d265c2eeb2cc8112f158d17e3b082581941aba37`と一致した。
- 追加のProduct Owner質問はない（`unresolved Product Owner questions: none`）。
- 採用済み判断はまだCanonical文書へ反映されていない。
- 本Artifact自体はReview合格、Planning完了、Implementation readinessを意味しない。
- ChatGPT画面上のモデル表示は`Pro`であり、厳密な内部モデル名は主張しない。

## Issue 357と358の並行作業境界

> Issue 358が、現在のAuthoring Surfaceに何が存在し、それが何を意味するかを定義する。Issue 357が、そのSurfaceを安全に生成・保存・操作するRuntime mechanismを実装する。

| Surface | Issue 357 | Issue 358 |
| --- | --- | --- |
| Parser / Registry / Command | 所有 | 変更しない |
| Lifecycle / Active / Dependency | 所有 | Guideで意味を説明するだけ |
| Template本文 / Authoring Guide本文 | 変更しない | 所有 |
| Artifact typeの意味 | 参照して実装 | 所有 |
| Artifact path / 命名 / lock / symlink | 所有 | 参照 |
| Node scaffold mechanism | 所有 | Scaffold内容を定義 |
| `report.md`本文 | 変更しない | 所有 |
| Planning Level | 解釈しない | 文書契約を所有 |
| Installer prune / Managed Skill | Inventoryを後続へ渡す | Inventoryまたは参照Pathを後続へ渡す |

## Requirement authoring handoff

### 目的

特定のモデル、Skill、Workflowに依存せず、Initiative / Epic / IssueのRequirement、Design、Planを高品質に作成できる、薄いTemplateと詳細GuideからなるAuthoring Kitを提供する。

### Canonical文書の責務

- `requirement.md`: 何を、なぜ、どの条件で実現するか。
- `design.md`: どの境界、構造、契約で実現するか。
- `plan.md`: どの順序、検証、完了条件で実装するか。
- `report.md`: Outcome、Verification、Residual Risks / Follow-upsの軽量Result Summary。

`report.md`は全Scopeで常設するが、記入は任意、空でもvalid、Workflow authorityではない。Durableな要件・設計・計画判断はR/D/Pへ、長寿命のArchitecture decisionはADRへ反映する。

### Planning Level

- 各IssueのCanonical `plan.md`は一つだけにする。
- 共通のPlan Guideと、`light`、`standard`、`strict`、`critical`の4 Completion Guideを提供する。
- Level、選択理由、Risk factor、再評価条件は`plan.md`本文に記載する。
- Runtime stateやMetadataにしない。
- Git diffを履歴とする。
- LevelはPriority、Dependency readiness、Implementation readinessを意味しない。
- Initiative / Epic PlanにはIssue Planning Levelを要求しない。

### Artifact semantics

| Type | 意味 |
| --- | --- |
| `blank` | Template拘束の弱い自由形式 |
| `research` | Source-groundedな単独調査 |
| `interview` | Product Owner等への明示質問と回答 |
| `disc` | 複数Evidenceの統合、分析、Reflection |
| `decision-candidate` | 未採用の判断候補 |
| `adr` | Architecture decision候補・記録 |

- Artifactが存在するだけではCanonical authorityにならない。
- 採用された内容をR/D/PまたはADRへ反映する。
- `analysis`は追加しない。単独調査は`research`、統合分析は`disc`を使う。
- Existing `pr-repair-batch`、`draft-*`、旧Discussion等はHistorical Evidenceとして保持する。

### In scope

- Initiative / Epic / IssueのR/D/P/Report Template
- Authoring overview
- Requirement / Design / Plan / Report Guide
- Planning Level Completion Guides
- Scope Layering Guide
- Artifact Guide / Rules
- Current / Historical navigation
- Provider templates / docsとdogfood projection
- Template / Docs / Link / Parity tests
- Removed Docs / Templates Inventory

### Out of scope

- Parser / Registry / Runtime
- Active / Lifecycle実装
- Artifact filename parser
- Dependency algorithm
- Node scaffolder実装
- Managed Skill本文
- Installerの最終Prune
- Existing Canonical文書、Report、Artifactの一括更新
- External intelligence smokeのRelease判定
- Issue 359 / 360の実装

## Design authoring handoff

### 推奨Provider-side構造

```text
src/spec_dock/assets/spec_dock/
├── templates/
│   ├── initiative/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   ├── epic/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   ├── issue/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── report.md
│   └── artifacts/
│       ├── blank.md
│       ├── research.md
│       ├── interview.md
│       ├── disc.md
│       ├── decision-candidate.md
│       └── adr.md
└── docs/
    ├── README.md
    ├── authoring/
    │   ├── overview.md
    │   ├── requirement.md
    │   ├── design.md
    │   ├── plan.md
    │   ├── report.md
    │   ├── scope-layering.md
    │   ├── artifacts.md
    │   └── issue-plan-levels/
    │       ├── light.md
    │       ├── standard.md
    │       ├── strict.md
    │       └── critical.md
    └── reference/
```

Dogfood projectionは同じ相対構造を`spec-dock/`以下に持つ。

### TemplateとGuideの分離

Templateに置くもの:

- 完成文書に残る見出し
- 各節の一行説明
- 最低限のPlaceholder

Guideに置くもの:

- 良い例・悪い例
- Scope差
- Optional section
- Diagram選択
- Test / Rollback / Migration
- 典型的な欠落
- Pressure test
- Anti-pattern

Templateへ詳細Policyを複製せず、GuideもProvider名、Model名、Prompt形式を必須契約にしない。

### `report.md` Target Template

```markdown
# Result Summary

## Outcome

## Verification

## Residual Risks / Follow-ups
```

必要なら`Notes`程度の4節目を許可する。Decision Ledger、EAL、Objective Alignment Ledger、Authoring Gate、Reviewer Status、Delegated Draft Evidence、Promotion、Completion Gateを含めない。Fresh Templateだけを置換し、Existing Report本文は保持する。

### Scope Layering / Authority

- ArtifactはEvidence。
- R/D/PはCanonical specification。
- Accepted ADRは長寿命Decision。
- Reportは結果要約。
- Durable decisionはR/D/PまたはADRへ反映する。
- Reviewer passやEALを文書構造上のAuthority条件にしない。

### Planning LevelのProgressive Disclosure

- Issue Planだけに適用する。
- 共通Guideと選択した1つのLevel Guideだけを読む。
- Level Guide間で共通規則を複製しない。
- Critical利用者にStandard / Strictの順読を強制しない。
- 未指定時の`standard`はAuthoring上の推奨にできるが、Runtime defaultにはしない。

## Plan authoring handoff

1. Templates、Authoring / Workflow / Phase docs、Rules、Report / Artifact / Profile templates、Provider / dogfood / testsの完全Inventoryを作る。
2. Requirement、Design、Plan、Report、Scope Layeringの意味論を固定する。
3. Base Plan Guideと4 Completion Guide、Plan TemplateのLevel sectionを作る。
4. Current Artifact 6種、Historical-only catalog、Rules、Navigation、Reflection先を整える。
5. Initiative / Epic / Issue / Report / Artifact templatesを薄型化する。
6. Storage Core + Authoring KitをCurrent docsの入口とし、旧Workflow docsをCurrent routeから外す。
7. Dogfood projection、byte parity、link、forbidden vocabulary、file inventoryを検証する。
8. Issue 359へGuide path、Issue 360へobsolete asset一覧を渡す。

### 受け入れ条件・回帰義務

- 全Scopeに薄いR/D/P/Report Templateが存在する。
- TemplateにGrade、Reviewer Gate、Promotion、EAL、Delegated Authoring、PR readinessがない。
- Requirement / Design / Plan / Reportの責務がGuideで分離される。
- Issue Plan Templateは一つだけで、4 Completion Guideが存在する。
- `plan-light.md`等のCanonical fileを生成しない。
- Planning LevelをRuntime metadataやauthorityとして説明しない。
- Reportは3〜4節、記入任意、空でもvalidと説明する。
- 6 Artifact typeの用途が重複なく、Current / Historicalを分けて説明される。
- `pr-repair-batch`、`draft-*`をCurrent catalogに含めない。
- Current navigationから旧Workflow docsを正規経路として案内しない。
- GuideはProvider-neutralで、Templateに詳細Policyを過剰複製しない。
- Provider / dogfood parity、catalog exact match、link validity、forbidden vocabularyを検証する。
- Initiative / Epic PlanへIssue Planning Levelを要求しない。
- Existing consumer文書のHashを変更しない。

## Migration / Historical compatibility

- Provider Template変更はFresh Nodeへ適用する。
- Existing Node-local R/D/P/ReportをUpdateで書き換えない。
- Existing `.assurance.json`、Profile由来文書、Draft、PR repair、Discussion、ADRを削除・移動しない。
- Obsolete managed Provider template / docsのPruneはIssue 360が行う。
- Historical文書に旧語彙が残ることは許容する。
- Current navigationからは旧語彙を正規契約として案内しない。

## 後続IssueへのHandoff

Issue 359へ渡すもの:

- Authoring overviewとRequirement / Design / Plan / Report Guide path
- Planning Level Guide path
- Scope LayeringとArtifact Rules path
- Current Artifact catalog
- Canonical / Evidence / Reportの意味

Issue 360へ渡すもの:

- Fresh install対象のTemplate / Docs一覧
- Obsolete profile / workflow / provider固有Asset一覧
- Existing consumer preservation対象
- Provider / dogfood / installed parity期待値
- Current navigationから削除するLink一覧

## 未解決事項と注意

- Product Ownerへ追加で確認すべき高影響な意図上のGapはない。
- External intelligence smokeのRelease上の位置づけは主にIssue 359 / 360と親Epicの責務であり、Issue 358の仕様作成を妨げない。
- 親Epicには古いBaseline、`analysis`、`optional report.md`、Lifecycle未定義等が残るため、Fresh Review前に別途整合させる。
- Canonical文書は旧Assurance Composeを使わず、採用済みArtifactから完全ファイルとしてAuthoringする。
- Dependency-readyをImplementation-readyと表現しない。

## 推奨反映先

- `requirement.md`: 文書責務、Planning Level、Artifact semantics、Report、In / Out、Acceptance Criteria。
- `design.md`: Provider file tree、Template / Guide分離、Scope Layering、Progressive Disclosure、Historical compatibility。
- `plan.md`: Complete Inventoryからprojection / regression / handoffまでの段階、テスト義務、完了条件。
- ADR: 現時点で新規ADR必須の論点なし。採用済み契約はCanonical文書で十分に表現できる。
