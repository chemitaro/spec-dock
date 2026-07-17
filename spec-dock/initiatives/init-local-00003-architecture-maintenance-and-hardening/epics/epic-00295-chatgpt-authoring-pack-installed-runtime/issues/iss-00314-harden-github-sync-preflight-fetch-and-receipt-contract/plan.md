
---

種別: 実装計画書（Issue）
ID: "iss-00314"
タイトル: "Harden GitHub Sync Preflight Fetch And Receipt Contract"
Issue Grade: "strict"
状態: "active"
作成者: "main orchestrator"
最終更新: "2026-07-13"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00295", "init-local-00003"]
-------------------------------------

## iss-00314 GitHub同期preflightのfetch・receipt契約を堅牢化する — Issue実装計画

> このplanはplanned contractの候補である。実装結果、Red/Green/Refactor、worker output、reviewer verdict、commit hashは `report.md` に記録する。この文書自体はimplementation開始許可、reviewer pass、execution-ready、PR-ready、completionを意味しない。

Authorized profileは`standard`である。本Issueはruntime、security/redaction、CLI contract、TOCTOUを扱うため、risk-calibrated manual escalationとしてSpec-Locked Closure Index、step-local delegation contract、concrete test cards、S90、S99、Final Exit Contractを含む強化計画を採用する。Current workflowでは、code/runtime/testsを含むstepはper-step `code-reviewer`、docs-only stepは`spec-reviewer`、S99は`qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`を必要とする。

## 0. Plan readiness

Implementation start前に次を満たすこと。

* [x] candidate `requirement.md` がmain orchestratorにより採否判断されている。
* [x] candidate `design.md` がmain orchestratorにより採否判断されている。
* [x] design `O-001`〜`O-006` がmaintainer判断でresolved。
* [x] `O-007` のconnector/remote terminology dispositionがreport/Epic/follow-upに記録済み。
* [x] `O-008` のPR delivery routeが明示済み。
* [x] canonical requirementにblocking open questionがない。
* [x] canonical designにblocking open itemがない。
* [x] requirement/designそれぞれのfresh `spec-reviewer` verdictが`passed`。
* [x] `standard` profileのauthority sourceが`assurance classify/verify`で確認済み。
* [x] `report.md` にSpec Authoring Gate、Evidence Adoption Ledger、Grade Specialist Evidence Gateが用意されている。
* [x] system-architect / implementation-planner evidenceがIssue-local artifactsとして存在する。
* [x] target branchをGitHub-synced preflightで確認し、planning inputsのsource manifest hashを記録済み。
* [ ] baseline focused testsの既知failureが0、または明示的にrecord済み。
* [ ] plan upfront approvalが得られている。

いずれかが未達ならimplementationへ進まず、`blocked` または `incomplete` をreportに記録する。

## 1. この計画で満たす要件ID

### Functional

`RQ-FUNC-001`〜`RQ-FUNC-017`

### Non-functional

`RQ-NF-001`〜`RQ-NF-009`

### Acceptance criteria

`AC-001`〜`AC-020`

### Edge cases

`EC-001`〜`EC-025`

### Constraints

`CON-001`〜`CON-010`

## 2. MUST / SHOULD / LATER execution boundary

### MUST — このplanのrequired closure

* S01: typed fixed-fetch tracer。
* S02: conservative classification/retry/redaction。
* S03: first-class safe atomic receipt publication。
* S04: post-fetch snapshot/concurrent-change guard。
* S05: versioned receipt integrity、pack binding、legacy compatibility。
* S06: provider/dogfood/install parity。
* S90: docs/skill impact resolution。
* S99: final quality gate。

### SHOULD — 本Issue closureではrequiredにしない

* pack実行時current repo revalidation。
* repo-local ignored output root。
* process-tree cancellation hardening。
* extended multi-version classifier corpus。
* legacy deprecation schedule。

### LATER — 実装禁止

* backend final fetch。
* orchestration command。
* immutable launcher。
* Trace2。
* generic all-writer refactor。
* `openat` / `dir_fd` hardening。
* direct connector integration。
* broad permission changes。

SHOULD/LATERを実装する必要が判明した場合、既存stepへ追加せずplan amendment、scope review、必要ならfollow-up Issueを先に行う。

## 3. 依存関係から導く実装順序

```text
S01 typed execution/result contract
  -> S02 classification/retry/redaction
      -> S03 receipt publication
      -> S04 stable post-fetch snapshot
          -> S05 pack receipt binding/compatibility
              -> S06 provider/dogfood/install parity
                  -> S90 docs/skill alignment
                      -> S99 final quality gate
```

順序の理由:

1. Receipt、retry、writerはtyped process outcomeに依存する。
2. Writerは最終receipt shapeがないと安全に固定できない。
3. Snapshot guardはfetch summaryとreceipt schemaの両方へ出力する。
4. Pack bindingは最終receipt semanticsへ依存する。
5. Projection/install parityはprovider implementationが安定してから閉じる。
6. Docsは実装contract確定後に更新する。
7. S99は全step-local review後にのみ実行する。

## 4. 許可変更面

