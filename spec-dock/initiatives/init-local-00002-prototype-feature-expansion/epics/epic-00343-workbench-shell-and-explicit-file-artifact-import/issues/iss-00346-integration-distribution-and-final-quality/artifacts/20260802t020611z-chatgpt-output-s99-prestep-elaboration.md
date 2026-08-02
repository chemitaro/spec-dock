# S99 Final-Quality Pre-Step Memo

## 現在の起点と権威境界

GitHub connector で `chemitaro/spec-dock` の current branch `iss-00346-integration-distribution-and-final-quality` を確認し、branch HEAD と指定 SHA `fac1776ccd0a5285185602b04c2278eb4177414f` の比較結果は `identical` だった。この SHA は **S99 の開始 HEAD** であり、test evidence、report、review Artifact の追加後に作られる **final review HEAD ではない**。

現状は S01〜S04とS90 combined code/spec reviewまで完了し、S99のfast/full regression、統合QA/code/spec review、PR handoff、Merge Preparationは未完了である。したがって、本メモはS99 pass、PR mergeability、Issue/Epic closureを主張しない。

canonical `requirement.md`、`design.md`、`plan.md`、accepted ADRを正本とし、本メモはGPT-5.6 Luna・推論Max向けのadvisory execution aidに限定する。Issue reportとEpic reportはobserved evidence ledgerであり、正本を変更しない。   

---

## 1. S99の厳密な実行順序とstop gate

### 1. 開始HEAD gate

1. repository、branch、local HEAD、remote branch HEADを取得する。
2. 開始時はすべて `fac1776ccd0a5285185602b04c2278eb4177414f` と一致させる。
3. `git status --short` が空であることを確認する。
4. 既存のignored build/workbench outputはinventoryし、candidate outputとの混同を防ぐ。

次の場合は直ちに停止する。

* local/remote/GitHub branch HEADの不一致
* 未帰属のtracked変更
* review済みS90状態とcanonical reportの矛盾
* requirement/design/ADR変更が必要な状態

### 2. Final candidate execution receipt

S99のtest対象となるpushed HEADを `execution_head` として固定する。HEAD、status、wheel sourceをrun前後で再確認する。

S01以後にHEADが動いているため、final candidate wheelは現在のcandidate sourceから再生成し、少なくとも次を記録する。

* `execution_head`
* wheel basename、version、SHA-256
* clean build receipt
* sorted inventoryとREADME allow/deny result
* isolated installed origin
* source checkout fallbackがないこと
* pre/post HEAD一致

wheel、test、provider/runtime inputのいずれかがrun中に変わった場合、そのrunはstaleとして破棄する。

### 3. Focused closure rerun

aggregate suiteだけでは原因が隠れるため、S01〜S04の主要focused suitesを先に実行する。

最低限、次を独立receiptにする。

* candidate wheel / fresh consumer
* existing consumer update / no-backfill / future shell
* target、external privacy、cross-filesystem、platform publisher
* opaque lifecycle、projection/context equality
* legacy compatibilityとshared-slot allocation
* disposable dogfood no-backfill、future shell、generic import
* provider→dogfood parity

focused failure、controlled negativeの非感応、fixture不正、expected status manifest不一致はすべてstopである。

### 4. Ordinary fast lane

`make lint` と通常の `uv run pytest` を実行する。

通常runでfull-regression対象がpolicy skipされること自体はfast laneの失敗ではないが、**そのskipをfull regressionの成功として扱ってはならない**。fast lane receiptとfull lane receiptは必ず別にする。

### 5. Explicit full-regression lane

別commandとして必ず次を実行する。

```bash
uv run pytest --run-full-regression
```

既知のfull-regression test bodiesが実際に実行されたことをcollection/resultから確認する。flagの付け忘れ、marker-only collection、required testのpolicy skip、timeoutの隠蔽、selector omissionはfull passではない。

full suiteに1件でもfailureがあれば、fast laneが成功していてもS99は停止する。

### 6. Validation、sync、platform freshness

次を実行する。

