---

kind: "tdd-ready-plan-candidate"
issue: "iss-00395"
title: "Issue #395 Code-free TDD Implementation Plan"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-canonical-replacement-candidate"
---

# Issue #395 Code-free TDD Implementation Plan

## 1. このPlanの役割

本Planは、LunaMaxが各stepで何を観測し、どの失敗なら修復へ進み、どのsurfaceを最小変更し、どのGREENと証拠で次へ進むかを定めます。

本Planは実装コード、test runner、snapshot utility、ledger mutation program、Git commit script、PR operation scriptを提供しません。それらをMarkdownからコピーすることを実装とみなしません。

Exact file、symbol、nodeid、test lane、期待結果、証拠、停止条件は固定します。Method body、helper decomposition、temporary evidence toolの内部実装は、verified sourceを読み、Designのcontract内でTDDにより決めます。

現在は`implementation_allowed=false`です。Step 0のread-only確認以外のmutationへ進みません。

## 2. Global execution rules

1. 一stepずつ進み、REDとGREENを同じrepair unitへ対応付けます。
2. Expected REDと異なる失敗を、修復対象へ都合よく読み替えません。
3. Selected heavy testはfull-regression permissionとshard modeを伴い、normal passを観測します。
4. Skip、xfail、xpass、未実行、setup/teardown errorをGREENと扱いません。
5. Accepted assertionを削除・弱化しません。
6. Productionをobsolete API/CLIへ戻しません。
7. Provider sourceを先に修復し、dogfood generated filesを手編集しません。
8. Ledgerは全behavior GREENとdogfood projection後の最後のsemantic transitionです。
9. Working-tree evidenceとexact clean SHA evidenceを区別します。
10. LunaMaxはhuman merge、revert、Issue closure、#396 startを行いません。

Selected heavy nodeの実行patternは、`uv run pytest --run-full-regression --full-regression-shard <nodeid>`を基礎とし、repositoryのobservation optionでcollected/executed/outcomeを記録します。Full verifierはcurrent `scripts.quality.verify_full_regression`をfour shardsとdedicated artifact directoryで実行します。これらはcommand contractであり、Plan内にrunner programを埋め込みません。

## 3. Repair map

| Unit | Rows                     | Primary surface                           | Product edit                             |
| ---- | ------------------------ | ----------------------------------------- | ---------------------------------------- |
| A    | 4–11                     | `_StubTemplateScaffolder`                 | なし                                       |
| B    | 1、13、14、15               | Test observers                            | なし                                       |
| C    | 3                        | Row 3 observerと`infra/git_cli.py`         | あり                                       |
| D    | 12                       | No-edit structural guard                  | なし                                       |
| E    | 1、3–15 + row 2 successor | Dogfood projectionとledger terminalization | Generated projection + final ledger only |

## 4. Step 0 — Read-only identity and authorization gate

| Field                      | Contract                                                                                                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose                    | Mutation前に、対象repository、branch、specification identity、review、permission、writer exclusivityを確定する                                                                              |
| Preconditions              | None。Read-onlyで実行可能                                                                                                                                                          |
| Inspect                    | Repository metadata、target branch tip、local HEAD/tree、upstream、remote tip、worktree status、P392 ancestry、spec pack diff、active Issue、metadata、review receipt、writer assertion |
| RED / blocking observation | 値の不一致、dirty state、review未pass、P0/P1 nonzero、implementation authorization不在、writer scope不足                                                                                    |
| Minimal change intent      | なし。Gateを通すためにrepository stateを修正しない                                                                                                                                          |
| GREEN                      | Exact identity一致、clean、review pass、authorization true、scoped writer absence、human merge only                                                                                 |
| Evidence                   | Repository/branch/SHA/tree、review identity/hash、writer assertion identity/scope/expiry、operations attempted                                                                  |
| Stop                       | 一項目でも不成立なら変更0で返す                                                                                                                                                             |

Commit/pushとPR preparationのpermissionは別fieldです。Step 0のmutation permissionがtrueでも、自動的にcommit、push、PR操作へ進みません。

