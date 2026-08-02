# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a66b411-5e70-83e8-bd27-1c2c18b35763

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

Continue only as the same dedicated Blue Team author for iss-00334. Use @GitHub to inspect exact remote HEAD 3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc and the attached new formal fresh Red FAIL. Produce bounded replacement-ready blocks only for P1-17, P1-18, P1-19, and P2-05. Make every public status deterministic; separate stage-only clean-H0 orphan handling from repository-visible recovery without adding a broad registry; remove summary-row state operations and make the required owner graph executable and acyclic, including S08, S99, and Final Exit; update the Report ledger. Preserve all previously closed controls, especially P1-11 through P1-16, and the one-Issue/one-branch/one-PR boundary. Do not review for PASS, edit the repository, produce a patch, or create a ZIP. Return verified HEAD/paths, exact Requirement/Design/Plan/Report replacements, traceability impacts, and a non-regression self-check.

## Answer

# 1. Verified remote source and inspected inputs

GitHub connector access succeeded.

| Field                   | Verified value                                        |
| ----------------------- | ----------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                 |
| Default branch          | `main`                                                |
| Current branch          | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Required exact HEAD     | `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc`            |
| Branch comparison       | identical; ahead `0`, behind `0`                      |
| Default-branch fallback | not used                                              |

The exact commit exists and records the prior bounded correction, Assurance rebinding, and Report update.

Canonical Issue directory:

```text
spec-dock/initiatives/
  init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00334-implement-chatgpt-issue-planning-workflow/
```

| Inspected path                                                           | Git blob at exact HEAD                     |
| ------------------------------------------------------------------------ | ------------------------------------------ |
| `requirement.md`                                                         | `cac8d9ec148f63bc85f32473e418195c4eced45f` |
| `design.md`                                                              | `bb380801353d1206aa756ad0e8ae95986326074d` |
| `plan.md`                                                                | `445fc8a633876fc4004adceab1d7eb04fefa6dca` |
| `report.md`                                                              | `c9c9744f8da16f929be9b271ff00a5eeb007f227` |
| `.assurance.json`                                                        | `5a51d98f5d5a24ab50389fa05fb68b9c9e593974` |
| `artifacts/20260727t022302z-chatgpt-fresh-canonical-review-fail.md`      | `306ae3bcdf119984f521b3a11277febda329c863` |
| `artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md` | `97d323fd77574024659c60502d1b17b19a62e6ab` |

The canonical blobs are confirmed directly by GitHub.

The attached fresh Red review identifies only P1-17, P1-18, P1-19, and P2-05 for this correction and explicitly records P1-11 through P1-16 as preserved or closed.

No repository mutation, patch, ZIP, or review verdict is produced below.

# 2. Exact Requirement replacements

## Requirement R-01 — replace all of `### REQ-013 Derived Readiness`

```markdown
### REQ-013 Derived Readiness and Deterministic Public Status

RuntimeはReview、Human decision、mode-specific parity、validation、publicationの論理積を評価し、approved adoptionの全条件成立時だけ`ready`を返す。

Public resultはtext／JSONで同一の`status`と`reason`を持つ。

- `status`の許可値は`ready`、`blocked`、`stale`、`rejected`、`rolled_back`、`publication_pending`、`blocked_remote_diverged`、`recovery_required`だけである。
- `ready`だけexit `0`、それ以外はexit `1`である。
- `reason`はDesignで定義するclosed snake-case reason codeであり、同じnamed observable conditionは常に同じ`status`／`reason`へ写像する。
- named acceptance fixtureは一つのexact expected statusを持ち、`A|B`、`A or B`、generic nonzero、generic failureを期待値にしない。
- 一つのinvocationに複数の不成立条件がある場合はDesignのordered classificationで最初に成立した条件だけをpublic resultへ使用する。

Stable status classes:

| Observable class | Required status |
|---|---|
| malformed／contradictory CLI、unsafe path、prohibited content、malformed Planner／Review／Human data、schema／identity／digest mismatch、Review mutation、unsafe archive | `rejected` |
| unknown Issue、dirty tree、upstream欠落またはremote access unavailable、required Review／Human source欠落、backend missing／timeout／nonzero、Review `fail` + Human `approved`、verified rejected-decision publication | `blocked` |
| local／remote HEAD不一致、expected HEAD不一致、branch／upstream source identity不一致、Candidate／reviewed target drift、published rejection後のold H0-bound evidence | `stale` |
| repository mutation開始後のpre-commit faultでexact baseline restoreに成功 | `rolled_back` |
| restore不一致、same-output manifest不整合、またはrepository-visible partial operationに必要なoriginal recovery workspaceを安全に取得できない | `recovery_required` |
| exact local H1 commitが存在するがpush／response／remote verificationが未完了 | `publication_pending` |
| retry時のremote／tree／operation identity divergence | `blocked_remote_diverged` |
| approved adoptionのReview／Human／parity／validation／remote publicationが全成立 | `ready` |

外部workspaceだけへstageした後、repository／index／HEADがexact clean H0のままcrashした状態はrepository-visible partial operationではない。別output invocationからそのorphan workspaceを発見できない場合、それだけを理由に`recovery_required`を返してはならない。RuntimeはDesignのstage-only orphan contractに従い、global registry、home scan、repository-wide workspace scan、custom Git refを新設しない。

operation-local staging／recovery manifestとexternal result JSONは許可するが、専用state database、receipt registry、authority registryを新設しない。
```

## Requirement R-02 — replace all of `### REQ-014 Negative Adoption Fixtures`

```markdown
### REQ-014 Negative Adoption Fixtures

以下を11件の独立named fixtureとして評価する。各fixtureは一つのexact status、exit `1`、readinessなし、下表で許可されたmutation contractだけを持つ。

| ID | Named rejected／non-ready condition | Exact status | Required mutation result |
|---|---|---|---|
| PA-NF-01 | valid archive Review resultだけ。Human source absent | `blocked` | repository mutation 0 |
| PA-NF-02 | valid git-bound Review resultだけ。Human source absent | `blocked` | repository mutation 0 |
| PA-NF-03 | Human approved sourceだけ。Review-result source absent | `blocked` | repository mutation 0 |
| PA-NF-04 | parityだけ。Review／Human sources absent | `blocked` | repository mutation 0 |
| PA-NF-05 | wrong logical Candidate filenameまたはZIP SHA | `rejected` | repository mutation 0 |
| PA-NF-06 | wrong reviewed HEAD、target paths、Issueまたはgit base | `rejected` | repository mutation 0 |
| PA-NF-07 | validated identity後のsource／Candidate／target drift | `stale` | repository mutation 0 |
| PA-NF-08 | adoption中のsemantic mutationをpre-commitで検出しexact restore成功 | `rolled_back` | baseline exact restore、commit 0 |
| PA-NF-09 | pre-commit parity failureでexact restore成功 | `rolled_back` | baseline exact restore、commit 0 |
| PA-NF-10A | pre-commit validation failureでexact restore成功 | `rolled_back` | baseline exact restore、commit 0 |
| PA-NF-10B | exact H1 commit作成後のpush failureまたはresponse loss | `publication_pending` | local H1保持、automatic reset／amend／force push 0 |

PA-NF-08、PA-NF-09、PA-NF-10Aでrestore自体が失敗するfixtureはPA-NFのstatusを変更せず、EC-006／EC-007の独立`recovery_required` fixtureとして扱う。PA-NF-10AとPA-NF-10Bを一つの代表fixtureまたは一つのgeneric failure countでcloseしない。
```

## Requirement R-03 — replace all of `### AC-010 Adoption Negative Set`

```markdown
### AC-010 Adoption Negative Set

PA-NF-01〜PA-NF-09、PA-NF-10A、PA-NF-10Bを各独立named fixtureとして実行し、11／11でRequirement表のexact status、exit `1`、readinessなし、許可されたmutation contractと一致し、violations 0を得る。

genericな「reject」、generic nonzero、複数statusの許容、PA-NF-10A／10Bの一括closeを代替証拠にしない。
```

## Requirement R-04 — replace the final sentence of `### AC-001 Official Entry and Complete Output`

```markdown
情報不足時はfinal ZIPを作らず、`status=blocked`、`reason=information_insufficient`、exit `1`を返す。
```

## Requirement R-05 — replace the `EC-001` row in `## 7. Error Conditions`