* `spec-dock validate`
* `sync --no-github`
* provider/dogfood diff
* existing `epic-00343` no-backfill再確認
* diff/status clean checks

S03 actual Linux、macOS、cross-filesystem evidenceについて、`execution_head`までの変更が次のいずれかに触れていないか確認する。

* publisher、import application、domain、ports/contracts
* platform probeまたはplatform test oracle
* privacy/publication semantics
* provider runtime sourceまたは実行されるprojection

影響がある場合はactual Linux/macOS/cross-FS lanesを再実行する。影響がないと判断する場合も、比較したcommit range、changed paths、既存host evidence refs、非影響理由をreportに残す。`unavailable`やhermetic simulationはrequired actual-host successの代替にならない。

### 7. Evidence integrationとreview freeze

test結果をIssue/Epic reportへ統合した後、commit/pushし、これを `review_head` とする。

`execution_head..review_head` がreport/evidence-only successorであることを確認する。provider、runtime、tests、test oracle、canonical R/D/Pが変化していれば、先のtest evidenceをstaleとし、手順2から再開する。

その後、次を行う。

1. decision/EAL/closure rowsに未解決の`open`、`stale`、`blocked`がないことを確認する。
2. Issue/Epic reportのreviewer evidence fieldsを空値に正規化する。
3. review packageのrepo-relative path manifestを作る。
4. sorted pathとnormalized bytesから`review_content_hash`を計算する。
5. manifest、hash、`review_head`を固定し、push済み状態を確認する。

既存helperがない場合の決定的な実装例は、SHA-256 over:

```text
UTF8(repo-relative-path) || NUL || uint64_be(byte_length) || file_bytes
```

をpath昇順で連結したstreamとする。hash fieldまたはmanifest自身を自己参照させず、入力対象外として明示する。

hash計算後のcontent mutationはfreezeを無効化する。

### 8. Single-thread combined review

同一ChatGPT Pro conversation/threadで、QA、code、specの3観点を同時にレビューする。

review開始前に必ず次を確認する。

* GitHub connector上のbranch HEAD = `review_head`
* local/remote HEAD一致
* `review_content_hash`一致
* current QA/code/spec Developer Instructionsがすべて完全に添付されている
* fast/full evidenceが分離されている
* required full bodiesとrequired host evidenceが存在する

3観点のいずれかが`fail`または`blocked`なら統合passにしない。未解決P0/P1が1件でもあれば停止する。

### 9. Review transcription、final push、PR handoff

3観点すべてがpassし、未解決P0/P1が0の場合だけ、外部review出力から次の限定fieldをreportへ転記できる。

* role perspective
* ChatGPT session/thread ID
* status
* findings count
* review scope
* `observed_at`
* mechanical gate state

転記後、reviewer fieldsを再び空値へ正規化して`review_content_hash`を再計算し、freeze時と一致させる。それ以外の変更またはhash不一致があれば、commit/pushし、同じthreadのfresh follow-up reviewへ戻る。

最終commit/push後にremote HEADを確認し、existing PRを再利用するか新規PRを作成する。その後にMerge Preparationを観測する。agentはmergeしない。

---

## 2. Fast laneとfull laneの必須証跡

| 項目                  | Ordinary fast lane                                           | Explicit full lane                                |
| ------------------- | ------------------------------------------------------------ | ------------------------------------------------- |
| Command             | `make lint`、`uv run pytest`                                  | `uv run pytest --run-full-regression`             |
| Head binding        | pre/post HEADとremote binding                                 | pre/post HEADとremote binding                      |
| 必須result            | exit code、pass/fail、skip、xfailed/xpassed、deselected、duration | 同左に加え、required full nodesが実行された証拠                 |
| Skipの扱い             | policy skipを明記。fast passは可能                                  | required full bodyのpolicy skip/unavailableはpass不可 |
| Collection evidence | summaryでよい                                                   | known full nodesのcollectionとbody resultを照合        |
| Failure semantics   | failureでS99 stop                                             | 1 failureでもS99 stop。fast passで相殺不可                |
| Report wording      | `fast_pass`と`full_not_yet_proven`を区別                         | `full_pass`は明示commandのbody成功時のみ                   |

