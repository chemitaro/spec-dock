
---

種別: 要件定義書（Issue）
ID: "iss-00314"
タイトル: "Harden GitHub Sync Preflight Fetch And Receipt Contract"
関連GitHub: ["#314"]
状態: "active"
作成者: "main orchestrator"
最終更新: "2026-07-13"
親: ["epic-00295", "init-local-00003"]
-------------------------------------

## iss-00314 GitHub同期preflightのfetch・receipt契約を堅牢化する — Issue要件定義

## 0. 根拠と入力状態

指定ブランチ `iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract` は GitHub connector で参照でき、指定された HEAD `48a26046c185c9563d073543e66404c8c8c4178f` は Issue #314 の調査artifactを追加する commit として確認できた。 Issue node の `.meta.json` は `iss-00314`、親 `epic-00295`、GitHub Issue #314 との対応を記録している。

初期ChatGPT候補では、follow-up briefに示された値をplanning contextとして使用した。その後、runtime commandとGitHub stateをlive確認し、canonical採用時点では次のように確定した。

* input framing: `context-heavy`
* authorized profile: `standard`（`assurance classify/verify`で確認済み）
* GitHub-synced preflight: `pass`
* source manifest hash: `f65cb99ce4d79bb1f3f600d1b579d0cb886036b5cfd1c67baf3a761e9dec1a87`
* original incident `chemitaro/taikyohiyou_project#2098` は successor `chemitaro/spec-dock#314` への移管後に close 済み。

現在のbranch上では、Issue `requirement.md`、`design.md`、`plan.md` はmain orchestratorによりcanonical planning artifactとして具体化済みである。ChatGPT outputとspecialist artifactsは引き続きevidence-onlyであり、各phaseのfresh reviewer gateを置き換えない。

## 1. 概要

### 1.1 目的

`authoring preflight github-sync` を、次の一つの SpecDock-owned operation として堅牢化する。

```text
固定argvの必須fetch
  -> 保守的な失敗分類
  -> 同一capability shapeでの限定retry
  -> fetch後のrepository/source観測
  -> concurrent-change検査
  -> versioned pass/blocked receipt
  -> 安全なatomic publication
```

これにより、fetch の非ゼロ終了を根拠に呼び出し側agentが shell syntax、raw `git fetch`、権限昇格、暗黙fallbackを追加する必要をなくし、成功時と失敗時の双方で検証可能な証跡を返す。

### 1.2 観測可能な成果

完了後に観測できること:

* `github-synced` preflight は、request safety check 後に `git fetch --prune origin` を必ず SpecDock 内部で実行する。
* fetch attempt の終了種別、終了コード、所要時間、分類、分類確度、retry判断を machine-readable receipt から確認できる。
* retry対象と高い確度で判断できた失敗だけが、同一 executable、argv、repository、remote、environment policy、permission shape、output policy のまま限定回数再試行される。
* timeout、authentication、configuration、lock、transport、unknown 等を完全に同定できない場合でも、推測で権限を変えず fail-closed に block できる。
* `--output-dir` を指定すると、shell redirect なしで固定名の JSON receipt が保存される。
* pass だけでなく blocked/stale result も、出力先が安全であれば保存される。
* repository、worktree、HEAD、upstream、remote-tracking HEAD、source manifest は fetch 後の整合した観測として記録される。
* 観測中に branch、HEAD、worktree、remote-tracking ref、source manifest が変化した場合は `concurrent_repo_change` として block される。
* existing JSON/text fields、exit code、`local-context`、explicit default-branch fallback、source-path safety が維持される。
* provider asset、dogfood projection、installed consumer runtime で同一の observable behavior が確認される。
* skill/docs は、fetch failure を権限昇格の証拠にしない運用を明示する。

完了後に観測できてはいけないこと:

* fetch failure を `synced` または `verified` と扱うこと。
* cached remote-tracking ref を fresh fetch evidence と無条件に扱うこと。
* fetch failure を理由に `require_escalated`、shell wrapper、redirect、pipe、`tee`、heredoc、command substitution、inline environment assignment を追加すること。
* agent-owned raw `git fetch` を標準復旧経路にすること。
* `local-context` または default branch へ暗黙に切り替えること。
* raw stderr/stdout、credential-bearing URL、credential helper output、complete environment、token、secret、private key、host-local private path を durable receipt に保存すること。
* Git lock file を自動削除すること。
* canonical `requirement.md`、`design.md`、`plan.md`、`report.md`、`.assurance.json` を receipt writer が上書きすること。
* このIssueの結果を canonical adoption、reviewer pass、execution-ready、PR-ready、merge-ready と表現すること。

### 1.3 Issueの種類

* [x] 既存振る舞いの変更
* [x] 既存振る舞いの不具合修正
* [x] 仕様・文書の明確化
* [x] CLI / script 挙動変更
* [x] workflow / skill / agent導線の変更
* [x] metadata / sync / validate の変更
* [x] 後方互換性を伴う変更
* [x] secret / credential redaction に関係する変更
* [ ] 破壊的migration
* [ ] GitHub repositoryへの新しいmutation
* [ ] canonical docsのruntime自動更新

## 2. 背景・現在の問題

### 2.1 現在の実装

現行実装は、source manifest、worktree、branch、local HEAD の一部を fetch 前に取得する。その後 `origin` の存在を確認し、`_refresh_origin()` を呼び出す。

`_refresh_origin()` 自体は shell を使わず、固定argvの `git fetch --prune origin` を `subprocess.run()` で実行し、stdout/stderrをcaptureする。ただし timeout、retry、非対話化、typed outcome はなく、非ゼロ時は文字列だけを返す。

caller はその文字列を public result に保存せず、`origin_fetch_failed` と一般的な remediation に集約する。