```markdown
| EC-001 | target／Git preflight不成立 | unknown Issueは`blocked: unknown_issue`。dirty treeは`blocked: dirty_tree`。upstream欠落は`blocked: upstream_missing`。remote access unavailableは`blocked: remote_unavailable`。current branch／upstream branch identity不一致は`stale: branch_upstream_mismatch`。local／remote HEAD不一致は`stale: local_remote_mismatch`。expected HEAD不一致は`stale: expected_head_mismatch`。すべてbackend／repository mutation前、exit `1` |
```

# 3. Exact Design replacements and additions

## Design D-01 — replace the current text／JSON status bullet in `## 3. Public Command Design`

```markdown
- text／JSONは同じclosed `status`と`reason`を返す。`status`は`ready|blocked|stale|rejected|rolled_back|publication_pending|blocked_remote_diverged|recovery_required`だけであり、`ready`だけexit `0`、それ以外はexit `1`とする。`failed`、`invalid`、`insufficient evidence`をpublic statusとして追加せず、必要な区別はclosed `reason`で表す。同じnamed observable conditionは常に同じstatus／reasonを返す。
```

## Design D-02 — replace all of `#### 4.4.3 Validation order and stable status semantics`

```markdown
#### 4.4.3 Validation order and deterministic status semantics

`planning apply`は次のordered classificationをrepository mutation前から順に適用する。複数条件が同時に成立する場合は、番号が最も小さい条件だけをpublic `status`／`reason`に使用する。

1. required option／source presence。
2. mode-specific option matrixとpath safety。
3. Review／Human exact file-byte readとdigest。
4. JSON／schema／field validation。
5. reviewed identity validationとdigest再計算。
6. Review／Human／CLI／Issue cross-binding。
7. apply-time source freshness。
8. Review verdict／Human decision combination。
9. recovery-state classification。
10. transaction／publication result。

Pre-mutation mapping:

| Named reason | Status | Exit | Repository mutation |
|---|---|---:|---:|
| `missing_review_source` | `blocked` | 1 | 0 |
| `missing_human_source` | `blocked` | 1 | 0 |
| `malformed_evidence` | `rejected` | 1 | 0 |
| `wrong_schema_version` | `rejected` | 1 | 0 |
| `wrong_evidence_kind` | `rejected` | 1 | 0 |
| `missing_required_key` | `rejected` | 1 | 0 |
| `unknown_key` | `rejected` | 1 | 0 |
| `duplicate_key` | `rejected` | 1 | 0 |
| `invalid_field_type` | `rejected` | 1 | 0 |
| `invalid_enum` | `rejected` | 1 | 0 |
| `invalid_timestamp` | `rejected` | 1 | 0 |
| `invalid_digest` | `rejected` | 1 | 0 |
| `partial_authorization` | `rejected` | 1 | 0 |
| `wrong_reviewer_role` | `rejected` | 1 | 0 |
| `nonfresh_review_declaration` | `rejected` | 1 | 0 |
| `non_read_only_review_authority` | `rejected` | 1 | 0 |
| `mode_mismatch` | `rejected` | 1 | 0 |
| `issue_mismatch` | `rejected` | 1 | 0 |
| `identity_object_mismatch` | `rejected` | 1 | 0 |
| `identity_digest_mismatch` | `rejected` | 1 | 0 |
| `review_result_digest_mismatch` | `rejected` | 1 | 0 |
| `unsafe_decision_destination` | `rejected` | 1 | 0 |
| `unsupported_revocation` | `rejected` | 1 | 0 |
| `source_identity_drift` | `stale` | 1 | 0 |
| `candidate_identity_drift` | `stale` | 1 | 0 |
| `git_target_drift` | `stale` | 1 | 0 |
| `review_failed_for_approval` | `blocked` | 1 | 0 |
| `review_only` | `blocked` | 1 | 0 |
| `human_only` | `blocked` | 1 | 0 |
| `parity_only` | `blocked` | 1 | 0 |
| valid Review `pass` + valid Human `approved` | transaction preflightへ継続 | not yet ready | 0 until staging |
| valid Review `pass|fail` + valid Human `rejected` | decision-record transactionへ継続 | not yet final | 0 until staging |

Post-mutation／publication mapping:

| Named reason | Status | Exit | Required state |
|---|---|---:|---|
| `precommit_fault_restored` | `rolled_back` | 1 | bytes／mode／index／HEAD／clean statusがH0とexact一致 |
| `restore_incomplete` | `recovery_required` | 1 | original recovery workspaceとbounded remediationを保持 |
| `repository_visible_partial_without_workspace` | `recovery_required` | 1 | new mutation 0、original exact outputを要求 |
| `publication_incomplete` | `publication_pending` | 1 | exact local H1保持 |
| `remote_diverged` | `blocked_remote_diverged` | 1 | force／reset／amend／new commit 0 |
| `rejection_record_published` | `blocked` | 1 | decision artifact + exact Planning decision commitだけ |
| `adoption_published` | `ready` | 0 | full readiness conjunction成立 |

stage-only workspace orphanが別output invocationから不可視で、repository／index／HEADがexact clean H0、supplied outputにmanifestがない場合は`repository_visible_partial_without_workspace`に分類しない。§4.6の`new_workspace_attempt`として扱う。

Review-only、Human-only、parity-only、published rejectionでは`ready`を導出しない。mode reinterpretation、waiver、silent fallback、missing-field default、unknown-key ignore、unsupported revocation translationを行わない。
```

## Design D-03 — replace all of `#### Recovery workspace identity` under §4.6

````markdown
#### Recovery workspace identity and bounded observability

1. `--output`はexisting non-symlink directoryとして検証する。
2. `canonical_output_directory`はstrict realpath解決後のabsolute normalized pathとする。
3. `output_directory_identity_sha256 = sha256(UTF-8 bytes of canonical_output_directory)`。
4. `workspace_attempt_id = sha256(canonical JSON of operation_id and output_directory_identity_sha256)`。
5. operation directoryは次のexact pathとする。

```text
<canonical-output-directory>/
  .spec-dock-planning-operations/
    <operation-id>/
```

6. recovery manifestは次のexact pathとする。

```text
<operation-directory>/recovery-manifest.json
```

`RecoveryManifestV1`はcanonical JSONであり、次をexact required fieldsとして持つ。

```text
schema_version = spec-dock.planning-recovery-manifest.v1
operation_id
operation_kind
workspace_attempt_id
output_directory_identity_sha256
issue_id
expected_head
reviewed_identity_sha256
review_result_sha256
human_decision_sha256
decision_artifact_repo_path
phase
targets[
  repo_path,
  before_sha256 or null,
  staged_sha256,
  backup_relative_path or null,
  completed
]
```

manifestはphase／target完了ごとにatomic replacementする。backup locatorはoperation-directory-relative non-symlink pathだけを許可する。

Recovery state classes are closed:

##### A. `workspace_only_stage`

次がすべて成立する状態。

- manifest phaseが`preflight`または`staged`。
- repository targetを一件も変更していない。
-全target `completed=false`。
- 全`backup_relative_path=null`。
- index／worktree／HEADがexact clean H0。
- operation commit trailerが存在しない。

Behavior:

- same exact output invocationはmanifest identityを照合し、owned staged bytesとmanifestを安全にcleanupしてpreflightから再開する。cleanup失敗だけを`recovery_required: stage_orphan_cleanup_failed`とする。
- different／missing output invocationがsupplied outputにmanifestを持たず、repositoryがexact clean H0なら`new_workspace_attempt`として開始できる。別outputを列挙・検索せず、未知のstage-only orphanだけを理由に`recovery_required`を返さない。
- original output workspaceはauthorityを持たないinert orphanである。same-output reuse時にRuntimeがcleanupする。Mainが手動cleanupする場合は、exact known operation path、valid manifest、stage-only phase、completed target 0、backup 0、operation commit 0を確認した場合だけoperation directoryを削除し、その観測結果をCandidate外evidenceへ記録する。
- global orphan registry、home scan、repository-wide output scan、custom Git refを作らない。

##### B. `repository_visible_precommit`

repository／indexはH0から変化しているがcommitは存在せず、current bytesがexact immutable inputsから導出したtransaction prefixと一致する状態。

Transaction prefixは次の順だけを許可する。

```text
decision artifact
→ requirement.md
→ design.md
→ plan.md
```

