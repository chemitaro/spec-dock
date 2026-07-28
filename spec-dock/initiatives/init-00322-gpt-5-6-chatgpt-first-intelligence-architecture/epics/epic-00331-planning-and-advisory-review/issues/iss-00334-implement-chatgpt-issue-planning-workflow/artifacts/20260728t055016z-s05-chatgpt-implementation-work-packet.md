---
artifact_type: s05-chatgpt-implementation-work-packet
created_at: 2026-07-28T05:50:16Z
created_by_role: chatgpt-pro
intended_issue: iss-00334
intended_step: S05
adoption_status: execution-input
review_required: false
source_repository: chemitaro/spec-dock
source_branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: 2e0589e1e4ce1b123cd30d14c338d07038ed1429
initial_session: iss00334-s05-implementa-brief
model_requested: Pro
model_resolved: Pro
model_selection_verified: true
---

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a683c13-dda8-83ee-a618-f530d0c2aa39

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

Use the attached prompt as the complete task brief. Inspect the required GitHub branch and return only the bounded S05 implementation work packet.

## Answer

# `iss-00334` — S05 Human Gate and Apply Transaction 実装ワークパケット

| 項目                   | 確定値                                                                               |
| -------------------- | --------------------------------------------------------------------------------- |
| Repository           | `chemitaro/spec-dock`                                                             |
| Current branch       | `iss-00334-implement-chatgpt-issue-planning-workflow`                             |
| Default branch       | `main`                                                                            |
| Exact pushed HEAD    | `2e0589e1e4ce1b123cd30d14c338d07038ed1429`                                        |
| Active Issue         | `iss-00334`                                                                       |
| Milestone            | **S05 — Human Gate and Apply Transaction only**                                   |
| Packet disposition   | **GO / review-waived**                                                            |
| Product-contract gap | **なし**                                                                            |
| 実装方針                 | 既存S01–S04契約を変更せず、S05専用application orchestrationとscoped transaction adapterだけを追加する |

本パケットは添付briefを完全な作業境界として扱う。

---

## 1. Verified GitHub identity evidence

### 1.1 検証結果

GitHub connectorで次を確認済み。

| 検証                      | 結果                                                                                                 |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| Repository access       | `chemitaro/spec-dock` を取得可能                                                                        |
| Default branch          | `main`                                                                                             |
| Requested branch access | `iss-00334-implement-chatgpt-issue-planning-workflow` 上のファイルを取得可能                                  |
| Exact HEAD comparison   | branch と `2e0589e1e4ce1b123cd30d14c338d07038ed1429` は `identical`、ahead `0`、behind `0`             |
| Exact commit            | `2e0589e1...1429` はS04 closure evidence commit                                                     |
| S04 prerequisite        | implementation commit `6042553343225541709f71e74eeeca549ead2089`、push、local/remote parity完了として記録済み |

Exact HEADのcommitは、S04をclosedとしS05へ進むこと、S04 implementation commitがpush済みであることを明示している。
Requested branch自体もGitHubから正常に読み出せている。

### 1.2 検証境界

GitHub connectorで検証したのはremote repository、branch、commit identityである。実装時のlocal worktree、Git index、upstream、fetch後remote-tracking ref、credentials、push可能性は未検証であり、S05 runtime preflightが毎回証明しなければならない。

---

## 2. Goal、obligations、non-goals

### 2.1 Goal

Exact Review bytesと、それへbindしたexact `PlanningHumanDecisionV1` bytesだけをHuman authorityとして受理し、承認時は安全なcanonical adoption、拒否時はdecision-only publicationを行う。

`ready`は次の論理積だけから導出する。

```text
ready =
    review.verdict == pass
    AND exact Human-approved binding
    AND reviewed identity freshness
    AND expected local/remote HEAD parity
    AND Candidate/canonical または reviewed-blob parity
    AND SpecDock validation pass
    AND SpecDock sync pass
    AND exact tracked-diff allowlist pass
    AND exact staged-tree proof
    AND planning-only commit proof
    AND normal push success
    AND local commit == remote branch HEAD
    AND local commit tree == remote commit tree
```

Review completionまたはHuman approvalだけでは、絶対に`ready`にしない。Canonical Planも、S05をexact evidence validation、decision-only rejection、whole-file adoption、transaction、validation、commit、push、remote parityとして固定している。

### 2.2 In-scope obligations

1. Review-result fileとHuman-decision fileをdescriptor-safeに一度だけ読み、exact bytesをoperation中固定する。
2. `PlanningReviewResult.from_json_bytes()`でReviewをstrict parseする。
3. `PlanningHumanDecisionV1.from_json_bytes(..., review_result_bytes=exact_bytes)`でHuman decisionをstrict parseする。
4. Request、Review、Human、resolved Issue、repository、branch、expected HEAD、Candidate identityまたはgit-bound identityを相互検証する。
5. `approved`はReview `pass`の場合だけadoptionへ進める。
6. `rejected`はcanonical三文書を一切変更せず、exact Human-decision bytesだけをdecision artifactとしてpublishする。
7. Archive modeでは、単一capture済み・検証済みCandidateから三文書だけをprivate stageへmaterializeし、whole-file replacementする。
8. Git-bound modeでは、reviewed HEADのexact target blob OIDsとcurrent bytesの一致を証明し、三文書は書かない。
9. Canonical三文書、decision artifact、raw Git index、managed SpecDock sync stateを対象とするbounded transactionを実装する。
10. Validation、sync、tracked diff、staged treeを証明してからPlanning専用commitを作る。
11. Normal push後にlocal/remote commitとtree parityを証明する。
12. Pre-mutation、pre-commit rollback、restore mismatch、post-commit publication pending、retry、remote divergenceをclosed status/reasonへ写像する。
13. PA-NF-01–09、10A、10Bを独立したnamed testsとして実装し、すべて`is_ready == False`を確認する。
14. Fake bare remoteを使い、全terminal resultでrepository、Git index、HEAD、remote HEADのpostconditionを確認する。
15. Archive Review省略はcanonical proof全条件が揃った場合だけ認める。

Requirementは、rejected decisionのdecision-only記録、archive whole-file parity、git-bound blob不変、rollback、Review-skip条件を明示している。

### 2.3 Explicit non-goals

