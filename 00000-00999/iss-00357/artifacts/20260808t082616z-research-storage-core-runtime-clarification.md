---
種別: research
ID: "20260808t082616z-research"
タイトル: "Storage Core Runtime Clarification Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-08-08"
親: ["iss-00357"]
関連:
  - "iss-00358"
  - "20260808t083300z-interview"
authority: "synthesized"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT clarification session: required-repository-connector-context-repository-57"
reflected_to: []
---

# 20260808t082616z-research Storage Core Runtime Clarification Research

## 位置づけ

- `iss-00357`のRequirement / Design / Plan作成前に、現行RuntimeとTargetのStorage Core境界を明らかにするsource-grounded evidenceである。
- Clarificationの主担当は、Epic方針を議論してきた元のChatGPTスレッドである。ローカルのrepo分析は、ChatGPTへ渡す検証材料と、回答の事実確認に用いた。
- 本ArtifactはCanonical specificationではない。Epic Requirement Reviewの`fail`、Design / Plan Review未実施、Issue Scaffold状態を解決済みとは扱わない。

## 調査目的

- Runtimeから削除する認知的Workflowと、Storage Coreとして保持する決定的機構を分ける。
- `iss-00358`と同時並行で作業しても同一ファイル・契約を二重所有しない境界を定める。
- 現行のAssurance / Profile / Artifact / Issue lifecycle結合を洗い出し、ユーザー判断が必要な点を特定する。

## sources / 調査方法

- 元のChatGPTスレッドへ、親Epic、Issue Scaffold、オンボーディングArtifact、現行Parser / Registry / Templates / Docsを添付し、`spec docs / grill with docs`相当のClarificationを依頼した。
- Provider正本を優先して以下を照合した。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `tests/cli_runtime/`および`tests/unit/`の関連テスト
- 親EpicのRequirement / Design / Plan / Reportと、Issue 357 / 358の`.meta.json`およびScaffoldを確認した。

## facts / 観測できた事実

### 現行Surface

- Parser / Registryには、Storage Core候補に加えて`assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`が現存する。
- `issue finish`はGitHub closeとactive clearだけでなく、lifecycle authority、promotion record、delegated artifact、Evidence Adoption Ledgerを評価する。
- `issue start`はactive Issue、branch、GitHub state、dependency readiness、checkoutを扱い、`--force`でもdependency blockは迂回しない契約である。
- `draft-design` / `draft-plan`は`.assurance.json`、`authorized_profile`、`templates/issue-profiles/<profile>/`へ結合している。
- 直接作成可能なArtifactとprofile routing専用の`draft-*`が同一Catalogに混在する。
- Issue 357 / 358には直接dependencyがなく、Epic Plan上も並行Laneだが、両IssueのCanonical文書は未具体化Scaffoldである。

### Storage Coreとして保持する候補

- Initiative / Epic / Issueのstable ID、親子階層、GitHub linkage。
- Canonical document、scope-local Artifact、Workbench / Worktree。
- `.meta.json.depends_on`、DAG validation、readiness projection。
- active scope、new / import / close / delete、sync / validate / doctor。
- Artifact path safety、timestamp collision、create lock、partial-write safety、rules symlink。
- `artifact import file`のようなprovider-neutralな汎用import。

### Runtimeから除去する候補

- Assurance、Grade / Profile classification、Authoring orchestration。
- Workflow guidance、promotion、delegated authoring、EAL gate。
- Product-owned ChatGPT runtimeとprovider固有import。
- Reviewer / PR readinessをRuntimeが判定する仕組み。

## ownership boundary / 並行作業境界

| Surface | Issue 357の所有 | Issue 358の所有 | 後続Issue |
|---|---|---|---|
| Parser / Registry / command implementation | 実装・削除 | 変更しない | - |
| `issue start` / `issue finish` | 機械的挙動 | 変更しない | Epic判断を受領 |
| Artifact typeの意味 | 実装しない | 定義 | I3がSkillへ接続 |
| Artifact path / naming / safety | 実装 | 契約を参照 | - |
| Canonical template本文 | 変更しない | 定義・編集 | I4が配布確認 |
| Template loader / node scaffold | 実装 | Target契約を提供 | I4がcutover |
| Installer managed inventory / prune | 変更しない | 変更しない | I4 |
| Managed Skill | 変更しない | Guide pathを提供 | I3 |