## 5. Step 1 — Entry baseline admission

| Field                      | Contract                                                                                                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Purpose                    | P392由来のexact baselineと、Issue #395が所有するfailure集合だけを確認する                                                                                                                         |
| Preconditions              | Step 0 GREEN                                                                                                                                                                   |
| Inspect                    | Ledger 15 rows、14 active、row 2 resolved/superseded、row order、nodeid/signature、row 2 successor、timing 243、required-fast 4、source blobs、policy/workflow no-touch                 |
| RED / expected entry state | Full verifierは`ledger-mismatch`。Rows 4–11と15はsignature mismatch、row 12はcoverage mismatch。Rows 1、3、13、14はactive historical failureとしてverified、row 2 successorはresolved verified |
| Minimal change intent      | なし。Entry observationを取得するだけ                                                                                                                                                    |
| GREEN to continue          | Exact allowance以外のviolationが0、#392-owned failure 0、unexpected failure 0                                                                                                        |
| Evidence                   | Ledger snapshot/hash、full verifier result/hash、row mapping、timing/required-fast counts、source identity                                                                         |
| Stop                       | Extra/missing violation、row drift、signature drift、source drift、row 12 drift                                                                                                    |

Entry full verifierが完全GREENである必要はありません。P392の唯一のnon-GREEN allowanceとexactに一致することが必要です。

## 6. Step 2 — First RED inventory

| Field                 | Contract                                                                                                                                                                                                  |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose               | 各repair rowの最初の誤り層を個別に確定し、誤ったsurfaceを修正しないようにする                                                                                                                                                           |
| Preconditions         | Step 1 GREEN、tracked mutation 0                                                                                                                                                                           |
| Targets               | Rows 1、3–11、13–15を一件ずつ実行。Row 12はfull verifier coverage mismatchとnode単体passを別に観測                                                                                                                           |
| Expected RED          | Row 1/13/14/15: retired active argument。Row 3: read-only current repo identity unresolved。Rows 4–11: test doubleにcurrent descriptor-bound operationがない。Row 12: nodeはpass、active ledgerだけcoverage mismatch |
| Minimal change intent | なし。観測だけ                                                                                                                                                                                                   |
| GREEN to continue     | 13 repair rowsがexpected layerでfailし、row 12 nodeがnormal passする                                                                                                                                             |
| Evidence              | Row ordinal、nodeid、exit/outcome、sanitized failure summary、failure signature、raw-log hash、observation hash                                                                                                 |
| Stop                  | Pass、skip、xfail、xpass、error、別failure layer、別node実行、credential exposure                                                                                                                                    |

Row 3のfailure outputにcredentialが出ている場合、Product修復へ進まずsecurity incidentとして停止します。

## 7. Step 3 — Unit A: Rows 4–11 test-double seam

| Field                 | Contract                                                                                                                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose               | Test fixtureをcurrent descriptor-bound application portへ追随させ、productionを退行させず8 behaviorsを回復する                                                                                            |
| Preconditions         | Step 2でrows 4–11がmissing current portをREDとして示す                                                                                                                                          |
| Target file/symbol    | `tests/cli_runtime/test_runtime_import_s10.py::_StubTemplateScaffolder.copy_scaffolded_tree_at`                                                                                         |
| Read-only references  | `application/ports.py::TemplateScaffolder`、`infra/template_scaffolder.py`、`application/create_node.py`                                                                                  |
| RED                   | `_StubTemplateScaffolder`がcurrent descriptor-bound operationを提供せず、rows 4–11がそのboundaryでfailする                                                                                           |
| Minimal change intent | Test doubleへcurrent call shapeを一つ追加し、existing production adapter behaviorへ委譲する。Second writerを作らず、old production pathへ戻さない                                                               |
| Protected behavior    | Parent fallback、two manifest reads、lock-side re-resolution、repo slug propagation、artifact path/name/content、negative sync、exactly-once create plan、rules symlink、retired output absence |
| GREEN                 | Rows 4–11が個別にcollected/executed once、normal pass、failure signature 0                                                                                                                    |
| Evidence              | Changed symbol、8 row observations、preserved assertion checklist、production no-touch diff                                                                                                |
| Stop                  | Port signature drift、production editが必要、assertion weakeningが必要、unexpected file change                                                                                                   |