* `requirement.md`、`design.md`、`plan.md`、`report.md`の編集
* S01のReview/Human/result schema変更
* Public CLI argumentsまたはcommand names変更
* `UseCases`、bootstrap、runtime construction wiring
* Generic `GitGateway`、generic transaction framework、generic publication frameworkの拡張
* S06 provider projection、installed Skill、packaging、fresh init/update、dogfood parity
* S07 live ChatGPT/GitHub dogfood、real target mutation、Delivery PR、Human merge
* Root `spec-dock/` dogfood projectionの直接編集
* Persistent registry、database、custom Git ref、hidden ref、別workspace探索
* `force`、`--force-with-lease`、`reset`、`amend`
* Real repositoryでのS05 apply、commit、push
* Canonical Planの改善提案または再設計

S06はprovider/distribution/projection/full E2Eを担う後続milestoneであり、本パケットでは触れない。

---

## 3. Exact existing symbols and primitives to reuse

| Existing symbol / primitive                                                         | S05での利用                                                              | 変更                     |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ---------------------- |
| `PlanningApplyRequest`                                                              | 現行apply requestをそのまま受ける                                              | **read-only**          |
| `PlanningReviewResult.from_json_bytes()`                                            | Exact Review bytesのclosed schema、identity、verdict検証                  | **read-only**          |
| `PlanningHumanDecisionV1.from_json_bytes()`                                         | Review raw-byte SHA、reviewed identity、truth tableの一括検証               | **read-only**          |
| `IssueCandidateIdentity`                                                            | CLI filename/SHA、actual ZIP、Review identityの一致判定                     | **read-only**          |
| `ReviewedPlanningIdentity`                                                          | archive/git-bound mode closureとexact canonical paths                 | **read-only**          |
| `PlanningCommandResult`                                                             | 全S05 status/reason、`is_ready`、text/JSON共通結果                          | **read-only**          |
| `resolve_existing_issue_target()`                                                   | Existing Issueとexact三文書pathを解決                                       | reuse                  |
| `_read_external_bounded_file()`                                                     | Review/Human external inputのsingle-read、bounded、symlink-safe capture | reuse                  |
| `_review_result_has_sensitive_content()`                                            | Unsafe Review dynamic contentのpre-mutation拒否                         | reuse                  |
| `load_verified_issue_candidate()`                                                   | Exact ZIP snapshot、archive safety、identity、files、SOURCE-BASELINE検証   | reuse                  |
| `VerifiedIssueCandidate.files`                                                      | `requirement.md`、`design.md`、`plan.md` exact bytes                   | reuse                  |
| `validate_candidate_output_directory()`                                             | Existing external non-symlink output boundary                        | reuse                  |
| `run_github_sync_preflight()`                                                       | Fetch、named branch、upstream、local/remote HEAD、clean/source freshness | reuse                  |
| `validate_tree()`                                                                   | Required SpecDock validation                                         | injected closureでreuse |
| `sync_after_import()`                                                               | `force=False`、GitHub fetchなし、active migrationなしのdeterministic sync   | injected closureでreuse |
| `current_branch_or_none()` / `current_head_or_none()` / `origin_github_repo_slug()` | Transaction中の追加Git guards                                            | reuse                  |
| `render_planning_result_text/json()`                                                | 新status/reasonを既存rendererで表示                                         | **read-only**          |
| Existing apply parser/handler                                                       | 現行request構築とgeneric result rendering                                 | **read-only**          |
| `UseCases.planning_apply` fail-closed stub                                          | S06 wiringまで未構成のまま保持                                                 | **read-only**          |

`PlanningHumanDecisionV1`はapproved/rejectedのtruth table、timezone付き`decided_at`、exact Review-result raw bytes SHA、Review identityとの完全一致をすでに検証する。

`PlanningCommandResult`も必要な全statusをすでに持ち、`ready/adoption_published`だけをreadiness success pairとして扱う。

Candidate loaderは単一capture済みZIPからvalidated identity、exact file bytes、source baselineを返すため、S05で別のZIP parserや`extractall()`を追加しない。Candidate inventoryはexact三文書と既存control filesに閉じている。

現行CLIにはapplyのmode、Review、Human decision、expected HEAD、Candidate identity optionsがすでにある。
`UseCases.planning_apply`はまだfail-closed stubであり、S05ではwiringしない。

### 3.1 新しいgeneric primitiveを追加しない理由

現行`infra/git_cli.py`にはread/branch/worktree primitivesはあるが、scoped index transaction、commit、push、remote parityの高位primitiveはない。

したがって、generic Git APIを拡張せず、S05 ownershipを明示した単一module `infra/issue_planning_apply.py`へ必要なdirect-argv Git処理を閉じ込める。

---

## 4. Implementation-local contracts、state machine、operation identity、evidence、retry

### 4.1 Application orchestration boundary

`application/issue_planning.py`へ次のinternal entry pointを追加する。

```python
def run_issue_planning_apply(
    *,
    request: PlanningApplyRequest,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
    repo_slug_resolver: Callable[[Path], str | None],
    validation_runner: Callable[[], ValidationResult],
    sync_runner: Callable[[], SyncCommandResult],
    preflight_runner: Callable[
        [GitHubSyncPreflightRequest], PreflightResult
    ] = run_github_sync_preflight,
    candidate_loader: Callable[
        [Path, Path], VerifiedIssueCandidate
    ] = load_verified_issue_candidate,
    transaction_runner: Callable[..., PlanningApplyExecution],
) -> PlanningCommandResult:
    ...
```

`validation_runner`と`sync_runner`はS05 testでfakeを注入する。S06 wiring時にのみ、次へbindする。

```text
validation_runner:
    validate_tree(ValidateTreeRequest(), ports)

sync_runner:
    sync_after_import(ports)
```

`sync_after_import()`はGitHub fetch、active update、active manifest migrationを行わない既存public sync pathである。

### 4.2 S05-local infra contracts

新規`infra/issue_planning_apply.py`内にのみ、次を置く。

```text
PlanningApplyOperation
- operation_id
- issue_id
- mode
- repository
- branch
- expected_head
- reviewed_identity
- reviewed_identity_sha256
- review_result_sha256
- human_decision_sha256
- decision
- canonical_target_paths
- pre_apply_target_blob_oids
- candidate_identity | None
- decision_artifact_path
- expected_tracked_change_paths
- human_decision_bytes        # repr=False
- replacement_documents       # repr=False; archive approved only
- pre_apply_document_bytes     # repr=False
```

```text
PlanningApplyExecution
- status
- reason
- operation_id
- decision_artifact_path | None
- local_commit | None
- local_tree | None
- remote_commit | None
- details                     # closed content-free codes only
```

```text
execute_planning_apply_transaction(
    operation,
    *,
    repo_root,
    output_dir,
    validation_runner,
    sync_runner,
    fault_hook=None,
) -> PlanningApplyExecution
```

`fault_hook`はtest-only dependency injectionであり、environment variable、CLI option、production registryとして公開しない。