- same exact outputとvalid manifestがある場合だけrollback／resumeできる。
- different／missing outputでmanifestを取得できない場合は`recovery_required: repository_visible_partial_without_workspace`、exit 1、new operation directory作成 0、new repository mutation 0とする。
- current dirty stateがexact transaction prefixと一致しない場合はrecovery stateと推測せず`blocked: dirty_tree`とする。

##### C. `committed_publication`

exact local H1がoperation trailerとworkspace trailerを持つ状態。

- same output identity、parent H0、tree、operation trailer、workspace trailerが一致する場合だけpush／remote verificationからresumeする。
- different／missing output identityは`recovery_required: committed_operation_workspace_mismatch`とし、new commit／reset／amend／force pushを行わない。
- remote divergenceは`blocked_remote_diverged`とする。

##### D. `clean_new_attempt`

supplied outputにmanifestがなく、repository／index／HEADがexact clean H0で、operation commitも存在しない状態。

- new invocationとして開始できる。
- 他outputの存在を推測またはscanしない。

completed success時はbackupを削除する。completed manifestとexternal result JSONはoperation-local observational evidenceとして保持できるが、readiness authorityにはしない。
````

## Design D-04 — replace all of `### 5.1 Apply State Machine and Transaction Boundary`

````markdown
### 5.1 Apply State Machine and Transaction Boundary

```text
preflight
  → validate all immutable inputs
  → classify recovery state using:
       supplied output workspace
       exact repository/index/HEAD
       exact operation/tree trailers
  → workspace_only_stage at same output:
       cleanup owned stage-only workspace
       restart preflight
  → clean_new_attempt:
       bind new workspace attempt
  → repository_visible_precommit:
       require exact original workspace
       rollback or stop recovery_required
  → committed_publication:
       require exact original workspace
       resume publication or stop
  → if operation_kind = adoption:
       stage decision artifact + canonical replacement set outside repository
    else operation_kind = rejection-record:
       stage decision artifact only outside repository
  → validate staged set
  → backup every existing target byte/mode
  → add decision artifact
  → if adoption:
       replace requirement → design → plan
  → validate exact allowed diff, bytes, parity, and operation kind
  → create one Planning commit with operation/workspace trailers
  → push
  → fetch and verify remote HEAD/tree
  → if adoption: ready
    else rejection-record: blocked
```

- `ScopedFileTransaction`を`infra/scoped_file_transaction.py`へ置き、`runbook_store.py`のcurrent stage／backup／restore behaviorを同primitiveへ移してcharacterization testsを維持する。Issue Planningは同primitiveを使用し、private helperをimportせず同等実装を複製しない。
- mutation前にCandidate／git identity、Review result、Human decision、operation kind、decision destination、clean branch、upstream、local／remote／expected HEAD、workspace safetyを検証する。
- adoptionのallowed diffはnew decision artifactとexact canonical replacement setだけである。
- rejection-recordのallowed diffはnew decision artifact一件だけであり、`requirement.md`、`design.md`、`plan.md`、`.assurance.json`、他artifactを変更しない。
- external staging完了前またはstage-only完了後のcrashでrepositoryがexact clean H0なら、repository rollbackは不要である。same-output retryはowned stage-only workspaceをcleanupして再開する。
- stage-only crash後のdifferent-output invocationは、supplied outputにmanifestがなくrepositoryがexact clean H0ならfresh workspace attemptとして開始できる。unknown original outputをscanせず、false `recovery_required`を生成しない。
- decision artifact追加後からcommit成功前までの例外、validation failure、commit failure、process interruptはreverse-order restoreを試み、new decision artifactを除去し、original bytes／mode／index／HEAD／`git status --porcelain=v1`を照合する。
- restore成功は`rolled_back: precommit_fault_restored`。
- restore不一致は`recovery_required: restore_incomplete`。
- wrong-output retryでrepositoryがexact transaction prefixに一致する場合は`recovery_required: repository_visible_partial_without_workspace`。
- wrong-output retryでdirty stateがtransaction prefixと一致しない場合は`blocked: dirty_tree`。
- commit成功後はautomatic rollback、reset、amend、force pushを行わない。
- push failureまたはresponse lossではlocal H1を保持して`publication_pending: publication_incomplete`を返す。
- same-operation retryはoperation trailer、workspace trailer、exact tree、parent H0、same output identityを照合する。
- wrong output identityを持つpost-commit retryは`recovery_required: committed_operation_workspace_mismatch`とする。
- remoteがH1ならremote verificationへ進む。remoteがH0かつlocal H1がexactならpushをretryする。それ以外は`blocked_remote_diverged: remote_diverged`。
- adoption verified successだけが`ready: adoption_published`。
- rejection-record verified successは`blocked: rejection_record_published`。
- success時はbackupを削除する。external result JSONとcompleted manifestは観測Evidenceであり、readiness authorityはReview、Human approval、canonical parity、validation、local／remote commit/treeから再構成する。
````

## Design D-05 — replace all of `## 11. Security and Failure Handling`

```markdown
## 11. Security and Failure Handling

| Named observable failure | Public result | Recovery |
|---|---|---|
| unknown Issue | `blocked: unknown_issue` | valid Issue IDを選択してnew run |
| dirty tree before operation | `blocked: dirty_tree` | unrelated workを解消しclean H0からnew run |
| upstream missing | `blocked: upstream_missing` | upstreamを設定してnew run |
| remote access unavailable | `blocked: remote_unavailable` | remote accessを復旧してnew run |
| current branch／upstream branch mismatch | `stale: branch_upstream_mismatch` | intended named branchへsource refresh |
| local／remote HEAD mismatch | `stale: local_remote_mismatch` | fetch／reconcile後にfresh identity |
| expected HEAD mismatch | `stale: expected_head_mismatch` | current exact HEADへfresh Review／Human decision |
| information insufficient | `blocked: information_insufficient` | bounded missing contextを補いnew run |
| unsafe Prompt／attachment／output path | `rejected: unsafe_path` | safe external pathを選択 |
| prohibited secret-like content | `rejected: prohibited_content` | prohibited contentを除去。backend call 0 |
| backend missing | `blocked: backend_unavailable` | backendを利用可能にしてsame contractでnew run |
| backend timeout | `blocked: backend_timeout` | bounded diagnostic後にnew run |
| backend nonzero | `blocked: backend_nonzero` | bounded redacted diagnosticに従いnew run |
| malformed／partial Planner response | `rejected: malformed_planner_response` | Semantic rerun／revision。final Candidate 0 |
| unexpected response file | `rejected: unexpected_response_file` | closed three-file responseでrerun |
| non-UTF-8 response | `rejected: non_utf8_response` | valid UTF-8 responseでrerun |
| authority claim in Planner response | `rejected: planner_authority_claim` | authority claimを含まないfresh response |
| unsafe archive／integrity mismatch | `rejected: archive_rejected` | new complete Candidate |
| Review mutation detected | `rejected: review_mutation_detected` | clean stateへ戻しfresh Review |
| Human approved against Review fail | `blocked: review_failed_for_approval` | findings反映後にfresh Review |
| valid Human rejection | decision-record transaction後`blocked: rejection_record_published` | published H1へsource refreshし、後続approvalはfresh Review |
| unsupported Human revocation claim | `rejected: unsupported_revocation` | shared Human／Main stop-or-revert ownerへroute |
| stage-only same-output cleanup failure | `recovery_required: stage_orphan_cleanup_failed` | exact original outputでbounded cleanup |
| repository-visible precommit state + original workspace unavailable | `recovery_required: repository_visible_partial_without_workspace` | exact original outputを再指定 |
| unrelated dirty state during retry | `blocked: dirty_tree` | unrelated workを解消 |
| pre-commit fault + exact restore | `rolled_back: precommit_fault_restored` | clean H0からsame or new run |
| restore incomplete | `recovery_required: restore_incomplete` | automatic continuation禁止 |
| push failure／response loss after H1 | `publication_pending: publication_incomplete` | same operation／workspaceでresume |
| wrong workspace for committed operation | `recovery_required: committed_operation_workspace_mismatch` | exact original outputを再指定 |
| retry remote divergence | `blocked_remote_diverged: remote_diverged` | force／resetせずHuman／Main reconcile |

Classification orderはCLI／path → target／Git → prohibited content → backend → Planner response → Review／Human apply evidence → recovery state → transaction／publicationとする。同じnamed fixtureに複数statusを許可しない。

Sensitive diagnostics are bounded and redacted. Direct argv is default. Shell exception is unavailable without explicit Human-approved Design and rollback evidence.
```