## 8. Step 4 — Unit B: Rows 1、13、14、15 observers

| Field                  | Contract                                                                                                                                                                                                                                                                           |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose                | Test observerをcurrent selection-only CLI surfaceへ追随させる                                                                                                                                                                                                                             |
| Preconditions          | Step 2でretired argumentsがfirst RED                                                                                                                                                                                                                                                 |
| Target files/symbols   | Row 1 exact method in `test_delete.py`、rows 13/14 exact methods in `test_sync.py`、row 15 exact method in `test_workbench.py`                                                                                                                                                       |
| Read-only reference    | `commands/active.py` argument contract                                                                                                                                                                                                                                             |
| Exact observer mapping | Row 1: `active set --id iss-00058 --force` → `active set --id iss-00058`。Row 13: `active set iss-00003 --force` → `active set iss-00003`。Row 14: `active set 305 --force --no-checkout` → `active set 305`。Row 15: `active set --id scope_id --force` → `active set --id scope_id` |
| RED                    | `--force`または`--no-checkout`がparserで拒否される。Row 15は失敗後に未生成stateを読む可能性がある                                                                                                                                                                                                              |
| Minimal change intent  | Retired argumentsだけを除去する。Row 15はactive operation successをstate readより先に検査する                                                                                                                                                                                                        |
| Protected behavior     | Row 1 delete non-reobservation、row 13 convergence、row 14 root outputs、row 15 copied-byte opacityと全observations                                                                                                                                                                     |
| GREEN                  | Four nodesが個別にnormal passし、retired argumentsが対象methodsから消える                                                                                                                                                                                                                        |
| Evidence               | Before/after observer invocation summary、4 row observations、protected assertion checklist                                                                                                                                                                                          |
| Stop                   | Product active command変更が必要、assertion削除が必要、active state semanticsが変わる                                                                                                                                                                                                              |

## 9. Step 5 — Unit C1: Row 3 test-first security contract

| Field                     | Contract                                                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Purpose                   | Existing row 3 nodeでsuccessとcredential non-exposureを同時に受け入れるcontractを先に固定する                                                          |
| Preconditions             | Step 2 row 3 RED、credential exposure 0                                                                                               |
| Target file/symbol        | `tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote`        |
| RED                       | Observer強化後も、failure reasonはread-only repo identity unresolvedである。Secret assertion自体の失敗ではない                                          |
| Minimal change intent     | Existing nodeとsuccess assertionを保持し、combined outputにsynthetic tokenとcredential-bearing URLが含まれないことを観測する。New nodeやnew ledger rowを作らない |
| GREEN for test-first step | Product未修復のためnodeはexpected identity failureのまま、credential leakageは0                                                                  |
| Evidence                  | Same nodeid、failure layer、non-exposure observation、test-only diff                                                                    |
| Stop                      | Testを変更しただけでpassする、credentialが出る、node renameが必要                                                                                      |

## 10. Step 6 — Unit C2: Row 3 Product boundary

| Field                 | Contract                                                                                                                             |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Purpose               | Read-only identity parsingをpublication policyから分離し、security strictnessを保持する                                                          |
| Preconditions         | Step 5 GREEN、existing symbols/signaturesを確認済み                                                                                        |
| Target file/symbols   | `src/.../infra/git_cli.py`の`_parse_github_repo_slug`、`origin_github_repo_slug`、`origin_github_publication_endpoint`                  |
| RED                   | Credential-bearing fetch originからread-only slugを得られず、same-repo importが失敗する                                                           |
| Minimal change intent | Identity parserはGitHub identityだけを返す。Read-only pathはfetch originだけを使う。Publication pathはfetch/push userinfo拒否とslug equalityを担う        |
| Forbidden change      | Existing port signatures、bootstrap binding、same-repo validation、numeric scope、foreign rejection、Git coordination、new public API      |
| GREEN                 | Row 3 normal pass。Four-case matrixでcredential-bearing fetch、push-only credential、mismatch、clean matchがDesignどおりとなり、secret exposure 0 |
| Evidence              | Changed symbols、row 3 observation、matrix result、stdout/stderr/exception sanitization、no-touch diff                                   |
| Stop                  | Publication strictnessを弱める必要、raw secret exposure、application policy変更が必要                                                             |

