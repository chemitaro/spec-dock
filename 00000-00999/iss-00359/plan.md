---
種別: 実装計画書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-12"
依存: ["requirement.md", "design.md"]
親: ["epic-00356", "init-local-00003"]
---
# iss-00359 Replace Managed Workflow Skills with SpecDock Skills — 実装計画

## 1. 実装基準

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
* Baseline commit: `8e10f255b3377bf879b459380f563729522e22b2`
* Dependency: `iss-00357`、`iss-00358`

実装中にCurrent CLI、Artifact template、provider path、dogfood path、installer mappingが本計画と異なると判明した場合、存在しないpathやcommandを補わず、R/D/Pへ戻る。

## 2. 対象ファイル

### 2.1 新規作成

| File                                                                                  | 内容                                              |
| ------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`                 | provider authorityとなる`spec-dock` contract       |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md` | provider authorityとなるgrill integration contract |
| `.agents/skills/spec-dock/SKILL.md`                                                   | `spec-dock`のdogfood projection                  |
| `.agents/skills/spec-dock-grill-with-docs/SKILL.md`                                   | grillのdogfood projection                        |

### 2.2 変更

| File                                                   | 変更                                                                                            |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/docs/README.md`        | 二つのskillとCurrent docsへの短いpointerを追加                                                           |
| `spec-dock/docs/README.md`                             | provider docsのbyte-identical projection                                                       |
| `src/spec_dock/assets/install_root/.codex/config.toml` | `developer_instructions`から旧SpecDock workflow固有責務だけを削除                                         |
| `.codex/config.toml`                                   | provider configのbyte-identical projection                                                     |
| `tests/unit/infra/test_init_update.py`                 | skill / docs / configのstatic contract、provider / dogfood parity、additive materialization test |
| `tests/cli_runtime/test_new.py`                        | 四routeの基本positive testとCLI-nativeな主要negative test                                             |

### 2.3 確認のみ・変更禁止

| File / Surface                                            | 用途                                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------------ |
| `src/spec_dock/cli.py`                                    | Current install-root mappingとmanaged / legacy managed inventoryの確認 |
| `_MANAGED_SKILL_NAMES`                                    | Issue #360へ渡す既存inventory。変更しない                                     |
| `_LEGACY_MANAGED_SKILL_NAMES`                             | Issue #360へ渡す既存inventory。変更しない                                     |
| installer init / update / uninstall logic                 | Current additive materializationの機構。変更しない                          |
| obsolete exact path inventory                             | Issue #360のprune入力。変更しない                                           |
| `tests/cli_runtime/test_storage_core_cli.py`              | Current CLI command surfaceの回帰確認                                   |
| `tests/unit/infra/test_artifact_templates.py`             | Current Artifact route / template / provider-dogfood parityの回帰確認   |
| `src/spec_dock/assets/spec_dock/templates/artifacts/*.md` | 四routeのCurrent template確認                                          |
| Runtime、parser、registry                                   | Issue #359では変更しない                                                  |

新しいreference file、host-specific metadata file、handoff manifestは追加しない。

## 3. 実装順序

### S00 — Current contract再確認

1. baseline SHAを確認する。
2. provider / dogfoodのskill、docs、config pathを確認する。
3. Current CLI root / leaf helpを確認する。
4. bare `doctor`と、`--github-repo`、`--github-pr`、`--github-head-sha`、`--github-extended`の実在を確認する。
5. 四routeのCurrent templateを確認する。
6. `src/spec_dock/cli.py`のmanaged / legacy managed inventoryを記録する。
7. `install_root`全通常fileがcurrent mappingへ含まれ、mappingがinit / update copyとuninstall inventoryに使用されることを確認する。
8. 対象外fileにbaseline外のdriftがある場合は停止する。

### S10 — Static contract testをREDにする

`tests/unit/infra/test_init_update.py`へ、次を確認する最小testを追加する。

* provider skill二件が存在する
* dogfood skill二件が存在する
* skill pairがそれぞれbyte-identicalである
* `spec-dock`にscope、docs pointer、CLI分類、旧workflow禁止境界がある
* bare `doctor`だけがexecute-read-onlyである
* external診断が次の実在optionを使うpresent-only invocationである

  * `--github-repo`
  * `--github-pr`
  * `--github-head-sha`
  * optional `--github-extended`
* `doctor --github`という存在しない形式がない
* grillにexplicit invocation、四route、external dependency、preflight、zero-write、exactly-one、partial recoveryがある
* grillが`--initiative`、`--epic`、`--issue`のいずれか一つの明示selectorを要求する
* grillにactive fallbackがない
* 新skillに旧skill fallback、upstream `grill-with-docs`、`analysis`、provider固有importがない
* docs pairがbyte-identicalで、対象pointerが存在する
* config pairがbyte-identicalでvalid TOMLである
* configから旧SpecDock workflow固有markerが消えている
* configに一般的な調査、委任、検証、直接編集境界と既存TOML tableが残っている
* Current install-root mappingが二つの新provider `SKILL.md`を含む
* `_MANAGED_SKILL_NAMES`と`_LEGACY_MANAGED_SKILL_NAMES`がbaseline inventoryから変わっていない
* obsolete inventoryとinstaller logicを変更せずmaterializationできる

### S20 — Provider `spec-dock`

provider `SKILL.md`へ次を実装する。

* explicit target優先、active target fallback
* parent、canonical docs、Report、Artifact、dependency、worktree、docsの読取り順
* Current CLI helpをauthorityとする規則
* execute-read-only / present-only / forbidden分類
* bare `doctor`とexternal GitHub diagnostic invocationの区別
* mutating commandを自動実行しない規則
* removed workflow、旧skill、provider固有routeへのfallback禁止

CLI syntaxやAuthoring Kit本文をskillへ複製しない。

### S30 — Provider `spec-dock-grill-with-docs`

provider `SKILL.md`へ次を実装する。

* 明示呼出しだけを受け付ける
* `--initiative`、`--epic`、`--issue`のいずれか一つだけを必須にする
* active targetへfallbackしない
* unique target、purpose、route、title、sourceの必須化
* `grilling`と`domain-modeling`のoperator-owned external dependency
* upstream `grill-with-docs`を使用しない
* external capabilityをread-onlyで使用する
* bootstrap preflight
* external responseを未信頼データとして扱う
* write前に本文を確定する
* Current CLIによる一回のArtifact作成
* exactly-one postcondition
* zero-write failure
* partial Artifactでの停止とoperator recovery
* canonical R/D/P、Report、ADR、CONTEXTを変更しない

### S40 — Codex configとdocs pointer

1. provider configの`developer_instructions`から、`design.md`で特定した旧SpecDock workflow固有条項だけを削除する。
2. TOMLの他のkey、table、一般責務を保持する。
3. provider docsへ二つのskill、Authoring Kit、Artifact guide、CLI helpのpointerを追加する。
4. installerのTarget inventoryがcutover済みとは記述しない。

### S50 — Dogfood projection

providerから次をdogfoodへ同一内容で反映する。

* 二つの`SKILL.md`
* docs `README.md`
* `.codex/config.toml`

手作業で意味の異なるdogfood専用文面を追加しない。

### S55 — Additive materialization確認

Current installer logicを変更せず、focused unit testで次だけを確認する。

* 二つの新provider `SKILL.md`が`_build_current_managed_file_mappings()`のcurrent mappingに含まれる
* target relative pathが対応するrepo-local skill pathである
* `_MANAGED_SKILL_NAMES`を変更していない
* `_LEGACY_MANAGED_SKILL_NAMES`を変更していない
* obsolete exact path inventoryを変更していない
* 旧skillをpruneしていない

次は実施しない。

* fresh init consumer matrix
* existing update consumer matrix
* uninstall consumer matrix
* installed consumer parity
* Target inventory cutover
* publicationまたはmigration検証

これらはIssue #360へ渡す。

### S60 — CLI behavior test

`tests/cli_runtime/test_new.py`で、bootstrap済みのIssue scopeに対し、次の四routeをparameterizeして実行する。

* `research`
* `interview`
* `disc`
* `decision-candidate`

各caseで次を確認する。

* `--issue`による明示selectorを受理する
* explicit titleを受理する
* routeに対応するCurrent templateでfileが作られる
* 作成されたfileが対象scopeの`artifacts/`直下にある
* 新規Artifactが一件だけである
* 既存Artifact、canonical文書、metadata、active、dependencyに差分がない

主要negativeは次に限定する。

* selectorなし
* 複数selector
* unsupportedな`analysis`またはunknown route
* 空title
* invalid scope selectorまたはscope mismatch
* unsafe destinationまたはsymlink escape
* invalid explicit slug
* existing collision
* `create.lock`による拒否

CLIがfile publish前に拒否するcaseでは、対象SpecDock treeの永続snapshotが不変であることを確認する。

hostがMarkdown skillを実行することを前提とする次の挙動は、static contract testで固定する。

* implicit invocation拒否
* active target fallback拒否
* external dependency不足時のzero-write
* external response内のwrite instruction拒否
* partial Artifactの自動修復禁止
* 二回目のArtifact作成禁止

### S70 — Handoff確定

1. legacy inventoryを本計画の一覧と再照合する。
2. Issue #359のdiffに`src/spec_dock/cli.py`、installer logic、inventory定数、obsolete inventory、旧skill削除が含まれないことを確認する。
3. additive materializationの結果と、Target inventory cutover未実施を分けて記録する。
4. IC-2向け最小入力を整理する。
5. Issue #359自身はIC-2 passを宣言しない。

### S90 — Docs impact確認

1. provider / dogfoodのCurrent docs entrypointが二つのskillとCurrent docs pathを案内することを確認する。
2. Issue #360のmigration、distribution、publication説明をIssue #359のdocsへ追加しない。

### S99 — 最終品質ゲート

1. 実装とfocused verificationを完了してから、Issue全体のQA、code、spec reviewを一回の最終gateとして実施する。stepごとのreviewは行わない。
2. 固定baseline以降のtracked差分とuntracked成果物を対象に、仕様適合、既存規約、安全境界、test十分性を確認する。
3. Issue #359のscope内にあるP0 / P1だけをblockerとする。P2 / P3をR/D/P、Report、companion、実装、testへ統合しない。
4. P0 / P1を修正した場合は、影響testと最終gateを再実行する。
5. 三reviewのpassと最終検証結果を`report.md`へ記録した後にだけ完了とする。

## 4. Legacy skill inventory

次はbaseline commitの`_MANAGED_SKILL_NAMES`に存在する。Issue #359では変更せず、Issue #360の再確認対象として渡す。

1. `spec-dock-hub`
2. `spec-dock-initiative-planning`
3. `spec-dock-epic-planning`
4. `spec-dock-epic-execution`
5. `spec-dock-issue-planning`
6. `spec-dock-issue-execution`
7. `spec-dock-chatgpt-authoring`
8. `spec-dock-initiative-planning-manual`
9. `spec-dock-epic-planning-manual`
10. `spec-dock-issue-planning-manual`
11. `spec-dock-clarification`
12. `spec-dock-adr-facilitation`
13. `spec-dock-codex-adapter`
14. `spec-dock-copilot-adapter`
15. `git-commit-conventional-ja`
16. `github-pr-observation`
17. `github-pr-creator`
18. `github-pr-merge-preparer`

次はbaseline commitの`_LEGACY_MANAGED_SKILL_NAMES`に存在する。

1. `spec-driven-tdd-workflow`
2. `spec-dock-system-architect`
3. `spec-dock-implementation-planner`

Issue #360はexact implementation commitで所有権と実在pathを再確認し、Target inventory、prune / preserve、migrationを決定する。Issue #359はこの一覧だけを根拠に削除しない。

## 5. 必要最小限のtest

### 5.1 Targeted test

```text
uv run pytest tests/unit/infra/test_init_update.py -q
uv run pytest tests/cli_runtime/test_new.py -q
```

### 5.2 Consumed contract regression

```text
uv run pytest tests/cli_runtime/test_storage_core_cli.py -q
uv run pytest tests/unit/infra/test_artifact_templates.py -q
```

本Issueではfull regression、consumer matrix、durable CI artifact、retention、長期証跡を完了条件にしない。

## 6. IC-2入力

Issue #359 ownerが提供する入力は次とする。

* 二つのskill名と四つのentry path
* provider / dogfood pairのparity結果
* Current install-root mappingによるadditive materialization結果
* managed / legacy managed inventory定数が未変更であること
* `spec-dock`のinput / output / no-go contract
* bare `doctor`とexternal diagnostic invocationの分類
* grillの明示selector、明示呼出し、external dependency、四route、write boundary
* missing dependencyと主要failureの挙動
* docs pointer
* Codex config cleanup結果
* targeted test結果
* Issue #360向けlegacy inventory
* Target inventory cutover、prune、consumer migrationが未実施であること

Epic main orchestratorはこれらを親Epic契約と照合する。Issue #359 ownerはIC-2のpass / failを単独で決めない。

## 7. 完了条件

* 対象ファイルだけが変更されている
* provider skill二件とdogfood skill二件が存在する
* 各skill pairがbyte-identicalである
* docs pairがbyte-identicalである
* config pairがbyte-identicalかつvalid TOMLである
* configから旧SpecDock workflow固有責務だけが削除されている
* `spec-dock`のCLI分類と禁止境界が固定されている
* bare `doctor`だけがexecute-read-onlyである
* external doctor診断が実在optionを使うpresent-only invocationとして固定されている
* grillが一つの明示selectorを要求し、active fallbackを持たない
* grillのexplicit route / title、preflight、zero-write、exactly-one、partial recoveryが固定されている
* 四routeの基本positive testが成功する
* 主要negative testがno-writeを確認する
* 新skillが旧skill、upstream `grill-with-docs`、`analysis`、provider固有importへfallbackしない
* 二つのprovider skillがCurrent install-root mappingから認識される
* `src/spec_dock/cli.py`、managed / legacy managed skill定数、obsolete inventory、installer logicを変更していない
* 旧managed skillをpruneしていない
* fresh / update / uninstall consumer matrixとTarget inventory cutoverを実施していない
* Issue #360向けlegacy inventoryとIC-2最小入力が揃っている