### 4.3 Exact validation order

順序は固定する。後段の証拠があっても、前段を省略しない。

1. Existing Issueをresolveし、exact canonical pathsを取得する。
2. Mode optionsのclosed combinationを再検証する。
3. `expected_head`、`reviewed_head`、SHA入力をlowercase fixed-length形式として検証する。
4. External output directoryを既存guardで検証する。
5. Review-result fileを一度だけbounded readする。
6. Human-decision fileを一度だけbounded readする。
7. Exact Review bytesをparseする。
8. Exact Human bytesを、exact Review bytesを渡してparseする。
9. Review/Human issue、mode、identity、identity SHA、request issueを一致させる。
10. Request `expected_head == reviewed_identity.source_head`を要求する。
11. Human `approved`の場合だけReview `verdict == pass`を要求する。
12. Human `rejected`の場合はReview verdictにかかわらず、exact bindingが成立すればdecision-only laneへ進める。
13. ArchiveではCLI logical filename/SHAとReview Candidate identityを先に比較する。
14. Actual Candidate ZIPをsingle snapshotでloadし、Review Candidate identityと完全一致させる。
15. Git-boundではexact canonical path tupleと`reviewed_head`を一致させる。
16. Repository slug、branch、local HEAD、fetched remote HEAD、upstreamをpreflightする。
17. ArchiveではCandidate `SOURCE-BASELINE.json`のcanonical/relevant pathsに対し、exact `source_manifest_hash`を再検証する。
18. Git-boundではreviewed HEADの三blobとcurrent三文書bytesを比較する。
19. Exact operation identityを計算する。
20. 同一operationの既存external manifestがあればretry pathへ入る。
21. 新規operationだけmutation transactionを開始する。

### 4.4 Stable result mapping

| Condition                                          | Status                    | Reason                         |
| -------------------------------------------------- | ------------------------- | ------------------------------ |
| Review file missing/unreadable                     | `blocked`                 | `review_result_unavailable`    |
| Human file missing/unreadable                      | `blocked`                 | `human_decision_unavailable`   |
| Approvalに対してReviewがfail                            | `blocked`                 | `review_not_passed`            |
| Detached/dirty/no valid upstream等                  | `blocked`                 | `git_preflight_blocked`        |
| Malformed mode/options                             | `rejected`                | `apply_request_rejected`       |
| Malformed/unsafe Review                            | `rejected`                | `review_result_rejected`       |
| Malformed/unbound Human decision                   | `rejected`                | `human_decision_rejected`      |
| CLI Candidate filename/SHAがreviewed identityと不一致   | `rejected`                | `candidate_identity_rejected`  |
| Review mode/HEAD/path identity mismatch            | `rejected`                | `review_identity_rejected`     |
| Unsafe Candidate archive                           | `rejected`                | `archive_rejected`             |
| Non-owned output/operation collision               | `rejected`                | `apply_output_rejected`        |
| Existing operation core mismatch                   | `rejected`                | `operation_identity_collision` |
| Current HEAD/source/Candidate/target drift         | `stale`                   | `apply_target_changed`         |
| Archive skip proof不足                               | `stale`                   | `fresh_review_required`        |
| Apply中semantic mutation、restore成功                  | `rolled_back`             | `adoption_semantic_mutation`   |
| Candidate/canonical parity failure、restore成功       | `rolled_back`             | `candidate_parity_failed`      |
| Tracked diff outside scope、restore成功               | `rolled_back`             | `apply_diff_out_of_scope`      |
| Validation failure、restore成功                       | `rolled_back`             | `specdock_validation_failed`   |
| Sync failure/scope violation、restore成功             | `rolled_back`             | `specdock_sync_failed`         |
| Commit未成立、restore成功                                | `rolled_back`             | `planning_commit_failed`       |
| Exact restoreを証明できない                               | `recovery_required`       | `restore_mismatch`             |
| Commit後push失敗                                      | `publication_pending`     | `push_failed`                  |
| Commit後remote parity未確認                            | `publication_pending`     | `remote_parity_unconfirmed`    |
| Retry時remoteが別commitへ進行                            | `blocked_remote_diverged` | `remote_diverged`              |
| Approved adoptionとremote parity完了                  | `ready`                   | `adoption_published`           |
| Rejected decision-only publicationとremote parity完了 | `rejected`                | `plan_rejected`                |

Canonical result statusesとPA-NF exact expectationsはRequirementですでに固定されている。

### 4.5 Operation identity

次のcore objectをcanonical JSON化する。

```json
{
  "schema_version": "spec-dock.issue-planning-apply-operation.v1",
  "issue_id": "iss-00334",
  "mode": "archive-candidate|git-bound",
  "repository": "owner/repo",
  "branch": "branch",
  "expected_head": "<40-hex>",
  "reviewed_identity": {},
  "reviewed_identity_sha256": "<64-hex>",
  "review_result_sha256": "<64-hex>",
  "human_decision_sha256": "<64-hex>",
  "decision": "approved|rejected",
  "canonical_target_paths": [],
  "pre_apply_target_blob_oids": {
    "<repo-relative-path>": "<git-blob-oid>"
  },
  "candidate_identity": null
}
```

Canonical encoding:

```text
UTF-8
ensure_ascii=False
sort_keys=True
separators=(",", ":")
allow_nan=False
single trailing LF
```

```text
operation_id = sha256(canonical_operation_core_bytes)
```

Host-private absolute paths、output directory、temporary filename、PID、random valueはoperation identityへ含めない。

Decision artifact pathはoperation IDから決定的に導出する。

```text
<issue-dir>/artifacts/
<decided_at UTC yyyymmddtHHMMSSz>-planning-human-decision-<operation_id[0:16]>.json
```

Artifact内容は**入力されたexact Human-decision bytesそのもの**とする。JSON再serialize、pretty-print、field reorder、newline補正をしない。

### 4.6 Evidence layout

Validated external output directoryの下だけに置く。

```text
planning-apply-<operation_id>/
├── operation.json
├── state.json
├── attempts/
│   └── <utc>-<nonce>.json
├── transaction/
│   ├── backup-manifest.json
│   ├── git-index.bin
│   ├── files/
│   │   └── <sha256(repo-relative-path)>.bin
│   └── managed-state/
│       └── <sha256(repo-relative-path)>.bin
├── commit.json
└── publication.json
```

Rules:

* Operation directory: mode `0700`
* Evidence/backup files: mode `0600`
* `operation.json`: immutable、atomic no-replace
* `commit.json`: local commit確定後にimmutable publish
* `publication.json`: remote parity確定後にimmutable publish
* `state.json`: owned fileとしてatomic replacement
* Attempt receipts: append-only、atomic no-replace
* Result/evidenceへraw Review findings、raw Git stderr、credential、token、private absolute pathを出さない
* Backup bytesはtransaction recovery専用であり、successまたはexact rollback後に削除する
* `recovery_required`の場合だけprivate backupを保持し、resultにはabsolute recovery pathを出さない
* Repository-wide registry、custom ref、別workspace locatorは作らない

### 4.7 Unified state machine

```text
INPUT_VALIDATED
  -> FRESH
  -> OPERATION_RECORDED
  -> BACKED_UP
  -> MUTATING
  -> CANONICAL_PROOF
  -> VALIDATED
  -> SYNCED
  -> DIFF_PROOF
  -> STAGED
  -> COMMITTED
  -> PUSHED
  -> REMOTE_PARITY
  -> READY | REJECTION_RECORDED
```

#### Pre-mutation

`INPUT_VALIDATED`または`FRESH`までの失敗はrepositoryへ書かない。

* `blocked`
* `rejected`
* `stale`

#### Mutation開始後、commit前

次をreverse orderでrestoreする。

1. Managed SpecDock sync state
2. Canonical三文書
3. Decision artifactの作成前不存在
4. Raw Git index bytesとmode

その後、次をすべて証明する。

```text
HEAD == expected_head
canonical bytes == backup bytes
decision path == absent
Git index SHA/mode == backup
managed state == backup inventory/bytes
git status --porcelain=v2 -z == empty
remote-tracking HEAD == expected_head
```

一致すれば`rolled_back`。一つでも証明不能なら`recovery_required/restore_mismatch`。

`git reset`は使用しない。

#### Commit後

Commit後はworktree/indexをpre-operationへ戻さない。

* Pushまたはremote observation失敗: `publication_pending`
* Commitは保持
* Amend/reset/new commitを作らない
* 同一operation retryだけを許可

Commit commandがnonzeroでも、直後のHEADがoperation commitへ進んでいる場合はcommit済みとして扱う。HEADが不明な別commitへ移動した場合は自動継続せず`recovery_required/unexpected_local_head`とする。

### 4.8 Archive mode

Approved archive operationでは次を行う。

1. `load_verified_issue_candidate()`が返した単一captured snapshotをauthorityとする。
2. `VerifiedIssueCandidate.files`から三文書だけをprivate stageへ書く。
3. Generic ZIP再読込、filesystem scan、`extractall()`をしない。
4. Staged bytes SHAをCandidate entry SHAと比較する。
5. Current三文書bytes/modeをbackupする。
6. Exact Human decision bytesをnew artifactとしてstageする。
7. 三文書をdeterministic orderでatomic whole-file replaceする。
8. Existing modeを保持し、fileとparent directoryをfsyncする。
9. 各canonical fileがCandidate entry bytesと完全一致することを証明する。
10. Candidate外tracked diffがないことを証明する。
11. Validation、sync、final diff proof、Git stagingへ進む。

Expected tracked change setは次で決定する。

```text
{decision_artifact_path}
UNION
{
  canonical_path
  for canonical_path
  if candidate_bytes != pre_apply_bytes
}
```

Candidateと同一bytesのdocumentはwhole-file replacementを実行しても、commit change setには含めない。

Rejected archive operationではCandidate identityとReview/Human bindingまで検証するが、三文書をstageまたはreplaceしない。Decision artifactだけをtransaction、validation、sync、commit、pushする。

### 4.9 Git-bound mode

1. `reviewed_head == expected_head == reviewed_identity.source_head`
2. `reviewed_identity.canonical_target_paths == resolved exact three paths`
3. `git ls-tree`でreviewed HEADの三target blob OIDsを取得する。
4. Current three filesをdescriptor-safeに一度読み、Git blob OIDを計算する。
5. Current OIDがreviewed OIDと完全一致することを要求する。
6. 三文書へwrite、touch、replaceを行わない。
7. Decision artifactだけを作る。
8. Expected tracked change setはexact decision artifact path一つとする。
9. Validation、sync、commit、push、remote parityはarchiveと同じtransactionを通す。

### 4.10 SpecDock validation and sync

Validation:

```text
validation_result.report.errors == []
```

Sync:

```text
sync_result.artifact_failure is None
sync_result.state.deps_preflight_error is None
```

Syncはmanaged derived stateだけを変更できる。現行writerが生成する主なstateは`.agent` index/tree、PlantUML、dashboardであり、これらはrepositoryでignored managed stateになっている。

S05 transactionが許可するmanaged sync inventory:

```text
spec-dock/.agent/index-all.json
spec-dock/.agent/index.json
spec-dock/.agent/tree-all.json
spec-dock/.agent/tree.json
spec-dock/.agent/deps-issues.json
spec-dock/tree-all.puml
spec-dock/tree.puml
spec-dock/deps-issues.puml
spec-dock/deps-raw.puml
spec-dock/dashboard.md
spec-dock/adrs/**
```

Existing syncのlegacy cleanup対象:

```text
spec-dock/.agent/deps.json
spec-dock/.agent/deps.puml
spec-dock/.agent/deps.todo.puml
spec-dock/.work/state.json
spec-dock/.work/index.json
spec-dock/.work/tree.json
```

Rules:

* Managed stateをpre-syncにbounded snapshotする。
* `ArtifactWriteResult`が返すpathsをexpected inventoryと比較する。
* 上記外のfilesystem mutationを検出したらrollbackする。
* Managed stateをGit stageまたはcommitしない。
* Rollback時はexact prior inventory、bytes、symlink target、absenceを復元する。
* Snapshot上限を超える場合はmutation前に`blocked/managed_state_snapshot_rejected`とする。

### 4.11 Git index、commit、push

#### Git index

* `git rev-parse --git-path index`でcurrent worktreeのindexを解決する。
* Regular non-symlink fileであることを要求する。
* Raw bytes、mode、SHA-256をbackupする。
* Exact restoreを証明できないsplit/shared-index configurationはmutation前にfail closedする。
* Stageは次だけ。

```text
git add -- <exact expected tracked change paths>
```

* `git diff --cached --name-only -z --no-renames`がexpected setと完全一致することを要求する。
* `git write-tree`でpre-commit staged treeを固定する。

#### Planning-only commit

Approved:

```text
docs(<issue-id>): adopt reviewed planning

SpecDock-Planning-Operation: <operation_id>
```

Rejected:

```text
docs(<issue-id>): record rejected planning decision

SpecDock-Planning-Operation: <operation_id>
```

Rules:

* Direct argv
* Shellなし
* `--amend`なし
* `--no-verify`なし
* Commit parentはexact `expected_head`
* Commit changed pathsはexpected tracked change setと完全一致
* Commit treeはpre-commit `git write-tree`結果と一致

#### Push

```text
git push origin HEAD:refs/heads/<current-branch>
```

禁止:

```text
--force
--force-with-lease
+
delete ref
custom ref
```

Push後にfetch/observeし、次を要求する。

```text
local HEAD == fetched remote branch HEAD
local HEAD tree == fetched remote branch tree
commit parent == expected_head
operation trailer == operation_id
```

### 4.12 Same-operation retry

Retryはexact operation manifestを再構成し、既存`operation.json`とbyte-equivalentであることを要求する。

#### `commit.json`がない場合

* Repository/indexがpre-operation baselineなら、新しいattemptとしてvalidationから再開できる。
* Backupが残りrepositoryがbaselineでなければ、restoreを一度だけ試す。
* Exact restore成功: `rolled_back`
* Exact restore不能: `recovery_required`

#### `commit.json`がある場合

Recorded local commitについて、parent、tree、changed paths、operation trailerを再検証する。

| Fetched remote branch              | Action                                          |
| ---------------------------------- | ----------------------------------------------- |
| `remote == local_operation_commit` | Tree parityを確認しterminal resultへ収束               |
| `remote == expected_head`          | 同じlocal commitをnormal pushしparity確認             |
| `remote`取得不能                       | `publication_pending/remote_parity_unconfirmed` |
| `remote`が上記以外                      | `blocked_remote_diverged/remote_diverged`       |

Retry中に新しいcommit、amend、reset、rebase、force pushを行わない。

### 4.13 Archive Review-skip rule

Archive Review後の二度目の完全Semantic Reviewを省略できるのは、次がすべて証明済みの場合だけ。

```text
current local HEAD == Candidate source_head
fetched remote HEAD == Candidate source_head
current branch/repository == Candidate identity
Candidate ZIP bytes/SHA/filename == reviewed Candidate identity
Review exact bytes == Human-bound Review digest
Review identity == Human identity
Candidate SOURCE-BASELINE source_manifest_hash == fresh source manifest
unexpected tracked Candidate-external diff == 0
canonical bytes == Candidate document bytes
SpecDock validation == pass
SpecDock sync == pass
```

一つでも不足した場合:

* Mutation前: `stale/fresh_review_required`
* Mutation後: exact rollbackし、該当する`rolled_back` reason
* 次のaction: new Candidateまたはfresh git-bound Review
* PASS継承、Review registry探索、別thread探索はしない

Canonical Review-skip条件はRequirementに明記されている。

---

## 5. Exact write allowlists

### 5.1 Implementation patch allowlist

Dev workerが変更してよいrepository pathsはexactly次の5件。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
tests/unit/application/test_issue_planning_apply.py
tests/unit/infra/test_issue_planning_apply.py
tests/integration/test_issue_planning_apply.py
```

1件でも追加変更が必要ならSTOPする。

### 5.2 Explicit read-only paths

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py
src/spec_dock/assets/install_root/**
spec-dock/**
pyproject.toml
```

特にcanonical `requirement.md`、`design.md`、`plan.md`、`report.md`をworkerが編集しない。

### 5.3 Product runtime repository mutation allowlist

#### Approved archive

```text
exact resolved requirement.md       # Candidate bytesがbaselineと異なる場合のみcommit change
exact resolved design.md            # 同上
exact resolved plan.md              # 同上
exact derived Human decision artifact
```

#### Approved git-bound

```text
exact derived Human decision artifact
```

#### Rejected decision

```text
exact derived Human decision artifact
```

#### Transaction-owned non-commit state

```text
current Git index file
external planning-apply-<operation_id>/**
declared managed SpecDock sync inventory
```

その他のtracked、untracked、ignored filesystem mutationはすべてscope violationとする。

---

## 6. Red-first test matrix

### 6.1 Common postcondition notation

```text
H0 = pre-operation local HEAD
R0 = pre-operation remote branch HEAD
I0 = pre-operation raw Git index bytes/mode
D0 = pre-operation canonical three-document bytes
M0 = pre-operation managed sync state
H1 = exact Planning operation commit
T1 = H1 commit tree
```

全testで必ず次を記録する。

* `result.status`
* `result.reason`
* `result.is_ready`
* canonical document hashes
* decision artifact presence/bytes
* raw Git index SHA/mode
* local HEAD
* local tree
* remote branch HEAD/tree
* `git status --porcelain=v2 -z`
* executed Git argv log
* force/reset/amend/custom-ref call count

### 6.2 Positive and rejection paths

| Test                                                                   | Condition                                           | Expected                                        | Required postcondition                                                   |
| ---------------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------ |
| `test_archive_approved_apply_is_ready_only_after_remote_parity`        | PASS Review＋approved Human＋fresh Candidate          | `ready/adoption_published`                      | canonical == Candidate、decision exact、HEAD=remote=H1、tree=T1、index clean |
| `test_git_bound_approved_apply_preserves_three_documents`              | PASS Review＋approved Human＋unchanged reviewed blobs | `ready/adoption_published`                      | D0 unchanged、decision exact、HEAD=remote=H1                               |
| `test_archive_rejected_decision_publishes_decision_only`               | exact archive Review＋rejected Human                 | `rejected/plan_rejected`                        | D0 unchanged、decision committed、HEAD=remote=H1、not ready                 |
| `test_git_bound_rejected_decision_publishes_decision_only`             | exact git-bound Review＋rejected Human               | `rejected/plan_rejected`                        | D0 unchanged、decision committed、HEAD=remote=H1、not ready                 |
| `test_ready_requires_commit_and_tree_parity_not_only_remote_head_name` | remote ref observation without tree proof           | `publication_pending/remote_parity_unconfirmed` | H1 retained、no ready                                                     |

### 6.3 PA-NF independent named tests