現在の `PreflightResult` は status、refs、heads、source manifest、blockers、remediation を持つが、schema version、fetch attempt、timeout、classification、confidence、diagnostic disposition、snapshot identity、publication evidence を持たない。

CLI は `--format` を持つが、preflight用の `--output-dir` または `--report-path` を持たない。一方、後続の `pack prepare` は入力preflight JSON fileを必要とする。 Command handler は result をstdoutへrenderするだけである。

### 2.2 原インシデント

原インシデントでは次が観測された。

1. direct argv の preflight は一度 pass し、local/remote SHA が一致した。
2. JSON を保存するため shell redirect を加えた再実行で `origin_fetch_failed` となった。
3. explicit raw `git fetch` は成功したが、後続のpreflight内部fetchは再度失敗した。
4. public result に詳細なfetch outcomeがなく、実原因は事後確定できなかった。
5. caller agent が sandbox/network restriction を推測し、preflight全体へ `require_escalated` とredirectを追加してユーザー承認を発生させた。
6. Epic directory内の `rules.md` symlink がsource validationで拒否された件は期待されたfail-closed behaviorであり、主因ではない。

### 2.3 問題の因果関係

```text
fetch nonzero
  -> origin_fetch_failedだけが残る
  -> retryable/permanent/policy/unknownを区別できない
  -> SpecDock-owned retry contractがない
  -> callerが権限不足を推測
  -> command/permission shapeを変更
  -> shell redirectも追加
  -> 不要なapproval
```

本Issueは、単にエラーメッセージを詳しくするのではなく、実行、分類、retry、snapshot、receipt publication の責任を SpecDock 内へ閉じる。

## 3. 親スコープとのtraceability

### 3.1 親Epic

Parent Epic 00295 は、authoring runtimeを evidence generation / validation plane とし、canonical adoption・readiness・PR delivery をauthority planeに残す。provider-side assetsをsource of truthとし、dogfood `spec-dock/` はimplementation authorityではない。

本Issueは主に次のEpic requirementsを補強する。

| Epic requirement    | 本Issueでのtrace                                            |
| ------------------- | -------------------------------------------------------- |
| `E-RQ-RT-003`       | machine-readable receiptとhuman-readable diagnosticsを拡張する |
| `E-RQ-RT-004`       | existing status taxonomyを維持する                            |
| `E-RQ-RT-005`       | passをcommand-local resultに限定する                           |
| `E-RQ-RT-006`       | canonical docsをwriterの対象外にする                             |
| `E-RQ-RT-007`       | explicit output destinationとownershipを導入する               |
| `E-RQ-GH-001`       | repo-aware invocation前のmandatory preflightを維持する          |
| `E-RQ-GH-002`       | repository/ref/source observationを追加・明確化する               |
| `E-RQ-GH-003`       | local/remote HEAD comparisonをfresh fetch後に行う             |
| `E-RQ-GH-004`       | unsafe/stale/diverged statesのfail-closedを維持する            |
| `E-RQ-GH-005`〜`006` | explicit fallback semanticsを変更しない                        |
| `E-RQ-GH-007`       | unavailable observationをverifiedにしない                     |
| `E-RQ-GH-008`〜`011` | `local-context`を明示modeとして維持する                            |
| `E-RQ-NF-001`       | fail-closed                                              |
| `E-RQ-NF-002`       | classification/retry decisionのdeterministic policy       |
| `E-RQ-NF-003`       | secret/private diagnosticを保存しない                          |
| `E-RQ-NF-004`       | provider sourceとdogfood projectionを分離する                  |
| `E-RQ-NF-005`       | docs/helpを実装と一致させる                                       |
| `E-RQ-NF-006`       | safe positive/negative fixtures                          |
| `E-RQ-NF-007`       | old workspaceのin-place migrationを新たに保証しない                |

親Epicはpreflightがclean/synced branchでpassし、dirty、ahead/behind/diverged、missing branch、origin mismatch等をblockすること、provider/installed双方でtestすることを受け入れ条件としている。

### 3.2 再定義しない上位境界

本Issueは次を再定義しない。

* ChatGPT outputのauthorityは `evidence_only`。
* canonical adoptionはmain orchestratorとfresh reviewer gateが所有する。
* `local-context`は明示選択であり、`github_sync: not_verified` を維持する。
* default branch fallbackはexplicit opt-inだけを許可する。
* source-path symlink、parent traversal、repo外absolute pathの拒否を緩めない。
* backend command selection、ZIP review/stage、candidate validation、approval checkのauthority boundary。
* GitHub connectorをruntime subprocessから直接起動する新しいproduct dependency。
* parent EpicのIssue relay/delivery方針。

## 4. Actorと代表シナリオ

### 4.1 Actor

| Actor                            | 役割                                                     |
| -------------------------------- | ------------------------------------------------------ |
| CLI利用者 / Codex agent             | direct argvでpreflightを要求し、stdoutまたはreceiptを消費する        |
| SpecDock command layer           | CLI入力を型付きrequestへ変換し、exit codeとpresentationを返す         |
| Preflight application service    | fetch、snapshot、評価、publicationを一つのoperationとして統括する      |
| Git fetch adapter                | 固定argv、非対話environment、timeout付きでchild processを実行する     |
| Git repository snapshot observer | post-fetch local/remote/source stateを観測する              |
| Receipt writer                   | explicit safe destinationへatomic JSON publicationを行う   |
| `authoring pack prepare`         | pass receiptを読み、内部整合とreceipt bindingを検証する              |
| Maintainer / operator            | permanent failureの設定・credential・network remediationを行う |
| Installed consumer repository    | provider assetから配布された同一runtime behaviorを利用する           |

### 4.2 代表シナリオ

#### SC-001: clean/synced branch

