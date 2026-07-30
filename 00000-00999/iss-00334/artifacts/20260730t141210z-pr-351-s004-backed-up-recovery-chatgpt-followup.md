# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b510a-f674-83ee-ba87-74d1e307e536

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached S004 brief as the complete defect-only follow-up. You MUST inspect the exact current GitHub branch and confirm HEAD 6c9302ab08c7f352e85a199b65bdeb522376171c; if unavailable return repository access failed and DO NOT inspect or substitute the default branch. Return only the requested bounded recovery-semantic guidance.

## Answer

## `minimal_strategy`

GitHub の current branch は `iss-00334-implement-chatgpt-issue-planning-workflow`、HEAD は要求どおり `6c9302ab08c7f352e85a199b65bdeb522376171c` と確認できた。

`BACKED_UP` recovery だけを次のように訂正する。

1. `_load_transaction_backup()` で durable backup を読み、operation ID、private evidence、manifest、inventory、digest を既存どおり検証する。
2. `backup.files` を `_apply_targets_match_snapshots(operation, repo_root, backup.files)` に渡す。この既存 helper により、次を backup 時点と比較する。

   * current branch
   * current HEAD
   * canonical 3 files の存在、bytes、mode
   * companion の存在／不在、bytes、mode
3. `BACKED_UP` では、比較結果にかかわらず `_restore_transaction()` を絶対に呼ばない。
4. mismatch がある場合だけ、backup を discard して `stale/apply_target_changed` を返す。
5. mismatch がなく、既存の remote-HEAD proof も成立する場合は、backup を discard して、pre-S003 の externally observable result である `rolled_back/planning_commit_failed` を返す。

exact GitHub HEAD の pre-S003 implementation は、successful interrupted-transaction recovery 後に `ROLLED_BACK` を記録し、`rolled_back/planning_commit_failed` を返している。 同じ HEAD の integration test も、`after_operation_recorded` を含む全 precommit checkpoint についてその結果を要求している。

最小の private-helper 修正として、`_discard_pre_mutation_backup()` に `final_state` を渡せるようにする。

* post-hook F003 drift: `final_state="OPERATION_RECORDED"`
* drifted `BACKED_UP` recovery: `final_state="OPERATION_RECORDED"`
* no-drift `BACKED_UP` recovery: `final_state="ROLLED_BACK"`

これにより、backup removal 後に二度 state を書き換える必要がなく、public schema、operation identity、status/reason set は変わらない。 

## `recovery_decision_table`

| Durable state / observation                                              | Recovery action                                        | Result                               | Final evidence state                     |
| ------------------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------ | ---------------------------------------- |
| state または backup evidence が unreadable／invalid                           | restore も discard も行わず fail closed                     | `recovery_required/restore_mismatch` | evidence retained where available        |
| `BACKED_UP`; branch、HEAD、canonical、companion のいずれかが backup snapshot と不一致 | **restore せず** backup のみ discard                       | `stale/apply_target_changed`         | transaction absent; `OPERATION_RECORDED` |
| `BACKED_UP`; local targets は一致するが existing remote-HEAD proof が不成立        | **restore せず** existing recovery failure semantics を維持 | `recovery_required/restore_mismatch` | transaction retained; `BACKED_UP`        |
| `BACKED_UP`; local targets と remote HEAD が一致                             | **restore せず** backup を discard                        | `rolled_back/planning_commit_failed` | transaction absent; `ROLLED_BACK`        |
| `BACKED_UP`; discard または final-state write が失敗                           | restore しない                                            | `recovery_required/restore_mismatch` | surviving evidence/stateを保持              |
| `MUTATING`、`VALIDATED`、`SYNCED`、`STAGED` 等                               | 現行 `_restore_transaction()` pathを変更しない                 | existing rollback/recovery result    | existing semantics                       |

remote mismatch／unavailability は、この S004 で `stale` へ再分類しない。pre-S003 recovery が持つ remote proof と `recovery_required/restore_mismatch` の意味をそのまま保持する。

## `operation_order`

1. `_load_operation_state()` を実行する。
2. state が `BACKED_UP` でなければ、既存の `MUTATING` 以降の recovery pathへ進み、変更しない。
3. state が `BACKED_UP` なら、最初に `_load_transaction_backup()` を実行する。

   * backup を削除する前に比較用 `FileSnapshot` を確保する。
   * invalid backup を「drift」とみなさず、`recovery_required/restore_mismatch` とする。
