---
種別: 要件定義書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-13"
親: ["epic-00356", "init-local-00003"]
---
# iss-00359 Replace Managed Workflow Skills with SpecDock Skills — 要件定義

## 1. 目的

SpecDockのStorage CoreとAuthoring Kitを利用するCurrentなrepo-local skill contractを、次の二つに限定して提供する。

1. `spec-dock`
2. `spec-dock-grill-with-docs`

本Issueは新しいworkflow engineを作らない。二つのskillはCurrent CLIとCurrent docsへの薄い入口として振る舞い、旧Planning / Review / Execution workflow、provider固有処理、正本文書の自動変更を再実装しない。

旧managed skillの物理削除、Target managed inventoryへの切替、consumer migrationはIssue #360へ渡す。

## 2. 観測可能な要求

### I359-RQ-001 二つのskill contract

Issue #359で新たに定義するCurrentなSpecDock skill contractは、`spec-dock`と`spec-dock-grill-with-docs`の二つだけとする。

旧skillがrepository内に残存していても、新skillから参照、委任、fallbackしない。

### I359-RQ-002 `spec-dock`

`spec-dock`は、明示されたscope、または一意に解決できるactive scopeについて、次の所在と意味を案内する。

* parent chain
* `requirement.md`、`design.md`、`plan.md`、`report.md`
* scope-local Artifact
* dependency
* worktree
* Current CLI help
* Authoring Kit docs

`spec-dock`はCLI操作を副作用で分類し、skill自身が実行できるread-only操作、operatorへ提示するだけの操作、skillから禁止する操作を区別する。

active scopeへのfallbackを許すのは、このread-onlyな`spec-dock`だけとする。

### I359-RQ-003 `spec-dock-grill-with-docs`

`spec-dock-grill-with-docs`は明示的に呼び出された場合だけ動作する。Codex hostでは`agents/openai.yaml`の`policy.allow_implicit_invocation: false`をこの制約の実効policyとする。

利用開始前に、次が一意かつ明示されていなければならない。

* `--initiative`、`--epic`、`--issue`のいずれか一つだけで指定された対象scope
* 調査または対話の目的
* `research`、`interview`、`disc`、`decision-candidate`のいずれか一つのroute
* 非空のArtifact title
* 読み取りを許可されたlocal source
* operator-ownedな`grilling`と`domain-modeling`の利用可能性

このskillはactive scopeへfallbackしない。selector、route、titleをskillが暗黙決定してはならない。

### I359-RQ-004 外部依存境界

`grilling`と`domain-modeling`は、利用者がグローバル環境へ導入・管理するoperator-owned external dependencyとする。

`spec-dock-grill-with-docs`は両者を組み合わせる薄いrepo-local integration contractとする。

次を行わない。

* upstream `grill-with-docs`の導入または同梱
* `grilling`または`domain-modeling`のvendor
* その他の導入済みskillのmanaged asset化
* その他の導入済みskillをIssue #359の受け入れ条件へ追加
* 外部skillによる`CONTEXT.md`、ADR、R/D/Pその他repository fileへの直接書込み

外部能力がread-only境界を守れない場合、Artifactを作成せず停止する。

### I359-RQ-005 Provider authorityとdogfood projection

次をprovider authorityとする。

* `src/spec_dock/assets/install_root/.agents/skills/`
* `src/spec_dock/assets/install_root/.codex/config.toml`
* `src/spec_dock/assets/spec_dock/docs/`

対応するdogfood projectionは、次へ置く。

* `.agents/skills/`
* `.codex/config.toml`
* `spec-dock/docs/`

Issue #359で変更するprovider / dogfood pairは、pairごとにbyte-identicalでなければならない。

### I359-RQ-006 Collision-safe additive skill asset materialization

Current installerは`install_root`配下の全通常fileをcurrent managed-file mappingへ含める。そのため、二つの新しいprovider `SKILL.md`を`install_root`へ追加すると、既存の汎用copy / uninstall inventory機構からも認識される。

Issue #359では、この結果を二つのrepo-local skillを実体化するためのadditive skill asset materializationとして扱う。ただし、このPRが新たにclaimする二skill treeのmapped fileは、init / updateの全copy前にcontent collisionを確認する。