* 前提: worktree clean、named branch、origin/upstreamあり、local HEADとfresh remote-tracking HEADが一致。
* 操作: direct argvで `authoring preflight github-sync` を実行する。
* 結果: `status=pass`、`sync_state=synced`、`github_sync=verified`、fetch attempt、snapshot、source hashesが出力される。
* 観測点: stdout JSON/text、任意のreceipt file、exit code 0。

#### SC-002: retryable failure後の成功

* 前提: 最初のfetchだけが高確度の一時障害として終了し、次の同一fetchが成功する。
* 操作: preflightを一度だけ呼ぶ。
* 結果: SpecDock内部で限定retryされ、callerはcommand shapeを変えない。receiptには全attemptが記録される。
* 観測点: attempt count、classification、retry decision、最終status。

#### SC-003: permanentまたはunknown failure

* 前提: authentication、host identity、repository configuration、execution denial、unknown failureのいずれか。
* 操作: preflightを実行する。
* 結果: 自動権限昇格、fallback、raw fetchを行わず、bounded blocked receiptを返す。
* 観測点: blocker、failure class、confidence、redacted diagnostic、remediation、exit code 1。

#### SC-004: receipt保存

* 前提: 安全なexisting output directoryが明示される。
* 操作: `--output-dir <dir>` 付きでpreflightを実行する。
* 結果: stdout formatに関係なく固定名JSON receiptがatomicに公開される。
* 観測点: fileのvalid JSON、ownership marker、digest、mode、old/new file atomicity。

#### SC-005: concurrent repository change

* 前提: fetch後のsnapshot取得中またはpublication直前にsource、HEAD、branch、worktree、remote-tracking refが変化する。
* 操作: preflightを実行する。
* 結果: `concurrent_repo_change` でblockし、mixed-time snapshotをpassにしない。
* 観測点: snapshot IDs、guard result、blocker。

#### SC-006: pack preparation

* 前提: versioned pass receiptが保存されている。
* 操作: `authoring pack prepare --preflight <receipt>` を実行する。
* 結果: receipt kind/schema/digest/semantic fieldsが検証され、receipt digestとsnapshot IDがprompt pack provenanceへbindingされる。
* 観測点: `provenance.json`、`stale-if.json`、pack prepare result。

## 5. スコープ

### 5.1 MUST — 本Issueの実装・closure対象

1. Mandatory fixed fetchの維持。
2. fetch subprocessのtimeout、非対話environment、captured bytes、typed termination outcome。
3. 保守的なfailure taxonomyとclassification confidence。
4. retry対象をallowlistしたbounded same-capability retry。
5. pass/blocked/stale resultのversioned additive receipt schema。
6. bounded/redacted diagnostic。
7. optional `--output-dir` と固定receipt filename。
8. unsafe/canonical/symlink/non-regular/non-owned targetの拒否。
9. same-directory temporary fileとatomic replaceによるpublication。
10. github-synced modeにおけるpost-fetch snapshot。
11. source manifestを含むpre/post concurrent-change guard。
12. fetch failure時のcached remote refをunverifiedと明示すること。
13. existing stdout JSON/text fieldsとexit codeの互換性。
14. new receiptのdigest/semantic validationとpack provenance binding。
15. legacy unversioned preflight JSONの互換読み取り。
16. provider、dogfood、fresh install/update runtimeのparity検証。
17. installed skillとworkflow docsの運用契約更新。
18. focused unit、hermetic Git、CLI、path safety、projection/install tests。

### 5.2 SHOULD — 本Issueのclosureを妨げない後続候補

* `pack prepare` 実行時にcurrent repository identity、HEAD、worktree、source manifestを再計算してreceiptと比較する。
* explicit operator-configured evidence rootを導入し、repo-local ignored output rootを安全に許可する。
* timeout/cancellation時のchild process tree containmentをplatform別に強化する。
* legacy unversioned receiptの廃止時期をrelease policyとして定める。
* classifier fixture corpusを複数Git/SSH/credential helper versionへ拡張する。

### 5.3 LATER — 本Issueでは実装しない

* backend invocation直前のmandatory final fetch。
* preflight→pack prepare→backend invokeの単一orchestration command。
* immutable/digest-verified launcherまたはoperator-managed privileged capability。
* Git Trace2によるfailure analysis。
* 全authoring writerの共通atomic writerへの一括移行。
* POSIX `openat` / `dir_fd`を使ったcross-platform hostile-race hardening。
* runtimeからGitHub connectorを直接呼び出すintegration。
* raw Git permissionやdanger-full-accessの拡張。

### 5.4 対象外

* mandatory fetchの削除。
* `git ls-remote`、cached refs、connector observationだけによるfetch代替。
* agent-owned raw `git fetch`。
* retryのためのpermission/sandbox変更。
* Git lock fileの自動削除。
* `local-context`への自動降格。
* default branchへのsilent fallback。
* canonical docsまたは`.assurance.json`へのreceipt保存。
* public status taxonomyの大規模再設計。
* user-configurable retry/timeout optionの多数追加。
* 新しいthird-party dependency。

## 6. 機能要件

### RQ-FUNC-001: Mandatory fetch ownership

`github-synced` preflightは、request/destinationの安全性検査を通過した後、SpecDock内部で固定の `git fetch --prune origin` を実行しなければならない。

### RQ-FUNC-002: Fixed execution shape

全attemptは次を維持しなければならない。

* logical executable
* argv
* working repository
* remote name
* environment policy
* timeout policy
* output capture policy
* callerから観測されるpermission/sandbox context

SpecDockはfetch outcomeを理由にこのshapeを変更してはならない。

### RQ-FUNC-003: Noninteractive bounded execution

