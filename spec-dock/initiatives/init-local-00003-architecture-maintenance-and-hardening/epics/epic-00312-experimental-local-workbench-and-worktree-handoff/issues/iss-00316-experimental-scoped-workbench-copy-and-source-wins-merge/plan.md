---
種別: 実装計画書（Issue）
ID: "iss-00316"
タイトル: "Experimental Scoped Workbench Copy And Source Wins Merge"
関連GitHub: ["#316"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00316 Experimental Scoped Workbench Copy And Source Wins Merge — 実装計画書（Standard）

## 1. この計画で満たす要件
- RQ-316-001–010、AC-316-001–010、EC-316-001–009。
- 親Epic W2を閉じ、最終distribution/docs/full quality/PRをIssue 319へrelayする。
- `authorized_profile=standard`。Symlink/containment、copy-time partial failure、manual linked-worktreeは追加obligationとして省略しない。

## 2. 依存関係から導く実装順序
```text
S00 baseline / planning gate
  -> S01 shared target resolver characterization
  -> S02 thin vertical copy command
  -> S03 independent scope + pre-mutation failures
  -> S04 source-wins opaque recursive merge
  -> S05 symlink / containment / copy failure
  -> S06 output / regression / manual relay
  -> S90 docs impact
  -> S99 final quality / deferred delivery / finish
```

- 各stepは前stepのfresh reviewer pass、report update、commit、clean tree後だけ開始する。
- Step中に親境界、observable semantics、required closureを変える必要が生じた場合は実装を止め、plan amendmentとfresh spec reviewを行う。

## 3. ステップ一覧と要件対応
| Step | Behavior slice | Closes | Depends on | Commit candidate |
|---|---|---|---|---|
| S00 | Baseline/assurance/evidence固定 | 実装開始条件 | planning reviews | planning docs |
| S01 | Existing target selector共有化 | AC-316-002、EC-006/007 | S00 | `refactor(worktree)` |
| S02 | Thin vertical happy path | AC-316-001、AC-316-003/005/009の最小経路 | S01 | `feat(workbench)` |
| S03 | Independent scope/preflight/no_source | AC-316-003/004、EC-001/009 | S02 | `feat(workbench)` |
| S04 | Recursive merge/content opacity | AC-316-005/006、EC-001/003/004 | S03 | `feat(workbench)` |
| S05 | Symlink/containment/failure | AC-316-007/008、EC-002/005/008/009 | S04 | `fix(workbench)` |
| S06 | Output/regression/manual relay | AC-316-001/002/009/010 | S05 | `test(workbench)` or approved-no-op |
| S90 | Docs impact resolution | RQ-316-009/010 | S06 | docs commit or approved-no-op |
| S99 | Whole-Issue quality/deferred delivery | all | S90 | final report commit |

## 4. 仕様固定クロージャ索引（Spec-Locked Closure Index）
| ID | Spec link | Observable input/state | Locked expectation | Bug class guarded | Required | Evidence level | Owner |
|---|---|---|---|---|---|---|---|
| C316-01 | AC-001 | CLI help/invalid args | Current-source fixed、scope/target各1、no `--from`/root | Public contract drift | yes | red-required | S02/S06 |
| C316-02 | AC-002、EC-006/007 | ID/path/basename/invalid/current/bare | Existing selector parity、mutation前拒否 | Resolver duplication/drift | yes | characterization+red | S01/S03 |
| C316-03 | AC-003 | Same ID/different slug、missing/invalid scopes | Source/target独立解決、failure時no mutation | Source path transposition | yes | red-required | S03 |
| C316-04 | AC-004、EC-001/009 | Missing/empty/non-directory Workbench | `no_source`/empty success/malformed failure、target保全 | Accidental target creation/deletion | yes | red-required | S03 |
| C316-05 | AC-005、EC-003/004 | Mixed source/destination tree | Destination-only保持、source wins、idempotent、type collision fail | Whole replacement/data loss | yes | red-required | S04 |
| C316-06 | AC-006 | Binary/archive/`.env`/nested `.git` | Classifierなし、ordinary bytes一致 | Allowlist/filter drift | yes | red-required | S04 |
| C316-07 | AC-007、EC-002/008/009 | Descendant/root/ancestor symlinks | Link non-deref、boundary外read/writeなし | Symlink traversal | yes | red-required | S05 |
| C316-08 | AC-008、EC-005 | Injected I/O/type/race failure | Failureをsuccessにせず、rollback claimなし | Hidden partial failure | yes | red-required | S05 |
| C316-09 | AC-009 | Text/JSON success/error | Experimental/noncanonical/one-shot/no-sync、body非露出 | Authority/secret leak | yes | contract-first | S02/S06 |
| C316-10 | AC-010 | Provider/dogfood/manual/regression/relay | Focused pass、manual handoff、Issue319 relay | Dogfood-only/delivery drift | yes | manual+review | S06/S90/S99 |

## 5. S00 — Baseline、assurance、planning closure
### Behavior goal
- Reviewed requirement/design/plan、current inventory、baseline、clean planning commitを実装者の唯一のhandoffへする。

### Planned contract
- Scope: Issue docs、scope-local evidence、read-only current runtime/tests。
- Test obligation: Existing worktree selector focused baselineと`assurance verify`。
- Evidence mode: `covered-existing` / inspect-only。
- Green: `assurance verify`、`validate`、focused selector tests、`git diff --check`。
- Amendment trigger: Baseline failureがcurrent branch change起因、またはexisting resolver semanticsがdesignと異なる。

### Delegation contract
- delegated role: repo-analyst（inventory済み）、ChatGPT 5.6 Pro evidence producer（artifact済み）、main orchestrator（canonical docs）、fresh spec-reviewer。
- input docs: requirement/design/plan/report、parent Epic、Issue315、planning artifact。
- allowed paths: Issue316 canonical docs/artifactのみ。
- forbidden changes: Production/tests/dogfood runtime。
- acceptance: All planning phase passes、assurance valid、no unresolved blocking EAL。
- verification: focused worktree tests、validate、diff check。
- reviewer focus: Spec trace、profile、step executability。
- stop conditions: Reviewer fail、assurance stale、product open question。
- output required: reviewer verdict、baseline commands、planning commit/clean evidenceをreportへ記録。

### 具体テストケース一覧
- `tc-s00-001` characterization: Existing selector baseline
  - 前提: Current branchのworktree focused tests。
  - 操作: ID/path/basename/ambiguity/current/bare/path casesを実行する。
  - 期待結果: Existing semanticsがpassする。
  - 失敗検出: Shared extraction前から壊れているbaselineを新実装へ混入することを防ぐ。
  - 検証方法: `tests/cli_runtime/test_worktree.py` focused pytest。
  - 関連 closure id: C316-02

### Step closure/gate
- Report: Spec Authoring Gate、EAL/OAL、Grade Specialist Evidence、baseline session。
- Gate: Fresh plan `spec-reviewer: pass`、planning commit、push、clean tree。

## 6. S01 — Existing target selectorの最小共有化
### Behavior goal
- Copy use caseがexisting target semanticsを複製せず使えるapplication boundaryを作る。

### Planned contract
- Scope: `application/worktree.py`、必要なら単一shared application module、selector tests。
- Test obligation: ID/path/basename、ambiguity、branch-only、external linked targetのtarget-record selection parity。Same-current/bare/path-missingはS03のcopy eligibilityで扱う。
- Red/alternative: characterization-first。Public resultが不変なことを抽出前後で比較する。
- Green: Focused worktree suiteとaffected lint/type check。
- Refactor guardrail: Stable ID generation/classification/outputを変更しない。Copy commandはまだ追加しない。
- Amendment trigger: Existing selector public semantics変更が必要。

### Delegation contract
- delegated role: dev-coder。
- input docs: requirement DES-316-002、plan C316-02、current worktree application/tests。
- allowed paths: worktree application/shared resolverとfocused tests。
- forbidden changes: Parser/command/copy adapter、public worktree output、managed classification contract。
- acceptance: Existing commandsとfuture copyが同一resolverを呼べる、all focused cases不変。
- required verification: selector focused pytest、Ruff/mypy affected、diff check。
- reviewer focus: No duplication、identity/current/bare/ambiguity semantics。
- stop conditions: Public behavior変更、scope外refactor、test baseline failure。
- output required: changed files、commands/results、risk、Ledger Note。

### 具体テストケース一覧
- `tc-s01-001` characterization: selector parity
  - 前提: Stable ID、absolute path、unique basenameの同一inventory。
  - 操作: 抽出後のexisting worktree operationsで各selectorを解決する。
  - 期待結果: 同じtarget recordとoutput/error categoryになる。
  - 失敗検出: Shared resolver抽出によるsemantic drift。
  - 検証方法: Existing/focused worktree pytest。
  - 関連 closure id: C316-02
- `tc-s01-002` negative: ambiguous/branch-only
  - 前提: Duplicate basenameとbranch-only token。
  - 操作: 各selectorを解決する。
  - 期待結果: Existing stable failure categoryが不変。
  - 失敗検出: Copy都合でtarget-record selectorを緩和する回帰。
  - 検証方法: Focused application/CLI pytest。
  - 関連 closure id: C316-02

### Step closure/gate
- Report: S01 Red/alternative/Green、delegation、closure、reviewer、commit evidence。
- Gate: Fresh code-reviewer pass → report update → focused commit → clean tree。

## 7. S02 — Thin vertical happy path
### Behavior goal
- Parserからtarget `.workbench/`へのsingle file copyとcontent-free resultまで、最小end-to-end Greenを通す。

### Planned contract
- Scope: parser/registry、new thin command、request/result/use case、ports/bootstrap、minimal fs operation/presentation、new focused CLI test。
- Test obligation: Help/parse、current source + one scope/target、empty target、single ordinary file、JSON markers。
- Red: Command未認識とcopy未成立を観測する。
- Green: One vertical happy pathだけを通す。
- Refactor guardrail: Error catalog、generic framework、root/sync/classifierを先行実装しない。
- Amendment trigger: Existing architectureではvertical pathを通せずnew cross-layer abstractionが必要。

### Delegation contract
- delegated role: dev-coder。
- input docs: DES-316-001/003/005/007、C316-01/03/05/09。
- allowed paths: Design module plan内のCLI/command/application/ports/bootstrap/fs/presentationとnew focused tests。
- forbidden changes: Existing worktree public semantics、root copy、complete safety/error matrix、public docs。
- acceptance: Single source fileがtarget側独立scope pathへcopyされ、text/JSONにauthority isolation markers。
- required verification: New focused Red/Green CLI test、affected lint/type、diff check。
- reviewer focus: Thin handler、layer direction、source current fixed、no hard-coded target scope path、no body output。
- stop conditions: Target resolver複製、source path転写、scope外API変更。
- output required: changed files、Red/Green、results、risk、Ledger Note。

### 具体テストケース一覧
- `tc-s02-001` acceptance: minimal end-to-end copy
  - 前提: Source/target linked worktreeに同scope ID、sourceにsingle file、target Workbench absent。
  - 操作: `workbench copy`をtarget IDで実行する。
  - 期待結果: Target側scope `.workbench`へ同bytesのfileができる。
  - 失敗検出: Wiringだけ追加されcopyが成立しない、またはsource pathを誤転写する欠陥。
  - 検証方法: New CLI runtime test。
  - 関連 closure id: C316-01、C316-03、C316-05
- `tc-s02-002` contract: JSON authority isolation
  - 前提: Minimal success fixture。
  - 操作: JSON outputでcopyする。
  - 期待結果: experimental=true、canonical=false、one_shot=true、sync=false相当を持ちbodyを含まない。
  - 失敗検出: Canonical/adoption claimまたはcontent leakage。
  - 検証方法: CLI JSON assertion。
  - 関連 closure id: C316-09

### Step closure/gate
- Report: S02 TDD/delegation/closure/reviewer/commit。
- Gate: Fresh code-reviewer pass → report → focused commit → clean tree。

## 8. S03 — Independent scope、eligibility、pre-mutation failure
### Behavior goal
- 全target/scope/source-root failureをmutation前に閉じ、different slugとempty sourceを正しく扱う。

### Planned contract
- Scope: Copy application/contracts/tests、必要なpreflight adapter query。
- Test obligation: Different slug、source/target missing/invalid、same-current/bare/path-missing、no_source absent/existing target、empty source、non-directory roots。
- Red: Mutation probeでgateway呼出し/target state changeを検出する。
- Green: All preflight failures stable、empty source success。
- Refactor guardrail: Path/ID input拡張、target fallback creationなし。
- Amendment trigger: Scope inventory API変更またはnew metadata semanticsが必要。

### Delegation contract
- delegated role: dev-coder。
- input docs: DES-316-003/004、C316-02/03/04。
- allowed paths: Copy application/contracts、focused application/CLI tests、必要最小限のport query。
- forbidden changes: Recursive merge internals、root/cross-repo/sync、existing node loader semantics。
- acceptance: All preflight failureでmerge未呼出し/target不変、different slug正解決、empty source success。
- required verification: Fake-port application tests、CLI selector matrix、lint/type/diff check。
- reviewer focus: Ordering、independent inventories、no_source before target create、same-current canonical identity。
- stop conditions: Mutation前にtarget mkdir、source path転写、error content leakage。
- output required: changed files、Red/Green、mutation probe evidence、Ledger Note。

### 具体テストケース一覧
- `tc-s03-001` acceptance: different slug independent resolution
  - 前提: Same scope ID、source slug `alpha`、target slug `renamed`。
  - 操作: Targetへcopyする。
  - 期待結果: Target `renamed/.workbench`だけが選ばれる。
  - 失敗検出: Source relative path転写。
  - 検証方法: Application/CLI fixture。
  - 関連 closure id: C316-03
- `tc-s03-002` negative: missing/invalid scopes no mutation
  - 前提: Sourceまたはtarget record missing/duplicate/invalid、target sentinelあり。
  - 操作: 各failureを実行する。
  - 期待結果: Side付きfailure、merge未呼出し、sentinel不変。
  - 失敗検出: Validation後回しによるpartial target creation。
  - 検証方法: Fake gateway probe + CLI assertions。
  - 関連 closure id: C316-03
- `tc-s03-003` negative/edge: no_source、empty、malformed roots
  - 前提: Missing/empty/file/symlink source Workbenchとnon-directory target root。
  - 操作: 各caseでcopyする。
  - 期待結果: Missingはno_source/no mutation、emptyはsuccess、malformedはexternal影響なしfailure。
  - 失敗検出: `exists()`誤用、broken symlink見落とし、target destructive replacement。
  - 検証方法: Application/infra-focused tests。
  - 関連 closure id: C316-04、C316-07

### Step closure/gate
- Report evidence destination: Session Log/TDD、Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure/Closure Coverage、Reviewer Gate Status、Milestone/Commit Candidate Gate。S03はsame-current/bare/path-missing/no_source/malformed rootのmerge未呼出しとtarget sentinel不変を記録する。
- Gate: Fresh code-reviewer pass → report → focused commit → clean tree。

## 9. S04 — Source-wins recursive mergeとcontent opacity
### Behavior goal
- Dedicated adapterでdestination-only保持、source wins、idempotency、unfiltered ordinary copyを閉じる。

### Planned contract
- Scope: Filesystem port/adapter、infra/application focused tests。
- Test obligation: Source-only/dest-only/same leaf/nested/repeat、binary/archive/`.env`/nested `.git`、leaf symlink replacement、directory/leaf collision、empty tree。
- Red: Existing primitiveがcontract未実装であることをfocused testsで確認。
- Green: Entry matrix全case。
- Refactor guardrail: No classifier/manifest/counter/transaction/generic framework。
- Amendment trigger: Standard primitiveでordinary bytesを保てない、またはentry matrix変更が必要。

### Delegation contract
- delegated role: dev-coder。
- input docs: DES-316-005、C316-05/06。
- allowed paths: Filesystem port/adapterとfocused infra/application tests。
- forbidden changes: CLI output、selector/scope contract、secret scan、rollback。
- acceptance: Mixed fixture contract、repeat equality、opaque bytes、collision保全。
- required verification: Infra focused pytest、application regression、lint/type/diff check。
- reviewer focus: `lstat`/non-deref、destination-only、collision data loss、no content branch。
- stop conditions: Whole target deletion、extension logic、unsupported entry silent skip。
- output required: changed files、Red/Green、tree/hash evidence、Ledger Note。

### 具体テストケース一覧
- `tc-s04-001` acceptance: mixed recursive merge
  - 前提: Source-only、destination-only、same leaf、nested directoryを含む両tree。
  - 操作: Mergeを2回実行する。
  - 期待結果: Add/preserve/overwriteが成立し、2回目後treeが同じ。
  - 失敗検出: Whole replacement、destination-only loss、non-idempotent結果。
  - 検証方法: Infra tree snapshot test。
  - 関連 closure id: C316-05
- `tc-s04-002` acceptance: opaque mixed content
  - 前提: Binary、archive、`.env`、Python、config、nested `.git`。
  - 操作: Mergeする。
  - 期待結果: 全ordinary file bytes一致、classificationなし。
  - 失敗検出: Extension/secret/filename filtering。
  - 検証方法: SHA/bytes assertions。
  - 関連 closure id: C316-06
- `tc-s04-003` negative: type collisions
  - 前提: Source directory/destination leafまたは逆、destination subtree sentinel。
  - 操作: Mergeする。
  - 期待結果: Failure、destination subtree/sentinel不変。
  - 失敗検出: Source-winsをdestructive subtree deletionと誤解する欠陥。
  - 検証方法: Infra negative tests。
  - 関連 closure id: C316-05

### Step closure/gate
- Report evidence destination: Session Log/TDD、Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure/Closure Coverage、Reviewer Gate Status、Milestone/Commit Candidate Gate。Mixed tree/hash/repeat/type-collision destination保全を記録する。
- Gate: Fresh code-reviewer pass → report → focused commit → clean tree。

## 10. S05 — Symlink、containment、copy failure
### Behavior goal
- Scope外read/writeを防ぎ、copy-time partial failureを正しくfailureとして観測する。

### Planned contract
- Scope: Copy preflight/merge adapter/result mappingとfocused tests。
- Test obligation: Descendant link object、source/target ancestor/root symlink、destination traversal symlink、leaf symlink replacement、external sentinel、injected mid-copy fault、content-free error。
- Red: Unsafe external accessまたはguard未実装のfailureを確認。
- Green: Fail-closed guard。全tree事前走査は要求せず、copy-time ancestry failureは`mutation_started=true`相当になり得る。
- Refactor guardrail: TOCTOU完全排除/transaction/rollbackを追加しない。
- Amendment trigger: External target read/writeを避けられない、またはatomicity claimが必要。

### Delegation contract
- delegated role: dev-coder。
- input docs: DES-316-004/006/007、C316-07/08/09。
- allowed paths: Copy application/fs adapter/result/presentationとfocused tests。
- forbidden changes: Symlink dereference、tree-wide prescan/rollback、raw OSError/body output。
- acceptance: External sentinels不変、descendant link text一致、all injected failures non-success、mutation_started semantics。
- required verification: Portable adapter tests、supported-host symlink integration、lint/type/diff check。
- reviewer focus: Resolve-before-guard bypass、existing destination ancestry、copy-time partial failure honesty、secret leakage。
- stop conditions: External access観測、platform guard未検証、success on failure。
- output required: changed files、Red/Green、external sentinel evidence、platform skip、Ledger Note。

### 具体テストケース一覧
- `tc-s05-001` acceptance: descendant symlink object copy
  - 前提: Broken/external target textを持つsource descendant symlink。
  - 操作: Copyする。
  - 期待結果: Targetに同link text、external targetはread/writeされない。
  - 失敗検出: Symlink dereference/copy target body。
  - 検証方法: `lstat`/`readlink` assertions。
  - 関連 closure id: C316-07
- `tc-s05-002` negative: ancestor/destination traversal symlink
  - 前提: Repo/specdock→scope/Workbench ancestorまたはdestination child ancestryがexternal directoryを指しsentinelあり。
  - 操作: Copyする。
  - 期待結果: Unsafe failure、external sentinel不変。Copy-time detectionならmutation_startedを真にする。
  - 失敗検出: Resolve-before-guard、`mkdir`/copy primitiveによるexternal write。
  - 検証方法: Preflight/infra integration tests。
  - 関連 closure id: C316-07、C316-08
- `tc-s05-003` negative: injected mid-copy I/O failure
  - 前提: First entry成功後にsecond entryでfaultするadapter fixture。
  - 操作: Copyする。
  - 期待結果: copy_failed、mutation_started=true、rollback/canonical claimなし、body非露出。
  - 失敗検出: Partial successをfull successとして返す欠陥。
  - 検証方法: Fault injection application/CLI tests。
  - 関連 closure id: C316-08、C316-09

### Step closure/gate
- Report evidence destination: Session Log/TDD、Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure/Closure Coverage、Reviewer Gate Status、Milestone/Commit Candidate Gate。Copy-time failureの`mutation_started=true`、external sentinel不変、platform skipをTDD/closure ledgerへ記録する。
- Gate: Security/path focusのfresh code-reviewer pass → report → focused commit → clean tree。

## 11. S06 — Public output、regression、manual handoff、relay
### Behavior goal
- 全public contractとfocused compatibilityを閉じ、実linked-worktree handoffを確認してIssue319へ送る。

### Planned contract
- Scope: Missing output/help/regression tests、minimal dogfood projection、manual fixture、report relay。
- Test obligation: Help/no forbidden options、all stable result categories、body secrecy、existing worktree/validate/sync/deps/opacity、manual different-slug mixed tree/repeat。
- Evidence: contract-first + manual-required。S02–S05で充足済み変更はapproved-no-op可。
- Green: Focused suitesとmanual scenario pass。
- Refactor guardrail: Final package/parity/docs/full suite/PRを先行しない。
- Amendment trigger: Installed surfaceにprovider implementationが届かずW5だけでは修復不能。

### Delegation contract
- delegated role: dev-coder（tests/projection/manual automation補助）。
- input docs: all design/closures、provider/dogfood runtime、existing regression suites。
- allowed paths: Missing tests、normal generated projection、Issue report evidence。
- forbidden changes: New semantics、public reference docs、Epic PR、Issue317/318機能。
- acceptance: C316-01/02/09/10 focused closure、manual scenario、W5 relay package。
- required verification: Focused workbench/worktree/validate/sync/deps tests、minimal dogfood compare、manual two-worktree commands。
- reviewer focus: Contract completeness、secret/body absence、W2/W5 boundary、dogfood-only patchなし。
- stop conditions: Final parity/full gateへscope拡張、manual result再現不能。
- output required: commands/results、manual fixture/result、changed files/no-op、relay evidence、Ledger Note。

### 具体テストケース一覧
- `tc-s06-001` contract: help/text/JSON matrix
  - 前提: Successと各selector/scope/no_source/unsafe/copy failure fixture。
  - 操作: Text/JSONとhelpを実行する。
  - 期待結果: Stable category、experimental/noncanonical/one-shot/no-sync、forbidden optionsなし、body/list非露出。
  - 失敗検出: Output drift/authority leak。
  - 検証方法: CLI contract tests。
  - 関連 closure id: C316-01、C316-09
- `tc-s06-002` regression: existing opacity/lifecycle
  - 前提: Copied Workbenchにfake metadata/ADR/dependency content。
  - 操作: Existing worktree/validate/sync/deps focused suitesを実行する。
  - 期待結果: Existing semantics pass、Workbench contentはdiscoveryされない。
  - 失敗検出: Explicit copy追加によるIssue315 opacity regression。
  - 検証方法: Existing/focused pytest。
  - 関連 closure id: C316-02、C316-10
- `tc-s06-003` manual: linked-worktree handoff
  - 前提: Same scope ID/different slug、source mixed content+link、target same leaf+target-only。
  - 操作: Basenameでcopy、absolute pathで再実行する。
  - 期待結果: Target-only保持、source wins、binary hash/link text一致、target slug配置、再実行差分なし。
  - 失敗検出: Unit fixtureだけでは見えないGit worktree/path integration defect。
  - 検証方法: Managed temp repoのmanual command record。
  - 関連 closure id: C316-03、C316-05–07、C316-10

### Step closure/gate
- Report evidence destination: Session Log/TDD、Implementation Delegation Gate、Delegated Worker Evidence、Step Contract Closure、Test Contract Closure/Closure Coverage、Reviewer Gate Status、Milestone/Commit Candidate Gate、Deferred Delivery/Issue319 relay。Public output matrix、focused regression、manual fixture/resultを記録する。
- Gate: Fresh code-reviewer pass → report → commitまたはapproved-no-op → clean tree。

## 12. S90 — Docs impact resolution
### Behavior goal
- 本Issueで必要なcommand-local docsを閉じ、final public guideをIssue319へ重複なくrelayする。

### Delegation contract
- delegated role: doc-writer。
- input docs: requirement/design、CLI help/output、current shipped docs、Epic W5 boundary。
- allowed paths: 必要と判断したprovider shipped docsとnormal dogfood projection、またはreport no-op evidence。
- forbidden changes: Issue317/318未実装機能、final migration/rollout、product semantics追加。
- acceptance: Help/text/JSONだけで利用契約が足りるならinspected paths付きapproved-no-op。Command inventory欠落が誤解を生む場合だけ最小experimental記述。
- required verification: Docs diff/links、provider-dogfood affected file compare、fresh spec review。
- reviewer focus: W2/W5 boundary、experimental/root manual/no-sync/noncanonical。
- stop conditions: Public docsがIssue319 final設計を先取りする。
- output required: Changed files or no-op rationale、inspection evidence、Ledger Note。

### 具体テストケース一覧
- `tc-s90-001` inspect: docs ownership
  - 前提: Current public guide/command inventoryとimplemented help。
  - 操作: New command欠落が利用不能/誤解を生むか点検する。
  - 期待結果: Minimal updateまたはIssue319 deferの根拠が一意。
  - 失敗検出: Docs gapまたはfuture semantics先行記述。
  - 検証方法: Docs inspection + fresh spec-reviewer。
  - 関連 closure id: C316-10

### Step closure/gate
- Report evidence destination: Docs Impact Gate、Delegated Worker Evidence、Reviewer Gate Status、Milestone/Commit Candidate Gate。Inspected docs、update/no-op理由、Issue319 deferを記録する。
- Gate: Fresh spec-reviewer pass → report → docs commitまたはapproved-no-op → clean tree。

## 13. S99 — 最終品質ゲートとIssue Finish
### Planned verification
1. All focused Workbench copy tests。
2. Existing worktree/validate/sync/deps/Issue315 opacity focused regression。
3. `uv run pytest tests/unit`と`uv run pytest tests/cli_runtime`はIssue319 final full gate所有のため、本Issueではqa-reviewerがriskにより必要性を判断する。Blocking regression疑いがあれば実行する。
4. Affected lint/format/mypyまたはrepository `make lint`をqa判断で実行。
5. `assurance verify`、`validate`、`git diff --check`。
6. Manual two-worktree evidenceとminimal dogfood projection。
7. Fresh qa-reviewer、issue-wide code-reviewer、spec-reviewer。Blocking findingは修正しfresh re-review。

### Final quality delegation
- qa-reviewer: C316-01–10のrisk-calibrated coverage、integration/full-suite判断。
- code-reviewer: Whole integrated diff、resolver parity、containment、data loss/output leakage。
- spec-reviewer: Requirement/design/plan/report/implementation/tests/docsとW5 relay。
- Main orchestrator: Findings統合、report final ledger、commit/push/clean、`issue finish`。

### Deferred delivery contract
- Per-Issue PRは作らない。
- Reportへ`deferred_to: iss-00319`、dependency edge、pushed head、commit一覧、remaining final package/parity/docs/full gate、merge-prepared未主張を記録する。
- Branchをpushしclean/synced確認後にactive Issue316を`issue finish`する。

## 14. Final Exit Contract
- Requirement/design/plan fresh review済み、assurance valid。
- C316-01–10にobserved evidenceがあり、required closure未解決なし。
- All implementation/docs stepsがfresh reviewer pass、report update、commit/no-op、clean treeを持つ。
- Final QA/code/specにblocking findingなし。
- Root/cross-repo/automatic/sync/classifier/transaction/Artifact import/workflow機能を実装していない。
- Issue319 relay、push、clean tree、Issue Finishが完了している。
