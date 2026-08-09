---
種別: disc
ID: "20260809t042431z-disc"
タイトル: "Issue 357 Strict clarification authoring handoff"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00357"]
関連: ["iss-00358"]
authority: "advisory"
derived_from:
  - "20260808t082616z-research-storage-core-runtime-clarification.md"
  - "20260808t092131z-interview-target-issue-finish-semantics.md"
  - "20260808t162136z-interview-target-active-start-and-readiness-semantics.md"
  - "20260809t004834z-interview-target-artifact-surface.md"
  - "iss-00358/20260808t083300z-interview-issue-profile-and-draft-routing.md"
  - "iss-00358/20260808t085519z-interview-planning-level-authoring-architecture-adoption.md"
  - "iss-00358/20260809t025001z-interview-target-report-contract.md"
reflected_to: []
strict_session: "required-strict-github-connector-verificati-8"
verified_github_sha: "d265c2eeb2cc8112f158d17e3b082581941aba37"
---

# Issue 357 Strict clarification authoring handoff

## 位置づけ

このArtifactは、元のChatGPTスレッドに対してChatGPT Use Strictを実施し、Issue 357の`requirement.md`、`design.md`、`plan.md`を新規作成するための引き継ぎを整理したAdvisory Evidenceである。

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

SpecDock Runtimeから認知的・運用的Workflowを除去し、次だけを担うStorage Coreへ縮退する。

- Node identityと階層
- GitHub Issue linkage
- Scope-local Artifact
- Dependency DAG
- Active Scope
- Thin Issue lifecycle
- Workbench / Worktree
- Sync / Validate / Doctor
- 決定的な構造操作

### Runtimeから除去するもの

- `assurance`
- `authoring`
- `guidance`
- `workflow`
- `delegated-authoring`
- Product-owned ChatGPT planning
- Runtime Profile / Grade分類
- Authority / grants / promotion record
- EAL判定
- Delegated Artifact判定
- Reviewer / Test / Plan completion判定
- `artifact import chatgpt-output`
- `pr-repair-batch`と`draft-*`の新規作成経路

### 維持するLifecycle契約

`active set`:

- Initiative / Epic / Issueの単純なActive Scope選択とする。
- Blocked Issueも調査・Clarification・Planning目的で選択できる。
- Authority、Review、Planning Level、Dependency readinessを評価しない。
- Current Active ManifestはIDとPathだけを保持する。

`issue start`:

- Issueだけを対象とする。
- 別の未完了Active IssueをGuardする。
- Dependency readinessを確認する。
- Branch checkout後にActiveを設定する。
- `--force`は未完了Active Issue Guardだけを迂回し、Dependency blockerは迂回しない。

`issue finish`:

- Active Issueを特定し、Linked GitHub Issueをcloseする。
- Already closedは成功とする。
- close成功後にactiveをclearし、post-syncする。
- close失敗時はactiveを保持する。
- clear失敗時はPartial Successとして再実行可能な診断を返す。
- 品質、Review、Plan、Test、`report.md`内容を判定しない。

### Artifact契約

Current creatable typeは次の6種とする。

```text
blank
research
interview
disc
decision-candidate
adr
```

- type省略時は`blank`。
- `analysis`は追加しない。
- Importは`artifact import file`だけをCurrent Surfaceに残す。
- Existing `pr-repair-batch`、`draft-*`、旧Discussion等はHistorical recognizableとして保持する。
- 新規作成可否と既存ファイル認識可否は別契約にする。

### `report.md`契約

- Fresh Initiative / Epic / Issueには薄い`report.md`を常にScaffoldする。
- 記入は任意で、空でもvalidとする。
- Runtimeは内容を読み、start / finish / dependency / quality / completionを判定しない。
- EAL、Reviewer Gate、Promotion、Delegated Authoringを復活させない。
- Existing `report.md`本文は自動変更しない。

### In scope

- Runtime Parser / Registry / Bootstrap
- Commands
- Domain / Application / Infra / Presentation
- Active Manifest / Context Pack
- Issue lifecycle
- Artifact type / filename / creation / import
- Node scaffold mechanism
- Runtime unit / CLI regression
- Provider Runtime sourceとdogfood Runtime projection
- Runtime Removal Inventory

### Out of scope

- Requirement / Design / Plan / Report Template本文
- Authoring Guide本文
- Planning Level Completion Guide本文
- Managed Skill本文
- Installerの最終Prune
- Release note / Migration Guide
- Existing Node / Document / Artifactの一括更新
- External intelligence smoke
- Issue 359 / 360の実装

## Design authoring handoff

### Current creatableとHistorical recognizableの分離

現行の単一集合が新規作成可否とFilename parse可否を兼ねる構造を分ける。概念上は次の2集合を持つ。

```python
CURRENT_CREATABLE_ARTIFACT_TYPES = (
    "blank",
    "research",
    "interview",
    "disc",
    "decision-candidate",
    "adr",
)

HISTORICAL_RECOGNIZABLE_ARTIFACT_TYPES = (
    "pr-repair-batch",
    "draft-requirement",
    "draft-design",
    "draft-plan",
    "scratch",
    "note",
)
```