fetchはterminal promptを要求しないenvironmentで実行し、有限のtimeoutを持たなければならない。timeoutの具体値はmaintainer-confirmed design constantとし、要求定義では固定しない。

### RQ-FUNC-004: Typed attempt evidence

各attemptは少なくとも次を記録しなければならない。

* attempt number
* termination kind
* return codeまたはspawn/timeout/cancel outcome
* duration
* failure class
* classification confidence
* retryable decision
* bounded diagnostic metadata

### RQ-FUNC-005: Conservative classification

classificationはOS-level outcome、timeout、static repository facts、allowlisted diagnostic signalを用いる。exit codeまたはstderr単独をroot causeの確定証拠としてはならない。分類不能は `unknown` とする。

### RQ-FUNC-006: Bounded retry

retryはmaintainer-confirmed finite budgetを持ち、allowlisted retryable classに限る。authentication、host identity、repository configuration、execution denial、spawn failure、cancellation、unknownは自動retryしてはならない。

具体的attempt数、timeout、backoffはdesign constantとして確定し、実行中またはagent判断で変更してはならない。

### RQ-FUNC-007: No escalation or fallback

fetch failureを理由に次を行ってはならない。

* permission escalation
* shell syntax追加
* raw fetchへの切替
* default branch fallbackの追加
* `local-context`への切替
* lock file削除

### RQ-FUNC-008: Versioned additive receipt

receiptはschema versionとreceipt kindを持ち、既存top-level fieldsを削除・renameせず、fetch、repository、freshness、publication、digest evidenceをadditiveに保持しなければならない。

### RQ-FUNC-009: First-class output destination

preflightはoptionalなfirst-class output destinationを持ち、shell redirectなしでmachine-readable JSON receiptを保存できなければならない。

### RQ-FUNC-010: Safe atomic publication

receipt writerは次を満たさなければならない。

* fixed filename
* explicit destination
* symlink component拒否
* canonical/protected root拒否
* non-regular target拒否
* non-owned existing target拒否
* same-directory temporary file
* flushとfile fsync
* atomic replace
* best-effort parent directory durability
* failure時のprevious target保護
* success/blocked双方のpublication

### RQ-FUNC-011: Post-fetch snapshot

github-syncedのfinal sync評価に使う次の値は、fetch終了後に取得しなければならない。

* current branch
* local HEAD
* normalized origin identity
* upstream
* remote-tracking HEAD
* ahead/behind/diverged state
* worktree state
* source manifest
* remote observation source/disposition

### RQ-FUNC-012: Concurrent-change guard

snapshot取得前後およびreceipt公開直前のcritical stateが一致しない場合、preflightはpassしてはならない。

### RQ-FUNC-013: Unverified cached ref

fetchが成功していない場合、cached remote-tracking refを既存互換fieldへ出力することは許容できるが、必ず `unverified_cache` 等の明示dispositionを伴い、`github_sync=verified` にしてはならない。

### RQ-FUNC-014: Pack receipt binding

versioned receiptを `pack prepare` が消費する場合、receipt kind、schema、digest、pass semantics、fetch success、snapshot guardを検査し、receipt digestとsnapshot identityをprompt pack provenanceへ引き継がなければならない。

本IssueのMUST scopeでは、pack時点のcurrent repository再観測までは要求しない。その不保証をdocsとprovenanceで明示する。

### RQ-FUNC-015: Legacy compatibility

legacy unversioned preflight JSONは、既存required fieldsとsemantic checksを満たす限り引き続き読み取れること。legacy inputからnew receipt digestまたはcurrent freshnessを推測してはならない。

### RQ-FUNC-016: Projection parity

provider-side assetをimplementation sourceとし、dogfood projectionとfresh installed consumerでCLI、receipt、tests、docs/skillが同一のobservable contractを持たなければならない。

### RQ-FUNC-017: Documentation contract

installed skill/docsは次を明示しなければならない。

* direct argvで実行する。
* shell wrapper、pipe、redirect、`tee`、heredoc、command substitution、inline env assignmentを使わない。
* `origin_fetch_failed` またはfetch nonzeroを追加権限の証拠にしない。
* retryはSpecDockが所有する。
* raw `git fetch`を標準復旧経路にしない。
* `local-context`またはdefault branchへ暗黙fallbackしない。
* receiptはevidenceでありcanonical authorityではない。
* receipt publication時点以後のremote freshnessは別gateなしには保証しない。

## 7. 非機能要件

### RQ-NF-001: Fail-closed

classification、snapshot、publication、digest、path safetyのいずれかを確定できない場合、成功を推測してはならない。

### RQ-NF-002: Deterministic policy

同じcaptured process outcomeと同じrepository snapshotに対し、failure class、confidence、retry decision、blocker、statusをdeterministicに返すこと。timestampsや実所要時間の一致は要求しない。

### RQ-NF-003: Security and redaction

durable receiptおよびstdoutへ次を出してはならない。

* raw unbounded stdout/stderr
* credential-bearing URL
* URL userinfo/query credential
* credential helper output
* complete environment
* token、password、secret、private key
* host-local private path
* raw HTTP authorization material

diagnostic excerptとdigestはredaction後のsafe representationだけを対象とする。

### RQ-NF-004: Bounded resource use

attempt数、timeout、diagnostic bytes、existing target parse、retry delayはfinite boundを持つこと。具体値はdesignで一元化し、CLI callerが任意に拡張できないこと。

### RQ-NF-005: Testability

clock、sleeper、fetch executor、snapshot observer、writerをtest doubleに置換でき、real network、real GitHub、実時間backoffに依存せずpolicyを検証できること。

### RQ-NF-006: Hermetic integration

Git sync behaviorはlocal bare repositoryとfake executableで検証でき、external networkをrequired test dependencyにしないこと。

### RQ-NF-007: No new dependency