各receiptには次を含める。

* exact command
* `execution_head`
* started/finishedまたは`observed_at`
* exit status
* test counts
* duration
* skip対象と理由
* logまたはArtifact reference
* required test nodesの実行確認
* pre/post HEAD同一
* production/test input mutationの有無

---

## 3. Single-thread QA/code/spec review prompt

以下を1つのpromptとして使用する。3つのDeveloper Instructionsは要約せず、実行時点のcurrent内容をそれぞれ所定位置へ**全文そのまま**挿入する。欠落、切り詰め、旧版しかない場合はreviewを開始せず`blocked`とする。

```markdown
# Issue 346 — S99 Single-Thread Final QA / Code / Spec Review

## Binding

Repository: chemitaro/spec-dock
Branch: iss-00346-integration-distribution-and-final-quality
Base branch: main
S99 start HEAD: fac1776ccd0a5285185602b04c2278eb4177414f
Expected review HEAD: <FULL_REVIEW_HEAD_SHA>
review_content_hash: sha256:<REVIEW_CONTENT_HASH>
review manifest: <REPO_RELATIVE_OR_ATTACHED_MANIFEST_REFERENCE>

Review lane:
- ChatGPT Pro
- wrapper receipt must record:
  - requested=Pro
  - resolved=Pro
  - verified=yes
- Do not claim an underlying exact model version unless separate evidence verifies it.

## Hard preflight

1. Use the GitHub connector before reviewing.
2. Resolve the current branch and compare it with Expected review HEAD.
3. If the branch is not identical to Expected review HEAD, return BLOCKED:
   stale_head. Do not review older content.
4. Verify the supplied review manifest and review_content_hash.
5. If any path/byte/hash is missing or mismatched, return BLOCKED:
   review_content_hash_mismatch.
6. Confirm that ordinary `uv run pytest` and explicit
   `uv run pytest --run-full-regression` have separate receipts.
7. A policy skip, unavailable required host, omitted selector, or unexecuted
   full-regression body is not a pass.
8. Treat canonical requirement/design/plan and accepted ADRs as authoritative.
   Reports and ChatGPT Artifacts are evidence only.
9. Do not modify files. Do not claim PR mergeability, merge, Issue completion,
   Epic closure, or S99 success beyond the reviewed evidence.

## Reviewer Developer Instructions — QA

<<INSERT THE CURRENT QA-REVIEWER DEVELOPER INSTRUCTIONS VERBATIM>>

## Reviewer Developer Instructions — Code

<<INSERT THE CURRENT ISSUE/EPIC-WIDE CODE-REVIEWER DEVELOPER INSTRUCTIONS VERBATIM>>

## Reviewer Developer Instructions — Spec

<<INSERT THE CURRENT SPEC-REVIEWER DEVELOPER INSTRUCTIONS VERBATIM>>

## Required review package

Inspect all of the following:

- canonical Issue 346 requirement/design/plan/report;
- parent Epic 343 requirement/design/plan/report;
- accepted generic identity/privacy, macOS cleanup, and Linux anonymous-staging
  ADRs;
- Issue 344 and Issue 345 completion/dependency evidence;
- exact `main...Expected review HEAD` diff and complete changed-path list;
- changed-path-to-closure and repair-boundary matrix;
- final candidate wheel receipt and installed-origin evidence;
- S01–S04 focused test receipts;
- ordinary fast-lane receipt and policy skip summary;
- explicit full-regression receipt and proof that required bodies executed;
- Linux, macOS, and cross-filesystem receipts, or a source-backed
  non-invalidation determination;
- provider-to-dogfood parity and no-backfill evidence;
- validate, sync, diff-check, clean-status, and local/remote-head receipts;
- complete EAL/decision/closure state;
- review manifest and review_content_hash.

## Independent perspectives

### QA perspective

Determine whether every required closure has current, reproducible evidence.

Focus on:
- end-to-end wheel/distribution truth;
- fixture validity and negative-control sensitivity;
- fast/full distinction;
- required host evidence;
- failure and retry semantics;
- missing, stale, skipped, or unavailable evidence.

Do not count a policy skip, simulation, or unsupported lane as success.

### Code perspective

Review the final diff against base and interaction with Issues 344/345.

Focus on:
- package/update/runtime/platform/lifecycle/compatibility behavior;
- no-backfill and provider-first ownership;
- privacy and opaque-body boundaries;
- Linux no-visible-fallback and macOS accepted exclusion;
- test-oracle validity;
- strict repair boundary and overimplementation.

No unresolved P0 or P1 is permitted.

### Spec perspective

Review consistency with the parent Epic, Issue 346 canonical R/D/P, accepted
ADRs, and delivery boundary.

Focus on:
- closure trace and evidence authority;
- no overclaim in Issue/Epic reports;
- durable decisions not stranded in reports;
- correct routing of requirement/design/ADR changes;
- PR handoff boundary and human-only merge.

## Finding requirements

Keep the three perspectives independent. For every finding provide:

- perspective;
- unique finding ID;
- severity P0, P1, P2, or P3;
- exact path/line, diff hunk, command receipt, or evidence reference;
- violated contract or closure;
- impact;
- minimum required action;
- whether the action is within the existing repair boundary.

P2/P3 findings may be recorded for human judgment, but by themselves do not
authorize branch mutation in the PR-preparation workflow.

## Integrated gate

The integrated review may be PASS only when:

- GitHub HEAD and review_content_hash both match;
- QA status is pass;
- code status is pass;
- spec status is pass;
- unresolved P0 count is 0;
- unresolved P1 count is 0;
- required full-regression bodies executed successfully;
- no required host or closure evidence is missing, stale, skipped, or
  unavailable.

Otherwise return FAIL or BLOCKED with the exact gate reason.

Preserve each attached reviewer instruction's required output contract. Return
one combined response containing the three independent role results and one
integrated gate summary.
```