# 4. Exact Plan replacements and additions

## Plan P-01 — replace the Closure Index introduction and the complete `required=no` summary table

````markdown
## 8. Spec-Locked Closure Index

この索引はmaterial obligationsのbounded coverage ledgerであり、全test implementation inventoryやglobal proof registryではない。

### 8.0 Closure graph semantics

`required=no` summary rowはnavigation aliasだけである。

- summary aliasはClosure ownerを持たない。
- summary aliasはowner portion、state、aggregate stateを持たない。
- summary aliasをstep closure contract、S99 closure target、Report closure-state rowとして`open`、`passed`、`failed`、`blocked`、`closed`へ遷移させない。
- test cardはsummary aliasをnavigation referenceとして記載できるが、required closure evidenceの代用にしない。

`required=yes` individual rowだけがexecutable closure nodeである。

Allowed owner order:

```text
S01
< S02A
< S02B
< S03
< S04
< S05
< S06
< S07
< S08
< S09A
< S09B
< S90
< S99
```

`Final Exit`はClosure ownerではない。

- single-owner rowは一つのowner portionを持つ。
- multi-owner rowは上記step orderでsortedされた独立owner portionsを持つ。
- owner portion stateの許可値は`open`、`passed`、`failed`、`blocked`だけである。
- stepはClosure Indexで自身がownerとして列挙されたportionだけを更新できる。
- aggregate stateは全owner portionが`passed`のときだけ`closed`。一つでも`open|failed|blocked`なら`open`。
- 後続drift、invalidated evidence、failed re-reviewは該当portionを再openし、aggregateを再openする。
- step-local testだけ、reviewerだけ、commit候補だけではportionを`passed`にしない。required evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkをすべて要求する。

S99 entryでは、ownerがS01〜S90の全portionが`passed`であることを要求する。S99-owned portionはentry時点で`open`でよい。S99が自身のportionを`passed`にした後、全`required=yes` aggregateが`closed`であることを再計算し、そこで初めてFinal Exitをunblockする。

MainはReportへ次のexact fieldsをowner portionごとに記録する。

```text
closure_id
closure_owner
owner_portion_state
observed_evidence
reviewer_verdict
commit_or_approved_noop
post_commit_clean
recorded_at_head
```

### Summary aliases — navigation only

| Closure ID | Spec link | Navigation meaning | Required | Closure owner | Evidence alias |
|---|---|---|---|---|---|
| `CLOS-CLI` | REQ-002 / AC-002 | command family and parser | no | — | `tc-s01-001`, `tc-s01-004` |
| `CLOS-CREATE` | REQ-004 / AC-001,004 | Planner response and Candidate package | no | — | `tc-s05-001`, `tc-s05-003`, `tc-s05-006` |
| `CLOS-GIT` | REQ-003 / AC-003,017 | Git/source preflight | no | — | `tc-s01-003`, `tc-s03-002` |
| `CLOS-SEC` | REQ-021 / AC-011 | direct argv and prohibited-content preflight | no | — | `tc-s03-003`, `tc-s03-004` |
| `CLOS-REVISION` | REQ-007 / AC-004 | semantic／mechanical revision | no | — | `tc-s04-001`, `tc-s04-002` |
| `CLOS-REVIEW` | REQ-006,008 / AC-005,007 | read-only dual-mode Review | no | — | `tc-s05-001`, `tc-s05-005` |
| `CLOS-ARCHIVE` | REQ-010,022 / AC-006 | Candidate controls and archive safety | no | — | `tc-s05-003`, `tc-s05-004[*]`, `tc-s05-006[*]` |
| `CLOS-ADOPTION` | REQ-009–012 / AC-008,009 | approved adoption／rejected decision record | no | — | `tc-s06-001`, `tc-s06-002`, `tc-s06-009`–`tc-s06-012B` |
| `CLOS-READINESS` | REQ-013,014 / AC-010,013 | typed readiness conjunction and exact non-ready statuses | no | — | `tc-s06-003[*]`, `tc-s08-003[*]` |
| `CLOS-SKILL` | REQ-001,005 / AC-001,011 | Skill／Prompt route | no | — | `tc-s02a-001`, `tc-s02b-001` |
| `CLOS-PROJECTION` | REQ-017,023 / AC-012,015 | install/update projection | no | — | `tc-s07-001`, `tc-s07-002` |
| `CLOS-INTEGRATION` | REQ-019,023 / AC-015 | fake-remote integration and compatibility | no | — | `tc-s08-001`, `tc-s08-002`, `tc-s08-003` |
| `CLOS-DOGFOOD` | REQ-018,024 / AC-014 | hermetic and Human/Main dogfood gates | no | — | `tc-s09a-001`, `tc-s09b-001` |
| `CLOS-DOCS` | REQ-020 / AC-016 | docs and delivery-boundary alignment | no | — | `tc-s90-001` |
| `CLOS-QUALITY` | AC-001–017 / EC-001–010 | final issue-wide quality | no | — | `tc-s99-001`, `tc-s99-002` |
````

## Plan P-02 — replace the indicated Requirement Closure rows

```markdown
| `CLOS-REQ-013` | REQ-013 / AC-008–010,013 | all named readiness and status conditions | only full approved conjunction returns `ready`; each named non-ready condition has one exact status／reason; stage-only orphan is not false recovery | partial gate／nondeterministic status／false recovery | S06/S08 | yes | red-required | `tc-s06-003[11 fixtures]`, `tc-s06-012A`, `tc-s06-012B`, `tc-s08-003[11 fixtures]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-014` | REQ-014 / AC-010 | PA-NF-01〜09、10A、10B | 11／11 exact status、exit 1、allowed mutation only | grouped negative hides validation or publication gap | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01..10b]`, `tc-s08-003[pa-nf-01..10b]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-020` | REQ-020 / AC-016 | one Issue／branch／Delivery PR contract and pre-handoff evidence | S90 aligns docs; S99 verifies final branch／handoff preconditions; Final Exit owns no Closure portion | delivery cycle／Final Exit circularity／issue-level policy rewrite | S90/S99 | yes | inspect-only + final-required | `tc-s90-001`, `tc-s99-001`, `tc-s99-002` | `report.md#Final-Quality-Gate` |
```

## Plan P-03 — replace `CLOS-EC-001`

```markdown
| `CLOS-EC-001` | EC-001 | named target／Git fixtures | unknown Issue／dirty tree／upstream or remote unavailable=`blocked`; branch/upstream、local/remote、expected HEAD mismatch=`stale`; backend/mutation 0 | arbitrary blocked/stale classification／wrong source execution | S01/S03 | yes | red-required | `tc-s01-002`, `tc-s01-003`, `tc-s03-002[git-preflight-*]` | `report.md#Test-Contract-Closure` |
```

## Plan P-04 — replace all of `### 8.3 PA-NF Closure`

```markdown
### 8.3 PA-NF Closure

| Closure ID | Spec link | Named input/state | Exact locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-PA-NF-01` | PA-NF-01 | archive Review only | `blocked: missing_human_source`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01]`, `tc-s08-003[pa-nf-01]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-02` | PA-NF-02 | git Review only | `blocked: missing_human_source`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-02]`, `tc-s08-003[pa-nf-02]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-03` | PA-NF-03 | Human approved only | `blocked: missing_review_source`, exit 1, mutation 0 | approval-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-03]`, `tc-s08-003[pa-nf-03]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-04` | PA-NF-04 | parity only | `blocked: missing_review_source`, exit 1, mutation 0 | parity-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-04]`, `tc-s08-003[pa-nf-04]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-05` | PA-NF-05 | wrong archive identity | `rejected: identity_object_mismatch`, exit 1, mutation 0 | Candidate substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-05]`, `tc-s08-003[pa-nf-05]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-06` | PA-NF-06 | wrong git identity／base | `rejected: identity_object_mismatch`, exit 1, mutation 0 | git target substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-06]`, `tc-s08-003[pa-nf-06]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-07` | PA-NF-07 | source drift | `stale: source_identity_drift`, exit 1, mutation 0 | stale approval reuse | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-07]`, `tc-s08-003[pa-nf-07]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-08` | PA-NF-08 | semantic mutation + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | post-review meaning drift | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-08]`, `tc-s08-003[pa-nf-08]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-09` | PA-NF-09 | parity failure + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | partial canonical adoption | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-09]`, `tc-s08-003[pa-nf-09]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-10A` | PA-NF-10A | validation failure + successful restore | `rolled_back: precommit_fault_restored`, exit 1, exact H0 | validation failure treated ready | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-10a]`, `tc-s08-003[pa-nf-10a]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-10B` | PA-NF-10B | H1 commit + publication failure | `publication_pending: publication_incomplete`, exit 1, local H1 retained | commit loss／false ready | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-10b]`, `tc-s08-003[pa-nf-10b]` | `report.md#Test-Contract-Closure` |
```

## Plan P-05 — add after `### 8.5 Design-risk Closure`