## 11. Step 7 — Unit D: Row 12 no-edit guard

| Field                 | Contract                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Purpose               | Historical defectが既に修復済みであるcurrent boundaryを、不要な再編集から守る                                                                        |
| Preconditions         | Entry node normal pass、verified source blobs一致                                                                                 |
| Guard paths           | `commands/new.py`、`application/contracts.py`、`domain/artifacts.py`、`test_runtime_shell_s11.py`                                 |
| RED                   | Ledger evaluatorのcoverage mismatchだけ。Nodeまたはsource boundaryのfailureではない                                                        |
| Minimal change intent | Product/test edit 0                                                                                                            |
| GREEN                 | Exact blobs unchanged、commands→application→domain direction、commandsからdomain/infra direct import 0、structural node normal pass |
| Evidence              | Blob identities、import-edge observation、node result、diff 0                                                                     |
| Stop                  | Any source/test drift、node failure、catalogue duplication、new wrapperが必要                                                        |

## 12. Step 8 — Pre-ledger 15-node normal-pass gate

| Field                 | Contract                                                                                                   |
| --------------------- | ---------------------------------------------------------------------------------------------------------- |
| Purpose               | Ledger truthを変える前に、14 historical nodesとrow 2 successorがcurrent Product/test candidateでnormal passすることを確認する |
| Preconditions         | Steps 3–7 GREEN                                                                                            |
| Targets               | Rows 1、3–15の14 historical nodeidsとrow 2 successor                                                          |
| RED                   | 一件でもnon-pass、skip、xfail、error、duplicate execution                                                          |
| Minimal change intent | なし。Failed rowのowned repair unitへ戻る                                                                         |
| GREEN                 | Exact 15 nodeidsがcollected/executed once、all passed、failure signatures 0                                   |
| Evidence              | Combined observationとrow-specific GREEN evidenceの対応                                                        |
| Stop                  | Unexpected failure、row 2 successor failure、row 12 regression、scope外repairが必要                               |

このgateより前にledgerを変更しません。

## 13. Step 9 — Provider-first dogfood projection

| Field                 | Contract                                                                                                                                       |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose               | Candidate-changing provider sourceをchecked-in dogfoodへcomplete projectionし、lifecycle/protected-data contractを保持する                              |
| Preconditions         | Step 8 GREEN。Provider source-focused testsとlint GREEN。Ledger entry stateのまま                                                                    |
| Snapshot              | Pre-projection digest、ready record、two `SKILL.md` hashes、consumer-owned rootsのtype/mode/symlink target/content hash、tracked diff               |
| Mutation surface      | Current lifecycle updateだけ。Generated four pathsを手編集しない                                                                                         |
| RED / failure         | Update non-complete、warning completion、digest不変/不一致、runtime mirror mismatch、protected-data drift、version/state/operation/policy drift          |
| Minimal change intent | One complete update candidateを生成する。Lifecycle implementationは変更しない                                                                              |
| GREEN                 | Provider/dogfood bytes一致、new digest三者以上一致、old/new digest差、version 0.2.4、ready/null/preserve-only、protected equality、dogfood parity normal pass |
| Evidence              | Sanitized update result、old/new digest、record/markers summary、source mirror hash、protected snapshot equality、parity observation                |
| Stop                  | Lifecycle/wire変更、generated hand-edit、consumer data drift、unexpected provider-root change                                                       |