---

## 4. Cheetahの扱い

D-003により、Cheetahは品質証跡として使用しない。

formal wrapperのdry-runではCheetah指定が`gpt-5.2`へ正規化されたため、Cheetah実行、Cheetah相当と推定した出力、またはCheetahを名乗る未検証出力をQA/code/spec gateへ採用してはならない。

次の出力も不採用とする。

* `detached`または`incomplete-capture`
* `promptSubmitted:null`
* 別Issueまたはstale HEADのharvest
* model resolutionが未確認のreview
* `resolved=Pro; verified=yes`を満たさないformal review receipt

ChatGPT Pro laneが利用不能なら、Cheetahや別modelで代替せず、S99を`blocked`にする。wrapperで確認できるのはcurrent Pro選択までであり、追加証跡なしに基盤model versionを検証済みと主張しない。

---

## 5. Bounded repair、re-push、re-review

Branch mutationを認めるのは次に限定する。

* reviewerが示したP0またはP1
* required CI/check failure
* required closureを直接阻害する再現可能なtest failure

P2/P3のみを理由としたmutationは禁止する。

repairを行う場合は次の順序を守る。

1. orchestratorがfindingを採否分類する。
2. root causeとowner closureを特定する。
   3.既存S01〜S04/S90のallowed pathまたはS99のbounded repair範囲に限定する。
3. requirement/design/ADR/ownership変更が必要なら実装せずEpic planning repairへ戻る。
4. finding-specific testを先に実行する。
5. affected focused suites、full regression、validate、syncを再実行する。
6. commit/pushし、local/remote/GitHub HEAD一致を確認する。
7. `review_content_hash`を再計算する。
8. 同じChatGPT threadへfollow-upし、QA/code/specの3観点すべてをfreshに再レビューする。

一部観点だけの旧passを持ち越さない。repair後は全体のexact-head/hash bindingを更新する。

---

## 6. PR handoff、Merge Preparation、human stop

Combined review passと限定転記後にのみ、final commit/pushへ進む。

PR handoffでは次を記録する。

* existing PR reuseまたはnew PR
* PR URL/number
* open/draft-ready state
* base branch
* head branch
* latest pushed SHA
* Issue #346 linkage
* duplicate PRがないこと
* observed timestamp