stdlibと既存runtime contractで実現し、新しいthird-party dependencyを導入しないこと。必要になった場合はplan amendmentを行う。

### RQ-NF-008: Portability

Linux/macOS/Windowsで意味論が同じであること。platform固有のdirectory fsync/process tree保証は、サポート可能な範囲を明示し、保証できない部分を成功扱いしない。

### RQ-NF-009: Evidence-only authority

receipt、pack provenance、tests、docs updateはいずれもcanonical adoption、reviewer pass、execution readiness、PR readinessを自己主張しない。

## 8. 振る舞い

### BH-001: clean sync

* Given: requestが安全で、fetchが成功し、post-fetch snapshotがclean/syncedである。
* When: github-synced preflightを実行する。
* Then: pass receiptを返す。
* And: fetch attempt、snapshot、source manifest、freshness dispositionが記録される。

### BH-002: retryable fetch failure

* Given: 最初のattemptがallowlisted retryable failureで、budgetが残る。
* When: preflightを実行する。
* Then: 同一shapeで内部retryする。
* And: callerへ追加permissionや再実行を要求しない。

### BH-003: permanent/unknown failure

* Given: failureがnon-retryableまたはunknownである。
* When: preflightを実行する。
* Then: retryせずblocked receiptを返す。
* And: actionableかつredactedなremediationを返す。

### BH-004: receipt publication

* Given: safe explicit output directoryがある。
* When: `--output-dir` 付きで実行する。
* Then: fixed filenameのJSON receiptをatomic publishする。
* And: stdout resultも既存formatで返す。

### BH-005: unsafe publication target

* Given: symlink、canonical root、repo内非許可先、non-regular target、non-owned targetのいずれか。
* When: receipt publicationを要求する。
* Then: targetを変更せずblockする。

### BH-006: concurrent repository change

* Given: snapshot中にcritical stateが変わる。
* When: final guardを実行する。
* Then: `concurrent_repo_change` でblockする。

### BH-007: fetch failure with cached ref

* Given: cached `origin/<ref>` があるがfetchは失敗する。
* When: preflightを実行する。
* Then: cached valueをfresh verified evidenceにしない。

### BH-008: pack binding

* Given: valid versioned pass receiptがある。
* When: pack prepareがreceiptを読む。
* Then: receipt digest/snapshotを検証・bindingする。
* And: current repository再検証を行っていないことを隠さない。

### BH-009: legacy caller

* Given: callerが `--output-dir` を使わず、既存fieldsだけを読む。
* When: preflightを実行する。
* Then:既存stdout/exit behaviorが維持される。

## 9. 受け入れ条件

### AC-001: mandatory fixed fetch

* Actor: CLI caller。
* 前提: safe github-synced request。
* 操作: preflightを実行する。
* 期待結果: logical command `git fetch --prune origin` が一度以上実行され、shellを介さない。
* 観測点: spy executor / integration fixture。
* 関連: `RQ-FUNC-001`, `RQ-FUNC-002`, `CON-002`。

### AC-002: structured success attempt

* 前提: fetch成功。
* 操作: JSON preflightを実行する。
* 期待結果: version、receipt kind、fetch status、attempt count、return code、duration、policy IDが出力される。
* 関連: `RQ-FUNC-004`, `RQ-FUNC-008`。

### AC-003: bounded retry

* 前提: 最初のattemptがallowlisted retryable class、次が成功。
* 操作: preflightを一度実行する。
* 期待結果: budget内でのみretryし、全attemptのexecution shapeが一致する。
* 関連: `RQ-FUNC-005`, `RQ-FUNC-006`。

### AC-004: non-retryable and unknown

* 前提: authentication、configuration、host identity、execution denial、spawn failure、cancel、unknown。
* 操作: preflightを実行する。
* 期待結果: 自動retryせずblocked resultを返す。
* 関連: `RQ-FUNC-005`〜`007`。

### AC-005: timeout and noninteractive mode

* 前提: child fetchがpolicy timeoutを超える。
* 操作: preflightを実行する。
* 期待結果: attemptはtimeoutとして終了し、terminal prompt待ちの無期限hangにならず、policyに従ってretryまたはblockする。
* 関連: `RQ-FUNC-003`, `RQ-NF-004`。

### AC-006: durable blocked receipt

* 前提: safe output directory、fetch permanent failure。
* 操作: `--output-dir`付きで実行する。
* 期待結果: exit code 1とblocked receipt fileの両方が得られる。
* 関連: `RQ-FUNC-008`〜`010`。

### AC-007: diagnostic redaction

* 前提: stderrにcredential URL、token、host path、non-UTF-8、上限超過textが含まれる。
* 操作: blocked receiptを生成する。
* 期待結果: unsafe valuesがstdout/fileへ現れず、safe code、redacted excerpt、redacted digest、byte count、truncation flagだけが残る。
* 関連: `RQ-NF-003`, `RQ-NF-004`。

### AC-008: pass receipt publication

* 前提: safe explicit output directory、clean/synced branch。
* 操作: textまたはJSON formatで `--output-dir` を指定する。
* 期待結果: stdout formatに関係なくfixed JSON receiptが作成される。
* 関連: `RQ-FUNC-009`, `RQ-FUNC-010`。

### AC-009: output path safety and atomicity

* 前提: symlink/canonical/non-regular/non-owned target、またはreplace前failure。
* 操作: receipt publicationを試みる。
* 期待結果: unsafe targetは変更されず、既存valid receiptはpartial writeで壊れない。
* 関連: `RQ-FUNC-010`。

### AC-010: post-fetch observation

* 前提: remoteがlocal cloneより先へ進んでいる。
* 操作: preflightを実行する。
* 期待結果: fetch後のremote-tracking HEADを観測し、`behind_remote` としてstaleにする。
* 関連: `RQ-FUNC-011`。