### Code / runtime

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_fetch_policy.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/authoring_pack/**`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py`

### Tests

* `tests/unit/authoring_pack/**`
* `tests/cli_runtime/test_authoring.py`
* `tests/cli_runtime/test_wrappers.py`
* `tests/unit/infra/test_init_update.py`
* narrowly required fixture/helper files。

### Docs / skill

* provider `spec-dock-chatgpt-authoring/SKILL.md`
* provider `workflow_chatgpt_authoring_pack.md`
* provider `authoring/chatgpt-pack.md` if receipt binding belongs there
* corresponding dogfood projections
* focused docs parity tests

### Generated projection

* `spec-dock/scripts/spec_dock_runtime/**`
* `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
* `spec-dock/docs/**`

Projectionはprovider sourceから生成・同期し、独立implementation sourceとして編集しない。

## 5. 禁止変更

* unrelated authoring commands。
* ZIP review/stage/candidate validatorsの意味論。
* backend invocation final fetch。
* canonical Issue docsのruntime write。
* `.assurance.json` mutation。
* generic report writer全体。
* root permission/sandbox config。
* Git lock deletion。
* `local-context` authority。
* default fallback option。
* source path safety weakening。
* status taxonomyのbreaking change。
* new third-party dependency。
* parent Epic boundary/delivery policyの無記録変更。

## 6. マイルストーン一覧

| Milestone | Steps                   | 成果                                       | Commit candidate             |
| --------- | ----------------------- | ---------------------------------------- | ---------------------------- |
| `M0`      | Plan readiness/baseline | policy decisionsとbaseline                | approved-no-opまたはreport-only |
| `M1`      | S01–S02                 | typed fetch + bounded policy             | C1                           |
| `M2`      | S03                     | safe atomic receipt publication          | C2                           |
| `M3`      | S04                     | stable post-fetch snapshot               | C3                           |
| `M4`      | S05–S06                 | pack binding + projection/install parity | C4                           |
| `M90`     | S90                     | docs/skill contract                      | C5                           |
| `M99`     | S99                     | issue-wide quality and ledger closure    | C6 final ledger commit       |

## 7. ステップ一覧

| Step | Observable behavior                                    | Depends on     | Unblocks   | Primary worker | Reviewer            |
| ---- | ------------------------------------------------------ | -------------- | ---------- | -------------- | ------------------- |
| S01  | CLI receiptがtyped fetch success evidenceを返す            | Plan readiness | S02–S04    | `dev-coder`    | `code-reviewer`     |
| S02  | retryableだけsame-shape retryし、permanent/unknownをblockする | S01            | S03–S05    | `dev-coder`    | `code-reviewer`     |
| S03  | pass/blocked receiptをsafe external dirへatomic保存する      | S01–S02        | S05–S06    | `dev-coder`    | `code-reviewer`     |
| S04  | fetch後のstable snapshotだけをpassにする                       | S01–S02        | S05–S06    | `dev-coder`    | `code-reviewer`     |
| S05  | pack prepareがversioned receiptを検証・bindingする            | S03–S04        | S06        | `dev-coder`    | `code-reviewer`     |
| S06  | provider/dogfood/installが同一behaviorを示す                 | S01–S05        | S90/S99    | `dev-coder`    | `code-reviewer`     |
| S90  | installed docs/skillがoperation contractと一致する           | S01–S06        | S99        | `doc-writer`   | `spec-reviewer`     |
| S99  | full test/review/ledger gateを閉じる                       | all            | Final Exit | reviewers      | three-reviewer gate |

## 8. 要件 ↔ ステップ対応

| Requirement         | Owner step               |
| ------------------- | ------------------------ |
| `RQ-FUNC-001`〜`004` | S01                      |
| `RQ-FUNC-005`〜`007` | S02                      |
| `RQ-FUNC-008`〜`010` | S01, S03                 |
| `RQ-FUNC-011`〜`013` | S04                      |
| `RQ-FUNC-014`〜`015` | S05                      |
| `RQ-FUNC-016`       | S06                      |
| `RQ-FUNC-017`       | S90                      |
| `RQ-NF-001`         | S01–S05, S99             |
| `RQ-NF-002`         | S02, S99                 |
| `RQ-NF-003`         | S02–S03, S90, S99        |
| `RQ-NF-004`         | S02–S03                  |
| `RQ-NF-005`〜`006`   | S01–S06                  |
| `RQ-NF-007`         | all implementation steps |
| `RQ-NF-008`         | S03, S06, S99            |
| `RQ-NF-009`         | S01–S06, S90             |

## 9. Spec-Locked Closure Index

| Closure ID | Spec link                     | Observable input/state                 | Locked expectation                           | Bug class guarded                     | Required | Evidence level       | Owner   |
| ---------- | ----------------------------- | -------------------------------------- | -------------------------------------------- | ------------------------------------- | -------: | -------------------- | ------- |
| `CLOS-001` | `RQ-FUNC-001`, `AC-001`       | safe github-synced request             | fixed mandatory fetch is executed            | stale cached evidence / omitted fetch |      yes | CLI + spy            | S01     |
| `CLOS-002` | `RQ-FUNC-002`, `AC-001`       | all attempts                           | executable/argv/repo/remote/policy unchanged | capability drift                      |      yes | unit                 | S01/S02 |
| `CLOS-003` | `RQ-FUNC-003`, `AC-005`       | hanging child                          | finite timeout and noninteractive policy     | indefinite prompt/hang                |      yes | unit                 | S01/S02 |
| `CLOS-004` | `RQ-FUNC-004`, `AC-002`       | process result                         | typed attempt evidence emitted               | diagnostic flattening                 |      yes | CLI JSON             | S01     |
| `CLOS-005` | `RQ-FUNC-005`〜`006`, `AC-003` | retryable first failure                | bounded internal retry                       | caller-owned arbitrary retry          |      yes | unit + CLI           | S02     |
| `CLOS-006` | `RQ-FUNC-005`〜`007`, `AC-004` | auth/config/unknown/cancel             | no retry/escalation/fallback                 | permission inference                  |      yes | unit                 | S02     |
| `CLOS-007` | `RQ-NF-003`, `AC-007`         | secret/non-UTF8/large diagnostic       | no unsafe raw output                         | credential/path leakage               |      yes | unit + CLI           | S02     |
| `CLOS-008` | `RQ-FUNC-008`, `AC-013`       | JSON/text caller                       | additive schema, old keys preserved          | automation breakage                   |      yes | CLI contract         | S01/S05 |
| `CLOS-009` | `RQ-FUNC-009`, `AC-008`       | safe output dir                        | fixed JSON receipt without shell             | redirect approval regression          |      yes | CLI/filesystem       | S03     |
| `CLOS-010` | `RQ-FUNC-010`, `AC-006`       | blocked result                         | blocked receipt is persisted                 | lost failure evidence                 |      yes | CLI/filesystem       | S03     |
| `CLOS-011` | `RQ-FUNC-010`, `AC-009`       | unsafe/non-owned target                | no target corruption                         | symlink/traversal/overwrite           |      yes | unit + CLI           | S03     |
| `CLOS-012` | `RQ-FUNC-011`, `AC-010`       | remote moves before preflight          | evaluation uses post-fetch state             | mixed-time snapshot                   |      yes | hermetic Git         | S04     |
| `CLOS-013` | `RQ-FUNC-012`, `AC-011`       | repository changes during observation  | `concurrent_repo_change` block               | false synced pass                     |      yes | injected concurrency | S04     |
| `CLOS-014` | `RQ-FUNC-013`, `AC-012`       | fetch fails, cached ref exists         | cache marked unverified                      | offline verified claim                |      yes | unit + CLI           | S04     |
| `CLOS-015` | `RQ-FUNC-014`, `AC-014`〜`015` | v1 receipt                             | kind/digest/semantic validation and binding  | tampered/stale pack input             |      yes | pack CLI             | S05     |
| `CLOS-016` | `RQ-FUNC-015`, `AC-013`       | legacy unversioned receipt             | remains readable without new claims          | version skew breakage                 |      yes | pack CLI             | S05     |
| `CLOS-017` | `AC-016`                      | local-context/fallback/source fixtures | existing semantics unchanged                 | regression outside bug scope          |      yes | regression           | S04/S05 |
| `CLOS-018` | `RQ-FUNC-016`, `AC-017`       | provider/dogfood/install               | observable parity                            | provider-only fix                     |      yes | install integration  | S06     |
| `CLOS-019` | `RQ-FUNC-017`, `AC-018`       | installed docs/skill                   | no shell/escalation/fallback guidance        | agent workflow recurrence             |      yes | docs assertion       | S90     |
| `CLOS-020` | `RQ-NF-009`, `AC-019`         | outputs/docs                           | no authority self-claim                      | evidence promotion                    |      yes | structural scan      | S90/S99 |
| `CLOS-021` | `AC-020`                      | integrated diff                        | full tests/reviews/validate pass             | hidden integration regression         |      yes | full gate            | S99     |

Every required closure must appear in `report.md` Step Contract Closure、Test Contract Closure、Closure Coverageにpassまたは正当なapproved-no-opとして記録する。

## 10. Deferred hardening ledger

| ID        | Priority | Candidate                         | Required for Final Exit |
| --------- | -------- | --------------------------------- | ----------------------: |
| `FUP-001` | SHOULD   | pack時点current repo revalidation   |                      no |
| `FUP-002` | SHOULD   | repo-local ignored evidence root  |                      no |
| `FUP-003` | SHOULD   | process-tree cancellation         |                      no |
| `FUP-004` | LATER    | backend final fetch/orchestration |                      no |
| `FUP-005` | LATER    | immutable launcher                |                      no |
| `FUP-006` | LATER    | Trace2                            |                      no |
| `FUP-007` | LATER    | generic writer / openat hardening |                      no |
| `FUP-008` | LATER    | direct connector observation      |                      no |

Final Exit時、各deferred itemには次をreportへ記録する。

* scope外理由
* current Issueをblockしない理由
* revisit trigger
* follow-up Issue/ADR/Epic disposition、または未起票理由

---

## 11. S01 — Typed fixed-fetch vertical tracer

### Metadata

* depends on: Plan readiness
* unblocks: S02, S03, S04
* target files:

  * `domain/authoring_pack/preflight_contract.py`
  * `infra/authoring_pack/git_fetch.py`（new file）
  * `application/authoring_pack/github_sync_preflight.py`
  * `presentation/authoring_pack/diagnostics.py`
  * `tests/unit/authoring_pack/test_github_fetch_policy.py`（new file）
  * focused portions of `tests/cli_runtime/test_authoring.py`

### Behavior goal

Clean/synced CLI invocationが既存status/refs/source fieldsを維持しながら、versioned receipt metadataと一件のtyped successful fetch attemptを返す。

### Planned contract

* scope:

  * process outcome、attempt data、schema v1 skeleton、fixed fetch executor。
* test obligation:

  * public CLI success、fixed argv/environment、spawn/timeout shape、legacy field preservation。
* red or alternative evidence:

  * `red-required`。まずCLI JSONにnew schema/fetch fieldsがないことを示す。
* minimal green:

  * retry/classification regex、writer、concurrent guardはまだ作らず、一件のsuccess/failure outcomeをtyped resultへ通す。
* green verification:

  * focused unit + clean/synced CLI test。
* refactor guardrail:

  * existing source/fallback/local-context semanticsを変えない。
  * generic subprocess frameworkを作らない。
* amendment trigger:

  * fixed argv変更、new status、new dependency、environment全allowlist、public field削除が必要になった場合。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * canonical requirement/design/plan
  * parent Epic requirement/design
  * current `github_sync_preflight.py`
  * current `preflight_contract.py`
  * current `commands/authoring.py`
  * current `diagnostics.py`
  * current preflight tests
* scope:

  * typed process/outcome tracerをprovider sourceへ実装する。
* source of truth:

  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
* allowed paths:

  * S01 target filesのみ。
* forbidden changes:

  * dogfood mirror先行編集
  * retry policy完成
  * writer実装
  * pack prepare変更
  * docs変更
  * local-context/fallback semantics変更
  * shell use
* acceptance criteria:

  * `CLOS-001`〜`CLOS-004`, `CLOS-008`のS01部分。
* required tests:

  * unit process outcome tests
  * clean/synced CLI JSON/text regression
* reviewer focus:

  * `code-reviewer`: layer ownership、fixed argv、raw diagnostic非serialize、additive compatibility。
* stop conditions:

  * existing contractをbreaking変更する必要がある。
  * current code layoutとdesign module splitが両立しない。
  * raw stderrをpublic resultへ入れる必要がある。
  * target外fileが必要。
* output required:

  * changed files
  * worker summary
  * Red/Green result
  * verification commands
  * unresolved risks
  * `Ledger Note` または `No material implementation decisions beyond the approved plan.`

### 具体テストケース一覧

* `tc-s01-001` acceptance: clean CLIがversioned typed fetch evidenceを返す

  * 前提: local bare originとclean/synced `main` branchを持つtemp repo。
  * 操作: `authoring preflight github-sync --format json` を実行する。
  * 期待結果: exit 0、existing fieldsが維持され、`schema_version=1`、receipt kind、`fetch.status=success`、attempt 1件、return code 0がある。
  * 失敗検出: fixed fetchは成功してもnew receipt evidenceが欠落する、またはexisting fieldsが変わる回帰。
  * 検証方法: `tests/cli_runtime/test_authoring.py` のred-first CLI test。
  * 関連 closure id: `CLOS-001`, `CLOS-004`, `CLOS-008`。

* `tc-s01-002` contract: fetch executable/argv/cwd/environment policyが固定される

  * 前提: spy fetch executor。
  * 操作: application preflightを一度実行する。
  * 期待結果: logical executable `git`、argv `fetch --prune origin`、repo cwd、shellなし、timeout/noninteractive policyがspyで観測される。
  * 失敗検出: command string化、remote/refのcaller依存、cwdずれ、shell wrapper。
  * 検証方法: `tests/unit/authoring_pack/test_github_fetch_policy.py`。
  * 関連 closure id: `CLOS-001`, `CLOS-002`, `CLOS-003`。

* `tc-s01-003` negative: spawn failureがtraceback/raw exceptionではなくtyped blocked evidenceになる

  * 前提: executorが`FileNotFoundError`相当outcomeを返す。
  * 操作: preflightを実行する。
  * 期待結果: nonzero result、`spawn_failure`、return code null、raw tracebackなし。
  * 失敗検出: exceptionがCLIをcrashさせる、またはgeneric stringだけへflattenされる。
  * 検証方法: unit testとfocused CLI fake executor test。
  * 関連 closure id: `CLOS-004`, `CLOS-006`。

### Step closure contract

S01をcloseできる条件:

* `CLOS-001`〜`004` pass。
* `CLOS-008`のadditive success shapeがpass。
* raw process bytesが`to_dict()`へ直接入らない。
* existing focused preflight testsがpass。
* per-step `code-reviewer` fresh passed。
* report更新済み。
* milestone M1はS02後にcommitするため、S01単独は`approved-no-op`ではなくworking step stateとして保持し、S02開始前のResult Approvalを明示する。

### Report evidence destination

* `実装記録（セッションログ）`
* `Implementation Delegation Gate`
* `Delegated Worker Evidence`
* `Step Contract Closure`
* `Test Contract Closure`
* `Closure Coverage`
* `Spec Interpretation / Decision Ledger`

### Step gate

1. worker verification。
2. report draft update。
3. per-step code-reviewer。
4. findingsをsame workerへbounded re-delegation。
5. fresh re-review。
6. S01 Step Result Approval。
7. S02へ進む。

---

## 12. S02 — Conservative classification, bounded retry, redaction

### Metadata

* depends on: S01 Result Approval
* unblocks: S03–S05
* target files:

  * new `application/authoring_pack/github_fetch_policy.py`
  * `infra/authoring_pack/git_fetch.py`（new file）
  * `preflight_contract.py`
  * `github_sync_preflight.py`
  * unit/CLI tests

### Behavior goal

Retryableと高い確度で分類されたfailureだけを同一shapeで最大budgetまでretryし、permanent/unknown/cancelled failureは一回でblockする。全diagnosticはbounded/redacted evidenceになる。

### Planned contract

* scope:

  * classifier、confidence、retry allowlist、policy constants、safe diagnostic。
* test obligation:

  * transient、timeout、throttle、lock、auth/not-found、host identity、config、permission、spawn、cancel、unknown、non-UTF8、secret、oversize。
* red:

  * `red-required`。fake attempt sequenceでcurrent implementationがretry/evidenceを持たないことを示す。
* green:

  * candidate policy constantsに従う最小implementation。
* refactor guardrail:

  * regexをsemantic truthにしない。
  * exit code単独で分類しない。
  * random jitter、Trace2、process group frameworkを追加しない。
* amendment trigger:

  * unknown retry、new retryable class、policy value変更、raw diagnostic保存、CLI retry knobsが必要になった場合。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * S01 result、canonical design sections 9–11、incident taxonomy、existing tests。
* allowed paths:

  * S02 target files。
* forbidden changes:

  * writer、pack prepare、docs、dogfood projection。
  * permission escalation、lock deletion。
* acceptance criteria:

  * `AC-003`〜`AC-007`。
* required tests:

  * pure classifier table tests。
  * retry sequence tests。
  * diagnostic redaction tests。
  * timeout/cancel tests。
* reviewer focus:

  * `code-reviewer`: false retry risk、confidence semantics、secret leakage、same-shape invariant、bounded resources。
* stop conditions:

  * reliable分類にTrace2やnetworkが必須となる。
  * credential helperを無効化しないとtestが通らない。
  * canonical design policy constantsからの変更が必要。
* output required:

  * classification table implementation summary
  * fixture corpus
  * same-shape evidence
  * Red/Green commands
  * unresolved classifier ambiguities
  * Ledger Note。

### 具体テストケース一覧

* `tc-s02-001` acceptance: transient first failure後に同一shapeで成功する

  * 前提: fake executorがtransient signal付きfailure、次にsuccessを返す。
  * 操作: preflightを一度実行する。
  * 期待結果: attempt 2件、最初はretryable/probable、二件目success、最終pass。
  * 失敗検出: caller retry要求、shape変更、budget超過、failureのまま終了。
  * 検証方法: pure policy unit test。
  * 関連 closure id: `CLOS-002`, `CLOS-005`。

* `tc-s02-002` negative: authentication/not-foundはretryしない

  * 前提: C localeのaccess denied/repository not found fixture。
  * 操作: policyを実行する。
  * 期待結果: attempt 1件、non-retryable、blocked remediation。
  * 失敗検出: credential failureをtransient扱いして再試行する回帰。
  * 検証方法: parametrized classifier/retry test。
  * 関連 closure id: `CLOS-006`。

* `tc-s02-003` negative: unknown failureはretryしない

  * 前提: nonzero、emptyまたはunmatched diagnostic。
  * 操作: policyを実行する。
  * 期待結果: class `unknown`、confidence `unknown`、attempt 1件、blocked。
  * 失敗検出:「一度だけなら安全」と推測retryする回帰。
  * 検証方法: unit test。
  * 関連 closure id: `CLOS-006`。

* `tc-s02-004` timeout: budget内だけretryする

  * 前提: fake executorが各attemptでtimeout outcome。
  * 操作: policyを実行する。
  * 期待結果: configured total attemptsで停止、各termination=`timeout`、最終blocked。
  * 失敗検出:無期限hang、budget超過、timeoutをsuccess扱い。
  * 検証方法: fake clock/sleeper unit test。実時間sleepは禁止。
  * 関連 closure id: `CLOS-003`, `CLOS-005`。

* `tc-s02-005` lock: ref lockを削除せず限定retryする

  * 前提: lock contention fixtureとsentinel lock file。
  * 操作: policyを実行する。
  * 期待結果: allowed retry後blockedまたはsuccess、sentinel fileは削除されない。
  * 失敗検出:自動lock cleanup、unbounded loop。
  * 検証方法: unit/filesystem fixture。
  * 関連 closure id: `CLOS-005`, `CLOS-006`。

* `tc-s02-006` security: diagnosticをredact/truncateする

  * 前提: credential URL、token、`/Users/...`、non-UTF-8、上限超過bytes。
  * 操作: safe diagnosticを生成する。
  * 期待結果: unsafe literalが結果に存在せず、redacted excerpt/digest/byte count/truncatedがある。
  * 失敗検出:stdout/JSON/fileへのsecret/path/raw bytes漏洩。
  * 検証方法: unit testとJSON serialization assertion。
  * 関連 closure id: `CLOS-007`。

* `tc-s02-007` cancellation: user cancelをretryしない

  * 前提: cancellation outcome。
  * 操作: policyを実行する。
  * 期待結果: attempt 1件、cancelled、nonzero、success receiptなし。
  * 失敗検出:cancelled operationのretryまたはpass。
  * 検証方法: unit test。
  * 関連 closure id: `CLOS-006`。

### Step closure contract

* `CLOS-002`, `CLOS-003`, `CLOS-005`, `CLOS-006`, `CLOS-007` pass。
* candidate policy constantsがsingle sourceにある。
* full environment/raw diagnosticsがresultにない。
* policy unit testsが実時間/networkなしでpass。
* per-step code-reviewer passed。
* S01+S02 diffをM1 commit candidateとして閉じる。

### Commit candidate C1

```text
refactor(authoring): model bounded GitHub preflight fetch outcomes
```

Commit前:

* report evidence記録。
* S01/S02 reviewer passed。
* focused tests pass。
* `git diff --check`。
* commit後clean check。

### Amendment trigger

* policy constants変更。
* class追加/削除。
* retry allowlist変更。
* jitter導入。
* host-specific helper suppression。
* raw stderr/digest policy変更。

---

## 13. S03 — First-class safe atomic receipt publication

### Metadata

* depends on: M1 committed
* unblocks: S05/S06
* target files:

  * `preflight_receipt_writer.py`
  * `commands/authoring.py`
  * `github_sync_preflight.py`
  * `diagnostics.py`
  * contract/tests

### Behavior goal

Callerがsafe external directoryを指定すると、shell redirectなしでpass/blocked/stale JSON receiptをfixed filenameへatomic publishできる。

### Planned contract

* scope:

  * optional `--output-dir`、path validation、ownership、atomic publication、publication evidence。
* test obligation:

  * pass、blocked、text format、unsafe path、repo-inside、symlink、non-owned、replace failure、old file preservation。
* red:

  * CLI helpにflagがなく、receiptが作られないtest。
* green:

  * existing outside-repo directoryのみを許可するreceipt-specific writer。
* refactor guardrail:

  * generic report writerへ拡張しない。
  * missing directoryのrecursive creationをfirst PRへ追加しない。
  * canonical/repo-local pathを許可しない。
* amendment trigger:

  * repo-local root、`--report-path`、automatic directory creation、generic writerが必要になった場合。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * design output API/writer sections、existing path safety patterns、CLI contract、S01/S02 result。
* allowed paths:

  * S03 target filesとfocused tests。
* forbidden changes:

  * pack prepare、snapshot ordering、docs。
  * canonical target allowlist。
  * broad filesystem abstraction。
* acceptance criteria:

  * `AC-006`, `AC-008`, `AC-009`。
* required tests:

  * writer unit matrix。
  * CLI pass/blocked publication。
  * atomic failure injection。
* reviewer focus:

  * `code-reviewer`: TOCTOU limits、symlink/ownership、old file preservation、file mode、publication status semantics。
* stop conditions:

  * external-only directory requirementがmaintainer未承認。
  * platformでatomic replaceの意味論が成立しない。
  * user-authored existing fileを上書きする必要がある。
* output required:

  * changed files
  * path policy summary
  * platform limitations
  * verification
  * Ledger Note。

### 具体テストケース一覧

* `tc-s03-001` acceptance: pass receiptをshellなしで保存する

  * 前提: clean/synced repoとexisting external temp directory。
  * 操作: CLIを`--output-dir`付きでdirect argv実行する。
  * 期待結果: stdoutはpass、fixed JSON fileが存在し、digest/ownership/kindがvalid。
  * 失敗検出:redirectが必要、file欠落、stdoutとfileのsemantic mismatch。
  * 検証方法: CLI integration test。
  * 関連 closure id: `CLOS-009`。

* `tc-s03-002` failure evidence: blocked fetch receiptを保存する

  * 前提: fake non-retryable fetch failureとsafe directory。
  * 操作: CLIを実行する。
  * 期待結果: exit 1、blocked stdout、blocked receipt fileが存在する。
  * 失敗検出:nonzero時にfileが失われる回帰。
  * 検証方法: CLI integration。
  * 関連 closure id: `CLOS-010`。

* `tc-s03-003` compatibility: text stdoutでもfileはJSON

  * 前提: default `--format text`。
  * 操作: `--output-dir`付きで実行する。
  * 期待結果: human text stdoutとmachine JSON fileの両方が得られる。
  * 失敗検出:output formatがfile encodingを変える。
  * 検証方法: CLI test。
  * 関連 closure id: `CLOS-008`, `CLOS-009`。

* `tc-s03-004` security: unsafe targetを変更しない

  * 前提: repo内、canonical root、leaf/ancestor symlink、broken symlink、non-directoryをparametrize。
  * 操作: publicationを要求する。
  * 期待結果: blocked/rejected publication evidence、target/link先に変化なし、fetch開始前blockが許容される。
  * 失敗検出:path traversal、canonical write、symlink following。
  * 検証方法: writer unit + CLI matrix。
  * 関連 closure id: `CLOS-011`。

* `tc-s03-005` ownership: non-owned existing fileを上書きしない

  * 前提: fixed targetにuser textまたはmalformed JSONが存在する。
  * 操作: preflightを実行する。
  * 期待結果:`non_owned_existing_receipt_target`、existing bytes unchanged。
  * 失敗検出:fixed filenameを理由にuser fileをreplaceする。
  * 検証方法: unit/CLI。
  * 関連 closure id: `CLOS-011`。

* `tc-s03-006` atomicity: replace前failureで旧receiptを保持する

  * 前提: valid owned old receiptとfault-injected fsync/replace。
  * 操作: new receipt publicationを行う。
  * 期待結果: command blocked、old receiptはvalid/unchanged、temporary fileはbest-effort cleanup。
  * 失敗検出:partial JSON、old file loss。
  * 検証方法: fake writer syscall adapterまたはmonkeypatch unit test。
  * 関連 closure id: `CLOS-011`。

* `tc-s03-007` publication separation: sync成功・write失敗

  * 前提: clean/synced snapshot、writer failure。
  * 操作: preflightを実行する。
  * 期待結果: top-level status blocked、sync evidenceは観測値を保ち、publication failed、pack利用不可。
  * 失敗検出:write失敗でもexit 0、またはsync failureと誤記。
  * 検証方法: application/CLI test。
  * 関連 closure id: `CLOS-010`, `CLOS-011`。

### Step closure contract

* `CLOS-009`〜`011` pass。
* pass/blocked fileが有効JSON。
* unsafe targetはunchanged。
* previous valid receiptはfailure時に保持。
* per-step code-reviewer passed。
* M2 commit candidate作成後clean。

### Commit candidate C2

```text
feat(authoring): publish GitHub preflight receipts atomically
```

### Amendment trigger

* arbitrary filename support。
* repo-local output。
* target directory自動作成。
* generic writerへの拡張。
* path policyのrelaxation。
* Windowsでdifferent semanticsが必要。

---

## 14. S04 — Post-fetch snapshot and concurrent-change guard

### Metadata

* depends on: M1 committed
* unblocks: S05/S06
* target files:

  * `github_sync_preflight.py`
  * snapshot-related contract/helper
  * source manifest integration
  * focused tests

### Behavior goal

Github-synced pass/stale/block判定は、fetch後に取得したstable repository/source snapshotだけを使用し、観測中の変更をpassにしない。

### Planned contract

* scope:

  * observation order、snapshot ID、guard、cached ref disposition。
* test obligation:

  * remote advance、source edit、branch/HEAD change、remote ref change、fetch failure with cache、local-context unchanged。
* red:

  * current mixed-order behaviorをcharacterizationし、injected concurrent mutationでfalse-stableになるtestを先に置く。
* green:

  * post-fetch hashingとpre/post guard。
* refactor guardrail:

  * repository lockを導入しない。
  * full raw status/pathをreceiptへ保存しない。
  * output directoryをsnapshot対象に含めない。
* amendment trigger:

  * global lock、source file inode-level algorithm、pack revalidation、connector observationが必要。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * design transaction/snapshot sections、source_manifest.py、current preflight tests。
* allowed paths:

  * S04 target files/tests。
* forbidden changes:

  * writer、pack prepare、docs。
  * source path safety weakening。
  * local-context authority変更。
* acceptance criteria:

  * `AC-010`〜`AC-012`, `AC-016`。
* required tests:

  * local bare remote integration。
  * injected concurrent-change tests。
  * legacy source/fallback regression。
* reviewer focus:

  * `code-reviewer`: observation ordering、guard completeness、false positive/negative、cached ref semantics、performance bound。
* stop conditions:

  * atomic repository snapshotを保証するためglobal lockが必要。
  * source manifest APIのbreaking change。
  * current testsとparent Epic contractに未解決矛盾。
* output required:

  * sequence change summary
  * snapshot fields
  * concurrency fixture
  * verification
  * Ledger Note。

### 具体テストケース一覧

* `tc-s04-001` acceptance: remote advanceをfetch後にstale判定する

  * 前提: local clone後、別cloneがremote branchへcommit/push。
  * 操作: preflightを実行する。
  * 期待結果: fetchがremote-tracking refを更新し、`behind_remote`、local/remote head mismatch、nonzero。
  * 失敗検出:cached refでpassする回帰。
  * 検証方法: existing hermetic Git testを維持・強化。
  * 関連 closure id: `CLOS-012`。

* `tc-s04-002` concurrency: source hashing中のeditをblockする

  * 前提: snapshot observer hookがmanifest hash途中でsource fileを変更する。
  * 操作: application preflightを実行する。
  * 期待結果:`concurrent_repo_change`、status blocked、pass receiptなし。
  * 失敗検出:mixed old/new source hashをstableとして公開する。
  * 検証方法: injected observer unit/integration。
  * 関連 closure id: `CLOS-013`。

* `tc-s04-003` concurrency: HEAD/branch changeをblockする

  * 前提: fetch後snapshotとfinal guardの間にcheckoutまたはcommitを行うhook。
  * 操作: preflightを実行する。
  * 期待結果:guard IDs mismatch、blocked。
  * 失敗検出:別HEADのlocal/remote/source valuesが一receiptに混在。
  * 検証方法: temp Git repo integration。
  * 関連 closure id: `CLOS-013`。

* `tc-s04-004` failure: cached remote refはunverified

  * 前提:origin ref cacheあり、fetch executorはfailure。
  * 操作: preflightを実行する。
  * 期待結果:`github_sync=failed`、remote disposition=`unverified_cache`、status non-pass。
  * 失敗検出:cached SHA一致を理由にverifiedとする。
  * 検証方法: unit/CLI。
  * 関連 closure id: `CLOS-014`。

* `tc-s04-005` regression: local-contextはfetchしない

  * 前提:valid local-context requestとspy fetch executor。
  * 操作: preflightを実行する。
  * 期待結果:fetch call 0、`github_sync=not_verified`、`sync_state=local_context`。
  * 失敗検出:github-synced transactionをlocal-contextへ誤適用。
  * 検証方法: existing local-context tests + spy。
  * 関連 closure id: `CLOS-017`。

* `tc-s04-006` regression: source symlink/fallback semantics

  * 前提:既存unsafe source、missing ref、explicit fallback fixtures。
  * 操作:new runtime testsを実行する。
  * 期待結果:existing blocker/status/requested/effective semanticsが維持される。
  * 失敗検出:TOCTOU refactorによる既存safety regression。
  * 検証方法:`tests/cli_runtime/test_authoring.py` focused regression。
  * 関連 closure id: `CLOS-017`。

### Step closure contract

* `CLOS-012`〜`014`, `CLOS-017`のS04部分pass。
* source manifestはgithub-syncedでfetch後に生成。
* final guard unstable時は必ずnon-pass。
* local-context/fallback/source safety regressionなし。
* per-step code-reviewer passed。
* M3 commit後clean。

### Commit candidate C3

```text
fix(authoring): verify stable post-fetch preflight snapshots
```

### Amendment trigger

* global repository lock。
* inode-level stable file reader。
* direct connector observation。
* pack/current state revalidation。
* receipt output inside repo。

---

## 15. S05 — Receipt integrity binding and legacy compatibility

### Metadata

* depends on: S03 + S04 committed
* unblocks: S06/S90
* target files:

  * `pack_prepare.py`
  * relevant prompt/provenance contract
  * preflight contract/serialization helpers
  * focused tests

### Behavior goal

`pack prepare` がversioned pass receiptのkind/schema/digest/fetch/freshness semanticsを検証し、receipt digestとsnapshot IDをprompt packへbindingする。legacy receiptはexisting behaviorで読み取れる。

### Planned contract

* scope:

  * v1 validation、digest verification、pass invariant、provenance/stale-if fields、legacy path。
* test obligation:

  * valid v1、tamper、inconsistent pass、legacy、extra fields、no current revalidation claim。
* red:

  * current pack prepareがnew receipt digestを検証しないtest。
* green:

  * schema-aware parserとbinding。
* refactor guardrail:

  * current repository再観測を追加しない。
  * backend invocation変更なし。
  * legacy receiptを無条件拒否しない。
* amendment trigger:

  * repo-root CLI追加、current HEAD/source revalidation、legacy rejection、new prompt pack required fileが必要。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * design receipt/pack boundary、current pack_prepare.py、provenance contract、pack tests。
* allowed paths:

  * S05 target files/tests。
* forbidden changes:

  * backend invoke。
  * ZIP review schema。
  * current repo revalidation。
  * docs（S90）。
* acceptance criteria:

  * `AC-013`〜`AC-016`。
* required tests:

  * pack prepare v1/legacy/tamper/inconsistent matrix。
  * additive JSON compatibility。
* reviewer focus:

  * `code-reviewer`: digest canonicalization、pass invariant、legacy downgrade、authority boundary、false freshness claim。
* stop conditions:

  * current repo revalidationなしではproduct requirementを満たせないと判明。
  * prompt pack breaking schemaが必要。
  * legacy supportがsecurity issueになる。
* output required:

  * v1/legacy compatibility matrix
  * provenance field list
  * test results
  * Ledger Note。

### 具体テストケース一覧

* `tc-s05-001` acceptance: valid v1 receiptをpackへbindingする

  * 前提:valid pass receipt、correct digest、stable snapshot。
  * 操作:`authoring pack prepare --preflight <receipt>`を実行する。
  * 期待結果:pack pass、provenanceにreceipt schema/kind/digest/snapshot/observed_at。
  * 失敗検出:receiptを検証せずsource fieldsだけ転記する。
  * 検証方法:CLI pack prepare test。
  * 関連 closure id:`CLOS-015`。

* `tc-s05-002` security/integrity: tampered receiptをblockする

  * 前提:receipt内容をdigest計算後に変更する。
  * 操作:pack prepareを実行する。
  * 期待結果:digest mismatch、nonzero、prompt pack pass outputなし。
  * 失敗検出:tampered preflight evidenceの採用。
  * 検証方法:CLI negative test。
  * 関連 closure id:`CLOS-015`。

* `tc-s05-003` semantic: `status=pass`とfailed fetchの矛盾をblockする

  * 前提:valid digestだが`status=pass`, `fetch.status=failed`。
  * 操作:pack prepareを実行する。
  * 期待結果:semantic inconsistency finding。
  * 失敗検出:syntactically valid forged pass receipt。
  * 検証方法:parametrized semantic test。
  * 関連 closure id:`CLOS-015`。

* `tc-s05-004` compatibility: legacy unversioned receiptを読む

  * 前提:existing required fieldsを持つlegacy receipt。
  * 操作:pack prepareを実行する。
  * 期待結果:existing behaviorでpass可能、provenanceはlegacy markerを持ち、new digest/snapshotを捏造しない。
  * 失敗検出:version rolloutでexisting automationを壊す、またはlegacyをnew freshnessとして表現する。
  * 検証方法:existing fixtureのlegacy test。
  * 関連 closure id:`CLOS-016`。

* `tc-s05-005` boundary: current repo freshnessを過大claimしない

  * 前提:v1 receipt作成後、repoが変化しているがfirst-PR pack policyは再観測しない。
  * 操作:pack prepareする。
  * 期待結果:provenanceはreceipt observation時点を示し、`current_repository_revalidated=false`相当の明示fieldまたはdocs contractを持つ。
  * 失敗検出:pack時点までfreshと誤認させる。
  * 検証方法:contract test/inspection。
  * 関連 closure id:`CLOS-015`。

* `tc-s05-006` compatibility: unknown additive v1 fieldsを許容する

  * 前提:valid v1 receiptにunknown additive field。
  * 操作:pack prepareする。
  * 期待結果:known invariantを満たせばpass。breaking意味変更は許容しない。
  * 失敗検出:additive evolutionを拒否する。
  * 検証方法:unit/CLI。
  * 関連 closure id:`CLOS-008`, `CLOS-015`。

### Step closure contract

* `CLOS-015`, `CLOS-016` pass。
* v1 tamper/inconsistencyはfail-closed。
* legacy current automation維持。
* pack outputはcurrent repo freshnessをclaimしない。
* per-step code-reviewer passed。
* S06後にM4 commit。

### Amendment trigger

* current repo revalidation。
* backend changes。
* legacy rejection。
* new required metadata file。
* schema version increment。

---

## 16. S06 — Provider/dogfood/install parity

### Metadata

* depends on: S01–S05 passed
* unblocks: S90/S99
* target files:

  * generated dogfood runtime projection
  * packaging/init/update tests
  * CLI parity tests
  * focused wrapper/tests if applicable

### Behavior goal

Authoritative provider implementationがdogfood projectionとfresh init/update consumerに完全に届き、help、pass、blocked、receipt publication、pack bindingが同じobservable behaviorを示す。

### Planned contract

* scope:

  * provider projection、package inclusion、init/update、consumer execution。
* test obligation:

  * provider/dogfood behavior、fresh init、update、module packaging、help、pass/blocked、no pycache dirty。
* red:

  * provider-only new moduleがinstalled packageに欠落するtest。
* green:

  * existing asset projection mechanismに従う。
* refactor guardrail:

  * dogfoodをsource of truthにしない。
  * installer architectureを再設計しない。
* amendment trigger:

  * package-data config、installer registry、migration contractの広い変更が必要。

### Delegation contract

* delegated role:

  * `dev-coder`
* input docs:

  * design projection section、pyproject package-data、existing init/update tests、Issue 307 installed simulation evidence。
* allowed paths:

  * provider/dogfood projection、focused packaging/install tests。
* forbidden changes:

  * unrelated installer behavior。
  * old workspace migration。
  * docs本文（S90）。
* acceptance criteria:

  * `AC-017`, `AC-020`のparity部分。
* required tests:

  * provider/dogfood import/behavior parity。
  * fresh init and update simulation。
  * package inclusion。
  * no bytecode dirtiness。
* reviewer focus:

  * `code-reviewer`: provider authority、missing hidden/module assets、projection drift、installed behavior。
* stop conditions:

  * installer-wide migrationが必要。
  * package data inclusionをbreaking変更する必要。
  * dogfood mirror生成方法が不明。
* output required:

  * parity matrix
  * install commands/results
  * changed projection files
  * Ledger Note。

### 具体テストケース一覧

* `tc-s06-001` acceptance: fresh installed runtimeがnew help/receipt contractを持つ

  * 前提:temp install targetとlocal source package。
  * 操作:`spec-dock init`後、installed `authoring preflight github-sync --help` とhermetic repo executionを行う。
  * 期待結果:`--output-dir`がhelpにあり、pass/blocked receipt behaviorがproviderと一致。
  * 失敗検出:new infra module/package asset欠落、provider-only success。
  * 検証方法:init simulation test。
  * 関連 closure id:`CLOS-018`。

* `tc-s06-002` compatibility: update targetへ新contractが届く

  * 前提:old installed fixture。
  * 操作:existing update mechanismを実行する。
  * 期待結果:managed runtime/docs/skillが更新され、user-authored filesを破壊せずnew helpを示す。
  * 失敗検出:initだけ成功しupdateがstale。
  * 検証方法:`tests/unit/infra/test_init_update.py`。
  * 関連 closure id:`CLOS-018`。

* `tc-s06-003` parity: providerとdogfoodが同一resultを返す

  * 前提:同じhermetic Git fixture。
  * 操作:provider runtime pathとdogfood runtime pathを実行する。
  * 期待結果:selected stable fields/status/blockers/receipt semanticsが一致。
  * 失敗検出:projection drift。
  * 検証方法:parameterized CLI parity test。
  * 関連 closure id:`CLOS-018`。

* `tc-s06-004` regression: runtime bytecodeでconsumer repoをdirtyにしない

  * 前提:PYTHONDONTWRITEBYTECODEを明示しないinstalled execution。
  * 操作:preflightを実行する。
  * 期待結果:untracked pycache/pycなし、status clean。
  * 失敗検出:new modulesがbytecode side effectを作る。
  * 検証方法:existing regression test拡張。
  * 関連 closure id:`CLOS-017`, `CLOS-018`。

* `tc-s06-005` packaging: new infra modulesがwheel/installへ含まれる

  * 前提:local source build。
  * 操作:isolated installしmodule import/CLIを実行する。
  * 期待結果:ImportErrorなし。
  * 失敗検出:asset package-data omission。
  * 検証方法:isolated local source install test。
  * 関連 closure id:`CLOS-018`。

### Step closure contract

* `CLOS-018` pass。
* provider/dogfood/fresh init/update matrix complete。
* package inclusion verified。
* no pycache/untracked regression。
* per-step code-reviewer passed。
* S05+S06をM4 commit。

### Commit candidate C4

```text
test(authoring): verify preflight receipt install parity
```

実装codeがS05に多く残る場合は、C4を次の二commitへ分けてもよい。

```text
feat(authoring): bind versioned preflight receipts to prompt packs
test(authoring): verify provider and installed preflight parity
```

分割時も各commit前のreport/review/clean gateを守る。

### Amendment trigger

* installer-wide changes。
* new package registry entry。
* migration。
* hidden asset packaging change。
* unrelated wrapper changes。

---

## 17. S90 — Docs impact resolution / docs refresh

### Metadata

* depends on: S01–S06 stable
* unblocks: S99
* primary worker: `doc-writer`
* reviewer: `spec-reviewer`

### Behavior goal

Installed skill/docsが実装済みCLI、fetch/retry、receipt、failure、freshness、authority boundaryを正確に説明し、agentが再びshell/permission escalationへ進まない。

### Required docs decision

Docs impactは`none`ではない。最低限、installed skillとChatGPT authoring workflowを更新する。

### Planned contract

* scope:

  * direct argv、no shell、no escalation、SpecDock-owned retry、output-dir、receipt semantics、pack boundary、operator remediation。
* evidence:

  * docs assertions、provider/dogfood parity、help comparison。
* docs-only verification:

  * structural grep/assertions、Markdown inspection、spec alignment review。
* refactor guardrail:

  * generic issue workflowを重複説明で肥大化させない。
  * LATER featuresをimplementedと書かない。
* amendment trigger:

  * public CLI/receipt fieldがdesignから変わる。
  * new reference docが必要。
  * docs scopeが複数workflowへ拡大する。

### Delegation contract

* delegated role:

  * `doc-writer`
* input docs:

  * approved requirement/design/plan
  * final implemented CLI help/schema
  * current installed skill
  * current workflow docs
  * S01–S06 worker summaries
* allowed paths:

  * provider skill/docsと対応dogfood projection
  * focused docs tests
* forbidden changes:

  * runtime code/tests except docs structural assertions
  * unrelated planning skills
  * canonical Issue report以外のIssue docs
  * future featuresをsupportedと記述
* acceptance criteria:

  * `AC-018`, `AC-019`。
* required docs-only verification:

  * direct argv/no-shell/no-escalation assertions
  * option/filename/freshness wording
  * provider/dogfood/install docs parity
* reviewer focus:

  * `spec-reviewer`: requirement/design/CLIとの一致、authority boundary、MUST/LATER区別、日本語ファースト。
* stop conditions:

  * implementation contractが未安定。
  * CLI helpとdesignが不一致。
  * direct connector/final fetch等の未実装機能を書かざるを得ない。
* output required:

  * changed docs
  * docs impact matrix
  * verification result
  * unresolved wording
  * Ledger Note。

### 必須文言

Skillには少なくとも次を含める。

```text
Run the SpecDock entrypoint as direct argv.
Do not add shell wrappers, redirects, pipes, tee, heredocs,
command substitution, or inline environment assignment.

A nonzero fetch result is not evidence that additional permissions are required.
Never add require_escalated or change sandbox/permission mode in response to a fetch result.

Use --output-dir to persist the preflight receipt.
Retry is owned by SpecDock and preserves the same execution shape.
Do not replace preflight with agent-owned raw git fetch.
Do not silently switch to local-context or default branch.
```

日本語primary proseとし、必要な英語contract文を併記してよい。

### 具体テストケース一覧

* `tc-s90-001` docs acceptance: no-shell/no-escalation guidance

  * 前提:installed provider skill text。
  * 操作:structural docs testを実行する。
  * 期待結果:direct argv、forbidden shell forms、fetch nonzero≠permission evidence、no escalationが存在。
  * 失敗検出:原インシデントと同じagent復旧を許容する曖昧なguidance。
  * 検証方法:`tests/cli_runtime/test_wrappers.py`またはfocused docs assertion。
  * 関連 closure id:`CLOS-019`。

* `tc-s90-002` contract: output/freshness wording

  * 前提:updated workflow docs。
  * 操作:docs inspection。
  * 期待結果:`--output-dir`、fixed receipt、blocked persistence、preflight observation時点、pack current revalidation非保証が記載。
  * 失敗検出:receiptをbackend直前までfreshと過大表現。
  * 検証方法:structural assertion + spec-review。
  * 関連 closure id:`CLOS-019`。

* `tc-s90-003` authority: forbidden claimsなし

  * 前提:updated skill/docs。
  * 操作:forbidden authority claim scan。
  * 期待結果:canonical adoption、reviewer pass、execution-ready、PR-ready等を達成claimとして含まない。
  * 失敗検出:evidence laneからauthority planeへの越権。
  * 検証方法:existing forbidden-claim assertion pattern。
  * 関連 closure id:`CLOS-020`。

* `tc-s90-004` parity: provider/dogfood/installed docs一致

  * 前提:provider sourceからprojection/install済み。
  * 操作:selected docs/skill contentまたはnormalized digestを比較。
  * 期待結果:三surfaceのoperational contract一致。
  * 失敗検出:provider docsのみ更新。
  * 検証方法:init/update parity test。
  * 関連 closure id:`CLOS-018`, `CLOS-019`。

### Step closure contract

* `CLOS-019`, `CLOS-020` pass。
* docs impact `none`ではなく、更新済み。
* doc-writer outputをparentがinspect/integrate。
* fresh spec-reviewer docs/spec alignment passed。
* M90 commit後clean。

### Commit candidate C5

```text
docs(authoring): define reliable preflight fetch and receipt usage
```

---

## 18. S99 — Final quality gate

S99は独立gateであり、per-step reviewを代替しない。

### Preconditions

* S01–S06、S90がStep Result Approval済み。
* 全milestoneがcommittedまたはvalid approved-no-op。
* unresolved blocking decision/EAL entryなし。non-blocking `deferred` / `partially_adopted` entryは、理由・revisit trigger・next actionが記録されていれば許容する。
* required closure rowのplan amendment漏れなし。
* docs/skill parity完了。
* delivery route決定済み。

### Verification commands候補

Repository conventionsとCIで最終確認し、実際のcommand差異はreportへ記録する。

```text
git diff --check

uv run pytest -q tests/unit/authoring_pack/test_github_fetch_policy.py
uv run pytest -q tests/unit/authoring_pack/test_preflight_receipt_writer.py

uv run pytest -q tests/cli_runtime/test_authoring.py -k "preflight or pack_prepare"
uv run pytest -q tests/cli_runtime/test_wrappers.py
uv run pytest -q tests/unit/infra/test_init_update.py

uv run ruff check src tests
uv run mypy src tests

./spec-dock/scripts/spec-dock validate
```

Installed simulation候補:

```text
uv build --wheel
uvx --isolated --from <ABSOLUTE_REPOSITORY_ROOT> spec-dock init <TEMP_INSTALL_TARGET>
<TEMP_INSTALL_TARGET>/spec-dock/scripts/spec-dock authoring preflight github-sync --help
```

Actual pass/blocked installed behaviorはlocal bare originを使うhermetic testで確認する。

Manual direct-argv evidence:

```text
./spec-dock/scripts/spec-dock
  authoring
  preflight
  github-sync
  --repo-root
  <REPOSITORY_ROOT>
  --ref
  <CURRENT_BRANCH>
  --source-path
  <EXPLICIT_SOURCE_PATH>
  --format
  json
  --output-dir
  <EXISTING_EXTERNAL_TEMP_DIRECTORY>
```

このmanual evidenceにredirect、pipe、`tee`、shell wrapperを付けない。

### S99 reviewer contracts

#### QA reviewer

* focus:

  * AC/EC/closure coverage。
  * retry/classifier/path/concurrency/install negative paths。
  * test sensitivityとhermeticity。
  * missing integration tests。
* fail conditions:

  * raw test countだけで十分性を主張。
  * unsafe path、secret、unknown failure、concurrency、install parityの欠落。
  * real network依存。
* required output:

  * pass/fail
  * missing tests
  * risk assessment
  * evidence references

#### Issue-wide code reviewer

* focus:

  * layer responsibility。
  * module splitの過不足。
  * fixed execution shape。
  * classifier false-positive retry。
  * writer safety。
  * snapshot ordering。
  * additive compatibility。
  * no generic scope creep。
* fail conditions:

  * applicationにsubprocess/path I/Oが再集中。
  * raw diagnostic leak。
  * status/field breaking change。
  * dogfood-only implementation。
  * LATER scope混入。
* required output:

  * pass/fail
  * blocking/non-blocking findings
  * affected closures

#### Final spec reviewer

* focus:

  * requirement/design/plan/report/implementation/tests/docsの一致。
    -全MUST closure。
  * SHOULD/LATER非混入。
  * unresolved decisions。
  * authority boundary。
  * parent Epic trace。
* fail conditions:

  * numeric policyが未承認。
  * connector-visible claimの誤表現。
  * backend freshnessの過大claim。
  * no-shell/no-escalation docs不足。
  * report closure不足。
* required output:

  * fresh pass/fail
  * target revision/hash
  * requirement coverage findings

いずれかがfailなら、findingを適切な`dev-coder`または`doc-writer`へbounded再委任し、focused verification後に該当reviewerをfresh再実行する。

### 具体テストケース一覧

* `tc-s99-001` integration:全MUST closure evidenceが存在する

  * 前提:final report draft。
  * 操作:Closure IndexとStep/Test Closureを照合する。
  * 期待結果:全required rowにowner step、verification、pass evidence。
  * 失敗検出:実装済みだがspec closure不明な状態。
  * 検証方法:manual/spec-review inspection。
  * 関連 closure id:`CLOS-021`。

* `tc-s99-002` full regression: focused/full checksがpassする

  * 前提:integrated diff。
  * 操作:上記command matrixを実行する。
  * 期待結果:required commands pass、known unrelated failureなし。
  * 失敗検出:unit passのみでinstall/docs/full regressionを見逃す。
  * 検証方法:command evidence。
  * 関連 closure id:`CLOS-021`。

* `tc-s99-003` security: secret/host-path/authority scan

  * 前提:final JSON/text/docs/tests。
  * 操作:representative secret fixturesとforbidden claim scan。
  * 期待結果:unsafe literalなし、authority boundary維持。
  * 失敗検出:durable evidence leak/overclaim。
  * 検証方法:automated assertions + reviewer inspection。
  * 関連 closure id:`CLOS-007`, `CLOS-020`, `CLOS-021`。

* `tc-s99-004` delivery readiness boundary

  * 前提:全local gates pass。
  * 操作:parent/delivery policyを確認する。
  * 期待結果:normal PR Delivery Gateまたは明示deferred gateのどちらか一方が選ばれ、merge-readyをprematureにclaimしない。
  * 失敗検出:old final Issueへのsilent defer、またはlocal testsだけでPR-ready claim。
  * 検証方法:report/parent plan inspection。
  * 関連 closure id:`CLOS-021`。

### S99 closure contract

* `CLOS-001`〜`CLOS-021`の全required rowがpass。
* qa-reviewer fresh passed。
* issue-wide code-reviewer fresh passed。
* final spec-reviewer fresh passed。
* reportのdecision/EAL/closure/reviewer/commit ledgers更新済み。
* no unresolved blocker/stale entry。
* final implementation diffは既にmilestone commitsで閉じている。
* final commitはreport/final evidence boundaryだけを閉じる。
* final commit後clean evidenceはexternal delivery evidenceへ記録する。

### Commit candidate C6

```text
chore(issue-00314): record final preflight hardening evidence
```

C6へ未commitのruntime/tests/docs差分を混ぜない。

## 19. Commit / reviewer mapping

| Commit | Scope                                    | Required reviewer before commit  |
| ------ | ---------------------------------------- | -------------------------------- |
| C1     | typed fetch + classifier/retry/redaction | per-step `code-reviewer` S01/S02 |
| C2     | output-dir + safe atomic writer          | per-step `code-reviewer` S03     |
| C3     | post-fetch snapshot/concurrent guard     | per-step `code-reviewer` S04     |
| C4     | pack binding + provider/install parity   | per-step `code-reviewer` S05/S06 |
| C5     | skill/docs                               | `spec-reviewer` S90              |
| C6     | final report/evidence ledger             | S99 three-reviewer passes        |

各commit前:

1. step report update。
2. reviewer passed。
3. relevant focused tests pass。
4. no next-step diff。
5. `git diff --check`。
6. commit。
7. `git status --short` clean確認。

## 20. Report evidence destinations

各stepは少なくとも次を更新する。

* `Spec Interpretation / Decision Ledger`
* `Evidence Adoption Ledger`
* `Objective Alignment Ledger`
* `Workflow-Scoped Authorization`
* `Implementation Delegation Gate`
* `Delegated Worker Evidence`
* `TDD / Red / Green / Refactor Evidence`
* `Step Contract Closure`
* `Test Contract Closure`
* `Closure Coverage`
* `Closure Delta`
* `Reviewer Gate Status`
* `Commit Evidence`
* `Docs Impact`
* `Final Quality Gate`

ChatGPT research採用時は、claim単位のadopted/partially_adopted/rejected/deferredを記録し、research artifact全体をauthorityとして扱わない。

## 21. Amendment triggers

次のいずれかを発見したら、report記録だけで進めずplan amendmentとre-reviewを行う。

* required closureの追加・削除・意味変更。
* fixed fetch argv/remote変更。
* retry class/budget/timeout/backoff変更。
* unknown failureのretry。
* public status/exit/keyのbreaking change。
* `--report-path`追加。
* repo-local output許可。
* canonical target write。
* raw diagnostic/digest policy変更。
* new dependency。
* direct connector/Trace2/launcher追加。
* pack current state revalidation追加。
* backend final fetch。
* all-writer refactor。
* source-path safety変更。
* local-context/default fallback authority変更。
* parent Epic/delivery route変更。
* Critical escalation condition。

## 22. Final Exit Contract

Issue local implementationを完了候補としてhandoffできるのは、次の全条件を満たした場合だけである。

### Specification

* canonical requirement/design/planにplaceholderがない。
* blocking open questionがない。
* design decisions `O-001`〜`O-008`にdispositionがある。
* fresh phase reviewer evidenceがある。
* strict specialist/fallback evidenceがreportにある。

### Implementation

* S01〜S06、S90がStep Result Approval済み。
  -全milestoneがcommittedまたはvalid approved-no-op。
* provider sourceがauthoritative。
* dogfood/install projection parityがpass。
* LATER scopeが混入していない。

### Verification

-全required closureがpass。

* focused/full pytest、ruff、mypy、SpecDock validate、diff checkがpass。
* hermetic Git、path safety、redaction、concurrency、legacy、install testsがpass。
* direct-argv manual evidenceがあり、shell syntaxを使っていない。
* runtimeがconsumer repoを意図せずdirtyにしない。

### Review

* per-step code/spec reviewがpass。
* S99 qa-reviewer pass。
* S99 issue-wide code-reviewer pass。
* S99 final spec-reviewer pass。
* reviewer outputはworker outputと独立している。

### Report

* Evidence Adoption LedgerにChatGPT researchの採否がある。
* no unresolved `blocked` / `stale` EAL entry。
* no `Status=open` decision entry。
* closure、delegation、reviewer、commit、docs、deferred hardeningが記録済み。
* secret/raw transcript/private reasoningをreportへ保存していない。

### Delivery

* maintainer-confirmed delivery routeを使用する。
* standalone maintenance routeなら通常のPR Delivery / Merge Preparation Gateへ進む。
* deferする場合は新しいfinal delivery Issue、dependency edge、理由、merge-ready非claimをparent plan/reportへ明記する。
* local closureだけでPR-ready/merge-readyを主張しない。
* final commit hashとpost-commit clean stateはexternal delivery evidenceとして記録する。

この契約の一項でも欠ける場合、結果は`blocked`または`incomplete`であり、completionを主張しない。

---