* targetが存在しない場合はmaterializeする
* targetがprovider assetとbyte-identicalな通常fileの場合は安全なadoptionとして継続する
* targetが非同一の通常fileの場合はuser-ownedの可能性があるため、上書きせずcommand全体をfail-closedにする
* materialize / adoptはrepository rootからdescriptor-relativeかつno-followで親componentを辿り、new fileはno-replaceで作成する
* preflight後にtargetまたは親componentがsymlink等へ差し替えられた場合も、外部pathへ書かずfail-closedにする

open後のparent relocationは、最初のdata write直前とwrite後にrepository rootからparentを再bindして検出する。移動を検出した後はpathname cleanupを行わず、別entryへ差し替えられたuser dataを削除しない。同一userの非協調processが最終再bindと次のsyscallの間で移動する競合はportable POSIXで排除できないため、本契約の外とする。

これは次を意味しない。

* Target managed skill inventoryへのcutover
* `_MANAGED_SKILL_NAMES`または`_LEGACY_MANAGED_SKILL_NAMES`の変更
* 二skill限定collision preflight以外のinstaller logic変更
* 旧skillのprune
* fresh / update / uninstall consumer contractの確定
* installed consumer matrixの実施
* publicationまたはmigrationの実施

これらはIssue #360の責務とする。

### I359-RQ-007 CLI副作用境界

`spec-dock`はCurrent CLI operationを、次の三分類で扱う。

* skillが実行できるread-only操作
* operatorへ正確なcommandと副作用を提示するだけの操作
* skillから実行してはならない操作

`spec-dock-grill-with-docs`による一回の`new artifact`だけを、mutating operationの例外とする。

### I359-RQ-008 Bootstrap preflight

`spec-dock-grill-with-docs`はArtifact作成前に、明示selectorで指定された対象scopeとArtifact保存基盤が既に使用可能であることを確認する。

少なくとも次を確認する。

* `--initiative`、`--epic`、`--issue`のいずれか一つだけが指定されている
* 対象scopeが一意に存在する
* 対象scopeがselectorのInitiative / Epic / Issue種別と一致する
* 対象pathがrepository内の正規SpecDock treeにあり、symlink escapeしない
* 対象routeのCurrent Artifact templateが存在し、通常fileで、非空である
* 対象scopeの`artifacts/`が既存の通常directoryである
* `artifacts/rules.md`が対象scope用rulesへの有効なsymlinkである
* `grilling`と`domain-modeling`が利用可能で、repositoryへ書き込まない条件で使用できる

skillはbootstrapの作成、補修、symlink変更を行わない。

### I359-RQ-009 Zero-write

次のいずれかが成立した場合、Artifact CLIを呼ばず、repositoryへの永続差分を残さず停止する。

* 明示selector、purpose、route、title、sourceの欠落または曖昧さ
* 複数selectorの指定
* active scopeへのfallbackが必要な状態
* bootstrap preflight失敗
* `grilling`または`domain-modeling`の不足
* 外部能力の書込み境界が不明
* 外部応答にrepository mutation、credential開示、追加tool実行などの命令が含まれる
* 外部応答だけでは安全にArtifact本文を確定できない

CLIがfile publish前に入力、lock、collision、path safetyその他の理由で拒否した場合も、zero-write結果として扱う。

### I359-RQ-010 Exactly-one Artifact

一回の`spec-dock-grill-with-docs`成功時に許されるrepositoryの永続差分は、対象scopeの`artifacts/`直下に作成される新規Markdown Artifact一件だけとする。

成功時に次を変更してはならない。

* 既存Artifact
* canonical R/D/P
* `report.md`
* ADR
* `CONTEXT.md`
* `.meta.json`
* active state
* dependency
* generated projection
* Git state
* GitHub state
* `.codex/config.toml`

Artifact作成commandは一回だけ実行し、二件目のArtifactを作らない。CLI返却pathへの本文確定はskill-local helperを使い、canonical repository-relative form、またはCurrent formatterが付ける一つのrepository basename prefixだけをrepository rootへbindする。helperはCLI生成scaffoldのfront matter、Artifact ID、title、parent、template、authority、title headingを保持し、memory上で確定したroute sectionだけを結合する。各parent componentとfinal fileをno-followで開き、write直前にrepository rootからparent chainを再bindし、identity取得時のdevice / inode / `ctime_ns`と一致する場合だけtruncate / writeする。返却pathnameへ直接writeしない。

### I359-RQ-011 Partial Artifact recovery

