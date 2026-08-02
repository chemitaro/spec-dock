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

Act only as the dedicated Blue Team author for iss-00334. First use @GitHub to inspect chemitaro/spec-dock branch iss-00334-implement-chatgpt-issue-planning-workflow at source HEAD b5447aef2c4d2ad5fabbab532cb9cef0e8d397b0. Read spec-dock/active/issue/design.md, spec-dock/active/issue/plan.md, and spec-dock/active/issue/artifacts/20260727t004653z-chatgpt-fresh-canonical-review-fail.md. Confirm those exact inputs before authoring. Produce bounded replacement-ready Markdown blocks only; do not edit the repository, do not create a patch, and do not issue a PASS/FAIL review. Close the two P1 findings: define closed versioned schemas plus validation and rejection semantics for planning apply Review result JSON and Human decision JSON; and make the Plan start gate admit either an approved Candidate identity or an approved git-bound reviewed identity without weakening source binding. Also close the two P2 findings: add a positive known-valid target-resolution test in S01; and relocate the S03 planning-specific argv/redaction fixture to an S03-allowed planning test while treating tests/unit/authoring_pack/test_github_fetch_policy.py as covered-existing only. Preserve all controls that the formal review marked closed, including explicit public planning apply, crash-safe transaction/recovery, 25 archive safety classes, schema-complete Closure Index, S02A/S02B, S09A/S09B, source binding, canonical-state rules, assurance/report evidence, and one-Issue-one-PR workflow. Return: (1) verified repository/branch/HEAD and paths inspected; (2) exact Design blocks to replace/add; (3) exact Plan blocks to replace/add; (4) acceptance tests and traceability impact; (5) a short self-check that no previously closed control regressed.

## Answer

# 1. Verified repository, branch, HEAD, and inspected paths

GitHub connector inspection was performed read-only on **2026-07-27**.

* Repository: `chemitaro/spec-dock`
* Default branch: `main`
* Required branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Verified branch HEAD: `b5447aef2c4d2ad5fabbab532cb9cef0e8d397b0`
* `b5447aef…397b0` is one commit after reviewed planning snapshot `2984c696…631`; that commit only added the fresh-review artifact and updated `report.md`. It did not modify `design.md` or `plan.md`.

The `spec-dock/active/issue/*` working-tree aliases were not directly retrievable as committed GitHub paths. The corresponding canonical Issue files inspected at the required HEAD were:

* `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/design.md`

  * Git blob: `b1ac02730462941165aa7ee6a08120b487d58191`
* `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/plan.md`

  * Git blob: `90c3d407b63046a6650e2c2d42bb3d2dc7b831f1`
* `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/artifacts/20260727t004653z-chatgpt-fresh-canonical-review-fail.md`

  * Git blob: `c39d69a066770ad3ad41fe6456d1557ea6a23a79`

The review artifact identifies exactly two P1 gaps—unclosed apply-evidence contracts and a Candidate-only Plan start gate—and two P2 gaps—the missing positive S01 target-resolution oracle and the S03 test-ownership mismatch.

The supplementary uploaded design note was not used as authority for these iss-00334 replacement blocks.

No repository mutation, patch, replacement file, or review verdict was produced.

# 2. Exact Design blocks to replace or add

## Design replacement D-01 — replace all of `## 3. Public Command Design`

````markdown
## 3. Public Command Design

```text
./spec-dock/scripts/spec-dock-chatgpt planning create --issue <id> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt planning revise --candidate <zip-or-tree> --lane <semantic|mechanical> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --mode archive-candidate --candidate <zip> --logical-filename <name> --zip-sha256 <sha256> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --mode git-bound --reviewed-head <sha> --target <repo-relative-path> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt planning apply --issue <id> --mode <archive-candidate|git-bound> --review-result <external-json> --human-decision <external-json> --decision-artifact <issue-artifacts-relative-json> --expected-head <sha> [mode identity] --output <external-dir>
```

- parser／dispatchは上記四つのChatGPT planning commandだけを公開する。
- `planning create`はscope、parent、dependencies、source HEADを解決し、closed Promptからcomplete三文書responseを要求する。response検証後、Core Runtimeがmandatory controlsを生成してimmutable Issue Candidate ZIPをfinal public artifactとして返す。
- `planning revise`はSkillが選択済みlaneを受ける。CLIはlaneを推測しない。
- `review planning`はmodeを推測せず、`ReviewedPlanningIdentityV1`のarchive identityまたはgit identityを検証してread-only reviewerを起動する。`planning apply`へ渡すauthority-bearing JSONは`PlanningReviewResultV1`へ適合しなければならず、Human-readable companion、raw transcript、Markdown verdictだけをapply evidenceとして受け付けない。
- `planning apply`は後半lifecycleの唯一のsupported public entrypointである。archive modeでは`--candidate <zip>`、`--logical-filename <name>`、`--zip-sha256 <sha256>`を、git-bound modeでは`--reviewed-head <sha>`とrepeatable `--target <repo-relative-path>`を追加必須とする。
- 両modeで`PlanningReviewResultV1` source、`PlanningHumanDecisionV1` source、decision artifact destination、expected HEAD、external output directoryを要求する。Runtimeは二つのexternal JSONをそれぞれ一回だけbytesとして読み、同じbytesからSHA-256計算とJSON validationを行う。
- Review result、Human decision、CLI mode identityは同一の`ReviewedPlanningIdentityV1` objectと`reviewed_identity_sha256`へbindしなければならない。Human decisionはさらにexact Review-result file bytesの`review_result_sha256`へbindする。
- schema version／evidence kind／required key／unknown key／duplicate key／enum／timestamp／digest／mode／identityの不一致はrepository mutation前に拒否する。current sourceがvalid reviewed identityからdriftした場合は`stale`とし、別mode、別identity、waiver、Candidateへの再解釈へfallbackしない。
- `--decision-artifact`はactive Issueの`artifacts/` direct childにある新規lowercase JSON pathだけを受け付け、既存file、symlink parent、scope外pathを拒否する。positive authorization gate通過後、Runtimeはvalidated `--human-decision` sourceのexact bytesだけをcanonical artifactへstageする。
- validなReview `fail`、Human `rejected`、Human `revoked`はauthority evidenceとして構造上受理できるが、adoption／implementation startを許可せず`blocked`、exit `1`、repository mutation `0`とする。
- text／JSONは同じstable `status`を返す。`ready`だけexit `0`、`blocked`、`stale`、`rejected`、`rolled_back`、`publication_pending`、`blocked_remote_diverged`、`recovery_required`はexit `1`。resultはoperation ID、source／review／Human identity digest、exact evidence file digests、mutation phase、local／remote HEAD、evidence locators、bounded remediationを含み、Human approvalやreviewer passを生成しない。
- output directoryはrepository／canonical tree外のexisting non-symlink directoryに限定する。
````