### AC-011: concurrent-change blocking

* 前提: source、branch、HEAD、status、remote refのいずれかがsnapshot中に変わる。
* 操作: preflightを実行する。
* 期待結果: passではなく `concurrent_repo_change` を返す。
* 関連: `RQ-FUNC-012`。

### AC-012: cached ref disposition

* 前提: cached remote refあり、fetch失敗。
* 操作: preflightを実行する。
* 期待結果: `github_sync=failed` かつremote evidence dispositionが`unverified_cache`または`unavailable`になる。
* 関連: `RQ-FUNC-013`。

### AC-013: additive compatibility

* 前提: existing callerが旧top-level keysとexit codeを利用する。
* 操作: new runtimeでpreflightを実行する。
* 期待結果:既存keysの意味とexit codeが維持され、new keysはadditiveである。
* 関連: `RQ-FUNC-008`, `RQ-FUNC-015`。

### AC-014: pack receipt integrity

* 前提: valid versioned pass receipt。
* 操作: pack prepareを実行する。
* 期待結果: kind/schema/digest/fetch/snapshot semanticsを検査し、receipt digest/snapshotをprovenanceへ記録する。
* 関連: `RQ-FUNC-014`。

### AC-015: tampered/inconsistent receipt

* 前提: digest mismatch、`status=pass`なのにfetch failed、unstable concurrent guard等。
* 操作: pack prepareを実行する。
* 期待結果: prompt packをpassとして作らずfail-closedにする。
* 関連: `RQ-FUNC-014`, `RQ-NF-001`。

### AC-016: unchanged existing semantics

* 前提: `local-context`、explicit fallback、unsafe source symlink、missing source等の既存fixture。
* 操作: new runtimeで既存testsを実行する。
* 期待結果:既存status/blocker/authority semanticsが維持される。
* 関連: `CON-004`, `CON-005`。

### AC-017: provider/dogfood/install parity

* 前提: provider source、checked-in dogfood projection、fresh init/update target。
* 操作: help、pass、blocked、receipt publication testsを実行する。
* 期待結果:三surfaceで同一contractを示す。
* 関連: `RQ-FUNC-016`。

### AC-018: skill/docs operation policy

* 前提: installed skill/docs。
* 操作: structural assertionsとdocs reviewを行う。
* 期待結果: direct argv、no shell、no escalation、SpecDock-owned retry、no implicit fallback、freshness boundaryが明記される。
* 関連: `RQ-FUNC-017`。

### AC-019: no authority escalation

* 操作: JSON/text/receipt/docsを検査する。
* 期待結果: canonical adoption、reviewer pass、execution-ready、PR-ready等の達成claimがない。
* 関連: `RQ-NF-009`。

### AC-020: full focused quality gate

* 操作: focused unit/CLI/hermetic Git/path safety/install tests、ruff、mypy、SpecDock validate、docs parityを実行する。
* 期待結果: required checksがpassし、意図しないgenerated/bytecode/worktree changesがない。
* 関連: 全MUST requirements。

## 10. 例外・エッジケース

| ID       | 条件                                                | 期待される扱い                                                            |
| -------- | ------------------------------------------------- | ------------------------------------------------------------------ |
| `EC-001` | `git` executable spawn失敗                          | retryせず`spawn_failure`、blocked                                     |
| `EC-002` | fetch timeout                                     | `timeout`としてbounded retryまたはblocked                                |
| `EC-003` | DNS/connection reset/5xx/throttleの明確なsignal       | probable transient class、budget内だけretry                            |
| `EC-004` | authentication/authorization/repository-not-found | private repo maskingを考慮して一群にし、retryせずoperator remediation          |
| `EC-005` | host key / certificate identity failure           | retryせず、policyを自動変更しない                                             |
| `EC-006` | local ref lock contention                         | short bounded retry、lockを削除しない                                     |
| `EC-007` | stderrだけではpermission sourceが不明                    | permission escalationせずunknownまたはnon-retryable                     |
| `EC-008` | empty stdout/stderr                               | unknown、fail-closed                                                |
| `EC-009` | non-UTF-8 diagnostic                              | replacement decode後redactし、raw bytesを保存しない                         |
| `EC-010` | diagnostic上限超過                                    | truncate flagとsafe digestを記録                                       |
| `EC-011` | output directory absent/non-directory             | publication開始前にblock                                               |
| `EC-012` | symlinkまたはbroken symlink target                   | reject/blockし、link先を変更しない                                          |
| `EC-013` | existing targetが他用途のfile/malformed JSON           | non-owned targetとして保存しない                                           |
| `EC-014` | write/fsync/replace failure                       | statusをblockedにし、previous targetを保持                                |
| `EC-015` | publicationだけ失敗しsync observationは成功               | top-level commandはblocked。sync evidenceとpublication evidenceを混同しない |
| `EC-016` | fetch失敗だがcached remote refあり                      | unverified cacheと明示しverifiedにしない                                   |
| `EC-017` | snapshot中のsource edit                             | concurrent changeとしてblock                                          |
| `EC-018` | snapshot中のcheckout/commit                         | concurrent changeとしてblock                                          |
| `EC-019` | user cancellation                                 | retryせずcancel outcome。success receiptを作らない                         |
| `EC-020` | legacy receipt                                    | legacyとして読み、new digest/freshnessを捏造しない                             |
| `EC-021` | versioned receiptのdigest mismatch                 | pack prepareをblock                                                 |
| `EC-022` | output先がrepo内                                     | first-PR候補設計ではblock。将来のignored evidence rootは別判断                   |
| `EC-023` | `local-context`                                   | fetch/retry/publicationのgithub-synced claimsを適用しない                 |
| `EC-024` | explicit default fallback                         | 既存requested/effective ref semanticsを維持                             |
| `EC-025` | source pathのsymlink                               | 既存blockを維持し、緩和しない                                                  |