## 14. Step 10 — Final ledger transition

| Field                 | Contract                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Purpose               | Repaired behaviorをtransitional ledgerへ最後に記録する                                                                                   |
| Preconditions         | Steps 8・9 GREEN。Saved entry ledgerとcurrent ledgerがbyte-semantic equal                                                           |
| Target                | `full-regression-ledger.json` only                                                                                              |
| RED                   | Any behavior non-pass、entry payload drift、row 2 drift、historical field drift                                                    |
| Minimal change intent | Rows 1、3–15の`lifecycle`をresolvedへ、`resolution_mode`をfixed-in-placeへするだけ                                                         |
| Forbidden change      | Nodeid、signatures、current/historical status、disposition、row order、row 2、top-level fields、row追加/削除/rename/successor substitution |
| GREEN                 | 15 total、0 active、15 resolved、14 fixed-in-place、1 superseded。Before/after comparisonが許容二field差だけを示す                             |
| Evidence              | Ledger before/after hashes、row-by-row delta、row 2 exact equality、top-level equality                                             |
| Stop                  | VerifierをGREENにするため他field変更が必要、JSON textだけでresolutionを宣言する必要                                                                    |

## 15. Step 11 — Working-tree complete verification

| Field            | Contract                                                                                                                                                                                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Purpose          | Uncommitted candidateのfunctional completenessを確認し、exact candidate freezeへ進めるか判断する                                                                                                                                                                                       |
| Preconditions    | Step 10 GREEN                                                                                                                                                                                                                                                           |
| Required checks  | Evaluator unit、15-node observation、current full verifier、ordinary lane、provider lifecycle unit、distribution cutover、platform/coordination、packaged distribution、dogfood suite、lint、SpecDock validate、row 3 matrix、row 12 guard、ledger invariant、protected-data equality |
| File-scope check | Expected 11 pathsだけがchanged。Timing、policy、workflow、wire、parent docs、#392、#396、row 12 pathsはno-touch                                                                                                                                                                     |
| GREEN            | All checks normal pass、violations 0、active_verified empty、resolved_verified 15、unexpected 0、diff check clean、untracked implementation artifacts 0                                                                                                                       |
| Evidence         | Complete binary diff SHA-256、provisional verifier hash、command receipts、manual invariant receipts                                                                                                                                                                       |
| Candidate state  | `working-tree-provisional`、`merge_ready=false`                                                                                                                                                                                                                          |
| Stop             | Any gate failure、extra/missing expected path、manual invariant failure、evidence identity不足                                                                                                                                                                               |

Working-tree full verifierのreported candidate SHAをuncommitted bytesのidentityとみなしません。HEADとbinary diff digestの組でprovisional evidenceにします。

## 16. Step 12 — Optional exact clean candidate and independent reviews

| Field               | Contract                                                                                            |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| Purpose             | Separate permissionがある場合だけ、candidateをone clean pushed SHA/treeへ固定し、merge-blocking evidenceを再束縛する    |
| Preconditions       | Step 11 GREEN、`commit_push_authorized=true`、remote Issue branchがspec freeze identityから動いていない        |
| Stage scope         | Exact 11 implementation pathsだけ。Evidence、logs、cache、untracked filesはstageしない                        |
| Mutation            | Conventional Commitとnormal push。Amend、force push、integration branch direct pushは禁止                  |
| Exact rerun         | Step 11の全checksとmanual invariantsをclean implementation SHA/treeで再実行する                               |
| Independent reviews | Code Review Strict pass、P0=0、P1=0。Final Quality Gate pass、coverage complete、unreviewed/unresolved 0 |
| GREEN               | Local HEAD、upstream、remote、review targets、all evidenceが同じimplementation SHA/tree                    |
| Evidence            | Implementation SHA/tree、exact diff、full verifier hash、all gate receipts、review receipts             |
| Stop                | Permission不在、remote drift、review finding、new commit、clean state不成立                                  |