正確なHistorical集合は実装前Inventoryで確定する。既存ファイルをMalformed扱いせず、新規作成だけを閉じることが設計目的である。

### Artifact CLI

推奨Target構文:

```text
spec-dock new artifact [type]
  (--initiative <id> | --epic <id> | --issue <id>)
  --title <title>
  [--slug <slug>]
```

- `type`は省略可能な位置引数、default=`blank`。
- 明示的な`blank`も許可する。
- `--type`との二重構文は追加しない。
- Helpに`[type]`、6種、defaultを表示する。
- これは既存の位置引数契約を最小変更するAdvisory設計解であり、Canonical Designで確定させる。

### Active State / Context Pack

- Current Active Manifestから`authority`、`grants`、`promotion_record`を除去する。
- Context PackからAuthority、Delegated Artifact、Report EALの評価を除去する。
- Active Scope、Parent chain、Canonical document path、Artifact path、Dependency view、generated stateへのPointerだけを提供する。

### Lifecycle / Node scaffold

- `issue finish`からAuthority Gate、Synthetic Promotion、Delegated Artifact validation、EAL parsingを除去する。
- close / clear / syncの順序とFailure recoveryは維持する。
- RuntimeはScope Template directoryを決定的にコピーするだけとし、文書内容を解釈しない。
- Fresh NodeにR/D/Pと薄い`report.md`を含める。
- `.assurance.json`を作成せず、Profile routingも行わない。

## Plan authoring handoff

1. Parser、Registry、Bootstrap、各Layer、tests、Provider / dogfood projectionを対象にRemoval Inventoryを作る。
2. Active Manifest、Context Pack、`active set`、`issue start`、`issue finish`を薄型化する。
3. Current / Historical Artifact typeを分離し、optional positional typeと`blank` defaultを実装する。
4. ChatGPT固有Importを除去し、generic file importの安全性を回帰確認する。
5. Node Scaffoldを単一R/D/P、薄いReport常設、Assurance非依存へ切り替える。
6. Retained Coreから参照がなくなった後にRemoved moduleを物理削除する。
7. Core regressionとRemoved Surface absenceを検証し、Issue 359 / 360へInventoryを渡す。

### 受け入れ条件・回帰義務

- Removed commandがParser、Registry、CLI helpから消え、別経路へfallbackしない。
- Fresh NodeをAssuranceなしで作成でき、薄い`report.md`が空でもRuntime操作を妨げない。
- Active ManifestはIDとPathだけである。
- `active set`はblocked Issueを選択できる。
- `issue start`はdependency blockerを`--force`でも迂回しない。
- `issue finish`はclose / clear / syncとPartial failure契約を満たす。
- type省略、明示blank、残る5 Typed types、unknown / historical-only拒否を検証する。
- Blank filenameに`blank` tokenを含めない。
- Same-second collision、suffix exhaustion、create lock、symlink、path escape、scope mismatchを回帰する。
- Generic importのopaque byte、privacy-safe output、collision、cleanupを回帰する。
- Existing `.assurance.json`、profile由来文書、`draft-*`、`pr-repair-batch`、legacy discussions、heavy reportがあってもCore validationを壊さず、旧Workflow評価を再開しない。
- Dependency cycle、invalid edge、重複Identity、既存Node treeとDependency storage formatの安全性を維持する。

## 後続IssueへのHandoff

Issue 359へ渡すもの:

- Retained CLI一覧
- `active set` / `issue start` / `issue finish`の意味
- Current Artifact 6種とgeneric import
- CLI help / Context Packの参照経路

Issue 360へ渡すもの:

- Runtime Removal Inventory
- Obsolete managed command / module / wrapper / test一覧
- Existing data preservation契約
- Generated state regeneration契約

## 未解決事項と注意

- Product Ownerへ追加で確認すべき高影響な意図上のGapはない。
- External intelligence smokeのRelease上の位置づけは主にIssue 359 / 360と親Epicの責務であり、Issue 357の仕様作成を妨げない。
- 親Epicには古いBaseline、`analysis`、`optional report.md`、Lifecycle未定義等が残るため、Fresh Review前に別途整合させる。
- Canonical文書は旧Assurance Composeを使わず、採用済みArtifactから完全ファイルとしてAuthoringする。
- Dependency-readyをImplementation-readyと表現しない。

## 推奨反映先

- `requirement.md`: 目的、In / Out、Lifecycle、Artifact、Report、Historical preservation、Acceptance Criteria。
- `design.md`: Runtime boundary、Current / Historical分離、CLI、Active / Context、Lifecycle failure、Scaffold、migration。
- `plan.md`: Removal Inventoryから回帰・Handoffまでの段階、テスト義務、完了条件。
- ADR: 現時点で新規ADR必須の論点なし。Canonical Designで十分に可逆・追跡可能。
