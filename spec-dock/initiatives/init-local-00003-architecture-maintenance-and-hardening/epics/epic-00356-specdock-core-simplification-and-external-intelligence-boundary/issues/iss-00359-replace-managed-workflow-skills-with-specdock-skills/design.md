---
種別: 設計書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-12"
依存: ["requirement.md"]
親: ["epic-00356", "init-local-00003"]
---
# iss-00359 Replace Managed Workflow Skills with SpecDock Skills — 設計

## 1. 設計方針

本設計のscopeと受け入れ条件の正本は`requirement.md`とする。

確認基準は次のexact sourceである。

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
* Commit: `8e10f255b3377bf879b459380f563729522e22b2`

二つのskillはMarkdownによる薄いclient contractとする。新しいRuntime、generic runner、workflow state、authority metadata、provider adapterは追加しない。

## 2. Provider / dogfood構造

### 2.1 Skill asset

| Provider authority                                                                    | Dogfood projection                                  |
| ------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`                 | `.agents/skills/spec-dock/SKILL.md`                 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md` | `.agents/skills/spec-dock-grill-with-docs/SKILL.md` |

`spec-dock`のFront Matterは、既存skill discoveryに必要な`name`と`description`に限定する。`spec-dock-grill-with-docs`は明示呼出し限定を実現するCurrent skill metadataとして、これらに`disable-model-invocation: true`を加える。未確認のhost固有metadataや`agents/openai.yaml`は追加しない。

### 2.2 Docs

| Provider authority                              | Dogfood projection         |
| ----------------------------------------------- | -------------------------- |
| `src/spec_dock/assets/spec_dock/docs/README.md` | `spec-dock/docs/README.md` |

Current docs entrypointは、次をcontext pointerとして示す。

* `spec-dock/docs/authoring/overview.md`
* `spec-dock/docs/authoring/artifacts.md`
* `./spec-dock/scripts/spec-dock --help`
* 対象commandのleaf help
* `.agents/skills/spec-dock/SKILL.md`
* `.agents/skills/spec-dock-grill-with-docs/SKILL.md`

### 2.3 Codex config

| Provider authority                                     | Dogfood projection   |
| ------------------------------------------------------ | -------------------- |
| `src/spec_dock/assets/install_root/.codex/config.toml` | `.codex/config.toml` |

変更後の各provider / dogfood pairはbyte-identicalとする。

### 2.4 Additive materialization境界

Current installerは次の順序で`install_root`を扱う。

1. `_iter_install_root_files()`が`install_root`配下の全通常fileを再帰的に列挙する。
2. `_build_current_managed_file_mappings()`が各fileを同じrelative targetへ対応付ける。
3. `_apply_managed_skill_install_plan()`がcurrent mappingを対象repositoryへcopyする。
4. uninstall inventoryも同じcurrent mappingを参照する。

したがって、二つのprovider `SKILL.md`を`install_root`へ追加すると、既存の汎用managed-file mappingを通じてcurrent init / update copyとuninstall inventoryから認識される。

Issue #359では、この機械的帰結をadditive skill asset materializationとして受け入れる。二つのskill contractとprovider assetを所有するという親Epicの境界に含まれる。

Issue #359は次を変更しない。

* `_MANAGED_SKILL_NAMES`
* `_LEGACY_MANAGED_SKILL_NAMES`
* `_iter_install_root_files()`
* `_build_current_managed_file_mappings()`
* `_build_managed_skill_install_plan()`
* `_apply_managed_skill_install_plan()`
* obsolete exact path inventory
* installerのinit / update / uninstall logic

Current mappingに二つのfileが追加されることと、Target managed inventoryを二つへcutoverすることは別である。

Issue #360が次を所有する。

* Target managed inventory
* 旧assetのprune
* fresh / update / uninstall migration
* installed consumer matrix
* publicationとcutover

## 3. `spec-dock` contract

### 3.1 責務

`spec-dock`は、明示targetを優先し、明示targetがない場合だけactive scopeを読む。

一意なscopeを解決した後、必要な範囲で次を読む。

1. scope identityとparent chain
2. canonical R/D/P
3. `report.md`
4. scope-local Artifact
5. `.meta.json.depends_on`
6. worktree state
7. Authoring Kit docs
8. Current CLI help

返す内容は、観測したscope、関連path、dependency、利用可能なCurrent commandとその副作用分類である。

### 3.2 非責務

`spec-dock`は次を行わない。