## 11. 入出力契約例

### 11.1 Candidate CLI

```text
./spec-dock/scripts/spec-dock authoring preflight github-sync
  --repo-root <REPOSITORY_ROOT>
  --ref <BRANCH>
  --source-path <PATH>
  --format json
  --output-dir <EXISTING_EXTERNAL_OUTPUT_DIRECTORY>
```

実際にはshell wrapper、redirect、pipeを付けず、引数配列として実行する。

### 11.2 Candidate receipt filename

```text
github-sync-preflight.receipt.json
```

### 11.3 Candidate top-level shape

```json
{
  "schema_version": 1,
  "receipt_kind": "spec-dock.authoring.github-sync-preflight",
  "status": "blocked",
  "evidence_mode": "github-synced",
  "sync_state": "blocked",
  "github_sync": "failed",
  "requested_ref": "feature/example",
  "effective_ref": "feature/example",
  "local_head": "0123456789abcdef",
  "remote_head": "fedcba9876543210",
  "source_manifest_hash": "sha256-value",
  "fetch": {
    "status": "failed",
    "policy_id": "origin-fetch-v1",
    "attempt_count": 1,
    "final_failure_class": "remote_access_denied_or_not_found",
    "classification_confidence": "probable",
    "attempts": []
  },
  "freshness": {
    "remote_head_disposition": "unverified_cache",
    "snapshot_id": "sha256-value",
    "concurrent_change_check": "stable"
  },
  "publication": {
    "requested": true,
    "status": "published",
    "filename": "github-sync-preflight.receipt.json"
  },
  "blockers": ["origin_fetch_failed"],
  "remediation": ["inspect origin access without changing command permissions"],
  "authority": "evidence_only",
  "adoption_requires": "explicit_eal_disposition",
  "bundle_generation_not_promotion": true,
  "receipt_digest": {
    "algorithm": "sha256-canonical-json-v1",
    "value": "sha256-value"
  }
}
```

この例のenum、field、numeric valueはdesign候補であり、maintainer confirmation前のcanonical contractではない。

## 12. 互換性・migration

### 12.1 CLI互換性

* `--output-dir` はoptional additive flag。
* flagなしのstdout-only pathは維持する。
* `--format text|json` はstdoutだけを制御し、file receiptはJSON固定。
* `pass=0`、`blocked/stale=1`、argument contract error=2を維持する。
* first PRでは`--report-path`を併設しない。

### 12.2 JSON/text互換性

削除・renameしないfield:

* `status`
* `evidence_mode`
* `sync_state`
* `authority`
* `github_sync`
* `requested_ref`
* `effective_ref`
* `local_head`
* `remote_head`
* `source_manifest_hash`
* `source_paths`
* `source_hashes`
* `source_hash_mismatch_checked`
* `blockers`
* `remediation`
* `adoption_requires`
* `bundle_generation_not_promotion`

新fieldはadditiveにする。

### 12.3 Persisted receipt互換性

* new explicit schemaはversion 1。
* existing unversioned JSONは`legacy_unversioned`として一時互換。
* legacyを読む場合はreceipt digest/snapshot bindingなしと明示する。
* breaking schema changeはversion incrementを必要とする。
* automatic migrationまたは既存file rewriteは行わない。

### 12.4 Installed workspace

* `spec-dock init/update` でprovider assetから新runtime/docs/skillが配布される。
* old workspaceへの自動in-place data migrationは導入しない。
* new output fileはexplicit request時だけ作成する。

## 13. セキュリティ・プライバシー

* fetch operationは既存credential/helperを利用できる必要があるが、credential dataをreceiptへ保存しない。
* environmentはinherit-and-sanitize policyを使い、complete environmentは記録しない。
* logical executableとfixed argvは記録可能だが、credential-bearing argumentは存在させない。
* normalized origin identityはuserinfo、query、secretを除去する。
* diagnosticはredaction後のexcerptとdigestだけを保存する。
* redaction前streamのdigestも、low-entropy secret fingerprintとなり得るため保存しない。
* `GIT_TERMINAL_PROMPT=0` 等の非対話化を使う。
* third-party GUI credential helperを完全に抑止できない場合、その不保証を明示し、timeout/cancelでfail-closedにする。
* output fileはprivate-by-default permissionを用いる。
* repo内、canonical root、symlinked pathへの保存をfirst-PR success pathにしない。
* receiptはGitHub mutationを行わない。
* operation failureをpermission evidenceとして扱わない。

## 14. 制約

### CON-001: Provider-side authority

実装sourceは `src/spec_dock/assets/...`。`spec-dock/...` dogfood projectionのみを直接修正してはならない。

### CON-002: Fixed fetch

fetch unitは `git fetch --prune origin` を維持する。変更が必要ならrequirement/design amendmentを行う。

### CON-003: No shell / no escalation

shell syntax、permission escalation、raw agent fetchを解決策にしない。

### CON-004: Explicit evidence mode/fallback

`local-context`とdefault branch fallbackはexplicitな既存optionだけを使う。

### CON-005: Existing contract preservation

既存status、top-level fields、exit codes、source safetyを不要に変更しない。

### CON-006: Secret boundary

raw diagnostics、credentials、complete environmentをdurable evidenceにしない。

### CON-007: Canonical write prohibition

receipt writerはcanonical docs、`.assurance.json`、managed node metadataを変更しない。

### CON-008: Lock safety

Git lock fileを自動削除しない。

### CON-009: Bounded implementation scope

immutable launcher、Trace2、all-writer refactor、backend final fetch、connector integrationをfirst PRへ含めない。