Finding修正でcommitが変わった場合、過去のexact-SHA evidenceとreview receiptを流用せず、影響checksと全merge-blocking invariantsをnew SHAへ再束縛します。

## 17. Step 13 — Pre-merge terminal return and post-merge handoff

### 17.1 LunaMax terminal point

Commit/push未許可なら、working-tree provisional candidateとevidenceを返して停止します。Commit/push許可かつreviews GREENなら、clean pushed exact candidateを返して停止します。

`pr_prepare_authorized=true`の場合だけ、review済みcandidateのPRをIssue branchからEpic integration branchへ作成または更新できます。LunaMaxはmergeしません。

### 17.2 Human merge boundary

Human merge前に、PR head SHA/tree、required Provider CI roles、exact full verifier、Code Review Strict、Final Quality Gate、unresolved finding 0を確認します。

### 17.3 Post-merge B1/B2 handoff

Post-merge operationはLunaMax implementation taskの外です。Human/Codexはclean checkoutでintegration tipを固定し、PR head treeとのequalityを確認します。

同じexact merged SHA/treeで、B1としてcurrent gatesとprovider parityを確認し、その後B2として15/0/15、14 fixed-in-place、1 superseded、approved 0、unexpected 0、timing 243、historical fields preservationを確認します。

LunaMaxは#392/#395 closure、#396 start、policy retirement、main mergeを行いません。

## 18. Evidence inventory

| Evidence       | Required content                                                        |
| -------------- | ----------------------------------------------------------------------- |
| Identity       | Repository、branch、P392、specification、optional implementation SHA/tree   |
| Entry          | Ledger before、timing/required-fast、entry verifier allowance             |
| RED            | 13 repair rows + row 12 evaluator RED/node GREEN                        |
| GREEN          | Row-specific outcomes、pre/post-ledger 15-node outcomes                  |
| Security       | Row 3 four-case matrix、secret exposure 0                                |
| Row 12         | Blob/import direction/node pass/no-edit                                 |
| Dogfood        | Update result、old/new digest、record/markers、mirror equality、parity      |
| Protected data | Before/after snapshot equality、two `SKILL.md` hashes                    |
| Ledger         | Before/after、allowed delta only、row 2/top-level preservation            |
| Verifier       | Entry、working-tree provisional、exact clean、post-merge result identities |
| Gates          | Ordinary、lifecycle、distribution、platform、package、dogfood、lint、validate  |
| Reviews        | Specification、Code Review Strict、Final Quality Gate                     |
| Terminal       | Candidate state、merge_ready、unresolved findings、rollback readiness      |

Distributed evidenceにraw credential、private absolute path、raw secret-bearing logを含めません。

## 19. Consolidated stop-and-return contract

停止時は次を返します。

| Field                     | Meaning                              |
| ------------------------- | ------------------------------------ |
| `issue`                   | `iss-00395`                          |
| `stage`                   | 停止したPlan step                        |
| `repository` / `branch`   | Expected identity                    |
| `expected` / `actual`     | Sanitized comparison                 |
| `row_ordinal` / `nodeid`  | Applicableな場合のrow identity           |
| `contract_id`             | Violated Requirement/Design contract |
| `changed_paths`           | 既に変更されたpath。変更0ならempty               |
| `observed_operations`     | 実行済みread/write操作と結果                  |
| `secret_redacted`         | 常にtrue                               |
| `owner_decision_required` | New decisionが必要か                     |
| `next_check`              | Cause isolationに必要な次のread-only確認     |

停止後にdefault branchや別branchへfallbackしません。Expected valueをactualに合わせて書き換えません。Reset、force checkout、force push、automatic rollbackを行いません。

## 20. Completion criteria

Implementation candidateがmerge-readyと評価されるのは、Step 12までを同じclean pushed SHA/treeで満たした場合だけです。Merge-readyはhuman merge permissionを意味しません。

本Planの採用だけではStep 1以降のmutationを許可しません。

* `implementation_allowed=false`
* `owner_decisions_required=[]`
* `human_merge_only=true`