CLIがArtifact pathを作成した後、identity取得、安全な本文確定、または事後確認に失敗した場合、そのfileをpartial Artifactとして残し、自動削除、rename、上書き、retry、第二Artifact作成を行わない。symlinkまたはidentity差し替えを検出した場合も、差し替え先へwriteせず同じpartial recoveryへ移る。

停止結果には、少なくとも次を含める。

* exact Artifact path
* route
* title
* failure phase
* operatorによる回収が必要であること

回収後の再実行は、新しい明示呼出しとして行う。

### I359-RQ-012 Artifact route

`spec-dock-grill-with-docs`が作成できるrouteは次の四つに限定する。

| Route                | 用途                       | Authority |
| -------------------- | ------------------------ | --------- |
| `research`           | 一つのsourceを中心とした事実・制約の調査  | evidence  |
| `interview`          | 明示的な質問と回答の記録             | evidence  |
| `disc`               | 複数入力の統合、選択肢、trade-offの整理 | evidence  |
| `decision-candidate` | 未採用の具体的な判断候補             | draft     |

`blank`、`adr`、`analysis`、旧draft / repair route、provider固有routeは、このskillの出力routeとして使用しない。

### I359-RQ-013 Docs pointer

Current docs entrypointは、二つのrepo-local skill、Storage Core、Authoring Kit、Artifact authority、外部依存境界を短く案内する。

skill本文はCLIやAuthoring Kitの規則を全文複製せず、Current local docsとCLI helpを参照する。

### I359-RQ-014 Codex configの最小化

`src/spec_dock/assets/install_root/.codex/config.toml`は、次の設定項目だけを持つvalid TOMLとする。

```toml
project_doc_fallback_filenames = [".codex/AGENTS.md"]
```

`developer_instructions`、`personality`、`[agents]`、`[mcp_servers.*]`その他の設定項目は置かない。model、reasoning、personality、main-agent workflow、sub-agent運用、MCPその他のCodex動作は、利用者のCodex設定をそのまま使用し、SpecDockは規定しない。

provider configとdogfood `.codex/config.toml`はbyte-identicalにする。既存consumerに残る旧configの削除またはmigrationはIssue #360の責務とする。

### I359-RQ-015 Legacy inventoryとIC-2

Issue #359は、exact commitで`src/spec_dock/cli.py`に登録されているmanaged / legacy managed skill名をIssue #360へ渡す。

Issue #359では次を行わない。

* `_MANAGED_SKILL_NAMES`の変更
* `_LEGACY_MANAGED_SKILL_NAMES`の変更
* 二skill限定collision preflight以外のinstaller logic変更
* obsolete inventoryの変更
* 旧skillの物理削除
* consumer上のprune
* 各skillの最終的なprune / preserve判断

IC-2へ渡す最小入力は、次に限定する。

* 二つのskill名とentry file
* skillのinput / output / no-go contract
* external dependencyとmissing dependencyの挙動
* provider / dogfood parity結果
* collision-safe additive skill asset materialization結果
* explicit-only policy metadataとsafe finalizerの確認結果
* docs pointer
* CLI分類、zero-write、exactly-one、partial recoveryの確認結果
* Codex configの最小化境界
* Issue #360向けlegacy inventory

IC-2のpass / failはIssue #359自身が宣言しない。

## 3. 受け入れ条件