## Design replacement D-02 — replace all of `### 4.3 Review Identity`

````markdown
### 4.3 Reviewed Planning Identity

`ReviewedPlanningIdentityV1`は、次の二つのclosed objectのどちらか一つだけである。全object levelでrequired keyはexact、unknown keyとduplicate keyは禁止する。文字列を暗黙trim／case-fold／path-normalizeして別identityへ変換しない。

#### archive-candidate identity

```json
{
  "mode": "archive-candidate",
  "logical_filename": "<normalized logical ZIP filename>",
  "observed_transport_filename": "<observed external filename>",
  "zip_sha256": "<64 lowercase hexadecimal characters>",
  "internal_root": "<single candidate root ending with />",
  "candidate_id": "<candidate id>",
  "source_repository": "<owner/repository>",
  "source_branch": "<named branch>",
  "source_head": "<40 lowercase hexadecimal characters>"
}
```

- `logical_filename`、ZIP SHA、internal root、Candidate ID、MANIFEST identity、source bindingは同じCandidate bytesから導出・照合する。
- `observed_transport_filename`は実際に受け取ったfilenameである。transportによるclosed `(N)` aliasだけを既存contractどおりlogical filenameへnormalizeでき、それ以外のrename、root変更、repackagingを許可しない。
- `source_repository`、`source_branch`、`source_head`はCandidate `SOURCE-BASELINE.json`およびMANIFESTと一致しなければならない。

#### git-bound identity

```json
{
  "mode": "git-bound",
  "repository": "<owner/repository>",
  "branch": "<named branch>",
  "reviewed_head": "<40 lowercase hexadecimal characters>",
  "target_paths": [
    "<repo-relative POSIX path>"
  ],
  "base": {
    "kind": "none",
    "head": null
  }
}
```

`base.kind`の許可値は`none`、`semantic-base`、`merge-base`だけである。`none`の場合は`base.head`を`null`、それ以外は40文字lowercase hexadecimal commit SHAとする。

- `target_paths`は1件以上、lexicographic ascending、duplicateなしでなければならない。
- 各pathはrelative POSIX pathであり、absolute path、`.`／`..` segment、backslash、NUL、empty segmentを拒否する。
- 各pathは`reviewed_head`でrepository内のtracked regular blobへ解決しなければならない。
- `repository`、`branch`、`reviewed_head`、`target_paths`、必要なbaseのいずれかが変われば別identityである。

#### Canonical identity digest

`reviewed_identity_sha256`は、validated `ReviewedPlanningIdentityV1` objectを次のcanonical JSONへ変換したbytesのSHA-256である。

1. input JSONはUTF-8、BOMなしであり、duplicate keyをparse時に拒否する。
2. object keyを全階層でlexicographic ascendingにする。
3. separatorは`,`と`:`だけを使用し、insignificant whitespaceを含めない。
4. non-ASCII文字をescapeせずUTF-8でencodeする。
5. array orderは保持する。`target_paths`はvalidation前に並べ替えず、既にsortedであることを要求する。
6. digestは64文字lowercase hexadecimalで表す。

Review result、Human decision、CLI mode-specific argumentsは、同じvalidated identity objectとのexact equalityと同じ`reviewed_identity_sha256`の双方を満たさなければならない。digest一致だけでobject mismatchを許可せず、object一致だけでdigest mismatchを許可しない。
````

## Design replacement D-03 — replace all of `### 4.4 Human Authorization Evidence`

````markdown
### 4.4 Review Result and Human Authorization Evidence

authority-bearing apply evidenceは`PlanningReviewResultV1`と`PlanningHumanDecisionV1`の二つだけである。既存Candidate decomposition／node creation approval contractとは別のnamed data contractだが、新しいschema registry、receipt registry、database、custom Git refを作らない。実装ownerは既存`domain/issue_planning_contracts.py`内のclosed data validationである。

全JSON objectはUTF-8、BOMなし、top-level object、duplicate keyなし、required key exact、unknown keyなしでなければならない。将来versionをv1 validatorがbest-effortで受理してはならない。

#### 4.4.1 `PlanningReviewResultV1`

```json
{
  "schema_version": "spec-dock.planning-review-result.v1",
  "evidence_kind": "planning-review-result",
  "issue_id": "iss-00334",
  "reviewer_role": "spec-reviewer",
  "reviewer_id": "<non-empty non-secret stable identifier>",
  "freshness": "fresh",
  "authority": "read-only",
  "verdict": "pass",
  "reviewed_at_utc": "2026-07-27T00:46:53Z",
  "reviewed_identity": {
    "<exact ReviewedPlanningIdentityV1 object>": "<mode-specific shape>"
  },
  "reviewed_identity_sha256": "<64 lowercase hexadecimal characters>",
  "finding_ids": []
}
```

