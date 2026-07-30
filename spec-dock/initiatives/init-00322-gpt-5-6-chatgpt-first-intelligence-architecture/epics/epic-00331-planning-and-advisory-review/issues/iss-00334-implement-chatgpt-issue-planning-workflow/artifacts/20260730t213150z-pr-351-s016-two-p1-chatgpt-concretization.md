---
種別: implementation-brief
ID: "20260730t213150z-pr-351-s016-two-p1-chatgpt-concretization"
タイトル: "PR 351 S016 repeated contention test and staged blob binding"
状態: "accepted"
作成者: "ChatGPT Pro"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: ["PR-351"]
authority: "advisory"
session: "iss00334-s016-two-p1"
source_head: "be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2"
model_evidence: "requested=Pro; resolved=Pro; verified=yes"
reflected_to: ["S016 bounded dev-coder input", "report.md"]
---

# PR 351 S016 repeated contention test and staged blob binding

## Verified scope

ChatGPTはGitHub connectorで`chemitaro/spec-dock`の
`iss-00334-implement-chatgpt-issue-planning-workflow` branchがpushed base
`be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`と同一であることを確認した。
default branchは参照していない。添付したprovider source／tests／decision artifactを
同HEAD上のcurrent uncommitted implementation stateとして分析した。

## Disposition

- P1-A repeated contentionはtest-onlyとし、`compare_replace` production behaviorを
  変更しない。
- P1-B staged content bindingはprovider Apply implementationへ一つのprivate
  staged-tree proofを追加し、focused regressionで閉じる。
- public CLI、schema、status／reason、allowed path set、Oracle boundaryは変更しない。

## P1-A: repeated contention regression

変更対象:

- `tests/integration/test_issue_planning_apply.py`

既存canonical race testsの近傍へ、次のfull-transaction regressionを追加する。

```text
test_archive_apply_second_canonical_replacement_during_exchange_back_retains_recovery_evidence
```

`_exchange_entries_at`をtest内で差し替え、`requirement.md`について:

1. 初回exchange直前にcanonicalをattachment Bへatomic replacementしてreal exchange。
2. exchange-back直前にcanonical transaction objectをattachment Cへatomic
   replacementしてreal exchange。

検証:

- resultは`recovery_required/restore_mismatch`。
- canonical `requirement.md`はB。
- mutation-ledgerが示すprivate workspace slotはC。
- original preimage Aは`backup-manifest.json`が示すprivate transaction backupに存在。
- mutation ledgerはoperation replacement digestを保持。
- local HEAD／bare-origin branchは初期HEADのまま。
- `commit.json`／`publication.json`は存在しない。
- `transaction/backup-manifest.json`／`transaction/mutation-ledger.json`は残る。

これはmissing characterization oracleであり、current S015 behaviorに対する
production Redを人工的に作らない。現実装で直ちにPASSすることを期待する。

## P1-B: staged index content binding

変更対象:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
- Apply focused unit／integration tests
- providerからdogfoodへのmechanical projection

追加するprivate helper:

```text
_expected_staged_blob_oids(
    operation,
    *,
    expected_companion_oid,
) -> Mapping[str, str | None]

_tree_blob_oids(
    repo_root,
    tree_oid,
    relatives,
) -> Mapping[str, str | None] | None
```

proof set:

```text
canonical_target_paths
+ companion_target_path
+ decision_artifact_path
```

authorized OID:

| target | authorized OID |
|---|---|
| archive-approved canonical documents | `_git_blob_oid(operation.replacement_documents[filename])` |
| other canonical document cases | `operation.pre_apply_target_blob_oids[path]` |
| approved companion | `_git_blob_oid(operation.replacement_companion)` |
| rejected companion | expected-HEAD companion OIDまたはexplicit absence |
| decision artifact | `_git_blob_oid(operation.human_decision_bytes)` |

必須ordering:

```text
worktree/untracked path-set proof
→ fault_hook("after_diff_proof")
→ git add -- <existing expected_paths only>
→ cached changed-path set == expected_paths
→ local_tree = git write-tree
→ five target entriesをlocal_treeから読む
→ operation-derived expected OID／absenceとexact比較
→ fault_hook("after_index_stage")
→ fault_hook("before_commit")
→ STAGED state
→ commit
```

`_tree_blob_oids`は一つのdirect argv、例えば
`git ls-tree -r -z <tree> -- <five paths>`を使い、次をfail closedする:

- nonzero Git result
- malformed output／non-UTF-8 path
- duplicate／unexpected target
- non-blob entry／unsupported mode
- invalid OID
- required entry missing／expected-absent entry present

expected OIDは`after_diff_proof`後のworktreeから導出しない。導出失敗、tree read
失敗、OID mismatchは既存
`_ApplyFailure("planning_commit_failed")`とし、commit前に停止する。

既存rollback semanticsを維持する:

- transaction-owned worktreeならexact rollback後
  `rolled_back/planning_commit_failed`。
- concurrent replacementでrestore不能ならevidenceを保持して
  `recovery_required/restore_mismatch`。

## Red tests

### Publishable atomic race

`design.md`、`plan.md`、`requirement.md`、companion、decision artifactを
parameterizeし、`after_diff_proof`で対象pathをunauthorized bytesへatomic
replacementしてそのまま残す。

修正後:

- `recovery_required/restore_mismatch`
- local commit 0、remote update 0
- `commit.json`／`publication.json` 0
- private transaction evidence保持

修正前はpath setが正しいためunauthorized bytesをstageし、
`ready/adoption_published`まで到達できる。

### Index-only poison

real `git add`後、test-only `hash-object -w`と
`update-index --cacheinfo`で一つのcanonical index entryだけをunauthorized blobへ
置換し、worktreeはauthorized bytesのままにする。

修正後:

- `rolled_back/planning_commit_failed`
- local／remote HEAD不変
- raw indexはpre-transaction snapshotへ一致
- worktree exact restore
- proven rollback後のtransaction evidence cleanup

修正前はunauthorized blobを含むlocal commitを作り、その後
`recovery_required/post_commit_workspace_changed`になるため、stop-before-commit
contractに反する。

## Green sequence

1. P1-A characterization testを追加しcurrent implementationでPASSを確認。
2. P1-Bの二つのregressionを追加しpre-fix failureを確認。
3. immutable operation fieldsだけからexpected OID mapを生成。
4. closed parserでtree entriesを取得。
5. 既存`git add -- <expected_paths>`とcached path-set proofを維持。
6. `write-tree`直後にfive target entryをexpected OID mapと比較。
7. mismatchはstaging fault hook／STAGED／commitより前に
   `planning_commit_failed`。
8. 既存postcommit `commit_tree == local_tree` proofを維持。
9. focused／full Apply regression後、既存projection workflowでdogfoodへ反映。

## Non-goals / stop conditions

- retry、lock、kernel CAS、retained storage、workspace scan、
  continuous-latest canonical pathname semanticsを追加しない。
- Oracle configuration behavior、wrapper policy、public CLI／schema、
  status／reason vocabulary、commit allowlist、push CAS、publication resumeを変更しない。
- five targetsをproof目的だけでstageしない。stageは既存`expected_paths`だけとし、
  immutable `local_tree`からfive entriesを検証する。
- target tree inventoryまたはOID／absenceが証明不能ならcommit前に停止する。
- rollback exactnessを証明できない場合は全evidenceを保持し、
  `recovery_required/restore_mismatch`だけを返す。