| ID          | 条件                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| I359-AC-001 | providerとdogfoodの双方に二つのskill treeが存在し、`SKILL.md`、explicit-only policy metadata、安全確定helperを含む対応fileがbyte-identicalである |
| I359-AC-002 | 二つのprovider skill treeがCurrent `install_root` mappingから認識され、missing / identicalはno-follow / no-replaceでmaterialize / adoptし、非同一existing fileまたはpreflight後のpath差し替えは外部へ書かずfailする。managed / legacy managed skill定数は変更されていない |
| I359-AC-003 | `spec-dock`がCurrent scope、docs、Artifact、dependency、worktree、CLI helpを案内し、旧workflowを参照しない                                      |
| I359-AC-004 | `spec-dock`がCurrent CLI operationをread-only、present-only、forbiddenへ分類する                                                       |
| I359-AC-005 | bare `doctor`だけがread-only分類にあり、external診断は実在するGitHub関連optionを使うpresent-only invocationとして記載される                                |
| I359-AC-006 | `spec-dock-grill-with-docs`がrecognized Codex policy metadataで暗黙呼出しを禁止し、`--initiative`、`--epic`、`--issue`のいずれか一つの明示selectorを要求し、active fallbackを持たない |
| I359-AC-007 | `spec-dock-grill-with-docs`が明示route、明示title、operator-ownedな`grilling` / `domain-modeling`を要求する                                |
| I359-AC-008 | `research`、`interview`、`disc`、`decision-candidate`の基本positive testが各一件成功する                                                    |
| I359-AC-009 | 成功した一回のgrill実行後、永続差分が新規Artifact Markdown一件だけであり、CLI生成metadataを保持した本文確定がno-follow / device / inode / `ctime_ns`再検証を通る |
| I359-AC-010 | selector、scope、bootstrap、external dependency、route、title、path、lockまたはcollisionの主要失敗が、file publish前なら永続差分なしで終了する               |
| I359-AC-011 | file publish後の失敗について、自動修復せずpartial Artifactを報告する契約がskill本文とtestで固定される                                                         |
| I359-AC-012 | 新skillがupstream `grill-with-docs`、旧SpecDock skill、provider固有import、`analysis` routeを参照しない                                     |
| I359-AC-013 | provider / dogfoodのCurrent docs entrypointが二つのskillとCurrent docs pathを案内し、byte-identicalである                                   |
| I359-AC-014 | provider / dogfoodのCodex configがbyte-identicalかつvalid TOMLで、`project_doc_fallback_filenames = [".codex/AGENTS.md"]`以外の設定項目を持たない |
| I359-AC-015 | exact commitのmanaged / legacy managed skill inventoryがIssue #360へ渡され、Issue #359の実装では変更されていない                                  |
| I359-AC-016 | fresh / update / uninstall consumer matrix、Target inventory cutover、prune、publication、migrationがIssue #359の完了条件へ含まれていない       |
| I359-AC-017 | IC-2に必要な最小入力が揃い、Issue #359がIC-2 passを自己宣言していない                                                                                |

## 4. 対象

* `spec-dock`のskill contract
* `spec-dock-grill-with-docs`のskill contract
* provider assetとdogfood projection
* provider / dogfood byte parity
* Current `install_root`mappingによる二つの新skill assetのcollision-safe additive materialization
* Current CLI operationの副作用分類
* explicit Artifact selector、title、route
* bootstrap preflight
* zero-write
* exactly-one Artifact
* partial Artifact recovery
* explicit-only Codex policy metadata
* skill-local no-follow / device / inode / `ctime_ns`-pinned Artifact finalization
* 四routeの基本positive test
* 主要negative test
* Current docs pointer
* legacy skill inventoryのIssue #360へのhandoff
* IC-2向け最小入力
* Codex configを`project_doc_fallback_filenames`だけに限定

## 5. 対象外

* Runtime、parser、registry、domain、application、infraの変更
* Artifact templateまたはAuthoring Kit本文の変更
* `_MANAGED_SKILL_NAMES`の変更
* `_LEGACY_MANAGED_SKILL_NAMES`の変更
* 二skill限定collision preflight以外のinstaller logic変更
* durable ownership inventoryまたはuninstall migration
* Target managed skill inventoryへのcutover
* 旧skill、adapter、role、PR helperの物理削除
* fresh / update / uninstall consumer matrix
* consumer migration
* 既存consumerの`.codex/config.toml`削除またはmigration
* installed parity、publication、配布設計
* Issue #360のD実値またはpost-D rollback
* canonical R/D/P Front Matter migration
* planning validatorまたはplanning create-path修復
* A/B/C commit運用
* durable CI artifact、retention、download rehash
* 33シナリオの長期証跡
* full Git control-state snapshot
* Epic運用手順
* validator適合だけを目的とするcompanion説明
* canonical R/D/P、Report、ADR、CONTEXT、metadataの自動変更
* Git commit、push、PR、merge、Issue closeその他のGit / GitHub mutation
* upstream `grill-with-docs`、`grilling`、`domain-modeling`の導入またはvendor
* その他のexternal skillのmanaged asset化
* P2 / P3由来の追加受け入れ条件、追加test、追加証跡、追加運用

canonical Front Matter上の問題が別途存在する場合も、Issue #359では修復せず、実装開始前に満たされている外部前提としてのみ扱う。