```markdown
### 8.6 Final-quality and Closure-graph Closure

| Closure ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Closure owner | Required | Evidence level | Closure evidence / verification | Evidence destination |
|---|---|---|---|---|---|---|---|---|---|
| `CLOS-S99-001` | AC-001–017 / EC-001–010 / Plan §8 | all pre-S99 owner portions、full diff、tests/build/validate、closure graph | non-S99 portions passed before entry; S99 portions pass during S99; owner graph is valid and acyclic; all required aggregates closed before Final Exit | circular gate／summary-row state／undeclared owner／focused-only Green | S99 | yes | final-required | `tc-s99-001`, `tc-s99-002`, three fresh reviewers | `report.md#Final-Quality-Gate` |
```

## Plan P-06 — replace `tc-s01-002`

```markdown
- `tc-s01-002` negative: unknown targetをexact statusでfail closedにする
  - 前提: canonical Issue treeに存在しないsyntactically valid Issue IDを指定する。
  - 操作: planning createのtarget-resolution phaseを実行する。
  - 期待結果: `status=blocked`、`reason=unknown_issue`、exit 1、backend call 0、filesystem／Git mutation 0、default branch／active alias／attached file／first-match fallback 0。
  - 失敗検出: unknown targetを任意に`rejected`または`stale`へ分類する回帰を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 required closure: `CLOS-EC-001`
```

## Plan P-07 — replace `tc-s03-002`

```markdown
- `tc-s03-002` negative: Git preflight named conditionsを一つのexact statusへ分類する
  - 前提: named fixturesを一件ずつ用意する。
  - expected mapping:
    - `git-preflight-dirty-tree` → `blocked: dirty_tree`
    - `git-preflight-upstream-missing` → `blocked: upstream_missing`
    - `git-preflight-remote-unavailable` → `blocked: remote_unavailable`
    - `git-preflight-branch-upstream-mismatch` → `stale: branch_upstream_mismatch`
    - `git-preflight-local-remote-mismatch` → `stale: local_remote_mismatch`
    - `git-preflight-expected-head-mismatch` → `stale: expected_head_mismatch`
  - 操作: planning createのpreflightを各parameterで実行する。
  - 期待結果: each parameterが上記exact status／reason、exit 1、backend call 0、repository mutation 0。test reportはparameter IDを保持する。
  - 失敗検出: `stale/blocked` union、all-blocked、all-stale実装を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 required closure: `CLOS-REQ-003`, `CLOS-EC-001`
```

## Plan P-08 — replace `tc-s06-003`

```markdown
- `tc-s06-003` negative: PA-NF 11件をexact statusで評価する
  - 前提: PA-NF-01〜PA-NF-09、PA-NF-10A、PA-NF-10Bを一件ずつ満たすnamed fixturesを用意する。
  - 操作: each fixtureをpublic `planning apply`／readiness evaluatorへ渡す。
  - 期待結果:
    - PA-NF-01 → `blocked: missing_human_source`
    - PA-NF-02 → `blocked: missing_human_source`
    - PA-NF-03 → `blocked: missing_review_source`
    - PA-NF-04 → `blocked: missing_review_source`
    - PA-NF-05 → `rejected: identity_object_mismatch`
    - PA-NF-06 → `rejected: identity_object_mismatch`
    - PA-NF-07 → `stale: source_identity_drift`
    - PA-NF-08 → `rolled_back: precommit_fault_restored`
    - PA-NF-09 → `rolled_back: precommit_fault_restored`
    - PA-NF-10A → `rolled_back: precommit_fault_restored`
    - PA-NF-10B → `publication_pending: publication_incomplete`
  - 全11件exit 1、readinessなし。
  - pre-mutation fixtureはmutation 0。
  - rollback fixtureはbytes／mode／index／HEAD／clean stateがexact H0。
  - publication fixtureはexact local H1だけを保持する。
  - 失敗検出: PA-NF-10の一括close、status union、generic failureを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10B`
```

## Plan P-09 — replace `tc-s06-012` with these two test cards

```markdown
- `tc-s06-012A` recovery: stage-only clean-H0 orphanをbounded workspaceとして扱う
  - 前提:
    - canonical output A。
    - different output B。
    - same semantic operation ID。
    - output Aでexternal staging完了後、repository target変更前にcrash。
  - 操作:
    1. Aのmanifestとstageを確認する。
    2. same args + output Aでrecovery classificationを実行する。
    3. fresh stage-only crashを作り、same args + output Bでclassificationを実行する。
    4. exact A operation pathへstage-only cleanupを実行する。
  - 期待結果:
    - crash後のworktree／index／HEADはexact clean H0。
    - A retryは`workspace_only_stage`を検出し、owned stage／manifestをcleanupしてpreflightから再開できる。
    - Bはsupplied outputにmanifestがなくclean H0なので`new_workspace_attempt`となり、`recovery_required`を返さない。
    - B classificationはA、home、repository内の他output directoryをscanしない。
    - exact-path cleanupはvalid stage-only manifest、completed target 0、backup 0、operation commit 0のときだけA operation directoryを削除する。
    - repository mutation、custom ref、global registryは0。
  - 失敗検出: 不可視stage orphanをfalse repository recoveryとしてblockする回帰と、broad workspace discoveryを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-EC-006`, `CLOS-RISK-001`

- `tc-s06-012B` recovery: repository-visible partial stateとcommitted stateはoriginal workspaceを要求する
  - 前提:
    - output Aでdecision artifact追加後またはfirst canonical replacement後にcrash。
    - separate fixtureでexact H1 commit後にpublication failure。
    - different output B。
  - 操作:
    1. pre-commit partial stateへsame args + output Bを渡す。
    2. same partial stateへoutput Aを渡す。
    3. committed publication stateへoutput Bを渡す。
    4. committed publication stateへoutput Aを渡す。
    5. exact operation prefixに一致しないunrelated dirty-tree fixtureを実行する。
  - 期待結果:
    - pre-commit partial + B → `recovery_required: repository_visible_partial_without_workspace`、new operation directory 0、new repository mutation 0。
    - pre-commit partial + A → manifestを使いrollbackまたはresume。
    - committed H1 + B → `recovery_required: committed_operation_workspace_mismatch`、reset／amend／force push 0。
    - committed H1 + A → `publication_pending`からpush／remote verificationをresume。
    - unrelated dirty tree → `blocked: dirty_tree`であり、recovery prefixと誤認しない。
  - 失敗検出: wrong-workspace resume、backup取り違え、unrelated dirty treeのfalse recovery、lost publication identityを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-EC-006`, `CLOS-EC-008`, `CLOS-RISK-001`, `CLOS-RISK-005`
```

## Plan P-10 — add `tc-s08-003` after `tc-s08-002`

```markdown
- `tc-s08-003` integration: PA-NF 11件とstatus reasonをpublic CLI経由で再検証する
  - 前提: fake remote、archive／git identities、PA-NF-01〜09／10A／10B fixturesを用意する。
  - 操作: public CLIから各fixtureを独立実行する。
  - 期待結果: 11／11がRequirement表とexact status／reason一致、exit 1、readinessなし。`.assurance.json`は全fixtureで不変。rollback／publication stateは各contractどおり。
  - 失敗検出: unit evaluatorとCLI rendererのstatus drift、S06-only false Greenを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 required closure: `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-REQ-016`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10B`
```

## Plan P-11 — replace every step closure contract with the corresponding block below

### S01

```markdown
#### step closure contract

S01は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-002` / S01
- `CLOS-REQ-009` / S01
- `CLOS-EC-001` / S01

exact help／parser matrix、unknown-target negative、known-valid target positive、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkが揃った場合だけ上記portionsを`passed`にする。

`CLOS-CLI`を含む`required=no` summary aliasにstateを付与しない。`CLOS-REQ-009`と`CLOS-EC-001`のaggregateは後続owner portionsがpassedになるまでopenのままとする。
```

### S02A