Merge Preparationでは次を観測する。

* required checksとnon-required checks
* reviewsとapproval state
* conflicts
* unresolved review threads
* connector/API上の観測制限
* blocker history
* latest-head binding

required check failure、P0/P1、conflict、stale observation、unresolved required threadはhuman/block stateとする。agentはmerge、auto-merge設定、branch削除を行わない。

最終stateには必ず次を含める。

```text
merge_performed_by_agent=false
handoff_state=human_merge_decision
```

---

## 7. 最低限のcommand queue

### Focused evidence

```bash
rm -rf dist build
uv build

uv run pytest \
  tests/integration/test_epic_00343_distribution.py \
  --run-full-regression

uv run pytest \
  tests/cli_runtime/test_artifact_import_s04.py \
  --run-full-regression

uv run pytest \
  tests/cli_runtime/test_artifact_import_chatgpt_output.py \
  tests/cli_runtime/test_workbench.py \
  tests/cli_runtime/test_artifact_import_file.py \
  --run-full-regression

uv run pytest \
  tests/unit/infra/test_binary_artifact_publisher.py \
  -k 'explicit or privacy or cross or linux or macos or publication or cleanup' \
  --run-full-regression
```

実行時にcurrent test discoveryでnearest focused nodeが変わっている場合、正確なcurrent nodeを使用し、置換理由をreportへ記録する。

### Canonical S99 queue

```bash
git status --short
git rev-parse HEAD
git diff --check

make lint
uv run pytest
uv run pytest --run-full-regression

./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github

git diff --check
git status --short
```

actual platform-sensitive inputが変化している場合は、S03で使用した同じreceipt contractにより次も再実行する。

```bash
ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-preflight

ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-supported-publication

ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-insufficient

ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-capability-preflight

ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-clone-publication
```

---

## 8. Reportへ必要な最小field

| Section                           | 必須field                                                                                                                         |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Final Candidate Receipt           | repository、branch、`execution_head`、`review_head`、local/remote一致、pre/post status、wheel basename/version/SHA-256、installed origin |
| Focused Test Evidence             | command、head、test nodes、counts、duration、result、negative sensitivity、evidence ref                                                |
| Fast and Full Regression Evidence | fast/full別command、head、exit、counts、duration、skip理由、required full bodies executed、logs                                           |
| Platform Freshness                | prior evidence refs、affected commit range、changed paths、rerun yes/no、理由、actual host receipts                                    |
| Validation and Sync               | validate result/node count、sync result、unexpected mutation、diff-check、clean status                                              |
| Closure/EAL Audit                 | open/stale/blocked count、各disposition、remaining non-blocking items                                                              |
| Review Freeze                     | normalized fields、sorted path manifest、hash algorithm、`review_content_hash`、computed head/time                                  |
| Reviewer Gate Status / S99        | thread/session ID、Pro receipt、reviewed head/hash、QA/code/spec status、P0〜P3 counts、integrated status                             |
| Repair Ledger                     | finding ID、adoption、root cause、changed paths、tests、new head/hash、re-review result                                               |
| Final Review Transcription        | 許可fieldだけの転記、正規化前後hash一致                                                                                                        |
| Commit and Push Evidence          | final commit SHA、remote SHA、push result、clean status                                                                            |
| PR Handoff Gate                   | PR URL/number/state、base/head、latest SHA、Issue linkage、reuse/new                                                                |
| Merge Preparation Gate            | checks、reviews、conflicts、threads、limitations、blockers、observed_at                                                               |
| Residual Risk / Human Handoff     | non-blocking P2/P3、platform limitations、`merge_performed_by_agent=false`                                                        |
| Parent Epic Trace                 | latest Issue head、S99/PR stateへの参照。raw evidenceの重複なし                                                                            |

S99のclose条件は、上記すべてがlatest applicable headへ束縛され、full regression、required host evidence、3観点review、final push、PR handoff、Merge Preparationが完了し、human merge前で停止していることだけである。現時点ではこのcloseを主張しない。
