---
種別: 設計書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-13"
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

| Provider authority                                                                                                      | Dogfood projection                                                    |
| ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`                                                   | `.agents/skills/spec-dock/SKILL.md`                                   |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md`                                   | `.agents/skills/spec-dock-grill-with-docs/SKILL.md`                   |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`                         | `.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`         |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py`               | `.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` |

`spec-dock`のFront Matterは、既存skill discoveryに必要な`name`と`description`に限定する。`spec-dock-grill-with-docs`の明示呼出し限定はCurrent Codexが認識する`agents/openai.yaml`の`policy.allow_implicit_invocation: false`で実効化する。SKILL front matterへ未認識のinvocation keyを置かない。

`finalize-artifact.py`はgrill skillだけが使用するskill-local client helperである。Artifact CLIのpublic argument、template、Runtimeを拡張せず、CLI publish後のsecond-openだけを安全にする。

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

configは`project_doc_fallback_filenames = [".codex/AGENTS.md"]`だけを持つ。変更後のprovider / dogfood pairはbyte-identicalとする。

### 2.4 Additive materialization境界

Current installerは次の順序で`install_root`を扱う。

1. `_iter_install_root_files()`が`install_root`配下の全通常fileを再帰的に列挙する。
2. `_build_current_managed_file_mappings()`が各fileを同じrelative targetへ対応付ける。
3. 二skill treeのmapped fileだけは、全copy前にmissing / byte-identical / non-identicalを判定する。
4. 二skill treeはrepository rootからdescriptor-relativeかつ`O_NOFOLLOW`で親を辿り、missing fileを`O_CREAT | O_EXCL`で作成する。existing fileはread-only no-follow openでbyte identityを再確認し、書き換えない。
5. その他のcurrent mappingは既存のcopy処理を使う。
6. uninstall inventoryも同じcurrent mappingを参照する。

したがって、二つのprovider skill treeを`install_root`へ追加すると、既存の汎用managed-file mappingを通じてcurrent init / update copyとuninstall inventoryから認識される。

Issue #359では、この機械的帰結をcollision-safe additive skill asset materializationとして受け入れる。新規targetはno-replaceで作成し、providerとbyte-identicalなexisting targetはread-only adoptionとし、非同一existing targetはuser-ownedの可能性があるため全copy前にfail-closedとする。preflight後のsymlink / path差し替えもdescriptor-relative no-follow処理で拒否する。open済みparentは最初のdata writeを行う関数内とwrite後にrepository rootから再openしたidentityと照合する。移動を検出した後はpathname cleanupを行わず、repo内で作成後に外部actorが移動した空のowned entryを保持し、user replacementを削除しない。判定は二skill treeへ限定し、generic ownership modelは作らない。

Issue #359は次を変更しない。

* `_MANAGED_SKILL_NAMES`
* `_LEGACY_MANAGED_SKILL_NAMES`
* `_build_managed_skill_install_plan()`
* obsolete exact path inventory
* 二skill限定content-collision preflight以外のinstaller init / update / uninstall logic

Current mappingに二skill treeが追加されることと、Target managed inventoryを二つへcutoverすることは別である。

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
6. route contractを満たす`##` section payloadをmemory上で確定する。CLIが生成するfront matter、Artifact ID、title、parent、template、authority、title headingはpayloadへ複製しない。
7. write直前に明示selectorとbootstrapを再確認する。
8. 対象scopeの`artifacts/`をsnapshotする。
9. 次のCurrent CLIを一回だけ実行する。

```text
./spec-dock/scripts/spec-dock new artifact <route> \
  --<initiative|epic|issue> <scope-id> \
  --title <title> \
  [--slug <slug>]
```

10. CLIが返したexact path textについて、skill-local helperの`identity`を使い、canonical repository-relative formまたはCurrent formatterの一つのrepository basename prefixだけをrepository rootへbindし、no-follow traversalでdevice / inode / `ctime_ns`を取得する。
11. 同helperの`finalize`へdevice / inode / `ctime_ns`とmemory上のroute sectionをstdinで渡す。helperはparent componentをdirfd + `O_NOFOLLOW`で開き、write直前にrepository rootからparent chainを再openして保持中parent fdと照合し、final fileのlstat / open / fstat identityも再確認する。CLI scaffoldの最初の`##`より前を保持してroute sectionだけを置換し、truncate / write / fsyncする。write後はctimeの更新を許容し、pathが同じdevice / inodeを指すことを確認する。
12. exactly-one postconditionを確認する。
13. exact pathとrouteをoperatorへ返す。

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

collision、CLI lock、no-replace publish、publish時のdestination safetyはCurrent Artifact CLIをauthorityとする。publish後の本文確定はskill-local helperをauthorityとし、返却pathnameへ直接writeしない。

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

成功後の`artifacts/` snapshot差分は、CLIが返した新規Markdown file一件だけでなければならない。本文確定前にhelperのidentityを取得し、finalize時に同じdevice / inode / `ctime_ns`であることを再検証する。CLI生成metadataとtitle headingを保持し、final pathまたはancestorがsymlinkの場合、またはidentityが変わった場合はwriteしない。

次のいずれかが検出された場合、成功と報告しない。

* 新規fileがゼロ件または複数件
* 返却path以外の新規entry
* 既存entryの変更または削除
* scope外の永続差分
* canonical文書、metadata、active、dependency、config、projectionの変更

### 6.4 Partial Artifact

Artifact publish後にidentity取得、安全な本文反映、またはpostcondition確認が失敗した場合、次の状態とする。

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

## 7. Codex configの最小化境界

provider configは次の一行だけを持つ。

```toml
project_doc_fallback_filenames = [".codex/AGENTS.md"]
```

この設定はrepository-localな`.codex/AGENTS.md`をproject documentation fallbackとして見つけるためだけに残す。次はprovider configで規定せず、利用者のCodex設定へ委ねる。

* `developer_instructions`
* `personality`
* modelとreasoning
* `[agents]`によるthread / depth設定
* `[mcp_servers.*]`
* その他のCodex設定項目

providerとdogfoodのTOML全体をbyte-identicalにする。Issue #359はfresh provider / dogfood contractだけを変更し、既存consumerに残る旧configの削除またはmigrationはIssue #360へ渡す。

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

* 二skill限定collision preflight以外のinstaller logic
* managed / legacy managed skill定数
* obsolete inventory
* Target inventory cutover
* 旧skill prune
* fresh / update / uninstall consumer migration
* installed consumer matrix
* publication

IC-2へは`requirement.md`で定義した最小入力だけを渡し、pass / failの判定はIssue #359 ownerとEpic main orchestratorの統合責務とする。