```markdown
#### step closure contract

S02Aは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-001` / S02A
- `CLOS-REQ-005` / S02A

docs inspection、fresh `spec-reviewer`、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-SKILL` summary aliasにstateを付与しない。
```

### S02B

```markdown
#### step closure contract

S02Bは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-001` / S02B
- `CLOS-REQ-005` / S02B

sensitivity Red、targeted Green、fresh `code-reviewer`、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-SKILL` summary aliasにstateを付与しない。
```

### S03

```markdown
#### step closure contract

S03は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-003` / S03
- `CLOS-REQ-004` / S03
- `CLOS-REQ-021` / S03
- `CLOS-EC-001` / S03
- `CLOS-EC-002` / S03

exact source matrix、complete response、benign direct-argv、prohibited-content backend-call-zero、covered-existing Git-fetch regression、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

`CLOS-GIT`、`CLOS-SEC`、`CLOS-CREATE` summary aliasesにstateを付与しない。S05またはS08をownerに含むaggregatesは後続portionsがpassedになるまでopenのままとする。
```

### S04

```markdown
#### step closure contract

S04は`CLOS-REQ-007` / S04だけを`passed`にできる。targeted Red／Green、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-REVISION` summary aliasにstateを付与しない。
```

### S05

```markdown
#### step closure contract

S05は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-004`, `CLOS-REQ-006`, `CLOS-REQ-008`, `CLOS-REQ-019`, `CLOS-REQ-022`, `CLOS-REQ-023` / S05
- `CLOS-EC-002`, `CLOS-EC-003`, `CLOS-EC-004` / S05
- `CLOS-ARC-01`〜`CLOS-ARC-25` / S05
- `CLOS-RISK-002`, `CLOS-RISK-004` / S05

direct create→Review、control-schema positives／field negatives、git identity matrix、generic archive regression、archive 25／25、cleanup evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

`CLOS-CREATE`、`CLOS-REVIEW`、`CLOS-ARCHIVE` summary aliasesにstateを付与しない。S03／S06／S07／S08を含むaggregatesは後続portionsがpassedになるまでopenのままとする。
```

### S06

```markdown
#### step closure contract

S06は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-009`〜`CLOS-REQ-016`のうちClosure IndexでS06 ownerとされたrows
- `CLOS-REQ-019` / S06
- `CLOS-EC-005`〜`CLOS-EC-009` / S06
- `CLOS-PA-NF-01`〜`CLOS-PA-NF-09`, `CLOS-PA-NF-10A`, `CLOS-PA-NF-10B` / S06
- `CLOS-RISK-001`, `CLOS-RISK-004`, `CLOS-RISK-005` / S06

次をすべて要求する。

- exact archive／git apply parser positives。
- Review schema matrix。
- Human approved／rejected truth table。
- revoked unsupported。
- exact Review SHA／Issue／identity cross-binding。
- exact EC-005 status matrix。
- PA-NF 11／11 exact status。
- durable rejected decision record。
- stage-only same-output cleanup。
- different-output clean-H0 new attempt。
- repository-visible wrong-output `recovery_required`。
- unrelated dirty-tree `blocked`。
- committed wrong-workspace `recovery_required`。
- all pre-commit rollback and rollback-failure stop。
- publication resume and remote-divergence stop。
- runbook regression。
- required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean check。

`CLOS-ADOPTION`と`CLOS-READINESS` summary aliasesにstateを付与しない。S08 owner portionsが存在するaggregatesはS08完了までopenのままとする。
```

### S07

```markdown
#### step closure contract

S07は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-017` / S07
- `CLOS-REQ-023` / S07

build／install／update parity、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-PROJECTION` summary aliasにstateを付与しない。
```

### S08

```markdown
#### step closure contract

S08は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-013`, `CLOS-REQ-014`, `CLOS-REQ-016`, `CLOS-REQ-019`, `CLOS-REQ-021`, `CLOS-REQ-023` / S08
- `CLOS-PA-NF-01`〜`CLOS-PA-NF-09`, `CLOS-PA-NF-10A`, `CLOS-PA-NF-10B` / S08
- `CLOS-RISK-004` / S08

archive／git positive E2E、PA-NF 11／11 exact public status、assurance unchanged、existing compatibility、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。

S08は`CLOS-REQ-003`〜`CLOS-REQ-012`、`CLOS-REQ-015`、`CLOS-REQ-017`、`CLOS-REQ-018`、`CLOS-REQ-020`、`CLOS-REQ-022`のowner portionを作成または更新しない。`CLOS-INTEGRATION` summary aliasにstateを付与しない。
```

### S09A

```markdown
#### step closure contract

S09Aは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-018` / S09A
- `CLOS-EC-010` / S09A
- `CLOS-RISK-003` / S09A

fake-only selection／abort／rollback／publication-retry evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkを要求する。`CLOS-DOGFOOD` summary aliasにstateを付与しない。
```

### S09B

```markdown
#### step closure contract

S09Bは次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-018` / S09B
- `CLOS-REQ-024` / S09B
- `CLOS-EC-010` / S09B
- `CLOS-RISK-003` / S09B

Human-selected eligible target、explicit live mutation authority、bounded operation、observability metrics、evidence destination、Main verificationを要求する。pytest workerはこのportionをpassできない。`CLOS-DOGFOOD` summary aliasにstateを付与しない。
```

### S90

```markdown
#### step closure contract

S90は`CLOS-REQ-020` / S90だけを`passed`にできる。

docs／Skill／referenceがone Issue／one branch／one Delivery PR、required review、Human-only merge、shared delivery owner boundaryと一致し、fresh `spec-reviewer`、Main Result Approval、commit、post-commit clean checkが揃った場合だけpassする。

`CLOS-DOCS` summary aliasと、Closure IndexでS90 ownerに指定されていない`CLOS-REQ-023` portionにstateを付与しない。
```

## Plan P-12 — replace the S06 step-gate completion sentence

```markdown
scope外diff 0、exact parser matrix、Review schema matrix、Human approved／rejected truth table、revoked unsupported、archive／git approved positives、durable rejection、PA-NF 11／11 exact status、all fault matrix、stage-only same-output cleanup、different-output clean-H0 new attempt、repository-visible wrong-output stop、committed wrong-workspace stop、existing runbook unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisional、status unionをpassとして扱わない。
```

## Plan P-13 — replace the S08 step gate

```markdown
focused planning／integration suitesとexisting authoring-pack suitesを成功させ、archive／git positive、PA-NF 11／11 exact status、assurance mutation 0、existing compatibility、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。S08 ownerでないrowをpassしたと記録しない。
```

## Plan P-14 — replace all of `### S99 final quality gate`