Field semantics:

- `schema_version`はexact literal `spec-dock.planning-review-result.v1`。
- `evidence_kind`はexact literal `planning-review-result`。
- `issue_id`はCLI `--issue`およびreviewed target Issueと一致する。
- `reviewer_role`のv1許可値は`spec-reviewer`だけである。
- `reviewer_id`は1〜200文字のnon-secret attribution identifierであり、control character、line break、empty stringを拒否する。単独でapproval authorityを付与しない。
- `freshness`のv1許可値は`fresh`だけである。freshnessはwall-clock TTLではなく、exact reviewed identityとapply時current sourceのno-driftによって再検証する。
- `authority`のv1許可値は`read-only`だけである。
- `verdict`の許可値は`pass`または`fail`だけである。
- `reviewed_at_utc`はvalid calendar valueを持つexact UTC RFC 3339 seconds form `YYYY-MM-DDTHH:MM:SSZ`とする。offset、timezone abbreviation、date-only、missing secondsを拒否する。
- `reviewed_identity`は§4.3のclosed mode-specific objectである。
- `reviewed_identity_sha256`は§4.3のcanonical identity digestと一致する。
- `finding_ids`は0〜256件のsorted unique string arrayであり、各要素は1〜128文字、control characterなしとする。`fail`は1件以上を要求する。`pass`は0件以上を許可し、nonblocking observationの存在をauthorityへ昇格させない。

Review-result file identityはself-referential JSON fieldにしない。Runtimeがexternal fileを一回だけ読み、そのexact bytesから計算したSHA-256を`review_result_sha256`とする。Human decisionはこのexact file digestへbindし、別serialization、copy-and-edit、Markdown companion、同じ意味と推測された別bytesを代用できない。

#### 4.4.2 `PlanningHumanDecisionV1`

```json
{
  "schema_version": "spec-dock.planning-human-decision.v1",
  "evidence_kind": "planning-human-decision",
  "issue_id": "iss-00334",
  "decision": "approved",
  "plan_adoption": true,
  "implementation_start": true,
  "approver_role": "human",
  "approver_id": "<non-empty non-secret stable identifier>",
  "decided_at_utc": "2026-07-27T01:00:00Z",
  "review_result_sha256": "<SHA-256 of the exact PlanningReviewResultV1 file bytes>",
  "reviewed_identity": {
    "<exact ReviewedPlanningIdentityV1 object>": "<mode-specific shape>"
  },
  "reviewed_identity_sha256": "<64 lowercase hexadecimal characters>",
  "revokes_decision_sha256": null
}
```

Field semantics:

- `schema_version`はexact literal `spec-dock.planning-human-decision.v1`。
- `evidence_kind`はexact literal `planning-human-decision`。
- `issue_id`はCLI `--issue`およびReview resultと一致する。
- `decision`の許可値は`approved`、`rejected`、`revoked`だけである。
- `approver_role`のv1許可値は`human`だけである。
- `approver_id`は1〜200文字のnon-secret stable identifierであり、control character、line break、empty stringを拒否する。
- `decided_at_utc`はexact UTC RFC 3339 seconds formであり、`reviewed_at_utc`より前であってはならない。
- `review_result_sha256`はRuntimeが同じinvocationで一回だけ読み込んだexact Review-result file bytesのSHA-256と一致する。
- `reviewed_identity`と`reviewed_identity_sha256`はReview resultおよびCLI mode identityとexact一致する。
- `revokes_decision_sha256`は`null`または64文字lowercase hexadecimalである。revocation lookup用registryを作らない。

Allowed decision combinations are closed:

| `decision` | `plan_adoption` | `implementation_start` | `revokes_decision_sha256` | Effect |
|---|---:|---:|---|---|
| `approved` | `true` | `true` | `null` | positive Human gate。残りのapply preconditionsへ進める |
| `rejected` | `false` | `false` | `null` | `blocked`。repository mutation 0 |
| `revoked` | `false` | `false` | prior decision SHA-256 | `blocked`。repository mutation 0 |

上記以外のpartial approval、`approved`とrevocation digestの併用、`rejected`／`revoked`でtrue authorizationを持つ組合せはschema-semantic violationとして`rejected`とする。

`revoked`のdigestは取り消し対象を説明するnegative evidenceであり、それ自体を検索・authority stateへ変換しない。`revoked`は常にnon-authorizingである。

#### 4.4.3 Validation order and rejection semantics

`planning apply`は次の順序をrepository mutation前に完了する。

1. external Review／Human filesとoutput／decision destinationのpath safetyを検証する。
2. 各external JSONを一回だけbytesとして読み、exact file SHA-256を計算する。
3. UTF-8、JSON object、duplicate key、schema version、evidence kind、required／unknown key、field type、enum、timestamp、digest formatを検証する。
4. 各`reviewed_identity`を§4.3で検証し、canonical digestを再計算する。
5. Review、Human、CLI `--mode`、mode-specific arguments、Issue IDのexact cross-bindingを検証する。
6. Human `review_result_sha256`とactual Review-result bytesを照合する。
7. current repository／branch／HEAD／Candidate bytes／target blobsをreviewed identityへ照合し、source freshnessを再評価する。
8. Review verdictとHuman decisionのauthority semanticsを評価する。
9. positive gateだけがstaging／transactionへ進む。

Stable pre-mutation mapping:

| Condition | Status | Exit | Repository mutation |
|---|---|---:|---:|
| malformed JSON、duplicate／unknown key、wrong version／kind、invalid enum／timestamp／digest | `rejected` | 1 | 0 |
| wrong reviewer role、non-fresh declaration、non-read-only authority | `rejected` | 1 | 0 |
| Review／Human／CLI mode mismatch | `rejected` | 1 | 0 |
| Review／Human／CLI identity objectまたはidentity digest mismatch | `rejected` | 1 | 0 |
| Human `review_result_sha256` mismatch | `rejected` | 1 | 0 |
| valid identityに対するcurrent source／Candidate／target drift | `stale` | 1 | 0 |
| valid Review `verdict=fail` | `blocked` | 1 | 0 |
| valid Human `decision=rejected|revoked` | `blocked` | 1 | 0 |
| unsafe／existing／scope外 decision artifact destination | `blocked` | 1 | 0 |
| Review `pass`、Human `approved` with both authorizations、全cross-binding valid | transaction preflightへ継続 | not yet ready | 0 until staging begins |

`pass`または`approved`単独では`ready`にしない。mode reinterpretation、waiver、silent fallback、missing field default、unknown-key ignoreを行わない。
````

## Design replacement D-04 — replace all of `### 4.5 Readiness Result`

````markdown
### 4.5 Readiness Result

```text
ReadinessResult = conjunction(
  valid PlanningReviewResultV1 with verdict = pass,
  valid PlanningHumanDecisionV1 with
      decision = approved,
      plan_adoption = true,
      implementation_start = true,
  exact review_result_sha256 binding,
  exact ReviewedPlanningIdentityV1 object and digest binding,
  apply-time source freshness,
  mode-specific parity,
  validation,
  Planning publication remote parity
)
```

専用state storeへ永続化せず、current Git／GitHub、exact external evidence bytes、canonical decision artifact、canonical filesから再構成する。いずれか一項だけ、またはReview／Human evidenceの構造上validなnegative decisionだけでは`ready`を導出しない。
````

## Design replacement D-05 — replace all of `### 4.6 Apply Request and Operation Identity`

````markdown
### 4.6 Apply Request and Operation Identity

```text
PlanningApplyRequest
- issue_id / repository / branch / expected_head
- mode = archive-candidate | git-bound
- reviewed_identity = validated ReviewedPlanningIdentityV1
- reviewed_identity_sha256
- review_result_path
- review_result_bytes = one read of the external file
- review_result_sha256 = sha256(review_result_bytes)
- review_result = validated PlanningReviewResultV1 parsed from the same bytes
- human_decision_path
- human_decision_bytes = one read of the external file
- human_decision_sha256 = sha256(human_decision_bytes)
- human_decision = validated PlanningHumanDecisionV1 parsed from the same bytes
- decision_artifact_repo_path
- archive identity:
    candidate_path / logical_filename / external_zip_sha256
  or git identity:
    reviewed_head / exact_target_paths / base
- output_directory

PlanningApplyOperation
- operation_id = sha256(canonical JSON of:
    issue_id,
    repository,
    branch,
    expected_head,
    mode,
    reviewed_identity_sha256,
    review_result_sha256,
    human_decision_sha256,
    decision_artifact_repo_path)
- phase = preflight | staged | replaced | validated | committed | pushed | verified
- planning_commit trailer = SpecDock-Planning-Operation: <operation_id>
```

operation IDはtimestamp、host path、output directory、process IDを含めず、same reviewed identity／exact Review bytes／exact Human decision bytes／source binding／destinationからpureに導出する。

`review_result_sha256`と`human_decision_sha256`はCLI supplied literalを信用せず、Runtimeが一回だけ読み込んだbytesから計算する。Human decision内の`review_result_sha256`はactual Review-result bytesと一致しなければならない。

positive authority gate通過後だけ、`human_decision_bytes`を`decision_artifact_repo_path`へbyte-exactにstageする。Review result、Human decision、identity、source、destinationのvalidation中はcanonical tree、index、HEAD、operation manifestを変更しない。

external output directory配下のoperation-local directoryはstage、backup、recovery manifestだけを保持し、global registryとして列挙・検索する機能を持たない。§5.1のtransaction、rollback、recovery、post-commit resume、remote-divergence semanticsを変更しない。
````

## Design replacement D-06 — replace all of `## 10. Human Gate and Adoption`

```markdown
## 10. Human Gate and Adoption

- `PlanningReviewResultV1`はHuman decisionの入力であり、単独ではstart authorityではない。
- archive Human decisionはexact archive `ReviewedPlanningIdentityV1`、そのdigest、exact Review-result file SHAへbindする。
- git-bound Human decisionはexact repository／branch／reviewed HEAD／target paths／base identity、そのdigest、exact Review-result file SHAへbindする。
- positive Human gateは`PlanningHumanDecisionV1`の`decision=approved`、`plan_adoption=true`、`implementation_start=true`が同時に成立する場合だけである。partial approvalを許可しない。
- validな`rejected`または`revoked` decisionはnegative durable evidenceであり、adoption／implementation startを許可せず、`planning apply`はrepository mutation前に`blocked`を返す。
- MainだけがHuman-supplied evidenceを確認して`planning apply`を起動する。CLI／RuntimeはReview verdict、Human decision、approver identity、missing field、modeを生成・推測しない。
- Runtimeはshared transaction primitiveでcanonical filesとnew decision artifactを処理し、Main authority下でGit commit／pushを行う。unexpected Candidate-external diffは0でなければならない。
- RuntimeはPA-NF-01〜PA-NF-10を独立に拒否する。
- Candidate adoptionやreadinessの副作用として`.assurance.json`を変更しない。
```

# 3. Exact Plan blocks to replace or add

## Plan replacement P-01 — replace all of `## 2. Plan Readiness and Stop Gate`