| Fixture / exact test                                          | Condition                            | Exact expected result                           | Postcondition                           |
| ------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------- | --------------------------------------- |
| `test_pa_nf_01_archive_review_only_is_blocked`                | Archive Reviewのみ                     | `blocked/human_decision_unavailable`            | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_02_git_bound_review_only_is_blocked`              | Git-bound Reviewのみ                   | `blocked/human_decision_unavailable`            | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_03_human_decision_only_is_blocked`                | Human decisionのみ                     | `blocked/review_result_unavailable`             | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_04_parity_only_is_blocked`                        | HEAD/tree parityのみ                   | `blocked/review_result_unavailable`             | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_05_wrong_candidate_filename_is_rejected`          | Wrong logical filename               | `rejected/candidate_identity_rejected`          | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_05_wrong_candidate_sha_is_rejected`               | Wrong ZIP SHA                        | `rejected/candidate_identity_rejected`          | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_06_wrong_reviewed_head_is_rejected`               | Wrong reviewed HEAD                  | `rejected/review_identity_rejected`             | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_06_wrong_target_paths_are_rejected`               | Wrong canonical paths                | `rejected/review_identity_rejected`             | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_07_source_drift_is_stale`                         | Source HEAD/manifest drift           | `stale/apply_target_changed`                    | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_07_candidate_drift_is_stale`                      | Candidate actual bytes drift         | `stale/apply_target_changed`                    | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_07_git_target_drift_is_stale`                     | Reviewed blob/current bytes drift    | `stale/apply_target_changed`                    | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_08_semantic_mutation_rolls_back`                  | Replace中にcanonical semantic mutation | `rolled_back/adoption_semantic_mutation`        | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_09_candidate_parity_failure_rolls_back`           | Candidate/canonical parity false     | `rolled_back/candidate_parity_failed`           | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_10a_validation_failure_rolls_back`                | Validation error                     | `rolled_back/specdock_validation_failed`        | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_10a_sync_failure_rolls_back`                      | Sync artifact failure                | `rolled_back/specdock_sync_failed`              | H0/R0/I0/D0/M0 exact                    |
| `test_pa_nf_10b_push_failure_is_publication_pending`          | Commit後push nonzero                  | `publication_pending/push_failed`               | local H1、remote R0、index clean、commit保持 |
| `test_pa_nf_10b_remote_parity_failure_is_publication_pending` | Push後fetch/parity不明                  | `publication_pending/remote_parity_unconfirmed` | local H1、remote unconfirmed、commit保持    |

全PA-NF testで次を共通assertする。

```python
assert result.is_ready is False
assert (result.status, result.reason) != ("ready", "adoption_published")
```

### 6.4 Fault-injection and recovery tests

Injection checkpointは少なくとも次を持つ。

```text
after_operation_recorded
after_decision_write
after_requirement_replace
after_design_replace
after_plan_replace
after_canonical_proof
after_validation
after_sync
after_diff_proof
after_index_stage
before_commit
after_commit
before_push
after_push
after_fetch
during_restore
after_restore
```

Required tests:

| Test                                                            | Fault                            | Expected                                          |
| --------------------------------------------------------------- | -------------------------------- | ------------------------------------------------- |
| `test_each_replacement_checkpoint_restores_exact_state`         | 各document replace後exception      | `rolled_back/*`                                   |
| `test_fault_after_index_stage_restores_raw_index_bytes`         | Stage後exception                  | `rolled_back/*`、I0 exact                          |
| `test_commit_failure_with_unchanged_head_rolls_back`            | `git commit` nonzero、HEAD=H0     | `rolled_back/planning_commit_failed`              |
| `test_commit_nonzero_but_matching_commit_is_publication_state`  | commit command不明終了、HEAD=valid H1 | push/retry laneへ進む                                |
| `test_restore_byte_mismatch_requires_recovery`                  | Restore後canonical mismatch       | `recovery_required/restore_mismatch`              |
| `test_restore_index_mismatch_requires_recovery`                 | I0不一致                            | `recovery_required/restore_mismatch`              |
| `test_restore_managed_state_mismatch_requires_recovery`         | Managed state不一致                 | `recovery_required/restore_mismatch`              |
| `test_post_commit_unexpected_worktree_change_requires_recovery` | Hookがunexpected fileを変更          | `recovery_required/post_commit_workspace_changed` |
| `test_sync_scope_violation_rolls_back`                          | Syncがmanaged inventory外を書く       | `rolled_back/specdock_sync_failed`                |

### 6.5 Retry and divergence tests

| Test                                                         | Initial state                   | Expected                                        |
| ------------------------------------------------------------ | ------------------------------- | ----------------------------------------------- |
| `test_same_operation_retry_pushes_recorded_commit`           | local H1、remote R0              | 同じH1をnormal push、terminal result                |
| `test_same_operation_retry_accepts_already_published_commit` | local H1、remote H1              | 新commit/pushなし、parity後terminal result           |
| `test_retry_does_not_duplicate_decision_artifact`            | decision artifact already in H1 | exact one artifact                              |
| `test_retry_does_not_create_second_commit`                   | `commit.json`あり                 | local commit count増加0                           |
| `test_retry_remote_divergence_is_blocked`                    | local H1、remote D≠H1/R0         | `blocked_remote_diverged/remote_diverged`       |
| `test_retry_unavailable_remote_remains_pending`              | fetch unavailable               | `publication_pending/remote_parity_unconfirmed` |
| `test_operation_manifest_mismatch_is_rejected`               | 同じoperation dirに別core           | `rejected/operation_identity_collision`         |

全retry testsでGit argv logに次がないことを確認する。

```text
--force
--force-with-lease
reset
commit --amend
rebase
update-ref refs/spec-dock/**
```

### 6.6 Review-skip tests

| Test                                                         | Condition               | Expected                      |
| ------------------------------------------------------------ | ----------------------- | ----------------------------- |
| `test_archive_review_skip_requires_all_canonical_proofs`     | 全proof成立                | Reviewer call 0、apply継続       |
| `test_archive_review_skip_rejects_source_manifest_drift`     | Relevant source drift   | `stale/fresh_review_required` |
| `test_archive_review_skip_rejects_candidate_external_diff`   | Undeclared tracked diff | `stale/fresh_review_required` |
| `test_archive_review_skip_rejects_candidate_identity_drift`  | Actual ZIP drift        | `stale/apply_target_changed`  |
| `test_archive_review_skip_failure_after_mutation_rolls_back` | Proof後にparity破壊         | `rolled_back/*`               |

### 6.7 Security and exact-byte tests

* Review symlink、inside-repository path、oversize、invalid UTF-8、duplicate JSON key
* Human decision symlink、inside-repository path、oversize、invalid UTF-8、duplicate JSON key
* Review SHA is exact raw-byte digest、semantic reserialization digestではない
* Human decision artifact bytes equal input bytes exactly
* Candidate ZIP path alias `(N)`は既存closed alias contractに従う
* Decision artifact collisionは同一operation exact bytes以外拒否
* Git argvはlist形式のみ
* Result/evidenceにraw stderr、token、credential、absolute pathがない
* Transaction backup permissions `0700/0600`
* Managed-state snapshot bounds超過はmutation前block

### 6.8 Fake remote integration topology