```markdown
### S99 final quality gate

#### behavior goal

全pre-S99 owner portions、test sufficiency、integrated diff、Requirement／Design／Plan／implementation／tests／docsの整合、およびClosure owner graphのvalidityを確認する。S99はmissing product workを直接実装しない。

#### depends on / unblocks

- depends on:
  - S90 complete。
  - ownerがS01〜S90である全`required=yes` portionsが`passed`。
  - open／failed／blocked pre-S99 portion 0。
- S99-owned portionsはentry時点で`open`でよい。
- unblocks: Final Exit only after S99-owned portions pass and every required aggregate becomes `closed`。

#### exact verification surface

- full provider diff and generated projection diff。
- `requirement.md`, `design.md`, `plan.md`, canonical `report.md`。
- all focused and repository-wide tests。
- package build and fresh install/update evidence。
- dogfood evidence and open risk list。
- Closure Index required rows、summary aliases、step closure contracts、dependency graph。
- current branch／one-Issue delivery handoff preconditions。

#### behavior slice execution

1. Mainが全pre-S99 owner portions、reviewer evidence、commit candidates、clean statusを確認する。
2. MainがClosure graph structural testを実行する。
3. `uv run pytest -q`、`make lint`、`uv build`、`./spec-dock/scripts/spec-dock validate`を実行する。
4. `qa-reviewer`がtest sufficiency、integration、failure pathsを確認する。
5. issue-wide `code-reviewer`がstructure、responsibility、security、regression riskを確認する。
6. `spec-reviewer`がall requirements、non-goals、authority、docs、Closure graphを確認する。
7. failはowning stepへ戻してbounded fix／re-reviewを行う。
8. 三者passed後、Mainがfinal report ledgerを更新しfinal commitを作成、post-commit clean checkを行う。
9. S99は自身がownerであるportionsだけを`passed`にする。
10. Mainが全`required=yes` aggregateを再計算し、全件`closed`の場合だけFinal Exitをunblockする。

#### delegation contract

- delegated role: reviewer-only。product mutationはowning stepへ戻す。
- allowed repository changes by reviewer: none。
- required verification: repository-wide commands、graph structural test、three fresh reviewer passes。
- stop conditions: failed／unavailable／denied reviewer、open material ledger、dirty tree、missing pre-S99 portion、invalid graph。
- output required: reviewer results、graph result、Main disposition、final commit scope、remaining risks。

#### 具体テストケース一覧

- `tc-s99-001` quality: full suite and package verification
  - 前提: S01〜S90のrequired owner portionsがpassedし、S99 portionsだけがopen。
  - 操作: full tests、lint、build、validate、three reviewersを実行する。
  - 期待結果: commands成功、three fresh reviewers passed、open material blocker 0、final report commit、post-commit clean。
  - 失敗検出: focused-only Green、docs drift、unreviewed integrated riskを検出する。
  - 検証方法: `uv run pytest -q && make lint && uv build && ./spec-dock/scripts/spec-dock validate`
  - 関連 required closure: `CLOS-REQ-020` / S99、`CLOS-S99-001` / S99

- `tc-s99-002` structure: Closure owner graphをdeterministically検証する
  - 前提: canonical Planのsummary table、required Closure tables、step dependencies、全step closure contractsを入力とする。
  - 操作: read-only parser／inspectionで次を検証する。
    1. `required=no` summary aliasはowner／stateを持たない。
    2. summary aliasがstep closure targetまたはS99 state targetに現れない。
    3. every `required=yes` ownerはallowed ordered step set内。
    4. `Final Exit` ownerは0。
    5. owner listはduplicateなし、step order ascending。
    6. each step closure contractがclaimするID setはClosure Indexでそのstepをownerに持つsetとexact一致。
    7. S08 claim setが`CLOS-REQ-013`, `014`, `016`, `019`, `021`, `023`, PA-NF 11 rows, `CLOS-RISK-004`だけと一致。
    8. S99 entry prerequisiteはpre-S99 portionsだけで、S99 portionsを事前要求しない。
    9. dependency edgesはallowed step orderのforward edgeだけ。
    10. graphはacyclic。
  - 期待結果: violations 0。each required rowには少なくとも一つのexecutable pre-terminal ownerがあり、S99完了後に全aggregateがclosedへ到達可能。
  - 失敗検出: stateless alias close、undeclared owner、Final Exit cycle、S08 overclaim、S99 self-dependencyを防ぐ。
  - 検証方法: Main-owned read-only structural parser／inspection。input、scriptまたはquery SHA、resultを`report.md#Final-Quality-Gate`へ保存する。
  - 関連 required closure: `CLOS-S99-001`

#### report evidence destination

Mainが`report.md#Final-Quality-Gate`へpre-S99 portion inventory、graph result、full verification、three reviewer results、S99-owned portion result、final commit scopeを記録する。

#### step closure contract

S99は次のrequired owner portionsだけを`passed`にできる。

- `CLOS-REQ-020` / S99
- `CLOS-S99-001` / S99

S99 entry時点では全pre-S99 portionsがpassedしていなければならない。full verification、graph violations 0、three fresh reviewers passed、final report update、final commit、post-commit clean checkが揃った場合だけ上記S99 portionsをpassedにする。

`CLOS-QUALITY` summary aliasにstateを付与しない。S99 portionsをpassedにした後、全required aggregateがclosedであることを再計算する。

#### step gate

failed／unavailable／denied／waived／provisionalをpassedとして扱わない。pre-S99 portion missing 0、graph violations 0、three fresh reviewer passes、clean final commit、全required aggregate closedを必要とする。
```

## Plan P-15 — replace all of `## 10. Final Exit Contract`

```markdown
## 10. Final Exit Contract

Final ExitはClosure ownerではなく、S99後のexternal shared delivery handoffである。Final Exit entry／executionはClosure Indexのowner portionまたはaggregateを変更しない。

### Entry conditions

- S01〜S90のrequired owner portions passed。
- S99-owned portions passed。
- 全`required=yes` aggregate state=`closed`。
- summary alias state 0。
- final report ledger、final commit、post-commit clean check complete。
- current source branchがintended Issue branch。
- unresolved material blocker 0。

### External delivery handoff

1. Mainはcurrent shared Issue delivery workflowを使用する。
2. one Issue／one branch／one Delivery PRを維持する。
3. PR Delivery／Merge Preparation evidence、required checks／reviews／blockersはshared workflow owner contractに従う。
4. Humanだけがmergeを決定・実行する。
5. merge後verificationとIssue lifecycle completionはcurrent shared workflowへ従い、本Planはそのsemanticsを再定義しない。

### Post-handoff evidence

PR URL、required check／review result、Human merge decision、post-merge verification、Issue lifecycle resultはReportまたはcurrent shared destinationへexternal completion evidenceとして記録する。

このpost-handoff evidenceはS99 admission prerequisite、Closure Index owner portion、S99 aggregate closureへ遡及的に組み込まない。PR／merge failureはshared workflowでblockし、S99を自己循環させない。ただしsource-changing correctionが必要な場合は該当owner portionとS99 evidenceをinvalid化し、owning stepへ戻す。

### Stop conditions

- required aggregate open。
- S99 incomplete。
- required review/check未完了。
- unresolved blocker。
- dirty tree。
- wrong branch/base。
- source drift。
- Human merge decision欠落。

Planning result、S99 result、PR readinessのいずれもHuman mergeまたはIssue completionを自己主張しない。
```

# 5. Exact Report replacements and additions

The current Report still labels the already-published `3fc0e61e…` snapshot as `commit pending`, which is the attached review’s P2-05.

## Report RPT-01 — replace the opening paragraph

```markdown
本書は Issue の観測証跡台帳である。planned requirements と closure contract は `plan.md` が所有し、本書は採用判断、reviewer verdict、実行結果、closure delta、commit evidence を時系列で記録する。published snapshot `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` に対するfresh ChatGPT Red Team reviewはP0=0、P1=3、P2=1のFAILであり、S01はblockedである。同一の専用Blue Team authoring threadはP1-17、P1-18、P1-19、P2-05だけを対象とするbounded correctionを作成した。修正版に対する別fresh Red reviewは未実施であり、製品実装は開始していない。
```

## Report RPT-02 — add this Decision Ledger row after `D-20260727-OP008`

```markdown
| D-20260727-CG009 | resolved | contract | fresh ChatGPT Red Team / same dedicated Blue Team | public status／PA-NF count、stage-only wrong-output recovery、Closure owner graph、published milestone ledgerが未閉鎖だった | status union維持; broad workspace registry; Final Exit owner portion; bounded deterministic correction | named statusを一意化しPA-NFを11 fixtureへ分割する。stage-only clean-H0 orphanとrepository-visible recoveryを分離し、broad registryなしでsame-output cleanup／wrong-output stopを定義する。summary aliasをstatelessに戻し、required owner graphをS99で閉じてからFinal Exitへhandoffする | Red findingsを実装前にtestableかつacyclicなowner contractへ変換し、P1-11〜P1-16とone-Issue／one-branch／one-PR境界を維持する | applied to bounded correction | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`; `requirement.md`; `design.md`; `plan.md`; `report.md` | correctionをcommit／pushし、actual new full HEADで別fresh Red review |
```

## Report RPT-03 — add these Evidence Adoption Ledger rows

```markdown
| EAL-20260727-CHATGPT-RED-3 | adopted | fresh ChatGPT Red Team read-only review | published snapshot `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` | exact branch／HEADとcanonical filesを確認した正式FAILとしてP0=0、P1=3、P2=1を採用した。P1-11〜P1-16はcurrent scopeでclosed／preservedと確認された | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md` | P1-17〜P1-19、P2-05だけをsame Blue Teamへ渡す |
| EAL-20260727-CHATGPT-BLUE-3 | adopted | same dedicated ChatGPT Blue Team authoring thread | Requirement／Design／Plan／Report bounded correction | exact remote HEAD、canonical blobs、fresh Red artifactを確認し、status determinism、bounded recovery observability、acyclic owner graph、Report milestoneだけを具体化した。BlueはPASS判定、repository mutation、patch、ZIP生成を行っていない | fresh Red artifact; bounded owner-document replacement blocks | Mainがactual diff／validation／assurance rebindingを確認し、new immutable HEADで別fresh review |
```

