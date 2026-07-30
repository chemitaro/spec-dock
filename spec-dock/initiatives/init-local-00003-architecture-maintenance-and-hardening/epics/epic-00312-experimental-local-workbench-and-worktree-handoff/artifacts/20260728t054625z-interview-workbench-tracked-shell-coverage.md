---
種別: interview
ID: "20260728t054625z-interview"
タイトル: "Workbench tracked shellの適用範囲"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00312"]
関連: ["20260728t054338z-research"]
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-28T05:46:25Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "2026-07-28 user clarification"
  - "20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md"
reflected_to:
  - "20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md"
---

# Workbench tracked shellの適用範囲

## 正式質問として扱う理由

この回答は次を変える。

- `requirement.md`
  - Workbench shellを必須とするscope
  - existing node migrationの要否
  - root/pre-scope Workbenchの位置づけ
- `design.md`
  - node templates
  - `init` / `update`
  - ignore pattern
  - migration flow
- `plan.md`
  - fresh node scaffoldだけを直すか、existing tree backfillも実装するか
- ADR
  - 通常は不要。migration / compatibility判断が長期契約になる場合だけ候補

chatだけで済ませると、「新規nodeだけ」「既存nodeも対象」「rootも対象」が混ざり、理想状態が再び曖昧になるため正式質問として記録する。

## 質問の目的

- 対象者:
  - product owner
- 明確にすること:
  - Git trackedな `.workbench/` shellを、どのscopeとどの時点のnodeへ必須化するか
- 後続への影響:
  - templatesだけの変更か、`init` / `update` migrationまで含むかが決まる

## 質問

Workbench の tracked shell は、次のどの範囲に必須とするのが意図でしょうか。

### Option A — 全scope・既存nodeも含めて統一（Codex推奨）

- root `spec-dock/.workbench/` は `init` / `update` で作る。
- Initiative / Epic / Issue は新規作成時に必ず作る。
- 既存 Initiative / Epic / Issue にも `update` またはmigrationで追加する。
- clone / checkout / linked worktreeではtracked markerにより最初から存在する。

### Option B — 今後新規作成するInitiative / Epic / Issueだけ

- 新規nodeには自動生成する。
- 既存nodeは変更しない。
- root Workbenchは従来どおり手動conventionとする。

### Option C — scope nodeは新旧すべて、rootは対象外

- Initiative / Epic / Issue は新規作成とexisting migrationの両方を行う。
- root/pre-scope Workbenchはtracked shellの対象にしない。

回答では、A / B / C、または修正版を指定してほしい。

## source-grounded context

確認済み:

- current Epic `requirement.md`
  - root/scoped placementは定義済み
  - runtimeはroot bucketを作成しない
  - scope Workbenchも手動配置が前提
- current Epic `design.md`
  - scope Workbenchはcopy時にtarget側だけ必要に応じて作る
- `application/create_node.py`
  - node作成はtemplate files、rules symlink、`.meta.json`を生成
- `templates/{initiative,epic,issue}/`
  - `.workbench/` markerは存在しない
- current managed ignore contract
  - `.workbench/` subtree全体をignoreする
- user clarification
  - directoryはGit管理し、contentsはGit管理しない
  - worktree終了時にcontentsが破棄される状態を求める

local contextで解決できたこと:

- Gitはempty directoryを追跡できないためtracked markerが必要
- contentsだけをignoreするpatternへ変更する必要がある
- Workbench contentsのhandoff/sync lifecycleは中心要件ではない

人間判断が必要な理由:

- 「新規作成時の自動生成」は明示されたが、existing nodesとrootを理想状態に含めるかは明示されていない
- この選択はmigration scopeとacceptance criteriaを変える

## Codexの分析

判断軸:

- directory構造の一貫性
- fresh clone / checkout時の予測可能性
- existing repositoryのmigration cost
- root/pre-scope workflowの必要性

tradeoff:

- Option Aは最も一貫するが、existing treeへのtracked marker追加が大量diffになりうる
- Option Bは最小変更だが、node作成時期によって構造が異なる
- Option Cはscope作業を統一できるが、rootだけ別ルールが残る

edge case:

- existing nodeにmarkerがなく、そこへcheckoutした利用者が再び手動`mkdir`を必要とする
- root Workbenchだけshellが存在せず、pre-scope作業とscope作業でUXが分かれる
- global ignore rule変更とexisting marker backfillの順序を誤ると、existing Workbench contentsが`git status`へ露出する

## Codexの推奨案

Option Aを推奨する。

理由:

- 「Workbenchはnodeの標準構造」という理想を例外なく表現できる
- tracked shellによりbranch/worktree間でdirectoryをcopyする必要がなくなる
- migrationを一度行えば、作成時期による構造差が残らない
- rootも含めればpre-scopeからscopeへのUXが一貫する

ただしmigrationは、existing Workbench contentsがGitへ露出しない順序で行う必要がある。

## ユーザー回答

- answer capture:
  - 2026-07-28 chat回答
- 回答:
  - Option AとBの中間。
  - fresh rootと今後新規作成するInitiative / Epic / IssueにはWorkbenchを自動生成する。
  - existing repositoryのrootとexisting Initiative / Epic / Issueは変更しない。
  - Workbenchの存在自体は必須ではない。
  - Workbenchがあれば利用でき、なければ利用者が作成してもよい。
- 回答日時:
  - 2026-07-28

## 追加確認の要否

- 追加確認が必要か: yes
- 次のquestion candidate:
  - `20260728t060417z-interview-generic-file-import-filename-contract.md`

## 採用判断

- adoption_status: adopted
- adoption target:
  - `20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md`
  - future `requirement.md`
  - future `design.md`
  - future `plan.md`
  - future `report.md` Evidence Adoption Ledger
- 理由:
  - product ownerが適用範囲とoptional contractを明示した
- `report.md`反映要否:
  - yes when canonical authoring begins

## requirement / design / plan / ADRへの含意

- `requirement.md`:
  - fresh rootとfuture-created nodesはWorkbench shellを生成する
  - existing root/nodesはmigrationしない
  - Workbench欠落はvalidation errorにしない
- `design.md`:
  - `init` scaffoldとfuture node templatesへtracked shell markerを含める
  - `update`はexisting Workbenchをbackfill/変更しない
  - user-created Workbenchも許容する
- `plan.md`:
  - fresh init/new node testsを追加する
  - existing update no-change testsを追加する
- `ADR`:
  - 現時点では不要
- reflected_to更新方針:
  - target-state researchへ反映済み
- adoption reflection:
  - canonical adoptionは後続authoringで行う