4. `_apply_targets_match_snapshots()` を一度実行し、branch、HEAD、canonical、companion の一致を判定する。
5. mismatch の場合:

   * `_discard_pre_mutation_backup(..., final_state="OPERATION_RECORDED")`
   * cleanup 成功時だけ `stale/apply_target_changed`
   * cleanup 失敗時は `recovery_required/restore_mismatch`
6. match の場合:

   * pre-S003 と同じく `_remote_head(repo_root, operation.branch) == operation.expected_head` を要求する。
   * remote proof 不成立なら、restore／discardを行わず `recovery_required/restore_mismatch`。
   * remote proof 成立なら、`_discard_pre_mutation_backup(..., final_state="ROLLED_BACK")`。
   * cleanup 成功後に `rolled_back/planning_commit_failed`。
7. どの `BACKED_UP` branch からも `_restore_transaction()` へ到達させない。

index、managed sync state、decision artifact は `BACKED_UP` recovery で restore または target-drift comparison の対象にしない。`BACKED_UP` は「durable backup 済みだが managed mutation は未開始」という S003 の意味を維持するためである。

## `tests`

### 1. No-drift `after_operation_recorded` crash recovery

現行 parameterized test から `after_operation_recorded` を分離し、専用 test にする。残りの `after_decision_write`、`after_plan_replace`、`after_companion_write`、`after_index_stage` は既存の `MUTATING` 以降の rollback test としてそのまま維持する。

専用 test の手順と assertion:

1. `fault_hook("after_operation_recorded")` で `BaseException` を投げ、process crash を模擬する。
2. crash 後、次を確認する。

   * `transaction/` が存在する。
   * `state.json == BACKED_UP`
   * canonical、companion、decision、HEAD に変更なし。
3. recovery invocation の直前に `_restore_transaction` を `pytest.fail("BACKED_UP must not restore")` へ monkeypatch する。
4. `validation_runner` と `sync_runner` も呼ばれたら fail とする。
5. recovery result は厳密に:

   * `rolled_back`
   * `planning_commit_failed`
6. recovery 後、次を確認する。

   * canonical bytes unchanged
   * companion absent
   * decision artifact absent
   * raw index unchanged
   * managed-state snapshot unchanged
   * local HEAD と remote HEAD は expected HEAD
   * `transaction/` absent
   * `state.json == ROLLED_BACK`

attached S003 test にある `after_operation_recorded` 専用の conditional `stale/apply_target_changed` expectation は削除し、GitHub exact-HEAD の従来 expectation に戻す。

### 2. Drifted `BACKED_UP` recovery after cleanup interruption

既存の `test_backed_up_recovery_discards_without_overwriting_concurrent_bytes` を維持し、次を追加する。

1. 最初の invocation:

   * `after_operation_recorded` で absent companion を concurrent bytes により作成する。
   * `_remove_transaction_backup` を一度だけ失敗させる。
   * result は `recovery_required/restore_mismatch`。
   * concurrent companion bytes preserved。
   * `transaction/` exists。
   * state は `BACKED_UP`。
2. recovery invocation 前に `_restore_transaction` を、呼ばれた場合に test failure とする monkeypatch に置換する。
3. recovery result は:

   * `stale`
   * `apply_target_changed`
4. recovery 後:

   * concurrent companion bytes preserved exactly
   * decision artifact absent
   * canonical bytes unchanged
   * local／remote HEAD unchanged
   * `transaction/` absent
   * `state.json == OPERATION_RECORDED`
   * validation／sync call 0

no-drift test と drifted test の結果差により、`BACKED_UP` recovery が unconditional `stale` ではなく、durable backup snapshotとの実比較で分類していることが決定的に証明される。

既存の direct post-hook F003 tests、および `MUTATING` 以降の exact rollback tests は変更しない。

## `residual_risk`

snapshot comparison は point-in-time 判定であるため、比較直後に外部変更が発生すれば、その invocation の result classification と最終 filesystem state がずれる可能性は残る。ただし `BACKED_UP` recovery は managed file を一切書かず、restore もしないため、その race によって concurrent bytes を上書きすることはない。後続 apply の通常 preflight／post-hook recheck が drift を再検出する。

この訂正は以下を変更しない。

* public status／reason／output schema
* operation schema／operation ID
* F002 Candidate publisher
* post-hook F003 preimage check
* `MUTATING` 以降の restore semantics
* remote divergence handling
* Oracle configuration boundary

## `advisory_verdict`

`implementable`