```markdown
## 2. Plan Readiness and Stop Gate

Implementationは次がすべて成立するまで開始しない。

- one exact `ReviewedPlanningIdentityV1`が次のどちらかとして確定していること。
  - archive-candidate: exact logical filename、observed transport filename、ZIP SHA、internal root、Candidate ID、source repository／branch／HEAD。
  - git-bound: exact repository、branch、reviewed HEAD、sorted unique target paths、必要なbase。
- 上記identity objectと`reviewed_identity_sha256`へbindされたfresh `PlanningReviewResultV1`があり、`reviewer_role=spec-reviewer`、`freshness=fresh`、`authority=read-only`、`verdict=pass`であること。
- 同じidentity object／digestおよびexact Review-result file SHAへbindされた`PlanningHumanDecisionV1`があり、`decision=approved`、`plan_adoption=true`、`implementation_start=true`であること。
- archive identityをgit-bound identityとして、またはgit-bound identityをCandidate identityとして再解釈していないこと。mode切替、waiver、silent fallbackはnew reviewed identityとfresh Review／Human decisionなしでは禁止する。
- Mainによるcanonical adoption／source refresh／assurance classification and compositionが完了していること。
- adopted `requirement.md`／`design.md`／`plan.md`とfresh spec review evidenceが一致していること。
- clean named branch、upstream、local HEAD == remote HEAD、no unresolved ledger entryであること。
- planning repair baseline `eadbfa544ad972c799162552f5684482d26e89b5`以降のrelevant implementation source manifestにdriftがないこと。planning docs／report／assuranceだけのcommitであっても、current三文書hash、reviewed identity、Review result、Human decisionをcurrent HEADへ再束縛すること。
- archive Candidate source、git-bound reviewed HEAD／target blobs、またはimplementation-relevant sourceがReview後に変化した場合は`stale`とし、new Candidateまたはnew git-bound Review identityを取得すること。

不足時は`blocked`、`stale`、`rejected`、または`未完了`としてMainがreason／next actionをCandidate外reportへ記録する。
```

## Plan replacement P-02 — replace the S01 row in `## 6. Step Summary`

```markdown
| S01 | Independent CLI walking skeleton including public `planning apply` help contract and exact positive／negative Issue target resolution | mode-neutral exact reviewed planning identity、fresh `PlanningReviewResultV1` pass、same-identity `PlanningHumanDecisionV1` approval for Plan adoption and implementation start | S02A | AC-002, AC-003 (target-resolution portion) |
```

## Plan replacement P-03 — replace the indicated Closure Index rows

```markdown
| `CLOS-ADOPTION` | REQ-009–012 / AC-008,009 | validated Review v1 + Human decision v1 + exact reviewed identity | closed evidence schemas, sole public transactional apply, and remote-equal publication | unbound authority／partial adoption／hidden mutation | S06 | no | summary | `tc-s06-001`, `tc-s06-002`, `tc-s06-009`, `tc-s06-010` | `report.md#Step-Contract-Closure` |
| `CLOS-READINESS` | REQ-013,014 / AC-010,013 | valid Review pass／Human dual authorization／identity／parity／validation／publication | only full typed conjunction returns ready | review-only／Human-only／schema-invalid start | S06/S08 | no | summary | `tc-s06-003[*]`, `tc-s06-009`, `tc-s06-010`, `tc-s08-001` | `report.md#Step-Contract-Closure` |
```

```markdown
| `CLOS-REQ-009` | REQ-009 / AC-008,009 / Design §§3,4.3–4.6,5 | exact `PlanningReviewResultV1` + exact `PlanningHumanDecisionV1` + same reviewed identity | `planning apply` is sole supported route; both archive and git-bound identities are admitted without reinterpretation | ad-hoc internal call／Candidate-only gate／partial authority | S01/S06 | yes | red-required | apply help + `tc-s06-001`, `tc-s06-002`, `tc-s06-009`, `tc-s06-010` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-015` | REQ-015 / AC-013 / Design §4.4 | exact Review bytes／exact Human decision bytes／decision artifact／result JSON | Human decision cross-binds exact Review SHA and identity; positive bytes alone are copied; no transcript or authority registry | evidence substitution／authority conflation／partial approval | S06 | yes | red-required | `tc-s06-009`, `tc-s06-010`, state-boundary assertions | `report.md#Test-Contract-Closure` |
```

```markdown
| `CLOS-EC-001` | EC-001 | known-valid target or invalid target／Git preflight | valid Issue resolves exact repo root／Issue path／parent／dependency with fallback absent; invalid source blocks before backend/mutation | wrong source resolution／default fallback | S01/S03 | yes | red-required | `tc-s01-002`, `tc-s01-003`, `tc-s03-002` | `report.md#Test-Contract-Closure` |
| `CLOS-EC-005` | EC-005 / Design §4.4.3 | malformed／negative／mismatched／stale Human evidence or destination | schema/cross-binding mismatch is `rejected`; current source drift is `stale`; rejected/revoked authority is `blocked`; mutation 0 | approval bypass／wrong status masking | S06 | yes | red-required | `tc-s06-003[pa-nf-03,05,06,07]`, `tc-s06-009`, `tc-s06-010` | `report.md#Test-Contract-Closure` |
```

```markdown
| `CLOS-PA-NF-01` | PA-NF-01 | valid archive Review v1 pass only | `blocked`, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01]`, `tc-s06-010[review-only-archive]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-02` | PA-NF-02 | valid git-bound Review v1 pass only | `blocked`, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-02]`, `tc-s06-010[review-only-git]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-03` | PA-NF-03 | valid Human approved decision without exact Review file | `blocked` or digest-binding `rejected`, mutation 0 | approval-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-03]`, `tc-s06-010[human-only]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-04` | PA-NF-04 | parity only | non-ready | parity-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-04]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-05` | PA-NF-05 | wrong archive logical filename or ZIP SHA in any binding surface | `rejected`, mutation 0 | Candidate substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-05]`, `tc-s06-010[wrong-archive-identity]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-06` | PA-NF-06 | wrong git-bound reviewed HEAD or target paths in any binding surface | `rejected`, mutation 0 | git target substitution | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-06]`, `tc-s06-010[wrong-git-identity]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-07` | PA-NF-07 | previously valid identity followed by current source drift | `stale`, mutation 0 | stale approval reuse | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-07]`, `tc-s06-010[stale-source]` | `report.md#Test-Contract-Closure` |
```

## Plan replacement P-04 — replace S01 `depends on / unblocks`

```markdown
#### depends on / unblocks