## Report RPT-04 — replace the canonical-planning row in `Objective Alignment Ledger`

```markdown
| canonical planning repair | ChatGPT-first Issue Planningのcreate→revise→review→Human Gate→apply→publication→readinessがREQ-001〜REQ-024と一貫する | closed CLI／Candidate controls／Review-Human authority、deterministic status、stage-only versus repository-visible recovery、acyclic required Closure graphをowner文書へ固定する | low。correctionは既存lifecycleを置換せず、曖昧なstatus／recovery／terminal proofだけを閉じる | published snapshot `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` のfresh Red verdictはFAIL。P1-17〜P1-19／P2-05 bounded correction後に別fresh reviewが必要 |
```

## Report RPT-05 — replace the three Spec Authoring Gate rows and their explanatory sentence

```markdown
| requirement | current Requirement、exact HEAD、fresh Red P1-17を照合 | なし。stable status、PA-NF-10A／10B、11／11 exact oracleを確定 | P1-17 Requirement owner部分をbounded correctionへ採用 | failed | yes | correction snapshotのfresh canonical re-review |
| design | current status table、apply／recovery state、fresh Red P1-17／P1-18を照合 | なし。undeclared statusを除去し、stage-only clean-H0 orphanとrepository-visible／committed recoveryを分離 | P1-17／P1-18 Design owner部分をbounded correctionへ採用 | failed | yes | correction snapshotのfresh canonical re-review |
| plan | Closure Index、S06／S08／S99／Final Exit、fresh Red P1-17〜P1-19を照合 | なし。11 PA-NF、exact owner sets、stateless summaries、pre-S99／S99／Final Exit DAGを確定 | P1-17〜P1-19 Plan owner部分をbounded correctionへ採用 | failed | yes | correction snapshotのfresh canonical re-review |

`failed`は`artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`の直近正式判定を表す。Blue correctionは自己承認ではなく、別fresh Red Team threadがnew exact HEADを再判定する。
```

## Report RPT-06 — replace the Reviewer Gate Status row

```markdown
| canonical planning | ChatGPT-first canonical spec review | fresh Red Team | current for published HEAD; stale after bounded correction | failed | no | new immutable correction snapshot requires fresh review | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`。P0=0、P1=3、P2=1。P1-17／P1-18／P1-19、P2-05 bounded correction対象。P1-11〜P1-16はpreserved |
```

## Report RPT-07 — replace the Milestone table with this block

```markdown
## マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）

| マイルストーン / step | クロージャ状態 | コミット候補 / 範囲 | コミットハッシュ / 最終台帳 | 差分確認 | 次アクション |
|---|---|---|---|---|---|
| second canonical correction snapshot | committed and published; fresh review failed | Requirement、Design、Plan、Assurance、Report、prior Red／Blue artifacts | `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` | remote branch HEADとexact identicalをGitHub connectorで確認 | P1-17〜P1-19／P2-05 bounded correctionへ進む |
| third bounded correction | authoring complete; commit pending | Requirement、Design、Plan、Report、new Red artifact、Assurance rebinding | pending — Main must record actual resulting full HEAD | integration後にvalidate、diff-check、assurance verify、clean checkを実行 | one immutable commitをpushし、actual resulting 40-character HEADで別fresh Red review |
| S01 | not started | `plan.md` S01 exact scope | none | 製品実装差分なし | P0=0／P1=0のfresh planning reviewとsame-identity Human authorization後だけ委任 |
```

## Report RPT-08 — replace the Final Spec Review row

```markdown
| Final Spec Review | Requirement、Design、Plan、Report、implementation、tests、docs alignment | failed | latest: `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md` against exact published HEAD `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc`; bounded correction後にnew exact HEADで別fresh review |
```

# 6. Traceability and test impact

| Finding                                           | Owner-document changes                                                                  | Primary planned evidence                                                                                                               |
| ------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| P1-17 — nondeterministic status／PA-NF             | Requirement R-01–R-05; Design D-01/D-02/D-05; Plan P-02–P-04/P-06–P-10/P-12/P-13        | `tc-s01-002`, rewritten `tc-s03-002`, `tc-s06-003[11]`, `tc-s08-003[11]`                                                               |
| P1-18 — impossible stage-only wrong-output oracle | Requirement R-01; Design D-03/D-04; Plan `tc-s06-012A`, `tc-s06-012B`, S06 closure/gate | same-output stage cleanup, different-output clean-H0 new attempt, repository-visible wrong-output stop, committed wrong-workspace stop |
| P1-19 — circular／contradictory Closure graph      | Plan P-01/P-02/P-04/P-05/P-11/P-14/P-15                                                 | `tc-s99-002`, exact S08 owner set, S99 two-phase admission/completion, Final Exit owner 0                                              |
| P2-05 — stale Report milestone                    | Report RPT-01–RPT-08                                                                    | exact published reviewed HEAD `3fc0e61e…03cc`, separate pending correction row                                                         |

The current Requirement allows `blocked` or `stale` for grouped source failures, the current Design still emits undeclared `failed` and “invalid Review evidence,” and the current Plan allows `stale/blocked` while splitting PA-NF-10 into two effective cases without updating the count.

The current recovery text simultaneously permits a new clean-H0 invocation when no supplied manifest exists and requires wrong-output `recovery_required` even for a stage-only crash.

The current Plan declares summary aliases stateless but later closes `CLOS-QUALITY`, gives `CLOS-REQ-020` a `Final Exit` owner, and lets S08 claim rows for which it is not an owner.

No product acceptance test was executed here. These are planned closure contracts, not observed Green evidence.

After Main integrates these blocks, `.assurance.json` must be regenerated or rebound to the resulting exact Requirement／Design／Plan bytes. A literal Assurance replacement cannot be supplied before those final bytes and hashes exist. The current Assurance is provisional and bound to the pre-correction hashes.

# 7. Non-regression self-check

| Previously closed control                                 | Preservation in these blocks                                                          |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| P1-11 exact review identity handling                      | No product expansion; actual future HEAD must be copied exactly                       |
| P1-12 EC-005 exact mapping                                | Unchanged; broader P1-17 status taxonomy is aligned around it                         |
| P1-13 exact public CLI identity                           | All archive／git／Issue／base arguments and derivations remain unchanged                 |
| P1-14 durable rejection／unsupported revocation            | Decision-only publication and old-H0 staleness remain unchanged                       |
| P1-15 closed Candidate controls                           | All four versioned byte-level schemas and negative matrices remain unchanged          |
| P1-16 secret pre-invocation rejection                     | Benign argv and prohibited-content tests remain separate; backend call zero preserved |
| Review／Human authority separation                         | Preserved                                                                             |
| Dual Plan-adoption and implementation-start authorization | Preserved                                                                             |
| Mode-neutral archive／git start gate                       | Preserved                                                                             |
| Exact Review-result byte binding                          | Preserved                                                                             |
| Source repository／branch／HEAD／Issue／target／base binding   | Preserved                                                                             |
| Public `planning apply` as sole late-lifecycle route      | Preserved                                                                             |
| Pre-commit reverse rollback                               | Preserved                                                                             |
| Restore-failure `recovery_required`                       | Preserved and made observable                                                         |
| Post-commit `publication_pending` resume                  | Preserved                                                                             |
| Remote divergence stop; no force/reset/amend              | Preserved                                                                             |
| Shared runbook transaction primitive                      | Preserved                                                                             |
| Twenty-five archive safety classes                        | Unchanged                                                                             |
| Inclusive archive resource ceilings                       | Unchanged                                                                             |
| Generic authoring-pack default compatibility              | Unchanged                                                                             |
| S01 positive target-resolution oracle                     | Preserved                                                                             |
| S03 planning-test ownership                               | Preserved                                                                             |
| S02A/S02B split                                           | Preserved                                                                             |
| S09A/S09B worker/Human split                              | Preserved                                                                             |
| Provider-first implementation ownership                   | Preserved                                                                             |
| `.assurance.json` product-flow immutability               | Preserved                                                                             |
| Report as observational ledger                            | Preserved; P2-05 is corrected without granting authority                              |
| one Issue／one branch／one Delivery PR                      | Preserved                                                                             |
| Human-only merge                                          | Preserved                                                                             |
| Final Exit shared-workflow ownership                      | Preserved; removed only from the preterminal Closure owner graph                      |
