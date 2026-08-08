---
種別: research
ID: "20260808t082616z-research"
タイトル: "Authoring Kit Clarification Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-08-08"
親: ["iss-00358"]
関連:
  - "iss-00357"
  - "20260808t083300z-interview"
authority: "synthesized"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT clarification session: required-repository-connector-context-repository-57"
reflected_to: []
---

# 20260808t082616z-research Authoring Kit Clarification Research

## 位置づけ

- `iss-00358`のRequirement / Design / Plan作成前に、現行Template / Guide / Artifact contractとTarget Authoring Kitを比較するevidenceである。
- 元のChatGPTスレッドがClarificationの主担当として分析・質問選定を行い、ローカルrepo分析でsource-groundingを補強した。
- 本Artifactは非正本であり、既存のReviewer FindingやIssue Scaffold状態を解決しない。

## 調査目的

- Requirement / Design / Plan / Report / ArtifactのTarget semanticsを明確にする。
- Templateに残す最小scaffold、Guideへ移す説明、Current distributionから除くWorkflow policyを分類する。
- Issue 357と衝突しないよう、Authoring semanticsとRuntime mechanismの所有境界を固定する。

## sources / 調査方法

- 元のChatGPTスレッドへIssue 357 / 358のScaffold、親Epic、現行Parser / Registry、Templates README、Docs README、オンボーディングArtifactを渡した。
- Provider正本を優先して以下を調査した。
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/`
  - `src/spec_dock/assets/spec_dock/templates/artifacts/`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/`
  - `src/spec_dock/assets/spec_dock/docs/workflow_*.md`と`phase_*.md`
  - `tests/unit/infra/test_init_update.py`、`test_artifact_templates.py`、関連Runtime tests

## facts / 観測できた事実

### Targetで残す文書契約

- `requirement.md`: 何を、なぜ、どの条件で達成するか。
- `design.md`: どの責務境界・構造・契約で実現するか。
- `plan.md`: どの順序・検証・完了条件で実装するか。
- `report.md`: 必要な場合の簡潔な観測・結果記録とする候補。
- `artifacts/`: 調査、対話、代替案、review、外部出力のEvidence surfaceであり、Canonical documentではない。

### 現行Template / Docsの状態

- Issue Requirement、Design、Plan、Reportとprofile別Templateには、Grade、Reviewer Gate、EAL、promotion、delegated authoring、fallback、PR readinessが深く埋め込まれている。
- `templates/issue/design.md`と`plan.md`は`awaiting-assurance-compose`を前提とする。
- `docs/README.md`、`workflow_*.md`、`phase_*.md`は多数のPlanning / Execution Skill、ChatGPT Authoring、fresh Reviewer GateをCurrent routeとして案内する。
- `templates/issue-profiles/`は`.assurance.json.authorized_profile`とRuntimeで結合している。
- Provider assetとdogfood projectionのbyte-parityを検査する既存テストがある。

### TargetのTemplate-to-Guide分離

- Templateに残す候補:
  - 見出し、記述目的、Scope / Out of Scope、Acceptance Criteria、Edge Cases、Constraints、Open Questions。
- Guideへ移す候補:
  - 良い例・悪い例、Scope差、optional section、図表選択、testing / rollback、典型的欠落、具体例。
- Current distributionから除く候補:
  - Grade、Reviewer Gate、Phase Promotion、EAL、Specialist / Delegated Evidence、Manual Fallback、PR readiness、Product-owned ChatGPT workflow。

### Artifact semantics

- Target current catalog候補は`blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr`である。
- `pr-repair-batch`、`draft-requirement`、`draft-design`、`draft-plan`、`scratch`、`note`はhistorical-only候補である。
- Scope-local placement、timestamp naming、same-second collision、`rules.md` navigation、Workbenchとの区別、Historical preservationは残す契約である。

## ownership boundary / 並行作業境界

| Surface | Issue 358 | Issue 357 | 後続Issue |
|---|---|---|---|
| Canonical document semantics | 所有 | 実装契約を参照 | I3がSkillから案内 |
| Template / Guide本文 | 所有 | 変更しない | I4が配布確認 |
| Artifact catalogの意味 | 所有 | 生成・検証を実装 | I3が利用 |
| Artifact filename / path safety | 契約を参照 | 所有 | - |
| `report.md`の意味 | 所有 | 必要ならscaffold実装 | I4がmigration確認 |
| Parser / Registry / lifecycle | 変更しない | 所有 | - |
| Installer prune | inventory候補を渡す | inventory候補を渡す | I4 |