- depends on: mode-neutral exact `ReviewedPlanningIdentityV1`、fresh bound `PlanningReviewResultV1` pass、same-identity `PlanningHumanDecisionV1` with both Plan-adoption and implementation-start authorization
- unblocks: S02A
```

## Plan replacement P-05 — replace S01 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: four-command public help、known-valid Issueのexact positive target resolution、unknown Issueのfail-closed resolution、source contract、regressionを検証する。
- positive target oracle: known-valid fixtureはrepo root、canonical Issue path、parent Epic／Initiative、declared dependencies、explicit branch／HEADをexactに返し、default branch、active alias、attached／tracked file、first-match searchへのfallbackがないことを観測する。
- red or alternative evidence requirement: red-required: current source has no `spec-dock-chatgpt` entrypoint、public command family、またはapproved exact target-resolution contract。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

Replace the S01 delegation acceptance-criteria line with:

```markdown
- acceptance criteria: `AC-002`, `AC-003`のtarget-resolution portion
```

## Plan replacement P-06 — replace `tc-s01-002` and add `tc-s01-003` immediately after it

```markdown
- `tc-s01-002` negative: unknown targetをfail closedにする
  - 前提: Issue registry／canonical treeに存在しないIDを指定する。
  - 操作: planning createのtarget-resolution phaseを実行する。
  - 期待結果: backend起動前にstable nonzeroとなり、filesystem mutationは0、default branch／active alias／attached file／first-match fallbackは0。
  - 失敗検出: target誤解決とbackendへの不正context送信を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-EC-001`

- `tc-s01-003` acceptance: known-valid Issueをexactに解決する
  - 前提: temp managed repositoryにknown-valid Issue、parent Epic／Initiative、declared dependency、explicit named branch／HEADを用意する。別locationに同じ短縮IDまたはfallback候補を置く。
  - 操作: backendを起動せずplanning createのtarget-resolution phaseを実行する。
  - 期待結果: resolved repository root、canonical Issue path、parent Epic ID、parent Initiative ID、dependency set、explicit branch／HEADがfixtureとexact一致し、`fallback_used=false`相当を観測する。別location、default branch、active alias、attached／tracked fileは選択されない。
  - 失敗検出: positive pathが偶然のfirst match、default fallback、parent／dependency omissionでGreenになることを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-EC-001`
```

## Plan replacement P-07 — replace S01 `step closure contract`

```markdown
#### step closure contract

`CLOS-CLI`、`CLOS-REQ-002`、`CLOS-EC-001`およびClosure IndexでS01をownerに持つ全`required=yes` rowは、four-command help Green、unknown-target negative Green、known-valid exact target-resolution positive Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。
```

## Plan replacement P-08 — replace S03 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: exact Git preflight、backend non-invocation on source mismatch、complete three-document response validation、planning-specific direct argv capture、planning-specific redaction、no repository mutation。
- planning-specific argv／redaction fixture owner: `tests/unit/application/test_issue_planning.py`または`tests/integration/test_chatgpt_planning_fake_oracle.py`のS03 allowed pathだけ。authoring-pack fixtureをS03 Red ownerにしない。
- red or alternative evidence requirement: red-required: fake backend create、planning-specific argv capture、またはredaction assertionがGit／source／response／invocation validation実装前に失敗する。
- owned Green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- covered-existing regression: `uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q`。このfileは変更せず、new planning fixtureを追加せず、S03 closureのRed evidenceとして数えない。failureはshared primitive regressionとしてS03 integrationをblockする。
- refactor guardrail: Green後のbounded tidyだけ。Candidate packaging、archive identity、new persistent state、shared policy、unrelated cleanupをこのstepへ追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

Replace the S03 delegation verification line with:

```markdown
- required tests or docs-only verification:
  - owned: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
  - covered-existing, read-only: `uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q`
```

## Plan replacement P-09 — replace `tc-s03-003`

```markdown
- `tc-s03-003` security: planning Prompt／path／operator contextをdirect argvで扱い、diagnosticをredactする
  - 前提: shell metacharacterを含むoperator contextとpath、secret-like sentinel、argv-capturing fake backendをplanning application fixtureとして用意する。
  - 操作: planning createのdry-run backend invocationを行い、captured argvとbounded diagnosticを取得する。
  - 期待結果: untrusted valuesはindividual argv elementsとしてbyte-preservingに渡され、shell executionは0。secret-like sentinelはdiagnostic、result、Planner responseへ出現しない。
  - 失敗検出: command injection、planning-specific argv regression、diagnostic leakageを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`, `CLOS-REQ-021`
```

## Plan replacement P-10 — replace S03 `step closure contract` and `step gate`

````markdown
#### step closure contract

`CLOS-GIT`, `CLOS-SEC`, `CLOS-REQ-003`, `CLOS-REQ-021`のS03 portion、`CLOS-EC-001`, `CLOS-EC-002`のS03 portion、およびClosure IndexでS03をownerに持つ全`required=yes` rowは、planning-owned source／response／argv／redaction testsのtargeted Green、covered-existing Git fetch policy regression Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。`tests/unit/authoring_pack/test_github_fetch_policy.py`はcovered-existingであり、S03 planning fixture、allowed edit、Red ownerにはしない。`CLOS-CREATE`と`CLOS-REQ-004`はS05までopenのままにする。