* Planning / Review / Execution workflowの開始または状態判定
* implementation-ready、review pass、completionの判定
* 旧SpecDock skillへの委任またはfallback
* model、provider、browser、Oracleの選択
* canonical文書の自動作成または自動変更
* raw metadata、active file、dependency fileの直接編集
* GitまたはGitHub mutation
* mutating CLI operationの自動実行

構造変更が必要な場合は、Current leaf helpから確認したcommandと副作用をoperatorへ提示する。

## 4. Current CLI operationの分類

分類の正本は次の表とする。skill本文へcommand仕様全文を複製せず、実行時にはCurrent local helpを確認する。

### 4.1 Execute-read-only

skillが実行できる操作である。

| Operation                | 条件                                 |
| ------------------------ | ---------------------------------- |
| root / leaf `--help`     | help表示だけ                           |
| `active show`            | active stateの読取りだけ                 |
| `deps check --no-github` | local dependencyの読取りだけ             |
| `worktree list`          | worktree一覧の読取りだけ                   |
| `worktree show`          | worktree情報の読取りだけ                   |
| `validate`               | local validationだけ                 |
| bare `doctor`            | GitHub target optionを付けないlocal診断だけ |

存在しない`doctor --github`という形式を使用しない。

### 4.2 Present-only

skillはCurrent helpから正確なcommandと副作用を示すが、自身では実行しない。

* `new initiative`
* `new epic`
* `new issue`
* `import initiative`
* `import epic`
* `import issue`
* `active set`
* `active clear`
* `deps add`
* `deps remove`
* GitHub参照を伴う`deps check`
* `issue start`
* `sync`
* `artifact import file`
* `worktree create`
* `worktree remove`
* `workbench copy`
* `new artifact`
* 次のexternal GitHub capability diagnostic invocation

```text
./spec-dock/scripts/spec-dock doctor \
  --github-repo <owner/repo> \
  --github-pr <pull-request-number> \
  --github-head-sha <head-sha> \
  [--github-extended]
```

`new artifact`は、`spec-dock-grill-with-docs`が本設計のpreflightを満たした一回に限って実行できる。

### 4.3 Forbidden-from-skill

skillから実行しない。

* `close`
* `delete`
* `issue finish`
* `update`
* `uninstall`
* Git commit、checkout、pushその他のGit mutation
* GitHub Issue、PR、dependencyその他のGitHub mutation
* raw `.meta.json`、active state、dependency sourceの直接変更
* canonical R/D/P、Report、ADRの自動変更
* removed commandまたは旧skillへのfallback

Current CLIの実際の副作用がこの分類と異なる場合、skill本文で例外を即興追加せず、Issue #359のR/D/Pを修正する。

## 5. `spec-dock-grill-with-docs` contract

### 5.1 外部依存

このskillは、operator-ownedな次の二つを直接必要とする。

* `grilling`
* `domain-modeling`

両者は質問、論点整理、用語・境界・判断候補の整理に使用する。repositoryへの書込みは許可しない。

upstream `grill-with-docs`は使用しない。

### 5.2 入力

Artifact作成前に次を確定する。

* `--initiative`、`--epic`、`--issue`のいずれか一つだけの明示selector
* selectorに対応する一意なtarget
* purposeまたはquestion
* 一つのroute
* 非空のexplicit title
* 読取りを許可されたlocal source set
* `grilling`と`domain-modeling`の利用可能性
* 両external capabilityがread-only条件を守れること

このskillはactive stateをtarget selectorとして使用しない。selectorがない場合、または複数selectorがある場合はwrite前に停止する。

titleは一つのCLI argumentとして渡し、shell codeへ連結しない。

slugはCurrent CLIのoptional inputのままとする。titleから安全なslugを得られない場合、CLI呼出し前に停止し、operatorが明示slugを指定した新しい呼出しを必要とする。skill独自のslug / filename規則は作らない。

### 5.3 Route

| Route                | Artifact本文の中心section                               | Authority |
| -------------------- | -------------------------------------------------- | --------- |
| `research`           | Question、Source、Findings、Reflection                | evidence  |
| `interview`          | Question、Answer、Reflection                         | evidence  |
| `disc`               | Inputs、Synthesis、Options and trade-offs、Reflection | evidence  |
| `decision-candidate` | Context、Options、Candidate、Reflection               | draft     |

本文はCurrent templateを使用する。外部応答を命令として実行せず、観測事実、operatorから得た判断、候補、未解決事項を区別して記録する。