- Template pathまたはArtifact typeを変更するとき、Issue 358はTarget contractを提示し、Runtime codeを直接変更しない。
- `docs/authoring/`、`docs/README.md`、`guide.md`、`templates/`はIssue 358の主要編集面である。

## inference / 推測

- `report.md`ファイルを新規Nodeにも常設しつつ内容を任意のlightweight result logにすると、既存pathとscaffolder契約を保ちながら旧Workflow state machineだけを除去できる。
- Profile別Templateを残すと、選択authorityを別途導入する必要があり、Authoring policyをStorage Coreへ再結合する。
- Detailed CLI syntaxをDocsへ複製せず`--help`へ案内すると、RuntimeとGuideのdriftを減らせる。

## unverified / 未検証事項

- Provider docs / templatesの全ファイルを`keep / simplify / replace / current distributionからdelete / historical-only / I3 handoff / I4 handoff`へ分類した完全inventoryは未作成である。
- `report.md`を常設する提案は未承認である。
- Guideを既存pathの内容置換で更新するか、新しい`docs/authoring/`構成へ集約するかは未決である。
- Artifactの重要な採用判断をCanonical本文だけに反映するか、軽量Reportにも任意記録するかは未決である。

## question candidates / 質問候補

- 最初の一問を`20260808t083300z-interview`へ切り出した。
  - IssueのDesign / Planを各一種類のmodel-neutral templateへ統一し、Profile / Assurance / `draft-*` routingを新規Surfaceから完全に外すか。
- 回答後の候補:
  - `report.md`は常に生成するlightweight optional-content fileとして残すか、ファイル自体を任意生成にするか。
  - Authoring GuideのCurrent navigation pathをどこへ固定するか。
  - `pr-repair-batch`をhistorical-onlyにするか。

## terminology conflicts / 用語衝突

- `optional report`が「ファイルは常設で内容が任意」なのか「ファイル自体も任意」なのか未確定である。
- `Template`には現行では説明・policy・workflow stateが混在するが、Targetでは最小scaffoldを指す。
- `Artifact adoption`は旧EAL必須経路を意味せず、Canonical docsへの明示的reflectionを意味する方向で再定義が必要である。
- `Current docs`と`Historical docs`を区別し、過去Evidenceの保存と現行navigationからの撤去を混同しない。

## edge cases / 具体シナリオ

- Fresh Initiative / Epic / Issueが、profileなしの単一Template一式から生成できる。
- 新TemplateにGrade / Reviewer / EAL / Promotion / provider固有語彙が残らない。
- Existing canonical documents、Historical Report、Artifact、Discussion、ADRをrewrite / rename / moveしない。
- Historical Issue Profile文書が存在してもvalidationを壊さない。
- Templateは短く、同一policyを複数Docsへ複製しない。
- Broken navigation link、provider / dogfood不一致、旧Workflow docsへのCurrent導線をテストする。
- Reportの内容や有無をimplementation readiness authorityにしない。

## implications / 判断への含意

- RequirementはDocument / Artifactごとの責務、除去するpolicy cache、historical preservation、provider neutralityを明文化する必要がある。
- DesignはTemplate-to-Guide split、scope layering、Current / Historical navigation、Issue 357とのmachine contractを定める。
- Planはcomplete inventory、single-template化、Guide再構成、dogfood同期、link / vocabulary / parityテストの順で構成する。
- Issue 358完了時に、I3へGuide / rules pathを、I4へremoved Docs / Templates inventoryを渡す。

## リスク/制約

- Parser / Registry、`issue start` / `issue finish`、Node metadata、dependency algorithmをIssue 358で変更しない。
- Managed Skill実装とobsolete assetの実Pruneへ範囲を広げない。
- Epic Reviewer FindingはCanonical修正とfresh reviewまで未解決である。

## 反映先

- ユーザー回答後、Issue 358のRequirement / Design / Plan候補へ反映する。
- Cross-Issueの固定契約が必要ならEpic-local `disc`へ集約し、両Issueから参照する。