#### step gate

次を双方成功させる。

```bash
uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q
uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q
````

scope外diff 0、`tests/unit/authoring_pack/test_github_fetch_policy.py` diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

````

## Plan replacement P-11 — replace S06 `behavior goal`

```markdown
#### behavior goal

public `planning apply`からclosed `PlanningReviewResultV1`と`PlanningHumanDecisionV1`を検証し、同じexact reviewed identity、exact Review-result SHA、Human dual authorizationへbindしたtransactional mode-specific adoption、parity、validation、publicationを実行し、その論理積だけからreadinessを導出する。
````

## Plan replacement P-12 — replace S06 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- evidence schema obligation: `domain/issue_planning_contracts.py`へclosed named `PlanningReviewResultV1`／`PlanningHumanDecisionV1` validationを実装する。required key exact、unknown／duplicate key reject、closed enum、strict UTC timestamp、mode-specific identity、canonical identity digest、exact Review file SHA cross-binding、Human decision truth tableをDesign §§4.3–4.4どおり固定する。
- no-new-subsystem obligation: external JSON Schema registry、receipt registry、database、custom Git ref、general approval frameworkを追加しない。existing digest、approval、Git preflight primitivesをbounded reuseする。
- public contract: `planning apply`はDesign §3のexact argsを受け、`ready`だけexit 0、`blocked|stale|rejected|rolled_back|publication_pending|blocked_remote_diverged|recovery_required`はexit 1でtext／JSON同一statusを返す。
- pre-mutation status contract:
  - malformed／wrong version／wrong kind／unknown key／duplicate key／invalid enum／timestamp／digestは`rejected`。
  - Review／Human／CLI modeまたはidentity mismatch、Review file SHA mismatchは`rejected`。
  - validated identityに対するcurrent source driftは`stale`。
  - valid Review `fail`、valid Human `rejected|revoked`は`blocked`。
  - すべてrepository mutation 0。
- transaction obligation: all inputs and staged bytesをmutation前に検証し、new decision artifact→`requirement.md`→`design.md`→`plan.md`をshared scoped transactionで処理する。commit前の各fault pointはreverse-order restoreとbaseline verificationを行う。
- recovery obligation: operation ID、atomic recovery manifest、commit trailer、tree digestでidempotencyを固定する。commit後はautomatic rollbackせず、push failure／response lossを`publication_pending`としてsame-operation retryする。remote divergenceは`blocked_remote_diverged`で停止する。
- shared reuse obligation: `runbook_store.py`のstage／backup／restoreを`scoped_file_transaction.py`へ抽出し、existing runbook testsをcharacterizationとして先にGreenにする。private helper import／duplicate transactionは禁止する。
- test obligation: Review v1 schema matrix、Human decision v1 truth table、exact Review SHA binding、archive／git identity cross-binding、wrong mode／identity／stale source status mapping、public CLI E2E、archive／git positive、PA-NF 10 independent rows、replacement／validation／commit fault、rollback failure、crash resume、push retry、remote divergence、runbook regression、state boundaryを検証する。
- red or alternative evidence requirement: red-required: current approval check is evidence-only and does not implement the closed evidence schemas or the complete E1-I1 readiness conjunction.
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_scoped_file_transaction.py tests/unit/infra/test_runbook_store.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Green後のbounded tidyだけ。Designで承認済みのclosed evidence validation、`planning apply`、shared scoped transaction以外のpublic contract／shared policy／unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

## Plan addition P-13 — add after `tc-s06-008`

```markdown
- `tc-s06-009` contract: `PlanningReviewResultV1`のclosed schemaを検証する
  - 前提: valid archive identity、valid git-bound identityと、named negative fixtures `review-wrong-version`、`review-wrong-kind`、`review-missing-key`、`review-unknown-key`、`review-duplicate-key`、`review-wrong-role`、`review-wrong-freshness`、`review-wrong-authority`、`review-invalid-verdict`、`review-invalid-time`、`review-identity-digest-mismatch`を用意する。
  - 操作: 各JSON bytesをReview-result validatorへ渡し、同じbytesのSHA-256を取得する。
  - 期待結果: archive／git positiveはexact parsed identityとdigestを返す。named negativeは全件`rejected`、exit 1、repository／index／HEAD／operation manifest mutation 0。`verdict=fail`はschema上validとしてparseされ、authority gateでだけ`blocked`になる。
  - 失敗検出: permissive versioning、unknown-key tolerance、wrong reviewer authority、digest substitution、mode-neutral field unionによるambiguous identityを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`, `CLOS-REQ-015`

- `tc-s06-010` contract: Human decision truth table、exact Review SHA、mode-neutral start gateを検証する
  - 前提: valid archive／git Review v1 pass、各exact Review file SHA、same-identity Human decisionと、named fixtures `approved-archive`、`approved-git`、`partial-plan-only`、`partial-start-only`、`wrong-review-sha`、`wrong-mode`、`wrong-archive-identity`、`wrong-git-identity`、`stale-source`、`review-fail`、`human-rejected`、`human-revoked`、`revoked-missing-prior-sha`、`review-only-archive`、`review-only-git`、`human-only`を用意する。
  - 操作: `planning apply` pre-mutation validation／authority evaluationを各parameterで実行する。
  - 期待結果:
    - `approved-archive`と`approved-git`だけがtransaction preflightへ進む。両方とも`plan_adoption=true`かつ`implementation_start=true`を要求する。
    - partial authorization、wrong Review SHA、wrong mode、cross-document identity mismatch、invalid revocationは`rejected`。
    - valid identity後のcurrent source driftは`stale`。
    - valid Review `fail`、Human `rejected`、Human `revoked`、Review-only、Human-onlyは`blocked`。
    - 全negative parameterでcanonical files、decision artifact、index、HEAD、operation manifest mutationは0。
  - 失敗検出: Candidate-only gate、git-bound exclusion、partial Human approval、Review file substitution、stale approval reuse、negative decisionの誤authorizationを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`, `CLOS-REQ-015`, `CLOS-EC-005`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-07`
