---
種別: implementation-brief
ID: "20260730t220930z-pr-351-s017-verified-tree-commit-binding-chatgpt-concretization"
タイトル: "PR 351 S017 verified tree to local commit binding"
状態: "accepted"
作成者: "ChatGPT Pro"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: ["PR-351"]
authority: "advisory"
conversation: "iss00334-s016-two-p1"
followup_session: "required-repository-connector-context-github-24"
source_head: "be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2"
model_evidence: "follow-up reused verified Blue conversation; follow-up selection resolved unavailable/verified no"
reflected_to: ["S017 bounded dev-coder input", "report.md"]
---

# PR 351 S017 verified tree to local commit binding

## Verified scope

S016と同じBlue Team conversationを継続した。ChatGPTはGitHub connectorで
`chemitaro/spec-dock`のexact current branchとpushed base
`be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`を確認し、default branchを使用して
いない。follow-upのためmodel再選択は行われず、follow-up run単体の
`resolved`／`verified` evidenceはunavailableである。

## Single finding

S016は`local_tree = git write-tree`のfive target OIDを検証するが、その後の
`after_index_stage`／`before_commit`／state persistenceと通常`git commit`の間に
real indexが置換されると、検証済み`local_tree`ではないtreeからunauthorized
local commitを生成できる。後段のtree mismatchはpushを止めるが、
stop-before-commit contractを満たさない。

## Required private seams

provider authorityの
`infra/issue_planning_apply.py`だけに、次と同等のprivate seamを追加する。

```text
_run_git_with_private_index(...)
_create_verified_operation_commit(...)
_install_operation_commit_cas(...)
```

- operation-private `GIT_INDEX_FILE`をdirect argvで扱う。
- verified `local_tree`と`operation.expected_head`からcommit objectを生成する。
- commit tree、single parent、changed paths、required operation trailerを検証する。
- checked-out branch refが`operation.expected_head`の間だけold-value CASでcommitを
  installする。
- generic `update-ref`を既存validatorへ開放せず、fixed argv／proof-bearing private
  helperへ閉じ込める。

## Required ordering

```text
existing add/cached path proof
→ local_tree = write-tree
→ existing five-target OID proof
→ after_index_stage
→ before_commit
→ persist STAGED
→ private 0700 commit workspace
→ private indexへread-tree local_tree
→ private write-tree == local_tree
→ pre-commit／prepare-commit-msg／commit-msg hooks
→ private write-tree == local_treeを再証明
→ real index write-tree == local_treeをlate check
→ commit-tree local_tree -p expected_head
→ commit object proof
→ exact checked-out branch refへold-value CAS update
→ committed = True
→ post-commit hook
→ existing commit evidence／COMMITTED／workspace gate／push CAS
```

実際のcommit objectは`commit-tree <local_tree> -p <expected_head>`で作り、
mutable real indexをconsumeしない。ref install前に:

- `symbolic-ref -q HEAD == refs/heads/<operation.branch>`
- real `HEAD == operation.expected_head`
- commit parentはexactly oneで`expected_head`
- commit treeは`local_tree`
- changed pathsは`expected_paths`
- messageは`SpecDock-Planning-Operation: <operation_id>`を保持

を証明する。

## Hook / signing boundary

- `git hook run --ignore-missing`をGit自身のdispatcherとして利用し、
  `pre-commit`、`prepare-commit-msg`、`commit-msg`、`post-commit`を通常順で実行する。
- pre-install hooksはprivate indexを参照する。
- pre-install hookのnonzero、private index mutation、message trailer欠落はcommit
  creation／ref install前に拒否する。
- `post-commit`はCAS install後だけ一度実行し、既存postcommit cleanliness gateへ
  接続する。
- implicit commit signingを失わないこと。supported Gitの`commit-tree` signing
  capabilityとrepository configを検証し、必要なら既存設定と同じsigning intentを
  explicitに適用する。silent signing bypassは禁止。
- 現環境はGit 2.54.0で`git hook run`を提供し、current checkoutには
  `commit.gpgsign`／`user.signingkey`／`gpg.format`の設定とactive local hooksが
  ないことをMainが確認した。一般consumer behaviorはfocused testで保護する。

## Red / Green tests

### Late real-index poison

`after_index_stage`でunauthorized blobをreal indexの`requirement.md`へ設定し、
worktreeはauthorized bytesのままにする。

修正前:

- ordinary `git commit`がpoisoned indexをconsume
- local HEADがunauthorized commitへ進む
- remoteはexpected HEAD
- 後段tree mismatchで`recovery_required/restore_mismatch`
- commit／publication evidenceなし、STAGED evidence保持

修正後:

- late real-index proofがcommit object生成前に検出
- `rolled_back/planning_commit_failed`
- local／remote HEAD不変
- worktree／real index exact restore
- local commit、commit／publication evidence 0

### Race after final real-index proof

final real-index proof直後／`commit-tree`直前にreal indexをpoisonする。installed
local commitが存在する場合も、treeは必ずverified `local_tree`、parentは
`expected_head`、target blobsはauthorizedである。残るreal-index driftは既存
`recovery_required/post_commit_workspace_changed`、remote不変へ接続する。

### Hook regressions

- four hooksが通常順で各1回。
- pre-install hooksは`local_tree`相当のprivate indexを参照。
- rejecting pre-commitはexact precommit rollback。
- index-mutating pre-commitはlocal commit install前に拒否。
- post-commit workspace mutationは既存
  `recovery_required/post_commit_workspace_changed`を維持。

## Crash / recovery

- ref install前のhook／proof／CAS failureは既存precommit rollback。
- `commit-tree`後／ref install前のunreachable objectはauthorityを持たず、
  existing STAGED recoveryを使う。
- CAS failureでrefを上書きしない。HEAD drift時は
  `recovery_required/restore_mismatch`。
- ref install直後に`committed = True`とし、以後reset／amend／rollbackしない。
- crash after ref install before `commit.json`は既存conservative recovery-required
  windowを維持し、新journal schemaを追加しない。
- private index／message fileはephemeralで、resume authorityへ昇格させない。

## Non-goals

lock、retry、custom ref、temporary branch、worktree、daemon state、public field／
status／reason、新依存、Oracle/config変更、S015 contention再設計、S016 five-target
proof再設計を行わない。