各integration testは一時directory内だけで次を構築する。

```text
bare origin.git
working repository
named feature branch
origin/<feature branch> upstream
initial H0 commit
exact Issue tree
external evidence directory
```

Network、GitHub API、real credentialsを使用しない。

各result classのpostcondition:

| Result class                           | Repository/index/HEAD/remote                                     |
| -------------------------------------- | ---------------------------------------------------------------- |
| `blocked` / input `rejected` / `stale` | H0/R0/I0/D0/M0 exact                                             |
| `rolled_back`                          | H0/R0/I0/D0/M0 exact、decision absent                             |
| `recovery_required`                    | 自動継続停止、backup retained、remote unchanged、mismatchを明示              |
| `publication_pending`                  | Local H1保持、index clean、commit tree exact、remote R0またはunconfirmed |
| `blocked_remote_diverged`              | Local H1保持、remote divergent commit保持、push mutation 0             |
| `ready`                                | Local=remote=H1、tree parity、index/worktree clean                 |
| published `rejected`                   | Local=remote=H1、D0 unchanged、decision exact、not ready            |

---

## 7. Ordered implementation sequence

### Step 1 — Red: application contract tests

新規`tests/unit/application/test_issue_planning_apply.py`へ、まず以下をRedで追加する。

1. Exact Review/Human bytes binding
2. Approval requires Review pass
3. Rejection selects decision-only lane
4. Mode/request/identity validation
5. Candidate identity request-vs-Review-vs-actual distinction
6. All PA-NF rows
7. `ready` logical conjunction
8. Archive Review-skip gate
9. Stable result/reason mapping
10. No transaction invocation on pre-mutation failure

### Step 2 — Red: transaction unit tests

新規`tests/unit/infra/test_issue_planning_apply.py`へ追加する。

1. Operation identity canonicalization
2. Deterministic decision artifact path
3. External operation directory ownership/collision
4. Exact document/index/managed-state backup
5. Atomic whole-file replacement
6. Exact restore
7. Restore mismatch
8. Diff/stage allowlist
9. Commit parent/tree/path/trailer checks
10. Push/parity/retry state machine
11. Direct argv prohibition matrix
12. All fault checkpoints

### Step 3 — Red: fake remote integration

新規`tests/integration/test_issue_planning_apply.py`へ追加する。

1. Archive approved positive
2. Git-bound approved positive
3. Archive rejected decision-only
4. Git-bound rejected decision-only
5. Precommit rollback
6. Recovery-required
7. Publication pending
8. Retry convergence
9. Remote divergence
10. Per-result repository/index/HEAD/remote postconditions

### Step 4 — Implement S05 transaction adapter

`infra/issue_planning_apply.py`へ、次の順で実装する。

1. Canonical operation core/ID
2. Safe external operation storage
3. Repository/index/managed-state snapshot
4. Exact decision artifact publication
5. Archive whole-file replacement
6. Git-bound blob guards
7. Canonical parity proof
8. Validation/sync wrapper
9. Diff/staging proof
10. Planning-only commit
11. Push/remote parity
12. Retry/recovery

### Step 5 — Implement application orchestration

`application/issue_planning.py`へ`run_issue_planning_apply()`を追加し、既存contracts/readers/loaders/preflightを組み合わせる。

Application layerは次だけを担当する。

* Inputsのexact-byte capture
* Domain contract parse
* Identity/freshness/authorization decision
* Archive/git-bound material construction
* Infra outcomeから`PlanningCommandResult`へのstable mapping

Filesystem mutation、Git index、commit、pushはinfra moduleへ閉じる。

### Step 6 — Green and bounded refactor

* PA-NFを個別selectorでGreen
* Fault testsをGreen
* Fake remoteをGreen
* Existing S01–S04 regressionをGreen
* Static、SpecDock validation/sync、diff/allowlistをGreen
* 5-path allowlist外の変更0を確認

### Step 7 — Handoff

* Real repositoryで新apply commandを実行しない
* Real commit/pushを実行しない
* Patchをuncommitted状態でcode/QA reviewへ渡す
* Milestone commit/push/closureは後続Human-controlled workflowで行う

---

## 8. Required commands

### 8.1 Focused S05

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

PA-NF only:

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_apply.py \
  -k 'pa_nf_'
```

Retry/publication only:

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py \
  -k 'retry or publication_pending or remote_diverg'
```

Rollback/recovery only:

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py \
  -k 'rollback or rolled_back or restore or recovery_required'
```

### 8.2 S01–S04 regression

```bash
uv run pytest -q \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

Existing contract tests already coverHuman/Review/result models and must remain regression-only rather than being rewritten.

### 8.3 Static checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

### 8.4 SpecDock validation and sync

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github --no-update-active
./spec-dock/scripts/spec-dock validate
```

### 8.5 Diff checks

```bash
git diff --check
git status --short --untracked-files=all
```

```bash
git diff --stat -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

### 8.6 Exact implementation allowlist check

```bash
uv run python - <<'PY'
from __future__ import annotations

import subprocess

expected = {
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py",
    "tests/unit/application/test_issue_planning_apply.py",
    "tests/unit/infra/test_issue_planning_apply.py",
    "tests/integration/test_issue_planning_apply.py",
}

def nul_paths(argv: list[str]) -> set[str]:
    raw = subprocess.check_output(argv)
    return {
        item.decode("utf-8")
        for item in raw.split(b"\0")
        if item
    }

tracked = nul_paths(
    ["git", "diff", "--name-only", "-z", "--no-renames", "HEAD"]
)
untracked = nul_paths(
    ["git", "ls-files", "--others", "--exclude-standard", "-z"]
)
actual = tracked | untracked

extra = actual - expected
missing = expected - actual

if extra or missing:
    raise SystemExit(
        "S05 write allowlist mismatch\n"
        f"extra={sorted(extra)}\n"
        f"missing={sorted(missing)}"
    )

print("S05 exact 5-path write allowlist: PASS")
PY
```

### 8.7 Prohibited real publication check

Implementation verification中は、current repositoryで次を実行しない。

```text
git commit
git push
./spec-dock/scripts/spec-dock planning-apply ...
```

Commit/push pathsはtemporary fake repositoryとlocal bare remote内だけでtestする。

---

## 9. Explicit stop conditions

次のいずれかを発見したら実装を停止し、canonical Planを拡張せずminimum unresolved choiceだけを返す。