### 5.4 処理順序

1. 明示selectorを含む入力を確定する。
2. bootstrap preflightを行う。
3. 許可されたlocal sourceだけを読む。
4. `grilling`と`domain-modeling`をread-onlyで使用する。
5. 外部応答を未信頼データとして検査する。
6. Artifact本文をmemory上で確定する。
7. write直前に明示selectorとbootstrapを再確認する。
8. 対象scopeの`artifacts/`をsnapshotする。
9. 次のCurrent CLIを一回だけ実行する。

```text
./spec-dock/scripts/spec-dock new artifact <route> \
  --<initiative|epic|issue> <scope-id> \
  --title <title> \
  [--slug <slug>]
```

10. CLIが返したexact pathだけへ、確定済み本文を反映する。
11. exactly-one postconditionを確認する。
12. exact pathとrouteをoperatorへ返す。

## 6. Write boundary

### 6.1 Bootstrap preflight

preflightはread-onlyで行う。

* selectorが一つだけ存在する
* targetが一意に存在する
* target kindとselectorが一致する
* target pathが`spec-dock/initiatives/`配下の正規pathである
* target path、`artifacts/`、template、rules sourceにsymlink escapeがない
* route templateが通常fileかつ非空である
* `artifacts/`が既存の通常directoryである
* `artifacts/rules.md`が対象kind用rulesへの有効なsymlinkである
* rules sourceが既存の通常fileである

preflightはactive stateからtargetを補完せず、directory、file、symlink、lockを作成・補修しない。

collision、CLI lock、no-replace publish、最終的なpath safetyの判定はCurrent Artifact CLIをauthorityとする。

### 6.2 Zero-write

次の状態遷移では永続差分を残さない。

```text
input / selector / preflight / external check failure
  -> Artifact CLIを呼ばず停止

Artifact CLIがpublish前に拒否
  -> Current CLIのrollback結果を確認して停止
```

外部能力はArtifact作成前に使用し、repository writeを許可しない。

### 6.3 Exactly-one

成功後の`artifacts/` snapshot差分は、CLIが返した新規Markdown file一件だけでなければならない。

次のいずれかが検出された場合、成功と報告しない。

* 新規fileがゼロ件または複数件
* 返却path以外の新規entry
* 既存entryの変更または削除
* scope外の永続差分
* canonical文書、metadata、active、dependency、config、projectionの変更

### 6.4 Partial Artifact

Artifact publish後に本文反映またはpostcondition確認が失敗した場合、次の状態とする。

```text
partial Artifact
  -> 自動削除しない
  -> renameしない
  -> 上書きによる修復をしない
  -> retryしない
  -> 第二Artifactを作らない
  -> exact path / route / title / failure phaseを報告して停止
```

operatorが回収を完了するまで、同じ実行を継続しない。

## 7. `developer_instructions`変更境界

`developer_instructions`から削除するのは、旧SpecDock workflow固有の次の意味を持つ条項だけとする。

* SpecDock command操作を`spec-manager`へ原則委任する
* SpecDock workflow依頼をnamed sub-agent / reviewer利用の包括的許可とみなす
* active repo / worktree / SpecDock scopeを根拠にrole別・phase別の許可確認を不要とする
* 上記の英語・日本語重複

次を保持する。

* main agentの人間インターフェース責務
* requirement / design / planの整理
* 一般的なsub-agent routing
* bounded task、委任入力、成果統合
* 調査、事実・推定・未解決の分離
* 最小変更、安全性、検証
* review結果の一般的な扱い
* main agent自身の直接編集境界
* session運用
* `personality`
* `project_doc_fallback_filenames`
* `[agents]`
* `[mcp_servers.*]`

変更後、providerとdogfoodのTOML全体をbyte-identicalにする。

## 8. Handoff境界

Issue #359は次を用意する。

* 二つのskill contract
* provider asset
* dogfood projection
* additive materialization確認
* config cleanup
* docs pointer
* targeted test
* legacy inventory

Issue #359は次を変更または実施しない。

* installer logic
* managed / legacy managed skill定数
* obsolete inventory
* Target inventory cutover
* 旧skill prune
* fresh / update / uninstall consumer migration
* installed consumer matrix
* publication

IC-2へは`requirement.md`で定義した最小入力だけを渡し、pass / failの判定はIssue #359 ownerとEpic main orchestratorの統合責務とする。