### CON-010: No authority claim

result、docs、tests、reportはcanonical adoption、reviewer pass、readinessを自己主張しない。

## 15. 等級

### 15.1 推奨grade

* [x] `strict`

### 15.2 理由

* 公開CLIへadditive optionを追加する。
* machine-readable receipt schemaを追加する。
* Git/network/filesystem/subprocess behaviorを変更する。
* installed runtime、dogfood projection、skill/docsへ影響する。
* backward compatibilityとsecurity/redactionの検証が必要。
* concurrency/TOCTOUとatomic filesystem behaviorを扱う。
* provider/install parityが必要。

### 15.3 Critical escalation guard

次が必要になった場合は、strictのまま吸収せず再分類する。

* raw credential/helper outputの保存。
* privileged/immutable launcherの導入。
* destructive overwriteまたは既存user file削除。
* GitHubへの新しいcredentialed mutation。
* repo-wide writer migration。
* rollback不能schema migration。
* security boundaryをoperator approvalなしで変更すること。

## 16. 依存関係

### 前提

* Epic 00295のauthoring runtime、preflight、pack prepare、installed skill/docs。
* current branchの調査artifact。
* current preflight tests。
* strict planning contract。
* main orchestratorによるrequirement/design/plan candidate adoptionとfresh review。

### 後続候補

* pack時点current repository revalidation。
* backend invocation直前final fetch/check。
* generic authoring atomic writer。
* immutable launcher/capability。
* connector-visible observation gapの解消。

## 17. 設計・計画への引き渡し

Designで固定する事項:

1. 最小component split。
2. process outcomeとfailure taxonomy。
3. classification confidence。
4. retry decision tableとpolicy constants。
5. inherited/sanitized environment。
6. receipt schema/digest。
7. output path safetyとatomic writer。
8. post-fetch snapshotとconcurrent guard。
9. pack receipt integrity boundary。
10. CLI/text/JSON compatibility。
11. provider/dogfood/install projection。
12. rollback。
13. first PRとLATERの境界。

Planで分解する成果:

1. versioned fetch outcome tracer。
2. conservative classification/retry/redaction。
3. first-class atomic receipt publication。
4. post-fetch snapshot/concurrent guard。
5. pack receipt binding/legacy compatibility。
6. provider/dogfood/install parity。
7. docs/skill更新。
8. final QA/code/spec gate。

## 18. 採用済みmaintainer decision

### Q-001: Output API

* 選択肢:

  * A: `--output-dir` + fixed filename。
  * B: `--report-path`。
  * C: 両方。
* 採用: A（`--output-dir` + fixed filename）。first PRでは `--report-path` を追加しない。
* 理由: basename、拡張子、canonical filename等の入力面を減らす。
* 影響: CLI、writer、tests、docs。

### Q-002: Retry/timeout constants

* 決める値:

  * total attempt budget
  * timeout per attempt
  * retry delay
  * jitterの有無
* 採用:

  * total attempts 2
  * timeout 60 seconds/attempt
  * single fixed delay 250 ms
  * first PRではjitterなし
* 理由: bounded、deterministic、over-engineering回避。
* 注記: 上記は一箇所のdesign policy constantとして管理し、CLI optionにはしない。

### Q-003: Diagnostic bound

* 決める値: safe excerpt上限。
* 採用: redaction後UTF-8 1024 bytes/attempt。
* digest対象: redacted full diagnostic。

### Q-004: Output root

* 選択肢:

  * A: first PRはexisting external directoryのみ。
  * B: repo-local ignored rootも許可。
  * C: operator-configured root。
* 採用: first PRは明示されたexisting external directoryだけをdelegated output rootとして扱い、repo-local output、protected canonical tree、symlink component、non-directory、unsafe existing targetを拒否する。
* 理由: receipt publication自身が観測直後のworktreeをdirtyにし、freshness evidenceと実行後stateを食い違わせることを防ぐため。repo-local ignored rootやoperator-configured rootはfollow-upで扱う。

### Q-005: Pack freshness boundary

* 選択肢:

  * A: first PRはreceipt integrity/bindingのみ。
  * B: current repo HEAD/source/worktreeをpack時に再観測。
  * C: backend直前まで統合。
* 採用: Aを本IssueのMUST、Bをnon-blocking follow-up、CをLATERとする。

### Q-006: Remote observation terminology

Parent Epicはconnector-visible branch/HEADを要求するが、現行CLIのdefault observerはfetch後のlocal remote-tracking refを読む。本Issue候補はそれを `fetched_remote_tracking_ref` と正直に記録し、direct connector integrationはLATERとする。

* 採用: receiptは `fetched_remote_tracking_ref` をtruthful observation sourceとして記録する。Epic wordingの広域整理とdirect connector integrationは本IssueのLATERであり、実装済みと主張しない。

### Q-007: PR delivery route

Issue 314はoriginal Epic sequence完了後のsuccessor maintenance Issueである可能性が高い。既存parent planの旧final Issueへ暗黙にdeliveryを再委譲してはならない。

* 採用: standalone maintenance Issueとして通常のPR Delivery / Merge Preparation Gateを使う。旧 `iss-00307` へ暗黙deferしない。

## 19. Candidate review checklist

* [ ] すべてのMUST requirementがdesign IDへ追跡されている。
* [x] Q-001〜Q-007のmaintainer decisionがcanonical requirementへ反映されている。
* [ ] Q-006のparent Epic contract gapが隠されていない。
* [ ] Q-007のdelivery routeが明示されている。
* [ ] numeric defaultsがrequirementとして無断固定されていない。
* [ ] LATER項目がfirst PR acceptanceへ混入していない。
* [ ] authority boundaryが維持されている。
* [ ] fresh `spec-reviewer` verdictは別途必要である。

---