1. Exact branchまたはHEADが`2e0589e1...1429`から変わっている。
2. `PlanningReviewResult`、`PlanningHumanDecisionV1`、`PlanningCommandResult` schema変更が必要。
3. `PlanningApplyRequest`またはpublic CLI option変更が必要。
4. `UseCases`、bootstrap、provider projection、installed Skill wiringがS05実装に必要。
5. Canonical targetを三文書以外へ拡張する必要がある。
6. Generic authoring-pack behaviorを変更しなければ実装できない。
7. Generic Git lifecycle APIを再設計しなければ実装できない。
8. Raw Git indexをexactly snapshot/restoreできない環境を自動処理しなければならない。
9. Syncがdeclared managed inventory外を変更する。
10. Required transaction backupがbounded limits内に収まらない。
11. Decision artifact parentがmissing、symlink、またはunsafeである。
12. Review/Human/Candidate external pathがrepository内、symlink、oversize、またはrace-safeに読めない。
13. Operation evidence directoryがnon-owned collisionを起こしている。
14. Commit hookがpost-commit unexpected repository mutationを残す。
15. Local operation commitとremote branchがdivergeしている。
16. Force、reset、amend、rebase、custom ref、別workspace探索が必要。
17. Secret、credential、private absolute path、raw backend transcriptをresult/evidenceへ保存する必要がある。
18. Implementation patchが5-path allowlistを超える。
19. `requirement.md`、`design.md`、`plan.md`、`report.md`の変更が必要。
20. S06またはS07能力を先行実装する必要がある。

Canonical Designもpersistent registry、custom Git ref、Human/Review semantics変更をamendment triggerとしている。

---

## 10. Copy-ready bounded `dev-coder` instruction

```text
Repository: chemitaro/spec-dock
Branch: iss-00334-implement-chatgpt-issue-planning-workflow
Required exact HEAD: 2e0589e1e4ce1b123cd30d14c338d07038ed1429
Milestone: S05 — Human Gate and Apply Transaction only
Packet status: GO / review-waived

Before editing:
1. Verify current branch and exact HEAD.
2. Verify the worktree/index are clean.
3. If branch or HEAD differs, STOP.
4. Do not amend requirement.md, design.md, plan.md, report.md, or any S06/S07 asset.

Exact implementation write allowlist:
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
- tests/unit/application/test_issue_planning_apply.py
- tests/unit/infra/test_issue_planning_apply.py
- tests/integration/test_issue_planning_apply.py

Implement one bounded S05 design:

A. Application orchestration
- Add run_issue_planning_apply().
- Read Review and Human decision external files once, with the existing descriptor-safe bounded reader.
- Parse exact PlanningReviewResult bytes.
- Parse PlanningHumanDecisionV1 against those exact Review bytes.
- Validate issue, mode, reviewed identity, identity digest, expected HEAD, Candidate identity or git-bound exact paths.
- Approval requires Review verdict pass.
- Rejection remains decision-only and never changes requirement.md/design.md/plan.md.
- Use existing load_verified_issue_candidate(), run_github_sync_preflight(), validation, sync, and result contracts unchanged.
- Map every result to the stable status/reason table in this packet.

B. S05-local transaction adapter
- Add only infra/issue_planning_apply.py; do not widen generic git_cli.py or application ports.
- Compute deterministic operation_id from canonical JSON containing exact identity and byte digests.
- Store operation evidence only under the validated external output directory.
- Derive one deterministic .json Human-decision artifact path under the Issue artifacts directory.
- Persist exact Human-decision input bytes without reserialization.
- Archive approved: stage and whole-file replace only the exact three Candidate documents, then prove byte parity.
- Git-bound: prove exact reviewed blob/current-byte parity and never write the three documents.
- Rejected: write only the decision artifact.
- Snapshot exact canonical bytes/modes, decision absence, raw Git index bytes/mode, and declared managed SpecDock sync state.
- Restore in reverse order on every post-mutation/pre-commit failure.
- Return rolled_back only after exact restore proof.
- Return recovery_required if any restore proof fails.
- Run required SpecDock validation and deterministic sync.
- Permit only the exact expected tracked change set.
- Stage only exact paths and verify cached path set and git write-tree.
- Create one planning-only commit with exact expected parent/tree/path set and operation trailer.
- Push with normal direct argv only.
- Verify local/remote commit and tree parity before ready.
- Preserve a local commit after push/parity failure and return publication_pending.
- Retry only the same operation:
  remote==local -> finalize;
  remote==expected parent -> push the same commit;
  other remote -> blocked_remote_diverged.
- Never force, force-with-lease, reset, amend, rebase, create a custom ref, search another workspace, or create a registry.

C. Red-first tests
- First add all PA-NF-01–09, 10A, 10B as independent named tests.
- Assert exact status/reason and result.is_ready is False for every PA-NF case.
- Add archive approved, git-bound approved, archive rejected, and git-bound rejected positives.
- Add fault injection after each replacement, validation, sync, staging, commit, push, fetch, and restore phase.
- Add exact raw Git-index restoration tests.
- Add restore mismatch -> recovery_required.
- Add push failure -> publication_pending.
- Add same-operation retry convergence and remote divergence.
- Add archive Review-skip positive and all proof-negative branches.
- Add a local bare fake remote integration suite.
- For every result, assert canonical bytes, decision bytes, raw index state, local HEAD/tree, remote HEAD/tree, and git status postconditions.
- Assert executed Git argv never contains force/reset/amend/rebase/custom-ref operations.

D. Verification
Run:
- focused S05 tests
- PA-NF selector
- rollback/recovery selector
- retry/publication selector
- S01–S04 planning regression
- ruff
- mypy
- SpecDock validate/sync/validate
- git diff --check
- exact 5-path allowlist checker

Do not:
- run planning apply against this repository;
- make a real repository commit;
- push this branch;
- edit provider/install/dogfood projection;
- add docs/help/packaging;
- implement S06 or S07.

Stop rather than expand scope if any contract/public CLI/provider/generic lifecycle/canonical document change becomes necessary.

Expected handoff:
- exact five changed paths only;
- all focused/regression/static/SpecDock/diff/allowlist gates Green;
- no real commit or push;
- concise implementation evidence and any stop reason;
- no patch outside S05.
```

### Packet qualification

* **根拠:** GitHub connectorでrepository、branch、default branch、exact pushed HEADを確認し、canonical Requirement、Design、PlanおよびS01–S04 implementation symbolsを直接確認した。
* **仮定:** S06は、S05で追加したinternal orchestrationへ既存`validate_tree()`と`sync_after_import()`のclosuresをbindする。
* **不確実性:** Local filesystem、Git index形式、hooks、push credential、実際のtest結果は本パケット作成時点では未検証。
* **未検証主張:** 本パケットではpatch作成、test実行、real commit、real pushを行っていない。