- 基本契約は「Issue 358が何を現行Surfaceとして存在させるかを定義し、Issue 357がそれを安全に生成・操作する仕組みを実装する」である。
- `create_artifact_doc.py`、`application/contracts.py`、`application/create_node.py`、`tests/cli_runtime/test_new.py`は共有結合点である。並行実装時は意味論をIssue 358、機械実装をIssue 357へ分ける。

## inference / 推測

- CLI項目をRegistryから消すだけではRuntime縮退にならず、Bootstrap、Application、Domain、Infra、Testsの依存除去まで必要になる。
- Profileを残したままAssuranceを削除すると、profile選択の新しいauthority、設定、metadata、commandのいずれかが必要になり、除去対象のPolicy stateを別名で再導入する。
- Historical `.assurance.json`や旧Artifactが存在してもCoreのvalidate / active / lifecycleを妨げないread compatibilityが必要である。

## unverified / 未検証事項

- Runtimeの全module・fixture・bootstrap dependencyを完全列挙したRemoval Inventoryは未作成である。Issue planningで機械的inventoryを作る必要がある。
- `issue start` / `issue finish`のTarget semanticsはChatGPTから推奨案が示されたが、ユーザー承認前である。
- `artifact import chatgpt-output`、`pr-repair-batch`、`draft-*`の新規Surfaceからの除去は未承認である。
- External smokeをCore完了条件から外しReference environmentのrelease evidenceにする提案は、Epic Canonicalへ未反映である。

## question candidates / 質問候補

- 最初の質問は、Issue 358配下の`20260808t083300z-interview`へ切り出した。
  - Profile別template、`.assurance.json`、`authorized_profile`、`draft-*` routingを新規Surfaceから完全に外すか。
- 後続候補:
  - `issue start` / `issue finish`を旧review / EALを評価しないthin lifecycle primitiveとして残すか。
  - `artifact import chatgpt-output`を削除し、`artifact import file`だけを残すか。
- 親Epicへrouteすべき候補:
  - External integration smokeをCore CI gateではなくreference release evidenceとするか。

## terminology conflicts / 用語衝突

- `ready`はdependency projection上の状態であり、planning completion / implementation-readyではない。
- `issue finish`は現行ではWorkflow gateを含むが、Targetではthin lifecycle primitiveを意味する候補である。
- `Artifact type`には直接作成型とprofile routing専用型が混在しており、Target Catalogでは区別が必要である。
- `Historical compatibility`は旧Workflowを動作保証することではなく、既存文書・Artifactを破壊せず読めることを意味する。

## edge cases / 具体シナリオ

- 壊れた、または古い`.assurance.json`が存在しても、Targetのvalidate / active / start / finishが旧Workflow評価を再開しない。
- GitHub close成功後にactive clearが失敗した場合、partial successを診断し再実行可能にする。
- GitHub close失敗時はactiveを保持する。
- 廃止したcommandはhelp / parser / registryから消え、fallbackせず明確なinvalid commandになる。
- Historical `draft-*` / `pr-repair-batch`は保持するが、新規作成を許可しない選択ができる。
- `templates/issue-profiles/`がなくてもCoreが起動し、通常Artifactを作成できる。
- Provider templateとdogfood projectionの不一致を回帰テストで検出する。

## implications / 判断への含意

- Requirementでは、保持するstructural invariants、除去するWorkflow semantics、historical read compatibilityを受け入れ条件として分離する必要がある。
- Designでは、Runtime mechanismとAuthoring semanticsのポートを固定し、Profile / Assurance storeをretained Coreへ持ち込まない。
- Planでは、Parser / Registry削除より前にdependency inventoryを作り、retained commandから旧gateを外した後にremoved moduleを削除する。
- Issue 357完了時に、I4へ渡すRuntime Removal Inventoryを必須成果物にする。

## リスク/制約

- Epic Requirement Reviewは`fail`のままであり、本Artifactだけで未解決Findingは解消しない。
- Existing node / document / artifactを一括書換えしない。
- Installer、managed Skill、top-level migrationはIssue 357へ広げない。

## 反映先

- ユーザー回答後、Issue 357のRequirement / Design / Plan候補へ反映する。
- Cross-IssueのStorage–Authoring Surface Contractは、必要ならEpic-local `disc`として一度だけ固定する。