```

## Plan replacement P-14 — replace S06 `step closure contract` and `step gate`

````markdown
#### step closure contract

`CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`〜`CLOS-REQ-016`のS06 portion、`CLOS-EC-005`〜`CLOS-EC-009`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10`, `CLOS-RISK-001`, `CLOS-RISK-004`, `CLOS-RISK-005`のS06 portion、およびClosure IndexでS06をownerに持つ全`required=yes` rowは、次がすべて揃った場合だけcloseする。

- `PlanningReviewResultV1` archive／git positive 2/2。
- Review schema named negative matrix全件。
- `PlanningHumanDecisionV1` approved／rejected／revoked truth table全件。
- exact Review-result SHAおよびreviewed identity object／digest cross-binding。
- wrong mode／wrong identity=`rejected`、current source drift=`stale`、valid negative authority=`blocked`のstatus matrix。
- public CLI Green。
- PA-NF 10/10 named results。
- 全pre-commit fault rollback、rollback-failure stop、push resume、remote-divergence stop。
- runbook regression。
- required reviewer pass。
- commit候補または正当なapproved-no-op。
- post-commit clean check。

#### step gate

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_scoped_file_transaction.py \
  tests/unit/infra/test_runbook_store.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_chatgpt_planning_fake_oracle.py \
  -q
```

scope外diff 0、Review schema matrix全件、Human truth table全件、archive／git approved positive 2/2、PA-NF 10/10、fault matrix全件、existing runbook unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。
````

# 4. Acceptance tests and traceability impact

| Finding closed by the blocks                                | Primary acceptance evidence                                           | Allowed test ownership                                                                                | Traceability impact                                                                                                 |
| ----------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Apply Review-result schema                                  | `tc-s06-009`                                                          | `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py` | `REQ-009`, `REQ-015`, `AC-008`, `AC-009`, `AC-013`, `CLOS-ADOPTION`, `CLOS-READINESS`                               |
| Human-decision schema, dual authorization, exact Review SHA | `tc-s06-010`                                                          | Existing S06 domain/application/integration paths                                                     | `REQ-009`, `REQ-015`, `EC-005`, PA-NF-01–07                                                                         |
| Archive or git-bound Plan start gate                        | `tc-s06-010[approved-archive,approved-git]` plus Plan gate inspection | Existing S06 paths; no new subsystem or path                                                          | Makes the gate identity-neutral while retaining exact repository／branch／HEAD／Candidate／target binding               |
| Positive S01 target resolution                              | `tc-s01-003`                                                          | `tests/unit/domain/test_issue_planning_contracts.py`                                                  | `AC-003` target-resolution portion and `CLOS-EC-001`; no transfer of Git preflight ownership from S03               |
| S03 argv/redaction ownership                                | Rewritten `tc-s03-003`                                                | `tests/unit/application/test_issue_planning.py`                                                       | `REQ-021`, `AC-011`, `CLOS-SEC`; the fixture now sits inside the S03 allowlist                                      |
| Existing Git-fetch policy                                   | Existing suite only                                                   | `tests/unit/authoring_pack/test_github_fetch_policy.py` remains unchanged                             | `covered-existing`; it may block integration on regression but supplies no S03 Red and receives no planning fixture |

No Requirement semantics or Requirement IDs need replacement. The current Requirement already requires an exact reviewed identity, both archive and git-bound positive chains, exact Human Plan-adoption and implementation-start authorization, and fail-closed status behavior.

After Main integrates these Design and Plan blocks, the changed document bytes require:

1. `.assurance.json` rebinding to the new canonical Requirement／Design／Plan hashes.
2. `report.md` ledger entries for the adopted correction and resulting source HEAD.
3. A new remote snapshot.
4. A separate fresh read-only review of that snapshot.

Those follow-up mutations are deliberately not included here; the review artifact assigns them to Main after bounded correction.

No implementation tests were executed in this thread. The listed tests are replacement-ready planned acceptance contracts, not observed Green evidence.

# 5. Self-check against previously closed controls

* **Explicit public apply:** retained and strengthened; `planning apply` remains the only supported post-Human-gate public route.
* **Crash-safe transaction/recovery:** Design §5.1 and all S06 rollback, recovery-manifest, post-commit resume, and remote-divergence behavior remain unchanged.
* **Twenty-five archive safety classes:** `CLOS-ARC-01` through `CLOS-ARC-25`, inclusive ceilings, and partial-output-zero rules are untouched.
* **Schema-complete Closure Index:** its columns, required rows, ownership, and evidence-destination structure remain intact; only the rows directly affected by the four findings are refined.
* **S02A/S02B:** docs ownership and structural-test ownership remain separate and unchanged.
* **S09A/S09B:** hermetic worker test and Human/Main live-operation gate remain separate and unchanged.
* **Source binding:** not weakened. Archive identity retains Candidate and source binding; git-bound identity requires repository, branch, reviewed HEAD, exact paths, and optional closed base identity. Cross-mode reinterpretation is expressly rejected.
* **Canonical-state and evidence boundaries:** no new authority registry, database, custom Git ref, transcript store, or `.assurance.json` product mutation is introduced.
* **Assurance and Report evidence:** authority remains external to Candidate/application flow; Main must rebind Assurance and update Report after document adoption.
* **One-Issue/one-branch/one-PR workflow:** unchanged; S99 still hands off to the existing shared delivery workflow and Human-only merge boundary.
* **Repository state:** unchanged by this response.
